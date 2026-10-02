# 03/10/2026 — Phép đo làm bẩn cây git khi không có gì mới: gương cloud và sổ nguồn (HV-13 · N11 · PM-14, BH153)

**Số đo (kiểm toàn diện 02/10).**
- **Gương cloud.** `cloud-mirror/trang-thai-chung-cu.json`: 27 commit «chore» / 30 ngày. Diff chỉ gồm `sinh_luc` và các số tự trôi
  theo lịch: «trung vị 92 → 94 ngày», «(115ng) → (117ng)», ngày in trong tiêu đề bảng, «N file chưa commit» — chính tệp gương là tệp
  chưa commit đó. Hook SessionStart chạy bộ sinh mỗi phiên, nên mỗi phiên lại sinh một «việc» giả.
- **Sổ nguồn.** `data/sources.json`: 34 commit / 30 ngày. Mỗi lượt `sources_health.py` trên máy thật viết lại sổ tracked chỉ để đổi
  `updated` + các `last_probe_at` (02/10: 16 dòng diff, toàn dấu ngày). Hai máy ghi cùng một dòng, cây làm việc bẩn sau một phép ĐO.

**Vá.**
- **`xuat_trang_thai_cloud.py`.** So CHỮ KÝ ỔN ĐỊNH, tức bỏ `sinh_luc` và che các token thời gian:
  - Bị che: ngày ISO; dd/mm/yyyy; dd/mm chỉ khi kèm giờ; giờ; số đứng trước «ngày»/«ng»; «N file chưa commit».
  - Chữ ký trùng và gương < 7 ngày tuổi ⇒ KHÔNG ghi.
  - Thử lần đầu đã che nhầm «0/4 cổng cứng» thành ngày; phép thử bắt được, mẫu dd/mm được hẹp lại. Số đếm THẬT («0/4 → 1/4 cổng
    cứng», «17/17 → 16/17 giác quan», số chủ đề, số quyết định, mã thoát) vẫn làm gương đổi ngay.
  - `--ep-ghi`: bước ⑥ của `xuat_goi_cap_nhat.py` (vừa cập nhật chứng cứ) luôn ghi.
- **`sources_health.py`.** Sổ tracked chỉ ghi khi NỘI DUNG đổi, tức `chu_ky_so` khác nhau sau khi bỏ `updated`/`last_probe_at`.
  - Dấu thăm sống luôn ghi vào `state/tham-song-nguon.json` (ngoài git).
  - Sổ bị trỏ đi nơi khác (test, BH50) thì dấu thăm nằm cạnh sổ đó, không rơi vào `state/` của repo.
  - Hai test cũ dùng «sổ tracked đã bị viết lại» làm dấu hiệu nhánh máy thật. Nay chúng kiểm sổ dấu thăm và kiểm sổ tracked GIỮ
    NGUYÊN. Hành vi đổi có chủ ý; assertion về nhãn `active` giữ nguyên.

**Kiểm.**
- 6 test mới, 2 test cập nhật, 2 test mới cho sổ nguồn.
- 6 đột biến đều bị bắt (sau khi sửa lỗi của chính runner: truyền ba tệp test thành MỘT chuỗi ⇒ pytest «no tests ran» ⇒ báo «bắt»
  giả); BH153 tự bắt cả hai đột biến chính.
- Đo SỐNG trên dữ liệu thật (symlink tạm, đã gỡ):
  - Lượt 1 ghi sổ vì nội dung đổi THẬT (`last_success_at` SRC-004: 27/09 → 02/10).
  - Lượt 2 ngay sau đó: băm SHA-256 sổ trước = sau, in «≡ … KHÔNG ghi sổ tracked».
- BH50 ✓ trên dữ liệu thật. `pytest tools/` xanh; `kiem_tuong_thich_da_nen` 🔴 0.
