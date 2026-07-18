# Thẩm định GRADE + NNT/NNH

*Đọc file này khi ca lâm sàng đang bàn cần: chấm độ tin cậy chứng cứ (GRADE) cho một/nhiều nghiên cứu đã có, tính ARR/NNT/NNH để lượng hóa lợi ích–tác hại, đánh giá nguy cơ sai lệch (RoB 2 / ROBINS-I / ROBINS-E / AMSTAR-2 / QUADAS-2) theo đúng thiết kế nghiên cứu, hoặc dựng khối Evidence-to-Decision (EtD) trước khi đề xuất áp dụng cho bệnh nhân — ví dụ câu hỏi "bài này đáng tin không", "NNT/NNH bao nhiêu", "nguy cơ sai lệch của nghiên cứu này thế nào", "GRADE mức nào", "kết quả có ý nghĩa thống kê hay ý nghĩa lâm sàng".*

## Mục tiêu

Từ (các) nghiên cứu đã có, chấm chất lượng chứng cứ theo từng kết cục quan trọng và lượng hóa lợi/hại (NNT/NNH) để bác sĩ ra quyết định. Nguyên tắc xuyên suốt: **giữ nguyên grading gốc của nguồn**; chỉ hạ/giữ bậc theo 5 yếu tố GRADE, KHÔNG tự nâng hạng vô căn cứ; **dùng ĐÚNG công cụ nguy cơ sai lệch theo thiết kế**; **tách độ chắc chắn CHỨNG CỨ với độ mạnh KHUYẾN CÁO**; mỗi phán định kèm lý do + nguồn (PMID/DOI); số liệu trích ĐÚNG nguồn, không bịa.

## 1. Đầu vào tối thiểu

Câu hỏi PICO + (các) nguồn nghiên cứu đã có sẵn từ bước tìm kiếm chứng cứ trước đó (tốt nhất kèm PMID/DOI) · thiết kế từng nghiên cứu · các kết cục quan trọng với bệnh nhân + số liệu hiệu ứng (RR/OR/HR + CI, biến cố/nhóm). Thiếu số liệu để tính NNT → ghi "không tính được", KHÔNG bịa nguy cơ nền.

## 2. Quy trình

**Bước kiểm tiền đề nguồn:** xác nhận có đủ nguồn phân giải được (PMID/DOI) và đúng câu hỏi; thiếu/không phân giải được → nêu rõ cần tìm thêm nguồn, đánh dấu **PARTIAL**, KHÔNG chấm "ép". Cần đọc TOÀN VĂN để chấm RoB 2/GRADE → lấy qua công cụ tra cứu PubMed/PMC sẵn có (toàn văn PMC hoặc metadata bài báo) nếu môi trường có; không có toàn văn → chỉ chấm phần có, nêu rõ giới hạn.

### 2.1 Phân loại thiết kế + gán ĐÚNG công cụ nguy cơ sai lệch

Đây là đầu vào cho domain "risk of bias" của GRADE — KHÔNG dùng RoB 2 cho nghiên cứu không phải RCT.

| Thiết kế nguồn | Công cụ RoB |
|---|---|
| RCT | **RoB 2** |
| Quan sát về CAN THIỆP (NRSI/cohort điều trị) | **ROBINS-I** — ưu tiên bản **V2** (vẫn là DRAFT, bản sửa đổi mới nhất 20/11/2025 theo riskofbias.info, hiện CHỈ phủ thiết kế cohort/theo dõi); quan sát khác cohort dùng ROBINS-I gốc (Sterne JA et al., BMJ 2016;355:i4919) |
| Quan sát về PHƠI NHIỄM/nguyên nhân | **ROBINS-E** |
| Tổng quan hệ thống | **AMSTAR-2** |
| Độ chính xác chẩn đoán | **QUADAS-2** |

### 2.2 GRADE theo từng kết cục quan trọng — GỌI CÔNG CỤ (không tự cộng/trừ bậc bằng tay)

Trước hết chọn **biến thể GRADE đúng loại câu hỏi**:

- **Can thiệp/điều trị** → GRADE chuẩn.
- **Độ chính xác chẩn đoán/test** → GRADE guidelines 21 phần 1+2 (phần 1 — risk of bias/indirectness: Schünemann HJ et al., J Clin Epidemiol 2020;122:129-141, PMID 32060007; phần 2 — inconsistency/imprecision/publication bias/domain khác: Schünemann HJ et al., J Clin Epidemiol 2020;122:142-152, PMID 32058069) — cần chấm CẢ 2 phần.
- **Tiên lượng** → GRADE cho prognosis (Iorio A et al., BMJ 2015;350:h870, PMID 25775931).
- **Thích ứng guideline có sẵn** → GRADE-ADOLOPMENT (Schünemann HJ et al., J Clin Epidemiol 2017;81:101-110, PMID 27713072).

