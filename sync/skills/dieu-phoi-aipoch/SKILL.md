---
name: dieu-phoi-aipoch
description: "Định tuyến yêu cầu nghiên cứu/lâm sàng tới đúng skill trong 605 skill của plugin aipoch-medical-research, theo 35 nhóm chuyên môn. Dùng khi bác sĩ mô tả một việc nhưng KHÔNG biết tên skill cụ thể trong bộ aipoch."
---

# Điều phối aipoch-medical-research

Skill này là **BỘ ĐIỀU PHỐI (router)** cho 605 skill của plugin `aipoch-medical-research` — plugin nặng nhất máy này, liệt kê đủ tên+mô tả tốn 71% ngân sách danh sách skill mỗi phiên (CLAUDE.md, mục "NGÂN SÁCH DANH SÁCH SKILL"). Mô tả skill này NGẮN nên gần như không tốn ngân sách; bảng nhóm dưới chỉ nạp vào ngữ cảnh KHI skill được gọi thật.

**KHÔNG tự làm việc chuyên môn ở đây.** Việc DUY NHẤT: đọc yêu cầu bác sĩ → khớp đúng NHÓM/skill dưới đây → invoke skill đó bằng tên đầy đủ `aipoch-medical-research:<ten-skill>`. Skill được gọi mới thật sự phân tích/viết lách, router không tự bịa kết quả.

> Vài tên skill gần giống nhau (`rct-bias-assessment-rob`/`-rob2`, `…-quadas`/`-quadas-2`, 2 bản `cover-letter-drafter`) do plugin gộp 2 kho nguồn trùng nội dung — chọn tên nào cũng được, ưu tiên tên khớp sát từ khoá bác sĩ dùng.

## 35 nhóm chuyên môn

### 1. Xây câu hỏi nghiên cứu, giả thuyết & mục tiêu
Biến ý tưởng mơ hồ thành câu hỏi, giả thuyết, mục tiêu đo được, khả thi.
`aim-and-hypothesis-designer`, `basic-research-design`, `bioinfo-analysis-plan`, `brainstorming`, `clinical-question-clarifier`, `feasibility-aware-study-planner`, `hypogenic` (sinh & kiểm giả thuyết LLM), `hypothesis-generation`, `primary-plan-recommender`, `study-objective-refiner`.

### 2. Tìm khoảng trống nghiên cứu, tính khả thi & tiềm năng dịch mã
Rà chủ đề đã bão hoà chưa, có mới không, khả thi không, dịch mã đi đâu.
`animal-and-cell-validation-planner`, `basic-discovery-translational-opportunity-finder`, `bioinformatics-translational-opportunity-finder`, `biomarker-landscape-scanner`, `blockbuster-therapy-predictor`, `contradictory-findings-resolver`, `cross-disciplinary-bridge-finder`, `disease-mechanism-evidence-map`, `drug-target-evidence-landscape`, `emerging-topic-scout`, `evidence-level-ranker`, `funding-trend-forecaster`, `grant-funding-scout`, `keyword-velocity-tracker`, `mechanism-to-validation-planner`, `medical-research-algorithm-matcher`, `medical-research-gap-finder`, `medical-research-gap-to-study-planner`, `medical-topic-saturation-and-whitespace-checker`, `method-gap-detector`, `novelty-vs-feasibility-assessor`, `population-gap-detector`, `target-novelty-scorer`, `topic-evidence-mapper`, `translational-gap-analyzer`, `translational-study-blueprint`, `unmet-clinical-need-extractor`.

### 3. Thiết kế nghiên cứu lâm sàng cổ điển & đề cương thử nghiệm
Khung bệnh-chứng, cohort, RWE, RCT: chọn-loại, kiểm soát nhiễu, kết cục, ngẫu nhiên hoá, SOP.
`adaptive-trial-simulator`, `case-control-study-planner`, `clinic-research-design`, `clinical-cohort-protocol-designer`, `clinical-trial-protocol-skill`, `confounder-and-bias-control-planner`, `endpoint-definition-designer`, `experiment-design`, `inclusion-criteria-gen`, `inclusion-exclusion-criteria-builder`, `protocol-standardization`, `randomization-gen`, `real-world-evidence-study-designer`, `research-proposal-generator`, `sop-writer`, `tooluniverse-clinical-trial-design`, `validation-strategy-designer`.

