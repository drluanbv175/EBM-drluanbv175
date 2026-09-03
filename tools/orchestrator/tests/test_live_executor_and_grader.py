#!/usr/bin/env python3
"""Hồi quy cho runtime thật, artifact có revision và critic Q1–Q7 độc lập."""

from __future__ import annotations

import tempfile
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from orchestrator.agent_adapter import AgentExecutor, AgentResult, LLMExecutor  # noqa: E402
from orchestrator.context import Session  # noqa: E402
from orchestrator.guardrail_bridge import IndependentClinicalGrader, make_live_guardrail_verdict  # noqa: E402
from orchestrator.orchestrator import Orchestrator  # noqa: E402
from orchestrator.registry import Registry  # noqa: E402
from orchestrator.tools_registry import ToolRegistry  # noqa: E402


class FakeClient:
    def __init__(self, response):
        self.response = response
        self.prompts = []

    def generate(self, prompt, *, output_schema=None):
        self.prompts.append((prompt, output_schema))
        return self.response


class RevisingExecutor(AgentExecutor):
    """Sinh bản cũ ở lượt đầu và sửa thật khi guardrail re-route."""

    def execute(self, agent, registry, tools, task_context=None):
        del registry, tools
        if (task_context or {}).get("step") == "reroute":
            return AgentResult(agent, "ok", "đã sửa", content="BẢN MỚI có nguồn PMID: 12345678. Cần bác sĩ kiểm chứng.")
        if agent == "tham-dinh-dau-ra":
            return AgentResult(agent, "ok", "critic riêng không đè bản nháp", content="PHÁN ĐỊNH")
        return AgentResult(agent, "ok", "đã sinh", content="BẢN CŨ thiếu nguồn. Cần bác sĩ kiểm chứng.")


class TestLiveExecutor(unittest.TestCase):
    def test_llm_executor_uses_injected_client_and_returns_content(self):
        client = FakeClient({
            "status": "ok", "summary": "xong", "content": "Nội dung. Cần bác sĩ kiểm chứng.",
            "needs_input": "", "tool_calls": [],
        })
        result = LLMExecutor(client=client).execute(
            "tra-cuu-chung-cu", Registry.load(), ToolRegistry(),
            {"request": "câu hỏi", "current_output": "", "draft_revision": 0},
        )
        self.assertEqual(result.status, "ok")
        self.assertIn("Cần bác sĩ kiểm chứng", result.content)
        self.assertEqual(len(client.prompts), 1)
        self.assertIsNotNone(client.prompts[0][1], "thực thi phải dùng JSON schema")

    def test_needs_input_is_preserved_and_blocks_non_gate_release(self):
        client = FakeClient({
            "status": "needs_input", "summary": "thiếu câu hỏi", "content": "",
            "needs_input": "Cần PICO cụ thể", "tool_calls": [],
        })
        result = LLMExecutor(client=client).execute(
            "kiem-chung-trich-dan", Registry.load(), ToolRegistry(), {"request": "kiểm trích dẫn"},
        )
        self.assertEqual(result.status, "needs_input")

        class NeedsInputExecutor(AgentExecutor):
            def execute(self, agent, registry, tools, task_context=None):
                del registry, tools, task_context
                return AgentResult(agent, "needs_input", "thiếu dữ kiện", needs_input="Cần PMID/DOI")

        session = Orchestrator().handle(
            "Kiểm chứng trích dẫn học thuật", executor=NeedsInputExecutor(), persist=False,
        )
        self.assertEqual(session.exit_code, 3)
        self.assertIn("needs_clarification", session.status)

    def test_reroute_revises_live_artifact_before_regrading(self):
        seen = []

        def verdict(session):
            seen.append((session.draft_revision, session.current_output))
            if "BẢN CŨ" in session.current_output:
                return {"status": "returned_for_fix", "code": "R1"}
            return {"status": "pass"}

        session = Orchestrator().handle(
            "Guideline nói gì về đích huyết áp?",
            executor=RevisingExecutor(),
            guardrail_verdict=verdict,
            persist=False,
        )
        self.assertEqual(session.exit_code, 0)
        self.assertIn("BẢN MỚI", session.current_output)
        self.assertGreaterEqual(session.draft_revision, 2)
        self.assertTrue(any("BẢN CŨ" in text for _rev, text in seen))
        self.assertTrue(any("BẢN MỚI" in text for _rev, text in seen))
        critic = next(row for row in session.trace if row["agent"] == "tham-dinh-dau-ra")
        self.assertFalse(critic["draft_revised"], "critic không được đè artifact")

    def test_tool_receipts_propagate_to_guardrail_agent(self):
        seen = []

        class ReceiptExecutor(AgentExecutor):
            def execute(self, agent, registry, tools, task_context=None):
                del registry, tools
                seen.append((agent, dict(task_context or {})))
                if agent == "tham-dinh-dau-ra":
                    return AgentResult(agent, "ok", "đã chấm")
                return AgentResult(
                    agent, "ok", "đã xác minh", content="PMID: 41698208. Cần bác sĩ kiểm chứng.",
                    provenance={
                        "executed_tools": ["citation-resolve"],
                        "tool_receipts": {"citation-resolve": {"complete": True}},
                    },
                )

        session = Orchestrator().handle(
            "Kiểm chứng PMID 41698208", executor=ReceiptExecutor(), persist=False,
        )
        guardrail_context = next(ctx for agent, ctx in seen if agent == "tham-dinh-dau-ra")
        self.assertTrue(guardrail_context["tool_receipts"]["citation-resolve"]["complete"])
        self.assertEqual(session.executed_tools, ["citation-resolve"])


