#!/usr/bin/env python3
"""build_research_readiness_evidence.py — xuất bảng chứng cứ sẵn sàng thực tiễn.

Công cụ này không tự tuyên bố hệ thống "hoàn hảo". Nó chạy một tập cổng kiểm
độc lập, lấy return code thật, rồi tạo bảng Markdown/JSON với:
- miền kiểm;
- lệnh/chứng cứ đã chạy;
- kết quả;
- điều chứng minh được;
- giới hạn trung thực còn lại.

Mục đích là biến câu trả lời "hệ đã áp dụng được chưa?" thành artifact kiểm
được, có thể commit/audit lại, thay vì một lời khẳng định thủ công.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Sequence

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT / "medical-ebm-automation"
DEFAULT_MD = ROOT / "reports" / "RESEARCH_READINESS_EVIDENCE.md"
DEFAULT_JSON = ROOT / "reports" / "RESEARCH_READINESS_EVIDENCE.json"


@dataclass(frozen=True)
class EvidenceCheck:
    domain: str
    command: List[str]
    proves: str
    limitation: str
    cwd: str = str(ROOT)
    blocking: bool = True


@dataclass(frozen=True)
class EvidenceRow:
    domain: str
    command: str
    status: str
    returncode: int
    evidence_tail: str
    proves: str
    limitation: str
    blocking: bool


CORE_CHECKS: List[EvidenceCheck] = [
    EvidenceCheck(
        domain="Agent sync Claude↔Codex",
        command=["tools/check_claude_codex_sync_health.py"],
        proves="50 agent nguồn và bản Codex sinh tự động có guardrail/disclaimer, không drift sync.",
        limitation="Chỉ kiểm cấu trúc file agent, không chứng minh chất lượng từng câu trả lời lâm sàng/nghiên cứu.",
    ),
    EvidenceCheck(
        domain="Định tuyến agent",
        command=["tools/verify_agent_routing.py"],
        proves="Nhạc trưởng tham chiếu đội agent thật, không có agent mồ côi hoặc tham chiếu treo.",
        limitation="Định tuyến là control-plane/deterministic; chưa phải thực thi LLM-agent thật ngoài môi trường hỗ trợ.",
    ),
    EvidenceCheck(
        domain="Hợp đồng gate nghiên cứu",
        command=["tools/verify_research_gate_contracts.py"],
        proves="Action queue/resume/release contract chặn G2/G6/G9 khi thiếu bằng chứng thật.",
        limitation="Dùng fixture synthetic; IRB/SAP/data-lock/liêm chính thật vẫn cần PI/bác sĩ xác nhận.",
    ),
    EvidenceCheck(
        domain="Luồng dữ liệu nghiên cứu thực tiễn",
        command=["tools/verify_research_practical_readiness.py"],
        proves="Raw PII bị chặn; de-id/pseudonymization, intake, cleaning, data-lock và audit G6 chạy được.",
        limitation="Dữ liệu synthetic; dữ liệu thật cần DMP/IRB, phân quyền, và kiểm định chất lượng tại đơn vị.",
    ),
    EvidenceCheck(
        domain="Tự động có kiểm soát: thẩm định-phản biện-PI/IRB-thống kê",
        command=["tools/verify_controlled_research_automation.py"],
        proves="Guardrail trả về sửa khi thiếu CI; automation không tự duyệt; role sai, thiếu mã reviewer giả danh và PII trong review bị chặn; review nhiều vai trò chỉ hoàn tất khi đủ PI/IRB/thống kê viên/phản biện; readiness tổng hợp vẫn BLOCKED nếu thiếu G2/G4/G9 đúng stakeholder; thống kê xuất effect size/CI và có DATA LOCK.",
        limitation="Fixture synthetic/offline; không thay thẩm định IRB, PI, thống kê viên, phản biện độc lập hoặc kiểm thử dữ liệu thật tại bệnh viện.",
    ),
    EvidenceCheck(
        domain="Scorecard hệ agent",
        command=["tools/assess_agent_system.py", "--deep"],
        proves="13 tiêu chí agent/hệ thống được probe bằng file, marker và lệnh thực thi.",
        limitation="Scorecard cấu trúc không thay phản biện chuyên gia hoặc đánh giá đầu ra mù độc lập.",
    ),
    EvidenceCheck(
        domain="Audit tổng thể",
        command=["tools/audit_ebm_system.py"],
        proves="Guardrail, dashboard/hub, evidence cards và audit vận hành đạt cổng tổng thể.",
        limitation="Không xác nhận mọi thẻ/chứng cứ là phù hợp cho một đề tài cụ thể nếu chưa rà theo protocol.",
    ),
]


FULL_TEST_CHECK = EvidenceCheck(
    domain="Full test repo sống",
    command=[sys.executable, "-m", "pytest"],
    cwd=str(REPO),
    proves="Bộ test hồi quy rộng của `medical-ebm-automation` chạy qua trong môi trường hiện tại.",
    limitation="Một số test online/golden có thể skipped; pytest không thay kiểm thử triển khai với dữ liệu thật tại bệnh viện.",
)


def _env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("PYTHONPYCACHEPREFIX", str(Path(tempfile.gettempdir()) / "ebm_pycache"))
    return env


def _tail(stdout: str, stderr: str, max_lines: int = 3) -> str:
    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    if not lines:
        lines = [line.strip() for line in stderr.splitlines() if line.strip()]
    selected = lines[-max_lines:] if lines else [""]
    return " / ".join(selected)[:500]


def _display_command(command: Sequence[str], cwd: str) -> str:
    prefix = "" if Path(cwd).resolve() == ROOT.resolve() else f"(cd {Path(cwd).name}) "
    return prefix + " ".join(command)


def run_check(check: EvidenceCheck, *, python: str) -> EvidenceRow:
    command = [python, *check.command] if check.command[0].endswith(".py") else list(check.command)
    proc = subprocess.run(
        command,
        cwd=check.cwd,
        env=_env(),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    status = "PASS" if proc.returncode == 0 else ("FAIL" if check.blocking else "WARN")
    return EvidenceRow(
        domain=check.domain,
        command=_display_command(command, check.cwd),
        status=status,
        returncode=proc.returncode,
        evidence_tail=_tail(proc.stdout or "", proc.stderr or ""),
        proves=check.proves,
        limitation=check.limitation,
        blocking=check.blocking,
    )


def build_report(*, include_full_pytest: bool = False,
                 python: str | None = None) -> dict:
    py = python or sys.executable
    checks = list(CORE_CHECKS)
    if include_full_pytest:
        checks.append(FULL_TEST_CHECK)
    rows = [run_check(check, python=py) for check in checks]
    blocking_failures = [row for row in rows if row.blocking and row.status != "PASS"]
    return {
        "kind": "research_readiness_evidence_report",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "overall_status": "PASS" if not blocking_failures else "FAIL",
        "blocking_failure_count": len(blocking_failures),
        "rows": [asdict(row) for row in rows],
        "disclaimer": (
            "Cần bác sĩ kiểm chứng. Đây là bảng chứng cứ kỹ thuật/guardrail, "
            "không thay IRB, PI, thống kê viên, phản biện độc lập hoặc thẩm định pháp lý."
        ),
    }


def _escape_cell(value: object) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", "<br>")


def markdown_report(report: dict) -> str:
    lines = [
        "# Bảng chứng cứ sẵn sàng thực tiễn hệ nghiên cứu y khoa",
        "",
        f"- Generated: `{report['generated_at']}`",
        f"- Overall status: `{report['overall_status']}`",
        f"- Blocking failures: `{report['blocking_failure_count']}`",
        "",
        "| Miền kiểm | Kết quả | Lệnh/chứng cứ | Dòng chứng cứ cuối | Chứng minh được | Giới hạn trung thực |",
        "|---|---|---|---|---|---|",
    ]
    for row in report["rows"]:
        lines.append(
            "| {domain} | {status} | `{command}` | {tail} | {proves} | {limit} |".format(
                domain=_escape_cell(row["domain"]),
                status=_escape_cell(row["status"]),
                command=_escape_cell(row["command"]),
                tail=_escape_cell(row["evidence_tail"]),
                proves=_escape_cell(row["proves"]),
                limit=_escape_cell(row["limitation"]),
            )
        )
    lines.extend([
        "",
        f"> {report['disclaimer']}",
        "",
    ])
    return "\n".join(lines)


def write_report(report: dict, *, out_md: Path, out_json: Path) -> None:
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(markdown_report(report), encoding="utf-8")
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def _print_summary(report: dict, out_md: Path, out_json: Path) -> None:
    print("Research readiness evidence report:", report["overall_status"])
    for row in report["rows"]:
        print(f"- {row['status']} {row['domain']}: {row['evidence_tail']}")
    print(f"Markdown: {out_md}")
    print(f"JSON: {out_json}")
    print(report["disclaimer"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--include-full-pytest", action="store_true",
                        help="Chạy thêm full pytest repo sống (chậm hơn).")
    parser.add_argument("--out-md", default=str(DEFAULT_MD))
    parser.add_argument("--out-json", default=str(DEFAULT_JSON))
    parser.add_argument("--json", action="store_true", help="In JSON ra stdout.")
    args = parser.parse_args()

    report = build_report(include_full_pytest=args.include_full_pytest)
    out_md = Path(args.out_md)
    out_json = Path(args.out_json)
    write_report(report, out_md=out_md, out_json=out_json)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        _print_summary(report, out_md, out_json)
    return 0 if report["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
