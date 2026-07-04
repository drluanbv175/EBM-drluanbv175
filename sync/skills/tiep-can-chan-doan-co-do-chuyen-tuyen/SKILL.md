---
name: tiep-can-chan-doan-co-do-chuyen-tuyen
description: Sử dụng skill này khi bác sĩ tiếp cận MỘT triệu chứng/hội chứng ngoại trú và cần đi từ triệu chứng → chẩn đoán phân biệt → CỜ ĐỎ bắt buộc loại trừ → ngưỡng chuyển tuyến/cấp cứu một cách AN TOÀN. Kích hoạt với "bệnh nhân đau ngực/đau đầu/đau bụng/khó thở/chóng mặt/đau lưng/sốt/sụt cân… tiếp cận thế nào", "có nguy hiểm không", "khi nào cần chuyển viện/cấp cứu", "đừng bỏ sót bệnh gì". Trọng tâm: an toàn — không để tra cứu làm trì hoãn cấp cứu. Đây là skill HỖ TRỢ tư duy, không thay khám trực tiếp; KHÔNG lưu PII.
metadata:
  version: 1.0.0
---

# Skill: Tiếp cận chẩn đoán an toàn — cờ đỏ & ngưỡng chuyển tuyến

## 1. Phạm vi
Dùng khi cần tiếp cận một triệu chứng/hội chứng ở phòng khám ngoại trú: dựng chẩn đoán phân biệt, **loại trừ bệnh nguy hiểm (can't-miss)**, và quyết định xử trí tại chỗ / theo dõi / chuyển tuyến / cấp cứu. Bổ trợ cho `kham-ngoai-tru-ebm` (skill kia lo trọn 5 bước EBM; skill này chuyên sâu phần an toàn–cờ đỏ–chuyển tuyến).

## 2. Nguyên tắc bất biến
- **Cấp cứu ưu tiên trước mọi tra cứu.** Nghi cấp cứu → kích hoạt cấp cứu/chuyển ngay, không chờ tính điểm/đọc tài liệu.
- Không bịa tỷ lệ, ngưỡng, độ nhạy/đặc hiệu; số liệu chỉ nêu khi nguồn xác minh (nối `tham-dinh-chung-cu-grade-nnt`).
- Cá thể hóa theo người cao tuổi/CKD/gan/đa thuốc/suy giảm miễn dịch (triệu chứng có thể mờ nhạt, ngưỡng cảnh giác cao hơn).

## 3. Quy trình 6 bước
1. **Đóng khung:** triệu chứng chính · cấp/bán cấp/mạn · tuổi & yếu tố nguy cơ · bối cảnh (sốt, sụt cân, chấn thương, thuốc).
2. **Chẩn đoán phân biệt 2 trục:** (a) **Thường gặp**; (b) **Không được bỏ sót** (nguy hiểm dù hiếm). Liệt kê cả hai.
3. **CỜ ĐỎ — chủ động hỏi/khám để loại trừ** (bảng mục 4). Có cờ đỏ → nâng mức xử trí.
4. **Cận lâm sàng theo giá trị (LR), không rải:** chọn test thay đổi xác suất đủ để đổi quyết định; nêu test nào trước.
5. **Quyết định xử trí:** xử trí tại chỗ · theo dõi có hẹn (safety-netting cụ thể: dấu hiệu nào → quay lại ngay) · chuyển tuyến (khám chuyên khoa) · **cấp cứu** (mục 4 cột cuối).
6. **Ghi chép + dặn dò:** nối `giao-tiep-quyet-dinh-soap` (ghi SOAP) + `tuan-thu-dieu-tri` (lời dặn A5).

## 4. Bảng CỜ ĐỎ nhanh theo triệu chứng ngoại trú thường gặp
> Đây là gợi ý NHẮC, không đầy đủ; luôn đối chiếu lâm sàng. Khi nghi → chuyển cấp cứu/chuyên khoa.

| Triệu chứng | Cờ đỏ "không được bỏ sót" | Hướng |
|---|---|---|
| Đau ngực | Đau kiểu mạch vành, lan tay/hàm, khó thở, vã mồ hôi, tụt HA; đau xé lan lưng (bóc tách); khó thở + đau ngực màng phổi (thuyên tắc phổi) | Cấp cứu/ECG-troponin ngay |
| Đau đầu | Đột ngột "sét đánh"; sốt + cứng gáy; thần kinh khu trú; phù gai; mới khởi phát >50 tuổi; nặng dần | Cấp cứu/chuyển ngay |
| Đau bụng | Bụng cứng/đề kháng; đau dữ dội đột ngột; nôn ra máu/đi cầu phân đen; bụng + tụt HA (phình ĐMC vỡ); đau khu trú hố chậu phải | Cấp cứu/ngoại |
| Khó thở | SpO₂ thấp, tím, nói ngắt quãng; khó thở cấp; đau ngực kèm theo | Cấp cứu |
| Đau lưng | Rối loạn cơ vòng/bí tiểu, tê yên ngựa (đuôi ngựa); sốt + đau (nhiễm trùng); sụt cân/ung thư; chấn thương; thần kinh tiến triển | Chuyển ngay/chuyên khoa |
| Chóng mặt | Khởi phát đột ngột + thần kinh khu trú/nói khó/nhìn đôi (đột quỵ tiểu não); HINTS bất thường | Cấp cứu đột quỵ |
| Sốt | Lơ mơ, tụt HA, thở nhanh (nhiễm khuẩn huyết); cứng gáy; giảm bạch cầu/suy giảm miễn dịch | Cấp cứu/nhập viện |
| Sụt cân không chủ ý | Kèm thiếu máu, nuốt nghẹn, hạch, máu trong phân; >5% trong 6–12 tháng | Tầm soát ung thư/chuyển |

## 5. Khung xác suất (gợi ý, không bịa số)
- Ước lượng tiền nghiệm theo dịch tễ/biểu hiện; dùng test để dịch chuyển qua ngưỡng test–treat.
- Khi nêu Sn/Sp/LR cụ thể: phải có nguồn (nối `tham-dinh-chung-cu-grade-nnt`); chưa có → ghi định tính + `[CẦN BỔ SUNG NGUỒN]`.

## 6. Đầu ra mặc định
1. **Tóm tắt an toàn:** có/không dấu hiệu cấp cứu ngay.
2. **Chẩn đoán phân biệt:** thường gặp · không-được-bỏ-sót.
3. **Cờ đỏ cần loại trừ** (đã hỏi/khám gì).
4. **Cận lâm sàng đề xuất** (ưu tiên, lý do).
5. **Quyết định + safety-netting** (dấu hiệu quay lại ngay) + **ngưỡng chuyển tuyến/cấp cứu**.
6. Nhóm đặc biệt (cao tuổi/CKD/gan/suy giảm miễn dịch).

## 7. Checklist
- Đã loại cấp cứu trước chưa? · Đã nêu cả nhóm "không được bỏ sót"? · Cờ đỏ rõ ràng? · Có safety-netting cụ thể? · Số liệu (nếu có) đã dẫn nguồn? · Có disclaimer "Cần bác sĩ kiểm chứng"? · Không PII?

## 7b. Chốt kiểm đầu ra 2 LỚP (trước khi trả lời)
Tự áp như agent `tham-dinh-dau-ra` (skill chạy độc lập): **Lớp 1 LIÊM CHÍNH** R1–R7 (nguồn · KHÔNG PII · không vượt Cổng A · không tự gán mức · tách 2 trục · nhãn `[CẦN…]` · disclaimer) + **Lớp 2 CHẤT LƯỢNG Med-PaLM** Q1–Q7 (đặc biệt **Q3 đầy đủ** [không sót cờ đỏ/must-not-miss] · **Q5 nguy cơ hại** · Q2 đúng đắn; `.claude/agents/_CHUAN-CHAT-LUONG-MEDPALM.md`). Còn 🔴 → sửa trước khi trả; **Q2/Q5 đỏ → cờ chuyển bác sĩ**. Tự-kiểm cùng phiên — rào cứng cuối vẫn là bác sĩ.

## 8. Liên hệ skill
`kham-ngoai-tru-ebm` (5 bước EBM) · `tham-dinh-chung-cu-grade-nnt` (số liệu test/điều trị) · `ke-don-an-toan-benh-man` (sau khi chẩn đoán) · `giao-tiep-quyet-dinh-soap` + `tuan-thu-dieu-tri` (dặn dò).
