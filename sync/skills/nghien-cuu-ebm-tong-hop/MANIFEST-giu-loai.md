# MANIFEST — Giữ / Loại (từ bộ Medical Research Skills của AIPOCH)

Tiêu chí: **phù hợp với bác sĩ lâm sàng EBM ngoại trú** (tìm–thẩm định chứng cứ, thiết kế
nghiên cứu lâm sàng, thống kê lâm sàng, viết bản thảo). Loại phần **bench/omics/ML tin sinh học,
network pharmacology, Mendelian randomization, persona nhập vai** — không phục vụ thực hành lâm sàng.

Nguồn gốc: ~140 skill (awesome-med-research-skills) + thư viện đầy đủ (scientific-skills). Giấy phép MIT.

## ✅ ĐÃ GIỮ → hợp nhất vào 5 mô-đun

**Mô-đun 1 — Tìm y văn:** biomedical-search-strategy-builder, multi-database-literature-collector,
high-value-paper-screener, clinical-question-clarifier.

**Mô-đun 2 — Thẩm định:** study-design-identifier, evidence-level-ranker, result-reliability-checker,
contradictory-findings-resolver, paper-to-claim-verifier, figure-first-paper-reader,
topic-evidence-mapper, medical-research-gap-finder.

**Mô-đun 3 — Thiết kế (phần lâm sàng):** aim-and-hypothesis-designer, study-objective-refiner,
case-control-study-planner, clinical-cohort-protocol-designer, real-world-evidence-study-designer,
inclusion-exclusion-criteria-builder, endpoint-definition-designer, confounder-and-bias-control-planner,
sample-size-and-power-planning-assistant, feasibility-aware-study-planner, validation-strategy-designer.

**Mô-đun 4 — Thống kê lâm sàng:** km-survival-curve, univariate-multivariable-cox-regression,
roc-diagnostic-performance, time-dependent-roc, model-calibration-curve, decision-curve-analysis,
nomogram-construction, external-model-validation.

**Mô-đun 5 — Viết bản thảo:** introduction/methods/results/discussion writers,
reporting-guideline-compliance-checker, reference-integrity-checker, title-and-abstract-optimizer,
conference-abstract-writer, cover-letter-drafter, target-journal-matcher, medical-english-precision-editor,
limitation-and-risk-writer, revision-strategy-planner, author-response-builder, claim-strength-calibrator.

## ❌ ĐÃ LOẠI (không phù hợp lâm sàng ngoại trú) — kèm lý do

- **Toàn bộ Data Analysis omics/ML bench**: WGCNA, GSEA/GSVA/ssGSEA, CIBERSORT, ESTIMATE, ceRNA,
  lncRNA/TF networks, PPI, DEG/differential-expression, batch-effect, PCA, UMAP/tSNE, consensus/
  hierarchical clustering, sample-correlation, ma trận biểu hiện gene, KNN imputation, GO/KEGG,
  immune-pathway/infiltration, LightGBM/XGBoost/elastic-net/lasso/RF/SVM/decision-tree (cho gene).
  *Lý do:* nghiên cứu tin sinh học/labo, không dùng trong khám–điều trị ngoại trú. (Cũng là phần
  chiếm ~280MB dữ liệu mẫu — không cần cho bác sĩ.)
- **Protocol Design omics/nhân quả genomics/network pharmacology**: tất cả *-omics, *-mr-*,
  mendelian-randomization, two-sample-mr, qtl-colocalization, network-toxicology/pharmacology,
  hub-gene (oncology/non-oncology), single-cell/scRNA, transcriptome-biomarker, comorbidity-immune,
  faers-pharmacovigilance-disproportionality, nhanes-retrospective.
  *Lý do:* thiết kế cho nghiên cứu cơ bản/dữ liệu lớn chuyên sâu, không phù hợp lâm sàng ngoại trú.
- **Evidence Insight thiên bench**: bioinformatics/basic-discovery translational-opportunity-finder,
  biomarker-landscape-scanner, drug-target-evidence-landscape, disease-mechanism-evidence-map,
  methods-reverse-engineer, method-gap-detector.
  *Lý do:* phục vụ khám phá đích phân tử/cơ chế, ngoài phạm vi EBM lâm sàng.
- **Academic Writing chuyên biệt khác ngành**: arxiv-preflight (vật lý/CS), grant-specific-aims
  (cơ chế tài trợ Mỹ), graphical-abstract-generator, poster-storyline-builder, slide-deck-for-lab-meeting,
  latex-manuscript-format-converter, lay-summary-for-cross-disciplinary-teams.
  *Lý do:* không thiết yếu cho bản thảo lâm sàng tiếng Việt; có thể bổ sung sau nếu cần.
- **Other (persona nhập vai)**: `bianque` (Biển Thước, đậm Đông y/望闻问切), `mendel` (di truyền học).
  *Lý do:* là nhân vật mentor nhập vai, không phải công cụ EBM; lệch trọng tâm lâm sàng.
- **Hạ tầng repo**: .github/workflows, node_modules (html-to-pdf), eval_report_*.json, fixtures dữ liệu lớn.
  *Lý do:* không phải nội dung skill; loại để gọn.

## Ghi chú
- Nếu sau này bạn làm nghiên cứu omics/MR thật, có thể bổ sung lại các mô-đun đã loại.
- Skill này tôn trọng quy tắc dự án: chỉ API miễn phí, PMID/DOI, disclaimer "Cần bác sĩ kiểm chứng",
  không lưu PII.
