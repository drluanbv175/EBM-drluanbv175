#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TỰ KHỞI ĐỘNG giám sát chứng cứ — thay cho lịch launchd vốn CHƯA BAO GIỜ nổ.

VÌ SAO CÓ (13/08/2026)
======================
Đo trực tiếp bằng `launchctl print`:

    com.medicalebm.weeklysafety    runs = 0   last exit code = (never exited)
    com.medicalebm.monthlyupdate   runs = 0   last exit code = (never exited)

`runs = 0` KHÔNG phải sự cố nhất thời — đó là trạng thái kể từ khi cài (11/07).
`StartCalendarInterval` đòi máy phải ĐANG THỨC đúng 19:00 thứ Bảy; MacBook đóng
nắp thì job không chạy và launchd không bù lại đáng tin. Trên Windows còn tệ hơn:
không có launchd nào cả.

Hệ quả đúng như đã đo: mọi lần chứng cứ được cập nhật đều do bác sĩ CHỦ ĐỘNG hỏi.
Một hệ chỉ động đậy khi được gọi là CÔNG CỤ, không phải hệ agent. Đây là chốt
đóng đúng khoảng trống đó.

CÁCH VÁ: bám theo thói quen THẬT, không bám đồng hồ
====================================================
Bác sĩ mở phiên Claude gần như mỗi ngày. Vậy lấy chính lúc mở phiên làm nhịp:
nếu giám sát đã quá hạn thì PHÓNG NGAY tiến trình thu thập ở NỀN (detached), rồi
trả quyền điều khiển lại tức thì. Không phụ thuộc máy có thức lúc 19:00 hay không,
và chạy giống nhau trên cả macOS lẫn Windows.

RANH GIỚI — đọc trước khi mở rộng file này
===========================================
1. CHỈ phóng được hai script CHỦ SỞ HỮU trong `OWNER` bên dưới. Doctrine đã chốt
   "owner thu thập duy nhất là weekly_safety.sh + monthly_update.sh"; mọi routine
   khác chỉ được dùng candidate queue. Công cụ này KHÔNG tự viết bộ thu thập mới.
2. Hai script đó THU THẬP và BÁO CÁO, không phát hành: bước nối Hub của chúng đã
   fail-closed theo `source_health`, và Cổng A/B vẫn nguyên vẹn. Không có đường
   nào từ đây tới việc đổi `decision`/`gradeLevel` của một mục chứng cứ.
3. Có CÔNG TẮC TẮT: tạo file `.tu-khoi-dong-tat` ở gốc repo là dừng hẳn.
4. Không bao giờ phóng chồng: khoá theo PID, coi là treo sau `HAN_TREO_GIO`.

Dùng:
    python3 tools/tu_khoi_dong.py             # xem sẽ làm gì, KHÔNG phóng
    python3 tools/tu_khoi_dong.py --phong     # phóng thật ở nền
    python3 tools/tu_khoi_dong.py --phong --im-khi-on   # cho hook
    python3 tools/tu_khoi_dong.py --tat / --bat         # công tắc

Mã thoát: 0 = không cần làm gì hoặc đã phóng · 1 = quá hạn mà chưa phóng · 2 = lỗi.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]
PROJ = REPO / "medical-ebm-automation"
KHOA = REPO / ".tu-khoi-dong.json"
CONG_TAC_TAT = REPO / ".tu-khoi-dong-tat"
NHAT_KY = PROJ / "data/archive/tu_khoi_dong.log"

# CHỈ các script trong allowlist này được phóng. Thêm mục = đổi doctrine — cần bác sĩ
# duyệt (mục 'quy' đã duyệt 15/08/2026 qua LÔ 0/Q3 của kế hoạch kiện toàn).
OWNER = {
    "tuan": {
        "script": PROJ / "scripts/weekly_safety.sh",
        "log": PROJ / "data/archive/launchd_weekly.log",
        "han_ngay": 10,          # chu kỳ tuần, nới 3 ngày
        "ten": "giám sát an toàn thuốc hằng tuần",
    },
    "thang": {
        "script": PROJ / "scripts/monthly_update.sh",
        "log": PROJ / "data/archive/launchd_monthly.log",
        "han_ngay": 35,          # chu kỳ tháng, nới 5 ngày
        "ten": "cập nhật guideline hằng tháng",
    },
    # CHỦ SỞ HỮU THỨ BA — bác sĩ duyệt Q3 ngày 15/08/2026 (LÔ 0 kế hoạch kiện toàn):
    # quét "chứng cứ bị vượt qua" toàn kho theo QUÝ, canh chỉ số "guideline đang dùng
    # nhưng đã bị thay thế = 0" vốn trước đó không ai canh định kỳ.
    # CHỦ SỞ HỮU THỨ TƯ (15/08/2026, vòng «tự động tốt nhất + trung thực»): nhịp
    # THÁNG của PHA 3 mục 4 — validate ledger · truy nguyên toàn sổ · sức khoẻ sổ
    # nguồn · eval gold set. Trước đây 4 tool này chỉ chạy khi có người gõ ⇒ nhịp
    # tháng chỉ tồn tại trên giấy.
    "thang_liem_chinh": {
        "script": PROJ / "scripts/evidence_integrity_monthly.sh",
        "log": PROJ / "data/archive/evidence_integrity.log",
        "han_ngay": 35,
        "ten": "liêm chính chứng cứ hằng tháng (ledger·truy nguyên·nguồn·eval)",
    },
    "quy": {
        "script": PROJ / "scripts/quarterly_superseded.sh",
        "log": PROJ / "data/archive/quarterly_superseded.log",
        "han_ngay": 92,          # chu kỳ quý, nới 2 ngày
        "ten": "quét chứng cứ bị vượt qua (quý)",
    },
}

