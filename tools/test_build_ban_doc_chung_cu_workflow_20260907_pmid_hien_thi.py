#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy: build_ban_doc_chung_cu.py::plot_row() KHÔNG bao giờ in định danh truy
nguyên (PMID/DOI/URL) của item ra bản đọc, dù header đầu trang tự khai
"N/N mục có định danh truy nguyên" (đếm bằng item.get("pmid") ở chỗ khác).

Phát hiện khi dựng dashboard Suy tim HFnrEF 2026-09-07 (WebDashboard_EBM_Van
DeCuThe_SuyTim_HFnrEF_20260907.html): cả 6 item đều khai đủ `pmid`, nhưng
0/6 PMID xuất hiện trong `derivatives/*_ban-doc.html` — bác sĩ đọc bản đọc
không có cách nào tự tra lại nguồn nếu không mở dashboard gốc. Vi phạm bất
biến "mỗi đầu ra kèm PMID/DOI" (CLAUDE.md, Nguyên tắc bắt buộc #5) và mục
"Nguồn ghi dạng văn bản thường... Vancouver/NLM" của acceptance-checklist.md.

Nguyên tắc viết test: gọi THẲNG plot_row() với dict item dựng tay, không grep
chuỗi trong mã nguồn.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_ban_doc_chung_cu as bd  # noqa: E402


def _item(**overrides):
    base = {
        "title": "Thử nghiệm mẫu",
        "design": "RCT",
        "decision": "consider",
        "effect": {"measure": "HR", "hr": 0.82, "lo": 0.73, "hi": 0.92},
    }
    base.update(overrides)
    return base


class TestPmidHienThiTrongPlotRow(unittest.TestCase):
    """★★ Ca chính — item có pmid PHẢI thấy chữ "PMID <số>" trong hàng render."""

    def setUp(self):
        self.ax = bd.LogAxis(0.4, 2.0)

    def test_pmid_hien_ra_trong_hang(self):
        row = bd.plot_row(_item(pmid="36027570"), self.ax)
        self.assertIn("PMID 36027570", row)

    def test_doi_hien_ra_khi_khong_co_pmid(self):
        row = bd.plot_row(_item(doi="10.1056/NEJMoa2206286"), self.ax)
        self.assertIn("DOI 10.1056/NEJMoa2206286", row)

    def test_pmid_uu_tien_hon_doi_khi_co_ca_hai(self):
        row = bd.plot_row(_item(pmid="36027570", doi="10.1056/NEJMoa2206286"), self.ax)
        self.assertIn("PMID 36027570", row)
        self.assertNotIn("DOI 10.1056/NEJMoa2206286", row)

    def test_url_hien_ra_khi_khong_co_pmid_doi(self):
        row = bd.plot_row(_item(url="https://example.org/guideline"), self.ax)
        self.assertIn("URL https://example.org/guideline", row)

    def test_khong_co_dinh_danh_nao_thi_khong_in_nhan_rong(self):
        row = bd.plot_row(_item(), self.ax)
        self.assertNotIn("PMID", row)
        self.assertNotIn("DOI ", row)
        self.assertNotIn("URL ", row)

    def test_item_khong_co_hieu_so_dinh_luong_van_hien_pmid(self):
        """Mục ở Section 4 (Khuyến cáo/đồng thuận) không có effect — vẫn phải
        thấy định danh, vì nhánh effectText là nhánh render KHÁC của cùng hàm."""
        row = bd.plot_row(
            _item(title="Guideline mẫu", design="Guideline", effect=None,
                  pmid="41110921"),
            self.ax,
        )
        self.assertIn("PMID 41110921", row)

    def test_dinh_danh_duoc_escape_chong_xss(self):
        row = bd.plot_row(_item(pmid="<script>alert(1)</script>"), self.ax)
        self.assertNotIn("<script>", row)


class TestPmidHienThiTrongNoEffectBlock(unittest.TestCase):
    """Đường render THỨ HAI, độc lập với plot_row(): mục KHÔNG có hiệu số định
    lượng (guideline/consensus, đi vào Section 4 "Khuyến cáo và đồng thuận")
    được dựng bởi hàm lồng `_src()` bên trong `build_page()`, không tái dùng
    plot_row(). Vá plot_row() một mình không đủ — ca thật ITEM-01 (guideline)
    của dashboard Suy tim HFnrEF vẫn thiếu PMID sau khi chỉ vá plot_row()."""

    def _data_with_item(self, item):
        return {
            "meta": {"question": "Câu hỏi thử", "updated": "2026-09-07"},
            "summary": {"conclusion": "x", "doNow": [], "dontDo": [], "redFlags": []},
            "items": [item],
        }

    def test_pmid_hien_ra_o_muc_khong_co_hieu_so(self):
        item = {
            "title": "Guideline mẫu", "design": "Guideline", "decision": "consider",
            "source": "Tác giả mẫu, Tạp chí 2025", "pmid": "41110921",
        }
        page = bd.build_page(self._data_with_item(item), "test.html", None)
        self.assertIn("PMID 41110921", page)

    def test_doi_hien_ra_khi_khong_co_pmid_o_muc_khong_co_hieu_so(self):
        item = {
            "title": "Guideline mẫu", "design": "Guideline", "decision": "consider",
            "source": "Tác giả mẫu, Tạp chí 2025", "doi": "10.1016/j.cjca.2025.07.027",
        }
        page = bd.build_page(self._data_with_item(item), "test.html", None)
        self.assertIn("DOI 10.1016/j.cjca.2025.07.027", page)


class TestDongBoHaiBanTrackGit(unittest.TestCase):
    """Đối chứng đồng bộ: tools/ và sync/skills/cap-nhat-chung-cu-y-khoa/tools/
    phải byte-identical sau bản vá."""

    def test_hai_ban_byte_identical(self):
        a = Path(__file__).resolve().parent / "build_ban_doc_chung_cu.py"
        b = (Path(__file__).resolve().parents[1] / "sync" / "skills" /
             "cap-nhat-chung-cu-y-khoa" / "tools" / "build_ban_doc_chung_cu.py")
        self.assertEqual(a.read_bytes(), b.read_bytes())


if __name__ == "__main__":
    unittest.main()
