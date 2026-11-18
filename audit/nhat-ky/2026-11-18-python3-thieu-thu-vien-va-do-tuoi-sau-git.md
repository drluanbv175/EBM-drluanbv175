# 18/11/2026 — python3 hệ thống thiếu thư viện làm sai kết quả chấm cổng; thao tác git làm độ tươi báo «cũ» giả

## Bối cảnh

Bác sĩ hỏi hệ nghiên cứu đã hoàn thiện chưa. Đo sống trên checkout chính bằng `python3 tools/...` (đúng như mọi lệnh trong
tài liệu) cho kết quả sai, rồi chính bước dọn sau phép đo gây thêm cảnh báo giả. Bác sĩ giao sửa cả hai
(PR y khoa drluanbv175/medical-ebm-automation#316).

## Lỗi 1 — python3 hệ thống thiếu 11/13 thư viện chuỗi cổng

- **Đo 18/11:** `python3` của Mac (3.14 hệ thống) thiếu defusedxml, cryptography, numpy, pandas, scipy, statsmodels,
  dotenv, fontTools, lifelines, matplotlib, openpyxl; `~/.ebm-venv` có đủ.
- **Hậu quả:**
  - G0-AUTO-08 không nạp được từ điển VI→EN, nên G0 của hai đề tài thật bị chấm vàng dù đã `PASS`;
  - 7 cổng C1a ra «không đo được» trong `hoi_dong_cong.py trach-nhiem`;
  - bộ chấm ghi trạng thái hạ cấp vào checkpoint (G0_checkpoint, G2_checkpoint).
- **Đã sửa:** `tools/moi_truong_venv.py`, gọi ở `__main__` của 32 điểm vào chuỗi cổng.
  - Thiếu thư viện và có venv ⇒ tự chạy lại bằng venv.
  - Không chuyển được ⇒ mã 2, không ghi gì, và chỉ chặn khi script thật sự cần thư viện thiếu.
  - Test đo cây import, nên thêm thư viện mới mà quên khai thì test đỏ.

## Lỗi 2 — git ghi lại tệp làm mọi cổng sau bị báo «cũ»

- **Đo 18/11:** trả các checkpoint bộ chấm vừa ghi đè bằng `git checkout --` đặt mtime về «bây giờ».
  - C1a: G1/G3/G4 bị báo «cũ», G10-AUTO-03 chặn, dù nội dung không đổi một byte.
  - `git pull` cũng gây cùng hiện tượng.
- **Đã sửa:** `pipeline_freshness` đối chiếu git. Chỉ gỡ cảnh báo khi đủ ba bằng chứng:
  1. cả hai tệp sạch và được theo dõi;
  2. mtime thượng nguồn muộn hơn giờ commit của chính nó;
  3. thượng nguồn trùng từng byte với bản ở commit cuối của cổng sau.

  Không bao giờ thêm «tươi»; cặp được gỡ hiện ở `cuu_theo_git`. Đột biến 14/14 đỏ.
- **Đo lại:** C1a còn đúng cảnh báo thật như báo cáo 09:50 (G5 cũ). BTM G1–G4 vẫn cũ, và đó là cảnh báo thật: tên đề
  tài trong G0 đổi ở #313 sau khi G1–G4 được ghi.

## Bài học

- Đo cổng trên checkout chính: dùng `--no-write` nếu bộ chấm có cờ đó, hoặc đo trong worktree. Không chạy bộ chấm có ghi
  rồi «dọn» bằng `git checkout --`: nội dung về đúng nhưng mtime đổi, phép đo độ tươi bị nhiễu (#316 nay nhận ra trường
  hợp này).
- Chỉnh mtime để khôi phục kết quả một phép kiểm là sửa đầu vào của giám sát. Lệnh `touch` của agent bị chặn; đúng
  cách là trình bằng chứng để bác sĩ quyết. Mốc agent đề xuất (giờ sinh ghi trong tệp) có thể sai so với mtime gốc
  (C1a G2: đề xuất 16:04, gốc nhiều khả năng 17:16:29 lúc git ghi G3/G4/G10).
- Checkout repo gốc tự kéo `master` (13:13) không sinh lại bản sao Codex ⇒ pre-commit repo y khoa báo «Agent sync check:
  FAIL». Chữa: `python3 tools/sync_agents_to_codex.py` (chỉ ghi tệp sinh, ngoài git).
