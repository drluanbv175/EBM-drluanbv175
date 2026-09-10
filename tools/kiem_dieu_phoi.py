#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ĐIỀU PHỐI AGENT — tham chiếu có phân giải được, agent có ai gọi, skill có nguồn không?

VÌ SAO CÓ (15/08/2026)
======================
Rà tầng điều phối lần đầu (14–15/08) cho ba bài học:

  1. **Phép dò ngây thơ tạo BÁO ĐỘNG GIẢ.** Bản đo đầu tiên dò tên `kebab-case` trong
     doctrine rồi so với danh sách AGENT — ra 6 "tham chiếu hỏng". Kiểm lại: 4 là SKILL
     trong `sync/skills/`, 1 là skill có nguồn ở thư mục khác
     (`skill-nghien-cuu-y-khoa-v5.2/`), 1 là skill chỉ có ở runtime. Tên agent và tên
     skill sống chung một mặt chữ (backtick) nhưng thuộc HAI SỔ ĐĂNG KÝ khác nhau —
     phân giải phải tra CẢ HAI, cộng runtime.
  2. **Phát hiện thật:** skill `nghien-cuu-ebm-tong-hop` (44K, 8 file) chạy ở runtime mà
     KHÔNG có nguồn ở đâu trong cây OneDrive — app dọn runtime (đã xảy ra nhiều lần) là
     mất trắng, và `dong_bo_skill.py` không hề biết nó tồn tại. Đã cứu về `sync/skills/`.
  3. Đồ thị điều phối hiện LÀNH: `dieu-phoi-lam-sang` gọi 23 agent, `dieu-phoi-nghien-cuu`
     gọi 31, không agent nào mồ côi. Chốt này giữ cho nó tiếp tục lành — thêm agent mới
     mà quên nối nhạc trưởng, hoặc đổi tên skill mà doctrine còn trỏ tên cũ, là chốt đỏ.

BA PHÉP KIỂM
============
  ① Tham chiếu backtick dạng tên-agent/skill phải PHÂN GIẢI được (agent ∪ skill nguồn ∪
    skill runtime). Chỉ báo tên KHÔNG phân giải được mà RẤT GIỐNG một tên thật (nghi đổi
    tên/gõ nhầm) — cố ý hẹp để không báo động giả trên từ vựng thường.
  ② Mỗi agent (trừ file hạ tầng `_*` và README) phải được ÍT NHẤT một file khác nhắc tới
    — agent không ai gọi là agent không tồn tại với dây chuyền (cùng lý BH41).
  ③ Mỗi skill ở RUNTIME phải có NGUỒN trong cây dự án — bắt đúng lớp lỗi vừa cứu.

Mã thoát: 0 = cả ba sạch · 1 = có việc cần xử lý.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
AG = REPO / ".claude" / "agents"

# ── HAI DANH SÁCH KHAI BÁO TƯỜNG MINH (đo 15/08/2026) — tránh báo động giả ──────
# Bản đầu của chốt này báo 22 skill "mất trắng khi app dọn runtime" — kiểm lại thì
# 20 là skill DỰNG SẴN của Anthropic (docx, pdf, pptx…), không phải của bác sĩ và
# không cần nguồn cục bộ; chỉ 2 là skill thật cần cứu. Khai báo thay vì suy đoán
# (BH28): skill lạ mới xuất hiện ở runtime mà không nguồn → vẫn ĐỎ, đúng như cần.
#
# VÁ 10/09/2026 (tái phát BH44): lần chạy lại báo 2 skill runtime không nguồn —
# `dieu-phoi-aipoch` (router tiếng Việt do bác sĩ/phiên trước tự viết cho plugin
# aipoch-medical-research, KHÔNG có bản dựng sẵn nào giống — đã cứu về
# sync/skills/dieu-phoi-aipoch/) và `setup-claude` (mô tả tiếng Anh "Guided
# setup — install role-matched plugins…", đúng khuôn SKILL_DUNG_SAN như
# `setup-cowork` đã có sẵn — có vẻ là tên mới của chính skill onboarding đó sau
# một bản cập nhật app, không phải skill riêng của dự án này). Thêm vào đây,
# không cứu vào sync/skills/, để không nhận nhầm skill của Anthropic là tài sản
# cần bảo vệ của bác sĩ.
SKILL_DUNG_SAN = {
    "algorithmic-art", "brand-guidelines", "canvas-design", "consolidate-memory",
    "doc-coauthoring", "docx", "explain-usage", "import-memory", "internal-comms", "learn",
    "mcp-builder", "morning", "pdf", "pptx", "schedule", "setup-claude", "setup-cowork",
    "skill-creator", "slack-gif-creator", "theme-factory", "web-artifacts-builder",
    "xlsx",
}
# Tên chỉ còn trong GHI CHÚ LỊCH SỬ về routine đã RETIRE / taskId đã đính chính —
# doctrine tự ghi rõ chúng "không tồn tại" (xem _BAN-DO-KET-NOI.md dòng 104,
# _LO-TRINH-HA-TANG.md dòng 22). Không phải điều phối hỏng; xoá chúng khỏi ghi chú
# sẽ mất dấu vết vì sao đã retire.
TEN_LICH_SU = {"antifacts-weekly-update", "giam-sat-chung-cu-noi-chung",
               "tu-kiem-dong-bo-agent"}


