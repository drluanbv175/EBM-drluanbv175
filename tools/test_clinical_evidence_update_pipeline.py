from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_clinical_evidence_update_pipeline as V  # noqa: E402


def test_synthetic_dashboard_fixture_has_disclaimer_doi_and_no_pii():
    with tempfile.TemporaryDirectory() as tmp:
        dash = V.write_synthetic_dashboard(Path(tmp), updated="2026-07-15")
        html = dash.read_text(encoding="utf-8")
        ok, detail = V._check_no_pii(html)

        assert V.DISCLAIMER in html
        assert V.FIXTURE_DOI in html
        assert "standards" in html
        assert "--strict-sources" in html
        assert "CONSORT, STROBE, PRISMA, STARD, TRIPOD" in html
        assert "AGREE II, AMSTAR 2, RoB 2, ROBINS-I, QUADAS-2, PROBAST" in html
        assert ok is True, detail


def test_clinical_evidence_update_pipeline_passes_offline():
    report = V.run_verification(online_dashboard_gate=False)
    domains = {row["name"]: row["status"] for row in report["rows"]}

    assert report["overall_status"] == "PASS"
    assert domains["Dashboard integrity gate"] == "PASS"
    assert domains["Evidence Workbench template contract"] == "PASS"
    assert domains["Library accumulation"] == "PASS"
    assert domains["Derivative artifacts"] == "PASS"
    assert "Cần bác sĩ kiểm chứng" in report["disclaimer"]
