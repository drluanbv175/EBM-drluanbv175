#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Xuất TRẠNG THÁI hệ cập nhật chứng cứ y khoa thành một mirror nhỏ, ĐI QUA GIT.

VÌ SAO CÓ (04/09/2026 — bác sĩ yêu cầu xây đồng bộ tự động Cloud↔cục bộ, đã
chọn phương án "mirror tóm tắt qua git" thay vì track toàn bộ cây dữ liệu hay
nối connector OneDrive):

`EBM-Dashboards/`/`EBM_MASTER/` nằm NGOÀI git CÓ CHỦ Ý (kiến trúc "mã→GitHub,
dữ liệu→OneDrive", xem .gitignore dòng 1-5) — nên một phiên Cloud (container
dựng MỚI mỗi lần) không bao giờ thấy được các thư mục này qua git, dù có đủ mã
nguồn. Công cụ này KHÔNG đảo ngược kiến trúc đó — dữ liệu dashboard vẫn ở
nguyên OneDrive, không nhân bản HTML/derivatives/video/zip. Nó chỉ chạy lại 3
bộ đếm ĐÃ CÓ SẴN (vốn đọc EBM-Dashboards/ khi được chạy trên máy THẬT có dữ
liệu) rồi đóng gói phần TÓM TẮT vào một file JSON nhỏ, git-tracked, để phiên
Cloud kế tiếp THẤY ĐƯỢC trạng thái mới nhất mà không cần OneDrive.

BỐN ĐIỀU CỐ Ý:
  1. CHỈ mirror phần TÓM TẮT/QUYẾT ĐỊNH ĐÃ DUYỆT — không copy dashboard HTML/
     derivatives/video/zip (đúng lý do các thứ đó bị loại khỏi git từ đầu:
     dung lượng lớn, không cần thiết chỉ để "biết trạng thái").
  2. AN TOÀN khi chạy trên máy KHÔNG có EBM-Dashboards/ (Cloud, Windows chưa
     có OneDrive…): ba bộ đếm bên dưới đã tự thiết kế để báo ⚪/🟡 "chưa có dữ
     liệu" thay vì crash — đã đo trực tiếp trên máy Cloud (đo 04/09/2026,
     0 crash, cả ba đều thoát trong vài giây). Script này KHÔNG đòi
     EBM-Dashboards/ phải tồn tại mới chạy được.
  3. KHÔNG PHẢI CỔNG — chỉ đọc và báo cáo, không tự sửa/áp dụng/ghi
     decision·gradeLevel (giữ đúng BH10). Muốn hành động dựa trên báo cáo là
     việc của bác sĩ.
  4. KHÔNG gọi mạng, không cần --online — ba bộ đếm bên dưới vốn đã offline.

Dùng:
    python3 tools/xuat_trang_thai_cloud.py           # ghi cloud-mirror/trang-thai-chung-cu.json
    python3 tools/xuat_trang_thai_cloud.py --in-thu  # chỉ in ra xem trước, không ghi file

Mã thoát: LUÔN 0 — đây là báo cáo, không phải phán quyết (cùng quy ước đã
dùng ở tools/tu_de_xuat_viec.py).
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util as _ilu
import json
import subprocess
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
DASH = REPO / "EBM-Dashboards"
MIRROR_DIR = REPO / "cloud-mirror"
MIRROR_FILE = MIRROR_DIR / "trang-thai-chung-cu.json"

# Ba bộ đếm ĐÃ CÓ SẴN, đều đọc EBM-Dashboards/ và đều tự an toàn khi thiếu dữ
# liệu (xem docstring). Danh sách này là NGUỒN DUY NHẤT — thêm bộ đếm mới thì
# thêm một dòng ở đây, không lặp tên script ở chỗ khác.
BO_DEM = [
    ("do_tuoi_chung_cu", ["kiem_do_tuoi_chung_cu.py"]),
    ("quyet_dinh_da_duyet", ["kiem_quyet_dinh_da_duyet.py"]),
    ("tu_de_xuat_viec", ["tu_de_xuat_viec.py", "--gon"]),
]

