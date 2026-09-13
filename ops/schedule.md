# LỊCH CHẠY HỢP NHẤT (bác sĩ duyệt Q2+Q3, 15/08/2026)

## Cơ chế THẬT (đã đo, không phải kỳ vọng)
| Kênh | Trạng thái đo được | Vai trò sau hợp nhất |
|---|---|---|
| launchd weekly/monthly | `runs = 0` — chưa từng nổ (máy không thức đúng giờ) | GIỮ như dự phòng; kích hoạt thật qua tu_khoi_dong |
| Hook `SessionStart` (7 chốt) | chạy MỖI phiên: 47 bài học + canary 10 ca · dong_bo_skill · độ tươi · nguồn thật · kho plugin · tu_khoi_dong · tu_sua_chua | XƯƠNG SỐNG tự động |
| `tu_khoi_dong --phong` | phóng script chủ sở hữu khi QUÁ HẠN lúc mở phiên | bộ kích lịch không-cần-máy-thức |

## Nhịp đã duyệt (Q3)
| Việc | Nhịp | Chủ sở hữu (allowlist tu_khoi_dong) | Đầu ra |
|---|---|---|---|
| Giám sát an toàn thuốc | TUẦN (hạn 10ng) | `weekly_safety.sh` | log + watermark + Antifacts |
| Cập nhật guideline | THÁNG (hạn 35ng) | `monthly_update.sh` | log + watermark |
| Quét chứng cứ BỊ VƯỢT QUA toàn kho | **QUÝ (hạn 92ng) — MỚI** | `quarterly_superseded.sh` | `derivatives/CHUNG-CU-VUOT-QUA_*.txt` + alerts |
| Rút bài toàn sổ | THÁNG (hạn 30ng có sẵn trong sổ xác minh) | `so_xac_minh_nguon --quet` | sổ + alerts |
| Đo độ trễ | MỖI lượt quét (tự động trong báo cáo) | `surveillance_scan` | khối `do_tre` |

## 6 tác vụ claude.ai web — ĐÃ XOÁ HẾT (13/09/2026)
Bảng dưới đây là TRẠNG THÁI LỊCH SỬ (Q2, 15/08/2026) — giữ lại để biết vì sao từng có 6 tác
vụ này và tại sao bị xoá, KHÔNG phải mô tả hiện trạng.

| Tác vụ web (đã xoá) | Từng trùng vai với | Lý do xoá |
|---|---|---|
| Updateebm | `goi-duyet-tuan-ebm` (tuần, ra thẻ CANDIDATE) | Trùng lặp thu thập — vi phạm nguyên tắc owner duy nhất |
| Guideline | `giam-sat-acc-aha-quy` (quý) + `kiem-tra-hoan-thien-he-thong-thang` (tháng) | Trùng lặp thu thập |
| Updatethuoc | `thu-thap-tuan-an-toan-thuoc` (tuần, chạy `weekly_safety.sh`) | Trùng lặp 100% |
| Thangdiemls | Không trùng — mảng RAG 32 thang điểm không có tác vụ thật nào khác phủ | Bác sĩ chủ động xoá dù không trùng — **để lại khoảng trống giám sát mảng thang điểm, ghi nhận ở đây để không quên** |
| Tonghopcapnhat | Có thể trùng phần tổng hợp tuần của `goi-duyet-tuan-ebm` | Bác sĩ tự xác nhận trùng, xoá |
| Ebmdakhoa | Không trùng — lựa chọn cá nhân (bản tin đa khoa) | Bác sĩ không còn đọc |

**Trạng thái hiện hành:** tự động hoá chạy DUY NHẤT qua 5 `scheduled-tasks` nội bộ
(`goi-duyet-tuan-ebm` · `thu-thap-tuan-an-toan-thuoc` · `cap-nhat-thang-ebm` ·
`giam-sat-acc-aha-quy` · `kiem-tra-hoan-thien-he-thong-thang`) — xem
`mcp__scheduled-tasks__list_scheduled_tasks` để đối chiếu trạng thái thật bất kỳ lúc nào.
Không còn tác vụ nào ở tầng claude.ai web song song với tầng này — nguyên tắc "web = người
tiêu thụ ứng viên, KHÔNG là bộ thu thập thứ hai" nay đơn giản là không còn tầng web nào để áp
dụng nguyên tắc đó nữa.
