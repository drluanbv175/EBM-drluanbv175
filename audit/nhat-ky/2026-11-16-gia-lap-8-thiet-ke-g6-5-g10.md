# 16/11/2026 — Giả lập trọn vòng 8 thiết kế đi hết G10: 12 lỗi hệ thống ngoài đề tài thuần tập, SPSS/R từng đề tài

## Bối cảnh
Tiếp `2026-11-16-quyet-dinh-da-chot-g7-g9-g10.md`. Bác sĩ giao: «Gộp các PR; hoàn thiện các đề tài giả lập, nhập vào SPSS
và R chi tiết, mỗi đề tài một thư mục; sau giả lập hoàn thiện hệ thống». Trước đợt này chỉ đề tài thuần tập đi hết G10;
7 thiết kế còn lại (RCT, cắt ngang mô tả, bệnh–chứng, chẩn đoán, dự báo, tổng quan–gộp, định tính) dừng ở G6 vì bộ giả
lập chưa có hồ sơ vai G6.5–G10 và đường phân tích cho 4 thiết kế đặc thù.

## Đã làm (repo y khoa — PR #290 đã gộp + nhánh `claude/gia-lap-8-thiet-ke-phan-2-20261116`)
1. **Phần 1 (PR #290, đã gộp):** G2 (ICF/PROSPERO không để ô mẫu chung; **G2-AUTO-11** đăng ký đề tài tiến cứu/tổng quan),
   G4 (chứng chỉ khoá chép §2; cắt ngang mô tả = tỷ lệ Wilson), G5 (khoá bản ghi đã duyệt; biến calc; cột ngày đã khai),
   G6 (họ «proportion»; quy ước `◆ MÔ HÌNH CHÍNH (SAP §4)`; nhóm con loại hiệp biến hằng sau lọc).
2. **Phân tích đặc thù** `tools/phan_tich_thiet_ke_dac_thu.py`: chẩn đoán (AUC Hanley–McNeil, độ nhạy/đặc hiệu/PPV/NPV
   Wilson), dự báo (logistic, C-statistic, Brier), tổng quan–gộp (RR DerSimonian–Laird + cố định), định tính (tần suất
   chủ đề + Wilson); kiểm chéo R (pROC/glm/metafor) + SPSS; Python khớp metafor/pROC tới 1e-9. Hàm `can_bac_hai` cho
   biến calc có sqrt (FIB-4).
3. **Hồ sơ vai G6.5–G10** cho 7 thiết kế (`tools/gia_lap_ho_so_sau_g6.py`); đối chiếu y văn bằng bài đã tra PubMed,
   chỉ số có trong tóm tắt: Thakkar 2016 (PMID 26831740), NCD-RisC 2021 (PMID 34450083), Masclee 2014 (PMID 24937265),
   Shah 2009 (PMID 19523535), Ouwerkerk 2014 (PMID 25194294), Zelniker 2019 (PMID 30424892), Polonsky 2011/2019
   (PMID 21469914, 30709604). Bộ đọc ước lượng của bộ giả lập đọc đúng khoá engine cho mọi thước đo.
4. **12 lỗi hệ thống lộ ra khi đi G6.5→G10:**
   - Engine G6: bệnh–chứng ghi «Risk difference» (lấy mẫu theo bệnh ⇒ không ước lượng được) — nay gỡ, ghi lý do; bảng
     Poisson gọi RR cho RCT/thuần tập (trước in «PR — tỷ lệ hiện mắc»).
   - G0: nhãn «[CẦN BÁC SĨ TỰ XÁC ĐỊNH …]» ngoài bộ nhãn skill ⇒ check_de_cuong R3 chặn G10 của MỌI đề tài G0 không thấy
     khoảng trống; nay `[CẦN — …]`.
   - G10 Đặt vấn đề: in khoảng trống máy suy dù PI đã viết ở G1 — nay ưu tiên người (như StudySpec từ 10/10).
   - G10 đề cương hỏi lại quyết định đặc thù đã chốt ⇒ `quyet_dinh_da_chot._theo_thiet_ke` lấp: ngưỡng chẩn đoán (SAP),
     tiêu chuẩn chọn + công cụ RoB + «không tính cỡ mẫu» của tổng quan, chọn mẫu/audit trail/hiện tượng trung tâm/hướng
     dẫn phỏng vấn của định tính, kiểm định/hiệu chuẩn/phân biệt + yếu tố dự báo của dự báo; «yếu tố nhiễu» = «Không áp
     dụng» cho thiết kế không nhân quả. `cong_cu_rob` dùng chung với phụ lục PROSPERO G2.
   - StudySpec D10: đọc `prevalence_source`/`confirmed_n_method` đã chốt ở G3.
   - G8-AUTO-08 đòi khai lại tuyên bố chia sẻ dữ liệu đã khai ở G7 — nay đọc G7.
   - G9-HUMAN-05 đòi đủ «dữ liệu gì/khi nào/cơ chế» cả khi thử nghiệm KHÔNG chia sẻ IPD — mâu thuẫn G8 (ICMJE 2017, PMID
     28582414, Ví dụ 4); nay nhận khi có lý do + khớp bản đăng ký.
   - G10-AUTO-09: DOI («doi:10.1007/s11606-026-10477-5») và ô «1.0» + ngày giờ của bảng phiên bản (chữ hiển thị .docx
     nối ô bằng xuống dòng) bị nhận là số điện thoại — nay bỏ DOI/URL và dò TỪNG DÒNG.
   - G4: SAP tổng quan–gộp dùng khuôn cá thể (EPV/VIF, MI m=20, ±1 SD, mice) — nay có khung riêng; SAP định tính điền
     sẵn tiếp cận/bão hoà/chọn mẫu từ G1; G4-AUTO-04/05/10 miễn đúng cho tổng quan.
   - A12 kiểm muộn ở G10 PMID mà đề cương trích thêm (nguồn cỡ mẫu G3, CONSORT, PRISMA-P 25554246) ⇒ ghi lại biên nhận
     làm vỡ manifest G9 đã khoá. `protocol_checklist_items.pmid_tai_lieu_chuan(<thiết kế>)`; quy trình: A12 phủ mọi PMID
     của gói (dựng nháp đề cương G10) TRƯỚC khi PI ký G9.
5. **Dạy 12 agent** (`dieu-phoi-g2/g4/g6/g7/g8/g9/g10`, `dao-duc-dang-ky`, `thiet-ke-nghien-cuu`, `phan-tich-thong-ke`,
   `dien-giai-ket-qua`, `kiem-chung-trich-dan`) — mục «… giả lập trọn vòng 8 thiết kế (16/11/2026)», đặt NGOÀI khối
   trách nhiệm máy sinh (lần đầu đặt nhầm trong khối của `kiem-chung-trich-dan` ⇒ `tieu_chuan_hoan_thien` A3 đỏ).

## Kiểm hồi quy (đo 16/11/2026)
- Bộ giả lập trọn vòng, lượt SẠCH từ G0 bằng mã cuối, khoá giả: **8/8 thiết kế đạt mọi cổng G2→G10**
  (`PASS_G10_RELEASE_PACKAGE_LOCKED`), không PMID kiểm muộn, bảng diễn giải không thiếu dòng.
- `tests/test_he_thong_sau_gia_lap_8_thiet_ke_20261116.py` (32) + `test_gia_lap_8_thiet_ke_tron_vong_20261116.py`
  (31) + `test_phan_tich_thiet_ke_dac_thu_20261116.py` (15). **29/29 phép đột biến** của phần 2 đỏ đúng chỗ rồi xanh lại.
- `test_g0_quality_gate_20260728::test_khong_bia_khoang_trong_viet_nam` từng đòi chuỗi «[CẦN BÁC SĨ» — nhãn đó không bao
  giờ qua R3; phép thử nay đòi «[CẦN — bác sĩ tự xác định» VÀ nhãn qua R3 (chặt hơn, không nới).
- Gói bàn giao: mỗi đề tài một thư mục, cú pháp SPSS + kịch bản R RIÊNG từng phân tích chạy thật; số khớp G6 (vd chẩn
  đoán AUC 0,599673… ở cả SPSS lẫn R). **Bẫy đo được:** SPSS giới hạn đường dẫn đầy đủ 255 ký tự — vượt thì báo
  «syntax is incomplete» (không phải lỗi cú pháp); thư mục kết quả phải ngắn.

## Còn lại / giới hạn
- Đây là dữ liệu MÔ PHỎNG, chữ ký khoá giả — không thay IRB/PI/thống kê viên/phản biện thật.
- Mục SAP «±1 SD» của khuôn cá thể vẫn in cho kết cục nhị phân (hồ sơ giả lập ghi «không áp dụng — SAP sửa đổi»); chưa
  đổi khuôn chung vì ảnh hưởng mọi thiết kế.
- `cau_noi_spss.py cu-phap` ghi đè MỘT tệp `spss/<mã>_phan_tich.sps` cho mọi phân tích (tệp còn lại là của phân tích chạy
  sau cùng) — gói bàn giao sinh lại cú pháp riêng từng phân tích; chưa đổi hành vi công cụ.
