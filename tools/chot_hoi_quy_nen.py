#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CHỐT HỒI QUY CHẠY NỀN — hook SessionStart chỉ ĐỌC kết quả, không chạy trọn bộ chốt (HV-01, 02/10/2026).

VÌ SAO CÓ. Hook `SessionStart` chạy `chot_hoi_quy_bai_hoc.py --im-khi-on` với `timeout: 30`, nhưng bộ chốt cần
46–55 giây trên máy thật. Đo 02/10/2026: hook hết hạn ở 18/19 phiên từ 24/09 ⇒ lưới an toàn «mù» 8 ngày, và vì
lệnh hook kết thúc bằng `; true` + chế độ `--im-khi-on` im lặng khi không có gì đỏ, «hook bị cắt giữa chừng» đọc
GIỐNG HỆT «mọi chốt xanh» (im lặng bị đọc thành xanh — cùng họ lỗi đã ghi ở CLAUDE.md §0.2).

CÁCH LÀM.
    python3 tools/chot_hoi_quy_nen.py --doc --im-khi-on   # hook: đọc state/chot-hoi-quy-gan-nhat.json (< 1 giây),
                                                          # nếu kết quả cũ thì tự phóng một lượt NỀN rồi trả ngay
    python3 tools/chot_hoi_quy_nen.py --chay              # chạy trọn bộ chốt (chặn), ghi kết quả — lượt nền gọi cái này
Ba trạng thái hiển thị, KHÔNG có trạng thái im lặng nào ngoài «xanh THẬT, còn mới»:
    XANH  (im lặng)  lượt đo gần nhất ≤ 72 giờ trước và 0 chốt đỏ.
    ĐỎ    (in)       có chốt đỏ — in nguyên báo cáo của bộ chốt kèm giờ đo (mã thoát 1).
    CHƯA ĐO ĐƯỢC (in 🟡)  không có kết quả / hỏng / cũ hơn 72 giờ / lượt gần nhất LỖI (mã thoát 2) —
                          TUYỆT ĐỐI không đọc thành «ổn».
Làm mới nền khi: chưa có kết quả, cũ hơn 6 giờ, hoặc HEAD git đã đổi so với lúc đo. Khoá `state/` chống hai lượt
nền chạy chồng (quá 20 phút coi là khoá mồ côi). Chỉ ĐO và BÁO — không sửa gì, không đổi mã thoát của bộ chốt.

Chạy trên cả Mac lẫn Windows: `sys.executable`, tách tiến trình bằng `start_new_session` / `DETACHED_PROCESS`, ép UTF-8.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
THU_MUC_STATE = REPO / "state"
TEP_KET_QUA = THU_MUC_STATE / "chot-hoi-quy-gan-nhat.json"
TEP_KHOA = THU_MUC_STATE / "chot-hoi-quy-nen.khoa"

NGUONG_CU_GIO = 72          # cũ hơn ⇒ «CHƯA ĐO ĐƯỢC», không bao giờ là «xanh»
NGUONG_LAM_MOI_GIO = 6      # cũ hơn ⇒ phóng lượt nền mới
KHOA_HET_HAN_PHUT = 20      # khoá cũ hơn ⇒ coi là mồ côi (lượt nền chết giữa chừng)
HAN_CHAY_GIAY = 900         # trần một lượt chạy trọn bộ chốt
GIOI_HAN_BAO_CAO = 4000     # ký tự báo cáo giữ lại trong kết quả

MA_XANH, MA_DO, MA_CHUA_DO = 0, 1, 2


def _bay_gio() -> datetime:
    return datetime.now(timezone.utc)


def _dinh_dang(t: datetime) -> str:
    return t.astimezone().strftime("%d/%m %H:%M")


def head_hien_tai() -> str:
    """SHA HEAD của cây làm việc; rỗng nếu không hỏi được (không coi là «đổi»)."""
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(REPO), capture_output=True, text=True,
                           timeout=8, encoding="utf-8", errors="replace")
    except (OSError, subprocess.SubprocessError):
        return ""
    return r.stdout.strip() if r.returncode == 0 else ""


