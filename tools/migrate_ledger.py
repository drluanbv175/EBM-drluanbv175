#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DI TRÚ LEDGER sang hợp đồng mới — MẶC ĐỊNH DRY-RUN, chỉ ghi khi bác sĩ duyệt.

Ánh xạ thẻ cũ (`evidence_cards`) → item theo `contracts/evidence-item.schema.json`;
mọi trường không ánh xạ được giữ NGUYÊN VẸN trong `legacy_raw` — không mất một
byte thông tin nào của bản cũ.

BA LUẬT AN TOÀN, cái nào cũng có lý do bằng máu:
1. KHÔNG BAO GIỜ mint APPROVED/APPLIED (I4): thẻ cũ không mang bằng chứng
   human_review máy đọc được, nên trạng thái cao nhất sau di trú là VERIFIED.
   Nâng lên APPROVED là việc của bác sĩ, hàng loạt hay từng thẻ đều được —
   nhưng phải là chữ ký của người, không phải suy diễn của máy.
2. `certainty.reported_by_source` để null (KHÔNG BIẾT ai chấm gradeLevel cũ —
   BH36) chứ không đặt bừa True/False; bài học «không biết ≠ có vấn đề» (BH08)
   và «không tự gán mức» (I2) gặp nhau ở đúng chỗ này.
3. `--ap-dung` ghi ra FILE MỚI `EBM_MASTER.v2.json` — không đè bản cũ; bản cũ
   vẫn là nguồn sự thật cho tới khi bác sĩ tuyên bố chuyển.

Dùng:  python3 tools/migrate_ledger.py            # dry-run, in thống kê + diff mẫu
       python3 tools/migrate_ledger.py --ap-dung  # CHỈ chạy sau khi bác sĩ duyệt
Thuần stdlib; tự nạp validator hợp đồng `tools/kiem_hop_dong_item.py` để chấm
từng item SAU ánh xạ — di trú mà không chấm lại là di trú mù.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

GOC = Path(__file__).resolve().parents[1]
LEDGER = GOC / "EBM_MASTER" / "EBM_MASTER.json"
DICH = GOC / "EBM_MASTER" / "EBM_MASTER.v2.json"


def _nap_validator():
    duong = GOC / "tools" / "kiem_hop_dong_item.py"
    spec = importlib.util.spec_from_file_location("kiem_hop_dong_item", duong)
    m = importlib.util.module_from_spec(spec)
    sys.modules["kiem_hop_dong_item"] = m
    try:
        spec.loader.exec_module(m)
    except BaseException:
        sys.modules.pop("kiem_hop_dong_item", None)
        raise
    return m


def anh_xa(card: dict) -> dict:
    """Thẻ cũ → item hợp đồng mới. Trường lạ nằm nguyên trong legacy_raw."""
    src = card.get("source") or {}
    vs = str(card.get("verification_status") or "")
    da_xac_minh = vs.startswith("đã xác minh")
    item = {
        "id": card.get("id"),
        "topic": card.get("topic") or card.get("specialty") or "",
        # Luật an toàn 1: trần là VERIFIED — không suy diễn phê duyệt của người.
        "status": "VERIFIED" if da_xac_minh else "NEW",
        "decision": card.get("decision"),
        "source": {
            "type": src.get("type") or "",
            "title": src.get("title") or "",
            "pmid": src.get("pmid") or None,
            "doi": src.get("doi") or None,
            "url": src.get("url") or None,
            "resolved": True if da_xac_minh else None,
        },
        "certainty": {
            # Luật an toàn 2: null = chưa biết ai chấm (BH36/BH08), không bịa.
            "reported_by_source": None,
            "level": card.get("gradeLevel"),
        },
        "human_review": None,
        "legacy_raw": card,
    }
    return item


def main() -> int:
    ap = argparse.ArgumentParser(description="Di trú ledger sang hợp đồng mới")
    ap.add_argument("--ap-dung", action="store_true",
                    help="ghi thật ra EBM_MASTER.v2.json (CHỈ sau khi bác sĩ duyệt diff)")
    a = ap.parse_args()

    d = json.loads(LEDGER.read_text(encoding="utf-8"))
    cards = d.get("evidence_cards", [])
    kiem = _nap_validator().kiem

    items, loi_theo_loai = [], Counter()
    hong: list[tuple[str, list[str]]] = []
    for c in cards:
        it = anh_xa(c)
        vi_pham = kiem(it)
        if vi_pham:
            hong.append((it.get("id") or "?", vi_pham))
            for v in vi_pham:
                loi_theo_loai[v.split("—")[0].strip()[:60]] += 1
        items.append(it)

    print(f"DI TRÚ {'THẬT' if a.ap_dung else 'DRY-RUN (chưa ghi gì)'} — "
          f"{len(cards)} thẻ cũ → {len(items)} item mới")
    print(f"  Hợp đồng mới: {len(items) - len(hong)} đạt · {len(hong)} vi phạm")
    for loai, n in loi_theo_loai.most_common(8):
        print(f"    ✗ {loai}: {n}")
    print(f"  Trạng thái sau di trú: "
          f"{dict(Counter(i['status'] for i in items))} "
          f"(KHÔNG thẻ nào được mint APPROVED/APPLIED — I4)")

    # Diff mẫu 1 thẻ để bác sĩ thấy đúng thứ sẽ xảy ra, không phải mô tả suông.
    print("\n── DIFF MẪU (thẻ đầu tiên) ──")
    goc0 = {k: v for k, v in cards[0].items() if k in
            ("id", "decision", "gradeLevel", "verification_status")}
    moi0 = {k: v for k, v in items[0].items() if k != "legacy_raw"}
    print("  TRƯỚC:", json.dumps(goc0, ensure_ascii=False))
    print("  SAU  :", json.dumps(moi0, ensure_ascii=False)[:400])
    print("  (toàn bộ thẻ cũ nằm nguyên trong legacy_raw — không mất gì)")

    if not a.ap_dung:
        print("\n⏸ CHƯA GHI GÌ. Bác sĩ duyệt con số + diff trên rồi chạy lại với "
              "--ap-dung; khi đó ghi ra EBM_MASTER.v2.json (KHÔNG đè bản cũ).")
        return 0
    DICH.write_text(json.dumps({
        "meta": {**d.get("meta", {}), "contract": "contracts/evidence-item.schema.json",
                 "di_tru_tu": str(LEDGER.name)},
        "items": items,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n✓ Đã ghi {DICH.relative_to(GOC)} ({len(items)} item). Bản cũ giữ nguyên.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
