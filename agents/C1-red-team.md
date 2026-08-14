# C1 — red-team

## 1. Định danh & vai trò
**Hiện thân thật:** tools/thu_dau_cuoi_chung_cu.py (canary 10 lỗi gài, 2s, offline)

## 2. Đầu vào
dây chuyền A2→B2

## 3. Đầu ra
10/10 lỗi gài phải bị BẮT; lỗi lịch sử gài lại phải đỏ 5/8

## 4. Công cụ được phép
—

## 5. File được GHI (quan trọng nhất — xem ma trận ở README)
scratch only

## 6. Cổng phải qua
chạy trong BH43 mỗi SessionStart

## 7. Điều kiện dừng khẩn
canary đỏ = lỗ hổng THẬT ở dây chuyền — sửa trước mọi việc khác

## 8. Giới hạn (negative capability)
không sửa dây chuyền cho canary xanh giả (kiểm HÀNH VI, không đếm chuỗi)

## 9. Một ca chuẩn
15/08: canary đỏ lộ đúng vụ dotenv/python3 → vá tận gốc

## 10. Số đo chất lượng
10/10 bắt; tái phát: 2 lần đều bị chặn

> Con trỏ biên chế — doctrine/tham số thật nằm ở hiện thân nêu trên. Sửa ở NGUỒN.
