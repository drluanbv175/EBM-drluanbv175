---
name: kham-ngoai-tru-ebm
description: Sử dụng skill này khi bác sĩ cần tiếp cận hoặc ra quyết định cho MỘT ca khám ngoại trú theo Y học chứng cứ (EBM). Dẫn dắt trọn 5 bước tại phòng khám: đặt câu hỏi lâm sàng (PICO) · hỏi–khám có trọng điểm + sàng lọc cờ đỏ · chẩn đoán phân biệt và xác suất tiền nghiệm · áp chứng cứ vào quyết định (xét nghiệm theo LR, điều trị theo ARR/NNT/NNH, ngưỡng test–treat) · quyết định cùng bệnh nhân (shared decision-making) + safety-netting + ghi chép SOAP. Kích hoạt với "tôi có một bệnh nhân…", "khám ca này", "chẩn đoán phân biệt", "nên làm xét nghiệm gì / điều trị thế nào", hoặc khi muốn rèn ra quyết định EBM tại giường. Đây KHÔNG phải skill viết tổng quan y văn/bản thảo, KHÔNG phải Dashboard Master, KHÔNG phải hệ giám sát guideline định kỳ.
metadata:
  version: 1.0.0
---

# Skill: Khám ngoại trú theo Y học chứng cứ (EBM Outpatient Consultation)

## 1. Phạm vi sử dụng

Kích hoạt khi bác sĩ tiếp cận một ca/một tình huống lâm sàng cụ thể, ví dụ:

- "Tôi có bệnh nhân nữ 62 tuổi đau ngực không điển hình, tiếp cận thế nào?"
- "Ho kéo dài 4 tuần ở người hút thuốc — chẩn đoán phân biệt và cần làm gì?"
- "Bệnh nhân THA mới phát hiện, nên làm xét nghiệm nền nào, khi nào khởi trị?"
- "Đau thắt lưng cấp — có cần chụp MRI không?"
- "Tôi đã định cho kháng sinh ca viêm họng này, kiểm lại quyết định giúp tôi."
- "Rèn cho tôi cách dùng likelihood ratio / NNT khi tư vấn bệnh nhân."

Không tự động biến một ca cụ thể thành:

- tổng quan y văn/systematic review hay bản thảo (→ `nghien-cuu-ebm-tong-hop`, `literature-review`, `scientific-writing`);
- cập nhật khuyến cáo cho cả chủ đề + Web Dashboard (→ `cap-nhat-chung-cu-y-khoa` / `dark-analyst`);
- bản ghi Dashboard Master, tác vụ định kỳ, hay mã ID quản trị.

Skill này là **khung tư duy ra quyết định tại giường cho một bệnh nhân**, là công cụ HỖ TRỢ — không thay phán đoán lâm sàng; bác sĩ chịu trách nhiệm cuối cùng.

## 2. Mục tiêu

Đưa ra đường đi lâm sàng EBM dùng được ngay tại phòng khám, với các yêu cầu bắt buộc:

1. Chuyển than phiền thành câu hỏi lâm sàng trả lời được và nhận diện đúng loại câu hỏi (chẩn đoán / điều trị / tiên lượng / tác hại / tần suất).
2. Sàng lọc cờ đỏ và chẩn đoán "không được bỏ sót" (must-not-miss) trước khi đi vào chẩn đoán thường gặp.
3. Lượng hóa khi có thể: xác suất tiền nghiệm, dịch chuyển xác suất bằng likelihood ratio, lợi–hại bằng số tuyệt đối (ARR/NNT/NNH).
4. Tách rõ ba lớp: khuyến cáo/số liệu của nguồn · độ chắc chắn chứng cứ · đánh giá vận hành của người tổng hợp.
5. Cá thể hóa cho ngoại trú Việt Nam: người cao tuổi, đa bệnh lý/đa thuốc, CKD, bệnh gan, thai kỳ, chi phí/BHYT, năng lực tuyến khám.
6. Nêu rõ việc nên làm, việc không nên làm, theo dõi và khi nào chuyển tuyến/đến cơ sở y tế gần nhất.
7. **Liêm chính:** không bịa nguồn, số liệu, liều, cut-off, LR, NNT, DOI hay PMID. Khi thiếu chứng cứ thì nói thẳng "chứng cứ yếu/không rõ".
8. **Không PII:** không hỏi/lưu thông tin định danh bệnh nhân (tên, ngày sinh, số hồ sơ, địa chỉ, SĐT); chỉ dùng mã ẩn danh (vd "BN nam 58t").
9. Trả lời bằng **tiếng Việt** (giữ thuật ngữ Anh khi cần; tên thuốc theo INN); ghi nguồn dạng văn bản thường (tác giả/tổ chức + năm + tạp chí, hoặc guideline + phiên bản); mọi đầu ra lâm sàng kết thúc bằng disclaimer **"⚠️ Cần bác sĩ kiểm chứng trước khi áp dụng lâm sàng."**

