# 13/10/2026 — EndNote: khối tóm tắt tiếng Việt quá dài để đọc nhanh ⇒ bản «EBM · ĐỌC NHANH»

## Vấn đề

- Bản đầu (PR #167) chép gần đủ mọi trường của mục dashboard và tới 3 + 3 ngữ cảnh mỗi trích dẫn: khối tiếng Việt trung vị
  2.241 ký tự, tối đa 9.546. Bác sĩ (13/10): «có thể ngắn gọn và thể hiện điểm nhấn để đọc tiếp cận nhanh cho thực hành».

## Cách làm

- Dòng đầu: khuyến nghị · mức chứng cứ · thiết kế; dòng ★: tiêu đề mục (câu điểm nhấn dashboard đã viết); rồi Kết quả ·
  Thực hành · An toàn · Lưu ý · Tại Việt Nam; cuối: chủ đề · PMID · toàn văn · «Cần bác sĩ kiểm chứng».
- Rút gọn bằng CHỌN TRƯỜNG, không cắt giữa câu (cắt câu có thể mất mệnh đề điều kiện «ngoài thai kỳ», «nếu không chống chỉ
  định»): Kết quả > 320 ký tự hay Tại Việt Nam > 220 ký tự ⇒ bỏ CẢ trường (vẫn giữ số đo hiệu ứng); Thực hành · An toàn · Lưu ý
  luôn in nguyên vẹn. Bỏ quần thể, PICO, theo dõi, nguồn phân hạng.
- Một ngữ cảnh chính = bản dashboard MỚI NHẤT; chủ đề khác chỉ nêu tên. Đo: 131 trích dẫn dùng ở nhiều chủ đề, 33 có khuyến
  nghị KHÁC nhau ⇒ dòng «⚠ Khuyến nghị KHÁC nhau giữa các chủ đề — A: … ; B: …» (không chọn hộ bên nào đúng).
- Chạy lại nhận ra dấu mở đầu của MỌI dạng khối đã ghi (`MO_DAU_DA_DUNG`) ⇒ thay khối cũ, không lồng lên.

## Chạy thật

- 847 bản ghi ghi lại (sao lưu trước), 0 lỗi; đọc lại 826 bản ghi theo PMID: 100% khối mới, 0 khối cũ, đúng một dấu phân cách;
  khối tiếng Việt trung vị 922 ký tự.

## Kiểm

- `tools/test_tom_tat_endnote_vi_20261013.py` 19 ca; 14/14 phép đột biến đỏ đúng chỗ (cắt «Thực hành», bỏ trần kết quả/VN,
  không cảnh báo lệch khuyến nghị, chọn bản cũ nhất, không nhận khối cũ, tham khảo nhận khuyến nghị, «na» ⇒ «Thấp», giá trị lạ
  ⇒ «Cân nhắc», mất abstract gốc, ghi trước sao lưu, coi không đọc được là rỗng, bỏ đổi emoji, ghi khi không đổi).
