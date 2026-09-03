#!/usr/bin/env python3
"""Kiểm hợp đồng repo giữa Claude Code và Codex.

Mục tiêu là bắt sớm kiểu lệch doctrine đã từng xảy ra: Claude Code đọc
`CLAUDE.md`/`.claude/agents`, còn Codex đọc `AGENTS.md`/TOML mirror cũ hơn. Tool
này chỉ đọc file và git index; không tự sửa/sync.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

import check_claude_codex_sync_health as sync_health
import sync_agents_to_codex as sync


ROOT = Path(__file__).resolve().parents[1]

# Khi script nay chay tu hook pre-commit cua mot repo con long ben trong
# (vd medical-ebm-automation/.githooks/pre-commit goi ra day), git da set
# san GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE tro vao repo con trong bien moi
# truong cua tien trinh hook. Cac bien nay ghi de viec git tu do repo theo
# cwd, nen `git ls-files` ben duoi van doc index cua repo con du subprocess
# duoc goi voi cwd=ROOT cua repo ngoai -> bao thieu file oan (tools/upgrade_
# verify.py, clinical_runtime/... khong ton tai trong repo con). Phai xoa
# cac bien nay truoc khi goi git.
_GIT_DISCOVERY_ENV_VARS = (
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
)

ROOT_DOCS = {
    "AGENTS.md": ROOT / "AGENTS.md",
    "CLAUDE.md": ROOT / "CLAUDE.md",
}
MEDICAL_DOCS = {
    "medical-ebm-automation/AGENTS.md": ROOT / "medical-ebm-automation" / "AGENTS.md",
    "medical-ebm-automation/CLAUDE.md": ROOT / "medical-ebm-automation" / "CLAUDE.md",
}

ROOT_CONTRACT_MARKERS = [
    ".claude/agents",
    ".Codex/agents",
    ".codex/agents",
    "tools/enforce_agent_guardrails.py",
    "tools/sync_agents_to_codex.py",
    "tools/check_claude_codex_sync_health.py",
    "tools/upgrade_verify.py",
    "clinical_runtime/",
    "tools/verify_clinical_runtime_schema_hardening.py",
    "G8 bình duyệt độc lập",
    "Cần bác sĩ kiểm chứng",
]

MEDICAL_CONTRACT_MARKERS = {
    "medical-ebm-automation/AGENTS.md": [
        "Claude Code",
        "commit",
        "Do not commit secrets",
        "Plans.md",
    ],
    "medical-ebm-automation/CLAUDE.md": [
        "Claude Code",
        "commit",
        "python ../tools/sync_agents_to_codex.py --check",
        "python ../tools/audit_ebm_system.py",
        "pytest",
        "ruff check",
    ],
}

TRACKED_CONTRACT_FILES = [
    "AGENTS.md",
    "CLAUDE.md",
    "tools/upgrade_verify.py",
    "tools/check_claude_codex_sync_health.py",
    "tools/verify_clinical_runtime_schema_hardening.py",
    "clinical_runtime/README.md",
    "clinical_runtime/OUTPUT_SCHEMA.json",
    "clinical_runtime/SAFETY_RULES_SCHEMA.json",
    "clinical_runtime/CLINICAL_DECISION_CONTRACT.json",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _missing_markers(path: Path, markers: list[str]) -> list[str]:
    if not path.exists():
        return markers
    text = _read(path)
    return [marker for marker in markers if marker not in text]


def _git_ls_files() -> set[str]:
    env = {k: v for k, v in os.environ.items() if k not in _GIT_DISCOVERY_ENV_VARS}
    proc = subprocess.run(
        ["git", "ls-files"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        env=env,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "git ls-files failed")
    return {line.strip() for line in proc.stdout.splitlines() if line.strip()}


def check_root_docs() -> dict[str, Any]:
    missing: dict[str, list[str]] = {}
    for label, path in ROOT_DOCS.items():
        absent = _missing_markers(path, ROOT_CONTRACT_MARKERS)
        if absent:
            missing[label] = absent
    return {
        "name": "root_docs",
        "status": "PASS" if not missing else "FAIL",
        "missing_markers": missing,
    }


def ban_sao_tran() -> bool:
    """True CHỈ khi bản sao git trần — định nghĩa DUY NHẤT ở tools/ban_sao_tran.py.

    SỬA 28/08 vòng 4 (bình duyệt đối kháng bắt được): bản đầu chỉ kiểm MỘT gốc
    (medical-ebm-automation/) — trên máy thật còn EBM-Dashboards/EBM_MASTER mà
    thiếu riêng repo y khoa (sự cố OneDrive đã gặp), hook lặng lẽ PASS = fail-open.
    Nay đòi cả BA gốc vắng mặt, cùng ngữ nghĩa với bộ chốt bài học/conftest."""
    import importlib.util
    duong = Path(__file__).resolve().parent / "ban_sao_tran.py"
    spec = importlib.util.spec_from_file_location("_bst_alignment", duong)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.ban_sao_git_tran(ROOT)


def check_medical_docs(tran: bool | None = None) -> dict[str, Any]:
    tran = ban_sao_tran() if tran is None else tran
    if tran:
        return {
            "name": "medical_repo_docs",
            "status": "NGOAI-PHAM-VI",
            "missing_markers": {},
            "ghi_chu": ("bản sao git trần — medical-ebm-automation/ không có trên máy "
                        "này; phần đối chiếu chéo repo chạy trên máy có đủ hai repo"),
        }
    missing: dict[str, list[str]] = {}
    for label, path in MEDICAL_DOCS.items():
        absent = _missing_markers(path, MEDICAL_CONTRACT_MARKERS[label])
        if absent:
            missing[label] = absent
    return {
        "name": "medical_repo_docs",
        "status": "PASS" if not missing else "FAIL",
        "missing_markers": missing,
    }


def check_tracked_contract_files() -> dict[str, Any]:
    tracked = _git_ls_files()
    missing = [path for path in TRACKED_CONTRACT_FILES if path not in tracked]
    return {
        "name": "tracked_contract_files",
        "status": "PASS" if not missing else "FAIL",
        "missing_files": missing,
    }


def check_agent_sync_health() -> dict[str, Any]:
    report = sync_health.evaluate_sync_health()
    return {
        "name": "agent_sync_health",
        "status": report.status,
        "source_agents": report.source.agents,
        "target_count": len(report.targets),
        "errors": report.errors,
    }


def check_agent_files_git_tracked() -> dict[str, Any]:
    """Bắt lỗ hổng mà `check_agent_sync_health()`/`check_tracked_contract_files()`
    không canh: một file `.claude/agents/*.md` có mặt trên đĩa (nên
    `sync.source_agent_paths()` đếm được, `evaluate_sync_health()` PASS vì so
    sánh đĩa-với-đĩa — hoàn toàn không đụng tới git) nhưng đã bị `git rm
    --cached` khỏi git index. Một checkout mới/clone mới sẽ KHÔNG có file đó —
    mất trắng một agent — mà không cổng nào từng bắt được, vì
    `check_tracked_contract_files()` chỉ canh một danh sách nhỏ file hạ tầng
    CỐ ĐỊNH (AGENTS.md, CLAUDE.md, clinical_runtime/*...), không canh từng
    file agent riêng lẻ (số lượng thay đổi mỗi khi thêm/bớt agent)."""
    tracked = _git_ls_files()
    disk_paths = sync.source_agent_paths() + sync.source_infra_paths()
    untracked = sorted(
        p.relative_to(ROOT).as_posix()
        for p in disk_paths
        if p.relative_to(ROOT).as_posix() not in tracked
    )
    return {
        "name": "agent_files_git_tracked",
        "status": "PASS" if not untracked else "FAIL",
        "untracked_files": untracked,
    }


def check_upgrade_verify_wires_alignment() -> dict[str, Any]:
    path = ROOT / "tools" / "upgrade_verify.py"
    required = [
        "tools/verify_claude_code_repo_alignment.py",
        "Repo/Claude Code alignment",
        "tools/check_claude_codex_sync_health.py",
        "tools/verify_clinical_runtime_schema_hardening.py",
        '"-m", "ruff", "check", "medical-ebm-automation"',
        "Lint repo sống",
    ]
    missing = _missing_markers(path, required)
    return {
        "name": "upgrade_verify_wiring",
        "status": "PASS" if not missing else "FAIL",
        "missing_markers": missing,
    }


def run_verification() -> dict[str, Any]:
    checks = [
        check_root_docs(),
        check_medical_docs(),
        check_tracked_contract_files(),
        check_agent_sync_health(),
        check_agent_files_git_tracked(),
        check_upgrade_verify_wires_alignment(),
    ]
    # «NGOAI-PHAM-VI» (chỉ phát khi bản sao trần) không phải FAIL: phần kiểm được
    # vẫn kiểm đủ, phần thiếu nguyên liệu được NÓI RA thay vì đỏ giả (BH82/BH08).
    overall = ("PASS" if all(check["status"] in ("PASS", "NGOAI-PHAM-VI")
                             for check in checks) else "FAIL")
    return {
        "overall_status": overall,
        "checks": checks,
        "scope": "repo doctrine + Claude Code/Codex sync contract; no clinical validation",
        "disclaimer": "Cần bác sĩ kiểm chứng.",
    }


def main() -> int:
    report = run_verification()
    print("Claude Code / Codex repo alignment:", report["overall_status"])
    for check in report["checks"]:
        print(f"- {check['status']}: {check['name']}")
        if check.get("missing_markers"):
            print(f"  - missing_markers: {check['missing_markers']}")
        if check.get("missing_files"):
            print(f"  - missing_files: {check['missing_files']}")
        if check.get("errors"):
            print(f"  - errors: {check['errors']}")
    print(report["disclaimer"])
    return 0 if report["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
