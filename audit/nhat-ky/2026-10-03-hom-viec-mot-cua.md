# 03/10/2026 — Hòm việc một cửa, PR chờ gộp, quyết định thẻ tuần (HV-02 · HV-04 · EV-10, BH154)

**Số đo (kiểm toàn diện 02/10).**
- **HV-02.** 986 sự kiện SessionStart trong nhật ký phiên: chứa «TỰ ĐỀ XUẤT VIỆC» = 0, nhắc cổng/PR = 0. Bảng tự đề xuất chỉ hiện
  khi có người nhớ mở, và chìm trong ~7 KB banner.
- **HV-04.** 11 PR mở mà không cảm biến nào đếm (`tu_de_xuat_viec` chỉ gọi `gh run list` cho CI).
- **EV-10.** 7 gói tuần, 49 thẻ có PMID, 0 quyết định được ghi lại; quyết định nằm trong chat.

**Vá.**
- **`tools/hom_viec_mot_cua.py`.**
  - `--doc` đọc bảng sinh sẵn `state/hom-viec.json` và in ≤ 12 dòng: 👤 trước theo ưu tiên, rồi 🛎; 🤖 chỉ đếm ở dòng đầu.
  - Còn giác quan chết ⇒ không bao giờ in «🟢 không có việc».
  - `--lam-moi-nen` (hook): bảng vắng hoặc cũ hơn 12 giờ ⇒ phóng lượt làm mới tách tiến trình, có khoá chống chạy chồng.
  - Đo 0,09 giây, không gọi mạng. Bảng đầy đủ mất ~12 giây nên không chạy trực tiếp trong hook.
- **`tools/tu_de_xuat_viec.py`.** Thêm `--json` (bảng dạng máy đọc) và hai giác quan:
  - ⑫ **PR chờ gộp.** Gọi `gh pr list` cho cả hai repo, báo CI xanh/đỏ/đang chạy, tuổi PR cũ nhất, PR XẾP CHỒNG (base không phải
    nhánh mặc định). Bỏ PR nháp. gh không trả lời ⇒ ⚪, không phải «0 PR». Trên Cloud ⇒ ⚪.
  - ⑬ **Thẻ tuần chưa quyết.** Chỉ xét gói mới nhất, tuổi từ 3 đến 21 ngày.
- **`tools/ghi_duyet_the_tuan.py`.** CHỈ GHI ĐÚNG lời bác sĩ, vd «duyệt W40: 1 ✓ 3 ✗ 5 hoãn», vào `state/duyet-the-tuan.jsonl`.
  - Thẻ không có trong gói, thẻ nêu hai lần trong một câu, hoặc câu thiếu tuần ⇒ TỪ CHỐI, không đoán.
  - Chạy thử là mặc định. Không đổi decision/gradeLevel nào.
- **Phần còn lại.** `intent.py` định tuyến «hòm việc / việc chờ tôi / cần tôi xác nhận» và «duyệt thẻ / quyết định thẻ tuần».
  Hook nguồn `sync/hooks-sessionstart.json` thêm lệnh `hom_viec_mot_cua.py --doc --lam-moi-nen`; BÁC SĨ áp dụng bằng
  `python3 tools/dong_bo_hook_sessionstart.py --ap-dung`. CLAUDE.md §9; BH154.

**Đo sống** (symlink tạm tới dữ liệu thật, đã gỡ):
- `tu_de_xuat_viec --json` đo 20/20 giác quan.
- Giác quan PR in «13 PR chờ bác sĩ gộp — gốc #75 #76 #89–#96 · y khoa #62 #68 #69 (CI xanh 12/13, đang chạy 1; cũ nhất 38 giờ);
  XẾP CHỒNG: #93→claude/cong-mien-chan-401-20261002».
- Giác quan thẻ tuần in «7/7 thẻ gói tuan-2026-W40 chưa ghi quyết định (4 ngày)».
- Hòm việc in 9 dòng.
- Ghi thẻ chạy thử trên gói W40 thật: đúng 3 quyết định; W40-09 bị từ chối; thẻ nêu hai lần bị từ chối.

**Kiểm.**
- 22 test, 7 đột biến đều bị bắt. Lần đầu lọt «🤖 chiếm dòng», vì ca thử quá nhiều việc bác sĩ che mất; đã thêm ca ít việc.
- Đột biến «bỏ khoá» đã phóng THẬT một lượt làm mới nền ghi `state/hom-viec.json` của worktree. Đó đúng là hành vi test chặn;
  tệp đã dọn.
- Test bắt một lỗi thật: `SO.relative_to(REPO)` văng khi sổ nằm ngoài repo.
- `pytest tools/` 2083 đạt; `orchestrator/tests` 181; chốt 🟢; `kiem_tuong_thich_da_nen` 🔴 0.
