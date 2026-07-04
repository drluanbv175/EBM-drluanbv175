#!/usr/bin/env python3
"""Audit tổng thể hệ Agent + Dashboard + EBM_MASTER.

Chạy từ thư mục gốc:
  python3 tools/audit_ebm_system.py

Mặc định chỉ dùng kiểm offline để chạy nhanh và không cần mạng. Muốn xác minh online PMID
cho một dashboard quan trọng, chạy riêng `verify_dashboard.py --online`.
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
        ROOT / "dashboard_mockups" / "templates" / "dark-analyst-template.html",
        MASTER / "skill_assets" / "web-dashboard-dark-analyst.html",
    ),
]
CHATGPT_REQUIRED_FILES = [
    CHATGPT_EXPORT / "CHATGPT_EBM_AGENT_SYSTEM_PROMPT.md",
    CHATGPT_EXPORT / "README_TICH_HOP_CHATGPT.md",
    CHATGPT_EXPORT / "STARTER_PROMPTS.md",
    CHATGPT_EXPORT / "INTEGRATION_CHECKLIST.md",
]
SCHEDULED = ROOT / "Scheduled"
BAN_DO_KET_NOI = AGENTS_SRC / "_BAN-DO-KET-NOI.md"
ROUTINE_WIRING = AGENTS_SRC / "_ROUTINE-AGENT-WIRING.md"


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
            and ("chưa" in str(c.get("verification_status", "")).lower()
                 or "cần" in str(c.get("verification_status", "")).lower())
            for c in cards
        ),
        "unverified_queue": sum(
            "chưa" in str(c.get("verification_status", "")).lower()
            or "cần" in str(c.get("verification_status", "")).lower()
            for c in cards
        ),
        "apply": sum(c.get("decision") == "apply" for c in cards),
        "consider": sum(c.get("decision") == "consider" for c in cards),
        "notyet": sum(c.get("decision") == "notyet" for c in cards),
    }


def verify_dashboards() -> tuple[int, list[str]]:
    verifier = DASH / "tools" / "verify_dashboard.py"
    failures: list[str] = []
    checked = 0
    for html in sorted(DASH.glob("WebDashboard_EBM_*.html")):
        checked += 1
        code, _out = run([sys.executable, str(verifier), str(html)], cwd=ROOT)
        if code != 0:
            failures.append(html.name)
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

    missing_default_files = default_file_failures()
    if missing_default_files:
        hard_errors.append("Thiếu file đồng bộ mặc định: " + ", ".join(missing_default_files))

    chatgpt_failures = chatgpt_integration_failures()
    if chatgpt_failures:
        hard_errors.append("Tích hợp ChatGPT thiếu/chưa chuẩn: " + "; ".join(chatgpt_failures))

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

    pytest_ok = module_available("pytest")
    ruff_ok = module_available("ruff")
    if not pytest_ok:
        warnings.append("Chưa chạy được pytest bằng Python hiện tại (thiếu dependency hoặc venv chưa cài)")
    if not ruff_ok:
        warnings.append("Chưa chạy được ruff bằng Python hiện tại (thiếu dependency hoặc venv chưa cài)")

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

    counts = master_counts()
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
    print("Default folder:", "PASS" if not missing_default_files else "FAIL")
    print("ChatGPT integration:", "PASS" if not chatgpt_failures else "FAIL")
    print("Routine layer (Scheduled/):", "PASS" if not routine_failures else "FAIL: " + "; ".join(routine_failures))
    print("Antifacts:", antifacts_msg if antifacts_ok else "FAIL")
    print("Repo compile:", "PASS" if compile_ok else "FAIL")
    print("Runtime deps:", "PASS" if env_ok else "WARN")
    print("Repo worktree:", git_dirty_summary())
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
