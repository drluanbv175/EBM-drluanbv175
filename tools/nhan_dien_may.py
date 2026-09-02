#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MỘT nguồn duy nhất cho câu hỏi «máy này là máy nào?» — dùng chung cho mọi công cụ sổ khai.

VÌ SAO CÓ (02/09/2026): `dong_bo_plugin_claude_codex.py` và `kiem_plugin_day_du.py` mỗi file
tự chép một bản `ten_may()` giống hệt nhau (Darwin→Mac · Windows→Windows · còn lại → tên
hệ điều hành). Phiên Claude Code trên WEB chạy Linux nên tự nhận là «Linux» — một cái tên
không có trong bất kỳ sổ khai nào, nên lane ⑤ (đối chiếu kho plugin với ý định) trên cloud
không biết mình phải có gì. Từ 02/09 bác sĩ quyết định cloud phải đủ plugin như local, nên
cloud cần một DANH TÍNH ổn định để khai ý định vào `sync/plugin-manifest.json`.

Hai bản chép là hai chỗ để phân kỳ (đúng lý do `tools/ban_sao_tran.py` ra đời ngày 28/08);
từ nay cả hai công cụ gọi vào đây.
"""
from __future__ import annotations

import os
import platform


def la_phien_cloud() -> bool:
    """True khi đang chạy trong Claude Code trên web (container dựng mới mỗi phiên)."""
    return os.environ.get("CLAUDE_CODE_REMOTE", "").strip().lower() == "true"


def ten_may() -> str:
    """'Cloud' | 'Mac' | 'Windows' | tên hệ điều hành khác (vd 'Linux' khi là máy Linux thật)."""
    if la_phien_cloud():
        return "Cloud"
    return {"Darwin": "Mac", "Windows": "Windows"}.get(
        platform.system(), platform.system() or "Khac")


if __name__ == "__main__":
    print(ten_may())
