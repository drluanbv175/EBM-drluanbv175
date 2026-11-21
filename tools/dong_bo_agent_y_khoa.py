#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PR CẶP cho agent: đưa `.claude/agents/*.md` đã sửa ở repo GỐC sang bản sao trong repo Y KHOA (21/11/2026).

VÌ SAO CÓ
=========
`.claude/agents/*.md` của repo gốc là nguồn DUY NHẤT; repo y khoa giữ bản sao y hệt (dùng bởi `runtime/agent_registry.py`,
khoá băm trong `runtime/manifests/agent_source_manifest.csv` + hằng `MANIFEST_SELF_CHECK_SHA256`). Ngày 20/11/2026 hai PR gốc
(#454 sửa `cap-nhat-guideline.md`, #456 sửa `_CONNECTOR-CHUNG-CU.md`) gộp mà KHÔNG có PR cặp: bản sao y khoa dạy agent «cổng chỉ
cảnh báo» trong khi cổng đã CHẶN; BH107 đỏ ở lượt nền 6 giờ sau. Làm PR cặp bằng tay gồm 5 bước dễ sót (chép tệp → sinh lại
manifest → dán SHA vào hằng → `--check` → commit có biến EBM_WORKSPACE_ROOT). Ý tưởng «kiểm lệch theo TRẠNG THÁI, im lặng khi
không đổi» mượn từ plugin research-superpowers (bác sĩ 21/11/2026: «Nếu Plugins không có giúp nâng cấp hệ thống thì không cài»
— plugin KHÔNG cài; chỉ dựng lại ý tưởng có ích trong hệ).

LÀM GÌ
======
  • Báo cáo (mặc định, chỉ đọc): so từng agent có ở CẢ hai repo — bản gốc (HEAD của checkout đang chạy) với bản trên
    `origin/<nhánh y khoa>` (đã fetch) và bản ở CÂY y khoa trên máy:
      - `can_pr_cap`  : gốc ≠ origin y khoa ⇒ cần PR cặp (`--ap-dung`);
      - `can_keo_cay` : origin đã trùng gốc nhưng cây y khoa trên máy chưa kéo ⇒ chỉ cần kéo cây (không mở PR trùng);
      - `chi_goc`     : agent chỉ có ở gốc ⇒ thêm agent mới vào y khoa là quyết định riêng (đổi số agent), máy không tự chép.
  • `--staged` (chốt pre-commit của repo gốc): agent đang STAGE khác bản origin y khoa ⇒ IN NHẮC kèm lệnh; LUÔN mã 0 — không chặn
    (PR cặp đi sau PR gốc vài phút–vài giờ là bình thường). Không gọi mạng: so với origin đã fetch lần gần nhất.
  • `--ap-dung`: tạo worktree `~/.ebm-worktrees/ykhoa-dong-bo-agent-<giờ>` từ `origin/<nhánh>`, chép NGUYÊN VĂN các tệp
    `can_pr_cap` (bản HEAD gốc), chạy `scripts/regenerate_agent_manifest.py --write`, thay SHA vào `MANIFEST_SELF_CHECK_SHA256` kèm một
    dòng chú thích ngày, chạy `--check`, commit (đặt EBM_WORKSPACE_ROOT để pre-commit y khoa tìm được chốt workspace). `--mo-pr` đẩy
    nhánh và mở PR bằng `gh`; không có cờ đó thì in lệnh đẩy/mở PR. KHÔNG tự gộp PR. Không chép agent chỉ có ở gốc.
Nguồn chép là bản ĐÃ COMMIT (HEAD) của checkout gốc — thay đổi chưa commit không bao giờ sang y khoa (có cảnh báo).

Dùng:  python3 tools/dong_bo_agent_y_khoa.py                     # báo cáo
       python3 tools/dong_bo_agent_y_khoa.py --ap-dung [--mo-pr]  # dựng PR cặp
       python3 tools/dong_bo_agent_y_khoa.py --staged             # chốt pre-commit (chỉ nhắc)
Mã thoát (báo cáo/--ap-dung): 0 khớp hết / đã dựng xong · 1 còn việc (PR cặp hoặc kéo cây) · 2 không đo được (vắng repo y khoa,
không đọc được origin) · 3 dựng PR cặp hỏng (manifest/--check/commit).
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
NHANH_Y_KHOA = "feat/r1-1-2-design-gap-remediation"
THU_MUC_AGENT = ".claude/agents"
TEP_REGISTRY = "runtime/agent_registry.py"
MAU_SHA_MOI = re.compile(r"Self-check SHA-256 của manifest MỚI:\s*([0-9a-f]{64})")
MAU_HANG_SHA = re.compile(r'(MANIFEST_SELF_CHECK_SHA256 = \(\n\s*")([0-9a-f]{64})("\n\))')


def goc_y_khoa(repo: Path = REPO) -> Path | None:
    """Repo y khoa: lồng (`repo/medical-ebm-automation`), anh em, hoặc dưới EBM_WORKSPACE_ROOT (worktree ngoài OneDrive)."""
    try:
        sp = importlib.util.spec_from_file_location("_dbay_bst", repo / "tools" / "ban_sao_tran.py")
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        p = m.duong_goc("medical-ebm-automation", repo)
    except Exception:  # noqa: BLE001
        p = None
    if p is None and os.environ.get("EBM_WORKSPACE_ROOT"):
        q = Path(os.environ["EBM_WORKSPACE_ROOT"]) / "medical-ebm-automation"
        p = q if q.exists() else None
    return p


def _git(repo: Path, *args: str, timeout: int = 60) -> tuple[int, bytes]:
    try:
        r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, timeout=timeout)
        return r.returncode, r.stdout
    except (OSError, subprocess.TimeoutExpired):
        return 1, b""


