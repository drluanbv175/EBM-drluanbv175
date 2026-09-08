---
name: statistical-analysis
description: Quy trình phân tích thống kê lâm sàng/nghiên cứu y khoa — mô tả dữ liệu, chọn kiểm định theo loại biến + thiết kế + giả định, hồi quy/sống còn/ROC/hiệu chỉnh, báo cáo ước lượng + 95% CI. Dùng khi cần chạy/đọc phân tích thống kê cho một đề tài (sau khi SAP & dữ liệu đã khóa), tính cỡ mẫu cần khung công thức, hoặc kiểm định một giả thuyết. Ưu tiên công cụ mở (Python scipy/statsmodels/lifelines/pingouin hoặc R). KHÔNG bịa số; báo CI không chỉ p.
---

<!-- EBM-VN-GUARD -->
> **⚕️ Bản điều chỉnh cho bác sĩ EBM ngoại trú (Việt Nam).** Skill gốc của K-Dense Inc. đã được chỉnh để phù hợp quy ước trong `CLAUDE.md` của người dùng.
>
> **QUY TẮC BẮT BUỘC — đọc trước, GHI ĐÈ mọi hướng dẫn tiếng Anh bên dưới:**
> 1. **Ngôn ngữ:** Mọi trao đổi và đầu ra cho người dùng viết bằng **tiếng Việt** (giữ thuật ngữ y khoa tiếng Anh khi cần; tên thuốc theo INN).
> 2. **Disclaimer:** Mọi đầu ra y khoa kết thúc bằng câu **"⚠️ Cần bác sĩ kiểm chứng trước khi áp dụng lâm sàng."**
> 3. **Nguồn:** Mọi nhận định/khuyến cáo phải **ghi nguồn (PMID/DOI)**; không có nguồn thì không khẳng định. **Tuyệt đối không bịa dữ liệu hay nguồn.**
> 4. **Không PII:** **KHÔNG** lưu hay tạo thông tin định danh bệnh nhân (tên, ngày sinh, số hồ sơ, địa chỉ...). Dùng mã ẩn danh.
> 5. **Chỉ nguồn miễn phí:** Khi tra cứu y văn dùng **PubMed E-utilities** (miễn phí, không cần API key) và các CSDL mở. **KHÔNG** dùng dịch vụ trả phí (parallel.ai, Perplexity, OpenRouter...). Nếu một lệnh gốc gọi `parallel-cli`/Perplexity, thay bằng `python scripts/pubmed_lookup.py "..."` hoặc REST miễn phí.
> 6. **Bối cảnh:** Bỏ qua phần chỉ phục vụ ngữ cảnh dược phẩm/pháp lý Mỹ (HIPAA/FDA/ICH-CSR) khi không liên quan ngoại trú VN; ưu tiên guideline quốc tế mới nhất rồi hiệu chỉnh theo Bộ Y tế VN.
>
> Phần kỹ thuật chi tiết (template, script, references) giữ nguyên tiếng Anh nhưng phải tạo ra **đầu ra tiếng Việt** theo các quy tắc trên.


# Skill: Phân tích thống kê lâm sàng (statistical-analysis)

Trợ giúp chọn ĐÚNG kiểm định/mô hình theo loại biến – thiết kế – giả định, chạy bằng công cụ mở, và báo cáo trung thực. Dùng cho `phan-tich-thong-ke`, `co-mau-nghien-cuu` (khung công thức).

## Nguyên tắc liêm chính (4 trụ cột)
- Chạy ĐÚNG kế hoạch định trước (SAP đã khóa); phân tích ngoài SAP gắn nhãn **"thăm dò (exploratory)"**.
- Báo **khoảng tin cậy 95%** + ước lượng hiệu ứng, KHÔNG chỉ p; KHÔNG p-hacking/HARKing; KHÔNG cherry-picking.
- Làm trên **BẢN SAO** dữ liệu, có script tái lập; KHÔNG PII. KHÔNG bịa số/kết quả.
- Không suy nhân quả vượt thiết kế (quan sát → "liên quan").

