from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_clinical_runtime_schema_hardening as V  # noqa: E402


def test_clinical_runtime_hardening_overall_passes():
    report = V.run_verification()

    assert report["overall_status"] == "PASS"
    assert {check["name"] for check in report["checks"]} == {
        "safety_rules",
        "output_schema",
        "decision_contract",
        "validation_cases",
        "runtime_flags",
        "cache_freshness",
        "outpatient_apply_gate",
    }


def test_safety_rules_cover_retraction_injection_and_conflicts():
    check = V.check_safety_rules()

    assert check["status"] == "PASS"
    assert check["missing_markers"] == []


def test_output_schema_requires_machine_readable_hardening_fields():
    check = V.check_output_schema()

    assert check["status"] == "PASS"
    assert check["missing_markers"] == []


def test_decision_contract_blocks_actionable_release_for_hardening_alerts():
    check = V.check_decision_contract()

    assert check["status"] == "PASS"
    assert check["missing_markers"] == []


def test_validation_cases_pin_expected_hardening_outputs():
    check = V.check_validation_cases()

    assert check["status"] == "PASS"
    assert check["missing_markers"] == {}


def test_validation_cases_covers_all_11_not_just_4():
    """10/09/2026: bản trước chỉ soi TC-007/008/010/011 (4/11) — 7 file còn lại
    không script nào kiểm dù README tự khai '10 (nay 11) DEMO_TEST... all must
    PASS'. Khoá số lượng để không tụt lại nếu ai rút bớt case_checks."""
    library = V.CLINICAL_RUNTIME / "VALIDATION_CASE_LIBRARY"
    so_file_that = len(list(library.glob("TC-*.json")))
    assert so_file_that == 11

    check = V.check_validation_cases()
    assert check["details"] == ["11 validation cases checked"]


def test_runtime_flags_reports_enforcement_site_for_every_true_flag():
    """10/09/2026: cờ TRUE mà không điểm thi hành nào đọc là cờ nói dối (họ lỗi
    BH94/BH98/BH61 vá ở nơi khác trong repo). Sau bản vá đi kèm
    (ensure_strict_source.py + kiem_hop_dong_item.py + kiem_safety_net.py đều
    đọc cờ thật), cả 3 cờ hiện có trong CLINICAL_RUNTIME_FLAGS.json phải có
    điểm thi hành — nếu ai gỡ một trong ba, test này đỏ trước khi CI đỏ."""
    check = V.check_runtime_flags()

    assert check["status"] == "PASS"
    assert check["missing_markers"] == []
    assert len(check["details"][0].split("->")) >= 2  # có ít nhất 1 cờ enforced


def test_cache_freshness_is_advisory_not_blocking():
    """10/09/2026 (vòng 3): 3 file cache trong clinical_runtime/ đã cũ 29-47
    ngày — check phải BÁO nhưng KHÔNG được chặn overall_status (bác sĩ mới
    biết ngưỡng nào hợp lý, không phải máy tự đoán)."""
    check = V.check_runtime_flags()
    assert check["status"] == "PASS"  # đối chứng: cờ vẫn PASS như cũ (không bị đụng)

    check2 = V.check_cache_freshness()
    assert check2["status"] == "ADVISORY"
    assert V.run_verification()["overall_status"] == "PASS"


def test_cache_freshness_doc_theo_noi_dung_khong_theo_mtime(tmp_path, monkeypatch):
    """BH76: 'Độ tươi phái sinh phải đo theo NỘI DUNG, không theo mtime'. Dựng
    file có mtime HÔM NAY nhưng trường `generated` bên trong ghi ngày CŨ — nếu
    check đọc mtime thay vì nội dung, nó sẽ báo sai '0 ngày trước'."""
    gia = tmp_path / "retraction_med_safety_report.json"
    gia.write_text(json.dumps({"generated": "2020-01-01T00:00:00Z"}), encoding="utf-8")
    # mtime của file vừa ghi luôn là "bây giờ" — đúng kịch bản worktree/clone mới.
    ket = V._ngay_that_cua_file(gia, "content:generated")
    assert ket is not None
    ngay, tuoi = ket
    assert ngay == "2020-01-01"
    assert tuoi > 2000  # nếu lỡ đọc mtime sẽ ra ~0, không phải hàng nghìn ngày


def test_outpatient_apply_gate_blocks_uncontrolled_practice_release():
    check = V.check_outpatient_apply_gate()

    assert check["status"] == "PASS"
    assert check["missing_markers"] == []


