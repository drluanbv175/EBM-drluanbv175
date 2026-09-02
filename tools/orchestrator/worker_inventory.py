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


# Hai lý do vắng mặt KHÁC NHAU về bản chất (01/09/2026, BH85). Plugin cài THEO TỪNG MÁY
# (sổ khai sync/plugin-manifest.json cho phép một plugin chỉ có ở Mac): máy không có thư
# mục provider là THIẾU NGUYÊN LIỆU — lane ⑤ dong_bo_plugin_claude_codex.py đối chiếu với
# ý định đã khai. Còn provider CÓ mà thiếu đúng SKILL.md đã khai là BINDING TREO thật.
# Gộp hai thứ thành một FAIL khiến cổng đỏ ở mọi máy không phải Mac (đo trên cloud:
# 10 binding «không tìm thấy» chỉ vì ~/.codex/plugins/cache không tồn tại).
LY_DO_CHUA_CAI = "plugin chưa cài trên máy này"
LY_DO_THIEU_SKILL = "không tìm thấy SKILL.md/lệnh trong provider đã khai"
LY_DO_KHONG_QUY_TAC = "provider chưa có quy tắc kiểm runtime"

# TIỀN TỐ TÊN UNIT cho worker kiểu LỆNH (không phải SKILL.md) — riêng của
# academic-research-skills (02/09/2026, phát hiện khi lần đầu cài THẬT plugin này).
# `plugin_ownership_registry.json` đặt tên 9 unit của provider này là
# `source-command-ars-<tên>`, nhưng file thật trên đĩa là `commands/ars-<tên>.md`
# (không có tiền tố) — registry chưa từng được đối chiếu với plugin cài thật, vì
# trước 02/09 provider này luôn ⚪ "chưa cài" trên mọi máy đã kiểm. Đây là quy ước
# ĐẶT TÊN của registry, không phải cách runtime khác đặt tên; không suy rộng cho
# provider khác (đã kiểm: không provider nào khác dùng tiền tố này).
TIEN_TO_LENH = "source-command-"


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
        # HAI kho cache — vá 02/09/2026. Bản cũ chỉ tra `~/.codex/plugins/cache`, trong khi
        # Claude Code cài plugin vào `~/.claude/plugins/cache`. Đo trên phiên cloud ngay sau
        # khi cài đủ 7 plugin (778 SKILL.md): thư mục Codex KHÔNG TỒN TẠI, nên cả 26 worker
        # binding đều báo «chưa cài» — nghĩa là nhạc trưởng sẽ luôn ghi LOCAL_FALLBACK và
        # KHÔNG BAO GIỜ dùng plugin vừa cài. Cùng họ lỗi «đo đúng, nhưng đo nhầm chỗ» của
        # BH74 (catalog quét sai thư mục đang phục vụ).
        # Thứ tự: Claude trước (nơi `claude plugin install` ghi), Codex sau (máy có Codex CLI).
        caches = (home / ".claude/plugins/cache", home / ".codex/plugins/cache")

        def duong(*hau_to: str) -> tuple[Path, ...]:
            """Cùng một hậu tố, tra ở CẢ HAI kho — thứ tự quyết định bản nào thắng."""
            return tuple(c / h for c in caches for h in hau_to)

        self.provider_roots = provider_roots or {
            "anthropic-skills": (ROOT / "sync/skills",) + duong("claude-cowork/anthropic-skills"),
            "academic-research-skills": duong("academic-research-skills"),
            "aipoch-medical-research": duong("aipoch-medical-research"),
            "meta-pipe": duong("meta-pipe"),
            "pubmed-search": duong("pubmed-search"),
            "claude-code-harness": duong("claude-code-harness-marketplace/claude-code-harness"),
            "bio-research": duong("claude-cowork/bio-research"),
            "openmed-skills": duong("openmed-skills"),
            "medsci-project": duong("medsci-skills/medsci-project"),
            "humanizer": duong("humanizer"),
            "codex": duong("openai-codex/codex"),
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
            # Một plugin có thể phơi năng lực bằng LỆNH (`commands/*.md`) thay vì SKILL.md —
            # đo được ở academic-research-skills: 4 SKILL.md ở gốc + 16 lệnh trong `commands/`,
            # và toàn bộ 9 worker registry bind vào ĐỀU trỏ lệnh, không trỏ skill. `rglob`
            # (không phải `root / "commands"`) vì `provider_roots` trỏ THƯ MỤC MARKETPLACE —
            # nội dung plugin thật nằm sâu thêm một cấp phiên bản (`<provider>/<version>/commands/`),
            # đúng cách SKILL.md ở trên cũng phải rglob thay vì `root.glob("SKILL.md")`.
            for cmd_file in root.rglob("commands/*.md"):
                if ".git" in cmd_file.parts or "__pycache__" in cmd_file.parts:
                    continue
                index.setdefault(cmd_file.stem.casefold(), cmd_file)
        return index

    def locate(self, worker: WorkerSpec) -> WorkerAvailability:
        muc_luc = self._index(worker.provider)
        unit = worker.unit.casefold()
        path = muc_luc.get(unit)
        nguon = "SKILL.md khả dụng"
        if path is None and unit.startswith(TIEN_TO_LENH):
            # Quy ước đặt tên riêng của registry (xem TIEN_TO_LENH) — không phải cách
            # runtime đặt tên; chỉ thử bỏ tiền tố SAU khi khớp thẳng đã thất bại.
            path = muc_luc.get(unit[len(TIEN_TO_LENH):])
            nguon = "lệnh khả dụng (registry đặt tên có tiền tố source-command-)"
        if path is not None:
            return WorkerAvailability(worker.key, True, str(path), nguon)
        roots = self.provider_roots.get(worker.provider, ())
        if not roots:
            return WorkerAvailability(worker.key, False, reason=LY_DO_KHONG_QUY_TAC)
        if not any(root.is_dir() for root in roots):
            return WorkerAvailability(worker.key, False, reason=LY_DO_CHUA_CAI)
        return WorkerAvailability(worker.key, False, reason=LY_DO_THIEU_SKILL)

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
