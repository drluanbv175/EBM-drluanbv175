# 15/10/2026 — Cổng toàn văn nhận trang tường phí dài, bỏ sót toàn văn CMAJ (BH164)

**Mã chốt:** BH164 (mới) · liên quan BH160 (cổng nội dung tầng Unpaywall), BH161 (bảo đảm đọc toàn văn), TT-04 (phiên Chrome
`--nhan` dùng chung cổng). Sự cố gốc của cổng nội dung: `2026-10-04-unpaywall-cong-giay-phep-trang-gioi-thieu.md`.

## Nguyên nhân

`tools/gom_toan_van_dashboard.py::la_toan_van_html` nhận CHỮ THÔ cả trang (`_van_ban_tho` bỏ hết thẻ) nên mù cấu trúc đề mục,
và nhánh «≥ 6000 từ ⇒ toàn văn» chạy TRƯỚC mọi dấu nhận diện.

1. **Dương tính giả (đo 15/10):** trang Nature Reviews Cardiology KHÔNG có quyền (PMID 27811932,
   `nature.com/articles/nrcardio.2016.174`) chỉ có các h2 Key Points · Abstract · «Access options» · References ·
   Acknowledgements · Author information · … — thân bài ~575 từ — nhưng danh mục tham khảo (~495 KB markup) kéo tổng lên
   8 743 từ ⇒ cổng trả `(True, '8743 từ')` ⇒ `phien_uy_quyen_chrome.kiem_tep` nhận tệp vào kho `PMID-27811932_CHR.html` ⇒ có
   thể bị BH161 tính «đã đọc toàn văn». Bác sĩ đã chuyển tệp vào Thùng rác (giữ làm tham chiếu cấu trúc; repo chỉ có fixture
   TỔNG HỢP cùng cấu trúc đề mục, không chép nội dung bài).
2. **Âm tính giả (đo 15/10, báo từ phiên «Cài đặt cho Endnote»):** CMAJ (PMID 16129869, Rockwood 2005, lưu từ PMC1188185
   qua phiên Chrome 04/10; PMC1188185 không thuộc tập OA nên không có đường dữ liệu thay) có 5 189 từ, tóm tắt h3
   Background/Methods/Results/Interpretation, thân bài h2 Methods · Results · Interpretation, mở bài không đề mục — CMAJ dùng
   «Interpretation» thay «Discussion» ⇒ chỉ đếm được 2 đề mục IMRaD ⇒ mục apply NguoiCaoTuoi_DaBenhLy_NgoaiTru_20260811
   ITEM-05 rơi vào sổ nợ BH161.
3. **Bản sao thứ hai của cùng luật:** `verify_dashboard._html_la_toan_van` (cổng BH161, 4 bản đồng bộ byte) có bản chép riêng
   của luật ≥ 6000 từ — vá một nơi thì tệp lọt vẫn được cổng chặn xuất tính «đã đọc».

## Cách vá

- Cổng nhận NGUYÊN VĂN HTML; `phan_tich_trang_html` tách thân bài theo thẻ h1–h6: bỏ khối hậu bài (References · Bibliography ·
  Author information · Acknowledgements · Rights and permissions · About this article · Cite this article · Cited by · Similar
  content…) cùng mọi tiểu mục; đề mục rỗng không phải ranh giới.
- **Đề mục tường phí** (Access options · Buy article PDF · Rent or buy · Purchase PDF · Get access · Access through your
  institution) xét TRƯỚC ngưỡng 6000 — chỉ khi là THẺ đề mục, không xét chuỗi toàn trang («Subscribe to this journal» ở thanh
  bên trang có quyền không bị tính). **Không phải án tuyệt đối:** đo 15/10, trang SAGE CÓ quyền (40277321 · 42084558 ·
  42751933 — toàn văn đủ IMRaD) vẫn có h4 «Access options» trong menu «View options» ⇒ có đề mục tường phí mà thân bài tự
  chứng minh cấu trúc toàn văn thì vẫn nhận.
- Nhóm IMRaD nhận đồng nghĩa (Background ≈ Introduction; Interpretation/Comment/Conclusions ≈ Discussion) CHỈ khi là thẻ đề mục
  NGOÀI khối tóm tắt (tiểu mục của «Abstract/Summary/Key Points» không tính) — tóm tắt có cấu trúc không tự đủ ba nhóm.
