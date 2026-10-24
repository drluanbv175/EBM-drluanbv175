# 24/10/2026 — Cảm biến «commit chưa đẩy» đếm mãi commit MERGE đã gộp ⇒ 🟡 giả mỗi phiên (BH169)

**Bối cảnh.** Bác sĩ: «Giải quyết tất cả vấn đề…». Hòm việc (`tools/tu_de_xuat_viec.py`) báo mỗi phiên 🟡 «Repo gốc: 3 commit
chưa có trên remote nào» và «Repo y khoa: 6 commit…» kèm việc «soi rồi commit/push».

**Nguyên nhân (đo 24/10).** Cả 9 commit là merge «Merge remote-tracking branch 'origin/<nhánh chính>' into <nhánh PR>» (10–17/10):
phiên trước kéo nhánh chính về nhánh PR, sau đó PR được gộp kiểu squash. Bản vá 09/10 lọc commit thường bằng `git cherry` (trùng
bản vá) và khớp tiêu đề squash — cả hai đều không xét commit merge ⇒ merge còn lại mãi trong danh sách «chưa đẩy». Đo từng merge:
`git diff-tree --cc` rỗng (merge không tự thêm dòng nào), cha thứ hai đã trên remote, cha thứ nhất đã được lọc là «đã gộp».
Thử tiêu chí khác: `git merge-tree` gộp merge vào nhánh chính chỉ ra «không đổi» 2/9 — 7/9 xung đột vì nhánh chính đã sửa tiếp
cùng dòng, nên không dùng.

**Vá.** `_commit_merge_sach`: nhận một merge khi ① combined diff rỗng và ② MỌI cha hoặc đã ở remote, hoặc đã được coi là đã gộp
(trùng bản vá / squash / merge sạch khác — lặp tới khi hết thêm). git lỗi / quá giờ / đầu ra lạ ⇒ không nhận (báo như cũ). Gọi
git trực tiếp, không qua `_chay` (số merge đổi theo ngày, không làm trôi bộ đếm giác quan). Dòng ⓘ «đã gộp» đếm cả merge sạch.

**Số đo sau vá (24/10).** Repo gốc 0 commit dở (38 trùng bản vá · 14 squash · 3 merge sạch); repo y khoa 0 (35 · 59 · 6).

**Giới hạn.** Merge có giải xung đột riêng (combined diff khác rỗng) vẫn bị đếm dù nội dung có thể đã vào nhánh chính — chiều an
toàn, soi tay. Đột biến «nhận cả commit thường một cha» sống sót: commit thường có nội dung luôn có diff khác rỗng nên bị loại
ở ①; chỉ commit RỖNG (`--allow-empty`) lọt — không có nội dung để đẩy, coi là tương đương.

**Kiểm hồi quy.** `tools/test_tu_de_xuat_viec_20261024_merge_sach.py` (4 ca) + test cũ 27/09, 09/10 (15/15 đạt); chốt **BH169**.
Đột biến 3/4 bị bắt (bỏ điều kiện merge sạch · bỏ điều kiện cha đã gộp · không trừ merge); BH169 đỏ đúng chỗ dưới hai đột biến chính.