# Hai sổ máy-đọc CHỈ bác sĩ thêm/sửa (theo tools/kiem_quyet_dinh_da_duyet.py và
# CLAUDE.md) — nhỏ, đã là phần TÓM TẮT nên an toàn nhân bản nguyên văn.
SO_DA_DUYET = [
    ("quyet_dinh_da_duyet", "quyet-dinh-da-duyet.json"),
    ("mau_thuan_da_duyet", "mau-thuan-da-duyet.json"),
]


def _ten_may() -> str:
    """Uỷ quyền cho tools/nhan_dien_may.py — MỘT nguồn duy nhất (cùng idiom kiem_plugin_day_du.py)."""
    try:
        _spec = _ilu.spec_from_file_location("nhan_dien_may", Path(__file__).resolve().parent / "nhan_dien_may.py")
        _m = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(_m)
        return _m.ten_may()
    except Exception:  # noqa: BLE001 — nhận diện máy hỏng không được làm chết báo cáo
        return "KHONG_XAC_DINH"


def _chay_bo_dem(ten_script: str, doi_them: list) -> dict:
    cmd = [sys.executable, str(REPO / "tools" / ten_script)] + doi_them
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=90, cwd=REPO)
        return {"ma_thoat": p.returncode, "stdout": p.stdout.strip(),
                "stderr": p.stderr.strip()[:2000]}
    except Exception as exc:  # noqa: BLE001 — một bộ đếm lỗi không được làm sập cả báo cáo
        return {"ma_thoat": None, "stdout": "", "stderr": f"LỖI CHẠY: {type(exc).__name__}: {exc}"}


def _doc_so_nho(ten_file: str):
    p = DASH / ten_file
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return {"loi_doc": f"{type(exc).__name__}: {exc}"}


def xay_trang_thai() -> dict:
    trang_thai = {
        "sinh_luc": dt.datetime.now().isoformat(timespec="seconds"),
        "may": _ten_may(),
        "co_du_lieu_dashboard_that": DASH.is_dir(),
        "bo_dem": {khoa: _chay_bo_dem(args[0], args[1:]) for khoa, args in BO_DEM},
        "so_da_duyet": {khoa: _doc_so_nho(ten_file) for khoa, ten_file in SO_DA_DUYET},
    }
    return trang_thai


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Xuất trạng thái hệ cập nhật chứng cứ y khoa vào mirror đi qua git")
    ap.add_argument("--in-thu", action="store_true", help="chỉ in ra xem trước, không ghi file")
    ap.add_argument("--im-khi-on", action="store_true",
                    help="chỉ ghi file, không in gì khi có dữ liệu dashboard thật — dùng cho"
                         " hook SessionStart (bảng đề xuất tự động mỗi khi mở phiên trên Mac/"
                         "Windows). Vẫn in cảnh báo khi máy KHÔNG có EBM-Dashboards/ thật, vì đó"
                         " là tín hiệu bác sĩ cần biết (mirror chỉ ghi được trạng thái rỗng).")
    a = ap.parse_args()

    trang_thai = xay_trang_thai()
    noi_dung = json.dumps(trang_thai, ensure_ascii=False, indent=2)

    if a.in_thu:
        print(noi_dung)
        return 0

    MIRROR_DIR.mkdir(parents=True, exist_ok=True)
    MIRROR_FILE.write_text(noi_dung + "\n", encoding="utf-8")
    im = a.im_khi_on and trang_thai["co_du_lieu_dashboard_that"]
    if not im:
        print(f"✓ Đã ghi {MIRROR_FILE}")
    if not trang_thai["co_du_lieu_dashboard_that"]:
        print("  ⚪ Máy này KHÔNG có EBM-Dashboards/ thật — mirror chỉ ghi được trạng thái"
              " 'chưa có dữ liệu'. Chạy lại trên máy có OneDrive (Mac/Windows) để mirror"
              " mang giá trị thật, rồi commit + push để Cloud thấy được.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
