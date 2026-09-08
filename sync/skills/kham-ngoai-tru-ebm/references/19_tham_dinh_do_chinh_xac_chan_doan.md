# Thẩm định độ chính xác chẩn đoán (QUADAS-3 v1.2)

*Đọc file này khi ca lâm sàng đang bàn cần thẩm định CHẤT LƯỢNG/ĐỘ TIN CẬY của một nghiên cứu ĐỘ CHÍNH XÁC CHẨN ĐOÁN (diagnostic test accuracy) — bài so sánh index test với reference standard (tiêu chuẩn vàng) — ví dụ câu hỏi "nghiên cứu về test X đáng tin không", "Se/Sp/LR của test này có vững không", "bài chẩn đoán này có sai lệch gì", "QUADAS-3 cho bài này", hoặc trước khi dùng LR của một nghiên cứu để cập nhật xác suất hậu nghiệm cho bệnh nhân (Bước 4a "Cận lâm sàng" của khung 5 bước — xem `SKILL.md` mục 4). KHÁC việc áp LR vào xác suất hậu nghiệm tại giường (file `06_chan_doan_xac_suat_bayes.md`) và KHÁC thẩm định chứng cứ ĐIỀU TRỊ bằng RoB 2/NNT (file `08_tham_dinh_grade_nnt.md`).*

## Mục tiêu

Phán định độ tin cậy của MỘT nghiên cứu độ chính xác chẩn đoán bằng ĐÚNG công cụ của thiết kế chẩn đoán — KHÔNG dùng khung RoB 2/NNT vốn dành cho chứng cứ điều trị — rồi xếp độ chắc chắn của Se/Sp/LR bằng GRADE-cho-test, để bác sĩ quyết dùng/không dùng test đó cho bệnh nhân đang khám.

Nguyên tắc xuyên suốt:
- **Không bịa Se/Sp/LR/AUC/ngưỡng cắt.** Mọi con số trích ĐÚNG từ bài (PMID/DOI) kèm 95%CI khi có; chưa chắc → `[CẦN KIỂM CHỨNG]`. **PPV/NPV phụ thuộc prevalence** — luôn nêu prevalence/bối cảnh khi diễn giải (một PPV ở tầm soát ≠ ở phòng khám chuyên khoa).
- **Dùng ĐÚNG công cụ theo thiết kế chẩn đoán:** QUADAS-3 v1.2 (một test — công cụ MẶC ĐỊNH hiện hành) / QUADAS-C (so sánh 2 test trên cùng đối tượng); QUADAS-2 CHỈ dùng khi tiếp tục một review cũ đã tiền định/khoá công cụ theo QUADAS-2 (tương thích ngược — phải ghi rõ lý do). **KHÔNG** dùng RoB 2 (RCT) hay ROBINS-I. Xếp độ chắc chắn bằng **GRADE cho test**, KHÔNG dùng mô hình GRADE-kết-cục-điều-trị/NNT.
- **Độ chính xác test ≠ lợi ích lâm sàng.** Một test chính xác chỉ hữu ích nếu **đổi quyết định** và cải thiện **kết cục quan trọng với bệnh nhân** — nêu rõ khoảng cách này; test-and-treat lý tưởng cần RCT về test.
- Đây là **ĐỀ XUẤT** cho bác sĩ cân nhắc, không phải phán định cuối cùng. KHÔNG PII.

## 1. Đầu vào tối thiểu

Bài/nghiên cứu chẩn đoán (ưu tiên toàn văn/PDF) + PMID/DOI · **index test** + **reference standard** · quần thể/bối cảnh + **prevalence** · ngưỡng cắt (nếu test liên tục) · bảng 2×2 hoặc Se/Sp/LR + CI. Thiếu toàn văn → nêu rõ chỉ thẩm định được phần có; thiếu số → `[CẦN KIỂM CHỨNG]`, KHÔNG bịa.

## 2. Quy trình

### Bước 0 — Kiểm tiền đề
(a) xác nhận đây là nghiên cứu **độ chính xác chẩn đoán** (index test đối chiếu reference standard) — nếu là RCT về test-and-treat hay điều trị, việc thẩm định đó không thuộc phạm vi file này (xem file `08_tham_dinh_grade_nnt.md` cho chứng cứ ĐIỀU TRỊ bằng RoB 2/NNT); (b) lấy toàn văn khi thiếu — dùng công cụ tra cứu PubMed/Europe PMC sẵn có (toàn văn PMC hoặc metadata bài báo) nếu môi trường có; (c) xác định index test · reference standard · prevalence · ngưỡng cắt.

### 2.1 QUADAS-3 — 6 pha, 4 miền

