# Tra cứu chứng cứ tại điểm khám

*Đọc file này khi ca đang tư vấn đặt ra câu hỏi kiểu: "chứng cứ mới nhất về…", "guideline nói gì về…", "thuốc/test này hiệu quả không, độ chính xác thế nào", hoặc ở bước Tìm (bước 2/5 khung EBM tại phòng khám) khi cần biến MỘT câu hỏi lâm sàng (PICO) thành câu trả lời ngắn gọn, CÓ TRÍCH DẪN (PMID/DOI), đáng tin. Đây KHÔNG phải bước thẩm định phê bình sâu (GRADE/NNT chính thức) và KHÔNG phải bước tổng quan y văn đầy đủ (recall cao) — chỉ là tra cứu nhanh, chính xác cho một thắc mắc cụ thể.*

## Mục tiêu

Trả lời nhanh, có trích dẫn, đáng tin cho MỘT câu hỏi lâm sàng tại điểm khám. Thứ tự tra cứu: RAG kho nội bộ → nguồn CHÍNH THỐNG (guideline hiệp hội/Cochrane/HTA) → PubMed/Europe PMC làm lớp ĐỐI CHIẾU + lấy định danh (PMID/DOI). Mục tiêu tỷ lệ trích dẫn ảo = 0%.

## Nguyên tắc bất biến

KHÔNG bịa nguồn/số liệu · mỗi ý kèm PMID/DOI · thiếu connector/nguồn → đánh dấu **PARTIAL**, KHÔNG kết luận "không có chứng cứ" · KHÔNG lưu/đưa thông tin định danh bệnh nhân (PII) · an toàn người bệnh trước · kết thúc bằng "Cần bác sĩ kiểm chứng."

## Đầu vào tối thiểu

Câu hỏi lâm sàng (thô hoặc đã ở dạng PICO) · dân số/bối cảnh (tuổi, bệnh nền nếu liên quan) · điều muốn biết (hiệu quả điều trị / độ chính xác test / tiên lượng / tác hại). Thiếu → tự tách khung PICO và nêu lại 1 dòng, vẫn chạy tiếp (không dừng lại hỏi vặt).

Trước khi tra cứu: kiểm nhanh xem các công cụ tra cứu (RAG nội bộ, PubMed/Europe PMC) có hoạt động không — thiếu/lỗi thì tra cứu vẫn chạy nhưng gắn cờ **PARTIAL** ở phần kết quả. Nếu câu hỏi gắn với một ca đang cấp cứu, tra cứu KHÔNG được làm chậm việc xử trí an toàn khẩn cấp (việc đó thuộc bước an toàn riêng, đã xử lý trước khi vào phần này).

## Tổng quan quy trình

| Bước | Tác vụ |
|---|---|
| 1 | Chuẩn hóa câu hỏi thô → PICO 1 dòng |
| 2 | RAG kho nội bộ (ưu tiên) → nguồn **CHÍNH THỐNG** (Cochrane/HTA + guideline hiệp hội chuyên khoa + 🇻🇳 kcb.vn/phác đồ cho câu hỏi liên quan Việt Nam) |
| 3 | **PubMed/Europe PMC = lớp ĐỐI CHIẾU + lấy PMID/DOI** cho chứng cứ Cấp 0/0.5; tìm sơ cấp CHỈ khi nguồn chính thống không phủ; ClinicalTrials.gov nếu là câu hỏi điều trị (ghi rõ status) |
| 4 | Lọc & xếp hạng theo độ mới + thứ bậc chứng cứ (guideline/Cochrane → SR → RCT → cohort) |
| 5 | **Corrective self-RAG bắt buộc**: đúng PICO? surrogate? retracted? mâu thuẫn nguồn bậc cao? → LOẠI + ghi lý do |
| 6 | Soạn câu trả lời: chỉ dùng PMID/DOI đã xác minh; trích dẫn từ trí nhớ chưa phân giải → gắn `[CẦN KIỂM CHỨNG]` |

## Quy trình chi tiết

### Bước 1 — Chuẩn hóa PICO
Câu hỏi thô → tự tách P (dân số) – I (can thiệp) – C (đối chứng) – O (kết cục), nêu lại 1 dòng trước khi tra cứu.

### Bước 2 — Tra theo thứ tự nguồn
(a) **RAG nội bộ đã curate** — kho chứng cứ đã tuyển chọn của bác sĩ (thư mục `medical-ebm-automation/evidence/` nếu có quyền truy cập) là nguồn đáng tin nhất, tra trước tiên.

