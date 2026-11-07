# 07/11/2026 — EndNote: bài rút trong thư viện không ai đối chiếu lại; nền Retraction Watch quá hạn; bản ghi rời nhóm sau đồng bộ

Bác sĩ hỏi đề xuất tốt nhất cho hệ chứng cứ kết nối EndNote, rồi chọn «Làm 1 và 2 trước cho tôi».

## Hiện tượng (đo trên `sdb.eni`, chế độ chỉ-đọc)

- Cổng `verify_dashboard` và tác vụ lịch `kiem-rut-bai-kho-thang` chỉ tái kiểm trích dẫn CỦA DASHBOARD. Bản ghi đã nằm trong EndNote
  thì không ai đối chiếu rút bài lại; ví dụ bản ghi bác sĩ tự nhập 11/2025, trích dẫn đề tài, câu hỏi AskTrip.
  Thư viện có 3.586 bản ghi: 3.375 có PMID/DOI, 211 không có định danh.
- Nền Retraction Watch trên máy đã **48 ngày tuổi** (hạn 30). `chu_trinh_chung_cu.py` chỉ gợi ý tải khi nền VẮNG, không tải khi
  nền CŨ, và không tác vụ nào làm mới nó.
- Bản ghi rời nhóm: một lượt đồng bộ online sáng cùng ngày làm 11 bản ghi rời nhóm chủ đề (`2026-11-07-endnote-ban-ghi-chua-phan-loai.md`).
  - Phép đo đầu tiên so khoá chủ đề với TÊN nhóm trong bảng `nhom_theo_chu_de` và ra 44 bản ghi «lệch». Soát từng bản ghi thì
    43/44 vẫn ở đúng nhóm chủ đề, chỉ là nhóm đã được bác sĩ đổi tên hoặc gộp, nên đó là báo động giả. Bản ghi duy nhất đặt sai
    thật là 8102 (tóm tắt chủ đề Suy tim nằm trong nhóm Thuốc ĐTĐ típ 2 & béo phì); đã báo bác sĩ, chưa sửa.
  - Định nghĩa đúng: mang khoá chủ đề mà KHÔNG thuộc nhóm phân loại nào. Theo định nghĩa này còn 17 bản ghi, đều là trích dẫn
    đề tài btm-dtd2 đã chuyển sang `loai_bo` có chủ ý.

## Cách vá

- **Làm mới nền**: đã chạy ngay `tai_retraction_watch.py` (bác sĩ đồng ý tải; Crossref Labs hết giờ chờ nên công cụ tự chuyển
  sang gương GitLab chính thức). Kết quả 73.688 dòng, nhiều hơn bản cũ 1.067 dòng.
- **`tools/kiem_rut_bai_endnote.py` (mới)**: đối chiếu mọi PMID/DOI với chỉ mục Retraction Watch của engine. Công cụ ngoại tuyến,
  chỉ đọc, chạy chưa tới 1 giây.
  - «Retraction» ⇒ đã rút; «Expression of concern» ⇒ báo riêng. Correction và Reinstatement không tính.
  - PMID «không biết» thì tra DOI.
  - Nền vắng ⇒ «không đo được» (⚪); nền quá hạn ⇒ 🟡. Không trường hợp nào được đọc thành «không có bài rút».
- **`gan_tag_endnote.py`**:
  - Bài rút cần tag «⛔ Đã rút bài» và mất tư cách «★ Áp dụng – tin cậy cao»: ★ đang có thì báo thừa, ★ chưa có thì không đòi gắn.
  - Thêm `roi_nhom` (🛎) kèm nhóm đề xuất; không tính trích dẫn đề tài đã loại và bản ghi ở nhóm chờ thùng rác.
  - Thêm `--dua-ve-nhom` để ghi hàng chờ `--cho-vao-nhom`. Nhóm đề xuất không còn ⇒ chọn tay, không đoán.
- **Hòm việc**: bài ĐÃ RÚT ⇒ 👤 ưu tiên 0; Expression of concern ⇒ 👤; nền quá hạn ⇒ 🤖; rời nhóm ⇒ 🛎. Không đo được ⇒ giác quan chết.
- **Tác vụ lịch `kiem-rut-bai-kho-thang`**: thêm bước 1b (làm mới nền khi quá hạn) và 2b (quét EndNote).

## Kiểm

- 20 ca mới (1 ca đầu–cuối với chỉ mục thật của engine, tự bỏ qua có khai báo khi máy không có repo y khoa).
- 30 đột biến đều đỏ, phục hồi xanh.
- Đối chứng dương trên nền thật: bắt đúng bài Wakefield (PMID 9500320 và DOI) và PMID 30267080 (rút-và-thay).
- Chạy thật trên thư viện: không thấy bài rút/EoC trong 3.375 bản ghi có PMID/DOI (nền 0 ngày), không bản ghi rời nhóm, hòm
  việc sạch. «Chưa thấy trong danh mục» KHÔNG có nghĩa «chưa bị rút».
