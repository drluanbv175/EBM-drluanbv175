#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sync_safety_check.py — Kiểm tra AN TOÀN đồng bộ Mac↔Windows (OneDrive) trước khi làm việc.

Trả lời đúng 1 câu: "Giờ mở/sửa hệ thống này có AN TOÀN không, hay đang có nguy cơ
mất việc / hỏng .git do OneDrive sync dở hoặc phiên khác đang chạy?"

Soi 5 nguy cơ (đều là thứ đã gặp thật trong dự án này):
  1. CONFLICT-COPY của OneDrive (dấu hiệu #1 của mất việc; conflict trên file
     sinh/ignored chỉ liệt kê, không hard-block như source/hồ sơ chính)
  2. Sức khỏe git 2 repo lồng (Claude AI + medical-ebm-automation): HEAD giải được? status
     chạy được (không treo như fsck)? có khóa/đang merge dở?
  3. File lõi ĐÃ TẢI THẬT (không phải placeholder "cloud-only" chưa tải về của OneDrive)
  4. Dấu hiệu PHIÊN KHÁC VỪA GHI (nhiều file đổi trong ~3 phút qua) → có thể máy kia đang chạy
  5. Số thay đổi chưa commit (nhiều bất thường = có thể việc dở của phiên khác)

Verdict: 🟢 AN TOÀN · 🟡 THẬN TRỌNG · 🔴 DỪNG.  Exit code 0 / 1 / 2 (để script khác dùng lại).

CHỈ dùng thư viện chuẩn Python → chạy được trên mọi máy, KHÔNG cần venv/mạng.
Đây là công cụ HỖ TRỢ, không thay phán đoán. Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations
import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path

# Console Windows mặc định dùng cp1252 → in tiếng Việt có dấu là crash (đã gặp thật,
# cùng lỗi với tools/eval/test_classify.py). Ép UTF-8 để chạy được "trên mọi máy" đúng
# như docstring hứa, không cần PYTHONUTF8=1 đặt sẵn.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent          # tools/ -> "Claude AI"
NOW = time.time()

# Thư mục BỎ QUA khi quét (nặng/không liên quan)
PRUNE_DIRS = {".git", "__pycache__", "node_modules", ".pytest_cache",
              "_archive", "_reskin_backup", "pycache", "worktrees",
              "copilot-worktrees", ".venv"}

# File LÕI phải tồn tại + đã tải thật (không placeholder). Thiếu = hệ chưa sẵn sàng.
CORE_FILES = [
    "CLAUDE.md",
    ".claude/agents/dieu-phoi-nghien-cuu.md",
    ".claude/agents/dieu-phoi-lam-sang.md",
    ".claude/agents/tham-dinh-dau-ra.md",
    "tools/eval/run_eval.py",
    "tools/eval/research_checks.py",
]

# 2 repo git lồng nhau cần kiểm
GIT_REPOS = [".", "medical-ebm-automation"]

# ── tiện ích ─────────────────────────────────────────────────────────────────
def _run_git(args: list[str], cwd: Path, timeout: int = 40):
    """Chạy 1 lệnh git có timeout. Trả (ok, stdout, ghi_chú). Timeout/treo = ok=False."""
    try:
        p = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                           text=True, timeout=timeout, encoding="utf-8", errors="replace")
        return (p.returncode == 0, p.stdout.strip(), p.stderr.strip())
    except subprocess.TimeoutExpired:
        return (False, "", f"TIMEOUT sau {timeout}s (git treo — OneDrive có thể đang tải file)")
    except FileNotFoundError:
        return (False, "", "chưa cài git")
    except Exception as e:                                   # noqa: BLE001
        return (False, "", f"lỗi: {e}")


def _iter_files(cap: int = 60000):
    """Duyệt file trong ROOT, prune thư mục nặng, có trần an toàn chống chạy vô tận."""
    n = 0
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in PRUNE_DIRS]
        for fn in fns:
            n += 1
            if n > cap:
                return
            yield Path(dp) / fn


# ── các cổng kiểm ────────────────────────────────────────────────────────────
def _dr_luan_conflict_base(f: Path, name: str, low: str) -> Path | None:
    """"-dr luân"/"-dr-luan" là marker thiết bị TỪNG gặp thật trong 1 conflict-copy — nhưng
    cụm này cũng xuất hiện trong tên file HỢP LỆ (vd mẫu văn bản do bác sĩ Luân soạn), nên
    chỉ coi là conflict nếu có bản GỐC (không hậu tố) tồn tại song song, giống logic "tên
    2.ext" bên dưới. Tránh dương tính giả đã gặp 2026-07-06 (file mẫu hợp lệ bị bắt nhầm)."""
    for suffix_marker in ("-dr luân", "-dr-luan"):
        idx = low.rfind(suffix_marker)
        if idx <= 0:
            continue
        ext = name[name.rindex("."):] if "." in name else ""
        candidate_base = f.with_name(name[:idx] + ext)
        if candidate_base.exists() and candidate_base != f:
            return candidate_base
    return None


