# 02/10/2026 — Cửa vào để câu mô tả ca TỰ NHIÊN rơi «unknown» và đẩy ca ngừng tim sang nhánh đề tài (B2, BH151)

**Triệu chứng (tôi tự đo lại, kiểm toàn diện 02/10).** `tools/orchestrator/intent.route()` trên 17 câu: 10 câu bác sĩ mô tả ca tự nhiên rơi
`unknown` («ông 65 tuổi sốt ho 3 ngày khó thở», «bà 70 tuổi rung nhĩ mới phát hiện…», «người 80 tuổi té ngã, uống 9 loại thuốc», «trẻ 3 tuổi sốt
cao co giật», «sản phụ 30 tuần HA 160/100», «cô 25 tuổi khó thở đột ngột», «anh 45t tiểu đường HbA1c 9», «chị 38 tuổi TSH tăng», «suy tim, kali
6,2, đang dùng spironolactone», «kê đơn cho CKD giai đoạn 4 đang dùng metformin»); «bệnh nhân ngừng tim, chạy protocol hồi sức thế nào» ⇒
`research_topic` vì chữ «protocol». `unknown` vẫn chạy BƯỚC 0 nhưng không vào luồng 5 bước; nhánh đề tài không có sàng lọc cờ đỏ tương đương.

**Vá.** Mẫu HẸP: xưng hô + tuổi (ông/bà/anh/chị/cô/chú/bác/cụ/em, có ranh giới từ — «không 5 tuổi» không khớp) — cũng vào nhánh «cá thể thắng cue
đề tài»; trẻ em/người/thai phụ + tuổi/tuần KHÔNG theo sau bởi khoảng («trở lên», «đến», «-») — loại mô tả QUẦN THỂ; «đang dùng/uống/tiêm» + thuốc.
Cue biến cố cấp cứu (ngừng tim, ngưng tim, ngừng thở, hồi sức, co giật, sốc phản vệ, bất tỉnh, hôn mê) vào luật cờ đỏ — cờ đỏ luôn thắng cue
đề tài (route()). Over-route sang nhạc trưởng lâm sàng là chiều an toàn đã ghi trong mã.

**Kiểm.** 25 ca pytest mới (có dấu + không dấu; quần thể và việc lẻ giữ nguyên) + BH151; 206 test orchestrator cũ vẫn đạt. Đột biến: BH151 bắt
6/6 (F5 «mọi mẫu vào nhánh thắng đề tài» lọt lần đầu — thêm ca đề tài quần thể phụ nữ mang thai rồi mới bắt), pytest bắt 6/6.
