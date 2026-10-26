# 27/10/2026 — Bản in JATS vẫn bỏ khai báo kiểu JAMA (thẻ `<p>` thẳng trong `author-notes`)

**Phát hiện.** Khi sửa AMSTAR-2 mục 16 cho PMID 42842238 (JAMA Cardiology), agent thấy XML có đủ «Conflict of Interest
Disclosures», «Funding/Support», «Role of the Funder/Sponsor», nhưng `van_ban.txt` (từ bản in) không có. Bản vá 26/10/2026
(`_khai_bao_tac_gia`, PR #263) chỉ in con `fn` của `author-notes`; JAMA đặt các khai báo này bằng `<p>` thẳng trong `author-notes`
(kèm `<title>Article Information</title>`), không bọc `fn`. Đo kho: 22 XML có `<p>` trực tiếp trong `author-notes`.

**Cách vá.** In cả `fn` và `p` là con trực tiếp của `author-notes`; vẫn bỏ `corresp` (địa chỉ liên hệ) và `title` (đã có đề mục
riêng «Author notes and funding (article metadata)»).

**Kiểm hồi quy.** `test_jats_giu_khai_bao_dang_p_trong_author_notes_kieu_jama`: 2 đột biến (bỏ `p` · in cả `title`) đều đỏ đúng
chỗ rồi xanh lại; 12 test đạt; ruff sạch.

**Việc kèm theo.** In lại bản in của 22 XML này và thay bản đính kèm EndNote theo cách đã làm ở lần trước (sao lưu ngoài OneDrive,
so mã băm trước khi ghi đè, giữ khoá ghi EndNote). Ghi chú giấy phép: XML JAMA ghi CC BY-NC-ND không cho TDM/huấn luyện AI;
JAMA đã có trong sổ uỷ quyền của bác sĩ (`EBM-Dashboards/dieu-khoan-bac-si-uy-quyen.json`).