Sau đó chấm mức độ NGHIÊM TRỌNG từng domain từ nguồn (0 = không có vấn đề, 1 = nghiêm trọng, 2 = rất nghiêm trọng) — tiêu chí VẬN HÀNH tối thiểu từng domain (xem đầy đủ ở PMID đã dẫn cho từng domain, đây chỉ là tóm tắt điều hướng, KHÔNG thay việc đọc nguồn):

- **Risk of bias** (PMID 21247734): tỷ lệ nghiên cứu RoB cao/một số quan ngại nghiêm trọng trong tổng trọng số bằng chứng — đa số RCT RoB thấp → 0; một phần đáng kể RoB cao ảnh hưởng ước lượng → 1; đa số/toàn bộ RoB cao → 2.
- **Inconsistency** (PMID 21803546): I² lớn + khoảng tin cậy các nghiên cứu KHÔNG chồng lấp + không giải thích được nguồn không đồng nhất (khác thiết kế/liều/quần thể) → 1-2 tùy mức độ; I² thấp + CI chồng lấp tốt → 0.
- **Indirectness** (PMID 21802903): quần thể/can thiệp/kết cục/so sánh trong nguồn KHÁC câu hỏi PICO đang hỏi (ví dụ kết cục thay thế thay vì kết cục lâm sàng thật, quần thể khác đáng kể) → 1-2 tùy mức lệch; khớp trực tiếp → 0.
- **Imprecision** (PMID 21839614): khoảng tin cậy hiệu ứng RỘNG bao trùm cả "có lợi" và "có hại" (băng qua ngưỡng quyết định lâm sàng), hoặc cỡ mẫu/biến cố dưới ngưỡng thông tin tối ưu (optimal information size) → 1-2; CI hẹp, đủ biến cố → 0.
- **Publication bias** (PMID 21802904): nghi ngờ mạnh (funnel plot bất đối xứng, chỉ có nghiên cứu nhỏ dương tính công bố, tài trợ công nghiệp + kết quả luôn thuận lợi) → 1-2; không có dấu hiệu → 0.
- **Rating up** (PMID 21802902, cho nghiên cứu quan sát): hiệu ứng LỚN nhất quán (RR>2 hoặc <0.5, không giải thích được bằng nhiễu tồn dư) → +1; RẤT lớn (RR>5 hoặc <0.2) → +2; có gradient liều-đáp ứng rõ → +1; mọi nhiễu tồn dư hợp lý đều làm GIẢM hiệu ứng quan sát được (nghĩa là hiệu ứng thật có thể còn lớn hơn) → +1.

Gọi công cụ tính (chỉ tổng hợp domain đã chấm theo thuật toán GRADE chính thức — công cụ KHÔNG tự đánh giá RoB/inconsistency/...; đó vẫn là việc đọc toàn văn):

```bash
python medical-ebm-automation/tools/clinical_calc.py grade --design <rct|observational|dta> \
    --rob <0|1|2> --inconsistency <0|1|2> --indirectness <0|1|2> \
    --imprecision <0|1|2> --publication-bias <0|1|2> \
    [--large-effect <0|1|2> --dose-response <0|1> --plausible-confounding-reduces-effect <0|1>] \
    [--json]
```

**Câu hỏi chẩn đoán/test** → dùng `--design dta`: khởi điểm CAO (giống RCT, KHÔNG phải thấp như "observational") — xác minh qua Schünemann HJ et al., "GRADE guidelines: 21 part 1", J Clin Epidemiol 2020;122:129-141, PMID 32060007 (nghiên cứu cắt ngang/đoàn hệ so sánh trực tiếp index test với reference standard "start as high certainty"). `risk_of_bias` chấm bằng **QUADAS-2** (không phải RoB 2); KHÔNG áp yếu tố nâng bậc quan sát (large_effect/dose_response/confounding — GRADE-DTA không định nghĩa các yếu tố này). Trình bày kèm khung đầy đủ Schünemann 21 phần 1+2 (PMID 32060007 + 32058069) khi cần diễn giải sâu hơn kết quả công cụ.

