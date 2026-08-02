#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_plugin_health.py — Soi SỨC KHOẺ mọi plugin đã cài, không chỉ đếm số lượng.

Ra đời sau sự cố medsci-skills (02/08/2026): skill nạp được, hiện đủ trong danh sách
khi gõ `/`, nhưng MỌI lệnh bên trong đều gãy vì chúng gọi nhau qua
`${MEDSCI_SKILLS_ROOT:-$HOME/workspace/medsci-skills}` — một thư mục không tồn tại
trên máy. Loại lỗi này không lộ ra ở bất kỳ phép đếm nào; chỉ lộ khi thật sự chạy.

Soi 4 nhóm:
  N1  Đường dẫn cài không tồn tại (plugin đã khai nhưng file biến mất)
  N2  Skill trỏ tới thư mục gốc NGOÀI nơi cài — dạng $HOME/... hoặc ~/... cứng
      trong lệnh; kiểm luôn thư mục đó có thật không
  N3  Công cụ ngoài mà skill gọi (Rscript, node, pandoc, quarto, soffice…) chưa có
      trên máy → skill chạy tới đó là dừng
  N4  Skill không có frontmatter description → không hiện khi gõ `/`

Chạy: python3 tools/check_plugin_health.py
Mã thoát 0 = không có lỗi chặn (N1/N2), 1 = có.
"""
from __future__ import annotations

import collections
import json
import pathlib
import re
import shutil
import sys

HOME = pathlib.Path.home()
SKIP_DIRS = {"node_modules", ".git", "dist", "build", "__pycache__", "test", "tests",
             "fixtures", "examples", ".venv", "venv", "demo"}

# Lệnh gọi công cụ ngoài — chỉ nhận khi đứng đầu dòng lệnh trong khối mã
CONG_CU = ["Rscript", "node", "npx", "pandoc", "quarto", "soffice", "latexmk",
           "pdflatex", "dot", "ffmpeg"]
# CHỈ bắt đường dẫn được dùng làm GỐC ĐỂ GỌI SCRIPT — đúng loại lỗi của medsci:
#     "${MEDSCI_SKILLS_ROOT:-$HOME/workspace/medsci-skills}/skills/..."
# Bắt rộng hơn sẽ toàn báo động giả: ~/.bashrc, ~/.pyenv, ~/.cache/... là đường dẫn
# tuỳ chọn hoặc thư mục cache tự tạo lúc chạy, không phải hỏng hóc.
DUONG_DAN = re.compile(
    r"\$\{[A-Z_]+:-((?:\$HOME|~)/[A-Za-z0-9_./-]+)\}"          # biến có giá trị mặc định
    r"|((?:\$HOME|~)/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*)(?=/(?:skills|scripts)/)"
)


def nap_plugin() -> list[tuple[str, pathlib.Path]]:
    """Danh sách (tên, thư mục cài) của mọi plugin đã đăng ký."""
    ds: list[tuple[str, pathlib.Path]] = []
    reg = HOME / ".claude/plugins/installed_plugins.json"
    if reg.exists():
        data = json.loads(reg.read_text("utf-8"))
        for key, entries in data.get("plugins", {}).items():
            ds.append((key, pathlib.Path(entries[0]["installPath"])))
    app = HOME / "Library/Application Support/Claude/local-agent-mode-sessions"
    for mf in app.rglob("rpm/manifest.json"):
        try:
            data = json.loads(mf.read_text("utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for p in data.get("plugins", []):
            if p.get("id"):
                ds.append((f"{p.get('name','?')} (claude.ai)", mf.parent / p["id"]))
    return ds


def main() -> int:
    loi: dict[str, list[str]] = collections.defaultdict(list)
    canh_bao: dict[str, list[str]] = collections.defaultdict(list)
    thieu_cong_cu: dict[str, set[str]] = collections.defaultdict(set)
    co_san = {c: shutil.which(c) is not None for c in CONG_CU}

    ds = nap_plugin()
    print(f"Soi {len(ds)} plugin đã đăng ký.\n")

    for ten, goc in ds:
        if not goc.exists():
            loi["N1 đường dẫn cài không tồn tại"].append(f"{ten} → {goc}")
            continue
        so_skill = 0
        goc_ngoai: set[str] = set()
        for f in goc.rglob("*.md"):
            if any(x in SKIP_DIRS for x in f.parts):
                continue
            la_skill = f.name == "SKILL.md"
            if la_skill:
                so_skill += 1
            try:
                t = f.read_text("utf-8", errors="replace")
            except OSError:
                continue
            if la_skill and not re.search(r"^description[:-]", t[:2000], re.M):
                canh_bao["N4 skill không có mô tả"].append(f"{ten}: {f.parent.name}")
            for m in DUONG_DAN.finditer(t):
                raw = m.group(1) or m.group(2)
                if not raw:
                    continue
                d = raw.replace("$HOME", str(HOME)).replace("~", str(HOME), 1)
                p = pathlib.Path(d)
                # chỉ tính đường dẫn nằm NGOÀI thư mục cài của chính plugin
                if str(goc) in str(p) or p.exists():
                    continue
                # Thư mục cache / dữ liệu do chính phần mềm tạo lúc chạy lần đầu
                # (~/.cache/huggingface, ~/.claude/data/...) — vắng mặt là bình thường.
                if re.search(r"/\.?cache/|/data/|/\.claude/data\b", raw):
                    continue
                if m.group(1):
                    # Dạng ${VAR:-đường-dẫn}: plugin DÙNG nó để gọi script của chính
                    # mình → thư mục không tồn tại nghĩa là skill sẽ gãy khi chạy.
                    goc_ngoai.add(raw)
                else:
                    # Đường dẫn trần: hầu hết là hướng dẫn cài cho công cụ KHÁC
                    # (~/.cursor, ~/.grok, ~/.config/opencode) — không phải hỏng.
                    canh_bao["N2b đường dẫn của công cụ khác (không phải lỗi)"].append(
                        f"{ten}: {raw}")
            for c in CONG_CU:
                if re.search(rf"(?<![\w/-]){re.escape(c)}\s+[-\w]", t) and not co_san[c]:
                    thieu_cong_cu[ten].add(c)
        if goc_ngoai:
            loi["N2 trỏ tới thư mục KHÔNG TỒN TẠI ngoài nơi cài"].append(
                f"{ten} ({so_skill} skill): " + ", ".join(sorted(goc_ngoai)[:3]))

    chan = 0
    for nhan in sorted(loi):
        print(f"  ✗ {nhan}: {len(loi[nhan])}")
        for x in loi[nhan][:8]:
            print(f"      - {x}")
        chan += len(loi[nhan])
    for nhan in sorted(canh_bao):
        print(f"  ⚠ {nhan}: {len(canh_bao[nhan])}")
        for x in canh_bao[nhan][:5]:
            print(f"      - {x}")
    if thieu_cong_cu:
        print(f"  ⚠ N3 công cụ ngoài chưa có trên máy — skill chạy tới đó sẽ dừng:")
        for ten, cs in sorted(thieu_cong_cu.items()):
            print(f"      - {ten}: {', '.join(sorted(cs))}")
    if not loi and not canh_bao and not thieu_cong_cu:
        print("  ✓ Không phát hiện vấn đề nào.")
    print(f"\nLỗi CHẶN (N1/N2): {chan}")
    return 1 if chan else 0


if __name__ == "__main__":
    sys.exit(main())
