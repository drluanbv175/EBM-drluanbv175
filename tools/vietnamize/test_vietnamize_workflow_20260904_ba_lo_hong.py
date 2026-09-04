#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy 3 phát hiện MEDIUM của Workflow đối kháng đa-agent 2026-09-04 (task
#67, nhánh audit `tools/vietnamize/*.py`):

1. `build_danh_muc.py`/`build_trang_tra_cuu.py` thiếu fallback khoá
   `name:<tên>` mà `apply_vi.py`/`verify_vi.py` đã có — bản dịch DÙNG CHUNG
   cho mọi bản sao cùng tên (vd bmad-method lặp nguyên bộ skill ở 6 plugin
   con) không tới được hai công cụ sinh trang này. Xác nhận trên chính
   catalog thật của repo: 75/1070 mục ở `catalog_may/Linux.json` chỉ tra
   được bản dịch qua khoá `name:`, không có khoá `id` trực tiếp.
2. `build_trang_tra_cuu.py` nhúng JSON vào `<script>` không thoát chuỗi
   "</" — một mô tả plugin bên thứ ba (KHÔNG kiểm soát được, khác
   `vi_descriptions.json` đã được bác sĩ duyệt) chứa literal "</script>"
   sẽ đóng thẻ script sớm, phá JS và chèn phần còn lại thành HTML thô.
   Latent trên dữ liệu hiện có, nhưng là lỗ hổng cấu trúc thật.
3. `sinh_lenh_viet.py` ghi frontmatter YAML bằng `.format()` thuần, không
   thoát dấu ngoặc kép trong mô tả — một mô tả chứa `"` sẽ làm hỏng cú
   pháp YAML. Latent (0 mục hiện tại có dấu ngoặc kép), khác
   `apply_vi.py::replace_field()` đã dùng đúng `json.dumps()` cho vấn đề
   này.

Nguyên tắc viết test: gọi THẲNG hàm nguồn, không grep chuỗi trong mã.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_danh_muc as bdm  # noqa: E402
import build_trang_tra_cuu as btc  # noqa: E402
import sinh_lenh_viet as slv  # noqa: E402


class TestFallbackKhoaNameBuildDanhMuc(unittest.TestCase):
    """★★ Phát hiện 1a — build_danh_muc.py::mo_ta_vi() phải tra được bản
    dịch qua khoá `name:<tên>` khi không có khoá `id` trực tiếp."""

    def test_chi_co_khoa_name_van_lay_dung_ban_dich(self):
        vi = {"name:mot-skill-lap-lai": {"vi": "Bản dịch tiếng Việt qua tên"}}
        i = {"id": "skill:plugin-a:mot-skill-lap-lai", "name": "mot-skill-lap-lai",
             "desc_en": "English placeholder"}
        self.assertEqual(bdm.mo_ta_vi(vi, i), "Bản dịch tiếng Việt qua tên")

    def test_co_khoa_id_truc_tiep_van_uu_tien_id(self):
        """★★ Đối chứng bắt buộc — id vẫn thắng name: (khớp thứ tự ưu tiên
        của apply_vi.py: 'id luôn thắng fallback')."""
        vi = {
            "skill:plugin-a:mot-skill": {"vi": "Bản dịch theo ID (đúng)"},
            "name:mot-skill": {"vi": "Bản dịch theo TÊN (không nên dùng ở đây)"},
        }
        i = {"id": "skill:plugin-a:mot-skill", "name": "mot-skill", "desc_en": "English"}
        self.assertEqual(bdm.mo_ta_vi(vi, i), "Bản dịch theo ID (đúng)")

    def test_khong_co_ca_hai_khoa_roi_ve_desc_en(self):
        vi: dict = {}
        i = {"id": "skill:x:y", "name": "y", "desc_en": "English fallback"}
        self.assertEqual(bdm.mo_ta_vi(vi, i), "English fallback")


