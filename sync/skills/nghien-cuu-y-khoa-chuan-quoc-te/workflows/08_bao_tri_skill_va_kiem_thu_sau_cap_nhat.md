# Bảo trì skill và kiểm thử sau cập nhật

## Khi dùng workflow này

Dùng khi người dùng yêu cầu chỉnh sửa skill bằng `skill-creator`, khi có chuẩn/pháp luật mới, hoặc khi kiểm thử cho thấy Claude bỏ sót yêu cầu quan trọng.

## Quy trình chỉnh sửa

1. Đọc `SKILL.md`, `MANIFEST.md`, các file trong `references/`, `workflows/`, `modules/`, `templates/`, `quality/`, `scripts/`.
2. Xác định thay đổi cần thiết: kích hoạt, ngắn gọn, chuẩn mới, an toàn dữ liệu, template hoặc test.
3. Ưu tiên giữ `SKILL.md` là bộ điều phối; đưa chi tiết chuyên sâu sang tài liệu phụ.
4. Kiểm tra mô tả skill nêu rõ **skill làm gì** và **khi nào dùng**, viết ở ngôi thứ ba, không vượt giới hạn kỹ thuật hiện hành.
5. Cập nhật `MANIFEST.md` và lập báo cáo thay đổi.
6. Chạy kiểm tra tĩnh: `python scripts/validate_skill.py` và `python scripts/run_static_evaluations.py`.
7. Sau upload vào Claude, chạy các ca trong `quality/02_ca_kiem_thu_dau_ra.md` trên model dự định sử dụng.
8. Chỉ phát hành bản mới khi không còn lỗi nghiêm trọng; ghi rõ điểm chưa xác nhận hoặc cần test thêm.

## Phân loại lỗi kiểm thử

| Mức | Ví dụ | Xử trí |
|---|---|---|
| Nghiêm trọng | Tạo dữ liệu giả; bỏ qua ethics/dữ liệu; chọn sai thiết kế/chuẩn; tuyên bố sẵn sàng sai | Không sử dụng bản skill; sửa ngay và kiểm thử lại |
| Quan trọng | Thiếu checklist, thiếu trạng thái G0-G9, thiếu yêu cầu xác nhận | Sửa trước sử dụng cho hồ sơ chính thức |
| Biên tập | Trình bày dài, lặp nội dung, bảng chưa rõ | Sửa trong lần phát hành tiếp theo |

## Báo cáo phát hành tối thiểu

- Phiên bản, ngày, người chỉnh sửa.
- Các file đã thay đổi.
- Chuẩn/pháp lý được thêm hoặc cập nhật và nguồn kiểm chứng.
- Kết quả script kiểm tra.
- Kết quả ca kiểm thử Claude thực tế.
- Rủi ro còn tồn tại.
