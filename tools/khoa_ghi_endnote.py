#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""khoa_ghi_endnote.py — KHOÁ «Claude đang ghi EndNote» (19/10/2026).

Sự cố 18/10/2026: Claude đang chuyển bản ghi vào thùng rác bằng giao diện thì bác sĩ cũng thao tác trên EndNote ⇒ 7 bản ghi
Unfiled bị chuyển vào thùng rác ngoài ý định của Claude. Bác sĩ 19/10/2026: «Hãy làm tất cả 6 việc giúp tôi» (việc 4: khoá ghi).

Mọi lệnh GHI vào EndNote của `nap_endnote_chu_de.EndNoteMac` (nhập, đăng vào nhóm, gắn tệp, ghi trường) gọi `cho_phep_ghi()`
trước. Hàm này:
  1. Chờ khi BÁC SĨ ĐANG DÙNG EndNote (EndNote là ứng dụng đang ở trước VÀ bàn phím/chuột vừa được dùng < NGUONG_RANH giây),
     tối đa CHO_TOI_DA giây; quá hạn ⇒ ném `BacSiDangDungEndNote` — người gọi BỎ lượt ghi và báo, không ghi chen.
  2. Giữ tệp khoá `~/.ebm-endnote-dang-ghi.json` (pid + giờ + lý do); một tiến trình Claude khác đang giữ khoá còn sống ⇒
     chờ rồi ném `DangCoTienTrinhKhacGhi`. Khoá của tiến trình đã chết hoặc quá HAN_KHOA giây ⇒ coi như bỏ. Mỗi lệnh ghi khi
     đang giữ khoá LÀM MỚI `luc_epoch` ⇒ khoá của tiến trình đang ghi dở không bị tiến trình khác coi là treo.
  3. Hiện MỘT thông báo macOS «Claude đang ghi EndNote: <lý do>» cho mỗi LẦN LẤY khoá (không lặp mỗi lệnh ghi).

Hai cách giữ khoá (24/10/2026):
  • THEO TIẾN TRÌNH (mặc định — script ngắn như `nap_endnote_chu_de.py`, `xuat_goi_cap_nhat.py` bước ⑧): lấy ở lần ghi đầu,
    nhả bằng `atexit` khi tiến trình thoát.
  • THEO PHẠM VI một thao tác — `with giu_khoa_ghi(...):` — cho tiến trình SỐNG LÂU (máy chủ MCP `endnote-ebm` sống cả phiên
    Claude): khoá lấy trong khối được nhả NGAY khi ra khỏi khối, kể cả khi lỗi. Sự cố đo 24/10/2026: sau MỘT lệnh ghi của
    MCP, khoá bị giữ tới khi quá HAN_KHOA (15 phút) ⇒ bộ năm VKDT_TongHop_20261024 bị bỏ bước ⑧ (`DangCoTienTrinhKhacGhi`:
    pid máy chủ MCP). Trạng thái khoá là biến của mô-đun ⇒ phạm vi chỉ thấy lần ghi đi qua CÙNG bản mô-đun: nạp bằng
    `nap_endnote_chu_de.nap_khoa_ghi()` (một bản cho cả tiến trình), không `spec_from_file_location` riêng.
