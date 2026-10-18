# 18/10/2026 — Tầng Unpaywall chỉ xét best_oa_location, bỏ sót bản CC ở kho trường

## Bác sĩ yêu cầu
«127 bản ghi có PMID nhưng chưa có tệp, và 19 bản ghi không có PMID hãy giải quyết toàn văn tất cả cho tôi».

## Đo (chỉ đọc metadata Unpaywall · OpenAlex · Europe PMC cho 129 PMID chưa có tệp)
- 100/129 không có bản mở hợp pháp ở đâu cả — chỉ có bản thuê bao.
- 29/129 có ít nhất một vị trí OA. Trong đó có bài mà vị trí «tốt nhất» Unpaywall chọn là bản không giấy phép của NXB «cấm»,
  còn vị trí khác mang giấy phép mở: PMID 42240859 (Eur J Heart Fail, OUP) — kho Glasgow CC BY-SA; PMID 23095984 (Eur Heart J)
  — kho Auckland CC BY.
- `tang_unpaywall` chỉ đọc `best_oa_location` ⇒ trả «cam_co_uq» cho cả bài, không bao giờ thử vị trí CC.

## Sửa
`tools/gom_toan_van_dashboard.py`:
- `vi_tri_oa_duoc_luu(uj, doi)`: duyệt best rồi mọi `oa_locations` (bỏ trùng URL), mỗi vị trí qua CÙNG `quyet_dinh_unpaywall`
  — không nới cổng; bản không giấy phép của NXB «cấm» vẫn không bao giờ được mở.
- `_tai_vi_tri_upw`: tách phần tải + cổng nội dung của một vị trí; `tang_unpaywall` thử lần lượt, vị trí lỗi mạng hoặc không phải
  toàn văn thì thử vị trí kế, lưu được thì dừng. Không vị trí nào qua cổng ⇒ ghi lý do của vị trí bị chặn đầu tiên như cũ.

## Kiểm
`tools/test_gom_unpaywall_moi_vi_tri_20261018.py` (7 ca); 6 đột biến (chỉ xét best · bỏ cổng · lỗi một vị trí giết cả bài · không
dừng khi đã lưu · dừng ngay sau vị trí đầu · bỏ lý do khi bị chặn) đều đỏ, phục hồi xanh. Test Unpaywall cũ xanh.

## Bài học
Unpaywall chọn «best» theo tiêu chí của họ (ưu tiên bản NXB), không theo giấy phép. Cổng giấy phép phải xét TỪNG vị trí — nếu
không, một bản không giấy phép đứng đầu che mất bản mở hợp lệ đứng sau.
