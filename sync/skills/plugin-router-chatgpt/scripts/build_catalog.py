#!/usr/bin/env python3
"""Sinh catalog Markdown/JSON từ các plugin đã cài trong Claude Code (cache `installed_plugins.json`).

Hai tầng đọc qua Codex (CLI `codex plugin list` và cấu hình/cache `~/.codex`) đã GỠ 19/11/2026 —
bác sĩ không còn dùng Codex; plugin `codex@openai-codex` cũng rời danh mục.

Catalog JSON phục vụ bộ xếp hạng cục bộ; Markdown là bản tra cứu khi runtime không chạy script.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


PLUGIN_IDS = (
    "humanizer@humanizer",
    "academic-research-skills@academic-research-skills",
    "openmed-skills@openmed-skills",
    "claude-code-harness@claude-code-harness-marketplace",
    "medsci-project@medsci-skills",
    "meta-pipe@meta-pipe",
    "pubmed-search@pubmed-search",
)


@dataclass(frozen=True)
class PluginRecord:
    plugin_id: str
    name: str
    marketplace: str
    version: str
    source_path: Path


@dataclass(frozen=True)
class SkillRecord:
    plugin_id: str
    plugin_name: str
    name: str
    description: str
    relative_path: str


def read_claude_code_cache_plugins(
    installed_path: Path | None = None,
) -> list[PluginRecord]:
    """Dự phòng TẦNG BA — đọc thẳng cache của CLAUDE CODE, không cần Codex CLI hay bất
    kỳ file cấu hình Codex nào.

    Vì sao cần (05/09/2026): hai tầng trên đều đòi ít nhất ``~/.codex/config.toml`` hoặc
    lệnh ``codex`` — một phiên Claude Code không cài Codex (xác nhận trên Cloud: không có
    ``~/.codex/config.toml`` lẫn ``~/.codex/plugins/cache``, dù plugin `codex@openai-codex`
    — bản thân MỘT plugin Claude Code — vẫn cài bình thường) khiến CẢ HAI tầng trên luôn
    ``RuntimeError``, nên trên máy đó catalog không bao giờ tự làm mới được. Hậu quả đo
    được: catalog cam kết 828 skill/9 plugin nhưng máy này đo trực tiếp ra 842 — lệch nặng
    nhất ở `claude-code-harness` (catalog ghi 25, thật 73, do plugin cập nhật nhiều lần kể
    từ lúc catalog được dựng 01/09) và giảm ở `academic-research-skills` (17→4) cùng
    `pubmed-search` (31→10, đúng ý đồ cắt tỉa còn 10 skill tra y văn đã ghi trong
    CLAUDE.md — catalog cũ chưa bao giờ thấy bản đã cắt).

    Đọc CÙNG nguồn dữ liệu với ``tools/kiem_plugin_day_du.py::quet()``
    (``installed_plugins.json`` + trường ``installPath`` của chính Claude Code) để hai
    phép đọc không lệch nhau — không tự suy đường dẫn theo quy ước tên/phiên bản.
    """

    installed_path = installed_path or Path.home() / ".claude/plugins/installed_plugins.json"
    try:
        payload = json.loads(installed_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Không đọc được {installed_path}: {exc}") from exc

    plugins = payload.get("plugins") if isinstance(payload, dict) else None
    if not isinstance(plugins, dict):
        raise RuntimeError(f"{installed_path} không có bảng plugins.")

    records: list[PluginRecord] = []
    missing: list[str] = []
    for plugin_id in PLUGIN_IDS:
        name, marketplace = plugin_id.split("@", 1)
        entries = plugins.get(plugin_id)
        entry = entries[0] if isinstance(entries, list) and entries else None
        install_path = entry.get("installPath") if isinstance(entry, dict) else None
        if not install_path or not Path(str(install_path)).is_dir():
            missing.append(plugin_id)
            continue
        records.append(
            PluginRecord(
                plugin_id=plugin_id,
                name=name,
                marketplace=marketplace,
                version=str(entry.get("version", "local")),
                source_path=Path(str(install_path)),
            )
        )
    if missing:
        raise RuntimeError("Plugin thiếu trong cache Claude Code: " + ", ".join(missing))
    return records


def load_plugin_records() -> list[PluginRecord]:
    """Đọc thẳng cache Claude Code (nguồn duy nhất từ 19/11/2026)."""

    return read_claude_code_cache_plugins()


def resolve_scan_root(record: PluginRecord) -> Path:
    candidates = [record.source_path]
    root = next((path for path in candidates if path.is_dir()), None)
    if root is None:
        raise RuntimeError(f"Không tìm thấy thư mục của {record.plugin_id}")
    return root


def _frontmatter(path: Path) -> tuple[str, str]:
    """Đọc name/description một dòng mà không thêm phụ thuộc YAML."""

    name = path.parent.name
    description = ""
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()[:120]
    except OSError:
        return name, description
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("name:"):
            name = stripped.split(":", 1)[1].strip().strip("\"'") or name
        elif stripped.startswith("description:"):
            description = stripped.split(":", 1)[1].strip().strip("\"'")
    return name, description


def collect_skills(record: PluginRecord) -> list[SkillRecord]:
    root = resolve_scan_root(record)
    found: dict[str, SkillRecord] = {}
    for path in root.rglob("SKILL.md"):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        name, description = _frontmatter(path)
        key = name.casefold()
        found.setdefault(
            key,
            SkillRecord(
                plugin_id=record.plugin_id,
                plugin_name=record.name,
                name=name,
                description=description,
                relative_path=path.relative_to(root).as_posix(),
            ),
        )
    return sorted(found.values(), key=lambda item: item.name.casefold())


def render_markdown(records: list[PluginRecord], skills: list[SkillRecord]) -> str:
    sections = [
        "# Danh mục plugin và skill đã cài",
        "",
        "Tệp được sinh tự động; chỉ đọc mục plugin liên quan, không nạp toàn bộ vào ngữ cảnh.",
        f"Tổng số skill duy nhất: **{len(skills)}** trên **{len(records)}** plugin.",
        "",
    ]
    for plugin in records:
        group = [skill for skill in skills if skill.plugin_id == plugin.plugin_id]
        sections.extend([f"## `{plugin.plugin_id}`", "", f"- Skill tìm thấy: **{len(group)}**", ""])
        if not group:
            sections.append("- Không có `SKILL.md` trực tiếp; plugin có thể chỉ cung cấp command/hook/MCP.")
        for skill in group:
            suffix = f" — {skill.description}" if skill.description else ""
            sections.append(f"- `@{skill.plugin_name}:{skill.name}`{suffix}")
        sections.append("")
    return "\n".join(sections).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parent.parent / "references"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=root / "plugin-catalog.md")
    parser.add_argument("--json-output", type=Path, default=root / "plugin-catalog.json")
    return parser.parse_args()


def _write_if_changed(path: Path, content: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    old = path.read_text(encoding="utf-8") if path.exists() else None
    if old == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def main() -> int:
    args = parse_args()
    try:
        plugins = load_plugin_records()
        skills = [skill for plugin in plugins for skill in collect_skills(plugin)]
        markdown = render_markdown(plugins, skills)
        payload = {
            "schema_version": 1,
            "plugins": [
                {
                    "plugin_id": plugin.plugin_id,
                    "name": plugin.name,
                    "marketplace": plugin.marketplace,
                    "version": plugin.version,
                }
                for plugin in plugins
            ],
            "skills": [asdict(skill) for skill in skills],
        }
        changed = _write_if_changed(args.output, markdown)
        changed |= _write_if_changed(
            args.json_output,
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        )
        print(("Đã cập nhật" if changed else "Danh mục đã khớp") + f": {len(skills)} skill")
    except (OSError, RuntimeError) as exc:
        print(f"LỖI: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
