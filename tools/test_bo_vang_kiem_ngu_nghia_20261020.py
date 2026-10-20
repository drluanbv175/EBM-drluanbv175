# -*- coding: utf-8 -*-
"""Bộ vàng kiểm chéo ngữ nghĩa (20/10/2026, bác sĩ: «Giải quyết 3 vấn đề chưa đạt»). Ba bất biến được chốt:
(1) máy KHÔNG tự gắn nhãn — nhãn chỉ vào tệp kèm nguyên văn lời bác sĩ; (2) phiếu MÙ với nhận định của máy;
(3) chưa có nhãn ⇒ CHƯA ĐO, không bao giờ in 0% báo động giả. OFFLINE."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

_TOOLS = Path(__file__).resolve().parent
_sp = importlib.util.spec_from_file_location("_bvk_test", _TOOLS / "bo_vang_kiem_ngu_nghia.py")
B = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(B)


def _muc(i, pmid="111", **nhan):
    return {"dashboard": "WebDashboard_EBM_X_20260101.html", "id": f"ITEM-{i}", "title": f"Mục {i}",
            "population": "Suy tim HFpEF", "action": "Dùng thuốc A", "pmid": pmid, "doi": None, "gradeLevel": "high",
            "co_dieu_kien": True,
            "nhan_bac_si": {"dung_quan_the": nhan.get("q"), "dung_chieu": nhan.get("c"),
                            "du_dieu_kien": nhan.get("d"), "ghi_chu": None}}


@pytest.fixture
def tep(tmp_path):
    t = tmp_path / "bo-vang.cho-duyet.json"
    t.write_text(json.dumps({"_mo_ta": "x", "so_muc": 3, "muc": [_muc(1), _muc(2), _muc(3)]}, ensure_ascii=False),
                 encoding="utf-8")
    return t


# ───── đọc lời bác sĩ ─────

def test_doc_loi_mau_chuan_va_ghi_chu_co_dau_cham_phay():
    nhan, loi = B.doc_loi("1: Đ Đ Đ · 2: S Đ Đ quần thể bài là HFrEF · 3: Đ Đ S thiếu «ngoài thai kỳ»; cần xem", 3)
    assert loi == []
    assert nhan[1] == {"dung_quan_the": True, "dung_chieu": True, "du_dieu_kien": True, "ghi_chu": None}
    assert nhan[2]["dung_quan_the"] is False and nhan[2]["ghi_chu"] == "quần thể bài là HFrEF"
    assert nhan[3]["du_dieu_kien"] is False and nhan[3]["ghi_chu"] == "thiếu «ngoài thai kỳ»; cần xem"


def test_khong_dau_ngan_cach_van_tach_dung_muc():
    nhan, loi = B.doc_loi("1: Đ Đ Đ 2: S Đ Đ", 3)
    assert loi == [] and set(nhan) == {1, 2} and nhan[2]["dung_quan_the"] is False


def test_ghi_chu_co_so_thap_phan_va_ti_le_khong_bi_cat():
    nhan, loi = B.doc_loi("mục 2: ✓ ✓ ✗ liều 2.5 mg, tỉ lệ 1:2", 3)
    assert loi == [] and nhan[2]["du_dieu_kien"] is False and nhan[2]["ghi_chu"] == "liều 2.5 mg, tỉ lệ 1:2"


@pytest.mark.parametrize("loi", [
    "1: Đ Đ Đ · 3: Đ Đ",          # mục 3 thiếu một chữ — không được nuốt vào ghi chú mục 1
    "linh tinh",
    "4: Đ Đ Đ",                    # ngoài phạm vi 3 mục
    "1: Đ Đ Đ · 1: S S S",         # trùng số mục — không đoán bản nào đúng
    "1: Đ Q Đ",                    # chữ lạ
])
def test_loi_khong_doc_duoc_bi_bao(loi):
    _nhan, sai = B.doc_loi(loi, 3)
    assert sai


# ───── ghi nhãn ─────

def test_ghi_chay_kho_khong_doi_tep(tep):
    truoc = tep.read_text(encoding="utf-8")
    assert B.ghi_nhan("1: Đ Đ Đ", ap_dung=False, ghi_de=False, tep=tep) == 0
    assert tep.read_text(encoding="utf-8") == truoc


def test_ghi_ap_dung_luu_nguyen_van_loi_bac_si(tep):
    loi = "1: Đ S Đ ngược chiều · 2: Đ Đ Đ"
    assert B.ghi_nhan(loi, ap_dung=True, ghi_de=False, tep=tep) == 0
    muc = json.loads(tep.read_text(encoding="utf-8"))["muc"]
    assert muc[0]["nhan_bac_si"]["dung_chieu"] is False and muc[0]["nhan_bac_si"]["loi_bac_si"] == loi
    assert muc[2]["nhan_bac_si"]["dung_quan_the"] is None   # mục bác sĩ chưa nói vẫn trống


def test_khong_ghi_de_nhan_da_co_tru_khi_ghi_de(tep):
    B.ghi_nhan("1: Đ Đ Đ", ap_dung=True, ghi_de=False, tep=tep)
    B.ghi_nhan("1: S S S", ap_dung=True, ghi_de=False, tep=tep)
    assert json.loads(tep.read_text(encoding="utf-8"))["muc"][0]["nhan_bac_si"]["dung_quan_the"] is True
    B.ghi_nhan("1: S S S", ap_dung=True, ghi_de=True, tep=tep)
    assert json.loads(tep.read_text(encoding="utf-8"))["muc"][0]["nhan_bac_si"]["dung_quan_the"] is False


@pytest.mark.parametrize("loi", ["1: Đ Đ Đ · 2: Đ Đ", "linh tinh · 1: Đ Đ Đ"])
def test_loi_co_phan_khong_doc_duoc_thi_khong_ghi_gi(tep, loi):
    """Một phần đọc được, một phần không ⇒ không ghi phần nào (bác sĩ nói lại cả câu), mã 1."""
    truoc = tep.read_text(encoding="utf-8")
    assert B.ghi_nhan(loi, ap_dung=True, ghi_de=False, tep=tep) == 1
    assert tep.read_text(encoding="utf-8") == truoc


# ───── đo ─────

def test_bang_nham_lan_mau_so_0_la_chua_do():
    b = B.bang_nham_lan([])
    assert b["bao_dong_gia"] is None and b["bo_lot"] is None and B._pt(b["bao_dong_gia"]) == "CHƯA ĐO"


def test_bang_nham_lan_dem_dung():
    # (máy báo, bác sĩ nói sai): tp · fp · fn · tn
    b = B.bang_nham_lan([(True, True), (True, False), (False, True), (False, False), (False, False)])
    assert (b["tp"], b["fp"], b["fn"], b["tn"]) == (1, 1, 1, 2)
    assert b["bao_dong_gia"] == pytest.approx(1 / 3) and b["bo_lot"] == pytest.approx(1 / 2)


def _kiem_gia(k1_bao: bool, k4_bao: bool):
    def kiem_muc(_it, _tx):
        return {"k1_nguong": [], "k1_cap": [{"muc": "can_doc" if k1_bao else "khop"}],
                "k4": {"muc": "can_doc" if k4_bao else "khop"}}
    return kiem_muc


def test_do_chi_tinh_muc_co_nhan_va_co_nguon():
    bv = {"muc": [_muc(1, pmid="1", q=True, c=True, d=True),      # máy báo cả hai ⇒ 2 báo động giả
                  _muc(2, pmid="2", q=False, c=False, d=False),   # có nhãn nhưng chưa có nguồn
                  _muc(3, pmid="3")]}                               # chưa có nhãn
    kq = B.do(bv, {"1": "abc", "2": None, "3": "abc"}, kiem_muc=_kiem_gia(True, True))
    assert kq["K1"]["fp"] == 1 and kq["K1"]["n"] == 1 and kq["K4"]["fp"] == 1
    assert kq["chua"] == {"chua_nhan": 1, "chua_nguon": 1}
    assert kq["muc_rung_dieu_kien"] == 1 and kq["so_nhan_dieu_kien"] == 2


def test_do_bo_lot_khi_bac_si_noi_sai_ma_may_im():
    bv = {"muc": [_muc(1, pmid="1", q=False, c=False)]}
    kq = B.do(bv, {"1": "abc"}, kiem_muc=_kiem_gia(False, False))
    assert kq["K1"]["fn"] == 1 and kq["K4"]["fn"] == 1 and kq["K1"]["bo_lot"] == 1.0


def test_muc_chua_nhan_khong_bi_dem_them_vao_chua_nguon():
    kq = B.do({"muc": [_muc(1, pmid="9")]}, {"9": None}, kiem_muc=_kiem_gia(True, True))
    assert kq["chua"] == {"chua_nhan": 1, "chua_nguon": 0}


def test_do_chua_nhan_thi_rung_dieu_kien_la_chua_do():
    kq = B.do({"muc": [_muc(1)]}, {"111": "abc"}, kiem_muc=_kiem_gia(True, True))
    assert kq["muc_rung_dieu_kien"] is None and kq["K1"]["n"] == 0


def test_do_voi_kiem_muc_that():
    """Dùng CHÍNH kiem_quan_the_chieu.kiem_muc: mục HFpEF, nguồn chỉ nói HFrEF ⇒ K1 báo; bác sĩ xác nhận sai ⇒ tp."""
    bv = {"muc": [_muc(1, pmid="1", q=False, c=True)]}
    kq = B.do(bv, {"1": "Patients with heart failure with reduced ejection fraction (HFrEF) were randomized."})
    assert kq["K1"]["tp"] == 1 and kq["K4"]["tn"] == 1


# ───── phiếu mù ─────

TOM_TAT = ("1. N Engl J Med. 2026;1:1.\n\nTrial title.\n\nSmith A(1).\n\nAuthor information:\n(1)Dept X. "
           "smith@uni.edu\n\nBACKGROUND: Patients with HFrEF. Contact a.b@c.org.\n\nCopyright © 2026.\n\n"
           "DOI: 10.1/x\nPMID: 111")


def test_phieu_mu_voi_nhan_dinh_cua_may_va_che_email():
    md = B.dung_phieu_md({"muc": [_muc(1)]}, {"111": TOM_TAT})
    assert "Suy tim HFpEF" in md and "Dùng thuốc A" in md and "PMID 111" in md
    for la in ("co_dieu_kien", "can_doc", "🟠", "k1_", "K4", "gradeLevel"):
        assert la not in md
    assert "smith@uni.edu" not in md and "a.b@c.org" not in md and "Author information" not in md
    assert "BACKGROUND: Patients with HFrEF" in md


def test_phieu_thieu_tom_tat_noi_ro():
    md = B.dung_phieu_md({"muc": [_muc(1)]}, {"111": None})
    assert "chưa tải được" in md


def test_main_thieu_tep_tra_2(monkeypatch, tmp_path):
    monkeypatch.setattr(B, "TEP_BO_VANG", tmp_path / "khong-co.json")
    assert B.main(["do"]) == 2


# ───── tệp bộ vàng đã commit ─────

def test_moi_nhan_trong_bo_vang_deu_kem_loi_bac_si():
    """Máy không tự gắn nhãn (audit/16, bác sĩ duyệt 25/09/2026): nhãn khác null mà thiếu nguyên văn lời bác sĩ ⇒ đỏ."""
    tep = B.TEP_BO_VANG
    assert tep.is_file(), "tệp ứng viên bộ vàng phải được commit cùng công cụ"
    for m in json.loads(tep.read_text(encoding="utf-8"))["muc"]:
        nh = m.get("nhan_bac_si") or {}
        if any(nh.get(k) is not None for k in B.NHAN):
            assert isinstance(nh.get("loi_bac_si"), str) and nh["loi_bac_si"].strip(), m.get("id")
