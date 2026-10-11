# 10/10/2026 — G1-T5 (an toàn người tham gia trong thiết kế RCT) không có kiểm máy · ô trống an toàn của đề cương lõi quy hết cho agent thiết kế

Bác sĩ giao: «Gộp và tiếp tục hoàn thiện». Đã gộp y khoa #103 (f403892); y khoa #105 + gốc #145 chờ CI.

## Đo (10/10)

- G1-T5 (`an-toan-nghien-cuu`, chỉ RCT) khai đầu ra là đề cương chung `G1_A2_PROTOCOL_DESIGN_<mã>.md` và không gắn
  tiêu chí máy nào.
- Đề cương lõi (PHẦN 0 của A2, sinh bằng `g1_quality_gate.build_protocol_core`) có hai dòng an toàn người tham gia
  thuộc phạm vi G1: «Cân bằng lợi ích, nguy cơ và tính hợp lý khoa học» (`gate_params.G1.benefit_risk_rationale`) và
  «Tiêu chí dừng/chuyển/điều trị cứu hộ nếu áp dụng» (`stopping_rescue_rules`). G1-AUTO-07 đếm mọi ô trống của PHẦN 0
  nhưng `PHAN_CONG` gán G1-AUTO-07 cho G1-T1 (`thiet-ke-nghien-cuu`) ⇒ phần nội dung an toàn không ai trong hội đồng
  chịu riêng; tài liệu `an-toan-nghien-cuu` chỉ dạy 5 tài liệu an toàn của G2/G6, không nhắc G1.
- AE/SAE, DMC và quy tắc dừng cấp thử nghiệm hoãn có chủ ý cho G2 (G2-T2, G2-AUTO-07) và G4 (G4-T2, SAP §13–§15).

## Vá

Repo y khoa (PR xếp chồng trên drluanbv175/medical-ebm-automation#105):
- `hoi_dong_cong.KIEM_NHIEM_VU["G1-T5"]` — hai dòng an toàn có mặt trong PHẦN 0 và đã điền, đếm bằng ĐÚNG
  `g1_quality_gate.o_trong_pham_vi_g1` (bộ đếm của G1-AUTO-07); «N/A — <lý do>» hợp lệ như bộ chấm; chỉ chạy khi thiết
  kế chắc là RCT. G1-AUTO-07 vẫn của G1-T1 — kiểm này chỉ chỉ ra phần nội dung an toàn của `an-toan-nghien-cuu`.

Repo gốc (PR này): `an-toan-nghien-cuu.md` dạy vai G1 (soạn hai khoá `gate_params.G1`, đưa PI duyệt, chạy lại G1,
không sửa tay A2); `dieu-phoi-g1.md` §3 hàng G1-T5; khối trách nhiệm sinh lại; `_HOI-DONG-CONG.md` §1b mục 7.

## Kiểm

- `tests/test_g1t5_an_toan_thiet_ke_20261010.py`: 12 ca (nhãn chép đúng khuôn sinh thật, hai dòng điền/trống, N/A có
  lý do, ô trống khác không quy cho G1-T5, khuôn cũ thiếu dòng, nhãn nằm ngoài PHẦN 0 không tính, bảng trách nhiệm
  chỉ kiểm khi chắc RCT).
- Đột biến **7/7** bị bắt, CÓ lượt nền xanh (nhãn lệch khuôn · không lọc dòng an toàn · bỏ kiểm thiếu dòng · vùng = cả
  tài liệu · bỏ G1-T5 khỏi kiểm máy · bỏ qua ô trống · chỉ kiểm dòng đầu).
- Đo C1a (chỉ đọc, SHA-256 trước = sau): cắt ngang ⇒ G1-T5 không áp dụng, không kiểm.

Còn chưa có hợp đồng/kiểm máy: G6-T2 (gộp — SR/MA), G6-T3 (diễn giải → Bàn luận G7), G10-T3 (sổ cái/bộ nhớ).
