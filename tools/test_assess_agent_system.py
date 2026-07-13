from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import assess_agent_system as A  # noqa: E402


def test_p_contains_all_pass_and_failure_details():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "probe.py"
        path.write_text("alpha\nbeta\n", encoding="utf-8")

        ok, detail = A.p_contains_all(path, ["alpha", "beta"], "marker probe")
        assert ok is True
        assert "2/2 marker" in detail

        ok, detail = A.p_contains_all(path, ["alpha", "gamma"], "marker probe")
        assert ok is False
        assert "1/2 marker" in detail
        assert "gamma" in detail


def test_scorecard_checks_research_gate_contract_surface():
    criteria = A.build_criteria(deep=False, py=sys.executable)
    by_id = {item["id"]: item for item in criteria}

    s3_results = [probe() for probe in by_id["S3"]["probes"]]
    s5_results = [probe() for probe in by_id["S5"]["probes"]]
    a6_results = [probe() for probe in by_id["A6"]["probes"]]
    a7_results = [probe() for probe in by_id["A7"]["probes"]]

    assert any(ok and "Hợp đồng phát hành từng cổng nghiên cứu" in detail
               for ok, detail in s3_results)
    assert any(ok and "Pipeline dữ liệu thật synthetic đi tới audit G6" in detail
               for ok, detail in s3_results)
    assert any(ok and "Cổng nghiên cứu chặn downstream" in detail
               for ok, detail in s5_results)
    assert any(ok and "Verifier thực tiễn dữ liệu nghiên cứu" in detail
               for ok, detail in s5_results)
    assert any(ok and "Bảng chứng cứ thực tiễn có thể sinh lại" in detail
               for ok, detail in s5_results)
    assert any(ok and "Audit cổng sinh action queue + resume contract" in detail
               for ok, detail in a6_results)
    assert any(ok and "Verifier thực tiễn dữ liệu nghiên cứu" in detail
               for ok, detail in a7_results)
