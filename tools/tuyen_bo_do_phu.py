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
# Nhịp quét ĐỊNH KỲ theo thứ tự in ra; `ad-hoc` cố ý không có ở đây (xem `_tach_theo_nhip`).
TEN_NHIP = (("daily", "ngày"), ("weekly", "tuần"), ("monthly", "tháng"), ("quarterly", "quý"))


def _ten(s: dict) -> str:
    return s["name"].split("—")[0].strip()


def _tach_theo_nhip(active: list[dict]) -> tuple[list[dict], list[dict]]:
    """Tách nguồn active thành (quét ĐỊNH KỲ, gọi THEO YÊU CẦU) theo `scan_frequency` của sổ.

    VÁ 30/09/2026: dòng «Đang giám sát tự động: N nguồn … nhịp tuần/tháng» từng đếm MỌI nguồn
    `status == "active"`. Từ 22–23/09 sổ có thêm các nguồn `scan_frequency: "ad-hoc"` — connector MCP chỉ
    gọi được trong phiên tương tác (Cochrane, Scite, Wiley), connector toàn văn gọi tay theo URL/DOI, bậc
    thang dự phòng chỉ chạy khi thiếu chứng cứ — nên đo 30/09: 9/30 nguồn in dưới «giám sát tự động» KHÔNG
    hề được quét định kỳ, và mỗi lần đăng ký thêm một công cụ gọi-theo-yêu-cầu (RxNorm chuẩn hoá tên thuốc…)
    con số đó lại tăng. «Active» nghĩa là DÙNG ĐƯỢC, không phải ĐANG ĐƯỢC QUÉT — gộp hai thứ là nói quá độ
    phủ ngay trong tuyên bố mang chữ «trung thực». Nguồn thiếu `scan_frequency` (fixture cũ) giữ ở nhóm định
    kỳ như trước; sổ thật luôn có trường này (hợp đồng `contracts/sources.schema.json`).
    """
    theo_yeu_cau = [s for s in active if s.get("scan_frequency") == "ad-hoc"]
    dinh_ky = [s for s in active if s.get("scan_frequency") != "ad-hoc"]
    return dinh_ky, theo_yeu_cau


def _dong_nhap_thu_cong(manual: list[dict]) -> str:
    """Dòng «Nhập thủ công»: TÊN từng làn `access: manual` và làn đó đã nhập hay chưa — đọc từ sổ, không viết cứng.

    VÁ 30/09/2026: dòng cũ là «Nhập thủ công (VN): N làn (BYT · Cục QLD) — số văn bản đã nhập: M» với nhãn viết
    cứng và hai con số đếm MỌI mục `access: manual`. Đo trên sổ 30/09 nó in «3 làn (BYT · Cục QLD) — số văn bản
    đã nhập: 1» trong khi: BYT đã là làn tự động từ 22/09 (SRC-020, html-watch); ba mục `manual` lúc đó là Cục QLD,
    Epistemonikos (API chờ token) và Wiley Scholar Gateway (connector MCP); còn «1 văn bản đã nhập» chính là ngày
    kiểm sống của Wiley — KHÔNG văn bản Việt Nam nào từng được nhập. In tên và trạng thái từng làn thì một mục khai
    nhầm `manual` hiện ra bằng TÊN ở đây thay vì lẩn trong một con số.
    """
    if not manual:
        return "Nhập thủ công: không có làn nào khai trong sổ; còn [CẦN XÁC NHẬN TẠI ĐƠN VỊ]."
    muc = [f"{_ten(s)} ({'lần nhập gần nhất ' + str(s['last_success_at']) if s.get('last_success_at') else 'CHƯA nhập văn bản nào'})"
           for s in manual]
    return f"Nhập thủ công: {len(manual)} làn — {'; '.join(muc)}; còn [CẦN XÁC NHẬN TẠI ĐƠN VỊ]."


def tra_khoi() -> str:
    du = json.loads((GOC / "data" / "sources.json").read_text(encoding="utf-8"))
    src = du["sources"]
    # Làn `access: manual` chỉ thuộc dòng «Nhập thủ công» — nhập tay không phải «giám sát tự động» dù mục đó active.
    active = [s for s in src if s["status"] == "active" and s["access"] != "manual"]
    dinh_ky, theo_yeu_cau = _tach_theo_nhip(active)
    co_nhip = {s.get("scan_frequency") for s in dinh_ky}
    nhip = "/".join(ten for ma, ten in TEN_NHIP if ma in co_nhip) or "tuần/tháng"
    dong_theo_yeu_cau = ""
    if theo_yeu_cau:
        dong_theo_yeu_cau = (f"\nGọi theo yêu cầu hoặc có điều kiện — KHÔNG tự quét định kỳ: {len(theo_yeu_cau)} "
                             f"nguồn/công cụ — {'; '.join(_ten(s) for s in theo_yeu_cau)}.")
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
Đang giám sát tự động: {len(dinh_ky)} nguồn — {"; ".join(_ten(s) for s in dinh_ky)}; nhịp {nhip}.{dong_theo_yeu_cau}
{_dong_nhap_thu_cong(manual)}
KHÔNG phủ ({len(khong)} nhóm, khai rõ): {"; ".join(_ten(s) for s in khong)}.
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
    # `reports/` là thư mục dữ liệu NGOÀI git: bản sao trần (worktree tươi, phiên Cloud, CI) không có nó ⇒ trước
    # 30/09/2026 lệnh này sập FileNotFoundError ngay sau khi đã dựng xong khối (đo trong một worktree).
    ra.parent.mkdir(parents=True, exist_ok=True)
    ra.write_text("# " + khoi.replace("\n", "\n\n", 1) + "\n\n> Sinh tự động từ "
                  "data/sources.json — sửa SỔ, đừng sửa file này.\n", encoding="utf-8")
    print(khoi)
    print(f"\n→ {ra.relative_to(GOC)} (dán khối này vào bản đọc/queue/báo cáo tháng)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
