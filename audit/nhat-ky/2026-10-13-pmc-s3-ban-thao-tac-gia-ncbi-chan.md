# 13/10/2026 — Bản thảo tác giả PMC bị bỏ khi NCBI chặn IP: thêm đường dự phòng PMC Cloud S3

Tiếp nối `2026-10-11-gom-oa-ncbi-chan-dung-som.md` (đường dự phòng Europe PMC).

## Đo được
- Ca thật: PMID 22591294 (Ray, NEJM 2012, azithromycin), PMC3374857, NIHMS381524. NCBI chặn IP (trang «Blocked
  Diagnostic») ⇒ tầng PMC đổi PMID→PMCID qua Europe PMC (`lien_ket_pmc_epmc`). Europe PMC ghi `isOpenAccess="N"` cho bản
  thảo tác giả NIH ⇒ `tai_jats(..., la_oa=False)` trả `"khong_oa_epmc"`, không lưu gì.
- Docstring của `tai_jats` vốn ghi «NCBI có thể có bản thảo tác giả khi hết chặn» — tức hệ ĐÃ nhận bản thảo tác giả PMC qua
  efetch; chỉ thiếu đường dự phòng trong lúc NCBI bị chặn.
- Bucket PMC Cloud Service `pmc-oa-opendata` (S3 công khai của NIH, không cùng hạ tầng NCBI): danh mục ListObjectsV2 với
  tiền tố `PMC3374857.` trả đúng một `CommonPrefixes` = `PMC3374857.1/`. `PMC3374857.1.json`: `is_pmc_openaccess: false`,
  `is_manuscript: true`, `license_code: "TDM"`, `is_retracted: false`, `xml_url` = `s3://…/PMC3374857.1.xml?md5=32b9de…`.
  Phiên 13/10 đã lưu tay `EBM-Dashboards/toan_van_oa/PMID-22591294_PMC3374857.xml`; md5 tệp đó TRÙNG md5 trong siêu dữ liệu.
- README.txt của bucket: `license_code` là mã Creative Commons hoặc «TDM» (bản thảo tác giả có toàn văn dùng được cho khai
  thác văn bản); mọi URL S3 trong JSON mang tham số `md5`; `is_retracted` tính theo từng phiên bản. Trang tài liệu PMC Cloud:
  có bài có bản 2 mà không có bản 1, và số phiên bản lớn hơn KHÔNG có nghĩa là mới hơn ⇒ không được thử «.1» mò.

## Vá (`tools/gom_toan_van_dashboard.py`)
- `tai_jats`: `la_oa is False` VÀ `trang["ncbi_chan"]` (NCBI chặn/elink lỗi) ⇒ `tai_jats_pmc_s3`. NCBI không chặn ⇒ hành vi
  cũ, không gọi gì.
- `tai_jats_pmc_s3`: tra danh mục để biết phiên bản (`phien_ban_pmc_s3`; danh mục bị cắt hoặc không phải danh mục S3 ⇒ lỗi,
  không coi là «không có») → đọc JSON mọi phiên bản → `chon_ban_pmc_s3` (thuần, không mạng): lệch khoá `pmcid`/`version` ⇒
  `"loi"`; BẤT KỲ phiên bản nào `is_retracted` ⇒ `"rut_bai_pmc"`, không lưu bản nào; cờ rút bài không rõ ⇒ `"loi"` (KHÔNG BIẾT
  ≠ «chưa rút»); không bản nào có giấy phép cho phép (TDM hoặc CC BY*/CC0/phạm vi công cộng — cùng tập cổng Unpaywall) ⇒
  `"khong_oa_epmc"` như cũ; nhiều bản được phép ⇒ bản công bố trước bản thảo tác giả, rồi số phiên bản → `xml_url` phải đúng
  bucket + đúng khoá bài + có `md5` → tải → md5 lệch ⇒ `"loi"` → `la_jats_toan_van` ⇒ lưu `PMID-<n>_PMC<id>.xml`.
- Lỗi mạng/JSON hỏng ⇒ `"loi"` (lượt sau thử lại). `main()` gom `"rut_bai_pmc"`, in ⛔ và ghi vào `DO-PHU-OA.md` (tín hiệu
  rút bài là tín hiệu dương — không được nuốt lặng).
- Chỉ thư viện chuẩn; không dùng client S3 của repo y khoa (`app/sources/pmc_guideline_fulltext.py`) vì client đó cần engine,
  không kiểm giấy phép/md5/rút bài và chọn phiên bản theo số lớn nhất.

## Kiểm
- `tools/test_gom_pmc_s3_ban_thao_tac_gia_20261013.py`: 19 hàm / 36 ca ngoại tuyến — lấy được · giấy phép không cho phép ·
  `is_retracted` (kể cả một phiên bản đã rút, cờ không rõ) · md5 lệch · `xml_url` lạ · lỗi mạng · danh mục bị cắt · không đoán
  «.1» · ưu tiên bản công bố · đầu–cuối qua `main()`.
- Dữ liệu thật ngoại tuyến: JSON thật + XML lưu tay 13/10 qua `tai_jats_pmc_s3` ⇒ `ok`, 82.344 byte, trùng byte.
- Đột biến (`python -B`, xoá `__pycache__` mỗi phép): 16/16 đỏ đúng test rồi phục hồi xanh. Lần đầu 1 phép sống sót («bỏ kiểm
  khoá siêu dữ liệu») vì fixture `_meta(pmcid="999")` đổi luôn `xml_url` nên chốt `xml_url` đỡ hộ — sửa fixture chỉ lệch MỘT
  khoá, thêm ca lệch `version`.

## Còn mở
- Repo y khoa `app/sources/pmc_guideline_fulltext.py::_tim_key_txt_moi_nhat` chọn «phiên bản số lớn nhất = mới nhất» — trái
  tài liệu PMC Cloud; khi một bài có cả bản thảo tác giả lẫn bản công bố, có thể lấy nhầm bản. Ngoài phạm vi PR này.
