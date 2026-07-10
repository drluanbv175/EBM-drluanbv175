# tools/ — LỚP CÔNG CỤ NGOÀI cho hệ Agent EBM (vượt "trần .md")

**[PROTOTYPE — cần cài deps + BS duyệt governance trước khi chạy trên dữ liệu thật]**
Cập nhật 2026-06-16. Lớp tools/ là cách vượt "trần .md" — không giải bài toán tools-layer bằng cách đẻ thêm agent .md (đội hiện 45 agent). KHÔNG PII — chỉ metadata chứng cứ.

| Thư mục | Hạng mục | Vượt "trần" gì | Trạng thái |
|---|---|---|---|
| [`critic/`](critic/README.md) | **A** | `tham-dinh-dau-ra` chạy ở **ngữ cảnh tách** (subagent/phiên 2) thay vì self-check cùng phiên | spec tự chứa + protocol chạy được; gọi tự động = [CẦN MÔI TRƯỜNG HỖ TRỢ] |
| [`rag/`](rag/README.md) | **B** | Truy xuất **ngữ nghĩa** metadata chứng cứ thay vì khóa-từ; có cổng khử PII | demo synthetic OK; **backend SEMANTIC NHẸ TF-IDF (sklearn) chạy được** — tách hạng tốt hơn hashing (~2,2× margin) |
| [`eval/`](eval/README.md) | **C** | Harness chấm đầu ra **rule-based, lặp lại được**; giữ người duyệt | demo 4 sample OK; **rubric 11 kiểm** (thêm năm nguồn · AWaRe · cấm nhân quả từ cắt ngang); auto-optimizer VẪN TẮT |

## Bất biến (4 trụ cột)
Trung thực · bảo mật · pháp lý · liêm chính. Mọi đầu ra kèm PMID/DOI + **"Cần bác sĩ kiểm chứng."**;
KHÔNG bịa; KHÔNG PII; agent chỉ ĐỀ XUẤT — bác sĩ duyệt mới "áp dụng" (Cổng A/B · G2/G4).
Lộ trình & điều kiện vận hành: `.claude/agents/_LO-TRINH-HA-TANG.md`.
