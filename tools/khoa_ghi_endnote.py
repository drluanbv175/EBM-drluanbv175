#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""khoa_ghi_endnote.py — KHOÁ «Claude đang ghi EndNote» (19/10/2026).

Sự cố 18/10/2026: Claude đang chuyển bản ghi vào thùng rác bằng giao diện thì bác sĩ cũng thao tác trên EndNote ⇒ 7 bản ghi
Unfiled bị chuyển vào thùng rác ngoài ý định của Claude. Bác sĩ 19/10/2026: «Hãy làm tất cả 6 việc giúp tôi» (việc 4: khoá ghi).

Mọi lệnh GHI vào EndNote của `nap_endnote_chu_de.EndNoteMac` (nhập, đăng vào nhóm, gắn tệp, ghi trường) gọi `cho_phep_ghi()`
trước. Hàm này:
  1. Chờ khi BÁC SĨ ĐANG DÙNG EndNote (EndNote là ứng dụng đang ở trước VÀ bàn phím/chuột vừa được dùng < NGUONG_RANH giây),
     tối đa CHO_TOI_DA giây; quá hạn ⇒ ném `BacSiDangDungEndNote` — người gọi BỎ lượt ghi và báo, không ghi chen.
  2. Giữ tệp khoá `~/.ebm-endnote-dang-ghi.json` (pid + giờ + lý do) suốt tiến trình; một tiến trình Claude khác đang giữ khoá
     còn sống ⇒ chờ rồi ném `DangCoTienTrinhKhacGhi`. Khoá của tiến trình đã chết hoặc quá HAN_KHOA giây ⇒ coi như bỏ.
  3. Hiện MỘT thông báo macOS «Claude đang ghi EndNote: <lý do>» cho mỗi tiến trình (không lặp mỗi lệnh ghi).
Đo hoạt động: `lsappinfo` (ứng dụng ở trước — không cần quyền Trợ năng) + `ioreg IOHIDSystem` (giây rảnh). Không đo được ⇒
coi là RẢNH (fail-open có chủ ý: khoá chỉ để không ghi chen khi bác sĩ đang thao tác, không được làm hỏng dây chuyền nền).
Dưới pytest (`PYTEST_CURRENT_TEST`) hàm công khai không đo, không ghi khoá — test gọi hàm lõi với bộ đo giả.
"""
from __future__ import annotations

import atexit
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
_DANG_GIU = {"pid": None, "thong_bao": False}


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


def doc_khoa(tep: Path = TEP_KHOA) -> dict | None:
    try:
        d = json.loads(tep.read_text(encoding="utf-8"))
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


def _ghi_khoa(ly_do: str, tep: Path) -> None:
    tep.write_text(json.dumps({"pid": os.getpid(), "luc_epoch": time.time(), "luc": datetime.now().isoformat(timespec="seconds"),
                               "ly_do": ly_do[:200]}, ensure_ascii=False), encoding="utf-8")


def _tha_khoa(tep: Path = TEP_KHOA) -> None:
    d = doc_khoa(tep)
    if d and d.get("pid") == os.getpid():
        try:
            tep.unlink()
        except OSError:
            pass


def _thong_bao(noi_dung: str) -> None:
    if sys.platform == "darwin":
        an = noi_dung.replace("\\", "\\\\").replace('"', "'")
        _chay(["osascript", "-e", f'display notification "{an}" with title "EBM · Claude đang ghi EndNote"'])


def cho_phep_ghi_loi(ung_dung: str, ly_do: str, *, tep: Path = TEP_KHOA, dang_dung=None, ngu=time.sleep,
                     dong_ho=time.monotonic, cho_toi_da: float = CHO_TOI_DA, buoc: float = 5, thong_bao=_thong_bao,
                     song=_pid_song) -> None:
    """Lõi của `cho_phep_ghi` (bộ đo/giờ/ngủ tiêm được để test). Ném lỗi khi phải bỏ lượt ghi."""
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
    if _DANG_GIU["pid"] != os.getpid() or not tep.exists():
        _ghi_khoa(ly_do, tep)
        _DANG_GIU["pid"] = os.getpid()
        atexit.register(_tha_khoa, tep)
    if not _DANG_GIU["thong_bao"]:
        _DANG_GIU["thong_bao"] = True
        thong_bao(ly_do)


def cho_phep_ghi(ung_dung: str, ly_do: str) -> None:
    """Gọi TRƯỚC mỗi lệnh ghi vào EndNote. Dưới pytest không làm gì (xem docstring mô-đun)."""
    if os.environ.get("PYTEST_CURRENT_TEST") or sys.platform != "darwin":
        return
    cho_phep_ghi_loi(ung_dung, ly_do)


if __name__ == "__main__":
    d = doc_khoa()
    print("Khoá ghi EndNote:", json.dumps(d, ensure_ascii=False) if d else "không có")
    print("Ứng dụng phía trước:", ung_dung_phia_truoc(), "| giây rảnh:", giay_ranh())
