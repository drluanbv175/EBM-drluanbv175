# 30/09/2026 — PDF toàn văn Wiley TDM rơi vào chỗ git THẤY của repo y khoa CÔNG KHAI; `kich_thuoc_byte` mang KiB (PR y khoa #51, #56)
Lần tải Wiley TDM THẬT thành công đầu tiên (30/09 18:37, DOI 10.1002/jcsm.70385, tệp 8.913.789 byte) lộ hai lỗi có từ 23/09.
(1) Thư mục tải mặc định `downloads_wiley_tdm/` — tương đối so với thư mục đang đứng, thư viện tự `mkdir` ngay lúc dựng client —
không có trong `.gitignore` ⇒ `git status` hiện `??`, một lần `git add -A` là đưa PDF của nhà xuất bản lên repo công khai.
(2) `KetQuaTaiWiley.kich_thuoc_byte` lấy thẳng `DownloadResult.size`, mà thư viện tính KiB làm tròn (báo 8705) và để trống
với `EXISTING_FILE`. Lỗi (2) sống 7 ngày qua 15 test xanh vì bản giả trong test trả `size=1234` mà không ghi tệp nào — bản giả
mang đúng giả định sai của mã. Chưa PDF nào vào lịch sử git (đo trên mọi ref đã fetch: 0 commit chạm đường dẫn đó, 0 PDF).
**Vá — PR y khoa #51:** luật `downloads_wiley_tdm/` KHÔNG neo gốc (bắt ở mọi cấp); hằng `THU_MUC_TAI_MAC_DINH` để ca kiểm đọc
đúng tên mà mã dùng; `kich_thuoc_byte` = `st_size` đo trên đĩa, chỉ khi tải thành công, không đo được ⇒ None kèm cảnh báo. Rà
bằng đọc mã bốn connector guideline: không tự ghi tệp (PDF qua `get_bytes` chỉ ở bộ nhớ); toàn văn PMC qua `get_text` nằm ở
cache HTTP `data/raw/_http_cache/` (đã ignore). Luật ignore đo trong kho git TẠM mang đúng `.gitignore` của dự án với cấu hình
git cô lập khỏi máy (một ca gài luật ignore toàn cục giả để chứng minh không xanh giả); một ca tải bằng thư viện THẬT, chỉ thay
biên mạng. 31 đột biến đỏ đúng chỗ.
**Đo thêm (ngoại tuyến, wiley-tdm 1.2.0) và vá — PR y khoa #56, phiên tiếp nối:** (A) thư mục tải tự đặt trong repo; (B) thư
viện lùi thư mục có dấu chấm («wiley.pdfs») về thư mục MẸ; (C) đứt mạng giữa chừng ⇒ `STORAGE_ERROR` để lại tệp dở (4.009 byte),
lượt sau `EXISTING_FILE` «thành công» mà không gọi mạng; (D) rào `toan_van_guideline.py --luu` so CHUỖI đường dẫn ⇒ lọt khi sai
chữ hoa/thường trên macOS. Vá: hỏi chính git về thư mục THẬT trước mỗi lượt tải (`app/utils/tam_nhin_git.py`), git thấy ⇒ từ
chối; `thanh_cong` đòi tệp trông như PDF trọn vẹn; `--luu` so `samefile`. Hai quyết định bác sĩ chốt và 74 đột biến mới: xem
CLAUDE.md y khoa, mục Wiley TDM.
**Bài học:** (1) Bản giả của thư viện ngoài phải được đối chiếu với thư viện THẬT ít nhất một ca (không cần mạng) — test xanh
trên bản giả chỉ chứng minh mã khớp với bản giả. (2) Luật ignore không đi theo cấu hình: nơi ghi tự đặt phải hỏi git lúc ghi.
(3) «Tải được» ≠ «tệp trọn vẹn». **Ghi chú quy trình:** phiên vá #51 mở lúc chốt an toàn đang 🔴 giả (mục BH133 bổ sung ngay
trên); đã xác minh là đỏ giả (mọi tín hiệu thật của repo y khoa xanh) rồi mới làm, trong worktree ngoài OneDrive.
