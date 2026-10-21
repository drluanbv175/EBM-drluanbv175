# 21/10/2026 — EMA chặn theo IP của VPN, NCBI chặn IP Việt Nam: lô chứng cứ phải tắt/bật VPN giữa chừng

**Hiện tượng.** Lô `ops/orchestrator.py --resume 20261018T143247-lo` dừng ở bước B2 của gói EMA_PRAC: mọi URL
`www.ema.europa.eu/en/news/meeting-highlights-…-prac-…` trả HTTP 403 cho cổng `verify_dashboard.py --online --strict-sources`.

**Đo (21/10/2026).**
- VPN BẬT: urllib nhận `HTTP Error 403: Forbidden`; chính trình duyệt trong app cũng nhận trang CloudFront «403 ERROR — The request
  could not be satisfied. Request blocked» ⇒ chặn theo IP thoát của VPN, KHÔNG phải chặn theo trình khách.
- VPN TẮT: trình duyệt mở được 3 trang PRAC (8–11/6, 6–9/7, 31/8–3/9/2026) đúng tiêu đề; cổng EMA_PRAC_20261021 PASS (4 URL HTTP
  200). Nhưng `medical-ebm-automation/tools/do_mang_nguon.py` đo NCBI E-utilities = `ncbi-chan` ⇒ bước A2 quét CKD không chạy
  được (thẻ `[MeSH Major Topic]` không dịch sang Europe PMC ⇒ fail-closed, đúng thiết kế).
- Hai nguồn đòi hai đường mạng NGƯỢC nhau ⇒ lô phải chạy: tắt VPN cho bước EMA → bật VPN cho phần còn lại (dừng 3 lần, bác sĩ
  bật/tắt VPN 4 lần).

**Vá (bác sĩ duyệt).** Khai `www.ema.europa.eu` + `ema.europa.eu` vào `MIEN_CHAN_TRUY_CAP_TU_DONG` — cùng cơ chế với FDA: 403 của
EMA khi VPN bật không còn là «lỗi mạng» dừng lô, mà đòi bằng chứng đã mở bằng trình duyệt thật trong
`EBM-Dashboards/url-xac-minh-trinh-duyet.json` (khớp đúng URL, hạn 180 ngày). Thiếu bằng chứng ⇒ orchestrator đổi thành việc 👤 và lô
đi tiếp (BH150). Lấy bằng chứng = tắt VPN, mở trang trong trình duyệt, `tools/xac_nhan_trinh_duyet.py --ghi`. Tên máy chủ khớp
chính xác (miền giả dạng như `www.ema.europa.eu.evil.com` không được nhận). `xac_nhan_trinh_duyet.py` từ chối tiêu đề chỉ là tên
cơ quan EMA và tiêu đề trang CloudFront (`ERROR: …` — luật sẵn có).

**Kiểm.** `tools/test_verify_dashboard_mien_chan_ema_20261021.py` 13 ca (cả hai chiều); test miền chặn cũ + làn xác nhận vẫn
xanh (63 ca). Đột biến: gỡ miền EMA ⇒ 5 ca đỏ; gỡ tiêu đề chung EMA ⇒ 1 ca đỏ; phục hồi ⇒ xanh.

**Không làm.** Không đổi `MA_CHAN_TU_DONG`, không giả dạng trình duyệt, không tự ghi sổ trước khi PR được gộp (công cụ ghi sổ từ
chối miền chưa khai trong bản cổng đang chạy).
