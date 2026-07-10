"""registry.py — Nạp registry 50 agent THẬT từ `.claude/agents/*.md`.

Grounded vào file nguồn: đọc frontmatter (name/description) của mỗi agent, và phân cụm
(lâm sàng / nghiên cứu / guardrail) bằng cách PHÂN TÍCH bảng cụm trong README.md — nhờ đó
danh sách tự cập nhật khi thêm/bớt agent, không hardcode.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from . import ROOT

AGENTS_DIR = ROOT / ".claude" / "agents"
README = AGENTS_DIR / "README.md"


@dataclass(frozen=True)
class AgentSpec:
    name: str
    description: str
    cluster: str  # 'clinical' | 'research' | 'guardrail' | 'unknown'
    path: Path

    @property
    def short(self) -> str:
        """Vai trò ngắn: câu đầu của description (tới dấu — hoặc . đầu tiên)."""
        d = self.description.strip()
        for sep in (" — ", " – ", ". ", ";"):
            if sep in d:
                return d.split(sep, 1)[0].strip()
        return d[:90]


def _parse_frontmatter(text: str) -> dict[str, str]:
    """Lấy các cặp key: value trong khối --- ... --- đầu file (name/description 1 dòng)."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end]
    out: dict[str, str] = {}
    for line in block.splitlines():
        m = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if m:
            out[m.group(1).strip()] = m.group(2).strip()
    return out


def _cluster_map_from_readme() -> dict[str, str]:
    """Phân cụm agent theo các mục '## Cụm Lâm sàng / Nghiên cứu / Guardrail' trong README."""
    mapping: dict[str, str] = {}
    if not README.exists():
        return mapping
    section = None
    for line in README.read_text(encoding="utf-8", errors="ignore").splitlines():
        h = line.strip().lower()
        if h.startswith("## "):
            if "cụm lâm sàng" in h:
                section = "clinical"
            elif "cụm nghiên cứu" in h:
                section = "research"
            elif "guardrail" in h:
                section = "guardrail"
            else:
                section = None
            continue
        if section and line.lstrip().startswith("|"):
            m = re.search(r"\|\s*`([a-z0-9-]+)`", line)
            if m:
                mapping[m.group(1)] = section
    return mapping


def load_agents(agents_dir: Path = AGENTS_DIR) -> dict[str, AgentSpec]:
    """Trả {name -> AgentSpec} cho mọi agent (loại README.md và file `_*` hạ tầng)."""
    clusters = _cluster_map_from_readme()
    agents: dict[str, AgentSpec] = {}
    for md in sorted(agents_dir.glob("*.md")):
        if md.name == "README.md" or md.name.startswith("_"):
            continue
        text = md.read_text(encoding="utf-8", errors="ignore")
        fm = _parse_frontmatter(text)
        name = fm.get("name") or md.stem
        agents[name] = AgentSpec(
            name=name,
            description=fm.get("description", ""),
            cluster=clusters.get(name, "unknown"),
            path=md,
        )
    return agents


@dataclass
class Registry:
    agents: dict[str, AgentSpec] = field(default_factory=dict)

    @classmethod
    def load(cls, agents_dir: Path = AGENTS_DIR) -> "Registry":
        return cls(agents=load_agents(agents_dir))

    def has(self, name: str) -> bool:
        return name in self.agents

    def get(self, name: str) -> AgentSpec | None:
        return self.agents.get(name)

    def by_cluster(self, cluster: str) -> list[AgentSpec]:
        return [a for a in self.agents.values() if a.cluster == cluster]

    def counts(self) -> dict[str, int]:
        out = {"total": len(self.agents), "clinical": 0, "research": 0, "guardrail": 0, "unknown": 0}
        for a in self.agents.values():
            out[a.cluster] = out.get(a.cluster, 0) + 1
        return out

    def validate(self, expected_total: int | None = None) -> list[str]:
        """Trả danh sách cảnh báo (rỗng = sạch). Bắt agent chưa phân cụm / lệch tổng."""
        warns: list[str] = []
        unknown = [a.name for a in self.agents.values() if a.cluster == "unknown"]
        if unknown:
            warns.append(f"{len(unknown)} agent chưa phân cụm (README?): {', '.join(sorted(unknown)[:6])}…")
        if expected_total is not None and len(self.agents) != expected_total:
            warns.append(f"Tổng agent = {len(self.agents)}, kỳ vọng {expected_total}")
        return warns
