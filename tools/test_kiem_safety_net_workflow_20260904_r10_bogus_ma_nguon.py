#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy phát hiện HIGH của audit đối kháng 2026-09-04:
kiem_safety_net.py::_nguon_truy_duoc_ld() (nuôi luật R10) chấp nhận một
`ma_nguon` BỊA — không khớp bất kỳ `tieu_chi[].ma` nào của CHÍNH hội chứng đó
— coi như đã tham chiếu tới một tiêu chí có nguồn thật.

Bối cảnh: docstring cũ của `_nguon_truy_duoc_ld()` đã tự khai `ma_nguon` là
"mã tham chiếu ngược về `tieu_chi` của `co_do_cho_bac_si`", và đo thật trên
`safety_net_templates.json` xác nhận mọi `tieu_chi` đều mang một `ma` ngắn
(S, N1, N2, O1, P8, Q1, W1…) mà `dan_benh_nhan_quay_lai.noi_dung[].ma_nguon`
trỏ ngược lại (kể cả dạng nhiều mã cách nhau bằng dấu phẩy: `"P1, P5"`). Vậy
mà trước bản vá, luật CHỈ kiểm `ma_nguon` khác chuỗi rỗng — hoàn toàn không
đối chiếu với tập `ma` thật. Một `"ma_nguon": "XYZ999-BIA"` (không trỏ tới
đâu cả) vẫn qua R10, đúng nghĩa "chấp nhận mã nguồn bịa" của phát hiện.

Nguyên tắc viết test: gọi THẲNG `_nguon_truy_duoc_ld()`/`_ma_hop_le_tieu_chi()`
và `kiem()`, không grep chuỗi trong mã nguồn. Dùng dữ liệu THẬT của
safety_net_templates.json làm đối chứng KHÔNG được chặn oan.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kiem_safety_net as ks  # noqa: E402

HOM_NAY = dt.date(2026, 9, 4)
CO_BAT = {"enforce_safety_net_templates": True}


def _cd(tieu_chi):
    return {
        "nguon": {"ten": "theo kinh nghiệm lâm sàng"},  # KHÔNG truy được ở cấp cd
        "gioi_han_nguyen_van_cua_nguon": "x",
        "tieu_chi": tieu_chi,
    }


class TestMaHopLeTieuChi(unittest.TestCase):
    """Đơn vị cho `_ma_hop_le_tieu_chi()` — hàm dựng tập đối chiếu."""

    def test_lay_dung_tap_ma(self):
        cd = _cd([{"ma": "O1", "mo_ta": "x"}, {"ma": "N2", "mo_ta": "y"}])
        self.assertEqual(ks._ma_hop_le_tieu_chi(cd), {"O1", "N2"})

    def test_tieu_chi_khong_co_ma_bi_loai(self):
        cd = _cd([{"mo_ta": "không có mã"}])
        self.assertEqual(ks._ma_hop_le_tieu_chi(cd), set())

    def test_khong_phai_dict_tra_rong(self):
        self.assertEqual(ks._ma_hop_le_tieu_chi(None), set())
        self.assertEqual(ks._ma_hop_le_tieu_chi("chuỗi"), set())

    def test_tieu_chi_khong_phai_list_tra_rong(self):
        self.assertEqual(ks._ma_hop_le_tieu_chi({"tieu_chi": "không phải list"}), set())


