#!/usr/bin/env python3
"""Generate an honest readiness report for clinical runtime/chronic-care.

The report can unlock repository-control progress, but it never clears clinical
production. Real patient use still requires human evidence, UAT, security/legal
review, clinical signoff, approval record, and go-live attestation.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT / "medical-ebm-automation"
OS_DIR = REPO / "chronic-care-clinic-os"
REPORTS = ROOT / "reports"
OUT = REPORTS / "clinical_runtime_readiness_latest.md"
OUT_JSON = REPORTS / "clinical_runtime_readiness_latest.json"

SOURCE_DOCS = [
    OS_DIR / "PRODUCTION_BLOCKERS.md",
    REPO / "docs" / "chronic-care" / "PHASE_3A_PRODUCTION_BLOCKERS.md",
]

RUNTIME_HARDENING_TS = OS_DIR / "lib" / "runtime-hardening.ts"

SUPPORTING_ARTEFACTS = {
    "security": [
        OS_DIR / "SECURITY.md",
        OS_DIR / "security" / "THREAT_MODEL.md",
        OS_DIR / "security" / "SECURITY_TEST_CASES.md",
        OS_DIR / "ROLE_MATRIX.md",
    ],
    "data_protection": [
        OS_DIR / "DATA_GOVERNANCE.md",
        OS_DIR / "DATA_PROTECTION_SIGNOFF_TEMPLATE.md",
        OS_DIR / "DATABASE_SCHEMA.md",
    ],
    "clinical_safety": [
        OS_DIR / "CLINICAL_SAFETY.md",
        OS_DIR / "CLINICAL_SAFETY_SIGNOFF_TEMPLATE.md",
        OS_DIR / "TEST_PLAN.md",
        OS_DIR / "MVP_01_ACCEPTANCE_TEST.md",
    ],
    "operations": [
        OS_DIR / "OPERATIONS_MANUAL.md",
        OS_DIR / "DEPLOYMENT.md",
        OS_DIR / "security" / "INCIDENT_RESPONSE_PLAYBOOK.md",
        OS_DIR / "docker-compose.yml",
        OS_DIR / "Dockerfile",
    ],
    "governance": [
        OS_DIR / "RISK_REGISTER.md",
        OS_DIR / "IMPLEMENTATION_STATUS.md",
        OS_DIR / "PROJECT_PLAN.md",
    ],
}

HUMAN_APPROVAL_TERMS = (
    "signoff",
    "sign-off",
    "approval",
    "approved",
    "assessment pháp lý",
    "assessment phap ly",
    "dpia",
    "penetration test",
    "uat",
    "user acceptance",
    "cơ sở thật",
    "co so that",
    "real operational users",
    "training",
    "competency",
    "production",
    "real patient",
    "ai must remain disabled",
    "privacy controls",
    "human review",
    "clinical rules are draft",
    "clinical safety",
    "emr/his",
)

STATUS_REPO_CONTROL_READY = "REPO_CONTROL_READY_HUMAN_GATED"
STATUS_REPO_ACTIONABLE = "REPO_ACTIONABLE"
STATUS_HUMAN_REQUIRED = "HUMAN_APPROVAL_REQUIRED"


@dataclass(frozen=True)
class UnlockRule:
    blocker_id: str
    control_id: str
    match_text: str
    unlock_note: str


@dataclass(frozen=True)
class RuntimeControl:
    control_id: str
    blocker_ids: list[str]
    files: list[str]
    residual_gate: str


@dataclass(frozen=True)
class BlockerRow:
    source: str
    bucket: str
    blocker: str
    status: str
    requires_human_approval: bool
    blocker_id: str | None = None
    control_id: str | None = None
    control_files: list[str] | None = None
    residual_gate: str | None = None
    unlock_note: str | None = None


# Tranche 2026-07-25: unlock blockers at repository-control level only.
# These are not production clearances; each row still keeps its residual human gate.
REPO_CONTROL_UNLOCK_RULES: tuple[UnlockRule, ...] = (
    UnlockRule(
        "SEC-001",
        "RUNTIME-RBAC-COVERAGE-001",
        "backend rbac route/action coverage contract added",
        "Route/action RBAC coverage contract is machine-readable in repo.",
    ),
    UnlockRule(
        "SEC-003",
        "RUNTIME-PASSWORD-001",
        "password hashing contract added",
        "Password hashing contract and test coverage exist in repo.",
    ),
    UnlockRule(
        "SEC-004",
        "RUNTIME-WRITE-GUARD-001",
        "rate limiting and csrf contract added",
        "Write guard requires authenticated actor, CSRF and rate-limit evidence.",
    ),
    UnlockRule(
        "SEC-005",
        "RUNTIME-HEADERS-001",
        "secure headers are configured in repo",
        "Secure-header policy is exposed by runtime hardening controls.",
    ),
    UnlockRule(
        "SEC-006",
        "RUNTIME-ENV-001",
        "environment validation contract added",
        "Production environment gate is modeled and tested.",
    ),
    UnlockRule(
        "SEC-007",
        "RUNTIME-DEPENDENCY-SCAN-001",
        "dependency lockfile and scan evidence contract exist",
        "Dependency scan evidence schema requires exact lockfile hash.",
    ),
    UnlockRule(
        "SEC-008",
        "RUNTIME-PHI-LOG-001",
        "phi redaction logger contract added",
        "Audit persistence sanitizer redacts PHI/PII before storage.",
    ),
    UnlockRule(
        "DATA-002",
        "RUNTIME-BACKUP-RESTORE-001",
        "backup/restore evidence validator added",
        "Backup/restore evidence validator is present.",
    ),
    UnlockRule(
        "DATA-001",
        "RUNTIME-SITE-ISOLATION-001",
        "organization/site isolation contract and denial tests exist",
        "Organization/site isolation contract denies cross-organization and cross-site access.",
    ),
    UnlockRule(
        "DATA-003",
        "RUNTIME-GOVERNANCE-PERSISTENCE-001",
        "audit log persistence contract and migration hardening are modeled",
        "Governance persistence evidence requires audit linkage and append-only verification.",
    ),
    UnlockRule(
        "DATA-004",
        "RUNTIME-RETENTION-001",
        "data retention/archive policy contract added",
        "Retention/archive policy contract is present.",
    ),
    UnlockRule(
        "CLIN-002",
        "RUNTIME-OUTPATIENT-AUTOMATION-001",
        "rule approval workflow and outpatient automation control contract exist",
        "Outpatient automation control blocks unsafe, expired or patient-facing rules without approval.",
    ),
    UnlockRule(
        "CLIN-003",
        "RUNTIME-OUTPATIENT-AUTOMATION-001",
        "clinical content and patient education approval not fully executable",
        "Outpatient automation and patient communication controls keep patient-facing content human-gated.",
    ),
    UnlockRule(
        "CLIN-004",
        "RUNTIME-A5-QA-001",
        "a5 output qa contract added",
        "A5 rendered-output QA contract checks format, checksum, disclaimer and emergency boundary.",
    ),
    UnlockRule(
        "OPS-001",
        "RUNTIME-DOCKER-SMOKE-001",
        "docker one-command run evidence contract exists",
        "Docker smoke evidence contract checks app/db health and secret redaction.",
    ),
    UnlockRule(
        "OPS-002",
        "RUNTIME-PRISMA-MIGRATION-001",
        "prisma migration review contract exists",
        "Prisma migration review contract checks SQL hash, smoke test and rollback evidence.",
    ),
    UnlockRule(
        "OPS-003",
        "RUNTIME-MONITORING-001",
        "error logging and monitoring evidence validator added",
        "Monitoring smoke evidence covers error capture, audit-failure alerts, red flags and on-call route.",
    ),
    UnlockRule(
        "OPS-004",
        "RUNTIME-INCIDENT-DRILL-001",
        "incident response process documented and drill validator added",
        "Incident drill evidence requires physician, data protection and operations coverage.",
    ),
    UnlockRule(
        "PHASE3A-PATIENT-COMMUNICATION-POLICY",
        "RUNTIME-PATIENT-COMM-001",
        "clinic-approved patient communication policy/signoff; repo contract",
        "Patient communication policy gate blocks messages without template, consent and physician approval.",
    ),
    UnlockRule(
        "PHASE3A-LIVE-GOVERNANCE-PERSISTENCE",
        "RUNTIME-GOVERNANCE-PERSISTENCE-001",
        "live governance persistence sign-off; repo contract",
        "Governance persistence contract requires live governance tables, backup and append-only audit evidence.",
    ),
    UnlockRule(
        "AI-001",
        "RUNTIME-AI-DRAFTS-GATE-001",
        "ai must remain disabled until mvp-01 is stable",
        "AI draft circuit breaker blocks future LLM call sites unless the flag is explicitly enabled after signoff.",
    ),
)


def configure_utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def _collect_bullets(path: Path) -> list[str]:
    bullets: list[str] = []
    for raw in _read(path).splitlines():
        line = raw.strip()
        if line.startswith("- [ ]"):
            bullets.append(line[5:].strip())
        elif line.startswith("- "):
            bullets.append(line[2:].strip())
        elif line.startswith("* "):
            bullets.append(line[2:].strip())
    return bullets


def _bucket(blocker: str) -> str:
    text = blocker.lower()
    if any(
        token in text
        for token in (
            "rbac",
            "auth",
            "password",
            "csrf",
            "headers",
            "environment",
            "rate",
            "dependency",
            "vulnerability",
            "penetration",
            "phi",
            "mfa",
        )
    ):
        return "security"
    if any(token in text for token in ("data", "retention", "backup", "audit log", "site isolation", "dpia")):
        return "data_protection"
    if any(token in text for token in ("clinical", "rule", "patient education", "red flag", "a5", "knowledge pack")):
        return "clinical_safety"
    if any(token in text for token in ("docker", "prisma", "logging", "monitoring", "incident", "infrastructure", "migration")):
        return "operations"
    if any(token in text for token in ("approval", "governance", "legal", "policy", "training", "workflow", "emr", "his")):
        return "governance"
    return "governance"


def _needs_human_approval(blocker: str) -> bool:
    text = blocker.lower()
    return any(term in text for term in HUMAN_APPROVAL_TERMS)


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _runtime_control_index(path: Path = RUNTIME_HARDENING_TS) -> dict[str, RuntimeControl]:
    text = _read(path)
    controls: dict[str, RuntimeControl] = {}
    for match in re.finditer(r"\{\s*controlId:\s*\"([^\"]+)\"(?P<body>.*?)\n\s*\}", text, re.DOTALL):
        control_id = match.group(1)
        body = match.group("body")
        blocker_ids = re.findall(r"blockerIds:\s*\[(.*?)\]", body, re.DOTALL)
        ids = re.findall(r"\"([^\"]+)\"", blocker_ids[0]) if blocker_ids else []
        file_chunks = re.findall(r"files:\s*\[(.*?)\]", body, re.DOTALL)
        files = re.findall(r"\"([^\"]+)\"", file_chunks[0]) if file_chunks else []
        residual_match = re.search(r"residualGate:\s*\"([^\"]+)\"", body)
        controls[control_id] = RuntimeControl(
            control_id=control_id,
            blocker_ids=ids,
            files=files,
            residual_gate=residual_match.group(1) if residual_match else "",
        )
    return controls


def _match_unlock_rule(blocker: str) -> UnlockRule | None:
    text = blocker.lower()
    for rule in REPO_CONTROL_UNLOCK_RULES:
        if rule.match_text in text:
            return rule
    return None


def _classify_blocker(
    source: Path,
    blocker: str,
    controls: dict[str, RuntimeControl],
) -> BlockerRow:
    requires_human = _needs_human_approval(blocker)
    rule = _match_unlock_rule(blocker)
    if rule:
        control = controls.get(rule.control_id)
        if control and rule.blocker_id in control.blocker_ids:
            return BlockerRow(
                source=_rel(source),
                bucket=_bucket(blocker),
                blocker=blocker,
                status=STATUS_REPO_CONTROL_READY,
                requires_human_approval=True,
                blocker_id=rule.blocker_id,
                control_id=rule.control_id,
                control_files=control.files,
                residual_gate=control.residual_gate,
                unlock_note=rule.unlock_note,
            )
        return BlockerRow(
            source=_rel(source),
            bucket=_bucket(blocker),
            blocker=blocker,
            status=STATUS_REPO_ACTIONABLE,
            requires_human_approval=requires_human,
            blocker_id=rule.blocker_id,
            control_id=rule.control_id,
            unlock_note=f"Rule matched, but repository control {rule.control_id} is missing or not linked.",
        )
    return BlockerRow(
        source=_rel(source),
        bucket=_bucket(blocker),
        blocker=blocker,
        status=STATUS_HUMAN_REQUIRED if requires_human else STATUS_REPO_ACTIONABLE,
        requires_human_approval=requires_human,
    )


def build_report() -> dict[str, Any]:
    missing_sources = [path for path in SOURCE_DOCS if not path.exists()]
    controls = _runtime_control_index()
    rows: list[BlockerRow] = []
    for source in SOURCE_DOCS:
        for blocker in _collect_bullets(source):
            rows.append(_classify_blocker(source, blocker, controls))

    by_bucket: dict[str, list[BlockerRow]] = {}
    for row in rows:
        by_bucket.setdefault(row.bucket, []).append(row)

    repo_control_ready = [row for row in rows if row.status == STATUS_REPO_CONTROL_READY]
    repo_actionable = [row for row in rows if row.status == STATUS_REPO_ACTIONABLE]
    human = [row for row in rows if row.requires_human_approval]
    expected_unlocked = len(REPO_CONTROL_UNLOCK_RULES)
    missing_expected = [
        rule.control_id
        for rule in REPO_CONTROL_UNLOCK_RULES
        if not any(row.control_id == rule.control_id and row.status == STATUS_REPO_CONTROL_READY for row in rows)
    ]

    return {
        "kind": "clinical_runtime_readiness_report",
        "generated_at": date.today().isoformat(),
        "summary": {
            "total_blockers": len(rows),
            "repo_control_ready_unlocked": len(repo_control_ready),
            "expected_repo_control_unlocks": expected_unlocked,
            "repo_actionable_without_control": len(repo_actionable),
            "requires_human_approval": len(human),
            "human_gate_remaining": len(human),
            "clinical_production_allowed": False,
            "ai_clinical_runtime_enabled": False,
            "status": "BLOCKED_FOR_PRODUCTION",
            "disclaimer": "Can bac si kiem chung.",
        },
        "missing_sources": [_rel(path) for path in missing_sources],
        "missing_expected_repository_controls": missing_expected,
        "supporting_artefacts": {
            bucket: {
                "present": [_rel(path) for path in paths if path.exists()],
                "missing": [_rel(path) for path in paths if not path.exists()],
            }
            for bucket, paths in SUPPORTING_ARTEFACTS.items()
        },
        "blockers_by_bucket": {
            bucket: [asdict(row) for row in by_bucket.get(bucket, [])]
            for bucket in ("security", "data_protection", "clinical_safety", "operations", "governance")
        },
        "repo_control_ready_blockers": [asdict(row) for row in repo_control_ready],
    }


def _status_label(row: dict[str, Any]) -> str:
    if row["status"] == STATUS_REPO_CONTROL_READY:
        return "REPO CONTROL READY; HUMAN EVIDENCE STILL REQUIRED"
    if row["status"] == STATUS_REPO_ACTIONABLE:
        return "CAN BE COMPLETED IN REPO"
    return "NEEDS REAL REVIEW/SIGNOFF"


def markdown_report(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines: list[str] = [
        "# Clinical Runtime Readiness Report",
        "",
        f"- Generated: `{report['generated_at']}`",
        f"- Total open blockers: `{summary['total_blockers']}`",
        (
            "- Repository-control unlocked: "
            f"`{summary['repo_control_ready_unlocked']}/{summary['total_blockers']}` "
            "(human-gated; not production clearance)"
        ),
        f"- Repo-actionable without control: `{summary['repo_actionable_without_control']}`",
        f"- Requires human approval/deployment evidence: `{summary['requires_human_approval']}`",
        f"- Clinical production allowed: `{summary['clinical_production_allowed']}`",
        f"- AI clinical runtime enabled: `{summary['ai_clinical_runtime_enabled']}`",
        f"- Status: `{summary['status']}`",
        "- Safety rule: unlocked repository controls reduce technical uncertainty only; every unlocked row still needs real evidence/signoff.",
        "",
    ]

    if report["missing_sources"]:
        lines.append("## Missing Blocker Sources")
        lines.extend(f"- `{path}`" for path in report["missing_sources"])
        lines.append("")

    if report["missing_expected_repository_controls"]:
        lines.append("## Missing Expected Repository Controls")
        lines.extend(f"- `{control}`" for control in report["missing_expected_repository_controls"])
        lines.append("")

    lines.append("## Supporting Artefacts")
    for bucket, artefacts in report["supporting_artefacts"].items():
        lines.append(f"### {bucket}")
        lines.extend(f"- Present: `{path}`" for path in artefacts["present"])
        if artefacts["missing"]:
            lines.extend(f"- Missing: `{path}`" for path in artefacts["missing"])
        lines.append("")

    lines.append(
        "## Repository-Control Unlocked Blockers "
        f"({summary['repo_control_ready_unlocked']}/{summary['total_blockers']})"
    )
    for row in report["repo_control_ready_blockers"]:
        files = ", ".join(f"`{item}`" for item in (row.get("control_files") or []))
        lines.append(
            f"- `{row['blocker_id']}` via `{row['control_id']}`: {row['unlock_note']} "
            f"Residual gate: {row['residual_gate']} Files: {files}"
        )
    lines.append("")

    lines.append("## Blockers By Group")
    for bucket, rows in report["blockers_by_bucket"].items():
        lines.append(f"### {bucket} ({len(rows)})")
        if not rows:
            lines.append("- No open blockers in this group.")
        for row in rows:
            gate = _status_label(row)
            suffix = ""
            if row.get("control_id"):
                suffix = f" [`{row['blocker_id']}` / `{row['control_id']}`]"
            lines.append(f"- [{gate}]{suffix} {row['blocker']} _(source: `{row['source']}`)_")
        lines.append("")

    lines.extend(
        [
            "## Operating Conclusion",
            "- The system may continue as an EBM assistant with physician review.",
            "- Clinical runtime/chronic-care is still blocked for production and real patient data.",
            "- Clear production only after signed evidence package, UAT, security/legal/clinical signoff, approval record and go-live attestation.",
            "",
            "Can bac si kiem chung.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_reports(report: dict[str, Any]) -> None:
    REPORTS.mkdir(exist_ok=True)
    OUT.write_text(markdown_report(report), encoding="utf-8")
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    configure_utf8_stdio()
    report = build_report()
    write_reports(report)
    summary = report["summary"]
    print(f"Clinical runtime readiness report: {_rel(OUT)}")
    print(f"- blockers: {summary['total_blockers']}")
    print(f"- repo_control_ready: {summary['repo_control_ready_unlocked']}/{summary['total_blockers']}")
    print(f"- repo_actionable: {summary['repo_actionable_without_control']}")
    print(f"- requires_human_approval: {summary['requires_human_approval']}")
    print(
        "summary: "
        f"repo_control_ready={summary['repo_control_ready_unlocked']}/{summary['total_blockers']}; "
        f"requires_human_approval={summary['requires_human_approval']}; "
        f"clinical_production_allowed={summary['clinical_production_allowed']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
