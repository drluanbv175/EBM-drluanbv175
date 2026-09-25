"""Kiểm K1 (quần thể) · K4 (chiều khuyến cáo) của `tools/kiem_cheo_ngu_nghia.py` — NGOẠI TUYẾN.

Mọi tóm tắt nguồn là giả, dựng tại chỗ; hàm tải mạng bị thay bằng hàm giả. Mỗi ca khoá MỘT luật để
phép đột biến trên luật đó làm đỏ đúng ca (audit/16, 25/09/2026).
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

_TEP = Path(__file__).resolve().parent / "kiem_cheo_ngu_nghia.py"
_sp = importlib.util.spec_from_file_location("kiem_cheo_ngu_nghia_k1k4", _TEP)
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)


@pytest.fixture(autouse=True)
def _khong_ngu(monkeypatch):
    monkeypatch.setattr(M, "_NGU", lambda s: None)


def _nguon(title: str, *phan: tuple[str, str]) -> dict:
    return {"title": title, "phan": list(phan), "nguon": "pubmed"}


def _muc(**kw) -> dict:
    it = {"id": "ITEM-01", "decision": "apply", "title": "", "population": "", "action": "Dùng thuốc.",
          "pico": {"P": ["", "match"], "I": ["", "match"]}, "pmid": "11111111"}
    it.update(kw)
    return it


# ── Tải tóm tắt ────────────────────────────────────────────────────────────────────────
_XML = """<?xml version="1.0"?><PubmedArticleSet>
<PubmedArticle><MedlineCitation><PMID>11111111</PMID><Article><ArticleTitle>Drug X in <i>HFrEF</i>.</ArticleTitle>
<Abstract><AbstractText Label="METHODS" NlmCategory="METHODS">Adults with reduced ejection fraction.</AbstractText>
<AbstractText NlmCategory="CONCLUSIONS">Drug X did not reduce mortality.</AbstractText></Abstract>
</Article></MedlineCitation></PubmedArticle>
<PubmedBookArticle><BookDocument><PMID>22222222</PMID><ArticleTitle>Book chapter</ArticleTitle>
<Abstract><AbstractText>Summary text.</AbstractText></Abstract></BookDocument></PubmedBookArticle>
</PubmedArticleSet>"""

_EPMC = json.dumps({"resultList": {"result": [{
    "pmid": "33333333", "title": "Trial <i>Y</i>",
    "abstractText": "<h4>Background</h4>Some text.<h4>Conclusions</h4>Y is not recommended."}]}})


def test_doc_xml_pubmed_lay_nhan_muc_va_ca_sach():
    kq = M.doc_xml_pubmed(_XML)
    assert kq["11111111"]["title"] == "Drug X in HFrEF."
    assert kq["11111111"]["phan"] == [("METHODS", "Adults with reduced ejection fraction."),
                                      ("CONCLUSIONS", "Drug X did not reduce mortality.")]
    assert kq["22222222"]["phan"] == [("", "Summary text.")]


def test_ncbi_tra_html_thi_lui_europe_pmc_va_hai_nguon_hong_thi_rong():
    def tai(url):
        if "efetch" in url:
            return b"<html><body>misuse</body></html>"
        return _EPMC.encode()
    kq, loi = M.tai_tom_tat(["33333333"], tai=tai)
    assert kq["33333333"]["nguon"] == "europepmc"
    assert kq["33333333"]["phan"] == [("Background", "Some text."), ("Conclusions", "Y is not recommended.")]
    assert loi and "PubMed" in loi[0]

    def hong(url):
        raise OSError("mất mạng")
    kq2, loi2 = M.tai_tom_tat(["33333333"], tai=hong)
    assert kq2 == {} and len(loi2) == 2           # không bao giờ bịa kết quả khi mạng hỏng


# ── K1a · cặp loại trừ nhau ─────────────────────────────────────────────────────────────
def _k1_cap(pop: str, nguon: dict) -> list[str]:
    return [c["muc"] for c in M.k1_cap(M.chuan_hoa(pop), nguon)]


def test_hfref_vs_hfpef_tieu_de_la_canh_bao_cung_ve_la_khop():
    kq = {c["ghi_chu"].split(":")[0]: c["muc"] for c in M.k1_cap(
        M.chuan_hoa("HFrEF"), _nguon("Drug X in heart failure with preserved ejection fraction"))}
    assert kq == {"suy tim EF giảm ↔ EF bảo tồn": "can_doc"}
    assert _k1_cap("HFrEF", _nguon("Drug X in heart failure with reduced ejection fraction")) == ["con"]


def test_mildly_reduced_khong_duoc_doc_thanh_hfref():
    assert _k1_cap("HFrEF", _nguon("Drug X in heart failure with mildly reduced ejection fraction")) == ["chua_kiem"]


def test_non_pregnant_khong_bi_doc_thanh_mang_thai():
    assert _k1_cap("Phụ nữ ngoài thai kỳ", _nguon("Drug X in non-pregnant women of reproductive age")) == ["con"]
    assert _k1_cap("Thai phụ", _nguon("Drug X in non-pregnant women of reproductive age")) == ["can_doc"]


def test_ve_kia_chi_mot_cau_la_thoang_qua_tieu_de_hoac_hai_cau_moi_canh_bao():
    mot = _nguon("Hepatitis B guideline", ("", "We address treatment. Infants born to mothers need vaccine."))
    assert _k1_cap("Người lớn nhiễm HBV", mot) == ["chua_kiem"]
    hai = _nguon("Hepatitis B trial", ("", "Children were randomized. Children received drug X."))
    assert _k1_cap("Người lớn nhiễm HBV", hai) == ["can_doc"]
    tieu_de = _nguon("Drug X in children with hepatitis B", ("", "Outcome improved."))
    assert _k1_cap("Người lớn nhiễm HBV", tieu_de) == ["can_doc"]


def test_cau_tieu_chuan_loai_tru_khong_tinh_la_quan_the():
    # vế KIA chỉ nằm trong câu loại trừ ⇒ không được thành 🟠
    n = _nguon("Asthma trial", ("", "Children were excluded. Adolescents were not eligible. Patients received X."))
    assert _k1_cap("Người lớn hen", n) == ["chua_kiem"]
    # vế CÙNG chỉ nằm trong câu loại trừ ⇒ không được thành ✓ (nguồn thật ra nghiên cứu trẻ em)
    n2 = _nguon("Asthma trial", ("", "Adults were excluded. Children were enrolled. Children received X."))
    assert _k1_cap("Người lớn hen", n2) == ["can_doc"]


# ── K1b · ngưỡng số ─────────────────────────────────────────────────────────────────────
def _k1_so(pop: str, nguon: dict, tv: str | None = None) -> list[tuple[str, str]]:
    return [(c["muc"], c["ghi_chu"]) for c in M.k1_nguong(M.chuan_hoa(pop), nguon, tv)]


def test_nguong_egfr_khac_la_canh_bao_trung_la_khop():
    n = _nguon("Drug X in CKD", ("METHODS", "Adults with an eGFR of 25 to 75 ml/min/1.73 m2 were enrolled."))
    assert _k1_so("Người lớn CKD, eGFR ≥ 20 mL/phút/1,73 m²", n)[0][0] == "can_doc"
    assert _k1_so("Người lớn CKD, eGFR 25–75", n)[0][0] == "con"


def test_so_khong_dinh_mo_neo_khong_bi_vet_vao():
    n = _nguon("Trial", ("METHODS", "Patients with an ejection fraction of 40% or less."))
    assert _k1_so("HFrEF, LVEF ≤ 40% (n = 5988)", n) == [("con", "EF 40 có trong tóm tắt")]


def test_tuoi_trung_binh_tach_khoi_nguong_tuoi():
    n = _nguon("Cohort", ("METHODS", "Participants had a mean age of 74.2 years."))
    assert _k1_so("3.619 người, tuổi trung bình 74,2 (ĐLC 6,99)", n)[0][0] == "con"
    n2 = _nguon("RA cohort", ("METHODS", "3002 patients, mean age 61 years."))
    assert _k1_so("Người ≥ 50 tuổi viêm khớp dạng thấp", n2)[0][0] == "chua_kiem"   # ngưỡng ≠ trung bình


def test_so_viet_kieu_viet_va_kieu_anh_so_duoc_voi_nhau():
    n = _nguon("TDF", ("METHODS", "Pregnant women with HBV DNA ≥200,000 IU/mL."))
    assert _k1_so("Thai phụ HBV DNA > 200.000 IU/mL", n)[0][0] == "con"


def test_so_o_phan_ket_qua_chi_xac_nhan_khong_tao_mau_thuan():
    n = _nguon("Drug X", ("METHODS", "Adults with type 2 diabetes."), ("RESULTS", "HbA1c <7% was reached by 40%."))
    assert _k1_so("ĐTĐ típ 2, HbA1c 8–10,5%", n)[0][0] == "chua_kiem"


def test_toan_van_chi_nang_chua_kiem_len_khop():
    n = _nguon("PARADIGM", ("METHODS", "Patients with an ejection fraction of 40% or less."))
    assert _k1_so("HFrEF, LVEF 35–40%", n)[0][0] == "chua_kiem"
    tv = "The ejection fraction of 35% or less was required after an amendment."
    assert _k1_so("HFrEF, LVEF 35–40%", n, tv)[0][0] == "con"


def test_co_mau_chi_khop_hoac_chua_kiem():
    assert [c["muc"] for c in M.k2_co_mau(M.chuan_hoa("COPD, gộp 42 nghiên cứu (N=54.278)"),
                                         M.chuan_hoa("42 studies with 54,278 participants."))] == ["con", "con"]
    assert [c["muc"] for c in M.k2_co_mau(M.chuan_hoa("N=999"), M.chuan_hoa("1000 participants"))] == ["chua_kiem"]


# ── K4 · chiều khuyến cáo ───────────────────────────────────────────────────────────────
def test_ket_luan_phu_dinh_hieu_qua_la_canh_bao():
    it = _muc(title="Drug X giảm tử vong", action="Dùng Drug X cho HFrEF.")
    n = _nguon("Trial of Drug X", ("RESULTS", "Deaths occurred."), ("CONCLUSIONS", "Drug X did not reduce mortality."))
    assert M.k4_chieu(it, n)["muc"] == "can_doc"


def test_phu_dinh_o_phan_ket_qua_khong_phai_ket_luan_thi_khong_bao():
    it = _muc(action="Dùng Drug X.")
    n = _nguon("Trial", ("RESULTS", "Drug X did not reduce hospitalization."), ("CONCLUSIONS", "Drug X improved survival."))
    assert M.k4_chieu(it, n)["muc"] == "con"


def test_khuyen_cao_phu_dinh_phai_nhac_dung_can_thiep():
    n = _nguon("Guideline", ("", "Corticosteroids are not recommended in nonsevere disease. Treat early. Follow up."))
    co = _muc(title="Corticosteroids cho CAP nặng", pico={"P": ["", ""], "I": ["Corticosteroids", ""]})
    khong = _muc(title="Kháng sinh ≥3 ngày", pico={"P": ["", ""], "I": ["Amoxicillin", ""]})
    assert M.k4_chieu(co, n)["muc"] == "can_doc"
    assert M.k4_chieu(khong, n)["muc"] == "con"


def test_phu_dinh_kep_should_not_be_withheld_khong_la_nguoc_chieu():
    it = _muc(title="Beta-blockers trong COPD", pico={"P": ["", ""], "I": ["Cardioselective beta-blockers", ""]})
    n = _nguon("Review", ("CONCLUSIONS", "Cardioselective beta-blockers should not be routinely withheld."))
    assert M.k4_chieu(it, n)["muc"] == "con"


def test_muc_lam_it_di_khong_ap_chi_xet_cau_dau():
    n = _nguon("Trial", ("CONCLUSIONS", "Drug X did not reduce mortality."))
    assert M.k4_chieu(_muc(action="Không dùng Drug X thường quy."), n)["muc"] == "khong_ap"
    assert M.k4_chieu(_muc(action="Dừng kháng sinh sau 3 ngày khi ổn định."), n)["muc"] == "khong_ap"
    lam = _muc(action="Dùng Drug X cho HFrEF. Khi đổi thuốc phải ngưng ACEi 36 giờ.")
    assert M.k4_chieu(lam, n)["muc"] == "can_doc"          # «ngưng» ở câu sau không đổi chiều


def test_k4_khong_nguon_hoac_chi_tieu_de_la_chua_kiem():
    assert M.k4_chieu(_muc(), None)["muc"] == "chua_kiem"
    assert M.k4_chieu(_muc(), _nguon("Trial of drug X"))["muc"] == "chua_kiem"


def test_mo_neo_loai_chu_viet_hoa_va_to_chuc_giu_viet_tat_thuoc():
    it = _muc(title="KHUNG CHẨN ĐOÁN — ATS 2025 CAP: DOAC và SGLT2i", pico={"P": ["", ""], "I": ["Dapagliflozin", ""]})
    assert M.neo_can_thiep(it) == ["dapagliflozin", "doac", "sglt2"]


# ── Toàn dòng lệnh, với dashboard giả ──────────────────────────────────────────────────
DASH_HTML = """<html><script>
const DATA = {
  meta:{question:'Q', updated:'2026-09-25'},
  summary:{conclusion:'Dùng X.', doNow:['A'], dontDo:['B'], redFlags:['C']},
  items:[
    {id:'ITEM-01', title:'Drug X cho HFrEF', pmid:'11111111', decision:'apply', population:'Người lớn HFrEF',
     pico:{P:['HFrEF','match'], I:['Drug X','match']}, action:'Dùng Drug X cho HFrEF.'}
  ]
};
// HẾT KHỐI DATA
</script></html>"""


def _xml(ket_luan: str) -> bytes:
    return ("<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>11111111</PMID><Article>"
            "<ArticleTitle>Drug X in heart failure with reduced ejection fraction</ArticleTitle><Abstract>"
            f"<AbstractText Label=\"CONCLUSIONS\">{ket_luan}</AbstractText></Abstract></Article>"
            "</MedlineCitation></PubmedArticle></PubmedArticleSet>").encode()


def test_main_nguon_ma_thoat_0_1_2(tmp_path, monkeypatch):
    dash = tmp_path / "WebDashboard_Test_20260925.html"
    dash.write_text(DASH_HTML, encoding="utf-8", newline="\n")
    monkeypatch.setattr(M, "_toan_van", lambda pm: None)
    monkeypatch.setattr(M, "_tai_url", lambda url: _xml("Drug X reduced mortality."))
    assert M.main([str(dash), "--nguon"]) == 0
    monkeypatch.setattr(M, "_tai_url", lambda url: _xml("Drug X did not reduce mortality."))
    assert M.main([str(dash), "--nguon"]) == 1

    def hong(url):
        raise OSError("mất mạng")
    monkeypatch.setattr(M, "_tai_url", hong)
    assert M.main([str(dash), "--nguon"]) == 2                  # không tải được ⇒ không bao giờ 0
    ban_doc = tmp_path / "bd.html"
    ban_doc.write_text("<p>Dùng X.</p>", encoding="utf-8", newline="\n")
    assert M.main([str(dash), "--nguon", "--ban-doc", str(ban_doc)]) == 2   # K3 sạch + K1/K4 mù ⇒ 2


def test_bo_vang_co_pico_chua_nhan_la_chua_do_co_nhan_thi_dem_bao_dong_gia(tmp_path, monkeypatch):
    dash = tmp_path / "WebDashboard_Test_20260925.html"
    dash.write_text(DASH_HTML, encoding="utf-8", newline="\n")
    dich = tmp_path / "bo-vang.json"
    assert M.main([str(dash), "--ung-vien-bo-vang", "--dich", str(dich)]) == 0
    d = json.loads(dich.read_text(encoding="utf-8"))
    assert d["muc"][0]["pico"]["P"][0] == "HFrEF" and "cach_chon" not in d
    assert M.main(["--do-bo-vang", "--dich", str(dich)]) == 2      # chưa có nhãn ⇒ chưa đo
    d["muc"][0]["nhan_bac_si"]["dung_chieu"] = True
    dich.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8", newline="\n")
    monkeypatch.setattr(M, "_tai_url", lambda url: _xml("Drug X did not reduce mortality."))
    rc, dong = M.danh_gia_bo_vang(dich)
    assert rc == 0 and any("báo động giả 1/1" in x for x in dong)


def test_lam_giau_khi_mang_hong_thi_khong_ghi(tmp_path, monkeypatch):
    dash = tmp_path / "WebDashboard_Test_20260925.html"
    dash.write_text(DASH_HTML, encoding="utf-8", newline="\n")

    def hong(url):
        raise OSError("mất mạng")
    monkeypatch.setattr(M, "_tai_url", hong)
    dich = tmp_path / "bo-vang.json"
    assert M.main([str(dash), "--ung-vien-bo-vang", "--lam-giau", "--dich", str(dich)]) == 2
    assert not dich.exists()
