#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy phát hiện HIGH của Workflow đối kháng đa-agent vòng 3 (2026-09-04) trong
build_ban_doc_chung_cu.py::build_page() — không cảnh báo khi DATA.summary có khoá SAI TÊN.

`summary.get('redFlags', [])`/`get('doNow', [])`/`get('dontDo', [])` coi khoá SAI TÊN
(vd `notDo` thay vì `dontDo` — đúng lỗi BH61 đã xảy ra HAI LẦN trong thực tế, ghi trong
CLAUDE.md) y hệt khoá VẮNG MẶT: trả về [] êm ru, không lỗi/cảnh báo. Panel "Không nên,
hoặc chưa nên đổi" render RỖNG mà không một dấu hiệu nào lộ ra trên trang.

verify_dashboard.py::kiem_khoa_summary() đã CHẶN CỨNG lỗi này ở CỔNG (18/08/2026), và
xuat_goi_cap_nhat.py (vá 2026-09-04, cùng vòng Workflow này) nay CHẶN XUẤT trước khi
gọi tới build_ban_doc_chung_cu.py qua đường ống chuẩn. Bản vá này là lớp phòng thủ THỨ
HAI cho trường hợp công cụ được gọi ĐỘC LẬP (không qua cổng, vd chạy tay).

Nguyên tắc viết test: gọi THẲNG build_page()/khoi_khoa_summary_la() với dict DATA dựng
tay, không grep chuỗi trong mã nguồn.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_ban_doc_chung_cu as bd  # noqa: E402


def _data(summary):
    return {
        "meta": {"question": "Câu hỏi thử", "updated": "2026-09-04"},
        "summary": summary,
        "items": [],
    }


class TestKhoaLaTrongSummaryDuocCanhBao(unittest.TestCase):
    """★★ Ca chính, đúng nguyên văn kịch bản BH61 trong finding."""

    def test_notdo_thay_vi_dontdo_bi_canh_bao(self):
        page = bd.build_page(
            _data({"conclusion": "x", "doNow": ["a"],
                   "notDo": ["KHÔNG ngừng opioid ĐỘT NGỘT ở người dùng dài hạn"],
                   "redFlags": []}),
            "test.html", None,
        )
        self.assertIn("khoá LẠ", page)
        self.assertIn("notDo", page)

    def test_noi_dung_duoi_khoa_sai_ten_khong_hien_o_panel_dung(self):
        """Đối chứng trực tiếp harm: nội dung dưới khoá sai tên KHÔNG xuất hiện ở
        panel 'Không nên, hoặc chưa nên đổi' — đúng thứ finding mô tả là mất."""
        page = bd.build_page(
            _data({"conclusion": "x", "doNow": ["a"],
                   "notDo": ["KHÔNG ngừng opioid ĐỘT NGỘT ở người dùng dài hạn"],
                   "redFlags": []}),
            "test.html", None,
        )
        # Nội dung có mặt đâu đó (trong khối cảnh báo khoá lạ) nhưng KHÔNG nằm
        # trong panel "act stop" (panel dontDo thật).
        stop_start = page.find('class="act stop"')
        stop_end = page.find("</div>", stop_start)
        self.assertNotIn("KHÔNG ngừng opioid", page[stop_start:stop_end])

    def test_khoi_khoa_summary_la_liet_ke_dung_khoa_sai(self):
        html = bd.khoi_khoa_summary_la({"conclusion": "x", "notDo": ["a"], "extraKey": ["b"]})
        self.assertIn("notDo", html)
        self.assertIn("extraKey", html)
        self.assertIn("khoá LẠ", html)


class TestKhoaDungKhongBiCanhBao(unittest.TestCase):
    """Đối chứng BẮT BUỘC: 4 khoá hợp lệ (conclusion/doNow/dontDo/redFlags) không
    kích hoạt cảnh báo — bản vá không được báo động giả trên dữ liệu đúng."""

    def test_du_bon_khoa_hop_le_khong_co_canh_bao(self):
        page = bd.build_page(
            _data({"conclusion": "x", "doNow": ["a"], "dontDo": ["b"], "redFlags": ["c"]}),
            "test.html", None,
        )
        self.assertNotIn("khoá LẠ", page)

    def test_khoi_khoa_summary_la_rong_khi_dung_khoa(self):
        self.assertEqual(
            bd.khoi_khoa_summary_la({"conclusion": "x", "doNow": [], "dontDo": [], "redFlags": []}),
            "",
        )

    def test_khoi_khoa_summary_la_rong_khi_thieu_khoa_khong_thua(self):
        """Thiếu khoá (không phải thừa khoá lạ) KHÔNG thuộc phạm vi cảnh báo này —
        đó là việc của panel rỗng bình thường, không phải nội dung bị vứt do gõ sai
        tên. Tránh chồng lấn cảnh báo."""
        self.assertEqual(bd.khoi_khoa_summary_la({"conclusion": "x"}), "")


class TestDongBoHaiBanTrackGit(unittest.TestCase):
    """Đối chứng đồng bộ: tools/ và sync/skills/cap-nhat-chung-cu-y-khoa/tools/ phải
    byte-identical sau bản vá — hai công cụ dựng bằng cùng nguồn."""

    def test_hai_ban_byte_identical(self):
        a = Path(__file__).resolve().parent / "build_ban_doc_chung_cu.py"
        b = (Path(__file__).resolve().parents[1] / "sync" / "skills" /
             "cap-nhat-chung-cu-y-khoa" / "tools" / "build_ban_doc_chung_cu.py")
        self.assertEqual(a.read_bytes(), b.read_bytes())


if __name__ == "__main__":
    unittest.main()
