"""Orchestrator EBM — control plane chạy được cho đội 50 agent và plugin worker.

Tám năng lực (mỗi năng lực = một module):
  1. Điều phối agent        → orchestrator.py + flows.py + agent_adapter.py
  2. Quản lý ngữ cảnh       → context.py (Session · checkpoint · resume)
  3. Định tuyến intent      → intent.py (IntentRouter)
  4. Tích hợp tri thức      → knowledge.py (thứ bậc nguồn Cấp 0/0.5/1)
  5. Tích hợp công cụ       → tools_registry.py (ToolRegistry)
  6. Quản lý vòng đời       → lifecycle.py (RequestLifecycle · cổng · guardrail · retry)
  7. Điều phối plugin       → plugin_ownership.py + plugin_ownership_registry.json
  8. Vòng khép kín          → worker_inventory.py + guardrail_bridge.py

Thiết kế: deterministic control plane, CHẠY & KIỂM ĐƯỢC OFFLINE (dry-run) và thực thi
agent thật qua Codex CLI chỉ-đọc khi bật ``--execute``. Grounded vào registry
`.claude/agents/*.md` THẬT — không hardcode danh sách agent.

"Cần bác sĩ kiểm chứng." — orchestrator chỉ ĐỀ XUẤT + dừng ở cổng bác sĩ duyệt.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

# ROOT = thư mục gốc "Claude AI" (orchestrator → tools → ROOT)
ROOT = Path(__file__).resolve().parents[2]


def _root_du_lieu_ngoai_git() -> Path:
    """Checkout CHÍNH để đọc `EBM-Dashboards/`/`medical-ebm-automation/` (ngoài-git)
    khi `ROOT` là một git worktree phụ — xem
    `tools/ban_sao_tran.py::checkout_chinh()` (VÁ 16/09/2026, vòng 6). `ROOT` vẫn là
    export CHÍNH dùng cho mọi đường dẫn GIT-TRACKED (`.claude/agents/`, `tools/`…) —
    worktree có bản checkout riêng, và đó là bản CẦN kiểm. Vắng nguyên liệu hoặc
    không xác định được ⇒ giữ NGUYÊN `ROOT` (không đoán liều, BH08)."""
    duong = Path(__file__).resolve().parents[1] / "ban_sao_tran.py"
    if not duong.is_file():
        return ROOT
    spec = importlib.util.spec_from_file_location("_orch_ban_sao_tran", duong)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        return mod.checkout_chinh(ROOT) or ROOT
    except Exception:  # noqa: BLE001
        return ROOT


ROOT_DU_LIEU = _root_du_lieu_ngoai_git()

__all__ = ["ROOT", "ROOT_DU_LIEU"]
__version__ = "2.0.0"
