#!/usr/bin/env python3
"""Audit tổng thể hệ Agent + Dashboard + EBM_MASTER.

Chạy từ thư mục gốc:
  python3 tools/audit_ebm_system.py

Mặc định chỉ dùng kiểm offline để chạy nhanh và không cần mạng. Muốn xác minh online PMID/DOI
và cổng nguồn nghiêm ngặt cho một dashboard quan trọng, chạy riêng
`verify_dashboard.py --online --strict-sources`.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from hashlib import sha256
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS_SRC = ROOT / ".claude" / "agents"
AGENTS_CODEX = ROOT / ".Codex" / "agents"
DASH = ROOT / "EBM-Dashboards"
MASTER = ROOT / "EBM_MASTER"
HUB_DASH = MASTER / "WEB_DASHBOARDS"
REPO = ROOT / "medical-ebm-automation"
CHATGPT_EXPORT = ROOT / "CHATGPT_EXPORT"
VENV_PY = (
    Path.home() / ".ebm-venv" / "Scripts" / "python.exe"
    if os.name == "nt"
    else Path.home() / ".ebm-venv" / "bin" / "python"
)
DEFAULT_FILES = [
    ROOT / "THU-MUC-MAC-DINH.md",
    ROOT / "Đồng bộ Claude-Codex.bat",
    ROOT / "Đồng bộ Claude-Codex.command",
    ROOT / "Kiểm tra môi trường EBM.bat",
    ROOT / "Kiểm tra môi trường EBM.command",
    ROOT / "Cài môi trường EBM.bat",
    ROOT / "Cài môi trường EBM.command",
    ROOT / "Mở Antifacts.bat",
    ROOT / "Mở Antifacts.command",
    ROOT / "Tạo ChatGPT EBM Copilot.bat",
    ROOT / "Tạo ChatGPT EBM Copilot.command",
    ROOT / "tools" / "open_chatgpt_ebm_setup.ps1",
]
TEMPLATE_PAIRS = [
    (
        ROOT / "dashboard_mockups" / "templates" / "evidence-workbench-template.html",
        MASTER / "skill_assets" / "web-dashboard-evidence-workbench.html",
    ),
    (
        ROOT / "dashboard_mockups" / "templates" / "evidence-workbench-template.html",
        ROOT / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "templates" / "web-dashboard-evidence-workbench.html",
    ),
    (
        ROOT / "dashboard_mockups" / "templates" / "evidence-workbench-template.html",
        ROOT / "sync" / "skills" / "dark-analyst" / "templates" / "web-dashboard-evidence-workbench.html",
    ),
    (
        ROOT / "dashboard_mockups" / "templates" / "dark-analyst-template.html",
        MASTER / "skill_assets" / "web-dashboard-dark-analyst.html",
    ),
]
# --- Ba bản song song của bộ tool .py thuộc skill cap-nhat-chung-cu-y-khoa ---------------
# Nguồn drift đã xác nhận (memory project-skill-tool-sync-topology-2026-07-05, commit 8931328):
# các tool .py của skill sống ở 3 nơi. Trước đây audit CHỈ so template HTML
# (template_sync_failures) và *chạy* verifier runtime, nên khi verify_dashboard.py runtime
# đi trước skill/skill_assets (2026-07-02, thêm --check-topic) thì drift lọt qua
# "Template sync: PASS" nhiều ngày. tool_sync_failures() bịt điểm mù đó bằng md5.
SKILL_TOOLS_DIR = ROOT / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools"  # git-tracked, nguồn phân phối
MASTER_ASSETS_DIR = MASTER / "skill_assets"                                        # mirror hub (untracked)
DASH_TOOLS_DIR = DASH / "tools"                                                    # runtime/dev (untracked)
TOOL_DIRS = {
    "sync/skills (nguồn git)": SKILL_TOOLS_DIR,
    "EBM_MASTER/skill_assets (mirror hub)": MASTER_ASSETS_DIR,
    "EBM-Dashboards/tools (runtime)": DASH_TOOLS_DIR,
}
# Tool DÙNG CHUNG cần đồng bộ md5, kèm TẬP THƯ MỤC KỲ VỌNG của từng tool → bắt cả drift
# HIỆN DIỆN ("shared tool biến mất khỏi 1 nơi") lẫn drift NỘI DUNG ("sửa 1 nơi quên nơi khác").
#   • 6 tool lõi phục vụ dựng/kiểm dashboard: có ở CẢ BA nơi.
#   • surveillance_scan.py: chỉ nguồn-git + runtime; CỐ Ý không mirror sang skill_assets
#     (là scanner giám sát định kỳ, không tham gia dựng dashboard cho hub).
SHARED_TOOL_EXPECTATIONS = {
    "build_library.py": {SKILL_TOOLS_DIR, MASTER_ASSETS_DIR, DASH_TOOLS_DIR},
    "check_topic_relevance.py": {SKILL_TOOLS_DIR, MASTER_ASSETS_DIR, DASH_TOOLS_DIR},
    "dashboard_content_audit.py": {SKILL_TOOLS_DIR, MASTER_ASSETS_DIR, DASH_TOOLS_DIR},
    "drug_safety_scan.py": {SKILL_TOOLS_DIR, MASTER_ASSETS_DIR, DASH_TOOLS_DIR},
    "make_derivatives.py": {SKILL_TOOLS_DIR, MASTER_ASSETS_DIR, DASH_TOOLS_DIR},
    "verify_dashboard.py": {SKILL_TOOLS_DIR, MASTER_ASSETS_DIR, DASH_TOOLS_DIR},
    "surveillance_scan.py": {SKILL_TOOLS_DIR, DASH_TOOLS_DIR},
}
# File CỐ Ý chỉ tồn tại ở MỘT nơi (chỉ-runtime: dev harness/reskin) — KHÔNG so, KHÔNG coi là
# drift. Ngoài danh sách này, mọi file test_*.py / conftest.py cũng được xem là chỉ-runtime.
RUNTIME_ONLY_TOOLS = {
    "assemble_dashboard.py",  # bộ ráp dashboard runtime, không thuộc gói skill phân phối
    "reskin_dashboards.py",   # áp lại vỏ template cho file đã xuất — chỉ dùng ở EBM-Dashboards
}
CHATGPT_REQUIRED_FILES = [
    CHATGPT_EXPORT / "CHATGPT_EBM_AGENT_SYSTEM_PROMPT.md",
    CHATGPT_EXPORT / "README_TICH_HOP_CHATGPT.md",
    CHATGPT_EXPORT / "STARTER_PROMPTS.md",
    CHATGPT_EXPORT / "INTEGRATION_CHECKLIST.md",
]
SCHEDULED = ROOT / "Scheduled"
BAN_DO_KET_NOI = AGENTS_SRC / "_BAN-DO-KET-NOI.md"
ROUTINE_WIRING = AGENTS_SRC / "_ROUTINE-AGENT-WIRING.md"
LIVING_LEDGER_COUNT_DOCS = {
    AGENTS_SRC / "_VONG-LAP-KHEP-KIN.md": [
        re.compile(r"ledger\s+(\d+)\s+thẻ", re.IGNORECASE),
    ],
    AGENTS_SRC / "cap-nhat-guideline.md": [
        re.compile(r"EBM_MASTER\s+—\s+(\d+)\+?\s+thẻ", re.IGNORECASE),
    ],
}


def configure_utf8_stdio() -> None:
    """Giúp audit in tiếng Việt ổn định trên Windows console."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def run(cmd: list[str], cwd: Path = ROOT) -> tuple[int, str]:
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("PYTHONPYCACHEPREFIX", str(Path(tempfile.gettempdir()) / "ebm_pycache"))
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def count_agent_guardrails() -> dict[str, int]:
    src_files = [
        p for p in AGENTS_SRC.glob("*.md")
        if p.name != "README.md" and not p.name.startswith("_")
    ]
    toml_files = list(AGENTS_CODEX.glob("*.toml"))
    marker = "EBM-MANDATORY-FINAL-GUARDRAIL"
    return {
        "source_agents": len(src_files),
        "codex_agents": len(toml_files),
        "source_guardrail": sum(marker in p.read_text(encoding="utf-8", errors="ignore") for p in src_files),
        "codex_guardrail": sum(marker in p.read_text(encoding="utf-8", errors="ignore") for p in toml_files),
        "source_disclaimer": sum("Cần bác sĩ kiểm chứng" in p.read_text(encoding="utf-8", errors="ignore") for p in src_files),
    }


