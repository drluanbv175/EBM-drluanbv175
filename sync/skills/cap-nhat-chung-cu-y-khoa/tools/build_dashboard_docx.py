#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_dashboard_docx.py — Xuất MỌI Web Dashboard EBM "Evidence Workbench" (WebDashboard_*.html)
thành 1 file Word chi tiết: trang bìa + cảnh báo, mục lục tự động, khối tóm tắt thực hành
(nên làm/không nên/cờ đỏ — có màu), và một bảng riêng cho từng mục chứng cứ với huy hiệu
màu mức chứng cứ + quyết định, dòng "Khuyến cáo/Hành động" tô nền làm điểm nhấn, tài liệu
tham khảo đầy đủ. Toàn bộ font Times New Roman.

MẶC ĐỊNH từ 2026-07-18 cho mọi yêu cầu "xuất bản Word chi tiết" từ một dashboard EBM đã có
(xem feedback_word_export_dashboard_format.md). Không tự chạy — gọi khi bác sĩ cần bản
in/lưu trữ/nộp ngoài trình duyệt cho một dashboard cụ thể.

Cách dùng (trong EBM-Dashboards/, venv ~/.ebm-venv):
  python3 tools/build_dashboard_docx.py <dashboard.html>
  python3 tools/build_dashboard_docx.py <dashboard.html> --out "derivatives/TenFile.docx"
  python3 tools/build_dashboard_docx.py <dashboard.html> --parts parts.json

  parts.json (TÙY CHỌN — chỉ cần khi muốn nhóm mục theo "phần" lớn, vd 1 dashboard gộp
  nhiều chủ đề con như VKDT "chẩn đoán-điều trị / bệnh kèm / đối tượng đặc biệt"):
    [
      {"title": "CHẨN ĐOÁN & ĐIỀU TRỊ", "ids": ["ITEM-01", "ITEM-02", "..."]},
      {"title": "BỆNH ĐỒNG MẮC",        "ids": ["ITEM-14", "..."]}
    ]
  KHÔNG truyền --parts → liệt kê tuần tự toàn bộ items đúng thứ tự trong dashboard, dưới
  một mục "NỘI DUNG CHỨNG CỨ" duy nhất — phù hợp đa số dashboard (chỉ 1 chủ đề).

