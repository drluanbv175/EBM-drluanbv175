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




class TestPhanXuRutVaThay(unittest.TestCase):
    """Khớp phân xử rút-và-thay — vá 15/08/2026 (ca ITEM-05 ViemGanB).

    Item khai chuẩn cố ý để pmid:"" (nguồn chính là DOI bản thay), PMID bài gốc
    CHỈ nằm ở replacesPmid — bộ khớp phải nhận đường này. Đồng thời khoá các
    đường lách: decision khác notyet, hay bài rút BỎ HẲN (không rut_va_thay),
    đều KHÔNG được phân xử.
    """

    ITEM = (
        'const DATA = { items:[ {id:"ITEM-05", pmid:"", '
        'doi:"10.1001/jamaoncol.2018.4070", replacesPmid:"30267080", '
        'replacementNoticePmid:"31021386", '
        'replacementNoticeDoi:"10.1001/jamaoncol.2019.0576", '
        'dateVersion:"2019 (bản thay thế)", decision:"%s", '
        'gradeSource:"số liệu lấy từ bản thay thế", flag:"x"} ] }\n// HẾT KHỐI DATA'
    )

    def _viet(self, decision):
        import tempfile, os
        f = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False,
                                        encoding="utf-8")
        f.write(self.ITEM % decision)
        f.close()
        self.addCleanup(os.unlink, f.name)
        return f.name

    def test_khop_qua_replacesPmid_khi_pmid_rong(self):
        rec = {"loai": "pmid", "gia_tri": "30267080", "rut_va_thay": True,
               "thong_bao": "31021386"}
        self.assertEqual(
            vd._replacement_acknowledgement(self._viet("notyet"), rec), "ITEM-05")

    def test_decision_apply_khong_duoc_phan_xu(self):
        rec = {"loai": "pmid", "gia_tri": "30267080", "rut_va_thay": True}
        self.assertIsNone(vd._replacement_acknowledgement(self._viet("apply"), rec))

    def test_rut_bo_han_khong_bao_gio_duoc_phan_xu(self):
        rec = {"loai": "pmid", "gia_tri": "30267080", "rut_va_thay": False}
        self.assertIsNone(vd._replacement_acknowledgement(self._viet("notyet"), rec))


