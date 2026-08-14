#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nhắc khi GIÁM SÁT CHỨNG CỨ quá hạn — thay cho lịch launchd vốn không nổ.

VÌ SAO CÓ (11/08/2026):
Hai job launchd `com.medicalebm.weeklysafety` (thứ Bảy 19:00) và
`com.medicalebm.monthlyupdate` (mùng 1, 18:00) khi kiểm thực tế đều cho
`runs = 0` · `last exit code = (never exited)`, log 0 byte từ 06/06 — tức
**chưa từng chạy một lần nào** kể từ khi cài (11/07). Từ đó tới nay đã lỡ 5 thứ
Bảy và 1 mùng 1.

Nguyên nhân: `StartCalendarInterval` của launchd đòi máy phải ĐANG THỨC đúng
thời điểm. MacBook đóng nắp lúc 19:00 thứ Bảy thì job không chạy, và launchd
không bù lại một cách đáng tin.

Máy móc bên dưới KHÔNG hỏng — chạy `weekly_safety.sh --canary` ngày 11/08 cho
PASS toàn bộ: 4/4 nguồn khoẻ (PubMed · Europe PMC · Crossref · openFDA),
scanner tìm được ứng viên, cổng dashboard strict PASS. Chỉ là không ai bật.

Nên cách vá hợp thói quen bác sĩ nhất: bác sĩ mở phiên Claude gần như mỗi ngày,
vậy NHẮC ngay lúc mở phiên. Không phụ thuộc máy có thức lúc 19:00 hay không.

Công cụ này CHỈ NHẮC, không tự chạy giám sát: quét chứng cứ là việc gọi mạng và
sinh nội dung y khoa, phải do bác sĩ chủ động và duyệt kết quả.

Dùng:
    python3 tools/kiem_do_tuoi_chung_cu.py            # in trạng thái
    python3 tools/kiem_do_tuoi_chung_cu.py --im-khi-on  # chỉ nói khi quá hạn (hook)

Mã thoát: 0 = còn hạn · 1 = quá hạn.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]
DASH = REPO / "EBM-Dashboards"
LOG_TUAN = REPO / "medical-ebm-automation/data/archive/launchd_weekly.log"
LOG_THANG = REPO / "medical-ebm-automation/data/archive/launchd_monthly.log"

# Ngưỡng nới hơn chu kỳ danh nghĩa: job tuần trễ 3 ngày chưa đáng gọi là bỏ bê.
HAN_AN_TOAN_NGAY = 10      # giám sát an toàn thuốc: chu kỳ tuần
HAN_CAP_NHAT_NGAY = 35     # cập nhật guideline: chu kỳ tháng
# Ngưỡng RIÊNG cho "chủ đề lâu chưa xem lại", cố ý cao hơn HAN_CAP_NHAT_NGAY nhiều.
# Lý do là chống nhờn cảnh báo: ở nhịp làm việc thật, phần lớn chủ đề luôn quá 35 ngày
# (đo 14/08: 37/59), nên lấy 35 làm ngưỡng báo động sẽ khiến mỗi phiên đều đỏ và bác sĩ
# học cách bỏ qua — lúc đó cảnh báo thật cũng chìm theo. 120 ngày là mức mà "chưa xem
# lại" khó biện minh với gần như mọi lĩnh vực.
HAN_RAT_LAU_NGAY = 120


def ngay_tu_ten(p: Path) -> dt.date | None:
    """Lấy ngày từ đuôi tên file `..._YYYYMMDD.html` — đáng tin hơn mtime, vì
    mtime bị OneDrive và các lần dựng lại vỏ (reskin) làm nhiễu."""
    m = re.search(r"_(\d{8})\.html$", p.name)
    if not m:
        return None
    try:
        return dt.datetime.strptime(m.group(1), "%Y%m%d").date()
    except ValueError:
        return None


