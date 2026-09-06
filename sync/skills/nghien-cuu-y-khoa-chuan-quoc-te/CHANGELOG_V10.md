# Cập nhật v10 (nội dung 5.4) — 2026-09-06

Đợt bảo trì theo `workflows/08`: **nâng khuôn đề cương 16 → 18 mục cấp 1** trong `templates/01_mau_de_cuong_tong_the.md`, đồng bộ canon máy đọc và bộ kiểm. Không đổi khung cổng G0-G9, không đổi cấu trúc Phụ lục.

## Báo cáo phát hành tối thiểu (theo workflow 08)

- **Phiên bản:** nội dung 5.4 (CHANGELOG v10).
- **Ngày:** 2026-09-06.
- **Người chỉnh sửa:** bảo trì qua Claude Code (phiên cloud), theo yêu cầu bác sĩ "đảm bảo mẫu đề cương, bài báo và mọi thứ đạt chuẩn"; tác giả con người kiểm chứng và chịu trách nhiệm.
- **Vì sao (đo được, không suy đoán):** đề tài thật `hai-long-benh-nhan-C1a-BVQY175` có HAI bản đề cương — bản viết tay 1272 dòng đã có Tổng quan tài liệu (§3.1–3.5), khung tham chiếu SERVQUAL/PSQ-18 và 6 bảng trống; bản `DE_CUONG_THONG_NHAT` do G10 lắp theo khuôn 16 mục thì không có chỗ chứa ba nội dung đó và ma trận 20 thành phần cũng không đòi. Khuôn thiếu ⇒ đề cương máy lắp giao hội đồng sẽ thiếu đúng ba chương hội đồng luôn hỏi.
- **File đã thay đổi (repo gốc):**
  - `templates/01_mau_de_cuong_tong_the.md` — thêm §3 *Tổng quan tài liệu và khung lý thuyết*, §13 *Dự kiến kết quả và khung bảng trống*; đổi tên §14 *Sai lệch, hạn chế và kiểm soát* (thêm bullet phạm vi/hạn chế dự kiến); đánh số lại §4–§18 và mọi "xem mục N"; khối kiểm soát nhắc Danh mục chữ viết tắt + Mục lục.
  - `MANIFEST.md` — bump 5.3 → 5.4.
  - `CHANGELOG_V10.md` — tệp này.
  - `.claude/agents/dieu-phoi-nghien-cuu.md`, `.claude/agents/_CROSSWALK-NGHIEN-CUU.md` — "mẫu 16 mục" → 18.
- **File đã thay đổi (repo `medical-ebm-automation`):**
  - `tools/skill_standards.py` — `DE_CUONG_SECTIONS` 18 mục; `DE_CUONG_SECTION_KEYS` + `de_cuong_heading()/de_cuong_sub_heading()` (số mục suy từ vị trí — không viết cứng nữa); `PROTOCOL_CORE_ITEMS` 20 → 23 (P21 tổng quan · P22 khung lý thuyết hoặc lý do không áp dụng · P23 dự kiến kết quả); P16 thêm "hạn chế dự kiến".
  - `tools/research_study_spec.py` — khối `literature` · `theory` · `expected_results` · `bias.limitations` trong StudySpec; luật P16/P21–P23; yêu cầu quyết định D17 (tổng quan + khung lý thuyết) và D18 (khung bảng trống).
  - `tools/run_g10_assemble.py` — `sec_tongquan()`, `sec_dukien_ketqua()`, `build_abbreviations()`; mọi tiêu đề mục lấy qua helper; số chương/thành phần in động.
  - `tools/check_de_cuong.py` — R1 đọc số mục từ canon (khoá kiểm `R1_16_sections` → `R1_sections`); R14 khớp `\d+` thành phần.
  - Test: `tests/test_de_cuong_18_muc_20260906.py` (mới, có ca đột biến), `test_skill_standards.py`, `test_g10_assemble.py`, `test_research_study_spec.py`.

## Ranh giới của bản này

- Mã P là **hợp đồng dữ liệu**: chỉ thêm P21–P23 vào cuối, không đánh số lại P01–P20 (giữ study_meta/checkpoint/báo cáo cũ đọc được).
- G10 vẫn **không viết văn xuôi học thuật**: §3 chỉ dựng khung + nhồi dữ liệu thật (số tài liệu G0, Evidence Ledger A2b, trường study_meta); tổng hợp y văn do `tong-quan-y-van`/bác sĩ soạn. §13 chỉ khung bảng — mọi con số bị R6 cảnh báo.
- Đề cương đã lắp bằng khuôn 16 mục phải **chạy lại G10** để có mục mới; validator sẽ báo thiếu mục 3/13 trên bản cũ — đó là hành vi mong muốn.
- Chưa có checklist theo từng mục SPIRIT 2025/PRISMA-P sinh kèm đề cương (chỉ kiểm TÊN chuẩn ở G1); danh mục item phải lấy từ nguồn chính thức, chưa lấy được trong phiên này — ghi ở CLAUDE.md gốc.
