# 20/11/2026 — Hòm việc chẩn đoán nhầm lỗi «API khi cần»: NCBI chặn IP bị báo thành «kiểm khoá/tín dụng»

**Hiện tượng.** Lượt `tools/api_khi_can.py` lúc 04:30 ngày 20/11 có 1 việc lỗi. Nguyên nhân là công cụ kiểm trích dẫn A12 tra PubMed và NCBI trả trang chặn (misuse). Claude API vẫn trả 200 ở cùng lượt. Hòm việc lại báo «LỖI … (kiểm khoá/tín dụng/trần ở console.anthropic.com)», khiến bác sĩ đi kiểm sai chỗ.

**Nguyên nhân.** `giac_quan_api_khi_can` gắn cứng câu gợi ý console cho MỌI việc lỗi, không đọc phần đuôi nhật ký (`chi_tiet[].duoi`) mà lượt chạy đã ghi.

**Cách vá.** Thêm `chan_doan_loi_api_khi_can`, chỉ đọc `dung` cùng đuôi của các công cụ lỗi (`ok: false`), rồi phân loại:
- **NCBI chặn IP** (ưu tiên 3): không phải lỗi Claude API. Gợi ý đổi đường mạng/VPN, đo bằng `do_mang_nguon.py`, hoặc liên hệ NCBI.
- **Lỗi Claude API** (401/403, khoá, tín dụng, HetNganSach, 429/529; ưu tiên 2): kiểm ở console.
- **Lỗi mạng** (ưu tiên 3).
- **Chưa rõ** (ưu tiên 2): xem `~/.ebm-api-khi-can.json.log`.

**Kiểm hồi quy.**
- 7 test trong `tools/test_api_khi_can_20261118.py`, dùng đuôi nhật ký thật của lượt 04:30.
- Kiểm đột biến 2/2 bắt: bỏ nhánh NCBI; đọc cả đuôi của công cụ đã chạy ổn.
