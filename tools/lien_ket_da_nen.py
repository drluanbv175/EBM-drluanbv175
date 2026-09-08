#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LIÊN KẾT ĐA NỀN — một lối tạo liên kết thư mục dùng chung cho Mac và Windows.

VÌ SAO CÓ (21/08/2026). Cơ chế đồng bộ skill hiện tại có HAI bản không nói chuyện
với nhau: `sync/link-skills.sh` (symlink, macOS) và `sync/link-skills.ps1`
(junction, Windows). Bản Python hợp nhất `tools/dong_bo_skill_claude_codex.py`
chọn cách thứ ba — `os.symlink` cho mọi nền — rồi **tự chặn chính nó** bằng
`if os.name == "nt": return 1`. Nên trên Windows KHÔNG có lệnh đồng bộ nào, và
nếu gỡ dòng chặn đó ra thì tool sẽ gãy vì ba lý do đo được:

  1. **Windows KHÔNG tạo được symlink.** `os.symlink` ném WinError 1314
     (SeCreateSymbolicLink — cần Developer Mode hoặc quyền admin). Đây KHÔNG phải
     giả định: máy Windows của bác sĩ đã đo đúng lỗi này ngày 17/08/2026, và repo
     y khoa phải thêm `_symlink_or_skip` cho 3 test vì «may chua bat Developer
     Mode» (commit c2e3c41). Junction (`mklink /J`) tạo được KHÔNG cần quyền gì —
     đó là lý do bản .ps1 dùng junction ngay từ đầu.

  2. **`Path.is_symlink()` trả FALSE cho junction.** Junction là reparse point loại
     MOUNT_POINT, không phải symlink, nên `os.path.islink` không nhận. Hệ quả nếu
     dùng nhầm: tool thấy junction → tưởng là THƯ MỤC THẬT → sao lưu rồi tạo lại,
     **mỗi lần chạy đẻ thêm một bản .bak**, và trên hook `SessionStart` thì mỗi
     phiên một bản.

  3. **`shutil.rmtree` trên junction xoá XUYÊN qua nó.** Xoá một junction bằng
     rmtree là xoá luôn nội dung THẬT ở `sync/skills/<tên>` — tức mất nguồn, không
     phải mất bản sao. Vì vậy `go()` dưới đây từ chối cứng mọi lối xoá đệ quy.

Bất biến của module: **không bao giờ xoá đệ quy**, không bao giờ đụng vào đích mà
liên kết trỏ tới, và mọi thao tác đều idempotent (chạy lại nhiều lần vẫn đúng).

