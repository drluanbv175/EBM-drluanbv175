"""Giác quan hòm việc «kiểm máy Claude API» (18/11/2026): báo cáo cũ · hỏng · chưa duyệt ⇒ việc cho bác sĩ.

Giác quan nạp `medical-ebm-automation/tools/duyet_kiem_may_api.py`; ở đây thay bằng một mô-đun giả trong thư mục tạm để
kiểm đúng phần ánh xạ (repo gốc chạy CI không kèm repo y khoa). Không gọi API, không đọc dữ liệu thật.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent


@pytest.fixture
def tdx():
    sp = importlib.util.spec_from_file_location("_tdx_kmapi", HERE / "tu_de_xuat_viec.py")
    m = importlib.util.module_from_spec(sp)
    sys.modules["_tdx_kmapi"] = m
    sp.loader.exec_module(m)
    return m


def _mea(tmp_path: Path, than: str) -> Path:
    goc = tmp_path / "mea"
    (goc / "tools").mkdir(parents=True)
    (goc / "tools" / "duyet_kiem_may_api.py").write_text(than, encoding="utf-8", newline="\n")
    return goc


def _bc(**kw):
    b = {"loai": "A12", "ten": "kiểm nội dung trích dẫn A12", "cu": False, "ly_do": "mã băm khớp",
         "can_duyet": 9, "chua_duyet": 0}
    b.update(kw)
    return b


def _tool(tt) -> str:
    return f"def tinh_trang_tat_ca(goc):\n    return {tt!r}\n"


def test_bao_cao_cu_la_viec_uu_tien_2_lenh_chay_kho(tmp_path, tdx, monkeypatch):
    # 18/11: ghim chính sách «không tự chạy» (repo nay có sync/api-khi-can.json) ⇒ vẫn là việc bác sĩ quyết.
    monkeypatch.setattr(tdx, "_chinh_sach_api_khi_can", lambda: None)
    tt = [{"study": "btm", "do_duoc": True, "bao_cao": [_bc(cu=True, ly_do="đề cương đổi", chua_duyet=9)]}]
    viec = tdx.giac_quan_kiem_may_api(_mea(tmp_path, _tool(tt)))
    assert len(viec) == 1
    uu, nhan, mo_ta, lenh = viec[0]
    assert (uu, nhan) == (2, "👤") and "CŨ" in mo_ta and "btm" in mo_ta
    assert "kiem_noi_dung_trich_dan.py --study btm" in lenh and "--goi-api" not in lenh  # chỉ chạy khô


def test_bao_cao_cu_va_chinh_sach_tu_chay_thi_may_tu_chay(tmp_path, tdx, monkeypatch):
    """18/11: bác sĩ cho TỰ CHẠY «Kiểm đề cương khi đổi» ⇒ 🛎 trỏ cơ chế API khi cần (chạy THẬT, không chạy khô)."""
    monkeypatch.setattr(tdx, "_chinh_sach_api_khi_can",
                        lambda: {"tu_chay": {"chu_de": True, "de_cuong": True, "cafes": True}})
    tt = [{"study": "btm", "do_duoc": True, "bao_cao": [_bc(cu=True, ly_do="đề cương đổi", chua_duyet=9)]}]
    (uu, nhan, mo_ta, lenh), = tdx.giac_quan_kiem_may_api(_mea(tmp_path, _tool(tt)))
    assert (uu, nhan) == (3, "🛎") and "TỰ CHẠY LẠI" in mo_ta and "btm" in mo_ta
    assert lenh == "python3 tools/api_khi_can.py --chay --chi de_cuong"


def test_khong_khang_dinh_duoc_cu_thi_khong_tu_chay(tmp_path, tdx, monkeypatch):
    """«Không khẳng định được» (cu=None) KHÔNG được coi là cũ để tự chi tiền."""
    monkeypatch.setattr(tdx, "_chinh_sach_api_khi_can",
                        lambda: {"tu_chay": {"chu_de": True, "de_cuong": True, "cafes": True}})
    tt = [{"study": "btm", "do_duoc": True, "bao_cao": [_bc(cu=None, ly_do="chưa có mã băm", chua_duyet=0)]}]
    assert all(v[1] != "🛎" for v in tdx.giac_quan_kiem_may_api(_mea(tmp_path, _tool(tt))))


def test_chua_duyet_la_uu_tien_3_kem_lenh_phieu(tmp_path, tdx):
    tt = [{"study": "btm", "do_duoc": True,
           "bao_cao": [_bc(loai="PHAN_BIEN", ten="phản biện máy đề cương", can_duyet=24, chua_duyet=24)]}]
    (uu, nhan, mo_ta, lenh), = tdx.giac_quan_kiem_may_api(_mea(tmp_path, _tool(tt)))
    assert (uu, nhan) == (3, "👤") and "24/24" in mo_ta and "duyet_kiem_may_api.py phieu --study btm" in lenh


def test_bao_cao_hong_bao_ra(tmp_path, tdx):
    tt = [{"study": "btm", "do_duoc": True, "bao_cao": [{"loai": "A12", "hong": True, "tep_bao_cao": "A12_X.json"}]}]
    (uu, _, mo_ta, _), = tdx.giac_quan_kiem_may_api(_mea(tmp_path, _tool(tt)))
    assert uu == 2 and "hỏng" in mo_ta


def test_con_hieu_luc_va_da_duyet_het_thi_im(tmp_path, tdx):
    tt = [{"study": "btm", "do_duoc": True, "bao_cao": [_bc()]}]
    assert tdx.giac_quan_kiem_may_api(_mea(tmp_path, _tool(tt))) == []


def test_chua_khang_dinh_duoc_thi_khong_bao_cu(tmp_path, tdx):
    """`cu=None` (báo cáo cũ chưa có mã băm, tệp không sửa sau đó) ⇒ không báo đỏ giả là CŨ; còn mục chưa duyệt vẫn nhắc."""
    tt = [{"study": "btm", "do_duoc": True, "bao_cao": [_bc(cu=None, chua_duyet=2)]}]
    (uu, _, mo_ta, _), = tdx.giac_quan_kiem_may_api(_mea(tmp_path, _tool(tt)))
    assert uu == 3 and "CŨ" not in mo_ta


def test_cong_cu_vang_hay_loi_la_giac_quan_chet(tmp_path, tdx):
    tdx._GIAC_QUAN_CHET.clear()
    assert tdx.giac_quan_kiem_may_api(tmp_path / "khong-co") == []
    assert tdx.giac_quan_kiem_may_api(_mea(tmp_path, "def tinh_trang_tat_ca(goc):\n    raise OSError('x')\n")) == []
    assert len(tdx._GIAC_QUAN_CHET) == 2 and all("kiểm máy Claude API" in x for x in tdx._GIAC_QUAN_CHET)


def test_giac_quan_duoc_noi_vao_hom_viec():
    """Giác quan không ai gọi thì với hòm việc nó không tồn tại (luật §6.4)."""
    than = (HERE / "tu_de_xuat_viec.py").read_text(encoding="utf-8")
    assert any(d.strip().startswith("de_xuat += giac_quan_kiem_may_api()") for d in than.splitlines())
