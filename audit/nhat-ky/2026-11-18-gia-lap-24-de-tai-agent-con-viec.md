# 18/11/2026 — Đo 24 đề tài giả lập: 112 lượt «agent còn việc» phần lớn do luật lệch nhau, không do đề tài thiếu

**Bối cảnh:** bác sĩ «Hãy đo và thực hiện trên tất cả các đề tài giả lập để hoàn thiện đề tài một cách tốt nhất».
24 kịch bản (16 khung + 8 chân thực) đều khoá được G10, 0 ô lỗi máy; nhưng `hoi_dong_cong.py trach-nhiem` báo 112 lượt
«agent còn việc» (đo 18/11).

## Nguyên nhân — 5 nguồn, đều KHÔNG phải đề tài thiếu
- G3-T2 xét biến định danh chỉ theo TÊN, trong khi G5-AUTO-02 đã bỏ qua trường phân loại từ 17/11 (`tc_dien_thoai`
  Có/Không) ⇒ báo «G5 sẽ chặn» mà G5 không chặn (1 lượt). Bài học: hai nơi soi CÙNG luật phải dùng CÙNG hàm/điều kiện.
- G6-AUTO-02/03: đề tài định tính khai seed/alpha «không áp dụng» treo «cần xem» vĩnh viễn — không có chỗ ghi xác nhận
  (4 lượt). Nay ĐẠT khi đo được thiết kế định tính + script không bước ngẫu nhiên/kiểm định.
- 6 kịch bản thêm ghi min/max rỗng cho mọi trường số ⇒ G3-T3 (9 lượt).
- Bộ giả lập ghi `G9_REPORTING_CHECKLIST_…`, hội đồng đòi `REPORTING_CHECKLIST_<mã>.md` (24 lượt).
- Tổng quan gộp thiếu `06_phan_tich_R/study_level_extraction.csv` (G5-T2, 2 lượt).

## Kết quả (PR y khoa #323)
112 → 72 lượt; còn đúng G0-T3 (tổng hợp bằng chứng), G0-T4 (khoảng trống), G10-T3 (sổ trạng thái) — tài liệu agent tự
viết mà bộ giả lập chưa mô phỏng. 37 test mới, 15/15 đột biến đỏ (3 sống sót lượt đầu do phép thử hở: bộ sinh tự ép
giá trị vào khoảng ⇒ phép «nằm trong khoảng» hiển nhiên đúng — thêm phép «có khoảng và không khoảng ra cùng dữ liệu»).

**Luật rút ra:** phép thử «giá trị nằm trong khoảng» vô nghĩa nếu bộ sinh tự kẹp vào khoảng — phải kiểm KHÔNG BỊ KẸP.
