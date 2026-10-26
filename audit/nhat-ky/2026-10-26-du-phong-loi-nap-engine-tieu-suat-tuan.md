# 26/10/2026 — Làn dự phòng tính phí trừ suất tuần khi engine KHÔNG NẠP ĐƯỢC (chạy bằng python3 hệ thống)

**Phát hiện.** Theo gợi ý của `tools/tu_de_xuat_viec.py` («`python3 ops/orchestrator.py --cu-nhat 3 --online`»), lượt
orchestrator 26/10 chạy bộ quét bằng python3 HỆ THỐNG. Phiếu A2 chủ đề «Viêm phổi cộng đồng (CAP)» ghi `làn
du_phong_bac_thang lỗi: ModuleNotFoundError` và «suất tuần đã tính»; sổ `EBM-Dashboards/.du-phong-trang-thai.json` ghi
`lan_cuoi_leo_thang` + `leo_thang_loi` cho CAP ngày 26/10 — 1/2 suất tuần W44 bị trừ với 0 lời gọi nguồn tính phí.

**Nguyên nhân.** `bo_sung_du_phong_lane()` nạp `app.sources.base`/`app.services.fallback_ladder` của engine; dưới python3
hệ thống (thiếu thư viện) lệnh nạp ném ModuleNotFoundError TRƯỚC mọi lời gọi. Nơi gọi bắt mọi ngoại lệ thành «lần gọi LỖI»
(không biết đã tới nguồn chưa ⇒ tính suất, cho thử lại). Luật 30/09 (BH117): nguồn KHÔNG được gọi — engine vắng · cờ tắt —
thì không tiêu suất; engine không nạp được thuộc nhóm đó.

**Cách vá.** Lỗi `ImportError` khi nạp engine ⇒ `KetQuaDuPhong([], "", 0, ly_do_khong_goi=…)` («chắc chắn không gọi»): không
ghi mốc xoay vòng, không dấu lỗi, ghi chú chủ đề nêu lý do kèm «chạy bằng ~/.ebm-venv/bin/python». Lệnh gợi ý ở
`tu_de_xuat_viec.py` và `kiem_do_tuoi_chung_cu.py` đổi sang `~/.ebm-venv/bin/python ops/orchestrator.py …`. Bộ ba bộ quét đồng
bộ (bản `dark-analyst` trước vá trùng hệt nguồn chuẩn — đã đối chiếu `cmp`). Suất CAP đã trừ hôm nay không sửa tay sổ: chạy lại
A2 cho CAP trong tuần dùng đúng lượt thử lại của chính suất đó (không đốt suất mới).

**Kiểm hồi quy.** `tools/test_surveillance_scan_du_phong_loi_nap_engine_20261026.py` (5 ca: base thiếu thư viện · bậc thang
thiếu thư viện · hàm tiêm sẵn vẫn chạy · KetQuaDuPhong cũ · toàn lượt không tiêu suất + ghi lý do). 4 đột biến đều đỏ đúng chỗ
rồi xanh lại; bộ test bộ quét 216 đạt; bộ chốt bài học không tái phát.
