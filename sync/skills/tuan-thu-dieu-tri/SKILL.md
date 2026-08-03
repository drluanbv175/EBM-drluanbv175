---
name: tuan-thu-dieu-tri
description: "Sử dụng skill này khi cần đánh giá và cải thiện TUÂN THỦ ĐIỀU TRỊ (medication & treatment adherence) cho bệnh nhân ngoại trú. Kích hoạt khi bác sĩ nói \"bệnh nhân không tuân thủ\", \"hay quên uống thuốc\", \"bỏ thuốc/tự ngưng thuốc\", \"uống không đều\", \"kém tuân thủ\", \"adherence/compliance\", \"làm sao để bệnh nhân uống thuốc đúng\", \"bệnh nhân không tái khám\", hoặc cần soạn lời dặn/kế hoạch giúp bệnh nhân theo đúng điều trị. Quy trình: phân loại kiểu không tuân thủ (không khởi trị / thực hiện kém / không duy trì) · tìm rào cản theo 5 nhóm WHO · chọn can thiệp có cấu trúc (5A, phỏng vấn tạo động lực, đơn giản hóa phác đồ, teach-back, nhắc lịch) · SOẠN NỘI DUNG LỜI DẶN đúng schema công cụ in A5 sẵn có · lập kế hoạch theo dõi tuân thủ. Đây là công cụ HỖ TRỢ, không thay phán đoán lâm sàng."
metadata:
  version: 1.0.0
---

# Skill: Hỗ trợ tuân thủ điều trị (Treatment Adherence)

## 1. Phạm vi sử dụng

Kích hoạt khi vấn đề là bệnh nhân không theo đúng điều trị, ví dụ:

- "Bệnh nhân THA cứ quên uống thuốc, làm sao?"
- "BN đái tháo đường tự ngưng metformin vì sợ hại thận."
- "Người bệnh không tái khám đúng hẹn."
- "Soạn lời dặn giúp bệnh nhân uống thuốc đúng cho ca này."
- Tiếp nối sau một ca khám (`kham-ngoai-tru-ebm`) cần phần hỗ trợ tuân thủ.

Không dùng skill này để: ra quyết định chẩn đoán/điều trị (→ `kham-ngoai-tru-ebm`); rà soát đa thuốc người cao tuổi (→ `nguoi-cao-tuoi-da-benh-da-thuoc`); làm tài liệu đào tạo/poster (→ `dao-tao-slide-tai-lieu-y-khoa`).

> Ngôn ngữ hiện đại dùng **"adherence/tuân thủ"** (hợp tác) thay cho "compliance/tuân lệnh". Mục tiêu là **gỡ rào cản, không đổ lỗi** và tôn trọng tự chủ của bệnh nhân.

## 2. Mục tiêu

Biến "bệnh nhân không tuân thủ" thành vấn đề chẩn đoán được và can thiệp được, với các yêu cầu:

1. Xác định ĐÚNG kiểu không tuân thủ (khởi trị / thực hiện / duy trì) trước khi khuyên.
2. Tìm rào cản GỐC theo 5 nhóm yếu tố của WHO; phân biệt không tuân thủ có chủ đích vs không chủ đích.
3. Chọn can thiệp **theo rào cản, đa thành phần, cá thể hóa** — không áp lời khuyên chung.
4. Xuất **lời dặn dễ hiểu cho bệnh nhân** đúng schema công cụ in A5 sẵn có, và **kế hoạch theo dõi** cho bác sĩ.
5. **Liêm chính:** trích số liệu tuân thủ/hiệu quả can thiệp đúng nguồn (tác giả/tổ chức + năm; PMID/DOI hoặc guideline + phiên bản); không phóng đại, không bịa.
6. **Không PII:** không lưu/tạo thông tin định danh; ô tên/ngày trên tờ in chỉ để bác sĩ điền tay khi in, không nhập vào hệ thống.
7. Trả lời bằng **tiếng Việt** (tên thuốc theo INN); mọi đầu ra lâm sàng kết thúc bằng disclaimer **"⚠️ Cần bác sĩ kiểm chứng trước khi áp dụng lâm sàng."**

## 3. Chế độ đầu ra

