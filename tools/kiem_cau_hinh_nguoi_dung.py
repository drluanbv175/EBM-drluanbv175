#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Canh các khoá trong ~/.claude/settings.json bị app ghi đè — và khôi phục.

VÌ SAO CÓ (22/08/2026). Bác sĩ than nhiều tháng: «skill cài rồi mà gọi không
được», «lúc đủ lúc không đủ». Nguyên nhân gốc tìm ra 10/08 là NGÂN SÁCH DANH SÁCH
SKILL: Claude Code chỉ dành `skillListingBudgetFraction` — mặc định 0,01 = 8.000
ký tự — cho danh sách skill gửi cho model, trong khi kho ~869 skill cần ~45.000
ký tự CHỈ ĐỂ HIỆN ĐỦ TÊN (vượt 5,6 lần). Vượt thì Claude Code **CẮT**: rụng mô tả
trước, rồi rụng luôn skill. File vẫn ĐỦ trên đĩa — chỉ là model không được cho
biết chúng tồn tại. Đã vá bằng `0.08` trên Mac 10/08 và Windows 12/08.

CHỖ HỞ NÀY VÁ: **app Claude ghi đè `settings.json`** sau một số đợt cập nhật — đã
đo HAI LẦN trên Mac (17/08: kho 839→1311 skill; 21/08: 870→1319). Đợt ghi đè đó
xoá cờ `enabledPlugins` (đã có `kiem_co_tat_plugin_trung.py` khôi phục) **và xoá
luôn bản vá ngân sách**. Trước công cụ này, KHÔNG có gì khôi phục khoá đó:
`kiem_plugin_day_du.py` chỉ ĐỌC và báo 🔴, còn `kiem_co_tat_plugin_trung.py` tự
giới hạn «chỉ chạm enabledPlugins, không đổi khoá nào khác». Nên mỗi lần app ghi
đè là triệu chứng cũ quay lại nguyên vẹn, và không ai biết vì sao.

BA RANH GIỚI:
  · Chỉ ghi đúng các khoá KHAI trong `sync/cau-hinh-nguoi-dung.json` — không đụng
    `enabledPlugins` hay bất kỳ khoá nào khác, luôn sao lưu trước khi ghi.
  · Khôi phục GIÁ TRỊ BÁC SĨ ĐÃ CHỌN, không tự tính một giá trị «tối ưu». Nhưng
    nếu ĐO ĐƯỢC rằng giá trị đã khai không còn đủ cho kho hiện tại thì NÓI RA —
    khôi phục một con số đã lỗi thời mà im lặng cũng là để bác sĩ mắc kẹt.
  · Phép đo «cần bao nhiêu ký tự» dùng lại `kiem_plugin_day_du.py` chứ không viết
    bản thứ hai: hai bản đo là hai thứ sẽ lệch nhau.

    python3 tools/kiem_cau_hinh_nguoi_dung.py            # kiểm, chỉ đọc
    python3 tools/kiem_cau_hinh_nguoi_dung.py --ap-dung  # khôi phục (có sao lưu)

Mã thoát: 0 = khớp · 1 = lệch/thiếu · 2 = không ghi được.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import shutil
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
KHAI = REPO / "sync/cau-hinh-nguoi-dung.json"
SETTINGS = Path.home() / ".claude" / "settings.json"


