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

# --- Ép stdout sang UTF-8 (vá 05/08/2026) ---------------------------------
# Windows mặc định stdout=cp1252 → mọi print() tiếng Việt làm script chết giữa
# chừng bằng UnicodeEncodeError, trong khi phần việc chính đã chạy xong. Ép ở
# đây thay vì bắt người dùng nhớ đặt PYTHONIOENCODING trước mỗi lệnh.
import sys as _sys

for _luong in (_sys.stdout, _sys.stderr):
    if _luong is not None and (getattr(_luong, "encoding", "") or "").lower().replace("-", "") != "utf8":
        try:
            _luong.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass          # luồng bị chuyển hướng kiểu không reconfigure được — bỏ qua
# --------------------------------------------------------------------------

import datetime
import json
import os
import platform
import re
from pathlib import Path

HOME = Path.home()
REPO = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "catalog_raw.json"
# Bản chụp DÙNG CHUNG giữa các máy: chỉ giữ phần độc lập với máy (bỏ đường dẫn tuyệt
# đối), nhờ vậy track được Git và build_danh_muc.py gộp được danh mục của cả Mac lẫn
# Windows. Bác sĩ cài bộ plugin KHÁC NHAU trên hai máy (03/08/2026: chung 137 mục,
# riêng Mac 1405, riêng Windows 293) nên một danh mục một máy luôn sai một nửa.
SNAP_DIR = Path(__file__).resolve().parent / "catalog_may"


def ten_may() -> str:
    """Nhãn máy — lấy theo HỆ ĐIỀU HÀNH, cố ý KHÔNG dùng tên máy thật (tên máy hay
    kèm tên người, không nên đẩy lên Git)."""
    return {"Darwin": "Mac", "Windows": "Windows"}.get(platform.system(),
                                                       platform.system() or "Khac")


# Các NHÓM NGUỒN mà bản công cụ này biết quét. Ghi thẳng vào bản chụp để
# build_danh_muc.py phân biệt được "máy kia không có mục này" với "máy kia quét
# bằng bản công cụ cũ, chưa biết nhóm này" — hai chuyện dẫn tới hai kết luận
# ngược nhau khi bác sĩ đọc danh mục.
NHOM_NGUON = ("plugin-cli", "claude.ai", "user-skills", "user-commands",
              "cowork", "ebm-agents")


def nhom_cua(source: str) -> str:
    """Nhóm nguồn của một mục. Plugin cài qua CLI có source riêng theo từng
    marketplace nên gom hết về 'plugin-cli'."""
    return source if source in NHOM_NGUON else "plugin-cli"