def _is_generated_conflict_artifact(rel: str) -> bool:
    """Generated/ignored artifacts can be noisy OneDrive conflicts without source drift."""
    low = rel.replace("\\", "/").lower()
    name = low.rsplit("/", 1)[-1]
    if name.endswith(".tsbuildinfo") or name.endswith(".log"):
        return True
    if "/data/archive/" in low or "/data/processed/" in low or "/data/reports/" in low:
        return True
    return low.startswith("medical-ebm-automation/results/knowledge_pack_update_queue-")


def _add_conflict_hit(hard_hits: list[str], generated_hits: list[str], f: Path, note: str = "") -> None:
    rel = str(f.relative_to(ROOT))
    detail = rel + note
    if _is_generated_conflict_artifact(rel):
        generated_hits.append(detail + "  (artefact sinh/ignored — không chặn source sync)")
    else:
        hard_hits.append(detail)


def check_conflict_copies() -> tuple[str, list[str]]:
    """Tìm file có dấu hiệu conflict-copy của OneDrive (mất việc)."""
    hard_hits = []
    generated_hits = []
    host_stem = socket.gethostname().split(".")[0].lower()  # tên máy đang chạy
    dup_re = re.compile(r"^(.*?) (\d+)(\.[^.]+)?$")         # "tên 2.ext" (bản OneDrive nhân đôi)
    for f in _iter_files():
        name = f.name
        low = name.lower()
        stem = low.rsplit(".", 1)[0]
        # Dấu hiệu conflict-copy THẬT của OneDrive — KHÔNG chỉ vì tên chứa chữ "conflict"
        # (conflict_queue.py, CONFLICT_OF_INTEREST… là file hợp lệ):
        is_conflict = (
            "conflicted copy" in low                        # hậu tố conflict chuẩn OneDrive/Office
            or stem.endswith(f"-{host_stem}")               # "tên-<tên-máy-này>.ext" = bản conflict cho máy này
        )
        if is_conflict:
            _add_conflict_hit(hard_hits, generated_hits, f)
            continue
        if _dr_luan_conflict_base(f, name, low) is not None:
            _add_conflict_hit(hard_hits, generated_hits, f, "  (nghi bản conflict — có bản gốc song song)")
            continue
        m = dup_re.match(name)                              # "X 2.ext" mà "X.ext" cũng tồn tại
        if m and m.group(2) in {"1", "2", "3"}:
            base = f.with_name(f"{m.group(1)}{m.group(3) or ''}")
            if base.exists():
                _add_conflict_hit(hard_hits, generated_hits, f, "  (nghi bản OneDrive nhân đôi)")
    if hard_hits:
        return ("RED", [*hard_hits, *generated_hits])
    if generated_hits:
        return ("GREEN", generated_hits)
    return ("GREEN", [])


def check_git_health() -> tuple[str, list[str]]:
    """Kiểm 2 repo lồng: HEAD giải được, status chạy được (không treo), không khóa/merge dở."""
    notes, worst = [], "GREEN"
    for rel in GIT_REPOS:
        repo = ROOT / rel
        gdir = repo / ".git"
        if not gdir.exists():
            notes.append(f"[{rel}] không phải git repo (bỏ qua)")
            continue
        # khóa / trạng thái dở
        for lock in ("index.lock", "MERGE_HEAD", "rebase-merge", "rebase-apply"):
            if (gdir / lock).exists():
                notes.append(f"🔴 [{rel}] có '{lock}' — git đang dở/kẹt, KHÔNG thao tác")
                worst = "RED"
        ok_head, head, err = _run_git(["rev-parse", "--short", "HEAD"], repo, timeout=20)
        if not ok_head:
            notes.append(f"🔴 [{rel}] HEAD không giải được: {err or '?'}")
            worst = "RED"
            continue
        ok_st, out, err = _run_git(["status", "--porcelain"], repo, timeout=45)
        if not ok_st:
            notes.append(f"🟡 [{rel}] git status lỗi/treo: {err or '?'} → đợi OneDrive tải xong rồi thử lại")
            worst = "RED" if worst == "RED" else "YELLOW"
            continue
        n_changes = len([l for l in out.splitlines() if l.strip()])
        tag = "🟢" if n_changes == 0 else "🟡"
        extra = "" if n_changes <= 8 else "  ← nhiều: nếu KHÔNG phải việc của bạn, có thể phiên/máy khác đang chạy"
        notes.append(f"{tag} [{rel}] HEAD={head} · {n_changes} thay đổi chưa commit{extra}")
        # WIP chưa commit CHỈ là 🟡 (thận trọng), KHÔNG 🔴 — 🔴 dành cho hỏng thật (khóa/HEAD/treo)
        if n_changes > 0 and worst == "GREEN":
            worst = "YELLOW"
    return (worst, notes)