### 4. Cỡ mẫu & lực mẫu thống kê
Tính cỡ mẫu/power cho thiết kế chẩn đoán, hiệu quả, bệnh nguyên, tiên lượng.
`clinic-sample-size`, `sample-size-and-power-planning-assistant`, `sample-size-basic`, `sample-size-power-calculator`.

### 5. Đề cương Mendelian randomization, dược lý/độc chất mạng & dược cảnh giác FAERS
Đề cương TRỌN GÓI: MR nhân quả di truyền, dược lý/độc chất mạng, tín hiệu an toàn thuốc FAERS.
`active-comparator-single-soc-faers-safety-comparison`, `bidirectional-multi-phenotype-mr-research-planner`, `bio-causal-genomics-mediation-analysis`, `bio-causal-genomics-pleiotropy-detection`, `comparative-network-toxicology-shared-mechanism-reference-grounded`, `drug-repurposing-study-planner`, `faers-multi-drug-soc-planner`, `faers-pharmacovigilance-disproportionality-research-planner`, `mendelian-randomisation`, `mendelian-randomization-protocol-designer`, `mr-scrna-research-planner`, `network-tox-docking-research-planner`, `qtl-colocalization-study-planner`, `single-compound-network-toxicology-disease-link-reference-grounded`, `single-drug-adverse-effect-hub-first-network-pharmacology`, `single-drug-adverse-effect-pathway-anchored-network-pharmacology`, `single-drug-faers-safety-profile-research-planner`, `two-sample-mr-exposure-screening-reference-grounded`, `two-sample-mr-research-planner`.

### 6. Đề cương nghiên cứu biomarker, đa-omics & ung thư chuyên biệt
Đề cương TRỌN GÓI biomarker/đa-omics: gen trục chung nhiều bệnh, đơn bào, chẩn đoán ML, tiên lượng, NHANES.
`bulk-omics-integrative-planner`, `comorbidity-common-immune-biomarker-research-planner`, `conventional-non-oncology-hub-gene-research-planner`, `conventional-oncology-hub-gene-research-planner`, `cross-disease-shared-biomarker-network-research-planner`, `dual-disease-shared-transcriptome-biomarker-research-planner`, `dual-disease-transcriptomic-ml-planner`, `generic-phenotype-scoring-research-planner`, `multi-omics-clinical-integration-planner`, `nhanes-clinical-retrospective-biomarker-research-planner`, `non-tumor-mechanism-guided-diagnostic-ml-research-planner`, `non-tumor-ml-research-planner`, `pcd-immune-oncology-research-planner`, `process-related-diagnostic-biomarker-nomogram-research-planner`, `prognostic-biomarker-protocol-designer`, `single-cell-research-planner`, `single-gene-oncology-reference-grounded-research-planner`, `treatment-response-predictor-planner`, `tumor-immune-infiltration-diagnostic-ml-research-planner`.

### 7. CSDL thử nghiệm lâm sàng & quy định dược phẩm
Tra ClinicalTrials.gov/EUCTR, theo dõi thử nghiệm đối thủ, CSDL quản lý dược FDA.
`clinical-trial-finder`, `clinicaltrials-database`, `clinicaltrials-db`, `clinicaltrials-gov-parser`, `competitor-trial-monitor`, `fda-database`, `fda-guideline-search`, `tooluniverse-clinical-trial-matching`.

