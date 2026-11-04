"""Trình bày tiếng Việt của bản tóm tắt chứng cứ Word/PDF — 04/11/2026.

Bác sĩ: «các bản tóm tắt toàn văn bằng tiếng Việt chưa thực sự chuẩn xác cả về trình bày và ngữ nghĩa». Đo trên 282 bản:
- PDF (bản bác sĩ mở trong EndNote) dựng qua pandoc ⇒ mất màu chữ (cảnh báo đỏ, lợi ích xanh), mất căn lề; ô «ĐIỂM NHẤN» một
  dòng thành dòng tiêu đề in đậm căn giữa; CSS «không ngắt giữa dòng» đẩy khối dài sang trang sau, trang 1 gần như trống;
- 32.436 số thập phân dấu chấm, 656 số nghìn kiểu Anh, nhãn «Nhận định thẩm định»/«…của người soạn» lẫn nhau, «lực mạnh/yếu»,
  «95% CI»; bảng kết quả 9 cột hẹp, ô bị bẻ 6–7 dòng.
Chuẩn hoá chỉ ở bước DỰNG — tom_tat.json (đã qua cổng số + kiểm chéo) không đổi; bất biến: dãy chữ số giữ nguyên.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import docx_sang_html_khong_pandoc as H  # noqa: E402
import tom_tat_chung_cu_word as T  # noqa: E402

try:
    import docx  # noqa: F401
    _CO_DOCX = True
except ImportError:  # CI bản sao trần không cài python-docx
    _CO_DOCX = False
CAN_DOCX = pytest.mark.skipif(not _CO_DOCX, reason="cần python-docx (venv ~/.ebm-venv)")


@pytest.mark.parametrize("vao, ra", [
    ("HR 0.80 (KTC 95% 0.70–0.91); p=0.0005", "HR 0,80 (KTC 95% 0,70–0,91); p=0,0005"),
    ("HR 0.80 và 0.85; -4.1 đến 18.4", "HR 0,80 và 0,85; -4,1 đến 18,4"),
    ("tuổi 68.8±12.7; mL/phút/1.73 m²; HR 0.80/0.85", "tuổi 68,8±12,7; mL/phút/1,73 m²; HR 0,80/0,85"),
    ("13,454 người; $10,000", "13.454 người; $10.000"),
    ("2,3-BPG và 1,25-dihydroxy", "2,3-BPG và 1,25-dihydroxy"),
    ("khuyến cáo 1.1, 1.2 và 1.3; HR 0.80", "khuyến cáo 1.1, 1.2 và 1.3; HR 0,80"),
    ("Phân tích 7.1 và 7.2 ghi OR 1.5", "Phân tích 7.1 và 7.2 ghi OR 1,5"),
    ("Bảng 12.1 · mục 5.2 · (R 2.1, mạnh)", "Bảng 12.1 · mục 5.2 · (R 2.1, mạnh)"),
    ("R 4.5.2 hoặc SAS 9.4; Stata 17.0", "R 4.5.2 hoặc SAS 9.4; Stata 17.0"),
    ("DOI 10.1161/CIRC.126.08; doi:10.1016/j.jad.2026.122421", "DOI 10.1161/CIRC.126.08; doi:10.1016/j.jad.2026.122421"),
    ("E11.65 (ICD-10)", "E11.65 (ICD-10)"),
    ("bài viết «HR 0.80; 95% CI 0.7» và HR 0.80", "bài viết «HR 0.80; 95% CI 0.7» và HR 0,80"),
    ("Nhận định thẩm định: x (nhận định của người soạn)", "Nhận định của người tóm tắt: x (nhận định của người tóm tắt)"),
    ("Lực khuyến cáo; đều lực yếu; lực mạnh; Không ghi lực (mô tả)",
     "Độ mạnh khuyến cáo; đều khuyến cáo yếu; khuyến cáo mạnh; Không ghi độ mạnh khuyến cáo (mô tả)"),
    ("thiếu lực thống kê; đủ lực; nguồn lực", "thiếu lực thống kê; đủ lực; nguồn lực"),
    ("SMD 0,44 (95% CI 0,21–0,67)", "SMD 0,44 (KTC 95% 0,21–0,67)"),
    ("Quality of evidence: very low", "Quality of evidence: very low (chất lượng chứng cứ rất thấp)"),
    ("tổng quan tường thuật. Tường thuật dẫn x", "tổng quan tường thuật. Phần diễn giải của nguồn dẫn x"),
])
def test_trinh_bay_vi(vao, ra):
    assert T.trinh_bay_vi(vao) == ra


def test_bat_bien_day_chu_so_tren_mau_gia():
    mau = ["HR 0.76 (KTC 95% 0.69-0.84), MRA HR 0.89", "13,454 người, 4.201% / 4.062%", "phân tích 1.1, P = 0.0066; R 4.5.2",
           "Bảng 2.1 và 2.2; 0.5 mg; 12 257 người", "doi 10.1056/NEJMoa2606998 · ARR 1.8 điểm %"]
    for s in mau:
        assert re.sub(r"\D", "", T.trinh_bay_vi(s)) == re.sub(r"\D", "", s), s


@CAN_DOCX
def test_bang_mot_dong_la_o_hop_khong_phai_dong_tieu_de():
    from docx import Document
    d = Document()
    t = d.add_table(rows=1, cols=1)
    t.cell(0, 0).paragraphs[0].add_run("ĐIỂM NHẤN: nội dung dài")
    html = H._bang_sang_html(t)
    assert html.startswith('<table class="hop">') and "<th" not in html


@CAN_DOCX
def test_bang_nhieu_dong_co_thead():
    from docx import Document
    d = Document()
    t = d.add_table(rows=2, cols=2)
    t.cell(0, 0).paragraphs[0].add_run("Kết cục")
    t.cell(1, 0).paragraphs[0].add_run("Tử vong")
    html = H._bang_sang_html(t)
    assert "<thead><tr><th>" in html and "<tbody><tr><td>" in html


@CAN_DOCX
def test_doan_giu_can_giua_mau_chu_va_co_chu():
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Pt, RGBColor
    d = Document()
    p = d.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("cảnh báo")
    r.font.color.rgb = RGBColor.from_string("C00000")
    r.font.size = Pt(16)
    html = H._doan_sang_html(p)
    assert 'style="text-align:center"' in html and "color:#C00000" in html and "font-size:16pt" in html


def test_dung_pdf_ep_khong_pandoc(tmp_path):
    docx = tmp_path / "a_TomTatChungCu.docx"
    docx.write_bytes(b"x")
    goi = []

    def chay(lenh, **k):
        goi.append(lenh)
        T.tep_pdf(docx).write_bytes(b"%PDF-")
        return type("KQ", (), {"returncode": 0, "stdout": ""})()

    assert T.dung_pdf(docx, chay=chay) is not None
    assert "--khong-pandoc" in goi[0], "pandoc bỏ màu chữ và căn lề của bản tóm tắt"


def test_bang_ket_qua_tam_cot_gop_hieu_ung_ktc():
    assert len(T.COT_BANG_SO) == len(T.RONG_BANG_SO) == 8
    assert abs(sum(T.RONG_BANG_SO) - 17.0) < 1e-9
    h = {"hieu_ung": "HR 0.80", "ktc95": "0.70–0.91", "may_tinh": []}
    assert T._hieu_ung_ktc(h) == "HR 0.80 (0.70–0.91)"
    assert T._hieu_ung_ktc({"hieu_ung": "ARR 2%", "ktc95": "", "may_tinh": ["hieu_ung"]}) == "ARR 2% †"
    assert T._hieu_ung_ktc({"hieu_ung": "", "ktc95": "0.7–0.9"}) == "0.7–0.9"


@CAN_DOCX
def test_word_in_theo_quy_uoc_viet_va_hai_dong_dau_trang():
    tt = {"loai_thiet_ke": "rct", "ket_luan_thuc_hanh": ["HR 0.80 (0.70–0.91); 13,454 người"],
          "ket_qua": [{"ket_cuc": "Tử vong", "chinh": True, "nhom_can_thiep": "434 (7.9%)", "nhom_so_sanh": "539 (9.7%)",
                       "hieu_ung": "HR 0.80", "ktc95": "0.70–0.91", "p": "0.0005", "tuyet_doi": "", "nnt": "",
                       "may_tinh": [], "trang": 5}]}
    ngc = {"ban_ghi": {"tieu_de": "T"}, "rut_bai": {"trang_thai": "khong_thay_rut", "luc": "2026-10-29T04:36:53"}}
    doc = T.dung_word(tt, ngc)
    chu = "\n".join(p.text for p in doc.paragraphs)
    o = "\n".join(c.text for t in doc.tables for r in t.rows for c in r.cells)
    assert "HR 0,80 (0,70–0,91); 13.454 người" in o
    assert "HR 0,80 (0,70–0,91)" in o and "434 (7,9%)" in o
    assert "THIẾT KẾ:" in chu and "RÚT BÀI:" in chu
    dong = [p.text for p in doc.paragraphs if "THIẾT KẾ:" in p.text or "RÚT BÀI:" in p.text]
    assert len(dong) == 2, "hai nhãn ở hai dòng riêng"
    assert "tra 29/10/2026" in o and "2026-10-29T" not in o
    assert json.dumps(tt)  # tom_tat.json không bị sửa tại chỗ
    assert tt["ket_luan_thuc_hanh"][0] == "HR 0.80 (0.70–0.91); 13,454 người"


def test_css_in_cho_o_hop_ngat_trang():
    import docx_sang_pdf_giu_mau as P
    css = re.sub(r"/\*.*?\*/", "", P.CSS_IN, flags=re.S)
    assert re.search(r"table\.hop\s+tr\s*\{[^}]*page-break-inside:\s*auto", css), "khối ĐIỂM NHẤN dài phải ngắt được giữa trang"
    assert re.search(r"table\.hop\s+td\s*\{[^}]*text-align:\s*left", css)
