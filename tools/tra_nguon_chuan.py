#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TRA NGUỒN CHUẨN — định tuyến authority-first cho một câu hỏi lâm sàng (19/08/2026).

VÌ SAO CÓ
=========
Bác sĩ 19/08: «cách Gemini/ChatGPT tìm các NGUỒN CHỨNG CỨ CHUẨN và tổng hợp cho
thực hành — chứ không phải vấn đề toàn văn». Chẩn đoán: hệ tìm PubMed-TRƯỚC nên
trả về bài nghiên cứu; guideline hiện hành của hiệp hội (ADA/ESC/KDIGO/GOLD…)
nằm trên trang của họ, PubMed tìm kém hoặc chậm chỉ mục. Chatbot thắng vì đi
THẲNG vào các trang đó.

Tool này là bước ĐẦU TIÊN của mọi lượt trả lời câu hỏi chủ đề: đọc danh bạ
`EBM-Dashboards/nguon_chuan/danh-ba-nguon-chuan.json` (chủ đề → tổ chức → hub
guideline → hệ phân mức nguyên bản), khớp từ khoá, trả về:
  · nguồn chuẩn phải đọc TRƯỚC KHI ra PubMed, kèm URL hub;
  · bản chụp đã có trong kho `guideline_snapshot/` (đọc ngay, khỏi ra mạng);
  · trạng thái kiểm-sống URL (máy thăm được / chặn máy → mở Browser hoặc tay).

--kiem-song: thăm từng URL (GET nhẹ, 15s) và GHI trạng thái + ngày vào danh bạ.
Trang chặn máy (403/timeout) là SỰ THẬT về hạ tầng, không phải nguồn chết —
in rõ «chặn máy — mở bằng Browser/tải tay», tuyệt đối không bỏ nguồn khỏi kết quả.

Dùng:  python3 tools/tra_nguon_chuan.py "quản lý CKD ở bệnh nhân ĐTĐ"
       python3 tools/tra_nguon_chuan.py --danh-sach
       python3 tools/tra_nguon_chuan.py --kiem-song [chủ-đề]
Mã thoát: 0 · 1 không khớp chủ đề nào (in danh sách để chọn tay).
Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import json
import sys
import unicodedata
import urllib.request
from datetime import date
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
DANH_BA = REPO / "EBM-Dashboards" / "nguon_chuan" / "danh-ba-nguon-chuan.json"
KHO_CHUP = REPO / "EBM-Dashboards" / "guideline_snapshot"


def _khong_dau(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s.lower())
                   if unicodedata.category(c) != "Mn").replace("đ", "d")


def _doc() -> dict:
    return json.loads(DANH_BA.read_text(encoding="utf-8"))


def _ban_chup_cua(url: str, khai_bao: str | None) -> list[str]:
    """Bản chụp trong kho khớp nguồn này (khai báo trong danh bạ hoặc theo sổ)."""
    ra = []
    if khai_bao and (KHO_CHUP / khai_bao).exists():
        ra.append(khai_bao)
    so = KHO_CHUP / "so-guideline.json"
    if so.exists():
        for m in json.loads(so.read_text(encoding="utf-8")):
            if m["url"] == url and m["file"] not in ra:
                ra.append(m["file"])
    return ra


