# 07 — Mô hình câu hỏi & khung thay thế cho cập nhật thực hành

Mục tiêu: trước khi tổng hợp chứng cứ, **tự nhận diện loại câu hỏi lâm sàng** rồi **chọn đúng khung đóng câu hỏi** (không mặc định mọi câu hỏi đều là PICO). Mỗi khung kéo theo *thiết kế nghiên cứu tốt nhất*, *công cụ thẩm định* và *chỉ số hiệu lực* riêng. Tất cả vẫn render vào **Evidence Workbench**.

> Luôn nêu một câu ở đầu phần tổng hợp: **"Đã dùng khung [X] vì câu hỏi thuộc loại [Y]."**

---

## 1. Bộ chọn khung theo loại câu hỏi

| Loại câu hỏi | Khung khuyến nghị | Thành phần chính | Thiết kế tốt nhất | Công cụ thẩm định | Chỉ số hiệu lực điển hình |
|---|---|---|---|---|---|
| **Điều trị / can thiệp** | **PICO(T)(S)** | P · I · C · O (+Time, +Setting/Study design) | RCT, SR-MA | RoB 2, AMSTAR-2, GRADE | RR, OR, HR, ARR, **NNT** |
| **Tác hại / nguyên nhân** | **PECO** | P · Phơi nhiễm (Exposure) · C · O | Cohort, case-control | ROBINS-I, GRADE | RR, OR, HR, **NNH** |
| **Chẩn đoán (độ chính xác)** | **PIRT** (Index–Reference–Target) | P · Index test · Chuẩn tham chiếu (=C) · Bệnh đích (O) | Cross-sectional độ chính xác | **QUADAS-2**, chuẩn báo cáo STARD | **Sn, Sp, LR+, LR−**, PPV/NPV, AUC |
| **Tiên lượng** | **PICOTS tiên lượng / PROGRESS** | P · Yếu tố tiên lượng · (so sánh) · Kết cục · Thời gian | Cohort dọc | QUIPS; mô hình: **PROBAST/TRIPOD** | HR, C-statistic, hiệu chuẩn |
| **Tầm soát / dự phòng** | **PICO mở rộng** | P · Test/biện pháp · C · Kết cục lâm sàng (không chỉ thay thế) | RCT, SR | GRADE, khung USPSTF | giảm tử vong/biến cố, NNT, tác hại tầm soát |
| **Tần suất / dịch tễ** | **CoCoPop** | Condition · Context · Population | Cross-sectional | JBI prevalence | tỷ lệ hiện mắc/mới mắc (CI) |
| **Trải nghiệm / định tính** | **SPIDER** (hoặc PICo) | Sample · Phenomenon of Interest · Design · Evaluation · Research type | Nghiên cứu định tính | CASP qualitative, ENTREQ | chủ đề (theme), trích dẫn |
| **Tổ chức / dịch vụ / chính sách** | **ECLIPSE** | Expectation · Client group · Location · Impact · Professionals · Service | Hỗn hợp | AGREE II (nếu guideline) | chỉ số dịch vụ |
| **Kinh tế y tế** | **PICO + chi phí** | + ICER, chi phí, hiệu quả | Đánh giá kinh tế | CHEERS | ICER, chi phí/QALY |

Lưu ý: PICO vẫn là **mặc định** cho câu hỏi điều trị/can thiệp (đa số câu hỏi ngoại trú). Chỉ chuyển khung khi câu hỏi thực sự thuộc loại khác.

---

## 2. Cách điền từng khung vào Evidence Workbench

Template Evidence Workbench dùng 4 ô P/I/C/O làm khung hiển thị chung. Với khung **không phải PICO**, dùng 2 field tùy chọn của mỗi item:

- `frame`: nhãn khung hiển thị trên panel (vd `'Chẩn đoán'`, `'Tiên lượng'`, `'PECO'`).
- `frameLabels`: đổi tên 4 ô để đúng ngữ nghĩa khung. Ví dụ ánh xạ:

```js
// Chẩn đoán (PIRT)
frame:'Chẩn đoán',
frameLabels:{P:'P', I:'Index test', C:'Chuẩn vàng', O:'Độ chính xác'},
pico:{ P:['Người nghi bệnh X','match'],
       I:['Test chỉ số (cut-off…)','match'],
       C:['Tiêu chuẩn tham chiếu','match'],
       O:['Sn/Sp/LR đúng như nguồn','match'] }

// Tiên lượng (PROGRESS)
frame:'Tiên lượng',
frameLabels:{P:'P', I:'Yếu tố TL', C:'So sánh', O:'Kết cục·Thời gian'},

// Tác hại (PECO)
frame:'PECO',
frameLabels:{P:'P', I:'Phơi nhiễm', C:'C', O:'O'},

// Tần suất (CoCoPop) — dùng ô mô tả
frame:'CoCoPop',
frameLabels:{P:'Population', I:'Condition', C:'Context', O:'Tỷ lệ'}
```

