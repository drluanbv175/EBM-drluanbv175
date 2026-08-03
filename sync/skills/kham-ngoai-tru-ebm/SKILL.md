---
name: kham-ngoai-tru-ebm
description: "Sử dụng skill này khi bác sĩ cần tiếp cận hoặc ra quyết định cho MỘT ca khám ngoại trú theo Y học chứng cứ (EBM). Dẫn dắt trọn 5 bước tại phòng khám: đặt câu hỏi lâm sàng (PICO) · hỏi–khám có trọng điểm + sàng lọc cờ đỏ · chẩn đoán phân biệt và xác suất tiền nghiệm · áp chứng cứ vào quyết định (xét nghiệm theo LR, điều trị theo ARR/NNT/NNH, ngưỡng test–treat) · quyết định cùng bệnh nhân (shared decision-making) + safety-netting + ghi chép SOAP. Kích hoạt với \"tôi có một bệnh nhân…\", \"khám ca này\", \"chẩn đoán phân biệt\", \"nên làm xét nghiệm gì / điều trị thế nào\", hoặc khi muốn rèn ra quyết định EBM tại giường. Đây KHÔNG phải skill viết tổng quan y văn/bản thảo, KHÔNG phải Dashboard Master, KHÔNG phải hệ giám sát guideline định kỳ."
metadata:
  version: 1.1.0
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

## 4. Quy trình bắt buộc cho mỗi ca (BƯỚC 0 an toàn + 5 bước EBM: Ask – Acquire – Appraise – Apply – Assess)

Thu thập bối cảnh ẩn danh tối thiểu trước: tuổi, giới, vấn đề chính, bệnh nền, thuốc đang dùng, dị ứng, chức năng gan–thận nếu liên quan. **Không** hỏi thông tin định danh. Chỉ hỏi lại khi thiếu dữ kiện có thể đổi xử trí hoặc gây mất an toàn.

### BƯỚC 0 — AN TOÀN/CỜ ĐỎ TRƯỚC TIÊN (bắt buộc, chạy TRƯỚC Bước 1 ASK)
Skill này **chạy độc lập, không qua nhạc trưởng `dieu-phoi-lam-sang`** — vì vậy PHẢI tự làm bước mà `dieu-phoi-lam-sang` lẽ ra làm hộ (BƯỚC 0 — CỜ ĐỎ TRƯỚC TIÊN) và tự đối chiếu bảng câu hỏi an toàn bắt buộc mà `sang-loc-co-do`/`ke-don-an-toan` dùng, **trước khi** đặt PICO hay bàn xét nghiệm/điều trị:
1. Quét nhanh dấu hiệu đe dọa tính mạng/cần chuyển cấp cứu ngay cho vấn đề đang xét — không để việc đặt câu hỏi PICO/chẩn đoán phân biệt trì hoãn xử trí an toàn.
2. **Đối chiếu bắt buộc với `.claude/agents/_CAU-HOI-AN-TOAN-BAT-BUOC.md`** — bảng câu hỏi an toàn theo bối cảnh (nguồn dùng chung với `sang-loc-co-do`/`ke-don-an-toan`/`tham-dinh-dau-ra`). Hai dòng kích hoạt hiện có, PHẢI hỏi & ghi nhận nếu khớp bệnh cảnh:
   - **S1** — mất ngủ + cảm giác thất bại/vô vọng + yêu cầu thuốc ngủ mạnh (benzodiazepine/Z-drug liều cao) → **HỎI Ý TƯỞNG TỰ SÁT** (PHQ-9 mục 9/C-SSRS rút gọn) trước khi bàn phương án thuốc ngủ.
   - **S2** — cân nhắc kê thuốc gây quái thai/độc thai (ACEi/ARB, valproate, isotretinoin, warfarin, methotrexate…) cho phụ nữ tuổi sinh đẻ/không loại trừ mang thai → **HỎI khả năng có thai + biện pháp tránh thai** trước khi kê.
   - Nếu bệnh cảnh khớp S1/S2 mà chưa hỏi được → **KHÔNG** tiến tới Bước 4 (quyết định điều trị) cho nhóm thuốc liên quan; nêu rõ `[CẦN HỎI THÊM — an toàn]` và dừng ở đó cho đến khi có câu trả lời.
3. Nếu ca có dấu hiệu vượt quá phạm vi khám ngoại trú EBM tại giường (cấp cứu thật) → dừng ngay, khuyến nghị "đến cơ sở y tế gần nhất", không tiếp tục 5 bước.

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

## 7. Tài liệu tham khảo chuyên sâu (đọc khi ca chạm đúng chủ đề)

19 file trong `references/` — mỗi file là hướng dẫn tự chứa cho MỘT mảng chuyên môn, chỉ đọc file khớp với ca đang xét (progressive disclosure — không đọc hết 19 file cho mọi ca). Mỗi file tự nêu rõ ở đầu bài "khi nào đọc file này".

