"""Hồi quy B5 (03/10/2026): sổ QA sống observability/APPRAISALS.jsonl không có dòng nào sau 07/2026 dù `tham-dinh-dau-ra` vẫn
được gọi (chỉ chế độ AUTO-DISPATCH mới chạy run_eval), và 6/17 dòng của orchestrator-live có `ts` RỖNG."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from tools.orchestrator import guardrail_bridge as gb

ROOT = Path(__file__).resolve().parents[3]


def test_emit_appraisal_khong_truyen_at_van_co_dau_thoi_gian(tmp_path):
    rec = gb.emit_appraisal({"verdict": "ĐẠT", "score": "10/10"}, "orchestrator-live-output", source="orchestrator-live",
                            log_path=tmp_path / "A.jsonl")
    assert rec["ts"] and datetime.fromisoformat(rec["ts"]).tzinfo is not None
    assert json.loads((tmp_path / "A.jsonl").read_text(encoding="utf-8"))["ts"] == rec["ts"]


def test_emit_appraisal_co_at_giu_nguyen_de_tai_lap(tmp_path):
    a = gb.emit_appraisal({"verdict": "ĐẠT"}, "x", at="2026-10-03T00:00:00+00:00", log_path=tmp_path / "A.jsonl")
    b = gb.emit_appraisal({"verdict": "ĐẠT"}, "x", at="2026-10-03T00:00:00+00:00", log_path=tmp_path / "B.jsonl")
    assert a["ts"] == "2026-10-03T00:00:00+00:00" and a["id"] == b["id"]


def test_doctrine_tham_dinh_dau_ra_bat_buoc_ghi_bien_nhan():
    s = (ROOT / ".claude" / "agents" / "tham-dinh-dau-ra.md").read_text(encoding="utf-8")
    assert "## 6bis. GHI BIÊN NHẬN" in s and "run_eval.py <tệp> --json --source tham-dinh-dau-ra" in s
    assert "BIÊN NHẬN MÁY:" in s.split("## 4. Mẫu đầu ra", 1)[1].split("## 5.", 1)[0], "mẫu đầu ra phải có dòng biên nhận"
    assert "KHÔNG bịa mã" in s