Nếu **không** đặt `frame`/`frameLabels`, panel hiển thị mặc định P/I/C/O như cũ (tương thích ngược).

---

## 3. Mô hình tổng hợp bổ trợ (áp dụng SAU khi đã đóng khung)

Đây là các "mô hình thay thế/bổ sung có giá trị cho cập nhật thực hành" — dùng phối hợp với khung câu hỏi:

1. **Phân tầng nguồn 6S** (chọn nguồn theo bậc): Systems → Summaries (guideline, UpToDate-like) → Synopses of syntheses → Syntheses (SR-MA) → Synopses of studies → Studies. *Ưu tiên bậc cao nhất sẵn có.*
2. **Cân lợi ích – tác hại (NNT/NNH)**: khi có số liệu nhị phân, trình bày ARR, **NNT** cho lợi ích và **NNH** cho tác hại — trích/diễn giải đúng nguồn, ghi mốc thời gian.
3. **GRADE Evidence-to-Decision (EtD) rút gọn** — khi cần ra một khuyến cáo: (a) vấn đề ưu tiên? (b) lợi ích mong muốn; (c) tác hại không mong muốn; (d) độ chắc chắn chứng cứ; (e) giá trị/ưu tiên của người bệnh; (f) cân bằng lợi–hại; (g) nguồn lực/chi phí; (h) công bằng; (i) khả năng chấp nhận; (j) khả thi → **quyết định + độ mạnh**.
4. **Bảng Tóm tắt phát hiện (Summary of Findings) rút gọn**: kết cục · số sự kiện/đối chứng · hiệu số tương đối · hiệu số tuyệt đối · độ chắc chắn.
5. **Tam giác liêm chính** (bắt buộc, xuyên suốt): tách rõ (a) khuyến cáo/kết quả của nguồn; (b) độ chắc chắn theo nguồn; (c) đánh giá vận hành của người tổng hợp.
6. **Phân loại tác động thực hành** (đã có): Áp dụng ngay / Cân nhắc chọn lọc / Chưa đủ thay đổi.

---

## 4. Công cụ thẩm định khớp với thiết kế (chọn đúng, không chấm thừa)

| Thiết kế nguồn | Công cụ |
|---|---|
| Guideline | **AGREE II** |
| Systematic review / meta-analysis | **AMSTAR-2** |
| RCT | **RoB 2** (Cochrane Risk of Bias 2) |
| Quan sát (cohort/case-control) | **ROBINS-I** / Newcastle-Ottawa |
| Nghiên cứu độ chính xác chẩn đoán | **QUADAS-2** |
| Nghiên cứu/Mô hình tiên lượng | **QUIPS** / **PROBAST** |
| Tổng thể độ chắc chắn theo kết cục | **GRADE** (giữ nguyên grading của nguồn nếu có) |

Mức độ thẩm định **tương xứng nhu cầu** (xem `references/02`): tra cứu nhanh chỉ kiểm tính chính thức/hiện hành/quần thể/áp dụng; khuyến cáo sửa phác đồ hoặc tài liệu học thuật mới chấm có cấu trúc.

---

## 5. Quy tắc liêm chính khi dùng khung thay thế

- Chỉ số đặc thù phải **trích đúng nguồn**: Sn/Sp/LR (chẩn đoán); HR/C-statistic (tiên lượng); RR/OR/ARR/NNT/NNH (điều trị/tác hại); tỷ lệ (tần suất). Không tự tính suy diễn gây sai lệch.
- **Không tự gán GRADE** hay đổi hệ phân hạng của nguồn.
- Khi chứng cứ không đồng nhất, nêu cả hai chiều.
- Khi chỉ có đồng thuận/nguyên lý (không số liệu), mô tả định tính và đánh dấu `[CẦN BỔ SUNG]`.
- Ghi nguồn sạch (tác giả/tổ chức + năm + tạp chí) + Vancouver/NLM; kèm PMID/DOI; disclaimer "Cần bác sĩ kiểm chứng"; không PII.

---

## 6. Ví dụ nhận diện nhanh

- "Metformin có gây thiếu B12 không?" → **PECO** (phơi nhiễm metformin).
- "HbA1c có chẩn đoán ĐTĐ chính xác không so với đường huyết đói?" → **PIRT/chẩn đoán** (QUADAS-2, Sn/Sp).
- "Microalbumin niệu có tiên lượng biến cố thận ở ĐTĐ?" → **Tiên lượng/PROGRESS** (HR).
- "Tỷ lệ bệnh thần kinh ngoại biên ở bệnh nhân ĐTĐ tại ngoại trú?" → **CoCoPop**.
- "Trải nghiệm tuân thủ insulin của người bệnh?" → **SPIDER/định tính**.
- "Nên tổ chức phòng khám bàn chân ĐTĐ thế nào?" → **ECLIPSE**.
- "SGLT2i có giảm nhập viện suy tim ở HFrEF?" → **PICO** (mặc định).
