#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""research_checks.py — 3 cổng kiểm ĐẶC THÙ NHÁNH NGHIÊN CỨU cho run_eval.py.

Vá khoảng hở D1 của scorecard nghiên cứu 2026-07-08: cổng QA (`run_eval.py`) TRƯỚC đây
KHÔNG có check chuẩn báo cáo / kiểm định lệch / khai báo AI (grep = 0). Module này bổ sung
3 mã ledger mới (khớp `_LESSONS-LEDGER-TAXONOMY.md` §2, rubric research §0):

    STD-REPORT    — sai/thiếu chuẩn báo cáo theo thiết kế (CONSORT/STROBE/PRISMA/SPIRIT/STARD/TRIPOD)
    STAT-MISMATCH — kiểm định lệch loại biến/thiết kế; hoặc p đơn độc thiếu 95%CI (bao R8)
    AI-DISCLOSE   — thiếu khai báo dùng AI / tác giả ICMJE khi sinh bản thảo để công bố

THIẾT KẾ CHỐNG-VA-CHẠM: module ĐỘC LẬP, tự-test được (`python3 research_checks.py`), KHÔNG
sửa `run_eval.py` (đang bị phiên khác biên tập). Hòa mạng vào `run_eval.py::evaluate()` chỉ là
3 dòng (xem cuối file — mục WIRING). Vì tách file nên KHÔNG thể phá `test_classify.py` hiện có.

Mỗi check trả (id, ok, detail) TƯƠNG THÍCH danh sách `checks` của run_eval (list các (k, ok, _)).
Cả 3 là TIER-1: nếu fail thì `run_eval` phải TRẢ-VỀ-SỬA để không phát hành đầu ra nghiên
cứu sai chuẩn. Đây là return-for-fix có thể sửa được, không phải hard-escalate kiểu PII.

Nguyên tắc: bảo thủ (ưu tiên KHÔNG báo động giả). Chỉ kích hoạt khi bối cảnh rõ là báo cáo/
bản thảo/nộp bài; nếu không đủ tín hiệu → trả ok=True kèm 'n/a' (không áp dụng), không phạt.

Docstring/comment tiếng Việt theo quy ước dự án. KHÔNG PII. Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations
import re

# ── mã ledger (khớp _LESSONS-LEDGER-TAXONOMY.md §2b) ─────────────────────────
RESEARCH_CHECK_ID_TO_LEDGER = {
    "reporting_standard": "STD-REPORT",
    "stat_mismatch": "STAT-MISMATCH",
    "ai_disclosure": "AI-DISCLOSE",
}
# Cả 3 là tier-1 return-for-fix. Tên biến giữ theo schema lịch sử của run_eval
# (`red_fails` điều khiển verdict), nhưng đây không đồng nghĩa hard-escalate.
RESEARCH_RED_KEYS: set[str] = set(RESEARCH_CHECK_ID_TO_LEDGER)

