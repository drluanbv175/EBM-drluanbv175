# 15/11/2026 — Danh mục trích dẫn (quyết định loại của chủ nhiệm) không công cụ nào của repo y khoa đọc; kiểm rút bài chỉ ghi tổng số

**Bác sĩ (nguyên văn):**
- «… Tổng Quan Tài Liệu … Hãy đảm bảo sự đồng bộ xuyên suốt và chính xác nhất»;
- «mỗi vấn đề xây dựng và hoàn thiện phải được cập nhật vào hệ thống»;
- «Hệ thống xây dựng mặc dù đã kết luận về tính hoàn thiện nhưng kiểm lại thì không đạt được sự thống nhất, đồng bộ».

## Phát hiện (kiểm tay, chỉ đọc)

| Đề tài | Phát hiện |
|---|---|
| BTM | Ngày 25/10, chủ nhiệm loại 19 bài khỏi `DANH_MUC_TRICH_DAN_<mã>.json` (không lấy được toàn văn, lệch đề tài). Sổ chứng cứ G1 (A2b) dựng 28/10 vẫn liệt kê **cả 19 bài** như chứng cứ của đề tài. |
| BTM | Bản ghi rút bài G0 chỉ có câu tổng: «56 PMID đã kiểm … 14 nguồn trong nước chỉ có DOI: CHƯA kiểm». Kết quả: **28/47** trích dẫn không đối chiếu được theo từng mã. |
| BTM | SAP, thiết kế G1 và bộ biến G3 dẫn 9 nguồn phương pháp chưa có trong danh mục. |
| C1a | TLTK đề cương nộp sạch: 52 mục, mọi `[n]` có mục, đúng thứ tự Vancouver, không trùng. Biên nhận A12 phủ đủ 35 PMID và 14 DOI. |
| C1a | Biên nhận A12 ngày 15/10 đã **31 ngày**, quá hạn trạng thái rút bài 30 ngày (CLAUDE.md §6.4). Biên nhận nằm trong gói G10 đã băm nên không được ghi đè. |
| C1a | SAP dẫn 3 nguồn trọng số/khảo sát (Lumley 2004 và hai DOI khác) không có trong TLTK đề cương nộp. §4.10 của đề cương mô tả trọng số hậu phân tầng mà không dẫn nguồn. |

**Nguyên nhân gốc:**
- `DANH_MUC_TRICH_DAN` do công cụ EndNote ở repo gốc dựng. Bộ sinh của repo y khoa (`g1_quality_gate.build_supporting_artifacts`) chỉ đọc sàng lọc G0, không biết quyết định loại.
- Không có công cụ kiểm rút bài theo từng trích dẫn của đề tài mà không ghi đè biên nhận A12.
- Không trục máy nào đo TLTK ↔ trích dẫn trong thân ↔ danh mục ↔ văn bản cổng.

**Lỗi trình bày gốc:** cả hai đề tài vẫn ra G10-AUTO-11 «PASS» khi còn các chỗ hở trên. Lý do: mức «cần xem» không đổi trạng thái cổng. Người đọc dễ hiểu «PASS» thành «đồng bộ».

## Cách vá

**Repo y khoa:**
- `tools/danh_muc_trich_dan.py`: một chỗ đọc chung cho danh mục trích dẫn, mục TLTK đánh số và số trích dẫn `[n]`.
- `tools/kiem_rut_bai_trich_dan.py --study <mã> --ghi`: kiểm rút bài từng trích dẫn và ghi `KIEM_RUT_BAI_TRICH_DAN_<mã>.json` theo từng mã. PMID đi qua chuỗi 3 tầng; DOI đi qua Crossref + Retraction Watch. Mã không kết luận được giữ «không biết».
- Đo thật 15/11/2026: BTM 47/47 «ok», C1a 49/49 «ok».
- Trục `trich_dan_tong_quan` (G0 · G1 · G10):
  - **Lệch mềm:** số trích thiếu mục; mục không được trích; sai thứ tự Vancouver; trùng định danh; dùng bài đã loại; mục TLTK chưa có bản ghi kiểm rút bài; bài có tín hiệu rút.
  - **Cần xem:** lần kiểm quá 30 ngày; trích bài G0 sàng là lạc đề; nguồn của văn bản cổng hoặc tham số G3 hoặc guideline khoảng trống chưa vào TLTK/danh mục; sổ A2b còn liệt kê bài đã loại.
- `g1_quality_gate`: sổ A2b tách bài đã loại ra mục riêng, kèm lý do và ngày loại. Đã dựng lại G1 phụ trợ BTM bằng `run_g1_auto.py --dung-lai-ho-tro`.
- `nhat_quan_xuyen_cong.ket_luan_trung_thuc()`: bản in kết thúc bằng «Kết luận: CHƯA đồng bộ hoàn toàn — còn n/N trục mở (…)» khi còn trục chưa khớp.
- `docs/DOI-CHIEU-BIEN-DE-CUONG.md`: bổ sung `ten_de_tai` và `cau_hoi_gia_thuyet` (giai đoạn 1 đã sót tài liệu), cùng `trich_dan_tong_quan`.

**Repo gốc:** dạy `thu-thu-tai-lieu`, `kiem-chung-trich-dan`, `dieu-phoi-g0`, `dieu-phoi-g1`, `dieu-phoi-nghien-cuu`.

## Kiểm hồi quy

- `tests/test_tong_quan_trich_dan_20261115.py`: 21 ca.
- 24/24 đột biến đỏ. Lượt đầu có một đột biến sống sót (luật «TLTK trích bài G0 lạc đề» chưa có ca); đã thêm ca.

## Còn mở (việc của người)

| Đề tài | Việc | Vai |
|---|---|---|
| C1a | Đưa 3 nguồn trọng số của SAP vào TLTK đề cương nộp và dẫn ở §4.10. SAP và gói G10 đã ký: chỉ sửa qua lượt sửa đổi. | PI |
| BTM | Quyết định danh mục trích dẫn có gồm nguồn phương pháp hay không. Nếu có, nguồn phương pháp cũng phải qua luật toàn văn và nạp EndNote. | chủ nhiệm |

## Giới hạn

- Số trích dẫn chỉ nhận dạng `[n]`. Dạng tác giả–năm không được đo.
- Thang đo viết trong ngoặc vuông như `[1–5]` có thể bị đọc nhầm là trích dẫn; nhóm có số 0 thì bỏ qua.
- Nội dung câu trích có đúng bài hay không vẫn là việc của A12 và người đọc toàn văn.
