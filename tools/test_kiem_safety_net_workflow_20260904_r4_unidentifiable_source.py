#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy phát hiện HIGH của audit đối kháng 2026-09-04:
kiem_safety_net.py::_nguon_truy_duoc() (nuôi luật R4) chấp nhận một nguồn
KHÔNG THỂ tra ngược lại được, dù `trang_thai: "co-nguon"` + R4 báo PASS.

Ba lỗ, tất cả cùng một họ "kiểm sự có mặt của trường, không kiểm ĐỊNH DẠNG có
định danh được hay không":
  1. `pmid` chỉ đòi `.isdigit()` — không giới hạn độ dài, không loại "0"/"00000".
     PubMed đánh số PMID bắt đầu từ 1, không có PMID 0; PMID thật hiện có 4-9
     chữ số (medical-ebm-automation/app/evidence/citation_validator.py::_PMID
     dùng đúng `^\\d{4,9}$` — mốc chuẩn CÓ SẴN trong hệ, không phải bịa mới).
  2. `doi` chỉ đòi `.startswith("10.")` — chuỗi "10." trơn (3 ký tự, không mã
     đăng ký, không hậu tố) qua được dù không trỏ tới bài nào. Một DOI thật
     LUÔN có dạng `10.<4-9 chữ số>/<hậu tố>`
     (citation_validator.py::_DOI dùng `^10\\.\\d{4,9}/\\S+$`).
  3. `nam` chỉ đòi khác rỗng — `"y"` cũng qua dù không phải năm thật.

Nguyên tắc viết test: gọi THẲNG `_nguon_truy_duoc()` và `kiem()`, không grep
chuỗi trong mã nguồn. Dùng dữ liệu THẬT của safety_net_templates.json (8/8
hội chứng co-nguon) làm đối chứng KHÔNG được chặn oan.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kiem_safety_net as ks  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
HOM_NAY = dt.date(2026, 9, 4)
CO_BAT = {"enforce_safety_net_templates": True}


class TestPmidKhongDinhDanhDuocBiChan(unittest.TestCase):
    """★★ Ca chính, nhóm PMID."""

    def test_pmid_bang_0_khong_truy_duoc(self):
        self.assertFalse(ks._nguon_truy_duoc({"pmid": "0"}))

    def test_pmid_toan_so_0_khong_truy_duoc(self):
        self.assertFalse(ks._nguon_truy_duoc({"pmid": "00000"}))

    def test_pmid_qua_ngan_khong_truy_duoc(self):
        self.assertFalse(ks._nguon_truy_duoc({"pmid": "123"}))

    def test_pmid_qua_dai_khong_truy_duoc(self):
        self.assertFalse(ks._nguon_truy_duoc({"pmid": "1234567890"}))

    def test_pmid_that_8_chu_so_van_truy_duoc(self):
        """Đối chứng bắt buộc — PMID thật KHÔNG được chặn oan."""
        self.assertTrue(ks._nguon_truy_duoc({"pmid": "30587518"}))

    def test_pmid_4_chu_so_bien_duoi_van_truy_duoc(self):
        self.assertTrue(ks._nguon_truy_duoc({"pmid": "1000"}))

    def test_pmid_9_chu_so_bien_tren_van_truy_duoc(self):
        self.assertTrue(ks._nguon_truy_duoc({"pmid": "123456789"}))


class TestDoiKhongDinhDanhDuocBiChan(unittest.TestCase):
    def test_doi_tron_khong_ma_dang_ky_bi_chan(self):
        self.assertFalse(ks._nguon_truy_duoc({"doi": "10."}))

    def test_doi_thieu_hau_to_bi_chan(self):
        self.assertFalse(ks._nguon_truy_duoc({"doi": "10.1001"}))

    def test_doi_khong_bat_dau_bang_10_bi_chan(self):
        self.assertFalse(ks._nguon_truy_duoc({"doi": "11.1001/jama.2016.0288"}))

    def test_doi_that_van_truy_duoc(self):
        """Đối chứng bắt buộc — DOI thật KHÔNG được chặn oan."""
        self.assertTrue(ks._nguon_truy_duoc({"doi": "10.1212/WNL.0000000000006697"}))


