---
name: kiem-tra-hoan-thien-he-thong-thang
description: Quét hoàn thiện kỹ thuật hàng tháng cho CẢ hệ nghiên cứu G0-G10 lẫn hệ cập nhật chứng cứ lâm sàng — dây nối cổng, doctrine agent, đối chiếu 2 repo, CI, tài liệu lỗi thời; khác 4 tác vụ hiện có (chỉ lo nội dung/an toàn chứng cứ)
---

NỀN TẢNG: macOS + Windows. THƯ MỤC LÀM VIỆC = gốc thư mục OneDrive «Claude AI» của MÁY ĐANG CHẠY (repo EBM-drluanbv175):
- macOS: "$HOME/Library/CloudStorage/OneDrive-Personal/Claude AI"
- Windows: "%USERPROFILE%\OneDrive\Claude AI" (máy hiện tại: C:\Users\Admin\OneDrive\Claude AI)
Không thấy thư mục đúng ⇒ DỪNG và báo nguyên văn; không đoán đường dẫn khác.
Trên Windows đổi lệnh: `python3` → `py -3`; `~/.ebm-venv/bin/python` → `%USERPROFILE%\.ebm-venv\Scripts\python.exe`.
Đường dẫn tương đối viết bằng `/` dùng được nguyên trên cả hai; tệp tạm ghi vào `state/` của thư mục làm việc, không dùng `/tmp`.

Đây là tác vụ nền hằng tháng cho dự án EBM Copilot của bác sĩ Luân — repo gốc
(THƯ MỤC LÀM VIỆC ở trên; nhánh làm việc hiện tại;
kiểm bằng `git branch --show-current`, remote `drluanbv175/EBM-drluanbv175`) và repo nghiên cứu
sống lồng bên trong `medical-ebm-automation/` (remote `drluanbv175/medical-ebm-automation`,
venv `~/.ebm-venv`). Đọc kỹ `CLAUDE.md` ở gốc TRƯỚC khi làm gì — đó là doctrine đầy đủ, rất dài,
ghi lại hàng trăm bài học đã vá; tự đối chiếu doctrine với mã sống thay vì tin lời khai trong đó.

MỤC ĐÍCH TÁC VỤ NÀY — khác hẳn tác vụ lịch nền nội dung `cap-nhat-thang-ebm` (từ 13/11/2026 gộp cả
thu thập an toàn thuốc, gói duyệt chứng cứ và phiếu thư mục EndNote — đều lo NỘI DUNG/AN
TOÀN chứng cứ lâm sàng, quét PubMed, cảnh báo thuốc). Tác vụ này lo **HOÀN THIỆN KỸ THUẬT CỦA
CHÍNH HỆ THỐNG**: dây nối cổng chất lượng, doctrine agent có theo kịp mã không, 2 repo có đối
chiếu nhau không, CI có chạy thật không, tài liệu CLAUDE.md có đoạn nào ghi số liệu/trạng thái
đã lỗi thời so với thực tế không. Đây là một "kiểm tra sức khỏe kỹ sư" định kỳ, không phải quét
chứng cứ y khoa.

DẤU VẾT LƯỢT — BẮT BUỘC (14/11/2026; cảm biến `tools/kiem_lich_nen.py` chỉ canh được tác vụ để lại dấu vết máy-đọc-được):
- Lệnh Bash ĐẦU TIÊN của lượt: `python3 tools/ghi_dau_vet_lich.py kiem-tra-hoan-thien-he-thong-thang --bat-dau`
- Lệnh Bash CUỐI CÙNG của lượt (sau báo cáo):
  `python3 tools/ghi_dau_vet_lich.py kiem-tra-hoan-thien-he-thong-thang --ma <0|1|2>` — 0 = mọi mảng sạch, không có việc ·
  1 = có việc cho bác sĩ / việc sửa cho phiên có người · 2 = có mảng KHÔNG đo được/không chạy được.
