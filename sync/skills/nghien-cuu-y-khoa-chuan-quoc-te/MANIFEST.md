# Manifest

- Tên gói: `nghien-cuu-y-khoa-chuan-quoc-te`
- Phiên bản nội dung: 5.3
- Ngày chỉnh sửa: 2026-07-06
- Ngôn ngữ: Tiếng Việt
- Phạm vi: Nghiên cứu y khoa đa thiết kế, từ G0 đến G9.

## Thay đổi của bản 5.3 (2026-07-06)

1. Làm giàu `templates/01_mau_de_cuong_tong_the.md` — từ bản chỉ có tiêu đề mục (16 mục + khối kiểm soát + Phụ lục, không nội dung hướng dẫn) thành template có hướng dẫn/bẫy thường gặp dưới mỗi mục, rút ra từ một ca thực tế (đề tài khảo sát hài lòng người bệnh) đã xử lý xong ở hệ agent nghiên cứu song song của dự án.
2. 5 bài học phương pháp được lồng vào đúng mục liên quan: (a) mục 9 — bắt buộc xác minh công cụ thu thập/CRF thật trước khi giả định dùng thang chuẩn quốc gia/quốc tế; (b) mục 7 — ưu tiên mục hỏi trực tiếp/độc lập làm kết cục chính khi công cụ có cả mục theo lĩnh vực lẫn mục hỏi chung (tránh thiên lệch phần-toàn thể); (c) mục 10 — codebook đã tự dựng sẵn là nguồn sự thật, đối chiếu trước khi tự suy luận phương pháp khác; (d) mục 10 — trường định danh nội bộ (vd mã hồ sơ bệnh án) dùng đối soát/chống trùng phải tách khỏi bộ dữ liệu bàn giao phân tích; (e) mục 9 — miền/thang con 1-2 mục không báo cáo Cronbach's alpha như một thang đầy đủ.
3. KHÔNG đổi khung G0-G9, KHÔNG đổi số lượng/tên 16 mục cấp 1 hay cấu trúc Phụ lục — chỉ bổ sung nội dung hướng dẫn dưới các tiêu đề đã có.
4. Hai script kiểm định của skill chạy lại: xem `CHANGELOG_V9.md`.

## Thay đổi của bản 5.2 (2026-06-06)

1. Tái kiểm chứng văn bản pháp luật Việt Nam với nguồn sơ cấp (xem `CHANGELOG_V8.md` và `references/00`):
   Thông tư 43/2024/TT-BYT (hiệu lực 01/02/2025, Điều 22) và Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15
   (hiệu lực 01/01/2026). **Không phát hiện thay đổi nội dung** so với bản 5.1 — chỉ gia hạn độ tươi nguồn.
2. Hai script kiểm định (`validate_skill.py`, `run_static_evaluations.py`) chạy lại: ĐẠT.

## Thay đổi trọng yếu của bản 5.0

1. Tối ưu `description` để Claude phát hiện đúng các yêu cầu nghiên cứu thường gặp; tuân thủ giới hạn chính thức tối đa 1024 ký tự.
2. Rút gọn `SKILL.md` thành bộ điều phối theo progressive disclosure; chi tiết chuyên biệt nằm trong references/workflows/modules/templates/quality.
3. Chuẩn hóa cổng chất lượng G0-G9 và điều kiện kết luận “sẵn sàng”.
4. Cập nhật nguồn kiểm chứng chính thức: Claude Skills, Declaration of Helsinki 2024, ICH E6(R3) 2025, ICMJE 01/2026, Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15, Luật Khám bệnh chữa bệnh 15/2023/QH15, Thông tư 43/2024/TT-BYT.
5. Bổ sung workflow bảo trì/kiểm thử sau khi dùng `skill-creator`.
6. Tách bộ kiểm thử thành checklist cấu trúc và ca kiểm thử đầu ra; thêm script đánh giá tĩnh nội dung.

## Giới hạn kiểm định

Các script trong gói xác nhận cấu trúc, liên kết file và sự hiện diện của các yêu cầu an toàn. Chúng không chứng minh Claude sẽ tạo đáp án đúng trong mọi tình huống; cần kiểm thử sau upload bằng ca thực tế và rà soát chuyên gia.
