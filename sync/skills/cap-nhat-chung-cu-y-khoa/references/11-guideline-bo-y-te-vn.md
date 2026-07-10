# 11 — Bản địa hóa theo guideline Bộ Y tế VN

Tăng độ sát thực hành VN: ở bước "Áp dụng tại Việt Nam" (Bước 6), đối chiếu khuyến cáo quốc tế với **hướng dẫn Bộ Y tế** bác sĩ đang theo, thay vì chỉ ghi `[CẦN XÁC NHẬN]`.

## Nguồn dữ liệu (do bác sĩ cung cấp — KHÔNG bịa)
- Sổ đăng ký: `EBM-Dashboards/vn-guidelines/registry.json` (tên · số QĐ · năm · phạm vi · file).
- PDF chính thức trong `EBM-Dashboards/vn-guidelines/`.
- (Khuyến nghị) Nạp PDF vào kho RAG của skill `clinical-evidence-rag` để truy xuất khuyến cáo cụ thể CÓ TRÍCH DẪN, có ngày, kiểm toán được.

## Quy trình khi cập nhật một vấn đề
1. Tra `registry.json` xem có hướng dẫn BYT phủ chủ đề không.
2. **Có:** trích nguồn BYT (tên + số QĐ + năm) và **đối chiếu quốc tế ↔ BYT**:
   - khác biệt phác đồ / ngưỡng / lựa chọn thuốc;
   - thuốc/xét nghiệm trong **danh mục BHYT** & khả năng tiếp cận;
   - **phân tuyến** (việc làm được ở tuyến cơ sở vs chuyển tuyến).
   Dùng `clinical-evidence-rag` để lấy câu khuyến cáo cụ thể từ PDF (có trích dẫn).
3. **Chưa có:** giữ `[CẦN XÁC NHẬN TẠI ĐƠN VỊ]` + gợi ý bác sĩ bổ sung tài liệu vào registry.

## Liêm chính (bắt buộc)
- **Không bịa** số quyết định, năm, hay nội dung hướng dẫn BYT. Chỉ dùng tài liệu đã có trong registry/RAG.
- Khi **quốc tế khác BYT**, nêu CẢ HAI chiều + lý do; tách rõ "khuyến cáo BYT" vs "chứng cứ quốc tế" vs "đánh giá vận hành".
- Ưu tiên an toàn người bệnh, chi phí/BHYT và năng lực tuyến khám.
- Đầu ra vẫn kèm PMID/DOI (chứng cứ quốc tế) + nguồn BYT (số QĐ); disclaimer; không PII.
