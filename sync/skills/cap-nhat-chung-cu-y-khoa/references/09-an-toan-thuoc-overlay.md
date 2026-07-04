# 09 — Lớp phủ an toàn thuốc (người cao tuổi / đa thuốc)

Khi một bản cập nhật có khuyến cáo **dùng thuốc** và liên quan nhóm `cao-tuoi` hoặc `da-thuoc`, chạy lớp phủ an toàn — **giảm hại, tránh kê đơn không phù hợp (PIM)**.

## Quy trình
1. Sau khi dựng dashboard, chạy:
   `python3 tools/drug_safety_scan.py <dashboard>.html`
   → quét tên thuốc, đối chiếu bảng cờ cô đọng (`data/drug_flags.json`, nguồn **Beers 2023 / STOPP-START v3**), in cảnh báo + sinh **prompt rà soát đầy đủ**.
2. Với BN cao tuổi/đa thuốc thật: dán prompt vào skill **`nguoi-cao-tuoi-da-benh-da-thuoc`** (skill này giữ tiêu chí GỐC đầy đủ: Beers AGS 2023, STOPP/START v3, gánh nặng kháng cholinergic, té ngã, hạ đường huyết, hạ HA tư thế).
3. Bổ sung kết quả vào dashboard: ghi cảnh báo ở trường `monitoring`/`safety` của item liên quan, hoặc `groups` đánh dấu `cao-tuoi`/`da-thuoc`.

## Giới hạn & liêm chính
- Bảng `drug_flags.json` **KHÔNG đầy đủ**, chỉ để **nhắc rà soát**; không thay tiêu chí gốc.
- Không tự khẳng định "phải ngưng thuốc" — nêu **cờ + lý do + nguồn**, để bác sĩ quyết định theo bối cảnh.
- Đối chiếu nguyên văn Beers 2023 / STOPP-START v3 trước khi áp dụng.
- Cá thể hóa mục tiêu (HbA1c, huyết áp) ở người cao tuổi theo skill người cao tuổi.

## Cập nhật bảng cờ
Khi có phiên bản Beers/STOPP mới, sửa `data/drug_flags.json` (giữ trường `source` + `_updated`).
