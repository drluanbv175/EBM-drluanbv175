# 13/10/2026 — Abstract EndNote nạp qua Europe PMC bị cắt ở dấu «<»

**Phát hiện:** phiên làm PR #171 (tóm tắt máy cho trích dẫn tham khảo) thấy abstract gốc trong EndNote bị cụt giữa câu —
INTERACT2 PMID 23713578 còn «target systolic level of Results»; AβYSS PMID 40401436 còn «mmHg, P Conclusions». Ước tính
lúc phát hiện: ≥ 15 trong 155 trích dẫn tham khảo.

## Nguyên nhân

`tools/nap_endnote_chu_de.py::_bo_the_html` dùng `re.sub(r"<[^>]+>", " ", s)` — coi MỌI dấu «<» là đầu thẻ HTML.
`abstractText` của Europe PMC chứa «<140 mm Hg», «P < .001», «<0·05» dạng CHỮ thô (không mã hoá `&lt;`), nên regex xoá
từ «<» tới dấu «>» kế tiếp — thường là thẻ `<h4>` của mục sau. Chỉ bản ghi đi làn DỰ PHÒNG Europe PMC (khi NCBI chặn IP —
gặp thật 11/10 và lại chặn suốt 13/10) dính lỗi; làn PubMed efetch dùng ElementTree nên không dính. Hàm cũ còn hai khuyết
tật cùng loại: không giải mã thực thể (`&lt;`/`&gt;` nằm nguyên trong EndNote) và không xử lý thẻ mã hoá KÉP trong tiêu đề
(«&lt;i&gt;Helicobacter pylori&lt;/i&gt;»).

## Số đo (13/10/2026)

- 828 PMID duy nhất của 72 dashboard, tải Europe PMC: tên thẻ thật dùng chỉ có `h4` · `i` · `sup` · `sub` · `b`; 211 PMID
  có dấu «<» là chữ; 12 `&lt;` + 13 `&gt;`; 6 tiêu đề mã hoá kép thẻ. Nếu đi làn Europe PMC, 194/828 abstract bị cắt.
- Thư viện EndNote thật của bác sĩ, chạy KHÔ (chỉ đọc) `sua_abstract_bi_cat_endnote.py --europepmc-khi-ncbi-chan`:
  853 bản ghi khớp PMID · **187 BỊ CẮT** (cả 187 mang ghi chú «Metadata: Europe PMC» — 148 là nguồn CHÍNH của mục dashboard,
  39 là tài liệu tham khảo; mất từ 1 tới 2.383 ký tự chữ-số, trung vị 265) · 655 khớp · 11 khác (đều KHÔNG do công cụ nạp
  — giữ nguyên) · 0 không đo được · 6 PMID chưa có bản ghi. Ca nhỏ cũng là mất thật: «placebo, <1%).» còn «placebo, .».
- Khối «EBM · ĐỌC NHANH» của mục CHÍNH chép từ dashboard nên không bị ảnh hưởng; phần ABSTRACT GỐC bên dưới thì bị cắt.

## Cách vá

1. `_bo_the_html` chỉ bỏ thẻ có tên trong danh sách (`h1–h6 p br div span i b u em strong sup sub sc`) và tên thẻ phải
   theo sau bởi khoảng trắng, «/» hoặc «>»; thẻ lạ để nguyên (hiện thừa một thẻ vô hại, xoá nhầm chữ thì không). Sau đó
   giải mã thực thể rồi bỏ thẻ lần nữa (thẻ mã hoá kép). Kiểm trên 828 bản ghi thật: giữ đủ mọi ký tự chữ-số, 0 thẻ sót,
   0 thực thể sót.
2. Công cụ mới `tools/sua_abstract_bi_cat_endnote.py` (chạy khô mặc định): tách abstract GỐC dưới `PHAN_CACH`, so với bản
   tải lại theo dãy ký tự chữ-số; chỉ sửa khi abstract trong EndNote là DÃY CON của bản đối chiếu và mọi đoạn thiếu bắt
   đầu ngay sau dấu «<» (xét mọi cách gióng tương đương); `--ap-dung` sao lưu `sdb.eni` trước, đọc lại trường ngay trước
   khi ghi, thay đúng phần dưới dấu phân cách, giữ nguyên khối tiếng Việt; không mở/đóng EndNote.
3. Nguồn đối chiếu mặc định PubMed efetch; NCBI chặn ⇒ KHÔNG ĐO ĐƯỢC (mã 2). Cờ `--europepmc-khi-ncbi-chan` (bác sĩ chọn)
   đối chiếu bản Europe PMC qua bộ lọc đã vá, báo cáo ghi rõ nguồn.

Kiểm dấu vân trên dữ liệu thật: 194/194 abstract bị regex cũ cắt ⇒ `bi_cat`; 828/828 bản lọc đúng ⇒ `khop`; 2.323/2.323
đoạn xoá ngẫu nhiên không bắt đầu ở «<» ⇒ `khac`; khuôn «giả PubMed» (nhãn VIẾT HOA đầu dòng, `<sup>` nối liền): 194/194 và
786/786. Bản đầu dùng cửa sổ cố định (12 ký tự trước + 24 sau) bắt đủ 194 nhưng nhận nhầm 18/783 ca «xoá một câu không
có «<»» — thay bằng xét trượt gióng.

## Kiểm hồi quy

- `tools/test_abstract_bi_cat_endnote_20261013.py` — 30 ca (bộ lọc thẻ, phân loại, thay đúng phần gốc, EndNote giả).
  Sau khi gộp master (PR #171/#172): `pytest tools/` 2.839 đạt; ruff sạch; `chot_hoi_quy_bai_hoc.py` mã 0.
- Đột biến 21/21 đỏ đúng test canh rồi phục hồi xanh (`python -B`, xoá `__pycache__` trước mỗi phép). Một đột biến (bỏ
  luật «đoạn sát nhau là nối tiếp») ban đầu KHÔNG bị bắt: fixture tự soạn không tái hiện phép gióng tách đoạn của 3/194 ca
  thật ⇒ lỗi phép thử; sửa bằng SequenceMatcher giả ép đúng cách gióng của ca thật PMID 42024702.

## Còn treo — việc của bác sĩ

- Chạy `--ap-dung` (187 bản ghi) hay chờ NCBI gỡ chặn để đối chiếu PubMed đúng như yêu cầu ban đầu.
- Kho tóm tắt máy `EBM-Dashboards/tom-tat-abstract-vi.json`: 39 PMID (đo lần cuối 13/10, kho đang được bổ sung — 37 ở
  lượt đo trước) có tóm tắt dựng từ abstract BỊ CẮT. Chốt
  `so_khong_khop` (PR #171) KHÔNG bắt được — chốt chỉ đòi mọi số của tóm tắt có trong abstract gốc, abstract đầy đủ chỉ
  THÊM số ⇒ tóm tắt cũ vẫn qua. Cần dựng lại các mục đó rồi `nap_endnote_chu_de.py --tat-ca --tom-tat-vi --ap-dung`.

Cần bác sĩ kiểm chứng.
