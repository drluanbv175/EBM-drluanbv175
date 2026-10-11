# 09/10/2026 — G3: bảng độ nhạy p × d bỏ qua hiệu ứng thiết kế cụm; G3-AUTO-12 lẫn số chùm tối thiểu với số chùm cố định

**Phát hiện:** 07/10/2026, khi bác sĩ chạy `run_g3_auto.py` trên đề tài thật C1a (cắt ngang, p 0,5, d 5%, ICC 0,02, m = 20,
bỏ cuộc 15%, `confirmed_n` 1000). Số đo trên mã y khoa `16e4a98`. Vá ở repo y khoa, nhánh
`claude/g3-do-nhay-cum-20261009`, PR `drluanbv175/medical-ebm-automation#104` (hai commit độc lập: lỗi 1, lỗi 2); PR do bác sĩ
gộp. Chưa chạy lại G3 trên C1a thật — sau khi gộp, bác sĩ tự chạy lại
`run_g3_auto.py --study hai-long-benh-nhan-C1a-BVQY175`.

## Lỗi 1 — bộ sinh (`tools/run_g3_auto.py`, `generate_artifact()`)

- **Triệu chứng:** ô cơ sở bảng p × d in **385**, N chính là **532** (385 × DE 1,38; 626 sau bù 15%); G3-AUTO-09 REVIEW
  «ô cơ sở bảng độ nhạy=385 không khớp n_total=532 hay n_adjusted=626». Tiêu đề bảng không nói đã nhân DE.
- **Nguyên nhân:** nhánh p × d gọi `ap_fpc_cum(n_prevalence(p, d), design_code, population_n)` mà không truyền `icc`,
  `cluster_size` nên chỉ nhân FPC. Docstring `sensitivity_table()` ghi «SAU FPC/cụm như N chính» nhưng nhánh này tự tính riêng.
- **Vì sao lọt:** ma trận test G3-06 (04/10) có cắt ngang + FPC và RCT + cụm, KHÔNG có cắt ngang + cụm. Đo bằng đột biến: với
  đúng bản lỗi cũ, **186/186 test G3 sẵn có vẫn xanh** — không chốt nào giữ lỗi này.
- **Vá:** mỗi ô đi qua `ap_fpc_cum` với đủ `population_n, icc, cluster_size` (DE lấy từ chính hàm đó); tiêu đề nêu «đã nhân
  hiệu ứng thiết kế cụm DE = … (m, ICC)» khi có cụm, không khai khi thiếu `icc` hoặc `cluster_size`.

## Lỗi 2 — bộ chấm (`tools/g3_quality_gate.py`, G3-AUTO-12)

- **Triệu chứng:** C1a có số chùm CỐ ĐỊNH (50 bàn khám thật), N kế hoạch 1000 (m = 20), N tối thiểu 532 ⇒ cần ≥ 27 chùm. Khai
  `n_clusters` = 50 bị báo «số chùm khai tay=50 khác số chùm suy từ N=27»; không khai thì phép thử mẫu nhỏ (< 40 chùm) chạy trên 27.
- **Nguyên nhân:** `checkpoint["n_clusters"]` = ⌈n_total/m⌉ là số chùm TỐI THIỂU cần cho N tối thiểu, bộ chấm coi là số chùm
  CỦA ĐỀ TÀI.
- **Hai phương án đã cân:** (a) suy số chùm từ N kế hoạch khi `confirmed_n` > `n_total`; (b) cho khai số chùm cố định rồi đối
  chiếu. **Chọn (b), bác (a):** N kế hoạch tăng có thể do chùm TO hơn chứ không do thêm chùm (DE tăng theo m), nên (a) có thể
  nới phép thử mẫu nhỏ sai chiều ngay cả khi bác sĩ không hề khai số chùm.
- **Luật mới (không thêm khoá, tái dùng `n_clusters`):** số chùm khai tay nhiều hơn mức tối thiểu (quá ±1) chỉ được tin để nới
  phép thử mẫu nhỏ khi khớp `confirmed_n` ÷ m (±1); khai ít hơn mức tối thiểu ⇒ báo «N tối thiểu không đạt được» và phép thử
  chạy trên số ÍT hơn (bản cũ im lặng); không đối chiếu được ⇒ báo lệch và giữ mức tối thiểu. Không ca PASS nào bị lật; chỉ có
  REVIEW → PASS ở ca số chùm cố định đã đối chiếu.
- **Giữ nguyên:** giá trị và nghĩa khoá checkpoint `n_clusters` — SAP G4 §12 in đúng khoá này và cổng G4 đối chiếu nó.

## Kiểm hồi quy

- `tests/test_g3_bang_do_nhay_cum_20261009.py` (6 test: lưới 9 ô theo giá trị tính độc lập, tiêu đề, đối chứng không cụm / chỉ có
  ICC, FPC + cụm, đầu–cuối C1a) · `tests/test_g3_quality_gate.py` (+7 test số chùm cố định).
- Đột biến (§0.8): 8 phép cho lỗi 1 và 13 lượt cho lỗi 2 (gồm «nới không đối chiếu», «suy theo N kế hoạch», «nới ngưỡng 40»,
  «bỏ kiểm cận dưới», «nới dung sai», «đứt đường nối `confirmed_n`») đều làm test ĐỎ; sao lưu + `cmp` trước và sau mỗi phép.
- Toàn bộ `pytest` repo y khoa (đo 10/10/2026 trên nhánh đã rebase lên `1135f81`): 8409 passed, 44 skipped, 0 fail, 13 phút 14 giây;
  `exports/` trước/sau không đổi (70 tệp).

## Bài học

- Phép tính THỨ HAI của cùng một đại lượng (ô cơ sở bảng độ nhạy) phải đi qua CÙNG đường tính với đại lượng chính; mỗi tham số
  cắt ngang (FPC, cụm, bỏ cuộc) cần ca test cho tổ hợp với từng thiết kế, không chỉ từng tham số riêng lẻ.
- Một khoá checkpoint tên là «số chùm» có thể mang nghĩa «mức tối thiểu cần», không phải «của đề tài» — cổng đọc khoá phải biết nghĩa.

## Việc còn treo (cố ý không làm ở PR này)

- PHẦN 2b của A4 in sai số biên «≈ ±3,1 điểm %» cho `confirmed_n` = 1000 mà bỏ qua DE; có DE 1,38 là ±3,64 (±3,95 nếu 15% không trả
  lời). Kết luận «ĐẠT» không đổi, chỉ con số in ra lạc quan (đo 10/10/2026 bằng tính tay độc lập).
- A4 «(~27 cụm)» và SAP §12 «Số cụm: 27» là SỐ TỐI THIỂU, dễ bị đọc là số bàn khám (50); đổi nhãn phải sửa đồng bộ regex
  `**Số cụm:**` của cổng G4.
- C1a còn REVIEW thật ở G3-AUTO-12: «cỡ chùm không khẳng định là đều nhưng thiếu hệ số biến thiên CV» — quyết định của bác sĩ
  (khai `equal_cluster_sizes` hoặc `cluster_size_cv`); máy không điền.
