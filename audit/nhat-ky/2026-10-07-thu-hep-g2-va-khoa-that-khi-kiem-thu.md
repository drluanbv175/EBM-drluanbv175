# 07/10/2026 — Thu hẹp nhánh tương thích G2 kiểu cũ · khoá ký THẬT và kho secrets khi chạy kiểm thử

Bác sĩ giao: «Giải quyết 2 vấn đề: thu hẹp nhánh tương thích G2 kiểu cũ và 2 việc của đợt khoá giả pytest».

## 1. Nhánh tương thích G2 kiểu cũ

**Trước:** `gate_contract.g2_quality_contract_satisfied` nhận G2 chỉ dựa vào checkpoint G2 (tệp KHÔNG ký) khi gói
`G2_A3_ETHICS_PACKAGE` không có attestation:
- checkpoint thiếu `quality_contract_version` ⇒ True vô điều kiện;
- checkpoint có version ⇒ tin `PASS_G2_APPROVED` + hạn + phiên bản ghi trong chính checkpoint.

Ai xoá trường phiên bản (hoặc bóc attestation khỏi gói trước khi ký) là quay lại được nhánh dễ dãi này. Mọi cổng sau
(G5 khoá dữ liệu, G6 phân tích, G7/G9/G10) đều nhận G2 kiểu đó.

**Đo (chỉ đọc, `exports/` thật trên Mac):**
- C1a chưa có phê duyệt G2, checkpoint đã mang `G2-2026.1` ⇒ không bị ảnh hưởng.
- Chỉ một thư mục kiểm toán sót lại (`ZZPH-G6-AUDIT`, tiền tố ZZ, không đánh dấu đề tài thử) có G2 ký sau mốc mà
  checkpoint không version — đúng dạng lỗ hổng cần đóng.
- Từ hợp đồng G2-2026.1, `g2_quality_gate` chỉ cho `PASS_G2_APPROVED` khi gói CÓ attestation (không attestation ⇒ tối
  đa `READY_FOR_IRB_SUBMISSION`). Vậy một G2 ký sau mốc mà gói không có attestation không bao giờ là phê duyệt hợp lệ.

**Vá (y khoa):**
- Mốc `G2_MOC_HOP_DONG_PHIEN_BAN` = commit `64b278f` đưa G2-2026.1 + attestation vào nhánh làm việc
  (2026-07-28 17:47:50 +07:00).
- `g2_ky_truoc_moc_hop_dong(study, out_dir)`: mốc KÝ lấy từ bản ghi G2 có thẩm quyền, chọn và xác minh bằng CÙNG hàm
  với `ledger_approved` (chữ ký đúng vai, niêm phong, thu hồi). `timestamp_utc` nằm trong nội dung ký ⇒ lùi ngày bằng
  tay làm hỏng chữ ký.
- Gói không attestation chỉ còn được xét theo checkpoint khi phê duyệt KÝ TRƯỚC mốc. Ký sau mốc, không có sổ cái hợp
  lệ, hoặc không truyền study/out_dir ⇒ False.
- Đồ gá test: `g5_test_helpers.ky_g2_hien_dai` dựng G2 bằng CHÍNH `approve_gate._prepare_g2_attestation` (hàm lệnh ký
  thật dùng), hợp lệ theo thiết kế (RCT/SR-MA bắt đăng ký), thay G2 kiểu cũ trong `prepare_upstream_approvals`.

## 2. Hai việc của đợt khoá giả pytest (05/10)

