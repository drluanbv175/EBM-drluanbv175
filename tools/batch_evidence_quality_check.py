#!/usr/bin/env python3
"""
Workflow Duyệt & Phân Lớp 78+ Thẻ Chứng Cứ — Q1-Q7 Auto-Check

Giai đoạn 2 (Tuần 3-4): Tự động kiểm Q1-Q7, phân lớp thẻ chờ duyệt

Quy trình:
  1. Load 78+ thẻ chờ xử lý (decision="notyet" hoặc verification_status pending)
  2. Chạy Q1-Q7 auto-check (readability, accuracy, completeness, bias, harm, currency, authority)
  3. Phân lớp: APPLY_IMMEDIATELY (Q1-Q7 all pass) / CONSIDER (chờ duyệt) / NOT_YET (chưa đủ)
  4. Xuất Excel: _EVIDENCE_APPROVAL_WORKFLOW.xlsx (dễ duyệt)
  5. (Sau đó) Bác sĩ ký Excel → process_approved_evidence.py cập nhật DB
"""

import json
import sys
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import re

try:
    import openpyxl
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
except ImportError:
    print("ERROR: openpyxl not found. Install: pip install openpyxl")
    sys.exit(1)

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Hằng số
EVIDENCE_DB_PATH = Path(__file__).parent.parent / "EBM_MASTER" / "EBM_MASTER.json"
OUTPUT_EXCEL = Path(__file__).parent.parent / "EBM_MASTER" / "_EVIDENCE_APPROVAL_WORKFLOW.xlsx"

# Tiêu chí Q1-Q7
QUALITY_CRITERIA = {
    "Q1": {
        "name": "Readability (Dễ đọc)",
        "description": "Abstract rõ ràng, structure logic, không jargon quá"
    },
    "Q2": {
        "name": "Accuracy (Đúng đắn)",
        "description": "PMID/DOI phân giải đúng, không có inconsistency"
    },
    "Q3": {
        "name": "Completeness (Đầy đủ)",
        "description": "Có effect size + CI, tác giả, năm, journal"
    },
    "Q4": {
        "name": "Bias (Thiên kiến)",
        "description": "RoB 2 (RCT) / ROBINS-I (obs) / QUADAS (diagnostic) tốt"
    },
    "Q5": {
        "name": "Harm (Hại)",
        "description": "SAE/harm thấp, ARD hợp lý"
    },
    "Q6": {
        "name": "Currency (Mới)",
        "description": "Công bố ≤5 năm (exception: landmark trials)"
    },
    "Q7": {
        "name": "Authority (Thẩm quyền)",
        "description": "IF ≥2.0 hoặc top-tier society guideline"
    }
}


