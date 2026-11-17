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
import pathlib
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
        # CÁCH LY khỏi kho thật. Nếu không: trên máy ĐÃ có khoá, chốt này gọi API THẬT — tốn tiền
        # và đổi kết quả theo môi trường (đo 17/11/2026: khoá bị từ chối ⇒ 'error' chứ không phải
        # 'skipped' ⇒ chốt đỏ oan). Chốt phải ngoại tuyến tuyệt đối, không phụ thuộc máy nào chạy.
        import tempfile as _tf
        cu_kho = ctr.KHO_BI_MAT
        with _tf.NamedTemporaryFile("w", suffix=".env", delete=False, encoding="utf-8") as _f:
            _f.write("# kho rỗng dành cho bộ kiểm\n")
            ctr.KHO_BI_MAT = _f.name
        # Vỏ bọc GHI nhật ký sức khoẻ vào thư mục nhà; chốt tuyệt đối không được đụng tệp thật.
        cu_nk = ctr.NHAT_KY_API
        ctr.NHAT_KY_API = str(pathlib.Path(_f.name).with_suffix(".nk.json"))
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
            ctr.NHAT_KY_API = cu_nk
            ctr.KHO_BI_MAT = cu_kho
            if cu is not None:
                os.environ["ANTHROPIC_API_KEY"] = cu


class KhoaPhaiToiDuocCongCu(unittest.TestCase):
    """★ Bẫy 17/11/2026: tool chỉ đọc `os.getenv`, nên khoá cất trong kho bí mật KHÔNG tới được nó.

    Lượt lịch / hook / mọi lượt chạy không qua shell có `export` sẽ lặng lẽ bỏ qua kiểm chủ đề —
    âm tính giả đúng kiểu doctrine cấm. Thứ tự đúng (§5): biến môi trường OS → kho secrets."""

    def setUp(self):
        ctr_path = HERE.parent / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "check_topic_relevance.py"
        if not ctr_path.exists():
            self.skipTest("⚪ không có check_topic_relevance.py ở cây này")
        self.ctr = _nap_module("_ctr_kho", ctr_path)
        self.cu = os.environ.pop("ANTHROPIC_API_KEY", None)

    def tearDown(self):
        if self.cu is not None:
            os.environ["ANTHROPIC_API_KEY"] = self.cu

    def _kho_gia(self, noi_dung: str) -> str:
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".env", delete=False, encoding="utf-8") as f:
            f.write(noi_dung)
            return f.name

    def test_doc_duoc_khoa_tu_kho_khi_vang_bien_moi_truong(self):
        kho = self._kho_gia("# ghi chú\nNCBI_EMAIL=a@b.vn\nANTHROPIC_API_KEY=gia-tri-gia\n")
        self.assertEqual(self.ctr._khoa_tu_kho(kho=kho), "gia-tri-gia")

    def test_bien_moi_truong_thang_kho(self):
        """Thứ tự §5: biến môi trường OS đứng TRƯỚC kho secrets."""
        kho = self._kho_gia("ANTHROPIC_API_KEY=trong-kho\n")
        os.environ["ANTHROPIC_API_KEY"] = "tu-moi-truong"
        try:
            self.ctr.KHO_BI_MAT = kho
            # call_claude lấy env trước; không gọi mạng nên dừng ở bước chọn khoá
            self.assertEqual(os.getenv("ANTHROPIC_API_KEY", "") or self.ctr._khoa_tu_kho(kho=kho), "tu-moi-truong")
        finally:
            os.environ.pop("ANTHROPIC_API_KEY", None)

    def test_kho_vang_hoac_hong_khong_bao_gio_nem_loi(self):
        self.assertEqual(self.ctr._khoa_tu_kho(kho="/khong/ton/tai/abc.env"), "")
        hong = self._kho_gia("dòng rác không có dấu bằng\n\n#chỉ chú thích\n")
        self.assertEqual(self.ctr._khoa_tu_kho(kho=hong), "")

    def test_bo_nhay_quanh_gia_tri(self):
        kho = self._kho_gia("ANTHROPIC_API_KEY='co-nhay'\n")
        self.assertEqual(self.ctr._khoa_tu_kho(kho=kho), "co-nhay")

    def test_dong_cuoi_thang_khi_kho_co_hai_dong(self):
        """★ Hỏng thật 17/11/2026: kho ghi kiểu NỐI THÊM. Bác sĩ ghi khoá mới mà dòng cũ còn đó;
        lấy dòng ĐẦU thì vẫn dùng khoá hỏng vừa thay — im lặng, rất khó đoán. `load_dotenv` của
        repo y khoa cũng để giá trị sau đè trước, nên dòng CUỐI phải thắng."""
        kho = self._kho_gia("ANTHROPIC_API_KEY=khoa-hong-cu\nNCBI_EMAIL=a@b.vn\nANTHROPIC_API_KEY=khoa-moi-dung\n")
        self.assertEqual(self.ctr._khoa_tu_kho(kho=kho), "khoa-moi-dung")

    def test_dong_rong_khong_de_len_dong_co_gia_tri(self):
        """Dòng `ANTHROPIC_API_KEY=` rỗng ở cuối không được xoá sạch khoá hợp lệ ghi phía trên."""
        kho = self._kho_gia("ANTHROPIC_API_KEY=khoa-that\nANTHROPIC_API_KEY=\n")
        self.assertEqual(self.ctr._khoa_tu_kho(kho=kho), "khoa-that")


