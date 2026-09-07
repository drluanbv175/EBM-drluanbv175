# 14. Tái thẩm định và tái dựng một tài liệu cập nhật chứng cứ ĐÃ CÓ SẴN

## Khi nào dùng

Khác với luồng mặc định của skill (bác sĩ nêu MỘT câu hỏi/vấn đề, hệ tổng hợp từ đầu — xem mục
4 và 5 của `SKILL.md`), tài liệu này áp dụng khi **điểm khởi đầu là một VĂN BẢN ĐÃ SOẠN SẴN**
bác sĩ tải lên (Word/PDF/Markdown), do chính bác sĩ, một công cụ AI khác (Gemini, ChatGPT, một
plugin soạn thảo…), hoặc một nguồn ngoài viết ra — và yêu cầu là **rà lại, chuẩn hoá, cập nhật**,
không phải tổng hợp mới.

Dấu hiệu nhận biết: bác sĩ nói "file này cấu trúc chưa đúng chuẩn", "chứng cứ chưa phải mới
nhất", "hãy kiểm tra lại", "tham khảo [công cụ khác] rồi cập nhật file trên" — trong khi vẫn đính
kèm file gốc.

**Vì sao cần một quy trình riêng.** Một câu hỏi mở luôn được TỰ hệ TÌM nguồn rồi mới viết — nên
mọi con số đi vào tài liệu đều đã qua Bước 2/3 của mục 4 (`SKILL.md`). Một văn bản có sẵn thì
NGƯỢC LẠI: các khẳng định đã VIẾT XONG trước, và rủi ro không nằm ở "tìm chưa đủ" mà ở ba lớp
khác hẳn — (a) khẳng định trông hợp lý nhưng nguồn không tồn tại hoặc bị gán sai, (b) văn bản
mang theo dấu vết hỏng của công cụ đã soạn ra nó (trích dẫn thô chưa xử lý, số liệu bị mất trong
một bước xử lý trung gian), (c) một quần thể/con số bị gán nhầm sang chỗ khác dù bản thân nó có
thật. Rà theo phản xạ "tìm chứng cứ mới" như luồng mặc định sẽ **bỏ sót cả ba lớp này**.

## Quy trình 6 bước

### Bước 0 — Trích xuất TOÀN VĂN, không tóm lược

Đọc hết mọi đoạn văn và mọi bảng bằng công cụ đọc cấu trúc thật (vd `python-docx` cho `.docx`:
lặp `document.paragraphs` lấy `.style.name`+`.text`, lặp `document.tables[i].rows[j].cells[k]`),
không dùng bản tóm tắt/OCR rút gọn. Giữ nguyên số thứ tự đoạn để định vị lại khi sửa. Một bảng có
ô rỗng vẫn phải liệt kê đủ ô — ô rỗng chính là dữ liệu cần điều tra ở Bước 1.

### Bước 1 — Rà "khoảng trống bất thường"

