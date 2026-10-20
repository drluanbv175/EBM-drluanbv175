# 20/10/2026 — Bước toàn văn ③: «còn bài chờ bác sĩ» bị báo thành «công cụ con lỗi hạ tầng/quá giờ»

**Phát hiện.** Lượt quét 7 chủ đề cũ ngày 20/10/2026 (`ops/orchestrator.py --topic … --online`, phục vụ vấn đề «độ tươi
chứng cứ»): CẢ 7 chủ đề đều nhận «⚠ 1 công cụ con lỗi hạ tầng/quá giờ — số liệu có thể thiếu, chạy lại khi mạng ổn», trong
khi mạng vẫn ổn và các bước khác đều chạy xong.

**Nguyên nhân gốc.** `tools/toan_van_theo_chu_de.py` bước ③ gọi `doc_toan_van_co_nguoi.py` (phiếu làn trình duyệt). Hợp
đồng của công cụ con: «phiếu 0 hết việc · 1 còn bài chờ · 2 KHÔNG ĐO ĐƯỢC». Bước ③ coi mọi mã ≠ 0 là cảnh báo, nên mã 1 —
đúng việc của bước này và đã được đếm ở «còn thiếu N» — trở thành dòng ⚠. Orchestrator đếm mọi dòng ⚠ là «lỗi hạ tầng/quá
giờ». Hậu quả là đỏ giả (§0.2): bác sĩ tưởng mạng hỏng và chạy lại vô ích.

**Cách vá.** Hằng số `MA_PHIEU_CON_BAI_CHO = 1`. Bước ③ chỉ cảnh báo khi mã ∉ {0, 1}: 2 (không đo được), -9 (quá giờ),
hoặc mã lạ.

**Kiểm hồi quy.** `tools/test_tv_buoc3_ma1_khong_phai_loi_20261020.py` gồm 5 ca:
- mã 1 ⇒ không có dòng ⚠, phiếu orchestrator vẫn nói «N bài còn thiếu toàn văn»;
- mã 2/-9/3 ⇒ vẫn cảnh báo;
- hằng số khớp chuỗi hợp đồng trong docstring công cụ con.

Ba phép đột biến (`rc != 0`; nuốt mã 2; nuốt mã -9) đều đỏ. 64 test toàn văn cũ vẫn xanh.
