#!/usr/bin/env python3
"""Kiem fail-closed quyen so huu giua agent, runtime va plugin worker."""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
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

from orchestrator import duong_that  # noqa: E402
from orchestrator.flows import RESEARCH_FLOW  # noqa: E402
from orchestrator.plugin_ownership import PluginOwnershipRegistry  # noqa: E402
from orchestrator.registry import Registry  # noqa: E402
from orchestrator.tools_registry import ToolRegistry  # noqa: E402
from orchestrator.worker_inventory import (  # noqa: E402
    LY_DO_CHUA_CAI,
    WorkerAvailability,
    WorkerInventory,
)

CONTRACT_MARKER = "_PLUGIN-ROUTING-CONTRACT.md"
REGISTRY_MARKER = "plugin_ownership_registry.json"
CANONICAL_GATES = {"G2", "G4", "G5", "G8", "G9", "G10"}
ROUTER_SOURCE = ROOT / "sync/skills/plugin-router-chatgpt"
ROUTER_ZIP = ROOT / "CHATGPT_SKILLS/dist/plugin-router-chatgpt.zip"


def _hien_thi(path: Path) -> str:
    """Đường dẫn ngắn để in — tương đối ROOT nếu trong cây, tuyệt đối nếu là
    sibling (medical-ebm-automation qua duong_that() có thể nằm ngoài ROOT)."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _contains(path: Path, markers: tuple[str, ...]) -> list[str]:
    if not path.exists():
        return [f"thieu file {_hien_thi(path)}"]
    text = path.read_text(encoding="utf-8", errors="ignore")
    return [
        f"{_hien_thi(path)} thieu marker {marker}"
        for marker in markers
        if marker not in text
    ]


def ban_sao_tran() -> bool:
    """True CHỈ khi bản sao git trần — định nghĩa DUY NHẤT ở tools/ban_sao_tran.py.

    SỬA 28/08 vòng 4 (bình duyệt đối kháng bắt được): bản đầu chỉ kiểm MỘT gốc
    (medical-ebm-automation/) — trên máy thật còn EBM-Dashboards/EBM_MASTER mà
    thiếu riêng repo y khoa (sự cố OneDrive đã gặp), hook lặng lẽ PASS = fail-open.
    Nay đòi cả BA gốc vắng mặt, cùng ngữ nghĩa với bộ chốt bài học/conftest."""
    import importlib.util
    duong = Path(__file__).resolve().parent / "ban_sao_tran.py"
    spec = importlib.util.spec_from_file_location("_bst_plugin_orch", duong)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.ban_sao_git_tran(ROOT)


def loi_ngoai_pham_vi_tran(error: str) -> bool:
    """Lỗi CHỈ vì nguyên liệu nằm trong repo y khoa (đường dẫn/binding trỏ sang đó)."""
    return ("medical-ebm-automation" in error
            or error.startswith("thieu production tool binding"))


def phan_loai_binding(item: WorkerAvailability) -> str:
    """'dat' | 'chua_cai' | 'loi' — tách «thiếu nguyên liệu» khỏi «binding treo» (BH08/BH85).

    Plugin không cài trên máy NÀY là chuyện sổ khai sync/plugin-manifest.json (can_o_may)
    đã dự liệu và lane ⑤ của dong_bo_tat_ca đối chiếu; cổng này KHÔNG đoán lại ý định
    máy, chỉ ghi ⚪ có khai báo. Provider có mặt mà thiếu đúng skill đã khai mới là lỗi.
    """
    if item.available:
        return "dat"
    if item.reason == LY_DO_CHUA_CAI:
        return "chua_cai"
    return "loi"


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
        duong_that("medical-ebm-automation/CLAUDE.md"): (CONTRACT_MARKER, REGISTRY_MARKER),
        duong_that("medical-ebm-automation/.claude/agents/dieu-phoi-nghien-cuu.md"): (CONTRACT_MARKER,),
        duong_that("medical-ebm-automation/.claude/agents/dieu-phoi-lam-sang.md"): (CONTRACT_MARKER,),
        duong_that("medical-ebm-automation/.claude/agents/tham-dinh-dau-ra.md"): (CONTRACT_MARKER,),
        duong_that("medical-ebm-automation/.claude/agents/_PLUGIN-ROUTING-CONTRACT.md"): (
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

    # Worker binding phải trỏ tới skill CÓ THẬT. Registry chỉ nói quyền; nếu không
    # kiểm runtime, một binding treo vẫn PASS và owner có thể tưởng plugin đã chạy.
    inventory = WorkerInventory()
    chua_cai: list[str] = []
    missing_workers: list[WorkerAvailability] = []
    for item in inventory.audit(plugins):
        loai = phan_loai_binding(item)
        if loai == "chua_cai":
            chua_cai.append(f"worker binding chua kiem duoc: {item.worker} — {item.reason}")
        elif loai == "loi":
            missing_workers.append(item)
    for item in missing_workers:
        errors.append(f"worker binding khong kha dung: {item.worker} — {item.reason}")
    if not missing_workers and not chua_cai:
        checks.append("mọi worker binding có SKILL.md thật trong đúng provider")
    elif not missing_workers:
        checks.append(f"worker binding: {len(chua_cai)} thuộc plugin chưa cài trên máy này (⚪), "
                      "còn lại có SKILL.md thật")

    # Router là cửa vào tự động cho ChatGPT/Codex. Kiểm nguồn canonical, liên kết hai
    # runtime và gói phân phối; symlink gãy không được phép bị báo như đã đồng bộ.
    router_files = (
        ROUTER_SOURCE / "SKILL.md",
        ROUTER_SOURCE / "agents/openai.yaml",
        ROUTER_SOURCE / "references/governance.md",
        ROUTER_SOURCE / "references/plugin-catalog.json",
        ROUTER_SOURCE / "scripts/build_catalog.py",
        ROUTER_SOURCE / "scripts/route_skill.py",
    )
    missing_router = [path for path in router_files if not path.is_file()]
    for path in missing_router:
        errors.append(f"router thieu file: {path.relative_to(ROOT)}")

    for runtime in (Path.home() / ".claude/skills", Path.home() / ".codex/skills"):
        target = runtime / "plugin-router-chatgpt"
        if not target.exists():
            errors.append(f"router runtime khong ton tai/liên ket gay: {target}")
        elif target.resolve() != ROUTER_SOURCE.resolve():
            errors.append(f"router runtime tro sai nguon: {target} -> {target.resolve()}")

    if not ROUTER_ZIP.is_file():
        errors.append(f"thieu goi router ChatGPT: {ROUTER_ZIP.relative_to(ROOT)}")
    elif not missing_router:
        source_files = [
            path
            for path in ROUTER_SOURCE.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
        ]
        newest_source = max(path.stat().st_mtime for path in source_files)
        if ROUTER_ZIP.stat().st_mtime < newest_source:
            errors.append("goi plugin-router-chatgpt.zip cu hon nguon canonical")
        try:
            with zipfile.ZipFile(ROUTER_ZIP) as archive:
                bad = archive.testzip()
                names = set(archive.namelist())
            if bad:
                errors.append(f"goi router ZIP hong tai: {bad}")
            if "plugin-router-chatgpt/SKILL.md" not in names:
                errors.append("goi router ZIP thieu SKILL.md o thu muc goc")
        except (OSError, zipfile.BadZipFile) as exc:
            errors.append(f"khong doc duoc goi router ZIP: {exc}")

    catalog_path = ROUTER_SOURCE / "references/plugin-catalog.json"
    if catalog_path.is_file():
        try:
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            count = len(catalog.get("skills", []))
            if count < 100:
                errors.append(f"catalog router bat thuong: chi co {count} skill")
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"catalog router JSON khong hop le: {exc}")

    if not missing_router and not any("router" in error or "catalog" in error for error in errors):
        checks.append("router canonical + runtime links + catalog + ZIP")

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
        "chua_cai": chua_cai,
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
        for muc in report.get("chua_cai", []):
            print(f"- ⚪ CHUA-CAI-TREN-MAY-NAY {muc}")
        if report.get("chua_cai"):
            print("  ⚪ KHONG phai dat — plugin cai theo tung may; y dinh o sync/plugin-manifest.json,"
                  " doi chieu bang tools/dong_bo_plugin_claude_codex.py (lane 5).")
        print("Cần bác sĩ kiểm chứng.")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