class TestNamKhongDinhDanhDuocBiChan(unittest.TestCase):
    def test_nam_khong_phai_so_bi_chan(self):
        self.assertFalse(ks._nguon_truy_duoc({"guideline": "NEWS2", "nam": "y"}))

    def test_nam_khong_hop_le_the_ky_bi_chan(self):
        self.assertFalse(ks._nguon_truy_duoc({"guideline": "NEWS2", "nam": "3017"}))

    def test_nam_that_van_truy_duoc(self):
        """Đối chứng bắt buộc — năm thật KHÔNG được chặn oan."""
        self.assertTrue(ks._nguon_truy_duoc({"guideline": "NEWS2", "nam": "2017"}))

    def test_guideline_rong_van_bi_chan_du_nam_hop_le(self):
        self.assertFalse(ks._nguon_truy_duoc({"guideline": "", "nam": "2017"}))


class TestDoiChungKhongPhaVoDuLieuThat(unittest.TestCase):
    """★★ Đối chứng bắt buộc trên FILE THẬT — bản vá tuyệt đối không được chặn
    oan bất kỳ hội chứng nào đã có nguồn thật trong safety_net_templates.json."""

    def test_ca_8_hoi_chung_co_nguon_that_van_truy_duoc(self):
        mau = json.loads(ks.MAU.read_text(encoding="utf-8"))
        hoi_chung = mau.get("hoi_chung", {})
        self.assertTrue(hoi_chung, "file thật phải có ít nhất một hội chứng")
        for khoa, hc in hoi_chung.items():
            if hc.get("trang_thai") != "co-nguon":
                continue
            cd = hc.get("co_do_cho_bac_si") or {}
            nguon = cd.get("nguon")
            with self.subTest(hoi_chung=khoa):
                self.assertTrue(
                    ks._nguon_truy_duoc(nguon),
                    f"[{khoa}] nguồn THẬT bị chặn oan bởi bản vá R4: {nguon!r}",
                )

    def test_kiem_tren_file_that_khong_sinh_loi_R4_moi(self):
        """Chạy trọn kiem() trên file thật — R4 không được xuất hiện trong lỗi
        cứng (mọi nguồn thật trong file đều hợp lệ theo mốc chuẩn mới)."""
        mau = json.loads(ks.MAU.read_text(encoding="utf-8"))
        co = json.loads(ks.CO.read_text(encoding="utf-8")) if ks.CO.exists() else CO_BAT
        loi, _canh_bao, _do_phu = ks.kiem(mau, co, HOM_NAY)
        loi_r4 = [d for d in loi if d.startswith("R4 ")]
        self.assertEqual(loi_r4, [], f"R4 nổ trên dữ liệu thật (không nên): {loi_r4}")


class TestNguonBiaBiChanQuaKiemTronVen(unittest.TestCase):
    """Tích hợp: một hội chứng khai co-nguon với nguồn KHÔNG định danh được
    phải bị R4 chặn khi chạy qua kiem() trọn vẹn, không chỉ ở hàm đơn vị."""

    def _hc_voi_nguon(self, nguon: dict) -> dict:
        return {
            "ten": "Test",
            "trang_thai": "co-nguon",
            "co_do_cho_bac_si": {
                "nguon": nguon,
                "gioi_han_nguyen_van_cua_nguon": "x",
                "tieu_chi": [{"mo_ta": "x", "do_duoc": True}],
            },
            "dan_benh_nhan_quay_lai": {"trang_thai": "chua-dien", "noi_dung": ks.PLACEHOLDER},
        }

    def test_pmid_bia_bi_chan_qua_kiem(self):
        mau = {"phien_ban": "test", "hoi_chung": {"x": self._hc_voi_nguon({"pmid": "00000"})}}
        loi, _canh_bao, _do_phu = ks.kiem(mau, CO_BAT, HOM_NAY)
        self.assertTrue(any(d.startswith("R4 ") for d in loi), loi)

    def test_pmid_that_khong_bi_chan_qua_kiem(self):
        mau = {"phien_ban": "test", "hoi_chung": {"x": self._hc_voi_nguon({"pmid": "30587518"})}}
        loi, _canh_bao, _do_phu = ks.kiem(mau, CO_BAT, HOM_NAY)
        self.assertFalse(any(d.startswith("R4 ") for d in loi), loi)


if __name__ == "__main__":
    unittest.main()
