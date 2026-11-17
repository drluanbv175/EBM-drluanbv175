# 17/11/2026 — Sinh lại G2 và dựng đề cương nộp cho BTM thật: guardrail đỏ giả khi xin miễn phiếu đồng ý, 8 lỗi bộ sinh đề cương

## Bối cảnh
Bác sĩ chọn hai việc cho đề tài `btm-dtd2-ngoai-tru-BVQY175`:
1. «Sinh lại, đưa qua PR» hồ sơ đạo đức G2.
2. «Bác sĩ chạy A12 trước» rồi mới dựng bản nháp đề cương nộp Hội đồng.

Bác sĩ tự chạy `check_citations.py --study`: 42/42 PMID sạch rút bài và phân giải được metadata. Mọi việc làm trong
worktree tách từ `feat` và đi qua PR dữ liệu drluanbv175/medical-ebm-automation#294; không ghi thẳng `exports/` của cây
OneDrive. Cây OneDrive lúc đó chậm `feat` 49 commit và chưa có tệp G2 nào.

## Đo được — lỗi chỉ lộ trên dữ liệu thật
16 kịch bản giả lập (16/16 G10 PASS, 377/377 trục khớp) không chạm tới các dạng sau:
1. **Guardrail G2 R6/R6b đỏ giả với MỌI đề tài xin miễn phiếu đồng ý.** Từ 15/11, `thu_gon_icf_khi_xin_mien` thay TÀI LIỆU
   4/5 bằng ghi chú «không áp dụng», nhưng R6/R6b vẫn đòi đủ 7 mục và 4 mục con của phiếu. Ở giả lập, guardrail không
   phải điều kiện đạt cổng nên không lộ. Lần sửa đầu so chuỗi nguyên văn nên vẫn lọt: bước làm sạch đổi «— chủ nhiệm»
   thành «. Chủ nhiệm». Lỗi chỉ thấy khi đo trên chính hồ sơ BTM.
2. **Bộ sinh đề cương** (K1–K8 vẫn ĐẠT):
   - trích dẫn liền trong trường G1 bị in thô: «KDIGO 2024 (PMID 38490803)», «PMID n, DOI …»; có 22 chỗ in trường G1 tự do;
   - biến tính toán bị bộ tách lựa chọn cắt sai: «round([can_nang] / … = 1)». Lỗi này có cả FIB-4 trong gói giả lập;
   - cụm dẫn tệp nội bộ lộ trong văn xuôi: «Theo G0_KHOANG_TRONG (25/10/2026):», «Theo:», «(biến XN_DU)», «G8–G9 –»,
     «(, từ …)», «N/A»;
   - nhãn biến phái sinh không được nạp ⇒ «người có khác 9»; nhãn bị hạ chữ thường cả từ viết tắt ⇒ «acei/arb theo kdigo
     2022», «uacr», «mt3»;
   - Bảng 3.1:
     - ghi «Tác giả và cộng sự» cho ADA/KDIGO;
     - ADA Standards xếp «Tổng quan hệ thống» (PubMed gắn Review);
     - nghiên cứu quan sát xếp «Hướng dẫn» chỉ vì có chữ «guidelines» trong tên bài;
     - ba chương ADA chiếm hết suất hướng dẫn, đẩy KDIGO 2024 ra ngoài;
   - đề tài cắt ngang có mục tiêu phân tích vẫn ghi «cắt ngang mô tả» (trục TK-01 bắt);
   - mục 4.8 để trống dù G1 có sổ 11 nguồn sai lệch PI đã chốt (`gate_params.G1.bias_controls`).
3. Lượt giả lập chạy cùng lúc với lúc bác sĩ chạy A12: bước A12 của bộ giả lập gọi NCBI thất bại sau 4 lần ⇒ 3/16 G10
   BLOCKED (R4 «nghi bịa» vì PMID chưa vào biên nhận). Chạy lại thì 3/3 PASS. Đây là lỗi mạng, không phải lỗi mã.

## Đã sửa (repo y khoa, PR nối tiếp #293)
- `run_g2_auto.guardrail_check_g2`: có ghi chú xin miễn (so bằng mẫu, chịu bước làm sạch) VÀ có đơn xin miễn TÀI LIỆU 9 ⇒
  R6/R6b không áp dụng. Bỏ phiếu mà không có đơn ⇒ R6 đỏ.
- `sinh_de_cuong_nop_hoi_dong`:
  - `_TruongTrichDan` (trường G1 đổi trích dẫn khi đọc, theo thứ tự xuất hiện); `TrichDan.thay` nuốt DOI đi kèm, dọn dấu câu;
  - `cong_thuc_doc`; gỡ cụm dẫn tệp nội bộ; `nap_nhan_bien_phai_sinh`; `_nhan_giua_cau`;
  - `_HUONG_DAN_MANH`; `_tac_gia_to_chuc` (mỗi tổ chức một dòng);
  - `ten_thiet_ke`; `bang_sai_lech`.
- Phép thử: `tests/test_truc_xuyen_cong_sau_gia_lap_20261117.py`. Kiểm đột biến từng luật đỏ đúng chỗ, gồm hai đột biến
  sống sót lần đầu đã bổ sung ca: PMID trần trước dấu phẩy; bỏ lời gọi nạp nhãn trong `Nguon`.

## Kết quả trên BTM (đo, chưa ai ký)
- G2: ô chưa điền 102 → 48; phiếu đồng ý thành ghi chú xin miễn; guardrail đạt; trạng thái vẫn
  `DRAFT_NEEDS_HUMAN_COMPLETION`.
- Đề cương nộp:
  - 584 dòng, 42 tài liệu tham khảo Vancouver, không PMID thô trong thân;
  - K1–K8 ĐẠT; còn 65 dòng chấm cho chủ nhiệm điền;
  - trục xuyên cổng 23 khớp / 2 cần xem / 1 lệch mềm. Cả ba là việc của người: kết cục đã xác nhận, neo hạn chế trong sổ
    sai lệch, duyệt đặc tả phân tích.

## Bài học
K1–K8 kiểm cấu trúc và dấu vết đã biết. Văn bản thật vẫn có thể đọc như máy viết ở những chỗ bộ kiểm chưa có mẫu. Sau mỗi
bản đề cương dựng từ dữ liệu thật phải đọc lại như người phản biện. Lỗi nào lặp lại thì sửa ở bộ sinh, kèm phép thử, không
vá tay bản máy. Dữ liệu giả lập không thay được dữ liệu thật: trích dẫn liền, biến phái sinh, tác giả tổ chức, sổ sai lệch
có cấu trúc chỉ xuất hiện ở đề tài thật.
