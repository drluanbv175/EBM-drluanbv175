# Độ nhạy kiểm chéo ngữ nghĩa K1–K4 — đột biến tổng hợp (14/11/2026)

> **Đột biến TỔNG HỢP có nhãn theo cấu trúc — KHÔNG thay bộ vàng do bác sĩ gắn nhãn.** Công cụ không đổi chế độ chặn; chuyển K1–K4 từ CẢNH BÁO sang CHẶN là quyết định của bác sĩ (audit/16 §4). Báo động trên đối chứng là CẬN TRÊN của báo động giả: mục thật chưa được gắn nhãn đúng/sai.

Sinh bởi `tools/do_nhay_kiem_ngu_nghia.py` · hạt giống 20261114 · băm mã (16 ký tự đầu): `kiem_cheo_ngu_nghia.py` 1de40bea61a7701c, `kiem_quan_the_chieu.py` e2712800183c6905, `do_nhay_kiem_ngu_nghia.py` 3188a911fb21e0de.

## Tóm tắt

- Độ nhạy trong phạm vi thiết kế: K1 53% (n=187; riêng phần trong từ điển bộ kiểm 96% [KTC 90%–98%; 99/103]) · K2 98% (n=169) · K3 53% (n=602; riêng phần trong từ điển bộ kiểm 72% [KTC 68%–76%; 320/442]) · K4 62% (n=107).
- Số gộp tính cả cách viết/dấu điều kiện mà bộ sinh CỐ Ý chọn ngoài từ điển bộ kiểm (đo lỗ hổng từ vựng); «riêng phần trong từ điển» = K1 với cách viết bộ kiểm nhận được, K3 với nhóm dấu có trong từ điển K3 (`dau_k3`) — phần còn lọt ở đó là lỗ hổng CƠ CHẾ, không phải từ vựng.
- Lớp lỗi NGOÀI phạm vi thiết kế (không phép nào được thiết kế để bắt): K2 · đổi ngưỡng số nằm trong HÀNH ĐỘNG 0/40 · K3 · rụng điều kiện NGAY TRONG MỤC so với nguồn 0/602 · K4 · MỤC đảo sang «không làm» khi nguồn ủng hộ 0/582.
- Đối chứng mức dashboard — nếu chuyển sang CHẶN: K1/K2/K4 chặn 46/97 dashboard đã PASS, K3 chặn 102/115.

## Dữ liệu

- Dashboard ĐÃ PASS (bản mới nhất mỗi chủ đề): 115 (đọc được DATA: 115).
- Mục `apply` sau khử trùng: 826 · có tóm tắt PubMed để K1/K2/K4 đọc: 663.
- Tóm tắt: cần 298 PMID · có sẵn trong bộ đệm 298 · tải mới 0 · tải hỏng 0.
- Bộ sinh phủ được (mục đủ điều kiện tiên quyết / mục đã thử): K1_quan_the 187/663 · K2_co_mau 95/663 · K2_nguong 74/663 · K2_nguong_hanh_dong 40/663 · K3 602/826 · K4_muc_dao 582/582 · K4_nguon_nguoc 107/582.

## 1. Độ nhạy theo phép (chỉ đột biến TRONG phạm vi thiết kế của phép)

| Phép | n đột biến | Bắt đúng chỗ | Độ nhạy (KTC 95% Wilson) | Riêng phần trong từ điển bộ kiểm (KTC 95%; bắt/n) | Kể cả 🟠 lệch chỗ | Lọt ✓ (trấn an sai) | Lọt ⚪ | Lọt im |
|---|---|---|---|---|---|---|---|---|
| K1 | 187 | 99 | 53% (46%–60%) | 96% (90%–98%; 99/103) | 53% (46%–60%) | 4 | 0 | 84 |
| K2 | 169 | 166 | 98% (95%–99%) | — | 98% (95%–99%) | 0 | 3 | 0 |
| K3 | 602 | 322 | 53% (49%–57%) | 72% (68%–76%; 320/442) | 53% (49%–57%) | 165 | 0 | 115 |
| K4 | 107 | 66 | 62% (52%–70%) | — | 62% (52%–70%) | 41 | 0 | 0 |

## 2. Theo lớp đột biến