def _minimal_contract_text(invariant: str) -> str:
    contract = {
        "output_fields": {"fields": [
            {"name": "source_integrity"}, {"name": "prompt_injection_review"},
            {"name": "conflict_review"}, {"name": "outpatient_apply_review"},
        ]},
        "input_fields": {"fields": [{"name": "retrieved_content_security_context"}]},
        "invariant": invariant,
    }
    return json.dumps(contract, ensure_ascii=False)


_FULL_INVARIANT = (
    "Retrieved content is checked for RETRACTED_SOURCE, PROMPT_INJECTION, and "
    "CONFLICTING_EVIDENCE. C3 Safety Gate, C5 Red Team Gate, C6 Guardrail Gate, "
    "C7 Human Approval Gate, and outpatient_apply_review MUST all pass before "
    "actionable clinical guidance can be shown. This is to "
    "prevent release_state='approved_for_use' without doctor_final_approval_required."
)


def test_decision_contract_checks_all_four_mandatory_gates_named_in_its_own_invariant(
    monkeypatch, tmp_path,
):
    """★ Phát hiện #9 của Workflow đối kháng đa-agent 2026-09-03: câu bất
    biến gốc trong CLINICAL_DECISION_CONTRACT.json khai ĐỦ 4 cổng bắt buộc
    "C3 Safety Gate, C5 Red Team Gate, C6 Guardrail Gate, C7 Human Approval
    Gate" — nhưng trước bản vá, danh sách `markers` viết tay trong
    check_decision_contract() chỉ canh 2/4 tên (thiếu C5/C6), nên xoá hẳn 2
    cổng đó khỏi câu bất biến vẫn không bị phát hiện. Test dựng contract TỐI
    THIỂU trong tmp_path (không đụng file thật) để cô lập đúng lỗ hổng, rồi tự
    đột biến ngay trong bài test để chứng minh markers Python thực sự canh
    ĐỦ CẢ 4 tên — không chỉ đọc mã mà suy luận."""
    contract_path = tmp_path / "CLINICAL_DECISION_CONTRACT.json"
    contract_path.write_text(_minimal_contract_text(_FULL_INVARIANT), encoding="utf-8")
    monkeypatch.setattr(V, "CLINICAL_RUNTIME", tmp_path)

    full = V.check_decision_contract()
    assert full["status"] == "PASS", full["missing_markers"]
    assert full["missing_markers"] == []

    # Xoá đúng cụm "C5 Red Team Gate, C6 Guardrail Gate, " — mô phỏng CHÍNH
    # kịch bản đã tái hiện trên file thật ở đợt audit (đột biến JSON, chốt cũ
    # vẫn PASS). Bản vá phải bắt được ngay.
    thieu_c5_c6 = _FULL_INVARIANT.replace("C5 Red Team Gate, C6 Guardrail Gate, ", "")
    contract_path.write_text(_minimal_contract_text(thieu_c5_c6), encoding="utf-8")

    mutated = V.check_decision_contract()
    assert mutated["status"] == "FAIL"
    assert "C5 Red Team Gate" in mutated["missing_markers"]
    assert "C6 Guardrail Gate" in mutated["missing_markers"]
    # C3/C7 (hai marker cũ đã có từ trước) vẫn còn nguyên trong câu — không
    # được báo thiếu oan, để tách rõ đây là lỗi CỦA RIÊNG C5/C6.
    assert "C3 Safety Gate" not in mutated["missing_markers"]
    assert "C7 Human Approval Gate" not in mutated["missing_markers"]


def test_decision_contract_still_fails_when_c3_or_c7_missing(monkeypatch, tmp_path):
    """Đối chứng: hai marker CŨ (C3/C7) vẫn phải bị chặn khi thiếu — bản vá
    không được vô tình làm yếu luật đã có từ trước."""
    contract_path = tmp_path / "CLINICAL_DECISION_CONTRACT.json"
    thieu_c3 = _FULL_INVARIANT.replace("C3 Safety Gate, ", "")
    contract_path.write_text(_minimal_contract_text(thieu_c3), encoding="utf-8")
    monkeypatch.setattr(V, "CLINICAL_RUNTIME", tmp_path)

    check = V.check_decision_contract()
    assert check["status"] == "FAIL"
    assert "C3 Safety Gate" in check["missing_markers"]
