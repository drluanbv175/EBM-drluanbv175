# B2 — integrity-gate

## 1. Định danh & vai trò
**Hiện thân thật:** EBM-Dashboards/tools/verify_dashboard.py (--online --strict-sources)

## 2. Đầu vào
1 dashboard

## 3. Đầu ra
PASS/FAIL + exit 0/1/2 (sạch/gói-sai/chưa-xác-minh — BH48)

## 4. Công cụ được phép
toàn bộ luật item + nguồn đã rút (sổ A4)

## 5. File được GHI (quan trọng nhất — xem ma trận ở README)
KHÔNG GHI — cổng chỉ đọc (đúng thiết kế)

## 6. Cổng phải qua
E3+E2 cứng; return sớm bị cấm (BH01)

## 7. Điều kiện dừng khẩn
exit 1: sửa gói; exit 2: mạng — dùng sổ, KHÔNG chạy lại lấy lần đẹp

## 8. Giới hạn (negative capability)
không parse được = CHẶN, không đoán (BH02/21)

## 9. Một ca chuẩn
gói apply trên Cochrane-low → CHẶN kèm dòng lý do

## 10. Số đo chất lượng
51/62 PASS; 11 còn lại = đúng 26 mục na-apply chờ bác sĩ

> Con trỏ biên chế — doctrine/tham số thật nằm ở hiện thân nêu trên. Sửa ở NGUỒN.
