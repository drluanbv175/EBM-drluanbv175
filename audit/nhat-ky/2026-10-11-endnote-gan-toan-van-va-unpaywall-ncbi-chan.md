# 11/10/2026 — EndNote: gắn toàn văn về sau · `close document` làm EndNote sập · tầng Unpaywall chết khi NCBI chặn

Bối cảnh: bác sĩ yêu cầu mỗi chủ đề cập nhật chứng cứ vào EndNote thành một nhóm, kèm toàn văn qua tài khoản
Wiley · ScienceDirect · NEJM · JAMA + PubMed «như đã thiết kế» (làn gom OA → làn Chrome có uỷ quyền → bản đọc sâu).
Chạy thật chủ đề COPD (`WebDashboard_EBM_VanDeCuThe_COPD_DoiTuongDacBiet_DaBenh_20260805.html`) vào thư viện chính
lộ ra ba lỗi.

## 1. `close document` của AppleScript làm EndNote 2025 SẬP

- Đo: `tell application "EndNote 2025" to close document "<thư viện thử>"` ⇒ lỗi -609 «Kết nối không hợp lệ»; báo cáo
  sự cố macOS `EXC_BAD_ACCESS (SIGSEGV)` cùng giây; ứng dụng tự mở lại.
- Thư viện chính đang mở lúc sập: kiểm trên BẢN SAO (đăng ký collation tuỳ biến của EndNote để `PRAGMA quick_check`
  chạy được) ⇒ `ok`, số bản ghi và nhóm không đổi. Sao lưu `.enl` + `.Data` trước mọi lần ghi (băm khớp bản gốc).
- Luật: công cụ KHÔNG BAO GIỜ đóng thư viện (đã ghi trong docstring `tools/nap_endnote_chu_de.py` và dòng ⑦ CLAUDE.md).

## 2. Toàn văn về SAU trích dẫn không bao giờ vào EndNote

- Nguyên nhân: công cụ chỉ đính PDF lúc NHẬP bản ghi mới; toàn văn thường về sau (gom OA/Unpaywall, Wiley TDM, phiên
  Chrome uỷ quyền) nên bản ghi đã nhập ở lại không có tệp.
- Kèm theo: chạy từ worktree thì không thấy `EBM-Dashboards/` ⇒ `kho=None` ⇒ báo «đính PDF 0, chưa có toàn văn 24»
  trong khi kho có sẵn PDF Wiley TDM của chủ đề — «chưa xét» bị đọc thành «không có».
- Vá: đo trên thư viện thử — `set field "File Attachments" of record … to "internal-pdf://…"` ghi đúng dòng `file_res`
  (kiểu 1, đính nội bộ). Mỗi lượt `--ap-dung` nay gắn PDF có trong kho vào bản ghi CHƯA có tệp nào (đọc lại để xác
  nhận; tệp bác sĩ đã gắn không bao giờ bị ghi đè; không đọc được trường đính kèm ⇒ không gắn, không báo thiếu), liệt
  kê bản ghi còn thiếu cho làn kế tiếp; thiếu kho ⇒ cảnh báo «CHƯA XÉT PDF». Chạy thật: gắn 1 PDF vào chủ đề COPD.
- Kiểm hồi quy: `tools/test_nap_endnote_chu_de_20261011.py` 30 ca; 26/26 phép đột biến đỏ đúng chỗ (10 phép mới G1–G10).

## 3. Tầng 2 Unpaywall chết lặng khi NCBI chặn IP

- Đo: NCBI trả trang HTML «Blocked Diagnostic» (mã 200) cho esummary ⇒ bước đổi PMID→DOI nổ `JSONDecodeError` ⇒ cả
  13 bài không-PMC của chủ đề COPD báo «chưa lấy được, lần sau thử lại» như thể Unpaywall hỏng.
- Vá: `gom_toan_van_dashboard.doi_cua_pmid` — NCBI chặn ⇒ DOI qua Europe PMC, cả lượt không gọi NCBI nữa; lỗi mạng lẻ
  tẻ chỉ chuyển bài đó; NCBI nói «không có DOI» là câu trả lời hợp lệ; hai nguồn cùng hỏng ⇒ ném lỗi, không trả rỗng.
  Chạy thật: 6/13 bài có bản đọc miễn phí nhưng thuộc NXB «cấm» (BMJ, Wiley, JAMA, Elsevier) ⇒ đúng thiết kế, sang làn
  Chrome có uỷ quyền.
