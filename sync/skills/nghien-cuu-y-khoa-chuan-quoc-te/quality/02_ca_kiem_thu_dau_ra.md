# Bộ ca kiểm thử đầu ra sau khi upload skill vào Claude

## Cách dùng

Chạy từng prompt trong Claude với skill được bật. Ghi kết quả bằng mẫu ở cuối tệp. Không dùng dữ liệu bệnh nhân thật trong kiểm thử.

## Ca 1. Khảo sát hài lòng người bệnh ngoại trú

**Prompt thử:** “Tôi muốn làm nghiên cứu cắt ngang đánh giá sự hài lòng của người bệnh ngoại trú tại một khoa khám bệnh. Hãy lập khung đề cương và kế hoạch phân tích.”

**Kỳ vọng bắt buộc:**
- Xác định G0/G1; yêu cầu dữ kiện còn thiếu.
- Đề nghị thiết kế cắt ngang; STROBE, CROSS nếu phù hợp; COSMIN nếu phát triển/thích nghi/đánh giá thang đo.
- Tạo ma trận mục tiêu-biến-công cụ-phân tích-bảng.
- Không tạo số liệu khảo sát giả.

## Ca 2. Nghiên cứu dữ liệu bệnh án/HIS/EMR

**Prompt thử:** “Tôi muốn dùng dữ liệu hồ sơ ngoại trú 2024-2025 để nghiên cứu yếu tố liên quan kiểm soát HbA1c.”

**Kỳ vọng bắt buộc:**
- STROBE + RECORD.
- Đề cập quyền truy cập, khử định danh, luật dữ liệu, extraction/validation rules.
- Không suy luận nhân quả quá mức.

## Ca 3. Thử nghiệm lâm sàng ngẫu nhiên

**Prompt thử:** “Thiết kế RCT so sánh hai chiến lược điều trị tăng huyết áp ngoại trú.”

**Kỳ vọng bắt buộc:**
- SPIRIT 2025, CONSORT 2025; ICH E6(R3) khi phù hợp.
- Đăng ký thử nghiệm trước/tại tuyển người tham gia đầu tiên theo yêu cầu áp dụng.
- Ethics, safety reporting, protocol deviation và SAP.

## Ca 4. Tổng quan hệ thống/meta-analysis

**Prompt thử:** “Tôi muốn tổng quan hệ thống về thuốc điều trị đau thần kinh ở bệnh nhân đái tháo đường.”

**Kỳ vọng bắt buộc:**
- PRISMA-P/PRISMA 2020, đăng ký PROSPERO/OSF khi phù hợp.
- PICO, chiến lược tìm kiếm, risk of bias, GRADE nếu đánh giá độ chắc chắn.
- Không bịa nghiên cứu hoặc kết quả.

## Ca 5. Chẩn đoán

**Prompt thử:** “Thiết kế nghiên cứu độ chính xác của xét nghiệm mới để phát hiện bệnh gan.”

**Kỳ vọng bắt buộc:**
- STARD; reference standard; spectrum/verification bias; cỡ mẫu phù hợp.
- Kết cục độ nhạy/độ đặc hiệu và CI.

## Ca 6. Mô hình dự báo/AI

**Prompt thử:** “Tôi muốn xây dựng mô hình AI dự báo nhập viện ở bệnh nhân ngoại trú.”

**Kỳ vọng bắt buộc:**
- TRIPOD+AI; validation, calibration, discrimination, clinical utility; bias assessment phù hợp.
- Data privacy và AI governance.
- Không kết luận triển khai chỉ từ AUC.

## Ca 7. Định tính hoặc mixed methods

**Prompt thử:** “Tôi muốn tìm hiểu lý do người bệnh không hài lòng và kết hợp với khảo sát định lượng.”

**Kỳ vọng bắt buộc:**
- Mixed-method rationale; COREQ/SRQR cho nhánh định tính; STROBE/CROSS cho nhánh khảo sát khi phù hợp.
- Sampling, reflexivity, integration plan và bảo mật phỏng vấn.

## Ca 8. Cải tiến chất lượng bệnh viện

**Prompt thử:** “Tôi muốn đánh giá và cải tiến thời gian chờ khám tại phòng khám.”

**Kỳ vọng bắt buộc:**
- Phân biệt QI và nghiên cứu; SQUIRE khi báo cáo QI.
- Nêu yêu cầu xác nhận đạo đức/quy định đơn vị.
- Chỉ số đầu ra, quy trình đo và kế hoạch triển khai.

## Mẫu ghi kết quả kiểm thử

| Ca | Model/phiên bản Claude | Ngày thử | Kích hoạt đúng? | Chuẩn đúng? | Có lỗi nghiêm trọng? | Cần sửa skill? |
|---|---|---|---|---|---|---|
| 1 | | | | | | |
| 2 | | | | | | |
