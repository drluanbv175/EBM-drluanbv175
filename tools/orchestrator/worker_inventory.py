"""Kiểm tra worker plugin có thật trong runtime cục bộ.

Registry nói worker nào ĐƯỢC PHÉP; inventory trả lời worker đó CÓ MẶT hay không.
Hai khái niệm phải tách nhau để thiếu plugin không làm đổi owner và không bị báo như đã gọi.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from . import ROOT
from .plugin_ownership import PluginOwnershipRegistry, WorkerSpec


@dataclass(frozen=True)
class WorkerAvailability:
    worker: str
    available: bool
    source: str = ""
    reason: str = ""

    def as_dict(self) -> dict[str, object]:
        return {
            "worker": self.worker,
            "available": self.available,
            "source": self.source,
            "reason": self.reason,
        }


class WorkerInventory:
    """Lập chỉ mục SKILL.md theo provider, không đọc nội dung nghiệp vụ vào context."""

    def __init__(self, provider_roots: dict[str, tuple[Path, ...]] | None = None) -> None:
        home = Path.home()
        cache = home / ".codex/plugins/cache"
        self.provider_roots = provider_roots or {
            "anthropic-skills": (
                ROOT / "sync/skills",
                cache / "claude-cowork/anthropic-skills",
            ),
            "academic-research-skills": (cache / "academic-research-skills",),
            "aipoch-medical-research": (cache / "aipoch-medical-research",),
            "meta-pipe": (cache / "meta-pipe",),
            "pubmed-search": (cache / "pubmed-search",),
            "claude-code-harness": (cache / "claude-code-harness-marketplace/claude-code-harness",),
            "bio-research": (cache / "claude-cowork/bio-research",),
            "openmed-skills": (cache / "openmed-skills",),
            "medsci-project": (cache / "medsci-skills/medsci-project",),
            "humanizer": (cache / "humanizer",),
            "codex": (cache / "openai-codex/codex",),
        }

    @staticmethod
    def _frontmatter_name(path: Path) -> str:
        try:
            for line in path.read_text(encoding="utf-8", errors="ignore").splitlines()[:80]:
                stripped = line.strip()
                if stripped.startswith("name:"):
                    return stripped.split(":", 1)[1].strip().strip("\"'")
        except OSError:
            pass
        return ""

    @lru_cache(maxsize=None)
    def _index(self, provider: str) -> dict[str, Path]:
        index: dict[str, Path] = {}
        for root in self.provider_roots.get(provider, ()):
            if not root.is_dir():
                continue
            for skill_file in root.rglob("SKILL.md"):
                if ".git" in skill_file.parts or "__pycache__" in skill_file.parts:
                    continue
                names = {skill_file.parent.name.casefold()}
                declared = self._frontmatter_name(skill_file)
                if declared:
                    names.add(declared.casefold())
                for name in names:
                    index.setdefault(name, skill_file)
        return index

    def locate(self, worker: WorkerSpec) -> WorkerAvailability:
        path = self._index(worker.provider).get(worker.unit.casefold())
        if path is not None:
            return WorkerAvailability(worker.key, True, str(path), "SKILL.md khả dụng")
        roots = self.provider_roots.get(worker.provider, ())
        if not roots:
            return WorkerAvailability(worker.key, False, reason="provider chưa có quy tắc kiểm runtime")
        return WorkerAvailability(worker.key, False, reason="không tìm thấy SKILL.md trong provider đã khai")

    def audit(self, registry: PluginOwnershipRegistry) -> list[WorkerAvailability]:
        seen: set[str] = set()
        results: list[WorkerAvailability] = []
        for capability in registry.capabilities.values():
            for worker in capability.workers:
                if worker.key in seen:
                    continue
                seen.add(worker.key)
                results.append(self.locate(worker))
        return results
