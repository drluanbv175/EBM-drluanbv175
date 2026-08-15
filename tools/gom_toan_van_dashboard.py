#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GOM TOÀN VĂN OA CHO DASHBOARD LÂM SÀNG — kho DÙNG CHUNG theo PMID (nâng cấp A, 15/08/2026).

Vì sao: bộ máy toàn văn (gom → hỏi → đối chiếu số) đã chạy cho đề tài nghiên cứu
(C1a); phía lâm sàng `kiem_so_lieu` vẫn chỉ đọc TÓM TẮT nên tồn cả lớp ⚪ «không
thấy» dù con số nằm ngay trong thân bài. Tool này phủ kho toàn văn sang lâm sàng.

Khác bản nghiên cứu (`medical-ebm-automation/tools/gom_toan_van_oa.py` — kho THEO
ĐỀ TÀI): kho ở đây DÙNG CHUNG toàn thư mục `EBM-Dashboards/toan_van_oa/`, khoá theo
PMID, tải một lần dùng cho mọi dashboard. TÁI DÙNG nguyên hàm của bản nghiên cứu
(qua importlib — không chép đôi logic, kế thừa luôn bộ lọc `pubmed_pmc` của BH53).

P5 giữ nguyên: chỉ PMC Open Access — không cào nguồn trả phí. Bài không-OA được
ghi rõ, KHÔNG đoán. Chạy lại an toàn: PMID đã có XML thì bỏ qua (idempotent).

Dùng:  python3 tools/gom_toan_van_dashboard.py            # mọi dashboard
       python3 tools/gom_toan_van_dashboard.py --file EBM-Dashboards/WebDashboard_X.html
Mã thoát: 0 = chạy trọn · 2 = hạ tầng (elink chết toàn phần).
"""
from __future__ import annotations

import argparse
import glob
import importlib.util
import re
import sys
import time
from datetime import date
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
DASH = REPO / "EBM-Dashboards"
KHO = DASH / "toan_van_oa"


def _nap_gom():
    duong = REPO / "medical-ebm-automation" / "tools" / "gom_toan_van_oa.py"
    sp = importlib.util.spec_from_file_location("gom_tv_nc", duong)
    m = importlib.util.module_from_spec(sp)
    sys.modules["gom_tv_nc"] = m
    sp.loader.exec_module(m)
    return m


def pmids_tu_dashboard(f: Path) -> set[str]:
    t = f.read_text(encoding="utf-8", errors="replace")
    return set(re.findall(r"pmid['\"]?\s*[:=]\s*['\"](\d{6,9})['\"]", t, re.I))


def main() -> int:
    ap = argparse.ArgumentParser(description="Gom toàn văn PMC-OA dùng chung cho dashboard")
    ap.add_argument("--file", nargs="*", help="dashboard cụ thể (mặc định: tất cả)")
    ap.add_argument("--gioi-han", type=int, default=0,
                    help="chỉ xử lý N PMID chưa có mỗi lần chạy (0 = không giới hạn)")
    a = ap.parse_args()
    files = ([Path(p) for m in a.file for p in glob.glob(m)] if a.file
             else sorted(DASH.glob("WebDashboard_*.html")))
    files = [f for f in files if f.exists()]
    if not files:
        print("✗ Không thấy dashboard nào.")
        return 2
    pmids: set[str] = set()
    for f in files:
        pmids |= pmids_tu_dashboard(f)
    KHO.mkdir(parents=True, exist_ok=True)
    da_co = {re.search(r"PMID-(\d+)_", p.name).group(1) for p in KHO.glob("PMID-*.xml")}
    khong_pmc_cu: set[str] = set()
    ghi_chu = KHO / "khong-oa.txt"   # nhớ bài đã tra và KHÔNG lấy được — khỏi tra lại
    if ghi_chu.exists():
        khong_pmc_cu = set(ghi_chu.read_text(encoding="utf-8").split())
    can = sorted(pmids - da_co - khong_pmc_cu)
    if a.gioi_han:
        can = can[: a.gioi_han]
    print(f"Kho chung: {len(da_co)} toàn văn sẵn có · {len(pmids)} PMID trong "
          f"{len(files)} dashboard · cần tra lần này: {len(can)}")
    if not can:
        print("✓ Không có gì mới để gom.")
        return 0
    gom = _nap_gom()
    try:
        anh_xa = gom.lien_ket_pmc(can)
    except Exception as exc:  # noqa: BLE001
        print(f"🔴 HẠ TẦNG: elink không trả lời ({type(exc).__name__}) — chưa gom, "
              "KHÔNG kết luận độ phủ.")
        return 2
    moi, khong_oa, khong_pmc = 0, [], []
    loi_mang = 0
    for pm in can:
        pmcid = anh_xa.get(pm)
        if not pmcid:
            khong_pmc.append(pm)
            continue
        # Lỗi MỘT bài không được giết CẢ lượt (đo thật 15/08: IncompleteRead ở file
        # 17/600 làm mất trọn lượt chạy dài). Bài lỗi mạng KHÔNG vào danh sách
        # «không-OA» — đó là CHƯA TẢI ĐƯỢC, lần chạy sau thử lại (idempotent).
        try:
            xml = gom.tai_toan_van(pmcid)
        except Exception:  # noqa: BLE001
            loi_mang += 1
            continue
        time.sleep(0.34)
        if xml:
            (KHO / f"PMID-{pm}_PMC{pmcid}.xml").write_bytes(xml)
            moi += 1
        else:
            khong_oa.append(pm)
    if loi_mang:
        print(f"  ⚠ {loi_mang} bài lỗi mạng lượt này — CHƯA tải được (không phải "
              "không-OA); chạy lại tool sẽ thử tiếp.")
    # ghi nhớ nhóm không lấy được (tra lại tốn mạng vô ích; xoá file này nếu muốn tra lại)
    ghi_chu.write_text("\n".join(sorted(khong_pmc_cu | set(khong_pmc) | set(khong_oa))) + "\n",
                       encoding="utf-8")
    tong_co = len(da_co) + moi
    (KHO / "DO-PHU-OA.md").write_text(
        f"# ĐỘ PHỦ TOÀN VĂN OA — kho dùng chung dashboard — {date.today().isoformat()}\n\n"
        f"- Toàn văn OA trong kho: **{tong_co}/{len(pmids)}** PMID đang được dashboard trích\n"
        f"- Lượt này: +{moi} tải mới · {len(khong_oa)} có PMC nhưng không-OA · "
        f"{len(khong_pmc)} không có bản PMC\n\n"
        "> Phần không-OA cần quyền truy cập của bác sĩ — độ phủ thấp là SỰ THẬT về OA,\n"
        "> không phải lỗi. Cần bác sĩ kiểm chứng.\n", encoding="utf-8")
    print(f"  +{moi} toàn văn mới · không-OA {len(khong_oa)} · không-PMC {len(khong_pmc)} "
          f"→ kho {tong_co}/{len(pmids)} PMID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
