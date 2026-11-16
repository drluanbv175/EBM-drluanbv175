# 16/11/2026 — Không hỏi lại điều đã chốt ở G7/G9/G10: một nguồn quyết định, gỡ khung bản nháp, G8 so đúng kết cục

## Bối cảnh
Tiếp `2026-11-15-gia-lap-tron-vong-g5-g10-spss-r.md`. Lượt giả lập trọn vòng đề tài thuần tập (PPI kéo dài → gãy xương
3 năm, N = 4396) đo được ba khiếm khuyết máy lớn nhất còn lại. Bác sĩ giao: «Hãy hoàn thiện vấn đề giả lập giúp tôi».

- **G7:** 14 ô bản thảo hỏi lại điều đã chốt ở G1/SAP/G2/G0, 3 ô hỏi lặp. Ngoài ra ~40 dòng khung bản nháp phải gỡ tay, vì
  hệ chưa có lệnh gỡ.
- **G9:** 53 ô hỏi lặp. Cover letter được chép lại trong gói A10, nên COI, tài trợ, chia sẻ dữ liệu và AI (đã khai ở
  G7–G8) bị hỏi lại.
- **G10:** PI phải khai lại 21 khoá cấp cao của `study_meta`, gồm SAP §4/§6/§11, G2 (miễn ICF, phiên bản, đăng ký), DMP
  và khoá dữ liệu G5, tác giả G7, phơi nhiễm/hiệp biến/nguồn đo của ma trận. Lý do: StudySpec chỉ đọc quyết định G0/G1.

## Đã làm (repo y khoa, nhánh `claude/hoi-lai-g7-g9-g10-20261116`)

1. **`tools/quyet_dinh_da_chot.py`** là MỘT nguồn «điều đã chốt».
   - `rut()` gom 21 khoá từ SAP đã khoá, G1, G2 (+ ngày duyệt trong sổ cái), G5, G7, và ma trận mục tiêu–biến (chỉ khi
     ma trận qua kiểm).
   - `lop_phu()` chỉ lấp khoá TRỐNG. Không ghi đè khoá PI, không chép ô còn [CẦN], không ghi đĩa.
   - Khoá «công cụ» chỉ lấp khi mọi nguồn đo là hồ sơ. Thang đo/PROM thì PI phải khai công cụ đã kiểm định.
   - Xem trước bằng `--study <mã>` (chỉ đọc).
2. **G10:** cả ba nơi dựng StudySpec đều áp lớp phủ: `run_g10_assemble.load_meta` (bộ lắp + cổng G10) và
   `check_de_cuong`.
   - Lượt giả lập đầu tiên sau vá cho thấy vì sao phải cùng một nguồn: check_de_cuong còn đọc `study_meta` thô, nên R16/R17
     chặn D08/D11/D12/D13/D15/D18 trên đề cương mà bộ lắp đã lấp đúng.
3. **G7:** `run_g7_auto.lap_o_da_chot_g7` lấp ô từ quyết định đã chốt. Checkpoint ghi `o_lay_tu_quyet_dinh_da_chot`.
   - Dòng Keywords để «[CẦN 3–5 MeSH terms chính thức]», vì bộ sinh thôi đoán từ khoá từ tiêu đề.
   - Lệnh mới `tools/go_khung_ban_thao_g7.py` gỡ ĐÚNG khung (chạy khô mặc định, `--ap-dung` sao lưu trước). Ô [CẦN…], số
     liệu và trích dẫn giữ nguyên.
4. **G9:** A10 Phần 6 chỉ trỏ tới tệp cover letter, không chép lại thư.
   - `lap_o_da_chot_g9` lấp các mục sau:
     - từ `G9_PUBLICATION_READINESS.json`: CRediT, người truy cập dữ liệu, tài trợ, AI, chia sẻ dữ liệu, guarantor;
     - từ `gate_params.G7/G8`: COI, tài trợ, AI;
     - từ khoá G5: N phân tích (cả khi G3 không có N kế hoạch);
     - từ G2: IRB, đăng ký;
     - từ bản thảo: tiêu đề, kết quả.
   - Danh tính tác giả chỉ ghi trên form ICMJE chính thức (gói lưu mã `AUTHOR-xx`). Phản biện đề xuất là mục tuỳ chọn.
5. **G8-AUTO-05 và `nhat_quan_xuyen_cong`** bỏ chú thích «*(điền sẵn từ quyết định đã chốt…)*» bằng cùng hằng
   `quyet_dinh_da_chot.GHI_CHU_DIEN_SAN_RE`.
   - Hồi quy bắt được lỗi này: G7 (đúng) không chép chú thích vào bản nộp, còn G8 so nguyên dòng SAP. Kết quả là phép thử
     đầu–cuối G10 của cả 8 thiết kế báo «kết cục chính vắng trong bản thảo».
6. **Bộ giả lập:**
   - Tác giả khai phiếu G9 rồi sinh lại gói.
   - Gỡ khung bằng công cụ của hệ.
   - Đo khoá G10 hệ tự lấp (`g10_he_tu_lap`).
   - Bỏ qua tệp `.bak-*`.
   - Ô «sau khi có dữ liệu thật» không bị coi là hỏi lại G3.

## Số đo (CHỈ đề tài thuần tập — 7 thiết kế còn lại chưa chạy trọn vòng G2→G10 trong bộ giả lập)

| Cổng | Trước | Sau |
|---|---|---|
| G7 hỏi lại điều đã chốt | 14 | 1 |
| G7 dòng khung gỡ tay | ~40 | 0 (công cụ hệ gỡ 50 dòng) |
| G9 hỏi lặp | 53 | 4 |
| G10 khoá PI khai lại | 21 | 0 (hệ tự lấp 21) |

- Mọi cổng G2–G10 vẫn PASS (khoá giả).
- Ô G7 còn lại là nhận định tính đại diện sau khi có dữ liệu, tức nội dung mới của tác giả.
- 4 ô G9 còn lại là phản hồi từng nhận xét trong khuôn thư phản biện, dùng sau khi tạp chí phản biện.
- Hồi quy: G7/G9/G10/StudySpec/check_de_cuong/placeholder/chấm sống đều xanh, gồm `test_chung_h_dau_cuoi_g10_toi_ready_khoa_va_rang_buoc`
  cho mọi thiết kế.
- 10 phép đột biến đều đỏ đúng chỗ rồi xanh lại.

## Đo chỉ đọc trên đề tài thật
- **C1a:** lớp phủ sẽ lấp 6 khoá trống: consent_plan, expected_results, primary_analysis, protocol_version, risk_benefit,
  table_shells.
- **BTM:** lớp phủ sẽ lấp 5 khoá trống: consent_plan, expected_results, missing_data_analysis, primary_analysis,
  table_shells.
- C1a đã ký G10 nhưng G10 đã «HẾT KHỚP» từ trước. Lắp lại sẽ ra StudySpec khác bản lưu, nên PI phải ký lại G10. Không
  sửa tay cho khớp.

## Bài học
- Một quyết định đã chốt phải đọc từ MỘT nguồn ở mọi nơi dùng nó. Bộ lắp, cổng và bộ kiểm đọc khác nhau thì chặn nhầm
  (R16/R17) hoặc xanh giả.
- Chú thích soạn thảo của khuôn không phải nội dung. Nơi nào bỏ nó thì mọi nơi so phải bỏ theo, bằng cùng một hằng.