def lan_chay_cuoi(log: Path) -> tuple[dt.date | None, str]:
    """(ngày lần chạy cuối, trạng thái) — trạng thái ∈ PASS · LỖI · DANG_DO · "".

    VÁ 13/08/2026 — bản cũ CHỈ đọc `st_mtime` rồi kết luận "còn hạn". Nhưng hai script
    giám sát ghi dòng "BẮT ĐẦU" vào log **NGAY khi khởi động**, trước khi làm bất cứ
    việc gì ⇒ một lượt chạy KHỞI ĐỘNG RỒI CHẾT vẫn làm mtime tươi mới, và bác sĩ nhận
    "🟢 CHỨNG CỨ còn hạn" trong khi giám sát thật sự đã hỏng.

    Từ khi `tu_khoi_dong.py` tự phóng mỗi phiên, điều này thành vòng lặp im lặng:
    phóng → hỏng → mtime tươi → "còn hạn" → không ai biết. Chính log ĐÃ chứa câu trả
    lời (dòng "KẾT THÚC … tổng thể=PASS | CÓ BƯỚC LỖI") — chỉ là chưa ai đọc.
    """
    if not (log.exists() and log.stat().st_size > 0):
        return None, ""
    ngay = dt.date.fromtimestamp(log.stat().st_mtime)
    try:
        dong = log.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ngay, ""
    for d in reversed(dong):
        if "KẾT THÚC" in d:
            return ngay, ("PASS" if "tổng thể=PASS" in d else "LỖI")
        if "BẮT ĐẦU" in d:
            # Gặp BẮT ĐẦU trước KẾT THÚC ⇒ lượt cuối chưa khép lại: đang chạy, hoặc
            # đã chết giữa chừng. Cả hai đều KHÔNG được coi là một lượt giám sát xong.
            return ngay, "DANG_DO"
    return ngay, ""


def launchd_runs(nhan: str) -> int | None:
    """Số lần job launchd đã chạy — CHỈ macOS mới có launchd.

    Trên Windows trả None (không phải lỗi): ở đó không có lịch nền nào để hỏi,
    nhưng chốt này vẫn nhắc được theo dấu vết log và ngày gói chứng cứ.

    VÁ 12/08/2026: bản cũ gọi `os.getuid()` — hàm KHÔNG tồn tại trên Windows —
    và chỉ bắt (OSError, SubprocessError), nên AttributeError lọt ra ngoài làm
    CHẾT cả công cụ. Vì hook SessionStart kết thúc bằng `; true`, lỗi bị nuốt
    IM LẶNG: suốt thời gian qua máy Windows không hề được nhắc độ tươi chứng cứ
    mà không ai biết. Đây đúng lớp lỗi "công cụ dùng chung gãy im lặng trên
    Windows" đã gặp nhiều lần — nên bắt Exception rộng, không đoán trước tên lỗi.
    """
    if sys.platform != "darwin":
        return None
    import os

    try:
        r = subprocess.run(["launchctl", "print", f"gui/{os.getuid()}/{nhan}"],
                           capture_output=True, text=True, timeout=10)
        m = re.search(r"runs = (\d+)", r.stdout)
        return int(m.group(1)) if m else None
    except Exception:  # noqa: BLE001 — chốt nhắc không được phép làm chết phiên
        return None


