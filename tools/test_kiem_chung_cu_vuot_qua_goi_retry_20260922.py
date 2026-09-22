#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vá 22/09/2026 (phản biện vòng 2, review:cong-rut-bai #1, phần thứ hai).

`_goi()` trước đây chỉ retry khi có EXCEPTION mạng — một phản hồi HTTP 200 với JSON HỢP LỆ
nhưng là bản LỖI (`{"error": "API rate limit exceeded", ...}`) không ném exception nào, nên
`_goi()` trả ngay bản lỗi đó sau ĐÚNG 1 lần hỏi, không có cơ hội thử lại như mọi lỗi mạng khác
— dù rate-limit thoáng qua hoàn toàn có thể tự hết sau vài giây.
"""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parent
import importlib.util  # noqa: E402

spec = importlib.util.spec_from_file_location("kcv_goi_retry_test", TOOLS / "kiem_chung_cu_vuot_qua.py")
kcv = importlib.util.module_from_spec(spec)
sys.modules["kcv_goi_retry_test"] = kcv
spec.loader.exec_module(kcv)


class _FakeResponse:
    def __init__(self, body: bytes):
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        return self._body


def test_json_loi_duoc_retry_roi_thanh_cong():
    """Hai lần đầu trả bản lỗi, lần ba trả kết quả thật — phải LẤY ĐƯỢC kết quả thật,
    không dừng lại ở lần đầu tiên."""
    goi = {"n": 0}
    body_loi = b'{"error":"API rate limit exceeded"}'
    body_ok = b'{"linksets": [{"linksetdbs": [{"links": ["99999999"]}]}]}'

    def urlopen_gia(req, timeout=0):
        goi["n"] += 1
        return _FakeResponse(body_loi if goi["n"] < 3 else body_ok)

    with mock.patch.object(kcv.time, "sleep", lambda *_: None), \
         mock.patch.object(urllib.request, "urlopen", urlopen_gia):
        ket_qua = kcv._goi("http://example.invalid/elink")
    assert ket_qua == {"linksets": [{"linksetdbs": [{"links": ["99999999"]}]}]}
    assert goi["n"] == 3, "phải thử lại khi gặp bản lỗi JSON hợp lệ, không dừng ở lần đầu"


def test_json_loi_lien_tuc_ca_ba_lan_van_tra_none_khong_bia():
    goi = {"n": 0}
    body_loi = b'{"error":"API rate limit exceeded"}'

    def urlopen_gia(req, timeout=0):
        goi["n"] += 1
        return _FakeResponse(body_loi)

    with mock.patch.object(kcv.time, "sleep", lambda *_: None), \
         mock.patch.object(urllib.request, "urlopen", urlopen_gia):
        ket_qua = kcv._goi("http://example.invalid/elink")
    assert ket_qua is None, "hỏng cả 3 lần ⇒ None (chưa hỏi được), không được bịa kết quả"
    assert goi["n"] == 3


def test_json_hop_le_khong_co_khoa_error_khong_bi_retry_thua():
    goi = {"n": 0}
    body_ok = b'{"linksets": []}'

    def urlopen_gia(req, timeout=0):
        goi["n"] += 1
        return _FakeResponse(body_ok)

    with mock.patch.object(kcv.time, "sleep", lambda *_: None), \
         mock.patch.object(urllib.request, "urlopen", urlopen_gia):
        ket_qua = kcv._goi("http://example.invalid/elink")
    assert ket_qua == {"linksets": []}
    assert goi["n"] == 1, "JSON hợp lệ không có khoá error ⇒ không được retry thừa"


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__, "-v"]))
