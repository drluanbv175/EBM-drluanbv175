#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""`kiem_so_lieu.py::main` — vá 21/09/2026 (đánh giá hoàn thiện, việc #2d). Ngoại tuyến, không PII.

Ca thật: khi MỌI truy vấn tóm tắt PubMed hỏng (NCBI chặn), `hong` = tổng, `can_doc` rỗng ⇒ bản cũ in «🟢 Mọi hiệu số đều tìm
thấy đủ trong tóm tắt» và thoát 0. Đúng họ BH27/BH32: công cụ chạy, in kết quả hợp lệ, nhưng thứ cần kiểm không được kiểm.
Luật: không đọc được ⇒ mã thoát 2 và KHÔNG xanh; mẫu (`--gioi-han`, `--file`) ⇒ nói là mẫu, không xanh cho «cả kho».
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
sys.path.insert(0, str(TOOLS))
import kiem_so_lieu as ksl  # noqa: E402

TT_KHOP = "Result: HR 0.72 (95% CI, 0.6 to 0.86). Conclusion: benefit."


def _dashboard(td: Path) -> Path:
    f = td / "WebDashboard_EBM_VanDeCuThe_ThuNghiem_20260921.html"
    # bh10-mien: fixture giả ghi vào thư mục tạm để thử kiem_so_lieu, không phải dashboard thật
    f.write_text(
        '<script>\nconst DATA = {\n  meta: { updated: "2026-09-21" },\n  items: [\n'
        '    { id: "ITEM-01", decision: "apply", pmid: "11111111", measure: "hr", effect: { hr: 0.72, lo: 0.60, hi: 0.86 } },\n'
        '    { id: "ITEM-02", decision: "apply", pmid: "22222222", measure: "hr", effect: { hr: 0.72, lo: 0.60, hi: 0.86 } }\n'
        '  ]\n};\n/* ▲▲▲  HẾT KHỐI DATA  ▲▲▲ */\n</script>\n', encoding="utf-8")
    return f


class KhongXanhKhiKhongDo(unittest.TestCase):
    def _chay(self, lay_tt, *them):
        with tempfile.TemporaryDirectory() as td:
            f = _dashboard(Path(td))
            out = io.StringIO()
            with mock.patch.object(ksl, "lay_tom_tat", lay_tt), mock.patch.object(ksl.time, "sleep", lambda s: None), \
                 mock.patch.object(sys, "argv", ["kiem_so_lieu.py", "--file", str(f), *them]), contextlib.redirect_stdout(out):
                rc = ksl.main()
        return rc, out.getvalue()

    def test_moi_truy_van_hong_khong_in_xanh_va_thoat_2(self):
        rc, van = self._chay(lambda pm: None)
        self.assertNotIn("🟢", van, "đúng lỗi cũ: mọi truy vấn hỏng nhưng vẫn in xanh")
        self.assertEqual(rc, 2)
        self.assertIn("KHÔNG ĐO ĐƯỢC 2/2", van)

    def test_mot_phan_hong_van_khong_xanh(self):
        rc, van = self._chay(lambda pm: TT_KHOP if pm == "11111111" else None)
        self.assertNotIn("🟢", van)
        self.assertIn("KHÔNG ĐO ĐƯỢC 1/2", van)

    def test_mau_khop_het_khong_duoc_doc_la_ca_kho_sach(self):
        rc, van = self._chay(lambda pm: TT_KHOP, "--gioi-han", "1")
        self.assertNotIn("🟢", van)
        self.assertIn("MẪU", van)
        self.assertEqual(rc, 0)

    def test_khong_co_muc_nao_de_doi_chieu_la_chua_do_thoat_2(self):
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "WebDashboard_EBM_VanDeCuThe_Rong_20260921.html"
            f.write_text("<script>\nconst DATA = { items: [] };\n/* ▲▲▲  HẾT KHỐI DATA  ▲▲▲ */\n</script>", encoding="utf-8")
            out = io.StringIO()
            with mock.patch.object(sys, "argv", ["kiem_so_lieu.py", "--file", str(f)]), contextlib.redirect_stdout(out):
                rc = ksl.main()
        self.assertEqual(rc, 2)
        self.assertNotIn("🟢", out.getvalue())
        self.assertNotIn("truy vấn tóm tắt hỏng", out.getvalue(), "lý do phải nói đúng: KHÔNG có mục, không phải mạng hỏng")

    def test_in_tham_so_dau_bao_cao(self):
        _rc, van = self._chay(lambda pm: TT_KHOP)
        self.assertIn("tham số:", van)

    def test_do_du_khop_het_toan_kho_van_xanh_duong_that_khong_bi_va_hong(self):
        with tempfile.TemporaryDirectory() as td:
            f = _dashboard(Path(td))
            out = io.StringIO()
            # TOÀN KHO = glob DASH ⇒ trỏ DASH vào thư mục tạm chỉ có một dashboard
            with mock.patch.object(ksl, "DASH", Path(td)), mock.patch.object(ksl, "lay_tom_tat", lambda pm: TT_KHOP), \
                 mock.patch.object(ksl.time, "sleep", lambda s: None), \
                 mock.patch.object(sys, "argv", ["kiem_so_lieu.py"]), contextlib.redirect_stdout(out):
                rc = ksl.main()
        self.assertEqual(rc, 0)
        self.assertIn("🟢", out.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
