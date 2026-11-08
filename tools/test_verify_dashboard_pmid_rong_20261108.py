#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cổng verify_dashboard.py: PubMed trả JSON KHÔNG có bản ghi của PMID ≠ «PMID không tồn tại» (08/11/2026).

VÌ SAO CÓ. Đo 08/11/2026: lô xuất lại bộ năm chạy song song lượt gom «vượt qua» (cùng gọi NCBI) ⇒ cổng `--online` CHẶN CỨNG
(mã 3) dashboard Gout vì PMID 20131255 và 34882311 «KHÔNG phân giải: không có trong PubMed» — cả hai có thật (thử nghiệm
colchicine Arthritis Rheum 2010; Cochrane NSAID 2021). Nguyên nhân: `verify_pmid_online` trả False cho MỌI phản hồi HTTP 200
không chứa bản ghi của PMID. Đo thật cùng ngày: PMID không có thật ⇒ NCBI trả bản ghi kèm `"error": "cannot get document
summary"`. Luật mới: False CHỈ khi NCBI từ chối rõ (và Europe PMC cũng không thấy); JSON thiếu bản ghi/báo vượt giới hạn tần
suất ⇒ nhánh lỗi tạm thời (thử lại, Europe PMC, cuối cùng None — «không xác minh được», fail-closed). Mạng giả hoàn toàn.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
NGUON = REPO / "sync/skills/cap-nhat-chung-cu-y-khoa/tools/verify_dashboard.py"
BAN_SAO = [REPO / "sync/skills/dark-analyst/tools/verify_dashboard.py"]


def _nap():
    sp = importlib.util.spec_from_file_location("_vd_pmid_rong", NGUON)
    m = importlib.util.module_from_spec(sp)
    sys.modules["_vd_pmid_rong"] = m
    sp.loader.exec_module(m)
    return m


vd = _nap()


class _PhanHoiGia:
    def __init__(self, than: str):
        self._than = than.encode("utf-8")
        self.headers = {"content-type": "application/json"}

    def read(self):
        return self._than

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def _ncbi(than: dict):
    dem = {"n": 0}

    def _mo(url, timeout=None):
        assert "esummary" in url, url
        dem["n"] += 1
        return _PhanHoiGia(json.dumps(than))
    return _mo, dem


def _chay(than: dict, epmc=(None, "europe pmc không trả lời", "")):
    mo, dem = _ncbi(than)
    with mock.patch.object(vd, "source_urlopen", mo), mock.patch.object(vd, "verify_pmid_europe_pmc", return_value=epmc), \
            mock.patch.object(vd.time, "sleep", lambda *_: None):
        return vd.verify_pmid_online("20131255"), dem["n"]


CO_BAN_GHI = {"result": {"uids": ["20131255"], "20131255": {"uid": "20131255", "title": "High versus low dosing of oral colchicine",
                                                             "pubdate": "2010 Apr", "articleids": []}}}
TU_CHOI_RO = {"result": {"uids": ["20131255"], "20131255": {"uid": "20131255", "error": "cannot get document summary"}}}
THIEU_BAN_GHI = {"header": {}, "result": {"uids": []}}
VUOT_GIOI_HAN = {"error": "API rate limit exceeded", "api-key": "1.2.3.4", "count": "4", "limit": "3"}


class TestPmidRongKhongPhaiKhongTonTai(unittest.TestCase):
    def test_co_ban_ghi_la_true(self):
        (kq, _t, _n), _ = _chay(CO_BAN_GHI)
        self.assertIs(kq, True)

    def test_tu_choi_ro_va_europe_pmc_khong_thay_la_false(self):
        (kq, info, _n), _ = _chay(TU_CHOI_RO, epmc=(False, "không thấy", ""))
        self.assertIs(kq, False)
        self.assertIn("không có trong PubMed", info)

    def test_tu_choi_ro_nhung_europe_pmc_thay_la_true(self):
        (kq, _t, _n), _ = _chay(TU_CHOI_RO, epmc=(True, "tiêu đề từ Europe PMC", "2010"))
        self.assertIs(kq, True)

    def test_json_thieu_ban_ghi_la_none_khong_phai_false(self):
        (kq, info, _n), so_lan = _chay(THIEU_BAN_GHI)
        self.assertIsNone(kq, "JSON thiếu bản ghi là phản hồi tạm thời — không được kết luận «không tồn tại»")
        self.assertGreater(so_lan, 1, "phải thử lại trước khi bỏ cuộc")

    def test_vuot_gioi_han_tan_suat_la_none(self):
        (kq, _i, _n), _ = _chay(VUOT_GIOI_HAN)
        self.assertIsNone(kq)

    def test_json_thieu_ban_ghi_ma_europe_pmc_thay_la_true(self):
        (kq, _t, _n), _ = _chay(THIEU_BAN_GHI, epmc=(True, "tiêu đề từ Europe PMC", "2010"))
        self.assertIs(kq, True)

    def test_cac_ban_dong_bo_giong_het_nguon_chuan(self):
        for p in BAN_SAO:
            self.assertEqual(p.read_bytes(), NGUON.read_bytes(), f"{p} lệch nguồn chuẩn")


if __name__ == "__main__":
    unittest.main()