| Lớp | Phạm vi thiết kế | n | Bắt | Độ nhạy (KTC 95%) | Lọt ✓ | Lọt ⚪ | Lọt im |
|---|---|---|---|---|---|---|---|
| K1 · đổi nhãn quần thể (thay/chèn vế loại trừ) | trong | 187 | 99 | 53% (46%–60%) | 4 | 0 | 84 |
| K2 · đổi/chèn cỡ mẫu n= | trong | 95 | 92 | 97% (91%–99%) | 0 | 3 | 0 |
| K2 · đổi ngưỡng số trong quần thể (EF/eGFR/tuổi/HbA1c/BMI/LDL) | trong | 74 | 74 | 100% (95%–100%) | 0 | 0 | 0 |
| K2 · đổi ngưỡng số nằm trong HÀNH ĐỘNG | **ngoài** | 40 | 0 | 0% (0%–9%) | 0 | 0 | 40 |
| K3 · rụng điều kiện ở BẢN XUẤT (mục giữ nguyên) | trong | 602 | 322 | 53% (49%–57%) | 165 | 0 | 115 |
| K3 · rụng điều kiện NGAY TRONG MỤC so với nguồn | **ngoài** | 602 | 0 | 0% (0%–1%) | 255 | 0 | 347 |
| K4 · MỤC đảo sang «không làm» khi nguồn ủng hộ | **ngoài** | 582 | 0 | 0% (0%–1%) | 582 | 0 | 0 |
| K4 · nguồn nói NGƯỢC chiều mục apply | trong | 107 | 66 | 62% (52%–70%) | 41 | 0 | 0 |

Lớp **ngoài phạm vi thiết kế** đo lỗ hổng — không tính vào độ nhạy của phép ở bảng 1:
- K2 · đổi ngưỡng số nằm trong HÀNH ĐỘNG: K1/K2 chỉ đọc population/pico.P/title — không đọc action.
- K3 · rụng điều kiện NGAY TRONG MỤC so với nguồn: K3 so BẢN XUẤT với MỤC, không so MỤC với nguồn ⇒ cụm đã rụng khỏi mục thì không còn gì để so.
- K4 · MỤC đảo sang «không làm» khi nguồn ủng hộ: K4 chỉ tìm tín hiệu ngược chiều trong NGUỒN; mục nói «không làm» còn được coi là cùng chiều nguồn.

**K3 — phân tích thêm (rụng ở bản xuất):**
- Bắt theo nhóm dấu điều kiện của bộ sinh: dau_k3 320/442 (72%; KTC 68%–76%), dau_khac 2/98 (2%; KTC 1%–7%), nguong_so 0/62 (0%; KTC 0%–6%) (`dau_k3` = dấu có trong từ điển K3; `dau_khac` = giới hạn quần thể/điều kiện ngoài từ điển; `nguong_so` = ngưỡng số đứng trần, không có «nếu/khi»).
- 280 lần lọt, quy theo cụm mà K3 THỰC trích từ hành động (không theo cụm của bộ sinh): 115 lần K3 không trích được cụm nào · 84 lần mọi cụm K3 trích vẫn nguyên trong hành động đã cắt (phần bị cắt nằm ngoài cụm của K3) · 81 lần cụm K3 bị cắt khỏi hành động nhưng còn ở chỗ khác trong bản xuất (K3 khớp cấp TÀI LIỆU, không biết cụm thuộc mục nào).
- Độ nhạy TỐI ĐA nếu K3 so theo TỪNG MỤC (bắt + ca khớp cấp tài liệu, trên cùng n = 602): 67% (63%–71%). Lỗ hổng trích cụm/từ vựng (199/280 lần lọt) lớn hơn lỗ hổng so khớp cấp tài liệu (81/280).
- 0 đột biến có hành động hiển thị ≥ 2 lần nguyên văn trong Word; nếu chỉ MỘT chỗ mất cụm thì K3 bắt 0/0.

**K1 — tách từ vựng khỏi cơ chế:**
- Cách viết bộ kiểm NHẬN được (hỏi thẳng `kiem_cap` thật): 96% (90%–98%; 99/103) · cách viết NGOÀI từ điển: 0% (0%–4%; 0/84).

**Lý do lọt (trong phạm vi thiết kế):**

