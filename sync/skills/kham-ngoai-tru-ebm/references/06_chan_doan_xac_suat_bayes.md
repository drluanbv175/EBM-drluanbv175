# Chẩn đoán xác suất (Bayes/LR)

*Đọc file này khi bác sĩ nêu câu hỏi loại **CHẨN ĐOÁN**: "khả năng bệnh X là bao nhiêu", "có nên làm xét nghiệm gì", "xét nghiệm này thay đổi chẩn đoán ra sao", "đủ chắc để điều trị chưa" — cần biến trực giác "ca này khả năng bệnh gì, có cần xét nghiệm không" thành con số ra quyết định được theo định lý Bayes, rồi đối chiếu ngưỡng để khuyên: ngưng truy tìm · làm thêm test · hay điều trị luôn.*

## Nguyên tắc bắt buộc

- **KHÔNG bịa chỉ số xét nghiệm.** Se/Sp/LR và xác suất tiền nghiệm phải đến từ: (a) **guideline/y văn** (PMID/DOI), (b) **quy tắc dự đoán lâm sàng đã thẩm định** (Wells, Centor/McIsaac, HEART, CURB-65… — ghi rõ tên quy tắc/nguồn), hoặc (c) **dịch tễ tại chỗ** do bác sĩ cung cấp. Không có nguồn → ghi `[CẦN NGUỒN/ƯỚC LƯỢNG CỦA BÁC SĨ]`, KHÔNG tự điền số đẹp.
- **Phép toán Bayes là toán học** — tính thẳng; nhưng mọi **đầu vào** (pretest, LR) phải có nguồn.
- **Cờ đỏ ưu tiên hơn xác suất.** Có dấu hiệu nguy hiểm → KHÔNG để bài toán xác suất trì hoãn xử trí an toàn (việc quét cờ đỏ đã xử lý ở bước an toàn riêng của quy trình khám — không lặp lại cơ chế đó ở đây, chỉ nhắc nguyên tắc ưu tiên).
- Kết mọi đầu ra: **"Cần bác sĩ kiểm chứng."** KHÔNG PII.

## 1. Mục tiêu

Định lượng khả năng bệnh và quyết định "không làm gì / test thêm / điều trị luôn" theo ngưỡng.

## 2. Đầu vào tối thiểu

Chẩn đoán đích đang nghi · bối cảnh (tuổi, phơi nhiễm, mùa dịch, yếu tố nguy cơ) · các triệu chứng/dấu hiệu/test đã có hoặc dự kiến · (nếu có) quy tắc dự đoán lâm sàng phù hợp. Thiếu chỉ số test/pretest có nguồn → đánh dấu `[CẦN NGUỒN]`, vẫn nêu khung định tính.

## 3. Quy trình (chỉ số test Se/Sp/LR phải lấy có nguồn — PMID/DOI/guideline)

**Trước khi vào bài toán xác suất:** đã loại trừ cấp cứu/nguy hiểm (bước an toàn riêng của quy trình khám). Nếu nghi cấp cứu, dừng bài toán xác suất, xử trí an toàn trước.

1. **Xác định chẩn đoán đích** + bối cảnh khám.
2. **Xác suất tiền nghiệm (pretest):** ưu tiên quy tắc dự đoán đã thẩm định hoặc tỷ lệ hiện mắc trong y văn (PMID/DOI). **Nếu thang cần tính có công cụ tính điểm xác định sẵn** (hiện có trong `risk_score_calc.py`: CHA₂DS₂-VASc, HAS-BLED, CURB-65, qSOFA, Wells-PE, PERC, Child-Pugh, MELD) → **bắt buộc dùng công cụ đó**, không tự cộng điểm tay. Chỉ tự ước lượng định tính khi thang không có công cụ (vd Centor/HEART) → dùng khoảng (thấp/vừa/cao) + nêu căn cứ.
3. **Áp LR — GỌI CÔNG CỤ, không tự nhẩm:**
   ```bash
   python medical-ebm-automation/tools/clinical_calc.py bayes --pretest <p> --lr <LR> [--json]
   # Chỉ có Se/Sp (chưa có LR trực tiếp):
   python medical-ebm-automation/tools/clinical_calc.py bayes --pretest <p> --se <Se> --sp <Sp> [--negative]
   ```
   Dùng **LR+ khi test dương, LR− khi âm**. Áp tuần tự nhiều test **CHỈ khi độc lập có điều kiện** — nhưng lưu ý: gọi lệnh `bayes` nhiều lần liên tiếp (lấy hậu nghiệm lần trước làm pretest lần sau) **KHÔNG bị CLI tự chặn** dù 2 test không độc lập (hàm `sequential_bayes(..., conditionally_independent=False)` có logic từ chối trong mã nguồn nhưng CHƯA được nối vào CLI — chỉ subcommand `bayes/threshold/nnt/grade` tồn tại). **Phải tự xác nhận tính độc lập có điều kiện TRƯỚC khi gọi `bayes` lần 2 trở lên** và tự nêu rõ giả định này trong đầu ra; nếu không chắc độc lập → không áp tuần tự, chỉ dùng test có LR mạnh nhất hoặc nêu rõ `[CẦN KIỂM CHỨNG tính độc lập]`. Kết quả công cụ trả về là số đã kiểm cho MỖI LẦN GỌI ĐƠN — dùng số đó, không tự nhẩm tay.
