#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DỌN WORKTREE TẠM — đo mức tích tụ và gỡ worktree SẠCH (14/11/2026, bác sĩ giao sau lượt dọn đĩa).

VÌ SAO CÓ. Đo 14/11/2026: `~/.ebm-worktrees` tích tới 379 worktree ≈ 9,5 GB — nguồn phình đĩa lớn nhất của máy, lại còn nuôi chỉ mục
Spotlight (`~/Library/Metadata`) phình lên 9,9 GB. Không bộ đếm nào nhìn chỗ đó, nên nó lớn âm thầm tới khi đĩa gần đầy mới lộ.
Công cụ này cho hòm việc một CON SỐ để cảnh báo sớm, và cho người chạy một đường dọn có kỷ luật.

LUẬT AN TOÀN — rút từ chính lượt dọn 307 worktree ngày 14/11:
  • chỉ xét worktree git THẬT; thư mục không phải worktree KHÔNG bao giờ bị đụng tới;
  • tên chứa `saoluu` / `sao-luu` / `sao_luu` / `backup` ⇒ bỏ qua, DÙ SẠCH (đó là bản sao lưu, không phải worktree bỏ đi);
  • «sạch» = `git status --porcelain` RỖNG — gồm cả tệp chưa theo dõi, không chỉ tệp đã sửa;
  • đọc trạng thái KHÔNG ĐƯỢC ⇒ xếp vào «chưa đo được», TUYỆT ĐỐI không xếp vào nhóm gỡ được;
  • kiểm lại trạng thái NGAY TRƯỚC khi gỡ — danh sách quét trước đó không được tin;
  • chạy khô mặc định, `--ap-dung` mới gỡ thật, và gỡ bằng `git worktree remove` chứ không `rm -rf` mù.

Mất thư mục gốc hoặc máy không có git ⇒ nói rõ CHƯA ĐO ĐƯỢC; không bao giờ đọc thành «không có gì để dọn».
Chạy cả Mac lẫn Windows: đường dẫn từ `Path.home()`/biến môi trường, dung lượng đo bằng `st_size` (Windows không có `st_blocks`).
Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parent.parent
SO_DO = REPO / "state" / "worktree-tich-tu.json"   # ảnh chụp lượt quét ĐẦY ĐỦ gần nhất (state/ nằm ngoài git)

NGUONG_SO = 40          # số ỨNG VIÊN gỡ được vượt ngần này ⇒ nhắc (ưu tiên 2)
NGUONG_SO_GAP = 100     # vượt ⇒ nhắc gấp (ưu tiên 1)
NGUONG_GB = 3.0
NGUONG_GB_GAP = 6.0
HAN_SO_DO_NGAY = 7      # ảnh chụp cũ hơn ngần này thì không dùng để nói về dung lượng

_TU_KHOA_SAO_LUU = ("saoluu", "sao-luu", "sao_luu", "backup")
_GB = 1 << 30


def goc_worktree(goc: str | Path | None = None) -> Path:
    """Thư mục chứa worktree tạm. Ưu tiên tham số, rồi biến môi trường `EBM_WORKTREES`, cuối cùng `~/.ebm-worktrees`."""
    if goc:
        return Path(goc)
    env = os.environ.get("EBM_WORKTREES")
    return Path(env) if env else Path.home() / ".ebm-worktrees"


def la_sao_luu(ten: str) -> bool:
    """Tên mang dấu hiệu BẢN SAO LƯU ⇒ không bao giờ gỡ, dù worktree sạch."""
    t = ten.lower()
    return any(k in t for k in _TU_KHOA_SAO_LUU)


def _chay_git(args: list[str], cwd: Path, giay: int = 60) -> tuple[int, str]:
    """Gọi git, trả (mã thoát, đầu ra). Lỗi gọi ⇒ mã thoát khác 0 — người gọi phải xử như «chưa đo được»."""
    try:
        r = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=giay)
        return r.returncode, (r.stdout or "")
    except (OSError, subprocess.SubprocessError):
        return 1, ""