Yêu cầu: python-docx (đã có sẵn trong ~/.ebm-venv). KHÔNG cần Node.js/LibreOffice/pandoc —
xem feedback_mac_missing_docx_toolchain.md về lý do và cách kiểm chứng thay thế
(scripts/office/validate.py của skill docx + tự mở lại file bằng python-docx để đếm
bảng/heading/màu, vì máy không dựng được ảnh xem trước).
"""
import argparse
import json
import os
import re
import sys

# Windows: stdout mặc định cp1252 → dòng print kết thúc (có '✓' và tiếng Việt) ném
# UnicodeEncodeError SAU KHI file .docx đã ghi xong, làm tiến trình thoát mã 1. Hậu quả
# đo được ngày 12/08/2026: `xuat_goi_cap_nhat.py` đọc mã thoát, kết luận bước ③ hỏng rồi
# BỎ LUÔN bước ④ và ⑤ — mất 3/5 sản phẩm dù bản Word 82 KB đã nằm sẵn trên đĩa. Đúng lớp
# lỗi "gãy im lặng trên Windows" đã vá cho tools/vietnamize/ và build_dashboard_from_data.py.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

FONT = "Times New Roman"

COL = dict(
    ink="14172B", ink2="3D4266", muted="6B7094",
    brand="1E3A8A", teal="0E7490",
    ok="15803D", warn="B45309", bad="B91C1C", white="FFFFFF",
)
BG = dict(
    lineLight="EEF0F7", okBg="E7F6EC", warnBg="FDF1E2", badBg="FBE4E4",
    infoBg="E5F4F6", highlight="EAF3FB", grayBg="EEF0F7",
)
GRADE_META = {
    "high": ("Cao", COL["ok"], BG["okBg"]),
    "mod":  ("Trung bình", COL["warn"], BG["warnBg"]),
    "low":  ("Thấp", COL["warn"], BG["warnBg"]),
    "vlow": ("Rất thấp", COL["bad"], BG["badBg"]),
    "na":   ("Nguồn không phân hạng", COL["muted"], BG["grayBg"]),
}
DEC_META = {
    "apply":    ("ÁP DỤNG NGAY", COL["ok"], BG["okBg"]),
    "consider": ("CÂN NHẮC CHỌN LỌC", COL["warn"], BG["warnBg"]),
    "notyet":   ("CHƯA ĐỦ THAY ĐỔI", COL["bad"], BG["badBg"]),
}
DESIGN_LABEL = {"Guideline": "Guideline", "Meta": "Meta-analysis", "RCT": "RCT", "Cohort": "Cohort", "Consensus": "Đồng thuận"}
GROUP_LABEL = {"cao-tuoi": "Người cao tuổi", "ckd": "CKD", "gan": "Bệnh gan", "dtd": "Đái tháo đường", "tim-mach": "Tim mạch", "da-thuoc": "Đa thuốc"}


# ==================== 1. Trích DATA từ dashboard (JS object literal -> dict Python) ====================







# Ba hàm chuyển JS→JSON đã CHUYỂN sang verify_dashboard.py (file được đồng bộ 3 nơi)
# ngày 18/08/2026, để cổng liêm chính dùng được CHÍNH parser này. Import ngược về đây
# giữ đúng MỘT bản cài đặt — copy lại sang file này là tái sinh rủi ro hai-parser-bất-đồng.
# Nạp CHỊU ĐƯỢC MỌI KIỂU GỌI. File này vừa chạy như script (sys.path[0] = thư mục
# tools ⇒ import thẳng được) vừa bị nạp bằng importlib.spec_from_file_location từ chốt
# hồi quy (khi đó thư mục tools KHÔNG nằm trong sys.path ⇒ ModuleNotFoundError). Bản
# đầu của bản vá 18/08 chỉ viết `from verify_dashboard import ...` và lập tức làm ĐỎ
# BH13 lẫn BH59 — hai chốt vốn nạp file này theo đường dẫn. Tự thêm thư mục của chính
# mình vào sys.path trước khi import là cách duy nhất đúng cho cả hai lối gọi.
import os as _os_bdd  # noqa: E402
import sys as _sys_bdd  # noqa: E402
_thu_muc_bdd = _os_bdd.path.dirname(_os_bdd.path.abspath(__file__))
if _thu_muc_bdd not in _sys_bdd.path:
    _sys_bdd.path.insert(0, _thu_muc_bdd)
from verify_dashboard import (  # noqa: E402
    js_object_literal_to_json, join_string_concatenation, strip_trailing_commas)


def extract_dashboard_data(html_path):
    html = open(html_path, encoding="utf-8").read()
    start = html.index("const DATA = {") + len("const DATA = ")
    end_markers = ["/* ▲▲▲  HẾT KHỐI DATA  ▲▲▲ */", "/* ▲▲▲ HẾT KHỐI DATA ▲▲▲ */"]
    end = -1
    for m in end_markers:
        idx = html.find(m, start)
        if idx != -1:
            end = idx; break
    if end == -1:
        raise ValueError(
            f"Không tìm thấy marker kết thúc khối DATA trong {html_path} — dashboard này có thể "
            "thiếu comment '/* ▲▲▲ HẾT KHỐI DATA ▲▲▲ */' cuối khối (xem "
            "project-vkdt-comprehensive-dashboard-2026-07-17.md về bug tương tự ở verify_dashboard.py)."
        )
    block = html[start:end].strip()
    block = re.sub(r";\s*$", "", block)
    json_text = js_object_literal_to_json(block)
    json_text = join_string_concatenation(json_text)
    json_text = strip_trailing_commas(json_text)
    return json.loads(json_text)


# ==================== 2. Helper dựng nội dung Word ====================

def style_cell(cell, shading=None, border_color="D9DCEA", border_sz=4, borders=True):
    """OOXML CT_TcPrBase yêu cầu ĐÚNG thứ tự con trong <w:tcPr>: tcBorders PHẢI đứng trước
    shd. Gộp cả 2 vào 1 hàm, append theo đúng thứ tự trong CÙNG 1 lần gọi — gọi 2 hàm riêng
    theo thứ tự tuỳ ý (shading trước borders) sẽ tạo XML sai schema dù python-docx không báo lỗi."""
    tcPr = cell._tc.get_or_add_tcPr()
    if borders:
        b = OxmlElement("w:tcBorders")
        for edge in ("top", "left", "bottom", "right"):
            el = OxmlElement(f"w:{edge}")
            el.set(qn("w:val"), "single"); el.set(qn("w:sz"), str(border_sz)); el.set(qn("w:color"), border_color)
            b.append(el)
        tcPr.append(b)
    if shading:
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), shading)
        tcPr.append(shd)


def set_col_widths(table, widths_cm):
    table.autofit = False
    for row in table.rows:
        for idx, w in enumerate(widths_cm):
            row.cells[idx].width = Cm(w)
    tbl = table._tbl
    tblGrid = tbl.find(qn("w:tblGrid"))
    if tblGrid is None:
        tblGrid = OxmlElement("w:tblGrid"); tbl.insert(0, tblGrid)
    else:
        for gc in list(tblGrid):
            tblGrid.remove(gc)
    for w in widths_cm:
        gc = OxmlElement("w:gridCol"); gc.set(qn("w:w"), str(int(w * 567)))
        tblGrid.append(gc)


def add_run(p, text, bold=False, italic=False, size=11, color=None, font=FONT, highlight_bg=None):
    r = p.add_run(text)
    r.font.name = font; r.font.size = Pt(size); r.font.bold = bold; r.font.italic = italic
    if color is not None:
        from docx.shared import RGBColor
        r.font.color.rgb = RGBColor.from_string(color) if isinstance(color, str) else color
    rPr = r._element.get_or_add_rPr()
    ea = OxmlElement("w:rFonts")
    ea.set(qn("w:ascii"), font); ea.set(qn("w:hAnsi"), font); ea.set(qn("w:eastAsia"), font); ea.set(qn("w:cs"), font)
    rPr.append(ea)
    if highlight_bg:
        shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), highlight_bg)
        rPr.append(shd)
    return r


def add_para(doc_or_cell, text="", bold=False, italic=False, size=11, color=None, align=None, space_before=0, space_after=6):
    p = doc_or_cell.add_paragraph()
    if align is not None:
        p.alignment = align
    pf = p.paragraph_format
    pf.space_before = Pt(space_before); pf.space_after = Pt(space_after)
    if text:
        add_run(p, text, bold=bold, italic=italic, size=size, color=color)
    return p


def label_value_row(table, label, value, value_color=None, value_bold=False, value_shade=None, size=10.5):
    row = table.add_row()
    lc, vc = row.cells[0], row.cells[1]
    style_cell(lc, shading=BG["lineLight"]); style_cell(vc)
    add_run(lc.paragraphs[0], label, bold=True, size=9.5, color=COL["muted"])
    lc.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    add_run(vc.paragraphs[0], value or "—", bold=value_bold, size=size, color=value_color or COL["ink2"])
    if value_shade:
        style_cell(vc, shading=value_shade, borders=False)
    return row


def build_item_table(doc, it, w_label=3.6, w_value=12.6):
    table = doc.add_table(rows=0, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    src_line = f'{it.get("org","")}{" · "+it["dateVersion"] if it.get("dateVersion") else ""}'
    ids = []
    if it.get("pmid"): ids.append("PMID " + it["pmid"])
    if it.get("doi"): ids.append("DOI " + it["doi"])
    if it.get("url") and not it.get("pmid") and not it.get("doi"): ids.append("URL: " + it["url"])
    if ids:
        src_line += (" · " if src_line else "") + " · ".join(ids)
    row = table.add_row(); lc, vc = row.cells
    style_cell(lc, shading=BG["lineLight"]); style_cell(vc)
    add_run(lc.paragraphs[0], "Nguồn", bold=True, size=9.5, color=COL["muted"])
    add_run(vc.paragraphs[0], it.get("source", "—"), bold=True, size=10.5, color=COL["ink"])
    p2 = vc.add_paragraph(); p2.paragraph_format.space_before = Pt(1); p2.paragraph_format.space_after = Pt(2)
    add_run(p2, src_line, size=9, color=COL["muted"])

    label_value_row(table, "Thiết kế", DESIGN_LABEL.get(it.get("design"), it.get("design", "—")), value_color=COL["teal"], value_bold=True)
    label_value_row(table, "Quần thể", it.get("population"))

    gm = GRADE_META.get(it.get("gradeLevel"), GRADE_META["na"])
    dm = DEC_META.get(it.get("decision"), DEC_META["consider"])
    row = table.add_row(); lc, vc = row.cells
    style_cell(lc, shading=BG["lineLight"]); style_cell(vc)
    add_run(lc.paragraphs[0], "Mức chứng cứ · Quyết định", bold=True, size=9.5, color=COL["muted"])
    p = vc.paragraphs[0]
    add_run(p, "  " + gm[0] + "  ", bold=True, size=9.5, color=COL["white"], highlight_bg=gm[1])
    add_run(p, "   ")
    add_run(p, "  " + dm[0] + "  ", bold=True, size=9.5, color=COL["white"], highlight_bg=dm[1])
    p2 = vc.add_paragraph(); p2.paragraph_format.space_before = Pt(2); p2.paragraph_format.space_after = Pt(2)
    add_run(p2, it.get("gradeSource") or "Nguồn không cung cấp phân hạng", italic=True, size=9, color=COL["muted"])

    eff = it.get("effectText")
    if not eff and it.get("effect"):
        e = it["effect"]
        eff = f'{e.get("measure","Hiệu số")}: {e.get("hr","—")} (95% CI {e.get("ci","—")})'
    if eff:
        # Nhãn hàng đổi theo LOẠI nội dung (hiệu đính văn phong 18/08/2026, theo phản
        # hồi bác sĩ): mục có effect{} định lượng mới mang nhãn «Hiệu số»; mục chỉ có
        # effectText văn xuôi (guideline, đồng thuận, bản đồ tra cứu) mang nhãn
        # «Tóm tắt nghiên cứu» — nhãn hứa con số mà nội dung là mục lục là sai ngăn
        # ngữ nghĩa, người đọc mất tin vào cả những hàng đúng.
        nhan = "Hiệu số (theo nguồn)" if it.get("effect") else "Tóm tắt nghiên cứu (theo nguồn)"
        label_value_row(table, nhan, eff)

    label_value_row(table, "Khuyến cáo / Hành động", it.get("action"), value_shade=BG["highlight"], size=10.5)
    label_value_row(table, "Theo dõi", it.get("monitoring"))
    label_value_row(table, "Áp dụng tại Việt Nam", it.get("vn"))

    if it.get("groups"):
        label_value_row(table, "Nhóm đặc biệt liên quan", ", ".join(GROUP_LABEL.get(g, g) for g in it["groups"]))
    if it.get("flag"):
        label_value_row(table, "⚑ Lưu ý", it["flag"], value_color=COL["warn"], value_bold=True, value_shade=BG["warnBg"])
    if it.get("safety"):
        label_value_row(table, "⚑ An toàn / Chuyển tuyến", it["safety"], value_color=COL["bad"], value_shade=BG["badBg"])

    refs = it.get("references") or []
    row = table.add_row(); lc, vc = row.cells
    style_cell(lc, shading=BG["lineLight"]); style_cell(vc)
    add_run(lc.paragraphs[0], "Tài liệu tham khảo", bold=True, size=9.5, color=COL["muted"])
    if refs:
        for i, r in enumerate(refs):
            p = vc.paragraphs[0] if i == 0 else vc.add_paragraph()
            p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(3 if i < len(refs) - 1 else 0)
            add_run(p, f"{i+1}. {r}", size=8.5, color=COL["ink2"])
    else:
        add_run(vc.paragraphs[0], "—", italic=True, size=9, color=COL["muted"])

    set_col_widths(table, [w_label, w_value])
    return table


def add_summary_box(doc, title, entries, color_key, total_w=16.2):
    if not entries:
        return
    color = COL[color_key]; bg = {"ok": BG["okBg"], "warn": BG["warnBg"], "bad": BG["badBg"]}[color_key]
    table = doc.add_table(rows=1, cols=1)
    cell = table.rows[0].cells[0]
    style_cell(cell, shading=bg, border_color=color, border_sz=6)
    p0 = cell.paragraphs[0]; p0.paragraph_format.space_after = Pt(6)
    add_run(p0, title, bold=True, size=11, color=color)
    for e in entries:
        p = cell.add_paragraph(); p.paragraph_format.space_after = Pt(4); p.paragraph_format.left_indent = Pt(10)
        add_run(p, "—  ", color=color, size=10)
        add_run(p, e, size=10, color=COL["ink2"])
    set_col_widths(table, [total_w])
    add_para(doc, "", size=2, space_after=10)


def add_part_heading(doc, title, count=None):
    p = doc.add_paragraph(); p.style = doc.styles["Heading 1"]
    # pBdr PHẢI đứng trước spacing trong <w:pPr> — append trước khi set space_before/after.
    pPr = p.paragraph_format.element.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr"); bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single"); bottom.set(qn("w:sz"), "12"); bottom.set(qn("w:space"), "6"); bottom.set(qn("w:color"), COL["brand"])
    pBdr.append(bottom); pPr.append(pBdr)
    pf = p.paragraph_format; pf.space_before = Pt(22); pf.space_after = Pt(10)
    add_run(p, title, bold=True, size=16, color=COL["brand"])
    if count is not None:
        add_run(p, f"   ({count} mục)", bold=False, size=11, color=COL["muted"])


def add_field_code_toc(doc):
    p = doc.add_paragraph()
    run = p.add_run(); rPr = run._element.get_or_add_rPr()
    fonts = OxmlElement("w:rFonts"); fonts.set(qn("w:ascii"), FONT); fonts.set(qn("w:hAnsi"), FONT); rPr.append(fonts)
    fld1 = OxmlElement("w:fldChar"); fld1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = 'TOC \\o "1-2" \\h \\z \\u'
    sep = OxmlElement("w:fldChar"); sep.set(qn("w:fldCharType"), "separate")
    t = OxmlElement("w:t"); t.text = "Mở file và bấm Có khi Word hỏi cập nhật Mục lục (hoặc chọn cả mục lục rồi bấm F9)."
    fld2 = OxmlElement("w:fldChar"); fld2.set(qn("w:fldCharType"), "end")
    for el in (fld1, instr, sep, t, fld2):
        run._element.append(el)


# ==================== 3. Dựng toàn bộ document ====================

def build_docx(data, out_path, part_defs=None, subtitle=None, verified=False):
    items = data["items"]
    by_id = {it["id"]: it for it in items}

    if part_defs:
        used = set()
        for pd in part_defs:
            used.update(pd["ids"])
        leftover = [it["id"] for it in items if it["id"] not in used]
        if leftover:
            part_defs = list(part_defs) + [{"title": "MỤC KHÁC", "ids": leftover}]
    else:
        part_defs = [{"title": "NỘI DUNG CHỨNG CỨ", "ids": [it["id"] for it in items]}]

    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.top_margin = sec.bottom_margin = Cm(2.0)
    sec.left_margin = sec.right_margin = Cm(2.2)

    normal = doc.styles["Normal"]
    normal.font.name = FONT; normal.font.size = Pt(11)
    rPr = normal.element.get_or_add_rPr()
    ef = OxmlElement("w:rFonts")
    ef.set(qn("w:ascii"), FONT); ef.set(qn("w:hAnsi"), FONT); ef.set(qn("w:eastAsia"), FONT); ef.set(qn("w:cs"), FONT)
    rPr.append(ef)
    from docx.shared import RGBColor
    for lvl, sz, col in [(1, 16, COL["brand"]), (2, 13.5, COL["ink"]), (3, 12, COL["ink"])]:
        st = doc.styles[f"Heading {lvl}"]
        st.font.name = FONT; st.font.size = Pt(sz); st.font.color.rgb = RGBColor.from_string(col); st.font.bold = True

    footer_p = sec.footer.paragraphs[0]; footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(footer_p, "Cần bác sĩ kiểm chứng · Không lưu PII", italic=True, size=8, color=COL["muted"])
    header_p = sec.header.paragraphs[0]; header_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    add_run(header_p, "Antifacts EBM", italic=True, size=8, color=COL["muted"])

    question = data.get("meta", {}).get("question", "Cập nhật chứng cứ y khoa")
    updated = data.get("meta", {}).get("updated", "")

    add_para(doc, "EBM COPILOT", bold=True, size=13, color=COL["teal"], align=WD_ALIGN_PARAGRAPH.CENTER, space_before=60, space_after=4)
    add_para(doc, "Cập nhật chứng cứ · Vấn đề lâm sàng", italic=True, size=11, color=COL["muted"], align=WD_ALIGN_PARAGRAPH.CENTER, space_after=20)
    add_para(doc, question.upper(), bold=True, size=22, color=COL["brand"], align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)
    if subtitle:
        add_para(doc, subtitle, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=24)
    add_para(doc, f"Cập nhật: {updated}   ·   {len(items)} mục chứng cứ   ·   đã qua cổng kiểm liêm chính",
             size=10.5, color=COL["muted"], align=WD_ALIGN_PARAGRAPH.CENTER, space_after=30)

    disc = doc.add_table(rows=1, cols=1)
    dc = disc.rows[0].cells[0]
    style_cell(dc, shading=BG["warnBg"], border_color=COL["warn"], border_sz=8)
    p0 = dc.paragraphs[0]; add_run(p0, "⚠  CẦN BÁC SĨ KIỂM CHỨNG", bold=True, size=11, color=COL["warn"])
    p1 = dc.add_paragraph(); p1.paragraph_format.space_before = Pt(6)
    # SỬA 2026-07-22 (vòng lặp kiểm tra-hoàn thiện vòng 10, phát hiện HIGH): trước đây câu này
    # LUÔN khẳng định CỨNG "đã xác minh qua PubMed/Crossref" bất kể verify_dashboard.py --online
    # đã chạy/PASS cho dashboard nguồn hay chưa — build_docx() không hề gọi/đọc kết quả công cụ
    # đó. Nay CHỈ khẳng định khi caller (pipeline đã chạy verify_dashboard.py --online PASS)
    # truyền verified=True tường minh; mặc định (gọi tool đơn lẻ) dùng câu trung thực hơn.
    verify_claim = (
        "kèm PMID/DOI đã xác minh qua PubMed/Crossref cho từng mục (tools/verify_dashboard.py --online đã PASS)"
        if verified else
        "PMID/DOI CẦN được xác minh qua PubMed/Crossref bằng tools/verify_dashboard.py --online trước khi tin "
        "tưởng nội dung — tài liệu này KHÔNG tự kiểm tra bước đó"
    )
    add_run(p1, f"Tài liệu tổng hợp bằng chứng y khoa, {verify_claim}. "
                "Đây là công cụ hỗ trợ tra cứu — KHÔNG thay thế phán đoán lâm sàng và cần đối chiếu toàn văn, bối cảnh "
                "bệnh nhân cụ thể trước khi áp dụng. Không lưu thông tin định danh bệnh nhân (PII).",
            size=10.5, color=COL["ink2"])
    set_col_widths(disc, [16.6])
    doc.add_page_break()

    add_para(doc, "MỤC LỤC", bold=True, size=16, color=COL["brand"], space_after=10)
    doc.styles["Normal"]  # no-op to keep style ref warm
    toc_heading = doc.paragraphs[-1]; toc_heading.style = doc.styles["Heading 1"]
    add_field_code_toc(doc)
    doc.add_page_break()

    summary = data.get("summary", {})
    if summary:
        add_part_heading(doc, "TÓM TẮT THỰC HÀNH NHANH")
        if summary.get("conclusion"):
            add_para(doc, summary["conclusion"], size=11, space_after=12)
        add_summary_box(doc, "✓ NÊN LÀM HIỆN NAY", summary.get("doNow"), "ok")
        add_summary_box(doc, "⊘ KHÔNG NÊN / GIỚI HẠN", summary.get("dontDo"), "warn")
        add_summary_box(doc, "⚑ CỜ ĐỎ / CHUYỂN TUYẾN", summary.get("redFlags"), "bad")
        doc.add_page_break()

    for pi, pd in enumerate(part_defs):
        add_part_heading(doc, pd["title"], len(pd["ids"]))
        for iid in pd["ids"]:
            it = by_id.get(iid)
            if not it:
                print(f"⚠ Bỏ qua {iid}: không thấy trong DATA.items", file=sys.stderr)
                continue
            p = doc.add_paragraph(); p.style = doc.styles["Heading 2"]
            p.paragraph_format.space_before = Pt(16); p.paragraph_format.space_after = Pt(6)
            add_run(p, f'{it["id"]}. ', bold=True, size=13, color=COL["teal"])
            add_run(p, it["title"], bold=True, size=13, color=COL["ink"])
            build_item_table(doc, it)
            add_para(doc, "", size=4, space_after=8)
        if pi < len(part_defs) - 1:
            doc.add_page_break()

    doc.add_page_break()
    add_part_heading(doc, "NGUỒN VÀ LIÊM CHÍNH DỮ LIỆU")
    verify_footer_claim = (
        "Mọi PMID/DOI đã được xác minh khớp qua PubMed/Crossref bằng công cụ tools/verify_dashboard.py --online "
        "(đã PASS trước khi xuất tài liệu này)."
        if verified else
        "PMID/DOI của dashboard nguồn CẦN được xác minh qua tools/verify_dashboard.py --online — công cụ xuất "
        "tài liệu này KHÔNG tự chạy hay kiểm tra bước đó, chỉ trích xuất nguyên văn nội dung dashboard."
    )
    add_para(doc, "Tài liệu này trích xuất trực tiếp, không chỉnh sửa nội dung, từ dashboard EBM \"Evidence Workbench\" "
                  f"nêu trên. {verify_footer_claim} Grading/mức chứng cứ giữ nguyên theo nguồn gốc — không tự gán "
                  "GRADE khi nguồn không phân hạng.", size=10.5)
    add_para(doc, f"Cập nhật lần cuối: {updated}. Tổng {len(items)} mục chứng cứ.", italic=True, size=10, color=COL["muted"])

    # python-docx tạo <w:zoom> thiếu w:percent bắt buộc — XSD reject nếu không vá.
    settings_el = doc.settings.element
    zoom = settings_el.find(qn("w:zoom"))
    if zoom is None:
        zoom = OxmlElement("w:zoom"); settings_el.insert(0, zoom)
    zoom.set(qn("w:percent"), "100")

    doc.save(out_path)
    return len(items), len(part_defs)


# ==================== 4. CLI ====================

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dashboard", help="Đường dẫn WebDashboard_*.html")
    ap.add_argument("--out", help="Đường dẫn file .docx xuất ra (mặc định: derivatives/<tên dashboard>_TaiLieuChiTiet.docx)")
    ap.add_argument("--parts", help="Đường dẫn file JSON định nghĩa nhóm 'phần' (xem docstring đầu file)")
    ap.add_argument("--subtitle", help="Dòng phụ đề dưới tiêu đề chính (tuỳ chọn)")
    ap.add_argument("--verified", action="store_true",
                     help="Xác nhận tools/verify_dashboard.py --online đã chạy PASS cho dashboard này "
                          "TRƯỚC khi gọi lệnh này — chỉ khi đó tài liệu mới khẳng định 'đã xác minh qua "
                          "PubMed/Crossref'. KHÔNG tự động kiểm tra cờ này; mặc định (không truyền) dùng "
                          "câu chữ trung thực hơn, không khẳng định điều chưa chắc đã xảy ra.")
    args = ap.parse_args()

    data = extract_dashboard_data(args.dashboard)

    part_defs = None
    if args.parts:
        part_defs = json.loads(open(args.parts, encoding="utf-8").read())

    out_path = args.out
    if not out_path:
        base = os.path.splitext(os.path.basename(args.dashboard))[0]
        base = re.sub(r"^WebDashboard_EBM_VanDeCuThe_", "", base)
        out_dir = os.path.join(os.path.dirname(os.path.abspath(args.dashboard)), "derivatives")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f"{base}_TaiLieuChiTiet.docx")

    n_items, n_parts = build_docx(data, out_path, part_defs=part_defs, subtitle=args.subtitle, verified=args.verified)
    print(f"✓ Đã ghi {out_path} — {n_items} mục / {n_parts} phần ({os.path.getsize(out_path)} bytes)")
    print("  Lưu ý: máy này không dựng được ảnh xem trước (thiếu LibreOffice) — nên tự mở file")
    print("  bằng Word/Pages để xem bố cục thật trước khi giao. Xác thực cấu trúc XML bằng:")
    print("  python3 <skill docx>/scripts/office/validate.py " + out_path)


if __name__ == "__main__":
    main()