QUADAS-3 chấm ở mức **TỪNG ƯỚC LƯỢNG** (estimate) cần thẩm định — khác QUADAS-2 vốn chấm gộp ở mức toàn nghiên cứu — qua 6 pha: (1) nêu câu hỏi tổng hợp đủ population/index test/target condition; (2) định nghĩa "ideal test accuracy trial" cho từng câu hỏi; (3) vẽ sơ đồ dòng (flow diagram); (4) chọn TỪNG ước lượng cần đánh giá; (5) chấm 4 miền bằng câu hỏi báo hiệu (signalling questions); (6) phân định tổng thể kèm lý do — ở mức TỪNG ƯỚC LƯỢNG, không gộp mơ hồ ở mức toàn nghiên cứu.

Mỗi miền chấm **nguy cơ sai lệch** theo thang **thấp/cao/không đủ thông tin**; riêng **tính áp dụng CHỈ đánh giá cho 3 miền đầu** — Participants/Index Test/Target Condition — theo đúng thiết kế của công cụ (Whiting PF et al., Ann Intern Med 2026;179:548-555, PMID 41698208, DOI 10.7326/ANNALS-25-02104); miền **"Analysis" KHÔNG có phán định tính áp dụng**. Mỗi miền cần dẫn chứng vị trí trong bài:

- **Participants:** cách tuyển tiến cứu/hồi cứu, liên tiếp/ngẫu nhiên hay chọn lọc, có hạn chế chọn mẫu không? Case-control chẩn đoán (bệnh nặng vs khỏe rõ) → **spectrum/selection bias** làm phóng đại Se/Sp.
- **Index Test:** cách tiến hành/diễn giải có bị mù với target condition không? Ngưỡng cắt **định trước** hay **tối ưu hóa trên chính dữ liệu** (overfit → phóng đại)?
- **Target Condition:** reference standard xác định tình trạng đích có đúng, độc lập và làm mù không? Index có nằm TRONG reference (**incorporation/review bias**)?
- **Analysis:** đủ người tham gia được đưa vào phân tích? Missing data xử lý ra sao? Đơn vị phân tích và cách tính Se/Sp cho từng ước lượng có đúng không?

*(So sánh 2 test trên cùng đối tượng → vẫn dùng **QUADAS-C**, không đổi khi nâng cấp lên QUADAS-3.)*

### 2.2 Diễn giải chỉ số (trích đúng + CI)

Se · Sp · **LR+ = Se/(1−Sp)** · **LR− = (1−Se)/Sp** (LR+ >10 hoặc LR− <0,1 = đổi xác suất mạnh) · PPV/NPV **kèm prevalence** · AUC/C-statistic · DOR. Test liên tục → xét cả **đường ROC** + ngưỡng, KHÔNG chỉ 1 điểm cắt "đẹp".

Sai lệch đặc thù chẩn đoán cần soi khi diễn giải: **spectrum bias · verification/partial verification bias · incorporation bias · review/test-review bias · ngưỡng cắt tối ưu hóa quá mức (overfit)**.

### 2.3 Đối chiếu chuẩn báo cáo STARD 2015

Nêu mục báo cáo còn thiếu (sơ đồ dòng bệnh nhân, cách xử lý kết quả không xác định/indeterminate, khoảng tin cậy…).

### 2.4 GRADE cho test (guidelines 21–22) — gọi công cụ

Chấm mức độ NGHIÊM TRỌNG từng domain (risk of bias qua **QUADAS-3**, indirectness, imprecision, inconsistency, publication bias — 0=không/1=nghiêm trọng/2=rất nghiêm trọng), rồi gọi:

```bash
python medical-ebm-automation/tools/clinical_calc.py grade --design dta \
    --rob <0|1|2> --inconsistency <0|1|2> --indirectness <0|1|2> \
    --imprecision <0|1|2> --publication-bias <0|1|2> [--json]
```

Khởi điểm CAO (không phải thấp như observational — Schünemann HJ et al., "GRADE guidelines: 21 part 1", J Clin Epidemiol 2020;122:129-141, PMID 32060007); công cụ CHỈ tổng hợp domain bạn đã chấm, KHÔNG tự đánh giá QUADAS-3. **Quy về kết cục quan trọng với bệnh nhân:** hệ quả của true+/false+/true−/false− (điều trị đúng/thừa/sót/trấn an sai) — độ chính xác cao KHÔNG tự động = lợi ích. Khung Schünemann đầy đủ (phần 1 risk of bias/indirectness PMID 32060007 + phần 2 inconsistency/imprecision/publication bias PMID 32058069) — xem thêm file `08_tham_dinh_grade_nnt.md` mục 2.2 trong gói này khi cần diễn giải sâu hơn kết quả công cụ.

### 2.5 Tính ứng dụng

Test này đổi quyết định trong bối cảnh của bác sĩ không? Prevalence đích khác nghiên cứu ra sao (đổi PPV/NPV)?

## 3. Mẫu đầu ra (template điền sẵn)

