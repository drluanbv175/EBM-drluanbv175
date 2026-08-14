# Mô-đun 1 — Tìm & thu thập y văn

Gộp từ: biomedical-search-strategy-builder, multi-database-literature-collector,
high-value-paper-screener, clinical-question-clarifier.

## 1. Làm rõ câu hỏi → PICO/PECO
- P (dân số), I/E (can thiệp/phơi nhiễm), C (so sánh), O (kết cục), + thiết kế mong muốn, mốc thời gian.
- Nếu thiếu yếu tố → hỏi lại 1 câu trước khi xây chiến lược.

## 2. Xây chuỗi tìm kiếm (search strategy)
- Mỗi khái niệm PICO = 1 khối; trong khối nối bằng `OR`, giữa khối nối bằng `AND`.
- Kết hợp **MeSH** + **từ khóa tự do** (title/abstract). Ví dụ PubMed:
  `("atrial fibrillation"[MeSH] OR "atrial fibrillation"[tiab]) AND (anticoagul*[tiab])`
- Bộ lọc hợp lý: loại thiết kế (RCT/SR), năm, ngôn ngữ, người lớn/trẻ em. **Ghi lại** mọi bộ lọc.
- Tránh thu hẹp quá sớm; chạy thử, xem số hit, tinh chỉnh.

## 3. Thu thập đa CSDL (miễn phí)
- PubMed (E-utilities), Europe PMC/PMC (toàn văn), Crossref (DOI/metadata), OpenAlex,
  Semantic Scholar, Unpaywall (bản open-access). bioRxiv/medRxiv cho preprint (đánh dấu CHƯA bình duyệt).
- Dùng `scripts/pubmed_search.py` để lấy PMID + metadata. Hợp nhất, **loại trùng** theo DOI > PMID > tiêu đề.
- Ghi rõ: ngày truy vấn, CSDL, chuỗi tìm, số kết quả (phục vụ PRISMA flow).

## 4. Sàng lọc bài giá trị cao
- Ưu tiên: guideline > SR/meta-analysis > RCT > cohort > case-control > case series.
- Tín hiệu chất lượng: đa trung tâm, cỡ mẫu lớn, kết cục lâm sàng cứng (tử vong/biến cố) thay vì surrogate,
  đăng ký trước, có GRADE. Cảnh báo: preprint, tạp chí săn mồi, COI nặng.
- Xuất bảng: [PMID/DOI] · tiêu đề · thiết kế · n · kết cục chính · mức ưu tiên · ghi chú.

## Đầu ra
Chuỗi tìm kiếm tái lập + bảng bài đã sàng (kèm PMID/DOI) + PRISMA-style counts.
⚠️ Cần bác sĩ kiểm chứng.
