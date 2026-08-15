#!/usr/bin/env python3
"""metrics_rollup.py — PHA 2 (instrument logging) của METRICS_SPEC_2026-07-08.

Vá khoảng hở 'mọi bằng chứng là snapshot 1 ngày': đây là ĐỒNG HỒ ĐO để thời gian sinh ra bằng
chứng cộng dồn (đường lên mức 4). Đọc log THẬT, tính chỉ số TẦNG 1-2 backfill được, ghi 1 snapshot
có ngày vào observability/METRICS_<ngày>.md. Chạy định kỳ -> mỗi lần 1 snapshot -> xu hướng.

TRUNG THỰC: chỉ số nào 'chưa đủ dữ liệu' thì nói rõ (không đọc '0% tái phạm tuần đầu' = 'trí nhớ
hoàn hảo'). Chỉ đọc METADATA quy trình — KHÔNG nội dung bệnh nhân, KHÔNG PII.
"""
from __future__ import annotations
import json
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APPRAISALS = ROOT / "observability" / "APPRAISALS.jsonl"
LEDGER = ROOT / "LEDGER_LESSONS.jsonl"
PROBES = ROOT / "observability" / "probe_outputs"
# Đếm theo TIỀN TỐ mở ngoặc (marker thường có chữ bên trong: "[CẦN KIỂM CHỨNG theo nguồn]").
GAP_MARKERS = ("[CẦN KIỂM CHỨNG", "[CẦN BỔ SUNG", "[CẦN XÁC NHẬN", "[DỰ THẢO")


def _jsonl(p: Path):
    out = []
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return out


