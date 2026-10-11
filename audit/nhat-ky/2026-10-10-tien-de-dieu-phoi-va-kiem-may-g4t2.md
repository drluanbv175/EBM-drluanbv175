# 10/10/2026 — «Tiền đề» §2 của điều phối lệch tiêu chí bộ chấm · G4-T2 (SAP RCT §13–§15) không có kiểm máy

Bác sĩ giao: «Tiếp tục hoàn thiện từng Agent và từng điều phối» (vòng sau drluanbv175/medical-ebm-automation#102 ·
drluanbv175/EBM-drluanbv175#143).

## Đo (10/10)

- **Từng agent:** mã tiêu chí `GN-AUTO/HUMAN-…` nhắc trong mọi tài liệu agent đều có trong bộ chấm (0 lệch); tên tệp hồ
  sơ `GN_…` nhắc trong tài liệu đều có nơi sinh (0 lệch).
- **Từng điều phối:** văn xuôi mục «2. Tiền đề» lệch tiêu chí tiền đề bộ chấm THẬT kiểm (đối chiếu mã nguồn):
  G3 ghi «G1» nhưng G3-AUTO-01 kiểm G0 và G1; G8 không nhắc G2 dù G8-AUTO-11 đối chiếu thiết kế G1 ↔ G2; G9 không nhắc
  G2 dù G9-AUTO-03 đòi G2 đã duyệt; G2 ghi «G0, G1 (G2-AUTO-02)» nhưng G2-AUTO-02 chỉ chấm sống G1. (G6 ghi G5 — đúng:
  G6-AUTO-06/08 kiểm khoá dữ liệu G5 khi đã phân tích dữ liệu thật.)
- **Từng cổng:** G4-T2 (`an-toan-nghien-cuu`, RCT — SAP §13 giữa kỳ/quy tắc dừng · §14 DMC · §15 tổn hại) không gắn tiêu
  chí máy nào dù bước ký G4 (`approve_gate._g4_sections_still_draft`) đã kiểm đúng ba mục này.

## Vá

Repo y khoa (drluanbv175/medical-ebm-automation#103, xếp chồng trên #102):
- `hoi_dong_cong.KIEM_NHIEM_VU["G4-T2"]` — gọi ĐÚNG `approve_gate._g4_sections_still_draft(…, "rct")`, chỉ lấy §13–§15
  (§1–§12 là của G4-T1/G4-AUTO-10). Kiểm máy cấp nhiệm vụ nay CHỈ chạy khi nhiệm vụ CHẮC áp dụng (`ap_dung is True`) —
  thiết kế chưa suy được thì không kiểm theo giả định.
- `tools/sinh_tai_lieu_trach_nhiem.py` sinh thêm khối «tiêu chí tiền đề bộ chấm kiểm» trong §2 của 11 điều phối (giữa dấu
  mốc `TIEN-DE-CONG`, trước dòng lệnh chấm sống) từ `PHAN_CONG`.

Repo gốc (PR này): sửa 4 mệnh đề §2 (G2, G3, G8, G9) theo mã; khối tiền đề sinh cho 11 điều phối; khối trách nhiệm
`an-toan-nghien-cuu` ghi chú kiểm máy G4-T2; `_HOI-DONG-CONG.md` §1b mục 7.

Còn 6 nhiệm vụ chưa có tệp hợp đồng riêng nên chưa kiểm máy được (chất lượng chỉ bảo đảm bằng đánh giá chéo): G1-T4 công
cụ đo lường, G1-T5 an toàn trong thiết kế RCT, G6-T2 phân tích gộp, G6-T3 diễn giải (đầu ra đi vào Bàn luận G7), G7-T2
hiệu đính song ngữ, G10-T3 sổ cái/bộ nhớ.

## Kiểm

`tests/test_g4t2_tien_de_dieu_phoi_20261010.py`: 20 ca. Đột biến **6/6** bị bắt, CÓ lượt nền xanh (không lọc §13–§15 · kiểm
G4-T2 luôn rỗng · kiểm khi chưa chắc áp dụng · chèn tiền đề sai chỗ · chỉ liệt kê tiêu chí tiền đề đầu · bỏ G4-T2 khỏi
kiểm máy). Hai test của đợt trước cập nhật theo kiểm G4-T2 (đồ gá SAP «SAP» trơn ⇒ SAP đủ §1–§15; tập kiểm máy «⊇»).

**Bài học quy trình:** lượt đột biến đầu báo «5/5» nhưng KHÔNG có lượt nền xanh — hai test đỏ sẵn (do kiểm G4-T2 mới) làm
mọi đột biến trông như bị bắt; chạy lại có nền xanh thì E4 «chèn tiền đề sai chỗ» LỌT (đồ gá chỉ kiểm vị trí trên tài
liệu đã có dấu mốc) ⇒ thêm khẳng định vị trí cho lần chèn đầu. Thông điệp commit đầu ghi «bộ đầy đủ qua» trước khi đọc
kết quả (thực tế 2 đỏ) — sửa trước khi đẩy.