## Quy trình
**BƯỚC 0 — Tiền đề:** xác nhận SAP đã khóa + DB đã khóa/khử định danh; chưa → đánh dấu PRELIMINARY hoặc dừng. Xác định **thiết kế** + **loại từng biến** (định danh/thứ hạng/khoảng-tỷ lệ; thời gian-đến-biến cố).
1. **Mô tả:** flow tham gia (CONSORT nếu RCT); đặc điểm nền (TB±SD hoặc trung vị[IQR] tùy phân phối; n(%) cho phân loại); dữ liệu thiếu (số lượng + cơ chế MCAR/MAR/MNAR nếu suy được).
2. **Kiểm giả định → chọn test:** xem bảng dưới. Kiểm chuẩn (Shapiro–Wilk/đồ thị Q–Q), phương sai (Levene), độc lập, tuyến tính, tỷ lệ rủi ro (Schoenfeld cho Cox).
3. **Phân tích chính (theo SAP):** ước lượng hiệu ứng + 95% CI + p; ITT cho RCT.
4. **Mô hình nâng cao:** hồi quy tuyến tính/logistic (kiểm đa cộng tuyến/VIF; hiệu chuẩn Hosmer–Lemeshow cho logistic; EPV≥10); **sống còn** (Kaplan–Meier + log-rank; Cox PH + HR/95% CI; kiểm PH); **ROC/độ chính xác chẩn đoán** (AUC, Se/Sp/PPV/NPV/LR, chọn ngưỡng Youden); **mô hình dự đoán** (TRIPOD+AI: hiệu chuẩn + phân biệt + validation nội/ngoại).
5. **Nhạy cảm + nhóm nhỏ:** chỉ phần định trước; phần thêm dán nhãn thăm dò; hiệu chỉnh đa so sánh khi cần.

## Bảng chọn test (gợi ý — kiểm giả định trước)
| Câu hỏi | Biến | Giả định đạt | Giả định KHÔNG đạt |
|---|---|---|---|
| So 2 nhóm độc lập, biến liên tục | liên tục | t-test độc lập | Mann–Whitney U |
| So 2 lần đo cùng đối tượng | liên tục | t-test ghép cặp | Wilcoxon signed-rank |
| So ≥3 nhóm | liên tục | ANOVA (+post-hoc) | Kruskal–Wallis |
| Liên hệ 2 biến phân loại | phân loại | Chi-square | Fisher exact (ô vọng <5) |
| Tương quan 2 biến liên tục | liên tục | Pearson | Spearman |
| Dự đoán biến nhị phân | hỗn hợp | Hồi quy logistic | — |
| Thời gian đến biến cố | sống còn | Cox PH (nếu PH đạt) | mô hình thời gian-phụ thuộc |

## Công cụ mở (ưu tiên)
- **Python:** `scipy.stats`, `statsmodels`, `lifelines` (sống còn), `pingouin`, `scikit-learn` (ROC/validation), `matplotlib` (forest/KM/ROC).
- **R:** base `stats`, `survival`, `pROC`, `rms`, `meta`/`metafor`.
- Viết script docstring tiếng Việt, tái lập được; lưu seed nếu có ngẫu nhiên.

## Mẫu đầu ra
```
Tiền đề: SAP khóa[✓/✗] · DB khóa[✓/✗] · khử định danh[✓/✗]
Mô tả mẫu: n=__; dữ liệu thiếu __; (CONSORT flow nếu RCT)
Giả định đã kiểm: ____ → test/mô hình chọn: ____
| Kết cục | Ước lượng | 95% CI | p | (định trước/thăm dò) |
Phần mềm/lệnh + script tái lập: ____   | Cảnh báo (vi phạm giả định/thiếu lực): ____
```

## Ranh giới
KHÔNG đổi kế hoạch (việc của thiết kế/SAP); KHÔNG viết Bàn luận; thử nghiệm then chốt → cần nhà thống kê độc lập xác nhận. Kết: **"Cần bác sĩ kiểm chứng."**
