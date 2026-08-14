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

## 6 tác vụ claude.ai web (Q2: CÓ tồn tại) — bảng hợp nhất
| Tác vụ web | Trùng vai với | Đề xuất |
|---|---|---|
| Updateebm | routine `uptodate` + skill cập nhật | GIỮ 1: web gọi ĐÚNG skill `cap-nhat-chung-cu-y-khoa` (v1.42.0) để ăn cùng cổng; nội dung là ỨNG VIÊN |
| Guideline | `giam-sat-chung-cu` + quét quý mới | web chỉ TỔNG HỢP, không thu thập song song (owner thu thập duy nhất) |
| Updatethuoc | `drug-safety-daily` + weekly_safety | như trên |
| Thangdiemls | RAG 32 thang điểm | giữ, tần suất thấp |
| Tonghopcapnhat | `tong-hop-chung-cu-hang-tuan` | hợp nhất một bản |
| Ebmdakhoa | bản tin đa khoa | giữ nếu bác sĩ còn đọc |
⚠ Chi tiết prompt/lịch của 6 tác vụ nằm phía claude.ai — `[CẦN XÁC NHẬN TẠI ĐƠN VỊ]`
từng cái khi bác sĩ mở trang Tasks; nguyên tắc hợp nhất: **web = người tiêu thụ ứng viên,
KHÔNG là bộ thu thập thứ hai** (doctrine owner duy nhất).
