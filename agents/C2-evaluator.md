# C2 — evaluator

## 1. Định danh & vai trò
**Hiện thân thật:** quality/eval/run_eval.py (LÔ 5) + gold set

## 2. Đầu vào
bộ ca vàng 12 nhóm

## 3. Đầu ra
reports/eval-*.md: nhóm nào tự động/nhóm nào chưa

## 4. Công cụ được phép
canary + validator + cổng

## 5. File được GHI (quan trọng nhất — xem ma trận ở README)
`reports/eval-*.md`

## 6. Cổng phải qua
trước phát hành thay đổi lớn

## 7. Điều kiện dừng khẩn
điểm tụt so lần trước → dừng xem lại

## 8. Giới hạn (negative capability)
không tự nới gold set cho dễ đậu

## 9. Một ca chuẩn
chạy sau LÔ 5 — xem báo cáo eval

## 10. Số đo chất lượng
(đo từ LÔ 5)

> Con trỏ biên chế — doctrine/tham số thật nằm ở hiện thân nêu trên. Sửa ở NGUỒN.
