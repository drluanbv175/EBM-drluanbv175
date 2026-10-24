# 24/10/2026 — Đặt-cạnh (Đài E-MOI) đếm cả dashboard đã bị phiên bản nối tiếp thay

**Hiện tượng.** Đài E-MOI «79 mục `apply` có nguồn tổng hợp mới hơn, chờ so» — đọc từ đầu bản
`DAT-CANH-CHUNG-CU-MOI_2026-10-18.md`. Sau 33 mục bác sĩ đã đóng ngày 18/10 (nhóm L/S), 79 mục còn lại phân theo dashboard
cho thấy nhiều mục nằm ở bản ĐÃ BỊ THAY: `BenhMachMauNao_HopNhat_20260614` (9 mục) đã có bản nối tiếp 18/10;
`SuyTim_TongHop` có 5 phiên bản (04/08 · 05/08 · 11/08 · 09/09 · 14/09) cùng được rà.

**Nguyên nhân.** `tools/dat_canh_chung_cu_moi.py` gom mục `apply` từ MỌI `WebDashboard_*.html`. Mục bác sĩ đã HẠ khỏi `apply`
ở bản mới (ITEM-06 mạch máu não 18/10, ITEM-06 Thận 21/10) vẫn bị đếm vì bản cũ còn ghi `apply`.

**Vá.** `chi_ban_moi_nhat()` — chỉ rà bản mới nhất của mỗi lát cắt, dùng lại CHÍNH `dang_ky_chu_de.tach_ten` (cùng lát cắt,
ngày mới hơn ⇒ thay bản cũ; lát cắt khác cùng chủ đề gốc là BỔ SUNG nên giữ cả hai). Bản tin không có phần chủ đề
(Uptodate, CapNhatTuan…) không thay nhau nên giữ đủ; tên không tách được ⇒ giữ. Nạp `tach_ten` riêng, không qua `_nap`.

**Kiểm.** `tools/test_dat_canh_chung_cu_moi_ban_moi_20261024.py` 5 ca; test đặt-cạnh/sổ đã xét cũ vẫn xanh (20 ca). Đột biến:
lấy bản CŨ nhất ⇒ 2 ca đỏ; bỏ ngoại lệ bản tin không chủ đề ⇒ 1 ca đỏ; phục hồi ⇒ xanh.

**Đo thật 24/10 (đính chính giả thuyết).** Lượt chạy bản sửa: rà 65/91 dashboard (bỏ 26 bản bị thay) nhưng VẪN 155 PMID
`apply` như bản 18/10 — các bản bị thay hôm nay không mang PMID `apply` riêng (đếm theo PMID đã khử trùng), nên E-MOI KHÔNG
giảm vì bản sửa: 79 → 80 do một nguồn tổng hợp mới sau 18/10. Giả thuyết «79 bị thổi phồng bởi bản cũ» là SAI về độ lớn;
bản sửa vẫn giữ vì chặn đúng ca mục bị HẠ ở bản mới mà bản cũ còn `apply`. 80 mục còn lại cần bác sĩ so (nhóm A/B).

**Không làm.** Không đóng mục nào thay bác sĩ (sổ `vuot-qua-da-xet.json` chỉ ghi lời bác sĩ); không phán chiều.
