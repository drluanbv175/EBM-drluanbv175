---
name: dark-analyst
description: Sử dụng skill này khi bác sĩ yêu cầu cập nhật chứng cứ hoặc khuyến cáo hiện hành cho MỘT vấn đề lâm sàng cụ thể. Mỗi cập nhật phải kèm Web Dashboard độc lập theo mô hình MẶC ĐỊNH "Evidence Workbench" (bố cục 3 cột: bộ lọc · bảng điểm chứng cứ · panel thẩm định; lớp Clinical Quick View là màn hình tóm tắt mặc định) nếu môi trường hỗ trợ tạo file; đây không phải hệ thống giám sát định kỳ hoặc Dashboard Master mặc định.
metadata:
  version: 1.12.0
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
2. Ưu tiên nguồn gốc chính thức và bằng chứng chất lượng cao.
3. Tách rõ: khuyến cáo của nguồn, độ chắc chắn chứng cứ, đánh giá vận hành của người tổng hợp.
4. Cá thể hóa cho ngoại trú Việt Nam, đặc biệt người cao tuổi, đa bệnh lý, đa thuốc, CKD, bệnh gan, bệnh tim mạch và đái tháo đường.
5. Nêu rõ điều cần làm, điều không nên làm, theo dõi và khi nào chuyển tuyến/cấp cứu.
6. Không bịa nguồn, số liệu, liều, cut-off, phân hạng, DOI hoặc tài liệu tham khảo.
7. Khi câu hỏi là về hiệu quả/an toàn của một can thiệp, cấu trúc hóa chứng cứ theo PICO và nêu hiệu số (point estimate) đúng như nguồn báo cáo (xem mục 5B và `references/06-pico-va-trich-dan.md`).
8. Ghi nguồn sạch trong văn bản (tác giả/tổ chức + năm + tạp chí) và liệt kê tham khảo theo Vancouver/NLM; KHÔNG chèn thẻ markup trích dẫn thô hay ký tự kỹ thuật vào câu trả lời (xem mục 5B).

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

Đọc `references/01-nguon-va-xac-minh.md`.

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
- **Cột giữa — Băng `CLINICAL QUICK VIEW` cố định + bảng điểm chứng cứ + các tab nội dung:** mỗi dòng là một `ITEM-xx`; click để mở thẩm định ở cột phải. Hiệu số (HR/RR/OR…) hiển thị kèm forest plot mini đúng như nguồn báo cáo.
- **Cột phải — Panel `EVIDENCE DETAIL VIEW`:** chi tiết item đang chọn.

Ba lớp nội dung bắt buộc ánh xạ vào bố cục:

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

Không hiển thị `Governance/Admin`, `CỔNG A/CỔNG B`, `ACTION_TRACKER` hoặc nhập Master trong Web Dashboard của vấn đề riêng lẻ, trừ khi bác sĩ yêu cầu tích hợp Dashboard Master.

### Tương tác bắt buộc

- Ô tìm kiếm theo bệnh/tình huống, thuốc, nhóm nguy cơ, hành động hoặc nguồn.
- Bộ lọc theo quyết định và nhóm đặc biệt khi có nhiều item.
- Nút `Mở chi tiết`.
- Nút xuất CSV hoặc JSON các item đang lọc nếu khả thi.
- Tab `Kiểm chứng thao tác` với 4 nhiệm vụ:
  1. Tìm hành động ưu tiên của vấn đề ≤30 giây.
  2. Tìm cờ đỏ/chuyển tuyến hoặc kết luận không có cập nhật liên quan ≤30 giây.
  3. Tìm nội dung cho nhóm đặc biệt liên quan ≤30 giây.
  4. Mở nguồn và ngày/phiên bản ≤60 giây.

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

**Sử dụng template MẶC ĐỊNH:** `templates/web-dashboard-evidence-workbench.html` (mẫu **"Evidence Workbench"** — nền sáng, 3 cột; có khối **GRADE Evidence-to-Decision**; mặc định từ 2026-06-07 theo lựa chọn của bác sĩ).
Chỉ cần thay khối hằng số `DATA = {…}` ở cuối file; KHÔNG sửa HTML/CSS. Chrome (tiêu đề, PICO chips, KPI, băng Clinical Quick View, EtD) **tự sinh từ `DATA`**.
**Mẫu KHI BÁC SĨ YÊU CẦU (nền tối, dày dữ liệu):** `templates/web-dashboard-dark-analyst.html` — **CÙNG schema `DATA`** (một khối dữ liệu chạy được cả hai). Template một-cột cũ `web-dashboard-van-de-cu-the-clinical-quick-view.html` chỉ dùng khi yêu cầu riêng.
Cả hai mẫu hỗ trợ field tùy chọn `effectText` (hiệu số phi-tỷ-số), `rob` (RoB 2, chỉ RCT), `frame`/`frameLabels` (khung không-PICO) và `etd` (GRADE Evidence-to-Decision).