HAN_TREO_GIO = 3       # tiến trình chạy quá ngần này giờ thì coi là treo, cho phóng lại


def _doc_khoa() -> dict:
    try:
        return json.loads(KHOA.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _ghi_khoa(d: dict) -> None:
    try:
        KHOA.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass


def _con_song(pid: int) -> bool:
    """Tiến trình còn chạy không. `os.kill(pid, 0)` không gửi tín hiệu nào,
    chỉ hỏi kernel — an toàn."""
    if sys.platform == "win32":
        try:
            r = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"],
                               capture_output=True, text=True, timeout=10, encoding="utf-8", errors="replace")
            return str(pid) in r.stdout
        except Exception:  # noqa: BLE001 — chốt không được làm chết phiên
            return False
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def dang_chay() -> str | None:
    """Tên việc đang chạy dở, hoặc None. Tự dọn khoá mồ côi/treo."""
    k = _doc_khoa()
    pid, viec, luc = k.get("pid"), k.get("viec"), k.get("luc")
    if not pid or not viec:
        return None
    if not _con_song(int(pid)):
        _ghi_khoa({})               # tiến trình đã xong/chết → dọn khoá
        return None
    try:
        bat_dau = dt.datetime.fromisoformat(luc)
        if (dt.datetime.now() - bat_dau).total_seconds() > HAN_TREO_GIO * 3600:
            return None             # treo quá lâu → cho phóng lại
    except (TypeError, ValueError):
        pass
    return viec


def _doc_trang_thai(log: Path) -> tuple[dt.date | None, str]:
    """Dùng LẠI `lan_chay_cuoi()` của `kiem_do_tuoi_chung_cu` — MỘT bản duy nhất.

    Hai công cụ này hỏi cùng một câu ("lượt giám sát cuối ra sao?") nên phải dùng
    chung một câu trả lời; hai bản riêng sẽ phân kỳ đúng như đã xảy ra hôm nay.
    """
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_dotuoi", Path(__file__).resolve().parent / "kiem_do_tuoi_chung_cu.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m.lan_chay_cuoi(log)
    except Exception:  # noqa: BLE001 — chốt không được phép làm chết phiên
        if not (log.exists() and log.stat().st_size > 0):
            return None, ""
        return dt.date.fromtimestamp(log.stat().st_mtime), ""


def qua_han() -> list[tuple[str, int]]:
    """Các việc đã quá hạn, kèm số ngày kể từ lần chạy cuối (-1 = chưa từng chạy).

    VÁ 14/08/2026 — VÁ DỞ DANG CỦA CHÍNH HÔM QUA. `kiem_do_tuoi_chung_cu` đã được
    sửa để đọc KẾT QUẢ lượt chạy thay vì chỉ nhìn `st_mtime`, nhưng hàm này — dùng
    CÙNG tín hiệu cho CÙNG mục đích — thì bị bỏ sót.

    Hậu quả nếu để nguyên: hai script giám sát ghi "BẮT ĐẦU" ngay lúc khởi động, nên
    một lượt **khởi động rồi chết** vẫn làm mtime tươi ⇒ `qua_han()` kết luận "còn
    hạn" ⇒ **KHÔNG phóng lại**. Giám sát hỏng vĩnh viễn mà không bao giờ được thử lại,
    và cũng không ai được báo. Đúng vòng lặp im lặng mà BH19 vừa bịt ở đầu kia.

    Nay: lượt cuối LỖI hoặc CHƯA KHÉP LẠI ⇒ coi như cần chạy lại, bất kể mtime.
    """
    ra: list[tuple[str, int]] = []
    hom_nay = dt.date.today()
    for ma, v in OWNER.items():
        log = v["log"]
        if not log.exists() or log.stat().st_size == 0:
            ra.append((ma, -1))
            continue
        ngay, tt = _doc_trang_thai(log)
        if ngay is None:
            ra.append((ma, -1))
            continue
        cach = (hom_nay - ngay).days
        if tt == "LỖI":
            ra.append((ma, cach))          # lượt cuối hỏng → phải chạy lại
        elif tt == "DANG_DO":
            # Có BẮT ĐẦU mà không có KẾT THÚC: đang chạy dở, hoặc đã chết. Khoá PID
            # ở `dang_chay()` lo trường hợp ĐANG chạy; tới đây nghĩa là tiến trình
            # không còn sống ⇒ lượt đó đã chết giữa chừng, cần chạy lại.
            ra.append((ma, cach))
        elif cach > v["han_ngay"]:
            ra.append((ma, cach))
    return ra


