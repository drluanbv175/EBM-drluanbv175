# 18/10/2026 — EndNote trống tệp dù kho đã có toàn văn (XML/HTML không được gắn)

## Bác sĩ báo
«Các trích dẫn trong EndNote vẫn chưa đầy đủ về toàn văn» — sau khi sổ toàn văn đã báo «Áp dụng ngay» 155/155 đọc toàn văn.

## Đo (chỉ đọc, qua chính lớp EndNote của `nap_endnote_chu_de.py`)
873 bản ghi trong 60 nhóm «EBM · …»:
- 370 đã có tệp đính kèm;
- **320 trống tệp dù kho có toàn văn THẬT** dạng XML JATS (PMC) hoặc HTML (Unpaywall, phiên Chrome có uỷ quyền);
- 47 chỉ có hồ sơ đọc có cấu trúc (`trinh_duyet/`, không lưu bản);
- 116 kho không có toàn văn;
- 20 không có PMID (guideline, bản ghi WoS).

## Nguyên nhân
`nap_endnote_chu_de.chon_pdf` và `gan_kho` chỉ nhận `PMID-<n>_<UPW|WTDM|CHR>.pdf`. Toàn văn lưu dạng XML/HTML đã qua cổng nội dung —
được sổ toàn văn tính «đã đọc» — nhưng không có PDF nên EndNote không bao giờ có tệp. Hai sổ đo hai thứ khác nhau mà không ai nối.

## Sửa
- Công cụ mới `tools/in_pdf_toan_van_kho.py`: với PMID có toàn văn thật (`tep_toan_van_that`, HTML phải qua cổng nội dung) mà chưa
  có PDF nào, dựng HTML in (JATS → HTML tối giản; HTML lưu sẵn → gỡ script/ảnh/khung nhúng/mọi `src`, không gọi mạng lúc in) rồi in
  bằng Chrome headless ra `PMID-<n>_BANIN.pdf`; dải đầu trang ghi nguồn và «dùng nội bộ, không phân phối lại» (bản `_CHR` ghi «CÓ
  BẢN QUYỀN»). Thân bài < 300 từ ⇒ không in.
- `nap_endnote_chu_de.NGUON_PDF` nhận `BANIN` với ưu tiên THẤP NHẤT (PDF gốc luôn thắng).
- Bộ năm ⑧ chạy công cụ in (kho CẠNH dashboard, `--file`) ngay trước khi nạp EndNote.
- `BANIN` KHÔNG khớp `TEN_TEP_TOAN_VAN` ⇒ sổ toàn văn và cổng BH161 không đếm bản in như một nguồn mới.

## Kiểm
`tools/test_in_pdf_toan_van_kho_20261018.py` 10 ca; 6 đột biến (bỏ BANIN khỏi NGUON_PDF, in cả khi đã có PDF, không gỡ script,
BANIN lọt mẫu tên toàn văn, bỏ chặn thân bài ngắn, đảo ưu tiên nguồn) đều đỏ đúng chỗ, phục hồi xanh. Nhóm test EndNote/bộ
năm/kho: 474 đạt. In thử 2 bài thật (XML PMC 12 trang, HTML Chrome 8 trang) — chữ đầy đủ, có dải nguồn.

## Bài học
Hai thước đo cùng tên «toàn văn» (sổ toàn văn = đã đọc; EndNote = có tệp) phải được nối bằng công cụ, không được giả định trùng
nhau. Còn lại sau bản sửa: 116 bài chưa có toàn văn ở đâu cả và 47 bài chỉ có hồ sơ đọc — cần làn Chrome hoặc «Find Full Text» của
bác sĩ.
