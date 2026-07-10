"""agent_adapter.py — Lớp THỰC THI agent (seam cắm LLM).

Agent EBM là subagent LLM (định nghĩa prompt .md). Control plane không tự chạy LLM; nó gọi
qua một AgentExecutor:
  • DryRunExecutor — chạy/kiểm OFFLINE: trả 'kế hoạch' (agent sẽ làm gì + công cụ nào),
    KHÔNG cần API. Dùng cho plan/test/CI.
  • LLMExecutor    — seam cho thực thi THẬT qua Codex/LLM wrapper (cần API key + env);
    CHƯA bật ở đây (trung thực về kỹ thuật) — cắm vào là chạy thật.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from .registry import Registry
from .tools_registry import ToolRegistry


@dataclass
class AgentResult:
    agent: str
    status: str            # 'planned' | 'ok' | 'error' | 'skipped'
    summary: str
    tool_calls: list[str] = field(default_factory=list)
    needs_input: str = ""  # nếu agent cần input đời thực (IRB/data/…)

    def as_dict(self) -> dict:
        return {"agent": self.agent, "status": self.status, "summary": self.summary,
                "tool_calls": self.tool_calls, "needs_input": self.needs_input}


class AgentExecutor(ABC):
    @abstractmethod
    def execute(self, agent: str, registry: Registry, tools: ToolRegistry) -> AgentResult: ...


class DryRunExecutor(AgentExecutor):
    """Không gọi LLM — trả kế hoạch dựa trên spec agent + công cụ đã đăng ký."""

    def execute(self, agent: str, registry: Registry, tools: ToolRegistry) -> AgentResult:
        spec = registry.get(agent)
        if spec is None:
            return AgentResult(agent, "error", f"agent '{agent}' KHÔNG có trong registry (tham chiếu treo)")
        tcalls = [t.tool_id for t in tools.for_agent(agent)]
        return AgentResult(agent, "planned", spec.short or "(không có mô tả)", tool_calls=tcalls)


class LLMExecutor(AgentExecutor):
    """Seam thực thi THẬT — cần LLM/Codex wrapper. CHƯA triển khai (cần API key + môi trường)."""

    def __init__(self, client=None) -> None:  # noqa: ANN001 — client wrapper do người cắm
        self.client = client

    def execute(self, agent: str, registry: Registry, tools: ToolRegistry) -> AgentResult:
        raise NotImplementedError(
            "LLMExecutor cần một wrapper Codex/LLM (API key + env) — [CẦN MÔI TRƯỜNG HỖ TRỢ]. "
            "Cắm client rồi truyền vào để thực thi agent thật; hiện dùng DryRunExecutor để plan/kiểm offline.")
