# A10 — impact-classifier

## 1. Định danh & vai trò
**Hiện thân thật:** gan_do_tin_cay() trong surveillance_scan.py (chạy TẠI CỬA NHẬN — BH37)

## 2. Đầu vào
ứng viên A2

## 3. Đầu ra
nhãn tin cậy: thiết kế + tầng + chưa-gán-loại (MEDLINE lag) + đã-có-trong-kho + đã-rút

## 4. Công cụ được phép
pubtype PubMed + RetractionChain

## 5. File được GHI (quan trọng nhất — xem ma trận ở README)
KHÔNG GHI riêng — nhãn nằm trong file ứng viên của A2

## 6. Cổng phải qua
E1

## 7. Điều kiện dừng khẩn
ứng viên đã-rút KHÔNG được vào hàng thường

## 8. Giới hạn (negative capability)
nhãn là XẾP HẠNG đọc trước/sau — không bao giờ là lý do LOẠI (BH38)

## 9. Một ca chuẩn
'⚡ mới vào PubMed — CHƯA gán loại' đọc trước thay vì bị lọc mất

## 10. Số đo chất lượng
15 chủ đề từng báo 'không có gì mới' nay có ứng viên

> Con trỏ biên chế — doctrine/tham số thật nằm ở hiện thân nêu trên. Sửa ở NGUỒN.
