---
name: kiem-thang-diem-quy
description: Quét quý PMID/DOI nguồn gốc 32 thang điểm verified qua kiem_do_tuoi_thang_diem.py — rút bài/expression of concern, không tự đổi cut-off
---

Bạn đang chạy một vòng KIỂM RÚT BÀI theo QUÝ cho kho 32 thang điểm/công cụ lâm sàng đã "verified" của hệ EBM Copilot, thư mục dự án: "/Users/nguyenluan/Library/CloudStorage/OneDrive-Personal/Claude AI/medical-ebm-automation".

BỐI CẢNH (đọc để hiểu vì sao việc này cần chạy định kỳ): app/clinical_scores/verified.py::VERIFIED_SCORES ghi PMID/DOI nguồn gốc cho 32 thang điểm (CURB-65, CHA2DS2-VASc, qSOFA, MELD-Na, Child-Pugh…), xác minh MỘT LẦN vào 2026-06-14. Trước 13/09/2026, kho này có 0 cơ chế tự động tái-kiểm định kỳ — một PMID nền tảng của công thức/ngưỡng lâm sàng có thể bị rút sau đó mà không ai biết, và hệ vẫn tính điểm/áp ngưỡng dựa trên nó. Tác vụ này là owner DUY NHẤT của việc tái-kiểm định kỳ đó (không nối trùng qua tu_khoi_dong.py).

CÁC BƯỚC:
1. Chạy: cd "/Users/nguyenluan/Library/CloudStorage/OneDrive-Personal/Claude AI/medical-ebm-automation" && bash scripts/quarterly_clinical_scores_check.sh
   (script này tự gọi tools/kiem_do_tuoi_thang_diem.py — chạy chuỗi 3 tầng rút bài Retraction Watch/NCBI/Europe PMC cho các PMID, Crossref cho DOI-only — rồi ghi log vào data/archive/quarterly_clinical_scores.log và tự ghi cảnh báo vào ../alerts/<ngày>.md nếu có phát hiện).
2. Đọc mã thoát và nội dung log vừa ghi:
   - Nếu tổng thể=PASS và bước (1)=0: chỉ cần báo MỘT dòng ngắn xác nhận đã quét sạch (không có rút bài/expression of concern nào trong 32 thang điểm).
   - Nếu bước (1)=1 (CÓ phát hiện): báo cáo NGẮN GỌN bằng tiếng Việt từng thang điểm bị gắn cờ 🔴 hoặc ⚠️ trong log (tên thang điểm, PMID/DOI, trạng thái, lý do), kèm câu "Cần bác sĩ đối chiếu và quyết định có đổi công thức/nguồn hay không — công cụ chỉ đo và báo, không tự đổi cut-off/decision nào."
   - Nếu bước (1)≥2 (lỗi công cụ, tổng thể="CÓ BƯỚC LỖI"): báo rõ lỗi đó nguyên văn — KHÔNG tự suy diễn nguyên nhân.
3. KHÔNG sửa app/clinical_scores/verified.py, KHÔNG đổi bất kỳ decision/gradeLevel/cut-off nào dù phát hiện rút bài — việc đó thuộc thẩm quyền bác sĩ.

RÀNG BUỘC BẤT BIẾN: đây CHỈ là bước GIÁM SÁT/PHÁT HIỆN. Không dùng PII. Trả lời bằng tiếng Việt.