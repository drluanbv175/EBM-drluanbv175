#!/usr/bin/env python3
"""sync_memory.py — Đồng bộ BỘ NHỚ Claude qua OneDrive (Mac↔Windows).

VẤN ĐỀ: bộ nhớ tự-động của Claude nằm ở `~/.claude/projects/<đường-dẫn-mã-hóa>/memory/`
— NGOÀI cây OneDrive → KHÔNG tự sync. Đổi máy = "mất trí nhớ" dự án.

CÁCH LÀM: mirror hai chiều giữa thư mục memory cục bộ và `<repo>/memory-sync/` (trong OneDrive).
An toàn: **file mới hơn thắng theo mtime, KHÔNG BAO GIỜ XÓA** → không mất dữ liệu (xấu nhất là
thừa file, không thiếu). Chạy trên MỖI máy (sau khi OneDrive xanh):
  • Máy A: đẩy memory mới → mirror OneDrive.
  • Máy B: kéo mirror → memory cục bộ của máy B (đúng đường-dẫn-mã-hóa của B) + đẩy thay đổi của B.

Dùng:
  python3 tools/sync_memory.py            # đồng bộ 2 chiều
  python3 tools/sync_memory.py --dry-run  # xem sẽ làm gì, không ghi
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

# Console Windows mặc định dùng cp1252 → in "═"/tiếng Việt có dấu là crash ngay khi bấm
# đúp "Đồng bộ Bộ nhớ.command" (đã gặp thật, cùng lỗi với sync_safety_check.py). Ép UTF-8
# để chạy được trên mọi máy không cần đặt sẵn PYTHONUTF8=1.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parents[1]          # thư mục "Claude AI" (repo gốc)
MIRROR = PROJECT_ROOT / "memory-sync"                        # bản mirror trong OneDrive (gitignored)
PROJECTS = Path.home() / ".claude" / "projects"


def _encode(path: Path) -> str:
    """Mã hóa đường dẫn dự án theo quy ước Claude Code (thay / \\ : và khoảng trắng bằng '-')."""
    return re.sub(r"[ /\\:]", "-", str(path))


def find_local_memory() -> Path:
    """Tìm thư mục memory cục bộ của MÁY NÀY cho dự án hiện tại (robust cross-OS).

    1) Thử đường-dẫn-mã-hóa tính từ PROJECT_ROOT (khớp trên máy đã tạo memory).
    2) Nếu chưa có: nếu chỉ có DUY NHẤT một project có memory/ → dùng nó.
    3) Nếu nhiều: chọn folder tên chứa 'Claude' (hoặc 'Claude-AI').
    4) Nếu vẫn không: trả về đường-dẫn-mã-hóa (sẽ được tạo mới — máy mới).
    """
    computed = PROJECTS / _encode(PROJECT_ROOT) / "memory"
    if computed.exists():
        return computed
    candidates = []
    if PROJECTS.exists():
        candidates = [p for p in PROJECTS.iterdir() if (p / "memory").exists()]
    if len(candidates) == 1:
        return candidates[0] / "memory"
    for p in candidates:
        if "claude" in p.name.lower():
            return p / "memory"
    return computed


def _files(d: Path) -> dict:
    """Map {tên_file: Path} cho các file .md/.json ở TẦNG ĐẦU của d (memory là phẳng)."""
    if not d.exists():
        return {}
    return {f.name: f for f in d.iterdir()
            if f.is_file() and f.suffix in (".md", ".json") and not f.name.startswith(".")}


def _copy(src: Path, dst: Path, dry: bool) -> None:
    if dry:
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)                                    # copy2 giữ mtime → so sánh đúng


def sync(dry: bool = False) -> int:
    local = find_local_memory()
    print(f"  Local  : {local}")
    print(f"  Mirror : {MIRROR}")
    if not local.exists() and not MIRROR.exists():
        print("  ⚠ Cả hai phía chưa có memory — không có gì để đồng bộ.")
        return 0

    lf, mf = _files(local), _files(MIRROR)
    names = sorted(set(lf) | set(mf))
    pushed = pulled = same = 0
    for name in names:
        lp, mp = lf.get(name), mf.get(name)
        if lp and not mp:                                    # chỉ có ở local → đẩy lên mirror
            _copy(lp, MIRROR / name, dry); pushed += 1
        elif mp and not lp:                                  # chỉ có ở mirror → kéo về local
            _copy(mp, local / name, dry); pulled += 1
        else:                                                # cả hai → file mới hơn thắng
            lm, mm = lp.stat().st_mtime, mp.stat().st_mtime
            if lm > mm + 1:                                  # +1s: chống nhiễu mtime
                _copy(lp, MIRROR / name, dry); pushed += 1
            elif mm > lm + 1:
                _copy(mp, local / name, dry); pulled += 1
            else:
                same += 1
    tag = "[DRY-RUN] " if dry else ""
    print(f"  {tag}→ đẩy lên mirror: {pushed} · kéo về local: {pulled} · không đổi: {same}")
    print("  ✅ Xong. (KHÔNG xóa file nào — file mới hơn thắng)")
    if not MIRROR.exists() or not _files(MIRROR):
        print("  ℹ Lần đầu trên máy này: chạy lại trên máy kia sau khi OneDrive xanh để kéo về.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Đồng bộ bộ nhớ Claude qua OneDrive")
    ap.add_argument("--dry-run", action="store_true", help="Xem sẽ làm gì, không ghi")
    args = ap.parse_args()
    print("═" * 60)
    print("  ĐỒNG BỘ BỘ NHỚ CLAUDE ↔ OneDrive (an toàn, không xóa)")
    print("═" * 60)
    return sync(dry=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
