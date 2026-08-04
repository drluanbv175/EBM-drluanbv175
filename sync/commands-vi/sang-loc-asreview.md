---
description: "Mở ASReview LAB để sàng lọc tiêu đề/tóm tắt bằng học chủ động — máy xếp lại thứ tự đọc, bác sĩ vẫn là người dán nhãn"
---

Việc cần làm: **$ARGUMENTS**

## ASReview là gì, dùng ở đâu

Phần mềm ngoài (asreview 3.0.8, Apache-2.0) làm **sàng lọc tiêu đề/tóm tắt bằng học chủ động** (active learning) cho tổng quan hệ thống. Nó KHÔNG phải plugin Claude Code — chạy riêng, có giao diện web.

Vị trí trong lộ trình: **bước 5 của Lộ trình B** trong `LO-TRINH-DE-TAI.md` (sàng lọc), sau khi `/tong-quan-y-van` đã tìm và khử trùng lặp, trước bước trích xuất dữ liệu.

## Cách chạy

```bash
~/.asreview-venv/bin/asreview lab
```

Trình duyệt tự mở ở `http://127.0.0.1:5000`. Thoát bằng Ctrl+C. Thêm `--no-browser` nếu không muốn tự mở, `--port <số>` nếu cổng bận.

## Cách nó giúp — và KHÔNG giúp

Bác sĩ dán nhãn vài chục bài đầu (liên quan / không liên quan); mô hình học dần rồi **xếp lại thứ tự** những bài chưa đọc để bài có khả năng liên quan nổi lên trước. Nhờ vậy tìm đủ bài cần sớm hơn nhiều so với đọc theo thứ tự ngẫu nhiên.

**Nó KHÔNG tự loại bài nào.** Mọi bài chưa đọc vẫn là chưa đọc, không phải đã loại. Quyết định **dừng sàng lọc ở đâu** là của bác sĩ, và phải khai minh bạch trong PRISMA — nếu dừng trước khi đọc hết, đó là một quyết định phương pháp cần nêu rõ trong bài, kèm tiêu chí dừng đã định trước.

## Ba điều phải nhớ

1. **Dữ liệu nằm ở `~/.asreview` — NGOÀI OneDrive**, không tự đồng bộ sang máy Windows và không nằm trong git. Muốn giữ thì tự sao lưu; chính ASReview cũng nhắc điều này lúc khởi động.
2. **KHÔNG nạp dữ liệu có thông tin định danh bệnh nhân.** Đây là công cụ sàng lọc y văn, dữ liệu vào là danh mục tài liệu (RIS/CSV/BibTeX), không phải hồ sơ bệnh án.
3. **Số liệu PRISMA lấy từ đây phải khớp bài báo**: số bài nhập vào, số đã sàng, số loại và lý do. Xuất kết quả rồi đối chiếu bằng `/kiem-prisma`.

## Việc của Claude trong lệnh này

- Hướng dẫn bác sĩ đúng bước đang cần (chuẩn bị file nhập, khởi động, xuất kết quả).
- KHÔNG tự dán nhãn thay bác sĩ — nhãn liên quan/không liên quan là phán đoán chuyên môn.
- Khi bác sĩ đã xuất kết quả, nối tiếp sang `/kiem-prisma` và bước trích xuất dữ liệu.

Cần bác sĩ kiểm chứng.
