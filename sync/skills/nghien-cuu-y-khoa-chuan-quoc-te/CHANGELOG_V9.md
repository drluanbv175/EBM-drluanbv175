# Cập nhật v9 (nội dung 5.3) — 2026-07-06

Đợt bảo trì theo `workflows/08`: làm giàu `templates/01_mau_de_cuong_tong_the.md`. Không thay đổi khung phương pháp, cổng chất lượng G0-G9, số lượng/tên mục cấp 1 của template hay bộ kiểm thử.

## Báo cáo phát hành tối thiểu (theo workflow 08)

- **Phiên bản:** nội dung 5.3 (CHANGELOG v9).
- **Ngày:** 2026-07-06.
- **Người chỉnh sửa:** bảo trì tự động qua Claude (soạn bằng workflow đa agent — 2 bản thảo độc lập + tổng hợp); tác giả con người kiểm chứng và chịu trách nhiệm.
- **File đã thay đổi:**
  - `templates/01_mau_de_cuong_tong_the.md` — thêm nội dung hướng dẫn/bẫy thường gặp dưới mỗi mục (16 mục cấp 1 + khối kiểm soát + Phụ lục giữ nguyên tên/số lượng).
  - `MANIFEST.md` — bump phiên bản 5.2 → 5.3, ngày 2026-07-06.
  - `CHANGELOG_V9.md` — tệp này.

## Nội dung được bổ sung và nguồn

Nguồn là một ca xử lý thực tế trong hệ agent nghiên cứu song song của dự án (đề tài khảo sát hài lòng người bệnh ngoại trú): đề cương từng xây dựng trên giả định dùng nguyên trạng một thang đo chuẩn quốc gia (chưa xác minh được toàn văn qua 3 vòng phản biện), khi có bản phiếu khảo sát + codebook thật thì công cụ hoàn toàn khác (bộ câu hỏi tự xây dựng, có mục hỏi trực tiếp độc lập về kết cục chung) — phải viết lại phần lớn đề cương. 5 bài học rút ra và vị trí lồng vào template:

| # | Bài học | Mục template |
|---|---|---|
| 1 | Xác minh CRF/công cụ thu thập thật trước khi giả định dùng thang chuẩn | 9. Công cụ và quy trình thu thập |
| 2 | Ưu tiên mục hỏi trực tiếp/độc lập làm kết cục chính khi có sẵn (tránh thiên lệch phần-toàn thể) | 7. Biến số và kết cục; 12. Sai lệch và kiểm soát |
| 3 | Codebook đã tự dựng sẵn là nguồn sự thật, đối chiếu trước khi tự suy luận phương pháp khác | 10. Quản trị dữ liệu và bảo mật |
| 4 | Trường định danh nội bộ (đối soát/chống trùng) phải tách khỏi bộ dữ liệu bàn giao phân tích | 10. Quản trị dữ liệu và bảo mật |
| 5 | Miền/thang con 1-2 mục không báo cáo Cronbach's alpha như một thang đầy đủ | 9. Công cụ và quy trình thu thập |

Đây là bài học phương pháp luận đúc kết từ thực hành, không phải văn bản pháp quy/chuẩn báo cáo mới — không có PMID/DOI/số hiệu văn bản cụ thể để trích dẫn cho chính bài học này (khác với các đợt cập nhật trước vốn tái kiểm chứng văn bản pháp luật).

## Kết quả script kiểm tra

- `python scripts/validate_skill.py` → **ĐẠT**: "cấu trúc skill và các tài liệu bắt buộc hợp lệ."
- `python scripts/run_static_evaluations.py` → **ĐẠT**: "gói skill bao phủ các neo nội dung an toàn, phương pháp và kiểm thử bắt buộc."

## Rủi ro còn tồn tại

- Nội dung hướng dẫn mới trong template là bổ trợ diễn giải (không phải quy tắc pháp lý) — vẫn cần chủ nhiệm/nhà thống kê đề tài rà soát áp dụng đúng bối cảnh từng nghiên cứu cụ thể, không áp dụng máy móc.
- Kiểm tra tĩnh không thay thế kiểm thử hành vi của Claude sau upload và rà soát chuyên gia (theo `quality/02_ca_kiem_thu_dau_ra.md`).

## Không thay đổi

- Khung cổng chất lượng G0-G9, cấu trúc progressive disclosure, `SKILL.md`, các module/workflow/reference/quality và bộ kiểm thử giữ nguyên. Số lượng/tên 16 mục cấp 1 + khối "Thông tin kiểm soát" + "Phụ lục" của template giữ nguyên — chỉ thêm nội dung hướng dẫn dưới các tiêu đề đã có.
