# 12/11/2026 — Cập nhật chứng cứ hằng tháng theo thư mục EndNote (phiếu tháng + tác vụ lịch ngày 5)

**Lời giao.** Bác sĩ nói trong chat 12/11/2026: «Xây dựng tự động cập nhật chứng cứ hàng tháng với các thư mục trong Endnote»;
bổ sung cùng ngày: «Với việc cập nhật những chứng cứ áp dụng cho thực hành lâm sàng đảm bảo toàn văn và tóm tắt như đã xây dựng
cho hệ thống cập nhật chứng cứ».

**Khoảng hở.** Dây chuyền cập nhật đi theo dashboard + watchlist; thư viện EndNote, nơi bác sĩ đọc chứng cứ theo thư mục, không có
công cụ nào nhìn từ phía thư mục. Kiểm kê tay 12/11: 165 thư mục có bài, 96 gắn dashboard, 69 chưa gắn. Không gì báo thư mục nào
đã cũ, thư mục nào không được bộ quét canh, mục «Áp dụng» nào thiếu PDF/khối tiếng Việt trong EndNote.

**Làm.** `tools/cap_nhat_thang_thu_muc_endnote.py` (chạy khô mặc định):
- đo từng thư mục qua công cụ sẵn có, không chép logic: bản sao tạm `sdb.eni`, `chu_de_resolver`, báo cáo quét đã có,
  `kiem_moi_nhat_toan_van`, `bao_phu_cuc_bo`, `tom_tat_endnote_vi.MO_DAU_DA_DUNG`, `tom_tat_chung_cu_word.hang_cho`, luật ★
  `dat_ap_dung_tin_cay`;
- xếp mỗi thư mục vào một nhóm (a)–(d);
- ghi phiếu `EBM-Dashboards/derivatives/CAP-NHAT-THANG-THU-MUC_<YYYY-MM>.md/.json` và đề xuất watchlist (khoá riêng
  `_de_xuat_thu_muc_endnote`, giữ mọi khoá khác, có sao lưu);
- `--quet` gọi orchestrator có trần; `--hoan-thien` chạy phần máy §6.2.

Nối vào lịch bằng tác vụ MỚI `cap-nhat-thang-thu-muc-endnote` (ngày 5, 18:00), dấu vết `file-thang` (loại mới của
`kiem_lich_nen`). Giác quan hòm việc ⑦p báo 👤 thư mục cần bản nối tiếp và 🛎 bước ghi EndNote chờ phiên Claude. Chưa có phiếu
tháng này thì giác quan ⚪.

**Hai số đo đổi thiết kế (12/11/2026, dữ liệu thật):**
1. Đếm «ứng viên có mặt trong báo cáo quét sau ngày dashboard» thì gần mọi chủ đề rơi vào (a): bộ quét lấy cửa sổ 90 ngày nên
   mỗi tuần trình lại bài cũ, và `authority_source` là hội gắn với TẠP CHÍ (một tổng quan trên Diabetologia mang «ADA/EASD»), không
   phải dấu hiệu guideline. Sửa:
   - chỉ tính bài bộ quét trình LẦN ĐẦU sau ngày dashboard;
   - phân loại theo loại xuất bản PubMed thật;
   - ngưỡng tổng quan/RCT nâng lên 5.
   Nhóm (a) chia «ưu tiên» (guideline/đồng thuận mới · M1 · quá 90 ngày) và «theo dõi» (chỉ có tổng quan/RCT mới).
2. Chốt BH173 `test_khai_khong_chua_lenh_ghi_quyet_dinh_thay_bac_si` đỏ khi khai `--ap-dung` cho lượt lịch. Ranh giới bác sĩ duyệt
   28/10 chỉ cho lượt lịch ĐO/BÁO/DỰNG GÓI, không ghi EndNote. KHÔNG nới chốt. Cờ ghi của công cụ là `--ghi`: phiếu, đề xuất, quét
   candidate, gom/in toàn văn vào kho — gói tuần đã làm đúng các việc này. Bước ghi EndNote (gắn kho, khối tiếng Việt) cần THÊM
   `--ghi-endnote`, chỉ phiên Claude có người, có rào:
   - sức khoẻ EndNote 🟢;
   - không có giao dịch treo;
   - không có khoá ghi `~/.ebm-endnote-dang-ghi.json` của tiến trình khác;
   - không có cờ `TAM-DUNG-ENDNOTE`.

   Rào được kiểm trước TỪNG bước ghi. Muốn lượt lịch ghi EndNote thì bác sĩ đổi `_ranh_gioi` và chốt kèm nguyên văn lời bác sĩ —
   không đổi tên cờ để lách.

**Lượt thật đầu tiên (13/11/2026 03:34, chế độ báo cáo, không quét, không hoàn thiện)** trên 165 thư mục:
- (a) 31: ưu tiên 15, theo dõi 16;
- (b) 34;
- (c) 71: 45 nhóm EBM cũ (cả 45 khớp câu hỏi một bản dashboard cũ), 19 khung, 3 NC/TT, 4 thư mục bác sĩ có nội dung thật;
- (d) 29: 17 🟢, 12 ⚪ vì dashboard vừa dựng, chưa có lượt quét sau đó.

Mục apply chưa đọc toàn văn: 0. PDF chưa gắn vào EndNote (apply/consider): 201. Thiếu khối tiếng Việt: 0. ⑨ chờ: 0.

**Kiểm hồi quy.** `tools/test_cap_nhat_thang_thu_muc_endnote_20261112.py`: 20 test, toàn fixture/mock, không đọc EndNote thật,
không gọi mạng. 11 đột biến đỏ đúng test rồi phục hồi xanh (`python -B`, xoá `__pycache__`):
- bỏ kiểm khoá; bỏ kiểm cờ tạm dừng;
- đảo in PDF ↔ gắn kho;
- bỏ lọc «lần đầu»;
- quét không dừng khi hạ tầng hỏng;
- chạy khô vẫn ghi;
- mục không định danh thành «chưa có bản ghi»;
- `authority_source` thành guideline;
- `kiem_lich_nen` bỏ `file-thang`;
- rào chỉ kiểm một lần;
- lượt lịch ghi EndNote.

Cần bác sĩ kiểm chứng.
