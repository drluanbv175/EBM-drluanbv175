#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CANH ĐĨA + LOG ONEDRIVE — báo SỚM khi OneDrive SyncEngine kẹt vòng lặp log ăn đĩa (02/10/2026).

VÌ SAO CÓ. Vụ «OneDrive ghi log liên tục» đã xảy ra ba lần (21/08, 17/09, 01–02/10): đo 02/10 thư mục log 20,7–24 GB, 24.796 tệp,
~54 tệp/phút, OneDrive 131% CPU. Nó ăn đĩa lặng lẽ; đĩa đầy thì MỌI thứ nền (lịch, quét, ghi sổ) hỏng theo. Chưa có gì canh việc này.
Chữa tận gốc là việc của bác sĩ (OneDrive → Sync Issues, xử lý hộp thoại, KHÔNG Reset); công cụ này chỉ ĐO và BÁO, không xoá, không dừng gì.

    python3 tools/canh_dia_onedrive.py                       # đo MỘT mẫu, ghi state, in kết quả
    python3 tools/canh_dia_onedrive.py --im-khi-on           # (hook) im lặng khi 🟢; mã 0 xanh · 1 vàng · 2 đỏ · 3 KHÔNG đo được
    python3 tools/canh_dia_onedrive.py --thong-bao           # thêm thông báo hệ thống macOS khi 🔴 (chống lặp: ≥60 phút/lần)
    python3 tools/canh_dia_onedrive.py --cai-launchd         # CHẠY KHÔ: in plist chạy mỗi 5 phút (macOS); thêm --ap-dung để cài; --go-launchd để gỡ

