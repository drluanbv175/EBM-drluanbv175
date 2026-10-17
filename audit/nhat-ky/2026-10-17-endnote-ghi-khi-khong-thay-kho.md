# 17/10/2026 — EndNote: chạy từ worktree với --file thì không thấy kho toàn văn, --ap-dung sẽ ghi «chưa xét» đè cả thư viện

**Phát hiện:** khi đo bản vá kho tóm tắt máy (PR #189), chạy `nap_endnote_chu_de.py` từ một worktree
(`~/.ebm-worktrees/<x>`), với `--file` trỏ tới dashboard thật và `--tom-tat-vi` (chạy khô), báo «sẽ ghi 877 · không đổi 0».
Cùng lệnh thêm `--kho-toan-van <EBM-Dashboards>/toan_van_oa` thì báo «sẽ ghi 0 · không đổi 877».

**Nguyên nhân:**
- `main()` chỉ suy kho từ `EBM-Dashboards/` của CÂY ĐANG CHẠY (`ban_sao_tran.duong_goc`). Ở worktree hoặc bản sao trần thư mục
  đó không có ⇒ `kho = None` ⇒ `tom_tat_endnote_vi` dựng dòng «Toàn văn: chưa xét (không thấy kho)» cho MỌI bản ghi.
- Thêm `--ap-dung` là ghi đè dòng «Toàn văn: có PDF … · có bản đọc sâu» của cả thư viện bằng thông tin kém hơn. Đường nạp
  `--ap-dung` thường cũng gọi bước tóm tắt nên dính cùng lỗi.
- `--tat-ca` đã tự chặn («không thấy thư mục EBM-Dashboards/»). Bước ⑧ của `xuat_goi_cap_nhat.py` an toàn vì đã truyền
  `--kho-toan-van` cạnh dashboard (TT-07, 15/10). Lỗ hổng chỉ ở lệnh gọi TAY với `--file`.
- Chưa có bản ghi nào bị ảnh hưởng: mọi lượt ghi thật tới 17/10 đều chạy từ cây chính.

**Cách vá (`tools/nap_endnote_chu_de.py`):**
- `xac_dinh_kho()` suy kho theo thứ tự:
  1. `--kho-toan-van` — giữ nguyên kể cả khi sai đường, không lặng lẽ đổi;
  2. `toan_van_oa` CẠNH dashboard của `--file` — cùng cách bước ⑧ và cổng BH161; dashboard ở nhiều thư mục có nhiều kho ⇒ mơ
     hồ, không chọn bừa;
  3. `EBM-Dashboards/toan_van_oa` của cây đang chạy.
- `chan_ghi_khi_thieu_kho()` — fail-closed khi GHI. Không có kho thật mà `--ap-dung` sẽ ghi khối ĐỌC NHANH ⇒ ⚪ «KHÔNG ĐO ĐƯỢC»,
  mã 2, không ghi gì.
  - Thứ tự xét: SAU kiểm nền tảng/cấu hình (máy không ghi được EndNote thì luật cũ — ⚪/mã 0 trong bộ năm — vẫn thắng), TRƯỚC
    bước có thể bật EndNote lên màn hình.
  - Không áp cho: chạy khô (in ⚠), `--ap-dung --khong-tom-tat` (chỉ nhập bản ghi), `--gan-kho`, `--xuat-xml`.
- Tách `_tim_dash_goc()` để test kín, không phụ thuộc cây đang đứng.
- Fixture `_dash` của `test_endnote_da_nen_cau_hinh_20261015.py` nay dựng kho cạnh dashboard đúng bố cục thật — sửa fixture,
  không nới assertion.

**Kiểm hồi quy:**
- `tools/test_endnote_chan_ghi_khong_kho_20261017.py` — 10 test.
- 10 phép đột biến đều đỏ đúng test rồi phục hồi xanh:
  - bỏ gọi chốt; chốt chặn cả `--khong-tom-tat`;
  - bỏ suy kho cạnh dashboard; chọn bừa khi nhiều kho;
  - kho chỉ rõ sai thì lặng lẽ đổi; chốt không xét `is_dir`;
  - đụng EndNote trước khi chặn; chốt chạy trước kiểm nền tảng;
  - bỏ cảnh báo chạy khô; kho gốc đứng trước kho cạnh.
- Đo thật (chạy khô từ worktree, `--file` dashboard thật, KHÔNG `--kho-toan-van`):
  - mã cũ: «sẽ ghi 877 · không đổi 0»;
  - mã mới: «sẽ ghi 0 · không đổi 877».
