#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CHỦ ĐỀ NÀO NÊN CẬP NHẬT TRƯỚC? — xếp theo (có chứng cứ MỚI) × (lâu chưa xem lại).

VÌ SAO CÓ (14/08/2026)
======================
`kiem_do_tuoi_chung_cu.py` trả lời được "chủ đề nào lâu chưa xem lại" — đo 14/08 là
**37/59 chủ đề quá 35 ngày**. Nhưng danh sách đó KHÔNG dùng để làm việc được: tuổi
tự nó không phải lý do cập nhật. Một chủ đề 68 ngày mà y văn không có gì mới thì
bản cũ vẫn đúng; một chủ đề 27 ngày mà vừa có 4 nghiên cứu đổi thực hành thì đã cũ.

Đo thật ngày dựng công cụ: trong 24 chủ đề có canh, **12 chủ đề KHÔNG có ứng viên
mới nào trong 75 ngày** dù nhiều mục đã 47–68 ngày tuổi. Nếu xếp việc theo tuổi
thuần, bác sĩ sẽ tiêu công vào đúng nhóm 12 chủ đề không cần đụng đó.

Ghép hai trục lại: **tuổi** (từ tên file, `kiem_do_tuoi_chung_cu`) × **số ứng viên
mới** (từ `surveillance_scan.py` — bộ thu thập CHỦ SỞ HỮU duy nhất, chế độ ứng viên).

GIỚI HẠN CÓ CHỦ Ý
=================
Chỉ ĐO và XẾP. Không tự chạy cập nhật, không tự nạp sổ cái, không đọc nội dung ứng
viên để phán "cần đổi thực hành" — số ứng viên là tín hiệu ĐỘNG LỰC, không phải kết
luận về chứng cứ. Bác sĩ quyết chủ đề nào làm trước.

Dùng:
    python tools/uu_tien_cap_nhat.py                 # quét mới (gọi mạng)
    python tools/uu_tien_cap_nhat.py --tu-json F     # dùng lại kết quả quét đã có
    python tools/uu_tien_cap_nhat.py --ngay 90       # cửa sổ tìm chứng cứ mới

Mã thoát: 0 luôn — đây là bảng xếp việc, không phải cổng.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
DASH = REPO / "EBM-Dashboards"
BANDO = DASH / "giam-sat-chu-de.json"


def _nap(ten_file: str, ten: str):
    spec = importlib.util.spec_from_file_location(ten, REPO / "tools" / ten_file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main() -> int:
    ap = argparse.ArgumentParser(description="Xếp thứ tự chủ đề nên cập nhật trước")
    ap.add_argument("--tu-json", help="dùng lại file JSON của surveillance_scan.py")
    ap.add_argument("--ngay", type=int, default=75, help="cửa sổ tìm chứng cứ mới (mặc định 75)")
    ap.add_argument("--max", type=int, default=6, help="số ứng viên tối đa mỗi chủ đề")
    a = ap.parse_args()

    if not BANDO.exists():
        print("⚠ Chưa có EBM-Dashboards/giam-sat-chu-de.json — chạy "
              "`python tools/kiem_phu_giam_sat.py` trước.")
        return 0
    bando = json.loads(BANDO.read_text(encoding="utf-8")).get("muc", {})

    if a.tu_json:
        du = json.loads(Path(a.tu_json).read_text(encoding="utf-8"))
    else:
        out = Path(tempfile.mkdtemp()) / "quet.json"
        print(f"Đang quét {a.ngay} ngày gần nhất (gọi mạng, có thể mất vài phút)…")
        r = subprocess.run(
            [sys.executable, str(DASH / "tools" / "surveillance_scan.py"),
             "--days", str(a.ngay), "--max", str(a.max),
             "--json-report", str(out), "--report", str(out.with_suffix(".md"))],
            capture_output=True, text=True)
        if not out.exists():
            print("✗ Quét không tạo được báo cáo — KHÔNG kết luận gì về độ ưu tiên.")
            print((r.stderr or r.stdout or "")[-400:])
            return 0
        du = json.loads(out.read_text(encoding="utf-8"))

    if du.get("status") != "PASS":
        # Quét PARTIAL/FAIL ⇒ số ứng viên THẤP có thể chỉ vì nguồn hỏng. Nói ra, không
        # để bác sĩ đọc "0 ứng viên" thành "không có gì mới".
        print(f"⚠ Lần quét ở trạng thái {du.get('status')} — số ứng viên có thể THIẾU do")
        print("  nguồn trục trặc, KHÔNG phải vì y văn không có gì mới.")

    per = {t["topic"]: len(t.get("candidates") or []) for t in du.get("topics", [])}
    kt = _nap("kiem_do_tuoi_chung_cu.py", "kt_uu_tien")
    tuoi = dict(kt.lau_chua_xem_lai())

    hang = []
    for goc, wl in bando.items():
        n = per.get(wl)
        if n is None:
            continue
        t = max((v for k, v in tuoi.items() if k.split("_")[0] == goc), default=None)
        if t is None:
            continue
        hang.append((n, t, goc, wl))
    if not hang:
        print("Không ghép được chủ đề nào — kiểm lại giam-sat-chu-de.json.")
        return 0
    hang.sort(key=lambda x: (-x[0], -x[1]))

    print(f"\nƯU TIÊN CẬP NHẬT — {du.get('candidate_count', '?')} ứng viên mới trong "
          f"{du.get('days', a.ngay)} ngày, {len(hang)} chủ đề có canh")
    print(f"{'mới':>4} {'ngày':>5}  chủ đề")
    for n, t, goc, wl in hang:
        if n == 0:
            continue
        print(f"{n:>4} {t:>5}  {goc:<24} ← {wl[:40]}")
    im = [g for n, _t, g, _w in hang if n == 0]
    if im:
        print(f"\n{len(im)} chủ đề KHÔNG có chứng cứ mới trong cửa sổ này — cũ nhưng chưa")
        print("cần đụng tới (tuổi tự nó KHÔNG phải lý do cập nhật):")
        print("   " + " · ".join(im))
    print("\nSố ứng viên là tín hiệu ĐỘNG LỰC, không phải kết luận về chứng cứ: công cụ")
    print("KHÔNG đọc nội dung ứng viên và không phán chúng có đổi thực hành hay không.")
    print("Chạy `/cap-nhat-chung-cu <chủ đề>` cho mục bác sĩ chọn. Cần bác sĩ kiểm chứng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
