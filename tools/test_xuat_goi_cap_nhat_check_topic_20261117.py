#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chốt: dây chuyền `--online` PHẢI truyền `--check-topic` cho cổng liêm chính (17/11/2026).

LỖI THẬT. `verify_dashboard.py` có sẵn luật kiểm LẠC CHỦ ĐỀ (`check_topic_relevance.py`, gọi LLM) — lấp đúng lỗ hổng đã làm
dashboard Tim mạch lọt 8/20 mục thực chất về sản/nhi/hô hấp/thận, chỉ đọc tay mới thấy. Nhưng cờ để «opt-in» và
`xuat_goi_cap_nhat.py` KHÔNG BAO GIỜ truyền (đếm 17/11: 0 lần trong cả tệp) ⇒ với dây chuyền hằng ngày, công cụ đó coi như
không tồn tại (doctrine §6.4: «một công cụ KHÔNG ai gọi thì … nó không tồn tại — xếp vào loại tuỳ chọn là cách nó lặng lẽ
không bao giờ chạy»).

Theo nguyên tắc của bộ chốt chị em (`test_xuat_goi_cap_nhat_20260926_ngoai_tuyen.py`): ca đơn vị GIẢ `run()` và đếm lời gọi
công cụ con — KHÔNG grep mã nguồn (bình luận mang cùng chuỗi sẽ làm chốt xanh giả)."""
from __future__ import annotations

import importlib.util
import io
import os
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _nap_module(ten: str, duong_dan: Path):
    spec = importlib.util.spec_from_file_location(ten, duong_dan)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[ten] = mod
    spec.loader.exec_module(mod)
    return mod


class CongPhaiGoiKiemChuDe(unittest.TestCase):
    def setUp(self):
        self.m = _nap_module("_xgc_check_topic", HERE / "xuat_goi_cap_nhat.py")
        self.goi: list[list[str]] = []

        def run_gia(cmd, cwd=None, timeout=None):
            self.goi.append([str(c) for c in cmd])
            return 0, "KẾT QUẢ: ✓ PASS — 0 lỗi cứng."

        self.m.run = run_gia
        if not self.m.VERIFY.exists():
            self.skipTest("⚪ không có verify_dashboard.py ở cây này — KHÔNG phải «đạt»")

    def _chay(self, co_online: bool) -> list[str]:
        kq: dict = {}
        with redirect_stdout(io.StringIO()):
            self.m._chay_cong(sys.executable, Path("khong-can-ton-tai.html"), co_online, kq)
        self.assertTrue(self.goi, "phải có ít nhất một lời gọi cổng")
        return self.goi[0]

    def test_online_phai_truyen_check_topic(self):
        """★ Chốt chính: thiếu cờ này thì luật lạc chủ đề im lặng không bao giờ chạy."""
        cmd = self._chay(True)
        self.assertIn("--online", cmd)
        self.assertIn("--check-topic", cmd)

    def test_ngoai_tuyen_khong_goi_llm(self):
        """★ Ngoại tuyến KHÔNG được gọi LLM — kiểm chủ đề cần mạng; gọi ở đây là tốn tiền và chắc chắn lỗi."""
        cmd = self._chay(False)
        self.assertNotIn("--online", cmd)
        self.assertNotIn("--check-topic", cmd)

    def test_canh_bao_khong_lam_hong_ma_thoat(self):
        """Kiểm chủ đề CHỈ cảnh báo: cổng PASS thì không có mã chặn, dù có bật cờ hay không."""
        kq: dict = {}
        with redirect_stdout(io.StringIO()):
            ma_chan, verified, rc_loi = self.m._chay_cong(sys.executable, Path("x.html"), True, kq)
        self.assertIsNone(ma_chan)
        self.assertTrue(verified)
        self.assertEqual(rc_loi, 0)


class ThieuKhoaThiBoQuaEm(unittest.TestCase):
    """★ Không có khoá API thì phải BỎ QUA ÊM — tuyệt đối không chặn dây chuyền xuất gói của bác sĩ."""

    def test_thieu_khoa_tra_skipped_chu_khong_nem_loi(self):
        ctr_path = HERE.parent / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "check_topic_relevance.py"
        if not ctr_path.exists():
            self.skipTest("⚪ không có check_topic_relevance.py ở cây này")
        ctr = _nap_module("_ctr_kiem", ctr_path)
        cu = os.environ.pop("ANTHROPIC_API_KEY", None)
        try:
            # tầng trong: nêu lỗi RÕ TÊN BIẾN còn thiếu, không nuốt im
            with self.assertRaises(ctr.TopicCheckError) as ngu_canh:
                ctr.call_claude("xin chào")
            self.assertIn("ANTHROPIC_API_KEY", str(ngu_canh.exception))
            # tầng ngoài (cái dây chuyền thật gọi): phải trả 'skipped', KHÔNG ném ra ngoài
            import tempfile
            # Khối DATA của dashboard là object literal JS (khoá KHÔNG đặt trong nháy) — bản
            # JSON đúng cú pháp sẽ không khớp `_extract_meta_question` và cho ra 'error', không phải 'skipped'.
            html = """<html><script>const DATA = {
              meta: { question: 'Chủ đề thử' },
              items: [ { id: 'ITEM-1', title: 'Bài thử', action: 'Cân nhắc' } ],
              summary: { conclusion: 'x', doNow: [], dontDo: [], redFlags: [] }
            };</script></html>"""
            with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
                f.write(html)
                duong = f.name
            kq = ctr.check_dashboard_topic_relevance(duong)
            self.assertEqual(kq["status"], "skipped")
            self.assertIn("ANTHROPIC_API_KEY", kq["message"])
        finally:
            if cu is not None:
                os.environ["ANTHROPIC_API_KEY"] = cu

    def test_model_mac_dinh_khong_lac_hau(self):
        """Model mặc định phải thuộc thế hệ hiện hành — bản cũ trỏ `claude-sonnet-4-6`, chậm một thế hệ."""
        ctr_path = HERE.parent / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "check_topic_relevance.py"
        if not ctr_path.exists():
            self.skipTest("⚪ không có check_topic_relevance.py ở cây này")
        nguon = ctr_path.read_text(encoding="utf-8")
        self.assertNotIn("claude-sonnet-4-6", nguon)
        self.assertIn("claude-sonnet-5-5", nguon)


if __name__ == "__main__":
    unittest.main()
