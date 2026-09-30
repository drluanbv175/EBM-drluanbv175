#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sync_safety_check.py — Kiểm tra AN TOÀN đồng bộ Mac↔Windows (OneDrive) trước khi làm việc.

Trả lời đúng 1 câu: "Giờ mở/sửa hệ thống này có AN TOÀN không, hay đang có nguy cơ
mất việc / hỏng .git do OneDrive sync dở hoặc phiên khác đang chạy?"

Soi 6 nguy cơ (đều là thứ đã gặp thật trong dự án này):
  1. CONFLICT-COPY của OneDrive (dấu hiệu #1 của mất việc; conflict trên file
     sinh/ignored chỉ liệt kê, không hard-block như source/hồ sơ chính)
  2. Sức khỏe git 2 repo lồng (Claude AI + medical-ebm-automation): HEAD giải được? status
     chạy được (không treo như fsck)? có khóa/đang merge dở?
  3. File lõi ĐÃ TẢI THẬT (không phải placeholder "cloud-only" chưa tải về của OneDrive)
  4. Dấu hiệu PHIÊN KHÁC VỪA GHI (nhiều file đổi trong ~3 phút qua) → có thể máy kia đang chạy
  5. Số thay đổi chưa commit (nhiều bất thường = có thể việc dở của phiên khác)
  6. CONFLICT-COPY NẰM TRONG `.git` (mục 1 bỏ qua `.git`): ref ma giữ commit nhánh thật không có
     = 🔴; bản sao config/HEAD/ref đã an toàn = 🟡; rác index/FETCH_HEAD/reflog chỉ liệt kê (30/09/2026)

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
import unicodedata
from pathlib import Path

# Console Windows mặc định dùng cp1252 → in tiếng Việt có dấu là crash (đã gặp thật,
# cùng lỗi với tools/eval/test_classify.py). Ép UTF-8 để chạy được "trên mọi máy" đúng
# như docstring hứa, không cần PYTHONUTF8=1 đặt sẵn.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent          # tools/ -> "Claude AI"
NOW = time.time()

# VÁ 07/09/2026: trước đây GIT_REPOS chỉ ghi tên tương đối rồi ghép `ROOT / rel`
# — giả định medical-ebm-automation nằm LỒNG trong ROOT (đúng máy thật). Trên
# phiên cloud (medical-ebm-automation là ANH EM của ROOT), `ROOT / rel` trỏ vào
# thư mục không tồn tại → check_git_health() lặng lẽ báo "không phải git repo
# (bỏ qua)" thay vì thật sự kiểm sức khỏe git của repo đó — đúng việc công cụ
# này (kiểm tra AN TOÀN đồng bộ, chạy MẶC ĐỊNH trước khi làm việc) sinh ra để
# bắt. Dùng duong_goc() — xem tools/ban_sao_tran.py.
import importlib.util as _ilu_ssc  # noqa: E402
_sp_ssc = _ilu_ssc.spec_from_file_location(
    "_bst_ssc", Path(__file__).resolve().parent / "ban_sao_tran.py")
_bst_ssc = _ilu_ssc.module_from_spec(_sp_ssc)
_sp_ssc.loader.exec_module(_bst_ssc)
_MEA_GOC = _bst_ssc.duong_goc("medical-ebm-automation", ROOT) or (ROOT / "medical-ebm-automation")

# Thư mục BỎ QUA khi quét (nặng/không liên quan)
PRUNE_DIRS = {".git", "__pycache__", "node_modules", ".pytest_cache",
              "_archive", "_reskin_backup", "pycache", "worktrees",
              "copilot-worktrees", ".venv"}

# Tên THIẾT BỊ OneDrive gắn vào bản sao xung đột: «tên-<thiết bị>.ext», lặp lại thì «tên-<thiết bị>-2.ext» (đo 30/09/2026:
# `so-tong-thuat-Dr Luân BV175-2.json`, `.git/index-C010000PK16BSL-5`). Mỗi máy dùng TÊN MÁY CỦA CHÍNH NÓ — Mac «Dr Luân
# BV175» (khác hostname), Windows «C010000PK16BSL» — nên chỉ so với `socket.gethostname()` là mù trước bản sao do máy KIA
# đẻ (30/09: `medical-ebm-automation/CLAUDE-C010000PK16BSL.md` chạy trên Mac sẽ lọt). Chỉ đặt ở đây tên không thể là chữ
# trong tên tệp hợp lệ; «Dr Luân» có thể là tên tác giả mẫu văn bản nên cây làm việc vẫn dùng `_dr_luan_conflict_base`
# (đòi bản gốc song song). Thêm máy mới ⇒ thêm tên máy (chữ thường) vào đây.
THIET_BI_ONEDRIVE = ("c010000pk16bsl",)
# Trong `.git` không tệp hợp lệ nào mang tên người ⇒ nhận luôn tên máy Mac, không cần bản gốc song song.
THIET_BI_TRONG_GIT = (*THIET_BI_ONEDRIVE, "dr luân bv175")


