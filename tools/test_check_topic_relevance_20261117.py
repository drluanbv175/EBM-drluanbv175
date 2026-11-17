#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chốt cổng kiểm lạc chủ đề (17/11/2026) — CI thu được, không gọi mạng, không tốn tiền.

Hai phần:
  1. Nạp các lớp kiểm CHUẨN VÀNG ở `sync/skills/cap-nhat-chung-cu-y-khoa/tools/test_check_topic_relevance.py`
     — CI chỉ chạy `pytest tools/`, nên tệp ở nguồn chuẩn không bao giờ được thu nếu không có tệp này.
  2. Chốt HÀNH VI cho bốn lỗi đo được 17/11/2026:
     • cắt cụt: Sonnet 5.5 bật thinking, ăn CHUNG max_tokens=2000 với JSON phán quyết — dashboard Suy tim
       83 mục ⇒ stop_reason=max_tokens ở 2000/2000, JSON cụt. Nay max_tokens 16000, effort «low»
       (bộ vàng 19 mục: 18/19 ở cả cấu hình cũ lẫn mới — hạ effort không làm kém đi);
     • im lặng: JSON hỏng từng quy về «skipped» (như thiếu khoá) ⇒ cảm biến ⑦r không báo. Nay «error»;
     • nuốt «uncertain»: verify_dashboard chỉ đọc off_topic, nên mục không chắc vẫn in «đều khớp»;
     • từ chối: có dự phòng `fallbacks: "default"` (beta), còn từ chối ⇒ «error» kèm nhóm.
Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
NGUON = HERE.parent / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools"
CTR = NGUON / "check_topic_relevance.py"


def _nap(ten: str, duong_dan: Path):
    if str(duong_dan.parent) not in sys.path:
        sys.path.insert(0, str(duong_dan.parent))
    spec = importlib.util.spec_from_file_location(ten, duong_dan)
    m = importlib.util.module_from_spec(spec)
    sys.modules[ten] = m
    spec.loader.exec_module(m)
    return m


# ── Phần 1: chốt chuẩn vàng của nguồn chuẩn, CI thu qua đây ──
if (NGUON / "test_check_topic_relevance.py").exists():
    _goc = _nap("_chot_ctr_chuan_vang", NGUON / "test_check_topic_relevance.py")
    for _ten in dir(_goc):
        _lop = getattr(_goc, _ten)
        if isinstance(_lop, type) and issubclass(_lop, unittest.TestCase) and _lop.__module__ == _goc.__name__:
            globals()["ChuanVang" + _ten] = _lop


# ── Phần 2: chốt hành vi ──
DASHBOARD = """<html><script>const DATA = {
  meta: { question: 'Chủ đề thử' },
  items: [ { id: 'ITEM-1', title: 'Bài thử', action: 'Cân nhắc' } ],
  summary: { conclusion: 'x', doNow: [], dontDo: [], redFlags: [] }
};</script></html>"""
JSON_DUNG = '{"ITEM-1": {"verdict": "in_topic", "reason": "x"}}'


def _sdk_gia(ghi: list, stop: str = "end_turn", text: str = JSON_DUNG, nhom: str | None = None):
    """Module `anthropic` giả: ghi lại kênh (thuong/beta) và tham số mỗi lượt gọi."""
    def _tra_loi():
        return types.SimpleNamespace(
            stop_reason=stop,
            stop_details=types.SimpleNamespace(category=nhom) if nhom else None,
            content=[types.SimpleNamespace(type="thinking", thinking=""), types.SimpleNamespace(type="text", text=text)])

    class _Msgs:
        def __init__(self, kenh):
            self.kenh = kenh

        def create(self, **kw):
            ghi.append((self.kenh, kw))
            return _tra_loi()

    class _Cli:
        def __init__(self, api_key=None):
            self.messages = _Msgs("thuong")
            self.beta = types.SimpleNamespace(messages=_Msgs("beta"))

    m = types.ModuleType("anthropic")
    m.Anthropic = _Cli
    return m


class _CoSoCong(unittest.TestCase):
    def setUp(self):
        if not CTR.exists():
            self.skipTest("⚪ không có check_topic_relevance.py ở cây này")
        self.ctr = _nap(f"_ctr_{self.id()}", CTR)
        self.tmp = Path(tempfile.mkdtemp())
        self.ctr.KHO_BI_MAT = str(self.tmp / "vang.env")          # không bao giờ đọc kho khoá THẬT
        self.ctr.NHAT_KY_API = str(self.tmp / "nhat-ky-api.json")  # không bao giờ ghi nhật ký THẬT
        self.env_cu = {k: os.environ.pop(k, None) for k in ("ANTHROPIC_API_KEY", "TOPIC_CHECK_MODEL", "TOPIC_CHECK_EFFORT")}
        self.sdk_cu = sys.modules.get("anthropic")
        self.html = self.tmp / "dash.html"
        self.html.write_text(DASHBOARD, encoding="utf-8")

    def tearDown(self):
        for k, v in self.env_cu.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        if self.sdk_cu is None:
            sys.modules.pop("anthropic", None)
        else:
            sys.modules["anthropic"] = self.sdk_cu
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _gan(self, **kw) -> list:
        ghi: list = []
        os.environ["ANTHROPIC_API_KEY"] = "khoa-gia-cho-kiem-thu"
        sys.modules["anthropic"] = _sdk_gia(ghi, **kw)
        return ghi


