#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test cho cổng nguồn nghiêm ngặt của verify_dashboard.py — unittest chuẩn, chạy:
    python3 tools/test_verify_dashboard_source_gate.py

VÌ SAO CÓ (12/08/2026): `verify_dashboard.py` là cổng liêm chính đứng trước MỌI
lần phát hành gói chứng cứ lâm sàng, nhưng cho tới hôm nay KHÔNG có một test nào.
Đợt rà 12/08 tìm ra ba lỗi trong chính cổng này, cả ba đều thuộc loại "cổng nói
sai về dữ liệu đúng" hoặc ngược lại — nguy hiểm hơn cổng không chạy, vì nó tạo
niềm tin sai:

  1. `field()` cắt giá trị ở dấu nháy loại kia nằm BÊN TRONG chuỗi, nên
     gradeSource:'"Usually Not Appropriate" — ACR' bị đọc thành RỖNG và cổng báo
     "thiếu gradeSource" cho item có đủ dữ liệu. Trích nguyên văn phân hạng của
     nguồn hầu như luôn có dấu nháy kép → lỗi nhắm đúng trường quan trọng nhất.
  2. Luật "apply cần gradeLevel mạnh" không phân biệt chứng cứ nghiên cứu với
     nguồn QUY PHẠM (guideline chính thức, nhãn thuốc). Hậu quả: ép hạ một CHỐNG
     CHỈ ĐỊNH và liều theo CrCl của nhãn FDA xuống "cân nhắc" — giảm an toàn.
  3. `KNOWN_DESIGNS` chỉ có 5 giá trị trong khi 35 item thật thuộc 23 loại, gồm
     "Nhãn thuốc" và "Cảnh báo dược cảnh giác".

Test này khoá cả ba hành vi, và khoá luôn các đường LÁCH của miễn trừ quy phạm.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_dashboard as vd  # noqa: E402


class TestFieldNhayLong(unittest.TestCase):
    """`field()` phải đọc trọn giá trị kể cả khi bên trong có dấu nháy loại kia."""

    def test_nhay_kep_ben_trong_nhay_don(self):
        chunk = """gradeSource:'"Usually Not Appropriate" — phân loại chính thức của ACR',"""
        self.assertEqual(
            vd.field(chunk, "gradeSource"),
            '"Usually Not Appropriate" — phân loại chính thức của ACR',
        )

    def test_nhay_don_ben_trong_nhay_kep(self):
        chunk = """gradeSource:"khuyến cáo 'mạnh' theo GRADE","""
        self.assertEqual(vd.field(chunk, "gradeSource"), "khuyến cáo 'mạnh' theo GRADE")

    def test_gia_tri_thuong_van_doc_dung(self):
        self.assertEqual(vd.field("""design:"Guideline",""", "design"), "Guideline")
        self.assertEqual(vd.field("""design:'Meta',""", "design"), "Meta")

    def test_khong_co_khoa_tra_none(self):
        self.assertIsNone(vd.field("""design:"Meta",""", "gradeSource"))

    def test_gia_tri_rong_van_la_rong(self):
        # Phân biệt "khoá vắng mặt" (None) với "khoá có nhưng rỗng" ('').
        self.assertEqual(vd.field("""gradeSource:"",""", "gradeSource"), "")


class TestMienTruQuyPham(unittest.TestCase):
    """Miễn trừ chỉ dành cho nguồn quy phạm ĐÃ KHAI BÁO TƯỜNG MINH."""

    def test_nhan_thuoc_khai_du_thi_duoc_mien(self):
        duoc, ly_do = vd.normative_exemption(
            "Nhãn thuốc", "na", "drug-label", "Nhãn thuốc FDA hiện hành")
        self.assertTrue(duoc)
        self.assertIsNone(ly_do)

    def test_guideline_chong_chi_dinh_duoc_mien(self):
        duoc, _ = vd.normative_exemption(
            "Guideline", "na", "contraindication", "Chống chỉ định rõ ràng, 2 guideline")
        self.assertTrue(duoc)

    def test_hau_to_mo_ta_van_nhan(self):
        duoc, _ = vd.normative_exemption(
            "Guideline/tổng quan", "na", "guideline-strong-rec", "khuyến cáo mạnh")
        self.assertTrue(duoc)

    # ── các đường LÁCH phải bị chặn ────────────────────────────────────────
    def test_consensus_khong_bao_gio_duoc_mien(self):
        """Đồng thuận chuyên gia KHÔNG phải văn bản quy phạm, dù khai gì."""
        duoc, ly_do = vd.normative_exemption(
            "Consensus", "na", "guideline-strong-rec", "đồng thuận Delphi")
        self.assertFalse(duoc)
        self.assertIsNone(ly_do)  # rơi về luật gốc, không phải "thiếu khai báo"

    def test_grade_low_khong_duoc_mien(self):
        """Nguồn ĐÃ tự phân hạng thấp thì không viện cớ quy phạm được."""
        for muc in ("low", "vlow"):
            duoc, _ = vd.normative_exemption(
                "Guideline", muc, "guideline-strong-rec", "GRADE thấp")
            self.assertFalse(duoc, f"gradeLevel={muc} không được miễn")

    def test_thieu_khai_bao_thi_bao_ro_thieu_gi(self):
        duoc, ly_do = vd.normative_exemption("Guideline", "na", None, "khuyến cáo mạnh")
        self.assertFalse(duoc)
        self.assertIn("normativeBasis", ly_do)

    def test_khai_bao_bay_khong_hop_le(self):
        duoc, ly_do = vd.normative_exemption(
            "Guideline", "na", "rất-quan-trọng", "khuyến cáo mạnh")
        self.assertFalse(duoc)
        self.assertIn("không hợp lệ", ly_do)

    def test_khai_normative_nhung_thieu_grade_source(self):
        """Khai loại quy phạm mà không dẫn phân hạng nguyên bản thì chưa đủ."""
        duoc, ly_do = vd.normative_exemption("Guideline", "na", "drug-label", None)
        self.assertFalse(duoc)
        self.assertIn("gradeSource", ly_do)

    def test_cohort_khong_duoc_mien(self):
        duoc, ly_do = vd.normative_exemption(
            "Cohort", "na", "guideline-strong-rec", "không phân hạng")
        self.assertFalse(duoc)
        self.assertIsNone(ly_do)


