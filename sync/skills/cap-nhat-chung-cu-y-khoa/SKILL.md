---
name: cap-nhat-chung-cu-y-khoa
description: "Sử dụng skill này khi bác sĩ yêu cầu cập nhật chứng cứ hoặc khuyến cáo hiện hành cho MỘT vấn đề lâm sàng cụ thể. Mỗi cập nhật phải kèm Web Dashboard độc lập theo mô hình MẶC ĐỊNH \"Evidence Workbench\" (bố cục 3 cột: bộ lọc · bảng điểm chứng cứ · panel thẩm định; có Clinical Quick View và tab Chuẩn & chất lượng) nếu môi trường hỗ trợ tạo file; đây không phải hệ thống giám sát định kỳ hoặc Dashboard Master mặc định."
metadata:
  version: 1.48.6
---

# Skill: Cập nhật chứng cứ y khoa theo vấn đề lâm sàng cụ thể

## 1. Phạm vi sử dụng

Kích hoạt khi người dùng hỏi một vấn đề cụ thể, ví dụ:

- “Cập nhật EBM điều trị suy tim EF bảo tồn hiện nay.”
- “Hen phế quản 2026: chẩn đoán và điều trị theo mức chứng cứ.”
- “Duloxetine có vai trò gì trong đau thần kinh ở người cao tuổi?”
- “Cập nhật an toàn của finasteride/dutasteride.”
- “Kháng sinh viêm phổi cộng đồng ngoại trú: lựa chọn và thời gian hiện hành.”
- “CHA₂DS₂-VASc / HAS-BLED / FRAX còn dùng thế nào?”
- “Guideline này có đáng tin để áp dụng tại phòng khám Việt Nam không?”

Không tự động biến một câu hỏi cụ thể thành:

- báo cáo giám sát tuần/tháng/quý;
- bản ghi Dashboard Master hoặc WebApp Master;
- tác vụ định kỳ;
- mã ID quản trị.

**Web Dashboard lâm sàng độc lập theo vấn đề cụ thể là đầu ra bắt buộc** khi môi trường hỗ trợ tạo file — nhưng đây là sản phẩm BỔ SUNG để tra cứu lại, KHÔNG thay cho câu trả lời văn xuôi đầy đủ luôn được viết trực tiếp trong khung chat trước (xem mục 3). Web Dashboard này chỉ giúp tra cứu nhanh nội dung vừa tổng hợp, không đồng nghĩa nội dung đã được duyệt vào Master. Chỉ tạo bản ghi quản trị, PATCH, CỔNG A/CỔNG B hoặc đồng bộ Master khi người dùng yêu cầu riêng.

## 2. Mục tiêu

Đưa ra câu trả lời EBM có thể dùng trong thực hành lâm sàng, với các yêu cầu:

1. Xác định khuyến cáo hiện hành và thay đổi có ý nghĩa thực hành.
2. Tìm rộng theo source universe, rồi ưu tiên nguồn gốc chính thức, registry nguồn uy tín lõi và bằng chứng chất lượng cao.
3. Tách rõ: khuyến cáo của nguồn, độ chắc chắn chứng cứ, đánh giá vận hành của người tổng hợp.
4. Cá thể hóa cho ngoại trú Việt Nam, đặc biệt người cao tuổi, đa bệnh lý, đa thuốc, CKD, bệnh gan, bệnh tim mạch và đái tháo đường.
5. Nêu rõ điều cần làm, điều không nên làm, theo dõi và khi nào chuyển tuyến/cấp cứu.
6. Không bịa nguồn, số liệu, liều, cut-off, phân hạng, DOI hoặc tài liệu tham khảo.
7. Khi câu hỏi là về hiệu quả/an toàn của một can thiệp, cấu trúc hóa chứng cứ theo PICO và nêu hiệu số (point estimate) đúng như nguồn báo cáo (xem mục 5B và `references/06-pico-va-trich-dan.md`).
8. Ghi nguồn sạch trong văn bản (tác giả/tổ chức + năm + tạp chí) và liệt kê tham khảo theo Vancouver/NLM; KHÔNG chèn thẻ markup trích dẫn thô hay ký tự kỹ thuật vào câu trả lời (xem mục 5B).
9. Trước khi gọi một nội dung là “áp dụng trực tiếp”, phải qua cổng direct-practice readiness: đúng nguồn, còn hiện hành, độ tin cậy cao, truy nguyên PMID/DOI/URL chính thức, không PII, không còn nhãn `[CẦN...]`, và có doctor/master gate. Đọc `references/12-direct-practice-readiness.md`.

## 3. Chế độ đầu ra

**Bất kể chế độ nào và bất kể có tạo thêm Web Dashboard/bộ năm export (mục 5A/5D) hay không, câu trả lời văn xuôi theo đúng khung mục của chế độ đó LUÔN được viết ĐẦY ĐỦ TRỰC TIẾP trong khung chat trước tiên.** Web Dashboard/file là sản phẩm BỔ SUNG để tra cứu lại sau — không bao giờ thay thế, rút gọn hay hoãn câu trả lời trong hội thoại (xem thêm mục 5A "Mục đích").

### Chế độ mặc định: Cập nhật thực hành có trọng tâm

Dùng khi bác sĩ hỏi một bệnh/vấn đề/thuốc mà không quy định độ dài. Trả lời đủ để ra quyết định ngoại trú, không biến thành chuyên luận dài. Dùng khung 8 mục ở mục 5 ("Cấu trúc đầu ra mặc định").

### Chế độ nhanh

Kích hoạt khi người dùng nói “tóm tắt nhanh”, “điểm cần làm”, “tra nhanh”, hoặc cần áp dụng ngay cho ca bệnh. Dùng ĐÚNG khung mục của `templates/mau-cap-nhat-nhanh.md` (Làm ngay · Không nên làm/Chưa nên thay đổi · Cờ đỏ và chuyển tuyến · Nhóm cần thận trọng · Điểm mới đã xác minh · Nguồn chủ chốt) — không tự ý đổi tên mục hay thêm/bớt mục giữa các lần trả lời.

### Chế độ chuyên sâu

Kích hoạt khi người dùng yêu cầu “đầy đủ”, “chuyên sâu”, “đề cương”, “bài giảng”, “theo guideline”, hoặc cần phục vụ đào tạo/nghiên cứu. **Mẫu chốt (khung mục bắt buộc, dùng ĐÚNG NGUYÊN VĂN, không tự đổi thứ tự/tên mục giữa các lần trả lời) là `templates/mau-cap-nhat-chuyen-sau.md`** (11 mục: Tóm tắt thực hành nhanh · Điểm mới có thể thay đổi xử trí · Chẩn đoán và chẩn đoán phân biệt · Phân tầng nguy cơ; nhập viện/chuyển tuyến · Điều trị không dùng thuốc và dùng thuốc · Bảng điều trị · Điều trị theo nhóm đặc biệt · Thực hành không còn phù hợp hoặc chưa đủ để thay đổi · Áp dụng tại Việt Nam · Thẩm định nguồn chính khi cần · Tài liệu tham khảo Vancouver/NLM). Đây là khung DUY NHẤT cho chế độ chuyên sâu — không dùng khung 8 mục của mục 5 (khung đó dành cho Chế độ mặc định) cho chế độ này, để tránh mỗi lần trả lời một cấu trúc khác nhau.

### Chế độ PICO (chứng cứ tốt nhất theo can thiệp)

Kích hoạt khi người dùng yêu cầu “PICO”, “chứng cứ tốt nhất”, “best evidence”, “hiệu quả điều trị”, “so sánh can thiệp”, hoặc khi câu hỏi cốt lõi là một can thiệp có hiệu quả/an toàn hay không cho một quần thể. Trình bày mỗi can thiệp thành một khối PICO kèm chứng cứ tốt nhất theo mục 5B. Có thể lồng vào chế độ chuyên sâu. Không bắt buộc cho tra cứu nhanh một bước.

### Chế độ thẩm định nguồn

Kích hoạt khi người dùng cung cấp/nhắc tên một guideline, systematic review, RCT, cohort hoặc công cụ lâm sàng và hỏi độ tin cậy. Dùng đúng công cụ thẩm định tương ứng, không chấm đầy đủ một công cụ nếu không có toàn văn/thông tin đủ.

## 4. Quy trình bắt buộc cho mỗi yêu cầu

### Bước 1 — Làm rõ câu hỏi lâm sàng

Xác định:

- Chủ đề chính: bệnh, thuốc, hội chứng, xét nghiệm, can thiệp, thang điểm hoặc nguồn cần thẩm định.
- Mục tiêu: chẩn đoán, điều trị, dự phòng, theo dõi, an toàn thuốc, kháng sinh, chuyển tuyến, tiên lượng.
- Quần thể: người lớn; người cao tuổi; CKD; bệnh gan; thai kỳ; đa bệnh lý/đa thuốc; hoặc nhóm khác.
- Bối cảnh: ngoại trú, cấp cứu ban đầu, nội trú, Việt Nam.

Không hỏi lại nếu đã đủ rõ để trả lời. Chỉ hỏi khi thiếu thông tin có thể làm thay đổi xử trí hoặc gây mất an toàn.

### Bước 2 — Tìm và xác minh nguồn hiện hành

Với nội dung có thể thay đổi theo thời gian, phải truy cập/tìm nguồn mới nhất nếu có công cụ web hoặc nguồn tài liệu.

Ưu tiên:

1. Guideline/statement/safety communication chính thức của tổ chức chuyên môn hoặc quản lý dược phù hợp.
2. Systematic review/meta-analysis chất lượng cao.
3. RCT đa trung tâm lớn.
4. Cohort/registry/RWD lớn khi có tác động thực hành rõ.
5. Consensus chuyên gia khi thiếu chứng cứ mạnh hơn, phải ghi rõ.

**CÁCH TÌM CỤ THỂ — 4 lượt, kế thừa đúng bài học của luồng giám sát định kỳ (14/08/2026).**
Luồng theo-yêu-cầu này từng KHÔNG thừa hưởng gì từ các bản vá của luồng định kỳ — bác sĩ nêu
vấn đề thì skill vẫn tìm theo lối cũ, dính lại đúng các lỗi đã vá:

1. **Lượt GUIDELINE/HTA — gọi TÊN nguồn, không chỉ từ khoá:** hiệp hội chuyên khoa của chủ đề
   (ESC/ACC-AHA · ADA/EASD · KDIGO · GOLD/GINA · EULAR/ACR · AASLD/EASL/APASL · IDSA…) +
   `"Cochrane Database Syst Rev"[ta]` + NICE + USPSTF + WHO. Nguồn quản lý dược khi liên quan
   thuốc (FDA/EMA/MHRA). Đây là tầng lấy KHUYẾN CÁO.
2. **Lượt SR/MA rồi RCT LỚN:** `systematic review[pt] OR meta-analysis[pt]`, rồi
   `randomized controlled trial[pt]` ưu tiên đa trung tâm/tạp chí đỉnh —
   `"N Engl J Med"[ta]` · `"Lancet"[ta]` · `"JAMA"[ta]` · `"BMJ"[ta]` · `"Ann Intern Med"[ta]`.
3. **⚡ Lượt MỚI-VÀO-PUBMED — BẮT BUỘC, không được bỏ:** cùng truy vấn chủ đề, `datetype=edat`
   (ngày VÀO PubMed), **KHÔNG lọc publication type**. Vì sao: MEDLINE gán loại thiết kế hàng
   tuần-đến-hàng-tháng SAU khi bài vào PubMed — đo 14/08: **30/40 bài mới nhất chưa gán loại,
   trong đó có cả tổng quan hệ thống**; lọc `[pt]` ở lượt này là vứt đi chính thứ mới nhất
   (BH38). Bài chưa gán loại → tự đọc tóm tắt để xếp tầng, ghi rõ *"⚡ mới vào PubMed — chưa
   gán loại, tự xếp"*.
4. **Lượt VƯỢT-QUA cho mọi mục định để `apply`:** chạy
   `python tools/kiem_chung_cu_vuot_qua.py --file <dashboard>.html` — hỏi PubMed có tổng
   quan/gộp/guideline MỚI HƠN về cùng chủ đề không (đo 14/08: **125/172 mục `apply` của kho có
   chứng cứ tổng hợp mới hơn**, gồm KDIGO 2026). Bài mới hơn có thể CỦNG CỐ hoặc BÁC — phải
   đọc, không phán từ tiêu đề.

**Với TỪNG PMID/DOI trước khi đưa vào gói:** kiểm rút bài bằng
`python medical-ebm-automation/tools/check_citation_retraction.py --pmid <PMID…>` (chuỗi 3
tầng, nền Retraction Watch chạy được khi mất mạng). Không tra được ⇒ ghi **"chưa kiểm rút
bài"**, TUYỆT ĐỐI không ghi "chưa bị rút". Ca chuẩn: PMID 30267080 — cả PubMed lẫn Europe PMC
đều trả `ok`, chỉ nền ngoại tuyến bắt được là đã rút-và-thay.

Phải xác minh tối thiểu:

- tiêu đề tài liệu;
- tổ chức/tác giả;
- ngày hoặc phiên bản;
- quần thể;
- khuyến cáo/kết quả liên quan trực tiếp đến câu hỏi.

Đọc `references/01-nguon-va-xac-minh.md` và `references/13-source-universe.md`.

### Bước 3 — Trích khuyến cáo nguyên bản, không tự nâng cấp chứng cứ

- Giữ nguyên grading/class/level nếu nguồn cung cấp.
- Không quy đổi hệ thống grading sang GRADE nếu nguồn không quy định.
- Nếu nguồn không báo cáo grading, ghi: “Nguồn không cung cấp phân hạng GRADE/độ mạnh khuyến cáo.”
- Nếu dùng High/Moderate/Low để giúp quyết định, phải ghi: “đánh giá vận hành, không phải phân hạng chính thức của nguồn.”

### Bước 4 — Thẩm định tương xứng với nhu cầu

Không bắt buộc chấm toàn bộ AGREE II/AMSTAR 2 cho mọi câu trả lời ngắn.

- **Tra cứu thực hành nhanh:** kiểm tra tính chính thức, tính hiện hành, quần thể, khuyến cáo và khả năng áp dụng.
- **Khuyến cáo có thể sửa phác đồ/đào tạo:** bổ sung đánh giá phương pháp phù hợp.
- **Yêu cầu thẩm định nguồn hoặc tài liệu học thuật:** thực hiện thẩm định có cấu trúc theo công cụ phù hợp.

