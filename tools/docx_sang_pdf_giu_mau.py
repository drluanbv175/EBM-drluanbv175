#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
docx_sang_pdf_giu_mau.py — Dựng PDF GIỮ MÀU từ bản Word của một lần cập nhật chứng cứ.

VÌ SAO KHÔNG DÙNG THẲNG pandoc: pandoc chuyển .docx sang HTML thì **bỏ hết màu nền ô**
(shading). Bản Word tô màu huy hiệu mức chứng cứ và quyết định theo bảng màu Evidence
Workbench — xanh lá = Cao/Áp dụng ngay, cam = Trung bình-Thấp/Cân nhắc, đỏ = Rất
thấp/Chưa đủ. Mất màu là mất đúng thứ giúp bác sĩ nhìn lướt bắt được mức khuyến cáo.

CÁCH LÀM: đọc màu TỪ CHÍNH file .docx (`w:shd/@w:fill`) rồi bơm vào bảng HTML mà pandoc
vừa dựng, theo đúng thứ tự bảng → hàng → ô. Giữ nguyên tắc "mọi bản phái sinh sinh ra từ
cùng một nguồn" — không dựng lại tài liệu từ dữ liệu, nên không có đường nào làm hai bản
lệch nhau.

IN PDF: Chrome headless (`--print-to-pdf`). Đã kiểm: Chrome giữ nguyên màu nền, không cần
cờ đặc biệt. macOS này KHÔNG có LibreOffice/Word-tự-động, và pandoc→PDF qua LaTeX cũng
không giữ được shading, nên Chrome là đường duy nhất giữ đúng màu.

Chạy:  python3 tools/docx_sang_pdf_giu_mau.py <file.docx>
       python3 tools/docx_sang_pdf_giu_mau.py <file.docx> --html-co-san <file.html>
