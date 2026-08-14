# A9 — safety-overlay

## 1. Định danh & vai trò
**Hiện thân thật:** EBM-Dashboards/data/drug_flags.json + tools/run_retraction_and_med_safety.py + weekly_safety.sh

## 2. Đầu vào
thuốc xuất hiện trong khuyến cáo

## 3. Đầu ra
cờ an toàn (Beers/STOPP/AWaRe/hộp đen) đè lên ứng viên

## 4. Công cụ được phép
openFDA + danh mục cờ nội bộ

## 5. File được GHI (quan trọng nhất — xem ma trận ở README)
`data/drug_flags.json` (đợt có bác sĩ duyệt)

## 6. Cổng phải qua
chạy trong B2 và tờ dặn bệnh nhân

## 7. Điều kiện dừng khẩn
cảnh báo hộp đen mới trên thuốc đang APPLY → alert

## 8. Giới hạn (negative capability)
cờ là NHẮC, không phải chống chỉ định tự động; nguồn quy phạm không bị hạ (BH03)

## 9. Một ca chuẩn
azithromycin trên dashboard CAP → cờ AWaRe Watch hiện ngay khi dựng

## 10. Số đo chất lượng
4 cờ AWaRe mới 15/08; bắt sống 1 ca trên CAP

> Con trỏ biên chế — doctrine/tham số thật nằm ở hiện thân nêu trên. Sửa ở NGUỒN.
