# Mẫu cấu trúc bài giảng, slide và các định dạng đầu ra

Đọc file này khi cần dàn ý chi tiết cho một bài giảng/slide hoàn chỉnh, hoặc khi
chọn định dạng trình bày cho một sản phẩm đào tạo. Mục lục:

1. Cấu trúc bài giảng đầy đủ (8 mục)
2. Mẫu ca lâm sàng lồng ghép
3. Thư viện định dạng đầu ra ngắn (chọn theo nhu cầu)
4. Quy ước dàn ý slide (storyboard)

---

## 1. Cấu trúc bài giảng đầy đủ

Dùng khi người dùng yêu cầu "bài giảng", "bài đào tạo", "chuyên đề". Không bắt buộc
đủ 8 mục cho mọi sản phẩm — chọn mục phù hợp với phạm vi yêu cầu.

```
# Bài giảng: [chủ đề]

## 1. Mục tiêu học tập
Viết theo động từ đo lường được (nhận diện, phân tầng, chỉ định, xử trí), tránh
"hiểu/biết" chung chung. Sau bài này người học có thể:
- Chẩn đoán / tiếp cận [vấn đề].
- Phân tầng nguy cơ.
- Lựa chọn điều trị ban đầu hợp lý.
- Nhận diện cờ đỏ.
- Quyết định thời điểm nhập viện/chuyển tuyến.

## 2. Đối tượng học viên
Nêu rõ tuyến/đối tượng (bác sĩ đa khoa tuyến cơ sở, học viên, điều dưỡng...) vì
điều này quyết định độ sâu và phạm vi áp dụng của khuyến cáo.

## 3. Dàn ý slide (storyboard)
| Slide | Tiêu đề | Thông điệp chính | Nội dung cốt lõi | Hình/bảng/thuật toán |
|---|---|---|---|---|

## 4. Nội dung từng slide
Mỗi slide: tiêu đề · 1 thông điệp chính · 3–5 ý · bảng/sơ đồ nếu cần · ghi chú
thuyết trình nếu cần.

## 5. Ca lâm sàng (nếu phù hợp)
Xem mục 2 bên dưới.

## 6. Thuật toán
Cho tiếp cận chẩn đoán, phân tầng, điều trị, theo dõi, chuyển tuyến.
Trình bày bằng Mermaid hoặc bảng quyết định — xem references/phong-cach-thi-giac.md.

## 7. Kết luận
- 3–5 take-home messages.
- Điều cần THAY ĐỔI trong thực hành.
- Điều KHÔNG nên làm (low-value / có hại).
- Cảnh báo an toàn.

## 8. Tài liệu tham khảo
Trình bày Vancouver/NLM khi yêu cầu — xem references/chung-cu-trich-dan.md.
```

---

## 2. Mẫu ca lâm sàng lồng ghép

Ca lâm sàng làm tăng khả năng ghi nhớ và chuyển giao vào thực hành. Cấu trúc gợi ý:

- **Tình huống**: bệnh cảnh ngắn, đủ dữ kiện để ra quyết định (tuổi, bệnh nền,
  triệu chứng chính, dấu hiệu sinh tồn nếu liên quan).
- **Câu hỏi thảo luận**: 1–2 câu hỏi quyết định (chẩn đoán phân biệt? cờ đỏ? bước
  tiếp theo?).
- **Phân tích**: lập luận lâm sàng, chỉ rõ dữ kiện then chốt và bẫy thường gặp.
- **Bài học thực hành**: 1–2 điểm rút ra, gắn với thông điệp chính của bài.

Không dùng dữ liệu định danh người bệnh thật. Nếu phỏng theo ca thật, ẩn danh hoàn
toàn và ghi rõ "[ca minh họa, đã ẩn danh]".

---

## 3. Thư viện định dạng đầu ra ngắn

Phần lớn yêu cầu thực hành không cần cả bài giảng mà chỉ cần một sản phẩm ngắn,
áp dụng được ngay. Chọn định dạng theo nhu cầu:

| Định dạng | Khi nào dùng |
|---|---|
| Tóm tắt thực hành nhanh | Gói gọn cách tiếp cận một vấn đề trong nửa trang |
| Bảng quyết định lâm sàng | So sánh phương án theo tiêu chí; có ô màu theo vai trò |
| Checklist cờ đỏ | Liệt kê dấu hiệu cần hành động ngay/chuyển tuyến |
| Thuật toán tiếp cận | Luồng quyết định phân nhánh (Mermaid hoặc sơ đồ) |
| Bảng thuốc/can thiệp | Chỉ định, liều, chống chỉ định, chỉnh liều thận/gan, lưu ý nhóm đặc biệt |
| Kế hoạch theo dõi | Mốc tái khám, chỉ số theo dõi, tiêu chí thất bại điều trị |
| Dặn dò người bệnh | Ngôn ngữ dễ hiểu, dấu hiệu cần quay lại ngay/đến cấp cứu (safety-netting) |
| Tiêu chí nhập viện/chuyển tuyến | Ngưỡng quyết định rõ ràng |

Bảng thuốc nên luôn có cột: chỉ định · liều thường dùng · chống chỉ định/thận trọng
· tác dụng phụ quan trọng · chỉnh liều theo thận/gan · lưu ý người cao tuổi/thai kỳ/
đa thuốc. Với kháng sinh, ghi phân nhóm WHO AWaRe khi phù hợp.

---

## 4. Quy ước dàn ý slide (storyboard)

- Một slide một thông điệp chính. Tiêu đề slide nên là chính thông điệp đó (câu
  khẳng định), không phải nhãn chung chung ("Điều trị" → "Khởi trị ngay khi nghi
  ngờ, không chờ xét nghiệm khẳng định").
- 3–5 ý/slide; ưu tiên bảng/sơ đồ thay cho đoạn văn dài.
- Không nhồi chữ; không hy sinh ý an toàn quan trọng để "cho đẹp".
- Slide cờ đỏ và cảnh báo an toàn dùng màu cam (#d97757) — xem phong-cach-thi-giac.md.
