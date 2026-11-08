# 08/11/2026 — Dựng lại 159 bản tóm tắt Word ★ theo bố cục «Áp dụng nhanh» + nhãn rút bài cho đính chính đã ký

**Yêu cầu bác sĩ (nguyên văn):** «Dựng lại để có bản tóm tắt tốt nhất» — sau `2026-11-08-tom-tat-word-ap-dung-nhanh.md`.

**Làm gì (chạy một lần, không phải công cụ thường trực):** với mỗi Word đã có trong `EndNote/TomTatChungCu/` mà bản ghi đạt ★
theo ngữ cảnh dashboard HIỆN HÀNH: sao lưu Word/PDF/`ngu_canh.json` cũ vào `~/.ebm-endnote-sao-luu/tomtat-truoc-dung-lai-20261108/`,
làm mới `ngu_canh_dashboard` + `tang_uu_tien` trong `ngu_canh.json` (không đụng `tom_tat.json`/`kiem_cheo.json` — kiểm chéo khoá băm
của `tom_tat.json`), rồi `dung` (tra rút bài LẠI, chạy lại MỌI cổng kể cả luật mới, đòi băm kiểm chéo khớp). Không ghi EndNote:
tệp giữ nguyên tên nên liên kết PDF cũ vẫn trỏ đúng.

**Số đo:** 282 Word · 121 không ★ (để nguyên) · 2 không còn bản ghi có PDF · 159 dựng lại, 159 đạt (0 lỗi cổng, 0 lỗi kiểm chéo,
0 bài rút, 0 «chưa kiểm rút bài»); cả 159 có mục 2 «Áp dụng nhanh tại phòng khám» + ô nguồn khuyến cáo; dòng rút bài: 156 «không
thấy thông báo rút», 2 «chỉ Retraction Watch» (bài không PMID), 1 đính chính đã ký (dưới). CIBIS-II (PMID 10023943): bản cũ ghi
«RÚT BÀI: CHƯA KIỂM ĐƯỢC», bản mới «không thấy thông báo rút».

**Bẫy gặp khi dựng:**
- **PDF toàn văn đổi mã băm so với lúc tóm tắt (23 bản):** 22 là bản «in từ kho toàn văn EBM» (dựng từ XML PMC) được in lại hàng
  loạt ~26/10 — chỉ khác dòng dấu trang 1 và chú thích tác giả nối cuối bài; các trang giữa giống ≥ 99,9% ⇒ cùng bài, số trang trích
  dẫn không lệch ⇒ vẫn dựng. Quy tắc dùng: trang giữa trùng hoặc giống ≥ 0,999, số trang bằng hoặc +1.
- **PMID-36328476 (EULAR 2022):** EndNote gắn bản tác giả HAL (bản quét ảnh, không trích được chữ, 62 MB); gói đọc được dựng có chủ
  ý từ bản tạp chí `toan_van_oa/PMID-36328476_CHR.pdf` (quy ước «PDF quét ảnh ⇒ dựng gói từ bản _CHR»). Mã băm gói = mã băm _CHR ⇒
  dựng riêng, đúng bài. So mã băm với PDF EndNote là SAI chỗ đo cho loại bản ghi này — phải so với tệp `pdf.tep` của gói.
- **PMID-41110921 (CCS/CHFS 2025):** đầu trang Word hiện «RÚT BÀI: —» màu ĐỎ vì bảng nhãn đầu trang thiếu khoá
  `dinh_chinh_bi_rut_da_ky` (bảng chi tiết bên dưới ghi đúng «bài gốc không bị rút — bác sĩ đã ký xem xét»). Vá: `NHAN_RUT_BAI_NGAN` +
  `MAU_RUT_BAI` dùng chung cho đầu trang và dòng «Rút bài» của bảng; trạng thái lạ vẫn «—» đỏ (fail-closed).
- Dựng từ worktree (không có `EBM-Dashboards` anh em) ⇒ tra rút bài của bản đính chính đã ký trả «CHƯA KIỂM ĐƯỢC» vì không thấy sổ ký
  `rut-bai-da-xem-xet.json` — đúng hành vi fail-closed; dựng lại phải chạy từ cây có dữ liệu (đã dựng lại bản này từ cây chính).

**Kiểm (vá nhãn):** `tools/test_tom_tat_ap_dung_nhanh_20261108.py` thêm 5 ca (mỗi trạng thái một nhãn + màu); đột biến 2/2 đỏ (bỏ
nhãn · bỏ màu của trạng thái đính chính đã ký). Bộ test tóm tắt Word 269 đạt.
