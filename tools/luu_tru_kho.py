#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
luu_tru_kho.py — Lưu trữ TẤT CẢ kho git vào MỘT thư mục trong Claude AI, dạng file tĩnh.

VÌ SAO KHÔNG DỜI THẲNG THƯ MỤC `.git` VÀO OneDrive: bộ nhớ dự án ghi **9 sự cố**
OneDrive làm hỏng repo git, trong đó 2 lần phải cứu hộ ref hỏng (16/07 và 30/07/2026).
Chính CLAUDE.md đã kết luận: `git bundle` ghi ra **một file tĩnh, an toàn để OneDrive
đồng bộ, khác hẳn việc đồng bộ `.git` sống**. Script này làm đúng vậy.

Mỗi kho → một file `.bundle` trong `luu-tru-kho/`. File tĩnh nên OneDrive đồng bộ sạch
và sang được máy Windows; khôi phục lại thành repo đầy đủ bằng một lệnh clone.

HAI BẪY ĐÃ TRẢ GIÁ, script đã xử:
  1. **Shallow clone cho ra bundle VÔ DỤNG.** Kho aipoch từng clone `--depth 1`; bundle
     của nó không clone lại được ("Could not read <oid>"). Script phát hiện `.git/shallow`
     và tự `fetch --unshallow` trước khi đóng gói.
  2. **`--all` bỏ sót ref lạ.** Ref của Copilot/Codex checkpoint nằm ngoài
     `refs/heads`+`refs/tags`; thêm `--remotes` và kiểm bằng `clone --mirror` mới thấy đủ.
     Kiểm bằng `clone` thường sẽ báo thiếu OAN vì clone không tạo ref cho những ref đó.

Chạy:  python3 tools/luu_tru_kho.py            # cập nhật toàn bộ
       python3 tools/luu_tru_kho.py --kiem     # chỉ kiểm bản lưu trữ hiện có
"""
from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import sys
import tempfile

for _s in (sys.stdout, sys.stderr):          # Windows: cp1252 giết print() tiếng Việt
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

GOC = pathlib.Path(__file__).resolve().parent.parent
RA = GOC / "luu-tru-kho"
HOME = pathlib.Path.home()

KHO = [
    ("Claude-AI",               GOC),
    ("medical-ebm-automation",  GOC / "medical-ebm-automation"),
    ("medical-research-skills", HOME / "Documents/GitHub/medical-research-skills"),
    ("meta-pipe",               HOME / "Documents/GitHub/meta-pipe"),
    ("pubmed-search-mcp",       HOME / "Documents/GitHub/pubmed-search-mcp"),
    ("watermarks-remover",      HOME / "Documents/GitHub/watermarks-remover"),
]


def git(d: pathlib.Path, *a: str) -> tuple[int, str]:
    r = subprocess.run(["git", "-C", str(d), *a], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout + r.stderr).strip()


def dem(d: pathlib.Path) -> int:
    _, o = git(d, "rev-list", "--all", "--remotes", "--count")
    return int(o) if o.isdigit() else -1


def main() -> int:
    ap = argparse.ArgumentParser(description="Lưu trữ mọi kho git thành file tĩnh")
    ap.add_argument("--kiem", action="store_true", help="chỉ kiểm, không ghi lại")
    a = ap.parse_args()
    RA.mkdir(exist_ok=True)

    print("=" * 66)
    print(f" LƯU TRỮ KHO GIT → {RA.name}/    ({'KIỂM' if a.kiem else 'CẬP NHẬT'})")
    print("=" * 66)

    loi = 0
    for ten, d in KHO:
        out = RA / f"{ten}.bundle"
        if not (d / ".git").exists():
            print(f"  ⚠ {ten:<26} không thấy kho git — bỏ qua")
            continue

        if a.kiem:
            if not out.exists():
                print(f"  ✗ {ten:<26} CHƯA có bản lưu trữ")
                loi += 1
                continue
            ma, _ = subprocess.run(["git", "bundle", "verify", str(out)],
                                   capture_output=True, text=True, encoding="utf-8", errors="replace").returncode, None
            with tempfile.TemporaryDirectory() as tmp:
                kho_tam = pathlib.Path(tmp) / "x.git"
                subprocess.run(["git", "clone", "--mirror", "-q", str(out), str(kho_tam)],
                               capture_output=True)
                n_luu = dem(kho_tam) if kho_tam.exists() else -1
            n_goc = dem(d)
            du = n_luu >= n_goc > 0
            dau = "✓" if (ma == 0 and du) else "✗"
            print(f"  {dau} {ten:<26} gốc {n_goc} commit → lưu trữ {n_luu}")
            loi += not (ma == 0 and du)
            continue

        # Shallow clone cho ra bundle không khôi phục được → nới ra trước
        if (d / ".git/shallow").exists():
            print(f"  … {ten}: kho đang shallow, tải đủ lịch sử trước")
            git(d, "fetch", "--unshallow", "-q")

        ma, msg = git(d, "bundle", "create", str(out), "--all", "--remotes")
        if ma != 0:
            print(f"  ✗ {ten:<26} {msg.splitlines()[-1][:60] if msg else 'lỗi'}")
            loi += 1
            continue
        mb = out.stat().st_size / 1024 / 1024
        print(f"  ✓ {ten:<26} {mb:6.1f} MB · {dem(d)} commit")

    tong = sum(f.stat().st_size for f in RA.glob("*.bundle")) / 1024 / 1024
    so_kho = len(list(RA.glob("*.bundle")))
    print()
    print(f"  tổng: {tong:.0f} MB · {so_kho} kho")
    print()
    print("  Khôi phục một kho:")
    print("     git clone luu-tru-kho/<tên>.bundle <thư-mục-mới>")
    print("  Khôi phục ĐỦ mọi ref (kể cả checkpoint của Copilot/Codex):")
    print("     git clone --mirror luu-tru-kho/<tên>.bundle <tên>.git")
    return 1 if loi else 0


if __name__ == "__main__":
    raise SystemExit(main())
