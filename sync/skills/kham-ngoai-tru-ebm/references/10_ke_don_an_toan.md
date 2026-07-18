# Rà soát an toàn kê đơn

*Đọc file này khi ca lâm sàng đang tư vấn có liên quan đến kê đơn/rà đơn: "đơn này an toàn không", "thuốc có đánh nhau/tương tác không", "chỉnh liều theo thận/gan", "cần theo dõi xét nghiệm gì khi dùng thuốc này", "có nên bớt/ngưng thuốc không", đa thuốc ở người cao tuổi (Beers/STOPP-START), hoặc bất kỳ lúc nào chuẩn bị đề xuất/đồng thuận một thuốc mới trong kế hoạch điều trị.*

## Chặn an toàn — kiểm TRƯỚC mọi việc khác, không ngoại lệ

**Chống chỉ định hoặc tương tác mức 🔴** (ví dụ: NSAID + suy tim, MAOI → SSRI, Aspirin cho trẻ sốt virus, thuốc thải qua thận khi eGFR thấp) → **BẮT BUỘC gắn cờ CHẶN ngay đầu output** + yêu cầu xử lý/thay thế có nguồn TRƯỚC khi đơn tới tay bệnh nhân. **KHÔNG bỏ qua dù bị hối** ("kê liều thấp thôi", "dặn uống sau ăn"). Đây chỉ là ĐỀ XUẤT — bác sĩ điều trị quyết định; KHÔNG tự sửa đơn thay bác sĩ.

**Chặn an toàn tâm thần:** trước khi đề xuất/đồng thuận **hypnotic mạnh** (benzodiazepine, "Z-drug" liều cao) trong bối cảnh **mất ngủ + cảm giác thất bại/vô vọng** hoặc **bệnh nhân đòi thuốc ngủ mạnh** → BẮT BUỘC xác nhận **đã sàng lọc ý tưởng tự sát** (PHQ-9 mục 9 / C-SSRS rút gọn). **Chưa sàng lọc → CHẶN**, yêu cầu bác sĩ thực hiện sàng lọc trước khi kê. Nếu sàng lọc (+): KHÔNG kê benzo/Z-drug **số lượng lớn**, chuyển/hội chẩn **tâm thần**, hạn chế tiếp cận phương tiện, chỉ kê lượng nhỏ nếu buộc dùng.

**Chặn an toàn thai kỳ:** trước khi đề xuất/đồng thuận thuốc **nhóm gây quái thai/độc thai** (danh mục đầy đủ ở mục 3.4 bên dưới) cho **phụ nữ tuổi sinh đẻ / không loại trừ mang thai** → BẮT BUỘC xác nhận **đã hỏi & ghi nhận khả năng có thai + biện pháp tránh thai**. **Chưa xác nhận → CHẶN**, hỏi trước khi kê. Có thai/không loại trừ → KHÔNG kê thuốc nhóm đó: đề xuất **thay thế an toàn có nguồn**, hoặc **hoãn + xác nhận (thử thai)**; thuốc có chương trình bắt buộc (isotretinoin/thalidomide) chỉ dùng theo **tránh thai kép + thử thai định kỳ**. Mức nguy cơ/thay thế CHỈ nêu khi có nguồn (FDA-PLLR·ACOG·LactMed·guideline từng thuốc); chưa chắc → `[CẦN KIỂM CHỨNG]`.

## 7 mục rà soát

| Mục | Nội dung |
|-----|----------|
| M1 | Đối chiếu thuốc đầy đủ; gắn cờ nhóm nguy cơ cao (chống đông · hạ đường huyết · độc thận · QT · an thần) |
| M2 | Tương tác thuốc–thuốc + thuốc–bệnh (🔴🟠🟡) — nguồn nhãn thuốc/openFDA/PMID |
| M3 | Chỉnh liều theo eGFR/suy gan: nêu theo nguồn hoặc `[CẦN KIỂM CHỨNG]` (KHÔNG bịa số) |
| M4 | Người cao tuổi đa thuốc: Beers AGS 2023 + STOPP/START v3 |
| M5 | Nhóm đặc biệt: thai kỳ/cho con bú — đối chiếu LactMed/FDA-PLLR |
| M6 | Trùng nhóm/prescribing cascade + cơ hội deprescribing |
| M7 | Xuất bảng 🔴🟠🟡 + xét nghiệm theo dõi + mốc; kháng sinh → WHO AWaRe |

