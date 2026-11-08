# 08/11/2026 — Word/PDF tóm tắt chứng cứ in phần trăm thập phân bằng dấu chấm khi chữ đứng trước giống «số hiệu»

**Phát hiện:** dựng bản ★ PMID 42593701 (guideline S3 PTSD, hàng chờ ⑨) ⇒ PDF in «(tuyên bố 2.2, 90.0%)» trong khi mọi số khác
đã theo quy ước Việt («95,8%»). Bộ dựng (`trinh_bay_vi` → `_doi_so`) coi «90.0» là số hiệu NỐI TIẾP của «tuyên bố 2.2» qua dấu
phẩy — luật viết cho «khuyến cáo 3.1, 3.2».

**Đo trên mọi bản đã dựng** (`~/.ebm-cache/tom-tat-chung-cu/*/tom_tat.json`, bỏ đoạn trích «…» vốn cố ý giữ nguyên): 5 bản, 6
chỗ — ngoài ca nối tiếp còn ba ca chữ đứng trước trùng từ khoá số hiệu: «toàn phần 99.8%» («phần» = mục), «điển hình 7.7%»
(«hình» = hình vẽ), «phân tích (0.5%», «hạng V 16.8–38.3%» («V» = phiên bản). Dữ kiện trong `tom_tat.json` đúng (cổng số + kiểm
chéo so NGUYÊN VĂN bài) — lỗi chỉ ở cách in.

**Vá** (`tools/tom_tat_chung_cu_word.py`): số đi kèm «%» (kể cả đầu khoảng «16.8–38.3%») luôn là số đo, không xét luật số hiệu.
Số hiệu thật («khuyến cáo 1.1, 1.2 và 1.3», «Bảng 12.1», «Phân tích 7.1 và 7.2») và đoạn trích «…» không đổi.

**Kiểm:** `tools/test_tom_tat_so_phan_tram_20261108.py` (13 ca); đột biến bỏ chốt «%» ⇒ 5 ca đỏ, phục hồi ⇒ xanh;
`tools/test_tom_tat_trinh_bay_vi_20261104.py` vẫn đạt. Năm bản cũ dựng lại Word/PDF sau khi gộp (bản ghi EndNote giữ nguyên, chỉ
thay tệp PDF đính kèm).
