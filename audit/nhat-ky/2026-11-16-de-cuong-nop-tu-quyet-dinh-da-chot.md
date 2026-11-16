# 16/11/2026 — Đề cương giả lập đọc như văn bản lỗi: thêm bộ sinh đề cương nộp Hội đồng + vá câu chữ G2/G3/G7/StudySpec

## Bối cảnh
Bác sĩ đọc đề cương của các đề tài giả lập (bản lắp `DE_CUONG_THONG_NHAT_<mã>`) và nhận xét: «không đúng với một đề
cương hoàn chỉnh vì những câu chữ, từ ngữ không phù hợp … hãy loại bỏ những vấn đề đó và cập nhật vào hệ thống».

Đọc lại bản RCT, liệt kê được các loại lỗi câu chữ:
- dấu vết nội bộ trong văn xuôi: «(G1 — đã chốt)», «(SAP §4 — đã chốt ở G4)», «*(điền sẵn từ quyết định đã chốt…)*»,
  «(SPIRIT 21b)», «(PI đã chốt — gate_params.G2…)», «SAP SAP §4», mã cổng, «§», cảnh báo ⚠, tên biến «(`nhom`)»,
  đường dẫn tuyệt đối của máy chạy (sổ bằng chứng G1);
- nhãn «(GIẢ LẬP CANARY — dữ liệu tổng hợp, không PII)» và «(giả lập)» gắn sau TỪNG câu, mã «PI-REF-01 (chủ nhiệm — mã
  vai trò, giả lập)» chèn giữa câu (kể cả «PI-REF-01 sẽ PI-REF-01» trong phiếu đồng ý);
- phiếu đồng ý G2 để ô trống những điều G1 đã chốt (mục đích, các bước, nhóm, xác suất 1:1, làm mù, số lần đến) rồi bộ
  giả lập điền «(GIẢ LẬP — hồ sơ chưa có)»; ô «Tổng thời gian tham gia ước tính» bị điền «TP. Hồ Chí Minh» (mẫu «tinh»
  khớp «ước tính»); dòng rủi ro cắt cứng 80 ký tự giữa chữ («quy trình vi»); dòng ký tên bị điền chữ;
- khối «cỡ mẫu dán vào đề cương» của G3 còn tên công thức tiếng Anh và lời dặn dòng lệnh «[CẦN — --p0 ở đây là …]»,
  chép nguyên vào bản thảo G7;
- StudySpec mô tả can thiệp bằng nhãn biến «nhóm nhận tin nhắn SMS (`nhom`)» thay can thiệp đã chốt ở G1.

Doctrine từ 15/10: bản lắp G10 là hồ sơ truy xuất nội bộ; bản NỘP là `DE_CUONG_NOP_HOI_DONG_<mã>` viết tay, kiểm bằng
`kiem_de_cuong_nop_hoi_dong.py` (K1–K7). Hệ chưa có cách dựng bản nộp — mọi đề tài mới phải viết tay từ đầu.

## Đã làm (repo y khoa, nhánh `claude/gia-lap-bien-the-kho-20261116`)
1. **`tools/sinh_de_cuong_nop_hoi_dong.py`** — dựng bản nộp từ quyết định đã chốt (StudySpec, G3, SAP, phiếu đồng ý G2,
   từ điển dữ liệu, biên nhận A12) theo cấu trúc đề cương tiếng Việt; lớp `lam_sach()` gỡ mọi dấu vết nội bộ; đoạn cỡ mẫu
   tiếng Việt dựng từ số G3 (hai tỷ lệ, không kém hơn, Schoenfeld, ước lượng tỷ lệ, AUC, cụm có DE, định tính, tổng quan);
   phiếu đồng ý thành văn bản liền mạch (bỏ khung, dòng «AI hỗ trợ», mục/bước «không áp dụng», đánh số lại); phiếu thu
   thập và bảng biến số dựng từ từ điển; TLTK Vancouver hai lượt (nguồn SAP, đề cương lắp, G3, danh mục trích dẫn — chỉ
   PMID sạch trong A12; số theo thứ tự xuất hiện); bìa ghi phiên bản. Không ghi đè bản viết tay (dấu máy dòng đầu).
2. **K3 theo thiết kế**: tổng quan hệ thống không đòi phụ lục phiếu đồng ý; nhận «phiếu trích xuất dữ liệu».
3. **G2** `_icf_tu_g1`: phiếu đồng ý tự điền từ G1 (mục đích bằng lời thường — thử nghiệm không kém hơn không hứa «cải
   thiện»; bước theo thiết kế; thời gian và số lần đến chỉ khi lịch là danh sách mốc; nhóm; xác suất từ tỷ lệ; ai biết
   nhóm từ làm mù; lựa chọn thay thế = đối chứng), người thực hiện từ `administrative`, quy trình tóm tắt từ
   `study_schema_timeline`; dòng rủi ro ngắt theo từ.
4. **G7** `_cong_thuc_g3_sach`: bỏ lời dặn dòng lệnh khỏi mô tả công thức G3 trước khi đưa vào bản thảo.
5. **StudySpec**: mô tả can thiệp ưu tiên G1 → PICO → nhãn biến; sổ bằng chứng chỉ ghi tên tệp.
6. **Bộ giả lập**: bỏ nhãn «(giả lập)» khỏi từng câu (tính tổng hợp giữ ở mã ZZCANARY, `study_kind` và sổ
   `gia_lap_pi_dien`; đề cương có một dòng ghi chú ở bìa); tên ví dụ «BS. Nguyễn Văn A», «ThS. Trần Thị B» thay mã vai
   trò; giữ trống chỗ ký G2; câu hướng dẫn «[CẦN]» đọc thành «ô trống»; gỡ dấu nhắc «[CẦN CHỦ NHIỆM XÁC NHẬN]:»; câu
   trả lời của chủ nhiệm cho các ô phiếu đồng ý và SAP §13–15; bước G10 gọi bộ sinh; phép thử trọn vòng đòi K1–K7 sạch.

## Kiểm
- `tests/test_sinh_de_cuong_nop_hoi_dong_20261116.py` (30 phép); đột biến 12/12 đỏ đúng chỗ, phục hồi xanh (đột biến gỡ
  nhãn giả lập sống sót khi chỉ tắt một mẫu vì có mẫu không phân biệt hoa thường dự phòng — tắt cả ba mẫu thì đỏ).
- Sinh trên bản sao 12 đề tài giả lập: đạt K1–K7; trục `de_cuong_nop` và `trich_dan_tong_quan` của
  `nhat_quan_xuyen_cong` về `khop` sau khi sửa thứ tự Vancouver và dòng phiên bản bìa.
- Kết quả trọn vòng 15 kịch bản và trọn bộ phép thử liên quan: xem PR repo y khoa.

## Giới hạn còn lại
- Bản máy là BẢN THẢO: văn phong bám câu chữ đã chốt ở các cổng (đặt vấn đề/tổng quan ngắn khi G1 ghi ngắn); chủ nhiệm
  biên tập trước khi nộp. Chưa có bản dịch phiếu đồng ý tiếng Anh tự động; nội dung hướng dẫn phỏng vấn định tính chưa
  có nguồn dữ liệu riêng (phụ lục C chỉ có phần thông tin người tham gia từ từ điển).
