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

Thiết kế: deterministic control plane, CHẠY & KIỂM ĐƯỢC OFFLINE (chế độ dry-run/plan),
có seam cắm LLM adapter (Codex wrapper) cho thực thi agent thật. Grounded vào registry
`.claude/agents/*.md` THẬT — không hardcode danh sách agent.

"Cần bác sĩ kiểm chứng." — orchestrator chỉ ĐỀ XUẤT + dừng ở cổng bác sĩ duyệt.
"""

from __future__ import annotations

from pathlib import Path

# ROOT = thư mục gốc "Claude AI" (orchestrator → tools → ROOT)
ROOT = Path(__file__).resolve().parents[2]


def duong_that(rel_path: str) -> Path:
    """Giải quyết một đường dẫn tương đối ROOT, ưu tiên sibling cho nhánh
    medical-ebm-automation/... — vá 07/09/2026 cùng tools/ban_sao_tran.py.

    Trên phiên cloud, add_repo dựng medical-ebm-automation làm ANH EM của repo
    gốc (`ROOT.parent/medical-ebm-automation`), không LỒNG bên trong (`ROOT/
    medical-ebm-automation`). `ROOT / rel_path` một mình không bao giờ tìm ra
    sibling — mọi rel_path bắt đầu bằng "medical-ebm-automation/" phải đi qua
    đây thay vì tự ghép `ROOT / rel_path`.
    """
    if rel_path.startswith("medical-ebm-automation/"):
        import importlib.util
        duong_bst = Path(__file__).resolve().parents[1] / "ban_sao_tran.py"
        spec = importlib.util.spec_from_file_location("_bst_orch", duong_bst)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        goc = mod.duong_goc("medical-ebm-automation", ROOT) or (ROOT / "medical-ebm-automation")
        return goc / rel_path[len("medical-ebm-automation/"):]
    return ROOT / rel_path


__all__ = ["ROOT", "duong_that"]
__version__ = "1.2.0"
