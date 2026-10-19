# 19/10/2026 — Tóm tắt chứng cứ Word cho từng trích dẫn có PDF; EndNote chỉ nhận tệp thêm dạng LIÊN KẾT

## Bác sĩ yêu cầu
Với mỗi trích dẫn có PDF toàn văn, bổ sung một tệp Word tóm tắt chi tiết bằng tiếng Việt, font Times New Roman, theo cấu trúc chuẩn tóm tắt chứng cứ cho thực hành lâm sàng. Bác sĩ sẽ dựa vào bản này để thực hành. Nếu EndNote không nhận Word thì chuyển sang PDF.

## Đo
- Thư viện có 875 bản ghi kèm PDF (19.148 trang; trung vị 13 trang, p90 39 trang, 70 tài liệu dài hơn 50 trang). Theo ngữ cảnh dashboard:
  - tầng 1 — nguồn chính của mục apply: 158;
  - tầng 2 — consider: 390;
  - tầng 3 — notyet/khác: 76;
  - tầng 4 — chỉ tham khảo hoặc không thuộc dashboard: 251.
- Thử trên BẢN SAO thư viện, đặt ngoài OneDrive:
  - `set field "File Attachments"` với giá trị = tệp cũ + `\r` + `file://…docx` ⇒ EndNote NHẬN Word. PDF cũ giữ nguyên (`file_type` 1); Word là tệp LIÊN KẾT theo đường dẫn tuyệt đối (`file_type` 2), không được chép vào `.Data/PDF`. PDF thêm vào theo cách này cũng chỉ là liên kết.
  - Gán thẳng `internal-pdf://<thư mục>/<tệp>` (kể cả khi thư mục mang tên số) ⇒ trả về `missing value`, sau đó cửa sổ bản sao đóng. KHÔNG thử cách này trên thư viện thật.

## Đã làm
`tools/tom_tat_chung_cu_word.py`:
- `liet-ke` / `tien-do` / `chuan-bi` / `kiem` / `dung [--gan-endnote --ap-dung]`.
- Gói đọc nằm ở `~/.ebm-cache/` (ngoài OneDrive). Word lưu cạnh thư viện ở `TomTatChungCu/`; JSON đã qua cổng lưu ở `TomTatChungCu/_nguon/`.
- Cổng kiểm, chặn (fail-closed) khi:
  - một con số không có nguyên văn trên trang khai (±1 trang). Số do máy tự tính phải khai `may_tinh` và được in kèm dấu †;
  - đoạn trích dài quá 15 từ, hoặc không tìm thấy trên trang khai;
  - công cụ nguy cơ sai lệch không đúng thiết kế nghiên cứu;
  - mức GRADE nằm ngoài danh mục cho phép;
  - PMID không khớp bản ghi EndNote;
  - định danh của tệp PDF không khớp bài;
  - bài đã bị rút. Rút bài được tra LẠI mỗi lần dựng, bằng chuỗi 3 tầng.
- Khi gắn vào EndNote:
  - giữ các tệp cũ; nếu đọc lại thấy mất tệp cũ thì ghi trả ngay;
  - không đọc được tệp cũ ⇒ không ghi;
  - mọi lần ghi đi qua khoá ghi.
- Bài thử đầu tiên: PARADIGM-HF (PMID 25176015) đã được gắn vào recNum 6914; PDF gốc còn nguyên.

## Kiểm
- `tools/test_tom_tat_chung_cu_word_20261019.py`: 22 ca.
- 9 phép đột biến đều làm kiểm đỏ (một phép sống sót ở lượt đầu — nới số nguyên — đã thêm ca để bắt).

## Bài học
Bác sĩ dựa vào bản tóm tắt để thực hành, nên cổng phải đối chiếu số với TRANG của PDF chứ không đối chiếu với trí nhớ của mô hình. PDF tách chữ sinh ra gạch nối kiểu «air -⏎way» và chữ của bảng chen giữa câu; bộ so khớp trích dẫn phải chịu được các lỗi này nhưng không được nới tới mức nhận câu bịa.
