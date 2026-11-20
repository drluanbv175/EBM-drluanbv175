# -*- coding: utf-8 -*-
"""Đoạn toàn văn cho bộ kiểm Claude API (prompt 2026-11-20b, 20/11/2026). OFFLINE.

Chốt: (1) CỔNG QUYỀN fail-closed theo từng tệp — PMC CC / bản thảo NIH / Unpaywall gửi được; bản Chrome chỉ khi NXB «cấm»
còn uỷ quyền LÚC GỌI hoặc NXB cho phép TDM; không xác định được ⇒ không gửi; (2) bộ chọn đoạn bỏ tiêu đề bảng, đoạn trùng,
chú giải viết tắt, chọn đúng đoạn khớp mục (kể cả qua bảng Việt→Anh); (3) khoá bộ đệm không đổi khi không có đoạn, đổi khi
có; (4) bước xuất gói ghép đoạn khi phiên bản prompt dùng toàn văn, và KHÔNG ghép tệp không có quyền.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

_TOOLS = Path(__file__).resolve().parent


def _nap(ten, tep):
    sp = importlib.util.spec_from_file_location(ten, _TOOLS / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


A = _nap("_knatv", "kiem_ngu_nghia_api.py")

DT_GIA = SimpleNamespace(
    nxb_cua=lambda doi="", url="", tieu_de="": (("Elsevier", {"ket_luan": "cam"}) if doi.startswith("10.1016/") else (None, None)),
    nxb_tdm_cho_phep=lambda doi="", url="": (("Cambridge University Press", {}) if doi.startswith("10.1017/") else (None, None)),
    uy_quyen_bac_si=lambda nxb: None)


def _tep(tmp_path, ten, noi_dung=""):
    f = tmp_path / ten
    f.write_text(noi_dung, encoding="utf-8")
    return f


@pytest.mark.parametrize("ten, noi_dung, doi, uq, ok", [
    ("PMID-1_PMC9.xml", '<article><license xlink:href="https://creativecommons.org/licenses/by/4.0/"/></article>', "", None, True),
    ("PMID-1_PMC9.xml", '<article><article-id pub-id-type="manuscript">nihms123</article-id></article>', "", None, True),
    ("PMID-1_PMC9.xml", "<article><p>không giấy phép</p></article>", "", None, False),
    # Unpaywall: tên tệp KHÔNG chứng minh giấy phép (rà độc lập 20/11/2026 — 32 tệp _UPW cũ không giấy phép mở)
    ("PMID-1_UPW.html", '<a href="https://creativecommons.org/licenses/by/4.0/">CC BY</a>', "", None, True),
    ("PMID-1_UPW.html", "<p>Copyright and License information</p>", "10.1128/AAC.00251-06", None, False),  # ASM chưa kiểm
    ("PMID-1_UPW.html", "<p>x</p>", "", None, False),
    ("PMID-1_UPW.html", "<p>x</p>", "10.1016/j.x", None, False),                  # NXB cấm, đã rút uỷ quyền
    ("PMID-1_UPW.html", "<p>x</p>", "10.1016/j.x", {"ngay": "2026-10-04"}, True),  # NXB cấm, còn uỷ quyền
    ("PMID-1_CHR.html", "<p>x</p>", "10.1016/j.x", None, False),                  # NXB cấm, không uỷ quyền
    ("PMID-1_CHR.html", "<p>x</p>", "10.1016/j.x", {"ngay": "2026-10-04"}, True),  # còn uỷ quyền
    ("PMID-1_BANIN.pdf", "", "10.1016/j.x", None, False),
    ("PMID-1_CHR.pdf", "", "10.1017/abc", None, False),     # bảng TDM chỉ cho phiên lưu bản sao — không cho gửi API
    ("PMID-1_CHR.html", "<p>x</p>", "10.9999/khong-ro", None, False),              # chưa xác định ⇒ không gửi
    ("PMID-1_CHR.html", "<p>x</p>", "", None, False),                              # không có DOI ⇒ không gửi
    ("PMID-1_WTDM.pdf", "", "", None, False),
])
def test_cong_quyen_gui_toan_van_fail_closed(tmp_path, ten, noi_dung, doi, uq, ok):
    f = _tep(tmp_path, ten, noi_dung)
    assert A.quyen_gui_toan_van(f, doi, DT=DT_GIA, uy_quyen_fn=lambda nxb: uq)[0] is ok


def test_cong_quyen_bang_dieu_khoan_loi_thi_khong_gui(tmp_path):
    hong = SimpleNamespace(nxb_cua=lambda **k: (_ for _ in ()).throw(RuntimeError("x")))
    assert A.quyen_gui_toan_van(_tep(tmp_path, "PMID-1_CHR.html", "x"), "10.1016/j", DT=hong)[0] is False


DOAN = [
    "Recommendations in 2021 version Class a Level b",                                    # tiêu đề bảng < 12 từ
    "BNP, B-type natriuretic peptide; CXR, chest X-ray; ECG, electrocardiogram; HbA1c, glycated haemoglobin; HF, heart failure",
    "The task force was selected by the board and the methods followed the standard procedure for all guideline documents.",
    "Uptitration of foundational therapy at least every 1–2 weeks in patients with HF, guided by blood pressure, potassium "
    "and renal function, is recommended to reach target doses.",
    "Uptitration of foundational therapy at least every 1–2 weeks in patients with HF, guided by blood pressure, potassium "
    "and renal function, is recommended to reach target doses.",                          # trùng
    "Metformin should not be used when eGFR is below 30 mL/min/1.73 m2 because of the risk of lactic acidosis in adults.",
]


def test_chon_doan_chon_dung_doan_va_bo_nhieu():
    it = {"title": "ESC: tăng liều thuốc nền mỗi 1–2 tuần", "population": "Người lớn suy tim",
          "action": "Hẹn tái khám 1–2 tuần, tăng liều nếu huyết áp, kali, creatinine cho phép"}
    d = A.chon_doan(DOAN, it)
    assert d.count("Uptitration") == 1 and "Class a Level b" not in d and "BNP, B-type" not in d
    assert d.index("Uptitration") < (d.index("Metformin") if "Metformin" in d else 10 ** 9)
    assert {"titrat", "blood pressure", "potassium", "week"} <= A.tu_khoa_muc(it)


def test_chon_doan_tran_ky_tu_va_du_phong_cau_khuyen_cao():
    it = {"title": "Metformin khi eGFR thấp", "population": "", "action": "không dùng metformin khi eGFR <30"}
    assert len(A.chon_doan(DOAN * 30, it, tran=200)) <= 200
    it2 = {"title": "Một chủ đề khác hẳn", "population": "", "action": "xyz"}
    assert "is recommended" in A.chon_doan(DOAN, it2) or "should not be used" in A.chon_doan(DOAN, it2)
    assert A.chon_doan([], it) == ""


def test_doan_toan_van_uu_tien_xml_bo_tep_khong_quyen_va_nho(tmp_path):
    cc = '<article><license xlink:href="https://creativecommons.org/licenses/by/4.0/"/><body><p>' + DOAN[5] + "</p></body></article>"
    _tep(tmp_path, "PMID-77_PMC1.xml", cc)
    _tep(tmp_path, "PMID-77_CHR.html", "<p>" + DOAN[3] + "</p>")
    it = {"pmid": "77", "doi": "10.1016/j.x", "title": "metformin eGFR", "population": "", "action": "không dùng metformin"}
    bo_nho = {}
    d, ly = A.doan_toan_van(it, tmp_path, bo_nho=bo_nho, quyen_fn=lambda f, doi: A.quyen_gui_toan_van(f, doi, DT=DT_GIA))
    assert "Metformin" in d and "Creative Commons" in ly and len(bo_nho) == 1
    (tmp_path / "PMID-77_PMC1.xml").unlink()
    d, ly = A.doan_toan_van(it, tmp_path, quyen_fn=lambda f, doi: A.quyen_gui_toan_van(f, doi, DT=DT_GIA))
    assert d == "" and "cấm" in ly                                                   # chỉ còn bản Chrome không uỷ quyền
    assert A.doan_toan_van({"pmid": ""}, tmp_path)[0] == "" and A.doan_toan_van(it, None)[0] == ""


def test_khoa_va_noi_dung_co_doan():
    it = {"title": "a", "population": "b", "action": "c"}
    assert A.khoa_muc(it, "tt", "m", "2026-11-20b") == A.khoa_muc(it, "tt", "m", "2026-11-20b", "")
    assert A.khoa_muc(it, "tt", "m", "2026-11-20b", "đoạn") != A.khoa_muc(it, "tt", "m", "2026-11-20b")
    assert "ĐOẠN TOÀN VĂN" in A.dung_noi_dung(it, "tt", "đoạn x") and "ĐOẠN TOÀN VĂN" not in A.dung_noi_dung(it, "tt")
    assert "2026-11-20b" in A.PHIEN_BAN_TOAN_VAN and "mục tự mâu thuẫn" in A.he_thong("2026-11-20b")
    assert "nguồn mâu thuẫn" in A.he_thong("2026-11-20b")


class _L(RuntimeError):
    pass


def test_buoc_xuat_ghep_doan_khi_phien_ban_dung_toan_van(tmp_path, capsys, monkeypatch):
    kho = tmp_path / "toan_van_oa"
    kho.mkdir()
    cc = '<article><license xlink:href="https://creativecommons.org/licenses/by/4.0/"/><body><p>' + DOAN[5] + "</p></body></article>"
    _tep(kho, "PMID-111_PMC1.xml", cc)
    _tep(kho, "PMID-222_CHR.html", "<p>" + DOAN[3] + "</p>")
    dash = tmp_path / "WebDashboard_X.html"
    dash.write_text("x", encoding="utf-8")
    items = [{"id": "ITEM-01", "decision": "apply", "pmid": "111", "doi": "", "title": "metformin eGFR", "population": "x",
              "action": "không dùng metformin khi eGFR <30"},
             {"id": "ITEM-02", "decision": "apply", "pmid": "222", "doi": "10.1016/j.x", "title": "tăng liều suy tim",
              "population": "x", "action": "tăng liều mỗi 1–2 tuần"}]
    gui = []

    def goi(nd, **kw):
        gui.append((nd, kw))
        return SimpleNamespace(van_ban=json.dumps({"dung_quan_the": True, "dung_chieu": True, "du_dieu_kien": True}),
                               model="m", token_vao=1, token_ra=1, token_cache_doc=0)
    cn = SimpleNamespace(goi=goi, doc_json=json.loads, LoiApi=_L, LoiCucBo=_L, KetQuaHong=_L,
                         ghi_nhat_ky_api=lambda *a, **k: None)
    kqtc = SimpleNamespace(doc_data=lambda d: {"items": items}, _tai_online=lambda pm: f"Tóm tắt {pm}", than_nguon=lambda r: r)
    monkeypatch.setattr(A, "PHIEN_BAN_PROMPT", "2026-11-20b")
    A.kiem_dashboard_api(dash, cau_noi=cn, goi_api=True, online=True, bv={"muc": []}, tep_dem=tmp_path / "d.json",
                         tep_tt=tmp_path / "t.json", tep_dem_bv=tmp_path / "bv.json", kqtc=kqtc, bvk=A._bvk(),
                         quyen_fn=lambda f, doi: A.quyen_gui_toan_van(f, doi, DT=DT_GIA))
    out = capsys.readouterr().out
    assert len(gui) == 2 and all(kw["he_thong"] == A.he_thong("2026-11-20b") for _, kw in gui)
    nd = {g[0].split("Tiêu đề: ")[1].split("\n")[0]: g[0] for g in gui}
    assert "ĐOẠN TOÀN VĂN" in nd["metformin eGFR"] and "Metformin should not" in nd["metformin eGFR"]
    assert "ĐOẠN TOÀN VĂN" not in nd["tăng liều suy tim"]                       # bản Chrome NXB cấm, không uỷ quyền
    assert "kèm đoạn toàn văn 1" in out


BANG_XML = ('<article xmlns:xlink="http://www.w3.org/1999/xlink">'                  # PMC thật luôn khai namespace xlink
            '<license xlink:href="https://creativecommons.org/licenses/by/4.0/"/><body>'
            '<p>For those with type 2 diabetes on insulin, doses should be reduced by 35%–50% during the diet period.</p>'
            '<table-wrap><label>TABLE 5</label><caption><p>Insulin adjustment for individuals with type 1 diabetes.</p></caption>'
            '<table><tr><th>Regimen</th><th>Advice</th></tr><tr><td>Basal insulin alone</td>'
            '<td>It may be necessary to reduce dose by 30%–50% of pre-diet dose. Do not stop insulin; risk of DKA</td></tr>'
            '</table></table-wrap></body></article>')


def test_bang_chi_lay_o_phien_ban_co_bang_va_khong_lap_doan(tmp_path):
    f = _tep(tmp_path, "PMID-5_PMC1.xml", BANG_XML)
    khong = A.boc_doan_toan_van(f)
    co = A.boc_doan_toan_van(f, co_bang=True)
    assert not any("30%–50%" in d for d in khong)                                  # bản b: chỉ <p>
    dong = [d for d in co if "30%–50%" in d]
    assert len(dong) == 1 and dong[0].startswith("[TABLE 5 — Insulin adjustment for individuals with type 1")
    assert sum("Insulin adjustment for individuals" in d for d in co) == 1         # <p> của chú thích không lấy riêng
    assert "2026-11-20c" in A.PHIEN_BAN_CO_BANG and "2026-11-20b" not in A.PHIEN_BAN_CO_BANG
    it = {"pmid": "5", "title": "insulin típ 1", "population": "típ 1", "action": "giảm insulin, không ngừng insulin"}
    q = lambda f, doi: (True, "x")  # noqa: E731
    assert "TABLE 5" in A.doan_toan_van(it, tmp_path, quyen_fn=q, co_bang=True)[0]
    assert "TABLE 5" not in A.doan_toan_van(it, tmp_path, quyen_fn=q)[0]