(b) **Nguồn CHÍNH THỐNG (Cấp 0):** Cochrane (cochranelibrary.com) hoặc Epistemonikos + guideline **hiệp hội chuyên khoa** (ESC/ACC-AHA/ADA/KDIGO/GOLD/GINA/IDSA/EULAR-ACR…). Lưu ý về Cochrane tại Việt Nam: **KHÔNG** miễn phí toàn bộ (Việt Nam thuộc Research4Life Group B, phí ~1.500 USD/năm/cơ sở, không có diện miễn phí quốc gia); phần **luôn miễn phí toàn cầu bất kể quốc gia** là: review đã xuất bản >12 tháng, protocol, và tóm tắt ngôn ngữ đơn giản (Plain Language Summary) — chỉ ~85% nội dung. 🇻🇳 Với câu hỏi liên quan thực hành tại Việt Nam, ưu tiên đối chiếu thêm kcb.vn/phác đồ Bộ Y tế.

(c) **Tạp chí đỉnh (Cấp 0.5):** NEJM/Lancet/JAMA/BMJ/Annals of Internal Medicine… cho toàn văn khi cần chi tiết hơn guideline. Nhóm (b)+(c) là nơi lấy khuyến cáo/kết luận thực hành.

### Bước 3 — PubMed/Europe PMC = lớp đối chiếu & lấy định danh (KHÔNG phải điểm khởi đầu)
Với chứng cứ đã tìm ở Bước 2, tra cứu PubMed (ví dụ công cụ `search_articles` → `get_article_metadata`/`convert_article_ids`) để **lấy PMID/DOI** (bất biến cần cho mọi trích dẫn) và **xác nhận trùng khớp** với nguồn chính thống đã dùng; lấy toàn văn qua PMC hoặc Europe PMC khi cần.

**CHỈ tìm PubMed sơ cấp độc lập khi nguồn chính thống ở Bước 2 KHÔNG phủ được câu hỏi** — khi đó ghi rõ đây là khoảng trống chứng cứ chính thống, không phải kết luận vội từ 1 bài lẻ.

Câu hỏi về **điều trị** → tra thêm ClinicalTrials.gov, **luôn ghi rõ `status`** của thử nghiệm; một thử nghiệm **chưa có kết quả công bố KHÔNG được coi là bằng chứng hiệu quả**.

Nguồn dạng "discovery" (ví dụ Consensus) chỉ dùng để tìm hướng tra cứu ban đầu, KHÔNG dùng làm nguồn trích dẫn cuối cùng — vẫn phải lấy PMID/DOI xác minh qua PubMed/Europe PMC.

> **Câu hỏi di truyền/ung thư học đặc hiệu** (biến thể gen/rsID/dbSNP, ý nghĩa lâm sàng biến thể theo ClinVar, đột biến soma ung thư theo COSMIC, liên kết SNP–bệnh theo GWAS Catalog, bệnh gene đơn dòng Mendel theo OMIM, hợp chất hóa học theo PubChem) nằm **ngoài phạm vi** các nguồn tra cứu ở trên — cần công cụ/cơ sở dữ liệu chuyên biệt khác nếu có, không cố suy diễn từ PubMed/guideline thông thường. Câu hỏi về thử nghiệm lâm sàng đang tuyển bệnh hoặc hợp chất/cơ chế dược lý học (ChEMBL) thì vẫn tra như Bước 3 ở trên.

### Bước 4 — Lọc & xếp hạng
Theo độ mới + thứ bậc chứng cứ (guideline/Cochrane → SR/meta-analysis → RCT → cohort). Ở điểm khám ưu tiên **PRECISION** (đúng PICO, trả lời nhanh) hơn là độ phủ đầy đủ (recall) — nếu câu hỏi thực chất là một đề tài cần tổng quan toàn diện, việc đó cần một quy trình tổng quan y văn riêng, không phải tra cứu điểm khám. Loại bỏ mọi nguồn không phân giải được PMID/DOI.