def lau_chua_xem_lai() -> list[tuple[str, int]]:
    """[(lát cắt, số ngày kể từ bản mới nhất của nó)] — xếp cũ nhất lên đầu.

    VÌ SAO CÓ (14/08/2026, vòng lặp kiểm tra–hoàn thiện vòng 3): mục (1) của công cụ
    này lấy `max(ngày)` trên toàn kho, nên **một gói mới làm cả kho trông còn hạn**.
    Đo thật hôm nay: gói mới nhất 1 ngày tuổi ⇒ in 🟢, trong khi 37/59 chủ đề đã quá
    35 ngày và trung vị là 45 ngày. Bác sĩ đọc dòng 🟢 đó sẽ tin rằng mọi chủ đề đều
    vừa được rà — đúng loại bảo đảm sai mà kho này đã vấp nhiều lần.

    Đơn vị đếm là LÁT CẮT, không phải file: ba bản SuyTim_TongHop nối tiếp nhau chỉ
    là một chủ đề được xem lại ba lần, không phải ba chủ đề.

    Công cụ CHỈ ĐO, không phán "đã lỗi thời": nhịp cập nhật của mỗi lĩnh vực rất khác
    nhau (cảnh báo thuốc tính bằng tuần, guideline tính bằng năm), và quyết định xem
    lại chủ đề nào trước là của bác sĩ.
    """
    import datetime as _dt
    hom_nay = _dt.date.today()
    moi_nhat: dict[str, _dt.date] = {}
    for p in DASH.glob("WebDashboard_*.html"):
        d = ngay_tu_ten(p)
        if not d:
            continue
        # Lát cắt = tên file bỏ tiền tố nhóm và bỏ ngày.
        m = re.match(r"WebDashboard_EBM_(?:VanDeCuThe|Uptodate|CapNhatTuan|AnToanThuoc|"
                     r"CongCuKeDon)_(?:(.+?)_)?\d{8}\.html$", p.name)
        if not m:
            continue
        lc = m.group(1) or p.name.split("_")[2]
        if lc not in moi_nhat or d > moi_nhat[lc]:
            moi_nhat[lc] = d
    return sorted(((k, (hom_nay - v).days) for k, v in moi_nhat.items()),
                  key=lambda kv: -kv[1])


def in_bang_tuoi(lau: list[tuple[str, int]]) -> None:
    """In phân bố tuổi để dòng 🟢 ở trên không bị đọc quá rộng."""
    if not lau:
        return
    tuoi = [t for _k, t in lau]
    qua = sum(1 for t in tuoi if t > HAN_CAP_NHAT_NGAY)
    print(f"   {len(lau)} chủ đề · trung vị {sorted(tuoi)[len(tuoi) // 2]} ngày kể từ lần "
          f"xem lại · {qua} chủ đề quá {HAN_CAP_NHAT_NGAY} ngày")
    if qua:
        ten = " · ".join(f"{k} ({t}ng)" for k, t in lau[:5])
        print(f"   Lâu nhất: {ten}")
        print("   (Đây là số ĐO, không phải phán quyết 'đã lỗi thời' — nhịp cập nhật mỗi")
        print("    lĩnh vực một khác, chọn chủ đề xem lại trước là quyết định của bác sĩ.)")


