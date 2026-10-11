# 10/10/2026 — Không có một thước đo «agent đã hoàn thiện» chung ⇒ mỗi vòng phải rà mở lại từ đầu (tốn thời gian, token)

Bác sĩ giao: «Mỗi Agent, mỗi điều phối xây dựng đảm bảo tiêu chuẩn hoàn thiện cho tôi, hãy xây dựng từng Agent một cho
tới khi hoàn thiện để khỏi phải tốn thời gian và Token».

## Đo (10/10)

- Các bộ kiểm rời rạc đã có (khung doctrine `agent_gate_governance`, khối sinh `sinh_tai_lieu_trach_nhiem`, lệnh trong tài
  liệu, phân công tiêu chí, chốt chống mồ côi) nhưng KHÔNG có bảng «agent nào đạt, thiếu gì» ⇒ mỗi vòng «hoàn thiện từng
  agent» phải đo lại bằng tay.
- Đo lần đầu bằng công cụ mới: **agent 62/64, điều phối 11/13**. Hai nhiệm vụ chỉ dựa đánh giá chéo, không kiểm máy:
  G1-T8 `kinh-te-y-te` (đầu ra docx dựng từ JSON tự do) và G7-T2 `hieu-dinh-song-ngu` (không có tệp đầu ra riêng) — kéo
  theo D3 của `dieu-phoi-g1`, `dieu-phoi-g7`.

## Vá

Repo y khoa (PR xếp chồng trên drluanbv175/medical-ebm-automation#108):
- `tools/tieu_chuan_hoan_thien.py` (mới) — MỘT thước đo, dùng lại đúng bộ kiểm có sẵn: agent A1 khung doctrine · A2 có
  điều phối giao việc · A3 khối sinh khớp · A4 mọi nhiệm vụ có kiểm máy (tiêu chí bộ chấm hoặc kiểm cấp nhiệm vụ) · A5 lệnh
  chạy được · A6 bản Codex; điều phối cổng D1 bảng §3 khớp · D2 phủ đủ tiêu chí bộ chấm (AST) · D3; nhạc trưởng lâm sàng L1;
  điều phối tổng N1/N2. Logic quét lệnh dời về đây làm MỘT nguồn (test kiểm lệnh dùng lại).
- G1-T8: đầu ra `G1_KINH_TE_Y_TE_<mã>.md` — 10 trường cố định; kiểm máy: đủ trường, loại CEA/CUA/CBA/BIA, chuẩn báo cáo
  khớp loại, WTP/chi phí có nguồn hoặc «chủ nhiệm ấn định», chiết khấu %/«N/A — lý do», không PII (docx nộp vẫn xuất bằng
  `gen_research_docx`).
- G7-T2: đầu ra `G7_A8_MANUSCRIPT_EN_<mã>.md` — kiểm máy bảo toàn tuyệt đối mọi con số (bỏ dấu phân cách, bỏ ngày dạng
  số), PMID, DOI của bản gốc `G7_A8_MANUSCRIPT_<mã>.md`; ≤ 5% dòng còn chữ tiếng Việt.

Repo gốc (PR này): `kinh-te-y-te.md` (mẫu 10 trường + luật), `hieu-dinh-song-ngu.md` (hợp đồng bản tiếng Anh), bảng §3
`dieu-phoi-g1/g7`, `_HOI-DONG-CONG.md` §1b mục 12, CLAUDE.md §1 một dòng TIÊU CHUẨN HOÀN THIỆN.

## Kiểm

- Sau vá: **agent 64/64 ĐẠT · điều phối 13/13 ĐẠT**; test chốt giữ mức đó (không lùi).
- `tests/test_tieu_chuan_hoan_thien_20261010.py`: 30 ca — mỗi hạng mục bắt được vi phạm trên bản sao thư mục agent; hai
  test vòng trước chốt đầu ra docx cũ của G1-T8 được cập nhật theo hợp đồng mới (giữ canh gác khoá artifact docx).
- Đột biến **14/14** bị bắt, CÓ lượt nền xanh.
