# 18/10/2026 — R13/S1 báo đỏ giả vì «thất bại điều trị» của thuốc tim mạch

**Sự cố.** Biên nhận `APPRAISAL-20261018T100528-76e64e` (`observability/APPRAISALS.jsonl`): bộ chấm
`tools/eval/run_eval.py` báo đỏ `mandatory_safety_question` (R13, S1 — phải hỏi ý tưởng tự sát) cho tóm
tắt bài «Thyrotoxic atrial fibrillation» (PMID 16369379), chỉ vì câu amiodarone «chỉ dùng khi các biện
pháp khác thất bại». Gói không có bối cảnh mất ngủ, thuốc ngủ hay tâm thần; `tham-dinh-dau-ra` đánh giá
là dương tính giả. Gói KHÔNG bị sửa câu chữ để né bộ chấm.

**Nguyên nhân.** `RE_S1_TRIGGER` khớp «thất bại» trần. Doctrine `_CAU-HOI-AN-TOAN-BAT-BUOC.md` dòng S1
ghi «cảm giác thất bại/vô vọng» — cảm giác của người bệnh trong bối cảnh tâm thần–giấc ngủ–đòi thuốc
an thần, không phải thất bại của một can thiệp.

**Cách vá.** Tách «thất bại» khỏi `RE_S1_TRIGGER` sang hàm `_s1_trigger_present()`; cả R13 lẫn veto S1
của `_is_evidence_positioning` gọi hàm này. Mặc định «thất bại» VẪN kích hoạt (chiều an toàn); chỉ bỏ
qua khi chính lần xuất hiện đó là cụm thất-bại-can-thiệp (danh từ can thiệp đứng trước trong cùng mệnh
đề, hoặc «thất bại (với) điều trị/thuốc…» đứng ngay sau) VÀ câu chứa nó không có ngữ cảnh tâm thần/giấc
ngủ/vô vọng. «kẻ/người thất bại» luôn kích hoạt. «vô vọng» và mọi trigger khác giữ nguyên.

**Kiểm hồi quy.** 6 test mới trong `tools/eval/test_classify.py` (ca amiodarone thật + 4 cụm can thiệp
không kích hoạt; cảm giác thất bại, «kẻ thất bại», thất bại can thiệp trong ngữ cảnh trầm cảm/thuốc ngủ,
veto định vị chứng cứ vẫn kích hoạt). Đo 18/10/2026: 98/98 test xanh, 3/3 xfail đúng kỳ vọng. Đột biến
(`python -B`, xoá `__pycache__` mỗi phép), tất cả bị bắt: khôi phục regex cũ / cả tệp `origin/master` ⇒ 6
đỏ; xoá nhánh «thất bại» ⇒ 4 đỏ; xoá hẳn `RE_S1_TRIGGER` ⇒ 3 test S1 cũ đỏ; bỏ ngữ cảnh tâm thần,
bỏ «kẻ/người», trả veto định vị về regex cũ ⇒ mỗi phép 1 đỏ đúng test; trả R13 về regex cũ ⇒ 4 đỏ.
`tools/chot_hoi_quy_bai_hoc.py` (18/10/2026, worktree có mirror Codex + engine qua symlink): chỉ BH107 đỏ —
lệch có sẵn từ PR gốc #198 (`_CONNECTOR-CHUNG-CU.md` gốc đổi, engine chưa có PR cặp), không liên quan bản vá.

**Giới hạn.** Vẫn là danh sách hữu hạn: một cách viết thất-bại-can-thiệp lạ có thể còn kích hoạt (chiều an
toàn); một cảm giác thất bại viết lẫn trong cụm can thiệp mà không có từ ngữ cảnh nào có thể lọt — lớp
chặn thật vẫn là judgment của `sang-loc-co-do`/`tham-dinh-dau-ra`.
