# Thang điểm nguy cơ đã kiểm định

*Đọc file này khi ca đang khám cần một THANG ĐIỂM/CÔNG CỤ NGUY CƠ lâm sàng đã kiểm định — vd rung nhĩ cân nhắc kháng đông (CHA₂DS₂-VASc/HAS-BLED), nguy cơ tim mạch 10 năm (ASCVD/SCORE2), nghi thuyên tắc phổi (Wells/PERC), viêm phổi cộng đồng (CURB-65), loãng xương (FRAX), nghi nhiễm khuẩn nặng/sepsis (qSOFA/NEWS2), bệnh gan mạn (Child-Pugh/MELD). Câu hỏi kích hoạt kiểu: "tính thang điểm gì", "nguy cơ … bao nhiêu phần trăm", "có cần kháng đông/statin không theo nguy cơ", "Wells bao nhiêu điểm", "đánh giá độ nặng viêm phổi". Dùng ở Bước 2 (luật quyết định lâm sàng), Bước 3 (xác suất tiền nghiệm) và Bước 4 (ARR/NNT/NNH, quyết định điều trị) của khung 5 bước EBM.*

## Nguyên tắc bắt buộc khi dùng thang điểm

- **KHÔNG bịa thang/điểm/ngưỡng/hệ số.** Mỗi thang phải nêu **tên đầy đủ + nguồn kiểm định (PMID/DOI hoặc guideline + năm)** và **quần thể đã kiểm định**. Không nhớ chắc công thức → ghi rõ `[CẦN KIỂM CHỨNG]`, không tự dựng điểm hay tự nhẩm hệ số.
- **Kiểm điều kiện áp dụng TRƯỚC khi tính:** một thang chỉ đúng trong quần thể nó được kiểm định; áp dụng ngoài phạm vi đó → cảnh báo rõ, không ép ra một con số.
- Tách rõ ba lớp: **điểm số** (con số thô) vs **diễn giải nguy cơ** (xác suất/nguy cơ tuyệt đối) vs **hành động đề xuất** (chỉ ĐỀ XUẤT — chờ bác sĩ duyệt trước khi áp dụng cho bệnh nhân).
- Không dùng thang ngoài phạm vi kiểm định mà không cảnh báo. Biến đầu vào thiếu → nêu chính xác biến nào còn thiếu, tính kịch bản có/không kèm khoảng, không tự gán giá trị mặc định.
- Kết thúc phần thang điểm bằng: **"Cần bác sĩ kiểm chứng."** KHÔNG PII.

## Quy trình

**Bước an toàn — Cờ đỏ TRƯỚC khi tính điểm:** nhiều thang ở đây định lượng mức độ NẶNG của bệnh cảnh đe dọa tính mạng:
- **qSOFA** — tiên lượng nặng/tử vong ở bệnh nhân ĐÃ nghi nhiễm khuẩn, KHÔNG dùng đơn độc để sàng lọc/loại trừ sepsis do độ nhạy thấp (Surviving Sepsis Campaign 2021 khuyến cáo ngược — PMID 34605781); ưu tiên SIRS/NEWS/MEWS để sàng lọc ban đầu.
- **CURB-65** — độ nặng viêm phổi cộng đồng, không phải công cụ sàng lọc viêm phổi.
- **Wells-PE/PERC** — thuyên tắc phổi, chỉ áp dụng đúng nhóm nguy cơ đã kiểm định (PERC chỉ dùng để LOẠI TRỪ ở nhóm nguy cơ thấp).

Trước khi tính, quét nhanh dấu hiệu đe dọa tính mạng NẰM NGOÀI các biến của chính thang đang tính (vd hạ huyết áp/SpO2 thấp không nằm trong CURB-65; dấu hiệu sốc không nằm trong qSOFA). Có dấu hiệu đó → khuyến nghị xử trí cấp cứu/đến cơ sở y tế gần nhất TRƯỚC, không để việc tính điểm trì hoãn xử trí an toàn.

