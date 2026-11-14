# Độ nhạy kiểm chéo ngữ nghĩa K1–K4 — đột biến tổng hợp (14/11/2026, lượt c)

> **Đột biến TỔNG HỢP có nhãn theo cấu trúc — KHÔNG thay bộ vàng do bác sĩ gắn nhãn.** Công cụ không đổi chế độ chặn; chuyển K1–K4 từ CẢNH BÁO sang CHẶN là quyết định của bác sĩ (audit/16 §4). Báo động trên đối chứng là CẬN TRÊN của báo động giả: mục thật chưa được gắn nhãn đúng/sai.

Sinh bởi `tools/do_nhay_kiem_ngu_nghia.py` · hạt giống 20261114 · băm mã (16 ký tự đầu): `kiem_cheo_ngu_nghia.py` 928b79ff754c3348, `kiem_quan_the_chieu.py` 09dbc9114a7e95e1, `do_nhay_kiem_ngu_nghia.py` 7815459a11fbe7a9.

## Tóm tắt

- Độ nhạy trong phạm vi thiết kế: K1 99% (n=187; riêng phần trong từ điển bộ kiểm 99% [KTC 97%–100%; 186/187]) · K2 98% (n=171) · K3 62% (n=604; riêng phần trong từ điển bộ kiểm 84% [KTC 80%–87%; 372/442]) · K3b 1% (n=604; riêng phần phép phán được 27% [KTC 14%–46%; 7/26]) · K4 99% (n=107) · K4b 25% (n=581; riêng phần phép phán được 56% [KTC 50%–62%; 145/258]).
- Số gộp tính cả cách viết/dấu điều kiện mà bộ sinh CỐ Ý chọn ngoài từ điển bộ kiểm (đo lỗ hổng từ vựng); «riêng phần trong từ điển» = K1 với cách viết bộ kiểm nhận được, K3 với nhóm dấu có trong từ điển K3 (`dau_k3`) — phần còn lọt ở đó là lỗ hổng CƠ CHẾ, không phải từ vựng; với K3b/K4b là phần đột biến mà phép PHÁN ĐƯỢC trên nguồn đó (K3b: nguồn có câu khuyến cáo có điều kiện neo được vào hành động; K4b: nguồn có câu ủng hộ hoặc chống rõ ràng).
- Lớp lỗi NGOÀI phạm vi thiết kế (không phép nào được thiết kế để bắt): K2 · đổi ngưỡng số nằm trong HÀNH ĐỘNG 0/40.
- Đối chứng mức dashboard — nếu chuyển sang CHẶN: K1/K2/K4 chặn 45/97 dashboard đã PASS, K3b/K4b chặn 4/97, K3 chặn 102/115.

## Dữ liệu

- Dashboard ĐÃ PASS (bản mới nhất mỗi chủ đề): 115 (đọc được DATA: 115).
- Mục `apply` sau khử trùng: 826 · có tóm tắt PubMed để K1/K2/K4 đọc: 663.
- Tóm tắt: cần 298 PMID · có sẵn trong bộ đệm 298 · tải mới 0 · tải hỏng 0.
- Bộ sinh phủ được (mục đủ điều kiện tiên quyết / mục đã thử): K1_quan_the 187/663 · K2_co_mau 95/663 · K2_nguong 76/663 · K2_nguong_hanh_dong 40/663 · K3 604/826 · K4_muc_dao 581/581 · K4_nguon_nguoc 107/581.

## 1. Độ nhạy theo phép (chỉ đột biến TRONG phạm vi thiết kế của phép)

| Phép | n đột biến | Bắt đúng chỗ | Độ nhạy (KTC 95% Wilson) | Riêng phần trong từ điển bộ kiểm — K3b/K4b: phần phép phán được (KTC 95%; bắt/n) | Kể cả 🟠 lệch chỗ | Lọt ✓ (trấn an sai) | Lọt ⚪ | Lọt im |
|---|---|---|---|---|---|---|---|---|
| K1 | 187 | 186 | 99% (97%–100%) | 99% (97%–100%; 186/187) | 99% (97%–100%) | 0 | 0 | 1 |
| K2 | 171 | 168 | 98% (95%–99%) | — | 98% (95%–99%) | 0 | 3 | 0 |
| K3 | 604 | 374 | 62% (58%–66%) | 84% (80%–87%; 372/442) | 62% (58%–66%) | 114 | 0 | 116 |
| K3b | 604 | 7 | 1% (1%–2%) | 27% (14%–46%; 7/26) | 1% (1%–2%) | 17 | 134 | 446 |
| K4 | 107 | 106 | 99% (95%–100%) | — | 99% (95%–100%) | 1 | 0 | 0 |
| K4b | 581 | 145 | 25% (22%–29%) | 56% (50%–62%; 145/258) | 25% (22%–29%) | 113 | 320 | 3 |

