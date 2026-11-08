"""Bản tóm tắt chứng cứ Word/PDF: số đi kèm «%» luôn in theo quy ước Việt — 08/11/2026.

Vì sao có. Dựng bản ★ PMID 42593701 (guideline S3 PTSD) ⇒ PDF in «(tuyên bố 2.2, 90,0%)» thành «90.0%»: số sau dấu phẩy bị coi
là số hiệu NỐI TIẾP của «tuyên bố 2.2» (luật dành cho «khuyến cáo 3.1, 3.2»). Đo trên mọi bản đã dựng (bỏ đoạn trích «…»): 5
bản cùng lỗi — «toàn phần 99.8%» («phần» = mục), «điển hình 7.7%» («hình» = hình vẽ), «phân tích (0.5%», «hạng V 16.8–38.3%»
(«V» = phiên bản). Số đo phần trăm không bao giờ là số hiệu mục/khuyến cáo. Bất biến cũ giữ nguyên: số hiệu thật không đổi.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import tom_tat_chung_cu_word as T  # noqa: E402


@pytest.mark.parametrize("vao, ra", [
    ("(tuyên bố 2.2, 90.0%)", "(tuyên bố 2.2, 90,0%)"),
    ("(khuyến cáo 2.1, EE/A, 92.0%)", "(khuyến cáo 2.1, EE/A, 92,0%)"),
    ("Độ đặc hiệu anti-HBc toàn phần 99.8%", "Độ đặc hiệu anti-HBc toàn phần 99,8%"),
    ("mô học lành 89.8%, không điển hình 7.7%", "mô học lành 89,8%, không điển hình 7,7%"),
    ("43 người bị loại trước phân tích (0.5%)", "43 người bị loại trước phân tích (0,5%)"),
    ("PSI hạng V 16.8–38.3%", "PSI hạng V 16,8–38,3%"),
    ("mục 5.2 · tỉ lệ 12.5 %", "mục 5.2 · tỉ lệ 12,5 %"),
])
def test_so_phan_tram_luon_doi_dau(vao, ra):
    assert T.trinh_bay_vi(vao) == ra


@pytest.mark.parametrize("vao", [
    "khuyến cáo 1.1, 1.2 và 1.3",
    "khuyến cáo 3.1, 3.2",
    "Phân tích 7.1 và 7.2",
    "Bảng 12.1 · mục 5.2 · (R 2.1, mạnh)",
    "tuyên bố 2.2 và khuyến cáo 4.3",
])
def test_so_hieu_that_khong_doi(vao):
    assert T.trinh_bay_vi(vao) == vao


def test_trich_nguyen_van_khong_dung():
    assert T.trinh_bay_vi("bài ghi «13.4%» ở trang 5") == "bài ghi «13.4%» ở trang 5"
