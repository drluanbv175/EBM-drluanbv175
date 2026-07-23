#!/usr/bin/env python3
"""Hồi quy HIGH (vòng lặp kiểm tra-hoàn thiện vòng 10, 2026-07-22, workflow
wf_8e7ca8c0-968): guardrail_bridge._safe_target() dùng bản khử PII tên file YẾU
HƠN bản gốc run_eval.py::_safe_target() — trước bản vá, số điện thoại/định danh
viết CÓ dấu phân cách (vd "0912-345-678") không bị khử, lọt vào
observability/APPRAISALS.jsonl (log bền, append-only).

Chạy: python tools/orchestrator/tests/test_guardrail_bridge_safe_target.py
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # tools/

from orchestrator.guardrail_bridge import _safe_target  # noqa: E402


class TestSafeTargetPhoneLikeSeparators(unittest.TestCase):
    def test_hyphen_separated_digits_are_redacted(self):
        display, _ = _safe_target("0912-345-678_review.md")
        self.assertTrue(display.startswith("redacted-"), display)
        self.assertTrue(display.endswith(".md"))

    def test_dot_separated_digits_are_redacted(self):
        display, _ = _safe_target("0912.345.678_review.md")
        self.assertTrue(display.startswith("redacted-"), display)

    def test_underscore_separated_digits_are_redacted(self):
        display, _ = _safe_target("0912_345_678_review.md")
        self.assertTrue(display.startswith("redacted-"), display)

    def test_unseparated_long_digit_run_still_redacted(self):
        # Không hồi quy ngược: trường hợp đơn giản (không có dấu phân cách) vốn đã đúng.
        display, _ = _safe_target("0912345678_review.md")
        self.assertTrue(display.startswith("redacted-"), display)

    def test_benign_short_filename_not_redacted(self):
        display, _ = _safe_target("guideline_v2.md")
        self.assertEqual(display, "guideline_v2.md")


if __name__ == "__main__":
    unittest.main()
