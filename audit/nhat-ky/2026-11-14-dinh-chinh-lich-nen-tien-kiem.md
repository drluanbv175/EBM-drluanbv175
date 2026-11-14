# 14/11/2026 — Đính chính PR #339 (lịch nền tiền kiểm + dấu vết): đỏ giả ở bước 4b, tiền đề sai, đường triển khai thật

Tệp gốc: `2026-11-14-lich-nen-tien-kiem-va-dau-vet.md` (PR #339, đã gộp 03:24Z, commit 0bc3ddc). Người duyệt độc lập nêu 5
vấn đề; đo lại cả 5 trên cây/máy thật — 4 vấn đề đúng và đã sửa, vấn đề 5 đúng nhưng là đánh đổi an toàn nên chờ bác sĩ chọn.

**Đo 14/11/2026 (chỉ đọc):**

1. `python3 tools/so_xac_minh_nguon.py --bao-cao` (cây chính) ⇒ mã 2, đầu ra chỉ có khối «✅ BẢN ĐÍNH CHÍNH bị rút — bác sĩ
   ĐÃ KÝ», không có khối 🔴 nào. Gốc: `bao_cao()` trả 2 khi `han` khác rỗng, mà `han` gồm cả ca đính chính đã ký. Bước 4b của
   PR #339 đọc «mã 2 không kèm `[MA] SO_HONG`» thành «CÓ NGUỒN ĐÃ BỊ RÚT» rồi ghi 🔴 vào `alerts/`. Từ kỳ 01/12, lượt tháng nào
   cũng sẽ ghi một cảnh báo đỏ giả. Đây là lỗi `chu_trinh_chung_cu.py` đã vá ngày 27/09 (BH122, họ BH115), nay tái phát.
2. Tiền đề «chưa có nhịp làm mới định kỳ» là SAI. Tác vụ `kiem-rut-bai-kho-thang` (ngày 4) là owner DUY NHẤT của việc tái kiểm
   (SKILL của nó ghi «không nối trùng»). Tác vụ này chạy `chu_trinh_chung_cu.py --vong 3`, gồm `so_xac_minh_nguon --vong 3`,
   `--quet-ledger` và `--phu-mo-coi`. `state/kiem-rut-bai-kho.log` có dòng KẾT THÚC ngày 24/10, 25/10, 02/11 và 04/11. Phần
   tồn đọng của sổ thuộc `[MA] CAN_XEM_TAY` và `[MA] CAN_NCBI_API_KEY`; chạy thêm `--vong 3` không gỡ được các mục này.
3. Với tác vụ `kiem-tra-hoan-thien-he-thong-thang`, `kiem_lich_nen` in «⚪ không đọc được state/… (bản sao trần/máy khác)»
   ngay trên máy chạy lịch. Tệp log chỉ được tạo khi `--bat-dau` chạy thành công. Nếu chính lệnh đó bị cắt vì chưa áp quyền,
   cảm biến sẽ đứng ở ⚪ mãi.
4. Đường triển khai thật là TỰ ĐỘNG, không phải bác sĩ chép tay như PR #339 viết. Hook SessionStart gọi
   `tu_sua_chua --ap-dung`. Bước `day_do_song_cloud --ap-dung` tua nhanh master (`merge --ff-only`), sau đó bước
   `dong_bo_tac_vu_lich --ap-dung` chép sang runtime. Đo bằng nguồn PR: cả hai tác vụ đều «🟡 tụt hậu (tự chép được)».
   Quyền còn thiếu trên máy (so `settings.local.json`, chỉ đọc, theo tệp khai sau đính chính): tác vụ tháng thiếu 3 quy tắc
   (`quyen_lich_nen --tac-vu …`, `kiem_lich_nen`, `xuat_goi_cap_nhat … --khong-endnote`); tác vụ kỹ thuật thiếu 2 quy tắc
   (`ghi_dau_vet_lich … --bat-dau` / `--ma *`).

**Vá (nhánh `claude/lich-nen-tien-kiem-20261114`, các commit sau khi gộp):**

- GỠ bước 4b khỏi `cap-nhat-thang-ebm`, kèm lệnh của nó trong `sync/quyen-lich-nen.json`. SKILL nay trỏ owner ngày 4, và việc
  phân xử mã 2 chỉ còn ở `chu_trinh_chung_cu` (đã tách đúng ca đính chính đã ký).
- `kiem_lich_nen`: thêm `dau_vet.tu_ngay`. Kỳ trước mốc không xét bằng log. Máy CÓ bản chạy (`~/.claude/scheduled-tasks/<id>/`)
  mà thiếu log từ mốc ⇒ 🔴 kỳ lỡ. Máy không có bản chạy ⇒ ⚪ với nhãn đúng. Sổ kỳ vọng khai mốc `2026-12-03` cho tác vụ kỹ thuật.
- `dong_bo_tac_vu_lich`: thêm phân loại `cho_quyen`. Bản chạy tụt hậu nhưng `quyen_lich_nen --tac-vu` của SKILL mới chưa 🟢
  (tập quyền lấy từ lệnh tiền kiểm trong SKILL, nếu không có thì lấy khoá tác vụ) ⇒ GIỮ bản cũ và báo 👤. Không đo được quyền ⇒
  cũng giữ. Tác vụ không có hợp đồng quyền, hoặc khai cho nền tảng khác ⇒ chép như cũ.
- Test `tools/test_lich_nen_dinh_chinh_20261114.py`: dùng đầu ra THẬT của `bao_cao()` trên sổ fixture có một đính chính đã ký,
  đưa qua phân xử thật của `chu_trinh` ⇒ không sinh 🔴. Chốt BH173 thêm (8)–(10).

**Việc của bác sĩ (NGAY):** PR #339 đã nằm trong master. Phiên Mac kế tiếp sẽ tự chép hai SKILL mới bằng `dong_bo_tac_vu_lich`
BẢN CŨ, bản chưa có cổng quyền. Vì vậy bác sĩ cần chạy `python3 tools/quyen_lich_nen.py --ap-dung` TRƯỚC phiên Mac kế tiếp hoặc
trước 01/12, rồi kiểm `--tac-vu cap-nhat-thang-ebm,goi-duyet-tuan-ebm` và `--tac-vu kiem-tra-hoan-thien-he-thong-thang` đều ra 🟢.
Nếu chưa áp: ở chế độ quyền default, lượt tháng bị cắt ngay lệnh đầu của bước 0, nên mất cả lượt thu thập an toàn thuốc.

**Chưa kết luận — chế độ auto:** `quyen_lich_nen` chỉ so danh sách allow TĨNH trong `settings.local.json`. Ở chế độ
`defaultMode=auto`, bộ phân loại có thể cho chạy lệnh không có trong allow: lượt kỹ thuật 03/11 đã chạy gh/pytest. Như vậy mã 1
có thể là DỪNG OAN. Nhưng 24/10 cũng có lượt lịch chết vì hỏi quyền khi đang ở Auto. Chưa có phép đo phân xử hai điều này.

**Vấn đề 5 — chờ bác sĩ chọn (KHÔNG sửa trong lượt này):** bước 0 hiện gộp cả quyền của bước 5 (gói duyệt) và bước 6 (phiếu
EndNote). Chỉ thiếu một quy tắc đóng gói (ca đo 14/11: `--khong-endnote`, thuộc bước 5) là mất cả bước 2–3 thu thập an toàn
thuốc. Lý lẽ «chạy dở thì watermark/con trỏ dịch mà gói không ra» chỉ đúng với con trỏ quét của bước 5. Với bước 2–3, chạy xong
mà watermark dịch là hợp lệ. Có hai phương án:
(A) giữ nguyên: thiếu bất kỳ quyền nào của bước 0–6 thì dừng cả lượt. Đơn giản, gói không bao giờ dở dang.
(B) tiền kiểm hai pha: bước 0 chỉ chặn theo lệnh của bước 1–4. Ngay trước bước 5 chạy `--tac-vu goi-duyet-tuan-ebm` (cộng lệnh
bước 6); thiếu quyền thì chỉ dừng bước 5–6, ghi alerts, và giữ kết quả thu thập an toàn thuốc. Cần tách khoá con trong
`quyen-lich-nen.json`, sửa chốt BH173 (6) và test thứ tự bước.
