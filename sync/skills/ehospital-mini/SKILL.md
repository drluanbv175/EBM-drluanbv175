---
name: ehospital-mini
description: Soạn LỜI DẶN & NHẮC TÁI KHÁM ngoại trú cho bệnh nhân — mẫu in (A5/A4), mốc tái khám, cách dùng thuốc gọn, tiêu chí QUAY LẠI NGAY/đi cấp cứu (safety-netting), kế hoạch tuân thủ. Dùng khi cần phát tay tờ dặn dò sau khám. KHÔNG bịa tích hợp phần mềm bệnh viện/HIS; nếu cần nối hệ thống thật (eHospital/HIS/SMS) → đánh dấu [CẦN XÁC NHẬN TẠI ĐƠN VỊ]. KHÔNG PII trong mẫu.
---

# Skill: Lời dặn & nhắc tái khám ngoại trú (ehospital-mini)

Công cụ soạn NỘI DUNG tờ dặn dò/nhắc tái khám để in phát tay. Dùng cho `loi-dan-tuan-thu`.

## ⚠️ Ranh giới tích hợp (KHÔNG bịa)
- Đây là công cụ **soạn nội dung + mẫu in**, KHÔNG phải phần mềm tự gửi nhắc/đặt lịch.
- Mọi nối với **hệ thống bệnh viện thật** (eHospital/HIS, tổng đài SMS/Zalo, lịch hẹn điện tử) → **[CẦN XÁC NHẬN TẠI ĐƠN VỊ]**; KHÔNG khẳng định đã tích hợp nếu chưa có bằng chứng.

## Nguyên tắc liêm chính (4 trụ cột)
- **KHÔNG PII** trong mẫu (để chỗ trống _Họ tên/Mã KB_ cho bác sĩ điền tay tại chỗ, không lưu vào AI).
- Liều/thuốc/ngưỡng chỉ ghi khi bác sĩ đã quyết & có nguồn; chỗ chưa chắc → `[CẦN BÁC SĨ ĐIỀN]`.
- Ngôn ngữ dễ hiểu cho bệnh nhân; an toàn là ưu tiên (safety-netting rõ ràng).

## Quy trình
**BƯỚC 0 — Tiền đề:** xác nhận chẩn đoán/điều trị đã được bác sĩ quyết (skill này chỉ trình bày lại cho bệnh nhân, không tự ra y lệnh).
1. **Chẩn đoán/tình trạng (ngôn ngữ bệnh nhân):** giải thích ngắn gọn.
2. **Thuốc & cách dùng:** tên – liều – thời điểm – lưu ý (đói/no, tác dụng phụ hay gặp); dùng teach-back để bệnh nhân nhắc lại.
3. **Theo dõi tại nhà:** dấu hiệu cần theo dõi + cách tự đo (vd HA, đường huyết) nếu phù hợp.
4. **🚩 QUAY LẠI NGAY / ĐI CẤP CỨU khi:** liệt kê tiêu chí cờ đỏ cụ thể của tình trạng đó.
5. **Tái khám:** mốc thời gian + mang theo gì + tiêu chí thất bại điều trị.
6. **Kế hoạch tuân thủ:** đơn giản hóa phác đồ, nhắc lịch (giấy/người nhà), gỡ rào cản.

## Mẫu in (A5 — điền tại chỗ, KHÔNG lưu PII vào AI)
```
TỜ DẶN DÒ SAU KHÁM — [Phòng khám/khoa]            Ngày: __/__/____
Họ tên: __________  Mã KB: ______   (bác sĩ điền tay)
1) Tình trạng: ____
2) Thuốc: | Tên | Liều | Khi nào | Lưu ý |
3) Theo dõi tại nhà: ____
4) 🚩 QUAY LẠI NGAY/CẤP CỨU khi: ____
5) Tái khám: ngày ____ — mang theo: ____ ; thất bại điều trị nếu: ____
6) Lưu ý tuân thủ: ____
Bác sĩ: __________
```
Kết: **"Cần bác sĩ kiểm chứng."**

## Ranh giới
KHÔNG ra chẩn đoán/y lệnh (chỉ trình bày lại quyết định của bác sĩ); KHÔNG tự gửi nhắc qua hệ thống thật ([CẦN XÁC NHẬN TẠI ĐƠN VỊ]); KHÔNG lưu PII.
