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
    PR năm bản sao của phép thử này đã phân kỳ thành hai ngữ nghĩa; hết nhân bản).

    VÒNG 5 (09/09/2026): định nghĩa này nay CLOUD-AWARE — trên cloud chỉ đòi
    EBM-Dashboards/EBM_MASTER vắng, KHÔNG còn đòi medical-ebm-automation vắng (xem
    docstring ban_sao_tran.py). Vì vậy nó KHÔNG còn dùng được cho _MODULE_CAN_REPO_Y_KHOA
    ngay dưới — nhóm đó cần biết ĐÚNG một điều: medical-ebm-automation có import được
    hay không, bất kể cloud hay không. Dùng hàm này CHO _TEST_CAN_NGUYEN_LIEU (đa số
    entry ở đó là về EBM-Dashboards/EBM_MASTER, xem chú thích từng entry)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_bst_conftest", Path(__file__).resolve().parent / "ban_sao_tran.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.ban_sao_git_tran(REPO)


def _thieu_medical_ebm_automation() -> bool:
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
    extra_date_columns, vá 09/09/2026)."""
    return not (REPO / "medical-ebm-automation").exists()


# 4 module import thẳng mã của repo y khoa NGAY LÚC THU THẬP — thiếu repo là
# ModuleNotFoundError trước khi test đầu tiên kịp chạy, pytest báo collection error.
_MODULE_CAN_REPO_Y_KHOA = [
    "test_controlled_research_automation.py",
    "test_evidence_approval_workflow.py",
    "test_research_practical_readiness.py",
    "test_verify_hard_gate_count_consistency.py",
]

collect_ignore = list(_MODULE_CAN_REPO_Y_KHOA) if _thieu_medical_ebm_automation() else []

_LY_DO_TRAN = ("bản sao git trần — nguyên liệu (medical-ebm-automation/ · "
               "EBM-Dashboards/ · EBM_MASTER/) nằm ngoài git; chạy trên máy có đủ cây dữ liệu")

# Test đọc/gọi tài nguyên ngoài git LÚC CHẠY (không phải lúc import).
# Khoá theo tên file → tập tên test — luôn ĐÍCH DANH, không có nghĩa «cả file»:
# bản đầu dùng None = cả file cho test_classify và skip oan 81/92 test vẫn chạy
# được không cần repo y khoa (chỉ 11 test đòi retry_loop). Đo rồi mới khai.
_TEST_CAN_NGUYEN_LIEU: dict[str, set[str]] = {
    # VÒNG 5 (09/09/2026): sau khi ban_sao_git_tran() học CLOUD-AWARE (chỉ đòi
    # EBM-Dashboards/EBM_MASTER vắng trên cloud, không còn đòi medical-ebm-automation
    # vắng), đo lại TOÀN BỘ danh sách này bằng cách tắt skip rồi chạy thật (không suy
    # đoán): 18/24 test trước đây bị khai ở đây thật ra ĐÃ PASS với
    # medical-ebm-automation/ có mặt — trong đó CẢ 11 test của test_classify.py (cần
    # retry_loop.py — chính là file NẰM TRONG medical-ebm-automation/tools/, nên đúng
    # ra phải theo _thieu_medical_ebm_automation(), và trên cloud với repo y khoa
    # NẰM TRONG kiến trúc lồng nhau thật thì file đó CÓ, test PASS chứ không cần
    # skip). Đã gỡ 18 test đó khỏi bảng dưới — giữ chúng ở đây sau vòng 5 sẽ SKIP OAN
    # test đang chạy tốt, đúng lớp lỗi mà bản vá ban_sao_tran.py hôm nay vừa sinh ra
    # ở _MODULE_CAN_REPO_Y_KHOA và ở check_medical_docs() của
    # verify_claude_code_repo_alignment.py (cả hai đã vá cùng ngày).
    # CHỈ CÒN 5 test dưới đây — đã xác nhận lại bằng chạy thật: cả 5 đều fail vì
    # EBM-Dashboards/tools/verify_dashboard.py hoặc pipeline phụ thuộc EBM-Dashboards,
    # KHÔNG phải vì medical-ebm-automation — đúng nhóm _ban_sao_tran() (cloud-aware)
    # vẫn phải gate.
    "test_orchestrator.py": {
        "test_validate_catches_dangling_single_task_reference",
        "test_validate_clean",
        # TOOLS đăng ký `verify-dashboard` trỏ EBM-Dashboards/tools/verify_dashboard.py
        # — gốc DUY NHẤT còn gây lỗi ở test này từ khi medical-ebm-automation/ có mặt
        # (đo thật 09/09: chỉ còn ĐÚNG 1 lỗi, không phải 11 như lượt khai 28/08 mô tả
        # — con số đó đúng cho topology CŨ khi medical-ebm-automation/ còn vắng).
        "test_tools_registered",
    },
    "test_clinical_evidence_update_pipeline.py": {
        # verify_clinical_evidence_update_pipeline.py cần
        # dashboard_mockups/templates/*.html + EBM-Dashboards/tools/*.py.
        "test_clinical_evidence_update_pipeline_passes_offline",
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