Đọc `references/02-cong-cu-tham-dinh-va-grade.md`.

### Bước 5 — Chuyển hóa thành quyết định thực hành

Phân loại từng nội dung:

- **Áp dụng ngay:** đủ xác minh, ảnh hưởng trực tiếp và có hành động cụ thể.
- **Cân nhắc chọn lọc:** phù hợp một nhóm/bối cảnh, cần xem sẵn có, chi phí, quy định hoặc đồng mắc.
- **Chưa đủ để thay đổi thực hành:** chưa xác minh đủ, chỉ là tín hiệu, dự thảo, dữ liệu gián tiếp hoặc không rõ tính áp dụng.

Nếu kết luận là **Áp dụng ngay** hoặc dùng cụm “áp dụng trực tiếp”, phải phân biệt:

- **Áp dụng trong câu trả lời chuyên đề:** đủ nguồn và đủ điều kiện để bác sĩ cân nhắc tại điểm khám.
- **READY_FOR_PHYSICIAN_DIRECT_USE trong sổ cái:** chỉ khi cổng `verify_direct_clinical_practice_readiness.py` PASS cho thẻ đó.

Chứng cứ mới từ engine/dashboards dù có PMID/DOI và high-grade vẫn giữ `REVIEW_REQUIRED` cho tới khi có doctor/master gate. Đọc `references/12-direct-practice-readiness.md` trước khi nâng ngôn ngữ từ “cân nhắc” thành “sẵn sàng áp dụng trực tiếp”.

### Bước 6 — Thích ứng ngoại trú tại Việt Nam

Luôn xem xét khi liên quan:

- thuốc/xét nghiệm/thiết bị có sẵn;
- chi phí, BHYT hoặc khả năng tiếp cận;
- năng lực tuyến khám;
- theo dõi cần thiết;
- phác đồ Bộ Y tế hoặc quy trình đơn vị;
- người cao tuổi, frailty, CKD, bệnh gan, đa thuốc.

Đánh dấu `[CẦN XÁC NHẬN TẠI ĐƠN VỊ]` khi quyết định phụ thuộc quy trình, thuốc, xét nghiệm hoặc nguồn lực địa phương.

Đọc `references/03-thich-ung-viet-nam.md`.

### Bước 7 — Xử lý đúng các nhóm chủ đề đặc biệt

- **An toàn thuốc/kê đơn:** ưu tiên safety communication, label hoặc quyết định quản lý nguy cơ chính thức.
- **Kháng sinh:** ưu tiên guideline hội chứng chính thức và WHO AWaRe khi phù hợp; chỉ nêu liều/thời gian khi đã xác minh nguồn.
- **Thang điểm/công cụ:** chỉ nêu công thức, cut-off và hành động khi đã xác minh đúng phiên bản và quần thể.
- **Cấp cứu:** không để việc tra cứu hoặc tính điểm làm trì hoãn chuyển cấp cứu.

Đọc `references/04-thuoc-khang-sinh-va-cong-cu.md`.

## 5. Cấu trúc đầu ra mặc định

Khung 8 mục dưới đây dùng cho **Chế độ mặc định** (mục 3). Chế độ nhanh dùng `templates/mau-cap-nhat-nhanh.md`; chế độ chuyên sâu dùng `templates/mau-cap-nhat-chuyen-sau.md` — không trộn ba khung này trong cùng một câu trả lời.

# Cập nhật thực hành: [Vấn đề cụ thể]

## 1. Kết luận thực hành nhanh

Nêu ngắn gọn:

- việc nên làm hiện nay;
- điều trị/chiến lược ưu tiên nếu có;
- điểm cần tránh hoặc chưa nên thay đổi;
- cờ đỏ/chỉ định chuyển tuyến nếu liên quan;
- nguồn chính mới nhất đã xác minh.

## 2. Điểm mới có thể thay đổi xử trí

Chỉ đưa vào bảng các thay đổi thực sự mới hoặc có khả năng đổi thực hành.

| Điểm mới | Quyết định thực hành | Đối tượng áp dụng | Nguồn chính; ngày/phiên bản | Độ mạnh/grading của nguồn |
|---|---|---|---|---|

Nếu không có thay đổi mới đủ xác minh, nói rõ: **“Không phát hiện thay đổi mới đủ để đổi thực hành; dưới đây là khuyến cáo hiện hành đã xác minh.”**

## 3. Chẩn đoán, phân tầng nguy cơ và chuyển tuyến

Chỉ bao gồm phần liên quan trực tiếp đến câu hỏi:

- tiêu chuẩn/định nghĩa đang dùng;
- triệu chứng/dấu hiệu giá trị cao;
- cận lâm sàng cần thiết;
- phân tầng nguy cơ;
- nhập viện/chuyển tuyến/cấp cứu.

## 4. Điều trị và theo dõi

| Can thiệp/thuốc | Chỉ định | Lợi ích kỳ vọng | Nguy cơ/thận trọng | Monitoring | Mức chứng cứ/khuyến cáo từ nguồn | Ghi chú thực hành |
|---|---|---|---|---|---|---|

Chỉ nêu liều, ngưỡng, thời gian điều trị hoặc hiệu chỉnh chức năng thận/gan khi nguồn đã xác minh hỗ trợ.

## 5. Nhóm đặc biệt và đa bệnh lý

Ưu tiên phân tích khi phù hợp:

- người cao tuổi/frailty/nguy cơ té ngã;
- CKD;
- bệnh gan;
- ĐTĐ;
- bệnh tim mạch;
- đa thuốc/tương tác;
- thai kỳ hoặc nhóm đặc biệt khác.

## 6. Điều không nên làm hoặc chưa đủ để thay đổi

| Nội dung | Lý do | Trạng thái |
|---|---|---|
|  |  | Chưa đủ để thay đổi thực hành / Không còn khuyến cáo / Cần xác nhận tại đơn vị |

## 7. Ứng dụng tại phòng khám Việt Nam

- Việc có thể triển khai ngay.
- Việc cần đối chiếu sẵn có, chi phí, BHYT hoặc phác đồ đơn vị.
- Theo dõi và safety-netting.
- Điểm cần chuyển tuyến.

## 8. Tài liệu tham khảo chủ chốt

Chỉ liệt kê tài liệu đã xác minh, theo Vancouver/NLM khi yêu cầu bản học thuật hoặc khi câu trả lời có nhiều khuyến cáo quan trọng.


## 5A. Web Dashboard lâm sàng độc lập — đầu ra bắt buộc khi tạo file được

### Mục đích

Sau mỗi cập nhật EBM cho một vấn đề cụ thể, tạo một file HTML độc lập để bác sĩ tra cứu nhanh tại điểm chăm sóc. Tên file gợi ý:

`WebDashboard_EBM_VanDeCuThe_<ChuDeKhongDau>_YYYYMMDD.html`

Ví dụ:

- `WebDashboard_EBM_VanDeCuThe_SuyTimHFpEF_20260602.html`
- `WebDashboard_EBM_VanDeCuThe_Duloxetine_DauThanKinh_20260602.html`

**Dashboard là sản phẩm BỔ SUNG, không phải nơi duy nhất chứa nội dung.** Bất kể môi trường có tạo file được hay không, đầy đủ nội dung EBM theo đúng khung mục của chế độ đang dùng (mục 3) luôn được viết trực tiếp trong khung chat trước, để bác sĩ đọc được ngay không cần mở file. Nếu môi trường không tạo file được, chỉ cần nói rõ điều đó — không được coi đây là lý do rút gọn câu trả lời trong hội thoại.

### Nguyên tắc dữ liệu

- Dashboard chỉ hiển thị nội dung đã xuất hiện trong câu trả lời và đã được xác minh theo quy trình của skill.
- Mỗi điểm thực hành đã xác minh trong Web Dashboard dùng mã cục bộ `ITEM-01`, `ITEM-02`... để mở chi tiết; mã này **không phải ID Dashboard Master**.
- Nội dung chưa đủ xác minh được đặt riêng trong mục `Chưa đủ để thay đổi thực hành`, không trộn với hành động áp dụng.
- Không tự tạo `EBM-W-...`, `MED-W-...`, `ABX-W-...`, `EBM-M-...`, `SCORE-Q-...` hoặc `tool-XX` trừ khi bác sĩ yêu cầu đưa vào hệ thống Master hoặc xác định công cụ cụ thể.
- Không tự ghi dữ liệu vào Excel Master/WebApp Master.

### Kiến trúc Web Dashboard bắt buộc — mô hình MẶC ĐỊNH "EVIDENCE WORKBENCH"

Mọi Web Dashboard lâm sàng theo vấn đề cụ thể MẶC ĐỊNH dùng mô hình **Evidence Workbench**: bố cục 3 cột (master–detail), dày dữ liệu, đọc nhanh tại điểm chăm sóc. (Mô hình một-cột `Clinical Quick View` cũ chỉ dùng khi bác sĩ yêu cầu riêng hoặc khi chỉ có 1–2 item.)

- **Cột trái — Bộ lọc (facets):** Quyết định thực hành (Áp dụng ngay / Cân nhắc chọn lọc / Chưa đủ thay đổi), Nhóm đặc biệt (người cao tuổi, CKD, gan, ĐTĐ, tim mạch, đa thuốc), Loại thiết kế, Mức chứng cứ.
- **Cột giữa — Băng `CLINICAL QUICK VIEW` cố định + bảng điểm chứng cứ + các tab nội dung:** mỗi dòng là một `ITEM-xx`; click để mở thẩm định ở cột phải. Có tab `Chuẩn & chất lượng` để rà chuẩn cập nhật chứng cứ. Hiệu số (HR/RR/OR…) hiển thị kèm forest plot mini đúng như nguồn báo cáo.
- **Cột phải — Panel `EVIDENCE DETAIL VIEW`:** chi tiết item đang chọn.

Bốn lớp nội dung bắt buộc ánh xạ vào bố cục:

#### Lớp 1 — `CLINICAL QUICK VIEW` (băng tóm tắt cố định + tab mặc định ở cột giữa)

Phải cho phép bác sĩ thấy và tìm nhanh:

- câu hỏi/vấn đề lâm sàng đang cập nhật;
- kết luận thực hành ngắn;
- hành động nên làm hiện nay;
- điều không nên làm hoặc giới hạn áp dụng;
- cờ đỏ/chỉ định cấp cứu hoặc chuyển tuyến nếu liên quan;
- nhóm cần thận trọng: người cao tuổi, CKD, bệnh gan, đa thuốc, tim mạch, ĐTĐ;
- quyết định: `Áp dụng ngay`, `Cân nhắc chọn lọc`, `Chưa thay đổi thực hành`;
- nguồn chính và ngày/phiên bản;
- nút `Mở chi tiết`.

#### Lớp 2 — `EVIDENCE DETAIL VIEW` (cột phải)

Mỗi `ITEM-xx` phải mở panel chi tiết (cột phải) gồm:

- tài liệu gốc, tổ chức, ngày/phiên bản, định danh hoặc link;
- quần thể;
- điểm mới hoặc khuyến cáo hiện hành đã xác minh;
- grading nguyên bản của nguồn; nếu không có, nói rõ;
- hành động phòng khám, monitoring, nhóm thận trọng;
- khả năng áp dụng tại Việt Nam;
- tài liệu tham khảo Vancouver/NLM.

#### Lớp 3 — `SAFETY / LIMITS / IMPLEMENTATION` (các tab riêng ở cột giữa)

Phải có các tab/khu vực riêng:

- `An toàn & chuyển tuyến`: chỉ hiển thị khi liên quan;
- `Chưa đủ để thay đổi thực hành`: dữ liệu chưa đủ xác minh hoặc không nên áp dụng rộng;
- `Áp dụng tại Việt Nam`: nội dung triển khai ngay và mục `[CẦN XÁC NHẬN TẠI ĐƠN VỊ]`.

#### Lớp 4 — `STANDARDS / QUALITY` (tab `Chuẩn & chất lượng`)

Mỗi dashboard thật phải khai báo `DATA.standards` để hiển thị:

- khung câu hỏi đã dùng: PICO/PECO/PIRD/PROGRESS hoặc khung phù hợp khác;
- thứ bậc nguồn và ngày/nguồn tìm kiếm;
- chuẩn báo cáo cần đối chiếu: CONSORT, STROBE, PRISMA, STARD, TRIPOD theo thiết kế;
- công cụ thẩm định: AGREE II, AMSTAR 2, RoB 2, ROBINS-I, QUADAS-3 v1.2, PROBAST hoặc JBI; QUADAS-2 chỉ để đọc nghiên cứu lịch sử;
- cổng liêm chính trước phát hành: truy nguyên nguồn, tách độ chắc chắn với quyết định thực hành, không PII, an toàn, tính phù hợp tại Việt Nam;
- truy nguyên từng `ITEM-xx` bằng PMID/DOI/URL/tài liệu tham khảo.

Không hiển thị `Governance/Admin`, `CỔNG A/CỔNG B`, `ACTION_TRACKER` hoặc nhập Master trong Web Dashboard của vấn đề riêng lẻ, trừ khi bác sĩ yêu cầu tích hợp Dashboard Master.

### Tương tác bắt buộc

- Ô tìm kiếm theo bệnh/tình huống, thuốc, nhóm nguy cơ, hành động hoặc nguồn.
- Bộ lọc theo quyết định và nhóm đặc biệt khi có nhiều item.
- Nút `Mở chi tiết`.
- Tab `Chuẩn & chất lượng` để rà câu hỏi, nguồn, chuẩn thẩm định, độ cập nhật, an toàn, Việt Nam và truy nguyên từng item.
- Nút xuất CSV hoặc JSON các item đang lọc nếu khả thi.
- Tab `Kiểm chứng thao tác` với 5 nhiệm vụ:
  1. Tìm hành động ưu tiên của vấn đề ≤30 giây.
  2. Tìm cờ đỏ/chuyển tuyến hoặc kết luận không có cập nhật liên quan ≤30 giây.
  3. Tìm nội dung cho nhóm đặc biệt liên quan ≤30 giây.
  4. Mở nguồn và ngày/phiên bản ≤60 giây.
  5. Rà tab `Chuẩn & chất lượng` trước phát hành ≤60 giây.

### Thiết kế giao diện — bảng màu mặc định "Evidence Workbench" (nền sáng, dày dữ liệu)

Nền & khung:
- Background `#eef1f6` · Surface `#ffffff` · Surface phụ `#f8fafc` / `#f1f5f9`
- Chữ chính `#0f172a` · chữ phụ `#334155` · mờ `#64748b` · đường kẻ `#e2e8f0`
- Nhấn chủ đạo: Teal `#0e7490` / `#0891b2` · Blue `#2563eb`

