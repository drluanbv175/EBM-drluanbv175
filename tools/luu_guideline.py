#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KHO BẢN CHỤP GUIDELINE — làn nguồn guideline có provenance (gói ②b, 19/08/2026).

VÌ SAO CÓ
=========
Bác sĩ 19/08: Gemini/ChatGPT «có vẻ tốt hơn» một phần vì chúng đọc web tự do nên
thấy guideline NICE/ADA/ESC bản mới nhất; hệ này cố ý giới hạn PubMed/PMC nên
tầng GUIDELINE — quan trọng nhất cho thực hành — bị mỏng. Làn này cho phép LƯU
BẢN CHỤP guideline lấy về hợp pháp (bản công khai miễn phí: KDIGO PDF, WHO,
USPSTF, bản HTML mở…) kèm provenance đầy đủ để trích được về sau.

MỖI BẢN CHỤP ghi vào sổ `so-guideline.json`: tổ chức · tiêu đề · URL nguồn ·
ngày chụp · SHA-256 · cỡ · định dạng. Trích dẫn từ bản chụp PHẢI kèm «bản chụp
<ngày>» — guideline đổi theo thời gian, bản chụp là ảnh tĩnh, không phải web sống.

KHÔNG cào nguồn trả phí/đăng nhập; trang chặn máy thì bác sĩ tải tay rồi nạp
bằng --file (provenance vẫn ghi URL gốc do bác sĩ khai).

Dùng:  python3 tools/luu_guideline.py --url <URL> --to-chuc KDIGO --tieu-de "..."
       python3 tools/luu_guideline.py --file <đã-tải.pdf> --url <URL-gốc> --to-chuc ... --tieu-de "..."
       python3 tools/luu_guideline.py --danh-sach
Mã thoát: 0 · 1 đối số thiếu · 2 tải thất bại/nội dung rỗng. Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
KHO = REPO / "EBM-Dashboards" / "guideline_snapshot"
SO = KHO / "so-guideline.json"


def _doc_so() -> list[dict]:
    if SO.exists():
        return json.loads(SO.read_text(encoding="utf-8"))
    return []


def _slug(s: str) -> str:
    s = re.sub(r"[^\w\s-]", "", s.lower()).strip()
    return re.sub(r"[\s_]+", "-", s)[:70]


def main() -> int:
    ap = argparse.ArgumentParser(description="Lưu bản chụp guideline có provenance")
    ap.add_argument("--url", help="URL nguồn (bắt buộc — provenance)")
    ap.add_argument("--file", help="file đã tải tay (bỏ qua bước tải mạng)")
    ap.add_argument("--to-chuc", help="tổ chức ban hành (KDIGO/WHO/NICE/ADA…)")
    ap.add_argument("--tieu-de", help="tiêu đề guideline")
    ap.add_argument("--nam", default="", help="năm ban hành (nếu biết)")
    ap.add_argument("--danh-sach", action="store_true", help="liệt kê kho bản chụp")
    a = ap.parse_args()

    if a.danh_sach:
        so = _doc_so()
        if not so:
            print("(kho bản chụp guideline đang rỗng)")
            return 0
        for m in so:
            print(f"• [{m['to_chuc']}] {m['tieu_de']} ({m.get('nam', '?')}) — "
                  f"chụp {m['ngay_chup']} · {m['dinh_dang']} · {m['kich_thuoc_kb']} KB\n"
                  f"  {m['file']} · sha256:{m['sha256'][:16]}… · nguồn: {m['url']}")
        return 0

    if not (a.url and a.to_chuc and a.tieu_de):
        print("✗ Cần --url --to-chuc --tieu-de (hoặc --danh-sach).")
        return 1
    if a.file:
        du_lieu = Path(a.file).read_bytes()
    else:
        try:
            req = urllib.request.Request(a.url, headers={"User-Agent": "Mozilla/5.0"})
            du_lieu = urllib.request.urlopen(req, timeout=60).read()
        except Exception as exc:  # noqa: BLE001
            print(f"🔴 Không tải được ({type(exc).__name__}) — trang có thể chặn máy; "
                  "bác sĩ tải tay rồi chạy lại với --file. KHÔNG lách tường phí.")
            return 2
    if len(du_lieu) < 10_000:
        print(f"🔴 Nội dung quá nhỏ ({len(du_lieu)} byte) — nhiều khả năng là trang "
              "chặn/chuyển hướng, KHÔNG phải guideline. Từ chối lưu.")
        return 2
    duoi = ".pdf" if du_lieu[:5] == b"%PDF-" else ".html"
    KHO.mkdir(parents=True, exist_ok=True)
    ten = f"{a.to_chuc}_{_slug(a.tieu_de)}_{date.today().isoformat()}{duoi}"
    (KHO / ten).write_bytes(du_lieu)
    so = _doc_so()
    so.append({"to_chuc": a.to_chuc, "tieu_de": a.tieu_de, "nam": a.nam,
               "url": a.url, "ngay_chup": date.today().isoformat(),
               "file": ten, "dinh_dang": duoi[1:].upper(),
               "kich_thuoc_kb": len(du_lieu) // 1024,
               "sha256": hashlib.sha256(du_lieu).hexdigest()})
    SO.write_text(json.dumps(so, ensure_ascii=False, indent=2), encoding="utf-8",
                  newline="\n")
    print(f"✓ {ten} ({len(du_lieu)//1024} KB) — đã ghi sổ provenance.")
    print("Trích dẫn từ bản này PHẢI kèm «bản chụp " + date.today().isoformat()
          + "». Cần bác sĩ kiểm chứng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
