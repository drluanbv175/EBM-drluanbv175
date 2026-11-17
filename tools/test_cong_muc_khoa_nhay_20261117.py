#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BH182 (17/11/2026): cổng liêm chính CHẶN CỨNG mục viết kiểu khoá có nháy ({"id": …} / {'id': …}).

`split_items` chỉ nhận `{id:` không nháy ⇒ mục kiểu nháy vẫn hiện trên trang nhưng mọi luật cấp mục, quét lạc chủ đề và
cầu nạp sổ cái hub không thấy, cổng vẫn PASS. Ca thật: VKDT_TamThanKinh_20261113 ITEM-63…68. Chạy CLI thật của cổng trên
dashboard tạm; không mạng. Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CONG = Path(__file__).resolve().parents[1] / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "verify_dashboard.py"
KHUON = ('<html><script>const DATA = { meta: { question: "Chủ đề thử" }, items: [ %s ], '
         'summary: { conclusion: "x", doNow: [], dontDo: [], redFlags: [] } };</script></html>')
MUC_THUONG = '{id:"ITEM-1", title:"Bài A", pmid:"12345678"}'


def _chay(cac_muc: str) -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "dash.html"
        p.write_text(KHUON % cac_muc, encoding="utf-8")
        r = subprocess.run([sys.executable, "-B", str(CONG), str(p)], capture_output=True, text=True,
                           encoding="utf-8", timeout=120)
        return r.returncode, r.stdout + r.stderr


class CongChanMucKhoaNhay(unittest.TestCase):
    def setUp(self):
        if not CONG.exists():
            self.skipTest("⚪ không có verify_dashboard.py ở cây này")

    def test_khoa_nhay_kep_bi_chan_va_neu_ten_muc(self):
        ma, ra = _chay(MUC_THUONG + ', {"id": "ITEM-2", "title": "Bài B"}')
        self.assertIn("khoá có nháy", ra)
        self.assertIn("ITEM-2", ra.split("khoá có nháy", 1)[1][:400])
        self.assertNotEqual(ma, 0)

    def test_khoa_nhay_don_cung_bi_chan(self):
        _, ra = _chay(MUC_THUONG + ", {'id': 'ITEM-3', 'title': 'Bài C'}")
        self.assertIn("khoá có nháy", ra)
        self.assertIn("ITEM-3", ra.split("khoá có nháy", 1)[1][:400])

    def test_khoa_khong_nhay_khong_bao_oan(self):
        _, ra = _chay(MUC_THUONG + ", {id:'ITEM-2', title:'Bài B'}")
        self.assertNotIn("khoá có nháy", ra)


if __name__ == "__main__":
    unittest.main()