def _nfc_thuong(s: str) -> str:
    """NFC + chữ thường: tên tệp đi qua Mac có thể ở dạng NFD («â» tách dấu) — so thẳng với chuỗi NFC trong mã sẽ trượt
    (bẫy đã gặp 05/08: so tên tệp trượt 324/358 lần)."""
    return unicodedata.normalize("NFC", s).lower()


def _hau_to_thiet_bi(ten_thuong: str, cac_thiet_bi) -> str | None:
    """Tên thiết bị nếu tên tệp kết thúc «-<thiết bị>» hoặc «-<thiết bị>-<N>», có thể kèm MỘT đuôi «.ext»."""
    for tb in dict.fromkeys(cac_thiet_bi):
        if tb and re.search(rf"-{re.escape(tb)}(?:-\d+)?(?:\.[^.\s]+)?$", ten_thuong):
            return tb
    return None

# File LÕI phải tồn tại + đã tải thật (không placeholder). Thiếu = hệ chưa sẵn sàng.
CORE_FILES = [
    "CLAUDE.md",
    ".claude/agents/dieu-phoi-nghien-cuu.md",
    ".claude/agents/dieu-phoi-lam-sang.md",
    ".claude/agents/tham-dinh-dau-ra.md",
    "tools/eval/run_eval.py",
    "tools/eval/research_checks.py",
]

# 2 repo git cần kiểm (lồng trên máy thật, anh em trên phiên cloud — xem duong_goc() ở trên)
GIT_REPOS = [(".", ROOT), ("medical-ebm-automation", _MEA_GOC)]

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


