# 02/11/2026 — Tầng Unpaywall lưu PDF của bài KHÁC thành toàn văn, và tải lại mỗi lượt bộ năm (BH175)

**Mã:** BH175. **Phát hiện:** bước ⑨ (`tools/tom_tat_chung_cu_word.py`, phép kiểm định danh) chặn tóm tắt Word cho PMID 38099896
trong lượt cập nhật «Suy tim người cao tuổi» 02/11.

## Chuyện gì đã xảy ra

PMID 38099896 (ISHLT 2023 «Assessing and managing frailty in advanced heart failure», doi 10.1016/j.healun.2023.09.013). Unpaywall
trả 4 vị trí OA; bản của NXB (jhltonline, Elsevier) không mang giấy phép nên cổng điều khoản BH160 chặn đúng. Vị trí DUY NHẤT qua
cổng là kho KU Leuven (Lirias, ghi cc-by), nhưng tệp ở đó là một bài JMIR khác hẳn («Mapping the Cardiometabolic Patient
Experience…», Liska et al.; hai bài có chung một đồng tác giả ở KU Leuven).

`gom_toan_van_dashboard._tai_vi_tri_upw` chỉ kiểm 5 byte đầu `%PDF-` rồi ghi `PMID-38099896_UPW.pdf`. Hậu quả:

- tệp mang tên hợp lệ nên `co_toan_van_trong_kho` / `bao_phu_cuc_bo` tính là «có toàn văn» (BH161 sẽ coi là đã đọc nếu mục là `apply`);
- bước gắn kho EndNote gắn tệp vào rec 7914;
- mỗi lượt `xuat_goi_cap_nhat.py --online` (bước ⑦) tải lại ĐÚNG tệp đó. Lượt 18:06 và lượt 19:0x đều tải; hai bản đã được dời
  sang `EBM-Dashboards/_cach-ly-toan-van-sai-bai/` để làm mẫu kiểm.

Đo trên mẫu cách ly bằng đúng hàm của bước ⑨: 11 trang, 2 444 từ ở 3 trang đầu, chỉ 38% từ của tiêu đề ISHLT, không có DOI ⇒ sai bài.

## Vì sao lọt

Ba cổng của tầng 2 đều có, nhưng không cổng nào hỏi «có đúng bài này không»: cổng điều khoản (BH160) xét GIẤY PHÉP của vị trí, cổng
nội dung (BH164) xét bản có phải TOÀN VĂN không, và nhánh PDF thì không qua cổng nội dung nào. Kho lưu trữ trường đại học gắn nhầm tệp
là chuyện có thật, và giấy phép cc-by của vị trí đó vẫn hợp lệ.

## Cách vá

- `kiem_dinh_danh_upw()` dùng CHUNG `tach_trang` + `khop_dinh_danh` của bước ⑨ (nạp bằng importlib, không viết logic song song):
  DOI có trong văn bản, hoặc ≥ 60% từ (≥ 4 chữ) của tiêu đề Unpaywall có ở 3 trang đầu. `tach_trang` nay nhận cả bytes.
- Áp cho cả ba nhánh lưu của `_tai_vi_tri_upw`: PDF, HTML (sau cổng toàn văn BH164; dùng thân bài cắt thành «trang» 800 từ) và JATS
  lấy qua PMC (PMCID có thể chỉ là một liên kết trong trang — không khớp thì bỏ JATS, xét tiếp chính trang).
- Kết luận: `dung` (chỉ kết luận này được lưu) · `sai_bai` · `khong_kiem_duoc` (PDF hỏng/không có lớp chữ, không có tiêu đề) ·
  `thieu_cong_cu` (thiếu pypdf — lỗi máy). Bị từ chối ⇒ vào `SAI_BAI_UNPAYWALL`, in một dòng ⚠, liệt kê trong `DO-PHU-OA.md`.
- Sổ `toan_van_oa/upw-sai-bai.json`: (PMID, URL) bị `sai_bai`/`khong_kiem_duoc` không được tải lại trong 30 ngày (cùng nhịp sổ
  «không-OA»); `thieu_cong_cu` KHÔNG ghi sổ (lượt sau thử lại). Sổ hỏng ⇒ coi như rỗng — mất sổ chỉ làm tải lại một lần.
