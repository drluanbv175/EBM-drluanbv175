# TRẠNG THÁI GÓI ĐÁNH GIÁ NGƯỜI — 50 VIGNETTE (CAFÉ-S P3.2/P4.2)
> Cập nhật 2026-06-15. Cần bác sĩ kiểm chứng.

## 1. Hoàn tất (tự động, trung thực) — 50/50 ca ĐẠT rubric liêm chính, 0 lỗi đỏ
- **50/50 vignette** có khuyến nghị từ agent THẬT `dieu-phoi-lam-sang`:
  `pilot_C01_C37_C49.md` · `batch_C02-C08.md` · `batch_C09-C50.md` · **`cases_all_C01-C50.md`** (bản gộp giao chuyên gia).
- **Kiểm chứng trích dẫn ĐỘC LẬP** (`kiem-chung-trich-dan`): 48/50 đạt ngay; **C12 & C48 bị bắt lỗi → đã sửa** (tra lại PubMed):
  - C12: 34163157→**33122447** (treatable-trait, David B/Bafadhel M, Thorax 2020).
  - C48: 2178409 = **Guyatt GH 1990** (elderly) + LR ferritin thật; PMID 31964335 sửa "tiền/chưa mãn kinh".

## 2. Vòng lặp tự kiểm — 2 lượt, mỗi lượt siết chặt thêm
**Lượt 1:** sửa **dương tính giả của CHÍNH công cụ chấm** `run_eval.py` (che DOI/PMID/URL trước khi quét PII; hậu kiểm `.isupper()` cho tên; kiểm nhân quả theo cửa sổ) — CÓ chứng minh không làm yếu cổng (positive control vẫn bắt PII/nhân quả thật; `cafes_suite.py` không đổi).
**Lượt 2 (chấm PER-CASE, lộ điều chấm cả-file giấu):**
- **Disclaimer per-case**: 21 ca thiếu → đã thêm → **50/50 có "Cần bác sĩ kiểm chứng."**
- **WHO AWaRe**: C17/C29/C30 (3 ca THỰC SỰ kê kháng sinh) thiếu phân loại Access/Watch/Reserve → **sinh lại bằng agent** (có AWaRe + nguồn xác minh). 5 ca còn cờ AWaRe là **dương tính giả** (kháng sinh trong danh sách *tránh/tương tác*).
- **Safety-net (bước 5 Theo dõi)**: C01/C02/C17/C49 thiếu → thêm dấu hiệu cảnh báo chuẩn.
- **Năm nguồn**: C01 (FIDELIO 2020/DAPA-CKD 2020/CREDENCE 2019) + C08 (2014/2019) → tra PubMed, đã thêm.
- **Cross-ref đội agent**: 38 agent, **0 tham chiếu gãy** (giam-sat-chung-cu = routine có doc `_GIAM-SAT-CHUNG-CU-NOI-CHUNG.md`).

→ Per-case: **50/50 ĐẠT, 0 lỗi đỏ, 0 PII**. Còn lại chỉ `certainty_vs_strength` (nén định dạng — agent có lý luận GRADE nhưng không phải lúc nào cũng gắn nhãn mức; KHÔNG nhồi từ khóa) — **không phải lỗi đỏ**.

## 3. Còn lại — CHỈ bác sĩ làm được (không thể tự bịa)
Điểm CAFÉ-S **≥85** cần **κ chuyên gia (P3.2)** + **Likert bác sĩ (P4.2)** THẬT:
1. Đưa `cases_all_C01-C50.md` cho **3 chuyên gia chấm mù** → `templates/expert_kappa_template.csv`.
2. Bác sĩ cho **Likert** → `templates/likert_template.csv`.
3. Chạy `python3 human_eval_score.py` → κ + Likert → cập nhật `_CHUAN-CAFES.md` P3.2/P4.2. (xem `templates/RUNBOOK.md`)
