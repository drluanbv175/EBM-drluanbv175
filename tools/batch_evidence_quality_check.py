#!/usr/bin/env python3
"""Workflow duyet the chung cu va phan lop Q1-Q7.

Mac dinh script tao batch 78 the `decision="notyet"` de bac si duyet.
Auto-classification chi la hang doi uu tien, khong tu cap nhat `decision`
trong EBM_MASTER.json va khong thay the phe duyet lam sang cua bac si.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import openpyxl
    from openpyxl.comments import Comment
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation
except ImportError:
    print("ERROR: openpyxl not found. Install: pip install openpyxl")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

EVIDENCE_DB_PATH = Path(__file__).parent.parent / "EBM_MASTER" / "EBM_MASTER.json"
OUTPUT_EXCEL = Path(__file__).parent.parent / "EBM_MASTER" / "_EVIDENCE_APPROVAL_WORKFLOW.xlsx"
OUTPUT_JSON = Path(__file__).parent.parent / "EBM_MASTER" / "_EVIDENCE_APPROVAL_WORKFLOW.report.json"
DEFAULT_REVIEW_LIMIT = 78

AUTO_APPLY_REVIEW = "READY_FOR_PHYSICIAN_APPLY_REVIEW"
AUTO_CONSIDER_REVIEW = "READY_FOR_PHYSICIAN_CONSIDER_REVIEW"
AUTO_NOT_READY = "NOT_READY_NEEDS_EVIDENCE_WORK"

DECISION_OPTIONS = ("APPLY", "CONSIDER", "NOT_YET", "UNCHANGED")
SCOPE_OPTIONS = ("pending", "broad", "all")

QUALITY_CRITERIA: dict[str, dict[str, str]] = {
    "Q1": {
        "name": "Readability",
        "description": "Noi dung ro muc tieu lam sang, de doc, tranh qua ngan hoac mo ho.",
    },
    "Q2": {
        "name": "Accuracy / Traceability",
        "description": "Co PMID, DOI, URL nguon, hoac references hop le; dinh dang khong sai.",
    },
    "Q3": {
        "name": "Completeness",
        "description": "Co nam, nguon/tap chi/guideline va effect estimate hoac khuyen cao.",
    },
    "Q4": {
        "name": "Bias",
        "description": "RCT can RoB 2; observational can ROBINS-I; guideline/consensus co the N/A.",
    },
    "Q5": {
        "name": "Harm",
        "description": "Co thao luan ve SAE, harm, contraindication, safety hoac nguy co hai.",
    },
    "Q6": {
        "name": "Currency",
        "description": "Uu tien cong bo trong 5 nam; landmark trial co the duoc ngoai le.",
    },
    "Q7": {
        "name": "Authority",
        "description": "Nguon co tham quyen: society guideline, co quan chinh thuc, hoac tap chi top.",
    },
}


@dataclass(frozen=True)
class WorkflowConfig:
    master: Path = EVIDENCE_DB_PATH
    output: Path = OUTPUT_EXCEL
    json_report: Path = OUTPUT_JSON
    scope: str = "pending"
    limit: int = DEFAULT_REVIEW_LIMIT


def configure_utf8_stdio() -> None:
    """Bao ve log/argparse tren Windows console khong dung UTF-8."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass


def _text(value: Any) -> str:
    return str(value or "").strip()


def _source(card: dict[str, Any]) -> dict[str, Any]:
    source = card.get("source")
    return source if isinstance(source, dict) else {}


def _critical_appraisal(card: dict[str, Any]) -> dict[str, Any]:
    appraisal = card.get("critical_appraisal")
    return appraisal if isinstance(appraisal, dict) else {}


def _is_unverified_status(status: str) -> bool:
    status_low = status.lower()
    markers = (
        "chua",
        "chưa",
        "pending",
        "unverified",
        "provisional",
        "draft",
        "can xac minh",
        "cần xác minh",
        "can kiem chung",
        "cần kiểm chứng",
    )
    return any(marker in status_low for marker in markers)


