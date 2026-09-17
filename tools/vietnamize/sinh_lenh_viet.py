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

# --- Ép stdout sang UTF-8 (vá 05/08/2026) ---------------------------------
# Windows mặc định stdout=cp1252 → mọi print() tiếng Việt làm script chết giữa
# chừng bằng UnicodeEncodeError, trong khi phần việc chính đã chạy xong. Ép ở
# đây thay vì bắt người dùng nhớ đặt PYTHONIOENCODING trước mỗi lệnh.
import sys as _sys

for _luong in (_sys.stdout, _sys.stderr):
    if _luong is not None and (getattr(_luong, "encoding", "") or "").lower().replace("-", "") != "utf8":
        try:
            _luong.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass          # luồng bị chuyển hướng kiểu không reconfigure được — bỏ qua
# --------------------------------------------------------------------------

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
BANG = HERE / "lenh_viet.json"
RA = REPO / "sync/commands-vi"

MAU = """---
description: {mo_ta}
---

{than}
"""


def sinh_noi_dung(mo_ta: str, than: str) -> str:
    """Nội dung file lệnh — frontmatter YAML + thân lệnh.

    SỬA 2026-09-04 (Workflow đối kháng đa-agent, phát hiện MEDIUM) — bản cũ
    ghi `"{mo_ta}"` vào frontmatter bằng `.format()` thuần, không thoát dấu
    ngoặc kép trong mo_ta — một mô tả chứa dấu " sẽ làm hỏng cú pháp YAML
    (đóng chuỗi sớm), nặng hơn có thể chèn được khoá YAML mới nếu phần còn
    lại tình cờ/cố ý hợp cú pháp. Dùng `json.dumps()` — JSON là tập con của
    YAML nên an toàn với dấu tiếng Việt/hai chấm/ngoặc — đúng khuôn
    `apply_vi.py::replace_field()` đã dùng cho đúng vấn đề này. `json.dumps`
    tự thêm cặp ngoặc kép nên template không còn ngoặc kép viết cứng."""
    return MAU.format(mo_ta=json.dumps(mo_ta, ensure_ascii=False), than=than.strip())


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
        noi_dung = sinh_noi_dung(v["mo_ta"], v["than"])
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
