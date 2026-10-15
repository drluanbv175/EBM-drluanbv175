# -*- coding: utf-8 -*-
"""Cổng nội dung toàn văn đọc CẤU TRÚC ĐỀ MỤC (15/10/2026 — `audit/nhat-ky/2026-10-15-cong-toan-van-tuong-phi-dai.md`).

Hai lỗi đo được cùng ngày trên `gom_toan_van_dashboard.la_toan_van_html` (cổng dùng chung của tầng Unpaywall, phiên Chrome
`--nhan` — TT-04 — và bộ đếm `bao_phu_cuc_bo`; bản sao trong `verify_dashboard._html_la_toan_van` là cổng BH161):
  • DƯƠNG TÍNH GIẢ — mọi trang ≥ 6000 từ là «toàn văn», xét TRƯỚC mọi dấu: trang Nature Reviews Cardiology KHÔNG có quyền
    (PMID 27811932) chỉ có Key Points · Abstract · «Access options» (thân bài ~575 từ) nhưng danh mục tham khảo kéo tổng lên
    8 743 từ ⇒ phiên Chrome nhận vào kho `PMID-27811932_CHR.html`.
  • ÂM TÍNH GIẢ — CMAJ (PMID 16129869) đặt đề mục Methods · Results · Interpretation, mở bài không đề mục ⇒ chỉ 2 «đề mục IMRaD»
    ⇒ toàn văn thật rơi vào sổ nợ BH161 (báo từ phiên «Cài đặt cho Endnote»).
Mọi fixture là HTML TỔNG HỢP cùng cấu trúc đề mục với trang thật (không chép nội dung bài có bản quyền). Mỗi fixture cô lập ĐÚNG
MỘT lớp phòng thủ, để kiểm đột biến (bỏ cắt References · bỏ dấu Access options · đảo thứ tự kiểm · bỏ «Interpretation» · bỏ loại
trừ tóm tắt · án tường phí tuyệt đối) làm đỏ đúng test của lớp đó. Ngoại tuyến hoàn toàn.
"""
from __future__ import annotations

import importlib.util
import re
import sys
import types
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap(rel: str, ten: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / rel)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


g = _nap("tools/gom_toan_van_dashboard.py", "_gom_tp1015")
vd = _nap("sync/skills/cap-nhat-chung-cu-y-khoa/tools/verify_dashboard.py", "_vd_tp1015")
dtv = _nap("tools/doc_toan_van_co_nguoi.py", "_dtv_tp1015")
P = _nap("tools/phien_uy_quyen_chrome.py", "_puq_tp1015")


def _tu(n: int, goc: str = "lorem") -> str:
    return " ".join(f"{goc}{i % 97}" for i in range(n))


def _muc(the: str, de_muc: str, so_tu: int, goc: str = "noi") -> str:
    return f"<{the}>{de_muc}</{the}><p>{_tu(so_tu, goc)}</p>"


def _trang(*khoi: str, dau: str = "") -> str:
    return f"<!doctype html><html><body>{dau}<article><h1>Synthetic article title</h1>{''.join(khoi)}</article></body></html>"


HAU_BAI_NATURE = (_muc("h2", "References", 8000, "ref") + _muc("h2", "Acknowledgements", 40, "ack")
                  + _muc("h2", "Author information", 20, "au") + _muc("h3", "Authors and Affiliations", 300, "aff")
                  + _muc("h3", "Corresponding author", 20, "co") + _muc("h2", "Rights and permissions", 60, "rp")
                  + _muc("h2", "About this article", 40, "ab") + _muc("h3", "Cite this article", 60, "ci"))
DAU_TRANG_KHONG_QUYEN = (_muc("h2", "Key Points", 120, "kp") + _muc("h2", "Abstract", 250, "abs")
                         + '<h2 class="c-article-section__title" id="access-options">Access options</h2>'
                         + "<p>Subscribe to this journal. Buy article PDF. Prices may be subject to local taxes.</p>"
                         + _muc("h3", "Similar content being viewed by others", 150, "sim"))
IMRAD_THAN = (_muc("h2", "Introduction", 700, "intro") + _muc("h2", "Methods", 900, "meth") + _muc("h2", "Results", 900, "res")
              + _muc("h2", "Discussion", 700, "disc"))
TOM_TAT_CAU_TRUC = ('<section class="abstract"><h2>Abstract</h2>' + _muc("h3", "Background", 70, "a1")
                    + _muc("h3", "Methods", 80, "a2") + _muc("h3", "Results", 90, "a3") + _muc("h3", "Interpretation", 60, "a4")
                    + "</section>")

