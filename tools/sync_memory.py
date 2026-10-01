#!/usr/bin/env python3
"""sync_memory.py — Đồng bộ BỘ NHỚ Claude qua OneDrive (Mac↔Windows).

VẤN ĐỀ: bộ nhớ tự-động của Claude nằm ở `~/.claude/projects/<đường-dẫn-mã-hóa>/memory/`
— NGOÀI cây OneDrive → KHÔNG tự sync. Đổi máy = "mất trí nhớ" dự án.

MỖI DỰ ÁN MỘT BỘ NHỚ — MỖI BỘ NHỚ MỘT MIRROR (vá 01/10/2026): Claude Code đặt bộ nhớ theo thư mục
MỞ PHIÊN và quy phiên trong worktree về repo chính của nó. Phiên mở ở repo gốc ghi vào
`<mã của …/Claude AI>/memory`; phiên mở ở repo con `medical-ebm-automation/` (kể cả mọi worktree
`medical-ebm-automation/.claude/worktrees/*`) ghi vào `<mã của …/Claude AI/medical-ebm-automation>/memory`.
Bản cũ chỉ đồng bộ bộ nhớ gốc ⇒ sang máy kia, các phiên trong repo y khoa mất trắng bộ nhớ của chúng.
Nay mỗi dự án trong `MEMORY_PROJECTS` có MIRROR RIÊNG:
  • gốc (Claude AI)          ↔ `memory-sync/`   (như cũ — máy kia vẫn kéo từ đây)
  • medical-ebm-automation   ↔ `memory-sync/medical-ebm-automation/`
KHÔNG gộp vào một mirror phẳng: hai bộ nhớ đều có `MEMORY.md` (chỉ mục) — đè nhau là hỏng chỉ mục.
Mirror của repo y khoa nằm trong repo GỐC (`memory-sync/` đã gitignore), KHÔNG trong repo y khoa (repo
công khai). Mirror gốc chỉ đọc tệp ở TẦNG ĐẦU nên không bao giờ thấy thư mục con của repo y khoa — bản
cũ còn chạy ở máy chưa cập nhật cũng vậy.

CÁCH LÀM: mirror hai chiều giữa thư mục memory cục bộ và mirror của từng dự án (trong OneDrive).
An toàn: **file mới hơn thắng theo mtime (+1 giây chống nhiễu), KHÔNG BAO GIỜ XÓA** → không mất dữ liệu
(xấu nhất là thừa file, không thiếu). Chạy trên MỖI máy (sau khi OneDrive xanh):
  • Máy A: đẩy memory mới → mirror OneDrive.
  • Máy B: kéo mirror → memory cục bộ của máy B (đúng đường-dẫn-mã-hóa của B) + đẩy thay đổi của B.

TÌM THƯ MỤC BỘ NHỚ CỤC BỘ (từng dự án, Mac lẫn Windows):
  1) Tên mã hoá ĐÚNG quy tắc Claude Code (`claude_project_slug`). Có thư mục dự án mang tên đó — kể cả
     chưa có `memory/` — thì dùng: đó chính là nơi Claude Code của máy này ghi.
  2) Chưa có: dò thư mục có `memory/` mà tên KẾT THÚC bằng đuôi mã hoá của dự án (gốc `-Claude-AI`,
     repo y khoa `-Claude-AI-medical-ebm-automation`) và KHÔNG mang chữ «worktrees» (worktree tạm:
     `.claude/worktrees`, `~/.ebm-worktrees`, `.harness-worktrees`). Đúng một ứng viên thì dùng; nhiều
     ứng viên thì KHÔNG đoán — bỏ qua dự án đó và báo.
  3) Không ứng viên: tên tính được (máy mới — thư mục được tạo khi kéo về).
  Bản cũ dò «chỉ một ứng viên» rồi «tên chứa claude»: nay thư mục của repo y khoa cũng chứa «Claude-AI»
  nên lối đó có thể đồng bộ bộ nhớ GỐC vào thư mục của repo y khoa — đã bỏ.

CHỐT CHỐNG TRỘN: trước khi ghi, so đường dẫn THẬT (đi theo symlink/junction). Thư mục cục bộ của hai dự
án trùng/lồng nhau, hoặc thư mục cục bộ của dự án này trùng/chứa mirror của dự án kia ⇒ TỪ CHỐI cả hai.

Dùng:
  python3 tools/sync_memory.py            # đồng bộ 2 chiều
  python3 tools/sync_memory.py --dry-run  # in từng cặp (cục bộ ↔ mirror) và việc sẽ làm, KHÔNG ghi

Mã thoát: 0 xong (kể cả dự án bỏ qua vì thiếu nguyên liệu) · 1 cần bác sĩ xem (ứng viên mơ hồ, lỗi chép
tệp) · 2 TỪ CHỐI vì hai dự án chung/lồng thư mục (đồng bộ sẽ trộn bộ nhớ).
Giới hạn: chỉ đồng bộ tệp .md/.json ở TẦNG ĐẦU (như bản cũ); không đọc `CLAUDE_CONFIG_DIR` hay cài đặt
`autoMemoryDirectory` của Claude Code (máy bác sĩ không đặt).
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import unicodedata
from dataclasses import dataclass
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

# Quy tắc đặt tên thư mục dự án của Claude Code — đọc trực tiếp trong mã Claude Code 2.1.284 (01/10/2026):
#   k(e)  = e.replace(/[^a-zA-Z0-9]/g, "-")      thay TỪNG mã UTF-16 (ký tự ngoài BMP ⇒ hai dấu '-')
#   PR(e) = k(e) nếu dài ≤ 200; ngược lại k(e).slice(0, 200) + "-" + Math.abs(UJ(e)).toString(36)
#   UJ(e) = h*31 + mã UTF-16, tràn số nguyên 32 bit có dấu (kiểu String.hashCode của Java)
# Đường dẫn dự án được chuẩn hoá NFC trước. Bản cũ chỉ thay [ /\\:] nên lệch với mọi đường dẫn có
# '.', '(', ')' hay chữ có dấu (vd OneDrive từng gắn ở «OneDrive-Personal(2)» ⇒ «…-Personal-2--…»).
_SLUG_MAX = 200
_BASE36 = "0123456789abcdefghijklmnopqrstuvwxyz"
# Mọi kiểu worktree tạm đều mang chữ này trong tên mã hoá: «.claude/worktrees» ⇒ «-claude-worktrees-»,
# «~/.ebm-worktrees» ⇒ «-ebm-worktrees-», «.harness-worktrees» ⇒ «-harness-worktrees-».
_WORKTREE_MARK = "worktrees"


def _utf16_units(text: str) -> list[int]:
    """Các mã UTF-16 của chuỗi — đúng đơn vị JavaScript làm việc (`charCodeAt`, regex không cờ u)."""
    raw = text.encode("utf-16-le", "surrogatepass")
    return [int.from_bytes(raw[i:i + 2], "little") for i in range(0, len(raw), 2)]


def _sanitize(units: list[int]) -> str:
    """Thay mọi mã UTF-16 ngoài [a-zA-Z0-9] bằng '-' (hàm `k` của Claude Code)."""
    return "".join(chr(u) if (0x30 <= u <= 0x39 or 0x41 <= u <= 0x5A or 0x61 <= u <= 0x7A) else "-"
                   for u in units)


def _java_string_hash(units: list[int]) -> int:
    """Hàm băm `UJ` của Claude Code: h = h*31 + mã UTF-16, giữ trong số nguyên 32 bit có dấu."""
    h = 0
    for unit in units:
        h = (h * 31 + unit) & 0xFFFF_FFFF
    return h - 0x1_0000_0000 if h & 0x8000_0000 else h


def _base36(n: int) -> str:
    """`Number.prototype.toString(36)` cho số nguyên không âm."""
    digits = ""
    while True:
        n, r = divmod(n, 36)
        digits = _BASE36[r] + digits
        if n == 0:
            return digits


def claude_project_slug(path: str | os.PathLike[str]) -> str:
    """Tên thư mục Claude Code đặt trong `~/.claude/projects/` cho một thư mục dự án (quy tắc ở đầu tệp)."""
    units = _utf16_units(unicodedata.normalize("NFC", os.fspath(path)))
    slug = _sanitize(units)
    if len(slug) <= _SLUG_MAX:
        return slug
    return f"{slug[:_SLUG_MAX]}-{_base36(abs(_java_string_hash(units)))}"


@dataclass(frozen=True)
class MemoryProject:
    """Một dự án có bộ nhớ Claude Code riêng, đồng bộ với một mirror RIÊNG trong OneDrive."""

    name: str          # tên in cho bác sĩ
    directory: Path    # thư mục mở phiên Claude Code trên MÁY NÀY
    mirror: Path       # mirror phẳng của riêng dự án này


MEMORY_PROJECTS: tuple[MemoryProject, ...] = (
    MemoryProject("gốc (Claude AI)", PROJECT_ROOT, MIRROR),
    MemoryProject("medical-ebm-automation", PROJECT_ROOT / "medical-ebm-automation",
                  MIRROR / "medical-ebm-automation"),
)


@dataclass(frozen=True)
class LocalMemory:
    """Kết quả dò thư mục bộ nhớ cục bộ của một dự án. `path is None` = mơ hồ, không dám chọn."""

    path: Path | None
    how: str
    candidates: tuple[Path, ...] = ()


def _slug_tail(project: MemoryProject, root: Path) -> str:
    """Đuôi tên mã hoá dùng khi dò dự phòng: tên thư mục gốc + đường dẫn tương đối của dự án.

    Gốc → «-Claude-AI»; repo y khoa → «-Claude-AI-medical-ebm-automation». Đuôi gồm cả tên thư mục gốc
    để không bắt nhầm một bản sao/worktree khác chỉ trùng tên repo con (vd worktree của repo gốc mở
    phiên ở thư mục con medical-ebm-automation: «…--claude-worktrees-<tên>-medical-ebm-automation»).
    """
    rel = Path(root.name) / project.directory.relative_to(root)
    return "-" + _sanitize(_utf16_units(unicodedata.normalize("NFC", rel.as_posix())))


def find_local_memory(project: MemoryProject, projects_dir: Path | None = None,
                      root: Path | None = None) -> LocalMemory:
    """Tìm thư mục memory cục bộ của MÁY NÀY cho một dự án (thứ tự dò ở đầu tệp)."""
    projects_dir = PROJECTS if projects_dir is None else projects_dir
    root = PROJECT_ROOT if root is None else root
    computed = projects_dir / claude_project_slug(project.directory)
    if computed.is_dir():
        how = "đúng tên Claude Code tính được"
        if not (computed / "memory").is_dir():
            how += " — chưa có memory/, sẽ tạo khi kéo về"
        return LocalMemory(computed / "memory", how)
    tail = _slug_tail(project, root).lower()
    candidates = []
    if projects_dir.is_dir():
        for d in sorted(projects_dir.iterdir()):
            name = d.name.lower()          # Mac/Windows không phân biệt hoa thường tên thư mục
            if name.endswith(tail) and _WORKTREE_MARK not in name and (d / "memory").is_dir():
                candidates.append(d / "memory")
    if len(candidates) == 1:
        return LocalMemory(candidates[0], f"dò theo đuôi tên «{tail}» (chưa có thư mục mang tên tính được)")
    if candidates:
        return LocalMemory(None, f"{len(candidates)} thư mục cùng khớp đuôi tên «{tail}» — không đoán",
                           tuple(candidates))
    return LocalMemory(computed / "memory", "máy mới — tạo đúng tên Claude Code tính được khi kéo về")


def _real(path: Path) -> str:
    """Đường dẫn THẬT để so sánh (đi theo symlink/junction; Windows không phân biệt hoa thường)."""
    return os.path.normcase(os.path.realpath(path))


def _same_or_inside(outer: str, inner: str) -> bool:
    """`inner` trùng `outer` hoặc nằm trong `outer` (đường dẫn đã qua `_real`)."""
    return inner == outer or inner.startswith(outer.rstrip(os.sep) + os.sep)


def find_crossings(pairs: list[tuple[str, Path, Path]]) -> tuple[set[str], list[str]]:
    """Dự án nào chồng thư mục lên dự án khác ⇒ đồng bộ sẽ trộn hai bộ nhớ.

    `pairs` = [(tên, thư mục cục bộ, mirror)]. Trả (tên các dự án phải từ chối, lời giải thích).
    Mirror gốc CHỨA mirror repo y khoa là thiết kế (mirror chỉ đọc tầng đầu) nên chỉ cấm mirror TRÙNG nhau.
    Thư mục cục bộ trùng mirror của CHÍNH dự án đó (liên kết) không phải trộn — `sync_all` bỏ qua cặp ấy.
    """
    blocked: set[str] = set()
    messages: list[str] = []
    real = [(name, _real(local), _real(mirror)) for name, local, mirror in pairs]
    for i, (name_a, local_a, mirror_a) in enumerate(real):
        for j, (name_b, local_b, mirror_b) in enumerate(real):
            if i == j:
                continue
            reasons = []
            if _same_or_inside(local_a, local_b):
                reasons.append("thư mục cục bộ trùng hoặc chứa thư mục cục bộ của")
            if _same_or_inside(local_a, mirror_b):
                reasons.append("thư mục cục bộ trùng hoặc chứa mirror của")
            if i < j and mirror_a == mirror_b:
                reasons.append("mirror trùng mirror của")
            for reason in reasons:
                blocked.update((name_a, name_b))
                messages.append(f"«{name_a}»: {reason} «{name_b}»")
    return blocked, messages


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


def sync_pair(local: Path, mirror: Path, dry: bool) -> tuple[int, int, int, int]:
    """Đồng bộ hai chiều MỘT cặp (cục bộ ↔ mirror), in từng việc. Trả (đẩy, kéo, không đổi, lỗi)."""
    lf, mf = _files(local), _files(mirror)
    pushed = pulled = same = errors = 0
    will = "sẽ " if dry else ""
    for name in sorted(set(lf) | set(mf)):
        lp, mp = lf.get(name), mf.get(name)
        try:
            if lp and not mp:                                # chỉ có ở local → đẩy lên mirror
                src, dst, why = lp, mirror / name, "chỉ có ở cục bộ"
            elif mp and not lp:                              # chỉ có ở mirror → kéo về local
                src, dst, why = mp, local / name, "chỉ có ở mirror"
            else:                                            # cả hai → file mới hơn thắng
                lm, mm = lp.stat().st_mtime, mp.stat().st_mtime
                if lm > mm + 1:                              # +1s: chống nhiễu mtime
                    src, dst, why = lp, mirror / name, "cục bộ mới hơn"
                elif mm > lm + 1:
                    src, dst, why = mp, local / name, "mirror mới hơn"
                else:
                    same += 1
                    continue
            _copy(src, dst, dry)
        except OSError as exc:
            errors += 1
            print(f"    ✗ {name}: không đồng bộ được ({type(exc).__name__}: {exc})")
            continue
        if src is lp:
            pushed += 1
            print(f"    → {will}đẩy lên mirror : {name}  ({why})")
        else:
            pulled += 1
            print(f"    ← {will}kéo về cục bộ  : {name}  ({why})")
    return pushed, pulled, same, errors


def sync_all(projects: tuple[MemoryProject, ...] | None = None, projects_dir: Path | None = None,
             root: Path | None = None, dry: bool = False) -> int:
    """Đồng bộ mọi dự án — mỗi dự án đúng MỘT cặp (cục bộ ↔ mirror riêng). Trả mã thoát (xem đầu tệp)."""
    projects = MEMORY_PROJECTS if projects is None else projects
    code = 0
    found: dict[str, LocalMemory] = {}
    for project in projects:
        if project.directory.is_dir():
            found[project.name] = find_local_memory(project, projects_dir, root)
    blocked, messages = find_crossings([(p.name, found[p.name].path, p.mirror) for p in projects
                                        if p.name in found and found[p.name].path is not None])
    if dry:
        print("  [DRY-RUN] chỉ xem — KHÔNG ghi gì.")
    for project in projects:
        print(f"\n── {project.name} " + "─" * max(0, 56 - len(project.name)))
        print(f"  Dự án  : {project.directory}")
        if project.name not in found:
            print("  ⚪ Bỏ qua: máy này không có thư mục dự án — không có gì để đồng bộ.")
            continue
        local = found[project.name]
        if local.path is None:
            code = max(code, 1)
            print(f"  🟡 Cục bộ: {local.how}:")
            for c in local.candidates:
                print(f"       • {c}")
            print(f"     Mở một phiên Claude Code tại «{project.directory}» trên máy này (Claude Code tạo đúng "
                  "thư mục mang tên tính được) rồi chạy lại.")
            continue
        print(f"  Cục bộ : {local.path}")
        print(f"           ({local.how})")
        print(f"  Mirror : {project.mirror}")
        if project.name in blocked:
            code = max(code, 2)
            print("  ⛔ TỪ CHỐI — đồng bộ sẽ trộn bộ nhớ của hai dự án:")
            for m in messages:
                if f"«{project.name}»" in m:
                    print(f"       • {m}")
            continue
        if _real(local.path) == _real(project.mirror):
            print("  ⚪ Cục bộ và mirror là MỘT thư mục (liên kết) — không cần đồng bộ.")
            continue
        if not local.path.exists() and not project.mirror.exists():
            print("  ⚪ Cả hai phía chưa có bộ nhớ — không có gì để đồng bộ.")
            continue
        pushed, pulled, same, errors = sync_pair(local.path, project.mirror, dry)
        tag = "[DRY-RUN] " if dry else ""
        print(f"  {tag}→ đẩy lên mirror: {pushed} · ← kéo về cục bộ: {pulled} · không đổi: {same}"
              + (f" · ✗ lỗi: {errors}" if errors else ""))
        if errors:
            code = max(code, 1)
    print()
    if code == 0:
        print("  ✅ Xong. (KHÔNG xóa file nào — file mới hơn thắng)"
              + ("  Chưa ghi gì — chạy lại không có --dry-run để đồng bộ." if dry else ""))
        print("  ℹ Đợi OneDrive xanh rồi chạy lệnh này trên máy kia để kéo về.")
    elif code == 1:
        print("  🟡 Có dự án cần bác sĩ xem (dòng 🟡/✗ ở trên). KHÔNG xóa file nào.")
    else:
        print("  ⛔ Có dự án bị TỪ CHỐI vì chồng thư mục — sửa liên kết/thư mục rồi chạy lại. KHÔNG xóa file nào.")
    return code


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Đồng bộ bộ nhớ Claude qua OneDrive — mỗi dự án một mirror riêng")
    ap.add_argument("--dry-run", action="store_true",
                    help="In từng cặp (cục bộ ↔ mirror) và việc sẽ làm, không ghi")
    args = ap.parse_args(argv)
    print("═" * 60)
    print("  ĐỒNG BỘ BỘ NHỚ CLAUDE ↔ OneDrive (an toàn, không xóa)")
    print("═" * 60)
    return sync_all(dry=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
