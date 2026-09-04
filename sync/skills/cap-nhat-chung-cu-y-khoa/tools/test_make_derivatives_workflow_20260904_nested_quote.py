#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy phát hiện HIGH của Workflow đối kháng đa-agent vòng 3 (2026-09-04) trong
make_derivatives.py::meta()/arr()/items() — cắt cụt/tách vỡ giá trị có dấu nháy kép
lồng bên trong chuỗi nháy đơn.

Cùng HỌ lỗi đã vá ở verify_dashboard.py::field() ngày 12/08/2026 (xem docstring hàm
đó): regex `['\"]([^'\"]*)['\"]` DỪNG ở dấu nháy loại KIA nằm bên trong chuỗi.
`title:'Chống chỉ định "tuyệt đối" ở bệnh nhân suy gan nặng, trừ khi đã ghép gan'` bị
cắt cụt thành "Chống chỉ định " — cả mệnh đề ngoại lệ lâm sàng biến mất, không báo
lỗi. `arr()` còn tệ hơn: MỘT bullet bị TÁCH thành HAI bullet rời rạc, mất liên từ
điều kiện.

Nguyên tắc viết test: gọi THẲNG meta()/arr()/items() với khối DATA dựng tay chứa
nháy kép lồng, không grep chuỗi trong mã nguồn.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_derivatives as md  # noqa: E402

TIEU_DE_LONG_NHAY = ('Chống chỉ định "tuyệt đối" ở bệnh nhân suy gan nặng, '
                      'trừ khi đã ghép gan')
BULLET_LONG_NHAY = 'Dùng liều thấp, "trừ khi" chống chỉ định'


class TestMetaKhongCatCutGiaTriCoNhayKepLong(unittest.TestCase):
    def test_meta_giu_nguyen_van_khi_co_nhay_kep_ben_trong(self):
        b = "conclusion:'%s'," % TIEU_DE_LONG_NHAY
        self.assertEqual(md.meta(b, "conclusion"), TIEU_DE_LONG_NHAY)

    def test_meta_van_dung_khi_khong_co_nhay_long(self):
        b = "conclusion:'Câu bình thường không nháy',"
        self.assertEqual(md.meta(b, "conclusion"), "Câu bình thường không nháy")

    def test_meta_ho_tro_nhay_kep_ben_ngoai_don_ben_trong(self):
        b = 'conclusion:"Nháy \'đơn\' bên trong chuỗi nháy kép",'
        self.assertEqual(md.meta(b, "conclusion"), "Nháy 'đơn' bên trong chuỗi nháy kép")


class TestArrKhongTachVoBulletCoNhayKepLong(unittest.TestCase):
    """★★ Ca chính, đúng nguyên văn kịch bản trong finding."""

    def test_arr_giu_nguyen_mot_bullet_khong_tach_lam_hai(self):
        b = "doNow:['%s']," % BULLET_LONG_NHAY
        self.assertEqual(md.arr(b, "doNow"), [BULLET_LONG_NHAY])

    def test_arr_nhieu_bullet_lan_bullet_co_nhay_long(self):
        b = "dontDo:['Bullet thường', '%s', 'Bullet khác']," % BULLET_LONG_NHAY
        self.assertEqual(
            md.arr(b, "dontDo"),
            ["Bullet thường", BULLET_LONG_NHAY, "Bullet khác"],
        )


class TestItemsKhongCatCutTitleCoNhayKepLong(unittest.TestCase):
    def test_items_title_giu_nguyen_van(self):
        b = (
            "items:[{id:'ITEM-01', title:'%s', source:'Guideline X', pmid:'123', "
            "effectText:'', gradeLevel:'high', decision:'apply'}]" % TIEU_DE_LONG_NHAY
        )
        its = md.items(b)
        self.assertEqual(len(its), 1)
        self.assertEqual(its[0]["title"], TIEU_DE_LONG_NHAY)
        self.assertEqual(its[0]["source"], "Guideline X")
        self.assertEqual(its[0]["pmid"], "123")


if __name__ == "__main__":
    unittest.main()
