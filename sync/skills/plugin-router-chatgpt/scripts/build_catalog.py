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
import tomllib
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


def read_configured_plugins_from_cache(
    config_path: Path | None = None,
    cache_root: Path | None = None,
) -> list[PluginRecord]:
    """Dự phòng fail-closed bằng cấu hình bật + cache thật khi Codex CLI lỗi.

    Một marketplace kiểu Claude không có manifest Codex có thể khiến
    ``codex plugin list`` hỏng TOÀN BỘ dù chín plugin đã cài vẫn còn nguyên trong
    cache. Nhánh này không cài/gỡ/sửa cấu hình: nó chỉ nhận plugin được ghi rõ
    ``enabled = true`` rồi đòi đúng thư mục cache tương ứng phải tồn tại.
    """

    config_path = config_path or Path.home() / ".codex/config.toml"
    cache_root = cache_root or Path.home() / ".codex/plugins/cache"
    try:
        config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise RuntimeError(f"Không đọc được cấu hình Codex dự phòng: {exc}") from exc

    configured = config.get("plugins")
    if not isinstance(configured, dict):
        raise RuntimeError("Cấu hình Codex không có bảng plugins.")

    records: list[PluginRecord] = []
    missing: list[str] = []
    for plugin_id in PLUGIN_IDS:
        name, marketplace = plugin_id.split("@", 1)
        setting = configured.get(plugin_id)
        base = cache_root / marketplace / name
        if not isinstance(setting, dict) or setting.get("enabled") is not True or not base.is_dir():
            missing.append(plugin_id)
            continue

        local = base / "local"
        if local.is_dir():
            source_path = local
            version = "local"
        else:
            candidates = [path for path in base.iterdir() if path.is_dir()]
            if not candidates:
                missing.append(plugin_id)
                continue
            source_path = max(candidates, key=lambda path: (path.stat().st_mtime_ns, path.name))
            version = source_path.name

        records.append(
            PluginRecord(
                plugin_id=plugin_id,
                name=name,
                marketplace=marketplace,
                version=version,
                source_path=source_path,
            )
        )

    if missing:
        raise RuntimeError("Plugin dự phòng thiếu/chưa bật/cache không tồn tại: " + ", ".join(missing))
    return records


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
    """Ưu tiên CLI chính thức; hạ xuống cache Codex; cuối cùng hạ xuống cache Claude Code
    trực tiếp khi máy không cài Codex ở bất kỳ dạng nào (vd phiên Cloud)."""

    try:
        return select_plugins(read_installed_plugins())
    except RuntimeError as cli_error:
        try:
            records = read_configured_plugins_from_cache()
            print(
                "CẢNH BÁO: Codex CLI không liệt kê được marketplace; "
                f"đã đối chiếu config+cache cục bộ ({cli_error}).",
                file=sys.stderr,
            )
            return records
        except RuntimeError as codex_cache_error:
            records = read_claude_code_cache_plugins()
            print(
                "CẢNH BÁO: Không có Codex CLI lẫn cấu hình/cache Codex; "
                f"đã đọc thẳng cache Claude Code ({codex_cache_error}).",
                file=sys.stderr,
            )
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