4. **Đối chiếu NGƯỠNG (Pauker–Kassirer) — GỌI CÔNG CỤ:**
   ```bash
   python medical-ebm-automation/tools/clinical_calc.py threshold --harm <H> --benefit <B> \
       [--se <Se> --sp <Sp> --test-cost <C>] [--json]
   ```
   `H`/`B` (đơn vị lợi ích/tác hại) LÀ GIÁ TRỊ do bác sĩ ấn định — ghi `[CẦN BÁC SĨ ẤN ĐỊNH]` nếu chưa có, KHÔNG tự bịa. Thiếu `--se/--sp` → công cụ chỉ trả ngưỡng điều trị đơn thuần (không có vùng test). Công cụ có thể báo "KHÔNG có vùng test hợp lệ" khi chi phí/rủi ro xét nghiệm vượt giá trị thông tin — đó là kết luận hợp lệ, không phải lỗi.
5. **Kết luận hành động:**
   - (a) dưới ngưỡng test → trấn an + safety-netting;
   - (b) giữa hai ngưỡng → test nào đáng làm nhất (LR mạnh, ít hại, sẵn có) + nó dịch xác suất ra sao;
   - (c) trên ngưỡng điều trị → điều trị luôn — kèm đánh giá độ mạnh khuyến cáo/NNT-NNH của điều trị đó và rà an toàn kê đơn (tương tác/CCĐ/chỉnh liều) trước khi thống nhất quyết định với bệnh nhân. Đây là các bước tiếp theo trong khung 5 bước EBM, nằm ngoài phạm vi tính toán của file này.

## 🌳 Suy luận đa nhánh (Tree-of-Thoughts) — bắt buộc khi có ≥2 chẩn đoán cạnh tranh

> Khung tường minh để KHÔNG khóa sớm vào một chẩn đoán (chống *anchoring / premature closure*).
> **Trước tiên:** có dấu hiệu cấp cứu → xử trí an toàn trước, KHÔNG để cây giả thuyết trì hoãn xử trí (xử lý ở bước an toàn riêng của quy trình khám).
> (a) **SINH NHÁNH:** liệt kê 2–3 chẩn đoán khả dĩ nhất, gồm ≥1 "không-được-bỏ-sót" nếu hợp bệnh cảnh.
> (b) **CHẤM NHÁNH:** mỗi nhánh = pretest (nguồn/quy tắc) → gọi CÔNG CỤ `clinical_calc.py bayes` ở §3 để tính **hậu nghiệm** (đầu vào phải có nguồn — không tự nhẩm tay cho từng nhánh).
> (c) **CẮT TỈA:** loại nhánh hậu nghiệm rất thấp **VÀ** không nguy hiểm; ghi 1 dòng lý do. KHÔNG cắt nhánh nguy hiểm chỉ vì xác suất thấp nếu hậu quả bỏ sót lớn — giữ để chủ động loại trừ.
> (d) **QUAY LUI (backtrack):** mỗi test mới → cập nhật hậu nghiệm các nhánh; nếu kết quả ĐẢO thứ hạng → mở lại nhánh đã cắt, ghi "đảo nhánh do [bằng chứng]".
> (e) **Chốt:** nhánh dẫn đầu + (các) nhánh còn phải loại trừ → đưa vào quyết định ngưỡng test–treat ở §3 (mục Quy trình).
>
> | Nhánh chẩn đoán | Pretest (nguồn) | LR áp (nguồn) | Hậu nghiệm | Giữ/Cắt (lý do) |
> |---|---|---|---|---|
>
> KHÔNG bịa Se/Sp/LR/pretest — thiếu → `[CẦN NGUỒN]`.