class TestMaNguonBiaBiChan(unittest.TestCase):
    """★★ Ca chính."""

    def test_ma_bia_khong_khop_tieu_chi_nao_bi_chan(self):
        ld = {"trang_thai": "co-nguon",
              "noi_dung": [{"cau": "x", "ma_nguon": "XYZ999-BIA"}]}
        ma_hop_le = {"O1", "N2"}
        self.assertFalse(ks._nguon_truy_duoc_ld(ld, ma_hop_le))

    def test_ma_that_khop_tieu_chi_thi_qua(self):
        ld = {"trang_thai": "co-nguon", "noi_dung": [{"cau": "x", "ma_nguon": "O1"}]}
        self.assertTrue(ks._nguon_truy_duoc_ld(ld, {"O1", "N2"}))

    def test_mot_mac_that_mot_muc_bia_van_bi_chan(self):
        """MỌI mục trong noi_dung[] phải đạt — một mục bịa lẫn trong danh sách
        vẫn phải chặn toàn bộ, không được để mục thật 'gánh' cho mục bịa."""
        ld = {"trang_thai": "co-nguon", "noi_dung": [
            {"cau": "thật", "ma_nguon": "O1"},
            {"cau": "bịa", "ma_nguon": "KHONG-TON-TAI"},
        ]}
        self.assertFalse(ks._nguon_truy_duoc_ld(ld, {"O1"}))

    def test_danh_sach_nhieu_ma_cach_nhau_dau_phay_deu_phai_khop(self):
        """Dữ liệu THẬT có dạng "P1, P5" — TẤT CẢ các mã trong danh sách phải
        khớp, không phải chỉ một."""
        ld = {"trang_thai": "co-nguon",
              "noi_dung": [{"cau": "x", "ma_nguon": "P1, P5"}]}
        self.assertTrue(ks._nguon_truy_duoc_ld(ld, {"P1", "P5", "P6"}))

    def test_danh_sach_nhieu_ma_mot_ma_bia_thi_chan(self):
        ld = {"trang_thai": "co-nguon",
              "noi_dung": [{"cau": "x", "ma_nguon": "P1, BIA-999"}]}
        self.assertFalse(ks._nguon_truy_duoc_ld(ld, {"P1", "P5", "P6"}))

    def test_ma_nguon_chi_toan_dau_phay_khong_vacuously_true(self):
        """Bẫy Python: `all([])` trả True — `ma_nguon` chỉ chứa dấu phẩy (sau
        khi tách/strip thành rỗng) KHÔNG được lách qua bằng danh sách rỗng."""
        ld = {"trang_thai": "co-nguon", "noi_dung": [{"cau": "x", "ma_nguon": " , , "}]}
        self.assertFalse(ks._nguon_truy_duoc_ld(ld, {"O1", "N2"}))

    def test_tap_ma_hop_le_rong_thi_moi_ma_nguon_deu_bi_chan(self):
        """Hội chứng chưa hề khai tieu_chi có mã (fixture cũ, chưa nâng cấp)
        -> ma_hop_le rỗng -> KHÔNG có gì để tham chiếu, mọi ma_nguon bị chặn
        thay vì đoán bừa là hợp lệ (fail-closed, không suy diễn PASS)."""
        ld = {"trang_thai": "co-nguon", "noi_dung": [{"cau": "x", "ma_nguon": "O1"}]}
        self.assertFalse(ks._nguon_truy_duoc_ld(ld, set()))


class TestDoiChungKhongPhaVoDuongCuKhac(unittest.TestCase):
    """Hai đường HỢP LỆ khác của R10 (nguồn cấp khối; nguon_goc chứa PMID/DOI)
    không được bị ảnh hưởng bởi bản vá — chỉ nhánh ma_nguon đổi hành vi."""

    def test_nguon_cap_khoi_van_qua_khong_can_ma_hop_le(self):
        ld = {"trang_thai": "co-nguon", "nguon": {"pmid": "30587518"},
              "noi_dung": [{"cau": "x"}]}
        self.assertTrue(ks._nguon_truy_duoc_ld(ld, set()))

    def test_nguon_goc_chua_pmid_van_qua_khong_can_ma_hop_le(self):
        ld = {"trang_thai": "co-nguon",
              "noi_dung": [{"cau": "x", "nguon_goc": "Bài gốc — PMID 30587518"}]}
        self.assertTrue(ks._nguon_truy_duoc_ld(ld, set()))


