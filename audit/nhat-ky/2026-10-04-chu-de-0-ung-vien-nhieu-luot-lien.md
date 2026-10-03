# 04/10/2026 — Chủ đề watchlist 0 ứng viên nhiều lượt tuần liền mà bộ quét vẫn PASS, không ai thấy

**Phát hiện (đếm thô 03/10/2026):** `EBM-Dashboards/surveillance/tuan-2026-W39-quet.json` và `…W40…` có 10/47 chủ
đề 0 ứng viên ở cả hai lượt; 7 trùng danh sách «truy vấn mù» mà `tools/kiem_san_luong_giam_sat.py` đo 02/10 (EV-02,
BH148). Bộ quét vẫn PASS và tiến con trỏ. Đề xuất viết lại truy vấn (`EBM-Dashboards/watchlist.de-xuat.json`, soạn
02/10) chưa được áp. Chốt sản lượng chỉ chạy trong `chu_trinh_chung_cu` chế độ đầy đủ, không nằm trong dây chuyền tuần.
Kết quả: không ai thấy.

**Nguyên nhân:** từng mảnh đều có, nhưng không có cảm biến nối chúng. Mảnh 1 là trạng thái lượt quét, PASS của TẬP
HỢP. Mảnh 2 là đề xuất nằm chờ. Mảnh 3 là sản lượng truy vấn. Không công cụ nào hỏi «chủ đề này đã 0 bao nhiêu lượt
liền, và đã có ai xử lý chưa».

**Cách vá:**
- `tools/kiem_chuoi_0_ung_vien.py` là công cụ mới, ngoại tuyến, chỉ đọc. Nó đếm số lượt LIỀN mà một chủ đề ĐO ĐƯỢC và
  có 0 ứng viên, rồi đối chiếu với đề xuất chờ duyệt, sản lượng đo gần nhất và kênh ngoài PubMed (EV-03).
- Cảm biến ⑦j trong `tu_de_xuat_viec.py` gồm hai loại việc. Loại 👤 là duyệt đề xuất, có lệnh
  `ap_dung_de_xuat_watchlist.py` ở đầu mô tả. Loại 🛎 là đo hoặc soạn đề xuất.
- Bước 2b được thêm vào `sync/scheduled-tasks/goi-duyet-tuan-ebm/SKILL.md`.
- `bam_watchlist()` là định nghĩa băm DUY NHẤT, dùng chung cho cả ghi lẫn đọc kết quả sản lượng.

**Luật đo (khoá bằng test):**
- Chỉ chủ đề `PASS` mới là «đo được». PASS_DEGRADED, FAIL, tệp hỏng và lượt FAIL KHÔNG BAO GIỜ được đọc thành
  «0 ứng viên».
- Lượt PARTIAL không làm hỏng chủ đề PASS bên trong, vì trạng thái lượt là số của tập hợp.
- Lượt không đo được nằm giữa thì không bắc cầu; trường hợp này ghi riêng ⚪ «chưa tính là liền».
- Tuần không có tệp quét không tính là một lượt, vì con trỏ tăng dần K8 cho lượt sau phủ cả cửa sổ đó.
- Nguyên liệu hỏng thì ghi ⚪ hoặc mã 2, không bao giờ in «không có chủ đề mù».

**Đo thật 04/10/2026** trên 7 lượt W33→W40 (không có W38):
- 3 chủ đề thẩm quyền (MHRA/FDA/EMA, NICE, USPSTF) 0 ứng viên 7 lượt liền. Đây là khoảng trống đã biết (EV-03), ghi
  dòng ⓘ.
- 7 chủ đề 0 ứng viên ở W40 nhưng W39 suy giảm, nên được ghi «chưa tính là liền».
- Cả 10 chủ đề có đề xuất chờ duyệt đều thành MỘT việc 👤 🟠. Chưa có số đo sản lượng lưu.

**Kiểm hồi quy:** `tools/test_chuoi_0_ung_vien_20261004.py` có 40 test. Kiểm đột biến 14/14 đỏ đúng chỗ rồi phục
hồi xanh.

**Bài học:** «PASS» của một lượt và «0 ứng viên» của từng chủ đề là hai trục khác nhau. Một cảnh báo không có người
nhận (đề xuất nằm chờ) không tồn tại với dây chuyền: phải có cảm biến đưa nó vào hòm việc.