Đo hoạt động: `lsappinfo` (ứng dụng ở trước — không cần quyền Trợ năng) + `ioreg IOHIDSystem` (giây rảnh). Không đo được ⇒
coi là RẢNH (fail-open có chủ ý: khoá chỉ để không ghi chen khi bác sĩ đang thao tác, không được làm hỏng dây chuyền nền).
Dưới pytest (`PYTEST_CURRENT_TEST`) hàm công khai không đo, không ghi khoá — test gọi hàm lõi với bộ đo giả.
"""
from __future__ import annotations

import atexit
import contextlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

TEP_KHOA = Path.home() / ".ebm-endnote-dang-ghi.json"
NGUONG_RANH = 20       # bàn phím/chuột rảnh ≥ 20 giây ⇒ bác sĩ không đang thao tác
CHO_TOI_DA = 120       # chờ bác sĩ rảnh tối đa 2 phút rồi bỏ lượt ghi
HAN_KHOA = 15 * 60     # khoá quá 15 phút coi là treo
_DANG_GIU = {"pid": None, "tep": None, "thong_bao": False, "pham_vi": 0, "tu_pham_vi": False, "atexit": False}


class BacSiDangDungEndNote(RuntimeError):
    """Bác sĩ đang thao tác trên EndNote — không ghi chen."""


class DangCoTienTrinhKhacGhi(RuntimeError):
    """Một tiến trình Claude khác đang giữ khoá ghi EndNote."""


def _chay(lenh: list[str], cho: int = 5) -> str:
    try:
        return subprocess.run(lenh, capture_output=True, text=True, timeout=cho, encoding="utf-8", errors="replace").stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def ung_dung_phia_truoc() -> str | None:
    """Tên ứng dụng đang ở trước (macOS, không cần quyền Trợ năng) — None nếu không đo được."""
    if sys.platform != "darwin":
        return None
    asn = _chay(["lsappinfo", "front"]).strip()
    if not asn:
        return None
    # Đo 19/10/2026 (macOS 27): dòng đầu dạng `"Claude" ASN:0x0-0x76076: (in front)`; bản cũ ghi `"LSDisplayName"="…"`.
    out = _chay(["lsappinfo", "info", "-only", "name", asn])
    m = re.search(r'"LSDisplayName"\s*=\s*"([^"]+)"', out) or re.match(r'\s*"([^"]+)"\s+ASN:', out)
    return m.group(1) if m else None


def giay_ranh() -> float | None:
    """Số giây bàn phím/chuột chưa được dùng (macOS) — None nếu không đo được."""
    if sys.platform != "darwin":
        return None
    m = re.search(r'"HIDIdleTime"\s*=\s*(\d+)', _chay(["ioreg", "-c", "IOHIDSystem"]))
    return int(m.group(1)) / 1e9 if m else None


def bac_si_dang_dung(ung_dung: str, phia_truoc=ung_dung_phia_truoc, ranh=giay_ranh, nguong: float = NGUONG_RANH) -> bool:
    """EndNote ở trước VÀ người dùng vừa thao tác (< nguong giây). Không đo được ⇒ False (xem docstring mô-đun)."""
    ten = phia_truoc()
    if not ten or not ten.lower().startswith(ung_dung.lower().split()[0]):
        return False
    g = ranh()
    return g is not None and g < nguong


def _pid_song(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except (PermissionError, OSError):
        return True  # có tiến trình nhưng không có quyền gửi tín hiệu ⇒ coi là còn sống (thận trọng)


def doc_khoa(tep: Path | None = None) -> dict | None:
    try:
        d = json.loads((tep or TEP_KHOA).read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else None
    except (OSError, ValueError):
        return None


def khoa_con_hieu_luc(d: dict | None, bay_gio: float | None = None, song=_pid_song) -> bool:
    """Khoá của một tiến trình KHÁC còn sống và chưa quá HAN_KHOA."""
    if not d or not isinstance(d.get("pid"), int) or d["pid"] == os.getpid():
        return False
    bay_gio = bay_gio if bay_gio is not None else time.time()
    if bay_gio - float(d.get("luc_epoch") or 0) > HAN_KHOA:
        return False
    return song(d["pid"])


def _ghi_khoa(ly_do: str, tep: Path, luc: float) -> None:
    """Ghi NGUYÊN TỬ (tệp tạm + `os.replace`): tiến trình khác đọc giữa lúc làm mới không bao giờ thấy JSON dở dang — JSON
    hỏng bị `doc_khoa` đọc thành «không có khoá» ⇒ hai tiến trình cùng ghi."""
    tam = tep.with_name(f"{tep.name}.{os.getpid()}.tam")
    tam.write_text(json.dumps({"pid": os.getpid(), "luc_epoch": luc, "luc": datetime.fromtimestamp(luc).isoformat(timespec="seconds"),
                               "ly_do": ly_do[:200]}, ensure_ascii=False), encoding="utf-8")
    os.replace(tam, tep)


def _tha_khoa(tep: Path | None = None) -> None:
    tep = tep or TEP_KHOA
    d = doc_khoa(tep)
    if d and d.get("pid") == os.getpid():
        try:
            tep.unlink()
        except OSError:
            pass


def _tha_khi_thoat() -> None:
    """`atexit` (đăng ký MỘT lần mỗi tiến trình): nhả khoá tiến trình còn giữ."""
    if _DANG_GIU["pid"] == os.getpid() and _DANG_GIU["tep"] is not None:
        _tha_khoa(_DANG_GIU["tep"])


def _thong_bao(noi_dung: str) -> None:
    if sys.platform == "darwin":
        an = noi_dung.replace("\\", "\\\\").replace('"', "'")
        _chay(["osascript", "-e", f'display notification "{an}" with title "EBM · Claude đang ghi EndNote"'])


def cho_phep_ghi_loi(ung_dung: str, ly_do: str, *, tep: Path | None = None, dang_dung=None, ngu=time.sleep,
                     dong_ho=time.monotonic, cho_toi_da: float = CHO_TOI_DA, buoc: float = 5, thong_bao=None,
                     song=_pid_song, bay_gio=time.time) -> None:
    """Lõi của `cho_phep_ghi` (bộ đo/giờ/ngủ tiêm được để test). Ném lỗi khi phải bỏ lượt ghi."""
    tep, thong_bao = tep or TEP_KHOA, thong_bao or _thong_bao
    dang_dung = dang_dung or (lambda: bac_si_dang_dung(ung_dung))
    het = dong_ho() + cho_toi_da
    while True:
        khac = khoa_con_hieu_luc(doc_khoa(tep), song=song)
        ban = dang_dung()
        if not khac and not ban:
            break
        if dong_ho() >= het:
            if khac:
                raise DangCoTienTrinhKhacGhi(f"tiến trình {doc_khoa(tep).get('pid')} đang ghi EndNote — bỏ lượt ghi này")
            raise BacSiDangDungEndNote(f"bác sĩ đang thao tác trên {ung_dung} — bỏ lượt ghi «{ly_do}», chạy lại sau")
        ngu(buoc)
    d = doc_khoa(tep)
    dang_giu = _DANG_GIU["pid"] == os.getpid() and _DANG_GIU["tep"] == tep and bool(d) and d.get("pid") == os.getpid()
    _ghi_khoa(ly_do, tep, bay_gio())  # lấy khoá mới, hoặc LÀM MỚI luc_epoch khi đang giữ
    if not dang_giu:
        _DANG_GIU.update(pid=os.getpid(), tep=tep, thong_bao=False, tu_pham_vi=_DANG_GIU["pham_vi"] > 0)
        if not _DANG_GIU["atexit"]:
            _DANG_GIU["atexit"] = True
            atexit.register(_tha_khi_thoat)
    if not _DANG_GIU["thong_bao"]:
        _DANG_GIU["thong_bao"] = True
        thong_bao(ly_do)


@contextlib.contextmanager
def pham_vi_ghi():
    """Lõi của `giu_khoa_ghi`: mở PHẠM VI một thao tác. Khoá do `cho_phep_ghi*` lấy TRONG phạm vi được nhả ngay khi khối
    NGOÀI CÙNG kết thúc (kể cả khi lỗi); khoá tiến trình đã giữ từ trước khi vào phạm vi giữ nguyên hành vi cũ (atexit).
    Không lệnh ghi nào trong khối (vd chạy khô) ⇒ không đụng tệp khoá."""
    _DANG_GIU["pham_vi"] += 1
    try:
        yield
    finally:
        _DANG_GIU["pham_vi"] -= 1
        if _DANG_GIU["pham_vi"] == 0 and _DANG_GIU["tu_pham_vi"] and _DANG_GIU["pid"] == os.getpid():
            _tha_khoa(_DANG_GIU["tep"])
            _DANG_GIU.update(pid=None, tep=None, thong_bao=False, tu_pham_vi=False)


def _bo_qua() -> bool:
    return bool(os.environ.get("PYTEST_CURRENT_TEST")) or sys.platform != "darwin"


def cho_phep_ghi(ung_dung: str, ly_do: str) -> None:
    """Gọi TRƯỚC mỗi lệnh ghi vào EndNote. Dưới pytest không làm gì (xem docstring mô-đun)."""
    if _bo_qua():
        return
    cho_phep_ghi_loi(ung_dung, ly_do)


@contextlib.contextmanager
def giu_khoa_ghi(ung_dung: str | None = None, ly_do: str | None = None):
    """Giữ khoá ghi EndNote theo PHẠM VI một thao tác, nhả ngay khi xong (xem docstring mô-đun và `pham_vi_ghi`).

    Có `ly_do` ⇒ lấy khoá ngay khi vào khối (chờ/ném như `cho_phep_ghi`). Không có ⇒ chỉ mở phạm vi: khoá lấy ở lệnh ghi
    đầu tiên trong khối — công cụ chạy khô không giữ khoá. Dưới pytest / ngoài macOS chỉ mở phạm vi (không đo, không ghi)."""
    with pham_vi_ghi():
        if ly_do:
            cho_phep_ghi(ung_dung or "EndNote", ly_do)
        yield


if __name__ == "__main__":
    d = doc_khoa()
    print("Khoá ghi EndNote:", json.dumps(d, ensure_ascii=False) if d else "không có")
    print("Ứng dụng phía trước:", ung_dung_phia_truoc(), "| giây rảnh:", giay_ranh())
