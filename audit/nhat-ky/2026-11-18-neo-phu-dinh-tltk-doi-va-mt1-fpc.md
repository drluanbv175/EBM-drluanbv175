# 18/11/2026 — Cụm neo đặc tả G6 trong câu phủ định; A12 đọc được tài liệu chỉ có DOI; agent bỏ nhầm một mục đặc tả

## Bối cảnh

Bác sĩ hỏi hệ nghiên cứu (không xét từng đề tài) còn cần làm gì, rồi giao hai việc máy. PR y khoa
drluanbv175/medical-ebm-automation#317 sửa cả hai; #318 là PR dữ liệu sửa sai sót lộ ra khi kiểm.

## (2) Cụm neo đặc tả G6 chỉ nằm trong câu phủ định

- **Lỗ hổng:** `kiem_phu_sap` chỉ hỏi «cụm neo có trong SAP không». Câu «Không áp …» vẫn được tính là neo hợp lệ, nên
  một mục SAP đã loại vẫn có thể chạy.
- **Đã sửa:** cảnh báo khi MỌI lần cụm neo xuất hiện đều đứng sau từ phủ định trong cùng mệnh đề (≤ 50 ký tự, không qua
  dấu câu). Có một lần khẳng định là không cảnh báo. Chỉ cảnh báo, không chặn; trục nhất quán chuyển «cần xem».

## (3) Kiểm nội dung trích dẫn A12 đọc được tài liệu chỉ có DOI

- **Lỗ hổng:** chỉ đọc abstract PubMed theo PMID, nên bài tạp chí trong nước, sách và bài phương pháp luôn «không kiểm
  được».
- **Đã sửa:** tra Europe PMC rồi tới Crossref theo đúng DOI. Không trùng DOI thì bỏ; lỗi mạng ⇒ `error`, không thành
  «không thấy».
- **Đo 18/11 (miễn phí):** một đề cương thật có 15 tài liệu chỉ có DOI; lấy được abstract cho 11 (10 Crossref,
  1 Europe PMC).

Đột biến 14/14 đỏ; 102 tệp test liên quan 1570 passed.

## Sai sót của agent lộ ra khi kiểm (sửa ở #318)

- **Chuyện gì xảy ra:** ở #313 agent bỏ mục `MT1_fpc` khỏi đặc tả G6 vì đọc câu «Không áp hiệu chỉnh quần thể hữu hạn ở
  phân tích chính». Chính câu đó còn vế sau: «nếu biết kích thước khung mẫu thì báo thêm KTC có hiệu chỉnh … như một
  thông tin phụ». Quyết định B4 cũng giữ bản hiệu chỉnh ở vai thông tin phụ.
- **Hậu quả:** PI đã duyệt đặc tả thiếu mục này.
- **Phát hiện:** chạy phép cảnh báo phủ định mới trên dữ liệu thật — cụm neo có một lần khẳng định nên đúng là không
  cảnh báo, và câu khẳng định đó lộ ra.
- **Sửa:** chủ nhiệm chọn «Thêm lại vào đặc tả»; neo vào câu khẳng định; PI phải duyệt lại.

## Bài học

- Trước khi bỏ một mục đặc tả hay biến «vì SAP nói không», đọc MỌI lần cụm đó xuất hiện trong SAP và đề cương, không chỉ
  câu đầu tiên. Câu «không … ở phân tích chính» thường đi kèm một phân tích phụ.
- Phép kiểm phủ ở `kiem_phu_sap` chỉ bắt buộc phủ §9 và mục nhãn đậm ở §1/§3/§5/§7. Phân tích phụ viết liền trong §2/§4
  không bị đòi phủ, nên bỏ `MT1_fpc` không làm gì đỏ. Đây là giới hạn đã biết, chưa sửa.