# ── Fixture (cấu trúc đề mục của trang thật đo 15/10/2026) ───────────────────────────────────────────────────────────────────
# Nature KHÔNG quyền (27811932): tóm tắt + «Access options» + 8 000 từ tham khảo — CẢ HAI lớp (cắt References, tường phí) chặn.
NATURE_KHONG_QUYEN = _trang(DAU_TRANG_KHONG_QUYEN, HAU_BAI_NATURE)
# Chỉ lớp CẮT REFERENCES chặn được (không có đề mục tường phí — vd tường phí là nút bấm, không phải đề mục).
CHI_CAT_REFERENCES = _trang(_muc("h2", "Key Points", 120, "kp"), _muc("h2", "Abstract", 250, "abs"),
                            "<p>Access through your institution · Purchase PDF</p>", HAU_BAI_NATURE)
# Chỉ lớp TƯỜNG PHÍ chặn được: danh mục tham khảo dưới đề mục bộ cắt KHÔNG nhận ra ⇒ thân bài ≥ 6000 từ, chỉ đề mục «Access
# options» (xét TRƯỚC ngưỡng 6000) mới loại được.
CHI_TUONG_PHI = _trang(DAU_TRANG_KHONG_QUYEN, _muc("h2", "Bibliografía", 8000, "ref"))
IMRAD_BINH_THUONG = _trang(TOM_TAT_CAU_TRUC, IMRAD_THAN, _muc("h2", "References", 3000, "ref"))
GUIDELINE_DAI = _trang(*(_muc("h2", f"Recommendation {i}", 700, f"rec{i}") for i in range(1, 11)),
                       _muc("h2", "References", 5000, "ref"))
GUIDELINE_DAI_MOT_MUC = _trang(_muc("h2", "Clinical practice guideline", 7000, "cpg"), _muc("h2", "References", 4000, "ref"))
# Nature CÓ quyền: thanh bên có «Subscribe to this journal» (cả dạng đề mục) — KHÔNG phải dấu tường phí.
NATURE_CO_QUYEN = _trang(IMRAD_THAN, HAU_BAI_NATURE,
                         dau="<aside><h3>Subscribe to this journal</h3><p>Receive 12 print issues and online access</p></aside>")
# SAGE CÓ quyền (40277321 · 42084558 · 42751933): toàn văn đủ IMRaD, menu «View options» vẫn có h4 «Access options».
SAGE_CO_QUYEN = _trang(TOM_TAT_CAU_TRUC, IMRAD_THAN, _muc("h2", "References", 1400, "ref"),
                       "<h2>View Options</h2><h3>View options</h3>" + _muc("h4", "PDF/EPUB", 2, "pdf")
                       + _muc("h4", "Access options", 100, "acc"))
# SAGE KHÔNG quyền (29368949): chỉ thanh công cụ + «Access options» + bài gợi ý.
SAGE_KHONG_QUYEN = _trang(_muc("h4", "Altmetric", 56, "alt"), _muc("h4", "Publications citing this one", 238, "pub"),
                          _muc("h4", "Access options", 163, "acc"), _muc("h2", "Similar articles:", 181, "sim"),
                          _muc("h2", "Sage recommends:", 185, "sage"), _muc("h2", "Sage recommends:", 311, "sage2"))
# CMAJ (16129869): tóm tắt h3 Background/Methods/Results/Interpretation; mở bài KHÔNG đề mục (h2 rỗng); thân bài h2 Methods ·
# Results · Interpretation — chỉ «Interpretation» (≈ Discussion) đưa số nhóm lên 3.
CMAJ = _trang(TOM_TAT_CAU_TRUC, "<h2></h2><p>" + _tu(600, "mo") + "</p>", _muc("h2", "Methods", 1200, "meth"),
              _muc("h3", "Box 1.", 100, "box"), _muc("h2", "Results", 1200, "res"), _muc("h2", "Interpretation", 1100, "interp"),
              _muc("h2", "Acknowledgments", 60, "ack"), _muc("h2", "Footnotes", 80, "fn"), _muc("h2", "References", 700, "ref"))
# Biến thể CMAJ có mở bài «Background» nhưng KHÔNG có Discussion/Interpretation — «Background» (≈ Introduction) quyết định.
CMAJ_BACKGROUND = _trang(TOM_TAT_CAU_TRUC, _muc("h2", "Background", 600, "bg"), _muc("h2", "Methods", 1200, "meth"),
                         _muc("h2", "Results", 1200, "res"), _muc("h2", "References", 2000, "ref"))
