#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HÒM VIỆC MỘT CỬA — ≤ 12 dòng việc của bác sĩ lúc mở phiên (HV-02, kiểm toàn diện 02/10/2026).

VÌ SAO CÓ. Đo 02/10: quét 986 sự kiện SessionStart trong nhật ký phiên — chứa «TỰ ĐỀ XUẤT VIỆC» = 0, nhắc cổng/PR = 0. Bảng tự đề xuất
(`tu_de_xuat_viec.py`) chỉ hiện khi có người nhớ mở; tín hiệu thật chìm trong ~7 KB banner đầu phiên. Bảng đầy đủ chạy ~12 giây (gọi
mạng, nhiều công cụ) — quá chậm cho hook đầu phiên. Nên công cụ này:
  • `--doc` (hook dùng): đọc bảng ĐÃ SINH SẴN `state/hom-viec.json`, in ≤ 12 dòng — việc 👤 (thẩm quyền bác sĩ) trước theo ưu tiên,
    rồi 🛎 (máy làm được nhưng chưa ai chạy), 🤖 chỉ đếm một dòng. Nhanh (< 1 giây), không gọi mạng.
  • bảng vắng / cũ hơn 12 giờ ⇒ nói rõ «cũ N giờ», và với `--lam-moi-nen` phóng một lượt làm mới Ở NỀN (tách tiến trình; khoá chống
    chạy chồng) để lần mở phiên sau có bảng tươi. Không bao giờ chặn phiên, mã thoát 0.
  • `--lam-moi`: chạy `tu_de_xuat_viec.py --gon --json state/hom-viec.json` ngay (tác vụ lịch/gói tuần dùng).

Chỉ ĐỌC và NHẮC — không tự làm việc 👤 nào. Chạy cả Mac lẫn Windows (`sys.executable`, `start_new_session`/`DETACHED_PROCESS`).
Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parent.parent
TEP = REPO / "state" / "hom-viec.json"
KHOA = REPO / "state" / "hom-viec.khoa"
HAN_GIO = 12
KHOA_HET_HAN_PHUT = 10
TOI_DA_DONG = 12


def doc(tep: Path | None = None) -> dict | None:
    tep = tep or TEP
    try:
        d = json.loads(tep.read_text(encoding="utf-8"))
        return d if isinstance(d, dict) and isinstance(d.get("viec"), list) else None
    except (OSError, ValueError):
        return None


def tuoi_gio(d: dict, bay_gio: datetime | None = None) -> float | None:
    try:
        return ((bay_gio or datetime.now()) - datetime.fromisoformat(str(d["sinh_luc"]))).total_seconds() / 3600
    except (KeyError, ValueError, TypeError):
        return None


def dong_hom(d: dict | None, bay_gio: datetime | None = None, toi_da: int = TOI_DA_DONG) -> list[str]:
    """Các dòng in ra (≤ toi_da). Thuần — không I/O."""
    if d is None:
        return ["📥 HÒM VIỆC: chưa có bảng (state/hom-viec.json) — đang dựng ở nền; xem ngay: python3 tools/tu_de_xuat_viec.py"]
    viec = [v for v in d["viec"] if isinstance(v, dict)]
    bac_si = sorted([v for v in viec if v.get("ai") == "👤"], key=lambda v: v.get("uu", 9))
    chuong = sorted([v for v in viec if v.get("ai") == "🛎"], key=lambda v: v.get("uu", 9))
    may = [v for v in viec if v.get("ai") == "🤖"]
    tuoi = tuoi_gio(d, bay_gio)
    cu = f" · ⚠ bảng cũ {tuoi:.0f} giờ" if tuoi is not None and tuoi > HAN_GIO else ""
    ra = [f"📥 HÒM VIỆC — {len(bac_si)} việc của bác sĩ · {len(chuong)} chờ người chạy · {len(may)} máy tự lo"
          f" (sinh {str(d.get('sinh_luc', '?'))[:16].replace('T', ' ')}{cu})"]
    cho = toi_da - 2
    for v in (bac_si + chuong)[:cho]:
        bieu = "🔴" if v.get("uu") == 0 else "🟠" if v.get("uu") == 1 else "🟡"
        ra.append(f"  {bieu} {v.get('ai')} {str(v.get('viec', ''))[:150]}")
    con = len(bac_si) + len(chuong) - cho
    chet = d.get("chet") or []
    duoi = []
    if con > 0:
        duoi.append(f"+{con} việc nữa")
    if chet:
        duoi.append(f"⚪ {len(chet)} giác quan không đo được")
    if not bac_si and not chuong and not chet:
        duoi.append("🟢 không có việc nào chờ bác sĩ")
    ra.append("  " + " · ".join(duoi + ["đủ lệnh: python3 tools/tu_de_xuat_viec.py"]))
    return ra[:toi_da]


def _khoa_con_hieu_luc(bay_gio: datetime | None = None) -> bool:
    try:
        return ((bay_gio or datetime.now()) - datetime.fromtimestamp(KHOA.stat().st_mtime)) < timedelta(minutes=KHOA_HET_HAN_PHUT)
    except OSError:
        return False


def phong_nen() -> bool:
    """Phóng `--lam-moi` ở NỀN (tách khỏi phiên). Đã có lượt đang chạy (khoá còn hiệu lực) ⇒ không phóng thêm."""
    if _khoa_con_hieu_luc():
        return False
    kw: dict = {"stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL, "cwd": str(REPO)}
    if os.name == "nt":
        kw["creationflags"] = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    else:
        kw["start_new_session"] = True
    try:
        subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--lam-moi"], **kw)
        return True
    except OSError:
        return False


def lam_moi(tep: Path | None = None) -> int:
    tep = tep or TEP
    tep.parent.mkdir(parents=True, exist_ok=True)
    if KHOA.exists() and not _khoa_con_hieu_luc():
        try:
            KHOA.unlink()
        except OSError:
            pass
    try:
        fd = os.open(str(KHOA), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
    except FileExistsError:
        print("⏳ đang có lượt làm mới hòm việc khác — không chạy chồng")
        return 0
    try:
        r = subprocess.run([sys.executable, str(REPO / "tools" / "tu_de_xuat_viec.py"), "--gon", "--json", str(tep)],
                           cwd=str(REPO), capture_output=True, text=True, timeout=300, encoding="utf-8", errors="replace")
        return 0 if r.returncode == 0 and doc(tep) is not None else 2
    except (OSError, subprocess.SubprocessError):
        return 2
    finally:
        try:
            KHOA.unlink()
        except OSError:
            pass


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Hòm việc một cửa — ≤ 12 dòng việc của bác sĩ (đọc bảng sinh sẵn)")
    ap.add_argument("--doc", action="store_true", help="in hòm việc từ state/hom-viec.json (mặc định)")
    ap.add_argument("--lam-moi-nen", action="store_true", help="cùng --doc: bảng vắng/cũ ⇒ phóng lượt làm mới ở nền")
    ap.add_argument("--lam-moi", action="store_true", help="làm mới bảng NGAY (chạy tu_de_xuat_viec.py --json)")
    a = ap.parse_args(argv)
    if a.lam_moi:
        return lam_moi()
    d = doc()
    for dong in dong_hom(d):
        print(dong)
    tuoi = tuoi_gio(d) if d else None
    if a.lam_moi_nen and (d is None or tuoi is None or tuoi > HAN_GIO):
        phong_nen()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
