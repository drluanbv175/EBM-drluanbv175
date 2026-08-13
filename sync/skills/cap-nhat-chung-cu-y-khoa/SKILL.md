---
name: cap-nhat-chung-cu-y-khoa
description: "Sử dụng skill này khi bác sĩ yêu cầu cập nhật chứng cứ hoặc khuyến cáo hiện hành cho MỘT vấn đề lâm sàng cụ thể. Mỗi cập nhật phải kèm Web Dashboard độc lập theo mô hình MẶC ĐỊNH \"Evidence Workbench\" (bố cục 3 cột: bộ lọc · bảng điểm chứng cứ · panel thẩm định; có Clinical Quick View và tab Chuẩn & chất lượng) nếu môi trường hỗ trợ tạo file; đây không phải hệ thống giám sát định kỳ hoặc Dashboard Master mặc định."
metadata:
  version: 1.16.0
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

**Web Dashboard lâm sàng độc lập theo vấn đề cụ thể là đầu ra bắt buộc** khi môi trường hỗ trợ tạo file. Web Dashboard này chỉ giúp tra cứu nhanh nội dung vừa tổng hợp, không đồng nghĩa nội dung đã được duyệt vào Master. Chỉ tạo bản ghi quản trị, PATCH, CỔNG A/CỔNG B hoặc đồng bộ Master khi người dùng yêu cầu riêng.

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

### Chế độ mặc định: Cập nhật thực hành có trọng tâm

Dùng khi bác sĩ hỏi một bệnh/vấn đề/thuốc mà không quy định độ dài. Trả lời đủ để ra quyết định ngoại trú, không biến thành chuyên luận dài.

### Chế độ nhanh

Kích hoạt khi người dùng nói “tóm tắt nhanh”, “điểm cần làm”, “tra nhanh”, hoặc cần áp dụng ngay cho ca bệnh. Trả lời theo cấu trúc:

- Việc cần làm hiện nay.
- Điều cần tránh hoặc chưa nên làm.
- Cờ đỏ/chuyển tuyến.
- Nhóm đặc biệt.
- Nguồn chính mới nhất đã xác minh.

### Chế độ chuyên sâu

Kích hoạt khi người dùng yêu cầu “đầy đủ”, “chuyên sâu”, “đề cương”, “bài giảng”, “theo guideline”, hoặc cần phục vụ đào tạo/nghiên cứu. Bổ sung thẩm định nguồn, bảng điều trị, phân tích khác biệt guideline và thích ứng Việt Nam.

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

Nếu môi trường không tạo file được, phải nói rõ và vẫn cung cấp đầy đủ nội dung EBM trong trả lời.

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
- công cụ thẩm định: AGREE II, AMSTAR 2, RoB 2, ROBINS-I, QUADAS-2, PROBAST hoặc JBI;
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
Cả hai mẫu hỗ trợ field tùy chọn `effectText` (hiệu số phi-tỷ-số), `rob` (RoB 2, chỉ RCT), `frame`/`frameLabels` (khung không-PICO), `etd` (GRADE Evidence-to-Decision) và `standards` (chuẩn cập nhật chứng cứ).

**TỰ ĐỘNG khi gọi skill — BỘ NĂM, MỘT LỆNH:** mỗi lần skill được gọi cho một vấn đề → dựng Dashboard (mẫu Evidence Workbench; Dark Analyst CHỈ khi bác sĩ yêu cầu) rồi chạy **một lệnh duy nhất**:

```bash
python3 tools/xuat_goi_cap_nhat.py <dashboard>.html --online
```

Lệnh này tự làm trọn và sinh **năm** sản phẩm từ CÙNG một khối `DATA` (nên không bản nào tụt lại một phiên bản so với bản khác):
① **Dashboard** — đã qua **HAI** cổng chạy sẵn bên trong: `verify_dashboard.py --online` (liêm chính:
PMID/DOI phân giải thật) và **①-bis `--strict-sources`** (cổng nguồn nghiêm ngặt) ·
② **Bản đọc** `derivatives/<mã>_ban-doc.html` — cờ đỏ và việc cần làm đứng trước ·
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

