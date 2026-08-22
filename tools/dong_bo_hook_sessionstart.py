#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ĐỒNG BỘ HOOK SessionStart — đưa cơ chế TỰ ĐỘNG đi được sang máy kia.

VÌ SAO CÓ (21/08/2026). Toàn bộ tính «tự động» của hệ nằm ở hook `SessionStart`:
7 chốt chạy mỗi phiên (chot_hoi_quy_bai_hoc · dong_bo_skill · kiem_do_tuoi_chung_cu
· kiem_nguon_that · kiem_plugin_day_du · tu_khoi_dong · tu_sua_chua). Nhưng hook
được khai trong `.claude/settings.json`, mà `.gitignore` loại trừ `/.claude/*`
(chỉ giữ `agents/`). Hệ quả: **bản khai hook không tồn tại ở đâu trong git** — máy
Windows muốn có cùng cơ chế thì phải gõ lại bằng tay, và không có bản nguồn nào để
đối chiếu xem hai máy còn khớp không. Đây là chỗ hở lớn nhất của chữ «tự động»:
mọi thứ khác (skill · agent · plugin · bộ nhớ · lệnh tiếng Việt) đều đã có đường đi.

CÔNG CỤ NÀY KHÔNG TỰ VIẾT HOOK. Nó XUẤT từ máy đang chạy đúng ra thành bản nguồn
trong git, rồi CÀI bản nguồn đó sang máy kia. Lý do là nguyên tắc nền của kho: bản
khai hook thật chỉ máy đó mới biết; một bản do công cụ soạn theo trí nhớ tài liệu
sẽ sai cờ, sai đường dẫn, và hỏng im lặng — đúng họ lỗi mà `.githooks/pre-commit`
sinh ra để chặn.

Theo đúng khuôn `sync/copy-claude-md.sh` đã dùng cho `~/.claude/CLAUDE.md`: CHÉP
chứ không liên kết. Hook là cấu hình nền — nếu nó là symlink trỏ vào cây đồng bộ
mà file chưa tải về thì Claude Code mất hook một cách IM LẶNG.

    python3 tools/dong_bo_hook_sessionstart.py --xuat      # máy đang đúng → git
    python3 tools/dong_bo_hook_sessionstart.py             # đối chiếu, chỉ đọc
    python3 tools/dong_bo_hook_sessionstart.py --ap-dung   # git → máy này (có sao lưu)

Mã thoát: 0 khớp · 1 lệch/chưa có nguồn · 2 không ghi được.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
NGUON = REPO / "sync/hooks-sessionstart.json"
PHAM_VI = {
    "du-an": REPO / ".claude/settings.json",
    "nguoi-dung": Path.home() / ".claude/settings.json",
}


def doc_json(p: Path) -> dict:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def lay_hook(cai_dat: dict) -> list:
    """Rút đúng khối SessionStart, không đụng phần còn lại của settings."""
    return (cai_dat.get("hooks") or {}).get("SessionStart") or []


def xuat(dich_pham_vi: str) -> int:
    """Chụp khối SessionStart của máy này thành bản nguồn trong git."""
    p = PHAM_VI[dich_pham_vi]
    hook = lay_hook(doc_json(p))
    if not hook:
        print(f"✗ Máy này không có hook SessionStart ở {p} — không có gì để xuất.",
              file=sys.stderr)
        print("  Chạy `--xuat` trên MÁY ĐANG CHẠY ĐÚNG (thường là Mac).", file=sys.stderr)
        return 1
    NGUON.parent.mkdir(parents=True, exist_ok=True)
    NGUON.write_text(json.dumps({
        "_ghi_chu": (
            "BẢN NGUỒN của hook SessionStart — chép từ máy đang chạy đúng bằng "
            "`python3 tools/dong_bo_hook_sessionstart.py --xuat`, KHÔNG soạn tay. "
            "Máy kia cài bằng `--ap-dung`. File này tồn tại vì .gitignore loại trừ "
            ".claude/settings.json, nên trước 21/08/2026 cơ chế tự động của hệ "
            "không có đường nào đi sang máy thứ hai."),
        "_pham_vi": dich_pham_vi,
        "_xuat_luc": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "SessionStart": hook,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    lenh = sum(len(m.get("hooks") or []) for m in hook)
    print(f"✓ Đã xuất {lenh} lệnh hook SessionStart ({dich_pham_vi}) → {NGUON}")
    print("  Commit file này để máy kia dùng được.")
    return 0


def ap_dung(dich_pham_vi: str, that: bool) -> int:
    """Cài bản nguồn vào settings của máy này; chỉ chạm khoá hooks.SessionStart."""
    nguon = doc_json(NGUON)
    muon = nguon.get("SessionStart")
    if not muon:
        print(f"✗ Chưa có bản nguồn {NGUON} — chạy `--xuat` trên máy đang chạy đúng.",
              file=sys.stderr)
        return 1

    p = PHAM_VI[dich_pham_vi]
    hien = doc_json(p)
    dang_co = lay_hook(hien)
    if dang_co == muon:
        print(f"✓ Hook SessionStart đã khớp bản nguồn ({dich_pham_vi}).")
        return 0

    if not that:
        print(f"⚠ Hook SessionStart LỆCH bản nguồn ({dich_pham_vi}):")
        print(f"    máy này: {sum(len(m.get('hooks') or []) for m in dang_co)} lệnh")
        print(f"    nguồn  : {sum(len(m.get('hooks') or []) for m in muon)} lệnh")
        print("  Thêm --ap-dung để cài bản nguồn (sẽ sao lưu settings hiện tại).")
        return 1

    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.exists():
            luu = p.with_name(f"{p.name}.bak-{dt.datetime.now():%Y%m%d-%H%M%S}")
            shutil.copy2(p, luu)
            print(f"  (đã sao lưu {luu.name})")
        # Chỉ ghi đè đúng một khoá. Settings còn giữ permissions, env,
        # skillListingBudgetFraction… — đè cả file là xoá cấu hình riêng của máy.
        hien.setdefault("hooks", {})["SessionStart"] = muon
        p.write_text(json.dumps(hien, ensure_ascii=False, indent=2) + "\n",
                     encoding="utf-8", newline="\n")
    except OSError as exc:
        print(f"✗ Không ghi được {p}: {exc}", file=sys.stderr)
        return 2
    print(f"✓ Đã cài hook SessionStart vào {p}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Đồng bộ hook SessionStart giữa hai máy")
    ap.add_argument("--xuat", action="store_true", help="máy này → bản nguồn trong git")
    ap.add_argument("--ap-dung", action="store_true", help="bản nguồn → máy này (có sao lưu)")
    ap.add_argument("--pham-vi", choices=sorted(PHAM_VI), default="du-an",
                    help="settings dự án (mặc định) hay của người dùng")
    a = ap.parse_args()
    if a.xuat:
        return xuat(a.pham_vi)
    return ap_dung(a.pham_vi, a.ap_dung)


if __name__ == "__main__":
    raise SystemExit(main())
