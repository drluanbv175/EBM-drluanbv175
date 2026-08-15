#!/usr/bin/env python3
"""fix_launchd_scheduled_jobs.py — Nạp lại (bootout + bootstrap) mọi job launchd
com.medicalebm.* mà plist trên đĩa đã đổi nhưng launchd vẫn đang chạy bản CŨ trong bộ nhớ.

VÌ SAO CẦN: launchd KHÔNG tự đọc lại file .plist khi nó đổi (vd đường dẫn OneDrive đổi tên) —
chỉ đọc lúc 'launchctl bootstrap'. Sửa file trên đĩa KHÔNG tự áp dụng; job cứ lặng lẽ lỗi mọi
lần chạy (đường dẫn cũ không tồn tại) cho tới khi có người NẠP LẠI thủ công. Bấm đúp file
"Sửa Lịch Nền EBM.command" ở thư mục gốc để chạy tool này — không cần mở Terminal/gõ lệnh.

Chỉ NẠP LẠI job đã có plist đúng trên đĩa; KHÔNG tạo mới, KHÔNG sửa nội dung plist, KHÔNG
đổi bất kỳ cấu hình hệ thống nào khác. Chỉ chạy trên macOS.
"""
from __future__ import annotations

import os
import plistlib
import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def _loaded_working_directory(label: str) -> tuple[bool, str]:
    """Trả (đã_nạp, working_directory_hiện_tại_trong_bộ_nhớ). đã_nạp=False nếu job chưa
    từng được bootstrap (launchctl print không thấy)."""
    try:
        p = subprocess.run(
            ["launchctl", "print", f"gui/{getattr(os, "getuid", lambda: 0)()}/{label}"],
            capture_output=True, text=True, timeout=10,
        )
    except Exception as e:  # noqa: BLE001
        print(f"  ⚠ Không chạy được 'launchctl print' cho {label}: {e}")
        return False, ""
    if p.returncode != 0:
        return False, ""
    m = re.search(r"working directory = (.+)", p.stdout)
    return True, (m.group(1).strip() if m else "")


def main() -> int:
    if sys.platform != "darwin":
        print("Tool này chỉ chạy trên macOS (launchd không tồn tại ở Windows). Bỏ qua.")
        return 0

    agents_dir = Path.home() / "Library" / "LaunchAgents"
    plists = sorted(
        p for p in agents_dir.glob("com.medicalebm.*.plist") if ".bak" not in p.name
    ) if agents_dir.exists() else []
    if not plists:
        print("Không tìm thấy plist com.medicalebm.* nào ở ~/Library/LaunchAgents/ — "
              "chưa cài lịch nền, không có gì để sửa.")
        return 0

    print("=" * 64)
    print(" SỬA LỊCH NỀN EBM (launchd) — nạp lại job lệch đĩa/bộ nhớ")
    print("=" * 64)

    fixed, already_ok, failed = [], [], []
    for plist_path in plists:
        try:
            with plist_path.open("rb") as f:
                on_disk = plistlib.load(f)
        except Exception as e:  # noqa: BLE001
            print(f"⛔ {plist_path.name}: không đọc được plist trên đĩa ({e}) — bỏ qua.")
            failed.append(plist_path.name)
            continue
        label = on_disk.get("Label", plist_path.stem)
        disk_wd = str(on_disk.get("WorkingDirectory", ""))

        loaded, loaded_wd = _loaded_working_directory(label)
        if loaded and disk_wd and disk_wd == loaded_wd:
            print(f"🟢 {label}: đã khớp đĩa ↔ bộ nhớ, không cần nạp lại.")
            already_ok.append(label)
            continue

        reason = "chưa từng nạp" if not loaded else f"đang chạy bản cũ ({loaded_wd!r})"
        print(f"🟡 {label}: {reason} — nạp lại từ {plist_path}…")
        subprocess.run(["launchctl", "bootout", f"gui/{getattr(os, "getuid", lambda: 0)()}/{label}"],
                       capture_output=True, text=True, timeout=15)
        boot = subprocess.run(
            ["launchctl", "bootstrap", f"gui/{getattr(os, "getuid", lambda: 0)()}", str(plist_path)],
            capture_output=True, text=True, timeout=15,
        )
        if boot.returncode != 0:
            print(f"  ⛔ bootstrap lỗi: {boot.stderr.strip() or boot.returncode}")
            failed.append(label)
            continue

        loaded2, loaded_wd2 = _loaded_working_directory(label)
        if loaded2 and disk_wd and disk_wd == loaded_wd2:
            print(f"  ✓ Đã nạp lại đúng — WorkingDirectory bây giờ khớp đĩa.")
            fixed.append(label)
        else:
            print(f"  ⚠ Đã bootstrap nhưng chưa xác minh được khớp — kiểm tra tay: "
                  f"launchctl print gui/$(id -u)/{label}")
            failed.append(label)

    print("-" * 64)
    print(f"Đã khớp sẵn: {len(already_ok)} · Vừa sửa xong: {len(fixed)} · "
          f"Cần xem tay: {len(failed)}")
    if failed:
        print("⚠ Có mục cần bác sĩ tự kiểm — xem chi tiết ở trên.")
        return 1
    print("✅ Xong. Job sẽ tự chạy đúng đường dẫn vào lần lên lịch kế tiếp "
          "(không cần khởi động lại máy).")
    print("Cần bác sĩ kiểm chứng — đây là công cụ hỗ trợ, không thay phán đoán.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
