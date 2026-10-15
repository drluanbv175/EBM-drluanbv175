# 15/10/2026 — Đề cương lắp máy G10 không nộp được Hội đồng; khép việc «đề cương nộp» vào cổng, agent và điều phối

**Bác sĩ:** «Đề cương hoàn thiện hãy viết theo đúng chuẩn cả về từ ngữ, thuật ngữ y khoa… hiện tại đọc qua thì khó mà chấp
nhận được», rồi hỏi «phần hoàn thiện đề cương đã đảm bảo với cấu trúc các agent và điều phối chưa». Trả lời đo được lúc hỏi:
**CHƯA** — bản nộp đã viết và PR cổng G10 đã mở, nhưng danh mục hội đồng cổng không có nhiệm vụ nào giao việc này, không có
công cụ kiểm, khuôn ICF G2 vẫn sinh câu mẫu sai.

## Nguyên nhân

- `DE_CUONG_THONG_NHAT_<mã>` (G10) là hồ sơ TRUY XUẤT: bảng cổng, ký hiệu «SAP §», tên biến tiếng Anh, khối kiểm hoàn thành —
  chính `check_de_cuong.py` đòi các khối đó. Hệ chưa từng có khái niệm «văn bản nộp» tách khỏi bản lắp, nên chữ ký G10 phủ bản
  máy chứ không phủ văn bản PI thật sự nộp.
- Khuôn ICF của `run_g2_auto.py` ghép câu mẫu cho mọi kịch bản («lên lịch hẹn trùng tái khám», «tự điền hoặc qua điện
  thoại/email», «quyền xem/sửa/xóa dữ liệu» không điều kiện) — chép thẳng vào ICF của khảo sát cắt ngang một lần, khuyết danh.
- `_PHONE_RE` của G10 đọc nhầm DOI `10.1108/IJHCQA-07-2025-0100` thành số điện thoại.

## Đã vá

- **Bản nộp C1a** `DE_CUONG_NOP_HOI_DONG_<mã>.md/.docx`: viết lại theo khung đề cương gốc v1.0, phiếu khảo sát NGUYÊN VĂN
  phiếu gốc của bác sĩ; qua một agent `tham-dinh-dau-ra` (≈490 nghìn token) — 5 lỗi đỏ (nói quá nguồn, gán nhầm nguồn, ICF
  thiếu trường HIS, dự phòng tự báo cáo không có câu hỏi, mã 8 trùng 8 phút) đã sửa. ICF G2 TL4/TL5 viết lại (y khoa #138).
- **Cổng G10** (y khoa #137): cặp `DE_CUONG_NOP_HOI_DONG_<mã>` vào manifest khi có (thiếu nửa ⇒ chặn); quét [CẦN…]/PII
  liên lạc (bỏ DOI/URL trước khi dò số điện thoại); A12 phủ PMID của bản nộp.
- **Cấu trúc agent/điều phối** (y khoa #137 + gốc #181): nhiệm vụ **G10-T4** trong `hoi_dong_cong.NHIEM_VU` — chủ
  `viet-ban-thao`, chấm chéo `tham-dinh-dau-ra` + `kiem-chung-trich-dan`, có điều kiện (gói trình Hội đồng/cập nhật đăng ký);
  kiểm máy cấp nhiệm vụ `tools/kiem_de_cuong_nop_hoi_dong.py` (K1 cặp tệp · K2 Word khớp .md · K3 đủ chương · K4 không ký
  hiệu nội bộ/tên biến trong văn xuôi · K5 cỡ mẫu khớp G3 · K6 PMID trong A12 · K7 PII); `viet-ban-thao` có mục quy tắc soạn;
  khối trách nhiệm của 4 agent sinh lại bằng `sinh_tai_lieu_trach_nhiem.py`.
- **Khuôn ICF G2:** câu lịch hẹn chỉ khi có tiếp xúc nhiều lần (RCT/thuần tập/chẩn đoán); rủi ro cắt ngang viết lại; quyền
  xem/sửa/xóa kèm điều kiện «dữ liệu còn liên kết được».
- **Xuất Word** (gốc #179, đã gộp): `md_sang_docx_times.py --trang-de-cuong` (A4, lề 3-2-2-2, căn đều, ngắt trang, số trang).

## Kiểm hồi quy

Test mới: `test_g10_de_cuong_nop_hoi_dong_20261015.py` 7/7 · `test_kiem_de_cuong_nop_hoi_dong_20261015.py` 12/12 ·
`test_g2_icf_dung_boi_canh_20261015.py` 3/3. Kiểm đột biến: G10 5/5, công cụ kiểm 7/7 (một phép thử K7 ban đầu «lọt» vì chỉ
tắt nhánh .md trong khi nhánh .docx vẫn bắt — lỗi phép thử, làm lại tắt cả hai nhánh thì bắt), khuôn ICF 2/2. Chuẩn hoàn
thiện agent 64/64 · điều phối 13/13; khối trách nhiệm 59/59 khớp.

## Còn treo (việc của PI)

Chỉ tiêu 85%/90% gán cho QĐ 56 chưa đối chiếu văn bản gốc; tên chính thức của Hội đồng; SAP G4 còn ghi N tối thiểu 626 và DE
1,38 (đề cương: 808 và 1,78); `study_meta.data_governance` còn «chỉ nhận mã + số phút chờ». Chi tiết:
`exports/<mã>/GHI_CHU_DE_CUONG_NOP_HOI_DONG_<mã>.md` §4 (repo y khoa).