class TestHoThietKe(unittest.TestCase):
    def test_cac_ho_that_deu_nhan_dien_duoc(self):
        # Lấy từ dữ liệu THẬT của 60 dashboard ngày 12/08.
        for d in ("Guideline", "Meta", "RCT", "Cohort", "Consensus",
                  "Nhãn thuốc", "Guideline/tổng quan", "Guideline hội chuyên ngành",
                  "Case series (trích lại trong guideline)", "PK + Cohort quan sát",
                  "Cơ chế + Cohort quan sát", "RCT pha 3 không thua kém",
                  "Đồng thuận đa hội (expert consensus)", "Cảnh báo dược cảnh giác",
                  "Phê duyệt cơ quan quản lý (regulatory)", "So sánh đa-guideline",
                  "Drug Safety Update (cơ quan quản lý)"):
            self.assertFalse(vd.design_khong_nhan_dien(d), f"phải nhận diện được: {d}")

    def test_design_vo_nghia_van_bi_bat(self):
        for d in ("Khác", "abc", "", None):
            self.assertTrue(vd.design_khong_nhan_dien(d), f"phải bắt được: {d!r}")


def _tim_thu_muc_dashboard() -> Path | None:
    """Tìm thư mục chứa WebDashboard_*.html.

    Test này tồn tại ở HAI nơi: bản runtime trong `EBM-Dashboards/tools/` (cạnh
    dashboard thật, nhưng thư mục đó bị .gitignore) và bản nguồn được track trong
    `sync/skills/cap-nhat-chung-cu-y-khoa/tools/`. Bản nguồn không nằm cạnh dữ
    liệu, nên phải dò lên — không thấy thì bỏ qua nhóm test dữ liệu thật thay vì
    báo đỏ giả.
    """
    here = Path(__file__).resolve()
    for to_tien in here.parents:
        ung_vien = to_tien / "EBM-Dashboards"
        if ung_vien.is_dir():
            return ung_vien
        if (to_tien / "WebDashboard_EBM_VanDeCuThe_DauDau_20260718.html").exists():
            return to_tien
    return None


class TestCongTrenDuLieuThat(unittest.TestCase):
    """Chạy cổng trên chính 5 dashboard đã sửa ngày 12/08 — chống hồi quy thật."""

    DASH = _tim_thu_muc_dashboard()
    FILES = [
        "WebDashboard_EBM_VanDeCuThe_NguoiCaoTuoi_DaBenhLy_NgoaiTru_20260811.html",
        "WebDashboard_EBM_VanDeCuThe_SuyThuongThan_ThuocBenhKem_DoiTuongTienLuong_20260811.html",
        "WebDashboard_EBM_VanDeCuThe_DauDau_20260718.html",
        "WebDashboard_EBM_VanDeCuThe_ViemGanB_DieuTri_20260716.html",
        "WebDashboard_EBM_VanDeCuThe_COPD_DoiTuongDacBiet_DaBenh_20260805.html",
    ]

    def test_khong_con_loi_an_toan(self):
        if self.DASH is None:
            self.skipTest("không tìm thấy thư mục EBM-Dashboards (bản test nguồn git)")
        for ten in self.FILES:
            p = self.DASH / ten
            if not p.exists():
                self.skipTest(f"không có {ten}")
            html = p.read_text(encoding="utf-8")
            db = vd.extract_data_block(html)
            items = vd.split_items(db)
            errors, _warns, _oks = vd.strict_source_checks(db, items)
            self.assertEqual(errors, [], f"{ten} còn lỗi cứng: {errors}")

    def test_moi_mien_tru_deu_co_khai_bao_that(self):
        """Mọi item 'apply' trên gradeLevel yếu phải có normativeBasis hợp lệ."""
        if self.DASH is None:
            self.skipTest("không tìm thấy thư mục EBM-Dashboards (bản test nguồn git)")
        for ten in self.FILES:
            p = self.DASH / ten
            if not p.exists():
                continue
            db = vd.extract_data_block(p.read_text(encoding="utf-8"))
            for ch in vd.split_items(db):
                if vd.field(ch, "decision") != "apply":
                    continue
                if vd.field(ch, "gradeLevel") not in {"low", "vlow", "na"}:
                    continue
                basis = vd.field(ch, "normativeBasis")
                self.assertIn(basis, vd.NORMATIVE_BASES,
                              f"{ten}:{vd.field(ch, 'id')} miễn trừ mà khai {basis!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
