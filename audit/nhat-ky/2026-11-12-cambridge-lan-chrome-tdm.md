# 12/11/2026 — Cambridge vào làn Chrome lưu bản sao qua bảng riêng `TDM_CHO_PHEP_LUU`

**Lệnh của bác sĩ (chat, 12/11/2026, nguyên văn):** «Thêm Cambridge vào làn Chrome».

## Vì sao phải có bảng thứ ba

Tới 11/11 phiên lưu bản sao (`tools/phien_uy_quyen_chrome.py`) chỉ nhận NXB nằm trong `DIEU_KHOAN_NXB` **và** có uỷ quyền đọc
của bác sĩ. Bảng đó cố ý chỉ nhận mục «cấm» (một mục khác «cấm» sẽ miễn khai `dieu_khoan` cho mọi bài ở `--nap`). Cambridge
không «cấm»: Terms of use của Cambridge Core («Last Updated: March 2025», mục «Machine Analysis (Text and Data Mining)», đọc trên
Chrome của bác sĩ 12/11/2026) cho phép tải, lưu, đánh chỉ mục nội dung truy cập hợp pháp để TDM phi thương mại. Nhét Cambridge
vào bảng «cấm» sẽ làm sai cả hai trục: đổi ngữ nghĩa bảng và bắt bác sĩ uỷ quyền cho một việc NXB đã cho phép.

Cách làm: bảng RIÊNG `TDM_CHO_PHEP_LUU` (`tools/doc_toan_van_co_nguoi.py`), CHỈ phiên lưu bản sao đọc. NXB trong bảng vào phạm vi
phiên mà không cần `--ghi-uy-quyen`; trang phải nằm trên miền của chính NXB (bản ở PMC, kho trường đại học… không hưởng, kể cả
khi miền đó có trong cấu hình làn Chrome); `nxb_cua` và `--nap` không đổi. Mục ghi đủ điều kiện của điều khoản (phi thương mại ·
truy cập hợp pháp · kèm liên kết bài gốc · xoá bản lưu khi dự án kết thúc · NXB có quyền giới hạn việc tải).

## Số đo DOM (12/11/2026, Chrome của bác sĩ, KHÔNG lưu tệp, KHÔNG bấm nút)

- Có quyền (đều là bài OA): PMID 42112625 (BJP) — `.abstract-content` 2.234 + `.content-box` 37.661 ký tự; PMID 42765379
  (Psychol Med) — 1.971 + 32.793. Meta `citation_pdf_url` cùng nguồn trả `%PDF-` (yêu cầu Range 8 byte).
- Không quyền: PMID 33952359 và 42169209 — URL chuyển về `/article/abs/…`, đề mục «Access options», `.content-box` rỗng.
  Bác sĩ chưa có quyền thuê bao Cambridge ⇒ thực tế chỉ lưu được bài OA.
- **Bẫy đã tránh:** nếu thêm `#references-list` vào vùng thân bài (như cấu hình ScienceDirect), bài KHÔNG quyền vẫn có vùng
  21.948 ký tự (danh mục tham khảo 20.325) ⇒ vượt `min` 12.000, chỉ còn khoá đề mục/URL chặn. Vùng chỉ lấy tóm tắt + thân bài.
- Khoá: dấu URL `/article/abs/` (thêm vào `dau_khong_quyen_url`) · `min` · đề mục «Access options» (khớp nguyên đề mục — cụm
  «access options» có thể nằm trong thân bài y tế) · cụm từ riêng `\bArticle purchase\b` (bài học PR #320). Mỗi lớp tự chặn
  được bài 33952359 khi thử riêng bằng `__ebmDanhGia`.

## Kiểm hồi quy

`tools/test_lan_chrome_cambridge_20261112.py` (29 test). Đột biến 8/8 đỏ đúng chỗ rồi xanh lại: bỏ tiền tố `10.1192/` · bỏ miền ·
bỏ Cambridge khỏi `nxb_duoc_luu` · khoá trần «Purchase» · bỏ dấu URL · thêm `#references-list` · nới miền TDM sang miền nền tảng ·
bỏ nhánh TDM của `lech_doctrine`. Doctrine `_CONNECTOR-CHUNG-CU.md` §2septies sửa câu Cambridge, `lech_doctrine` nay so cả bảng
TDM (tên + tiền tố + tên bảng).

Việc còn lại: sau khi gộp, chạy hai bài OA (42112625, 42765379) qua `lan_chrome.py toan-van` trong phiên có lời bác sĩ để kiểm
nhánh lưu, PDF nhúng và cổng nội dung `--nhan`, rồi sửa `kiem_lan_cuoi`. Cần bác sĩ kiểm chứng.
