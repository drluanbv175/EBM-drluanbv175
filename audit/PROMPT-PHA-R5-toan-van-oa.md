# PROMPT PHA R5 — «ĐỌC BÀI HỘ»: TOÀN VĂN PMC-OA CHO MỖI ĐỀ TÀI (15/08/2026)

Khoảng trống SciSpace cuối của tuyến nghiên cứu: hệ thẩm định trên ABSTRACT;
SciSpace đọc TOÀN VĂN hộ người dùng. Đóng bằng nguồn HỢP PHÁP duy nhất máy được
phép: PubMed Central Open Access (P5 — không cào nguồn trả phí, không Sci-Hub).

R5-1 `tools/gom_toan_van_oa.py --study <mã>`: với mỗi PMID nền của đề tài
 (đọc từ G0 artifact §3) → elink pubmed→pmc → efetch toàn văn XML → lưu
 `exports/<study>/toan_van_oa/` + báo cáo ĐỘ PHỦ TRUNG THỰC (bao nhiêu % có OA;
 phần không OA ghi rõ «cần quyền truy cập của bác sĩ», không lách).
R5-2 Chạy THẬT trên đề tài demo — đo tỷ lệ OA thật của nền statin-adherence.
R5-3 BH52: R1C (kiểm rút bài tại G0) phải SỐNG — chấm trên đề tài demo, phải
 thấy cờ EoC 39259232; mutation-test (tháo R1C → đỏ).
R5-4 Commit 2 repo + báo cáo. KHÔNG đụng nhánh ký (runbook 6 bước vẫn của bác sĩ).
