---
name: plugin-router-chatgpt
description: "Điều phối yêu cầu rộng, mơ hồ hoặc nhiều bước tới đúng nhạc trưởng, plugin và skill trong hệ Claude–Codex–ChatGPT. Dùng khi cần tự chọn công cụ, phối hợp nhiều chuyên môn hoặc kiểm tra ai là owner; không thay một skill chuyên biệt đã được người dùng gọi rõ."
---

# Nhạc trưởng Plugin Claude–Codex–ChatGPT

Định tuyến theo nguyên tắc **một việc, một owner**. Chỉ gọi worker bổ trợ khi chúng tạo ra
đầu ra khác nhau và owner có thể hợp nhất được.

## Quy trình khép kín

1. Phân loại yêu cầu thành: ca lâm sàng, vòng đời nghiên cứu, việc nghiên cứu lẻ,
   truy xuất/thẩm định chứng cứ, viết–xuất bản, phân tích dữ liệu, hoặc kỹ thuật phần mềm.
2. Chọn nhạc trưởng/owner từ [governance.md](references/governance.md). Yêu cầu đích danh
   plugin chỉ ưu tiên worker, không chuyển quyền owner.
3. Nếu cần tên skill cụ thể, chạy:

   ```bash
   python3 scripts/route_skill.py "<yêu cầu>" --top 5
   ```

   Trong môi trường không chạy được script, tra [plugin-catalog.md](references/plugin-catalog.md)
   và chỉ đọc đúng mục plugin liên quan.
4. Chọn skill hẹp nhất; không nạp toàn bộ catalog hoặc gọi tất cả worker cùng lúc.
5. Trước khi giao việc, xác nhận worker hiện khả dụng. Nếu thiếu, owner tiếp tục bằng năng lực
   nội bộ và ghi `LOCAL_FALLBACK`; không giả vờ đã gọi plugin.
6. Mỗi worker phải trả: phạm vi đã làm, nguồn/đường dẫn đầu vào, kết quả, giới hạn và điều còn
   bất định. Owner loại trùng, xử lý mâu thuẫn và tạo một đầu ra thống nhất.
7. Chạy guardrail. Lỗi sửa được được định tuyến lại tối đa ba vòng; lỗi PII, an toàn, quyền
   owner hoặc cổng người thì dừng và chuyển người duyệt ngay.
8. Chỉ kết thúc khi đạt một trạng thái rõ: `RELEASED`, `GATE_PENDING`, `LOCAL_FALLBACK`,
   `RETURNED_FOR_FIX` hoặc `BLOCKED`.

## Chọn nhạc trưởng

| Loại việc | Owner |
|---|---|
| Một ca lâm sàng ngoại trú | `dieu-phoi-lam-sang` |
| Một đề tài/vòng đời nghiên cứu | `dieu-phoi-nghien-cuu` |
| Thiết kế nghiên cứu lẻ | `thiet-ke-nghien-cuu` |
| Tổng quan hệ thống/meta-analysis | `tong-quan-y-van` / `meta-phan-tich` |
| Tìm tài liệu/chứng cứ | `thu-thu-tai-lieu` / `tra-cuu-chung-cu` |
| Trích dẫn | `kiem-chung-trich-dan` |
| Viết bản thảo | `viet-ban-thao` |
| Thống kê | `phan-tich-thong-ke` |
| Kỹ thuật phần mềm | workflow kỹ thuật của repo |

## Ranh giới

- Plugin không được tự mở Cổng A/B/G, tự xác nhận IRB, khóa SAP/dữ liệu hoặc ký thay người.
- Không coi “đã cài” là “đang khả dụng”; phải kiểm session/runtime hiện tại.
- Không dùng `humanizer` để thay đổi số liệu, trích dẫn hoặc kết luận khoa học.
- Với y khoa/nghiên cứu: không PII, không bịa PMID/DOI/dữ liệu và luôn giữ mức bất định.
