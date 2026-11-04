# 04/11/2026 — Nhãn mức từng miền nguy cơ sai lệch ngoài thang của công cụ (tóm tắt chứng cứ ⑨)

**Bối cảnh:** bác sĩ chọn «chấm bù theo lô» cho 157 bản tóm tắt làm trước luật 26/10/2026 (kiểm chéo phải chấm cả phán quyết từng
miền + kết cục chính). Lô 1 (20 bản) + nhóm đầu lô 2: người chấm độc lập bắt 4 mục `sai`, đều là MỨC KHÔNG CÓ TRONG THANG:
QUADAS «trung bình», ROBINS-E «không đánh giá được» ở cấp miền, kết quả công cụ Cochrane của chính bài xếp làm «miền 17» AMSTAR-2
(«cao/không rõ»), AMSTAR-2 mức kép «Có (vận động) · Không (tâm lý–xã hội)». Số liệu của cả 4 mục đều đúng.

**Đo toàn kho (282 bản):** 15 mục ngoài thang ở 14 bản (PROBAST «có lo ngại» ×5, «không đánh giá được», «không xác định được từ
bản đã đọc», «cao hơn cho…», «thiếu thông tin nhỏ…», «dự kiến thấp đến trung bình», các «miền» «Ngoài AMSTAR-2») + mức kép
AMSTAR-2; 188 nhãn đồng nghĩa viết lẫn lộn (AMSTAR-2 «đạt / đạt một phần / không đạt» bên cạnh «có / có một phần / không»;
ROBINS-I «vừa», «không rõ»; RoB 2 «nguy cơ thấp», «có một số lo ngại»).

**Vá:** `THANG_MUC` + `DONG_NGHIA_MUC` trong `tom_tat_chung_cu_word.py`; cổng `_muc_sai_thang` (mỗi đoạn phải mở đầu bằng một
mức của thang; RoB 2/ROBINS/QUADAS/PROBAST cho ghi theo kết cục kèm «với/cho/ở/theo/khi/nếu …» hoặc chú thích ngoặc; tiền tố
«dự kiến» cho bài đề cương; AMSTAR-2 một mức); bước dựng in nhãn chuẩn (`muc_chuan`, giữ chữ hoa đầu). Hướng dẫn đọc (mục 3)
dạy thang mức cùng lúc. Công cụ ngoài bảng (AGREE II, JBI, SANRA) không kiểm thang.

**Kiểm:** `tools/test_tom_tat_thang_muc_20261104.py` 33 ca; 7 đột biến đều đỏ; bộ test tóm tắt xanh.

**Sau khi gộp:** các bản ngoài thang bị cổng chặn tới khi sửa — sửa theo đề xuất người chấm độc lập + kiểm chéo lần 2 (bác sĩ
đồng ý 04/11/2026).
