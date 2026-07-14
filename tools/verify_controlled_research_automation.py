#!/usr/bin/env python3
"""Kiểm chứng lớp tự động có kiểm soát cho nghiên cứu y khoa.

Verifier này dùng fixture tổng hợp, offline, không PII để kiểm ba năng lực
người dùng yêu cầu trước khi coi hệ nghiên cứu là sẵn sàng:

1. Thẩm định: guardrail rule-based phải phát hiện thiếu CI/effect size và trả
   về sửa, không cho phát hành im lặng.
2. Phản biện: automation không được tự ghi review decision; mọi artifact quan
   trọng vẫn vào hàng đợi người thật/PI/statistician.
3. Thống kê: engine thống kê chạy được trên số tổng hợp và luôn xuất cỡ hiệu
   ứng + khoảng tin cậy; đường phân tích dữ liệu thật có marker DATA LOCK.
4. Stakeholder gates: G2/G4/G9 chỉ thỏa khi đúng nhóm IRB/thống kê viên/PI;
   phản biện độc lập được route vào gói bản thảo/review pack.

Cần bác sĩ kiểm chứng. Đây là kiểm kỹ thuật/guardrail, không thay IRB, PI,
thống kê viên hoặc phản biện độc lập.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
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

import run_eval  # noqa: E402
import gate_contract as GC  # noqa: E402
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
    get_review_status,
    list_review_queue,
    make_review_queue_item,
    record_decision,
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
    """G2/G4/G9 phải fail-closed khi approval sai stakeholder hoặc synthetic."""
    ledger = ApprovalLedger()

    wrong_g2_ok, _ = ledger.add_approval(_make_approval("G2", "PI_PROJECT_OWNER"))
    wrong_g4_ok, _ = ledger.add_approval(_make_approval("G4", "PI_PROJECT_OWNER"))
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
        and not GC.reviewer_role_satisfies_gate("G4", "PI_PROJECT_OWNER")
        and GC.reviewer_role_satisfies_gate("G4", "BIOSTATISTICIAN")
        and GC.reviewer_role_satisfies_gate("G9", "PRINCIPAL_INVESTIGATOR")
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
        "proves": "G2/G4/G9 yêu cầu đúng stakeholder: IRB, thống kê/phương pháp, PI; synthetic approval không mở cổng.",
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
    lock_markers = [
        "_require_locked_analysis_dataset",
        "LOCKED_FOR_ANALYSIS",
        "provided_data_is_not_locked_dataset",
        "locked_dataset_checksum_mismatch",
        "G6_analysis_summary.json",
    ]
    has_lock_gate = all(marker in stats_source for marker in lock_markers)
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
        check_statistics_control(),
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
