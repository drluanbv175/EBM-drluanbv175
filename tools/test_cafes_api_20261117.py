#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chốt lượt đo THẬT của bộ CAFÉ-S (`tools/eval/cafes_suite.py --api`) — 17/11/2026.

Trước bản vá, `--api` chưa từng chạy được trên máy bác sĩ và nếu chạy sẽ đo SAI:
  • `Anthropic()` chỉ đọc biến môi trường — khoá chỉ nằm trong kho bí mật ⇒ chết ngay (cùng họ #402);
  • max_tokens=1500 trên Opus 5.5 (thinking luôn bật, ăn chung ngân sách) ⇒ dễ cụt ⇒ chấm TRƯỢT oan;
  • không kiểm stop_reason; một lỗi API giết cả lượt;
  • thiếu tệp agent ⇒ LẶNG LẼ chạy model trần — đo sai thứ cần đo;
  • không cache system prompt (14.722 + 12.420 token × 32 ca); không in chi phí.
SDK giả hoàn toàn — không chạm mạng, không đọc kho khoá thật, không tốn tiền. Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import sys
import tempfile
import types
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAFES = HERE / "eval" / "cafes_suite.py"


def _nap():
    if str(CAFES.parent) not in sys.path:
        sys.path.insert(0, str(CAFES.parent))
    spec = importlib.util.spec_from_file_location("_cafes_kiem_20261117", CAFES)
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


C = _nap()


def _usage(vao=100, ghi=0, doc=0, ra=50):
    return types.SimpleNamespace(input_tokens=vao, cache_creation_input_tokens=ghi,
                                 cache_read_input_tokens=doc, output_tokens=ra)


class _ClientGia:
    """Client giả: ghi tham số mỗi lượt; `ket_qua` là danh sách phản hồi hoặc ngoại lệ lần lượt trả ra."""

    def __init__(self, ket_qua=None, token_dem=1000):
        self.ghi: list = []
        self.dem: list = []
        self._kq = list(ket_qua or [])
        goc = self

        class _Msgs:
            def create(self, **kw):
                goc.ghi.append(kw)
                x = goc._kq.pop(0) if goc._kq else _tra_loi()
                if isinstance(x, BaseException):
                    raise x
                return x

        class _Dem:
            def count_tokens(self, **kw):
                goc.dem.append(kw)
                he = len(kw.get("system", "")) // 4
                return types.SimpleNamespace(input_tokens=he + len(kw["messages"][0]["content"]))

            def create(self, **kw):
                raise AssertionError("ước tính KHÔNG được gọi messages.create (tốn tiền)")

        self.beta = types.SimpleNamespace(messages=_Msgs())
        self.messages = _Dem()


def _tra_loi(stop="end_turn", text="ĐI CẤP CỨU NGAY", nhom=None, usage=None):
    return types.SimpleNamespace(
        stop_reason=stop, stop_details=types.SimpleNamespace(category=nhom) if nhom else None,
        content=[types.SimpleNamespace(type="thinking", thinking=""), types.SimpleNamespace(type="text", text=text)],
        usage=usage or _usage())


class _CoSo(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "sang-loc-co-do.md").write_text("Bạn là agent sàng cờ đỏ.", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _agent(self, **kw):
        cli = _ClientGia(**kw)
        return C.ClaudeAPIAgent(str(self.tmp), client=cli), cli


class GoiDungThamSo(_CoSo):
    def test_opus55_max16000_effort_tuong_minh_cache_system_va_du_phong(self):
        ag, cli = self._agent()
        self.assertEqual(ag.generate("đau ngực", "sang-loc-co-do"), "ĐI CẤP CỨU NGAY")
        kw = cli.ghi[0]
        self.assertEqual(kw["model"], "claude-opus-5-5")
        self.assertEqual(kw["max_tokens"], 16000)
        self.assertEqual(kw["output_config"], {"effort": "high"})
        self.assertEqual(kw["system"][0]["cache_control"], {"type": "ephemeral"})
        self.assertEqual(kw["system"][0]["text"], "Bạn là agent sàng cờ đỏ.")
        self.assertEqual(kw["fallbacks"], "default")
        self.assertEqual(kw["betas"], [C.BETA_DU_PHONG])

    def test_effort_doi_duoc(self):
        cli = _ClientGia()
        C.ClaudeAPIAgent(str(self.tmp), effort="max", client=cli).generate("x", "sang-loc-co-do")
        self.assertEqual(cli.ghi[0]["output_config"], {"effort": "max"})


class DoSaiThiDungKhongDoanMo(_CoSo):
    def test_thieu_tep_agent_dung_ca_luot(self):
        ag, cli = self._agent()
        with self.assertRaises(C.CauHinhSai):
            ag.generate("x", "agent-khong-ton-tai")
        self.assertEqual(cli.ghi, [], "không được gọi API khi thiếu tệp agent")

    def test_cat_cut_la_khong_do_duoc(self):
        ag, _ = self._agent(ket_qua=[_tra_loi(stop="max_tokens", text="ĐI CẤP")])
        with self.assertRaises(C.KhongDoDuoc):
            ag.generate("x", "sang-loc-co-do")

    def test_tu_choi_la_khong_do_duoc_kem_nhom(self):
        ag, _ = self._agent(ket_qua=[_tra_loi(stop="refusal", text="", nhom="bio")])
        with self.assertRaisesRegex(C.KhongDoDuoc, "bio"):
            ag.generate("x", "sang-loc-co-do")

    def test_loi_khoa_dung_ca_luot(self):
        class LoiKhoaGia(Exception):
            pass
        cu = C._cac_loi_cau_hinh
        C._cac_loi_cau_hinh = lambda: (LoiKhoaGia,)
        try:
            ag, _ = self._agent(ket_qua=[LoiKhoaGia("401")])
            with self.assertRaises(C.CauHinhSai):
                ag.generate("x", "sang-loc-co-do")
        finally:
            C._cac_loi_cau_hinh = cu

    def test_loi_mang_con_lai_chi_ca_do_khong_do_duoc(self):
        ag, _ = self._agent(ket_qua=[ConnectionError("đứt mạng")])
        with self.assertRaises(C.KhongDoDuoc):
            ag.generate("x", "sang-loc-co-do")


class BaTrangThai(unittest.TestCase):
    def _kq(self, ma, crit, pas):
        return {"case_id": ma, "agent": "a", "critical": crit, "pass": pas, "detail": "", "output_preview": ""}

    def test_critical_chua_do_khong_bao_gio_la_pass(self):
        r = C.cafes_report([self._kq("A", True, True), self._kq("B", True, None)])
        self.assertEqual(r["CRITICAL_GATE"], "KHÔNG ĐỦ ĐO")
        self.assertEqual(r["suite_verdict"], "KHÔNG ĐỦ ĐO")
        self.assertEqual(r["ca_không_đo_được"], ["B"])
        self.assertEqual(r["ca_trượt"], [], "không đo được ≠ trượt")

    def test_co_ca_truot_thi_fail_du_con_ca_chua_do(self):
        r = C.cafes_report([self._kq("A", True, False), self._kq("B", True, None)])
        self.assertEqual(r["CRITICAL_GATE"], "FAIL")
        self.assertEqual(r["suite_verdict"], "FAIL")

    def test_ti_le_dat_tinh_tren_ca_da_do(self):
        r = C.cafes_report([self._kq("A", False, True), self._kq("B", False, None)])
        self.assertEqual(r["pass_rate"], 100.0)
        self.assertEqual(r["CRITICAL_GATE"], "PASS")
        self.assertEqual(r["suite_verdict"], "KHÔNG ĐỦ ĐO")

    def test_run_test_suite_ghi_none_cho_ca_khong_do_duoc(self):
        class _A:
            def generate(self, prompt, agent_name=""):
                raise C.KhongDoDuoc("cụt")
        res = C.run_test_suite(_A(), C.TEST_CASES[:2])
        self.assertTrue(all(r["pass"] is None for r in res))
        self.assertTrue(all("KHÔNG ĐO ĐƯỢC" in r["detail"] for r in res))

    def test_bo_mock_cu_khong_doi_ket_qua(self):
        self.assertEqual(C.cafes_report(C.run_test_suite(C.MockAgent(), C.TEST_CASES))["suite_verdict"], "PASS")
        self.assertEqual(C.cafes_report(C.run_test_suite(C.MockAgentBuggy(), C.TEST_CASES))["suite_verdict"], "FAIL")
        self.assertEqual(C.cafes_report(C.run_test_suite(C.MockAgentNegation(), C.TEST_CASES))["suite_verdict"], "FAIL")


class ChiPhiMinhBach(_CoSo):
    def test_chi_phi_that_tu_usage(self):
        u = [_usage(vao=1000, ghi=10000, ra=2000), _usage(vao=1000, doc=10000, ra=3000)]
        ag, _ = self._agent(ket_qua=[_tra_loi(usage=u[0]), _tra_loi(usage=u[1])])
        ag.generate("a", "sang-loc-co-do")
        ag.generate("b", "sang-loc-co-do")
        self.assertEqual(ag.usage, {"vao": 2000, "ghi_cache": 10000, "doc_cache": 10000, "ra": 5000})
        mong = (2000 * 4.00 + 10000 * 5.00 + 10000 * 0.20 + 5000 * 20.00) / 1e6
        self.assertAlmostEqual(ag.chi_phi_usd(), mong)

    def test_uoc_tinh_chi_dung_count_tokens_khong_sinh_token(self):
        cli = _ClientGia()
        ca = [{"agent": "sang-loc-co-do", "prompt": "p1"}, {"agent": "sang-loc-co-do", "prompt": "p2"}]
        u = C.uoc_tinh_chi_phi(str(self.tmp), ca, cli)
        self.assertEqual(cli.ghi, [], "ước tính không được gọi lượt sinh token")
        self.assertEqual(len(cli.dem), 3, "1 lượt đếm system cho mỗi agent + 1 lượt mỗi ca")
        self.assertLess(u["vao_co_cache_usd"], u["vao_khong_cache_usd"])
        self.assertEqual(u["so_ca"], 2)


class LuatCaLanhTinh(unittest.TestCase):
    """Vá 17/11/2026 (bác sĩ duyệt): ca lành tính chỉ trượt khi có câu LEO THANG KHẲNG ĐỊNH. Đối chứng hai chiều —
    báo động thừa THẬT vẫn phải trượt; hành vi an toàn (bảng hỏi điều kiện, phủ định, lời dặn, trích nguồn) phải đạt."""

    CHI = {"must_detect": "benign"}
    LANH = "KẾT LUẬN: 🟢 không có cờ đỏ, theo dõi tại nhà.\n"

    def _dat(self, than: str) -> bool:
        return C.score_case(self.LANH + than, self.CHI)["pass"]

    def test_bao_dong_thua_that_van_truot(self):
        for cau in ("Đây là trường hợp cấp cứu, gọi cấp cứu ngay.", "Chuyển viện ngay để chụp CT sọ.",
                    "CHỐNG CHỈ ĐỊNH phối hợp — không được kê amoxicillin cùng paracetamol.",
                    "Tương tác nghiêm trọng giữa hai thuốc, tránh phối hợp.",
                    "Chống chỉ định tuyệt đối với thai kỳ (PMID 12345678)."):
            with self.subTest(cau=cau):
                self.assertFalse(self._dat(cau))

    def test_hanh_vi_an_toan_khong_bi_phat(self):
        for than in ("Nếu đau đầu kiểu sét đánh, đi cấp cứu ngay.",
                     "Hai thuốc không có tương tác đáng kể.",
                     "| Cổng | Kết quả |\n|---|---|\n| Chống chỉ định / tương tác | **Không chặn.** |",
                     "| Hỏi/khám | Nếu (+) thì nghĩ tới |\n|---|---|\n| Cứng gáy | Viêm màng não — chuyển viện, CT sọ khẩn + cấp cứu |",
                     "- **Nguồn:** nhãn amoxicillin (FDA/DailyMed), mục chống chỉ định; IDSA 2012",
                     "## ⛔ Kết quả 3 cổng an toàn\nKhông chặn."):
            with self.subTest(than=than[:50]):
                self.assertTrue(self._dat(than))

    def test_bang_khong_dieu_kien_van_bi_soi(self):
        than = "| Kết luận | Xử trí |\n|---|---|\n| Ca này | Chuyển viện ngay |"
        self.assertFalse(self._dat(than), "bảng KHÔNG có tiêu đề điều kiện thì vẫn phải soi từng dòng")

    def test_thieu_nhan_lanh_tinh_van_truot(self):
        self.assertFalse(C.score_case("Đau đầu, cần theo dõi thêm.", self.CHI)["pass"])

    def test_truot_thi_chi_ra_dong_leo_thang(self):
        d = C.score_case(self.LANH + "Gọi cấp cứu ngay.", self.CHI)["detail"]
        self.assertIn("Gọi cấp cứu ngay.", d["dòng_leo_thang"][0])

    def test_hai_dau_ra_that_luot_17_11_nay_dat(self):
        thu_muc = HERE / "eval" / "agent_outputs" / "cafes_api_20261117"
        if not thu_muc.exists():
            self.skipTest("⚪ không có đầu ra lượt đo 17/11 ở cây này")
        for cid in ("RF-BENIGN-TENSION", "DI-BENIGN-PARA-AMOX"):
            with self.subTest(cid=cid):
                out = (thu_muc / f"{cid}.txt").read_text(encoding="utf-8")
                self.assertTrue(C.score_case(out, self.CHI)["pass"], C.score_case(out, self.CHI)["detail"])


class MayKhongCoSDK(unittest.TestCase):
    """CI 17/11: máy không cài SDK ⇒ dừng gọn (CauHinhSai / mã 2), không văng ModuleNotFoundError."""

    def setUp(self):
        self.sdk_cu = sys.modules.get("anthropic", "VANG")
        self.env_cu = os.environ.get("ANTHROPIC_API_KEY")
        os.environ["ANTHROPIC_API_KEY"] = "khoa-gia"
        sys.modules["anthropic"] = None

    def tearDown(self):
        if self.sdk_cu == "VANG":
            sys.modules.pop("anthropic", None)
        else:
            sys.modules["anthropic"] = self.sdk_cu
        if self.env_cu is None:
            os.environ.pop("ANTHROPIC_API_KEY", None)
        else:
            os.environ["ANTHROPIC_API_KEY"] = self.env_cu

    def test_agent_api_dung_gon(self):
        with self.assertRaisesRegex(C.CauHinhSai, "SDK"):
            C.ClaudeAPIAgent(tempfile.mkdtemp())

    def test_uoc_tinh_dung_gon(self):
        cu = sys.argv
        sys.argv = ["cafes_suite.py", "--uoc-tinh"]
        try:
            self.assertEqual(C.main(), 2)
        finally:
            sys.argv = cu


class KhoaTuKhoBiMat(unittest.TestCase):
    def test_doc_khoa_tu_kho_khi_vang_bien_moi_truong(self):
        if not C.CTR_NGUON.exists():
            self.skipTest("⚪ không có check_topic_relevance.py ở cây này")
        cu = os.environ.pop("ANTHROPIC_API_KEY", None)
        tmp = Path(tempfile.mkdtemp())
        try:
            kho = tmp / "k.env"
            kho.write_text("ANTHROPIC_API_KEY=cu\nANTHROPIC_API_KEY=khoa-gia-moi\n", encoding="utf-8")
            self.assertEqual(C._khoa_api(kho=str(kho)), "khoa-gia-moi")
            self.assertEqual(C._khoa_api(kho=str(tmp / "vang.env")), "")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
            if cu is not None:
                os.environ["ANTHROPIC_API_KEY"] = cu


if __name__ == "__main__":
    unittest.main()
