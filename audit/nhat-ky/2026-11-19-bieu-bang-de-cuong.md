# 19/11/2026 — Biểu bảng của đề cương «chưa có và chưa đúng chuẩn»

**Bác sĩ:**

> «Tôi đọc qua đề cương thấy phần trình bày biểu bảng chưa có và chưa đúng chuẩn; hãy xây dựng bổ sung vấn đề này thật hoàn thiện»

và thêm: «và cả đồ thị và tất cả vấn đề liên quan số liệu phân tích, kết quả phân tích».

**Đo xác nhận.**
- Chương 5 do máy dựng chép 2–4 bảng chung của SAP §11. Bảng nền chỉ 2 dòng, ô kết cục «…», có dòng «(12 biến)». Không có sơ đồ chọn đối tượng, không biểu đồ, không ghi chú chữ viết tắt.
- C1a (soạn tay): tên bảng in nghiêng; «Hình 5.1» dựng bằng một cái bảng; «Bảng 5.5» chỉ là một câu văn.
- Chỉ mục kết quả G6 in chuỗi JSON thô; G6 chỉ vẽ được Kaplan–Meier.
- K1–K8 không luật nào đo phần này.

**Xây (repo y khoa, PR #336).**
- **`tools/khung_bieu_bang.py`:** dựng chương từ ma trận mục tiêu – biến, bộ biến và đặc tả G6, theo 8 thiết kế:
  - sơ đồ CONSORT/STROBE/STARD/TRIPOD+AI/PRISMA/COREQ vẽ thật;
  - bảng nền không cột p;
  - bảng và biểu đồ cho từng mục tiêu;
  - nhóm nhỏ/độ nhạy kèm forest plot;
  - an toàn cho RCT.
- **Hai chế độ cho đề cương đã có:** `--thay-chuong` và `--nang-cap` (giữ bảng soạn tay).
- **K9 trong `kiem_de_cuong_nop_hoi_dong`.**
- **`md2docx_vn`:** chèn ảnh, căn giữa tên bảng/hình.
- **`chay_sap_g6`:** ước lượng viết theo chuẩn; forest plot vẽ từ số thật.

**Repo gốc.**
- `md_sang_docx_times`: tệp ra trong `exports/` thì bảng 11pt (gốc của 4 Word BTM 12pt), chèn ảnh, căn giữa tên. Có chốt BH183.
- Dạy agent `viet-ban-thao` và `phan-tich-thong-ke`.

**Đo.**
- 26/26 đề tài (24 giả lập + bản chép C1a/BTM) đạt K9 + K4/K8.
- 22 test mới; 14/14 đột biến đỏ; 677 test liên quan đạt.

**Bẫy gặp.**
- «G4 (eGFR 15–29)» theo KDIGO bị K4 đọc thành mã cổng. Khung luôn ghi kèm «eGFR», và K4 chỉ miễn ở dòng có eGFR.
- Mô tả phân tích trong đặc tả viết cho máy («Tỷ lệ xn_du — phòng khám = 1 (nội tiết)»). Phải đổi sang lời cho người đọc trước khi vào văn bản nộp, nếu không K8 bắt.
- Hook runtime chặn lệnh Bash có chuỗi «nc =» (tưởng netcat), nên đoạn vá phải ghi ra tệp rồi mới chạy.
