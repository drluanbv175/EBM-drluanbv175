# 19/11/2026 — Bộ đối chiếu xuyên cổng suy «đã kiểm rút bài» từ câu văn của G0-T3

**Bối cảnh.** Đây là việc mở số 2 trong nhật ký `2026-11-19-g7-hat-giong-bo-qua-sang-loc-g0.md`. Bác sĩ duyệt sửa ngày 19/11/2026 («việc 2 sửa»).

**Lỗ.** Trục `trich_dan_tong_quan` của `nhat_quan_xuyen_cong` báo «mục TLTK chưa có bản ghi kiểm rút bài» với PMID/DOI chưa được kiểm. Một trong các nguồn «đã kiểm» của nó là khoá `rut_bai` trong `G0_TONG_HOP_BANG_CHUNG_<mã>.json`, mà khoá này là CÂU VĂN tự do. `_da_kiem_rut_bai` coi mọi dãy 7–8 chữ số trong đó là «PMID đã kiểm», nên:
- câu «PMID x chưa kiểm được» cũng làm x thành đã kiểm. Mục TLTK trích x không bị báo, tức báo xanh giả đúng ở chỗ an toàn, trái luật «không tra được ⇒ chưa kiểm»;
- C1a bị đọc nhầm khoá ngày viết liền «ngay_bo_sung_20261017» thành PMID 20261017.

**Đo trên đề tài thật trước khi sửa.**
- C1a: 9 PMID và 4 DOI được nêu trong `rut_bai`, tất cả đều ở câu «kiểm OK», nên không có sai thật, chỉ có mã rác 20261017.
- BTM: không nêu mã nào.

**Cách vá** (repo y khoa):
- `g0_tong_hop.ma_da_kiem_rut_bai()` đọc danh sách có cấu trúc `rut_bai.pmid_da_kiem` (bắt buộc, được để rỗng) và `rut_bai.doi_da_kiem` (tuỳ chọn).
- `kiem_tong_hop` kiểm đúng dạng và không trùng mã.
- `_da_kiem_rut_bai` chỉ đọc hai danh sách này, không đọc câu văn nữa.
- Bộ giả lập ghi `pmid_da_kiem` gồm đúng các PMID có kết quả trong kho A12.
- Hướng dẫn agent `tong-quan-y-van` được cập nhật.
- Dữ liệu (PR riêng): C1a được điền đúng 9 PMID và 4 DOI mà câu văn đã ghi OK; BTM được điền danh sách rỗng, vì câu văn không nêu mã nào. Không thêm mã nào khác.

**Kiểm.**
- `tests/test_rut_bai_g0_co_cau_truc_20261119.py`: 7 ca.
- Kiểm đột biến 9/9 đỏ đúng chỗ.
- Trên bản sao hồ sơ thật:
  - C1a: số định danh đã kiểm từ 79 xuống 78 (chỉ mất mã rác 20261017);
  - BTM: không đổi;
  - G10 của cả hai vẫn PASS, không có cảnh báo mới.

**Còn để ý, chưa sửa.** Báo cáo `A12_CITATION_VERIFICATION_<mã>.md` cũng được đọc bằng `danh_muc_trich_dan.dinh_danh`. Mọi «PMID x» trong báo cáo, kể cả ở bảng đối chiếu nội dung, đều tính là đã kiểm rút bài. Đây là cùng họ lỗi nhưng rủi ro thấp hơn, vì biên nhận máy `A12_RETRACTION_RECEIPT.json` là nguồn song song. Việc sửa chờ bác sĩ quyết.
