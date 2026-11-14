# -*- coding: utf-8 -*-
"""Cấu hình làn Chrome cho ba miền Elsevier đo thật 14/11/2026 (làn Chrome đợt 6) — `tools/lan_chrome/cau_hinh.json`.

Đo thật 14/11/2026 trên Chrome macOS của bác sĩ (phiên uỷ quyền 20261114-081341): www.jpain.org (PMID 30453109),
www.mayoclinicproceedings.org (PMID 34481599), www.heartlungcirc.org (PMID 43015148) chưa có cấu hình ⇒ `toan-van` báo «chưa
có cấu hình ĐÃ KIỂM»; chạy thử bằng `--cau-hinh` chép đúng khuôn `elsevier_hoi` (article · min 12000 · PDF meta · khoá «Article
preview») thì cổng nội dung của `nhan` nhận cả ba, lưu HTML + PDF nhúng. Miền nhà xuất bản (khoá điều khoản Elsevier) đã khai từ
13/11 ở `doc_toan_van_co_nguoi.py` — test này chỉ chốt phần CẤU HÌNH TRANG. jaci-inpractice.org và amjmed.com cố ý CHƯA thêm:
đợt 6 chỉ gặp trang /abstract «Get full text access» (chưa thấy bài đọc được ⇒ chưa đo được khuôn).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import lan_chrome as L  # noqa: E402

CAU_HINH = json.loads((REPO / "tools" / "lan_chrome" / "cau_hinh.json").read_text(encoding="utf-8"))
MIEN_MOI = ("www.jpain.org", "www.mayoclinicproceedings.org", "www.heartlungcirc.org")


def test_khuon_hop_le_va_ba_mien_moi_vao_elsevier_hoi():
    assert L.kiem_cau_hinh(CAU_HINH) == []
    for host in MIEN_MOI:
        assert L.tim_nxb(host, CAU_HINH)[0] == "elsevier_hoi", host
    assert L.tim_nxb("www.jpain.org".upper(), CAU_HINH)[0] == "elsevier_hoi"  # khớp không phân biệt hoa thường


def test_mien_gia_mao_va_mien_chua_do_khong_nhan_cau_hinh():
    for host in ("notjpain.org", "www.jpain.org.evil.com", "jpain.org"):  # khớp ĐÚNG tên miền, không khớp đuôi
        assert L.tim_nxb(host, CAU_HINH) == (None, None), host
    for host in ("www.jaci-inpractice.org", "www.amjmed.com"):  # chưa đo được bài đọc được ⇒ chưa thêm
        assert L.tim_nxb(host, CAU_HINH) == (None, None), host


def test_dien_cau_hinh_ba_mien_moi_dung_khuon_elsevier_hoi():
    url = "https://www.jpain.org/article/S1526-5900(18)30988-X/fulltext"
    o = L.dien_cau_hinh(CAU_HINH["nxb"]["elsevier_hoi"], url, "10.1016/j.jpain.2018.11.003",
                        CAU_HINH["dau_khong_quyen_url"])
    assert o["chon"] == "article" and o["min"] == 12000 and o["pdf"] == "meta"
    assert o["khoaTrang"] == "Article preview"


def test_moc_kiem_ghi_pmid_do_that():
    moc = CAU_HINH["nxb"]["elsevier_hoi"]["kiem_lan_cuoi"]
    for pmid in ("30453109", "34481599", "43015148"):
        assert pmid in moc, pmid
