# 14/11/2026 — Tác vụ kỹ thuật tháng có lệnh ghép và git/gh lọt khỏi khai quyền (BH173 mở rộng)

**Mã:** BH173 (mở rộng, mục 11–12). Tiếp nối `2026-11-14-lich-nen-tien-kiem-va-dau-vet.md` và
`2026-11-14-dinh-chinh-lich-nen-tien-kiem.md` (bước 0 tiền kiểm của tác vụ tháng `cap-nhat-thang-ebm`, #339/#342).

## Hiện trạng đo được (14/11/2026)

- `sync/scheduled-tasks/kiem-tra-hoan-thien-he-thong-thang/SKILL.md` chứa 11 lệnh Bash không có trong
  `sync/quyen-lich-nen.json`: `gh run list …`, `git worktree list`, `git branch --show-current`, `git status`, `git fetch`,
  `git push`, `git branch -a --sort=-committerdate | head -20` và bốn chuỗi `cd medical-ebm-automation && …` (fetch + status,
  pytest dây nối, pytest chọn lọc, `list_studies.py`).
- `python3 tools/quyen_lich_nen.py` vẫn báo «🟢 đủ» cho tác vụ này: phép dò `_LENH_RE` chỉ nhận lệnh trong backtick bắt đầu bằng
  `python3`/`~/.ebm-venv/bin/python`/`bash`. Chốt BH173 dùng cùng phép dò nên cũng xanh.
- Claude Code xét quyền TỪNG lệnh con của `a && b`/`a | b`/`a; b` ⇒ một mục `Bash(...)` không bao giờ cho cả chuỗi chạy. Lượt lịch
  không có ai bấm «cho phép» ⇒ bị cắt ngang ngay lệnh đầu tiên như vậy (`git branch --show-current` ở phần mở đầu), cảm biến
  `kiem_lich_nen` chỉ thấy «BẮT ĐẦU thiếu KẾT THÚC» SAU khi kỳ 03/12 đã hỏng.
- SKILL còn dặn lượt lịch tự sửa tệp, commit và `git push` — đúng các bước mà `_ghi_chu` của khoá khai nói «cố ý KHÔNG khai».
- Máy Mac (đo chỉ đọc `settings.local.json`): 17/24 quy tắc của khoá mới chưa áp, kể cả hai lệnh ghi dấu vết từ #339/#342.

## Cách vá

1. `tools/quyen_lich_nen.py`: phép dò nhận thêm đầu lệnh `git`/`gh`/`cd`; hàm mới `ly_do_ghep()` (tách bằng `shlex` giữ nháy,
   «<…>» là chỗ điền) coi `&&`, `||`, `|`, `;`, `&`, `>`/`<`, `(`/`)` và `cd` đầu lệnh là LỆNH GHÉP ⇒ luôn vào `thieu_khai`, kể cả
   khi trùng chữ một mục `lenh` (mục `lenh` có toán tử cũng bị báo). Chỉ miễn khi khai ở `khong_chay` (lượt không gõ). Backtick
   có «…» với đầu lệnh mới là mẫu mô tả (vd lời dặn «không thêm `cd … &&`» của SKILL gói duyệt) ⇒ không xét. Ngoài khoá đã khai,
   xét cả tác vụ đang chạy theo `sync/lich-nen-ky-vong.json` (thiếu khoá ⇒ mọi lệnh «chưa khai»). Khuôn trả về giữ ba khoá cũ
   (test cũ so khớp cả dict).
2. SKILL kỹ thuật: mọi lệnh thành MỘT lệnh đơn chạy từ gốc (`git -C medical-ebm-automation …`,
   `medical-ebm-automation/tools/…` — hai công cụ tự tìm gốc theo `Path(__file__)`, đo chạy được từ gốc); thêm BƯỚC 0
   `python3 tools/quyen_lich_nen.py --tac-vu kiem-tra-hoan-thien-he-thong-thang` ngay sau BẮT ĐẦU — mã 1/2 ⇒ ghi KẾT THÚC mã 2 rồi
   DỪNG; Windows bỏ qua (khai chỉ cho darwin, cùng cách `dong_bo_tac_vu_lich` coi là «không áp»); khối QUY TẮC CHẠY LỆNH; lượt
   lịch KHÔNG tự sửa/commit/push mà ghi «🛎 việc sửa cho phiên có người».
3. Hồi quy dây nối `tests/test_approve_gate_quality_gate_wiring_20260824.py`: KHÔNG khai cho lượt lịch — tên tệp chứa
   `approve_gate`, rào «lệnh ghi quyết định» của BH173 (và test `test_khai_khong_chua_lenh_ghi_quyet_dinh_thay_bac_si`) chặn
   đúng chuỗi đó; không nới rào. Lượt lịch đọc CI repo y khoa (chạy trọn bộ test hermetic, gồm tệp này); phiên có người chạy
   trực tiếp (khai ở `khong_chay`). Thử `pytest medical-ebm-automation/tests -k …` từ gốc: lỗi thu thập ở một tệp test phụ thuộc
   thư mục chạy (tệp đó xanh khi chạy trong repo y khoa) ⇒ không dùng.
4. Đồng bộ runtime: `dong_bo_tac_vu_lich.cong_quyen` đọc tập `--tac-vu` từ SKILL nguồn ⇒ giữ bản chạy cũ tới khi quyền 🟢.

## Kiểm hồi quy

- Test mới `tools/test_tien_kiem_ky_thuat_20261114.py` (27 test); 301 test lịch nền/quyền liên quan xanh; chốt tổng
  `chot_hoi_quy_bai_hoc.py` mã 0.
- Kiểm đột biến 16 phép (sao lưu + `cmp` khớp sau mỗi phép): 16/16 làm test pytest đỏ đúng chỗ; chốt BH173 bắt 15/16 (phép còn
  lại chỉ đổi lời in, test pytest bắt). Hai phép đầu (bỏ phát hiện toán tử, bỏ luật `cd`) lúc đầu lọt chốt BH173 vì phép dựng
  (11) chỉ dùng lệnh git chưa khai — đã sửa phép dựng: khai trùng chữ các lệnh ghép để chỉ luật lệnh ghép bắt được.

## Việc của bác sĩ

Sau khi gộp: `python3 tools/quyen_lich_nen.py --ap-dung` (thêm 17 quy tắc của khoá kỹ thuật + các quy tắc còn thiếu khác), rồi
`python3 tools/quyen_lich_nen.py --tac-vu kiem-tra-hoan-thien-he-thong-thang` phải 🟢 trước kỳ 03/12/2026.

Cần bác sĩ kiểm chứng.
