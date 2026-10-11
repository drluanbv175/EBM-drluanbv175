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
