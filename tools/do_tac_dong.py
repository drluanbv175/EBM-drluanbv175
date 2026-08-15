#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ĐO TÁC ĐỘNG THỰC HÀNH — hệ có ĐƯỢC DÙNG thật không, và dùng vào thẻ nào (Tầng-2).

Vì sao: cả hai hệ đo rất kỹ «chứng cứ có đúng không» nhưng chưa từng đo «bác sĩ
có dùng không» — vòng phản hồi thực hành là mảnh cuối của EBM (bước Đánh giá).
Nguồn số DUY NHẤT: `state/nhat-ky-tac-dong.jsonl` do tra_diem_kham ghi — thiết kế
KHÔNG-PII TỪ GỐC (chỉ id thẻ/miss/thời điểm/độ trễ; câu hỏi thô không bao giờ lưu).

Trung thực phép đo — ba điều KHÔNG được suy:
  · «0 lượt» = chưa dùng kênh điểm-khám, KHÔNG suy «hệ vô dụng» (bác sĩ còn dùng
    dashboard/bản đọc — các kênh đó không đo ở đây).
  · Lượt tra ≠ lượt ÁP DỤNG lâm sàng — áp dụng là Cổng A, hệ không nhìn thấy.
  · miss cao ở một cụm = TÍN HIỆU mở rộng watchlist (đã tự ghi kênh LÔ 5),
    không phải lỗi của ai.

Dùng:  python3 tools/do_tac_dong.py [--ngay 30]
Mã thoát: 0 (kể cả khi log trống — «chưa có số» là kết quả hợp lệ).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from collections import Counter
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

GOC = Path(__file__).resolve().parents[1]
LOG = GOC / "state" / "nhat-ky-tac-dong.jsonl"


def main() -> int:
    ap = argparse.ArgumentParser(description="Đo mức dùng kênh điểm-khám (không PII)")
    ap.add_argument("--ngay", type=int, default=30, help="cửa sổ ngày (mặc định 30)")
    a = ap.parse_args()
    print("=" * 64)
    print(f"  ĐO TÁC ĐỘNG THỰC HÀNH — kênh điểm-khám, {a.ngay} ngày gần nhất")
    print("=" * 64)
    if not LOG.exists():
        print("  Chưa có lượt tra nào được ghi — nhật ký bắt đầu từ 16/08/2026.")
        print("  «Chưa có số» là kết quả hợp lệ, KHÔNG suy ra hệ vô dụng "
              "(dashboard/bản đọc không đo ở kênh này). Cần bác sĩ kiểm chứng.")
        return 0
    tu = dt.datetime.now() - dt.timedelta(days=a.ngay)
    luot, miss, ms_tong = 0, 0, 0
    the = Counter()
    theo_gio = Counter()
    for dong in LOG.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(dong)
            luc = dt.datetime.fromisoformat(r["luc"])
        except (json.JSONDecodeError, KeyError, ValueError):
            continue
        if luc < tu:
            continue
        luot += 1
        ms_tong += r.get("ms", 0)
        theo_gio[luc.hour] += 1
        if r.get("miss"):
            miss += 1
        for t in r.get("khop", []):
            if t:
                the[t] += 1
    if not luot:
        print(f"  0 lượt trong {a.ngay} ngày — xem ghi chú «chưa có số» ở docstring.")
        return 0
    print(f"  Lượt tra: {luot} · miss (ngoài giám sát): {miss} "
          f"({miss * 100 // luot}%) · độ trễ TB {ms_tong // luot} ms")
    if the:
        print("  Thẻ được tra nhiều nhất:")
        for tid, n in the.most_common(8):
            print(f"    {n:3} × {tid}")
    if theo_gio:
        dinh = theo_gio.most_common(3)
        print("  Khung giờ hay tra: " + " · ".join(f"{h}h ({n})" for h, n in dinh))
    if miss:
        print(f"\n  → {miss} lượt miss đã tự vào kênh ứng-viên-watchlist (LÔ 5) — "
              "xem state/cau-hoi-chua-giam-sat.jsonl khi rà tuần.")
    print("\n  Lượt tra ≠ lượt ÁP DỤNG (Cổng A của bác sĩ — hệ không nhìn thấy). "
          "Cần bác sĩ kiểm chứng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
