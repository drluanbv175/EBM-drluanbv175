# 15/11/2026 — Báo «hoàn thiện» khi chuỗi biến ↔ phiếu ↔ đề cương còn lệch

**Bác sĩ (nguyên văn):**
- «Biến xác định không đúng, nhập liệu không đúng thì không thể phân tích được nên phải đảm bảo xác định biến đúng
  đồng bộ với đề cương».
- «Phải đạt sự đồng bộ giữa các cổng, từ vấn đề nghiên cứu, câu hỏi nghiên cứu, tổng quan tài liệu, mục tiêu nghiên cứu,
  thiết kế nghiên cứu, cỡ mẫu, chọn mẫu, biến, công cụ nghiên cứu và đề cương nghiên cứu…».
- «Phải đảm bảo nhất quán xuyên suốt và đồng bộ, đã có sự kiểm tra chéo, điều phối nhưng đã không thực hiện được và
  được báo cáo hoàn thiện».

## Nguyên nhân

Mỗi bộ chấm báo «đạt» đúng trong phạm vi nó đo, nhưng không phạm vi nào phủ đồng bộ biến:

| Bộ chấm | Phạm vi đo trước 15/11 |
|---|---|
| `gN_quality_gate` | Đủ hồ sơ của TỪNG cổng, không so giữa các cổng. |
| `nhat_quan_xuyen_cong` | 8 thông số: N, α, thiết kế, kết cục chính, quần thể, kết cục phục vụ N, giả thuyết, d. |
| G5 | Đồng bộ từ điển ↔ phiếu ↔ đề cương chỉ là ô người tự xác nhận (`dictionary_crf_aligned`). |
| Trách nhiệm cổng · hội đồng RQ4 | Dựa trên các số trên, nên kết luận DAT / AGENT_XONG trong khi biến còn sai. |

Lệch thật đo ngày 15/11 (chi tiết trong báo cáo kiểm đồng bộ cùng ngày):

- **BTM:**
  - `du_tieu_chuan` và `bmi` là trường calc REDCap; khi nhập qua Excel/SPSS chúng không được tính, nên quần thể phân tích rỗng.
  - SAP cần 8 cách mã hoá mà bộ biến G3 chưa có.
  - 2/3 mục tiêu không được SAP gọi tên.
- **C1a:** `NhomTuoi` 3 mức trong khi đề cương dùng 4 mức.

## Cách vá

**Repo y khoa:**

- `doi_chieu_bien_de_cuong.py` (PR y khoa «đối chiếu biến»).
- `nhat_quan_xuyen_cong` thêm 6 trục chuỗi:
  - biến ↔ đề cương/bộ biến;
  - phiếu ↔ từ điển (gồm mã từng câu và ô KSD);
  - mục tiêu ↔ SAP;
  - chọn mẫu chùm ↔ DE ↔ biến chùm;
  - đặc tả chờ bổ sung bộ biến;
  - tổng quan ↔ đề cương.

  Có `TRUC_THEO_CONG` để gán mỗi trục về các cổng liên quan.
- **G5-AUTO-11** do máy đo:
  - lệch nhập liệu ⇒ BLOCK;
  - chưa đủ để so ⇒ REVIEW;
  - lệch phân tích không chặn khoá nhập liệu, vì G6 tự chặn.
- `hoi_dong_cong.trach_nhiem` và `ho_so_cong` mang các trục của cổng:
  - lệch cứng ⇒ việc của điều phối cổng;
  - lệch mềm ⇒ chờ PI.

**Repo gốc:** RQ4 của `giam-khao-cong`, `_HOI-DONG-CONG` và `hoi-dong-cong.js` phải chấm TRÊN số đo máy.

## Kiểm hồi quy

- `tests/test_nhat_quan_day_du_20261115.py`: 22 ca; 19 phép đột biến đều đỏ đúng chỗ.
- Test đã bắt hai lỗi thật của chính bản vá trước khi commit:
  - `_muc_cao_nhat` xếp `chua_du` dưới `khop`, nên trục không đo được vẫn ra PASS;
  - `_co_that` coi câu khoảng trống «Chưa có nghiên cứu…» là ô trống.
- Fixture G5 nay mang bộ biến G3 + phiếu khớp từ điển. Đây là sửa fixture cho hợp lệ, không nới chốt (§0.8).

## Bài học

Báo «hoàn thiện» phải nêu phạm vi đo: công cụ nào đo gì, mắt xích nào chưa đo (⚪). Một ô người tự xác nhận
không phải là phép đo. Khi gộp mức của nhiều trục, phải kiểm thứ tự của hàm gộp: «không đo được» không bao giờ là
«khớp».
