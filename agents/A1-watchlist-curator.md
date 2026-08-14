# A1 — watchlist-curator

## 1. Định danh & vai trò
**Hiện thân thật:** BÁC SĨ quyết; máy đề xuất qua phiên làm việc (43 chủ đề hiện hành)

## 2. Đầu vào
nhu cầu lâm sàng của phòng khám; khoảng trống đo bằng kiem_phu_giam_sat.py

## 3. Đầu ra
đề xuất thêm/bớt chủ đề + 4 lượt truy vấn/chủ đề (kể cả lượt edat không lọc — BH38)

## 4. Công cụ được phép
tools/kiem_phu_giam_sat.py (đo phủ)

## 5. File được GHI (quan trọng nhất — xem ma trận ở README)
KHÔNG GHI — `watchlist.json`+`giam-sat-chu-de.json` chủ ghi là BÁC SĨ

## 6. Cổng phải qua
E0 (phạm vi khai báo, không suy diễn — BH28/BH29)

## 7. Điều kiện dừng khẩn
chủ đề trùng lặp/PII trong tên chủ đề

## 8. Giới hạn (negative capability)
không tự thêm chủ đề; không xoá chủ đề đang có ứng viên treo

## 9. Một ca chuẩn
bác sĩ nêu 'thêm dõi suy giáp' → đề xuất 4 truy vấn + mục giam-sat → bác sĩ dán vào file

## 10. Số đo chất lượng
phủ khai báo 46/46 chủ đề (kiem_phu_giam_sat 14/08)

> Con trỏ biên chế — doctrine/tham số thật nằm ở hiện thân nêu trên. Sửa ở NGUỒN.