> **Tra/đối chiếu mã thuốc:** khi cần đối chiếu mã ATC↔NDC↔RxNorm (ví dụ chuẩn hóa tên thuốc giữa các hệ thống, hoặc nhóm ATC để rà trùng nhóm ở M6), có thể dùng công cụ tra mã dược (InnerMap/CrossMap, offline). CHỈ dùng để TRA MÃ/chuẩn hóa định danh — **KHÔNG** dùng làm nguồn cho mức độ nặng tương tác/ngưỡng chỉnh liều (nguồn đó vẫn PHẢI là nhãn thuốc/openFDA/guideline/PMID như quy tắc dưới).

## Nguyên tắc nguồn & không bịa số

KHÔNG PII (chỉ tuổi/chức năng cơ quan/chẩn đoán) · **mỗi cảnh báo kèm nguồn** (nhãn thuốc/openFDA/guideline + PMID/DOI khi có) · **liều/ngưỡng CHỈ nêu khi xác minh được nguồn; không chắc → `[CẦN KIỂM CHỨNG]`, KHÔNG chế số**. **Nguồn cảnh báo kê đơn = nhãn thuốc/openFDA + guideline + PubMed (PMID/DOI)** — KHÔNG dựa **ChEMBL** cho mức nặng tương tác/ngưỡng chỉnh liều: ChEMBL là dữ liệu dược lý tiền lâm sàng (IC50/ADMET dự đoán), chỉ dùng để làm giàu thông tin cơ chế phía nghiên cứu, KHÔNG phải chỗ dựa cho quyết định an toàn kê đơn lâm sàng.

## 1. Đầu vào tối thiểu

Danh sách **thuốc dự kiến + đang dùng** (kể cả OTC/thực phẩm chức năng) · tuổi · **eGFR/creatinin** và **chức năng gan** nếu liên quan · cân nặng (thuốc theo cân) · bệnh nền · dị ứng thuốc · thai kỳ/cho con bú. Thiếu dữ kiện then chốt (ví dụ creatinin để chỉnh liều) → nêu **giả định** + đánh dấu `[CẦN BỔ SUNG]`, không tự suy số.

## 2. Quy trình

**Bước 0 — Đối chiếu thuốc (medication reconciliation) + cờ đỏ thuốc:** lập danh sách thuốc đầy đủ; gắn cờ ngay nhóm nguy cơ cao (chống đông, hạ đường huyết, độc thận, QT, an thần ở người già/lái xe).

### 2.1 Tương tác thuốc–thuốc và thuốc–bệnh
Rà cặp có ý nghĩa lâm sàng (thuốc–thuốc) và chống chỉ định theo bệnh nền (thuốc–bệnh).

### 2.2 Chỉnh liều theo cơ quan
Dựa eGFR/chức năng gan; nêu liều khuyến cáo **theo nguồn** hoặc thuốc cần tránh — không có nguồn → `[CẦN KIỂM CHỨNG]`.

### 2.3 Người cao tuổi đa thuốc
Đối chiếu **Beers (AGS 2023)** và **STOPP/START (v3)**; gắn cờ thuốc nên tránh/nên cân nhắc thêm.

### 2.4 Nhóm đặc biệt — thai kỳ / cho con bú
Rà nếu phụ nữ tuổi sinh đẻ, kể cả khi chưa khẳng định có thai: đối chiếu mỗi thuốc với chống chỉ định/thận trọng theo thai kỳ + tam cá nguyệt và theo cho con bú. Danh mục **thuốc nguy cơ cao điển hình** (đã công nhận rộng — vẫn PHẢI đối chiếu nhãn thuốc/nguồn trước khi loại trừ, KHÔNG tự khẳng định mức từ trí nhớ):

