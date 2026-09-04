#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy phát hiện #1 của Workflow đối kháng đa-agent vòng 3 (2026-09-04, CRITICAL) trong
`xuat_goi_cap_nhat.py` — cổng liêm chính bước ① chỉ CHẶN XUẤT đúng MỘT nhánh lỗi cứng
(`decision='apply'` trên chứng cứ yếu, phát hiện bởi `--strict-sources`). Mọi lỗi cứng KHÁC
từ lượt `--online` thường — kể cả đúng lỗi `DATA.summary có khoá LẠ` (BH61: `notDo` thay vì
`dontDo`, xoá mất cả panel "Không nên/giới hạn" trên MỌI sản phẩm phái sinh) hoặc một trích
dẫn ĐÃ BỊ RÚT (`kiem_nguon_da_rut`) — chỉ hạ câu chữ "đã xác minh" rồi vẫn chạy tiếp ②③④⑤,
kết thúc bằng dòng "── Bộ năm đã sẵn sàng ──" như không có gì xảy ra.

`verify_dashboard.py` TỰ phân biệt hai loại thất bại qua mã thoát: rc=1 = ≥1 lỗi cứng THẬT
(nội dung/an toàn/cấu trúc dữ liệu), rc=2 = TOÀN BỘ lỗi cứng là do MÁY/MẠNG (xem
`_canh_bao_loi_mang`/`report()` trong chính file đó). Bản vá dùng lại đúng ranh giới đó:
rc=1 ⇒ CHẶN XUẤT (return 3, không chạy bước ②); rc=2 ⇒ vẫn xuất như cũ (không phải kết luận
về nguồn).

Ghi chú MÔI TRƯỜNG (phiên cloud): `EBM-Dashboards/` là hạ tầng đồng bộ qua OneDrive, KHÔNG
qua git (đúng doctrine CLAUDE.md) — trên checkout git thuần này, `xuat_goi_cap_nhat.DASH_TOOLS`
không tồn tại trên đĩa, nên `VERIFY`/`DOCX` (trỏ vào đó) không có file thật. Bản sao NGUỒN
tương đương của `verify_dashboard.py` sống ở `sync/skills/cap-nhat-chung-cu-y-khoa/tools/` (có
track Git) — test patch thẳng hằng số module `XGCN.VERIFY`/`XGCN.DOCX` trỏ vào đó/một file có
thật để cô lập được logic điều khiển của CHÍNH `xuat_goi_cap_nhat.py`, tách khỏi việc thiếu hạ
tầng OneDrive của môi trường chạy test — không liên quan tới lỗi đang vá.