Công cụ nối dòng BẮT ĐẦU/KẾT THÚC (giờ do máy lấy) vào `state/kiem-tra-hoan-thien-he-thong.log` khai ở
`sync/lich-nen-ky-vong.json`. Có BẮT ĐẦU mà thiếu KẾT THÚC ⇒ cảm biến báo 🔴 «lượt bị cắt ngang/chết giữa chừng»; thiếu cả hai
⇒ 🔴 kỳ lỡ. KHÔNG tự gõ dòng vào log bằng Write/Edit (dấu vết tự khai giờ là dấu vết giả). Lệnh in «⚪ KHÔNG ghi dấu vết…»
(mã 2) ⇒ chép nguyên văn vào báo cáo, không chạy lại kiểu khác.

BƯỚC 0 — TIỀN KIỂM QUYỀN (14/11/2026; lượt phải GÃY ỒN, không gãy âm thầm — mẫu theo bước 0 của `cap-nhat-thang-ebm`).
Ngay sau lệnh BẮT ĐẦU, chạy `python3 tools/quyen_lich_nen.py --tac-vu kiem-tra-hoan-thien-he-thong-thang` (quyền của ĐÚNG các
lệnh lượt này sẽ gõ, khai ở khoá `kiem-tra-hoan-thien-he-thong-thang` của `sync/quyen-lich-nen.json`):
- mã 0 (🟢) ⇒ làm tiếp các mảng ①–⑨.
- mã 1 (🔴 có lệnh của lượt này chưa được phép trên máy, hoặc SKILL có lệnh chưa khai/lệnh ghép — lượt sẽ bị cắt ngang giữa
  chừng mà bộ lập lịch vẫn ghi «succeeded») HOẶC mã 2 (⚪ KHÔNG đo được quyền — «không đo được» không phải «đủ»)
  ⇒ DỪNG LƯỢT NGAY, KHÔNG chạy mảng ①–⑨. Chạy
  `python3 tools/ghi_dau_vet_lich.py kiem-tra-hoan-thien-he-thong-thang --ma 2` (ghi KẾT THÚC mã 2 — lượt không chạy được) rồi
  kết thúc bằng tin nhắn mở đầu «🔴 LƯỢT KỸ THUẬT THÁNG DỪNG Ở BƯỚC 0 — tiền kiểm quyền mã <n>», dán NGUYÊN VĂN các dòng ✗/⚪
  công cụ in, và lệnh bác sĩ tự chạy `python3 tools/quyen_lich_nen.py --ap-dung` rồi «Run now».
  (Nếu chính lệnh ghi KẾT THÚC bị cắt vì chưa áp quyền, cảm biến tự báo 🔴 «cắt ngang» — vẫn là gãy ồn; không thử cách khác.)
- Windows: BỎ QUA bước 0 — hợp đồng quyền `sync/quyen-lich-nen.json` chỉ khai cho macOS (`nen_tang: darwin`, cùng cách
  `tools/dong_bo_tac_vu_lich.py` coi là «không áp»); ghi «⚪ bước 0 không áp trên Windows» vào báo cáo rồi làm tiếp.

QUY TẮC CHẠY LỆNH — lượt lịch KHÔNG có ai bấm «cho phép» (14/11/2026):
- Mỗi lần gọi Bash chạy ĐÚNG MỘT lệnh viết Y NHƯ trong tệp này (chỉ thay «<…>» bằng giá trị). Phiên đã đứng sẵn ở THƯ MỤC LÀM
  VIỆC: KHÔNG `cd …`, không nối `&&`/`;`/`|`, không chuyển hướng `>`/`2>&1`. Lệnh cho repo y khoa viết bằng
  `git -C medical-ebm-automation …` hoặc đường dẫn `medical-ebm-automation/tools/…` (công cụ tự tìm gốc theo vị trí tệp).
  Claude Code xét quyền TỪNG lệnh con của một chuỗi ghép — chuỗi ghép luôn bị đòi duyệt ⇒ lượt bị CẮT NGANG, mất dòng KẾT THÚC.
- Đọc/tìm trong tệp ⇒ dùng công cụ Read/Grep (không gõ grep/cat/ls/find qua Bash).
- LƯỢT LỊCH KHÔNG TỰ SỬA: bước SỬA (Edit/Write vào mã hay tài liệu, pytest chọn lọc sau khi sửa, commit, push, mở PR) cố ý
  KHÔNG khai quyền (`sync/quyen-lich-nen.json`, khoá của tác vụ này) — gõ là lượt bị cắt ngang. Phát hiện cần sửa ⇒ ghi một dòng
  «🛎 việc sửa cho phiên có người: <tệp> — <bằng chứng: lệnh đã chạy + kết quả> — <cách kiểm lại>» vào báo cáo; kết thúc `--ma 1`.
