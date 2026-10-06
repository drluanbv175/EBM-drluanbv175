# 06/10/2026 — Soát từng cổng G0–G10 hoàn tất: 11 cổng + điều phối NGANG + doctrine CHUNG-I

Tiếp nối `2026-10-04-soat-tung-cong-va-dieu-phoi-g0g10.md` (đợt 0). Bác sĩ chọn «tôi làm trực tiếp từng cổng»
(không workflow). Nhánh y khoa `claude/hoan-thien-cong-g0g10-20261004` xếp chồng trên y khoa #89; nhánh gốc
`claude/hoan-thien-cong-g0g10-goc-20261006` xếp chồng trên gốc #128.

**Từng cổng (y khoa)** — mỗi cổng: vá phát hiện đã phản biện xác nhận → test hồi quy → kiểm đột biến → toàn bộ bộ test →
đo C1a trên BẢN SAO (exports thật không đổi, so băm) → commit:

| Cổng | Commit | Đột biến bị bắt |
|---|---|---|
| G0 | 34a039e | 18/18 |
| G1 | e31be97 | 43/43 |
| G2 | 30787e6 | 52/52 |
| G3 | 62d9ed2 | 39/39 |
| G4 | b5befcb | 56/56 |
| G5 | 9c81f66 | 61/61 |
| G6 | c41bae6 | 49/49 |
| G7 | 639b4ca | 46/49 + bù 5/5 |
| G8 | 5cfb55a | 33/42 + bù 10/10 + 1/1 + 4/4 |
| G9 | eedce2f | 31/33 + bù 6/6 |
| G10 | dbcab0a | 38/39 + bù 1/1 |
| NGANG | 00d61d3 | 24/26 (1 tương đương) + bù 1/1 |
| CHUNG-H/CHUNG-F | 9eceb20 | 54/55 + bù 2/2 |

**G10 (lần đầu chạy chuỗi THẬT G0→G9 khoá tới G10):** đề cương đủ dữ kiện vẫn không bao giờ qua G10-AUTO-09 vì khuôn in
«[CẦN]» VÔ ĐIỀU KIỆN (đặt vấn đề, pháp lý, DMP, tài liệu tham khảo…), ghi chú rà G3 sau khi thống kê viên đã chốt, repr
dict, R4 của check_de_cuong không biết PMID đã qua A12. Mục đích ETHICS_SUBMISSION/REGISTRY_UPDATE có trong danh sách mà
không bao giờ khoá được (đòi G5–G9) — nay chỉ đòi G0–G4; kiểm trên chuỗi TRƯỚC IRB thật (run_g2_auto → PI điền ô
trước-nộp ⇒ G2 READY_FOR_IRB_SUBMISSION chưa duyệt; G4 chưa ký) ⇒ READY → PI ký → LOCKED.

**Sự cố do chính bản vá gây ra (bắt được trước khi gộp):** G10-02 cho G10 chấm LẠI `check_de_cuong` trên đề cương hiện
hành. `check_de_cuong` gọi `skill_standards.real_world_signals`, hàm này lại chấm sống G10 ⇒ G10 → check_de_cuong → tín
hiệu → G10 … đệ quy tới RecursionError — bị nuốt thành «chưa khoá» (RecursionError là RuntimeError). Đo trên bản sao C1a:
một lượt chấm G10 15,9 giây, study_readiness 23 giây; toàn bộ bộ test vẫn xanh vì kết quả «chưa khoá» trùng kỳ vọng. Lộ
nhờ ĐO THỜI GIAN một phép đo C1a (6 phút) rồi cProfile. Vá: tín hiệu đời thực chấm qua `cong_song.trang_thai_song` (đệm +
chốt vòng lặp) ⇒ 0,2 giây; test chốt số lần gọi bộ chấm G10 ≤ 2.

**Bài học:**
1. Một cổng bắt đầu chấm lại thứ gì đó mà thứ đó lại đọc «tín hiệu» của chính cổng ⇒ kiểm vòng gọi. Mọi phép chấm sống
   xuyên cổng đi qua `cong_song` (có chốt vòng lặp), không gọi thẳng `gN_quality_gate.evaluate_study`.
2. Bộ test xanh không chứng minh hết lỗi: kết quả sai trùng kỳ vọng bi quan («chưa khoá») thì không test nào đỏ — đo thời
   gian bất thường là tín hiệu.
3. CHUNG-A («tin trạng thái LƯU») còn sống ở CÔNG CỤ HIỂN THỊ sau khi mọi cổng đã chấm sống: study_readiness, đài kiểm soát,
   kiem_chi_tiet, tín hiệu đời thực. Nay đều chấm sống; cờ đời thực bác sĩ khai trong study_meta chỉ còn tác dụng với
   checkpoint KIỂU CŨ (cổng đã có hợp đồng ⇒ chấm sống quyết định).

