# RUNBOOK — Chạy gói đánh giá người thật (CAFÉ-S P3.2 + P4.2)

**Bước 1–3 dưới đây ĐÃ XONG (2026-07-05)** — 2 file dùng ngay, KHÔNG cần dựng lại:
- `expert_kappa_50cases.csv` — 50 dòng, cột `case_id`/`summary`/`agent_rec` đã điền sẵn từ `agent_outputs/cases_all_C01-C50.md`; chỉ còn `expert1/2/3/ghi_chu` trống.
- `likert_50cases.csv` — 150 dòng (50 ca × BS1/BS2/BS3); chỉ còn `c1..c5` trống.
- (`expert_kappa_template.csv` / `likert_template.csv` = bản skeleton cũ, giữ lại tham khảo cấu trúc cột, KHÔNG dùng để chấm.)

1. ~~Chọn 50 ca~~ ✅ đã có (`../cases_50_vignettes.md`).
2. ~~Sinh khuyến nghị agent~~ ✅ đã có, trích dẫn xác minh PubMed độc lập (`../agent_outputs/cases_all_C01-C50.md`).
3. **Chấm MÙ (việc DUY NHẤT còn lại):** gửi 2 file `*_50cases.csv` cho **3 chuyên gia độc lập** điền `expert1/2/3` (Phần A) + **3 bác sĩ** điền Likert c1–c5 (Phần B) — KHÔNG đổi cấu trúc cột/thứ tự dòng.
   - Có thể trùng người; chuyên gia KHÔNG biết đâu là đầu ra AI.
4. **Tính điểm:** `python3 ../human_eval_score.py --kappa expert_kappa_50cases.csv --likert likert_50cases.csv`
5. **Cập nhật** P3.2 + P4.2 vào `.claude/agents/_CHUAN-CAFES.md` → cộng tổng (xem có vượt 85 không).
   - Ca nào ≥1 chuyên gia đánh **ai_nguy_hiem** → rà critical safety NGAY (không để TB che lấp).

> Liêm chính: kết quả chỉ có giá trị khi chấm THẬT–MÙ–ĐỘC LẬP. AI KHÔNG tự chấm thay. "Cần bác sĩ kiểm chứng."
