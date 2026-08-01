#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_catalog.py — Trích DANH MỤC mọi thứ có thể gọi được trong Claude Code trên máy này.

Quét 4 nguồn thật (không đoán, không hardcode danh sách):
  1. Plugin đã cài  : đọc ~/.claude/plugins/installed_plugins.json rồi vào từng installPath
                      lấy skills/*/SKILL.md, commands/*.md, agents/*.md
  2. Skill cấp user : ~/.claude/skills/*/SKILL.md
  3. Skill Cowork   : ~/.claude-science/orgs/*/skills/*/SKILL.md
  4. Agent EBM      : <repo>/.claude/agents/*.md  (đã tiếng Việt sẵn)

Xuất catalog_raw.json gồm: mã mục, loại, nguồn, tên, mô tả gốc, đường dẫn file,
đã-có-tiếng-Việt-chưa, và tầng ưu tiên ĐỀ XUẤT (người duyệt lại, không tin máy).

KHÔNG sửa file nào — đây là bước đọc.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HOME = Path.home()
REPO = Path(__file__).resolve().parents[2]
APP_SUPPORT = HOME / "Library/Application Support/Claude/local-agent-mode-sessions"
OUT = Path(__file__).resolve().parent / "catalog_raw.json"

# Dấu tiếng Việt — dùng để nhận biết mô tả đã Việt hoá hay chưa
VN_CHARS = re.compile(
    r"[àáâãèéêìíòóôõùúýăđĩũơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]",
    re.IGNORECASE,
)

# Tầng ưu tiên đề xuất theo NGUỒN. Máy chỉ gợi ý; người duyệt lại trong bản dịch.
#   1 = phục vụ trực tiếp công việc y khoa/nghiên cứu của bác sĩ
#   2 = kỹ thuật, có thể cần khi sửa chính hệ EBM
#   3 = ngoài chuyên môn (trading, IoT, marketing...)
TIER_BY_SOURCE = {
    "openmed-skills": 1,
    "academic-research-skills": 1,
    "healthcare": 1,
    "bio-research": 1,
    "user-skills": 1,
    "cowork": 1,
    "ebm-agents": 1,
    "codex": 2,
    "claude-code-harness": 2,
    "understand-anything": 2,
    "mattpocock": 2,
    "bmad": 2,
    "humanizer": 2,
}
# Thư mục bỏ qua khi quét đệ quy — không phải mục gọi được
SKIP_DIRS = {"node_modules", ".git", "dist", "build", "__pycache__", "test", "tests",
             "fixtures", "examples", ".venv", "venv"}

TIER3_HINTS = (
    "neural-trader", "market-data", "iot-cognitum", "federation",
    "ruvllm", "ruvector", "agentdb", "rvf", "arena", "browser",
)


def read_frontmatter(path: Path) -> dict:
    """Đọc YAML frontmatter tối giản (name/description/argument-hint).

    Cố ý KHÔNG dùng thư viện YAML: chỉ cần vài trường phẳng, và phải chạy được
    trên máy chưa cài PyYAML.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end]

    out: dict[str, str] = {}
    key = None
    buf: list[str] = []
    for line in block.splitlines():
        m = re.match(r"^([a-zA-Z_][\w-]*):\s*(.*)$", line)
        if m and not line.startswith(" "):
            if key:
                out[key] = " ".join(buf).strip()
            key, first = m.group(1), m.group(2)
            buf = [first]
        elif key and (line.startswith(" ") or line.startswith("\t")):
            buf.append(line.strip())
        elif key and not line.strip():
            continue
    if key:
        out[key] = " ".join(buf).strip()

    for k, v in list(out.items()):
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
            v = v[1:-1]
        out[k] = v
    return out


def guess_tier(source: str, plugin: str) -> int:
    if any(h in plugin for h in TIER3_HINTS):
        return 3
    for key, tier in TIER_BY_SOURCE.items():
        if key in source or key in plugin:
            return tier
    if plugin.startswith("ruflo"):
        return 3
    return 2


def add(items: list, *, kind: str, source: str, plugin: str, name: str,
        desc: str, path: Path, invoke: str) -> None:
    items.append({
        "id": f"{kind}:{plugin or source}:{name}",
        "kind": kind,              # skill | command | agent
        "source": source,
        "plugin": plugin,
        "name": name,
        "invoke": invoke,          # cách gõ để gọi
        "desc_en": desc,
        "already_vi": bool(VN_CHARS.search(desc)),
        "tier_guess": guess_tier(source, plugin),
        "path": str(path),
    })


def main() -> int:
    items: list[dict] = []

    # --- 1. Plugin đã cài -------------------------------------------------
    reg = HOME / ".claude/plugins/installed_plugins.json"
    if reg.exists():
        data = json.loads(reg.read_text(encoding="utf-8"))
        for key, entries in data.get("plugins", {}).items():
            plugin = key.split("@")[0]
            root = Path(entries[0]["installPath"])
            if not root.exists():
                continue
            # Quét ĐỆ QUY, không cố định khuôn `skills/*/SKILL.md`: mỗi plugin bày
            # thư mục một kiểu — mattpocock lồng thêm cấp nhóm (`skills/engineering/
            # tdd/`), bmad để ở `src/core-skills/` và `web-bundles/`, humanizer đặt
            # SKILL.md ngay gốc. Khuôn cố định từng bỏ sót trọn 3 plugin này.
            for f in sorted(root.rglob("SKILL.md")):
                if any(p in SKIP_DIRS for p in f.parts):
                    continue
                fm = read_frontmatter(f)
                if not fm.get("description"):
                    continue                      # không có mô tả thì không phải mục gọi được
                nm = fm.get("name") or f.parent.name
                add(items, kind="skill", source=key, plugin=plugin, name=nm,
                    desc=fm["description"], path=f, invoke=f"/{plugin}:{nm}")
            for f in sorted(root.rglob("*.md")):
                if any(p in SKIP_DIRS for p in f.parts):
                    continue
                if f.parent.name == "commands":
                    fm = read_frontmatter(f)
                    if not fm.get("description"):
                        continue
                    add(items, kind="command", source=key, plugin=plugin,
                        name=f.stem, desc=fm["description"], path=f,
                        invoke=f"/{f.stem}")
                elif f.parent.name == "agents":
                    fm = read_frontmatter(f)
                    if not fm.get("description"):
                        continue
                    nm = fm.get("name") or f.stem
                    add(items, kind="agent", source=key, plugin=plugin, name=nm,
                        desc=fm["description"], path=f, invoke=f"agent {nm}")

    # --- 1b. Plugin từ claude.ai (Claude Desktop / local agent mode) -------
    # Nằm ở ~/Library/Application Support/Claude/local-agent-mode-sessions/.../rpm/
    # Trên đĩa có cả BẢN CŨ của những lần cập nhật trước (healthcare từng có 3 bản),
    # nên CHỈ lấy plugin_id đang khai trong manifest.json — bản đang thật sự dùng.
    for mf in sorted(APP_SUPPORT.rglob("rpm/manifest.json")):
        try:
            data = json.loads(mf.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for p in data.get("plugins", []):
            pid, ten = p.get("id"), p.get("name") or "?"
            if not pid:
                continue
            pdir = mf.parent / pid
            if not pdir.is_dir():
                continue
            # Quét CẢ skill, lệnh và agent — nhóm claude.ai cũng có agents/ và
            # commands/ (healthcare 3 agent, pdf-viewer 4 lệnh...), bản đầu chỉ lấy
            # SKILL.md nên bỏ sót 17 mục.
            for f in sorted(pdir.rglob("*.md")):
                if any(x in SKIP_DIRS for x in f.parts):
                    continue
                if f.name == "SKILL.md":
                    kind, invoke_fmt = "skill", "/{ten}:{nm}"
                elif f.parent.name == "commands":
                    kind, invoke_fmt = "command", "/{nm}"
                elif f.parent.name == "agents":
                    kind, invoke_fmt = "agent", "agent {nm}"
                else:
                    continue
                fm = read_frontmatter(f)
                if not fm.get("description"):
                    continue
                nm = fm.get("name") or (f.parent.name if kind == "skill" else f.stem)
                add(items, kind=kind, source="claude.ai", plugin=ten, name=nm,
                    desc=fm["description"], path=f,
                    invoke=invoke_fmt.format(ten=ten, nm=nm))

    # --- 2. Skill cấp user ------------------------------------------------
    for f in sorted((HOME / ".claude/skills").glob("*/SKILL.md")):
        fm = read_frontmatter(f)
        nm = fm.get("name") or f.parent.name
        add(items, kind="skill", source="user-skills", plugin="", name=nm,
            desc=fm.get("description", ""), path=f, invoke=f"/{nm}")

    # --- 3. Skill Cowork (claude-science) ---------------------------------
    for f in sorted((HOME / ".claude-science/orgs").glob("*/skills/*/SKILL.md")):
        fm = read_frontmatter(f)
        nm = fm.get("name") or f.parent.name
        add(items, kind="skill", source="cowork", plugin="anthropic-skills",
            name=nm, desc=fm.get("description", ""), path=f,
            invoke=f"/anthropic-skills:{nm}")

    # --- 4. Agent EBM của bác sĩ ------------------------------------------
    for f in sorted((REPO / ".claude/agents").glob("*.md")):
        if f.name.startswith("_") or f.name == "README.md":
            continue
        fm = read_frontmatter(f)
        nm = fm.get("name") or f.stem
        add(items, kind="agent", source="ebm-agents", plugin="", name=nm,
            desc=fm.get("description", ""), path=f, invoke=f"agent {nm}")

    OUT.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

    # --- Báo cáo ----------------------------------------------------------
    print(f"Tổng mục gọi được: {len(items)}")
    for kind in ("skill", "command", "agent"):
        sub = [i for i in items if i["kind"] == kind]
        vi = sum(1 for i in sub if i["already_vi"])
        print(f"  {kind:8s}: {len(sub):4d}  (đã có tiếng Việt: {vi})")
    print()
    for tier in (1, 2, 3):
        sub = [i for i in items if i["tier_guess"] == tier]
        vi = sum(1 for i in sub if i["already_vi"])
        print(f"  Tầng {tier}: {len(sub):4d} mục  — đã Việt {vi}, CÒN PHẢI DỊCH {len(sub)-vi}")
    empty = [i for i in items if not i["desc_en"].strip()]
    print(f"\nMục không có mô tả trong frontmatter: {len(empty)}")
    print(f"→ đã ghi: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