def main() -> int:
    ap = argparse.ArgumentParser(description="Nhắc khi giám sát chứng cứ quá hạn")
    ap.add_argument("--im-khi-on", action="store_true",
                    help="không in gì khi còn hạn (dùng cho hook)")
    a = ap.parse_args()

    hom_nay = dt.date.today()
    canh_bao: list[str] = []

    # 1) Gói chứng cứ mới nhất — thước đo trực tiếp nhất của "hệ có đang sống không"
    ngays = [d for d in (ngay_tu_ten(p) for p in DASH.glob("WebDashboard_*.html")) if d]
    mới_nhất = max(ngays) if ngays else None
    if mới_nhất:
        cach = (hom_nay - mới_nhất).days
        if cach > HAN_CAP_NHAT_NGAY:
            canh_bao.append(
                f"Gói chứng cứ mới nhất là {mới_nhất:%d/%m/%Y} — cách đây {cach} ngày "
                f"(ngưỡng {HAN_CAP_NHAT_NGAY}). Chạy `/cap-nhat-chung-cu <vấn đề>` "
                f"cho chủ đề đang cần.")

    # 2) Giám sát an toàn thuốc hằng tuần
    chay_tuan, tt_tuan = lan_chay_cuoi(LOG_TUAN)
    runs = launchd_runs("com.medicalebm.weeklysafety")
    if chay_tuan is None:
        if sys.platform == "darwin":
            n = "" if runs is None else f" (launchd runs = {runs})"
            ly_do = (f"{n}. Lịch launchd đòi máy thức lúc 19:00 thứ Bảy nên hay lỡ")
        else:
            # Windows KHÔNG có launchd — hai job com.medicalebm.* chỉ tồn tại trên Mac.
            # Nói rõ điều này, thay vì để bác sĩ tưởng có lịch nền đang chạy hộ.
            ly_do = (". Máy này (Windows) KHÔNG có lịch nền nào chạy giám sát — "
                     "hai job launchd chỉ tồn tại trên MacBook, nên ở đây luôn phải chạy tay")
        canh_bao.append(
            f"Giám sát AN TOÀN THUỐC hằng tuần CHƯA TỪNG chạy{ly_do}. Chạy tay khi tiện:\n"
            f"     bash medical-ebm-automation/scripts/weekly_safety.sh\n"
            f"     (kiểm nhanh nguồn, không ghi gì: thêm `--canary`)")
    else:
        cach = (hom_nay - chay_tuan).days
        # Lượt chạy HỎNG hoặc chưa khép lại KHÔNG được tính là một lượt giám sát xong,
        # dù log vừa được ghi (script ghi 'BẮT ĐẦU' ngay lúc khởi động).
        if tt_tuan == "LỖI":
            canh_bao.append(
                f"Giám sát an toàn thuốc lượt cuối ({chay_tuan:%d/%m/%Y}) CÓ BƯỚC LỖI — "
                f"log ghi 'tổng thể=CÓ BƯỚC LỖI'. Chạy lại và đọc "
                f"medical-ebm-automation/data/archive/launchd_weekly.log để biết bước nào.")
        elif tt_tuan == "DANG_DO":
            canh_bao.append(
                f"Giám sát an toàn thuốc lượt cuối ({chay_tuan:%d/%m/%Y}) CHƯA KHÉP LẠI — "
                f"log có 'BẮT ĐẦU' mà không có 'KẾT THÚC': đang chạy dở, hoặc đã chết "
                f"giữa chừng. KHÔNG tính là một lượt giám sát xong.")
        elif cach > HAN_AN_TOAN_NGAY:
            canh_bao.append(
                f"Giám sát an toàn thuốc chạy lần cuối {chay_tuan:%d/%m/%Y} — "
                f"cách đây {cach} ngày (ngưỡng {HAN_AN_TOAN_NGAY}).")

    # 3) TUỔI TỪNG CHỦ ĐỀ — thứ mà `max()` ở mục (1) không nói được.
    lau = lau_chua_xem_lai()
    rat_lau = [x for x in lau if x[1] > HAN_RAT_LAU_NGAY]
    if rat_lau:
        ten = ", ".join(f"{k} ({t}ng)" for k, t in rat_lau[:3])
        canh_bao.append(
            f"{len(rat_lau)} chủ đề chưa xem lại quá {HAN_RAT_LAU_NGAY} ngày: {ten}"
            + (f" và {len(rat_lau) - 3} chủ đề nữa" if len(rat_lau) > 3 else "")
            + ". Chạy `/cap-nhat-chung-cu <chủ đề>` cho mục cần trước.")

    if not canh_bao:
        if not a.im_khi_on:
            # NÓI ĐÚNG THỨ ĐÃ ĐO. Câu cũ "CHỨNG CỨ còn hạn" suy từ `max(ngày)` — tức
            # chỉ cần MỘT gói mới là cả kho trông còn hạn. Đo 14/08/2026: gói mới nhất
            # 1 ngày tuổi trong khi 37/59 chủ đề đã quá 35 ngày, trung vị 45 ngày. Một
            # dòng 🟢 đọc thành "mọi chủ đề đều mới" là lời bảo đảm không có cơ sở —
            # cùng lớp lỗi BH15/BH30: con số không đo thứ nó tự nhận là đang đo.
            print(f"🟢 HỆ GIÁM SÁT còn hoạt động — gói mới nhất {mới_nhất:%d/%m/%Y}"
                  if mới_nhất else "🟢 HỆ GIÁM SÁT còn hoạt động")
            in_bang_tuoi(lau)
        return 0

    if a.im_khi_on:
        print("")
    print("🟡 GIÁM SÁT CHỨNG CỨ QUÁ HẠN")
    for c in canh_bao:
        print(f"   • {c}")
    print("   (Chốt này chỉ NHẮC — quét chứng cứ phải do bác sĩ chủ động và duyệt kết quả.)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
