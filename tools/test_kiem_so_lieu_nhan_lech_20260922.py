#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vá 22/09/2026 (phản biện vòng 2, review:cong-rut-bai #6, LOW).

Một mục khai `measure: 'rr'` nhưng tóm tắt PubMed nói "hazard ratio" (cùng trị số) trước đây
VẪN được cộng vào "✓ KHỚP đầy đủ" (vì hr/lo/hi khớp số) — trong khi CHÍNH MỤC ĐÓ cũng bị liệt
"🔴 NHÃN LỆCH" ở danh sách cần đọc. Hai tuyên bố mâu thuẫn cho cùng một mục.
"""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import kiem_so_lieu as ksl  # noqa: E402

TT_HR_TRONG_RR = "In the intention-to-treat analysis, the hazard ratio was 0.72 (95% CI 0.64-0.82)."


def _dashboard_do_luong_lech(td: Path) -> Path:
    f = td / "WebDashboard_EBM_VanDeCuThe_ThuNghiem_20260922.html"
    # bh10-mien: fixture giả ghi vào thư mục tạm để thử kiem_so_lieu, không phải dashboard thật
    f.write_text(
        '<script>\nconst DATA = {\n  meta: { updated: "2026-09-22" },\n  items: [\n'
        '    { id: "ITEM-01", decision: "apply", pmid: "11111111", measure: "rr", '
        'effect: { hr: 0.72, lo: 0.64, hi: 0.82 } }\n'
        '  ]\n};\n/* ▲▲▲  HẾT KHỐI DATA  ▲▲▲ */\n</script>\n', encoding="utf-8")
    return f


class KhopVaNhanLechKhongMauThuan(unittest.TestCase):
    def _chay(self):
        with tempfile.TemporaryDirectory() as td:
            f = _dashboard_do_luong_lech(Path(td))
            out = io.StringIO()
            with mock.patch.object(ksl, "lay_tom_tat", lambda pm: TT_HR_TRONG_RR), \
                 mock.patch.object(ksl.time, "sleep", lambda s: None), \
                 mock.patch.object(sys, "argv", ["kiem_so_lieu.py", "--file", str(f)]), \
                 contextlib.redirect_stdout(out):
                rc = ksl.main()
        return rc, out.getvalue()

    def test_muc_nhan_lech_khong_duoc_dem_vao_khop(self):
        rc, van = self._chay()
        self.assertIn("🔴 NHÃN LỆCH", van)
        # Dòng tổng kết "✓ KHỚP đầy đủ" phải là 0 — mục DUY NHẤT trong kho bị nhãn lệch,
        # không được cộng vào khớp dù số hr/lo/hi trùng khớp abstract.
        self.assertIn("✓ KHỚP đầy đủ : 0", van, "mục nhãn lệch không được cộng vào ✓ KHỚP")
        self.assertIn("🔴 NHÃN LỆCH  : 1", van, "phải có dòng tổng kết riêng cho nhãn lệch")

    def test_muc_nhan_lech_khong_roi_vao_mot_phan_hay_khong_thay(self):
        rc, van = self._chay()
        self.assertIn("🟠 MỘT PHẦN   : 0", van)
        self.assertIn("⚪ KHÔNG THẤY : 0", van)


if __name__ == "__main__":
    unittest.main(verbosity=2)
