#!/usr/bin/env python3
"""Kiểm chứng lớp tự động có kiểm soát cho nghiên cứu y khoa.

Verifier này dùng fixture tổng hợp, offline, không PII để kiểm ba năng lực
người dùng yêu cầu trước khi coi hệ nghiên cứu là sẵn sàng:

1. Thẩm định: guardrail rule-based phải phát hiện thiếu CI/effect size và trả
   về sửa, không cho phát hành im lặng.
2. Phản biện: automation không được tự ghi review decision; mọi artifact quan
   trọng vẫn vào hàng đợi người thật/PI/statistician.
3. Readiness có kiểm soát: review đầy đủ vẫn chưa đủ nếu thiếu G2/G4/G9 đúng
   stakeholder; chỉ mở khi đủ PI/IRB/thống kê/phản biện + approval.
4. Thống kê: engine thống kê chạy được trên số tổng hợp và luôn xuất cỡ hiệu
   ứng + khoảng tin cậy; đường phân tích dữ liệu thật có marker DATA LOCK.
5. Stakeholder gates: G2/G4/G9 chỉ thỏa khi đúng nhóm IRB/thống kê viên/PI;
   phản biện độc lập được route vào gói bản thảo/review pack.
6. Chuẩn hiện hành: WHO TRDS 1.3.1 và ICMJE 1/2026 phải tạo kiểm tra hành vi
   fail-closed, không chỉ xuất hiện dưới dạng nhãn trong tài liệu.

Cần bác sĩ kiểm chứng. Đây là kiểm kỹ thuật/guardrail, không thay IRB, PI,
thống kê viên hoặc phản biện độc lập.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import pathlib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT / "medical-ebm-automation"
TOOLS = ROOT / "tools"
EVAL_TOOLS = TOOLS / "eval"
MT = REPO / "tools"

for path in (str(TOOLS), str(EVAL_TOOLS), str(REPO), str(MT)):
    if path not in sys.path:
        sys.path.insert(0, path)

# 28/08/2026 — repo y khoa nằm ngoài bản sao git gốc; thiếu thì khai báo rõ
# thay vì ModuleNotFoundError trần (trông như lỗi mã, thật ra thiếu nguyên liệu).
if not (MT / "gate_contract.py").exists():
    # Vòng 4 (bình duyệt đối kháng): thông điệp cũ «FAIL (bỏ qua CÓ KHAI BÁO)» tự mâu
    # thuẫn, và không phân biệt bản trần với máy thật đang hỏng. Nay tách hai nhánh
    # bằng định nghĩa DUY NHẤT ở tools/ban_sao_tran.py; CẢ HAI đều thoát ≠0 vì toàn bộ
    # đối tượng của verifier này nằm trong repo y khoa — không có gì kiểm được thì
    # không được đọc thành «đã kiểm» (khác nhóm hook vốn còn phần trong-repo kiểm đủ).
    import importlib.util as _ilu
    _sp = _ilu.spec_from_file_location(
        "_bst_vcra", pathlib.Path(__file__).resolve().parent / "ban_sao_tran.py")
    _bst = _ilu.module_from_spec(_sp)
    _sp.loader.exec_module(_bst)
    if _bst.ban_sao_git_tran(ROOT):
        _LY_DO = ("⚪ NGOÀI PHẠM VI BẢN SAO TRẦN: thiếu medical-ebm-automation/tools/ — "
                  "toàn bộ đối tượng của verifier này nằm trong repo y khoa nên không có phần "
                  "trong-repo nào kiểm được; thoát 1 để không ai đọc thành «đã kiểm». "
                  "Chạy trên máy có đủ hai repo.")
    else:
        _LY_DO = ("FAIL: máy này CÓ cây dữ liệu OneDrive nhưng thiếu medical-ebm-automation/tools/ — "
                  "repo y khoa hỏng hoặc đồng bộ dở; chạy tools/sync_safety_check.py trước.")
    if __name__ == "__main__":
        raise SystemExit(_LY_DO)
    raise ModuleNotFoundError(_LY_DO)

import run_eval  # noqa: E402
import g2_quality_gate as G2Q  # noqa: E402
import g9_quality_gate as G9Q  # noqa: E402
import gate_contract as GC  # noqa: E402
import skill_standards as STANDARDS  # noqa: E402
try:  # noqa: E402
    import annex2_quality_gate as ANNEX2
except ImportError:
    # VÁ 03/09/2026 — `medical-ebm-automation/tools/annex2_quality_gate.py` KHÔNG TỒN TẠI:
    # không có trong cây làm việc, không có trên `origin/master` của CẢ HAI repo, và chuỗi
    # "annex2" xuất hiện ĐÚNG 0 lần trong toàn bộ repo y khoa. Trước bản vá này, dòng
    # `import` trần làm CHẾT verifier ngay khi nạp ⇒ **toàn bộ 764 dòng chưa từng chạy**,
    # kể cả các trục không liên quan (WHO TRDS 1.3.1, ICMJE 1/2026, 6 cổng cứng canonical,
    # QUADAS-3). Trong khi CLAUDE.md chỉ đích danh công cụ này là cách kiểm những trục đó.
    # Một khiếm khuyết ở MỘT trục không được phép làm mù toàn bộ bộ kiểm — cùng họ BH99.
    ANNEX2 = None

from orchestrator.guardrail_bridge import make_run_eval_verdict  # noqa: E402
from runtime.approval_ledger import ApprovalLedger  # noqa: E402
from research_project.project_config import (  # noqa: E402
    ARTIFACT_FILENAME,
    ArtifactID,
    ProjectConfig,
)
from research_project.project_config import REQUIRE_HUMAN_INPUT_MARKER as RHI  # noqa: E402
from research_project.project_review_operations import (  # noqa: E402
    AutoReviewForbidden,
    HumanDecision,
    MissingReviewActorReference,
    PIIInReviewRecord,
    ReviewRole,
    UnauthorizedReviewRole,
    get_controlled_review_readiness,
    get_review_status,
    list_review_queue,
    make_review_queue_item,
    record_decision,
    required_roles_for_artifact,
)
from meta_analysis_calc import pool_effects  # noqa: E402

DISCLAIMER = (
    "Cần bác sĩ kiểm chứng. Verifier dùng dữ liệu tổng hợp/offline; không thay "
    "IRB, PI, thống kê viên, phản biện độc lập hoặc kiểm định triển khai tại đơn vị."
)


def _project_config() -> ProjectConfig:
    return ProjectConfig(
        project_id="SYNTH-CONTROLLED-AUTO-001",
        title="Synthetic controlled automation verification",
        study_type="cohort",
        primary_objectives=[f"{RHI} PI xác nhận mục tiêu chính."],
        secondary_objectives=[],
        primary_outcomes=[f"{RHI} PI xác nhận kết cục chính."],
        secondary_outcomes=[],
        research_constraints={},
        data_mode="NO_REAL_DATA",
        external_actions_forbidden=True,
        draft_only=True,
        created_at="2026-07-14T00:00:00+00:00",
        version="0.1.0",
        human_owner="PI-SYNTH-001",
    )


def _write_minimal_artifact(project_dir: Path, artifact_id: ArtifactID) -> None:
    fname = ARTIFACT_FILENAME[artifact_id]
    fpath = project_dir / fname
    fpath.parent.mkdir(parents=True, exist_ok=True)
    fpath.write_text(
        "\n".join(
            [
                f"# {artifact_id.value}",
                "",
                f"{RHI} Nội dung tổng hợp cần người thật xác nhận.",
                "",
                "Cần bác sĩ / PI kiểm chứng. Đây là bản DRAFT tự động.",
            ]
        ),
        encoding="utf-8",
    )


def _accept_required_reviews(project_dir: Path, config: ProjectConfig, artifact_id: ArtifactID) -> None:
    for role in required_roles_for_artifact(artifact_id):
        record_decision(
            project_dir=project_dir,
            config=config,
            artifact_id_str=artifact_id.value,
            decision=HumanDecision.ACCEPT_DRAFT_FOR_NEXT_INTERNAL_STAGE,
            review_role=role,
            reason=f"Synthetic {role.value} acceptance for {artifact_id.value}.",
            reviewer_ref=f"{role.value}-CTRL-001",
            automation_caller=False,
        )


def check_appraisal_control() -> dict[str, Any]:
    """Guardrail phải bắt p-value đơn độc và chuyển thành RETURN-FOR-FIX/R8."""
    output_text = (
        "Bản nháp báo cáo nghiên cứu. Độ chắc chứng cứ thấp; khuyến cáo có điều "
        "kiện vì kết quả chính khác biệt có ý nghĩa thống kê p<0.03. Cờ đỏ và "
        "safety-net được nêu rõ trước khi áp dụng lâm sàng. PMID: 12345678 "
        "(2024). Cần bác sĩ kiểm chứng."
    )
    direct = run_eval.evaluate(output_text, {"type": "research"})
    with tempfile.TemporaryDirectory() as tmp:
        log_path = Path(tmp) / "APPRAISALS.jsonl"
        verdict = make_run_eval_verdict(
            output_text,
            target="synthetic-controlled-output.md",
            source="ci",
            at="2026-07-14T00:00:00+00:00",
            log_path=log_path,
        )(None)
        log_lines = log_path.read_text(encoding="utf-8").splitlines()
        record = json.loads(log_lines[-1])

    ok = (
        direct.get("verdict") == "TRẢ-VỀ-SỬA"
        and "effect_size_ci_required" in direct.get("red_fails", [])
        and verdict.get("status") == "returned_for_fix"
        and verdict.get("code") == "R8"
        and "R8" in record.get("ledger_codes", [])
    )
    return {
        "pillar": "appraisal_guardrail",
        "status": "PASS" if ok else "FAIL",
        "returned_for_fix": verdict.get("status") == "returned_for_fix",
        "direct_run_eval_verdict": direct.get("verdict"),
        "direct_run_eval_red_fails": direct.get("red_fails", []),
        "code": verdict.get("code"),
        "ledger_codes": record.get("ledger_codes", []),
        "proves": "Cổng thẩm định phát hiện p-value đơn độc thiếu 95% CI/effect size và trả về sửa.",
    }


def check_peer_review_control() -> dict[str, Any]:
    """Automation phải bị chặn khi cố tự ghi review decision."""
    with tempfile.TemporaryDirectory() as tmp:
        project_dir = Path(tmp)
        config = _project_config()
        _write_minimal_artifact(project_dir, ArtifactID.PROTOCOL_DRAFT)
        _write_minimal_artifact(project_dir, ArtifactID.SAP_DRAFT)
        _write_minimal_artifact(project_dir, ArtifactID.METHODS_AND_SAMPLE_SIZE)
        _write_minimal_artifact(project_dir, ArtifactID.REPORTING_CHECKLIST_DRAFT)
        _write_minimal_artifact(project_dir, ArtifactID.REVIEW_PACK)

        queue = list_review_queue(project_dir, config)
        protocol_item = next(i for i in queue if i["artifact_id"] == ArtifactID.PROTOCOL_DRAFT.value)
        sap_item = next(i for i in queue if i["artifact_id"] == ArtifactID.SAP_DRAFT.value)
        reporting_item = next(
            i for i in queue if i["artifact_id"] == ArtifactID.REPORTING_CHECKLIST_DRAFT.value
        )
        review_pack_item = next(i for i in queue if i["artifact_id"] == ArtifactID.REVIEW_PACK.value)
        synthetic_queue_item = make_review_queue_item(
            config.project_id,
            ArtifactID.SAP_DRAFT,
            "Kiểm thử synthetic: SAP cần reviewer phương pháp/thống kê.",
        )

        automation_blocked = False
        try:
            record_decision(
                project_dir=project_dir,
                config=config,
                artifact_id_str=ArtifactID.SAP_DRAFT.value,
                decision=HumanDecision.ACCEPT_DRAFT_FOR_NEXT_INTERNAL_STAGE,
                review_role=ReviewRole.METHODS_STATISTICS_REVIEWER,
                reason="Automation attempt should be blocked.",
                reviewer_ref="STAT-REV-AUTO-001",
                automation_caller=True,
            )
        except AutoReviewForbidden:
            automation_blocked = True

        unauthorized_role_blocked = False
        try:
            record_decision(
                project_dir=project_dir,
                config=config,
                artifact_id_str=ArtifactID.SAP_DRAFT.value,
                decision=HumanDecision.ACCEPT_DRAFT_FOR_NEXT_INTERNAL_STAGE,
                review_role=ReviewRole.PI_PROJECT_OWNER,
                reason="PI should not replace the statistician for SAP.",
                reviewer_ref="PI-REV-WRONG-001",
                automation_caller=False,
            )
        except UnauthorizedReviewRole:
            unauthorized_role_blocked = True

        missing_actor_ref_blocked = False
        try:
            record_decision(
                project_dir=project_dir,
                config=config,
                artifact_id_str=ArtifactID.EVIDENCE_PLAN.value,
                decision=HumanDecision.REQUEST_HUMAN_INPUT,
                review_role=ReviewRole.EVIDENCE_CITATION_REVIEWER,
                reason="Reviewer reference is mandatory.",
                reviewer_ref="",
                automation_caller=False,
            )
        except MissingReviewActorReference:
            missing_actor_ref_blocked = True

        pii_in_review_record_blocked = False
        try:
            record_decision(
                project_dir=project_dir,
                config=config,
                artifact_id_str=ArtifactID.SAP_DRAFT.value,
                decision=HumanDecision.REVISION_REQUIRED,
                review_role=ReviewRole.METHODS_STATISTICS_REVIEWER,
                reason="Remove email from the review note before storing it.",
                required_actions=["Không ghi họ tên hoặc patient_id vào review ledger."],
                reviewer_ref="STAT-REV-PII-001",
                automation_caller=False,
            )
        except PIIInReviewRecord:
            pii_in_review_record_blocked = True

        record_decision(
            project_dir=project_dir,
            config=config,
            artifact_id_str=ArtifactID.PROTOCOL_DRAFT.value,
            decision=HumanDecision.ACCEPT_DRAFT_FOR_NEXT_INTERNAL_STAGE,
            review_role=ReviewRole.PI_PROJECT_OWNER,
            reason="Synthetic PI internal draft acceptance.",
            reviewer_ref="PI-REV-001",
            automation_caller=False,
        )
        partial_protocol_item = next(
            i for i in list_review_queue(project_dir, config)
            if i["artifact_id"] == ArtifactID.PROTOCOL_DRAFT.value
        )
        partial_review_enforced = (
            partial_protocol_item["current_status"] == "PARTIAL_REVIEW"
            and ReviewRole.METHODS_STATISTICS_REVIEWER.value in partial_protocol_item["missing_roles"]
            and ReviewRole.IRB_ETHICS_COMMITTEE.value in partial_protocol_item["missing_roles"]
        )
        for role in (ReviewRole.METHODS_STATISTICS_REVIEWER, ReviewRole.IRB_ETHICS_COMMITTEE):
            record_decision(
                project_dir=project_dir,
                config=config,
                artifact_id_str=ArtifactID.PROTOCOL_DRAFT.value,
                decision=HumanDecision.ACCEPT_DRAFT_FOR_NEXT_INTERNAL_STAGE,
                review_role=role,
                reason=f"Synthetic {role.value} internal draft acceptance.",
                reviewer_ref=f"{role.value}-REV-001",
                automation_caller=False,
            )
        complete_protocol_item = next(
            i for i in list_review_queue(project_dir, config)
            if i["artifact_id"] == ArtifactID.PROTOCOL_DRAFT.value
        )
        complete_multi_role_review = (
            complete_protocol_item["current_status"] == "ACCEPTED_DRAFT"
            and complete_protocol_item["complete_required_review"] is True
            and complete_protocol_item["missing_roles"] == []
        )
        status = get_review_status(project_dir)

    methods_routed = (
        ReviewRole.METHODS_STATISTICS_REVIEWER.value in protocol_item["primary_roles"]
        and ReviewRole.METHODS_STATISTICS_REVIEWER.value in sap_item["primary_roles"]
    )
    irb_routed = ReviewRole.IRB_ETHICS_COMMITTEE.value in protocol_item["primary_roles"]
    independent_peer_routed = (
        ReviewRole.INDEPENDENT_PEER_REVIEWER.value in reporting_item["primary_roles"]
        and ReviewRole.INDEPENDENT_PEER_REVIEWER.value in review_pack_item["primary_roles"]
    )
    human_required = all(item["human_review_required"] for item in queue)
    no_auto_approve = synthetic_queue_item["auto_approve"] is False
    ok = (
        automation_blocked and methods_routed and irb_routed
        and independent_peer_routed and unauthorized_role_blocked
        and missing_actor_ref_blocked and pii_in_review_record_blocked
        and partial_review_enforced and complete_multi_role_review
        and human_required and no_auto_approve
    )
    return {
        "pillar": "peer_review_control",
        "status": "PASS" if ok else "FAIL",
        "automation_review_blocked": automation_blocked,
        "methods_statistics_review_routed": methods_routed,
        "irb_ethics_review_routed": irb_routed,
        "independent_peer_review_routed": independent_peer_routed,
        "unauthorized_review_role_blocked": unauthorized_role_blocked,
        "missing_review_actor_ref_blocked": missing_actor_ref_blocked,
        "pii_in_review_record_blocked": pii_in_review_record_blocked,
        "partial_multi_role_review_enforced": partial_review_enforced,
        "complete_multi_role_review_detected": complete_multi_role_review,
        "human_review_required": human_required,
        "auto_approve": synthetic_queue_item["auto_approve"],
        "review_status": status,
        "proves": "Automation không thể tự duyệt; role sai, thiếu mã reviewer giả danh và PII trong review đều bị chặn; protocol đi qua PARTIAL_REVIEW rồi chỉ hoàn tất khi đủ PI+IRB+thống kê; bản thảo/review pack có phản biện độc lập.",
    }


def _make_approval(gate_id: str, role: str):
    return ApprovalLedger.make_human_approval(
        gate_id=gate_id,
        reviewer_role=role,
        reviewer_ref=f"REF-{gate_id}-{role}",
        scope=f"Stakeholder gate fixture {gate_id}",
        evidence_content=f"Evidence {gate_id} {role}",
    )


def check_stakeholder_gate_control() -> dict[str, Any]:
    """G2/G4/G9 phải fail-closed khi approval sai stakeholder hoặc synthetic.

    Vá 2026-07-15: G4 CHẤP NHẬN CẢ thống kê viên LẪN PI tự ký (gate_contract.py,
    2026-07-14 — khớp doctrine thiet-ke-nghien-cuu.md). PI_PROJECT_OWNER không còn là
    "role sai" cho G4 kể từ đó — dùng IRB_ETHICS_COMMITTEE làm role sai để tiếp tục
    kiểm fail-closed (IRB chưa từng và vẫn không thỏa G4)."""
    ledger = ApprovalLedger()

    wrong_g2_ok, _ = ledger.add_approval(_make_approval("G2", "PI_PROJECT_OWNER"))
    wrong_g4_ok, _ = ledger.add_approval(_make_approval("G4", "IRB_ETHICS_COMMITTEE"))
    wrong_roles_rejected_by_gate = (
        wrong_g2_ok and wrong_g4_ok
        and not ledger.has_ethics_approval()
        and not ledger.has_sap_lock()
    )

    synthetic_irb = ApprovalLedger.make_synthetic_approval(
        gate_id="G2",
        scope="Synthetic IRB fixture",
        evidence_content="Synthetic ethics content",
        reviewer_role="IRB_ETHICS_COMMITTEE",
        reviewer_ref="IRB-SYNTH",
    )
    ledger._records.append(synthetic_irb)
    synthetic_not_accepted = not ledger.has_ethics_approval()

    for gate_id, role in (
        ("G2", "IRB_ETHICS_COMMITTEE"),
        ("G4", "METHODS_STATISTICS_REVIEWER"),
        ("G9", "PI_PROJECT_OWNER"),
    ):
        ok, reason = ledger.add_approval(_make_approval(gate_id, role))
        if not ok:
            return {
                "pillar": "stakeholder_gate_control",
                "status": "FAIL",
                "reason": reason,
                "proves": "Không ghi được approval stakeholder hợp lệ trên fixture synthetic.",
            }

    statuses = {gate: ledger.stakeholder_gate_status(gate) for gate in ("G2", "G4", "G9")}
    gate_contract_roles = (
        not GC.reviewer_role_satisfies_gate("G2", "PI_PROJECT_OWNER")
        and GC.reviewer_role_satisfies_gate("G2", "IRB_ETHICS_COMMITTEE")
        and GC.reviewer_role_satisfies_gate("G4", "PI_PROJECT_OWNER")
        and GC.reviewer_role_satisfies_gate("G4", "BIOSTATISTICIAN")
        and not GC.reviewer_role_satisfies_gate("G4", "IRB_ETHICS_COMMITTEE")
        and GC.reviewer_role_satisfies_gate("G5", "DATA_MANAGER")
        and GC.reviewer_role_satisfies_gate("G5", "PI_PROJECT_OWNER")
        and not GC.reviewer_role_satisfies_gate("G5", "IRB_ETHICS_COMMITTEE")
        and GC.reviewer_role_satisfies_gate("G8", "INDEPENDENT_PEER_REVIEWER")
        and not GC.reviewer_role_satisfies_gate("G8", "PI_PROJECT_OWNER")
        and GC.reviewer_role_satisfies_gate("G9", "PRINCIPAL_INVESTIGATOR")
        and GC.reviewer_role_satisfies_gate("G10", "PRINCIPAL_INVESTIGATOR")
        and not GC.reviewer_role_satisfies_gate("G10", "INDEPENDENT_PEER_REVIEWER")
    )
    ok = (
        wrong_roles_rejected_by_gate
        and synthetic_not_accepted
        and all(status["satisfied"] for status in statuses.values())
        and gate_contract_roles
    )
    return {
        "pillar": "stakeholder_gate_control",
        "status": "PASS" if ok else "FAIL",
        "wrong_role_approvals_do_not_unlock": wrong_roles_rejected_by_gate,
        "synthetic_approval_does_not_unlock": synthetic_not_accepted,
        "g2_irb_status": statuses["G2"],
        "g4_statistician_status": statuses["G4"],
        "g9_pi_status": statuses["G9"],
        "gate_contract_role_filter": gate_contract_roles,
        "proves": "Sáu cổng cứng G2/G4/G5/G8/G9/G10 lọc đúng vai trò; PI không thể thay IRB hoặc phản biện độc lập; synthetic approval không mở cổng.",
    }


def check_current_standards_control() -> dict[str, Any]:
    """WHO TRDS, ICMJE 1/2026 và ICH Annex 2 phải là hợp đồng hành vi."""
    meta = {
        "gate_params": {
            "G0": {
                "intervention": "Can thiệp tổng hợp X",
                "comparison": "Chăm sóc chuẩn",
                "outcomes": ["Đáp ứng", "Biến cố bất lợi"],
                "primary_outcome": "Đáp ứng",
                "primary_outcome_measure": "Tỷ lệ đạt đáp ứng",
                "primary_outcome_timepoint": "12 tuần",
            },
            "G1": {
                "intervention_or_exposure": "Can thiệp tổng hợp X",
                "comparator": "Chăm sóc chuẩn",
                "inclusion_criteria": ["Tuổi từ 18"],
                "exclusion_criteria": ["Chống chỉ định can thiệp"],
                "primary_outcome": "Đáp ứng",
                "secondary_outcomes": ["Biến cố bất lợi"],
            },
        }
    }
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp)
        common = {
            "study": "SYNTH-STANDARDS-001",
            "topic": "Can thiệp X ở người trưởng thành",
            "design_code": "rct",
            "design_primary": "Thử nghiệm ngẫu nhiên có đối chứng",
            "risk": {
                "registration": "BẮT BUỘC trước tuyển mẫu",
                "register_where": "WHO primary registry",
            },
            "n_target": 120,
            "out_dir": out_dir,
            "generated_at": "2026-08-01T00:00:00+00:00",
        }
        complete_path = G2Q.build_registration_draft(**common, meta=meta)
        complete = json.loads(complete_path.read_text(encoding="utf-8"))
        complete_gaps = G2Q.scientific_registration_item_gaps(complete, "rct")
        missing_path = G2Q.build_registration_draft(
            **{**common, "study": "SYNTH-STANDARDS-MISSING"},
            meta=None,
        )
        missing = json.loads(missing_path.read_text(encoding="utf-8"))
        missing_gaps = G2Q.scientific_registration_item_gaps(missing, "rct")

    readiness = G9Q.build_readiness_template("SYNTH-G9-STANDARDS", 1)
    author_refs = {"AUTHOR-01"}
    access_default_ok, _ = G9Q.data_access_governance_ok(readiness, author_refs)
    readiness["data_access_governance"].update(
        {
            "all_authors_can_review_supporting_data": True,
            "primary_data_access_author_ref": "AUTHOR-01",
            "primary_data_access_confirmed": True,
            "analysis_participation_confirmed": True,
            "academic_nonacademic_collaboration": False,
            "sponsored_research": False,
            "confirmed_at": "2026-08-01T00:00:00+00:00",
        }
    )
    access_complete_ok, _ = G9Q.data_access_governance_ok(readiness, author_refs)
    icmje_access_standard = any(
        "Access to Data" in row.get("standard", "")
        for row in G9Q.STANDARDS_BASIS
    )
    hard_gates = tuple(STANDARDS.PIPELINE_HARD_GATES)
    annex2_missing = {
        "gate_params": {"G1": {"annex2": {
            "applicable": True, "methodologies": ["decentralised", "rwd"],
        }}}
    }
    annex2_complete = {
        "gate_params": {"G1": {"annex2": {
            "applicable": True,
            "methodologies": ["decentralised", "rwd"],
            "fit_for_purpose_justification": "Phương pháp phù hợp mục tiêu và quần thể.",
            "participant_burden_and_access": "Có thiết bị mượn và lựa chọn khám trực tiếp.",
            "roles_and_oversight": "PI giám sát theo mức trọng yếu của dữ liệu.",
            "safety_information_flow": "Cảnh báo DHT chuyển tới investigator theo SLA.",
            "remote_data_collection_plan": "DHT đã thẩm định; lịch và hỗ trợ được tiền định.",
            "data_provenance_and_quality": "Nguồn RWD, lineage và fitness-for-use đã mô tả.",
            "data_variability_and_sap": "SAP tiền định biến thiên theo nguồn và sensitivity.",
            "irb_information_plan": "IRB nhận mô tả đầy đủ mọi phương pháp Annex 2.",
            "privacy_confidentiality_security": "Mã hóa, phân quyền và lưu vết truy cập.",
            "remote_consent_and_identity": "Xác minh danh tính và quy trình eConsent tiền định.",
            "alternative_access_path": "Có bản giấy/khám trực tiếp khi người tham gia yêu cầu.",
            "dht_validation_and_support": "Kiểm định DHT, đào tạo và hỗ trợ kỹ thuật.",
            "access_and_permissions": "Quyền truy cập và phạm vi consent RWD đã xác định.",
            "data_governance": "Sponsor chịu trách nhiệm; service provider có RACI/audit.",
        }}}
    }
    if ANNEX2 is None:
        # ⚠️ FAIL, KHÔNG phải ⚪ «chưa kiểm được» — và phân biệt này là CỐ Ý.
        # ⚪ dành cho thiếu NGUYÊN LIỆU trên máy đang chạy (BH08/BH85). Ở đây khác hẳn:
        # doctrine `dao-duc-dang-ky.md` §"ICH E6(R3) Annex 2 — hợp đồng CHẠY ĐƯỢC tại G1/G2"
        # KHẲNG ĐỊNH một cổng đang CHẶN ("Thiếu trường thật hoặc còn nhãn [CẦN...] → BLOCK,
        # không được mở G1/G2") và chỉ đích danh file thi hành. File đó chưa bao giờ tồn tại
        # ⇒ đây là LỜI KHAI VỀ MỘT CỔNG KHÔNG CÓ THẬT, đúng họ BH27 — phải đỏ.
        annex2_missing_g1 = annex2_missing_g2 = {"status": "KHONG_CO_BO_THI_HANH"}
        annex2_complete_g1 = annex2_complete_g2 = {"status": "KHONG_CO_BO_THI_HANH"}
        annex2_behavior = False
        annex2_bao_cao = {
            "trang_thai": "KHONG_CO_BO_THI_HANH",
            "module_thieu": "medical-ebm-automation/tools/annex2_quality_gate.py",
            "hai": ("doctrine khai đây là hợp đồng CHẠY ĐƯỢC chặn G1/G2 cho thử nghiệm "
                    "decentralised/pragmatic/RWD, nhưng KHÔNG có mã nào thi hành — "
                    "thử nghiệm loại này hiện KHÔNG được máy chặn ở G1/G2."),
            "viec_cua_nguoi": ("nội dung ICH E6(R3) Annex 2 là chuẩn quy phạm — bộ tiêu chí "
                               "phải do PI/methodologist ấn định, agent KHÔNG được tự bịa. "
                               "Trong lúc chưa có: xử lý tay và đừng đọc doctrine như đã có cổng."),
        }
    else:
        annex2_missing_g1 = ANNEX2.evaluate(annex2_missing, "rct", "G1")
        annex2_missing_g2 = ANNEX2.evaluate(annex2_missing, "rct", "G2")
        annex2_complete_g1 = ANNEX2.evaluate(annex2_complete, "rct", "G1")
        annex2_complete_g2 = ANNEX2.evaluate(annex2_complete, "rct", "G2")
        annex2_bao_cao = None
    annex2_behavior = annex2_behavior if ANNEX2 is None else (
        ANNEX2.ADOPTED_DATE == "2026-06-03"
        and annex2_missing_g1["status"] == "BLOCK"
        and annex2_missing_g2["status"] == "BLOCK"
        and annex2_complete_g1["status"] == "PASS"
        and annex2_complete_g2["status"] == "PASS"
    )
    quadas_map = (ROOT / ".claude/agents/_BAN-DO-KET-NOI.md").read_text(encoding="utf-8")
    quadas_agent = (ROOT / ".claude/agents/tham-dinh-do-chinh-xac-chan-doan.md").read_text(
        encoding="utf-8"
    )
    quadas3_operational = (
        "chẩn đoán/QUADAS-3+STARD" in quadas_map
        and "QUADAS-2+STARD" not in quadas_map
        and "QUADAS-3 — 6 pha" in quadas_agent
        and "Participants · Index Test · Target Condition · Analysis" in quadas_agent
        and "đánh giá theo từng ước lượng" in quadas_agent
        and "PMID 41698208" in quadas_agent
    )
    ok = all(
        (
            G2Q.WHO_TRDS_VERSION == "1.3.1",
            G2Q.WHO_TRDS_ITEM_COUNT == 24,
            complete_gaps == [],
            len(missing_gaps) == 4,
            G9Q.QUALITY_CONTRACT_VERSION == "G9-2026.2",
            icmje_access_standard,
            access_default_ok is False,
            access_complete_ok is True,
            hard_gates == ("G2", "G4", "G5", "G8", "G9", "G10"),
            annex2_behavior,
            quadas3_operational,
        )
    )
    return {
        "pillar": "current_standards_control",
        "status": "PASS" if ok else "FAIL",
        "who_trds_version": G2Q.WHO_TRDS_VERSION,
        "who_trds_items": G2Q.WHO_TRDS_ITEM_COUNT,
        "complete_scientific_gaps": complete_gaps,
        "missing_scientific_gaps": missing_gaps,
        "g9_contract_version": G9Q.QUALITY_CONTRACT_VERSION,
        "icmje_authors_access_to_data": icmje_access_standard,
        "default_access_attestation_fails_closed": access_default_ok is False,
        "complete_access_attestation_passes": access_complete_ok is True,
        "canonical_hard_gates": list(hard_gates),
        "ich_e6_r3_annex2": annex2_bao_cao if ANNEX2 is None else {
            "version": ANNEX2.VERSION,
            "adopted_date": ANNEX2.ADOPTED_DATE,
            "missing_g1_blocks": annex2_missing_g1["status"] == "BLOCK",
            "missing_g2_blocks": annex2_missing_g2["status"] == "BLOCK",
            "complete_g1_passes": annex2_complete_g1["status"] == "PASS",
            "complete_g2_passes": annex2_complete_g2["status"] == "PASS",
        },
        "quadas3_operational_mapping": quadas3_operational,
        "proves": "WHO TRDS 1.3.1 lấy dữ kiện PI đã pin và thiếu 13/14/19/20 bị phát hiện; G9 thực thi quyền tác giả truy cập dữ liệu theo ICMJE 1/2026; ICH E6(R3) Annex 2 chặn G1/G2 khi thử nghiệm decentralised/pragmatic/RWD thiếu kiểm soát (CHỈ khi annex2_quality_gate.py tồn tại — xem khoá ich_e6_r3_annex2 để biết trục này đã thật sự được chấm hay đang KHONG_CO_BO_THI_HANH); nguồn chuẩn khớp sáu cổng ký runtime.",
    }


def check_controlled_readiness_gate() -> dict[str, Any]:
    """Review đầy đủ chỉ mở milestone khi approval stakeholder tương ứng cũng đủ."""
    with tempfile.TemporaryDirectory() as tmp:
        project_dir = Path(tmp)
        config = _project_config()
        controlled_artifacts = (
            ArtifactID.PROTOCOL_DRAFT,
            ArtifactID.METHODS_AND_SAMPLE_SIZE,
            ArtifactID.SAP_DRAFT,
            ArtifactID.REPORTING_CHECKLIST_DRAFT,
            ArtifactID.MANUSCRIPT_OUTLINE_DRAFT,
            ArtifactID.REVIEW_PACK,
        )
        for artifact_id in controlled_artifacts:
            _write_minimal_artifact(project_dir, artifact_id)

        empty_ledger = ApprovalLedger()
        initial = get_controlled_review_readiness(project_dir, approval_ledger=empty_ledger)
        initially_blocked = initial["overall_status"] == "BLOCKED"

        for artifact_id in controlled_artifacts:
            _accept_required_reviews(project_dir, config, artifact_id)

        review_only = get_controlled_review_readiness(project_dir, approval_ledger=empty_ledger)
        review_only_blocked = (
            review_only["overall_status"] == "BLOCKED"
            and review_only["milestone_ready_count"] == 0
            and "stakeholder_approval_missing:G2:IRB" in json.dumps(review_only["milestones"])
            and "stakeholder_approval_missing:G4:STATISTICIAN" in json.dumps(review_only["milestones"])
            and "stakeholder_approval_missing:G9:PI" in json.dumps(review_only["milestones"])
        )

        approval_ledger = ApprovalLedger()
        for gate_id, role in (
            ("G2", "IRB_ETHICS_COMMITTEE"),
            ("G4", "METHODS_STATISTICS_REVIEWER"),
            ("G9", "PI_PROJECT_OWNER"),
        ):
            ok, reason = approval_ledger.add_approval(_make_approval(gate_id, role))
            if not ok:
                return {
                    "pillar": "controlled_readiness_gate",
                    "status": "FAIL",
                    "reason": reason,
                    "proves": "Không ghi được approval stakeholder hợp lệ trên fixture synthetic.",
                }

        ready = get_controlled_review_readiness(project_dir, approval_ledger=approval_ledger)

    peer_review_in_readiness = (
        ReviewRole.INDEPENDENT_PEER_REVIEWER.value in json.dumps(ready["milestones"])
    )
    all_milestones_ready = (
        ready["overall_status"] == "PASS"
        and ready["can_advance_controlled_workflow"] is True
        and ready["milestone_ready_count"] == ready["milestone_total"] == 3
        and ready["blocking_count"] == 0
        and ready["final_released_submitted_count"] == 0
    )
    ok = initially_blocked and review_only_blocked and all_milestones_ready and peer_review_in_readiness
    return {
        "pillar": "controlled_readiness_gate",
        "status": "PASS" if ok else "FAIL",
        "initially_blocked": initially_blocked,
        "review_only_still_blocked": review_only_blocked,
        "all_milestones_ready_after_stakeholder_approvals": all_milestones_ready,
        "peer_review_in_readiness": peer_review_in_readiness,
        "ready_snapshot": ready,
        "proves": "Readiness tổng hợp fail-closed: đủ review nhưng thiếu G2/G4/G9 vẫn chặn; chỉ PASS khi đủ PI+IRB+thống kê+phản biện và stakeholder approvals.",
    }


def check_statistics_control() -> dict[str, Any]:
    """Engine thống kê phải xuất effect size + CI và main analysis phải có DATA LOCK."""
    pooled = pool_effects(
        effects=[0.08, 0.22, -0.03],
        variances=[0.040, 0.055, 0.060],
        alpha=0.05,
    )
    random_effect = pooled["random_effect"]
    fixed_effect = pooled["fixed_effect"]
    stats_source = (MT / "run_stats_analysis.py").read_text(encoding="utf-8")
    gate_contract_source = (MT / "gate_contract.py").read_text(encoding="utf-8")
    # Logic data-lock đã được gom vào gate_contract để run_stats_analysis và các
    # template G6 dùng chung. Kiểm cả điểm gọi lẫn implementation canonical; không
    # đòi các reason-code phải còn lặp lại trong file caller.
    caller_markers = [
        "_require_locked_analysis_dataset",
        "GC.locked_analysis_dataset_blockers",
        "G6_analysis_summary.json",
    ]
    contract_markers = [
        "def locked_analysis_dataset_blockers",
        "LOCKED_FOR_ANALYSIS",
        "provided_data_is_not_locked_dataset",
        "locked_dataset_checksum_mismatch",
    ]
    has_lock_gate = (
        all(marker in stats_source for marker in caller_markers)
        and all(marker in gate_contract_source for marker in contract_markers)
    )
    has_effect_ci = (
        isinstance(random_effect.get("pooled"), float)
        and len(random_effect.get("ci", [])) == 2
        and len(fixed_effect.get("ci", [])) == 2
        and pooled["heterogeneity"]["I2_percent"] >= 0
    )
    ok = has_effect_ci and has_lock_gate
    return {
        "pillar": "statistics_control",
        "status": "PASS" if ok else "FAIL",
        "k_studies": pooled["k_studies"],
        "random_effect": {
            "pooled": round(random_effect["pooled"], 6),
            "ci": [round(x, 6) for x in random_effect["ci"]],
        },
        "fixed_effect_ci_present": len(fixed_effect.get("ci", [])) == 2,
        "heterogeneity_i2_percent": round(pooled["heterogeneity"]["I2_percent"], 3),
        "prediction_interval_present": pooled["prediction_interval"]["pi"] is not None,
        "data_lock_gate_markers_present": has_lock_gate,
        "proves": "Engine thống kê tính pooled effect/95% CI/I2/PI trên fixture tổng hợp và script G6 có cổng DATA LOCK.",
    }


def run_verification() -> dict[str, Any]:
    checks = [
        check_appraisal_control(),
        check_peer_review_control(),
        check_stakeholder_gate_control(),
        check_controlled_readiness_gate(),
        check_statistics_control(),
        check_current_standards_control(),
    ]
    failures = [check for check in checks if check["status"] != "PASS"]
    return {
        "kind": "controlled_research_automation_verification",
        "overall_status": "PASS" if not failures else "FAIL",
        "failure_count": len(failures),
        "checks": checks,
        "disclaimer": DISCLAIMER,
    }


def print_summary(report: dict[str, Any]) -> None:
    print(f"CONTROLLED_RESEARCH_AUTOMATION: {report['overall_status']}")
    for check in report["checks"]:
        print(f"- {check['status']} {check['pillar']}: {check['proves']}")
    print(report["disclaimer"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="In JSON ra stdout.")
    args = parser.parse_args()

    report = run_verification()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_summary(report)
    return 0 if report["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
