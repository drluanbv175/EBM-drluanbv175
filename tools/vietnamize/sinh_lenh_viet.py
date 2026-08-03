#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sinh_lenh_viet.py — Sinh LỆNH TÊN TIẾNG VIỆT trỏ tới skill/agent có sẵn.

VÌ SAO CẦN: khi gõ `/`, bộ lọc chắc chắn khớp theo TÊN lệnh. Tên skill lại là
tiếng Anh (`calc-sample-size`, `check-reporting`), nên gõ "cỡ mẫu" không ra gì —
dù mô tả đã Việt hoá. Cách chắc chắn là tạo thêm lệnh MANG TÊN TIẾNG VIỆT trỏ về
đúng skill đó; tên đặt không dấu để gõ nhanh, không cần bật bộ gõ.

Bảng ánh xạ nằm ở `lenh_viet.json` — sửa ở đó rồi chạy lại script này.

KIỂM ĐÍCH: mỗi lệnh khai `dich` (tên skill/agent nó gọi). Script đối chiếu với
catalog_raw.json và TỪ CHỐI sinh lệnh trỏ vào thứ không có trên máy — một lệnh
gọi ra rồi báo "không tìm thấy skill" còn tệ hơn là không có lệnh.

Chạy: python3 tools/vietnamize/sinh_lenh_viet.py [--dry-run]
Sinh vào sync/commands-vi/, cài lên máy bằng sync/copy-commands-vi.sh
"""
from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
BANG = HERE / "lenh_viet.json"
RA = REPO / "sync/commands-vi"

MAU = """---
description: "{mo_ta}"
---

{than}
"""


def main() -> int:
    dry = "--dry-run" in sys.argv
    bang = json.loads(BANG.read_text("utf-8"))
    muc = json.loads((HERE / "catalog_raw.json").read_text("utf-8"))
    co_tren_may = {i["name"] for i in muc} | {i["invoke"] for i in muc}

    RA.mkdir(parents=True, exist_ok=True)
    tao, bo_qua, giu = 0, [], 0
    for ten, v in bang.items():
        if ten.startswith("_"):
            continue
        dich = v.get("dich", "")
        # Đích phải có thật trên máy. Không có thì BỎ QUA và nói rõ — thà thiếu
        # một lệnh còn hơn có một lệnh gọi ra là lỗi.
        if dich and dich not in co_tren_may:
            bo_qua.append(f"{ten} → {dich}")
            continue
        noi_dung = MAU.format(mo_ta=v["mo_ta"], than=v["than"].strip())
        f = RA / f"{ten}.md"
        if f.exists() and f.read_text("utf-8") == noi_dung:
            giu += 1
            continue
        if not dry:
            f.write_text(noi_dung, encoding="utf-8")
        tao += 1

    print(f"{'(XEM TRƯỚC) ' if dry else ''}Sinh/cập nhật: {tao} · giữ nguyên: {giu}")
    if bo_qua:
        print(f"\n⚠ BỎ QUA {len(bo_qua)} lệnh vì đích không có trên máy này:")
        for x in bo_qua:
            print("   -", x)
    print(f"\n→ {RA}")
    print("Cài lên máy: bash sync/copy-commands-vi.sh")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
