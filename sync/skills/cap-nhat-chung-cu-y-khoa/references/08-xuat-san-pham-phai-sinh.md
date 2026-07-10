# 08 — Xuất sản phẩm phái sinh từ một bản cập nhật

Mục tiêu: từ MỘT bản cập nhật đã xác minh (khối `DATA` / dashboard đã **PASS cổng liêm chính** `tools/verify_dashboard.py`), tạo nhanh 3 sản phẩm cho 3 đối tượng — **giữ nguyên liêm chính nguồn**, chỉ đổi **ngôn ngữ** và **độ sâu**.

> Nguyên tắc gốc: **không thêm nội dung chưa xác minh**. Mọi sản phẩm phái sinh chỉ lấy từ nội dung đã có trong bản cập nhật; kèm disclaimer; **không PII**; ghi ngày + nguồn chính.

---

## 1. Ba sản phẩm & cách ánh xạ từ `DATA`

| Sản phẩm | Đối tượng | Skill dùng | Độ sâu | Map từ DATA |
|---|---|---|---|---|
| **Tờ dặn người bệnh** (.docx/.pdf) | Người bệnh | `dao-tao-slide-tai-lieu-y-khoa` / `docx` | Phổ thông, BỎ liều & chi tiết kỹ thuật | `summary.conclusion`→tóm tắt; `doNow`→"Bạn nên"; `redFlags`→"Đi khám ngay nếu"; `vn`→lưu ý |
| **Slide bài giảng** (.pptx) | Đồng nghiệp/đào tạo | `dao-tao-slide-tai-lieu-y-khoa` / `pptx` | Giữ độ sâu kỹ thuật | mỗi `item`→1 slide (tiêu đề · khung/PICO · hiệu số đúng nguồn · GRADE · quyết định · PMID); + slide tóm tắt + cờ đỏ + tài liệu tham khảo |
| **Kịch bản TikTok** (script→.mp4) | Cộng đồng | `tao-video-tiktok` | 30–60s, đời thường, 1 thông điệp | `conclusion`→hook+chốt; 2–3 `doNow`→điểm chính; `redFlags`→cảnh báo; "hỏi bác sĩ" |

---

## 2. Quy trình 1-click (4 bước)

1. Hoàn tất bản cập nhật + dashboard (mẫu Dark Analyst mặc định).
2. **Chạy cổng liêm chính:** `python3 tools/verify_dashboard.py <dashboard>.html --online` → phải **PASS**.
3. Chọn sản phẩm → dùng template tương ứng (`templates/phai-sinh-*.md`) + gọi skill tạo file thật.
4. **Bác sĩ DUYỆT** trước khi phát tay / trình chiếu / đăng.

---

## 3. Quy tắc liêm chính cho sản phẩm phái sinh (bắt buộc)

- Chỉ dùng nội dung đã PASS cổng liêm chính; **không thêm số liệu/khuyến cáo mới**.
- **Tờ dặn người bệnh & TikTok: KHÔNG nêu liều thuốc cụ thể** (an toàn, tránh tự dùng); chỉ nói nhóm việc & khi nào gặp bác sĩ. Liều/chi tiết kỹ thuật chỉ ở **slide cho nhân viên y tế**.
- Mọi sản phẩm có **disclaimer "Cần bác sĩ kiểm chứng"** (hoặc với người bệnh: "Thông tin tham khảo, không thay tư vấn của bác sĩ của bạn").
- **Không PII**: không dùng tên/ảnh/mã bệnh nhân thật.
- Ghi **ngày cập nhật + nguồn chính** (vd "Dựa trên ADA 2026, AAN 2022"). Slide đào tạo giữ **tài liệu tham khảo Vancouver + PMID**.
- TikTok: tránh y lệnh trực tiếp ("hãy uống…"); dùng "nên đi khám để được tư vấn"; gắn disclaimer trên màn.

---

## 4. Mẫu nhanh

- Tờ dặn người bệnh: `templates/phai-sinh-to-dan-nguoi-benh.md`
- Kịch bản TikTok: `templates/phai-sinh-kich-ban-tiktok.md`
- Slide: tạo trực tiếp bằng skill `dao-tao-slide-tai-lieu-y-khoa` từ dashboard (mỗi item = 1 slide; giữ hiệu số + GRADE + PMID).

Mỗi mẫu có sẵn ví dụ điền cho ca **biến chứng thần kinh ĐTĐ** để dùng làm khuôn.
