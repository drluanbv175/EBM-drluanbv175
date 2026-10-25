# 25/10/2026 — Bản clone lồng làm `pytest` y khoa dừng · nhãn «ĐỒNG THUẬN» che phần hội đồng chưa họp · đếm việc tính tiêu chí của cổng đã qua

Phát hiện khi bác sĩ hỏi «hệ thống nghiên cứu đã đạt trạng thái tự động hoàn thiện tốt nhất chưa» (đo sống 25/10, 13:40).
Thước đo tổng (64/64 agent, 13/13 điều phối, 0 việc agent, 🔴 0) đều đạt — ba lỗi dưới đây nằm NGOÀI các thước đo đó.

## 1. Bản clone lồng làm `pytest` của repo y khoa dừng ở bước thu thập

**Hiện tượng.** `medical-ebm-automation/medical-ebm-automation/` là một bản `git clone` thứ hai của chính repo y khoa
(reflog: clone 07:43; 48 MB, 2.110 tệp; có fetch lúc 13:31). `pytest` ở gốc repo y khoa thu thập trùng
`tests/conftest.py` ⇒ `ImportPathMismatchError`, «3 errors during collection», cả lượt dừng. CI không thấy (CI clone sạch).
`git status` chỉ hiện `?? medical-ebm-automation/` — `sync_safety_check` đếm «1 thay đổi chưa commit», không nói là gì.