def main(stamp: str | None = None) -> None:
    # Vá 2026-07-09 (tự phát hiện khi dùng công cụ đúng như docstring mô tả — "chạy định kỳ"):
    # mặc định TỪNG hardcode "2026-07-08". Chạy CLI trần (không đối số, đúng cách docstring
    # hướng dẫn) sẽ mãi ghi đè CÙNG MỘT file, không bao giờ tiến ngày — ngược hẳn mục đích nêu
    # ở đầu file ("mỗi lần 1 snapshot -> xu hướng"). Nay mặc định = ngày hôm nay; vẫn cho override
    # qua argv[1] (backfill 1 ngày cụ thể) hoặc gọi main(stamp=...) trực tiếp khi cần.
    if stamp is None:
        stamp = date.today().isoformat()
    apps = _jsonl(APPRAISALS)
    ledger = _jsonl(LEDGER)

    # — Catch-rate cổng QA —
    verdicts = Counter(a.get("verdict") for a in apps)
    total = len(apps)
    returns = verdicts.get("RETURN-FOR-FIX", 0)
    catch_rate = (returns / total * 100) if total else None

    # — Tần suất theo kỳ (ngày) — để biết đã có ≥2 kỳ chưa (điều kiện chỉ số tái phạm có nghĩa) —
    app_days = Counter(a.get("ts", "")[:10] for a in apps)
    ledger_days = Counter(l.get("ngay_phat_hien", "")[:10] for l in ledger)
    all_days = sorted(set(app_days) | set(ledger_days))

    # — Ledger: lỗi lâm sàng thật vs lỗi mã cổng; recurrence-reduction —
    clin_codes = {"CLIN-REDFLAG", "CLIN-SAFETYNET", "CLIN-SAFETYQ", "DRG-DOSE", "DRG-INCOMPLETE", "DRG-ABX", "CIT-WASH"}
    clin_entries = [l for l in ledger if "run_eval" not in l.get("noi_phat_sinh", "")]
    gate_entries = [l for l in ledger if "run_eval" in l.get("noi_phat_sinh", "")]
    reduced = [l for l in ledger if l.get("re_test") and l.get("so_lan_tai_pham", 1) == 0]
    star_ok = [l for l in ledger if l.get("quy_tac_rut_ra") and l.get("ghi_nguoc_vao")]

    # — Gap-marker present trong output probe —
    gap = defaultdict(int)
    if PROBES.exists():
        for f in sorted(PROBES.glob("CL-A*.md")):
            txt = f.read_text(encoding="utf-8")
            gap[f.name] = sum(txt.count(m) for m in GAP_MARKERS)

    L = []
    L.append(f"# METRICS snapshot — {stamp}")
    L.append("")
    L.append("> PHA 2 của `METRICS_SPEC_2026-07-08.md`, sinh bởi `tools/eval/metrics_rollup.py`.")
    L.append("> Chạy định kỳ -> mỗi lần 1 snapshot -> ý nghĩa nằm ở XU HƯỚNG, không ở 1 lần đọc.")
    L.append("")
    L.append("## TẦNG 1 — 2 kiểu hỏng lõi")
    app_periods = sorted(app_days)
    ledger_periods = sorted(ledger_days)
    L.append(f"- **Kỳ ở TẦNG CỔNG QA (appraisal):** {len(app_periods)} — {app_periods}  "
             "← đây mới là nguồn cho ⭐ 'tỷ lệ tái phạm'")
    if len(app_periods) < 2:
        L.append("  - ⚠️ **<2 kỳ ở tầng cổng** → 'tỷ lệ tái phạm' CHƯA ĐỦ DỮ LIỆU (mọi appraisal hiện cùng 1 ngày; "
                 "đừng đọc '0% tái phạm' = 'trí nhớ hoàn hảo'). Cần ≥2 kỳ appraisal THẬT ở các ngày khác nhau.")
    else:
        L.append("  - ✅ ≥2 kỳ appraisal → 'tỷ lệ tái phạm' bắt đầu có ý nghĩa (theo dõi tiếp).")
    L.append(f"- **Kỳ ở tầng LEDGER (ghi bài học):** {len(ledger_periods)} — {ledger_periods}  "
             "*(gồm mục backfill 2026-06-15; KHÁC kỳ cổng QA ở trên — không dùng thay)*")
    L.append(f"- **Hoạt động ghi ledger:** {len(ledger)} mục "
             f"({len(clin_entries)} lỗi lâm sàng thật, {len(gate_entries)} lỗi mã cổng); "
             f"{len(star_ok)}/{len(ledger)} đủ 2 trường ★.")
    L.append(f"- **Recurrence-reduction (ghi-ngược HIỆU QUẢ):** {len(reduced)} mục có `re_test` xác nhận "
             f"KHÔNG tái phạm sau ghi-ngược (vd safety-net/AWaRe 2026-06-15 → probe 2026-07-08 PASS).")
    L.append("")
    L.append("## TẦNG 2 — Liêm chính & chất lượng")
    if catch_rate is None:
        L.append("- **Catch-rate cổng QA:** chưa có bản ghi APPRAISAL.")
    else:
        L.append(f"- **Catch-rate cổng QA:** {returns}/{total} = {catch_rate:.0f}% RETURN-FOR-FIX "
                 f"(PASS={verdicts.get('PASS',0)}).")
        L.append("  - ⚠️ **Lưu ý precision:** 2/2 RETURN phiên 2026-07-08 (CL-A5, CL-A8) là **DƯƠNG TÍNH GIẢ** "
                 "(grader độc lập: output ĐÚNG) — cổng rule-based thiếu phân loại document/task-type. "
                 "Đây là hướng an-toàn (over-return) nhưng cần tinh chỉnh → xem `PROMOTION_QUEUE.md` (LSN-20260708-51/52).")
    L.append("- **Hiện diện gap-marker (output probe):** " +
             ", ".join(f"{k.split('_')[0]}={v}" for k, v in sorted(gap.items())) + " marker.")
    L.append("- **Độ cũ guideline / GRADE tự gán:** chưa instrument (theo METRICS_SPEC: bắt đầu đếm từ đây).")
    L.append("")
    L.append("## Đường lên mức 4 (cộng dồn đo được)")
    L.append("- Cần: chạy `run_eval.py --source gate` trên MỌI output lâm sàng thật + chạy lại rollup này")
    L.append("  mỗi kỳ. Sau ≥2–3 kỳ, 'tỷ lệ tái phạm' + '≥1 đề bạt' mới đủ bằng chứng nâng D1/D2 lên 4.")
    L.append("")
    L.append("**Cần bác sĩ kiểm chứng.**")

    out = ROOT / "observability" / f"METRICS_{stamp}.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"Da ghi: {out}")
    print(f"  Appraisals={total} (PASS={verdicts.get('PASS',0)}, RETURN={returns}); ky={len(all_days)}; "
          f"ledger={len(ledger)} (lam sang={len(clin_entries)}, ma cong={len(gate_entries)})")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
