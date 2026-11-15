# 15/11/2026 — Hạn chế mở của G1 chưa vào đề cương; bảng kiểm báo cáo bỏ chuẩn mở rộng của đề tài (giai đoạn 8–9)

**Bác sĩ (nguyên văn):** «Tiếp tục các giai đoạn còn lại; Sau đó kiểm tra lại Hệ thống xây dựng mặc dù đã kết luận về tính hoàn thiện nhưng kiểm lại thì không đạt được sự thống nhất, đồng bộ ....» — giai đoạn 8 (giải thích & bàn luận) và 9 (báo cáo & công bố) trong chương trình đồng bộ 9 giai đoạn. Hai đề tài CHƯA có dữ liệu ⇒ chỉ kiểm được phần ĐÃ BIẾT TRƯỚC: hạn chế khai ở G1 và chuẩn báo cáo áp cho bản thảo.

## Phát hiện (kiểm tay C1a, BTM)

| Chỗ hở | Đề tài | Chi tiết |
|---|---|---|
| Hạn chế mở của G1 không có trong mục «Hạn chế» của đề cương nộp | C1a | G1 ghi hai sai lệch `trang_thai` «… hạn chế mở»: **nhiễu tồn dư** và **tình trạng sức khỏe/kỳ vọng của người bệnh**. Bảng 4.9 «Hạn chế» của đề cương nộp không nêu cả hai ⇒ Hội đồng không thấy, và phần Bàn luận sau này dễ bỏ. Không công cụ nào nối G1 ↔ mục «Hạn chế». |
| Bảng kiểm báo cáo G7 chỉ có chuẩn chính | C1a, BTM | `run_g7_auto.generate_checklist` sinh «STROBE 2007, 22 mục» nhưng bỏ chuẩn mở rộng G1 đã chốt ở giai đoạn 4 (`reporting_extensions`): CROSS cho khảo sát C1a, RECORD cho dữ liệu thường quy BTM. Bản thảo viết theo bảng kiểm đó sẽ thiếu mục báo cáo đặc thù (tỷ lệ đáp ứng, mã hoá/thuật toán chọn quần thể). |
| BTM chưa có đề cương nộp | BTM | SL-09 không đo được ⇒ tự bỏ qua (không báo đỏ giả). |

## Cách vá

**Repo y khoa:**
- **SL-09 của `tools/doi_chieu_sai_lech_sap.py`:** dòng đối chiếu của sai lệch G1 «hạn chế mở» phải khai cột mới `neo_han_che` (cụm chữ NGUYÊN VĂN) và cụm đó phải nằm trong mục «Hạn chế…» của `DE_CUONG_NOP_HOI_DONG_<mã>.md` (tới tiêu đề cùng cấp kế tiếp); chưa có đề cương ⇒ bỏ qua. Đi qua trục `kiem_soat_sai_lech` sẵn có.
- **`run_g7_auto.khoi_bang_kiem_mo_rong`:** `generate_checklist(..., reporting_extensions=)` thêm khối «Bảng kiểm mở rộng bắt buộc» cho từng chuẩn của G1, dẫn nguồn bảng kiểm gốc từ `skill_standards.NGUON_CHUAN_MO_RONG` — chỉ trích dẫn đã có trong danh mục của đề tài và đã kiểm rút bài (CROSS PMID 33886027; RECORD PMID 26440803); chuẩn chưa có nguồn đã kiểm ⇒ `[CẦN KIỂM CHỨNG NGUỒN CHÍNH THỨC]`. KHÔNG chép nguyên văn từng mục bảng kiểm.
- **Dữ liệu C1a:** Bảng 4.9 của đề cương nộp thêm 2 dòng (Nhiễu tồn dư; Tình trạng sức khỏe và kỳ vọng của người bệnh) — chiều sai lệch và biện pháp lấy từ G1/SAP, không thêm khẳng định mới; sinh lại `.docx`. `_doi-chieu-sai-lech-sap.csv` của cả hai đề tài thêm cột `neo_han_che` (C1a: 4 neo; BTM: cột rỗng vì chưa có đề cương).

**Repo gốc:** dạy `viet-ban-thao`, `dien-giai-ket-qua`, `binh-duyet`, `dieu-phoi-g7`.

## Kiểm hồi quy

- `tests/test_thiet_ke_20261115.py`: thêm ca SL-09 (đủ neo · thiếu neo · neo không có trong mục Hạn chế · chưa có đề cương ⇒ bỏ qua) và ca bảng kiểm mở rộng G7; 6/6 đột biến đỏ đúng ca.
- Đề cương C1a cũ chạy qua SL-09: 2 lỗi (đúng hai hạn chế mở bị thiếu). Sau khi sửa: 0 lỗi.

## Còn mở (việc của người / chưa đo được)

| Việc | Vai |
|---|---|
| Phần Bàn luận thật (so sánh y văn, ý nghĩa lâm sàng, điểm mạnh) — chỉ viết được sau khi có kết quả; máy hiện chỉ kiểm hạn chế mở đã có trong đề cương | người viết + `dien-giai-ket-qua` sau G6 |
| Điền bảng kiểm gốc CROSS/RECORD kèm vị trí trong bản thảo | người viết bản thảo, kiểm ở G8 |
| BTM: viết đề cương nộp (cần PI đồng ý) ⇒ SL-09 mới đo được | PI |
