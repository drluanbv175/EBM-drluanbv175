#!/usr/bin/env python3
"""Sinh báo cáo readiness cho clinical runtime/chronic-care.

Báo cáo này không tự gỡ blocker production. Mục tiêu là chuẩn hóa một nơi
đọc được: blocker nào đã có tài liệu/artefact hỗ trợ, blocker nào vẫn cần
phê duyệt thật của bác sĩ, pháp lý, bảo mật hoặc cơ sở triển khai.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT / "medical-ebm-automation"
OS_DIR = REPO / "chronic-care-clinic-os"
REPORTS = ROOT / "reports"
OUT = REPORTS / "clinical_runtime_readiness_latest.md"

SOURCE_DOCS = [
    OS_DIR / "PRODUCTION_BLOCKERS.md",
    REPO / "docs" / "chronic-care" / "PHASE_3A_PRODUCTION_BLOCKERS.md",
]

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
    "dpia",
    "penetration test",
    "uat",
    "user acceptance",
    "cơ sở thật",
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


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def _collect_bullets(path: Path) -> list[str]:
    bullets: list[str] = []
    for raw in _read(path).splitlines():
        line = raw.strip()
        if line.startswith("- "):
            bullets.append(line[2:].strip())
        elif line.startswith("* "):
            bullets.append(line[2:].strip())
        elif line.startswith("- [ ]"):
            bullets.append(line[5:].strip())
    return bullets


def _bucket(blocker: str) -> str:
    text = blocker.lower()
    if any(token in text for token in ("rbac", "auth", "password", "csrf", "headers", "rate", "dependency", "vulnerability", "phi")):
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


def main() -> int:
    REPORTS.mkdir(exist_ok=True)

    missing_sources = [path for path in SOURCE_DOCS if not path.exists()]
    blockers: list[tuple[str, str, str]] = []
    for source in SOURCE_DOCS:
        for blocker in _collect_bullets(source):
            blockers.append((_rel(source), _bucket(blocker), blocker))

    by_bucket: dict[str, list[tuple[str, str]]] = {}
    for source, bucket, blocker in blockers:
        by_bucket.setdefault(bucket, []).append((source, blocker))

    human = [(source, blocker) for source, _, blocker in blockers if _needs_human_approval(blocker)]
    repo_actionable = [(source, blocker) for source, _, blocker in blockers if not _needs_human_approval(blocker)]

    lines: list[str] = []
    lines.append("# Clinical Runtime Readiness Report")
    lines.append("")
    lines.append(f"- Ngày sinh báo cáo: {date.today().isoformat()}")
    lines.append(f"- Tổng blocker mở: {len(blockers)}")
    lines.append(f"- Có thể chuẩn hóa thêm trong repo: {len(repo_actionable)}")
    lines.append(f"- Cần phê duyệt/triển khai thật: {len(human)}")
    lines.append("- Trạng thái production: BLOCKED_FOR_PRODUCTION cho đến khi bác sĩ/pháp lý/bảo mật/cơ sở duyệt thật.")
    lines.append("- AI clinical runtime: phải giữ disabled khi còn blocker.")
    lines.append("")

    if missing_sources:
        lines.append("## Nguồn blocker bị thiếu")
        lines.extend(f"- {_rel(path)}" for path in missing_sources)
        lines.append("")

    lines.append("## Artefact hỗ trợ hiện có")
    for bucket, paths in SUPPORTING_ARTEFACTS.items():
        present = [path for path in paths if path.exists()]
        missing = [path for path in paths if not path.exists()]
        lines.append(f"### {bucket}")
        lines.extend(f"- Có: `{_rel(path)}`" for path in present)
        if missing:
            lines.extend(f"- Thiếu: `{_rel(path)}`" for path in missing)
        lines.append("")

    lines.append("## Blocker theo nhóm")
    for bucket in ("security", "data_protection", "clinical_safety", "operations", "governance"):
        rows = by_bucket.get(bucket, [])
        lines.append(f"### {bucket} ({len(rows)})")
        if not rows:
            lines.append("- Không có blocker đang mở trong nhóm này.")
        for source, blocker in rows:
            gate = "CẦN DUYỆT/THỬ NGHIỆM THẬT" if _needs_human_approval(blocker) else "CÓ THỂ XỬ LÝ TRONG REPO"
            lines.append(f"- [{gate}] {blocker} _(nguồn: `{source}`)_")
        lines.append("")

    lines.append("## Kết luận vận hành")
    lines.append("- Hệ dashboard/chứng cứ/agent có thể đạt PASS ở mức trợ lý EBM có bác sĩ duyệt.")
    lines.append("- Clinical runtime/chronic-care chưa được nâng lên production chỉ bằng một lệnh tự động.")
    lines.append("- Khi các mục cần duyệt thật đã có chữ ký/biên bản/triển khai, mới được sửa tài liệu blocker và chạy audit lại.")
    lines.append("")
    lines.append("Cần bác sĩ kiểm chứng.")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Clinical runtime readiness report: {_rel(OUT)}")
    print(f"- blockers: {len(blockers)}")
    print(f"- repo_actionable: {len(repo_actionable)}")
    print(f"- requires_human_approval: {len(human)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