def references(card: dict[str, Any]) -> list[str]:
    refs = card.get("references")
    if isinstance(refs, list):
        return [_text(ref) for ref in refs if _text(ref)]
    return []


def traceability_level(card: dict[str, Any]) -> str:
    src = _source(card)
    if _text(src.get("pmid")) and _text(src.get("doi")):
        return "pmid+doi"
    if _text(src.get("pmid")):
        return "pmid"
    if _text(src.get("doi")):
        return "doi"
    if _text(src.get("url")) or references(card):
        return "url_or_reference"
    return "missing"


def _extract_year(card: dict[str, Any]) -> int | None:
    raw_year = _text(card.get("date_source"))
    match = re.search(r"(19|20)\d{2}", raw_year)
    if not match:
        return None
    return int(match.group(0))


def _grade_priority(card: dict[str, Any]) -> int:
    grade = _text(card.get("gradeLevel")).lower()
    if grade in {"high", "a", "grade a"} or "high" in grade:
        return 0
    if grade in {"moderate", "b", "grade b"} or "moderate" in grade:
        return 1
    if grade in {"low", "c", "grade c"} or "low" in grade:
        return 2
    if grade in {"very low", "d", "na", "n/a", ""}:
        return 3
    return 4


def _review_priority_key(card: dict[str, Any]) -> tuple[int, int, int, int, int, str]:
    decision = _text(card.get("decision")).lower()
    decision_priority = {"notyet": 0, "consider": 1, "apply": 2}.get(decision, 3)
    verification_priority = 0 if _is_unverified_status(_text(card.get("verification_status"))) else 1
    trace_priority = {
        "pmid+doi": 0,
        "pmid": 1,
        "doi": 2,
        "url_or_reference": 3,
        "missing": 4,
    }[traceability_level(card)]
    year = _extract_year(card) or 0
    return (
        decision_priority,
        verification_priority,
        _grade_priority(card),
        trace_priority,
        -year,
        _text(card.get("id")),
    )


