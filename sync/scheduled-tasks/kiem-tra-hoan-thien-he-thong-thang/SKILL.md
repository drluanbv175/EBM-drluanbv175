---
name: kiem-tra-hoan-thien-he-thong-thang
description: Quét hoàn thiện kỹ thuật hàng tháng cho CẢ hệ nghiên cứu G0-G10 lẫn hệ cập nhật chứng cứ lâm sàng — dây nối cổng, doctrine agent, đối chiếu 2 repo, CI, tài liệu lỗi thời; khác 4 tác vụ hiện có (chỉ lo nội dung/an toàn chứng cứ)
---

Đây là tác vụ nền hằng tháng cho dự án EBM Copilot của bác sĩ Luân — repo gốc
`/Users/nguyenluan/Library/CloudStorage/OneDrive-Personal/Claude AI` (nhánh làm việc hiện tại;
kiểm bằng `git branch --show-current`, remote `drluanbv175/EBM-drluanbv175`) và repo nghiên cứu
sống lồng bên trong `medical-ebm-automation/` (remote `drluanbv175/medical-ebm-automation`,
venv `~/.ebm-venv`). Đọc kỹ `CLAUDE.md` ở gốc TRƯỚC khi làm gì — đó là doctrine đầy đủ, rất dài,
ghi lại hàng trăm bài học đã vá; tự đối chiếu doctrine với mã sống thay vì tin lời khai trong đó.

MỤC ĐÍCH TÁC VỤ NÀY — khác hẳn 4 tác vụ lịch nền hiện có (`thu-thap-tuan-an-toan-thuoc`,
`goi-duyet-tuan-ebm`, `cap-nhat-thang-ebm`, `giam-sat-acc-aha-quy` — cả 4 đều lo NỘI DUNG/AN
TOÀN chứng cứ lâm sàng, quét PubMed, cảnh báo thuốc). Tác vụ này lo **HOÀN THIỆN KỸ THUẬT CỦA
CHÍNH HỆ THỐNG**: dây nối cổng chất lượng, doctrine agent có theo kịp mã không, 2 repo có đối
chiếu nhau không, CI có chạy thật không, tài liệu CLAUDE.md có đoạn nào ghi số liệu/trạng thái
đã lỗi thời so với thực tế không. Đây là một "kiểm tra sức khỏe kỹ sư" định kỳ, không phải quét
chứng cứ y khoa.

