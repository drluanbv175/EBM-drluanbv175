# 10/10/2026 — G6-T2 (phân tích gộp) không chịu tiêu chí nào dù G6-AUTO-09 có họ «meta» · không sửa G6-AUTO-09 sang «dòng thi hành»

Cùng lượt «Gộp và tiếp tục hoàn thiện» với `2026-10-10-g1t5-an-toan-thiet-ke.md`.

## Đo (10/10)

- G6-T2 (`meta-phan-tich`, chỉ khi tổng quan hệ thống có gộp định lượng) không gắn tiêu chí máy nào.
- G6-AUTO-09 (mô hình phân tích chính trong script ↔ SAP §4) có sẵn họ «meta» (SAP: «meta-analysis/random-effects/
  REML»; script: `metabin(`/`metagen(`/`rma(`) và khuôn SR/MA của `run_g6_auto._r03_srma_template` sinh đúng họ đó —
  nhưng `PHAN_CONG` giao cố định cho G6-T1 `phan-tich-thong-ke`. Với SR/MA, script gộp là sản phẩm của `meta-phan-tich`.
- **Đã cân nhắc và KHÔNG sửa:** G6-AUTO-09 khớp regex trên cả tệp, kể cả dòng chú thích (trái tinh thần §0.8 «khớp dòng
  thi hành»). Đo 11 khuôn script phân tích chính của bộ sinh G6 (`make_r03_cohort` + `_r03_*`: cohort, RCT, nhị phân
  RR/OR, MD, case-control, cắt ngang, thứ bậc, chẩn đoán, dự báo, SR/MA): CẢ 11 để lời gọi mô hình ở dòng chú thích có
  chủ ý — script chỉ chạy khi có dữ liệu khoá; khuôn định tính chỉ khớp qua một dòng `message(…)`, không phải mô
  hình. G6-AUTO-09 đang đối chiếu «phương pháp đã chuẩn bị» với SAP. Đổi sang chỉ dòng thi hành sẽ làm mọi khuôn vừa
  sinh «không nhận ra mô hình» ⇒ đổi ngữ nghĩa cổng cho mọi thiết kế — là quyết định thiết kế cổng, không phải vá
  lỗi; để nguyên.

## Vá

Repo y khoa (cùng PR với G1-T5): `PHAN_CONG["G6"]["G6-AUTO-09"] = "G6-T2|G6-T1"` (khuôn ô có điều kiện của
G2-AUTO-07): `sr_ma` ⇒ `meta-phan-tich`; thiết kế khác/chưa suy được ⇒ `phan-tich-thong-ke`.

Repo gốc: `meta-phan-tich.md` §6 dạy tiêu chí G6-AUTO-09 của mình; khối trách nhiệm 3 agent sinh lại (dieu-phoi-g6,
meta-phan-tich, phan-tich-thong-ke); `_HOI-DONG-CONG.md` §1b mục 7 nêu hai ô có điều kiện theo thiết kế.

## Kiểm

`tests/test_g6t2_mo_hinh_gop_20261010.py`: 9 ca (chủ theo thiết kế sr_ma/cohort/rct/chưa rõ; G6-T2 ra khỏi danh sách
«không tiêu chí»; neo khuôn SR/MA ↔ họ «meta»; bảng trách nhiệm giao đúng agent; tài liệu hai agent nêu đúng vai).
Đột biến **4/4** bị bắt, CÓ lượt nền xanh (về G6-T1 cố định · đảo thứ tự lựa chọn · điều kiện SR/MA trỏ sai thiết kế ·
bộ sinh đổi nhãn).

Còn chưa có hợp đồng/kiểm máy: G6-T3 (diễn giải → Bàn luận G7), G10-T3 (sổ cái/bộ nhớ — sổ trạng thái hiện nằm trong
tệp doctrine dùng chung `_SO-TRANG-THAI-CHECKPOINT.md`, chưa có tệp riêng theo đề tài; đặt hợp đồng ở đâu cần bác sĩ
quyết).
