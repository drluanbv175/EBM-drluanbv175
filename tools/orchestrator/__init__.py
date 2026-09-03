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

from pathlib import Path

# ROOT = thư mục gốc "Claude AI" (orchestrator → tools → ROOT)
ROOT = Path(__file__).resolve().parents[2]

__all__ = ["ROOT"]
__version__ = "2.0.0"