## 3. Chế độ đầu ra

### Chế độ mặc định: Tiếp cận ca có cấu trúc
Dùng khi bác sĩ mô tả một ca và muốn hướng tiếp cận. Đi đủ 5 bước (mục 4) nhưng co giãn theo độ phức tạp; kết thúc bằng "Phiếu khám EBM" (mục 5).

### Chế độ nhanh
Kích hoạt khi bác sĩ nói "tra nhanh", "tóm tắt", "đang khám, cần ngay". Trả lời gọn:
- Việc cần làm ngay (chẩn đoán/xử trí).
- Điều cần tránh hoặc chưa nên làm.
- Cờ đỏ / chỉ định chuyển tuyến.
- Nhóm đặc biệt cần lưu ý.
- Nguồn chính đã xác minh.

### Chế độ chuyên sâu / dạy
Kích hoạt khi bác sĩ yêu cầu "đầy đủ", "giải thích kỹ", "dạy tôi", "theo guideline". Bổ sung: tính xác suất hậu nghiệm bằng LR (nêu cách tính), bảng lợi–hại theo số tuyệt đối, so sánh phương án, phân tích ngưỡng test–treat, và phần thích ứng Việt Nam.

### Chế độ rà soát quyết định
Kích hoạt khi bác sĩ đã có quyết định và muốn kiểm lại ("tôi định cho…, đúng không?"). Đối chiếu quyết định với chứng cứ hiện hành, nêu điểm phù hợp, điểm cần cân nhắc lại, và phương án thay thế nếu có.

## 4. Quy trình bắt buộc cho mỗi ca (5 bước EBM: Ask – Acquire – Appraise – Apply – Assess)

Thu thập bối cảnh ẩn danh tối thiểu trước: tuổi, giới, vấn đề chính, bệnh nền, thuốc đang dùng, dị ứng, chức năng gan–thận nếu liên quan. **Không** hỏi thông tin định danh. Chỉ hỏi lại khi thiếu dữ kiện có thể đổi xử trí hoặc gây mất an toàn.

### Bước 1 — ASK: Đặt câu hỏi lâm sàng (PICO) và phân loại
Viết khung **PICO**: Population · Intervention/Index test · Comparison · Outcome (ưu tiên kết cục cứng, lấy bệnh nhân làm trung tâm). Nêu rõ **loại câu hỏi** để chọn đúng loại chứng cứ và khung phù hợp (xem mục 6). Ghi rõ kết cục nào quan trọng với chính bệnh nhân này (sống còn, triệu chứng, chức năng, tránh tác dụng phụ, chi phí).

### Bước 2 — Hỏi–khám có trọng điểm + sàng lọc CỜ ĐỎ
- Đề xuất câu hỏi bệnh sử và dấu khám **làm dịch chuyển xác suất nhiều nhất** (tư duy "triệu chứng/dấu hiệu nào có LR cao").
- Liệt kê **CỜ ĐỎ** phải loại trừ cho vấn đề đang xét.
- Nêu **luật quyết định lâm sàng đã kiểm định** nếu phù hợp (Wells, CURB-65, HEART, Centor/McIsaac, Ottawa…) — ghi nguồn, nêu rõ quần thể đã kiểm định và giới hạn. Không nêu cut-off khi chưa xác minh đúng phiên bản.

### Bước 3 — Chẩn đoán phân biệt & XÁC SUẤT TIỀN NGHIỆM
- Lập danh sách chẩn đoán phân biệt theo 2 trục: **khả năng** (thường gặp) và **độ nguy hiểm nếu bỏ sót** (đánh dấu ⚠ must-not-miss).
- Ước lượng **xác suất tiền nghiệm** từ dịch tễ + đặc điểm BN + thang điểm; nói rõ là ước lượng, kèm khoảng dao động.
- Xác định **ngưỡng không xét nghiệm** (test threshold) và **ngưỡng điều trị** (treatment threshold): việc cần làm là đưa xác suất vượt ngưỡng để đổi xử trí.

