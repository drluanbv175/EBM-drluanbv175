# 02/10/2026 — 10/42 truy vấn watchlist «mù» (≤3 bản ghi/90 ngày) mà chốt phủ giám sát vẫn xanh «49/49» (EV-02, BH148)

**Triệu chứng.** Kiểm toàn diện 02/10: `kiem_phu_giam_sat.py` báo «Mọi chủ đề đã khai (49/49)», nhưng đo sản lượng thật (esearch `retmax=0`, ghép ĐÚNG bộ lọc loại thiết kế
của `surveillance_scan.search()`, `reldate=90`) cho 42 chủ đề có đủ 4 tầng: **10 chủ đề tổng ≤3 bản ghi trong CẢ BỐN tầng** — Lupus thận, Cấp cứu ban đầu, Hội chứng thận hư,
Suy thượng thận, Kê đơn tâm thần kinh = 0; Viêm đa dây TK = 1; RA, Động mạch cảnh/mạch máu não = 2; Gout = 2; Hen = 3 — trong khi ĐTĐ+béo phì+GLP-1 = 1.441. Tôi tự đo lại độc
lập (không dùng số của agent): cùng 10/42 chủ đề mù; lệch duy nhất là Gout 2 (agent báo 3); RA = guideline 0 · SR/MA 0 · RCT 0 · mới-vào 2.

**Nguyên nhân gốc.** (1) Chốt phủ chỉ đo KHAI BÁO («chủ đề có mục watchlist»), không đo mục đó tìm ra gì. (2) Cụm truy vấn dài viết như câu («rheumatoid arthritis treatment EULAR
guideline», «lupus nephritis IgA nephropathy treatment guideline») bị PubMed ngầm AND mọi từ: đòi cả «EULAR» lẫn «guideline», hoặc cả hai bệnh trong một bản ghi. Hệ quả: «0 ứng viên»
đọc thành «không có chứng cứ mới» trong khi thật ra là cấu trúc truy vấn (CLAUDE.md §6.4).

**Vá (không tự ý đổi watchlist).**
- `tools/kiem_san_luong_giam_sat.py`: đo sản lượng từng tầng bằng ĐÚNG `DESIGN`/`EUTILS`/kênh TLS của bộ quét chuẩn (nạp từ `sync/skills/…/surveillance_scan.py`, không chép tay); tổng ≤3 ⇒ 🔴 «có thể mù»;
  tầng lỗi mạng ⇒ ⚪ KHÔNG ĐO ĐƯỢC (không bao giờ thành 0/ổn); không đo được gì ⇒ mã 2. `--dung-lai-neu-moi-hon-ngay 7` dùng lại kết quả khi cùng băm watchlist/ngưỡng/cửa sổ và lần đó đo trọn.
- `tools/ap_dung_de_xuat_watchlist.py`: bác sĩ duyệt `EBM-Dashboards/watchlist.de-xuat.json` rồi chép; chạy khô mặc định; `--ap-dung` sao lưu (so byte) rồi chỉ thay `queries`; từ chối đề xuất bỏ/đổi tầng
  `moi_vao_pubmed`, thiếu cân ngoặc/nháy, tên chủ đề lạ/trùng.
- Bước ②b của `chu_trinh_chung_cu.py` (chỉ chế độ đầy đủ; `--nhanh` không gọi mạng).
- Đề xuất 10 chủ đề (tệp ở EBM-Dashboards, ngoài git): MeSH Major Topic + tiêu đề thay cụm dài; sản lượng 90 ngày sau đề xuất 66–1.108 (RA 2 → 1.017). Máy đã đọc mẫu tiêu đề từng truy vấn để soi độ đúng chủ đề
  và siết lại 2 chủ đề nhiễu (động mạch cảnh: «carotid»[ti] trơn kéo cả giải phẫu thú y/tai mũi họng; cấp cứu: «resuscitation»[ti] kéo cả ICU). «Cấp cứu ban đầu ngoại trú» có phạm vi mơ hồ — ghi rõ trong `_ly_do` để bác sĩ chốt.

**Chốt BH148** (`tools/chot_hoi_quy_bai_hoc.py`): phân loại MU/ON/KHONG_DO + mã thoát 2; đề xuất bỏ/đổi tầng bắt-cái-mới bị từ chối; chu trình đầy đủ GỌI chốt, `--nhanh` KHÔNG gọi, mã 1 ⇒ việc 🟠, mã 2 ⇒ ghi chú ⚪.
Kèm 46 ca pytest `tools/test_san_luong_giam_sat_20261002.py`. **Kiểm đột biến:** BH148 bắt 9/9 (chu trình không gọi · `--nhanh` gọi mạng · mã 1 không thành việc · mã 2 im lặng · lỗi mạng ⇒ 0 · bỏ bộ lọc thiết kế ·
bỏ bất biến moi_vao_pubmed · cho bỏ tầng · không đo được ⇒ mã 0/1); pytest bắt 12/12; phục hồi `cmp` đúng. Hai lỗi của chính bài test được sửa trong lúc viết (mô hình ngưỡng sai; tệp kết quả cũ thiếu khoá làm `in_bao_cao` sập —
nay `dung_lai_duoc` từ chối tệp thiếu khoá).

**Việc của bác sĩ.** Duyệt đề xuất (đọc `_ly_do`, xoá chủ đề không muốn đổi), rồi `python3 tools/ap_dung_de_xuat_watchlist.py` (chạy khô) → `--ap-dung`. Sau đó đo lại `python3 tools/kiem_san_luong_giam_sat.py`
và chạy một lượt quét thử trước khi tin vào các bài mới.