| # | File | Đọc khi nào |
|---|---|---|
| 1 | `references/01_sang_loc_co_do_va_nguong_chuyen_tuyen.md` | Bước 0 mọi ca — cờ đỏ theo hội chứng, luật tam chứng bắt buộc, ngưỡng chuyển cấp cứu |
| 2 | `references/02_khai_thac_benh_su_kham_co_trong_diem.md` | Bước 2 — khung SOCRATES/OPQRST, tiền sử + khám trọng điểm theo hội chứng |
| 3 | `references/03_pico_lam_sang.md` | Bước 1 — chuẩn hóa câu hỏi PICO, phân loại nền/tiền cảnh, kết cục quan trọng với BN |
| 4 | `references/04_tra_cuu_chung_cu_tai_diem_kham.md` | Bước 4c — thứ tự nguồn tra cứu (guideline hiệp hội → NEJM/Lancet/JAMA/BMJ → PubMed), quy trình corrective self-RAG |
| 5 | `references/05_dien_giai_can_lam_sang.md` | Có kết quả xét nghiệm/hình ảnh cần đọc — bảng giá trị nguy kịch đồng thuận, quy trình 6 bước diễn giải |
| 6 | `references/06_chan_doan_xac_suat_bayes.md` | Bước 3 — tính xác suất hậu nghiệm bằng LR, ngưỡng test–treat, công cụ CLI `clinical_calc.py` |
| 7 | `references/07_thang_diem_nguy_co.md` | Cần một thang điểm nguy cơ đã kiểm định (CHA₂DS₂-VASc, HAS-BLED, CURB-65, Wells-PE, PERC, Child-Pugh, MELD, qSOFA...) |
| 8 | `references/08_tham_dinh_grade_nnt.md` | Cần thẩm định nhanh 1 bài/guideline — chấm GRADE, tính NNT/NNH, chọn công cụ nguy cơ sai lệch đúng thiết kế |
| 9 | `references/09_huong_dan_lam_sang_apply.md` | Bước 4 — đặt phát hiện vào bối cảnh guideline hiện hành, dựng khối GRADE Evidence-to-Decision |
| 10 | `references/10_ke_don_an_toan.md` | Ca chạm tới kê/rà đơn thuốc — tương tác, chống chỉ định, hiệu chỉnh liều theo thận/gan, đa thuốc người cao tuổi |
| 11 | `references/11_quyet_dinh_chung_sdm.md` | Bước 5 — cá thể hóa khuyến cáo, trình bày lợi–hại cho bệnh nhân hiểu, shared decision-making |
| 12 | `references/12_loi_dan_tuan_thu.md` | Cần soạn lời dặn A5 hoặc kế hoạch tuân thủ điều trị |
| 13 | `references/13_theo_doi_benh_man.md` | Ca bệnh mạn cần kế hoạch theo dõi dài hạn/treat-to-target (ĐTĐ, THA, COPD-hen...) |
| 14 | `references/14_du_phong_tam_soat.md` | Câu hỏi về tầm soát/dự phòng theo tuổi-giới-nguy cơ (không phải xử trí bệnh đang có) |
| 15 | `references/15_dau_man_tinh.md` | Đau mạn tính >3 tháng (không do ung thư tiến triển cấp) — phân loại cơ chế đau, opioid stewardship |
| 16 | `references/16_cham_soc_giam_nhe.md` | Bệnh nặng/giai đoạn cuối — kiểm soát triệu chứng, thảo luận mục tiêu chăm sóc |
| 17 | `references/17_tram_cam_lo_au.md` | Nghi trầm cảm/lo âu — sàng lọc PHQ-9/GAD-7, chăm sóc theo bậc (stepped care) |
| 18 | `references/18_quan_ly_khang_dong.md` | Rung nhĩ/VTE/van cơ học cần kháng đông — chọn thuốc, chỉnh liều DOAC, bắc cầu quanh thủ thuật |
| 19 | `references/19_tham_dinh_do_chinh_xac_chan_doan.md` | Câu hỏi về ĐỘ TIN CẬY của một xét nghiệm/test chẩn đoán (QUADAS-2, Se/Sp/LR có vững không) |

## 8. Nối tiếp sang skill khác (gợi ý, hỏi bác sĩ trước)

- **Tuân thủ điều trị** (rào cản + lời dặn A5 cho BN) → `tuan-thu-dieu-tri`.
- **Người cao tuổi đa thuốc** (Beers/STOPP-START, deprescribing) → `nguoi-cao-tuoi-da-benh-da-thuoc`.
- **Kế hoạch điều trị chính thức** (3–4 trang) → `treatment-plans`.
- **Lời dặn bệnh nhân A5** in tại phòng khám → công cụ `Loi-dan-benh-nhan/loi-dan-benh-nhan.html`.
- **Bản ghi chuẩn (SOAP/H&P)** → `clinical-reports`.
- **Cập nhật khuyến cáo cả chủ đề + dashboard** → `cap-nhat-chung-cu-y-khoa` / `dark-analyst`.

