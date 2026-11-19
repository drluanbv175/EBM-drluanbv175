# 19/11/2026 — Câu văn báo cáo A12 bị tính là «đã kiểm rút bài»

**Bối cảnh.** Nhật ký `2026-11-19-rut-bai-g0-doc-cau-van.md` có ghi một điểm cùng họ lỗi mà lượt sửa trước chưa đụng. Bác sĩ giao sửa nốt ngày 19/11/2026: «báo cáo kiểm trích dẫn A12 cũng đang bị máy đọc như câu văn. Hãy giải quyết vấn đề giúp tôi».

**Lỗ.** `nhat_quan_xuyen_cong._da_kiem_rut_bai` đọc `A12_CITATION_VERIFICATION_<mã>.md` bằng `danh_muc_trich_dan.dinh_danh`. Mọi «PMID x» hay DOI có trong báo cáo đều được tính là «đã kiểm rút bài» vào ngày của biên nhận A12, kể cả:
- bảng đối chiếu NỘI DUNG, vốn không phải kết quả kiểm rút bài;
- câu «chưa kiểm được».

Báo cáo này do agent viết tay. Phần có máy đứng sau chỉ là biên nhận `A12_RETRACTION_RECEIPT.json`: có chữ ký nhưng chỉ có PMID.

**Đã soát:** các cổng G7, G8, G10 đọc báo cáo A12 qua `run_g10_assemble.citation_verification_ok`. Hàm này đòi mọi PMID nhắc trong báo cáo phải nằm trong biên nhận có chữ ký, nên không có lỗ. Bộ đối chiếu xuyên cổng là nơi DUY NHẤT suy «đã kiểm» từ câu văn A12.

**Cách vá** (repo y khoa, cùng PR với lượt sửa G0):
- Bỏ phần đọc báo cáo A12 trong `_da_kiem_rut_bai`. Nguồn «đã kiểm» nay chỉ còn bản ghi có cấu trúc:
  - biên nhận máy A12;
  - `KIEM_RUT_BAI_TRICH_DAN_<mã>.json`;
  - danh sách `rut_bai.pmid_da_kiem`/`doi_da_kiem` của G0;
  - `G0_checkpoint.pmids_verified`.
- Hướng dẫn agent `kiem-chung-trich-dan` thêm luật: DOI phải được kiểm qua `kiem_rut_bai_trich_dan.py --ghi`, không chỉ ghi vào báo cáo.

**Đo trên bản sao hồ sơ thật.**
- C1a: số định danh đã kiểm giảm từ 78 xuống 76. Hai DOI bị bỏ, cả hai chỉ có trong bảng DOI của báo cáo A12: `10.1093/jssam/smv024` và `10.3368/jhr.50.2.301`, là tài liệu phương pháp mà SAP §3/§4 dẫn. Hai DOI không nằm trong TLTK đề cương nộp nên không sinh cảnh báo mới. Nếu sau này chúng vào TLTK, trục sẽ báo «chưa có bản ghi kiểm rút bài» cho tới khi chạy `kiem_rut_bai_trich_dan.py --study hai-long-benh-nhan-C1a-BVQY175 --ghi`.
- BTM: không đổi.
- G10 của cả hai vẫn PASS.

**Kiểm.**
- Thêm test `test_cau_van_bao_cao_a12_khong_phai_ban_ghi_kiem_rut_bai`. Fixture `_sach` nay ghi DOI vào tệp kiểm theo từng mã, đúng như đề tài thật.
- Kiểm đột biến M10 (khôi phục đọc câu văn A12) đỏ đúng chỗ; cả bộ 10/10 đột biến bị bắt.
- 798 test liên quan tới báo cáo A12 và bộ đối chiếu xuyên cổng đều đạt.
