#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CHỦ ĐỀ NÀO CÓ DASHBOARD MÀ KHÔNG AI CANH? — chốt phủ giám sát.

VÌ SAO CÓ (14/08/2026)
======================
Kho có **46 chủ đề gốc** nhưng watchlist giám sát chỉ khai **30**. Chủ đề nằm ngoài
watchlist thì KHÔNG lần quét định kỳ nào tìm chứng cứ mới cho nó — bản cập nhật cứ
âm thầm cũ đi và **không có gì báo**. Đối chiếu tay 14/08 tìm ra 9 chủ đề như vậy,
trong đó có những mục bác sĩ gặp thường xuyên: đau đầu · IBS · thiếu máu · sốc phản
vệ ở trẻ · suy thượng thận · viêm dạ dày/H. pylori · viêm gan B · hidradenitis
suppurativa · kê đơn thuốc tâm thần kinh.

Đây là khoảng trống **im lặng nhất** trong cả dây chuyền: mọi chốt khác đều kiểm thứ
ĐÃ CÓ trong kho (nguồn thật chưa · rút bài chưa · mâu thuẫn không), không chốt nào
hỏi *"thứ đáng lẽ phải có mà chưa có thì sao"*.

VÌ SAO KHÔNG TỰ GHÉP
====================
Ghép "chủ đề gốc" với "mục watchlist" là phán đoán NGỮ NGHĨA. Dùng độ giống tên để
ghép sẽ vừa bỏ sót (`HuyetHoc` ↔ "Thiếu máu & Đa hồng cầu" không giống nhau chữ nào)
vừa ghép bừa (`Than` ↔ "Bệnh thận nhi"), và **cái giá của ghép nhầm là một dấu ✓ sai**
— hệ báo "đã canh" trong khi không ai canh. Đúng bài học BH28.
Nên bản đồ là **KHAI BÁO** trong `EBM-Dashboards/giam-sat-chu-de.json`; công cụ này
chỉ ĐỌC. Chủ đề chưa khai ⇒ báo **CHƯA KHAI BÁO**, không đoán hộ.

Mã thoát: 0 = mọi chủ đề đều đã khai · 1 = còn chủ đề chưa khai hoặc trỏ sai.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
DASH = REPO / "EBM-Dashboards"
BANDO = DASH / "giam-sat-chu-de.json"
WL = DASH / "watchlist.json"


def _nap_dang_ky():
    spec = importlib.util.spec_from_file_location(
        "dkcd_phu", REPO / "tools" / "dang_ky_chu_de.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main() -> int:
    ap = argparse.ArgumentParser(description="Kiểm chủ đề có dashboard mà không ai giám sát")
    ap.add_argument("--im-khi-on", action="store_true",
                    help="không in gì khi mọi chủ đề đã được khai (dùng cho hook)")
    a = ap.parse_args()

    if not BANDO.exists():
        print("⚠ Chưa có EBM-Dashboards/giam-sat-chu-de.json — không kiểm được độ phủ "
              "giám sát. Đây là 'chưa biết', KHÔNG phải 'đã phủ đủ'.")
        return 1
    bd = json.loads(BANDO.read_text(encoding="utf-8"))
    co_canh = bd.get("muc", {}) or {}
    khong_can = bd.get("khong_can", {}) or {}

    ten_wl = set()
    if WL.exists():
        ten_wl = {t.get("topic") for t in json.loads(WL.read_text(encoding="utf-8")).get("topics", [])
                  if t.get("active", True)}

    dk = _nap_dang_ky()
    _vd, _lat, theo_goc = dk.quet_kho()
    chu_de = sorted(theo_goc)

    chua_khai = [c for c in chu_de if c not in co_canh and c not in khong_can]
    # Trỏ tới một mục watchlist KHÔNG tồn tại (hoặc đã tắt) là dấu ✓ rỗng — nguy hiểm
    # hơn chưa khai, vì nó trông như đã canh.
    tro_sai = [(c, co_canh[c]) for c in chu_de
               if c in co_canh and ten_wl and co_canh[c] not in ten_wl]

    if a.im_khi_on and not chua_khai and not tro_sai:
        return 0

    da_canh = len([c for c in chu_de if c in co_canh])
    print(f"PHỦ GIÁM SÁT — {len(chu_de)} chủ đề gốc · {da_canh} có canh · "
          f"{len([c for c in chu_de if c in khong_can])} cố ý không canh · "
          f"{len(chua_khai)} CHƯA KHAI BÁO")

    if tro_sai:
        print("\n🔴 TRỎ SAI — khai là có canh nhưng mục watchlist không tồn tại/đã tắt:")
        for c, m in tro_sai:
            print(f"   {c} → {m!r}")
    if chua_khai:
        print("\n⚠ CHƯA KHAI BÁO — không lần quét định kỳ nào tìm chứng cứ mới cho các")
        print("  chủ đề này, và trước nay KHÔNG có gì báo:")
        for c in chua_khai:
            n = len({lc for _n, lc, _p in theo_goc[c]})
            print(f"   {c}  ({n} lát cắt)")
        print("\n  Sửa: thêm mục vào EBM-Dashboards/watchlist.json rồi khai ánh xạ trong")
        print("  EBM-Dashboards/giam-sat-chu-de.json (hoặc khai vào 'khong_can' kèm lý do).")
    if not chua_khai and not tro_sai:
        print("🟢 Mọi chủ đề có dashboard đều đã được khai (canh hoặc cố ý không canh).")
    print("\nChốt này chỉ ĐO độ phủ khai báo — không chứng minh lần quét đã CHẠY, và không")
    print("thay bác sĩ quyết chủ đề nào cần cập nhật trước. Cần bác sĩ kiểm chứng.")
    return 1 if (chua_khai or tro_sai) else 0


if __name__ == "__main__":
    raise SystemExit(main())
