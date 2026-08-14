# A2 — source-harvester

## 1. Định danh & vai trò
**Hiện thân thật:** EBM-Dashboards/tools/surveillance_scan.py (chạy: python3 tools/surveillance_scan.py --topic <tên>)

## 2. Đầu vào
watchlist.json (4 tầng truy vấn) + cursor + RetractionChain tại cửa nhận

## 3. Đầu ra
surveillance/<ngày>-<chủ đề>.md: ứng viên mang nhãn tin cậy + tầng + trễ MEDLINE

## 4. Công cụ được phép
PubMed E-utilities (esearch/esummary); app/sources/retraction_chain.py

## 5. File được GHI (quan trọng nhất — xem ma trận ở README)
`.quet-cursor.json` · `.quet.lock` · `surveillance/*.md` · dòng vào `alerts/` (kênh append chung)

## 6. Cổng phải qua
E1 nhận diện + E2 rút bài tại cửa (BH37); latency đo mỗi lượt (BH43 canary)

## 7. Điều kiện dừng khẩn
scan FAIL toàn tầng · ứng viên đã rút → alert khẩn, KHÔNG vào hàng thường

## 8. Giới hạn (negative capability)
chỉ THU THẬP — không chấm GRADE, không đổi decision (BH10); không tự thêm chủ đề

## 9. Một ca chuẩn
--topic 'Suy tim' → 12 ứng viên, 2 tầng edat, trễ trung vị 3 ngày, 0 đã-rút

## 10. Số đo chất lượng
165 ứng viên/lượt toàn watchlist; 0-candidate topics 22→7 sau BH38

> Con trỏ biên chế — doctrine/tham số thật nằm ở hiện thân nêu trên. Sửa ở NGUỒN.
