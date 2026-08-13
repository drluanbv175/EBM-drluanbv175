# 12. Cổng direct-practice readiness

## Mục tiêu

Bảo đảm hệ thống chỉ đưa vào hàng "sẵn sàng cho bác sĩ áp dụng trực tiếp" những thẻ chứng cứ đã đủ 4 lớp:

1. **Đúng nguồn**: có PMID/DOI hoặc URL chính thức tin cậy; tiêu đề, tổ chức, ngày/phiên bản và quần thể khớp câu hỏi.
2. **Mới/còn hiện hành**: có ngày rà soát gần đây; không gọi là "mới" nếu chỉ là khuyến cáo nền vẫn còn hiệu lực.
3. **Độ tin cậy cao**: ưu tiên guideline chính thức, systematic review/meta-analysis chất lượng cao, RCT lớn, safety communication chính thức; `gradeLevel` direct-use chỉ chấp nhận `high` hoặc `mod`.
4. **Bác sĩ duyệt và áp dụng được tại đơn vị**: không còn nhãn `[CẦN XÁC NHẬN...]`, không PII, không thiếu an toàn thuốc/nhóm đặc biệt, và có bằng chứng doctor/master gate.

## Luật phân loại

- `READY_FOR_PHYSICIAN_DIRECT_USE`: chỉ dùng cho thẻ `decision="apply"` đã xác minh, GRADE `high/mod`, truy nguyên được, còn mới theo ngày rà soát, có doctor/master gate, không còn nhãn cần bổ sung.
- `REVIEW_REQUIRED`: chứng cứ mới từ engine, dù có DOI/PMID và high-grade, vẫn chỉ ở hàng duyệt nếu chưa có doctor/master gate.
- `BLOCKED_FOR_DIRECT_USE`: mọi thẻ `apply` thiếu một điều kiện ở trên phải bị chặn, không được trình bày như hướng dẫn áp dụng trực tiếp.

## Lệnh kiểm trong repo sống

Chạy trong `medical-ebm-automation/`:

```bash
python tools/verify_direct_clinical_practice_readiness.py --today YYYY-MM-DD --write
```

Báo cáo sinh ra:

- `reports/DIRECT_CLINICAL_PRACTICE_READINESS.json`
- `reports/DIRECT_CLINICAL_PRACTICE_READINESS.md`

Khi cần fail-closed nếu còn thẻ `apply` không đủ điều kiện direct-use:

```bash
python tools/verify_direct_clinical_practice_readiness.py --today YYYY-MM-DD --strict-apply
```

## Cách dùng trong skill

Trước khi nói chứng cứ có thể "áp dụng trực tiếp", phải:

- gọi rõ đây là **sẵn sàng cho bác sĩ áp dụng**, không phải hệ thống tự điều trị;
- nếu cổng direct-use chưa chạy, ghi trạng thái là `REVIEW_REQUIRED`;
- nếu cổng báo `BLOCKED_FOR_DIRECT_USE`, nêu lý do chặn và không hạ thấp tiêu chuẩn để chiều theo yêu cầu;
- luôn giữ disclaimer: `Cần bác sĩ kiểm chứng.`

Không tự sửa `EBM_MASTER.json` để chuyển `consider/notyet` thành `apply`. Việc nâng hạng cần bác sĩ duyệt và ghi dấu trong sổ cái.