def tim(cau_hoi: str) -> int:
    db = _doc()
    hoi = _khong_dau(cau_hoi)
    khop: list[tuple[str, dict]] = []
    for ma, cd in db["chu_de"].items():
        diem = sum(1 for tk in cd["tu_khoa"] if _khong_dau(tk) in hoi)
        if diem:
            khop.append((ma, cd, diem))
    if not khop:
        print(f"✗ Không khớp chủ đề nào trong danh bạ cho: «{cau_hoi}»")
        print("  Chủ đề hiện có: " + " · ".join(sorted(db["chu_de"])))
        print("  → dùng làn PubMed 3 tầng như cũ, VÀ cân nhắc thêm chủ đề mới vào danh bạ.")
        return 1
    khop.sort(key=lambda x: -x[2])
    print(f"NGUỒN CHUẨN cho «{cau_hoi}» — đọc TRƯỚC khi ra PubMed:\n")
    for ma, cd, _ in khop[:2]:
        print(f"■ Chủ đề [{ma}]")
        for ng in cd["nguon"]:
            ks = ng.get("kiem_song", {})
            tt = {"ok": "✓ máy thăm được", "chan": "⛔ chặn máy — mở Browser/tải tay",
                  "": "chưa kiểm sống"}.get(ks.get("trang_thai", ""), ks.get("trang_thai", ""))
            if ng.get("url"):
                url = ng["url"]
            elif ng.get("pmid"):
                url = f"https://pubmed.ncbi.nlm.nih.gov/{ng['pmid']}/"
            else:
                url = "(không có URL/PMID trong danh bạ — tra tay theo tên nguồn)"
            print(f"  • {ng['to_chuc']} — {ng['ten']}")
            print(f"    {url}")
            print(f"    hệ mức nguyên bản: {ng.get('he_muc', 'chưa rõ')} · {tt}"
                  + (f" ({ks.get('ngay', '')})" if ks.get("ngay") else ""))
            for bc in _ban_chup_cua(url, ng.get("ban_chup")):
                print(f"    📌 BẢN CHỤP SẴN TRONG KHO: guideline_snapshot/{bc} — đọc ngay")
            if ng.get("ghi_chu"):
                print(f"    ghi chú: {ng['ghi_chu']}")
        print()
    print("Luật dùng: trích MỨC NGUYÊN BẢN của tổ chức (COR/LoE, GRADE 1A-2D, A-D…),")
    print("kèm «bản chụp <ngày>» nếu đọc từ kho chụp. Cần bác sĩ kiểm chứng.")
    return 0


def kiem_song(loc: str | None) -> int:
    db = _doc()
    hom_nay = date.today().isoformat()
    for ma, cd in db["chu_de"].items():
        if loc and loc != ma:
            continue
        for ng in cd["nguon"]:
            url = ng.get("url") or (f"https://pubmed.ncbi.nlm.nih.gov/{ng['pmid']}/" if ng.get("pmid") else None)
            if not url:
                # Thiếu cả url lẫn pmid trong dữ liệu — đây là DỮ LIỆU CHƯA ĐỦ,
                # KHÁC "chặn máy" (host từ chối bot). Gộp chung sẽ đọc sai thành
                # "nguồn có URL nhưng bị chặn" trong khi thực ra chưa có gì để thăm.
                ng["kiem_song"] = {"trang_thai": "khong_co_url", "ngay": hom_nay}
                print(f"  ? {ng['to_chuc']:<18} thiếu cả url và pmid trong danh bạ — cần bổ sung tay")
                continue
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=15) as ph:
                    du = ph.read(2048)
                ng["kiem_song"] = {"trang_thai": "ok" if du else "chan", "ngay": hom_nay}
                print(f"  ✓ {ng['to_chuc']:<18} {url[:64]}")
            except Exception as exc:  # noqa: BLE001 — chặn máy là dữ kiện, không phải lỗi dừng
                ng["kiem_song"] = {"trang_thai": "chan", "ngay": hom_nay,
                                   "loi": type(exc).__name__}
                print(f"  ⛔ {ng['to_chuc']:<18} {type(exc).__name__} — mở Browser/tải tay")
    DANH_BA.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8",
                       newline="\n")
    print("\n✓ Đã ghi trạng thái kiểm-sống vào danh bạ. «Chặn máy» = hạ tầng chặn bot,")
    print("  KHÔNG suy ra nguồn hỏng — Browser pane/bác sĩ vẫn mở bình thường.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Định tuyến nguồn chuẩn authority-first")
    ap.add_argument("cau_hoi", nargs="?", help="câu hỏi/chủ đề lâm sàng")
    ap.add_argument("--danh-sach", action="store_true")
    ap.add_argument("--kiem-song", nargs="?", const="", metavar="CHỦ-ĐỀ",
                    help="thăm URL và ghi trạng thái (lọc theo mã chủ đề nếu truyền)")
    a = ap.parse_args()
    if a.kiem_song is not None:
        return kiem_song(a.kiem_song or None)
    if a.danh_sach:
        db = _doc()
        for ma, cd in sorted(db["chu_de"].items()):
            print(f"• {ma}: {len(cd['nguon'])} nguồn — {', '.join(n['to_chuc'] for n in cd['nguon'])}")
        return 0
    if not a.cau_hoi:
        print("✗ Truyền câu hỏi, hoặc --danh-sach / --kiem-song.")
        return 1
    return tim(a.cau_hoi)


if __name__ == "__main__":
    raise SystemExit(main())