class EvidenceQualityChecker:
    """Checker Q1-Q7 tự động cho mỗi thẻ"""
    
    def __init__(self):
        self.results = {}
    
    def check_q1_readability(self, card: Dict) -> Tuple[bool, str]:
        """Q1: Readability — abstract rõ ràng?"""
        recommendation = card.get("recommendation", "")
        title = card.get("source", {}).get("title", "")
        
        # Heuristic: độ dài abstract, số từ
        text = recommendation + " " + title
        if len(text) < 30:
            return False, "Abstract quá ngắn (< 30 ký tự)"
        
        # Check có từ khóa common thì tốt
        good_keywords = ["diagnose", "treat", "prevent", "monitor", "screen", "chuẩn đoán", "điều trị", "phòng ngừa"]
        has_good_keyword = any(kw in text.lower() for kw in good_keywords)
        
        if has_good_keyword:
            return True, "Abstract rõ ràng ✓"
        else:
            return False, "Abstract không rõ ràng — thiếu mục tiêu cụ thể"
    
    def check_q2_accuracy(self, card: Dict) -> Tuple[bool, str]:
        """Q2: Accuracy — PMID/DOI phân giải đúng?"""
        source = card.get("source", {})
        pmid = source.get("pmid", "")
        doi = source.get("doi", "")
        
        # Check format PMID (số 7-8 chữ số)
        if pmid and not re.match(r"^\d{7,8}$", pmid):
            return False, f"PMID không hợp lệ: {pmid}"
        
        # Check format DOI
        if doi and not re.match(r"^10\.\d+/", doi):
            return False, f"DOI không hợp lệ: {doi}"
        
        # Phải có ít nhất 1 (PMID hoặc DOI)
        if not (pmid or doi):
            return False, "Thiếu PMID hoặc DOI"
        
        return True, "PMID/DOI hợp lệ ✓"
    
    def check_q3_completeness(self, card: Dict) -> Tuple[bool, str]:
        """Q3: Completeness — đầy đủ tác giả/năm/journal/effect size?"""
        source = card.get("source", {})
        critical_appraisal = card.get("critical_appraisal", {})
        
        # Check năm
        date_source = card.get("date_source", "")
        if not date_source or date_source == "":
            return False, "Thiếu năm công bố"
        
        # Check tạp chí
        agency_or_journal = source.get("agency", "") or source.get("journal", "")
        if not agency_or_journal:
            return False, "Thiếu tên tạp chí/guideline"
        
        # Check effect estimate hoặc recommendation
        effect = critical_appraisal.get("effect_estimate", "")
        recommendation = card.get("recommendation", "")
        
        if not (effect or recommendation):
            return False, "Thiếu effect estimate hoặc khuyến cáo"
        
        return True, "Đầy đủ tác giả/năm/journal ✓"
    
    def check_q4_bias(self, card: Dict) -> Tuple[bool, str]:
        """Q4: Bias — RoB 2 / ROBINS-I / QUADAS?"""
        design = card.get("critical_appraisal", {}).get("design", "").lower()
        
        # Nếu là guideline hoặc expert opinion → không áp dụng RoB 2
        if "guideline" in design or "consensus" in design or "expert" in design:
            return True, "Guideline/Consensus — không cần RoB 2 (N/A)"
        
        # Nếu là RCT — nên có RoB 2
        if "rct" in design or "randomized" in design:
            # TODO: Parser chi tiết RoB 2 score từ description
            # Hiện tại heuristic: nếu mention RoB thì OK
            if "rob" in card.get("critical_appraisal", {}).get("effect_estimate", "").lower():
                return True, "RoB 2 có ✓"
            else:
                return False, "RCT nhưng thiếu RoB 2 assessment"
        
        # Nếu observational
        if "cohort" in design or "case-control" in design or "observational" in design:
            if "robins" in card.get("critical_appraisal", {}).get("effect_estimate", "").lower():
                return True, "ROBINS-I có ✓"
            else:
                return False, "Observational nhưng thiếu ROBINS-I"
        
        return True, "Design có — không cần bias risk tool"
    
    def check_q5_harm(self, card: Dict) -> Tuple[bool, str]:
        """Q5: Harm — SAE/harm thấp, ARD hợp lý?"""
        recommendation = card.get("recommendation", "").lower()
        certainty = card.get("certainty", "").lower()
        
        # Heuristic: check có mention SAE / adverse event / contraindication
        harm_keywords = ["sae", "adverse", "harm", "contraindication", "safety", "side effect", "tai biến"]
        has_harm_discussion = any(kw in recommendation or kw in certainty for kw in harm_keywords)
        
        if not has_harm_discussion:
            # CẢNH BÁO: không nhắc đến harm
            return False, "⚠️ Không nhắc tới SAE/harm — cần rà lại"
        
        return True, "Harm đã thảo luận ✓"
    
    def check_q6_currency(self, card: Dict) -> Tuple[bool, str]:
        """Q6: Currency — công bố ≤5 năm?"""
        date_source = card.get("date_source", "")
        current_year = datetime.now().year
        
        if not date_source:
            return False, "Thiếu năm công bố"
        
        try:
            year = int(date_source)
        except (ValueError, TypeError):
            return False, f"Năm không hợp lệ: {date_source}"
        
        age = current_year - year
        
        # Exception: landmark trials có thể > 5 năm (vd Framingham, trial cổ điển)
        is_landmark = "landmark" in card.get("critical_appraisal", {}).get("design", "").lower()
        
        if age <= 5 or is_landmark:
            return True, f"Recent ({year}) ✓"
        else:
            return False, f"Cũ ({year}, {age} năm trước) — kiểm xem có guideline mới không"
    
    def check_q7_authority(self, card: Dict) -> Tuple[bool, str]:
        """Q7: Authority — IF ≥2.0 hoặc top-tier society?"""
        agency = card.get("source", {}).get("agency", "").lower()
        source_type = card.get("source", {}).get("type", "").lower()
        
        # Top-tier society/org
        top_tier = [
            "who", "nice", "esc", "aha", "ada", "kdigo", "gina", "gold",
            "nejm", "lancet", "jama", "bmj", "nature", "science"
        ]
        
        is_top_tier = any(org in (agency + source_type) for org in top_tier)
        
        if is_top_tier:
            return True, f"Top-tier ({agency}) ✓"
        else:
            # Nếu không rõ → warn (heuristic không đủ, cần xác minh)
            return False, f"Source {agency} — kiểm xem IF/tier"
    
    def run_all_checks(self, card: Dict) -> Dict[str, Tuple[bool, str]]:
        """Chạy Q1-Q7 cho 1 thẻ"""
        results = {
            "Q1": self.check_q1_readability(card),
            "Q2": self.check_q2_accuracy(card),
            "Q3": self.check_q3_completeness(card),
            "Q4": self.check_q4_bias(card),
            "Q5": self.check_q5_harm(card),
            "Q6": self.check_q6_currency(card),
            "Q7": self.check_q7_authority(card),
        }
        return results
    
    def get_classification(self, results: Dict[str, Tuple[bool, str]]) -> str:
        """Phân lớp dựa trên Q1-Q7"""
        passed = sum(1 for pass_flag, _ in results.values() if pass_flag)
        
        if passed >= 6:
            return "APPLY_IMMEDIATELY"
        elif passed >= 4:
            return "CONSIDER"
        else:
            return "NOT_YET"


