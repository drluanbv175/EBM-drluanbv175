# 28/10/2026 — Cổng số của tóm tắt ⑨ chặn số thập phân đúng vì PDF tách «7 .9»

**Đo (lô ⑨ 40 bài, 28/10):** pypdf tách số thập phân ở bài Lancet/NEJM: «7 .9%», «11 ·1», «1 ·01», «2·⏎12». Cổng `kiem` so số của
tóm tắt với số trong văn bản trang nên báo «không có trong bài» cho số ĐÚNG; người soạn phải viết lách thành «7 phẩy 9%» (PMID
42670293) hoặc đổi sang số nhánh/tử–mẫu (PMID 42669300) — Word in ra kém chính xác hơn bài.

**Vá:** `_chuan_so` ghép lại hai dạng tách chắc chắn là số thập phân: dấu chấm có dấu cách ĐỨNG TRƯỚC (câu văn không đặt dấu cách
trước dấu chấm) và chấm giữa «·»/«⋅» có khoảng trắng hai bên. KHÔNG ghép «3. 12» hay «7.⏎9» (chấm cuối câu rồi số mới).

**Kiểm:** `test_so_thap_phan_bi_pdf_tach_van_khop` (5 khẳng định, có hai ca không được ghép); 3 đột biến (bỏ luật chấm, bỏ khoảng trắng
quanh «·», ghép mọi khoảng trắng giữa hai số) đều đỏ; bộ test tóm tắt 47 đạt.
