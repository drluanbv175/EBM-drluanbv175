# 01/10/2026 — Nhật ký sự cố chung là điểm nóng xung đột duy nhất khi gộp nhánh; chuyển sang mỗi sự cố một tệp

**Triệu chứng (30/09–01/10):** PR #66 phải gộp origin/master hai lần (058bf8d sau PR #65, 256d68d sau
PR #67/#70). Lần nào xung đột cũng chỉ nằm ở `audit/NHAT-KY-SU-CO.md`, vì hai mục cùng được nối vào cuối
tệp. Lần nào cũng phải gộp tay giữ cả hai mục, và tính năng Auto-fix của app bị đánh thức.

**Đo (01/10/2026, `git merge-tree --write-tree --name-only` phát lại trên mọi merge commit của
origin/master từ 10/09; vòng lặp viết bằng bash để `$?` lấy đúng ngay sau lệnh):**
- 93 merge commit: 88 sạch, 5 xung đột. 3 lần xung đột chỉ ở nhật ký (360c511 · 058bf8d · 256d68d),
  2 lần ở tệp khác (16/09 và 20/09, đều trước khi có quy ước nhật ký).
- Từ 24/09 (ngày `CLAUDE.md` rút gọn và đặt quy ước «ghi vào mục SAU 24/09/2026 ở cuối tệp»):
  49 PR được merge; 32 PR (65%) sửa nhật ký, cả 32 chỉ THÊM dòng (0 dòng xoá). Cả 3 merge có xung
  đột từ 24/09 đều chỉ ở nhật ký, và đều do hai bên chèn tại cùng một dòng cuối. Ở 058bf8d/256d68d
  hai bên cũng cùng sửa `tools/chot_hoi_quy_bai_hoc.py` nhưng git tự gộp sạch ⇒ nhật ký là điểm
  nóng duy nhất.
- Giới hạn: chỉ thấy xung đột đã thành merge commit; xung đột giải bằng rebase hoặc bỏ nhánh làm
  lại không đếm được ⇒ 3 là cận dưới.

**Ba phương án đã so (bác sĩ chọn (b) ngày 01/10/2026):**
- (a) `.gitattributes` `merge=union`. Thử trên repo tạm và bản clone tạm (khai ở `.git/info/attributes`
  của bản clone, không đụng repo dùng chung). Phát lại 3 xung đột thật: cả 3 tự gộp sạch, đủ mọi
  khối `###`, mục liền khối; chỉ khác thứ tự mục và mất một dòng trống. Nhưng: hai bên sửa CÙNG một
  dòng (kiểu «ĐÍNH CHÍNH») ⇒ giữ cả hai câu mâu thuẫn, mã thoát 0, không dấu xung đột; một bên xoá
  dòng còn bên kia sửa ⇒ dòng xoá sống lại, không báo; nhánh tạo trước khi có dòng thuộc tính thì
  vẫn xung đột. Về GitHub: tài liệu chính thức không nhắc `merge=union`; thư hỗ trợ GitHub 2017 nói
  GitHub không đọc `.gitattributes` của người dùng, thảo luận cộng đồng
  https://github.com/orgs/community/discussions/9288 còn mở tới 2026 ⇒ nhiều khả năng PR vẫn hiện
  CONFLICTING và Auto-fix vẫn bị gọi (CHƯA thử trực tiếp trên GitHub).
- (b) Mỗi sự cố một tệp — ĐÃ CHỌN: hai PR khác tên tệp không bao giờ xung đột, kể cả trên GitHub;
  không có gộp ngầm sai.
- (c) Giữ nguyên + hướng dẫn gộp tay: không đổi gì, nhưng xung đột và Auto-fix tiếp diễn.

**Đã làm:**
- `audit/NHAT-KY-SU-CO.md` ĐÓNG BĂNG: thêm đúng một dòng trỏ ở đầu tệp, không sửa mục nào; chốt
  `check_nhat_ky_su_co()` trong `tools/verify_claude_code_repo_alignment.py` (nối vào
  `run_verification` ⇒ chạy ở pre-commit) so SHA-256 của tệp (chuẩn hoá CRLF→LF) với hằng
  `NHAT_KY_CU_SHA256`.
- Quy ước thư mục mới: `audit/nhat-ky/README.md`; luật tên tệp + dòng đầu nằm ở
  `tools/muc_luc_nhat_ky.py` (nguồn duy nhất, chốt gọi lại); công cụ đó in mục lục khi cần —
  mục lục KHÔNG commit vì sẽ thành điểm nóng mới.
- `CLAUDE.md` dòng 3–4 và mục Bộ chốt bài học trỏ sang quy ước mới; thông điệp lỗi ngân sách
  `CLAUDE.md` trỏ sang `audit/nhat-ky/`.

**Kiểm (01/10/2026):** `tools/test_nhat_ky_mot_tep_20261001.py` (27 ca: tệp thật, tệp tạm, một repo
git tạm chứng minh hai nhánh thêm hai tệp khác tên gộp sạch còn đối chứng hai nhánh cùng nối cuối
một tệp thì xung đột). Kiểm đột biến (`python -B`, xoá `__pycache__` mỗi phép): 12/12 đỏ rồi phục
hồi xanh — bỏ so băm · bỏ chuẩn hoá CRLF · tháo khỏi `run_verification` · bỏ lỗi thư mục mới · nhận
ngày 30/02 · regex tên dễ dãi · bỏ kiểm dòng đầu · không đòi ngày trùng tên · bỏ miễn README · bỏ miễn
tệp ẩn · bỏ chặn thư mục con · dòng trống đầu tính là dòng đầu. Đột biến thứ 13 (bỏ vế độ dài tiêu đề)
lọt vì vế đó là mã chết (`_dong_dau` đã `rstrip`) ⇒ gỡ. Đầu–cuối: nối một dòng vào tệp cũ, stage,
chạy `.githooks/pre-commit` ⇒ mã 1, FAIL `nhat_ky_su_co`. Hai test cũ cố định tập tên chốt
(`test_claude_code_repo_alignment.py`, `..._20260926_tap_check.py`) thêm `nhat_ky_su_co`.
`pytest tools/` như CI: 1873 đạt, 31 bỏ qua có khai lý do. `python3 tools/chot_hoi_quy_bai_hoc.py`
trọn bộ trên worktree trần: 106 ✓, 0 tái phát, 36 ⚪ (thiếu cây dữ liệu/engine ngoài git — KHÔNG phải đạt).

**Thứ tự merge cần chú ý:** PR #75 và #76 (mở trước khi đóng băng) vẫn nối vào cuối tệp cũ. Nếu
chúng merge TRƯỚC PR này thì phải gộp origin/master vào nhánh này và cập nhật `NHAT_KY_CU_SHA256`
cho khớp tệp mới; nếu PR này merge trước thì hai nhánh đó phải dời mục sang `audit/nhat-ky/` theo
mục «Nhánh mở TRƯỚC khi đóng băng» của README.