def doc_git(repo: Path, rev_duong: str) -> bytes | None:
    """`git show <rev>:<đường>` — None khi không có (tệp vắng ở rev đó, hoặc lỗi git)."""
    rc, out = _git(repo, "show", rev_duong)
    return out if rc == 0 else None


def phan_loai(ten_ds: list[str], doc_goc: Callable[[str], bytes | None], doc_origin: Callable[[str], bytes | None],
              doc_cay: Callable[[str], bytes | None]) -> list[dict]:
    """Phân loại từng agent theo ba bản (gốc · origin y khoa · cây y khoa trên máy). Hàm thuần — dễ kiểm."""
    ra = []
    for ten in sorted(set(ten_ds)):
        g = doc_goc(ten)
        if g is None:
            continue
        o = doc_origin(ten)
        if o is None:
            loai = "chi_goc"
        elif g != o:
            loai = "can_pr_cap"
        else:
            c = doc_cay(ten)
            loai = "can_keo_cay" if (c is not None and c != o) else "khop"
        ra.append({"ten": ten, "loai": loai})
    return ra


def cap_nhat_sha(van_ban: str, sha_moi: str, ghi_chu: str) -> str:
    """Thay SHA trong `MANIFEST_SELF_CHECK_SHA256 = (\\n    "<hex>"\\n)` và chèn MỘT dòng chú thích ngay trước hằng.
    Mẫu không khớp đúng một lần ⇒ ValueError (không đoán chỗ sửa)."""
    if not re.fullmatch(r"[0-9a-f]{64}", sha_moi):
        raise ValueError("SHA mới không phải 64 ký tự hex")
    if len(MAU_HANG_SHA.findall(van_ban)) != 1:
        raise ValueError("không thấy đúng MỘT hằng MANIFEST_SELF_CHECK_SHA256 dạng chuẩn")
    moi = MAU_HANG_SHA.sub(lambda m: m.group(1) + sha_moi + m.group(3), van_ban)
    return moi.replace("MANIFEST_SELF_CHECK_SHA256 = (", f"# {ghi_chu}\nMANIFEST_SELF_CHECK_SHA256 = (", 1)


