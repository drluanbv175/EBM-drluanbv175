#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HIỆU SỐ TRÍCH TRONG DASHBOARD CÓ THẬT TRONG BÀI KHÔNG? — đối chiếu với tóm tắt.

VÌ SAO CÓ (14/08/2026)
======================
Hệ đang xác minh **"PMID có thật + tiêu đề khớp"**. Nó KHÔNG xác minh thứ bác sĩ thật
sự đọc: **con số**. Một mục có thể trích đúng PMID, đúng tiêu đề, mà hiệu số lại là số
của một kết cục khác, một phân nhóm khác, hoặc đơn giản là gõ sai — và không cổng nào
bắt được. Đây là khoảng trống lớn nhất còn lại về ĐỘ TIN CẬY sau khi đã đóng chuỗi
"nguồn có thật / chưa bị rút".

CÁCH ĐỌC KẾT QUẢ — QUAN TRỌNG
==============================
Tóm tắt PubMed **thường không chứa** mọi con số của bài. Vì vậy công cụ này phân ba
mức và **cố ý không có mức "SAI"**:

  ✓ KHỚP        — tìm thấy cả ước lượng điểm lẫn hai đầu khoảng tin cậy trong tóm tắt.
  🟠 MỘT PHẦN   — thấy ước lượng điểm nhưng không thấy đủ khoảng tin cậy.
  ⚪ KHÔNG THẤY — tóm tắt không nêu con số nào khớp. **KHÔNG kết luận là trích sai**:
                  rất nhiều bài chỉ để số trong toàn văn/bảng.

Nói "sai" từ việc vắng mặt trong tóm tắt chính là biến *không biết* thành *có vấn đề* —
lỗi BH08 đã trả giá nhiều lần trong kho này. Nên mức nặng nhất ở đây là **cảnh báo để
đọc lại**, không phải phán quyết.

Xử lý được cả ba lối viết số: `0.72` · `0·72` (Lancet dùng dấu chấm giữa) · `0,72`.

Dùng:
    python tools/kiem_so_lieu.py                 # mọi item có effect{hr,lo,hi}
    python tools/kiem_so_lieu.py --file F
    python tools/kiem_so_lieu.py --chi-apply     # chỉ mục decision='apply'

Mã thoát: 0 = không có mục nào ở mức MỘT PHẦN/KHÔNG THẤY · 1 = có mục cần đọc lại.
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", line_buffering=True)
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
DASH = REPO / "EBM-Dashboards"
EFETCH = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
          "?db=pubmed&rettype=abstract&retmode=text&id=")


def lay_tom_tat(pmid: str) -> str | None:
    req = urllib.request.Request(EFETCH + pmid, headers={"User-Agent": "EBM-Copilot/1.0"})
    for lan in range(3):
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                t = r.read().decode("utf-8", "replace")
            if "<html" in t[:200].lower():
                raise ValueError("NCBI trả HTML")
            return t
        except (urllib.error.URLError, ValueError):
            if lan < 2:
                time.sleep(1.5 * (lan + 1))
    return None


def _chuan_hoa(t: str) -> str:
    """Đưa mọi lối viết số về dạng dấu chấm để so được: 0·72 và 0,72 → 0.72."""
    return re.sub(r"(?<=\d)[·,](?=\d)", ".", t)


def co_so(van_ban: str, x: float) -> bool:
    """Số x có xuất hiện như MỘT SỐ RIÊNG trong văn bản không (không phải phần của số khác)."""
    s = f"{x:g}"
    return re.search(r"(?<![\d.])" + re.escape(s) + r"(?![\d])", van_ban) is not None


def doc_effect(chunk: str) -> tuple[float, float, float] | None:
    def num(k):
        m = re.search(rf"\b{k}\s*:\s*(-?\d+(?:\.\d+)?)", chunk)
        return float(m.group(1)) if m else None
    hr, lo, hi = num("hr"), num("lo"), num("hi")
    if hr is None or lo is None or hi is None:
        return None
    return hr, lo, hi


