# 07/11/2026 — EndNote: bản ghi không nhóm, không tag lọt khỏi kế hoạch gắn tag; 11 bản ghi mất nhóm + tag sau một lượt đồng bộ

Bác sĩ giao: «Trong Endnote tôi đã có nhiều tab hãy gắn tab tất cả cho phù hợp giúp tôi», sau đó «Tiếp tục hoàn thiện».

## Hiện tượng (đo trên `sdb.eni`, chế độ chỉ-đọc)

- Kế hoạch của `tools/gan_tag_endnote.py` chỉ xét bản ghi THUỘC NHÓM (tag theo nhóm) và tag Áp dụng (theo dashboard). Kết quả là
  nó in «✓ Mọi bản ghi đã đủ tag theo luật» trong khi 74/3.504 bản ghi không thuộc nhóm nào và không có tag nào. Gồm:
  - 6020–6121: bản ghi bác sĩ tự nhập 11/2025, phần lớn tim mạch – chuyển hoá;
  - 7328–7331: câu hỏi AskTrip-AI;
  - 7414–7473: trích dẫn đã chuyển sang `loai_bo` của đề tài btm-dtd2-ngoai-tru-BVQY175;
  - 8103: bản ghi tóm tắt chủ đề VKDT – tâm thần kinh, nằm ngoài nhóm của chủ đề.
- 11 bản ghi chủ đề Chăm sóc giảm nhẹ (9080 … 9109, nhập 09:05):
  - bản sao lưu 09:45 cho thấy chúng còn tag «Lão khoa» (9088 có thêm «★ Áp dụng»);
  - bản sao lưu 10:06 cho thấy chúng đã mất HẾT tag và không còn thuộc nhóm nào;
  - không lệnh nào báo việc này.
- Theo số đo của phiên «Cập nhật vấn đề Endnote», `changed_membership_timestamp` đổi TUẦN TỰ theo recNum, mỗi bản ghi cách nhau
  2–3 giây (10:05:11 → 10:05:33), rồi `record_last_updated` của cả 11 bản ghi cùng mang mốc 10:05:46.
- Màn hình Sync Status lúc 10:09 ghi «Last sync … 10:06». Không công cụ nào của hệ chạy lệnh bỏ khỏi nhóm hay bỏ tag trong khoảng đó.

## Nguyên nhân

- Kế hoạch thiếu nhánh cho bản ghi lẻ (không nhóm). Có thể có tag mà không ai kiểm.
- Vì sao 11 bản ghi mất nhóm và tag thì **chưa chứng minh được**. Giả thuyết là đồng bộ online của EndNote lúc 10:05–10:06 ghi đè
  trạng thái nhóm/tag phía máy bằng trạng thái phía online: kiểu thay đổi tuần tự từng bản ghi khớp với cách xử lý của Sync,
  không khớp với một lần kéo-thả.

## Cách vá

- `sync/endnote-tag-ban-ghi-le.json` (khoá recNum):
  - 73 bản ghi lẻ được phân loại theo tiêu đề: tag chuyên khoa rộng kèm tag chủ đề sẵn có;
  - không gắn «Nghiên cứu khoa học» cho trích dẫn đề tài đã loại;
  - tag lẻ mất ⇒ kế hoạch hiện thành thiếu.
- Kế hoạch có thêm hai mục:
  - `chua_phan_loai`: không nhóm, không trong tệp lẻ, không tag nào ngoài tag Áp dụng ⇒ 🛎;
  - `tag_trung`: tên tag xuất hiện ở ≥ 2 tag ⇒ 👤 (đo 07/11: «Frailty» ×2, đã gộp).
- Nhóm làm việc tên bắt đầu bằng «_»:
  - không đòi tag;
  - bản ghi chỉ nằm ở nhóm đó vẫn tính là chưa phân loại, trừ nhóm chờ thùng rác.
- Hòm việc `tu_de_xuat_viec.giac_quan_gan_tag_endnote` báo cả hai mục mới.
- Tệp lẻ hỏng ⇒ «không đo được» và báo đúng tên lỗi, kể cả trên máy chưa có EndNote.
- `--huong-dan`: ưu tiên CHẾ ĐỘ NỀN. Đo 07/11: các dòng do `--hien` tô sáng chính là vùng chọn ⇒ `app_drag` từ một dòng tô sáng mang
  cả vùng chọn (43 bản ghi một lần kéo, 22 tag · 153 cặp, 0 nhầm). Bấm vào danh sách làm mất vùng chọn.
- Đã làm trên thư viện thật:
  - 73 bản ghi lẻ được gắn tag;
  - 8103 vào nhóm 149;
  - 11 bản ghi giảm nhẹ vào lại nhóm 30 «End-of-life & Palliative Care» và nhận lại «Lão khoa»;
  - 41 bản ghi Sỏi thận từ hàng chờ vào nhóm 38 và nhận tag;
  - 9088 và 9111 nhận «★ Áp dụng».

  Sau mỗi lượt đều đối chiếu với bản sao lưu: 0 tag thêm ngoài kế hoạch, 0 mất.

## Kiểm

- `tools/test_endnote_tag_ban_ghi_le_20261107.py`: 18 ca.
- Sửa fixture `test_ke_hoach_du_tag`: bản ghi ngoài nhóm nay mang tag bác sĩ tự gắn, đúng định nghĩa mới; không nới assertion.
- 20 đột biến trên mã mới đều đỏ, phục hồi xanh.
- Chạy thật sau khi vá: «✓ Mọi bản ghi đã đủ tag theo luật» (3.544 bản ghi), hòm việc không còn mục.

## Bài học

- «Đủ tag theo luật» chỉ đúng với tập bản ghi mà luật CÓ xét. Phải đếm cả phần bù (bản ghi không thuộc nhóm nào).
- Đồng bộ online có thể làm mất nhóm/tag mà không báo ⇒ sau mỗi lượt gắn tag, chạy lại kế hoạch sau lượt đồng bộ kế tiếp; cảm biến
  `chua_phan_loai` ở hòm việc là lưới đỡ.
