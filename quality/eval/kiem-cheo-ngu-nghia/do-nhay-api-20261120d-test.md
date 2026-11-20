# Độ bắt lỗi bộ kiểm ngữ nghĩa Claude API — đột biến tổng hợp tất định (20261120d, prompt 2026-11-20c)

> **Đột biến TỔNG HỢP có nhãn theo cấu trúc — KHÔNG thay bộ vàng do bác sĩ gắn nhãn.** Cùng bộ sinh, cùng hạt giống (20261114) với báo cáo độ nhạy luật cứng `do-nhay-dot-bien-*.md`; luật cứng chấm trên CÙNG đột biến để so cặp. Báo động trên đối chứng là CẬN TRÊN của báo động giả. Công cụ không đổi chế độ chặn.

Model `claude-sonnet-5-5` · mẫu tối đa 40 đột biến/lớp · dashboard PASS 114 · mục apply 822 · mã: `do_nhay_api_ngu_nghia.py` a651203316101141, `kiem_ngu_nghia_api.py` 53d23c4e39527547, `do_nhay_kiem_ngu_nghia.py` 4b3da503f490d594

## TEST (tập giữ lại — số để quyết)

| Lớp đột biến | Trục API | n tính | API bắt | Độ bắt lỗi API (KTC 95%) | Riêng phần nguồn đủ thông tin (KTC 95%; bắt/n) | Luật cứng cùng đột biến (KTC 95%) | **Kết hợp: luật cứng HOẶC API** (KTC 95%) | Chỉ API bắt | Chỉ luật cứng bắt | p McNemar | Lọt ✓ | Lọt ⚪ | Bắt lệch trục | Gốc đã nghi |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| K1 · đổi nhãn quần thể | quần thể | 15 | 13 | 87% (62%–96%) | 86% (60%–96%; 12/14) | 100% (80%–100%) | **100%** (80%–100%) | 0 | 2 | 0.5 | 2 | 0 | 0 | 0 |
| K2 · đổi ngưỡng số trong quần thể | quần thể | 14 | 11 | 79% (52%–92%) | 79% (52%–92%; 11/14) | 100% (78%–100%) | **100%** (78%–100%) | 0 | 3 | 0.25 | 3 | 0 | 0 | 0 |
| K2 · đổi ngưỡng số trong HÀNH ĐỘNG | điều kiện | 5 | 2 | 40% (12%–77%) | 50% (15%–85%; 2/4) | 100% (57%–100%) | **100%** (57%–100%) | 0 | 3 | 0.25 | 2 | 1 | 0 | 6 |
| K3b · rụng điều kiện NGAY TRONG MỤC | điều kiện | 7 | 1 | 14% (3%–51%) | 0% (0%–56%; 0/3) | 0% (0%–35%) | **14%** (3%–51%) | 1 | 0 | 1 | 3 | 3 | 0 | 5 |
| K4 · nguồn nói NGƯỢC chiều mục | chiều | 7 | 0 | 0% (0%–35%) | 0% (0%–35%; 0/7) | 100% (65%–100%) | **100%** (65%–100%) | 0 | 7 | 0.0156 | 7 | 0 | 0 | 0 |
| K4b · mục đảo sang «không làm» | chiều | 13 | 8 | 62% (36%–82%) | 64% (35%–85%; 7/11) | 54% (29%–77%) | **69%** (42%–87%) | 2 | 1 | 1 | 3 | 1 | 1 | 0 |

**Đối chứng (mục gốc, không đột biến):** n = 37 · API nghi ≥ 1 trục 18 (49%; KTC 33%–64%) — theo trục: quần thể 0 · chiều 0 · điều kiện 18 · luật cứng báo 0 (0%). Trả «không đủ thông tin» (null): quần thể 3 · chiều 4 · điều kiện 7.

## Phủ mẫu

| Lớp | Đột biến có sẵn | API không nhìn thấy phần đổi | Đã chọn | Loại vì sinh từ mục phần B (giữ mù) |
|---|---|---|---|---|
| K1 · đổi nhãn quần thể | 49 | 0 | 40 | 8 |
| K2 · đổi ngưỡng số trong quần thể | 35 | 0 | 35 | 4 |
| K2 · đổi ngưỡng số trong HÀNH ĐỘNG | 20 | 0 | 20 | 0 |
| K3b · rụng điều kiện NGAY TRONG MỤC | 604 | 0 | 40 | 6 |
| K4 · nguồn nói NGƯỢC chiều mục | 27 | 0 | 27 | 7 |
| K4b · mục đảo sang «không làm» | 181 | 0 | 40 | 6 |

Ngoài tầm API (không đo): K2_co_mau — API không chấm con số cỡ mẫu · K3_rung_ban_xuat — API không đọc bản xuất.

Cách đọc: «bắt» = trục đích của bản đột biến là false trong khi bản gốc không false; «gốc đã nghi» = API đã phán false trục đó ở bản gốc nên không quy được cho đột biến (loại khỏi mẫu số); «lọt ⚪» = mô hình trả null (không đủ thông tin trong tóm tắt). Chuyển sang CHẶN là quyết định của bác sĩ; bỏ lọt trên lỗi THẬT vẫn cần bộ vàng do bác sĩ gắn nhãn (`tools/bo_vang_kiem_ngu_nghia.py`).

Cần bác sĩ kiểm chứng.
