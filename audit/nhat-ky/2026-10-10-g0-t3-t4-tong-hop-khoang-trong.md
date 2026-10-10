# 10/10/2026 — G0-T3/T4 bị hội đồng trả về sửa: A1 chỉ là số hit + tiêu đề 5/12 bài, khoảng trống phủ định không ghi phạm vi

Bác sĩ giao: «Những vấn đề chưa hoàn thiện của Agent và điều phối hãy hoàn thiện từng vấn đề cho tôi». Hai biên bản đánh
giá chéo của hội đồng G0 (C1a, 07/10/2026 — `G0-DG-20261007T182841-0b213597` cho G0-T3 `tong-quan-y-van`,
`…-79f9a227` cho G0-T4 `khoang-trong-nghien-cuu`) đều «trả về sửa».

## Đo (10/10, đọc biên bản + mã sống)

- A1 do bộ sinh bản 31/07 dựng, chưa sinh lại: `_format_article_list(max_show=5)` ⇒ §3.5 chỉ hiện 5/12 PMID, giấu đúng
  4 bài sát đề tài nhất (34445940, 36439278, 32584904, 31703089) trong khi G0-HUMAN-06 bảo PI «đọc danh sách PMID ở §3».
- `analyze_evidence_gaps` viết «Chưa có systematic review / Chưa có RCT / Chưa có guideline» từ 0 hit của MỘT truy vấn
  gắn «Vietnam» — lan nguyên văn sang sổ chứng cứ G1 và đề cương G10 (StudySpec ưu tiên `research_gaps` của máy hơn
  `knowledge_gap`/`novelty_justification` do người viết), trái QĐ 56/QĐ-BYT 2024 mà chính đề cương dẫn.
- Câu hỏi mô tả (cắt ngang đã ghim) vẫn nhận «chưa có RCT» làm khoảng trống và gợi ý «RCT … HOẶC Cohort».
- Khối bàn giao A1 thiếu đúng khoá bộ chấm đòi (lý do FINER, `dau_van_tay_chot`, `registry_manual_checked`); «~13%» văn
  mẫu không nguồn; ô «[suy ra từ topic]» trái «hệ KHÔNG suy PICO»; checkpoint lưu `PASS_G0_CONFIRMED` cũ trái chấm sống.
- Không có chỗ nào cho công ĐỌC BÀI của agent: viết thẳng vào A1 thì lần chạy lại G0 xoá sạch.

## Vá

Repo y khoa (PR riêng):
- `tools/g0_tong_hop.py` (mới) — hai tệp dữ liệu, mỗi agent một tệp: `G0_TONG_HOP_BANG_CHUNG_<mã>.json` (G0-T3: sàng
  lọc ĐỦ mọi PMID nền · nguồn bổ sung kèm cách tìm PRISMA-S · tóm lược dẫn PMID liên quan trực tiếp · kiểm rút bài) và
  `G0_KHOANG_TRONG_<mã>.json` (G0-T4: bảng guideline/văn bản quy phạm · phát biểu 1–2 câu cấm tuyệt đối hoá · loại +
  mức tính mới · trạng thái nguồn · nháp FINER với F/E bắt buộc «CẦN PI QUYẾT —»). Bộ kiểm cấu trúc dùng chung cho bộ
  sinh A1 và bảng trách nhiệm (`KIEM_NHIEM_VU` G0-T3/T4); ngày dd/mm/yyyy bị chặn vì guardrail R2 coi là nghi ngày sinh
  (đo thật: lượt dựng lại đầu tiên làm C1a thành BLOCKED).
- `run_g0_auto.py`: liệt kê đủ bài; khoảng trống phủ định ghi phạm vi; câu hỏi không can thiệp không nêu thiếu RCT; thiết
  kế đã ghim/loại câu hỏi đi trước gợi ý theo số hit; năm mới nhất tính mọi nhánh; PHẦN 4b + §3.0; khối bàn giao đúng
  khoá; `--dung-lai-a1` (dựng lại A1/DOCX từ `G0_pubmed_raw.json`, KHÔNG tra lại PubMed, giữ tập PMID); thiếu `--topic`
  mà không dựng lại ⇒ từ chối (trước đây sẽ ghi checkpoint BLOCKED đè hồ sơ); đường dẫn artifact trong checkpoint tương
  đối theo gốc repo; lưu tác giả vào dữ liệu thô.
- `research_study_spec.py`: khoảng trống do người viết đi trước câu suy của máy.
- `sinh_tai_lieu_trach_nhiem.py`: khối trách nhiệm luôn hiện kiểm máy cấp nhiệm vụ (bản cũ ẩn khi nhiệm vụ có tiêu chí).
- C1a: hai tệp agent soạn từ tóm tắt PubMed 20 PMID (12 nền: 4 trực tiếp · 3 gián tiếp · 5 không liên quan; 8 bổ sung),
  kiểm rút bài 20/20 «OK» theo PubMed 10/10/2026; A1 dựng lại, guardrail PASS, G0 vẫn DRAFT_READY (4 việc của PI).

Repo gốc (PR này): `tong-quan-y-van.md`, `khoang-trong-nghien-cuu.md` (hợp đồng đầu ra + khối sinh), `dieu-phoi-g0.md`
(«dựng lại A1 ≠ tra lại PubMed»).

## Kiểm

- `tests/test_g0_tong_hop_bien_ban_20261010.py`: 21 ca; một test cũ chốt chuỗi «hiển thị» đổi sang «liệt kê đủ» (giữ ý tách
  số hit khỏi số bài).
- Đột biến 14/14 bị bắt, có lượt nền xanh (909 test nhóm G0/hội đồng/StudySpec).
- Bảng trách nhiệm G0 của C1a sau sửa: AGENT_XONG_CHO_NGUOI (đo trong worktree). Hai biên bản 07/10 chuyển trạng thái «cũ»
  (tài liệu đã đổi) — xác nhận chất lượng cần hội đồng chấm chéo lại, việc tốn token nên hỏi bác sĩ trước.