### Chế độ mặc định: Chẩn đoán rào cản + kế hoạch
Đi đủ quy trình (mục 4) và xuất kế hoạch tuân thủ (mục 5.2). Soạn lời dặn A5 (mục 5.1) khi có chỉ định thuốc/điều trị cụ thể.

### Chế độ nhanh
Kích hoạt khi bác sĩ nói "gợi ý nhanh", "đang khám". Trả lời gọn: kiểu không tuân thủ nghi ngờ · 1–2 rào cản khả dĩ nhất · can thiệp ưu tiên · 1 câu lời dặn cốt lõi cho BN.

### Chế độ soạn lời dặn A5
Kích hoạt khi bác sĩ nói "soạn lời dặn", "làm tờ dặn", "đưa vào app lời dặn". Tập trung xuất khối nội dung đúng schema (mục 5.1) để dán vào công cụ.

## 4. Quy trình bắt buộc

Thu thập bối cảnh ẩn danh tối thiểu: bệnh, thuốc/điều trị đang dùng, biểu hiện không tuân thủ (quên? tự ngưng? chưa mua thuốc?), hoàn cảnh (chi phí, hỗ trợ gia đình, tác dụng phụ). Không hỏi thông tin định danh.

### Bước 1 — PHÂN LOẠI kiểu không tuân thủ (ABC taxonomy)
Theo Vrijens 2012 (ABC taxonomy, *Br J Clin Pharmacol*):
1. **Không khởi trị (non-initiation):** kê đơn nhưng chưa từng dùng liều nào.
2. **Thực hiện kém (poor implementation):** dùng sai liều/giờ/cách, quên, bỏ liều.
3. **Không duy trì (non-persistence):** đã dùng rồi tự ngưng sớm.

Mỗi kiểu có rào cản & can thiệp khác nhau.

### Bước 2 — TÌM RÀO CẢN (5 nhóm yếu tố của WHO)
Theo WHO 2003 (*Adherence to Long-Term Therapies*):
- **Hệ thống y tế / quan hệ thầy thuốc:** khó tái khám, chi phí, thiếu giải thích, thiếu theo dõi.
- **Tình trạng bệnh:** không triệu chứng (THA, rối loạn lipid), bệnh tâm thần, lệ thuộc.
- **Điều trị:** phác đồ phức tạp, nhiều lần/ngày, tác dụng phụ, thời gian dài, đường dùng khó.
- **Yếu tố bệnh nhân:** quên, niềm tin/lo sợ về thuốc, hiểu sai, trầm cảm, kỳ vọng.
- **Kinh tế–xã hội:** chi phí, hỗ trợ gia đình, health literacy, văn hóa, đi lại.

Phân biệt **CÓ CHỦ ĐÍCH** (intentional — niềm tin/tác dụng phụ/chi phí → cần đối thoại, điều chỉnh phác đồ) vs **KHÔNG CHỦ ĐÍCH** (unintentional — quên/nhầm → cần nhắc lịch, đơn giản hóa). Có thể dùng thang tự báo cáo đã kiểm định để sàng lọc (nêu nguồn, giới hạn); không suy diễn điểm số khi chưa có dữ liệu thật.

### Bước 3 — CHỌN CAN THIỆP dựa chứng cứ
Không có "viên đạn bạc"; can thiệp đa thành phần, cá thể hóa theo rào cản hiệu quả hơn lời khuyên đơn lẻ (Cochrane — Nieuwlaat 2014). Bản đồ rào cản → can thiệp:

| Rào cản gốc | Can thiệp ưu tiên |
|---|---|
| Quên, phác đồ phức tạp | Đơn giản hóa: giảm số lần/ngày, viên phối hợp liều cố định, gắn với thói quen; hộp chia thuốc; nhắc lịch (chuông/app/người nhà) |
| Niềm tin/lo sợ, hiểu sai | Giáo dục ngắn + **teach-back** (BN nhắc lại); làm rõ "tại sao cần", "nếu ngưng thì sao"; xử lý kỳ thị |
| Tác dụng phụ | Báo trước & cách xử trí; chỉnh liều/đổi thuốc; hẹn đánh giá lại sớm |
| Bệnh không triệu chứng | Giải thích nguy cơ dài hạn bằng số tự nhiên; mục tiêu đo được BN tự theo dõi (HA, HbA1c) |
| Động lực thấp / mâu thuẫn | **Phỏng vấn tạo động lực (MI):** đồng cảm, khơi "change talk", tránh tranh luận |
| Chi phí | Chọn thuốc rẻ/đúng danh mục BHYT, kê đủ ngày, gộp lần lấy thuốc |
| Trầm cảm / sức khỏe tâm thần | Tầm soát & điều trị đồng thời (rào cản tuân thủ mạnh) |

