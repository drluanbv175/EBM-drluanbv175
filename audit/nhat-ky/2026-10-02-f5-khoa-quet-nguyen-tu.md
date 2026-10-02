# 02/10/2026 — F5: khoá `.quet.lock` của bộ quét giám sát không nguyên tử — nhiều tiến trình cùng «giành được» (không cấp BH mới; chốt bằng test tiến trình thật)

**Triệu chứng (đo 02/10/2026, Mac, Python của `~/.ebm-venv`).** `gianh_khoa()` trong `surveillance_scan.py` làm «kiểm rồi
mới ghi»: `kp.exists()` → đọc → `kp.write_text(...)`. Đo ở kiểm toàn diện: 10 tiến trình cùng giành một mốc thời gian,
10 vòng ⇒ **10/10 vòng có > 1 tiến trình cùng «giành được»** (5–10 tiến trình/vòng). Hệ quả khi xảy ra thật (tác vụ lịch
tuần + một lượt chạy tay, hoặc hai lượt `ops/orchestrator.py`): hai lượt quét cùng ghi con trỏ `.quet-cursor.json` và sổ
dự phòng tính phí — đúng loại hỏng mà khoá sinh ra để chặn (K3/I7).

**Thử vá thứ nhất chưa đủ — đo lại mới thấy.** Chỉ đổi sang `os.open(O_CREAT | O_EXCL)` làm ca thư mục trống đạt (đúng 1
tiến trình/vòng), nhưng ca **đã có khoá MỒ CÔI** (khoá cũ 2 giờ) vẫn hở: 8 tiến trình, 8 vòng ⇒ **2–5 tiến trình/vòng** cùng
thay khoá. Hai đường hở: (a) tiến trình đến sau đã đọc khoá mồ côi, rồi gỡ NHẦM khoá mới của tiến trình đến trước; (b) khoá
vừa tạo bằng `O_EXCL` còn RỖNG trong lúc ghi ⇒ tiến trình khác đọc thấy «hỏng định dạng» ⇒ coi là mồ côi ⇒ gỡ. Bổ sung
«đọc lại ngay trước khi gỡ» vẫn hở vì đường (b).

**Vá (2 bản `surveillance_scan.py` trong git, đồng bộ byte).**
- `_mutex_khoa(kp)`: khoá loại trừ CẤP HỆ ĐIỀU HÀNH (`fcntl.flock` trên macOS/Linux, `msvcrt.locking` trên Windows) trên tệp
  `.quet.lock.mutex` cạnh tệp khoá — tự nhả khi tiến trình chết nên không bao giờ mồ côi. Đặt cạnh tệp khoá, KHÔNG ở thư mục
  tạm: `TMPDIR` khác nhau giữa tác vụ lịch và phiên tay sẽ làm mỗi bên một mutex riêng.
- `_gianh_trong_mutex()`: cả thủ tục đọc → (mồ côi/hỏng thì) gỡ → tạo `O_EXCL` → ghi chạy TRONG mutex. `O_EXCL` giữ lại để
  phòng bản cũ chưa vá (bản runtime `EBM-Dashboards/tools/` trước khi đồng bộ) chạy song song.
- Không khoá được vùng găng (Windows `LK_LOCK` hết 10 lần thử, thư mục chỉ đọc…) ⇒ `gianh_khoa()` trả `False` kèm lý do —
  fail-closed, caller đã FAIL RÕ RÀNG như cũ.
- Ngữ nghĩa giữ nguyên: khoá tươi (< 30 phút) ⇒ không chạy chồng; khoá cũ/hỏng định dạng ⇒ mồ côi, được thay. Giữa HAI MÁY
  vẫn chỉ dựa vào OneDrive đồng bộ tệp khoá — giới hạn cũ, không đổi.

**Kiểm.**
- `tools/test_khoa_quet_nguyen_tu_20261002.py` (7 ca, ~12 giây). Ca chính chạy 6 tiến trình Python THẬT × 3 vòng, cùng đợi
  một mốc, ở hai ca: thư mục trống và có khoá mồ côi sẵn. Mỗi vòng phải đúng 1 tiến trình giành được. Còn có các ca: khoá tươi,
  khoá mồ côi, khoá hỏng, nhả rồi giành lại. Thêm một chốt trên CÂY CÚ PHÁP: có `O_EXCL`, có `with _mutex_khoa(kp)`, không có
  `write_text`. Chốt này không khớp chuỗi cả tệp, vì docstring có nhắc «O_EXCL» nên khớp chuỗi sẽ xanh giả.
- Đột biến (sao lưu + `cmp` trước, phục hồi + `cmp` sau):
  - Bỏ mutex ⇒ ca mồ côi đỏ `[4, 3, 4]`.
  - Trả về bản HEAD ⇒ hai ca tiến trình đỏ: thư mục trống `[6, 5, 6]`, có khoá mồ côi `[3, 4, 4]`.
  - Phục hồi ⇒ 7/7 xanh.
- `python -B -m pytest tools/`: 2068 đạt / 32 bỏ qua.
- `python -B tools/chot_hoi_quy_bai_hoc.py`: 🟢 (bản sao trần, 39 mục ⚪ — ⚪ không phải ĐẠT).
- `tools/kiem_tuong_thich_da_nen.py`: 🔴 0. Hai 🟡 có sẵn từ trước, không thuộc tệp của PR này.
- `ruff`: sạch.

**Chưa kiểm.** Nhánh `msvcrt` chưa chạy trên Windows thật trong phiên này (máy Mac) — CI đa nền tảng và lượt quét đầu tiên trên
máy Windows sau khi gộp là phép đo thật. Bản runtime `EBM-Dashboards/tools/surveillance_scan.py` (ngoài git) chỉ nhận bản vá sau
khi gộp + `python3 tools/dong_bo_scanner_giam_sat.py` (tự sửa chữa chạy mỗi phiên). Tệp `.quet.lock.mutex` rỗng sẽ xuất hiện
cạnh `.quet.lock` (thư mục `EBM-Dashboards/`, ngoài git) và được OneDrive đồng bộ — vô hại (nội dung rỗng, khoá hệ điều hành không đi qua đồng bộ).