Thuần thư viện chuẩn. Không mạng. Dùng được từ Python 3.9 trở lên.
"""
from __future__ import annotations

import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

WINDOWS = os.name == "nt"


def kieu() -> str:
    """Tên cơ chế liên kết dùng trên nền này — để thông điệp nói đúng thứ đang làm."""
    return "junction" if WINDOWS else "symlink"


def la_junction(p: Path) -> bool:
    """Nhận diện junction của Windows.

    `os.path.isjunction` có từ Python 3.12 (máy Windows của bác sĩ chạy 3.12.10,
    Mac 3.14.6 — cả hai đều có). Giữ nhánh lùi cho 3.9–3.11 bằng `os.readlink`,
    vốn đọc được junction từ 3.8: thư mục thường sẽ ném OSError, junction thì không.
    """
    if not WINDOWS:
        return False
    if hasattr(os.path, "isjunction"):
        return os.path.isjunction(p)
    try:
        os.readlink(p)
        return True
    except OSError:
        return False


def la_lien_ket(p: Path) -> bool:
    """TRUE nếu p là symlink HOẶC junction. Đây là hàm mà mọi nơi phải gọi —
    dùng thẳng `p.is_symlink()` là bỏ sót junction (lý do 2 ở đầu file)."""
    return p.is_symlink() or la_junction(p)


_TIEN_TO_DUONG_DAN_MO_RONG = "\\\\?\\"


def dich_cua(p: Path) -> Path | None:
    """Đích thật mà liên kết trỏ tới; None nếu p không phải liên kết hoặc đã gãy.

    Trên Windows, ``os.readlink`` cho junction trả về đường dẫn có tiền tố
    mở-rộng ``\\\\?\\`` (vd ``\\\\?\\C:\\...``), trong khi ``Path.resolve()`` của
    một đường dẫn thường KHÔNG có tiền tố này. Không cắt bỏ thì ``tro_dung()`` so
    hai chuỗi khác dạng và LUÔN trả False — kể cả khi junction đang trỏ ĐÚNG nơi
    (đo được thật 05/09/2026: mọi junction đã nối đúng đều bị báo "trỏ nơi khác").
    """
    if not la_lien_ket(p):
        return None
    try:
        dich = os.readlink(p)
    except OSError:
        return None
    if dich.startswith(_TIEN_TO_DUONG_DAN_MO_RONG):
        dich = dich[len(_TIEN_TO_DUONG_DAN_MO_RONG):]
    return Path(dich).resolve()


def tro_dung(p: Path, nguon: Path) -> bool:
    """Liên kết p có đang trỏ đúng vào nguon không.

    Ưu tiên ``os.path.samefile`` — so bằng định danh file thật (inode trên
    POSIX, file ID qua GetFileInformationByHandle trên Windows), KHÔNG so
    chuỗi hai ``Path.resolve()`` độc lập. Đã đo thật trên GitHub Actions
    windows-latest (06/09/2026): cùng một thư mục tồn tại, hai lần resolve()
    độc lập (một lần trong hàm này, một lần ở nơi gọi) có thể ra hai chuỗi
    KHÁC NHAU (một bên có tiền tố đường dẫn mở rộng ``\\\\?\\``, một bên
    không) — so chuỗi báo sai KHÔNG khớp dù liên kết trỏ ĐÚNG. Nguy cơ này
    không chỉ riêng CI: OneDrive cũng dựng file placeholder bằng reparse
    point, cùng cơ chế gây lệch chuỗi. Lùi về so chuỗi khi một trong hai
    đường dẫn không tồn tại (liên kết treo — ``samefile`` sẽ ném lỗi).
    """
    dich = dich_cua(p)
    if dich is None:
        return False
    try:
        if dich.exists() and nguon.exists():
            return os.path.samefile(dich, nguon)
        return dich == nguon.resolve()
    except OSError:
        return False


def tao(nguon: Path, lien_ket: Path) -> None:
    """Tạo liên kết thư mục `lien_ket` → `nguon`. Đích phải CHƯA tồn tại.

    macOS/Linux dùng symlink; Windows dùng junction qua `mklink /J` (không cần
    quyền admin, khác `os.symlink`). Không tự xoá cái đang có — người gọi phải
    quyết định sao lưu hay bỏ qua, để module này không bao giờ là nơi mất dữ liệu.
    """
    if lien_ket.exists() or la_lien_ket(lien_ket):
        raise FileExistsError(f"đã tồn tại, không đè: {lien_ket}")
    lien_ket.parent.mkdir(parents=True, exist_ok=True)
    if not WINDOWS:
        os.symlink(nguon, lien_ket, target_is_directory=True)
        return
    ket_qua = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(lien_ket), str(nguon)],
        check=False, capture_output=True, text=True, timeout=60,
    )
    if ket_qua.returncode != 0 or not la_lien_ket(lien_ket):
        loi = (ket_qua.stderr or ket_qua.stdout or "").strip()
        raise OSError(f"mklink /J thất bại cho {lien_ket}: {loi or 'không rõ lý do'}")


def go(p: Path) -> None:
    """Gỡ MỘT liên kết, giữ nguyên đích nó trỏ tới.

    Từ chối cứng khi p không phải liên kết: gọi nhầm vào thư mục thật ở đây chính
    là lối mất `sync/skills/<tên>` (lý do 3 ở đầu file). Junction/symlink-thư-mục
    gỡ bằng `os.rmdir` — thao tác này chỉ tháo điểm nối, KHÔNG đụng nội dung bên
    trong.

    Windows phân biệt liên kết THƯ MỤC (gỡ bằng rmdir/RemoveDirectory) với liên
    kết FILE (gỡ bằng unlink/DeleteFile) ngay TỪ LÚC TẠO — không phụ thuộc đích
    có còn tồn tại hay không. Vì vậy dùng ``os.lstat`` (đọc thuộc tính của CHÍNH
    liên kết, không theo nó tới đích) để biết liên kết thuộc loại nào, KHÔNG
    dùng ``Path.is_dir()``: is_dir() theo liên kết rồi stat() đích — với liên
    kết TREO (đích không còn tồn tại): trên Python 3.9–3.11 (chưa có
    ``os.path.isjunction``, xem nhánh lùi của ``la_junction``), một liên kết
    FILE bị treo lại bị fallback đó coi NHẦM là junction (readlink đọc được ⇒
    coi là junction, không phân biệt symlink thường), nên vẫn rơi vào nhánh cũ
    `la_junction(p) or (WINDOWS and p.is_dir())` rồi gọi `os.rmdir` sai loại,
    ném WinError 267 (đo thật trên GitHub Actions windows-latest/Python 3.11,
    06/09/2026; Python 3.12 không dính vì có `os.path.isjunction` chính xác).
    Cách này cũng khỏi cần gọi riêng ``la_junction`` — junction luôn mang thuộc
    tính thư mục, ``os.lstat`` đã bắt đúng cả hai, và đúng trên mọi bản Python.
    """
    if not la_lien_ket(p):
        raise ValueError(f"từ chối gỡ: {p} không phải liên kết (có thể là dữ liệu thật)")
    if WINDOWS and stat.S_ISDIR(os.lstat(p).st_mode):
        os.rmdir(p)
    else:
        p.unlink()


def sao_luu_ra_ngoai(muc_tieu: Path, kho_backup: Path, dau_thoi_gian: str) -> Path:
    """Dời một thư mục THẬT ra khỏi vùng quét, trả về nơi đã dời.

    Sao lưu phải nằm NGOÀI thư mục skill: để bản `.bak-…` ngay tại chỗ thì Claude
    Code nạp nó thành một skill riêng — menu `/` hiện hai bản trùng tên, bản cũ
    mang mô tả cũ. Đã xảy ra thật 03/08/2026 với `kham-ngoai-tru-ebm` và
    `tuan-thu-dieu-tri`; bản .ps1 đã vá còn bản .sh thì chưa (vá cùng đợt 21/08).
    """
    kho_backup.mkdir(parents=True, exist_ok=True)
    dich = kho_backup / f"{muc_tieu.name}.bak-{dau_thoi_gian}"
    shutil.move(str(muc_tieu), str(dich))
    return dich
