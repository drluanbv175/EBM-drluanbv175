# 04/11/2026 — Bản tóm tắt chứng cứ tiếng Việt (Word/PDF ⑨): trình bày và thuật ngữ chưa chuẩn

**Bác sĩ:** «Với các bản tóm tắt toàn văn bằng tiếng việt chưa thực sự chuẩn xác cả về trình bày và ngữ nghĩa; Hãy kiểm tra và
hoàn thiện lại».

**Đo (282 bản trong `EndNote/TomTatChungCu`, xem PDF từng trang bằng PDFKit):**
- PDF — bản bác sĩ mở trong EndNote — dựng qua pandoc: pandoc BỎ màu chữ (cảnh báo đỏ `[!…!]`, lợi ích xanh `[+…+]`), cỡ chữ và
  căn lề; coi dòng duy nhất của ô «ĐIỂM NHẤN» (bảng 1×1) là dòng tiêu đề ⇒ cả khối in đậm, căn giữa. CSS in `tr {
  page-break-inside: avoid }` đẩy khối dài sang trang sau ⇒ trang 1 gần như trống (mẫu PMID 42670293: 16 trang).
- «THIẾT KẾ» và «RÚT BÀI» dính một dòng; ngày tra rút bài in dạng máy «2026-10-29T04:36:53».
- Bảng kết quả 9 cột, cột «Kết cục» 4,1 cm: ô bị bẻ 6–7 dòng.
- Chữ: 32.436 số thập phân dấu chấm («HR 0.80») trong khi mọi sản phẩm khác của hệ viết «0,80»; 656 số nghìn kiểu Anh
  («13,454 người»); 1.423 nhãn «Nhận định thẩm định» / «Nhận định của người soạn» cho cùng một ý; 219 chỗ «lực mạnh/yếu, lực
  khuyến cáo»; 24 chỗ «95% CI» lẫn với «KTC 95%»; «Tường thuật …» làm chủ ngữ đầu câu.

**Vá — chỉ ở bước DỰNG, `tom_tat.json` (đã qua cổng số + kiểm chéo độc lập) không đổi:**
- `docx_sang_html_khong_pandoc.py`: giữ căn lề, màu chữ, cỡ chữ riêng; bảng một dòng = ô hộp (`class="hop"`, không `<th>`);
  bảng nhiều dòng có `<thead>`.
- `docx_sang_pdf_giu_mau.py`: cờ `--khong-pandoc`; CSS cho ô hộp ngắt được giữa trang, chữ thường căn trái.
- `tom_tat_chung_cu_word.py`: `dung_pdf` dùng `--khong-pandoc`; `trinh_bay_vi()` áp cho mọi chữ in ra — thập phân dấu phẩy,
  nghìn dấu chấm, giữ số hiệu (khuyến cáo/mục/bảng/phân tích 1.1 và số nối tiếp «7.1 và 7.2», R 2.1, phiên bản phần mềm), DOI/URL
  và trích nguyên văn «…»; thống nhất «Nhận định của người tóm tắt», «độ mạnh khuyến cáo / khuyến cáo mạnh», «KTC 95%», thêm lời
  giải tiếng Việt cho nhãn gốc «Quality of evidence: …» (nhãn phân hạng GỐC của nguồn giữ nguyên). Bảng kết quả 8 cột (gộp
  «Hiệu ứng (KTC 95%)»); hai dòng đầu trang riêng; ngày dd/mm/yyyy; bảng khuyến cáo rộng cột «Mức chứng cứ».
- Bẫy gặp khi làm: biểu thức số mới đặt tên `_SO` trùng biểu thức của CỔNG kiểm số ⇒ cổng hỏng; 26 test cũ bắt được ngay, đổi tên
  `_SO_VI`.

**Kiểm:** bất biến trên toàn kho (72.677 trường): dãy chữ số sau chuẩn hoá giống hệt bản gốc (0 vi phạm). Test
`tools/test_tom_tat_trinh_bay_vi_20261104.py` 26 ca; 12 đột biến đều đỏ. Bộ test tóm tắt cũ 219 xanh (một test khoá «4.7 điểm %
†» đổi sang «4,7» theo quy ước mới). Mẫu PMID 42670293: 16 → 12 trang, trang 1 có nội dung, màu điểm nhấn hiện lại.

**Chưa làm (cần bác sĩ quyết vì tốn token):** biên tập lại CÂU CHỮ dịch sát (vd «… đi kèm tử vong thấp hơn», «p danh nghĩa»)
cần mô hình đọc lại từng bản và một bước đối chiếu nghĩa độc lập, kiểm chéo cũ gắn băm JSON nên không tái dùng được.
