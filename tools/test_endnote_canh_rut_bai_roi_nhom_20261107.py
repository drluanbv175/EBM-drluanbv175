# -*- coding: utf-8 -*-
"""Canh RÚT BÀI cho toàn thư viện EndNote + cảm biến RỜI NHÓM CHỦ ĐỀ (07/11/2026, bác sĩ: «Làm 1 và 2 trước cho tôi»).

Đo thật 07/11/2026: nền Retraction Watch trên máy 48 ngày (hạn 30), không tác vụ nào làm mới khi quá hạn; bản ghi EndNote ngoài
dashboard không ai đối chiếu rút bài; một lượt đồng bộ online làm 11 bản ghi rời nhóm chủ đề. Kiểm: (1) phân loại rút bài
(Retraction ⇒ rút, EoC ⇒ riêng, tra DOI khi PMID «không biết», không định danh ⇒ không kiểm được); (2) nền vắng/quá hạn KHÔNG
BAO GIỜ thành «không có bài rút»; (3) bài rút mất tư cách ★ và cần tag ⛔; (4) rời nhóm = mang khoá chủ đề mà không thuộc nhóm
phân loại NÀO (không so tên — 43/44 «lệch tên» đo 07/11 là báo động giả), trừ loai_bo đề tài và nhóm chờ thùng rác;
(5) `--dua-ve-nhom` ghi hàng chờ theo nhóm có thật, nhóm vắng ⇒ chọn tay; (6) hòm việc báo đúng mức."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / "tools" / tep)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


R = _nap("_rbe_test", "kiem_rut_bai_endnote.py")
G = _nap("_gte_rbe_test", "gan_tag_endnote.py")
tdxv = _nap("_tdxv_rbe_test", "tu_de_xuat_viec.py")
AD, RUT = G.TAG_AP_DUNG, G.TAG_RUT_BAI

CHI_MUC = {"pmid": {"111": {"status": "retracted", "nature": "Retraction", "retraction_date": "2/6/2010"},
                    "222": {"status": "expression_of_concern", "nature": "Expression of concern"}},
           "doi": {"10.1/rut": {"status": "retracted", "nature": "Retraction"}}}


def _tra_pmid(p):
    return CHI_MUC["pmid"].get(p)


def _tra_doi(d):
    return CHI_MUC["doi"].get(d)


class _ChiMucGia:
    def __init__(self, tuoi):
        self._tuoi = tuoi

    def tra(self, p):
        return _tra_pmid(p)

    def tra_doi(self, d):
        return _tra_doi(d)

    def tuoi_ngay(self):
        return self._tuoi


# ───────────────────────── (1) phân loại ─────────────────────────

def test_phan_loai_rut_eoc_doi_va_khong_dinh_danh():
    bg = {1: {"pmid": "111"}, 2: {"pmid": "222"}, 3: {"pmid": "999", "doi": "10.1/rut"}, 4: {"pmid": None, "doi": None},
          5: {"pmid": "555", "doi": "10.9/sach"}}
    kq = R.phan_loai(bg, _tra_pmid, _tra_doi)
    assert [m["rec"] for m in kq["rut"]] == [1, 3]           # 3: PMID «không biết» ⇒ tra DOI
    assert [m["rec"] for m in kq["eoc"]] == [2]               # EoC KHÔNG lẫn vào rút bài
    assert kq["khong_dinh_danh"] == [4] and kq["da_kiem"] == 4


def test_dinh_danh_accession_chu_khong_phai_pmid():
    assert R.dinh_danh("EBM-TT:EBM_VanDeCuThe_X", None) == (None, None)
    assert R.dinh_danh(" 12345 ", "10.1000/x") == ("12345", "10.1000/x")
    assert R.dinh_danh("12345", "zenodo-khong-doi") == ("12345", None)


# ───────────────────────── (2) không đo được / quá hạn ≠ sạch ─────────────────────────

@pytest.mark.parametrize("tuoi, qua_han, ma", [(3.0, False, 0), (31.0, True, 2), (None, True, 2)])
def test_nen_qua_han_khong_bao_gio_xanh(tuoi, qua_han, ma):
    kq = R.kiem_ban_ghi({1: {"pmid": "555"}}, _ChiMucGia(tuoi))
    assert kq["do_duoc"] and kq["qua_han"] is qua_han and R.ma_thoat(kq) == ma
    assert ("🟡" in R.dong_nen(kq)) is qua_han


def test_khong_do_duoc_va_co_rut():
    khong = {"do_duoc": False, "ly_do": "nền vắng"}
    assert R.ma_thoat(khong) == 2 and R.tom_tat_mot_dong(khong).startswith("⚪")
    co = R.kiem_ban_ghi({1: {"pmid": "111"}}, _ChiMucGia(1.0))
    assert R.ma_thoat(co) == 1 and "🔴 1 bản ghi ĐÃ RÚT" in R.tom_tat_mot_dong(co)
    sach = R.kiem_ban_ghi({1: {"pmid": "555"}}, _ChiMucGia(1.0))
    assert "chưa thấy trong danh mục ≠ chưa bị rút" in R.tom_tat_mot_dong(sach)


def test_kiem_rut_bai_loi_thanh_khong_do_duoc(monkeypatch):
    def hong(*a, **k):
        raise RuntimeError("engine hỏng")
    monkeypatch.setattr(G, "_nap", hong)
    rb = G._kiem_rut_bai({1: {"pmid": "1"}}, {})
    assert rb["do_duoc"] is False and "RuntimeError" in rb["ly_do"]
    assert G.dong_rut_bai({"kiem_rut_bai": rb}).startswith("⚪")


# ───────────────────────── (3) bài rút trong kế hoạch gắn tag ─────────────────────────

def _muc(grade="high"):
    return {"vai": "muc", "decision": "apply", "gradeLevel": grade, "design": "RCT", "ban_cu": False}


def _ke_hoach(**kw):
    mac_dinh = dict(ban_ghi={1: {"pmid": "11"}, 2: {"pmid": "22"}},
                    nhom=[{"group_id": 9, "ten": "EBM · Suy tim", "rec": [1, 2]}],
                    tag_hien_co={1: {"Tim mạch", AD}, 2: {"Tim mạch"}}, ten_tag={"Tim mạch", AD},
                    anh_xa={}, chuyen_khoa=lambda q: "Tim mạch",
                    ngu_canh_cua=lambda p, d: [_muc()] if p == "11" else [], tag_le={})
    mac_dinh.update(kw)
    return G.lap_ke_hoach(**mac_dinh)


def test_bai_rut_mat_tu_cach_ap_dung_va_can_tag_rut():
    kh = _ke_hoach(rut_bai={1, 77})                             # 77 không thuộc ban_ghi (thùng rác) ⇒ bỏ qua
    assert kh["rut_bai"] == [1]
    assert kh["thieu"] == {RUT: [1]} and list(kh["thieu"])[0] == RUT
    assert kh["thua_ap_dung"] == [1]                           # ★ đang có trên bài rút ⇒ phải gỡ
    assert kh["dat_ap_dung"] == 0 and RUT in kh["tag_chua_tao"]
    kh_sach = _ke_hoach()
    assert kh_sach["rut_bai"] == [] and kh_sach["thua_ap_dung"] == [] and kh_sach["dat_ap_dung"] == 1


def test_tag_rut_bai_trung_giua_hai_cong_cu():
    assert G.TAG_RUT_BAI == R.TAG_RUT_BAI


def test_dong_rut_bai_trong_dong_tom_tat():
    co_rut = {"do_duoc": True, "rut": [{"rec": 5}], "eoc": [], "qua_han": False, "tuoi_ngay": 2.0, "da_kiem": 10}
    kh = dict(_ke_hoach(), do_duoc=True, tag_trung=[], kiem_rut_bai=co_rut)
    assert not G.con_viec(kh)
    assert G.tom_tat_mot_dong(kh).startswith("✓") and "🔴 1 bản ghi ĐÃ RÚT" in G.tom_tat_mot_dong(kh)
    qua_han = dict(co_rut, rut=[], qua_han=True, tuoi_ngay=48.0)
    assert "🟡 nền Retraction Watch 48 ngày" in G.dong_rut_bai({"kiem_rut_bai": qua_han})
    sach = dict(co_rut, rut=[])
    assert G.tom_tat_mot_dong(dict(kh, kiem_rut_bai=sach)) == f"✓ tag EndNote đủ (1 bản ghi mang «{AD}»)"
    assert G.dong_rut_bai({}) is None                          # kế hoạch không mang kết quả kiểm ⇒ không bịa câu


# ───────────────────────── (4) rời nhóm chủ đề ─────────────────────────

def test_khoa_chu_de_khong_bat_nhan_tom_tat():
    kw = "EBM: EBM_VanDeCuThe_SuyTim_20261101\rEBM: tóm tắt chủ đề\rEBM: DE-TAI_btm-dtd2-ngoai-tru-BVQY175"
    assert G.KHOA_CHU_DE.findall(kw) == ["EBM_VanDeCuThe_SuyTim_20261101", "DE-TAI_btm-dtd2-ngoai-tru-BVQY175"]


def test_roi_nhom_dung_dinh_nghia():
    bg = {r: {"pmid": None, "khoa": ["EBM_X"]} for r in (1, 2, 3, 4, 5, 6)}
    bg[7] = {"pmid": None, "khoa": []}
    nhom = [{"group_id": 9, "ten": "Tên nhóm đã đổi", "rec": [1]},                  # nhóm khác tên ⇒ vẫn là ĐÃ ở nhóm
            {"group_id": 170, "ten": "_Can toan van - Find Full Text", "rec": [2]},  # chỉ ở nhóm làm việc ⇒ rời nhóm
            {"group_id": 39, "ten": "_Cho thung rac 20261106", "rec": [3]},          # chờ thùng rác ⇒ không báo
            {"group_id": 173, "ten": "Not found", "loai": "TYPE;7", "rec": [4]}]     # nhóm hệ thống ⇒ không tính
    kh = _ke_hoach(ban_ghi=bg, nhom=nhom, tag_hien_co={}, bang_nhom={"EBM_X": "EBM · Chủ đề X"}, loai_bo={6})
    assert [m["rec"] for m in kh["roi_nhom"]] == [2, 4, 5]
    assert kh["roi_nhom"][0] == {"rec": 2, "khoa": "EBM_X", "nhom": "EBM · Chủ đề X"}
    assert 2 not in kh["chua_phan_loai"] and 7 in kh["chua_phan_loai"]     # không báo trùng; 7 không khoá ⇒ chưa phân loại
    assert G.con_viec(kh) and "3 bản ghi rời nhóm chủ đề" in G.tom_tat_mot_dong(dict(kh, do_duoc=True))


def test_loai_bo_de_tai(tmp_path):
    ma = "btm-x"
    (tmp_path / ma).mkdir()
    (tmp_path / ma / f"DANH_MUC_TRICH_DAN_{ma}.json").write_text(json.dumps(
        {"loai_bo": [{"pmid": "111"}, {"pmid": None, "doi": "10.1/ABC"}]}), encoding="utf-8")
    bg = {1: {"pmid": "111", "khoa": [f"DE-TAI_{ma}"]}, 2: {"pmid": None, "doi": "10.1/abc", "khoa": [f"DE-TAI_{ma}"]},
          3: {"pmid": "333", "khoa": [f"DE-TAI_{ma}"]}, 4: {"pmid": "111", "khoa": ["EBM_Khac"]}}
    assert G.loai_bo_de_tai(bg, tmp_path) == {1, 2}            # 4: cùng PMID nhưng không thuộc đề tài ⇒ không miễn
    assert G.loai_bo_de_tai(bg, None) == set()                 # không thấy exports ⇒ thà báo thừa


def test_dua_ve_nhom_ghi_hang_cho_nhom_co_that():
    goi = []

    def ghi(tv, ten, *, them, da_vao, group_id):
        goi.append((ten, them, group_id))
        return them
    kh = {"do_duoc": True, "thu_vien": "x.enl",
          "roi_nhom": [{"rec": 1, "khoa": "EBM_X", "nhom": "EBM · X"}, {"rec": 2, "khoa": "EBM_X", "nhom": "EBM · X"},
                       {"rec": 3, "khoa": "EBM_Y", "nhom": "Nhóm đã xoá"}, {"rec": 4, "khoa": "EBM_Z", "nhom": None}]}
    nhom = [{"group_id": 9, "ten": "EBM · X", "loai": "custom"}, {"group_id": 172, "ten": "Nhóm đã xoá", "loai": "TYPE;7"}]
    ra = []
    ma = G.dua_ve_nhom(kh, nhom=nhom, ghi=ghi, khoa_ten=lambda t: t.strip().lower(), in_ra=ra.append)
    assert goi == [("EBM · X", [1, 2], [9])]                   # nhóm hệ thống cùng tên KHÔNG được nhận
    assert ma == G.MA_CON_VIEC and sum("chọn tay" in x for x in ra) == 2
    assert G.dua_ve_nhom({"do_duoc": True, "roi_nhom": []}, nhom=[], ghi=ghi, khoa_ten=str, in_ra=ra.append) == G.MA_OK


# ───────────────────────── (5) hòm việc ─────────────────────────

def test_hom_viec_bao_rut_bai_dung_muc(monkeypatch):
    chet = []
    monkeypatch.setattr(tdxv, "_ghi_chet", lambda lenh, ly: chet.append(ly))
    co = {"do_duoc": True, "rut": [{"rec": 5}], "eoc": [{"rec": 6}], "qua_han": True, "tuoi_ngay": 48.0}
    kh = {"do_duoc": True, "thieu": {}, "thua_ap_dung": [], "tag_chua_tao": [], "nhom_chua_anh_xa": [],
          "roi_nhom": [{"rec": 9}], "kiem_rut_bai": co}
    ra = tdxv.giac_quan_gan_tag_endnote(lambda: kh)
    muc = {(r[0], r[1]) for r in ra}
    assert (0, "👤") in muc and (1, "👤") in muc and (2, "🤖") in muc and (2, "🛎") in muc
    assert any("ĐÃ RÚT" in r[2] and "5" in r[2] for r in ra)
    ra2 = tdxv.giac_quan_gan_tag_endnote(lambda: dict(kh, roi_nhom=[], kiem_rut_bai={"do_duoc": False, "ly_do": "nền vắng"}))
    assert ra2 == [] and chet == ["nền vắng"]                  # không đo được ⇒ giác quan chết, không phải «sạch»


# ───────────────────────── (6) đầu–cuối với chỉ mục THẬT của engine (khi có engine) ─────────────────────────

def test_dau_cuoi_chi_muc_engine_that(tmp_path):
    bst = _nap("_bst_rbe_test", "ban_sao_tran.py")
    mea = bst.duong_goc("medical-ebm-automation", REPO)
    if mea is None or not (mea / "app" / "sources" / "retraction_watch.py").is_file():
        pytest.skip("không có repo y khoa cạnh repo gốc (CI/worktree) — phần thuần đã kiểm ở trên")
    import sys
    sys.path.insert(0, str(mea))
    from app.sources.retraction_watch import RetractionWatchIndex
    cot = ["Record ID", "Title", "Journal", "RetractionDate", "RetractionDOI", "RetractionPubMedID", "OriginalPaperDOI",
           "OriginalPaperPubMedID", "RetractionNature", "Reason"]
    dong = [["1", "a", "j", "2/6/2010", "", "0", "10.1016/x1", "9500320", "Retraction", ""],
            ["2", "b", "j", "1/1/2020", "", "0", "10.9/eoc", "222", "Expression of concern", ""],
            ["3", "c", "j", "1/1/2020", "", "0", "10.9/corr", "333", "Correction", ""],
            ["4", "d", "j", "1/1/2019", "", "0", "", "444", "Retraction", ""],
            ["5", "d", "j", "1/1/2021", "", "0", "", "444", "Reinstatement", ""]]
    csv = tmp_path / "rw.csv"
    csv.write_text("\n".join(",".join(x) for x in [cot, *dong]) + "\n", encoding="utf-8")
    meta = tmp_path / "rw.meta.json"
    meta.write_text(json.dumps({"tai_ve_luc": "2099-01-01T00:00:00+00:00"}), encoding="utf-8")
    idx = RetractionWatchIndex(csv_path=csv, meta_path=meta)
    kq = R.kiem_ban_ghi({1: {"pmid": "9500320"}, 2: {"pmid": "222"}, 3: {"pmid": "333"}, 4: {"pmid": "444"},
                         5: {"pmid": None, "doi": "https://doi.org/10.1016/X1"}}, idx)
    assert [m["rec"] for m in kq["rut"]] == [1, 5]              # DOI chuẩn hoá (tiền tố + chữ hoa) vẫn bắt được
    assert [m["rec"] for m in kq["eoc"]] == [2]                 # Correction không tính; Reinstatement (444) không kết luận


def test_bai_rut_chua_co_sao_khong_bi_doi_gan_sao_va_tag_rut_xep_dau():
    """Bài rút đạt tiêu chí cũ (apply/high) mà CHƯA mang ★ ⇒ kế hoạch không được đòi gắn ★; tag ⛔ đứng đầu danh sách."""
    kh = _ke_hoach(tag_hien_co={1: {"Tim mạch"}, 2: set()}, rut_bai={1})
    assert AD not in kh["thieu"]
    assert list(kh["thieu"]) == [RUT, "Tim mạch"] and kh["thieu"]["Tim mạch"] == [2]


def test_chi_roi_nhom_cung_la_con_viec():
    kh = _ke_hoach(ban_ghi={1: {"pmid": None, "khoa": ["EBM_X"]}}, nhom=[], tag_hien_co={1: {"Tim mạch"}}, bang_nhom={})
    assert kh["roi_nhom"] == [{"rec": 1, "khoa": "EBM_X", "nhom": None}]
    assert kh["thieu"] == {} and kh["chua_phan_loai"] == [] and G.con_viec(kh)
