#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chuyển tài liệu Markdown sang Word (.docx) — FONT MẶC ĐỊNH TIMES NEW ROMAN.

VÌ SAO CÓ (22/08/2026):
Repo đã có `EBM-Dashboards/tools/build_dashboard_docx.py`, nhưng công cụ đó chỉ
đọc được khối `DATA` của một dashboard Evidence Workbench — nó KHÔNG chuyển được
một tài liệu Markdown thường (báo cáo, hồ sơ kiểm kê, bản giao kiến trúc). Trước
nay các tài liệu đó chỉ có bản `.md`, mà `.md` thì không mở được bằng Word và
không in ra giấy cho hội đồng/đồng nghiệp đọc được.

NGUYÊN TẮC ĐI CÙNG DÂY CHUYỀN SẴN CÓ: bản `.docx` sinh TỪ CHÍNH file `.md` nguồn,
không gõ lại tay và không dựng lại nội dung từ dữ liệu khác — cùng lý do mà bộ năm
xuất đồng thời của dashboard tồn tại: hai bản dựng từ hai nguồn sẽ lệch nhau mà
không ai nhận ra.

FONT: Times New Roman toàn văn (thân bài · đề mục · bảng · trích dẫn), khớp quy ước
`build_dashboard_docx.py` đã dùng cho mọi tài liệu lưu trữ của hệ. Đoạn mã/đường dẫn
giữ NGUYÊN Times New Roman nhưng tô nền xám nhạt để vẫn phân biệt được — không đổi
sang font khác, vì mặc định đã được ấn định là Times New Roman.

PHẠM VI CỐ Ý HẸP — công cụ này KHÔNG kiểm nội dung y khoa, KHÔNG chấm chất lượng,
KHÔNG thay `verify_dashboard.py` hay bất kỳ cổng nào. Nó chỉ đổi định dạng.

Cú pháp Markdown hỗ trợ: đề mục `#`–`####` · đoạn văn · **đậm** · *nghiêng* ·
`mã` · [chữ](liên-kết) · bảng dạng ống · trích dẫn `>` · danh sách `-`/`*`/`1.` ·
đường kẻ ngang `---`.

CHẾ ĐỘ TRÌNH BÀY ĐỀ CƯƠNG (`--trang-de-cuong`, thêm 15/10/2026): dùng cho văn bản nộp
Hội đồng (đề cương, thuyết minh). Khổ A4; lề trái 3 cm, phải/trên/dưới 2 cm; đoạn văn
căn đều hai bên, giãn dòng 1,3; số trang giữa chân trang. Đường kẻ `---` KHÔNG vẽ
thành đường kẻ mà thành NGẮT TRANG; mọi nội dung đứng trước `---` đầu tiên là TRANG BÌA
và được căn giữa.

Dùng:
    python3 tools/md_sang_docx_times.py <đầu-vào>.md [--ra <đầu-ra>.docx]
    python3 tools/md_sang_docx_times.py bao-cao.md --co-chu 12
    python3 tools/md_sang_docx_times.py de-cuong.md --co-chu 13 --trang-de-cuong

Mã thoát: 0 = xong · 2 = lỗi đầu vào hoặc thiếu python-docx.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt, RGBColor
except ImportError:  # pragma: no cover - phụ thuộc môi trường
    print("❌ Thiếu python-docx. Cài: pip install python-docx "
          "(venv ~/.ebm-venv đã có sẵn).", file=sys.stderr)
    raise SystemExit(2) from None

FONT = "Times New Roman"
XAM_MA = "EEEEEE"       # nền đoạn mã
XAM_CHU = RGBColor(0x44, 0x44, 0x44)

# Inline: mã trước tiên để nội dung bên trong không bị parse tiếp.
_INLINE = re.compile(
    r"(`[^`]+`)"
    r"|(\*\*[^*]+\*\*)"
    r"|(\*[^*\n]+\*)"
    r"|(\[[^\]]+\]\([^)]+\))"
)


def _dat_font(run, dam=False, nghieng=False, ma=False, co: float | None = None):
    run.font.name = FONT
    # Word cần khai riêng cho bảng mã Đông Á, nếu không dấu tiếng Việt có thể
    # rơi về font thay thế trên một số máy.
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.append(rf)
    for thuoc_tinh in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(thuoc_tinh), FONT)
    run.bold = dam
    run.italic = nghieng
    if co:
        run.font.size = Pt(co)
    if ma:
        run.font.color.rgb = XAM_CHU
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:fill"), XAM_MA)
        rpr.append(shd)