### 8. Tra cứu & tìm kiếm y văn / CSDL học thuật
Tìm bài qua PubMed +9 CSDL khác, xây chiến lược tìm, theo dõi chủ đề/tạp chí, tải toàn văn, kiểm rút bài.
`arxiv-database`, `biomedical-search-strategy-builder`, `biorxiv-database`, `citation-chasing-mapping`, `citation-network`, `crossref-database`, `find-paper-references`, `fulltext-fetcher`, `medical-vector-search`, `multi-database-literature-collector`, `openalex-db`, `paper-lookup`, `pmc-official-download`, `preprint-surveillance-finder`, `pubmed-database`, `pubmed-search-specialist`, `pubmed-topic-recommend`, `reference-finder`, `reference-retrieval-skill`, `reference-search`, `research-article-weekly`, `research-hotspot-analysis`, `research-paper-downloader`, `retraction-watcher`, `scite-database`, `search-pubmed`, `semantic-scholar-database`, `tooluniverse-literature-deep-research`.

### 9. Đọc, tóm tắt & thẩm định nhanh bài báo
Đọc nhanh bài đã có sẵn: tóm theo hình, trích phương pháp, đối chiếu tuyên bố với dữ liệu, chấm điểm.
`bibliography`, `clinical-study-info-extractor`, `experiment-detail-comparator`, `figure-first-paper-reader`, `high-value-paper-screener`, `key-takeaways`, `litbase` (đọc bài qua Semantic Scholar), `literature-close-read`, `literature-experiment-extract`, `literature-extensive-read`, `literatureimages-interpretation`, `medical-research-literature-reader-pro`, `methodology-extractor`, `methods-reverse-engineer`, `molecular-review-workflow`, `paper-to-claim-verifier`, `pdf-extract-experimental-materials`, `result-reliability-checker`, `scholar-evaluation`.

### 10. Quản lý trích dẫn & định dạng tài liệu tham khảo
Đổi định dạng trích dẫn (APA/Vancouver/BibTeX/RIS), đồng bộ EndNote/Zotero, quản lý thư viện tài liệu.
`bib-formatter`, `citation-formatter`, `citation-management`, `format-references-endnote`, `format-references-zotero`, `literature-management`, `literature-statistics`, `reference-style-sync`.

### 11. Thẩm định chất lượng nghiên cứu & nguy cơ sai lệch
Chấm sai lệch đúng công cụ theo thiết kế: NOS, QUADAS-2/C, ROB2, PROBAST/QUAPAS.
`case-control-study-quality-assessment-nos`, `cohort-study-quality-assessment-nos`, `diagnostic-study-quality-assessment-quadas`, `diagnostic-study-quality-assessment-quadas-2`, `probast-quality-assessment-for-prediction-model-studies`, `quadas-c-assessment-for-diagnostic-accuracy-studies`, `quality-assessment`, `quapas-quality-assessment-for-prognosis-studies`, `rct-bias-assessment-rob`, `rct-bias-assessment-rob2`, `scientific-critical-thinking`, `study-design-identifier`, `study-design-scale-selector`.

### 12. Phân tích gộp & tổng quan hệ thống (PRISMA)
TRỌN dây chuyền PRISMA: PICOS, đăng ký PROSPERO/INPLASY, sàng lọc, trích kết cục, forest/funnel plot, viết Methods/Results.
`baseline-extraction-for-clinical-trials`, `inplasy-registration-helper`, `literature-filtering`, `literature-review`, `medical-imaging-review`, `medical-review-writer-architect`, `meta-abstract-screener`, `meta-analysis`, `meta-analysis-methods-generator`, `meta-baseline-generator`, `meta-baujat-plot`, `meta-criteria-generator`, `meta-feasibility-analyzer`, `meta-forest-binary-plot`, `meta-forest-continuous-plot`, `meta-forest-model-plot`, `meta-funnel-plot`, `meta-manuscript-generator`, `meta-picos-generator`, `meta-protocol-writer`, `meta-radial-plot`, `meta-results-forest-plot-analyzer`, `meta-results-funnel-plot-generator`, `meta-results-risk-of-bias`, `meta-results-sensitivity-analysis`, `meta-rob-plot`, `meta-screening-fulltext`, `meta-search-builder`, `meta-sensitivity-plot`, `meta-title-generator`, `outcome-extraction-for-clinical-trials`, `prospero-registration-helper`, `systematic-review`, `systematic-review-screener`.

