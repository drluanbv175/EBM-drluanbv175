# Cỡ mẫu và Kế hoạch phân tích thống kê (SAP)

## 1. Cỡ mẫu

Không đưa ra con số cuối nếu thiếu giả định. Mọi tính toán cần nêu:
- Kết cục chính.
- Thiết kế.
- Tham số đầu vào và nguồn/giả định.
- Alpha, power hoặc độ chính xác mong muốn.
- Tỷ lệ bỏ cuộc/missing/non-response.
- Design effect nếu lấy mẫu cụm.
- Số biến/biến cố nếu xây dựng mô hình.
- Phần mềm/công thức.

Bảng giả định:
| Tham số | Giá trị | Nguồn/lý do | Phân tích độ nhạy cần có? |
|---|---:|---|---|

## 2. Cấu trúc SAP

1. Phiên bản/ngày/SAP final trước khi xem kết quả chính.
2. Mục tiêu và giả thuyết.
3. Quần thể phân tích.
4. Kết cục chính/phụ và định nghĩa.
5. Biến phơi nhiễm/can thiệp/yếu tố nhiễu.
6. Mô tả dữ liệu.
7. Phân tích chính.
8. Phân tích phụ định trước.
9. Xử lý missing.
10. Phân tích độ nhạy.
11. Phân nhóm và tương tác.
12. Multiple testing.
13. Kiểm tra giả định/mô hình.
14. Phần mềm và syntax/script.
15. Shell tables/figures.
16. Quy tắc thay đổi SAP.

## 3. Quy tắc diễn giải

- Báo cáo estimate + CI 95% khi thích hợp.
- p-value không đại diện độ lớn hay ý nghĩa lâm sàng.
- Không chọn biến mô hình chỉ dựa trên p-value đơn biến.
- Phân biệt association, prediction và causal inference.
- Nêu confounding, selection bias, measurement bias.
- Với kết cục phổ biến, diễn giải OR thận trọng.
- Ghi rõ data-driven/post-hoc/exploratory analyses.

## 4. Mô hình và kiểm tra

| Mục tiêu | Kết cục | Phân tích chính | Effect measure | Nhiễu/điều chỉnh | Kiểm tra giả định | Độ nhạy |
|---|---|---|---|---|---|---|

## 5. Shell tables trước phân tích

Tạo các bảng rỗng trước khi phân tích để chống chọn báo cáo theo kết quả:
- Đặc điểm nền.
- Kết cục chính.
- Phân tích chính đã điều chỉnh.
- Biến cố bất lợi nếu có.
- Missing và flow.
- Phân tích độ nhạy.
