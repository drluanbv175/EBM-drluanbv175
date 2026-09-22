#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vá 22/09/2026 (phản biện vòng 2, review:cong-rut-bai #9, LOW).

NCBI esummary có thể trả phản hồi HỢP LỆ ở tầng ngoài (có khoá 'result') nhưng MỘT SỐ
uid bên trong lại là bản lỗi riêng — vd {"uid": "123", "error": "cannot get document
summary"} — hoặc vắng mặt hẳn khỏi 'result'. Bản cũ `if not m: continue` gộp cả hai
trường hợp này thành "không đáng ghi", nên nếu TOÀN BỘ ứng viên của một lượt đều lỗi
từng-id thì hàm trả `[]` — bị đọc là "đã dò xong, sạch" dù không ứng viên nào thật sự
được kiểm. `main()` sẽ cộng PMID gốc đó vào `da_do` (đã dò) thay vì `hong` (chưa dò).
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("kcv_loi_tung_id_test", TOOLS / "kiem_chung_cu_vuot_qua.py")
kcv = importlib.util.module_from_spec(spec)
sys.modules["kcv_loi_tung_id_test"] = kcv
spec.loader.exec_module(kcv)

ELINK_HAI_ID = {"linksets": [{"linksetdbs": [{"links": ["88888888", "99999999"]}]}]}
ELINK_MOT_ID = {"linksets": [{"linksetdbs": [{"links": ["99999999"]}]}]}


class LoiTungIdTrongEsummaryKhongDuocDocThanhSach(unittest.TestCase):
    def test_toan_bo_uid_deu_co_khoa_error_rieng_tra_none(self):
        """Cả hai uid ứng viên đều mang {"error": ...} riêng — KHÔNG được đọc thành
        '[]' (đã dò, sạch); phải trả None (chưa kiểm được thật)."""
        esum = {"result": {
            "uids": ["88888888", "99999999"],
            "88888888": {"uid": "88888888", "error": "cannot get document summary"},
            "99999999": {"uid": "99999999", "error": "cannot get document summary"},
        }}

        def gia(url, cho=25):
            return ELINK_HAI_ID if "elink.fcgi" in url else esum

        with mock.patch.object(kcv, "_goi", gia):
            r = kcv.tong_quan_moi_hon("11111111", 2020, None)
        self.assertIsNone(r, "toàn bộ ứng viên lỗi từng-id ⇒ CHƯA kiểm, không phải 'sạch'")

    def test_uid_vang_mat_hoan_toan_khoi_result_cung_bi_tinh_la_loi(self):
        """uid không có mặt trong 'result' (không phải chỉ mang khoá error) — cùng một
        lớp lỗi, cùng cách xử lý."""
        esum = {"result": {"uids": ["99999999"]}}  # thiếu hẳn mục "99999999"

        def gia(url, cho=25):
            return ELINK_MOT_ID if "elink.fcgi" in url else esum

        with mock.patch.object(kcv, "_goi", gia):
            r = kcv.tong_quan_moi_hon("11111111", 2020, None)
        self.assertIsNone(r)

    def test_mot_uid_loi_mot_uid_co_du_lieu_duong_tinh_van_duoc_giu(self):
        """Bất đối xứng: một uid lỗi, một uid khác đọc được VÀ khớp tiêu chí (bài mới
        hơn) — dương tính đó vẫn phải được giữ, không bị None hoá theo uid lỗi kia."""
        esum = {"result": {
            "uids": ["88888888", "99999999"],
            "88888888": {"uid": "88888888", "error": "cannot get document summary"},
            "99999999": {"pubdate": "2025 Jan", "title": "Tong quan moi",
                         "source": "J", "pubtype": ["Systematic Review"]},
        }}

        def gia(url, cho=25):
            return ELINK_HAI_ID if "elink.fcgi" in url else esum

        with mock.patch.object(kcv, "_goi", gia):
            r = kcv.tong_quan_moi_hon("11111111", 2020, None)
        self.assertTrue(r and r[0]["pmid"] == "99999999",
                         "dương tính thật không được mất chỉ vì uid khác lỗi")

    def test_khong_co_loi_tung_id_van_tra_rong_dung_khi_khong_khop_tieu_chi(self):
        """Hồi quy: uid đọc được BÌNH THƯỜNG (không lỗi) nhưng năm cũ hơn nam_goc — vẫn
        phải trả '[]' như cũ (đã dò, không có gì mới), KHÔNG bị vá thành None."""
        esum = {"result": {
            "uids": ["99999999"],
            "99999999": {"pubdate": "2019 Jan", "title": "Tong quan cu",
                         "source": "J", "pubtype": ["Systematic Review"]},
        }}

        def gia(url, cho=25):
            return ELINK_MOT_ID if "elink.fcgi" in url else esum

        with mock.patch.object(kcv, "_goi", gia):
            r = kcv.tong_quan_moi_hon("11111111", 2020, None)
        self.assertEqual(r, [], "đọc được bình thường mà không khớp tiêu chí ⇒ '[]' đúng nghĩa, không phải None")


if __name__ == "__main__":
    unittest.main(verbosity=2)