class EvidenceQualityChecker:
    """Checker Q1-Q7 tu dong cho moi the."""

    def check_q1_readability(self, card: dict[str, Any]) -> tuple[bool, str]:
        source = _source(card)
        text = " ".join(
            [
                _text(card.get("recommendation")),
                _text(source.get("title")),
                _text(card.get("topic")),
            ]
        )
        if len(text) < 30:
            return False, "Noi dung qua ngan (<30 ky tu)."

        keywords = (
            "diagnose",
            "diagnosis",
            "treat",
            "treatment",
            "prevent",
            "prevention",
            "monitor",
            "screen",
            "guideline",
            "recommend",
            "chan doan",
            "chẩn đoán",
            "dieu tri",
            "điều trị",
            "du phong",
            "dự phòng",
            "theo doi",
            "theo dõi",
            "khuyen cao",
            "khuyến cáo",
        )
        if any(keyword in text.lower() for keyword in keywords):
            return True, "Noi dung co muc tieu/hanh dong lam sang ro."
        return False, "Thieu muc tieu hoac hanh dong lam sang ro."

    def check_q2_accuracy(self, card: dict[str, Any]) -> tuple[bool, str]:
        source = _source(card)
        pmid = _text(source.get("pmid"))
        doi = _text(source.get("doi"))
        url = _text(source.get("url"))

        if pmid and not re.match(r"^\d{1,9}$", pmid):
            return False, f"PMID khong hop le: {pmid}"
        if doi and not re.match(r"^10\.\d+/", doi, re.IGNORECASE):
            return False, f"DOI khong hop le: {doi}"
        if url and not re.match(r"^https?://", url, re.IGNORECASE):
            return False, f"URL nguon khong hop le: {url}"
        if not (pmid or doi or url or references(card)):
            return False, "Thieu truy nguyen nguon: PMID/DOI/URL/references."
        return True, f"Truy nguyen hop le: {traceability_level(card)}."

    def check_q3_completeness(self, card: dict[str, Any]) -> tuple[bool, str]:
        source = _source(card)
        appraisal = _critical_appraisal(card)
        if _extract_year(card) is None:
            return False, "Thieu hoac sai nam cong bo."

        agency_or_journal = (
            _text(source.get("agency"))
            or _text(source.get("journal"))
            or _text(source.get("title"))
            or _text(source.get("type"))
        )
        if not agency_or_journal:
            return False, "Thieu nguon/tap chi/guideline."

        if not (_text(appraisal.get("effect_estimate")) or _text(card.get("recommendation"))):
            return False, "Thieu effect estimate hoac khuyen cao."

        return True, "Co nam, nguon va effect estimate/khuyen cao."

    def check_q4_bias(self, card: dict[str, Any]) -> tuple[bool, str]:
        appraisal = _critical_appraisal(card)
        design = _text(appraisal.get("design")).lower()
        effect = _text(appraisal.get("effect_estimate")).lower()
        title = _text(_source(card).get("title")).lower()
        blob = " ".join([design, effect, title])

        if any(token in blob for token in ("guideline", "consensus", "expert", "society")):
            return True, "Guideline/consensus: bias tool N/A."
        if any(token in blob for token in ("rct", "randomized", "randomised")):
            if "rob" in blob or "risk of bias" in blob:
                return True, "RCT co RoB/risk-of-bias."
            return False, "RCT nhung thieu RoB 2/risk-of-bias."
        if any(token in blob for token in ("cohort", "case-control", "observational")):
            if "robins" in blob or "risk of bias" in blob:
                return True, "Observational co ROBINS-I/risk-of-bias."
            return False, "Observational nhung thieu ROBINS-I/risk-of-bias."
        if design:
            return True, "Design co mo ta; bias tool khong bat buoc theo heuristic."
        return False, "Thieu design de danh gia risk of bias."

    def check_q5_harm(self, card: dict[str, Any]) -> tuple[bool, str]:
        blob = " ".join(
            [
                _text(card.get("recommendation")),
                _text(card.get("certainty")),
                _text(card.get("safety")),
                _text(card.get("topic")),
                _text(_critical_appraisal(card).get("effect_estimate")),
            ]
        ).lower()
        harm_keywords = (
            "sae",
            "adverse",
            "harm",
            "contraindication",
            "safety",
            "side effect",
            "bleeding",
            "mortality",
            "toxicity",
            "renal",
            "hepatic",
            "tai bien",
            "tác dụng phụ",
            "an toan",
            "an toàn",
            "chong chi dinh",
            "chống chỉ định",
            "chay mau",
            "chảy máu",
            "nguy co",
            "nguy cơ",
            "canh bao",
            "cảnh báo",
        )
        if any(keyword in blob for keyword in harm_keywords):
            return True, "Harm/safety duoc thao luan."
        return False, "Khong thay thao luan SAE/harm/safety."

    def check_q6_currency(self, card: dict[str, Any]) -> tuple[bool, str]:
        year = _extract_year(card)
        if year is None:
            return False, "Thieu hoac sai nam cong bo."
        age = datetime.now().year - year
        design = _text(_critical_appraisal(card).get("design")).lower()
        if age <= 5 or "landmark" in design:
            return True, f"Con moi hoac landmark ({year})."
        return False, f"Cu ({year}, {age} nam); can kiem guideline moi."

    def check_q7_authority(self, card: dict[str, Any]) -> tuple[bool, str]:
        source = _source(card)
        blob = " ".join(
            [
                _text(source.get("agency")),
                _text(source.get("type")),
                _text(source.get("journal")),
                _text(source.get("title")),
                _text(source.get("url")),
            ]
        ).lower()
        top_tier = (
            "who",
            "nice",
            "esc",
            "aha",
            "acc",
            "ada",
            "kdigo",
            "gina",
            "gold",
            "cdc",
            "uspstf",
            "cochrane",
            "nejm",
            "lancet",
            "jama",
            "bmj",
            "nature",
            "science",
        )
        if any(org in blob for org in top_tier):
            return True, "Nguon co tham quyen cao."
        return False, "Can bac si xac minh authority/IF/tier cua nguon."

    def run_all_checks(self, card: dict[str, Any]) -> dict[str, tuple[bool, str]]:
        return {
            "Q1": self.check_q1_readability(card),
            "Q2": self.check_q2_accuracy(card),
            "Q3": self.check_q3_completeness(card),
            "Q4": self.check_q4_bias(card),
            "Q5": self.check_q5_harm(card),
            "Q6": self.check_q6_currency(card),
            "Q7": self.check_q7_authority(card),
        }

    def get_classification(self, results: dict[str, tuple[bool, str]]) -> str:
        passed = sum(1 for pass_flag, _ in results.values() if pass_flag)
        if not results["Q2"][0]:
            return AUTO_NOT_READY
        if passed >= 6 and results["Q5"][0]:
            return AUTO_APPLY_REVIEW
        if passed >= 4:
            return AUTO_CONSIDER_REVIEW
        return AUTO_NOT_READY


