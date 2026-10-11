# 11/10/2026 — PI chốt tính mới G0 (C1a) trên bản nháp bỏ sót DOI trong nước mà hội đồng đã giao

## Đo

- Bác sĩ chạy công cụ một chạm `Chot FINER C1a.command` (agent viết, chỉ soạn câu chữ) và chốt G0 lúc 09:02:59 ⇒
  `PASS_G0_CONFIRMED`. Câu tính mới lấy nguyên từ `G0_KHOANG_TRONG_*.json` (agent soạn 10/10): «chưa thấy dữ liệu
  công bố về mức hài lòng… tại một khoa khám theo yêu cầu của bệnh viện quân y tuyến cuối».
- Biên bản tranh biện BD-G0-T2 (07/10, `sua_ket_luan`) đã giao gộp 5 DOI trong nước vào MỘT danh mục đọc cho PI; bản
  nháp 10/10 bỏ sót cả 5. Trong đó doi:10.52163/yhc.v67icd5.5018 (Tạp chí Y học Cộng đồng 2026, n=445, có đo hài lòng,
  Khoa Khám bệnh theo yêu cầu BV TƯQĐ 108 — xác minh Crossref) mâu thuẫn trực tiếp với câu đã chốt; hai bài khác ở
  chính BV Quân y 175 (khoa YHCT).
- `hoi_dong_cong.py trach-nhiem --gate G0` vẫn báo DAT_TIEU_CHI (mã 0): bảng trách nhiệm KHÔNG đọc việc treo của hội
  đồng. Cùng lúc `study_readiness` báo G1 «HỎNG» vì `hoi_dong/G1/ap_dung_nhiem_vu.json` bị đọc như biên bản.
- Dấu vân tay G0 (`dau_van_tay_g0`) băm chủ đề + PMID PubMed + `gate_params.G0` — KHÔNG băm danh mục bổ sung ⇒ danh
  mục đọc đổi sau khi PI chốt thì cổng vẫn PASS.
- Guardrail R4 của G1 chỉ nhận PMID đứng gần một hiệu số ⇒ số liệu từ tạp chí trong nước chỉ có DOI bị coi «nghi bịa».

## Vá

- Repo y khoa #118: `trach_nhiem` thêm `hoi_dong_treo` (CẦN SỬA · BẤT ĐỒNG · CHUYỂN BÁC SĨ · HỎNG · KHÔNG ĐO ĐƯỢC),
  in cảnh báo; `doc_bien_ban` bỏ qua đúng tệp khai áp dụng. TƯ VẤN — không đổi kết luận/mã thoát.
- Repo y khoa #117: gộp 9 DOI trong nước vào `G0_TONG_HOP_BANG_CHUNG` (kiểm rút bài Crossref + Retraction Watch), soạn
  lại khoảng trống/tính mới/FINER-N, dựng lại A1 bằng `--dung-lai-a1` (không tra lại PubMed); đính chính nháp G1. PI
  chốt lại G0 bằng công cụ (công cụ nay hiện tình trạng hội đồng trước khi PI đọc).

## Bài học

- Công cụ soạn sẵn cho PI chốt phải đối chiếu BIÊN BẢN HỘI ĐỒNG còn hiệu lực của cổng (yêu cầu sửa, nguồn được giao)
  trước khi lấy bản nháp — bản nháp mới nhất chưa chắc đã làm theo biên bản.
- «Phần agent hoàn chỉnh» không được báo xanh khi hội đồng còn yêu cầu sửa giao cho agent.
- Còn mở (chờ bác sĩ quyết): đưa danh mục bổ sung vào dấu vân tay G0; cho R4 nhận DOI.
