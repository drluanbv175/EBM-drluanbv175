# -*- coding: utf-8 -*-
"""Hồi quy 26/09/2026 — tools/conftest.py dò repo y khoa ĐÚNG (lồng HOẶC anh em).

Hai lỗi cùng gốc (synthesis #20, #21):
  • #20 — `_thieu_medical_ebm_automation()` chỉ ghép `REPO / "medical-ebm-automation"`
    (vị trí LỒNG) ⇒ trên phiên Cloud bố cục ANH EM, `collect_ignore` bỏ ÂM THẦM 4
    module (22 test) dù repo y khoa có mặt và nhập được.
  • #21 — bảng skip chung skip 23 test chỉ theo cờ «bản sao trần» (trên Cloud LUÔN
    True) ⇒ 21 test chạy được bị che, trong đó 11 ca ÂM của guardrail R13/R14/PII.

Kiểm HÀNH VI qua hàm thật của conftest (nạp theo đường dẫn file, không phụ thuộc
cách pytest tự nạp conftest), dựng bố cục thư mục bằng tmp_path.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_CONFTEST = Path(__file__).resolve().parent / "conftest.py"


def _nap_conftest():
    spec = importlib.util.spec_from_file_location("_conftest_hoi_quy_20260926", _CONFTEST)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def cf():
    return _nap_conftest()


# ---------- #20: dò repo y khoa ở cả hai bố cục ----------

def _dung_bo_cuc(tmp_path: Path, kieu: str) -> Path:
    """Trả đường repo gốc giả; `kieu` ∈ {"long", "anh_em", "khong"}."""
    cha = tmp_path / "cha"
    goc = cha / "EBM-drluanbv175"
    goc.mkdir(parents=True)
    if kieu == "long":
        (goc / "medical-ebm-automation").mkdir()
    elif kieu == "anh_em":
        (cha / "medical-ebm-automation").mkdir()
    return goc


def test_bo_cuc_long_khong_thieu(cf, tmp_path):
    goc = _dung_bo_cuc(tmp_path, "long")
    assert cf._co_repo_y_khoa(goc) is True
    assert cf._thieu_medical_ebm_automation(goc) is False


def test_bo_cuc_anh_em_khong_thieu(cf, tmp_path):
    """Ca đỏ trước bản vá: `.exists()` lồng thuần tuý báo «thiếu» ở bố cục anh em."""
    goc = _dung_bo_cuc(tmp_path, "anh_em")
    assert cf._co_repo_y_khoa(goc) is True
    assert cf._thieu_medical_ebm_automation(goc) is False


def test_khong_co_o_dau_ca_thi_thieu(cf, tmp_path):
    """Hành vi CI giữ nguyên: không có repo y khoa ở đâu ⇒ thiếu ⇒ collect_ignore."""
    goc = _dung_bo_cuc(tmp_path, "khong")
    assert cf._co_repo_y_khoa(goc) is False
    assert cf._thieu_medical_ebm_automation(goc) is True


def test_khong_noi_danh_sach_module_can_repo_y_khoa(cf):
    """Bản vá KHÔNG được nới/xoá mục nào của _MODULE_CAN_REPO_Y_KHOA."""
    assert set(cf._MODULE_CAN_REPO_Y_KHOA) == {
        "test_controlled_research_automation.py",
        "test_evidence_approval_workflow.py",
        "test_research_practical_readiness.py",
        "test_verify_hard_gate_count_consistency.py",
    }


# ---------- #21: tách bảng skip, điều kiện skip nhóm repo y khoa ----------

@pytest.mark.parametrize("tran, co_repo, ky_vong", [
    (True, False, True),    # CI / Cloud không repo y khoa ⇒ skip (như cũ)
    (True, True, False),    # Cloud có repo anh em ⇒ CHẠY (bản vá)
    (False, False, False),  # máy thật hỏng dở OneDrive ⇒ KHÔNG skip, phải ĐỎ (vòng 4)
    (False, True, False),   # máy thật đủ cây ⇒ chạy
])
def test_bang_chan_tri_bo_qua_nhom_repo_y_khoa(cf, tran, co_repo, ky_vong):
    assert cf._bo_qua_nhom_repo_y_khoa(tran, co_repo) is ky_vong


_GUARDRAIL_AM = {
    "test_classify_pii_triggers_must_escalate",
    "test_r13_s1_suicide_screen_missing_escalates",
    "test_r13_s3_antidepressant_suicide_screen_missing_escalates",
    "test_r14_prescribing_without_safety_review_escalates",
}


def test_bang_repo_y_khoa_dung_21_test_va_khong_chong_bang_onedrive(cf):
    yk = {(f, t) for f, ts in cf._TEST_CAN_REPO_Y_KHOA.items() for t in ts}
    od = {(f, t) for f, ts in cf._TEST_CAN_ONEDRIVE.items() for t in ts}
    assert len(yk) == 21
    assert not (yk & od), "một test không được nằm ở cả hai bảng"
    # Các ca ÂM của guardrail lâm sàng phải thuộc nhóm repo y khoa, KHÔNG thuộc nhóm
    # OneDrive (nếu không, trên Cloud chúng lại bị che).
    for ten in _GUARDRAIL_AM:
        assert ("test_classify.py", ten) in yk
        assert ("test_classify.py", ten) not in od
    # Test đòi cây OneDrive thật vẫn skip theo điều kiện cũ.
    assert ("test_clinical_evidence_update_pipeline.py",
            "test_clinical_evidence_update_pipeline_passes_offline") in od


class _ItemGia:
    def __init__(self, ten_file: str, ten: str):
        self.fspath = Path("/khong/ton/tai") / ten_file
        self.name = ten
        self.marks: list = []

    def add_marker(self, mark):
        self.marks.append(mark)


def _chay_modifyitems(cf, monkeypatch, *, tran: bool, co_repo: bool):
    monkeypatch.setattr(cf, "_ban_sao_tran", lambda: tran)
    monkeypatch.setattr(cf, "_co_repo_y_khoa", lambda repo=cf.REPO: co_repo)
    # Cô lập khỏi thuộc tính filesystem thật của máy chạy test.
    monkeypatch.setattr(cf, "_fs_phan_biet_hoa_thuong", lambda: False)
    guardrail = _ItemGia("test_classify.py", "test_r14_prescribing_without_safety_review_escalates")
    onedrive = _ItemGia("test_clinical_evidence_update_pipeline.py",
                        "test_clinical_evidence_update_pipeline_passes_offline")
    khac = _ItemGia("test_classify.py", "test_mot_test_khong_khai_bao")
    cf.pytest_collection_modifyitems(None, [guardrail, onedrive, khac])
    return guardrail, onedrive, khac


def test_cloud_co_repo_anh_em_guardrail_chay_onedrive_van_skip(cf, monkeypatch):
    guardrail, onedrive, khac = _chay_modifyitems(cf, monkeypatch, tran=True, co_repo=True)
    assert guardrail.marks == [], "guardrail R14 bị skip dù repo y khoa có mặt (xanh giả)"
    assert len(onedrive.marks) == 1
    assert onedrive.marks[0].kwargs["reason"] == cf._LY_DO_TRAN_ONEDRIVE
    assert khac.marks == []


def test_ban_sao_tran_khong_repo_y_khoa_skip_ca_hai_nhom_co_ly_do(cf, monkeypatch):
    guardrail, onedrive, khac = _chay_modifyitems(cf, monkeypatch, tran=True, co_repo=False)
    assert len(guardrail.marks) == 1
    assert guardrail.marks[0].kwargs["reason"] == cf._LY_DO_TRAN_REPO_Y_KHOA
    assert len(onedrive.marks) == 1
    assert khac.marks == []


def test_may_that_hong_do_khong_skip_gi(cf, monkeypatch):
    """Còn cây OneDrive nhưng mất repo y khoa ⇒ KHÔNG skip (test phải đỏ thật)."""
    guardrail, onedrive, khac = _chay_modifyitems(cf, monkeypatch, tran=False, co_repo=False)
    assert guardrail.marks == [] and onedrive.marks == [] and khac.marks == []
