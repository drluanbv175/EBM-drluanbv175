# Cú pháp KỊCH BẢN cho skill tạo video TikTok

File kịch bản là `.md`/`.txt` thuần. Gồm 2 thành phần: **directive cấu hình** (dòng
bắt đầu `::`) và **lời đọc** (mọi dòng còn lại). Dòng trống = ngắt đoạn (lấy hơi).

## 1. Dấu NGHỈ trong lời đọc (tạo nhịp "ngắt nghỉ, mềm mại")

| Dấu | Ý nghĩa | Mặc định |
|-----|---------|----------|
| `,` `.` `!` `?` | edge-tts tự ngắt nghỉ tự nhiên theo dấu câu | (tự động) |
| `…` hoặc `...` | nhấn nhá nhẹ, ngập ngừng | ~0.40s |
| `\|\|` | nghỉ LẤY HƠI rõ (giữa các ý lớn, trước câu chốt) | ~0.80s |
| `[0.6s]` | nghỉ CHÍNH XÁC theo số giây ghi trong ngoặc | đúng số đó |
| (dòng trống) | hết một đoạn → nghỉ dài | ~0.55s |

Mẹo: câu ngắn + đặt `,` đúng chỗ là cách tốt nhất để giọng nghe dịu, tự nhiên.
Dùng `||` tiết chế (1–2 lần mỗi đoạn) để không bị "khựng".

## 2. Directive cấu hình (`::`)

Đặt ở đầu file hoặc bất cứ đâu. CLI (cờ dòng lệnh) sẽ GHI ĐÈ directive.

| Directive | Tác dụng | Ví dụ |
|-----------|----------|-------|
| `::tieu-de TEXT` | Tiêu đề ghim trên đầu video | `::tieu-de 3 mẹo ngủ ngon` |
| `::voice nu\|nam\|<id>` | Giọng đọc (mặc định `nu` = HoaiMy mềm) | `::voice nam` |
| `::rate -10%` | Tốc độ; **âm = chậm/mềm hơn** | `::rate -12%` |
| `::pitch -2Hz` | Cao độ (ít dùng) | `::pitch -1Hz` |
| `::che-do kinetic\|slide\|whiteboard` | Kiểu hình | `::che-do slide` |
| `::nen gradient\|toi\|sang\|#hex\|ẢNH` | Nền cho kinetic | `::nen #0F172A` |
| `::slide ĐƯỜNG_DẪN_ẢNH` | (chế độ slide) mở đoạn mới gắn ảnh này | `::slide ./anh/1.jpg` |
| `::nhac ĐƯỜNG_DẪN` | Nhạc nền (tự nhỏ tiếng + fade) | `::nhac ./nhac.mp3` |
| `::hashtag ...` | Hashtag cho caption khi đăng | `::hashtag #suckhoe #mẹo` |
| `::nguon ...` | Nguồn y khoa (PMID/DOI) → ghi vào video & mô tả | `::nguon PMID: 38912345` |
| `::disclaimer TEXT\|off` | Ép/bỏ khuyến cáo (mặc định: tự suy đoán) | `::disclaimer off` |
| `::zoom off` | Tắt hiệu ứng zoom mềm | `::zoom off` |

## 3. Giọng đọc có sẵn
- `nu` → `vi-VN-HoaiMyNeural` (nữ, dịu, mềm mại — **mặc định**)
- `nam` → `vi-VN-NamMinhNeural` (nam, trầm ấm)
- Hoặc ghi thẳng id edge-tts bất kỳ.
- Mất mạng / bị chặn tần suất kéo dài → tự lùi về giọng **Linh** (macOS, offline).

## 4. Ví dụ tối thiểu (chế độ mặc định — chữ động trên nền)
```
::tieu-de 3 mẹo uống nước đúng cách
::voice nu
::hashtag #suckhoe #uongnuoc #mẹovặt

Bạn uống nước mỗi ngày, nhưng đã đúng cách chưa? ||
Thứ nhất, uống ngụm nhỏ, chậm rãi… đừng tu một hơi.
Thứ hai, ưu tiên nước ấm vào buổi sáng. [0.5s] Nó giúp cơ thể tỉnh dậy nhẹ nhàng.
Lưu lại để nhớ nhé! || Theo dõi mình để xem thêm.
```

## 5. Ví dụ chế độ TRÌNH CHIẾU ẢNH
```
::che-do slide
::voice nu
::nhac ./nhac-nhe.mp3

::slide ./anh/intro.jpg
Có ba điều ít người để ý khi chăm sóc da buổi tối.

::slide ./anh/buoc1.jpg
Đầu tiên, làm sạch thật kỹ nhưng nhẹ nhàng.

::slide ./anh/buoc2.jpg
Tiếp theo, dưỡng ẩm khi da còn hơi ẩm để khoá nước.
```
Mỗi ảnh hiện đúng khoảng thời gian đang đọc đoạn của nó; phụ đề chạy đè lên trên.
