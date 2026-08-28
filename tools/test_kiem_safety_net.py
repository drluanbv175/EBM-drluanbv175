#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy cho `kiem_safety_net.py` — ngoại tuyến, không PII, không mạng.

Mỗi ca gắn với một rủi ro THẬT: lá cờ tuyên bố thi hành không tồn tại (R9),
nguồn không truy được (R4), tiêu chí không đo được (R5), hai trục bị gộp (R3),
trạng thái và nội dung nói hai thứ khác nhau (R2).

Chạy:  python3 tools/kiem_safety_net.py && python3 tools/test_kiem_safety_net.py
"""
from __future__ import annotations

import datetime as dt
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kiem_safety_net as ks  # noqa: E402

HOM_NAY = dt.date(2026, 8, 22)
CO_BAT = {"enforce_safety_net_templates": True}


def hc_co_nguon(**ghi_de) -> dict:
    goc = {
        "ten": "Đau đầu",
        "trang_thai": "co-nguon",
        "co_do_cho_bac_si": {
            "nguon": {"pmid": "30587518", "doi": "10.1212/WNL.0000000000006697"},
            "gioi_han_nguyen_van_cua_nguon": "chưa có công cụ sàng lọc đã kiểm định",
            "tieu_chi": [{"mo_ta": "Khởi phát sau 65 tuổi", "do_duoc": True}],
        },
        "dan_benh_nhan_quay_lai": {"trang_thai": "chua-dien", "noi_dung": ks.PLACEHOLDER},
        "ngay_ra_soat": "2026-08-22",
    }
    goc.update(ghi_de)
    return goc


def hc_chua_dien() -> dict:
    return {
        "ten": "Đau ngực",
        "trang_thai": "chua-dien",
        "co_do_cho_bac_si": {"trang_thai": "chua-dien", "noi_dung": ks.PLACEHOLDER},
        "dan_benh_nhan_quay_lai": {"trang_thai": "chua-dien", "noi_dung": ks.PLACEHOLDER},
        "ngay_ra_soat": "2026-08-22",
    }


def mau(hoi_chung: dict) -> dict:
    return {"phien_ban": "2.0.0", "hoi_chung": hoi_chung}


def chay(hoi_chung: dict, co: dict = CO_BAT):
    return ks.kiem(mau(hoi_chung), co, HOM_NAY)


class LaCoKhongNoiHo(unittest.TestCase):
    """R9 — chính là lỗi đã tồn tại trong repo trước 22/08/2026."""

    def test_co_bat_ma_khong_hoi_chung_nao_co_nguon_la_loi_cung(self):
        loi, _, _ = chay({"dau-nguc": hc_chua_dien()})
        self.assertTrue(any(x.startswith("R9") for x in loi), loi)

    def test_co_it_nhat_mot_hoi_chung_co_nguon_thi_R9_im(self):
        loi, _, _ = chay({"dau-dau": hc_co_nguon(), "dau-nguc": hc_chua_dien()})
        self.assertFalse(any(x.startswith("R9") for x in loi), loi)

    def test_co_tat_thi_R9_khong_ap(self):
        loi, _, _ = chay({"dau-nguc": hc_chua_dien()},
                         co={"enforce_safety_net_templates": False})
        self.assertFalse(any(x.startswith("R9") for x in loi), loi)

    def test_thieu_file_co_thi_fail_closed(self):
        """Thiếu file cờ KHÔNG được đọc thành 'cờ đang tắt'."""
        ma = ks.main(["--mau", str(Path(__file__).parent.parent
                                   / "clinical_runtime" / "safety_net_templates.json"),
                      "--co", "/khong/co/that.json", "--hom-nay", "2026-08-22"])
        self.assertIn(ma, (0, 1), "thiếu file cờ không được làm chết công cụ")


class NguonPhaiTruyDuoc(unittest.TestCase):
    def test_nguon_van_xuoi_bi_chan(self):
        hc = hc_co_nguon()
        hc["co_do_cho_bac_si"]["nguon"] = {"ten": "theo kinh nghiệm lâm sàng"}
        loi, _, _ = chay({"dau-dau": hc})
        self.assertTrue(any(x.startswith("R4") for x in loi), loi)

    def test_guideline_kem_nam_thi_duoc(self):
        hc = hc_co_nguon()
        hc["co_do_cho_bac_si"]["nguon"] = {"guideline": "NICE NG12", "nam": "2021"}
        loi, _, _ = chay({"dau-dau": hc})
        self.assertFalse(any(x.startswith("R4") for x in loi), loi)

    def test_guideline_thieu_nam_bi_chan(self):
        hc = hc_co_nguon()
        hc["co_do_cho_bac_si"]["nguon"] = {"guideline": "NICE NG12"}
        loi, _, _ = chay({"dau-dau": hc})
        self.assertTrue(any(x.startswith("R4") for x in loi), loi)

    def test_pmid_khong_phai_so_bi_chan(self):
        hc = hc_co_nguon()
        hc["co_do_cho_bac_si"]["nguon"] = {"pmid": "sắp bổ sung"}
        loi, _, _ = chay({"dau-dau": hc})
        self.assertTrue(any(x.startswith("R4") for x in loi), loi)


class PhaiCoTieuChiDoDuoc(unittest.TestCase):
    def test_toan_tieu_chi_khong_do_duoc_bi_chan(self):
        hc = hc_co_nguon()
        hc["co_do_cho_bac_si"]["tieu_chi"] = [
            {"mo_ta": "nếu nặng hơn", "do_duoc": False},
            {"mo_ta": "nếu thấy không ổn", "do_duoc": False},
        ]
        loi, _, _ = chay({"dau-dau": hc})
        self.assertTrue(any(x.startswith("R5") for x in loi), loi)

    def test_mot_tieu_chi_do_duoc_la_du(self):
        loi, _, _ = chay({"dau-dau": hc_co_nguon()})
        self.assertFalse(any(x.startswith("R5") for x in loi), loi)


class HaiTrucKhongDuocGop(unittest.TestCase):
    def test_thieu_khoi_loi_dan_bi_chan(self):
        hc = hc_co_nguon()
        del hc["dan_benh_nhan_quay_lai"]
        loi, _, _ = chay({"dau-dau": hc})
        self.assertTrue(any(x.startswith("R3") for x in loi), loi)


class TrangThaiPhaiKhopNoiDung(unittest.TestCase):
    def test_khai_chua_dien_ma_khong_co_placeholder(self):
        hc = hc_chua_dien()
        hc["co_do_cho_bac_si"] = {"trang_thai": "chua-dien", "noi_dung": "đau ngực dữ dội"}
        loi, _, _ = chay({"dau-dau": hc_co_nguon(), "dau-nguc": hc})
        self.assertTrue(any(x.startswith("R2") for x in loi), loi)

    def test_khai_co_nguon_ma_con_placeholder(self):
        hc = hc_co_nguon()
        hc["co_do_cho_bac_si"]["tieu_chi"] = [
            {"mo_ta": ks.PLACEHOLDER, "do_duoc": True}]
        loi, _, _ = chay({"dau-dau": hc})
        self.assertTrue(any(x.startswith("R6") for x in loi), loi)

    def test_trang_thai_la_bi_chan(self):
        hc = hc_co_nguon(trang_thai="xong-roi")
        loi, _, _ = chay({"dau-dau": hc})
        self.assertTrue(any(x.startswith("R2") for x in loi), loi)


class GioiHanNguonPhaiNoiRa(unittest.TestCase):
    def test_thieu_gioi_han_thi_canh_bao(self):
        hc = hc_co_nguon()
        hc["co_do_cho_bac_si"]["gioi_han_nguyen_van_cua_nguon"] = ""
        _, canh_bao, _ = chay({"dau-dau": hc})
        self.assertTrue(any(x.startswith("R7") for x in canh_bao), canh_bao)


class HanRaSoat(unittest.TestCase):
    def test_qua_han_thi_canh_bao(self):
        hc = hc_co_nguon(ngay_ra_soat="2024-01-01")
        _, canh_bao, _ = chay({"dau-dau": hc})
        self.assertTrue(any(x.startswith("R8") for x in canh_bao), canh_bao)

    def test_thieu_ngay_ra_soat_la_loi_cung(self):
        hc = hc_co_nguon()
        del hc["ngay_ra_soat"]
        loi, _, _ = chay({"dau-dau": hc})
        self.assertTrue(any(x.startswith("R8") for x in loi), loi)


class DoPhuPhaiDuocNoiRa(unittest.TestCase):
    """BH32: một lá cờ `true` không được trình bày như kết luận về toàn bộ."""

    def test_do_phu_duoc_dem_dung(self):
        _, canh_bao, dp = chay({"dau-dau": hc_co_nguon(), "dau-nguc": hc_chua_dien(),
                                "sot": hc_chua_dien()})
        self.assertEqual(dp, {"tong": 3, "co_nguon": 1, "co_loi_dan": 0})
        self.assertTrue(any("Độ phủ CỜ ĐỎ" in x for x in canh_bao), canh_bao)
        self.assertTrue(any("LỜI DẶN CHO BỆNH NHÂN" in x for x in canh_bao), canh_bao)


class FileThatTrongRepo(unittest.TestCase):
    def test_file_that_khong_co_loi_cung(self):
        """File đang sống phải qua được chốt — nếu không, chốt hoặc file sai."""
        ma = ks.main(["--hom-nay", "2026-08-22"])
        self.assertIn(ma, (0, 1), "file thật trong repo đang có LỖI CỨNG")

    def test_file_that_giu_dung_hai_truc(self):
        d = json.loads((Path(__file__).parent.parent / "clinical_runtime"
                        / "safety_net_templates.json").read_text(encoding="utf-8"))
        for khoa, hc in d["hoi_chung"].items():
            self.assertIn("co_do_cho_bac_si", hc, khoa)
            self.assertIn("dan_benh_nhan_quay_lai", hc, khoa)

    def test_khong_co_PII_trong_file_that(self):
        raw = (Path(__file__).parent.parent / "clinical_runtime"
               / "safety_net_templates.json").read_text(encoding="utf-8")
        for cam in ("@", "CCCD", "CMND", "ngày sinh"):
            self.assertNotIn(cam, raw, f"file mẫu không được chứa {cam!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
