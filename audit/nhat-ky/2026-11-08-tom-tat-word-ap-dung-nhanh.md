# 08/11/2026 — Tóm tắt Word ⑨: mục «Áp dụng nhanh tại phòng khám» đứng ngay sau kết luận

**Yêu cầu bác sĩ (nguyên văn):** «Tóm tắt tiếng việt đảm bảo đúng chuẩn,chính xác nhất và giúp áp dụng nhanh cho thực hành lâm
sàng». Nối tiếp `2026-11-08-hang-cho-tom-tat-word-chi-sao.md` (hàng chờ chỉ ★).

**Vì sao:** phần áp dụng (Nên làm · Không nên · Điều kiện · Theo dõi) nằm ở mục 10/11 — sau thông tin trích dẫn, PICO, phương
pháp, kết quả, tác hại, RoB, GRADE, khả năng áp dụng. Bác sĩ cần áp dụng nhanh phải lật qua 6–8 trang mới tới. Bản tóm tắt cũng
không nói bài đang đỡ khuyến cáo nào của hệ thống.

**Vá:** `tools/tom_tat_chung_cu_word.py`
- `dung_word`: mục 2 «Áp dụng nhanh tại phòng khám» ngay sau «Kết luận cho thực hành»; mục áp dụng cũ ở cuối bỏ (vẫn 11 mục,
  không in hai lần).
- `vi_tri_khuyen_cao()`: ô «BÀI LÀ NGUỒN CỦA KHUYẾN CÁO TRÊN DASHBOARD» — chỉ ngữ cảnh vai «muc» của phiên bản HIỆN HÀNH, bản mới
  nhất trước, khử trùng, tối đa 3 dòng; ghi quyết định (ÁP DỤNG/CÂN NHẮC…) và mức chứng cứ CỦA DASHBOARD — trục quyết định, tách
  khỏi GRADE máy ở mục GRADE. Lưu ý cuối văn bản ghi rõ đây là trạng thái ứng viên của dashboard, không phải phê duyệt.
- `la_sao()` + cổng `kiem_tom_tat`: bài ★ (cùng luật tag `gan_tag_endnote.dat_ap_dung_tin_cay`) thiếu CẢ `goi_y_ap_dung.dieu_kien`
  lẫn `theo_doi` ⇒ chặn — phần áp dụng nhanh phải đủ để làm ngay.
- `HUONG_DAN_DOC` luật 11: `nen_lam` mở bằng hành động chính; điều kiện/chống chỉ định đúng như bài; theo dõi có chỉ số + thời
  điểm; bài không đỡ đúng chiều/quần thể khuyến cáo dashboard ⇒ ghi `can_xac_nhan`, không viết lệch bài cho khớp dashboard.
- Độ chính xác giữ nguyên các lớp đã có: số phải có nguyên văn trên trang khai, kiểm chéo độc lập 0 sai mới ra Word.

**Số đo 08/11:** 163/163 gói tóm tắt ★ trong `~/.ebm-cache/tom-tat-chung-cu/` đã có điều kiện hoặc theo dõi ⇒ cổng mới không chặn
ngược bản nào. Bản mẫu CIBIS-II (PMID 10023943) dựng lại vào thư mục tạm: 12 trang như bản đang dùng, mục 2 bắt đầu ở trang 1.
Bẫy đo: chuyển PDF bằng `docx_sang_pdf_giu_mau.py` KHÔNG kèm `--khong-pandoc` cho bản căn giữa, mất màu, 16 trang — dây chuyền thật
(`dung_pdf` trong tom_tat_chung_cu_word) luôn dùng `--khong-pandoc`; so bản mẫu phải dùng đúng cờ đó.

**Kiểm:** `tools/test_tom_tat_ap_dung_nhanh_20261108.py` (12 ca). Đột biến 9/9 đỏ: bỏ cổng bài ★ · cổng áp cả bài không ★ · luật ★
bản sao riêng · vị trí lấy cả bản cũ · xếp cũ trước · không khử trùng · tiêu đề về cũ · bỏ luật 11 · không in ô nguồn khuyến cáo.
Bộ test tóm tắt Word cũ 252 đạt.
