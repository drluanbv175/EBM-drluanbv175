#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vá 22/09/2026 (phản biện vòng 2, review:cong-rut-bai #5, MEDIUM).

`lay_tom_tat()` trước đây chỉ nhận diện thân HTML là lỗi (`"<html" in t[:200]`) — thân LỖI DẠNG
JSON (`{"error":"API rate limit exceeded",...}`) hoặc thân RỖNG của efetch vẫn được đọc là «tóm
tắt đã đọc thành công», nên mất-đo hoàn toàn bị trình bày là ⚪ KHÔNG THẤY bình thường thay vì vào
nhánh `hong`/mã thoát 2 mà bản vá 21/09 dựng riêng cho trường hợp không đọc được.
"""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import kiem_so_lieu as ksl  # noqa: E402


class _FakeResponse:
    def __init__(self, body: bytes):
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        return self._body


def test_than_loi_json_khong_duoc_doc_thanh_tom_tat_da_doc():
    with mock.patch.object(ksl.time, "sleep", lambda *_: None), \
         mock.patch.object(urllib.request, "urlopen",
                            return_value=_FakeResponse(b'{"error":"API rate limit exceeded","api-key":"x"}')):
        ket = ksl.lay_tom_tat("11111111")
    assert ket is None, "bản lỗi JSON hợp lệ không được đọc thành tóm tắt đã đọc"


def test_than_rong_khong_duoc_doc_thanh_tom_tat_da_doc():
    with mock.patch.object(ksl.time, "sleep", lambda *_: None), \
         mock.patch.object(urllib.request, "urlopen", return_value=_FakeResponse(b"")):
        ket = ksl.lay_tom_tat("11111111")
    assert ket is None, "thân rỗng không được đọc thành tóm tắt đã đọc"


def test_than_chi_toan_khoang_trang_cung_bi_coi_la_rong():
    with mock.patch.object(ksl.time, "sleep", lambda *_: None), \
         mock.patch.object(urllib.request, "urlopen", return_value=_FakeResponse(b"   \n  \n")):
        ket = ksl.lay_tom_tat("11111111")
    assert ket is None


def test_tom_tat_that_van_doc_duoc_binh_thuong():
    body = b"1. J Med. 2026.\n\nResult: HR 0.72 (95% CI, 0.60 to 0.86). Conclusion: benefit.\n"
    with mock.patch.object(urllib.request, "urlopen", return_value=_FakeResponse(body)):
        ket = ksl.lay_tom_tat("11111111")
    assert ket is not None and "0.72" in ket


def test_tom_tat_bat_dau_bang_ngoac_nhon_nhung_khong_phai_html_van_qua():
    """Đối chứng chặn quá tay: một tóm tắt (giả định, không thật xảy ra với PubMed) bắt đầu
    bằng '{' nhưng KHÔNG chứa '\"error\"' thì không được coi là lỗi."""
    body = "{1} Ket qua nghien cuu: HR 0.72 (95% CI 0.60-0.86).".encode("utf-8")
    with mock.patch.object(urllib.request, "urlopen", return_value=_FakeResponse(body)):
        ket = ksl.lay_tom_tat("11111111")
    assert ket is not None