# ── 1) CHUẨN BÁO CÁO theo thiết kế (STD-REPORT) ──────────────────────────────
# Bản đồ: loại thiết kế → chuẩn báo cáo ĐÚNG (bản hiện hành). Nguồn: EQUATOR Network.
#   RCT→CONSORT · quan sát (cohort/case-control/cross-sectional)→STROBE ·
#   SR/meta-analysis→PRISMA · protocol thử nghiệm→SPIRIT · độ chính xác chẩn đoán→STARD ·
#   mô hình tiên lượng/dự báo→TRIPOD(+AI)
_DESIGN_PATTERNS = [
    ("SR",          re.compile(r"tổng\s*quan\s*hệ\s*thống|systematic\s*review|meta[-\s]?analysis|phân\s*tích\s*gộp", re.I)),
    ("PROTOCOL",    re.compile(r"\b(?:đề\s*cương|protocol)\b.*\b(?:thử\s*nghiệm|trial|RCT|can\s*thiệp)\b|trial\s*protocol", re.I)),
    ("RCT",         re.compile(r"thử\s*nghiệm\s*(?:lâm\s*sàng\s*)?ngẫu\s*nhiên|randomi[sz]ed\s*controlled|\bRCT\b|ngẫu\s*nhiên\s*có\s*đối\s*chứng", re.I)),
    ("DIAGNOSTIC",  re.compile(r"độ\s*chính\s*xác\s*chẩn\s*đoán|diagnostic\s*(?:test\s*)?accuracy|độ\s*nhạy.*độ\s*đặc\s*hiệu", re.I)),
    ("PREDICTION",  re.compile(r"mô\s*hình\s*(?:tiên\s*lượng|dự\s*báo|dự\s*đoán)|prediction\s*model|prognostic\s*model|nomogram", re.I)),
    ("OBS",         re.compile(r"đoàn\s*hệ|cohort|bệnh[-\s]?chứng|case[-\s]?control|cắt\s*ngang|cross[-\s]?sectional|nghiên\s*cứu\s*quan\s*sát|observational", re.I)),
]
_DESIGN_TO_STANDARD = {
    "SR": "PRISMA", "PROTOCOL": "SPIRIT", "RCT": "CONSORT",
    "DIAGNOSTIC": "STARD", "PREDICTION": "TRIPOD", "OBS": "STROBE",
}
_STANDARD_PATTERNS = {
    "CONSORT": re.compile(r"\bCONSORT\b", re.I),
    "STROBE":  re.compile(r"\bSTROBE\b", re.I),
    "PRISMA":  re.compile(r"\bPRISMA\b", re.I),
    "SPIRIT":  re.compile(r"\bSPIRIT\b", re.I),
    "STARD":   re.compile(r"\bSTARD\b", re.I),
    "TRIPOD":  re.compile(r"\bTRIPOD(?:\+?AI)?\b", re.I),
}
# Bối cảnh "đang chọn/viết chuẩn báo cáo hoặc bản thảo" → mới xét STD-REPORT.
_REPORTING_CONTEXT = re.compile(
    r"chuẩn\s*báo\s*cáo|reporting\s*(?:standard|guideline|checklist)|checklist|"
    r"bản\s*thảo|manuscript|IMRAD|viết\s*bài|nộp\s*(?:bài|tạp\s*chí)|EQUATOR", re.I)


def _detect_designs(text: str) -> list[str]:
    """Trả TẤT CẢ họ thiết kế khớp (để nhận diện bối cảnh 'nhiều thiết kế' = checklist/bàn luận)."""
    return [name for name, pat in _DESIGN_PATTERNS if pat.search(text)]


def check_reporting_standard(text: str, gold: dict | None = None):
    """STD-REPORT: nếu bối cảnh là báo cáo/bản thảo và có nêu MỘT thiết kế → chuẩn báo cáo phải ĐÚNG.

    - Không phát hiện thiết kế → n/a (ok).
    - NHIỀU họ thiết kế cùng xuất hiện (thường là checklist/bàn luận, vd liệt kê
      'CONSORT(RCT)/STROBE(quan sát)/PRISMA(SR)') → n/a để TRÁNH BÁO ĐỘNG GIẢ (bảo thủ).
    - Không phải bối cảnh báo cáo và không nêu chuẩn nào → n/a (tránh báo động giả).
    - Nêu ĐÚNG chuẩn kỳ vọng → ĐẠT.
    - Nêu SAI chuẩn (khác kỳ vọng) → RỚT.
    - Bối cảnh báo cáo + có thiết kế nhưng KHÔNG nêu chuẩn nào → RỚT (thiếu chuẩn).
    """
    designs = _detect_designs(text)
    if not designs:
        return ("reporting_standard", True, "n/a — không nêu loại thiết kế")
    if len(set(designs)) > 1:
        return ("reporting_standard", True,
                f"n/a — nhiều họ thiết kế cùng nêu {sorted(set(designs))} (checklist/bàn luận, không phán)")
    design = designs[0]
    expected = _DESIGN_TO_STANDARD[design]
    named = [s for s, pat in _STANDARD_PATTERNS.items() if pat.search(text)]
    in_report_ctx = bool(_REPORTING_CONTEXT.search(text))

    if expected in named:
        return ("reporting_standard", True, f"ĐẠT — thiết kế {design} ↔ đúng chuẩn {expected}")
    wrong = [s for s in named if s != expected]
    if wrong:
        return ("reporting_standard", False,
                f"SAI chuẩn báo cáo: nêu {wrong} nhưng thiết kế {design} cần {expected}")
    # không nêu chuẩn nào:
    if in_report_ctx:
        return ("reporting_standard", False,
                f"THIẾU chuẩn báo cáo: thiết kế {design} cần nêu {expected} (bối cảnh viết/nộp)")
    return ("reporting_standard", True, f"n/a — có {design} nhưng không phải bối cảnh chọn chuẩn")