## 2. Theo lớp đột biến

| Lớp | Phạm vi thiết kế | n | Bắt | Độ nhạy (KTC 95%) | Lọt ✓ | Lọt ⚪ | Lọt im |
|---|---|---|---|---|---|---|---|
| K1 · đổi nhãn quần thể (thay/chèn vế loại trừ) | trong | 187 | 186 | 99% (97%–100%) | 0 | 0 | 1 |
| K2 · đổi/chèn cỡ mẫu n= | trong | 95 | 92 | 97% (91%–99%) | 0 | 3 | 0 |
| K2 · đổi ngưỡng số trong quần thể (EF/eGFR/tuổi/HbA1c/BMI/LDL) | trong | 76 | 76 | 100% (95%–100%) | 0 | 0 | 0 |
| K2 · đổi ngưỡng số nằm trong HÀNH ĐỘNG | **ngoài** | 40 | 0 | 0% (0%–9%) | 0 | 0 | 40 |
| K3 · rụng điều kiện ở BẢN XUẤT (mục giữ nguyên) | trong | 604 | 374 | 62% (58%–66%) | 114 | 0 | 116 |
| K3 · rụng điều kiện NGAY TRONG MỤC so với nguồn | trong | 604 | 7 | 1% (1%–2%) | 17 | 134 | 446 |
| K4 · MỤC đảo sang «không làm» khi nguồn ủng hộ | trong | 581 | 145 | 25% (22%–29%) | 113 | 320 | 3 |
| K4 · nguồn nói NGƯỢC chiều mục apply | trong | 107 | 106 | 99% (95%–100%) | 1 | 0 | 0 |

Lớp **ngoài phạm vi thiết kế** đo lỗ hổng — không tính vào độ nhạy của phép ở bảng 1:
- K2 · đổi ngưỡng số nằm trong HÀNH ĐỘNG: K1/K2 chỉ đọc population/pico.P/title — không đọc action.

**K3 — phân tích thêm (rụng ở bản xuất):**
- Bắt theo nhóm dấu điều kiện của bộ sinh: dau_k3 372/442 (84%; KTC 80%–87%), dau_khac 2/98 (2%; KTC 1%–7%), nguong_so 0/64 (0%; KTC 0%–6%) (`dau_k3` = dấu có trong từ điển K3; `dau_khac` = giới hạn quần thể/điều kiện ngoài từ điển; `nguong_so` = ngưỡng số đứng trần, không có «nếu/khi»).
- 230 lần lọt, quy theo cụm mà K3 THỰC trích từ hành động (không theo cụm của bộ sinh): 116 lần K3 không trích được cụm nào · 85 lần mọi cụm K3 trích vẫn nguyên trong hành động đã cắt (phần bị cắt nằm ngoài cụm của K3) · 29 lần cụm K3 bị cắt khỏi hành động nhưng còn ở chỗ khác trong phạm vi K3 so (từ 14/11/2026c: đoạn của chính mục khi bản xuất in «ITEM-xx. <tiêu đề>»; cả tài liệu khi không định vị được).
- Cận trên nếu cả phần «còn ở chỗ khác» cũng được quy đúng mục (bắt + phần đó, trên cùng n = 604): 67% (63%–70%). Lỗ hổng trích cụm/từ vựng (201/230 lần lọt) lớn hơn lỗ hổng so khớp cấp tài liệu (29/230).
- 0 đột biến có hành động hiển thị ≥ 2 lần nguyên văn trong Word; nếu chỉ MỘT chỗ mất cụm thì K3 bắt 0/0.

**K1 — tách từ vựng khỏi cơ chế:**
- Cách viết bộ kiểm NHẬN được (hỏi thẳng `kiem_cap` thật): 99% (97%–100%; 186/187) · cách viết NGOÀI từ điển: CHƯA ĐO (—; 0/0).

**Lý do lọt (trong phạm vi thiết kế):**

