# 24/10/2026 — `--gan-kho` không gắn toàn văn cho bản ghi nhập từ Web of Science («WOS:…») hoặc ghi «PMID: n»

**Phát hiện.** Đo toàn bộ thư viện (chỉ đọc, 24/10 tối): 144 bản ghi «chỉ có DOI». Tra PubMed `<doi>[doi]` (chỉ nhận đúng MỘT
PMID và esummary ghi lại đúng DOI): 90 có PMID — nhưng Accession Number của cả 90 đã có giá trị: 84 «WOS:…» (nhập từ Web of
Science), 6 «PMID: n». Lượt gom cho 87 PMID (3 là bản TRÙNG của bản ghi khác) lấy về 57 toàn văn mà
«0 có bản ghi trong thư viện · gắn thêm 0»: `gan_kho` chỉ tìm Accession Number == PMID thuần số.

**Vá.** `tools/nap_endnote_chu_de.py::gan_kho` thêm hai bậc cho PMID còn thiếu: (1) «PMID: n»; (2) DOI của PMID theo PubMed
(`doi_cua_pmid`: efetch, NCBI lỗi ⇒ Europe PMC) khớp trường DOI — bỏ bản ghi có Accession Number là MỘT PMID KHÁC
(`_la_pmid_khac`). Tra DOI lỗi ⇒ `doi_khong_do_duoc` + dòng ⚪, không gắn theo DOI lượt đó (không phải «không có»). Không ghi đè
Accession Number (mã WoS giữ nguyên). Mọi công cụ sinh PDF gọi `--gan-kho` qua `main` nên tự hưởng.

**Kiểm.** `tools/test_endnote_gan_kho_khop_doi_20261024.py` (7 ca); 6 đột biến đều đỏ (bỏ bậc «PMID: n», bỏ chặn PMID khác,
`main` không truyền `doi_cua`, không bắt lỗi tra DOI, không lùi Europe PMC, tra DOI cả PMID đã khớp). Chạy khô trên thư viện thật
bằng mã mới: «1212 có bản ghi (khớp «PMID: n» 5 · khớp DOI 57) · sẽ gắn 0» — đúng 57 bản ghi đã gắn tay trước đó bằng
`state/gan-pdf-theo-doi-20261024.py`.

**Còn mở (việc của bác sĩ).** 3 bản ghi WoS trùng PMID với bản ghi khác (rec 4875↔6378, 5142↔5037, 5902↔5736) — chọn bản giữ;
117 bản ghi không định danh và 54 bản ghi có DOI nhưng không có trong PubMed (gắn được 11 bản mở hợp lệ qua Unpaywall/PMC).

Cần bác sĩ kiểm chứng.