**KHÔNG tự chạy `EBM_MASTER/tools/sync_all.py`** (đổi mặc định 2026-08-05 theo yêu cầu bác sĩ) — chỉ chạy khi bác sĩ yêu cầu riêng. ⚠️ Bỏ chạy `sync_all.py` là CHƯA ĐỦ để giữ một gói ngoài Antifacts: `tools/build_antifacts.py` quét `EBM-Dashboards/WebDashboard_*.html` bằng glob và hai lịch launchd vẫn dựng lại hub từ chính thư mục đó. Muốn giữ ngoài hub thì phải khai tên file vào `EBM-Dashboards/antifacts-exclude.txt` rồi chạy lại `build_antifacts.py`.

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
| Chẩn đoán (độ chính xác) | **PIRT** | P·Index test·Chuẩn tham chiếu·Bệnh đích | Cross-sectional độ chính xác | QUADAS-2, STARD | **Sn/Sp/LR**, AUC |
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
- Đã tạo Web Dashboard độc lập từ template MẶC ĐỊNH `web-dashboard-evidence-workbench.html` (Evidence Workbench; hoặc `web-dashboard-dark-analyst.html` khi bác sĩ yêu cầu — CÙNG schema `DATA`) với `DATA.standards`/tab `Chuẩn & chất lượng`, và chạy TRỌN dây chuyền tự động (cổng liêm chính → thư viện → phái sinh) chưa?
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
- `EBM_MASTER/tools/sync_all.py` — **KHÔNG còn tự chạy** (đổi 2026-08-05); chỉ khi bác sĩ yêu cầu
- `EBM-Dashboards/tools/reskin_dashboards.py` — áp lại vỏ template chuẩn (EW/DA) cho MỌI dashboard đã xuất bản khi bố cục/CSS template đổi (bóc khối `DATA`, bọc vỏ mới, giữ nguyên dữ liệu, tự backup).

---

## Chốt kiểm đầu ra 2 LỚP — Med-PaLM (BẮT BUỘC, ngay trước khi trả lời)
Skill chạy độc lập (không qua nhạc trưởng) → **tự áp** chốt kiểm 2 lớp như agent `tham-dinh-dau-ra`.
- **Lớp 1 — LIÊM CHÍNH (R1–R7):** nguồn PMID/DOI hoặc nhãn thiếu · KHÔNG PII · không tự "áp dụng cho BN" (dừng Cổng A) · không tự gán GRADE/độ mạnh khi nguồn không cấp · tách độ chắc chứng cứ vs độ mạnh khuyến cáo · nhãn `[CẦN…]` đúng chỗ · disclaimer cuối.
- **Lớp 2 — CHẤT LƯỢNG Med-PaLM (Q1–Q7):** Q1 dễ đọc (đúng đối tượng nhận) · **Q2 đúng đắn** (khớp guideline/đồng thuận — nghi sai → CHUYỂN BÁC SĨ) · Q3 đầy đủ-an toàn (không sót cờ đỏ/CCĐ/tương tác/chỉnh liều/theo dõi) · Q4 không thiên kiến nhóm · **Q5 nguy cơ hại** (hại nặng không cảnh báo → CHUYỂN BÁC SĨ) · Q6 cập nhật · Q7 thẩm quyền nguồn (cảnh giác tạp chí săn mồi). Bản chuẩn: `.claude/agents/_CHUAN-CHAT-LUONG-MEDPALM.md`.
- Còn 🔴 ở lớp nào → **sửa trước khi trả**; **Q2/Q5 đỏ → nêu cờ "cần bác sĩ phán định"**. Tự-kiểm cùng phiên (giảm mù chung, KHÔNG khử thiên lệch) — rào cứng cuối vẫn là bác sĩ.

**"Cần bác sĩ kiểm chứng."**