CHI_TOM_TAT = _trang(TOM_TAT_CAU_TRUC, _muc("h2", "References", 900, "ref"))
# Tóm tắt có cấu trúc + một khối bình luận dài KHÔNG phải IMRaD: chỉ việc loại tiểu mục TRONG tóm tắt giữ được kết luận «không».
TOM_TAT_CAU_TRUC_THAN_DAI = _trang(TOM_TAT_CAU_TRUC, _muc("h2", "Commentary", 2800, "com"), _muc("h2", "References", 1500, "ref"))
# Bài ngắn đủ IMRaD bằng thẻ (42702887: ~2 000 từ thân bài) và bài tổng quan không IMRaD (34610473: 21 mục, ~5 000 từ).
IMRAD_NGAN = _trang(_muc("h2", "Introduction", 250, "i"), _muc("h3", "Trial design and oversight", 200, "t"),
                    _muc("h3", "Statistical analysis", 200, "s"), _muc("h2", "Results", 600, "r"), _muc("h2", "Discussion", 450, "d"),
                    _muc("h2", "References", 800, "ref"))
TONG_QUAN = _trang(_muc("h2", "Abstract", 150, "abs"), *(_muc("h2", f"Topic section {i}", 420, f"t{i}") for i in range(1, 11)),
                   _muc("h2", "References", 4000, "ref"))

CA = {
    "nature_khong_quyen": (NATURE_KHONG_QUYEN, False),
    "chi_cat_references": (CHI_CAT_REFERENCES, False),
    "chi_tuong_phi": (CHI_TUONG_PHI, False),
    "imrad_binh_thuong": (IMRAD_BINH_THUONG, True),
    "guideline_dai": (GUIDELINE_DAI, True),
    "guideline_dai_mot_muc": (GUIDELINE_DAI_MOT_MUC, True),
    "nature_co_quyen": (NATURE_CO_QUYEN, True),
    "sage_co_quyen": (SAGE_CO_QUYEN, True),
    "sage_khong_quyen": (SAGE_KHONG_QUYEN, False),
    "cmaj": (CMAJ, True),
    "cmaj_background": (CMAJ_BACKGROUND, True),
    "chi_tom_tat": (CHI_TOM_TAT, False),
    "tom_tat_cau_truc_than_dai": (TOM_TAT_CAU_TRUC_THAN_DAI, False),
    "imrad_ngan": (IMRAD_NGAN, True),
    "tong_quan": (TONG_QUAN, True),
}


def _so_tu_ca_trang(html: str) -> int:
    return len(g._chu_tho(html).split())


def test_fixture_dung_tien_de_cua_lop_phong_thu():
    """Fixture phải đúng tiền đề nó kiểm, nếu không phép đột biến không đo gì: trang Nature/«chỉ tường phí» > 6000 từ cả trang
    (cổng CŨ nhận); «chỉ tường phí» có thân bài ≥ 6000 (bộ cắt không cứu được); CMAJ < 6000 từ cả trang."""
    for ten in ("nature_khong_quyen", "chi_cat_references", "chi_tuong_phi"):
        assert _so_tu_ca_trang(CA[ten][0]) >= 6000, ten
    assert len(g.phan_tich_trang_html(CHI_TUONG_PHI)["than_bai"].split()) >= 6000
    assert len(g.phan_tich_trang_html(CHI_CAT_REFERENCES)["than_bai"].split()) < 1500
    assert not g.phan_tich_trang_html(CHI_CAT_REFERENCES)["tuong_phi"]
    assert _so_tu_ca_trang(CMAJ) < 6000


@pytest.mark.parametrize("ten", sorted(CA))
def test_ket_luan_cong_gom(ten):
    html, ky_vong = CA[ten]
    ok, ly = g.la_toan_van_html(html)
    assert ok is ky_vong, f"{ten}: {ly}"


@pytest.mark.parametrize("ten", sorted(CA))
def test_cong_bh161_verify_dashboard_cung_ket_luan(ten, tmp_path):
    """Bản sao luật trong verify_dashboard (cổng BH161 — 4 bản đồng bộ byte) phải ra CÙNG kết luận với cổng gom."""
    q = tmp_path / "PMID-1_CHR.html"
    q.write_text(CA[ten][0], encoding="utf-8")
    assert vd._html_la_toan_van(q) is CA[ten][1], ten


