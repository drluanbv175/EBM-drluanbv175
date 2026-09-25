# 16 · Thiết kế kiểm chéo ngữ nghĩa cho mục `decision:'apply'` (25/09/2026) — [DỰ THẢO, CHỜ BÁC SĨ DUYỆT HƯỚNG]

> Đề xuất #7 trong đợt «đo lại nguồn chứng cứ» 24–25/09/2026. Tài liệu này là **thiết kế**, chưa có mã.
> Mọi ngưỡng/từ điển dưới đây là đề xuất của máy — cần bác sĩ duyệt trước khi thi công.

## 1. Khoảng trống cần đóng

Các cổng hiện có kiểm **hình thức** và **nguồn có thật** (PMID tồn tại, tiêu đề khớp, chưa bị rút, hiệu số
HR có trong tóm tắt — `tools/kiem_so_lieu.py`). Chúng **không kiểm nội dung có đúng không**:

| Loại sai | Ví dụ | Cổng hiện tại |
|---|---|---|
| Sai quần thể | Mục ghi «HFpEF» nhưng trích thử nghiệm chỉ HFrEF; ghi «eGFR ≥ 20» trong khi nguồn là ≥ 25 | Không bắt (`pico.P:'match'` là lời NGƯỜI SOẠN tự khai) |
| Rụng mệnh đề điều kiện | DATA ghi «nếu không có chống chỉ định», bản đọc/Word/tin chat mất vế này | Không bắt |
| Sai chiều khuyến cáo | `apply` trên nguồn nói «not recommended» / Class III | Không bắt (chỉ kiểm `gradeLevel`) |
| Sai con số ngoài HR | Cỡ mẫu, ngưỡng tuổi/eGFR/EF/HbA1c | Chỉ HR/CI được kiểm |

## 2. Bốn phép kiểm đề xuất (đều CHỈ BÁO, không đổi `decision`)

Cùng triết lý `kiem_so_lieu.py`: ba mức **✓ khớp · 🟠 cần đọc lại · ⚪ nguồn không nêu (chưa kiểm được)** —
cố ý KHÔNG có mức «SAI», vì vắng mặt trong tóm tắt không chứng minh trích sai (BH08).

- **K1 — Quần thể.** Trích từ `population` + `pico.P` các ngưỡng số (EF, eGFR, tuổi, HbA1c, BMI, LDL…)
  và nhãn quần thể; đối chiếu với tiêu đề + tóm tắt nguồn (PubMed efetch). Thêm bảng **cặp loại trừ nhau**
  (HFrEF↔HFpEF · típ 1↔típ 2 · người lớn↔trẻ em · thai kỳ↔ngoài thai kỳ · CKD lọc máu↔không lọc máu):
  mục mang một vế mà nguồn chỉ nêu vế kia ⇒ 🟠.
- **K2 — Con số mở rộng.** Mở rộng `kiem_so_lieu.py` sang ngưỡng của K1 và cỡ mẫu `n=` ghi trong mục.
- **K3 — Bảo toàn mệnh đề điều kiện (NGOẠI TUYẾN, rẻ nhất, giá trị ngay).** Trích từ `action`/`summary`/
  `dontDo` các cụm điều kiện («nếu…», «trừ khi…», «khi eGFR…», «ngoài thai kỳ», «không dùng khi…») rồi
  kiểm từng cụm có còn trong **bộ năm** (bản đọc, Word HTML) và bản tin chat. Không cần mạng.
- **K4 — Chiều khuyến cáo.** `apply` mà tóm tắt/tiêu đề nguồn có tín hiệu ngược chiều («not recommended»,
  «no benefit», «harm», «Class III», «should not») ⇒ 🟠 kèm câu nguyên văn để bác sĩ đọc.

## 3. Nối vào dây chuyền

- Công cụ mới `tools/kiem_cheo_ngu_nghia.py` (repo gốc), đọc khối `DATA`, chạy K1–K4, in bảng + JSON.
- Gọi ở bước ①-ter của `tools/xuat_goi_cap_nhat.py`, **mức CẢNH BÁO** (không đổi mã thoát) — in vào
  bản đọc như dải vàng «Cần đọc lại N mục» cạnh dải đỏ/cam hiện có.
- Chỉ chuyển sang CHẶN khi bác sĩ duyệt, sau khi đo tỉ lệ báo động giả trên bộ vàng (mục 4).
- Dạy agent cùng lúc (luật §6.4): `tham-dinh-dau-ra` thêm R1d; `trich-xuat-y-van` gọi K1/K2.

## 4. Cách đo trước khi tin (bắt buộc)

Bộ vàng ~20 mục `apply` thật lấy từ các dashboard hiện có, **bác sĩ gắn nhãn tay** (đúng quần thể/đúng
chiều/đủ điều kiện hay không). Chạy K1–K4, đo: số 🟠 trên mục bác sĩ nói «đúng» (báo động giả) và số mục
bác sĩ nói «sai» mà công cụ bỏ lọt. Báo động giả cao ⇒ giữ mức cảnh báo, không chặn (bức tường đỏ giả làm
người ta bỏ qua cả cảnh báo thật).

## 5. Giới hạn nói trước

- Chỉ đọc **tóm tắt** (toàn văn có bản quyền) ⇒ ⚪ sẽ nhiều; ⚪ ≠ sai.
- Khớp từ vựng không hiểu phủ định phức tạp và đồng nghĩa hiếm; K4 chỉ bắt tín hiệu ngược chiều rõ ràng.
- Không thay việc bác sĩ đọc nguồn gốc; mục tiêu là **chỉ ra mục đáng đọc lại**, không phán quyết.

## 6. Bác sĩ cần quyết

1. Thi công phép nào trước — máy đề xuất **K3** (ngoại tuyến, rẻ, chống đúng lỗi «rụng điều kiện» của kênh
   chat) rồi **K1**.
2. Giữ mức CẢNH BÁO vĩnh viễn hay cho phép chặn sau khi đo bộ vàng.
3. Chọn ~20 mục `apply` cho bộ vàng và gắn nhãn (máy có thể soạn danh sách ứng viên để bác sĩ chọn).

_Cần bác sĩ kiểm chứng._
