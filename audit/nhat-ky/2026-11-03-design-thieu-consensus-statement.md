# 03/11/2026 — Bộ lọc loại thiết kế của bộ quét loại im lặng mọi «Consensus Statement» ở tầng guideline (BH178)

**Mã:** BH178 (ban đầu ghi BH176; đổi cùng ngày vì PR #288 gộp trước đã dùng BH176 và BH177 — chốt BH68 bắt trùng). **Phát hiện:** phiên đưa chủ đề «Rung nhĩ ở người có stent mạch vành» vào watchlist (03/11). ESC ACS 2023
(PMID 37622654) chỉ được PubMed gán «Journal Article» nên tầng guideline lọt mất. Rà tiếp toàn watchlist thì gặp một lỗ lớn hơn.

## Chuyện gì đã xảy ra

`surveillance_scan.search()` AND hằng `DESIGN` vào mọi tầng có `loc_thiet_ke: true` (57/58 tầng guideline, mọi tầng sr_ma/rct).
`DESIGN` gồm Guideline · Practice Guideline · Systematic Review · Meta-Analysis · RCT, nhưng **không có `"consensus statement"[ptyp]`**.
Đây là loại đồng thuận hiện hành của PubMed (NLM đã bỏ `consensus development conference`, xem CLAUDE.md §6.4). Mọi truy vấn tầng
guideline đều tự khai `"consensus statement"[pt]`, và `khoa_manh_nhat` xếp loại này ngang guideline (điểm 5). Bộ lọc AND thêm vào
lại loại bỏ đúng nhóm bản ghi đó: bản ghi chỉ mang «Consensus Statement», không kèm «Guideline», bị loại không một dòng báo.
Đường dự phòng Europe PMC có cùng lỗ (`PUB_TYPE` không có consensus statement).

## Đo (03/11/2026, PubMed sống, cửa sổ pdat 01/11/2023–03/11/2026, 58 chủ đề có tầng)

- Truy vấn tầng guideline khớp nhưng `DESIGN` loại: **792 bản ghi**. Lấy mẫu tối đa 300 bản/chủ đề thì 759 bản có tiêu đề
  kiểu guideline/consensus/statement/recommendation. Ví dụ: ESC ACVC «clinical consensus statement» về viêm trong hội chứng
  vành (PMID 42536391), SCAI statement nong bóng động mạch phổi (42055655), position statement thiếu máu KDIGO 2026 của SEN
  (42414122), đồng thuận đái tháo đường thận Ấn Độ (42543958).
- Nhiều nhất: ĐTĐ type 2 101 (phần lớn là các phần ADA Standards of Care chỉ mang «Journal Article», thuộc lớp lỗi thứ hai dưới),
  Mạch vành 96, CKD 60, Nốt và u phổi 56, Cấp cứu ban đầu 45, Hen 39.
- Tầng sr_ma/rct: 58/58 truy vấn tự giới hạn bằng `[pt]` của chính nó ⇒ thêm loại vào `DESIGN` không đổi kết quả hai tầng đó.

## Lớp lỗi thứ hai, KHÔNG vá trong PR này (là truy vấn, cần bác sĩ duyệt)

13 chủ đề có heuristic tiêu đề trong tầng guideline: ĐTĐ type 2 (`Standards[ti] AND Care[ti] AND Diabetes[ti]`), 3 chủ đề nốt/u
phổi và 9 lát cắt Sleep Psychiatry (`guideline*[ti] OR consensus[ti] OR recommendation*[ti] OR statement[ti]`). `DESIGN` chỉ
xét `[ptyp]` nên vô hiệu hoá các heuristic này: guideline chỉ mang «Journal Article» vẫn bị loại. Cách chữa theo từng chủ đề là
đặt `loc_thiet_ke: false` ở tầng guideline, như chủ đề Rung nhĩ đã làm. Đây là đổi phạm vi truy vấn, nên máy chỉ soạn
`watchlist.de-xuat.json` để bác sĩ duyệt, rồi `tools/ap_dung_de_xuat_watchlist.py`.

## Vá

- `DESIGN` thêm `"consensus statement"[ptyp]`; `search_europe_pmc` thêm `PUB_TYPE:"consensus statement"` (đo sống: Europe PMC
  gán pubType «Consensus Statement» cho 42372819 và 42536391; truy vấn `PUB_TYPE:"consensus statement"` trả 408 bản 01–03/2026).
- Hai bản trong git (`cap-nhat-chung-cu-y-khoa`, `dark-analyst`) chép trùng khít; bản runtime `EBM-Dashboards/tools/` đồng bộ
  bằng `tools/dong_bo_scanner_giam_sat.py --ap-dung` sau khi gộp.
- `kiem_san_luong_giam_sat.py` nạp `DESIGN` từ nguồn chuẩn nên tự theo, không cần sửa.

## Kiểm hồi quy

- `tools/test_surveillance_scan_design_consensus_20261103.py` (4 test). Test kiểm HÀNH VI: chuỗi `term` thật gửi NCBI, truy vấn
  thật gửi Europe PMC, tầng không lọc giữ nguyên, và mọi loại điểm 5 của bảng xếp hạng đều qua bộ lọc.
- Đột biến (`python -B`, xoá `__pycache__`, sao lưu + `cmp`): bỏ loại ở `DESIGN` ⇒ 2 test đỏ; bỏ ở Europe PMC ⇒ 1 đỏ; phục hồi ⇒
  4 xanh. Bộ test bộ quét hiện có: 314 qua, 2 bỏ qua.
- Chốt `BH178` trong `tools/chot_hoi_quy_bai_hoc.py` (ngoại tuyến).
