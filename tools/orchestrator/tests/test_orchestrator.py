#!/usr/bin/env python3
"""Test bộ Orchestrator EBM — chạy OFFLINE (dry-run), không cần API/mạng.

Chạy:  python tools/orchestrator/tests/test_orchestrator.py
hoặc:  python -m unittest discover -s tools/orchestrator/tests
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

# cho phép `import orchestrator` (thêm thư mục tools/ vào path)
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from orchestrator import intent as intent_mod  # noqa: E402
from orchestrator import orchestrator as orchestrator_mod  # noqa: E402
from orchestrator.context import ContextStore  # noqa: E402
from orchestrator.intent import route  # noqa: E402
from orchestrator.knowledge import KnowledgeLayer  # noqa: E402
from orchestrator.orchestrator import Orchestrator  # noqa: E402
from orchestrator.registry import Registry  # noqa: E402
from orchestrator.tools_registry import ToolRegistry  # noqa: E402


class TestRegistry(unittest.TestCase):
    def setUp(self):
        self.reg = Registry.load()

    def test_counts(self):
        c = self.reg.counts()
        self.assertEqual(c["total"], 50, "phải có đúng 50 agent")
        self.assertEqual(c["clinical"], 21)
        self.assertEqual(c["research"], 28)
        self.assertEqual(c["guardrail"], 1)
        self.assertEqual(c["unknown"], 0, "mọi agent phải được phân cụm từ README")

    def test_key_agents_present(self):
        for name in ("dieu-phoi-lam-sang", "dieu-phoi-nghien-cuu", "tham-dinh-dau-ra",
                     "quan-ly-khang-dong", "tham-dinh-do-chinh-xac-chan-doan"):
            self.assertTrue(self.reg.has(name), f"thiếu agent {name}")


class TestIntent(unittest.TestCase):
    def test_clinical_case(self):
        r = route("Tôi có bệnh nhân nam 68 tuổi ĐTĐ2, eGFR 40, thêm thuốc gì?")
        self.assertEqual(r.kind, "clinical_case")
        self.assertEqual(r.target, "dieu-phoi-lam-sang")

    def test_research_topic_beats_benh_nhan(self):
        # Regression: 'đề tài' phải thắng 'bệnh nhân' (mô tả quần thể NC)
        r = route("Đề tài hiệu quả metformin ở bệnh nhân PCOS ngoại trú")
        self.assertEqual(r.kind, "research_topic")
        self.assertEqual(r.target, "dieu-phoi-nghien-cuu")

    def test_single_task_gate(self):
        r = route("Đơn này an toàn không, thuốc có đánh nhau không?")
        self.assertEqual(r.kind, "single_task")
        self.assertEqual(r.target, "ke-don-an-toan")

    def test_single_task_nogate(self):
        r = route("Guideline nói gì về đích huyết áp ở người cao tuổi?")
        self.assertEqual(r.kind, "single_task")
        self.assertEqual(r.target, "tra-cuu-chung-cu")

    def test_unknown(self):
        r = route("xin chào buổi sáng")
        self.assertEqual(r.kind, "unknown")


class TestOrchestration(unittest.TestCase):
    def setUp(self):
        self.orch = Orchestrator()

    def test_validate_clean(self):
        warns = self.orch.validate()
        self.assertEqual(warns, [], f"điều phối ⇄ registry phải sạch, có cảnh báo: {warns}")

    def test_validate_catches_dangling_single_task_reference(self):
        # Regression 2026-07-11: validate() trước đây chỉ quét flows.py, bỏ sót tham chiếu
        # treo trong intent.SINGLE_TASK_RULES/GATE_HINTS/REROUTE_DEFAULT.
        orig_rules = list(intent_mod.SINGLE_TASK_RULES)
        orig_hints = dict(orchestrator_mod.GATE_HINTS)
        orig_reroute = dict(orchestrator_mod.REROUTE_DEFAULT)
        try:
            intent_mod.SINGLE_TASK_RULES.append((["test-fake-kw"], "ten-agent-treo-single-task", "test"))
            warns_single = self.orch.validate()
            self.assertTrue(any("ten-agent-treo-single-task" in w for w in warns_single))

            intent_mod.SINGLE_TASK_RULES[:] = orig_rules
            orchestrator_mod.GATE_HINTS["ten-agent-treo-gate"] = "A"
            warns_gate = self.orch.validate()
            self.assertTrue(any("ten-agent-treo-gate" in w for w in warns_gate))

            orchestrator_mod.GATE_HINTS.clear()
            orchestrator_mod.GATE_HINTS.update(orig_hints)
            orchestrator_mod.REROUTE_DEFAULT["FAKE"] = "ten-agent-treo-reroute"
            warns_reroute = self.orch.validate()
            self.assertTrue(any("ten-agent-treo-reroute" in w for w in warns_reroute))
        finally:
            intent_mod.SINGLE_TASK_RULES[:] = orig_rules
            orchestrator_mod.GATE_HINTS.clear()
            orchestrator_mod.GATE_HINTS.update(orig_hints)
            orchestrator_mod.REROUTE_DEFAULT.clear()
            orchestrator_mod.REROUTE_DEFAULT.update(orig_reroute)
        self.assertEqual(self.orch.validate(), [], "phải sạch lại sau khi khôi phục")

    def test_clinical_stops_at_gate_A_and_B(self):
        s = self.orch.handle("Tôi có bệnh nhân nam 68, ĐTĐ2, thêm thuốc gì?", persist=False)
        self.assertEqual(s.kind, "clinical_case")
        self.assertIn("A", s.gates_pending)
        self.assertIn("B", s.gates_pending)
        self.assertEqual(s.exit_code, 2, "gate_pending → mã thoát 2")
        # guardrail luôn là bước cuối
        self.assertTrue(any(e["agent"] == "tham-dinh-dau-ra" for e in s.trace))

    def test_research_hard_gates(self):
        s = self.orch.handle("Đề tài metformin ở PCOS", persist=False)
        self.assertEqual(s.kind, "research_topic")
        for g in ("G2", "G4", "G9"):
            self.assertIn(g, s.gates_pending)
        self.assertEqual(s.exit_code, 2)

    def test_single_task_released(self):
        s = self.orch.handle("Guideline nói gì về đích huyết áp?", persist=False)
        self.assertEqual(s.kind, "single_task")
        self.assertEqual(s.gates_pending, [])
        self.assertEqual(s.exit_code, 0, "không cổng → released → mã thoát 0")

    def test_no_dangling_agent_in_plan(self):
        # mọi agent trong trace phải tồn tại trong registry (status 'skipped' OK, 'error' không)
        s = self.orch.handle("Tôi có bệnh nhân đau ngực", persist=False)
        for e in s.trace:
            self.assertNotEqual(e["status"], "error", f"agent treo trong plan: {e['agent']}")

    def test_capabilities_has_six(self):
        caps = self.orch.capabilities()
        self.assertEqual(len(caps), 6)

    # ── Nhánh có điều kiện (vá lỗ hổng "chạy mù mọi nhánh") ──────────
    def _status_of(self, session, agent_name):
        for e in session.trace:
            if e["agent"] == agent_name:
                return e["status"]
        return None

    def test_labs_branch_runs_when_signal_present(self):
        s = self.orch.handle("Bệnh nhân đau ngực, kết quả xét nghiệm troponin tăng, cần đánh giá",
                             persist=False)
        self.assertEqual(self._status_of(s, "dien-giai-can-lam-sang"), "planned")

    def test_labs_branch_skipped_without_signal(self):
        s = self.orch.handle("Bệnh nhân nam 50 tuổi than đau đầu 2 ngày nay", persist=False)
        self.assertEqual(self._status_of(s, "dien-giai-can-lam-sang"), "skipped")

    def test_diagnostic_branch_conditional(self):
        s_yes = self.orch.handle("Bệnh nhân đau họng sốt, có nên làm xét nghiệm liên cầu không?",
                                 persist=False)
        self.assertEqual(self._status_of(s_yes, "chan-doan-xac-suat"), "planned")
        self.assertEqual(self._status_of(s_yes, "tham-dinh-do-chinh-xac-chan-doan"), "planned")
        s_no = self.orch.handle("Bệnh nhân đau đầu 2 ngày nay, khám tổng quát", persist=False)
        self.assertEqual(self._status_of(s_no, "chan-doan-xac-suat"), "skipped")

    def test_specialty_branch_pain(self):
        s = self.orch.handle("Bệnh nhân đau lưng mạn tính hơn 6 tháng, đang dùng opioid", persist=False)
        self.assertEqual(self._status_of(s, "dau-man-tinh"), "planned")
        self.assertEqual(self._status_of(s, "cham-soc-giam-nhe"), "skipped")
        self.assertEqual(self._status_of(s, "tram-cam-lo-au"), "skipped")

    def test_closing_loop_always_present_clinical(self):
        s = self.orch.handle("Bệnh nhân nam 50 tuổi đau đầu", persist=False)
        self.assertEqual(self._status_of(s, "ket-qua-hoc-tap"), "planned")
        self.assertEqual(self._status_of(s, "cap-nhat-guideline"), "planned")

    def test_research_g1_conditional_agents(self):
        s_prom = self.orch.handle("Đề tài xây dựng và kiểm định thang đo hài lòng người bệnh COSMIN",
                                  persist=False)
        self.assertEqual(self._status_of(s_prom, "cong-cu-do-luong"), "planned")
        self.assertEqual(self._status_of(s_prom, "kinh-te-y-te"), "skipped")

        s_econ = self.orch.handle("Đề tài phân tích chi phí–hiệu quả của can thiệp X so với chăm sóc thường quy",
                                  persist=False)
        self.assertEqual(self._status_of(s_econ, "kinh-te-y-te"), "planned")
        self.assertEqual(self._status_of(s_econ, "cong-cu-do-luong"), "skipped")

    def test_signals_checkpoint_recorded(self):
        s = self.orch.handle("Bệnh nhân rung nhĩ đang dùng warfarin, cần chuyển DOAC không?",
                             persist=False)
        sig_ckpt = next((c for c in s.checkpoints if c.get("stage") == "signals"), None)
        self.assertIsNotNone(sig_ckpt, "phải có checkpoint ghi tín hiệu ngữ cảnh")
        self.assertTrue(sig_ckpt["data"]["flags"].get("anticoag"))


class TestContextResume(unittest.TestCase):
    def test_resume_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = ContextStore(Path(tmp))
            orch = Orchestrator()
            s = orch.handle("Đơn này an toàn không?", store=store, persist=True)
            back = orch.resume(s.session_id, store=store)
            self.assertIsNotNone(back)
            self.assertEqual(back.request, s.request)
            self.assertEqual(back.exit_code, s.exit_code)


class TestKnowledgeAndTools(unittest.TestCase):
    def test_knowledge_tiers(self):
        k = KnowledgeLayer()
        self.assertEqual(len(k.tiers), 4)
        self.assertEqual(k.tier_of("Cochrane"), "0")
        self.assertEqual(k.tier_of("PubMed/MEDLINE"), "1")
        self.assertTrue(len(k.retrieval_order()) >= 4)
        self.assertEqual(k.verify_against_ssot(), [], "SSOT connector phải còn đủ tham chiếu")

    def test_tools_registered(self):
        tr = ToolRegistry()
        self.assertIn("grade", tr.tools)
        self.assertIn("nnt", tr.tools)
        self.assertTrue(tr.for_agent("tham-dinh-grade-nnt"))
        # dry-run trả về lệnh, không chạy thật
        res = tr.invoke("grade", ["--design", "rct"], dry_run=True)
        self.assertIn("cmd", res)


class TestGuardrailReroute(unittest.TestCase):
    """D3 — re-route khi guardrail TRẢ-VỀ-SỬA (trích dẫn không phân giải → quay lại kiểm chứng).

    `guardrail_verdict` là seam: mỗi test bơm một verdict giả lập (production cắm run_eval /
    tham-dinh-dau-ra). Kiểm ĐÚNG hành vi mà rubric D3 nhắm tới: input hỏng ≠ input sạch.
    """
    def setUp(self):
        self.orch = Orchestrator()

    def _fail_then_pass(self, code="R1", reroute_to="kiem-chung-trich-dan"):
        """Verdict TRẢ-VỀ-SỬA lần đầu (trích dẫn hỏng), ĐẠT ở lần sau (đã sửa)."""
        calls = {"n": 0}
        def verdict(_session):
            calls["n"] += 1
            if calls["n"] == 1:
                return {"status": "returned_for_fix", "code": code, "reroute_to": reroute_to}
            return {"status": "pass"}
        return verdict

    def _reroutes(self, session):
        return [e for e in session.trace if e.get("status") == "reroute"]

    def test_reroute_on_unresolved_citation(self):
        # Ca có trích dẫn không phân giải → phải RE-ROUTE về kiem-chung-trich-dan rồi mới release
        s = self.orch.handle("Guideline nói gì về đích huyết áp?", persist=False,
                             guardrail_verdict=self._fail_then_pass())
        rr = self._reroutes(s)
        self.assertEqual(len(rr), 1, "phải có đúng 1 lần re-route")
        self.assertEqual(rr[0]["agent"], "kiem-chung-trich-dan")
        self.assertEqual(rr[0]["reroute_for"], "R1")
        self.assertEqual(s.retries, 1, "đúng 1 vòng guardrail_fail (mã sống)")
        self.assertEqual(s.exit_code, 0, "sau khi sửa xong → released")
        # có checkpoint log re-route (artifact D3)
        self.assertTrue(any(c.get("stage") == "reroute" for c in s.checkpoints))

    def test_no_reroute_when_clean(self):
        # Verdict sạch ngay → KHÔNG re-route, KHÔNG tiêu lượt retry
        s = self.orch.handle("Guideline nói gì về đích huyết áp?", persist=False,
                             guardrail_verdict=lambda _s: {"status": "pass"})
        self.assertEqual(self._reroutes(s), [])
        self.assertEqual(s.retries, 0)
        self.assertEqual(s.exit_code, 0)

    def test_default_no_verdict_is_backward_compatible(self):
        # KHÔNG truyền verdict → hành vi y hệt trước khi vá (không re-route, released)
        s = self.orch.handle("Guideline nói gì về đích huyết áp?", persist=False)
        self.assertEqual(self._reroutes(s), [])
        self.assertEqual(s.retries, 0)
        self.assertEqual(s.exit_code, 0)

    def test_reroute_exhausts_to_blocked(self):
        # Verdict luôn hỏng → cạn MAX_RETRIES → BLOCK/leo thang (mã thoát 3), không lặp vô hạn
        s = self.orch.handle("Guideline nói gì về đích huyết áp?", persist=False,
                             guardrail_verdict=lambda _s: {"status": "returned_for_fix", "code": "R1"})
        self.assertEqual(s.exit_code, 3, "cạn lượt → blocked → mã thoát 3")
        self.assertIn("leo thang", s.status)
        self.assertTrue(any(e.get("status") == "blocked" for e in s.trace))
        # số lần re-route = MAX_RETRIES (mỗi vòng còn lượt mới re-route)
        from orchestrator.lifecycle import MAX_RETRIES
        self.assertEqual(len(self._reroutes(s)), MAX_RETRIES)

    def test_reroute_default_target_by_code(self):
        # Không chỉ định reroute_to → suy đích theo mã (R4 = nghi bịa → truy xuất lại nguồn)
        s = self.orch.handle("Guideline nói gì về đích huyết áp?", persist=False,
                             guardrail_verdict=self._fail_then_pass(code="R4", reroute_to=None))
        rr = self._reroutes(s)
        self.assertEqual(len(rr), 1)
        self.assertEqual(rr[0]["agent"], "tra-cuu-chung-cu")

    def test_fail_closed_on_none_verdict(self):
        # M3: verdict trả None (dị dạng) → KHÔNG được release; FAIL-CLOSED → blocked, leo thang
        s = self.orch.handle("Guideline nói gì về đích huyết áp?", persist=False,
                             guardrail_verdict=lambda _s: None)
        self.assertEqual(s.exit_code, 3, "verdict bất định → fail-closed → blocked (3), KHÔNG release")
        self.assertIn("bất định", s.status)
        self.assertIn("GUARDRAIL_INDETERMINATE", s.status)
        self.assertEqual(self._reroutes(s), [], "KHÔNG re-route mù khi verdict bất định")

    def test_fail_closed_on_verdict_exception(self):
        # M3: verdict_fn ném lỗi → KHÔNG crash phiên, KHÔNG release → blocked
        def boom(_s):
            raise RuntimeError("seam sản xuất hỏng")
        s = self.orch.handle("Guideline nói gì về đích huyết áp?", persist=False,
                             guardrail_verdict=boom)
        self.assertEqual(s.exit_code, 3)
        self.assertTrue(any(e.get("reroute_for") == "GUARDRAIL_ERROR" for e in s.trace))


class TestGuardrailBridge(unittest.TestCase):
    """D1+D3 operational: cổng rule-based THẬT (run_eval.evaluate) làm guardrail_verdict, cắt
    bản ghi APPRAISAL bền + drive re-route trên NỘI DUNG THẬT (không cần LLM).

    Ánh xạ verdict test bằng cách thay `evaluate` (kiểm logic bridge, độc lập nội dung cụ thể qua
    đủ mọi check); MỘT test integration dùng nội dung lỗi THẬT + run_eval.evaluate thật."""
    def setUp(self):
        from orchestrator import guardrail_bridge as gb
        self.gb = gb
        self.orch = Orchestrator()
        self._orig_load = gb._load_evaluate

    def tearDown(self):
        self.gb._load_evaluate = self._orig_load

    def _patch_evaluate(self, res):
        self.gb._load_evaluate = lambda: (lambda _text, _gold: res)

    def test_safe_target_redacts_pii_filename(self):
        # H1: tên file dính PII (SĐT / họ tên) → KHỬ trước khi ghi
        d1, _ = self.gb._safe_target("/x/BN_Nguyen Van A_0912345678.md")
        self.assertTrue(d1.startswith("redacted-"), "tên file có SĐT+tên phải bị khử")
        d2, _ = self.gb._safe_target("SGLT2-HFpEF-2026.md")
        self.assertEqual(d2, "SGLT2-HFpEF-2026.md", "tên file sạch giữ nguyên")

    def test_verdict_pass_mapping_and_emits(self):
        self._patch_evaluate({"verdict": "ĐẠT", "score": "13/13", "red_fails": []})
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "APPRAISALS.jsonl"
            v = self.gb.make_run_eval_verdict("x", source="test", at="2026-07-09T00:00:00",
                                              log_path=log)(None)
            self.assertEqual(v["status"], "pass")
            recs = [json.loads(x) for x in log.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(recs[-1]["verdict"], "PASS")

    def test_verdict_reroutable_code_no_escalate(self):
        # Lỗi SỬA ĐƯỢC (R1 = trích dẫn) → returned_for_fix, KHÔNG escalate → sẽ re-route
        self._patch_evaluate({"verdict": "TRẢ-VỀ-SỬA", "score": "9/13", "red_fails": ["pmid_or_doi"]})
        with tempfile.TemporaryDirectory() as tmp:
            v = self.gb.make_run_eval_verdict("x", source="test", at="2026-07-09T00:00:00",
                                              log_path=Path(tmp) / "a.jsonl")(None)
            self.assertEqual((v["status"], v["code"]), ("returned_for_fix", "R1"))
            self.assertFalse(v.get("escalate"), "R1 sửa được → KHÔNG escalate")

    def test_verdict_hard_code_escalates(self):
        # Lỗi CỔNG CỨNG (no_pii → R2) → escalate=True (leo thang ngay, không auto-fix)
        self._patch_evaluate({"verdict": "TRẢ-VỀ-SỬA", "score": "8/13", "red_fails": ["no_pii"]})
        with tempfile.TemporaryDirectory() as tmp:
            v = self.gb.make_run_eval_verdict("x", source="test", at="2026-07-09T00:00:00",
                                              log_path=Path(tmp) / "a.jsonl")(None)
            self.assertEqual(v["code"], "R2")
            self.assertTrue(v.get("escalate"), "mã cổng cứng phải escalate ngay")

    def test_end_to_end_pass_released(self):
        self._patch_evaluate({"verdict": "ĐẠT", "score": "13/13", "red_fails": []})
        with tempfile.TemporaryDirectory() as tmp:
            vf = self.gb.make_run_eval_verdict("x", source="test", at="2026-07-09T00:00:00",
                                               log_path=Path(tmp) / "a.jsonl")
            s = self.orch.handle("Guideline nói gì về đích huyết áp?", persist=False,
                                 guardrail_verdict=vf)
            self.assertEqual(s.exit_code, 0)

    def test_end_to_end_reroute_on_auto_fix_code(self):
        # Lỗi sửa-được (R1) + không có LLM sửa (text không đổi) → re-route ≤3 rồi leo thang (mã 3)
        self._patch_evaluate({"verdict": "TRẢ-VỀ-SỬA", "score": "9/13", "red_fails": ["pmid_or_doi"]})
        with tempfile.TemporaryDirectory() as tmp:
            vf = self.gb.make_run_eval_verdict("x", source="test", at="2026-07-09T00:00:00",
                                               log_path=Path(tmp) / "a.jsonl")
            s = self.orch.handle("Guideline nói gì về đích huyết áp?", persist=False,
                                 guardrail_verdict=vf)
            self.assertEqual(s.exit_code, 3)
            rr = [e for e in s.trace if e.get("status") == "reroute"]
            self.assertTrue(rr and rr[0]["agent"] == "kiem-chung-trich-dan",
                            "R1 → re-route tới kiem-chung-trich-dan")

    def test_end_to_end_real_hard_content_escalates_immediately(self):
        # INTEGRATION: nội dung lâm sàng lỗi THẬT + run_eval.evaluate THẬT (không patch). Có cờ
        # đỏ cổng cứng (R12 thiếu safety-net) → LEO THANG NGAY, KHÔNG re-route auto-fix vô nghĩa.
        dirty = "Uống cà phê làm giảm trầm cảm. Khuyến cáo dùng ngay."
        with tempfile.TemporaryDirectory() as tmp:
            vf = self.gb.make_run_eval_verdict(dirty, source="test", at="2026-07-09T00:00:00",
                                               log_path=Path(tmp) / "a.jsonl")
            s = self.orch.handle("Guideline nói gì về đích huyết áp?", persist=False,
                                 guardrail_verdict=vf)
            self.assertEqual(s.exit_code, 3, "cổng cứng → block/leo thang")
            self.assertEqual([e for e in s.trace if e.get("status") == "reroute"], [],
                             "cổng cứng KHÔNG re-route auto-fix")


if __name__ == "__main__":
    unittest.main(verbosity=2)
