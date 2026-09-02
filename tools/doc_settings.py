#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""doc_settings.py — Đọc cấu hình người dùng của Claude Code từ ĐÚNG mọi file đang có hiệu lực.

VÌ SAO CÓ (02/09/2026). Sáng hôm đó chốt kho báo 🔴 gắt: «DANH SÁCH SKILL VƯỢT NGÂN
SÁCH… skillListingBudgetFraction=0.01, ĐANG DÙNG MẶC ĐỊNH», kèm 8 bộ medsci trùng
«MỚI so với mốc», kho phồng 842 → 1322 skill. Cả hai đều SAI.

Sự thật: `~/.claude/settings.json` biến mất, nhưng cấu hình của bác sĩ vẫn còn nguyên ở
`~/.claude/settings.local.json` (budget 0,08 · maxDescChars 80 · đủ 8 cờ `false`).
Claude Code đọc CẢ HAI file và bản `.local` ĐÈ LÊN bản chung; công cụ của ta thì chỉ đọc
`settings.json`, nên thấy trống rồi kết luận «chưa đặt» và «tất cả plugin đang bật».

Đây đúng họ lỗi đã lặp nhiều lần trong hệ này — **đo đúng, nhưng đo nhầm chỗ** (BH74:
catalog quét `.claude-science` trong khi lệnh chạy ở Cowork). Hại theo hướng nguy hiểm
nhất: báo động ĐỎ giả. Một bức tường đỏ sai dạy người ta bỏ qua cả cảnh báo thật (BH08),
và ở đây nó còn xúi làm hai việc gây hại — `--ghi-moc` lúc kho đang phồng, và đặt lại
một khoá vốn đã đúng.

HỢP ĐỒNG:
  doc_settings()      → dict đã gộp; `.local` thắng khi trùng khoá.
  duong_dan_doc()     → danh sách file đã đọc thật (để báo cáo cho người dùng).
  duong_dan_ghi()     → file NÊN ghi khi cần sửa. Giữ nguyên lệ cũ: ưu tiên
                        `settings.json`; chỉ trả `.local` khi CHỈ có file đó — ghi vào
                        file không tồn tại rồi để bản `.local` đè lên là sửa mà không
                        có tác dụng, đúng kiểu hỏng im lặng doctrine vẫn chống.

KHÔNG bắt chước `json.load` rồi bỏ qua lỗi: file hỏng phải NÓI RA, vì im lặng ở đây
nghĩa là mọi chốt phía sau đo trên cấu hình rỗng.
"""
from __future__ import annotations

import json
from pathlib import Path

GOC = Path.home() / ".claude"
# Thứ tự = thứ tự ĐÈ: file sau đè file trước (khớp cách Claude Code gộp).
TEN_FILE = ("settings.json", "settings.local.json")


def duong_dan_doc(goc: Path | None = None) -> list[Path]:
    """Các file cấu hình THẬT SỰ tồn tại, theo thứ tự đè.

    `goc` = file settings CHÍNH. Truyền vào để chốt hồi quy tiêm được fixture: mỗi công
    cụ đưa hằng `SETTINGS` của chính nó, nên khi test gán `m.SETTINGS = <file tạm>` thì
    hàm này soi đúng thư mục tạm đó. Không truyền → dùng `~/.claude/`.
    (Bài học 02/09: bản đầu đọc thẳng đường dẫn thật, làm hỏng BH69 và BH81 — hai chốt
    đang chạy tốt — vì fixture không còn đường chen vào. Một chốt không tiêm được dữ
    liệu thử thì không chứng minh được điều gì.)
    """
    thu_muc = GOC if goc is None else goc.parent
    # Thứ tự đè LUÔN theo TEN_FILE, không theo file nào được truyền vào. Bản đầu xếp
    # `goc` lên trước rồi mới tới anh em, nên truyền `goc=settings.local.json` sẽ khiến
    # settings.json đè ngược lại bản .local — sai chiều mà chốt không bắt được (phép
    # đột biến đảo thứ tự TEN_FILE vẫn xanh). Neo vào TEN_FILE thì chiều đè là một.
    ds = [thu_muc / t for t in TEN_FILE]
    if goc is not None and goc.name not in TEN_FILE:
        ds.insert(0, goc)          # fixture đặt tên khác: đọc trước, để .local vẫn đè
    return [f for f in ds if f.is_file()]


def doc_settings(nghiem: bool = True, goc: Path | None = None) -> dict:
    """Gộp mọi file cấu hình đang có. `.local` đè `settings.json`.

    nghiem=True  → file hỏng thì ném lỗi (mặc định: thà dừng còn hơn đo trên dict rỗng).
    nghiem=False → bỏ qua file hỏng, dùng cho chốt chỉ-cảnh-báo.
    """
    gop: dict = {}
    for f in duong_dan_doc(goc):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            if nghiem:
                raise
            continue
        if isinstance(d, dict):
            gop.update(d)
    return gop


def duong_dan_ghi() -> Path:
    """File nên ghi khi cần khôi phục một khoá."""
    chinh, cuc_bo = GOC / TEN_FILE[0], GOC / TEN_FILE[1]
    if chinh.is_file():
        return chinh
    if cuc_bo.is_file():
        return cuc_bo
    return chinh          # chưa có file nào → dựng file chung