class TestIndependentGrader(unittest.TestCase):
    @staticmethod
    def _dimensions(red=None):
        red = set(red or [])
        return {
            q: {"status": "red" if q in red else "pass", "reason": "fixture"}
            for q in ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7")
        }

    def test_q2_red_forces_doctor_escalation(self):
        client = FakeClient({
            "applicable": True,
            "dimensions": self._dimensions({"Q2"}),
            "overall": "pass",  # cố tình model khai sai; code phải tính lại
            "doctor_escalation": False,
            "summary": "fixture",
        })
        result = IndependentClinicalGrader(client=client, model="critic-test").grade("x")
        self.assertEqual(result["overall"], "returned_for_fix")
        self.assertTrue(result["doctor_escalation"])
        self.assertEqual(result["red_codes"], ["Q2"])
        self.assertFalse(result["provenance"]["physician_panel"])

    def test_live_bridge_q2_blocks_without_reroute(self):
        from orchestrator import guardrail_bridge as gb
        original = gb._load_evaluate
        gb._load_evaluate = lambda: (lambda _text, _gold: {
            "verdict": "ĐẠT", "score": "13/13", "red_fails": [], "checks": []
        })
        try:
            client = FakeClient({
                "applicable": True, "dimensions": self._dimensions({"Q2"}),
                "overall": "returned_for_fix", "doctor_escalation": True, "summary": "fixture",
            })
            with tempfile.TemporaryDirectory() as tmp:
                verdict = make_live_guardrail_verdict(
                    IndependentClinicalGrader(client=client),
                    source="test", log_path=Path(tmp) / "appraisals.jsonl",
                )
                session = Orchestrator().handle(
                    "Tôi có bệnh nhân đau đầu, cần xử trí thế nào?",
                    executor=RevisingExecutor(), guardrail_verdict=verdict, persist=False,
                )
            self.assertEqual(session.exit_code, 3)
            self.assertIn("Q2", session.status)
            self.assertEqual([x for x in session.trace if x.get("status") == "reroute"], [])
        finally:
            gb._load_evaluate = original

    def test_live_bridge_classifies_citation_package_as_research(self):
        from orchestrator import guardrail_bridge as gb
        original = gb._load_evaluate
        seen = []

        def evaluate(_text, gold):
            seen.append(gold)
            return {"verdict": "ĐẠT", "score": "13/13", "red_fails": [], "checks": []}

        gb._load_evaluate = lambda: evaluate
        try:
            with tempfile.TemporaryDirectory() as tmp:
                verdict = make_live_guardrail_verdict(
                    IndependentClinicalGrader(client=FakeClient({})),
                    source="test", log_path=Path(tmp) / "appraisals.jsonl",
                )
                session = Session(
                    request="Kiểm chứng PMID 41698208", kind="single_task",
                    entry_agent="kiem-chung-trich-dan",
                    current_output="PMID: 41698208. Cần bác sĩ kiểm chứng.", draft_revision=1,
                )
                result = verdict(session)
            self.assertEqual(result["status"], "pass")
            self.assertEqual(seen[0]["type"], "research")
            self.assertFalse(seen[0]["must_have"]["reporting_standard"])
        finally:
            gb._load_evaluate = original

    def test_live_bridge_does_not_require_stard_for_citation_metadata_audit(self):
        text = (
            "PMID:41698208; DOI:10.7326/annals-25-02104. "
            "QUADAS-3: a revised tool for diagnostic test accuracy studies. "
            "Chưa đánh giá citation distortion trong bản thảo vì thiếu câu khẳng định. "
            "Cần bác sĩ kiểm chứng."
        )
        with tempfile.TemporaryDirectory() as tmp:
            verdict = make_live_guardrail_verdict(
                IndependentClinicalGrader(client=FakeClient({})),
                source="test", log_path=Path(tmp) / "appraisals.jsonl",
            )
            session = Session(
                request="Kiểm chứng PMID 41698208", kind="single_task",
                entry_agent="kiem-chung-trich-dan", current_output=text, draft_revision=1,
            )
            result = verdict(session)
        self.assertEqual(result["status"], "pass")
        self.assertNotIn("STD-REPORT", session.guardrail["rule_based"]["ledger_codes"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
