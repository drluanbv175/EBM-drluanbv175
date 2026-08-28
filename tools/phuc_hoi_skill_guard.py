#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PHỤC HỒI SKILL MẤT KHỐI EBM-VN-GUARD — tự sửa máy móc, chạy được CẢ HAI MÁY (27/08/2026).

VÌ SAO CÓ — sự cố đã TÁI PHÁT 2 LẦN, không phải giả định
=========================================================
26/08: 2 skill `peer-review`/`literature-review` trong sync/skills/ bị GHI ĐÈ TRỌN
bằng nội dung một hệ skill khác không liên quan («Claude Science» — tiếng Anh, từ
khoá tiếng Hàn, kernel.py, reviewer profiles X-quang). Bác sĩ quyết «khôi phục ngay»;
đã cứu từ Cowork runtime + thêm chốt BH77.
27/08 SÁNG HÔM SAU: TÁI PHÁT — mtime bản hỏng là 21/08 chứng tỏ OneDrive đồng bộ lại
bản cũ TỪ MÁY KIA (máy Windows chưa từng được sửa); lần này CẢ Cowork runtime cũng
nhiễm (hook dong_bo_skill --ap-dung đẩy nhầm bản hỏng sang trước khi ai kịp nhìn).
Nguồn cứu duy nhất còn lại là GIT HEAD — nội dung hỏng chưa bao giờ được commit.

BH77 chỉ BÁO. Tool này TỰ SỬA — và vì `tu_sua_chua.py` chạy qua hook SessionStart
trên CẢ HAI MÁY, máy Windows sẽ tự vá ngay lần mở Claude Code kế tiếp, chặn vòng
lặp «Mac sửa → Windows đè lại» mà không cần bác sĩ gõ tay lệnh nào.

ĐIỀU KIỆN HÀNH ĐỘNG — fail-safe, chống sửa oan
===============================================
Chỉ khôi phục một skill khi HỘI ĐỦ CẢ HAI:
  (a) bản git HEAD của SKILL.md CÓ chuỗi «EBM-VN-GUARD»;
  (b) bản working-tree MẤT chuỗi đó (hoặc SKILL.md biến mất).
Bác sĩ chủ ý sửa skill sẽ không xoá nguyên khối guard bắt buộc; và một thay đổi
chủ ý thật sự phải đi qua commit — lúc đó HEAD đổi theo và tool tự im lặng.
Danh sách skill canh KHÔNG hardcode: quét động mọi skill mà HEAD có marker —
thêm skill guard mới vào git là tự được canh, khỏi sửa hai nơi (bài học BH74).

Trước khi ghi đè bất cứ gì: CÁCH LY bản hỏng vào sync/skills/_quarantine-guard/
(gitignored) — không mất dữ liệu, bác sĩ muốn xem thì còn nguyên.

Runtime Cowork (chỉ có trên Mac): nếu bản runtime của skill đó CŨNG mất marker
thì thay bằng bản nguồn vừa khôi phục; còn marker thì không đụng. Trên Windows
(không có thư mục runtime) phần này tự bỏ qua — BH05/BH55.

Dùng:
  python3 tools/phuc_hoi_skill_guard.py --im-khi-on   # kiểm, im khi ổn (exit 1 khi có skill hỏng)
  python3 tools/phuc_hoi_skill_guard.py --ap-dung     # khôi phục thật
  python3 tools/phuc_hoi_skill_guard.py               # báo cáo, không ghi
Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
NGUON = REPO / "sync" / "skills"
MARKER = "EBM-VN-GUARD"
QUARANTINE = NGUON / "_quarantine-guard"


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(REPO), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def skill_guard_theo_head() -> list[str]:
    """Tên các skill mà bản HEAD của SKILL.md chứa marker — nguồn sự thật động."""
    ra: list[str] = []
    r = _git("ls-tree", "-r", "--name-only", "HEAD", "sync/skills")
    if r.returncode != 0:
        return ra
    for line in r.stdout.splitlines():
        p = Path(line)
        if p.name != "SKILL.md" or len(p.parts) != 4:  # sync/skills/<ten>/SKILL.md
            continue
        show = _git("show", f"HEAD:{line}")
        if show.returncode == 0 and MARKER in show.stdout:
            ra.append(p.parts[2])
    return sorted(ra)