def _viet_inline(para, text: str, co: float | None = None, dam_het=False):
    """Ghi một đoạn văn có định dạng nội tuyến vào paragraph."""
    vi_tri = 0
    for m in _INLINE.finditer(text):
        if m.start() > vi_tri:
            _dat_font(para.add_run(text[vi_tri:m.start()]), dam=dam_het, co=co)
        tho = m.group(0)
        if tho.startswith("`"):
            _dat_font(para.add_run(tho[1:-1]), ma=True, co=co)
        elif tho.startswith("**"):
            _dat_font(para.add_run(tho[2:-2]), dam=True, co=co)
        elif tho.startswith("["):
            chu = tho[1:tho.index("]")]
            lien_ket = tho[tho.index("(") + 1:-1]
            _dat_font(para.add_run(chu), dam=dam_het, co=co)
            # Giữ URL dạng chữ để bản in giấy vẫn tra được nguồn.
            if lien_ket.startswith("http"):
                _dat_font(para.add_run(f" ({lien_ket})"), ma=True,
                          co=(co - 1.5) if co else 9)
        else:
            _dat_font(para.add_run(tho[1:-1]), nghieng=True, co=co)
        vi_tri = m.end()
    if vi_tri < len(text):
        _dat_font(para.add_run(text[vi_tri:]), dam=dam_het, co=co)


def _o_bang(row) -> list[str]:
    tho = row.strip().strip("|")
    return [c.strip() for c in re.split(r"(?<!\\)\|", tho)]


def _la_dong_ngan_cach(dong: str) -> bool:
    return bool(re.fullmatch(r"\s*\|?[\s:|-]+\|?\s*", dong)) and "-" in dong


def _so_trang_chan_trang(section) -> None:
    """Chèn trường PAGE căn giữa ở chân trang."""
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    for loai in ("begin", "instr", "end"):
        if loai == "instr":
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = "PAGE"
        else:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), loai)
        run._r.append(el)
    _dat_font(run)


def _trinh_bay_de_cuong(doc) -> None:
    """Khổ A4, lề 3-2-2-2 cm, số trang; đoạn văn thân bài căn đều, giãn dòng 1,3."""
    for s in doc.sections:
        s.page_width, s.page_height = Cm(21), Cm(29.7)
        s.top_margin = s.bottom_margin = Cm(2)
        s.left_margin, s.right_margin = Cm(3), Cm(2)
        _so_trang_chan_trang(s)
    for p in doc.paragraphs:
        if p.alignment is not None or p.style.name.startswith("Heading"):
            continue
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.3
    for bang in doc.tables:
        for hang in bang.rows:
            for o in hang.cells:
                for p in o.paragraphs:
                    p.paragraph_format.line_spacing = 1.1
                    p.paragraph_format.space_after = Pt(2)


