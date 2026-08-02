#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_chat_luong.py — Chấm CHẤT LƯỢNG bản dịch, không chỉ đếm "đã có tiếng Việt".

Một mô tả chỉ hữu ích khi bác sĩ đọc dòng đó lúc gõ `/` là biết ngay có nên gọi hay
không. Script soi 6 lỗi làm mô tả mất tác dụng:

  L1  Quá ngắn (< 45 ký tự) — không đủ để quyết định
  L2  Không nói DÙNG KHI NÀO (thiếu "Dùng khi/Dùng cho/Dùng ở") — chỉ tả công cụ,
      không tả tình huống. Chỉ tính là lỗi với mục Tầng 1.
  L3  Mất từ khoá kích hoạt tiếng Anh (không có phần "Từ khoá:") — hệ thống dựa vào
      đó để tự chọn skill; dịch sạch trơn sẽ làm skill khó được gọi
  L4  Còn sót câu tiếng Anh dài (≥ 6 từ Latin liền nhau không dấu, ngoài phần Từ khoá)
  5   Quá dài (> 400 ký tự) — tràn dòng, khó đọc khi gõ `/`
  L6  Trùng y hệt mô tả của mục khác — dấu hiệu dịch ẩu, dán nhầm

Chạy: python3 tools/vietnamize/check_chat_luong.py [--sua-duoc]
Mã thoát 0 = không có lỗi chặn (L1/L2/L3), 1 = có.
"""
from __future__ import annotations

import collections
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
VN = re.compile(r"[àáâãèéêìíòóôõùúýăđĩũơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]", re.I)
# chuỗi ≥6 từ Latin liền nhau, không từ nào có dấu tiếng Việt
CAU_ANH = re.compile(r"(?:\b[A-Za-z][A-Za-z'-]{1,}\b[ ,]){5,}\b[A-Za-z][A-Za-z'-]{1,}\b")


def main() -> int:
    items = json.loads((HERE / "catalog_raw.json").read_text("utf-8"))
    vi = json.loads((HERE / "vi_descriptions.json").read_text("utf-8"))

    loi: dict[str, list] = collections.defaultdict(list)
    theo_mo_ta: dict[str, list[str]] = collections.defaultdict(list)

    for i in items:
        key_id, key_ten = i["id"], f"name:{i['name']}"
        entry = vi.get(key_id) or vi.get(key_ten)
        if not entry:
            continue                       # mục vốn đã tiếng Việt (agent EBM, skill riêng)
        d = entry["vi"].strip()
        tier = i["tier_guess"]
        theo_mo_ta[d].append(i["id"])

        if len(d) < 45:
            loi["L1 quá ngắn"].append((i["id"], d))
        # L2 chỉ áp cho thứ bác sĩ GÕ `/` GỌI TRỰC TIẾP. Agent do nhạc trưởng điều
        # phối gọi, mô tả của nó phục vụ việc định tuyến chứ không phải để bác sĩ
        # đọc rồi quyết định — đòi "Dùng khi" ở đó chỉ tạo câu chữ gượng ép.
        if tier == 1 and i["kind"] != "agent" and not re.search(r"\bDùng\s+\S", d):
            loi["L2 không nói dùng khi nào (skill/lệnh Tầng 1)"].append((i["id"], d[:70]))
        if "Từ khoá:" not in d:
            loi["L3 mất từ khoá kích hoạt"].append((i["id"], d[:70]))
        than = d.split("Từ khoá:")[0]
        m = CAU_ANH.search(than)
        if m and not VN.search(m.group(0)):
            loi["L4 còn câu tiếng Anh"].append((i["id"], m.group(0)[:60]))
        if len(d) > 400:
            loi["L5 quá dài"].append((i["id"], f"{len(d)} ký tự"))

    for d, ids in theo_mo_ta.items():
        ten = {x.split(":")[-1] for x in ids}
        if len(ids) > 1 and len(ten) > 1:   # trùng mô tả giữa các mục KHÁC TÊN
            loi["L6 trùng mô tả giữa mục khác nhau"].append((", ".join(ids[:3]), d[:60]))

    print(f"Đã chấm {sum(1 for i in items if vi.get(i['id']) or vi.get('name:'+i['name']))} "
          f"mô tả trên {len(items)} mục đang nạp.\n")
    chan = 0
    for nhan in sorted(loi):
        ds = loi[nhan]
        print(f"  {nhan}: {len(ds)}")
        for k, v in ds[:6]:
            print(f"      - {k}\n        {v}")
        if len(ds) > 6:
            print(f"      … và {len(ds)-6} mục nữa")
        if nhan.startswith(("L1", "L2", "L3")):
            chan += len(ds)
    if not loi:
        print("  ✓ Không phát hiện lỗi chất lượng nào.")
    print(f"\nLỗi CHẶN (L1/L2/L3): {chan}")
    return 1 if chan else 0


if __name__ == "__main__":
    sys.exit(main())
