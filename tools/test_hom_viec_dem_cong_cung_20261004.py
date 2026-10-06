# -*- coding: utf-8 -*-
"""Hòm việc nhận dòng «chữ ký thật: 0/<n>» của study_readiness (04/10/2026: từ «0/4» viết tay sang SÁU cổng cứng của
gate_contract repo y khoa). Kiểm HÀNH VI của hàm thuần `so_cong_cung_chua_ky` + dòng thi hành gọi nó. Ngoại tuyến."""
from __future__ import annotations

import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import tu_de_xuat_viec as T  # noqa: E402


def test_nhan_dang_moi_sau_cong_va_dang_cu_bon_cong():
    assert T.so_cong_cung_chua_ky("   → Cổng CỨNG đã có chữ ký thật: 0/6 (G2 · G4 · G5 · G8 · G9 · G10)") == "6"
    assert T.so_cong_cung_chua_ky("   → Cổng CỨNG đã có chữ ký thật: 0/4 (G2 · G4 · G8 · G9)") == "4"


def test_khong_bat_nham_khi_da_co_chu_ky_hoac_chi_co_ngay_thang():
    assert T.so_cong_cung_chua_ky("   → Cổng CỨNG đã có chữ ký thật: 2/6 (G2 · G4 · G5 · G8 · G9 · G10)") is None
    # Bản trước dò chuỗi «0/4» trơn ⇒ ngày «10/4», «20/4» trong đầu ra bật nhầm dòng nhắc C1a.
    assert T.so_cong_cung_chua_ky("Lần chạy 10/4/2026 · hạn 20/4 · KẾT LUẬN: CÒN 3 việc") is None
    assert T.so_cong_cung_chua_ky("") is None and T.so_cong_cung_chua_ky(None) is None


def test_dong_thi_hanh_goi_ham_va_khong_con_do_chuoi_tron():
    dong = [x.strip() for x in (TOOLS / "tu_de_xuat_viec.py").read_text(encoding="utf-8").splitlines()]
    assert "_so_cc = so_cong_cung_chua_ky(out)" in dong
    assert not any(x.startswith("if") and '"0/4" in out' in x for x in dong)