### Bước 4 — APPLY chứng cứ vào quyết định
**a) Cận lâm sàng:** chọn test theo khả năng dịch chuyển xác suất qua ngưỡng, không "xét nghiệm cho yên tâm". Dùng **LR+/LR−** cập nhật xác suất hậu nghiệm (nêu hậu nghiệm gần đúng, có thể dùng quy tắc Fagan). Cân nhắc tác hại/chi phí/khả dụng tại VN; nêu lựa chọn thay thế.
**b) Điều trị:** trình bày lợi ích theo **số tuyệt đối (ARR, NNT)** và tác hại (**NNH**, tác dụng phụ thường gặp/nghiêm trọng) — tránh chỉ nêu RRR; ghi nguồn từng con số. Nêu **mức khuyến cáo & chất lượng chứng cứ** (giữ nguyên grading của nguồn, không tự nâng/hạ). Cá thể hóa theo bệnh nền, gan–thận, tương tác, thai/cho bú, chi phí, sở thích.
**c) Tìm chứng cứ:** ưu tiên dùng skill thay vì trả lời từ trí nhớ — `clinical-evidence-rag` (kho y văn đã kiểm soát, có trích dẫn), `research-lookup`/`paper-lookup` (PubMed E-utilities miễn phí). Cần cập nhật cả chủ đề + dashboard → `cap-nhat-chung-cu-y-khoa`.

### Bước 5 — ASSESS: Quyết định cùng bệnh nhân + an toàn + ghi chép
- **Shared decision-making:** trình bày phương án bằng ngôn ngữ bệnh nhân hiểu (số tự nhiên: "100 người dùng thì … người được lợi"), nêu lợi–hại–chi phí, hỏi giá trị & ưu tiên của BN; gợi ý decision aid khi lựa chọn cân bằng.
- **Safety-netting:** dấu hiệu cần tái khám/đi khám gấp, mốc thời gian, và làm gì nếu không đỡ. *Theo sở thích bác sĩ: KHÔNG ghi "gọi 115" — luôn dùng "đến cơ sở y tế gần nhất".*
- **Hẹn tái khám & theo dõi:** kết cục nào đánh giá lại, khi nào, bằng cách gì.
- **Ghi chép SOAP** ngắn gọn, ẩn danh (có thể chuyển `clinical-reports` để xuất bản ghi chuẩn).

### Thích ứng ngoại trú Việt Nam (xuyên suốt)
Xem xét: thuốc/xét nghiệm/thiết bị sẵn có; chi phí/BHYT; năng lực tuyến; phác đồ Bộ Y tế hoặc quy trình đơn vị; nhóm cao tuổi/frailty/CKD/gan/đa thuốc. Đánh dấu `[CẦN XÁC NHẬN TẠI ĐƠN VỊ]` khi quyết định phụ thuộc nguồn lực địa phương.

## 5. Cấu trúc đầu ra mặc định — "Phiếu khám EBM" (ẩn danh)

```
## Phiếu khám EBM — [vấn đề] — [mã ẩn danh, vd BN nữ 62t]

1. Câu hỏi lâm sàng — PICO + loại câu hỏi + khung đã dùng
2. Trọng điểm hỏi–khám & CỜ ĐỎ đã loại trừ
3. Chẩn đoán phân biệt + xác suất tiền nghiệm (⚠ = must-not-miss)
4. Quyết định cận lâm sàng — test → LR → hậu nghiệm; lý do làm/không làm
5. Quyết định điều trị — phương án; ARR/NNT/NNH; mức khuyến cáo + nguồn
6. Quyết định cùng bệnh nhân — đã trao đổi gì; lựa chọn của BN
7. Safety-netting + hẹn tái khám + kế hoạch theo dõi
8. Nguồn (tác giả/tổ chức + năm; PMID/DOI / guideline + phiên bản)

⚠️ Cần bác sĩ kiểm chứng trước khi áp dụng lâm sàng.
```

Chỉ giữ các mục liên quan trực tiếp; ca đơn giản có thể gộp mục.

## 6. Biến thể theo loại câu hỏi — tự chọn khung

Tự nhận diện loại câu hỏi và chọn khung phù hợp; nêu rõ một câu: **"Đã dùng khung [X] vì câu hỏi thuộc loại [Y]."**

| Loại câu hỏi | Khung | Thiết kế tốt nhất | Chỉ số điển hình |
|---|---|---|---|
| Điều trị/can thiệp | PICO(T) | RCT / SR-MA | ARR, **NNT**, RR/HR |
| Tác hại/nguyên nhân | PECO | Cohort / bệnh–chứng | **NNH**, RR/OR/HR |
| Chẩn đoán (độ chính xác) | PIRT | Cross-sectional độ chính xác | **Sn/Sp/LR**, hậu nghiệm |
| Tiên lượng | PICOTS | Cohort dọc | HR, nguy cơ tuyệt đối |
| Tầm soát/dự phòng | PICO mở rộng | RCT / SR | giảm biến cố, NNT |
| Tần suất | CoCoPop | Cross-sectional | tỷ lệ (CI) |

Chỉ số đặc thù phải trích đúng nguồn; không tự gán GRADE; không lập số liệu định lượng khi chỉ có đồng thuận/nguyên lý (mô tả định tính + đánh dấu `[CẦN BỔ SUNG]`). Khi chứng cứ không đồng nhất, nêu cả hai chiều.