- **Gây quái thai mạnh / thường chống chỉ định:** ACEi & ARB (đặc biệt tam cá nguyệt 2–3) · warfarin · valproate & nhiều thuốc chống động kinh (carbamazepine, phenytoin, topiramate) · isotretinoin/retinoid · methotrexate · mycophenolate · thalidomide · lithium (dị tật Ebstein) · misoprostol · methimazole (tam cá nguyệt 1 → cân nhắc PTU) · **vắc-xin sống**.
- **Thận trọng theo giai đoạn:** NSAID (tránh tam cá nguyệt 3 — đóng ống động mạch sớm) · statin (theo nhãn) · tetracycline/fluoroquinolone/aminoglycoside · một số kháng đông.
- **Cho con bú:** rà riêng (ví dụ thuốc độc tế bào, amiodarone, lithium…) — đối chiếu **LactMed (NIH)**.
- Mọi mức nguy cơ + lựa chọn thay thế CHỈ nêu khi có nguồn (nhãn thuốc/openFDA/guideline/LactMed); chưa chắc → `[CẦN KIỂM CHỨNG]`. KHÔNG bịa.

### 2.5 Trùng nhóm / kê thác (prescribing cascade)
Rà trùng nhóm dược lý và cơ hội **giảm gánh thuốc (deprescribing)**.

### 2.6 Cảnh báo đặc biệt + theo dõi
QT kéo dài, chảy máu, hạ đường huyết, té ngã, hạ Na/K, độc thận; nêu **xét nghiệm theo dõi** cần làm và mốc.

### 2.7 Kháng sinh (nếu có)
Đánh giá có thực sự cần không; ưu tiên hợp lý; cân nhắc **WHO AWaRe**.

## 3. Mẫu đầu ra (phân tầng theo mức nặng)

```
Đối chiếu thuốc: [n thuốc] | Dữ kiện thiếu: [CẦN BỔ SUNG: ___]
🔴 NGHIÊM TRỌNG/CHỐNG CHỈ ĐỊNH — xử lý trước khi kê
   • [vấn đề] · cơ chế · ĐỀ XUẤT thay thế · NGUỒN
🟠 THẬN TRỌNG/CHỈNH LIỀU
   • [vấn đề] · liều theo nguồn hoặc [CẦN KIỂM CHỨNG] · cách theo dõi · NGUỒN
🟡 LƯU Ý/THEO DÕI
   • [tác dụng phụ cần dặn] · xét nghiệm theo dõi + mốc
Nhóm đặc biệt — thai kỳ/cho con bú (nếu phụ nữ tuổi sinh đẻ): [đã rà: có/không · thuốc cần tránh/đổi · nguồn]
Cơ hội deprescribing: [thuốc/lý do]   | Kháng sinh: [cần/không + AWaRe]
```

Kết: **"Đây là rà soát hỗ trợ; quyết định kê đơn thuộc về bác sĩ điều trị. Cần bác sĩ kiểm chứng."**

## 4. Ví dụ minh họa (ẩn danh, KHÔNG PII)

> *Đầu vào:* "Người ~75, đang warfarin, nay định thêm một NSAID đường uống cho đau khớp; eGFR ~35."
> *Đầu ra:* 🔴 NSAID + warfarin → tăng nguy cơ xuất huyết tiêu hóa (cộng hưởng) + NSAID độc thận khi eGFR thấp + Beers khuyến cáo tránh NSAID kéo dài ở người cao tuổi/CKD → ĐỀ XUẤT: ưu tiên giảm đau thay thế (ví dụ paracetamol/giảm đau tại chỗ) **[liều cụ thể theo nguồn]**, nếu buộc dùng thì bàn lại nguy cơ + bảo vệ dạ dày + theo dõi. *Liều/ngưỡng cụ thể chỉ ghi khi có nguồn; nếu không → `[CẦN KIỂM CHỨNG]`.*

## 5. Tiêu chí hoàn thành + safety-netting

**Hoàn thành khi:** đã đối chiếu đủ thuốc; mỗi cảnh báo có mức + cơ chế + đề xuất + nguồn (hoặc `[CẦN KIỂM CHỨNG]`); nêu xét nghiệm theo dõi + mốc; nêu cơ hội deprescribing.

**Safety-netting:** dặn dấu hiệu ngộ độc/tác dụng phụ nặng cần ngừng thuốc + đi khám ngay; mốc tái khám/xét nghiệm.

## 6. Ranh giới

KHÔNG tự đổi đơn; KHÔNG lưu thông tin bệnh nhân. Thiếu dữ liệu (cân nặng, creatinin…) → nêu giả định + `[CẦN BỔ SUNG]`. Quyết định kê đơn thuộc bác sĩ điều trị.

---

**Cần bác sĩ kiểm chứng.**