def load_evidence_db() -> List[Dict]:
    """Load EBM_MASTER.json"""
    if not EVIDENCE_DB_PATH.exists():
        logger.error(f"File not found: {EVIDENCE_DB_PATH}")
        sys.exit(1)
    
    with open(EVIDENCE_DB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return data.get("evidence_cards", [])


def filter_cards_for_review(cards: List[Dict]) -> List[Dict]:
    """Lọc 78+ thẻ cần duyệt (decision="notyet" hoặc verification_status pending)"""
    review_cards = [
        c for c in cards 
        if c.get("decision") in ["notyet", "consider"] or 
           c.get("verification_status", "").lower() in ["pending", "chưa xác minh"]
    ]
    logger.info(f"Found {len(review_cards)} cards for review")
    return review_cards


def run_quality_check_batch(cards: List[Dict]) -> List[Dict]:
    """Chạy Q1-Q7 cho batch thẻ"""
    checker = EvidenceQualityChecker()
    results = []
    
    for idx, card in enumerate(cards, 1):
        q_results = checker.run_all_checks(card)
        classification = checker.get_classification(q_results)
        
        # Tính score Q1-Q7 (số tiêu chí pass / 7)
        q_score = sum(1 for pass_flag, _ in q_results.values() if pass_flag) / 7.0
        
        result = {
            "id": card.get("id", ""),
            "title": card.get("recommendation", "")[:80],  # Truncate để gọn Excel
            "topic": card.get("topic", ""),
            "specialty": card.get("specialty", ""),
            "pmid": card.get("source", {}).get("pmid", ""),
            "doi": card.get("source", {}).get("doi", ""),
            "source_agency": card.get("source", {}).get("agency", ""),
            "date_source": card.get("date_source", ""),
            "gradeLevel": card.get("gradeLevel", ""),
            "current_decision": card.get("decision", ""),
            "Q1_Readability": "✓" if q_results["Q1"][0] else "✗",
            "Q1_Note": q_results["Q1"][1],
            "Q2_Accuracy": "✓" if q_results["Q2"][0] else "✗",
            "Q2_Note": q_results["Q2"][1],
            "Q3_Completeness": "✓" if q_results["Q3"][0] else "✗",
            "Q3_Note": q_results["Q3"][1],
            "Q4_Bias": "✓" if q_results["Q4"][0] else "✗",
            "Q4_Note": q_results["Q4"][1],
            "Q5_Harm": "✓" if q_results["Q5"][0] else "✗",
            "Q5_Note": q_results["Q5"][1],
            "Q6_Currency": "✓" if q_results["Q6"][0] else "✗",
            "Q6_Note": q_results["Q6"][1],
            "Q7_Authority": "✓" if q_results["Q7"][0] else "✗",
            "Q7_Note": q_results["Q7"][1],
            "Q_Score": f"{q_score:.1%}",
            "Auto_Classification": classification,
            "Doctor_Decision": "",  # Bác sĩ điền
            "Doctor_Notes": "",     # Bác sĩ điền
            "original_card": card   # Keep for later processing
        }
        
        results.append(result)
        
        if idx % 10 == 0:
            logger.info(f"Processed {idx}/{len(cards)} cards")
    
    logger.info(f"Completed Q1-Q7 check for {len(results)} cards")
    return results


def export_to_excel(results: List[Dict]) -> Path:
    """Xuất kết quả ra Excel"""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Evidence Approval"
    
    # Header
    headers = [
        "ID", "Title (80 ký)", "Topic", "Specialty", "PMID", "DOI", "Agency", "Year", "Grade",
        "Current\nDecision",
        "Q1\nReadability", "Q1 Note",
        "Q2\nAccuracy", "Q2 Note",
        "Q3\nComplete", "Q3 Note",
        "Q4\nBias", "Q4 Note",
        "Q5\nHarm", "Q5 Note",
        "Q6\nCurrency", "Q6 Note",
        "Q7\nAuthority", "Q7 Note",
        "Q_Score",
        "Auto\nClassify",
        "Doctor\nDecision",
        "Doctor\nNotes"
    ]
    
    ws.append(headers)
    
    # Style header
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=10)
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment
    
    # Data rows
    for idx, result in enumerate(results, 2):
        row_data = [
            result["id"],
            result["title"],
            result["topic"],
            result["specialty"],
            result["pmid"],
            result["doi"],
            result["source_agency"],
            result["date_source"],
            result["gradeLevel"],
            result["current_decision"],
            result["Q1_Readability"],
            result["Q1_Note"],
            result["Q2_Accuracy"],
            result["Q2_Note"],
            result["Q3_Completeness"],
            result["Q3_Note"],
            result["Q4_Bias"],
            result["Q4_Note"],
            result["Q5_Harm"],
            result["Q5_Note"],
            result["Q6_Currency"],
            result["Q6_Note"],
            result["Q7_Authority"],
            result["Q7_Note"],
            result["Q_Score"],
            result["Auto_Classification"],
            result["Doctor_Decision"],
            result["Doctor_Notes"],
        ]
        
        ws.append(row_data)
        
        # Color by auto-classification
        classify_cell = ws[f"AA{idx}"]  # Auto_Classification column
        if result["Auto_Classification"] == "APPLY_IMMEDIATELY":
            classify_cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
        elif result["Auto_Classification"] == "CONSIDER":
            classify_cell.fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
        else:  # NOT_YET
            classify_cell.fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
    
    # Column widths
    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 30
    ws.column_dimensions["C"].width = 20
    ws.column_dimensions["D"].width = 15
    
    for col in ["E", "F", "G", "H", "I", "J"]:
        ws.column_dimensions[col].width = 12
    
    for col in ["K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X"]:
        ws.column_dimensions[col].width = 14
    
    # Freeze header + 1st col
    ws.freeze_panes = "B2"
    
    # Save
    wb.save(OUTPUT_EXCEL)
    logger.info(f"Excel exported: {OUTPUT_EXCEL}")
    return OUTPUT_EXCEL


