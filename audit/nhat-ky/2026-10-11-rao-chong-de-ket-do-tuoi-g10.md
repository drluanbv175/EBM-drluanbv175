# 11/10/2026 — Rào chống đè G2/G4 thoát trước khi ghi checkpoint ⇒ độ tươi kẹt vĩnh viễn, G10 bị chặn

## Đo

- Soát G10 cho C1a với mục đích `ETHICS_SUBMISSION` (gói trình Hội đồng Đạo đức, chỉ đòi G0–G4): `pipeline_freshness`
  báo G2 (13:45) cũ hơn G0/G1 (13:47), G3 cũ hơn G0–G2, G4 (checkpoint 01/09) cũ hơn G0–G3 ⇒ G10-AUTO-03 CHẶN.
- Nguyên nhân: rào «TỪ CHỐI đè» của `run_g2_auto`/`run_g4_auto` (01/09) thoát mã 2 TRƯỚC bước ghi checkpoint. Đề tài
  thật luôn có hồ sơ G2 và SAP đã biên tập (PI phải điền ô trống) ⇒ chạy lại bộ sinh không bao giờ làm tươi được
  checkpoint; cặp G2↔G3 phụ thuộc hai chiều ⇒ không thứ tự chạy nào gỡ được. Mọi đề tài thật sẽ kẹt ở G10.
- Bộ chấm chất lượng ghi checkpoint bằng `ghi_checkpoint_giu_moc_sinh` (giữ mtime, đúng thiết kế) ⇒ nút chốt của PI
  cũng không làm tươi. Test đầu–cuối G10 dùng đồ gá sinh mới, không có bản đã biên tập ⇒ không lộ.

## Vá

- Repo y khoa #122: nhánh từ chối vẫn giữ nguyên bản đã biên tập từng byte, vẫn `.bak-*`, vẫn mã 2, nhưng chấm
  guardrail trên chính bản đã biên tập, ghi lại checkpoint theo thượng nguồn hiện hành và không đè `.docx` chuẩn.
  Đột biến 4/4 bị bắt. Thử thật trên bản sao C1a: hết cổng cũ, dấu vân tay G3/G4 không đổi, trạng thái G0–G4 không đổi.
- Nút `Chot G10 C1a` (gốc, ngoài git): bước «làm tươi» chạy G2→G3→G4 liền nhau, dừng nếu dấu vân tay đổi hoặc cổng tụt.

## Bài học

- Rào bảo vệ nội dung người viết không được bỏ qua phần ghi trạng thái máy (checkpoint, độ tươi): tách «không sinh lại
  nội dung» khỏi «không cập nhật dấu tươi».
- Đồ gá sinh mới không thay được một đề tài thật đã biên tập đi hết dây chuyền tới G10.
