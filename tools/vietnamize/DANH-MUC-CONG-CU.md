# Danh mục công cụ gọi được trong Claude Code

> Sinh tự động bằng `tools/vietnamize/build_danh_muc.py`. KHÔNG sửa tay — chạy lại script sau mỗi lần cập nhật plugin.


**Tổng cộng 472 mục.** Cách gọi: gõ `/` rồi tên lệnh, hoặc nói thẳng nhu cầu để hệ thống tự chọn.


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

## Skill DỰNG SẴN của Claude Code  (14 mục)

> Nhóm này **không có file trên máy** — chúng nhúng trong chính phần mềm nên không Việt hoá tại chỗ được (sửa sẽ phá chữ ký và mất khi cập nhật). Mô tả dưới đây là bản giải thích để tra cứu.

| Gọi bằng | Là gì | Dùng khi nào | Lưu ý |
|---|---|---|---|
| `/artifact-capabilities` — Năng lực động của trang Artifact | Cho biết một trang Artifact được phép làm gì ngoài HTML tĩnh: đọc dữ liệu sống, giữ trạng thái chung giữa nhiều người xem, tự cập nhật lại chính nó. | Khi bác sĩ muốn một trang không chỉ hiển thị cố định mà còn tự làm mới hoặc lưu lựa chọn của người xem. | Phải nạp skill này TRƯỚC khi viết trang; không phải tài khoản nào cũng bật đủ năng lực. |
| `/artifact-design` — Thiết kế trang kết quả (Artifact) | Nguyên tắc trình bày khi tạo một trang HTML độc lập để bác sĩ xem hoặc chia sẻ — bố cục, cỡ chữ, khoảng trắng, mức đầu tư thiết kế tương xứng với yêu cầu. | Tự chạy khi tạo trang kết quả dạng Artifact. | Artifact mặc định là RIÊNG TƯ; chỉ thành công khai khi bác sĩ tự bấm chia sẻ. |
| `/claude-api` — Tra cứu Claude API | Tài liệu tra cứu về Claude API và bộ thư viện Anthropic: mã model, giá, giới hạn, cách gọi công cụ, cách lưu đệm ngữ cảnh. | Bắt buộc đọc trước khi viết hoặc sửa mã có gọi Claude, và trước khi trả lời câu hỏi về giá hay chọn model — để không nói theo trí nhớ. | Bỏ qua nếu đang làm với nhà cung cấp khác (OpenAI, Gemini...). |
| `/dataviz` — Vẽ biểu đồ đúng chuẩn | Hướng dẫn cách vẽ MỌI biểu đồ, đồ thị, bảng số liệu hay bảng điều khiển sao cho đọc được và nhất quán — chọn dạng biểu đồ theo loại dữ liệu, bảng màu an toàn cho người mù màu, quy tắc trục và chú giải. | Tự chạy trước khi vẽ bất kỳ biểu đồ nào, dù bằng Python, HTML hay hình SVG. Bác sĩ không cần gọi tay. | Dashboard lâm sàng EBM của bác sĩ vẫn theo mẫu Evidence Workbench riêng, không dùng bảng màu của skill này. |
| `/fewer-permission-prompts` — Bớt bị hỏi xin phép | Đọc lại lịch sử phiên làm việc, tìm những lệnh chỉ ĐỌC mà bác sĩ vẫn phải bấm đồng ý mỗi lần, rồi đề xuất danh sách cho phép sẵn. | Khi thấy phải bấm đồng ý quá nhiều cho những việc vô hại như xem file, xem trạng thái git. | — |
| `/init` — Khởi tạo hồ sơ dự án | Quét một kho mã rồi sinh file CLAUDE.md mô tả dự án đó, để những phiên sau hiểu ngay bối cảnh. | Khi bắt đầu làm việc với một kho mã mới chưa có CLAUDE.md. | Dự án EBM của bác sĩ đã có CLAUDE.md rất chi tiết — chạy lại sẽ ghi đè, đừng dùng ở đây. |
| `/keybindings-help` — Tuỳ chỉnh phím tắt | Đổi phím tắt trong Claude Code, kể cả tổ hợp nhiều phím liên tiếp. | Khi phím mặc định vướng với thói quen gõ của bác sĩ. | — |
| `/loop` — Chạy lặp theo chu kỳ | Lặp lại một yêu cầu theo khoảng thời gian đều đặn, hoặc để hệ thống tự chọn nhịp. | Khi cần theo dõi liên tục một việc đang chạy, ví dụ chờ một tiến trình dài kết thúc. | Chỉ dùng cho việc LẶP LẠI. Việc làm một lần thì không cần. |
| `/review` — Rà soát mã tìm lỗi | Đọc phần mã đã thay đổi để tìm lỗi sai thật sự: sai logic, thiếu trường hợp biên, rò rỉ tài nguyên. | Trước khi chốt một thay đổi quan trọng. | Khác `simplify`: cái kia lo cách viết cho gọn, cái này đi tìm lỗi. |
| `/run` — Chạy thử ứng dụng của dự án | Khởi động ứng dụng của dự án để tận mắt thấy thay đổi có chạy đúng không, thay vì chỉ dựa vào kết quả kiểm thử. | Khi bác sĩ bảo 'chạy thử xem', hoặc muốn ảnh chụp màn hình chứng minh sửa xong đã đúng. | — |
| `/schedule` — Đặt lịch chạy tự động | Tạo tác vụ chạy theo lịch trên máy chủ (theo giờ, theo ngày trong tuần), hoặc hẹn chạy một lần vào thời điểm định trước. | Khi muốn một việc tự chạy định kỳ mà không cần bác sĩ mở máy — ví dụ quét cập nhật guideline hằng tuần. | Hệ EBM của bác sĩ đã có lịch riêng bằng launchd (com.medicalebm.weeklysafety / monthlyupdate) — đừng đặt trùng hai nơi. |
| `/security-review` — Rà soát an toàn bảo mật | Soi phần mã đã thay đổi theo góc bảo mật: lộ khoá hay mật khẩu, dữ liệu người dùng đi ra ngoài, kiểm tra đầu vào lỏng lẻo, phân quyền sai. | Trước khi phát hành thay đổi có đụng tới dữ liệu nhạy cảm. | Rất đáng chạy với mọi thay đổi trong hệ EBM có chạm tới dữ liệu bệnh nhân hoặc khoá ký cổng. |
| `/simplify` — Rà gọn phần mã vừa sửa | Soi lại đoạn mã vừa thay đổi để tìm chỗ trùng lặp, chỗ viết vòng vo, chỗ đặt sai tầng — rồi sửa gọn lại. | Sau khi vừa viết xong một tính năng, muốn dọn trước khi chốt. | CHỈ lo chất lượng cách viết, KHÔNG đi tìm lỗi sai. Muốn tìm lỗi thì dùng `review`. |
| `/update-config` — Sửa cấu hình Claude Code | Sửa file settings.json: cấp quyền chạy lệnh, đặt biến môi trường, và quan trọng nhất là cài HOOK — cơ chế để hệ thống TỰ LÀM một việc mỗi khi xảy ra sự kiện nào đó. | Khi bác sĩ muốn 'từ nay mỗi lần X thì tự động làm Y', hoặc muốn bớt bị hỏi xin phép cho một loại lệnh. | Yêu cầu kiểu 'mỗi lần... thì tự động...' BẮT BUỘC phải qua hook — ghi vào bộ nhớ hay CLAUDE.md đều không làm được, vì đó là việc của phần mềm chứ không phải của trợ lý. |

---

## TẦNG 1 — Y khoa, nghiên cứu, tài liệu (dùng thường xuyên)  (281 mục)


### openmed-skills  (72)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `/openmed-skills:annotating-variants` | kỹ năng | Chú giải biến thể di truyền trong file VCF và chuẩn hoá danh pháp HGVS bằng công cụ mở (Ensembl VEP, SnpEff, ANNOVAR). Dùng cho nghiên cứu di truyền. Từ khoá: VCF, HGVS, variant annotation. |
| `/openmed-skills:assembling-fhir-bundles` | kỹ năng | Gói nhiều tài nguyên FHIR R4 thành một transaction Bundle hợp lệ, sẵn sàng gửi vào bệnh án điện tử. Dùng ở bước cuối trước khi ghi vào hệ thống. Từ khoá: FHIR Bundle. |
| `/openmed-skills:auditing-deid-leakage` | kỹ năng | Rà ĐỐI KHÁNG văn bản ĐÃ khử định danh để tìm định danh còn sót, và CHẶN phát hành nếu còn dù một dấu vết. Dùng làm chốt kiểm CUỐI trước khi chia sẻ hay công bố dữ liệu. Từ khoá: leakage audit, residual PHI. |
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
| `/openmed-skills:detecting-pv-signals` | kỹ năng | Tính tín hiệu bất cân xứng (PRR, ROR, EBGM, IC) trên dữ liệu FAERS/OpenFDA để phát hiện nghi ngờ về an toàn thuốc. Dùng khi nghiên cứu cảnh giác dược. Từ khoá: pharmacovigilance signal, PRR, ROR. |
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
| `/openmed-skills:resolving-clinical-context` | kỹ năng | Gán PHỦ ĐỊNH, THỜI ĐIỂM và MỨC CHẮC CHẮN cho thực thể đã trích, để 'không đau ngực' không bị đếm thành có đau ngực. Dùng BẮT BUỘC trước khi thống kê tần suất triệu chứng. Từ khoá: negation, temporality, ConText. |
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
| `/openmed-skills:validating-us-core` | kỹ năng | Kiểm tài nguyên và Bundle FHIR R4 theo hồ sơ US Core/USCDI bằng bộ kiểm chính thức của HL7. Dùng trước khi gửi dữ liệu vào bệnh án điện tử, để bắt lỗi cấu trúc sớm. Từ khoá: US Core validation. |