Khung tổ chức buổi tư vấn — **5A:** *Assess · Advise · Agree · Assist · Arrange*. Luôn shared decision-making (phối hợp `kham-ngoai-tru-ebm`).

### Bước 4 — Thích ứng ngoại trú Việt Nam
Xét: danh mục BHYT & chi phí thực; sẵn có viên phối hợp liều cố định; vai trò người nhà/y tế cơ sở; khả năng tái khám/đi lại; phác đồ đơn vị. Đánh dấu `[CẦN XÁC NHẬN TẠI ĐƠN VỊ]` khi phụ thuộc nguồn lực địa phương.

## 5. Cấu trúc đầu ra mặc định

### 5.1 — Lời dặn cho bệnh nhân (nối công cụ A5)

Bác sĩ có sẵn công cụ in lời dặn khổ **A5**: `Loi-dan-benh-nhan/loi-dan-benh-nhan.html` (HTML offline; gõ từ khóa → chọn → IN). Skill này **chuẩn bị nội dung đúng schema** rồi hướng dẫn đưa vào — KHÔNG sửa HTML/CSS.

Schema một mục (đưa vào khối `const DATA=[...]` để đồng bộ mọi máy, hoặc dán qua nút ✎ "Sửa"):

```js
{
  id: 'tuanthu-<slug>',                 // duy nhất, không dấu
  group: 'Dặn dò chung',                // hoặc đúng chuyên khoa của bệnh
  title: 'Cách uống thuốc đúng — <bệnh>',
  tags: ['tuan thu','uong thuoc','<khong dau>'],   // tìm không dấu, có xếp hạng
  sections: [
    { h: 'Vì sao phải uống đều', items: ['Lý do bằng lợi ích cụ thể, câu ngắn'] },
    { h: 'Uống thế nào cho đúng', items: ['Gắn với mốc trong ngày','Cách không quên: hộp chia thuốc / chuông'] },
    { h: 'Nếu quên một liều', items: ['Hướng xử trí an toàn theo loại thuốc (ghi nguồn)'] }
  ],
  warn: ['Dấu hiệu cần đến cơ sở y tế gần nhất']    // KHÔNG ghi "gọi 115"
}
```

Quy tắc nội dung (khớp công cụ A5 hiện hành):
- Câu ngắn, mức đọc hiểu lớp 6; nhấn **lý do + cách nhớ + xử trí khi quên**.
- Cảnh báo dùng cụm **"đến cơ sở y tế gần nhất"**, không dùng "gọi 115".
- Mỗi bệnh ≈ 1 mặt A5 (công cụ tự co chữ); nội dung chung, **không PII**.
- Lời dặn *cách uống thuốc* tách khỏi *toa thuốc* (toa in riêng).
- Sửa khối `const DATA` đồng bộ mọi máy; sửa qua nút ✎ chỉ lưu localStorage máy đó. Sau khi thêm mục, xuất lại bộ PDF nếu cần bản in tĩnh.

### 5.2 — Kế hoạch theo dõi tuân thủ (cho bác sĩ, ẩn danh)

```
## Kế hoạch tuân thủ — <bệnh> — <mã ẩn danh>
- Kiểu không tuân thủ: [khởi trị / thực hiện / duy trì]
- Rào cản gốc (WHO): […]; có chủ đích? [có/không]
- Can thiệp đã chọn (theo 5A): […]
- Công cụ giao BN: [lời dặn A5 id=…, hộp chia thuốc, nhắc lịch…]
- Chỉ số theo dõi: [tỷ lệ lấy thuốc / đếm viên / tự báo cáo / kết cục đại diện như HA-HbA1c]
- Hẹn đánh giá lại: [mốc thời gian] — tiêu chí điều chỉnh
- Nguồn: [tác giả/tổ chức + năm; PMID/DOI / guideline]

⚠️ Cần bác sĩ kiểm chứng trước khi áp dụng lâm sàng.
```

