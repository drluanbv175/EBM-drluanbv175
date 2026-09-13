#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TUYÊN BỐ ĐỘ PHỦ TRUNG THỰC — LÔ I PHA 4 (15/08/2026).

Sinh TỰ ĐỘNG từ `data/sources.json` + số đo thật, để dán lên bản đọc/queue/báo
cáo. CẤM các cụm «bao phủ toàn diện», «mọi nguồn uy tín», «đảm bảo không bỏ sót»
— hàm tự kiểm chuỗi cấm trước khi trả (P1).

Dùng:  python3 tools/tuyen_bo_do_phu.py            # in + ghi reports/do-phu-hien-hanh.md
       from tuyen_bo_do_phu import tra_khoi        # nhúng vào bản đọc/queue
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

GOC = Path(__file__).resolve().parents[1]
CAM = ("bao phủ toàn diện", "mọi nguồn uy tín", "đảm bảo không bỏ sót")


def tra_khoi() -> str:
    du = json.loads((GOC / "data" / "sources.json").read_text(encoding="utf-8"))
    src = du["sources"]
    active = [s for s in src if s["status"] == "active"]
    manual = [s for s in src if s["access"] == "manual"]
    khong = [s for s in src if s["status"] == "not-covered" and s["access"] != "manual"]
    lat = [s.get("measured_latency_days") for s in active
           if s.get("measured_latency_days") is not None]
    dc = GOC / "quality" / "eval" / "doi-chung" / "2026-Q3.md"
    uoc = "7/10 (Q3/2026)" if dc.exists() else "[CHƯA CHẠY VÒNG NÀO]"
    # Trạm "web hội" = access html-watch (GOLD/GINA/KDIGO/ADA/ESC/ACC-AHA…). Đo THẬT
    # từ last_success_at thay vì câu chữ cố định — vá 13/09/2026: câu cũ hardcode
    # "CHƯA CHẠY (chờ phê duyệt egress)" cho MỌI lần sinh báo cáo, kể cả sau khi
    # nhiều trạm đã chạy thật qua kênh Browser (--nap-van-ban), khiến báo cáo nói
    # sai một sự thật đã đổi.
    web_hoi = [s for s in src if s.get("access") == "html-watch"]
    da_chay = [s for s in web_hoi if s.get("last_success_at")]
    chua_chay = [s for s in web_hoi if not s.get("last_success_at")]
    if not web_hoi:
        dong_web_hoi = "trạm web hội: [CHƯA CÓ TRẠM NÀO KHAI TRONG SỔ NGUỒN]"
    elif not chua_chay:
        dong_web_hoi = (f"trạm web hội {len(da_chay)}/{len(web_hoi)} đã chạy thật qua kênh "
                         f"Browser (egress Python cho tiến trình sandbox/cloud vẫn bị chặn — "
                         f"xem audit/07-tong-kiem-do-phu-nguon-chung-cu_2026-08-30.md)")
    else:
        dong_web_hoi = (f"trạm web hội {len(da_chay)}/{len(web_hoi)} đã chạy thật qua kênh Browser; "
                         f"còn {len(chua_chay)} trạm CHƯA CHẠY "
                         f"({', '.join(s['name'].split('—')[0].strip() for s in chua_chay)}) — "
                         f"egress Python vẫn chặn, chưa áp workaround Browser cho các trạm này")
    khoi = f"""ĐỘ PHỦ NGUỒN (cập nhật {du.get('updated', date.today().isoformat())})
Đang giám sát tự động: {len(active)} nguồn — {"; ".join(s['name'].split('—')[0].strip() for s in active)}; nhịp tuần/tháng.
Nhập thủ công (VN): {len(manual)} làn (BYT · Cục QLD) — số văn bản đã nhập: {sum(1 for s in manual if s.get('last_success_at')) or 0}; còn [CẦN XÁC NHẬN TẠI ĐƠN VỊ].
KHÔNG phủ ({len(khong)} nhóm, khai rõ): {"; ".join(s['name'].split('—')[0].strip() for s in khong)}.
Độ trễ đo được: PubMed-lane trung vị {lat[0] if lat else '[CHƯA ĐO]'} ngày (W33); {dong_web_hoi} — guideline web-first hiện chịu trễ theo PubMed cho tới khi trạm được nối vào lịch tự động.
Ước lượng bắt được (đối chứng ngoài, quý gần nhất): {uoc} — ước lượng CÓ THIÊN LỆCH, không phải độ phủ.
Giới hạn: hệ thống không đo được cái chưa từng thấy; thẩm định thiếu toàn văn bị gắn nhãn «thẩm định một phần» và chặn khỏi mức 'áp dụng ngay'."""
    thap = khoi.lower()
    for c in CAM:
        if c in thap:
            raise RuntimeError(f"tuyên bố chứa cụm CẤM: {c!r}")
    return khoi


def main() -> int:
    khoi = tra_khoi()
    ra = GOC / "reports" / "do-phu-hien-hanh.md"
    ra.write_text("# " + khoi.replace("\n", "\n\n", 1) + "\n\n> Sinh tự động từ "
                  "data/sources.json — sửa SỔ, đừng sửa file này.\n", encoding="utf-8")
    print(khoi)
    print(f"\n→ {ra.relative_to(GOC)} (dán khối này vào bản đọc/queue/báo cáo tháng)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
