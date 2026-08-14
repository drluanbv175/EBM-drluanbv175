#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SỨC KHOẺ LEDGER — chấm 1193 thẻ EBM_MASTER.json theo hợp đồng dữ liệu (LÔ 1 PHA 2).

Vì sao: `contracts/evidence-item.schema.json` mô tả HÌNH DẠNG MỚI cho gói đi qua
E0–E6, nhưng sổ cái thật mang hình dạng CŨ (evidence_cards) chưa từng được chấm
toàn bộ. Công cụ này trả lời "sổ đang khoẻ đến đâu" bằng luật đúc từ SỐ ĐO THẬT
ngày 15/08/2026 (phân bố decision/gradeLevel/định danh đã đo trước khi viết luật
— không bịa luật rồi ép dữ liệu theo).

Hai mức, KHÔNG gộp (bài học BH08 — «không biết» ≠ «có vấn đề»):
  CHẶN     — hỏng cấu trúc máy đọc được: id thiếu/trùng, decision/gradeLevel
             ngoài tập, không một định danh nào truy nguyên được.
  BÁO CÁO  — cần bác sĩ để mắt nhưng KHÔNG phải lỗi máy tự kết luận được:
             apply trên low/vlow/na (ledger KHÔNG mang normativeBasis nên máy
             không phân biệt được nhãn-thuốc-FDA với chứng cứ yếu — đúng chỗ
             từng chặn oan 12/08), thẻ chưa xác minh, thẻ chỉ có URL/NCT.

Chỉ ĐỌC — không sửa gì. Ra `reports/ledger-health.md`. Mã thoát: 0 sạch CHẶN,
1 có CHẶN, 2 không đọc được sổ. Thuần stdlib, chạy được python3 lẫn venv (BH05).
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

GOC = Path(__file__).resolve().parents[1]
LEDGER = GOC / "EBM_MASTER" / "EBM_MASTER.json"
BAO_CAO = GOC / "reports" / "ledger-health.md"

DECISION = {"apply", "consider", "notyet"}
GRADE = {"high", "mod", "low", "vlow", "na"}
# PII quét BẢO THỦ: email + số ĐT Việt Nam có tách nhóm. Cố ý KHÔNG quét chuỗi
# 8-12 chữ số trần — PMID (8 số) và NCT sẽ dương tính giả hàng loạt.
RE_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
RE_PHONE = re.compile(r"\b0\d{2,3}[ .\-]\d{3}[ .\-]\d{3,4}\b")


def dinh_danh(card: dict) -> str:
    """Phân loại khả năng truy nguyên: pmid-doi | url-nct | không."""
    src = card.get("source") or {}
    if src.get("pmid") or src.get("doi"):
        return "pmid-doi"
    refs = " ".join(str(r) for r in (card.get("references") or []))
    if "PMID:" in refs or "DOI:" in refs or "10." in refs:
        return "pmid-doi"
    if "URL:" in refs or "NCT" in refs or src.get("url"):
        return "url-nct"
    return "không"


def cham(cards: list[dict]) -> dict:
    chan: dict[str, list[str]] = {}
    bao_cao: dict[str, list[str]] = {}

    def ghi(kho: dict, luat: str, cid: str) -> None:
        kho.setdefault(luat, []).append(cid)

    da_thay: set[str] = set()
    for c in cards:
        cid = c.get("id") or "(thiếu id)"
        if not c.get("id"):
            ghi(chan, "V1 thiếu id", cid)
        elif cid in da_thay:
            ghi(chan, "V1 id trùng", cid)
        da_thay.add(cid)

        if c.get("decision") not in DECISION:
            ghi(chan, f"V2 decision lạ ({c.get('decision')!r})", cid)
        if c.get("gradeLevel") not in GRADE:
            ghi(chan, f"V3 gradeLevel lạ ({c.get('gradeLevel')!r})", cid)

        loai = dinh_danh(c)
        if loai == "không":
            ghi(chan, "V4 KHÔNG một định danh nào (pmid/doi/url/nct)", cid)
        elif loai == "url-nct":
            ghi(bao_cao, "V4b chỉ có URL/NCT (không PMID/DOI) — nguồn cơ quan, "
                         "bác sĩ nên biết", cid)

        # V5 — chỉ BÁO CÁO: ledger không mang normativeBasis nên máy không được
        # kết luận "apply trên na là sai" (nhãn thuốc FDA hợp lệ vẫn là na).
        if c.get("decision") == "apply" and c.get("gradeLevel") in {"low", "vlow"}:
            ghi(bao_cao, "V5 apply trên low/vlow — cần bác sĩ xem", cid)
        elif c.get("decision") == "apply" and c.get("gradeLevel") == "na":
            ghi(bao_cao, "V5b apply trên na (không phân hạng) — cần bác sĩ xem", cid)

        vs = str(c.get("verification_status") or "")
        if vs.startswith("chưa xác minh"):
            ghi(bao_cao, "V6 chưa xác minh nguồn", cid)

        goi = json.dumps(c, ensure_ascii=False)
        if RE_EMAIL.search(goi) or RE_PHONE.search(goi):
            ghi(chan, "V7 nghi PII (email/số ĐT)", cid)

    return {"chan": chan, "bao_cao": bao_cao}


def main() -> int:
    try:
        d = json.loads(LEDGER.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"🔴 Không đọc được ledger: {exc}")
        return 2
    cards = d.get("evidence_cards", [])
    kq = cham(cards)
    tong_chan = sum(len(v) for v in kq["chan"].values())

    dong = [f"# SỨC KHOẺ LEDGER — {date.today().isoformat()}", ""]
    dong += [f"- Tổng: **{len(cards)} thẻ** (+{len(d.get('quarantined_cards', []))} cách ly)",
             f"- Mức CHẶN: **{tong_chan}** · mức BÁO CÁO: "
             f"**{sum(len(v) for v in kq['bao_cao'].values())}**",
             f"- decision: {dict(Counter(c.get('decision') for c in cards))}",
             f"- gradeLevel: {dict(Counter(c.get('gradeLevel') for c in cards))}", ""]
    for tieu_de, kho in (("## 🔴 CHẶN (hỏng máy đọc được)", kq["chan"]),
                         ("## 🟠 BÁO CÁO (cần mắt bác sĩ, máy không kết luận)",
                          kq["bao_cao"])):
        dong.append(tieu_de)
        if not kho:
            dong.append("- (không có)")
        for luat, ids in sorted(kho.items()):
            vd = ", ".join(ids[:5]) + ("…" if len(ids) > 5 else "")
            dong.append(f"- **{luat}**: {len(ids)} thẻ — {vd}")
        dong.append("")
    dong.append("> Chỉ ĐỌC và BÁO — không công cụ nào tự đổi decision/gradeLevel "
                "(BH10). Cần bác sĩ kiểm chứng.")

    BAO_CAO.parent.mkdir(parents=True, exist_ok=True)
    BAO_CAO.write_text("\n".join(dong) + "\n", encoding="utf-8")
    print(f"{'🔴' if tong_chan else '🟢'} {len(cards)} thẻ — CHẶN {tong_chan} · "
          f"BÁO CÁO {sum(len(v) for v in kq['bao_cao'].values())} → {BAO_CAO.relative_to(GOC)}")
    for luat, ids in sorted(kq["chan"].items()):
        print(f"   ✗ {luat}: {len(ids)}")
    return 1 if tong_chan else 0


if __name__ == "__main__":
    raise SystemExit(main())
