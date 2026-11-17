# 17/11/2026 — G6 không sinh Bảng 1 cho định tính · dự báo · tổng quan–gộp · cắt ngang mô tả; G7 không đọc kết quả đặc thù

## Bối cảnh
Việc tách ra từ `2026-11-17-hon-hop-va-van-ban-khong-dau-vet.md`. Bộ giả lập trước đây điền nhãn
«(GIẢ LẬP — hồ sơ chưa có)» vào ô trống. Khi bỏ nhãn đó, ba thiết kế định tính · dự báo · tổng quan–gộp dừng ở G7
(G7-AUTO-05). Bác sĩ giao làm ngay trong phiên: «Sinh Bảng 1 ở G6 cho định tính, dự báo, tổng quan gộp».

## Đo được — ba nguyên nhân chồng nhau
1. Tóm tắt G6 của `phan_tich_thiet_ke_dac_thu.py` không có `data_lock.sha256` và `generated`. Vì vậy
   `run_g7_auto.doc_tom_tat_g6_hop_le` fail-closed: «không chứng minh được sinh từ bản khoá». Cả phần Kết quả của bản
   thảo (luồng chọn mẫu, Bảng 1, ước lượng, nhạy cảm) là khung trống. Lỗi này áp cho cả chẩn đoán.
2. Không có `table1` ở đường đặc thù. `run_stats_analysis` cũng chỉ dựng Bảng 1 khi có biến chia nhóm, nên cắt ngang
   ước lượng tỷ lệ không có Bảng 1 (34 ô trống ở bản thảo).
3. G7 không đọc `dac_thu` (chủ đề, OR/C-statistic, RR gộp, AUC). Khối ước lượng luôn là ô «tóm tắt G6 chỉ ghi N».

## Đã sửa (repo y khoa, PR #292)
- **Nguồn gốc:** tóm tắt đặc thù ghi `generated` và `data_lock` giống `run_stats_analysis`.
- **Bảng 1:** `bang1_dac_thu` chia theo đúng bảng đặc điểm mẫu của chuẩn báo cáo:
  - dự báo theo có/không kết cục (TRIPOD+AI 23a);
  - chẩn đoán theo chuẩn tham chiếu (STARD 20);
  - định tính mô tả người tham gia (COREQ 16);
  - tổng quan–gộp mô tả đặc điểm nghiên cứu (PRISMA 17);
  - mã nhiều mức đổi sang nhãn từ điển G5 (NYHA I–IV, tên thuốc);
  - ghi cả `G6_table1_descriptive.txt`.
- **Cắt ngang mô tả:** thiết kế không có nhóm so sánh nhận Bảng 1 một nhóm «Toàn bộ».
- **Bộ lọc biến dùng chung:** `run_stats_analysis.bien_bang1_mo_ta` bỏ định danh, ngày, văn bản tự do và kết cục.
- **G7:** `_khoi_dac_thu_g6` chép từng loại kết quả: bảng chủ đề + KTC Wilson; OR + C-statistic + Brier; RR gộp ngẫu
  nhiên/cố định + Q/I²/τ² + từng nghiên cứu; AUC/Se/Sp/PPV/NPV/LR. Mọi số qua bộ tự kiểm nguyên văn.
  «Cỡ mẫu kế hoạch» dùng N đã chốt G3 khi thiết kế không tính theo lực (từng in N = 0).

## Kiểm
- `tests/test_bang1_dac_thu_20261117.py` 13 phép; đột biến 9/9 đỏ đúng chỗ.
- Lượt sạch 16 kịch bản từ G0: 16/16 `PASS_G10_RELEASE_PACKAGE_LOCKED`, 0 ô lỗi máy, 16/16 đề cương nộp mã 0.
- Ô «chưa có thông tin» ở bản thảo G7 còn 9–13 mỗi đề tài: số sàng lọc, lý do loại trừ, phân tích nhạy cảm chưa tự
  động. Đây là việc của người thật, bộ giả lập không bịa.
- Không còn «GIẢ LẬP»/«bản nháp»; câu «dữ liệu mô phỏng» bị ngắt dòng trong lời văn kịch bản cũng đã gỡ.

## Bài học
Lời điền của bộ giả lập phải là thứ hợp đồng ô trống (`placeholder_contract`) NHẬN RA là chưa điền. Một nhãn mà bộ dò
không biết sẽ biến ô trống thành «có nội dung», và cổng đạt giả trên đúng thiết kế đang thiếu chức năng.