def ten_agent_hai_ben(repo: Path, mea: Path, nhanh: str) -> list[str]:
    """Tên `*.md` ở thư mục agent của gốc (HEAD) hợp với của origin y khoa — đủ để thấy cả agent chỉ-gốc."""
    def ds(r: Path, rev: str) -> set[str]:
        rc, out = _git(r, "ls-tree", "--name-only", f"{rev}:{THU_MUC_AGENT}")
        return {x for x in out.decode("utf-8", "replace").split("\n") if x.endswith(".md")} if rc == 0 else set()
    return sorted(ds(repo, "HEAD") | ds(mea, f"origin/{nhanh}"))


def bao_cao(repo: Path, mea: Path | None, nhanh: str) -> tuple[int, list[dict], list[str]]:
    if mea is None or not (mea / ".git").exists():
        return 2, [], ["⚪ không thấy repo y khoa (lồng/anh em/EBM_WORKSPACE_ROOT) — không đo được"]
    if _git(mea, "rev-parse", "--verify", f"origin/{nhanh}")[0] != 0:
        return 2, [], [f"⚪ repo y khoa chưa có origin/{nhanh} — chạy `git -C {mea} fetch origin` rồi đo lại"]
    ds = phan_loai(ten_agent_hai_ben(repo, mea, nhanh),
                   lambda t: doc_git(repo, f"HEAD:{THU_MUC_AGENT}/{t}"),
                   lambda t: doc_git(mea, f"origin/{nhanh}:{THU_MUC_AGENT}/{t}"),
                   lambda t: (mea / THU_MUC_AGENT / t).read_bytes() if (mea / THU_MUC_AGENT / t).is_file() else None)
    pr = [x["ten"] for x in ds if x["loai"] == "can_pr_cap"]
    keo = [x["ten"] for x in ds if x["loai"] == "can_keo_cay"]
    chi = [x["ten"] for x in ds if x["loai"] == "chi_goc"]
    dong = [f"Agent gốc (HEAD) ↔ y khoa (origin/{nhanh}): {len(ds)} tệp · cần PR cặp {len(pr)} · cần kéo cây {len(keo)} · "
            f"chỉ có ở gốc {len(chi)}"]
    if pr:
        dong.append(f"  🟠 cần PR CẶP: {', '.join(pr)} → python3 tools/dong_bo_agent_y_khoa.py --ap-dung --mo-pr")
    if keo:
        dong.append(f"  🟡 origin y khoa đã trùng gốc, CÂY y khoa trên máy chưa kéo: {', '.join(keo)} → "
                    f"git -C \"{mea}\" pull --ff-only (khi không có thay đổi chưa commit chồng lấn của phiên khác)")
    if chi:
        dong.append(f"  ⓘ chỉ có ở gốc: {', '.join(chi)} — thêm agent vào y khoa là quyết định riêng (đổi số agent), máy không tự chép")
    chua_commit = _git(repo, "status", "--porcelain", "--", THU_MUC_AGENT)[1].decode("utf-8", "replace").strip()
    if chua_commit:
        dong.append("  ⚠ agent ở gốc có thay đổi CHƯA COMMIT — không sang y khoa; commit ở gốc trước rồi chạy lại")
    return (1 if (pr or keo) else 0), ds, dong


