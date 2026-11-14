"""Vá lớp kiểm ngữ nghĩa K1–K4 + thêm K3b/K4b (14/11/2026, lượt c) — ngoại tuyến.

Mỗi lỗ hổng đo được ở quality/eval/kiem-cheo-ngu-nghia/do-nhay-dot-bien-20261114 có test riêng:
  (a) chuan_hoa coi mọi «<…>» là thẻ HTML  ·  (b) K1/K4 đọc cả dòng tác giả/cơ quan  ·  (c) từ vựng K1/K4 + bộ lọc kết cục phụ
  (d) K3 so khớp cấp tài liệu  ·  K3b (nguồn khuyến cáo có điều kiện mà mục không giữ)  ·  K4b (mục nói KHÔNG làm khi nguồn ủng hộ)
Văn bản nguồn là tóm tắt TỰ DỰNG theo khuôn efetch dạng text (không trích nguyên văn bài báo nào). Mọi phép vẫn ở mức CẢNH BÁO.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

_THU_MUC = Path(__file__).resolve().parent


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, _THU_MUC / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


K3 = _nap("kiem_cheo_ngu_nghia_c", "kiem_cheo_ngu_nghia.py")
Q = _nap("kiem_quan_the_chieu_c", "kiem_quan_the_chieu.py")
DN = _nap("do_nhay_kiem_ngu_nghia_c", "do_nhay_kiem_ngu_nghia.py")


def _efetch(tieu_de: str, than: str, tac_gia: str = "Author A(1), Author B(2), Author C(1).",
            co_quan: str = "(1)Department of Medicine, Example University Hospital.") -> str:
    return (f"1. Fake J Med. 2026 Jan;1(1):1995-2008. doi: 10.0000/fake.\n\n{tieu_de}\n\n{tac_gia}\n\n"
            f"Author information:\n{co_quan}\n\n{than}\n\nCopyright © 2026 Example.\n\n"
            "Conflict of interest statement: Author A reports fees from Children's Health Fund.\n\n"
            "DOI: 10.0000/fake\nPMID: 900001")


# ───────────────────────── (a) chuẩn hoá: «<» so sánh không phải thẻ HTML ─────────────────────────

def test_chuan_hoa_html_bo_the_that_giu_dau_so_sanh():
    assert K3.chuan_hoa("<p>Giảm liều <b>khi</b> eGFR &lt;30</p><!-- ghi chú --><br/>") == "giảm liều khi egfr <30"
    assert K3.chuan_hoa("eGFR <30 và >15 thì giảm liều") == "egfr <30 và >15 thì giảm liều"   # chuỗi DATA không mã hoá
    assert K3.chuan_hoa('<td class="x">A</td><!DOCTYPE html>') == "a"


def test_chuan_hoa_nguon_van_ban_thuan_giu_chu_giua_hai_dau():
    raw = "Risk was < 3 % in arm A; drug Z is not recommended when > 5 % in arm B."
    assert "drug z is not recommended" in Q.chuan_hoa_nguon(raw)
    assert "drug z" not in K3.chuan_hoa(raw.replace("< 3", "<x"))      # dạng «<chữ … >» trong HTML vẫn là thẻ
    assert Q.chuan_hoa_nguon("Drug <i>X</i> reduced 10<sup>3</sup> events.") == "drug x reduced 10 3 events."


def test_k4_thay_cau_nam_giua_dau_so_sanh():
    src = _efetch("Drug Z in adults.", "RESULTS: LNM risk < 3 % overall. CONCLUSIONS: Drug Z is not recommended "
                  "for routine use; benefit was > 5 % only in a subgroup.")
    r = Q.kiem_muc({"id": "X", "decision": "apply", "action": "Dùng thuốc Z.", "pmid": "1"}, src)
    assert r["k4"]["muc"] == "can_doc" and any("not recommended" in c for c in r["k4"]["cau_nguon"])


# ───────────────────────── (b) thân tóm tắt: bỏ trích dẫn, tác giả, cơ quan ─────────────────────────

def test_than_nguon_bo_dong_tac_gia_co_quan_va_dinh_danh():
    src = _efetch("Drug X in adults with heart failure.", "BACKGROUND: x.\nCONCLUSIONS: Drug X reduced death.",
                  co_quan="(1)Department of Paediatrics, Example Children's Hospital.")
    than = Q.than_nguon(src)
    assert "Drug X in adults" in than and "CONCLUSIONS" in than
    for chu in ("Children's Hospital", "Paediatrics", "Author A", "PMID", "1995-2008", "Copyright", "Conflict"):
        assert chu not in than


def test_than_nguon_bo_tac_gia_to_chuc_theo_vi_tri():
    # tác giả là TỔ CHỨC không nhận được qua khuôn tên — chỉ vị trí (đoạn ngay sau tiêu đề) mới bỏ được
    src = _efetch("Guideline on drug X in adults.", "RECOMMENDATIONS: Drug X is recommended for adults.",
                  tac_gia="American Academy of Pediatrics Committee on Drugs.")
    than = Q.than_nguon(src)
    assert "Pediatrics" not in than and "Drug X is recommended" in than
    r = Q.kiem_muc({"id": "X", "decision": "apply", "population": "Người lớn", "action": "a", "pmid": "1"}, src)
    assert r["k1_cap"] == [{"ve_muc": "người lớn", "ve_nguon": "người lớn", "muc": "khop"}]


def test_than_nguon_khuon_retracted_bo_danh_sach_tac_gia_theo_khuon_ten():
    src = ("1. RETRACTED ARTICLE\n\nFake J. 2025 Oct;41(10):1-9. doi: 10.0000/x.\n\nGuideline on drug Q.\n\n"
           "Nguyen Children A(1), Tran Pediatric B(2), Le C(3), Pham D(1).\n\nAuthor information:\n(1)Hospital.\n\n"
           "Retraction in\n    Fake J. 2025.\n\nDrug Q is recommended in adults.\n\nPMID: 900004")
    than = Q.than_nguon(src)
    assert "Nguyen Children" not in than and "Drug Q is recommended" in than and "Hospital" not in than


def test_than_nguon_khong_tac_gia_va_bai_tieng_duc():
    khong_tac_gia = ("1. Lancet. 1999 Jan 2;353(9146):9-13.\n\nTrial of drug Y.\n\n[No authors listed]\n\n"
                     "BACKGROUND: Drug Y improved survival.\n\nPMID: 900002")
    assert "Drug Y improved survival" in Q.than_nguon(khong_tac_gia)      # «[No authors listed]» là dòng tác giả ⇒ giữ thân
    duc = ("1. Nervenarzt. 2026 Jan;97(1):1-9.\n\n[Treatment of X].\n\n[Article in German]\n\n"
           "Schmidt A(1), Weber B(2), Fischer C(3), Wagner D(1).\n\nAuthor information:\n(1)Klinik.\n\n"
           "Drug W reduced symptoms in children.\n\nPMID: 900003")
    than = Q.than_nguon(duc)
    assert "Drug W reduced symptoms" in than and "Schmidt" not in than and "Klinik" not in than


def test_than_nguon_giu_nguyen_van_ban_khong_theo_khuon_efetch():
    assert Q.than_nguon("Tiêu đề. Adults with HFrEF were enrolled.") == "Tiêu đề. Adults with HFrEF were enrolled."
    assert Q.than_nguon("") == ""


def test_k1_khong_doc_children_hospital_o_dong_co_quan():
    src = _efetch("Drug X in adults.", "METHODS: We enrolled adults with asthma.\nCONCLUSIONS: Drug X reduced attacks.",
                  co_quan="(1)Example Children's Hospital, Department of Pediatrics.")
    r = Q.kiem_muc({"id": "X", "decision": "apply", "population": "Trẻ em hen", "action": "a", "pmid": "1"}, src)
    assert r["k1_cap"] == [{"ve_muc": "trẻ em", "ve_nguon": "người lớn", "muc": "can_doc"}]   # trước đây: ✓ (trấn an sai)


def test_k2_khong_khop_so_trang_dong_trich_dan():
    src = _efetch("Drug X.", "METHODS: We randomized 4304 adults.\nCONCLUSIONS: Drug X reduced events.")
    r = Q.kiem_muc({"id": "X", "decision": "apply", "population": "Người lớn (n=1995)", "action": "a", "pmid": "1"}, src)
    assert r["k2_co_mau"][0]["muc"] == "can_doc"                  # «1995» chỉ có ở số trang 1995-2008 của dòng trích dẫn


# ───────────────────────── (c) từ vựng K1 + K4, bộ lọc kết cục phụ ─────────────────────────

def test_k1_tu_vung_moi_o_muc():
    ng = Q.chuan_hoa_nguon("adults with type 2 diabetes and preserved ejection fraction were enrolled")
    for viet, ve in (("bệnh nhi", "trẻ em"), ("trẻ vị thành niên", "trẻ em"), ("ĐTĐ1", "ĐTĐ típ 1"),
                     ("suy tim PSTM giảm", "HFrEF")):
        kq = Q.kiem_cap(Q.chuan_hoa(viet), ng)
        assert {"ve_muc": ve, "ve_nguon": next(x["ve_nguon"] for x in kq if x["ve_muc"] == ve), "muc": "can_doc"} in kq, viet
    assert Q.kiem_cap(Q.chuan_hoa("người trưởng thành"), ng) == [{"ve_muc": "người lớn", "ve_nguon": "người lớn",
                                                                   "muc": "khop"}]
    assert Q.kiem_cap(Q.chuan_hoa("suy tim phân suất tống máu còn bảo tồn"), ng)[0]["muc"] == "khop"


def test_k1_nguon_khong_doc_child_pugh_la_tre_em():
    kq = Q.kiem_cap(Q.chuan_hoa("người lớn xơ gan"), Q.chuan_hoa_nguon("patients with child-pugh class b cirrhosis"))
    assert kq == [{"ve_muc": "người lớn", "ve_nguon": "người lớn", "muc": "chua_kiem"}]   # không thành «nguồn chỉ nêu trẻ em»
    kq2 = Q.kiem_cap(Q.chuan_hoa("người lớn"), Q.chuan_hoa_nguon("adolescents aged 12 to 17 years"))
    assert kq2[0]["muc"] == "can_doc"


def test_k4_dang_phu_dinh_moi():
    for cau in ("Drug X does not reduce mortality.", "Drug X was not effective in this population.",
                "Treatment did not result in a lower rate of death.", "Mortality was not lower with drug X.",
                "Drug X should not be considered for routine use.", "Drug X was not non-inferior to drug Y.",
                "Drug X did not attenuate decline.", "Drug X were not superior to placebo."):
        assert Q.kiem_chieu(Q.chuan_hoa_nguon(cau)), cau


def test_k4_menh_de_gia_dinh_khong_phai_ket_luan_nguoc_chieu():
    for cau in ("If a liberal policy does not improve outcomes, a restrictive approach is reasonable.",
                "Patients in whom education is not effective should receive preventive treatment.",
                "Psychotherapy was recommended when CBT was not effective."):
        bao, bo = Q.kiem_chieu_chi_tiet(Q.chuan_hoa_nguon(cau))
        assert bao == [] and len(bo) == 1, cau
    # «when compared» không phải điều kiện; «not recommended» (luôn báo) thì không bao giờ bỏ qua
    assert Q.kiem_chieu(Q.chuan_hoa_nguon("When compared with placebo, drug X did not reduce events."))
    assert Q.kiem_chieu(Q.chuan_hoa_nguon("If eGFR is below 20, drug X is not recommended."))


def test_k4_bo_loc_ket_cuc_phu_khong_an_secondary_analysis():
    assert Q.kiem_chieu(Q.chuan_hoa_nguon("In this secondary analysis, drug X did not reduce the risk of stroke."))
    assert Q.kiem_chieu(Q.chuan_hoa_nguon("For secondary prevention, drug X did not reduce events."))
    bao, bo = Q.kiem_chieu_chi_tiet(Q.chuan_hoa_nguon("There was no significant difference in secondary outcomes."))
    assert bao == [] and len(bo) == 1                             # kết cục phụ thật vẫn bỏ qua


# ───────────────────────── (d) K3 so theo TỪNG MỤC ─────────────────────────

DATA_K3 = {
    "summary": {"conclusion": "x", "doNow": [], "dontDo": [], "redFlags": []},
    "items": [
        {"id": "ITEM-01", "title": "Thuốc X ở bệnh thận mạn", "decision": "apply",
         "action": "Dùng thuốc X khi eGFR ≥ 30 ml/phút."},
        {"id": "ITEM-02", "title": "Thuốc Z trong suy tim", "decision": "apply",
         "action": "Giảm liều thuốc Z khi eGFR ≥ 30 ml/phút."},
        {"id": "ITEM-03", "title": "Ngắn", "decision": "consider", "action": "c"},
    ],
}


def test_doan_cua_muc_mo_o_tieu_de_dong_o_moc_ke_tiep():
    vb = K3.chuan_hoa("<h2>ITEM-01. Thuốc X ở bệnh thận mạn</h2><p>aaa</p><h2>ITEM-02. Thuốc Z trong suy tim</h2><p>bbb</p>"
                      "<p>ITEM-03</p>")
    doan = K3.doan_cua_muc(vb, K3.neo_muc(DATA_K3))
    (a, b), = doan["ITEM-01"]
    assert "aaa" in vb[a:b] and "bbb" not in vb[a:b]
    assert "ITEM-03" not in doan                                   # định danh đứng một mình không phải đầu mục
    assert [m.start() for m in K3._mau_dinh_danh("ITEM-1").finditer("item-10 x item-1 y")] == [10]
    # bản đọc: trích định danh trong ngoặc «(item-01, item-02)», tiêu đề ở danh sách nguồn ⇒ không cắt đoạn
    bd2 = K3.chuan_hoa("<p>Dùng thuốc X khi eGFR ≥ 30 (ITEM-01, ITEM-02).</p><p>Nguồn: Thuốc X ở bệnh thận mạn.</p>")
    assert K3.co_cau_truc_muc(bd2, K3.neo_muc(DATA_K3)) is False
    # chỉ 1/3 mục có mốc «ITEM-xx. <tiêu đề>» (bản đọc trích nguyên một đầu mục) ⇒ chưa đủ một nửa ⇒ không cắt đoạn
    bd3 = K3.chuan_hoa("<p>Xem ITEM-01. Thuốc X ở bệnh thận mạn — dùng khi eGFR ≥ 30.</p><p>Giảm liều thuốc Z.</p>")
    assert K3.doan_cua_muc(bd3, K3.neo_muc(DATA_K3)) == {}
    # bản đọc: có tiêu đề nhưng KHÔNG in định danh ⇒ không phải sản phẩm theo từng mục ⇒ không cắt đoạn
    bd = K3.chuan_hoa("<p>Nguồn: Thuốc X ở bệnh thận mạn; Thuốc Z trong suy tim.</p><p>Dùng thuốc X khi eGFR ≥ 30.</p>")
    assert K3.co_cau_truc_muc(bd, K3.neo_muc(DATA_K3)) is False and K3.doan_cua_muc(bd, K3.neo_muc(DATA_K3)) == {}


def test_k3_cum_rung_o_muc_a_con_o_muc_b_nay_bi_bat():
    nguon = K3.lay_nguon_dieu_kien(DATA_K3)
    word = ("<h2>ITEM-01. Thuốc X ở bệnh thận mạn</h2><p>Dùng thuốc X.</p>"
            "<h2>ITEM-02. Thuốc Z trong suy tim</h2><p>Giảm liều thuốc Z khi eGFR ≥ 30 ml/phút.</p>")
    cap_tl = K3.doi_chieu(nguon, {"word_html": word})                       # không mốc ⇒ cấp tài liệu như cũ
    theo_muc = K3.doi_chieu(nguon, {"word_html": word}, K3.neo_muc(DATA_K3))
    kq = {d["vi_tri"]: d["ket_qua"]["word_html"] for d in theo_muc["dong"]}
    assert all(d["ket_qua"]["word_html"] == "con" for d in cap_tl["dong"])   # lỗ hổng cũ: ✓ sai
    assert kq == {"ITEM-01.action": "can_doc", "ITEM-02.action": "con"}
    assert {d["vi_tri"]: d["pham_vi"]["word_html"] for d in theo_muc["dong"]} == {"ITEM-01.action": "muc",
                                                                                  "ITEM-02.action": "muc"}


def test_k3_khong_dinh_vi_duoc_muc_thi_so_ca_tai_lieu_va_summary_luon_tai_lieu():
    data = {**DATA_K3, "summary": {"conclusion": "Thêm thuốc X nếu không có chống chỉ định.", "doNow": [], "dontDo": [],
                                   "redFlags": []}}
    nguon = K3.lay_nguon_dieu_kien(data)
    kq = K3.doi_chieu(nguon, {"ban_doc": "<p>Thêm thuốc X nếu không có chống chỉ định. Dùng thuốc X khi eGFR ≥ 30 "
                                         "ml/phút.</p>"}, K3.neo_muc(data))
    pv = {d["vi_tri"]: (d["ket_qua"]["ban_doc"], d["pham_vi"]["ban_doc"]) for d in kq["dong"]}
    assert pv["summary.conclusion"] == ("con", "tai_lieu")
    assert pv["ITEM-01.action"] == ("con", "tai_lieu")             # bản đọc không in tiêu đề/định danh ⇒ không phạt


def test_k3_main_dung_neo(tmp_path):
    dash = tmp_path / "WebDashboard_K3TungMuc_20261114.html"
    dash.write_text("<html><script>\nconst DATA = " + json.dumps(DATA_K3, ensure_ascii=False)
                    + ";\n// HẾT KHỐI DATA\n</script></html>", encoding="utf-8", newline="\n")
    word = tmp_path / "w.html"
    word.write_text("<h2>ITEM-01. Thuốc X ở bệnh thận mạn</h2><p>Dùng thuốc X.</p><h2>ITEM-02. Thuốc Z trong suy tim</h2>"
                    "<p>Giảm liều thuốc Z khi eGFR ≥ 30 ml/phút.</p>", encoding="utf-8", newline="\n")
    assert K3.main([str(dash), "--word-html", str(word)]) == 1


# ───────────────────────── K3b ─────────────────────────

SRC_K3B = _efetch("Guideline on drug X.", "RECOMMENDATIONS: We recommend dapagliflozin in patients with heart failure "
                  "if eGFR is 20 or higher. This guideline should be used with clinical judgment in patients with CKD.")


def _muc(action: str, population: str = "", title: str = "Thuốc ức chế SGLT2") -> dict:
    return {"id": "X", "decision": "apply", "title": title, "population": population, "action": action, "pmid": "1"}


def test_k3b_bat_mat_nguong_cua_cau_khuyen_cao_neo_thuat_ngu():
    ng = Q.chuan_hoa_nguon(Q.than_nguon(SRC_K3B))
    assert Q.kiem_k3b(_muc("Khởi trị dapagliflozin khi eGFR ≥ 20."), ng) == [
        {"loai": "nguong", "dieu_kien": "egfr 20", "muc": "khop", "doan_nguon": Q.kiem_k3b(
            _muc("Khởi trị dapagliflozin khi eGFR ≥ 20."), ng)[0]["doan_nguon"]}]
    mat = Q.kiem_k3b(_muc("Khởi trị dapagliflozin cho suy tim."), ng)
    assert [(x["loai"], x["dieu_kien"], x["muc"]) for x in mat] == [("nguong", "egfr 20", "can_doc")]
    # mục nhắc eGFR với con số KHÁC ⇒ để K1 phán, K3b không báo trùng
    assert Q.kiem_k3b(_muc("Khởi trị dapagliflozin khi eGFR ≥ 25."), ng) == []


def test_k3b_menh_de_dinh_tinh_va_khong_neo_thi_im():
    ng = Q.chuan_hoa_nguon("Recommendations: In patients with asthma, budesonide-formoterol should be used only if "
                           "symptoms persist.")
    co = Q.kiem_k3b(_muc("Dùng budesonide-formoterol khi triệu chứng kéo dài."), ng)
    khong = Q.kiem_k3b(_muc("Dùng budesonide-formoterol hằng ngày."), ng)
    assert [(x["loai"], x["muc"]) for x in co] == [("menh_de", "khop")]
    assert [(x["loai"], x["muc"]) for x in khong] == [("menh_de", "can_doc")]
    assert Q.kiem_k3b(_muc("Dùng salbutamol hằng ngày."), ng) == []        # không chung thuật ngữ ⇒ K3b im
    # câu mô tả phạm vi tài liệu («this guideline… clinical judgment») không phải khuyến cáo
    ng2 = Q.chuan_hoa_nguon("This guideline on dapagliflozin should be used with clinical judgment in patients with CKD.")
    assert Q.kiem_k3b(_muc("Dùng dapagliflozin."), ng2) == []


def test_k3b_tuoi_can_ngu_canh_tuoi_khong_doc_thoi_gian_theo_doi():
    assert Q.trich_nguong_nguon("we recommend statin for adults aged 75 years or older if ldl-c >= 70.") == [
        ("ldl", "70"), ("tuoi", "75")]
    assert Q.trich_nguong_nguon("statin should be continued if follow-up > 3 years.") == []
    assert Q.trich_nguong_nguon("patients with an egfr of 25 to 75 were eligible.") == []   # khoảng = tiêu chuẩn nhận


def test_k3b_den_kiem_muc_va_ma_thoat(tmp_path, capsys):
    dash = tmp_path / "WebDashboard_K3b_20261114.html"
    data = {"summary": {"conclusion": "x", "doNow": [], "dontDo": [], "redFlags": []},
            "items": [{"id": "ITEM-01", "title": "SGLT2i trong suy tim", "pmid": "1", "decision": "apply",
                       "population": "Suy tim", "action": "Khởi trị dapagliflozin cho mọi người suy tim."}]}
    dash.write_text("<html><script>\nconst DATA = " + json.dumps(data, ensure_ascii=False)
                    + ";\n// HẾT KHỐI DATA\n</script></html>", encoding="utf-8", newline="\n")
    nguon = tmp_path / "nguon.json"
    nguon.write_text(json.dumps({"1": SRC_K3B}), encoding="utf-8", newline="\n")
    assert Q.main([str(dash), "--nguon-json", str(nguon)]) == 1          # chỉ K3b 🟠 vẫn là «có mục cần đọc lại»
    out = capsys.readouterr().out
    assert "K3b nguồn khuyến cáo kèm ngưỡng «egfr 20»" in out and "K3b 1" in out


# ───────────────────────── K4b ─────────────────────────

SRC_UNG_HO = _efetch("Drug X for heart failure.", "METHODS: Adults were randomized.\nCONCLUSIONS: Drug X reduced the risk "
                     "of death or hospitalization.")


def test_k4b_muc_khong_lam_khi_nguon_ung_ho():
    ng = Q.chuan_hoa_nguon(Q.than_nguon(SRC_UNG_HO))
    r = Q.kiem_k4b(_muc("KHÔNG khởi trị thuốc X ở suy tim."), ng)
    assert r["muc"] == "can_doc" and "drug x reduced the risk" in r["cau_nguon"][0]
    assert Q.kiem_k4b(_muc("Khởi trị thuốc X ở suy tim."), ng) is None      # mục không phải khuyến cáo phủ định
    # K4 vẫn ✓ (nguồn không có tín hiệu ngược chiều) — chỉ K4b thấy mâu thuẫn
    r_day = Q.kiem_muc(_muc("Tránh dùng thuốc X ở suy tim."), SRC_UNG_HO)
    assert r_day["k4"]["muc"] == "khop" and r_day["k4b"]["muc"] == "can_doc"


def test_k4b_nguon_co_cau_chong_hai_la_cung_chieu_khong_ro_la_chua_kiem():
    chong = Q.chuan_hoa_nguon("Conclusions: Drug X increased the risk of bleeding and should be avoided in older adults.")
    assert Q.kiem_k4b(_muc("Không kê thuốc X cho người cao tuổi."), chong)["muc"] == "khop"
    mo_ta = Q.chuan_hoa_nguon("2024 guidelines for heart failure. These guidelines summarize the evidence.")
    assert Q.kiem_k4b(_muc("Không kê thuốc X."), mo_ta) == {"muc": "chua_kiem", "cau_nguon": []}
    # khuôn USPSTF «benefits and harms» là câu phương pháp, không phải câu chống
    bh = Q.chuan_hoa_nguon("Conclusions: Screening reduced mortality; clinicians should weigh the benefits and harms.")
    assert Q.kiem_k4b(_muc("Không tầm soát thường quy."), bh)["muc"] == "can_doc"


def test_k4b_phu_dinh_kep_va_tu_mo_ta_khong_phai_khuyen_cao_chong():
    for act in ("KHÔNG từ chối SGLT2i chỉ vì eGFR thấp.", "Không ngừng chẹn beta ở COPD.",
                "Không dung nạp NSAID: dùng paracetamol.", "KHÔNG khuyên kiêng sữa/canxi.",
                "Không triệu chứng: theo dõi định kỳ."):
        assert Q.muc_phu_dinh_that(_muc(act)) is False, act
    for act in ("KHÔNG kê benzodiazepine.", "Tránh NSAID ở suy tim.", "Không nên tầm soát PSA ở người ≥ 70 tuổi."):
        assert Q.muc_phu_dinh_that(_muc(act)) is True, act


def test_kiem_dashboard_dem_theo_phep():
    data = {"items": [{"id": "ITEM-01", "title": "t", "pmid": "1", "decision": "apply", "population": "Suy tim",
                       "action": "KHÔNG khởi trị thuốc X."}]}
    kq = Q.kiem_dashboard(data, {"1": SRC_UNG_HO}, False)
    assert kq["dem_theo_phep"]["K4b"]["can_doc"] == 1 and kq["dem_theo_phep"]["K4"]["khop"] == 1
    assert sum(v["can_doc"] for v in kq["dem_theo_phep"].values()) == kq["dem"]["can_doc"]


# ───────────────────────── bộ đo độ nhạy: ánh xạ K3b/K4b ─────────────────────────

def test_do_nhay_cham_k3b_k4b_va_khong_nguon():
    bo = DN.bo_kiem_that()
    it = _muc("Khởi trị dapagliflozin khi eGFR ≥ 20.")
    goc = bo["kiem_muc"](it, SRC_K3B)
    db = {"phep": "K3b", "truong": "k3b", "dich": {}, "muc_dot_bien": _muc("Khởi trị dapagliflozin."),
          "nguon_dot_bien": SRC_K3B}
    assert DN.cham_k124(db, goc, bo) == "bat" and db["phan_duoc"] is True
    assert DN.cham_k124({**db, "muc_dot_bien": it}, goc, bo) == "lot_xanh"        # không đổi gì ⇒ không bắt
    assert DN.cham_k124({**db, "nguon_dot_bien": None}, goc, bo) == "lot_trang"   # không có nguồn ⇒ ⚪
    it4 = _muc("Khởi trị thuốc X ở suy tim.")
    db4 = {"phep": "K4b", "truong": "k4b", "dich": {}, "muc_dot_bien": _muc("KHÔNG khởi trị thuốc X ở suy tim."),
           "nguon_dot_bien": SRC_UNG_HO}
    assert DN.cham_k124(db4, bo["kiem_muc"](it4, SRC_UNG_HO), bo) == "bat"


def test_do_nhay_k3_ban_xuat_that_dung_neo_cua_dashboard():
    bo = DN.bo_kiem_that()
    rec = {"muc": DATA_K3["items"][0], "dashboard": "WebDashboard_X.html", "chi_so": 0, "duong_dan": Path("x")}
    word = DN.gon_dau(DN.chuan_hoa("<h2>ITEM-01. Thuốc X ở bệnh thận mạn</h2><p>Dùng thuốc X khi eGFR ≥ 30 ml/phút.</p>"
                                   "<h2>ITEM-02. Thuốc Z trong suy tim</h2><p>Giảm liều thuốc Z khi eGFR ≥ 30 ml/phút.</p>"))
    dbs = DN.sinh_k3(rec, 1, word, K3.neo_muc(DATA_K3))
    bx = next(d for d in dbs if d["lop"] == "K3_rung_ban_xuat")
    assert bx["neo"] and DN.cham_k3(bx, bo) == "bat"                    # cụm còn ở mục B không còn che mục A
    assert DN.cham_k3({**bx, "neo": None}, bo) == "lot_xanh"            # cùng đột biến, so cấp tài liệu (lỗ hổng cũ)


def test_do_nhay_so_sanh_truoc_sau_va_ten_luot():
    def o(bat, n):
        return {"n": n, "bat": bat}
    cu = {"hat_giong": 1, "tong_hop": {"theo_phep_trong_pham_vi": {"K1": o(5, 10)},
                                       "theo_lop": {"K3_rung_trong_muc": o(0, 8), "K4_muc_dao": o(0, 6)}},
          "doi_chung": {"muc": {"K1": {"n": 10, "bao": 2}}, "dashboard": {"K124": {"n": 3, "bao": 1}}},
          "chan_doan_nguon": {"nguon_bi_cat": 7, "so_nguon": 9}}
    moi = {"tong_hop": {"theo_phep_trong_pham_vi": {"K1": o(9, 10), "K3b": o(1, 8), "K4b": o(2, 6)}, "theo_lop": {}},
           "doi_chung": {"muc": {"K1": {"n": 10, "bao": 1}, "K3b": {"n": 10, "bao": 0}}, "dashboard": {}},
           "chan_doan_nguon": {"nguon_bi_cat": 0, "so_nguon": 9}}
    ss = DN.so_sanh(cu, moi, "cu.json")
    assert ss["phep"]["K1"] == ("5/10 (50%)", "9/10 (90%)")
    assert ss["phep"]["K3b · rụng điều kiện NGAY TRONG MỤC (trước: ngoài phạm vi)"] == ("0/8 (0%)", "1/8 (12%)")
    assert ss["doi_chung"]["K1 · mục có 🟠 / mục có nguồn"] == ("2/10 (20%)", "1/10 (10%)")
    assert ss["doi_chung"]["K3b · mục có 🟠 / mục có nguồn"] == ("—", "0/10 (0%)")
    assert ss["doi_chung"]["Nguồn bị chuẩn hoá xoá chữ"] == ("7/9", "0/9")


# ───────────────────────── bộ vàng: K3b/K4b đo theo nhãn bác sĩ ─────────────────────────

def test_bo_vang_do_k3b_theo_du_dieu_kien_va_k4b_theo_dung_chieu(capsys):
    B = _nap("bo_vang_kiem_ngu_nghia_c", "bo_vang_kiem_ngu_nghia.py")

    def muc(i, dk, chieu):
        return {"id": f"ITEM-{i}", "pmid": str(i), "nhan_bac_si": {"dung_quan_the": True, "dung_chieu": chieu,
                                                                     "du_dieu_kien": dk}}

    def gia(it, _tx):
        i = int(it["id"].split("-")[1])
        return {"k1_nguong": [], "k1_cap": [], "k4": {"muc": "khop"},
                "k3b": [{"muc": "can_doc"}] if i in (1, 2) else [],
                "k4b": {"muc": "can_doc"} if i == 3 else ({"muc": "khop"} if i == 4 else None)}
    bv = {"muc": [muc(1, False, True), muc(2, True, True), muc(3, True, True), muc(4, True, False), muc(5, False, True)]}
    kq = B.do(bv, {str(i): "abc" for i in range(1, 6)}, kiem_muc=gia)
    assert (kq["K3b"]["tp"], kq["K3b"]["fp"], kq["K3b"]["fn"], kq["K3b"]["tn"]) == (1, 1, 1, 2)
    assert (kq["K4b"]["n"], kq["K4b"]["fp"], kq["K4b"]["fn"]) == (2, 1, 1)          # chỉ mục K4b phán (3, 4)
    B.in_do(kq)
    out = capsys.readouterr().out
    assert "K3b (nguồn có điều kiện mà mục không giữ): 5 mục có nhãn" in out and "CHƯA phép kiểm nào bắt" not in out
    # bộ kiểm cũ/giả không có khoá k3b ⇒ CHƯA ĐO (mẫu số 0), không phải 0%
    kq2 = B.do(bv, {str(i): "abc" for i in range(1, 6)},
               kiem_muc=lambda it, tx: {"k1_nguong": [], "k1_cap": [], "k4": {"muc": "khop"}})
    assert kq2["K3b"]["n"] == 0 and kq2["K3b"]["bao_dong_gia"] is None
