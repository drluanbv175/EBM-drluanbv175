# 15/11/2026 — PR gộp ở đầu cũ làm rơi commit dạy agent + vòng xung đột manifest agent giữa các PR y khoa

**Hiện tượng 1 — rơi commit:** ba PR gốc được gộp ở commit đầu, trước khi các commit sau thẩm định kịp đẩy lên.
- #383 rơi phần dạy bảng G3 ⇒ đưa lại ở #385.
- #385 rơi d2a9fcd7 (luật K4/N4-G1 sau thẩm định y khoa #277).
- #389 rơi d68e2bba (luật ghim sau thẩm định y khoa #281).

Repo y khoa (gộp #277 đủ) có các dòng mà repo gốc thiếu ⇒ cặp agent lệch. Đưa lại ở drluanbv175/EBM-drluanbv175#394. Chỉ thay đúng 6 dòng, nội dung phiên khác giữ nguyên.

**Hiện tượng 2 — xung đột lặp:** mọi PR y khoa sửa agent đều sinh lại `runtime/manifests/agent_source_manifest.csv` và hằng `MANIFEST_SELF_CHECK_SHA256` trong `runtime/agent_registry.py`.
- Nhánh nền có thêm một PR là MỌI PR còn mở xung đột ở cùng dòng đó.
- 15/11 có #274/#277/#281 phải gộp nền lặp lại sau #276, #279, #280, #278, #277.
- Bác sĩ: «Các PR gộp bị lỗi và rất mất thời gian».

**Cách xử lý:**
- Gom #274 vào #281 thành MỘT PR y khoa (đóng #274 kèm ghi chú).
- PR dạy agent ở repo gốc gom vào MỘT PR (#394).
- Một PR y khoa + một PR gốc không bao giờ xung đột với nhau.

**Bài học / cách làm từ nay:**
- PR có bước thẩm định: mở `--draft`, chỉ `ready` khi sửa xong (đã có trong bộ nhớ từ 14/11).
- Commit sau thẩm định đẩy lên TRƯỚC khi báo «sẵn sàng».
- Nhiều việc cùng sửa agent ở repo y khoa ⇒ gom vào MỘT nhánh/PR. Hằng self-check manifest là điểm nóng xung đột cố hữu (thiết kế cố ý: khoá lại baseline là bước người xác nhận, không đổi).
- Gộp nền vào PR đã đẩy: `git merge`, không rebase. Xung đột manifest ⇒ lấy bên nền rồi `scripts/regenerate_agent_manifest.py --write` + vá hằng SHA + `tools/sinh_mirror_codex.py --ghi`.
