# 17/11/2026 — Hai tích hợp app y khoa gọi API kiểu cũ; giác quan API im như xanh khi lượt gọi đã cũ

Bác sĩ hỏi «kết nối API đã hoàn thiện và tự động tốt nhất chưa» rồi duyệt «làm mục 1 và 2». Đo trên máy cùng ngày.

## 1. Hai tích hợp app y khoa (`ambient_scribe.py`, `image_reading.py`, viết 23/08/2026)

- **Đo được:** model mặc định cũ (`claude-sonnet-4-6`, `claude-opus-4-8`); `max_tokens=1500` mà model hiện hành luôn
  suy nghĩ và tính phần suy nghĩ VÀO `max_tokens`; không kiểm `stop_reason` ⇒ bản nháp SOAP/bản đọc ECG bị cắt cụt vẫn
  được trả như hoàn chỉnh (mục cuối — P của SOAP, cờ đỏ của bản đọc ảnh — là mục dễ mất nhất); không ghi nhật ký sức
  khoẻ `~/.ebm-api-claude.json` ⇒ hòm việc mù với hai đường này; khoá chỉ đọc từ biến môi trường.
- **Vá (repo y khoa):** `app/integrations/_api_claude.py` cho hai tích hợp đi qua cầu nối chung `tools/api_claude_nc.py`
  (cùng luật với ba công cụ hệ nghiên cứu): Sonnet 5.5 cho SOAP, Opus 5.5 cho ảnh (biến môi trường cũ vẫn đè được);
  `max_tokens` 16000; cắt cụt/từ chối ⇒ lỗi của tích hợp, không trả nửa câu trả lời; khoá theo §5 (môi trường → kho
  bí mật); ghi sức khoẻ với `nguon` = `ambient_scribe` / `image_reading`; dưới pytest không dựng khách thật. Chữ ký
  hàm và lớp lỗi giữ nguyên ⇒ bảng tích hợp Streamlit và CLI không phải sửa.
- **Kiểm:** `tests/test_api_tich_hop_20261117.py` (khách API giả); đột biến 7/7 bị bắt (model cũ ×2, `max_tokens` 1500,
  bỏ ghi sức khoẻ, kết quả hỏng ghi «error», bỏ kiểm cắt cụt ở cầu nối, sai `nguon`).

## 2. Giác quan `giac_quan_api_claude` không tính tuổi lượt gọi (repo gốc)

- **Đo được:** lượt «ok» chỉ nói khoá sống LÚC ĐÓ. Vài tuần không xuất gói nào thì nhật ký vẫn «ok» trong khi tín dụng có
  thể đã cạn — giác quan im như xanh (trái §0.2: «không đo được» ≠ «ổn»).
- **Vá:** lượt không lỗi cũ hơn `NGAY_API_CU` = 14 ngày, hoặc mốc thời gian không đọc được ⇒ ⚪ «chưa đo được» (không 👤 —
  không báo đỏ giả; vẫn KHÔNG gọi thử API). Lượt LỖI báo 👤 bất kể tuổi. Thêm `nguon` của hai tích hợp vào `_VIEC_API`
  để thông báo trỏ đúng lệnh `python -m app.integrations.cli soap|image`.
- **Kiểm:** 7 test mới trong `tools/test_canh_api_claude_20261117.py` (thời điểm tiêm qua `bay_gio`, không phụ thuộc
  ngày chạy CI); đột biến 6/6 bị bắt (bỏ luật tuổi, lệch biên `>`/`>=`, ngưỡng 30 ngày, mốc hỏng im lặng, lượt lỗi
  không báo, mất nguồn ambient).

## Còn ngoài tầm máy (không đo được từ Mac)

Khoá trên máy Windows và trong môi trường Cloud (mỗi nơi đặt riêng); trần chi tiêu tháng ở console.anthropic.com là cài
đặt tài khoản của bác sĩ.
