#!/usr/bin/env python3
"""Kiểm dây chuyền cập nhật chứng cứ lâm sàng bằng fixture offline.

Verifier này không tuyên bố một khuyến cáo lâm sàng là đúng. Nó chỉ chứng minh
đường ống kỹ thuật đang chạy được, fail-closed ở các điểm quan trọng:
- dashboard Evidence Workbench có disclaimer, PMID/DOI/URL, gradeLevel, decision;
- dashboard Evidence Workbench có tab chuẩn chất lượng cập nhật chứng cứ (`standards`);
- dashboard qua cổng `verify_dashboard.py --strict-sources`;
- thư viện tích lũy `library.json` / `evidence-library.html` được sinh;
- 3 tài liệu phái sinh được sinh;
- `sync_all.py` còn hợp đồng gom dashboard qua cổng liêm chính và quarantine.

Dashboard thật vẫn phải chạy `verify_dashboard.py --online --strict-sources`, rà an toàn
thuốc khi liên quan và được bác sĩ duyệt trước khi áp dụng cho bệnh nhân.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
DASH_TOOLS = ROOT / "EBM-Dashboards" / "tools"
VERIFY_DASHBOARD = DASH_TOOLS / "verify_dashboard.py"
BUILD_LIBRARY = DASH_TOOLS / "build_library.py"
MAKE_DERIVATIVES = DASH_TOOLS / "make_derivatives.py"
SYNC_ALL = ROOT / "EBM_MASTER" / "tools" / "sync_all.py"
EW_TEMPLATE = ROOT / "dashboard_mockups" / "templates" / "evidence-workbench-template.html"
EW_HUB_ASSET = ROOT / "EBM_MASTER" / "skill_assets" / "web-dashboard-evidence-workbench.html"
EW_SKILL_TEMPLATE = ROOT / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "templates" / "web-dashboard-evidence-workbench.html"
EW_DARK_SKILL_TEMPLATE = ROOT / "sync" / "skills" / "dark-analyst" / "templates" / "web-dashboard-evidence-workbench.html"
DEFAULT_MD = ROOT / "reports" / "CLINICAL_EVIDENCE_UPDATE_PIPELINE.md"
DEFAULT_JSON = ROOT / "reports" / "CLINICAL_EVIDENCE_UPDATE_PIPELINE.json"

DISCLAIMER = "Cần bác sĩ kiểm chứng"
FIXTURE_DOI = "10.1136/bmj.c869"
FIXTURE_PMID = "20332511"


def _configure_utf8_stdio() -> None:
    """Keep Vietnamese verifier output printable on Windows legacy consoles."""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is not None and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass


_configure_utf8_stdio()


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: str
    evidence: str
    proves: str
    limitation: str
    blocking: bool = True


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
    return " / ".join(lines[-max_lines:] if lines else [""])[:600]


def _run(cmd: Sequence[str], *, cwd: Path) -> tuple[bool, str]:
    proc = subprocess.run(
        list(cmd),
        cwd=str(cwd),
        env=_env(),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.returncode == 0, _tail(proc.stdout or "", proc.stderr or "")


def _contains_all(path: Path, needles: Sequence[str]) -> tuple[bool, str]:
    if not path.exists():
        return False, f"THIẾU file {path}"
    text = path.read_text(encoding="utf-8", errors="ignore")
    missing = [needle for needle in needles if needle not in text]
    if missing:
        return False, "thiếu marker: " + ", ".join(missing[:6])
    return True, f"đủ {len(needles)}/{len(needles)} marker"


def _synthetic_dashboard_html(updated: str) -> str:
    """Sinh fixture không chứa PII; DOI thật chỉ dùng để kiểm đường ống."""
    return f"""<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8"/>
  <title>WebDashboard_EBM_VanDeCuThe_SyntheticClinicalEvidenceUpdate</title>
</head>
<body>
<main>
  <h1>Evidence Workbench - Synthetic clinical evidence update</h1>
  <p><strong>{DISCLAIMER}.</strong> Fixture này chỉ kiểm đường ống, không phải khuyến cáo điều trị.</p>
