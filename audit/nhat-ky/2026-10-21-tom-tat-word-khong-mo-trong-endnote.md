# 21/10/2026 — Tóm tắt chứng cứ dạng Word không mở trực tiếp được trong EndNote

**Hiện tượng (bác sĩ báo):** 14 bản tóm tắt chứng cứ Word (`OneDrive/EndNote/TomTatChungCu/*.docx`) gắn vào bản ghi EndNote
dạng liên kết (`file_res.file_type` 2) — EndNote không hiển thị Word trong khung đọc như PDF toàn văn (`file_type` 1,
`internal-pdf://`), bác sĩ phải mở bằng ứng dụng khác.

**Gốc:** công cụ `tom_tat_chung_cu_word.py` (19/10) chỉ xuất Word. Gắn `internal-pdf://` qua AppleScript vào bản ghi ĐÃ có tệp
từng trả «missing value» (đo 19/10 trên bản sao) ⇒ không đi đường đính nội bộ.

**Sửa:** `dung` dựng thêm PDF giữ màu cùng tên bằng `docx_sang_pdf_giu_mau.py` (cùng công cụ bước ⑤ bộ năm); `--gan-endnote`
gắn PDF (liên kết) THAY liên kết Word, giữ PDF toàn văn; đọc lại thiếu tệp được giữ ⇒ ghi trả nguyên trạng. `pdf-hoa
[--ap-dung]` chuyển mọi bản Word đã có. Tệp Word giữ trong thư mục để sửa. Test `tools/test_tom_tat_pdf_endnote_20261021.py`
(11 ca) + 5 đột biến đều bị bắt.