**Doctrine CHUNG-I:** 11 agent nghiên cứu bỏ mọi chỉ dẫn «agent ghi Gx_STATUS=LOCKED», tiền đề theo chấm sống, bảng hợp
đồng hiện hành G1/G3/G4/G5/G6/G7/G8/G9/G10, Annex 2 (bộ thi hành có thật; RCT khai `annex2.applicable`), PROSPERO bắt buộc
cho SR/MA, xác nhận người gắn dấu vân tay.

**C1a (đo trên bản sao 06/10/2026):** G0/G1 DỰ THẢO khi chấm sống (study_meta sửa sau xác nhận), G2 DỰ THẢO (hồ sơ còn ô
trống; chưa ký), G3/G4 BỊ CHẶN và cũ hơn G0–G2; với mục đích ETHICS_SUBMISSION, G10 chỉ còn đòi G0–G4 và nêu đúng các lý do
đó. SAP cũ của C1a in «Power 80%» cho thiết kế mô tả và chưa in sai số d ⇒ sinh lại SAP khi bác sĩ chốt G3.

**CHUNG-H (chuỗi THẬT G0→G9 khoá → G10 cho CẢ 8 thiết kế) + CHUNG-F — commit y khoa 9eceb20 (doctrine 22bc4be; gốc 217ae17):** test từng cổng và chuỗi
đầu–cuối của cohort không thấy các lỗi sau; mỗi thiết kế lộ một khuôn riêng:
1. RCT — A12 ghép NGƯỢC: G7/G8/G9 dùng chung hàm A12 của G10, hàm này đối chiếu cả đề cương G10 ⇒ lắp G10 (đề cương
   trích PMID SPIRIT 2025) làm G7 tụt DRAFT, G8 BLOCKED, G9 mất khoá. Nay chỉ G10 đối chiếu đề cương (`kiem_ban_g10`).
2. RCT — quyết định đã chốt ở G1 (ngẫu nhiên hoá, che giấu, làm mù, quy tắc dừng, lịch trình) không tới §6; tác hại trỏ
   kế hoạch an toàn G2 khi PI đã xác nhận; kế hoạch vào manifest.
3. Cắt ngang (thiết kế của C1a) — mọi loại giả thuyết khác «superiority» rơi vào nhánh biên Δ của NI ⇒ đề cương mô tả in
   «Margin Δ = [CẦN…] [CẦN Hội đồng… CONSORT-NI]», R3 chặn G10. G4 đã vá đúng lỗi này ở SAP §12 ngày 04/10 — G10 thì chưa.
4. SR/MA — R4 gắn «nghi bịa» cho PRISMA-P 2015 (PMID 25554246) do CHÍNH hệ chèn vào đề cương ⇒ G10 BLOCKED. Nay là GHI
   CHÚ (nguồn: `protocol_checklist_items`), vẫn phải qua A12.
5. Định tính — dòng «Phần mềm mã hóa (QDA)» in «[CẦN BỔ SUNG]» vô điều kiện ⇒ G10-AUTO-09 không bao giờ qua; nay đọc khai
   báo và StudySpec Q02 đòi khi thiếu.
6. CHUNG-F (đo trên bản sao C1a): StudySpec chỉ đọc khoá CẤP CAO của study_meta ⇒ C1a đã chốt ở G1 câu hỏi, mục tiêu,
   bối cảnh, thời gian, quần thể, tiêu chuẩn, cách chọn mẫu, kết cục mà vẫn bị báo thiếu D02/D03/D05–D08 và đề cương in
   «[CẦN BỔ SUNG]» — bác sĩ sẽ phải khai LẠI. Nay G1 (rồi G0) là nguồn kế tiếp; khoá cấp cao vẫn thắng; kết cục chính đọc
   CẢ khối đúng thứ tự bộ chấm G1 đọc (một định nghĩa cho mọi cổng). Mục «Đối tượng» chỉ in `sampling_method` (StudySpec
   D07 nhận cả cách tuyển) và chưa từng in quần thể đích.
7. Ký tự «ℹ» của biểu ngữ gói G10 không có glyph trong Times New Roman (ô vuông trong Word).

Đột biến: 54/55 + bù 2/2; toàn bộ bộ test y khoa 8091 qua, 0 đỏ. Test đầu–cuối G10 nay tham số hoá đủ 8 thiết kế (READY → PI ký → LOCKED; đề cương không còn
«[CẦN»; quyết định G1 có mặt mà PI không khai lại).

**Bài học:** (1) «điều phối xong» chỉ nói được sau khi chuỗi THẬT của MỌI thiết kế hỗ trợ đi hết tới G10 — một thiết kế
đại diện che các khuôn riêng (biên NI, PRISMA-P, QDA). (2) Bản vá một lỗi ở cổng này phải tìm cùng lỗi ở cổng khác (biên Δ:
G4 vá 04/10, G10 sót tới 06/10). (3) Đo trên đề tài THẬT (bản sao C1a) lộ lỗi mà đồ gá không có: đồ gá khai mọi khoá ở cấp
cao nên không bao giờ thử đường «lấy từ G1».

Cần bác sĩ kiểm chứng.
