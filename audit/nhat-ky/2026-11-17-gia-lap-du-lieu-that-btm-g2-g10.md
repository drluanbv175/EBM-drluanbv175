# 17/11/2026 — Giả lập dữ liệu chân thực trên khung thật BTM: lần đầu đi trọn G2→G10, lộ 9 lỗi hệ

## Bối cảnh

Bác sĩ yêu cầu: «Hãy giả lập với dữ liệu để hoàn thiện toàn diện. Hãy giải quyết cho xong các vấn đề trên dựa trên sự
giả lập chân thực và chính xác».

Buổi diễn tập trước, cùng ngày (nhật ký `2026-11-17-ba-de-xuat-hoan-thien-he-nghien-cuu.md`), dừng ở bước tiếp nhận dữ
liệu G5. Lý do: dữ liệu mô phỏng không theo logic nhánh của phiếu.

Lần này dữ liệu được sinh THEO ĐÚNG từ điển REDCap G5 của BTM, bằng công cụ mới `tools/sinh_du_lieu_redcap.py`:
- logic nhánh, trường calc, khoảng hợp lệ, thứ tự ngày;
- trích tiếp hồ sơ cho tới khi đủ 385 hồ sơ `du_tieu_chuan = 1`, như SOP-TR-01;
- creatinin và UACR rút có điều kiện theo Folkerts 2021 (PMID 33722396).

Buổi diễn tập chạy trên bản sao ngoài repo, với khoá giả.

## Kết quả đo được

- **G2 → G9:** đạt hết. G5 khoá dữ liệu với 0 query mở. MT1 chạy trên dữ liệu khoá: 168/385 = 43,6%. G7 xác nhận, G8 ghi
  nhận phản biện, G9 khoá.
- **G10:** dừng ở đúng ba việc của người. Một là phê duyệt của PI. Hai là trục nhất quán «kết cục chính» cần chủ nhiệm
  giải trình. Ba là ô TLTK tiếng Việt, mà nguyên nhân là lỗi hệ số 10 bên dưới.
- **Số ô lỗi máy:** 0.

## Lỗi hệ (đã sửa ở PR y khoa cùng đợt)

1. **Trường calc vắng trong tệp Excel/SPSS.** Mọi nhánh dựa trên calc (`[du_tieu_chuan] = '1'`) «không đánh giá được» ở
   464/464 hàng. Bộ làm sạch mở 19.952 query thiếu oan. Công cụ nhập Excel lại bỏ qua câu bắt buộc trống. Sửa:
   `nhap_lieu_excel.tinh_calc` tính lại calc theo công thức từ điển (if(), so sánh, + − × ÷), chỉ cho logic, và chỉ tính
   calc mà nhánh/luật DQ tham chiếu.
2. **Câu chọn nhiều BẮT BUỘC.** REDCap xuất các câu này thành `<biến>___<mã>`. Bộ làm sạch và G5-AUTO-07b cùng báo «thiếu
   biến bắt buộc» không đóng được.
3. **G6 không nhắc lọc quần thể phân tích.** Bảng 1 tính trên 458 hồ sơ đã mở (gồm 73 hồ sơ bị loại), G7 chép N = 458.
   Nay `chay_sap_g6 kiem` đọc «Quần thể chính» ở SAP §1. Phân tích chính thiếu `tham_so.loc` ⇒ lỗi; phân tích khác ⇒ cảnh
   báo.
4. **G8-AUTO-05** không rút được «- **Kết cục chính (MT1):**» (có ngoặc mục tiêu sau nhãn).
5. **R15 (StudySpec)** báo biến kết cục chính `xn_du` «không có trong CRF», dù đó là biến phái sinh đã khai. Lỗi này sẽ
   chặn G10 thật của BTM ngay khi có G5.
6. **R4 gắn nhãn «nghi bịa» cho 6 PMID thật** (KDIGO 2022/2024, ADA 2026…) khi lượt A12 không gọi được NCBI. Nay tách
   thành «CHƯA XÁC MINH ĐƯỢC — chạy lại A12». Vẫn chặn, nhưng nói đúng nguyên nhân.
7. **Bộ giả lập:** ghi Excel chỉ trang biểu mẫu đầu, làm so nhập kép báo 25.556 ô lệch giả. Ghi đè phiếu thu thập do chủ
   nhiệm soạn. Coi ô «Mục tiêu chung» là hỏi lại `G1.objectives`. Sinh dữ liệu bằng `eval` (nay dùng bộ đánh giá chung
   của hệ).
8. **Kịch bản diễn tập trước:** G2 ghi đè quyết định thật của BTM (hồi cứu, miễn phiếu đồng ý) thành «tiến cứu +
   ClinicalTrials.gov», và đầu vào G7–G10 mượn nội dung tăng huyết áp. Lần này giữ quyết định thật và viết đầu vào riêng
   cho BTM.
9. **Bộ sinh đề cương nộp ghi cứng câu cam kết** «huỷ [bảng nối mã] sau khi kết thúc nghiên cứu», trái với quy trình dữ
   liệu đã chốt («huỷ sau khi khoá dữ liệu»).

## Chưa sửa ở đợt này (bước kế tiếp)

10. **TLTK chỉ có DOI.** Cả hai bộ sinh đề cương và cổng A12 chỉ xử lý PMID. 12 bài tạp chí trong nước của BTM (vd
    15,32%, DOI 10.51298/vmj.v556i3.16531; 31,1%, DOI 10.32895/hcjm.m.2025.11.21) không vào được danh mục TLTK.
    Muốn sửa phải mở rộng hợp đồng biên nhận A12 (có chữ ký): tra rút bài qua Crossref `updated-by`, metadata Crossref,
    đánh số và in trong cả hai bộ sinh. Tách thành PR riêng.

## Việc của người (phiếu đề xuất gửi bác sĩ)

`PHIEU-DE-XUAT-BTM-SAU-GIA-LAP_20261117.md` có 6 mục:
- B1: câu EPV, kèm [38];
- B2: nguồn cho 15,32–31,1%;
- B3: hình thức xét duyệt;
- B4: hiệu chỉnh quần thể hữu hạn cho KTC;
- B5: mục tiêu chung;
- B6: kinh phí.

Agent chỉ đề xuất. Số tham số = 16 đã kiểm là đúng.

## Bài học

- **Dữ liệu mô phỏng phải đi qua ĐÚNG cổng mà dữ liệu thật đi qua.** Sinh từ từ điển G5 của chính đề tài, không sinh từ
  bộ biến phẳng. Lỗi 1–3 không bao giờ lộ với 16 kịch bản cũ, vì khuôn của chúng không có trường calc, checkbox bắt buộc
  hay hồ sơ sàng lọc trong bộ dữ liệu.
- **Diễn tập trên khung thật thì mọi đầu vào «người» cũng phải là của đề tài đó** (G2, tác giả, phản biện, G10).
  Mượn kịch bản mẫu làm hồ sơ sai đi mà không cổng nào bắt.
