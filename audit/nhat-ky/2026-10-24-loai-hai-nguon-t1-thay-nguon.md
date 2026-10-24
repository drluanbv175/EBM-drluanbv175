# 24/10/2026 — Bác sĩ loại hai nguồn T1 (PMID 36170288, 36728514): thay nguồn bằng phiên bản nối tiếp; hub VKDT kẹt vì ITEM-38 trùng mã

**Quyết định (nguyên văn).** «Loại PMID 36170288 (nguồn của ITEM-25),PMID 36728514 (nguồn của ITEM-03, con số «AUC 0,84»)» — sau
khi lượt tóm tắt chi tiết T1 đề xuất CAN_NHAC_LOAI (n=29 không tiêu chuẩn tham chiếu; hồi cứu một trung tâm 57 ca tử vong, PROBAST cao).

**Cách làm (quy trình đúng — dùng lại lần sau).**
1. Không sửa đè dashboard cũ: lưu bản sửa thành PHIÊN BẢN NỐI TIẾP ngày mới (`…_VKDT_TongHop_20261024.html`,
   `…_TienLuongSuyTim_20261024.html`), bản cũ trả nguyên từ sao lưu.
2. Thay nguồn bằng nguồn tốt hơn đã tra PubMed + kiểm rút bài: ITEM-25 ⇒ 2022 EULAR recommendations (PMID 36328476, khuyến cáo 2:
   LoE 2b, GoR B thang Oxford — đọc bản CC BY 4.0 trên HAL); ITEM-03 ⇒ Khanam 2018 (PMID 30485284, PMC) làm nguồn chính, kèm Pocock
   2013 / Sartipy 2014 / Sawano 2018. Bỏ khẳng định mà nguồn mới không nói («đặc biệt nếu đã tiêm BCG» — EULAR không nêu).
   Giữ `decision`/`gradeLevel`/`normativeBasis`; sửa cả câu tóm tắt dashboard còn trích số cũ («MAGGIC (AUC 0,84)»).
3. Cổng `verify_dashboard` (PASS) → `so_xac_minh_nguon.py --quet` → `ingest_dashboard.py --noi-tiep` (chạy khô rồi `--ap-dung`) →
   `xuat_goi_cap_nhat.py --online` → `endnote_loai_tru` cho PMID bị loại + nhóm «_Cho thung rac <ngày>».

**Vướng còn mở.**
- Hub VKDT: `--noi-tiep` dừng fail-closed «Bản cũ có hai mục cùng khoá ITEM-38» (RCT ngưng methotrexate khi tiêm cúm và guideline
  PANLAR 2026 cùng mang ITEM-38 trong bản 17/07). Thẻ EVID-2026-0675 còn nguồn cũ — chờ bác sĩ quyết đánh lại mã.
- Pocock 2013 (OUP, điều khoản cấm dùng với AI) không đọc được toàn văn khi không có phiên Chrome uỷ quyền ⇒ không làm nguồn chính
  của mục `apply` (cổng BH161 đòi đã đọc toàn văn).
- NCBI chặn IP (misuse) + Europe PMC 503 làm 3 PMID «chưa kiểm rút bài» tới khi bác sĩ bật lại VPN (IP thoát đổi) — đo lại thì đủ.

Hồ sơ: `state/loai-nguon-20261024.md` (ngoài git). Cần bác sĩ kiểm chứng.
