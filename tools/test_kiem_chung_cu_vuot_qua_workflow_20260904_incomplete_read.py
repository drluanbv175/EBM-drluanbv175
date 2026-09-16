#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy phát hiện MEDIUM của Workflow đối kháng đa-agent 2026-09-04 (task #62):
`tools/kiem_chung_cu_vuot_qua.py::_goi()` — lưới bắt lỗi mạng thiếu
`http.client.HTTPException`/`OSError`, khác sibling đã vá của chính công cụ này
(`tools/kiem_so_lieu.py::lay_tom_tat()`, sửa 15/08/2026 cho ĐÚNG lỗi này).

Cơ chế lỗi (xác nhận bằng thực nghiệm — không suy đoán): `http.client.IncompleteRead`
là con của `http.client.HTTPException`, KHÔNG phải con của `urllib.error.URLError`
hay `OSError`. `_goi()` cũ chỉ bắt `(urllib.error.URLError, ValueError,
json.JSONDecodeError)` — một `IncompleteRead` nổ TRONG `r.read()` (giữa chừng tải
JSON esummary/elink) sẽ THOÁT lưới bắt hoàn toàn.

`_goi()` được gọi từ `tong_quan_moi_hon()`, và `main()` gọi `tong_quan_moi_hon()`
trong một vòng `for k, pm in enumerate(ds, 1):` KHÔNG có try/except nào bọc quanh
— nên một IncompleteRead ở PMID thứ N sẽ giết TRỌN lượt dò còn lại (N+1..cuối),
đúng sự cố đã xảy ra thật ngày 15/08/2026 cho 234 mục ở `lay_tom_tat()`.

Bản vá thêm `http.client.HTTPException, OSError` vào except clause của `_goi()`,
đúng khuôn sibling đã vá.

Nguyên tắc viết test: mock `urllib.request.urlopen` để `.read()` ném
`http.client.IncompleteRead` thật (không phải Exception giả), gọi THẲNG `_goi()`,
không grep chuỗi trong mã nguồn.
"""
from __future__ import annotations

import http.client
import sys
import urllib.request
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kiem_chung_cu_vuot_qua as kcv  # noqa: E402


class _RaiseOnReadResponse:
    """Context manager mô phỏng response HTTP mà .read() nổ IncompleteRead —
    đúng vị trí lỗi thật đã xảy ra 15/08 (giữa chừng tải, không phải lúc mở kết nối)."""

    def __init__(self, loi: Exception):
        self._loi = loi

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        raise self._loi


class TestIncompleteReadKhongLamChetCaLuot:
    """★★ Ca chính — `_goi()` phải bắt được `http.client.IncompleteRead` và
    trả None («chưa hỏi được»), KHÔNG được để lỗi thoát ra ngoài giết cả vòng
    lặp `main()` đang dò nhiều PMID."""

    def test_incomplete_read_tra_ve_none_khong_nem_loi(self):
        loi = http.client.IncompleteRead(partial=b"", expected=10)
        with mock.patch.object(kcv.time, "sleep", lambda *_: None), \
             mock.patch.object(urllib.request, "urlopen",
                                return_value=_RaiseOnReadResponse(loi)):
            ket_qua = kcv._goi("http://example.invalid/elink")
        assert ket_qua is None

    def test_os_error_tra_ve_none_khong_nem_loi(self):
        """★★ Đối chứng — OSError trần (vd mất kết nối giữa chừng) cũng phải
        được lưới bắt, không chỉ riêng HTTPException."""
        with mock.patch.object(kcv.time, "sleep", lambda *_: None), \
             mock.patch.object(urllib.request, "urlopen",
                                return_value=_RaiseOnReadResponse(OSError("mất kết nối"))):
            ket_qua = kcv._goi("http://example.invalid/elink")
        assert ket_qua is None

    def test_tong_quan_moi_hon_khong_chet_khi_goi_that_bai(self):
        """★★ Đối chứng quan trọng nhất — hàm gọi TỪ main() (`tong_quan_moi_hon`)
        cũng phải sống sót, vì chính main() KHÔNG bọc try/except quanh lời gọi
        này (xác nhận bằng đọc mã: vòng lặp `for k, pm in enumerate(ds, 1):`
        gọi thẳng, không try/except)."""
        loi = http.client.IncompleteRead(partial=b"", expected=10)
        with mock.patch.object(kcv.time, "sleep", lambda *_: None), \
             mock.patch.object(urllib.request, "urlopen",
                                return_value=_RaiseOnReadResponse(loi)):
            ket_qua = kcv.tong_quan_moi_hon("30267080", 2018, None)
        assert ket_qua == []


class TestPhanLoaiKieuLoiThucNghiem:
    """Xác nhận bằng thực nghiệm (không suy đoán) quan hệ kế thừa giữa các lớp
    lỗi — đây chính là lý do lưới bắt cũ bị thủng."""

    def test_incomplete_read_khong_phai_con_urlerror(self):
        import urllib.error
        assert not issubclass(http.client.IncompleteRead, urllib.error.URLError)

    def test_incomplete_read_la_con_httpexception(self):
        assert issubclass(http.client.IncompleteRead, http.client.HTTPException)

    def test_incomplete_read_khong_phai_con_oserror(self):
        assert not issubclass(http.client.IncompleteRead, OSError)