# Số agent LÕI (baseline) — 21 lâm sàng + 28 nghiên cứu + 1 guardrail chung.
# (2026-07-04: +1 `quan-ly-khang-dong` — quản lý kháng đông trọn vòng (48→49);
#  +1 `tham-dinh-do-chinh-xac-chan-doan` — thẩm định độ chính xác chẩn đoán
#  QUADAS-2/QUADAS-C + GRADE-cho-test + STARD, lấp khoảng trống nhánh chẩn đoán (49→50).)
# Agent TỰ SINH (qua tools/generate_agent.py) được phép VƯỢT baseline MIỄN LÀ đã
# đăng ký trong _TU-SINH-AGENT-REGISTRY.json — nhờ đó tripwire vẫn bắt được agent
# thêm/bớt "chui" (không qua registry) mà KHÔNG chặn cơ chế tự sinh hợp lệ.
CORE_AGENT_COUNT = 50
AUTOGEN_REGISTRY = AGENTS_SRC / "_TU-SINH-AGENT-REGISTRY.json"


def registered_autogen_count() -> int:
    """Số agent tự sinh ĐÃ ĐĂNG KÝ và còn tồn tại file .md."""
    if not AUTOGEN_REGISTRY.exists():
        return 0
    try:
        data = json.loads(AUTOGEN_REGISTRY.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return 0
    names = {
        g.get("name") for g in data.get("generated", [])
        if g.get("name") and (AGENTS_SRC / f"{g['name']}.md").exists()
    }
    return len(names)


def _is_unverified_status(status: str) -> bool:
    """True nếu status là THẬT SỰ chưa xác minh (chưa xác minh/cần xác minh).

    Không đếm các status đã bắt đầu bằng "đã xác minh..." dù có ghi caveat
    phụ chứa từ "chưa"/"cần" (vd "đã xác minh nguồn chính thức (...); chưa
    đọc toàn văn") — đó là thẻ ĐÃ xác minh nguồn, chỉ chưa đọc hết toàn văn,
    không thuộc hàng chờ xác minh. Kiểm định đối kháng 2026-07-05 xác nhận
    6 thẻ bị đếm nhầm trước khi có hàm này (32 vs đúng ra phải phân biệt rõ).
    """
    s = status.lower().strip()
    if s.startswith("đã xác minh"):
        return False
    return "chưa" in s or "cần" in s


def master_counts() -> dict[str, int]:
    data = json.loads((MASTER / "EBM_MASTER.json").read_text(encoding="utf-8"))
    cards = data.get("evidence_cards", [])
    quarantined = data.get("quarantined_cards", [])
    def src(c: dict) -> dict:
        return c.get("source") if isinstance(c.get("source"), dict) else {}
    def has_trace(c: dict) -> bool:
        refs = c.get("references") if isinstance(c.get("references"), list) else []
        s = src(c)
        return bool(refs or s.get("pmid") or s.get("doi") or s.get("url"))
    return {
        "cards": len(cards),
        "quarantined_cards": len(quarantined),
        "missing_trace": sum(not has_trace(c) for c in cards),
        "apply_unverified": sum(
            c.get("decision") == "apply"
            and _is_unverified_status(str(c.get("verification_status", "")))
            for c in cards
        ),
        "unverified_queue": sum(
            _is_unverified_status(str(c.get("verification_status", "")))
            for c in cards
        ),
        "apply": sum(c.get("decision") == "apply" for c in cards),
        "consider": sum(c.get("decision") == "consider" for c in cards),
        "notyet": sum(c.get("decision") == "notyet" for c in cards),
    }


def living_document_count_failures(current_cards: int) -> list[str]:
    """Bắt các sổ TRẠNG THÁI SỐNG còn hardcode sai số thẻ hub.

    Không quét mọi tài liệu vì nhiều dòng là lịch sử/snapshot có ngày rõ ràng
    (vd "2026-07-12: chạy thật trên hub 259 thẻ"). Cổng này chỉ soi những file
    đang được agent dùng như hướng dẫn vận hành hiện hành; ở đó số thẻ phải đọc
    động từ EBM_MASTER/audit, hoặc nếu hardcode thì phải khớp số thật.
    """
    failures: list[str] = []
    for path, patterns in LIVING_LEDGER_COUNT_DOCS.items():
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in patterns:
            for match in pattern.finditer(text):
                claimed = int(match.group(1))
                if claimed != current_cards:
                    failures.append(
                        f"{path.relative_to(ROOT)} ghi {claimed} thẻ, "
                        f"EBM_MASTER hiện có {current_cards} thẻ"
                    )
    return failures


def _dashboard_data_block_hash(path: Path) -> str | None:
    """Hash riêng khối DATA để bắt lệch nội dung dashboard sau khi đồng bộ hub.

    Không so toàn bộ HTML vì vỏ template/runtime có thể được reskin hợp lệ; khối DATA mới là
    phần quyết định nguồn, DOI/PMID, URL truy nguyên và nội dung chứng cứ mà bác sĩ sẽ đọc.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    start = text.find("const DATA")
    if start == -1:
        return None
    end = text.find("HẾT KHỐI DATA", start)
    block = text[start:end if end != -1 else start + 60000]
    return sha256(block.encode("utf-8")).hexdigest()


def verify_dashboards() -> tuple[int, list[str]]:
    verifier = DASH / "tools" / "verify_dashboard.py"
    failures: list[str] = []
    checked = 0
    copies: dict[str, dict[str, Path]] = {}
    dashboard_dirs = (
        (DASH, "EBM-Dashboards"),
        (HUB_DASH, "EBM_MASTER/WEB_DASHBOARDS"),
    )
    for folder, label in dashboard_dirs:
        if not folder.exists():
            continue
        for html in sorted(folder.glob("WebDashboard_EBM_*.html")):
            checked += 1
            code, _out = run([sys.executable, str(verifier), str(html)], cwd=ROOT)
            if code != 0:
                failures.append(f"{label}/{html.name}")
            copies.setdefault(html.name, {})[label] = html

    for name, by_label in sorted(copies.items()):
        staging = by_label.get("EBM-Dashboards")
        hub = by_label.get("EBM_MASTER/WEB_DASHBOARDS")
        if not staging or not hub:
            continue
        staging_hash = _dashboard_data_block_hash(staging)
        hub_hash = _dashboard_data_block_hash(hub)
        if staging_hash and hub_hash and staging_hash != hub_hash:
            failures.append(
                "Dashboard DATA drift: "
                f"{name} khác DATA giữa EBM-Dashboards và EBM_MASTER/WEB_DASHBOARDS"
            )
    return checked, failures


def template_sync_failures() -> list[str]:
    failures: list[str] = []
    for source, target in TEMPLATE_PAIRS:
        if not source.exists() or not target.exists():
            failures.append(f"thiếu template {source.name} hoặc {target.name}")
            continue
        if file_sha256(source) != file_sha256(target):
            failures.append(f"{source.name} lệch với {target.name}")
    return failures


def _is_runtime_only_tool(name: str) -> bool:
    """File tool được PHÉP chỉ tồn tại ở một nơi (không so, không coi là drift)."""
    return (
        name in RUNTIME_ONLY_TOOLS
        or name.startswith("test_")
        or name == "conftest.py"
    )


def tool_sync_failures() -> tuple[bool, list[str]]:
    """So md5 các bản .py tool DÙNG CHUNG của skill cap-nhat-chung-cu-y-khoa giữa 3 thư mục
    song song (nguồn git · mirror hub · runtime) — bịt điểm mù nêu ở memory
    project-skill-tool-sync-topology-2026-07-05: audit chỉ so template HTML nên drift verifier
    runtime (2026-07-02, thêm --check-topic) lọt qua "Template sync: PASS" nhiều ngày.

    Trả (ran, failures). Chỉ so file THỰC SỰ dùng chung; bỏ qua file cố ý chỉ-runtime
    (RUNTIME_ONLY_TOOLS / test_*). Nếu <2 trong 3 thư mục tồn tại (vd đang chạy trong git
    worktree, nơi EBM_MASTER và EBM-Dashboards bị .gitignore) → ran=False, KHÔNG so được gì
    (không có bản thật để đối chiếu) — caller PHẢI in SKIP, không được coi là PASS đã kiểm
    (audit 2026-07-10: in "PASS" khi so sánh chưa từng chạy là chính điểm mù check này sinh ra
    để bịt lại lần đầu).
    """
    failures: list[str] = []
    live = [(label, d) for label, d in TOOL_DIRS.items() if d.exists()]
    if len(live) < 2:
        return False, failures
    label_of = {d: label for label, d in TOOL_DIRS.items()}

    # (A) Drift NỘI DUNG — so md5 mọi .py xuất hiện ở ≥2 thư mục đang tồn tại (tự bao phủ cả
    #     tool thêm mới sau này, không cần khai trước), trừ file cố ý chỉ-runtime.
    py_names: set[str] = set()
    for _label, d in live:
        py_names.update(p.name for p in d.glob("*.py"))
    for name in sorted(py_names):
        if _is_runtime_only_tool(name):
            continue
        holders = [d for _label, d in live if (d / name).exists()]
        if len(holders) < 2:
            continue
        by_digest: dict[str, list[str]] = {}
        for d in holders:
            by_digest.setdefault(file_sha256(d / name), []).append(label_of[d])
        if len(by_digest) > 1:
            groups = " ≠ ".join(
                "{" + ", ".join(sorted(labels)) + "}" for labels in by_digest.values()
            )
            failures.append(f"{name}: nội dung lệch giữa {groups}")

    # (B) Drift HIỆN DIỆN — tool dùng chung đã khai phải có mặt đủ ở tập thư mục kỳ vọng
    #     (trong số đang tồn tại). Bắt ca "shared tool bị thêm/xóa ở chỉ một nơi".
    for name, expected in SHARED_TOOL_EXPECTATIONS.items():
        live_expected = [d for d in expected if d.exists()]
        if len(live_expected) < 2:
            continue
        have = [d for d in live_expected if (d / name).exists()]
        missing = [d for d in live_expected if not (d / name).exists()]
        if have and missing:
            failures.append(
                f"{name}: thiếu ở " + ", ".join(label_of[d] for d in missing)
                + " (đang có ở " + ", ".join(label_of[d] for d in have) + ")"
            )

    return True, failures


def default_file_failures() -> list[str]:
    return [str(path.relative_to(ROOT)) for path in DEFAULT_FILES if not path.exists()]


def chatgpt_integration_failures() -> list[str]:
    failures = [str(path.relative_to(ROOT)) for path in CHATGPT_REQUIRED_FILES if not path.exists()]
    prompt = CHATGPT_EXPORT / "CHATGPT_EBM_AGENT_SYSTEM_PROMPT.md"
    if prompt.exists():
        text = prompt.read_text(encoding="utf-8", errors="ignore")
        required_tokens = [
            "dieu-phoi-lam-sang",
            "dieu-phoi-nghien-cuu",
            "R1-R7",
            "Q1-Q7",
            "Cần bác sĩ kiểm chứng",
        ]
        missing = [token for token in required_tokens if token not in text]
        if missing:
            failures.append("CHATGPT_EBM_AGENT_SYSTEM_PROMPT.md thiếu: " + ", ".join(missing))
    return failures


def claude_codex_sync_health() -> tuple[bool, str, list[str]]:
    """Run the standalone Claude/Codex sync health gate and return a compact status."""
    checker = ROOT / "tools" / "check_claude_codex_sync_health.py"
    if not checker.exists():
        return False, "thiếu tools/check_claude_codex_sync_health.py", [
            "thiếu cổng kiểm tra Claude/Codex sync health"
        ]
    code, out = run([sys.executable, str(checker), "--json"], cwd=ROOT)
    if code != 0:
        try:
            data = json.loads(out)
            return False, "FAIL", list(data.get("errors", []))
        except json.JSONDecodeError:
            return False, "FAIL", [out.strip()[:500] or "không đọc được output sync health"]
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return False, "FAIL", ["output sync health không phải JSON hợp lệ"]
    status = str(data.get("status", "FAIL"))
    targets = data.get("targets", [])
    source = data.get("source", {})
    summary = (
        f"{status}: {source.get('agents', '?')} nguồn, "
        + ", ".join(
            f"{target.get('label', '?')}={target.get('agent_toml', '?')}"
            for target in targets
        )
    )
    return status == "PASS", summary, list(data.get("errors", []))


def routine_layer_failures() -> list[str]:
    """Đối chiếu Scheduled/*/SKILL.md (thư mục thật trên đĩa) với bảng routine khai trong
    _BAN-DO-KET-NOI.md §8 và _ROUTINE-AGENT-WIRING.md. Vá lỗ hổng F2 nêu trong đánh giá độc
    lập 2026-07-03 (README kiểm 'không tham chiếu treo' cho lớp AGENT nhưng chưa áp cho lớp
    ROUTINE — khiến 1 routine ma + routine SKILL.md rỗng lọt lưới)."""
    failures: list[str] = []
    if not SCHEDULED.exists():
        return failures

    real_routines: set[str] = set()
    empty_routines: set[str] = set()
    for d in sorted(SCHEDULED.iterdir()):
        if not d.is_dir() or d.name.startswith("_") or d.name.startswith("."):
            continue
        skill_md = d / "SKILL.md"
        if skill_md.exists() and skill_md.stat().st_size > 0:
            real_routines.add(d.name)
        else:
            empty_routines.add(d.name)

    if empty_routines:
        failures.append(
            "Scheduled/ có thư mục KHÔNG có SKILL.md thật (rỗng/thiếu): "
            + ", ".join(sorted(empty_routines))
        )

    def mentioned(doc: Path, names: set[str]) -> set[str]:
        # Tên routine có thể xuất hiện bọc backtick, **in đậm**, hay trần trong văn xuôi/bảng
        # (2 tài liệu không nhất quán định dạng) — khớp theo TOKEN trọn vẹn, không phụ thuộc
        # ký tự bao quanh, tránh dương tính giả kiểu "drug-safety-daily" chỉ in đậm không backtick.
        if not doc.exists():
            return set()
        text = doc.read_text(encoding="utf-8", errors="ignore")
        found = set()
        for name in names:
            pattern = r"(?<![\w-])" + re.escape(name) + r"(?![\w-])"
            if re.search(pattern, text):
                found.add(name)
        return found

    all_folder_names = real_routines | empty_routines
    ban_do = mentioned(BAN_DO_KET_NOI, all_folder_names)
    wiring = mentioned(ROUTINE_WIRING, all_folder_names)

    undocumented = real_routines - ban_do
    if undocumented:
        failures.append(
            "Routine có SKILL.md thật nhưng KHÔNG được nhắc trong _BAN-DO-KET-NOI.md §8: "
            + ", ".join(sorted(undocumented))
        )

    mismatch = ban_do.symmetric_difference(wiring)
    if mismatch:
        failures.append(
            "_BAN-DO-KET-NOI.md và _ROUTINE-AGENT-WIRING.md liệt kê KHÔNG khớp routine: "
            + ", ".join(sorted(mismatch))
        )

    return failures


def launchd_registration_drift() -> list[str]:
    """macOS only: đối chiếu plist THẬT trên đĩa (~/Library/LaunchAgents/com.medicalebm.*.plist)
    với bản ĐANG NẠP trong bộ nhớ launchd. launchd KHÔNG tự đọc lại file khi nó đổi — chỉ đọc
    lúc 'launchctl bootstrap'; sửa file trên đĩa (vd đường dẫn OneDrive đổi) KHÔNG tự áp dụng,
    phải bootout+bootstrap lại thủ công. Lớp lỗi này đã gặp thật nhiều vòng liền (plist đã sửa
    đúng nhưng launchd vẫn chạy đường dẫn CŨ, job không bao giờ chạy thành công) mà KHÔNG có
    cổng nào tự phát hiện — phải người soi tay từng 'launchctl print'. Vá 2026-07-11: thêm cổng
    tự động này để khoảng trống KHÔNG lặp lại âm thầm. Chỉ chạy trên macOS (launchd không tồn
    tại ở Windows); bỏ qua êm nếu máy chưa cài lịch nền com.medicalebm.*."""
    import plistlib

    if sys.platform != "darwin":
        return []
    agents_dir = Path.home() / "Library" / "LaunchAgents"
    if not agents_dir.exists():
        return []
    plists = sorted(
        p for p in agents_dir.glob("com.medicalebm.*.plist")
        if ".bak" not in p.name
    )
    if not plists:
        return []

    drift: list[str] = []
    for plist_path in plists:
        try:
            with plist_path.open("rb") as f:
                on_disk = plistlib.load(f)
        except Exception as e:  # noqa: BLE001
            drift.append(f"{plist_path.name}: không đọc được plist trên đĩa ({e})")
            continue
        label = on_disk.get("Label", plist_path.stem)
        disk_args = [str(a) for a in on_disk.get("ProgramArguments", [])]
        disk_wd = str(on_disk.get("WorkingDirectory", ""))
        reload_cmd = (
            f"launchctl bootout gui/$(id -u)/{label} && "
            f"launchctl bootstrap gui/$(id -u) {plist_path}"
        )

        try:
            p = subprocess.run(
                ["launchctl", "print", f"gui/{os.getuid()}/{label}"],
                capture_output=True, text=True, timeout=10,
            )
        except Exception as e:  # noqa: BLE001
            drift.append(f"{label}: không chạy được 'launchctl print' để đối chiếu ({e})")
            continue
        if p.returncode != 0:
            drift.append(
                f"{label}: có plist trên đĩa nhưng CHƯA được nạp vào launchd — job sẽ KHÔNG "
                f"BAO GIỜ tự chạy cho tới khi nạp: {reload_cmd}"
            )
            continue

        loaded_text = p.stdout
        m_wd = re.search(r"working directory = (.+)", loaded_text)
        loaded_wd = m_wd.group(1).strip() if m_wd else ""
        m_args = re.search(r"arguments = \{([^}]*)\}", loaded_text)
        loaded_args = (
            [line.strip() for line in m_args.group(1).splitlines() if line.strip()]
            if m_args else []
        )

        if disk_wd and loaded_wd and disk_wd != loaded_wd:
            drift.append(
                f"{label}: plist trên đĩa đã sửa (WorkingDirectory={disk_wd!r}) nhưng launchd "
                f"vẫn chạy bản CŨ trong bộ nhớ (WorkingDirectory={loaded_wd!r}) — job LỖI mọi "
                f"lần chạy cho tới khi nạp lại: {reload_cmd}"
            )
        elif disk_args and loaded_args and disk_args != loaded_args:
            drift.append(
                f"{label}: ProgramArguments trên đĩa khác bản đang nạp trong launchd — "
                f"cần nạp lại: {reload_cmd}"
            )
    return drift


def node_executable() -> str | None:
    node = shutil.which("node")
    if node:
        return node
    bundled = (
        Path.home()
        / ".cache"
        / "codex-runtimes"
        / "codex-primary-runtime"
        / "dependencies"
        / "node"
        / "bin"
        / ("node.exe" if os.name == "nt" else "node")
    )
    return str(bundled) if bundled.exists() else None


def antifacts_status() -> tuple[bool, str]:
    html_path = ROOT / "Antifacts.html"
    if not html_path.exists():
        return False, "thiếu Antifacts.html"
    html = html_path.read_text(encoding="utf-8", errors="replace")
    required = ["const DATA=", "function openScale", "showScaleTab", "renderCalc", "detail_html"]
    missing = [token for token in required if token not in html]
    if missing:
        return False, "thiếu JS/data: " + ", ".join(missing)
    if html.count("detail_html") < 45:
        return False, "chưa nhúng đủ chi tiết 45 thang điểm"

    scripts = "\n".join(re.findall(r"<script>(.*?)</script>", html, flags=re.S))
    if not scripts.strip():
        return False, "không tìm thấy script Antifacts"
    node = node_executable()
    if not node:
        return True, "PASS (không có node để kiểm JS sâu)"
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as tmp:
        tmp.write(scripts)
        tmp_path = Path(tmp.name)
    try:
        code, out = run([node, "--check", str(tmp_path)], cwd=ROOT)
    finally:
        try:
            tmp_path.unlink()
        except OSError:
            pass
    if code != 0:
        return False, out.strip()[:300] or "node --check FAIL"
    return True, "PASS"


def repo_compile_status() -> tuple[bool, str]:
    if not REPO.exists():
        return False, "không thấy medical-ebm-automation/"
    py = str(VENV_PY if VENV_PY.exists() else sys.executable)
    code, out = run([py, "-m", "compileall", "-q", "app", "scripts", "tests"], cwd=REPO)
    return code == 0, out.strip()


def repo_environment_status() -> tuple[bool, str]:
    checker = REPO / "scripts" / "check_environment.py"
    if not checker.exists():
        return False, "thiếu scripts/check_environment.py"
    py = str(VENV_PY if VENV_PY.exists() else sys.executable)
    code, out = run([py, str(checker), "--quiet"], cwd=REPO)
    return code == 0, out.strip()


def approval_independence_failures() -> list[str]:
    """Smoke-check runtime rule: creator_agent không được tự review cùng artifact."""
    failures: list[str] = []
    if not REPO.exists():
        return ["không thấy medical-ebm-automation/ để kiểm ApprovalLedger"]

    old_path = list(sys.path)
    try:
        sys.path.insert(0, str(REPO))
        from runtime.approval_ledger import ApprovalLedger

        ledger = ApprovalLedger()
        bad = ApprovalLedger.make_human_approval(
            gate_id="GATE_A",
            reviewer_role="AUDIT_GUARDRAIL_REVIEWER",
            reviewer_ref="AUDIT-SELF-REVIEW",
            scope="Audit self-review smoke check",
            evidence_content="audit evidence",
            artifact_creator_agent="tham-dinh-dau-ra",
            reviewer_agent="tham-dinh-dau-ra",
        )
        success, reason = ledger.add_approval(bad)
        if success or reason != "SELF_REVIEW_BLOCKED":
            failures.append(
                "ApprovalLedger không chặn self-review bằng SELF_REVIEW_BLOCKED"
            )

        legacy = ApprovalLedger.make_human_approval(
            gate_id="GATE_B",
            reviewer_role="AUDIT_LEGACY_IMPORT",
            reviewer_ref="AUDIT-LEGACY",
            scope="Audit imported legacy self-review trace",
            evidence_content="legacy evidence",
            artifact_creator_agent="tham-dinh-dau-ra",
            reviewer_agent="tham-dinh-dau-ra",
        )
        ledger._records.append(legacy)
        if not ledger.has_self_review_violations():
            failures.append("ApprovalLedger không phát hiện legacy self-review violation")

        good = ApprovalLedger.make_human_approval(
            gate_id="GATE_A",
            reviewer_role="AUDIT_GUARDRAIL_REVIEWER",
            reviewer_ref="AUDIT-INDEPENDENT",
            scope="Audit independent review trace",
            evidence_content="independent evidence",
            artifact_creator_agent="dieu-phoi-lam-sang",
            reviewer_agent="tham-dinh-dau-ra",
        )
        ledger2 = ApprovalLedger()
        success, reason = ledger2.add_approval(good)
        if not success or reason != "ADDED":
            failures.append("ApprovalLedger chặn nhầm creator/reviewer độc lập")
    except Exception as exc:  # noqa: BLE001
        failures.append(f"không chạy được kiểm ApprovalLedger independence: {exc}")
    finally:
        sys.path = old_path

    return failures


def chronic_care_production_guard() -> tuple[str, int, list[str], list[str]]:
    """Bảo đảm chronic-care runtime vẫn bị khóa khỏi production khi blocker còn mở."""
    failures: list[str] = []
    warnings: list[str] = []
    blocker_count = 0
    blocker_doc = REPO / "chronic-care-clinic-os" / "PRODUCTION_BLOCKERS.md"
    phase3a_doc = REPO / "docs" / "chronic-care" / "PHASE_3A_PRODUCTION_BLOCKERS.md"

    if not REPO.exists():
        return "FAIL", 0, ["không thấy medical-ebm-automation/ để kiểm chronic-care"], warnings

    docs: list[tuple[Path, str]] = []
    for path in (blocker_doc, phase3a_doc):
        if not path.exists():
            failures.append(f"thiếu {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        docs.append((path, text))
        blocker_count += sum(
            1 for line in text.splitlines()
            if line.lstrip().startswith(("- ", "* ", "- [ ]"))
        )

    blocker_text = next((text for path, text in docs if path == blocker_doc), "")
    phase3a_text = next((text for path, text in docs if path == phase3a_doc), "")
    blocker_lower = blocker_text.lower()
    phase3a_lower = phase3a_text.lower()

    required_blocker_markers = {
        "not production-ready": "PRODUCTION_BLOCKERS.md phải nói rõ chưa production-ready",
        "real patient data": "PRODUCTION_BLOCKERS.md phải cấm dùng dữ liệu bệnh nhân thật",
        "ai must remain disabled": "PRODUCTION_BLOCKERS.md phải giữ AI ở trạng thái disabled",
    }
    for token, message in required_blocker_markers.items():
        if blocker_text and token not in blocker_lower:
            failures.append(message)

    required_phase3a_markers = {
        "dpia": "PHASE_3A_PRODUCTION_BLOCKERS.md phải nhắc DPIA/data protection",
        "clinical safety sign-off": "PHASE_3A_PRODUCTION_BLOCKERS.md phải nhắc clinical safety sign-off",
        "production migration approval": "PHASE_3A_PRODUCTION_BLOCKERS.md phải nhắc production migration approval",
        "live governance persistence": "PHASE_3A_PRODUCTION_BLOCKERS.md phải nhắc live governance persistence",
    }
    for token, message in required_phase3a_markers.items():
        if phase3a_text and token not in phase3a_lower:
            failures.append(message)

    if failures:
        return "FAIL", blocker_count, failures, warnings

    if blocker_count:
        status = "BLOCKED_FOR_PRODUCTION"
        warnings.append(
            "Clinical runtime/chronic-care: BLOCKED_FOR_PRODUCTION — "
            f"{blocker_count} blocker còn mở; không dùng dữ liệu bệnh nhân thật; AI phải tắt"
        )
    else:
        status = "NO_OPEN_BLOCKERS_DOCUMENTED"
        warnings.append(
            "Clinical runtime/chronic-care không còn bullet blocker trong tài liệu; "
            "cần ký duyệt lâm sàng/pháp lý thủ công trước khi đổi trạng thái production"
        )

    return status, blocker_count, failures, warnings


def research_completion_gate_failures() -> list[str]:
    """Smoke-check dossier gate: đủ cấu trúc nhưng vẫn require human review."""
    failures: list[str] = []
    if not REPO.exists():
        return ["không thấy medical-ebm-automation/ để kiểm research completion gates"]

    old_path = list(sys.path)
    try:
        sys.path.insert(0, str(REPO))
        from research_studio.project_schema import ResearchProject, StudyType
        from research_studio.research_completion_gates import evaluate_research_completion
        from research_studio.research_quality_checks import ResearchGateDecision
        from research_studio.research_workflow import (
            build_draft_mode_registry,
            build_research_registry,
            run_project,
        )
        from research_studio.study_type_router import get_template

        full_registry = build_research_registry()
        draft_registry = build_draft_mode_registry()
        project = ResearchProject(
            project_id="AUDIT-RESEARCH-COMPLETE",
            title="[SYNTHETIC] audit research completion gate",
            principal_investigator="PI-SYNTH-AUDIT",
            research_domain="audit",
            study_type=StudyType.RCT,
            clinical_question="Can the synthetic research gate complete a draft dossier?",
            pico_or_equivalent={"P": "synthetic", "I": "workflow", "C": "none", "O": "readiness"},
            objectives=["Validate automated research dossier completion gate"],
            outcomes=["draft dossier readiness"],
        )
        run = run_project(project)
        reporting = {"sections_addressed": get_template(project.study_type).required_sections}
        report = evaluate_research_completion(
            project,
            run.artifacts,
            reporting=reporting,
            full_registry=full_registry,
            draft_registry=draft_registry,
        )

        if run.blocked:
            failures.append(f"run_project bị BLOCK ngoài dự kiến: {run.block_reason}")
        if report.decision != ResearchGateDecision.REQUIRE_HUMAN_REVIEW:
            failures.append(f"completion gate decision={report.decision.value}, kỳ vọng REQUIRE_HUMAN_REVIEW")
        if report.missing_artifacts:
            failures.append("completion gate thiếu artifact: " + ",".join(report.missing_artifacts))
        if "REPORTING_CHECKLIST_DRAFT" not in report.present_artifacts:
            failures.append("completion gate không thấy REPORTING_CHECKLIST_DRAFT")
        if any(reason.startswith("GATE_AGENT_MATRIX:") for reason in report.reason_codes):
            failures.append("completion gate phát hiện agent matrix lệch")
        if not report.real_research_blocked:
            failures.append("completion gate không chặn real research execution")
        if not report.external_release_blocked:
            failures.append("completion gate không chặn external release")
    except Exception as exc:  # noqa: BLE001
        failures.append(f"không chạy được research completion gate smoke-check: {exc}")
    finally:
        sys.path = old_path

    return failures


def hard_gate_count_consistency_failures() -> list[str]:
    checker = ROOT / "tools" / "verify_hard_gate_count_consistency.py"
    if not checker.exists():
        return ["thiếu tools/verify_hard_gate_count_consistency.py"]
    code, out = run([sys.executable, str(checker), "--check"], cwd=ROOT)
    if code == 0:
        return []
    return [out.strip()[:1000] or "hard gate count consistency FAIL"]


def clinical_practice_apply_gate_failures() -> list[str]:
    checker = ROOT / "tools" / "verify_clinical_practice_apply_gate.py"
    if not checker.exists():
        return ["thiếu tools/verify_clinical_practice_apply_gate.py"]
    code, out = run([sys.executable, str(checker)], cwd=ROOT)
    if code == 0:
        return []
    return [out.strip()[:1000] or "clinical practice apply gate FAIL"]


def module_available(module: str) -> bool:
    py = str(VENV_PY if VENV_PY.exists() else sys.executable)
    code, _ = run([py, "-m", module, "--version"], cwd=REPO if REPO.exists() else ROOT)
    return code == 0


def git_dirty_summary() -> str:
    if not (REPO / ".git").exists():
        return "không có git repo"
    code, out = run(["git", "-c", f"safe.directory={REPO.as_posix()}", "status", "--short"], cwd=REPO)
    if code != 0:
        return "không đọc được git status"
    lines = [line for line in out.splitlines() if line.strip()]
    return "sạch" if not lines else f"{len(lines)} mục thay đổi/chưa theo dõi"


def main() -> int:
    configure_utf8_stdio()

    hard_errors: list[str] = []
    warnings: list[str] = []

    agent_sync_code, sync_out = run([sys.executable, "tools/sync_agents_to_codex.py", "--check"])
    if agent_sync_code != 0:
        hard_errors.append("Agent sync drift/FAIL")

    guard = count_agent_guardrails()
    n_autogen = registered_autogen_count()
    expected_agents = CORE_AGENT_COUNT + n_autogen
    if guard["source_agents"] != guard["codex_agents"]:
        hard_errors.append(
            f"Sync lệch: {guard['source_agents']} agent nguồn ≠ "
            f"{guard['codex_agents']} Codex")
    elif guard["source_agents"] != expected_agents:
        hard_errors.append(
            f"Số lượng agent = {guard['source_agents']}, kỳ vọng {expected_agents} "
            f"({CORE_AGENT_COUNT} lõi + {n_autogen} tự sinh đã đăng ký). "
            "Có agent thêm/bớt KHÔNG qua registry _TU-SINH-AGENT-REGISTRY.json.")
    if guard["source_guardrail"] != guard["source_agents"]:
        hard_errors.append("Chưa đủ guardrail trong agent nguồn")
    if guard["codex_guardrail"] != guard["codex_agents"]:
        hard_errors.append("Chưa đủ guardrail trong agent Codex")
    if guard["source_disclaimer"] != guard["source_agents"]:
        hard_errors.append("Chưa đủ disclaimer trong agent nguồn")

    checked_dash, dash_failures = verify_dashboards()
    if dash_failures:
        hard_errors.append("Dashboard offline FAIL: " + ", ".join(dash_failures[:10]))

    template_failures = template_sync_failures()
    if template_failures:
        hard_errors.append("Template dashboard lệch: " + "; ".join(template_failures))

    tool_sync_ran, tool_failures = tool_sync_failures()
    if tool_failures:
        hard_errors.append("Tool skill cap-nhat-chung-cu-y-khoa lệch bản: " + "; ".join(tool_failures))

    missing_default_files = default_file_failures()
    if missing_default_files:
        hard_errors.append("Thiếu file đồng bộ mặc định: " + ", ".join(missing_default_files))

    chatgpt_failures = chatgpt_integration_failures()
    if chatgpt_failures:
        hard_errors.append("Tích hợp ChatGPT thiếu/chưa chuẩn: " + "; ".join(chatgpt_failures))

    sync_health_ok, sync_health_summary, sync_health_errors = claude_codex_sync_health()
    if not sync_health_ok:
        hard_errors.append(
            "Claude/Codex sync health FAIL: " + "; ".join(sync_health_errors)
        )

    routine_failures = routine_layer_failures()
    if routine_failures:
        hard_errors.append("Lớp routine (Scheduled/) lệch tài liệu: " + "; ".join(routine_failures))

    antifacts_ok, antifacts_msg = antifacts_status()
    if not antifacts_ok:
        hard_errors.append("Antifacts FAIL: " + antifacts_msg)

    integrity_code, integrity_out = run(
        [sys.executable, "tools/integrity_guard.py", "--strict"],
        cwd=MASTER,
    )
    if integrity_code != 0:
        hard_errors.append("EBM_MASTER integrity_guard FAIL")

    compile_ok, compile_out = repo_compile_status()
    if not compile_ok:
        hard_errors.append("medical-ebm-automation compileall FAIL" + (f": {compile_out[:180]}" if compile_out else ""))

    env_ok, env_out = repo_environment_status()
    if not env_ok:
        warnings.append("Môi trường Python chưa đủ dependency; chạy 'Cài môi trường EBM' khi có mạng/quyền cài")

    approval_failures = approval_independence_failures()
    if approval_failures:
        hard_errors.append(
            "ApprovalLedger independence FAIL: " + "; ".join(approval_failures)
        )

    research_completion_failures = research_completion_gate_failures()
    if research_completion_failures:
        hard_errors.append(
            "Research completion gates FAIL: "
            + "; ".join(research_completion_failures)
        )

    hard_gate_count_failures = hard_gate_count_consistency_failures()
    if hard_gate_count_failures:
        hard_errors.append(
            "Research hard-gate doctrine consistency FAIL: "
            + "; ".join(hard_gate_count_failures)
        )

    clinical_apply_gate_failures = clinical_practice_apply_gate_failures()
    if clinical_apply_gate_failures:
        hard_errors.append(
            "Clinical practice apply gate FAIL: "
            + "; ".join(clinical_apply_gate_failures)
        )

    clinical_runtime_status, clinical_runtime_blockers, clinical_runtime_failures, clinical_runtime_warnings = (
        chronic_care_production_guard()
    )
    if clinical_runtime_failures:
        hard_errors.append(
            "Clinical runtime production guard FAIL: "
            + "; ".join(clinical_runtime_failures)
        )
    warnings.extend(clinical_runtime_warnings)

    pytest_ok = module_available("pytest")
    ruff_ok = module_available("ruff")
    if not pytest_ok:
        warnings.append("Chưa chạy được pytest bằng Python hiện tại (thiếu dependency hoặc venv chưa cài)")
    if not ruff_ok:
        warnings.append("Chưa chạy được ruff bằng Python hiện tại (thiếu dependency hoặc venv chưa cài)")

    launchd_drift = launchd_registration_drift()
    if launchd_drift:
        warnings.append(
            "Lịch nền launchd LỆCH giữa đĩa và bộ nhớ (job sẽ KHÔNG tự chạy đúng cho tới khi "
            "nạp lại): " + "; ".join(launchd_drift)
        )

    # S1/S2 — kiểm chứng đồ thị định tuyến agent (vá 2026-07-04: trước đây tuyên bố
    # "không mồ côi/không tham chiếu treo" ở _BAN-DO-KET-NOI.md là văn xuôi thủ công,
    # chưa có công cụ nào kiểm lại bằng máy). Đã xác nhận CHẠY SẠCH lần đầu trên hệ
    # thật (0 dangling). CHỈ đặt là WARNING (không hard_errors) ở LẦN TÍCH HỢP ĐẦU —
    # cần vài lần chạy sạch liên tiếp mới đủ tin cậy để nâng thành cổng cứng, tránh
    # audit đột ngột FAIL vì một dương tính giả bộ lọc chưa lường hết.
    try:
        import verify_agent_routing as _routing
        routing_rep = _routing.audit_routing()
        if routing_rep["dangling_references"]:
            warnings.append(
                "Tham chiếu agent TREO trong nhạc trưởng: "
                + ", ".join(routing_rep["dangling_references"]))
        if routing_rep["orphan_agents"]:
            warnings.append(
                f"{len(routing_rep['orphan_agents'])} agent không được nhạc trưởng "
                "gọi trực tiếp (có thể vẫn hợp lệ nếu bác sĩ gọi tay): "
                + ", ".join(routing_rep["orphan_agents"]))
    except Exception as _e:  # noqa: BLE001
        warnings.append(f"Không chạy được kiểm chứng định tuyến agent: {_e}")

    # Audit 2026-07-11: git_dirty_summary() (medical-ebm repo only — sync_safety_check.py
    # là công cụ CHÍNH kiểm sức khỏe git cả 2 repo) từng chỉ in cho biết, không hề ảnh
    # hưởng PASS/FAIL dù chính "không đọc được git status" là dấu hiệu hỏng index/object.
    git_summary = git_dirty_summary()
    if git_summary == "không đọc được git status":
        warnings.append("medical-ebm-automation: không đọc được git status — kiểm tra "
                         "sync_safety_check.py, có thể là dấu hiệu .git hỏng")

    counts = master_counts()
    stale_count_failures = living_document_count_failures(counts["cards"])
    if stale_count_failures:
        hard_errors.append(
            "Sổ hạ tầng trạng thái sống hardcode sai số thẻ EBM_MASTER: "
            + "; ".join(stale_count_failures)
        )
    if counts["missing_trace"]:
        hard_errors.append(f"EBM_MASTER còn {counts['missing_trace']} thẻ thiếu truy nguyên")
    if counts["apply_unverified"]:
        hard_errors.append(f"EBM_MASTER còn {counts['apply_unverified']} thẻ apply chưa/cần xác minh")
    if counts["unverified_queue"]:
        warnings.append(f"{counts['unverified_queue']} thẻ đang ở hàng chưa/cần xác minh, không áp dụng tự động")
    if counts["quarantined_cards"]:
        warnings.append(f"{counts['quarantined_cards']} thẻ đã cách ly khỏi evidence_cards vì thiếu truy nguyên")

    print("================================================================")
    print("AUDIT TỔNG THỂ — EBM Copilot")
    print("================================================================")
    print("Agent sync:", "PASS" if agent_sync_code == 0 else "FAIL")
    print(
        "Agent guardrail: "
        f"{guard['source_guardrail']}/{guard['source_agents']} nguồn, "
        f"{guard['codex_guardrail']}/{guard['codex_agents']} Codex; "
        f"disclaimer {guard['source_disclaimer']}/{guard['source_agents']}"
    )
    print(f"Dashboard offline: {checked_dash} kiểm, {len(dash_failures)} lỗi")
    print("Template sync:", "PASS" if not template_failures else "FAIL")
    if not tool_sync_ran:
        print("Tool sync: SKIP (< 2/3 thư mục tồn tại — không có bản để đối chiếu, vd đang chạy trong worktree)")
    else:
        print("Tool sync:", "PASS" if not tool_failures else "FAIL: " + "; ".join(tool_failures))
    print("Default folder:", "PASS" if not missing_default_files else "FAIL")
    print("ChatGPT integration:", "PASS" if not chatgpt_failures else "FAIL")
    print("Claude/Codex sync health:", sync_health_summary)
    print("Routine layer (Scheduled/):", "PASS" if not routine_failures else "FAIL: " + "; ".join(routine_failures))
    print("Antifacts:", antifacts_msg if antifacts_ok else "FAIL")
    print("Repo compile:", "PASS" if compile_ok else "FAIL")
    print("Runtime deps:", "PASS" if env_ok else "WARN")
    print("Approval independence:", "PASS" if not approval_failures else "FAIL")
    print("Research completion gates:", "PASS" if not research_completion_failures else "FAIL")
    print("Research hard-gate doctrine:", "PASS" if not hard_gate_count_failures else "FAIL")
    print("Clinical practice apply gate:", "PASS" if not clinical_apply_gate_failures else "FAIL")
    print(
        "Clinical runtime:",
        f"{clinical_runtime_status} ({clinical_runtime_blockers} blocker)"
        if clinical_runtime_status != "FAIL"
        else "FAIL",
    )
    print("Repo worktree:", git_summary)
    print("Dev tools:", f"pytest={'yes' if pytest_ok else 'no'}, ruff={'yes' if ruff_ok else 'no'}")
    print(
        "EBM_MASTER: "
        f"{counts['cards']} thẻ chính "
        f"({counts['apply']} apply · {counts['consider']} consider · {counts['notyet']} notyet), "
        f"{counts['quarantined_cards']} cách ly"
    )
    print(f"Thiếu truy nguyên trong evidence_cards: {counts['missing_trace']}")
    print(f"Apply chưa/cần xác minh: {counts['apply_unverified']}")
    if warnings:
        print("----------------------------------------------------------------")
        for warn in warnings:
            print("⚠", warn)
    if hard_errors:
        print("----------------------------------------------------------------")
        print("KẾT QUẢ: FAIL")
        for err in hard_errors:
            print("⛔", err)
        return 1
    print("----------------------------------------------------------------")
    print("KẾT QUẢ: PASS — đạt chuẩn vận hành an toàn ở mức trợ lý EBM có bác sĩ duyệt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
