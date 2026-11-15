# 15/11/2026 — Giả lập 8 thiết kế: lỗi đầu chuỗi G0/G1 và canary đếm nhầm

## Bối cảnh
Bác sĩ giao: «Hãy giả lập hoàn thiện chi tiết 8 loại thiết kế rồi từ đó vá để hệ thống đang trạng thái tự động tốt nhất», rồi
nhấn mạnh: «Việc giả lập phải được thực hiện như một đề tài thật xuyên suốt thống nhất từ đó mới đánh giá và hoàn thiện được hệ
thống».

Canary `tools/gia_lap_dinh_ky.py` trước đó chỉ có 2 kịch bản (RCT, cắt ngang). Đã thêm 6 kịch bản ở
`tools/gia_lap_kich_ban_them.py`: thuần tập, bệnh–chứng, chẩn đoán, mô hình dự báo, tổng quan/gộp, định tính. Mỗi kịch bản là
một đề tài ngoại trú tổng hợp, có nhãn GIẢ LẬP, không PII. Nguồn số tra PubMed và đã kiểm rút bài (pubmed `ok`):

| Kịch bản | Nguồn |
|---|---|
| Thuần tập | PMID 26462494 (RR 1,33) |
| Bệnh–chứng | PMID 23137151 (RR 1,84 ibuprofen) |
| Chẩn đoán | PMID 34001645 (AUROC 0,76; tỷ lệ 30%) |
| Dự báo | PMID 32188600 (Riley; N tính tay 898) |

Hồ sơ mỗi đề tài nay gồm cả bộ biến và ma trận mục tiêu → biến, nộp cùng G3.

## Đo được (chạy trực tuyến, dây chuyền thật trên bản sao tạm)
1. **G0-AUTO-08 kẹt truy vấn đúng chuẩn.** Hàm so thuật ngữ đòi đủ mọi chữ của cụm dịch máy, nên:
   - Chẩn đoán: «diagnosis» không nhận «diagnostic accuracy»[tiab].
   - Định tính: «insulin therapy» không nhận `insulin[tiab]`.
   - RCT «Tin nhắn SMS…»: từ điển chỉ rút «antihypertensive agents» (thuốc được nhắc), thiếu «tin nhắn», nên báo thiếu I.
2. **G1 thiếu nhóm từ khoá «thuần tập/đoàn hệ/cohort».** Câu hỏi tác hại luôn thành bệnh–chứng, kể cả với tên đề tài
   «…: nghiên cứu thuần tập hồi cứu».
3. **G1 không nhận «bệnh–chứng» viết bằng gạch ngang dài, và tên đề tài dạng NFD.** Hệ quả: đề tài «bệnh–chứng lồng trong
   thuần tập» bị nhận thành thuần tập.
4. **Canary đếm «tự chạy G3» thành lỗi N4 ở 4/6 thiết kế.** Nguyên nhân thật là G3-AUTO-19: kịch bản chưa nộp bộ biến.

## Sửa
1. `g0_quality_gate`:
   - chữ chung không bắt buộc;
   - nhận biến thể hình thái (từ ≥6 ký tự, gốc ≥5);
   - thuật ngữ Latin PI viết sẵn trong PICO (SMS, FIB-4, PPI…) là phương án THAY THẾ: chỉ thêm khi khái niệm đã có thuật ngữ
     từ điển hoặc PI khai, hoặc khi truy vấn do máy dịch; không phủ hộ khái niệm khác.

   `run_g0_auto.VI_EN_TERMS`: thêm «tin nhắn»/«nhắn tin».
2. `run_g1_auto`:
   - nhóm «cohort» là cụm khai thiết kế, giữ nguyên loại câu hỏi;
   - thứ tự: sau bệnh–chứng/chẩn đoán/dự báo, trước mô tả;
   - R6 không cảnh báo «cohort» cho chẩn đoán/dự báo/tổng quan;
   - `_kw_in` chuẩn hoá NFC và mọi loại gạch.
3. Canary:
   - «tự chạy cổng» mà tiêu chí máy không đổi ⇒ ghi `tu_chay_cong_khong_doi`, không tính lỗi máy;
   - PI nộp bộ biến và ma trận cùng nội dung G3.

## Kiểm
- Test: `tests/test_gia_lap_8_thiet_ke_dau_chuoi_20261115.py` (24 ca) và 3 ca mới ở `tests/test_gia_lap_dinh_ky_20261115.py`.
- 16 phép đột biến đều làm test đỏ đúng ca. Lần đầu M12 sống sót vì từ điển «tin nhắn» che phần Latin; đã thêm ca chỉ token
  Latin mới cứu được. Lần đầu M8 hỏng cú pháp nên đã làm lại.