Màu ngữ nghĩa theo Quyết định thực hành (dùng nhất quán cho facet, badge, KPI):
- `Áp dụng ngay` = Green `#16a34a`
- `Cân nhắc chọn lọc` = Amber `#ca8a04`
- `Chưa đủ thay đổi` = Orange `#ea580c`
- `Cờ đỏ / chuyển tuyến` = Red `#dc2626`

Màu mức chứng cứ (GRADE): Cao `#16a34a` · TB `#ca8a04` · Thấp `#ea580c` · Rất thấp `#dc2626`.
Màu loại thiết kế (badge): RCT `#2563eb` · Meta `#7c3aed` · Cohort `#0891b2` · Guideline `#059669` · Đồng thuận `#db2777`.

**Sử dụng template MẶC ĐỊNH:** `templates/web-dashboard-evidence-workbench.html` (mẫu **"Evidence Workbench"** — nền sáng, 3 cột; có khối **GRADE Evidence-to-Decision** và tab **Chuẩn & chất lượng**; mặc định từ 2026-06-07 theo lựa chọn của bác sĩ, nâng chuẩn 2026-07-15).
Chỉ cần thay khối hằng số `DATA = {…}` ở cuối file; KHÔNG sửa HTML/CSS. Chrome (tiêu đề, PICO chips, KPI, băng Clinical Quick View, EtD, standards/quality) **tự sinh từ `DATA`**.
**Mẫu KHI BÁC SĨ YÊU CẦU (nền tối, dày dữ liệu):** `templates/web-dashboard-dark-analyst.html` — **CÙNG schema `DATA`** (một khối dữ liệu chạy được cả hai). Template một-cột cũ `web-dashboard-van-de-cu-the-clinical-quick-view.html` chỉ dùng khi yêu cầu riêng.
Cả hai mẫu hỗ trợ field tùy chọn `effectText` (hiệu số phi-tỷ-số), `rob` (RoB 2, chỉ RCT), `frame`/`frameLabels` (khung không-PICO), `etd` (GRADE Evidence-to-Decision) và `standards` (Lớp 4, tab `Chuẩn & chất lượng`).
✅ **ĐÍNH CHÍNH LẦN HAI (10/09/2026) — `standards` NAY thật sự cùng schema.** Đợt kiểm 10/09/2026 (đính chính lần một ở trên) phát hiện Dark Analyst chưa render `DATA.standards`; đã vá cùng ngày: thêm CSS `.qual-wrap`/`.qual-grid`/`.qbox`/`.qgate`/`.qtrace`, hàm `qualityView()` render đủ 7 khối (khung câu hỏi · thứ bậc nguồn · độ cập nhật · xác minh tự động nguồn · chuẩn báo cáo · công cụ thẩm định · an toàn+VN) + cổng liêm chính + bảng truy nguyên từng item, escape XSS bằng `escHtml()`/`escUrl()` đúng khuôn `evidence-workbench-template.html`. Đặt trong `.main` (vùng cuộn được), không phải chrome cố định — tránh bị `.app{overflow:hidden}` cắt mất. Tương thích ngược nguyên vẹn: `DATA.standards` không khai báo thì ẩn cả section, không bịa khung rỗng. Đính chính lần một ở trên (⚠️) vì vậy đã LỖI THỜI — giữ lại để thấy lịch sử, không xoá.

**TỰ ĐỘNG khi gọi skill — BỘ NĂM, MỘT LỆNH:** mỗi lần skill được gọi cho một vấn đề → dựng Dashboard (mẫu Evidence Workbench; Dark Analyst CHỈ khi bác sĩ yêu cầu) rồi chạy **một lệnh duy nhất**:

```bash
python3 tools/xuat_goi_cap_nhat.py <dashboard>.html --online
```

Lệnh này tự làm trọn và sinh **năm** sản phẩm từ CÙNG một khối `DATA` (nên không bản nào tụt lại một phiên bản so với bản khác):
① **Dashboard** — đã qua **HAI** cổng chạy sẵn bên trong: `verify_dashboard.py --online` (liêm chính:
PMID/DOI phân giải thật) và **①-bis `--strict-sources`** (cổng nguồn nghiêm ngặt) ·
② **Bản đọc** `derivatives/<mã>_ban-doc.html` — cờ đỏ và việc cần làm đứng trước; từ 14/08/2026
mang thêm **hai dải cảnh báo về ĐỘ TIN CẬY của chính tài liệu**, đặt ngay dưới đầu trang: dải
**đỏ "Nguồn đã bị rút"** và dải **cam "Bản khác cùng chủ đề đang kết luận ngược"** (xem 5D-a
và mục *Đăng ký chủ đề*). Cả hai chỉ ĐẶT CẠNH NHAU hai kết luận, **không đổi `decision` nào**
(BH10) và **không đoán bên nào đúng** (BH28 — hai bản có thể đang nói về hai kết cục khác nhau
của cùng một thử nghiệm). Không tính được thì in rõ *"chưa kiểm"*, tuyệt đối không im lặng ·
③ **Bản Word** `derivatives/<mã>_TaiLieuChiTiet.docx` — bản lưu trữ chuẩn, có màu ·
④ **Word dạng HTML** `<mã>_TaiLieuChiTiet.html` — đọc thẳng trong khung chat (mất màu nền ô) ·
⑤ **PDF giữ màu** `<mã>_TaiLieuChiTiet.pdf` — giữ đúng huy hiệu mức chứng cứ (xanh lá Cao/Áp dụng ngay · cam Trung bình/Cân nhắc · đỏ Rất thấp), in bằng Chrome headless.

Cổng liêm chính KHÔNG đạt thì vẫn xuất file nhưng bản Word tự hạ câu chữ thành "CẦN xác minh" — không bao giờ khẳng định sai. Thiếu `pandoc` (bước ④) hoặc thiếu Chrome/Edge (bước ⑤) thì bỏ qua đúng bước đó kèm thông báo rõ, KHÔNG làm hỏng các bước còn lại và KHÔNG đổi mã thoát — hai bước này là tiện ích đọc, không phải cổng chất lượng.

**Cổng nguồn ①-bis xử lý HAI loại lỗi khác hẳn nhau — đừng gộp:**
- `decision='apply'` trên `gradeLevel` na/low, hoặc `apply` chỉ dựa Consensus ⇒ **CHẶN XUẤT, mã thoát 3**.
  Cách sửa phụ thuộc nguồn thuộc nhóm nào: nguồn **QUY PHẠM** (guideline chính thức, nhãn thuốc FDA —
  `gradeLevel:'na'` vì nguồn không dùng thang GRADE) thì khai `normativeBasis`, **KHÔNG hạ** `decision`
  (hạ một chống chỉ định hay liều theo CrCl xuống "cân nhắc" là làm GIẢM an toàn); chứng cứ **yếu thật**
  thì HẠ `decision` xuống `consider`/`notyet`. **TUYỆT ĐỐI không nâng `gradeLevel`.**
- Thiếu `DATA.standards` ⇒ chỉ **CẢNH BÁO**, vẫn xuất. Nhưng **dashboard MỚI phải luôn khai
  `DATA.standards`** — bỏ trống là tự đánh mất hợp đồng nguồn của chính lần tìm kiếm vừa làm.

⚠️ **Bài học 12/08/2026 — đọc kết quả cổng phải hỏi "cổng đã chạy tới luật nào", không chỉ đếm số lỗi.**
Bản cũ của `verify_dashboard.py` `return` NGAY khi thiếu `DATA.standards`, nên toàn bộ luật an toàn cấp
item chưa từng chạy trên 47 dashboard. Cổng báo đúng "1 lỗi cứng" và người đọc kết luận "chỉ thiếu siêu
dữ liệu, nội dung không sai" — một ảo ảnh. Sau khi bỏ `return` sớm, đo lại 61 dashboard: **73 mục `apply`
trên chứng cứ yếu/không phân hạng, trên 16 dashboard** (trước chỉ thấy 4).

**Chạy tiếp sau bộ năm:** `tools/drug_safety_scan.py` (nếu có thuốc + cao tuổi/đa thuốc) → `tools/build_library.py add <dashboard>.html` (tích lũy vào chỉ mục tra cứu).

**KHÔNG tự chạy `EBM_MASTER/tools/sync_all.py`** (đổi mặc định 2026-08-05 theo yêu cầu bác sĩ) — chỉ chạy khi bác sĩ yêu cầu riêng. ⚠️ Bỏ chạy `sync_all.py` là CHƯA ĐỦ để giữ một gói ngoài Antifacts: `tools/build_antifacts.py` quét `EBM-Dashboards/WebDashboard_*.html` bằng glob và scheduled-task `ebm-antifacts-weekly` (thay hai lịch launchd đã TẮT từ 15/08/2026) vẫn dựng lại hub từ chính thư mục đó. Muốn giữ ngoài hub thì phải khai tên file vào `EBM-Dashboards/antifacts-exclude.txt` rồi chạy lại `build_antifacts.py`.

**MẶC ĐỊNH sau khi chạy xong:** mở cả năm file cho bác sĩ ngay trong Claude (SendUserFile — `display:"render"` cho dashboard · bản đọc · Word-dạng-HTML · PDF; `.docx` đính kèm để tải). Không bắt bác sĩ tự đi tìm trong thư mục.
**CỔNG TRA CỨU DUY NHẤT cho bác sĩ** (không phải lục từng file): nút **"Mở EBM (WebApp).command"** → `EBM_MASTER/EBM_WEBAPP.html` (tìm/lọc mọi cập nhật đã làm). `EBM-Dashboards/` chỉ là vùng staging tạo file mới.


## 5B. Trình bày theo PICO và ghi nguồn sạch

### Khi nào dùng PICO

Dùng khối PICO khi câu hỏi cốt lõi là **một can thiệp có hiệu quả/an toàn hay không** (điều trị, dự phòng, xét nghiệm chẩn đoán, thang điểm) cho một quần thể cụ thể; hoặc khi người dùng yêu cầu “PICO”, “chứng cứ tốt nhất”, “best evidence”, “so sánh can thiệp”. Mỗi can thiệp = một khối PICO độc lập. Không bắt buộc cho tra cứu nhanh một bước hay câu hỏi mô tả/định nghĩa.

### Khối PICO chuẩn (bắt buộc đủ 5 dòng)

Mỗi can thiệp trình bày theo đúng thứ tự sau:

1. **Tiêu đề:** [Rối loạn] — [Can thiệp] (vai trò: đầu tay / thay thế / chống dùng).
2. **P – I – C – O:**
   - **P (Population):** quần thể đích, nêu rõ nhóm đặc biệt nếu có.
   - **I (Intervention):** can thiệp, liều/cách dùng chỉ khi nguồn đã xác minh.
   - **C (Comparator):** nhóm so sánh (giả dược, chăm sóc thường quy, can thiệp khác, hoặc “không điều trị”).
   - **O (Outcome):** tiêu chí chính (và phụ nếu cần), nêu đúng thước đo của nghiên cứu.
3. **Chứng cứ tốt nhất:** thiết kế (guideline / SR-MA / RCT / cohort), cỡ mẫu nếu có, **hiệu số là ước lượng điểm** kèm khoảng tin cậy/giá trị p **đúng như nguồn báo cáo**, và nguồn (tác giả/tổ chức + năm + tạp chí).
4. **Độ mạnh/grading từ nguồn:** ghi nguyên văn phân hạng của nguồn (Strong/Conditional, Level A/B/C, GRADE High/Moderate/Low…). Nếu nguồn không cung cấp, ghi rõ “Nguồn không cung cấp phân hạng”. **Không tự gán GRADE.**
5. **Kết luận thực hành:** một câu hành động + giới hạn áp dụng tại Việt Nam khi liên quan.

### Quy tắc liêm chính cho PICO

- Hiệu số (ARR, RRR, NNT, NNH, OR, RR, HR, chênh lệch trung bình, %…) phải **trích đúng từ nguồn**; không tự tính, suy diễn hay làm tròn gây sai lệch ý nghĩa.
- Tách rõ ba lớp: (a) khuyến cáo/kết quả của nguồn; (b) độ chắc chắn chứng cứ theo nguồn; (c) đánh giá vận hành của người tổng hợp (nếu có, phải ghi “đánh giá vận hành”).
- Khi chứng cứ không đồng nhất (vd RCT lớn âm tính sau các RCT nhỏ dương tính), **nêu cả hai chiều** và thử nghiệm quyết định, không chọn lọc thiên lệch.
- Không lập PICO định lượng khi chỉ có đồng thuận/nguyên lý; thay vào đó mô tả định tính và đánh dấu `[CẦN BỔ SUNG]`.
- Có thể tổng hợp các khối PICO thành một bảng độ mạnh chứng cứ ở cuối (rối loạn · can thiệp · thiết kế · độ mạnh từ nguồn).

### Ghi nguồn sạch (bắt buộc) — tránh lỗi hiển thị

- Ghi nguồn **trực tiếp trong câu** bằng văn bản thường: tác giả/tổ chức + năm + tạp chí/phiên bản. Ví dụ: “(Trauer và cộng sự, meta-analysis 20 RCT, *Ann Intern Med* 2015)”, hoặc “theo AASM 2024”.
- Liệt kê **tài liệu tham khảo theo Vancouver/NLM** ở cuối khi có nhiều khuyến cáo quan trọng hoặc khi cần bản học thuật.
- **TUYỆT ĐỐI KHÔNG** chèn thẻ markup trích dẫn thô, mã chỉ mục, hay ký tự kỹ thuật của công cụ tìm kiếm vào câu trả lời (ví dụ các đoạn dạng `cite index`); đây là lỗi hiển thị, làm bản trình bày rối và phải tránh tuyệt đối.
- Trước khi gửi, rà soát để bảo đảm không còn bất kỳ thẻ/mã kỹ thuật nào lẫn trong văn bản; mọi nguồn chỉ xuất hiện dưới dạng văn bản người đọc được.

Xem mẫu chi tiết: `references/06-pico-va-trich-dan.md`.


## 5C. Tự chọn khung câu hỏi — PICO và các khung thay thế

Trước khi tổng hợp, **tự nhận diện loại câu hỏi lâm sàng** và **chọn khung phù hợp** — không mặc định mọi câu hỏi đều là PICO. Nêu rõ một câu: **"Đã dùng khung [X] vì câu hỏi thuộc loại [Y]."** PICO vẫn là mặc định cho câu hỏi điều trị/can thiệp (đa số ca ngoại trú); chỉ chuyển khung khi câu hỏi thực sự thuộc loại khác.