### 2.3 Lượng hóa — GỌI CÔNG CỤ

Trích RR/OR/HR + CI từ nguồn (không tự tính), rồi tính ARR, NNT/NNH + 95%CI:

```bash
# Có RR + CI + nguy cơ nền (CER):
python medical-ebm-automation/tools/clinical_calc.py nnt --cer <CER> --rr <RR> \
    --rr-ci-lower <lo> --rr-ci-upper <hi> [--json]
# Có OR thay vì RR (công cụ tự chuyển OR→RR theo Zhang–Yu 1998):
python medical-ebm-automation/tools/clinical_calc.py nnt --cer <CER> --or <OR> \
    --or-ci-lower <lo> --or-ci-upper <hi> [--json]
# Có số liệu thô 2 nhóm:
python medical-ebm-automation/tools/clinical_calc.py nnt --cer <CER> --eer <EER> \
    --n-control <n> --n-experimental <n> [--json]
```

Khi CI của ARR vắt qua 0, công cụ tự báo dạng chuẩn Altman "NNTB … → vô cực → NNTH …" — dùng NGUYÊN VĂN, không tự diễn giải khác. Thiếu dữ liệu → công cụ báo lỗi rõ (không bịa). Phân biệt **ý nghĩa thống kê vs ý nghĩa lâm sàng (MCID)**.

### 2.4 Cân bằng lợi–hại

Ở mức quần thể; nêu rõ nhóm bệnh nhân hưởng lợi nhiều nhất.

### 2.5 Khối Evidence-to-Decision (EtD)

Vấn đề · lợi/hại · giá trị-ưu tiên bệnh nhân · cân bằng · **khuyến nghị có điều kiện** (mạnh/yếu, thuận/nghịch) — tách rõ khỏi mức chứng cứ.

```
══════════════════════════════════════════════════════════
EVIDENCE-TO-DECISION (GRADE EtD) — CHỜ BÁC SĨ DUYỆT
══════════════════════════════════════════════════════════
Vấn đề: ____ | Quần thể: ____ | Bối cảnh: ____

LỢI ÍCH (chứng cứ):
  Kết cục chính: ____ | GRADE: ____ | Nguồn: PMID/DOI
  ARR = CER − EER = ___% | NNT = 1/ARR = ___ (95% CI: ___)
  Kết cục phụ quan trọng: ____

TÁC HẠI & AN TOÀN:
  Sự kiện bất lợi: ____ | NNH = ___ | Độ nghiêm trọng: ____
  Chống chỉ định đặc biệt: ____

GIÁ TRỊ & ƯU TIÊN BỆNH NHÂN:
  [Phần lớn ưu tiên lợi ích / Lo ngại tác hại / Không chắc / Khác biệt lớn]

CÂN BẰNG LỢI ÍCH–TÁC HẠI:
  ☐ Lợi ích vượt trội rõ  ☐ Tác hại vượt trội  ☐ Cân bằng  ☐ Không chắc

4 TIÊU CHÍ EtD BỔ SUNG (đủ bộ 12 tiêu chí GRADE EtD chính thức — Alonso-Coello P et al.,
BMJ 2016;353:i2016/i2089, PMID 27353417/27365494 — CHỈ điền khi quyết định có liên quan chi
phí đáng kể/bất bình đẳng tiếp cận; bỏ qua với quyết định lâm sàng thường quy chi phí thấp để
giữ công cụ gọn nhẹ tại điểm khám):
  Nguồn lực cần thiết: ☐ Thấp ☐ Trung bình ☐ Cao ☐ Không đánh giá (chi phí thấp/thường quy)
  Công bằng tiếp cận: ☐ Không ảnh hưởng ☐ Có thể làm rộng khoảng cách BHYT/chi trả — nêu rõ
  Tính chấp nhận được (với BN/nhân viên y tế): ☐ Cao ☐ Không chắc ☐ Thấp
  Tính khả thi tại đơn vị: ☐ Sẵn có ngay ☐ Cần chuẩn bị thêm ☐ Không khả thi tại đây

KHUYẾN NGHỊ CÓ ĐIỀU KIỆN:
  ☐ Mạnh THUẬN  ☐ Yếu/Điều kiện THUẬN  ☐ Yếu/Điều kiện NGHỊCH  ☐ Mạnh NGHỊCH
  Lý do: ____

→ Đây là ĐỀ XUẤT CÓ ĐIỀU KIỆN — chờ BÁC SĨ DUYỆT trước khi áp dụng cho bệnh nhân.
══════════════════════════════════════════════════════════
```

