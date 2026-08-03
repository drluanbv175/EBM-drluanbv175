#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bo_dau.py — Chuyển mô tả sang tiếng Việt KHÔNG DẤU cho phần hiển thị khi gõ `/`.

CHỈ DÙNG KHI giao diện danh sách lệnh không vẽ được chữ Việt có dấu (ô vuông, ký tự
lạ, mất dấu, chữ chồng lấn). Đây là bước LÙI về ASCII thuần — chắc chắn hiển thị đúng
ở mọi font, đổi lại đọc kém hơn. Đừng chạy nếu font hiển thị bình thường.

Phạm vi CỐ Ý HẸP: chỉ đụng trường `description` (dòng hiện khi gõ `/`) và `mo_ta` của
bộ lệnh. KHÔNG đụng:
  - thân skill (nội dung hướng dẫn Claude đọc — có dấu vẫn tốt hơn)
  - `description-en` (bản gốc tiếng Anh, phải giữ nguyên vẹn)
  - file tài liệu, danh mục, CLAUDE.md (bác sĩ đọc bằng trình soạn thảo, không lỗi)

Hoàn tác: `apply_vi.py --restore` trả mô tả về tiếng Anh, rồi chạy lại `apply_vi.py`
với từ điển có dấu.

Chạy:  python3 tools/vietnamize/bo_dau.py --dry-run    # xem trước
       python3 tools/vietnamize/bo_dau.py              # ghi thật
"""
from __future__ import annotations

import json
import pathlib
import sys
import unicodedata as ud

HERE = pathlib.Path(__file__).resolve().parent
TU_DIEN = HERE / "vi_descriptions.json"
LENH = HERE / "lenh_viet.json"

# Ký tự đặc biệt hay mất glyph → thay bằng ASCII tương đương
THAY = {
    "—": "-", "–": "-", "…": "...", "→": "->", "↔": "<->",
    "·": "*", "≥": ">=", "≤": "<=", "×": "x", "≠": "!=",
    "“": '"', "”": '"', "‘": "'", "’": "'",
    "₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4",
    "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4",
}


def bo_dau(s: str) -> str:
    """Bỏ dấu tiếng Việt, giữ nguyên chữ và số. đ/Đ phải xử lý riêng vì
    KHÔNG phải là 'd' + dấu tổ hợp — tách NFD không chạm tới nó."""
    for a, b in THAY.items():
        s = s.replace(a, b)
    s = s.replace("đ", "d").replace("Đ", "D")
    s = ud.normalize("NFD", s)
    s = "".join(c for c in s if not ud.combining(c))
    return ud.normalize("NFC", s)


def main() -> int:
    dry = "--dry-run" in sys.argv
    doi = 0

    d = json.loads(TU_DIEN.read_text("utf-8"))
    for k, v in d.items():
        if k.startswith("_"):
            continue
        moi = bo_dau(v["vi"])
        if moi != v["vi"]:
            doi += 1
            if doi <= 3:
                print(f"  {k}\n    trước: {v['vi'][:88]}\n    sau  : {moi[:88]}")
            v["vi"] = moi
    if not dry:
        TU_DIEN.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")

    l = json.loads(LENH.read_text("utf-8"))
    doi_l = 0
    for k, v in l.items():
        if k.startswith("_"):
            continue
        moi = bo_dau(v["mo_ta"])
        if moi != v["mo_ta"]:
            doi_l += 1
            v["mo_ta"] = moi
    if not dry:
        LENH.write_text(json.dumps(l, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n{'(XEM TRƯỚC) ' if dry else ''}Đổi {doi} mô tả skill + {doi_l} mô tả lệnh.")
    if not dry:
        print("Chạy tiếp: apply_vi.py  →  sinh_lenh_viet.py  →  copy-commands-vi.sh")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