class TestPhanBietThieuTieuDeVsTraoThat(unittest.TestCase):
    """Khoá bản vá 2026-08-24 (Sprint 10): overlap tiêu đề thấp phải được phân biệt
    thành 'references[] thiếu tiêu đề gốc' (KHÔNG phải bằng chứng tráo, vẫn chặn
    strict-sources nhưng với thông điệp đúng bản chất + gợi ý sửa đúng) khỏi 'nghi
    tráo thật' (entry đủ dài mà vẫn không khớp — giữ nguyên thông điệp cũ). Đo thực
    nghiệm: 8/8 lỗi cứng liên tiếp của một đợt quét 67 dashboard đều là trường hợp
    thứ nhất — bản vá KHÔNG được làm yếu khả năng bắt trường hợp thứ hai."""

    REAL_TITLE = ("2026 ACC/AHA/AACVPR/ABC/ACPM/ADA/AGS/APhA/ASPC/NLA/PCNA Guideline "
                  "on the Management of Dyslipidemia: A Report of the American College "
                  "of Cardiology/American Heart Association Joint Committee")

    # ── _find_reference_entry_for_pmid ──────────────────────────────────────

    def test_tim_thay_entry_chua_dung_pmid(self):
        ch = "references:['Long B, Gottlieb M. Am J Emerg Med. 2026. PMID 42127879.']"
        entry = vd._find_reference_entry_for_pmid(ch, "42127879")
        self.assertIsNotNone(entry)
        self.assertIn("42127879", entry)

    def test_khong_tim_thay_khi_pmid_khong_xuat_hien_trong_references(self):
        ch = "references:['Fraenkel L, et al. Arthritis Rheumatol. 2021. PMID 34101376.']"
        self.assertIsNone(vd._find_reference_entry_for_pmid(ch, "99999999"))

    def test_khong_tim_thay_khi_thieu_hoan_toan_references(self):
        ch = "title:'Không có references nào', action:'test'"
        self.assertIsNone(vd._find_reference_entry_for_pmid(ch, "42127879"))

    # ── _reference_entry_missing_title ──────────────────────────────────────

    def test_entry_ngan_thieu_tieu_de_la_true(self):
        # Đúng ca thật CAP_ATS2025 ITEM-03 trước khi sửa: chỉ tác giả+tạp chí+năm+PMID.
        entry = "Long B, Gottlieb M. Am J Emerg Med. 2026;107:16-20. PMID 42127879."
        self.assertTrue(vd._reference_entry_missing_title(entry, self.REAL_TITLE))

    def test_entry_du_dai_co_tieu_de_la_false(self):
        entry = (
            "Long B, Gottlieb M. 2025 guideline updates for community-acquired "
            "pneumonia diagnosis and management. Am J Emerg Med. 2026;107:16-20. "
            "PMID 42127879."
        )
        # Cùng entry NHƯNG so với tiêu đề ngắn hơn (CAP thay vì dyslipidemia đa hội) —
        # kiểm đúng ngữ cảnh thật thay vì trộn tiêu đề của case khác.
        real_title_cap = "2025 guideline updates for community-acquired pneumonia diagnosis and management."
        self.assertFalse(vd._reference_entry_missing_title(entry, real_title_cap))

    def test_gioi_han_co_chu_y_entry_dai_do_tac_gia_khong_duoc_nhan_dien(self):
        """GIỚI HẠN CÓ CHỦ Ý, không phải bug: khi tên tác giả (nhiều đồng tác giả) +
        tên tạp chí KHÔNG viết tắt khiến entry tình cờ dài gần bằng một tiêu đề
        multi-society cũng rất dài, thuật toán so ĐỘ DÀI không phân biệt được — và
        NGHIÊNG VỀ AN TOÀN (coi vẫn có thể là 'nghi tráo', không tự ý nới lỏng) thay
        vì đoán liều là 'thiếu tiêu đề'. Đây là đánh đổi có chủ ý: thà báo động giả
        thêm ở ca hiếm này còn hơn làm yếu khả năng bắt tráo thật ở ca không chắc
        chắn. ĐỪNG sửa hàm để test này pass — nếu cần xử lý ca này, phải là một tín
        hiệu MẠNH HƠN (vd so khớp cấu trúc "Tên. Tiêu đề. Tạp chí." bằng dấu chấm),
        không phải nới ngưỡng độ dài."""
        entry = ("Blumenthal RS, Morris PB, Gaudino M, Johnson HM, Anderson TS, et al. "
                 "Journal of the American College of Cardiology. 2026;87(19). PMID 41824590.")
        self.assertFalse(vd._reference_entry_missing_title(entry, self.REAL_TITLE))

    def test_entry_rong_khong_loi(self):
        self.assertFalse(vd._reference_entry_missing_title("", self.REAL_TITLE))
        self.assertFalse(vd._reference_entry_missing_title(None, self.REAL_TITLE))

    # ── _title_mismatch_message — hành vi tổng hợp ──────────────────────────

    def test_message_thieu_tieu_de_khong_noi_nghi_trao(self):
        ch = "references:['Long B, Gottlieb M. Am J Emerg Med. 2026. PMID 42127879.']"
        msg = vd._title_mismatch_message("ITEM-03", "42127879", self.REAL_TITLE, ch, 0.14)
        self.assertIn("KHÔNG ĐỦ DỮ LIỆU", msg)
        self.assertNotIn("NGHI TRÁO PMID", msg)
        self.assertIn("bổ sung", msg.lower())

    def test_message_khong_co_reference_van_la_nghi_trao(self):
        """references[] hoàn toàn không nhắc PMID này — KHÔNG có cơ sở nào để nói
        'chỉ thiếu tiêu đề', nên giữ nguyên mức nghiêm ngặt cũ."""
        ch = "title:'ITEM khác chủ đề', action:'không liên quan'"
        msg = vd._title_mismatch_message("ITEM-13", "34153348", self.REAL_TITLE, ch, 0.0)
        self.assertIn("NGHI TRÁO PMID", msg)

    def test_message_entry_du_dai_ma_van_khong_khop_la_nghi_trao_that(self):
        """Entry ĐỦ DÀI (đủ chỗ chứa tiêu đề) nhưng vẫn không khớp — đây mới là
        trường hợp heuristic PHẢI giữ nguyên mức nghiêm ngặt, không được nới lỏng."""
        # Entry dài, có vẻ đủ chứa 1 tiêu đề — nhưng tiêu đề đó không phải REAL_TITLE.
        ch = ("references:['Smith J, Doe A, Nguyen K, et al. Một tiêu đề hoàn toàn "
              "khác về chủ đề khác, dài ngang bằng tiêu đề thật để không bị coi là "
              "thiếu, nhưng nội dung sai be bét. J Fake Journal. 2020. PMID 41824590.']")
        msg = vd._title_mismatch_message("ITEM-01", "41824590", self.REAL_TITLE, ch, 0.05)
        self.assertIn("NGHI TRÁO PMID", msg)


if __name__ == "__main__":
    unittest.main(verbosity=2)
