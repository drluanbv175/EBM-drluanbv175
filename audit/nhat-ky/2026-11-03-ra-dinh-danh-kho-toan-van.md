# 03/11/2026 — Tệp toàn văn ĐÃ có trong kho chưa từng được kiểm định danh; cổng BH175 chỉ gác tệp mới (BH176)

**Mã:** BH176. **Nối tiếp:** `2026-11-02-unpaywall-pdf-sai-bai.md` (BH175, PR #284 — cổng định danh cho tệp MỚI của tầng Unpaywall).

## Chuyện gì đã xảy ra

BH175 thêm cổng định danh vào tầng Unpaywall, nhưng cổng chỉ xét bản vừa tải về. Mọi tệp đã nằm trong
`EBM-Dashboards/toan_van_oa/` trước đó (Unpaywall, phiên Chrome, Wiley TDM, bản in `BANIN`) chưa ai kiểm có đúng là bài mang tên
tệp không. Phép đo 03/11 của phiên BH175 dùng tiêu đề lấy từ dashboard: 81 `_UPW.pdf` ⇒ 42 khớp · 2 sai bài · 37 thiếu dữ kiện.

Hai ca sai bài đã biết, nay đo lại bằng định danh lấy từ PubMed:

- **39186635** — bài thật «Hypoxia-Inducible Factor Prolyl Hydroxylase Inhibitors in Kidney Disease» (NEJM Evid 2024, doi
  10.1056/EVIDoa2300189); tệp kho là «Dapagliflozin and anemia in patients with chronic kidney disease» (Koshino et al.), 25% từ
  của tiêu đề ở 3 trang đầu. EndNote rec 6812 gắn bản sao CÙNG mã băm.
- **42701440** — bài thật «Addressing Cardiopulmonary Risk in COPD: A Multidisciplinary Expert Opinion Framework for the United
  States Healthcare System» (doi 10.2147/COPD.S596426); tệp kho là NCHS Data Brief 521 «Mortality in the United States, 2023»,
  25%. EndNote rec 7305 gắn bản sao CÙNG mã băm.
- **38099896** (ca gốc của BH175) — đã cách ly ngày 02/11, nhưng `PMID-38099896_UPW.pdf` **lại có trong kho, ghi lúc 07:08
  03/11** (cùng kích thước 1 189 886 byte với hai bản cách ly). Bản gom chạy trên cây chính lúc đó chưa có cổng BH175 (#284 gộp
  sau đó cùng ngày) nên lượt nào chạy tầng Unpaywall cũng tải lại. Thư mục PDF của EndNote có `8531119863/PMID-38099896.pdf` cùng mã băm.

Hệ quả giống BH175: BH161 tính tệp sai bài là «đã đọc toàn văn», đọc sâu và đối chiếu số đọc nhầm bài, EndNote gắn nhầm.

## Cách vá

`tools/ra_dinh_danh_kho_toan_van.py` (CHỈ ĐỌC, chạy khô mặc định):

- Rà mọi `PMID-<n>_<HẬU TỐ>.pdf` của kho (UPW · CHR · WTDM · BANIN) và `zenodo_hub_*/DOI-*.pdf`; PDF tên lạ được liệt kê riêng.
- Định danh từ NGUỒN: PubMed esummary theo lô (tiêu đề tiếng Anh, tiêu đề nguyên ngữ, DOI) → Europe PMC khi NCBI chặn/lỗi →
  Crossref khi chỉ khớp nhờ DOI (DOI của bản ghi có đúng là bài này?) hoặc khi lệch tiêu đề (thử tiêu đề Crossref trước khi kết
  luận). Tệp Zenodo: sổ tải `_tai_ve.json`.
- Kết luận gọi ĐÚNG `gom_toan_van_dashboard.kiem_dinh_danh_upw()` (BH175 → `khop_dinh_danh` của bước ⑨), không có logic so khớp
  song song. Thứ tự thử: tiêu đề PubMed → tiêu đề nguyên ngữ của PubMed → DOI (đối chiếu Crossref với CẢ HAI tiêu đề PubMed) →
  tiêu đề Crossref (chỉ nhận khi cùng bài với tiêu đề PubMed — DOI trỏ nhầm thì PDF của bài kia không được «khớp»). Bốn nhóm:
  khớp · sai bài · không kiểm được (PDF ảnh/hỏng, không có bản ghi, DOI lệch Crossref) · không đo được (lỗi mạng, thiếu pypdf,
  không đọc được tệp). Lỗi mạng không bao giờ thành «khớp».
- Trước khi kết luận «sai bài», hai phép XÉT LẠI chỉ được HẠ xuống «không kiểm được», không bao giờ nâng lên «khớp»: bản in BANIN
  xét lại trên tệp nguồn ghi ở dải đầu trang (cùng cổng BH175, `loai` jats/html); PDF mà lớp chữ ở 3 trang đầu chỉ là dòng lặp
  (chân trang «Downloaded from…») được nhận là PDF quét.
- Báo cáo `EBM-Dashboards/RA-DINH-DANH-KHO-TOAN-VAN.md` (bảng đủ mọi tệp). Tệp sai bài kèm chữ đầu trang 1, DOI thấy trong tệp,
  tệp nguồn của bản in BANIN, và bản ghi EndNote đang gắn tệp đó.
- EndNote chỉ ĐỌC: bản sao tạm `sdb.eni` (`endnote_suc_khoe.ban_sao_csdl`); quét bảng lỗi ⇒ đọc từng rowid (trần lấy từ
  `sqlite_sequence`); thêm đường dự phòng dò thư mục `PDF/*/PMID-<n>.pdf` và so mã băm với tệp kho.
- `--cach-ly --ap-dung --pmid <đã duyệt>` DỜI (không xoá) tệp đang bị kết luận sai bài ở CHÍNH lượt đó sang
  `_cach-ly-toan-van-sai-bai/`, nối lý do vào README.txt; bản in BANIN sai ⇒ dời cả tệp nguồn ghi trên dải đầu trang (không thì
  `in_pdf_toan_van_kho.py` in lại đúng tệp sai). Thiếu `--pmid` ⇒ mã 3.
- Đọc PDF song song nhiều tiến trình khi chạy dòng lệnh (tuần tự đo được ~2,4 giây/tệp ⇒ cả kho hơn một giờ).

## Kiểm hồi quy

- `tools/test_ra_dinh_danh_kho_toan_van_20261103.py` (28, ngoại tuyến, PDF giả `pdf_gia_kiem_thu.py`): hai ca đối chứng · thử
  tiêu đề Crossref trước khi kết luận · mạng đứt cả hai nguồn ⇒ không đo được · NCBI chặn ⇒ Europe PMC, không gọi NCBI nữa · lỗi
  Crossref không làm sai bài thành khớp · không có bản ghi · khớp chỉ nhờ DOI có đối chiếu Crossref · DOI lệch Crossref · tiêu đề
  nguyên ngữ · PDF ảnh, tệp không phải PDF · thiếu pypdf · đi qua cổng BH175 · Zenodo + PDF tên lạ · chạy khô không dời, báo cáo
  phủ mọi tệp · `--ap-dung` cần `--cach-ly` và `--pmid` · cách ly chỉ dời tệp sai bài đã duyệt, nguyên vẹn, không đè bản cũ ·
  BANIN dời cả tệp nguồn · mã thoát 0/1/2 · EndNote: bản ghi gắn đúng tệp, bản sao đọc lỗi vẫn tìm qua rowid và thư mục PDF,
  không đọc được thì báo rõ · song song hỏng ⇒ rà lại tuần tự đủ tệp · tiêu đề Crossref của bài khác không thành khớp · tiêu đề
  Crossref cùng bài cứu cách viết khác · PDF quét chỉ có chân trang lặp · bản in cụt mà tệp nguồn khớp (không dời) · bài tiếng Tây
  Ban Nha có DOI.
- Chốt BH176 gọi THẬT `ra_kho`/`main` với mạng giả. Đột biến 5 phép (`python -B`, xoá `__pycache__`, sao lưu + `cmp`): sai bài
  thành khớp · lỗi mạng thành khớp · chặn tất cả · chạy khô vẫn dời · bỏ giới hạn `--pmid` ⇒ cả năm làm chốt đỏ đúng câu; phục hồi
  ⇒ xanh. Thêm 5 đột biến trên test (bỏ chốt tiêu đề Crossref · bỏ xét tệp nguồn bản in · bỏ lọc dòng lặp · bỏ thử nguyên ngữ
  trước DOI · Crossref chỉ so tiêu đề Anh) ⇒ đúng test tương ứng đỏ; phục hồi xanh.

## Bài học: lượt rà đầu tiên tự báo sai giả

Lượt rà toàn kho đầu tiên (mã trước bản vá xét lại) ra 5 «sai bài» và 4 «không kiểm được». Soi từng ca bằng tay: 2 «sai bài» và 3
«không kiểm được» là báo GIẢ —

- `PMID-32568065_BANIN.pdf`: bản in 1 trang (291 từ) chỉ in được mục «Notes» của báo cáo HTA BiCARB; tệp nguồn `_CHR.html` là
  toàn văn đúng bài (23 570 từ, cổng BH175 trên tệp nguồn: «dung»). Bản đầu của công cụ còn đề xuất DỜI CẢ tệp nguồn đúng.
- `PMID-2899840_CHR.pdf` (NEJM 1988): bản quét; lớp chữ mỗi trang chỉ có «Downloaded from nejm.org…» (28 từ/trang) — vượt
  ngưỡng «PDF ảnh» 50 từ của cổng nên thành «sai bài». Cổng BH175 cũng sẽ kết luận như vậy với một PDF quét mới tải về (xem
  Giới hạn).
- 41494416 (Tây Ban Nha), 42162485 (Đức), 42809786 (Tây Ban Nha): PubMed ghi tiêu đề DỊCH, Crossref ghi tiêu đề nguyên ngữ ⇒
  phép so hai tiêu đề báo «DOI lệch» giả.

Danh sách cho bác sĩ duyệt phải được soi từng ca trước khi trình — «sai bài» từ máy là ĐỀ XUẤT, không phải phán quyết.

## Đo trên kho thật 03/11

Lượt cuối 03/11 07:30 (mã đã có bước xét lại; 8 tiến trình), **1655 PDF**:

| Hậu tố | Khớp | Sai bài | Không kiểm được | Không đo được |
|---|---:|---:|---:|---:|
| BANIN | 1026 | 0 | 1 | 0 |
| CHR | 515 | 0 | 2 | 0 |
| UPW | 79 | 3 | 0 | 0 |
| WTDM | 25 | 0 | 0 | 0 |
| ZENODO | 4 | 0 | 0 | 0 |
| **Tổng** | **1649** | **3** | **3** | **0** |

- Sai bài: đúng ba ca đã biết — 38099896, 39186635, 42701440 (cả ba `_UPW.pdf`). Cả ba đều có bản sao CÙNG mã băm trong thư mục
  PDF của EndNote: rec 6812 (39186635), rec 7305 (42701440); 38099896 có tệp `8531119863/PMID-38099896.pdf` nhưng bản sao sdb.eni
  không đọc được bản ghi nào gắn nó (rec 7914 theo phiên BH175).
- Không kiểm được: 2899840 (`_CHR.pdf`, NEJM 1988 quét), 32568065 (`_BANIN.pdf` cụt, tệp nguồn khớp — nên in lại), 42810337
  (`_CHR.pdf`, PDF ảnh).
- 21 tệp khớp CHỈ nhờ DOI, Crossref xác nhận DOI cùng bài (phần lớn là PDF Cochrane — xem Giới hạn).
- Định danh: PubMed 1651 tệp, sổ tải Zenodo 4; NCBI không chặn lượt này; 0 tệp không đo được.
- Số tệp tăng từ 1648 (lượt 07:21) lên 1655 (lượt 07:30): phiên khác đang ghi thêm vào kho.

## Giới hạn đã biết

- Luật của bước ⑨ nhận DOI ở BẤT KỲ đâu trong PDF, kể cả danh mục tham khảo: bài khác TRÍCH bài cần tìm vẫn qua. Báo cáo liệt kê
  riêng các tệp «khớp CHỈ nhờ DOI» để liếc lại.
- PDF của Cochrane Library: pypdf tách tiêu đề thành từng ký tự («P r e g a b a lin f o r…») nên phép so tiêu đề trượt; các tệp
  này chỉ khớp nhờ DOI (DOI ở chân trang đọc được, Crossref xác nhận cùng bài). So tiêu đề trên chuỗi đã bỏ khoảng trắng — như
  phép so DOI đang làm — là sửa ở `khop_dinh_danh` (một nơi cho cả bước ⑨), chưa làm ở đây.
- Tiêu đề chung chung có thể đạt 60% trên 3 trang đầu của một bài cùng chủ đề; «khớp» là phép so định danh, không phải thẩm định.
- Hai phép xét lại (tệp nguồn của bản in, lọc dòng lặp) nằm ở CÔNG CỤ RÀ, chưa ở cổng BH175: một PDF quét có chân trang chữ mới
  tải qua Unpaywall vẫn bị cổng gọi là «sai bài» (vẫn KHÔNG được lưu — chiều an toàn, chỉ là nhãn sai). Đưa lọc dòng lặp vào
  `kiem_dinh_danh_upw` là việc tiếp theo sau khi #284 gộp.
- Chỉ rà PDF. `_UPW.html`, `_CHR.html` và XML JATS chưa rà (cổng BH175 có nhánh HTML/JATS, nhưng thân bài HTML lưu từ trình duyệt
  có thể không mang tiêu đề — cần đo trước khi bật để không báo sai bài giả).
- Bản sao `sdb.eni` chép lúc EndNote đang mở đọc lỗi một phần: quét toàn bảng `refs`/`file_res` báo «database disk image is
  malformed», dòng rec 7914 đọc ra rác (`accession_number` = «ed to pr»). Có thể chỉ là bản chép giữa hai lần ghi của EndNote,
  chưa phải thư viện hỏng — chưa kết luận. Công cụ không dựa hẳn vào CSDL: dò thêm thư mục PDF theo tên tệp.

## Việc của bác sĩ / còn lại

- Duyệt danh sách sai bài trong `EBM-Dashboards/RA-DINH-DANH-KHO-TOAN-VAN.md`, rồi chạy lệnh dời in ở cuối mục sai bài (dời,
  không xoá).
- Gỡ đính kèm sai trong EndNote: các bản ghi/tệp liệt kê trong báo cáo (agent không đụng EndNote).
- In lại bản BANIN bị cụt của 32568065 (`in_pdf_toan_van_kho.py`; bản in hiện tại chỉ có mục «Notes»).