## 9. Checklist trước khi trả lời

- **BƯỚC 0 đã chạy TRƯỚC PICO chưa?** Đã đối chiếu `_CAU-HOI-AN-TOAN-BAT-BUOC.md` (S1 tự sát khi mất ngủ+vô vọng+đòi thuốc ngủ mạnh · S2 thai kỳ trước thuốc gây quái thai) chưa — nếu khớp bệnh cảnh mà chưa hỏi được, đã dừng trước Bước 4 chưa?
- Đã đặt PICO và nhận diện đúng loại câu hỏi + khung chưa?
- Đã sàng lọc cờ đỏ và liệt kê must-not-miss chưa?
- Đã ước lượng xác suất tiền nghiệm và nêu ngưỡng test/điều trị khi liên quan chưa?
- Test đề nghị có thật sự dịch chuyển quyết định không (LR → hậu nghiệm)?
- Lợi–hại điều trị đã nêu theo số tuyệt đối (ARR/NNT/NNH), giữ nguyên grading của nguồn chưa?
- Đã cá thể hóa cho nhóm đặc biệt và bối cảnh VN, đánh dấu `[CẦN XÁC NHẬN TẠI ĐƠN VỊ]` khi cần chưa?
- Đã nêu safety-netting ("đến cơ sở y tế gần nhất", không "gọi 115") + hẹn tái khám chưa?
- Mọi số liệu/nguồn đều trích đúng, không bịa; ghi nguồn dạng văn bản thường chưa?
- Không có PII; có disclaimer "Cần bác sĩ kiểm chứng" chưa?

## 9b. Chốt kiểm đầu ra 2 LỚP (BẮT BUỘC, ngay trước khi trả lời)
Skill này chạy độc lập (không qua nhạc trưởng) → **tự áp** chốt kiểm 2 lớp như agent `tham-dinh-dau-ra`. Bản chuẩn: `.claude/agents/_CHUAN-CHAT-LUONG-MEDPALM.md` + `_KIEM-DUYET-DOC-LAP.md`.
- **Lớp 1 — LIÊM CHÍNH (R1–R7):** R1 nguồn (PMID/DOI hoặc nhãn thiếu) · R2 KHÔNG PII · R3 không tự "áp dụng cho BN" (dừng Cổng A) · R4 không tự gán GRADE/độ mạnh khi nguồn không cấp · R5 tách độ chắc chứng cứ vs độ mạnh khuyến cáo · R6 nhãn `[CẦN…]` đúng chỗ · R7 disclaimer cuối.
- **Lớp 2 — CHẤT LƯỢNG Med-PaLM (Q1–Q7):** Q1 dễ đọc (đúng đối tượng nhận) · **Q2 đúng đắn** (khớp guideline/đồng thuận — nghi sai → CHUYỂN BÁC SĨ, không tự khẳng định) · **Q3 đầy đủ — cụ thể: đã hỏi S1 (ý tưởng tự sát, nếu mất ngủ+vô vọng+đòi thuốc ngủ mạnh) và S2 (khả năng có thai, nếu cân nhắc thuốc gây quái thai) theo `_CAU-HOI-AN-TOAN-BAT-BUOC.md` chưa, không chỉ "không sót cờ đỏ" chung chung** — cùng với CCĐ/tương tác/chỉnh liều/theo dõi · Q4 không thiên kiến nhóm · **Q5 nguy cơ hại** (hại nặng không cảnh báo → CHUYỂN BÁC SĨ) · Q6 cập nhật · Q7 thẩm quyền nguồn (cảnh giác tạp chí săn mồi).
- **Còn 🔴 ở lớp nào → SỬA trước khi trả; Q2/Q5 đỏ → nêu cờ "cần bác sĩ phán định".** Đây là tự-kiểm cùng phiên (giảm mù chung, KHÔNG khử thiên lệch) — rào cứng cuối vẫn là bác sĩ.

## 10. Tài nguyên & liêm chính

- Tìm chứng cứ: `clinical-evidence-rag`, `research-lookup`, `paper-lookup` (chỉ nguồn miễn phí: PubMed E-utilities, CSDL mở; KHÔNG dịch vụ trả phí).
- Công cụ lời dặn A5: `Loi-dan-benh-nhan/loi-dan-benh-nhan.html`.
- Nguyên tắc xuyên suốt: ưu tiên số tuyệt đối hơn tương đối · giữ nguyên grading của nguồn · tách "khuyến cáo nguồn / độ chắc chắn / đánh giá vận hành" · không PII · không bịa · mọi đầu ra kết thúc bằng disclaimer.
