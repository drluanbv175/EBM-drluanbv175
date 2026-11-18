# 18/11/2026 — Giữ trích dẫn đạt chuẩn khi chưa có toàn văn (riêng C1a, lời bác sĩ)

**Bối cảnh.** Sáng 18/11 bác sĩ đặt luật «tất cả trích dẫn cho nghiên cứu … phải luôn là toàn văn, nếu … không thể lấy
được toàn văn thì loại bỏ». Luật được mã hoá thành chốt G10-AUTO-12 (repo y khoa PR #324; repo gốc #431, #432).
Sau đó tôi chạy hai làn toàn văn cho đề tài thật (biên nhận ở PR dữ liệu y khoa #326):
- BTM: 42/42 TLTK có toàn văn.
- C1a: 33/58 có toàn văn; 10 TLTK đã thử đủ hai làn mà không lấy được; 15 còn làn chưa thử.

**Vấn đề.** Gỡ 10 bài kia theo luật sẽ xoá căn cứ của các câu phương pháp trong đề cương và SAP:
- ngưỡng chỉ số phù hợp CFA (Hu & Bentler 1999; Browne & Cudeck 1992);
- hồi quy Firth (Heinze & Schemper 2002);
- cỡ mẫu theo cụm (Eldridge 2006; Campbell 2005).

Bác sĩ chọn «(a) Loại theo luật», rồi chỉnh lại ngay: «Riêng với đề tài C1a hãy giữ lại trích dẫn đủ tiêu chuẩn
của nghiên cứu y khoa chuẩn».

**Cách vá** (repo y khoa PR #327, `tools/toan_van_trich_dan.py`):
- Quyền GIỮ ghi theo TỪNG đề tài ở `exports/<mã>/GIU_TRICH_DAN_CHUAN_<mã>.json`, bắt buộc nguyên văn lời bác sĩ.
- Chỉ giữ TLTK đạt đủ ba tiêu chí. Cổng đo lại ở mỗi lần chạy, không tin lời khai trong tệp:
  - **định danh:** PMID trong A12 khớp DOI hoặc tiêu đề; DOI có bản ghi Crossref khớp tiêu đề và năm; văn bản không
    định danh có cơ quan ban hành + số hiệu, hoặc tổ chức y tế quốc tế là nhà xuất bản;
  - **rút bài:** đã kiểm không rút trong 30 ngày;
  - **loại nguồn:** bài tạp chí có bình duyệt, sách học thuật, văn bản quy phạm, tài liệu của tổ chức y tế quốc tế.
    Tiền ấn phẩm không đạt, kể cả medRxiv có PMID.
- Kết quả cổng:
  - bài giữ bị rút ⇒ BLOCK;
  - kiểm rút bài quá hạn ⇒ REVIEW;
  - đạt ⇒ `DAT_CO_GIU`: G10-AUTO-12 PASS kèm danh sách TLTK được giữ, để không trông như mọi bài có toàn văn.
- Được giữ không miễn việc tiếp tục tìm toàn văn.

**Đo trên dữ liệu thật C1a (chạy khô).** Cả 25 TLTK chưa có toàn văn đều đạt:
- 22 bài có PMID/DOI phân giải đúng và đã kiểm không rút. Bài 21 khớp tiêu đề thấp chỉ vì tiêu đề gốc tiếng Tây Ban
  Nha; DOI trùng.
- Hai quyết định của Bộ Y tế: 56/QĐ-BYT/2024 và 3869/QĐ-BYT/2019. Đề cương ghi đúng rằng mẫu phiếu của QĐ 3869 đã được
  QĐ 56 thay thế.
- Sách WHO của Lwanga & Lemeshow, 1991.

**Kiểm hồi quy.**
- `tests/test_giu_trich_dan_chuan_20261118.py`: 23 test. Kiểm đột biến 18/18 đỏ đúng chỗ, phục hồi thì xanh. Đột
  biến M1 lúc đầu sống sót vì bài giữ bị rút mà còn làn chưa thử chỉ rơi xuống «còn việc»; test đã được làm chặt.
- Dạy `kiem-chung-trich-dan`, `thu-thu-tai-lieu`, `dieu-phoi-g10` ở cả bản gốc (PR này) lẫn bản sao trong repo y khoa.

**Bài học.**
1. Một luật toàn cục («không toàn văn thì loại») có thể phá căn cứ phương pháp. Trước khi thi hành phần gỡ bỏ, phải
   cho bác sĩ thấy câu nào trong đề cương mất căn cứ.
2. Ngoại lệ của bác sĩ được ghi bằng tệp theo đề tài, kèm nguyên văn lời bác sĩ, và máy đo lại mỗi lần chạy. Không
   nới luật chung.
