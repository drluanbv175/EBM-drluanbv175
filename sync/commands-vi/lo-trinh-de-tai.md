---
description: "Lộ trình làm trọn một đề tài: gọi lệnh nào, theo thứ tự nào, dừng ở cổng nào — và đề tài đang ở đâu"
---

Đề tài (mã hoặc tên, để trống nếu chỉ muốn xem lộ trình): **$ARGUMENTS**

1. Đọc `LO-TRINH-DE-TAI.md` ở thư mục gốc dự án.

2. Nếu bác sĩ đưa MÃ đề tài, chạy để biết trạng thái THẬT:
   `cd medical-ebm-automation && python tools/study_readiness.py --study <mã>`
   Công cụ này cố ý bi quan: chỉ đếm việc CHƯA làm, và chỉ ghi "ĐÃ KÝ" khi sổ cái xác
   nhận thật. Đừng suy diễn thêm ngoài những gì nó in ra.

3. Trả lời bác sĩ đúng 3 ý, ngắn gọn:
   - **Đang ở bước nào** (số thứ tự trong lộ trình A hoặc B)
   - **Gọi gì tiếp theo** — đúng MỘT lệnh, kèm một câu vì sao
   - **Cổng ký gần nhất phía trước** và ai phải ký

4. Nếu chưa có mã đề tài: hỏi loại đề tài (nghiên cứu gốc hay tổng quan hệ thống) rồi
   chỉ lộ trình tương ứng, bắt đầu từ bước 1.

Không tự chạy bước nào — chỉ chỉ đường. Bác sĩ gọi lệnh kế tiếp khi sẵn sàng.
