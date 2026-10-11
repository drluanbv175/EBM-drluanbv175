# 11/10/2026 — Bước gom bản truy cập mở DỪNG SỚM khi NCBI chặn, bỏ luôn tầng Unpaywall

## Đo được
- Lượt toàn văn mọi trích dẫn cho 63 chủ đề: 49 bài «có bản truy cập mở (PMC…) mà chưa gom». Phiếu ghi bước ① mã 2:
  «🔴 HẠ TẦNG: elink không trả lời (JSONDecodeError)». NCBI chặn IP ⇒ elink trả trang HTML ⇒ JSONDecodeError ⇒
  `gom_toan_van_dashboard.main` `return 2` NGAY — tầng Unpaywall nằm sau nên KHÔNG chạy cho chủ đề nào.
- Rủi ro kèm: `gom_toan_van_oa.tai_toan_van` nhận mọi phản hồi có «<body» — trang chặn NCBI cũng có «<body» ⇒ nếu elink chạy
  mà efetch bị chặn, trang chặn sẽ được lưu làm «toàn văn XML». Đo kho: 0 tệp XML là HTML (chưa xảy ra, vì elink chết trước).

## Vá (`tools/gom_toan_van_dashboard.py`)
- elink hỏng ⇒ `lien_ket_pmc_epmc` đổi PMID→PMCID qua Europe PMC (kèm cờ `isOpenAccess`).
- `tai_jats`: NCBI efetch trước; NCBI chặn/lỗi/trả HTML ⇒ Europe PMC `rest/PMC…/fullTextXML` (đo: JATS đầy đủ cho bài OA,
  HTTP 500 cho bài không OA). `la_jats_toan_van` loại trang HTML/trang chặn (cần «<article» + «<body», không «<html»).
- Europe PMC nói «không OA»/không có bản ghi ⇒ KHÔNG ghi sổ «không lấy được» 30 ngày (NCBI có thể có bản thảo tác giả khi
  hết chặn). Cả hai nguồn chết ⇒ tầng Unpaywall VẪN chạy, cuối lượt trả mã 2 (không kết luận độ phủ).
- Kiểm: `tools/test_gom_pmc_du_phong_europepmc_20261011.py` 11 ca; 8/8 phép đột biến đỏ đúng chỗ (một phép sống sót lần đầu
  vì fixture HTML thiếu thẻ `<article>` — sửa fixture thành trang HTML5 có `<article>`, đúng dạng trang NXB thật).