## Bài học
- Một tiêu chí so khái niệm phải được đo trên truy vấn ĐÚNG CHUẨN của từng thiết kế. Chỉ đo trên đề tài khởi nguồn (tuân thủ,
  hài lòng) thì không lộ việc nó chặn oan nghiên cứu chẩn đoán/định tính.
- Nới luật phải giữ một chiều: thuật ngữ thay thế chỉ được thêm cách ĐẠT. Nếu không, nó tạo ra nghĩa vụ mới (mã ICD trong P)
  hoặc phủ hộ khái niệm khác (FIB-4 trong câu kết cục).
- Giả lập phải là đề tài thật có hồ sơ duy nhất. Thiếu bộ biến làm canary đổ lỗi sai chỗ.

## Phần trọn vòng (đề tài như thật, G2/G4 có ký bằng khoá giả trong pytest)
Bác sĩ chỉnh hướng giữa chừng: giả lập phải như một đề tài thật, xuyên suốt và thống nhất. Bộ giả lập trọn vòng mới là
`tools/gia_lap_tron_vong.py`, chạy bằng `GIA_LAP_TRON_VONG=1 pytest tests/test_gia_lap_tron_vong_20261115.py`.

Mọi vai mô phỏng chỉ điền từ hồ sơ đề tài. Mỗi ô [CẦN] được phân loại trước khi điền:
- hỏi lại điều đã chốt;
- hỏi lặp;
- không áp dụng;
- mới đúng vai;
- hồ sơ chưa có.

Sau mỗi cổng, đo trục nhất quán. Đề tài thuần tập đi tới `PASS_G2_APPROVED` (miễn phiếu đồng ý) và `PASS_G4_SAP_LOCKED`.

Đo được thêm:
5. **Trục kết cục chính** so NGUYÊN dòng §2 do chính máy điền sẵn từ G1 với tên kết cục G0. Hệ quả: lệch mềm, PI phải xác
   nhận «cùng một kết cục» (BTM phải làm đúng bước này, mục B1). Sửa: `_ten_ket_cuc_sap` chỉ so phần tên. Hai đề tài thật
   có số đo trước/sau và dấu vân tay xác nhận (`be7a10ba02e38f7d`) trùng khít.
6. **G2 sinh phiếu đồng ý dù PI đã xin miễn.**
   - Đề tài thuần tập hồi cứu: 37 ô ICF thừa.
   - BTM: ~220 dòng ICF.
   - Quyền xin miễn cố định theo thiết kế.

   Sửa:
   - `ap_xin_mien_icf` và `thu_gon_icf_khi_xin_mien`: khi `icf_waiver_requested` = true thì TÀI LIỆU 4/5 thành «không áp
     dụng», luôn có TÀI LIỆU 9; không áp cho RCT.
   - Cổng G2 không đòi mục ICF và hai nhãn chỉ thuộc ICF.

   Kết quả: số ô G2 giảm 89 → 52.
7. **G3 in khung độ chính xác cho định tính khi khai «descriptive_precision».** Hệ quả: G3-AUTO-17 của chính hệ chặn đề tài
   định tính. Sửa: 3 thiết kế không dùng công thức lực mẫu có hàng «Khung cỡ mẫu» thay thế, không in α/lực/bảng
   Power×ES.
8. **Ma trận tổng quan/gộp bị MT-05 chặn.** Phiếu trích xuất cần số biến cố của hai nhánh. Sửa: thiết kế `sr_ma` được khai
   nhiều dòng kết cục chính kiểu đếm/liên tục.

Gộp với #281 (phiên khác) cùng sửa canary và G0:
- Lấy cơ chế `bien_so`/G3-T2 của #281 làm chuẩn. 6 kịch bản mới chuyển sang khuôn đó; bỏ cơ chế trùng.
- Ở G0, #281 nhận chữ viết tắt vô điều kiện, dẫn tới rò «FIB» sang O và tạo nghĩa vụ «ICD». Đã giữ ý của cả hai: chữ viết
  tắt chỉ là phương án thay thế, không phủ hộ khái niệm khác. Test của cả hai bên đều đạt; ba phép đột biến then chốt đều đỏ.

Còn để ngỏ, đo được nhưng chưa sửa ở đợt này:
- G2 vẫn hỏi lại thời gian nghiên cứu và lý do cần nghiên cứu (đã chốt ở G1).
- Thông tin chủ nhiệm, tài trợ, nơi lưu bị hỏi lặp nhiều nơi.
- Mục mã đăng ký thử nghiệm vẫn hiện dù PI chốt không bắt buộc đăng ký.
- `approve_gate` đòi dấu vân tay G4 ở nhóm phê duyệt trong khi màn chấm báo READY.
- G5→G10 chưa chạy trong bộ giả lập trọn vòng.
