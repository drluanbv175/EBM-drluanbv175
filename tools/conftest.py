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


def _nap_ban_sao_tran():
    """Nạp tools/ban_sao_tran.py theo đường dẫn file (không phụ thuộc sys.path) —
    MỘT chỗ nạp dùng chung cho cả `_ban_sao_tran()` lẫn `_co_repo_y_khoa()`."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_bst_conftest", Path(__file__).resolve().parent / "ban_sao_tran.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _ban_sao_tran() -> bool:
    """Uỷ quyền cho định nghĩa DUY NHẤT ở tools/ban_sao_tran.py (vòng 4 — trong một
    PR năm bản sao của phép thử này đã phân kỳ thành hai ngữ nghĩa; hết nhân bản).

    VÒNG 5 (09/09/2026): định nghĩa này nay CLOUD-AWARE — trên cloud chỉ đòi
    EBM-Dashboards/EBM_MASTER vắng, KHÔNG còn đòi medical-ebm-automation vắng (xem
    docstring ban_sao_tran.py). Vì vậy nó KHÔNG còn dùng được cho _MODULE_CAN_REPO_Y_KHOA
    ngay dưới — nhóm đó cần biết ĐÚNG một điều: medical-ebm-automation có import được
    hay không, bất kể cloud hay không. Dùng hàm này CHO _TEST_CAN_ONEDRIVE (nguyên
    liệu chỉ sống trong OneDrive) và làm MỘT nửa điều kiện của _TEST_CAN_REPO_Y_KHOA."""
    return _nap_ban_sao_tran().ban_sao_git_tran(REPO)


def _co_repo_y_khoa(repo: Path = REPO) -> bool:
    """medical-ebm-automation/ có mặt ở vị trí LỒNG (`repo/…`, máy thật) HOẶC ANH EM
    (`repo.parent/…`, phiên Cloud dựng các repo cạnh nhau) — dò qua
    ban_sao_tran.duong_goc(), KHÔNG tự ghép đường dẫn (VÁ 26/09/2026, cùng họ bản vá
    17/09 ở tools/verify_claude_code_repo_alignment.py::_thieu_medical_ebm_automation)."""
    return _nap_ban_sao_tran().duong_goc("medical-ebm-automation", repo) is not None


def _thieu_medical_ebm_automation(repo: Path = REPO) -> bool:
    """Kiểm TRỰC TIẾP, không qua ban_sao_git_tran(): 4 module dưới đây import thẳng
    mã của medical-ebm-automation/ NGAY LÚC THU THẬP — câu hỏi thật của chúng là
    "medical-ebm-automation/ có import được không", KHÔNG phải "đây có phải bản sao
    trần không". Hai câu hỏi từng trùng nhau (bản sao trần cũ đòi CẢ BA gốc vắng,
    nên medical-ebm-automation vắng ⇒ bản sao trần), nhưng tách nhau kể từ khi
    ban_sao_git_tran() học cách CLOUD-AWARE (vòng 5): trên cloud với kiến trúc lồng
    nhau đúng, medical-ebm-automation CÓ MẶT mà ban_sao_git_tran() vẫn trả True (vì
    chỉ còn đòi EBM-Dashboards/EBM_MASTER vắng) — nếu vẫn uỷ quyền cho nó, 4 module
    này bị SKIP OAN dù nhập được thật, đúng như đã đo bằng --collect-only sau khi
    vá ban_sao_tran.py: test_research_practical_readiness.py biến mất khỏi danh sách
    thu thập trong khi module đó CHẠY ĐƯỢC và đang canh một lỗi thật (dictionary_path/
    extra_date_columns, vá 09/09/2026).

    VÁ 26/09/2026 (cascade duong_goc, sót từ đợt 17/09): bản 09/09 ở trên quay lại
    `.exists()` LỒNG THUẦN TUÝ — trên phiên Cloud bố cục ANH EM (repo.parent/
    medical-ebm-automation) hàm này báo «thiếu» dù repo có mặt, nên `collect_ignore`
    bỏ ÂM THẦM 4 module (22 test canh verifier đếm cổng cứng, khử định danh → G6…) —
    không hiện cả trong danh sách «skipped» của `pytest -rs`. Đúng lỗi mà
    verify_claude_code_repo_alignment.py đã vá 17/09 bằng duong_goc(). Nay dùng
    `_co_repo_y_khoa()` (lồng HOẶC anh em). CI (không có repo y khoa ở đâu cả) và
    máy thật bố cục lồng: hành vi KHÔNG đổi (duong_goc ưu tiên vị trí lồng)."""
    return not _co_repo_y_khoa(repo)


# 4 module import thẳng mã của repo y khoa NGAY LÚC THU THẬP — thiếu repo là
# ModuleNotFoundError trước khi test đầu tiên kịp chạy, pytest báo collection error.
_MODULE_CAN_REPO_Y_KHOA = [
    "test_controlled_research_automation.py",
    "test_evidence_approval_workflow.py",
    "test_research_practical_readiness.py",
    "test_verify_hard_gate_count_consistency.py",
]

collect_ignore = list(_MODULE_CAN_REPO_Y_KHOA) if _thieu_medical_ebm_automation() else []

_LY_DO_TRAN_ONEDRIVE = (
    "bản sao git trần — nguyên liệu chỉ sống trong OneDrive (EBM-Dashboards/ · "
    "dashboard_mockups/ · EBM_MASTER/) nằm ngoài git; chạy trên máy có đủ cây dữ liệu")
_LY_DO_TRAN_REPO_Y_KHOA = (
    "bản sao git trần VÀ không tìm thấy medical-ebm-automation/ (đã dò cả vị trí lồng "
    "lẫn anh em) — chạy trên máy/phiên có repo y khoa")

# Test đọc/gọi tài nguyên ngoài git LÚC CHẠY (không phải lúc import).
# Khoá theo tên file → tập tên test — luôn ĐÍCH DANH, không có nghĩa «cả file»:
# bản đầu dùng None = cả file cho test_classify và skip oan 81/92 test vẫn chạy
# được không cần repo y khoa (chỉ 11 test đòi retry_loop). Đo rồi mới khai.
#
# ĐÍNH CHÍNH 16/09/2026 (workflow kiểm tra toàn diện, khi cherry-pick commit
# 4dbcc2f): bản "VÒNG 5 (09/09/2026)" từng thu hẹp bảng skip xuống chỉ 5 test, dựa
# trên giả định "trên cloud, medical-ebm-automation/ LUÔN được nối lồng vào repo
# nên 18 test kia đã PASS thật" — giả định đó CHỈ đúng cho phiên cloud CỤ THỂ hôm
# đó (một phiên đã được nối kiến trúc lồng nhau thủ công). Xác minh lại 16/09 trên
# MỘT phiên cloud khác (container không có medical-ebm-automation/ nào cả, kể cả
# dạng sibling) VÀ trên CI (GitHub Actions runner — không hề set CLAUDE_CODE_REMOTE,
# không hề có medical-ebm-automation/): cả 18 test đó FAIL THẬT (không phải PASS),
# đúng như bảng gốc trước vòng 5 đã khai. Khôi phục ĐỦ danh sách gốc; giữ nguyên
# phần còn lại của bản vá cloud-aware (ban_sao_tran.py, _thieu_medical_ebm_automation(),
# _MODULE_CAN_REPO_Y_KHOA/collect_ignore) vì các phần đó kiểm TRỰC TIẾP sự có mặt
# của thư mục, không suy đoán theo biến môi trường "đang ở cloud hay không".
#
# TÁCH HAI BẢNG 26/09/2026: bảng chung cũ `_TEST_CAN_NGUYEN_LIEU` (23 test) skip
# mọi thứ chỉ theo cờ «bản sao trần» — mà trên Cloud cờ đó LUÔN True (thiếu
# EBM-Dashboards/EBM_MASTER) kể cả khi repo y khoa có mặt ở vị trí anh em. Đo trên
# phiên Cloud có repo anh em, chạy `--noconftest`: 21/23 test PASS thật (trong đó 11
# test test_classify — các ca ÂM chứng minh guardrail R13/R14/PII bắt được đầu ra
# nguy hiểm), chỉ 2 test đòi cây OneDrive là đỏ đúng thiết kế. Nay:
#   • `_TEST_CAN_ONEDRIVE`: giữ NGUYÊN điều kiện cũ — skip khi bản sao trần.
#   • `_TEST_CAN_REPO_Y_KHOA`: skip CHỈ khi ĐỒNG THỜI bản sao trần VÀ không tìm thấy
#     repo y khoa (lồng hoặc anh em). Máy thật hỏng dở OneDrive (còn EBM-Dashboards,
#     mất repo y khoa) KHÔNG phải bản sao trần ⇒ test vẫn ĐỎ như vòng 4 đòi.
#   KHÔNG dùng «`RE._retry_loop is None`» làm điều kiện skip: nếu retry_loop.py có
#   lỗi thật (SyntaxError/import hỏng) trong khi repo y khoa có mặt, cả nhóm sẽ bị
#   skip âm thầm — đúng loại xanh giả mà test_classify_available tồn tại để bắt.
_TEST_CAN_ONEDRIVE: dict[str, set[str]] = {
    "test_claude_code_repo_alignment.py": {
        # Giữ skip tới khi phép so tập check của test được cập nhật (claude_md_budget).
        "test_claude_code_repo_alignment_overall_passes",
    },
    "test_clinical_evidence_update_pipeline.py": {
        # verify_clinical_evidence_update_pipeline.py cần
        # dashboard_mockups/templates/*.html + EBM-Dashboards/tools/*.py.
        "test_clinical_evidence_update_pipeline_passes_offline",
    },
}

_TEST_CAN_REPO_Y_KHOA: dict[str, set[str]] = {
    # 11 test trong test_classify cần retry_loop.py của repo y khoa (run_eval.py tự dò
    # cả lồng lẫn anh em qua duong_goc); 81 test còn lại chạy được không cần repo y khoa.
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
        # TOOLS liệt kê 11 tool trỏ vào medical-ebm-automation/ (10) và
        # EBM-Dashboards/ (1); trên bản sao trần không repo y khoa validate() trả về
        # các lỗi đó, không phụ thuộc commit nào.
        "test_tools_registered",
    },
    "test_assess_agent_system.py": {
        "test_scorecard_checks_research_gate_contract_surface",
    },
    "test_claude_code_repo_alignment.py": {
        "test_medical_repo_docs_keep_claude_code_completion_contract",
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


def _bo_qua_nhom_repo_y_khoa(tran: bool, co_repo_y_khoa: bool) -> bool:
    """Quyết định skip cho `_TEST_CAN_REPO_Y_KHOA` — hàm THUẦN (dễ kiểm đột biến).

    Chỉ skip khi CẢ HAI: bản sao trần (không có cây OneDrive) VÀ không tìm thấy repo
    y khoa. Còn cây OneDrive (máy thật, kể cả hỏng dở) ⇒ KHÔNG skip, test thiếu
    nguyên liệu vẫn ĐỎ (vòng 4). Có repo y khoa (lồng/anh em) ⇒ KHÔNG skip, test chạy
    thật — không để guardrail R13/R14/PII bị che trên Cloud."""
    return bool(tran) and not bool(co_repo_y_khoa)


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
    tran = _ban_sao_tran()
    if tran:
        danh_dau = pytest.mark.skip(reason=_LY_DO_TRAN_ONEDRIVE)
        for item in items:
            if _khop(_TEST_CAN_ONEDRIVE, item):
                item.add_marker(danh_dau)
    if _bo_qua_nhom_repo_y_khoa(tran, _co_repo_y_khoa()):
        danh_dau_yk = pytest.mark.skip(reason=_LY_DO_TRAN_REPO_Y_KHOA)
        for item in items:
            if _khop(_TEST_CAN_REPO_Y_KHOA, item):
                item.add_marker(danh_dau_yk)
    if _fs_phan_biet_hoa_thuong():
        danh_dau_fs = pytest.mark.skip(
            reason="filesystem phân biệt hoa-thường — test này kiểm hành vi dedup "
                   "chỉ có trên APFS/NTFS (.Codex ≡ .codex); trên Linux hai thư mục "
                   "là thật và dedup là sai kỳ vọng theo thiết kế")
        for item in items:
            if _khop(_TEST_CAN_FS_KHONG_PHAN_BIET, item):
                item.add_marker(danh_dau_fs)
