#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""In toàn văn XML/HTML đã đọc trong kho thành PDF cho EndNote (18/10/2026).

Khoá:
  • JATS → HTML giữ tiêu đề · tác giả · định danh · Abstract (không lặp đề mục) · phần · bảng (colspan) · tài liệu tham khảo;
    hình chỉ giữ chú thích, không có thẻ tải tài nguyên; XML hỏng ⇒ ValueError;
  • HTML lưu sẵn: gỡ script (kể cả PDF base64 nhúng), ảnh, khung nhúng, trình xử lý sự kiện, mọi `src` — không gọi mạng lúc in;
  • dải đầu trang của bản `_CHR` ghi «CÓ BẢN QUYỀN» và «không phân phối lại»;
  • chọn nguồn: chỉ toàn văn THẬT, bỏ PMID đã có PDF hoặc đã có bản in, ưu tiên PMC > UPW > CHR; thân bài < 300 từ ⇒ không in;
  • `nap_endnote_chu_de.NGUON_PDF` nhận `BANIN` với ưu tiên THẤP NHẤT; `TEN_TEP_TOAN_VAN`/`bao_phu_cuc_bo` KHÔNG đếm `BANIN`;
  • bộ năm ⑧ chạy công cụ in với kho CẠNH dashboard, `--file`, `--ap-dung`.
Ngoại tuyến, không cần Chrome.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, TOOLS / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


IP = _nap("_in_pdf_20261018", "in_pdf_toan_van_kho.py")
NEC = _nap("_nec_banin_20261018", "nap_endnote_chu_de.py")
DTV = IP.dtv()

JATS = b"""<?xml version="1.0"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink"><front>
<journal-meta><journal-title-group><journal-title>Tap Chi Thu</journal-title></journal-title-group></journal-meta>
<article-meta><article-id pub-id-type="pmid">12345678</article-id><article-id pub-id-type="doi">10.1/abc</article-id>
<title-group><article-title>Bai <italic>thu</italic> nghiem</article-title></title-group>
<contrib-group><contrib contrib-type="author"><name><surname>Nguyen</surname><given-names>An</given-names></name></contrib></contrib-group>
<pub-date><year>2020</year></pub-date><volume>7</volume><fpage>11</fpage><lpage>19</lpage>
<abstract><title>Abstract</title><p>Tom tat ngan.</p></abstract></article-meta></front>
<body><sec><title>Methods</title><p>Phuong phap <xref ref-type="bibr" rid="r1">1</xref>.</p>
<table-wrap><label>Table 1</label><caption><p>Dac diem</p></caption><table><tr><td colspan="2">Gop</td></tr></table></table-wrap>
<fig><label>Figure 1</label><caption><p>Chu thich hinh</p></caption><graphic xlink:href="f1.jpg"/></fig></sec></body>
<back><ref-list><ref id="r1"><mixed-citation>Tac gia A. Bai tham khao. 2019.</mixed-citation></ref></ref-list></back></article>"""


def test_jats_sang_html_giu_cau_truc_va_khong_tai_tai_nguyen() -> None:
    h = IP.jats_sang_html(JATS)
    assert "<h1>Bai <i>thu</i> nghiem</h1>" in h
    assert "An Nguyen" in h and "Tap Chi Thu, 2020, tập 7, tr. 11-19" in h
    assert "PMID: 12345678" in h and "DOI: 10.1/abc" in h
    assert h.count(">Abstract<") == 1, "abstract tự có <title> ⇒ không thêm đề mục trùng"
    assert "<h2>Methods</h2>" in h and 'colspan="2"' in h
    assert "Chu thich hinh" in h and "<img" not in h and "f1.jpg" not in h
    assert "<h2>References</h2>" in h and "Bai tham khao" in h


def test_jats_hong_bao_loi() -> None:
    with pytest.raises(ValueError):
        IP.jats_sang_html(b"<article><front>")


