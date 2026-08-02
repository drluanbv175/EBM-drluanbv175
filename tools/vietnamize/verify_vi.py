#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_vi.py — Kiểm ĐỘC LẬP kết quả Việt hoá mô tả skill/lệnh/agent.

Cố ý KHÔNG dùng lại hàm đọc frontmatter của apply_vi.py: nếu hàm đó sai thì
việc kiểm bằng chính nó sẽ không bao giờ phát hiện ra. Ở đây dùng PyYAML — cùng
loại parser mà hệ thống thật dùng để đọc frontmatter.

Kiểm 5 điều trên mọi mục đã dịch:
  1. Frontmatter còn PHÂN TÍCH ĐƯỢC (hỏng = skill biến mất khỏi danh sách gõ `/`).
  2. `description` đúng bằng bản tiếng Việt trong vi_descriptions.json.
  3. `description-en` khớp CHÍNH XÁC mô tả gốc trong file .vi-bak.
  4. Không phát sinh/mất khoá nào khác trong frontmatter (bắt lỗi ghi sót phần
     đuôi của mô tả nhiều dòng thành rác).
  5. Thân file (phần sau frontmatter) không bị đụng tới.

Chạy: python3 tools/vietnamize/verify_vi.py
Mã thoát 0 = sạch, 1 = có lỗi.
"""
from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent

try:
    import yaml
except ImportError:
    print("✗ Cần PyYAML để kiểm. Kích hoạt venv: source ~/.ebm-venv/bin/activate")
    raise SystemExit(1)


def split(text: str):
    """Tách (frontmatter, thân) — cùng quy ước với công cụ đọc skill."""
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end == -1:
        return None, text
    return text[3:end], text[end:]


def main() -> int:
    catalog = {i["id"]: i for i in json.loads((HERE / "catalog_raw.json").read_text("utf-8"))}
    vi_map = json.loads((HERE / "vi_descriptions.json").read_text("utf-8"))

    loi: list[str] = []
    canh_bao: list[str] = []
    da_kiem = 0

    # Dựng danh sách (khoá dịch, mục) — hỗ trợ cả khoá id đầy đủ lẫn `name:<tên>`
    # (một bản dịch áp cho nhiều bản sao cùng tên, xem apply_vi.py).
    cap: list[tuple[str, dict, dict]] = []
    theo_ten: dict[str, list] = {}
    for i in catalog.values():
        theo_ten.setdefault(i["name"], []).append(i)
    for key, entry in vi_map.items():
        if key.startswith("_"):
            continue
        if key.startswith("name:"):
            # Bỏ những mục đã có khoá id RIÊNG — id luôn thắng fallback theo tên
            # (apply_vi.py), nên so chúng với bản dịch của khoá tên là so nhầm.
            ds = [i for i in theo_ten.get(key[5:], []) if i["id"] not in vi_map]
            if not ds and not theo_ten.get(key[5:]):
                # Bản dịch còn nhưng mục đã biến mất — bình thường khi plugin bị gỡ.
                # Không phải lỗi: giữ lại bản dịch để dùng nếu plugin được cài lại.
                canh_bao.append(f"{key}: không còn mục nào mang tên này (plugin đã gỡ?)")
            cap.extend((key, entry, i) for i in ds)
        elif key in catalog:
            cap.append((key, entry, catalog[key]))
        else:
            canh_bao.append(f"{key}: không còn trong danh mục (plugin đã gỡ hoặc đổi tên?)")

    for key, entry, item in cap:
        path = pathlib.Path(item["path"])
        if not path.exists():
            loi.append(f"{key}: file không tồn tại — {path}")
            continue

        fm, body = split(path.read_text("utf-8", errors="replace"))
        if fm is None:
            loi.append(f"{key}: MẤT frontmatter")
            continue
        try:
            data = yaml.safe_load(fm)
        except Exception as exc:                      # noqa: BLE001
            loi.append(f"{key}: frontmatter HỎNG — {str(exc)[:80]}")
            continue
        if not isinstance(data, dict):
            loi.append(f"{key}: frontmatter không phải bảng khoá-giá trị")
            continue

        # 2. mô tả đúng bản tiếng Việt
        if (data.get("description") or "").strip() != entry["vi"].strip():
            loi.append(f"{key}: `description` KHÁC bản dịch đã khai")

        # 3+4+5. đối chiếu với bản gốc
        bak = path.with_suffix(path.suffix + ".vi-bak")
        if not bak.exists():
            canh_bao.append(f"{key}: không còn .vi-bak để đối chiếu bản gốc")
        else:
            fm0, body0 = split(bak.read_text("utf-8", errors="replace"))
            try:
                goc = yaml.safe_load(fm0) or {}
            except Exception:                          # noqa: BLE001
                goc = {}
                canh_bao.append(f"{key}: bản gốc vốn đã không phân tích được")
            if goc:
                if (goc.get("description") or "").strip() != (data.get("description-en") or "").strip():
                    loi.append(f"{key}: `description-en` LỆCH mô tả gốc")
                them = set(data) - set(goc) - {"description-en", "description-src"}
                mat = set(goc) - set(data)
                if them:
                    loi.append(f"{key}: frontmatter phát sinh khoá lạ {sorted(them)}")
                if mat:
                    loi.append(f"{key}: frontmatter MẤT khoá {sorted(mat)}")
            if body.strip() != body0.strip():
                loi.append(f"{key}: THÂN file bị thay đổi (không được phép)")
        da_kiem += 1

    print(f"Đã kiểm {da_kiem} mục đã dịch.")
    if canh_bao:
        print(f"\n⚠ Cảnh báo ({len(canh_bao)}):")
        for c in canh_bao[:10]:
            print("   -", c)
    if loi:
        print(f"\n✗ LỖI ({len(loi)}):")
        for e in loi[:30]:
            print("   -", e)
        return 1
    print("✓ Sạch: frontmatter hợp lệ, mô tả đúng bản dịch, bản gốc còn nguyên, thân file không đổi.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