1. **Xác định câu hỏi nguy cơ** + loại (tiên lượng biến cố · phân tầng độ nặng · quyết định điều trị/dự phòng).
2. **Chọn thang phù hợp + nêu nguồn kiểm định + quần thể đích.** Nếu có vài thang cạnh tranh → nêu lựa chọn và lý do (vd HAS-BLED bổ sung CHA₂DS₂-VASc khi cân nhắc kháng đông).
3. **Kiểm điều kiện áp dụng:** ca này có thuộc quần thể đã kiểm định không? đủ biến đầu vào không? có yếu tố làm thang mất giá trị không?
4. **Tính điểm — dùng công cụ, không tự cộng tay** (xem khối lệnh bên dưới). Biến thiếu → tính kịch bản có/không + nêu khoảng, không gọi công cụ với giá trị bịa.
5. **Diễn giải:** điểm → **nguy cơ tuyệt đối** (theo bảng/nguồn của thang) + độ bất định/hạn chế của thang ở ca này.
6. **Hành động theo ngưỡng (chỉ ĐỀ XUẤT — chờ bác sĩ duyệt):** ngưỡng can thiệp/theo dõi đúng theo guideline nguồn; KHÔNG tự đặt ngưỡng riêng.

## Công cụ tính điểm

```bash
python medical-ebm-automation/tools/risk_score_calc.py cha2ds2vasc --chf 0|1 --hypertension 0|1 \
    --age <tuổi> --diabetes 0|1 --stroke-tia-thromboembolism 0|1 --vascular-disease 0|1 --sex male|female
python medical-ebm-automation/tools/risk_score_calc.py hasbled --hypertension 0|1 --abnormal-renal 0|1 \
    --abnormal-liver 0|1 --stroke 0|1 --bleeding-history 0|1 --labile-inr 0|1 --age <tuổi> --drugs 0|1 --alcohol 0|1
python medical-ebm-automation/tools/risk_score_calc.py curb65 --confusion 0|1 --urea-high 0|1 \
    --rr-high 0|1 --bp-low 0|1 --age <tuổi>
python medical-ebm-automation/tools/risk_score_calc.py qsofa --rr-high 0|1 --altered-mentation 0|1 --sbp-low 0|1
python medical-ebm-automation/tools/risk_score_calc.py wells-pe --dvt-signs 0|1 --pe-most-likely 0|1 \
    --hr-over-100 0|1 --immobilization-surgery 0|1 --previous-dvt-pe 0|1 --hemoptysis 0|1 --malignancy 0|1
python medical-ebm-automation/tools/risk_score_calc.py perc --age-under-50 0|1 --hr-under-100 0|1 \
    --spo2-95-or-above 0|1 --no-hemoptysis 0|1 --no-estrogen 0|1 --no-prior-dvt-pe 0|1 \
    --no-leg-swelling 0|1 --no-recent-surgery-trauma 0|1
python medical-ebm-automation/tools/risk_score_calc.py child-pugh --bilirubin <mg/dL> --albumin <g/dL> \
    --inr <giá trị> --ascites none|mild|moderate_severe --encephalopathy none|grade_1_2|grade_3_4
python medical-ebm-automation/tools/risk_score_calc.py meld --bilirubin <mg/dL> --inr <giá trị> \
    --creatinine <mg/dL> [--dialysis-2x-past-week true]
```

**CHỈ 8 thang trên có công cụ tính điểm THẬT** (điểm-cộng đơn giản/MELD công thức đơn — rủi ro sai công thức thấp). **ASCVD Pooled Cohort Equations · FRAX · SCORE2 · MELD-Na CHƯA có công cụ** (hệ số hồi quy đa biến/độc quyền phức tạp — nhớ nhầm 1 hệ số cho kết quả sai mà không tự phát hiện được) → dùng máy tính CHÍNH THỨC (MDCalc hoặc công cụ của hãng/guideline gốc) hoặc gắn nhãn `[CẦN CÔNG CỤ CHÍNH THỨC]`, KHÔNG tự nhẩm các thang này.

Nếu không có sẵn môi trường chạy công cụ trên (`medical-ebm-automation/tools/risk_score_calc.py`), trình bày công thức/tiêu chí cộng điểm đúng theo nguồn kiểm định của thang và nêu rõ đã dùng nguồn nào — không tự bịa cách cộng.

## Trình bày trong Phiếu khám EBM

Đưa kết quả vào đúng các mục của "Phiếu khám EBM" (mục 2–5 của skill), theo khung sau:

