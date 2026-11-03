# -*- coding: utf-8 -*-
"""PDF GIẢ HỢP LỆ cho kiểm thử ngoại tuyến (02/11/2026).

Vì sao có: tầng Unpaywall của `gom_toan_van_dashboard.py` nay đọc chữ PDF (pypdf) để kiểm định danh trước khi ghi kho. Chuỗi
`b"%PDF-1.7" + rác` mà các test cũ dùng không phải PDF — pypdf không đọc được ⇒ cổng (đúng) từ chối. Fixture phải là PDF THẬT
mang tiêu đề/DOI của bài, nên test và chốt hồi quy dựng PDF bằng hàm này (không nới cổng).

Chỉ dùng thư viện chuẩn; phông Helvetica chuẩn của PDF ⇒ chỉ ký tự Latin-1 (đủ cho tiêu đề tiếng Anh, DOI).
"""
from __future__ import annotations

import textwrap


def _thoat(s: str) -> str:
    return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def pdf_co_chu(*trang: str, rong: int = 90) -> bytes:
    """PDF nhiều trang (mỗi đối số một trang), chữ ngắt dòng `rong` ký tự; bảng xref đúng vị trí byte."""
    if not trang:
        trang = ("",)
    n = len(trang)
    doi_tuong = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        ("<< /Type /Pages /Kids [%s] /Count %d >>" % (" ".join("%d 0 R" % (4 + 2 * i) for i in range(n)), n)).encode(),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
    ]
    for i, chu in enumerate(trang):
        dong = textwrap.wrap(chu, rong) or [""]
        noi_dung = ("BT /F1 10 Tf 12 TL 40 800 Td " + " ".join("(%s) Tj T*" % _thoat(d) for d in dong) + " ET").encode("latin-1")
        doi_tuong.append(("<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 3 0 R >> >> "
                          "/Contents %d 0 R >>" % (5 + 2 * i)).encode())
        doi_tuong.append(b"<< /Length %d >>\nstream\n" % len(noi_dung) + noi_dung + b"\nendstream")
    ra = bytearray(b"%PDF-1.4\n")
    vi_tri = []
    for so, dt in enumerate(doi_tuong, 1):
        vi_tri.append(len(ra))
        ra += b"%d 0 obj\n" % so + dt + b"\nendobj\n"
    xref = len(ra)
    ra += b"xref\n0 %d\n0000000000 65535 f \n" % (len(doi_tuong) + 1)
    ra += b"".join(b"%010d 00000 n \n" % v for v in vi_tri)
    ra += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(doi_tuong) + 1, xref)
    return bytes(ra)
