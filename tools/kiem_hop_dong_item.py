#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VALIDATOR hợp đồng mục chứng cứ — thi hành máy trạng thái, thuần stdlib.

Vì sao tự viết thay vì jsonschema: venv này không có thư viện đó, và bộ luật cần thi
hành là NGỮ NGHĨA (máy không được đặt APPROVED, không tự gán mức…) chứ không chỉ hình
dạng JSON. Luật lấy từ `contracts/evidence-item.schema.json` + `state-machine.md`.

Dùng:
    python tools/kiem_hop_dong_item.py --file item.json
    python tools/kiem_hop_dong_item.py --self-test     # canary/BH46 gọi

Mã thoát: 0 = hợp lệ · 1 = vi phạm (in từng vi phạm).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

STATUS = {"NEW", "VERIFIED", "APPRAISED", "CANDIDATE", "APPROVED", "APPLIED",
          "DROPPED", "UNRESOLVED"}
DECISION = {"apply", "consider", "notyet"}
CERTAINTY = {"high", "mod", "low", "vlow", "na"}
BASIS = {"contraindication", "drug-label", "official-classification",
         "guideline-strong-rec", "guideline-explicit-criteria", None}


def kiem(item: dict) -> list[str]:
    """Trả danh sách vi phạm — rỗng nghĩa là hợp lệ."""
    loi: list[str] = []
    for k in ("id", "topic", "source", "status", "decision"):
        if not item.get(k):
            loi.append(f"thiếu trường bắt buộc `{k}`")
    st = item.get("status")
    if st and st not in STATUS:
        loi.append(f"status={st!r} ngoài máy trạng thái")
    if item.get("decision") and item["decision"] not in DECISION:
        loi.append(f"decision={item['decision']!r} không hợp lệ")

    src = item.get("source") or {}
    if st not in ("UNRESOLVED", "NEW", None) and not (src.get("pmid") or src.get("doi")):
        loi.append(f"status={st} nhưng KHÔNG có PMID/DOI — chưa truy nguyên thì chưa qua NEW (I1)")
    if st in ("CANDIDATE", "APPROVED", "APPLIED") and src.get("resolved") is not True:
        loi.append(f"status={st} nhưng source.resolved != true — nhảy cóc qua truy nguyên (cấm #2)")
    if src.get("retracted") is True and st in ("CANDIDATE", "APPROVED", "APPLIED"):
        loi.append(f"source.retracted=true mà status={st} — điều kiện dừng khẩn (cấm #3)")

    # I4 — MÁY KHÔNG ĐƯỢC ĐẶT APPROVED/APPLIED: hai trạng thái này đòi người duyệt thật.
    if st in ("APPROVED", "APPLIED"):
        hr = item.get("human_review") or {}
        if not hr.get("reviewed_by"):
            loi.append(f"status={st} mà human_review.reviewed_by rỗng — chỉ bác sĩ được đặt (I4)")

    # I2/BH36 — không tự gán mức
    ct = item.get("certainty") or {}
    if ct.get("reported_by_source") is False and ct.get("level") not in ("na", None):
        loi.append(f"certainty: nguồn KHÔNG chấm mà level={ct.get('level')!r} — tự gán mức (I2)")
    if ct.get("level") and ct["level"] not in CERTAINTY:
        loi.append(f"certainty.level={ct['level']!r} không hợp lệ")

    sr = item.get("source_recommendation") or {}
    if sr.get("normativeBasis") not in BASIS:
        loi.append(f"normativeBasis={sr.get('normativeBasis')!r} không hợp lệ")

    ef = item.get("effect") or {}
    if ef and (ef.get("point_estimate") is not None) and ef.get("as_reported") is not True \
            and not ef.get("derivation"):
        loi.append("effect có số mà as_reported≠true và KHÔNG ghi derivation — số ở đâu ra? (I1)")

    oa = item.get("operational_assessment") or {}
    if oa and oa.get("label") != "đánh giá vận hành — không phải phân hạng của nguồn":
        loi.append("operational_assessment thiếu nhãn bắt buộc — lớp 3 phải tự xưng danh (I3)")
    return loi


def _self_test() -> int:
    tot = {"id": "EBM-2026-0001", "topic": "t", "status": "CANDIDATE", "decision": "consider",
           "source": {"type": "SR-MA", "title": "x", "year": 2026, "pmid": "123", "resolved": True},
           "certainty": {"reported_by_source": True, "level": "mod"}}
    ca_xau = [
        ("máy tự APPROVED", {**tot, "status": "APPROVED"}),
        ("retracted vẫn CANDIDATE", {**tot, "source": {**tot["source"], "retracted": True}}),
        ("tự gán mức", {**tot, "certainty": {"reported_by_source": False, "level": "high"}}),
        ("CANDIDATE chưa resolved", {**tot, "source": {**tot["source"], "resolved": False}}),
        ("số không nguồn gốc", {**tot, "effect": {"measure": "RR", "point_estimate": 0.8,
                                                  "as_reported": False}}),
    ]
    ok = not kiem(tot)
    hong = [(ten, kiem(it)) for ten, it in ca_xau]
    bat_het = all(v for _t, v in hong)
    print(f"item hợp lệ → {'PASS' if ok else 'FAIL SAI'}")
    for ten, v in hong:
        print(f"  ca xấu «{ten}» → {'BẮT ĐƯỢC' if v else '🔴 LỌT'}: {v[0] if v else ''}")
    return 0 if (ok and bat_het) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Validator hợp đồng mục chứng cứ")
    ap.add_argument("--file", help="file JSON chứa MỘT item hoặc mảng item")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return _self_test()
    if not a.file:
        ap.error("cần --file hoặc --self-test")
    du = json.loads(Path(a.file).read_text(encoding="utf-8"))
    ds = du if isinstance(du, list) else [du]
    tong = 0
    for i, it in enumerate(ds):
        for v in kiem(it):
            print(f"  ✗ [{it.get('id', f'#{i}')}] {v}")
            tong += 1
    print(f"{'🔴 ' + str(tong) + ' vi phạm' if tong else '🟢 Hợp lệ'} ({len(ds)} item)")
    return 1 if tong else 0


if __name__ == "__main__":
    raise SystemExit(main())