```
NGHIÊN CỨU ĐỘ CHÍNH XÁC CHẨN ĐOÁN — [index test] vs [reference standard] | PMID/DOI
Bối cảnh + prevalence: ____ | Ngưỡng cắt: ____ (định trước/tối ưu hóa?)
| Miền QUADAS-3 | Nguy cơ sai lệch (thấp/cao/không đủ thông tin) | Tính áp dụng | Dẫn chứng (vị trí) |
| Participants |  |  |  |
| Index test |  |  |  |
| Target condition |  |  |  |
| Analysis |  | — (QUADAS-3 không đánh giá tính áp dụng cho miền này) |  |
Chỉ số: Se=[..%(CI)] · Sp=[..%(CI)] · LR+=[..] · LR−=[..] · PPV/NPV@prev=[..] · AUC=[..]
Sai lệch đặc thù nghi ngờ: [spectrum/verification/incorporation/review/overfit ngưỡng]
STARD — mục thiếu: ____
GRADE cho test (độ chắc chắn Se/Sp): [Cao/TB/Thấp/Rất thấp] — lý do hạ bậc: ____
Ý nghĩa lâm sàng (true+/false+/true−/false− → lợi–hại): ____ | Đổi quyết định? ____
Bước tiếp theo: áp LR vào xác suất hậu nghiệm tại giường (file 06_chan_doan_xac_suat_bayes.md)
  · nếu ca có kết cục điều trị đi kèm, thẩm định thêm bằng RoB 2/NNT (file 08_tham_dinh_grade_nnt.md)
```

Kết: **"Cần bác sĩ kiểm chứng."**

## 4. Ví dụ minh họa (ẩn danh, KHÔNG PII)

> *Đầu vào:* "Bài về D-dimer chẩn đoán thuyên tắc phổi — Se/Sp có đáng tin không?" → Bước 0: index = D-dimer, reference = CTPA; **prevalence** cao/thấp? → QUADAS-3 (lưu ý **verification bias** nếu chỉ người D-dimer(+) được chụp CTPA; spectrum bias nếu chọn ca nặng) → Se cao/Sp thấp điển hình → **LR− thấp** (loại trừ tốt khi pretest thấp), LR+ yếu → STARD mục thiếu → GRADE-cho-test (hạ nếu verification bias) → ý nghĩa: hữu ích LOẠI TRỪ ở nhóm pretest thấp/trung bình, không xác nhận. *Mọi Se/Sp/LR chỉ ghi khi có nguồn; chưa chắc → `[CẦN KIỂM CHỨNG]`.*

## 5. Tiêu chí hoàn thành

**Hoàn thành khi:** đã xác định index test + reference standard + prevalence + ngưỡng; QUADAS-3 v1.2 (hoặc QUADAS-C khi so sánh test) đủ 4 miền THEO TỪNG ƯỚC LƯỢNG có dẫn chứng vị trí; chỉ số trích đúng + CI, PPV/NPV kèm prevalence; sai lệch đặc thù đã soi; STARD mục thiếu; GRADE-cho-test + lý do; nêu ý nghĩa lâm sàng (true/false +/− → lợi–hại) + có đổi quyết định không; bước tiếp theo rõ. KHÔNG bịa số; KHÔNG dùng RoB 2/NNT cho bài chẩn đoán.

## 6. Đầu vào hình ảnh (ảnh chụp/scan bảng biểu, ROC)

Môi trường có thể cấp năng lực nhìn ảnh (không phải mọi phiên). Khi bác sĩ đưa ảnh bảng 2×2/đường ROC/bảng kết quả: **mô tả nội dung ĐỌC ĐƯỢC** + nêu phần không chắc → `[CẦN XÁC NHẬN]`; số trích từ ảnh phải được bác sĩ xác nhận; KHÔNG bịa số mờ/cắt; KHÔNG coi ảnh là nguồn thay PMID/DOI. KHÔNG nhận ảnh chứa PII.

## 7. Ranh giới

- CHỈ thẩm định độ chính xác của MỘT nghiên cứu/ước lượng chẩn đoán (QUADAS-3 v1.2; QUADAS-2 tương thích ngược/QUADAS-C khi phù hợp + GRADE-cho-test + STARD).
- **KHÔNG áp Bayes vào ca cụ thể** (pretest→LR→hậu nghiệm→ngưỡng test–treat) — dùng file `06_chan_doan_xac_suat_bayes.md` trong gói này cho việc đó.
- **KHÔNG thẩm định chứng cứ ĐIỀU TRỊ** (RoB 2/NNT) — dùng file `08_tham_dinh_grade_nnt.md` trong gói này cho việc đó.
- **KHÔNG làm tổng quan hệ thống/phân tích gộp** cho câu hỏi chẩn đoán — nằm ngoài phạm vi skill này (xem `SKILL.md` mục 1: dùng skill tổng quan y văn/bản thảo riêng).
- **KHÔNG kê đơn thuốc, KHÔNG tự ghi vào sổ theo dõi bệnh nhân** — đầu ra ở đây là input cho quyết định lâm sàng của bác sĩ, không phải y lệnh cuối cùng.

**Cần bác sĩ kiểm chứng.**
