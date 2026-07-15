from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_research_readiness_evidence as E  # noqa: E402


def test_markdown_report_contains_honest_evidence_table():
    report = {
        "kind": "research_readiness_evidence_report",
        "generated_at": "2026-07-13T12:00:00",
        "overall_status": "PASS",
        "blocking_failure_count": 0,
        "rows": [
            {
                "domain": "Luồng dữ liệu nghiên cứu thực tiễn",
                "command": "python tools/verify_research_practical_readiness.py",
                "status": "PASS",
                "returncode": 0,
                "evidence_tail": "KẾT: PASS",
                "proves": "Synthetic real-data path reaches G6.",
                "limitation": "Dữ liệu thật vẫn cần PI xác nhận.",
                "blocking": True,
            }
        ],
        "disclaimer": "Cần bác sĩ kiểm chứng.",
    }

    md = E.markdown_report(report)

    assert "Bảng chứng cứ sẵn sàng thực tiễn" in md
    assert "Luồng dữ liệu nghiên cứu thực tiễn" in md
    assert "Dữ liệu thật vẫn cần PI xác nhận" in md
    assert "Cần bác sĩ kiểm chứng" in md


def test_core_checks_include_controlled_research_automation():
    commands = [" ".join(check.command) for check in E.CORE_CHECKS]

    assert any("verify_controlled_research_automation.py" in cmd for cmd in commands)


def test_core_checks_include_repo_alignment_and_clinical_hardening():
    commands = [" ".join(check.command) for check in E.CORE_CHECKS]
    domains = {check.domain for check in E.CORE_CHECKS}

    assert "Repo/Claude Code/Codex alignment" in domains
    assert "Clinical runtime schema hardening" in domains
    assert any("verify_claude_code_repo_alignment.py" in cmd for cmd in commands)
    assert any("verify_clinical_runtime_schema_hardening.py" in cmd for cmd in commands)


def test_write_report_writes_markdown_and_json():
    report = {
        "kind": "research_readiness_evidence_report",
        "generated_at": "2026-07-13T12:00:00",
        "overall_status": "PASS",
        "blocking_failure_count": 0,
        "rows": [],
        "disclaimer": "Cần bác sĩ kiểm chứng.",
    }
    with tempfile.TemporaryDirectory() as tmp:
        out_md = Path(tmp) / "evidence.md"
        out_json = Path(tmp) / "evidence.json"
        E.write_report(report, out_md=out_md, out_json=out_json)

        assert out_md.exists()
        assert out_json.exists()
        assert "Overall status: `PASS`" in out_md.read_text(encoding="utf-8")
        assert '"overall_status": "PASS"' in out_json.read_text(encoding="utf-8")
