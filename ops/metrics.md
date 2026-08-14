# ĐO LƯỜNG — định nghĩa vận hành của «mới nhất» & «tin cậy nhất» (K4 đã đóng phần lõi)

| Chỉ số (mục 7 prompt) | Ngưỡng | Đo ở đâu | Trạng thái |
|---|---|---|---|
| Độ trễ phát hiện | ≤14ng (guideline) / ≤7ng (an toàn thuốc) | khối `do_tre` TRONG MỖI báo cáo quét (trung vị + số mục quá 14ng) | ✅ đo lần đầu 15/08: trung vị 3ng, 0 mục quá ngưỡng |
| Nguồn phân giải được | 100% | E2 + sổ xác minh `--bao-cao` | ✅ 99% sổ (1153/1155; phần còn lại là URL thuần) |
| Trích dẫn ảo | 0 | cổng + `kiem-chung-trich-dan`; canary ca PMID giả | ✅ cơ chế; kiểm ngẫu nhiên 10%/tháng `[CẦN BỔ SUNG]` |
| Sai lệch hiệu số vs nguồn | 0 nghiêm trọng | `kiem_so_lieu.py` (mẫu 25 mục: 24 khớp đủ, 1 một-phần) | ✅ công cụ; nhịp tháng `[CẦN BỔ SUNG]` |
| Item bị bác sĩ loại ở E6 | theo dõi ↓ | ledger EBM_MASTER | `[CẦN BỔ SUNG]` bộ đếm |
| Guideline đã bị thay thế còn dùng | 0 | quét QUÝ `quarterly_superseded.sh` (mới) | ✅ nhịp đã gắn |
| Retraction chưa gỡ | 0 | quét THÁNG sổ xác minh (hạn 30ng) + alerts | ✅ |

Mẫu báo cáo tháng: gộp `--bao-cao` sổ + `do_tre` gần nhất + alerts trong tháng + đếm hàng
chờ E6. Thiếu số → ghi `[CẦN BỔ SUNG]`, không ước lượng.

## Số đo NGHIỆM THU PHA 2 (15/08/2026 — đo thật, không ước lượng)
| Chỉ số | Giá trị | Nguồn |
|---|---|---|
| Diễn tập phục hồi ledger | ĐẠT (hash khớp từng byte, 1193 thẻ) | runbook §Sao lưu |
| Sức khoẻ sổ | 0 CHẶN · 288 BÁO CÁO /1193 | `reports/ledger-health.md` |
| Di trú hợp đồng mới (dry-run) | 1157/1193 đạt · 0 mint APPROVED | chờ bác sĩ duyệt diff |
| Truy nguyên toàn sổ | 951 ok-30d · 241 KHÔNG BIẾT · 1 dương tính (notyet) | `reports/provenance-2026-08-15.md` |
| Gold set tự động | 12/12 đạt (~26 hành vi) · 5 nhóm khai CẦN MẠNG/CHƯA TỰ ĐỘNG | `reports/eval-2026-08-15.md` |
| E2E CKD --online | 5/5 bước rc=0, ~135s, trễ trung vị 2 ngày | `logs/20260815T064642-*.jsonl` |
| Chốt hồi quy | 48/48 xanh (BH48 mới, mutation-tested) | `chot_hoi_quy_bai_hoc.py` |
