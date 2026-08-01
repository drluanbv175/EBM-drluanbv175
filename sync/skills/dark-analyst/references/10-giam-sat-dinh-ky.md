# 10 - Giám sát định kỳ (Track B)

Track B chỉ tạo **ứng viên** để Track A thẩm định; không tự đổi thực hành, không tự
gắn `apply`, không dùng dữ liệu bệnh nhân thật.

## Quyền sở hữu

- Engine `weekly_safety.sh`/`monthly_update.sh`: owner thu thập, source health, watermark.
- `giam-sat-chung-cu`: owner thẩm định candidate.
- `tong-hop-chung-cu-hang-tuan`: worker tóm tắt queue, không quét lại.
- `uptodate`: owner closed-loop/Hub sau khi đủ cổng.
- Dark Analyst/Antifacts: phân tích và trình bày, không sở hữu quyết định.

## Bộ quét và trạng thái

`tools/surveillance_scan.py` có retry/backoff, kiểm schema watchlist, dedup PMID và
audit JSON từng chủ đề. `PARTIAL/FAIL` trả mã khác 0; chủ đề lỗi không được diễn giải
là "không có cập nhật".

```bash
python3 tools/surveillance_scan.py --days 30 \
  --report surveillance_<ngày>.md \
  --json-report surveillance_<ngày>.json
```

## Cổng triển khai

Chạy `medical-ebm-automation/tools/verify_evidence_surveillance_deployment.py --online`.
Chỉ `READY_FOR_CONTROLLED_DEPLOYMENT` mới cho phép candidate-only. Cần canary online,
runtime tuần/tháng còn mới, alert, rollback hash-match, hai chu kỳ shadow, năm mẫu nguồn
do bác sĩ đối chiếu và phê duyệt bác sĩ + vận hành. Agent không tự điền PASS/ký thay.

`PARTIAL/FAIL` giữ watermark, chặn Hub và không gửi cảnh báo nội dung.

**Cần bác sĩ kiểm chứng.**