def _skill_nguon() -> set[str]:
    """Tên mọi skill CÓ NGUỒN trong cây dự án (thư mục chứa SKILL.md, quét nông)."""
    ra: set[str] = set()
    for goc in (REPO / "sync" / "skills", REPO / "Scheduled"):
        if goc.is_dir():
            ra |= {p.parent.name for p in goc.glob("*/SKILL.md")}
    # skill có nguồn ở thư mục riêng ngoài sync/skills (quét một tầng thư mục gốc)
    for p in REPO.glob("skill-*/*/SKILL.md"):
        ra.add(p.parent.name)
    return ra


def _skill_runtime() -> tuple[Path | None, set[str]]:
    goc = Path.home() / "Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin"
    for p in sorted(goc.glob("*/*/skills")) if goc.is_dir() else []:
        # Bỏ qua thư mục `.bak-*` — đó là SAO LƯU do dong_bo_skill.py tạo trước khi ghi
        # đè (cơ chế phục hồi có chủ ý), không phải skill cần nguồn. Bản đầu của chốt
        # này đếm chúng là "skill mất nguồn" ngay lượt chạy sau một lần --ap-dung —
        # tức chốt tự báo động về dấu vết của chính quy trình đồng bộ. Chúng nằm ngoài
        # phạm vi ①②③; dọn định kỳ là việc riêng, không phải lỗi điều phối.
        return p, {x.parent.name for x in p.glob("*/SKILL.md")
                   if ".bak-" not in x.parent.name}
    return None, set()


def main() -> int:
    ap = argparse.ArgumentParser(description="Kiểm điều phối agent + phân giải tham chiếu")
    ap.add_argument("--im-khi-on", action="store_true", help="im lặng khi sạch (hook)")
    a = ap.parse_args()

    agent = {p.stem for p in AG.glob("*.md") if not p.name.startswith("_") and p.stem != "README"}
    nguon = _skill_nguon()
    rt_path, rt = _skill_runtime()
    phan_giai = agent | nguon | rt

    # ① tham chiếu nghi hỏng — không phân giải được mà giống một tên thật
    nghi_hong: dict[str, list[str]] = {}
    duoc_goi: set[str] = set()
    for p in sorted(AG.glob("*.md")):
        s = p.read_text(encoding="utf-8", errors="replace")
        for m in set(re.findall(r"`([a-z][a-z0-9-]{3,44})`", s)):
            if m in phan_giai:
                if m in agent and m != p.stem:
                    duoc_goi.add(m)
                continue
            if "-" not in m or m.startswith(("--", "tools", "run-")) or "." in m:
                continue
            if m in TEN_LICH_SU:
                continue
            # chỉ nghi khi giống RẤT DÀI một tên thật — dấu hiệu đổi tên/gõ nhầm
            if any(t[:10] == m[:10] for t in phan_giai if len(t) >= 10 and len(m) >= 10):
                nghi_hong.setdefault(m, []).append(p.name)

    # ② agent không ai gọi
    mo_coi = sorted(agent - duoc_goi)

    # ③ skill runtime không nguồn
    khong_nguon = sorted(rt - nguon - SKILL_DUNG_SAN)

    sach = not nghi_hong and not mo_coi and not khong_nguon
    if a.im_khi_on and sach:
        return 0

    print("=" * 70)
    print("  ĐIỀU PHỐI AGENT — tham chiếu · phủ điều phối · nguồn skill")
    print("=" * 70)
    print(f"  {len(agent)} agent · {len(nguon)} skill nguồn · {len(rt)} skill runtime"
          + ("" if rt_path else " (KHÔNG thấy runtime — chưa kiểm được ③)"))

    if nghi_hong:
        print(f"\n🔴 ① {len(nghi_hong)} tham chiếu KHÔNG phân giải được (nghi đổi tên/gõ nhầm):")
        for t, fs in sorted(nghi_hong.items()):
            print(f"   `{t}` ← {', '.join(fs[:4])}")
    else:
        print("  ✓ ① mọi tham chiếu agent/skill đều phân giải được")

    if mo_coi:
        print(f"\n🔴 ② {len(mo_coi)} agent KHÔNG file nào gọi tới — với dây chuyền là không tồn tại:")
        for t in mo_coi:
            print(f"   · {t}")
    else:
        print(f"  ✓ ② {len(agent)} agent đều có đường điều phối tới")

    if khong_nguon:
        print(f"\n🔴 ③ {len(khong_nguon)} skill runtime KHÔNG CÓ NGUỒN — app dọn runtime là mất trắng,")
        print("     và dong_bo_skill.py không biết chúng tồn tại:")
        for t in khong_nguon:
            print(f"   · {t}   → cứu: cp -R \"<runtime>/{t}\" sync/skills/")
    elif rt_path:
        print(f"  ✓ ③ {len(rt)} skill runtime đều có nguồn")

    print("-" * 70)
    print("🟢 Điều phối sạch." if sach else "🔴 Có việc cần xử lý — xem trên.")
    print("   Chốt kiểm CẤU TRÚC điều phối, không kiểm nội dung doctrine. Cần bác sĩ kiểm chứng.")
    return 0 if sach else 1


if __name__ == "__main__":
    raise SystemExit(main())
