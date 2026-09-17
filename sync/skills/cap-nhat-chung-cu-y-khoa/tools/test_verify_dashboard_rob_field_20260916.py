#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""Cổng liêm chính (verify_dashboard.py) nay CẢNH BÁO khi `rob` không phải object hợp lệ
{miền:'l'|'s'|'h'} — thêm 2026-09-16, cùng đợt làm cứng template (xem
tools/test_ew_template_ho_thiet_ke_thang_hieu_so.py ở gốc repo và mục "Dashboard lâm sàng"
trong CLAUDE.md).

VÌ SAO CÓ. Ca thật WebDashboard_EBM_VanDeCuThe_CKM_TimThanChuyenHoa_20260628.html ITEM-02/
03/04 (design RCT) có `rob` là CHUỖI văn xuôi thay vì object theo schema. Template khi đó
SẬP hoàn toàn khi mở (TypeError khi lặp Object.values(chuỗi)) — nhưng verify_dashboard.py
KHÔNG bắt được, vì cổng chỉ kiểm pmid/doi/gradeLevel/decision/references[], chưa từng đọc
`rob`. Một dashboard hỏng như vậy vẫn PASS cổng liêm chính sạch sẽ.

Template nay đã làm cứng (rob chuỗi → hiện nguyên văn, không sập) nên cảnh báo ở ĐÂY CỐ Ý
KHÔNG chặn xuất — rob chuỗi vẫn là nội dung hợp lệ, chỉ khác hình thức. Test gọi THẲNG
rob_entries()/kiem_rob(), không grep chuỗi trong mã nguồn.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_dashboard as vd  # noqa: E402


def _chunk(rob_literal: str | None, design: str = "RCT") -> str:
    rob_part = ("rob:%s, " % rob_literal) if rob_literal is not None else ""
    return (
        "{id:'ITEM-01', design:'%s', %sgradeLevel:'na', decision:'consider', "
        "source:'x', org:'x', dateVersion:'2024', pmid:'12345678', gradeSource:'x'}"
        % (design, rob_part)
    )


class TestRobEntriesTrichObjectPhang(unittest.TestCase):
    def test_object_nhay_don_du_ba_mien(self):
        chunk = _chunk("{D1:'l', D2:'s', D3:'h'}")
        block, entries = vd.rob_entries(chunk)
        self.assertIsNotNone(block)
        self.assertEqual(entries, [("D1", "l"), ("D2", "s"), ("D3", "h")])

    def test_object_khoa_nhay_kep_co_khoang_trang(self):
        chunk = _chunk('{"D1 Ngẫu nhiên hoá":"l", "D5 Báo cáo chọn lọc":"h"}')
        block, entries = vd.rob_entries(chunk)
        self.assertIsNotNone(block)
        self.assertEqual(entries, [("D1 Ngẫu nhiên hoá", "l"), ("D5 Báo cáo chọn lọc", "h")])

    def test_chuoi_khong_phai_object_tra_none(self):
        chunk = _chunk("'Mù đôi, phân bổ ngẫu nhiên che giấu, phân tích ITT.'")
        block, entries = vd.rob_entries(chunk)
        self.assertIsNone(block)
        self.assertIsNone(entries)

    def test_vang_mat_tra_none(self):
        chunk = _chunk(None)
        block, entries = vd.rob_entries(chunk)
        self.assertIsNone(block)
        self.assertIsNone(entries)

    def test_object_rong_tra_block_khong_null_nhung_entries_rong(self):
        chunk = _chunk("{}")
        block, entries = vd.rob_entries(chunk)
        self.assertIsNotNone(block)
        self.assertEqual(entries, [])


class TestKiemRobObjectHopLe(unittest.TestCase):
    def test_ca_ba_mien_hop_le_khong_canh_bao(self):
        warns: list[str] = []
        vd.kiem_rob(_chunk("{D1:'l', D2:'s', D3:'h'}"), "ITEM-01", warns)
        self.assertEqual(warns, [])

    def test_ma_la_lan_ma_hop_le_chi_neu_dung_ma_la(self):
        warns: list[str] = []
        vd.kiem_rob(_chunk("{D1:'khong-xac-dinh', D2:'l'}"), "ITEM-01", warns)
        self.assertEqual(len(warns), 1)
        self.assertIn("ITEM-01", warns[0])
        self.assertIn("khong-xac-dinh", warns[0])
        self.assertNotIn("'l'", warns[0])  # mã HỢP LỆ không bị liệt vào danh sách "mã lạ"

    def test_hai_ma_la_deu_duoc_neu(self):
        warns: list[str] = []
        vd.kiem_rob(_chunk("{D1:'zzz', D2:'yyy'}"), "ITEM-01", warns)
        self.assertEqual(len(warns), 1)
        self.assertIn("zzz", warns[0])
        self.assertIn("yyy", warns[0])

    def test_object_rong_canh_bao_khong_doc_duoc_ma_mien(self):
        warns: list[str] = []
        vd.kiem_rob(_chunk("{}"), "ITEM-01", warns)
        self.assertEqual(len(warns), 1)
        self.assertIn("không đọc được mã miền nào", warns[0])


class TestKiemRobChuoi(unittest.TestCase):
    def test_chuoi_khong_rong_canh_bao_khong_chan(self):
        warns: list[str] = []
        vd.kiem_rob(
            _chunk("'Mù đôi, phân bổ ngẫu nhiên che giấu, phân tích ITT.'", design="RCT"),
            "ITEM-02", warns,
        )
        self.assertEqual(len(warns), 1)
        self.assertIn("ITEM-02", warns[0])
        self.assertIn("CHUỖI", warns[0])
        self.assertIn("không sập", warns[0])  # cảnh báo, không phải mô tả lỗi chặn

    def test_chuoi_rct_goi_y_chuan_hoa_ve_object(self):
        warns: list[str] = []
        vd.kiem_rob(_chunk("'Nguy cơ sai lệch thấp.'", design="RCT"), "ITEM-03", warns)
        self.assertIn("chuẩn hoá về object", warns[0])

    def test_chuoi_khong_phai_rct_khong_goi_y_chuan_hoa(self):
        warns: list[str] = []
        vd.kiem_rob(_chunk("'Tóm tắt định tính, không chấm theo miền.'", design="Cohort"), "ITEM-04", warns)
        self.assertNotIn("chuẩn hoá về object", warns[0])

    def test_chuoi_toan_khoang_trang_khong_canh_bao(self):
        warns: list[str] = []
        vd.kiem_rob(_chunk("'   '"), "ITEM-05", warns)
        self.assertEqual(warns, [])


class TestKiemRobVangMat(unittest.TestCase):
    def test_khong_co_rob_khong_canh_bao(self):
        warns: list[str] = []
        vd.kiem_rob(_chunk(None), "ITEM-06", warns)
        self.assertEqual(warns, [])


class TestKiemRobNoiVaoVongLapChinh(unittest.TestCase):
    """kiem_rob() phải THẬT SỰ được gọi trong main() — không chỉ tồn tại rời rạc.
    Kiểm bằng cách đọc mã nguồn main() (không phải hành vi runtime, vì main() cần argv/file
    thật) — chấp nhận được ở ĐÂY vì đối tượng kiểm là "lời gọi có tồn tại", không phải "logic
    đúng" (logic đã kiểm bằng lời gọi trực tiếp ở các test trên)."""

    def test_main_goi_kiem_rob_trong_vong_lap_item(self):
        import inspect
        src = inspect.getsource(vd.main)
        self.assertIn("kiem_rob(", src)


if __name__ == "__main__":
    unittest.main()