| Lớp | Lý do | Số lần |
|---|---|---|
| K1_quan_the | cách viết tiếng Việt của nhãn không có trong từ điển bộ kiểm | 1 |
| K2_co_mau | nguồn không nêu ⇒ ⚪ | 3 |
| K3_rung_ban_xuat | K3 không trích được cụm điều kiện nào từ hành động | 116 |
| K3_rung_ban_xuat | mọi cụm K3 trích được vẫn nguyên trong hành động đã cắt (phần bị cắt nằm ngoài cụm của K3) | 85 |
| K3_rung_ban_xuat | cụm K3 trích được bị cắt khỏi hành động nhưng còn ở chỗ khác trong phạm vi K3 so (đoạn của mục; không định vị được mục thì cả tài liệu) ⇒ K3 vẫn thấy | 29 |
| K3_rung_trong_muc | nguồn không có câu khuyến cáo CÓ ĐIỀU KIỆN chung thuật ngữ với hành động ⇒ K3b im | 446 |
| K3_rung_trong_muc | mục không có tóm tắt nguồn ⇒ K3b không phán được (⚪) | 134 |
| K3_rung_trong_muc | hành động đã cắt vẫn còn dấu điều kiện khác (K3b chỉ biết «còn/không còn điều kiện») hoặc mục còn nhắc chỉ số của ngưỡng | 17 |
| K4_muc_dao | nguồn không có câu ủng hộ rõ (thường gặp: tóm tắt guideline chỉ mô tả phạm vi) ⇒ ⚪ | 320 |
| K4_muc_dao | phần Kết luận/tiêu đề nguồn có câu chống/hại (rộng có chủ ý) ⇒ K4b coi là cùng chiều | 113 |
| K4_muc_dao | mục đảo không được nhận là khuyến cáo «KHÔNG làm» thật | 3 |
| K4_nguon_nguoc | câu đã đảo bị bộ lọc «kết cục phụ» bỏ qua (vd «secondary analysis», «secondary prevention») | 1 |

## 3. Theo biến thể (dạng bề mặt) — lỗ hổng từ vựng

