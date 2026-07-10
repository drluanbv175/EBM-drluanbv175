"""Orchestrator EBM — control plane chạy được cho đội 50 agent.

Sáu năng lực (mỗi năng lực = một module):
  1. Điều phối agent        → orchestrator.py + flows.py + agent_adapter.py
  2. Quản lý ngữ cảnh       → context.py (Session · checkpoint · resume)
  3. Định tuyến intent      → intent.py (IntentRouter)
  4. Tích hợp tri thức      → knowledge.py (thứ bậc nguồn Cấp 0/0.5/1)
  5. Tích hợp công cụ       → tools_registry.py (ToolRegistry)
  6. Quản lý vòng đời       → lifecycle.py (RequestLifecycle · cổng · guardrail · retry)

Thiết kế: deterministic control plane, CHẠY & KIỂM ĐƯỢC OFFLINE (chế độ dry-run/plan),
có seam cắm LLM adapter (Codex wrapper) cho thực thi agent thật. Grounded vào registry
`.claude/agents/*.md` THẬT — không hardcode danh sách agent.

"Cần bác sĩ kiểm chứng." — orchestrator chỉ ĐỀ XUẤT + dừng ở cổng bác sĩ duyệt.
"""

from __future__ import annotations

from pathlib import Path

# ROOT = thư mục gốc "Claude AI" (orchestrator → tools → ROOT)
ROOT = Path(__file__).resolve().parents[2]

__all__ = ["ROOT"]
__version__ = "1.0.0"