### 13. CSDL gen · protein · pathway · biến thể
Tra CSDL sinh học phân tử công khai: gen, protein, con đường tín hiệu, biến thể di truyền, chất chuyển hoá.
`alphafold-db`, `arboreto`, `bio-ontology-mapper`, `biodbnet-api`, `biogrid-orcs`, `bioservices`, `brenda-database`, `cellosaurus-api`, `cellxgene-census`, `chea-api`, `clinvar-database`, `cosmic-database`, `ena-database`, `encode-api`, `encori-api`, `ensembl-database`, `gene-database`, `gene-info`, `gene-structure-mapper`, `geo-search-api`, `gget`, `gwas-database`, `hgnc-api`, `hmdb-database`, `jaspar-api`, `kegg-api`, `kegg-database`, `metabolomics-workbench-database`, `open-targets-db`, `pdb-database`, `rare-disease-hpo-mapper`, `reactome-skill`, `singlecell-portal`, `string-database`, `uniprot-database`, `variant-annotation`, `variant-pathogenicity-predictor`.

### 14. Xử lý dữ liệu tin sinh học thô: trình tự, tệp NGS & tín hiệu
Đọc/ghi tệp sinh học thô bằng thư viện lập trình: FASTA/GenBank/FASTQ, BAM/SAM/VCF, cây loài, tín hiệu sinh lý.
`biopython`, `biopython-advanced`, `biopython-alignment`, `biopython-entrez`, `biopython-phylo`, `biopython-sequence-io`, `biopython-structure`, `circos-plot-generator`, `cnv-caller-plotter`, `deeptools`, `dnanexus-integration`, `etetoolkit`, `facs-gating-viz-style`, `fastqc-report-interpreter`, `flowio`, `geniml`, `gtars`, `lamindb`, `neurokit`, `neuropixels-analysis`, `open-source-license-check`, `pysam`, `sanger-chromatogram-qa`, `scikit-bio`, `sequence-alignment`.

### 15. Phân tích biểu hiện gen, làm giàu chức năng & mạng điều hoà
Từ ma trận biểu hiện: gen biểu hiện vi sai, GO/KEGG/GSEA/GSVA, WGCNA, mạng điều hoà, miễn dịch xâm nhập, phân cụm.
`batch-effect-correction`, `cerna-analysis`, `cibersort-immune-infiltration-analysis`, `consensus-clustering-analysis`, `crispr-screen-analyzer`, `deg-screening-analysis`, `differential-expression-analysis`, `estimate-immune-score-analysis`, `gene-protein-expression-matrix-normalization`, `gokegg-analysis`, `gsea`, `gsva-analysis-and-visualization`, `hierarchical-clustering-plot`, `immune-pathway-analysis`, `knn-imputation`, `lncrna-regulatory-network-construction-analysis`, `microbiome-diversity-reporter`, `neoantigen-predictor`, `outlier-detection-handler`, `pca-dimensionality-reduction`, `ppi-network-analysis`, `pydeseq`, `sample-correlation-analysis`, `ssgsea-immune-infiltration-analysis`, `tf-target-gene-regulatory-network`, `umap-tsne-analysis`, `volcano-plot-script`, `wgcna-analysis`.

### 16. Sinh học đơn bào & không gian (single-cell/spatial omics)
Xử lý scRNA-seq/không gian: QC, chú giải loại tế bào, quỹ đạo giả thời gian, mô hình sinh.
`anndata`, `pseudotime-trajectory-viz`, `scanpy`, `scrna-cell-type-annotator`, `scvi-tools`, `spatial-transcriptomics-mapper`.

