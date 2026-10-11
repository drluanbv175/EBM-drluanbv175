# 10/10/2026 — G1-T4 (công cụ đo lường) không bao giờ bị đòi sản phẩm · nhiệm vụ có điều kiện «khai ở khối bàn giao» không máy nào đọc lại

Bác sĩ giao: «Gộp và Tiếp tục hoàn thiện từng Agent và từng điều phối». Đã gộp gốc #143 #144 · y khoa #102; y khoa #103
chờ CI Windows.

## Đo (10/10)

- Nhiệm vụ còn chưa có hợp đồng/kiểm máy (sau đợt G3-T2/T3, G4-T2): G1-T4, G1-T5, G6-T2, G6-T3, G7-T2, G10-T3.
- **G1-T4** (`cong-cu-do-luong`) khai đầu ra là đề cương chung `G1_A2_PROTOCOL_DESIGN_<mã>.md` ⇒ «có đầu ra» chỉ vì đề
  cương tồn tại; sản phẩm thật của pha phát triển bộ câu hỏi (phiếu chấm CVI + nhật ký phỏng vấn nhận thức của
  `tools/pha_phat_trien_cong_cu.py mau`, có từ 28/09) không ai đòi. C1a: bộ câu hỏi tự xây, đề cương khoá pha I-CVI
  (mục 4.5.1), thư mục `pha_cong_cu/` chưa có.
- Điều kiện của G1-T4 («khi đề tài dùng thang đo/bộ câu hỏi») và G7-T2 («nộp tạp chí tiếng Anh») máy không suy được từ
  thiết kế ⇒ nhiệm vụ mãi `nhiem_vu_chua_xac_dinh`. Quy tắc 5 mục 4b chỉ dặn điều phối «khai ở khối bàn giao» — không
  máy nào đọc lại, nên đầu ra của hai nhiệm vụ này KHÔNG BAO GIỜ bị đòi.
- Điều kiện cũ của G1-T4 lệch tài liệu agent: `cong-cu-do-luong` §Phạm vi áp dụng tách hai nhánh — thang chuẩn dùng
  NGUYÊN TRẠNG (không pha CVI) và phát triển/sửa đổi/dịch (đủ COSMIN, có CVI + phỏng vấn nhận thức). Đòi phiếu CVI cho
  mọi đề tài «dùng thang đo» sẽ ép dựng phiếu rỗng cho thang chuẩn.
- Lỗi chữ «khi khi đề tài…» ở `dieu-phoi-g1.md` §3 và khối trách nhiệm sinh của `cong-cu-do-luong`.

## Vá

Repo y khoa (PR xếp chồng trên drluanbv175/medical-ebm-automation#103):
- `hoi_dong_cong.py`: G1-T4 = «Phát triển/thích nghi & kiểm định công cụ đo lường (COSMIN)», điều kiện «khi đề tài phát
  triển, sửa đổi hoặc dịch–thích nghi bộ câu hỏi/thang đo»; đầu ra hợp đồng thêm `pha_cong_cu/phieu_cvi.csv` +
  `pha_cong_cu/nhat_ky_phong_van_nhan_thuc.csv`; `KIEM_NHIEM_VU["G1-T4"]` kiểm bằng ĐÚNG `pha_phat_trien_cong_cu`
  (phiếu CVI đúng cấu trúc, mục không trùng, điểm 1–4, ≥ 3 chuyên gia — Polit, Beck & Owen 2007, PMID 17654487; nhật ký
  đủ cột). Ô chưa chấm / I-CVI thấp KHÔNG là lỗi agent (việc hội đồng chuyên gia/chủ nhiệm).
- Lệnh mới `khai-ap-dung --study --gate --nhiem-vu --ap-dung co|khong --ly-do` ⇒ `hoi_dong/<GN>/ap_dung_nhiem_vu.json`
  (từ chối nhiệm vụ không điều kiện, điều kiện thiết kế RCT/SR — máy quyết, lý do < 10 ký tự, PII; đề tài không tồn tại
  ⇒ mã 2, không tạo thư mục). `trach_nhiem` dùng khai báo: «co» ⇒ đòi đầu ra + kiểm máy; «khong» ⇒ bỏ; điều kiện thiết
  kế không bị khai tay đè.
- Bộ sinh tài liệu: quy tắc 5 mục 4b của 11 điều phối dạy lệnh `khai-ap-dung` + liệt kê nhiệm vụ cần khai của cổng;
  bỏ «khi khi». Test 4b chỉ đọc HÀNG BẢNG (dòng văn xuôi có «|» trong mã lệnh từng làm test đọc nhầm thành phân công).

Repo gốc (PR này): `dieu-phoi-g1.md` §3 hàng G1-T4; `cong-cu-do-luong.md` hợp đồng đầu ra G1-T4 (thang nguyên trạng ⇒
báo điều phối khai «khong», KHÔNG dựng phiếu rỗng); 11 điều phối quy tắc 5 sinh lại; `_HOI-DONG-CONG.md` §1b mục 9.

## Kiểm

- `tests/test_g1t4_khai_ap_dung_20261010.py`: 19 ca. Đột biến **14/14** bị bắt, CÓ lượt nền xanh (ngưỡng 3→2 · bỏ kiểm
  cột nhật ký · `_ap_dung` bỏ qua khai · khai thắng điều kiện thiết kế · cho khai điều kiện thiết kế · bỏ quét PII · lý
  do ngắn · G1-T4 chỉ khai đề cương · bỏ G1-T4 khỏi kiểm máy · bảng không đọc khai · CLI khai sai mã 0 · in bảng bỏ dòng
  đã khai · bộ sinh bỏ «Ở GN» · nhận nhiệm vụ không điều kiện). M11 lượt đầu «không áp được» (mốc khớp 2 chỗ) ⇒ chạy
  lại với mốc riêng.
- Đo C1a (chỉ đọc, SHA-256 trước = sau): G1 `AGENT_CON_VIEC` (G1-AUTO-07 `thiet-ke-nghien-cuu`), G1-T4 «chưa xác
  định» — chờ `dieu-phoi-g1` khai (đề cương khoá pha I-CVI ⇒ nhiều khả năng «co»; agent KHÔNG tự khai thay điều phối
  trong lượt sửa hệ này).

Còn chưa có hợp đồng/kiểm máy: G1-T5 (an toàn trong thiết kế RCT — nằm trong đề cương chung), G6-T2 (gộp), G6-T3 (diễn
giải → Bàn luận G7), G7-T2 (hiệu đính — nay ít nhất được khai), G10-T3 (sổ cái/bộ nhớ).