Tìm câu văn còn NGUYÊN cấu trúc ngữ pháp nhưng thiếu con số ở đúng vị trí lẽ ra phải có: đơn vị
đứng một mình không có số đi kèm ("liều... mg/ngày"), mệnh đề so sánh thiếu một vế ("... so với
... ở nhóm chứng"), khoảng trắng kép giữa hai từ nối. Đây là dấu hiệu **MẤT DỮ LIỆU trong một
bước xử lý trước đó** (thường là một script trung gian xoá nhầm giá trị số khi định dạng lại văn
bản) — không phải bác sĩ cố ý để trống, và không được lấp bằng cách đoán hoặc bằng trí nhớ huấn
luyện. Mỗi ô/câu như vậy phải được coi là MỘT khẳng định cần xác minh lại từ đầu, y hệt như đang
viết một câu trả lời mới.

### Bước 2 — Rà nguồn: PHẢI TỒN TẠI THẬT, không chỉ đúng định dạng

- Mỗi PMID/DOI phải **phân giải thật** (`mcp__PubMed__get_article_metadata`, không chỉ
  `search_articles`) — lấy đủ tiêu đề, tạp chí, ngày công bố để đối chiếu với câu văn đang trích.
- Mỗi TÊN guideline/hướng dẫn phải được kiểm tra **tồn tại thật**, kể cả khi nghe rất hợp lý và
  đúng định dạng ("Hướng dẫn ESC năm X"). Một cái tên nghe thuận tai không phải bằng chứng nó có
  thật — công cụ soạn thảo trước có thể đã "nội suy" một phiên bản chưa từng công bố.
- Áp dụng **CÁCH TÌM CỤ THỂ — 4 lượt** của mục 4 (`SKILL.md`) cho MỌI nguồn định thay/giữ, kể cả
  nguồn có vẻ đã đúng — không tin tưởng ngầm định chỉ vì nó đã có mặt trong file gốc.
- Kiểm rút bài cho TỪNG PMID/DOI trước khi giữ lại, theo đúng chuỗi 3 tầng đã mô tả ở mục 4.

### Bước 3 — Rà artifact công cụ khác để lại

Tìm dấu vết CHƯA XỬ LÝ XONG của một công cụ soạn thảo AI khác: chuỗi trích dẫn thô kiểu
`[cite: N, M]`/`【N†source】`, dấu ngoặc rỗng, placeholder chưa render. Đây là loại lỗi hiển thị mà
mục 5B (`SKILL.md`) đã cấm tuyệt đối đưa vào MỌI câu trả lời của skill này — khi rà một tài liệu
có sẵn, phải chủ động tìm và loại bỏ chúng, không chỉ tránh tự tạo ra.

### Bước 4 — Đối chiếu ĐÚNG QUẦN THỂ cho từng con số, không suy đoán theo cấu trúc câu

Khi một RCT báo cáo hiệu số **tách riêng theo nhiều quần thể/phân nhóm** (toàn bộ nghiên cứu vs.
đơn trị liệu, ITT vs. PP, theo LVEF/tuổi/mức lọc cầu thận…), phải đọc nguyên văn abstract để biết
CHÍNH XÁC con số nào thuộc quần thể nào — **tuyệt đối không suy đoán theo vị trí câu** trong tài
liệu đang rà, vì văn bản gốc có thể đã gán sai ngay từ đầu.

**Ca thật (07/09/2026, kiểm bằng `mcp__PubMed__get_article_metadata`, PMID 39213194 — HELIOS-B,
Fontana và cs., *N Engl J Med* 2024, DOI: 10.1056/NEJMoa2409134).** Tài liệu bác sĩ tải lên viết:
"Ở nhóm bệnh nhân đơn trị liệu... giảm tỷ lệ tử vong do mọi nguyên nhân tích lũy tại tháng thứ 42
(HR: 0,65)". Đọc nguyên văn abstract: HR 0,65 (KTC 95% 0,46–0,90; p=0,01) là **tử vong do mọi
nguyên nhân của TOÀN BỘ quần thể nghiên cứu**; con số riêng của nhóm đơn trị liệu là HR 0,67
(KTC 95% 0,49–0,93; p=0,02) cho **biến cố gộp** (không phải tử vong đơn thuần). Cấu trúc câu của
tài liệu gốc — đặt số ngay sau cụm "nhóm đơn trị liệu" — khiến việc gán nhầm trông hợp lý nếu chỉ
đọc lướt. Chỉ phát hiện được bằng cách tra lại đúng câu trong abstract gốc, không phải bằng cách
đọc lại câu trong tài liệu cần sửa kỹ hơn.

### Bước 5 — Khai báo CẤP NGUỒN khi không thể xác minh từng ô riêng lẻ

Một số bảng (điển hình: bảng liều thuốc trụ cột đã ổn định nhiều năm trong thực hành, ví dụ liều
khởi đầu/liều đích của 15-20 phân tử GDMT) có khối lượng giá trị quá lớn để trích PMID riêng cho
từng ô mà không kéo dài việc tra cứu một cách không tương xứng với giá trị tăng thêm. Trong
trường hợp này:

- **KHÔNG** để trống (đó là hồi quy về đúng lỗi Bước 1 vừa sửa).
- **KHÔNG** gán một PMID không thật sự hỗ trợ giá trị đó chỉ để "trông có nguồn" (đó là bịa
  provenance).
- **KHÔNG** fabricate độ chính xác giả bằng cách trích PMID cho một giá trị chỉ tra được ở mức
  hướng dẫn tổng hợp.
- **PHẢI** khai báo tường minh CẤP NGUỒN cho từng ô/nhóm ô: đánh dấu rõ ô nào trích trực tiếp từ
  một RCT/PMID cụ thể đã xác minh, và ô nào lấy theo liều/ngưỡng chuẩn của hướng dẫn tổng hợp
  (ESC/ACC-AHA/Bộ Y tế Việt Nam…) mà không trích PMID riêng cho từng giá trị — kèm MỘT dòng chú
  thích ở đầu bảng nói rõ quy ước hai cấp này. Xem cột "Cấp nguồn" trong bảng mẫu ở
  `templates/mau-cap-nhat-chuyen-sau.md` mục 6.

## Đầu ra

- Nếu tài liệu gốc là chuyên luận dài, liền mạch (không phải danh sách PICO rời rạc) — sản phẩm
  ra là **văn bản dài** theo cấu trúc `templates/mau-cap-nhat-chuyen-sau.md`, không bắt buộc phải
  ép thành Web Dashboard "Evidence Workbench" (khác quy tắc mặc định ở mục 5A, vì bản chất đầu
  vào là chuyên luận, không phải PICO rời rạc). Vẫn nên hỏi bác sĩ có muốn tách thêm các khẳng
  định định lượng chính thành `ITEM-xx` cho Web Dashboard để tra nhanh sau này hay không.
- Ghi rõ, ngay đầu tài liệu đầu ra, DANH SÁCH những gì đã sửa so với bản gốc: nguồn giả bị loại,
  nguồn thay thế thật, ô số liệu đã điền lại, và bất kỳ trường hợp gán-sai-quần-thể nào đã sửa
  theo Bước 4 — bác sĩ cần biết CHÍNH XÁC đâu là nội dung mới so với bản họ đã tải lên.
- Mọi số liệu điền lại phải đến từ MỘT lần tra cứu thật trong chính phiên làm việc này (không tái
  sử dụng trí nhớ huấn luyện làm bằng chứng, kể cả với các thử nghiệm rất nổi tiếng) — cùng
  nguyên tắc XÁC MINH TRƯỚC — KHÔNG bịa đã áp cho toàn skill.

## Trang đọc thiết kế kiểu Artifact (tuỳ chọn, khi bác sĩ cần đọc ngay trong khung chat)

Bác sĩ không mở được `.docx` trực tiếp trong khung chat (chỉ ra thẻ tải về). Khi cần một trang
đọc được ngay — có mục lục, màu theo mức chứng cứ, bảng dễ đọc — dùng
`tools/build_trang_doc_artifact.py <src.html> <out.html> --title "..."` trên bản HTML thô xuất từ
`.docx` (vd bằng `tools/docx_sang_html_khong_pandoc.py`), rồi xuất bản bằng công cụ Artifact.

Công cụ này ra đời 07/09/2026 sau khi bản đầu (làm tay, một lần, cho một tài liệu Suy tim) bị bác
sĩ phản hồi "thiết kế chưa cân đối, bảng trình bày, các chứng cứ chưa có điểm nhấn rõ rệt" — đã
sửa (giới hạn đọc chỉ áp cho văn xuôi chứ không cả cột, để bảng/callout dùng trọn bề ngang; bọc
mọi cụm HR/RR/OR/Rate Ratio/Risk Ratio + KTC 95%/p thành "chip" màu xanh ngọc tách biệt khỏi màu
trích dẫn `[n]`; huy hiệu màu cho mức Class/Level; bảng có header dính khi cuộn) rồi mới đóng gói
thành công cụ dùng lại được, KHÔNG chỉ sửa một lần cho một file.

**Phần dùng lại AN TOÀN cho mọi tài liệu:** bảng màu, quy tắc bọc chip chứng cứ, huy hiệu
Class/Level, khung CSS 3-theme. **Phần CẦN đối chiếu lại mỗi tài liệu mới** (giả định bố cục 4
đoạn mở đầu + 1 bảng cảnh báo ngay sau) — xem "GIỚI HẠN" trong docstring của công cụ. Đây là bước
BỔ SUNG, không bắt buộc như 6 bước ở trên; không thay thế bản `.docx`/`.pdf` vẫn là bản lưu trữ
chuẩn.

## Liên kết

- Quy trình 4 lượt tìm nguồn + kiểm rút bài: mục 4, `SKILL.md`.
- Ghi nguồn sạch, cấm artifact trích dẫn thô: mục 5B, `SKILL.md`.
- Mẫu chuyên sâu (đích đến của quy trình này): `templates/mau-cap-nhat-chuyen-sau.md`.
- Trang đọc kiểu Artifact (tuỳ chọn): `tools/build_trang_doc_artifact.py`.
- Checklist trước khi bàn giao: `quality/acceptance-checklist.md`.