</main>
<script>
const DATA = {{
  meta: {{kind:'clinical-evidence-update', skin:'Evidence Workbench'}},
  question:'Synthetic clinical evidence update pipeline fixture',
  updated:'{updated}',
  eyebrow:'Evidence Workbench',
  conclusion:'Fixture offline dùng để kiểm cổng dashboard, thư viện chứng cứ và tài liệu phái sinh.',
  doNow:['Chỉ dùng fixture này để kiểm pipeline kỹ thuật, không dùng làm khuyến cáo điều trị.'],
  dontDo:['Không áp dụng fixture này cho bệnh nhân hoặc quy trình chăm sóc thật.'],
  redFlags:['Nếu đây là ca bệnh thật, bác sĩ phải đánh giá cấp cứu và bối cảnh người bệnh.'],
  standards:{{
    frame:'Câu hỏi có cấu trúc trước khi chọn nguồn.',
    sourceHierarchy:'Guideline chính thức, tổng quan hệ thống, thử nghiệm ngẫu nhiên và nguồn an toàn thuốc.',
    reporting:'CONSORT, STROBE, PRISMA, STARD, TRIPOD tùy thiết kế.',
    appraisal:'AGREE II, AMSTAR 2, RoB 2, ROBINS-I, QUADAS-3, PROBAST hoặc JBI.',
    currency:'Fixture offline cập nhật ngày {updated}; dashboard thật phải ghi ngày tìm kiếm.',
    searchSources:['PubMed','Cochrane','Guideline society'],
    sourceVerification:'Fixture PASS khi verify_dashboard.py --strict-sources chạy sạch; dashboard thật phải chạy thêm --online.',
    verificationTool:'verify_dashboard.py --online --strict-sources',
    lastVerified:'{updated}',
    safety:'Fixture không đưa khuyến cáo điều trị; dashboard thật phải rà chống chỉ định, tương tác, chuyển tuyến.',
    vietnamFit:'Dashboard thật phải đối chiếu sẵn có, chi phí/BHYT và năng lực theo dõi tại Việt Nam.',
    gates:[
      {{label:'Không PII',status:'ok',note:'Fixture không chứa dữ liệu người bệnh.'}},
      {{label:'Truy nguyên nguồn',status:'ok',note:'Có DOI thật để kiểm đường ống.'}},
      {{label:'Không phát hành lâm sàng',status:'ok',note:'Đây chỉ là fixture kỹ thuật.'}}
    ]
  }},
  items:[
    {{
      id:'CLIN-EVID-PIPE-001',
      title:'CONSORT 2010 Explanation and Elaboration: updated guidelines for reporting parallel group randomised trials',
      source:'BMJ',
      org:'CONSORT Group',
      dateVersion:'2010',
      pmid:'{FIXTURE_PMID}',
      doi:'{FIXTURE_DOI}',
      design:'Guideline',
      population:'Báo cáo thử nghiệm ngẫu nhiên song song',
      frame:'reporting-standard',
      pico:{{P:'thử nghiệm ngẫu nhiên',I:'chuẩn báo cáo CONSORT',C:'báo cáo không chuẩn hóa',O:'minh bạch và tái lập'}},
      effectText:'Chuẩn báo cáo nghiên cứu, không phải hiệu quả điều trị.',
      gradeSource:'Nguồn không phân hạng GRADE cho quyết định điều trị',
      gradeLevel:'na',
      decision:'consider',
      groups:['research-reporting'],
      action:'Dùng làm fixture kiểm đường ống; mọi khuyến cáo lâm sàng thật phải qua strict source gate và bác sĩ duyệt trước khi áp dụng.',
      monitoring:'Xác nhận không chứa PII và không phát hành như khuyến cáo điều trị.',
      vn:'Không áp dụng trực tiếp cho bệnh nhân; chỉ dùng trong kiểm thử pipeline.',
      references:['Schulz KF, Altman DG, Moher D. CONSORT 2010 Explanation and Elaboration. BMJ. 2010;340:c869. doi:{FIXTURE_DOI}.']
    }}
  ],
  etd:{{
    problem:'Cần kiểm tự động đường ống cập nhật chứng cứ trước khi dùng cho dashboard thật.',
    desirable:'Phát hiện sớm lỗi dashboard, thư viện và tài liệu phái sinh.',
    undesirable:'Không thay thế xác minh online hoặc thẩm định lâm sàng độc lập.',
    certainty:'Fixture kỹ thuật offline; không phân hạng lâm sàng.',
    values:'Ưu tiên minh bạch, truy nguyên và không PII.',
    balance:'Lợi ích kiểm kỹ thuật cao; không dùng để ra quyết định điều trị.',
    resources:'Dùng thư mục tạm, không ghi vào hub thật.',
    equity:'Không dùng dữ liệu người bệnh.',
    acceptability:'Chấp nhận cho kiểm CI/offline.',
    feasibility:'Chạy bằng thư viện chuẩn Python và công cụ repo hiện có.',
    recommendation:'PASS kỹ thuật chỉ khi toàn bộ artifact được sinh và cổng liêm chính không lỗi.',
    strength:'conditional'
  }}
}};
/* ▲▲▲  HẾT KHỐI DATA  ▲▲▲ */
</script>
</body>
</html>
"""


def write_synthetic_dashboard(base: Path, *, updated: str | None = None) -> Path:
    """Ghi dashboard fixture vào thư mục tạm để các tool hiện hữu xử lý như file thật."""
    dash = base / "WebDashboard_EBM_VanDeCuThe_SyntheticClinicalEvidenceUpdate.html"
    dash.write_text(_synthetic_dashboard_html(updated or date.today().isoformat()), encoding="utf-8")
    return dash


def _check_no_pii(text: str) -> tuple[bool, str]:
    patterns = [
        r"\b\d{1,2}/\d{1,2}/\d{4}\b",
        r"\b0\d{9}\b",
        r"[\w.+-]+@[\w-]+\.[\w.-]+",
        r"\b(?:CCCD|CMND|số\s*BHYT|mã\s*BN|MRN)\b",
    ]
    hits: list[str] = []
    for pat in patterns:
        hits.extend(re.findall(pat, text, flags=re.I))
    if hits:
        return False, "nghi PII: " + ", ".join(sorted(set(hits))[:5])
    return True, "không thấy mẫu PII rõ trong fixture/artifact"


def _check_library(base: Path) -> CheckResult:
    lib_path = base / "library.json"
    html_path = base / "evidence-library.html"
    if not lib_path.exists() or not html_path.exists():
        return CheckResult(
            "Library accumulation",
            "FAIL",
            "thiếu library.json hoặc evidence-library.html",
            "Dashboard PASS phải được thêm vào thư viện tích lũy.",
            "Không kiểm giao diện bằng trình duyệt; chỉ kiểm artifact tĩnh.",
        )
    try:
        lib = json.loads(lib_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return CheckResult(
            "Library accumulation",
            "FAIL",
            f"library.json lỗi JSON: {exc}",
            "Thư viện phải đọc lại được để Antifacts/Hub tích lũy.",
            "Không kiểm mọi dashboard cũ trong thư viện thật.",
        )
    ok = len(lib) == 1 and FIXTURE_DOI in (lib[0].get("dois") or [])
    return CheckResult(
        "Library accumulation",
        "PASS" if ok else "FAIL",
        f"{len(lib)} entry; DOI fixture {'có' if ok else 'thiếu'}; html={html_path.exists()}",
        "build_library.py add tạo chỉ mục và giữ DOI truy nguyên.",
        "Fixture offline; không xác nhận DOI qua Crossref trong bước này.",
    )


def _check_derivatives(base: Path) -> CheckResult:
    outdir = base / "derivatives"
    files = sorted(outdir.glob("*.md"))
    text = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in files)
    suffixes = {"to-dan-nguoi-benh", "slide-outline", "kich-ban-tiktok"}
    has_all_suffixes = all(any(suffix in p.name for p in files) for suffix in suffixes)
    has_draft_labels = "BẢN NHÁP" in text and DISCLAIMER in text
    no_pii, pii_detail = _check_no_pii(text)
    ok = len(files) == 3 and has_all_suffixes and has_draft_labels and no_pii
    evidence = (
        f"{len(files)} file; suffixes={has_all_suffixes}; draft/disclaimer={has_draft_labels}; "
        f"{pii_detail}"
    )
    return CheckResult(
        "Derivative artifacts",
        "PASS" if ok else "FAIL",
        evidence,
        "make_derivatives.py sinh đủ tờ dặn, slide outline và kịch bản truyền thông có nhãn nháp/disclaimer.",
        "Không thay bác sĩ biên tập ngôn ngữ phổ thông, liều dùng hoặc nội dung truyền thông thật.",
    )


def _check_templates() -> CheckResult:
    required = [
        "EVIDENCE WORKBENCH",
        "CLINICAL QUICK VIEW",
        "EVIDENCE DETAIL VIEW",
        "GRADE EtD",
        "Chuẩn & chất lượng",
        "Chuẩn chất lượng cập nhật chứng cứ",
        "qualityView",
        "standards",
        "sourceHierarchy",
        "searchSources",
        "CONSORT",
        "STROBE",
        "PRISMA",
        "AGREE II",
        "AMSTAR 2",
        "ROBINS-I",
        "QUADAS-3",
        "PROBAST",
        "Truy nguyên từng item",
        "--strict-sources",
        "Kiểm chứng thao tác",
        "exportData('csv')",
        "exportData('json')",
        DISCLAIMER,
        "gradeLevel",
        "decision",
        "etd",
    ]
    details = []
    ok_all = True
    for path in (EW_TEMPLATE, EW_HUB_ASSET, EW_SKILL_TEMPLATE, EW_DARK_SKILL_TEMPLATE):
        ok, detail = _contains_all(path, required)
        ok_all = ok_all and ok
        details.append(f"{path.name}: {detail}")
    return CheckResult(
        "Evidence Workbench template contract",
        "PASS" if ok_all else "FAIL",
        "; ".join(details),
        "Template nguồn và asset hub cùng giữ các điều khiển/tabs/schema tối thiểu cho cập nhật chứng cứ, gồm lớp standards/chất lượng và strict source gate.",
        "Không kiểm visual bằng Playwright; chỉ kiểm marker cấu trúc tĩnh.",
    )


def _check_sync_all_contract() -> CheckResult:
    required = [
        "def _passes_offline_gate",
        "verify_dashboard.py",
        "return r.returncode == 0",
        "def harvest",
        "integrity_guard.py",
        "--quarantine-untraceable",
        "build_library.py",
        "build_antifacts.py",
    ]
    ok, detail = _contains_all(SYNC_ALL, required)
    return CheckResult(
        "Hub sync_all contract",
        "PASS" if ok else "FAIL",
        detail,
        "sync_all.py còn gom dashboard qua cổng liêm chính, quarantine thẻ thiếu truy nguyên và làm giàu thư viện.",
        "Không chạy sync_all trên hub thật trong verifier này để tránh churn dữ liệu.",
    )


def run_verification(*, online_dashboard_gate: bool = False) -> dict:
    rows: list[CheckResult] = []
    rows.append(_check_templates())
    rows.append(_check_sync_all_contract())

    with tempfile.TemporaryDirectory(prefix="clinical-evidence-pipeline-") as tmp:
        base = Path(tmp)
        dash = write_synthetic_dashboard(base)
        html = dash.read_text(encoding="utf-8")
        no_pii, pii_detail = _check_no_pii(html)
        rows.append(CheckResult(
            "Synthetic dashboard fixture",
            "PASS" if (DISCLAIMER in html and FIXTURE_DOI in html and no_pii) else "FAIL",
            f"file={dash.name}; doi={FIXTURE_DOI}; {pii_detail}",
            "Fixture có disclaimer, DOI truy nguyên và không chứa mẫu PII rõ.",
            "Fixture không phải khuyến cáo điều trị và không thay dashboard thật.",
        ))

        verify_cmd = [sys.executable, str(VERIFY_DASHBOARD), str(dash), "--strict-sources"]
        if online_dashboard_gate:
            verify_cmd.append("--online")
        ok, tail = _run(verify_cmd, cwd=ROOT)
        rows.append(CheckResult(
            "Dashboard integrity gate",
            "PASS" if ok else "FAIL",
            tail,
            "verify_dashboard.py chặn thiếu disclaimer/truy nguyên/grade/decision/nội dung rác và hợp đồng nguồn nghiêm ngặt.",
            (
                "Đã chạy canary online trên PMID fixture; dashboard thật vẫn phải chạy online với chính nguồn của nó."
                if online_dashboard_gate
                else "Mặc định chạy strict offline cho fixture; dashboard thật nên chạy thêm --online để phân giải PMID/DOI."
            ),
        ))

        ok, tail = _run([sys.executable, str(BUILD_LIBRARY), "add", str(dash)], cwd=base)
        rows.append(CheckResult(
            "build_library.py add",
            "PASS" if ok else "FAIL",
            tail,
            "Dashboard đã PASS có thể vào thư viện tích lũy cục bộ.",
            "Không ghi vào EBM-Dashboards thật trong verifier này.",
        ))
        rows.append(_check_library(base))

        ok, tail = _run([sys.executable, str(MAKE_DERIVATIVES), str(dash)], cwd=base)
        rows.append(CheckResult(
            "make_derivatives.py",
            "PASS" if ok else "FAIL",
            tail,
            "Công cụ sinh bộ phái sinh từ dashboard đã PASS.",
            "Các tài liệu phái sinh vẫn là bản nháp cần bác sĩ rà.",
        ))
        rows.append(_check_derivatives(base))

    blocking_failures = [row for row in rows if row.blocking and row.status != "PASS"]
    return {
        "kind": "clinical_evidence_update_pipeline_verification",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "overall_status": "PASS" if not blocking_failures else "FAIL",
        "blocking_failure_count": len(blocking_failures),
        "online_dashboard_gate": online_dashboard_gate,
        "rows": [asdict(row) for row in rows],
        "disclaimer": (
            "Cần bác sĩ kiểm chứng. Đây là canary kỹ thuật online của pipeline cập nhật chứng cứ, "
            "không thay double-review nguồn thật, rà an toàn thuốc hoặc quyết định lâm sàng."
            if online_dashboard_gate
            else
            "Cần bác sĩ kiểm chứng. Đây là kiểm chứng kỹ thuật/offline của pipeline cập nhật chứng cứ, "
            "không thay xác minh online, rà an toàn thuốc hoặc quyết định lâm sàng."
        ),
    }


def markdown_report(report: dict) -> str:
    lines = [
        "# Clinical Evidence Update Pipeline Verification",
        "",
        f"- Generated: `{report['generated_at']}`",
        f"- Overall status: `{report['overall_status']}`",
        f"- Blocking failures: `{report['blocking_failure_count']}`",
        f"- Online dashboard gate: `{report['online_dashboard_gate']}`",
        "",
        "| Cổng kiểm | Kết quả | Chứng cứ | Chứng minh được | Giới hạn trung thực |",
        "|---|---|---|---|---|",
    ]
    for row in report["rows"]:
        lines.append(
            "| {name} | {status} | {evidence} | {proves} | {limitation} |".format(
                name=str(row["name"]).replace("|", "\\|"),
                status=str(row["status"]).replace("|", "\\|"),
                evidence=str(row["evidence"]).replace("|", "\\|"),
                proves=str(row["proves"]).replace("|", "\\|"),
                limitation=str(row["limitation"]).replace("|", "\\|"),
            )
        )
    lines.extend(["", f"> {report['disclaimer']}", ""])
    return "\n".join(lines)


def write_report(report: dict, *, out_md: Path, out_json: Path) -> None:
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(markdown_report(report), encoding="utf-8")
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def _print_summary(report: dict, out_md: Path, out_json: Path) -> None:
    print("Clinical evidence update pipeline:", report["overall_status"])
    for row in report["rows"]:
        print(f"- {row['status']} {row['name']}: {row['evidence']}")
    print(f"Markdown: {out_md}")
    print(f"JSON: {out_json}")
    print(report["disclaimer"])


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--online-dashboard-gate", action="store_true",
                        help="Chạy verify_dashboard.py --online --strict-sources cho fixture (cần mạng; không dùng mặc định trong audit offline).")
    parser.add_argument("--out-md", default=str(DEFAULT_MD))
    parser.add_argument("--out-json", default=str(DEFAULT_JSON))
    parser.add_argument("--no-write", action="store_true", help="Không ghi báo cáo Markdown/JSON.")
    parser.add_argument("--json", action="store_true", help="In JSON ra stdout.")
    args = parser.parse_args(argv)

    report = run_verification(online_dashboard_gate=args.online_dashboard_gate)
    out_md = Path(args.out_md)
    out_json = Path(args.out_json)
    if not args.no_write:
        write_report(report, out_md=out_md, out_json=out_json)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        _print_summary(report, out_md, out_json)
    return 0 if report["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
