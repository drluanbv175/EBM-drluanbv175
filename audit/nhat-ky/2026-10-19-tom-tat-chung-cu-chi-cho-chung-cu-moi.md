# 19/10/2026 — Tóm tắt chứng cứ Word chỉ cho chứng cứ MỚI: mốc «để nguyên», bước ⑨ của bộ năm, giác quan hòm việc

## Bác sĩ quyết định
Bác sĩ được báo chi phí đo thật: kiểm chéo độc lập một bài 12 trang tốn khoảng 361.000 token; ngoại suy cả tầng 1 vào khoảng 25–60 triệu token. Sau đó bác sĩ quyết: «Bây giờ xây dựng cho những chứng cứ sau này, còn hiện tại hãy để nguyên».

## Đã làm
- `tools/tom_tat_chung_cu_word.py moc --loi "<nguyên văn>"`:
  - ghi `OneDrive/EndNote/TomTatChungCu/_moc_de_nguyen.json` — mọi recNum đang có (kể cả bản ghi trong thùng rác), kèm lời bác sĩ;
  - không ghi đè mốc trừ khi có `--ghi-de`;
  - lời căn cứ phải đủ dài.
  - Đã ghi mốc với 1887 bản ghi. Các bản ghi này không bao giờ vào hàng chờ, kể cả khi sau này được gắn thêm PDF.
- `hang-cho [--dashboard] [--chuan-bi] [--json]`:
  - lấy bản ghi có PDF, nạp SAU mốc và chưa có Word;
  - lọc được theo trích dẫn của một dashboard.
  - Thiếu mốc, mốc hỏng hoặc mốc rỗng ⇒ trả `None`, KHÔNG đoán (nếu coi mốc rỗng là hợp lệ, cả thư viện sẽ bị đẩy vào hàng chờ).
- `xuat_goi_cap_nhat.py` thêm bước ⑨, chạy sau ⑧, chỉ khi `--online` (gói đọc phải tra rút bài):
  - lập hàng chờ của chủ đề và dựng sẵn gói đọc;
  - best-effort, không đổi mã thoát.
  - Python chỉ liệt kê. Phiên Claude xử lý tuần tự theo skill `cap-nhat-chung-cu-y-khoa` v1.54.0, bước ⑨.
- `tu_de_xuat_viec.py` thêm giác quan ⑦n:
  - báo 🛎 «N trích dẫn MỚI có PDF chờ tóm tắt»;
  - chưa có mốc ⇒ giác quan chết (⚪), không phải «không có việc».

## Kiểm
- `tools/test_tom_tat_chung_cu_tuong_lai_20261019.py`: 9 ca.
- 7 phép đột biến đều làm kiểm đỏ: bỏ lọc mốc · coi mốc rỗng là hợp lệ · không bỏ mục đã có Word · ghi đè mốc · bỏ lọc dashboard · giác quan im lặng khi chưa có mốc · ⑨ chạy khi không có `--online`.
