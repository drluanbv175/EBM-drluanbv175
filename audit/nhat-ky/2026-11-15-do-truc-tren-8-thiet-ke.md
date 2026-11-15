# 15/11/2026 — Đo mọi trục nhất quán trên đề tài giả của 8 thiết kế: một báo sai cho định tính; giới hạn «mọi đề tài»

**Bác sĩ (nguyên văn):** «Tất cả vấn đề xây dưng cho hệ thống nghiên cứu y khoa đã đạt sự đồng bộ xuyên suốt và đạt chuẩn để có thể thực hiện với tất cả các nghiên cứu y khoa chưa chứ không phải chỉ cho 2 đề tài trên».

## Cách đo

Dựng đề tài giả nhất quán đi trọn G0→G10 cho từng thiết kế, dùng đồ gá `_de_tai_g10_that` của test đầu–cuối G10. Tám thiết kế: RCT, thuần tập, bệnh–chứng, cắt ngang, chẩn đoán, mô hình dự báo, SR/MA, định tính. Chạy `nhat_quan_xuyen_cong.doi_chieu` và tổng hợp mức của từng trục.

## Kết quả

- Không trục nào sập. Không có lệch cứng hay lệch mềm sai ở thiết kế nào.
- **Một báo sai thật:** trục `thoi_diem_ket_cuc` (thêm cùng ngày) đòi SAP §2 của nghiên cứu **định tính** nêu «thời điểm đo kết cục chính». Với định tính, kết cục chính là hiện tượng/câu hỏi nghiên cứu ⇒ đã sửa; mốc thời gian nếu có vẫn được so.
- Các «cần xem» khác là do đồ gá giả: thiếu `title` và `research_question`, mục tiêu kiểu RCT cho mọi thiết kế, kết cục có xác nhận của PI.
- Các trục vắng mặt (kiểm soát sai lệch, quy trình dữ liệu, công cụ đo lường…) là do đồ gá chưa khai tiền đề G1. Đề tài thật đã khai G1 mà thiếu bảng đối chiếu thì trục hiện «chưa đủ để so», không im lặng.

## Cách vá

**Repo y khoa:**
- `truc_thoi_diem_ket_cuc(…, thiet_ke=)`: thiết kế định tính không bị đòi thời điểm ở SAP.
- Phép đo được biến thành test thường trực `tests/test_truc_tren_8_thiet_ke_20261115.py`: 8 ca; đột biến bỏ bản sửa ⇒ đỏ đúng ca định tính.

**Repo gốc:** dạy `dieu-phoi-nghien-cuu` phải nêu phạm vi thiết kế đã kiểm và chạy test 8 thiết kế khi sửa trục hay bộ sinh.

## Giới hạn trung thực (báo bác sĩ)

| # | Giới hạn |
|---|---|
| 1 | Bằng chứng trên đề tài thật chỉ ở 2 đề tài cắt ngang; bảy thiết kế còn lại mới có bằng chứng trên đề tài giả. |
| 2 | Các điểm đồng bộ đặc thù từng thiết kế (RCT, thuần tập, chẩn đoán, SR/MA, định tính) chưa được rà theo chương trình 9 giai đoạn. |
| 3 | Bảng quy trình dữ liệu, đặc tả G6, đề cương nộp còn dựng tay (chưa có lệnh sinh khung). |
| 4 | Bước 8–12 chưa chạy trên dữ liệu thật. |
| 5 | Còn các PR chưa gộp. |
| 6 | Máy không chấm được chất lượng nội dung hay tính độc lập của người ký. |

**Không** kết luận «đạt cho mọi nghiên cứu y khoa».
