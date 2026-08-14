# Mô-đun 4 — Thống kê & mô hình lâm sàng

Gộp từ (CHỈ thống kê lâm sàng, KHÔNG omics/ML bench): km-survival-curve,
univariate-multivariable-cox-regression, roc-diagnostic-performance, time-dependent-roc,
model-calibration-curve, decision-curve-analysis, nomogram-construction, external-model-validation.
> ĐÃ LOẠI: WGCNA, GSEA/GSVA/ssGSEA, CIBERSORT/ESTIMATE, PCA/UMAP/tSNE, clustering, DEG, ceRNA,
> PPI, LASSO/elastic-net/XGBoost/LightGBM/RF/SVM/decision-tree dùng cho gene expression.

## Nguyên tắc trước khi chọn test
- Xác định: loại biến (định lượng/định tính), phân phối, ghép cặp hay độc lập, số nhóm, kiểm định giả định.
- Báo cáo chuẩn: ước lượng điểm + **khoảng tin cậy 95%**, không chỉ p. Phân biệt ý nghĩa thống kê vs lâm sàng.

## 1. Sống còn (Kaplan–Meier)
- Đường KM theo nhóm + số còn nguy cơ (at-risk) + log-rank. Kiểm tỉ lệ kiểm duyệt (censoring).

## 2. Hồi quy Cox (đơn & đa biến)
- Đơn biến sàng lọc → đa biến (tránh nhồi biến: ~≥10 biến cố/biến). Báo cáo **HR (95% CI)**, p.
- Kiểm giả định **tỉ lệ nguy cơ (PH)** (Schoenfeld). Nêu xử lý vi phạm (biến phụ thuộc thời gian).

## 3. ROC & hiệu năng chẩn đoán
- AUC (95% CI), độ nhạy/độ đặc hiệu tại ngưỡng, PPV/NPV (lưu ý phụ thuộc tỷ lệ hiện mắc), LR±.
- So sánh AUC: DeLong. **Time-dependent ROC** cho kết cục theo thời gian (mô hình tiên lượng).

## 4. Hiệu chỉnh (calibration)
- Đường hiệu chỉnh (dự đoán vs quan sát), Hosmer-Lemeshow/độ dốc-điểm chặn, Brier score.

## 5. Decision Curve Analysis (DCA)
- Net benefit theo ngưỡng xác suất; so với "điều trị tất cả"/"không ai". Trả lời: mô hình có ích lâm sàng không.

## 6. Nomogram
- Xây từ mô hình hồi quy (Cox/logistic) đã thẩm định; KÈM C-index + đường hiệu chỉnh. Không trình bày tách rời thẩm định.

## 7. Ngoại kiểm mô hình (external validation)
- Áp mô hình lên tập độc lập; báo cáo discrimination (AUC/C-index) + calibration + DCA. Cảnh báo
  optimism nếu chỉ nội kiểm. Nêu khác biệt dân số (case-mix).

## Lưu ý triển khai
- Để CHẠY thực tế: dùng Python (`statsmodels`, `lifelines`, `scikit-learn`) hoặc R (`survival`,
  `rms`, `timeROC`, `rmda`). Ghi rõ phiên bản & hạt giống (seed). KHÔNG bịa số liệu/kết quả.

## Đầu ra
Lựa chọn test + giả định đã kiểm + bảng kết quả (ước lượng + 95% CI) + biểu đồ; diễn giải lâm sàng.
⚠️ Cần bác sĩ kiểm chứng.
