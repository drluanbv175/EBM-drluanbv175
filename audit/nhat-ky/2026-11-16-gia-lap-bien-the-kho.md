# 16/11/2026 — Giả lập 7 biến thể khó tới G10: 8 lỗi hệ thống (Poisson cụm, mã thiếu, A12 phủ gói, kinh tế y tế…)

## Bối cảnh
Tiếp `2026-11-16-gia-lap-8-thiet-ke-g6-5-g10.md` (8 thiết kế chuẩn đã đi hết G10). Bác sĩ giao: «Làm tiếp giả lập thêm
các biến thể khó, mỗi biến thể một kịch bản», rồi «giả lập tới khi xác nhận đã đạt trạng thái hoàn thiện, tự động tốt
nhất có thể cho mọi đề tài». Mỗi biến thể là một kịch bản riêng trong `tools/gia_lap_bien_the_kho.py` (repo y khoa),
chạy bằng `tests/test_gia_lap_tron_vong_20261115.py::test_gia_lap_bien_the_kho[<id>]` (cần GIA_LAP_TRON_VONG=1).

| Kịch bản | Điều hệ phải làm đúng |
|---|---|
| `rct_ni` — RCT không kém hơn | biên Δ có khung + biện minh + nguồn; kết luận theo cận KTC so với biên |
| `rct_cum` — RCT theo cụm | ICC có nguồn; ≥ 40 cụm; Poisson với sai số theo cụm |
| `cohort_cox` — thuần tập sống còn | ma trận biến đúng vai thời gian/biến cố; Cox; HR |
| `cohort_mi` — thuần tập dữ liệu thiếu | mã thiếu khai báo; gán đa trị m = 20 |
| `rct_rut_bai` — trích dẫn đã rút | A12 chặn PMID 18453793 (Morisky 2008, đã rút), tác giả thay nguồn |
| `cohort_vong_sua` — vòng sửa sau phản biện | «Sửa lớn» chặn ký G8; sửa bản thảo ⇒ G7 đòi PI xác nhận lại |
| `rct_kinh_te` — RCT + chi phí–hiệu quả | SAP §16 (CHEERS 2022); ICER, bootstrap, CEAC kiểm chéo R/SPSS |
| hỗn hợp định tính–định lượng | ĐO: `mixed_methods` ngoài 8 mã ⇒ G1-AUTO-02c chặn có chủ ý — chờ bác sĩ quyết |

## Lỗi hệ thống tìm được và đã vá (repo y khoa, nhánh `claude/gia-lap-bien-the-kho-20261116`)
1. **Engine G6 — Poisson vững không hỗ trợ cụm:** `poisson_pr_model` trả lỗi khi có `cot_cum` ⇒ RCT cụm không có PR
   nào. Nay sandwich theo cụm CR1 + t(G−1); khớp R `vcovCL(type = "HC1")` tới 4 chữ số (đo trên dữ liệu cố định);
   kiểm chéo R/SPSS (GENLIN GEE robust, ghi «khác phương pháp» ở KTC) nối theo.
2. **Bảng 5 MI với kết cục Poisson in «?»:** bộ in chỉ đọc `OR_adj`/`beta` ⇒ G6.5 không chép được PR sau MI.
3. **Làm sạch G5 truy vấn cả ô mang mã thiếu đã khai:** hướng dẫn nhập liệu dạy «câu bắt buộc mà nguồn không có thì
   ghi mã thiếu», nhưng bộ làm sạch mở `missing_required_value` cho chính các ô đó (1013 truy vấn ở kịch bản MI) ⇒ đề
   tài hồi cứu không khoá được G5. Nay ô mang mã đã khai là thiếu có ghi nhận (`required_missing_coded`); ô trống thật
   và token mặc định vẫn bị truy vấn.
