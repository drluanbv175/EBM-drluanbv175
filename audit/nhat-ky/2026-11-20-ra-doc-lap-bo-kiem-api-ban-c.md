# 20/11/2026 — Rà độc lập PR #447/#448: cổng quyền `_UPW` mở lọt, rò phần B vào số đo; JBDS và bảng; bản c

**Bối cảnh.** Bác sĩ (20/11/2026): «Giải quyết tất cả các vấn đề trên cho tôi một cách tốt nhất». Trước khi gộp, một agent ĐỘC LẬP, CHỈ ĐỌC đã rà PR #447 và #448. Trong lúc đó bác sĩ đã gộp #447, #448 (mới phần đầu, `645eb817`) và #449. Commit đo độ bắt lỗi + prompt v2 (`dc32d48c`) được đẩy lên SAU khi #448 gộp, nên phải cherry-pick sang nhánh mới `claude/api-do-bat-loi-v2-20261120`. Repo gốc nay gộp kiểu squash, đúng bài học 14/11.

**Lỗi chặn gộp — cổng quyền `_UPW` mở lọt.**
- `quyen_gui_toan_van` coi mọi tệp `_UPW` là có giấy phép mở chỉ vì TÊN tệp. Nhật ký 04/10 lại ghi kho còn 32 tệp `_UPW` cũ không giấy phép mở.
- Ca thật: PMID 17005808 (ASM, NXB chưa kiểm điều khoản) sẽ bị gửi đi.
- Đã kiểm các lượt đo hôm nay: chỉ có 3 tệp `_UPW` không giấy phép CC từng được chọn gửi — Lancet/Elsevier, Cochrane/Wiley, ADA. Cả ba NXB đều **còn uỷ quyền đọc của bác sĩ** (03–04/10), nên KHÔNG có nội dung nào ra ngoài phạm vi uỷ quyền.
- Vá:
  - `_UPW` chỉ được gửi khi chính tệp mang giấy phép Creative Commons; không thì xét như bản Chrome (NXB «cấm» cần uỷ quyền lúc gọi; NXB khác không gửi).
  - Bỏ nhánh `TDM_CHO_PHEP_LUU`, vì bảng đó tự khai chỉ dành cho phiên lưu bản sao. Gửi cho API cần bác sĩ quyết riêng.

**Lỗi nên sửa — đã vá.**
1. **Giữ mù.**
   - `kiem_ngu_nghia_api.py --goi-api` nay mặc định KHÔNG chấm mục thật chờ nhãn; muốn chấm phải bật cờ `--ca-muc-cho-nhan`.
   - Đính chính: lượt 19/11 chạy không lọc, nên bộ đệm đã có kết quả v1 cho cả 40 mục phần B. Kết quả này chưa từng được in cho bác sĩ.
   - Số đo loại 31 đột biến sinh từ chính mục phần B (theo PMID cộng hành động, hoặc theo dashboard cộng id).
   - Bước xuất gói khi thiếu bộ vàng thì không gọi (fail-closed).
2. **Cảm biến hòm việc** không còn sập khi báo cáo chỉ có tập DEV, và ưu tiên báo cáo có tập TEST. Tên báo cáo kèm tập (`-test`/`-dev`) để lượt DEV không đè lượt TEST. Việc đo tính phí đổi từ 🛎 sang 👤.
3. **Test không ghim giá trị chính sách.** Bác sĩ đặt `false` thì không làm CI đỏ.
4. **#447 `doc_nguon_chinh_thuc.py`:**
   - lỗi bất kỳ của một nguồn (PDF hỏng, `IncompleteRead`) không giết cả lượt;
   - PMC/Bookshelf (`ncbi.nlm.nih.gov`) không còn là «miền nhà nước giấy phép mở»;
   - `mien_cua` dùng hostname, không bị lừa bởi `cdc.gov:x@evil.example`;
   - không đi theo chuyển hướng sang miền không được phép tải;
   - DOI dạng URL vẫn nhận ra NXB.
5. **Bước ④-quinquies:** công cụ con sập (không có dòng «Tổng:») thì báo «không chạy xong», không đọc thành «API nghi»; thêm giới hạn 1800 giây.

**JBDS — khuyến nghị của tôi SAI, đã không ghi.**
- Khi phân xử 8 bất đồng, tôi khuyên đổi mục 17 (JBDS) sang S vì chỉ đọc đoạn văn xuôi «típ 2 giảm 35–50%».
- Lịch sử nhãn (20/10) và **Bảng 2/5** của toàn văn cho thấy mục khớp nguồn: Bảng 2 ghi típ 2 giảm 50% tổng liều khi bắt đầu chế độ ăn giảm thể tích gan; Bảng 5 ghi típ 1 giảm 30–50% và không bao giờ ngừng insulin.
- Bác sĩ chọn «theo khuyến nghị», nhưng tôi KHÔNG ghi mục 17 và KHÔNG sửa mục JBDS trên dashboard. Đã ghi S (trục điều kiện) cho mục 1, 11, 12, 16; giữ Đ cho mục 6, 10, 13, 17.
- Bài học: bộ chọn đoạn toàn văn bỏ qua BẢNG ⇒ thêm dòng bảng (`PHIEN_BAN_CO_BANG`, prompt `2026-11-20c`, nay là mặc định). Bản b giữ nguyên để số cũ tái lập được.

**Thiên lệch hợp nhất.** 4 nhãn ở mục 1–20 được sửa SAU khi xem phán quyết của API, nên số đo trên 20 mục này là «đồng thuận sau phân xử», không độc lập. Tập kiểm độc lập duy nhất trên lỗi thật là 40 mục phần B (bác sĩ gắn nhãn).

**Số đo bản c** (20/11; chi phí đo cả ngày khoảng 5 USD):
- 56 đột biến bác sĩ đã duyệt: quần thể 22/22, chiều 17/18, điều kiện 13/16. Luật cứng cùng tập: 4/22, 2/18, 0/16.
- 20 mục thật đã phân xử: trục điều kiện bắt 5/5, báo giả 5/13; trục chiều báo giả 0/20.
- Tập TEST tổng hợp (đã loại phần B, n nhỏ), xem `do-nhay-api-20261120-test.md`.

**Việc khác cùng ngày.**
- Sửa mục Beers ở `WebDashboard_EBM_CapNhatTuan_NgoaiTru_20260609.html` ITEM-04: tránh MỌI sulfonylurea theo Beers 2023. Có sao lưu `.bak-20261120-beers-sulfonylurea`; cổng `--online` qua; bộ năm 5/5.
- Mục HS: bản mới nhất 07/11 đã đúng, nên không sửa.

**Kiểm hồi quy.**
- Test mới/sửa trong 6 tệp test.
- Kiểm đột biến 15/15 bắt (V1–V15: cổng `_UPW` ×2, nhánh TDM, loại phần B, giữ mù mặc định, thiếu bộ vàng, cảm biến DEV ×2, nhãn 👤, sập ≠ nghi, PMC, chuẩn hoá DOI, hostname, chuyển hướng, lỗi lạ).
