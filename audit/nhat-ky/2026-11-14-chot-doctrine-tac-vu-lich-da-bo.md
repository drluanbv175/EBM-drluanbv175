# 14/11/2026 — Chốt máy: doctrine không được nhắc tác vụ lịch đã bỏ

**Bối cảnh:** hướng hoàn thiện (1) sau tầng 1–2; bác sĩ trả lời «Tiếp tục» lúc 12:08 ngày 14/11/2026.
Bổ sung cho `2026-11-14-claude-md-loi-thoi-kiem-thang.md`.

**Lỗi gốc:** quyết định 13/11 bỏ 6 tác vụ lịch:
- `2026-11-13-gop-lich-nen-mot-tac-vu-thang.md`;
- `2026-11-13-bo-tac-vu-kiem-thang-diem-quy.md`.

Hai dòng CLAUDE.md vẫn gọi tên các tác vụ đó:
- §1(c): «tác vụ lịch `goi-duyet-tuan-ebm`», sửa ở #336;
- §10: «tác vụ `kiem-thang-diem-quy`», sửa ở #334.

Không chốt nào bắt được. Chỉ lượt kiểm tháng đọc bằng mắt mới thấy.

**Vá:** thêm phép kiểm `doctrine_tac_vu_lich` vào `tools/verify_claude_code_repo_alignment.py`. Phép kiểm chạy ở pre-commit, quét CLAUDE.md và AGENTS.md gốc.

Tập tên CÒN SỐNG gồm thư mục `sync/scheduled-tasks/*` có `SKILL.md`, cộng `id` trong `sync/lich-nen-ky-vong.json`. Ba luật:
1. Tên đứng sau cụm «tác vụ …» phải còn sống, và không nằm trong `TAC_VU_LICH_DA_BO`.
2. Đường dẫn `scheduled-tasks/<tên>` phải trỏ tới thư mục có thật.
3. Tên đã bỏ hẳn (không còn thư mục, không có trong sổ) thì cấm nhắc ở bất cứ đâu.

`goi-duyet-tuan-ebm` vẫn được nhắc khi gọi đúng là QUY TRÌNH. Thư mục của nó còn, vì tác vụ tháng đọc tệp đó.

Mỗi tên trong `TAC_VU_LICH_DA_BO` dẫn tới tệp nhật ký ghi lời bác sĩ. Test đòi tên có mặt trong đúng tệp đó.

**Kiểm:**
- 15 test ở `tools/test_verify_doctrine_tac_vu_lich_20261114.py`.
- Hai tập check kỳ vọng cập nhật thêm `doctrine_tac_vu_lich`.
- Đột biến 12/12 đỏ đúng chỗ. Mỗi phép sao lưu `cp -p` rồi `cmp` khớp sau khi khôi phục.
- Chạy trên bản CLAUDE.md trước #334 và trước #336: FAIL, chỉ đúng dòng 28 và 199. Bản hiện tại: PASS.

**Luật khi bỏ tác vụ về sau:** thêm một dòng vào `TAC_VU_LICH_DA_BO` trong CÙNG PR xoá thư mục `sync/scheduled-tasks/<tên>/`. Nếu quên, luật 1 vẫn bắt câu «tác vụ … `<tên>`», vì tên không còn sống.
