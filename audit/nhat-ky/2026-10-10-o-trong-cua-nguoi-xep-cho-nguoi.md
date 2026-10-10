# 10/10/2026 — Ô trống gửi đích danh người bị tính là «agent còn việc»; G0 chờ PI bị tô đỏ «máy sửa được»

Bác sĩ hỏi: hệ nghiên cứu, các agent và điều phối đã đủ, đã hoàn thiện chưa — chưa thì xây tiếp, xong hết mới họp hội
đồng từng cổng.

## Đo (10/10, worktree gộp cục bộ y khoa #110 + #111, không đẩy)

- `tieu_chuan_hoan_thien.py`: agent 64/64 · điều phối 13/13 ĐẠT. `verify_controlled_research_automation.py`: PASS.
- `hoi_dong_cong.py trach-nhiem --gate ALL` (C1a): G1 và G4 vẫn «AGENT_CON_VIEC» dù phần còn lại chỉ là ô của chủ
  nhiệm — G1-AUTO-07 còn đúng dòng «Thời gian nghiên cứu» (quyết định PI, G1-HUMAN-03 chấm riêng); G4-AUTO-10 còn đúng
  thẻ «[CẦN CHỦ NHIỆM XÁC NHẬN]» ở SAP §5 (biến `chuyenkhoa`). Bảng giao agent việc agent không làm được ⇒ «phần agent
  hoàn chỉnh» không bao giờ đạt.
- `kiem_chi_tiet_he_nghien_cuu.py`: 1 ô 🔴 «G0 checkpoint BLOCKED dù tiền đề đã đủ — máy sửa được» trong khi G0 bị chặn vì
  CHÍNH nó chờ PI (needs_input `MISSING_PICO` sau khi chấm lại đồng bộ trạng thái sống). Lỗi bị che trước đó vì checkpoint
  mang trạng thái «đã giải quyết» lỗi thời. Công cụ chỉ xét tiền đề, không xét mã lý do.

## Vá (repo y khoa, PR xếp chồng trên y khoa #111; không đổi trạng thái tiêu chí của cổng nào)

- `placeholder_contract.vai_cua_o_trong`: thẻ «[CẦN CHỦ NHIỆM/PI/THỐNG KÊ VIÊN/CNTT/HỘI ĐỒNG …]» ⇒ vai người.
- G1-AUTO-07 / G4-AUTO-10: phần còn lại chỉ là ô của người ⇒ bằng chứng mở đầu «CHỜ NGƯỜI (vai)»; ô chung «[CẦN BỔ SUNG]»,
  «___» hoặc mục VẮNG vẫn là việc agent.
- `hoi_dong_cong.trach_nhiem`: bằng chứng «CHỜ NGƯỜI (vai)» ⇒ xếp «chờ người» (kèm nhiệm vụ chuẩn bị hồ sơ); thông điệp
  nhiệm vụ không có tiêu chí cổng nói rõ «có kiểm máy» nếu có.
- `kiem_chi_tiet_he_nghien_cuu`: chặn với mã lý do chỉ người/đời thực gỡ được (PICO, PubMed cần từ khoá, effect size, IRB,
  khoá SAP, dữ liệu thật, chữ ký liêm chính/bình duyệt/phát hành, bản thảo đổi sau bình duyệt) ⇒ 🟡; lý do máy làm được
  vẫn 🔴.
- Doctrine `_HOI-DONG-CONG.md` §1b mục 13 (repo gốc — PR này, bản cặp y hệt ở y khoa).

## Kiểm

- C1a sau vá: G1 CHO_CONG_TRUOC (0 việc agent, G1-AUTO-07 → PI), G4 CHO_CONG_TRUOC (G4-AUTO-10 → PI); kiểm chi tiết 🔴 0.
- `tests/test_dinh_tuyen_cho_nguoi_20261010.py`: 6 ca. Đột biến 9/9 bị bắt (có lượt nền xanh 1088 test nhóm liên quan);
  D9 lọt lần đầu do điều kiện thừa (`not tim_thay`) + test thiếu ca hai mục — bỏ điều kiện thừa, thêm ca.
