---
name: scientific-writing
description: Viết bản thảo khoa học y khoa theo cấu trúc IMRAD, văn xuôi liền mạch, khớp CHUẨN BÁO CÁO đúng thiết kế (CONSORT/STROBE/PRISMA/SPIRIT/STARD/TRIPOD+AI; COREQ/SRQR cho định tính; SQUIRE cho QI). Dùng khi cần viết bài báo, protocol, hoặc báo cáo nghiệm thu; soạn Methods/Results/Discussion; đối chiếu checklist chuẩn báo cáo. Mỗi khẳng định có nguồn PMID/DOI; KHÔNG bịa số liệu/trích dẫn; nhắc khai báo AI + tác giả ICMJE + COI.
---

# Skill: Viết bản thảo khoa học (scientific-writing)

<!-- EBM-VN-GUARD -->
**QUY TẮC EBM BẮT BUỘC:** đầu ra tiếng Việt; **KHÔNG bịa trích dẫn/số liệu** — mỗi khẳng định kèm PMID/DOI, số chưa có ghi `[CẦN BỔ SUNG]`; kèm disclaimer "⚠️ Cần bác sĩ kiểm chứng"; **KHÔNG lưu PII**.

Chuyển kết quả nghiên cứu thành bản thảo mạch lạc, trung thực, đạt chuẩn tạp chí. Dùng cho `viet-ban-thao`.

## Nguyên tắc liêm chính (4 trụ cột)
- **KHÔNG bịa** trích dẫn/số liệu — chỉ viết điều dữ liệu/nguồn chống đỡ; mỗi khẳng định có **PMID/DOI**.
- Phân biệt phát hiện vs suy diễn; không overclaim; không suy nhân quả vượt thiết kế.
- Số liệu chưa có → `[CẦN BỔ SUNG]`; KHÔNG PII; nhắc khai báo **dùng AI + đóng góp tác giả (ICMJE) + COI/tài trợ** theo yêu cầu tạp chí.

## Quy trình 2 bước
**BƯỚC 0 — Tiền đề:** xác nhận kết quả từ SAP đã khóa; có mã đăng ký + số phê duyệt đạo đức THẬT (do tác giả cấp; thiếu → `[CẦN BỔ SUNG]`); chọn ĐÚNG chuẩn báo cáo theo thiết kế.
**Bước 1 — Dàn ý:** chốt thông điệp chính (1 câu) → chọn chuẩn báo cáo → lập sườn IMRAD theo checklist chuẩn đó.
**Bước 1b — Vỏ bài báo (làm SAU khi thân bài xong, KHÔNG làm trước):**
- **Tiêu đề:** nêu quần thể + can thiệp/phơi nhiễm + kết cục chính, và **gọi tên thiết kế** (RCT / đoàn hệ / cắt ngang / tổng quan hệ thống) theo chuẩn báo cáo tương ứng. Không câu hỏi tu từ, không viết tắt chưa định nghĩa, không khẳng định vượt dữ liệu.
- **Tóm tắt có cấu trúc:** đủ **5 phần** — bối cảnh · mục tiêu · phương pháp (thiết kế, đối tượng, cỡ mẫu, kết cục chính) · kết quả (ước lượng + 95% CI, không chỉ p) · kết luận. Theo giới hạn từ của tạp chí (thường 250–300). **Độc lập**: đọc riêng tóm tắt vẫn nắm được nghiên cứu. Mọi con số phải **có mặt y hệt** trong Results — lệch số giữa tóm tắt và thân bài là lỗi bị bắt nhiều nhất.
- **Từ khóa:** 3–6 từ, **ưu tiên từ chưa có trong tiêu đề** (lặp lại tiêu đề không tăng khả năng được tìm thấy). Đối chiếu MeSH Browser; chưa tra được thì ghi `[CẦN KIỂM CHỨNG NGUỒN CHÍNH THỨC]`.

**Bước 2 — Văn xuôi (liền mạch, KHÔNG gạch đầu dòng trong thân):**
- **Introduction:** khoảng trống kiến thức → mục tiêu/giả thuyết.
- **Methods:** đủ chi tiết tái lặp; nêu phê duyệt đạo đức + mã đăng ký; tham chiếu SAP.
- **Results:** chỉ sự kiện, kèm ước lượng + 95% CI; bảng/hình không lặp văn. **KHÔNG diễn giải, KHÔNG so sánh y văn ở mục này** — để dành cho Discussion.
- **Discussion:** diễn giải trong giới hạn; đối chiếu y văn; điểm mạnh–hạn chế; ý nghĩa lâm sàng (thận trọng).
- **Conclusion:** đóng góp cốt lõi trong đúng phạm vi dữ liệu; **không lặp lại Results**; không phóng đại, không suy nhân quả vượt thiết kế; nêu **câu hỏi/hướng nghiên cứu tiếp**.
- **References:** chỉ tài liệu **đã thực sự trích trong bài** (không "đọc thêm"); Vancouver/NLM, đánh số theo thứ tự xuất hiện; kiểm khớp 1-1 giữa số trong văn bản và danh mục cuối bài trước khi nộp.

## Chọn chuẩn báo cáo theo thiết kế
| Thiết kế | Chuẩn | Ghi chú |
|---|---|---|
| RCT/thử nghiệm | **CONSORT** (+**SPIRIT** cho protocol) | sơ đồ CONSORT, ITT |
| Quan sát (cohort/bệnh-chứng/cắt ngang) | **STROBE** | nêu nhiễu, sai lệch |
| Tổng quan hệ thống/Meta | **PRISMA 2020** | +PROSPERO |
| Độ chính xác chẩn đoán | **STARD** | Se/Sp/LR/AUC |
| Mô hình dự đoán/AI | **TRIPOD+AI** | hiệu chuẩn + phân biệt + validation |
| Định tính / hỗn hợp | **COREQ/SRQR** | trustworthiness |
| Cải tiến chất lượng | **SQUIRE 2.0** | PDSA |

## 🔒 Cổng cứng trích dẫn (trước khi coi là "xong")
Mọi tham khảo phải qua kiểm chứng (skill `citation-management`/agent `kiem-chung-trich-dan`): PMID/DOI có thật + nội dung trích đúng. Trích dẫn chưa xác minh → `[TRÍCH DẪN CHƯA XÁC MINH]`, KHÔNG để lọt bản nộp.

## Mẫu đầu ra
```
Thông điệp chính (1 câu): ____ | Chuẩn báo cáo: [CONSORT/STROBE/…]
Tiêu đề: ____ | Từ khóa (3–6, ưu tiên từ ngoài tiêu đề): ____
Tóm tắt có cấu trúc (5 phần, ≤ giới hạn tạp chí) — mọi số khớp Results
Bản thảo IMRAD (Markdown; xuất DOCX/PDF/LaTeX khi cần)
| Mục checklist chuẩn | Ở đoạn/mục nào |
Danh mục tham khảo (đã kiểm chứng PMID/DOI)
Khai báo: COI · tài trợ · đóng góp tác giả (ICMJE) · dùng AI  [tác giả xác nhận]
[CẦN BỔ SUNG]: chỗ thiếu dữ liệu
```

## Ranh giới
KHÔNG tạo dữ liệu/kết quả chưa có; KHÔNG tự quyết phân tích (nhận từ `statistical-analysis`). Bản thảo phải qua bình duyệt (`peer-review`) trước khi coi là sẵn sàng nộp. Kết: **"Cần bác sĩ kiểm chứng."**
