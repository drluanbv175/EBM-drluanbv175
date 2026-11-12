# -*- coding: utf-8 -*-
"""Chốt số của tóm tắt máy với dấu cách Unicode làm dấu nghìn (13/11/2026) — `tom_tat_endnote_vi._cac_so`.

Sự cố đo 13/11/2026: abstract PubMed efetch của PMID 35219395 viết «18 152 participants» với U+2008 (PUNCTUATION SPACE)
làm dấu nghìn. Tóm tắt máy chép đúng U+2008 ⇒ bị tách thành 18 và 152; abstract trong EndNote (recNum 9342) lưu dấu
cách thường ⇒ «18152». `nap_endnote_chu_de.py --tom-tat-vi --ap-dung` báo «số không có trong abstract gốc» và không in
tóm tắt. Nay mọi dấu cách loại Zs được đổi về dấu cách thường TRƯỚC khi tách số, ở CẢ hai phía. Luật «số phải có
nguyên văn trong gốc» KHÔNG nới: số lệch thật vẫn bị bắt.

Mã nguồn test viết dấu cách đặc biệt bằng mã thoát \\uXXXX, không viết ký tự trần (ký tự vô hình dễ gõ nhầm).
Ngoại tuyến hoàn toàn, văn bản là chuỗi giả.
"""
from __future__ import annotations

import importlib.util
import sys
import unicodedata
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap(rel: str, ten: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / rel)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


tt = _nap("tools/tom_tat_endnote_vi.py", "_tt_dau_cach_unicode")

PUNCT = "\u2008"   # PUNCTUATION SPACE — ký tự gây sự cố 13/11
HEP = "\u202f"     # NARROW NO-BREAK SPACE
MONG = "\u2009"    # THIN SPACE
NBSP = "\u00a0"    # NO-BREAK SPACE


def _goc(dau: str) -> str:
    return f"Methods: We followed 18{dau}152 participants for 5 years. Results: HR 0.85 (95% CI 0.71-0.93)."


def _tom(dau: str) -> dict:
    return {"thiet_ke": f"Đoàn hệ, n = 18{dau}152, theo dõi 5 năm", "ket_qua": "HR 0.85 (KTC 95% 0.71–0.93)"}


def test_tom_tat_u2008_khop_goc_dau_cach_thuong():
    """Đúng ca 13/11: tóm tắt chép U+2008 từ efetch, abstract EndNote lưu dấu cách thường."""
    assert tt._cac_so(f"18{PUNCT}152") == {"18152"}, "U+2008 giữa hai nhóm số phải là dấu nghìn như dấu cách thường"
    assert tt.so_khong_khop(_tom(PUNCT), _goc(" ")) == []
    tom, lech = tt.kiem_tom_tat_may(_tom(PUNCT), _goc(" "))
    assert lech == [] and tom is not None, f"tóm tắt chép đúng số bị chặn oan: {lech}"


def test_tom_tat_dau_cach_thuong_khop_goc_u2008():
    """Chiều ngược: văn bản gốc (vd toàn văn/abstract efetch) giữ U+2008, tóm tắt gõ dấu cách thường."""
    assert tt.so_khong_khop(_tom(" "), _goc(PUNCT)) == []
    tom, lech = tt.kiem_tom_tat_may(_tom(" "), _goc(PUNCT))
    assert lech == [] and tom is not None, f"tóm tắt chép đúng số bị chặn oan: {lech}"


@pytest.mark.parametrize("tom_dau, goc_dau", [(HEP, " "), (" ", HEP), (HEP, PUNCT), (MONG, NBSP), (NBSP, "\u3000")])
def test_moi_dau_cach_zs_so_cung_mot_dang(tom_dau, goc_dau):
    assert tt.so_khong_khop(_tom(tom_dau), _goc(goc_dau)) == [], \
        f"U+{ord(tom_dau):04X} (tóm tắt) vs U+{ord(goc_dau):04X} (gốc) phải so cùng một dạng"


@pytest.mark.parametrize("dau", [PUNCT, HEP, " "])
def test_so_lech_that_van_bi_bat(dau):
    """Không nới luật: số không có nguyên văn trong gốc vẫn chặn, dù viết bằng dấu cách nào."""
    goc = _goc(" ")
    assert tt.so_khong_khop({"thiet_ke": f"n = 18{dau}125"}, goc) == ["18125"], "đảo chữ số nhóm nghìn phải bị bắt"
    assert tt.so_khong_khop({"ket_qua": f"HR 0.77; n = 18{dau}152"}, goc) == ["0.77"], "số sai cạnh số đúng phải bị bắt"
    tom, lech = tt.kiem_tom_tat_may({"thiet_ke": f"n = 18{dau}125"}, goc)
    assert tom is None and lech == ["18125"]


def test_gop_nham_hai_so_rieng_cua_goc_van_bi_bat():
    """Gốc có 18 và 152 là HAI số riêng; tóm tắt ghép thành «18 152» (U+2008) ⇒ 18152 không có trong gốc ⇒ chặn."""
    goc = "Across 18 sites, 152 deaths occurred."
    assert tt.so_khong_khop({"ket_qua": f"18{PUNCT}152 ca tử vong"}, goc) == ["18152"]


def test_bay_nam_va_dau_phay_liet_ke_giu_hanh_vi_cu_cho_moi_dau_cach():
    """Hành vi cũ giữ nguyên, chỉ mở rộng tập ký tự: năm 4 chữ số + dấu cách + 3 chữ số vẫn bị gộp (bẫy đã biết);
    dấu phẩy liệt kê kèm khoảng trắng không phải dấu nghìn; dấu phẩy thập phân không chuẩn hoá."""
    for dau in (" ", PUNCT, HEP, NBSP):
        assert tt._cac_so(f"năm 2024{dau}120 ca") == {"2024120"}, f"bẫy năm đổi hành vi với U+{ord(dau):04X}"
        assert tt._cac_so(f"1,{dau}234") == {"1", "234"}, f"dấu phẩy liệt kê + U+{ord(dau):04X} bị gộp nhầm"
        assert tt._cac_so(f"18{dau}1520") == {"18", "1520"}, "nhóm sau dấu cách không đủ đúng 3 chữ số thì không gộp"
    assert tt._cac_so("9,1%") == {"9", "1"}, "dấu phẩy thập phân vẫn KHÔNG được chuẩn hoá"


def test_lop_dau_cach_phu_dung_moi_ky_tu_zs():
    """Lớp ký tự phải phủ ĐÚNG mọi ký tự loại Zs trừ dấu cách thường — bản Unicode mới thêm ký tự Zs thì test đỏ."""
    zs = {chr(i) for i in range(sys.maxunicode + 1) if unicodedata.category(chr(i)) == "Zs"} - {" "}
    khop = {c for c in map(chr, range(sys.maxunicode + 1)) if tt._DAU_CACH_UNICODE.fullmatch(c)}
    assert khop == zs, f"thiếu: {sorted(hex(ord(c)) for c in zs - khop)} · thừa: {sorted(hex(ord(c)) for c in khop - zs)}"