def test_lam_sach_html_go_moi_duong_goi_mang() -> None:
    s = ("<!-- ebm-phien:1 pmid:1 url:x -->\n<!doctype html><html><head><title>t</title></head><body>"
         "<p onclick=\"x()\">Than bai</p><img src=\"https://a/b.png\"><iframe src=\"https://c\"></iframe>"
         "<script type=\"application/pdf;base64\" id=\"ebm-pdf\">JVBERi0xLjQ=</script><video src=\"v.mp4\"></video>"
         "<link rel=\"stylesheet\" href=\"https://d/e.css\"><div data-src=\"https://f\">x</div></body></html>")
    r = IP.lam_sach_html(s)
    for cam in ("<script", "JVBERi0", "<img", "<iframe", "<video", "<link", "onclick", "https://", "ebm-phien", "<html", "<body"):
        assert cam not in r, cam
    assert "Than bai" in r


def test_dai_dau_trang_ban_chr_ghi_ban_quyen() -> None:
    t = IP.bao_trang("<p>x</p>", "1", Path("PMID-1_CHR.html"))
    assert "CÓ BẢN QUYỀN" in t and "không phân phối lại" in t and "PMID 1" in t


def _gia_lap_that(monkeypatch, tep_theo_pmid: dict[str, list[str]], kho: Path) -> None:
    monkeypatch.setattr(DTV, "tep_toan_van_that", lambda k, pm: [kho / n for n in tep_theo_pmid.get(pm, [])])


def test_chon_nguon_chi_toan_van_that_chua_co_pdf_uu_tien_pmc(tmp_path, monkeypatch) -> None:
    _gia_lap_that(monkeypatch, {
        "1": ["PMID-1_CHR.html", "PMID-1_PMC9.xml", "PMID-1_UPW.html"],
        "2": ["PMID-2_CHR.html", "PMID-2_UPW.html"],
        "3": ["PMID-3_CHR.html", "PMID-3_CHR.pdf"],
        "4": [],
        "5": ["PMID-5_CHR.html"],
    }, tmp_path)
    (tmp_path / "PMID-5_BANIN.pdf").write_bytes(b"%PDF-1.4")
    assert IP.chon_nguon(tmp_path, "1").name == "PMID-1_PMC9.xml"
    assert IP.chon_nguon(tmp_path, "2").name == "PMID-2_UPW.html"
    assert IP.chon_nguon(tmp_path, "3") is None, "đã có PDF thật ⇒ EndNote gắn PDF đó, không in"
    assert IP.chon_nguon(tmp_path, "4") is None, "không có toàn văn thật ⇒ không in"
    assert IP.chon_nguon(tmp_path, "5") is None, "đã có bản in ⇒ không in lại"


def test_than_bai_qua_ngan_khong_in(tmp_path) -> None:
    q = tmp_path / "PMID-9_CHR.html"
    q.write_text("<html><body><p>Chi co tom tat ngan.</p></body></html>", encoding="utf-8")
    with pytest.raises(ValueError):
        IP.html_in("9", q)


def test_endnote_nhan_banin_uu_tien_thap_nhat(tmp_path) -> None:
    assert NEC.NGUON_PDF[-1][0] == "BANIN"
    (tmp_path / "PMID-7_BANIN.pdf").write_bytes(b"%PDF-1.4")
    assert NEC.chon_pdf(tmp_path, "7")[0].name == "PMID-7_BANIN.pdf"
    (tmp_path / "PMID-7_CHR.pdf").write_bytes(b"%PDF-1.4")
    assert NEC.chon_pdf(tmp_path, "7")[0].name == "PMID-7_CHR.pdf", "PDF gốc luôn thắng bản in"


def test_banin_khong_duoc_dem_thanh_toan_van(tmp_path) -> None:
    assert not DTV.TEN_TEP_TOAN_VAN.fullmatch("PMID-8_BANIN.pdf")
    (tmp_path / "PMID-8_BANIN.pdf").write_bytes(b"%PDF-1.4 " + b"x" * 4000)
    assert DTV.bao_phu_cuc_bo(["8"], tmp_path)["8"] == "chua_co"


