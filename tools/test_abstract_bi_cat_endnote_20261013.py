# -*- coding: utf-8 -*-
"""Abstract Europe PMC bị cắt ở dấu «<» (13/10/2026) — `nap_endnote_chu_de._bo_the_html` + `sua_abstract_bi_cat_endnote.py`.

Lỗi: `_bo_the_html` cũ dùng `<[^>]+>` ⇒ «target systolic level of <140 mm Hg … <h4>Results</h4>» còn «target systolic level
of Results». Ngoại tuyến hoàn toàn: văn bản fixture TỰ SOẠN theo đúng khuôn Europe PMC/PubMed (không chép abstract thật),
EndNote là đối tượng giả, sao lưu là hàm giả, nguồn đối chiếu là hàm giả.
"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap(rel: str, ten: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / rel)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


N = _nap("tools/nap_endnote_chu_de.py", "_nap_abs_cat")
S = _nap("tools/sua_abstract_bi_cat_endnote.py", "_sua_abs_cat")
T = S.T


def _cu(s: str) -> str:
    """Bộ lọc CŨ (trước 13/10) — dựng lại đúng lỗi để làm dữ liệu «đã bị cắt»."""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()


# Khuôn Europe PMC: tiêu đề mục là <h4>, «<» trong chữ KHÔNG mã hoá. Khuôn PubMed (phan_tich_pubmed_xml): «NHÃN: …» mỗi dòng.
EPMC = ("<h4>Background</h4>Whether fast lowering of pressure helps is unclear.<h4>Methods</h4>Patients were assigned to a "
        "target of <140 mm Hg within 1 hour or a target of <180 mm Hg. Outcome was disability at 90 days."
        "<h4>Results</h4>Among 2000 patients, events were 52.0% vs 55.6% (P=0.06).<h4>Conclusions</h4>No clear benefit.")
PUBMED = ("BACKGROUND: Whether fast lowering of pressure helps is unclear.\nMETHODS: Patients were assigned to a target of "
          "<140 mm Hg within 1 hour or a target of <180 mm Hg. Outcome was disability at 90 days.\nRESULTS: Among 2000 "
          "patients, events were 52.0% vs 55.6% (P=0.06).\nCONCLUSIONS: No clear benefit.")


# ── 1. bộ lọc thẻ đã vá ────────────────────────────────────────────────────────────────────────────────────────────

def test_bo_the_giu_dau_nho_hon_la_chu():
    ra = N._bo_the_html(EPMC)
    assert _cu(EPMC).startswith("Background Whether") and "target of Results" in _cu(EPMC), "fixture phải tái hiện lỗi"
    assert "target of <140 mm Hg within 1 hour or a target of <180 mm Hg." in ra
    assert "Results Among 2000 patients" in ra and "<h4>" not in ra and "</h4>" not in ra


@pytest.mark.parametrize("chu", ["P < .001]", "p<0.05", "<0·05", "< 0.05", "x <= 3", "(< three months)",
                                 "eGFR 25 to <50 ml", "P < .001; diastolic > 3"])
def test_bo_the_khong_dung_chu(chu):
    s = f"<h4>Results</h4>Before {chu} after.<h4>Conclusions</h4>End."
    assert N._bo_the_html(s) == re.sub(r"\s+", " ", f"Results Before {chu} after. Conclusions End.")


def test_bo_the_that_va_de_nguyen_the_la():
    assert N._bo_the_html("HbA<sub>1c</sub> and 10<sup>9</sup>/L in <i>H. pylori</i>, <b>bold</b><br/>x<BR>y") == \
        "HbA 1c and 10 9 /L in H. pylori , bold x y"
    assert N._bo_the_html('<H4 class="x">Methods</H4>ok') == "Methods ok"
    assert N._bo_the_html("a <foo> b <b-blocker> c") == "a <foo> b <b-blocker> c", "thẻ lạ để nguyên — không xoá chữ"


def test_giai_ma_thuc_the_va_the_ma_hoa_kep():
    assert N._bo_the_html("target &lt;140 mm Hg &amp; P &gt; 0.05") == "target <140 mm Hg & P > 0.05"
    assert N._bo_the_html("Management of &lt;i&gt;Helicobacter pylori&lt;/i&gt; infection") == \
        "Management of Helicobacter pylori infection"
    assert N._bo_the_html("HbA&lt;sub&gt;1c&lt;/sub&gt; &lt;7%") == "HbA 1c <7%"


def test_phan_tich_europepmc_giu_nguyen_abstract():
    js = {"resultList": {"result": [{"pmid": "11111111", "title": "Target &lt;140 in <i>ICH</i>", "abstractText": EPMC}]}}
    m = N.phan_tich_europepmc(js)["11111111"]
    assert m["tieu_de"] == "Target <140 in ICH"
    assert "<140 mm Hg within 1 hour" in m["tom_tat"] and "Among 2000 patients" in m["tom_tat"]


# ── 2. phân loại abstract trong EndNote so với bản đối chiếu ───────────────────────────────────────────────────────

def test_phan_loai_bi_cat_dung_dau_van():
    kq = S.phan_loai(_cu(EPMC), PUBMED)
    assert kq["loai"] == "bi_cat" and kq["thieu"] > 50
    assert kq["doan"][0].startswith("<140 mm Hg within 1 hour")


def test_phan_loai_khop_khi_chi_khac_khuon():
    assert S.phan_loai(N._bo_the_html(EPMC), PUBMED) == {"loai": "khop"}, "nhãn HOA vs tiêu đề thường, xuống dòng"
    assert S.phan_loai(PUBMED, PUBMED) == {"loai": "khop"}
    assert S.phan_loai("HbA 1c was 7 mmol/mol", "HbA1c was 7 mmol/mol") == {"loai": "khop"}, "Europe PMC tách <sub>"
    khong_nhan = N._bo_the_html(re.sub(r"<h4>.*?</h4>", " ", EPMC))
    assert S.phan_loai(khong_nhan, PUBMED) == {"loai": "khop"}, "thiếu riêng NHÃN mục không phải thiếu nội dung"


def test_phan_loai_thuc_the():
    assert S.phan_loai(N._bo_the_html(EPMC).replace("<140", "&lt;140"), PUBMED)["loai"] == "thuc_the"


def test_phan_loai_truot_trai_qua_chu_lap():
    """Đo 13/10: «short-term (< three months) and long-term (> three months)» — phép gióng trượt đoạn thiếu qua «term»."""
    epmc = ("<h4>Aims</h4>We studied short-term (< three months) and long-term (> three months) dynamics of the drug."
            "<h4>Results</h4>Done.")
    pm = "AIMS: We studied short-term (< three months) and long-term (> three months) dynamics of the drug.\nRESULTS: Done."
    assert S.phan_loai(_cu(epmc), pm)["loai"] == "bi_cat"


def test_phan_loai_mot_doan_bi_tach_lam_hai():
    """Đo 13/10: «(<25 kg/m<sup>2</sup>) ( p < 0.001)» — chữ «2» còn giữ nằm giữa hai đoạn thiếu thật."""
    epmc = ("<h4>Results</h4>Higher BMI (≥25 kg/m<sup>2</sup>) raised risk compared with lower BMI (<25 kg/m<sup>2</sup>) "
            "(<i>p</i> < 0.001).<h4>Conclusion</h4>Obesity matters.")
    pm = ("RESULTS: Higher BMI (≥25 kg/m2) raised risk compared with lower BMI (<25 kg/m2) (p < 0.001).\n"
          "CONCLUSION: Obesity matters.")
    assert S.phan_loai(_cu(epmc), pm)["loai"] == "bi_cat"


def test_phan_loai_chu_le_bi_giong_nham_van_la_mot_doan(monkeypatch):
    """Đo 13/10 (3/194 ca thật, vd PMID 42024702): «P <0.001). Bleeding was the predominant …» — difflib gióng chữ «P» còn
    giữ vào «p» của «predominant», tách một đoạn thiếu thành hai; đoạn sau (bắt đầu ở «redominant») tự nó không có khe «<».
    Cách gióng phụ thuộc cả abstract dài nên ÉP đúng cách gióng đó bằng SequenceMatcher giả."""
    pm = "RESULTS: Risk fell (P <0.001). Bleeding was the predominant event.\nCONCLUSIONS: Better."
    en = _cu("<h4>Results</h4>Risk fell (P <0.001). Bleeding was the predominant event.<h4>Conclusions</h4>Better.")
    a = "".join(k for k, _ in S._ky_tu(pm))
    b = "".join(k for k, _ in S._ky_tu(en))
    i_p, i_q, i_c = a.index("fellp") + 4, a.index("predominant"), a.index("conclusions")
    assert b == a[:i_p + 1] + a[i_c:], "fixture: EndNote giữ «P» rồi nhảy tới «Conclusions»"
    ep = [("equal", 0, i_p, 0, i_p), ("delete", i_p, i_q, i_p, i_p), ("equal", i_q, i_q + 1, i_p, i_p + 1),
          ("delete", i_q + 1, i_c, i_p + 1, i_p + 1), ("equal", i_c, len(a), i_p + 1, len(b))]

    class _GiongEp:
        def __init__(self, _junk, x, y, autojunk=True):
            assert "".join(x) == a and "".join(y) == b

        def get_opcodes(self):
            return ep
    monkeypatch.setattr(S.difflib, "SequenceMatcher", _GiongEp)
    kq = S.phan_loai(en, pm)
    assert kq["loai"] == "bi_cat" and kq["doan"] == ["(P <0.001). Bleeding was the predominant event"]


def test_phan_loai_thieu_khong_do_dau_nho_hon_la_khac():
    """Xoá một câu KHÔNG bắt đầu ở «<» (bản khác, bác sĩ sửa) ⇒ khác — không bao giờ tự sửa."""
    bo_cau = PUBMED.replace(" Outcome was disability at 90 days.", "")
    assert S.phan_loai(bo_cau, PUBMED)["loai"] == "khac"
    assert S.phan_loai(PUBMED + " Ghi chú riêng của bác sĩ.", PUBMED)["loai"] == "khac", "EndNote có chữ thừa ⇒ khác"


def test_phan_loai_rong_va_khong_co_ban_doi_chieu():
    assert S.phan_loai("", PUBMED)["loai"] == "rong"
    assert S.phan_loai(S.KHONG_CO_ABS, PUBMED)["loai"] == "rong", "câu giữ chỗ của tom_tat_endnote_vi = trống"
    assert S.phan_loai("", "") == {"loai": "khop"}
    assert S.phan_loai("Có chữ.", "")["loai"] == "khac"


# ── 3. thay đúng phần abstract gốc ─────────────────────────────────────────────────────────────────────────────────

KHOI = f"{T.MO_DAU} Cân nhắc · Chứng cứ: Trung bình\n★ Tiêu đề điểm nhấn\nPMID 11111111 · Toàn văn: CHƯA có\n{T.CHAN}"


def test_thay_goc_giu_nguyen_khoi_tieng_viet():
    cu = T.ghep_abstract(_cu(EPMC), KHOI).replace("\n", "\r")      # EndNote lưu xuống dòng thành \r
    moi = S.thay_goc(cu, PUBMED)
    assert moi.startswith(KHOI + "\n\n" + T.PHAN_CACH + "\n") and moi.endswith(PUBMED)
    assert T.tach_goc(moi) == PUBMED


def test_thay_goc_khong_khoi_va_mat_phan_cach():
    assert S.thay_goc(_cu(EPMC), PUBMED) == PUBMED
    assert S.thay_goc(f"{T.MO_DAU} khối hỏng không có dấu phân cách", PUBMED) is None


# ── 4. đo và sửa trên EndNote giả ──────────────────────────────────────────────────────────────────────────────────

class _EndNoteGia:
    def __init__(self, truong: dict[str, str], khop: dict[str, list[str]], doc_hong: frozenset = frozenset()):
        self.truong = dict(truong)
        self.khop = khop
        self.doc_hong = doc_hong
        self.nhat_ky: list[str] = []
        self.thu_vien = Path("/khong-ton-tai/tv.enl")

    def tim_khop(self, gia_tri, truong):
        assert truong == "Accession Number"
        return {v: self.khop[v] for v in gia_tri if v in self.khop}

    def doc_truong(self, ids, truong):
        if truong == "Notes":
            return {m: "Nạp tự động bởi EBM Copilot … Metadata: Europe PMC." for m in ids}
        self.nhat_ky.append("doc")
        return {m: self.truong.get(m, "") for m in ids if m not in self.doc_hong}

    def ghi_truong(self, cap, truong):
        assert truong == "Abstract"
        for m, gt in cap:
            self.truong[m] = gt.replace("\n", "\r")
            self.nhat_ky.append(f"ghi:{m}")
        return {m: "" for m, _ in cap}


def _meta(**pmid_abs):
    return lambda pmids: {p: {"pmid": p, "tom_tat": v} for p, v in pmid_abs.items() if p in pmids}


def _en():
    return _EndNoteGia(
        {"r1": T.ghep_abstract(_cu(EPMC), KHOI),                 # bị cắt, có khối tiếng Việt
         "r2": PUBMED,                                          # lành
         "r3": PUBMED.replace(" Outcome was disability at 90 days.", ""),   # khác — bác sĩ sửa tay
         "r4": N._bo_the_html(EPMC).replace("<140", "&lt;140"),   # còn mã HTML
         "r5": _cu(EPMC)},                                      # bản trùng PMID 1, bị cắt, chưa có khối tiếng Việt
        {"1": ["r1", "r5"], "2": ["r2"], "3": ["r3"], "4": ["r4"]})


def _lay():
    return _meta(**{"1": PUBMED, "2": PUBMED, "3": PUBMED, "4": PUBMED})


def test_chay_kho_dem_dung_khong_ghi_khong_sao_luu():
    en = _en()
    bc = S.do_va_sua(en, ["1", "2", "3", "4", "9"], ap_dung=False, lay_pm=_lay(),
                     sao_luu=lambda: pytest.fail("chạy khô không sao lưu"))
    assert bc["dem"] == {"khop": 1, "bi_cat": 2, "thuc_the": 1, "khac": 1, "rong": 0, "khong_do": 0}
    assert bc["se_sua"] == 3 and bc["khong_co_ban_ghi"] == ["9"] and bc["doi_chieu"] == "PubMed efetch"
    assert not [x for x in en.nhat_ky if x.startswith("ghi")]
    assert S.ma_thoat(bc, False) == S.MA_CON_VIEC


def test_ap_dung_sao_luu_truoc_chi_sua_ban_dung_dau_van_giu_khoi_viet():
    en = _en()
    r3_truoc = en.truong["r3"]
    thu_tu: list[str] = []
    bc = S.do_va_sua(en, ["1", "2", "3", "4"], ap_dung=True, lay_pm=_lay(),
                     sao_luu=lambda: (thu_tu.append(len(en.nhat_ky)), "/sao-luu/x")[1])
    ghi = [x for x in en.nhat_ky if x.startswith("ghi")]
    assert sorted(ghi) == ["ghi:r1", "ghi:r4", "ghi:r5"] and bc["da_sua"] == 3 and not bc["loi"]
    assert thu_tu and not any(x.startswith("ghi") for x in en.nhat_ky[:thu_tu[0]]), "sao lưu TRƯỚC mọi lần ghi"
    assert bc["sao_luu"] == "/sao-luu/x"
    r1 = T.chuan_dong(en.truong["r1"])
    assert r1.startswith(KHOI + "\n\n" + T.PHAN_CACH) and T.tach_goc(r1) == PUBMED, "khối tiếng Việt giữ nguyên"
    assert en.truong["r3"] == r3_truoc, "bản «khác» KHÔNG bao giờ bị sửa"
    assert T.chuan_dong(en.truong["r5"]) == PUBMED
    bc2 = S.do_va_sua(en, ["1", "2", "3", "4"], ap_dung=True, lay_pm=_lay(),
                      sao_luu=lambda: pytest.fail("không còn gì để sửa thì không sao lưu"))
    assert bc2["dem"]["bi_cat"] == 0 and bc2["dem"]["thuc_the"] == 0 and bc2["dem"]["khop"] == 4


def test_sao_luu_hong_thi_khong_ghi_gi():
    en = _en()

    def hong():
        raise OSError("không thấy sdb.eni")
    with pytest.raises(OSError):
        S.do_va_sua(en, ["1"], ap_dung=True, lay_pm=_lay(), sao_luu=hong)
    assert not [x for x in en.nhat_ky if x.startswith("ghi")]


def test_truong_doi_tu_luc_do_thi_bo_qua():
    en = _en()
    goc_doc = en.doc_truong

    def doc(ids, truong):
        ra = goc_doc(ids, truong)
        if truong == "Abstract" and en.nhat_ky.count("doc") >= 2 and "r1" in ra:
            ra["r1"] = ra["r1"] + " Bác sĩ vừa gõ thêm."   # lần đọc lại ngay trước khi ghi
        return ra
    en.doc_truong = doc
    bc = S.do_va_sua(en, ["1"], ap_dung=True, lay_pm=_lay(), sao_luu=lambda: "/sao-luu/x")
    assert "ghi:r1" not in en.nhat_ky and "ghi:r5" in en.nhat_ky
    assert any("đổi từ lúc đo" in x for x in bc["loi"]) and S.ma_thoat(bc, True) == S.MA_CON_VIEC


def test_khong_do_duoc_khong_bao_gio_la_khop():
    en = _en()
    en.doc_hong = frozenset({"r2"})
    en.truong["r3"] = f"{T.MO_DAU} khối mất dấu phân cách"
    bc = S.do_va_sua(en, ["2", "3", "4"], ap_dung=False, lay_pm=_meta(**{"3": PUBMED}))
    ly_do = sorted(x["ly_do"] for x in bc["chi_tiet"] if x["loai"] == "khong_do")
    assert bc["dem"]["khong_do"] == 3 and bc["dem"]["khop"] == 0
    assert any("không đọc được" in x for x in ly_do) and any("không trả bản ghi" in x for x in ly_do)
    assert any("mất dấu phân cách" in x for x in ly_do)
    assert S.ma_thoat(bc, False) == S.MA_KHONG_DO


def test_ncbi_chan_mac_dinh_nem_co_lui_thi_doi_chieu_europepmc():
    def chan(_):
        raise S.N.NcbiChan("chặn")      # lớp của CHÍNH bản module công cụ nạp (N.lay_pubmed thật ném lớp này)
    with pytest.raises(S.N.NcbiChan):
        S.do_va_sua(_en(), ["1"], ap_dung=False, lay_pm=chan)
    bc = S.do_va_sua(_en(), ["1"], ap_dung=False, lay_pm=chan, lay_ep=_lay())
    assert bc["doi_chieu"].startswith("Europe PMC") and bc["dem"]["bi_cat"] == 2


def test_liet_ke_kho_tom_tat_may_can_dung_lai():
    kho = {"PMID 1": {"ket_qua": "từ abstract bị cắt"}, "PMID 2": {"ket_qua": "lành"}}
    bc = S.do_va_sua(_en(), ["1", "2"], ap_dung=False, lay_pm=_lay(), kho_tt=kho)
    assert bc["kho_tom_tat_dung_lai"] == ["1"]


def test_doc_kho_tom_tat(tmp_path):
    assert S.doc_kho_tom_tat(None) == {} and S.doc_kho_tom_tat(tmp_path) == {}
    (tmp_path / S.TEP_KHO_TOM_TAT).write_text('{"muc": {"PMID 1": {}}}', encoding="utf-8")
    assert S.doc_kho_tom_tat(tmp_path) == {"PMID 1": {}}
    (tmp_path / S.TEP_KHO_TOM_TAT).write_text('{"khac": 1}', encoding="utf-8")
    with pytest.raises(ValueError):
        S.doc_kho_tom_tat(tmp_path)


def test_ma_thoat_va_tham_so(monkeypatch, capsys):
    sach = {"loi": [], "se_sua": 0, "dem": {"khong_do": 0}}
    assert S.ma_thoat(sach, False) == S.MA_OK
    assert S.ma_thoat(dict(sach, se_sua=2), True) == S.MA_OK, "áp dụng xong, không lỗi"
    assert S.main(["--pmid", "1", "--file", "x.html"]) == S.MA_THAM_SO
    assert S.main(["--pmid", "abc"]) == S.MA_THAM_SO
    monkeypatch.setattr(S.N, "doc_cau_hinh", lambda: {"thu_vien": "/khong-ton-tai/tv.enl", "ung_dung": "EndNote 2025"})
    assert S.main(["--pmid", "23713578"]) == S.MA_KHONG_DO, "dưới pytest không bao giờ điều khiển EndNote thật"
    assert "Không đo được" in capsys.readouterr().out