class TestDoiChungDuLieuThatKhongBiChanOan(unittest.TestCase):
    """★★ Đối chứng bắt buộc trên FILE THẬT — bản vá tuyệt đối không được
    chặn oan bất kỳ hội chứng nào đã có `ma_nguon` hợp lệ thật."""

    def test_ca_8_hoi_chung_van_qua_kiem_tron_ven(self):
        repo = Path(__file__).resolve().parents[1]
        mau = json.loads((repo / "clinical_runtime" / "safety_net_templates.json")
                          .read_text(encoding="utf-8"))
        co = json.loads((repo / "clinical_runtime" / "CLINICAL_RUNTIME_FLAGS.json")
                         .read_text(encoding="utf-8"))
        loi, _canh_bao, _do_phu = ks.kiem(mau, co, HOM_NAY)
        loi_r10 = [d for d in loi if d.startswith("R10 ")]
        self.assertEqual(loi_r10, [], f"R10 nổ trên dữ liệu thật (không nên): {loi_r10}")

    def test_moi_ma_nguon_that_trong_file_khop_dung_tieu_chi_cua_chinh_no(self):
        """Đối chiếu TRỰC TIẾP từng ma_nguon trong file với tieu_chi cùng hội
        chứng — chứng minh dữ liệu THẬT vốn đã đúng quy ước, không phải bản vá
        tình cờ khớp."""
        repo = Path(__file__).resolve().parents[1]
        mau = json.loads((repo / "clinical_runtime" / "safety_net_templates.json")
                          .read_text(encoding="utf-8"))
        kiem_duoc = 0
        for khoa, hc in mau.get("hoi_chung", {}).items():
            cd = hc.get("co_do_cho_bac_si") or {}
            ma_hop_le = ks._ma_hop_le_tieu_chi(cd)
            ld = hc.get("dan_benh_nhan_quay_lai") or {}
            for muc in (ld.get("noi_dung") or []):
                if not isinstance(muc, dict):
                    continue
                ma_nguon = str(muc.get("ma_nguon", "")).strip()
                if not ma_nguon:
                    continue
                ma_list = [m.strip() for m in ma_nguon.split(",") if m.strip()]
                with self.subTest(hoi_chung=khoa, ma_nguon=ma_nguon):
                    self.assertTrue(
                        ma_list and all(m in ma_hop_le for m in ma_list),
                        f"[{khoa}] ma_nguon={ma_nguon!r} không khớp tieu_chi "
                        f"thật ({sorted(ma_hop_le)})",
                    )
                    kiem_duoc += 1
        self.assertGreater(kiem_duoc, 0, "phải kiểm được ít nhất một ma_nguon thật")


class TestTichHopQuaKiemTronVen(unittest.TestCase):
    """Tích hợp: một hội chứng khai co-nguon với ma_nguon bịa phải bị R10
    chặn khi chạy qua kiem() trọn vẹn, không chỉ ở hàm đơn vị."""

    def _hc(self, ld_override: dict, tieu_chi: list) -> dict:
        return {
            "ten": "Test",
            "trang_thai": "co-nguon",
            "co_do_cho_bac_si": {
                "nguon": {"pmid": "30587518"},
                "gioi_han_nguyen_van_cua_nguon": "x",
                "tieu_chi": tieu_chi,
            },
            "dan_benh_nhan_quay_lai": ld_override,
            "ngay_ra_soat": "2026-09-01",
        }

    def test_ma_nguon_bia_bi_chan_qua_kiem(self):
        hc = self._hc(
            {"trang_thai": "co-nguon", "noi_dung": [{"cau": "x", "ma_nguon": "BIA"}]},
            [{"ma": "O1", "mo_ta": "x", "do_duoc": True}],
        )
        mau = {"phien_ban": "test", "hoi_chung": {"x": hc}}
        loi, _canh_bao, _do_phu = ks.kiem(mau, CO_BAT, HOM_NAY)
        self.assertTrue(any(d.startswith("R10 ") for d in loi), loi)

    def test_ma_nguon_that_khong_bi_chan_qua_kiem(self):
        hc = self._hc(
            {"trang_thai": "co-nguon", "noi_dung": [{"cau": "x", "ma_nguon": "O1"}]},
            [{"ma": "O1", "mo_ta": "x", "do_duoc": True}],
        )
        mau = {"phien_ban": "test", "hoi_chung": {"x": hc}}
        loi, _canh_bao, _do_phu = ks.kiem(mau, CO_BAT, HOM_NAY)
        self.assertFalse(any(d.startswith("R10 ") for d in loi), loi)


if __name__ == "__main__":
    unittest.main()
