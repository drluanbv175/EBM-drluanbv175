#!/usr/bin/env python3
"""Standalone Claude/Codex agent sync health gate.

Source of truth is `.claude/agents`. This gate is intentionally read-only:
it checks the generated Codex mirrors, mandatory guardrails, disclaimer
coverage, and core infrastructure files without rewriting anything.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import sync_agents_to_codex as sync


ROOT = Path(__file__).resolve().parents[1]
MARKER = "EBM-MANDATORY-FINAL-GUARDRAIL"
DISCLAIMER = "Cần bác sĩ kiểm chứng"


@dataclass(frozen=True)
class SourceHealth:
    agents: int
    infra_files: int
    guardrail_agents: int
    disclaimer_agents: int
    missing_guardrail: list[str]
    missing_disclaimer: list[str]


@dataclass(frozen=True)
class TargetHealth:
    label: str
    exists: bool
    alias_of: str | None
    agent_toml: int
    infra_files: int
    guardrail_agents: int
    disclaimer_agents: int
    missing_guardrail: list[str]
    missing_disclaimer: list[str]
    sync_errors: list[str]


@dataclass(frozen=True)
class SyncHealthReport:
    status: str
    source: SourceHealth
    targets: list[TargetHealth]
    errors: list[str]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _source_health() -> SourceHealth:
    agents = sync.source_agent_paths()
    infra = sync.source_infra_paths()
    missing_guardrail: list[str] = []
    missing_disclaimer: list[str] = []
    for path in agents:
        text = _read(path)
        if MARKER not in text:
            missing_guardrail.append(path.name)
        if DISCLAIMER not in text:
            missing_disclaimer.append(path.name)
    return SourceHealth(
        agents=len(agents),
        infra_files=len(infra),
        guardrail_agents=len(agents) - len(missing_guardrail),
        disclaimer_agents=len(agents) - len(missing_disclaimer),
        missing_guardrail=missing_guardrail,
        missing_disclaimer=missing_disclaimer,
    )


def _target_rows() -> list[tuple[Path, str, str | None]]:
    rows: list[tuple[Path, str, str | None]] = []
    canonical: list[tuple[Path, str]] = []
    for target_dir, target_label in sync.TARGETS:
        alias_of: str | None = None
        for seen_dir, seen_label in canonical:
            try:
                if target_dir.exists() and seen_dir.exists() and target_dir.samefile(seen_dir):
                    alias_of = seen_label
                    break
            except OSError:
                continue
        rows.append((target_dir, target_label, alias_of))
        if alias_of is None:
            canonical.append((target_dir, target_label))
    return rows


def _target_health(target_dir: Path, target_label: str, alias_of: str | None) -> TargetHealth:
    sync_errors = [] if alias_of else sync.check_target(target_dir, target_label)
    toml_files = sorted(target_dir.glob("*.toml")) if target_dir.exists() else []
    infra_files = sorted(
        path for path in target_dir.glob("*.md")
        if path.name == "README.md" or path.name.startswith("_")
    ) if target_dir.exists() else []
    missing_guardrail: list[str] = []
    missing_disclaimer: list[str] = []
    for path in toml_files:
        text = _read(path)
        if MARKER not in text:
            missing_guardrail.append(path.name)
        if DISCLAIMER not in text:
            missing_disclaimer.append(path.name)
    return TargetHealth(
        label=target_label,
        exists=target_dir.exists(),
        alias_of=alias_of,
        agent_toml=len(toml_files),
        infra_files=len(infra_files),
        guardrail_agents=len(toml_files) - len(missing_guardrail),
        disclaimer_agents=len(toml_files) - len(missing_disclaimer),
        missing_guardrail=missing_guardrail,
        missing_disclaimer=missing_disclaimer,
        sync_errors=sync_errors,
    )


def evaluate_sync_health() -> SyncHealthReport:
    source = _source_health()
    targets = [_target_health(path, label, alias_of) for path, label, alias_of in _target_rows()]
    errors: list[str] = []

    if source.missing_guardrail:
        errors.append(
            "source agents missing mandatory guardrail: "
            + ", ".join(source.missing_guardrail)
        )
    if source.missing_disclaimer:
        errors.append(
            "source agents missing clinical disclaimer: "
            + ", ".join(source.missing_disclaimer)
        )

    for target in targets:
        if not target.exists:
            errors.append(f"{target.label}: missing target directory")
        if target.alias_of:
            continue
        if target.agent_toml != source.agents:
            errors.append(
                f"{target.label}: {target.agent_toml} TOML != {source.agents} source agents"
            )
        if target.missing_guardrail:
            errors.append(
                f"{target.label}: missing mandatory guardrail in "
                + ", ".join(target.missing_guardrail)
            )
        if target.missing_disclaimer:
            errors.append(
                f"{target.label}: missing clinical disclaimer in "
                + ", ".join(target.missing_disclaimer)
            )
        if target.sync_errors:
            errors.append(f"{target.label}: sync drift/errors detected")

    status = "PASS" if not errors else "FAIL"
    return SyncHealthReport(status=status, source=source, targets=targets, errors=errors)


def _print_text(report: SyncHealthReport) -> None:
    print("Claude/Codex sync health:", report.status)
    print(
        "- source: "
        f"{report.source.agents} agents, "
        f"guardrail {report.source.guardrail_agents}/{report.source.agents}, "
        f"disclaimer {report.source.disclaimer_agents}/{report.source.agents}, "
        f"infra {report.source.infra_files}"
    )
    for target in report.targets:
        alias = f", alias_of {target.alias_of}" if target.alias_of else ""
        print(
            f"- {target.label}: "
            f"{target.agent_toml} TOML, "
            f"guardrail {target.guardrail_agents}/{target.agent_toml}, "
            f"disclaimer {target.disclaimer_agents}/{target.agent_toml}, "
            f"infra {target.infra_files}, "
            f"sync_errors {len(target.sync_errors)}"
            f"{alias}"
        )
    if report.errors:
        print("Errors:")
        for error in report.errors:
            print(f"- {error}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    report = evaluate_sync_health()
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        _print_text(report)
    return 0 if report.status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
