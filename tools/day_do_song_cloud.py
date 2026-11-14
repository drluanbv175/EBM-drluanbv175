#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ĐẨY DỮ LIỆU ĐO SỐNG LÊN CLOUD — Mac tự commit + push đúng các tệp đo sống đã khai (14/11/2026).

VÌ SAO CÓ
=========
Bác sĩ chọn 14/11/2026 «Một chiều + tự động»: kho chứng cứ (dashboard, sổ cái, toàn văn, EndNote) ở lại OneDrive — hai
repo GitHub đều CÔNG KHAI và toàn văn có bản quyền — còn phiên Cloud chỉ đọc bản TÓM TẮT qua git. Hook SessionStart của
Mac đã tự sinh lại gương `cloud-mirror/trang-thai-chung-cu.json`, nhưng không gì commit/đẩy nó: đo 14/11, 7 tệp đo sống
(gương, sổ nguồn, cảnh báo 05–13/11) nằm chờ trên Mac từ 05/11 ⇒ phiên Cloud nhìn trạng thái cũ 9 ngày (họ BH41: bước
không ai chạy thì như không có). Công cụ này là mảnh còn thiếu; nối vào `tools/tu_sua_chua.py` để mỗi phiên Mac tự chạy.

CHỈ đụng DANH SÁCH TRẮNG `TEP_DO_SONG` — mọi thay đổi khác trong cây ĐỂ NGUYÊN (có thể là việc dở của phiên khác).
Rào trước khi ghi: không chạy trên Cloud · phải có EBM-Dashboards/ · nhánh master · master tua nhanh được theo origin ·
`sync_safety_check` không 🔴. Commit qua hook pre-commit như thường (KHÔNG --no-verify; hook chặn gương hạ cấp). Chỉ đẩy
khi MỌI commit cục bộ chưa lên origin đều chỉ chạm danh sách trắng. Đẩy lỗi mạng ⇒ giữ commit, lượt sau đẩy tiếp.
KHÔNG đẩy dashboard, sổ cái, toàn văn hay EndNote — những thứ đó không bao giờ rời OneDrive.

Dùng:  python3 tools/day_do_song_cloud.py              # chạy thử: in tệp sẽ commit/đẩy, không ghi gì
       python3 tools/day_do_song_cloud.py --ap-dung    # sinh lại gương, commit + push
       python3 tools/day_do_song_cloud.py --im-khi-on  # chỉ nói khi có việc (tu_sua_chua)
Mã thoát: 0 không còn gì phải đẩy (kể cả ⚪ không áp dụng: Cloud / vắng EBM-Dashboards) · 1 còn tệp/commit chờ (chạy
thử) hoặc đẩy/hỏi remote lỗi mạng · 2 từ chối (sai nhánh, 🔴 an toàn, không tua nhanh được, commit lạ chưa đẩy) ·
3 hook pre-commit chặn. Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
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
PY = sys.executable
NHANH = "master"
# Danh sách trắng: tệp ĐO SỐNG do máy sinh, đã track (hoặc thư mục đã mở trong .gitignore) — commit f643d6c/e98da81.
TEP_DO_SONG = ("cloud-mirror/trang-thai-chung-cu.json", "data/sources.json",
               "quality/eval/negative/mau-thuan-quet-that.log")
THU_MUC_DO_SONG = (("alerts", ".md"),)   # tệp trực tiếp trong thư mục, đúng đuôi


def thuoc_danh_sach_trang(rel: str) -> bool:
    rel = rel.replace("\\", "/")
    if rel in TEP_DO_SONG:
        return True
    for thu_muc, duoi in THU_MUC_DO_SONG:
        dau, _, ten = rel.partition("/")
        if dau == thu_muc and ten and "/" not in ten and ten.endswith(duoi):
            return True
    return False


def _git(repo: Path, *args: str, timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=timeout)


def tep_cho_commit(repo: Path) -> tuple[list[str], list[str]]:
    """(tệp danh sách trắng đã đổi/mới, tệp danh sách trắng bị XOÁ — không tự commit việc xoá)."""
    r = _git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    doi, xoa = [], []
    muc = r.stdout.split("\0")
    i = 0
    while i < len(muc):
        m = muc[i]
        i += 1
        if len(m) < 4:
            continue
        trang_thai, rel = m[:2], m[3:]
        if trang_thai[0] in "RC":   # đổi tên: mục kế là đường dẫn cũ
            i += 1
        if not thuoc_danh_sach_trang(rel):
            continue
        (xoa if "D" in trang_thai else doi).append(rel)
    return sorted(doi), sorted(xoa)


def commit_chua_day(repo: Path) -> tuple[list[str], list[str]]:
    """(commit chỉ chạm danh sách trắng, commit chạm tệp khác) có trên HEAD mà chưa có trên origin/master."""
    r = _git(repo, "rev-list", "--reverse", f"origin/{NHANH}..HEAD")
    sach, la = [], []
    for c in r.stdout.split():
        tep = _git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", c).stdout.split()
        (sach if tep and all(thuoc_danh_sach_trang(t) for t in tep) else la).append(c)
    return sach, la


def _sinh_guong(repo: Path, ep_ghi: bool) -> int:
    lenh = [PY, str(repo / "tools" / "xuat_trang_thai_cloud.py"), "--im-khi-on"] + (["--ep-ghi"] if ep_ghi else [])
    return subprocess.run(lenh, cwd=repo, timeout=900).returncode


