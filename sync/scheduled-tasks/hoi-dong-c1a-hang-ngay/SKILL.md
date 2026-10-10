---
name: hoi-dong-c1a-hang-ngay
description: 18:00 MỖI NGÀY (từ 11/10/2026) họp hội đồng MỘT cổng của đề tài C1a do máy chọn, rồi tự hoàn thiện đầu ra đề tài + hệ thống (công cụ/agent/điều phối) bằng PR — bác sĩ giao 10/10/2026
---

NỀN TẢNG: macOS + Windows. THƯ MỤC LÀM VIỆC = gốc thư mục OneDrive «Claude AI» của MÁY ĐANG CHẠY (repo EBM-drluanbv175):
- macOS: "$HOME/Library/CloudStorage/OneDrive-Personal/Claude AI"
- Windows: "%USERPROFILE%\OneDrive\Claude AI" (máy hiện tại: C:\Users\Admin\OneDrive\Claude AI)
Không thấy thư mục đúng ⇒ DỪNG và báo nguyên văn; không đoán đường dẫn khác.
Trên Windows đổi lệnh: `python3` → `py -3`; `~/.ebm-venv/bin/python` → `%USERPROFILE%\.ebm-venv\Scripts\python.exe`;
`~/.ebm-worktrees` → `%USERPROFILE%\.ebm-worktrees`.
Đường dẫn tương đối viết bằng `/` dùng được nguyên trên cả hai; tệp tạm ghi vào `state/` của thư mục làm việc, không dùng `/tmp`.

NGÀY BẮT ĐẦU: bác sĩ hẹn bắt đầu 18:00 ngày 11/10/2026. Lượt chạy trước ngày đó (ngày hệ thống < 2026-10-11) ⇒ DỪNG
NGAY, không chạy lệnh nào khác, không ghi báo cáo.

BỐI CẢNH. Bác sĩ (PI, quản trị duy nhất của hệ) giao ngày 10/10/2026: «Việc họp như vậy sẽ như hoàn thiện đề tài
nghiên cứu của tôi, mỗi ngày họp một cổng và với lần họp này sẽ đảm bảo hệ thống được hoàn thiện tự động tốt nhất từ
vấn đề hệ thống, Agent và các điều phối» và «Bắt đầu từ 18h ngày mai». Đề tài: `hai-long-benh-nhan-C1a-BVQY175`.
Quy trình chuẩn nằm ở `.claude/agents/_HOI-DONG-CONG.md` §5, đoạn «Nhịp hằng ngày + vòng hoàn thiện sau họp» — ĐỌC
đoạn đó và §3 (rubric, bài học hệ thống) trước khi làm. Hội đồng là TƯ VẤN: không mở, không chặn cổng. Mọi báo cáo
bằng TIẾNG VIỆT. Repo y khoa lồng ở `medical-ebm-automation/` (venv `~/.ebm-venv`); mọi lệnh `tools/hoi_dong_cong.py`
dưới đây chạy TRONG `medical-ebm-automation/`. Không đặt thư mục làm việc trong `exports/<đề tài>`.

BƯỚC 0 — an toàn và điều kiện (chỉ đọc, 0 agent):
a. Repo gốc: `python3 tools/sync_safety_check.py` — 🔴 ⇒ DỪNG, vẫn ghi báo cáo ngày (bước 5) với lý do.
b. Cập nhật cây chính, KHÔNG đổi nhánh/stash/reset: repo gốc `git fetch origin && git pull --ff-only origin master`;
   repo y khoa (phải đang ở `feat/r1-1-2-design-gap-remediation`) `git fetch origin && git pull --ff-only origin
   feat/r1-1-2-design-gap-remediation`. Pull thất bại ⇒ để nguyên, ghi vào báo cáo. Thay đổi chưa commit của phiên khác
   ở cây chính: để nguyên. Sau khi kéo: `python3 tools/sync_agents_to_codex.py --check` ở gốc; lệch ⇒ chạy không `--check`.
c. Điều kiện có công cụ: `python3 tools/hoi_dong_cong.py lich-hop --help`. Báo «invalid choice» ⇒ PR họp tiết kiệm/
   họp hằng ngày CHƯA được gộp vào cây chính ⇒ KHÔNG họp; ghi báo cáo ngày «chưa họp — cần bác sĩ gộp PR y khoa
   #114 và PR gốc #153 cùng hai PR họp hằng ngày nối sau chúng» rồi DỪNG.

BƯỚC 1 — chọn cổng (0 agent): `python3 tools/hoi_dong_cong.py lich-hop --study hai-long-benh-nhan-C1a-BVQY175 --json`.
`gate` null ⇒ hôm nay không họp: bỏ bước 2, vẫn làm bước 3–5. Có cổng ⇒ ghi lại `khuyen_nghi` và `uoc_tinh`
(`nen_cho_cong_truoc` vẫn họp — nhịp bác sĩ chọn — nhưng báo cáo phải nói biên bản có thể CŨ khi cổng trước chốt).

BƯỚC 2 — họp MỘT cổng: `python3 tools/hoi_dong_cong.py ho-so --study hai-long-benh-nhan-C1a-BVQY175 --gate <G> --json`,
rồi chạy Workflow đã lưu tên `hoi-dong-cong` (tệp `.claude/workflows/hoi-dong-cong.js` của repo gốc) với args
{"study": "hai-long-benh-nhan-C1a-BVQY175", "gate": "<G>", "ho_so": <JSON vừa in, nguyên văn, là đối tượng — không
phải chuỗi>, "max_vong": 1, "max_agent": 16}. Đúng MỘT lượt, MỘT cổng; KHÔNG dùng `dieu-phoi-tong-hoi-dong`. Workflow
lỗi/dừng giữa chừng ⇒ KHÔNG resume, KHÔNG chạy lại (tốn token) — đọc journal của lượt, ghi vào báo cáo đã ghi được gì.
Sau đó (chỉ đọc): `tom-tat --study …` và `trach-nhiem --study … --gate <G> --ghi`.

