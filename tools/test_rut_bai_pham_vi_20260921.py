"""Cổng liêm chính phải NÓI RA phạm vi kiểm rút bài — việc #2a (21/09/2026).

Tái hiện gốc: dashboard mang PMID 9500320 (Wakefield 1998, ĐÃ RÚT) PASS ngoại tuyến 0 lỗi cứng vì «sổ im lặng» gồm cả
«đã kiểm sạch» lẫn «chưa kiểm lần nào». Nay: (1) cổng in K/M định danh có dấu vết kiểm còn hạn, (2) hỏi nền Retraction
Watch NGOẠI TUYẾN cho PMID chưa kiểm — CHỈ nhận tín hiệu dương, (3) không có nền ⇒ 'chưa biết', không phải 'sạch'.
Ngoại tuyến 100%: sổ và nền Retraction Watch là hàm/đối tượng giả.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _nap(ten: str, duong: Path):
    sp = importlib.util.spec_from_file_location(ten, duong)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


SO = _nap("so_xm_pv", ROOT / "tools" / "so_xac_minh_nguon.py")
VD_NGUON = ROOT / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "verify_dashboard.py"


def _iso(ngay_truoc: int) -> str:
    return (dt.date.today() - dt.timedelta(days=ngay_truoc)).isoformat()


# ── 1. pham_vi_kiem_rut_bai ───────────────────────────────────────────────────────────────────────────
def test_phan_biet_da_kiem_con_han_voi_chua_kiem_hoac_qua_han(monkeypatch):
    so = {"muc": {
        "pmid:1111111": {"loai": "pmid", "gia_tri": "1111111", "xac_minh_luc": _iso(2), "kiem_rut_luc": _iso(2)},
        "pmid:2222222": {"loai": "pmid", "gia_tri": "2222222", "xac_minh_luc": _iso(2), "kiem_rut_luc": _iso(400)},   # quá hạn
        "pmid:3333333": {"loai": "pmid", "gia_tri": "3333333", "xac_minh_luc": _iso(2)},                              # chưa kiểm rút bài
        "doi:10.1/abc": {"loai": "doi", "gia_tri": "10.1/abc", "xac_minh_luc": _iso(2), "kiem_rut_luc": _iso(1)},
        "pmid:5555555": {"loai": "pmid", "gia_tri": "5555555", "da_rut": True},                                       # đã biết rút ⇒ có dấu vết
    }}
    monkeypatch.setattr(SO, "doc_so", lambda: so)
    pv = SO.pham_vi_kiem_rut_bai(["1111111", "2222222", "3333333", "4444444", "10.1/ABC", "5555555"])
    assert sorted(pv["co"]) == ["10.1/ABC", "1111111", "5555555"]
    assert sorted(pv["chua"]) == ["2222222", "3333333", "4444444"], "vắng sổ / chưa kiểm / quá hạn đều là CHƯA KIỂM"


def test_khong_co_nhanh_nao_tra_sach_cho_dinh_danh_vang_so(monkeypatch):
    monkeypatch.setattr(SO, "doc_so", lambda: {"muc": {}})
    assert SO.pham_vi_kiem_rut_bai(["9500320"]) == {"co": [], "chua": ["9500320"]}


# ── 2. Retraction Watch ngoại tuyến ───────────────────────────────────────────────────────────────────
class _ChiMucGia:
    def __init__(self, du_lieu):
        self._d = du_lieu

    def tra(self, pmid):
        return self._d.get(pmid)


def test_rw_ngoai_tuyen_chi_tra_duong_tinh(monkeypatch):
    monkeypatch.setitem(SO._RW_NGOAI_TUYEN, "da_thu", True)
    monkeypatch.setitem(SO._RW_NGOAI_TUYEN, "chi_muc", _ChiMucGia({"9500320": {"status": "retracted", "reason": "Falsification;", "notice_pmid": "20137807"}}))
    ra = SO.rut_bai_retraction_watch_ngoai_tuyen(["9500320", "34101376"])
    assert [r["gia_tri"] for r in ra] == ["9500320"], "PMID không có trong danh mục KHÔNG được thành 'sạch' hay 'rút'"
    assert ra[0]["tinh_trang"] == "retracted" and "Retraction Watch" in ra[0]["nguon"]


def test_rw_ngoai_tuyen_vang_nen_tra_none_khong_phai_rong(monkeypatch):
    monkeypatch.setitem(SO._RW_NGOAI_TUYEN, "da_thu", True)
    monkeypatch.setitem(SO._RW_NGOAI_TUYEN, "chi_muc", None)
    assert SO.rut_bai_retraction_watch_ngoai_tuyen(["9500320"]) is None, "None = CHƯA KIỂM; [] sẽ bị đọc thành 'sạch'"


# ── 3. Cổng verify_dashboard: tích hợp bằng cây thư mục giả ──────────────────────────────────────────────
STUB_SO = '''
_RW = {}
def nguon_da_rut(ten): return []
def dinh_danh_da_rut(ids): return []
def pham_vi_kiem_rut_bai(ids):
    co = [i for i in ids if i in _CO]
    return {"co": co, "chua": [i for i in ids if i not in _CO]}
def rut_bai_retraction_watch_ngoai_tuyen(pmids):
    if _NEN_VANG: return None
    return [{"khoa": "pmid:"+p, "loai": "pmid", "gia_tri": p, "tinh_trang": "retracted", "tieu_de": "", "kiem_luc": "2026-09-21",
             "nguon": "Retraction Watch (nền ngoại tuyến; lý do: x)", "rut_va_thay": False, "thong_bao": "",
             "sua_loi_bi_rut": False, "thong_bao_ids": []} for p in pmids if p in _RUT]
'''


def _dung_cay(tmp: Path, co: set, rut: set, nen_vang: bool = False):
    (tmp / "tools").mkdir()
    shutil.copy(VD_NGUON, tmp / "tools" / "verify_dashboard.py")
    (tmp / "tools" / "so_xac_minh_nguon.py").write_text(
        f"_CO = {sorted(co)!r}\n_RUT = {sorted(rut)!r}\n_NEN_VANG = {nen_vang!r}\n" + STUB_SO, encoding="utf-8")
    page = tmp / "WebDashboard_EBM_VanDeCuThe_X_20260921.html"
    page.write_text("<script>const DATA={items:[{id:'ITEM-01',pmid:'9500320'},{id:'ITEM-02',pmid:'34101376'}]}</script>", encoding="utf-8")
    spec = importlib.util.spec_from_file_location("vd_tich_hop_" + tmp.name, tmp / "tools" / "verify_dashboard.py")
    vd = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vd)
    return vd, page


def test_pmid_da_rut_chua_tung_qua_so_van_bi_chan_boi_nen_ngoai_tuyen(tmp_path):
    vd, page = _dung_cay(tmp_path, co={"34101376"}, rut={"9500320"})
    errors, warns, oks = [], [], []
    vd.kiem_nguon_da_rut(str(page), errors, warns, oks)
    assert any("ĐÃ BỊ RÚT" in e and "9500320" in e for e in errors), (errors, warns)


def test_chua_kiem_duoc_noi_ra_thanh_canh_bao_khong_phai_sach(tmp_path):
    vd, page = _dung_cay(tmp_path, co={"34101376"}, rut=set())
    errors, warns, oks = [], [], []
    vd.kiem_nguon_da_rut(str(page), errors, warns, oks)
    assert not errors
    pv = [w for w in warns if "Phạm vi kiểm rút bài" in w]
    assert pv and "1/2" in pv[0] and "9500320" in pv[0] and "KHÔNG phải 'sạch'" in pv[0]
    assert not any("Rút bài:" in o for o in oks), "còn định danh chưa kiểm thì tuyệt đối không được in ✓"


def test_nen_ngoai_tuyen_vang_duoc_noi_ro(tmp_path):
    vd, page = _dung_cay(tmp_path, co={"34101376"}, rut=set(), nen_vang=True)
    errors, warns, oks = [], [], []
    vd.kiem_nguon_da_rut(str(page), errors, warns, oks)
    pv = [w for w in warns if "Phạm vi kiểm rút bài" in w]
    assert pv and "KHÔNG có trên máy này" in pv[0]


def test_du_dau_vet_moi_duoc_in_xanh(tmp_path):
    vd, page = _dung_cay(tmp_path, co={"34101376", "9500320"}, rut=set())
    errors, warns, oks = [], [], []
    vd.kiem_nguon_da_rut(str(page), errors, warns, oks)
    assert not errors and not [w for w in warns if "Phạm vi kiểm rút bài" in w]
    assert any("Rút bài: 2/2" in o for o in oks)


# ── Vòng phản biện độc lập 21/09 ─────────────────────────────────────────────────────────────────────────
def test_nen_ngoai_tuyen_duoc_hoi_cho_ca_pmid_da_co_dau_vet_ok(tmp_path):
    """PMID có bản ghi sổ `ok` còn hạn vẫn có thể bị rút SAU lần kiểm đó — bản đầu chỉ hỏi nền cho PMID «chưa kiểm»."""
    vd, page = _dung_cay(tmp_path, co={"34101376", "9500320"}, rut={"9500320"})     # 9500320 CÓ dấu vết ok nhưng nền nói đã rút
    errors, warns, oks = [], [], []
    vd.kiem_nguon_da_rut(str(page), errors, warns, oks)
    assert any("ĐÃ BỊ RÚT" in e and "9500320" in e for e in errors), (errors, warns)


def test_khong_in_dong_tick_rut_bai_khi_vua_phat_hien_bai_da_rut(tmp_path):
    vd, page = _dung_cay(tmp_path, co={"34101376"}, rut={"9500320"})
    errors, warns, oks = [], [], []
    vd.kiem_nguon_da_rut(str(page), errors, warns, oks)
    assert errors and not any("Rút bài:" in o for o in oks), "vừa in ✗ ĐÃ BỊ RÚT mà vẫn in ✓ «không thấy dương tính»"


def test_retract_and_replace_tu_nen_ngoai_tuyen_duoc_gan_nhan_rut_va_thay(monkeypatch):
    class Nen:
        def tra(self, pmid):
            return {"status": "retracted", "reason": "Error in Data; Retract and Replace", "notice_pmid": "1"} if pmid == "31603910" else None
    monkeypatch.setitem(SO._RW_NGOAI_TUYEN, "da_thu", True)
    monkeypatch.setitem(SO._RW_NGOAI_TUYEN, "chi_muc", Nen())
    ra = SO.rut_bai_retraction_watch_ngoai_tuyen(["31603910"])
    assert ra[0]["rut_va_thay"] is True, "rút-và-thay không được gắn nhãn «rút bỏ hẳn» — khác đường sổ cho cùng loại bài"
    monkeypatch.setitem(SO._RW_NGOAI_TUYEN, "chi_muc", type("N", (), {"tra": lambda self, p: {"status": "retracted", "reason": "Falsification"}})())
    assert SO.rut_bai_retraction_watch_ngoai_tuyen(["9500320"])[0]["rut_va_thay"] is False
