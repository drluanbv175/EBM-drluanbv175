#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""Hồi quy phát hiện HIGH của Workflow đối kháng đa-agent vòng 3 (2026-09-04) trong
verify_dashboard.py::_MANH_RE/_co_bang_chung_khuyen_cao_manh() — dương tính giả trên
"NYHA class I" và các mention rời rạc khác.

`normative_exemption()` cho phép một item `gradeLevel='low'/'vlow'` (chứng cứ chất
lượng THẤP) vẫn giữ `decision='apply'` NẾU `gradeSource` trích được bằng chứng nguyên
văn nguồn tuyên bố khuyến cáo MẠNH (`normativeBasis='guideline-strong-rec'`). Trước bản
vá, `_MANH_RE` có 3 alternative KHÔNG đòi ngữ cảnh: `class\s*i\b`, `loại\s*i\b`, và
`1[abc]` trần — khớp NHẦM mọi hệ phân loại lâm sàng khác dùng cùng chữ số La Mã/chữ cái
(NYHA class I — độ suy tim, ASA class I, Killip class, số bảng/phụ lục "Bảng 1A"), không
liên quan gì tới ĐỘ MẠNH khuyến cáo. Hậu quả: một gradeSource ghi "NYHA class I" + TỰ
KHAI "guideline không nêu rõ mức khuyến cáo" vẫn được miễn oan luật gradeLevel — một
khuyến cáo 'apply' trên chứng cứ rất yếu đi qua cổng --strict-sources sạch sẽ.

Nguyên tắc viết test: gọi THẲNG _co_bang_chung_khuyen_cao_manh()/normative_exemption(),
không grep chuỗi trong mã nguồn.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_dashboard as vd  # noqa: E402


class TestNyhaClassIKhongDuocTinhLaKhuyenCaoManh(unittest.TestCase):
    """★★ Ca chính, đúng nguyên văn kịch bản trong finding."""

    def test_nyha_class_i_khong_kich_hoat_mien_tru(self):
        text = ("Khuyến cáo áp dụng cho bệnh nhân suy tim NYHA class I theo bảng phân độ "
                "chức năng; guideline không nêu rõ mức khuyến cáo cho khuyến cáo này")
        self.assertFalse(vd._co_bang_chung_khuyen_cao_manh(text))

    def test_normative_exemption_khong_mien_oan_cho_nyha(self):
        # grade='vlow' (khác 'na') mà KHÔNG có bằng chứng khuyến cáo mạnh thật ⇒
        # normative_exemption() trả (False, None) — ly_do chỉ được điền ở nhánh
        # grade='na', đây là hợp đồng SẴN CÓ của hàm, không phải điều bản vá này đổi.
        duoc, ly_do = vd.normative_exemption(
            "Guideline", "vlow", "guideline-strong-rec",
            "NYHA class I; guideline không nêu rõ mức khuyến cáo cho khuyến cáo này",
        )
        self.assertFalse(duoc)

    def test_asa_class_i_khong_kich_hoat_mien_tru(self):
        self.assertFalse(vd._co_bang_chung_khuyen_cao_manh(
            "Bệnh nhân ASA class I trước phẫu thuật, không có bệnh lý nền"))

    def test_bang_phu_luc_danh_so_1a_khong_kich_hoat_mien_tru(self):
        self.assertFalse(vd._co_bang_chung_khuyen_cao_manh(
            "Xem chi tiết ở Bảng 1A và Phụ lục 1C của guideline gốc"))

    def test_soi_tren_toan_van_ket_qua_end_to_end_strict_source_checks(self):
        """Tái hiện end-to-end như repro_notes của finding: item apply/vlow với
        gradeSource chỉ mention NYHA class I (không phải khuyến cáo mạnh thật)
        phải bị CHẶN bởi strict_source_checks(), không được miễn oan."""
        data_block = """
        const DATA = {
          standards:{frame:'x', sourceHierarchy:'x', reporting:'x', appraisal:'x',
                     currency:'2026-09-01', safety:'x', vietnamFit:'x',
                     searchSources:['PubMed','Guideline'], gates:['x']},
        };
        """
        chunk = (
            "{id:'ITEM-01', design:'Guideline', gradeLevel:'vlow', decision:'apply', "
            "source:'x', org:'x', dateVersion:'2024', "
            "gradeSource:'NYHA class I; guideline không nêu rõ mức khuyến cáo cho "
            "khuyến cáo này', normativeBasis:'guideline-strong-rec', "
            "references:['x']}"
        )
        errors, warns, oks = vd.strict_source_checks(data_block, [chunk],
                                                      today=vd.date(2026, 9, 4))
        self.assertTrue(
            any("decision='apply'" in e and "ITEM-01" in e for e in errors),
            f"errors={errors!r} oks={oks!r}",
        )


class TestDoiChungKhuyenCaoManhThatVanDuocMienTru(unittest.TestCase):
    """Đối chứng BẮT BUỘC: khuyến cáo MẠNH THẬT (ACC/AHA 'Class of Recommendation I'/
    'COR I' đi kèm chữ 'recommendation'/'khuyến cáo' ở gần) vẫn phải được nhận diện —
    bản vá không được thu hẹp tới mức mất khả năng phát hiện thật."""

    def test_class_of_recommendation_i_duoc_nhan_dien(self):
        self.assertTrue(vd._co_bang_chung_khuyen_cao_manh(
            "ACC/AHA Class of Recommendation: I, Level of Evidence B"))

    def test_cor_i_viet_tat_duoc_nhan_dien(self):
        self.assertTrue(vd._co_bang_chung_khuyen_cao_manh("COR I, LOE A"))

    def test_khuyen_cao_loai_i_tieng_viet_duoc_nhan_dien(self):
        self.assertTrue(vd._co_bang_chung_khuyen_cao_manh(
            "Khuyến cáo loại I, mức bằng chứng B theo phân loại ACC/AHA"))

    def test_class_i_recommendation_dang_tinh_tu_pho_bien_nhat_duoc_nhan_dien(self):
        """Dạng thật phổ biến nhất trong guideline ACC/AHA: 'Class I' đứng TRƯỚC,
        'recommendation' theo ngay sau như tính từ bổ nghĩa."""
        self.assertTrue(vd._co_bang_chung_khuyen_cao_manh(
            "This is a Class I recommendation for statin therapy"))

    def test_class_i_voi_chu_thich_ngoac_don_duoc_nhan_dien(self):
        self.assertTrue(vd._co_bang_chung_khuyen_cao_manh(
            "Class I (strong) recommendation based on multiple RCTs"))

    def test_we_recommend_van_dung_nhu_cu(self):
        self.assertTrue(vd._co_bang_chung_khuyen_cao_manh("We recommend this treatment"))

    def test_grade_1a_van_dung_nhu_cu(self):
        self.assertTrue(vd._co_bang_chung_khuyen_cao_manh("GRADE 1A recommendation"))

    def test_co_dieu_kien_van_thang_du_co_class_i_gan_khuyen_cao(self):
        """Đối chứng: dấu hiệu CÓ ĐIỀU KIỆN vẫn phải thắng ngay cả khi câu có
        'class I' + 'recommendation' đứng gần — không được để bản vá làm suy yếu
        luật ưu tiên có sẵn."""
        self.assertFalse(vd._co_bang_chung_khuyen_cao_manh(
            "Class of Recommendation I nhưng đây là khuyến cáo có điều kiện"))


if __name__ == "__main__":
    unittest.main()
