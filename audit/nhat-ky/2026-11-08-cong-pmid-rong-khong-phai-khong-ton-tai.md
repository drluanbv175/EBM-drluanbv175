# 08/11/2026 — Cổng verify_dashboard chặn giả: PubMed trả JSON thiếu bản ghi bị đọc thành «PMID không tồn tại»

**Phát hiện:** lô xuất lại bộ năm 32 dashboard (bác sĩ «Tiếp tục hoàn thiện các vấn đề còn lại») chạy song song lượt gom «vượt
qua» (`state/gom-vuot-qua-day-du-20261108.py`) và `dat_canh_chung_cu_moi.py` — ba tiến trình cùng gọi NCBI. Cổng `--online
--strict-sources` CHẶN CỨNG (mã 3) `Gout_NgoaiTru_20261105`: «[ITEM-09] PMID 20131255 KHÔNG phân giải: không có trong PubMed»,
«[ITEM-10] PMID 34882311 …». Tra lại qua connector PubMed: cả hai có thật (Terkeltaub, Arthritis Rheum 2010, colchicine liều
thấp/cao — doi:10.1002/art.27327; Cochrane NSAID cho gout cấp 2021 — doi:10.1002/14651858.CD010120.pub3).

**Gốc:** `verify_pmid_online` trả `False` («không có trong PubMed» ⇒ lỗi cứng, không phải lỗi mạng) cho MỌI phản hồi HTTP 200 mà
JSON không chứa bản ghi có `title` của PMID. Đo thật cùng ngày: PMID không có thật (99999999) ⇒ NCBI trả
`{"result": {"uids": ["99999999"], "99999999": {"uid": …, "error": "cannot get document summary"}}}`; PMID có thật ⇒ bản ghi có
`title`. Phản hồi lúc quá tải/giới hạn tần suất (JSON thiếu bản ghi, `{"error": "API rate limit exceeded"}`) rơi vào nhánh False.

**Vá** (`sync/skills/cap-nhat-chung-cu-y-khoa/tools/verify_dashboard.py`, đồng bộ byte sang `sync/skills/dark-analyst/tools/`;
hai bản chạy ngoài git `EBM-Dashboards/tools/` và `EBM_MASTER/skill_assets/` chép sau khi gộp):
- `False` CHỈ khi bản ghi của đúng PMID mang `error` (NCBI từ chối rõ) VÀ Europe PMC cũng không thấy.
- JSON thiếu bản ghi/không có `result` ⇒ nhánh lỗi tạm thời đã có: thử lại có giãn, Europe PMC dự phòng, cuối cùng `None`
  («không xác minh được» — fail-closed, không có `--verified`), KHÔNG BAO GIỜ `False`.

**Kiểm:** `tools/test_verify_dashboard_pmid_rong_20261108.py` (7 ca, mạng giả). Đối chứng bản cổng cũ: 5/7 đỏ (thiếu bản ghi ·
vượt giới hạn tần suất · từ chối rõ nhưng Europe PMC thấy · thiếu bản ghi nhưng Europe PMC thấy · đồng bộ byte). Bộ test có nhắc
`verify_dashboard`: 648 đạt, 3 bỏ qua. Bài học vận hành: đừng chạy nhiều lượt gọi NCBI song song với lô bộ năm khi không có
`NCBI_API_KEY`.
