---
name: giao-tiep-quyet-dinh-soap
description: Sử dụng skill này khi cần kỹ năng GIAO TIẾP với bệnh nhân, RA QUYẾT ĐỊNH CÙNG BỆNH NHÂN (shared decision-making), báo tin xấu, hoặc GHI HỒ SƠ SOAP. Kích hoạt với "giải thích cho bệnh nhân thế nào", "bệnh nhân không chịu điều trị/lưỡng lự", "trình bày lựa chọn điều trị", "nói chuyện khó/báo tin xấu", "ghi bệnh án SOAP", "tư vấn để bệnh nhân hiểu và đồng thuận". Dùng khung giao tiếp (ask-tell-ask, teach-back), trình bày lợi–hại bằng số tự nhiên, SPIKES cho tin xấu, cấu trúc SOAP. Cốt lõi để tăng TUÂN THỦ. KHÔNG lưu thông tin định danh bệnh nhân (PII) trong hồ sơ mẫu.
metadata:
  version: 1.0.0
---

# Skill: Giao tiếp · Quyết định cùng bệnh nhân · Ghi SOAP

## 1. Phạm vi
Hỗ trợ phần "con người" của buổi khám: giải thích dễ hiểu, cùng quyết định, xử lý lưỡng lự/khó, báo tin xấu, và ghi chép chuẩn. Đây là đòn bẩy lớn nhất cho **tuân thủ** — nối chặt với `tuan-thu-dieu-tri`.

## 2. Nguyên tắc
- Ngôn ngữ phổ thông, tránh thuật ngữ; kiểm tra hiểu bằng **teach-back** (bảo bệnh nhân nhắc lại bằng lời của họ).
- Trình bày nguy cơ bằng **số tự nhiên & cùng mẫu số** ("trong 100 người như bác, khoảng X…"), tránh chỉ nói %RRR gây phóng đại.
- Tôn trọng giá trị/ưu tiên của bệnh nhân; quyết định là CÙNG nhau, không áp đặt.
- Hồ sơ: KHÔNG ghi thông tin định danh khi tạo mẫu/chia sẻ.

## 3. Bộ khung dùng theo tình huống

### A. Giải thích & tư vấn — "Ask–Tell–Ask"
1. **Hỏi** bệnh nhân đã hiểu/lo gì.
2. **Nói** thông tin chính, ngắn, từng khối nhỏ (chunking).
3. **Hỏi lại (teach-back):** "Để chắc em giải thích rõ, bác nhắc lại giúp em sẽ uống thế nào?"

### B. Quyết định cùng bệnh nhân (Shared Decision-Making) — khung SHARE
- **S**: nêu có nhiều lựa chọn (kể cả không điều trị/theo dõi).
- **H**: trình bày lợi ích & tác hại từng lựa chọn bằng số tự nhiên (nối `tham-dinh-chung-cu-grade-nnt` lấy NNT/NNH).
- **A**: hỏi giá trị/ưu tiên & hoàn cảnh (chi phí, sinh hoạt).
- **R**: cùng chọn.
- **E**: đánh giá lại ở lần sau.

### C. Phỏng vấn tạo động lực (khi lưỡng lự/đề kháng) — OARS
Câu hỏi mở · Khẳng định điểm tích cực · Phản ánh (lắng nghe) · Tóm tắt. Khơi "ngôn ngữ thay đổi", tránh tranh cãi. (Sâu hơn: `tuan-thu-dieu-tri`.)

### D. Báo tin xấu — SPIKES
**S**etting (riêng tư) · **P**erception (hỏi họ biết gì) · **I**nvitation (hỏi muốn biết tới đâu) · **K**nowledge (báo, từ tốn, cảnh báo trước) · **E**motions (đón nhận cảm xúc, đồng cảm) · **S**trategy (kế hoạch tiếp theo + hẹn).

## 4. Ghi hồ sơ SOAP (chuẩn, không PII trong mẫu chia sẻ)
- **S (Subjective):** lý do khám, bệnh sử, triệu chứng theo lời bệnh nhân, tiền sử/thuốc/dị ứng liên quan.
- **O (Objective):** sinh hiệu, khám thực thể, cận lâm sàng có sẵn.
- **A (Assessment):** chẩn đoán/chẩn đoán phân biệt + mức độ/nguy cơ; lý giải ngắn.
- **P (Plan):** xét nghiệm/điều trị/liều (có nguồn) · giáo dục & teach-back đã làm · **safety-netting** (dấu hiệu quay lại ngay) · hẹn tái khám · điều cần theo dõi.
> Mẫu dùng `[BN]`, `[tuổi]`, `[mã ẩn danh]` — KHÔNG tên/định danh thật.

## 5. Đầu ra mặc định
Tùy yêu cầu: (a) **kịch bản lời thoại** mẫu (ask-tell-ask/SPIKES); (b) **bảng lựa chọn** lợi–hại bằng số tự nhiên cho SDM; (c) **mẫu SOAP** điền sẵn khung; (d) **câu teach-back** + nội dung dặn (nối tờ A5).

## 6. Checklist
- Ngôn ngữ phổ thông, có teach-back? · Nguy cơ trình bày bằng số tự nhiên (không chỉ %RRR)? · Đã hỏi giá trị/ưu tiên bệnh nhân? · SOAP đủ S-O-A-P + safety-netting? · Không PII? · Có disclaimer khi là nội dung cho bệnh nhân?

## 6b. Chốt kiểm đầu ra 2 LỚP (trước khi trả lời)
Tự áp như agent `tham-dinh-dau-ra` (skill chạy độc lập): **Lớp 1 LIÊM CHÍNH** R1–R7 (nguồn PMID/DOI hoặc nhãn thiếu · KHÔNG PII · không tự "áp dụng cho BN"/dừng Cổng A · không tự gán GRADE/độ mạnh · tách độ chắc chứng cứ vs độ mạnh khuyến cáo · nhãn `[CẦN…]` · disclaimer) + **Lớp 2 CHẤT LƯỢNG Med-PaLM** Q1–Q7 (dễ đọc · đúng đắn · đầy đủ-an toàn · thiên kiến · nguy cơ hại · cập nhật · thẩm quyền nguồn; `.claude/agents/_CHUAN-CHAT-LUONG-MEDPALM.md`). Còn 🔴 → sửa trước khi trả; **Q2/Q5 đỏ → cờ chuyển bác sĩ**. Tự-kiểm cùng phiên — rào cứng cuối vẫn là bác sĩ.

## 7. Liên hệ skill
`tuan-thu-dieu-tri` (kế hoạch tuân thủ + tờ A5) · `kham-ngoai-tru-ebm` (ghi SOAP cuối buổi khám) · `tham-dinh-chung-cu-grade-nnt` (số liệu cho SDM) · `tiep-can-chan-doan-co-do-chuyen-tuyen` (safety-netting/chuyển tuyến).
