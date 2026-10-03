# 03/10/2026 — EV-03: làn thẩm quyền báo «PASS / 0 ứng viên» suốt 7 tuần dù không quan sát được văn bản chính thức

**Số đo (đo lại 03/10 trên `EBM-Dashboards/surveillance/tuan-2026-W*-quet.json`).** «An toàn thuốc — cảnh báo mới (MHRA/FDA/EMA)»,
«NICE — hướng dẫn mới», «USPSTF — khuyến cáo dự phòng» trả PASS/0 ở cả 7 tuần W33–W40. Kiểm toàn diện 02/10 đọc tiêu đề 18 bản ghi mẫu
của truy vấn (8 USPSTF, 10 NICE): 0/18 là văn bản chính thức. Gói tuần đọc PASS/0 như «không có gì mới».

**Vá (2 bản `surveillance_scan.py` trong git, đồng bộ byte).** Không đổi `status`, vì bên tiêu thụ cũ đọc PASS/FAIL.
- `KENH_THAT_NGOAI_PUBMED` trỏ tới kênh khác ĐANG CÓ trong sổ nguồn:
  - cảnh báo thuốc → SRC-006 openFDA (weekly_safety.sh) + SRC-016 EMA/MHRA;
  - NICE → SRC-017 + SRC-037;
  - USPSTF → SRC-019.
  Test kiểm mọi mã SRC đều có thật trong sổ.
- `gan_ghi_chu_quan_sat()`: chủ đề thuộc bảng mà 0 ứng viên ⇒ nối ghi chú «QUAN SÁT HẠN CHẾ … 0 ứng viên ≠ không có cập nhật» vào
  trường ghi chú; không xoá ghi chú cũ.
- JSON thêm `quan_sat_han_che`; báo cáo Markdown thêm một dòng ⚪.
- Bước 2 của tác vụ tuần: chép khối này vào gói, cấm viết «không có gì mới» cho các chủ đề đó.

**Kiểm.**
- 5 test; tên chủ đề khớp watchlist THẬT (symlink tạm). 4 đột biến đều bị bắt.
- `pytest tools/` xanh.
- Bản runtime `EBM-Dashboards/tools/surveillance_scan.py` nhận vá sau khi gộp + `python3 tools/dong_bo_scanner_giam_sat.py`.
