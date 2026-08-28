#!/usr/bin/env python3
"""Kiem fail-closed quyen so huu giua agent, runtime va plugin worker."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Windows: stdout mặc định cp1252 giết print() tiếng Việt — ép UTF-8 (chốt BH55/R4)
import sys as _sys_r4
for _s_r4 in (_sys_r4.stdout, _sys_r4.stderr):
    try:
        _s_r4.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from orchestrator.flows import RESEARCH_FLOW  # noqa: E402
from orchestrator.plugin_ownership import PluginOwnershipRegistry  # noqa: E402
from orchestrator.registry import Registry  # noqa: E402
from orchestrator.tools_registry import ToolRegistry  # noqa: E402

CONTRACT_MARKER = "_PLUGIN-ROUTING-CONTRACT.md"
REGISTRY_MARKER = "plugin_ownership_registry.json"
CANONICAL_GATES = {"G2", "G4", "G5", "G8", "G9", "G10"}


def _contains(path: Path, markers: tuple[str, ...]) -> list[str]:
    if not path.exists():
        return [f"thieu file {path.relative_to(ROOT)}"]
    text = path.read_text(encoding="utf-8", errors="ignore")
    return [
        f"{path.relative_to(ROOT)} thieu marker {marker}"
        for marker in markers
        if marker not in text
    ]


def ban_sao_tran() -> bool:
    """True khi repo y khoa vắng mặt HOÀN TOÀN (bản clone git trần — cloud/CI).

    28/08/2026 — trên bản trần mọi mục cần medical-ebm-automation/ đỏ vì thiếu
    nguyên liệu, chặn luôn hook pre-commit ⇒ phiên cloud commit KHÔNG QUA CỔNG
    nào. Chỉ nhận diện khi CẢ THƯ MỤC repo vắng mặt; repo có mà file/binding
    mất vẫn FAIL như cũ (fail-closed nguyên vẹn trên hai máy thật)."""
    return not (ROOT / "medical-ebm-automation").exists()


def loi_ngoai_pham_vi_tran(error: str) -> bool:
    """Lỗi CHỈ vì nguyên liệu nằm trong repo y khoa (đường dẫn/binding trỏ sang đó)."""
    return ("medical-ebm-automation" in error
            or error.startswith("thieu production tool binding"))


def verify() -> dict[str, Any]:
    errors: list[str] = []
    checks: list[str] = []

    agents = Registry.load()
    plugins = PluginOwnershipRegistry.load()
    errors.extend(plugins.validate(set(agents.agents)))
    if not errors:
        checks.append("registry schema + owner/provider + runtime")

    research = plugins.resolve("research_lifecycle")
    if research.owner_unit != "dieu-phoi-nghien-cuu":
        errors.append("research_lifecycle khong do dieu-phoi-nghien-cuu so huu")
    if set(research.hard_gates) != CANONICAL_GATES:
        errors.append("research_lifecycle khong du 6 cong cung canonical")
    ars_full = [worker for worker in research.workers if worker.unit == "source-command-ars-full"]
    if len(ars_full) != 1 or ars_full[0].mode != "stage_worker":
        errors.append("/ars-full chua bi ha cap dung thanh stage_worker")
    else:
        checks.append("research owner + /ars-full stage worker + 6 cong cung")

    clinical = plugins.resolve("clinical_case")
    if clinical.owner_unit != "dieu-phoi-lam-sang":
        errors.append("clinical_case khong do dieu-phoi-lam-sang so huu")
    if set(clinical.hard_gates) != {"A", "B"}:
        errors.append("clinical_case khong dung tai ca hai cong A/B")
    else:
        checks.append("clinical owner + cong A/B")

    code_gates = {step.gate for step in RESEARCH_FLOW if step.gate}
    if code_gates != CANONICAL_GATES:
        errors.append(f"RESEARCH_FLOW gate drift: {sorted(code_gates)}")
    else:
        checks.append("RESEARCH_FLOW G0-G10 khop canonical")

    tools = ToolRegistry()
    for tool_id in ("research-pipeline", "g10-assemble"):
        tool = tools.get(tool_id)
        if tool is None or not tool.exists:
            errors.append(f"thieu production tool binding: {tool_id}")
    if not any(error.startswith("thieu production tool binding") for error in errors):
        checks.append("production runtime bindings")

    source_contracts = {
        ROOT / "AGENTS.md": (CONTRACT_MARKER, REGISTRY_MARKER, "verify_plugin_orchestration.py"),
        ROOT / "CLAUDE.md": (CONTRACT_MARKER, REGISTRY_MARKER, "verify_plugin_orchestration.py"),
        ROOT / ".claude/agents/dieu-phoi-nghien-cuu.md": (CONTRACT_MARKER, REGISTRY_MARKER),
        ROOT / ".claude/agents/dieu-phoi-lam-sang.md": (CONTRACT_MARKER, REGISTRY_MARKER),
        ROOT / ".claude/agents/tham-dinh-dau-ra.md": (CONTRACT_MARKER, "G2/G4/G5/G8/G9/G10"),
        ROOT / ".githooks/pre-commit": ("verify_plugin_orchestration.py",),
        ROOT / "tools/sync_agents_to_codex.py": (CONTRACT_MARKER,),
        ROOT / "medical-ebm-automation/CLAUDE.md": (CONTRACT_MARKER, REGISTRY_MARKER),
        ROOT / "medical-ebm-automation/.claude/agents/dieu-phoi-nghien-cuu.md": (CONTRACT_MARKER,),
        ROOT / "medical-ebm-automation/.claude/agents/dieu-phoi-lam-sang.md": (CONTRACT_MARKER,),
        ROOT / "medical-ebm-automation/.claude/agents/tham-dinh-dau-ra.md": (CONTRACT_MARKER,),
        ROOT / "medical-ebm-automation/.claude/agents/_PLUGIN-ROUTING-CONTRACT.md": (
            "HỢP ĐỒNG ĐIỀU PHỐI PLUGIN",
        ),
    }
    before = len(errors)
    for path, markers in source_contracts.items():
        errors.extend(_contains(path, markers))
    if len(errors) == before:
        checks.append("doctrine Claude Code + Codex source + pre-commit")

    mirror_contracts = {
        ROOT / ".Codex/agents/dieu-phoi-nghien-cuu.toml": (CONTRACT_MARKER, REGISTRY_MARKER),
        ROOT / ".Codex/agents/dieu-phoi-lam-sang.toml": (CONTRACT_MARKER, REGISTRY_MARKER),
        ROOT / ".Codex/agents/tham-dinh-dau-ra.toml": (CONTRACT_MARKER,),
        ROOT / ".Codex/agents/_PLUGIN-ROUTING-CONTRACT.md": ("HỢP ĐỒNG ĐIỀU PHỐI PLUGIN",),
    }
    before = len(errors)
    for path, markers in mirror_contracts.items():
        errors.extend(_contains(path, markers))
    if len(errors) == before:
        checks.append("mirror Codex co plugin contract")

    unknown = plugins.resolve("capability-khong-ton-tai")
    unauthorized = plugins.resolve("research_lifecycle", ["plugin-khong-allowlist"])
    if not unknown.status.startswith("BLOCKED"):
        errors.append("unknown capability khong fail-closed")
    if unauthorized.blocked_requests != ("plugin-khong-allowlist",):
        errors.append("worker ngoai allowlist khong bi bao blocked")
    if not errors:
        checks.append("unknown capability + worker ngoai allowlist fail-closed")

    # Trên bản sao trần, các lỗi CHỈ vì nguyên liệu nằm trong repo y khoa được tách
    # sang «ngoài phạm vi» — vẫn IN RA đầy đủ, không đếm FAIL (BH82/BH08). Máy có
    # repo y khoa: ngoai_pham_vi luôn rỗng, hành vi cũ giữ nguyên.
    ngoai_pham_vi: list[str] = []
    if ban_sao_tran():
        ngoai_pham_vi = [e for e in errors if loi_ngoai_pham_vi_tran(e)]
        errors = [e for e in errors if not loi_ngoai_pham_vi_tran(e)]
    return {
        "status": "PASS" if not errors else "FAIL",
        "policy_id": plugins.policy_id,
        "summary": plugins.summary(),
        "checks": checks,
        "errors": errors,
        "ngoai_pham_vi": ngoai_pham_vi,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Kiem quyen so huu plugin EBM")
    parser.add_argument("--json", action="store_true", help="In JSON may doc")
    args = parser.parse_args()
    report = verify()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"PLUGIN_ORCHESTRATION: {report['status']}")
        print(f"- policy: {report['policy_id']}")
        for check in report["checks"]:
            print(f"- PASS {check}")
        for error in report["errors"]:
            print(f"- FAIL {error}")
        for muc in report.get("ngoai_pham_vi", []):
            print(f"- ⚪ NGOAI-PHAM-VI (ban sao tran) {muc}")
        if report.get("ngoai_pham_vi"):
            print("  ⚪ KHONG phai dat — phan nay chi kiem duoc tren may co du hai repo.")
        print("Cần bác sĩ kiểm chứng.")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
