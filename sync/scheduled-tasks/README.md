# Nguồn cứu hộ SKILL của tác vụ lịch (scheduled-tasks)

Bản chạy thật nằm NGOÀI cây OneDrive: `~/.claude/scheduled-tasks/<tên>/SKILL.md`
— app dọn runtime là mất trắng (đã xảy ra với skill thường, đo 13/08: 20/22 lệch bản).
Thư mục này là BẢN SAO NGUỒN trong OneDrive để (a) không mất khi runtime bị dọn,
(b) máy Windows chép sang được. Chiều đồng bộ: nguồn git → runtime, KHÔNG chép ngược.
Đồng bộ: `python3 tools/dong_bo_tac_vu_lich.py` (đo) · `--ap-dung` (chép bản tụt hậu, sao lưu trước; GIỮ bản cũ khi quyền
của SKILL mới chưa 🟢 — trạng thái `cho_quyen`). `dong_bo_skill.py` KHÔNG quản nhánh này.
Thư mục `goi-duyet-tuan-ebm/` không còn là tác vụ lịch (13/11/2026) — là QUY TRÌNH mà tác vụ tháng `cap-nhat-thang-ebm` đọc.
Cần bác sĩ kiểm chứng.

## Chạy được trên Mac lẫn Windows (28/09/2026)
Mỗi SKILL mở đầu bằng ĐÚNG MỘT khối nền tảng:
- `NỀN TẢNG: macOS + Windows` — thư mục làm việc cho cả hai máy (`$HOME/Library/CloudStorage/OneDrive-Personal/Claude AI`
  · `%USERPROFILE%\OneDrive\Claude AI`), quy tắc đổi `python3` → `py -3` và venv; tệp tạm vào `state/`, không `/tmp/`.
- `NỀN TẢNG: CHỈ CHẠY TRÊN MAC` — chỉ khi tác vụ gọi script bash (`*.sh`); Windows DỪNG và báo.
Không viết cứng `/Users/<tên>` hay `/tmp/`. Kiểm: `python3 tools/kiem_tac_vu_lich_da_nen.py` (Windows `py -3 …`); chốt BH130.
Sau khi sửa ở đây, chép lại bản runtime `~/.claude/scheduled-tasks/<tên>/SKILL.md` trên TỪNG máy.

## Quy ước soạn SKILL tác vụ lịch (14/11/2026)
Lượt lịch chạy ở chế độ quyền «default» và KHÔNG có ai bấm «cho phép»: lệnh nào chưa được phép là lượt bị CẮT NGANG mà bộ
lập lịch vẫn ghi «succeeded» (gói tuần W44 mất 26/10/2026; lượt kỹ thuật tháng vấp `gh`/`git`/`cd … &&` 14/11/2026). Vì vậy:

1. **Mỗi lần gọi Bash = MỘT lệnh đơn, chạy từ gốc THƯ MỤC LÀM VIỆC.** Không `cd …`, không nối `&&` `||` `;` `|` `&`, không
   chuyển hướng `>` `2>&1`. Lệnh cho repo y khoa viết `git -C medical-ebm-automation …` hoặc đường dẫn
   `medical-ebm-automation/tools/…`. Claude Code xét quyền TỪNG lệnh con của một chuỗi ghép — một quy tắc khai không phủ được
   chuỗi ghép, kể cả khi trùng chữ (phép dò `tools/quyen_lich_nen.py` báo «LỆNH GHÉP»; chỉ miễn ở `khong_chay`).
2. **Mọi lệnh phải khai Y NHƯ trong SKILL** ở `sync/quyen-lich-nen.json` (khoá = tên thư mục tác vụ; «*» thay tham số; chỗ
   điền trong SKILL viết `<…>`). Phép dò xét mọi lệnh trong dấu huyền bắt đầu bằng `python3`, `~/.ebm-venv/bin/python`,
   `bash`, `git`, `gh` hoặc `cd` — **`git`/`gh` cũng phải khai**. Lệnh SKILL chỉ IN cho bác sĩ tự chạy ⇒ `khong_chay`. Không
   khai lệnh ghi quyết định thay bác sĩ (`_ranh_gioi`: `--ap-dung`, `approve_gate`, `ghi_vuot_qua_da_xet`… — chốt BH173 chặn).
   Thêm lệnh vào SKILL ⇒ khai trong CÙNG PR; bác sĩ chạy `python3 tools/quyen_lich_nen.py --ap-dung` (chỉ thêm, sao lưu trước).
3. **Câu mô tả không gõ nguyên văn phải có «…»** (vd lời dặn «không thêm `cd … &&`») — phép dò bỏ qua mẫu mô tả với
   `git`/`gh`/`cd`; lệnh có chỗ điền `<…>` vẫn là lệnh thật, vẫn phải khai.
4. **Đọc/tìm tệp bằng công cụ Read/Grep**, không gõ `cat`/`grep`/`ls`/`find` qua Bash. Ghi tệp bằng Write/Edit chỉ vào thư mục
   khai ở `ghi` của tác vụ.
5. **Bước 0 tiền kiểm** — trước mọi lệnh việc (chỉ sau lệnh ghi dấu vết BẮT ĐẦU nếu tác vụ có):
   `python3 tools/quyen_lich_nen.py --tac-vu <tên>[,<quy trình nó thi hành>]`. Mã 1 (thiếu quyền/lệnh chưa khai) hoặc mã 2 (không
   đo được) ⇒ DỪNG LƯỢT NGAY, ghi một dòng `alerts/<ngày>.md`, báo lệnh `--ap-dung` cho bác sĩ. Windows bỏ qua (hợp đồng quyền
   chỉ khai cho macOS). Chốt BH173 (13) đòi điều này cho MỌI tác vụ trong `sync/lich-nen-ky-vong.json`.
6. **Dấu vết máy-đọc-được** — mỗi tác vụ trong `sync/lich-nen-ky-vong.json` để lại dấu vết mà `tools/kiem_lich_nen.py` đọc.
   Dòng «KẾT THÚC» theo hợp đồng mã `MA_TRON`: 0 sạch · 1 đi hết, có việc cho bác sĩ · 2 có phần KHÔNG đo được/không chạy được
   (⇒ 🟠 «lượt không trọn»); «tổng thể=PASS»/«tổng thể=CÓ BƯỚC LỖI» cho script launchd. Dừng ở bước 0 thì KHÔNG ghi KẾT THÚC.
   Không bao giờ tự gõ dòng log bằng Write/Edit (dấu vết tự khai giờ là dấu vết giả).
7. **Lệnh chạy lâu** (chu trình chứng cứ, bộ thu thập) ⇒ gọi Bash với `run_in_background: true` rồi ĐỢI thông báo hoàn tất.
8. **Bỏ một tác vụ lịch** ⇒ trong CÙNG PR: xoá thư mục `sync/scheduled-tasks/<tên>/` (trừ khi còn là quy trình), gỡ khỏi
   `sync/lich-nen-ky-vong.json` và khoá ở `sync/quyen-lich-nen.json` (trừ khoá quy trình), và thêm MỘT dòng vào
   `TAC_VU_LICH_DA_BO` trong `tools/verify_claude_code_repo_alignment.py`, trỏ tệp nhật ký `audit/nhat-ky/…` ghi lời bác sĩ.
   Chốt `doctrine_tac_vu_lich` (pre-commit) chặn CLAUDE.md/AGENTS.md còn gọi tên đó là tác vụ.
