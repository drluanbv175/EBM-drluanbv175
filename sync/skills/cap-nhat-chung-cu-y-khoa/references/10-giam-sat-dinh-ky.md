# 10 — Giám sát định kỳ (Track B)

Bổ sung cho cập nhật theo-yêu-cầu (Track A): một vòng giám sát HẸP để **bắt thay đổi mình không nghĩ sẽ tra** (guideline mới, RCT/meta lớn, an toàn thuốc) trên các chủ đề lõi.

> Track A (pull) vẫn là trục chính. Track B (push) chỉ surface ỨNG VIÊN — không tự đổi thực hành.

## Thành phần
- **Danh sách theo dõi:** `EBM-Dashboards/watchlist.json` — 10–20 chủ đề bác sĩ gặp nhiều nhất (giữ HẸP để tránh nhiễu). Bác sĩ tự sửa.
- **Bộ quét:** `tools/surveillance_scan.py` — với mỗi chủ đề, truy vấn PubMed tìm guideline/SR/meta/RCT MỚI trong N ngày → báo cáo ứng viên (PMID · ngày · tiêu đề).

## Quy trình (định kỳ, vd hằng tuần/tháng)
```bash
cd EBM-Dashboards
python3 tools/surveillance_scan.py --days 30 --report surveillance_<ngày>.md
```
1. Đọc báo cáo, **chọn mục thật sự liên quan**.
2. Với mục đáng giá → chạy skill cập nhật chứng cứ (Track A) để **thẩm định đầy đủ** + dựng dashboard + cổng liêm chính + thư viện.
3. (Tùy chọn) Ghi thay đổi vào Dashboard Master (skill `dashboard-master-ebm-ngoai-tru`).

## Tự động hóa (tùy chọn — bác sĩ xác nhận nhịp)
Dùng skill `schedule` để chạy bộ quét định kỳ (vd mỗi sáng thứ Hai) và gửi báo cáo. **An toàn thuốc** đã có routine riêng `Scheduled/drug-safety-daily`. Không bật lịch tự động khi chưa được bác sĩ đồng ý nhịp + chủ đề.

## Liêm chính
- Kết quả giám sát là **ỨNG VIÊN**, chưa thẩm định — không trích như khuyến cáo.
- Mọi thay đổi thực hành phải qua Track A (xác minh nguồn, PICO/khung, GRADE, cổng liêm chính).
- Giữ watchlist hẹp; rà lại định kỳ để bỏ chủ đề không còn theo.