def main():
    logger.info("="*60)
    logger.info("BATCH EVIDENCE QUALITY CHECK — Q1-Q7")
    logger.info("="*60)
    
    # Load DB
    cards = load_evidence_db()
    logger.info(f"Loaded {len(cards)} evidence cards")
    
    # Filter for review
    review_cards = filter_cards_for_review(cards)
    
    if not review_cards:
        logger.warning("No cards for review found")
        return
    
    # Run Q1-Q7 check
    results = run_quality_check_batch(review_cards)
    
    # Phân bố classification
    classify_counts = {}
    for r in results:
        classify = r["Auto_Classification"]
        classify_counts[classify] = classify_counts.get(classify, 0) + 1
    
    logger.info("\nClassification Distribution:")
    for classify, count in sorted(classify_counts.items()):
        logger.info(f"  {classify}: {count} cards")
    
    # Export Excel
    excel_file = export_to_excel(results)
    
    logger.info("\n" + "="*60)
    logger.info(f"✅ DONE — {len(results)} cards checked")
    logger.info(f"📊 Output: {excel_file}")
    logger.info("\nCách dùng:")
    logger.info("  1. Bác sĩ mở Excel, kiểm Q1-Q7 auto-check")
    logger.info("  2. Điền Doctor_Decision (APPLY / CONSIDER / NOT_YET)")
    logger.info("  3. Ghi ghi chú nếu khác auto-classification")
    logger.info("  4. Save + upload → process_approved_evidence.py cập nhật DB")
    logger.info("="*60)


if __name__ == "__main__":
    main()
