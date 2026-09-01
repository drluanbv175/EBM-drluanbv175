#!/usr/bin/env python3
"""Sinh catalog Markdown/JSON từ chín plugin đã cài trong Codex.

Catalog JSON phục vụ bộ xếp hạng cục bộ; Markdown là bản tra cứu khi runtime không chạy script.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


PLUGIN_IDS = (
    "codex@openai-codex",
    "humanizer@humanizer",
    "academic-research-skills@academic-research-skills",
    "openmed-skills@openmed-skills",
    "claude-code-harness@claude-code-harness-marketplace",
    "medsci-project@medsci-skills",
    "aipoch-medical-research@aipoch-medical-research",
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


def _codex_binary() -> str:
    candidates = (
        os.environ.get("EBM_CODEX_BIN"),
        shutil.which("codex"),
        "/Applications/ChatGPT.app/Contents/Resources/codex",
        str(Path.home() / ".local/bin/codex"),
    )
    found = next((item for item in candidates if item and Path(item).is_file()), None)
    if not found:
        raise RuntimeError("Không tìm thấy lệnh codex; đặt EBM_CODEX_BIN để chỉ rõ đường dẫn.")
    return found


def read_installed_plugins() -> dict[str, object]:
    """Đọc trạng thái plugin thật từ Codex CLI."""

    try:
        result = subprocess.run(
            [_codex_binary(), "plugin", "list", "--json"],
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
        payload = json.loads(result.stdout)
    except (FileNotFoundError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Không đọc được danh sách plugin Codex: {exc}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("Cấu trúc JSON plugin không hợp lệ.")
    return payload


def select_plugins(payload: dict[str, object]) -> list[PluginRecord]:
    installed = payload.get("installed")
    if not isinstance(installed, list):
        raise RuntimeError("Thiếu danh sách installed trong dữ liệu plugin.")
    by_id = {
        item["pluginId"]: item
        for item in installed
        if isinstance(item, dict) and isinstance(item.get("pluginId"), str)
    }
    records: list[PluginRecord] = []
    missing: list[str] = []
    for plugin_id in PLUGIN_IDS:
        item = by_id.get(plugin_id)
        if not item or item.get("enabled") is not True:
            missing.append(plugin_id)
            continue
        source = item.get("source")
        source_path = source.get("path") if isinstance(source, dict) else ""
        records.append(
            PluginRecord(
                plugin_id=plugin_id,
                name=str(item.get("name", "")),
                marketplace=str(item.get("marketplaceName", "")),
                version=str(item.get("version", "local")),
                source_path=Path(str(source_path)),
            )
        )
    if missing:
        raise RuntimeError("Plugin thiếu hoặc chưa bật: " + ", ".join(missing))
    return records


def resolve_scan_root(record: PluginRecord) -> Path:
    candidates = [
        Path.home() / ".codex/plugins/cache" / record.marketplace / record.name / record.version,
        Path.home() / ".codex/plugins/cache" / record.marketplace / record.name,
        record.source_path,
    ]
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
        plugins = select_plugins(read_installed_plugins())
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