def quet_nhanh(goc: str | Path | None = None) -> dict:
    """ĐẾM thư mục con, KHÔNG gọi git — tức thì, dùng cho giác quan đầu phiên."""
    g = goc_worktree(goc)
    if not g.is_dir():
        return {"do_duoc": False, "ly_do": f"không có thư mục worktree tạm {g} ở máy này", "tong": 0, "ten": [],
                "ung_vien": [], "so_sao_luu": 0, "so_khong_worktree": 0}
    try:
        ten = sorted(p.name for p in g.iterdir() if p.is_dir() and not p.name.startswith("."))
    except OSError as exc:
        return {"do_duoc": False, "ly_do": f"không đọc được {g} ({type(exc).__name__})", "tong": 0, "ten": [],
                "ung_vien": [], "so_sao_luu": 0, "so_khong_worktree": 0}
    # ỨNG VIÊN = worktree git thật, không phải bản sao lưu. Chỉ `stat` nên vẫn tức thì — KHÔNG gọi git.
    # Đo 14/11: đếm TỔNG thư mục làm cảm biến kêu oan (77 thư mục nhưng 41 bản sao lưu + 24 thư mục thường, chỉ 5 cái gỡ được).
    ung_vien = [n for n in ten if not la_sao_luu(n) and (g / n / ".git").exists()]
    return {"do_duoc": True, "ly_do": "", "tong": len(ten), "ten": ten, "ung_vien": ung_vien,
            "so_sao_luu": sum(1 for n in ten if la_sao_luu(n)),
            "so_khong_worktree": len(ten) - len(ung_vien) - sum(1 for n in ten if la_sao_luu(n))}


def dung_luong(d: Path) -> int:
    """Tổng byte của một thư mục (`st_size`, chạy được cả Windows). Tệp không đọc được thì bỏ qua, không làm hỏng cả lượt đo."""
    t = 0
    for dp, _dn, fn in os.walk(d, onerror=lambda _e: None):
        for f in fn:
            try:
                t += os.lstat(os.path.join(dp, f)).st_size
            except OSError:
                pass
    return t


def quet_day_du(goc: str | Path | None = None, chay=None, do_dung_luong: bool = True) -> dict:
    """Phân loại TỪNG worktree: sạch · còn việc dở · bản sao lưu · không phải worktree · chưa đo được."""
    tu_tiem = chay is not None          # người gọi tự lo đường gọi git (bộ kiểm) ⇒ không đòi git trên máy
    chay = chay or _chay_git
    nh = quet_nhanh(goc)
    khung = {"sach": [], "ban": [], "sao_luu": [], "khong_worktree": [], "chua_do": [],
             "byte_sach": 0, "byte_tong": 0}
    if not nh["do_duoc"]:
        return {**nh, **khung}
    if not tu_tiem and shutil.which("git") is None:
        return {"do_duoc": False, "ly_do": "máy này không có git — chưa phân loại được worktree nào",
                "tong": nh["tong"], "ten": nh["ten"], **khung}
    g = goc_worktree(goc)
    kq = {**nh, **khung}
    for ten in nh["ten"]:
        d = g / ten
        b = dung_luong(d) if do_dung_luong else 0
        kq["byte_tong"] += b
        if la_sao_luu(ten):
            kq["sao_luu"].append(ten)
            continue
        if not (d / ".git").exists():
            kq["khong_worktree"].append(ten)
            continue
        rc, out = chay(["status", "--porcelain"], d)
        if rc != 0:
            kq["chua_do"].append(ten)          # đọc không được ⇒ KHÔNG BAO GIỜ tính là gỡ được
            continue
        if out.strip():
            kq["ban"].append(ten)
        else:
            kq["sach"].append(ten)
            kq["byte_sach"] += b
    return kq