- Ngưỡng hiệu chỉnh lại trên THÂN BÀI (đo 303 tệp HTML của kho): trang tường phí/giới thiệu 575–1 463 từ thân bài, ≤ 5 mục nội
  dung; toàn văn không IMRaD (tổng quan, báo cáo lâm sàng — 28193791, 31461595, 39647534, 42107500, 42447589) 4 054–5 764 từ,
  10–22 mục — trước đây chỉ qua ngưỡng 6000 nhờ References. Thêm hai luật cấu trúc: bài ngắn ≥ 1 500 từ + ≥ 3 nhóm IMRaD bằng
  thẻ + ≥ 5 mục (42702887); bài không IMRaD ≥ 2 500 từ + ≥ 8 mục nội dung.
- Ba nơi gọi (`tang_unpaywall`, `phien_uy_quyen_chrome.kiem_tep`, `doc_toan_van_co_nguoi.la_html_toan_van`) truyền nguyên văn
  HTML; chữ thô không thẻ giữ luật cũ (tương thích ngược). `verify_dashboard._la_toan_van_kho` chép cùng thuật toán, hai bản
  trong git trùng byte.
- Doctrine `_CONNECTOR-CHUNG-CU.md` §2septies mục 8 (điều kiện 3) dạy agent: trang hiện đề mục tường phí mà thân bài không có
  cấu trúc toàn văn ⇒ bác sĩ chưa có quyền — đừng lưu, xếp «BÁC SĨ ĐỌC TRỰC TIẾP», không cắt đề mục khỏi tệp. Bản cặp ở repo y
  khoa (BH107) qua PR riêng.

## Số đo sau vá (15/10/2026, chỉ đọc kho `EBM-Dashboards/toan_van_oa/`)

- 303 tệp `PMID-*.html`: **0 tệp True→False** (tệp lọt duy nhất đã ở Thùng rác; cổng mới trả `False — tường phí — đề mục
  «Access options», thân bài không có cấu trúc toàn văn (575 từ, 0 mục; bỏ 7 khối hậu bài)`); **5 tệp False→True**, đều là toàn
  văn thật soi theo cấu trúc đề mục: 16129869 (CMAJ), 41294344, 30366684, 34610473, 38864796.
- `tools/so_toan_van.py`: nợ toàn văn apply 9 → 8 (hết nợ ITEM-05 PMID 16129869), không nợ mới.
- Hai bản cổng (gom · verify_dashboard) cùng kết luận trên 304 tệp (303 + tệp trong Thùng rác).

## Kiểm hồi quy

- `tools/test_cong_toan_van_tuong_phi_20261015.py` — 15 fixture tổng hợp, mỗi fixture cô lập MỘT lớp phòng thủ; cả hai bản cổng;
  phiên Chrome và tầng Unpaywall từ chối trang tường phí; `bao_phu_cuc_bo` + `co_toan_van_trong_kho`; chốt khớp LỜI GỌI
  (không khớp chuỗi nhắc tên hàm) cho nơi gọi.
- Kiểm đột biến 14/14 đỏ đúng chỗ rồi phục hồi xanh (`python -B`, xoá `__pycache__` mỗi phép): bỏ cắt References · bỏ dấu Access
  options · đảo thứ tự kiểm · bỏ Interpretation · bỏ Background · bỏ loại trừ tiểu mục tóm tắt · án tường phí tuyệt đối · bỏ luật
  bài không IMRaD · bỏ luật IMRaD ngắn · ba nơi gọi truyền chữ thô (phiên Chrome · `bao_phu_cuc_bo` · tầng Unpaywall qua biến
  trung gian — test hành vi mạng giả) · hai đột biến trên bản BH161.
- Chốt BH164 trong `tools/chot_hoi_quy_bai_hoc.py` (đỏ với 4 đột biến: bỏ cắt References · đảo thứ tự · bỏ Interpretation · nơi
  gọi truyền chữ thô).

## Giới hạn còn lại

- Cổng dựa vào THẺ đề mục: trang dùng `<b>`/`<div class="title">` thay h1–h6 thì không đọc được cấu trúc — rơi về luật chữ cũ
  trên thân bài (không bao giờ dễ hơn trước). Danh mục tham khảo không có đề mục nhận ra được (vd tiếng nước ngoài) không bị cắt.
- Bài toàn văn rất ngắn (< 1 500 từ thân bài, vd research letter) vẫn bị coi «chưa phải toàn văn» (fail-closed).
- Hai bản chạy NGOÀI git (`EBM-Dashboards/tools/verify_dashboard.py`, `EBM_MASTER/skill_assets/verify_dashboard.py`) chỉ nhận luật
  mới khi chép từ nguồn sau khi PR được gộp.
