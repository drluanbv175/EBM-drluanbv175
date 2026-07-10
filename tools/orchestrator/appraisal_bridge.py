"""appraisal_bridge.py — NỐI cổng QA (APPRAISAL verdict) → máy trạng thái Lifecycle.

Vá khoảng hở D3: trước đây `Lifecycle.guardrail_fail()` (retry ≤3 → leo thang) là DEAD CODE —
không nơi nào gọi. Cầu này biến phán quyết cổng QA thành chuyển trạng thái vòng đời THẬT:

    PASS            → guardrail_pass()  → released (vẫn dừng Cổng A/B)
    RETURN-FOR-FIX  → guardrail_fail()  → returned_for_fix (retry) hoặc blocked (quá 3 vòng → leo thang)

Dùng bởi nhạc trưởng khi thực thi thật (LLMExecutor) hoặc mô phỏng vòng tự-sửa. Thuần logic điều
phối — KHÔNG gọi LLM, KHÔNG sinh nội dung lâm sàng.
"""
from __future__ import annotations

from .lifecycle import Lifecycle

_PASS = {"PASS", "ĐẠT"}
_FAIL = {"RETURN-FOR-FIX", "TRẢ-VỀ-SỬA", "AUTO-FAIL"}


def apply_verdict(lc: Lifecycle, verdict: str, *, red_codes: list[str] | None = None) -> str:
    """Áp 1 phán quyết cổng QA lên vòng đời. Trả trạng thái mới.

    - verdict PASS  → released.
    - verdict RETURN/AUTO-FAIL → guardrail_fail(): còn lượt → returned_for_fix; hết lượt → blocked.
    """
    lc.to("guardrail", f"cổng QA: {verdict}" + (f" {red_codes}" if red_codes else ""))
    if verdict in _PASS:
        lc.guardrail_pass()
    elif verdict in _FAIL:
        lc.guardrail_fail()   # tự chuyển returned_for_fix / blocked theo số lần retry
    else:
        lc.to("blocked", f"verdict lạ '{verdict}' — leo thang bác sĩ")
    return lc.stage


def run_self_fix_loop(verdicts: list[str]) -> Lifecycle:
    """Mô phỏng vòng tự-sửa: áp lần lượt các phán quyết cho tới PASS hoặc blocked.

    `verdicts` = chuỗi kết quả cổng qua từng vòng (vd ['RETURN-FOR-FIX','RETURN-FOR-FIX','PASS']).
    Dừng ngay khi released/blocked. Đây là đường THẬT khiến guardrail_fail() được thực thi + test.
    """
    lc = Lifecycle()
    lc.to("routed"); lc.to("planned"); lc.to("running")
    for v in verdicts:
        stage = apply_verdict(lc, v)
        if stage in ("released", "blocked"):
            break
    return lc