| Lớp | Biến thể | n | Bắt | Độ nhạy (KTC 95%) | Lọt |
|---|---|---|---|---|---|
| K1_quan_the | `chen_nhan:HFrEF` | 1 | 1 | 100% (21%–100%) | 0 |
| K1_quan_the | `chen_nhan:bệnh nhi` | 15 | 15 | 100% (80%–100%) | 0 |
| K1_quan_the | `chen_nhan:ngoài thai kỳ` | 9 | 9 | 100% (70%–100%) | 0 |
| K1_quan_the | `chen_nhan:người lớn` | 2 | 2 | 100% (34%–100%) | 0 |
| K1_quan_the | `chen_nhan:người trưởng thành` | 6 | 5 | 83% (44%–97%) | 1 |
| K1_quan_the | `chen_nhan:nhi khoa` | 14 | 14 | 100% (78%–100%) | 0 |
| K1_quan_the | `chen_nhan:phụ nữ không mang thai` | 12 | 12 | 100% (76%–100%) | 0 |
| K1_quan_the | `chen_nhan:suy tim PSTM giảm` | 1 | 1 | 100% (21%–100%) | 0 |
| K1_quan_the | `chen_nhan:suy tim phân suất tống máu còn bảo tồn` | 1 | 1 | 100% (21%–100%) | 0 |
| K1_quan_the | `chen_nhan:trẻ em` | 14 | 14 | 100% (78%–100%) | 0 |
| K1_quan_the | `chen_nhan:trẻ vị thành niên` | 15 | 15 | 100% (80%–100%) | 0 |
| K1_quan_the | `chen_nhan:ĐTĐ típ 2` | 1 | 1 | 100% (21%–100%) | 0 |
| K1_quan_the | `chen_nhan:ĐTĐ1` | 3 | 3 | 100% (44%–100%) | 0 |
| K1_quan_the | `chen_nhan:đái tháo đường type 1` | 2 | 2 | 100% (34%–100%) | 0 |
| K1_quan_the | `thay_nhan:HFpEF` | 3 | 3 | 100% (44%–100%) | 0 |
| K1_quan_the | `thay_nhan:bệnh nhi` | 19 | 19 | 100% (83%–100%) | 0 |
| K1_quan_the | `thay_nhan:chưa lọc máu` | 1 | 1 | 100% (21%–100%) | 0 |
| K1_quan_the | `thay_nhan:ngoài thai kỳ` | 3 | 3 | 100% (44%–100%) | 0 |
| K1_quan_the | `thay_nhan:nhi khoa` | 14 | 14 | 100% (78%–100%) | 0 |
| K1_quan_the | `thay_nhan:phụ nữ không mang thai` | 4 | 4 | 100% (51%–100%) | 0 |
| K1_quan_the | `thay_nhan:suy tim EF bảo tồn` | 1 | 1 | 100% (21%–100%) | 0 |
| K1_quan_the | `thay_nhan:suy tim PSTM giảm` | 2 | 2 | 100% (34%–100%) | 0 |
| K1_quan_the | `thay_nhan:suy tim phân suất tống máu bảo tồn` | 3 | 3 | 100% (44%–100%) | 0 |
| K1_quan_the | `thay_nhan:suy tim phân suất tống máu còn bảo tồn` | 1 | 1 | 100% (21%–100%) | 0 |
| K1_quan_the | `thay_nhan:suy tim phân suất tống máu giảm` | 1 | 1 | 100% (21%–100%) | 0 |
| K1_quan_the | `thay_nhan:trẻ em` | 14 | 14 | 100% (78%–100%) | 0 |
| K1_quan_the | `thay_nhan:trẻ vị thành niên` | 21 | 21 | 100% (85%–100%) | 0 |
| K1_quan_the | `thay_nhan:ĐTĐ tuýp 1` | 2 | 2 | 100% (34%–100%) | 0 |
| K1_quan_the | `thay_nhan:ĐTĐ típ 1` | 1 | 1 | 100% (21%–100%) | 0 |
| K1_quan_the | `thay_nhan:đái tháo đường type 1` | 1 | 1 | 100% (21%–100%) | 0 |
| K2_co_mau | `chen_n:N={:,}` | 10 | 10 | 100% (72%–100%) | 0 |
| K2_co_mau | `chen_n:n = {:,}` | 16 | 16 | 100% (81%–100%) | 0 |
| K2_co_mau | `chen_n:n={:,}` | 17 | 16 | 94% (73%–99%) | 1 |
| K2_co_mau | `chen_n:n={:d}` | 16 | 16 | 100% (81%–100%) | 0 |
| K2_co_mau | `thay_n` | 36 | 34 | 94% (82%–98%) | 2 |
| K2_nguong | `bmi:chi_truoc` | 1 | 1 | 100% (21%–100%) | 0 |
| K2_nguong | `ef:chi_truoc` | 12 | 12 | 100% (76%–100%) | 0 |
| K2_nguong | `egfr:chi_truoc` | 8 | 8 | 100% (68%–100%) | 0 |
| K2_nguong | `tuoi:chi_truoc` | 1 | 1 | 100% (21%–100%) | 0 |
| K2_nguong | `tuoi:so_truoc` | 54 | 54 | 100% (93%–100%) | 0 |
| K2_nguong_hanh_dong | `bmi:chi_truoc` | 1 | 0 | 0% (0%–79%) | 1 |
| K2_nguong_hanh_dong | `ef:chi_truoc` | 2 | 0 | 0% (0%–66%) | 2 |
| K2_nguong_hanh_dong | `egfr:chi_truoc` | 3 | 0 | 0% (0%–56%) | 3 |
| K2_nguong_hanh_dong | `ldl:chi_truoc` | 1 | 0 | 0% (0%–79%) | 1 |
| K2_nguong_hanh_dong | `tuoi:chi_truoc` | 1 | 0 | 0% (0%–79%) | 1 |
| K2_nguong_hanh_dong | `tuoi:so_truoc` | 32 | 0 | 0% (0%–11%) | 32 |
| K3_rung_ban_xuat | `ban_xuat_that|dau_k3:chỉ khi` | 11 | 11 | 100% (74%–100%) | 0 |
| K3_rung_ban_xuat | `ban_xuat_that|dau_k3:chống chỉ định` | 7 | 5 | 71% (36%–92%) | 2 |
| K3_rung_ban_xuat | `ban_xuat_that|dau_k3:khi` | 239 | 199 | 83% (78%–87%) | 40 |
| K3_rung_ban_xuat | `ban_xuat_that|dau_k3:không dùng cho` | 1 | 1 | 100% (21%–100%) | 0 |
| K3_rung_ban_xuat | `ban_xuat_that|dau_k3:không dùng khi` | 2 | 2 | 100% (34%–100%) | 0 |
| K3_rung_ban_xuat | `ban_xuat_that|dau_k3:ngoài thai kỳ` | 1 | 1 | 100% (21%–100%) | 0 |
| K3_rung_ban_xuat | `ban_xuat_that|dau_k3:nếu` | 107 | 90 | 84% (76%–90%) | 17 |
| K3_rung_ban_xuat | `ban_xuat_that|dau_k3:sau khi` | 3 | 3 | 100% (44%–100%) | 0 |
| K3_rung_ban_xuat | `ban_xuat_that|dau_k3:trước khi` | 67 | 56 | 84% (73%–91%) | 11 |
| K3_rung_ban_xuat | `ban_xuat_that|dau_k3:trừ khi` | 3 | 3 | 100% (44%–100%) | 0 |
| K3_rung_ban_xuat | `ban_xuat_that|dau_khac:trừ` | 8 | 0 | 0% (0%–32%) | 8 |
| K3_rung_ban_xuat | `ban_xuat_that|dau_khac:ở bệnh nhân` | 9 | 0 | 0% (0%–30%) | 9 |
| K3_rung_ban_xuat | `ban_xuat_that|dau_khac:ở người` | 78 | 1 | 1% (0%–7%) | 77 |
| K3_rung_ban_xuat | `ban_xuat_that|dau_khac:ở phụ nữ` | 3 | 1 | 33% (6%–79%) | 2 |
| K3_rung_ban_xuat | `ban_xuat_that|nguong_so:bmi` | 2 | 0 | 0% (0%–66%) | 2 |
| K3_rung_ban_xuat | `ban_xuat_that|nguong_so:ef` | 12 | 0 | 0% (0%–24%) | 12 |
| K3_rung_ban_xuat | `ban_xuat_that|nguong_so:egfr` | 16 | 0 | 0% (0%–19%) | 16 |
| K3_rung_ban_xuat | `ban_xuat_that|nguong_so:ldl` | 2 | 0 | 0% (0%–66%) | 2 |
| K3_rung_ban_xuat | `ban_xuat_that|nguong_so:tuoi` | 32 | 0 | 0% (0%–11%) | 32 |
| K3_rung_ban_xuat | `ban_xuat_tong_hop|dau_k3:khi` | 1 | 1 | 100% (21%–100%) | 0 |
| K3_rung_trong_muc | `dau_k3:chỉ khi` | 11 | 0 | 0% (0%–26%) | 11 |
| K3_rung_trong_muc | `dau_k3:chống chỉ định` | 7 | 0 | 0% (0%–35%) | 7 |
| K3_rung_trong_muc | `dau_k3:khi` | 240 | 1 | 0% (0%–2%) | 239 |
| K3_rung_trong_muc | `dau_k3:không dùng cho` | 1 | 0 | 0% (0%–79%) | 1 |
| K3_rung_trong_muc | `dau_k3:không dùng khi` | 2 | 0 | 0% (0%–66%) | 2 |
| K3_rung_trong_muc | `dau_k3:ngoài thai kỳ` | 1 | 0 | 0% (0%–79%) | 1 |
| K3_rung_trong_muc | `dau_k3:nếu` | 107 | 2 | 2% (1%–7%) | 105 |
| K3_rung_trong_muc | `dau_k3:sau khi` | 3 | 1 | 33% (6%–79%) | 2 |
| K3_rung_trong_muc | `dau_k3:trước khi` | 67 | 1 | 1% (0%–8%) | 66 |
| K3_rung_trong_muc | `dau_k3:trừ khi` | 3 | 0 | 0% (0%–56%) | 3 |
| K3_rung_trong_muc | `dau_khac:trừ` | 8 | 1 | 12% (2%–47%) | 7 |
| K3_rung_trong_muc | `dau_khac:ở bệnh nhân` | 9 | 0 | 0% (0%–30%) | 9 |
| K3_rung_trong_muc | `dau_khac:ở người` | 78 | 0 | 0% (0%–5%) | 78 |
| K3_rung_trong_muc | `dau_khac:ở phụ nữ` | 3 | 1 | 33% (6%–79%) | 2 |
| K3_rung_trong_muc | `nguong_so:bmi` | 2 | 0 | 0% (0%–66%) | 2 |
| K3_rung_trong_muc | `nguong_so:ef` | 12 | 0 | 0% (0%–24%) | 12 |
| K3_rung_trong_muc | `nguong_so:egfr` | 16 | 0 | 0% (0%–19%) | 16 |
| K3_rung_trong_muc | `nguong_so:ldl` | 2 | 0 | 0% (0%–66%) | 2 |
| K3_rung_trong_muc | `nguong_so:tuoi` | 32 | 0 | 0% (0%–11%) | 32 |
| K4_muc_dao | `tien_to:KHÔNG` | 192 | 56 | 29% (23%–36%) | 136 |
| K4_muc_dao | `tien_to:Không nên` | 189 | 40 | 21% (16%–28%) | 149 |
| K4_muc_dao | `tien_to:Tránh` | 200 | 49 | 24% (19%–31%) | 151 |
| K4_nguon_nguoc | `associated_lower:not` | 1 | 1 | 100% (21%–100%) | 0 |
| K4_nguon_nguoc | `benefit:no` | 2 | 2 | 100% (34%–100%) | 0 |
| K4_nguon_nguoc | `effective:not` | 5 | 4 | 80% (38%–96%) | 1 |
| K4_nguon_nguoc | `hien_tai:does_not` | 10 | 10 | 100% (72%–100%) | 0 |
| K4_nguon_nguoc | `qua_khu:did_not` | 32 | 32 | 100% (89%–100%) | 0 |
| K4_nguon_nguoc | `recommend:against` | 20 | 20 | 100% (84%–100%) | 0 |
| K4_nguon_nguoc | `recommended:not` | 16 | 16 | 100% (81%–100%) | 0 |
| K4_nguon_nguoc | `resulted_in:did_not` | 5 | 5 | 100% (57%–100%) | 0 |
| K4_nguon_nguoc | `should_be:not` | 7 | 7 | 100% (65%–100%) | 0 |
| K4_nguon_nguoc | `superior:not` | 5 | 5 | 100% (57%–100%) | 0 |
| K4_nguon_nguoc | `was_lower:not` | 4 | 4 | 100% (51%–100%) | 0 |

