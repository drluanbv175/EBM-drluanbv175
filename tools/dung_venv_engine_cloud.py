#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DỰNG VENV ENGINE CHỨNG CỨ CHO PHIÊN CLOUD (24/09/2026, audit/15 §7quater).

Vì sao có: engine nguồn chứng cứ (`medical-ebm-automation/run.py`, mọi connector ở `app/sources/`)
cần `requirements.lock.txt` — khoá scipy 1.18.0 nên đòi Python ≥ 3.12 — trong khi Python mặc định
của container Cloud là 3.11 và KHÔNG có sqlalchemy/python-dotenv/pypdf/wiley-tdm. Đo 24/09 trên
một phiên Cloud: `python3 run.py test-live pubmed` chết ngay ở `import sqlalchemy`. Nghĩa là dù bác
sĩ đã mở mạng + đặt biến môi trường + khai khoá, một phiên Cloud MỚI vẫn không chạy được MỘT nguồn
nào qua engine — venv từng dùng để đo là do agent dựng tay trong một phiên, và mất theo container.
Hook Cloud chỉ cài 3 thư viện đọc tài liệu (python-docx · beautifulsoup4 · lxml), không cài engine.

Nối vào `tu_sua_chua.py::VIEC_MAY` với `chay_tren_cloud=True` (hook Cloud ⑤b chạy
`--pham-vi-cloud --ap-dung`). Việc dựng (tạo venv + pip install ~130 gói) mất vài phút nên chạy ở
NỀN, tách tiến trình — chặn lúc mở phiên là dạy người ta tắt hook (cùng lý do BH86). Trên máy thật:
KHÔNG làm gì (mã 0) — venv `~/.ebm-venv` ở đó do bác sĩ quản, công cụ không được tự cài hộ.

Mã thoát: 0 = không phải Cloud / venv đã sẵn sàng / đã phóng dựng ở nền (hoặc đang dựng) ·
1 = Cloud mà venv chưa sẵn sàng (--im-khi-on) · 2 = không phóng được việc dựng.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

GOC = Path(__file__).resolve().parents[1]
_sp = importlib.util.spec_from_file_location("_bst_dve", Path(__file__).resolve().parent / "ban_sao_tran.py")
_bst = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(_bst)

# Đường venv chuẩn của dự án trên macOS/Linux (CLAUDE.md: `~/.ebm-venv`).
VENV = Path.home() / ".ebm-venv"
NHAT_KY = Path.home() / ".claude" / "ebm-venv-engine-cloud.log"
KHOA = Path.home() / ".claude" / "ebm-venv-engine-cloud.lock"
# Các module mà engine chết ngay khi thiếu (đo 24/09) + thư viện của connector toàn văn.
MODULE_BAT_BUOC = ("sqlalchemy", "dotenv", "requests", "pypdf", "wiley_tdm")


def la_phien_cloud() -> bool:
    return os.environ.get("CLAUDE_CODE_REMOTE", "").strip().lower() == "true"


def goc_engine() -> Path | None:
    return _bst.duong_goc("medical-ebm-automation", GOC)


def python_venv(venv: Path = VENV) -> Path:
    return venv / "bin" / "python"


def venv_san_sang(venv: Path = VENV) -> bool:
    """Venv có Python chạy được VÀ nạp được mọi module bắt buộc — có thư mục chưa đủ."""
    py = python_venv(venv)
    if not py.exists():
        return False
    try:
        r = subprocess.run([str(py), "-c", "import " + ", ".join(MODULE_BAT_BUOC)],
                           capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return False
    return r.returncode == 0


def dang_dung(khoa: Path = KHOA) -> bool:
    """Khoá theo PID: tiến trình dựng còn sống thì không phóng chồng."""
    try:
        pid = int(khoa.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def tim_python312() -> str | None:
    for ten in ("python3.12", "python3.13", "python3.14"):
        duong = shutil.which(ten)
        if duong:
            return duong
    return None


def lenh_dung(py312: str, mea: Path, venv: Path = VENV) -> str:
    """Chuỗi lệnh shell dựng venv — tạo mới (xoá venv cũ chưa dùng được) rồi cài ĐÚNG bản khoá."""
    lock = mea / "requirements.lock.txt"
    # `--clear`: container có thể còn một `~/.ebm-venv` dựng bằng Python 3.11 (đo 24/09) — tạo
    # lại đè lên thư mục cũ mà không xoá thì venv giữ nguyên Python 3.11 và pip chết ở scipy 1.18.0.
    return (f'"{py312}" -m venv --clear "{venv}" && '
            f'"{venv}/bin/python" -m pip install -q --disable-pip-version-check -r "{lock}"')


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--im-khi-on", action="store_true")
    ap.add_argument("--ap-dung", action="store_true", help="dựng venv ở nền nếu thiếu (chỉ trên Cloud)")
    a = ap.parse_args()

    if not la_phien_cloud():
        if not a.im_khi_on:
            print("ℹ Không phải phiên Cloud — venv engine do bác sĩ quản trên máy thật, không làm gì.")
        return 0
    mea = goc_engine()
    if mea is None:
        if not a.im_khi_on:
            print("⚪ Phiên Cloud không có medical-ebm-automation — không có engine để dựng venv.")
        return 0
    if venv_san_sang():
        if not a.im_khi_on:
            print(f"🟢 Venv engine đã sẵn sàng: {python_venv()}")
        return 0
    if dang_dung():
        if not a.im_khi_on:
            print(f"⏳ Venv engine đang được dựng ở nền — nhật ký: {NHAT_KY}")
        return 0
    if not a.ap_dung:
        print("🟠 Phiên Cloud CHƯA có venv engine — mọi connector nguồn chứng cứ không chạy được. "
              "Chạy: python3 tools/dung_venv_engine_cloud.py --ap-dung")
        return 1
    py312 = tim_python312()
    if py312 is None:
        print("🔴 Container không có Python ≥ 3.12 — requirements.lock.txt cần scipy 1.18.0 (≥3.12).")
        return 2
    try:
        NHAT_KY.parent.mkdir(parents=True, exist_ok=True)
        with NHAT_KY.open("w", encoding="utf-8") as log:
            p = subprocess.Popen(["bash", "-c", lenh_dung(py312, mea)], cwd=str(mea),
                                 stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        KHOA.write_text(str(p.pid), encoding="utf-8")
    except OSError as exc:
        print(f"🔴 Không phóng được việc dựng venv: {exc}")
        return 2
    print(f"⏳ Đã phóng dựng venv engine ở nền (vài phút) — nhật ký: {NHAT_KY}. "
          f"Xong thì dùng: {python_venv()} run.py …")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
