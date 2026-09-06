# 05. Web Dashboard "Evidence Workbench" cho vấn đề lâm sàng cụ thể

## Phạm vi

Web Dashboard này là đầu ra tra cứu lâm sàng độc lập của một yêu cầu EBM cụ thể. Nó không phải Dashboard Master và không xác nhận thay đổi quy trình đơn vị.

## Mô hình MẶC ĐỊNH: "Evidence Workbench" (3 cột, dày dữ liệu)

Template chuẩn: `templates/web-dashboard-evidence-workbench.html` — chỉ thay khối `DATA = {…}` ở cuối file (đã kèm schema + ví dụ minh hoạ), KHÔNG sửa HTML/CSS.

Bố cục 3 cột (master–detail):

| Cột | Vai trò | Nội dung |
|---|---|---|
| Trái — Bộ lọc | Khoanh vùng nhanh | Facet: Quyết định · Nhóm đặc biệt · Thiết kế · Mức chứng cứ (có số đếm) |
| Giữa — Quick View + Bảng | Tra nhanh & duyệt | Băng `Clinical Quick View` cố định + bảng `ITEM-xx` + tab Chuẩn & chất lượng / An toàn / Chưa đủ thay đổi / Áp dụng VN / Kiểm chứng thao tác |
| Phải — Evidence Detail | Kiểm chứng | Nguồn, ngày/phiên bản, quần thể, PICO, hiệu số (forest), grading, hành động, tham khảo |

Bốn lớp nội dung bắt buộc ánh xạ vào bố cục:

| Lớp | Vị trí | Nội dung |
|---|---|---|
| Clinical Quick View | Băng trên + tab mặc định (cột giữa) | Làm ngay, tránh gì, cờ đỏ, nhóm đặc biệt |
| Evidence Detail View | Cột phải (mở khi click item) | Nguồn, ngày/phiên bản, quần thể, grading, tham khảo |
| Safety / Limits / Vietnam | Các tab riêng (cột giữa) | Chuyển tuyến, chưa đủ đổi thực hành, áp dụng tại Việt Nam |
| Standards / Quality | Tab `Chuẩn & chất lượng` (cột giữa) | Khung câu hỏi, thứ bậc nguồn, chuẩn báo cáo, công cụ thẩm định, độ cập nhật, an toàn, Việt Nam, truy nguyên từng item |

(Mô hình một-cột `Clinical Quick View` cũ chỉ dùng khi bác sĩ yêu cầu riêng hoặc khi chỉ có 1–2 item.)

## Quy tắc record

Mỗi điểm thực hành trong dashboard dùng mã cục bộ `ITEM-01`, `ITEM-02`...; đây chỉ là anchor/nút tra cứu trong file HTML. Không tự ánh xạ sang ID Master.

Trường cốt lõi:

- `local_item_id`
- `clinical_situation`
- `topic`
- `decision`
- `priority`
- `do_now`
- `do_not_do`
- `red_flags_referral`
- `special_populations`
- `document`
- `organization`
- `version_date`
- `population`
- `new_point_or_recommendation`
- `source_grading`
- `operational_assessment_if_used`
- `monitoring`
- `vietnam_application`
- `reference_vancouver_nlm`
- `verification_status`
- `standards.frame`
- `standards.sourceHierarchy`
- `standards.reporting`
- `standards.appraisal`
- `standards.currency`
- `standards.searchSources[]`
- `standards.sourceVerification`
- `standards.lastVerified`
- `standards.verificationTool`
- `standards.safety`
- `standards.vietnamFit`
- `standards.gates[]`

## Hành vi giao diện

- Tab mặc định là `Clinical Quick View` (cột giữa), có băng tóm tắt cố định phía trên.
- Tab `Chuẩn & chất lượng` bắt buộc có để rà PICO/PECO/PIRD/PROGRESS, nguồn tìm kiếm, CONSORT/STROBE/PRISMA/STARD/TRIPOD, AGREE II/AMSTAR 2/RoB 2/ROBINS-I/QUADAS-3 v1.2/PROBAST/JBI (QUADAS-2 chỉ để đọc nghiên cứu lịch sử), trạng thái `verify_dashboard.py --online --strict-sources` và truy nguyên từng item.
- Bộ lọc facet (cột trái) theo Quyết định / Nhóm đặc biệt / Thiết kế / Mức chứng cứ, có số đếm.
- Tìm kiếm toàn cục hoạt động trên tình huống, thuốc, hành động, nhóm nguy cơ và nguồn.
- Click một dòng `ITEM-xx` → mở panel `Evidence Detail View` ở cột phải.
- Có nút xuất `CSV` và `JSON` cho các item đang lọc.
- Dữ liệu “Chưa đủ để thay đổi thực hành” đặt ở tab/cột riêng, không hiển thị như hành động áp dụng.
- Khu vực tích hợp Master chỉ xuất hiện khi yêu cầu có mục tiêu quản trị.
- Dashboard phải hữu dụng ngay khi mở, không buộc tải Excel trước.

### Ánh xạ trường record → khoá trong template

`do_now`/`do_not_do`/`red_flags_referral` → `summary.doNow/dontDo/redFlags`; `decision` → `item.decision` (`apply`/`consider`/`notyet`); `source_grading` → `item.gradeSource` (+ `gradeLevel` để tô màu); `document`/`organization`/`version_date`/`population` → `item.source`/`org`/`dateVersion`/`population`; `monitoring`/`vietnam_application` → `item.monitoring`/`vn`; `reference_vancouver_nlm` → `item.references[]`; `local_item_id` → `item.id`; chuẩn cập nhật chứng cứ → `standards.frame/sourceHierarchy/reporting/appraisal/currency/searchSources/sourceVerification/lastVerified/verificationTool/safety/vietnamFit/gates`.

## Kiểm soát độ tin cậy

- Nội dung trên Dashboard phải khớp câu trả lời EBM đã xác minh.
- Không đưa liều, cut-off, thời gian điều trị hoặc thay đổi nhãn vào Dashboard nếu chưa được xác minh trong nguồn.
- Phân biệt grading của nguồn và nhận định vận hành.
- Ghi rõ ngày/phiên bản cho nguồn chính.
- Ghi rõ ngày tìm kiếm, thứ bậc nguồn, chuẩn báo cáo và công cụ thẩm định trong `DATA.standards`.
- Chỉ phát hành khi `python3 tools/verify_dashboard.py <dashboard>.html --online --strict-sources` PASS.
- Không phát hành nếu tab `Chuẩn & chất lượng` còn cổng `need` mà chưa giải thích hoặc chưa chuyển thành `[CẦN KIỂM CHỨNG]`.

## Kiểm chứng khả dụng

Mục tiêu thao tác:

| Tác vụ | Thời gian mục tiêu |
|---|---:|
| Tìm hành động chính | ≤30 giây |
| Tìm cờ đỏ/chuyển tuyến | ≤30 giây |
| Tìm nhóm đặc biệt | ≤30 giây |
| Mở nguồn/ngày cập nhật | ≤60 giây |
| Rà chuẩn & chất lượng trước phát hành | ≤60 giây |
