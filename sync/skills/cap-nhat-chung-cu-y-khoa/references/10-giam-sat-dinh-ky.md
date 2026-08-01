# 10 - Giám sát định kỳ (Track B)

Track B chỉ tạo **ứng viên** để Track A thẩm định; không tự đổi thực hành, không tự
gắn `apply`, không dùng dữ liệu bệnh nhân thật.

## Quyền sở hữu

- Engine `weekly_safety.sh`/`monthly_update.sh`: owner thu thập, source health, watermark.
- `giam-sat-chung-cu`: owner thẩm định candidate.
- `tong-hop-chung-cu-hang-tuan`: worker tóm tắt queue, không quét lại.
- `uptodate`: owner closed-loop/Hub sau khi đủ cổng.
- `antifacts-weekly-ebm`: trình bày, không sở hữu quyết định.

## Bộ quét

`tools/surveillance_scan.py` đọc `EBM-Dashboards/watchlist.json`, truy vấn PubMed và
ghi Markdown + audit JSON. Bộ quét có retry/backoff, User-Agent, kiểm schema, dedup
PMID và ghi lỗi từng chủ đề. `PARTIAL/FAIL` trả mã khác 0; chủ đề lỗi không được ghi
"không có cập nhật".

```bash
cd EBM-Dashboards
python3 tools/surveillance_scan.py --days 30 \
  --report surveillance_<ngày>.md \
  --json-report surveillance_<ngày>.json
```

## Cổng triển khai

```bash
cd medical-ebm-automation
python tools/verify_evidence_surveillance_deployment.py --online
```

Chỉ `READY_FOR_CONTROLLED_DEPLOYMENT` mới cho phép chạy candidate-only. Điều kiện:

1. Canary PubMed, Europe PMC, Crossref, openFDA và dashboard strict-source online PASS.
2. LaunchAgent đúng path và các runtime status tuần/tháng PASS, còn mới.
3. Alert đã gửi/nhận thử; restore backup đã drill và hash khớp.
4. Ít nhất hai chu kỳ shadow không lỗi, không auto-apply.
5. Bác sĩ đã mở/đối chiếu tối thiểu năm nguồn; bác sĩ và vận hành cùng phê duyệt.

Canary không ghi DB/Hub:

```bash
bash scripts/weekly_safety.sh --canary
bash scripts/monthly_update.sh --canary
```

Agent không tự điền PASS, không tự ký UAT. `PARTIAL/FAIL` phải giữ watermark, chặn
`bridge_to_ebm_master.py`, không gửi cảnh báo nội dung và ghi runtime status FAIL.

**Cần bác sĩ kiểm chứng.**
