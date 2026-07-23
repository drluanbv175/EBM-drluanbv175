#!/usr/bin/env python3
"""Hồi quy MEDIUM (vòng lặp kiểm tra-hoàn thiện vòng 10, 2026-07-22, workflow
wf_8e7ca8c0-968): observability/APPRAISAL_REPEATS.json có 2 bản _bump_repeats()
độc lập (tools/eval/run_eval.py và tools/orchestrator/guardrail_bridge.py) đọc-
sửa-ghi TOÀN BỘ file không khóa — gọi gần như đồng thời có thể mất cập nhật
(lost update). Test này gọi CẢ HAI hàm từ nhiều luồng đồng thời trên cùng 1 file
tạm và xác nhận không mất bản ghi nào.

Chạy: python tools/orchestrator/tests/test_appraisal_repeats_concurrency.py
"""
from __future__ import annotations

import json
import sys
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # tools/
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "eval"))  # tools/eval/

import run_eval as RE  # noqa: E402
from orchestrator import guardrail_bridge as GB  # noqa: E402


class TestAppraisalRepeatsConcurrency(unittest.TestCase):
    def setUp(self):
        self._orig_re_path = RE.APPRAISAL_REPEATS
        self._orig_gb_path = GB.APPRAISAL_REPEATS
        self.tmp_path = Path(self._orig_re_path).parent / "TEST_APPRAISAL_REPEATS_concurrency.json"
        if self.tmp_path.exists():
            self.tmp_path.unlink()
        RE.APPRAISAL_REPEATS = self.tmp_path
        GB.APPRAISAL_REPEATS = self.tmp_path

    def tearDown(self):
        RE.APPRAISAL_REPEATS = self._orig_re_path
        GB.APPRAISAL_REPEATS = self._orig_gb_path
        for suffix in (".json", ".json.tmp", ".json.lock"):
            p = self.tmp_path.with_suffix(suffix)
            if p.exists():
                p.unlink()

    def test_concurrent_bumps_from_both_modules_lose_nothing(self):
        n_threads = 20
        distinct_hashes = [f"hash{i:04d}aa" for i in range(n_threads)]
        errors = []

        def worker(i):
            try:
                if i % 2 == 0:
                    RE._bump_repeats(["R1"], distinct_hashes[i])
                else:
                    GB._bump_repeats(["R1"], distinct_hashes[i])
            except Exception as exc:  # noqa: BLE001
                errors.append(exc)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(errors, [])
        data = json.loads(self.tmp_path.read_text(encoding="utf-8"))
        recorded = set(data.get("R1", []))
        missing = set(distinct_hashes) - recorded
        self.assertEqual(
            missing, set(),
            f"Mất cập nhật (lost update): {len(missing)}/{n_threads} hash không được ghi nhận — "
            "TOCTOU race giữa 2 module _bump_repeats() chưa được khóa đúng."
        )


if __name__ == "__main__":
    unittest.main()