def test_ly_do_noi_ro_tuong_phi_va_hau_bai():
    ok, ly = g.la_toan_van_html(NATURE_KHONG_QUYEN)
    assert not ok and "tường phí" in ly and "Access options" in ly and "hậu bài" in ly


def test_cat_tu_de_muc_hau_bai_cung_tieu_muc():
    pt = g.phan_tich_trang_html(NATURE_KHONG_QUYEN)
    assert "References" in pt["hau_bai"] and "Author information" in pt["hau_bai"]
    assert "aff1" not in pt["than_bai"] and "ci1" not in pt["than_bai"], "tiểu mục của khối hậu bài phải bị bỏ theo"
    assert "abs1" in pt["than_bai"]


def test_de_muc_rong_khong_lam_ranh_gioi_hau_bai():
    pt = g.phan_tich_trang_html(_trang(_muc("h2", "Introduction", 50), _muc("h2", "References", 500, "ref"),
                                       "<h3></h3><p>" + _tu(300, "ref") + "</p>"))
    assert "ref1" not in pt["than_bai"]


def test_tieu_muc_tom_tat_khong_tinh_nhom_imrad():
    assert g.phan_tich_trang_html(CHI_TOM_TAT)["nhom_imrad"] == set()
    assert g.phan_tich_trang_html(CMAJ)["nhom_imrad"] == {"phuong_phap", "ket_qua", "ban_luan"}


def test_chu_tho_khong_the_giu_luat_cu():
    """Chuỗi KHÔNG có thẻ (gọi kiểu cũ) giữ nguyên luật cũ — tương thích `test_gom_unpaywall_cong_20261004`."""
    assert g.la_toan_van_html("Recommendation " + "x " * 6500)[0]
    assert not g.la_toan_van_html("word " * 1000)[0]


_GOI_CHU_THO = re.compile(r"la_toan_van_html\(\s*(?:[A-Za-z_][\w.]*\.)?_van_ban_tho\(")


def test_moi_noi_goi_truyen_nguyen_van_html():
    """Chốt khớp DÒNG THI HÀNH (CLAUDE.md §0.8): không LỜI GỌI nào truyền chữ thô `_van_ban_tho(...)` vào cổng — chữ thô làm cổng
    MÙ đề mục, mọi lớp mới thành vô hiệu. Mẫu khớp đúng lời gọi (chuỗi ký tự nhắc tên hàm trong bộ kiểm không khớp)."""
    assert _GOI_CHU_THO.search('cong.la_toan_van_html(cong._van_ban_tho(van_ban.encode("utf-8")))')
    assert _GOI_CHU_THO.search("la_toan_van_html(_van_ban_tho(du_lieu))")
    assert not _GOI_CHU_THO.search('if "la_toan_van_html(" in code and "_van_ban_tho(" in code:')
    sai = []
    for q in sorted((REPO / "tools").glob("*.py")):
        if q.name.startswith("test_"):
            continue
        for i, dong in enumerate(q.read_text(encoding="utf-8").splitlines(), 1):
            if _GOI_CHU_THO.search(dong.split("#", 1)[0]):
                sai.append(f"{q.name}:{i}")
    assert not sai, sai


def test_tang_unpaywall_tu_choi_trang_tuong_phi(tmp_path, monkeypatch):
    """Tầng 2 Unpaywall (bản mang giấy phép mở nên qua cổng điều khoản) tải về trang tường phí dài ⇒ KHÔNG lưu; toàn văn CMAJ ⇒
    lưu. Mạng giả, kho tạm — khoá nơi gọi qua biến trung gian mà chốt khớp dòng không thấy."""
    import io
    import json

    trang = {"10.1038/x": NATURE_KHONG_QUYEN, "10.1503/y": CMAJ}
    pm_doi = {"27811932": "10.1038/x", "16129869": "10.1503/y"}

    class _PH(io.BytesIO):
        def __init__(self, b, u):
            super().__init__(b)
            self._u = u

        def geturl(self):
            return self._u

    def _mang(req, timeout=None, context=None):
        u = req if isinstance(req, str) else req.full_url
        if "esummary.fcgi" in u:
            pm = re.search(r"id=(\d+)", u).group(1)
            return _PH(json.dumps({"result": {pm: {"articleids": [{"idtype": "doi", "value": pm_doi[pm]}]}}}).encode(), u)
        if "api.unpaywall.org" in u:
            doi = re.search(r"/v2/(10\.\d+/\w)", u).group(1)
            return _PH(json.dumps({"is_oa": True, "best_oa_location": {"url": f"https://oa.invalid/{doi}", "license": "cc-by"}}).encode(), u)
        doi = u.split("oa.invalid/", 1)[1]
        return _PH(trang[doi].encode("utf-8"), u)

    monkeypatch.setattr("urllib.request.urlopen", _mang)
    monkeypatch.setattr(g, "KHO", tmp_path)
    monkeypatch.setattr(g, "_email_lich_su", lambda: "test@example.org")
    monkeypatch.setattr(g.time, "sleep", lambda s: None)
    moi, con_thieu = g.tang_unpaywall(["27811932", "16129869"])
    assert not (tmp_path / "PMID-27811932_UPW.html").exists() and "27811932" in con_thieu
    assert (tmp_path / "PMID-16129869_UPW.html").exists() and moi == 1