class TestFallbackKhoaNameBuildTrangTraCuu(unittest.TestCase):
    """★★ Phát hiện 1b — build_trang_tra_cuu.py::nap_ban_chup() phải tra
    được bản dịch qua khoá `name:<tên>` khi item không có khoá `id`
    khớp trực tiếp trong lớp phủ."""

    def test_nap_ban_chup_dung_fallback_name(self, ):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            vi_desc = tmp_path / "vi_descriptions.json"
            vi_desc.write_text(json.dumps({
                "name:mot-skill-lap-lai": {"vi": "Bản dịch qua tên"},
            }, ensure_ascii=False), encoding="utf-8")
            snap_dir = tmp_path / "catalog_may"
            snap_dir.mkdir()
            (snap_dir / "TestMachine.json").write_text(json.dumps({
                "may": "TestMachine",
                "ngay_quet": "2026-09-04",
                "muc": [{
                    "id": "skill:plugin-a:mot-skill-lap-lai",
                    "name": "mot-skill-lap-lai",
                    "kind": "kỹ năng",
                    "desc_en": "English placeholder",
                }],
            }, ensure_ascii=False), encoding="utf-8")

            old_vi_desc, old_snap_dir = btc.VI_DESC, btc.SNAP_DIR
            try:
                btc.VI_DESC = vi_desc
                btc.SNAP_DIR = snap_dir
                muc, _ngay = btc.nap_ban_chup()
            finally:
                btc.VI_DESC, btc.SNAP_DIR = old_vi_desc, old_snap_dir

            self.assertEqual(len(muc), 1)
            self.assertEqual(muc[0]["desc_en"], "Bản dịch qua tên")


class TestNhungJsonVaoScriptThoatDungThe(unittest.TestCase):
    """★★ Phát hiện 2 — DATA nhúng vào <script> không được để lọt chuỗi
    "</script" (đóng thẻ sớm, phá JS + chèn HTML thô)."""

    def _sinh(self, mo_ta: str) -> str:
        muc = [{"ten": "x", "loai": "kỹ năng", "nhom": "n", "goi": "/x",
               "goi_khac": [], "may": ["Linux"], "mo_ta": mo_ta}]
        return btc.sinh_html(muc, [], {"Linux": "2026-09-04"})

    def test_mo_ta_chua_dong_script_khong_lot_ra_ngoai(self):
        html_ra = self._sinh('Mô tả có chèn </script><script>alert(1)</script> để thử')
        self.assertNotIn("</script", html_ra.lower().replace(
            "</script></body></html>", "").replace("</style></head>", ""))

    def test_du_lieu_binh_thuong_van_hien_thi_dung(self):
        """★★ Đối chứng bắt buộc — mô tả bình thường (không có "</") vẫn
        phải xuất hiện nguyên vẹn trong HTML sinh ra."""
        html_ra = self._sinh("Tính điểm CURB-65 cho viêm phổi cộng đồng")
        self.assertIn("Tính điểm CURB-65 cho viêm phổi cộng đồng", html_ra)

    def test_du_lieu_co_dau_gach_cheo_thuong_khong_bi_doi(self):
        """★★ Đối chứng — dấu "/" đơn lẻ (không đứng sau "<") không bị đổi,
        chỉ riêng chuỗi "</" mới bị thoát."""
        html_ra = self._sinh("Tỷ lệ 1/3 bệnh nhân cần theo dõi thêm")
        self.assertIn("1/3", html_ra)


class TestSinhLenhVietThoatDauNgoacKepFrontmatter(unittest.TestCase):
    """★★ Phát hiện 3 — sinh_lenh_viet.py::sinh_noi_dung() phải sinh
    frontmatter YAML hợp lệ dù mô tả có dấu " (json.dumps thay vì .format()
    thuần)."""

    def test_mo_ta_co_dau_ngoac_kep_van_ra_yaml_hop_le(self):
        mo_ta_doc = 'Tính điểm "CURB-65" cho viêm phổi'
        noi_dung = slv.sinh_noi_dung(mo_ta_doc, "Nội dung lệnh")
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML không có trên máy này — bỏ qua bước parse thật")
        fm = noi_dung.split("---")[1]
        parsed = yaml.safe_load(fm)
        self.assertEqual(parsed["description"], mo_ta_doc)

    def test_mo_ta_binh_thuong_khong_doi_hanh_vi(self):
        mo_ta_doc = "Tính cỡ mẫu nghiên cứu cắt ngang"
        noi_dung = slv.sinh_noi_dung(mo_ta_doc, "Nội dung lệnh")
        self.assertIn(f'description: "{mo_ta_doc}"', noi_dung)


if __name__ == "__main__":
    unittest.main()