### 17. Hoá dược, sàng lọc hợp chất, thiết kế phân tử & phổ khối
CSDL thuốc, lọc dược tính, docking phân tử, thiết kế protein, hoá lượng tử, phổ khối, PK/PD tiền lâm sàng.
`adaptyv` (lab cloud kiểm protein), `adme-property-predictor`, `chembl-database`, `chemical-structure-converter`, `clinpgx-database`, `cobrapy` (mô hình chuyển hoá), `ctd-api`, `d-molecule-ray-tracer`, `datamol`, `diffdock-molecular-docking`, `drugbank-database`, `esm` (mô hình ngôn ngữ protein), `lipinski-rule-filter`, `matchms`, `medchem`, `preclinical-pkpd-analyst`, `pubchem-database-skill`, `pyopenms-skill`, `pytdc` (bộ dữ liệu ML dược), `rowan` (hoá lượng tử cloud), `smiles-de-salter`, `torchdrug-english`, `toxicity-structure-alert`, `zinc-database`.

### 18. Học máy dự đoán & mô hình tiên lượng lâm sàng
Mô hình dự đoán trên dữ liệu bảng/omics (XGBoost, RF, SVM, SHAP), sống còn (Cox, KM, nomogram, ROC), dịch tễ học.
`decision-curve-analysis`, `decision-tree-analysis`, `elastic-net-feature-selection`, `epidemiology`, `external-model-validation`, `km-survival-curve`, `lasso-logistics-analysis`, `lightgbm-analysis`, `model-calibration-curve`, `nomogram-construction`, `pyhealth`, `rf-model-importance-analysis`, `roc-diagnostic-performance`, `scikit-survival`, `shap` (giải thích mô hình ML), `survival-analysis-km`, `survival-curve-risk-table`, `svm-model-importance-analysis`, `time-dependent-roc`, `tooluniverse-statistical-modeling`, `univariate-multivariable-cox-regression`, `xgboost-analysis`.

### 19. Thống kê tổng quát & khám phá dữ liệu
Chọn test thống kê, kiểm định giả định, khám phá cấu trúc dữ liệu, biến đổi/làm sạch bảng, dữ liệu địa lý.
`data-stats-analysis`, `data-transform`, `experimental-data-analysis`, `exploratory-data-analysis`, `geopandas`, `spreadsheet-ops`, `statistical-analysis`, `statistical-analysis-advisor`.

### 20. Hình ảnh y sinh & bệnh học số
Ảnh mô bệnh học toàn tiêu bản (WSI), DICOM, khử định danh ảnh, thước tỷ lệ hiển vi, định lượng Western blot.
`dicom-anonymizer`, `histolab`, `microscopy-scale-bar-adder`, `multi-panel-figure-assembler`, `pathml`, `pathology-roi-selector`, `pydicom`, `western-blot-quantifier`.

### 21. Vận hành, an toàn & quản lý dữ liệu phòng thí nghiệm
Pha đệm, xếp hoá chất theo nguy hiểm, xử lý chất thải, cảnh báo hạn dùng/tồn kho, bảo trì thiết bị, ELN.
`benchling-integration`, `buffer-calculator`, `chemical-storage-sorter`, `co-tank-monitor` (giám sát bình CO2 nuôi cấy), `cold-chain-risk-calculator`, `equipment-maintenance-log`, `lab-budget-forecaster`, `lab-inventory-predictor`, `lab-prep-calculations`, `labarchive-integration`, `reagent-expiry-alert`, `reagent-substitute-scout`, `sds-msds-risk-scanner`, `waste-disposal-guide`.

### 22. Vẽ đồ thị, sơ đồ & trực quan hoá khoa học
Vẽ hình lập trình + mẫu chuyên biệt: forest/volcano/heatmap, sơ đồ cơ chế, graphical abstract, mindmap.
`forest-plot-styler`, `graphical-abstract-generator`, `graphical-abstract-wizard`, `heatmap-beautifier`, `imagegenskill`, `journal-cover-prompter`, `kv-design`, `matplotlib`, `mechanism-flowchart`, `metagenomic-krona-chart`, `mindmap`, `mindmap-helper`, `mindmap-html-generator`, `motif-logo-generator`, `phylogenetic-tree-styler`, `plotly`, `sample-group-sankey-plot`, `scientific-schematics`, `seaborn`, `text-to-technical-roadmap`, `upset-plot-converter`, `volcano-plot-labeler`.