def load_evidence_db(master: Path = EVIDENCE_DB_PATH) -> list[dict[str, Any]]:
    if not master.exists():
        raise FileNotFoundError(f"File not found: {master}")
    with master.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    cards = data.get("evidence_cards", [])
    if not isinstance(cards, list):
        raise ValueError("EBM_MASTER.json does not contain a list at evidence_cards.")
    return cards


def filter_cards_for_review(
    cards: list[dict[str, Any]],
    scope: str = "pending",
    limit: int = DEFAULT_REVIEW_LIMIT,
) -> list[dict[str, Any]]:
    if scope not in SCOPE_OPTIONS:
        raise ValueError(f"Unknown scope: {scope}")
    if limit < 0:
        raise ValueError("limit must be >= 0; use 0 for no limit.")

    def include_card(card: dict[str, Any]) -> bool:
        decision = _text(card.get("decision")).lower()
        verification_status = _text(card.get("verification_status"))
        if scope == "pending":
            return decision == "notyet"
        if scope == "broad":
            return decision in {"notyet", "consider"} or _is_unverified_status(verification_status)
        return True

    review_cards = sorted((card for card in cards if include_card(card)), key=_review_priority_key)
    if limit:
        review_cards = review_cards[:limit]

    logger.info("Found %s cards for review with scope=%s limit=%s", len(review_cards), scope, limit)
    return review_cards


def _red_flags(card: dict[str, Any], q_results: dict[str, tuple[bool, str]]) -> list[str]:
    flags: list[str] = []
    if not q_results["Q2"][0]:
        flags.append("Q2_TRACEABILITY_FAIL")
    if not q_results["Q5"][0]:
        flags.append("Q5_HARM_NEEDS_REVIEW")
    if not q_results["Q7"][0]:
        flags.append("Q7_AUTHORITY_NEEDS_REVIEW")
    if _is_unverified_status(_text(card.get("verification_status"))):
        flags.append("UNVERIFIED_STATUS")
    if traceability_level(card) == "missing":
        flags.append("NO_SOURCE_TRACE")
    return flags


