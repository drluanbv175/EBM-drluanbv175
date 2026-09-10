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

_FLAGS_PATH = Path(__file__).resolve().parents[1] / "clinical_runtime" / "CLINICAL_RUNTIME_FLAGS.json"


def _require_human_approval_flag() -> bool:
    """Đọc cờ `require_human_approval` — thiếu file/lỗi đọc thì MẶC ĐỊNH True
    (fail-closed): validator I4 không được vì thiếu cờ mà nới lỏng luật.

    VÌ SAO THÊM (10/09/2026): I4 vốn thi hành CỨNG, không đọc cờ này — nghĩa
    là `CLINICAL_RUNTIME_FLAGS.json.require_human_approval` chỉ là lời hứa
    suông (đúng họ lỗi 'cờ nói dối' đã vá ở nơi khác trong repo). Nối đọc thật
    vào đây; giá trị hiện tại là true nên HÀNH VI KHÔNG ĐỔI — chỉ khi bác sĩ
    tự đặt false thì I4 mới thật sự lùi thành khuyến nghị.
    """
    try:
        return bool(json.loads(_FLAGS_PATH.read_text(encoding="utf-8")).get("require_human_approval", True))
    except (OSError, ValueError, json.JSONDecodeError):
        return True


def kiem(item: dict, *, require_human_approval: bool | None = None) -> list[str]:
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
    if st not in ("UNRESOLVED", "NEW", None) and not (src.get("pmid") or src.get("doi")
                                                       or src.get("alt_id")):
        loi.append(f"status={st} nhưng KHÔNG có PMID/DOI/alt_id — chưa truy nguyên thì chưa qua NEW (I1)")
    if st in ("CANDIDATE", "APPROVED", "APPLIED") and src.get("resolved") is not True:
        loi.append(f"status={st} nhưng source.resolved != true — nhảy cóc qua truy nguyên (cấm #2)")
    if src.get("retracted") is True and st in ("CANDIDATE", "APPROVED", "APPLIED"):
        loi.append(f"source.retracted=true mà status={st} — điều kiện dừng khẩn (cấm #3)")

    # I4 — MÁY KHÔNG ĐƯỢC ĐẶT APPROVED/APPLIED: hai trạng thái này đòi người duyệt thật.
    doi_hoi_duyet = (require_human_approval if require_human_approval is not None
                     else _require_human_approval_flag())
    if st in ("APPROVED", "APPLIED") and doi_hoi_duyet:
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
    # LÔ H PHA 4 (15/08/2026) — checklist trích số cho mức ẢNH HƯỞNG TRỰC TIẾP:
    # item APPLY mang hiệu số phải khai kết cục chính/phụ + vị trí trong nguồn
    # (để đối chiếu ngược được). Chỉ áp cho apply — thẻ cũ/consider không bị
    # chặn oan bởi trường ra đời sau chúng (đúng bài học provenanceUnknown).
    if item.get("decision") == "apply" and ef.get("point_estimate") is not None:
        if not ef.get("outcome_role"):
            loi.append("apply + hiệu số mà thiếu effect.outcome_role (chính/phụ?) — LÔ H 9.1")
        if not ef.get("source_location"):
            loi.append("apply + hiệu số mà thiếu effect.source_location (bảng/hình nào?) "
                       "— không đối chiếu ngược được (LÔ H 9.1)")

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
        ("apply + hiệu số thiếu checklist 9.1", {**tot, "decision": "apply",
         "effect": {"measure": "HR", "point_estimate": 0.8, "as_reported": True}}),
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