- Kiểm hồi quy: `tools/test_gom_unpaywall_ncbi_chan_20261011.py` 8 ca; 7/7 phép đột biến đỏ đúng chỗ.

## Bẫy vận hành (không phải lỗi mã)

- zsh không tách biến chưa trích dẫn thành nhiều đối số: `--pmid $P` gửi 24 PMID thành MỘT chuỗi ⇒ phiếu báo
  «0/1 bài, CHƯA RÕ». Dùng `--pmid ${=P}` (zsh) hoặc mảng.

## 4. Toàn văn về sau vẫn phải chạy lại bằng tay mới vào EndNote

- Đo trong phiên Chrome uỷ quyền cùng ngày (8 bài COPD lưu vào kho): mỗi PDF mới chỉ vào EndNote khi có người chạy lại
  `nap_endnote_chu_de.py --file <dashboard> --ap-dung`; quên là PDF nằm trong kho mà nhóm EndNote vẫn thiếu.
- Vá: chế độ `--gan-kho [--pmid …]` gắn PDF trong kho vào bản ghi CÓ SẴN cùng PMID (không cần dashboard, cùng luật: chỉ bản
  ghi chưa có tệp, bản trùng PMID chỉ gắn bản đầu); `--chi-khi-dang-mo` ⇒ thư viện chưa mở thì ⚪, KHÔNG tự bật EndNote.
  `phien_uy_quyen_chrome.py --nhan` (khi có `_CHR.pdf`) và tầng Unpaywall của `gom_toan_van_dashboard.py` (PDF mới của lượt)
  tự gọi; mọi lỗi của bước phụ chỉ thành một dòng ⚪, lượt chính không hỏng; dưới pytest không bao giờ gọi.
- Chạy thật: gắn thêm 3 PDF vào bản ghi CỦA BÁC SĨ (không do công cụ nhập) cùng PMID, chưa có tệp — chạy lại «sẽ gắn 0».
- Kiểm hồi quy: `tools/test_nap_endnote_chu_de_20261011.py` + `tools/test_endnote_gan_tu_cong_cu_20261011.py`; 11/11 phép
  đột biến đỏ đúng chỗ (K1–K11, trên ba tệp).

## Bẫy vận hành của làn Chrome (đo 11/10)

- Chrome chặn lần tải TỰ ĐỘNG thứ hai trên cùng miền và nhớ lệnh chặn (europepmc.org), kể cả với cú bấm; bác sĩ bấm «Luôn cho
  phép» ở thanh địa chỉ thì Chrome NHẢ cả các lần tải đã giữ ⇒ có bản trùng «… (1).pdf» — so byte rồi mới xoá bản trùng.
- PDF của JAMA/OUP/Cochrane chuyển hướng sang miền khác ⇒ `fetch` cùng trang hỏng; ScienceDirect đi qua trang trung gian
  (`pdfft` trả HTML) ⇒ bấm «View PDF», tải từ tab `pdf.sciencedirectassets.com`.
- Europe PMC `?pdf=render` trả PDF trong Chrome của bác sĩ nhưng 403 cho Python; bài JAMA trong PMC trả 404 (không có PDF).

## 5. Nhiều phiên bản một chủ đề sinh nhiều nhóm gần trùng

- Đo khi chuẩn bị nạp 72 dashboard: tên nhóm theo câu hỏi lâm sàng ⇒ 68 nhóm cho 64 chủ đề (Suy tim tổng hợp: 5 bản, 4 câu
  hỏi khác chữ; Tiên lượng suy tim: 3 bản, 2 câu). Bác sĩ dặn: «chủ đề nào đã có và trùng thì giữ nguyên và bổ sung phần thiếu».
- Vá: `nap_nhieu` — một khoá chủ đề (tên tệp bỏ đuôi ngày) = một nhóm; bản MỚI NHẤT đặt tên; bảng `nhom_theo_chu_de` trong
  `~/.ebm-endnote.json` ghi nhớ nhóm (chỉ khi nạp thật) để bản cập nhật sau vẫn vào nhóm cũ dù câu hỏi đổi chữ; khai lại
  cùng thư viện giữ bảng, đổi thư viện thì bỏ. 5/5 phép đột biến đỏ đúng chỗ.
- EndNote sập lần hai lúc 13:40 khi bác sĩ đóng thư viện thử: luồng `ENWebSync::GetAccountInfo` (đồng bộ của chính EndNote),
  không phải lệnh của công cụ. Thư viện chính kiểm trên bản sao (`sqlite3 .backup` — nhất quán dù đang mở): `quick_check` ok.