## 4. Đối chứng KHÔNG đột biến (cận trên báo động giả)

| Phép | Mục có nguồn | Mục có 🟠 | Tỉ lệ (KTC 95%) | Mục phép phán được ✓/🟠 |
|---|---|---|---|---|
| K1 | 663 | 13 | 2% (1%–3%) | 122 (18%) |
| K2 | 663 | 12 | 2% (1%–3%) | 107 (16%) |
| K3b | 663 | 4 | 1% (0%–2%) | 32 (5%) |
| K4 | 663 | 52 | 8% (6%–10%) | 663 (100%) |
| K4b | 663 | 0 | 0% (0%–1%) | 10 (2%) |

Mức DASHBOARD (đúng như mã thoát bước ④-bis/④-ter — nếu chuyển sang CHẶN, bao nhiêu bản đã PASS hôm nay sẽ bị chặn):

- K1/K2/K4 (bộ đệm tóm tắt, ngoại tuyến): 45/97 dashboard có ≥1 🟠 (46%).
- K3b/K4b (cùng bước ④-ter): 4/97 dashboard có ≥1 🟠.
- K3 (bản đọc + Word HTML thật, so theo TỪNG MỤC khi định vị được mục): 102/115 dashboard có ≥1 🟠 · 888/3530 dòng cụm-điều-kiện × sản phẩm là 🟠.


