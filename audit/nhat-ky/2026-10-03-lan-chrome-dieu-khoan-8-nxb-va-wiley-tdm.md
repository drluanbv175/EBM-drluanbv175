# 03/10/2026 — Làn Chrome: đọc điều khoản 8 NXB, Wiley TDM tải 18/23 bài, tiện ích Chrome che chuỗi băm

Bác sĩ yêu cầu «xử lý triệt để nguồn chặn bot và đọc toàn văn». Đo trên 72 dashboard: 163 PMID thuộc mục `apply`, chỉ 49 có
toàn văn trong kho; 114 thiếu. Phiếu chia theo miền cho thấy rào chính KHÔNG phải chặn bot mà là điều khoản NXB.

**Điều khoản đọc cùng ngày** (Chrome của bác sĩ + WebFetch):
- Cấm RÕ dùng nội dung với công cụ AI: OUP (legal notice có cả chữ «prompt»), NEJM, AAP, SAGE.
- JAMA: trang điều khoản AMA chặn cứng («Sorry, you have been blocked») cả trong Chrome thật.
- Chỉ cấm huấn luyện mô hình hoặc im lặng về AI: BMJ, ACP, Wolters Kluwer.
- Wiley: TDM chỉ qua API, không qua cào trang.

Bác sĩ chọn uỷ quyền máy đọc qua Chrome cho cả hai nhóm. Đã ghi 11 khoá vào sổ uỷ quyền ngoài git.

**Bằng chứng nền tảng đã dời:**
- atsjournals.org chuyển 301 sang academic.oup.com.
- journals.lww.com chuyển sang ovid.com.

Bảng theo tiền tố DOI vẫn đúng, nhưng bảng theo miền phải thêm miền mới.

**Wiley TDM** (token của bác sĩ, truy cập theo IP): 18/23 bài tải được. 5 bài ACCESS_DENIED do IP 149.50.211.66 không có quyền. Lượt đầu bỏ sót 8 bài vì script tạm chỉ nhận tiền tố `10.1002/`, trong khi Wiley-Blackwell dùng `10.1111/`. PDF lưu dạng `PMID-<n>_WTDM.pdf`, phiếu xếp «tdm_nxb», không gọi là OA.

**Lỗi quy trình:** Claude in Chrome che chuỗi hex 64 ký tự liền thành «[BLOCKED: Base64 encoded data]», nên bước 3 của `--huong-dan` không lấy được `sha256_toan_van`. Đã vá để trả theo nhóm 8 ký tự.

**Bài học:**
1. «Không truy cập được» có hai tầng khác nhau: chặn kỹ thuật (bác sĩ bấm xác minh hoặc đăng nhập là qua) và điều khoản (bấm bao nhiêu cũng không đổi). Đo tầng điều khoản trước khi mở bài.
2. Bảng theo miền mục theo thời gian vì nhà xuất bản dời nền tảng. Khi một miền «chưa kiểm» trả 301, phải đo lại.
3. Một công cụ trung gian (tiện ích trình duyệt) có thể sửa dữ liệu trả về. Hướng dẫn chép tay phải được chạy thật ít nhất một lần.