**(a) Khoá ký THẬT khi kiểm thử.** Dưới pytest, thiếu `EBM_GATE_KEY_PATH` làm `_base_key_path()`/`_ed_private_dir()`
LẶNG LẼ rơi về `~/.ebm-secrets` — khoá riêng của bác sĩ. Móc audit của conftest chỉ thấy tiến trình pytest, không
thấy tiến trình con kế thừa `PYTEST_CURRENT_TEST` mà mất biến khoá.
- Vá: `_chan_khoa_that_khi_kiem_thu` — đang kiểm thử mà đường dẫn khoá nằm trong thư mục bí mật thật (chốt lúc import)
  ⇒ ném `KhoaThatKhiKiemThuError` TRƯỚC khi mở tệp. Rào lỗi mật mã (`_fail_closed_on_crypto_error`, bắt
  `BaseException`) ném lại lỗi này thay vì nuốt.
- Giả lập «vận hành thật» bằng cách vá `_test_context_active()` thì chốt nhường (test chỉ so đường dẫn).

**(b) Kho secrets khi kiểm thử.** `app/config.py` nạp `~/.ebm-secrets/medical-ebm-automation.env` lúc import ở mọi
tiến trình (~36 lần/lượt pytest), nên chốt canh phải khai miễn trừ ĐỌC cho tệp đó.
- Vá: `app.config.dang_chay_kiem_thu()` (cùng tín hiệu với gate_contract). Đang kiểm thử ⇒ không nạp tệp môi trường
  nào — cả kho lẫn `.env` của repo (từng là symlink vào kho; chốt canh không theo symlink).
- Phần nạp tách thành `_nap_tep_moi_truong(dang_kiem_thu, nap=…)` để test kiểm thứ tự nạp của lần chạy THẬT bằng bộ nạp
  giả, không mở tệp thật nào.
- Hai công cụ tự đọc kho (`gom_toan_van_oa._email_lien_he`, `tai_retraction_watch._email`) cũng không đọc khi kiểm thử.
- Mã vận hành không import pytest (đo) ⇒ tín hiệu này không làm một lần chạy THẬT bỏ kho rồi rơi về dữ liệu MOCK.
- `tests/conftest.py` BỎ miễn trừ: chạm tệp đó (cả ĐỌC) nay là vi phạm như mọi tệp khác trong kho.

**Giới hạn còn lại (nói thẳng):** tiến trình con dựng `env=` từ đầu, bỏ cả `EBM_GATE_KEY_PATH` lẫn
`PYTEST_CURRENT_TEST`, thì không còn tín hiệu nào cho biết đang kiểm thử — nó chạy như lần vận hành thật.

## Kiểm

- Y khoa: `tests/test_thu_hep_g2_va_khoa_that_20261007.py` có 21 test. Lùi ngày ký bằng tay làm hỏng chữ ký ⇒ chặn;
  đồ gá G2 hiện đại đạt hợp đồng nhờ attestation cho cả RCT, SR/MA, cohort, định tính.
- Đột biến 19/19 bị bắt. Lượt đột biến chạy trong HOME GIẢ (chỉ symlink venv), nên không đột biến nào chạm được kho
  bí mật thật.
- Toàn bộ bộ test y khoa: 8269 qua · 44 bỏ qua · 0 đỏ; `exports/` trước/sau khớp.
- Lượt đầu có 6 test đỏ, đều do đồ gá còn dựa G2 kiểu cũ — đã sửa đồ gá, không nới assertion:
  - 3 chuỗi RCT G8/G9/G10: G8-AUTO-07 phát hiện đăng ký khai ở G8 (`NCT01234567`) lệch attestation G2 của đồ gá mới;
    sửa bằng hằng dùng chung `DANG_KY_THU_RCT` — đúng loại nhất quán xuyên cổng mà G2 kiểu cũ (không attestation)
    từng che;
  - 2 test G2 gọi hợp đồng không kèm đề tài;
  - 1 test run_stats dựa nhánh kiểu cũ (checkpoint mất + cờ IRB).
- Gốc: 2 agent dạy luật mới (`dao-duc-dang-ky`, `dieu-phoi-g2`), khớp từng byte với repo y khoa; guardrail 64/64;
  căn chỉnh repo PASS.

Cần bác sĩ kiểm chứng.