| Loại câu hỏi | Khung | Thành phần chính | Thiết kế tốt nhất | Thẩm định | Chỉ số điển hình |
|---|---|---|---|---|---|
| Điều trị/can thiệp | **PICO(T)(S)** | P·I·C·O (+Time/Setting) | RCT/SR-MA | RoB 2, AMSTAR-2, GRADE | RR/OR/HR/ARR/**NNT** |
| Tác hại/nguyên nhân | **PECO** | P·Phơi nhiễm·C·O | Cohort/case-control | ROBINS-I | RR/OR/HR/**NNH** |
| Chẩn đoán (độ chính xác) | **PIRT** | P·Index test·Chuẩn tham chiếu·Bệnh đích | Cross-sectional độ chính xác | QUADAS-3 v1.2, STARD; QUADAS-2 chỉ cho nghiên cứu lịch sử | **Sn/Sp/LR**, AUC |
| Tiên lượng | **PROGRESS/PICOTS** | P·Yếu tố TL·(so sánh)·Kết cục·Thời gian | Cohort dọc | QUIPS, PROBAST | HR, C-statistic |
| Tầm soát/dự phòng | **PICO mở rộng** | P·Test/biện pháp·C·Kết cục lâm sàng | RCT/SR | GRADE, USPSTF | giảm biến cố, NNT |
| Tần suất/dịch tễ | **CoCoPop** | Condition·Context·Population | Cross-sectional | JBI prevalence | tỷ lệ (CI) |
| Trải nghiệm/định tính | **SPIDER** | Sample·PoI·Design·Eval·Type | Định tính | CASP | chủ đề (theme) |
| Tổ chức/dịch vụ/chính sách | **ECLIPSE** | Expectation·Client·Location·Impact·Professionals·Service | Hỗn hợp | AGREE II | chỉ số dịch vụ |
| Kinh tế y tế | **PICO + chi phí** | + ICER/chi phí | Đánh giá kinh tế | CHEERS | ICER, chi phí/QALY |

**Mô hình tổng hợp bổ trợ** (áp dụng sau khi đóng khung): phân tầng nguồn **6S**; cân lợi ích–tác hại bằng **NNT/NNH**; **GRADE Evidence-to-Decision (EtD)** rút gọn cho khuyến cáo; bảng **Tóm tắt phát hiện (SoF)**; **tam giác liêm chính** (khuyến cáo nguồn / độ chắc chắn / đánh giá vận hành).

**Render Evidence Workbench:** với khung không phải PICO, dùng field tùy chọn `frame` (nhãn khung) và `frameLabels` để đổi tên 4 ô P/I/C/O trong panel thẩm định (vd Chẩn đoán → P/Index test/Chuẩn vàng/Độ chính xác). Không đặt thì hiển thị P/I/C/O như cũ. Chỉ số đặc thù (Sn/Sp/LR, HR, NNT/NNH) trích đúng nguồn; **không tự gán GRADE**.

Chi tiết, ví dụ & cách ánh xạ: `references/07-mo-hinh-cau-hoi-va-khung-thay-the.md`.


## 5D. Cổng liêm chính · Thư viện cập nhật · Sản phẩm phái sinh

Sau khi dựng dashboard, dùng bộ công cụ trong `tools/` để bảo đảm chất lượng và nhân giá trị:

**(a) Cổng kiểm liêm chính — `tools/verify_dashboard.py`** (chạy TRƯỚC khi giao):
`python3 tools/verify_dashboard.py <dashboard>.html --online --strict-sources`
Kiểm: mỗi item có PMID/DOI/URL truy nguyên · `gradeLevel` & `decision` hợp lệ · có disclaimer · quét PII · **tự xác minh mỗi PMID phân giải đúng trên PubMed và DOI qua Crossref** · kiểm `DATA.standards`, ngày tìm kiếm còn mới, ≥2 nguồn tìm kiếm, references[], và chặn `apply` nếu chứng cứ yếu/không phân hạng/chỉ dựa đồng thuận. FAIL → sửa trước khi giao.
Cờ **opt-in `--check-topic`** (thêm sau `--online`): gọi LLM chấm mỗi item có LẠC CHỦ ĐỀ/chuyên khoa của dashboard không (`tools/check_topic_relevance.py` — lấp khoảng trống cổng kỹ thuật không bắt được item lạc chủ đề, vd bài sản/nhi lọt vào dashboard Tim mạch). Chỉ CẢNH BÁO, không chặn cứng; thiếu `ANTHROPIC_API_KEY` → bỏ qua êm.

🔴 **CỔNG NAY CHẶN NGUỒN ĐÃ BỊ RÚT (thêm 14/08/2026 — trước đó KHÔNG kiểm).** Cổng vẫn giữ
nguyên tắc *không tự kết luận* trạng thái rút bài từ một nguồn metadata thiếu thẩm quyền; điều
mới là nó **đọc lại kết luận DƯƠNG TÍNH** mà chuỗi 3 tầng đã xác nhận và ghi vào
`EBM-Dashboards/.so-xac-minh-nguon.json`, qua `tools/so_xac_minh_nguon.py::nguon_da_rut()`.
*Vì sao cần:* PMID 30267080 (JAMA Oncology, rút 2019, dạng **retract-and-replace**) nằm trong
`ViemGanB_DieuTri` và **đi qua cổng sạch sẽ** suốt — nó chỉ hiện khi bác sĩ chủ động gõ
`so_xac_minh_nguon.py --bao-cao`.
**Bất đối xứng bắt buộc:** có bản ghi ⇒ **lỗi cứng**; sổ **im lặng ⇒ KHÔNG** phát tín hiệu nào
(im lặng chỉ nghĩa là chưa ai quét file đó — biến nó thành dấu ✓ là dựng lời bảo đảm không có
cơ sở); tra cứu hỏng ⇒ **cảnh báo hiện ra**, không bỏ qua thầm lặng. Khoá bằng **BH31**.
⚠️ Cổng chỉ ĐO. Không tự gỡ mục: *retract-and-replace* nghĩa là bài đã được sửa rồi đăng lại,
việc cần làm là **đối chiếu số liệu với bản đã thay**, không phải xoá — và đó là việc của bác sĩ.

**(b) Thư viện cập nhật — `tools/build_library.py`** (tích lũy thành tài sản tra cứu):
`python3 tools/build_library.py add <dashboard>.html` → cập nhật `library.json` + sinh `evidence-library.html` (chỉ mục mọi bản cập nhật, có tìm/lọc, mở thẳng từng dashboard).

**(c) Sản phẩm phái sinh — TỰ ĐỘNG mỗi lần chạy:** sau khi cổng liêm chính PASS, tự sinh 3 sản phẩm vào `EBM-Dashboards/derivatives/` (`tools/make_derivatives.py <dashboard>.html`): **tờ dặn người bệnh** (ngôn ngữ phổ thông, BỎ liều) · **dàn ý slide** (giữ hiệu số + GRADE + PMID) · **kịch bản TikTok**. Slide = faithful; tờ dặn & TikTok do model rà ngôn ngữ phổ thông trước khi giao. **Video TikTok thật: theo yêu cầu qua skill `tao-video-tiktok`.** Playbook: `references/08-xuat-san-pham-phai-sinh.md`. Người bệnh & TikTok **KHÔNG nêu liều**; kèm disclaimer; không PII; bác sĩ duyệt trước khi phát/đăng.

**GRADE Evidence-to-Decision (EtD):** Dashboard Dark Analyst tự hiển thị khối EtD khi `DATA` có field `etd` (vấn đề · lợi ích · tác hại · độ chắc chắn · giá trị · cân bằng · nguồn lực · công bằng · chấp nhận · khả thi → khuyến cáo + độ mạnh). **Hàng lợi ích/tác hại/độ chắc chắn lấy TỪ chứng cứ; các hàng còn lại + khuyến cáo = "đánh giá vận hành"** (ghi rõ trên dashboard). Điền `etd` cho mỗi cập nhật có khuyến cáo đổi thực hành.

**(d) Thư mục chung tích lũy:** xuất MỌI dashboard vào `EBM-Dashboards/` (trong OneDrive → tự đồng bộ Mac↔Windows). Sau khi PASS cổng (a), chạy `EBM-Dashboards/tools/build_library.py add <file>.html` để tích lũy vào chỉ mục `EBM-Dashboards/evidence-library.html`. Hướng dẫn: `EBM-Dashboards/README.md`.


## 5E. Lớp phủ an toàn thuốc · Giám sát định kỳ · Bản địa hóa BYT

**(a) An toàn thuốc (người cao tuổi/đa thuốc):** khi cập nhật có thuốc và liên quan nhóm `cao-tuoi`/`da-thuoc`, chạy `tools/drug_safety_scan.py <dashboard>.html` (đối chiếu bảng cờ **Beers 2023/STOPP-START v3** trong `data/drug_flags.json`) → cảnh báo + sinh prompt rà soát ĐẦY ĐỦ bằng skill `nguoi-cao-tuoi-da-benh-da-thuoc`. Bảng cờ KHÔNG đầy đủ, chỉ để nhắc. Chi tiết: `references/09-an-toan-thuoc-overlay.md`.

**(b) Giám sát định kỳ (Track B):** `tools/surveillance_scan.py` quét PubMed tìm guideline/SR/meta/RCT MỚI theo `EBM-Dashboards/watchlist.json` → xuất Markdown + audit JSON của ỨNG VIÊN (KHÔNG tự đổi thực hành). Scanner có retry/backoff, kiểm schema watchlist, dedup PMID và mặc định trả mã khác 0 khi PARTIAL/FAIL; chủ đề lỗi không được diễn giải là "không có cập nhật". Owner thu thập duy nhất là engine tuần/tháng; các routine khác chỉ dùng lại candidate queue, không quét trùng cùng cửa sổ.

**Cổng triển khai bắt buộc:** `medical-ebm-automation/tools/verify_evidence_surveillance_deployment.py --online`. Chỉ trạng thái `READY_FOR_CONTROLLED_DEPLOYMENT` mới cho phép chạy ở chế độ candidate-only. Cổng yêu cầu canary nguồn + dashboard online, runtime tuần/tháng còn mới, alert đã nhận thử, drill rollback hash-match, ít nhất 2 chu kỳ shadow không lỗi/không auto-apply, và UAT/phê duyệt bác sĩ + vận hành. Agent không tự điền PASS hoặc ký thay. PARTIAL/FAIL giữ watermark, chặn `bridge_to_ebm_master.py` và không gửi cảnh báo nội dung. Chi tiết: `references/10-giam-sat-dinh-ky.md`.

**(c) Bản địa hóa Bộ Y tế VN:** ở bước "Áp dụng tại VN", tra `EBM-Dashboards/vn-guidelines/registry.json` (bác sĩ điền từ tài liệu CHÍNH THỨC — **KHÔNG bịa số QĐ**) + RAG (`clinical-evidence-rag`) để đối chiếu quốc tế ↔ BYT (phác đồ, danh mục BHYT, phân tuyến). Chi tiết: `references/11-guideline-bo-y-te-vn.md`.


## 5F. Ba chốt TỰ ĐỘNG chạy mỗi phiên (thêm 13/08/2026)

Ba công cụ dưới đây đã nối vào hook `SessionStart` và chạy **không cần bác sĩ gọi**.
Chúng bổ sung cho nhau, không thay nhau — đừng gộp.

**(a) `tools/tu_khoi_dong.py --phong` — TỰ KHỞI ĐỘNG giám sát.**
Đo bằng `launchctl print`: hai job `com.medicalebm.weeklysafety` và
`com.medicalebm.monthlyupdate` đều cho `runs = 0 · (never exited)` — **chưa từng nổ
lần nào** kể từ khi cài (11/07). `StartCalendarInterval` đòi máy phải THỨC đúng
19:00 thứ Bảy; Windows thì không có launchd nào cả. Hệ quả: mọi lần cập nhật chứng
cứ đều do bác sĩ chủ động — tức hệ là CÔNG CỤ, không phải agent.
Chốt này lấy chính lúc mở phiên làm nhịp: quá hạn thì **phóng ở NỀN** (tách tiến
trình, không chặn phiên) rồi trả quyền điều khiển ngay.
*Ranh giới:* chỉ phóng được **hai script chủ sở hữu** trong allowlist `OWNER` — không
tự viết bộ thu thập mới; kết quả vào **hàng ứng viên**, `clinical_auto_apply: false`,
Cổng A/B nguyên vẹn; khoá theo PID nên không phóng chồng; tắt hẳn bằng `--tat`.
*Đã kiểm thật 13/08:* phóng lần đầu → chạy trọn → `status: PASS`, 4/4 bước = 0.

**(b) `tools/chot_hoi_quy_bai_hoc.py` — CHỐT HỒI QUY trên lỗi ĐÃ TỪNG xảy ra.**
Vá xong mà bài học chỉ nằm trong tài liệu thì lần refactor sau lỗi quay lại y nguyên,
và vẫn im lặng như cũ. 10 mục BH01–BH10, mỗi mục là **một lỗi có thật, có ngày**, kiểm
bằng cách **gọi vào mã đang sống** — không mock, không đếm chuỗi tài liệu.
Ba luật khi thêm mục: (1) chỉ thêm lỗi ĐÃ xảy ra thật; (2) kiểm HÀNH VI chứ không kiểm
sự có mặt của câu chữ — đếm chuỗi chính là bẫy TAUTOLOGY đã gặp ở guardrail G3/G8;
(3) chạy nhanh và ngoại tuyến.
*Bắt được ngay lần chạy đầu:* `tools/run_retraction_and_med_safety.py` ghi cứng
`C:/Users/Admin/...` nên **chưa từng chạy được trên Mac** — cùng lớp lỗi với
`ensure_strict_source.py`, và nằm đúng trong công cụ kiểm RÚT BÀI. Đã vá.

**(d) Hai lỗi PHÂN LOẠI NGUỒN tìm được ở đợt kiểm toàn diện 13/08 — cùng một lớp:
giả định ngầm bị vỡ trong im lặng.**

**BH11 — tool skill 3 bản, runtime đi TRƯỚC nguồn.** 4 tool (`build_library`,
`dashboard_content_audit`, `drug_safety_scan`, `make_derivatives`) tồn tại ở
`EBM-Dashboards/tools` (runtime) · `sync/skills/.../tools` (nguồn git) ·
`EBM_MASTER/skill_assets` (mirror hub). Runtime có **11 dòng riêng**, nguồn có **0** —
11 dòng đó là **bản vá UTF-8 cho Windows** (stdout cp1252 làm `print()` tiếng Việt ném
UnicodeEncodeError và giết tiến trình SAU KHI việc đã xong; đo 12/08: bản Word 82 KB đã
ghi ra đĩa mà tool thoát mã 1 ⇒ caller tưởng hỏng, bỏ 2 bước sau).
**Đẩy nguồn→runtime theo phản xạ sẽ XOÁ bản vá khỏi cả 4 tool.** Chiều đúng quyết theo
NỘI DUNG (bên nào bao trùm), không theo mtime, cũng không theo "nguồn luôn thắng runtime".

**Dương tính giả "WHO" — bài thường bị NÂNG thành nguồn chính thức.**
`match_authority_source()` lọc tham số rỗng TRƯỚC rồi mới cắt `blobs[:2]` làm vùng kiểm
alias mơ hồ. Khi `authors` rỗng thì **`title` trượt lên vị trí 2**, nên chữ "who" trong
câu tiếng Anh khớp alias WHO:
`detect_official_org("patients who underwent surgery", journal="J Surg") → 'WHO'`.
Hệ quả: một bài bất kỳ có chữ "who" trong tiêu đề được phân loại là Tổ chức Y tế Thế
giới — đúng loại dương tính giả mà lớp alias mơ hồ sinh ra để chặn, và nó nâng hạng
nguồn chứ không hạ. Vá bằng cách **giữ nguyên vị trí** (đệm chuỗi rỗng) rồi mới lấy 2 vị
trí đầu. Kiểm: `pytest tests/test_group_c_scoring.py`.

**(e) Hai lỗi IM LẶNG của dây chuyền xuất, tìm được ở vòng lặp 13/08.**

**BH13 — bộ dựng Word chết trên chuỗi nối kiểu JS.** Dashboard viết tay hay ngắt chuỗi
dài bằng dấu cộng: `source:"...EMA; 12 June 2026. "+"https://..."`. Hợp lệ trong
JavaScript, KHÔNG hợp lệ trong JSON ⇒ `json.loads()` ném *Expecting ',' delimiter*.
`AnToanThuoc_EMA_PRAC_20260614` là bản DUY NHẤT trong 10 bản xuất lại không ra `.docx`,
và vì **bước ⑤ PDF dựng TỪ `.docx`** nên mất luôn PDF — 3/5 sản phẩm thay vì 5/5.
Dây chuyền chỉ in `⚠ Bỏ qua: chưa có file .docx`, **không nói lý do**, nên lỗi trông như
một bước bị bỏ chứ không như một bản thảo hỏng. Vá bằng `join_string_concatenation()`
quét theo TRẠNG THÁI chuỗi — dấu cộng trong nội dung ("nguy cơ tim mạch + chuyển hoá")
không được đụng tới.

**BH12 — vòng quét nguồn chạy đúng nhưng trông như treo.** Hai lỗi chồng nhau:
`ghi_so()` chỉ gọi SAU khi hết một vòng (mạng chậm vì NCBI chặn ⇒ một vòng ~180 mục rất
lâu ⇒ đóng phiên là **mất trắng** mọi bằng chứng vừa thu), và stdout bị đệm theo KHỐI khi
chuyển hướng ra file ⇒ **0 byte log sau 12 phút**. Đo thật: tiến trình sống, chỉ 5,3 giây
CPU trên 12 phút — đang chờ mạng, không hề treo. Vá: ghi sổ mỗi 10 mục + `line_buffering`.
Sau vá, thấy tiến độ sau **40 giây**.

> **Bài học chung của cả hai:** một công cụ chạy nền mà không kể chuyện thì "đang chạy
> đúng" và "đã chết" trông giống hệt nhau — và người vận hành sẽ giết nhầm, hoặc tệ hơn,
> tin rằng bước đó đã xong.

**(f) LUẬT MỚI 13/08 — `gradeSource` là LỜI KHAI, không phải sự thật đã kiểm.**

Khi sửa `gradeLevel` dựa trên câu "nguồn không phân hạng GRADE" trong `gradeSource`, **phải
tra nguồn trước**. Ca thật: `SuyTim_NoiTiet ITEM-05` khai *"không phân hạng GRADE chính thức"*,
nhưng hướng dẫn Endocrine Society (Bornstein 2016, PMID 26760044, doi:10.1210/jc.2015-1710) nói
rõ **được xây dựng BẰNG hệ thống GRADE**. Chuyển `gradeLevel` sang `na` theo lời khai đó sẽ là
ghi sai về nguồn — và vì `na` mở khoá miễn trừ quy phạm, nó còn NÂNG hiệu lực khuyến cáo dựa
trên một tiền đề sai. Mục này đã được DỪNG LẠI chờ đọc toàn văn.

**Ba loại thay đổi hợp lệ, phân biệt rõ (đợt 13/08, 11 mục bác sĩ duyệt):**
| Loại | Khi nào | Ví dụ |
|---|---|---|
| **HẠ `decision`** | nguồn tự nói yếu/có điều kiện | ACR 2021 *"khuyến cáo CÓ ĐIỀU KIỆN"* → `consider` |
| **GIỮ `apply`, sửa siêu dữ liệu** | nguồn quy phạm bị ghi nhầm hạng | nhãn FDA: `low → na` + `normativeBasis:"drug-label"` |
| **ĐỒNG NHẤT hai bản** | cùng ITEM/PMID/design, chỉ khác vì một bản chưa được áp đợt sửa | chép nguyên từ bản đã duyệt |

⚠️ **Loại 2 và 3 làm khuyến cáo MẠNH hơn** ⇒ luôn cần bác sĩ chuẩn y, kể cả khi máy nhìn ra
nguyên nhân rõ ràng. Loại 1 cũng vậy — cả ba đều là quyết định lâm sàng.

**(g) BH14 — KHÔNG BAO GIỜ khuyên một việc chắc chắn vô ích.**

Chu trình từng kết luận *"Còn nguồn chưa xác minh hoặc hết hạn — **chạy lại thêm vòng**"*
cho MỌI mục hết hiệu lực. Đo thật: **562/1146 mục hết hiệu lực, và CẢ 562 là PMID chưa kiểm
được rút bài vì NCBI đang chặn máy** — chạy lại một trăm vòng cũng không đổi được gì.

Lời khuyên chắc chắn vô ích **tiêu thời gian THẬT của bác sĩ**, và tệ hơn: nó làm mất niềm tin
vào những cảnh báo ĐÚNG khác của cùng công cụ — cùng lớp tác hại với báo động giả.

Nay báo cáo TÁCH lý do và chỉ đúng cách sửa cho từng loại:

| Lý do hết hiệu lực | Cách sửa | Mã |
|---|---|---|
| PMID chưa kiểm được rút bài, **chưa tải nền Retraction Watch ngoại tuyến** | tải MỘT LẦN, không cần khoá API: `python medical-ebm-automation/tools/tai_retraction_watch.py` rồi chạy lại — **SẼ** sửa được | `CAN_TAI_RETRACTION_WATCH` |
| PMID chưa kiểm được rút bài, **nền ngoại tuyến ĐÃ tải mà vẫn tắc** | chạy lại thêm vòng có thể sửa (chuỗi 3 tầng); phần còn sót cần thêm `NCBI_API_KEY` vào `~/.ebm-secrets/medical-ebm-automation.env` để mở tầng NCBI | `CAN_NCBI_API_KEY` |
| xác minh tồn tại quá 180 ngày | chạy lại thêm vòng **SẼ** sửa được | `CAN_CHAY_THEM_VONG` |
| lý do khác | xem tay | `CAN_XEM_TAY` |

⚠️ **ĐÍNH CHÍNH 10/09/2026 (đợt kiểm độc lập tuyến ĐỘ TIN CẬY):** bản trước của bảng này chỉ
có MỘT dòng cho "PMID chưa kiểm được rút bài" và ghi cứng *"chạy lại KHÔNG sửa được — cần
NCBI_API_KEY"* — đúng lời khuyên mà chính mục BH14 này sinh ra để cấm, và mâu thuẫn với chuỗi
3 tầng đã mô tả ở Bước 2 (dòng ~118) và ở mục *"HẾT PHỤ THUỘC NCBI API KEY"* của `CLAUDE.md`.
Mã nguồn thật (`tools/so_xac_minh_nguon.py`, đổi 14/08/2026, khoá hồi quy bằng
`chot_hoi_quy_bai_hoc.py::bh14_khong_khuyen_viec_chac_chan_vo_ich`) đã tách hai nhánh từ lâu;
chỉ riêng bảng doctrine ở đây chưa theo kịp. Đã sửa lại cho khớp mã đang chạy.

> **Luật:** trước khi in một lời khuyên, hỏi *"làm theo lời này có thật sự đổi được trạng thái
> không?"*. Nếu không, phải nói rõ điều gì mới đổi được.

**(h) BH15 — ĐẾM MỤC, KHÔNG ĐẾM DÒNG LỖI.**

`verify_dashboard` sinh HAI dòng cho cùng một item khi nó vi phạm hai luật (vừa
`gradeLevel='na'` vừa "chỉ dựa Consensus"). Bản báo việc cũ dùng
`out.count("decision='apply'")` nên báo **64 mục** trong khi thực tế chỉ **49** — phóng đại
khối lượng việc của bác sĩ **31%**. Con số thổi phồng trong bản báo việc cũng là nói sai, và
nó khiến người ta hoãn một việc thật ra nhỏ hơn tưởng. Nay đếm qua `id_muc_apply()`.

**Cùng lớp lỗi, gặp HAI LẦN trong ngày:** ghép tên sản phẩm phái sinh. File sinh ra theo hai
quy ước (`WebDashboard_EBM_<chủ-đề>_...docx` và `<chủ-đề>_...docx`); chỉ khớp một dạng thì **14
bản CÓ ĐỦ file bị báo là "thiếu Word"** — đủ sức đẩy người ta đi dựng lại 14 tài liệu đã tồn
tại. Logic ghép nay gom vào `phai_sinh_lech()`, không đo lại bằng tay nữa.

> **Luật đo lường:** trước khi báo một con số, hỏi *"tôi đang đếm ĐƠN VỊ nào — mục, dòng, hay
> file?"* và *"cách ghép của tôi có bỏ sót biến thể tên nào không?"*. Cả hai lỗi hôm nay đều
> sai theo hướng **thổi phồng việc**, không phải bỏ sót việc — nhưng cả hai đều làm bác sĩ
> hành động sai.

**(i) BH16 — CẢ 7 CHỐT BIẾN MẤT nếu mở Claude ở thư mục khác.**

Guard cũ là `[ -f tools/X.py ]` — đường dẫn **TƯƠNG ĐỐI**. Mở Claude ở thư mục con
(vd `medical-ebm-automation/`) thì guard sai ⇒ **không chốt nào chạy**, và vì mỗi lệnh kết
thúc bằng `; true` nên mã thoát vẫn 0.

> **Bác sĩ nhận đúng cùng một màn hình im lặng như khi mọi thứ đều tốt.** Đây là kiểu hỏng
> tệ nhất của một hệ giám sát: nó không báo sai — nó **biến mất**.

Vá: neo vào `$CLAUDE_PROJECT_DIR` (fallback `$PWD`) và **BÁO TO** khi không tìm thấy công cụ,
thay vì im lặng bỏ qua. Đã kiểm thật: chạy cả 7 lệnh hook nguyên văn từ `/private/tmp` —
trước vá thì 0/7 chạy và không một dòng báo; sau vá thì 7/7 chạy đúng.

**Ba lỗi BH14–BH16 cùng một họ, và đó là họ nguy hiểm nhất của hệ này:** hệ *nói sai với bác
sĩ* mà không sai một phép tính nào — khuyên việc vô ích, thổi phồng khối lượng, hoặc lặng lẽ
không chạy. Không lỗi nào trong ba lỗi này làm test đỏ; cả ba chỉ lộ ra khi có người hỏi
*"con số này thật sự đếm gì?"* và *"làm theo lời khuyên này có đổi được gì không?"*.

**(j) BH17 — dây chuyền tuyên bố "Bộ năm đã sẵn sàng" khi chỉ có 3/5.**

Dòng tổng kết in **VÔ ĐIỀU KIỆN**. Ca thật cùng ngày: `AnToanThuoc_EMA_PRAC_20260614` hỏng
bước ③ (chuỗi nối kiểu JS làm chết bộ dựng Word) nên mất cả ④ lẫn ⑤ — mà tiêu đề vẫn nói
"đã sẵn sàng". Bác sĩ đọc lướt sẽ tin gói đủ và **đem bản Word CŨ đi dùng cho người bệnh**.

Nay tiêu đề nói đúng: `── Bộ năm: 3/5 — THIẾU Word dạng HTML, PDF giữ màu ──`, và các ô
trống ghi rõ `(CHƯA SINH ĐƯỢC)`. Bước ④ hỏng nay **đổi mã thoát** (nó là một trong bộ năm đã
hứa) — riêng bước ⑤ PDF vẫn cố ý không đổi mã thoát vì là tiện ích đọc, đúng doctrine cũ.

**Bốn lỗi BH14–BH17 là MỘT HỌ, và là họ nguy hiểm nhất của hệ này:**

| | Hệ nói gì | Sự thật |
|---|---|---|
| BH14 | "chạy lại thêm vòng" | chạy lại không bao giờ sửa được |
| BH15 | "64 mục cần duyệt" | thật ra 49 |
| BH16 | *(im lặng — mọi thứ ổn)* | 0/7 chốt đã chạy |
| BH17 | "Bộ năm đã sẵn sàng" | chỉ có 3/5 |

**Không lỗi nào làm test đỏ. Không lỗi nào sai một phép tính.** Chúng chỉ lộ ra khi hỏi
*"con số này đếm ĐƠN VỊ gì?"*, *"làm theo lời khuyên này có đổi được gì không?"* và
*"câu tuyên bố này có điều kiện nào không, hay in ra bất kể kết quả?"*.

**(k) BH18 — BÁO ĐỘNG GIẢ trong hàng đợi quyết định của bác sĩ.**

`dang_ky_chu_de.doc_muc()` khoá dict theo PMID, nên khi một dashboard có NHIỀU item cùng
trích một nguồn thì chỉ item CUỐI theo thứ tự file được giữ — các item khác bị bỏ **im lặng**.

Đó là chuyện BÌNH THƯỜNG, không phải bất thường: một guideline (KDIGO 2024, ACC/AHA…) mang
hàng chục khuyến cáo, mỗi khuyến cáo có `decision` riêng. Đo được **21 ca** như vậy trong kho.

Hệ quả: phần so mâu thuẫn đem so một item **tuỳ ý** của bản này với một item **tuỳ ý** của bản
kia ⇒ tuyên bố "hai bản nói ngược nhau" trong khi chúng chỉ nói về **hai khuyến cáo khác nhau
của cùng một tài liệu**.

Đo toàn kho: **3/224 PMID chung bị ảnh hưởng**, và **2 trong số đó đã bị báo cho bác sĩ như
mâu thuẫn thật** (BenhThanMan PMID 38490803 · ViemGanB PMID 41186418). Sau vá: **14 → 12**
mâu thuẫn thật, 3 PMID chuyển sang nhóm riêng *"không so tự động được — bác sĩ đọc tay"*.

> **Luật:** khi gom dữ liệu theo một khoá, hỏi *"khoá này có thật sự DUY NHẤT không?"*. Ở đây
> PMID là **tài liệu**, không phải **khuyến cáo** — và cả hệ này nói về khuyến cáo.

**(l) BH19 — "🟢 CHỨNG CỨ còn hạn" dựa trên một tín hiệu KHÔNG có nghĩa đó.**

Chốt độ tươi kết luận từ `st_mtime` của file log. Nhưng hai script giám sát ghi dòng
`BẮT ĐẦU` vào log **NGAY khi khởi động**, trước khi làm bất cứ việc gì ⇒ một lượt chạy
**khởi động rồi chết** vẫn làm mtime tươi mới, và bác sĩ nhận `🟢 CHỨNG CỨ còn hạn`.

Từ khi `tu_khoi_dong.py` tự phóng mỗi phiên, đây thành **vòng lặp im lặng**:
phóng → hỏng → mtime tươi → "còn hạn" → không ai biết, tuần này qua tuần khác.
Bản thân log **ĐÃ chứa** câu trả lời (`KẾT THÚC … tổng thể=PASS | CÓ BƯỚC LỖI`) — chỉ là
chưa ai đọc. Nay `lan_chay_cuoi()` trả `(ngày, trạng_thái)` với 3 trạng thái phân biệt:
`PASS` · `LỖI` · `DANG_DO` (có BẮT ĐẦU mà không có KẾT THÚC).

> **Luật đọc tín hiệu:** trước khi dùng một dấu hiệu để kết luận, hỏi *"dấu hiệu này
> thật sự CÓ NGHĨA là điều tôi đang kết luận không?"*. `mtime` nghĩa là **"file vừa
> được ghi"**, KHÔNG phải **"công việc đã xong tốt"**.

**(m) BH20 — VÁ DỞ DANG của chính BH19, và hậu quả nặng hơn.**

BH19 sửa `kiem_do_tuoi_chung_cu` để đọc KẾT QUẢ lượt chạy thay vì chỉ nhìn `st_mtime`.
Nhưng `tu_khoi_dong.qua_han()` — dùng **CÙNG tín hiệu cho CÙNG mục đích** — thì bị bỏ sót.

Hậu quả nếu để nguyên còn nặng hơn BH19: script ghi `BẮT ĐẦU` ngay lúc khởi động ⇒ một lượt
**khởi động rồi chết** vẫn làm mtime tươi ⇒ `qua_han()` kết luận "còn hạn" ⇒ **KHÔNG phóng
lại**. BH19 chỉ làm bác sĩ *tưởng* còn hạn; BH20 làm giám sát **hỏng vĩnh viễn, không bao giờ
được thử lại**, và cũng không ai được báo.

Nay `tu_khoi_dong` gọi lại chính `lan_chay_cuoi()` — **một bản duy nhất** cho cùng một câu hỏi.

> **Bài học kép:**
> (a) khi vá một tín hiệu bị dùng sai nghĩa, phải tìm **MỌI** nơi dùng tín hiệu đó cho cùng
> mục đích — vá một chỗ có thể để lại chỗ tệ hơn;
> (b) hai công cụ hỏi cùng một câu phải dùng **CHUNG** một câu trả lời, nếu không chúng sẽ
> phân kỳ đúng như đã xảy ra ở đây.

**(n) BH21 + BH11 mở rộng — BÀI HỌC BH20 LẶP LẠI HAI LẦN NỮA trong cùng một vòng.**

**BH21 — hai parser của cùng một dữ liệu bất đồng.** BH13 vá gộp chuỗi nối JS cho
`build_dashboard_docx`, nhưng `array_field()` của cổng liêm chính thì bỏ sót. Từ 13/08 tới
14/08, bộ dựng Word đọc `references` của `AnToanThuoc_EMA_PRAC` ra **3** phần tử còn cổng đọc
**4** — một tài liệu tham khảo bị tách đôi, nửa sau chỉ là URL trần.

**BH11 mở rộng — danh sách viết cứng đã mục.** Chốt cũ liệt cứng 4 tên tool nên chỉ phủ 4/8, và
`verify_dashboard.py` — **cổng liêm chính, tool quan trọng nhất bộ** — lệch bản mà chốt vẫn xanh.
Nay tự dò danh sách từ thư mục nguồn. Vừa mở rộng đã bắt ngay **2 tool thiếu bản vá UTF-8**
(`check_topic_relevance`, `surveillance_scan`) — cả hai đều in tiếng Việt nên sẽ chết giữa chừng
trên Windows.

Kèm theo, chốt được chỉnh cho **đúng mức**: chỉ đòi bản vá UTF-8 ở file THẬT SỰ in ký tự ngoài
ASCII. `test_verify_dashboard_source_gate.py` không in ký tự nào như vậy, nên đòi nó là tự tạo
báo động giả — đúng thứ chốt này sinh ra để diệt.

> **Bài học BH20 nay đã lặp ba lần trong hai vòng.** Kết luận: mỗi khi vá một logic dùng chung,
> phải **liệt kê mọi nơi dùng nó** và vá đồng thời — và mọi danh sách kiểm phải **tự dò**, vì
> danh sách viết cứng luôn mục đúng vào lúc có thành phần mới quan trọng nhất.

**(o) BH22 — quy trình đồng bộ tự đẩy CHÍNH file sao lưu của mình vào nơi chạy.**

`BO_QUA` so trên `f.parts` (thành phần đường dẫn) nên không bao giờ bắt được một TÊN FILE như
`verify_dashboard.py.bak-20260814-005720`. Đo được **8 file sao lưu** đã nằm trong thư mục skill
ĐANG CHẠY, ngay cạnh bản sống.

Không gây lỗi chạy (đuôi `.bak-*` không import được), nhưng kho phình mãi và **một bản CŨ của
công cụ an toàn nằm cạnh bản mới** gây hiểu nhầm cho bất kỳ ai mở thư mục đó ra xem. Đã thêm
`BO_QUA_MAU` lọc theo mẫu tên, và dọn 8 file — bản gốc ở `sync/` giữ nguyên, chỉ xoá bản sao
chép thừa (không bao giờ xoá bản duy nhất).

Điểm tốt cần ghi nhận: `.gitignore` đã có `**/*.bak-*` từ trước nên **0 file sao lưu lọt vào
git** — repo sạch. Rào chắn ở tầng git đã đúng; chỗ hở nằm ở tầng đồng bộ runtime.

> **Bài học:** bộ lọc phải kiểm ĐÚNG TRỤC. `BO_QUA` kiểm *thành phần đường dẫn* (`__pycache__`)
> nhưng thứ cần chặn lại là *mẫu tên file* — hai trục khác nhau, và một bộ lọc đúng trục này
> im lặng vô dụng ở trục kia.

**(p) BH23 — một dashboard bị LOẠI IM LẶNG khỏi đăng ký chủ đề.**

`tach_ten()` bắt buộc dạng `<nhóm>_<chủ-đề>_<ngày>`, nên `WebDashboard_EBM_Uptodate_20260607.html`
(không có phần chủ đề) KHÔNG khớp regex và bị bỏ qua — **vô hình luôn với phần dò mâu thuẫn**.
Đo được **61/62** tách được, đúng một bản rơi ra mà **không một dòng báo**.

Nay phần tên chủ đề là TUỲ CHỌN; thiếu thì lấy chính tên nhóm làm lát cắt. Sau vá **62/62**, và
số mâu thuẫn **không đổi (12)** — tức vá không sinh dương tính giả.

Chốt BH23 kiểm trên dữ liệu SỐNG: **mọi** dashboard trong kho phải tách được tên, nên một quy
ước đặt tên mới trong tương lai sẽ đỏ ngay thay vì lặng lẽ rơi ra.

> **Ba lỗi BH16 · BH22 · BH23 cùng một họ:** thứ bị loại thầm lặng nguy hiểm hơn thứ báo lỗi,
> vì **không ai đi tìm cái mình không biết là đang thiếu**. Với mọi bộ lọc/regex/danh sách, phải
> hỏi: *"cái gì rơi ra khỏi đây, và tôi có được báo không?"*

**(q) BH24 — cùng một nguồn, chỉ khác CÁCH GHI, nhận hai mức bảo đảm khác hẳn.**

Mục `doi:` được xác minh **metadata qua Crossref**; mục `url:` chỉ được kiểm **"địa chỉ có phản
hồi"**. Nhưng **17 định danh** trong kho là DOI viết dạng `https://doi.org/10.…` nên rơi vào
nhánh yếu — và mức yếu hơn đó **không hề được nói ra**.

