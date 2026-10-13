# 13/10/2026 — EndNote: tóm tắt thực hành tiếng Việt trong trường Abstract; emoji bị EndNote đổi thành «?»

## Yêu cầu

- Bác sĩ (13/10): mỗi trích dẫn đưa vào EndNote phải có toàn văn, và trường Abstract ghi tóm tắt tiếng Việt cho thực hành
  lâm sàng để mở bản ghi là đọc nhanh được chứng cứ.

## Cách làm (không sinh nội dung y khoa mới)

- `tools/tom_tat_endnote_vi.py`: khối «TÓM TẮT THỰC HÀNH» CHÉP các trường của mục dashboard đã qua cổng liêm chính
  (tiêu đề, nguồn, thiết kế, quần thể, PICO, kết quả, mức chứng cứ, khuyến nghị, theo dõi, an toàn, áp dụng VN, lưu ý) với
  ĐÚNG nhãn của mẫu dashboard («Nguồn không phân hạng» ≠ chứng cứ yếu; giá trị lạ ⇒ «chưa rõ», không đoán). Bài chỉ là tài
  liệu tham khảo của một mục ⇒ ghi vai đó, KHÔNG gán kết quả/khuyến nghị của nguồn chính. Mỗi chủ đề lấy phiên bản dashboard
  MỚI NHẤT; trích dẫn chỉ còn ở bản cũ vẫn có khối, gắn nhãn «bản dashboard CŨ».
- Abstract gốc giữ nguyên dưới dấu phân cách; chạy lại chỉ thay khối tiếng Việt; khối không mang ngày chạy ⇒ dashboard không
  đổi thì lượt sau không ghi gì. Không đọc được Abstract ⇒ không ghi đè. Sao lưu nhất quán `sdb.eni` (đọc được khi EndNote
  đang mở; `.enl` bị khoá độc quyền nên chép tệp) TRƯỚC lần ghi đầu; sao lưu hỏng ⇒ không ghi gì.
- `nap_endnote_chu_de.py --tom-tat-vi` (chạy khô mặc định) và tự chạy sau mỗi lượt nạp `--ap-dung` (`--khong-tom-tat` để tắt).
  `EndNoteMac.doc_truong`/`ghi_truong`: ngăn bằng ký tự điều khiển 30/31 (Abstract có xuống dòng), ghi xong đọc lại trong
  cùng lệnh.

## Sự cố đo được khi chạy thật

- Lượt ghi 846 bản ghi: 845 khớp, 1 lệch — EndNote KHÔNG lưu được ký tự ngoài mặt phẳng cơ bản: «🔴» đọc lại thành «?». Vá:
  emoji màu ⇒ nhãn chữ («●đỏ»…), ký tự ngoài mặt phẳng cơ bản khác ⇒ «◆». Lượt sau ghi đúng bản ghi đó, 0 lỗi.
- Kho dùng chủ yếu `\n` cho xuống dòng (78 abstract) so với `\r` (17) — khối ghi bằng `\n`, so đọc lại sau chuẩn hoá.

## Kiểm

- `tools/test_tom_tat_endnote_vi_20261013.py` 16 ca; 12/12 phép đột biến đỏ đúng chỗ (gán kết quả cho bài tham khảo, «na» ⇒
  «Thấp», quyết định lạ ⇒ «Cân nhắc», mất abstract gốc, không nhận khối cũ, ghi trước sao lưu, ghi khi không đổi, coi không đọc
  được là rỗng, bản cũ thắng bản mới, in ô giữ chỗ, so đọc lại không chuẩn hoá, tham khảo tự trỏ thành ngữ cảnh thứ hai).