# ── 2) KIỂM ĐỊNH LỆCH loại biến/thiết kế (STAT-MISMATCH) ─────────────────────
_TTEST = re.compile(r"\bt[-\s]?test\b|independent[-\s]?samples?\s*t|kiểm\s*định\s*t\b|student'?s?\s*t", re.I)
# biến nhị phân/tỷ lệ làm KẾT CỤC của so sánh t-test
_BINARY_OUTCOME = re.compile(
    r"tỷ\s*lệ|proportion|nhị\s*phân|\bbinary\b|có\s*/\s*không|\(có/không\)|"
    r"đáp\s*ứng\s*\(?có|biến\s*cố\s*\(?có|categorical|phân\s*loại", re.I)
# >2 nhóm
_MULTI_GROUP = re.compile(r"\b3\s*nhóm\b|ba\s*nhóm|>?\s*2\s*nhóm|nhiều\s*nhóm|three\s*groups?|multiple\s*groups?", re.I)
# t-test từng cặp / nhiều lần t-test
_PAIRWISE_TTEST = re.compile(
    r"t[-\s]?test\s*(?:từng\s*cặp|cặp|pairwise)|(?:từng\s*cặp|pairwise)\s*t[-\s]?test|"
    r"\b\d+\s*t[-\s]?test\b|nhiều\s*t[-\s]?test|các\s*t[-\s]?test", re.I)
# đã hiệu chỉnh / dùng omnibus đúng → KHÔNG phạt
_CORRECTED = re.compile(
    r"Bonferroni|Holm|Tukey|Dunn|Šidák|Sidak|hiệu\s*chỉnh\s*(?:đa\s*so\s*sánh|bội)|"
    r"ANOVA|Kruskal[-\s]?Wallis|correction\s*for\s*multiple", re.I)
# đúng kiểm định cho biến nhị phân → KHÔNG phạt (nếu chỉ dùng cái đúng)
_CORRECT_CAT_TEST = re.compile(r"chi[-\s]?bình\s*phương|chi[-\s]?squared?|χ²|fisher|logistic", re.I)
# p-value trần và có/không có 95%CI (bao R8)
_PVALUE_BARE = re.compile(r"\bp\s*[<=>]\s*0?\.\d+|\bp\s*[<=>]\s*\d|p[-\s]?value", re.I)
_CI95 = re.compile(r"95%\s*(?:CI|KTC|khoảng\s*tin\s*cậy)|KTC\s*95%|CI\s*95%|khoảng\s*tin\s*cậy\s*95", re.I)
_EFFECT_SIZE = re.compile(
    r"\b(?:OR|RR|HR|MD|SMD|hazard\s*ratio|odds\s*ratio|risk\s*ratio|effect\s*size|"
    r"cỡ\s*hiệu\s*ứng|chênh\s*lệch\s*trung\s*bình|mean\s*difference)\b", re.I)


