# 25/10/2026 — Agent hội đồng gọi `python3` hệ thống ⇒ không kiểm được chữ ký Ed25519 ⇒ đọc G4 đã khoá thành «chờ ký»

**Hiện tượng.** Hội đồng G1 của C1a (run `wf_c6a486fb-641`, 10 agent) ghi vào biên bản tranh biện DP-G1-1 căn cứ «G4
READY_FOR_SIGNATURE (nguồn sống), chưa khoá — còn cửa bổ sung SAP trước khi ký», và đề xuất bổ sung SAP «trước khi ký
G4». Đo cùng lúc ở phiên chính: G4 `PASS_G4_SAP_LOCKED` (đã ký, đã khoá). Tái hiện: cùng lệnh
`hoi_dong_cong.py cham-song --gate G4` chạy bằng `~/.ebm-venv/bin/python` ⇒ PASS_G4_SAP_LOCKED; bằng `python3` hệ thống
⇒ READY_FOR_SIGNATURE kèm «G4-HUMAN-01 BẤT THƯỜNG — chữ ký KHÔNG xác minh được (bị sửa sau khi ký…)».

**Nguyên nhân.** `python3` hệ thống không có thư viện `cryptography`. Mọi chữ ký «ed1» (Ed25519) của sổ cái ra False — đúng
hướng fail-closed — nhưng (a) thông điệp nói «có thể bị sửa sau khi ký», (b) lớp chấm sống `cong_song` coi trạng thái ấy
là số đo thật («nguồn sống»), (c) lời nhắc workflow `hoi-dong-cong.js` ghi `python3 tools/…`. Đúng dạng CLAUDE.md §0.2:
«không đo được» bị đọc thành «có vấn đề».

**Vá.**
- Repo y khoa (PR nhánh `claude/ed1-thieu-thu-vien-20261025`): `gate_contract.verify_approval_signature` VẪN trả False khi
  thiếu thư viện (không nới cổng) nhưng ghi sổ «không kiểm được»; `cong_song` lấy mốc sổ trước/sau mỗi lượt chấm (không
  xoá sổ — chấm G10 gọi lồng G0–G9) ⇒ có chữ ký không kiểm được ⇒ «⚪ KHÔNG ĐO ĐƯỢC», nêu Python đang chạy và lệnh đo lại;
  thông điệp bản ghi/con dấu nói «THIẾU thư viện cryptography — không phải bằng chứng bị sửa». Đo trên C1a bằng `python3`:
  G2/G4/G10 ⇒ KHÔNG_DO_DUOC (7/21/126 chữ ký không kiểm được); bằng venv: trạng thái thật.
- Repo gốc (PR này): lời nhắc chung của `hoi-dong-cong.js` — «python3» nghĩa là `~/.ebm-venv/bin/python`; «không đo
  được»/«chữ ký không kiểm được» KHÔNG phải trạng thái cổng.

**Kiểm.** 6 ca test (`tests/test_ed1_thieu_thu_vien_khong_do_duoc_20261025.py`); đột biến 5/5 bị bắt (không ghi sổ ·
thiếu thư viện thành ĐẠT · chấm sống bỏ qua sổ · lý do cũ · mọi chữ ký đều «thiếu thư viện»), phục hồi khớp sao lưu.

**Hệ quả với biên bản đã ghi.** Biên bản `G1-TB-20261025T152106-1ac1bb54` (DP-G1-1) mang căn cứ sai về G4. Biên bản không
sửa tay; phán quyết «chuyển bác sĩ» vẫn đúng hướng, nhưng mọi bổ sung SAP lúc này là SỬA ĐỔI SAU KHOÁ (G4 phải ký lại,
SAP nằm trong gói G10 đã khoá ⇒ G10 cũng ký lại) — đã báo bác sĩ cạnh từng câu hỏi.

**Bài học.** Agent con không kế thừa venv của phiên chính. Công cụ dùng chung phải tự nói khi môi trường chạy không đủ để
đo, thay vì trả một trạng thái trông như thật.
