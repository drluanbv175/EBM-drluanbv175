# -*- coding: utf-8 -*-
"""conftest — cho bộ test tools/ chạy được cả trên BẢN SAO GIT TRẦN (cloud/CI).

VÌ SAO CÓ (28/08/2026): đo trên bản clone git KHÔNG có cây OneDrive cho 23 test
fail + 4 module không thu thập được — soi từng cái thì TẤT CẢ đều vì nguyên liệu
nằm ngoài git (medical-ebm-automation/ · EBM-Dashboards/ · EBM_MASTER/), hoặc vì
một test viết riêng cho filesystem KHÔNG phân biệt hoa-thường (APFS/NTFS) chạy
trên Linux. Không cái nào là lỗi mã — nhưng 27 dòng đỏ giả là đúng «bức tường đỏ
giả» mà BH08/BH82 cảnh báo: nó che mất fail THẬT nếu một ngày có.

Quy ước (cùng họ ⚪ «bỏ qua CÓ KHAI BÁO» của chot_hoi_quy_bai_hoc/BH82):
  • CHỈ can thiệp khi bản sao trần (cả 3 gốc dữ liệu vắng mặt) — trên máy bác sĩ
    (còn ≥1 gốc) file này KHÔNG đổi gì, test thiếu file vẫn đỏ như trước.
  • Skip phải NÓI RÕ lý do (`pytest -rs` đọc được), không im lặng.
  • Danh sách khai báo TƯỜNG MINH theo tên module/tên test — không suy đoán từ
    thông điệp lỗi (đúng cách _CAN_NGUYEN_LIEU_NGOAI_REPO đã làm).
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _ban_sao_tran() -> bool:
    """Uỷ quyền cho định nghĩa DUY NHẤT ở tools/ban_sao_tran.py (vòng 4 — trong một
    PR năm bản sao của phép thử này đã phân kỳ thành hai ngữ nghĩa; hết nhân bản)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_bst_conftest", Path(__file__).resolve().parent / "ban_sao_tran.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.ban_sao_git_tran(REPO)


# 4 module import thẳng mã của repo y khoa NGAY LÚC THU THẬP — thiếu repo là
# ModuleNotFoundError trước khi test đầu tiên kịp chạy, pytest báo collection error.
_MODULE_CAN_REPO_Y_KHOA = [
    "test_controlled_research_automation.py",
    "test_evidence_approval_workflow.py",
    "test_research_practical_readiness.py",
    "test_verify_hard_gate_count_consistency.py",
]

collect_ignore = list(_MODULE_CAN_REPO_Y_KHOA) if _ban_sao_tran() else []

_LY_DO_TRAN = ("bản sao git trần — nguyên liệu (medical-ebm-automation/ · "
               "EBM-Dashboards/ · EBM_MASTER/) nằm ngoài git; chạy trên máy có đủ cây dữ liệu")

# Test đọc/gọi tài nguyên ngoài git LÚC CHẠY (không phải lúc import).
# Khoá theo tên file → tập tên test — luôn ĐÍCH DANH, không có nghĩa «cả file»:
# bản đầu dùng None = cả file cho test_classify và skip oan 81/92 test vẫn chạy
# được không cần repo y khoa (chỉ 11 test đòi retry_loop). Đo rồi mới khai.
_TEST_CAN_NGUYEN_LIEU: dict[str, set[str]] = {
    # 11 test trong test_classify cần retry_loop.py của repo y khoa; 81 test còn lại chạy được
    "test_classify.py": {
        "test_classify_available",
        "test_classify_maps_known_checks_to_rcodes",
        "test_classify_passes_when_no_mapped_failures",
        "test_classify_pii_triggers_must_escalate",
        "test_format_dispatch_matches_house_style",
        "test_unmapped_checks_are_skipped_not_guessed",
        "test_r8_bare_pvalue_without_ci_fails",
        "test_r1b_label_gaming_flagged_when_no_real_source",
        "test_r13_s1_suicide_screen_missing_escalates",
        "test_r13_s3_antidepressant_suicide_screen_missing_escalates",
        "test_r14_prescribing_without_safety_review_escalates",
    },
    "test_orchestrator.py": {
        "test_validate_catches_dangling_single_task_reference",
        "test_validate_clean",
        "test_registry_is_fail_closed_and_valid",
    },
    "test_assess_agent_system.py": {
        "test_scorecard_checks_research_gate_contract_surface",
    },
    "test_claude_code_repo_alignment.py": {
        "test_claude_code_repo_alignment_overall_passes",
        "test_medical_repo_docs_keep_claude_code_completion_contract",
    },
    "test_clinical_evidence_update_pipeline.py": {
        "test_clinical_evidence_update_pipeline_passes_offline",
    },
    "test_clinical_runtime_readiness_report.py": {
        "test_readiness_report_unlocks_21_of_37_repo_controls_without_production",
        "test_unlocked_rows_are_still_human_gated_and_control_linked",
        "test_markdown_names_21_of_37_and_keeps_safety_boundary",
    },
    "test_lessons_rubric_alignment.py": {
        "test_current_lessons_rubric_alignment_passes",
    },
}

# Test viết riêng cho filesystem KHÔNG phân biệt hoa-thường (APFS/NTFS): trên
# filesystem phân biệt (Linux/ext4), `.Codex` và `.codex` là HAI thư mục thật nên
# kỳ vọng «dedup còn một» sai theo thiết kế của chính filesystem, không phải bug.
_TEST_CAN_FS_KHONG_PHAN_BIET = {
    "test_sync_agents_to_codex.py": {
        "test_real_checkout_active_targets_dedups_to_single_canonical_entry",
    },
}


def _fs_phan_biet_hoa_thuong() -> bool:
    """Đo THẬT thuộc tính filesystem bằng file thử — không đoán theo os.name."""
    with tempfile.TemporaryDirectory(prefix="fs-case-probe-") as td:
        (Path(td) / "a").write_text("x", encoding="utf-8")
        return not (Path(td) / "A").exists()


def _khop(bang: dict[str, set[str]], item) -> bool:
    muc = bang.get(Path(str(item.fspath)).name)
    if not muc:
        return False
    return item.name.split("[")[0] in muc


def pytest_collection_modifyitems(config, items):
    if _ban_sao_tran():
        danh_dau = pytest.mark.skip(reason=_LY_DO_TRAN)
        for item in items:
            if _khop(_TEST_CAN_NGUYEN_LIEU, item):
                item.add_marker(danh_dau)
    if _fs_phan_biet_hoa_thuong():
        danh_dau_fs = pytest.mark.skip(
            reason="filesystem phân biệt hoa-thường — test này kiểm hành vi dedup "
                   "chỉ có trên APFS/NTFS (.Codex ≡ .codex); trên Linux hai thư mục "
                   "là thật và dedup là sai kỳ vọng theo thiết kế")
        for item in items:
            if _khop(_TEST_CAN_FS_KHONG_PHAN_BIET, item):
                item.add_marker(danh_dau_fs)