Nguyên tắc viết test: (a) một ca SỐNG dùng chính verify_dashboard.py thật (bản nguồn track Git)
với dashboard tối giản gài đúng lỗi BH61 (`notDo`) để chứng minh kịch bản thất bại nguyên văn
của phát hiện; (b) các ca đơn vị monkeypatch hàm `run()` để tách bạch rc=0/1/2 mà không cần
mạng, đếm số lần các tool con được gọi để chứng minh bước ②③④⑤ có/không chạy — không grep
chuỗi trong mã nguồn.
"""
from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
VERIFY_NGUON = HERE.parent / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "verify_dashboard.py"


def _nap_module(ten: str, duong_dan: Path):
    spec = importlib.util.spec_from_file_location(ten, duong_dan)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[ten] = mod
    spec.loader.exec_module(mod)
    return mod


XGCN = _nap_module("xuat_goi_cap_nhat_test_target", HERE / "xuat_goi_cap_nhat.py")


DASHBOARD_KHOA_LA = """<!doctype html><html><body>
<!-- Cần bác sĩ kiểm chứng -->
<script>
const DATA = {
  meta:{kind:'cong-cu', updated:'2026-09-04', question:'Test khoá lạ'},
  summary:{conclusion:'Kết luận thử.', doNow:['Việc nên làm'], notDo:['KHÔNG ngừng thuốc đột ngột'], redFlags:[]},
  items:[]
};
/* ▲▲▲  HẾT KHỐI DATA  ▲▲▲ */
</script>
</body></html>
"""


class _PatchDuongDanTool(unittest.TestCase):
    """Base: patch XGCN.VERIFY/BAN_DOC/DOCX trỏ vào file CÓ THẬT trên đĩa của checkout
    git này, để cô lập logic điều khiển khỏi việc thiếu thư mục EBM-Dashboards/ (OneDrive)."""

    def setUp(self):
        self.assertTrue(VERIFY_NGUON.exists(), "thiếu bản nguồn verify_dashboard.py để test")
        self._old_verify = XGCN.VERIFY
        self._old_docx = XGCN.DOCX
        self._old_ban_doc = XGCN.BAN_DOC
        self._old_dash_tools = XGCN.DASH_TOOLS
        XGCN.VERIFY = VERIFY_NGUON
        # DOCX không có bản track-Git nào trong checkout này (chỉ tồn tại qua OneDrive) —
        # trỏ tạm vào một file CÓ THẬT chỉ để qua được kiểm .exists() ở đầu main(); các
        # test dưới đây không bao giờ thật sự CHẠY DOCX (rc=1 chặn trước khi tới đó, và
        # rc=2/rc=0 dừng sớm ở bước ② qua run() đã bị monkeypatch).
        XGCN.DOCX = VERIFY_NGUON
        XGCN.BAN_DOC = HERE / "build_ban_doc_chung_cu.py"
        # `run(..., cwd=DASH_TOOLS.parent)` cần một thư mục CÓ THẬT — DASH_TOOLS gốc
        # (EBM-Dashboards/tools, chỉ tồn tại qua OneDrive) không có trên checkout git này.
        XGCN.DASH_TOOLS = VERIFY_NGUON.parent

    def tearDown(self):
        XGCN.VERIFY = self._old_verify
        XGCN.DOCX = self._old_docx
        XGCN.BAN_DOC = self._old_ban_doc
        XGCN.DASH_TOOLS = self._old_dash_tools


class TestSongDongKhoaLaBH61ChanXuat(_PatchDuongDanTool):
    """★★ Ca chính, chạy SỐNG: dashboard gài đúng lỗi BH61 (notDo thay vì dontDo) —
    verify_dashboard.py --online (không strict-sources) phải trả rc=1, và
    xuat_goi_cap_nhat.py phải CHẶN XUẤT (mã thoát 3), KHÔNG được in '② Bản đọc…'."""

    _TEN_DASH = "WebDashboard_TestKhoaLa_20260904"

    def tearDown(self):
        super().tearDown()
        # An toàn cho lần chạy test TRÊN CODE ĐÃ HỎNG (vd hồi quy tương lai): nếu bước ②
        # thật sự chạy, build_ban_doc_chung_cu.py (script THẬT, không mock) ghi ra
        # ROOT/EBM-Dashboards/derivatives/ theo đường mặc định của CHÍNH nó, KHÔNG theo
        # thư mục tạm của test — dọn sạch để không để lại rác trong repo thật.
        # CỐ Ý bảo thủ: chỉ xoá ĐÚNG file mang tên dashboard giả của chính test này,
        # KHÔNG bao giờ đụng tới thư mục `EBM-Dashboards/` — trên máy thật đó là dữ
        # liệu bác sĩ đồng bộ qua OneDrive, không phải rác của test.
        deriv = HERE.parent / "EBM-Dashboards" / "derivatives"
        if deriv.exists():
            for p in deriv.glob(f"{self._TEN_DASH}*"):
                p.unlink(missing_ok=True)
            try:
                deriv.rmdir()  # chỉ thành công khi RỖNG — không ép xoá nếu còn gì khác
            except OSError:
                pass

    def test_chan_xuat_khi_khoa_la_va_khong_chay_buoc_hai(self):
        with tempfile.TemporaryDirectory() as td:
            dash = Path(td) / f"{self._TEN_DASH}.html"
            dash.write_text(DASHBOARD_KHOA_LA, encoding="utf-8")

            # Xác nhận trước bằng chính verify_dashboard.py thật (KHÔNG qua xuat_goi_cap_nhat):
            # fixture này thật sự khiến rc=1 dưới --online thường (không strict-sources) —
            # nếu không, phần còn lại của test vô nghĩa.
            import subprocess
            r = subprocess.run(
                [sys.executable, str(VERIFY_NGUON), str(dash), "--online"],
                capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
            self.assertIn("khoá LẠ", r.stdout)

            old_argv = sys.argv
            buf = io.StringIO()
            try:
                sys.argv = ["xuat_goi_cap_nhat.py", str(dash), "--online", "--json"]
                with redirect_stdout(buf):
                    rc = XGCN.main()
            finally:
                sys.argv = old_argv
            out = buf.getvalue()

            self.assertEqual(rc, 3, out)
            self.assertNotIn("② Bản đọc", out)
            self.assertIn("CHẶN XUẤT", out)
            # Không được tạo ra bất kỳ sản phẩm phái sinh nào của gói lỗi này.
            self.assertFalse(list(Path(td).glob("*ban-doc*")))
            self.assertFalse(list(Path(td).glob("*.docx")))


class TestDonViPhanBietRc1Rc2(_PatchDuongDanTool):
    """Đơn vị: monkeypatch run() để tách bạch rc=1 (chặn) khỏi rc=2 (mạng, vẫn xuất)
    mà không cần mạng thật lẫn dashboard hợp lệ đầy đủ."""

    def _chay_main_voi_run_gia(self, fake_run):
        goi = []

        def wrap(cmd, cwd=None):
            cmd_s = [str(c) for c in cmd]
            goi.append(cmd_s)
            return fake_run(cmd_s)

        with tempfile.TemporaryDirectory() as td:
            dash = Path(td) / "WebDashboard_Gia_20260904.html"
            dash.write_text(DASHBOARD_KHOA_LA, encoding="utf-8")
            old_run = XGCN.run
            old_argv = sys.argv
            buf = io.StringIO()
            try:
                XGCN.run = wrap
                sys.argv = ["xuat_goi_cap_nhat.py", str(dash), "--online"]
                with redirect_stdout(buf):
                    rc = XGCN.main()
            finally:
                XGCN.run = old_run
                sys.argv = old_argv
        return rc, buf.getvalue(), goi

    def test_rc1_that_chan_xuat_ngay_khong_goi_buoc_hai(self):
        """★★ rc=1 (lỗi cứng THẬT, không phải mạng) từ lượt --online thường phải CHẶN
        XUẤT ngay — build_ban_doc_chung_cu.py (bước ②) KHÔNG được gọi lần nào."""
        def fake_run(cmd):
            if "verify_dashboard.py" in cmd[1] and "--strict-sources" not in cmd:
                return 1, ("  ✗ DATA.summary có khoá LẠ 'notDo'...\n"
                           "KẾT QUẢ: ✗ FAIL — 1 lỗi cứng, 0 cảnh báo.")
            raise AssertionError("Không được gọi thêm run() nào sau khi rc=1 chặn xuất: %r" % cmd)

        rc, out, goi = self._chay_main_voi_run_gia(fake_run)
        self.assertEqual(rc, 3, out)
        self.assertEqual(len(goi), 1, goi)
        self.assertIn("CHẶN XUẤT", out)
        self.assertNotIn("② Bản đọc", out)

    def test_rc2_thuan_mang_van_chay_tiep_buoc_hai(self):
        """Đối chứng bắt buộc: rc=2 (TOÀN BỘ lỗi cứng là do mạng/DNS) KHÔNG được chặn
        xuất — bước ② vẫn phải được GỌI (dù bản thân nó thất bại trong test này, việc
        được GỌI mới là điều cần chứng minh: hành vi cũ 'vẫn xuất khi mạng lỗi' còn nguyên)."""
        def fake_run(cmd):
            if "verify_dashboard.py" in cmd[1] and "--strict-sources" in cmd:
                return 2, ("  ✗ [ITEM-01] PMID 1 CHƯA XÁC MINH ĐƯỢC (lỗi mạng: timed out)\n"
                           "KẾT QUẢ: ✗ FAIL — 1 lỗi cứng, 0 cảnh báo.")
            if "verify_dashboard.py" in cmd[1]:
                return 2, ("  ✗ [ITEM-01] PMID 1 CHƯA XÁC MINH ĐƯỢC (lỗi mạng: timed out)\n"
                           "KẾT QUẢ: ✗ FAIL — 1 lỗi cứng, 0 cảnh báo.")
            if "build_ban_doc_chung_cu.py" in cmd[1]:
                return 1, "dừng ở đây có chủ ý — chỉ cần biết bước ② ĐÃ được gọi"
            raise AssertionError("Lệnh không mong đợi trong test này: %r" % cmd)

        rc, out, goi = self._chay_main_voi_run_gia(fake_run)
        self.assertEqual(rc, 2, out)  # return 2 tại chính bước ② khi nó thất bại — KHÔNG phải 3
        self.assertGreaterEqual(len(goi), 2, goi)
        self.assertTrue(any("build_ban_doc_chung_cu.py" in c[1] for c in goi), goi)
        self.assertIn("CHƯA xác minh được do MÁY/MẠNG", out)
        self.assertIn("② Bản đọc", out)

    def test_rc0_pass_van_chay_tiep_va_bat_co_verified(self):
        """Đối chứng: rc=0 (PASS thật) phải bật verified=True và vẫn chạy tiếp — hành
        vi đường PASS không bị đụng tới bởi bản vá."""
        def fake_run(cmd):
            if "verify_dashboard.py" in cmd[1] and "--strict-sources" not in cmd:
                return 0, "KẾT QUẢ: ✓ PASS — 0 lỗi cứng, 0 cảnh báo."
            if "verify_dashboard.py" in cmd[1] and "--strict-sources" in cmd:
                return 0, "KẾT QUẢ: ✓ PASS — 0 lỗi cứng, 0 cảnh báo."
            if "build_ban_doc_chung_cu.py" in cmd[1]:
                return 1, "dừng ở đây có chủ ý — chỉ cần biết bước ② ĐÃ được gọi"
            raise AssertionError("Lệnh không mong đợi trong test này: %r" % cmd)

        rc, out, goi = self._chay_main_voi_run_gia(fake_run)
        self.assertEqual(rc, 2, out)
        self.assertTrue(any("build_ban_doc_chung_cu.py" in c[1] for c in goi), goi)
        self.assertIn("② Bản đọc", out)


if __name__ == "__main__":
    unittest.main()