BƯỚC 3 — hoàn thiện ĐẦU RA đề tài: `python3 tools/hoi_dong_cong.py trach-nhiem --study … --gate <G> --json` (khi không họp:
cổng có biên bản «trả về sửa» gần nhất). Với mỗi mục `agent_con_viec` (hội đồng trả về sửa · kiểm máy · thiếu đầu ra):
sửa bằng CÔNG CỤ THẬT của cổng theo đúng biên bản (`run_g<N>_auto.py`, `g0_tong_hop.py`, `xuat_docx_chuan.py --file`…),
trong worktree mới `~/.ebm-worktrees/yk-hd-ngay-<YYYYMMDD>` tạo từ `origin/feat/r1-1-2-design-gap-remediation`;
chấm lại bằng `g<N>_quality_gate.py` và `trach-nhiem`; commit tiếng Việt (biến môi trường `EBM_WORKSPACE_ROOT` = THƯ
MỤC LÀM VIỆC; tệp `exports/` đã track thêm bằng `git add -u -- <thư mục>`), push, mở PR base
`feat/r1-1-2-design-gap-remediation`. Mục `cho_nguoi`, ô của PI/IRB/thống kê viên, mọi cờ xác nhận: KHÔNG điền —
chép vào báo cáo là việc của bác sĩ.

BƯỚC 4 — hoàn thiện HỆ THỐNG: `python3 tools/hoi_dong_cong.py bai-hoc --study … --chua-xu-ly --json`. Với mỗi bài học,
theo thứ tự `cong_cu` → `agent` → `dieu_phoi` → `doctrine` → `quy_trinh_hoi_dong`:
- Kiểm lại trên MÃ SỐNG (`git fetch` + đọc nhánh chính) — sai ⇒ `--ket khong_sua` kèm lý do có căn cứ.
- Xem PR đang mở của hai repo (`gh pr list --state open`) — đã có PR cho cùng vấn đề ⇒ `--ket trung`/ghi PR đó, không mở PR trùng.
- Đúng ⇒ sửa trong worktree `~/.ebm-worktrees/<goc|yk>-hd-ngay-<YYYYMMDD>`: chốt mới phải có test + kiểm đột biến (lượt
  nền xanh, sao lưu, phục hồi y hệt từng byte); sửa tài liệu agent thì chạy dây sinh mirror/manifest theo CLAUDE.md của
  repo đó; bản cặp agent/doctrine giữa hai repo phải y hệt byte; nhật ký sự cố một tệp `audit/nhat-ky/<ngày>-<slug>.md`
  ở repo gốc. Chạy bộ test liên quan; có sửa mã y khoa thì chạy bộ pytest đầy đủ ở nền trước khi mở PR.
- Commit tiếng Việt + push + PR, rồi `python3 tools/hoi_dong_cong.py bai-hoc --study … --xu-ly <mã> --ket da_sua --pr
  <URL> --ly-do "<đã sửa gì>"`.
Không đủ thời gian cho mọi bài học ⇒ làm theo thứ tự trên, phần còn lại để ngày sau (ghi báo cáo).

BƯỚC 5 — BÁO CÁO NGÀY (LUÔN ghi, kể cả khi dừng sớm hoặc không họp — đây là dấu vết của `tools/kiem_lich_nen.py`):
`medical-ebm-automation/exports/hai-long-benh-nhan-C1a-BVQY175/hoi_dong/BAO_CAO_NGAY_<YYYY-MM-DD>.md` (ngày chạy) gồm:
cổng đã họp + khuyến nghị + số agent thật đã dùng; mã biên bản đã ghi; từng nhiệm vụ qua/trả về sửa (lý do chính + căn
cứ); từng DP giữ/sửa kết luận/chuyển bác sĩ; PR đã mở (URL) và PR còn chờ bác sĩ gộp; bài học hệ thống đã/chưa xử lý;
việc của bác sĩ còn lại; dòng cuối «Cần bác sĩ kiểm chứng.». Không PII.

RANH GIỚI BẮT BUỘC: KHÔNG gộp PR (bác sĩ gộp), KHÔNG bật auto-merge; KHÔNG ký, KHÔNG chạy `approve_gate.py`; KHÔNG ghi
`gate_params`, cờ xác nhận, `reviewed_at`, `dau_van_tay_chot`; KHÔNG đụng `approval_ledger*`/seal; KHÔNG đọc/chép khoá
trong `~/.ebm-secrets`; KHÔNG sửa `.claude/hooks/`; KHÔNG `--no-verify`; KHÔNG PII; không đổi nhánh cây chính repo y
khoa; worktree chỉ ở `~/.ebm-worktrees` (không `/private/tmp`); không đọc DynaMed/Scopus/WoS; mọi đầu ra y khoa kèm
PMID/DOI + «Cần bác sĩ kiểm chứng»; không bịa định danh. Chi phí ước của một cổng: số `uoc_tinh` của bước 1
(đo 07/10/2026: ~380 nghìn token/agent) cộng phần sửa — không mở thêm agent ngoài workflow của bước 2.
