#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kiểm SKILL tác vụ lịch (sync/scheduled-tasks/*/SKILL.md) chạy được trên CẢ Mac lẫn Windows — 28/09/2026 (N3).

Vì sao: trước 28/09, 12/14 SKILL viết cứng `/Users/nguyenluan/Library/CloudStorage/...` và `/tmp/...` — chép sang
máy Windows theo sync/scheduled-tasks/README.md là tác vụ chạy vào đường dẫn không tồn tại. Luật (mỗi SKILL):

  L1  Không đường dẫn tuyệt đối của MỘT người dùng (`/Users/<tên>`, `/home/<tên>/`) và không `/tmp/`.
  L2  Có đúng một khối nền tảng:
      · «NỀN TẢNG: macOS + Windows» kèm dòng `- macOS:` + `- Windows:` và quy tắc đổi `py -3`; HOẶC
      · «NỀN TẢNG: CHỈ CHẠY TRÊN MAC» kèm «Windows: DỪNG».
  L3  Gọi script bash (`bash <tệp>.sh`) ⇒ bắt buộc khối CHỈ-MAC (Windows không có bash mặc định).
  L4  Khối CHỈ-MAC mà không gọi script bash nào ⇒ lỗi (đánh dấu thừa làm Windows mất tác vụ chạy được).

Chỉ ĐỌC. Mã thoát: 0 đạt · 1 có vi phạm · 2 không có thư mục/tệp để kiểm.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
THU_MUC = REPO / "sync" / "scheduled-tasks"

DA_NEN = "NỀN TẢNG: macOS + Windows"
CHI_MAC = "NỀN TẢNG: CHỈ CHẠY TRÊN MAC"
_NEO_NGUOI_DUNG = re.compile(r"/Users/[A-Za-z0-9._-]+|/home/[A-Za-z0-9._-]+/")
_TMP = re.compile(r"(?<![\w.])/tmp/")
_GOI_BASH = re.compile(r"\bbash\s+\S+\.sh\b")


def kiem_van_ban(van_ban: str) -> list[str]:
    """Trả danh sách vi phạm (rỗng = đạt) cho nội dung MỘT SKILL."""
    loi: list[str] = []
    neo = sorted(set(_NEO_NGUOI_DUNG.findall(van_ban)))
    if neo:
        loi.append(f"L1 đường dẫn neo một người dùng: {', '.join(neo[:3])}")
    if _TMP.search(van_ban):
        loi.append("L1 dùng /tmp/ — Windows không có; ghi tệp tạm vào state/")
    dong = [d.strip() for d in van_ban.splitlines()]
    co_da = any(d.startswith(DA_NEN) for d in dong)
    co_mac = any(d.startswith(CHI_MAC) for d in dong)
    goi_bash = bool(_GOI_BASH.search(van_ban))
    if co_da == co_mac:
        loi.append("L2 cần ĐÚNG MỘT khối «NỀN TẢNG: macOS + Windows» hoặc «NỀN TẢNG: CHỈ CHẠY TRÊN MAC»")
    elif co_da:
        if not any(d.startswith("- macOS:") for d in dong) or not any(d.startswith("- Windows:") for d in dong):
            loi.append("L2 khối đa nền thiếu dòng `- macOS:` hoặc `- Windows:`")
        if "py -3" not in van_ban:
            loi.append("L2 khối đa nền thiếu quy tắc đổi `python3` → `py -3` cho Windows")
        if goi_bash:
            loi.append("L3 gọi script bash nhưng khai đa nền — Windows không chạy được; đổi sang CHỈ CHẠY TRÊN MAC")
    else:
        dong_mac = next(d for d in dong if d.startswith(CHI_MAC))
        if "Windows: DỪNG" not in dong_mac:
            loi.append("L2 khối CHỈ-MAC phải dặn «Windows: DỪNG» ngay trên dòng đó")
        if not goi_bash:
            loi.append("L4 khai CHỈ-MAC nhưng không gọi script bash nào — tác vụ lẽ ra chạy được trên Windows")
    return loi


def kiem_thu_muc(thu_muc: Path = THU_MUC) -> dict[str, list[str]]:
    """{tên tác vụ: [vi phạm]} cho mọi SKILL; thư mục vắng/rỗng ⇒ {}."""
    if not thu_muc.is_dir():
        return {}
    return {f.parent.name: kiem_van_ban(f.read_text(encoding="utf-8", errors="replace"))
            for f in sorted(thu_muc.glob("*/SKILL.md"))}


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # Windows cp1252 không in được tiếng Việt
    except (AttributeError, ValueError):
        pass
    kq = kiem_thu_muc(Path(argv[0]) if argv else THU_MUC)
    if not kq:
        print(f"⚪ Không có SKILL tác vụ lịch nào để kiểm ở {THU_MUC}")
        return 2
    xau = {k: v for k, v in kq.items() if v}
    for ten, loi in kq.items():
        print(f"  {'🔴' if loi else '🟢'} {ten}")
        for x in loi:
            print(f"      - {x}")
    print(f"\nKẾT: {len(kq) - len(xau)}/{len(kq)} tác vụ chạy đúng nền tảng đã khai. Cần bác sĩ kiểm chứng.")
    return 1 if xau else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
