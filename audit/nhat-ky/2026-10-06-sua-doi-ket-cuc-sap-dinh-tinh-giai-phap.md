# 06/10/2026 — Đường sửa đổi kết cục chính (G10-07) · SAP định tính · hội đồng đưa ra giải pháp tốt nhất

Ba quyết định bác sĩ giao cùng ngày: «Hội đồng cổng đưa ra những giải pháp tốt nhất»; «Đường sửa đổi kết cục chính
(G10-07) hãy giải quyết một cách triệt để tốt nhất»; «SAP định tính có thêm dòng «Kết cục chính:» hãy giải quyết theo
hướng tốt nhất».

## 1. G10-07 — sửa đổi kết cục chính có kiểm chứng

**Trước:** lệch kết cục chính giữa các cổng chỉ có MỘT lối ra — xác nhận «cùng một kết cục, khác diễn đạt». Đổi kết
cục THẬT (có lý do) thì không có đường: hoặc nói sai «cùng kết cục», hoặc kẹt REVIEW mãi.

**Chuẩn đã tra trực tuyến:**
- CONSORT 2025 mục 10 «Important changes to the trial after it commenced including any outcomes or analyses that were
  not prespecified, with reason» (PMID 40228477, doi:10.1371/journal.pmed.1004587, tra PubMed/PMC 06/10/2026).
- SPIRIT 2025 mục 31 (kế hoạch truyền đạt sửa đổi đề cương quan trọng; PMID 40294593 — đã xác minh, có trong
  `protocol_checklist_items.py`).

**Vá (y khoa):** `gate_params.G10.sua_doi_ket_cuc_chinh` (danh sách theo thời gian). Mỗi lần sửa gồm:
- kết cục cũ → mới;
- lý do ≥ 30 ký tự;
- mã sửa đổi đề cương;
- ngày;
- Hội đồng đạo đức chấp thuận;
- đăng ký cập nhật (kèm ngày);
- PI xác nhận.

Lần cuối gắn dấu vân tay; tới bản thảo thì thêm vị trí công bố.

Hợp lệ khi đủ cả các điều kiện sau ⇒ «cần xem» (hiện ra, không chặn):
- chuỗi nối tiếp và theo thời gian;
- mọi nơi ghi thuộc chuỗi;
- SAP §2 và khai báo G8 là kết cục MỚI nhất. G0/G1/bản nháp đăng ký được giữ kết cục cũ — không sửa ngược hồ sơ cổng;
- sửa TRƯỚC ngày khoá dữ liệu (cùng ngày ⇒ hậu kiểm, thận trọng);
- bản thảo G7 có câu nêu kết cục cũ + «thay đổi/sửa đổi».

Thiếu bất kỳ điều nào ⇒ lệch mềm kèm lý do. Đề cương G10 in bảng «Sửa đổi kết cục chính».

## 2. SAP định tính — dòng «Kết cục chính:»

**Đo:** khuôn SAP đã CÓ dòng «Kết cục chính:» cho mọi thiết kế. Vấn đề thật nằm ở nghĩa và ở các bộ đọc:
- **Khuôn:** ví dụ định lượng («tỷ lệ nhập viện…») và các dòng đơn vị/ngưỡng/an toàn không hợp với định tính.
- **G6-AUTO-04:** đòi tên biến kết cục (định tính không có ⇒ phải bịa).
- **G8-AUTO-05:** chỉ nhận bản thảo có cụm «kết cục chính».
- **Hàm rút biến của G6 — hai lỗi tiềm ẩn lộ thêm:**
  - đọc thẳng hai dòng kế nên lấy NHẦM biến của «Kết cục phụ 1»;
  - nhận cả câu chỉ NHẮC «kết cục chính» là dòng khai — dòng diễn giải «(SRQR, …)» thành biến `srqr`.

**Vá (y khoa):**
- SAP định tính điền sẵn «Kết cục chính:» = hiện tượng/câu hỏi nghiên cứu đã chốt ở G1, kèm dòng diễn giải (SRQR); đơn
  vị/ngưỡng, an toàn KHÔNG ÁP DỤNG.
- G6: chỉ nhận dòng có NHÃN đứng đầu; chỉ đọc dòng nối tiếp; định tính không đòi biến.
- G8: nhận «câu hỏi/hiện tượng/mục tiêu nghiên cứu» với định tính, kể cả ở chỗ gọi.

## 3. Hội đồng cổng — giải pháp tốt nhất

Hội đồng giữ vai TƯ VẤN, không chặn cổng. Phán quyết trọng tài BẮT BUỘC `giai_phap_tot_nhat`:
- phương án khuyến nghị cụ thể + căn cứ kiểm được;
- sửa kết luận/chuyển bác sĩ ⇒ thêm ≥ 1 phương án khác kèm lý do không chọn.

Công cụ (biên bản v2) từ chối ghi khi thiếu căn cứ, có PII hoặc viết như trạng thái cổng. Biên bản và bàn giao in giải
pháp. Lộ thêm và vá luôn: `thoi_diem` biên bản cắt về giây ⇒ hai biên bản cùng giây chọn «mới nhất» theo đuôi băm
(test chập chờn ~50%) — nay giữ micro giây, sắp theo mốc thời gian thật.

## Kiểm

- Y khoa: `tests/test_sua_doi_ket_cuc_va_sap_dinh_tinh_20261006.py` (18 test) và `test_hoi_dong_cong` +5.
- Đột biến:
  - kết cục + SAP định tính: 28/28 (26 + bù 2/2);
  - hội đồng: 10/10.
- Gốc: workflow `hoi-dong-cong.js` (lược đồ `GIAI_PHAP`, kiểm cú pháp node); 8 agent dạy luật mới; toàn bộ `tools/` 2654
  qua.
- Toàn bộ bộ test y khoa: ghi ở PR.
