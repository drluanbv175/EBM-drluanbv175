# 20/10/2026 — gradeBy G11 gán «nguồn không tự phân hạng» cho mục trích GRADE của chính nguồn

**Phát hiện.** Bác sĩ duyệt các nhóm đề xuất `gradeBy` ngày 20/10/2026. Trước khi ghi, tôi rà từng mục; 5/119 mục của G11
có nhắc tới chất lượng hoặc mức chứng cứ:
- VKDT_TamThanKinh ITEM-05 ghi «GRADE nguyên văn: very low/low-quality» — đây là phân hạng CỦA BÀI, vậy mà bị đề xuất
  «Người soạn — đánh giá theo thiết kế (nguồn không tự phân hạng)». Ghi như thế là sai truy nguyên (họ R4).
- BenhMachMauNao_HopNhat ITEM-09 «IPD meta-analysis (chứng cứ độ chắc chắn cao)» và SuyTim ITEM-12 «Meta-analysis độ
  chắc chắn cao» không nói ai chấm, nên máy không được đoán.
- Hai mục còn lại thật sự do người soạn chấm: một mục là khối GRADE EtD do người soạn dựng, một mục là NOS — thang chất
  lượng các nghiên cứu thành phần.

**Nguyên nhân.** Luật G11 chỉ đòi chữ mô tả thiết kế, không có tổ chức, không có «khuyến cáo/guideline». Luật không loại
trường hợp chữ có nói về MỨC CHẮC CHẮN, mà mức đó có thể là của nguồn.

**Cách vá.** `_MUC_CO_THE_CUA_NGUON` (GRADE trừ «GRADE EtD» · nguyên văn · certainty · quality · độ chắc chắn · chất
lượng cao/thấp/trung bình) chặn G11; các mục này về nhóm «để tay người». Chạy lại đề xuất: G11 từ 119 còn 115, nhóm tay
người từ 107 lên 111.

**Kiểm hồi quy.** `tools/test_de_xuat_gradeby_mo_rong_20261020.py` thêm 4 ca phải để tay người và 2 ca phải giữ G11.
4 phép đột biến đều đỏ: bỏ chốt · loại cả GRADE EtD · bỏ «nguyên văn» · bỏ «độ chắc chắn».

**Áp dụng (bác sĩ duyệt 20/10/2026: «Duyệt nhóm gradeBy»).** `--ap-dung G8 G9 G10 G11` ghi 219 trường vào 33 dashboard
(mỗi tệp có sao lưu `.bak-gradeby-2026-10-20`). Kiểm theo dòng so với bản sao lưu: chỉ có 219 chuỗi `gradeBy` được chèn, 0
thay đổi khác; cả 33 tệp vẫn qua `verify_dashboard.py` (mã 0). Số mục thiếu `gradeBy` giảm từ 330 xuống 111 (mục apply từ
140 xuống 55).