**TỰ ĐỘNG khi gọi skill:** mỗi lần skill được gọi cho một vấn đề → tự chạy TRỌN dây chuyền (không cần yêu cầu từng bước): dựng Dashboard (EW mặc định) → `tools/verify_dashboard.py --online` (PASS) → `tools/drug_safety_scan.py` (nếu có thuốc + cao tuổi/đa thuốc) → `tools/build_library.py add` → `tools/make_derivatives.py` (3 phái sinh) → **`python3 EBM_MASTER/tools/sync_all.py`** (nạp vào sổ cái trung tâm EBM_MASTER, sinh lại WebApp duy nhất). Dùng mẫu Dark Analyst CHỈ khi bác sĩ yêu cầu.
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
`python3 tools/verify_dashboard.py <dashboard>.html --online`
Kiểm: mỗi item có PMID/DOI · `gradeLevel` & `decision` hợp lệ · có disclaimer · quét PII · và **tự xác minh mỗi PMID phân giải đúng trên PubMed** (chống trích dẫn ảo). FAIL → sửa trước khi giao.

**(b) Thư viện cập nhật — `tools/build_library.py`** (tích lũy thành tài sản tra cứu):
`python3 tools/build_library.py add <dashboard>.html` → cập nhật `library.json` + sinh `evidence-library.html` (chỉ mục mọi bản cập nhật, có tìm/lọc, mở thẳng từng dashboard).

**(c) Sản phẩm phái sinh — TỰ ĐỘNG mỗi lần chạy:** sau khi cổng liêm chính PASS, tự sinh 3 sản phẩm vào `EBM-Dashboards/derivatives/` (`tools/make_derivatives.py <dashboard>.html`): **tờ dặn người bệnh** (ngôn ngữ phổ thông, BỎ liều) · **dàn ý slide** (giữ hiệu số + GRADE + PMID) · **kịch bản TikTok**. Slide = faithful; tờ dặn & TikTok do model rà ngôn ngữ phổ thông trước khi giao. **Video TikTok thật: theo yêu cầu qua skill `tao-video-tiktok`.** Playbook: `references/08-xuat-san-pham-phai-sinh.md`. Người bệnh & TikTok **KHÔNG nêu liều**; kèm disclaimer; không PII; bác sĩ duyệt trước khi phát/đăng.

**GRADE Evidence-to-Decision (EtD):** Dashboard Dark Analyst tự hiển thị khối EtD khi `DATA` có field `etd` (vấn đề · lợi ích · tác hại · độ chắc chắn · giá trị · cân bằng · nguồn lực · công bằng · chấp nhận · khả thi → khuyến cáo + độ mạnh). **Hàng lợi ích/tác hại/độ chắc chắn lấy TỪ chứng cứ; các hàng còn lại + khuyến cáo = "đánh giá vận hành"** (ghi rõ trên dashboard). Điền `etd` cho mỗi cập nhật có khuyến cáo đổi thực hành.

**(d) Thư mục chung tích lũy:** xuất MỌI dashboard vào `EBM-Dashboards/` (trong OneDrive → tự đồng bộ Mac↔Windows). Sau khi PASS cổng (a), chạy `EBM-Dashboards/tools/build_library.py add <file>.html` để tích lũy vào chỉ mục `EBM-Dashboards/evidence-library.html`. Hướng dẫn: `EBM-Dashboards/README.md`.


## 5E. Lớp phủ an toàn thuốc · Giám sát định kỳ · Bản địa hóa BYT

**(a) An toàn thuốc (người cao tuổi/đa thuốc):** khi cập nhật có thuốc và liên quan nhóm `cao-tuoi`/`da-thuoc`, chạy `tools/drug_safety_scan.py <dashboard>.html` (đối chiếu bảng cờ **Beers 2023/STOPP-START v3** trong `data/drug_flags.json`) → cảnh báo + sinh prompt rà soát ĐẦY ĐỦ bằng skill `nguoi-cao-tuoi-da-benh-da-thuoc`. Bảng cờ KHÔNG đầy đủ, chỉ để nhắc. Chi tiết: `references/09-an-toan-thuoc-overlay.md`.

**(b) Giám sát định kỳ (Track B):** `tools/surveillance_scan.py` quét PubMed tìm guideline/SR/meta/RCT MỚI theo `EBM-Dashboards/watchlist.json` (10–20 chủ đề lõi) → báo cáo ỨNG VIÊN để thẩm định (KHÔNG tự đổi thực hành). Track A (theo yêu cầu) vẫn là trục chính. Tự động hóa qua skill `schedule` chỉ khi bác sĩ xác nhận nhịp. Chi tiết: `references/10-giam-sat-dinh-ky.md`.

