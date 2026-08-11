#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nhắc khi GIÁM SÁT CHỨNG CỨ quá hạn — thay cho lịch launchd vốn không nổ.

VÌ SAO CÓ (11/08/2026):
Hai job launchd `com.medicalebm.weeklysafety` (thứ Bảy 19:00) và
`com.medicalebm.monthlyupdate` (mùng 1, 18:00) khi kiểm thực tế đều cho
`runs = 0` · `last exit code = (never exited)`, log 0 byte từ 06/06 — tức
**chưa từng chạy một lần nào** kể từ khi cài (11/07). Từ đó tới nay đã lỡ 5 thứ
Bảy và 1 mùng 1.

Nguyên nhân: `StartCalendarInterval` của launchd đòi máy phải ĐANG THỨC đúng
thời điểm. MacBook đóng nắp lúc 19:00 thứ Bảy thì job không chạy, và launchd
không bù lại một cách đáng tin.

Máy móc bên dưới KHÔNG hỏng — chạy `weekly_safety.sh --canary` ngày 11/08 cho
PASS toàn bộ: 4/4 nguồn khoẻ (PubMed · Europe PMC · Crossref · openFDA),
scanner tìm được ứng viên, cổng dashboard strict PASS. Chỉ là không ai bật.

Nên cách vá hợp thói quen bác sĩ nhất: bác sĩ mở phiên Claude gần như mỗi ngày,
vậy NHẮC ngay lúc mở phiên. Không phụ thuộc máy có thức lúc 19:00 hay không.

Công cụ này CHỈ NHẮC, không tự chạy giám sát: quét chứng cứ là việc gọi mạng và
sinh nội dung y khoa, phải do bác sĩ chủ động và duyệt kết quả.

Dùng:
    python3 tools/kiem_do_tuoi_chung_cu.py            # in trạng thái
    python3 tools/kiem_do_tuoi_chung_cu.py --im-khi-on  # chỉ nói khi quá hạn (hook)

Mã thoát: 0 = còn hạn · 1 = quá hạn.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]
DASH = REPO / "EBM-Dashboards"
LOG_TUAN = REPO / "medical-ebm-automation/data/archive/launchd_weekly.log"
LOG_THANG = REPO / "medical-ebm-automation/data/archive/launchd_monthly.log"

# Ngưỡng nới hơn chu kỳ danh nghĩa: job tuần trễ 3 ngày chưa đáng gọi là bỏ bê.
HAN_AN_TOAN_NGAY = 10      # giám sát an toàn thuốc: chu kỳ tuần
HAN_CAP_NHAT_NGAY = 35     # cập nhật guideline: chu kỳ tháng


def ngay_tu_ten(p: Path) -> dt.date | None:
    """Lấy ngày từ đuôi tên file `..._YYYYMMDD.html` — đáng tin hơn mtime, vì
    mtime bị OneDrive và các lần dựng lại vỏ (reskin) làm nhiễu."""
    m = re.search(r"_(\d{8})\.html$", p.name)
    if not m:
        return None
    try:
        return dt.datetime.strptime(m.group(1), "%Y%m%d").date()
    except ValueError:
        return None


def lan_chay_cuoi(log: Path) -> dt.date | None:
    if log.exists() and log.stat().st_size > 0:
        return dt.date.fromtimestamp(log.stat().st_mtime)
    return None