def don(ten_ds: list[str], goc: str | Path | None = None, ap_dung: bool = False, chay=None) -> dict:
    """Gỡ worktree SẠCH. Kiểm lại trạng thái NGAY TRƯỚC khi gỡ — không tin danh sách quét trước đó."""
    chay = chay or _chay_git
    g = goc_worktree(goc)
    kq = {"da": [], "bo_qua": [], "loi": []}
    for ten in ten_ds:
        d = g / ten
        if not d.is_dir():
            kq["bo_qua"].append((ten, "không còn thư mục"))
            continue
        if la_sao_luu(ten):
            kq["bo_qua"].append((ten, "là bản sao lưu"))
            continue
        if not (d / ".git").exists():
            kq["bo_qua"].append((ten, "không phải worktree"))
            continue
        rc, out = chay(["status", "--porcelain"], d)
        if rc != 0:
            kq["bo_qua"].append((ten, "không đọc được trạng thái"))
            continue
        if out.strip():
            kq["bo_qua"].append((ten, "vừa có thay đổi chưa commit"))
            continue
        if not ap_dung:
            kq["da"].append(ten)
            continue
        rc2, _ = chay(["worktree", "remove", "--force", str(d)], d)
        if rc2 == 0 and not d.exists():
            kq["da"].append(ten)
        else:
            kq["loi"].append(ten)
    return kq


