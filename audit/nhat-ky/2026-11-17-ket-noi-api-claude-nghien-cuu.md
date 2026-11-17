# 17/11/2026 — Kết nối Claude API cho hệ nghiên cứu G0–G10: ba công cụ tư vấn

## Bối cảnh
Bác sĩ hỏi «Kết nối API Claude» và chọn ba việc (kèm «đề xuất tốt nhất»): kiểm nội dung trích dẫn A12, phản biện máy
đề cương nộp, hội đồng cổng qua Batch API. Trước đó cổng G0–G10 không gọi API nào: mọi việc đọc–chấm chạy bằng agent
trong phiên Claude Code, nên chỉ làm được khi có người mở phiên và tốn token phiên (hội đồng BTM G0–G4 bằng workflow:
16–30 triệu token theo `hoi_dong_cong.py uoc-tinh`).

## Đã làm (repo y khoa)
- `tools/api_claude_nc.py`: luật chung — khoá env → kho bí mật (dòng cuối thắng), chạy khô mặc định, dưới pytest không
  đọc kho thật / không dựng khách thật / không ghi nhật ký thật, kiểm `stop_reason` trước khi đọc, JSON hỏng thì không
  đoán, nhật ký sức khoẻ `~/.ebm-api-claude.json` có thêm khoá `nguon`. Lỗi phía máy (`LoiCucBo`) và câu trả lời hỏng
  (`KetQuaHong`) KHÔNG ghi thành «API chết».
- `tools/kiem_noi_dung_trich_dan.py`: mỗi nhóm dấu [n] một đơn vị kiểm với đúng đoạn đứng trước nó (để số của [5]
  không bị so với abstract của [6]); `PubMedClient.fetch_abstracts`. Máy kiểm lại model: «trích» phải có nguyên văn
  trong abstract, số % / thập phân phải có trong abstract.
- `tools/phan_bien_may_de_cuong.py`: phần tất định (trích dẫn ngoài danh mục, tài liệu không được trích, thứ tự
  Vancouver) + một lượt đọc toàn văn; chỉ trình phát hiện có trích nguyên văn (cả chỗ đối chiếu); lệch số dòng thì máy
  đặt lại đúng dòng.
- `tools/hoi_dong_cong_batch.py`: máy trạng thái chấm → đề xuất → phản biện → trọng tài, mỗi bước một batch; system
  prompt là chính tệp agent; ghi qua `hoi_dong_cong.ghi_bien_ban` (thêm chế độ `batch_api`, khoá `nguon_may`); tài
  liệu đổi sau khi khởi tạo thì không ghi.

## Đo trên đề tài thật (chỉ đọc, chạy khô)
- Kiểm trích dẫn: BTM 28 đoạn / 5 lượt ≈ 0,08 USD; C1a 83 đoạn / 14 lượt ≈ 0,19 USD; C1a có 18 tài liệu không PMID
  (máy không kiểm — vẫn đọc tay).
- Phản biện máy: phần tất định sạch trên cả hai; một lượt ≈ 0,13 (BTM) và 0,17 USD (C1a).
- Hội đồng Batch BTM: G0 ≈ 0,73 · G3 ≈ 0,59 · G4 ≈ 0,30 USD (Sonnet 5.5, giá Batch).

## Giới hạn nói thẳng
- Chưa gọi API thật lần nào (tính phí — bác sĩ quyết). Mọi kiểm thử dùng khách giả.
- Kiểm trích dẫn chỉ ở mức ABSTRACT; «không đủ thông tin» không phải trích sai.
- Hội đồng Batch: tranh biện một vòng; model không có công cụ nên căn cứ «lenh» chỉ trỏ được hai lệnh chạy sẵn.
- Giá chỉ ghi cho Sonnet 5.5 (theo `quet_lac_chu_de_kho.py`); model khác chỉ báo token.

## Luật rút ra
Công cụ gọi API trong hệ nghiên cứu luôn: chạy khô mặc định, máy kiểm nguyên văn mọi trích dẫn model đưa ra, ghi sức
khoẻ API chỉ khi lỗi nằm ở kênh, và không bao giờ mở/chặn cổng.
