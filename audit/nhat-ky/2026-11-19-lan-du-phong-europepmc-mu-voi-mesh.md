# 19/11/2026 — Làn dự phòng Europe PMC gần như MÙ với mọi truy vấn MeSH (và RAISE với 106 truy vấn watchlist)

**Phát hiện:** kiểm toàn diện hệ chứng cứ, bộ test `pytest tools/` trên máy thật.
- `test_toan_bo_watchlist_that_dich_duoc_neu_co_du_lieu` ĐỎ. CI bỏ qua test này vì thiếu `EBM-Dashboards`.

**Nguyên nhân** (`surveillance_scan.dich_pubmed_sang_europepmc`, bộ dịch PubMed → Europe PMC dùng khi NCBI chặn — BH113):
1. **106/1485 truy vấn watchlist thật** dùng `[MeSH Major Topic]` (71) và `[mesh]` (35). Hai thẻ này không có trong bảng dịch ⇒ RAISE (fail-closed đúng thiết kế), nên các chủ đề đó MẤT giám sát khi NCBI chặn. Có ghi nhớ «MeSH Major hở» từ 30/10.
2. `[mh]` dịch sang `MESH:`, nhưng danh mục `/fields` của Europe PMC không có trường MeSH nào. Đo 19/11, theo PubMed `[mh:noexp]` → Europe PMC (lọc `SRC:MED`):

   | MeSH | PubMed | `MESH:` | `KW:` |
   |---|---|---|---|
   | Dyslipidemias | 17.022 | 374 | 17.456 |
   | Hypercholesterolemia | 28.224 | 3.352 | 31.923 |
   | Liver Neoplasms | 200.992 | 1.774 | 215.196 |

   ⇒ `MESH:` chỉ bắt 0,4–12% số bài, làn dự phòng gần như mù.
3. Kiểm chéo theo PMID: 54/60 bài mẫu từ `KW:"Dyslipidemias"` đúng là có MeSH đó trong PubMed (32/60 là chủ đề chính).

**Cách vá** (PR gốc «hoàn thiện chứng cứ 19/11»):
- Mọi thẻ MeSH (`mh`, `mesh`, `mesh terms`, `majr`, `mesh major topic`, kể cả `:noexp`) dịch sang `KW:`.
- Europe PMC không có trường «chủ đề chính» ⇒ `[majr]` thành tập RỘNG hơn (thêm nhiễu, không bỏ sót). Đây là làn đã gắn PASS_DEGRADED.
- Europe PMC cũng không mở rộng cây MeSH (≈ `[mh:noexp]`).

**Kiểm:**
- 1485/1485 truy vấn thật dịch được (trước: 106 lỗi).
- Truy vấn rối loạn lipid máu dịch xong trả 41 bài 2025–2026 trên Europe PMC thật.
- Test bộ dịch 24/24; chốt BH113 thêm phép kiểm MeSH ⇒ KW.
- Đột biến (trả ánh xạ `MESH:`) ⇒ test + BH113 ĐỎ.

**Bài học:** bộ dịch cú pháp phải được ĐO bằng số kết quả thật so với nguồn gốc, không chỉ kiểm «không còn thẻ chưa dịch». Một trường «hợp lệ về cú pháp» vẫn có thể gần như rỗng.
