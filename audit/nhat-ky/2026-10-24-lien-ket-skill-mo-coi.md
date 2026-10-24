# 24/10/2026 — Gỡ skill nguồn để lại liên kết treo ở runtime ⇒ BH44 đỏ

**Hiện tượng.** Sau khi gộp #236 (bác sĩ quyết gỡ plugin aipoch, gỡ `sync/skills/dieu-phoi-aipoch`), lượt chốt hồi quy
nền trên HEAD 9530c85 đỏ: BH44 «Điều phối agent phải sạch» — `kiem_dieu_phoi` ③ «1 skill runtime KHÔNG CÓ NGUỒN». Đài
hoàn thiện báo N-CHOT ĐỎ.

**Nguyên nhân.** `~/.claude/skills/dieu-phoi-aipoch` và `~/.codex/skills/dieu-phoi-aipoch` là liên kết trỏ vào nguồn
vừa gỡ (treo). `dong_bo_skill_claude_codex.py` chỉ đi theo skill NGUỒN đang có (`ensure_link`) nên không bao giờ thấy
liên kết của skill đã gỡ — hook SessionStart chạy `--ap-dung` mỗi phiên vẫn để nguyên.

**Vá.** `don_lien_ket_mo_coi()` — gỡ ĐÚNG liên kết (`LK.go`, không đụng dữ liệu) khi đích nằm trong nguồn và không còn
tồn tại; thư mục thật, liên kết còn sống, liên kết treo trỏ nơi khác giữ nguyên; chạy khô chỉ báo «MO_COI» (mã 1).

**Kiểm.** `tools/test_dong_bo_skill_lien_ket_mo_coi_20261024.py` 3 ca; 27 ca đồng bộ skill cũ xanh. Đột biến: bỏ điều kiện
«trỏ vào nguồn» ⇒ 2 đỏ · bỏ «đích không còn» ⇒ 2 đỏ · bỏ phép gỡ ⇒ 1 đỏ; phục hồi ⇒ xanh.

**Bài học.** Gỡ một skill khỏi `sync/skills/` là thay đổi hai phía: nguồn và runtime. Công cụ đồng bộ phải đối chiếu cả
chiều ngược (runtime → nguồn), không chỉ nguồn → runtime.

**Lớp thứ hai (đo lại sau khi gỡ hai liên kết, BH44 vẫn đỏ).** Runtime Cowork
(`~/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/…/skills/`) giữ một BẢN THẬT của
`dieu-phoi-aipoch` — bản đó đến từ bộ skill TÀI KHOẢN claude.ai mà bác sĩ đã tải lên; app chép lại nếu xoá trên máy, chỉ
bác sĩ gỡ được (claude.ai → Settings → Skills). Gợi ý «cứu: cp -R … sync/skills/» của `kiem_dieu_phoi` là làm NGƯỢC
quyết định gỡ. Vá: `SKILL_DA_GO_CHO_TAI_KHOAN` (khai báo kèm lý do, cùng kiểu `SKILL_DUNG_SAN`) + `phan_loai_runtime()` —
skill đã gỡ có chủ ý còn ở runtime ⇒ dòng 👤 cho bác sĩ, không 🔴; skill lạ không nguồn vẫn đỏ; skill trở lại nguồn thì
không còn là «đã gỡ». Test 3 ca; 2 đột biến bị bắt.