> Đây là dạng nguy hiểm riêng: hệ đưa ra một bảo đảm **THẤP HƠN mức nó ngụ ý**, trong khi sổ vẫn
> ghi "đã xác minh".

Nay nhận diện link `doi.org/` và `/doi/`, rút DOI rồi xác minh qua Crossref. Crossref không phân
giải được thì **lùi về kiểm HTTP** — đúng mức bảo đảm cũ, không tự hạ thành "chưa xác minh"
(HTTP vẫn là bằng chứng thật, chỉ yếu hơn). 5 bản ghi đã bị hạ cấp được **gỡ khỏi sổ để xác
minh lại** (fail-closed), có sao lưu.

Cùng vòng, hai giả thuyết khác đã kiểm và **loại**: `gom_nguon` dùng `vd.field()` nên xử lý cả
hai kiểu nháy; **0/1701** định danh bị bỏ qua vì sai định dạng.

**(r) 14/08 — TÔI VI PHẠM CHÍNH LUẬT CỦA MÌNH, và chốt vẫn xanh trên mã hỏng.**

Bản vá BH24 thiếu `import re` ở cấp module ⇒ `xac_minh_mot()` ném
`NameError: name 're' is not defined` ngay dòng đầu nhánh vừa vá, và **cả lượt quét nền chết**.

