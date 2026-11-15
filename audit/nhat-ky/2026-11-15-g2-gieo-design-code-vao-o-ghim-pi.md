# 15/11/2026 — G2 gieo thiết kế máy suy vào ô «bác sĩ ghim» ⇒ G1 chạy lại tự gỡ cờ thiết kế mơ hồ

**Phát hiện:** thẩm định đối kháng PR y khoa drluanbv175/medical-ebm-automation#277. Tái hiện được bằng orchestrate thật.

**Nguyên nhân:**
- `run_g2_auto` gọi `ensure_study_meta(seed={"design_code": <thiết kế G1 máy suy>})`.
- `run_g1_auto._read_pinned_design` đọc chính ô đó như PIN CỦA PI.
- Hệ quả: mỗi lượt G1 chạy lại sau G2 (dây chuyền dirty, `--from G1`, N4-G1), G1 gỡ cờ mơ hồ. G1-AUTO-04/04b chuyển REVIEW→PASS và G1-AUTO-02d hạ CHẶN→XEM mà không ai xác nhận. Đây là vượt ranh giới §0.5.
- Lỗi có từ bản G2 đầu tiên (02/07/2026).

**Bác sĩ chọn** (15/11, hỏi trước khi đổi luật cổng): «G2 thôi gieo + ghim cần dấu người».

**Cách vá** (y khoa drluanbv175/medical-ebm-automation#281):
- `skill_standards.ghim_thiet_ke(meta)` → (giá trị, có_dấu) là MỘT nguồn cho run_g1_auto và bộ chấm. Dấu người là một trong:
  - `gate_params.G1.design`;
  - `design_code_nguon="PI"`;
  - `design_confirmed is True`;
  - `design_code` trùng G1.design.
- `G1.design` lệch `design_code` không nhãn PI ⇒ `G1.design` thắng.
- `design_code` đứng một mình: vẫn là thiết kế đang dùng nhưng KHÔNG gỡ cờ mơ hồ, KHÔNG hạ 02d. Checkpoint ghi `ghim_chua_co_dau_pi`.
- G2 không ghi khoá máy nào vào `study_meta.json`. Thiết kế G2 dùng nằm ở `G2_checkpoint.design_code`.

**Thẩm định #281 bắt thêm hai lỗi ĐỎ của chính bản vá:**
1. Ô G1.design của PI từng bị giá trị gieo đè. Thêm nữa, `design_confirmed=true` «đóng dấu PI» cho giá trị máy.
2. Bản nháp ghi `design_code_tu_g1` vào study_meta ⇒ đổi byte tệp, làm 2 biên bản xử lý G1 của C1a thành «cũ».

**Kiểm:**
- 30 test; đột biến 18/18 đỏ.
- Đo bản sao C1a/btm: không hồ sơ nào thiếu dấu; chấm G1 không đổi; byte study_meta giữ nguyên (C1a 1703ce4b, btm 5d6260da).

**Bài học:**
- Ô nào là «quyết định của người» thì máy KHÔNG được gieo vào đó, kể cả gieo «chỉ khi trống».
- Bản sao của máy phải ở checkpoint, không ở tệp mà biên bản băm.