def _iter_files(cap: int = 1_000_000, time_budget_s: float = 25.0):
    """Duyệt file trong ROOT, prune thư mục nặng, có trần an toàn chống chạy vô tận.

    SỬA 16/09/2026: cap cũ 60.000 là ĐIỂM MÙ THẬT, không phải phòng ngừa lý thuyết —
    đo trực tiếp trên cây làm việc này (os.walk không sort, không đảm bảo thứ tự):
    172.400 file (đã prune) và thư mục `state/` (chứa conflict-copy thật, xem
    _quarantine-conflict-copy/) chỉ được os.walk() chạm tới ở file thứ 150.679 — SAU
    cap cũ rất xa. Nghĩa là 3 trong 4 cổng của chốt này (conflict-copy · file lõi ·
    phiên khác vừa ghi) chưa từng soi tới ~65% cây, im lặng, mọi phiên. Cùng họ lỗi
    "báo động giả còn tệ hơn không kiểm" đã lặp nhiều lần trong CLAUDE.md, nhưng
    ngược chiều: đây là ÂM TÍNH GIẢ (báo 🟢 sạch trong khi thật ra chưa hề nhìn tới).
    Đo lại: walk KHÔNG prune, đủ 172.400 file mất 1,68 giây trên máy này — cap theo
    SỐ LƯỢNG không cần thiết để chống treo; trần THẬT phải là THỜI GIAN (ổ mạng/
    OneDrive đang tải file cloud-only mới là nguy cơ treo thật). `cap` giữ lại chỉ
    làm hàng rào cuối cùng chống vòng lặp symlink bệnh lý chưa nằm trong PRUNE_DIRS.
    """
    n = 0
    t0 = time.monotonic()
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in PRUNE_DIRS]
        if time.monotonic() - t0 > time_budget_s:
            return
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
    if low.startswith("medical-ebm-automation/results/knowledge_pack_update_queue-"):
        return True
    # .claude/sessions/ + .claude/state/ là sổ bookkeeping NỘI BỘ của chính Claude Code
    # (active session tracker, instructions-loaded log…) — hoàn toàn nằm ngoài git
    # (/.claude/* bị .gitignore loại, xem dòng 67 file đó) và được app tự sinh lại mỗi
    # phiên. check_recent_writes() đã coi 2 đường dẫn này là NOISE (dòng ~211) từ trước;
    # trước bản vá này riêng check_conflict_copies() lại chấm chúng là hard_hits, khiến
    # RED giả mỗi khi nhiều phiên/máy cùng chạy — đúng việc thường trực của dự án này —
    # và báo động giả dạy người ta bỏ qua cả cảnh báo thật (bài học lặp lại nhiều lần
    # trong CLAUDE.md). Quarantine an toàn: xem cloud-mirror/_quarantine-conflict-copy/.
    if low.startswith(".claude/sessions/") or "/.claude/sessions/" in low:
        return True
    if low.startswith(".claude/state/") or "/.claude/state/" in low:
        return True
    return False


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
    cac_thiet_bi = (host_stem, *THIET_BI_ONEDRIVE)          # máy này + máy đã biết (bản sao do máy KIA đẻ)
    dup_re = re.compile(r"^(.*?) (\d+)(\.[^.]+)?$")         # "tên 2.ext" (bản OneDrive nhân đôi)
    for f in _iter_files():
        name = unicodedata.normalize("NFC", f.name)
        low = name.lower()
        # Dấu hiệu conflict-copy THẬT của OneDrive — KHÔNG chỉ vì tên chứa chữ "conflict"
        # (conflict_queue.py, CONFLICT_OF_INTEREST… là file hợp lệ):
        is_conflict = (
            "conflicted copy" in low                        # hậu tố conflict chuẩn OneDrive/Office
            or _hau_to_thiet_bi(low, cac_thiet_bi) is not None  # "tên-<máy>(-N).ext" — máy này hoặc máy kia, cả bản lặp
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
    for rel, repo in GIT_REPOS:
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
        n_changes = len([dong for dong in out.splitlines() if dong.strip()])
        tag = "🟢" if n_changes == 0 else "🟡"
        extra = "" if n_changes <= 8 else "  ← nhiều: nếu KHÔNG phải việc của bạn, có thể phiên/máy khác đang chạy"
        notes.append(f"{tag} [{rel}] HEAD={head} · {n_changes} thay đổi chưa commit{extra}")
        # WIP chưa commit CHỈ là 🟡 (thận trọng), KHÔNG 🔴 — 🔴 dành cho hỏng thật (khóa/HEAD/treo)
        if n_changes > 0 and worst == "GREEN":
            worst = "YELLOW"
    return (worst, notes)


# ── bản sao xung đột NẰM TRONG .git ───────────────────────────────────────────
# Thêm 30/09/2026. Mục 1 prune `.git` (đúng — kho đối tượng hàng vạn tệp) nên KHÔNG BAO GIỜ thấy bản sao xung đột OneDrive
# đẻ ngay trong `.git` khi hai máy cùng ghi (lỗ hổng ghi nhận từ 03/08). Đo 30/09: 36 tệp trong `.git` hai repo —
# `config-C010000PK16BSL`, index ×7, FETCH_HEAD ×7, reflog ×13, commit-graph-chain ×2, ORIG_HEAD ×2 — cùng một ref ma
# `origin/master-C010000PK16BSL` hiện trong `git for-each-ref`, mà chốt vẫn 🟢. Phân loại theo thứ git THẬT SỰ ĐỌC:
#  - refs/**, packed-refs: git coi mọi tệp dưới refs/ là một ref ⇒ bản sao thành «ref ma». Giữ commit mà ref thật KHÔNG có
#    ⇒ 🔴 (họ «6 commit mồ côi» 09/07 — dời trước là mất việc); commit đã nằm trong ref thật, hoặc ref máy chủ ⇒ 🟡.
#  - config, HEAD: bản đang dùng có thể đã mất thiết lập/nhánh mà bản kia có ⇒ 🟡 (so rồi dời).
#  - còn lại (index, FETCH_HEAD, ORIG_HEAD, logs/, objects/info/…): git không đọc tên có hậu tố ⇒ rác vô hại, chỉ liệt kê
#    (không chặn) — nhưng là BẰNG CHỨNG hai máy từng ghi `.git` cùng lúc.
def _quet_ban_sao_git(git_dir: Path, cac_thiet_bi, time_budget_s: float) -> tuple[list[tuple[str, str]], bool]:
    """(các (đường dẫn trong .git dạng posix NFC, thiết bị), đã quét hết?) — bỏ đối tượng rời objects/xx và objects/pack."""
    t0 = time.monotonic()
    ra: list[tuple[str, str]] = []
    for dp, dns, fns in os.walk(git_dir):
        if time.monotonic() - t0 > time_budget_s:
            return ra, False
        if Path(dp) == git_dir / "objects":
            dns[:] = [d for d in dns if d == "info"]         # tên hex, không ai đọc tên có hậu tố máy
        for fn in fns:
            ten = _nfc_thuong(fn)
            tb = _hau_to_thiet_bi(ten, cac_thiet_bi)
            if tb is None and "conflicted copy" not in ten:
                continue
            rel = unicodedata.normalize("NFC", (Path(dp) / fn).relative_to(git_dir).as_posix())
            ra.append((rel, tb or ""))
    return ra, True


def _bo_hau_to(rel: str, tb: str) -> str:
    """'refs/heads/x-<máy>-2' → 'refs/heads/x' (chỉ đụng phần tên cuối)."""
    dau, _, cuoi = rel.rpartition("/")
    goc = re.sub(rf"-{re.escape(tb)}(?:-\d+)?(?=(?:\.[^.\s]+)?$)", "", cuoi, flags=re.IGNORECASE)
    return f"{dau}/{goc}" if dau else goc


def _commit_nam_trong(repo: Path, sha: str, ref_that: str) -> bool:
    """`sha` đã là tổ tiên (hoặc chính) của ref thật đang dùng? Ref thật vắng/không kiểm được ⇒ False."""
    ok_that, _, _ = _run_git(["rev-parse", "--verify", "--quiet", ref_that], repo, timeout=20)
    return ok_that and _run_git(["merge-base", "--is-ancestor", sha, ref_that], repo, timeout=30)[0]


def _xet_ref_ma(repo: Path, tep: Path, ref_that: str) -> tuple[str, str]:
    try:
        noi_dung = tep.read_text(encoding="utf-8", errors="replace").strip()
    except OSError as e:
        return "RED", f"ref ma không đọc được ({e}) — kiểm tay trước khi dời"
    if noi_dung.startswith("ref:"):
        return "YELLOW", "ref ma kiểu tượng trưng (không giữ commit) — dời được"
    sha = noi_dung.split()[0] if noi_dung else ""
    if not re.fullmatch(r"[0-9a-f]{40}(?:[0-9a-f]{24})?", sha):
        return "RED", "ref ma không chứa mã commit hợp lệ — kiểm tay trước khi dời"
    if ref_that and _commit_nam_trong(repo, sha, ref_that):
        return "YELLOW", f"ref ma — commit {sha[:7]} đã nằm trong `{ref_that}`, dời được (không mất gì)"
    if ref_that.startswith("refs/remotes/"):
        return "YELLOW", f"ref ma của nhánh máy chủ — `git fetch --prune` gỡ; commit {sha[:7]} lấy lại từ máy chủ nếu còn"
    return "RED", (f"ref ma giữ commit {sha[:7]} mà `{ref_that or '?'}` KHÔNG có — tạo nhánh `rescue/…` từ commit đó "
                   "trước khi dời (dời trước là mất việc)")


def _xet_packed_refs_ma(repo: Path, tep: Path) -> tuple[str, str]:
    try:
        dong = tep.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as e:
        return "RED", f"bản sao packed-refs không đọc được ({e}) — kiểm tay trước khi dời"
    mat = []
    for d in dong:
        p = d.split()
        if len(p) != 2 or d.startswith(("#", "^")) or not p[1].startswith("refs/") or p[1].startswith("refs/remotes/"):
            continue
        if not _commit_nam_trong(repo, p[0], p[1]):
            mat.append(p[1])
    if mat:
        return "RED", (f"bản sao packed-refs giữ {len(mat)} ref mà bản đang dùng KHÔNG có/lùi hơn (vd `{mat[0]}`) — "
                       "cứu bằng nhánh `rescue/…` trước khi dời")
    return "YELLOW", "bản sao packed-refs — mọi nhánh trong đó đã nằm trong ref đang dùng, dời được"


def _xet_mot_ban_sao_git(repo: Path, git_dir: Path, rel: str, tb: str) -> tuple[str, str]:
    """(mức, lời giải thích) cho một bản sao xung đột trong `.git`; mức GREEN = rác git không đọc."""
    if rel.startswith("refs/"):
        return _xet_ref_ma(repo, git_dir / rel, _bo_hau_to(rel, tb) if tb else "")
    if rel.startswith("packed-refs"):
        return _xet_packed_refs_ma(repo, git_dir / rel)
    ten = rel.rsplit("/", 1)[-1]
    o_goc = "/" not in rel or re.fullmatch(r"worktrees/[^/]+/[^/]+", rel) is not None
    if o_goc and ten.lower().startswith("config"):
        return "YELLOW", ("bản sao cấu hình git — so `git config -f <tệp này> --list` với cấu hình đang dùng "
                          "(nhánh theo dõi, hooksPath…) rồi dời")
    if o_goc and ten.startswith("HEAD"):
        return "YELLOW", "HEAD bị ghi từ hai máy — kiểm `git status -sb` đang đứng đúng nhánh rồi dời"
    return "GREEN", ""


def check_git_conflict_copies(time_budget_s: float = 10.0) -> tuple[str, list[str]]:
    """Bản sao xung đột OneDrive NẰM TRONG `.git` của 2 repo — mục 1 prune `.git` nên không thấy (xem khối chú thích trên)."""
    host_stem = socket.gethostname().split(".")[0].lower()
    cac_thiet_bi = (host_stem, *THIET_BI_TRONG_GIT)
    order = {"GREEN": 0, "YELLOW": 1, "RED": 2}
    worst, notes = "GREEN", []
    for rel_repo, repo in GIT_REPOS:
        git_dir = repo / ".git"
        if not git_dir.is_dir():
            continue                                        # không phải repo, hoặc worktree phụ (`.git` là tệp)
        ban_sao, du = _quet_ban_sao_git(git_dir, cac_thiet_bi, time_budget_s)
        if not du:
            notes.append(f"🟡 [{rel_repo}] quét `.git` quá {time_budget_s:.0f}s — chưa soi hết (OneDrive đang tải?)")
            worst = max(worst, "YELLOW", key=order.get)
        rac = []
        for rel, tb in sorted(ban_sao):
            muc, loi = _xet_mot_ban_sao_git(repo, git_dir, rel, tb)
            if muc == "GREEN":
                rac.append(rel)
                continue
            notes.append(f"{'🔴' if muc == 'RED' else '🟡'} [{rel_repo}] .git/{rel} — {loi}")
            worst = max(worst, muc, key=order.get)
        if rac:
            vd = ", ".join(rac[:3]) + (f" … (+{len(rac) - 3})" if len(rac) > 3 else "")
            notes.append(f"[{rel_repo}] {len(rac)} tệp rác trong .git (git không đọc tên có hậu tố máy — dấu hai máy từng "
                         f"ghi .git cùng lúc; dời ra ngoài OneDrive được): {vd}")
    return worst, notes


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


def check_recent_writes(window_min: int = 3, time_budget_s: float = 8.0) -> tuple[str, list[str]]:
    """Nhiều file vừa đổi trong ~3 phút → có thể PHIÊN KHÁC/máy kia đang chạy (đừng chồng lên).

    `time_budget_s` NHỎ HƠN mặc định của `_iter_files()` có chủ ý: kiểm này gọi
    `f.stat()` cho MỌI file (172.400 lượt trên cây thật, ~25s hết ngân sách mặc định)
    trong khi bản thân nó chỉ là tín hiệu 🟡 THAM KHẢO (khác conflict-copy là 🔴 chặn
    cứng) — không đáng trả phí đầy đủ 25s mỗi phiên cho một cảnh báo mềm. Quét được
    một phần lớn vẫn tốt hơn hẳn cap cũ 60.000 (luôn cùng một tập con cố định do thứ
    tự os.walk không đổi giữa các lần chạy), và tín hiệu bỏ sót ở đây không nguy hiểm
    bằng bỏ sót conflict-copy — không có sạch tuyệt đối, có xu hướng đủ dùng."""
    cutoff = NOW - window_min * 60
    # Nhiễu LUÔN thay đổi (macOS + bookkeeping của chính Claude Code phiên NÀY) → bỏ,
    # nếu không mục này không bao giờ về 🟢. Còn lại = ghi vào FILE HỆ THỐNG thật.
    NOISE = ("/.claude/sessions/", "/.claude/state/", "sync_safety_check")
    NOISE_NAMES = (".ds_store", "changed-files.jsonl", "active.json", "broadcast.md")
    recent = []
    for f in _iter_files(time_budget_s=time_budget_s):
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
        ("5. Bản sao xung đột TRONG .git (2 repo)", check_git_conflict_copies),
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
