#!/usr/bin/env python3
"""assess_agent_system.py — TỰ ĐÁNH GIÁ hệ Agent theo BỘ TIÊU CHÍ 13 mục.

Biến bộ tiêu chí "một Agent tốt / một hệ Agent tốt" thành CHECK CHẠY ĐƯỢC, khách
quan, lặp lại được — nhờ đó tính "có thể kiểm chứng" + "đánh giá hiệu suất" của
chính hệ trở thành số liệu, không phải lời tự khen.

7 tiêu chí AGENT:  A1 nhận biết môi trường · A2 lập kế hoạch · A3 suy luận ·
                   A4 dùng công cụ · A5 bộ nhớ dài+ngắn · A6 tự đánh giá & sửa lỗi ·
                   A7 an toàn/ổn định/kiểm chứng
6 tiêu chí HỆ:     S1 kiến trúc rõ · S2 phối hợp agent · S3 pipeline nhiệm vụ ·
                   S4 mở rộng · S5 giám sát/guardrail/rủi ro · S6 đánh giá hiệu suất

Mỗi tiêu chí = nhiều PROBE (kiểm khách quan: file tồn tại · marker code · công cụ
exit 0 · đếm ngưỡng). Trạng thái: strong (mọi probe ✓) · partial (một phần) ·
gap (không/yếu). KHÔNG thổi điểm: probe là sự thật kiểm được, không phải ý kiến.

Dùng:
  python tools/assess_agent_system.py            # nhanh (file/marker/đếm)
  python tools/assess_agent_system.py --deep      # + chạy audit/retry/generate thật
  python tools/assess_agent_system.py --json      # in JSON
Xuất: in bảng điểm + ghi .claude/agents/_HE-THONG-SCORECARD.json
Mã thoát: 0 nếu KHÔNG tiêu chí nào 'gap/absent'; 1 nếu có lỗ thật.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / ".claude" / "agents"
TOOLS = ROOT / "tools"
MT = ROOT / "medical-ebm-automation" / "tools"
TESTS = ROOT / "medical-ebm-automation" / "tests"
MASTER = ROOT / "EBM_MASTER"

# (ok, detail) — một probe khách quan.
Probe = Tuple[bool, str]


# ── Tiện ích probe ──────────────────────────────────────────────────────────
def p_exists(rel: Path, label: str) -> Probe:
    return (rel.exists(), f"{label}: {'có' if rel.exists() else 'THIẾU'} ({rel.name})")


def p_contains(rel: Path, needle: str, label: str) -> Probe:
    if not rel.exists():
        return (False, f"{label}: THIẾU file {rel.name}")
    ok = needle in rel.read_text(encoding="utf-8", errors="ignore")
    return (ok, f"{label}: {'✓' if ok else '✗'} ({rel.name})")


def p_contains_all(rel: Path, needles: List[str], label: str) -> Probe:
    """Kiểm một file có đủ marker bắt buộc; dùng cho hợp đồng liên-module."""
    if not rel.exists():
        return (False, f"{label}: THIẾU file {rel.name}")
    text = rel.read_text(encoding="utf-8", errors="ignore")
    missing = [needle for needle in needles if needle not in text]
    ok = not missing
    detail = f"{label}: {'✓' if ok else '✗'} ({rel.name}; {len(needles) - len(missing)}/{len(needles)} marker)"
    if missing:
        detail += " thiếu " + ", ".join(missing[:4])
    return (ok, detail)


def p_count(n: int, threshold: int, label: str) -> Probe:
    return (n >= threshold, f"{label}: {n} (ngưỡng ≥{threshold})")


def p_glob(base: Path, pattern: str, threshold: int, label: str) -> Probe:
    n = len(list(base.glob(pattern))) if base.exists() else 0
    return (n >= threshold, f"{label}: {n} khớp '{pattern}' (≥{threshold})")


def p_run(cmd: List[str], label: str, timeout: int = 300,
          need_rc: int = 0) -> Probe:
    """Chạy công cụ thật — probe MẠNH NHẤT (kiểm chứng bằng thực thi)."""
    try:
        env = os.environ.copy()
        env.setdefault("PYTHONIOENCODING", "utf-8")
        env.setdefault("PYTHONPYCACHEPREFIX", str(Path(tempfile.gettempdir()) / "ebm_pycache"))
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True,
                              text=True, timeout=timeout, env=env)
        ok = proc.returncode == need_rc
        return (ok, f"{label}: exit={proc.returncode} (cần {need_rc}) {'✓' if ok else '✗'}")
    except Exception as e:  # noqa: BLE001
        return (False, f"{label}: LỖI chạy ({str(e)[:60]})")


def _ledger_cards() -> int:
    p = MASTER / "EBM_MASTER.json"
    if not p.exists():
        return 0
    try:
        return len(json.loads(p.read_text(encoding="utf-8")).get("evidence_cards", []))
    except (json.JSONDecodeError, OSError):
        return 0


def _agent_count() -> int:
    return len([p for p in AGENTS.glob("*.md")
                if p.name != "README.md" and not p.name.startswith("_")])


# ── Định nghĩa 13 tiêu chí + probe (deep=probe chạy công cụ thật) ────────────
def build_criteria(deep: bool, py: str) -> List[Dict]:
    C: List[Dict] = []

    def crit(cid, name, level, probes):
        C.append({"id": cid, "name": name, "level": level, "probes": probes})

    # ---- AGENT ----
    crit("A1", "Nhận biết môi trường", "agent", [
        lambda: p_exists(MT / "pipeline_freshness.py", "Freshness guard (phát hiện checkpoint cũ)"),
        lambda: p_contains(MT / "gate_contract.py", "ensure_study_meta", "Đọc/PIN trạng thái study_meta"),
        lambda: p_contains(MT / "run_g0_auto.py", "_is_vietnamese_topic", "Nhận diện ngữ cảnh VN/EN"),
        lambda: p_contains(AGENTS / "dieu-phoi-nghien-cuu.md", "BƯỚC 0", "Kiểm tiền đề (đọc sổ cái/checkpoint)"),
    ])
    crit("A2", "Lập kế hoạch", "agent", [
        lambda: p_contains(MT / "run_pipeline.py", "GATE_ORDER", "Kế hoạch cổng G0→G10"),
        lambda: p_contains(AGENTS / "dieu-phoi-nghien-cuu.md", "GIAO THỨC TỰ ĐỘNG", "Giao thức tự động (suy loại thiết kế)"),
        lambda: p_contains(AGENTS / "dieu-phoi-lam-sang.md", "5 bước", "Kế hoạch lâm sàng 5 bước EBM"),
        lambda: (deep and p_run([py, str(TOOLS / "run_orchestrator.py"), "--validate"],
                                "Orchestrator control-plane validate PASS", 30)) or
                p_exists(TOOLS / "orchestrator" / "orchestrator.py", "Orchestrator control-plane có mặt"),
    ])
    crit("A3", "Suy luận", "agent", [
        lambda: p_contains(AGENTS / "cau-hoi-nghien-cuu.md", "FINER", "PICO/FINER"),
        lambda: p_contains(AGENTS / "tham-dinh-grade-nnt.md", "GRADE", "GRADE/NNT"),
        lambda: p_contains(AGENTS / "chan-doan-xac-suat.md", "LR", "Suy luận Bàyes (LR)"),
        lambda: p_contains(MT / "run_g3_auto.py", "n_log_rank", "Công thức thống kê THẬT (cỡ mẫu NC)"),
        # VÁ 2026-07-04: máy tính suy luận LÂM SÀNG chạy được — Bayes/ngưỡng
        # test-treat/NNT-ARR/GRADE (medical-ebm-automation/tools/clinical_calc.py).
        lambda: p_contains(MT / "clinical_calc.py", "def grade_rating", "Máy tính lâm sàng chạy được (Bayes/ngưỡng/NNT/GRADE)"),
        lambda: p_contains_all(
            MT / "meta_analysis_calc.py",
            ["pool_effects", "random_effect", '"ci"', "prediction_interval"],
            "Engine phân tích gộp xuất effect size/CI/PI",
        ),
    ])
    crit("A4", "Dùng công cụ", "agent", [
        lambda: p_glob(MT, "run_g*_auto.py", 10, "Công cụ cổng G0–G10"),
        lambda: p_exists(MT / "run_stats_analysis.py", "Engine thống kê Python"),
        lambda: p_exists(TOOLS / "generate_agent.py", "Công cụ tự sinh agent"),
        lambda: (deep and p_run([py, "-m", "py_compile", str(MT / "run_pipeline.py")],
                                "Công cụ import/compile được", 60)) or
                p_exists(MT / "run_pipeline.py", "Orchestrator có mặt"),
    ])
    crit("A5", "Bộ nhớ dài hạn + ngắn hạn", "agent", [
        lambda: p_count(_ledger_cards(), 1, "Sổ cái dài hạn EBM_MASTER (số thẻ)"),
        lambda: p_contains(AGENTS / "so-cai-ghi-nho.md", "AUTO-CP", "Checkpoint tạm (ngắn hạn, mỗi 3 output)"),
        lambda: p_exists(AGENTS / "_SO-TRANG-THAI-CHECKPOINT.md", "Schema sổ trạng thái (resume)"),
        lambda: p_contains(MT / "gate_contract.py", "study_meta", "PIN tham số bền qua phiên"),
    ])
    crit("A6", "Tự đánh giá và sửa lỗi", "agent", [
        lambda: p_exists(AGENTS / "tham-dinh-dau-ra.md", "Guardrail 2 lớp (completeness-critic)"),
        lambda: p_exists(AGENTS / "_KIEM-DUYET-DOC-LAP.md", "Kiểm duyệt độc lập"),
        lambda: (deep and p_run([py, str(MT / "retry_loop.py"), "--demo"],
                                "Vòng tự sửa retry_loop CHẠY THẬT", 60)) or
                p_contains(MT / "retry_loop.py", "class RetryLoop", "Vòng tự sửa (code)"),
        lambda: p_contains(MT / "run_pipeline.py", "blocked_missing_input", "Hợp đồng DỪNG (tự phát hiện thiếu input)"),
        # VÁ 2026-07-04: retry_loop nay được IMPORT THẬT bởi tools/eval/run_eval.py
        # (--classify) — run_eval.py chính nó đã là phụ thuộc sản xuất của
        # cafes_suite.py, nên retry_loop không còn là thư viện không ai gọi.
        lambda: p_contains(TOOLS / "eval" / "run_eval.py", "import retry_loop", "retry_loop nối vào run_eval.py --classify (production, qua cafes_suite)"),
        lambda: p_contains_all(
            MT / "audit_research_gates.py",
            ["ACTION_QUEUE_JSON", "resume_contract", "next_agent_action"],
            "Audit cổng sinh action queue + resume contract",
        ),
    ])
    crit("A7", "An toàn, ổn định, kiểm chứng", "agent", [
        lambda: p_exists(AGENTS / "_HIEN-PHAP-LIEM-CHINH.md", "Hiến pháp liêm chính"),
        lambda: p_exists(AGENTS / "_CHUAN-CHAT-LUONG-MEDPALM.md", "Chuẩn chất lượng Med-PaLM"),
        lambda: p_glob(TESTS, "test_*.py", 40, "Bộ test tự động (file)"),
        lambda: (deep and p_run([py, str(TOOLS / "audit_ebm_system.py")],
                                "Audit hệ PASS (kiểm chứng)", 300)) or
                p_exists(TOOLS / "audit_ebm_system.py", "Công cụ audit có mặt"),
        lambda: p_exists(TOOLS / "verify_research_practical_readiness.py", "Verifier thực tiễn dữ liệu nghiên cứu"),
    ])

    # ---- HỆ ----
    crit("S1", "Kiến trúc rõ ràng", "system", [
        lambda: p_count(_agent_count(), 40, "Số agent chuyên trách"),
        lambda: p_exists(AGENTS / "README.md", "Bản đồ đội agent"),
        lambda: p_exists(AGENTS / "_BAN-DO-KET-NOI.md", "Bản đồ kết nối"),
        lambda: p_glob(AGENTS, "dieu-phoi-*.md", 2, "Nhạc trưởng (đa-agent)"),
        # KIỂM CHỨNG BẰNG MÁY (không chỉ văn xuôi): không agent nào mồ côi hoàn toàn
        # khỏi cả 2 nhạc trưởng (vá 2026-07-04 — trước đây tuyên bố này là thủ công).
        lambda: (deep and p_run([py, str(TOOLS / "verify_agent_routing.py")],
                                "Kiểm định tuyến agent chạy được", 30)) or
                p_exists(TOOLS / "verify_agent_routing.py", "Công cụ kiểm định tuyến có mặt"),
    ])
    crit("S2", "Phối hợp giữa các agent", "system", [
        lambda: p_exists(AGENTS / "_CROSSWALK-NGHIEN-CUU.md", "Crosswalk vai/cổng/artifact"),
        lambda: p_exists(AGENTS / "_ROUTINE-AGENT-WIRING.md", "Wiring routine↔agent"),
        lambda: p_contains(AGENTS / "dieu-phoi-nghien-cuu.md", "agent con", "Dispatch agent con"),
        # Không tham chiếu TREO (tên trông như agent nhưng không khớp file nào) —
        # kiểm bằng máy, không phải khẳng định thủ công.
        lambda: (deep and p_run([py, str(TOOLS / "verify_agent_routing.py"), "--strict"],
                                "0 tham chiếu treo (--strict)", 30)) or
                p_exists(TOOLS / "verify_agent_routing.py", "Công cụ kiểm định tuyến có mặt"),
        lambda: (deep and p_run([py, str(TOOLS / "orchestrator" / "tests" / "test_orchestrator.py")],
                                "Orchestrator 23 test (bàn giao/nhánh điều kiện) PASS", 30)) or
                p_exists(TOOLS / "orchestrator" / "flows.py", "Flow điều phối agent↔agent có mặt"),
    ])
    crit("S3", "Pipeline xử lý nhiệm vụ", "system", [
        lambda: p_contains(MT / "run_pipeline.py", "orchestrate", "Pipeline G0→G10 (code)"),
        lambda: p_exists(AGENTS / "_SO-DO-PIPELINE-HOP-NHAT.md", "Sơ đồ pipeline hợp nhất"),
        lambda: p_exists(AGENTS / "_VONG-LAP-KHEP-KIN.md", "Vòng lặp khép kín"),
        lambda: p_contains_all(
            MT / "audit_research_gates.py",
            ["release_contract", "can_release_to_next_gate", "prevents_downstream", "gate_release_summary"],
            "Hợp đồng phát hành từng cổng nghiên cứu",
        ),
        lambda: p_contains_all(
            TOOLS / "verify_research_practical_readiness.py",
            ["deidentify_dataset", "pseudonymize_dataset", "clean_dataset", "lock_dataset", "audit_gates"],
            "Pipeline dữ liệu thật synthetic đi tới audit G6",
        ),
    ])
    crit("S4", "Khả năng mở rộng", "system", [
        lambda: p_exists(TOOLS / "generate_agent.py", "Tự sinh agent (code)"),
        lambda: p_exists(AGENTS / "_TU-SINH-AGENT.md", "Giao thức tự sinh"),
        lambda: p_exists(AGENTS / "_TU-SINH-AGENT-REGISTRY.json", "Registry agent tự sinh"),
        lambda: (deep and p_run([py, str(TOOLS / "generate_agent.py"), "--name",
                                 "probe-check", "--description", "probe", "--role",
                                 "probe", "--dry-run"], "generate_agent chạy (dry-run)", 60)) or
                p_exists(TOOLS / "sync_agents_to_codex.py", "Sync mở rộng có mặt"),
    ])
    crit("S5", "Giám sát, guardrail, kiểm soát rủi ro", "system", [
        lambda: (deep and p_run([py, str(TOOLS / "audit_ebm_system.py")],
                                "Audit registry-aware PASS", 300)) or
                p_exists(TOOLS / "audit_ebm_system.py", "Audit hệ có mặt"),
        lambda: p_exists(TOOLS / "enforce_agent_guardrails.py", "Cấy guardrail bắt buộc"),
        lambda: p_contains(MT / "run_pipeline.py", "HARD_GATE_SIGNAL", "Cổng cứng + báo trung thực"),
        lambda: p_exists(MT / "gen_morning_brief.py", "Giám sát định kỳ (morning brief)"),
        lambda: p_contains_all(
            MT / "audit_research_gates.py",
            ["HUMAN_EVIDENCE_REQUIRED", "AUTO_RUN_ALLOWED", "Không chuyển cổng downstream"],
            "Cổng nghiên cứu chặn downstream khi thiếu bằng chứng thật",
        ),
        lambda: (deep and p_run([py, str(TOOLS / "verify_research_gate_contracts.py")],
                                "Smoke-test hợp đồng cổng nghiên cứu PASS", 60)) or
                p_exists(TOOLS / "verify_research_gate_contracts.py", "Verifier hợp đồng cổng nghiên cứu có mặt"),
        lambda: (deep and p_run([py, str(TOOLS / "verify_research_practical_readiness.py")],
                                "Smoke-test thực tiễn dữ liệu nghiên cứu PASS", 90)) or
                p_exists(TOOLS / "verify_research_practical_readiness.py", "Verifier thực tiễn dữ liệu nghiên cứu có mặt"),
        lambda: (deep and p_run([py, str(TOOLS / "verify_controlled_research_automation.py")],
                                "Smoke-test thẩm định/phản biện/thống kê có kiểm soát PASS", 90)) or
                p_exists(TOOLS / "verify_controlled_research_automation.py", "Verifier tự động có kiểm soát có mặt"),
        lambda: p_contains_all(
            TOOLS / "build_research_readiness_evidence.py",
            ["EvidenceRow", "blocking_failure_count", "verify_controlled_research_automation.py", "Cần bác sĩ kiểm chứng"],
            "Bảng chứng cứ thực tiễn có thể sinh lại",
        ),
    ])
    crit("S6", "Đánh giá hiệu suất", "system", [
        lambda: p_exists(TOOLS / "eval" / "cafes_suite.py", "Bộ eval CAFÉ-S (code)"),
        lambda: p_exists(TOOLS / "eval" / "run_eval.py", "Chấm rule-based (code)"),
        lambda: p_exists(TOOLS / "eval" / "human_eval_score.py", "Chấm người (κ/Likert)"),
        lambda: p_exists(TOOLS / "eval" / "cases_50_vignettes.md", "50 vignette kiểm chứng"),
        lambda: p_contains_all(
            TOOLS / "verify_controlled_research_automation.py",
            ["appraisal_guardrail", "peer_review_control", "statistics_control", "overall_status"],
            "Verifier hợp nhất thẩm định/phản biện/thống kê",
        ),
    ])
    return C


STATUS_ICON = {"strong": "🟢", "partial": "🟡", "gap": "🔴", "absent": "⛔"}

# GIỚI HẠN TRƯỞNG THÀNH trung thực (không thổi điểm) — cơ chế có thể TỒN TẠI +
# CHẠY nhưng chưa TRƯỞNG THÀNH đủ. Nêu rõ để bác sĩ biết mức thật.
CAVEATS: Dict[str, List[str]] = {
    "A2": ["2026-07-04 (vá): đã dựng `tools/orchestrator/` — control-plane CHẠY ĐƯỢC cho CẢ HAI "
           "nhánh (lâm sàng 8 bước có nhánh điều kiện + nghiên cứu G0–G9), grounded vào registry "
           "50 agent .md THẬT (không hardcode), 23 test offline PASS. GIỚI HẠN CÒN LẠI (trung "
           "thực, không thổi phồng): đây là lớp ĐỊNH TUYẾN + LẬP KẾ HOẠCH + CỔNG quyết định "
           "(dry-run) — nó CHƯA tự gọi LLM để agent thực thi thật; seam `LLMExecutor` đã có sẵn "
           "nhưng cần cắm wrapper Codex/API `[CẦN MÔI TRƯỜNG HỖ TRỢ]`. Việc thực thi agent thật "
           "hiện vẫn qua Agent/Task tool của phiên Claude Code, không phải orchestrator tự chạy."],
    "S2": ["2026-07-04 (vá): orchestrator control-plane nay tham chiếu THẲNG 50 agent .md qua "
           "registry (không phải script cổng run_g*_auto.py) — `--validate` xác nhận 0 tham "
           "chiếu treo giữa flow ⇄ registry. Bàn giao agent↔agent trong plan là DETERMINISTIC "
           "(mã hoá trong flows.py, có điều kiện qua signals.py), không còn hoàn toàn do LLM lúc "
           "chạy tự quyết. GIỚI HẠN CÒN LẠI: tín hiệu ngữ cảnh (signals.py) là khớp từ khóa minh "
           "bạch, KHÔNG phải NLU — plan là ước lượng tốt hơn, agent thật khi chạy vẫn tự xác "
           "nhận lại bối cảnh."],
    "S4": ["Registry tự sinh còn RỖNG — cơ chế đã test đầu-cuối nhưng chưa dùng "
           "cho ca production nào (không thể fabricate việc dùng thật)."],
    "S6": ["Chấm rule-based + CAFÉ-S chạy được, nay CÓ phân loại lỗi qua retry_loop "
           "(--classify); đánh giá NGƯỜI (κ/Likert) còn CHỜ → vòng đánh giá hiệu "
           "suất chưa khép hoàn toàn (cần bác sĩ/chuyên gia chấm mù thật)."],
}


def assess(deep: bool) -> Dict:
    py = sys.executable
    criteria = build_criteria(deep, py)
    rows = []
    for c in criteria:
        results = [pr() for pr in c["probes"]]
        n_ok = sum(1 for ok, _ in results if ok)
        n = len(results)
        if n_ok == n:
            status = "strong"
        elif n_ok == 0:
            status = "absent"
        elif n_ok >= max(1, (n + 1) // 2):
            status = "strong" if n_ok == n else "partial"
        else:
            status = "gap"
        rows.append({
            "id": c["id"], "name": c["name"], "level": c["level"],
            "status": status, "passed": n_ok, "total": n,
            "probes": [{"ok": ok, "detail": d} for ok, d in results],
            "caveats": CAVEATS.get(c["id"], []),
        })
    n_strong = sum(1 for r in rows if r["status"] == "strong")
    n_partial = sum(1 for r in rows if r["status"] == "partial")
    n_weak = sum(1 for r in rows if r["status"] in ("gap", "absent"))
    return {
        "mode": "deep" if deep else "fast",
        "summary": {"strong": n_strong, "partial": n_partial, "weak": n_weak,
                    "total": len(rows)},
        "criteria": rows,
    }


def print_report(rep: Dict) -> None:
    print("\n" + "=" * 66)
    print("  TỰ ĐÁNH GIÁ HỆ AGENT — 13 TIÊU CHÍ  (chế độ: "
          f"{rep['mode']})")
    print("=" * 66)
    print("  🟢 strong · 🟡 partial · 🔴 gap · ⛔ absent · ⚠ = giới hạn trưởng thành")
    print("  (probe = kiểm KHÁCH QUAN: file/marker/đếm/exit-code; KHÔNG tự khen)")
    lvl = None
    for r in rep["criteria"]:
        if r["level"] != lvl:
            lvl = r["level"]
            print(f"\n── {'AGENT' if lvl == 'agent' else 'HỆ THỐNG'} ──")
        icon = STATUS_ICON[r["status"]]
        print(f"  {icon} [{r['id']}] {r['name']:<34} {r['passed']}/{r['total']} probe")
        for pr in r["probes"]:
            if not pr["ok"]:
                print(f"        ✗ {pr['detail']}")
        for cv in r.get("caveats", []):
            print(f"        ⚠ giới hạn: {cv}")
    s = rep["summary"]
    print("\n" + "-" * 66)
    print(f"  TỔNG: 🟢 strong {s['strong']} · 🟡 partial {s['partial']} · "
          f"🔴/⛔ yếu {s['weak']}  / {s['total']} tiêu chí")
    if s["weak"] > 0:
        verdict = f"CÒN {s['weak']} TIÊU CHÍ YẾU (gap/absent) — xem ✗ ở trên"
    elif s["partial"] > 0:
        verdict = (f"VỮNG NỀN — {s['strong']}/13 strong; {s['partial']} partial còn "
                   "giới hạn trưởng thành (xem ⚠), KHÔNG có lỗ hổng cứng")
    else:
        verdict = "ĐẠT — hệ vững ở mọi tiêu chí"
    print(f"  KẾT: {verdict}")
    print("  → Cần bác sĩ kiểm chứng. Đây là tự-đánh-giá cấu trúc, không thay "
          "thẩm định lâm sàng.")
    print("=" * 66)


def main() -> int:
    ap = argparse.ArgumentParser(description="Tự đánh giá hệ Agent theo 13 tiêu chí.")
    ap.add_argument("--deep", action="store_true",
                    help="Chạy công cụ THẬT (audit/retry/generate) — chậm hơn, kiểm chứng mạnh")
    ap.add_argument("--json", action="store_true", help="In JSON")
    ap.add_argument("--out", default=str(AGENTS / "_HE-THONG-SCORECARD.json"),
                    help="Đường dẫn ghi scorecard JSON")
    args = ap.parse_args()

    rep = assess(args.deep)
    try:
        Path(args.out).write_text(json.dumps(rep, ensure_ascii=False, indent=2),
                                  encoding="utf-8")
        rep["scorecard_json"] = args.out
    except OSError:
        pass

    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        print_report(rep)
    return 0 if rep["summary"]["weak"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