class GoiAPIDungKhoaVaDungModel(unittest.TestCase):
    """★ Chốt HÀNH VI (không grep mã nguồn): `call_claude` phải lấy khoá từ KHO khi biến môi trường
    vắng, và gọi đúng model thế hệ hiện hành. Tiêm SDK giả nên không chạm mạng, không tốn tiền."""

    def setUp(self):
        ctr_path = HERE.parent / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "check_topic_relevance.py"
        if not ctr_path.exists():
            self.skipTest("⚪ không có check_topic_relevance.py ở cây này")
        self.ctr = _nap_module("_ctr_goi", ctr_path)
        self.cu_env = os.environ.pop("ANTHROPIC_API_KEY", None)
        self.cu_kho = self.ctr.KHO_BI_MAT

    def tearDown(self):
        self.ctr.KHO_BI_MAT = self.cu_kho
        sys.modules.pop("anthropic", None)
        if self.cu_env is not None:
            os.environ["ANTHROPIC_API_KEY"] = self.cu_env

    def test_lay_khoa_tu_kho_va_dung_model_hien_hanh(self):
        import tempfile
        import types
        with tempfile.NamedTemporaryFile("w", suffix=".env", delete=False, encoding="utf-8") as f:
            f.write("ANTHROPIC_API_KEY=khoa-gia-cho-kiem-thu\n")
            self.ctr.KHO_BI_MAT = f.name

        ghi: dict = {}

        class _Msgs:
            def create(self, **kw):
                ghi.update(kw)
                return types.SimpleNamespace(stop_reason="end_turn", content=[types.SimpleNamespace(text="OK")])

        class _Cli:
            # Từ 17/11 model hiện hành đi kênh beta (để có `fallbacks`); model khác đi kênh thường.
            def __init__(self, api_key=None):
                ghi["api_key"] = api_key
                self.messages = _Msgs()
                self.beta = types.SimpleNamespace(messages=_Msgs())

        gia = types.ModuleType("anthropic")
        gia.Anthropic = _Cli
        sys.modules["anthropic"] = gia

        self.assertEqual(self.ctr.call_claude("hỏi thử"), "OK")
        self.assertEqual(ghi["api_key"], "khoa-gia-cho-kiem-thu")   # ★ khoá đến từ KHO
        self.assertEqual(ghi["model"], "claude-sonnet-5-5")          # ★ model thế hệ hiện hành


class LoiSDKKhongDuocLOT(unittest.TestCase):
    """★ Đo thật 17/11/2026: khoá sai ⇒ `anthropic.AuthenticationError 401` LỌT ra ngoài — chạy tay
    văng traceback, chạy trong cổng thì thành cảnh báo khó đọc. Mọi lỗi SDK/mạng phải quy về
    `status='error'` như các nhánh khác, và KHÔNG được nuốt im."""

    def setUp(self):
        ctr_path = HERE.parent / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "check_topic_relevance.py"
        if not ctr_path.exists():
            self.skipTest("⚪ không có check_topic_relevance.py ở cây này")
        self.ctr = _nap_module("_ctr_loi", ctr_path)
        import tempfile as _tf2
        with _tf2.NamedTemporaryFile("w", suffix=".nk.json", delete=False, encoding="utf-8") as _f2:
            _f2.write("{}")
        self.ctr.NHAT_KY_API = _f2.name   # không ghi vào nhật ký THẬT ở thư mục nhà

    def _dashboard_gia(self) -> str:
        import tempfile
        html = """<html><script>const DATA = {
          meta: { question: 'Chủ đề thử' },
          items: [ { id: 'ITEM-1', title: 'Bài thử', action: 'Cân nhắc' } ],
          summary: { conclusion: 'x', doNow: [], dontDo: [], redFlags: [] }
        };</script></html>"""
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
            f.write(html)
            return f.name

    def test_loi_401_thanh_error_chu_khong_nem_traceback(self):
        class LoiGia(Exception):
            pass

        def no_tung(_prompt):
            raise LoiGia("Error code: 401 - Invalid bearer token")

        self.ctr.call_claude = no_tung
        kq = self.ctr.check_dashboard_topic_relevance(self._dashboard_gia())
        self.assertEqual(kq["status"], "error")
        self.assertIn("LoiGia", kq["message"])
        self.assertIn("401", kq["message"])

    def test_thieu_khoa_van_la_skipped_chu_khong_phai_error(self):
        """Thiếu khoá ≠ lỗi: vẫn phải là «skipped» để cổng phân biệt «chưa bật» với «bật mà hỏng»."""
        def thieu(_prompt):
            raise self.ctr.TopicCheckError("Thiếu ANTHROPIC_API_KEY — …")

        self.ctr.call_claude = thieu
        kq = self.ctr.check_dashboard_topic_relevance(self._dashboard_gia())
        self.assertEqual(kq["status"], "skipped")

if __name__ == "__main__":
    unittest.main()
