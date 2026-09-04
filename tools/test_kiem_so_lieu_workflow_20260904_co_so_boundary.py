#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy phát hiện MEDIUM của Workflow đối kháng đa-agent 2026-09-04 (task #61):
`tools/kiem_so_lieu.py::co_so()` — hàm xác minh một hiệu số dashboard có xuất
hiện trong tóm tắt PubMed hay không — có hai lỗ ranh giới:

  1. Lookbehind cũ `(?<![\\d.])` không loại trừ DẤU TRỪ đứng trước, nên tra
     x=0.72 khớp NHẦM bên trong "-0.72" — một số HOÀN TOÀN KHÁC, đổi cả CHIỀU
     tác dụng lâm sàng (bảo vệ ↔ có hại). Đúng lớp lỗi mà công cụ này sinh ra
     để bắt (BH24/BH34: "dấu/phiên bản bị bỏ sót, cảnh báo lặng lẽ biến mất"),
     xảy ra ngay trong chính công cụ soi lỗi đó.
  2. Lookahead cũ `(?![\\d])` không loại trừ DẤU CHẤM theo sau, nên tra x=5
     khớp NHẦM bên trong "5.2" — một số khác hẳn về độ lớn.

Bản vá thêm "." vào lookahead, và lọc hậu-kiểm bằng Python thuần cho lookbehind:
một dấu "-" đứng ngay trước số CHỈ bị loại trừ khi bản thân dấu "-" đó KHÔNG
đứng ngay sau một chữ số khác — phân biệt DẤU ÂM ("-0.72", loại) khỏi RANH GIỚI
KHOẢNG ("0.60-0.86", giữ, để không mất khả năng khớp cận CI cao). Chỉ áp cho
x không âm — khi x âm, `s` đã tự mang dấu "-" nên khớp nguyên văn không cần lọc.

Logic ranh giới được tách vào hàm dùng chung `_khop_so_doc_lap()`, vì hàm
`nhan_lech()` (so NHÃN đo lường HR/RR/OR/MD/SMD quanh trị số) trong CÙNG file
mang Y HỆT biểu thức regex cũ — xác nhận bằng thực nghiệm trước khi vá: khai
measure="rr", x=5, văn bản chỉ có "5.2 (OR)" hoặc "-5.0 (MD)" → `nhan_lech()`
báo LỆCH sang "or"/"md" dù trị số 5 hoàn toàn không có trong văn bản — báo
động giả về một trị số không hề tồn tại, cùng họ lỗi với `co_so()`.

Nguyên tắc viết test: gọi THẲNG `co_so()`/`nhan_lech()`, không grep chuỗi
trong mã nguồn.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kiem_so_lieu as ksl  # noqa: E402


class TestSignDropFalsePositiveFixed(unittest.TestCase):
    """★★ Ca chính 1 — số dương x không được khớp bên trong "-x"."""

    def test_positive_target_khong_khop_ben_trong_so_am(self):
        text = "the mean difference was -0.72 (95% CI -1.10 to -0.34)"
        self.assertFalse(ksl.co_so(text, 0.72))

    def test_negative_target_van_khop_dung_dau(self):
        """★★ Đối chứng bắt buộc — x ÂM vẫn phải khớp đúng khi văn bản có số âm."""
        text = "the mean difference was -0.72 (95% CI -1.10 to -0.34)"
        self.assertTrue(ksl.co_so(text, -0.72))

    def test_positive_target_van_khop_khi_van_ban_khong_co_dau_tru(self):
        """★★ Đối chứng bắt buộc — trường hợp khớp bình thường không bị ảnh hưởng."""
        text = "the HR was 0.72 (95% CI 0.60 to 0.86)"
        self.assertTrue(ksl.co_so(text, 0.72))

    def test_dau_tru_dung_dau_van_ban_van_loai_dung(self):
        text = "-5 patients withdrew"
        self.assertFalse(ksl.co_so(text, 5))


class TestDecimalBoundaryFalsePositiveFixed(unittest.TestCase):
    """★★ Ca chính 2 — số nguyên x không được khớp bên trong x.y (số thập phân
    có phần nguyên trùng x)."""

    def test_so_nguyen_khong_khop_ben_trong_so_thap_phan(self):
        text = "the odds ratio was 5.2 (95% CI 3.1 to 8.4)"
        self.assertFalse(ksl.co_so(text, 5))

    def test_so_nguyen_van_khop_khi_theo_sau_khong_phai_thap_phan(self):
        """★★ Đối chứng bắt buộc — số nguyên đứng riêng (theo sau bởi dấu
        phẩy, khoảng trắng...) vẫn phải khớp như cũ."""
        text = "the study enrolled 5, all completed follow-up"
        self.assertTrue(ksl.co_so(text, 5))


