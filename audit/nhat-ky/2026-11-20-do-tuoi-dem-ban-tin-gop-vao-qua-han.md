# 20/11/2026 — Độ tươi: số «quá 35 ngày» đếm cả bản tin gộp, còn «Lâu nhất» thì loại

**Hiện tượng.** `tools/kiem_do_tuoi_chung_cu.py` in (đo 20/11/2026, cây chính):
«114 chủ đề · trung vị 8 ngày · **11 chủ đề quá 35 ngày**» rồi «Lâu nhất: Orlistat_AKI_FDA (31ng) · …».
Hai dòng nói về hai tập khác nhau: số đếm tính MỌI lát cắt, danh sách loại bản tin gộp `khong_can`
(`EBM-Dashboards/giam-sat-chu-de.json`). Liệt kê từng lát cắt: cả 11 lát cắt quá 35 ngày đều là bản tin
tuần gộp (Uptodate, W24–W32, CapNhatTuan_NgoaiTru) — orchestrator không làm mới được (không có A2).
Chủ đề làm mới được cũ nhất: 31 ngày.

**Hậu quả suýt xảy ra.** Một phiên nhận việc «làm mới ~11 chủ đề quá 35 ngày» và chuẩn bị lập danh sách
≈ 0,5–0,8 triệu token/chủ đề cho việc không làm được. Bắt được nhờ đếm lại theo từng lát cắt trước khi
hỏi bác sĩ (CLAUDE.md §0.2 — «con số này của TẬP HỢP hay của MỘT phần tử»).

**Vá.** `in_bang_tuoi()`: trung vị và số «quá hạn» chỉ tính chủ đề LÀM MỚI ĐƯỢC; bản tin gộp in dòng riêng
(số bản + số bản quá hạn — vẫn hiện, không giấu). Gọi không truyền `khong_can` ⇒ hành vi cũ.
Sau vá (20/11/2026): «102 chủ đề · trung vị 8 ngày · 0 chủ đề quá 35 ngày» + «(12 bản tin gộp … 11 bản quá 35 ngày)».

**Kiểm hồi quy.** `tools/test_kiem_do_tuoi_khong_can.py` thêm 3 ca. Đột biến (`python -B`, xoá `__pycache__`):
(1) tính tuổi trên toàn bộ lát cắt ⇒ 3 ca đỏ; (2) giấu dòng bản tin gộp ⇒ 3 ca đỏ; phục hồi ⇒ xanh.
Người tiêu thụ stdout (`tu_de_xuat_viec.py` đọc `trung vị (\d+)`, gương cloud) không đổi khuôn chuỗi.
