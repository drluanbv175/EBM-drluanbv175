from __future__ import annotations

import re
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
    assert "Rubric QA ↔ LESSONS taxonomy" in domains
    assert any("verify_claude_code_repo_alignment.py" in cmd for cmd in commands)
    assert any("verify_clinical_runtime_schema_hardening.py" in cmd for cmd in commands)
    assert any("verify_lessons_rubric_alignment.py" in cmd for cmd in commands)


def test_core_checks_include_controlled_automation_cycle():
    commands = [" ".join(check.command) for check in E.CORE_CHECKS]
    domains = {check.domain for check in E.CORE_CHECKS}

    assert "Chu trình tự động có kiểm soát" in domains
    assert any("run_controlled_automation_cycle.py" in cmd for cmd in commands)


def test_core_checks_include_clinical_evidence_update_pipeline():
    commands = [" ".join(check.command) for check in E.CORE_CHECKS]
    domains = {check.domain for check in E.CORE_CHECKS}

    assert "Cập nhật chứng cứ lâm sàng" in domains
    assert any("verify_clinical_evidence_update_pipeline.py" in cmd for cmd in commands)


def test_core_checks_include_blocking_repo_lint():
    lint_checks = [check for check in E.CORE_CHECKS if check.domain == "Lint repo sống"]

    assert len(lint_checks) == 1
    lint = lint_checks[0]
    assert lint.command == ["-m", "ruff", "check", "."]
    assert Path(lint.cwd).resolve() == E.REPO.resolve()
    assert lint.blocking is True


def test_upgrade_verify_wires_blocking_repo_lint():
    """Bước 27 (lint medical-ebm-automation) phải còn BLOCKING (`True`).

    VÁ 07/09/2026: trước đây kiểm bằng SO KHỚP CHUỖI đúng nguyên văn dòng args,
    kể cả chuỗi "medical-ebm-automation" hardcode — nhưng chuỗi đó đã đổi thành
    biểu thức `str(_MEA_GOC_UV)` (đường dẫn TUYỆT ĐỐI qua duong_goc(), vì
    "medical-ebm-automation" tương đối chỉ đúng khi repo LỒNG trong ROOT — sai
    trên phiên cloud, xem tools/ban_sao_tran.py). Kiểm lại bằng regex khớp
    CẤU TRÚC dòng (nhãn · lệnh ruff check · biến đường dẫn đã resolve · blocking
    True) thay vì đúng-nguyên-văn chuỗi thư mục.
    """
    upgrade = (E.ROOT / "tools" / "upgrade_verify.py").read_text(encoding="utf-8")

    match = re.search(
        r'\("27\. Lint repo sống",\s*\["-m",\s*"ruff",\s*"check",\s*(\S+)\],\s*(True|False)\)',
        upgrade,
    )
    assert match, "Không tìm thấy dòng bước 27 (lint medical-ebm-automation) trong upgrade_verify.py"
    path_expr, blocking = match.group(1), match.group(2)
    assert blocking == "True"
    assert "MEA_GOC" in path_expr, (
        "Đường dẫn bước 27 phải qua biến resolve động (duong_goc()), "
        "không hardcode chuỗi tương đối 'medical-ebm-automation'."
    )


def test_full_pytest_uses_project_python(monkeypatch):
    seen: list[tuple[str, list[str], str]] = []

    def fake_run_check(check: E.EvidenceCheck, *, python: str) -> E.EvidenceRow:
        seen.append((check.domain, check.command, python))
        return E.EvidenceRow(
            domain=check.domain,
            command=" ".join(check.command),
            status="PASS",
            returncode=0,
            evidence_tail="ok",
            proves=check.proves,
            limitation=check.limitation,
            blocking=check.blocking,
        )

    monkeypatch.setattr(E, "_project_python", lambda: "/tmp/ebm-venv/bin/python")
    monkeypatch.setattr(E, "run_check", fake_run_check)

    report = E.build_report(include_full_pytest=True)

    assert report["overall_status"] == "PASS"
    full_pytest = [
        command
        for domain, command, python in seen
        if domain == "Full test repo sống" and python == "/tmp/ebm-venv/bin/python"
    ]
    assert full_pytest
    assert full_pytest[0][:2] == ["-m", "pytest"]
    assert full_pytest[0][2].startswith("--basetemp=")
    assert "OneDrive" not in full_pytest[0][2]
    assert all(python == "/tmp/ebm-venv/bin/python" for _, _, python in seen)


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