| Lớp | Lý do | Số lần |
|---|---|---|
| K1_quan_the | cách viết tiếng Việt của nhãn không có trong từ điển bộ kiểm | 84 |
| K1_quan_the | từ khoá vế đổi sang chỉ có ở DÒNG TÁC GIẢ/cơ quan (vd «Children's Hospital») ⇒ bộ kiểm tưởng nguồn có nêu | 4 |
| K2_co_mau | nguồn không nêu ⇒ ⚪ | 3 |
| K3_rung_ban_xuat | K3 không trích được cụm điều kiện nào từ hành động | 115 |
| K3_rung_ban_xuat | mọi cụm K3 trích được vẫn nguyên trong hành động đã cắt (phần bị cắt nằm ngoài cụm của K3) | 84 |
| K3_rung_ban_xuat | cụm K3 trích được bị cắt khỏi hành động nhưng còn ở chỗ khác trong bản xuất ⇒ K3 khớp cấp tài liệu vẫn thấy | 81 |
| K4_nguon_nguoc | dạng phủ định không có trong từ điển K4 (thì hiện tại, «not effective», «did not result in»…) | 35 |
| K4_nguon_nguoc | câu đã đảo nằm trong đoạn chuan_hoa xoá như thẻ HTML («<» so sánh … «>») | 3 |
| K4_nguon_nguoc | câu đã đảo bị bộ lọc «kết cục phụ» bỏ qua (vd «secondary analysis», «secondary prevention») | 3 |

## 3. Theo biến thể (dạng bề mặt) — lỗ hổng từ vựng

| Lớp | Biến thể | n | Bắt | Độ nhạy (KTC 95%) | Lọt |
|---|---|---|---|---|---|
| K1_quan_the | `chen_nhan:HFrEF` | 1 | 1 | 100% (21%–100%) | 0 |
| K1_quan_the | `chen_nhan:bệnh nhi` | 15 | 0 | 0% (0%–20%) | 15 |
| K1_quan_the | `chen_nhan:ngoài thai kỳ` | 9 | 9 | 100% (70%–100%) | 0 |
| K1_quan_the | `chen_nhan:người lớn` | 2 | 2 | 100% (34%–100%) | 0 |
| K1_quan_the | `chen_nhan:người trưởng thành` | 6 | 0 | 0% (0%–39%) | 6 |
| K1_quan_the | `chen_nhan:nhi khoa` | 14 | 14 | 100% (78%–100%) | 0 |
| K1_quan_the | `chen_nhan:phụ nữ không mang thai` | 12 | 12 | 100% (76%–100%) | 0 |
| K1_quan_the | `chen_nhan:suy tim PSTM giảm` | 1 | 0 | 0% (0%–79%) | 1 |
| K1_quan_the | `chen_nhan:suy tim phân suất tống máu còn bảo tồn` | 1 | 0 | 0% (0%–79%) | 1 |
| K1_quan_the | `chen_nhan:trẻ em` | 14 | 12 | 86% (60%–96%) | 2 |
| K1_quan_the | `chen_nhan:trẻ vị thành niên` | 15 | 0 | 0% (0%–20%) | 15 |
| K1_quan_the | `chen_nhan:ĐTĐ típ 2` | 1 | 1 | 100% (21%–100%) | 0 |
| K1_quan_the | `chen_nhan:ĐTĐ1` | 3 | 0 | 0% (0%–56%) | 3 |
| K1_quan_the | `chen_nhan:đái tháo đường type 1` | 2 | 2 | 100% (34%–100%) | 0 |
| K1_quan_the | `thay_nhan:HFpEF` | 3 | 3 | 100% (44%–100%) | 0 |
| K1_quan_the | `thay_nhan:bệnh nhi` | 19 | 0 | 0% (0%–17%) | 19 |
| K1_quan_the | `thay_nhan:chưa lọc máu` | 1 | 1 | 100% (21%–100%) | 0 |
| K1_quan_the | `thay_nhan:ngoài thai kỳ` | 3 | 3 | 100% (44%–100%) | 0 |
| K1_quan_the | `thay_nhan:nhi khoa` | 14 | 14 | 100% (78%–100%) | 0 |
| K1_quan_the | `thay_nhan:phụ nữ không mang thai` | 4 | 4 | 100% (51%–100%) | 0 |
| K1_quan_the | `thay_nhan:suy tim EF bảo tồn` | 1 | 1 | 100% (21%–100%) | 0 |
| K1_quan_the | `thay_nhan:suy tim PSTM giảm` | 2 | 0 | 0% (0%–66%) | 2 |
| K1_quan_the | `thay_nhan:suy tim phân suất tống máu bảo tồn` | 3 | 3 | 100% (44%–100%) | 0 |
| K1_quan_the | `thay_nhan:suy tim phân suất tống máu còn bảo tồn` | 1 | 0 | 0% (0%–79%) | 1 |
| K1_quan_the | `thay_nhan:suy tim phân suất tống máu giảm` | 1 | 1 | 100% (21%–100%) | 0 |
| K1_quan_the | `thay_nhan:trẻ em` | 14 | 12 | 86% (60%–96%) | 2 |
| K1_quan_the | `thay_nhan:trẻ vị thành niên` | 21 | 0 | 0% (0%–15%) | 21 |
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
| K2_nguong | `tuoi:so_truoc` | 52 | 52 | 100% (93%–100%) | 0 |
| K2_nguong_hanh_dong | `bmi:chi_truoc` | 1 | 0 | 0% (0%–79%) | 1 |
| K2_nguong_hanh_dong | `ef:chi_truoc` | 2 | 0 | 0% (0%–66%) | 2 |
| K2_nguong_hanh_dong | `egfr:chi_truoc` | 3 | 0 | 0% (0%–56%) | 3 |
| K2_nguong_hanh_dong | `ldl:chi_truoc` | 1 | 0 | 0% (0%–79%) | 1 |
| K2_nguong_hanh_dong | `tuoi:chi_truoc` | 1 | 0 | 0% (0%–79%) | 1 |
| K2_nguong_hanh_dong | `tuoi:so_truoc` | 32 | 0 | 0% (0%–11%) | 32 |
| K3_rung_ban_xuat | `ban_xuat_that|dau_k3:chỉ khi` | 11 | 10 | 91% (62%–98%) | 1 |
| K3_rung_ban_xuat | `ban_xuat_that|dau_k3:chống chỉ định` | 7 | 5 | 71% (36%–92%) | 2 |
| K3_rung_ban_xuat | `ban_xuat_that|dau_k3:khi` | 236 | 166 | 70% (64%–76%) | 70 |
| K3_rung_ban_xuat | `ban_xuat_that|dau_k3:không dùng cho` | 1 | 1 | 100% (21%–100%) | 0 |
| K3_rung_ban_xuat | `ban_xuat_that|dau_k3:không dùng khi` | 2 | 2 | 100% (34%–100%) | 0 |
| K3_rung_ban_xuat | `ban_xuat_that|dau_k3:ngoài thai kỳ` | 1 | 0 | 0% (0%–79%) | 1 |
| K3_rung_ban_xuat | `ban_xuat_that|dau_k3:nếu` | 107 | 81 | 76% (67%–83%) | 26 |
| K3_rung_ban_xuat | `ban_xuat_that|dau_k3:sau khi` | 3 | 3 | 100% (44%–100%) | 0 |
| K3_rung_ban_xuat | `ban_xuat_that|dau_k3:trước khi` | 67 | 45 | 67% (55%–77%) | 22 |
| K3_rung_ban_xuat | `ban_xuat_that|dau_k3:trừ khi` | 3 | 3 | 100% (44%–100%) | 0 |
| K3_rung_ban_xuat | `ban_xuat_that|dau_khac:trừ` | 8 | 0 | 0% (0%–32%) | 8 |
| K3_rung_ban_xuat | `ban_xuat_that|dau_khac:ở bệnh nhân` | 9 | 0 | 0% (0%–30%) | 9 |
| K3_rung_ban_xuat | `ban_xuat_that|dau_khac:ở người` | 76 | 1 | 1% (0%–7%) | 75 |
| K3_rung_ban_xuat | `ban_xuat_that|dau_khac:ở phụ nữ` | 3 | 1 | 33% (6%–79%) | 2 |
| K3_rung_ban_xuat | `ban_xuat_that|nguong_so:bmi` | 2 | 0 | 0% (0%–66%) | 2 |
| K3_rung_ban_xuat | `ban_xuat_that|nguong_so:ef` | 10 | 0 | 0% (0%–28%) | 10 |
| K3_rung_ban_xuat | `ban_xuat_that|nguong_so:egfr` | 16 | 0 | 0% (0%–19%) | 16 |
| K3_rung_ban_xuat | `ban_xuat_that|nguong_so:ldl` | 2 | 0 | 0% (0%–66%) | 2 |
| K3_rung_ban_xuat | `ban_xuat_that|nguong_so:tuoi` | 31 | 0 | 0% (0%–11%) | 31 |
| K3_rung_ban_xuat | `ban_xuat_tong_hop|dau_k3:khi` | 4 | 4 | 100% (51%–100%) | 0 |
| K3_rung_ban_xuat | `ban_xuat_tong_hop|dau_khac:ở người` | 2 | 0 | 0% (0%–66%) | 2 |
| K3_rung_ban_xuat | `ban_xuat_tong_hop|nguong_so:ef` | 1 | 0 | 0% (0%–79%) | 1 |
| K3_rung_trong_muc | `dau_k3:chỉ khi` | 11 | 0 | 0% (0%–26%) | 11 |
| K3_rung_trong_muc | `dau_k3:chống chỉ định` | 7 | 0 | 0% (0%–35%) | 7 |
| K3_rung_trong_muc | `dau_k3:khi` | 240 | 0 | 0% (0%–2%) | 240 |
| K3_rung_trong_muc | `dau_k3:không dùng cho` | 1 | 0 | 0% (0%–79%) | 1 |
| K3_rung_trong_muc | `dau_k3:không dùng khi` | 2 | 0 | 0% (0%–66%) | 2 |
| K3_rung_trong_muc | `dau_k3:ngoài thai kỳ` | 1 | 0 | 0% (0%–79%) | 1 |
| K3_rung_trong_muc | `dau_k3:nếu` | 107 | 0 | 0% (0%–3%) | 107 |
| K3_rung_trong_muc | `dau_k3:sau khi` | 3 | 0 | 0% (0%–56%) | 3 |
| K3_rung_trong_muc | `dau_k3:trước khi` | 67 | 0 | 0% (0%–5%) | 67 |
| K3_rung_trong_muc | `dau_k3:trừ khi` | 3 | 0 | 0% (0%–56%) | 3 |
| K3_rung_trong_muc | `dau_khac:trừ` | 8 | 0 | 0% (0%–32%) | 8 |
| K3_rung_trong_muc | `dau_khac:ở bệnh nhân` | 9 | 0 | 0% (0%–30%) | 9 |
| K3_rung_trong_muc | `dau_khac:ở người` | 78 | 0 | 0% (0%–5%) | 78 |
| K3_rung_trong_muc | `dau_khac:ở phụ nữ` | 3 | 0 | 0% (0%–56%) | 3 |
| K3_rung_trong_muc | `nguong_so:bmi` | 2 | 0 | 0% (0%–66%) | 2 |
| K3_rung_trong_muc | `nguong_so:ef` | 11 | 0 | 0% (0%–26%) | 11 |
| K3_rung_trong_muc | `nguong_so:egfr` | 16 | 0 | 0% (0%–19%) | 16 |
| K3_rung_trong_muc | `nguong_so:ldl` | 2 | 0 | 0% (0%–66%) | 2 |
| K3_rung_trong_muc | `nguong_so:tuoi` | 31 | 0 | 0% (0%–11%) | 31 |
| K4_muc_dao | `tien_to:KHÔNG` | 193 | 0 | 0% (0%–2%) | 193 |
| K4_muc_dao | `tien_to:Không nên` | 189 | 0 | 0% (0%–2%) | 189 |
| K4_muc_dao | `tien_to:Tránh` | 200 | 0 | 0% (0%–2%) | 200 |
| K4_nguon_nguoc | `associated_lower:not` | 1 | 0 | 0% (0%–79%) | 1 |
| K4_nguon_nguoc | `benefit:no` | 2 | 2 | 100% (34%–100%) | 0 |
| K4_nguon_nguoc | `effective:not` | 5 | 0 | 0% (0%–43%) | 5 |
| K4_nguon_nguoc | `hien_tai:does_not` | 10 | 0 | 0% (0%–28%) | 10 |
| K4_nguon_nguoc | `qua_khu:did_not` | 32 | 27 | 84% (68%–93%) | 5 |
| K4_nguon_nguoc | `recommend:against` | 20 | 20 | 100% (84%–100%) | 0 |
| K4_nguon_nguoc | `recommended:not` | 16 | 14 | 88% (64%–97%) | 2 |
| K4_nguon_nguoc | `resulted_in:did_not` | 5 | 0 | 0% (0%–43%) | 5 |
| K4_nguon_nguoc | `should_be:not` | 7 | 1 | 14% (3%–51%) | 6 |
| K4_nguon_nguoc | `superior:not` | 5 | 2 | 40% (12%–77%) | 3 |
| K4_nguon_nguoc | `was_lower:not` | 4 | 0 | 0% (0%–49%) | 4 |

## 4. Đối chứng KHÔNG đột biến (cận trên báo động giả)

| Phép | Mục có nguồn | Mục có 🟠 | Tỉ lệ (KTC 95%) | Mục phép phán được ✓/🟠 |
|---|---|---|---|---|
| K1 | 663 | 19 | 3% (2%–4%) | 139 (21%) |
| K2 | 663 | 14 | 2% (1%–4%) | 107 (16%) |
| K4 | 663 | 51 | 8% (6%–10%) | 663 (100%) |

Mức DASHBOARD (đúng như mã thoát bước ④-bis/④-ter — nếu chuyển sang CHẶN, bao nhiêu bản đã PASS hôm nay sẽ bị chặn):

- K1/K2/K4 (bộ đệm tóm tắt, ngoại tuyến): 46/97 dashboard có ≥1 🟠 (47%).
- K3 (bản đọc + Word HTML thật): 102/115 dashboard có ≥1 🟠 · 889/3504 dòng cụm-điều-kiện × sản phẩm là 🟠.


## Phát hiện phụ — chuẩn hoá nguồn làm mất chữ

`chuan_hoa()` (K3, được K1/K2/K4 dùng lại) xoá mọi đoạn «<…>» như thẻ HTML. Bản tóm tắt efetch là văn bản THUẦN, «<» là dấu so sánh ⇒ chữ tới dấu «>» kế tiếp bị xoá trước khi K1/K2/K4 đọc: 7/298 nguồn bị cắt, 3 nguồn mất đoạn > 200 ký tự, tổng 5,030 / 1,607,222 ký tự. Đoạn bị xoá có thể chứa đúng câu «not recommended» mà K4 cần thấy.

## Cách đọc và giới hạn

- «Bắt đúng chỗ» = trường đích của phép chuyển 🟠; «🟠 lệch chỗ» = phép có 🟠 MỚI nhưng ở phần tử khác; «Lọt ✓» = phép báo khớp trên mục đã bị làm sai (nguy hiểm nhất); «Lọt ⚪» = phép nói chưa kiểm được; «Lọt im» = phép không sinh dòng nào cho phần bị đổi (từ điển/phạm vi không với tới).
- Nhãn lỗi theo CẤU TRÚC: máy biết đã đổi gì; điều kiện tiên quyết bảo đảm bản gốc khớp nguồn (ngưỡng/cỡ mẫu/nhãn có trong thân tóm tắt) và giá trị mới không có trong nguồn. K4: chỉ đột biến mục mà đối chứng K4 = ✓.
- Danh mục của bộ sinh cố ý rộng hơn từ điển bộ kiểm (cách viết tiếng Việt khác, dạng động từ hiện tại, dấu điều kiện ngoài danh sách K3) — vì vậy độ nhạy phản ánh cả lỗ hổng từ vựng, không chỉ cơ chế.
- Đột biến tổng hợp ≠ lỗi thật: lỗi do người/agent soạn có thể tinh vi hơn (diễn đạt lại, sai một phần). Tóm tắt PubMed không phải toàn văn. Khử trùng theo bản PASS mới nhất mỗi chủ đề.
- Báo cáo không chép văn bản nguồn; tóm tắt nằm ở bộ đệm ngoài git.

_Cần bác sĩ kiểm chứng._