def canh_bao_staged(repo: Path, mea: Path | None, nhanh: str) -> list[str]:
    """Agent STAGE ở gốc mà khác bản origin y khoa ⇒ dòng nhắc. Không có gì / không đo được ⇒ danh sách rỗng (im lặng)."""
    rc, out = _git(repo, "diff", "--cached", "--name-only", "--diff-filter=AM", "--", f"{THU_MUC_AGENT}/*.md")
    ten = [Path(x).name for x in out.decode("utf-8", "replace").split("\n") if x.strip()] if rc == 0 else []
    if not ten or mea is None or _git(mea, "rev-parse", "--verify", f"origin/{nhanh}")[0] != 0:
        return []
    ds = phan_loai(ten, lambda t: doc_git(repo, f":{THU_MUC_AGENT}/{t}"),
                   lambda t: doc_git(mea, f"origin/{nhanh}:{THU_MUC_AGENT}/{t}"), lambda t: None)
    pr = [x["ten"] for x in ds if x["loai"] == "can_pr_cap"]
    if not pr:
        return []
    return [f"⚠ NHẮC PR CẶP: {len(pr)} agent đang commit ở gốc khác bản sao trong repo y khoa ({', '.join(pr)}).",
            "  Gộp PR gốc xong (hoặc ngay sau commit này) chạy: python3 tools/dong_bo_agent_y_khoa.py --ap-dung --mo-pr",
            "  (quên bước này ⇒ agent y khoa dạy luật cũ; BH107/hòm việc chỉ bắt được sau vài giờ — sự cố 20/11/2026)"]