## Chuẩn hoá nguồn — chữ bị xoá

Bộ chuẩn hoá NGUỒN mà bộ kiểm đang dùng xoá chữ ở 0/298 nguồn (0 nguồn mất đoạn > 200 ký tự; tổng 0 / 1,607,222 ký tự). Với mẫu cũ (mọi «<…>» là thẻ HTML, trước bản vá 14/11/2026) con số này là 7/298: trong văn bản THUẦN «<» là dấu so sánh, chữ tới dấu «>» kế tiếp bị xoá trước khi K1/K2/K4 đọc.

## So sánh TRƯỚC/SAU (cùng hạt giống, cùng dữ liệu) — trước: `do-nhay-dot-bien-20261114.json`

| Phép / lớp | Trước: bắt/n (độ nhạy) | Sau: bắt/n (độ nhạy) |
|---|---|---|
| K1 | 99/187 (53%) | 186/187 (99%) |
| K2 | 166/169 (98%) | 168/171 (98%) |
| K3 | 322/602 (53%) | 374/604 (62%) |
| K4 | 66/107 (62%) | 106/107 (99%) |
| K1 · riêng cách viết trong từ điển | 99/103 (96%) | 186/187 (99%) |
| K1 · cách viết ngoài từ điển (đo lỗ hổng từ vựng) | 0/84 (0%) | — |
| K3b · rụng điều kiện NGAY TRONG MỤC (trước: ngoài phạm vi) | 0/602 (0%) | 7/604 (1%) |
| K4b · MỤC đảo sang «không làm» (trước: ngoài phạm vi) | 0/582 (0%) | 145/581 (25%) |
| K2 · ngưỡng trong HÀNH ĐỘNG (vẫn ngoài phạm vi) | 0/40 (0%) | 0/40 (0%) |

