#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Đọc KẾT QUẢ lượt tái kiểm rút bài kho gần nhất cho gói duyệt tuần — 28/09/2026 (N4).

Vì sao: tác vụ tháng `kiem-rut-bai-kho-thang` nối một dòng «KẾT THÚC chu_trinh_chung_cu (mã N)» vào
`state/kiem-rut-bai-kho.log`. `kiem_lich_nen.py` chỉ canh kỳ đó CÓ CHẠY hay không, không đọc MÃ. Nếu không ai đọc mã,
một phát hiện rút bài (mã 1) nằm im trong log cho tới lượt bác sĩ tự mở. Gói tuần là nơi bác sĩ chắc chắn đọc.

Luật (chỉ dòng KẾT THÚC CUỐI CÙNG có giá trị — một lượt sạch cũ không che lượt có phát hiện mới):
  🔴 mã 1 và còn trong cửa sổ tươi → có việc cần bác sĩ (nguồn bị rút/đáng ngờ) — đặt LÊN ĐẦU gói tuần.
  🟢 mã 0 và còn trong cửa sổ tươi → kho sạch về TOÀN VẸN KỸ THUẬT (không phải thẩm định nội dung).
  ⚪ còn lại: chưa có log / không có dòng KẾT THÚC / dòng cuối cũ hơn cửa sổ tươi / mã 2 (nền tảng không đáng tin) /
     mã lạ → «chưa đo được», KHÔNG được viết thành «kho sạch».
Cửa sổ tươi mặc định 35 ngày (kỳ tháng + 4 ngày trễ). Chỉ ĐỌC. Mã thoát: 0 🟢 · 1 🔴 · 3 ⚪.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
LOG_MAC_DINH = GOC / "state" / "kiem-rut-bai-kho.log"
_DONG = re.compile(r"=+ (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) : KẾT THÚC chu_trinh_chung_cu \(mã (-?\d+)\)")
MA_THOAT = {"🟢": 0, "🔴": 1, "⚪": 3}


def doc(duong: Path = LOG_MAC_DINH, hom_nay: dt.datetime | None = None, tuoi_toi_da: int = 35) -> dict:
    """Trả {muc, dong, luc, ma, tuoi_ngay} cho dòng KẾT THÚC cuối của log."""
    hom_nay = hom_nay or dt.datetime.now()
    try:
        van = duong.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {"muc": "⚪", "dong": f"⚪ Rút bài kho: chưa đo được — không có {duong.name} (tác vụ tháng chưa chạy "
                                     "trên máy này). KHÔNG coi là kho sạch."}
    cac = _DONG.findall(van)
    if not cac:
        return {"muc": "⚪", "dong": "⚪ Rút bài kho: chưa đo được — log không có dòng KẾT THÚC nào. KHÔNG coi là kho sạch."}
    luc_s, ma_s = cac[-1]
    luc, ma = dt.datetime.strptime(luc_s, "%Y-%m-%d %H:%M:%S"), int(ma_s)
    tuoi = (hom_nay - luc).days
    kq = {"luc": luc_s, "ma": ma, "tuoi_ngay": tuoi}
    if tuoi > tuoi_toi_da:
        kq.update(muc="⚪", dong=f"⚪ Rút bài kho: chưa đo được — lượt cuối {luc:%d/%m/%Y} (mã {ma}) đã {tuoi} ngày, "
                                f"quá {tuoi_toi_da} ngày (kỳ tháng có thể đã lỡ). KHÔNG coi là kho sạch.")
    elif ma == 1:
        kq.update(muc="🔴", dong=f"🔴 Rút bài kho ({luc:%d/%m/%Y}): CÓ phát hiện cần bác sĩ xem — chạy "
                                f"`python3 tools/chu_trinh_chung_cu.py --vong 3` để xem chi tiết từng nguồn.")
    elif ma == 0:
        kq.update(muc="🟢", dong=f"🟢 Rút bài kho ({luc:%d/%m/%Y}): không thấy nguồn bị rút — chỉ là toàn vẹn kỹ thuật, "
                                "không thay thẩm định nội dung.")
    elif ma == 2:
        kq.update(muc="⚪", dong=f"⚪ Rút bài kho ({luc:%d/%m/%Y}): chưa đo được — mã 2, nền tảng không đáng tin (nguồn "
                                "giả/thiếu cấu hình). KHÔNG coi là kho sạch.")
    else:
        kq.update(muc="⚪", dong=f"⚪ Rút bài kho ({luc:%d/%m/%Y}): chưa đo được — mã lạ {ma}. KHÔNG coi là kho sạch.")
    return kq


def main(argv: list[str] | None = None) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Đọc kết quả tái kiểm rút bài kho gần nhất (cho gói tuần)")
    ap.add_argument("--log", type=Path, default=LOG_MAC_DINH)
    ap.add_argument("--tuoi-toi-da", type=int, default=35, help="số ngày lượt cuối còn được coi là tươi")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    kq = doc(a.log, tuoi_toi_da=a.tuoi_toi_da)
    print(json.dumps(kq, ensure_ascii=False) if a.json else kq["dong"])
    return MA_THOAT[kq["muc"]]


if __name__ == "__main__":
    sys.exit(main())
