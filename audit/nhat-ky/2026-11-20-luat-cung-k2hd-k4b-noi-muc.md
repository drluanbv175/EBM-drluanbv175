# 20/11/2026 — Luật cứng mới cho K2-hđ (ngưỡng trong hành động) và K4b (mâu thuẫn nội mục); K3b chưa có luật cứng đạt

## Bối cảnh

Số đo TEST 20/11 (`quality/eval/kiem-cheo-ngu-nghia/do-nhay-api-20261120-test.md`, mẫu ≤ 40 đột biến/lớp, chia DEV/TEST
theo MỤC — cách cũ): luật cứng K2-hđ 0% · K3b 0% · K4b 7%; kết hợp với API: K2-hđ 40% · K3b 12% · K4b 57%.
Bác sĩ giao: cải tiến LUẬT CỨNG (không gọi API) chỉ bằng trường có sẵn của mục; đo DEV (chia theo PMID) trước, TEST một lần
khi DEV cải thiện rõ; đo báo động trên mục gốc.

Đính chính tên lớp: trong mã, «K2-hđ» (`K2_nguong_hanh_dong`) là **đổi ngưỡng số nằm trong HÀNH ĐỘNG** (EF/eGFR/tuổi/HbA1c/BMI/
LDL đổi sang giá trị nguồn không nêu) — không phải «hiệu số gắn sai kết cục». K3b = cắt một cụm điều kiện («nếu…», «khi…»,
«ở người…», «chống chỉ định…», ngưỡng số) khỏi `action`. K4b = thêm «KHÔNG/Tránh/Không nên» vào đầu `action` của mục khẳng định.

## Hai luật mới (`tools/kiem_quan_the_chieu.py`, vẫn CHỈ CẢNH BÁO)

1. **K2 ngưỡng trong hành động** (`k2_nguong_hd`): ngưỡng trích từ `action` đối chiếu nguồn bằng đúng `kiem_nguong` của K1a
   (chỉ số có trong nguồn mà không thấy con số ấy trong ±60 ký tự ⇒ 🟠; nguồn không nhắc chỉ số ⇒ ⚪). Ngưỡng đã có ở quần thể
   thì bỏ (K1 đã phán). Đếm vào phép K2 (`phan_quyet_theo_phep`), mã thoát ④-ter như cũ.
2. **K4b nội mục** (`k4b_noi_muc`): `action` mở đầu phủ định thật, trong khi tiêu đề KHÔNG có dấu phủ định/thận trọng nào
   («không» mô tả quần thể như «không triệu chứng», «không dung nạp» không tính) VÀ `gradeSource` + `effectText` KHÔNG có dấu
   chống/hại nào (COR 3, mức D, có hại, chống chỉ định, tăng nguy cơ, tránh, ngừng, thu hồi…) ⇒ 🟠, báo cả khi nguồn có câu chống
   rộng (giữ phán quyết nguồn ở `muc_nguon`). Không phán khi thiếu cả `gradeSource` lẫn `effectText` (mục rút gọn — vd bộ vàng gọi
   `kiem_muc` với 6 trường ⇒ số bộ vàng KHÔNG đổi), tiêu đề trống hoặc `normativeBasis = contraindication`.

Bộ chấm `tools/do_nhay_kiem_ngu_nghia.py`: lớp K2-hđ chấm ở trường `k2_nguong_hd`, chuyển vào phạm vi (`trong_pham_vi=True`);
test cũ khẳng định «ngoài phạm vi» sửa theo đặc tả mới.

## Số đo (đột biến tổng hợp hạt giống 20261114; 49 nguồn trong bộ đệm; loại đột biến sinh từ mục phần B của bộ vàng)

DEV, chia theo PMID, MỌI đột biến có nguồn (bộ đo tạm gọi đúng `cham_k124`/`kiem_muc`, không gọi API):

| Lớp | Luật cũ | Luật mới |
|---|---|---|
| K2-hđ | 0/0 — DEV KHÔNG có đột biến lớp này | 0/0 |
| K3b | 1/61 | 1/61 |
| K4b | 12/85 (14%) | **46/85 (54%)** |
| Mục gốc có nguồn có ≥ 1 🟠 (mọi phép) | 3/89 (đều K1, có sẵn) | 3/89 (không thêm) |
| K4b nội mục trên MỌI mục gốc DEV (kể cả chưa có nguồn) | — | 0/411 (16 mục phủ định thật) |
| K2-hđ trên mục gốc DEV có ngưỡng trong hành động | — | 0 🟠 / 16 mục |

TEST — đo MỘT lần sau khi DEV cải thiện rõ (K4b):

| Lớp | Luật cũ | Luật mới |
|---|---|---|
| K2-hđ (mọi đột biến, chia PMID) | 0/20 | **20/20** — cả 20 từ MỘT bài (PMID 37139824), đều ngưỡng tuổi |
| K3b | 1/55 | 1/55 |
| K4b | 15/69 (22%) | **28/69 (41%)** |
| Mục gốc có nguồn có ≥ 1 🟠 | 3/73 (đều K4, có sẵn) | 3/73 (không thêm) |
| K4b nội mục trên MỌI mục gốc TEST | — | 0/371 (9 mục phủ định thật) |

