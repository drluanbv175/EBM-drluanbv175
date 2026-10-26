# 26/10/2026 — Bản in JATS (BANIN) bỏ khai xung đột lợi ích và tài trợ ⇒ tóm tắt ⑨ kết luận sai «bài không khai»

**Phát hiện.** Kiểm chéo độc lập PMID 42914541 (BMJ Open) chấm sai câu «bản XML PMC không có mục khai xung đột lợi ích». XML gốc
có `<fn fn-type="COI-statement">None declared.</fn>`, nhưng nằm trong `article-meta/author-notes`. `tools/in_pdf_toan_van_kho.py::
jats_sang_html` chỉ in tiêu đề, tác giả, abstract, thân bài và `back`; `author-notes` bị bỏ hẳn, `funding-group` nằm trong
`_BO_QUA`. Bước ⑨ đọc đúng tệp PDF gắn trong EndNote (bản in đó) nên không bao giờ thấy các khai báo này.

**Phạm vi đo.** 752 bản in từ JATS trong kho: 267 có `author-notes/fn`, 288 có `funding-group`. 21 tóm tắt ⑨ đã kiểm chéo dựa trên
các bản in này. Đối chiếu XML gốc: kết luận sai thật ở 42799440 (FIGO/WHF — bài CÓ khai tư vấn cho Gedeon Richter, Merck… nhưng
tóm tắt ghi «không có công bố xung đột lợi ích», AGREE II Miền 6 «không có thông tin») và 42914541. Không chính xác ở 42877103
(«không có mục tài trợ», trong khi bài khai không nhận hỗ trợ tài chính) và 36170288. Năm bài còn lại chỉ thiếu ghi chú tác
giả đồng hạng, ghi chú biên tập hoặc ORCID — không đổi kết luận.

**Cách vá.** `_khai_bao_tac_gia(meta)`: in `author-notes/fn` (bỏ `corresp` — địa chỉ liên hệ) và `funding-group` (câu
`funding-statement`; không có thì tên nhà tài trợ + mã tài trợ) thành mục «Author notes and funding (article metadata)» cuối bản in.

**Kiểm hồi quy.** `test_jats_giu_khai_xung_dot_loi_ich_va_tai_tro_bo_dia_chi_lien_he`: 4 đột biến (bỏ author-notes · in cả corresp
· bỏ tên nhà tài trợ · bỏ câu khai tài trợ) đều đỏ đúng chỗ rồi xanh lại; 11 test đạt; ruff sạch. Thử trên XML thật 42799440,
42914541: khai báo hiện đủ.

**Việc còn lại.** Bản in cũ trong kho và bản đã gắn EndNote không tự đổi. In lại và thay tệp đính kèm là việc ghi vào thư viện
EndNote ⇒ chờ bác sĩ quyết. Bốn tóm tắt bị ảnh hưởng sửa riêng, có kiểm chéo đối chiếu XML.
