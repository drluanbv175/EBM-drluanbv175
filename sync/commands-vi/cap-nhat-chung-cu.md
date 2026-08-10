---
description: "Cập nhật chứng cứ cho một vấn đề lâm sàng — dựng dashboard rồi xuất BỘ NĂM (dashboard · bản đọc · Word · Word-dạng-HTML · PDF giữ màu)"
---

Vấn đề lâm sàng cần cập nhật: **$ARGUMENTS**

Dùng kỹ năng `cap-nhat-chung-cu-y-khoa`, chạy trọn dây chuyền, KHÔNG hỏi từng bước.

## Sau khi dựng xong dashboard — MỘT lệnh duy nhất

```bash
python3 tools/xuat_goi_cap_nhat.py <dashboard>.html --online
```

Sinh đồng thời **năm** sản phẩm từ CÙNG khối `DATA`, nên không bản nào tụt phiên bản:
① dashboard (đã qua cổng liêm chính) · ② bản đọc · ③ bản Word `.docx` (bản lưu trữ chuẩn) ·
④ Word dạng HTML (đọc thẳng trong khung chat) · ⑤ **PDF giữ màu** huy hiệu mức chứng cứ.

Rồi chạy tiếp: `tools/drug_safety_scan.py` nếu có thuốc cho người cao tuổi/đa thuốc, và
`tools/build_library.py add <dashboard>.html` để tích lũy vào chỉ mục tra cứu.

**KHÔNG tự chạy `EBM_MASTER/tools/sync_all.py`** — chỉ khi bác sĩ yêu cầu riêng.

## Xong thì mở luôn cho bác sĩ

Gửi cả năm file bằng SendUserFile — `display:"render"` cho dashboard, bản đọc,
Word-dạng-HTML và PDF; `.docx` đính kèm để tải. Đừng bắt bác sĩ tự tìm trong thư mục.

Cổng liêm chính không đạt thì vẫn xuất, nhưng bản Word tự hạ câu chữ thành "CẦN xác minh".
Mọi khẳng định kèm PMID/DOI; KHÔNG PII. Cần bác sĩ kiểm chứng.