4. **A12 không phủ tệp gói (lỗ «trích dẫn ma» + vỡ manifest G9):** G7/G8/G9 chỉ đối chiếu PMID do chính mô tả A12 liệt
   kê. Nay `run_g10_assemble.tep_phu_a12` liệt kê tệp mỗi cổng phải phủ (G7 bản thảo + diễn giải; G8 + bản nhận xét; G9
   + A9, SAP, tệp G9; G10 mục đích đầy đủ như G9). Trước đó PMID CONSORT cụm (22951546, bản nhận xét G8) và CHEERS 2022
   (35017145, SAP §16) chỉ lộ ở G10 ⇒ chạy lại A12 làm vỡ manifest G9 đã khoá. Đo hai đề tài thật (chỉ đọc): C1a mục
   đích ETHICS_SUBMISSION không bị ảnh hưởng; BTM chưa tới G7, SAP có 8 PMID sẽ phải qua A12 khi tới G9.
5. **G4 không có mục cho đánh giá kinh tế:** `gate_params.G1.economic_evaluation` ⇒ SAP §16 (CHEERS 2022), mục bắt buộc
   ở `approve_gate`/`g4_quality_gate`.
6. **G6 chưa có phân tích kinh tế:** `phan_tich_thiet_ke_dac_thu` thêm `kinh_te` (ICER + góc phần tư dùng
   `health_econ_calc.icer`, NMB, bootstrap phân tầng B = 2000, CEAC), nối `chay_sap_g6`, kịch bản R/SPSS.
7. **Khuôn 03_analysis.R:** Cox (thuần tập, RCT) và hiệu số tỷ lệ chưa đánh dấu `◆ MÔ HÌNH CHÍNH (SAP §4)` (Cox còn viết
   nhiều dòng — bật một dòng là cú pháp R hỏng).
8. **Khuôn hiệu số tỷ lệ tính NGƯỢC dấu:** `prop.test(bang[, "1"], rowSums(bang))` ra p0 − p1 (engine ghi p1 − p0) — với
   thử nghiệm không kém hơn, đảo dấu là đảo kết luận so với biên.

Hồ sơ biến thể sai do người viết kịch bản (không phải lỗi hệ, đã sửa hồ sơ): NI ghim `effect_type` «RR» thay
`NI_PROPORTION`, thiếu nguồn biên; cụm thiếu nguồn ICC, 17 cụm < 40; ma trận sống còn khai biến cố nhị phân làm kết cục
chính; MI chưa khai mã thiếu. Cổng G3 chặn đúng cả bốn.

## Hành vi hệ đã đúng sẵn (giả lập xác nhận)
- A12 chuỗi 3 tầng bắt bài đã rút ngay lần đầu (mã 1, `rut: ["18453793"]`); thay nguồn ⇒ sạch.
- `approve_gate` từ chối ký G8 khi phản biện «Sửa lớn» (G8-HUMAN-06); sửa bản thảo sau xác nhận ⇒ G7-HUMAN-04.

## Kiểm
- `tests/test_bien_the_kho_he_thong_20261116.py` (repo y khoa): Poisson cụm khớp số R; mã thiếu; §16; kinh tế; khuôn G6
  + chạy prop.test thật bằng R; Bảng 5 MI. Đột biến 8/8 đỏ đúng chỗ (một đột biến sống sót lần đầu — Cox — đã siết phép
  thử để đòi dòng `coxph(` thi hành).
- Kết quả trọn vòng từng biến thể và trọn bộ pytest: xem PR repo y khoa.

## Còn mở (cần bác sĩ)
- Hỗn hợp định tính–định lượng (và bán thực nghiệm, cải tiến chất lượng, ca lâm sàng, kinh tế dựa mô hình): ngoài chuỗi
  G0–G10 — quyết định kiến trúc (thêm mã thiết kế thứ 9, hay hai nhánh liên kết + tài liệu tích hợp).
- Bảng kiểm CHEERS 2022 28 mục chưa tự sinh.