def ghi_ban_chung(items: list[dict]) -> Path:
    """Ghi bản chụp danh mục của máy đang chạy, đã bỏ đường dẫn tuyệt đối."""
    SNAP_DIR.mkdir(exist_ok=True)
    f = SNAP_DIR / f"{ten_may()}.json"
    f.write_text(json.dumps({
        "may": ten_may(),
        "ngay_quet": datetime.date.today().isoformat(),
        "nhom_da_quet": list(NHOM_NGUON),
        "muc": [{k: v for k, v in i.items() if k != "path"} for i in items],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return f


def tim_app_support() -> Path:
    """Thư mục plugin của Claude Desktop (nhóm claude.ai) — mỗi hệ điều hành một nơi.

    Trước 03/08/2026 chỉ có đường dẫn macOS viết cứng, nên chạy trên Windows là
    IM LẶNG bỏ qua toàn bộ plugin claude.ai (bác sĩ dùng cả 2 máy qua OneDrive):
    rglob trên thư mục không tồn tại trả về rỗng, không báo lỗi.
    """
    ung_vien = [
        HOME / "Library/Application Support/Claude/local-agent-mode-sessions",   # macOS
        Path(os.environ.get("APPDATA") or HOME / "AppData/Roaming")
        / "Claude/local-agent-mode-sessions",                                    # Windows
        HOME / ".config/Claude/local-agent-mode-sessions",                       # Linux
    ]
    for p in ung_vien:
        if p.is_dir():
            return p
    return ung_vien[0]


APP_SUPPORT = tim_app_support()

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
    "medsci": 1,
    "aipoch": 1,                     # kho aipoch: 603 skill nghiên cứu y khoa/khoa học
    "healthcare": 1,
    "bio-research": 1,
    "user-skills": 1,
    "user-commands": 1,
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

# Hai bảng dưới khớp CHÍNH XÁC tên plugin, không khớp chuỗi con như TIER3_HINTS.
# Lý do: tên ngắn kiểu "data"/"legal" nếu khớp chuỗi con sẽ nuốt nhầm plugin y khoa
# ("medsci-data" 58 mục thành Tầng 3). Bổ sung 03/08/2026 sau khi soi máy Windows —
# hai bảng cũ chỉ dựng theo bộ plugin trên Mac nên bỏ trắng toàn bộ nhóm claude.ai.
TIER1_PLUGINS = {
    "pubmed", "icd10-codes", "clinical-trials", "clinical-trial-protocol",
    "consensus", "biorxiv", "scientific-problem-selection",
}
TIER3_PLUGINS = {
    "zoom-plugin", "small-business", "bigdata-com", "brightdata-plugin", "figma",
    "ip-legal", "ai-governance-legal", "product-legal", "legal", "finance",
    "marketing", "human-resources", "product-management", "operations", "design",
    "productivity", "enterprise-search", "hubspot", "sentry", "snowflake",
    "datadog", "linear", "notion", "claude-for-msft-365-install",
}


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
    if plugin in TIER1_PLUGINS:        # khớp đúng tên → xét trước mọi luật chuỗi con
        return 1
    if plugin in TIER3_PLUGINS:
        return 3
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
        # Marketplace kiểu "directory": plugin cài từ một thư mục trên máy. Khi cache
        # chưa được dựng, installPath chưa tồn tại — nhưng NGUỒN thì có, và cache sẽ
        # được sao ra từ nguồn. Dịch vào nguồn để bản dịch đi theo lúc cache sinh ra.
        nguon_thu_muc: dict[str, Path] = {}
        # Plugin ĐÃ CÀI nhưng ĐANG TẮT vẫn nằm trong installed_plugins.json. Trước
        # 05/08/2026 danh mục liệt kê cả chúng → mời gọi những lệnh gõ vào là không
        # chạy. Lộ ra khi tắt 8/9 plugin medsci-* (9 plugin đó chứa BỘ SKILL Y HỆT
        # NHAU — đã so md5 byte-identical — nên 522 mục chỉ là 59 skill nhân bản).
        # Chỉ loại khi settings ghi rõ false; vắng mặt thì GIỮ, để bản vá này không
        # âm thầm làm rỗng danh mục trên máy cấu hình theo kiểu khác.
        tat_ro_rang: set[str] = set()
        st = HOME / ".claude/settings.json"
        if st.exists():
            try:
                cfg = json.loads(st.read_text(encoding="utf-8"))
                for mp, v in (cfg.get("extraKnownMarketplaces") or {}).items():
                    src = (v or {}).get("source") or {}
                    if src.get("source") == "directory" and src.get("path"):
                        nguon_thu_muc[mp] = Path(src["path"])
                for k, bat in (cfg.get("enabledPlugins") or {}).items():
                    if bat is False:
                        tat_ro_rang.add(k)
            except (OSError, json.JSONDecodeError):
                pass

        for key, entries in data.get("plugins", {}).items():
            if key in tat_ro_rang:
                continue
            plugin, _, mktp = key.partition("@")
            root = Path(entries[0]["installPath"])
            if not root.exists():
                thay_the = nguon_thu_muc.get(mktp)
                if thay_the and thay_the.exists():
                    root = thay_the          # quét thẳng nguồn
                else:
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

    # --- 2b. Lệnh tiếng Việt cấp user (~/.claude/commands) -----------------
    # Bộ lệnh do chính bác sĩ soạn (nguồn ở sync/commands-vi, chép sang bằng
    # copy-commands-vi.*). Trước 03/08/2026 danh mục KHÔNG quét nhóm này, nên bảng
    # tra nhanh mời gọi /tra-ma-icd10, /khu-dinh-danh… mà chúng không nằm trong
    # danh mục nào để đối chiếu — không biết máy nào có, máy nào không.
    for f in sorted((HOME / ".claude/commands").glob("*.md")):
        fm = read_frontmatter(f)
        nm = fm.get("name") or f.stem
        add(items, kind="command", source="user-commands", plugin="", name=nm,
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
    print(f"→ bản chụp dùng chung ({ten_may()}): {ghi_ban_chung(items)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
