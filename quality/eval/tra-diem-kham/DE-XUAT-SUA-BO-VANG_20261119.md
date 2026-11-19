# Đề xuất sửa bộ vàng tra điểm khám — chờ bác sĩ duyệt (19/11/2026)

Kiểm toàn diện hệ chứng cứ ngày 19/11 chạy `pytest tools/` trên máy thật. Bộ vàng `bo-vang.json` (80 câu, bác sĩ duyệt 24/09) đo trên sổ cái thật 3.248 thẻ: **73/80**, trước đây 80/80. Máy đã đo từng câu hỏng và tìm nguyên nhân. **Máy không tự đổi nhãn:** mọi dòng dưới đây chờ bác sĩ quyết, rồi ghi vào `bo-vang.json` với `bac_si_duyet: true`.

| # | Câu | Nhãn hiện tại | Kết quả đo 19/11 | Nguyên nhân | Đề xuất |
|---|---|---|---|---|---|
| 1 | chống đông rung nhĩ DOAC | trung · `rung nhi` | rỗng (khớp yếu) | **Hồi quy THUẬT TOÁN.** Một tiêu đề «CHỈ ĐỊNH KHÁNG ĐÔNG: rung nhĩ…» biến cặp «đông-rung» thành «từ ghép» giả, loại thẻ «Kháng đông đường uống cho rung nhĩ (DOAC ưu tiên)». | **Đã sửa mã** (`_la_tu_ghep`, PR này). Câu trở lại đúng, không đổi nhãn. |
| 2 | viêm khớp dạng thấp JAK inhibitor người cao tuổi nguy cơ tim mạch | trung · `jak` | rỗng | Nội dung kho đổi: thẻ «JAK inhibitor: nguy cơ tim mạch…» từng khớp không còn. Ba thẻ hiện có (vd «Thận trọng JAK inhibitor: tăng MACE, huyết khối…») phủ tiêu đề 46%, dưới ngưỡng 50%. Thuật toán chạy đúng thiết kế, thiên về độ chính xác. | Bác sĩ chọn: (a) giữ nhãn, để nghiên cứu nới luật phủ cho câu dài có ≥2 từ hiếm (rủi ro độ chính xác); hoặc (b) chuyển sang `da_biet_chua_dat` có ghi chú. |
| 3 | sốt xuất huyết dengue ngoại trú dấu hiệu cảnh báo | chưa giám sát («token dengue không có ở BẤT KỲ thẻ nào») | ra thẻ «WHO 2025 — guideline lâm sàng bệnh do arbovirus…» | Kho đã PHỦ chủ đề này. | Bác sĩ xem thẻ; đúng chủ đề thì đổi thành `trung`, `the_phai_chua_mot_trong: ["dengue", "arbovirus", "sot xuat huyet"]`. |
| 4 | thoát vị đĩa đệm | chưa giám sát («0 thẻ») | ra thẻ «Châm cứu cho thần kinh toạ mạn do thoát vị đĩa đệm» | Kho đã có thẻ. | Đúng chủ đề thì đổi thành `trung`, `["thoat vi"]`. |
| 5 | kháng sinh dự phòng | chưa giám sát («0 thẻ chứa cụm này») | ra 3 thẻ (AHA 2021 dự phòng viêm nội tâm mạc; gộp nghiên cứu quan sát; Cochrane 2022) | Kho đã có thẻ. | Đúng chủ đề thì đổi thành `trung`, `["khang sinh du phong"]`. |
| 6 | tăng cân | không trả thẻ lạc đề · cấm `huyet ap`, `mach vanh` | ra 2 thẻ có «TĂNG CÂN» trong tiêu đề, tình cờ có nhắc huyết áp (glucocorticoid liều thấp; thuốc chống trầm cảm và chuyển hoá) | Luật cấm theo từ quá thô: thẻ ĐÚNG chủ đề bị coi là lạc đề. | Đổi thành `trung`, `["tang can"]`. Vẫn bắt được lỗi «cân→cần», vì thẻ lạc đề không chứa «tăng cân». |
| 7 | viêm da | không trả thẻ lạc đề · cấm `da day` | ra «Viêm mạch do thấp: loét da, hoại tử đầu chi và viêm đa dây thần kinh» | **Lỗi chính xác THẬT.** «viêm đa (dây)» gấp dấu thành «viêm da». Người gõ CÓ dấu («viêm») nhưng «da» vốn không dấu, nên máy không phân biệt được «da» với «đa». | Giữ nguyên nhãn (đang bắt đúng lỗi). Hướng sửa thuật toán: câu có từ khác MANG dấu thì token không dấu ngắn coi là gõ đúng nguyên văn. Cần đo trên bộ vàng trước khi áp. |

Sau khi bác sĩ duyệt các dòng 2–6, bộ vàng trên sổ thật dự kiến: 79/80 nếu dòng 2 chọn (b), còn lại đúng 1 lỗi chính xác thật (dòng 7).

Cần bác sĩ kiểm chứng.