Nhưng chốt BH24 vẫn **XANH**, vì nó chỉ (a) thử regex ở BÊN NGOÀI và (b) tìm chuỗi
`doi_rut_tu_url` trong mã nguồn — **không hề gọi vào `xac_minh_mot`**. Đó đúng là bẫy TAUTOLOGY
mà luật 2 của chính file chốt cấm, và tôi vừa mắc nó khi viết chốt cho bản vá của mình.

> **Một chốt không chạy qua đúng đường nó canh thì KHÔNG canh gì cả — tệ hơn, nó phát ra sự
> yên tâm sai.** Đây chính là kiểu hỏng đã gặp ở guardrail G3/G8 (R3–R7 tautology), nay tái
> hiện ở tầng công cụ.

Đã thêm **luật 4** vào `chot_hoi_quy_bai_hoc.py`: *phải THỰC SỰ GỌI vào đường mã mình canh*.
BH24 nay dùng một `vd` giả NGOẠI TUYẾN để đi hết nhánh `url → doi`, và sẽ đỏ ngay với lỗi kiểu
`NameError`. Kiểm lại: DOI-trong-URL → `crossref` kèm DOI đã rút; URL thường → `http`.

**(s) BH25 — cổng GỘP hai trục mà GRADE cố ý TÁCH. Phát hiện quan trọng nhất về mặt khái niệm.**

GRADE có **hai trục ĐỘC LẬP**:

| Trục | Giá trị |
|---|---|
| **Độ MẠNH khuyến cáo** | strong (1) · conditional (2) |
| **Chất lượng CHỨNG CỨ** | high · moderate · low · very low |

Một **khuyến cáo MẠNH trên chứng cứ chất lượng THẤP** là kết quả GRADE hợp lệ và phổ biến —
đúng những tình huống đe doạ tính mạng mà bỏ sót thì tai hoạ.

Cổng cũ chặn thẳng mọi `gradeLevel` khác `na`, nên ép một lựa chọn **sai cả hai đường** với
`SuyTim_NoiTiet ITEM-05` (nhận biết khủng hoảng thượng thận):
• giữ `low` → bị chặn, dù Endocrine Society viết nguyên văn **"We recommend"** (= MẠNH);
• đổi sang `na` → **nói sai về nguồn**, vì hướng dẫn đó *có* dùng GRADE.

