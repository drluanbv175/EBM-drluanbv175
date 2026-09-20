"""B5 «hàng chờ bác sĩ» không được báo xanh khi còn gói bị chặn chờ chữ ký — T4-04, 20/09/2026."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
sp = importlib.util.spec_from_file_location("tm_t", GOC / "tools" / "trinh_muc_can_duyet.py")
tm = importlib.util.module_from_spec(sp)
sys.modules["tm_t"] = tm
sp.loader.exec_module(tm)


def test_khong_bao_xanh_khi_con_goi_cho_ky():
    d = tm.dong_khi_khong_co_muc(["WebDashboard_X_20260914.html"])
    assert d.startswith("🟠") and "CHỜ BÁC SĨ KÝ" in d and "WebDashboard_X_20260914.html" in d and "🟢" not in d


def test_xanh_chi_khi_that_su_khong_co_gi_va_noi_ro_pham_vi():
    d = tm.dong_khi_khong_co_muc([])
    assert d.startswith("🟢") and "chỉ xét luật này" in d


def test_cong_cu_phu_hong_khong_lam_chet_hang_cho(monkeypatch):
    monkeypatch.setattr(tm.importlib.util, "spec_from_file_location", lambda *a, **k: (_ for _ in ()).throw(OSError("x")))
    assert tm.cho_ky_rut_bai([Path("a.html")]) == []
