# 22/11/2026 — Khâu 9–10 chưa có ở cổng phán giả lập: hình bắt buộc và mục hạn chế trượt chuẩn mà CI vẫn xanh

**Bối cảnh:** bác sĩ giao kiểm toàn hệ 11 khâu nghiên cứu (vấn đề → … → công bố) trên mọi đề tài giả lập; nội dung
không đạt chuẩn thì phải loại bỏ.

**Đo (ảnh chụp 22/11/2026):** dùng 24 báo cáo CI giả lập của drluanbv175/medical-ebm-automation#401. Cả 24 kịch bản khoá được G10,
0 ô lỗi máy, đề cương nộp đạt K1–K17. Hai khâu không có trong `kiem_gia_lap_16`:

- **Khâu 9 (trình bày kết quả):** 22/24 kịch bản thiếu hình bắt buộc `so_do_luong`. Nguyên nhân: lượt G6 chỉ dựng
  MẪU sổ sàng lọc, cột n trống ⇒ `CHUA_DU_SO`. Bộ phán chỉ đỏ khi hình LỖI, không đỏ khi hình bắt buộc THIẾU. Nhãn
  danh mục hình RCT còn ghi «CONSORT 2010 (mục 13)».
- **Khâu 10 (diễn giải):** `dien_giai_ket_qua.kiem` chỉ đòi có chữ «hạn chế».
  - 11/24 bản không bàn khả năng khái quát.
  - 11/24 bản không nêu nguồn sai lệch.
  - Gần như không bản quan sát nào nói hướng của sai lệch (STROBE 19 đòi «cả hướng lẫn độ lớn»).
- **Kèm (phiên K18 đo bản thảo G7):** luật `khong_ap_dung` của giả lập đọc cả câu «Ví dụ với cohort: thiếu ngẫu
  nhiên hóa…» trong khuôn. Hệ quả: ô «§5 Hạn chế» của thuần tập bị điền «chỉ áp dụng cho thử nghiệm ngẫu nhiên».

**Vá (drluanbv175/medical-ebm-automation#403):**
- **Sổ sàng lọc:** vai nghiên cứu viên giả lập điền sổ sàng lọc mô phỏng rồi chạy lại G6, đúng đường hướng dẫn cho đề
  tài thật.
  - Hộp cuối mỗi nhánh bằng n phân tích chính.
  - Nhánh chia theo dữ liệu đã khoá.
  - Số học kiểm bằng `bieu_do_bao_cao.kiem_so_hoc_luong`.
- **Cổng phán `kiem_gia_lap_16`:** đỏ khi thiếu hình bắt buộc, khi có hình lỗi, khi không có biểu đồ, hoặc khi G6.5
  chưa đạt.
- **Diễn giải:** `kiem_han_che_khai_quat` kiểm theo chuẩn của từng thiết kế.
  - RCT: CONSORT 2025 mục 30.
  - Quan sát: STROBE 19, 21.
  - Chẩn đoán: STARD 26. Dự báo: TRIPOD+AI 26.
  - Tổng quan gộp: PRISMA 23b/23c. Định tính: SRQR 18/19.
  - Không suy được thiết kế ⇒ lỗi, không coi là đạt.
- Văn bản mục 4–5 của 13 kịch bản được viết lại.
- `phan_loai_o` bỏ phần «Ví dụ…» khi xét «không áp dụng».
- Agent `dien-giai-ket-qua` và `viet-ban-thao` được dạy luật mới trong PR cặp này.

**Kiểm hồi quy:** `tests/test_chuan_khau_9_10_20261122.py` (40 ca); 13 phép đột biến đều đỏ, phục hồi xanh. Chạy CI 24
kịch bản: sơ đồ luồng vẽ thật (thuần tập 8→9 hình, chẩn đoán 15→16), G6.5 đạt, G10 vẫn khoá.

**Bài học:** bộ phán CI chỉ bắt được điều nó đọc. Mỗi khâu mới có đầu ra (hình, bản diễn giải…) phải có dòng trong
`kiem_gia_lap_16`. Nếu không, «24/24 xanh» không nói gì về khâu đó.

**Còn mở (chưa vá, ghi để không ai hiểu nhầm là đã đạt):**
- RCT giả lập không có biến tổn hại theo nhóm, nên CONSORT 2025 mục 27 và 29 chưa có dữ liệu.
- Bảng 1 RCT còn hàng biến định danh và nhóm 0/1 chưa nhãn. Đã báo phiên K18.
- Câu số sàng lọc trong văn bản G7 (STROBE 13a/13b) chưa đọc `SO_DO_LUONG`. Đã đề nghị phiên K18.
