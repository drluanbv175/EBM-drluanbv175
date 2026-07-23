#!/usr/bin/env python3
"""promote_lessons.py — DÒ ỨNG VIÊN ĐỀ BẠT (recurrence -> cổng cứng), CHỜ BÁC SĨ DUYỆT.

Vá khoảng hở D5 (rubric lâm sàng): thao tác hóa vòng 'bài học tái diễn -> đề bạt thành cổng
cứng'. Đọc 2 nguồn tín hiệu tái phạm THẬT:
  • observability/APPRAISAL_REPEATS.json — bộ đếm mã R từ cổng QA (run_eval emit_appraisal).
  • LEDGER_LESSONS.jsonl — đếm số mục theo ma_loi (+ so_ca_trong_dot, so_lan_tai_pham).
Mã nào đạt ngưỡng -> LIỆT KÊ làm ỨNG VIÊN vào observability/PROMOTION_QUEUE.md, KÈM provenance
(mục nào đóng góp) để BÁC SĨ tự phán định có thật là 'cùng một kiểu lỗi tái diễn' hay không.

RÀO CỨNG: công cụ KHÔNG tự đề bạt / KHÔNG tự sửa cổng. Chỉ gắn cờ + chờ bác sĩ (human-gate của
rubric — chống hệ tự nới chuẩn cho mình). In ra + ghi file; không đụng agent/cổng nào.
"""
from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "LEDGER_LESSONS.jsonl"
REPEATS = ROOT / "observability" / "APPRAISAL_REPEATS.json"
QUEUE = ROOT / "observability" / "PROMOTION_QUEUE.md"
THRESHOLD = 3  # khớp REPEAT_PROMOTE_THRESHOLD trong run_eval.py

# Mã ĐÃ là cổng cứng (TIER-0/1) — đề bạt thêm = tăng lớp CODE tự động, không phải 'chưa có gate'.
# SỬA 2026-07-22 (vòng lặp kiểm tra-hoàn thiện vòng 10, phát hiện MEDIUM): thiếu
# "DRG-INCOMPLETE" (mã ledger của R14 theo retry_loop.RCODE_TO_LESSON_CODE) — prescribing_
# safety_r14 vừa là red_key trong run_eval.py::evaluate() (tier-0/1, chặn phát hành khi
# fail) vừa là ESCALATE_HARD trong retry_loop.ERROR_ROUTING_TABLE, cùng tiêu chí đã dùng
# để đưa DRG-DOSE vào set này — thiếu entry khiến tool có thể đề bạt lại một cổng ĐÃ cứng.
ALREADY_HARD = {"CLIN-SAFETYQ", "CIT-GHOST", "SEC-PII", "SEC-INJECT", "GRD-SELF", "FAB-DATA",
                "FAB-ADMIN", "INFER-CAUSAL", "DRG-DOSE", "DRG-INCOMPLETE", "CLIN-REDFLAG",
                "CLIN-SAFETYNET"}


def _count(v) -> int:
    """Bộ đếm tái phạm có 2 định dạng: int (cũ) hoặc list các appraisal-id (mới, dedup)."""
    if isinstance(v, int):
        return v
    if isinstance(v, list):
        return len(v)
    return 0


def _read_ledger():
    rows = []
    if LEDGER.exists():
        for line in LEDGER.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return rows


def main() -> None:
    rows = _read_ledger()
    repeats = {}
    if REPEATS.exists():
        try:
            repeats = json.loads(REPEATS.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            repeats = {}

    by_code = defaultdict(list)
    for r in rows:
        by_code[r.get("ma_loi", "?")].append(r)

    # Tổng tín hiệu tái phạm = số mục ledger cùng mã + bộ đếm cổng QA (map R->mã đã ở ledger codes).
    lines = ["# HÀNG CHỜ ĐỀ BẠT — ứng viên cổng cứng (CHỜ BÁC SĨ DUYỆT)",
             "",
             "> Sinh bởi `tools/eval/promote_lessons.py`. Công cụ **KHÔNG tự đề bạt** — chỉ gắn cờ.",
             f"> Ngưỡng tái phạm = {THRESHOLD}. Nguồn: `LEDGER_LESSONS.jsonl` + `observability/APPRAISAL_REPEATS.json`.",
             "> Bác sĩ tự phán định các mục đóng góp có THẬT là *cùng một kiểu lỗi tái diễn* không (khác",
             "> bug ngẫu nhiên trùng mã), rồi mới quyết đề bạt thành cổng cứng / luật skill.",
             ""]

    candidates = []
    for code, items in sorted(by_code.items()):
        ledger_n = len(items)
        # tổng số ca (nếu mục ghi so_ca_trong_dot) — tín hiệu prevalence
        cases = sum(int(i.get("so_ca_trong_dot", 1)) for i in items)
        if ledger_n >= THRESHOLD:
            candidates.append((code, ledger_n, cases, items))

    # thêm ứng viên từ APPRAISAL_REPEATS (mã R vượt ngưỡng) — provenance riêng
    repeat_candidates = {k: _count(v) for k, v in repeats.items() if _count(v) >= THRESHOLD}

    lines.append("## 1. Ứng viên theo LEDGER (số mục cùng mã ≥ ngưỡng)")
    if not candidates:
        lines.append("- *(chưa có mã nào đạt ≥3 mục ledger — cần tích lũy thêm kỳ; đừng đọc 'trống' là 'không có lỗi')*")
    for code, n, cases, items in candidates:
        tag = " · **ĐÃ là cổng cứng** (đề bạt = tăng lớp code tự động)" if code in ALREADY_HARD else " · **CHƯA là cổng cứng** → ứng viên đề bạt thật"
        lines.append(f"\n### `{code}` — {n} mục ledger, ~{cases} ca{tag}")
        for it in items:
            src = "lỗi lâm sàng thật" if "run_eval" not in it.get("noi_phat_sinh", "") else "lỗi mã cổng"
            lines.append(f"- `{it['id']}` ({it['ngay_phat_hien'][:10]}, {src}): {it['mo_ta'][:110]}…")
        lines.append(f"- **Đề xuất**: bác sĩ xét đề bạt/siết luật cho `{code}`; xem `ghi_nguoc_vao` các mục trên.")

    lines.append("\n## 2. Ứng viên theo BỘ ĐẾM CỔNG QA (APPRAISAL_REPEATS ≥ ngưỡng)")
    if not repeat_candidates:
        lines.append(f"- *(chưa mã R nào ≥{THRESHOLD} trong bộ đếm cổng — hiện: "
                     + (", ".join(f"{k}={_count(v)}" for k, v in sorted(repeats.items())) or "rỗng") + ")*")
    else:
        for k, v in sorted(repeat_candidates.items()):
            lines.append(f"- `{k}`: {v} lần → ứng viên; tra APPRAISALS.jsonl để xem target nào đóng góp.")

    lines.append("\n**Cần bác sĩ kiểm chứng.**")
    QUEUE.parent.mkdir(parents=True, exist_ok=True)
    QUEUE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Da ghi: {QUEUE}")
    print(f"  Ung vien theo ledger: {[c[0] for c in candidates] or 'khong'}")
    print(f"  Ung vien theo cong QA: {list(repeat_candidates) or 'khong'}")
    print("Cong cu KHONG tu de bat — cho bac si duyet. Can bac si kiem chung.")


if __name__ == "__main__":
    main()