### 23. Poster, slide & trình bày hội nghị
Poster khoa học (LaTeX/PPTX), slide họp nhóm, chuyển bài báo thành PPT/video/web, hỏi-đáp và tweet hội nghị.
`academic-poster-generator`, `conference-abstract-adaptor`, `conference-abstract-writer`, `conference-poster-pitch`, `conference-tweet-generator`, `journal-club-presenter`, `latex-posters`, `paper-web`, `pdf-ppt`, `pdf-to-ppt-pack`, `poster-designer`, `poster-layout-planner`, `poster-storyline-builder`, `ppt`, `ppt-master`, `pptx-posters`, `pptx-skill`, `presentation-hook`, `q-and-a-prep-partner`, `slide-deck-for-lab-meeting`, `slide-deck-images`.

### 24. Viết các phần bản thảo IMRAD & bảng/hình đi kèm
Viết Introduction/Methods/Results/Discussion, giới thiệu pathway/phenotype, chú thích hình, Bảng 1, biên tập tiếng Anh y khoa.
`biomed-outline-generator`, `comparison-table-gen`, `discussion-composer`, `discussion-section-architect`, `figure-legend-gen`, `figure-legend-writer`, `introduction-logic-builder`, `introduction-section-writer`, `limitation-and-risk-writer`, `medical-english-precision-editor`, `method-writing`, `methods-section-writer`, `pathway-introduction-expert`, `phenotype-introduction`, `results-section-structurer`, `results-section-writer`, `study-limitations-drafter`, `table-1-generator`, `table-1-generator-advanced`, `table-narrative-writer`.

### 25. Tóm tắt, tối ưu abstract/tiêu đề & Highlights
Rút gọn thành abstract 250 từ, cắt theo giới hạn từ, tối ưu tiêu đề, viết Highlights nộp tạp chí.
`abstract-summarizer`, `abstract-trimmer`, `academic-abstract-refiner`, `academic-highlight-generator`, `title-and-abstract-optimizer`.

### 26. Kiểm liêm chính, nhất quán & khả tái lập bản thảo
Đối chiếu chuẩn báo cáo (CONSORT/STROBE/PRISMA), soát nhất quán số liệu-hình-bảng, đạo văn/COI, khả tái lập.
`academic-norm-review`, `authorship-credit-gen`, `claim-strength-calibrator`, `code-refactor-for-reproducibility`, `conflict-of-interest-checker`, `consistency-checker-across-manuscript`, `content-proofreading`, `figure-reference-checker`, `reference-integrity-checker`, `reporting-guideline-compliance-checker`, `reproducibility-check`, `result-figure-consistencycheck`, `semantic-consistency-auditor`.

### 27. Bình duyệt, phản hồi phản biện & sửa bài
Mô phỏng hội đồng bình duyệt gắt, soạn thư phản hồi từng điểm, làm mềm giọng văn, lập kế hoạch sửa bài.
`author-response-builder`, `grant-mock-reviewer`, `paper-sprint-review`, `peer-review`, `peer-review-response-drafter`, `rebuttal-letter-strategist`, `response-letter`, `response-tone-polisher`, `revision-strategy-planner`, `sci-paper-reviewer`.

### 28. Chọn tạp chí, định dạng & chuẩn bị nộp bài
Gợi ý tạp chí phù hợp, ẩn danh cho bình duyệt kín, chuyển định dạng theo tạp chí đích, cover letter, hạn nộp lại.
`article-format-adjustment`, `arxiv-preflight`, `blind-review-sanitizer`, `cover-letter-drafter`, `cover-letter-generator`, `journal-impact-factor-trend`, `journal-latest-issue`, `journal-matchmaker`, `journal-recommender`, `journal-skills`, `latex-manuscript-format-converter`, `open-access-scout`, `resubmission-deadline-tracker`, `smart-journal-monitor`, `style-journal-rewrite`, `target-journal-matcher`, `venue-templates`.