def test_pmid_cua_dashboard_chi_doc_khoi_data(tmp_path) -> None:
    f = tmp_path / "WebDashboard_x.html"
    f.write_text("<p>pmid:'99999999'</p><script>const DATA = {items:[{id:'ITEM-01', pmid:'12345678'},"
                 "{id:'ITEM-02', pmid:\"23456789\"}]}; // HẾT KHỐI DATA</script>", encoding="utf-8")
    assert IP.pmid_cua_dashboard(f) == ["12345678", "23456789"]


def test_bo_nam_buoc_8_goi_cong_cu_in_voi_kho_canh_dashboard() -> None:
    XG = _nap("_xg_banin_20261018", "xuat_goi_cap_nhat.py")
    dash = Path("/du-lieu/EBM-Dashboards/WebDashboard_A.html")
    lenh = XG.lenh_in_pdf("python3", dash)
    assert lenh[1].endswith("in_pdf_toan_van_kho.py")
    assert lenh[lenh.index("--kho") + 1] == str(dash.parent / "toan_van_oa")
    assert "--ap-dung" in lenh and lenh[lenh.index("--file") + 1] == str(dash)


JATS_KHAI = b"""<?xml version="1.0"?>
<article><front><article-meta><article-id pub-id-type="pmid">87654321</article-id>
<title-group><article-title>Bai co khai bao</article-title></title-group>
<author-notes><corresp>Correspondence: <email>tacgia@vidu.org</email></corresp>
<fn fn-type="COI-statement"><p>Author A has acted in an advisory capacity for Hang Duoc X.</p></fn></author-notes>
<funding-group><award-group><funding-source>National Institute for Health and Care Research</funding-source>
<award-id>NIHR-1</award-id></award-group></funding-group>
<abstract><p>Tom tat.</p></abstract></article-meta></front>
<body><sec><title>Methods</title><p>Phuong phap.</p></sec></body></article>"""


def test_jats_giu_khai_xung_dot_loi_ich_va_tai_tro_bo_dia_chi_lien_he() -> None:
    """26/10/2026: `author-notes/fn` (khai xung đột lợi ích) và `funding-group` nằm trong article-meta từng bị bỏ hẳn ⇒
    tóm tắt ⑨ ghi «bài không khai xung đột lợi ích» trong khi bài có khai (PMID 42799440, 42914541)."""
    h = IP.jats_sang_html(JATS_KHAI)
    assert "advisory capacity for Hang Duoc X" in h
    assert "National Institute for Health and Care Research" in h and "NIHR-1" in h
    assert "tacgia@vidu.org" not in h, "địa chỉ liên hệ (corresp) không in"
    h2 = IP.jats_sang_html(JATS_KHAI.replace(
        b"<award-group>", b"<funding-statement>No specific funding was received.</funding-statement><award-group>"))
    assert "No specific funding was received." in h2 and "NIHR-1" not in h2, "có câu khai tài trợ ⇒ dùng câu đó"
    assert "Author notes and funding" not in IP.jats_sang_html(JATS), "bài không có khai báo ⇒ không thêm mục rỗng"


def test_jats_giu_khai_bao_dang_p_trong_author_notes_kieu_jama() -> None:
    """27/10/2026: JAMA đặt «Conflict of Interest Disclosures», «Funding/Support» bằng <p> thẳng trong author-notes (không bọc
    <fn>) ⇒ bản vá 26/10 chỉ in `fn` vẫn bỏ sót (PMID 42842238 và 21 XML khác trong kho)."""
    jama = JATS_KHAI.replace(
        b"<fn fn-type=\"COI-statement\"><p>Author A has acted in an advisory capacity for Hang Duoc X.</p></fn>",
        b"<title>Article Information</title><p><bold>Conflict of Interest Disclosures:</bold> Dr B reported grants from Y.</p>"
        b"<p><bold>Funding/Support:</bold> Supported by Quy Z.</p>")
    h = IP.jats_sang_html(jama)
    assert "Dr B reported grants from Y." in h and "Supported by Quy Z." in h
    assert "tacgia@vidu.org" not in h
    assert "Article Information" not in h, "title của author-notes không in lặp (đã có đề mục riêng)"