- CI `kiem-tinh-da-nen` cài thêm `pypdf`: thiếu thư viện thì cổng (đúng) từ chối mọi PDF và các test lưu PDF phải đỏ, không skip.

## Kiểm hồi quy

- Test mới `tools/test_gom_unpaywall_dinh_danh_20261102.py` (13): ca thật mô phỏng · lượt hai không tải lại · sổ hết hạn thì thử
  lại · vị trí đầu sai thì thử vị trí kế · PDF đúng qua tiêu đề hoặc chỉ qua DOI · HTML toàn văn của bài khác · JATS PMC của bài khác ·
  thiếu pypdf · PDF không có chữ · cùng kết luận với `khop_dinh_danh` · sổ hỏng.
- Fixture của 4 tệp test cũ sửa cho HỢP LỆ (không nới assertion): «PDF» cũ là `%PDF-1.7` + rác — pypdf không đọc được, nay dựng PDF
  thật bằng `tools/pdf_gia_kiem_thu.py`; Unpaywall giả trả `title` như bản thật, trang giả mang đúng tiêu đề đó.
- Chốt BH175 gọi THẬT `tang_unpaywall` với mạng giả. Đột biến 4 phép (`python -B`, xoá `__pycache__`, sao lưu + `cmp`): bỏ kiểm PDF ·
  bỏ sổ URL · bỏ kiểm HTML · cổng chặn tất cả ⇒ cả bốn làm chốt đỏ đúng câu; phục hồi ⇒ xanh.

## Đo thêm 03/11 (chỉ đọc, chưa xử lý)

Quét 81 tệp `PMID-*_UPW.pdf` đang có trong kho bằng cổng mới, DOI + tiêu đề lấy từ chuỗi trích dẫn trong DATA của dashboard
(EndNote đọc lỗi `DatabaseError` lúc đo): **42 khớp · 2 sai bài · 37 không có dữ kiện định danh trong dashboard** (chưa kiểm được).

- 39186635 — dashboard: Ha JT et al., HIF prolyl hydroxylase inhibitors in kidney disease (NEJM Evid 2024); tệp là bài khác
  («Dapagliflozin and anemia in patients with chronic kidney disease», Koshino et al.). Mục dashboard Huyết học: `consider`.
- 42701440 — dashboard: Brunton S et al., khung nguy cơ tim phổi COPD (Int J COPD 2026); tệp là NCHS Data Brief 521 «Mortality in
  the United States, 2023». Mục dashboard COPD: `consider`. Bài này còn có bản `_PMC13545340.xml`.

Cả ba ca (kể cả 38099896) đều là `consider` ⇒ BH161 (chỉ xét `apply`) không bị qua cổng sai, nhưng toàn văn sai vẫn đi vào đọc sâu,
đối chiếu số và đính kèm EndNote.

## Giới hạn đã biết

- Luật của bước ⑨ nhận DOI ở BẤT KỲ đâu trong PDF, kể cả danh mục tham khảo: bài khác TRÍCH bài cần tìm sẽ qua cổng. Với HTML, cổng
  dùng thân bài đã bỏ References nên hở này nhỏ hơn. Sửa luật là sửa `khop_dinh_danh` (một nơi, cho cả bước ⑨).
- Tiêu đề chung chung (toàn từ phổ biến của chủ đề) có thể đạt 60% trên 3 trang đầu của một bài cùng chủ đề.
- PDF ảnh (không có lớp chữ) bị từ chối là `khong_kiem_duoc` — thà thiếu toàn văn còn hơn tính «đã đọc» một tệp máy không đọc được.
- Máy chạy bộ năm phải có pypdf (`~/.ebm-venv` và python3 hệ thống trên Mac có, đo 03/11); máy Windows chưa đo.

## Việc của bác sĩ / còn lại

- Gỡ tệp đính kèm sai ở EndNote rec 7914 (bác sĩ; agent không đụng EndNote).
- Hai tệp sai bài ở trên: dời sang `_cach-ly-toan-van-sai-bai/` (không xoá) và kiểm đính kèm EndNote của hai bản ghi đó.
- 37 tệp chưa kiểm được: cần rà định danh với PubMed/Crossref khi có mạng (công cụ rà toàn kho chưa có).
