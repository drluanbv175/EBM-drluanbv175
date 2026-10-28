# 28/10/2026 — Gói tuần W44 mất vì lượt lịch bị cắt ngang ở lệnh chưa được phép (BH173)

**Phát hiện:** `tools/kiem_lich_nen.py` báo 🔴 «goi-duyet-tuan-ebm kỳ 26/10/2026 18:30: thiếu queue/tuan-2026-W44.md», trong khi
`list_task_runs` ghi lượt 26/10 là «succeeded».

**Đo (bản ghi lượt `beafd9c1…`):** lượt chạy 73 giây ở chế độ quyền `default`. Bước 0 (`python3 tools/doc_ket_qua_rut_bai_kho.py`,
đã có trong allow) chạy được; lệnh kế `python3 tools/tu_de_xuat_viec.py` trả «Tool permission request failed: AbortError: Tool
permission stream closed before response received». Lượt dừng hẳn nhưng phiên vẫn ghi `lastTurnCutShort: true` và bộ lập lịch
ghi «succeeded». Đối chiếu 2.152 mục `permissions.allow` của `.claude/settings.local.json`: **16/17** lệnh của gói tuần chưa được
phép, 0 quyền ghi tệp. Hai tác vụ tháng cũng thiếu: `kiem-rut-bai-kho-thang` 2/3, `kiem-tra-hoan-thien-he-thong-thang` 7/7.
Bản vá quy trình 24/10 (mỗi lượt một lệnh, không `cd`/`ls`/`ps`) chỉ chữa phần lệnh ghép; lệnh đơn chưa có trong allow vẫn chết.

**Bác sĩ chọn (AskUserQuestion 28/10):** «Khai đúng lệnh» (không dùng chế độ Auto cho lượt lịch).

**Vá:**
- `sync/quyen-lich-nen.json` (đi qua git): mỗi tác vụ khai `lenh` (y như SKILL.md, «*» thay tham số), `khong_chay` (lệnh chỉ in cho
  bác sĩ), `ghi` (thư mục được Write/Edit). Ranh giới: không khai lệnh ghi quyết định thay bác sĩ hay `--ap-dung`. Tác vụ tháng
  kiểm tra hoàn thiện chỉ khai lệnh ĐO; bước sửa mã cố ý không khai.
- `tools/quyen_lich_nen.py`: `--kiem` (mọi lệnh backtick của SKILL.md phải được khai; mọi quy tắc khai phải có trên máy; không
  đúng nền tảng/thiếu tệp ⇒ ⚪ mã 2, không bao giờ «đủ») · `--ap-dung` (sao lưu `settings.local.json.bak-quyen-lich-*`, chỉ thêm).
- Giác quan ⑦f-bis trong `tu_de_xuat_viec.py`: báo 🔴 TRƯỚC kỳ (👤 lệnh mới chưa khai · 🤖 máy chưa áp).
- `tu_de_xuat_viec.py --phai-sinh-cu`: in tên dashboard có Word/bản đọc cũ — trước đó bước «xuất lại phái sinh» của gói tuần
  phải tự `ls`/`find` (bị chặn ở lượt lịch).
- SKILL.md gói tuần: lấy tóm tắt bằng `tools/tra_dinh_danh.py --pmids … --abstract` (thay «efetch» không có lệnh cụ thể); sao
  chép bằng Read rồi Write (không `cp`); ghi rõ luật quyền.

**Kiểm hồi quy:** `tools/test_quyen_lich_nen_20261028.py` (15 ca) + chốt **BH173**. 8 phép đột biến: 7 đỏ đúng chỗ; phép còn
lại (bỏ bước thay tham số «<…>» trước khi khớp) là đột biến tương đương — «*» của quy tắc khớp được cả «<W>» — nên đã gỡ hàm thừa.

**Sau khi gộp:** `python3 tools/quyen_lich_nen.py --ap-dung` trên Mac, chép SKILL.md gói tuần từ `sync/scheduled-tasks/` sang
runtime, rồi «Run now» tác vụ `goi-duyet-tuan-ebm` để bù W44 và đo đầu–cuối. Windows: tệp khai cho `darwin`; máy Windows báo ⚪.