Ngưỡng (đo thật 02/10): 🔴 đĩa trống < 10 GiB · log OneDrive > 8 GiB · log tăng ≥ 150 MB/phút hoặc ≥ 30 tệp/phút giữa hai mẫu cách ≥ 2 phút ·
đĩa giảm đủ nhanh để cạn trong < 2 giờ. 🟡 đĩa trống < 20 GiB · log > 1 GiB · đĩa giảm ≥ 150 MB/phút (có thể chỉ là đồng bộ sau khởi động).
KHÔNG đo được (không thấy thư mục log/không đọc được) ⇒ ⚪ nói rõ, KHÔNG báo xanh. Một mẫu đơn lẻ không chứng minh vòng lặp — tốc độ chỉ tính
khi có mẫu trước 2 phút – 3 giờ. Cần bác sĩ kiểm chứng."""
from __future__ import annotations

import argparse
import json
import os
import plistlib
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TEP_STATE = REPO / "state" / "canh-dia-onedrive.json"
NHAN_LAUNCHD = "vn.drluan.ebm-canh-dia"

GIB = 1024 ** 3
MIB = 1024 ** 2
DO_DIA_GIB, VANG_DIA_GIB = 10, 20
DO_LOG_GIB, VANG_LOG_GIB = 8, 1
DO_TOC_DO_MB_PHUT, DO_TOC_DO_TEP_PHUT = 150, 30
DO_CAN_GIO = 2.0          # đĩa cạn trong < 2 giờ theo tốc độ hiện tại ⇒ đỏ
CUA_SO_TOC_DO_GIAY = (120, 3 * 3600)
KHOANG_THONG_BAO_GIAY = 3600
HAN_QUET_GIAY = 6.0


def thu_muc_log() -> list[Path]:
    """Thư mục log OneDrive theo nền tảng (chỉ trả những thư mục CÓ THẬT)."""
    home = Path.home()
    ung_vien: list[Path] = []
    if sys.platform == "darwin":
        ung_vien = [home / "Library" / "Logs" / "OneDrive",
                    home / "Library" / "Group Containers" / "UBF8T346G9.OneDriveStandaloneSuite" / "FileProviderLogs"]
    elif os.name == "nt":
        goc = os.environ.get("LOCALAPPDATA")
        if goc:
            ung_vien = [Path(goc) / "Microsoft" / "OneDrive" / "logs"]
    return [p for p in ung_vien if p.is_dir()]


def dem_thu_muc(duong: list[Path], han_giay: float = HAN_QUET_GIAY) -> dict:
    """Tổng số tệp + dung lượng; quá hạn thời gian thì trả số đo dở (do_do=True) — KHÔNG im lặng cắt."""
    ket = {"tep": 0, "byte": 0, "do_do": False}
    han = time.monotonic() + han_giay
    for goc in duong:
        pending = [goc]
        while pending:
            if time.monotonic() > han:
                ket["do_do"] = True
                return ket
            try:
                with os.scandir(pending.pop()) as it:
                    for e in it:
                        try:
                            if e.is_dir(follow_symlinks=False):
                                pending.append(Path(e.path))
                            elif e.is_file(follow_symlinks=False):
                                ket["tep"] += 1
                                ket["byte"] += e.stat(follow_symlinks=False).st_size
                        except OSError:
                            continue
            except OSError:
                continue
    return ket


def do_mau(thu_muc: list[Path] | None = None, bay_gio: float | None = None) -> dict:
    thu_muc = thu_muc_log() if thu_muc is None else thu_muc
    try:
        du = shutil.disk_usage(str(Path.home()))
        trong, tong = du.free, du.total
    except OSError:
        trong = tong = None
    mau = {"t": time.time() if bay_gio is None else bay_gio, "dia_trong": trong, "dia_tong": tong,
           "co_log": bool(thu_muc), "log_tep": None, "log_byte": None, "do_do": False}
    if thu_muc:
        d = dem_thu_muc(thu_muc)
        mau.update(log_tep=d["tep"], log_byte=d["byte"], do_do=d["do_do"])
    return mau


def phan_loai(mau: dict, truoc: dict | None) -> tuple[str, list[str]]:
    """Trả (mức, lý do). mức ∈ XANH | VANG | DO | KHONG_DO. HÀM THUẦN — không đọc đĩa."""
    do: list[str] = []
    vang: list[str] = []
    if mau.get("dia_trong") is None:
        return "KHONG_DO", ["không đọc được dung lượng đĩa"]
    gib = mau["dia_trong"] / GIB
    if gib < DO_DIA_GIB:
        do.append(f"đĩa trống chỉ {gib:.1f} GiB (< {DO_DIA_GIB})")
    elif gib < VANG_DIA_GIB:
        vang.append(f"đĩa trống {gib:.1f} GiB (< {VANG_DIA_GIB})")
    if mau.get("log_byte") is not None:
        lg = mau["log_byte"] / GIB
        if lg > DO_LOG_GIB:
            do.append(f"log OneDrive {lg:.1f} GiB / {mau['log_tep']} tệp (> {DO_LOG_GIB} GiB — vòng lặp log?)")
        elif lg > VANG_LOG_GIB:
            vang.append(f"log OneDrive {lg:.1f} GiB / {mau['log_tep']} tệp (> {VANG_LOG_GIB} GiB)")
    if truoc and truoc.get("t") is not None:
        dt = mau["t"] - truoc["t"]
        if CUA_SO_TOC_DO_GIAY[0] <= dt <= CUA_SO_TOC_DO_GIAY[1]:
            phut = dt / 60
            if mau.get("log_byte") is not None and truoc.get("log_byte") is not None:
                mb_phut = (mau["log_byte"] - truoc["log_byte"]) / MIB / phut
                tep_phut = (mau["log_tep"] - truoc["log_tep"]) / phut
                if mb_phut >= DO_TOC_DO_MB_PHUT or tep_phut >= DO_TOC_DO_TEP_PHUT:
                    do.append(f"log đang TĂNG NÓNG: +{mb_phut:.0f} MB/phút, +{tep_phut:.0f} tệp/phút")
            if truoc.get("dia_trong") is not None:
                giam_mb_phut = (truoc["dia_trong"] - mau["dia_trong"]) / MIB / phut
                if giam_mb_phut >= DO_TOC_DO_MB_PHUT:
                    gio_can = (mau["dia_trong"] / MIB) / giam_mb_phut / 60
                    if gio_can < DO_CAN_GIO:
                        do.append(f"đĩa giảm {giam_mb_phut:.0f} MB/phút — cạn sau ~{gio_can:.1f} giờ")
                    else:
                        vang.append(f"đĩa giảm {giam_mb_phut:.0f} MB/phút (cạn sau ~{gio_can:.0f} giờ; có thể chỉ là đồng bộ)")
    if mau.get("do_do"):
        vang.append("đếm tệp log chưa xong trong hạn — số đo log là CẬN DƯỚI")
    if not mau.get("co_log"):
        vang.append("không thấy thư mục log OneDrive — chỉ đo được đĩa, KHÔNG biết có vòng lặp log hay không")
    if do:
        return "DO", do + vang
    if vang:
        return "VANG", vang
    return "XANH", []


def doc_state(duong_dan: Path = TEP_STATE) -> dict:
    try:
        d = json.loads(duong_dan.read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def ghi_state(d: dict, duong_dan: Path = TEP_STATE) -> None:
    duong_dan.parent.mkdir(parents=True, exist_ok=True)
    tam = duong_dan.with_name(duong_dan.name + f".tmp{os.getpid()}")
    tam.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    os.replace(tam, duong_dan)


def can_thong_bao(muc: str, st: dict, bay_gio: float) -> bool:
    """Chỉ thông báo khi 🔴, và ≥ 60 phút kể từ lần thông báo trước (chống lặp mỗi 5 phút)."""
    return muc == "DO" and (bay_gio - float(st.get("thong_bao_luc") or 0)) >= KHOANG_THONG_BAO_GIAY


def thong_bao_he_thong(noi_dung: str) -> bool:
    if sys.platform != "darwin":
        return False
    loi = noi_dung.replace("\\", " ").replace('"', "'")[:180]
    try:
        subprocess.run(["osascript", "-e", f'display notification "{loi}" with title "ĐĨA / ONEDRIVE — cần xem"'],
                       capture_output=True, timeout=10)
        return True
    except (OSError, subprocess.SubprocessError):
        return False


def tao_plist(python: str, tep: Path) -> bytes:
    return plistlib.dumps({
        "Label": NHAN_LAUNCHD,
        "ProgramArguments": [python, str(tep), "--im-khi-on", "--thong-bao"],
        "StartInterval": 300,
        "RunAtLoad": True,
        "StandardOutPath": os.devnull,
        "StandardErrorPath": os.devnull,
        "ProcessType": "Background",
    })


def cai_launchd(ap_dung: bool, go: bool) -> int:
    if sys.platform != "darwin":
        print("⚪ --cai-launchd chỉ cho macOS. Windows: tạo tác vụ Task Scheduler chạy "
              f"`python {Path(__file__).name} --im-khi-on` mỗi 5 phút (chưa tự động hoá).")
        return 3
    duong = Path.home() / "Library" / "LaunchAgents" / f"{NHAN_LAUNCHD}.plist"
    lay_uid = getattr(os, "getuid", None)   # API chỉ-POSIX (CLAUDE.md §0.9): Windows không có — test vá sys.platform vẫn không sập
    if lay_uid is None:
        print("⚪ Không lấy được uid người dùng (nền tảng không phải POSIX) — không cài launchd.")
        return 3
    dich = f"gui/{lay_uid()}"
    if go:
        print(f"{'GỠ' if ap_dung else 'CHẠY KHÔ gỡ'}: launchctl bootout {dich}/{NHAN_LAUNCHD} + xoá {duong}")
        if ap_dung:
            subprocess.run(["launchctl", "bootout", f"{dich}/{NHAN_LAUNCHD}"], capture_output=True)
            duong.unlink(missing_ok=True)
        else:
            print("(chạy khô — thêm --ap-dung để gỡ thật)")
        return 0
    noi_dung = tao_plist(sys.executable, Path(__file__).resolve())
    print(f"{'CÀI' if ap_dung else 'CHẠY KHÔ cài'} agent nền {NHAN_LAUNCHD} (mỗi 300 giây; chỉ ĐO và báo, không xoá gì):")
    print(f"  tệp: {duong}\n  python: {sys.executable}\n  tool: {Path(__file__).resolve()}")
    if not ap_dung:
        print("(chạy khô — thêm --ap-dung để cài; gỡ: --go-launchd --ap-dung)")
        return 0
    duong.parent.mkdir(parents=True, exist_ok=True)
    duong.write_bytes(noi_dung)
    subprocess.run(["launchctl", "bootout", f"{dich}/{NHAN_LAUNCHD}"], capture_output=True)
    r = subprocess.run(["launchctl", "bootstrap", dich, str(duong)], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"✗ launchctl bootstrap lỗi (mã {r.returncode}): {(r.stderr or '').strip()[:200]}")
        return 2
    print("✓ Đã cài và nạp. Kiểm: launchctl print " + f"{dich}/{NHAN_LAUNCHD}")
    return 0


def main(argv: list[str] | None = None) -> int:
    for luong in (sys.stdout, sys.stderr):
        try:
            if "utf" not in (getattr(luong, "encoding", "") or "").lower() and hasattr(luong, "reconfigure"):
                luong.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Canh đĩa + log OneDrive (chỉ đo và báo)")
    ap.add_argument("--im-khi-on", action="store_true", help="im lặng khi 🟢")
    ap.add_argument("--thong-bao", action="store_true", help="thông báo hệ thống macOS khi 🔴 (chống lặp)")
    ap.add_argument("--cai-launchd", action="store_true", help="in/cài agent launchd chạy mỗi 5 phút (macOS)")
    ap.add_argument("--go-launchd", action="store_true", help="in/gỡ agent launchd")
    ap.add_argument("--ap-dung", action="store_true", help="với --cai-launchd/--go-launchd: làm thật (mặc định chạy khô)")
    a = ap.parse_args(argv)
    if a.cai_launchd or a.go_launchd:
        return cai_launchd(a.ap_dung, a.go_launchd)
    st = doc_state()
    mau = do_mau()
    muc, ly_do = phan_loai(mau, st.get("mau"))
    moi = {"mau": mau, "muc": muc, "ly_do": ly_do, "thong_bao_luc": st.get("thong_bao_luc", 0)}
    if a.thong_bao and can_thong_bao(muc, st, mau["t"]) and thong_bao_he_thong("; ".join(ly_do)):
        moi["thong_bao_luc"] = mau["t"]
    try:
        ghi_state(moi)
    except OSError as e:
        print(f"⚠ không ghi được state: {e}", file=sys.stderr)
    ma = {"XANH": 0, "VANG": 1, "DO": 2, "KHONG_DO": 3}[muc]
    if muc == "XANH" and a.im_khi_on:
        return 0
    bieu = {"XANH": "🟢", "VANG": "🟡", "DO": "🔴", "KHONG_DO": "⚪"}[muc]
    luc = datetime.fromtimestamp(mau["t"], tz=timezone.utc).astimezone().strftime("%H:%M")
    trong = "?" if mau["dia_trong"] is None else f"{mau['dia_trong'] / GIB:.0f}"
    log = "không thấy log" if not mau["co_log"] else f"log {mau['log_byte'] / MIB:.0f} MB/{mau['log_tep']} tệp"
    print(f"{bieu} ĐĨA/ONEDRIVE {luc}: trống {trong} GiB · {log}" + (f" — {'; '.join(ly_do)}" if ly_do else ""))
    if muc == "DO":
        print("   → mở menu OneDrive → Sync Issues, xử lý hộp thoại «Remove files from OneDrive?» (KHÔNG bấm Reset). "
              "Công cụ này không xoá gì; xoá log chỉ sau khi vòng lặp dừng và có sự đồng ý của bác sĩ.")
    return ma


if __name__ == "__main__":
    sys.exit(main())