### 29. Đơn xin tài trợ, đạo đức, patent, bảo mật dữ liệu & tuân thủ quy định
Đề cương tài trợ, hồ sơ IRB/IACUC, đồng thuận, nộp FDA/EMA, ISO 13485, patent, PHI/HIPAA.
`adverse-event-narrative`, `clinical-data-cleaner`, `ectd-xml-compiler`, `grant-budget-justification`, `grant-gantt-chart-gen`, `grant-proposal-assistant`, `grant-specific-aims-writer`, `hipaa-compliance-auditor`, `iacuc-protocol-drafter`, `ib-summarizer` (tóm tắt Investigator's Brochure), `irb-application-assistant`, `iso-certification`, `medical-device-mdr-auditor`, `nsfc-grant-writer`, `patent-assistant`, `patent-claim-mapper`, `patent-landscape`, `patient-consent-simplifier`, `patient-recruitment-ad-gen`, `phi-prompt-guard`, `protocol-deviation-classifier`, `regulatory-submission`, `research-grants`, `uspto-database`.

### 30. Ghi chú lâm sàng, hồ sơ bệnh án & giao tiếp điều trị
SOAP note, tóm tắt xuất viện, chuyển tuyến, bàn giao trực, đối chiếu thuốc, mã ICD-10/CPT, kế hoạch điều trị.
`automated-soap-note-generator`, `clinical-decision-support`, `clinical-diagnostic-reasoning`, `clinical-reports`, `digital-twin-discharge-drafter`, `discharge-summary-writer`, `drug-interaction-checker`, `ehr-semantic-compressor`, `icd10-cpt-coding-assistant`, `medical-email-polisher`, `medical-scribe-dictation`, `medication-adherence-message-gen`, `medication-reconciliation`, `prior-auth-letter-drafter`, `referral-letter-generator`, `shift-handover-summarizer`, `symptom-checker-triage`, `treatment-plans`, `unstructured-medical-text-miner`.

### 31. Công cụ tính toán lâm sàng nhanh
BMI/BSA, ngày tháng y khoa (thai kỳ, tái khám), đổi đơn vị xét nghiệm, độ nhạy/đặc hiệu/NNT.
`bmi-bsa-calculator`, `date-calculator`, `ebm-calculator`, `medical-unit-converter`.

### 32. Viết truyền thông khoa học & nội dung đại chúng
Bài phổ biến khoa học, thông cáo báo chí, kịch bản video ngắn, giải thích cho người không chuyên, dịch thuật y khoa.
`biotech-pitch-deck-narrative`, `concept-explainer`, `expert-interview-generator`, `expert-interview-topics`, `faq-generator`, `graph-interpretation`, `lab-result-interpretation`, `lay-press-release-writer`, `lay-summary-for-cross-disciplinary-teams`, `lay-summary-gen`, `market-access-value`, `market-research-report-generator`, `medical-case-interpreter`, `medical-case-report-generator`, `medical-translation`, `moa-explainer` (cơ chế tác dụng thuốc), `multi-source-news-writer`, `paper-tweet-generator`, `science-popularization-article`, `scientific-podcast-summary`, `short-video-script-generator`, `soft-article-writer`, `tone-adjuster`, `visual-content-desc`.

### 33. Giáo dục y khoa, mô phỏng ca & trợ lý kiến thức
Ca lâm sàng kiểu USMLE, câu hỏi hình ảnh học, đóng vai bệnh nhân OSCE, thẻ ghi nhớ, trợ lý kiến thức y học.
`acronym-unpacker`, `anatomy-quiz-master`, `bianque` (kiến thức y học cổ truyền TQ), `hippocrates` (kiến thức y học tổng quát), `learning-tutoring`, `mendel` (kiến thức di truyền học), `note-summarizer`, `radiology-image-quiz`, `usmle-case-generator`, `virtual-patient-roleplay`.

### 34. Hồ sơ nghề nghiệp, học bổng & phát triển sự nghiệp y khoa
Personal statement, CV/biosketch, thư giới thiệu, phỏng vấn nội trú, hồ sơ LinkedIn, tìm học bổng.
`academic-cv-generator`, `anki-card-creator`, `dei-statement-drafter`, `linkedin-optimizer`, `medical-cv-resume-builder`, `networking-email-drafter`, `nih-biosketch-builder`, `personal-statement`, `postdoc-fellowship-matcher`, `recommendation-letter-assistant`, `residency-interview-prep`.

### 35. Tiện ích văn phòng, quản lý tệp & lịch trình
Đọc/ghi Word, đổi định dạng PDF/Office, OCR, quản lý/tìm/mã hoá tệp, lịch/nhắc việc, kiểm skill khác.
`api-design-principles`, `chart-style-unifier`, `docx-feedback-tracker`, `dpi-upscaler-checker`, `file-management`, `file-search`, `file-security-toolkit`, `html-to-pdf`, `id-photo-tool`, `image-ocr`, `image-processing`, `knowledge-base-search`, `markitdown`, `meeting-assistant`, `meeting-minutes`, `meeting-minutes-generator`, `pdf-extract`, `pdf-processor`, `plan-generator`, `schedule-management`, `skill-auditor`, `task-reminder`, `text-format-organizer`, `time-zone-planner`, `vector-text-fixer`, `word-read-write`.

## Cách định tuyến

1. Đọc yêu cầu, tìm từ khoá chuyên môn (bệnh, loại dữ liệu, sản phẩm đầu ra).
2. Khớp ĐÚNG MỘT nhóm ở trên theo nội dung, không theo tên nhóm nghe "gần đúng".
3. Trong nhóm đó, chọn skill HẸP NHẤT khớp việc cụ thể (vd "vẽ Kaplan-Meier" → `km-survival-curve`, không cả nhóm nếu chỉ cần một biểu đồ nhanh).
4. Yêu cầu mơ hồ, ≥2 skill hợp lý ngang nhau → hỏi lại ĐÚNG MỘT câu để chọn; không hỏi khi chỉ có một lựa chọn hợp lý.
5. Invoke bằng tên đầy đủ, vd `aipoch-medical-research:wgcna-analysis`. KHÔNG bỏ tiền tố, KHÔNG tự đoán tên nếu không có trong bảng trên.
6. Không skill nào khớp → nói rõ, gợi ý agent/skill khác của hệ nếu biết, không ép invoke skill không phù hợp.

## Ranh giới

- **Không tự bịa tên skill.** Chỉ invoke skill có tên xuất hiện nguyên văn ở trên.
- **Không thay chủ đã có trong bảng định tuyến chính của repo** (`.claude/agents/_PLUGIN-ROUTING-CONTRACT.md`, mục "Định tuyến khi NHIỀU công cụ cùng nhận một việc" ở CLAUDE.md). Việc CÓ CỔNG (cỡ mẫu G3, SAP G4, kiểm trích dẫn A12, bình duyệt G8, nộp bài G9, khử định danh G5, ca lâm sàng Cổng A/B…) vẫn qua agent/skill CHỦ (`co-mau-nghien-cuu`, `thiet-ke-nghien-cuu`, `kiem-chung-trich-dan`, `binh-duyet`, `nop-bai-phan-hoi`, `quan-ly-du-lieu`, `dieu-phoi-lam-sang`…) — router chỉ là worker phụ khi bác sĩ gọi đích danh skill aipoch, không thay quyền chủ việc có cổng.
- **Không PII.** Không đưa thông tin định danh bệnh nhân vào tham số gọi skill.
- **Không bịa PMID/DOI/số liệu.** Skill được gọi chịu trách nhiệm trích dẫn; giữ nguyên văn PMID/DOI skill trả về, không tự sửa.
- **Đầu ra lâm sàng vẫn qua `tham-dinh-dau-ra`** (guardrail 2 lớp của repo) trước khi đưa bác sĩ — router không miễn trừ bước này.