def _an_toan(repo: Path) -> int:
    return subprocess.run([PY, str(repo / "tools" / "sync_safety_check.py")], cwd=repo, timeout=600,
                          capture_output=True).returncode


def chay(repo: Path, *, ap_dung: bool, im: bool = False, ep_ghi: bool = False, dash: Path | None = None,
         sinh_guong: Callable[[Path, bool], int] = _sinh_guong, an_toan: Callable[[Path], int] = _an_toan,
         moi_truong: dict | None = None) -> int:
    env = os.environ if moi_truong is None else moi_truong
    noi = (lambda *x: None) if im else print

    if str(env.get("CLAUDE_CODE_REMOTE", "")).lower() == "true":
        noi("⚪ phiên Cloud — đẩy dữ liệu đo sống chỉ chạy trên máy có EBM-Dashboards/ (Mac).")
        return 0
    dash = dash or (repo / "EBM-Dashboards")
    if not dash.is_dir():
        noi(f"⚪ không thấy {dash} — máy này không có kho chứng cứ, không có gì để đẩy.")
        return 0
    nhanh = _git(repo, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if nhanh != NHANH:
        print(f"⚠ cây gốc đang ở nhánh «{nhanh}», không phải {NHANH} — không tự commit dữ liệu đo sống.")
        return 2

    if ap_dung:
        try:
            lay = _git(repo, "fetch", "-q", "origin", NHANH, timeout=120)
        except subprocess.TimeoutExpired:
            lay = None
        if lay is None or lay.returncode != 0:
            print("🟡 không hỏi được GitHub (mạng?) — chưa commit, lượt sau thử lại.")
            return 1
        sau = _git(repo, "rev-list", "--count", f"HEAD..origin/{NHANH}").stdout.strip()
        if sau not in ("", "0"):
            tua = _git(repo, "merge", "--ff-only", "-q", f"origin/{NHANH}")
            if tua.returncode != 0:
                print(f"⚠ {NHANH} không tua nhanh được theo origin (có thay đổi trùng tệp hoặc lệch nhánh) — dừng, "
                      f"không commit. Xem: git status -sb")
                return 2
        sinh_guong(repo, ep_ghi)

    doi, xoa = tep_cho_commit(repo)
    sach, la = commit_chua_day(repo)
    if la:
        print(f"⚠ {NHANH} có {len(la)} commit cục bộ chưa đẩy chạm tệp NGOÀI danh sách đo sống — không tự đẩy "
              f"(việc của bác sĩ/phiên khác). Xem: git log origin/{NHANH}..HEAD")
        return 2
    for rel in xoa:
        print(f"⚠ {rel} bị xoá — không tự commit việc xoá; bác sĩ xem lại.")
    if not doi and not sach:
        noi("🟢 dữ liệu đo sống trên GitHub đã khớp máy này.")
        return 0
    if not ap_dung:
        print("DỮ LIỆU ĐO SỐNG CHƯA LÊN GITHUB (phiên Cloud đang nhìn bản cũ):")
        for rel in doi:
            print(f"   • {rel}")
        if sach:
            print(f"   • {len(sach)} commit đo sống cục bộ chưa đẩy")
        print("   → python3 tools/day_do_song_cloud.py --ap-dung")
        return 1

    if doi:
        if an_toan(repo) >= 2:
            print("🔴 sync_safety_check báo DỪNG — không commit (đợi OneDrive xanh).")
            return 2
        _git(repo, "add", "--", *doi)
        ngay = dt.date.today().strftime("%d/%m/%Y")
        than = "Tệp: " + ", ".join(doi) + "\n\nTự động trên Mac bằng tools/day_do_song_cloud.py (chỉ danh sách trắng đo sống)."
        cm = _git(repo, "commit", "-q", "-m", f"chore(do-song): gương Cloud + sổ nguồn + cảnh báo ({ngay}, tự động trên Mac)",
                  "-m", than, timeout=900)
        if cm.returncode != 0:
            _git(repo, "reset", "-q", "--", *doi)
            print("🔴 hook pre-commit chặn commit dữ liệu đo sống — đã bỏ stage, không đẩy gì:")
            print((cm.stdout + cm.stderr).strip()[-1500:])
            return 3
        print(f"✓ đã commit {len(doi)} tệp đo sống.")
    try:
        day = _git(repo, "push", "-q", "origin", f"HEAD:{NHANH}", timeout=180)
    except subprocess.TimeoutExpired:
        day = None
    if day is None or day.returncode != 0:
        print("🟡 đẩy lên GitHub lỗi (mạng?) — commit giữ cục bộ, lượt sau đẩy tiếp.")
        return 1
    print("✓ đã đẩy dữ liệu đo sống lên GitHub — phiên Cloud sẽ thấy trạng thái mới.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Đẩy dữ liệu đo sống (gương Cloud, sổ nguồn, cảnh báo) lên GitHub")
    ap.add_argument("--ap-dung", action="store_true", help="sinh lại gương, commit + push (mặc định chạy thử)")
    ap.add_argument("--im-khi-on", action="store_true", help="chỉ nói khi có việc")
    ap.add_argument("--ep-ghi", action="store_true", help="ép sinh lại gương (truyền cho xuat_trang_thai_cloud.py)")
    a = ap.parse_args(argv)
    return chay(REPO, ap_dung=a.ap_dung, im=a.im_khi_on, ep_ghi=a.ep_ghi)


if __name__ == "__main__":
    raise SystemExit(main())
