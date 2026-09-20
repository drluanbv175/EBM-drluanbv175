#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy phát hiện MEDIUM của Workflow đối kháng đa-agent 2026-09-04 (task #64):
`tools/chu_trinh_chung_cu.py` bước ⑤ — coi MỌI mã thoát 1 của
`dang_ky_chu_de.py --mau-thuan` là "đã tìm thấy mâu thuẫn lâm sàng thật", trong
khi mã đó mang HAI NGHĨA HOÀN TOÀN KHÁC NHAU:

  (a) tìm thấy mâu thuẫn thật giữa hai bản cùng chủ đề (dòng cuối `main()` của
      `dang_ky_chu_de.py`, sau khi đã quét được kho);
  (b) KHÔNG QUÉT ĐƯỢC vì thiếu `EBM-Dashboards/tools/verify_dashboard.py`
      (`FileNotFoundError` bắt ngay đầu `main()`, in dòng "⚪ Không kiểm được
      trên máy này" rồi CŨNG trả về mã 1).

Xác nhận bằng thực nghiệm TRÊN CHÍNH BẢN SAO TRẦN NÀY (nơi `EBM-Dashboards/`
thật sự không tồn tại — không phải kịch bản dựng): chạy
`python tools/chu_trinh_chung_cu.py --nhanh` in ra dòng "🔴 Có mục hai bản
CÙNG CHỦ ĐỀ nói ngược nhau" ở mục ⑤ của tổng kết — một báo động giả về nội
dung LÂM SÀNG trong khi sự thật chỉ là THIẾU NGUYÊN LIỆU trên máy. Cùng lớp
lỗi mà chính bước ③④ của file này ĐÃ xử lý đúng (đọc `out` để phân biệt lý
do thay vì đưa một lời khuyên chung, xem chú thích SỬA 13/08/2026 tại đó) —
nhưng bước ⑤ chưa từng nhận được cùng cách xử lý.

Bản vá đọc `out` để phân biệt: khớp chuỗi "Không kiểm được trên máy này" (dòng
đầu ra ổn định của `dang_ky_chu_de.py::quet_kho()` khi thiếu nguyên liệu) →
báo đúng "chưa quét được", KHÔNG báo "đã tìm thấy mâu thuẫn".

Nguyên tắc viết test: mock `subprocess.run` để kiểm soát output/mã thoát của
TỪNG bước con theo đúng cách `chay()` gọi thật, rồi gọi THẲNG `main()` — không
grep chuỗi trong mã nguồn, không phụ thuộc `EBM-Dashboards/` có tồn tại hay
không trên máy chạy test.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chu_trinh_chung_cu as ctcc  # noqa: E402


class _FakeProc:
    def __init__(self, returncode: int, stdout: str = "", stderr: str = ""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _lam_gia_subprocess(dang_ky_chu_de_rc: int, dang_ky_chu_de_out: str):
    """Sinh side_effect cho subprocess.run: mọi bước con khác đều 'sạch' (rc=0),
    CHỈ riêng dang_ky_chu_de.py --mau-thuan (bước ⑤) được điều khiển theo tham số —
    cô lập đúng nhánh đang kiểm, không phụ thuộc hành vi thật của 5 bước còn lại."""

    def _goi(cmd, **kwargs):
        ten_file = str(cmd[1]) if len(cmd) > 1 else ""
        if "dang_ky_chu_de.py" in ten_file:
            return _FakeProc(dang_ky_chu_de_rc, stdout=dang_ky_chu_de_out)
        # Mọi bước con khác: rc=0, không có nội dung đặc biệt.
        return _FakeProc(0, stdout="")

    return _goi


class TestKhongQuetDuocKhongBiBaoThanhMauThuanThat:
    """★★ Ca chính — rc=1 vì THIẾU NGUYÊN LIỆU (thông điệp "Không kiểm được
    trên máy này") phải được báo ĐÚNG bản chất, KHÔNG được gộp vào lời cảnh
    báo "đã tìm thấy mâu thuẫn lâm sàng"."""

    def test_khong_quet_duoc_bao_dung_khong_bao_mau_thuan_gia(self, capsys):
        out_gia = ("⚪ Không kiểm được trên máy này: thiếu "
                   "/fake/EBM-Dashboards/tools/verify_dashboard.py — EBM-Dashboards "
                   "nằm ngoài git (bản sao trần). Chạy trên máy có đủ cây OneDrive.")
        with mock.patch.object(sys, "argv", ["chu_trinh_chung_cu.py", "--nhanh"]), \
             mock.patch.object(ctcc.subprocess, "run",
                                side_effect=_lam_gia_subprocess(1, out_gia)):
            ma_thoat = ctcc.main()
        in_ra = capsys.readouterr().out
        assert "Chưa quét được mâu thuẫn hai bản" in in_ra
        assert "🔴 Có mục hai bản CÙNG CHỦ ĐỀ nói ngược nhau" not in in_ra
        assert ma_thoat == 1  # vẫn là "có việc cần bác sĩ", chỉ đổi NỘI DUNG lời báo


class TestMauThuanThatVanDuocBaoDungNhuCu:
    """★★ Đối chứng bắt buộc — mâu thuẫn THẬT (rc=1, không có dấu hiệu "Không
    kiểm được") vẫn phải được báo ĐÚNG như hành vi trước bản vá."""

    def test_mau_thuan_that_van_bao_dung(self, capsys):
        out_that = ("🔴 3 MỤC HAI BẢN NÓI NGƯỢC NHAU — cùng PMID, khác quyết định\n"
                    "  ▸ COPD_TongHop: bản A (2026-06-10) ⟷ bản B (2026-08-05)")
        with mock.patch.object(sys, "argv", ["chu_trinh_chung_cu.py", "--nhanh"]), \
             mock.patch.object(ctcc.subprocess, "run",
                                side_effect=_lam_gia_subprocess(1, out_that)):
            ma_thoat = ctcc.main()
        in_ra = capsys.readouterr().out
        assert "🔴 Có mục hai bản CÙNG CHỦ ĐỀ nói ngược nhau" in in_ra
        assert "Chưa quét được mâu thuẫn hai bản" not in in_ra
        assert ma_thoat == 1


class TestKhongMauThuanKhongBaoGiViec:
    """Đối chứng — rc=0 (không mâu thuẫn, quét được bình thường) không được
    sinh ra bất kỳ việc nào ở mục ⑤."""

    def test_rc0_khong_sinh_viec(self, capsys):
        with mock.patch.object(sys, "argv", ["chu_trinh_chung_cu.py", "--nhanh"]), \
             mock.patch.object(ctcc.subprocess, "run",
                                side_effect=_lam_gia_subprocess(0, "🟢 KHÔNG có mục nào hai bản nói ngược nhau.")):
            ma_thoat = ctcc.main()
        in_ra = capsys.readouterr().out
        assert "🔴 Có mục hai bản CÙNG CHỦ ĐỀ nói ngược nhau" not in in_ra
        assert "Chưa quét được mâu thuẫn hai bản" not in in_ra
        assert ma_thoat == 0