```
• Câu hỏi nguy cơ: ____
• Thang chọn: [tên đầy đủ] — nguồn kiểm định: [PMID/DOI/guideline+năm] — quần thể đích: ____
• Điều kiện áp dụng: [đạt / cảnh báo ngoài phạm vi: ____]
• Biến đầu vào (đủ/thiếu): ____   | Điểm: ____ (nêu khoảng nếu thiếu biến)
• Diễn giải nguy cơ tuyệt đối: ____ % (theo nguồn) — độ bất định/hạn chế: ____
• Hành động theo ngưỡng (ĐỀ XUẤT — chờ bác sĩ duyệt): [ngưỡng + đề xuất, có nguồn]
```

Nguy cơ tiền nghiệm tính được ở đây dùng trực tiếp cho Bước 3 (chẩn đoán phân biệt & xác suất tiền nghiệm); nguy cơ nền tuyệt đối dùng cho Bước 4 (lợi–hại bằng ARR/NNT/NNH). Nếu kết quả dẫn tới cân nhắc kê/chỉnh thuốc (vd kháng đông theo CHA₂DS₂-VASc/HAS-BLED), rà thêm tương tác/chống chỉ định/chỉnh liều trước khi đề xuất — có thể cần thêm skill `ke-don-an-toan-benh-man` nếu ca phức tạp (đa thuốc, bệnh thận/gan kèm theo).

## Ví dụ minh họa (ẩn danh, KHÔNG PII)

> *Đầu vào:* "Nam ~72, rung nhĩ không van, THA, ĐTĐ — có nên kháng đông?" → chọn **CHA₂DS₂-VASc** (nêu nguồn + quần thể) → kiểm điều kiện (rung nhĩ không van: phù hợp) → tính điểm từ tuổi/THA/ĐTĐ bằng công cụ → diễn giải nguy cơ đột quỵ/năm → bổ sung **HAS-BLED** để cân nhắc song song nguy cơ chảy máu → đề xuất theo ngưỡng guideline (chờ bác sĩ duyệt) → tiếp tục ở Bước 4 (lợi–hại ARR/NNT/NNH của kháng đông) và cân nhắc rà đơn nếu tiến tới kê thuốc. *Điểm/ngưỡng CHỈ ghi khi có nguồn; không nhớ chắc → `[CẦN KIỂM CHỨNG]`.*

## Checklist hoàn thành phần thang điểm

- Đã chọn thang đúng, có nguồn kiểm định + quần thể đích.
- Đã kiểm điều kiện áp dụng (quần thể, biến đầu vào, yếu tố làm mất giá trị thang).
- Đã tính điểm bằng công cụ (hoặc nêu rõ biến thiếu + khoảng ước lượng).
- Đã diễn giải thành nguy cơ tuyệt đối kèm độ bất định/hạn chế.
- Đã nêu ngưỡng hành động có nguồn, đóng khung là ĐỀ XUẤT chờ bác sĩ duyệt — không tự "áp dụng cho bệnh nhân".
- Không dùng thang ngoài phạm vi kiểm định mà không cảnh báo.

## Ranh giới nội dung của file này

Phần này chỉ CHỌN – ÁP – DIỄN GIẢI thang/công cụ nguy cơ đã kiểm định thành một con số nguy cơ có nguồn. Nó KHÔNG tự làm thay:
- suy luận Bayes/xác suất hậu nghiệm chi tiết bằng LR (đã có ở Bước 4a của khung 5 bước — dùng nguy cơ tiền nghiệm từ đây làm đầu vào);
- quyết định kê đơn cụ thể, rà tương tác/chống chỉ định/chỉnh liều (dùng skill `ke-don-an-toan-benh-man` khi ca chạm tới kê đơn);
- tự chấm lại mức GRADE của chứng cứ nguồn (giữ nguyên grading gốc, không tự nâng/hạ);
- ra khuyến cáo tầm soát/dự phòng cho cả quần thể (đây là cho MỘT bệnh nhân cụ thể tại phòng khám).

## Disclaimer

Kết thúc mọi phần dùng thang điểm nguy cơ bằng: **"Cần bác sĩ kiểm chứng."**