## 6. Biến thể theo bối cảnh

- **Không khởi trị:** ưu tiên gỡ rào cản tiếp cận (chi phí, hiểu nhầm "chưa cần"), xác nhận BN đã mua/bắt đầu thuốc; theo dõi lần lấy thuốc đầu.
- **Thực hiện kém (quên):** trọng tâm công cụ nhắc + đơn giản hóa phác đồ + teach-back; ít cần đối thoại niềm tin.
- **Không duy trì (tự ngưng):** khai thác lý do ngưng (tác dụng phụ? thấy "khỏe rồi"? chi phí?) → MI + điều chỉnh phác đồ + tái khám sớm.
- **Bệnh mạn không triệu chứng (THA, lipid, loãng xương):** nhấn nguy cơ dài hạn bằng số tự nhiên + mục tiêu tự theo dõi.
- **Người cao tuổi đa thuốc:** giảm gánh nặng thuốc tăng tuân thủ → chuyển `nguoi-cao-tuoi-da-benh-da-thuoc` (deprescribing, đơn giản hóa).

## 7. Nối tiếp sang skill khác

- **Khám ca / quyết định điều trị** → `kham-ngoai-tru-ebm`.
- **Người cao tuổi đa thuốc** (đơn giản hóa, deprescribing) → `nguoi-cao-tuoi-da-benh-da-thuoc`.
- **Kế hoạch điều trị chính thức** → `treatment-plans`.
- **Tài liệu giáo dục bệnh nhân/đào tạo** (poster, infographic) → `dao-tao-slide-tai-lieu-y-khoa`.
- Tìm chứng cứ về can thiệp tuân thủ → `clinical-evidence-rag`, `research-lookup`, `paper-lookup`.

## 8. Checklist trước khi trả lời

- Đã phân loại đúng kiểu không tuân thủ (ABC) chưa?
- Đã tìm rào cản gốc theo 5 nhóm WHO và phân biệt có/không chủ đích chưa?
- Can thiệp đã chọn có khớp rào cản và đa thành phần không (không phải lời khuyên chung)?
- Lời dặn A5 (nếu có): đúng schema, dùng "đến cơ sở y tế gần nhất", tách khỏi toa, không PII chưa?
- Kế hoạch theo dõi có chỉ số tuân thủ + mốc đánh giá lại chưa?
- Số liệu trích đúng nguồn, không phóng đại chưa? Có disclaimer "Cần bác sĩ kiểm chứng" chưa?
- Đã đánh dấu `[CẦN XÁC NHẬN TẠI ĐƠN VỊ]` khi phụ thuộc BHYT/nguồn lực địa phương chưa?

## 8b. Chốt kiểm đầu ra 2 LỚP (trước khi trả lời)
Tự áp như agent `tham-dinh-dau-ra` (skill chạy độc lập): **Lớp 1 LIÊM CHÍNH** R1–R7 (nguồn · KHÔNG PII · không vượt Cổng A · không tự gán mức · tách 2 trục · nhãn `[CẦN…]` · disclaimer) + **Lớp 2 CHẤT LƯỢNG Med-PaLM** Q1–Q7 (đặc biệt **Q1 dễ đọc** cho bản phát tay bệnh nhân · Q3 đầy đủ · Q5 nguy cơ hại · Q7 thẩm quyền nguồn; `.claude/agents/_CHUAN-CHAT-LUONG-MEDPALM.md`). Còn 🔴 → sửa trước khi trả; **Q2/Q5 đỏ → cờ chuyển bác sĩ**. Tự-kiểm cùng phiên — rào cứng cuối vẫn là bác sĩ.

## 9. Tài nguyên & liêm chính

- Công cụ lời dặn A5: `Loi-dan-benh-nhan/loi-dan-benh-nhan.html` (schema mục: `{id, group, title, tags, sections, warn}`).
- Khung tham chiếu: ABC taxonomy (Vrijens 2012) · 5 nhóm yếu tố WHO 2003 · Cochrane Nieuwlaat 2014 · 5A · phỏng vấn tạo động lực (MI). Trích đúng nguồn, không bịa PMID.
- Nguyên tắc xuyên suốt: gỡ rào cản không đổ lỗi · cá thể hóa · tôn trọng tự chủ · không PII · mọi đầu ra kết thúc bằng disclaimer.
