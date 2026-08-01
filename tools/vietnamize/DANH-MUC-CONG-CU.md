# Danh mục công cụ gọi được trong Claude Code

> Sinh tự động bằng `tools/vietnamize/build_danh_muc.py`. KHÔNG sửa tay — chạy lại script sau mỗi lần cập nhật plugin.


**Tổng cộng 532 mục.** Cách gọi: gõ `/` rồi tên lệnh, hoặc nói thẳng nhu cầu để hệ thống tự chọn.


## Tra nhanh theo nhu cầu

| Cần làm gì | Gọi cái gì |
|---|---|
| Khám một ca bệnh theo 5 bước EBM | agent `dieu-phoi-lam-sang` |
| Chạy một đề tài nghiên cứu qua các cổng G0–G10 | agent `dieu-phoi-nghien-cuu` |
| Tra chứng cứ cho một câu hỏi lâm sàng | agent `tra-cuu-chung-cu` |
| Tính cỡ mẫu | agent `co-mau-nghien-cuu` |
| Thẩm định chứng cứ, tính NNT | agent `tham-dinh-grade-nnt` |
| Rà an toàn một đơn thuốc | agent `ke-don-an-toan` |
| Kiểm trích dẫn PMID/DOI có thật không | agent `kiem-chung-trich-dan` |
| Tra mã ICD-10 | `/tra-ma-icd10` |
| Tra thử nghiệm lâm sàng đang tuyển | `/tra-thu-nghiem-lam-sang` |
| Tra bản thảo tiền in (preprint) | `/tra-preprint` |
| Tra mức đồng thuận của y văn | `/tra-consensus` |
| Tra dược lý, cơ chế tác dụng của thuốc | `/tra-thuoc` |
| Bóc thông tin có cấu trúc từ bệnh án | `/trich-xuat-benh-an` |
| Khử định danh bệnh án trước khi nghiên cứu | `/khu-dinh-danh` |
| Cập nhật chứng cứ + dựng dashboard | kỹ năng `cap-nhat-chung-cu-y-khoa` |
| Không biết dùng gì | `/cong-cu-gi <việc cần làm>` |

---

## TẦNG 1 — Y khoa, nghiên cứu, tài liệu (dùng thường xuyên)  (220 mục)


### openmed-skills  (72)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `/openmed-skills:annotating-variants` | kỹ năng | Chú giải biến thể di truyền trong file VCF và chuẩn hoá danh pháp HGVS bằng công cụ mở (Ensembl VEP, SnpEff, ANNOVAR). Dùng cho nghiên cứu di truyền. Từ khoá: VCF, HGVS, variant annotation. |
| `/openmed-skills:assembling-fhir-bundles` | kỹ năng | Gói nhiều tài nguyên FHIR R4 thành một transaction Bundle hợp lệ, sẵn sàng gửi vào bệnh án điện tử. Dùng ở bước cuối trước khi ghi vào hệ thống. Từ khoá: FHIR Bundle. |
| `/openmed-skills:auditing-deid-leakage` | kỹ năng | Rà ĐỐI KHÁNG văn bản ĐÃ khử định danh để tìm định danh còn sót, và CHẶN phát hành nếu còn dù chỉ một dấu vết. Dùng như chốt kiểm cuối trước khi công bố hay chia sẻ dữ liệu. Từ khoá: leakage audit, residual PHI. |
| `/openmed-skills:auditing-deidentification-runs` | kỹ năng | Sinh vết kiểm toán có chữ ký, tái lập được và KHÔNG chứa PHI cho một lần chạy khử định danh. Dùng khi cần hồ sơ tuân thủ nộp cho hội đồng hoặc thanh tra. Từ khoá: audit trail, deidentify(audit=True). |
| `/openmed-skills:auditing-part11-trails` | kỹ năng | Sinh và kiểm vết kiểm toán kiểu 21 CFR Part 11 — ai, làm gì, lúc nào, chữ ký điện tử, chống sửa lén — cho môi trường GxP. Dùng khi đề tài chịu quản lý của cơ quan dược phẩm. Từ khoá: 21 CFR Part 11, GxP. |
| `/openmed-skills:auditing-safe-harbor-checklist` | kỹ năng | Đối chiếu kết quả khử định danh với đủ 18 nhóm định danh của HIPAA Safe Harbor và báo nguy cơ tái định danh còn lại. Dùng khi cần khẳng định dữ liệu đạt chuẩn Safe Harbor. Từ khoá: HIPAA Safe Harbor, 18 identifiers. |
| `/openmed-skills:auditing-subgroup-fairness` | kỹ năng | Soi mô hình NER/khử định danh xem có chênh lệch hiệu năng giữa các phân nhóm nhân khẩu (giới, nhóm tuổi, dân tộc). Dùng khi cần chứng minh công cụ không thiệt thòi cho nhóm bệnh nhân nào. Từ khoá: subgroup fairness audit. |
| `/openmed-skills:authoring-model-cards` | kỹ năng | Soạn 'thẻ mô hình' (model card) ghi mục đích sử dụng, số đo hiệu năng, kết quả theo phân nhóm và giới hạn đã biết. Dùng khi công bố hoặc bàn giao một mô hình. Từ khoá: model card. |
| `/openmed-skills:batch-processing-clinical-text` | kỹ năng | Chạy NER, bóc PII hoặc khử định danh HÀNG LOẠT trên nhiều bệnh án ngay tại máy, có chia mẻ, lưu điểm dừng và chạy tiếp được khi gián đoạn. Dùng khi xử lý số lượng lớn. Từ khoá: batch processing, sharding, resumable. |
| `/openmed-skills:benchmark-pii-recall` | kỹ năng | Đo độ NHẠY của mô hình PII bằng dữ liệu chuẩn tổng hợp, báo cáo tỷ lệ bắt đúng mà không in ra chính các định danh. Dùng khi cần bằng chứng model đủ an toàn trước khi xử lý hồ sơ thật. Từ khoá: PII recall benchmark. |
| `/openmed-skills:benchmarking-clinical-ner` | kỹ năng | Chấm mô hình NER trên bộ ngữ liệu chuẩn của chính bác sĩ: độ chính xác, độ nhạy, F1 ở mức thực thể, rồi phân rã lỗi theo loại. Dùng khi cần biết model sai ở đâu chứ không chỉ điểm tổng. Từ khoá: NER benchmark, precision recall F1. |
| `/openmed-skills:bridging-presidio-and-spacy` | kỹ năng | Ghép OpenMed với Microsoft Presidio, spaCy hoặc LangChain qua bộ chuyển đổi có sẵn (openmed.interop). Dùng khi đã có sẵn đường ống xử lý khác và muốn dùng chung. Từ khoá: Presidio, spaCy, LangChain interop. |
| `/openmed-skills:building-gold-corpus` | kỹ năng | Dựng dự án gán nhãn CHUẨN VÀNG tổng hợp để đánh giá model: khung nhãn, hướng dẫn gán nhãn, định dạng BIO. Dùng khi chưa có bộ dữ liệu tham chiếu để chấm điểm. Từ khoá: gold corpus, annotation guidelines. |
| `/openmed-skills:building-patient-timelines` | kỹ năng | Dựng dòng thời gian bệnh của một người từ các sự kiện đã trích, chuẩn hoá ngày và giải nghĩa mốc tương đối ('ba tuần trước'). Dùng khi cần nhìn diễn tiến bệnh theo trình tự. Từ khoá: patient timeline. |
| `/openmed-skills:building-with-openmed` | kỹ năng | Khởi động một dự án dùng OpenMed — thư viện xử lý ngôn ngữ y khoa CHẠY NGAY TRÊN MÁY (không gửi dữ liệu ra ngoài): nhận diện thực thể lâm sàng (NER), khử định danh PHI, mã hoá thuật ngữ. Dùng khi bắt đầu bất kỳ việc gì với OpenMed. Từ kh… |
| `/openmed-skills:checking-hipaa-compliance` | kỹ năng | Chạy checklist Quy tắc Riêng tư và Bảo mật của HIPAA trên toàn đường ống dữ liệu, xuất báo cáo khoảng trống TRƯỚC khi đụng vào PHI thật. Dùng khi chuẩn bị triển khai trên dữ liệu bệnh nhân. Từ khoá: HIPAA compliance checklist. |
| `/openmed-skills:choosing-openmed-models` | kỹ năng | Chọn đúng mô hình OpenMed cho một nhiệm vụ, chuyên khoa hoặc ngôn ngữ. Dùng khi phân vân 'nên dùng model nào', cần model tiếng Việt/đa ngữ, hoặc cân nhắc độ chính xác so với dung lượng máy. Từ khoá: model selection, OpenMed registry. |
| `/openmed-skills:coding-hcc-risk-adjustment` | kỹ năng | Ánh xạ bệnh mạn tính đã trích sang nhóm điều chỉnh nguy cơ CMS-HCC V28 và ước tính điểm RAF. Dùng cho bài toán chi trả theo mức nguy cơ; kết quả chỉ để hỗ trợ quyết định. Từ khoá: HCC, RAF, risk adjustment. |
| `/openmed-skills:coding-icd10` | kỹ năng | Gợi ý mã CHẨN ĐOÁN ICD-10-CM (và mã thủ thuật ICD-10-PCS) kèm lý do, luôn nhắc phải có người mã hoá xác nhận. Dùng khi cần mã hoá danh sách chẩn đoán hoặc chuẩn bị hồ sơ thanh toán. Từ khoá: ICD-10-CM, diagnosis coding, billable code. |
| `/openmed-skills:computing-ecqms` | kỹ năng | Tính chỉ số chất lượng lâm sàng điện tử (eCQM) bằng logic CQL/QDM, lấy thêm dữ kiện tử số và tiêu chí loại trừ từ bệnh án chữ tự do. Dùng cho báo cáo chất lượng và cải tiến chất lượng (QI). Từ khoá: eCQM, CQL, QDM. |
| `/openmed-skills:configuring-privacy-policies` | kỹ năng | Chọn và tuỳ chỉnh 7 hồ sơ chính sách bảo mật có sẵn của OpenMed cho việc khử định danh, hoặc tự dựng bộ sinh giá trị thay thế. Dùng khi mức che mặc định quá chặt hoặc quá lỏng so với nhu cầu. Từ khoá: privacy policy profiles. |
| `/openmed-skills:defining-cohort-phenotypes` | kỹ năng | Viết định nghĩa KIỂU HÌNH và nhóm bệnh nhân theo kiểu OHDSI ATLAS/CIRCE trên OMOP CDM, kết hợp bộ mã chuẩn với dữ kiện rút từ bệnh án. Dùng khi chọn quần thể nghiên cứu từ dữ liệu sẵn có. Từ khoá: computable phenotype, cohort definition. |
| `/openmed-skills:deidentify-a-dataset` | kỹ năng | Khử định danh các cột chữ tự do trong cả một bộ dữ liệu CSV/JSONL/Parquet, xuất ra bộ dữ liệu đã che kèm báo cáo không chứa PHI. Dùng khi cần làm sạch toàn bộ dữ liệu nghiên cứu chứ không phải một bệnh án lẻ. Từ khoá: dataset de-identifi… |
| `/openmed-skills:deidentifying-clinical-text` | kỹ năng | KHỬ ĐỊNH DANH bệnh án chữ tự do ngay trên máy — xoá, che hoặc thay thế PHI/PII bằng OpenMed deidentify(). Dùng trước khi đưa bệnh án vào nghiên cứu, chia sẻ hay phân tích. Từ khoá: de-identification, PHI removal, HIPAA. |
| `/openmed-skills:deidentifying-multilingual-text` | kỹ năng | Khử định danh bệnh án KHÔNG PHẢI TIẾNG ANH bằng tham số lang=/locale=. Dùng khi hồ sơ viết bằng tiếng Việt hoặc ngôn ngữ khác. Từ khoá: multilingual de-identification. |
| `/openmed-skills:deploying-openmed-mcp` | kỹ năng | Chạy máy chủ MCP của OpenMed để Claude Code, Codex và các ứng dụng chat gọi được trực tiếp NER, bóc PII, khử định danh. Dùng khi muốn dùng OpenMed ngay trong phiên trò chuyện. Từ khoá: MCP server. |
| `/openmed-skills:detecting-pv-signals` | kỹ năng | Tính tín hiệu bất cân xứng (PRR, ROR, EBGM, IC) trên dữ liệu FAERS/OpenFDA để phát hiện nghi ngờ về an toàn thuốc. Dùng trong nghiên cứu cảnh giác dược. Từ khoá: pharmacovigilance signal, PRR, ROR. |
| `/openmed-skills:enforcing-nophi-logging` | kỹ năng | Cài lớp chặn PHI lọt vào log, telemetry và báo cáo lỗi. Dùng khi triển khai hệ thống thật — đây là đường rò dữ liệu hay bị bỏ quên nhất. Từ khoá: no-PHI logging guard. |
| `/openmed-skills:etl-to-omop-cdm` | kỹ năng | Ánh xạ bệnh, thuốc, chỉ số đã mã hoá vào bảng OMOP CDM v5.4 (condition_occurrence, drug_exposure…). Dùng khi cần đưa dữ liệu về chuẩn chung để nghiên cứu đa trung tâm. Từ khoá: OMOP CDM, ETL. |
| `/openmed-skills:evaluating-with-leakage-gates` | kỹ năng | Chấm mô hình khử định danh hoặc NER theo bộ cổng G1a–G8 lấy tiêu chí rò rỉ PHI làm ưu tiên số một. Dùng khi cần đánh giá chính thức trước khi đưa model vào dùng. Từ khoá: leakage-first gates. |
| `/openmed-skills:exporting-bulk-fhir` | kỹ năng | Khởi động và thu nhận FHIR Bulk Data $export (toàn hệ thống, theo nhóm hoặc theo bệnh nhân), rồi đẩy thẳng luồng NDJSON vào khử định danh hàng loạt. Dùng khi rút dữ liệu quy mô lớn cho nghiên cứu. Từ khoá: Bulk FHIR export, NDJSON. |
| `/openmed-skills:exporting-to-fhir` | kỹ năng | Chuyển kết quả NER thành tài nguyên FHIR R4 — Condition, MedicationStatement, Observation. Dùng khi cần đưa dữ liệu bóc từ bệnh án vào hệ thống bệnh án điện tử. Từ khoá: FHIR R4 export. |
| `/openmed-skills:extract-clinical-entities-to-fhir` | kỹ năng | Chạy trọn một mạch: trích thực thể từ văn bản tổng hợp hoặc đã khử định danh rồi dựng luôn tài nguyên và Bundle FHIR R4. Dùng khi muốn đi thẳng từ bệnh án tới FHIR trong một bước. Từ khoá: text to FHIR. |
| `/openmed-skills:extracting-clinical-entities` | kỹ năng | Nhận diện thực thể lâm sàng trong văn bản y khoa (bệnh, thuốc, xét nghiệm, thủ thuật, giải phẫu) bằng OpenMed analyze_text. Dùng khi cần bóc thông tin có cấu trúc ra khỏi bệnh án chữ tự do. Từ khoá: clinical NER, extract entities. |
| `/openmed-skills:extracting-dicom-metadata` | kỹ năng | Đọc header file DICOM và nội dung DICOM-SR để lấy thông tin ca chụp và phần báo cáo, đồng thời gắn cờ PHI nằm lẫn trong header. Dùng khi làm việc với dữ liệu chẩn đoán hình ảnh. Từ khoá: DICOM metadata, DICOM-SR. |
| `/openmed-skills:extracting-lab-tables` | kỹ năng | Phát hiện và bóc BẢNG xét nghiệm từ PDF, bản scan và ảnh thành dòng dữ liệu có cấu trúc. Dùng khi kết quả cận lâm sàng nằm trong bảng chứ không phải câu văn. Từ khoá: lab table extraction. |
| `/openmed-skills:extracting-pii-entities` | kỹ năng | PHÁT HIỆN (không xoá) các đoạn chứa thông tin định danh trong bệnh án: họ tên, ngày tháng, số hồ sơ, điện thoại, địa chỉ. Dùng khi cần biết dữ liệu có PHI ở đâu trước khi quyết định xử lý. Từ khoá: extract_pii, PHI detection. |
| `/openmed-skills:extracting-sdoh` | kỹ năng | Bóc YẾU TỐ XÃ HỘI ẢNH HƯỞNG SỨC KHOẺ (SDOH): nhà ở bấp bênh, thiếu ăn, thất nghiệp, khó khăn đi lại, cô lập xã hội, khó khăn tài chính. Dùng khi nghiên cứu hoặc chăm sóc cần yếu tố xã hội. Từ khoá: SDOH. |
| `/openmed-skills:fetching-fhir-resources` | kỹ năng | Lấy và phân trang tài nguyên FHIR R4 (Patient, DocumentReference, DiagnosticReport, Observation, Condition) từ máy chủ FHIR, giải mã cả tệp đính kèm. Dùng khi cần kéo dữ liệu về từ bệnh án điện tử. Từ khoá: FHIR REST, paging. |
| `/openmed-skills:gating-deid-leakage` | kỹ năng | Cài cổng tự động trong CI: dựng thất bại khi độ nhạy phát hiện PHI tụt dưới ngưỡng hoặc lọt loại định danh nghiêm trọng. Dùng khi muốn cơ chế chặn chạy tự động, không phụ thuộc trí nhớ người. Từ khoá: CI leakage gate. |
| `/openmed-skills:generating-synthea-data` | kỹ năng | Sinh hồ sơ bệnh nhân GIẢ nhưng thực tế bằng MITRE Synthea (FHIR R4, C-CDA, CSV) để phát triển, kiểm thử và trình diễn. Dùng khi cần dữ liệu thử mà không đụng bệnh nhân thật. Từ khoá: Synthea, synthetic patients. |
| `/openmed-skills:generating-synthetic-surrogates` | kỹ năng | Thay PHI đã phát hiện bằng giá trị GIẢ nhưng hợp lý (tên giả, ngày giả đúng định dạng) để bệnh án vẫn đọc và phân tích được, thay vì đầy dấu [REDACTED]. Dùng khi cần dữ liệu vừa an toàn vừa còn dùng được. Từ khoá: synthetic surrogates. |
| `/openmed-skills:ingesting-clinical-documents` | kỹ năng | Biến fax scan, ảnh chụp, file CSV/CDA thành văn bản sạch sẵn sàng cho OpenMed, xử lý hoàn toàn trên máy. Dùng khi hồ sơ đầu vào là bản scan hay ảnh. Từ khoá: document ingestion, OCR. |
| `/openmed-skills:linking-umls-concepts` | kỹ năng | Nối thực thể đã trích với mã khái niệm CUI của UMLS bằng khoá UTS RIÊNG của bác sĩ (không đóng gói sẵn dữ liệu UMLS). Dùng khi cần chuẩn hoá khái niệm ở mức toàn diện nhất. Từ khoá: UMLS, CUI linking. |
| `/openmed-skills:loading-openmed-models` | kỹ năng | Nạp mô hình OpenMed từ Hugging Face Hub hoặc từ đĩa và dùng lại hiệu quả qua nhiều lần gọi. Dùng khi cần tải model, tăng tốc chạy hàng loạt hoặc quản lý bộ nhớ. Từ khoá: load model, Hugging Face. |
| `/openmed-skills:mapping-loinc` | kỹ năng | Ánh xạ tên xét nghiệm và chỉ số quan sát sang mã LOINC qua API công khai của Regenstrief. Dùng khi cần chuẩn hoá tên xét nghiệm giữa các labo khác nhau. Từ khoá: LOINC mapping. |
| `/openmed-skills:mapping-to-snomed` | kỹ năng | Ánh xạ khái niệm lâm sàng sang SNOMED CT qua máy chủ thuật ngữ CỦA CHÍNH BÁC SĨ (Ontoserver, Snowstorm…). Dùng khi cần chuẩn hoá khái niệm để trao đổi hoặc gộp dữ liệu. Từ khoá: SNOMED CT mapping. |
| `/openmed-skills:mining-pubmed-literature` | kỹ năng | Tìm và tải bài từ PubMed/PMC qua NCBI E-utilities để thu thập bằng chứng và dựng kho văn bản. Dùng khi cần quét y văn số lượng lớn, không phải tra một bài lẻ. Từ khoá: PubMed, E-utilities, PMC. |
| `/openmed-skills:normalizing-rxnorm` | kỹ năng | Chuẩn hoá tên thuốc đã trích về mã RxCUI của RxNorm qua API RxNav miễn phí. Dùng khi cần gộp biệt dược và hoạt chất về một mối để thống kê. Từ khoá: RxNorm, RxCUI, drug normalization. |
| `/openmed-skills:parsing-ccda-documents` | kỹ năng | Đọc tài liệu C-CDA/CCD dạng XML để lấy phần tường thuật và các mục đã mã hoá, phân theo mã LOINC của từng mục. Dùng khi nhận hồ sơ trao đổi giữa các cơ sở y tế. Từ khoá: C-CDA, CCD parsing. |
| `/openmed-skills:parsing-hl7v2-messages` | kỹ năng | Giải mã bản tin HL7 v2.x (ADT, ORU, MDM, ORM) thành segment/field có cấu trúc và lấy ra phần chữ tự do ở OBX-5, NTE-3. Dùng khi ghép nối với hệ thống thông tin bệnh viện. Từ khoá: HL7 v2, ADT, ORU. |
| `/openmed-skills:parsing-lab-values` | kỹ năng | Đọc trị số xét nghiệm và khoảng tham chiếu từ bệnh án, gắn cờ thấp/bình thường/cao/NGUY KỊCH. Dùng khi cần diễn giải nhanh kết quả trong văn bản. Từ khoá: lab values, reference range, critical. |
| `/openmed-skills:parsing-trial-eligibility` | kỹ năng | Chuyển tiêu chuẩn chọn/loại của thử nghiệm lâm sàng từ chữ tự do thành logic có cấu trúc, rồi đối chiếu với dữ kiện bệnh nhân. Dùng khi sàng bệnh nhân đủ điều kiện tham gia nghiên cứu. Từ khoá: trial eligibility, patient matching. |
| `/openmed-skills:pick-a-pii-model` | kỹ năng | Chọn mô hình phát hiện PII chạy trên máy theo ngôn ngữ, định dạng và dung lượng, BẮT BUỘC kiểm định độ nhạy trước khi dùng thật. Dùng khi cần cân nhắc giữa model nhẹ và model bắt sót ít. Từ khoá: PII model selection. |
| `/openmed-skills:pseudonymizing-for-gdpr` | kỹ năng | Giả danh hoá đạt chuẩn GDPR, giữ khoá liên kết ngược ở nơi tách biệt để có thể khôi phục có kiểm soát. Dùng khi nghiên cứu chịu ràng buộc GDPR châu Âu. Từ khoá: GDPR pseudonymization. |
| `/openmed-skills:querying-openfda-labels` | kỹ năng | Tra nhãn thuốc FDA, danh mục NDC, chỉ định, CẢNH BÁO ĐÓNG KHUNG và các đợt thu hồi qua API OpenFDA miễn phí. Dùng khi cần kiểm tra thông tin an toàn thuốc từ nguồn gốc. Từ khoá: OpenFDA, drug label, boxed warning. |
| `/openmed-skills:querying-terminology-service` | kỹ năng | Gọi máy chủ thuật ngữ FHIR ($validate-code, $expand, $lookup, $translate) để kiểm và mở rộng bộ mã. Dùng khi cần xác nhận một mã có hợp lệ hoặc lấy trọn nhánh mã con. Từ khoá: FHIR terminology service. |
| `/openmed-skills:reconciling-problem-lists` | kỹ năng | Gộp trùng và đối chiếu các chẩn đoán đã trích thành MỘT danh sách vấn đề sạch, có trạng thái đang mắc / đã khỏi / tiền sử. Dùng khi hồ sơ nhiều lần khám bị lặp chẩn đoán. Từ khoá: problem list reconciliation. |
| `/openmed-skills:reidentifying-text` | kỹ năng | Khử định danh CÓ THỂ ĐẢO NGƯỢC — lưu bảng ánh xạ riêng để sau này khôi phục lại PHI gốc. Dùng khi cần giả danh hoá (pseudonymization) thay vì xoá hẳn, ví dụ còn phải liên hệ lại bệnh nhân. Từ khoá: re-identification, pseudonymization. |
| `/openmed-skills:reporting-adverse-events` | kỹ năng | Chuyển biến cố bất lợi đã trích thành các trường báo cáo chuẩn FAERS / ICH E2B(R3): thuốc nghi ngờ, phản ứng theo MedDRA, mức nghiêm trọng. Dùng khi làm cảnh giác dược. Từ khoá: adverse event, FAERS, E2B, MedDRA. |
| `/openmed-skills:resolving-clinical-context` | kỹ năng | Gán PHỦ ĐỊNH, THỜI ĐIỂM và MỨC CHẮC CHẮN cho thực thể đã trích, để 'không đau ngực' không bị đếm thành có đau ngực. Dùng bắt buộc trước khi thống kê tần suất triệu chứng. Từ khoá: negation, temporality, ConText. |
| `/openmed-skills:reviewing-reidentification-risk` | kỹ năng | Chấm nguy cơ TÁI ĐỊNH DANH theo kiểu chuyên gia thẩm định: k-anonymity, l-diversity, cộng thêm phép tấn công thử nghiệm thật lên dữ liệu đã che. Dùng khi Safe Harbor chưa đủ và cần expert determination. Từ khoá: re-identification risk, k… |
| `/openmed-skills:running-openmed-ondevice` | kỹ năng | Chạy mô hình OpenMed hoàn toàn trên máy bằng MLX (chip Apple), CoreML hoặc ONNX/WebGPU, kèm cách chuyển đổi định dạng. Dùng khi dữ liệu tuyệt đối không được rời máy. Từ khoá: on-device, MLX, CoreML, ONNX. |
| `/openmed-skills:running-zeroshot-ner` | kỹ năng | Bóc tách loại thực thể TỰ ĐỊNH NGHĨA mà không cần huấn luyện lại, bằng GLiNER/GLiNER2 trong OpenMed. Dùng khi cần trích một khái niệm lạ chưa có model sẵn (ví dụ 'yếu tố nguy cơ nghề nghiệp'). Từ khoá: zero-shot NER, GLiNER. |
| `/openmed-skills:scaffolding-smart-on-fhir` | kỹ năng | Dựng khung ứng dụng SMART-on-FHIR (SMART App Launch v2, OAuth2 PKCE, scope, xử lý token) để công cụ chạy được ngay trong bệnh án điện tử. Dùng khi muốn tích hợp vào phần mềm bệnh viện. Từ khoá: SMART on FHIR. |
| `/openmed-skills:searching-clinicaltrials` | kỹ năng | Tra ClinicalTrials.gov theo bệnh, can thiệp và trạng thái tuyển bệnh, dùng API v2. Dùng khi cần biết 'đã có ai đang làm nghiên cứu này chưa' hoặc tìm thử nghiệm cho bệnh nhân. Từ khoá: ClinicalTrials.gov. |
| `/openmed-skills:segmenting-clinical-sections` | kỹ năng | Cắt bệnh án thành các mục chuẩn (Lý do khám, Bệnh sử, Tiền sử, Thuốc đang dùng, Dị ứng, Đánh giá & Kế hoạch) trước khi chạy NER. Dùng khi cần trích thông tin đúng mục, tránh lẫn tiền sử với bệnh hiện tại. Từ khoá: section segmentation. |
| `/openmed-skills:serving-openmed-rest-api` | kỹ năng | Dựng dịch vụ REST FastAPI của OpenMed cho NER, bóc PII và khử định danh, có health check và quản lý vòng đời model. Dùng khi nhiều người/nhiều ứng dụng cùng gọi chung một máy chủ. Từ khoá: REST API, FastAPI. |
| `/openmed-skills:shifting-clinical-dates` | kỹ năng | Dời ngày tháng theo từng bệnh nhân sao cho GIỮ NGUYÊN khoảng cách giữa các mốc thời gian mà vẫn đạt quy tắc ngày của HIPAA Safe Harbor. Dùng khi nghiên cứu cần trình tự thời gian nhưng không được lộ ngày thật. Từ khoá: date shifting. |
| `/openmed-skills:structuring-radiology-reports` | kỹ năng | Chuyển báo cáo chẩn đoán hình ảnh chữ tự do thành cấu trúc: tổn thương, kích thước, bên phải/trái, vị trí giải phẫu, khuyến nghị theo dõi. Dùng khi cần dữ liệu hình ảnh có cấu trúc cho nghiên cứu. Từ khoá: radiology report structuring. |
| `/openmed-skills:summarizing-clinical-notes` | kỹ năng | Tóm tắt bệnh án có CHỈ RÕ NGUỒN cho từng ý — tóm tắt một dòng, diễn biến nằm viện, tóm tắt theo vấn đề. Dùng khi cần bản tóm tắt kiểm chứng được, không phải bản viết lại tự do. Từ khoá: clinical summarization, citation-anchored. |
| `/openmed-skills:validating-us-core` | kỹ năng | Kiểm tài nguyên và Bundle FHIR R4 theo hồ sơ US Core/USCDI bằng bộ kiểm chính thức của HL7 trước khi gửi vào bệnh án điện tử. Dùng để bắt lỗi cấu trúc trước, tránh bị hệ thống từ chối. Từ khoá: US Core validation. |

