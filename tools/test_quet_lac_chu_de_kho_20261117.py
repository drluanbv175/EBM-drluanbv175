#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chốt công cụ quét lạc chủ đề toàn kho (`tools/quet_lac_chu_de_kho.py`, 17/11/2026) — client Batch giả, không tốn tiền.

Khoá: chỉ bản MỚI NHẤT mỗi chủ đề; chạy khô không gửi gì; tham số batch đúng như cổng (max 16000, effort low) và
KHÔNG có `fallbacks` (Batch API không nhận); mọi hỏng hóc của một dashboard ⇒ «error» kèm lý do, không đoán;
`--tiep` không gửi lại (không trả tiền hai lần); dưới pytest không bao giờ đọc kho khoá thật. Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sys
import tempfile
import types
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
NGUON = HERE.parent / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools"


def _nap():
    spec = importlib.util.spec_from_file_location("_quet_kho_kiem", HERE / "quet_lac_chu_de_kho.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


Q = _nap()


def _dash(muc: list[tuple[str, str]], chu_de: str = "Tim mạch") -> str:
    ds = ", ".join(f"{{ id: '{i}', title: '{t}', action: '' }}" for i, t in muc)
    return (f"<html><script>const DATA = {{ meta: {{ question: '{chu_de}' }}, items: [ {ds} ], "
            "summary: { conclusion: 'x', doNow: [], dontDo: [], redFlags: [] } };</script></html>")


def _thanh_cong(text, stop="end_turn", nhom=None):
    return types.SimpleNamespace(type="succeeded", message=types.SimpleNamespace(
        stop_reason=stop, stop_details=types.SimpleNamespace(category=nhom) if nhom else None,
        content=[types.SimpleNamespace(type="text", text=text)],
        usage=types.SimpleNamespace(input_tokens=1000, output_tokens=100)))


class _ClientBatch:
    def __init__(self, ket_qua: dict, trang_thai=("in_progress", "ended")):
        self.gui: list = []
        self._tt = list(trang_thai)
        goc = self

        class _B:
            def create(self, requests):
                goc.gui.append(requests)
                return types.SimpleNamespace(id="msgbatch_gia")

            def retrieve(self, bid):
                s = goc._tt.pop(0) if len(goc._tt) > 1 else goc._tt[0]
                return types.SimpleNamespace(processing_status=s, request_counts=types.SimpleNamespace(
                    processing=1, succeeded=0, errored=0))

            def results(self, bid):
                return [types.SimpleNamespace(custom_id=k, result=v) for k, v in ket_qua.items()]

        self.messages = types.SimpleNamespace(batches=_B())


class _CoSo(unittest.TestCase):
    def setUp(self):
        if not (NGUON / "check_topic_relevance.py").exists():
            self.skipTest("⚪ không có check_topic_relevance.py ở cây này")
        self.goc = Path(tempfile.mkdtemp())
        dich = self.goc / Q.CTR_REL.parent
        dich.mkdir(parents=True)
        for ten in ("check_topic_relevance.py", "verify_dashboard.py", "dashboard_content_audit.py"):
            if (NGUON / ten).exists():
                shutil.copy2(NGUON / ten, dich / ten)
        kho = self.goc / "EBM-Dashboards"
        kho.mkdir()
        (kho / "WebDashboard_A_20261101.html").write_text(_dash([("ITEM-1", "cũ")]), encoding="utf-8")
        (kho / "WebDashboard_A_20261110.html").write_text(
            _dash([("ITEM-1", "Suy tim"), ("ITEM-2", "Thai kỳ")]), encoding="utf-8")
        (kho / "WebDashboard_B_20261105.html").write_text(
            _dash([("ITEM-1", "Rung nhĩ"), ("ITEM-2", "Mơ hồ")], "Tim mạch B"), encoding="utf-8")
        (kho / "WebDashboard_C_20261105.html").write_text("<html>không có DATA</html>", encoding="utf-8")
        self.env_cu = os.environ.pop("ANTHROPIC_API_KEY", None)

    def tearDown(self):
        shutil.rmtree(self.goc, ignore_errors=True)
        if self.env_cu is not None:
            os.environ["ANTHROPIC_API_KEY"] = self.env_cu

    def _chay(self, *thamso, client=None):
        return Q.main(["--goc", str(self.goc), "--nghi", "0", *thamso], client=client, ngu=lambda s: None)


JSON_A = json.dumps({"ITEM-1": {"verdict": "in_topic", "reason": "tim"},
                     "ITEM-2": {"verdict": "off_topic", "reason": "sản khoa"}})
JSON_B = json.dumps({"ITEM-1": {"verdict": "in_topic", "reason": "tim"},
                     "ITEM-2": {"verdict": "uncertain", "reason": "thiếu thông tin"}})


class ChonVaChayKho(_CoSo):
    def test_chi_lay_ban_moi_nhat_moi_chu_de(self):
        ten = [p.name for p in Q.chon_ban_moi_nhat(self.goc / "EBM-Dashboards")]
        self.assertIn("WebDashboard_A_20261110.html", ten)
        self.assertNotIn("WebDashboard_A_20261101.html", ten)

    def test_chay_kho_khong_gui_gi(self):
        cli = _ClientBatch({})
        self.assertEqual(self._chay(client=cli), 0)
        self.assertEqual(cli.gui, [])


class GuiVaChamDung(_CoSo):
    def test_tham_so_nhu_cong_khong_co_fallbacks_va_bao_cao_dung(self):
        cli = _ClientBatch({"d001": _thanh_cong(JSON_A), "d002": _thanh_cong(JSON_B)})
        self.assertEqual(self._chay("--ap-dung", client=cli), 0)
        yc = cli.gui[0]
        self.assertEqual(len(yc), 2, "C không có mục ⇒ không gửi")
        p = yc[0]["params"]
        self.assertEqual(p["model"], "claude-sonnet-5-5")
        self.assertEqual(p["max_tokens"], 16000)
        self.assertEqual(p["output_config"], {"effort": "low"})
        self.assertNotIn("fallbacks", p)
        tt = json.loads((self.goc / "state" / "quet-lac-chu-de.json").read_text(encoding="utf-8"))
        self.assertEqual(tt["batch_id"], "msgbatch_gia")
        md = next((self.goc / "EBM-Dashboards" / "derivatives").glob("QUET-LAC-CHU-DE_*.md")).read_text(encoding="utf-8")
        self.assertIn("1 mục NGHI LẠC CHỦ ĐỀ", md)
        self.assertIn("1 mục KHÔNG CHẮC", md)
        self.assertIn("Thai kỳ", md)
        self.assertIn("không mục nào bị gỡ", md)

    def test_moi_hong_hoc_la_error_va_ma_1(self):
        cli = _ClientBatch({"d001": _thanh_cong("{cụt", stop="max_tokens"),
                            "d002": types.SimpleNamespace(type="errored", error=types.SimpleNamespace(type="overloaded"))})
        self.assertEqual(self._chay("--ap-dung", client=cli), 1)
        js = json.loads(next((self.goc / "EBM-Dashboards" / "derivatives").glob("*.json")).read_text(encoding="utf-8"))
        ly_do = {c["tep"]: c["ly_do"] for c in js["ket_qua"]}
        self.assertIn("CẮT CỤT", ly_do["WebDashboard_A_20261110.html"])
        self.assertIn("errored", ly_do["WebDashboard_B_20261105.html"])

    def test_tu_choi_la_error_kem_nhom(self):
        cli = _ClientBatch({"d001": _thanh_cong("", stop="refusal", nhom="bio"), "d002": _thanh_cong(JSON_B)})
        self._chay("--ap-dung", client=cli)
        js = json.loads(next((self.goc / "EBM-Dashboards" / "derivatives").glob("*.json")).read_text(encoding="utf-8"))
        self.assertIn("bio", js["ket_qua"][0]["ly_do"])

    def test_tiep_khong_gui_lai(self):
        cli = _ClientBatch({"d001": _thanh_cong(JSON_A), "d002": _thanh_cong(JSON_B)})
        self._chay("--ap-dung", client=cli)
        cli2 = _ClientBatch({"d001": _thanh_cong(JSON_A), "d002": _thanh_cong(JSON_B)})
        self.assertEqual(self._chay("--tiep", "msgbatch_gia", client=cli2), 0)
        self.assertEqual(cli2.gui, [], "--tiep tuyệt đối không gửi lại (không trả tiền hai lần)")

    def test_qua_tran_cho_thi_dung_va_chi_cach_tiep(self):
        cli = _ClientBatch({}, trang_thai=("in_progress",))
        self.assertFalse(Q.cho_xong(cli, "msgbatch_gia", nghi=0, tran_giay=-1, ngu=lambda s: None))

    def test_duoi_pytest_khong_doc_kho_khoa_that(self):
        """Không tiêm client, không có biến môi trường ⇒ rào của cổng chặn kho khoá thật ⇒ dừng mã 2, không gọi API."""
        self.assertEqual(self._chay("--ap-dung"), 2)


if __name__ == "__main__":
    unittest.main()