def doc_ket_qua(duong_dan: Path | None = None) -> dict | None:
    """Đọc kết quả gần nhất; hỏng/thiếu/sai kiểu ⇒ None (người gọi báo CHƯA ĐO ĐƯỢC, không báo xanh)."""
    duong_dan = duong_dan or TEP_KET_QUA  # tra lúc GỌI, không chốt lúc nạp mô-đun (test vá được hằng)
    try:
        d = json.loads(duong_dan.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(d, dict) or d.get("trang_thai") not in ("XANH", "DO", "LOI"):
        return None
    if not isinstance(d.get("ket_thuc"), str):
        return None
    return d


def danh_gia(kq: dict | None, bay_gio: datetime, head: str) -> tuple[str, str, bool]:
    """Trả (loại, thông điệp, cần_làm_mới). loại ∈ XANH_IM | DO | CHUA_DO.

    HÀM THUẦN — không đọc đĩa, không gọi git — để test hành vi trực tiếp."""
    if kq is None:
        return ("CHUA_DO", "chưa có kết quả đo (lần đầu hoặc tệp hỏng)", True)
    try:
        t = datetime.fromisoformat(kq["ket_thuc"])
        if t.tzinfo is None:
            t = t.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return ("CHUA_DO", "dấu thời gian của kết quả không đọc được", True)
    tuoi = bay_gio - t
    if tuoi < timedelta(minutes=-5):  # đồng hồ lệch/dấu thời gian tương lai: không tin
        return ("CHUA_DO", "dấu thời gian của kết quả nằm trong TƯƠNG LAI (đồng hồ lệch?)", True)
    gio = tuoi.total_seconds() / 3600
    doi_head = bool(head) and bool(kq.get("head")) and kq.get("head") != head
    can_moi = gio > NGUONG_LAM_MOI_GIO or doi_head
    luc = _dinh_dang(t)
    if gio > NGUONG_CU_GIO:
        return ("CHUA_DO", f"lượt đo gần nhất {luc} đã cũ {gio:.0f} giờ (> {NGUONG_CU_GIO})", True)
    if kq["trang_thai"] == "LOI":
        return ("CHUA_DO", f"lượt chạy nền {luc} bị LỖI: {str(kq.get('bao_cao') or '')[:300]}", True)
    if kq["trang_thai"] == "DO":
        ghi_chu = f"[đo lúc {luc}, {gio:.0f} giờ trước" + (" · mã đã đổi từ lúc đó, đang đo lại" if doi_head else "") + "]"
        return ("DO", f"{str(kq.get('bao_cao') or '').strip()}\n  {ghi_chu}", can_moi)
    return ("XANH_IM", "", can_moi)


def khoa_con_hieu_luc(bay_gio: datetime) -> bool:
    try:
        t = datetime.fromtimestamp(TEP_KHOA.stat().st_mtime, tz=timezone.utc)
    except OSError:
        return False
    return (bay_gio - t) < timedelta(minutes=KHOA_HET_HAN_PHUT)


def phong_nen() -> bool:
    """Phóng MỘT lượt `--chay` tách khỏi hook rồi trả ngay. False nếu đang có lượt khác hoặc không phóng được."""
    if khoa_con_hieu_luc(_bay_gio()):
        return False
    kw: dict = {"stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL,
                "cwd": str(REPO)}
    if os.name == "nt":
        kw["creationflags"] = (getattr(subprocess, "DETACHED_PROCESS", 0)
                               | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))
    else:
        kw["start_new_session"] = True
    try:
        subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--chay"], **kw)
    except OSError:
        return False
    return True


def _ghi_nguyen_tu(duong_dan: Path, noi_dung: str) -> None:
    duong_dan.parent.mkdir(parents=True, exist_ok=True)
    tam = duong_dan.with_name(duong_dan.name + f".tmp{os.getpid()}")
    tam.write_text(noi_dung, encoding="utf-8", newline="\n")
    os.replace(tam, duong_dan)


