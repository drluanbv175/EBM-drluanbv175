# 15/11/2026 — Bộ sinh in chuỗi chủ đề G0 (và mã đề tài) làm TÊN ĐỀ TÀI

**Bác sĩ (nguyên văn):** «… hãy tiếp tục đối với Xác Định Vấn Đề & Hình Thành Câu Hỏi Nghiên Cứu; … Hãy đảm bảo sự đồng bộ xuyên suốt và chính xác nhất» và «mỗi vấn đề xây dựng và hoàn thiện phải được cập nhật vào hệ thống».

## Phát hiện (đo trên C1a, chỉ đọc)

C1a đang mang hai tên đề tài:

| Tên | Nguồn | Văn bản dùng |
|---|---|---|
| Tên chính thức | `study_meta.title` | đề cương nộp, hồ sơ đạo đức (đã sửa tay) |
| Tên chủ đề | `study_meta.topic`: «… tại Khoa Khám bệnh theo yêu cầu, bệnh viện quân y tuyến cuối» — chuỗi để tìm y văn ở G0 | SAP đã ký, đề cương thống nhất G10, G3, G5, mục 10 «Scientific Title» của bản đăng ký WHO TRDS |

Chuẩn WHO TRDS đòi tên khoa học trùng tên đề cương.

**Nguyên nhân gốc:**
- `g2_quality_gate.who_trds_values` gán mục 10 = `topic`.
- Các bộ sinh `run_g2/g3/g4/g5/g6_auto` và `run_g10_assemble` in `topic` làm «Tên đề tài».
- `run_g2_auto` còn in **mã đề tài** (`study_name`) vào ô «Tên đề tài / Đề tài: … | Phiên bản». Chuỗi đầu–cuối giả lập bắt được lỗi này.

Phần câu hỏi ↔ mục tiêu ↔ giả thuyết của hai đề tài đều khớp:
- C1a: câu hỏi mô tả; MT2 phân tích có giả thuyết định trước.
- BTM: MT3 ghi rõ «thăm dò».

## Cách vá

**Repo y khoa:**
- `tools/ten_de_tai.py`:
  - `ten_chinh_thuc` = `study_meta.title`, chưa khai thì lùi về `topic`;
  - `ten_khoa_hoc_dang_ky` = `gate_params.G2.scientific_title`, nếu không có thì dùng tên chính thức.
- WHO TRDS mục 10 và mọi tiêu đề do máy sinh dùng tên chính thức. Ô tên không còn in mã đề tài; bản Word ghi «Mã đề tài».
- Hai trục mới trong `nhat_quan_xuyen_cong`:

| Trục | Lệch mềm khi | Cần xem khi |
|---|---|---|
| `ten_de_tai` | đề cương nộp, bản đăng ký hoặc hồ sơ đạo đức khác tên chính thức | văn bản đã ký hoặc do máy sinh khác tên; so bỏ qua dấu câu vì bộ trình bày G2 đổi «—» thành «,» |
| `cau_hoi_gia_thuyet` | câu hỏi phân tích thiếu H0/H1 | mục tiêu phân tích thiếu giả thuyết định trước hoặc chữ «thăm dò»; câu hỏi không phủ mục tiêu |

- Dữ liệu C1a: mục 10 của bản đăng ký nháp được sửa về tên chính thức. Trạng thái G2 không đổi (READY_FOR_IRB_SUBMISSION).

**Repo gốc:** dạy `cau-hoi-nghien-cuu`, `dao-duc-dang-ky`, `dieu-phoi-g0`.

## Kiểm hồi quy

- `tests/test_van_de_cau_hoi_20261115.py`: 13 ca; 14 đột biến đều đỏ.
- Chuỗi đầu–cuối G10 lộ ra fixture sai: G0 giả lập không có `topic`, nên G2 in mã đề tài làm tên. Đã sửa fixture (PI khai tên chính thức trước G2), không nới chốt.

## Giới hạn

SAP và đề cương thống nhất của C1a đã ký, vẫn mang tên chủ đề. Trục để ở mức «cần xem»; chỉ đổi ở lượt sửa đổi hoặc ký sau.