class GoiDungThamSoTheHeHienHanh(_CoSoCong):
    def test_model_hien_hanh_goi_beta_effort_low_max_16000_co_du_phong(self):
        ghi = self._gan()
        self.assertEqual(self.ctr.call_claude("hỏi"), JSON_DUNG)
        kenh, kw = ghi[0]
        self.assertEqual(kenh, "beta")
        self.assertEqual(kw["model"], "claude-sonnet-5-5")
        self.assertEqual(kw["max_tokens"], 16000)
        self.assertEqual(kw["output_config"], {"effort": "low"})
        self.assertEqual(kw["betas"], [self.ctr.BETA_DU_PHONG])
        self.assertEqual(kw["fallbacks"], "default")

    def test_model_khac_goi_kenh_thuong_khong_them_tham_so_moi(self):
        ghi = self._gan()
        os.environ["TOPIC_CHECK_MODEL"] = "claude-haiku-4-5"
        self.ctr.call_claude("hỏi")
        kenh, kw = ghi[0]
        self.assertEqual(kenh, "thuong")
        self.assertNotIn("output_config", kw)
        self.assertNotIn("fallbacks", kw)


class KetQuaHongLaErrorKhongPhaiSkipped(_CoSoCong):
    def test_cat_cut_thanh_error(self):
        self._gan(stop="max_tokens", text='{"ITEM-1": {"verd')
        kq = self.ctr._cham_chu_de(str(self.html))
        self.assertEqual(kq["status"], "error")
        self.assertIn("CẮT CỤT", kq["message"])

    def test_tu_choi_thanh_error_kem_nhom(self):
        self._gan(stop="refusal", text="", nhom="bio")
        kq = self.ctr._cham_chu_de(str(self.html))
        self.assertEqual(kq["status"], "error")
        self.assertIn("bio", kq["message"])

    def test_json_hong_thanh_error(self):
        self._gan(text="khong phai json")
        self.assertEqual(self.ctr._cham_chu_de(str(self.html))["status"], "error")

    def test_thieu_khoa_van_la_skipped(self):
        sys.modules["anthropic"] = _sdk_gia([])
        kq = self.ctr._cham_chu_de(str(self.html))
        self.assertEqual(kq["status"], "skipped")

    def test_cat_cut_len_hom_viec_uu_tien_1(self):
        """Đầu–cuối: cổng cụt ⇒ nhật ký «error» ⇒ cảm biến ⑦r báo 👤 ưu tiên 1 (trước đây im lặng)."""
        self._gan(stop="max_tokens", text="{")
        self.ctr.check_dashboard_topic_relevance(str(self.html))
        nk = json.loads(Path(self.ctr.NHAT_KY_API).read_text(encoding="utf-8"))
        self.assertEqual(nk["trang_thai"], "error")
        tdx = _nap("_tdx_bh180", HERE / "tu_de_xuat_viec.py")
        viec = tdx.giac_quan_api_claude(tep=Path(self.ctr.NHAT_KY_API))
        self.assertTrue(viec and viec[0][0] == 1 and viec[0][1] == "👤", viec)


