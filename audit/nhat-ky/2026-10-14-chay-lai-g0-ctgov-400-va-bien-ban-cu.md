# 14/10/2026 — Chạy lại tìm G0 (C1a): CT.gov trả 400 với chuỗi PubMed có thẻ trường; biên bản hội đồng G0 thành CŨ

**Bối cảnh.** Việc 4 của biên bản tranh biện BD-G0-T2 (hội đồng G0, 07/10): PI chọn chuỗi PubMed rồi chạy lại
`run_g0_auto.py` một lần. NCBI gỡ chặn IP chiều 14/10; chạy với chuỗi §5.2 của gói PRISMA-S (MeSH + từ tự do).
Repo y khoa PR #128 (commit 27e1c85).

## Sự cố 1 — tra đăng ký «CHƯA TRA ĐƯỢC» dù mạng tốt

- **Nguyên nhân:** `tools/trial_registry.py::check_trial_registry` gửi nguyên `base_query` sang ClinicalTrials.gov.
  Chuỗi cũ là từ thường nên chưa từng lộ; chuỗi mới có `[Mesh]`/`[tiab]` ⇒ CT.gov HTTP 400 ⇒ `checked=False`.
  Đo 14/10: bỏ thẻ trường ⇒ HTTP 200 (5 hồ sơ). Hàm dùng chung G0 + G2 ⇒ hồ sơ đạo đức G2 cũng dính nếu dùng chuỗi kiểu này.
- **Vá:** `truy_van_ctgov()` bỏ thẻ trường trước khi gửi, ghi chuỗi đã gửi vào `query_gui_ctgov` (truy nguyên PRISMA-S);
  liên kết «tra lại» dùng đúng chuỗi đó.
- **Kiểm hồi quy:** `tests/test_trial_registry_bo_the_pubmed_20261014.py` (4 test, giả CT.gov từ chối «[»); đột biến
  2/2 bị bắt (gửi lại chuỗi gốc; liên kết không chuẩn hoá).

## Sự cố 2 — chạy lại G0 làm lệch đầu ra agent và làm CŨ mọi biên bản G0

- Tổng hợp G0-T3 sàng theo nền cũ (12 PMID) ⇒ `g0_tong_hop.kiem_tong_hop` báo thiếu 8 PMID mới + 4 PMID ngoài nền.
  Phải sàng lại cùng lúc (8/16 bài nền mới lạc đề; recall 5 bài mốc: 0/5 có lọc thiết kế · 3/5 nhánh không lọc).
- Biên bản băm A1/checkpoint/tệp thô ⇒ cả 6 biên bản G0 (4 đánh giá chéo + 2 tranh biện) thành CŨ. Ước tính họp nở
  từ «2 agent chỉ BD-G0-T2, ~1 triệu token» thành 11–23 agent, 4,2–8,7 triệu (`hoi_dong_cong.py uoc-tinh`).
- **Bài học:** đo lại `uoc-tinh`/`ho-so` trên bản sao nội dung MỚI (biên bản ngoài git, chỉ ở cây chính) trước khi
  báo chi phí; họp SAU khi PI chốt lại (chốt ghi checkpoint).

## Kèm theo

- Nút `chot_g0_c1a.py` (ngoài git): đường chốt lại nhanh nhận cả ca G0-HUMAN-08 chỉ thiếu `registry_overlap_assessment`
  (gõ KHONG-TRUNG hoặc nhận định của PI; Enter trống không ghi). Diễn tập trên worktree: chốt lại xong ⇒ G0 + G1 PASS.
- Test `test_g0_c1a_dien_that_van_toi_pass`: kịch bản «bác sĩ làm đủ» thêm đánh giá chồng lấn (việc cổng nay đòi),
  assertion PASS giữ nguyên; đột biến bỏ bước này bị bắt.