Đọc bảng trên: nếu lượt SAU thêm vào từ điển bộ kiểm CHÍNH những cách viết/dạng phủ định mà bộ sinh dùng, phần tăng ở đây đo CƠ CHẾ trên các cách viết đó — không chứng minh bộ kiểm phủ được cách viết khác (cần một danh sách biến thể giữ riêng, bộ kiểm chưa từng thấy). Mẫu số có thể lệch vài đơn vị vì bộ sinh dùng chung chuẩn hoá và đối chứng K4 của bộ kiểm làm điều kiện tiên quyết.

| Đối chứng (mục thật, chưa đột biến) | Trước | Sau |
|---|---|---|
| K1 · mục có 🟠 / mục có nguồn | 19/663 (3%) | 13/663 (2%) |
| K2 · mục có 🟠 / mục có nguồn | 14/663 (2%) | 12/663 (2%) |
| K3b · mục có 🟠 / mục có nguồn | — | 4/663 (1%) |
| K4 · mục có 🟠 / mục có nguồn | 51/663 (8%) | 52/663 (8%) |
| K4b · mục có 🟠 / mục có nguồn | — | 0/663 (0%) |
| K1/K2/K4 · dashboard có 🟠 | 46/97 (47%) | 45/97 (46%) |
| K3b/K4b · dashboard có 🟠 | — | 4/97 (4%) |
| K3 · dashboard có 🟠 | 102/115 (89%) | 102/115 (89%) |
| K3 · dòng cụm × sản phẩm là 🟠 | 889/3504 | 888/3530 |
| Nguồn bị chuẩn hoá xoá chữ | 7/298 | 0/298 |

## Cách đọc và giới hạn

- «Bắt đúng chỗ» = trường đích của phép chuyển 🟠; «🟠 lệch chỗ» = phép có 🟠 MỚI nhưng ở phần tử khác; «Lọt ✓» = phép báo khớp trên mục đã bị làm sai (nguy hiểm nhất); «Lọt ⚪» = phép nói chưa kiểm được; «Lọt im» = phép không sinh dòng nào cho phần bị đổi (từ điển/phạm vi không với tới).
- Nhãn lỗi theo CẤU TRÚC: máy biết đã đổi gì; điều kiện tiên quyết bảo đảm bản gốc khớp nguồn (ngưỡng/cỡ mẫu/nhãn có trong thân tóm tắt) và giá trị mới không có trong nguồn. K4: chỉ đột biến mục mà đối chứng K4 = ✓.
- Danh mục của bộ sinh cố ý rộng hơn từ điển bộ kiểm (cách viết tiếng Việt khác, dạng động từ hiện tại, dấu điều kiện ngoài danh sách K3) — vì vậy độ nhạy phản ánh cả lỗ hổng từ vựng, không chỉ cơ chế.
- Đột biến tổng hợp ≠ lỗi thật: lỗi do người/agent soạn có thể tinh vi hơn (diễn đạt lại, sai một phần). Tóm tắt PubMed không phải toàn văn. Khử trùng theo bản PASS mới nhất mỗi chủ đề.
- K3b/K4b (14/11/2026c) đọc tóm tắt tiếng ANH để so với mục tiếng VIỆT ⇒ chỉ so được thứ ánh xạ tất định: K3b xét câu khuyến cáo CÓ ĐIỀU KIỆN của nguồn neo vào hành động qua thuật ngữ La-tinh chung (ngưỡng có toán tử / hành động còn hay mất mọi dấu điều kiện), K4b xét câu ủng hộ/chống ở Kết luận. Mệnh đề định tính không so được nội dung.
- Báo cáo không chép văn bản nguồn; tóm tắt nằm ở bộ đệm ngoài git.

_Cần bác sĩ kiểm chứng._
