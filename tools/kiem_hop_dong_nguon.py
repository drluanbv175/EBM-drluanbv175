#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VALIDATOR hợp đồng sổ đăng ký nguồn — thuần stdlib.

VÌ SAO CÓ (vòng 2, 10/09/2026): `contracts/sources.schema.json` ("Sổ đăng ký nguồn
— hợp đồng PHA 4 LÔ A") khai luật cho `data/sources.json`, và `data/sources.json`
là dữ liệu THẬT đang được duy trì (updated 09/09/2026, 19 nguồn) — nhưng TRƯỚC
công cụ này, **0 nơi nào trong repo đọc cả hai file cùng lúc để đối chiếu**. Đúng
họ lỗi "hợp đồng có, không ai thi hành" (cùng lớp với `kiem_hop_dong_item.py`
canh `contracts/evidence-item.schema.json`, xây từ 15/08 — sổ NGUỒN chưa từng có
bản song sinh). Chạy thử lần đầu bắt được NGAY một vi phạm thật: SRC-031
`scan_frequency="theo lượt quét A2"` — không khớp enum {daily,weekly,monthly,
quarterly,ad-hoc} của chính hợp đồng đã khai (đã sửa cùng đợt, xem
`data/sources.json`, giữ nguyên ngữ nghĩa "chạy theo A2" trong `known_gap`).

Vì sao tự viết thay vì jsonschema: cùng lý do `kiem_hop_dong_item.py` — venv
không có thư viện đó, và luật `id` trùng lặp là ngữ nghĩa (jsonschema draft
2020-12 không tự bắt trùng giá trị) chứ không chỉ hình dạng JSON.

Dùng:
    python tools/kiem_hop_dong_nguon.py
    python tools/kiem_hop_dong_nguon.py --self-test     # canary/BH101 gọi

Mã thoát: 0 = hợp lệ · 1 = vi phạm (in từng vi phạm) · 2 = thiếu file.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "data" / "sources.json"
SCHEMA = ROOT / "contracts" / "sources.schema.json"

ID_RE = re.compile(r"^SRC-\d{3}$")
TIER = {1, 2, 3}
ACCESS = {"api", "rss", "html-watch", "file", "manual", "none"}
SCAN_FREQ = {"daily", "weekly", "monthly", "quarterly", "ad-hoc"}
DETECTION = {"api-query", "feed-item", "content-hash", "version-field", "human"}
STATUS = {"active", "degraded", "broken", "not-covered"}
REQUIRED = ("id", "name", "org", "tier", "domain", "access",
            "scan_frequency", "detection_method", "owner", "status")


def kiem(data: dict) -> list[str]:
    """Trả danh sách vi phạm — rỗng nghĩa là hợp lệ."""
    loi: list[str] = []
    if "updated" not in data:
        loi.append("thiếu trường gốc `updated`")
    nguon = data.get("sources")
    if not isinstance(nguon, list):
        loi.append("`sources` không phải mảng — dừng, không kiểm được từng mục")
        return loi

    dem_id: dict[str, int] = {}
    for i, s in enumerate(nguon):
        if not isinstance(s, dict):
            loi.append(f"#{i}: mỗi nguồn phải là object")
            continue
        nhan = s.get("id") or f"#{i}"
        for k in REQUIRED:
            if k not in s:
                loi.append(f"{nhan}: thiếu trường bắt buộc `{k}`")

        sid = s.get("id")
        if sid is not None:
            if not isinstance(sid, str) or not ID_RE.match(sid):
                loi.append(f"{nhan}: id={sid!r} không khớp mẫu SRC-\\d{{3}}")
            dem_id[sid] = dem_id.get(sid, 0) + 1

        if "tier" in s and s["tier"] not in TIER:
            loi.append(f"{nhan}: tier={s.get('tier')!r} ngoài {{1,2,3}}")
        if "access" in s and s["access"] not in ACCESS:
            loi.append(f"{nhan}: access={s.get('access')!r} không hợp lệ")
        if "scan_frequency" in s and s["scan_frequency"] not in SCAN_FREQ:
            loi.append(f"{nhan}: scan_frequency={s.get('scan_frequency')!r} không hợp lệ")
        if "detection_method" in s and s["detection_method"] not in DETECTION:
            loi.append(f"{nhan}: detection_method={s.get('detection_method')!r} không hợp lệ")
        if "status" in s and s["status"] not in STATUS:
            loi.append(f"{nhan}: status={s.get('status')!r} không hợp lệ")
        if "domain" in s and not isinstance(s["domain"], list):
            loi.append(f"{nhan}: domain phải là mảng")

        eu = s.get("endpoint_or_url")
        if eu is not None and not isinstance(eu, str):
            loi.append(f"{nhan}: endpoint_or_url phải là chuỗi hoặc null")
        for k in ("auth_required", "terms_ok"):
            v = s.get(k)
            if v is not None and not isinstance(v, bool):
                loi.append(f"{nhan}: {k} phải là boolean hoặc null")
        ml = s.get("measured_latency_days")
        if ml is not None and not isinstance(ml, (int, float)):
            loi.append(f"{nhan}: measured_latency_days phải là số hoặc null")

        # P6 (chính schema tự khai): endpoint chưa xác minh → null, không bịa URL
        # kèm known_gap giải thích — cấm URL "để đó" không kèm lý do khi status
        # không phải active.
        if s.get("status") == "not-covered" and eu is not None and not s.get("known_gap"):
            loi.append(f"{nhan}: status=not-covered có endpoint nhưng thiếu known_gap "
                       "(P6 — vì sao chưa phủ phải nói rõ, không để URL đơn độc)")

    trung = sorted(sid for sid, n in dem_id.items() if n > 1)
    if trung:
        loi.append(f"id trùng lặp: {', '.join(trung)}")
    return loi


def _self_test() -> int:
    tot = {
        "updated": "2026-09-10",
        "sources": [
            {"id": "SRC-001", "name": "x", "org": "y", "tier": 1, "domain": ["d"],
             "access": "api", "scan_frequency": "weekly", "detection_method": "api-query",
             "owner": "agent-A2", "status": "active"},
        ],
    }
    ca_xau = [
        ("id sai mẫu", {**tot, "sources": [{**tot["sources"][0], "id": "SRC-1"}]}),
        ("scan_frequency ngoài enum", {**tot, "sources": [
            {**tot["sources"][0], "scan_frequency": "theo lượt quét A2"}]}),
        ("thiếu trường bắt buộc", {**tot, "sources": [{"id": "SRC-002"}]}),
        ("id trùng lặp", {**tot, "sources": [tot["sources"][0], tot["sources"][0]]}),
        ("not-covered có URL mà không giải thích", {**tot, "sources": [
            {**tot["sources"][0], "status": "not-covered",
             "endpoint_or_url": "https://x", "known_gap": None}]}),
    ]
    ok = not kiem(tot)
    hong = [(ten, kiem(it)) for ten, it in ca_xau]
    bat_het = all(v for _t, v in hong)
    print(f"sổ hợp lệ → {'PASS' if ok else 'FAIL SAI'}")
    for ten, v in hong:
        print(f"  ca xấu «{ten}» → {'BẮT ĐƯỢC' if v else '🔴 LỌT'}: {v[0] if v else ''}")
    return 0 if (ok and bat_het) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Validator hợp đồng sổ đăng ký nguồn")
    ap.add_argument("--file", help="file JSON thay cho data/sources.json mặc định")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return _self_test()

    duong = Path(a.file) if a.file else SOURCES
    if not duong.is_file():
        print(f"⚠ Không tìm thấy {duong} — chưa kiểm được, KHÔNG phải đã hợp lệ.")
        return 2
    data = json.loads(duong.read_text(encoding="utf-8"))
    vi_pham = kiem(data)
    for v in vi_pham:
        print(f"  ✗ {v}")
    n = len(data.get("sources", []))
    print(f"{'🔴 ' + str(len(vi_pham)) + ' vi phạm' if vi_pham else '🟢 Hợp lệ'} ({n} nguồn)")
    return 1 if vi_pham else 0


if __name__ == "__main__":
    raise SystemExit(main())
