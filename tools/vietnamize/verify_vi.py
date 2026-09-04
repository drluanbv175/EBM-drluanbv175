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
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent

try:
    import yaml
except ImportError:
    print("✗ Cần PyYAML để kiểm. Kích hoạt venv: source ~/.ebm-venv/bin/activate")
    raise SystemExit(1)


# Dấu tiếng Việt — CỐ Ý khai lại tại đây thay vì import từ apply_vi/extract_catalog:
# file này kiểm chéo hai công cụ đó, dùng chung định nghĩa thì lỗi chung sẽ vô hình.
VN = re.compile(r"[àáâãèéêìíòóôõùúýăđĩũơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]",
                re.IGNORECASE)

# SỬA 2026-09-04 (Workflow đối kháng đa-agent vòng 2) — CỐ Ý khai lại danh sách này
# (không import từ apply_vi.py, cùng lý do VN ở trên). Phải khớp cùng bộ từ và
# ngưỡng ≥3 mà apply_vi.py dùng để nhận "giữ-bản-việt-tự-viết" — nếu không, một mô
# tả không dấu apply_vi.py ĐÚNG khi bỏ qua (giữ nguyên) sẽ bị verify_vi.py báo
# NHẦM là lỗi (vì mô tả trên đĩa khác bản dịch từ điển, và VN không bắt được chữ
# không dấu).
_TU_TIENG_VIET_KHONG_DAU = frozenset({
    "khong", "duoc", "cua", "nhung", "benh", "nhan", "kham", "thuoc",
    "dieu", "doan", "nghien", "cuu", "chung", "truoc", "hoac", "trong",
    "ngoai", "danh", "quyet", "dinh", "huong", "phuong", "phap", "nguoi",
})


def _co_dau_hieu_tieng_viet_khong_dau(text: str) -> bool:
    tu = re.findall(r"[a-z]+", text.lower())
    return sum(1 for t in tu if t in _TU_TIENG_VIET_KHONG_DAU) >= 3


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
    # Bản dịch có trong từ điển nhưng mục KHÔNG có trên máy đang chạy. Tách riêng
    # khỏi `canh_bao` vì bác sĩ dùng 2 máy qua OneDrive: từ điển là bản DÙNG CHUNG,
    # còn plugin thì mỗi máy cài một bộ (Windows 03/08/2026: 721 mục kiểu này, toàn
    # bộ là plugin chỉ cài trên Mac). Gộp chung sẽ đẩy cảnh báo THẬT ra khỏi 10 dòng
    # được in — tức là giấu đúng thứ cần thấy.
    khac_may: list[str] = []
    da_kiem = 0

    # Dựng danh sách (khoá dịch, mục) — hỗ trợ cả khoá id đầy đủ lẫn `name:<tên>`
    # (một bản dịch áp cho nhiều bản sao cùng tên, xem apply_vi.py).
    # Phần tử: (khoá dịch, bản dịch, mục, khớp-qua-tên). Cờ cuối cần cho luật
    # "giữ bản Việt tự viết" của apply_vi.py — xem chỗ dùng bên dưới.
    cap: list[tuple[str, dict, dict, bool]] = []
    giu: list[str] = []
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
                # Bản dịch còn nhưng mục không có ở đây — bình thường khi plugin bị
                # gỡ, HOẶC khi plugin đó chỉ cài ở máy kia. Không phải lỗi: giữ lại
                # bản dịch để dùng khi cài lại / khi chạy trên máy kia.
                khac_may.append(f"{key}: không có mục nào mang tên này trên máy này")
            cap.extend((key, entry, i, True) for i in ds)
        elif key in catalog:
            cap.append((key, entry, catalog[key], False))
        else:
            khac_may.append(f"{key}: không có trong danh mục của máy này")

    for key, entry, item, qua_ten in cap:
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
            # Ngoại lệ DUY NHẤT, khớp luật "giữ-bản-việt-tự-viết" của apply_vi.py:
            # mô tả đang có đã là tiếng Việt (có dấu HOẶC không dấu) do người viết
            # tay (không mang dấu `description-src`) → cố ý không đè. Kiểm điều
            # kiện tại đây bằng dữ liệu đọc được, KHÔNG hỏi apply_vi.py, để nếu công
            # cụ kia đè nhầm thật thì chỗ này vẫn bắt được.
            # SỬA 2026-09-04: apply_vi.py đã BỎ điều kiện `qua_ten` từ 24/08/2026
            # (luật áp cho mọi cách khớp — id lẫn tên — không chỉ khớp qua tên); giữ
            # `qua_ten` ở đây là lệch khỏi hành vi thật của apply_vi.py, khiến một
            # file khớp qua ID (không phải tên) mà apply_vi.py ĐÚNG khi bỏ qua bị
            # verify_vi.py báo NHẦM thành lỗi.
            mo_ta_hien_tai = data.get("description") or ""
            if ((VN.search(mo_ta_hien_tai) or _co_dau_hieu_tieng_viet_khong_dau(mo_ta_hien_tai))
                    and "description-src" not in data):
                giu.append(f"{key}: giữ mô tả tiếng Việt tự viết trong file")
                continue
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
    if giu:
        print(f"\nℹ {len(giu)} mục cố ý GIỮ mô tả tiếng Việt tự viết (không đè bằng "
              "bản dịch khớp theo tên):")
        for g in giu[:5]:
            print("   -", g)
    if khac_may:
        print(f"\nℹ {len(khac_may)} bản dịch không dùng tới trên máy này "
              "(plugin chỉ cài ở máy kia, hoặc đã gỡ) — giữ nguyên trong từ điển.")
        for c in khac_may[:3]:
            print("   -", c)
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