def test_bao_phu_cuc_bo_dung_cong_moi(tmp_path):
    """Bộ đếm «đã có toàn văn» (`bao_phu_cuc_bo` → `la_html_toan_van`) và cổng BH161 cùng loại trang tường phí, cùng nhận CMAJ."""
    a, b = tmp_path / "PMID-27811932_CHR.html", tmp_path / "PMID-16129869_CHR.html"
    a.write_text(NATURE_KHONG_QUYEN, encoding="utf-8")
    b.write_text(CMAJ, encoding="utf-8")
    assert not dtv.la_html_toan_van(a) and dtv.la_html_toan_van(b)
    assert not vd.co_toan_van_trong_kho("27811932", tmp_path) and vd.co_toan_van_trong_kho("16129869", tmp_path)


# ── Phiên Chrome `--nhan` (TT-04): trang tường phí bị TỪ CHỐI, không vào kho ─────────────────────────────────────────────────
T0 = datetime(2026, 10, 15, 9, 0, 0, tzinfo=timezone(timedelta(hours=7)))
URL = "https://www.nature.com/articles/nrcardio.2016.174"


def _dtv_gia():
    bang = {"Springer Nature": {"ket_luan": "cam", "doi": ("10.1038/",), "mien": ("nature.com",)}}

    def nxb_cua(doi="", url="", tieu_de=""):
        return ("Springer Nature", bang["Springer Nature"]) if P._mien(url).endswith("nature.com") else (None, None)
    return types.SimpleNamespace(DIEU_KHOAN_NXB=bang, nxb_cua=nxb_cua, uy_quyen_bac_si=lambda ten, hom_nay=None: {"nxb": ten})


def test_phien_chrome_tu_choi_trang_tuong_phi(tmp_path):
    so = tmp_path / "state" / "phien.json"
    assert P.mo("uỷ quyền phiên: đọc và lưu toàn văn các bài trong phiếu hôm nay", bay_gio=T0, tep=so, dtv=_dtv_gia())[0] == 0
    ma = P.doc_phien(so)["ma"]
    for pmid, than, ky_vong in (("27811932", NATURE_KHONG_QUYEN, None), ("16129869", CMAJ, "html")):
        t = tmp_path / f"tai-{pmid}.html"
        t.write_text(f"<!-- ebm-phien:{ma} pmid:{pmid} url:{URL} -->\n{than}", encoding="utf-8")
        loai, ly = P.kiem_tep(t, pmid, ma)
        assert loai == ky_vong, (pmid, ly)
        if ky_vong is None:
            assert "tường phí" in ly


def test_hai_ban_verify_dashboard_trung_byte():
    a = REPO / "sync/skills/cap-nhat-chung-cu-y-khoa/tools/verify_dashboard.py"
    assert a.read_bytes() == (REPO / "sync/skills/dark-analyst/tools/verify_dashboard.py").read_bytes()


def test_hai_ban_cong_cung_bo_mau_de_muc():
    """Danh sách đề mục tường phí / hậu bài / tóm tắt / nhóm IMRaD của hai bản phải TRÙNG (so mẫu regex đã biên dịch)."""
    assert g.DE_MUC_TUONG_PHI.pattern == vd._DE_MUC_TUONG_PHI_KHO.pattern
    assert g.DE_MUC_HAU_BAI.pattern == vd._DE_MUC_HAU_BAI_KHO.pattern
    assert g.DE_MUC_TOM_TAT.pattern == vd._DE_MUC_TOM_TAT_KHO.pattern
    assert [(t, m.pattern) for t, m in g.NHOM_IMRAD] == [(t, m.pattern) for t, m in vd._NHOM_IMRAD_KHO]
    assert re.sub(r"\s", "", str(g._NHOM_TU_KHOA_CU)) == re.sub(r"\s", "", str(vd._NHOM_TU_KHOA_CU_KHO))
