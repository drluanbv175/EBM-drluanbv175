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

RÀO «DANH MỤC GỘP HAI MÁY» (26/09/2026). DANH-MUC-CONG-CU.md và INDEX-CONG-CU.md ĐANG TRACK
là danh mục GỘP Mac+Windows, dựng từ catalog_may/*.json — thư mục bị bỏ qua trong git, chỉ đi
giữa hai máy qua OneDrive. Trên Cloud nó chỉ có bản chụp của chính container, nên bước ②③ từng
ghi đè hai tệp track bằng dữ liệu một máy (tái lập: DANH-MUC 1876 → 1032 mục, INDEX 865 → 236
dòng; commit vào là hỏng `/cong-cu-gi` trên cả hai máy). Nay: phiên Cloud ⇒ dừng TRƯỚC mọi
bước; máy thật mà catalog_may/ thiếu bản chụp của Mac hoặc Windows (xét trường `may` BÊN TRONG
tệp) ⇒ dừng sau ①, trước ②③. Cả hai trả mã 2, không ghi tệp track nào. Mốc so «nhảy vọt» ở
bước ④ lấy đúng máy qua `nhan_dien_may.ten_may()` (bản cũ: mọi máy không phải Darwin đều bị
so với mốc Windows ⇒ trên Cloud «4→9 plugin» sai máy).

Dùng:  python3 tools/sau_cap_nhat_plugin.py [--ghi-moc]
Mã thoát: 0 trọn vẹn · 1 có bước lỗi (dừng tại đó, không ghi mốc) · 2 nơi này KHÔNG dựng được
danh mục gộp hai máy (phiên Cloud / thiếu bản chụp máy kia) — không ghi tệp track nào.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
# Bản chụp kho từng máy (ngoài git, đi qua OneDrive) — nguồn của danh mục GỘP hai máy.
SNAP_DIR = REPO / "tools" / "vietnamize" / "catalog_may"
MAY_CAN_GOP = ("Mac", "Windows")


def _nhan_dien_may():
    """Nạp tools/nhan_dien_may.py theo đường dẫn tệp — MỘT nguồn cho «máy này là máy nào»."""
    duong = Path(__file__).resolve().parent / "nhan_dien_may.py"
    spec = importlib.util.spec_from_file_location("_scnp_nhan_dien_may", duong)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def may_trong_catalog(snap_dir: Path | None = None) -> set[str]:
    """Tên máy có bản chụp trong catalog_may/ — theo trường `may` BÊN TRONG tệp (OneDrive có thể
    đẻ «Mac-DESKTOP-XYZ.json»), lùi về tên tệp khi thiếu trường; tệp hỏng bị bỏ qua."""
    snap_dir = SNAP_DIR if snap_dir is None else snap_dir
    may: set[str] = set()
    for f in sorted(snap_dir.glob("*.json")) if snap_dir.is_dir() else []:
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        may.add(str((d.get("may") if isinstance(d, dict) else None) or f.stem))
    return may


def ly_do_khong_dung_danh_muc(cloud: bool, snap_dir: Path | None = None) -> str:
    """Lý do KHÔNG được dựng lại danh mục gộp ở nơi này («» = được dựng)."""
    if cloud:
        return ("phiên Cloud — catalog_may/ (ngoài git, chỉ đi qua OneDrive) chỉ có bản chụp của "
                "container này; dựng ②③ ở đây sẽ ghi đè DANH-MUC/INDEX đang track bằng dữ liệu "
                "một máy. Danh mục gộp chỉ dựng được trên máy thật (Mac/Windows).")
    thieu = [m for m in MAY_CAN_GOP if m not in may_trong_catalog(snap_dir)]
    if thieu:
        return (f"catalog_may/ thiếu bản chụp của {', '.join(thieu)} — danh mục gộp hai máy dựng từ "
                "ít máy hơn sẽ ghi đè DANH-MUC/INDEX đang track bằng dữ liệu thiếu. Đợi OneDrive "
                "xanh (bản chụp máy kia về tới), hoặc chạy ① trên máy kia trước.")
    return ""


def _buoc(ten: str, lenh: list[str]) -> bool:
    print(f"\n── {ten}")
    r = subprocess.run([sys.executable, *lenh], cwd=REPO)
    if r.returncode not in (0, 1):  # 1 = cảnh báo ở một số tool, không phải hỏng
        print(f"   🔴 dừng — mã thoát {r.returncode}")
        return False
    return True


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Nghi thức sau-cập-nhật-plugin (4 bước, 1 lệnh)")
    ap.add_argument("--ghi-moc", action="store_true",
                    help="chốt kho hiện tại làm mốc chuẩn mới (sau cập nhật CÓ CHỦ Ý)")
    a = ap.parse_args(argv)
    ndm = _nhan_dien_may()
    if ndm.la_phien_cloud():   # Cloud: dừng TRƯỚC mọi bước — không ghi gì cả
        print(f"⚪ KHÔNG chạy nghi thức ở đây: {ly_do_khong_dung_danh_muc(True)}")
        return 2
    if not _buoc("① chụp kho máy này", ["tools/vietnamize/extract_catalog.py"]):
        return 1
    ly_do = ly_do_khong_dung_danh_muc(False)
    if ly_do:   # máy thật: ① vừa ghi bản chụp của máy này; còn thiếu máy kia ⇒ dừng trước ②③
        print(f"\n⚪ DỪNG trước ②③ (không ghi DANH-MUC/INDEX đang track): {ly_do}")
        return 2
    for ten, lenh in (("② dựng danh mục tiếng Việt", ["tools/vietnamize/build_danh_muc.py"]),
                      ("③ dựng trang tra cứu", ["tools/vietnamize/build_trang_tra_cuu.py"])):
        if not _buoc(ten, lenh):
            return 1
    if a.ghi_moc:
        # CHẶN NHẢY VỌT (16/08 — lỗi thật vừa xảy: app ghi đè settings làm 8 bộ
        # medsci trùng bật lại ⇒ kho phồng 9→17 plugin/839→1311 skill, và nghi
        # thức đã TỰ CHỐT MỐC SAI trên trạng thái đó. Ghi mốc là tuyên bố «kho
        # đang đủ» — thay đổi >25% phải có mắt người xem, không tự gật).
        moc_p = REPO / "tools" / "moc_chuan_plugin.json"
        try:
            may = ndm.ten_may()   # đúng máy (bản cũ: không phải Darwin ⇒ «Windows», sai trên Cloud/Linux)
            cu = json.loads(moc_p.read_text(encoding="utf-8")).get(may, {}).get("plugin", {})
            n_cu = len(cu)
            sk_cu = sum(v.get("so_skill", 0) for v in cu.values())
            # đếm nhanh theo cùng nguồn kiem_plugin_day_du dùng (SKILL.md trên đĩa)
            r = subprocess.run([sys.executable, "tools/kiem_plugin_day_du.py"],
                               capture_output=True, text=True, cwd=REPO, timeout=60, encoding="utf-8", errors="replace")
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