class TestRangeSeparatorHyphenPreserved(unittest.TestCase):
    """★★ Đối chứng bắt buộc quan trọng nhất — dấu "-" dùng làm RANH GIỚI
    khoảng tin cậy (không phải dấu âm) không được bị bản vá làm mất khả năng
    khớp cận CAO của khoảng."""

    def test_can_cao_sau_dau_gach_ngang_noi_khoang_van_khop(self):
        text = "HR 0.72 (95% CI 0.60-0.86)"
        self.assertTrue(ksl.co_so(text, 0.86))

    def test_can_thap_truoc_dau_gach_ngang_van_khop(self):
        text = "HR 0.72 (95% CI 0.71-0.86)"
        self.assertTrue(ksl.co_so(text, 0.71))


class TestSoDoiChungKhongThayDoiHanhViCu(unittest.TestCase):
    """Các ca đơn giản không liên quan tới dấu/ranh giới thập phân — phải
    hoàn toàn không đổi hành vi."""

    def test_khong_tim_thay_van_tra_false(self):
        self.assertFalse(ksl.co_so("no numbers relevant here", 0.72))

    def test_so_am_khong_khop_khi_van_ban_khong_co(self):
        self.assertFalse(ksl.co_so("the HR was 0.72", -0.72))

    def test_khop_giua_cau_binh_thuong(self):
        # LƯU Ý: dùng "0.7" (không phải "0.70") trong văn bản — co_so() có một
        # giới hạn KHÁC, TỒN TẠI TỪ TRƯỚC bản vá này (không thuộc phạm vi task
        # #61): f"{x:g}" bỏ số 0 thừa (0.70 -> "0.7"), nên tra x=0.70 KHÔNG
        # khớp được với chuỗi viết "0.70" có số 0 thừa trong văn bản gốc — đã
        # xác nhận bằng thực nghiệm hành vi này y hệt trước và sau bản vá,
        # không phải hồi quy. Ghi nhận riêng, không sửa ở đây (ngoài phạm vi).
        text = "risk reduced by 30% (RR 0.7, 95% CI 0.55 to 0.89, p<0.01)"
        self.assertTrue(ksl.co_so(text, 0.70))
        self.assertTrue(ksl.co_so(text, 0.89))


class TestNhanLechChiaSeLoiRanhGioi(unittest.TestCase):
    """★★ `nhan_lech()` dùng CHUNG `_khop_so_doc_lap()` với `co_so()` — cùng hai
    lỗ ranh giới, xác nhận bằng thực nghiệm TRƯỚC khi vá (xem docstring module),
    nay phải vá đồng thời qua điểm dùng chung."""

    def test_decimal_boundary_khong_con_bao_dong_gia_ve_nhan(self):
        text = "in a separate analysis the odds ratio (OR) was 5.2 (95% CI 3.1 to 8.4)"
        self.assertIsNone(ksl.nhan_lech(text, "rr", 5))

    def test_sign_drop_khong_con_bao_dong_gia_ve_nhan(self):
        text = "the mean difference (MD) was -5.0 (95% CI -7.2 to -2.8)"
        self.assertIsNone(ksl.nhan_lech(text, "rr", 5))

    def test_doi_chung_bat_buoc_van_bat_dung_lech_that(self):
        """★★ Đối chứng bắt buộc — ca lệch THẬT (self-test nội bộ của module)
        không được bản vá làm mất khả năng bắt."""
        text = "In the intention-to-treat analysis, the hazard ratio was 0.72 (95% CI 0.64-0.82)."
        self.assertEqual(ksl.nhan_lech(text, "rr", 0.72), "hr")

    def test_doi_chung_bat_buoc_khai_dung_van_khop(self):
        text = "In the intention-to-treat analysis, the hazard ratio was 0.72 (95% CI 0.64-0.82)."
        self.assertIsNone(ksl.nhan_lech(text, "hr", 0.72))

    def test_self_test_noi_bo_van_dat(self):
        """Chốt hồi quy có sẵn trong chính module — phải tiếp tục ĐẠT sau vá."""
        self.assertEqual(ksl._self_test_nhan(), 0)


if __name__ == "__main__":
    unittest.main()
