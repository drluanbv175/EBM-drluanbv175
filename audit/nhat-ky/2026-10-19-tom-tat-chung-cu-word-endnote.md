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
- `tools/test_tom_tat_chung_cu_word_20261019.py`: 28 ca.
- 17 phép đột biến (9 của cổng gốc + 8 của khuôn v2) đều làm kiểm đỏ; phép «nới số nguyên» sống sót ở lượt đầu — đã thêm ca để bắt.

## Trình bày theo yêu cầu bác sĩ (cùng ngày, khuôn v2)
- Bỏ các mục «đối chiếu dashboard», «trích nguyên văn», «câu hỏi còn mở». Mỗi mục mở đầu bằng một ô ĐIỂM NHẤN tô màu, chữ đậm màu mang nghĩa: xanh lá = lợi ích / nguy cơ sai lệch thấp; đỏ = cảnh báo / nguy cơ cao; cam = thận trọng; xanh dương = theo dõi. Bộ dựng chuyển sang python-docx trực tiếp; bộ chuyển Markdown cũ không có màu.
- «Cần kiểm chứng», «cần xác nhận», «[CẦN…]», «đề xuất của máy» bị cấm trong thân văn bản (cổng chặn); chỉ ghi ở mục Lưu ý CUỐI văn bản (trường `can_xac_nhan`). Ghi chú «GRADE do máy đánh giá» chuyển xuống cuối, không bỏ.
- Mở rộng phép kiểm số ra MỌI trường chữ. Ở bài thử, cổng bắt được tổng tự cộng «8399», «2031» và số làm tròn «70%» khi trước đó chỉ phần tóm lược được kiểm.
- Bộ kiểm có hai lỗi đã vá: (1) coi dấu cách thường là phân cách hàng nghìn, nên gộp hai số đứng cạnh nhau trong bảng PDF thành «15121», «696100»; (2) không bỏ số 0 đứng đầu, nên «08» ≠ «8».
- Tệp Word qua trình xác thực OOXML của skill docx. Lỗi duy nhất lúc đầu nằm ở mẫu mặc định của python-docx (`w:zoom` thiếu `w:percent`), đã vá.

## Bác sĩ: «không được phép sai sót về chứng cứ và số liệu» (cùng ngày)
Tự soát lại bản PARADIGM-HF câu theo câu, thấy các lỗi mà cổng kiểm số KHÔNG bắt được:
- «RCT mù đôi lớn nhất» — khẳng định so sánh không có trong bài;
- nhận định về thực hành ở Việt Nam và «chi phí cao» không ghi nguồn;
- số của MỘT nhánh trình bày như số chung (93.1% thay vì 93.1% / 92.9%);
- số «≈».

Đã thêm hai lớp kiểm:
1. Kiểm tất định từng dòng bảng (`kiem_nhat_quan_dong`):
   - ước lượng phải nằm trong KTC 95%;
   - chiều HR/RR/OR phải khớp tỷ lệ hai nhóm (bắt lỗi đảo nhóm);
   - p không được mâu thuẫn rõ với KTC;
   - `danh_gia` của dòng tác hại phải khớp tỷ lệ;
   - cấm «≈», «~».
2. Kiểm chéo ĐỘC LẬP (`kiem-cheo`):
   - MỘT agent ngữ cảnh mới chấm TỪNG câu và TỪNG dòng bảng (PARADIGM-HF: 111 mục);
   - `kiem_cheo.json` gắn băm SHA-256 của đúng bản `tom_tat.json` đã chấm — sửa bản tóm tắt sau đó thì phải kiểm chéo lại;
   - `dung` đòi phủ đủ 100% mục, không mục nào «sai» hay «không có trong bài».
- Kiểm thử: 42 ca; 27 phép đột biến đều làm kiểm đỏ.
- Kiểm chéo lần 1 (PARADIGM-HF, 111 mục, ≈ 332.000 token): 66 đúng · 35 suy luận hợp lý · 2 ngoài bài có nguồn · **1 sai · 7 không có trong bài**. Mọi con số đều khớp; lỗi nằm ở CÂU CHỮ:
  - phù mạch không nặng bị ghi «tương đương», trong khi bài viết nhóm LCZ696 có tỷ lệ cao hơn;
  - «theo dõi phù mạch giai đoạn đầu», SGLT2, «đúng như đăng ký», «đường uống» — không có trong bài;
  - ngưỡng HATT/kali bỏ mất mốc «lúc sàng lọc / lúc ngẫu nhiên»;
  - NNT thiếu khung thời gian.
  Kiểm chéo còn bắt một lỗi CÔNG CỤ: nhãn rút bài kể «Europe PMC» trong khi chuỗi tra chỉ tới PubMed — nay nhãn không kể tên nguồn, nguồn thật đi kèm.
- Kế thừa kết luận: mục KHÔNG đổi chữ và đã đạt thì không chấm lại (băm nội dung từng mục); mục «sai»/«không có trong bài» luôn phải chấm lại. Lần 2: 17 mục phải chấm, 94 mục kế thừa (thêm ≈ 19.000 token). Kết quả lần 2: 5 mục SAI cùng một lỗi — người soạn chép nguyên đề nghị «phù mạch không nặng» của kiểm chéo lần 1, trong khi Bảng 3 có 3 so với 1 ca phải nhập viện; chính kiểm chéo nhận đề nghị lần 1 của nó là sai. Đã tách phù mạch thành 4 dòng theo mức độ của Bảng 3; thêm luật 11 vào hướng dẫn đọc: sửa theo góp ý phải đối chiếu lại bài, tác hại chia mức độ thì ghi từng mức. Lần 3 (11 mục, ≈ 10.000 token): 10 đúng · 1 suy luận hợp lý · 0 sai ⇒ Word được dựng. Tổng chi phí kiểm chéo một bài 12 trang qua ba lượt ≈ 361.000 token (lượt 1 gọi công cụ 8 lần — mỗi lần gửi lại toàn bộ ngữ cảnh; hướng dẫn nay đòi đọc một lần, ghi một lần). Lúc dựng lần cuối mạng mất DNS ⇒ chuỗi rút bài trả «CHƯA KIỂM ĐƯỢC» (Word ghi đúng trạng thái đó, không ghi «chưa bị rút»); dựng lại khi có mạng ⇒ «không thấy» (retraction_watch, pubmed). Kiểm thử 45 ca; thêm 3 phép đột biến, đều làm kiểm đỏ.

## Bài học
Cổng tất định chỉ chứng minh được «số có trong bài», không chứng minh «câu đúng»: khẳng định định tính sai (so sánh nhất, nhận định ngoài bài) chỉ một người đọc độc lập mới bắt được — nên kiểm chéo độc lập là bắt buộc trước khi ra Word. Bác sĩ dựa vào bản tóm tắt để thực hành, nên cổng phải đối chiếu số với TRANG của PDF chứ không đối chiếu với trí nhớ của mô hình. PDF tách chữ sinh ra gạch nối kiểu «air -⏎way» và chữ của bảng chen giữa câu; bộ so khớp trích dẫn phải chịu được các lỗi này nhưng không được nới tới mức nhận câu bịa.