def check_stat_mismatch(text: str, gold: dict | None = None):
    """STAT-MISMATCH: bắt (a) t-test cho biến nhị phân, (b) đa t-test không hiệu chỉnh,
    (c) p đơn độc thiếu 95%CI/effect size. RỚT nếu bất kỳ tín hiệu nào bật."""
    problems = []

    # (a) t-test trên biến nhị phân/tỷ lệ, mà KHÔNG dùng kiểm định phân loại đúng
    if _TTEST.search(text) and _BINARY_OUTCOME.search(text) and not _CORRECT_CAT_TEST.search(text):
        problems.append("t-test cho biến nhị phân/tỷ lệ (cần χ²/Fisher/logistic)")

    # (b) so sánh >2 nhóm bằng nhiều t-test từng cặp không hiệu chỉnh
    multi = _MULTI_GROUP.search(text) or _PAIRWISE_TTEST.search(text)
    if _TTEST.search(text) and _PAIRWISE_TTEST.search(text) and multi and not _CORRECTED.search(text):
        problems.append("đa so sánh t-test từng cặp không hiệu chỉnh (cần omnibus ANOVA/Kruskal + hậu kiểm)")

    # (c) p-value trần thiếu 95%CI VÀ thiếu effect size (bao R8)
    if _PVALUE_BARE.search(text) and not _CI95.search(text) and not _EFFECT_SIZE.search(text):
        problems.append("p-value đơn độc thiếu 95%CI/effect size (R8)")

    if problems:
        return ("stat_mismatch", False, "; ".join(problems))
    if not _PVALUE_BARE.search(text) and not _TTEST.search(text):
        return ("stat_mismatch", True, "n/a — không có nội dung thống kê để kiểm")
    return ("stat_mismatch", True, "ĐẠT — không phát hiện kiểm định lệch")


# ── 3) KHAI BÁO AI + tác giả ICMJE (AI-DISCLOSE) ─────────────────────────────
_AI_USE = re.compile(
    r"dùng\s*AI|sử\s*dụng\s*AI|mô\s*hình\s*ngôn\s*ngữ|LLM\b|ChatGPT|generative\s*AI|"
    r"trí\s*tuệ\s*nhân\s*tạo|AI\s*hỗ\s*trợ|công\s*cụ\s*AI|do\s*AI\s*(?:soạn|viết|sinh)", re.I)
_PUBLISH_CTX = re.compile(
    r"nộp\s*(?:bài|tạp\s*chí)|tạp\s*chí|cover\s*letter|bản\s*thảo|manuscript|công\s*bố|"
    r"submission|đăng\s*bài|xuất\s*bản|peer\s*review|bình\s*duyệt", re.I)
_AI_DISCLOSED = re.compile(
    r"khai\s*báo\s*(?:dùng\s*)?AI|khai\s*báo\s*sử\s*dụng\s*AI|ICMJE|"
    r"AI\s*(?:không\s*(?:được\s*)?(?:là|đứng\s*tên|làm)\s*(?:tác\s*giả|đồng\s*tác\s*giả))|"
    r"declaration\s*of\s*(?:generative\s*)?AI|disclos\w*\s*AI|AI\s*disclosure|"
    r"không\s*được\s*là\s*tác\s*giả|generative\s*AI\s*in\s*(?:scientific\s*)?writing", re.I)


def check_ai_disclosure(text: str, gold: dict | None = None):
    """AI-DISCLOSE: nếu nêu DÙNG AI trong bối cảnh công bố/nộp bài → PHẢI có khai báo AI +
    ghi nhận AI không đứng tên tác giả (ICMJE). Thiếu → RỚT."""
    if not (_AI_USE.search(text) and _PUBLISH_CTX.search(text)):
        return ("ai_disclosure", True, "n/a — không nêu dùng AI trong bối cảnh công bố")
    if _AI_DISCLOSED.search(text):
        return ("ai_disclosure", True, "ĐẠT — có nhắc khai báo AI/ICMJE")
    return ("ai_disclosure", False,
            "THIẾU khai báo AI: nêu dùng AI để công bố nhưng không nhắc khai báo ICMJE / AI không đứng tên tác giả")


# ── API hòa mạng ─────────────────────────────────────────────────────────────
RESEARCH_CHECKS = (check_reporting_standard, check_stat_mismatch, check_ai_disclosure)


def research_checks(text: str, gold: dict | None = None) -> list[tuple[str, bool, str]]:
    """Trả list (id, ok, detail) — dán thẳng vào `checks` của run_eval.py::evaluate()."""
    return [fn(text, gold) for fn in RESEARCH_CHECKS]