- Lệnh bị đòi duyệt quyền mà lượt vẫn còn sống ⇒ ghi «⚪ mảng <n> chưa chạy được — lệnh cần duyệt quyền: <lệnh>», làm tiếp mảng
  khác, kết thúc `--ma 2`. Thêm lệnh mới vào tệp này ⇒ khai ở `sync/quyen-lich-nen.json` trước (chốt BH173 đỏ nếu quên hoặc
  nếu viết lệnh ghép).

QUY TẮC BẮT BUỘC (dự án này có kỷ luật rất cao — đọc CLAUDE.md để hiểu vì sao từng quy tắc
tồn tại, phần lớn xuất phát từ một lỗi thật đã xảy ra):
1. KHÔNG tin lời tự khai "đã sửa"/"PASS" trong CLAUDE.md — luôn TỰ CHẠY LẠI mã sống để xác nhận.
   Dự án này đã nhiều lần phát hiện tài liệu nói một đằng, mã sống chạy một nẻo ("đo đúng, nhưng
   đo nhầm chỗ" — lớp lỗi lặp lại nhiều lần, xem BH93 và các đính chính trong CLAUDE.md).
2. Trước khi kết luận về `medical-ebm-automation/`, kiểm cây có lạc hậu không: chạy
   `git -C medical-ebm-automation fetch origin --quiet` (chỉ cập nhật ref theo dõi từ xa — không đổi nhánh, không đổi cây làm
   việc), `git fetch origin --quiet` (repo gốc), rồi `python3 tools/kiem_cay_lam_viec.py` (đo lạc hậu CẢ HAI repo; mã 1 = cây không
   đủ tư cách kết luận) — repo y khoa từng bị phát hiện lạc hậu 55 commit khiến một đợt kiểm toán trước đó kết luận sai hàng loạt
   (BH93). Fetch lỗi mạng ⇒ ghi ⚪, không thử cách khác. Chỉ đo, báo cáo nếu lạc hậu, KHÔNG tự ý merge/rebase/reset/đổi nhánh.
3. Nhiều phiên Claude Code khác (kể cả worktree) có thể đang chạy song song trên cùng repo — chạy `git status --short` và
   `git -C medical-ebm-automation status --short`; thay đổi lạ không phải của mình ⇒ để nguyên, chỉ ghi nhận trong báo cáo.
4. Việc phiên có người được sửa TRỰC TIẾP (ghi «🛎» kèm bằng chứng): lỗi tài liệu lỗi thời có bằng chứng rõ ràng (đối chiếu bằng
   lệnh thật), comment sai, một dòng cấu hình sai rõ ràng, đường dẫn hỏng trên nền tảng khác. Việc CHỈ báo cáo (phiên có người
   cũng không tự sửa): mã cổng an toàn/logic chấm điểm y khoa/nội dung lâm sàng/quyết định `decision`/`gradeLevel`.
5. TUYỆT ĐỐI không xóa bất cứ gì — nội dung nghi ngờ chỉ ghi vào báo cáo để phiên có người move/quarantine/backup.
6. Phiên có người làm việc sửa xong: chạy lại chốt hồi quy liên quan + `python3 tools/chot_hoi_quy_bai_hoc.py` (root)
   trước khi commit; sửa bên trong `medical-ebm-automation/` thì chạy thêm (phiên có người — lệnh ghép này KHÔNG chạy trong
   lượt lịch; vài tệp test phụ thuộc thư mục chạy nên thu thập cả `tests/` phải đứng trong repo y khoa)
   `cd medical-ebm-automation && ~/.ebm-venv/bin/python -m pytest -k "<phần liên quan>" -q`.
7. Nếu mọi thứ sạch (không tìm ra gì cần sửa), đó là kết quả HỢP LỆ — không cần bịa việc để làm.

VIỆC CẦN KIỂM MỖI LẦN CHẠY (9 mảng, làm tuần tự):

**① Dây nối 11 cổng G0-G10.** Dùng công cụ Grep (mẫu `quality_gate|evaluate_study`, tệp
`medical-ebm-automation/tools/approve_gate.py`) rồi Read quanh mỗi match — xác nhận 6 cổng cứng canonical (G2,G4,G5,G8,G9,G10)
đều có lời gọi `gN_quality_gate.evaluate_study` THẬT trước dòng ghi ledger. Hồi quy dây nối
(`tests/test_approve_gate_quality_gate_wiring_20260824.py`): lượt lịch KHÔNG chạy pytest này — tên tệp mang tên công cụ ghi quyết
định `approve_gate`, chốt BH173 không cho khai lệnh chứa tên đó cho lượt lịch. Thay vào đó đọc CI repo y khoa ở mảng ⑤ (CI chạy
TRỌN bộ test hermetic, gồm tệp này, mỗi lần đẩy): CI xanh trên commit đầu nhánh chính ⇒ hồi quy PASS ở commit đó; CI đỏ/không
chạy thật ⇒ ⚪ chưa xác nhận. Phiên có người chạy trực tiếp
`~/.ebm-venv/bin/python -m pytest medical-ebm-automation/tests/test_approve_gate_quality_gate_wiring_20260824.py -v`.

**② Tautology scan trên 2-3 cổng CHƯA từng soi kỹ gần đây** (đổi ngẫu nhiên mỗi lần chạy để dần
phủ hết 11 cổng — G0,G1,G3,G4,G5,G6,G7,G8,G9,G10): đọc (Read) `medical-ebm-automation/tools/gN_quality_gate.py` tương ứng,
xác minh vài luật AUTO có kiểm nội dung THẬT SỰ THAY ĐỔI theo dữ liệu đề tài hay chỉ đếm chuỗi
mà bộ sinh artifact luôn in cứng (tautology — lớp lỗi đã gặp nhiều lần ở G3/G8).

**③ Doctrine agent có theo kịp luật cổng mới không.** Rà CLAUDE.md tìm mọi bản vá cổng G/quality
gate trong 60 ngày gần nhất (tìm theo ngày ghi trong file), rồi dùng Grep xem khái niệm mới đó (tên
trường, luật mới) có được nhắc trong `.claude/agents/*.md` liên quan không — đúng luật nền BH39
"thêm luật ở CỔNG thì phải DẠY AGENT cùng lúc". Chạy `python3 tools/kiem_dieu_phoi.py` xác nhận
vẫn 🟢.

**④ Sức khỏe từng đề tài THẬT.** `~/.ebm-venv/bin/python medical-ebm-automation/tools/list_studies.py`
rồi với mỗi đề tài thật (không phải fixture ZZ*/PYTEST-*/REFUTE-*), chạy
`~/.ebm-venv/bin/python medical-ebm-automation/tools/kiem_chi_tiet_he_nghien_cuu.py --study <mã> --no-write` — báo cáo
nếu có 🔴 mới xuất hiện so với lần trước (không có "lần trước" để so thì chỉ báo cáo hiện trạng).

**⑤ Đối chiếu 2 repo + CI thật.** `python3 tools/verify_claude_code_repo_alignment.py` (root; repo y khoa không có bản riêng —
đo 14/11/2026). Kiểm CI THẬT (không suy đoán) bằng hai lệnh
`gh run list --repo drluanbv175/EBM-drluanbv175 --limit 3 --json databaseId,status,conclusion,headSha` và
`gh run list --repo drluanbv175/medical-ebm-automation --limit 3 --json databaseId,status,conclusion,headSha` — xác nhận job thật
sự chạy (không phải `runner_id:0` hay `queued` treo, dấu hiệu Actions bị tắt ở cấp tài khoản như đã từng xảy ra
09/2026). Nếu CI đỏ hoặc không chạy thật, báo rõ — đây là việc CHỈ bác sĩ xử lý được qua giao
diện web GitHub (Settings → Actions), không phải lỗi agent sửa được.

**⑥ Nhánh mồ côi / worktree có việc thật chưa merge.** `git worktree list` và
`git for-each-ref --count=20 --sort=-committerdate --no-merged=master refs/heads refs/remotes` (root repo — 20 nhánh mới nhất
chưa gộp vào master); với nhánh đáng ngờ xem `git log --oneline -10 master..<nhánh>`. Nếu thấy nhánh có commit thật
(không phải nhánh rác/thử nghiệm) mang sửa lỗi có giá trị mà chưa vào nhánh làm việc chính, ghi
rõ tên nhánh + commit hash + tóm tắt để báo cáo, KHÔNG tự ý merge (rủi ro cao, cần người xem lại).

**⑦ Quét CLAUDE.md tìm khẳng định lỗi thời.** Chọn 3-5 đoạn "ĐÍNH CHÍNH"/"đã vá"/"PASS" gần
ngày nhất trong CLAUDE.md (root), ưu tiên đoạn có con số/lệnh cụ thể kiểm được. Lệnh của đoạn đó trùng một lệnh đã có trong
tệp này ⇒ chạy để xác minh; lệnh KHÁC (chưa khai quyền cho lượt này) ⇒ KHÔNG gõ, ghi «⚪ chưa xác minh trong lượt lịch —
<lệnh> chưa khai quyền» cho phiên có người. Sai lệch rõ ràng ⇒ «🛎» cho phiên có người (chỉ văn bản mô tả, không phải số liệu y
khoa); đính chính mới đi vào tệp mới `audit/nhat-ky/` theo quy ước, KHÔNG thêm chữ vào CLAUDE.md (có ngân sách ký tự).

**⑧ Chốt hồi quy tổng + kho công cụ.** `python3 tools/chot_hoi_quy_bai_hoc.py` (root, kỳ vọng
sạch, ghi rõ nếu có "BÀI HỌC TÁI PHÁT"). `python3 tools/kiem_plugin_day_du.py` — kho công cụ có
đủ không (🟢/🟡/🔴).

**⑨ Sổ đo sử dụng công cụ (thêm 03/10/2026, Q7).** Transcript chỉ giữ ~26 ngày nên kết luận «công cụ X không ai dùng» chỉ có giá
trị khi có sổ dài hạn. Chạy `python3 tools/do_su_dung_cong_cu.py --thang <THÁNG TRƯỚC, YYYY-MM> --ghi` (chỉ đếm TÊN tool/skill/
lệnh/agent/MCP/mô hình — không giữ nội dung hội thoại), rồi `python3 tools/do_su_dung_cong_cu.py --tong-hop`; ghi số tháng đã có
vào báo cáo. KHÔNG đề xuất tắt công cụ khi sổ mới có < 3 tháng.

BÁO CÁO: viết một bản tóm tắt ngắn gọn BẰNG TIẾNG VIỆT (đúng theo chỉ thị ngôn ngữ toàn cục của
người dùng) liệt kê: bước 0 (mã tiền kiểm), mảng nào sạch, mảng nào có việc cần bác sĩ xử lý (kèm lệnh cụ thể để tự
chạy), mảng nào có «🛎 việc sửa cho phiên có người» (kèm bằng chứng), mảng nào ⚪ chưa chạy được (kèm lệnh cần duyệt quyền).
Lượt lịch KHÔNG commit, KHÔNG push, KHÔNG mở PR (các lệnh đó cố ý không khai quyền — gõ là lượt bị cắt ngang). Phiên có người
làm việc sửa thì theo lệ dự án: thông điệp commit tiếng Việt, đẩy CHỈ lên nhánh làm việc, mở PR. TUYỆT ĐỐI KHÔNG tự gộp,
fast-forward hay đẩy vào `master` (bác sĩ đã bỏ quy tắc tự gộp ngày 20/09/2026): mọi thay đổi vào `master` chỉ đi qua Pull
Request do bác sĩ duyệt. KHÔNG hỏi lại người dùng — đây là phiên chạy nền không có ai theo dõi trực tiếp; nếu gặp quyết định
thật sự cần người (không phải việc máy tự quyết được), chỉ ghi vào báo cáo, không dừng lại chờ.

BƯỚC CUỐI BẮT BUỘC: chạy lệnh ghi dòng KẾT THÚC ở mục «DẤU VẾT LƯỢT» phía trên (`--ma` theo kết quả báo cáo). Thiếu bước này thì
kỳ tháng bị cảm biến tính là LỠ dù báo cáo đã viết xong.