QUY TẮC BẮT BUỘC (dự án này có kỷ luật rất cao — đọc CLAUDE.md để hiểu vì sao từng quy tắc
tồn tại, phần lớn xuất phát từ một lỗi thật đã xảy ra):
1. KHÔNG tin lời tự khai "đã sửa"/"PASS" trong CLAUDE.md — luôn TỰ CHẠY LẠI mã sống để xác nhận.
   Dự án này đã nhiều lần phát hiện tài liệu nói một đằng, mã sống chạy một nẻo ("đo đúng, nhưng
   đo nhầm chỗ" — lớp lỗi lặp lại nhiều lần, xem BH93 và các đính chính trong CLAUDE.md).
2. Trước khi kết luận về `medical-ebm-automation/`, kiểm cây có lạc hậu không:
   `cd medical-ebm-automation && git fetch origin --quiet && git status` — repo này từng bị
   phát hiện lạc hậu 55 commit khiến một đợt kiểm toán trước đó kết luận sai hàng loạt (BH93).
   KHÔNG tự `git fetch` nếu việc đó sẽ kéo hàng trăm MB trên máy không phù hợp — chỉ đo, báo
   cáo nếu lạc hậu, KHÔNG tự ý merge/rebase/reset.
3. Nhiều phiên Claude Code khác (kể cả worktree) có thể đang chạy song song trên cùng repo —
   LUÔN `git status` trước khi sửa bất kỳ file nào; nếu thấy thay đổi lạ không phải của mình,
   để nguyên, chỉ ghi nhận.
4. Sửa TRỰC TIẾP khi: lỗi tài liệu lỗi thời có bằng chứng rõ ràng (đối chiếu bằng lệnh thật),
   comment sai, một dòng cấu hình sai rõ ràng, đường dẫn hỏng trên nền tảng khác. KHÔNG tự sửa
   mã cổng an toàn/logic chấm điểm y khoa/nội dung lâm sàng/quyết định `decision`/`gradeLevel`
   — những việc đó CHỈ báo cáo, để phiên có người theo dõi xử lý.
5. TUYỆT ĐỐI không xóa bất cứ gì — luôn move/quarantine/backup với hậu tố thời gian nếu cần
   cách ly nội dung nghi ngờ.
6. Sau khi sửa: chạy lại chốt hồi quy liên quan + `python3 tools/chot_hoi_quy_bai_hoc.py` (root)
   trước khi commit. Nếu sửa gì bên trong `medical-ebm-automation/`, chạy thêm
   `cd medical-ebm-automation && ~/.ebm-venv/bin/python -m pytest -k "<phần liên quan>" -q`.
7. Nếu mọi thứ sạch (không tìm ra gì cần sửa), đó là kết quả HỢP LỆ — không cần bịa việc để làm.

VIỆC CẦN KIỂM MỖI LẦN CHẠY (8 mảng, làm tuần tự hoặc song song tùy khả năng của phiên chạy):

**① Dây nối 11 cổng G0-G10.** `grep -n "quality_gate\|evaluate_study" medical-ebm-automation/tools/approve_gate.py`
rồi đọc quanh mỗi match — xác nhận 6 cổng cứng canonical (G2,G4,G5,G8,G9,G10) đều có lời gọi
`gN_quality_gate.evaluate_study` THẬT trước dòng ghi ledger. Chạy
`cd medical-ebm-automation && ~/.ebm-venv/bin/python -m pytest tests/test_approve_gate_quality_gate_wiring_20260824.py -v`
để xác nhận hồi quy còn PASS thật.

**② Tautology scan trên 2-3 cổng CHƯA từng soi kỹ gần đây** (đổi ngẫu nhiên mỗi lần chạy để dần
phủ hết 11 cổng — G0,G1,G3,G4,G5,G6,G7,G8,G9,G10): đọc `tools/gN_quality_gate.py` tương ứng,
xác minh vài luật AUTO có kiểm nội dung THẬT SỰ THAY ĐỔI theo dữ liệu đề tài hay chỉ đếm chuỗi
mà bộ sinh artifact luôn in cứng (tautology — lớp lỗi đã gặp nhiều lần ở G3/G8).

**③ Doctrine agent có theo kịp luật cổng mới không.** Rà CLAUDE.md tìm mọi bản vá cổng G/quality
gate trong 60 ngày gần nhất (tìm theo ngày ghi trong file), rồi grep xem khái niệm mới đó (tên
trường, luật mới) có được nhắc trong `.claude/agents/*.md` liên quan không — đúng luật nền BH39
"thêm luật ở CỔNG thì phải DẠY AGENT cùng lúc". Chạy `python3 tools/kiem_dieu_phoi.py` xác nhận
vẫn 🟢.

**④ Sức khỏe từng đề tài THẬT.** `cd medical-ebm-automation && ~/.ebm-venv/bin/python tools/list_studies.py`
rồi với mỗi đề tài thật (không phải fixture ZZ*/PYTEST-*/REFUTE-*), chạy
`~/.ebm-venv/bin/python tools/kiem_chi_tiet_he_nghien_cuu.py --study <mã> --no-write` — báo cáo
nếu có 🔴 mới xuất hiện so với lần trước (không có "lần trước" để so thì chỉ báo cáo hiện trạng).

**⑤ Đối chiếu 2 repo + CI thật.** `python3 tools/verify_claude_code_repo_alignment.py` (root) và
bản trong `medical-ebm-automation/` nếu có. Kiểm CI THẬT (không suy đoán) bằng
`gh run list --repo drluanbv175/EBM-drluanbv175 --limit 3 --json databaseId,status,conclusion,headSha`
và tương tự cho `drluanbv175/medical-ebm-automation` — xác nhận job thật sự chạy (không phải
`runner_id:0` hay `queued` treo, dấu hiệu Actions bị tắt ở cấp tài khoản như đã từng xảy ra
09/2026). Nếu CI đỏ hoặc không chạy thật, báo rõ — đây là việc CHỈ bác sĩ xử lý được qua giao
diện web GitHub (Settings → Actions), không phải lỗi agent sửa được.

**⑥ Nhánh mồ côi / worktree có việc thật chưa merge.** `git worktree list` và
`git branch -a --sort=-committerdate | head -20` (root repo) — nếu thấy nhánh có commit thật
(không phải nhánh rác/thử nghiệm) mang sửa lỗi có giá trị mà chưa vào nhánh làm việc chính, ghi
rõ tên nhánh + commit hash + tóm tắt để báo cáo, KHÔNG tự ý merge (rủi ro cao, cần người xem lại).

**⑦ Quét CLAUDE.md tìm khẳng định lỗi thời.** Chọn 3-5 đoạn "ĐÍNH CHÍNH"/"đã vá"/"PASS" gần
ngày nhất trong CLAUDE.md (root), ưu tiên đoạn có con số/lệnh cụ thể kiểm được, chạy đúng lệnh
đó để xác minh còn khớp không. Sửa trực tiếp (thêm đính chính mới, KHÔNG xóa đính chính cũ) nếu
tìm ra sai lệch rõ ràng và an toàn để tự sửa (chỉ sửa văn bản mô tả, không phải số liệu y khoa).

**⑧ Chốt hồi quy tổng + kho công cụ.** `python3 tools/chot_hoi_quy_bai_hoc.py` (root, kỳ vọng
sạch, ghi rõ nếu có "BÀI HỌC TÁI PHÁT"). `python3 tools/kiem_plugin_day_du.py` — kho công cụ có
đủ không (🟢/🟡/🔴).

BÁO CÁO: viết một bản tóm tắt ngắn gọn BẰNG TIẾNG VIỆT (đúng theo chỉ thị ngôn ngữ toàn cục của
người dùng) liệt kê: mảng nào sạch, mảng nào có việc cần bác sĩ xử lý (kèm lệnh cụ thể để tự
chạy), mảng nào đã tự sửa (kèm bằng chứng). Nếu có sửa file: `git status` để chắc không đè lên
việc người khác, rồi commit theo đúng lệ dự án (thông điệp tiếng Việt, mô tả ngắn gọn WHY) và
`git push` CHỈ lên nhánh làm việc hiện tại. TUYỆT ĐỐI KHÔNG tự gộp, fast-forward hay đẩy vào
`master` (bác sĩ đã bỏ quy tắc tự gộp ngày 20/09/2026): mọi thay đổi vào `master` chỉ đi qua Pull
Request do bác sĩ duyệt; nếu nhánh làm việc đã có PR mở thì chỉ đẩy commit lên nhánh đó. KHÔNG hỏi
lại người dùng — đây là phiên chạy nền không có ai theo dõi trực tiếp; nếu gặp quyết định thật sự cần
người (không phải việc máy tự quyết được), chỉ ghi vào báo cáo, không dừng lại chờ.