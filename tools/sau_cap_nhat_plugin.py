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
        if not _buoc("④ ghi mốc chuẩn mới", ["tools/kiem_plugin_day_du.py", "--ghi-moc"]):
            return 1
    else:
        print("\n(bỏ qua ④ — thêm --ghi-moc để chốt kho hiện tại làm mốc chuẩn)")
    print("\n✓ Nghi thức sau-cập-nhật hoàn tất. Nhớ chạy lại trên MÁY KIA khi tới lượt nó"
          " cập nhật — mốc và catalog ghi riêng từng máy. Cần bác sĩ kiểm chứng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