def dung_docx(md: str, co_chu: float, trang_de_cuong: bool = False) -> "Document":
    doc = Document()
    # Trạng thái chế độ đề cương: đang ở trang bìa? đoạn kế tiếp có ngắt trang trước?
    trang = {"bia": trang_de_cuong, "ngat": False}

    def _moi(p):
        """Áp trạng thái trang bìa/ngắt trang cho đoạn vừa tạo."""
        if trang["ngat"]:
            p.paragraph_format.page_break_before = True
            trang["ngat"] = False
        if trang["bia"]:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(12)
        return p

    # Font mặc định cho TOÀN tài liệu.
    for ten_style in ("Normal", "Title", "Heading 1", "Heading 2", "Heading 3",
                      "Heading 4", "List Bullet", "List Number", "Quote"):
        try:
            st = doc.styles[ten_style]
        except KeyError:
            continue
        st.font.name = FONT
        rpr = st.element.get_or_add_rPr()
        rf = rpr.find(qn("w:rFonts"))
        if rf is None:
            rf = OxmlElement("w:rFonts")
            rpr.append(rf)
        for tt in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
            rf.set(qn(tt), FONT)
        if ten_style == "Normal":
            st.font.size = Pt(co_chu)
            st.font.color.rgb = RGBColor(0, 0, 0)

    dong_md = md.splitlines()
    i = 0
    while i < len(dong_md):
        dong = dong_md[i]
        tho = dong.strip()

        if not tho:
            i += 1
            continue

        # Đường kẻ ngang
        if re.fullmatch(r"-{3,}|\*{3,}|_{3,}", tho):
            if trang_de_cuong:
                # Chế độ đề cương: đường kẻ = ngắt trang; hết trang bìa ở đường kẻ đầu tiên.
                trang["bia"] = False
                trang["ngat"] = True
                i += 1
                continue
            p = doc.add_paragraph()
            ppr = p._p.get_or_add_pPr()
            bdr = OxmlElement("w:pBdr")
            bot = OxmlElement("w:bottom")
            bot.set(qn("w:val"), "single")
            bot.set(qn("w:sz"), "6")
            bot.set(qn("w:color"), "BBBBBB")
            bdr.append(bot)
            ppr.append(bdr)
            i += 1
            continue

        # Đề mục
        m = re.match(r"^(#{1,4})\s+(.*)$", tho)
        if m:
            muc = len(m.group(1))
            chu = m.group(2).strip()
            if muc == 1:
                p = _moi(doc.add_paragraph())
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                _viet_inline(p, chu, co=co_chu + 6, dam_het=True)
            else:
                p = _moi(doc.add_heading(level=min(muc, 4)))
                p.text = ""
                _viet_inline(p, chu, co=co_chu + (4 - muc))
                for r in p.runs:
                    r.font.color.rgb = RGBColor(0x14, 0x25, 0x2C)
                    if trang["bia"]:
                        r.font.size = Pt(co_chu + 3)
                        r.bold = True
            i += 1
            continue

        # Bảng
        if tho.startswith("|") and i + 1 < len(dong_md) and _la_dong_ngan_cach(dong_md[i + 1]):
            dau = _o_bang(dong)
            i += 2
            than = []
            while i < len(dong_md) and dong_md[i].strip().startswith("|"):
                than.append(_o_bang(dong_md[i]))
                i += 1
            if trang["ngat"]:
                _moi(doc.add_paragraph())
            bang = doc.add_table(rows=1, cols=len(dau))
            bang.style = "Table Grid"
            for j, o in enumerate(dau):
                cell = bang.rows[0].cells[j]
                cell.text = ""
                _viet_inline(cell.paragraphs[0], o, co=co_chu - 1, dam_het=True)
            for hang in than:
                cells = bang.add_row().cells
                for j, o in enumerate(hang[:len(dau)]):
                    cells[j].text = ""
                    _viet_inline(cells[j].paragraphs[0], o, co=co_chu - 1)
            doc.add_paragraph()
            continue

        # Trích dẫn
        if tho.startswith(">"):
            khoi = []
            while i < len(dong_md) and dong_md[i].strip().startswith(">"):
                khoi.append(dong_md[i].strip().lstrip(">").strip())
                i += 1
            p = _moi(doc.add_paragraph())
            p.paragraph_format.left_indent = Pt(24)
            _viet_inline(p, " ".join(khoi), co=co_chu)
            for r in p.runs:
                r.italic = True
            continue

        # Danh sách
        m = re.match(r"^(\s*)([-*•]|\d+[.)])\s+(.*)$", dong)
        if m:
            thut = len(m.group(1)) // 2
            style = "List Number" if m.group(2)[0].isdigit() else "List Bullet"
            noi_dung = [m.group(3).strip()]
            i += 1
            # gộp dòng tiếp nối (thụt lề, không phải mục mới)
            while (i < len(dong_md) and dong_md[i].strip()
                   and not re.match(r"^(\s*)([-*•]|\d+[.)])\s+", dong_md[i])
                   and dong_md[i].startswith(("  ", "\t"))
                   and not dong_md[i].strip().startswith(("#", "|", ">"))):
                noi_dung.append(dong_md[i].strip())
                i += 1
            try:
                p = _moi(doc.add_paragraph(style=style))
            except KeyError:
                p = _moi(doc.add_paragraph())
            p.paragraph_format.left_indent = Pt(18 + 18 * thut)
            _viet_inline(p, " ".join(noi_dung), co=co_chu)
            continue

        # Đoạn văn thường — gộp các dòng liền nhau
        khoi = [tho]
        i += 1
        while (i < len(dong_md) and dong_md[i].strip()
               and not dong_md[i].strip().startswith(("#", "|", ">", "---"))
               and not re.match(r"^(\s*)([-*•]|\d+[.)])\s+", dong_md[i])):
            khoi.append(dong_md[i].strip())
            i += 1
        p = _moi(doc.add_paragraph())
        if not trang["bia"]:
            p.paragraph_format.space_after = Pt(6)
        _viet_inline(p, " ".join(khoi), co=co_chu)

    if trang_de_cuong:
        _trinh_bay_de_cuong(doc)
    return doc


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Markdown → Word (.docx), font mặc định Times New Roman.")
    ap.add_argument("nguon", type=Path, help="file .md đầu vào")
    ap.add_argument("--ra", type=Path, help="file .docx đầu ra (mặc định cùng tên)")
    ap.add_argument("--co-chu", type=float, default=12.0, help="cỡ chữ thân bài (pt)")
    ap.add_argument("--trang-de-cuong", action="store_true",
                    help="trình bày văn bản nộp Hội đồng: A4, lề 3-2-2-2 cm, căn đều, "
                         "«---» = ngắt trang, phần trước «---» đầu tiên là trang bìa căn giữa")
    a = ap.parse_args(argv)

    if not a.nguon.exists():
        print(f"❌ Không tìm thấy {a.nguon}", file=sys.stderr)
        return 2
    ra = a.ra or a.nguon.with_suffix(".docx")
    ra.parent.mkdir(parents=True, exist_ok=True)

    doc = dung_docx(a.nguon.read_text(encoding="utf-8"), a.co_chu, a.trang_de_cuong)
    doc.save(str(ra))
    print(f"✅ {ra}  ({ra.stat().st_size:,} byte · font {FONT} · {a.co_chu:g}pt)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
