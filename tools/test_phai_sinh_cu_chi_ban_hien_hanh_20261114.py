"""Bộ đếm «phái sinh lỗi thời» chỉ tính dashboard HIỆN HÀNH, bỏ bản đã bị bản nối tiếp thay (14/11/2026).

Đo 13/11/2026: `tu_de_xuat_viec.py --phai-sinh-cu` báo 12 dashboard — cả 12 đã có bản nối tiếp mới hơn, nên quy trình gói
duyệt xuất lại bản lỗi thời mà bác sĩ không đọc.
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
sp = importlib.util.spec_from_file_location("tdxv_psc", GOC / "tools" / "tu_de_xuat_viec.py")
m = importlib.util.module_from_spec(sp)
sys.modules["tdxv_psc"] = m
sp.loader.exec_module(m)


def _kho(tmp: Path) -> Path:
    (tmp / "derivatives").mkdir()
    (tmp / "tools").mkdir()
    vd = GOC / "EBM-Dashboards" / "tools" / "verify_dashboard.py"
    if vd.exists():
        shutil.copy2(vd, tmp / "tools" / "verify_dashboard.py")
    return tmp


def _dash(kho: Path, ten: str, co_docx_moi: bool) -> None:
    f = kho / f"WebDashboard_EBM_VanDeCuThe_{ten}.html"
    f.write_text("<html><script>const DATA = {items:[]};\n// HẾT KHỐI DATA\n</script></html>", encoding="utf-8")
    os.utime(f, (5_000, 5_000))
    docx = kho / "derivatives" / f"{ten}_TaiLieuChiTiet.docx"
    docx.write_text("x", encoding="utf-8")
    t = 9_000 if co_docx_moi else 1_000  # không sidecar ⇒ lùi về so mtime
    os.utime(docx, (t, t))


def test_ban_cu_bi_thay_khong_bao(tmp_path):
    kho = _kho(tmp_path)
    _dash(kho, "SuyTim_NguoiCaoTuoi_20261103", co_docx_moi=False)  # bản cũ, phái sinh cũ
    _dash(kho, "SuyTim_NguoiCaoTuoi_20261113", co_docx_moi=True)   # bản hiện hành, phái sinh mới
    assert [p.name for p in m.liet_ke_dashboard_phai_sinh_loi_thoi(kho)] == []


def test_ban_hien_hanh_loi_thoi_van_bao(tmp_path):
    kho = _kho(tmp_path)
    _dash(kho, "SuyTim_NguoiCaoTuoi_20261103", co_docx_moi=True)
    _dash(kho, "SuyTim_NguoiCaoTuoi_20261113", co_docx_moi=False)
    assert [p.name for p in m.liet_ke_dashboard_phai_sinh_loi_thoi(kho)] == [
        "WebDashboard_EBM_VanDeCuThe_SuyTim_NguoiCaoTuoi_20261113.html"]


def test_lat_cat_khac_cung_chu_de_khong_bi_coi_la_thay(tmp_path):
    # COPD tổng quát và COPD đối tượng đặc biệt là LÁT CẮT KHÁC — bổ sung, không thay nhau
    kho = _kho(tmp_path)
    _dash(kho, "COPD_20261020", co_docx_moi=False)
    _dash(kho, "COPD_DoiTuongDacBiet_DaBenh_20261104", co_docx_moi=True)
    assert [p.name for p in m.liet_ke_dashboard_phai_sinh_loi_thoi(kho)] == [
        "WebDashboard_EBM_VanDeCuThe_COPD_20261020.html"]