## 7. Nối tiếp sang skill khác (gợi ý, hỏi bác sĩ trước)

- **Tuân thủ điều trị** (rào cản + lời dặn A5 cho BN) → `tuan-thu-dieu-tri`.
- **Người cao tuổi đa thuốc** (Beers/STOPP-START, deprescribing) → `nguoi-cao-tuoi-da-benh-da-thuoc`.
- **Kế hoạch điều trị chính thức** (3–4 trang) → `treatment-plans`.
- **Lời dặn bệnh nhân A5** in tại phòng khám → công cụ `Loi-dan-benh-nhan/loi-dan-benh-nhan.html`.
- **Bản ghi chuẩn (SOAP/H&P)** → `clinical-reports`.
- **Cập nhật khuyến cáo cả chủ đề + dashboard** → `cap-nhat-chung-cu-y-khoa` / `dark-analyst`.

## 8. Checklist trước khi trả lời

- Đã đặt PICO và nhận diện đúng loại câu hỏi + khung chưa?
- Đã sàng lọc cờ đỏ và liệt kê must-not-miss chưa?
- Đã ước lượng xác suất tiền nghiệm và nêu ngưỡng test/điều trị khi liên quan chưa?
- Test đề nghị có thật sự dịch chuyển quyết định không (LR → hậu nghiệm)?
- Lợi–hại điều trị đã nêu theo số tuyệt đối (ARR/NNT/NNH), giữ nguyên grading của nguồn chưa?
- Đã cá thể hóa cho nhóm đặc biệt và bối cảnh VN, đánh dấu `[CẦN XÁC NHẬN TẠI ĐƠN VỊ]` khi cần chưa?
- Đã nêu safety-netting ("đến cơ sở y tế gần nhất", không "gọi 115") + hẹn tái khám chưa?
- Mọi số liệu/nguồn đều trích đúng, không bịa; ghi nguồn dạng văn bản thường chưa?
- Không có PII; có disclaimer "Cần bác sĩ kiểm chứng" chưa?

## 8b. Chốt kiểm đầu ra 2 LỚP (BẮT BUỘC, ngay trước khi trả lời)
Skill này chạy độc lập (không qua nhạc trưởng) → **tự áp** chốt kiểm 2 lớp như agent `tham-dinh-dau-ra`. Bản chuẩn: `.claude/agents/_CHUAN-CHAT-LUONG-MEDPALM.md` + `_KIEM-DUYET-DOC-LAP.md`.
- **Lớp 1 — LIÊM CHÍNH (R1–R7):** R1 nguồn (PMID/DOI hoặc nhãn thiếu) · R2 KHÔNG PII · R3 không tự "áp dụng cho BN" (dừng Cổng A) · R4 không tự gán GRADE/độ mạnh khi nguồn không cấp · R5 tách độ chắc chứng cứ vs độ mạnh khuyến cáo · R6 nhãn `[CẦN…]` đúng chỗ · R7 disclaimer cuối.
- **Lớp 2 — CHẤT LƯỢNG Med-PaLM (Q1–Q7):** Q1 dễ đọc (đúng đối tượng nhận) · **Q2 đúng đắn** (khớp guideline/đồng thuận — nghi sai → CHUYỂN BÁC SĨ, không tự khẳng định) · Q3 đầy đủ (không sót cờ đỏ/CCĐ/tương tác/chỉnh liều/theo dõi) · Q4 không thiên kiến nhóm · **Q5 nguy cơ hại** (hại nặng không cảnh báo → CHUYỂN BÁC SĨ) · Q6 cập nhật · Q7 thẩm quyền nguồn (cảnh giác tạp chí săn mồi).
- **Còn 🔴 ở lớp nào → SỬA trước khi trả; Q2/Q5 đỏ → nêu cờ "cần bác sĩ phán định".** Đây là tự-kiểm cùng phiên (giảm mù chung, KHÔNG khử thiên lệch) — rào cứng cuối vẫn là bác sĩ.

## 9. Tài nguyên & liêm chính

- Tìm chứng cứ: `clinical-evidence-rag`, `research-lookup`, `paper-lookup` (chỉ nguồn miễn phí: PubMed E-utilities, CSDL mở; KHÔNG dịch vụ trả phí).
- Công cụ lời dặn A5: `Loi-dan-benh-nhan/loi-dan-benh-nhan.html`.
- Nguyên tắc xuyên suốt: ưu tiên số tuyệt đối hơn tương đối · giữ nguyên grading của nguồn · tách "khuyến cáo nguồn / độ chắc chắn / đánh giá vận hành" · không PII · không bịa · mọi đầu ra kết thúc bằng disclaimer.
