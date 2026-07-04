# RUNBOOK — Chạy gói đánh giá người thật (CAFÉ-S P3.2 + P4.2)

1. **Chọn 50 ca** phức tạp (đa bệnh/đa thuốc/chẩn đoán khó), **ẩn danh** (mã C01..C50, KHÔNG PII).
   - Nguồn: thực hành thật đã khử định danh, HOẶC nhờ tôi sinh 50 vignette chuẩn.
2. **Sinh khuyến nghị agent:** cho `dieu-phoi-lam-sang` chạy từng ca → điền cột `agent_rec`.
3. **Chấm MÙ:** 3 chuyên gia độc lập điền `expert1/2/3` (Phần A) + 3 bác sĩ điền Likert c1–c5 (Phần B).
   - Có thể trùng người; chuyên gia KHÔNG biết đâu là đầu ra AI.
4. **Tính điểm:** `python3 ../human_eval_score.py --kappa expert_kappa.csv --likert likert.csv`
5. **Cập nhật** P3.2 + P4.2 vào `.claude/agents/_CHUAN-CAFES.md` → cộng tổng (xem có vượt 85 không).
   - Ca nào ≥1 chuyên gia đánh **ai_nguy_hiem** → rà critical safety NGAY (không để TB che lấp).

> Liêm chính: kết quả chỉ có giá trị khi chấm THẬT–MÙ–ĐỘC LẬP. AI KHÔNG tự chấm thay. "Cần bác sĩ kiểm chứng."
