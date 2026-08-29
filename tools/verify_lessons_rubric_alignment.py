#!/usr/bin/env python3
"""Kiểm rubric QA và LESSONS taxonomy không lệch mã lỗi.

Mỗi mục rớt ở `_RUBRIC-EVALUATE-CUNG-QA-GATE.md` phải ghi được một `ma_loi`
có kiểm soát trong `_LESSONS-LEDGER-TAXONOMY.md`. Verifier này chặn tình huống
rubric thêm mã mới nhưng taxonomy chưa có, làm hở vòng Evaluate -> Learn.

Cần bác sĩ kiểm chứng: đây là kiểm cấu trúc mã lỗi, không thay đánh giá lâm sàng.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
RUBRIC = ROOT / ".claude" / "agents" / "_RUBRIC-EVALUATE-CUNG-QA-GATE.md"
TAXONOMY = ROOT / ".claude" / "agents" / "_LESSONS-LEDGER-TAXONOMY.md"
RETRY_LOOP_DIR = ROOT / "medical-ebm-automation" / "tools"
DEFAULT_MD = ROOT / "reports" / "LESSONS_RUBRIC_ALIGNMENT.md"
DEFAULT_JSON = ROOT / "reports" / "LESSONS_RUBRIC_ALIGNMENT.json"

CODE_RE = re.compile(r"`([A-Z][A-Z0-9]+(?:-[A-Z0-9]+)+)`")
STALE_GAP_RE = re.compile(r"CHƯA\s+có\s+hàng\s+tương\s+ứng|chưa\s+có\s+mã\s+ledger", re.I)


@dataclass(frozen=True)
class AlignmentReport:
    generated_at: str
    overall_status: str
    rubric_codes: list[str]
    taxonomy_codes: list[str]
    missing_in_taxonomy: list[str]
    missing_in_bridge: list[str]
    retry_loop_codes: dict[str, str]
    retry_loop_codes_missing_in_taxonomy: list[str]
    r1b_r6_distinct: bool
    stale_gap_note_found: bool
    disclaimer: str


def _section(text: str, start: str, end: str | None = None) -> str:
    i = text.find(start)
    if i == -1:
        return ""
    if end is None:
        return text[i:]
    j = text.find(end, i + len(start))
    return text[i:j] if j != -1 else text[i:]


def extract_codes(text: str) -> set[str]:
    return set(CODE_RE.findall(text))


def rubric_controlled_codes(rubric_text: str) -> set[str]:
    """Lấy mã TIER 0/1/2 trong rubric; bỏ các mã ví dụ ở phần vận hành sau đó."""
    block = _section(rubric_text, "## 3. TIER 0", "## 6. Bản ghi phán quyết")
    return extract_codes(block)


def taxonomy_table_codes(taxonomy_text: str) -> set[str]:
    """Chỉ lấy bảng taxonomy §2, không lấy các ví dụ/ghi chú bên dưới."""
    block = _section(taxonomy_text, "## 2. Taxonomy lỗi", "## 2b.")
    return extract_codes(block)


def taxonomy_bridge_codes(taxonomy_text: str) -> set[str]:
    """Lấy các mã có mặt trong bảng đối chiếu §2b."""
    block = _section(taxonomy_text, "## 2b.", "## 3. Schema")
    return extract_codes(block)


def retry_loop_lesson_codes() -> dict[str, str]:
    """Đọc bridge R-code -> LESSONS code từ retry_loop của repo sống."""
    # 28/08/2026 — repo y khoa nằm ngoài bản sao git gốc; thiếu thì khai báo rõ
    # thay vì ModuleNotFoundError trần (trông như lỗi mã, thật ra thiếu nguyên liệu).
    if not (RETRY_LOOP_DIR / "retry_loop.py").exists():
        raise SystemExit(
            "FAIL (bỏ qua CÓ KHAI BÁO): thiếu medical-ebm-automation/tools/retry_loop.py — "
            "repo y khoa không có trên bản sao git này; chạy trên máy có đủ hai repo.")
    if str(RETRY_LOOP_DIR) not in sys.path:
        sys.path.insert(0, str(RETRY_LOOP_DIR))
    import retry_loop  # noqa: PLC0415

    return dict(getattr(retry_loop, "RCODE_TO_LESSON_CODE", {}))


def _sorted(values: Iterable[str]) -> list[str]:
    return sorted(set(values))


def build_report() -> AlignmentReport:
    rubric_text = RUBRIC.read_text(encoding="utf-8")
    taxonomy_text = TAXONOMY.read_text(encoding="utf-8")
    rubric_codes = rubric_controlled_codes(rubric_text)
    taxonomy_codes = taxonomy_table_codes(taxonomy_text)
    bridge_codes = taxonomy_bridge_codes(taxonomy_text)
    retry_codes = retry_loop_lesson_codes()

    missing_in_taxonomy = rubric_codes - taxonomy_codes
    missing_in_bridge = rubric_codes - bridge_codes
    retry_missing = set(retry_codes.values()) - taxonomy_codes
    r1b_r6_distinct = (
        retry_codes.get("R1b") == "GAP-LABEL-WASH"
        and retry_codes.get("R6") == "GAP-MISSING"
        and retry_codes.get("R1b") != retry_codes.get("R6")
    )
    stale_gap_note_found = bool(STALE_GAP_RE.search(rubric_text + "\n" + taxonomy_text))
    ok = (
        not missing_in_taxonomy
        and not missing_in_bridge
        and not retry_missing
        and r1b_r6_distinct
        and not stale_gap_note_found
    )

    return AlignmentReport(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        overall_status="PASS" if ok else "FAIL",
        rubric_codes=_sorted(rubric_codes),
        taxonomy_codes=_sorted(taxonomy_codes),
        missing_in_taxonomy=_sorted(missing_in_taxonomy),
        missing_in_bridge=_sorted(missing_in_bridge),
        retry_loop_codes=dict(sorted(retry_codes.items())),
        retry_loop_codes_missing_in_taxonomy=_sorted(retry_missing),
        r1b_r6_distinct=r1b_r6_distinct,
        stale_gap_note_found=stale_gap_note_found,
        disclaimer=(
            "Cần bác sĩ kiểm chứng. Đây là kiểm cấu trúc mã lỗi rubric/taxonomy, "
            "không thay thẩm định chuyên môn hoặc quyết định lâm sàng."
        ),
    )


def markdown_report(report: AlignmentReport) -> str:
    rows = [
        ("Rubric codes", ", ".join(report.rubric_codes)),
        ("Taxonomy codes", ", ".join(report.taxonomy_codes)),
        ("Missing in taxonomy", ", ".join(report.missing_in_taxonomy) or "None"),
        ("Missing in bridge §2b", ", ".join(report.missing_in_bridge) or "None"),
        ("Retry loop codes missing in taxonomy", ", ".join(report.retry_loop_codes_missing_in_taxonomy) or "None"),
        ("R1b/R6 distinct", str(report.r1b_r6_distinct)),
        ("Stale gap note found", str(report.stale_gap_note_found)),
    ]
    lines = [
        "# Lessons Rubric Alignment",
        "",
        f"- Generated: `{report.generated_at}`",
        f"- Overall status: `{report.overall_status}`",
        "",
        "| Check | Evidence |",
        "|---|---|",
    ]
    for name, evidence in rows:
        escaped = evidence.replace("|", "\\|")
        lines.append(f"| {name} | {escaped} |")
    lines.extend(["", f"> {report.disclaimer}", ""])
    return "\n".join(lines)


def write_report(report: AlignmentReport, *, out_md: Path, out_json: Path) -> None:
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(markdown_report(report), encoding="utf-8")
    out_json.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-md", default=str(DEFAULT_MD))
    parser.add_argument("--out-json", default=str(DEFAULT_JSON))
    parser.add_argument("--no-write", action="store_true", help="Không ghi report vào reports/.")
    parser.add_argument("--json", action="store_true", help="In JSON ra stdout.")
    args = parser.parse_args(argv)

    report = build_report()
    if not args.no_write:
        write_report(report, out_md=Path(args.out_md), out_json=Path(args.out_json))
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print("Lessons rubric alignment:", report.overall_status)
        print(f"- rubric codes: {len(report.rubric_codes)}")
        print(f"- taxonomy codes: {len(report.taxonomy_codes)}")
        print(f"- missing in taxonomy: {', '.join(report.missing_in_taxonomy) or 'None'}")
        print(f"- missing in bridge: {', '.join(report.missing_in_bridge) or 'None'}")
        print(f"- retry loop missing in taxonomy: {', '.join(report.retry_loop_codes_missing_in_taxonomy) or 'None'}")
        print(f"- R1b/R6 distinct: {report.r1b_r6_distinct}")
        print(f"- stale gap note found: {report.stale_gap_note_found}")
        print(report.disclaimer)
    return 0 if report.overall_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
