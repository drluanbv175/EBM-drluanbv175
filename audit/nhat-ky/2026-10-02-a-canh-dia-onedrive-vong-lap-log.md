# 02/10/2026 — OneDrive SyncEngine kẹt vòng lặp log LẦN THỨ BA mà không có gì canh sớm (A, BH149)

**Triệu chứng.** Đo trực tiếp 02/10: thư mục log OneDrive ~20,7–24 GB, 24.796 tệp, ~54 tệp/phút, OneDrive 131% CPU và 4,7 GB RAM; đĩa 82% đầy. Đã xảy ra 21/08 và 17/09 (gốc: hộp thoại
«Remove files from OneDrive?» treo trong Sync Issues). Một dự báo «cạn đĩa 18:07» của agent là SAI (đĩa tự phục hồi lên 34–37 GiB) — nhưng vòng lặp là thật. Sau khi bác sĩ khởi động lại máy,
đo lại 18:04: log chỉ còn 11 tệp/1,6 MB, 0 tệp log mới trong 40 giây, đĩa trống 59 GiB; vẫn còn giảm ~1,3 MB/giây không kèm log mới (nghi đồng bộ sau khởi động, chưa chứng minh).

**Nguyên nhân gốc (chưa xử lý).** Hộp thoại Sync Issues của OneDrive — việc của bác sĩ (mở menu OneDrive → Sync Issues, KHÔNG Reset). Vòng lặp quay lại được vì không có gì canh: lần nào cũng phát hiện khi đã nặng.

**Vá (chỉ ĐO và BÁO — không xoá, không dừng tiến trình).**
- `tools/canh_dia_onedrive.py`: đo đĩa trống, tổng tệp/byte thư mục log OneDrive (macOS: `~/Library/Logs/OneDrive` + `FileProviderLogs`; Windows: `%LOCALAPPDATA%\Microsoft\OneDrive\logs`) và tốc độ giữa hai mẫu cách 2 phút–3 giờ.
  🔴 đĩa <10 GiB · log >8 GiB · log +150 MB/phút hoặc +30 tệp/phút · đĩa cạn <2 giờ; 🟡 đĩa <20 GiB · log >1 GiB · đĩa giảm ≥150 MB/phút (có thể chỉ là đồng bộ); không đọc được đĩa ⇒ ⚪ KHÔNG ĐO ĐƯỢC (mã 3);
  không thấy thư mục log ⇒ 🟡 (không biết có vòng lặp hay không); đếm tệp quá hạn ⇒ 🟡 «cận dưới». Một mẫu đơn lẻ không chứng minh vòng lặp.
- Hook SessionStart gọi `--im-khi-on` (im lặng khi 🟢). `--thong-bao`: thông báo hệ thống macOS khi 🔴, chống lặp 60 phút. `--cai-launchd`: agent chạy mỗi 5 phút (chạy khô mặc định; `--ap-dung` cài, `--go-launchd --ap-dung` gỡ) —
  cài đặt agent nền là việc của bác sĩ.

**Đo thật sau vá.** Hai mẫu cách ~2 phút trên máy này: 🟢 trống 54 GiB, log 26→36 MB, 143→153 tệp (5 tệp/phút).

**Chốt BH149** + 37 ca pytest `tools/test_canh_dia_onedrive.py`. BH149 kiểm HÀNH VI hàm thuần `phan_loai` trên đúng ca đo 02/10 (log 24 GB/24.796 tệp ⇒ 🔴; +54 tệp/phút ⇒ 🔴; đĩa 9 GiB ⇒ 🔴; không đọc được đĩa ⇒ KHÔNG_ĐO;
không thấy thư mục log ⇒ 🟡; không suy tốc độ từ hai mẫu cách <2 phút), mã nguồn không có lệnh xoá/giết tiến trình (ast), và bản khai hook có gọi công cụ đúng một lần. **Kiểm đột biến:** BH149 bắt 7/7 (không đo được ⇒ xanh · suy tốc độ từ mẫu quá gần ·
log 24 GB không đỏ · ngưỡng đĩa lỏng · không thấy log ⇒ xanh · thêm lệnh xoá · hook không gọi); pytest bắt 10/10; phục hồi `cmp` đúng.

**Việc của bác sĩ.** (1) Xử lý gốc ở Sync Issues. (2) Sau khi merge: `python3 tools/dong_bo_hook_sessionstart.py --ap-dung` (nhận hook mới; cùng lệnh với HV-01/#84). (3) Tuỳ chọn:
`python3 tools/canh_dia_onedrive.py --cai-launchd` (chạy khô) rồi `--ap-dung` để canh nền khi không mở phiên.