def phong(ma: str) -> tuple[bool, str]:
    """Phóng script chủ sở hữu ở NỀN, tách hẳn khỏi phiên Claude.

    Tách tiến trình là bắt buộc: một lượt quét đi mạng có thể mất nhiều phút, mà
    hook SessionStart chỉ có vài chục giây. Chạy đồng bộ sẽ làm treo lúc mở phiên —
    đúng kiểu phiền toái khiến người ta tắt luôn cơ chế tự động.
    """
    v = OWNER[ma]
    sc = v["script"]
    if not sc.exists():
        return False, f"không thấy {sc.relative_to(REPO)}"
    NHAT_KY.parent.mkdir(parents=True, exist_ok=True)
    try:
        f = open(NHAT_KY, "a", encoding="utf-8")
        f.write(f"\n===== {dt.datetime.now():%Y-%m-%d %H:%M:%S} : TỰ PHÓNG {ma} =====\n")
        f.flush()
        kw: dict = {"cwd": str(PROJ), "stdout": f, "stderr": subprocess.STDOUT, "stdin": subprocess.DEVNULL}
        if sys.platform == "win32":
            # CREATE_NEW_PROCESS_GROUP + DETACHED_PROCESS: sống tiếp khi phiên đóng
            kw["creationflags"] = 0x00000200 | 0x00000008
            lenh = ["bash", str(sc)]
        else:
            kw["start_new_session"] = True     # tách session → không chết theo Claude
            lenh = ["bash", str(sc)]
        p = subprocess.Popen(lenh, **kw)  # noqa: S603 — lệnh từ allowlist OWNER, không từ đầu vào
    except (OSError, subprocess.SubprocessError) as e:
        return False, f"không phóng được: {e}"
    _ghi_khoa({"pid": p.pid, "viec": ma, "luc": dt.datetime.now().isoformat(timespec="seconds")})
    return True, f"đã phóng ở nền (pid {p.pid}), ghi vào {NHAT_KY.relative_to(REPO)}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Tự khởi động giám sát chứng cứ")
    ap.add_argument("--phong", action="store_true", help="thật sự phóng ở nền")
    ap.add_argument("--im-khi-on", action="store_true", help="chỉ nói khi có việc")
    ap.add_argument("--tat", action="store_true", help="tắt hẳn cơ chế tự khởi động")
    ap.add_argument("--bat", action="store_true", help="bật lại")
    a = ap.parse_args()

    if a.tat:
        CONG_TAC_TAT.write_text("Tắt tự khởi động giám sát. Xoá file này để bật lại.\n",
                                encoding="utf-8")
        print("✓ ĐÃ TẮT tự khởi động. Giám sát chỉ chạy khi bác sĩ gọi tay.")
        return 0
    if a.bat:
        CONG_TAC_TAT.unlink(missing_ok=True)
        print("✓ ĐÃ BẬT lại tự khởi động.")
        return 0
    if CONG_TAC_TAT.exists():
        if not a.im_khi_on:
            print("⏸ Tự khởi động ĐANG TẮT (có file .tu-khoi-dong-tat).")
        return 0

    đang = dang_chay()
    if đang:
        if not a.im_khi_on:
            print(f"⏳ Đang chạy: {OWNER[đang]['ten']} — chờ xong, không phóng chồng.")
        return 0

    can = qua_han()
    if not can:
        if not a.im_khi_on:
            print("🟢 Giám sát còn hạn — không cần phóng.")
        return 0

    # Chỉ phóng MỘT việc mỗi lượt: hai lượt quét mạng cùng lúc dễ bị nguồn chặn IP,
    # và bản thân việc bị chặn lại tạo báo động giả ở chốt kiểm nguồn.
    ma, cach = can[0]
    ten = OWNER[ma]["ten"]
    mo_ta = "CHƯA TỪNG chạy" if cach < 0 else f"quá hạn {cach} ngày"

    if not a.phong:
        print(f"▸ {ten}: {mo_ta} → sẽ phóng ở nền (thêm --phong để làm thật).")
        return 1

    ok, tin = phong(ma)
    if a.im_khi_on:
        print("")
    print(f"{'🚀' if ok else '⚠'} TỰ KHỞI ĐỘNG: {ten} ({mo_ta}) — {tin}")
    if ok:
        print("   Chạy ở nền, không chặn phiên. Kết quả vào hàng ỨNG VIÊN;")
        print("   KHÔNG tự phát hành — Cổng A/B vẫn do bác sĩ giữ.")
        print("   Tắt hẳn: python3 tools/tu_khoi_dong.py --tat")
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