def ghi_so_do(kq: dict, tep: Path | None = None, bay_gio: dt.datetime | None = None) -> None:
    """Ghi ảnh chụp lượt quét đầy đủ để giác quan nói được về DUNG LƯỢNG mà không phải quét lại."""
    tep = tep or SO_DO
    try:
        tep.parent.mkdir(parents=True, exist_ok=True)
        tep.write_text(json.dumps({
            "do_luc": (bay_gio or dt.datetime.now()).isoformat(timespec="seconds"),
            "tong": kq.get("tong", 0), "so_sach": len(kq.get("sach") or []),
            "byte_tong": kq.get("byte_tong", 0), "byte_sach": kq.get("byte_sach", 0),
        }, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    except OSError:
        pass


def _so_do_gan_nhat(tep: Path | None = None, bay_gio: dt.datetime | None = None) -> tuple[float | None, float | None, str]:
    """(GB tổng, GB sạch, ngày đo) của lượt quét đầy đủ gần nhất — quá hạn/hỏng/vắng ⇒ (None, None, "")."""
    tep = tep or SO_DO
    try:
        d = json.loads(tep.read_text(encoding="utf-8"))
        luc = dt.datetime.fromisoformat(str(d["do_luc"]))
    except (OSError, ValueError, KeyError, TypeError):
        return None, None, ""
    if ((bay_gio or dt.datetime.now()) - luc).days > HAN_SO_DO_NGAY:
        return None, None, ""
    try:
        return float(d["byte_tong"]) / _GB, float(d.get("byte_sach", 0)) / _GB, luc.strftime("%d/%m")
    except (KeyError, TypeError, ValueError):
        return None, None, ""


def giac_quan(goc: str | Path | None = None, quet_fn=None, tep_so_do: Path | None = None,
              bay_gio: dt.datetime | None = None) -> tuple[list[tuple[int, str, str, str]], list[str]]:
    """Giác quan cho hòm việc: (việc, lý do chưa đo được). Chỉ ĐẾM (tức thì) — dung lượng lấy từ ảnh chụp còn hạn, nếu có.

    Không đo được ⇒ ([], [lý do]) — một dòng ⚪, KHÔNG BAO GIỜ đọc thành «worktree vẫn trong ngưỡng»."""
    nh = (quet_fn or quet_nhanh)(goc)
    if not nh.get("do_duoc"):
        return [], [str(nh.get("ly_do") or "không đo được số worktree tạm")]
    tong = int(nh.get("tong") or 0)
    ung = len(nh.get("ung_vien") or [])
    gb, _gb_sach, ngay = _so_do_gan_nhat(tep_so_do, bay_gio)
    if ung >= NGUONG_SO_GAP or (gb is not None and gb >= NGUONG_GB_GAP):
        uu = 1
    elif ung >= NGUONG_SO or (gb is not None and gb >= NGUONG_GB):
        uu = 2
    else:
        return [], []
    them = f" ≈ {gb:.1f} GB (đo {ngay})" if gb is not None else ""
    giu = tong - ung
    dong = (f"{ung} worktree tạm có thể gỡ ở {goc_worktree(goc)}{them} — vượt ngưỡng {NGUONG_SO} "
            f"(tổng {tong}; {giu} bản sao lưu/thư mục thường luôn được giữ); "
            "chỉ worktree SẠCH mới gỡ, cái còn thay đổi chưa commit giữ nguyên")
    return [(uu, "🛎", dong, "python3 tools/don_worktree_tam.py")], []


def _in_bang(kq: dict) -> None:
    g = goc_worktree()
    print(f"Thư mục worktree tạm: {g.as_posix()}")
    if not kq["do_duoc"]:
        print(f"  ⚪ CHƯA ĐO ĐƯỢC — {kq['ly_do']}")
        return
    print(f"  tổng {kq['tong']} worktree · {kq['byte_tong']/_GB:.2f} GB")
    print(f"  ✓ gỡ được (sạch)        : {len(kq['sach']):4}  ({kq['byte_sach']/_GB:.2f} GB)")
    print(f"  ⏸ giữ — còn việc dở     : {len(kq['ban']):4}")
    print(f"  ⏸ giữ — là bản sao lưu  : {len(kq['sao_luu']):4}")
    print(f"  ⏸ giữ — không phải worktree: {len(kq['khong_worktree']):4}")
    if kq["chua_do"]:
        print(f"  ⚪ chưa đo được trạng thái : {len(kq['chua_do']):4}  (không tính là gỡ được)")
    for ten in kq["ban"][:10]:
        print(f"     ⏸ {ten}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Đo mức tích tụ worktree tạm và gỡ những cái SẠCH (chạy khô mặc định).")
    p.add_argument("--goc", help="thư mục worktree tạm (mặc định $EBM_WORKTREES hoặc ~/.ebm-worktrees)")
    p.add_argument("--ap-dung", action="store_true", help="gỡ thật (mặc định chỉ liệt kê)")
    p.add_argument("--nhanh", action="store_true", help="chỉ đếm, không gọi git và không đo dung lượng")
    p.add_argument("--json", dest="tep_json", help="ghi kết quả ra tệp JSON")
    a = p.parse_args(argv)

    if a.nhanh:
        nh = quet_nhanh(a.goc)
        print(f"{nh['tong']} worktree tạm · {len(nh['ung_vien'])} ứng viên gỡ được · "
              f"{nh['so_sao_luu']} bản sao lưu · {nh['so_khong_worktree']} thư mục thường"
              if nh["do_duoc"] else f"⚪ CHƯA ĐO ĐƯỢC — {nh['ly_do']}")
        return 0

    kq = quet_day_du(a.goc)
    _in_bang(kq)
    if kq["do_duoc"]:
        ghi_so_do(kq)
        d = don(kq["sach"], a.goc, ap_dung=a.ap_dung)
        if a.ap_dung:
            print(f"\n  ✓ đã gỡ {len(d['da'])} worktree · bỏ qua {len(d['bo_qua'])} · lỗi {len(d['loi'])}")
            for ten, vi in d["bo_qua"][:10]:
                print(f"     ⏸ {ten} — {vi}")
        else:
            print(f"\n  → chạy khô: {len(d['da'])} worktree sẽ được gỡ. Gỡ thật: thêm --ap-dung")
    if a.tep_json:
        Path(a.tep_json).write_text(json.dumps(kq, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
