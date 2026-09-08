---
name: tham-dinh-chung-cu-grade-nnt
description: Sử dụng skill này khi cần THẨM ĐỊNH NHANH một bài báo/guideline/nghiên cứu để quyết định có đáng đổi thực hành không. Kích hoạt với "bài này có đáng tin không", "đọc giúp tôi nghiên cứu này", "NNT/NNH bao nhiêu", "nguy cơ sai lệch (risk of bias)", "GRADE mức nào", "độ nhạy/độ đặc hiệu/LR của test", "guideline này áp dụng được không", "ý nghĩa thống kê hay lâm sàng". Quy trình ~10 phút theo loại thiết kế (RCT·SR/MA·guideline·chẩn đoán·cohort), tính/đọc hiệu số đúng nguồn (ARR·NNT·NNH·LR·HR), tách 3 lớp khuyến cáo–độ chắc chắn–đánh giá vận hành. KHÔNG tự gán GRADE; trích số ĐÚNG nguồn; KHÔNG bịa.
metadata:
  version: 1.0.0
---

# Skill: Thẩm định nhanh chứng cứ (GRADE · NNT · LR)

## 1. Phạm vi
Đọc & thẩm định nhanh một nguồn (RCT, systematic review/meta-analysis, guideline, nghiên cứu chẩn đoán, cohort) để trả lời: **đáng tin tới đâu? áp dụng được cho bệnh nhân VN của tôi không?** Bổ trợ `cap-nhat-chung-cu-y-khoa` (khi cần xoáy vào thẩm định một nguồn cụ thể).

## 2. Nguyên tắc bất biến
- **Trích hiệu số ĐÚNG như nguồn báo cáo** (point estimate + KTC95%/p). Không tự tính sai lệch, không làm tròn gây hiểu nhầm.
- **Không tự gán GRADE.** Giữ nguyên phân hạng của nguồn (Class/Level, GRADE High/Mod/Low). Nếu tự đánh giá để ra quyết định → ghi rõ **"đánh giá vận hành, không phải phân hạng chính thức"**.
- Tách 3 lớp: (a) khuyến cáo/kết quả của nguồn; (b) độ chắc chắn theo nguồn; (c) đánh giá vận hành của ta.
- Nêu CẢ HAI CHIỀU khi chứng cứ mâu thuẫn (vd RCT lớn âm tính sau loạt nhỏ dương tính).

## 3. Chọn khung theo loại câu hỏi
| Loại | Thiết kế tốt nhất | Công cụ thẩm định | Chỉ số chính |
|---|---|---|---|
| Điều trị/can thiệp | RCT, SR/MA | RoB 2, AMSTAR-2, GRADE | RR/OR/HR, ARR, **NNT** |
| Tác hại/nguyên nhân | Cohort/bệnh-chứng | ROBINS-I | RR/OR/HR, **NNH** |
| Chẩn đoán | Cắt ngang độ chính xác | QUADAS-3 v1.2, STARD; QUADAS-2: lịch sử | **Sn/Sp, LR+, LR−** |
| Tiên lượng | Cohort dọc | QUIPS, PROBAST | HR, C-statistic |
| Guideline | — | AGREE II | tính chính thức/cập nhật |

## 4. Quy trình ~10 phút
1. **Câu hỏi & dân số:** PICO của nghiên cứu khớp bệnh nhân của bạn? (sai dân số = cờ giảm tin cậy).
2. **Thiết kế phù hợp câu hỏi?** (điều trị nên là RCT/SR; chẩn đoán nên là nghiên cứu độ chính xác).
3. **Nguy cơ sai lệch (RoB):** RCT → ngẫu nhiên hóa, che giấu phân nhóm, mù, mất theo dõi, phân tích ITT. SR → có hệ thống, đánh giá RoB, dị hợp (I²). Guideline → COI, độc lập, dựa chứng cứ.
4. **Cỡ hiệu lực + độ chính xác:** point estimate + KTC95%; KTC rộng/vắt qua 1 (RR/OR/HR) hoặc qua 0 (chênh lệch) = không chắc.
5. **Quy ra quyết định:** tính/đọc **NNT/NNH**; phân biệt **ý nghĩa thống kê ≠ ý nghĩa lâm sàng** (p nhỏ nhưng hiệu số tí xíu → ít giá trị).
6. **Áp dụng tại VN:** sẵn có thuốc/XN, BHYT, tuyến, bệnh đồng mắc; `[CẦN XÁC NHẬN TẠI ĐƠN VỊ]`.

