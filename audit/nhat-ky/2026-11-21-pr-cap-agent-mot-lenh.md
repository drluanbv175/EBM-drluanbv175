# 21/11/2026 — PR cặp agent gốc → y khoa: nhắc lúc commit + dựng một lệnh (ý tưởng mượn từ research-superpowers, KHÔNG cài plugin)

**Bối cảnh.** Bác sĩ hỏi plugin `leiverkus/research-superpowers` có giúp hệ nghiên cứu và cập nhật chứng cứ không; sau đánh giá,
bác sĩ chốt «Thực hiện giúp tôi; Nếu Plugins không có giúp nâng cấp hệ thống thì không cài». Kết luận đánh giá (21/11):

- Plugin dành cho thần học / khảo cổ / sử / nhân văn số.
- Cổng của plugin là SOFT-GATE (ghi lý do vượt, không chặn).
- Ba skill trùng chủ đã có ở §1.1 (tổng quan, viết bản thảo, bình duyệt).
- Plugin khuyên dùng MCP bên thứ ba.
- Hai hook SessionStart thêm, 18 skill chiếm ngân sách danh sách.

⇒ **không cài**. Chỉ dựng lại MỘT ý tưởng có ích: kiểm lệch theo TRẠNG THÁI, im lặng khi không đổi.

**Sự cố gốc (BH107, 20/11/2026).**
- PR gốc #454 (sửa `cap-nhat-guideline.md`) và #456 (sửa `_CONNECTOR-CHUNG-CU.md`) gộp mà không có PR cặp ở repo y khoa.
  Bản sao y khoa dạy agent «cổng nguồn chính thức chỉ cảnh báo» trong khi cổng đã CHẶN.
- BH107 chỉ đỏ ở lượt chốt hồi quy nền khoảng 6 giờ sau. PR cặp y khoa #351 làm tay 5 bước: chép → sinh manifest → dán SHA vào
  `MANIFEST_SELF_CHECK_SHA256` → `--check` → commit có `EBM_WORKSPACE_ROOT`.
- Hôm sau (21/11) hook vẫn báo «BH107 tái phát» và hòm việc báo «2 lệch — đồng bộ bằng PR CẶP», dù #351 đã gộp: cây y khoa trên máy
  sau origin 5 commit. Làm theo dòng đó sẽ mở PR TRÙNG.

**Vá.**
1. `tools/dong_bo_agent_y_khoa.py` phân loại từng agent theo ba bản: HEAD gốc · `origin/<nhánh y khoa>` · cây y khoa trên máy.
   - Bốn nhóm: `can_pr_cap` · `can_keo_cay` · `chi_goc` · `khop`.
   - `--ap-dung [--mo-pr]` dựng PR cặp trong worktree mới ở `~/.ebm-worktrees`.
   - Chỉ chép bản ĐÃ COMMIT, không bao giờ chép agent chỉ-gốc, không tự gộp.
2. `.githooks/pre-commit` (gốc) gọi `--staged`: agent đang stage khác bản origin y khoa ⇒ NHẮC kèm lệnh.
   - Luôn mã 0 (PR cặp đi sau PR gốc là bình thường).
   - Không gọi mạng.
3. `tu_de_xuat_viec.giac_quan_agent_lech(…, doc_origin=…)` tách hai dòng:
   - «cần PR cặp» ⇒ chạy công cụ trên;
   - «origin đã trùng, cây chưa kéo» ⇒ `git pull --ff-only`, mức ưu tiên 3.
   Đọc origin lỗi ⇒ vẫn báo cần PR cặp (không giấu lệch).

**Kiểm.**
- `tools/test_dong_bo_agent_y_khoa_20261121.py`: 6 test, repo git tạm, origin giả bằng `update-ref`.
- Năm đột biến đều đỏ rồi xanh lại: đảo điều kiện kéo cây · bỏ im lặng khi trùng origin · chép bản worktree thay HEAD · bỏ kiểm
  đếm hằng SHA · giác quan bỏ origin.
- Đột biến «bỏ im lặng» lần đầu KHÔNG bị bắt. Lỗi nằm ở phép thử: fixture stage trùng HEAD nên hàm trả về sớm. Đã sửa fixture
  (HEAD ≠ origin, stage = origin) và có assert «phải CÓ tệp stage».
- Chạy thật 21/11: 99 tệp, 0 cần PR cặp, 0 cần kéo cây (cây y khoa đã được kéo).

CLAUDE.md không thêm dòng (còn 5 ký tự ngân sách). Hướng dẫn nằm trong chính thông điệp của chốt pre-commit và hòm việc.
