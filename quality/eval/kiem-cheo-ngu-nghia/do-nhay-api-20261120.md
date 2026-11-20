# Độ bắt lỗi bộ kiểm ngữ nghĩa Claude API — đột biến tổng hợp tất định (20261120, prompt 2026-11-20b)

> **Đột biến TỔNG HỢP có nhãn theo cấu trúc — KHÔNG thay bộ vàng do bác sĩ gắn nhãn.** Cùng bộ sinh, cùng hạt giống (20261114) với báo cáo độ nhạy luật cứng `do-nhay-dot-bien-*.md`; luật cứng chấm trên CÙNG đột biến để so cặp. Báo động trên đối chứng là CẬN TRÊN của báo động giả. Công cụ không đổi chế độ chặn.

Model `claude-sonnet-5-5` · mẫu tối đa 40 đột biến/lớp · dashboard PASS 114 · mục apply 822 · mã: `do_nhay_api_ngu_nghia.py` e247c0349cc7597f, `kiem_ngu_nghia_api.py` f5f4b4f906863cb2, `do_nhay_kiem_ngu_nghia.py` 7815459a11fbe7a9

## TEST (tập giữ lại — số để quyết)

| Lớp đột biến | Trục API | n tính | API bắt | Độ bắt lỗi API (KTC 95%) | Riêng phần nguồn đủ thông tin (KTC 95%; bắt/n) | Luật cứng cùng đột biến (KTC 95%) | **Kết hợp: luật cứng HOẶC API** (KTC 95%) | Chỉ API bắt | Chỉ luật cứng bắt | p McNemar | Lọt ✓ | Lọt ⚪ | Bắt lệch trục | Gốc đã nghi |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| K1 · đổi nhãn quần thể | quần thể | 17 | 14 | 82% (59%–94%) | 81% (57%–93%; 13/16) | 100% (82%–100%) | **100%** (82%–100%) | 0 | 3 | 0.25 | 3 | 0 | 0 | 0 |
| K2 · đổi ngưỡng số trong quần thể | quần thể | 15 | 12 | 80% (55%–93%) | 80% (55%–93%; 12/15) | 100% (80%–100%) | **100%** (80%–100%) | 0 | 3 | 0.25 | 3 | 0 | 0 | 0 |
| K2 · đổi ngưỡng số trong HÀNH ĐỘNG | điều kiện | 6 | 2 | 33% (10%–70%) | 67% (21%–94%; 2/3) | 0% (0%–39%) | **33%** (10%–70%) | 2 | 0 | 0.5 | 2 | 2 | 0 | 5 |
| K3b · rụng điều kiện NGAY TRONG MỤC | điều kiện | 11 | 1 | 9% (2%–38%) | 17% (3%–56%; 1/6) | 0% (0%–26%) | **9%** (2%–38%) | 1 | 0 | 1 | 5 | 5 | 0 | 7 |
| K4 · nguồn nói NGƯỢC chiều mục | chiều | 11 | 2 | 18% (5%–48%) | 18% (5%–48%; 2/11) | 100% (74%–100%) | **100%** (74%–100%) | 0 | 9 | 0.00391 | 8 | 0 | 1 | 0 |
| K4b · mục đảo sang «không làm» | chiều | 15 | 8 | 53% (30%–75%) | 54% (29%–77%; 7/13) | 13% (4%–38%) | **67%** (42%–85%) | 8 | 2 | 0.109 | 5 | 1 | 1 | 0 |

**Đối chứng (mục gốc, không đột biến):** n = 48 · API nghi ≥ 1 trục 22 (46%; KTC 33%–60%) — theo trục: quần thể 0 · chiều 1 · điều kiện 22 · luật cứng báo 0 (0%). Trả «không đủ thông tin» (null): quần thể 3 · chiều 6 · điều kiện 9.

## Phủ mẫu

| Lớp | Đột biến có sẵn | API không nhìn thấy phần đổi | Đã chọn |
|---|---|---|---|
| K1 · đổi nhãn quần thể | 49 | 0 | 40 |
| K2 · đổi ngưỡng số trong quần thể | 35 | 0 | 35 |
| K2 · đổi ngưỡng số trong HÀNH ĐỘNG | 20 | 0 | 20 |
| K3b · rụng điều kiện NGAY TRONG MỤC | 601 | 0 | 40 |
| K4 · nguồn nói NGƯỢC chiều mục | 27 | 0 | 27 |
| K4b · mục đảo sang «không làm» | 181 | 0 | 40 |

Ngoài tầm API (không đo): K2_co_mau — API không chấm con số cỡ mẫu · K3_rung_ban_xuat — API không đọc bản xuất.

Cách đọc: «bắt» = trục đích của bản đột biến là false trong khi bản gốc không false; «gốc đã nghi» = API đã phán false trục đó ở bản gốc nên không quy được cho đột biến (loại khỏi mẫu số); «lọt ⚪» = mô hình trả null (không đủ thông tin trong tóm tắt). Chuyển sang CHẶN là quyết định của bác sĩ; bỏ lọt trên lỗi THẬT vẫn cần bộ vàng do bác sĩ gắn nhãn (`tools/bo_vang_kiem_ngu_nghia.py`).

Cần bác sĩ kiểm chứng.
