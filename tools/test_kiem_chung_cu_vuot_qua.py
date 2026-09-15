#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy cho `kiem_chung_cu_vuot_qua.py` — ngoại tuyến, không mạng, không PII.

Rủi ro THẬT được canh (14/09/2026): NCBI chặn địa chỉ mạng của máy ⇒ mọi lời gọi elink
trả trang HTML ⇒ `tong_quan_moi_hon()` trả `[]` như thể "không có bài mới" ⇒ công cụ in
🟢 "không thấy tổng quan/gộp/guideline nào MỚI HƠN" cho 12/12 PMID mà thực tế chưa hỏi
được một PMID nào. Luật: KHÔNG HỎI ĐƯỢC thì KHÔNG BAO GIỜ được in xanh.

Chạy:  python3 tools/test_kiem_chung_cu_vuot_qua.py
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
spec = importlib.util.spec_from_file_location("kcv_test", TOOLS / "kiem_chung_cu_vuot_qua.py")
kcv = importlib.util.module_from_spec(spec)
sys.modules["kcv_test"] = kcv          # @dataclass/annotation cần module đã đăng ký (bài học _nap)
spec.loader.exec_module(kcv)

ELINK_RONG = {"linksets": [{"linksetdbs": []}]}
ELINK_CO_ID = {"linksets": [{"linksetdbs": [{"links": ["99999999"]}]}]}


def _goc_verify_dashboard() -> Path | None:
    """Thư mục chứa tools/verify_dashboard.py: cây dữ liệu thật, hoặc bản vendor trong skill."""
    for goc in (REPO / "EBM-Dashboards", REPO / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa"):
        if (goc / "tools" / "verify_dashboard.py").exists():
            return goc
    return None


class HamDungChungTachHaiNghia(unittest.TestCase):
    def test_khong_hoi_duoc_elink_tra_None_khong_phai_danh_sach_rong(self):
        with mock.patch.object(kcv, "_goi", lambda url, cho=25: None):
            self.assertIsNone(kcv.tong_quan_moi_hon("11111111", 2020, None))

    def test_hoi_duoc_ma_khong_co_lien_ket_tra_danh_sach_rong(self):
        with mock.patch.object(kcv, "_goi", lambda url, cho=25: ELINK_RONG):
            self.assertEqual(kcv.tong_quan_moi_hon("11111111", 2020, None), [])

    def test_elink_duoc_nhung_esummary_hong_van_la_None(self):
        def gia(url, cho=25):
            return ELINK_CO_ID if "elink.fcgi" in url else None
        with mock.patch.object(kcv, "_goi", gia):
            self.assertIsNone(kcv.tong_quan_moi_hon("11111111", 2020, None))


class PhanLoaiKetLuan(unittest.TestCase):
    def test_bang_phan_loai(self):
        self.assertEqual(kcv.phan_loai(0, 0, 0), "CHUA_DO")
        self.assertEqual(kcv.phan_loai(12, 0, 12), "KHONG_HOI_DUOC")
        self.assertEqual(kcv.phan_loai(12, 0, 3), "MOT_PHAN")
        self.assertEqual(kcv.phan_loai(12, 2, 3), "CO_BAI_MOI")
        self.assertEqual(kcv.phan_loai(12, 0, 0), "SACH")


class MainKhongInXanhKhiKhongHoiDuoc(unittest.TestCase):
    """Đi TRỌN đường main() — không chỉ thử hàm con (luật 4 của chot_hoi_quy_bai_hoc)."""

    def _chay_main(self, goi_gia):
        goc = _goc_verify_dashboard()
        if goc is None:
            self.skipTest("không có verify_dashboard.py (cả cây dữ liệu lẫn bản vendor) — CHƯA KIỂM, không phải ĐẠT")
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "WebDashboard_EBM_VanDeCuThe_ThuNghiem_20260914.html"
            db.write_text(
                '<script>\nconst DATA = {\n  meta: { updated: "2026-09-14" },\n  items: [\n'
                '    { id: "ITEM-01", title: "Muc thu nhat", decision: "apply", pmid: "11111111", dateVersion: "01/2020" },\n'
                '    { id: "ITEM-02", title: "Muc thu hai", decision: "apply", pmid: "22222222", dateVersion: "01/2021" }\n'
                '  ]\n};\n/* ▲▲▲  HẾT KHỐI DATA  ▲▲▲ */\n</script>\n', encoding="utf-8")
            out = io.StringIO()
            with mock.patch.object(kcv, "DASH", goc), mock.patch.object(kcv, "_goi", goi_gia), \
                 mock.patch.object(kcv.time, "sleep", lambda s: None), \
                 mock.patch.object(sys, "argv", ["kiem_chung_cu_vuot_qua.py", "--file", str(db)]), \
                 contextlib.redirect_stdout(out):
                rc = kcv.main()
        return rc, out.getvalue()

    def test_ncbi_chan_toan_bo_thi_khong_in_xanh_va_ma_thoat_khac_0(self):
        rc, van = self._chay_main(lambda url, cho=25: None)
        self.assertNotIn("🟢", van, "KHÔNG hỏi được mà vẫn in xanh — đúng lỗi 14/09/2026")
        self.assertIn("KHÔNG HỎI ĐƯỢC", van)
        self.assertEqual(rc, 2)

    def test_hoi_duoc_that_su_khong_co_bai_moi_van_duoc_in_xanh(self):
        rc, van = self._chay_main(lambda url, cho=25: ELINK_RONG)
        self.assertIn("🟢", van, "đường âm tính THẬT không được bị vá hỏng")
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
