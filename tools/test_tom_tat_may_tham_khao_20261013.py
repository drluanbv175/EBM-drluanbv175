# -*- coding: utf-8 -*-
"""Tóm tắt MÁY cho trích dẫn CHỈ là tài liệu tham khảo (13/10/2026) — `tom_tat_endnote_vi.py`.

Bác sĩ: «Gộp và hoàn thiện với các trích dẫn còn lại». Dashboard không có nội dung riêng cho bài tham khảo ⇒ tóm tắt rút
từ abstract gốc, lưu ở kho riêng, nhãn «chưa qua cổng». Chốt cứng: số trong tóm tắt phải có nguyên văn trong abstract gốc.
Ngoại tuyến hoàn toàn: dashboard là dict giả, EndNote là đối tượng giả.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap(rel: str, ten: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / rel)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


tt = _nap("tools/tom_tat_endnote_vi.py", "_tt_may")
N = _nap("tools/nap_endnote_chu_de.py", "_nap_tt_may")

MUC = {"id": "ITEM-01", "title": "Colchicine dự phòng thứ phát — chưa đủ dùng thường quy", "source": "CONVINCE · Lancet 2024",
       "design": "RCT", "dateVersion": "2024", "pmid": "31111111", "doi": "10.1016/aaa",
       "pico": {"P": ["Đột quỵ", "match"], "I": ["Colchicine", "match"], "C": "Chuẩn", "O": ["Tái phát", "match"]},
       "effectText": "Kết quả chính không đạt ý nghĩa", "effect": {"measure": "HR", "hr": 0.84, "ci": "0.68–1.05"},
       "gradeLevel": "mod", "decision": "notyet", "action": "CHƯA thêm colchicine thường quy",
       "references": ["Kelly P. Lancet 2024. PMID 31111111. doi:10.1016/aaa", "Phụ lục: Smith J. Stroke 2020. PMID 32222222",
                      "Bản chỉ có DOI: doi:10.1093/BBB"]}
GOC = ("Background: Inflammation drives recurrence. Methods: We randomly assigned 1,234 adults aged 40 years or older "
       "to drug or placebo. Findings: The primary outcome occurred in 9·1% vs 12·0% (HR 0·85, 95% CI 0·71–0·93).")
TOM_TAT = {"thiet_ke": "RCT, n = 1234", "P": "Người lớn ≥ 40 tuổi", "I": "Thuốc", "C": "Giả dược",
           "O": "Kết cục chính", "ket_qua": "9.1% so với 12.0%; HR 0.85 (KTC 95% 0.71–0.93)"}


def _doc(bang: dict):
    return lambda p: bang.get(Path(p).name)


def _ds():
    f = Path("/khong-ton-tai/WebDashboard_X_20260614.html")
    d = {"meta": {"question": "Đột quỵ"}, "items": [MUC]}
    return f, _doc({f.name: d}), tt.ngu_canh([f], _doc({f.name: d}))


def test_tham_khao_co_tom_tat_may_nhan_ro_chua_qua_cong_va_khong_gan_khuyen_nghi(tmp_path):
    _, _, ds = _ds()
    muc = ds["pmid:32222222"]
    tom, lech = tt.tom_tat_cho(muc, {"PMID 32222222": TOM_TAT}, GOC)
    assert lech == [] and tom is TOM_TAT
    k = tt.khoi_tieng_viet(muc, tmp_path, tom)
    dong = k.splitlines()
    assert dong[0] == f"{tt.MO_DAU} ℹ️ TÀI LIỆU THAM KHẢO BỔ TRỢ" and "NGUỒN CHÍNH" in dong[1], "vai tham khảo giữ nguyên"
    i = dong.index("ℹ️ TÓM TẮT MÁY TỪ ABSTRACT (chưa qua cổng dashboard — không phải khuyến nghị):")
    assert dong[i + 1:i + 7] == ["   THIẾT KẾ: RCT, n = 1234", "   P · ĐỐI TƯỢNG: Người lớn ≥ 40 tuổi",
                                 "   I · CAN THIỆP/PHƠI NHIỄM: Thuốc", "   C · SO SÁNH: Giả dược",
                                 "   O · KẾT CỤC: Kết cục chính",
                                 "   KẾT QUẢ: 9.1% so với 12.0%; HR 0.85 (KTC 95% 0.71–0.93)"]
    assert dong[-1] == tt.CHAN_MAY and tt.CHAN not in k, "dòng chân phải nói đúng: nội dung rút từ abstract, chưa qua cổng"
    for chu in ("Chứng cứ:", "ÁP DỤNG", "THỰC HÀNH:", "HR 0.84", "CHƯA thêm colchicine"):
        assert chu not in k, f"tóm tắt máy không mang mức chứng cứ/khuyến nghị/kết quả nguồn chính: {chu}"


@pytest.mark.parametrize("sua, lech", [({"ket_qua": "HR 0.77"}, ["0.77"]),
                                       ({"P": "Người lớn ≥ 45 tuổi"}, ["45"]),
                                       ({"ket_qua": "9,1% so với 12,0%"}, ["0", "1", "12", "9"])])
def test_so_khong_co_nguyen_van_trong_abstract_thi_khong_in(tmp_path, sua, lech):
    _, _, ds = _ds()
    tom, bao = tt.tom_tat_cho(ds["pmid:32222222"], {"PMID 32222222": dict(TOM_TAT, **sua)}, GOC)
    assert tom is None and bao == lech, "dấu phẩy thập phân không được chuẩn hoá — phải chép số đúng như abstract"


def test_cac_so_chuan_hoa_cham_giua_lancet_va_phan_cach_hang_nghin():
    assert tt._cac_so("HR 0·85; 1,234 and 12 345; 1,234,567") == {"0.85", "1234", "12345", "1234567"}
    assert tt._cac_so("1, 234") == {"1", "234"}, "dấu phẩy liệt kê (có khoảng trắng) không phải phân cách hàng nghìn"


def test_khong_abstract_thi_tom_tat_co_so_bi_chan_khong_so_thi_in():
    _, _, ds = _ds()
    assert tt.tom_tat_cho(ds["pmid:32222222"], {"PMID 32222222": TOM_TAT}, "")[0] is None
    chu = {"thiet_ke": "Tổng quan tường thuật", "P": "Người bệnh đột quỵ"}
    assert tt.tom_tat_cho(ds["pmid:32222222"], {"PMID 32222222": chu}, "")[0] == chu


def test_muc_chinh_giu_khoi_da_qua_cong_tom_tat_may_tach_rieng_ben_duoi(tmp_path):
    """24/10/2026 (bác sĩ: chứng cứ chưa đạt chuẩn ⇒ tóm tắt tiếng Việt chi tiết vào Abstract): mục chính CÓ mục kho thì nhận
    thêm tóm tắt máy — nhưng khối dashboard đã qua cổng vẫn đứng trước NGUYÊN VẸN với dòng chân của nó; không có mục kho ⇒
    khối như cũ."""
    _, _, ds = _ds()
    muc = ds["pmid:31111111"]
    assert tt.tom_tat_cho(muc, {"PMID 31111111": TOM_TAT}, GOC) == (TOM_TAT, [])
    cu = tt.khoi_tieng_viet(muc, tmp_path, None)
    assert "TÓM TẮT MÁY" not in cu and cu.splitlines()[-1] == tt.CHAN, "không có mục kho ⇒ mục chính chỉ dùng nội dung đã qua cổng"
    k = tt.khoi_tieng_viet(muc, tmp_path, TOM_TAT)
    assert k.startswith(cu + "\n\n"), "khối dashboard + dòng chân «đã qua cổng» giữ nguyên, đứng trước, cách một dòng trống"
    sau = k[len(cu) + 2:].splitlines()
    assert sau[0].startswith("ℹ️ TÓM TẮT MÁY TỪ ABSTRACT") and sau[-1] == tt.CHAN_MAY and tt.CHAN not in sau, \
        "tóm tắt máy có dòng chân riêng — không đứng dưới chân «chép từ dashboard đã qua cổng»"


def test_tra_theo_doi_chu_thuong_va_kho_rong_khong_lam_gi():
    _, _, ds = _ds()
    muc = ds["doi:10.1093/bbb"]
    chu = {"thiet_ke": "Đồng thuận chuyên gia"}
    assert tt.tom_tat_cho(muc, {"DOI 10.1093/bbb": chu}, GOC) == (chu, [])
    assert tt.tom_tat_cho(muc, {}, GOC) == (None, [])
    assert tt.tom_tat_cho(muc, {"DOI 10.1093/bbb": {"thiet_ke": " ", "P": "—"}}, GOC) == (None, []), "toàn ô trống ⇒ không in"


def test_nap_kho_vang_hong_va_hop_le(tmp_path):
    assert tt.nap_tom_tat_abstract(tmp_path) == {} and tt.nap_tom_tat_abstract(None) == {}
    tep = tmp_path / tt.TEP_TOM_TAT_ABS
    tep.write_text("{hỏng", encoding="utf-8")
    with pytest.raises(ValueError):
        tt.nap_tom_tat_abstract(tmp_path)
    tep.write_text(json.dumps({"muc": ["sai khuôn"]}), encoding="utf-8")
    with pytest.raises(ValueError):
        tt.nap_tom_tat_abstract(tmp_path)
    tep.write_text(json.dumps({"_mo_ta": "x", "muc": {"PMID 1": {"P": "a"}}}), encoding="utf-8")
    assert tt.nap_tom_tat_abstract(tmp_path) == {"PMID 1": {"P": "a"}}


class _EndNoteGia:
    def __init__(self, abstract: dict[str, str], khop: dict[str, list[str]]):
        self.abstract = dict(abstract)
        self.khop = khop
        self.da_ghi: list[str] = []
        self.thu_vien = Path("/khong-ton-tai/tv.enl")

    def tim_khop(self, gia_tri, truong):
        return {v: self.khop[v] for v in gia_tri if v in self.khop}

    def doc_truong(self, ids, truong):
        return {m: self.abstract.get(m, "") for m in ids}

    def ghi_truong(self, cap, truong):
        for m, gt in cap:
            self.abstract[m] = gt.replace("\n", "\r")
            self.da_ghi.append(m)
        return {m: "" for m, _ in cap}


def test_ghi_tom_tat_dung_abstract_goc_cua_ban_ghi_va_chay_lai_khong_doi(tmp_path):
    f, doc, _ = _ds()
    en = _EndNoteGia({"r1": "Original.", "r2": GOC, "r3": GOC.replace("0·85", "0·91")},
                     {"31111111": ["r1"], "32222222": ["r2", "r3"]})
    kho_tt = {"PMID 32222222": TOM_TAT}
    bc = tt.ghi_tom_tat(en, [f], kho=tmp_path, ap_dung=True, doc_data=doc, sao_luu=lambda: "/s", tom_tat_abs=kho_tt)
    assert "TÓM TẮT MÁY" in en.abstract["r2"] and en.abstract["r2"].endswith(GOC.split(". ")[-1]), "abstract gốc giữ nguyên"
    assert "TÓM TẮT MÁY" not in en.abstract["r3"], "bản ghi có abstract khác số ⇒ không in tóm tắt cho bản ghi đó"
    assert bc["tom_tat_may"] == 1 and len(bc["tom_tat_lech_so"]) == 1 and "r3" in bc["tom_tat_lech_so"][0]
    assert "TÓM TẮT MÁY" not in en.abstract["r1"]
    bc2 = tt.ghi_tom_tat(en, [f], kho=tmp_path, ap_dung=True, doc_data=doc,
                         sao_luu=lambda: pytest.fail("không đổi thì không ghi"), tom_tat_abs=kho_tt)
    assert bc2["se_ghi"] == 0 and bc2["khong_doi"] == 3


def test_chay_tom_tat_kho_hong_van_chay_khong_tom_tat_may(capsys):
    nhan: dict = {}

    class _TT:
        TEP_TOM_TAT_ABS = tt.TEP_TOM_TAT_ABS

        @staticmethod
        def nap_tom_tat_abstract(dash):
            raise ValueError("thiếu khoá «muc»")

        @staticmethod
        def ghi_tom_tat(endnote, files, **kw):
            nhan.update(kw)
            return {"trich_dan": 1, "co_ban_ghi": 1, "da_ghi": 0, "se_ghi": 0, "khong_doi": 1, "khong_co_ban_ghi": [],
                    "loi": [], "tom_tat_may": 0, "tom_tat_lech_so": []}

    N._nap_doc_data = lambda: None
    bc = N.chay_tom_tat(object(), [Path("/khong-ton-tai/WebDashboard_X.html")], None, False, tt=_TT)
    ra = capsys.readouterr().out
    assert bc is not None and nhan["tom_tat_abs"] == {} and "không đọc được" in ra and "tóm tắt máy (tham khảo) 0" in ra