def ap_dung(repo: Path, mea: Path, nhanh: str, ten: list[str], *, mo_pr: bool, luc: dt.datetime | None = None,
            chay: Callable[..., subprocess.CompletedProcess] = subprocess.run,
            goc_wt: Path | None = None) -> tuple[int, list[str]]:
    """Dựng PR cặp cho `ten` trong worktree mới của repo y khoa. Trả (mã, dòng báo cáo).
    `goc_wt` mặc định `~/.ebm-worktrees` (ngoài OneDrive, không ở /private/tmp — CLAUDE.md §0.7)."""
    luc = luc or dt.datetime.now()
    nhan = luc.strftime("%Y%m%d-%H%M")
    wt = (goc_wt or Path.home() / ".ebm-worktrees") / f"ykhoa-dong-bo-agent-{nhan}"
    nhanh_moi = f"claude/dong-bo-agent-{nhan}"
    if wt.exists():
        return 3, [f"✗ {wt} đã tồn tại — không ghi chồng"]
    r = chay(["git", "-C", str(mea), "worktree", "add", "-q", "-b", nhanh_moi, str(wt), f"origin/{nhanh}"],
             capture_output=True, text=True)
    if r.returncode != 0:
        return 3, [f"✗ tạo worktree hỏng: {(r.stderr or '').strip()[:300]}"]
    for t in ten:
        du_lieu = doc_git(repo, f"HEAD:{THU_MUC_AGENT}/{t}")
        if du_lieu is None:
            return 3, [f"✗ không đọc được HEAD:{THU_MUC_AGENT}/{t} ở gốc"]
        (wt / THU_MUC_AGENT / t).write_bytes(du_lieu)
    r = chay([sys.executable, "-B", "scripts/regenerate_agent_manifest.py", "--write"], cwd=wt, capture_output=True, text=True)
    m = MAU_SHA_MOI.search(r.stdout or "")
    if r.returncode != 0 or not m:
        return 3, [f"✗ sinh lại manifest hỏng (mã {r.returncode}) — worktree giữ ở {wt} để xem"]
    reg = wt / TEP_REGISTRY
    try:
        reg.write_text(cap_nhat_sha(reg.read_text(encoding="utf-8"), m.group(1),
                                    f"{luc:%d/%m/%Y}: đồng bộ bản sao {', '.join(ten)} với nguồn gốc "
                                    "(tools/dong_bo_agent_y_khoa.py)."),
                       encoding="utf-8", newline="\n")
    except ValueError as e:
        return 3, [f"✗ {e} — worktree giữ ở {wt}"]
    r = chay([sys.executable, "-B", "scripts/regenerate_agent_manifest.py", "--check"], cwd=wt, capture_output=True, text=True)
    if r.returncode != 0:
        return 3, [f"✗ regenerate_agent_manifest.py --check KHÔNG đạt — worktree giữ ở {wt}"]
    env = dict(os.environ)
    env.setdefault("EBM_WORKSPACE_ROOT", str(mea.parent if (mea.parent / ".githooks" / "pre-commit").exists() else repo))
    them = [f"{THU_MUC_AGENT}/{t}" for t in ten] + [TEP_REGISTRY, "runtime/manifests/agent_source_manifest.csv"]
    chay(["git", "-C", str(wt), "add", "--", *them], capture_output=True, text=True)
    tieu_de = f"chore(agents): đồng bộ bản sao {', '.join(ten)} với nguồn gốc"
    than = (f"Repo gốc đổi {len(ten)} tệp agent mà bản sao trong repo y khoa chưa nhận. Chép nguyên văn bản HEAD của gốc, "
            "sinh lại manifest (scripts/regenerate_agent_manifest.py --write), cập nhật MANIFEST_SELF_CHECK_SHA256, --check đạt. "
            "Dựng bằng tools/dong_bo_agent_y_khoa.py.\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>")
    r = chay(["git", "-C", str(wt), "commit", "-q", "-m", tieu_de, "-m", than], capture_output=True, text=True, env=env)
    if r.returncode != 0:
        return 3, [f"✗ commit hỏng (pre-commit?): {((r.stderr or '') + (r.stdout or '')).strip()[-400:]} — worktree {wt}"]
    dong = [f"✓ đã commit PR cặp ở {wt} (nhánh {nhanh_moi}): {', '.join(ten)}"]
    lenh_day = ["git", "-C", str(wt), "push", "-q", "-u", "origin", nhanh_moi]
    lenh_pr = ["gh", "pr", "create", "--repo", "drluanbv175/medical-ebm-automation", "--base", nhanh, "--head", nhanh_moi,
               "--title", tieu_de, "--body", than.split("\n\nCo-Authored-By")[0]
               + "\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)"]
    if not mo_pr:
        dong.append("  Đẩy + mở PR: thêm --mo-pr, hoặc tự chạy `git push` và `gh pr create` cho nhánh trên")
        return 0, dong
    r = chay(lenh_day, capture_output=True, text=True)
    if r.returncode != 0:
        return 3, dong + [f"✗ đẩy nhánh hỏng: {(r.stderr or '').strip()[-300:]}"]
    r = chay(lenh_pr, capture_output=True, text=True, cwd=wt)
    if r.returncode != 0:
        return 3, dong + [f"✗ mở PR hỏng: {(r.stderr or '').strip()[-300:]}"]
    return 0, dong + [f"✓ PR cặp: {(r.stdout or '').strip().splitlines()[-1] if (r.stdout or '').strip() else '(gh không in URL)'}"
                      " — bác sĩ gộp"]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="PR cặp cho agent gốc → bản sao repo y khoa (báo cáo mặc định)")
    ap.add_argument("--nhanh", default=NHANH_Y_KHOA, help="nhánh mặc định của repo y khoa")
    ap.add_argument("--staged", action="store_true", help="chốt pre-commit: chỉ nhắc, luôn mã 0")
    ap.add_argument("--ap-dung", action="store_true", help="dựng PR cặp trong worktree mới")
    ap.add_argument("--mo-pr", action="store_true", help="cùng --ap-dung: đẩy nhánh và mở PR bằng gh")
    a = ap.parse_args(argv)
    mea = goc_y_khoa(REPO)
    if a.staged:
        dong = canh_bao_staged(REPO, mea, a.nhanh)
        if dong:
            print("\n".join(dong), file=sys.stderr)
        return 0
    ma, ds, dong = bao_cao(REPO, mea, a.nhanh)
    print("\n".join(dong))
    if not a.ap_dung or ma == 2:
        return ma
    pr = [x["ten"] for x in ds if x["loai"] == "can_pr_cap"]
    if not pr:
        print("Không có tệp cần PR cặp.")
        return ma
    if shutil.which("git") is None:
        print("⚪ không có git")
        return 2
    ma2, dong2 = ap_dung(REPO, mea, a.nhanh, pr, mo_pr=a.mo_pr)
    print("\n".join(dong2))
    return ma2


if __name__ == "__main__":
    raise SystemExit(main())