Nay chứng cứ chất lượng thấp **vẫn được miễn NẾU** nguồn tuyên bố khuyến cáo MẠNH, và điều đó
phải có **bằng chứng văn bản** trong `gradeSource` (`"we recommend"`, `GRADE 1A/1B/1C`, "khuyến
cáo mạnh"…) — không chấp nhận chỉ dán nhãn. Dấu hiệu **CÓ ĐIỀU KIỆN** xuất hiện là chặn ngay,
kể cả khi cùng trường có chữ "recommend": khi hai dấu hiệu cùng có, mức thấp hơn mới đáng tin.

⚠️ **Bản đầu của chính bản vá này đặt nhánh mới TRƯỚC phép kiểm `design`** ⇒ mở lại đúng lỗ hổng
**BH03** (một văn bản `Consensus` gõ thêm nhãn là đi qua cổng). Bắt được nhờ ca biên trong bộ
kiểm 9 ca, đã sửa thứ tự. Bài học: **nới một cổng an toàn thì phải chạy lại TOÀN BỘ ca biên cũ,
không chỉ ca mới.**

**Đã áp cho ITEM-05:** `gradeSource` sửa cho đúng nguồn, khai `normativeBasis:"guideline-strong-rec"`,
**giữ nguyên `gradeLevel:'low'`** — không falsify. Bản đó nay 0 mục bị chặn.

**(t) 14/08 — LÔ 22 MỤC bác sĩ duyệt: khai `normativeBasis` (8) + hạ `decision` (14).**

Mục 'apply' bị cổng chặn: **56 → 49 → 40 → 27**.

**Khai `normativeBasis`, GIỮ `decision` — 8 mục có bằng chứng quy phạm trích được nguyên văn:**

| Mục | Căn cứ trong `gradeSource` | basis |
|---|---|---|
| `AnToanThuoc_MHRA` ITEM-01/02 | *"Khuyến cáo cơ quan quản lý (MHRA/CHM/PEAG)"* | `drug-label` |
| `CapNhatTuan` ITEM-04 | *"AGS 2023 — **bảng tiêu chí** đồng thuận"* | `guideline-explicit-criteria` |
| `COPD` ITEM-01 | *"**Tiêu chuẩn chẩn đoán** GOLD"* | `official-classification` |
| `COPD` ITEM-02 | *"**Khung đánh giá** GOLD (bỏ C/D, gộp E)"* | `official-classification` |
| `VKDT` ITEM-27 | *"**Quyết định quản lý dược chính thức** (regulatory action)"* | `drug-label` |
| `VKDT` ITEM-36 | *"**Nhãn thuốc được FDA phê duyệt** (Boxed Warning + Contraindications)"* | `contraindication` |
| `VKDT` ITEM-01 | *"**Tiêu chuẩn phân loại** ACR/EULAR 2010"* | `official-classification` |

Ba mục VKDT phải **sửa `design` trước** — chúng bị gắn nhãn `Consensus` trong khi nguồn là nhãn
thuốc FDA / hành động pháp quy / tiêu chuẩn phân loại. Đây đúng vấn đề đã ghi ở mục (d):
**`design` là chuỗi tự do và nó đang nói sai về nguồn.**

**Hạ `decision` → `consider` — 14 mục KHÔNG phải văn bản quy phạm:**
nghiên cứu đơn lẻ (`RCT gốc`, `RCT n=17`, `RCT thí điểm nhãn mở`), phân tích gộp không có bảng
GRADE, gộp nghiên cứu quan sát, nghiên cứu kiểm định công cụ, Cochrane không trích được độ chắc
chắn — và `ViemDaDayThanKinh ITEM-01` vì **AAN Mức C là mức YẾU** trong hệ AAN.

> Với nhóm này KHÔNG được tự gán `gradeLevel` để "cứu" mức `apply` — đó là lỗi tự gán mức (R4).
> Hạ `decision` mới là đường đúng.

⚠️ **Bẫy kỹ thuật đã gặp khi sửa hàng loạt:** neo bằng ~42 ký tự ngữ cảnh **trùng nhau giữa các
mục** (11/14 mục hỏng ở lần đầu). Cách chắc chắn: định vị theo `id` của mục rồi giới hạn phạm vi
tới `id` kế tiếp mới thay. Sửa dữ liệu y khoa hàng loạt thì neo phải **duy nhất theo cấu trúc**,
không dựa vào ngữ cảnh văn bản.

**(u) Lô SuyTim + BH26 — mục 'apply' bị chặn: 56 → 49 → 40 → 27 → 16.**

**ITEM-01 (×3 bản) — nâng, GIỮ `apply`:** nguồn là *"AHA/ACC/ESC/WHF Expert Consensus Document:
**Second Universal Definition** of Heart Failure (2026)"* — đây là **văn bản ĐỊNH NGHĨA** do bốn
hiệp hội cùng ban hành, đúng loại tiêu chuẩn phân loại (cùng hạng với ICHD-3, ACR/EULAR 2010).
`design` sửa cho đúng bản chất + `normativeBasis:"official-classification"`.

**ITEM-02 · 37 · 42 — hạ xuống `consider`:**
• ITEM-02: `gradeSource` **TỰ KHAI** *"là lộ trình đồng thuận, KHÔNG phải guideline có class/level"*
• ITEM-37: bài báo tạp chí đề xuất khung thích ứng
• ITEM-42: *position statement* của HFA/ESC — không có class/level

**BH26 — NEO SỬA HÀNG LOẠT.** Hôm nay hỏng **hai lần theo hai kiểu**:
1. neo bằng ~42 ký tự **ngữ cảnh** → trùng giữa các mục (11/14 mục hỏng);
2. chuyển sang neo `{id:'ITEM-xx'}` → **vẫn trúng nhầm**, vì mỗi dashboard có một **khối chú
   thích schema** mở đầu bằng đúng dạng đó (`design:'Guideline'|'Meta'|'RCT'|…`). ITEM-01 khớp
   **2 chỗ**.

May là lần 2 không hỏng dữ liệu (regex đòi đúng `'Consensus'` nên khối schema không khớp) —
nhưng đó là **may, không phải thiết kế**. Đã kiểm lại: khối schema nguyên vẹn ở cả 3 file.

> **Neo an toàn duy nhất: chính đoạn do `split_items()` trả về** — đúng thứ mọi công cụ khác
> coi là một mục. BH26 canh tiền đề của cách đó: mỗi đoạn phải xuất hiện **đúng một lần** trong
> file, nếu không thì neo bằng đoạn cũng không an toàn.

**(v) Lô guideline — mục 'apply' bị chặn: 16 → 2. MỤC 2 gần như đóng.**

**NÂNG (3 mục) — bản chất quy phạm, giữ `apply`:** `CKM ITEM-01` khung **phân giai đoạn CKM**
(AHA 2023) → `official-classification` · `COPD ITEM-03` **bảng phác đồ khởi trị GOLD theo nhóm
ABE** → `guideline-explicit-criteria` · `CapNhatTuan ITEM-05` **bộ tiêu chí STOPP/START v3**,
cùng hạng AGS Beers → `guideline-explicit-criteria` (phải sửa `design` từ `Consensus`).

**HẠ (11 mục) — nguồn CÓ phân hạng nhưng item KHÔNG ghi mức:** GOLD ITEM-04/13,
COPD_TimThanChuyenHoa ITEM-20/21/22/24/25, EULAR RA, AAN, ADA, PhatAmPhuAm. `gradeSource` chỉ
nói *"nguồn không cung cấp GRADE riêng"* hoặc *"item này tóm tắt"*.

> **Phân biệt phải giữ cho rõ:** *"nguồn KHÔNG phân hạng"* (→ có thể là quy phạm, xét
> `normativeBasis`) khác hẳn *"nguồn CÓ phân hạng nhưng ta chưa trích"* (→ thiếu dữ kiện, phải
> hạ). Trộn hai thứ này là con đường ngắn nhất tới việc tự gán mức (R4).

🔴 **HAI MỤC CỐ Ý GIỮ LẠI CHO BÁC SĨ** — `VKDT ITEM-13` · `ViemKhopDangThap ITEM-08`: **sàng lọc
lao tiềm ẩn + HBV/HCV BẮT BUỘC trước b/tsDMARD**. Nguồn EULAR không ghi mức trong dashboard,
nhưng đây là yêu cầu an toàn trước thuốc ức chế miễn dịch — hạ xuống "cân nhắc" có thể khiến bỏ
sót sàng lọc và làm bùng lao/viêm gan B. Máy không nên tự chọn chiều ở đây.

**(c) `tools/tu_sua_chua.py --ap-dung` — TỰ VÁ phần máy móc.**
Skill lệch bản · kho plugin thiếu · cấu hình sai interpreter. **KHÔNG** đụng nội dung
y khoa: ba việc bị cấm tự động vĩnh viễn là đổi `decision`, đổi `gradeLevel`, và phân
xử khi hai dashboard nói ngược nhau.

> **BẰNG CHỨNG vì sao ba việc đó phải cấm — xảy ra ngay 13/08 với chính công cụ tôi
> vừa viết.** `tools/trinh_muc_can_duyet.py` bản đầu xét dấu hiệu "yếu" TRƯỚC dấu hiệu
> "quy phạm", mà trường `design` trong dữ liệu thật gắn nhãn `Consensus` cho **cả cảnh
> báo hộp đen FDA về JAK inhibitor** (PMID 35081280) **lẫn chống chỉ định leflunomide
> trên nhãn thuốc FDA**. Kết quả: 8 nguồn quy phạm bị xếp vào nhóm "nên HẠ decision".
> Nếu lớp ngữ nghĩa đó có quyền ghi, nó đã hạ hai cảnh báo an toàn.
> Đã vá (xét NGUỒN trước THỂ LOẠI, thêm nhóm riêng `ĐỒNG THUẬN`): 20 mục "yếu thật"
> rút về đúng **2** — khớp phân tích tay từng mục.
> Bài học: `design` là chuỗi tự do, **không dùng nó làm căn cứ quyết định an toàn**.

**(u) BH30 · BH31 · BH32 — 14/08, vòng lặp kiểm tra–hoàn thiện. Một họ lỗi duy nhất: CON SỐ
KHÔNG ĐO THỨ NÓ TỰ NHẬN LÀ ĐANG ĐO.** Cả ba đều lọt qua mọi chốt trước đó vì công cụ vẫn chạy,
vẫn in ra một kết quả trông hợp lệ.

| Mã | Lỗi | Vì sao vô hình | Hại theo hướng |
|---|---|---|---|
| **BH30** | `dang_ky_chu_de.tach_ten()` trả **tên chủ đề** ở vị trí **ngày** (lệch một bậc sau bản vá "chủ đề là tuỳ chọn"). Cache dò mâu thuẫn khoá theo giá trị đó ⇒ 3 bản `SuyTim_TongHop` sập vào MỘT khoá; cặp 04/08⟷05/08 hoá thành so bản 11/08 với **chính nó** ⇒ vĩnh viễn 0 mâu thuẫn | tổng số mâu thuẫn **không đổi** (11) vì kho tình cờ không có mâu thuẫn giữa các bản SuyTim | **bỏ sót** |
| **BH31** | Cổng liêm chính **không hề kiểm rút bài**; kết luận dương tính đã nằm trong sổ mà không ai đọc | gói FAIL/PASS đúng ở mọi luật khác nên trông như đã soi đủ | **bỏ sót** |
| **BH32** | `kiem_do_tuoi_chung_cu` lấy `max(ngày)` toàn kho rồi in *"🟢 CHỨNG CỨ còn hạn"* — nghĩa thật chỉ là *"có ít nhất MỘT gói mới"* | 🟢 là màu người ta không kiểm lại | **yên tâm giả** |

*Số đo 14/08 cho BH32:* gói mới nhất **1 ngày** tuổi ⇒ in 🟢, trong khi **37/59 chủ đề đã quá 35
ngày**, trung vị **45 ngày**. Nay in kèm trung vị + 5 chủ đề lâu nhất, và ngưỡng báo động để
**riêng ở 120 ngày** — cố ý cao hơn nhiều, vì ở nhịp làm việc thật phần lớn chủ đề luôn quá 35
ngày; lấy 35 làm ngưỡng đỏ sẽ khiến mỗi phiên đều đỏ và bác sĩ học cách bỏ qua, lúc đó cảnh báo
thật cũng chìm theo.

> **Luật rút ra, áp cho mọi chốt về sau:** khi đọc kết quả một công cụ, hỏi **"nó đã chạy tới
> luật nào"** và **"con số này là của TẬP HỢP hay của MỘT phần tử"** — chứ không chỉ đếm số lỗi.
> Một chỉ số gộp (`max`/`min`/"mới nhất") **không bao giờ** được trình bày như kết luận về toàn bộ.

**(v) BH33 — ĐỔI KIỂU GHI ĐỊNH DANH KHÔNG ĐƯỢC LÀ ĐƯỜNG THOÁT CỔNG.** Chuỗi 3 tầng chỉ nhận
**PMID** ⇒ **540 DOI** trong kho (gần nửa số định danh) **chưa từng được kiểm rút bài lần nào**,
mà sổ vẫn xếp chúng vào "còn hiệu lực".
*Bị chạm vào ngay trong ngày:* `ViemGanB_DieuTri` ITEM-05 trích PMID 30267080 (đã rút) được sửa
thành trích DOI `10.1001/jamaoncol.2018.4070`. Tra PubMed + Crossref: **hai định danh đó là CÙNG
MỘT BÀI**, và Crossref ghi `updated-by: retraction → 10.1001/jamaoncol.2019.0576`. Nội dung
không đổi, chỉ có **cảnh báo tắt đi**.
*Đã vá:* tầng Crossref (`app/sources/crossref_retraction.py`) + `kiem_rut_bai_theo_doi()`;
`con_hieu_luc()` đòi dấu vết kiểm rút bài cho **DOI, kể cả DOI ghi dạng URL** (lý lẽ BH24),
**không** đòi với URL thuần. `correction`/`erratum` cố ý KHÔNG tính là rút bài.
> **Luật:** *một định danh mang bảo đảm nào thì phải chịu đúng phép kiểm của bảo đảm đó, bất kể
> nó được ghi bằng kiểu gì.*

⚠️ **Cách sửa ĐÚNG cho *retract-and-replace*:** đối chiếu số liệu với **bản đã thay** rồi trích
đúng bản đó — KHÔNG đổi sang một định danh khác của **chính bài đã rút**, cũng KHÔNG xoá mục.

*Đã kiểm bằng đột biến từng chốt:* tái hiện lỗi cũ ⇒ BH30/BH31/BH32 đỏ; khôi phục bản vá ⇒ xanh.


## 6. Biến thể đầu ra theo chủ đề

### An toàn thuốc

Bắt buộc có:

- thuốc/nhóm thuốc;
- cảnh báo/thay đổi nhãn đã xác minh;
- nhóm nguy cơ;
- hành động kê đơn;
- theo dõi;
- điều không nên suy diễn;
- nguồn quản lý dược chính thức và ngày.

### Antibiotic stewardship

Bắt buộc có:

- hội chứng;
- khi nào cần/không cần kháng sinh;
- lựa chọn/giới hạn theo nguồn chính thức;
- AWaRe nếu phù hợp và có thể xác minh;
- cấy/xuống thang/chuyển viện nếu liên quan;
- liều và thời gian chỉ khi nguồn xác minh.

### Thang điểm/công cụ

Bắt buộc có:

- mục đích và quần thể;
- phiên bản/công thức/cut-off đã xác minh;
- cách diễn giải;
- hành động đi kèm;
- cảnh báo dùng sai;
- không dùng thay đánh giá lâm sàng hoặc trì hoãn cấp cứu.

### Thẩm định guideline/nghiên cứu

Bắt buộc có:

- câu hỏi nghiên cứu hoặc phạm vi guideline;
- loại nguồn;
- công cụ thẩm định phù hợp;
- kết quả thẩm định dựa trên thông tin có thể kiểm tra;
- hệ quả đối với mức tin cậy và áp dụng tại Việt Nam.

## 7. Tích hợp Dashboard Master chỉ khi người dùng yêu cầu

Web Dashboard "Evidence Workbench" độc lập theo vấn đề cụ thể (lớp Clinical Quick View là màn hình tóm tắt mặc định) được tạo mặc định khi tạo file được, theo mục 5A.

Chỉ khi người dùng nói rõ cần **đưa nội dung đã xác minh vào Dashboard Master** hoặc **theo dõi triển khai**, mới bổ sung:

- mã bản ghi quản trị phù hợp;
- bảng PATCH/Change Log;
- Action Tracker;
- CỔNG A/CỔNG B;
- đồng bộ Excel Master/WebApp Master.

Không mặc định coi Web Dashboard theo vấn đề cụ thể là bản ghi đã được duyệt vào Master.

## 8. Checklist trước khi trả lời

- Đã xác định đúng vấn đề cụ thể và quần thể chưa?
- Đã tìm/xác minh nguồn hiện hành cho nội dung có thể thay đổi chưa?
- Đã quét/đối chiếu đủ các lớp nguồn bắt buộc trong `references/13-source-universe.md` và ghi rõ lớp nào thiếu nếu source health PARTIAL/FAIL chưa?
- Đã ghi đúng tiêu đề, tổ chức, ngày/phiên bản và quần thể của nguồn chưa?
- Đã giữ nguyên grading của nguồn, không tự gán GRADE chưa?
- Đã tách “điểm mới” khỏi “kiến thức nền hiện hành” chưa?
- Đã nêu hành động, monitoring, cờ đỏ/chuyển tuyến khi cần chưa?
- Đã phân tích nhóm đặc biệt liên quan chưa?
- Đã ghi rõ nội dung chưa đủ để thay đổi chưa?
- Đã tạo Web Dashboard độc lập từ template MẶC ĐỊNH `web-dashboard-evidence-workbench.html` (Evidence Workbench; hoặc `web-dashboard-dark-analyst.html` khi bác sĩ yêu cầu) với `DATA.standards` đã điền đủ, và chạy TRỌN dây chuyền tự động (cổng liêm chính → thư viện → phái sinh) chưa? (tab `Chuẩn & chất lượng` để rà nội dung này chỉ hiện trên Evidence Workbench — xem đính chính ở 5A)
- Đã tránh tạo ID quản trị hoặc cập nhật Dashboard Master khi người dùng không yêu cầu chưa?
- Đã dùng tài liệu tham khảo có thể truy nguyên chưa?
- Nếu câu hỏi về hiệu quả can thiệp: đã trình bày khối PICO đủ 5 dòng và trích hiệu số đúng như nguồn (point estimate + CI/p) chưa?
- Đã tự nhận diện loại câu hỏi và chọn đúng khung (PICO/PECO/chẩn đoán/tiên lượng/tần suất/định tính/dịch vụ) và nêu rõ khung đã dùng chưa? (xem 5C)
- Đã chạy `tools/verify_dashboard.py --online --strict-sources` và PASS (PMID/DOI phân giải, nguồn còn mới, `DATA.standards` đủ, có disclaimer, không PII) trước khi giao chưa? (xem 5D)
- Nếu dùng cụm “áp dụng trực tiếp” hoặc nạp/thẩm định thẻ `decision="apply"` trong `EBM_MASTER`: đã chạy/đối chiếu `medical-ebm-automation/tools/verify_direct_clinical_practice_readiness.py` và không còn `BLOCKED_FOR_DIRECT_USE` cho thẻ đó chưa? (xem `references/12-direct-practice-readiness.md`)
- Nếu cập nhật có thuốc cho người cao tuổi/đa thuốc: đã chạy `tools/drug_safety_scan.py` + đối chiếu Beers/STOPP qua skill người cao tuổi chưa? (xem 5E)
- Đã tự sinh 3 sản phẩm phái sinh (tờ dặn/slide/TikTok) vào `derivatives/` và (khi có khuyến cáo đổi thực hành) điền khối `etd` cho Dashboard chưa? (xem 5D)
- Đã điền/rà `DATA.standards` gồm thứ bậc nguồn, chuẩn báo cáo, công cụ thẩm định, ngày tìm kiếm, an toàn, Việt Nam và truy nguyên từng item chưa?
- Đã nêu cả hai chiều khi chứng cứ không đồng nhất, và đánh dấu `[CẦN BỔ SUNG]` khi chỉ có đồng thuận/nguyên lý chưa?
- Đã ghi nguồn dạng văn bản thường (tác giả/tổ chức + năm + tạp chí) và rà soát để KHÔNG còn thẻ markup trích dẫn/mã kỹ thuật thô lẫn trong câu trả lời chưa?
- Nếu là giám sát định kỳ: `source_health=PASS`, runtime status, canary online và deployment gate đã đủ chưa? Nếu chưa, đã giữ nhãn `BLOCKED_FOR_DEPLOYMENT`/`PARTIAL`, giữ watermark và chặn Hub chưa?

## 9. Tài nguyên kèm theo

- `references/01-nguon-va-xac-minh.md`
- `references/02-cong-cu-tham-dinh-va-grade.md`
- `references/03-thich-ung-viet-nam.md`
- `references/04-thuoc-khang-sinh-va-cong-cu.md`
- `templates/mau-cap-nhat-nhanh.md`
- `templates/mau-cap-nhat-chuyen-sau.md`
- `templates/web-dashboard-evidence-workbench.html` ⭐ TEMPLATE MẶC ĐỊNH (Evidence Workbench, nền sáng; có EtD + tab Chuẩn & chất lượng; chrome tự sinh từ DATA)
- `templates/web-dashboard-dark-analyst.html` (mẫu KHI YÊU CẦU — nền tối, CÙNG schema DATA)
- `templates/web-dashboard-van-de-cu-the-clinical-quick-view.html` (một-cột cũ, chỉ khi yêu cầu riêng)
- `templates/web-dashboard-record-schema.csv`
- `references/05-web-dashboard-clinical-quick-view.md`
- `references/06-pico-va-trich-dan.md`
- `references/07-mo-hinh-cau-hoi-va-khung-thay-the.md`
- `references/08-xuat-san-pham-phai-sinh.md`
- `templates/phai-sinh-to-dan-nguoi-benh.md`
- `templates/phai-sinh-kich-ban-tiktok.md`
- `tools/verify_dashboard.py` (cổng kiểm liêm chính + xác minh PMID/DOI + `--strict-sources`; cờ opt-in `--check-topic`)
- `tools/check_topic_relevance.py` (opt-in: LLM chấm item lạc chủ đề — chỉ cảnh báo, cần `ANTHROPIC_API_KEY`)
- `tools/build_library.py` (thư viện chỉ mục cập nhật → evidence-library.html)
- `tools/make_derivatives.py` (tự sinh tờ dặn người bệnh / dàn ý slide / kịch bản TikTok → derivatives/)
- `references/09-an-toan-thuoc-overlay.md` · `tools/drug_safety_scan.py` · `data/drug_flags.json` (lớp phủ Beers/STOPP)
- `references/10-giam-sat-dinh-ky.md` · `tools/surveillance_scan.py` (giám sát PubMed theo watchlist)
- `references/11-guideline-bo-y-te-vn.md` (bản địa hóa Bộ Y tế VN)
- `references/12-direct-practice-readiness.md` (cổng phân loại READY_FOR_PHYSICIAN_DIRECT_USE / REVIEW_REQUIRED / BLOCKED_FOR_DIRECT_USE; nối với `medical-ebm-automation/tools/verify_direct_clinical_practice_readiness.py`)
- `references/13-source-universe.md` (ma trận lớp nguồn bắt buộc: bibliographic core · guideline/HTA · high-impact journals · trial registries · drug safety · retraction/integrity · full-text/citation context)
- `quality/acceptance-checklist.md`
- `quality/web-dashboard-acceptance-checklist.md`

Ngoài thư mục skill (dùng chung với các skill/quy trình EBM khác — KHÔNG nhân bản vào đây, chỉ tham chiếu):
- `tools/xuat_goi_cap_nhat.py` — **lệnh duy nhất** của chuỗi tự động: sinh đồng thời bộ năm (dashboard · bản đọc · Word · Word-dạng-HTML · PDF giữ màu) từ cùng một khối `DATA`
- `tools/docx_sang_pdf_giu_mau.py` — bước ⑤: đọc màu từ chính `.docx` rồi in PDF bằng Chrome headless (pandoc bỏ hết màu nền ô nên bước ④ không dùng được cho việc này)
- `data/sources.json` + `tools/tuyen_bo_do_phu.py` — sổ đăng ký nguồn máy-đọc thật (PubMed · Retraction Watch ngoại tuyến · Crossref · Europe PMC · openFDA · OpenAlex · ClinicalTrials.gov+preprint · trạm web hội) và bộ sinh khối "TUYÊN BỐ ĐỘ PHỦ" trung thực từ chính sổ đó; `build_ban_doc_chung_cu.py` tự nhúng khối này vào footer bản đọc — xem `references/13-source-universe.md` §ĐÍNH CHÍNH 10/09/2026
- `tools/sources_health.py` · `tools/giam_sat_to_chuc.py` — kiểm sức khoẻ định kỳ và bật trạm web hội (chỉ chạy trên máy thật, ngoài sandbox)
- `EBM_MASTER/tools/sync_all.py` — **KHÔNG còn tự chạy** (đổi 2026-08-05); chỉ khi bác sĩ yêu cầu
- `EBM-Dashboards/tools/reskin_dashboards.py` — áp lại vỏ template chuẩn (EW/DA) cho MỌI dashboard đã xuất bản khi bố cục/CSS template đổi (bóc khối `DATA`, bọc vỏ mới, giữ nguyên dữ liệu, tự backup).

---

## Chốt kiểm đầu ra 2 LỚP — Med-PaLM (BẮT BUỘC, ngay trước khi trả lời)
Skill chạy độc lập (không qua nhạc trưởng) → **tự áp** chốt kiểm 2 lớp như agent `tham-dinh-dau-ra`.
- **Lớp 1 — LIÊM CHÍNH (R1–R7):** nguồn PMID/DOI hoặc nhãn thiếu · KHÔNG PII · không tự "áp dụng cho BN" (dừng Cổng A) · không tự gán GRADE/độ mạnh khi nguồn không cấp · tách độ chắc chứng cứ vs độ mạnh khuyến cáo · nhãn `[CẦN…]` đúng chỗ · disclaimer cuối.
- **Lớp 2 — CHẤT LƯỢNG Med-PaLM (Q1–Q7):** Q1 dễ đọc (đúng đối tượng nhận) · **Q2 đúng đắn** (khớp guideline/đồng thuận — nghi sai → CHUYỂN BÁC SĨ) · Q3 đầy đủ-an toàn (không sót cờ đỏ/CCĐ/tương tác/chỉnh liều/theo dõi) · Q4 không thiên kiến nhóm · **Q5 nguy cơ hại** (hại nặng không cảnh báo → CHUYỂN BÁC SĨ) · Q6 cập nhật · Q7 thẩm quyền nguồn (cảnh giác tạp chí săn mồi). Bản chuẩn: `.claude/agents/_CHUAN-CHAT-LUONG-MEDPALM.md`.
- Còn 🔴 ở lớp nào → **sửa trước khi trả**; **Q2/Q5 đỏ → nêu cờ "cần bác sĩ phán định"**. Tự-kiểm cùng phiên (giảm mù chung, KHÔNG khử thiên lệch) — rào cứng cuối vẫn là bác sĩ.

**"Cần bác sĩ kiểm chứng."**


## CHỐNG THIÊN LỆCH CÁI MỚI + KỶ LUẬT TRÍCH SỐ (PHA 4 LÔ G/H, 15/08/2026)

**G-1** Một RCT ĐƠN LẺ không được tự xếp `apply` — trừ khi trả lời câu hỏi chưa từng có
chứng cứ, hoặc là tín hiệu an toàn từ cơ quan quản lý dược.
**G-2** Trước khi đề xuất đổi thực hành: đối chiếu guideline hiện hành + SR gần nhất
(`kiem_chung_cu_vuot_qua.py`); ghi rõ nghiên cứu mới *củng cố* hay *mâu thuẫn* khối chứng cứ.
**G-3** Mâu thuẫn khối chứng cứ hiện có → mặc định `notyet` («chưa đủ để đổi thực hành») kèm lý do.
**G-4** Kết cục THAY THẾ (surrogate) phải ghi rõ là surrogate.
**G-5** Mẫu không đại diện bệnh nhân ngoại trú VN (tuổi/đa bệnh/chủng tộc/tuyến) → ghi rõ ở vietnamFit.

**Trích số (checklist 9.1 — BẮT BUỘC cho item `apply` có hiệu số):** khai `effect.outcome_role`
(chính/phụ) · `effect.source_location` (bảng/hình nào — để đối chiếu ngược) · `measure` ĐÚNG nhãn
nguồn dùng (KHÔNG quy đổi HR↔RR↔OR — lớp so nhãn `kiem_so_lieu.py` sẽ bắt) · ITT/mITT/PP ·
phân nhóm phải nêu định-trước + kiểm tương tác · ghi cả hiệu số tuyệt đối khi nguồn có.

**Toàn văn (LÔ D):** item sắp `apply` phải thẩm định TOÀN VĂN hợp pháp (PMC OA · Europe PMC ·
bản công khai của tổ chức · quyền của bác sĩ [CẦN XÁC NHẬN TẠI ĐƠN VỊ]); chỉ có abstract →
khai `appraisalCompleteness:'partial'` — cổng CHẶN khỏi `apply`, tối đa `consider`.

**Tuyên bố độ phủ (LÔ I):** mỗi gói phát hành dán khối từ `python3 tools/tuyen_bo_do_phu.py`.


## BƯỚC 0 — ĐỊNH TUYẾN KHI BÁC SĨ NÊU VẤN ĐỀ (15/08/2026)
Trước khi dựng gì mới, đi theo thứ tự rẻ→đắt: (1) `tools/tra_diem_kham.py "<câu hỏi>"` —
có thẻ đã duyệt thì trả lời NGAY, kèm cờ 🟠 nếu có bản tổng hợp mới chưa rà; (2) chủ đề có
trong watchlist → `ops/orchestrator.py --topic "<tên>" --online` chạy chuỗi máy; (3) «chưa
giám sát» → đề xuất bác sĩ thêm watchlist (mẫu 4 tầng, tầng edat không lọc) rồi mới dựng
dashboard theo skill này. Không nhánh nào tự duyệt thẻ — CANDIDATE là trần của máy.
