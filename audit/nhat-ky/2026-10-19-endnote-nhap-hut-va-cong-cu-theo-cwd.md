# 19/10/2026 — EndNote ⑧ báo «nhập mới 17» mà thư viện không có bài; build_library/make_derivatives ghi theo thư mục đang đứng

**Mã:** BH165 · **Bối cảnh:** xuất gói chứng cứ «Tăng huyết áp ngoại trú» (`WebDashboard_EBM_VanDeCuThe_TangHuyetAp_NgoaiTru_20261019.html`)
bằng `python3 tools/xuat_goi_cap_nhat.py <dashboard> --online` — bộ năm 5/5, cổng PASS.

## Hai lỗi, cùng họ BH17 (tuyên bố không điều kiện)

1. **Bước ⑧ EndNote báo số DỰ ĐỊNH như số đã nhập.** `nap_endnote_chu_de.py` in «17 trích dẫn · đã có 0 · nhập mới 17
   (đính PDF 4…)» rồi «Đăng thêm vào nhóm: 0 · nhóm hiện có 0 bản ghi». Đo lại chỉ-đọc ngay sau đó (`EndNoteMac.tim_khop`
   theo `Accession Number` và `DOI`): 0/17 bản ghi, không có nhóm «EBM · Tăng huyết áp ngoại trú…». AppleScript
   `import x into document` trả về KHÔNG lỗi. Lúc đó EndNote 2025 đang mở 3 cửa sổ: thư viện, «Libraries Preferences»,
   «EndNote™ Preferences» — nghi cửa sổ Preferences làm lệnh nhập im lặng (chưa tái hiện có chủ đích). Mã thoát vẫn 0 nên
   bộ xuất không cảnh báo gì; 4 thư mục PDF vừa đặt vào `.Data/PDF/` thành mồ côi.
2. **`build_library.py add` và `make_derivatives.py` ghi theo `os.getcwd()`.** Chạy từ gốc repo:
   `build_library.py add EBM-Dashboards/<dashboard>.html` nối vào một `library.json` CŨ ở gốc (4 → 5 bản; liên kết tương đối
   trong trang chỉ mục không mở được dashboard) thay vì thư viện chuẩn `EBM-Dashboards/` (74 bản); `make_derivatives.py`
   tạo thư mục `derivatives/` ở gốc, tách khỏi bộ năm trong `EBM-Dashboards/derivatives/`. Đã dọn tay cùng ngày: hoàn
   nguyên thư viện gốc về 4 bản, thêm vào thư viện chuẩn (75 bản), dời 3 tệp phái sinh, gỡ thư mục nhầm.

## Cách vá

- `nap_endnote_chu_de.py`: `tra_ban_ghi_sau_nhap()` tra lại thư viện SAU lệnh nhập (lặp ≤ `CHO_NHAP_GIAY` = 10 lượt × 1
  giây phòng EndNote ghi chậm); báo `nhap_thuc`/`nhap_hut`; dòng báo cáo in «nhập mới X/Y (đếm lại trong thư viện sau
  nhập)» và «🔴 NHẬP HỤT …» kèm tên cửa sổ EndNote đang mở (`EndNoteMac.ten_cua_so()`, chỉ đọc); dọn PDF vừa đặt cho bài
  hụt; `ma_thoat_nap()` ⇒ mã 2 khi nhập hụt (bộ xuất in «⚠ EndNote chưa nạp được»; không đổi mã thoát bộ năm).
- `build_library.py`: `add` lấy thư mục của CHÍNH dashboard (dashboard ở nhiều thư mục ⇒ từ chối, đòi `--thu-vien`); `build`
  không dựng thư viện rỗng khi thiếu `library.json`. `make_derivatives.py`: `--outdir` mặc định = `derivatives/` CẠNH
  dashboard. Sửa nguồn `sync/skills/cap-nhat-chung-cu-y-khoa/tools/` + bản trùng `sync/skills/dark-analyst/tools/`.

## Kiểm hồi quy

- Test: 5 test mới trong `tools/test_nap_endnote_chu_de_20261011.py` (46/46) và `tools/test_duong_dan_neo_dashboard_20261019.py`
  (8/8, chạy công cụ bằng tiến trình con từ cwd khác, cả hai bản skill).
- Đột biến (§0.8): 5 đột biến ⑧ (bỏ phát hiện hụt · in số dự định · mã thoát bỏ hụt · bỏ dọn PDF · không tra lại) và 3 đột
  biến đường dẫn (add theo cwd · build thư viện rỗng · derivatives theo cwd) — tất cả làm test đỏ, phục hồi xanh.
- Chốt **BH165** gọi thật `nap_chu_de` với EndNote giả có lệnh nhập im lặng và chạy hai công cụ từ cwd khác; đỏ với 3 đột biến
  then chốt.

## Việc còn lại sau khi gộp

- BH11 đòi 3 bản khớp md5: chép nguồn `sync/skills/cap-nhat-chung-cu-y-khoa/tools/{build_library,make_derivatives}.py`
  sang `EBM-Dashboards/tools/` và `EBM_MASTER/skill_assets/` (runtime không có dòng riêng — đã so 19/10, ba bản trùng byte).
- Nạp lại 17 trích dẫn gói THA vào EndNote sau khi bác sĩ đóng cửa sổ Preferences:
  `python3 tools/nap_endnote_chu_de.py --file EBM-Dashboards/WebDashboard_EBM_VanDeCuThe_TangHuyetAp_NgoaiTru_20261019.html --ap-dung`.
