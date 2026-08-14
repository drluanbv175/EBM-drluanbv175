# B5 — approval-broker

## 1. Định danh & vai trò
**Hiện thân thật:** tools/trinh_muc_can_duyet.py + hàng chờ bác sĩ

## 2. Đầu vào
mục cần quyết (na-apply, mâu thuẫn, đã-rút)

## 3. Đầu ra
danh sách trình bày NGUỒN-trước-THỂ-LOẠI (BH03) cho bác sĩ

## 4. Công cụ được phép
—

## 5. File được GHI (quan trọng nhất — xem ma trận ở README)
KHÔNG GHI decision — chỉ bác sĩ (I4/Cổng A/B)

## 6. Cổng phải qua
E6 NGƯỜI

## 7. Điều kiện dừng khẩn
—

## 8. Giới hạn (negative capability)
máy tuyệt đối không APPROVED/APPLIED; 3 việc lâm sàng cấm tự động (BH10)

## 9. Một ca chuẩn
13/08: 11 quyết định bác sĩ duyệt, 1 mục DỪNG vì dashboard khai sai nguồn

## 10. Số đo chất lượng
0 lần máy tự đặt decision (kiểm validator I4)

> Con trỏ biên chế — doctrine/tham số thật nằm ở hiện thân nêu trên. Sửa ở NGUỒN.
