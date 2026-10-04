# 04/10/2026 — Phiên uỷ quyền Chrome: bác sĩ nói một câu mỗi phiên, Claude đọc và lưu bản sao toàn văn (BH158)

**Yêu cầu của bác sĩ (04/10):** khi bác sĩ đăng nhập làn Chrome thì uỷ quyền truy cập toàn văn và tải trong cả phiên làm việc
đó. Bác sĩ chọn lưu «HTML thân bài + PDF nếu có» và để phiên kéo dài «đến khi bác sĩ nói "dừng"».

**Vì sao cần công cụ riêng:** quy trình cũ (03/10) hỏi bác sĩ cho TỪNG tệp trước khi lưu, nên một buổi vượt chặn Cloudflare
chỉ lưu được vài bài. Ngoài ra, uỷ quyền đọc ngày 03/10 ghi rõ phạm vi là «tóm tắt và lập hồ sơ trích xuất… KHÔNG lưu toàn văn».
Lưu bản sao là phạm vi RỘNG HƠN, nên phải có quyết định riêng của bác sĩ, ghi đúng lời và đúng phiên.

**Thiết kế (`tools/phien_uy_quyen_chrome.py`):**
- `--mo "<nguyên văn lời bác sĩ>"`: lời phải dài ≥ 20 ký tự. Phạm vi gồm các NXB có uỷ quyền đọc còn hiệu lực, KHÔNG BAO GIỜ
  gồm DynaMed/EBSCO, Scopus, Web of Science. Agent KHÔNG tự mở phiên và không suy uỷ quyền từ việc bác sĩ đã đăng nhập.
- `--kiem <PMID> --url`: kiểm trước mỗi bài — phiên còn mở, NXB thuộc phạm vi, chưa quá 20 bài/miền, đã nghỉ ≥ 60 giây kể từ
  bài trước cùng miền.
- `--nhan <PMID> --tep --url`:
  - HTML phải mang dấu `<!-- ebm-phien:<mã> pmid:<n> … -->` đúng phiên, đúng bài, và không chứa giao diện tài khoản;
  - PDF phải có chữ ký `%PDF-` và cỡ hợp lệ;
  - không ghi đè; tệp chuyển vào `toan_van_oa/PMID-<n>_CHR.html|pdf`; nhật ký phiên ghi kèm SHA-256.
- `--dung` khi bác sĩ nói «dừng»; phiên cũng tự hết hạn khi sang ngày.
- Kho tính tệp `_CHR` là «phien_chrome» (máy có toàn văn). Bộ đọc sâu sinh bản đọc từ PDF `_CHR` với nhãn «có bản quyền, KHÔNG
  phải OA», không ghi là «token TDM»; HTML `_CHR` được đọc trực tiếp như `_UPW`.
- Điều khoản NXB KHÔNG đổi và trách nhiệm thuộc bác sĩ. Trần bài và nhịp nghỉ để giống một người đọc, tránh bị NXB khoá tài khoản.
- Claude vẫn KHÔNG bấm xác minh chống bot, KHÔNG gõ tài khoản/mật khẩu.

**Kiểm:**
- `tools/test_phien_uy_quyen_chrome_20261004.py`: 16 test.
- Đột biến 12/12 đỏ đúng chỗ.
- BH158 kiểm hành vi ngoại tuyến.