def main() -> int:
    ap = argparse.ArgumentParser(description="Đối chiếu hiệu số trong dashboard với tóm tắt bài")
    ap.add_argument("--file", help="chỉ một dashboard")
    ap.add_argument("--chi-apply", action="store_true", help="chỉ mục decision='apply'")
    ap.add_argument("--gioi-han", type=int, help="chỉ N mục đầu")
    a = ap.parse_args()

    spec = importlib.util.spec_from_file_location("vd_so", DASH / "tools" / "verify_dashboard.py")
    vd = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vd)

    viec: list[tuple] = []
    files = [Path(a.file)] if a.file else sorted(DASH.glob("WebDashboard_*.html"))
    for f in files:
        try:
            blk = vd.extract_data_block(f.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        if not blk:
            continue
        for c in vd.split_items(blk):
            pm = vd.field(c, "pmid")
            dec = vd.field(c, "decision") or ""
            if not pm or (a.chi_apply and dec != "apply"):
                continue
            e = doc_effect(c)
            if e:
                viec.append((f.name, vd.field(c, "id"), pm, dec, e))
    if a.gioi_han:
        viec = viec[:a.gioi_han]

    print(f"Đối chiếu {len(viec)} mục có hiệu số định lượng…")
    tom_tat: dict[str, str | None] = {}
    khop = mot_phan = khong_thay = hong = 0
    can_doc: list[tuple] = []
    for k, (fn, iid, pm, dec, (hr, lo, hi)) in enumerate(viec, 1):
        if pm not in tom_tat:
            tom_tat[pm] = lay_tom_tat(pm)
            time.sleep(0.34)
        tt = tom_tat[pm]
        if tt is None:
            hong += 1
            continue
        t = _chuan_hoa(tt)
        c_hr, c_lo, c_hi = co_so(t, hr), co_so(t, lo), co_so(t, hi)
        if c_hr and c_lo and c_hi:
            khop += 1
        elif c_hr:
            mot_phan += 1
            can_doc.append(("🟠 MỘT PHẦN", fn, iid, pm, dec, hr, lo, hi))
        else:
            khong_thay += 1
            can_doc.append(("⚪ KHÔNG THẤY", fn, iid, pm, dec, hr, lo, hi))
        if k % 25 == 0:
            print(f"  … {k}/{len(viec)}")

    print("\n" + "=" * 70)
    print(f"  ✓ KHỚP đầy đủ : {khop}")
    print(f"  🟠 MỘT PHẦN   : {mot_phan}  (thấy ước lượng điểm, không đủ khoảng tin cậy)")
    print(f"  ⚪ KHÔNG THẤY : {khong_thay}  (tóm tắt không nêu — KHÔNG kết luận là trích sai)")
    if hong:
        print(f"  ⚠ Không lấy được tóm tắt: {hong} — 'chưa kiểm', không phải 'không sao'")
    print("=" * 70)
    if not can_doc:
        print("  🟢 Mọi hiệu số đều tìm thấy đủ trong tóm tắt.")
        return 0
    print("  Danh sách nên đọc lại (ưu tiên decision='apply'):\n")
    can_doc.sort(key=lambda x: (x[4] != "apply", x[0]))
    for muc, fn, iid, pm, dec, hr, lo, hi in can_doc[:40]:
        print(f"  {muc}  {fn.replace('WebDashboard_EBM_VanDeCuThe_', '')[:34]:36} {iid:8} "
              f"dec={dec:9} PMID {pm}  trích {hr} ({lo}–{hi})")
    if len(can_doc) > 40:
        print(f"  … và {len(can_doc) - 40} mục nữa")
    print("\n  ⚪ KHÔNG THẤY là chuyện BÌNH THƯỜNG: nhiều bài chỉ để số trong toàn văn/bảng.")
    print("  Công cụ KHÔNG kết luận trích sai và KHÔNG sửa gì. Cần bác sĩ kiểm chứng.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
