from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_research_practical_readiness as V  # noqa: E402


def test_practical_readiness_verifier_runs_end_to_end():
    summary = V.run_verification()

    assert summary["status"] == "PASS"
    assert summary["uses_synthetic_data"] is True
    assert summary["deidentification"]["raw_intake_status"] == "BLOCKED_PII_OR_UNSAFE"
    assert summary["deidentification"]["then_import_status"] == "READY_FOR_CLEANING_NOT_LOCKED"
    assert summary["pseudonymization_to_g6"]["locked_status"] == "LOCKED_FOR_ANALYSIS"
    assert summary["pseudonymization_to_g6"]["g6_status"] == "LOCKED_REAL_SIGNAL"
    assert summary["pseudonymization_to_g6"]["g6_can_release"] is True
