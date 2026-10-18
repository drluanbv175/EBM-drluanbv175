# 18/10/2026 — Đọc điều khoản sáu NXB chưa kiểm + ba bài giấy phép CC qua làn `--nap`

## Bối cảnh
Bác sĩ yêu cầu «hoàn thiện hết các vấn đề». Sau lượt Unpaywall và phiên uỷ quyền Chrome 20261018-064748 còn 12 bài «consider»
(và một bài nợ apply 23095984) không lưu được vì `phien_uy_quyen_chrome.py --kiem` từ chối «NXB của bài (chưa kiểm điều khoản)».
Làm theo uỷ quyền thường trực 04/10/2026 (doctrine `_CONNECTOR-CHUNG-CU.md` §2septies mục 8): đọc trang điều khoản trên Chrome
của bác sĩ (lớp Cloudflare do bác sĩ qua) → PR bảng → `--ghi-uy-quyen` SAU KHI bác sĩ gộp.

## Đo được
- **Unpaywall gắn nhầm giấy phép.** DOI 10.3310/hta24270 (NIHR HTA) được Unpaywall ghi `cc-by`, nhưng dòng bản quyền in trong CHÍNH
  báo cáo là «© Queen's Printer and Controller of HMSO 2020 … freely reproduced for the purposes of private research and study».
  Câu «distributed under the terms of the Creative Commons Attribution License» trong bài thuộc tài liệu trích lại (đề cương đã
  công bố). Tầng OA (`gom_toan_van_dashboard.py --unpaywall`) tin nhãn `license` của Unpaywall; lần này may mà trang trả 403 nên
  không lưu. Bài học: nhãn giấy phép của Unpaywall là gợi ý — với NXB lưu giữ bản quyền, đọc dòng bản quyền của chính tài liệu.
- **Ba bài mang CC của chính bài** (đi `doc_toan_van_co_nguoi.py --nap` khai `giay_phep_cc`, KHÔNG cần mục bảng):
  WJG 22147965 (Baishideng, mục «Open-Access Policy of This Article»: CC BY-NC 4.0 — bản PMC cùng bài chỉ ghi «All rights
  reserved»), HSF 33798049 (IMR Press lưu giữ số cũ, thông báo CC-BY-NC; toàn văn chỉ là PDF — băm tệp PDF trong trình duyệt khớp
  bản tải về thư mục tạm, đọc xong xoá), Turk J Surg 42830623 (Galenos, CC BY-NC 4.0). Cả ba: xác minh định danh được, độ đầy đủ
  `full`. Bài HSF tự mâu thuẫn số liệu giữa tóm tắt (19 nghiên cứu, HR suy tim mạn 1,13) và kết quả (23 đoàn hệ, HR 1,26) — ghi
  cả hai kèm vị trí trong hồ sơ.
- **Tiền tố DOI dùng chung:** 10.5606 là của Baycinar Tibbi Yayincilik (Crossref), nhiều tạp chí ⇒ khoá TJPMR khớp hẹp
  `10.5606/tftrd.`. 10.4997 (J R Coll Physicians Edinb) nay phân giải sang SAGE ⇒ đã thuộc khoá SAGE theo miền.
- **Không truy cập được (ghi `--khong-truy-cap`, 90 ngày):** 23095984 (OUP, bản «bronze» Unpaywall không còn mở; kho Auckland
  chỉ có siêu dữ liệu), 31808452 (SAGE «Get access»), 3704105 (QJM 1986, OUP), 35522453 (BJCN, MA Healthcare «GET ACCESS»).
- **Chưa kiểm được:** *Beijing Da Xue Xue Bao* (`10.19723/`) — trang tạp chí và chndoi.org không tải được qua VPN; để lượt tắt VPN.

## Thay đổi
- `tools/doc_toan_van_co_nguoi.py`: sáu mục «cam» («không rõ ⇒ xử như cấm») — Baishideng (`10.3748/`, `10.4240/`), CFPC (miền
  cfp.ca, không DOI), RCGP/BJGP (`10.3399/`), NIHR Journals Library (`10.3310/`), TJPMR (`10.5606/tftrd.`), Medscape (miền).
- Doctrine §2septies mục 1: đợt đọc 18/10 + ba NXB không vào bảng vì bài mang CC + cảnh báo nhãn Unpaywall.
- `tools/test_dieu_khoan_nxb_dot_20261018.py`: 26 ca; 7 đột biến đều đỏ đúng chỗ, phục hồi xanh.

## Việc sau khi bác sĩ gộp
`--ghi-uy-quyen` cho sáu khoá (căn cứ: uỷ quyền thường trực 04/10/2026) rồi lưu qua làn Chrome: CFP 28500192 (trang cfp.ca,
`.fulltext-view`), BJGP 34711558 và TJPMR 31453503 (bản PMC, truyền `--doi`), HTA 32568065 (trang NIHR, `#full-report`).
MedGenMed 16369379 (PMC, không DOI) vẫn để bác sĩ đọc trực tiếp.