def run_quality_check_batch(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    checker = EvidenceQualityChecker()
    results: list[dict[str, Any]] = []

    for idx, card in enumerate(cards, 1):
        q_results = checker.run_all_checks(card)
        classification = checker.get_classification(q_results)
        q_score_num = sum(1 for pass_flag, _ in q_results.values() if pass_flag)
        source = _source(card)

        result = {
            "id": _text(card.get("id")),
            "title": (_text(card.get("recommendation")) or _text(source.get("title")))[:120],
            "topic": _text(card.get("topic")),
            "specialty": _text(card.get("specialty")),
            "pmid": _text(source.get("pmid")),
            "doi": _text(source.get("doi")),
            "source_agency": _text(source.get("agency")) or _text(source.get("journal")) or _text(source.get("type")),
            "date_source": _text(card.get("date_source")),
            "gradeLevel": _text(card.get("gradeLevel")),
            "current_decision": _text(card.get("decision")),
            "verification_status": _text(card.get("verification_status")),
            "traceability": traceability_level(card),
            "Q_Score_Num": q_score_num,
            "Q_Score": f"{q_score_num}/7",
            "Auto_Classification": classification,
            "Doctor_Decision": "",
            "Doctor_Notes": "",
        }
        for key in QUALITY_CRITERIA:
            passed, note = q_results[key]
            result[f"{key}_Status"] = "PASS" if passed else "FAIL"
            result[f"{key}_Note"] = note

        result["red_flags"] = "; ".join(_red_flags(card, q_results))
        results.append(result)

        if idx % 10 == 0:
            logger.info("Processed %s/%s cards", idx, len(cards))

    logger.info("Completed Q1-Q7 check for %s cards", len(results))
    return results


def _add_readme_sheet(wb: openpyxl.Workbook, config: WorkflowConfig, row_count: int) -> None:
    ws = wb.create_sheet("README")
    rows = [
        ("Purpose", "Doctor-facing approval workflow for evidence cards."),
        ("Batch", f"{row_count} cards; scope={config.scope}; limit={config.limit}."),
        ("Safety", "Auto classification is triage only. Doctor approval is required."),
        ("Output", str(config.output)),
        ("Decision options", ", ".join(DECISION_OPTIONS)),
        ("Disclaimer", "Can bac si kiem chung. Khong dua vao workflow nay nhu quyet dinh lam sang tu dong."),
    ]
    for row in rows:
        ws.append(row)
    ws.column_dimensions["A"].width = 22
    ws.column_dimensions["B"].width = 110
    for cell in ws["A"]:
        cell.font = Font(bold=True)


def _add_criteria_sheet(wb: openpyxl.Workbook) -> None:
    ws = wb.create_sheet("Q1-Q7 Criteria")
    ws.append(["Code", "Name", "Description"])
    for key, criterion in QUALITY_CRITERIA.items():
        ws.append([key, criterion["name"], criterion["description"]])
    for cell in ws[1]:
        cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        cell.font = Font(bold=True, color="FFFFFF")
    ws.column_dimensions["A"].width = 8
    ws.column_dimensions["B"].width = 26
    ws.column_dimensions["C"].width = 100
    ws.freeze_panes = "A2"


def export_to_excel(results: list[dict[str, Any]], config: WorkflowConfig) -> Path:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Evidence Approval"

    headers = [
        "ID",
        "Title",
        "Topic",
        "Specialty",
        "PMID",
        "DOI",
        "Agency",
        "Year",
        "Grade",
        "Current\nDecision",
        "Verification\nStatus",
        "Traceability",
        "Red\nFlags",
        "Q1\nReadability",
        "Q1 Note",
        "Q2\nAccuracy",
        "Q2 Note",
        "Q3\nComplete",
        "Q3 Note",
        "Q4\nBias",
        "Q4 Note",
        "Q5\nHarm",
        "Q5 Note",
        "Q6\nCurrency",
        "Q6 Note",
        "Q7\nAuthority",
        "Q7 Note",
        "Q_Score",
        "Auto\nClassify",
        "Doctor\nDecision",
        "Doctor\nNotes",
    ]
    ws.append(headers)
    header_by_name = {name: idx for idx, name in enumerate(headers, 1)}

    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=10)
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment

    row_keys = [
        "id",
        "title",
        "topic",
        "specialty",
        "pmid",
        "doi",
        "source_agency",
        "date_source",
        "gradeLevel",
        "current_decision",
        "verification_status",
        "traceability",
        "red_flags",
        "Q1_Status",
        "Q1_Note",
        "Q2_Status",
        "Q2_Note",
        "Q3_Status",
        "Q3_Note",
        "Q4_Status",
        "Q4_Note",
        "Q5_Status",
        "Q5_Note",
        "Q6_Status",
        "Q6_Note",
        "Q7_Status",
        "Q7_Note",
        "Q_Score",
        "Auto_Classification",
        "Doctor_Decision",
        "Doctor_Notes",
    ]

    fill_apply = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
    fill_consider = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
    fill_not_ready = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
    fill_fail = PatternFill(start_color="F4CCCC", end_color="F4CCCC", fill_type="solid")
    fill_pass = PatternFill(start_color="D9EAD3", end_color="D9EAD3", fill_type="solid")

    auto_col = header_by_name["Auto\nClassify"]
    doctor_decision_col = header_by_name["Doctor\nDecision"]
    q_status_headers = {
        "Q1": "Q1\nReadability",
        "Q2": "Q2\nAccuracy",
        "Q3": "Q3\nComplete",
        "Q4": "Q4\nBias",
        "Q5": "Q5\nHarm",
        "Q6": "Q6\nCurrency",
        "Q7": "Q7\nAuthority",
    }

    for result in results:
        ws.append([result[key] for key in row_keys])
        row_idx = ws.max_row

        auto_cell = ws.cell(row=row_idx, column=auto_col)
        if result["Auto_Classification"] == AUTO_APPLY_REVIEW:
            auto_cell.fill = fill_apply
        elif result["Auto_Classification"] == AUTO_CONSIDER_REVIEW:
            auto_cell.fill = fill_consider
        else:
            auto_cell.fill = fill_not_ready

        for q_code, status_header in q_status_headers.items():
            status_col = header_by_name[status_header]
            status_cell = ws.cell(row=row_idx, column=status_col)
            status_cell.fill = fill_pass if status_cell.value == "PASS" else fill_fail

    if results:
        options = ",".join(DECISION_OPTIONS)
        validation = DataValidation(type="list", formula1=f'"{options}"', allow_blank=True)
        validation.error = "Use APPLY, CONSIDER, NOT_YET, or UNCHANGED."
        validation.errorTitle = "Invalid doctor decision"
        validation.prompt = "Select doctor decision after review."
        validation.promptTitle = "Doctor decision"
        ws.add_data_validation(validation)
        decision_letter = get_column_letter(doctor_decision_col)
        validation.add(f"{decision_letter}2:{decision_letter}{len(results) + 1}")

    header_comments = {
        "Auto\nClassify": "Triage suggestion only; does not change the database.",
        "Doctor\nDecision": "Doctor-approved final action consumed by process_approved_evidence.py.",
        "Red\nFlags": "Review blockers or cautions surfaced from Q1-Q7 heuristics.",
    }
    for header, comment in header_comments.items():
        ws.cell(row=1, column=header_by_name[header]).comment = Comment(comment, "Codex")

    widths = {
        "A": 16,
        "B": 45,
        "C": 24,
        "D": 18,
        "E": 12,
        "F": 24,
        "G": 20,
        "H": 10,
        "I": 10,
        "J": 14,
        "K": 18,
        "L": 18,
        "M": 32,
    }
    for letter, width in widths.items():
        ws.column_dimensions[letter].width = width
    for col_idx in range(14, len(headers) + 1):
        ws.column_dimensions[get_column_letter(col_idx)].width = 18

    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)

    ws.freeze_panes = "B2"
    ws.auto_filter.ref = ws.dimensions

    _add_readme_sheet(wb, config, len(results))
    _add_criteria_sheet(wb)

    config.output.parent.mkdir(parents=True, exist_ok=True)
    wb.save(config.output)
    logger.info("Excel exported: %s", config.output)
    return config.output


