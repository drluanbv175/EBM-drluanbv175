# C5 — orchestrator

## 1. Định danh & vai trò
**Hiện thân thật:** ops/orchestrator.py (LÔ 4) — driver mỏng gọi A2→B5 đúng thứ tự

## 2. Đầu vào
chủ đề (hoặc toàn watchlist) + cờ --dry-run/--since/--topic/--resume

## 3. Đầu ra
logs/<run_id>.jsonl + gói ứng viên cuối

## 4. Công cụ được phép
gọi các hiện thân trên, KHÔNG tự làm nội dung

## 5. File được GHI (quan trọng nhất — xem ma trận ở README)
`logs/*.jsonl` (+ khoá qua ops/lock.py)

## 6. Cổng phải qua
mọi cổng của từng bước giữ nguyên

## 7. Điều kiện dừng khẩn
bước nào exit≠0 → dừng đúng chỗ, ghi log, không nhảy cóc

## 8. Giới hạn (negative capability)
driver KHÔNG chứa logic y khoa — chỉ thứ tự + dừng; không đổi decision

## 9. Một ca chuẩn
(sau LÔ 4)

## 10. Số đo chất lượng
(sau LÔ 4)

> Con trỏ biên chế — doctrine/tham số thật nằm ở hiện thân nêu trên. Sửa ở NGUỒN.