def doc_json(p: Path) -> dict:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def do_ngan_sach() -> tuple[int, int, int] | None:
    """(ký tự CẦN, số skill, ký tự ngân sách ĐÃ KHAI cho) — hoặc None nếu không đo được.

    So với GIÁ TRỊ ĐÃ KHAI, không phải giá trị đang nằm trong file: nếu app vừa xoá
    khoá đi thì file đang là mặc định 0,01 và mọi phép so với nó đều vô nghĩa. Phép
    đo hỏi thẳng `kiem_plugin_day_du.do_ky_tu_can()` — một nguồn duy nhất.
    """
    khai = (doc_json(KHAI) or {}).get("khoa") or {}
    phan = (khai.get("skillListingBudgetFraction") or {}).get("gia_tri")
    if not isinstance(phan, (int, float)):
        return None
    try:
        import importlib.util
        f = REPO / "tools/kiem_plugin_day_du.py"
        spec = importlib.util.spec_from_file_location("_kpdd_cauhinh", f)
        m = importlib.util.module_from_spec(spec)
        sys.modules["_kpdd_cauhinh"] = m
        spec.loader.exec_module(m)
        can, tong = m.do_ky_tu_can(m.quet())
        return can, tong, int(m.CUA_SO_KY_TU * phan)
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Canh khoá settings.json bị app ghi đè")
    ap.add_argument("--ap-dung", action="store_true", help="ghi lại khoá đã khai (có sao lưu)")
    ap.add_argument("--im-khi-on", action="store_true", help="im khi mọi khoá đã khớp")
    a = ap.parse_args()

    khai = (doc_json(KHAI) or {}).get("khoa") or {}
    if not khai:
        print(f"⚠ Chưa có bản khai {KHAI.name} — không biết phải giữ khoá nào.", file=sys.stderr)
        return 1
    if not SETTINGS.exists():
        print(f"⚠ Máy này chưa có {SETTINGS} — bỏ qua.", file=sys.stderr)
        return 0

    hien = doc_json(SETTINGS)
    lech: list[tuple[str, object, object]] = []
    for ten, m in khai.items():
        muon = m.get("gia_tri")
        dang_co = hien.get(ten, "(KHÔNG CÓ)")
        if dang_co != muon:
            lech.append((ten, dang_co, muon))

    if not lech:
        if not a.im_khi_on:
            print(f"🟢 {len(khai)} khoá người dùng khớp bản khai.")
        # Khoá khớp bản khai KHÔNG có nghĩa giá trị đã khai còn ĐỦ: kho skill lớn
        # dần theo mỗi lần cài plugin. Chỉ nói khi ĐO ĐƯỢC là đã vượt.
        do = do_ngan_sach()
        if do and do[0] > do[2]:
            print(f"⚠ Giá trị đã khai KHÔNG CÒN ĐỦ: kho cần ~{do[0]:,} ký tự cho "
                  f"{do[1]} skill, ngân sách đã khai chỉ cho {do[2]:,} "
                  f"(vượt {do[0]/do[2]:.1f} lần).")
            print(f"   Nâng skillListingBudgetFraction trong {KHAI.name} — máy sẽ lại "
                  f"cắt danh sách skill nếu để nguyên.")
            return 1
        return 0

    print(f"🔴 {len(lech)} khoá người dùng LỆCH bản khai "
          f"— nhiều khả năng app vừa ghi đè settings.json:")
    for ten, dang_co, muon in lech:
        print(f"   • {ten}: đang là {dang_co!r}, phải là {muon!r}")
        ly_do = (khai[ten].get("ly_do") or "").strip()
        if ly_do:
            print(f"     {ly_do}")
    if any(t == "skillListingBudgetFraction" for t, _, _ in lech):
        print("   ⇒ Đây chính là lý do «skill cài rồi mà gọi không được»: file vẫn đủ "
              "trên đĩa,\n     nhưng danh sách gửi cho model bị CẮT nên model không "
              "biết chúng tồn tại.")

    if not a.ap_dung:
        print("\n   Chạy lại với --ap-dung để khôi phục (sẽ sao lưu settings.json trước).")
        return 1

    try:
        luu = SETTINGS.with_name(f"settings.json.bak-{_dt.datetime.now():%Y%m%d-%H%M%S}")
        shutil.copy2(SETTINGS, luu)
        for ten, _cu, muon in lech:
            hien[ten] = muon              # CHỈ khoá đã khai; không đụng khoá khác
        SETTINGS.write_text(json.dumps(hien, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8", newline="\n")
    except OSError as exc:
        print(f"✗ Không ghi được {SETTINGS}: {exc}", file=sys.stderr)
        return 2
    print(f"\n✓ Đã khôi phục {len(lech)} khoá (sao lưu {luu.name}).")
    print("   Mở lại Claude Code để danh sách skill được dựng theo ngân sách mới.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