def launchd_runs(nhan: str) -> int | None:
    """Số lần job launchd đã chạy — CHỈ macOS mới có launchd.

    Trên Windows trả None (không phải lỗi): ở đó không có lịch nền nào để hỏi,
    nhưng chốt này vẫn nhắc được theo dấu vết log và ngày gói chứng cứ.

    VÁ 12/08/2026: bản cũ gọi `os.getuid()` — hàm KHÔNG tồn tại trên Windows —
    và chỉ bắt (OSError, SubprocessError), nên AttributeError lọt ra ngoài làm
    CHẾT cả công cụ. Vì hook SessionStart kết thúc bằng `; true`, lỗi bị nuốt
    IM LẶNG: suốt thời gian qua máy Windows không hề được nhắc độ tươi chứng cứ
    mà không ai biết. Đây đúng lớp lỗi "công cụ dùng chung gãy im lặng trên
    Windows" đã gặp nhiều lần — nên bắt Exception rộng, không đoán trước tên lỗi.
    """
    if sys.platform != "darwin":
        return None
    import os

    try:
        r = subprocess.run(["launchctl", "print", f"gui/{os.getuid()}/{nhan}"],
                           capture_output=True, text=True, timeout=10)
        m = re.search(r"runs = (\d+)", r.stdout)
        return int(m.group(1)) if m else None
    except Exception:  # noqa: BLE001 — chốt nhắc không được phép làm chết phiên
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Nhắc khi giám sát chứng cứ quá hạn")
    ap.add_argument("--im-khi-on", action="store_true",
                    help="không in gì khi còn hạn (dùng cho hook)")
    a = ap.parse_args()

    hom_nay = dt.date.today()
    canh_bao: list[str] = []

    # 1) Gói chứng cứ mới nhất — thước đo trực tiếp nhất của "hệ có đang sống không"
    ngays = [d for d in (ngay_tu_ten(p) for p in DASH.glob("WebDashboard_*.html")) if d]
    mới_nhất = max(ngays) if ngays else None
    if mới_nhất:
        cach = (hom_nay - mới_nhất).days
        if cach > HAN_CAP_NHAT_NGAY:
            canh_bao.append(
                f"Gói chứng cứ mới nhất là {mới_nhất:%d/%m/%Y} — cách đây {cach} ngày "
                f"(ngưỡng {HAN_CAP_NHAT_NGAY}). Chạy `/cap-nhat-chung-cu <vấn đề>` "
                f"cho chủ đề đang cần.")

    # 2) Giám sát an toàn thuốc hằng tuần
    chay_tuan = lan_chay_cuoi(LOG_TUAN)
    runs = launchd_runs("com.medicalebm.weeklysafety")
    if chay_tuan is None:
        if sys.platform == "darwin":
            n = "" if runs is None else f" (launchd runs = {runs})"
            ly_do = (f"{n}. Lịch launchd đòi máy thức lúc 19:00 thứ Bảy nên hay lỡ")
        else:
            # Windows KHÔNG có launchd — hai job com.medicalebm.* chỉ tồn tại trên Mac.
            # Nói rõ điều này, thay vì để bác sĩ tưởng có lịch nền đang chạy hộ.
            ly_do = (". Máy này (Windows) KHÔNG có lịch nền nào chạy giám sát — "
                     "hai job launchd chỉ tồn tại trên MacBook, nên ở đây luôn phải chạy tay")
        canh_bao.append(
            f"Giám sát AN TOÀN THUỐC hằng tuần CHƯA TỪNG chạy{ly_do}. Chạy tay khi tiện:\n"
            f"     bash medical-ebm-automation/scripts/weekly_safety.sh\n"
            f"     (kiểm nhanh nguồn, không ghi gì: thêm `--canary`)")
    else:
        cach = (hom_nay - chay_tuan).days
        if cach > HAN_AN_TOAN_NGAY:
            canh_bao.append(
                f"Giám sát an toàn thuốc chạy lần cuối {chay_tuan:%d/%m/%Y} — "
                f"cách đây {cach} ngày (ngưỡng {HAN_AN_TOAN_NGAY}).")

    if not canh_bao:
        if not a.im_khi_on:
            print(f"🟢 CHỨNG CỨ còn hạn — gói mới nhất {mới_nhất:%d/%m/%Y}"
                  if mới_nhất else "🟢 CHỨNG CỨ còn hạn")
        return 0

    if a.im_khi_on:
        print("")
    print("🟡 GIÁM SÁT CHỨNG CỨ QUÁ HẠN")
    for c in canh_bao:
        print(f"   • {c}")
    print("   (Chốt này chỉ NHẮC — quét chứng cứ phải do bác sĩ chủ động và duyệt kết quả.)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