**(c) Bản địa hóa Bộ Y tế VN:** ở bước "Áp dụng tại VN", tra `EBM-Dashboards/vn-guidelines/registry.json` (bác sĩ điền từ tài liệu CHÍNH THỨC — **KHÔNG bịa số QĐ**) + RAG (`clinical-evidence-rag`) để đối chiếu quốc tế ↔ BYT (phác đồ, danh mục BHYT, phân tuyến). Chi tiết: `references/11-guideline-bo-y-te-vn.md`.


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
- Đã ghi đúng tiêu đề, tổ chức, ngày/phiên bản và quần thể của nguồn chưa?
- Đã giữ nguyên grading của nguồn, không tự gán GRADE chưa?
- Đã tách “điểm mới” khỏi “kiến thức nền hiện hành” chưa?
- Đã nêu hành động, monitoring, cờ đỏ/chuyển tuyến khi cần chưa?
- Đã phân tích nhóm đặc biệt liên quan chưa?
- Đã ghi rõ nội dung chưa đủ để thay đổi chưa?
- Đã tạo Web Dashboard độc lập từ template MẶC ĐỊNH `web-dashboard-evidence-workbench.html` (Evidence Workbench; hoặc `web-dashboard-dark-analyst.html` khi bác sĩ yêu cầu — CÙNG schema `DATA`) và chạy TRỌN dây chuyền tự động (cổng liêm chính → thư viện → phái sinh) chưa?
- Đã tránh tạo ID quản trị hoặc cập nhật Dashboard Master khi người dùng không yêu cầu chưa?
- Đã dùng tài liệu tham khảo có thể truy nguyên chưa?
- Nếu câu hỏi về hiệu quả can thiệp: đã trình bày khối PICO đủ 5 dòng và trích hiệu số đúng như nguồn (point estimate + CI/p) chưa?
- Đã tự nhận diện loại câu hỏi và chọn đúng khung (PICO/PECO/chẩn đoán/tiên lượng/tần suất/định tính/dịch vụ) và nêu rõ khung đã dùng chưa? (xem 5C)
- Đã chạy `tools/verify_dashboard.py --online` và PASS (mọi item có PMID/DOI, PMID phân giải đúng, có disclaimer, không PII) trước khi giao chưa? (xem 5D)
- Nếu cập nhật có thuốc cho người cao tuổi/đa thuốc: đã chạy `tools/drug_safety_scan.py` + đối chiếu Beers/STOPP qua skill người cao tuổi chưa? (xem 5E)
- Đã tự sinh 3 sản phẩm phái sinh (tờ dặn/slide/TikTok) vào `derivatives/` và (khi có khuyến cáo đổi thực hành) điền khối `etd` cho Dashboard chưa? (xem 5D)
- Đã nêu cả hai chiều khi chứng cứ không đồng nhất, và đánh dấu `[CẦN BỔ SUNG]` khi chỉ có đồng thuận/nguyên lý chưa?
- Đã ghi nguồn dạng văn bản thường (tác giả/tổ chức + năm + tạp chí) và rà soát để KHÔNG còn thẻ markup trích dẫn/mã kỹ thuật thô lẫn trong câu trả lời chưa?

## 9. Tài nguyên kèm theo

- `references/01-nguon-va-xac-minh.md`
- `references/02-cong-cu-tham-dinh-va-grade.md`
- `references/03-thich-ung-viet-nam.md`
- `references/04-thuoc-khang-sinh-va-cong-cu.md`
- `templates/mau-cap-nhat-nhanh.md`
- `templates/mau-cap-nhat-chuyen-sau.md`
- `templates/web-dashboard-evidence-workbench.html` ⭐ TEMPLATE MẶC ĐỊNH (Evidence Workbench, nền sáng; có EtD; chrome tự sinh từ DATA)
- `templates/web-dashboard-dark-analyst.html` (mẫu KHI YÊU CẦU — nền tối, CÙNG schema DATA)
- `templates/web-dashboard-van-de-cu-the-clinical-quick-view.html` (một-cột cũ, chỉ khi yêu cầu riêng)
- `templates/web-dashboard-record-schema.csv`
- `references/05-web-dashboard-clinical-quick-view.md`
- `references/06-pico-va-trich-dan.md`
- `references/07-mo-hinh-cau-hoi-va-khung-thay-the.md`
- `references/08-xuat-san-pham-phai-sinh.md`
- `templates/phai-sinh-to-dan-nguoi-benh.md`
- `templates/phai-sinh-kich-ban-tiktok.md`
- `tools/verify_dashboard.py` (cổng kiểm liêm chính + xác minh PMID/DOI)
- `tools/build_library.py` (thư viện chỉ mục cập nhật → evidence-library.html)
- `tools/make_derivatives.py` (tự sinh tờ dặn người bệnh / dàn ý slide / kịch bản TikTok → derivatives/)
- `references/09-an-toan-thuoc-overlay.md` · `tools/drug_safety_scan.py` · `data/drug_flags.json` (lớp phủ Beers/STOPP)
- `references/10-giam-sat-dinh-ky.md` · `tools/surveillance_scan.py` (giám sát PubMed theo watchlist)
- `references/11-guideline-bo-y-te-vn.md` (bản địa hóa Bộ Y tế VN)
- `quality/acceptance-checklist.md`
- `quality/web-dashboard-acceptance-checklist.md`