> **Lưu ý sai lệch tinh vi ngoài khung RoB/GRADE chuẩn:** khi nghi ngờ nguồn có ngụy biện logic, thiên kiến báo cáo tinh vi (HARKing, p-hacking), hoặc lỗi diễn giải thống kê (Simpson's paradox, base rate neglect) làm sai lệch số liệu ARR/NNT đang dùng — cân nhắc kỹ trước khi chốt GRADE/NNT. Đây là bổ trợ, KHÔNG thay khung RoB/GRADE chính ở trên.

## 3. Mẫu đầu ra (template điền sẵn)

```
Trạng thái nguồn: [ĐỦ/PARTIAL]
BẢNG GRADE theo outcome:
| Outcome | Thiết kế | Hạ/nâng bậc (lý do) | Chất lượng | Nguồn (PMID/DOI) |
LƯỢNG HÓA: RR/OR/HR=[..] (CI ..) | nguy cơ nền=[..,nguồn] | ARR=[..] | NNT=[.. (CI)] / NNH=[..]
   (thiếu dữ liệu → "không tính được")
Ý nghĩa: thống kê=[..] | lâm sàng/MCID=[..]
KHỐI EtD: vấn đề · lợi · hại · giá trị BN · cân bằng · khuyến nghị [mạnh/yếu, thuận/nghịch]
→ Đây là khuyến nghị có điều kiện, không phải lệnh điều trị.
```

## 4. Ví dụ minh họa (ẩn danh, KHÔNG PII)

> *Đầu vào:* 1 SR/MA về một thuốc dự phòng biến cố tim mạch. *Vận hành:* phân loại MA → chấm GRADE cho kết cục "biến cố tim mạch lớn" (hạ bậc nếu CI rộng/không nhất quán) → trích RR + CI **đúng từ bài** → tính ARR/NNT **chỉ khi bài cung cấp nguy cơ nền** (nếu không → "không tính được") → EtD. *Mọi con số trích đúng nguồn; không có nguồn → `[CẦN KIỂM CHỨNG]`.*

## 5. Tiêu chí hoàn thành

Mỗi outcome quan trọng có hàng GRADE + lý do + nguồn; lượng hóa (hoặc nêu rõ không tính được); tách ý nghĩa thống kê/lâm sàng; có khối EtD với khuyến nghị **có điều kiện**. Không tự gán mức nếu nguồn không phân hạng (`gradeLevel:'na'`).

## 6. Đầu vào hình ảnh (ảnh chụp/scan tài liệu)

Khi bác sĩ đưa ảnh chụp/scan bảng biểu, forest plot, bảng kết quả hay trang PDF (nếu môi trường hỗ trợ đọc ảnh): **mô tả nội dung ĐỌC ĐƯỢC** (số liệu, nhãn, chú thích) và **nêu rõ phần nào không đọc chắc** → gắn `[CẦN XÁC NHẬN]`. Số liệu trích từ ảnh phải được **bác sĩ xác nhận** trước khi dùng làm căn cứ; **KHÔNG bịa** số bị mờ/cắt; **KHÔNG** coi ảnh là nguồn đã kiểm chứng thay PMID/DOI. KHÔNG nhận ảnh chứa PII (che/loại định danh trước khi đưa vào).

## 7. Ranh giới

- KHÔNG tự bịa nguồn mới ngoài danh sách đã có sẵn cho ca này; thiếu nguồn → nói rõ và nêu cần tìm thêm trước khi chấm.
- KHÔNG kê đơn thuốc, KHÔNG tự ghi vào sổ theo dõi bệnh nhân — đầu ra ở đây là input cho quyết định lâm sàng của bác sĩ, không phải lệnh điều trị.
- Nếu trọng tâm câu hỏi chỉ là chất lượng PHƯƠNG PHÁP của một nghiên cứu độ chính xác chẩn đoán (Se/Sp/LR, QUADAS-2) mà chưa cần chuyển thành GRADE/quyết định lâm sàng đầy đủ, có thể dừng ở đánh giá QUADAS-2 + trình bày Se/Sp/LR, không nhất thiết phải đi hết quy trình GRADE-DTA.
- Nếu khuyến cáo nền không có bản guideline mới nhất để đối chiếu, nêu rõ giới hạn này và gắn nhãn `[CẦN CẬP NHẬT GUIDELINE]`, không tự suy đoán mức khuyến cáo.

**Cần bác sĩ kiểm chứng.**