def _json_cards(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cards = []
    for result in results:
        cards.append(
            {
                "id": result["id"],
                "title": result["title"],
                "current_decision": result["current_decision"],
                "verification_status": result["verification_status"],
                "traceability": result["traceability"],
                "q_score": result["Q_Score"],
                "auto_classification": result["Auto_Classification"],
                "red_flags": result["red_flags"],
                "q_results": {
                    key: {
                        "status": result[f"{key}_Status"],
                        "note": result[f"{key}_Note"],
                    }
                    for key in QUALITY_CRITERIA
                },
            }
        )
    return cards


def build_report(
    results: list[dict[str, Any]],
    total_cards: int,
    selected_cards: int,
    config: WorkflowConfig,
) -> dict[str, Any]:
    q_fail_counts: Counter[str] = Counter()
    for result in results:
        for q_code in QUALITY_CRITERIA:
            if result[f"{q_code}_Status"] == "FAIL":
                q_fail_counts[q_code] += 1

    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "workflow": "evidence_approval_q1_q7",
        "scope": config.scope,
        "limit": config.limit,
        "paths": {
            "master": str(config.master),
            "excel": str(config.output),
            "json_report": str(config.json_report),
        },
        "summary": {
            "total_cards_in_master": total_cards,
            "selected_cards": selected_cards,
            "database_mutated": False,
            "doctor_approval_required": True,
            "disclaimer": "Can bac si kiem chung.",
        },
        "classification_distribution": dict(Counter(r["Auto_Classification"] for r in results)),
        "traceability_distribution": dict(Counter(r["traceability"] for r in results)),
        "verification_status_distribution": dict(Counter(r["verification_status"] for r in results)),
        "q_fail_distribution": dict(q_fail_counts),
        "cards": _json_cards(results),
    }