### anthropic-skills  (65)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `/anthropic-skills:EBM-MASTER` | kỹ năng | Nền tảng Y HỌC BẰNG CHỨNG hợp nhất của bác sĩ: lâm sàng, nghiên cứu, thống kê, giám sát guideline, an toàn thuốc, quản lý kháng sinh. Dùng khi cần cửa vào chung cho công việc EBM. Từ khoá: EBM platform. |
| `/anthropic-skills:algorithmic-art` | kỹ năng | Tạo tranh thuật toán bằng p5.js với yếu tố ngẫu nhiên có hạt giống và tham số điều chỉnh được. Dùng cho minh hoạ sáng tạo, không phải biểu đồ dữ liệu. Từ khoá: algorithmic art, p5.js. |
| `/anthropic-skills:alphafold2` | kỹ năng | [Sinh học cấu trúc] Dự đoán cấu trúc protein đơn phân và đa phân bằng AlphaFold2. Dùng cho nghiên cứu tiền lâm sàng, KHÔNG dùng cho chăm sóc bệnh nhân. Từ khoá: AlphaFold2. |
| `/anthropic-skills:antifacts` | kỹ năng | Dùng khi bác sĩ muốn MỞ hoặc CẬP NHẬT \"Antifacts\" — Trung tâm EBM theo chuyên khoa (gom cập nhật chứng cứ + 45 thang điểm lâm sàng + công cụ nghiên cứu theo chuyên khoa). Kích hoạt khi nghe \"Antifacts\", \"mở Antifacts\", \"cập nhật A… |
| `/anthropic-skills:boltz` | kỹ năng | [Sinh học cấu trúc] Dự đoán cấu trúc phức hợp protein – acid nucleic – phân tử nhỏ bằng Boltz-2. Dùng cho nghiên cứu tiền lâm sàng. Từ khoá: Boltz-2. |
| `/anthropic-skills:borzoi` | kỹ năng | [Tin sinh học] Dự đoán tín hiệu chức năng toàn hệ gen (RNA-seq, CAGE, DNase, ChIP) từ chuỗi DNA bằng Borzoi. Dùng trong nghiên cứu hệ gen. Từ khoá: Borzoi, functional genomics. |
| `/anthropic-skills:brand-guidelines` | kỹ năng | Áp bộ màu và kiểu chữ chính thức của Anthropic. Dùng khi làm sản phẩm cần đúng nhận diện thương hiệu đó; ít dùng cho tài liệu y khoa. Từ khoá: brand guidelines. |
| `/anthropic-skills:canvas-design` | kỹ năng | Tạo ẤN PHẨM HÌNH ẢNH đẹp dạng .png/.pdf theo nguyên tắc thiết kế (poster, tờ rơi, thiệp). Dùng khi cần sản phẩm in được. Từ khoá: canvas design, poster. |
| `/anthropic-skills:cap-nhat-chung-cu-y-khoa` | kỹ năng | Sử dụng skill này khi bác sĩ yêu cầu cập nhật chứng cứ hoặc khuyến cáo hiện hành cho MỘT vấn đề lâm sàng cụ thể. Mỗi cập nhật phải kèm Web Dashboard độc lập theo mô hình MẶC ĐỊNH "Evidence Workbench" (bố cục 3 cột: bộ lọc · bảng điểm chứ… |
| `/anthropic-skills:chai1` | kỹ năng | [Sinh học cấu trúc] Dự đoán cấu trúc phức hợp bằng mô hình nền Chai-1. Dùng cho nghiên cứu tiền lâm sàng. Từ khoá: Chai-1. |
| `/anthropic-skills:citation-management` | kỹ năng | Quản lý & kiểm chứng trích dẫn học thuật — phân giải PMID/DOI bắt buộc qua API miễn phí (PubMed/Crossref), đối chiếu metadata, bắt trích dẫn ma & citation washing, cảnh báo retracted/trùng, xuất danh mục Vancouver/ICMJE/AMA/BibTeX. Dùng … |
| `/anthropic-skills:clinical-evidence-rag` | kỹ năng | Cầu nối kiến thức–thực hành: trả lời câu hỏi lâm sàng bằng cách truy xuất (RAG) từ kho y văn do bác sĩ tự nạp. Dùng khi muốn tra trong kho tài liệu riêng thay vì tìm mới trên mạng. Từ khoá: clinical RAG. |
| `/anthropic-skills:compute-env-setup` | kỹ năng | Cài môi trường tính toán trên máy chủ từ xa (SSH/conda, cụm Slurm) để chạy việc nặng. Dùng khi máy cá nhân không đủ sức. Từ khoá: compute environment. |
| `/anthropic-skills:customize` | kỹ năng | Tạo và bảo trì hồ sơ agent riêng, và soạn skill mới qua công cụ repl. Dùng khi muốn tuỳ biến cách trợ lý làm việc. Từ khoá: customize agent profile. |
| `/anthropic-skills:dao-tao-slide-tai-lieu-y-khoa` | kỹ năng | Tạo và chuẩn hóa sản phẩm đào tạo y khoa và tài liệu chuyên môn — bài giảng, slide PowerPoint (.pptx), tài liệu Word (.docx), PDF, infographic/poster, bảng tóm tắt, bảng quyết định, thuật toán lâm sàng (Mermaid), checklist cờ đỏ, bảng th… |
| `/anthropic-skills:dark-analyst` | kỹ năng | Sử dụng skill này khi bác sĩ yêu cầu cập nhật chứng cứ hoặc khuyến cáo hiện hành cho MỘT vấn đề lâm sàng cụ thể. Mỗi cập nhật phải kèm Web Dashboard độc lập theo mô hình MẶC ĐỊNH "Evidence Workbench" (bố cục 3 cột: bộ lọc · bảng điểm chứ… |
| `/anthropic-skills:dashboard-master-ebm-ngoai-tru` | kỹ năng | Tạo, cập nhật hoặc kiểm định Dashboard Master EBM ngoại trú và các sổ Change Log, Evidence Register, Medication Safety, Action Register; xác minh nguồn, loại trùng, lập báo cáo điều hành tháng. |
| `/anthropic-skills:diffdock` | kỹ năng | [Sinh học cấu trúc] Dự đoán tư thế gắn của phân tử nhỏ vào protein bằng DiffDock-L. Dùng khi sàng lọc thuốc tiền lâm sàng. Từ khoá: DiffDock. |
| `/anthropic-skills:doc-coauthoring` | kỹ năng | Đồng soạn tài liệu theo quy trình có cấu trúc (tài liệu kỹ thuật, đề xuất, hướng dẫn). Dùng khi viết tài liệu dài cần thống nhất bố cục. Từ khoá: doc co-authoring. |
| `/anthropic-skills:ehospital-mini` | kỹ năng | Soạn LỜI DẶN & NHẮC TÁI KHÁM ngoại trú cho bệnh nhân — mẫu in (A5/A4), mốc tái khám, cách dùng thuốc gọn, tiêu chí QUAY LẠI NGAY/đi cấp cứu (safety-netting), kế hoạch tuân thủ. Dùng khi cần phát tay tờ dặn dò sau khám. KHÔNG bịa tích hợp… |
| `/anthropic-skills:esmfold2` | kỹ năng | [Sinh học cấu trúc] Gấp cuộn toàn nguyên tử bằng ESMFold2, chạy được từ một chuỗi đơn. Dùng cho nghiên cứu tiền lâm sàng. Từ khoá: ESMFold2. |
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
| `/anthropic-skills:ligandmpnn` | kỹ năng | [Thiết kế protein] Suy ngược chuỗi có tính tới phối tử, acid nucleic và ion kim loại. Dùng cho nghiên cứu tiền lâm sàng. Từ khoá: LigandMPNN. |
| `/anthropic-skills:literature-review` | kỹ năng | Tìm, XÁC MINH và tổng hợp y văn — từ 'bài kinh điển của chủ đề X là bài nào' cho tới tổng quan đa nguồn đầy đủ. Dùng khi cần rà y văn có kiểm chứng nguồn. Từ khoá: literature review. |
| `/anthropic-skills:managed-model-endpoints` | kỹ năng | Đăng ký một dịch vụ mô hình (cục bộ hoặc từ xa) để hệ thống tự bật/tắt khi cần. Dùng khi muốn chạy mô hình riêng ngoài Claude. Từ khoá: model endpoint. |
| `/anthropic-skills:mcp-builder` | kỹ năng | Hướng dẫn dựng máy chủ MCP chất lượng tốt để mô hình gọi được dịch vụ bên ngoài. Dùng khi muốn nối một nguồn dữ liệu mới vào Claude. Từ khoá: MCP server builder. |
| `/anthropic-skills:morning` | kỹ năng | Dựng BẢN TIN BUỔI SÁNG dạng trang HTML, hoặc đặt lịch chạy tự động các ngày trong tuần. Dùng khi bác sĩ yêu cầu rõ — không tự chạy. Từ khoá: morning brief. |
| `/anthropic-skills:nghien-cuu-ebm-tong-hop` | kỹ năng | >- Trợ lý NGHIÊN CỨU Y KHOA & Y HỌC CHỨNG CỨ (EBM) hợp nhất cho bác sĩ lâm sàng. Gồm 5 mô-đun: (1) Tìm & thu thập y văn; (2) Đọc & thẩm định chứng cứ; (3) Thiết kế nghiên cứu lâm sàng; (4) Thống kê & mô hình lâm sàng; (5) Viết & nộp bản … |
| `/anthropic-skills:nghien-cuu-y-khoa-chuan-quoc-te` | kỹ năng | Thực hiện, thiết kế và rà soát nghiên cứu y khoa theo chuẩn quốc tế qua cổng chất lượng G0-G9. Dùng skill này khi người dùng cần xác định câu hỏi/đề cương/protocol, hồ sơ đạo đức và đăng ký nghiên cứu, tính cỡ mẫu, thiết kế biến số/CRF/p… |
| `/anthropic-skills:nguoi-cao-tuoi-da-benh-da-thuoc` | kỹ năng | Chăm sóc toàn diện người cao tuổi suy yếu, đa bệnh lý và đa thuốc theo hướng an toàn thuốc, giảm hại và tránh điều trị quá mức. Dùng skill này bất cứ khi nào có bệnh nhân lớn tuổi kèm nhiều thuốc hoặc nhiều bệnh đồng mắc — rà soát và đối… |
| `/anthropic-skills:openfold3` | kỹ năng | [Sinh học cấu trúc] Dự đoán cấu trúc bằng OpenFold3 — bản mã nguồn mở của AlphaFold3. Dùng cho nghiên cứu tiền lâm sàng. Từ khoá: OpenFold3. |
| `/anthropic-skills:paper-lookup` | kỹ năng | Tra cứu bài báo y khoa qua API MIỄN PHÍ (PubMed E-utilities, Crossref, Europe PMC) — tìm theo PICO/từ khóa/MeSH, phân giải và xác minh PMID/DOI, lấy metadata gốc. Dùng khi cần tìm bài cho một câu hỏi, kiểm một PMID/DOI có thật, hoặc lấy … |
| `/anthropic-skills:paper-narrative` | kỹ năng | Chấm và sắp lại MẠCH TRUYỆN mà bộ hình trong bài báo đang kể — đầu vào là chính bản thảo + bộ hình. Dùng khi bài đủ dữ liệu nhưng đọc rời rạc. Từ khoá: paper narrative, figure story. |
| `/anthropic-skills:pdf-explore` | kỹ năng | Đọc sâu tài liệu PDF dài (bài báo, báo cáo) khi câu trả lời nằm rải ở nhiều chỗ trong file. Dùng khi bác sĩ đính kèm PDF và cần tổng hợp xuyên suốt, không chỉ tra một đoạn. Từ khoá: PDF exploration. |
| `/anthropic-skills:peer-review` | kỹ năng | Bình duyệt bản thảo khoa học có CẤU TRÚC — đánh giá tính hợp lệ (validity), phương pháp, thống kê, đạo đức/đăng ký, trình bày & chuẩn báo cáo, trích dẫn; soạn nhận xét đối kháng đa lăng kính + thư phản biện cho tác giả. Dùng trước khi nộ… |
| `/anthropic-skills:product-self-knowledge` | kỹ năng | Tra thông tin CHÍNH XÁC về sản phẩm của Anthropic (Claude Code, gói dịch vụ, giới hạn). Dùng BẮT BUỘC trước khi khẳng định điều gì về sản phẩm, tránh nói theo trí nhớ. Từ khoá: product facts. |
| `/anthropic-skills:proteinmpnn` | kỹ năng | [Thiết kế protein] Suy ngược chuỗi acid amin từ khung cấu trúc bằng ProteinMPNN. Dùng cho nghiên cứu tiền lâm sàng. Từ khoá: ProteinMPNN. |
| `/anthropic-skills:quan-ly-cap-nhat-ebm` | kỹ năng | Sử dụng skill này khi bác sĩ muốn QUẢN LÝ kho cập nhật EBM đã lưu (sổ cái EBM_MASTER) — xem tổng quan, tìm/lọc, duyệt và phê chuẩn các cập nhật. Kích hoạt với "quản lý EBM", "xem các cập nhật", "hàng đợi duyệt", "duyệt thẻ…", "thống kê s… |
| `/anthropic-skills:remote-compute-modal` | kỹ năng | Chạy việc cần GPU trên tài khoản Modal của bác sĩ. Dùng cho tác vụ học máy nặng. Từ khoá: Modal GPU. |
| `/anthropic-skills:remote-compute-ssh` | kỹ năng | Gửi việc tính toán lên máy chủ SSH/SLURM của bác sĩ rồi chờ và thu kết quả. Dùng sau khi đã quyết định chạy từ xa. Từ khoá: SSH, SLURM. |
| `/anthropic-skills:research-lookup` | kỹ năng | Tra cứu NGHIÊN CỨU & ĐĂNG KÝ THỬ NGHIỆM qua nguồn mở — ClinicalTrials.gov (API v2), WHO ICTRP, PROSPERO. Dùng khi cần kiểm một thử nghiệm đã đăng ký chưa, tìm nghiên cứu đang tiến hành/đã hoàn tất, đối chiếu kết cục đăng ký vs công bố (c… |
| `/anthropic-skills:scgpt` | kỹ năng | [Tế bào đơn] Biểu diễn và chú giải dữ liệu biểu hiện gen tế bào đơn bằng scGPT. Dùng khi phân tích dữ liệu tế bào đơn. Từ khoá: scGPT. |
| `/anthropic-skills:scientific-writing` | kỹ năng | Viết bản thảo khoa học y khoa theo cấu trúc IMRAD, văn xuôi liền mạch, khớp CHUẨN BÁO CÁO đúng thiết kế (CONSORT/STROBE/PRISMA/SPIRIT/STARD/TRIPOD+AI; COREQ/SRQR cho định tính; SQUIRE cho QI). Dùng khi cần viết bài báo, protocol, hoặc bá… |
| `/anthropic-skills:scvi-tools` | kỹ năng | [Tế bào đơn] Phân tích RNA-seq tế bào đơn theo mô hình xác suất với scvi-tools. Dùng khi cần hiệu chỉnh lô hoặc chuyển nhãn bán giám sát. Từ khoá: scvi-tools, scVI. |
| `/anthropic-skills:self-awareness` | kỹ năng | Truy vấn cơ sở dữ liệu phiên làm việc của Claude Science. Dùng khi cần tự kiểm phiên đang chạy gì. Từ khoá: session introspection. |
| `/anthropic-skills:skill-creator` | kỹ năng | Tạo skill mới, sửa và cải thiện skill sẵn có, đo hiệu quả của skill. Dùng khi bác sĩ muốn tự đóng gói một quy trình thành skill gọi được. Từ khoá: skill creator. |
| `/anthropic-skills:slack-gif-creator` | kỹ năng | Tạo ảnh động GIF tối ưu cho Slack, kèm ràng buộc kích thước và công cụ kiểm tra. Dùng khi cần ảnh động cho tin nhắn nhóm. Từ khoá: Slack GIF. |
| `/anthropic-skills:solublempnn` | kỹ năng | [Thiết kế protein] Suy ngược chuỗi thiên về protein TAN được. Dùng cho nghiên cứu tiền lâm sàng. Từ khoá: SolubleMPNN. |
| `/anthropic-skills:statistical-analysis` | kỹ năng | Quy trình phân tích thống kê lâm sàng/nghiên cứu y khoa — mô tả dữ liệu, chọn kiểm định theo loại biến + thiết kế + giả định, hồi quy/sống còn/ROC/hiệu chỉnh, báo cáo ước lượng + 95% CI. Dùng khi cần chạy/đọc phân tích thống kê cho một đ… |
| `/anthropic-skills:tao-video-tiktok` | kỹ năng | >- Tạo video TikTok dọc (9:16, 1080x1920) từ nội dung do người dùng cung cấp, có GIỌNG ĐỌC tiếng Việt mềm mại, ngắt nghỉ tự nhiên (edge-tts HoaiMy nữ / NamMinh nam, tự lùi về giọng macOS "Linh" khi mất mạng) và PHỤ ĐỀ ĐỘNG karaoke đồng b… |
| `/anthropic-skills:tham-dinh-chung-cu-grade-nnt` | kỹ năng | Sử dụng skill này khi cần THẨM ĐỊNH NHANH một bài báo/guideline/nghiên cứu để quyết định có đáng đổi thực hành không. Kích hoạt với "bài này có đáng tin không", "đọc giúp tôi nghiên cứu này", "NNT/NNH bao nhiêu", "nguy cơ sai lệch (risk … |
| `/anthropic-skills:theme-factory` | kỹ năng | Bộ chủ đề trình bày cho slide, tài liệu, báo cáo, trang HTML — có 10 chủ đề dựng sẵn. Dùng khi muốn thống nhất phong cách một bộ sản phẩm. Từ khoá: theme, styling. |
| `/anthropic-skills:tiep-can-chan-doan-co-do-chuyen-tuyen` | kỹ năng | Sử dụng skill này khi bác sĩ tiếp cận MỘT triệu chứng/hội chứng ngoại trú và cần đi từ triệu chứng → chẩn đoán phân biệt → CỜ ĐỎ bắt buộc loại trừ → ngưỡng chuyển tuyến/cấp cứu một cách AN TOÀN. Kích hoạt với "bệnh nhân đau ngực/đau đầu/… |
| `/anthropic-skills:tuan-thu-dieu-tri` | kỹ năng | Sử dụng skill này khi cần đánh giá và cải thiện TUÂN THỦ ĐIỀU TRỊ (medication & treatment adherence) cho bệnh nhân ngoại trú. Kích hoạt khi bác sĩ nói "bệnh nhân không tuân thủ", "hay quên uống thuốc", "bỏ thuốc/tự ngưng thuốc", "uống kh… |
| `/anthropic-skills:using-model-endpoint` | kỹ năng | Gọi một mô hình đã đăng ký qua HTTP API của nó. Dùng sau khi đã đăng ký endpoint. Từ khoá: call model endpoint. |
| `/anthropic-skills:web-artifacts-builder` | kỹ năng | Bộ công cụ dựng trang HTML nhiều thành phần bằng React/Tailwind cho artifact trên claude.ai. Dùng khi cần trang tương tác phức tạp hơn dashboard mẫu. Từ khoá: web artifacts, React. |

### academic-research-skills  (62)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent abstract_bilingual_agent` | agent | [ARS] Agent viết và dịch tóm tắt sang ngôn ngữ đích theo yêu cầu tạp chí. Từ khoá: bilingual abstract. |
| `agent argument_builder_agent` | agent | [ARS] Agent dựng lập luận cốt lõi và mạch suy luận của bài. Từ khoá: argument builder. |
| `agent bibliography_agent` | agent | [ARS] Agent tìm, chú giải và định dạng danh mục tài liệu tham khảo. Từ khoá: bibliography. |
| `agent citation_compliance_agent` | agent | [ARS] Agent đối chiếu trích dẫn với yêu cầu định dạng của tạp chí và gắn cờ chỗ sai. Từ khoá: citation compliance. |
| `agent claim_ref_alignment_audit_agent` | agent | [ARS] Agent soi từng khẳng định có trích dẫn xem có ĐÚNG với nội dung tài liệu gốc không — bắt lỗi trích sai ý. Từ khoá: claim-reference alignment. |
| `agent collaboration_depth_agent` | agent | [ARS] Agent chấm mức độ hợp tác giữa người và AI trong quá trình làm bài. Từ khoá: collaboration depth. |
| `agent compliance_agent` | agent | [ARS] Agent kiểm tuân thủ chuẩn báo cáo tại các cổng liêm chính giữa chừng. Từ khoá: compliance, PRISMA. |
| `agent devils_advocate_agent` | agent | [ARS] Agent phản biện ngược: thách thức giả định và thử phá mạch lập luận. Từ khoá: devil's advocate. |
| `agent devils_advocate_reviewer_agent` | agent | [ARS] Agent phản biện ngược trong vai người bình duyệt: công kích lập luận cốt lõi. Từ khoá: devil's advocate reviewer. |
| `agent domain_reviewer_agent` | agent | [ARS] Agent phản biện số 2: chấm độ chính xác chuyên ngành. Từ khoá: domain reviewer. |
| `agent draft_writer_agent` | agent | [ARS] Agent viết bản thảo đầy đủ theo từng mục từ dàn ý đã chốt. Từ khoá: draft writer. |
| `agent editor_in_chief_agent` | agent | [ARS] Agent rà soát ở mức tạp chí Q1, ra phán quyết Nhận/Từ chối kèm góp ý cụ thể. Từ khoá: editorial verdict. |
| `agent editorial_synthesizer_agent` | agent | [ARS] Agent gộp mọi báo cáo phản biện thành một thư quyết định thống nhất. Từ khoá: editorial synthesis. |
| `agent eic_agent` | agent | [ARS] Agent giữ ghế tổng biên tập: chấm mức phù hợp tạp chí, tính mới và chất lượng chung. Từ khoá: editor-in-chief. |
| `agent ethics_review_agent` | agent | [ARS] Agent tự rà đạo đức nghiên cứu — KHÔNG thay Hội đồng Đạo đức. Hồ sơ nộp hội đồng dùng agent `dao-duc-dang-ky`. Từ khoá: ethics self-check. |
| `agent field_analyst_agent` | agent | [ARS] Agent nhận diện lĩnh vực của bài rồi cấu hình đội phản biện cho phù hợp. Từ khoá: field analyst. |
| `agent formatter_agent` | agent | [ARS] Agent định dạng bản thảo cuối theo yêu cầu của tạp chí đích. Từ khoá: formatting. |
| `agent intake_agent` | agent | [ARS] Agent phỏng vấn đầu vào để dựng hồ sơ cấu hình cho bài báo. Từ khoá: intake. |
| `agent integrity_verification_agent` | agent | [ARS] Agent kiểm mọi tài liệu, trích dẫn và số liệu trước khi nộp. Bản y khoa xác minh PMID/DOI thật là `kiem-chung-trich-dan`. Từ khoá: integrity verification. |
| `agent literature_strategist_agent` | agent | [ARS] Agent thiết kế chiến lược tìm y văn và chọn nguồn. Từ khoá: literature strategy. |
| `agent meta_analysis_agent` | agent | [ARS] Agent tổng hợp định lượng: tính cỡ hiệu ứng, đánh giá tính không đồng nhất. Bản y khoa đầy đủ hơn là agent `meta-phan-tich`. Từ khoá: meta-analysis. |
| `agent methodology_reviewer_agent` | agent | [ARS] Agent phản biện số 1: chấm tính vững của phương pháp và thiết kế nghiên cứu. Từ khoá: methodology reviewer. |
| `agent monitoring_agent` | agent | [ARS] Agent theo dõi y văn mới công bố sau khi nghiên cứu đã xong. Từ khoá: literature monitoring. |
| `agent peer_reviewer_agent` | agent | [ARS] Agent đóng vai phản biện để tìm điểm yếu trước khi nộp. Từ khoá: peer reviewer. |
| `agent perspective_reviewer_agent` | agent | [ARS] Agent phản biện số 3: chấm mức liên ngành và tác động rộng hơn. Từ khoá: perspective reviewer. |
| `agent pipeline_orchestrator_agent` | agent | [ARS] Agent điều phối toàn bộ dây chuyền nghiên cứu học thuật nhiều bước. Từ khoá: pipeline orchestrator. |
| `agent report_compiler_agent` | agent | Agent soạn báo cáo học thuật theo chuẩn APA 7.0 từ kết quả nghiên cứu. Chạy ở Giai đoạn 4 và 6 của dây chuyền ARS. Từ khoá: APA report drafting. |
| `agent report_compiler_agent` | agent | Agent soạn báo cáo học thuật theo chuẩn APA 7.0 từ kết quả nghiên cứu. Chạy ở Giai đoạn 4 và 6 của dây chuyền ARS. Từ khoá: APA report drafting. |
| `agent research_architect_agent` | agent | Agent thiết kế KHUNG PHƯƠNG PHÁP: chọn hệ hình nghiên cứu, phương pháp, chiến lược dữ liệu và khung phân tích. Cho đề tài y khoa thì thiet-ke-nghien-cuu của bác sĩ đúng chuẩn hơn. Từ khoá: methodology blueprint. |
| `agent research_architect_agent` | agent | Agent thiết kế KHUNG PHƯƠNG PHÁP: chọn hệ hình nghiên cứu, phương pháp, chiến lược dữ liệu và khung phân tích. Cho đề tài y khoa thì thiet-ke-nghien-cuu của bác sĩ đúng chuẩn hơn. Từ khoá: methodology blueprint. |
| `agent research_question_agent` | agent | [ARS] Agent biến chủ đề mơ hồ thành câu hỏi nghiên cứu rõ, chấm theo FINER. Với đề tài y khoa nên dùng agent `cau-hoi-nghien-cuu` (có PICO và cổng G0). Từ khoá: research question. |
| `agent revision_coach_agent` | agent | [ARS] Agent phân tích góp ý phản biện thành kế hoạch sửa bài có cấu trúc. Từ khoá: revision coach. |
| `agent risk_of_bias_agent` | agent | [ARS] Agent đánh giá nguy cơ sai lệch bằng RoB 2 (thử nghiệm ngẫu nhiên) và ROBINS-I (nghiên cứu quan sát). Trùng vai với `tham-dinh-grade-nnt` của bác sĩ — ưu tiên agent EBM vì có gắn cổng. Từ khoá: risk of bias. |
| `agent socratic_mentor_agent` | agent | [ARS] Agent dẫn dắt tác giả bằng câu hỏi Socratic để mài sắc lập luận. Từ khoá: Socratic mentor. |
| `agent socratic_mentor_agent` | agent | [ARS] Agent dẫn dắt tác giả bằng câu hỏi Socratic để mài sắc lập luận. Từ khoá: Socratic mentor. |
| `agent source_verification_agent` | agent | [ARS] Agent chấm mức bằng chứng, phát hiện tạp chí săn mồi và kiểm chứng khẳng định. Từ khoá: source verification, predatory journal. |
| `agent state_tracker_agent` | agent | [ARS] Agent theo dõi trạng thái dây chuyền và lịch sử phiên làm việc. Từ khoá: state tracker. |
| `agent structure_architect_agent` | agent | [ARS] Agent thiết kế bố cục các mục và dàn ý chi tiết trước khi viết. Từ khoá: structure architect. |
| `agent synthesis_agent` | agent | Agent TỔNG HỢP xuyên nguồn: gộp phát hiện, xử lý mâu thuẫn giữa các bằng chứng và chỉ ra khoảng trống kiến thức. Từ khoá: synthesis, evidence conflict. |
| `agent synthesis_agent` | agent | Agent TỔNG HỢP xuyên nguồn: gộp phát hiện, xử lý mâu thuẫn giữa các bằng chứng và chỉ ra khoảng trống kiến thức. Từ khoá: synthesis, evidence conflict. |
| `agent timeline_extraction_agent` | agent | [ARS] Agent rút mốc thời gian và nguồn gốc trích dẫn của từng tài liệu. Từ khoá: timeline extraction. |
| `agent visualization_agent` | agent | [ARS] Agent mô tả đặc tả hình và biểu đồ đạt chuẩn công bố. Từ khoá: figure specification. |
| `/ars-3w` | lệnh | Quét bài báo theo ba trục TẠI SAO / LÀM THẾ NÀO / CÁI GÌ. Dùng khi cần so sánh nhanh nhiều bài, nhẹ hơn tổng quan tài liệu. Từ khoá: ARS three-way scan. |
| `/ars-abstract` | lệnh | Viết TÓM TẮT song ngữ + từ khoá. Dùng khi chuẩn bị nộp bài. LƯU Ý: song ngữ ở đây là Trung phồn thể + Anh (zh-TW/EN), KHÔNG phải Việt–Anh. Từ khoá: ARS abstract. |
| `/ars-cache-invalidate` | lệnh | Xoá kết quả kiểm trích dẫn đã lưu tạm của một hoặc nhiều tài liệu, buộc kiểm lại từ đầu. Dùng khi nghi kết quả cũ đã lỗi thời. Từ khoá: ARS cache invalidate. |
| `/ars-citation-check` | lệnh | Xuất BÁO CÁO LỖI TRÍCH DẪN cho bản thảo. Dùng khi rà bài trước khi nộp; với bài y khoa hãy dùng agent `kiem-chung-trich-dan` vì nó xác minh PMID/DOI thật và tra bài bị rút. Từ khoá: ARS citation check. |
| `/ars-disclosure` | lệnh | Soạn câu KHAI BÁO SỬ DỤNG AI theo yêu cầu riêng của từng tạp chí. Dùng khi nộp bài — ICMJE Mục V bắt buộc khai. Từ khoá: ARS AI disclosure. |
| `/ars-format-convert` | lệnh | Chuyển bản thảo qua lại giữa LaTeX / DOCX / PDF / Markdown. Dùng khi tạp chí đòi định dạng khác. Từ khoá: ARS format convert. |
| `/ars-full` | lệnh | Chạy TRỌN dây chuyền bài báo học thuật: tra cứu → viết → bình duyệt → sửa → hoàn thiện. Dùng khi muốn chạy một mạch; tốn token nhất trong bộ ARS. Từ khoá: ARS full pipeline. |
| `/ars-lit-review` | lệnh | Dựng THƯ MỤC CÓ CHÚ GIẢI trình bày theo dạng bài báo. Dùng khi cần phần tổng quan tài liệu; tổng quan hệ thống theo PRISMA thì dùng agent tong-quan-y-van. Từ khoá: ARS lit-review. |
| `/ars-mark-read` | lệnh | Đánh dấu 'người đã đọc thật' cho một hoặc nhiều tài liệu trích dẫn. Dùng khi cần phân biệt bài đã đọc toàn văn với bài chỉ đọc tóm tắt. Từ khoá: ARS mark read. |
| `/ars-outline` | lệnh | Dựng DÀN Ý chi tiết kèm bản đồ bằng chứng cho từng mục, KHÔNG viết thành văn. Dùng khi muốn chốt khung trước khi viết. Từ khoá: ARS outline. |
| `/ars-plan` | lệnh | Lập kế hoạch bài viết theo lối HỎI ĐÁP SOCRATIC, đi từng chương một. Dùng khi chưa rõ nên viết gì, cần người hỏi ngược để làm rõ ý. Từ khoá: ARS plan mode. |
| `/ars-rebuttal-audit` | lệnh | Soi lại THƯ PHẢN HỒI đã viết xem đã trả lời hết từng ý phản biện chưa (chỉ góp ý, không viết thay). Dùng trước khi gửi thư đi. Từ khoá: ARS rebuttal audit. |
| `/ars-reviewer` | lệnh | Chạy hội đồng bình duyệt mô phỏng đầy đủ trên bản thảo. Dùng khi muốn biết bài sẽ bị chê ở đâu trước khi nộp. Từ khoá: ARS reviewer panel. |
| `/ars-revision` | lệnh | Sinh BẢN SỬA của bản thảo kèm phần trả lời góp ý (R&R). Dùng sau khi đã có nhận xét của phản biện. Từ khoá: ARS revision. |
| `/ars-revision-coach` | lệnh | Phân tích góp ý của phản biện thành LỘ TRÌNH SỬA BÀI + khung thư phản hồi. Dùng ngay khi vừa nhận quyết định 'sửa và nộp lại'. Từ khoá: ARS revision coach. |
| `/ars-unmark-read` | lệnh | Gỡ dấu 'đã đọc' đã gắn trước đó cho tài liệu trích dẫn. Dùng khi đánh dấu nhầm. Từ khoá: ARS unmark read. |
| `/academic-research-skills:academic-paper` | kỹ năng | Dây chuyền VIẾT BÀI BÁO HỌC THUẬT tổng quát (12 agent, 11 chế độ). Dùng khi viết bài NGOÀI y khoa; bài y khoa nên dùng agent `viet-ban-thao` vì bám CONSORT/STROBE. Từ khoá: academic paper, APA. |
| `/academic-research-skills:academic-paper-reviewer` | kỹ năng | Mô phỏng HỘI ĐỒNG BÌNH DUYỆT nhiều góc nhìn: 1 tổng biên tập + 3 phản biện + người bảo vệ, mỗi vai một tính cách khác nhau. Dùng khi muốn thử phản biện bản thảo trước khi nộp thật. Từ khoá: peer review simulation. |
| `/academic-research-skills:academic-pipeline` | kỹ năng | Điều phối TRỌN VÒNG bài báo học thuật: tra cứu → viết → kiểm liêm chính → bình duyệt → sửa → bình duyệt lại. Dùng khi muốn chạy một mạch thay vì gọi từng chế độ. Tốn nhiều token (một lần chạy đầy đủ khoảng 4–6 USD). Từ khoá: full pipeline. |
| `/academic-research-skills:deep-research` | kỹ năng | Đội 13 agent NGHIÊN CỨU SÂU cho bất kỳ chủ đề nào, 8 chế độ (nghiên cứu đầy đủ, tóm lược nhanh, so sánh…). Dùng cho chủ đề ngoài y khoa hoặc cần quét rộng; câu hỏi lâm sàng vẫn nên đi qua tra-cuu-chung-cu để có PMID/DOI. Từ khoá: deep re… |

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

### healthcare  (14)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent documents-reader-cli` | agent | [Pháp lý] Tiến trình con đọc một phần kho hợp đồng, bản chạy qua dòng lệnh. Chạy nội bộ, không gọi trực tiếp. Từ khoá: contracts sweep worker CLI. |
| `agent documents-reader-mcp` | agent | [Pháp lý] Tiến trình con đọc một phần kho hợp đồng và ghi nhận phát hiện kèm trích dẫn. Chạy nội bộ, không gọi trực tiếp. Từ khoá: contracts sweep worker. |
| `agent note-extract-worker` | agent | [Y khoa] Tiến trình con bóc dữ liệu cho từng bệnh án khi chạy hàng loạt. Chạy nội bộ, không gọi trực tiếp — dùng `/trich-xuat-benh-an`. Từ khoá: note extraction worker. |
| `/healthcare:clinical-note-extract-skill` | kỹ năng | [Y khoa] Bóc dữ liệu có cấu trúc từ bệnh án, chỉ rõ vị trí từng thông tin trong văn bản gốc. Khử định danh trước khi dùng. Từ khoá: clinical note extraction. |
| `/healthcare:clinical-trial-protocol-skill` | kỹ năng | [Nghiên cứu] Sinh đề cương thử nghiệm lâm sàng cho thuốc hoặc thiết bị y tế. Với đề tài của bác sĩ nên đi qua agent `dieu-phoi-nghien-cuu` để có cổng G0–G10. Từ khoá: trial protocol. |
| `/healthcare:contracts` | kỹ năng | [Pháp lý] Trả lời câu hỏi xuyên suốt một kho hợp đồng, có trích dẫn vị trí. Từ khoá: contract corpus. |
| `/healthcare:doc-extract` | kỹ năng | [Tài liệu] Rút văn bản thuần từ file PDF, DOCX, XLSX, PPTX. Từ khoá: document extraction. |
| `/healthcare:fhir` | kỹ năng | [Y khoa] Kết nối tới máy chủ FHIR R4 của bệnh viện (Epic, Oracle Health/Cerner) để đọc dữ liệu bệnh án điện tử. Từ khoá: FHIR R4, EHR. |
| `/healthcare:fhir-developer-skill` | kỹ năng | [Y khoa] Hướng dẫn lập trình API FHIR khi tự xây điểm cuối cho hệ thống y tế. Từ khoá: FHIR development. |
| `/healthcare:fraud-detection` | kỹ năng | [Y khoa — hệ Mỹ] Sàng kho hồ sơ thanh toán Medicare/Medicaid tìm gian lận và lãng phí. Từ khoá: claims fraud. |
| `/healthcare:icd10-cm-skill` | kỹ năng | [Y khoa] Rút mã chẩn đoán ICD-10-CM dùng để thanh toán từ một bệnh án. Xem thêm lệnh `/tra-ma-icd10`. Từ khoá: ICD-10-CM. |
| `/healthcare:prior-auth-review-skill` | kỹ năng | [Y khoa — hệ Mỹ] Tự động hoá việc xét duyệt yêu cầu chấp thuận trước của hãng bảo hiểm. Ít dùng ở Việt Nam. Từ khoá: prior authorization. |
| `/healthcare:procedure-coding` | kỹ năng | [Y khoa] Gán mã thủ thuật CPT và HCPCS cấp II từ hồ sơ lâm sàng. Đây là bộ mã của Mỹ, khác quy định Việt Nam. Từ khoá: CPT, HCPCS. |
| `/healthcare:verify` | kỹ năng | [Hỗ trợ] Kiểm tra thay đổi đối với script cài đặt quản trị. Từ khoá: verify install. |

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

### bio-research  (6)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `/bio-research:instrument-data-to-allotrope` | kỹ năng | [Tin sinh học] Chuyển dữ liệu máy xét nghiệm (PDF, CSV, Excel) sang chuẩn Allotrope. Từ khoá: Allotrope. |
| `/bio-research:nextflow-development` | kỹ năng | [Tin sinh học] Chạy các đường ống phân tích nf-core (rnaseq, sarek, atacseq) bằng Nextflow. Từ khoá: Nextflow, nf-core. |
| `/bio-research:scientific-problem-selection` | kỹ năng | [Nghiên cứu] Giúp nhà khoa học chọn vấn đề nghiên cứu đáng làm. Từ khoá: problem selection. |
| `/bio-research:scvi-tools` | kỹ năng | [Tế bào đơn] Phân tích RNA tế bào đơn bằng học sâu với scvi-tools. Dùng khi cần hiệu chỉnh lô hoặc chuyển nhãn tế bào. Từ khoá: scvi-tools. |
| `/bio-research:single-cell-rna-qc` | kỹ năng | [Tin sinh học] Kiểm chất lượng dữ liệu RNA tế bào đơn (file .h5ad). Từ khoá: single-cell QC. |
| `/bio-research:start` | kỹ năng | [Nghiên cứu sinh học] Cài môi trường bio-research và xem có sẵn công cụ gì. Dùng khi lần đầu làm quen bộ plugin này, hoặc muốn biết máy chủ tra cứu y văn / dược / hình ảnh nào đang kết nối. Từ khoá: bio-research start, setup. |

### cowork-plugin-management  (2)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `/cowork-plugin-management:cowork-plugin-customizer` | kỹ năng | [Hỗ trợ] Tuỳ chỉnh một plugin Claude Code cho nhu cầu riêng của đơn vị. Từ khoá: plugin customizer. |
| `/cowork-plugin-management:create-cowork-plugin` | kỹ năng | [Hỗ trợ] Hướng dẫn tạo một plugin mới từ đầu. Từ khoá: create plugin. |

---

## TẦNG 2 — Kỹ thuật, dùng khi sửa chính hệ EBM  (191 mục)


### claude-code-harness  (82)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent advisor` | agent | [Lập trình] Agent cố vấn KHÔNG thực thi: chỉ trả về hướng xử lý cho yêu cầu mà agent thợ gửi lên. Từ khoá: advisor agent. |
| `agent advisor` | agent | [Lập trình] Agent cố vấn KHÔNG thực thi: chỉ trả về hướng xử lý cho yêu cầu mà agent thợ gửi lên. Từ khoá: advisor agent. |
| `agent reviewer` | agent | [Lập trình] Agent rà soát CHỈ ĐỌC: đưa phán quyết dựa trên hợp đồng công việc và tài liệu rà soát. Từ khoá: reviewer agent. |
| `agent reviewer` | agent | [Lập trình] Agent rà soát CHỈ ĐỌC: đưa phán quyết dựa trên hợp đồng công việc và tài liệu rà soát. Từ khoá: reviewer agent. |
| `agent test-wiring-auditor` | agent | 変更差分に対してテスト網が追随しているかを fresh-context で監査する read-only auditor |
| `agent worker` | agent | [Lập trình] Agent thợ chính: thực hiện một việc trọn gói — viết mã, tự kiểm trước, xác minh và chuẩn bị commit. Từ khoá: worker agent. |
| `agent worker` | agent | [Lập trình] Agent thợ chính: thực hiện một việc trọn gói — viết mã, tự kiểm trước, xác minh và chuẩn bị commit. Từ khoá: worker agent. |
| `/handoff-to-claude` | lệnh | [Lập trình] Sinh câu lệnh giao việc cho Claude Code. Từ khoá: handoff to Claude. |
| `/handoff-to-claude` | lệnh | [Lập trình] Sinh câu lệnh giao việc cho Claude Code. Từ khoá: handoff to Claude. |
| `/plan-with-cc` | lệnh | [Lập trình] Lập kế hoạch — phối hợp với Claude Code để chia nhỏ công việc. Từ khoá: plan with CC. |
| `/plan-with-cc` | lệnh | [Lập trình] Lập kế hoạch — phối hợp với Claude Code để chia nhỏ công việc. Từ khoá: plan with CC. |
| `/project-overview` | lệnh | [Lập trình] Nắm nhanh bức tranh tổng thể của dự án. Từ khoá: project overview. |
| `/project-overview` | lệnh | [Lập trình] Nắm nhanh bức tranh tổng thể của dự án. Từ khoá: project overview. |
| `/review-cc-work` | lệnh | [Lập trình] Rà soát việc Claude Code đã làm rồi bàn giao lại kèm chỉ dẫn duyệt hoặc sửa. Từ khoá: review CC work. |
| `/review-cc-work` | lệnh | [Lập trình] Rà soát việc Claude Code đã làm rồi bàn giao lại kèm chỉ dẫn duyệt hoặc sửa. Từ khoá: review CC work. |
| `/start-session` | lệnh | [Lập trình] Bắt đầu phiên làm việc: nắm tình hình → lập kế hoạch → giao việc cho Claude Code. Từ khoá: start session. |
| `/start-session` | lệnh | [Lập trình] Bắt đầu phiên làm việc: nắm tình hình → lập kế hoạch → giao việc cho Claude Code. Từ khoá: start session. |
| `/claude-code-harness:agent-browser` | kỹ năng | [Lập trình] Điều khiển trình duyệt tự động: mở trang, điền biểu mẫu, chụp màn hình, thu thập dữ liệu. Từ khoá: browser automation. |
| `/claude-code-harness:agent-browser` | kỹ năng | [Lập trình] Điều khiển trình duyệt tự động: mở trang, điền biểu mẫu, chụp màn hình, thu thập dữ liệu. Từ khoá: browser automation. |
| `/claude-code-harness:agent-browser` | kỹ năng | [Lập trình] Điều khiển trình duyệt tự động: mở trang, điền biểu mẫu, chụp màn hình, thu thập dữ liệu. Từ khoá: browser automation. |
| `/claude-code-harness:breezing` | kỹ năng | [Lập trình] Chế độ chạy theo NHÓM — tên gọi cũ tương đương harness-work có điều phối nhiều agent. Từ khoá: team execution. |
| `/claude-code-harness:breezing` | kỹ năng | [Lập trình] Chế độ chạy theo NHÓM — tên gọi cũ tương đương harness-work có điều phối nhiều agent. Từ khoá: team execution. |
| `/claude-code-harness:breezing` | kỹ năng | [Lập trình] Chế độ chạy theo NHÓM — tên gọi cũ tương đương harness-work có điều phối nhiều agent. Từ khoá: team execution. |
| `/claude-code-harness:breezing` | kỹ năng | [Lập trình] Chế độ chạy theo NHÓM — tên gọi cũ tương đương harness-work có điều phối nhiều agent. Từ khoá: team execution. |
| `/claude-code-harness:cc-update-review` | kỹ năng | [Lập trình] Chốt chất lượng khi tích hợp bản cập nhật Claude/Codex; bắt trường hợp chỉ thêm tài liệu mà chưa có mã thật. Từ khoá: update review. |
| `/claude-code-harness:cc-update-review` | kỹ năng | [Lập trình] Chốt chất lượng khi tích hợp bản cập nhật Claude/Codex; bắt trường hợp chỉ thêm tài liệu mà chưa có mã thật. Từ khoá: update review. |
| `/claude-code-harness:ci` | kỹ năng | [Lập trình] Chữa cháy CI: build đỏ, test hỏng, pipeline lỗi. Từ khoá: CI failure, build error. |
| `/claude-code-harness:ci` | kỹ năng | [Lập trình] Chữa cháy CI: build đỏ, test hỏng, pipeline lỗi. Từ khoá: CI failure, build error. |
| `/claude-code-harness:ci` | kỹ năng | [Lập trình] Chữa cháy CI: build đỏ, test hỏng, pipeline lỗi. Từ khoá: CI failure, build error. |
| `/claude-code-harness:cursor-ask` | kỹ năng | [Lập trình] Hỏi Cursor ở chế độ CHỈ ĐỌC để điều tra, bàn thiết kế, phản biện — không cho sửa file. Từ khoá: cursor ask. |
| `/claude-code-harness:cursor-ask` | kỹ năng | [Lập trình] Hỏi Cursor ở chế độ CHỈ ĐỌC để điều tra, bàn thiết kế, phản biện — không cho sửa file. Từ khoá: cursor ask. |
| `/claude-code-harness:cursor-ask` | kỹ năng | [Lập trình] Hỏi Cursor ở chế độ CHỈ ĐỌC để điều tra, bàn thiết kế, phản biện — không cho sửa file. Từ khoá: cursor ask. |
| `/claude-code-harness:cursor-do` | kỹ năng | [Lập trình] Giao MỘT việc có sửa file cho Cursor trong nhánh làm việc tách biệt rồi thu kết quả về. Từ khoá: cursor do. |
| `/claude-code-harness:cursor-do` | kỹ năng | [Lập trình] Giao MỘT việc có sửa file cho Cursor trong nhánh làm việc tách biệt rồi thu kết quả về. Từ khoá: cursor do. |
| `/claude-code-harness:cursor-do` | kỹ năng | [Lập trình] Giao MỘT việc có sửa file cho Cursor trong nhánh làm việc tách biệt rồi thu kết quả về. Từ khoá: cursor do. |
| `/claude-code-harness:cursor-review` | kỹ năng | [Lập trình] Nhờ Cursor rà soát như ý kiến thứ hai; kết luận cuối vẫn thuộc về bên chính. Từ khoá: cursor review. |
| `/claude-code-harness:cursor-review` | kỹ năng | [Lập trình] Nhờ Cursor rà soát như ý kiến thứ hai; kết luận cuối vẫn thuộc về bên chính. Từ khoá: cursor review. |
| `/claude-code-harness:cursor-review` | kỹ năng | [Lập trình] Nhờ Cursor rà soát như ý kiến thứ hai; kết luận cuối vẫn thuộc về bên chính. Từ khoá: cursor review. |
| `/claude-code-harness:cursor-setup` | kỹ năng | [Lập trình] Cài và kiểm tra nền Cursor cho harness. Từ khoá: cursor setup. |
| `/claude-code-harness:cursor-setup` | kỹ năng | [Lập trình] Cài và kiểm tra nền Cursor cho harness. Từ khoá: cursor setup. |
| `/claude-code-harness:cursor-setup` | kỹ năng | [Lập trình] Cài và kiểm tra nền Cursor cho harness. Từ khoá: cursor setup. |
| `/claude-code-harness:failure-codifier` | kỹ năng | Extract recurring failure patterns from breezing orchestration logs and Judgment Ledger, emit failure-rule.v1 proposals with confidence scores. SSOT promotion to patterns.md or decisions.md is proposal-only — human-approval-required. Use… |
| `/claude-code-harness:failure-codifier` | kỹ năng | Extract recurring failure patterns from breezing orchestration logs and Judgment Ledger, emit failure-rule.v1 proposals with confidence scores. SSOT promotion to patterns.md or decisions.md is proposal-only — human-approval-required. Use… |
| `/claude-code-harness:failure-codifier` | kỹ năng | Extract recurring failure patterns from breezing orchestration logs and Judgment Ledger, emit failure-rule.v1 proposals with confidence scores. SSOT promotion to patterns.md or decisions.md is proposal-only — human-approval-required. Use… |
| `/claude-code-harness:harness-accept` | kỹ năng | [Lập trình] Dựng trang HTML NGHIỆM THU cho người không rành kỹ thuật xem trước khi quyết định phát hành. Từ khoá: acceptance demo. |
| `/claude-code-harness:harness-accept` | kỹ năng | [Lập trình] Dựng trang HTML NGHIỆM THU cho người không rành kỹ thuật xem trước khi quyết định phát hành. Từ khoá: acceptance demo. |
| `/claude-code-harness:harness-accept` | kỹ năng | [Lập trình] Dựng trang HTML NGHIỆM THU cho người không rành kỹ thuật xem trước khi quyết định phát hành. Từ khoá: acceptance demo. |
| `/claude-code-harness:harness-loop` | kỹ năng | [Lập trình] Chạy việc DÀI HƠI theo vòng lặp, tự hẹn giờ quay lại với ngữ cảnh mới. Dùng cho việc nhiều giờ. Từ khoá: harness loop. |
| `/claude-code-harness:harness-loop` | kỹ năng | [Lập trình] Chạy việc DÀI HƠI theo vòng lặp, tự hẹn giờ quay lại với ngữ cảnh mới. Dùng cho việc nhiều giờ. Từ khoá: harness loop. |
| `/claude-code-harness:harness-loop` | kỹ năng | [Lập trình] Chạy việc DÀI HƠI theo vòng lặp, tự hẹn giờ quay lại với ngữ cảnh mới. Dùng cho việc nhiều giờ. Từ khoá: harness loop. |
| `/claude-code-harness:harness-loop` | kỹ năng | [Lập trình] Chạy việc DÀI HƠI theo vòng lặp, tự hẹn giờ quay lại với ngữ cảnh mới. Dùng cho việc nhiều giờ. Từ khoá: harness loop. |
| `/claude-code-harness:harness-plan` | kỹ năng | [Lập trình] Lập KẾ HOẠCH công việc có kiểm chứng, quản lý Plans.md và đồng bộ tiến độ. Dùng khi bắt đầu một hạng mục sửa hệ thống. Từ khoá: harness plan, Plans.md. |
| `/claude-code-harness:harness-plan` | kỹ năng | [Lập trình] Lập KẾ HOẠCH công việc có kiểm chứng, quản lý Plans.md và đồng bộ tiến độ. Dùng khi bắt đầu một hạng mục sửa hệ thống. Từ khoá: harness plan, Plans.md. |
| `/claude-code-harness:harness-plan` | kỹ năng | [Lập trình] Lập KẾ HOẠCH công việc có kiểm chứng, quản lý Plans.md và đồng bộ tiến độ. Dùng khi bắt đầu một hạng mục sửa hệ thống. Từ khoá: harness plan, Plans.md. |
| `/claude-code-harness:harness-plan-brief` | kỹ năng | [Lập trình] Dựng trang HTML TÓM TẮT KẾ HOẠCH dễ đọc cho người không rành kỹ thuật, trước khi bắt tay làm. Từ khoá: plan brief. |
| `/claude-code-harness:harness-plan-brief` | kỹ năng | [Lập trình] Dựng trang HTML TÓM TẮT KẾ HOẠCH dễ đọc cho người không rành kỹ thuật, trước khi bắt tay làm. Từ khoá: plan brief. |
| `/claude-code-harness:harness-plan-brief` | kỹ năng | [Lập trình] Dựng trang HTML TÓM TẮT KẾ HOẠCH dễ đọc cho người không rành kỹ thuật, trước khi bắt tay làm. Từ khoá: plan brief. |
| `/claude-code-harness:harness-progress` | kỹ năng | [Lập trình] Dựng trang HTML THEO DÕI TIẾN ĐỘ phiên làm việc để liếc nhanh. Từ khoá: progress tracker. |
| `/claude-code-harness:harness-progress` | kỹ năng | [Lập trình] Dựng trang HTML THEO DÕI TIẾN ĐỘ phiên làm việc để liếc nhanh. Từ khoá: progress tracker. |
| `/claude-code-harness:harness-progress` | kỹ năng | [Lập trình] Dựng trang HTML THEO DÕI TIẾN ĐỘ phiên làm việc để liếc nhanh. Từ khoá: progress tracker. |
| `/claude-code-harness:harness-release` | kỹ năng | [Lập trình] Tự động hoá phát hành theo Keep a Changelog + GitHub, có một cổng xác nhận trước khi chạy. Từ khoá: harness release. |
| `/claude-code-harness:harness-release` | kỹ năng | [Lập trình] Tự động hoá phát hành theo Keep a Changelog + GitHub, có một cổng xác nhận trước khi chạy. Từ khoá: harness release. |
| `/claude-code-harness:harness-release` | kỹ năng | [Lập trình] Tự động hoá phát hành theo Keep a Changelog + GitHub, có một cổng xác nhận trước khi chạy. Từ khoá: harness release. |
| `/claude-code-harness:harness-review` | kỹ năng | [Lập trình] RÀ SOÁT mã nguồn, kế hoạch và phạm vi từ nhiều góc; kiểm bảo mật và chất lượng. Từ khoá: harness review, code review. |
| `/claude-code-harness:harness-review` | kỹ năng | [Lập trình] RÀ SOÁT mã nguồn, kế hoạch và phạm vi từ nhiều góc; kiểm bảo mật và chất lượng. Từ khoá: harness review, code review. |
| `/claude-code-harness:harness-review` | kỹ năng | [Lập trình] RÀ SOÁT mã nguồn, kế hoạch và phạm vi từ nhiều góc; kiểm bảo mật và chất lượng. Từ khoá: harness review, code review. |
| `/claude-code-harness:harness-setup` | kỹ năng | [Lập trình] Khởi tạo dự án, cài công cụ, cấu hình agent, dựng bộ nhớ và đồng bộ bản sao skill. Từ khoá: harness setup, init. |
| `/claude-code-harness:harness-setup` | kỹ năng | [Lập trình] Khởi tạo dự án, cài công cụ, cấu hình agent, dựng bộ nhớ và đồng bộ bản sao skill. Từ khoá: harness setup, init. |
| `/claude-code-harness:harness-setup` | kỹ năng | [Lập trình] Khởi tạo dự án, cài công cụ, cấu hình agent, dựng bộ nhớ và đồng bộ bản sao skill. Từ khoá: harness setup, init. |
| `/claude-code-harness:harness-sync` | kỹ năng | [Lập trình] Đối chiếu Plans.md với mã thật, phát hiện lệch, cập nhật mốc và rút kinh nghiệm. Dùng khi hỏi 'đang làm tới đâu'. Từ khoá: harness sync, drift. |
| `/claude-code-harness:harness-sync` | kỹ năng | [Lập trình] Đối chiếu Plans.md với mã thật, phát hiện lệch, cập nhật mốc và rút kinh nghiệm. Dùng khi hỏi 'đang làm tới đâu'. Từ khoá: harness sync, drift. |
| `/claude-code-harness:harness-sync` | kỹ năng | [Lập trình] Đối chiếu Plans.md với mã thật, phát hiện lệch, cập nhật mốc và rút kinh nghiệm. Dùng khi hỏi 'đang làm tới đâu'. Từ khoá: harness sync, drift. |
| `/claude-code-harness:harness-work` | kỹ năng | [Lập trình] THỰC THI các việc trong Plans.md, từ một việc lẻ tới chạy song song cả nhóm. Từ khoá: harness work, implement. |
| `/claude-code-harness:harness-work` | kỹ năng | [Lập trình] THỰC THI các việc trong Plans.md, từ một việc lẻ tới chạy song song cả nhóm. Từ khoá: harness work, implement. |
| `/claude-code-harness:harness-work` | kỹ năng | [Lập trình] THỰC THI các việc trong Plans.md, từ một việc lẻ tới chạy song song cả nhóm. Từ khoá: harness work, implement. |
| `/claude-code-harness:harness-work` | kỹ năng | [Lập trình] THỰC THI các việc trong Plans.md, từ một việc lẻ tới chạy song song cả nhóm. Từ khoá: harness work, implement. |
| `/claude-code-harness:maintenance` | kỹ năng | [Lập trình] Dọn dẹp và lưu trữ file: Plans.md phình to, nhật ký phiên, log cũ. Từ khoá: cleanup, archiving. |
| `/claude-code-harness:maintenance` | kỹ năng | [Lập trình] Dọn dẹp và lưu trữ file: Plans.md phình to, nhật ký phiên, log cũ. Từ khoá: cleanup, archiving. |
| `/claude-code-harness:maintenance` | kỹ năng | [Lập trình] Dọn dẹp và lưu trữ file: Plans.md phình to, nhật ký phiên, log cũ. Từ khoá: cleanup, archiving. |
| `/claude-code-harness:memory` | kỹ năng | [Lập trình] Quản lý bộ nhớ dự án và tìm kiếm xuyên công cụ; giữ decisions.md và patterns.md. Từ khoá: memory, SSOT. |
| `/claude-code-harness:memory` | kỹ năng | [Lập trình] Quản lý bộ nhớ dự án và tìm kiếm xuyên công cụ; giữ decisions.md và patterns.md. Từ khoá: memory, SSOT. |
| `/claude-code-harness:memory` | kỹ năng | [Lập trình] Quản lý bộ nhớ dự án và tìm kiếm xuyên công cụ; giữ decisions.md và patterns.md. Từ khoá: memory, SSOT. |

### mattpocock-skills  (41)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `/mattpocock-skills:ask-matt` | kỹ năng | [Lập trình] Hỏi xem tình huống hiện tại nên dùng kỹ năng nào trong bộ này. Từ khoá: skill router. |
| `/mattpocock-skills:batch-grill-me` | kỹ năng | [Lập trình] Chất vấn dồn dập, hỏi mọi câu khó cùng lúc theo từng vòng. Từ khoá: batch grilling. |
| `/mattpocock-skills:claude-handoff` | kỹ năng | [Lập trình] Bàn giao cuộc trò chuyện cho một agent chạy nền tiếp nhận. Từ khoá: claude handoff. |
| `/mattpocock-skills:code-review` | kỹ năng | [Lập trình] Rà soát thay đổi kể từ một mốc cố định (commit, nhánh, thẻ). Từ khoá: code review. |
| `/mattpocock-skills:codebase-design` | kỹ năng | [Lập trình] Bộ từ vựng chung để thiết kế mô-đun có chiều sâu. Từ khoá: deep modules. |
| `/mattpocock-skills:design-an-interface` | kỹ năng | [Lập trình] Sinh nhiều phương án thiết kế giao diện lập trình khác hẳn nhau để so sánh. Từ khoá: interface design. |
| `/mattpocock-skills:diagnosing-bugs` | kỹ năng | [Lập trình] Vòng chẩn đoán cho lỗi khó và sụt hiệu năng. Từ khoá: bug diagnosis. |
| `/mattpocock-skills:domain-modeling` | kỹ năng | [Lập trình] Dựng và mài sắc mô hình miền nghiệp vụ của dự án. Từ khoá: domain model. |
| `/mattpocock-skills:edit-article` | kỹ năng | [Viết lách] Biên tập bài viết: sắp lại bố cục, làm rõ ý, gọt câu chữ. Từ khoá: edit article. |
| `/mattpocock-skills:git-guardrails-claude-code` | kỹ năng | [Lập trình] Cài chốt chặn lệnh git nguy hiểm (push, reset --hard...). Từ khoá: git guardrails. |
| `/mattpocock-skills:grill-me` | kỹ năng | [Lập trình] Phỏng vấn gắt để mài sắc một kế hoạch hoặc thiết kế. Từ khoá: grill me. |
| `/mattpocock-skills:grill-with-docs` | kỹ năng | [Lập trình] Vừa chất vấn vừa sinh tài liệu ghi lại quyết định. Từ khoá: grill with docs. |
| `/mattpocock-skills:grilling` | kỹ năng | [Lập trình] Chất vấn liên tục về một kế hoạch, quyết định hay ý tưởng để lộ điểm yếu. Từ khoá: grilling. |
| `/mattpocock-skills:handoff` | kỹ năng | [Lập trình] Nén cuộc trò chuyện hiện tại thành tài liệu bàn giao cho agent khác tiếp tục. Từ khoá: handoff. |
| `/mattpocock-skills:implement` | kỹ năng | [Lập trình] Triển khai một phần việc theo đặc tả hoặc danh sách hạng mục. Từ khoá: implement. |
| `/mattpocock-skills:improve-codebase-architecture` | kỹ năng | [Lập trình] Quét kho mã tìm chỗ nên làm sâu hơn, xuất báo cáo HTML trực quan. Từ khoá: architecture improvement. |
| `/mattpocock-skills:loop-me` | kỹ năng | [Lập trình] Chất vấn về đặc tả cho các quy trình muốn xây trong không gian làm việc này. Từ khoá: loop me. |
| `/mattpocock-skills:migrate-to-shoehorn` | kỹ năng | [Lập trình] Chuyển file kiểm thử sang dùng thư viện shoehorn thay cho ép kiểu bằng `as`. Từ khoá: shoehorn migration. |
| `/mattpocock-skills:obsidian-vault` | kỹ năng | [Lập trình] Tìm, tạo và quản lý ghi chú trong kho Obsidian, có liên kết wiki. Từ khoá: Obsidian. |
| `/mattpocock-skills:prototype` | kỹ năng | [Lập trình] Dựng bản thử nghiệm dùng một lần để trả lời một câu hỏi thiết kế. Từ khoá: prototype. |
| `/mattpocock-skills:qa` | kỹ năng | [Lập trình] Phiên kiểm thử tương tác: người dùng báo lỗi bằng lời, hệ thống ghi nhận và xử lý. Từ khoá: QA session. |
| `/mattpocock-skills:request-refactor-plan` | kỹ năng | [Lập trình] Lập kế hoạch tái cấu trúc chi tiết với các bước commit rất nhỏ. Từ khoá: refactor plan. |
| `/mattpocock-skills:research` | kỹ năng | [Lập trình] Tra cứu một câu hỏi dựa trên nguồn gốc đáng tin và ghi lại kết quả. Từ khoá: research. |
| `/mattpocock-skills:resolving-merge-conflicts` | kỹ năng | [Lập trình] Xử lý xung đột khi đang merge hoặc rebase dở dang. Từ khoá: merge conflicts. |
| `/mattpocock-skills:scaffold-exercises` | kỹ năng | [Lập trình] Dựng khung thư mục bài tập gồm đề bài, lời giải và giải thích. Từ khoá: scaffold exercises. |
| `/mattpocock-skills:setup-matt-pocock-skills` | kỹ năng | [Lập trình] Cấu hình kho mã để dùng được bộ kỹ năng này. Từ khoá: setup. |
| `/mattpocock-skills:setup-pre-commit` | kỹ năng | [Lập trình] Cài chốt kiểm trước khi commit: định dạng mã, kiểm kiểu. Từ khoá: pre-commit hooks. |
| `/mattpocock-skills:setup-ts-deep-modules` | kỹ năng | [Lập trình] Cấu hình kho mã TypeScript để mỗi gói là một mô-đun sâu. Từ khoá: deep modules, TypeScript. |
| `/mattpocock-skills:tdd` | kỹ năng | [Lập trình] Phát triển hướng kiểm thử: viết test trước rồi mới viết mã. Từ khoá: TDD. |
| `/mattpocock-skills:teach` | kỹ năng | [Lập trình] Dạy một kỹ năng hoặc khái niệm mới ngay trong không gian làm việc. Từ khoá: teach. |
| `/mattpocock-skills:to-questionnaire` | kỹ năng | [Lập trình] Biến một quyết định chưa tự trả lời được thành bộ câu hỏi gửi người khác. Từ khoá: questionnaire. |
| `/mattpocock-skills:to-spec` | kỹ năng | [Lập trình] Biến cuộc trò chuyện hiện tại thành bản đặc tả và đăng lên hệ theo dõi việc. Từ khoá: to spec. |
| `/mattpocock-skills:to-tickets` | kỹ năng | [Lập trình] Chia kế hoạch hoặc đặc tả thành các phiếu việc nhỏ chạy được. Từ khoá: to tickets. |
| `/mattpocock-skills:triage` | kỹ năng | [Lập trình] Đưa các vấn đề và pull request bên ngoài qua quy trình phân loại nhiều vai. Từ khoá: triage. |
| `/mattpocock-skills:ubiquitous-language` | kỹ năng | [Lập trình] Rút bảng thuật ngữ thống nhất cho dự án từ chính cuộc trò chuyện. Từ khoá: ubiquitous language. |
| `/mattpocock-skills:wayfinder` | kỹ năng | [Lập trình] Lập kế hoạch cho khối việc lớn hơn sức chứa của một phiên agent. Từ khoá: wayfinder. |
| `/mattpocock-skills:wizard` | kỹ năng | [Lập trình] Sinh trình hướng dẫn dạng bash dắt người dùng qua một quy trình thủ công. Từ khoá: bash wizard. |
| `/mattpocock-skills:writing-beats` | kỹ năng | [Viết lách] Giai đoạn DỰNG MẠCH: ghép nguyên liệu thành hành trình các nhịp có căn cứ. Từ khoá: writing beats. |
| `/mattpocock-skills:writing-fragments` | kỹ năng | [Viết lách] Giai đoạn KHAI PHÁ: gom mảnh ý thô, chưa cần bố cục. Từ khoá: writing fragments. |
| `/mattpocock-skills:writing-great-skills` | kỹ năng | [Lập trình] Tài liệu tham chiếu về cách viết và biên tập một skill cho tốt. Từ khoá: writing skills. |
| `/mattpocock-skills:writing-shape` | kỹ năng | [Viết lách] Giai đoạn ĐỊNH HÌNH: nắn nguyên liệu thô thành bài, từng đoạn một. Từ khoá: writing shape. |

### pubmed  (14)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent documents-reader-cli` | agent | [Pháp lý] Tiến trình con đọc một phần kho hợp đồng, bản chạy qua dòng lệnh. Chạy nội bộ, không gọi trực tiếp. Từ khoá: contracts sweep worker CLI. |
| `agent documents-reader-mcp` | agent | [Pháp lý] Tiến trình con đọc một phần kho hợp đồng và ghi nhận phát hiện kèm trích dẫn. Chạy nội bộ, không gọi trực tiếp. Từ khoá: contracts sweep worker. |
| `agent note-extract-worker` | agent | [Y khoa] Tiến trình con bóc dữ liệu cho từng bệnh án khi chạy hàng loạt. Chạy nội bộ, không gọi trực tiếp — dùng `/trich-xuat-benh-an`. Từ khoá: note extraction worker. |
| `/pubmed:clinical-note-extract-skill` | kỹ năng | [Y khoa] Bóc dữ liệu có cấu trúc từ bệnh án, chỉ rõ vị trí từng thông tin trong văn bản gốc. Khử định danh trước khi dùng. Từ khoá: clinical note extraction. |
| `/pubmed:clinical-trial-protocol-skill` | kỹ năng | [Nghiên cứu] Sinh đề cương thử nghiệm lâm sàng cho thuốc hoặc thiết bị y tế. Với đề tài của bác sĩ nên đi qua agent `dieu-phoi-nghien-cuu` để có cổng G0–G10. Từ khoá: trial protocol. |
| `/pubmed:contracts` | kỹ năng | [Pháp lý] Trả lời câu hỏi xuyên suốt một kho hợp đồng, có trích dẫn vị trí. Từ khoá: contract corpus. |
| `/pubmed:doc-extract` | kỹ năng | [Tài liệu] Rút văn bản thuần từ file PDF, DOCX, XLSX, PPTX. Từ khoá: document extraction. |
| `/pubmed:fhir` | kỹ năng | [Y khoa] Kết nối tới máy chủ FHIR R4 của bệnh viện (Epic, Oracle Health/Cerner) để đọc dữ liệu bệnh án điện tử. Từ khoá: FHIR R4, EHR. |
| `/pubmed:fhir-developer-skill` | kỹ năng | [Y khoa] Hướng dẫn lập trình API FHIR khi tự xây điểm cuối cho hệ thống y tế. Từ khoá: FHIR development. |
| `/pubmed:fraud-detection` | kỹ năng | [Y khoa — hệ Mỹ] Sàng kho hồ sơ thanh toán Medicare/Medicaid tìm gian lận và lãng phí. Từ khoá: claims fraud. |
| `/pubmed:icd10-cm-skill` | kỹ năng | [Y khoa] Rút mã chẩn đoán ICD-10-CM dùng để thanh toán từ một bệnh án. Xem thêm lệnh `/tra-ma-icd10`. Từ khoá: ICD-10-CM. |
| `/pubmed:prior-auth-review-skill` | kỹ năng | [Y khoa — hệ Mỹ] Tự động hoá việc xét duyệt yêu cầu chấp thuận trước của hãng bảo hiểm. Ít dùng ở Việt Nam. Từ khoá: prior authorization. |
| `/pubmed:procedure-coding` | kỹ năng | [Y khoa] Gán mã thủ thuật CPT và HCPCS cấp II từ hồ sơ lâm sàng. Đây là bộ mã của Mỹ, khác quy định Việt Nam. Từ khoá: CPT, HCPCS. |
| `/pubmed:verify` | kỹ năng | [Hỗ trợ] Kiểm tra thay đổi đối với script cài đặt quản trị. Từ khoá: verify install. |

### icd10-codes  (14)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `agent documents-reader-cli` | agent | [Pháp lý] Tiến trình con đọc một phần kho hợp đồng, bản chạy qua dòng lệnh. Chạy nội bộ, không gọi trực tiếp. Từ khoá: contracts sweep worker CLI. |
| `agent documents-reader-mcp` | agent | [Pháp lý] Tiến trình con đọc một phần kho hợp đồng và ghi nhận phát hiện kèm trích dẫn. Chạy nội bộ, không gọi trực tiếp. Từ khoá: contracts sweep worker. |
| `agent note-extract-worker` | agent | [Y khoa] Tiến trình con bóc dữ liệu cho từng bệnh án khi chạy hàng loạt. Chạy nội bộ, không gọi trực tiếp — dùng `/trich-xuat-benh-an`. Từ khoá: note extraction worker. |
| `/icd10-codes:clinical-note-extract-skill` | kỹ năng | [Y khoa] Bóc dữ liệu có cấu trúc từ bệnh án, chỉ rõ vị trí từng thông tin trong văn bản gốc. Khử định danh trước khi dùng. Từ khoá: clinical note extraction. |
| `/icd10-codes:clinical-trial-protocol-skill` | kỹ năng | [Nghiên cứu] Sinh đề cương thử nghiệm lâm sàng cho thuốc hoặc thiết bị y tế. Với đề tài của bác sĩ nên đi qua agent `dieu-phoi-nghien-cuu` để có cổng G0–G10. Từ khoá: trial protocol. |
| `/icd10-codes:contracts` | kỹ năng | [Pháp lý] Trả lời câu hỏi xuyên suốt một kho hợp đồng, có trích dẫn vị trí. Từ khoá: contract corpus. |
| `/icd10-codes:doc-extract` | kỹ năng | [Tài liệu] Rút văn bản thuần từ file PDF, DOCX, XLSX, PPTX. Từ khoá: document extraction. |
| `/icd10-codes:fhir` | kỹ năng | [Y khoa] Kết nối tới máy chủ FHIR R4 của bệnh viện (Epic, Oracle Health/Cerner) để đọc dữ liệu bệnh án điện tử. Từ khoá: FHIR R4, EHR. |
| `/icd10-codes:fhir-developer-skill` | kỹ năng | [Y khoa] Hướng dẫn lập trình API FHIR khi tự xây điểm cuối cho hệ thống y tế. Từ khoá: FHIR development. |
| `/icd10-codes:fraud-detection` | kỹ năng | [Y khoa — hệ Mỹ] Sàng kho hồ sơ thanh toán Medicare/Medicaid tìm gian lận và lãng phí. Từ khoá: claims fraud. |
| `/icd10-codes:icd10-cm-skill` | kỹ năng | [Y khoa] Rút mã chẩn đoán ICD-10-CM dùng để thanh toán từ một bệnh án. Xem thêm lệnh `/tra-ma-icd10`. Từ khoá: ICD-10-CM. |
| `/icd10-codes:prior-auth-review-skill` | kỹ năng | [Y khoa — hệ Mỹ] Tự động hoá việc xét duyệt yêu cầu chấp thuận trước của hãng bảo hiểm. Ít dùng ở Việt Nam. Từ khoá: prior authorization. |
| `/icd10-codes:procedure-coding` | kỹ năng | [Y khoa] Gán mã thủ thuật CPT và HCPCS cấp II từ hồ sơ lâm sàng. Đây là bộ mã của Mỹ, khác quy định Việt Nam. Từ khoá: CPT, HCPCS. |
| `/icd10-codes:verify` | kỹ năng | [Hỗ trợ] Kiểm tra thay đổi đối với script cài đặt quản trị. Từ khoá: verify install. |

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

### scientific-problem-selection  (6)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `/scientific-problem-selection:clinical-trial-protocol-skill` | kỹ năng | [Nghiên cứu] Sinh đề cương thử nghiệm lâm sàng cho thuốc hoặc thiết bị y tế. Với đề tài của bác sĩ nên đi qua agent `dieu-phoi-nghien-cuu` để có cổng G0–G10. Từ khoá: trial protocol. |
| `/scientific-problem-selection:instrument-data-to-allotrope` | kỹ năng | [Tin sinh học] Chuyển dữ liệu máy xét nghiệm (PDF, CSV, Excel) sang chuẩn Allotrope. Từ khoá: Allotrope. |
| `/scientific-problem-selection:nextflow-development` | kỹ năng | [Tin sinh học] Chạy các đường ống phân tích nf-core (rnaseq, sarek, atacseq) bằng Nextflow. Từ khoá: Nextflow, nf-core. |
| `/scientific-problem-selection:scientific-problem-selection` | kỹ năng | [Nghiên cứu] Giúp nhà khoa học chọn vấn đề nghiên cứu đáng làm. Từ khoá: problem selection. |
| `/scientific-problem-selection:scvi-tools` | kỹ năng | [Tế bào đơn] Phân tích RNA tế bào đơn bằng học sâu với scvi-tools. Dùng khi cần hiệu chỉnh lô hoặc chuyển nhãn tế bào. Từ khoá: scvi-tools. |
| `/scientific-problem-selection:single-cell-rna-qc` | kỹ năng | [Tin sinh học] Kiểm chất lượng dữ liệu RNA tế bào đơn (file .h5ad). Từ khoá: single-cell QC. |

### clinical-trial-protocol  (6)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `/clinical-trial-protocol:clinical-trial-protocol-skill` | kỹ năng | [Nghiên cứu] Sinh đề cương thử nghiệm lâm sàng cho thuốc hoặc thiết bị y tế. Với đề tài của bác sĩ nên đi qua agent `dieu-phoi-nghien-cuu` để có cổng G0–G10. Từ khoá: trial protocol. |
| `/clinical-trial-protocol:instrument-data-to-allotrope` | kỹ năng | [Tin sinh học] Chuyển dữ liệu máy xét nghiệm (PDF, CSV, Excel) sang chuẩn Allotrope. Từ khoá: Allotrope. |
| `/clinical-trial-protocol:nextflow-development` | kỹ năng | [Tin sinh học] Chạy các đường ống phân tích nf-core (rnaseq, sarek, atacseq) bằng Nextflow. Từ khoá: Nextflow, nf-core. |
| `/clinical-trial-protocol:scientific-problem-selection` | kỹ năng | [Nghiên cứu] Giúp nhà khoa học chọn vấn đề nghiên cứu đáng làm. Từ khoá: problem selection. |
| `/clinical-trial-protocol:scvi-tools` | kỹ năng | [Tế bào đơn] Phân tích RNA tế bào đơn bằng học sâu với scvi-tools. Dùng khi cần hiệu chỉnh lô hoặc chuyển nhãn tế bào. Từ khoá: scvi-tools. |
| `/clinical-trial-protocol:single-cell-rna-qc` | kỹ năng | [Tin sinh học] Kiểm chất lượng dữ liệu RNA tế bào đơn (file .h5ad). Từ khoá: single-cell QC. |

### desktop-commander  (6)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `/desktop-commander:ai-tools-setup` | kỹ năng | [Máy tính] Cài, nối, kiểm và sửa Claude Desktop cùng các máy chủ MCP. Từ khoá: MCP setup. |
| `/desktop-commander:computer-health-check` | kỹ năng | [Máy tính] Kiểm tra sức khoẻ máy tính, CHỈ ĐỌC, không thay đổi gì. Từ khoá: health check. |
| `/desktop-commander:desktop-commander-overview` | kỹ năng | [Máy tính] Tổng quan năng lực Desktop Commander: phiên dòng lệnh lâu dài, thao tác file. Từ khoá: Desktop Commander. |
| `/desktop-commander:knowledge-base` | kỹ năng | [Máy tính] Tạo và duy trì kho tri thức dạng Markdown cho mọi trợ lý AI dùng chung. Từ khoá: knowledge base. |
| `/desktop-commander:obsidian-vault` | kỹ năng | [Máy tính] Sắp xếp kho Obsidian: bản đồ nội dung, liên kết wiki, frontmatter. Từ khoá: Obsidian. |
| `/desktop-commander:terminal` | kỹ năng | [Máy tính] Dùng Desktop Commander cho công việc dòng lệnh. Từ khoá: terminal. |

### pdf-viewer  (5)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `/annotate` | lệnh | [Tài liệu] Chú thích PDF cùng nhau — đề xuất đánh dấu, cùng xem lại và chỉnh dần. Từ khoá: annotate PDF. |
| `/fill-form` | lệnh | [Tài liệu] Điền biểu mẫu PDF với xem trước trực tiếp từng ô. Từ khoá: fill PDF form. |
| `/open` | lệnh | [Tài liệu] Mở một file PDF trong trình xem tương tác. Từ khoá: open PDF. |
| `/sign` | lệnh | [Tài liệu] Đặt chữ ký hoặc chữ viết tắt lên file PDF. LƯU Ý: chỉ chèn hình ảnh chữ ký sẵn có, không thay việc bác sĩ tự ký văn bản pháp lý. Từ khoá: sign PDF. |
| `/pdf-viewer:view-pdf` | kỹ năng | [Tài liệu] Trình xem PDF tương tác — mở và xem tài liệu ngay trong phiên. Từ khoá: PDF viewer. |

### claude-tag-troubleshoot  (3)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `/debug-plugins` | lệnh | [Hỗ trợ] Chẩn đoán vì sao một plugin hoặc skill không hoạt động như mong đợi. Từ khoá: plugin debug. |
| `/claude-tag-troubleshoot:config-guide` | kỹ năng | [Hỗ trợ] Tài liệu tra cứu cách cấu hình các agent @Claude. Từ khoá: config guide. |
| `/claude-tag-troubleshoot:debug-plugins` | kỹ năng | [Hỗ trợ] Chẩn đoán vì sao một plugin hoặc skill không hoạt động như mong đợi. Từ khoá: plugin debug. |

### humanizer  (1)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `/humanizer:humanizer` | kỹ năng | [Viết lách] Xoá dấu vết văn phong máy trong một đoạn văn bản. Dùng khi biên tập bài viết cho tự nhiên hơn. Từ khoá: humanizer, AI-generated writing. |

### google-drive  (1)

| Gọi bằng | Loại | Làm gì |
|---|---|---|
| `/google-drive:google-drive-api` | kỹ năng | [Kết nối] Tìm, đọc, tạo, cập nhật và chia sẻ file trên Google Drive. Từ khoá: Google Drive. |

---

## TẦNG 3 — Ngoài chuyên môn (biết là có, hiếm khi dùng)  (0 mục)