def bi_mat_guard(ten: str) -> bool:
    f = NGUON / ten / "SKILL.md"
    if not f.is_file():
        return True
    try:
        return MARKER not in f.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return True


def tim_runtime() -> Path | None:
    goc = Path.home() / "Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin"
    if not goc.is_dir():  # Windows / máy chưa có Cowork — bỏ qua, không phải lỗi
        return None
    ung_vien = sorted(goc.glob("*/*/skills"), key=lambda p: p.stat().st_mtime, reverse=True)
    return ung_vien[0] if ung_vien else None


def phuc_hoi(ten: str, ap_dung: bool) -> list[str]:
    """Khôi phục 1 skill từ HEAD. Trả các dòng tường thuật."""
    ra: list[str] = []
    thu_muc = NGUON / ten
    if not ap_dung:
        ra.append(f"   • {ten}: SẼ cách ly bản hiện tại rồi khôi phục từ git HEAD")
        return ra
    dau = datetime.now().strftime("%Y%m%d-%H%M%S")
    if thu_muc.is_dir():
        QUARANTINE.mkdir(parents=True, exist_ok=True)
        noi_cach_ly = QUARANTINE / f"{ten}-{dau}"
        shutil.copytree(thu_muc, noi_cach_ly)
        ra.append(f"   • {ten}: cách ly bản hỏng → {noi_cach_ly.relative_to(REPO)}")
    r1 = _git("checkout", "--", f"sync/skills/{ten}")
    r2 = _git("clean", "-fd", f"sync/skills/{ten}")
    if r1.returncode != 0:
        ra.append(f"   ✗ {ten}: git checkout lỗi — {r1.stderr.strip()[:120]}")
        return ra
    don = [ln for ln in r2.stdout.splitlines() if ln.strip()]
    ra.append(f"   • {ten}: đã khôi phục từ HEAD (+dọn {len(don)} mục lạ)")
    runtime = tim_runtime()
    if runtime is not None:
        rt = runtime / ten
        rt_skill = rt / "SKILL.md"
        rt_nhiem = (not rt_skill.is_file()) or (
            MARKER not in rt_skill.read_text(encoding="utf-8", errors="replace"))
        if rt_nhiem:
            if rt.is_dir():
                shutil.rmtree(rt)
            shutil.copytree(thu_muc, rt,
                            ignore=shutil.ignore_patterns("__pycache__", "*.vi-bak"))
            ra.append(f"   • {ten}: runtime Cowork cũng nhiễm → đã thay bằng bản sạch")
    return ra


def main() -> int:
    ap = argparse.ArgumentParser(description="Phục hồi skill mất khối EBM-VN-GUARD")
    ap.add_argument("--ap-dung", action="store_true", help="khôi phục thật")
    ap.add_argument("--im-khi-on", action="store_true", help="im lặng khi mọi skill còn guard")
    a = ap.parse_args()

    canh = skill_guard_theo_head()
    if not canh:
        # Không đọc được HEAD (repo hỏng?) — KHÔNG kết luận gì, không phải "ổn" (BH08)
        print("⚠ Không đọc được danh sách skill guard từ git HEAD — bỏ qua, kiểm tay git.")
        return 0
    hong = [t for t in canh if bi_mat_guard(t)]
    if not hong:
        if not a.im_khi_on:
            print(f"🟢 {len(canh)}/{len(canh)} skill còn khối {MARKER} (đối chiếu git HEAD).")
        return 0

    print(f"🔴 {len(hong)}/{len(canh)} skill MẤT khối {MARKER} (HEAD có, working-tree mất "
          f"— dấu hiệu ghi đè lạ, xem BH77): {', '.join(hong)}")
    for ten in hong:
        for dong in phuc_hoi(ten, a.ap_dung):
            print(dong)
    if a.ap_dung:
        con = [t for t in hong if bi_mat_guard(t)]
        if con:
            print(f"   ✗ CÒN HỎNG sau khôi phục: {', '.join(con)} — cần bác sĩ xem tay.")
            return 1
        print("   ✓ Đã khôi phục xong toàn bộ. Cần bác sĩ kiểm chứng.")
        return 0
    print("   (chưa ghi gì — thêm --ap-dung để khôi phục thật)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