**Vá (PR y khoa drluanbv175/medical-ebm-automation#190).** `pytest.ini` thêm `--ignore=medical-ebm-automation`;
`.gitignore` thêm `/medical-ebm-automation/` (chặn `git add -A` đưa bản clone vào thành gitlink). Đo trên cây chính có
bản clone: không rào 9.042 test + 3 lỗi · có rào 9.042 test, 0 lỗi.

**Nguồn gốc (đo, chưa kết luận).** Repo gốc cũng chứa một bản clone của CHÍNH nó: `EBM-drluanbv175/` (40 MB), reflog chỉ
toàn `pull --ff --recurse-submodules --progress` (19/10, 20/10, 25/10 07:43:18) — dạng lệnh do app git có giao diện chạy.
Bản lồng của repo y khoa được clone lúc 07:43:46, 28 giây sau. Có thể cả hai do cùng một app git của bác sĩ; chưa xác minh.
Repo gốc chỉ chạy `pytest tools/` nên `EBM-drluanbv175/` không làm vỡ test.

**Chưa làm (👤).** Hai bản clone KHÔNG bị xoá hay dời. Nếu là bản của app git, nên trỏ app tới nơi NGOÀI hai repo (vd
`~/.ebm-worktrees/` hoặc thư mục ngoài OneDrive) để không nhân đôi 88 MB qua OneDrive.

## 2. «ĐỒNG THUẬN» của hội đồng cổng là nhãn gộp che phần chưa họp

**Hiện tượng.** `hoi_dong_cong.tom_tat_cong` (đọc bởi `study_readiness`, `audit_research_gates`, bảng trách nhiệm) trả
«ĐỒNG THUẬN» khi các biên bản CÒN HIỆU LỰC không có bất đồng — không xét nhiệm vụ nào chưa từng được chấm. C1a G1 báo
«ĐỒNG THUẬN» trong khi chỉ G1-T4 có biên bản; G1-T1…T3 đủ đầu ra mà chưa ai chấm (`uoc-tinh` cùng lúc báo G1 «HỌP ĐƯỢC»).
Tương tự G3 (G3-T1) và G10 (G10-T1, G10-T2). Đúng dạng CLAUDE.md §0.2: chỉ số gộp nói thay cho toàn bộ.

**Vá.** Trạng thái mới «ĐỒNG THUẬN MỘT PHẦN» (tư vấn, không thuộc `TRANG_THAI_CAN_XU_LY`): nhiệm vụ áp dụng hoặc chưa xác
định áp dụng, ĐỦ đầu ra, chưa có đánh giá chéo còn hiệu lực — cùng luật «can_cham»/«chua_xac_dinh» của `ho_so_cong`;
nhiệm vụ thiếu đầu ra là «chưa tới lượt», không tính; lý do nêu «chưa đánh giá chéo» hay «biên bản cũ — tài liệu đã
đổi». Fixture G4 cũ thiếu thiết kế (G4-T2 chỉ-RCT dùng chung SAP nên chưa xác định áp dụng) ⇒ fixture khai thiết kế cắt
ngang, assertion giữ nguyên.

## 3. `study_readiness` đếm tiêu chí của cổng đã qua thành «việc chưa làm»

**Hiện tượng.** 60 «việc chưa làm» của C1a gồm 5 dòng PHẦN 5 «TIÊU CHÍ QUA CỔNG G3» của `G3_A4` — G3 đã
PASS_G3_CONFIRMED; 2 dòng («effect size», «biến cố nền (sống còn)») không bao giờ áp dụng cho thiết kế mô tả theo độ chính
xác. `run_g3_auto.py` in cùng một checklist cho mọi thiết kế. `G3_A4` nằm trong bản kê G10 đã khoá ⇒ không tick được.

**Vá.** (a) `study_readiness`: khối «TIÊU CHÍ QUA CỔNG Gk» của cổng ĐẠT theo chấm sống (cổng mềm ✅, cổng cứng 🔒 có
chữ ký) không đếm; báo cáo in rõ «không đếm N dòng … — Gk đã đạt»; cổng mất trạng thái đạt ⇒ đếm lại ngay. C1a: 60 → 55.
(b) `run_g3_auto.py` PHẦN 5 theo thiết kế: mô tả độ chính xác ⇒ «p và d», so sánh ⇒ «effect size», sống còn (HR) mới có
«biến cố nền», có cụm mới có «ICC và cỡ cụm»; R6 (≥ 3 nhãn [CẦN) vẫn đạt.

## 4. Trục «Power» ⚪ vĩnh viễn ở thiết kế không có power

**Hiện tượng.** `nhat_quan_xuyen_cong` luôn so alpha và power. C1a tính N theo độ chính xác (p, d): SAP §12 không có dòng
power, G3 chỉ lưu mặc định 0,8 của bộ tính ⇒ «⚪ chỉ có ≤ 1 nơi ghi — chưa đủ để so», và `kiem_chi_tiet` mang ⚪ 1 mãi.

**Vá.** Bỏ trục không áp dụng khi nó «chưa đủ để so», theo khung §12 (`g4_quality_gate.loai_muc_12`): độ chính xác và
SR/dự báo không có power; định tính không có alpha lẫn power. Hai nơi ghi mà LỆCH nhau thì vẫn báo. Thiết kế so sánh mới
ghi một nơi vẫn hiện ⚪ (test giữ).

## Kiểm

Test mới: 3 ca hội đồng (`test_hoi_dong_cong_20261006.py`) + 10 ca (`test_tieu_chi_cong_dat_va_g3_theo_thiet_ke_20261025.py`).
Đột biến 12/12 bị bắt (bỏ nhánh một phần · bỏ kiểm đủ đầu ra · bỏ lý do «cũ» · bỏ loại «không áp dụng» · không bỏ khối ·
khối không kết thúc ở tiêu đề kế · báo cáo không nối cổng đạt · G3 luôn «effect size» · G3 luôn «biến cố nền» · không bỏ trục không áp dụng · bảng «chính xác» rỗng · bỏ cả trục đang lệch), phục hồi
khớp sao lưu. Lượt đột biến đầu ra «no tests ran» vì zsh không tách biến nhiều đường dẫn — đã chạy lại bằng `${=T}`.

## Bài học

Một hệ «đạt mọi thước đo» vẫn có thể sai ở chỗ không thước đo nào nhìn: nhãn gộp («đồng thuận»), bộ đếm bi quan đếm cả
tiêu chí đã thoả, và môi trường chạy test bị một thư mục lạ làm hỏng. Trước khi trả lời «đã tốt nhất chưa», đo cả ước
tính họp (`uoc-tinh`), từng dòng «việc chưa làm», và chạy thử `pytest --collect-only` trên cây thật.