def write_json_report(report: dict[str, Any], config: WorkflowConfig) -> Path:
    config.json_report.parent.mkdir(parents=True, exist_ok=True)
    with config.json_report.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
    logger.info("JSON report exported: %s", config.json_report)
    return config.json_report


def parse_args(argv: list[str] | None = None) -> WorkflowConfig:
    parser = argparse.ArgumentParser(
        description="Create doctor approval workbook for evidence cards with Q1-Q7 classification."
    )
    parser.add_argument("--master", type=Path, default=EVIDENCE_DB_PATH, help="Path to EBM_MASTER.json.")
    parser.add_argument("--output", type=Path, default=OUTPUT_EXCEL, help="Output Excel workbook.")
    parser.add_argument("--json-report", type=Path, default=OUTPUT_JSON, help="Output JSON audit report.")
    parser.add_argument(
        "--scope",
        choices=SCOPE_OPTIONS,
        default="pending",
        help="pending=notyet only; broad=notyet/consider/unverified; all=all cards.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_REVIEW_LIMIT,
        help="Maximum cards to export; use 0 for no limit.",
    )
    args = parser.parse_args(argv)
    return WorkflowConfig(
        master=args.master,
        output=args.output,
        json_report=args.json_report,
        scope=args.scope,
        limit=args.limit,
    )


def main(argv: list[str] | None = None) -> int:
    configure_utf8_stdio()
    config = parse_args(argv)

    logger.info("=" * 60)
    logger.info("BATCH EVIDENCE QUALITY CHECK - Q1-Q7")
    logger.info("=" * 60)

    cards = load_evidence_db(config.master)
    logger.info("Loaded %s evidence cards", len(cards))

    review_cards = filter_cards_for_review(cards, scope=config.scope, limit=config.limit)
    if not review_cards:
        logger.warning("No cards for review found.")
        return 0

    results = run_quality_check_batch(review_cards)
    report = build_report(results, total_cards=len(cards), selected_cards=len(review_cards), config=config)

    logger.info("Classification distribution:")
    for classify, count in sorted(report["classification_distribution"].items()):
        logger.info("  %s: %s cards", classify, count)

    export_to_excel(results, config)
    write_json_report(report, config)

    logger.info("=" * 60)
    logger.info("DONE - %s cards checked", len(results))
    logger.info("Excel: %s", config.output)
    logger.info("JSON: %s", config.json_report)
    logger.info("Doctor next step: fill Doctor Decision in Excel, then run process_approved_evidence.py.")
    logger.info("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