### anthropic-skills  (65)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `/anthropic-skills:EBM-MASTER` | kỹ năng | Nền tảng Y HỌC BẰNG CHỨNG hợp nhất của bác sĩ: chăm sóc lâm sàng, nghiên cứu, thống kê, giám sát guideline, an toàn thuốc, quản lý kháng sinh. Dùng làm cửa vào chung cho công việc EBM. Từ khoá: EBM platform. |
| `/anthropic-skills:algorithmic-art` | kỹ năng | Tạo tranh thuật toán bằng p5.js với yếu tố ngẫu nhiên có hạt giống và tham số điều chỉnh được. Dùng cho minh hoạ sáng tạo, không phải biểu đồ dữ liệu. Từ khoá: algorithmic art, p5.js. |
| `/anthropic-skills:alphafold2` | kỹ năng | [Sinh học cấu trúc] Dự đoán cấu trúc protein đơn phân và đa phân bằng AlphaFold2 qua ColabFold. Công cụ nghiên cứu tiền lâm sàng, không dùng cho chăm sóc bệnh nhân. Từ khoá: AlphaFold2, protein structure. |
| `/anthropic-skills:antifacts` | kỹ năng | Dùng khi bác sĩ muốn MỞ hoặc CẬP NHẬT \"Antifacts\" — Trung tâm EBM theo chuyên khoa (gom cập nhật chứng cứ + 45 thang điểm lâm sàng + công cụ nghiên cứu theo chuyên khoa). Kích hoạt khi nghe \"Antifacts\", \"mở Antifacts\", \"cập nhật A… |
| `/anthropic-skills:boltz` | kỹ năng | [Sinh học cấu trúc] Dự đoán cấu trúc phức hợp protein – acid nucleic – phân tử nhỏ bằng Boltz-2. Công cụ nghiên cứu tiền lâm sàng. Từ khoá: Boltz-2, complex structure. |
| `/anthropic-skills:borzoi` | kỹ năng | [Tin sinh học] Dự đoán tín hiệu chức năng toàn hệ gen (RNA-seq, CAGE, DNase, ChIP) từ chuỗi DNA bằng Borzoi. Dùng trong nghiên cứu hệ gen. Từ khoá: Borzoi, functional genomics. |
| `/anthropic-skills:brand-guidelines` | kỹ năng | Áp bộ màu và kiểu chữ chính thức của Anthropic cho sản phẩm cần đúng nhận diện thương hiệu đó. Ít dùng cho tài liệu y khoa của bác sĩ. Từ khoá: brand guidelines. |
| `/anthropic-skills:canvas-design` | kỹ năng | Tạo ẤN PHẨM HÌNH ẢNH đẹp dạng .png/.pdf theo nguyên tắc thiết kế (poster, tờ rơi, thiệp). Dùng khi cần sản phẩm in được. Từ khoá: canvas design, poster. |
| `/anthropic-skills:cap-nhat-chung-cu-y-khoa` | kỹ năng | Sử dụng skill này khi bác sĩ yêu cầu cập nhật chứng cứ hoặc khuyến cáo hiện hành cho MỘT vấn đề lâm sàng cụ thể. Mỗi cập nhật phải kèm Web Dashboard độc lập theo mô hình MẶC ĐỊNH "Evidence Workbench" (bố cục 3 cột: bộ lọc · bảng điểm chứ… |
| `/anthropic-skills:chai1` | kỹ năng | [Sinh học cấu trúc] Dự đoán cấu trúc phức hợp bằng mô hình nền Chai-1. Công cụ nghiên cứu tiền lâm sàng. Từ khoá: Chai-1. |
| `/anthropic-skills:citation-management` | kỹ năng | Quản lý & kiểm chứng trích dẫn học thuật — phân giải PMID/DOI bắt buộc qua API miễn phí (PubMed/Crossref), đối chiếu metadata, bắt trích dẫn ma & citation washing, cảnh báo retracted/trùng, xuất danh mục Vancouver/ICMJE/AMA/BibTeX. Dùng … |
| `/anthropic-skills:clinical-evidence-rag` | kỹ năng | Cầu nối kiến thức–thực hành: trả lời câu hỏi lâm sàng bằng cách truy xuất (RAG) từ kho y văn do bác sĩ tự nạp. Dùng khi muốn tra trong kho tài liệu riêng thay vì tìm mới trên mạng. Từ khoá: clinical RAG. |
| `/anthropic-skills:compute-env-setup` | kỹ năng | Cài môi trường tính toán trên máy chủ từ xa (SSH/conda, cụm Slurm) để chạy việc nặng. Dùng khi máy cá nhân không đủ sức. Từ khoá: compute environment. |
| `/anthropic-skills:customize` | kỹ năng | Tạo và bảo trì hồ sơ agent riêng, và soạn skill mới qua công cụ repl. Dùng khi muốn tuỳ biến cách trợ lý làm việc. Từ khoá: customize agent profile. |
| `/anthropic-skills:dao-tao-slide-tai-lieu-y-khoa` | kỹ năng | Tạo và chuẩn hóa sản phẩm đào tạo y khoa và tài liệu chuyên môn — bài giảng, slide PowerPoint (.pptx), tài liệu Word (.docx), PDF, infographic/poster, bảng tóm tắt, bảng quyết định, thuật toán lâm sàng (Mermaid), checklist cờ đỏ, bảng th… |
| `/anthropic-skills:dark-analyst` | kỹ năng | Sử dụng skill này khi bác sĩ yêu cầu cập nhật chứng cứ hoặc khuyến cáo hiện hành cho MỘT vấn đề lâm sàng cụ thể. Mỗi cập nhật phải kèm Web Dashboard độc lập theo mô hình MẶC ĐỊNH "Evidence Workbench" (bố cục 3 cột: bộ lọc · bảng điểm chứ… |
| `/anthropic-skills:dashboard-master-ebm-ngoai-tru` | kỹ năng | Tạo, cập nhật hoặc kiểm định Dashboard Master EBM ngoại trú và các sổ Change Log, Evidence Register, Medication Safety, Action Register; xác minh nguồn, loại trùng, lập báo cáo điều hành tháng. |
| `/anthropic-skills:diffdock` | kỹ năng | [Sinh học cấu trúc] Dự đoán tư thế gắn của phân tử nhỏ vào protein bằng DiffDock-L (docking mù). Dùng trong sàng lọc thuốc tiền lâm sàng. Từ khoá: DiffDock, molecular docking. |
| `/anthropic-skills:doc-coauthoring` | kỹ năng | Đồng soạn tài liệu theo quy trình có cấu trúc (tài liệu kỹ thuật, đề xuất, hướng dẫn). Dùng khi viết tài liệu dài cần thống nhất bố cục. Từ khoá: doc co-authoring. |
| `/anthropic-skills:ehospital-mini` | kỹ năng | Soạn LỜI DẶN & NHẮC TÁI KHÁM ngoại trú cho bệnh nhân — mẫu in (A5/A4), mốc tái khám, cách dùng thuốc gọn, tiêu chí QUAY LẠI NGAY/đi cấp cứu (safety-netting), kế hoạch tuân thủ. Dùng khi cần phát tay tờ dặn dò sau khám. KHÔNG bịa tích hợp… |
| `/anthropic-skills:esmfold2` | kỹ năng | [Sinh học cấu trúc] Gấp cuộn toàn nguyên tử bằng ESMFold2 của Biohub, chạy được từ một chuỗi đơn. Công cụ nghiên cứu tiền lâm sàng. Từ khoá: ESMFold2. |
| `/anthropic-skills:evo2` | kỹ năng | [Tin sinh học] Chấm điểm, biểu diễn và sinh chuỗi DNA bằng mô hình nền Evo 2 ngữ cảnh dài. Dùng trong nghiên cứu hệ gen. Từ khoá: Evo 2, genomic foundation model. |
| `/anthropic-skills:fair-esm2` | kỹ năng | [Tin sinh học] Sinh vector biểu diễn (embedding) cho protein bằng ESM-2 của Meta AI. Dùng khi phân tích chuỗi protein bằng học máy. Từ khoá: ESM-2, protein embedding. |
| `/anthropic-skills:figure-composer` | kỹ năng | Dựng MỘT hình nhiều panel đạt chuẩn công bố, từ một câu khẳng định + dữ liệu nguồn. Dùng khi cần hình chính cho bài báo. Từ khoá: multi-panel figure. |
| `/anthropic-skills:figure-style` | kỹ năng | Quy tắc trình bày hình đạt chuẩn công bố (độ đọc được, nhãn, đơn vị, màu). Dùng cho hình NỘP BÀI, không cần cho biểu đồ xem nhanh. Từ khoá: figure style, publication-grade. |
| `/anthropic-skills:giao-tiep-quyet-dinh-soap` | kỹ năng | Sử dụng skill này khi cần kỹ năng GIAO TIẾP với bệnh nhân, RA QUYẾT ĐỊNH CÙNG BỆNH NHÂN (shared decision-making), báo tin xấu, hoặc GHI HỒ SƠ SOAP. Kích hoạt với "giải thích cho bệnh nhân thế nào", "bệnh nhân không chịu điều trị/lưỡng lự… |
| `/anthropic-skills:indication-dossier` | kỹ năng | Soạn HỒ SƠ CHỈ ĐỊNH ĐIỀU TRỊ: quần thể bệnh nhân, dịch tễ, sinh bệnh học, chuẩn điều trị hiện hành, bối cảnh pháp quy. Dùng cho tổng quan chuyên sâu một chỉ định. Từ khoá: indication dossier. |
| `/anthropic-skills:internal-comms` | kỹ năng | Viết các loại THÔNG BÁO NỘI BỘ theo mẫu quen dùng của đơn vị. Dùng cho thư gửi khoa/phòng, thông báo thay đổi quy trình. Từ khoá: internal communications. |
| `/anthropic-skills:ke-don-an-toan-benh-man` | kỹ năng | Sử dụng skill này khi cần KÊ ĐƠN / RÀ ĐƠN AN TOÀN cho bệnh nhân bệnh mạn ngoại trú (mọi lứa tuổi, không chỉ người cao tuổi). Kích hoạt với "đơn này có an toàn không", "thuốc có đánh nhau không/tương tác", "hiệu chỉnh liều theo thận/gan",… |
| `/anthropic-skills:kham-ngoai-tru-ebm` | kỹ năng | Sử dụng skill này khi bác sĩ cần tiếp cận hoặc ra quyết định cho MỘT ca khám ngoại trú theo Y học chứng cứ (EBM). Dẫn dắt trọn 5 bước tại phòng khám: đặt câu hỏi lâm sàng (PICO) · hỏi–khám có trọng điểm + sàng lọc cờ đỏ · chẩn đoán phân … |
| `/anthropic-skills:learn` | kỹ năng | Giải thích để HIỂU BẢN CHẤT một vấn đề (vì sao, cơ chế thế nào) thay vì làm hộ một việc. Dùng khi bác sĩ muốn học chứ không muốn nhận kết quả. Từ khoá: learn, understanding. |
| `/anthropic-skills:ligandmpnn` | kỹ năng | [Thiết kế protein] Suy ngược chuỗi có tính tới phối tử, acid nucleic và ion kim loại, bằng LigandMPNN. Công cụ nghiên cứu tiền lâm sàng. Từ khoá: LigandMPNN. |
| `/anthropic-skills:literature-review` | kỹ năng | Tìm, XÁC MINH và tổng hợp y văn — từ 'bài kinh điển của chủ đề X là bài nào' cho tới tổng quan đa nguồn đầy đủ. Dùng khi cần rà y văn có kiểm chứng nguồn. Từ khoá: literature review. |
| `/anthropic-skills:managed-model-endpoints` | kỹ năng | Đăng ký một dịch vụ mô hình (chạy cục bộ hoặc từ xa) để hệ thống tự bật/tắt khi cần. Từ khoá: model endpoint. |
| `/anthropic-skills:mcp-builder` | kỹ năng | Hướng dẫn dựng máy chủ MCP chất lượng tốt để mô hình gọi được dịch vụ bên ngoài. Dùng khi muốn nối một nguồn dữ liệu mới vào Claude. Từ khoá: MCP server builder. |
| `/anthropic-skills:morning` | kỹ năng | Dựng BẢN TIN BUỔI SÁNG dạng trang HTML, hoặc đặt lịch chạy tự động các ngày trong tuần. Chỉ dùng khi bác sĩ yêu cầu rõ. Từ khoá: morning brief. |
| `/anthropic-skills:nghien-cuu-ebm-tong-hop` | kỹ năng | >- Trợ lý NGHIÊN CỨU Y KHOA & Y HỌC CHỨNG CỨ (EBM) hợp nhất cho bác sĩ lâm sàng. Gồm 5 mô-đun: (1) Tìm & thu thập y văn; (2) Đọc & thẩm định chứng cứ; (3) Thiết kế nghiên cứu lâm sàng; (4) Thống kê & mô hình lâm sàng; (5) Viết & nộp bản … |
| `/anthropic-skills:nghien-cuu-y-khoa-chuan-quoc-te` | kỹ năng | Thực hiện, thiết kế và rà soát nghiên cứu y khoa theo chuẩn quốc tế qua cổng chất lượng G0-G9. Dùng skill này khi người dùng cần xác định câu hỏi/đề cương/protocol, hồ sơ đạo đức và đăng ký nghiên cứu, tính cỡ mẫu, thiết kế biến số/CRF/p… |
| `/anthropic-skills:nguoi-cao-tuoi-da-benh-da-thuoc` | kỹ năng | Chăm sóc toàn diện người cao tuổi suy yếu, đa bệnh lý và đa thuốc theo hướng an toàn thuốc, giảm hại và tránh điều trị quá mức. Dùng skill này bất cứ khi nào có bệnh nhân lớn tuổi kèm nhiều thuốc hoặc nhiều bệnh đồng mắc — rà soát và đối… |
| `/anthropic-skills:openfold3` | kỹ năng | [Sinh học cấu trúc] Dự đoán cấu trúc bằng OpenFold3 — bản tái dựng mã nguồn mở của AlphaFold3. Công cụ nghiên cứu tiền lâm sàng. Từ khoá: OpenFold3. |
| `/anthropic-skills:paper-lookup` | kỹ năng | Tra cứu bài báo y khoa qua API MIỄN PHÍ (PubMed E-utilities, Crossref, Europe PMC) — tìm theo PICO/từ khóa/MeSH, phân giải và xác minh PMID/DOI, lấy metadata gốc. Dùng khi cần tìm bài cho một câu hỏi, kiểm một PMID/DOI có thật, hoặc lấy … |
| `/anthropic-skills:paper-narrative` | kỹ năng | Chấm và sắp lại MẠCH TRUYỆN mà bộ hình trong bài báo đang kể — đầu vào là chính bản thảo + bộ hình. Dùng khi bài đủ dữ liệu nhưng đọc rời rạc. Từ khoá: paper narrative, figure story. |
| `/anthropic-skills:pdf-explore` | kỹ năng | Đọc sâu tài liệu PDF dài (bài báo, báo cáo) khi câu trả lời nằm rải ở nhiều chỗ trong file. Dùng khi bác sĩ đính kèm PDF và cần tổng hợp xuyên suốt, không chỉ tra một đoạn. Từ khoá: PDF exploration. |
| `/anthropic-skills:peer-review` | kỹ năng | Bình duyệt bản thảo khoa học có CẤU TRÚC — đánh giá tính hợp lệ (validity), phương pháp, thống kê, đạo đức/đăng ký, trình bày & chuẩn báo cáo, trích dẫn; soạn nhận xét đối kháng đa lăng kính + thư phản biện cho tác giả. Dùng trước khi nộ… |
| `/anthropic-skills:product-self-knowledge` | kỹ năng | Tra thông tin CHÍNH XÁC về sản phẩm của Anthropic (Claude Code, gói dịch vụ, giới hạn). Dùng bắt buộc trước khi khẳng định điều gì về sản phẩm, tránh nói theo trí nhớ. Từ khoá: product facts. |
| `/anthropic-skills:proteinmpnn` | kỹ năng | [Thiết kế protein] Suy ngược chuỗi acid amin từ khung cấu trúc protein bằng ProteinMPNN. Công cụ nghiên cứu tiền lâm sàng. Từ khoá: ProteinMPNN, inverse folding. |
| `/anthropic-skills:quan-ly-cap-nhat-ebm` | kỹ năng | Sử dụng skill này khi bác sĩ muốn QUẢN LÝ kho cập nhật EBM đã lưu (sổ cái EBM_MASTER) — xem tổng quan, tìm/lọc, duyệt và phê chuẩn các cập nhật. Kích hoạt với "quản lý EBM", "xem các cập nhật", "hàng đợi duyệt", "duyệt thẻ…", "thống kê s… |
| `/anthropic-skills:remote-compute-modal` | kỹ năng | Chạy việc cần GPU trên tài khoản Modal của bác sĩ. Dùng cho tác vụ học máy nặng. Từ khoá: Modal GPU. |
| `/anthropic-skills:remote-compute-ssh` | kỹ năng | Gửi việc tính toán lên máy chủ SSH/SLURM của bác sĩ rồi chờ và thu kết quả. Dùng sau khi đã quyết định chạy từ xa. Từ khoá: SSH, SLURM. |
| `/anthropic-skills:research-lookup` | kỹ năng | Tra cứu NGHIÊN CỨU & ĐĂNG KÝ THỬ NGHIỆM qua nguồn mở — ClinicalTrials.gov (API v2), WHO ICTRP, PROSPERO. Dùng khi cần kiểm một thử nghiệm đã đăng ký chưa, tìm nghiên cứu đang tiến hành/đã hoàn tất, đối chiếu kết cục đăng ký vs công bố (c… |
| `/anthropic-skills:scgpt` | kỹ năng | [Tế bào đơn] Biểu diễn và chú giải dữ liệu biểu hiện gen tế bào đơn bằng mô hình nền scGPT. Từ khoá: scGPT, single-cell. |
| `/anthropic-skills:scientific-writing` | kỹ năng | Viết bản thảo khoa học y khoa theo cấu trúc IMRAD, văn xuôi liền mạch, khớp CHUẨN BÁO CÁO đúng thiết kế (CONSORT/STROBE/PRISMA/SPIRIT/STARD/TRIPOD+AI; COREQ/SRQR cho định tính; SQUIRE cho QI). Dùng khi cần viết bài báo, protocol, hoặc bá… |
| `/anthropic-skills:scvi-tools` | kỹ năng | [Tế bào đơn] Phân tích RNA-seq tế bào đơn theo mô hình xác suất với scvi-tools (scVI hiệu chỉnh lô, scANVI chuyển nhãn bán giám sát). Từ khoá: scvi-tools, scVI. |
| `/anthropic-skills:self-awareness` | kỹ năng | Truy vấn cơ sở dữ liệu phiên làm việc của chính Claude Science qua host.query(). Dùng để tự kiểm tra phiên đang chạy gì. Từ khoá: session introspection. |
| `/anthropic-skills:skill-creator` | kỹ năng | Tạo skill mới, sửa và cải thiện skill sẵn có, đo hiệu quả của skill. Dùng khi bác sĩ muốn tự đóng gói một quy trình thành skill gọi được. Từ khoá: skill creator. |
| `/anthropic-skills:slack-gif-creator` | kỹ năng | Tạo ảnh động GIF tối ưu cho Slack, kèm ràng buộc kích thước và công cụ kiểm tra. Từ khoá: Slack GIF. |
| `/anthropic-skills:solublempnn` | kỹ năng | [Thiết kế protein] Suy ngược chuỗi thiên về protein TAN được, bằng SolubleMPNN. Công cụ nghiên cứu tiền lâm sàng. Từ khoá: SolubleMPNN, solubility. |
| `/anthropic-skills:statistical-analysis` | kỹ năng | Quy trình phân tích thống kê lâm sàng/nghiên cứu y khoa — mô tả dữ liệu, chọn kiểm định theo loại biến + thiết kế + giả định, hồi quy/sống còn/ROC/hiệu chỉnh, báo cáo ước lượng + 95% CI. Dùng khi cần chạy/đọc phân tích thống kê cho một đ… |
| `/anthropic-skills:tao-video-tiktok` | kỹ năng | >- Tạo video TikTok dọc (9:16, 1080x1920) từ nội dung do người dùng cung cấp, có GIỌNG ĐỌC tiếng Việt mềm mại, ngắt nghỉ tự nhiên (edge-tts HoaiMy nữ / NamMinh nam, tự lùi về giọng macOS "Linh" khi mất mạng) và PHỤ ĐỀ ĐỘNG karaoke đồng b… |
| `/anthropic-skills:tham-dinh-chung-cu-grade-nnt` | kỹ năng | Sử dụng skill này khi cần THẨM ĐỊNH NHANH một bài báo/guideline/nghiên cứu để quyết định có đáng đổi thực hành không. Kích hoạt với "bài này có đáng tin không", "đọc giúp tôi nghiên cứu này", "NNT/NNH bao nhiêu", "nguy cơ sai lệch (risk … |
| `/anthropic-skills:theme-factory` | kỹ năng | Bộ chủ đề trình bày cho slide, tài liệu, báo cáo, trang HTML — có 10 chủ đề dựng sẵn. Dùng khi muốn thống nhất phong cách một bộ sản phẩm. Từ khoá: theme, styling. |
| `/anthropic-skills:tiep-can-chan-doan-co-do-chuyen-tuyen` | kỹ năng | Sử dụng skill này khi bác sĩ tiếp cận MỘT triệu chứng/hội chứng ngoại trú và cần đi từ triệu chứng → chẩn đoán phân biệt → CỜ ĐỎ bắt buộc loại trừ → ngưỡng chuyển tuyến/cấp cứu một cách AN TOÀN. Kích hoạt với "bệnh nhân đau ngực/đau đầu/… |
| `/anthropic-skills:tuan-thu-dieu-tri` | kỹ năng | Sử dụng skill này khi cần đánh giá và cải thiện TUÂN THỦ ĐIỀU TRỊ (medication & treatment adherence) cho bệnh nhân ngoại trú. Kích hoạt khi bác sĩ nói "bệnh nhân không tuân thủ", "hay quên uống thuốc", "bỏ thuốc/tự ngưng thuốc", "uống kh… |
| `/anthropic-skills:using-model-endpoint` | kỹ năng | Gọi một mô hình đã đăng ký qua HTTP API của nó. Dùng sau khi đã đăng ký endpoint. Từ khoá: call model endpoint. |
| `/anthropic-skills:web-artifacts-builder` | kỹ năng | Bộ công cụ dựng trang HTML nhiều thành phần bằng React/Tailwind cho artifact trên claude.ai. Dùng khi cần trang tương tác phức tạp hơn dashboard mẫu. Từ khoá: web artifacts, React. |

### ebm-agents  (50)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent an-toan-nghien-cuu` | agent | An toàn người tham gia trong nghiên cứu CAN THIỆP — cảnh giác dược (AE/SAE), định nghĩa & phân độ biến cố, quy tắc dừng (stopping rules), điều lệ DSMB/DMC, báo cáo an toàn theo timeline. Dùng cho thử nghiệm lâm sàng/can thiệp. Với nghiên… |
| `agent bien-so-nghien-cuu` | agent | Đặc tả bộ BIẾN SỐ nghiên cứu đầy đủ-đúng chuẩn, gắn với câu hỏi/PICO/kết cục và loại thiết kế (RCT, cohort, case-control, cắt ngang, chẩn đoán…). Dùng khi cần liệt kê đủ nhóm biến, phân loại vai trò nhân quả (nhiễu/điều chỉnh hiệu quả/tr… |
| `agent binh-duyet` | agent | Bình duyệt bản thảo/đề cương theo checklist trước khi nộp. Dùng khi cần rà soát phản biện: tính hợp lệ phương pháp, tính đúng thống kê, tuân thủ chuẩn báo cáo (CONSORT/STROBE/PRISMA), liêm chính khoa học (trích dẫn, COI, đạo đức, khai bá… |
| `agent cap-nhat-guideline` | agent | Theo dõi guideline mới, meta-analysis và thử nghiệm lớn mới công bố; cảnh báo khi khuyến cáo cũ đã lỗi thời ("có guideline 2025 thay đổi thực hành…"). Quét nguồn neo (WHO/NICE/ESC/AHA/ADA/KDIGO/GOLD/GINA…), đối chiếu mốc cập nhật, đề xuấ… |
| `agent cau-hoi-nghien-cuu` | agent | Xác định câu hỏi nghiên cứu — chuyển một vấn đề lâm sàng thành câu hỏi PICO/PECO rõ ràng, xác định kết cục chính/phụ, đề xuất giả thuyết, và kiểm tính khả thi FINER. Dùng ở cổng G0 trước khi thiết kế. Đầu ra là nền cho tong-quan-y-van và… |
| `agent cham-soc-giam-nhe` | agent | Chăm sóc GIẢM NHẸ / cuối đời ngoại trú — kiểm soát TRIỆU CHỨNG bệnh nhân bệnh nặng/giai đoạn cuối (đau bậc WHO, khó thở, buồn nôn, táo bón, mê sảng, lo âu; thang ESAS), MỤC TIÊU CHĂM SÓC (goals of care), KẾ HOẠCH CHĂM SÓC TRƯỚC (ACP). Dù… |
| `agent chan-doan-xac-suat` | agent | Suy luận chẩn đoán theo xác suất (Bayes) tại điểm khám: XÁC SUẤT TIỀN NGHIỆM → áp TỶ SỐ KHẢ DĨ (LR+/LR−) → XÁC SUẤT HẬU NGHIỆM → đối chiếu NGƯỠNG TEST–TREAT để quyết định không làm gì / test thêm / điều trị luôn. Dùng khi câu hỏi loại CH… |
| `agent co-mau-nghien-cuu` | agent | Tính CỠ MẪU / POWER tối ưu cho nghiên cứu y khoa TRƯỚC khi thu dữ liệu (cổng G3): tự nhận diện thiết kế (RCT song song/bắt chéo, cohort, case-control, cắt ngang, độ chính xác chẩn đoán, sống còn/log-rank, non-inferiority/equivalence), ch… |
| `agent cong-cu-do-luong` | agent | Phát triển và KIỂM ĐỊNH CÔNG CỤ ĐO LƯỜNG (bộ câu hỏi, thang đo, PROM) theo chuẩn COSMIN. Dùng khi đề tài cần bộ câu hỏi/thang đo (hài lòng người bệnh, chất lượng sống, tuân thủ, mức độ triệu chứng) và phải chứng minh công cụ ĐÁNG TIN: dị… |
| `agent dao-duc-dang-ky` | agent | Sản xuất hồ sơ đạo đức và đăng ký nghiên cứu TRƯỚC khi thu thập dữ liệu (cổng G2). Dùng khi cần soạn hồ sơ Hội đồng Đạo đức (IRB), phiếu đồng thuận tham gia (ICF), bản đăng ký nghiên cứu (ClinicalTrials.gov/WHO ICTRP/đăng ký trong nước),… |
| `agent dau-man-tinh` | agent | Quản lý ĐAU MẠN TÍNH ngoại trú (đau > 3 tháng, KHÔNG do ung thư tiến triển cấp): phân loại theo CƠ CHẾ đau, chọn thang đã kiểm định (NRS, BPI, DN4), chiến lược ĐA MÔ THỨC, QUẢN LÝ OPIOID an toàn & cai/giảm liều, tầm soát trầm cảm/lo âu. … |
| `agent dien-giai-can-lam-sang` | agent | Đọc–diễn giải KẾT QUẢ CẬN LÂM SÀNG ngoại trú (panel xét nghiệm máu/nước tiểu, ECG…): gắn cờ GIÁ TRỊ NGUY KỊCH (critical value) cần xử trí/chuyển tuyến ngay. Dùng khi bác sĩ đưa bộ kết quả và hỏi "kết quả này nghĩa là gì / có nguy hiểm kh… |
| `agent dien-giai-ket-qua` | agent | Diễn giải kết quả nghiên cứu (Results Interpretation) — chuyển con số thống kê thành Ý NGHĨA LÂM SÀNG, so sánh với y văn, phân tích điểm mạnh/yếu, và đề xuất hướng nghiên cứu tiếp theo. Cầu nối giữa phan-tich-thong-ke (ra số) và viet-ban… |
| `agent dieu-phoi-lam-sang` | agent | Điều phối trọn một CA khám ngoại trú EBM theo 5 bước (Hỏi→Tìm→Thẩm định→Áp dụng→Theo dõi). Dùng khi bác sĩ NÊU MỘT CA/TÌNH HUỐNG lâm sàng ('tôi có bệnh nhân…', 'khám ca này', hỏi chẩn đoán/xử trí cho một người bệnh cụ thể) — tự chạy tuần… |
| `agent dieu-phoi-nghien-cuu` | agent | Điều phối đề tài nghiên cứu y khoa từ ý tưởng đến gói phát hành qua G0–G10. Dùng khi nhà nghiên cứu nêu MỘT đề tài/câu hỏi nghiên cứu, hoặc chạy một chặng vòng đời. CHỈ CẦN TÊN/MÔ TẢ ĐỀ TÀI là tự march G0→G10, dừng ở 6 cổng cứng: đạo đức… |
| `agent du-phong-tam-soat` | agent | Dự phòng & tầm soát dựa chứng cứ, bệnh nhân ngoại trú, theo tuổi–giới–nguy cơ: cấp 1 (lối sống, tiêm chủng, hóa dự phòng statin/aspirin), cấp 2 (ung thư cổ tử cung·vú·đại trực tràng·phổi, ĐTĐ, lipid, loãng xương, phình ĐMC bụng…), cấp 3 … |
| `agent hieu-dinh-song-ngu` | agent | Hiệu đính & dịch SONG NGỮ Việt↔Anh cho bản thảo khoa học trước khi nộp tạp chí quốc tế — dịch trung thành thuật ngữ y khoa, chống lỗi "Vietlish" (trật tự từ, mạo từ, thì, danh-động hóa, câu dài lê thê), chuẩn hóa văn phong học thuật (act… |
| `agent huong-dan-lam-sang` | agent | Cầu nối Nghiên cứu ↔ Thực hành — đặt phát hiện vào bối cảnh hướng dẫn lâm sàng hiện hành, dựng khối GRADE Evidence-to-Decision, đề xuất hoặc cập nhật khuyến cáo (chiều + độ mạnh), rồi nạp EBM_MASTER. Dùng khi cần trả lời "phát hiện này đ… |
| `agent ke-don-an-toan` | agent | Rà soát an toàn kê đơn cho bệnh nhân ngoại trú. Dùng khi cần kiểm tra tương tác thuốc, chống chỉ định, chỉnh liều theo chức năng thận/gan, đa thuốc ở người cao tuổi (Beers/STOPP-START), hiệu chỉnh theo bệnh mạn. Trả về cảnh báo phân tầng… |
| `agent ke-hoach-trien-khai` | agent | Lập KẾ HOẠCH TRIỂN KHAI đề tài (artifact A13) — nhân lực & phân công vai trò (thu thập/nhập liệu/phân tích/giám sát), TIẾN ĐỘ theo mốc cổng G0–G9 (biểu Gantt/timeline), DỰ TRÙ KINH PHÍ (nhân công, vật tư, xét nghiệm, phần mềm, công bố/AP… |
| `agent ket-qua-hoc-tap` | agent | Ghi nhận kết quả điều trị (ẩn danh) và phát hiện tín hiệu để cải tiến thực hành. Theo dõi kết cục/biến cố/không dung nạp, tổng hợp "pattern" ở nhóm bệnh nhân tương tự. CẢNH BÁO: tín hiệu nội bộ là GIẢ THUYẾT cần kiểm chứng bằng chứng — K… |
| `agent khai-thac-benh-su-kham` | agent | Khai thác BỆNH SỬ và KHÁM LÂM SÀNG CÓ TRỌNG ĐIỂM cho ca ngoại trú — hỏi bệnh có hệ thống (SOCRATES/OPQRST), điểm lại cơ quan (ROS), tiền sử, đề xuất khám thực thể theo hội chứng; trả bộ dữ liệu lâm sàng có cấu trúc cho chẩn đoán phân biệ… |
| `agent khoang-trong-nghien-cuu` | agent | Đối chiếu câu hỏi nghiên cứu với guideline/khuyến cáo hiện hành và xác định KHOẢNG TRỐNG NGHIÊN CỨU (research gap). Trả lời "câu hỏi này đã được giải đáp chưa, guideline nói gì, còn thiếu gì" để biện minh tính mới và ý nghĩa của đề tài. … |
| `agent kiem-chung-trich-dan` | agent | Kiểm chứng và quản lý trích dẫn học thuật — cổng cứng chống trích dẫn ma. Dùng khi cần xác minh mọi PMID/DOI có thật và đúng nội dung, đối chiếu tài liệu tham khảo với câu khẳng định trong bài, sinh danh mục Vancouver/AMA/APA hoặc BibTeX… |
| `agent kinh-te-y-te` | agent | Thiết kế và báo cáo PHÂN TÍCH KINH TẾ Y TẾ cho nghiên cứu/đề tài: chi phí–hiệu quả (CEA), chi phí–thỏa dụng (CUA, QALY/DALY), chi phí–lợi ích (CBA), tác động ngân sách (BIA). ICER + ngưỡng sẵn lòng chi trả (WTP); độ nhạy PSA/CEAC; mô hìn… |
| `agent loi-dan-tuan-thu` | agent | Sinh lời dặn bệnh nhân khổ A5 và kế hoạch tuân thủ điều trị tại điểm khám. Dùng khi cần in tờ dặn dò dễ hiểu (dùng thuốc, thay đổi lối sống, dấu hiệu nguy hiểm, tái khám) và/hoặc lập kế hoạch theo dõi tuân thủ. Văn phong cho bệnh nhân, k… |
| `agent meta-phan-tich` | agent | Phân tích gộp (meta-analysis) khi tổng hợp định lượng nhiều nghiên cứu — chọn mô hình hiệu ứng, tính pooled effect (OR/RR/HR/MD/SMD) + 95% CI, vẽ forest/funnel plot, đánh giá tính không đồng nhất (I²/Q/τ²) và publication bias (Egger). Ch… |
| `agent mo-hinh-tien-luong` | agent | Phát triển và KIỂM ĐỊNH MÔ HÌNH TIÊN LƯỢNG/CHẨN ĐOÁN (clinical prediction model) cho nghiên cứu y khoa theo chuẩn TRIPOD+AI; PROBAST+AI khi thẩm định mô hình đã có. Dùng khi đề tài xây/kiểm định công cụ dự báo nguy cơ. KHÔNG bịa hệ số/AU… |
| `agent nghien-cuu-dinh-tinh` | agent | Thiết kế & phân tích NGHIÊN CỨU ĐỊNH TÍNH & HỖN HỢP (mixed-methods) — chọn cách tiếp cận (hiện tượng học, grounded theory, phân tích chủ đề, nghiên cứu trường hợp), lấy mẫu có chủ đích + BÃO HÒA DỮ LIỆU, soạn câu hỏi phỏng vấn/nhóm tiêu … |
| `agent nop-bai-phan-hoi` | agent | Hỗ trợ nộp bài và phản hồi phản biện sau khi bản thảo sẵn sàng. Dùng khi cần chọn tạp chí đích (đúng phạm vi, có chỉ mục uy tín, tránh predatory), soạn cover letter, đóng gói nộp theo yêu cầu tạp chí, và viết thư phản hồi phản biện (resp… |
| `agent phan-tich-thong-ke` | agent | Phân tích thống kê SAU khi dữ liệu đã khóa — chạy đúng SAP đã khóa trên DB đã khóa, kiểm giả định, hồi quy/sống còn/meta-analysis, báo cáo ước lượng + 95% CI chuẩn báo cáo. Dùng ở G6. Mọi việc thiết kế/khóa SAP thuộc về thiet-ke-nghien-c… |
| `agent pico-lam-sang` | agent | Đặt câu hỏi lâm sàng PICO tại điểm khám — chuyển than phiền/bệnh cảnh thành câu hỏi PICO sắc, xác định KẾT CỤC QUAN TRỌNG VỚI BỆNH NHÂN (tử vong, biến cố tim mạch, chất lượng sống…) và loại câu hỏi (điều trị/chẩn đoán/tiên lượng/tác hại)… |
| `agent quan-ly-du-lieu` | agent | Quản lý, làm sạch và khóa dữ liệu nghiên cứu + đóng gói tái lặp (cổng G5). Dùng khi cần thiết kế CRF/data dictionary, luật kiểm tra dữ liệu (range/logic/consistency), khử định danh, nhật ký truy vấn, kế hoạch dữ liệu thiếu, quy trình khó… |
| `agent quan-ly-khang-dong` | agent | Quản lý KHÁNG ĐÔNG ngoại trú trọn vòng (rung nhĩ không do van, VTE, van tim cơ học): cân bằng nguy cơ huyết khối vs chảy máu (CHA₂DS₂-VASc/HAS-BLED qua thang-diem-nguy-co), CHỌN thuốc VKA vs DOAC theo chỉ định (van cơ học/hẹp van 2 lá vừ… |
| `agent quyet-dinh-chung` | agent | Cá thể hóa khuyến cáo theo bối cảnh bệnh nhân và hỗ trợ quyết định chung (shared decision-making). Điều chỉnh theo bệnh kèm, tuổi, thai kỳ, suy thận/gan, dị ứng, kinh tế, văn hóa, giá trị-ưu tiên; trình bày lợi ích–nguy cơ–bất định + lựa… |
| `agent sang-loc-co-do` | agent | Sàng lọc CỜ ĐỎ và ngưỡng CHUYỂN TUYẾN/CẤP CỨU ở BƯỚC 0 của mọi ca ngoại trú — quét nhanh dấu hiệu nguy hiểm theo triệu chứng/hội chứng (đau ngực, khó thở, đau đầu, đau bụng, sốt, đau lưng, chóng mặt, sụt cân…), nêu NGAY điều cần loại trừ… |
| `agent so-cai-ghi-nho` | agent | Thư ký sổ cái & bộ nhớ của đề tài — ghi quyết định, mốc cổng, artifact và bài học vào EBM_MASTER + bộ nhớ bền (MEMORY.md) để không mất qua phiên. Dùng sau mỗi cổng G hoàn tất, khi chốt một quyết định thiết kế/thống kê, hoặc khi cần khôi … |
| `agent tham-dinh-dau-ra` | agent | THẨM ĐỊNH ĐẦU RA ĐỘC LẬP — chốt kiểm cuối chạy SAU mỗi nhạc trưởng (dieu-phoi-lam-sang, dieu-phoi-nghien-cuu), trước khi trả bác sĩ. Soi gói 2 LỚP: Lớp 1 LIÊM CHÍNH R1–R7 (nguồn · PII · vượt cổng A/B/G · tự gán GRADE · tách 2 trục · nhãn… |
| `agent tham-dinh-do-chinh-xac-chan-doan` | agent | Thẩm định ĐỘ TIN CẬY nghiên cứu ĐỘ CHÍNH XÁC CHẨN ĐOÁN (diagnostic test accuracy): QUADAS-2 (2 test → QUADAS-C), chuẩn STARD 2015, diễn giải Se/Sp/LR/PPV-NPV theo prevalence, soi sai lệch đặc thù chẩn đoán, GRADE cho test. Dùng khi câu h… |
| `agent tham-dinh-grade-nnt` | agent | Thẩm định chất lượng chứng cứ và lượng hóa lợi ích/tác hại cho một câu hỏi lâm sàng. Dùng khi đã có (các) nghiên cứu và cần chấm GRADE, tính NNT/NNH, đánh giá nguy cơ sai lệch bằng ĐÚNG công cụ theo thiết kế (RoB 2 cho RCT; ROBINS-I V2/R… |
| `agent tham-dinh-phe-binh` | agent | Thẩm định phê bình MỘT nghiên cứu (đọc toàn văn/PDF) — tóm tắt theo PICO, đánh giá nguy cơ sai lệch theo đúng công cụ của thiết kế (RoB 2, ROBINS-I, QUADAS-3 — bản kế nhiệm QUADAS-2, Ann Intern Med 17/2/2026, doi:10.7326/ANNALS-25-02104,… |
| `agent thang-diem-nguy-co` | agent | Chọn ĐÚNG và áp dụng THANG ĐIỂM/CÔNG CỤ NGUY CƠ lâm sàng đã kiểm định cho ca ngoại trú → nguy cơ tuyệt đối + ngưỡng hành động (Cổng A): CHA₂DS₂-VASc·HAS-BLED cho rung nhĩ; ASCVD/SCORE2 cho nguy cơ tim mạch; Wells·PERC cho thuyên tắc phổi… |
| `agent theo-doi-benh-man` | agent | KẾ HOẠCH THEO DÕI DÀI HẠN & ĐIỀU TRỊ THEO MỤC TIÊU (treat-to-target) cho bệnh mạn ngoại trú (ĐTĐ, THA, lipid, COPD/hen, gút…): ĐÍCH điều trị theo guideline, cá thể hóa theo tuổi/bệnh kèm/kỳ vọng sống; TÁI KHÁM, XÉT NGHIỆM theo dõi + tần … |
| `agent thiet-ke-nghien-cuu` | agent | Thiết kế nghiên cứu y khoa TRƯỚC khi có dữ liệu — chọn thiết kế phù hợp, kiểm soát sai lệch, soạn và KHÓA kế hoạch phân tích thống kê (SAP) + khung bảng kết quả (dummy tables). Dùng ở G1/G4. Cỡ mẫu/power do co-mau-nghien-cuu đảm nhiệm (G… |
| `agent thu-thu-tai-lieu` | agent | Tìm y văn & dựng/soát tài liệu tham khảo cho nghiên cứu y khoa. TÌM (đề tài/câu hỏi): PICO → CHIẾN LƯỢC TÌM (từ khóa, MeSH, nguồn PubMed/Cochrane/Europe PMC/guideline) → LOẠI TÀI LIỆU ưu tiên (guideline, SR/MA, RCT…) → DANH MỤC → Vancouv… |
| `agent tong-quan-y-van` | agent | Thực hiện tổng quan y văn có hệ thống cho một câu hỏi nghiên cứu (PICO/PECO). Dùng khi cần rà soát bằng chứng theo PRISMA, dựng chiến lược tìm, sàng lọc, trích xuất dữ liệu, đánh giá nguy cơ sai lệch và tổng hợp (định tính/meta-analysis)… |
| `agent tra-cuu-chung-cu` | agent | Tra cứu chứng cứ y khoa cho MỘT câu hỏi lâm sàng (PICO). Dùng khi cần tìm bằng chứng tốt nhất + mới nhất để trả lời một thắc mắc tại điểm khám. Trả về câu trả lời CÓ TRÍCH DẪN (PMID/DOI), thứ tự: RAG kho → nguồn CHÍNH THỐNG (guideline hi… |
| `agent tram-cam-lo-au` | agent | Tiếp cận TRẦM CẢM & LO ÂU người lớn ngoại trú (chăm sóc ban đầu) theo CHĂM SÓC THEO BẬC — sàng lọc PHQ-9/GAD-7, khởi trị/theo dõi đáp ứng & tác dụng phụ, ngưỡng CHUYỂN tâm thần. BẮT BUỘC nối CỨNG sang-loc-co-do sàng Ý TƯỞNG TỰ SÁT/tự hại… |
| `agent trich-xuat-y-van` | agent | Trích xuất và tóm tắt có cấu trúc MỘT bài báo/nghiên cứu thành bảng dữ liệu chuẩn (PICO, thiết kế, cỡ mẫu, kết cục, hiệu ứng + CI, nguy cơ sai lệch). Dùng khi cần đọc nhanh một bài, dựng bảng trích xuất cho tổng quan hệ thống, hoặc chuẩn… |
| `agent viet-ban-thao` | agent | Viết bản thảo khoa học theo cấu trúc IMRAD, văn xuôi liền mạch, trích dẫn Vancouver/APA/AMA, tuân thủ chuẩn báo cáo (CONSORT/STROBE/PRISMA/SPIRIT/STARD/TRIPOD). Dùng khi cần viết bài báo nghiên cứu, protocol, hoặc báo cáo nghiệm thu. Quy… |

### academic-research-skills  (23)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent report_compiler_agent` | agent | Agent soạn báo cáo học thuật theo chuẩn APA 7.0 từ kết quả nghiên cứu. Chạy ở Giai đoạn 4 và 6 của dây chuyền ARS. Từ khoá: APA report drafting. |
| `agent research_architect_agent` | agent | Agent thiết kế KHUNG PHƯƠNG PHÁP: chọn hệ hình nghiên cứu, phương pháp, chiến lược dữ liệu và khung phân tích. Cho đề tài y khoa thì thiet-ke-nghien-cuu của bác sĩ đúng chuẩn hơn. Từ khoá: methodology blueprint. |
| `agent synthesis_agent` | agent | Agent TỔNG HỢP xuyên nguồn: gộp phát hiện, xử lý mâu thuẫn giữa các bằng chứng và chỉ ra khoảng trống kiến thức. Từ khoá: synthesis, evidence conflict. |
| `/ars-3w` | lệnh | Quét bài báo theo ba trục TẠI SAO / LÀM THẾ NÀO / CÁI GÌ để so sánh nhanh nhiều bài. Nhẹ hơn lit-review. Từ khoá: ARS three-way scan. |
| `/ars-abstract` | lệnh | Viết TÓM TẮT song ngữ + từ khoá. LƯU Ý: song ngữ ở đây là Trung phồn thể + Anh (zh-TW/EN), KHÔNG phải Việt–Anh; cần abstract Việt–Anh thì nói rõ trong yêu cầu. Từ khoá: ARS abstract. |
| `/ars-cache-invalidate` | lệnh | Xoá kết quả kiểm trích dẫn đã lưu tạm của một hoặc nhiều tài liệu, buộc kiểm lại từ đầu. Dùng khi nghi kết quả cũ đã lỗi thời. Từ khoá: ARS cache invalidate. |
| `/ars-citation-check` | lệnh | Xuất BÁO CÁO LỖI TRÍCH DẪN cho bản thảo. LƯU Ý: với bài y khoa nên dùng agent kiem-chung-trich-dan của bác sĩ vì nó xác minh PMID/DOI thật và tra bài bị rút. Từ khoá: ARS citation check. |
| `/ars-disclosure` | lệnh | Soạn câu KHAI BÁO SỬ DỤNG AI theo yêu cầu riêng của từng tạp chí. Dùng khi nộp bài — ICMJE Mục V bắt buộc khai. Từ khoá: ARS AI disclosure. |
| `/ars-format-convert` | lệnh | Chuyển bản thảo qua lại giữa LaTeX / DOCX / PDF / Markdown. Dùng khi tạp chí đòi định dạng khác. Từ khoá: ARS format convert. |
| `/ars-full` | lệnh | Chạy TRỌN dây chuyền bài báo học thuật: tra cứu → viết → bình duyệt → sửa → hoàn thiện. Tốn nhiều token nhất trong bộ ARS. Từ khoá: ARS full pipeline. |
| `/ars-lit-review` | lệnh | Dựng THƯ MỤC CÓ CHÚ GIẢI trình bày theo dạng bài báo. Dùng khi cần phần tổng quan tài liệu; tổng quan hệ thống theo PRISMA thì dùng agent tong-quan-y-van. Từ khoá: ARS lit-review. |
| `/ars-mark-read` | lệnh | Đánh dấu 'người đã đọc thật' cho một hoặc nhiều tài liệu trích dẫn. Dùng để phân biệt bài đã đọc toàn văn với bài chỉ đọc tóm tắt. Từ khoá: ARS mark read. |
| `/ars-outline` | lệnh | Dựng DÀN Ý chi tiết kèm bản đồ bằng chứng cho từng mục, KHÔNG viết thành văn. Dùng khi muốn chốt khung trước khi viết. Từ khoá: ARS outline. |
| `/ars-plan` | lệnh | Lập kế hoạch bài viết theo lối HỎI ĐÁP SOCRATIC, đi từng chương một. Dùng khi chưa rõ nên viết gì, cần người hỏi ngược để làm rõ ý. Từ khoá: ARS plan mode. |
| `/ars-rebuttal-audit` | lệnh | Soi lại THƯ PHẢN HỒI đã viết xem đã trả lời hết từng ý phản biện chưa (chỉ góp ý, không viết thay). Dùng trước khi gửi thư đi. Từ khoá: ARS rebuttal audit. |
| `/ars-reviewer` | lệnh | Chạy hội đồng bình duyệt mô phỏng đầy đủ trên bản thảo. Dùng khi muốn biết bài sẽ bị chê ở đâu trước khi nộp. Từ khoá: ARS reviewer panel. |
| `/ars-revision` | lệnh | Sinh BẢN SỬA của bản thảo kèm phần trả lời góp ý (R&R). Dùng sau khi đã có nhận xét của phản biện. Từ khoá: ARS revision. |
| `/ars-revision-coach` | lệnh | Phân tích góp ý của phản biện thành LỘ TRÌNH SỬA BÀI + khung thư phản hồi. Dùng ngay khi vừa nhận quyết định 'sửa và nộp lại'. Từ khoá: ARS revision coach. |
| `/ars-unmark-read` | lệnh | Gỡ dấu 'đã đọc' đã gắn trước đó cho tài liệu trích dẫn. Dùng khi đánh dấu nhầm. Từ khoá: ARS unmark read. |
| `/academic-research-skills:academic-paper` | kỹ năng | Dây chuyền VIẾT BÀI BÁO HỌC THUẬT tổng quát (12 agent, 11 chế độ: viết trọn, lập dàn ý, sửa bài, tóm tắt, tổng quan tài liệu, đổi định dạng, kiểm trích dẫn). LƯU Ý: chuẩn chung cho mọi ngành, KHÔNG theo CONSORT/STROBE — bài y khoa nên dù… |
| `/academic-research-skills:academic-paper-reviewer` | kỹ năng | Mô phỏng HỘI ĐỒNG BÌNH DUYỆT nhiều góc nhìn: 1 tổng biên tập + 3 phản biện + người bảo vệ, mỗi vai một tính cách khác nhau. Dùng khi muốn thử phản biện bản thảo trước khi nộp thật. Từ khoá: peer review simulation. |
| `/academic-research-skills:academic-pipeline` | kỹ năng | Điều phối TRỌN VÒNG bài báo học thuật: tra cứu → viết → kiểm liêm chính → bình duyệt → sửa → bình duyệt lại. Dùng khi muốn chạy một mạch thay vì gọi từng chế độ. Tốn nhiều token (một lần chạy đầy đủ khoảng 4–6 USD). Từ khoá: full pipeline. |
| `/academic-research-skills:deep-research` | kỹ năng | Đội 13 agent NGHIÊN CỨU SÂU cho bất kỳ chủ đề nào, 8 chế độ (nghiên cứu đầy đủ, tóm lược nhanh, so sánh…). Dùng cho chủ đề ngoài y khoa hoặc cần quét rộng; câu hỏi lâm sàng vẫn nên đi qua tra-cuu-chung-cu để có PMID/DOI. Từ khoá: deep re… |

### user-skills  (10)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `/citation-management` | kỹ năng | Quản lý trích dẫn học thuật: tìm bài trên PubMed (E-utilities miễn phí) và Google Scholar, trích xuất metadata chính xác, kiểm chứng trích dẫn, sinh BibTeX đúng chuẩn. Dùng khi cần tìm bài, xác minh thông tin trích dẫn, đổi DOI→BibTeX ho… |
| `/clinical-decision-support` | kỹ năng | Tạo tài liệu hỗ trợ quyết định lâm sàng (CDS): phân tích nhóm bệnh nhân (cohort) theo dấu ấn sinh học, báo cáo khuyến cáo điều trị dựa trên bằng chứng kèm thuật toán quyết định và phân độ GRADE; phân tích thống kê (HR, đường sống còn); x… |
| `/clinical-reports` | kỹ năng | Viết báo cáo lâm sàng: case report (chuẩn CARE), báo cáo chẩn đoán (X-quang/giải phẫu bệnh/xét nghiệm), báo cáo thử nghiệm lâm sàng (ICH-E3) và hồ sơ bệnh án (SOAP, H&P, tóm tắt xuất viện). Kèm template và công cụ kiểm tra. Mọi đầu ra kè… |
| `/literature-review` | kỹ năng | Thực hiện tổng quan y văn có hệ thống (systematic review, tổng quan, meta-analysis) bằng các CSDL học thuật MIỄN PHÍ (PubMed E-utilities, PMC, bioRxiv, medRxiv, OpenAlex, Crossref, Semantic Scholar). Dùng khi cần tổng hợp bằng chứng cho … |
| `/paper-lookup` | kỹ năng | Tra cứu bài báo khoa học qua REST API MIỄN PHÍ của nhiều CSDL: PubMed, PMC (toàn văn), bioRxiv, medRxiv, arXiv, OpenAlex, Crossref, Semantic Scholar, CORE, Unpaywall. Dùng khi cần tìm bài theo chủ đề, tra DOI/PMID, lấy abstract/toàn văn,… |
| `/peer-review` | kỹ năng | Bình duyệt bản thảo/đề cương theo checklist: đánh giá phương pháp, tính hợp lệ thống kê, tuân thủ chuẩn báo cáo (CONSORT/STROBE) và góp ý mang tính xây dựng. Dùng khi viết phản biện chính thức hoặc rà soát bản thảo trước khi nộp. |
| `/research-lookup` | kỹ năng | Tra cứu thông tin nghiên cứu hiện hành qua PubMed E-utilities (MIỄN PHÍ, không cần API key). Dùng để tìm bài báo, thu thập dữ liệu nghiên cứu, kiểm chứng thông tin khoa học cho câu hỏi lâm sàng. Đã LOẠI BỎ mọi backend trả phí (parallel.a… |
| `/scientific-writing` | kỹ năng | Viết bản thảo khoa học theo cấu trúc IMRAD, văn xuôi liền mạch (không gạch đầu dòng), trích dẫn Vancouver/APA/AMA, tuân thủ chuẩn báo cáo (CONSORT/STROBE/PRISMA). Dùng khi viết bài báo nghiên cứu hoặc bản thảo nộp tạp chí. Quy trình 2 bư… |
| `/statistical-analysis` | kỹ năng | Hướng dẫn phân tích thống kê: chọn test phù hợp với dữ liệu, kiểm tra giả định, tính cỡ mẫu (power), trình bày kết quả chuẩn APA. Dùng khi cần chọn kiểm định hoặc báo cáo thống kê cho nghiên cứu y khoa. (Để chạy mô hình cụ thể bằng code,… |
| `/treatment-plans` | kỹ năng | Soạn kế hoạch điều trị y khoa ngắn gọn (3-4 trang) xuất LaTeX/PDF cho nhiều chuyên khoa: nội khoa chung, phục hồi chức năng, sức khỏe tâm thần, quản lý bệnh mạn, chu phẫu, giảm đau. Dùng khung mục tiêu SMART, can thiệp dựa bằng chứng. Kè… |

---

## TẦNG 2 — Kỹ thuật, dùng khi sửa chính hệ EBM  (73 mục)


### claude-code-harness  (42)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent advisor` | agent | [Lập trình] Agent cố vấn KHÔNG thực thi: chỉ trả về hướng xử lý cho yêu cầu mà agent thợ gửi lên. Từ khoá: advisor agent. |
| `agent reviewer` | agent | [Lập trình] Agent rà soát CHỈ ĐỌC: đưa phán quyết dựa trên hợp đồng công việc và tài liệu rà soát. Từ khoá: reviewer agent. |
| `agent worker` | agent | [Lập trình] Agent thợ chính: thực hiện một việc trọn gói — viết mã, tự kiểm trước, xác minh và chuẩn bị commit. Từ khoá: worker agent. |
| `/claude-code-harness:agent-browser` | kỹ năng | [Lập trình] Điều khiển trình duyệt tự động: mở trang, điền biểu mẫu, chụp màn hình, thu thập dữ liệu. Từ khoá: browser automation. |
| `/claude-code-harness:auth` | kỹ năng | [Lập trình] Hỗ trợ dựng phần đăng nhập và thanh toán (Clerk, Supabase Auth, Stripe). Từ khoá: authentication, payment. |
| `/claude-code-harness:breezing` | kỹ năng | [Lập trình] Chế độ chạy theo NHÓM — tên gọi cũ tương đương harness-work có điều phối nhiều agent. Từ khoá: team execution. |
| `/claude-code-harness:cc-cursor-cc` | kỹ năng | [Lập trình] Chuyển ý tưởng qua Cursor thẩm định, cập nhật Plans.md rồi bàn giao ngược lại. Từ khoá: Cursor round-trip. |
| `/claude-code-harness:cc-update-review` | kỹ năng | [Lập trình] Chốt chất lượng khi tích hợp bản cập nhật Claude/Codex; bắt trường hợp chỉ thêm tài liệu mà chưa có mã thật. Từ khoá: update review. |
| `/claude-code-harness:ci` | kỹ năng | [Lập trình] Chữa cháy CI: build đỏ, test hỏng, pipeline lỗi. Từ khoá: CI failure, build error. |
| `/claude-code-harness:crud` | kỹ năng | [Lập trình] Dựng nhanh khung thêm/sửa/xoá dữ liệu và các điểm cuối API. Từ khoá: CRUD, API endpoint. |
| `/claude-code-harness:cursor-ask` | kỹ năng | [Lập trình] Hỏi Cursor ở chế độ CHỈ ĐỌC để điều tra, bàn thiết kế, phản biện — không cho sửa file. Từ khoá: cursor ask. |
| `/claude-code-harness:cursor-do` | kỹ năng | [Lập trình] Giao MỘT việc có sửa file cho Cursor trong nhánh làm việc tách biệt rồi thu kết quả về. Từ khoá: cursor do. |
| `/claude-code-harness:cursor-rescue` | kỹ năng | [Lập trình] Chẩn đoán và khắc phục khi nền Cursor gặp sự cố. Từ khoá: cursor rescue. |
| `/claude-code-harness:cursor-review` | kỹ năng | [Lập trình] Nhờ Cursor rà soát như ý kiến thứ hai; kết luận cuối vẫn thuộc về bên chính. Từ khoá: cursor review. |
| `/claude-code-harness:cursor-setup` | kỹ năng | [Lập trình] Cài và kiểm tra nền Cursor cho harness. Từ khoá: cursor setup. |
| `/claude-code-harness:deploy` | kỹ năng | [Lập trình] Triển khai lên Vercel/Netlify. KHÔNG dùng cho hệ EBM (chạy cục bộ, không đưa dữ liệu bệnh nhân lên máy chủ ngoài). Từ khoá: deploy, Vercel. |
| `/claude-code-harness:generate-slide` | kỹ năng | [Lập trình] Sinh slide giới thiệu dự án. Chỉ chạy khi gọi thẳng bằng lệnh. Từ khoá: generate slide. |
| `/claude-code-harness:generate-video` | kỹ năng | [Lập trình] Sinh video minh hoạ sản phẩm. Chỉ chạy khi gọi thẳng bằng lệnh. Từ khoá: generate video. |
| `/claude-code-harness:gogcli-ops` | kỹ năng | [Lập trình] Thao tác Google Workspace bằng dòng lệnh (Drive, Sheets, Docs, Slides). Từ khoá: Google Workspace CLI. |
| `/claude-code-harness:harness-accept` | kỹ năng | [Lập trình] Dựng trang HTML NGHIỆM THU cho người không rành kỹ thuật xem trước khi quyết định phát hành. Từ khoá: acceptance demo. |
| `/claude-code-harness:harness-loop` | kỹ năng | [Lập trình] Chạy việc DÀI HƠI theo vòng lặp, tự hẹn giờ quay lại với ngữ cảnh mới. Dùng cho việc nhiều giờ. Từ khoá: harness loop. |
| `/claude-code-harness:harness-orchestration` | kỹ năng | [Lập trình] Xem phiên/dự án này đã điều phối bao nhiêu việc qua các nền khác nhau (Claude / Codex / Cursor). Từ khoá: orchestration report. |
| `/claude-code-harness:harness-plan` | kỹ năng | [Lập trình] Lập KẾ HOẠCH công việc có kiểm chứng, quản lý Plans.md và đồng bộ tiến độ. Dùng khi bắt đầu một hạng mục sửa hệ thống. Từ khoá: harness plan, Plans.md. |
| `/claude-code-harness:harness-plan-brief` | kỹ năng | [Lập trình] Dựng trang HTML TÓM TẮT KẾ HOẠCH dễ đọc cho người không rành kỹ thuật, trước khi bắt tay làm. Từ khoá: plan brief. |
| `/claude-code-harness:harness-progress` | kỹ năng | [Lập trình] Dựng trang HTML THEO DÕI TIẾN ĐỘ phiên làm việc để liếc nhanh. Từ khoá: progress tracker. |
| `/claude-code-harness:harness-release` | kỹ năng | [Lập trình] Tự động hoá phát hành theo Keep a Changelog + GitHub, có một cổng xác nhận trước khi chạy. Từ khoá: harness release. |
| `/claude-code-harness:harness-review` | kỹ năng | [Lập trình] RÀ SOÁT mã nguồn, kế hoạch và phạm vi từ nhiều góc; kiểm bảo mật và chất lượng. Từ khoá: harness review, code review. |
| `/claude-code-harness:harness-setup` | kỹ năng | [Lập trình] Khởi tạo dự án, cài công cụ, cấu hình agent, dựng bộ nhớ và đồng bộ bản sao skill. Từ khoá: harness setup, init. |
| `/claude-code-harness:harness-sync` | kỹ năng | [Lập trình] Đối chiếu Plans.md với mã thật, phát hiện lệch, cập nhật mốc và rút kinh nghiệm. Dùng khi hỏi 'đang làm tới đâu'. Từ khoá: harness sync, drift. |
| `/claude-code-harness:harness-work` | kỹ năng | [Lập trình] THỰC THI các việc trong Plans.md, từ một việc lẻ tới chạy song song cả nhóm. Từ khoá: harness work, implement. |
| `/claude-code-harness:maintenance` | kỹ năng | [Lập trình] Dọn dẹp và lưu trữ file: Plans.md phình to, nhật ký phiên, log cũ. Từ khoá: cleanup, archiving. |
| `/claude-code-harness:memory` | kỹ năng | [Lập trình] Quản lý bộ nhớ dự án và tìm kiếm xuyên công cụ; giữ decisions.md và patterns.md. Từ khoá: memory, SSOT. |
| `/claude-code-harness:notebookLM` | kỹ năng | [Lập trình] Sinh file YAML và slide cho NotebookLM. Từ khoá: NotebookLM. |
| `/claude-code-harness:principles` | kỹ năng | [Lập trình] Nguyên tắc phát triển, hướng dẫn an toàn và quy tắc sửa mã theo diff. Từ khoá: principles, safety. |
| `/claude-code-harness:session` | kỹ năng | [Lập trình] Cửa sổ quản lý PHIÊN làm việc gộp một chỗ: khởi tạo, bộ nhớ, trạng thái. Từ khoá: session management. |
| `/claude-code-harness:session-control` | kỹ năng | [Lập trình] Điều khiển tiếp tục hoặc rẽ nhánh một phiên làm việc. Từ khoá: session resume, fork. |
| `/claude-code-harness:session-init` | kỹ năng | [Lập trình] Kiểm tra đầu phiên: trạng thái Plans.md, tình trạng git, gói khôi phục bộ nhớ. Skill nội bộ, thường không gọi trực tiếp. Từ khoá: session init. |
| `/claude-code-harness:session-memory` | kỹ năng | [Lập trình] Bàn giao giữa các phiên và lưu bài học lâu dài. Skill nội bộ. Từ khoá: session memory. |
| `/claude-code-harness:session-state` | kỹ năng | [Lập trình] Quản lý chuyển trạng thái phiên theo từng mốc công việc. Skill nội bộ. Từ khoá: session state. |
| `/claude-code-harness:ui` | kỹ năng | [Lập trình] Dựng thành phần giao diện: khối mở đầu, biểu mẫu, thông báo, trang liên hệ. Từ khoá: UI components. |
| `/claude-code-harness:vibecoder-guide` | kỹ năng | [Lập trình] Hướng dẫn người KHÔNG chuyên kỹ thuật: nên hỏi gì tiếp theo, mô tả công việc thế nào cho máy hiểu. Từ khoá: vibecoder coaching. |
| `/claude-code-harness:workflow-guide` | kỹ năng | [Lập trình] Hướng dẫn quy trình hai agent Cursor ↔ Claude Code phối hợp. Từ khoá: two-agent workflow. |

### understand-anything  (19)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent architecture-analyzer` | agent | [Đọc hiểu mã] Agent nhận diện các TẦNG KIẾN TRÚC và xếp mỗi file vào đúng một tầng. Từ khoá: architecture layers. |
| `agent article-analyzer` | agent | [Đọc hiểu mã] Agent phân tích file markdown để rút thực thể, luận điểm và quan hệ ngầm. Từ khoá: article analyzer. |
| `agent assemble-reviewer` | agent | [Đọc hiểu mã] Agent soi kết quả gộp bản đồ để bắt lỗi ngữ nghĩa mà script không thấy, khôi phục nút/cạnh bị rơi. Từ khoá: assemble reviewer. |
| `agent design-analyzer` | agent | [Đọc hiểu mã] Agent phân tích cấu trúc thiết kế Figma và bổ sung diễn giải ngữ nghĩa. Từ khoá: design analyzer. |
| `agent domain-analyzer` | agent | [Đọc hiểu mã] Agent rút tri thức nghiệp vụ: miền, luồng nghiệp vụ và các bước xử lý. Từ khoá: domain analyzer. |
| `agent file-analyzer` | agent | [Đọc hiểu mã] Agent phân tích từng lô file nguồn thành nút và cạnh của bản đồ tri thức. Từ khoá: file analyzer. |
| `agent graph-reviewer` | agent | [Đọc hiểu mã] Agent kiểm tính đúng, đủ và chất lượng của bản đồ tri thức rồi ra phán quyết duyệt hay không. Từ khoá: graph reviewer. |
| `agent knowledge-graph-guide` | agent | [Đọc hiểu mã] Agent hướng dẫn cách đọc, truy vấn và làm việc với bản đồ tri thức đã dựng. Từ khoá: knowledge graph guide. |
| `agent project-scanner` | agent | [Đọc hiểu mã] Agent quét thư mục dự án, lập danh mục file, ngôn ngữ, khung công nghệ và ước lượng độ phức tạp. Từ khoá: project scanner. |
| `agent tour-builder` | agent | [Đọc hiểu mã] Agent thiết kế lộ trình 5–15 bước dẫn người mới đi qua kiến trúc và khái niệm chính của dự án. Từ khoá: guided tour. |
| `/understand-anything:understand` | kỹ năng | [Đọc hiểu mã] Phân tích cả một kho mã thành BẢN ĐỒ TRI THỨC tương tác để hiểu kiến trúc, thành phần và quan hệ. Hữu ích khi cần nắm lại hệ EBM đã lớn. Từ khoá: knowledge graph, codebase. |
| `/understand-anything:understand-chat` | kỹ năng | [Đọc hiểu mã] Hỏi đáp về kho mã dựa trên bản đồ tri thức đã dựng. Từ khoá: ask codebase. |
| `/understand-anything:understand-dashboard` | kỹ năng | [Đọc hiểu mã] Mở bảng điều khiển web để xem trực quan bản đồ tri thức của kho mã. Từ khoá: dashboard, visualize. |
| `/understand-anything:understand-diff` | kỹ năng | [Đọc hiểu mã] Phân tích thay đổi git hoặc pull request: đổi những gì, ảnh hưởng tới đâu. Từ khoá: analyze diff, PR. |
| `/understand-anything:understand-domain` | kỹ năng | [Đọc hiểu mã] Rút ra tri thức NGHIỆP VỤ từ mã nguồn và dựng sơ đồ luồng nghiệp vụ. Từ khoá: domain knowledge, business flow. |
| `/understand-anything:understand-explain` | kỹ năng | [Đọc hiểu mã] Giải thích sâu MỘT file, hàm hoặc mô-đun cụ thể. Từ khoá: explain file, deep dive. |
| `/understand-anything:understand-figma` | kỹ năng | [Đọc hiểu mã] Phân tích file Figma qua API và dựng bản đồ thiết kế (trang, màn hình, thành phần). Từ khoá: Figma design graph. |
| `/understand-anything:understand-knowledge` | kỹ năng | [Đọc hiểu mã] Phân tích một kho tri thức dạng wiki và dựng bản đồ thực thể liên kết. Từ khoá: knowledge base graph. |
| `/understand-anything:understand-onboard` | kỹ năng | [Đọc hiểu mã] Sinh tài liệu HƯỚNG DẪN NHẬP MÔN cho người mới tham gia dự án. Từ khoá: onboarding guide. |

### codex  (12)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent codex-rescue` | agent | [Codex] Agent cứu hộ: dùng khi cần lượt cài đặt hoặc chẩn đoán thứ hai, hoặc giao hẳn một việc lớn cho Codex. Từ khoá: codex rescue agent. |
| `/adversarial-review` | lệnh | [Codex] Nhờ Codex rà soát theo lối PHẢN BIỆN — chất vấn chính cách tiếp cận và lựa chọn thiết kế. Từ khoá: adversarial review. |
| `/cancel` | lệnh | [Codex] Huỷ một việc Codex đang chạy nền trong kho mã này. Từ khoá: codex cancel. |
| `/rescue` | lệnh | [Codex] Giao việc điều tra, sửa lỗi hoặc cứu hộ tiếp nối cho Codex. Dùng khi bí hướng và muốn góc nhìn thứ hai. Từ khoá: codex rescue. |
| `/result` | lệnh | [Codex] Xem kết quả cuối đã lưu của một việc Codex đã hoàn thành. Từ khoá: codex result. |
| `/review` | lệnh | [Codex] Nhờ Codex rà soát mã dựa trên trạng thái git hiện tại. Từ khoá: codex review. |
| `/setup` | lệnh | [Codex] Kiểm Codex CLI đã sẵn sàng chưa và bật/tắt cổng rà soát trước khi dừng phiên. Từ khoá: codex setup. |
| `/status` | lệnh | [Codex] Xem các việc Codex đang chạy và vừa xong trong kho mã này. Từ khoá: codex status. |
| `/transfer` | lệnh | [Codex] Chuyển phiên Claude Code hiện tại thành một luồng Codex tiếp tục được. Từ khoá: codex transfer. |
| `/codex:codex-cli-runtime` | kỹ năng | [Codex] Hợp đồng nội bộ để gọi runtime Codex từ Claude Code. Skill nội bộ, không gọi trực tiếp. Từ khoá: codex runtime. |
| `/codex:codex-result-handling` | kỹ năng | [Codex] Hướng dẫn nội bộ về cách trình bày kết quả Codex trả về cho người dùng. Từ khoá: codex result. |
| `/codex:gpt-5-4-prompting` | kỹ năng | [Codex] Hướng dẫn nội bộ soạn câu lệnh cho Codex/GPT-5.4 khi viết mã, rà soát, chẩn đoán, tra cứu. Từ khoá: GPT-5.4 prompting. |

---

## TẦNG 3 — Ngoài chuyên môn (biết là có, hiếm khi dùng)  (239 mục)


### ruflo-cost-tracker  (22)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent cost-analyst` | agent | [Chi phí] Agent phân tích chi phí theo agent và mô hình, quy ra tiền và đề xuất tối ưu. Từ khoá: cost analyst. |
| `/ruflo-cost` | lệnh | [Chi phí] Lệnh chung về chi phí: báo cáo, xem chi tiết, đặt hạn mức. Từ khoá: cost operations. |
| `/ruflo-cost-tracker:cost-anomaly` | kỹ năng | [Chi phí] Phát hiện phiên tiêu bất thường bằng phương pháp MAD. Từ khoá: cost anomaly. |
| `/ruflo-cost-tracker:cost-benchmark` | kỹ năng | [Chi phí] Chạy bộ đo chuẩn để so hiệu quả giữa các mô hình. Từ khoá: cost benchmark. |
| `/ruflo-cost-tracker:cost-booster-edit` | kỹ năng | [Chi phí] Sửa mã bằng máy WASM tăng tốc, rẻ hơn gọi mô hình. Từ khoá: agent booster. |
| `/ruflo-cost-tracker:cost-booster-route` | kỹ năng | [Chi phí] Điều hướng việc qua bộ tăng tốc khi có thể để giảm chi phí. Từ khoá: booster routing. |
| `/ruflo-cost-tracker:cost-budget-check` | kỹ năng | [Chi phí] Đối chiếu chi tiêu tích luỹ với hạn mức đã đặt. Từ khoá: budget check. |
| `/ruflo-cost-tracker:cost-burn` | kỹ năng | [Chi phí] Xu hướng TỐC ĐỘ tiêu tiền theo thời gian, có cảnh báo khi lệch. Từ khoá: burn rate. |
| `/ruflo-cost-tracker:cost-compact-context` | kỹ năng | [Chi phí] Nén ngữ cảnh để giảm token. Từ khoá: compact context. |
| `/ruflo-cost-tracker:cost-conversation` | kỹ năng | [Chi phí] Xem chi phí theo từng cuộc trò chuyện. Từ khoá: per-conversation cost. |
| `/ruflo-cost-tracker:cost-counterfactual` | kỹ năng | [Chi phí] So chi phí thực tế với các phương án giả định khác. Từ khoá: counterfactual cost. |
| `/ruflo-cost-tracker:cost-diff` | kỹ năng | [Chi phí] So chênh lệch chi phí giữa hai lần đo. Từ khoá: cost diff. |
| `/ruflo-cost-tracker:cost-export` | kỹ năng | [Chi phí] Xuất số liệu chi phí sang Prometheus hoặc webhook. Từ khoá: cost export. |
| `/ruflo-cost-tracker:cost-federation` | kỹ năng | [Chi phí] Gom số liệu chi tiêu từ nhiều nơi cài đặt khác nhau. Từ khoá: federation spend. |
| `/ruflo-cost-tracker:cost-health` | kỹ năng | [Chi phí] Cổng kiểm tổng hợp: hạn mức + tốc độ tiêu + bất thường. Từ khoá: cost health gate. |
| `/ruflo-cost-tracker:cost-optimize` | kỹ năng | [Chi phí] Phân tích cách dùng token và đề xuất cách tiết kiệm. Từ khoá: cost optimization. |
| `/ruflo-cost-tracker:cost-projection` | kỹ năng | [Chi phí] Dự báo chi tiêu sắp tới dựa trên mức tiêu hiện tại. Từ khoá: cost projection. |
| `/ruflo-cost-tracker:cost-report` | kỹ năng | [Chi phí] Báo cáo token và tiền theo từng agent và mô hình. Từ khoá: cost report. |
| `/ruflo-cost-tracker:cost-session` | kỹ năng | [Chi phí] Bóc tách chi phí theo từng tin nhắn trong một phiên. Từ khoá: per-message cost. |
| `/ruflo-cost-tracker:cost-summary` | kỹ năng | [Chi phí] Kết xuất toàn bộ dữ liệu chi phí một lần: tổng tiền, theo bậc, theo mô hình. Từ khoá: cost summary. |
| `/ruflo-cost-tracker:cost-track` | kỹ năng | [Chi phí] Tự ghi số token dùng trong mỗi phiên làm việc. Từ khoá: cost tracking. |
| `/ruflo-cost-tracker:cost-trend` | kỹ năng | [Chi phí] Theo dõi xu hướng qua các lần đo chuẩn: tỷ lệ thắng, độ trễ. Từ khoá: cost trend. |

### ruflo-workflows  (16)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent gaia-benchmark-runner` | agent | [Đo chuẩn GAIA] Agent chạy và theo dõi các lượt đo chuẩn GAIA. Từ khoá: GAIA runner. |
| `agent gaia-submission-coordinator` | agent | [Đo chuẩn GAIA] Agent đóng gói, ký và điều phối việc nộp kết quả GAIA. Từ khoá: GAIA submission. |
| `agent workflow-specialist` | agent | [Quy trình] Agent chuyên tạo, chạy và quản lý quy trình nhiều bước. Từ khoá: workflow specialist. |
| `/gaia` | lệnh | [Đo chuẩn GAIA] Lệnh điều phối chung cho bộ đo chuẩn GAIA. Từ khoá: GAIA dispatcher. |
| `/gaia-cost` | lệnh | [Đo chuẩn GAIA] Báo chi phí API tích luỹ và dự trù cho cấu hình sắp chạy. Từ khoá: GAIA cost. |
| `/gaia-history` | lệnh | [Đo chuẩn GAIA] Xem lịch sử các lần đo đã lưu. Từ khoá: GAIA history. |
| `/gaia-leaderboard` | lệnh | [Đo chuẩn GAIA] Xem bảng xếp hạng GAIA hiện tại và vị trí của mình. Từ khoá: GAIA leaderboard. |
| `/gaia-run` | lệnh | [Đo chuẩn GAIA] Chạy một lượt đo chuẩn GAIA. Từ khoá: GAIA run. |
| `/gaia-submit` | lệnh | [Đo chuẩn GAIA] Đóng gói và ký kết quả GAIA để nộp bảng xếp hạng. Từ khoá: GAIA submit. |
| `/gaia-validate` | lệnh | [Đo chuẩn GAIA] Kiểm trước khi nộp: mã sạch, dữ liệu truy cập được. Từ khoá: GAIA validate. |
| `/workflow` | lệnh | [Quy trình] Quản lý quy trình — liệt kê quy trình và mẫu có sẵn. Từ khoá: workflow management. |
| `/ruflo-workflows:gaia-architecture-comparison` | kỹ năng | [Đo chuẩn GAIA] So sánh ruflo với các bộ khung GAIA khác. Không liên quan y khoa. Từ khoá: GAIA comparison. |
| `/ruflo-workflows:gaia-debugging` | kỹ năng | [Đo chuẩn GAIA] Tìm nguyên nhân một câu hỏi GAIA bị sai. Không liên quan y khoa. Từ khoá: GAIA debugging. |
| `/ruflo-workflows:gaia-submission` | kỹ năng | [Đo chuẩn GAIA] Đi trọn quy trình chạy và nộp kết quả bộ đo chuẩn GAIA. Không liên quan y khoa. Từ khoá: GAIA submission. |
| `/ruflo-workflows:workflow-create` | kỹ năng | [Quy trình] Soạn một quy trình tự động nhiều bước. Từ khoá: workflow create. |
| `/ruflo-workflows:workflow-run` | kỹ năng | [Quy trình] Chạy quy trình đã soạn: thực thi, tạm dừng, tiếp tục, huỷ. Từ khoá: workflow run. |

### ruflo-agent  (15)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent nested-coordinator` | agent | [Agent] Agent điều phối sinh agent con lồng nhau tới 5 tầng. Từ khoá: nested coordinator. |
| `agent nested-leaf` | agent | [Agent] Agent lá: làm một việc gọn rồi trả kết quả, cố ý không được sinh agent con. Từ khoá: leaf worker. |
| `agent nested-queen` | agent | [Agent] Agent điều phối hạng nặng, gắn thêm cơ chế đồng thuận và ngân sách. Từ khoá: queen orchestrator. |
| `agent nested-queen-leaf` | agent | [Agent] Agent lá bậc 2 trong cây do queen dẫn, có ghi lại vết thực thi. Từ khoá: queen leaf. |
| `agent nested-queen-researcher` | agent | [Agent] Agent tra cứu bậc 2 có tìm mẫu và lọc nội dung web qua lớp an toàn. Từ khoá: queen researcher. |
| `agent nested-queen-reviewer` | agent | [Agent] Agent rà soát bậc 2, dùng bỏ phiếu đồng thuận thay vì phán quyết đơn lẻ. Từ khoá: queen reviewer. |
| `agent nested-researcher` | agent | [Agent] Agent tra cứu đệ quy, tự tách nhánh khi vấn đề cần đào sâu. Từ khoá: recursive researcher. |
| `agent nested-reviewer` | agent | [Agent] Agent rà soát đệ quy: mỗi phát hiện có thể sinh một agent phản biện riêng. Từ khoá: recursive reviewer. |
| `agent wasm-specialist` | agent | [Agent] Agent chuyên về hộp cát WASM: tạo, quản lý, chia sẻ môi trường cách ly. Từ khoá: WASM specialist. |
| `/managed-agent` | lệnh | [Agent] Lệnh quản lý agent đám mây: liệt kê phiên, tạo, theo dõi. Từ khoá: managed agent. |
| `/wasm` | lệnh | [Agent] Lệnh quản lý agent WASM: liệt kê, xem trạng thái, duyệt kho. Từ khoá: WASM management. |
| `/ruflo-agent:managed-agent` | kỹ năng | [Agent] Chạy agent trên đám mây của Anthropic thay vì máy cá nhân. Từ khoá: managed agent, cloud. |
| `/ruflo-agent:nested-subagents` | kỹ năng | [Agent] Sinh agent con lồng nhau, sâu tối đa 5 tầng. Từ khoá: nested subagents. |
| `/ruflo-agent:wasm-agent` | kỹ năng | [Agent] Tạo và quản lý agent chạy trong hộp cát WASM cách ly. Từ khoá: WASM agent. |
| `/ruflo-agent:wasm-gallery` | kỹ năng | [Agent] Duyệt, đăng và cài agent WASM từ kho cộng đồng. Từ khoá: WASM gallery. |

### ruflo-metaharness  (15)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent metaharness-architect` | agent | [Khung agent] Agent kiến trúc sư tích hợp MetaHarness vào ruflo. Từ khoá: metaharness architect. |
| `/ruflo-metaharness` | lệnh | [Khung agent] Lệnh chung MetaHarness: chấm điểm, bộ gen, dựng mới, quét MCP, mô hình đe doạ. Từ khoá: metaharness. |
| `/ruflo-metaharness:harness-bench` | kỹ năng | [Khung agent] Quản lý bộ đo chuẩn cho khung agent. Từ khoá: harness bench. |
| `/ruflo-metaharness:harness-drift-from-history` | kỹ năng | [Khung agent] Phát hiện trôi lệch cấu hình theo lịch sử bằng một lệnh. Từ khoá: drift detection. |
| `/ruflo-metaharness:harness-evolve` | kỹ năng | [Khung agent] Cho khung agent tự tiến hoá bằng cách đột biến các chính sách của nó. Từ khoá: harness evolve. |
| `/ruflo-metaharness:harness-genome` | kỹ năng | [Khung agent] Báo cáo 7 phần về mức sẵn sàng của một kho mã. Từ khoá: harness genome. |
| `/ruflo-metaharness:harness-gepa` | kỹ năng | [Khung agent] Xem và kiểm bộ gen GEPA. Từ khoá: GEPA genome. |
| `/ruflo-metaharness:harness-learn` | kỹ năng | [Khung agent] Chạy một chu kỳ học GEPA cho khung agent. Từ khoá: harness learn, GEPA. |
| `/ruflo-metaharness:harness-mcp-scan` | kỹ năng | [Khung agent] Quét bảo mật tĩnh các công cụ MCP mà khung agent khai báo. Từ khoá: MCP scan. |
| `/ruflo-metaharness:harness-mint` | kỹ năng | [Khung agent] Dựng khung agent mới từ mẫu. Từ khoá: harness mint. |
| `/ruflo-metaharness:harness-oia-audit` | kỹ năng | [Khung agent] Kiểm toán tổng hợp giai đoạn 2 cho khung agent. Từ khoá: OIA audit. |
| `/ruflo-metaharness:harness-score` | kỹ năng | [Khung agent] Chấm điểm mức sẵn sàng của một bộ khung agent theo 5 chiều. Từ khoá: harness score. |
| `/ruflo-metaharness:harness-security-bench` | kỹ năng | [Khung agent] Chạy bộ đo chuẩn về BẢO MẬT cho khung agent. Từ khoá: security bench. |
| `/ruflo-metaharness:harness-similarity` | kỹ năng | [Khung agent] Đo mức giống nhau giữa hai khung agent. Từ khoá: harness similarity. |
| `/ruflo-metaharness:harness-threat-model` | kỹ năng | [Khung agent] Dựng mô hình mối đe doạ đạt mức rà soát doanh nghiệp. Từ khoá: threat model. |

### ruflo-neural-trader  (14)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent backtest-engineer` | agent | [Giao dịch] Agent kiểm định chiến lược trên dữ liệu quá khứ. Từ khoá: backtest engineer. |
| `agent market-analyst` | agent | [Giao dịch] Agent phân tích thị trường và nhận diện trạng thái. Từ khoá: market analyst. |
| `agent risk-analyst` | agent | [Giao dịch] Agent đánh giá rủi ro danh mục — cổng chặn trước khi ra lệnh. Từ khoá: risk analyst. |
| `agent trading-strategist` | agent | [Giao dịch] Agent thiết kế và tối ưu chiến lược giao dịch. Từ khoá: trading strategist. |
| `/trader` | lệnh | [Giao dịch] Lệnh chung: chiến lược, kiểm định, tín hiệu, rủi ro. Từ khoá: neural trader. |
| `/ruflo-neural-trader:trader-backtest` | kỹ năng | [Giao dịch — không liên quan y khoa] Chạy kiểm định chiến lược trên dữ liệu quá khứ. Từ khoá: backtest. |
| `/ruflo-neural-trader:trader-cloud-backtest` | kỹ năng | [Giao dịch] Chạy kiểm định nặng trên đám mây. Từ khoá: cloud backtest. |
| `/ruflo-neural-trader:trader-explain` | kỹ năng | [Giao dịch] Giải thích vì sao mô hình ra tín hiệu đó, ở mức đủ cho cơ quan quản lý. Từ khoá: feature attribution. |
| `/ruflo-neural-trader:trader-portfolio` | kỹ năng | [Giao dịch] Tối ưu phân bổ danh mục theo mô hình trung bình–phương sai. Từ khoá: portfolio optimization. |
| `/ruflo-neural-trader:trader-portfolio-cg` | kỹ năng | [Giao dịch] Tối ưu danh mục bằng thuật toán gradient liên hợp, nhanh hơn nhiều lần. Từ khoá: conjugate gradient. |
| `/ruflo-neural-trader:trader-regime` | kỹ năng | [Giao dịch] Nhận diện trạng thái thị trường: tăng, giảm, đi ngang. Từ khoá: market regime. |
| `/ruflo-neural-trader:trader-risk` | kỹ năng | [Giao dịch] Đánh giá rủi ro danh mục: VaR, CVaR, Sharpe, cỡ vị thế. Từ khoá: portfolio risk. |
| `/ruflo-neural-trader:trader-signal` | kỹ năng | [Giao dịch] Sinh tín hiệu mua bán bằng phát hiện bất thường. Từ khoá: trading signal. |
| `/ruflo-neural-trader:trader-train` | kỹ năng | [Giao dịch] Huấn luyện mô hình mạng nơ-ron trên dữ liệu thị trường. Từ khoá: train model. |

### ruflo-browser  (12)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent browser-agent` | agent | [Trình duyệt] Agent điều khiển trình duyệt qua Playwright, có lớp lọc an toàn nội dung. Từ khoá: browser agent. |
| `/ruflo-browser` | lệnh | [Trình duyệt] Lệnh quản lý vòng đời phiên duyệt web: liệt kê, xem, phát lại, xuất. Từ khoá: browser session. |
| `/ruflo-browser:browser-auth-flow` | kỹ năng | [Trình duyệt] Dò lỗ hổng trong luồng đăng nhập của một trang: rò chuyển hướng, thiếu CSRF. Từ khoá: auth flow probe. |
| `/ruflo-browser:browser-extract` | kỹ năng | [Trình duyệt] Bóc dữ liệu có cấu trúc từ trang web. Từ khoá: extract data. |
| `/ruflo-browser:browser-form-fill` | kỹ năng | [Trình duyệt] Điền biểu mẫu web theo ánh xạ tên trường → giá trị. Từ khoá: form fill. |
| `/ruflo-browser:browser-intent` | kỹ năng | [Trình duyệt] Ra lệnh cho trình duyệt bằng câu tiếng tự nhiên. Từ khoá: browser intent. |
| `/ruflo-browser:browser-login` | kỹ năng | [Trình duyệt] Đăng nhập một lần rồi lưu phiên đã được làm sạch để dùng lại. Từ khoá: browser login. |
| `/ruflo-browser:browser-record` | kỹ năng | [Trình duyệt] Ghi lại một phiên duyệt web để phát lại về sau. Từ khoá: record session. |
| `/ruflo-browser:browser-replay` | kỹ năng | [Trình duyệt] Phát lại phiên đã ghi trên cùng trang hoặc trang đã đổi. Từ khoá: replay session. |
| `/ruflo-browser:browser-scrape` | kỹ năng | [Trình duyệt] ĐÃ NGỪNG DÙNG từ v0.2.0 — hãy dùng browser-extract. Từ khoá: deprecated. |
| `/ruflo-browser:browser-screenshot-diff` | kỹ năng | [Trình duyệt] So ảnh chụp và cấu trúc trang giữa hai phiên ghi. Từ khoá: screenshot diff. |
| `/ruflo-browser:browser-test` | kỹ năng | [Trình duyệt] Công thức kiểm thử giao diện: ghi rồi phát lại để đối chiếu. Từ khoá: UI test. |

### ruflo-core  (11)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent coder` | agent | [Hạ tầng ruflo] Agent viết mã theo đúng khuôn mẫu sẵn có của dự án. Từ khoá: coder. |
| `agent researcher` | agent | [Hạ tầng ruflo] Agent tra cứu trong mã nguồn và bộ nhớ để tìm mẫu và tiền lệ. Từ khoá: researcher. |
| `agent reviewer` | agent | [Hạ tầng ruflo] Agent rà soát mã về chất lượng, bảo mật và chuẩn mực. Từ khoá: reviewer. |
| `agent witness-curator` | agent | [Hạ tầng ruflo] Agent giữ bản kê bản vá đã ký, truy commit gây lỗi tái phát. Từ khoá: witness curator. |
| `/ruflo-status` | lệnh | [Hạ tầng ruflo] Lệnh xem nhanh tình trạng hệ thống và agent. Từ khoá: ruflo status. |
| `/witness` | lệnh | [Hạ tầng ruflo] Lệnh quản lý và kiểm bản kê bản vá đã ký. Từ khoá: witness. |
| `/ruflo-core:discover-plugins` | kỹ năng | [Hạ tầng ruflo] Gợi ý plugin ruflo phù hợp với cách làm việc hiện tại. Từ khoá: discover plugins. |
| `/ruflo-core:init-project` | kỹ năng | [Hạ tầng ruflo] Khởi tạo dự án ruflo mới với công cụ MCP, hook và cấu hình agent. Từ khoá: init project. |
| `/ruflo-core:ruflo-doctor` | kỹ năng | [Hạ tầng ruflo] Kiểm tra sức khoẻ bản cài và tự sửa lỗi thường gặp. Từ khoá: ruflo doctor. |
| `/ruflo-core:ruflo-status` | kỹ năng | [Hạ tầng ruflo] Xem tình trạng hệ thống, máy chủ MCP và agent đang chạy. Từ khoá: ruflo status. |
| `/ruflo-core:witness` | kỹ năng | [Hạ tầng ruflo] Ký và kiểm dấu vết các bản vá để phát hiện lỗi tái phát. Từ khoá: witness manifest. |

### ruflo-goals  (10)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent deep-researcher` | agent | [Mục tiêu] Agent tra cứu đa nguồn, đối chiếu chéo và xử lý mâu thuẫn. Từ khoá: deep researcher. |
| `agent dossier-investigator` | agent | [Mục tiêu] Agent điều tra song song nhiều nguồn để dựng hồ sơ có ghi nguồn từng ý. Từ khoá: dossier investigator. |
| `agent goal-planner` | agent | [Mục tiêu] Agent lập kế hoạch tối ưu bằng tìm kiếm A*, tự lập lại kế hoạch khi cần. Từ khoá: goal planner. |
| `agent horizon-tracker` | agent | [Mục tiêu] Agent theo dõi mục tiêu dài hạn, phát hiện chệch hướng. Từ khoá: horizon tracker. |
| `/goals` | lệnh | [Mục tiêu] Xem mục tiêu đang theo đuổi, tiến độ và kết quả tra cứu. Từ khoá: goals. |
| `/ruflo-goals:deep-research` | kỹ năng | [Mục tiêu] Tra cứu sâu nhiều giai đoạn, kết hợp tìm web và bộ nhớ. Từ khoá: deep research. |
| `/ruflo-goals:dossier-collect` | kỹ năng | [Mục tiêu] Dựng hồ sơ dạng mạng lưới về một đối tượng bằng cách toả nhánh nhiều nguồn. Từ khoá: dossier. |
| `/ruflo-goals:goal-plan` | kỹ năng | [Mục tiêu] Lập và chạy kế hoạch hành động theo mục tiêu, có điều kiện tiên quyết. Từ khoá: GOAP. |
| `/ruflo-goals:horizon-track` | kỹ năng | [Mục tiêu] Theo dõi mục tiêu dài hạn xuyên nhiều phiên, có mốc kiểm. Từ khoá: horizon tracking. |
| `/ruflo-goals:research-synthesize` | kỹ năng | [Mục tiêu] Tổng hợp kết quả tra cứu thành báo cáo có cấu trúc kèm mức độ bằng chứng. Từ khoá: research synthesis. |

### ruflo-iot-cognitum  (10)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent device-coordinator` | agent | [IoT] Agent điều phối đội thiết bị theo 5 bậc tin cậy. Từ khoá: device coordinator. |
| `agent fleet-manager` | agent | [IoT] Agent quản lý đội thiết bị và chính sách chung. Từ khoá: fleet manager. |
| `agent telemetry-analyzer` | agent | [IoT] Agent phân tích dữ liệu đo để tìm bất thường bằng điểm Z. Từ khoá: telemetry analyzer. |
| `agent witness-auditor` | agent | [IoT] Agent kiểm chuỗi chứng thực Ed25519 và phát hiện lỗ hổng nguồn gốc. Từ khoá: witness auditor. |
| `/iot` | lệnh | [IoT] Lệnh chung quản lý thiết bị, đội thiết bị, phần sụn và dữ liệu đo. Từ khoá: IoT management. |
| `/ruflo-iot-cognitum:iot-anomalies` | kỹ năng | [IoT] Phát hiện và phân loại bất thường trong dữ liệu thiết bị. Từ khoá: telemetry anomaly. |
| `/ruflo-iot-cognitum:iot-firmware` | kỹ năng | [IoT] Triển khai phần sụn theo lô nhỏ, tự dừng khi phát hiện bất thường. Từ khoá: firmware rollout. |
| `/ruflo-iot-cognitum:iot-fleet` | kỹ năng | [IoT] Tạo và quản lý đội thiết bị cùng chính sách phần sụn. Từ khoá: device fleet. |
| `/ruflo-iot-cognitum:iot-register` | kỹ năng | [IoT — không liên quan y khoa] Đăng ký một thiết bị Cognitum Seed. Từ khoá: IoT register. |
| `/ruflo-iot-cognitum:iot-witness-verify` | kỹ năng | [IoT] Kiểm tính toàn vẹn chuỗi chứng thực của thiết bị. Từ khoá: witness chain. |

### ruflo-adr  (7)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent adr-architect` | agent | [Kiến trúc] Agent quản lý bản ghi quyết định kiến trúc: tạo, lập mục lục, thay thế, liên kết với mã. Từ khoá: ADR architect. |
| `/adr` | lệnh | [Kiến trúc] Lệnh quản lý vòng đời bản ghi quyết định kiến trúc. Từ khoá: ADR lifecycle. |
| `/ruflo-adr:adr-create` | kỹ năng | [Kiến trúc] Tạo một BẢN GHI QUYẾT ĐỊNH KIẾN TRÚC mới, đánh số tuần tự. Từ khoá: ADR create. |
| `/ruflo-adr:adr-index` | kỹ năng | [Kiến trúc] Dựng lại mục lục và sơ đồ phụ thuộc giữa các quyết định kiến trúc. Từ khoá: ADR index. |
| `/ruflo-adr:adr-reindex` | kỹ năng | [Kiến trúc] Cập nhật mục lục sau khi xoá một bản ghi quyết định. Từ khoá: ADR reindex. |
| `/ruflo-adr:adr-review` | kỹ năng | [Kiến trúc] Đối chiếu thay đổi mã với các quyết định kiến trúc đã duyệt. Từ khoá: ADR review. |
| `/ruflo-adr:adr-verify` | kỹ năng | [Kiến trúc] Soi tham chiếu treo và mâu thuẫn trong hệ thống quyết định kiến trúc. Từ khoá: ADR verify. |

### ruflo-ruvector  (6)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent vector-engineer` | agent | [Vector] Agent chuyên về vector: đánh chỉ mục HNSW, gom cụm, biểu diễn phân cấp. Từ khoá: vector engineer. |
| `/vector` | lệnh | [Vector] Lệnh chung: sinh vector, tìm kiếm ngữ nghĩa, quản lý kho vector. Từ khoá: ruvector. |
| `/ruflo-ruvector:vector-cluster` | kỹ năng | [Vector] Gom nhóm mã nguồn theo cộng đồng trong đồ thị. Từ khoá: code clustering. |
| `/ruflo-ruvector:vector-embed` | kỹ năng | [Vector] Sinh vector biểu diễn cho văn bản. Từ khoá: embedding. |
| `/ruflo-ruvector:vector-hyperbolic` | kỹ năng | [Vector] Biểu diễn dữ liệu phân cấp trong không gian hyperbolic. Từ khoá: hyperbolic embedding. |
| `/ruflo-ruvector:vector-setup` | kỹ năng | [Vector] Cài đặt lần đầu cho bộ công cụ vector. Từ khoá: vector setup. |

### ruflo-swarm  (6)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent architect` | agent | [Bầy agent] Agent kiến trúc sư: thiết kế cách làm, hợp đồng API, ranh giới mô-đun. Từ khoá: architect. |
| `agent coordinator` | agent | [Bầy agent] Agent điều phối: quản vòng đời agent, giao việc, chống trôi lệch. Từ khoá: coordinator. |
| `/swarm` | lệnh | [Bầy agent] Lệnh khởi tạo, theo dõi và quản lý bầy nhiều agent. Từ khoá: swarm. |
| `/watch` | lệnh | [Bầy agent] Xem trực tiếp hoạt động của các agent. Từ khoá: watch. |
| `/ruflo-swarm:monitor-stream` | kỹ năng | [Bầy agent] Xem trực tiếp sự kiện của bầy agent theo thời gian thực. Từ khoá: monitor stream. |
| `/ruflo-swarm:swarm-init` | kỹ năng | [Bầy agent] Khởi tạo một bầy nhiều agent có cấu hình chống trôi lệch. Từ khoá: swarm init. |

### ruflo-intelligence  (6)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent intelligence-specialist` | agent | [Học máy] Agent tự học theo chu trình 4 bước: truy hồi → phán đoán → chưng cất → hợp nhất. Từ khoá: intelligence specialist. |
| `/intelligence` | lệnh | [Học máy] Bảng điều khiển: thống kê, chỉ số, cách chọn mô hình. Từ khoá: intelligence dashboard. |
| `/neural` | lệnh | [Học máy] Huấn luyện, dự đoán, nén mẫu và tối ưu đường ống. Từ khoá: neural. |
| `/ruflo-intelligence:intelligence-route` | kỹ năng | [Học máy] Chọn mô hình phù hợp cho từng việc theo 3 bậc và mẫu đã học. Từ khoá: model routing. |
| `/ruflo-intelligence:intelligence-transfer` | kỹ năng | [Học máy] Chia sẻ mẫu đã học giữa các dự án qua IPFS. Từ khoá: pattern transfer. |
| `/ruflo-intelligence:neural-train` | kỹ năng | [Học máy] Huấn luyện mẫu từ những việc đã làm thành công. Từ khoá: neural training. |

### ruflo-agentdb  (5)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent agentdb-specialist` | agent | [Cơ sở dữ liệu agent] Agent chuyên về AgentDB và tìm kiếm ngữ nghĩa. Từ khoá: AgentDB specialist. |
| `/agentdb` | lệnh | [Cơ sở dữ liệu agent] Xem tình trạng AgentDB và quản lý phiên. Từ khoá: AgentDB status. |
| `/embeddings` | lệnh | [Cơ sở dữ liệu agent] Trạng thái và thao tác của bộ sinh vector. Từ khoá: embeddings. |
| `/ruflo-agentdb:agentdb-query` | kỹ năng | [Cơ sở dữ liệu agent] Truy vấn AgentDB: định tuyến ngữ nghĩa, truy hồi phân cấp. Từ khoá: AgentDB query. |
| `/ruflo-agentdb:vector-search` | kỹ năng | [Cơ sở dữ liệu agent] Tìm kiếm bằng vector trên quy mô lớn. Từ khoá: vector search, HNSW. |

### ruflo-autopilot  (5)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent autopilot-coordinator` | agent | [Tự động] Agent điều phối chế độ tự động hoàn thành việc. Từ khoá: autopilot coordinator. |
| `/autopilot` | lệnh | [Tự động] Bật, cấu hình hoặc tắt chế độ tự động hoàn thành việc. Từ khoá: autopilot. |
| `/autopilot-status` | lệnh | [Tự động] Xem nhanh tiến độ và số việc đã hoàn thành. Từ khoá: autopilot status. |
| `/ruflo-autopilot:autopilot-loop` | kỹ năng | [Tự động] Chạy một vòng lặp tự động: xem tiến độ, làm việc kế tiếp. Từ khoá: autopilot loop. |
| `/ruflo-autopilot:autopilot-predict` | kỹ năng | [Tự động] Dự đoán hành động kế tiếp tối ưu từ mẫu đã học. Từ khoá: autopilot predict. |

### ruflo-ddd  (5)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent domain-modeler` | agent | [Thiết kế miền] Agent mô hình hoá miền nghiệp vụ và thiết kế thực thể gốc. Từ khoá: domain modeler. |
| `/ddd` | lệnh | [Thiết kế miền] Lệnh dựng khung và kiểm ranh giới theo lối thiết kế hướng miền. Từ khoá: DDD. |
| `/ruflo-ddd:ddd-aggregate` | kỹ năng | [Thiết kế miền] Dựng khung thực thể gốc kèm kho lưu trữ và đối tượng giá trị. Từ khoá: aggregate root. |
| `/ruflo-ddd:ddd-context` | kỹ năng | [Thiết kế miền] Tạo và quản lý một miền nghiệp vụ có ranh giới rõ. Từ khoá: bounded context. |
| `/ruflo-ddd:ddd-validate` | kỹ năng | [Thiết kế miền] Kiểm ranh giới miền, phát hiện phụ thuộc vượt biên. Từ khoá: domain boundary. |

### ruflo-federation  (5)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent federation-coordinator` | agent | [Liên kết máy] Agent điều phối liên kết theo nguyên tắc không tin tưởng mặc định. Từ khoá: federation coordinator. |
| `/federation` | lệnh | [Liên kết máy] Lệnh quản lý liên kết agent giữa nhiều nơi cài đặt. Từ khoá: federation. |
| `/ruflo-federation:federation-audit` | kỹ năng | [Liên kết máy] Tra nhật ký kiểm toán liên kết theo bộ lọc tuân thủ. Từ khoá: federation audit. |
| `/ruflo-federation:federation-init` | kỹ năng | [Liên kết máy] Khởi tạo liên kết giữa nhiều nơi cài đặt, sinh cặp khoá. Từ khoá: federation init. |
| `/ruflo-federation:federation-status` | kỹ năng | [Liên kết máy] Xem tình trạng liên kết: nút ngang hàng, phiên, mức tin cậy. Từ khoá: federation status. |

### ruflo-testgen  (5)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent tester` | agent | [Kiểm thử] Agent viết bộ kiểm thử đầy đủ theo trường phái London. Từ khoá: tester. |
| `/testgen` | lệnh | [Kiểm thử] Sinh test cho một file hoặc mô-đun dựa trên phân tích độ phủ. Từ khoá: test generation. |
| `/ruflo-testgen:tdd-repair` | kỹ năng | [Kiểm thử] Sửa lỗi từ một test đang đỏ, chạy trong tiến trình tách biệt. Từ khoá: TDD repair. |
| `/ruflo-testgen:tdd-workflow` | kỹ năng | [Kiểm thử] Quy trình phát triển hướng kiểm thử theo trường phái London. Từ khoá: TDD. |
| `/ruflo-testgen:test-gaps` | kỹ năng | [Kiểm thử] Tìm chỗ THIẾU kiểm thử và đề xuất test cần thêm. Từ khoá: test gaps, coverage. |

### ruflo-rag-memory  (5)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent memory-specialist` | agent | [Bộ nhớ] Agent chuyên về bộ nhớ truy hồi: tìm lai ghép, truy hồi nhiều bước. Từ khoá: memory specialist. |
| `/recall` | lệnh | [Bộ nhớ] Nhớ lại nhanh — tìm trên mọi vùng bộ nhớ. Từ khoá: recall. |
| `/ruflo-memory` | lệnh | [Bộ nhớ] Thao tác bộ nhớ: lưu, tìm, lấy ra, liệt kê. Từ khoá: memory CRUD. |
| `/ruflo-rag-memory:memory-bridge` | kỹ năng | [Bộ nhớ] Nối bộ nhớ tự động của Claude Code vào AgentDB, có khử trùng lặp. Từ khoá: memory bridge. |
| `/ruflo-rag-memory:memory-search` | kỹ năng | [Bộ nhớ] Tìm kiếm ngữ nghĩa nâng cao trong bộ nhớ, kết hợp nhiều cách truy hồi. Từ khoá: memory search. |

### ruflo-sparc  (5)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent sparc-orchestrator` | agent | [Quy trình SPARC] Agent điều phối 5 giai đoạn SPARC, có cổng chất lượng giữa các giai đoạn. Từ khoá: SPARC orchestrator. |
| `/ruflo-sparc` | lệnh | [Quy trình SPARC] Lệnh khởi tạo, theo dõi và tiến bước qua 5 giai đoạn SPARC. Từ khoá: SPARC. |
| `/ruflo-sparc:sparc-implement` | kỹ năng | [Quy trình SPARC] Giai đoạn Mã giả và Kiến trúc. Từ khoá: SPARC implement. |
| `/ruflo-sparc:sparc-refine` | kỹ năng | [Quy trình SPARC] Giai đoạn Tinh chỉnh và Hoàn tất: rà mã, tăng kiểm thử. Từ khoá: SPARC refine. |
| `/ruflo-sparc:sparc-spec` | kỹ năng | [Quy trình SPARC] Giai đoạn Đặc tả: thu thập yêu cầu, định nghĩa tiêu chí nghiệm thu. Từ khoá: SPARC spec. |

### ruflo-loop-workers  (5)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent loop-worker-coordinator` | agent | [Chạy nền] Agent điều phối lịch chạy, theo dõi sức khoẻ và phân việc cho tiến trình nền. Từ khoá: loop coordinator. |
| `/ruflo-loop` | lệnh | [Chạy nền] Khởi động một tiến trình nền (kiểm toán, tối ưu, tìm lỗ hổng test). Từ khoá: ruflo loop. |
| `/ruflo-schedule` | lệnh | [Chạy nền] Đặt lịch cho tiến trình nền. Từ khoá: ruflo schedule. |
| `/ruflo-loop-workers:cron-schedule` | kỹ năng | [Chạy nền] Đặt lịch chạy tiến trình nền lâu dài. Từ khoá: cron schedule. |
| `/ruflo-loop-workers:loop-worker` | kỹ năng | [Chạy nền] Chạy tiến trình nền theo cơ chế lặp của Claude Code. Từ khoá: loop worker. |

### ruflo-aidefence  (4)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent safety-specialist` | agent | [An toàn AI] Agent chuyên về an toàn: phát hiện đe doạ, quét PII, huấn luyện phòng vệ. Từ khoá: safety specialist. |
| `/aidefence` | lệnh | [An toàn AI] Bảng theo dõi tình trạng phòng vệ và thống kê mối đe doạ. Từ khoá: AI defence. |
| `/ruflo-aidefence:pii-detect` | kỹ năng | [An toàn AI] Phát hiện thông tin định danh cá nhân trong văn bản và mã. Với bệnh án nên dùng nhóm OpenMed vì có chuẩn HIPAA. Từ khoá: PII detection. |
| `/ruflo-aidefence:safety-scan` | kỹ năng | [An toàn AI] Quét đầu vào để phát hiện tấn công tiêm lệnh và nội dung không an toàn. Từ khoá: prompt injection. |

### ruflo-daa  (4)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent daa-specialist` | agent | [Agent thích nghi] Agent chuyên về kiến trúc agent thích nghi và chia sẻ tri thức. Từ khoá: DAA specialist. |
| `/daa` | lệnh | [Agent thích nghi] Xem chỉ số học tập và agent đang hoạt động. Từ khoá: DAA status. |
| `/ruflo-daa:cognitive-pattern` | kỹ năng | [Agent thích nghi] Định nghĩa và quản lý mẫu tư duy cho agent. Từ khoá: cognitive pattern. |
| `/ruflo-daa:daa-agent` | kỹ năng | [Agent thích nghi] Tạo agent tự học và tiến hoá theo thời gian. Từ khoá: adaptive agent. |

### ruflo-docs  (4)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent docs-writer` | agent | [Tài liệu] Agent chuyên viết và bảo trì tài liệu dự án. Từ khoá: docs writer. |
| `/ruflo-docs` | lệnh | [Tài liệu] Sinh hoặc cập nhật tài liệu cho một file, mô-đun hoặc cả dự án. Từ khoá: docs. |
| `/ruflo-docs:api-docs` | kỹ năng | [Tài liệu] Sinh tài liệu API từ mã nguồn, hỗ trợ JSDoc và OpenAPI. Từ khoá: API docs. |
| `/ruflo-docs:doc-gen` | kỹ năng | [Tài liệu] Sinh và bảo trì tài liệu, có phát hiện tài liệu lệch với mã. Từ khoá: doc generation. |

### ruflo-security-audit  (4)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent security-auditor` | agent | [Bảo mật] Agent kiểm toán bảo mật và khắc phục lỗ hổng. Từ khoá: security auditor. |
| `/audit` | lệnh | [Bảo mật] Chạy kiểm toán bảo mật cho dự án. Từ khoá: security audit. |
| `/ruflo-security-audit:dependency-check` | kỹ năng | [Bảo mật] Quét thư viện phụ thuộc để tìm lỗ hổng đã công bố (CVE). Từ khoá: dependency check, CVE. |
| `/ruflo-security-audit:security-scan` | kỹ năng | [Bảo mật] Quét bảo mật toàn bộ mã nguồn. Từ khoá: security scan. |

### ruflo-rvf  (4)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent session-specialist` | agent | [Bộ nhớ RVF] Agent chuyên giữ trạng thái phiên và chuyển tiếp bộ nhớ. Từ khoá: session specialist. |
| `/rvf` | lệnh | [Bộ nhớ RVF] Lệnh quản lý bộ nhớ RVF: liệt kê, thống kê, quản phiên. Từ khoá: RVF management. |
| `/ruflo-rvf:rvf-manage` | kỹ năng | [Bộ nhớ RVF] Quản lý file bộ nhớ agent dạng chuyển được giữa các máy. Từ khoá: RVF. |
| `/ruflo-rvf:session-persist` | kỹ năng | [Bộ nhớ RVF] Lưu và khôi phục phiên agent qua nhiều cuộc trò chuyện. Từ khoá: session persist. |

### ruflo-ruvllm  (4)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent llm-specialist` | agent | [Mô hình cục bộ] Agent chuyên cấu hình mô hình chạy cục bộ và tinh chỉnh nhẹ. Từ khoá: LLM specialist. |
| `/ruvllm` | lệnh | [Mô hình cục bộ] Xem cấu hình mô hình và bộ điều hợp đang dùng. Từ khoá: RuVLLM status. |
| `/ruflo-ruvllm:chat-format` | kỹ năng | [Mô hình cục bộ] Định dạng câu lệnh cho từng nhà cung cấp mô hình khác nhau. Từ khoá: chat template. |
| `/ruflo-ruvllm:llm-config` | kỹ năng | [Mô hình cục bộ] Cấu hình chạy mô hình ngôn ngữ ngay trên máy. Từ khoá: local inference. |

### ruflo-observability  (4)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent observability-engineer` | agent | [Giám sát] Agent dựng nhật ký có cấu trúc, lần vết phân tán và thu thập chỉ số. Từ khoá: observability engineer. |
| `/observe` | lệnh | [Giám sát] Lệnh giám sát: lần vết, xem chỉ số, lọc nhật ký. Từ khoá: observability. |
| `/ruflo-observability:observe-metrics` | kỹ năng | [Giám sát] Gom và hiển thị chỉ số hệ thống, có phát hiện bất thường. Từ khoá: metrics. |
| `/ruflo-observability:observe-trace` | kỹ năng | [Giám sát] Lần theo quá trình chạy của agent thành cây vết. Từ khoá: tracing. |

### ruflo-plugin-creator  (4)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent plugin-developer` | agent | [Plugin] Agent chuyên dựng, kiểm và phát hành plugin Claude Code. Từ khoá: plugin developer. |
| `/create-plugin` | lệnh | [Plugin] Lệnh dựng khung plugin mới theo lối hỏi đáp. Từ khoá: create plugin. |
| `/ruflo-plugin-creator:create-plugin` | kỹ năng | [Plugin] Dựng khung một plugin Claude Code mới đúng cấu trúc. Từ khoá: create plugin. |
| `/ruflo-plugin-creator:validate-plugin` | kỹ năng | [Plugin] Kiểm cấu trúc, frontmatter và tham chiếu công cụ MCP của plugin. Từ khoá: validate plugin. |

### ruflo-migrations  (4)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent migration-engineer` | agent | [Cơ sở dữ liệu] Agent sinh các bước chuyển đổi tuần tự có kiểm tra an toàn khi quay lui. Từ khoá: migration engineer. |
| `/migrate` | lệnh | [Cơ sở dữ liệu] Lệnh chuyển đổi cấu trúc dữ liệu: tạo, áp dụng, quay lui, kiểm. Từ khoá: migrate. |
| `/ruflo-migrations:migrate-create` | kỹ năng | [Cơ sở dữ liệu] Tạo bước chuyển đổi cấu trúc dữ liệu mới, có cả chiều tiến và lùi. Từ khoá: migration. |
| `/ruflo-migrations:migrate-validate` | kỹ năng | [Cơ sở dữ liệu] Kiểm các bước chuyển đổi đang chờ: ràng buộc khoá ngoại, khả năng quay lui. Từ khoá: migration validate. |

### ruflo-market-data  (4)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent data-engineer` | agent | [Dữ liệu thị trường] Agent nạp, chuẩn hoá dữ liệu giá và so khớp mẫu hình. Từ khoá: data engineer. |
| `/market` | lệnh | [Dữ liệu thị trường] Lệnh nạp dữ liệu, nhận mẫu và tra lịch sử. Từ khoá: market data. |
| `/ruflo-market-data:market-ingest` | kỹ năng | [Dữ liệu thị trường — không liên quan y khoa] Nạp và chuẩn hoá dữ liệu giá. Từ khoá: market ingest. |
| `/ruflo-market-data:market-pattern` | kỹ năng | [Dữ liệu thị trường] Nhận diện mẫu hình nến từ dữ liệu đã nạp. Từ khoá: candlestick pattern. |

### ruflo-knowledge-graph  (4)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent graph-navigator` | agent | [Bản đồ tri thức] Agent dựng và duyệt bản đồ tri thức từ mã và tài liệu. Từ khoá: graph navigator. |
| `/kg` | lệnh | [Bản đồ tri thức] Lệnh rút thực thể, duyệt quan hệ và tìm kiếm trên bản đồ. Từ khoá: knowledge graph. |
| `/ruflo-knowledge-graph:kg-extract` | kỹ năng | [Bản đồ tri thức] Rút thực thể và quan hệ từ mã nguồn để dựng bản đồ tri thức. Từ khoá: entity extraction. |
| `/ruflo-knowledge-graph:kg-traverse` | kỹ năng | [Bản đồ tri thức] Đi theo quan hệ trong bản đồ tri thức từ một điểm xuất phát. Từ khoá: graph traversal. |

### ruflo-jujutsu  (4)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent git-specialist` | agent | [Git] Agent chuyên về git: phân tích thay đổi, đánh giá rủi ro, quản pull request. Từ khoá: git specialist. |
| `/jujutsu` | lệnh | [Git] Phân tích thay đổi mã kèm chấm rủi ro và phân loại. Từ khoá: jujutsu. |
| `/ruflo-jujutsu:diff-analyze` | kỹ năng | [Git] Phân tích thay đổi mã: chấm mức rủi ro, gợi ý người rà soát. Từ khoá: diff analysis. |
| `/ruflo-jujutsu:git-workflow` | kỹ năng | [Git] Quy trình git nâng cao: quản nhánh, xử lý xung đột. Từ khoá: git workflow. |

### ruflo-arena  (1)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `/arena` | lệnh | [Thi đấu] Chạy giải đấu so tài giữa các chiến lược chương trình. Không liên quan y khoa. Từ khoá: arena, tournament. |