Cùng mẫu với báo cáo 20/11 (chia theo MỤC, ≤ 40/lớp), API lấy từ BỘ ĐỆM — không gọi API
(`do-nhay-api-20261120d-test.md`): luật cứng K2-hđ 0% → **100%** (5/5; kết hợp 40% → **100%**), K3b 0% → 0% (kết hợp 14%),
K4b 7% → **54%** (7/13; kết hợp 57% → **69%**, 9/13); đối chứng luật cứng vẫn 0/37. Bộ đệm thiếu 5 lượt API so với lượt 20/11
⇒ n tính lệch 1 ở vài lớp (lượt thiếu bị loại khỏi mẫu số, không đoán).

## K3b: thử năm hướng, KHÔNG đưa luật nào vào (DEV, n = 61 đột biến có nguồn · 89 mục gốc)

| Hướng thử | Bắt | Mục gốc bị báo |
|---|---|---|
| Cụm điều kiện ở tiêu đề không còn trong hành động | 7 | 22 (25%) |
| Như trên, chỉ khi hành động không còn dấu điều kiện nào | 6 | 7 (8%) |
| Ngưỡng ở tiêu đề mà hành động không nhắc chỉ số | 1 | 4 |
| Cụm lặp ở ≥ 2 trường khác (tiêu đề/effectText/gradeSource/quần thể/pico) | 1 | 10 |
| Dấu điều kiện mạnh (chống chỉ định, thai kỳ, trừ khi…) ở ≥ 1 trường khác | 2 | 13 |
| Khái niệm của cụm vắng hẳn khỏi hành động (tiêu đề / + effectText) | 2–4 | 11–26 |

Nguyên nhân: 58/61 đột biến «lọt im» vì tóm tắt nguồn không có câu khuyến cáo CÓ ĐIỀU KIỆN cùng thuật ngữ (điều kiện thường chỉ
có ở toàn văn); trên 320 đột biến K3b DEV (kể cả chưa có nguồn) chỉ ~37% còn cụm ở trường khác của mục. Mọi hướng nội mục đều
báo nhiều mục gốc hơn số đột biến bắt được ⇒ trái nguyên tắc «thà im còn hơn báo động giả» của K3b. K3b cần toàn văn/API.

## Giới hạn nói trước

* **K4b nội mục chỉ bắt lỗi SỬA MỘT PHẦN** (hành động lệch với phần còn lại của mục). Đột biến tổng hợp đúng là kiểu đó ⇒ số đo
  LẠC QUAN hơn lỗi thật; mục sai đồng bộ ở mọi trường chỉ phép đối chiếu nguồn bắt được. Báo động giả 0/411 + 0/371 nhưng nền
  nhỏ (25 mục phủ định thật).
* **K2-hđ: DEV không có ca nào** (chia theo PMID, cả 20 rơi vào TEST) ⇒ luật thiết kế từ nguyên lý (cùng phép K1a đã đạt 100% ở
  quần thể), không tinh chỉnh trên dữ liệu; TEST 20/20 thực chất là MỘT bài — KTC Wilson trên n = 20 lạc quan giả.
* Từ vựng chỉ số dùng nguyên từ điển K1a (không mở rộng) — cách viết ngoài từ điển («PSTM», «độ lọc cầu thận»…) vẫn lọt.

## Sự cố trong lúc đo

Lượt đo TEST đầu báo K2-hđ 0/20 dù luật mới đã phán 🟠 cả 20: tệp đột biến của BỘ ĐO TẠM sinh bằng bộ sinh cũ (trường chấm
`k1_nguong`). Sinh lại bằng bộ sinh mới (tập đột biến trùng khớp 934/934, chỉ khác trường chấm) rồi đo lại — luật KHÔNG đổi giữa
hai lượt. Bài học: đổi trường chấm của bộ sinh thì phải sinh lại đột biến, không dùng lại tệp đột biến cũ.

## Kiểm hồi quy

`tools/test_luat_cung_k2hd_k4b_noi_muc_20261120.py` (11 test). Kiểm đột biến `python -B`, xoá `__pycache__` mỗi phép: 13/13 đột
biến đỏ đúng test (bỏ vòng `k2_nguong_hd`, bỏ khỏi phép K2, bỏ chống báo trùng, tắt hợp nhất nội mục, bỏ điều kiện thiếu trường,
bỏ loại «không» mô tả, bỏ «khuyến cáo … chống», bỏ «thu hồi/bị rút», bỏ «mức d», bỏ chặn `contraindication`, bộ chấm chỉ đọc
`k1_nguong`, chữ ký thiếu `nguong_hd`, bỏ `muc_nguon`), phục hồi xanh.

Ranh giới giữ nguyên: K1–K4 CHỈ CẢNH BÁO (không nâng chặn), không gắn nhãn bộ vàng, không sửa dashboard/`decision`/`gradeLevel`,
không gọi API. Cần bác sĩ kiểm chứng.
