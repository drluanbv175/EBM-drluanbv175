"""Hồi quy #33 (26/09/2026): cổng approved_for_use không được xanh giả vì chữ hoa,
khoảng trắng, trường vắng/None hay giá trị ngoài enum OUTPUT_SCHEMA.

Trước bản vá: grade_level 'Low'/' low'/vắng, decision 'Apply' (kèm grade low),
source_status 'Retracted'/None đều PASS mã 0 qua `evaluate_packet` — đúng ca cổng được
thiết kế để chặn. Test chạy ngoại tuyến, chỉ dùng fixture synthetic của chính verifier.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_clinical_practice_apply_gate as V  # noqa: E402

_VANG = V._VANG


def _goi(**thay: object) -> dict:
    """approved_fixture() với evidence_basis[0] bị thay/xoá trường theo `thay`."""
    pkt = V.approved_fixture()
    muc = pkt["evidence_basis"][0]
    for truong, gia_tri in thay.items():
        if gia_tri is _VANG:
            muc.pop(truong, None)
        else:
            muc[truong] = gia_tri
    return pkt


@pytest.mark.parametrize(
    "thay",
    [
        {"grade_level": "Low"},
        {"grade_level": " low"},
        {"grade_level": "LOW"},
        {"grade_level": "VLOW"},
        {"grade_level": "NA"},
        {"grade_level": _VANG},
        {"grade_level": None},
        {"grade_level": ""},
        {"grade_level": "xyz"},
        {"grade_level": "very low"},
        {"grade_level": 3},
        {"decision": "Apply", "grade_level": "low"},
        {"decision": " APPLY ", "grade_level": "vlow"},
        {"decision": _VANG},
        {"decision": "xyz"},
        {"source_status": "Retracted"},
        {"source_status": "RETRACTED"},
        {"source_status": " retracted "},
        {"source_status": "Quarantined"},
        {"source_status": None},
        {"source_status": ""},
        {"source_status": "xyz"},
    ],
    ids=lambda t: ",".join(f"{k}={'<vang>' if v is _VANG else repr(v)}" for k, v in t.items()),
)
def test_approved_chan_moi_bien_the_lach(thay):
    ket = V.evaluate_packet(_goi(**thay))
    assert ket["status"] == "FAIL", ket


def test_grade_chu_hoa_bi_chan_boi_luat_apply_yeu_sau_chuan_hoa():
    """'Low' phải bị bắt bởi CHÍNH luật apply-yếu (sau chuẩn hoá), không chỉ nhánh enum."""
    ket = V.evaluate_packet(_goi(grade_level="Low"))
    assert any("decision='apply' với grade_level='low'" in e for e in ket["errors"]), ket


def test_source_status_none_ve_unknown_va_bi_chan():
    ket = V.evaluate_packet(_goi(source_status=None))
    assert any("source_status='unknown'" in e for e in ket["errors"]), ket


def test_source_status_chu_hoa_bi_chan_nhu_retracted():
    ket = V.evaluate_packet(_goi(source_status="Retracted"))
    assert any("source_status='retracted'" in e for e in ket["errors"]), ket


def test_grade_vang_bi_chan_boi_nhanh_enum():
    ket = V.evaluate_packet(_goi(grade_level=_VANG))
    assert any("grade_level=None vắng hoặc ngoài enum" in e for e in ket["errors"]), ket


def test_chu_hoa_hop_le_van_pass_khong_do_gia():
    """Chuẩn hoá chỉ gỡ chữ hoa/khoảng trắng: 'Mod'/'Apply'/'Active' hợp lệ vẫn PASS."""
    ket = V.evaluate_packet(_goi(grade_level=" Mod ", decision="Apply", source_status="Active"))
    assert ket["status"] == "PASS", ket


def test_fixture_chuan_van_pass():
    ket = V.evaluate_packet(V.approved_fixture())
    assert ket == {"status": "PASS", "errors": [], "warnings": []}


def test_release_state_chu_hoa_van_chiu_du_luat_approved():
    """'Approved_For_Use' không được rơi vào nhánh 'không actionable' rồi PASS."""
    pkt = _goi(grade_level="low")
    pkt["release_state"] = "Approved_For_Use"
    ket = V.evaluate_packet(pkt)
    assert ket["status"] == "FAIL", ket
    assert any("decision='apply'" in e for e in ket["errors"]), ket


def test_release_state_ngoai_enum_bi_chan():
    pkt = V.approved_fixture()
    pkt["release_state"] = "approved"
    ket = V.evaluate_packet(pkt)
    assert ket["status"] == "FAIL", ket
    assert any("ngoài enum OUTPUT_SCHEMA" in e for e in ket["errors"]), ket


def test_goi_khong_actionable_hop_le_khong_bi_do_gia():
    """Gói doctor_review_required hợp lệ vẫn PASS kèm cảnh báo (không đổi hành vi cũ)."""
    pkt = copy.deepcopy(V.approved_fixture())
    pkt["release_state"] = "doctor_review_required"
    pkt["evidence_basis"][0]["grade_level"] = "Low"
    ket = V.evaluate_packet(pkt)
    assert ket["status"] == "PASS", ket


def test_run_verification_co_check_tu_kiem_enum_va_pass():
    rep = V.run_verification()
    theo_ten = {c["name"]: c for c in rep["checks"]}
    assert theo_ten["blocks_enum_bypass"]["status"] == "PASS", theo_ten["blocks_enum_bypass"]
    assert rep["overall_status"] == "PASS"


def test_enum_verifier_khop_output_schema_song():
    schema = json.loads((V.CLINICAL_RUNTIME / "OUTPUT_SCHEMA.json").read_text(encoding="utf-8"))
    assert V._enum_drift_errors(schema) == []


def test_enum_schema_lech_hoac_vang_bi_bao_loi():
    schema = json.loads((V.CLINICAL_RUNTIME / "OUTPUT_SCHEMA.json").read_text(encoding="utf-8"))
    lech = copy.deepcopy(schema)
    lech["properties"]["evidence_basis"]["items"]["properties"]["grade_level"]["enum"].append("moderate")
    assert any("grade_level lệch" in e for e in V._enum_drift_errors(lech))
    vang = copy.deepcopy(schema)
    del vang["properties"]["release_state"]["enum"]
    assert any("cho release_state" in e and "thiếu enum" in e for e in V._enum_drift_errors(vang))
    assert V._enum_drift_errors({}) != []


def test_check_contract_files_noi_day_doi_chieu_enum(monkeypatch):
    """Lệch enum giữa verifier và schema sống phải làm contract_files FAIL (đã nối dây)."""
    assert V.check_contract_files()["status"] == "PASS"
    monkeypatch.setattr(V, "VALID_GRADES", {"high", "mod", "low", "vlow"})
    ket = V.check_contract_files()
    assert ket["status"] == "FAIL", ket
    assert any("grade_level lệch OUTPUT_SCHEMA" in e for e in ket["errors"]), ket
