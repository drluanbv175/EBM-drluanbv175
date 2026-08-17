#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NGHI THỨC SAU-CẬP-NHẬT-PLUGIN — bốn việc lệ phí gói thành MỘT lệnh (16/08/2026).

VÌ SAO CÓ
=========
Kho plugin KHÔNG đứng yên: plugin tự đổi phiên bản giữa phiên (đo 16/08:
academic-research 3.19→3.20.1, harness 5.6→5.8 ngay trong một resume), cache tự
dọn-nạp lại, danh sách skill đổi theo. Mỗi lần như vậy có BỐN việc lệ phí phải
chạy mà trước nay là bốn lệnh rời — quên một là danh mục/trang tra/mốc chuẩn
trôi khỏi thực tế (đã xảy ra nhiều lần, xem CLAUDE.md mục kho công cụ).

BỐN BƯỚC (đúng thứ tự phụ thuộc):
  ① extract_catalog  — chụp kho thật của MÁY NÀY vào catalog_may/<Máy>.json
  ② build_danh_muc   — dựng lại INDEX-CONG-CU + DANH-MUC-CONG-CU (lớp phủ tiếng Việt)
  ③ build_trang_tra_cuu — dựng lại TRA-CUU-CONG-CU.html (gộp cả hai máy)
  ④ kiem_plugin_day_du --ghi-moc — CHỐT trạng thái hiện tại làm mốc chuẩn mới

Bước ④ chỉ chạy khi ①–③ sạch VÀ có cờ --ghi-moc (ghi mốc = tuyên bố «kho đang
đủ» — chạy sau một đợt cập nhật CÓ CHỦ Ý; không cờ thì chỉ dựng lại và BÁO).
Mốc ghi RIÊNG từng máy — trên Windows phải chạy lại tool này ở đó.

Dùng:  python3 tools/sau_cap_nhat_plugin.py [--ghi-moc]
Mã thoát: 0 trọn vẹn · 1 có bước lỗi (dừng tại đó, không ghi mốc).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]


def _buoc(ten: str, lenh: list[str]) -> bool:
    print(f"\n── {ten}")
    r = subprocess.run([sys.executable, *lenh], cwd=REPO)
    if r.returncode not in (0, 1):  # 1 = cảnh báo ở một số tool, không phải hỏng
        print(f"   🔴 dừng — mã thoát {r.returncode}")
        return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="Nghi thức sau-cập-nhật-plugin (4 bước, 1 lệnh)")
    ap.add_argument("--ghi-moc", action="store_true",
                    help="chốt kho hiện tại làm mốc chuẩn mới (sau cập nhật CÓ CHỦ Ý)")
    a = ap.parse_args()
    cac_buoc = [
        ("① chụp kho máy này", ["tools/vietnamize/extract_catalog.py"]),
        ("② dựng danh mục tiếng Việt", ["tools/vietnamize/build_danh_muc.py"]),
        ("③ dựng trang tra cứu", ["tools/vietnamize/build_trang_tra_cuu.py"]),
    ]
    for ten, lenh in cac_buoc:
        if not _buoc(ten, lenh):
            return 1
    if a.ghi_moc:
        # CHẶN NHẢY VỌT (16/08 — lỗi thật vừa xảy: app ghi đè settings làm 8 bộ
        # medsci trùng bật lại ⇒ kho phồng 9→17 plugin/839→1311 skill, và nghi
        # thức đã TỰ CHỐT MỐC SAI trên trạng thái đó. Ghi mốc là tuyên bố «kho
        # đang đủ» — thay đổi >25% phải có mắt người xem, không tự gật).
        import json
        moc_p = REPO / "tools" / "moc_chuan_plugin.json"
        try:
            import platform
            may = "Mac" if platform.system() == "Darwin" else "Windows"
            cu = json.loads(moc_p.read_text(encoding="utf-8")).get(may, {}).get("plugin", {})
            n_cu = len(cu)
            sk_cu = sum(v.get("so_skill", 0) for v in cu.values())
            # đếm nhanh theo cùng nguồn kiem_plugin_day_du dùng (SKILL.md trên đĩa)
            r = subprocess.run([sys.executable, "tools/kiem_plugin_day_du.py"],
                               capture_output=True, text=True, cwd=REPO, timeout=60)
            import re
            m = re.search(r"(\d+) plugin, (\d+) skill", r.stdout or "")
            if m and n_cu:
                n_moi, sk_moi = int(m.group(1)), int(m.group(2))
                if abs(n_moi - n_cu) / n_cu > 0.25 or (sk_cu and abs(sk_moi - sk_cu) / sk_cu > 0.25):
                    print(f"\n🔴 TỪ CHỐI tự ghi mốc: kho đổi quá 25% so mốc cũ "
                          f"({n_cu}→{n_moi} plugin · {sk_cu}→{sk_moi} skill).")
                    print("   Nhảy vọt cỡ này thường là cache nạp lại hàng loạt hoặc app ghi đè")
                    print("   enabledPlugins (đã xảy ra 16/08: 8 bộ medsci trùng bật lại).")
                    print("   → Bác sĩ xem `python3 tools/kiem_plugin_day_du.py` + settings.json,")
                    print("     xử xong chạy lại; hoặc cố ý chấp nhận thì chạy thẳng")
                    print("     `python3 tools/kiem_plugin_day_du.py --ghi-moc`.")
                    return 1
        except (OSError, json.JSONDecodeError, subprocess.SubprocessError):
            pass  # thiếu mốc cũ/không đọc được — cho qua, lần đầu ghi mốc là hợp lệ
        if not _buoc("④ ghi mốc chuẩn mới", ["tools/kiem_plugin_day_du.py", "--ghi-moc"]):
            return 1
    else:
        print("\n(bỏ qua ④ — thêm --ghi-moc để chốt kho hiện tại làm mốc chuẩn)")
    print("\n✓ Nghi thức sau-cập-nhật hoàn tất. Nhớ chạy lại trên MÁY KIA khi tới lượt nó"
          " cập nhật — mốc và catalog ghi riêng từng máy. Cần bác sĩ kiểm chứng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
