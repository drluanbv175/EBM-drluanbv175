#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ĐỒNG BỘ TÁC VỤ LỊCH — nguồn git `sync/scheduled-tasks/` → bản chạy của app (`~/.claude/scheduled-tasks/`), 29/09/2026.

VÌ SAO CÓ
=========
Đo 29/09: 13/14 bản chạy SKILL.md trên Mac tụt hậu nguồn git — phần lớn là bản 17/08. Hệ quả: PR #58 (tác vụ chạy đa
nền) và các sửa sau đó KHÔNG có hiệu lực trên máy này suốt 6 tuần mà không ai biết, còn tác vụ mới
`kiem-rut-bai-kho-thang` (PR #57) chưa từng được tạo. CLAUDE.md §9 đã có luật «chép SKILL.md từ NGUỒN GIT sang runtime,
không chép ngược» — nhưng không gì chạy luật đó (họ BH41: công cụ/luật không ai gọi thì như không có).

PHẠM VI: chỉ các tác vụ PHẢI hoạt động theo `sync/lich-nen-ky-vong.json`. Mỗi tác vụ xếp một trong:
  • khop      — bản chạy trùng nguồn hiện tại;
  • tut_hau   — bản chạy trùng khít MỘT phiên bản CŨ của nguồn trong git ⇒ tự chép được (`--ap-dung`, sao lưu trước);
  • khac_rieng — bản chạy khác MỌI phiên bản nguồn (có sửa riêng) ⇒ KHÔNG chép đè, cần bác sĩ xem;
  • chua_tao  — có nguồn, không có bản chạy ⇒ tạo tác vụ trong app là việc của bác sĩ (máy KHÔNG tự tạo/xoá tác vụ).
Không có thư mục bản chạy (Cloud, máy chưa cài app) ⇒ ⚪ không đo được, mã 0 — không báo đỏ giả.

Dùng:  python3 tools/dong_bo_tac_vu_lich.py [--im-khi-on]      # mã 1 nếu có tác vụ tụt hậu
       python3 tools/dong_bo_tac_vu_lich.py --ap-dung            # chép nguồn → bản chạy cho tác vụ tụt hậu
       python3 tools/dong_bo_tac_vu_lich.py --can-bac-si         # mã 1 nếu có tác vụ chưa tạo / có sửa riêng
Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
SO_LUONG_PHIEN_BAN = 40          # số phiên bản nguồn gần nhất đem so khi tìm bản chạy tụt hậu


def thu_muc_ban_chay() -> Path:
    return Path(os.environ.get("EBM_TAC_VU_LICH_DIR") or (Path.home() / ".claude" / "scheduled-tasks"))


def tac_vu_ky_vong(repo: Path) -> list[str]:
    d = json.loads((repo / "sync" / "lich-nen-ky-vong.json").read_text(encoding="utf-8"))
    return [str(t["id"]) for t in d.get("tac_vu", []) if t.get("id")]


def _phien_ban_cu(repo: Path, rel: str) -> list[bytes] | None:
    """Nội dung các phiên bản của `rel` trong lịch sử git (mới → cũ), hoặc None nếu không đọc được git."""
    try:
        r = subprocess.run(["git", "-C", str(repo), "log", f"-n{SO_LUONG_PHIEN_BAN}", "--format=%H", "--", rel],
                           capture_output=True, timeout=60, check=True)
        ra = []
        for c in r.stdout.decode().split():
            s = subprocess.run(["git", "-C", str(repo), "show", f"{c}:{rel}"], capture_output=True, timeout=60)
            if s.returncode == 0:
                ra.append(s.stdout)
        return ra
    except (OSError, subprocess.SubprocessError):
        return None


def phan_loai(repo: Path, ban_chay: Path) -> dict[str, str]:
    """{id tác vụ: khop · tut_hau · khac_rieng · chua_tao · thieu_nguon · khong_do_duoc}."""
    ra: dict[str, str] = {}
    for ma in tac_vu_ky_vong(repo):
        nguon = repo / "sync" / "scheduled-tasks" / ma / "SKILL.md"
        dich = ban_chay / ma / "SKILL.md"
        if not nguon.exists():
            ra[ma] = "thieu_nguon"
        elif not dich.exists():
            ra[ma] = "chua_tao"
        elif dich.read_bytes() == nguon.read_bytes():
            ra[ma] = "khop"
        else:
            cu = _phien_ban_cu(repo, nguon.relative_to(repo).as_posix())
            if cu is None:
                ra[ma] = "khong_do_duoc"
            else:
                ra[ma] = "tut_hau" if dich.read_bytes() in cu else "khac_rieng"
    return ra


def ap_dung(repo: Path, ban_chay: Path, loai: dict[str, str]) -> tuple[list[str], Path | None]:
    """Chép nguồn → bản chạy cho tác vụ tụt hậu; sao lưu CẢ thư mục bản chạy (ngoài OneDrive) trước khi ghi."""
    can = [ma for ma, v in loai.items() if v == "tut_hau"]
    if not can:
        return [], None
    sao_luu = ban_chay.parent / f"{ban_chay.name}-backup-{dt.datetime.now():%Y%m%d-%H%M%S}"
    shutil.copytree(ban_chay, sao_luu)
    for ma in can:
        shutil.copyfile(repo / "sync" / "scheduled-tasks" / ma / "SKILL.md", ban_chay / ma / "SKILL.md")
    return can, sao_luu


_NHAN = {
    "tut_hau": "🟡 tụt hậu nguồn git (tự chép được, --ap-dung)",
    "khac_rieng": "🔴 bản chạy có sửa riêng — KHÔNG chép đè, cần bác sĩ xem",
    "chua_tao": "👤 chưa tạo trong app — bác sĩ tạo tác vụ (máy không tự tạo)",
    "thieu_nguon": "⚪ kỳ vọng có nhưng không thấy nguồn trong git",
    "khong_do_duoc": "⚪ không đọc được lịch sử git — không phân loại được",
}


def main() -> int:
    ap = argparse.ArgumentParser(description="Đồng bộ tác vụ lịch: nguồn git → bản chạy của app")
    ap.add_argument("--ap-dung", action="store_true", help="chép nguồn → bản chạy cho tác vụ tụt hậu (sao lưu trước)")
    ap.add_argument("--can-bac-si", action="store_true", help="mã 1 nếu có tác vụ chưa tạo hoặc có sửa riêng")
    ap.add_argument("--im-khi-on", action="store_true", help="chỉ nói khi có việc")
    a = ap.parse_args()

    ban_chay = thu_muc_ban_chay()
    if not ban_chay.is_dir():
        if not a.im_khi_on:
            print(f"⚪ Không có thư mục tác vụ lịch của app ({ban_chay}) — máy này không chạy tác vụ lịch, không đo được.")
        return 0
    loai = phan_loai(REPO, ban_chay)
    if a.ap_dung:
        da_chep, sao_luu = ap_dung(REPO, ban_chay, loai)
        if da_chep:
            print(f"✓ Đã chép nguồn → bản chạy: {', '.join(da_chep)} (sao lưu: {sao_luu})")
        loai = phan_loai(REPO, ban_chay)

    can_bac_si = {ma: v for ma, v in loai.items() if v in ("chua_tao", "khac_rieng")}
    quan_tam = can_bac_si if a.can_bac_si else {ma: v for ma, v in loai.items() if v != "khop"}
    if quan_tam:
        print(f"ĐỒNG BỘ TÁC VỤ LỊCH — nguồn: sync/scheduled-tasks · bản chạy: {ban_chay}")
        for ma, v in sorted(quan_tam.items()):
            print(f"   {ma}: {_NHAN[v]}")
    elif not a.im_khi_on:
        print(f"🟢 {len(loai)}/{len(loai)} tác vụ kỳ vọng khớp nguồn git.")
    if a.can_bac_si:
        return 1 if any(v in ("chua_tao", "khac_rieng") for v in loai.values()) else 0
    return 1 if any(v == "tut_hau" for v in loai.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