### Bước 5 — Tự sửa (corrective self-RAG), BẮT BUỘC trước khi kết luận
Với mỗi nguồn định dùng, tự chất vấn:
- **Đúng câu hỏi?** Dân số/can thiệp/kết cục của bài có khớp PICO đã tách, hay bị lệch P/I/O?
- **Hiểu đúng bối cảnh?** Kết cục là **lâm sàng cứng** hay chỉ là **dấu ấn thay thế (surrogate)**? Thiết kế là **non-inferiority / cắt ngang / phân tích dưới nhóm** dễ bị đọc nhầm thành "superiority / nhân quả / kết cục chính" không? Bài có bị **rút (retracted)** hoặc đã bị nghiên cứu lớn hơn **bác bỏ** không?
- **Có nguồn bậc cao hơn mâu thuẫn không?** Nếu có → ưu tiên nguồn mạnh/mới hơn + NÊU RÕ mâu thuẫn, KHÔNG tự chọn bài hợp ý mình.
- **Truy xuất nghèo/lệch?** → mở rộng truy vấn (đồng nghĩa/MeSH liên quan, nới ràng buộc) rồi lọc lại; vẫn nghèo → gắn **PARTIAL**, KHÔNG kết luận chắc chắn.
- Bài không qua được các câu hỏi trên → **LOẠI, ghi rõ lý do** (ví dụ "trả về sai chủ đề", "đã bị rút (retracted)", "surrogate không suy ra được kết cục cứng").

### Bước 6 — Soạn câu trả lời
Ngắn gọn, có trích dẫn + nêu rõ khoảng trống chứng cứ nếu có. Trích dẫn lấy từ trí nhớ (chưa phân giải PMID/DOI bằng công cụ tra cứu thật) → gắn `[CẦN KIỂM CHỨNG]` và KHÔNG đưa vào bảng nguồn chính thức. Mục tiêu: tỷ lệ trích dẫn ảo = 0%.

## Mẫu đầu ra

```
PICO (1 dòng): P[..] I[..] C[..] O[..]
Trả lời ngắn (3–6 câu): [kết luận thực hành] — độ mạnh chứng cứ mô tả: [cao/TB/thấp] (KHÔNG gán GRADE chính thức ở bước này)
| Loại thiết kế | Năm | Phát hiện chính | PMID/DOI |
|---|---|---|---|
| [SR/RCT/…]    |     |                 |          |
Khoảng trống / điểm tranh cãi: ____
[⚠ PARTIAL — thiếu nguồn online, kết quả chưa đầy đủ] (chỉ ghi khi connector/nguồn lỗi)
```

## Ví dụ minh họa (ẩn danh, KHÔNG PII)

> *Đầu vào:* "SGLT2i có giảm nhập viện suy tim ở bệnh nhân suy tim EF giảm không?"
> *PICO:* P: suy tim EF giảm; I: SGLT2i; C: chăm sóc chuẩn; O: nhập viện do suy tim.
> *Xử lý:* tra RAG/guideline trước, bổ sung SR/RCT qua PubMed để lấy PMID/DOI → trả lời 4 câu + bảng nguồn có PMID/DOI → nêu mức chứng cứ mô tả (không gán GRADE chính thức). Con số hiệu quả cụ thể (HR, NNT…) chỉ ghi khi có nguồn xác minh được, không suy diễn từ trí nhớ.

## Tiêu chí hoàn thành

Coi là hoàn thành khi có đủ:
- PICO 1 dòng.
- Trả lời ngắn nêu độ mạnh chứng cứ mô tả (không gán GRADE chính thức).
- Bảng nguồn — mỗi dòng có PMID/DOI đã xác minh.
- Nêu rõ khoảng trống/điểm tranh cãi nếu có.
- Gắn cờ PARTIAL nếu connector/nguồn lỗi hoặc thiếu.

## Ranh giới của phần tra cứu này

- CHỈ tra cứu + tổng hợp có trích dẫn cho MỘT câu hỏi lâm sàng cụ thể.
- KHÔNG ra quyết định điều trị thay bác sĩ.
- KHÔNG tự chấm GRADE/NNT chính thức — chỉ mô tả độ mạnh chứng cứ định tính (cao/trung bình/thấp). Chấm GRADE/NNT đầy đủ và định vị chứng cứ mới giữa các guideline hiện hành mâu thuẫn là một bước thẩm định chuyên sâu riêng, ngoài phạm vi tra cứu nhanh này.
- KHÔNG tự ghi/đồng bộ kết quả vào bất kỳ hệ lưu trữ chứng cứ trung tâm nào — phần này chỉ trả kết quả tra cứu cho ca đang tư vấn.

**Fallback khi nghi guideline đã lỗi thời:** nếu KHÔNG trích dẫn được guideline mới nhất cho chủ đề, hoặc nghi bản đang dùng đã lỗi thời → nêu rõ trong đầu ra rằng bản guideline hiện có **CHƯA xác minh là bản mới nhất**, gắn `[CẦN KIỂM CHỨNG]`, và đề nghị bác sĩ đối chiếu trực tiếp nguồn hiệp hội chuyên khoa gốc. KHÔNG tự kết luận "không có cập nhật".

---

**Cần bác sĩ kiểm chứng.**
