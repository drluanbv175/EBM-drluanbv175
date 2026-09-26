#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy phát hiện #11 (26/09/2026): `xuat_goi_cap_nhat.py` chạy KHÔNG có `--online`
thì bỏ TOÀN BỘ cổng liêm chính mà vẫn trả mã 0, in «Bộ năm đã sẵn sàng (5/5)».

Các luật KHÔNG cần mạng — khoá summary lạ (BH61), `decision='apply'` trên gradeLevel
na/low (strict_source_checks), nguồn rút đã có trong sổ — bị bỏ qua hoàn toàn, lệch với
tuyến ops/orchestrator B2 (luôn chạy --strict-sources kể cả ngoại tuyến, BH96).

Bản vá: một hàm `_chay_cong(co_online)` dùng cho CẢ hai chế độ. Ngoại tuyến: vẫn chặn
xuất (mã 3) với lỗi cứng thật; bản Word không bao giờ nhận `--verified`; tiêu đề tổng kết
mang hậu tố «CHƯA xác minh nguồn sống». KHÔNG dùng mã 2 cho «ngoại tuyến» (orchestrator
đọc B4 rc=2 là thiếu công cụ).

Nguyên tắc viết test:
  · Các ca SỐNG gọi CHÍNH verify_dashboard.py thật (bản vendor có track git) qua `run()` gốc
    — để bắt cả trường hợp verify_dashboard đổi câu chữ thông điệp «decision='apply'» làm
    nhánh chặn im lặng hết tác dụng (rủi ro phản biện đã nêu).
  · Các ca ĐƠN VỊ giả `run()` để tách bạch từng nhánh, đếm lời gọi công cụ con — không grep
    mã nguồn.
  · Không mạng, không ghi vào cây repo (build_ban_doc thật không bao giờ được chạy).
