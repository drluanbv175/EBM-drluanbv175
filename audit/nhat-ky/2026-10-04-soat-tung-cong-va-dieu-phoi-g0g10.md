# 04/10/2026 — Soát từng cổng G0–G10 + điều phối thống nhất: bảy chỗ hở đo được trên mã sống

**Bác sĩ:** «Các cổng của hệ thống nghiên cứu y khoa đã được hoàn thiện và có sự điều phối giữa các cổng một cách thống nhất…
nếu chưa hãy hoàn thiện một cách triệt để», rồi «từng cổng phải hoàn thiện một cách triệt để, sau đó là sự điều phối thống
nhất giữa các cổng». Chọn cách làm: tôi làm trực tiếp từng cổng (không workflow).

**Bộ đo sẵn có báo xanh:**
- `verify_controlled_research_automation.py` PASS.
- `kiem_chi_tiet_he_nghien_cuu.py` cho C1a: 0 🔴, 39 🟡 (việc người thật).

Hai bộ đo này không soi phần điều phối xuyên cổng, cũng không soi việc «mỗi cổng có đủ cho mọi thiết kế».

**TỪNG CỔNG — đo được:**
1. **G4:** `_G4_REQUIRED_SECTIONS` chỉ có §1/§2/§5/§10. **§4 PHÂN TÍCH CHÍNH** và **§9 PHÂN TÍCH ĐỘ NHẠY** không được kiểm
   ô trống, trong khi bộ sinh điền «[CẦN]» vào phương pháp chính cho thiết kế không có khuôn ⇒ SAP ký khoá được khi phân tích
   chính còn trống.
2. **G1:** thiết kế bác sĩ GHIM ngoài 8 mã mà chuỗi hỗ trợ (rct/cohort/case_control/cross_sectional/diagnostic/sr_ma/
   prediction/qualitative) bị lặng lẽ thay bằng thiết kế suy luận — chỉ có một dòng in ra màn hình, checkpoint không ghi gì.
3. **G7:** ba chỗ `.get(design, ("STROBE 2007", 22))` / khuôn cohort ⇒ thiết kế chưa có bảng checklist được đối chiếu bằng
   STROBE mà không cảnh báo.
4. **G8:** `real_world_signals` đọc hai trường mà không mã nào ghi ⇒ G8 chỉ «đã duyệt» khi `study_meta` tự khai, trong khi
   năm cổng cứng còn lại đều chấm sống qua bộ chấm có kiểm sổ cái.

**ĐIỀU PHỐI — đo được:**

5. **Hai công cụ trái nguồn sự thật về số cổng cứng** (`gate_contract` có SÁU cổng):
   - `run_pipeline.py` báo cổng cứng thiếu G8;
   - `study_readiness.py` đếm «x/4» (thiếu G5, G10) — nguồn của dòng hòm việc «C1a: 0/4 cổng cứng».
6. **Không phép đối chiếu nào nhìn cả chuỗi.**
   - Cùng một thông số có nhiều bản sao: kết cục chính ở gate_params G0/G1/G8, TRDS 19 và SAP §2; N ở G3, TRDS 17, G4 và SAP §12;
     thiết kế ở checkpoint G1–G10 và TRDS 15.
   - Các phép so cũ rải rác theo cặp (G4, G8).
7. **Độ tươi đo bằng mtime.** Bản clone dàn phẳng mtime ⇒ cổng lạc hậu bị báo TƯƠI, trong khi G10-AUTO-03 dùng đúng phép đo
   này làm tiêu chí chặn.

Thêm: bảng định tuyến `.claude/agents/README.md` và hai sơ đồ hạ tầng vẫn ghi «march G0→G9».

**Vá** (PR y khoa + PR gốc cặp, doctrine trùng byte):
- **Mục 1:** thêm §4 và §9 vào tập mục bắt buộc.
- **Mục 2:** ghi `design.pin_bi_tu_choi` vào checkpoint; G1-AUTO-02c CHẶN.
- **Mục 3:** `_checklist_cho_thiet_ke` lấy tên chuẩn đúng từ `skill_standards`, gắn «[CẦN BỔ SUNG DANH MỤC…]» thay vì
  STROBE.
- **Mục 4:** thêm nhánh hợp đồng chất lượng cho G8, mirror G9.
- **Mục 5:** cả hai công cụ rút tập cổng cứng từ `gate_contract`. Hòm việc gốc nhận cả «0/6» lẫn «0/4».
- **Mục 6:** công cụ mới `tools/nhat_quan_xuyen_cong.py` (chỉ đọc), nối vào bốn nơi:
  - G10-AUTO-11: lệch cứng N/α/power/thiết kế/loại đăng ký ⇒ BLOCK; kết cục chính lệch ⇒ REVIEW;
  - mục XUYÊN của `kiem_chi_tiet`;
  - `study_readiness`;
  - báo cáo `run_pipeline`.
- **Mục 7:** `mtime_khong_tin_duoc` ⇒ fresh=False, không tự chạy lại hàng loạt.
- Doctrine `dieu-phoi-nghien-cuu`/`thiet-ke-nghien-cuu` dạy các luật mới. README và hai sơ đồ sửa thành G0–G10.

**Đo trên C1a sau vá:**
- Xuyên cổng 7/7 khớp: N = 1000 ở 5 nơi; cắt ngang ở 6 nơi; kết cục chính thống nhất ở 4 nơi.
- §4/§9 SAP đã điền ⇒ không chặn oan.

**Kiểm:**
- 23 test mới (`tests/test_dieu_phoi_thong_nhat_g0g10_20261004.py`); đột biến 18/18 bị bắt.
- 922 test liên quan xanh.

**Giới hạn còn lại (ghi rõ, chưa làm):**
- Chuỗi G0–G10 chỉ hỗ trợ 8 thiết kế. TREND/SQUIRE 2.0/CARE/hỗn hợp/kinh tế-làm-thiết-kế-chính cần bổ sung khuôn ở
  G3/G4/G6/G7, kèm danh mục checklist đã xác minh nguyên văn — dự án riêng.
- Độ tươi theo dấu vân nội dung lúc sinh (thay mtime) phải sửa 11 bộ sinh; hiện chỉ làm phần chặn an toàn (dàn phẳng ⇒
  không đo được).