def _lay_khoa() -> bool:
    """Tạo khoá nguyên tử. False nếu lượt khác đang giữ khoá còn hiệu lực."""
    THU_MUC_STATE.mkdir(parents=True, exist_ok=True)
    if TEP_KHOA.exists() and not khoa_con_hieu_luc(_bay_gio()):
        try:
            TEP_KHOA.unlink()
        except OSError:
            pass
    try:
        fd = os.open(str(TEP_KHOA), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return False
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write(str(os.getpid()))
    return True


def chay_tron_bo_chot() -> int:
    """Chạy trọn bộ chốt, ghi `state/chot-hoi-quy-gan-nhat.json`. Mã thoát: 0 xong · 3 đang có lượt khác."""
    if not _lay_khoa():
        print("đang có một lượt chạy nền khác — bỏ qua", file=sys.stderr)
        return 3
    bat_dau = _bay_gio()
    try:
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        try:
            r = subprocess.run([sys.executable, str(REPO / "tools" / "chot_hoi_quy_bai_hoc.py"), "--im-khi-on"],
                               cwd=str(REPO), capture_output=True, text=True, timeout=HAN_CHAY_GIAY, env=env,
                               encoding="utf-8", errors="replace")
            ma = r.returncode
            bao_cao = (r.stdout or "").strip()
            if ma not in (0, 1):
                bao_cao = f"mã thoát {ma}: {(r.stderr or '').strip()[-600:] or bao_cao[-600:]}"
            trang_thai = {0: "XANH", 1: "DO"}.get(ma, "LOI")
        except subprocess.TimeoutExpired:
            ma, trang_thai, bao_cao = -1, "LOI", f"quá hạn {HAN_CHAY_GIAY} giây — bộ chốt không chạy xong"
        except OSError as e:
            ma, trang_thai, bao_cao = -2, "LOI", f"không chạy được bộ chốt: {e}"
        ket_thuc = _bay_gio()
        _ghi_nguyen_tu(TEP_KET_QUA, json.dumps({
            "schema": 1,
            "bat_dau": bat_dau.isoformat(),
            "ket_thuc": ket_thuc.isoformat(),
            "giay": round((ket_thuc - bat_dau).total_seconds(), 1),
            "ma_thoat": ma,
            "trang_thai": trang_thai,
            "bao_cao": bao_cao[:GIOI_HAN_BAO_CAO],
            "head": head_hien_tai(),
        }, ensure_ascii=False, indent=1) + "\n")
        return 0
    finally:
        try:
            TEP_KHOA.unlink()
        except OSError:
            pass


def doc_va_bao(im_khi_on: bool) -> int:
    """Chế độ hook: đọc, in đúng điều cần in, phóng nền nếu cần. Không bao giờ chặn quá vài trăm mili-giây."""
    loai, thong_diep, can_moi = danh_gia(doc_ket_qua(), _bay_gio(), head_hien_tai())
    da_phong = phong_nen() if can_moi else False
    if loai == "DO":
        print("\n🔴 CHỐT HỒI QUY (kết quả lượt nền gần nhất):")
        print(thong_diep)
        return MA_DO
    if loai == "CHUA_DO":
        print(f"🟡 CHỐT HỒI QUY: CHƯA ĐO ĐƯỢC — {thong_diep}."
              + (" Đang chạy nền, kết quả hiện ở phiên sau." if da_phong else "")
              + " KHÔNG đọc là «xanh».")
        return MA_CHUA_DO
    if not im_khi_on:
        print("CHỐT HỒI QUY (nền) — xanh, lượt đo gần nhất còn hạn.")
    return MA_XANH


def main(argv: list[str] | None = None) -> int:
    for luong in (sys.stdout, sys.stderr):
        try:
            if "utf" not in (getattr(luong, "encoding", "") or "").lower() and hasattr(luong, "reconfigure"):
                luong.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Chốt hồi quy chạy nền: hook chỉ đọc kết quả")
    nhom = ap.add_mutually_exclusive_group()
    nhom.add_argument("--doc", action="store_true", help="(mặc định) đọc kết quả gần nhất, phóng nền khi cũ")
    nhom.add_argument("--chay", action="store_true", help="chạy trọn bộ chốt (chặn) và ghi kết quả")
    ap.add_argument("--im-khi-on", action="store_true", help="im lặng khi xanh THẬT và còn mới")
    a = ap.parse_args(argv)
    if a.chay:
        return chay_tron_bo_chot()
    return doc_va_bao(a.im_khi_on)


if __name__ == "__main__":
    sys.exit(main())