## 4. Mẫu đầu ra (template điền sẵn)

```
🚑 Cờ đỏ: [không/có → xử trí trước]
Chẩn đoán đích: ____ | Pretest = [..%] (nguồn/quy tắc: ____)
BẢNG BAYES:
| Test | Kết quả | LR áp dụng (nguồn) | Hậu nghiệm |
Hai ngưỡng: test=[..%] · điều trị=[..%] (căn cứ/giả định: ____)
Hậu nghiệm rơi vào: [dưới test / giữa / trên điều trị]
→ KHUYẾN NGHỊ HÀNH ĐỘNG: [trấn an+safety-netting / test ___ / điều trị]
Độ tin cậy chỉ số (BẮT BUỘC nhận xét): [QUADAS-2 cho nghiên cứu nguồn Se/Sp/LR — có / CẦN NGUỒN] | tham số thiếu: [CẦN NGUỒN]
```
Kết: **"Cần bác sĩ kiểm chứng."**

## 5. Ví dụ minh họa (ẩn danh, KHÔNG PII)

> *Đầu vào:* "Người lớn đau họng, sốt, không ho — khả năng viêm họng liên cầu, có cần test/điều trị?" *Vận hành:* dùng **quy tắc Centor/McIsaac** ước pretest (ghi nguồn quy tắc) → nếu có test nhanh kháng nguyên, áp **LR+/LR− từ y văn (ghi PMID/DOI)** → hậu nghiệm → đối chiếu ngưỡng. *Mọi LR/Se/Sp chỉ ghi khi có nguồn; chưa có → `[CẦN NGUỒN]`, không chế số.*

## 6. Tiêu chí hoàn thành + safety-netting

**Hoàn thành khi:** cờ đỏ đã loại; pretest có căn cứ; LR có nguồn (hoặc đánh dấu thiếu); hậu nghiệm tính đúng; hai ngưỡng (định lượng/định tính) + khuyến nghị hành động đã nêu rõ. **Safety-netting:** vùng "giữa hai ngưỡng" hoặc trấn an luôn kèm dấu hiệu quay lại + mốc thời gian tái khám.

## 7. Nguyên tắc nền & disclaimer

Cờ đỏ > xác suất; không bịa Se/Sp/LR/pretest; KHÔNG PII; dừng ở bước khuyến nghị hành động — bác sĩ mới là người quyết định áp dụng cho bệnh nhân. Kết: **"Cần bác sĩ kiểm chứng."**

## 📷 Đầu vào hình ảnh (X-quang/ECG/ảnh lâm sàng)

Khi bác sĩ đưa ảnh X-quang/ECG/ảnh tổn thương: chỉ **MÔ TẢ** dấu hiệu quan sát được ở mức hỗ trợ và **cần bác sĩ xác nhận**; **KHÔNG tự đưa chẩn đoán hình ảnh thay chuyên khoa** (chẩn đoán hình ảnh/tim mạch…). Nghi cấp cứu trên ảnh → ưu tiên an toàn, đề nghị hội chẩn chuyên khoa, KHÔNG để việc đọc ảnh làm trì hoãn xử trí. KHÔNG dùng ảnh thay tiêu chuẩn vàng; KHÔNG bịa dấu hiệu; KHÔNG nhận ảnh chứa PII (che định danh trước).

## Ranh giới nội dung (những gì KHÔNG thuộc phạm vi file này)

- Chỉ số test (Se/Sp/LR) dùng ở đây phải đã có nguồn (PMID/DOI) sẵn — việc **tìm/tra cứu** chứng cứ gốc là công việc khác, không nằm trong file này.
- **Đọc–mô tả có hệ thống một panel xét nghiệm/ECG** là việc khác; nội dung này chỉ NHẬN kết quả đã diễn giải để áp Bayes (pretest→LR→hậu nghiệm→ngưỡng test–treat), KHÔNG tự đọc/gom panel.
- File này **KHÔNG hướng dẫn kê đơn, KHÔNG chấm GRADE chứng cứ điều trị, KHÔNG ghi sổ theo dõi bệnh án** — đó là các bước khác trong khung 5 bước EBM.
- File này **KHÔNG thẩm định CHẤT LƯỢNG một nghiên cứu độ chính xác chẩn đoán** (QUADAS-2/QUADAS-C/GRADE-cho-test) — đó là việc khác với việc ÁP Se/Sp/LR đã có sẵn mà file này hướng dẫn.

**Cần bác sĩ kiểm chứng.**
