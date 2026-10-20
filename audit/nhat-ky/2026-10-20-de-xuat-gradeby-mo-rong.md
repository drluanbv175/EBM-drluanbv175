# 20/10/2026 — Đề xuất gradeBy: 74 mục biến mất khỏi báo cáo, kho mẫu thiếu, ba nhãn gán sai tổ chức

## Bối cảnh
Bác sĩ hỏi hệ cập nhật chứng cứ đã đạt chuẩn chưa. Phép đo sống cho thấy 330/587 mục có `gradeLevel` chưa khai `gradeBy` (140 mục apply), tức khâu minh bạch «ai chấm mức» của GRADE mới đạt một phần. Sau đó bác sĩ yêu cầu: «Giải quyết 3 vấn đề chưa đạt».

## Đo
`tools/de_xuat_gradeby.py` (16/08) chỉ đề xuất được 1/256 mục. Có ba nguyên nhân.
1. **74 mục biến mất khỏi báo cáo.** Mục khớp mẫu GRADE nhưng không có tên tổ chức bị `break` loại khỏi CẢ danh sách đề xuất lẫn danh sách «không tự suy». Báo cáo vì thế đếm 256, trong khi `kiem_phan_hang.py` đếm 330.
2. **Kho mẫu thiếu.** Nhiều `gradeSource` đã ghi rõ ai chấm nhưng kho mẫu không nhận ra: «đánh giá vận hành», Cochrane tự chấm, AAN Level B, GOLD (A–D), ADA A/B/C/E, AHA/ASA «khuyến cáo loại I», AGA «khuyến cáo có điều kiện, độ chắc chắn thấp».
3. **Ba kiểu gán sai tổ chức**, tìm ra khi soát toàn văn từng đề xuất:
   - G1 gán «ACC/AHA» cho một mục trích AHA/ASA;
   - mẫu «LoE» của G5 không phân biệt hoa/thường nên bắt cả «LOE A» của AHA và gán EULAR;
   - lấy tên tổ chức từ trường `org` («SVS / ESVS») nên «SVS grade 1» thành ESVS.

## Đã làm
- Tách `phan_nhom(gs, org)`; `quet()` luôn xếp mục vào một trong hai danh sách. Tổng sau sửa: 330, khớp `kiem_phan_hang`.
- Canh G1 (phải có chữ ACC) và G5 (phải có chữ EULAR).
- Bốn nhóm mới, vẫn theo luật 1 — chỉ đề xuất khi CHỮ của item chứng minh ai chấm:
  - G9: lời người soạn tự nhận «đánh giá vận hành»;
  - G8: Cochrane kèm từ chỉ mức chắc chắn;
  - G10: đúng một tổ chức nêu trong `gradeSource`, trùng tổ chức của item, kèm thuật ngữ phân hạng tường minh; hoặc có thuật ngữ phân hạng mà `org` của item chỉ đúng một tổ chức;
  - G11: chỉ mô tả thiết kế, không nêu tổ chức nào.
- Để tay người, không gán nhãn: mục có «bác sĩ» hoặc «thẩm định», mục nêu từ hai tổ chức trở lên, Cochrane không nêu mức, tổ chức chỉ là tạp chí.
- Kết quả trên kho thật: 223 mục chia 4 nhóm (G9 75 · G8 6 · G10 23 · G11 119) và 107 mục để tay người. Ghi vào dashboard CHỈ khi bác sĩ duyệt nhóm (`--ap-dung`).

## Kiểm
- `tools/test_de_xuat_gradeby_mo_rong_20261020.py`: 17 ca, mỗi ca là một ca thật gặp khi soát.
- 7 phép đột biến đều làm kiểm đỏ.

## Bài học
Một công cụ đề xuất phải được soát bằng TOÀN VĂN đầu vào trước khi trình. Ba nhãn sai tổ chức kể trên đều «nhìn hợp lý» khi chỉ đọc tên nhóm.