"""
from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
VERIFY_NGUON = HERE.parent / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "verify_dashboard.py"


def _nap_module(ten: str, duong_dan: Path):
    spec = importlib.util.spec_from_file_location(ten, duong_dan)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[ten] = mod
    spec.loader.exec_module(mod)
    return mod


XGCN = _nap_module("xuat_goi_cap_nhat_ngoai_tuyen_20260926", HERE / "xuat_goi_cap_nhat.py")
RUN_GOC = XGCN.run

_DAU = """<!doctype html><html><body>
<!-- Cần bác sĩ kiểm chứng -->
<script>
const DATA = {
  meta:{kind:'cong-cu', updated:'2026-09-26', question:'Test ngoại tuyến'},
"""
_CUOI = """
};
/* ▲▲▲  HẾT KHỐI DATA  ▲▲▲ */
</script>
</body></html>
"""

# Lỗi BH61: khoá `notDo` thay vì `dontDo` — lượt verify THƯỜNG (không strict) chặn.
DASH_KHOA_LA = _DAU + (
    "  summary:{conclusion:'Kết luận thử.', doNow:['Việc nên làm'], notDo:['Không ngừng thuốc'],"
    " redFlags:[]},\n  items:[]") + _CUOI

# Lượt THƯỜNG đạt; lượt --strict-sources báo «decision='apply' nhưng gradeLevel='na'».
DASH_APPLY_NA = _DAU + (
    "  summary:{conclusion:'Kết luận thử.', doNow:['Việc nên làm'], dontDo:['Không làm'],"
    " redFlags:[]},\n  items:[\n    {id:'IT-01', title:'Khuyến cáo thử', design:'Cohort',"
    " gradeLevel:'na', gradeBy:'Tác giả', decision:'apply', pmid:'12345678'}\n  ]") + _CUOI

# Như trên nhưng decision='consider' ⇒ strict chỉ còn lỗi «THIẾU DATA.standards» (chỉ cảnh báo).
DASH_CHI_THIEU_STANDARDS = DASH_APPLY_NA.replace("decision:'apply'", "decision:'consider'")


class _Nen(unittest.TestCase):
    """Trỏ VERIFY/DOCX/BAN_DOC vào tệp CÓ THẬT của checkout git (EBM-Dashboards/ chỉ có qua
    OneDrive), và cung cấp bộ chạy main() với run() giả/lai."""

    def setUp(self):
        self.assertTrue(VERIFY_NGUON.exists(), "thiếu bản vendor verify_dashboard.py để test")
        self._cu = {k: getattr(XGCN, k) for k in
                    ("VERIFY", "DOCX", "BAN_DOC", "DASH_TOOLS", "run",
                     "xuat_ban_word_html", "ghi_sidecar_hash_data")}
        XGCN.VERIFY = VERIFY_NGUON
        XGCN.DOCX = VERIFY_NGUON          # chỉ để qua kiểm .exists(); DOCX thật không bao giờ chạy
        XGCN.BAN_DOC = HERE / "build_ban_doc_chung_cu.py"
        XGCN.DASH_TOOLS = VERIFY_NGUON.parent
        XGCN.xuat_ban_word_html = lambda docx, dash: (Path(str(docx)).with_suffix(".html"), "")
        XGCN.ghi_sidecar_hash_data = lambda dash, word: None

    def tearDown(self):
        for k, v in self._cu.items():
            setattr(XGCN, k, v)

    def chay(self, noi_dung: str, co_online: bool, gia, verify_that: bool):
        """Chạy XGCN.main(). `gia(cmd)` trả (rc, out) cho công cụ con; nếu `verify_that`
        thì mọi lời gọi verify_dashboard.py đi qua run() GỐC (chạy thật, ngoại tuyến)."""
        goi = []

        def run_lai(cmd, cwd=None):
            cmd_s = [str(c) for c in cmd]
            goi.append(cmd_s)
            if verify_that and cmd_s[1].endswith("verify_dashboard.py"):
                return RUN_GOC(cmd, cwd=cwd)
            return gia(cmd_s)

        with tempfile.TemporaryDirectory() as td:
            dash = Path(td) / "WebDashboard_ThuNgoaiTuyen_20260926.html"
            dash.write_text(noi_dung, encoding="utf-8")
            XGCN.run = run_lai
            argv_cu = sys.argv
            buf, loi = io.StringIO(), io.StringIO()
            try:
                sys.argv = ["xuat_goi_cap_nhat.py", str(dash), "--json"] + (
                    ["--online"] if co_online else [])
                with redirect_stdout(buf), redirect_stderr(loi):
                    rc = XGCN.main()
            finally:
                sys.argv = argv_cu
                XGCN.run = self._cu["run"]
        out = buf.getvalue()
        return rc, out, goi, loi.getvalue()

    @staticmethod
    def json_cuoi(out: str) -> dict:
        i = out.rfind("\n{")
        return json.loads(out[i + 1:] if i >= 0 else out[out.index("{"):])

    @staticmethod
    def goi_verify(goi):
        return [c for c in goi if c[1].endswith("verify_dashboard.py")]


def _khong_duoc_goi(cmd):
    raise AssertionError("Không được gọi công cụ con nào sau khi cổng chặn: %r" % cmd)


class TestSongNgoaiTuyenChanXuat(_Nen):
    """★★ Ca SỐNG — verify_dashboard.py thật, KHÔNG --online."""

    def test_khoa_la_bh61_chan_xuat_ma_3(self):
        rc, out, goi, _ = self.chay(DASH_KHOA_LA, False, _khong_duoc_goi, verify_that=True)
        self.assertEqual(rc, 3, out)
        self.assertNotIn("② Bản đọc", out)
        self.assertIn("CHẶN XUẤT", out)
        self.assertIn("khoá LẠ", out)
        v = self.goi_verify(goi)
        self.assertEqual(len(v), 1, goi)
        self.assertNotIn("--online", v[0], "chế độ ngoại tuyến không được gửi --online")
        self.assertEqual(self.json_cuoi(out)["cong_liem_chinh"], "CHẶN BỞI CỔNG LIÊM CHÍNH")

    def test_apply_tren_na_chan_xuat_ma_3_qua_strict_ngoai_tuyen(self):
        rc, out, goi, _ = self.chay(DASH_APPLY_NA, False, _khong_duoc_goi, verify_that=True)
        self.assertEqual(rc, 3, out)
        self.assertNotIn("② Bản đọc", out)
        # Hợp đồng câu chữ: verify_dashboard THẬT phải còn in «decision='apply'».
        self.assertIn("decision='apply'", out)
        v = self.goi_verify(goi)
        self.assertEqual(len(v), 2, goi)
        self.assertNotIn("--strict-sources", v[0])
        self.assertIn("--strict-sources", v[1])
        self.assertFalse(any("--online" in c for c in v), v)
        kq = self.json_cuoi(out)
        self.assertEqual(kq["cong_liem_chinh"], "CHẶN BỞI CỔNG NGUỒN")
        self.assertEqual(kq["cong_nguon_nghiem"], "CHẶN")
        self.assertFalse(kq["verified_flag"])

    def test_chi_thieu_standards_van_chay_buoc_hai(self):
        """Đối chứng: gói cũ chỉ thiếu DATA.standards thì KHÔNG bị chặn oan."""
        def gia(cmd):
            if cmd[1].endswith("build_ban_doc_chung_cu.py"):
                return 1, "dừng có chủ ý — chỉ cần biết bước ② ĐÃ được gọi"
            raise AssertionError("Lệnh không mong đợi: %r" % cmd)

        rc, out, goi, _ = self.chay(DASH_CHI_THIEU_STANDARDS, False, gia, verify_that=True)
        self.assertEqual(rc, 2, out)  # dừng tại chính bước ② (giả hỏng) — KHÔNG phải 3
        self.assertIn("② Bản đọc", out)
        self.assertIn("thiếu `DATA.standards`", out)
        self.assertEqual(len(self.goi_verify(goi)), 2, goi)


def _gia_day_chuyen(rc_verify=0, rc_strict=0, strict_out="KẾT QUẢ: ✓ PASS"):
    """run() giả cho CẢ dây chuyền ②③④⑤⑥ chạy thông, không ghi đĩa."""
    def gia(cmd):
        ten = Path(cmd[1]).name
        if ten == "verify_dashboard.py":
            if "--strict-sources" in cmd:
                return rc_strict, strict_out
            return rc_verify, "KẾT QUẢ: ✓ PASS — 0 lỗi cứng"
        if ten == "build_ban_doc_chung_cu.py":
            return 0, "✓ Đã ghi /gia/ban-doc.html"
        if ten == "kiem_cheo_ngu_nghia.py" or ten == "kiem_quan_the_chieu.py":
            return 0, "Tổng: 0"
        if ten == "docx_sang_pdf_giu_mau.py":
            return 0, "✓ /gia/a.pdf"
        if ten == "xuat_trang_thai_cloud.py":
            return 0, "✓ mirror"
        # DOCX được nhận diện riêng ở TestDonViNgoaiTuyen._gia_co_docx (đường dẫn giả riêng).
        raise AssertionError("Lệnh không mong đợi: %r" % cmd)
    return gia


class TestDonViNgoaiTuyen(_Nen):
    """Đơn vị: run() giả — tách bạch từng nhánh của _chay_cong ở chế độ ngoại tuyến."""

    def setUp(self):
        super().setUp()
        # DOCX riêng biệt để phân biệt với VERIFY trong run() giả.
        self._docx_gia = HERE / "xuat_goi_cap_nhat.py"
        XGCN.DOCX = self._docx_gia

    def _gia_co_docx(self, gia_goc):
        def gia(cmd):
            if cmd[1] == str(self._docx_gia):
                return 0, "✓ Đã ghi /gia/a.docx — xong"
            return gia_goc(cmd)
        return gia

    def test_strict_gia_co_dong_apply_chan_ma_3(self):
        gia = _gia_day_chuyen(rc_strict=1, strict_out=(
            "  ✗ [IT-01] decision='apply' nhưng gradeLevel='low' — phải hạ xuống consider/notyet\n"
            "KẾT QUẢ: ✗ FAIL — 1 lỗi cứng"))
        rc, out, goi, _ = self.chay(DASH_APPLY_NA, False, self._gia_co_docx(gia), verify_that=False)
        self.assertEqual(rc, 3, out)
        self.assertNotIn("② Bản đọc", out)
        self.assertFalse(any(Path(c[1]).name == "build_ban_doc_chung_cu.py" for c in goi), goi)

    def test_ngoai_tuyen_pass_khong_verified_va_tieu_de_khong_noi_san_sang(self):
        rc, out, goi, _ = self.chay(DASH_CHI_THIEU_STANDARDS, False,
                                    self._gia_co_docx(_gia_day_chuyen()), verify_that=False)
        self.assertEqual(rc, 0, out)
        docx = [c for c in goi if c[1] == str(self._docx_gia)]
        self.assertEqual(len(docx), 1, goi)
        self.assertNotIn("--verified", docx[0], "ngoại tuyến KHÔNG bao giờ được gắn --verified")
        self.assertIn("5/5 — CHƯA xác minh nguồn sống", out)
        self.assertNotIn("đã sẵn sàng", out)
        kq = self.json_cuoi(out)
        self.assertEqual(kq["cong_liem_chinh"], XGCN.NHAN_CONG_NGOAI_TUYEN)
        self.assertFalse(kq["verified_flag"])
        # Hai lượt verify đều đã chạy (thường + strict), không lượt nào mang --online.
        v = self.goi_verify(goi)
        self.assertEqual(len(v), 2, goi)
        self.assertFalse(any("--online" in c for c in v), v)

    def test_doi_chung_online_pass_van_verified_va_san_sang(self):
        """Đối chứng: đường --online PASS không bị bản vá đụng tới."""
        rc, out, goi, _ = self.chay(DASH_CHI_THIEU_STANDARDS, True,
                                    self._gia_co_docx(_gia_day_chuyen()), verify_that=False)
        self.assertEqual(rc, 0, out)
        docx = [c for c in goi if c[1] == str(self._docx_gia)]
        self.assertIn("--verified", docx[0])
        self.assertIn("── Bộ năm đã sẵn sàng (5/5) ──", out)
        v = self.goi_verify(goi)
        self.assertTrue(all("--online" in c for c in v), v)
        self.assertEqual(self.json_cuoi(out)["cong_liem_chinh"], "PASS")

    def test_thieu_verify_ngoai_tuyen_ma_1(self):
        XGCN.VERIFY = HERE / "khong_ton_tai_verify_dashboard.py"
        rc, out, goi, loi = self.chay(DASH_CHI_THIEU_STANDARDS, False,
                                      self._gia_co_docx(_gia_day_chuyen()), verify_that=False)
        self.assertEqual(rc, 1, out)
        self.assertIn("Thiếu verify_dashboard.py", loi)
        self.assertEqual(self.json_cuoi(out)["cong_liem_chinh"], "THIẾU TOOL")
        self.assertNotIn("đã sẵn sàng", out)


class TestTieuDeBoNam(unittest.TestCase):
    """`tom_tat_bo_nam` chỉ nói «đã sẵn sàng» khi đủ 5/5 VÀ cổng PASS sống."""

    DU = {"dashboard": "a", "ban_doc": "b", "word": "c", "word_html": "d", "pdf": "e"}

    def test_pass_moi_noi_san_sang(self):
        self.assertEqual(XGCN.tom_tat_bo_nam(dict(self.DU, cong_liem_chinh="PASS")),
                         "── Bộ năm đã sẵn sàng (5/5) ──")

    def test_ngoai_tuyen_khong_noi_san_sang(self):
        t = XGCN.tom_tat_bo_nam(dict(self.DU, cong_liem_chinh=XGCN.NHAN_CONG_NGOAI_TUYEN))
        self.assertIn("5/5", t)
        self.assertIn("CHƯA xác minh nguồn sống", t)
        self.assertNotIn("sẵn sàng", t)

    def test_vang_khoa_cong_coi_la_chua_xac_minh(self):
        t = XGCN.tom_tat_bo_nam(dict(self.DU))
        self.assertIn("5/5", t)
        self.assertNotIn("sẵn sàng", t)

    def test_thieu_san_pham_van_noi_thieu(self):
        t = XGCN.tom_tat_bo_nam({"dashboard": "a", "ban_doc": "b", "word": "c",
                                 "cong_liem_chinh": "PASS"})
        self.assertIn("3/5", t)
        self.assertIn("THIẾU", t)
        self.assertNotIn("sẵn sàng", t)


if __name__ == "__main__":
    unittest.main()
