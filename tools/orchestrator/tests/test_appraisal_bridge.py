#!/usr/bin/env python3
"""Test appraisal_bridge — cầu cổng QA (APPRAISAL) → Lifecycle.

Vá D3: chứng minh `Lifecycle.guardrail_fail()` (từng là DEAD CODE) nay được thực thi + kiểm.
Chạy:  python tools/orchestrator/tests/test_appraisal_bridge.py
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # tools/

from orchestrator.appraisal_bridge import apply_verdict, run_self_fix_loop  # noqa: E402
from orchestrator.lifecycle import Lifecycle, MAX_RETRIES  # noqa: E402


class TestAppraisalBridge(unittest.TestCase):
    def test_pass_releases(self):
        lc = Lifecycle()
        self.assertEqual(apply_verdict(lc, "PASS"), "released")
        self.assertEqual(lc.exit_code(), 0)

    def test_return_then_pass(self):
        # RETURN 1 vòng rồi PASS — guardrail_fail() ĐƯỢC GỌI (không còn dead code)
        lc = run_self_fix_loop(["RETURN-FOR-FIX", "PASS"])
        self.assertEqual(lc.stage, "released")
        self.assertEqual(lc.retries, 1)
        self.assertIn("returned_for_fix", lc.history)

    def test_exceed_retries_blocks(self):
        # Quá MAX_RETRIES vòng RETURN liên tiếp → blocked (leo thang bác sĩ)
        lc = run_self_fix_loop(["RETURN-FOR-FIX"] * (MAX_RETRIES + 1))
        self.assertEqual(lc.stage, "blocked")
        self.assertEqual(lc.exit_code(), 3)
        self.assertGreater(lc.retries, MAX_RETRIES)

    def test_auto_fail_uses_fail_path(self):
        lc = Lifecycle()
        lc.to("routed"); lc.to("planned"); lc.to("running")
        stage = apply_verdict(lc, "AUTO-FAIL")
        self.assertEqual(stage, "returned_for_fix")  # vòng 1 vẫn còn lượt
        self.assertEqual(lc.retries, 1)

    def test_unknown_verdict_blocks(self):
        lc = Lifecycle()
        self.assertEqual(apply_verdict(lc, "???"), "blocked")


if __name__ == "__main__":
    unittest.main(verbosity=2)
