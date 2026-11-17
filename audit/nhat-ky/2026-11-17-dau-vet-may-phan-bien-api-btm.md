# 17/11/2026 — Lượt Claude API thật đầu tiên trên đề cương BTM: 11 dấu vết máy mà K1–K8 bỏ sót, một trích dẫn bị máy làm ngược nghĩa

## Bối cảnh
Ngay sau khi gộp ba công cụ API (medical-ebm-automation#298), bác sĩ tự chạy thật hai công cụ trên đề cương nộp BTM:
- `kiem_noi_dung_trich_dan.py --goi-api`: 4 lượt gọi, ≈ 0,13 USD; 9/50 cặp cần xem.
- `phan_bien_may_de_cuong.py --goi-api`: 1 lượt, ≈ 0,14 USD; 19 phát hiện mức cao/vừa, 5 phát hiện máy không xác minh được.

Đề cương này đã «ĐẠT K1–K8» và có 23 trục xuyên cổng khớp trước đó.

## Đo được — đều kiểm lại bằng tay trên văn bản thật
1. **Mười một dấu vết máy có thật, K1–K8 không bắt.** Nguồn đều là ô đã chốt (`study_meta`) hoặc câu của SAP; bộ sinh chép sang mà làm sạch không đủ:
   - «(xem G0_KHOANG_TRONG)»
   - «gate_params.G0.intervention» → «như.intervention»
   - «(quyết ở G2)» → «(quyết)»
   - «chủ nhiệm chọn tham chiếu 15/11/2026»
   - «(chủ nhiệm duyệt C1–C3)», «(chủ nhiệm đề tài chốt)»
   - «xem điểm S6 của phiếu đề xuất»
   - «qua công cụ phân tích của hệ thống»
   - «(bảng RACI ở A13)»
   - «thống nhất với G3;» → «với;»
   - «(SOP-TR-01)» không giải thích
   - «..»
   - «yeu to» ở Phụ lục A
2. **Máy làm một trích dẫn ngược nghĩa.** SAP viết «EPV ≥ 10 (Ogundimu 2016, PMID 26964707: EPV nên dựa vào dữ liệu, không phải quy tắc cứng)». `TrichDan.thay` nuốt cả lời giải thích, thành «EPV ≥ 10 [41]», trong khi bài [41] phản đối ngưỡng cứng. Lỗi này do máy gây ra, không phải do người soạn.
3. **Bảng 3.1 xếp sai loại tài liệu.**
   - KDIGO Summit (Journal Article) bị xếp «Hướng dẫn thực hành».
   - Sau khi tách loại đồng thuận, lộ thêm một nghiên cứu quan sát tên «Concordance With … Guidelines for …» chiếm suất «hướng dẫn».
4. **Danh mục chữ viết tắt thiếu** UACR, eGFR, BTM, PR, KDIGO, ADA…
5. **Bộ ước tính chi phí của công cụ kiểm trích dẫn thấp**: báo 0,08 USD, thật 0,13 USD.

## Đã sửa (repo y khoa, nhánh `claude/de-cuong-dau-vet-api-20261117`)
- Bộ sinh đề cương: thêm luật gỡ/đổi cho từng dạng trên.
  - Mã cổng làm tân ngữ đổi sang cách nói tương ứng, không xoá trơn.
  - Lời giải thích sau PMID được giữ thành «(lời [k])».
  - Thêm loại «Đồng thuận chuyên môn/báo cáo hội nghị»; nghiên cứu đo tuân thủ hướng dẫn không còn được xếp là hướng dẫn.
  - Phụ lục A có nhãn vai trò tiếng Việt cho mọi mã.
  - Bổ sung chữ viết tắt; thêm lượt dọn dấu chấm đôi trên toàn văn bản.
- K8 thêm 10 luật tất định.
  - Bắt mọi dạng trên trong đề cương BTM cũ.
  - 0 báo oan trên đề cương C1a và 16 đề cương giả lập; trên 16 bản giả lập cũ chỉ bắt đúng lỗi «yeu to».
- Sinh lại đề cương BTM (dữ liệu, cùng PR):
  - K1–K8 ĐẠT; kiểm trích dẫn tất định sạch.
  - Trục xuyên cổng giữ nguyên: 23 khớp, 2 cần xem, 1 lệch mềm — đều là việc của người.
- 40 phép kiểm mới; 21/21 đột biến đỏ đúng chỗ. Một đột biến sống sót ở lượt đầu do luật thừa; đã bỏ luật đó.

## Không sửa — việc của người
- Câu EPV vụng có sẵn trong SAP, và cách diễn đạt ngưỡng EPV khi [38] và [41] phản đối mốc 10. Đây là việc của thống kê viên (SAP chờ ký).
- Số liệu 15,32% và 31,1% chưa có nguồn.
- Định nghĩa bệnh thận mạn nên dẫn thêm [3].
- Đề nghị miễn xét duyệt hay trình xét duyệt; mốc huỷ bảng nối mã; quyết định đăng ký; đếm lại 16 tham số.
- [3] và [4] không có abstract — phải đọc tay.

## Luật rút ra
Bộ kiểm tất định chỉ bắt dạng lỗi đã biết. Một lượt đọc bằng model, có máy kiểm nguyên văn từng phát hiện, rẻ (≈ 0,3 USD cho cả hai công cụ) và tìm được lớp lỗi mà K1–K8 không mô tả. Mỗi phát hiện xác nhận được phải mã hoá NGAY thành luật tất định, để lần sau không cần API mới bắt được.