## 5. Công thức cốt lõi (chỉ dùng số CÓ trong nguồn)
- **ARR** = nguy cơ nhóm chứng − nguy cơ nhóm can thiệp (CER − EER).
- **NNT** = 1 / ARR (làm tròn LÊN). **NNH** = 1 / ARI (tăng nguy cơ tuyệt đối).
- **RRR** = ARR / CER.
- **LR+** = Sn / (1 − Sp); **LR−** = (1 − Sn) / Sp. (LR+ >10 hoặc LR− <0,1 = đổi xác suất mạnh).
- Nếu nguồn chỉ cho RR/HR mà không cho nguy cơ nền → KHÔNG tự bịa ARR/NNT; ghi "nguồn không đủ số liệu để tính NNT".

## 6. Đầu ra mặc định
1. **Loại nguồn + câu hỏi PICO.**
2. **Kết quả chính:** hiệu số đúng nguồn (ước lượng điểm + KTC95%/p).
3. **Nguy cơ sai lệch:** điểm mạnh/yếu chính.
4. **Quy ra quyết định:** NNT/NNH hoặc LR; ý nghĩa lâm sàng.
5. **Phân hạng nguồn** (nguyên văn) — không tự gán GRADE.
6. **Kết luận áp dụng:** áp dụng ngay / cân nhắc / chưa đủ — kèm bối cảnh VN.

## 7. Checklist
- Đã chọn đúng khung theo loại câu hỏi? · Trích số đúng nguồn (estimate+CI)? · Đã nêu RoB? · NNT/NNH/LR đúng (không bịa nguy cơ nền)? · Phân biệt thống kê vs lâm sàng? · Giữ nguyên phân hạng nguồn, ghi rõ "đánh giá vận hành" nếu tự đánh giá? · Nêu mâu thuẫn (nếu có)? · Disclaimer + không PII?

## 8. Liên hệ skill
`cap-nhat-chung-cu-y-khoa` (cập nhật + dashboard) · `kham-ngoai-tru-ebm` (áp số vào quyết định tại giường) · `tiep-can-chan-doan-co-do-chuyen-tuyen` (LR cho test chẩn đoán) · `nghien-cuu-ebm-tong-hop` (khi làm tổng quan/đề cương).

---

## Chốt kiểm đầu ra 2 LỚP — Med-PaLM (BẮT BUỘC, ngay trước khi trả lời)
Skill chạy độc lập (không qua nhạc trưởng) → **tự áp** chốt kiểm 2 lớp như agent `tham-dinh-dau-ra`.
- **Lớp 1 — LIÊM CHÍNH (R1–R7):** nguồn PMID/DOI hoặc nhãn thiếu · KHÔNG PII · không tự "áp dụng cho BN" (dừng Cổng A) · không tự gán GRADE/độ mạnh khi nguồn không cấp · tách độ chắc chứng cứ vs độ mạnh khuyến cáo · nhãn `[CẦN…]` đúng chỗ · disclaimer cuối.
- **Lớp 2 — CHẤT LƯỢNG Med-PaLM (Q1–Q7):** Q1 dễ đọc (đúng đối tượng nhận) · **Q2 đúng đắn** (khớp guideline/đồng thuận — nghi sai → CHUYỂN BÁC SĨ) · Q3 đầy đủ-an toàn (không sót cờ đỏ/CCĐ/tương tác/chỉnh liều/theo dõi) · Q4 không thiên kiến nhóm · **Q5 nguy cơ hại** (hại nặng không cảnh báo → CHUYỂN BÁC SĨ) · Q6 cập nhật · Q7 thẩm quyền nguồn (cảnh giác tạp chí săn mồi). Bản chuẩn: `.claude/agents/_CHUAN-CHAT-LUONG-MEDPALM.md`.
- Còn 🔴 ở lớp nào → **sửa trước khi trả**; **Q2/Q5 đỏ → nêu cờ "cần bác sĩ phán định"**. Tự-kiểm cùng phiên (giảm mù chung, KHÔNG khử thiên lệch) — rào cứng cuối vẫn là bác sĩ.

**"Cần bác sĩ kiểm chứng."**