class KiemThuKhongChamTrangThaiThat(_CoSoCong):
    """Rào 17/11/2026: dưới pytest, cổng không đọc kho khoá THẬT, không ghi nhật ký THẬT — kể cả qua tiến trình con.
    Thủ phạm đo được: test_xuat_goi_cap_nhat_workflow_20260904 chạy xuat_goi --online ⇒ ghi đè nhật ký thật."""

    def _gia_lam_that(self):
        kho = self.tmp / "kho-that.env"
        kho.write_text("ANTHROPIC_API_KEY=khoa-gia-dong-vai-that\n", encoding="utf-8")
        nk = self.tmp / "nk-that.json"
        nk.write_text("CU", encoding="utf-8")
        self.ctr._KHO_THAT = self.ctr.KHO_BI_MAT = str(kho)
        self.ctr._NK_THAT = self.ctr.NHAT_KY_API = str(nk)
        return kho, nk

    def test_duoi_pytest_khong_doc_kho_that(self):
        self.assertTrue(os.environ.get("PYTEST_CURRENT_TEST"), "pytest phải đặt biến này")
        self._gia_lam_that()
        self.assertEqual(self.ctr._khoa_tu_kho(), "")

    def test_duoi_pytest_khong_ghi_nhat_ky_that(self):
        _, nk = self._gia_lam_that()
        self.ctr.ghi_nhat_ky_api({"status": "ok", "total_items": 3})
        self.assertEqual(nk.read_text(encoding="utf-8"), "CU")

    def test_chu_dong_do_that_thi_mo_rao(self):
        kho, nk = self._gia_lam_that()
        os.environ["EBM_KIEM_API_THAT"] = "1"
        try:
            self.assertEqual(self.ctr._khoa_tu_kho(), "khoa-gia-dong-vai-that")
            self.ctr.ghi_nhat_ky_api({"status": "ok", "total_items": 3})
            self.assertIn('"trang_thai": "ok"', nk.read_text(encoding="utf-8"))
        finally:
            os.environ.pop("EBM_KIEM_API_THAT", None)

    def test_tien_trinh_con_ke_thua_rao(self):
        """Đúng đường thủ phạm: tiến trình con, HOME có kho khoá + nhật ký «thật» — không được đọc, không được ghi."""
        nha = self.tmp / "nha"
        (nha / ".ebm-secrets").mkdir(parents=True)
        (nha / ".ebm-secrets" / "medical-ebm-automation.env").write_text("ANTHROPIC_API_KEY=khoa-gia\n", encoding="utf-8")
        (nha / ".ebm-api-claude.json").write_text("CU", encoding="utf-8")
        ma = ("import sys, json; sys.path.insert(0, sys.argv[1]); import check_topic_relevance as c; "
              "print(json.dumps(c.check_dashboard_topic_relevance(sys.argv[2])))")
        env = {k: v for k, v in os.environ.items() if k not in ("ANTHROPIC_API_KEY", "EBM_KIEM_API_THAT")}
        env.update(HOME=str(nha), USERPROFILE=str(nha), PYTHONIOENCODING="utf-8")
        r = subprocess.run([sys.executable, "-B", "-c", ma, str(NGUON), str(self.html)], capture_output=True,
                           text=True, encoding="utf-8", timeout=120, env=env)
        kq = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertEqual(kq["status"], "skipped", r.stdout + r.stderr)
        self.assertEqual((nha / ".ebm-api-claude.json").read_text(encoding="utf-8"), "CU")


class VerifyDashboardKhongNuotUncertain(unittest.TestCase):
    """Chạy verify_dashboard THẬT trong thư mục tạm, với check_topic_relevance giả trả kết quả cố định."""

    def setUp(self):
        if not (NGUON / "verify_dashboard.py").exists():
            self.skipTest("⚪ không có verify_dashboard.py ở cây này")
        self.tmp = Path(tempfile.mkdtemp())
        for ten in ("verify_dashboard.py", "dashboard_content_audit.py"):
            if (NGUON / ten).exists():
                shutil.copy2(NGUON / ten, self.tmp / ten)
        (self.tmp / "check_topic_relevance.py").write_text(
            "import json, os\n\ndef check_dashboard_topic_relevance(p):\n    return json.loads(os.environ['KQ_GIA'])\n",
            encoding="utf-8")
        self.html = self.tmp / "dash.html"
        self.html.write_text(DASHBOARD, encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _chay(self, uncertain: list, off_topic: list) -> str:
        kq = {"status": "ok", "topic": "Chủ đề thử", "total_items": 3, "off_topic": off_topic, "uncertain": uncertain}
        env = dict(os.environ, KQ_GIA=json.dumps(kq), PYTHONIOENCODING="utf-8")
        r = subprocess.run([sys.executable, "-B", str(self.tmp / "verify_dashboard.py"), str(self.html), "--check-topic"],
                           capture_output=True, text=True, encoding="utf-8", timeout=120, env=env, cwd=str(self.tmp))
        return r.stdout + r.stderr

    def test_co_uncertain_thi_bao_khong_chac_va_khong_noi_deu_khop(self):
        ra = self._chay(["ITEM-2", "ITEM-3"], [])
        self.assertIn("KHÔNG CHẮC", ra)
        self.assertIn("ITEM-2, ITEM-3", ra)
        self.assertNotIn("đều khớp chủ đề", ra)

    def test_khong_co_uncertain_khong_lac_thi_moi_noi_deu_khop(self):
        ra = self._chay([], [])
        self.assertIn("3/3 item đều khớp chủ đề", ra)
        self.assertNotIn("KHÔNG CHẮC", ra)

    def test_vua_lac_vua_khong_chac_bao_ca_hai(self):
        ra = self._chay(["ITEM-3"], [{"id": "ITEM-2", "title": "b", "reason": "r"}])
        self.assertIn("LẠC CHỦ ĐỀ", ra)
        self.assertIn("KHÔNG CHẮC", ra)
        self.assertNotIn("đều khớp chủ đề", ra)


if __name__ == "__main__":
    unittest.main()