"""
from __future__ import annotations

import argparse
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

# Windows: stdout mặc định cp1252 → mọi print() tiếng Việt ném UnicodeEncodeError.
# Vá 12/08/2026, cùng đợt với build_dashboard_docx.py và build_dashboard_from_data.py:
# bước ⑤ của dây chuyền bị bỏ qua với thông báo 'charmap codec can't encode ơ'
# (chữ 'ơ') — nghĩa là công cụ chết TRƯỚC khi kịp thử tìm trình duyệt, nên bác sĩ
# tưởng máy thiếu Chrome trong khi Chrome vẫn có sẵn.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# Chrome trên macOS. Edge dùng được y hệt nếu máy không có Chrome.
TRINH_DUYET = [
    # macOS
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # da-nen: bo-qua (dò theo TỒN TẠI file; danh sách đã gồm Windows — vá 12/08)
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",  # da-nen: bo-qua (dò theo TỒN TẠI file; danh sách đã gồm Windows — vá 12/08)
    "/Applications/Chromium.app/Contents/MacOS/Chromium",  # da-nen: bo-qua (dò theo TỒN TẠI file; danh sách đã gồm Windows — vá 12/08)
    # Windows — VÁ 12/08/2026. Trước đó danh sách CHỈ có macOS, và nhánh dự phòng
    # `shutil.which` lại dò tên Unix ("chromium"/"google-chrome"), nên trên Windows
    # bước ⑤ KHÔNG BAO GIỜ chạy được dù máy có sẵn cả Chrome lẫn Edge. Đã kiểm trên
    # máy Windows ngày 12/08: cả hai đường dẫn dưới đây đều tồn tại thật.
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

CSS_IN = """
<style>
  /* Ép trình duyệt in cả màu nền — mặc định nhiều nơi bỏ qua để tiết kiệm mực */
  *, *::before, *::after {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }
  @page { size: A4; margin: 14mm 12mm; }
  body { font-family: "Times New Roman", Times, serif; font-size: 11.5pt; line-height: 1.45; }
  table { border-collapse: collapse; width: 100%; page-break-inside: auto; }
  tr { page-break-inside: avoid; }
  td, th { border: 1px solid #b9bfd0; padding: 5px 7px; vertical-align: top; }
  h1, h2, h3 { page-break-after: avoid; }
  /* Bảng dài không bị cắt giữa dòng khi sang trang */
  thead { display: table-header-group; }
</style>
"""


def tim_trinh_duyet() -> str | None:
    """Tìm một trình duyệt nhân Chromium để in PDF (Chrome/Edge/Chromium).

    Dò theo 3 lớp cho chạy được trên CẢ macOS lẫn Windows:
      1) các đường dẫn cài đặt chuẩn (hằng TRINH_DUYET);
      2) bản cài theo NGƯỜI DÙNG trên Windows (%LOCALAPPDATA%) — Chrome rất hay
         nằm ở đây khi máy không cho cài vào Program Files, như máy công sở;
      3) PATH, với đủ tên gọi của cả hai hệ (Windows dùng chrome/msedge, Unix
         dùng chromium/google-chrome).
    """
    for p in TRINH_DUYET:
        if pathlib.Path(p).exists():
            return p

    localappdata = os.environ.get("LOCALAPPDATA")
    if localappdata:
        for duoi in (r"Google\Chrome\Application\chrome.exe",
                     r"Microsoft\Edge\Application\msedge.exe",
                     r"Chromium\Application\chrome.exe"):
            p = pathlib.Path(localappdata) / duoi
            if p.exists():
                return str(p)

    for ten in ("chrome", "msedge", "chromium", "google-chrome", "chromium-browser"):
        found = shutil.which(ten)
        if found:
            return found
    return None


def mau_tung_o(docx_path: pathlib.Path) -> list[list[list[str | None]]]:
    """Trả về màu nền theo cấu trúc [bảng][hàng][ô]; None nghĩa là không tô."""
    import docx  # nạp muộn để script vẫn chạy --help khi thiếu thư viện

    tai_lieu = docx.Document(str(docx_path))
    ket_qua: list[list[list[str | None]]] = []
    for bang in tai_lieu.tables:
        hang_list = []
        for hang in bang.rows:
            o_list: list[str | None] = []
            for o in hang.cells:
                fill = None
                for shd in o._tc.iter(f"{NS}shd"):
                    f = shd.get(f"{NS}fill")
                    if f and f.lower() not in ("auto", "ffffff"):
                        fill = f
                        break
                o_list.append(fill)
            hang_list.append(o_list)
        ket_qua.append(hang_list)
    return ket_qua


def bom_mau(html: str, mau: list[list[list[str | None]]]) -> tuple[str, int]:
    """Gắn style nền cho từng <td>/<th> theo đúng thứ tự bảng → hàng → ô của .docx."""
    da_bom = 0
    bang_html = list(re.finditer(r"<table\b.*?</table>", html, re.S | re.I))
    if len(bang_html) != len(mau):
        print(f"  ! số bảng lệch: HTML {len(bang_html)} vs Word {len(mau)} — "
              "chỉ bơm cho phần khớp được", file=sys.stderr)

    ra: list[str] = []
    vi_tri = 0
    for i, m in enumerate(bang_html):
        ra.append(html[vi_tri:m.start()])
        khoi = m.group(0)
        if i < len(mau):
            hang_html = list(re.finditer(r"<tr\b.*?</tr>", khoi, re.S | re.I))
            moi_khoi: list[str] = []
            vt = 0
            for j, hm in enumerate(hang_html):
                moi_khoi.append(khoi[vt:hm.start()])
                hang = hm.group(0)
                if j < len(mau[i]):
                    o_html = list(re.finditer(r"<(td|th)\b([^>]*)>", hang, re.I))
                    moi_hang: list[str] = []
                    v2 = 0
                    for k, om in enumerate(o_html):
                        moi_hang.append(hang[v2:om.start()])
                        fill = mau[i][j][k] if k < len(mau[i][j]) else None
                        if fill:
                            thuoc_tinh = om.group(2)
                            style = f"background-color:#{fill};"
                            if re.search(r'style="', thuoc_tinh, re.I):
                                thuoc_tinh = re.sub(r'style="', f'style="{style}',
                                                    thuoc_tinh, count=1, flags=re.I)
                            else:
                                thuoc_tinh += f' style="{style}"'
                            moi_hang.append(f"<{om.group(1)}{thuoc_tinh}>")
                            da_bom += 1
                        else:
                            moi_hang.append(om.group(0))
                        v2 = om.end()
                    moi_hang.append(hang[v2:])
                    hang = "".join(moi_hang)
                moi_khoi.append(hang)
                vt = hm.end()
            moi_khoi.append(khoi[vt:])
            khoi = "".join(moi_khoi)
        ra.append(khoi)
        vi_tri = m.end()
    ra.append(html[vi_tri:])
    return "".join(ra), da_bom


def main() -> int:
    ap = argparse.ArgumentParser(description="Dựng PDF giữ màu từ bản Word")
    ap.add_argument("docx", help="đường dẫn file .docx")
    ap.add_argument("--html-co-san", help="dùng bản HTML đã có thay vì gọi lại pandoc")
    ap.add_argument("--ra", help="đường dẫn PDF đầu ra (mặc định: cùng tên, đuôi .pdf)")
    a = ap.parse_args()

    dx = pathlib.Path(a.docx).resolve()
    if not dx.exists():
        print(f"✗ không thấy {dx}", file=sys.stderr)
        return 2
    ra_pdf = pathlib.Path(a.ra).resolve() if a.ra else dx.with_suffix(".pdf")

    trinh_duyet = tim_trinh_duyet()
    if not trinh_duyet:
        print("✗ không thấy Chrome/Edge/Chromium — không in được PDF giữ màu.\n"
              "  Ba sản phẩm kia (dashboard · bản đọc · Word) KHÔNG bị ảnh hưởng.",
              file=sys.stderr)
        return 3

    # 1) HTML nền: dùng bản có sẵn, hoặc gọi pandoc
    if a.html_co_san and pathlib.Path(a.html_co_san).exists():
        html = pathlib.Path(a.html_co_san).read_text("utf-8", errors="replace")
    else:
        pandoc = shutil.which("pandoc")
        if not pandoc:
            # NHÁNH DỰ PHÒNG (12/08/2026) — xem docx_sang_html_khong_pandoc.py.
            # Trước đây thiếu pandoc là dừng hẳn, nên máy Windows không bao giờ
            # in được PDF giữ màu dù có sẵn Chrome/Edge.
            try:
                sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
                from docx_sang_html_khong_pandoc import dung_html_tu_docx

                with tempfile.TemporaryDirectory() as tmp:
                    tam = pathlib.Path(tmp) / "x.html"
                    dung_html_tu_docx(dx, tam, tieu_de=dx.stem)
                    html = tam.read_text("utf-8", errors="replace")
            except Exception as e:  # noqa: BLE001
                print(f"✗ thiếu pandoc và nhánh dự phòng cũng lỗi: {e}", file=sys.stderr)
                return 3
        else:
            with tempfile.TemporaryDirectory() as tmp:
                tam = pathlib.Path(tmp) / "x.html"
                r = subprocess.run([pandoc, "-f", "docx", "-t", "html5", "--standalone",
                                    "--embed-resources", str(dx), "-o", str(tam)],
                                   capture_output=True, text=True)
                if r.returncode != 0:
                    print(f"✗ pandoc lỗi: {r.stderr.strip()[:160]}", file=sys.stderr)
                    return 3
                html = tam.read_text("utf-8", errors="replace")

    # 2) Bơm màu đọc từ chính .docx
    mau = mau_tung_o(dx)
    tong_o_mau = sum(1 for b in mau for h in b for o in h if o)
    html, da_bom = bom_mau(html, mau)
    print(f"  màu trong Word: {tong_o_mau} ô · bơm được vào HTML: {da_bom} ô")

    # 3) Chèn CSS in (đặt cuối <head> để thắng CSS sẵn có)
    if "</head>" in html:
        html = html.replace("</head>", CSS_IN + "</head>", 1)
    else:
        html = CSS_IN + html

    # 4) In PDF
    with tempfile.TemporaryDirectory() as tmp:
        nguon = pathlib.Path(tmp) / "in.html"
        nguon.write_text(html, encoding="utf-8")
        r = subprocess.run([trinh_duyet, "--headless", "--disable-gpu",
                            "--no-pdf-header-footer", "--print-background",
                            f"--print-to-pdf={ra_pdf}", f"file://{nguon}"],
                           capture_output=True, text=True, timeout=300)
    if not ra_pdf.exists():
        print(f"✗ không in được PDF: {r.stderr.strip()[:200]}", file=sys.stderr)
        return 3
    print(f"  ✓ {ra_pdf.name} ({ra_pdf.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
