"""guardrail_bridge.py — Cầu nối D1↔D3: biến cổng rule-based THẬT thành `guardrail_verdict`.

Làm cho cổng QA CHẠY THẬT trên NỘI DUNG THẬT từ RUNTIME điều phối (không chỉ unit-test):
  • D1 — cắt bản ghi phán quyết APPRAISAL bền (observability/APPRAISALS.jsonl) mỗi lần chấm;
    tên file KHỬ PII; đếm tái phạm dedup-theo-output; ứng viên đề bạt (human-gate).
  • D3 — map verdict rule-based → pass / returned_for_fix để `Orchestrator.handle` re-route
    (trích dẫn không phân giải → kiem-chung-trich-dan…).

KHÔNG cần LLM: dùng `run_eval.evaluate` (cổng rule-based đã ổn định, chấm text thật). Tự chứa
emitter (không phụ thuộc phần chưa-commit của run_eval) để commit sạch, không đụng Phase B.

Giới hạn trung thực: đây gate + re-route trên nội dung ĐÃ CÓ. Việc agent SINH LẠI bản sửa thật
vẫn cần `LLMExecutor` (API key/env) — ngoài phạm vi cầu này; khi output không đổi, cổng đúng
mực sẽ leo thang bác sĩ sau ≤ MAX_RETRIES thay vì giả vờ đã sửa.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys

from . import ROOT

APPRAISAL_LOG = ROOT / "observability" / "APPRAISALS.jsonl"
APPRAISAL_REPEATS = ROOT / "observability" / "APPRAISAL_REPEATS.json"
PROMOTE_THRESHOLD = 3
_EXCLUDE_SOURCES = {"corpus", "test", "batch", "ci"}          # không tính vào tái phạm (nhiễu)
# Mã VỐN đã là cổng cứng (ESCALATE_HARD) — KHÔNG đề bạt lại (M2).
# THÊM 2026-07-19 (audit vòng 3, D5_orchestrator_dry_run_drift — cao): "R14"
# (an toàn kê đơn HARD-RED, tham-dinh-dau-ra.md §3) THIẾU khỏi cả _HARD_CODES
# lẫn _CHECK_ID_TO_RCODE — cầu này reroute R14 như lỗi SỬA-ĐƯỢC (3 lần) trước
# khi mới leo thang, thay vì leo thang NGAY như các cổng cứng khác (R2/R3/
# R11-R13/Q2/Q5).
_HARD_CODES = {"R2", "R3", "R11", "R12", "R13", "R14", "Q2", "Q5"}
# check-id (run_eval.evaluate) → mã R chuẩn (bản sao ỔN ĐỊNH để không phụ thuộc nội bộ run_eval).
_CHECK_ID_TO_RCODE = {
    "pmid_or_doi": "R1", "no_pii": "R2", "gate_respected": "R3", "no_fabrication": "R4",
    "certainty_vs_strength": "R5", "disclaimer": "R7", "source_has_year": "R9",
    "who_aware_if_antibiotic": "R10", "no_causal_from_observational": "R11", "red_flags": "R12",
    "effect_size_ci_required": "R8", "label_gaming_r1b": "R1b", "mandatory_safety_question": "R13",
    "prescribing_safety_r14": "R14",
    "reporting_standard": "STD-REPORT", "stat_mismatch": "STAT-MISMATCH",
    "ai_disclosure": "AI-DISCLOSE",
}
_REROUTABLE = (
    "R1", "R1b", "R4", "R8", "R9", "STD-REPORT", "STAT-MISMATCH", "AI-DISCLOSE",
)  # mã sửa-được → ưu tiên chọn re-route
_RETURN_FOR_FIX_CHECKS = {
    "effect_size_ci_required", "label_gaming_r1b",
    "reporting_standard", "stat_mismatch", "ai_disclosure",
}


# ── import run_eval.evaluate (chỉ hàm cổng rule-based; giảm phụ thuộc) ────────────
def _load_evaluate():
    eval_dir = ROOT / "tools" / "eval"
    if str(eval_dir) not in sys.path:
        sys.path.insert(0, str(eval_dir))
    import run_eval  # noqa: E402 — nạp trễ để tránh phụ thuộc vòng
    return run_eval.evaluate


# ── D1: APPRAISAL emitter tự chứa (KHỬ PII tên file) ─────────────────────────────
def _safe_target(path_or_name: str) -> tuple:
    """(display, hash). KHỬ PII tên file lâm sàng (hay chứa họ tên/SĐT/mã BN): chuẩn hóa dấu
    phân cách; nếu có run chữ số ≥6 (SĐT/mã), khoảng trắng, hoặc ≥2 token viết-hoa (họ tên)
    → `redacted-<hash>` (giữ đuôi). Không cần scanner ngoài. KHÔNG ghi tên gốc dính PII ra đĩa."""
    from pathlib import PurePath
    name = PurePath(str(path_or_name)).name
    thash = hashlib.sha1(name.encode("utf-8")).hexdigest()[:10]
    probe = re.sub(r"[_\-.]+", " ", name)
    # SỬA 2026-07-22 (vòng lặp kiểm tra-hoàn thiện vòng 10, phát hiện HIGH): trước đây chỉ
    # kiểm \d{6,} trên `probe` ĐÃ tokenize (dấu _-. → khoảng trắng) — nhưng chính bước
    # tokenize lại CẮT ĐỨT số điện thoại/định danh viết CÓ dấu phân cách (vd
    # "0912-345-678" → "0912 345 678") thành các nhóm 3-4 chữ số rời rạc, không còn chuỗi
    # ≥6 số liên tục nào để bắt — làm lọt PII dạng này vào observability/APPRAISALS.jsonl
    # (log bền, append-only). Kiểm THÊM trên bản đã gộp hết khoảng trắng của `probe` (khôi
    # phục chuỗi số liên tục) trước khi đếm độ dài.
    collapsed_digits = re.sub(r"\s+", "", probe)
    caps = re.findall(r"[A-ZÀ-Ỵ][a-zà-ỹ]+", probe)
    if (re.search(r"\d{6,}", probe) or re.search(r"\d{6,}", collapsed_digits)
            or (" " in name) or len(caps) >= 2):
        ext = PurePath(name).suffix
        return f"redacted-{thash[:8]}{ext}", thash
    return name, thash


def _bump_repeats(codes: list, thash: str) -> dict:
    """Đếm tái phạm DEDUP theo output (thash) — chấm lại cùng file KHÔNG cộng dồn. Ghi nguyên
    tử (tmp+os.replace). Trả {code: số_output_distinct}. Best-effort."""
    import os
    data = {}
    if APPRAISAL_REPEATS.exists():
        try:
            data = json.loads(APPRAISAL_REPEATS.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {}
    for c in codes:
        lst = data.get(c) or []
        if not isinstance(lst, list):
            lst = []
        if thash not in lst:
            lst.append(thash)
        data[c] = lst
    try:
        APPRAISAL_REPEATS.parent.mkdir(parents=True, exist_ok=True)
        tmp = APPRAISAL_REPEATS.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        os.replace(tmp, APPRAISAL_REPEATS)
    except OSError:
        pass
    return {c: len(data.get(c, [])) for c in codes}


def _failed_required_check_ids(res: dict) -> list:
    """Các check không nằm trong `red_fails` nhưng vẫn phải chặn phát hành tự động.

    `run_eval.evaluate()` cố ý chỉ dùng `red_fails` cho lỗi an toàn/liêm chính cứng.
    Tuy nhiên một số lỗi chất lượng bắt buộc của nghiên cứu (vd R8: p-value đơn độc,
    stat_mismatch) vẫn phải RETURN-FOR-FIX ở tầng điều phối, nếu không bridge có thể
    phát PASS dù bảng checks đã báo fail.
    """
    ids = []
    for check in res.get("checks", []) or []:
        check_id = check.get("id")
        if check_id in _RETURN_FOR_FIX_CHECKS and check.get("pass") is False:
            ids.append(check_id)
    return ids


def _ledger_codes_from_result(res: dict) -> list:
    seen = set()
    codes = []
    for check_id in list(res.get("red_fails", [])) + _failed_required_check_ids(res):
        code = _CHECK_ID_TO_RCODE.get(check_id, check_id)
        if code not in seen:
            seen.add(code)
            codes.append(code)
    return codes


def emit_appraisal(res: dict, target: str, *, source: str = "orchestrator",
                   at: str | None = None, log_path=None) -> dict:
    """Cắt bản ghi phán quyết bền (§6 `_RUBRIC-EVALUATE-CUNG-QA-GATE.md`). `at` = timestamp ISO
    (người gọi truyền để test tái lặp). Best-effort: lỗi ghi đĩa KHÔNG làm hỏng chấm."""
    verdict = {"ĐẠT": "PASS", "TRẢ-VỀ-SỬA": "RETURN-FOR-FIX"}.get(
        res.get("verdict", ""), res.get("verdict", "?"))
    display, thash = _safe_target(target)
    red = list(res.get("red_fails", []))
    required_fix = _failed_required_check_ids(res)
    codes = _ledger_codes_from_result(res)
    counts = _bump_repeats(codes, thash) if (codes and source not in _EXCLUDE_SOURCES) else {}
    promo = sorted({c for c in codes if counts.get(c, 0) >= PROMOTE_THRESHOLD and c not in _HARD_CODES})
    rec = {
        "id": f"APPRAISAL-{thash[:6]}-{hashlib.sha1((display + verdict + (at or '')).encode()).hexdigest()[:6]}",
        "ts": at or "", "target": display, "target_hash": thash, "source": source,
        "verdict": verdict, "score": res.get("score"),
        "tier0_red_fails": red, "return_for_fix_checks": required_fix,
        "ledger_codes": codes, "promotion_candidate": promo,
    }
    lp = log_path or APPRAISAL_LOG
    try:
        lp.parent.mkdir(parents=True, exist_ok=True)
        with open(lp, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError:
        pass
    return rec


# ── D3: verdict-maker cho Orchestrator.handle(guardrail_verdict=…) ────────────────
def make_run_eval_verdict(output_text: str, *, target: str = "orchestrator-output",
                          source: str = "orchestrator", at: str | None = None, log_path=None):
    """Trả callable `verdict(session) -> dict` chấm `output_text` bằng run_eval.evaluate (THẬT),
    cắt APPRAISAL (D1), map verdict → pass / returned_for_fix để orchestrator re-route (D3)."""
    evaluate = _load_evaluate()

    def verdict(_session) -> dict:
        res = evaluate(output_text, None)
        rec = emit_appraisal(res, target, source=source, at=at, log_path=log_path)
        codes = rec["ledger_codes"]
        if res.get("verdict") == "ĐẠT" and not codes:
            return {"status": "pass", "appraisal": rec["id"]}
        # Mã VỐN cổng cứng (PII/nhân quả/thiếu câu hỏi an toàn…) → LEO THANG NGAY, KHÔNG re-route
        # auto-fix vô nghĩa. Chỉ re-route khi lỗi thuộc loại SỬA ĐƯỢC (trích dẫn/thiếu nguồn).
        hard = [c for c in codes if c in _HARD_CODES]
        if hard:
            return {"status": "returned_for_fix", "code": hard[0],
                    "escalate": True, "appraisal": rec["id"]}
        code = next((c for c in codes if c in _REROUTABLE), codes[0] if codes else "R1")
        return {"status": "returned_for_fix", "code": code, "appraisal": rec["id"]}

    return verdict