# ── WIRING (dán vào run_eval.py khi file rảnh — 3 chỗ) ───────────────────────
#   (1) đầu file:      from research_checks import research_checks, RESEARCH_CHECK_ID_TO_LEDGER
#   (2) trong evaluate(), ngay trước dòng tính red_fails:
#          checks += research_checks(text, gold)
#   (3) hợp nhất map cho emit_appraisal/classify:
#          CHECK_ID_TO_RCODE.update(RESEARCH_CHECK_ID_TO_LEDGER)
#   → 3 mã mới nằm trong RESEARCH_RED_KEYS ⇒ verdict thành "TRẢ-VỀ-SỬA" (tier-1),
#      nhưng orchestrator vẫn định tuyến sửa, không hard-escalate.


# ── TỰ-TEST (verify-by-running; bài học dự án: không tin báo cáo, phải CHẠY) ──
def _selftest() -> int:
    """Chạy 3 check trên cặp BAD (phải RỚT) / GOOD (phải ĐẠT) mô phỏng probe RS-A2/A7/A9."""
    cases = [
        # (mô tả, text, check_fn, kỳ vọng ok?)
        ("RS-A2 STD-REPORT bad (cohort nhưng nêu CONSORT)",
         "Nghiên cứu đoàn hệ tiến cứu về tái nhập viện. Bản thảo tuân theo chuẩn báo cáo CONSORT.",
         check_reporting_standard, False),
        ("RS-A2 STD-REPORT good (cohort → STROBE)",
         "Nghiên cứu đoàn hệ tiến cứu; khi viết bản thảo tuân theo checklist STROBE (cohort).",
         check_reporting_standard, True),
        ("RS-A2 STD-REPORT n/a (không nêu thiết kế)",
         "Chúng tôi khảo sát mức độ hài lòng của người bệnh.",
         check_reporting_standard, True),
        ("RS-A7 STAT-MISMATCH bad (t-test cho tỷ lệ + đa t-test không hiệu chỉnh)",
         "So sánh tỷ lệ đáp ứng (có/không) giữa 2 nhóm bằng independent t-test, p=0.04. "
         "Ngoài ra chạy 3 t-test từng cặp giữa 3 nhóm VAS, đều p<0.05.",
         check_stat_mismatch, False),
        ("RS-A7 STAT-MISMATCH good (χ² + ANOVA/Tukey + CI)",
         "So sánh tỷ lệ đáp ứng bằng kiểm định chi-bình phương, p=0.04 (KTC 95% 1.02–1.5). "
         "So sánh 3 nhóm bằng ANOVA rồi hậu kiểm Tukey.",
         check_stat_mismatch, True),
        ("RS-A7 STAT-MISMATCH bad (p trần thiếu CI/effect size)",
         "Nhóm can thiệp cải thiện rõ so với chứng, p=0.003.",
         check_stat_mismatch, False),
        ("RS-A9 AI-DISCLOSE bad (dùng AI + nộp, không khai báo)",
         "Tôi đã dùng AI để soạn phần lớn bản thảo và chuẩn bị nộp tạp chí kèm cover letter.",
         check_ai_disclosure, False),
        ("RS-A9 AI-DISCLOSE good (có khai báo ICMJE)",
         "Tôi dùng AI soạn bản thảo để nộp tạp chí; đã khai báo dùng AI theo ICMJE và AI không đứng tên tác giả.",
         check_ai_disclosure, True),
        ("RS-A9 AI-DISCLOSE n/a (không dùng AI)",
         "Chuẩn bị nộp bản thảo cho tạp chí, kèm cover letter.",
         check_ai_disclosure, True),
    ]
    fails = 0
    for desc, text, fn, expect_ok in cases:
        cid, ok, detail = fn(text, None)
        status = "OK " if ok == expect_ok else "FAIL"
        if ok != expect_ok:
            fails += 1
        mark = "✅" if ok == expect_ok else "❌"
        print(f"{mark} [{status}] {desc}\n      → ({cid}, ok={ok}) {detail}")
    print(f"\n{'PASS' if fails == 0 else 'FAIL'} — {len(cases)-fails}/{len(cases)} case đúng kỳ vọng.")
    return 1 if fails else 0


if __name__ == "__main__":
    import sys
    sys.exit(_selftest())
