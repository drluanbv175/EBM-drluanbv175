#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_vi.py — Việt hoá dòng MÔ TẢ hiện ra khi bác sĩ gõ `/` để gọi skill/lệnh/agent.

Dòng đó chính là trường `description:` trong YAML frontmatter của SKILL.md /
commands/*.md / agents/*.md. Script thay nó bằng bản tiếng Việt trong
`vi_descriptions.json`, và LƯU bản gốc vào `description-en:` ngay trong frontmatter.

Ba tính chất bắt buộc (vì file plugin bị ghi đè mỗi lần cập nhật):
  1. IDEMPOTENT — chạy lại bao nhiêu lần cũng ra cùng kết quả.
  2. KHÔI PHỤC ĐƯỢC — `--restore` trả mọi mô tả về nguyên bản tiếng Anh.
  3. KHÔNG IM LẶNG BỎ SÓT — khi plugin cập nhật làm đổi mô tả gốc, script
     BÁO ĐỘNG (mô tả tiếng Việt có thể đã lỗi thời) thay vì âm thầm giữ bản cũ;
     mục mới chưa có bản dịch cũng được liệt kê ra.

Cách dùng:
    python3 tools/vietnamize/apply_vi.py --dry-run    # xem trước, không ghi
    python3 tools/vietnamize/apply_vi.py              # áp bản dịch
    python3 tools/vietnamize/apply_vi.py --restore    # trả về tiếng Anh gốc
    python3 tools/vietnamize/apply_vi.py --report     # chỉ báo cáo độ phủ

CHẠY LẠI SAU MỖI LẦN CẬP NHẬT/CÀI THÊM PLUGIN — bản dịch nằm trong thư mục
cài đặt có số phiên bản nên sẽ mất khi plugin lên bản mới.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOG = HERE / "catalog_raw.json"
DICT = HERE / "vi_descriptions.json"

FM_KEY = re.compile(r"^([a-zA-Z_][\w-]*):", re.MULTILINE)


def digest(text: str) -> str:
    """Vân tay của mô tả gốc — để phát hiện plugin đã đổi mô tả sau khi ta dịch."""
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()[:16]


def split_frontmatter(text: str) -> tuple[str, str] | None:
    """Tách (khối frontmatter, phần thân). Trả None nếu file không có frontmatter."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    return text[3:end], text[end:]


def read_field(block: str, key: str) -> str | None:
    """Đọc một trường phẳng trong frontmatter, gộp cả phần xuống dòng thụt đầu."""
    lines = block.splitlines()
    for i, line in enumerate(lines):
        m = re.match(rf"^{re.escape(key)}:\s*(.*)$", line)
        if not m:
            continue
        buf = [m.group(1)]
        for nxt in lines[i + 1:]:
            if re.match(r"^[a-zA-Z_][\w-]*:", nxt) or nxt.startswith("---"):
                break
            if nxt.strip():
                buf.append(nxt.strip())
        val = " ".join(buf).strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "'\"":
            # Chuỗi nháy kép có thể chứa escape (\" bên trong mô tả). Phải GIẢI MÃ,
            # không được bóc nháy thô: bóc thô làm dấu escape nhân đôi sau mỗi lần
            # ghi lại, hỏng dần bản mô tả gốc tiếng Anh.
            if val[0] == '"':
                try:
                    return json.loads(val)
                except json.JSONDecodeError:
                    pass
            val = val[1:-1]
        return val
    return None


def replace_field(block: str, key: str, value: str) -> str:
    """Thay (hoặc thêm) một trường, ghi ở dạng chuỗi nháy kép hợp lệ YAML.

    Dùng json.dumps vì JSON là tập con của YAML → an toàn với dấu tiếng Việt,
    dấu hai chấm, dấu ngoặc trong mô tả.
    """
    encoded = json.dumps(value, ensure_ascii=False)
    lines = block.splitlines()
    out: list[str] = []
    i = 0
    replaced = False
    while i < len(lines):
        line = lines[i]
        if re.match(rf"^{re.escape(key)}:\s*", line):
            out.append(f"{key}: {encoded}")
            i += 1
            # nuốt phần tiếp nối (dòng thụt đầu) của trường cũ
            while i < len(lines) and not re.match(r"^[a-zA-Z_][\w-]*:", lines[i]) \
                    and lines[i].strip():
                i += 1
            replaced = True
            continue
        out.append(line)
        i += 1
    if not replaced:
        # chèn ngay sau `name:` nếu có, để frontmatter dễ đọc
        for idx, line in enumerate(out):
            if line.startswith("name:"):
                out.insert(idx + 1, f"{key}: {encoded}")
                break
        else:
            out.append(f"{key}: {encoded}")
    return "\n".join(out)


def process(item: dict, vi_entry: dict, *, restore: bool, dry: bool) -> str:
    """Trả về mã kết quả: applied | already | restored | nothing | skip-* | STALE."""
    path = Path(item["path"])
    if not path.exists():
        return "skip-missing"

    text = path.read_text(encoding="utf-8", errors="replace")
    parts = split_frontmatter(text)
    if parts is None:
        return "skip-nofrontmatter"
    block, body = parts

    cur_desc = read_field(block, "description") or ""
    saved_en = read_field(block, "description-en")

    if restore:
        # CHỈ khôi phục file do CHÍNH công cụ này sửa — nhận biết bằng vân tay
        # `description-src`. Không được dựa vào sự có mặt của `description-en`:
        # một số plugin (claude-code-harness) dùng chính tên trường đó cho cơ chế
        # đa ngữ riêng của họ, và bản vá này ra đời sau khi `--restore` lỡ xoá
        # trường ấy ở 39 skill của harness (2026-08-01).
        if saved_en is None or read_field(block, "description-src") is None:
            return "nothing"
        nb = replace_field(block, "description", saved_en)
        nb = "\n".join(l for l in nb.splitlines()
                       if not l.startswith("description-en:")
                       and not l.startswith("description-src:"))
        if not dry:
            path.write_text("---" + nb + body, encoding="utf-8")
        return "restored"

    vi = vi_entry.get("vi", "").strip()
    if not vi:
        return "no-translation"

    original_en = saved_en if saved_en is not None else cur_desc
    src_hash = read_field(block, "description-src")

    # Plugin đã cập nhật và đổi mô tả gốc → bản dịch có thể lỗi thời.
    stale = bool(src_hash) and src_hash != digest(original_en)

    if cur_desc == vi and saved_en is not None and not stale:
        return "already"

    nb = replace_field(block, "description", vi)
    nb = replace_field(nb, "description-en", original_en)
    nb = replace_field(nb, "description-src", digest(original_en))

    if not dry:
        bak = path.with_suffix(path.suffix + ".vi-bak")
        if not bak.exists():
            shutil.copy2(path, bak)
        path.write_text("---" + nb + body, encoding="utf-8")
    return "STALE" if stale else "applied"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="xem trước, không ghi")
    ap.add_argument("--restore", action="store_true", help="trả mô tả về tiếng Anh gốc")
    ap.add_argument("--report", action="store_true", help="chỉ báo cáo độ phủ")
    ap.add_argument("--tier", type=int, default=0, help="chỉ xử lý một tầng (1/2/3)")
    args = ap.parse_args()

    if not CATALOG.exists():
        print("✗ Chưa có catalog_raw.json — chạy extract_catalog.py trước.")
        return 1
    items = json.loads(CATALOG.read_text(encoding="utf-8"))
    vi_map = json.loads(DICT.read_text(encoding="utf-8")) if DICT.exists() else {}

    if args.report:
        for tier in (1, 2, 3):
            sub = [i for i in items if i["tier_guess"] == tier]
            have = sum(1 for i in sub if i["id"] in vi_map or i["already_vi"])
            print(f"  Tầng {tier}: {have}/{len(sub)} mục đã có mô tả tiếng Việt")
        missing = [i for i in items
                   if i["tier_guess"] <= 2 and i["id"] not in vi_map and not i["already_vi"]]
        print(f"\nTầng 1-2 CÒN THIẾU bản dịch: {len(missing)}")
        for i in missing[:15]:
            print(f"   - {i['id']}")
        if len(missing) > 15:
            print(f"   … và {len(missing)-15} mục nữa")
        return 0

    counts: dict[str, int] = {}
    stale_ids: list[str] = []
    for item in items:
        if args.tier and item["tier_guess"] != args.tier:
            continue
        entry = vi_map.get(item["id"], {})
        if not entry and not args.restore:
            continue
        res = process(item, entry, restore=args.restore, dry=args.dry_run)
        counts[res] = counts.get(res, 0) + 1
        if res == "STALE":
            stale_ids.append(item["id"])

    mode = "XEM TRƯỚC (chưa ghi gì)" if args.dry_run else "ĐÃ GHI"
    print(f"=== {mode} ===")
    for k, v in sorted(counts.items()):
        print(f"  {k:20s}: {v}")
    if stale_ids:
        print("\n⚠ Mô tả GỐC đã đổi sau lần dịch trước (plugin cập nhật) —"
              " cần xem lại bản tiếng Việt:")
        for i in stale_ids:
            print(f"   - {i}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