def check_core_materialized() -> tuple[str, list[str]]:
    """File lõi phải tồn tại + có nội dung (không phải placeholder cloud-only chưa tải)."""
    missing = []
    for rel in CORE_FILES:
        p = ROOT / rel
        try:
            if (not p.exists()) or p.stat().st_size == 0:
                missing.append(rel)
        except OSError:
            missing.append(rel + " (không đọc được — cloud-only?)")
    if missing:
        return ("RED", missing)
    return ("GREEN", [])


def check_recent_writes(window_min: int = 3) -> tuple[str, list[str]]:
    """Nhiều file vừa đổi trong ~3 phút → có thể PHIÊN KHÁC/máy kia đang chạy (đừng chồng lên)."""
    cutoff = NOW - window_min * 60
    # Nhiễu LUÔN thay đổi (macOS + bookkeeping của chính Claude Code phiên NÀY) → bỏ,
    # nếu không mục này không bao giờ về 🟢. Còn lại = ghi vào FILE HỆ THỐNG thật.
    NOISE = ("/.claude/sessions/", "/.claude/state/", "sync_safety_check")
    NOISE_NAMES = (".ds_store", "changed-files.jsonl", "active.json", "broadcast.md")
    recent = []
    for f in _iter_files():
        try:
            if f.stat().st_mtime < cutoff:
                continue
        except OSError:
            continue
        rel = str(f.relative_to(ROOT))
        low = ("/" + rel.replace("\\", "/")).lower()
        if any(nz in low for nz in NOISE) or f.name.lower() in NOISE_NAMES or low.endswith(".lock"):
            continue
        recent.append(rel)
    if len(recent) > 4:
        return ("YELLOW", recent[:8] + ([f"… và {len(recent)-8} file khác"] if len(recent) > 8 else []))
    return ("GREEN", recent[:4])


# ── tổng hợp + in ────────────────────────────────────────────────────────────
def main() -> int:
    host = socket.gethostname()
    print("=" * 64)
    print(" KIỂM TRA AN TOÀN ĐỒNG BỘ  ·  Mac↔Windows (OneDrive)")
    print(f" Máy: {host}  ·  Thư mục: {ROOT.name}")
    print("=" * 64)

    order = {"GREEN": 0, "YELLOW": 1, "RED": 2}
    overall = "GREEN"
    sections = [
        ("1. Conflict-copy OneDrive", check_conflict_copies),
        ("2. Sức khỏe git (2 repo)", check_git_health),
        ("3. File lõi đã tải thật", check_core_materialized),
        ("4. Dấu hiệu phiên khác vừa ghi (3')", check_recent_writes),
    ]
    for title, fn in sections:
        try:
            level, details = fn()
        except Exception as e:                              # noqa: BLE001
            # Vá 2026-07-10: một cổng kiểm BỊ CRASH nghĩa là KHÔNG xác minh được an toàn →
            # fail-closed = RED (DỪNG), KHÔNG hạ xuống YELLOW ("thận trọng rồi làm tiếp").
            # Trước đây mọi lỗi bị nuốt thành YELLOW → có thể vượt cổng khi thật ra không rõ.
            level, details = "RED", [f"CỔNG KIỂM CRASH — không xác minh được (coi như KHÔNG an toàn): {e}"]
        icon = {"GREEN": "🟢", "YELLOW": "🟡", "RED": "🔴"}[level]
        print(f"\n{icon} {title}")
        if not details:
            print("     — sạch")
        for d in details:
            print(f"     • {d}")
        if order[level] > order[overall]:
            overall = level

    print("\n" + "=" * 64)
    if overall == "GREEN":
        print(" ✅ AN TOÀN — mở Claude Code / làm việc bình thường.")
        code = 0
    elif overall == "YELLOW":
        print(" ⚠️  THẬN TRỌNG — có thể OneDrive đang tải hoặc phiên khác vừa ghi.")
        print("    → Đợi OneDrive hiện ✓ 'Up to date', chạy lại tool này tới khi 🟢 rồi mới làm.")
        code = 1
    else:
        print(" ⛔ DỪNG — có nguy cơ mất việc/hỏng git. KHÔNG sửa gì cho tới khi xử lý.")
        print("    → Xem mục 🔴 ở trên: gỡ/di dời conflict-copy; đợi OneDrive sync xong;")
        print("      không mở 2 máy cùng lúc. Cần thì nhờ Claude Code soi từng mục.")
        code = 2
    print("=" * 64)
    print(" Quy tắc vàng: 1 máy tại một thời điểm · đợi OneDrive XANH rồi mới đổi máy.")
    print(" Cần bác sĩ kiểm chứng — đây là công cụ hỗ trợ, không thay phán đoán.")
    return code


if __name__ == "__main__":
    sys.exit(main())
