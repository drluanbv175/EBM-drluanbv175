# Danh mục công cụ gọi được trong Claude Code

> Sinh tự động bằng `tools/vietnamize/build_danh_muc.py`. KHÔNG sửa tay — chạy lại script sau mỗi lần cập nhật plugin.


**Tổng cộng 594 mục.** Cách gọi: gõ `/` rồi tên lệnh, hoặc nói thẳng nhu cầu để hệ thống tự chọn.


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
| Kiểm bản thảo theo chuẩn báo cáo (47 chuẩn) | `/medsci-review:check-reporting` |
| Chọn tạp chí để nộp bài | `/medsci-submission:find-journal` |
| Viết thư phản hồi phản biện | `/medsci-submission:revise` |
| Khử định danh dữ liệu nghiên cứu | `/medsci-data:deidentify` hoặc `/khu-dinh-danh` |
| Làm sạch và khảo sát bộ dữ liệu | `/medsci-data:clean-data` · `/medsci-data:generate-codebook` |
| Tổng quan hệ thống / phân tích gộp | `/medsci-analysis:meta-analysis` |
| Vẽ hình đạt chuẩn đăng bài | `/medsci-presentation:make-figures` |
| Gọt tiếng Anh học thuật trước khi nộp | `/medsci-writing:polish-language` |
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
| `/schedule` — Đặt lịch chạy tự động | Tạo tác vụ chạy theo lịch trên máy chủ (theo giờ, theo ngày trong tuần), hoặc hẹn chạy một lần vào thời điểm định trước. | Khi muốn một việc tự chạy định kỳ mà không cần bác sĩ mở máy — ví dụ quét cập nhật guideline hằng tuần. | Hệ EBM của bác sĩ đã có lịch riêng bằng scheduled-tasks Claude (thu-thap-tuan-an-toan-thuoc, cap-nhat-thang-ebm, goi-duyet-tuan-ebm... — thay launchd đã tắt từ 15/08/2026) — đừng đặt trùng hai nơi. |
| `/security-review` — Rà soát an toàn bảo mật | Soi phần mã đã thay đổi theo góc bảo mật: lộ khoá hay mật khẩu, dữ liệu người dùng đi ra ngoài, kiểm tra đầu vào lỏng lẻo, phân quyền sai. | Trước khi phát hành thay đổi có đụng tới dữ liệu nhạy cảm. | Rất đáng chạy với mọi thay đổi trong hệ EBM có chạm tới dữ liệu bệnh nhân hoặc khoá ký cổng. |
| `/simplify` — Rà gọn phần mã vừa sửa | Soi lại đoạn mã vừa thay đổi để tìm chỗ trùng lặp, chỗ viết vòng vo, chỗ đặt sai tầng — rồi sửa gọn lại. | Sau khi vừa viết xong một tính năng, muốn dọn trước khi chốt. | CHỈ lo chất lượng cách viết, KHÔNG đi tìm lỗi sai. Muốn tìm lỗi thì dùng `review`. |
| `/update-config` — Sửa cấu hình Claude Code | Sửa file settings.json: cấp quyền chạy lệnh, đặt biến môi trường, và quan trọng nhất là cài HOOK — cơ chế để hệ thống TỰ LÀM một việc mỗi khi xảy ra sự kiện nào đó. | Khi bác sĩ muốn 'từ nay mỗi lần X thì tự động làm Y', hoặc muốn bớt bị hỏi xin phép cho một loại lệnh. | Yêu cầu kiểu 'mỗi lần... thì tự động...' BẮT BUỘC phải qua hook — ghi vào bộ nhớ hay CLAUDE.md đều không làm được, vì đó là việc của phần mềm chứ không phải của trợ lý. |

---

## TẦNG 1 — Y khoa, nghiên cứu, tài liệu (dùng thường xuyên)  (499 mục)


### anthropic-skills  (94)

| Gọi bằng | Loại | Máy | Làm gì |
|---|---|---|---|
| `/anthropic-skills:EBM-MASTER` | kỹ năng | Mac | Nền tảng Y HỌC BẰNG CHỨNG hợp nhất của bác sĩ: lâm sàng, nghiên cứu, thống kê, giám sát guideline, an toàn thuốc, quản lý kháng sinh. Dùng khi cần cửa vào chung cho công việc EBM. Từ khoá: EBM platform. |
| `/anthropic-skills:algorithmic-art` | kỹ năng | Mac | Tạo tranh thuật toán bằng p5.js với yếu tố ngẫu nhiên có hạt giống và tham số điều chỉnh được. Dùng cho minh hoạ sáng tạo, không phải biểu đồ dữ liệu. Từ khoá: algorithmic art, p5.js. |
| `/anthropic-skills:alphafold2` | kỹ năng | Mac | [Sinh học cấu trúc] Dự đoán cấu trúc protein đơn phân và đa phân bằng AlphaFold2. Dùng cho nghiên cứu tiền lâm sàng, KHÔNG dùng cho chăm sóc bệnh nhân. Từ khoá: AlphaFold2. |
| `/anthropic-skills:antifacts` | kỹ năng | Mac | Dùng khi bác sĩ muốn MỞ hoặc CẬP NHẬT \"Antifacts\" — Trung tâm EBM theo chuyên khoa (gom cập nhật chứng cứ + 45 thang điểm lâm sàng + công cụ nghiên cứu theo chuyên khoa). Kích hoạt khi nghe \"Antifacts\", \"mở Antifacts\", \"cập nhật A… |
| `/anthropic-skills:boltz` | kỹ năng | Mac | [Sinh học cấu trúc] Dự đoán cấu trúc phức hợp protein – acid nucleic – phân tử nhỏ bằng Boltz-2. Dùng cho nghiên cứu tiền lâm sàng. Từ khoá: Boltz-2. |
| `/anthropic-skills:borzoi` | kỹ năng | Mac | [Tin sinh học] Dự đoán tín hiệu chức năng toàn hệ gen (RNA-seq, CAGE, DNase, ChIP) từ chuỗi DNA bằng Borzoi. Dùng trong nghiên cứu hệ gen. Từ khoá: Borzoi, functional genomics. |
| `/anthropic-skills:brand-guidelines` | kỹ năng | Mac | Áp bộ màu và kiểu chữ chính thức của Anthropic. Dùng khi làm sản phẩm cần đúng nhận diện thương hiệu đó; ít dùng cho tài liệu y khoa. Từ khoá: brand guidelines. |
| `/anthropic-skills:canvas-design` | kỹ năng | Mac | Tạo ẤN PHẨM HÌNH ẢNH đẹp dạng .png/.pdf theo nguyên tắc thiết kế (poster, tờ rơi, thiệp). Dùng khi cần sản phẩm in được. Từ khoá: canvas design, poster. |
| `/anthropic-skills:cap-nhat-chung-cu-y-khoa` | kỹ năng | Mac | Sử dụng skill này khi bác sĩ yêu cầu cập nhật chứng cứ hoặc khuyến cáo hiện hành cho MỘT vấn đề lâm sàng cụ thể. Mỗi cập nhật phải kèm Web Dashboard độc lập theo mô hình MẶC ĐỊNH \"Evidence Workbench\" (bố cục 3 cột: bộ lọc · bảng điểm c… |
| `/anthropic-skills:chai1` | kỹ năng | Mac | [Sinh học cấu trúc] Dự đoán cấu trúc phức hợp bằng mô hình nền Chai-1. Dùng cho nghiên cứu tiền lâm sàng. Từ khoá: Chai-1. |
| `/anthropic-skills:citation-management` | kỹ năng | Mac | Quản lý & kiểm chứng trích dẫn học thuật — phân giải PMID/DOI bắt buộc qua API miễn phí (PubMed/Crossref), đối chiếu metadata, bắt trích dẫn ma & citation washing, cảnh báo retracted/trùng, xuất danh mục Vancouver/ICMJE/AMA/BibTeX. Dùng … |
| `/anthropic-skills:clinical-decision-support` | kỹ năng | Mac | Tạo tài liệu hỗ trợ quyết định lâm sàng (CDS): phân tích nhóm bệnh nhân (cohort) theo dấu ấn sinh học, báo cáo khuyến cáo điều trị dựa trên bằng chứng kèm thuật toán quyết định và phân độ GRADE; phân tích thống kê (HR, đường sống còn); x… |
| `/anthropic-skills:clinical-evidence-rag` | kỹ năng | Mac | Cầu nối kiến thức–thực hành: trả lời câu hỏi lâm sàng bằng cách truy xuất (RAG) từ kho y văn do bác sĩ tự nạp. Dùng khi muốn tra trong kho tài liệu riêng thay vì tìm mới trên mạng. Từ khoá: clinical RAG. |
| `/anthropic-skills:clinical-reports` | kỹ năng | Mac | Viết báo cáo lâm sàng: case report (chuẩn CARE), báo cáo chẩn đoán (X-quang/giải phẫu bệnh/xét nghiệm), báo cáo thử nghiệm lâm sàng (ICH-E3) và hồ sơ bệnh án (SOAP, H&P, tóm tắt xuất viện). Kèm template và công cụ kiểm tra. Mọi đầu ra kè… |
| `/anthropic-skills:compute-env-setup` | kỹ năng | Mac | Cài môi trường tính toán trên máy chủ từ xa (SSH/conda, cụm Slurm) để chạy việc nặng. Dùng khi máy cá nhân không đủ sức. Từ khoá: compute environment. |
| `/anthropic-skills:consolidate-memory` | kỹ năng | Mac | [Bộ nhớ] Rà lại toàn bộ file bộ nhớ của Claude: gộp mục trùng, sửa thông tin đã lỗi thời, tỉa bớt chỉ mục cho gọn. Dùng khi bộ nhớ phình to, có hai mục nói ngược nhau, hoặc trước khi bàn giao sang máy khác. Từ khoá: consolidate memory, m… |
| `/anthropic-skills:customize` | kỹ năng | Mac | Tạo và bảo trì hồ sơ agent riêng, và soạn skill mới qua công cụ repl. Dùng khi muốn tuỳ biến cách trợ lý làm việc. Từ khoá: customize agent profile. |
| `/anthropic-skills:dao-tao-slide-tai-lieu-y-khoa` | kỹ năng | Mac | Tạo và chuẩn hóa sản phẩm đào tạo y khoa và tài liệu chuyên môn — bài giảng, slide PowerPoint (.pptx), tài liệu Word (.docx), PDF, infographic/poster, bảng tóm tắt, bảng quyết định, thuật toán lâm sàng (Mermaid), checklist cờ đỏ, bảng th… |
| `/anthropic-skills:dark-analyst` | kỹ năng | Mac | Sử dụng skill này khi bác sĩ yêu cầu cập nhật chứng cứ hoặc khuyến cáo hiện hành cho MỘT vấn đề lâm sàng cụ thể. Mỗi cập nhật phải kèm Web Dashboard độc lập theo mô hình MẶC ĐỊNH \"Evidence Workbench\" (bố cục 3 cột: bộ lọc · bảng điểm c… |
| `/anthropic-skills:dashboard-master-ebm-ngoai-tru` | kỹ năng | Mac | Tạo, cập nhật hoặc kiểm định Dashboard Master EBM ngoại trú và các sổ Change Log, Evidence Register, Medication Safety, Action Register; xác minh nguồn, loại trùng, lập báo cáo điều hành tháng. |
| `/anthropic-skills:database-lookup` | kỹ năng | Mac | Truy vấn 78+ CƠ SỞ DỮ LIỆU khoa học/y khoa công khai qua API đã tài liệu hóa rõ endpoint, bộ lọc, phân trang và nguồn gốc dữ liệu (PubChem, ChEMBL, UniProt, ClinicalTrials.gov, FDA, dbSNP, ClinVar, COSMIC, GWAS Catalog, OMIM... phần lớn … |
| `/anthropic-skills:dieu-phoi-aipoch` | kỹ năng | Mac | Định tuyến yêu cầu nghiên cứu/lâm sàng tới đúng skill trong 605 skill của plugin aipoch-medical-research, theo 35 nhóm chuyên môn. Dùng khi bác sĩ mô tả một việc nhưng KHÔNG biết tên skill cụ thể trong bộ aipoch. |
| `/anthropic-skills:diffdock` | kỹ năng | Mac | [Sinh học cấu trúc] Dự đoán tư thế gắn của phân tử nhỏ vào protein bằng DiffDock-L. Dùng khi sàng lọc thuốc tiền lâm sàng. Từ khoá: DiffDock. |
| `/anthropic-skills:doc-coauthoring` | kỹ năng | Mac | Đồng soạn tài liệu theo quy trình có cấu trúc (tài liệu kỹ thuật, đề xuất, hướng dẫn). Dùng khi viết tài liệu dài cần thống nhất bố cục. Từ khoá: doc co-authoring. |
| `/anthropic-skills:docs` | kỹ năng | Mac | docs (editable docs people share and comment on; the default for any document, named as a doc or not: a document, report, proposal, resume, cover letter, letter, contract, policy, form, template, worksheet, essay, handbook, guide, how-to… |
| `/anthropic-skills:docx` | kỹ năng | Mac | [Tài liệu] Tạo, đọc và sửa file Word (.docx) cùng mẫu Word (.dotx): mục lục, đề mục, số trang, tiêu đề thư, bảng, chèn hoặc thay ảnh, tìm-thay hàng loạt, theo dõi thay đổi. Dùng khi bác sĩ nhắc tới file Word, .docx, .dotx, hoặc cần xuất … |
| `/anthropic-skills:ehospital-mini` | kỹ năng | Mac | Soạn LỜI DẶN & NHẮC TÁI KHÁM ngoại trú cho bệnh nhân — mẫu in (A5/A4), mốc tái khám, cách dùng thuốc gọn, tiêu chí QUAY LẠI NGAY/đi cấp cứu (safety-netting), kế hoạch tuân thủ. Dùng khi cần phát tay tờ dặn dò sau khám. KHÔNG bịa tích hợp… |
| `/anthropic-skills:esmfold2` | kỹ năng | Mac | [Sinh học cấu trúc] Gấp cuộn toàn nguyên tử bằng ESMFold2, chạy được từ một chuỗi đơn. Dùng cho nghiên cứu tiền lâm sàng. Từ khoá: ESMFold2. |
| `/anthropic-skills:evo2` | kỹ năng | Mac | [Tin sinh học] Chấm điểm, biểu diễn và sinh chuỗi DNA bằng mô hình nền Evo 2 ngữ cảnh dài. Dùng trong nghiên cứu hệ gen. Từ khoá: Evo 2, genomic foundation model. |
| `/anthropic-skills:experimental-design` | kỹ năng | Mac | Thiết kế thí nghiệm/nghiên cứu TRƯỚC khi thu thập dữ liệu — chọn thiết kế, ngẫu nhiên hóa (randomization), phân khối (blocking/stratification), bố trí factorial/fractional-factorial, crossover, split-plot, Latin square, kiểm soát hiệu ứn… |
| `/anthropic-skills:explain-usage` | kỹ năng | Mac | [Tiện ích] Giải thích phiên làm việc này đã tiêu token vào đâu, kèm MỘT biểu đồ đơn giản và lời văn dễ hiểu. Dùng khi bác sĩ hỏi «token đi đâu hết», «giải thích mức dùng», hoặc muốn xem bảng bóc tách chi phí của phiên. Từ khoá: usage, to… |
| `/anthropic-skills:exploratory-data-analysis` | kỹ năng | Mac | Khảo sát nhanh cấu trúc, chất lượng và đặc điểm của MỘT file dữ liệu khoa học (200+ định dạng: bảng tính, gen học, hóa học, ảnh vi mô, phổ, proteomics...) — tự nhận diện định dạng, sinh báo cáo markdown về chất lượng dữ liệu và gợi ý bướ… |
| `/anthropic-skills:fair-esm2` | kỹ năng | Mac | [Tin sinh học] Sinh vector biểu diễn (embedding) cho protein bằng ESM-2 của Meta AI. Dùng khi phân tích chuỗi protein bằng học máy. Từ khoá: ESM-2, protein embedding. |
| `/anthropic-skills:figure-composer` | kỹ năng | Mac | Dựng MỘT hình nhiều panel đạt chuẩn công bố, từ một câu khẳng định + dữ liệu nguồn. Dùng khi cần hình chính cho bài báo. Từ khoá: multi-panel figure. |
| `/anthropic-skills:figure-style` | kỹ năng | Mac | Quy tắc trình bày hình đạt chuẩn công bố (độ đọc được, nhãn, đơn vị, màu). Dùng cho hình NỘP BÀI, không cần cho biểu đồ xem nhanh. Từ khoá: figure style, publication-grade. |
| `/anthropic-skills:giao-tiep-quyet-dinh-soap` | kỹ năng | Mac | Sử dụng skill này khi cần kỹ năng GIAO TIẾP với bệnh nhân, RA QUYẾT ĐỊNH CÙNG BỆNH NHÂN (shared decision-making), báo tin xấu, hoặc GHI HỒ SƠ SOAP. Kích hoạt với "giải thích cho bệnh nhân thế nào", "bệnh nhân không chịu điều trị/lưỡng lự… |
| `/anthropic-skills:google-workspace` | kỹ năng | Mac | Read this before the first Google Drive, Docs, Sheets or Slides connector call whenever the task creates or changes a Google file. Use this skill whenever the user wants to create or change a Google Doc, Sheet or Slides file in their Goo… |
| `/anthropic-skills:hypothesis-generation` | kỹ năng | Mac | Hình thức hóa GIẢ THUYẾT khoa học từ quan sát/dữ liệu — sinh 3-5 giả thuyết CẠNH TRANH kèm CƠ CHẾ, chấm chất lượng theo 7 tiêu chí (khả kiểm định, khả bác bỏ theo Popper, tính đơn giản, sức giải thích, phạm vi, nhất quán, tính mới), rồi … |
| `/anthropic-skills:import-memory` | kỹ năng | Mac | [Bộ nhớ] Nhập bản xuất bộ nhớ từ một trợ lý AI khác vào bộ nhớ của Claude — theo lối trò chuyện, CHỈ THÊM chứ không đè, và coi nội dung nhập vào là DỮ LIỆU chứ không phải chỉ thị. Dùng khi chuyển từ trợ lý khác sang. Từ khoá: import memo… |
| `/anthropic-skills:indication-dossier` | kỹ năng | Mac | Soạn HỒ SƠ CHỈ ĐỊNH ĐIỀU TRỊ: quần thể bệnh nhân, dịch tễ, sinh bệnh học, chuẩn điều trị hiện hành, bối cảnh pháp quy. Dùng cho tổng quan chuyên sâu một chỉ định. Từ khoá: indication dossier. |
| `/anthropic-skills:internal-comms` | kỹ năng | Mac | Viết các loại THÔNG BÁO NỘI BỘ theo mẫu quen dùng của đơn vị. Dùng cho thư gửi khoa/phòng, thông báo thay đổi quy trình. Từ khoá: internal communications. |
| `/anthropic-skills:ke-don-an-toan-benh-man` | kỹ năng | Mac | Sử dụng skill này khi cần KÊ ĐƠN / RÀ ĐƠN AN TOÀN cho bệnh nhân bệnh mạn ngoại trú (mọi lứa tuổi, không chỉ người cao tuổi). Kích hoạt với \"đơn này có an toàn không\", \"thuốc có đánh nhau không/tương tác\", \"hiệu chỉnh liều theo thận/… |
| `/anthropic-skills:kham-ngoai-tru-ebm` | kỹ năng | Mac | Sử dụng skill này khi bác sĩ cần tiếp cận hoặc ra quyết định cho MỘT ca khám ngoại trú theo Y học chứng cứ (EBM). Dẫn dắt trọn 5 bước tại phòng khám: đặt câu hỏi lâm sàng (PICO) · hỏi–khám có trọng điểm + sàng lọc cờ đỏ · chẩn đoán phân … |
| `/anthropic-skills:learn` | kỹ năng | Mac | Giải thích để HIỂU BẢN CHẤT một vấn đề (vì sao, cơ chế thế nào) thay vì làm hộ một việc. Dùng khi bác sĩ muốn học chứ không muốn nhận kết quả. Từ khoá: learn, understanding. |
| `/anthropic-skills:ligandmpnn` | kỹ năng | Mac | [Thiết kế protein] Suy ngược chuỗi có tính tới phối tử, acid nucleic và ion kim loại. Dùng cho nghiên cứu tiền lâm sàng. Từ khoá: LigandMPNN. |
| `/anthropic-skills:literature-review` | kỹ năng | Mac | Tìm, XÁC MINH và tổng hợp y văn — từ 'bài kinh điển của chủ đề X là bài nào' cho tới tổng quan đa nguồn đầy đủ. Dùng khi cần rà y văn có kiểm chứng nguồn. Từ khoá: literature review. |
| `/anthropic-skills:managed-model-endpoints` | kỹ năng | Mac | Đăng ký một dịch vụ mô hình (cục bộ hoặc từ xa) để hệ thống tự bật/tắt khi cần. Dùng khi muốn chạy mô hình riêng ngoài Claude. Từ khoá: model endpoint. |
| `/anthropic-skills:mcp-builder` | kỹ năng | Mac | Hướng dẫn dựng máy chủ MCP chất lượng tốt để mô hình gọi được dịch vụ bên ngoài. Dùng khi muốn nối một nguồn dữ liệu mới vào Claude. Từ khoá: MCP server builder. |
| `/anthropic-skills:morning` | kỹ năng | Mac | Dựng BẢN TIN BUỔI SÁNG dạng trang HTML, hoặc đặt lịch chạy tự động các ngày trong tuần. Dùng khi bác sĩ yêu cầu rõ — không tự chạy. Từ khoá: morning brief. |
| `/anthropic-skills:nghien-cuu-ebm-tong-hop` | kỹ năng | Mac | >- Trợ lý NGHIÊN CỨU Y KHOA & Y HỌC CHỨNG CỨ (EBM) hợp nhất cho bác sĩ lâm sàng. Gồm 5 mô-đun: (1) Tìm & thu thập y văn; (2) Đọc & thẩm định chứng cứ; (3) Thiết kế nghiên cứu lâm sàng; (4) Thống kê & mô hình lâm sàng; (5) Viết & nộp bản … |
| `/anthropic-skills:nghien-cuu-y-khoa-chuan-quoc-te` | kỹ năng | Mac | Thực hiện, thiết kế và rà soát nghiên cứu y khoa theo chuẩn quốc tế qua cổng chất lượng G0-G9. Dùng skill này khi người dùng cần xác định câu hỏi/đề cương/protocol, hồ sơ đạo đức và đăng ký nghiên cứu, tính cỡ mẫu, thiết kế biến số/CRF/p… |
| `/anthropic-skills:nguoi-cao-tuoi-da-benh-da-thuoc` | kỹ năng | Mac | Chăm sóc toàn diện người cao tuổi suy yếu, đa bệnh lý và đa thuốc theo hướng an toàn thuốc, giảm hại và tránh điều trị quá mức. Dùng skill này bất cứ khi nào có bệnh nhân lớn tuổi kèm nhiều thuốc hoặc nhiều bệnh đồng mắc — rà soát và đối… |
| `/anthropic-skills:openfold3` | kỹ năng | Mac | [Sinh học cấu trúc] Dự đoán cấu trúc bằng OpenFold3 — bản mã nguồn mở của AlphaFold3. Dùng cho nghiên cứu tiền lâm sàng. Từ khoá: OpenFold3. |
| `/anthropic-skills:paper-lookup` | kỹ năng | Mac | Tra cứu bài báo y khoa qua API MIỄN PHÍ (PubMed E-utilities, Crossref, Europe PMC) — tìm theo PICO/từ khóa/MeSH, phân giải và xác minh PMID/DOI, lấy metadata gốc. Dùng khi cần tìm bài cho một câu hỏi, kiểm một PMID/DOI có thật, hoặc lấy … |
| `/anthropic-skills:paper-narrative` | kỹ năng | Mac | Chấm và sắp lại MẠCH TRUYỆN mà bộ hình trong bài báo đang kể — đầu vào là chính bản thảo + bộ hình. Dùng khi bài đủ dữ liệu nhưng đọc rời rạc. Từ khoá: paper narrative, figure story. |
| `/anthropic-skills:pdf` | kỹ năng | Mac | [Tài liệu] Mọi việc với file PDF: đọc và bóc chữ hay bảng, gộp, tách, xoay trang, đóng dấu chìm, tạo PDF mới, điền biểu mẫu, mã hoá và giải mã, bóc ảnh, OCR bản scan cho tra được chữ. Dùng khi bác sĩ nhắc tới một file .pdf hoặc muốn xuất… |
| `/anthropic-skills:pdf-explore` | kỹ năng | Mac | Đọc sâu tài liệu PDF dài (bài báo, báo cáo) khi câu trả lời nằm rải ở nhiều chỗ trong file. Dùng khi bác sĩ đính kèm PDF và cần tổng hợp xuyên suốt, không chỉ tra một đoạn. Từ khoá: PDF exploration. |
| `/anthropic-skills:peer-review` | kỹ năng | Mac | Bình duyệt bản thảo khoa học có CẤU TRÚC — đánh giá tính hợp lệ (validity), phương pháp, thống kê, đạo đức/đăng ký, trình bày & chuẩn báo cáo, trích dẫn; soạn nhận xét đối kháng đa lăng kính + thư phản biện cho tác giả. Dùng trước khi nộ… |
| `/anthropic-skills:plugin-router-chatgpt` | kỹ năng | Mac | Điều phối yêu cầu rộng, mơ hồ hoặc nhiều bước tới đúng nhạc trưởng, plugin và skill trong hệ Claude–Codex–ChatGPT. Dùng khi cần tự chọn công cụ, phối hợp nhiều chuyên môn hoặc kiểm tra ai là owner; không thay một skill chuyên biệt đã đượ… |
| `/anthropic-skills:pptx` | kỹ năng | Mac | [Trình bày] Làm việc với file PowerPoint (.pptx, .potx): dựng bộ slide, bóc chữ từ slide có sẵn, sửa bài trình bày, gộp hoặc tách file, xử lý mẫu, bố cục, ghi chú người trình bày và bình luận. Dùng bất cứ khi nào có .pptx/.potx ở đầu vào… |
| `/anthropic-skills:product-self-knowledge` | kỹ năng | Mac | Tra thông tin CHÍNH XÁC về sản phẩm của Anthropic (Claude Code, gói dịch vụ, giới hạn). Dùng BẮT BUỘC trước khi khẳng định điều gì về sản phẩm, tránh nói theo trí nhớ. Từ khoá: product facts. |
| `/anthropic-skills:proteinmpnn` | kỹ năng | Mac | [Thiết kế protein] Suy ngược chuỗi acid amin từ khung cấu trúc bằng ProteinMPNN. Dùng cho nghiên cứu tiền lâm sàng. Từ khoá: ProteinMPNN. |
| `/anthropic-skills:pyhealth` | kỹ năng | Mac | Xây dựng pipeline học máy lâm sàng bằng thư viện PyHealth: tải dữ liệu EHR (MIMIC-III/IV, eICU, OMOP), định nghĩa tác vụ (tử vong, tái nhập viện, gợi ý thuốc, giai đoạn ngủ, mã hóa ICD), huấn luyện mô hình (Transformer, RETAIN, GAMENet, … |
| `/anthropic-skills:quan-ly-cap-nhat-ebm` | kỹ năng | Mac | Sử dụng skill này khi bác sĩ muốn QUẢN LÝ kho cập nhật EBM đã lưu (sổ cái EBM_MASTER) — xem tổng quan, tìm/lọc, duyệt và phê chuẩn các cập nhật. Kích hoạt với "quản lý EBM", "xem các cập nhật", "hàng đợi duyệt", "duyệt thẻ…", "thống kê s… |
| `/anthropic-skills:remote-compute-modal` | kỹ năng | Mac | Chạy việc cần GPU trên tài khoản Modal của bác sĩ. Dùng cho tác vụ học máy nặng. Từ khoá: Modal GPU. |
| `/anthropic-skills:remote-compute-ssh` | kỹ năng | Mac | Gửi việc tính toán lên máy chủ SSH/SLURM của bác sĩ rồi chờ và thu kết quả. Dùng sau khi đã quyết định chạy từ xa. Từ khoá: SSH, SLURM. |
| `/anthropic-skills:research-lookup` | kỹ năng | Mac | Tra cứu NGHIÊN CỨU & ĐĂNG KÝ THỬ NGHIỆM qua nguồn mở — ClinicalTrials.gov (API v2), WHO ICTRP, PROSPERO. Dùng khi cần kiểm một thử nghiệm đã đăng ký chưa, tìm nghiên cứu đang tiến hành/đã hoàn tất, đối chiếu kết cục đăng ký vs công bố (c… |
| `/anthropic-skills:scgpt` | kỹ năng | Mac | [Tế bào đơn] Biểu diễn và chú giải dữ liệu biểu hiện gen tế bào đơn bằng scGPT. Dùng khi phân tích dữ liệu tế bào đơn. Từ khoá: scGPT. |
| `/anthropic-skills:schedule` | kỹ năng | Mac | [Tiện ích] Tạo hoặc sửa TÁC VỤ CHẠY THEO LỊCH, tự nổ đúng giờ mà không cần ngồi chờ. Dùng khi bác sĩ nói «mỗi ngày», «mỗi sáng», «nhắc tôi sau một giờ», «chạy lúc 12 giờ trưa», hoặc muốn đổi giờ một tác vụ đã đặt. Từ khoá: schedule, sche… |
| `/anthropic-skills:scholar-evaluation` | kỹ năng | Mac | Chấm điểm ĐỊNH LƯỢNG chất lượng học thuật của bản thảo/đề cương/tổng quan theo khung ScholarEval — 8 chiều (đặt vấn đề, tổng quan y văn, phương pháp, thu thập dữ liệu, phân tích, kết quả, văn phong, trích dẫn), mỗi chiều chấm 0-5 có trọn… |
| `/anthropic-skills:scientific-critical-thinking` | kỹ năng | Mac | Khung THẨM ĐỊNH chất lượng chứng cứ và tính hợp lệ của thiết kế nghiên cứu — áp dụng GRADE, Cochrane Risk of Bias, nhận diện thiên kiến/nhiễu/ngụy biện logic và các lỗi thống kê thường gặp. Dùng để dạy hoặc tự kiểm tra tư duy phản biện k… |
| `/anthropic-skills:scientific-writing` | kỹ năng | Mac | Viết bản thảo khoa học y khoa theo cấu trúc IMRAD, văn xuôi liền mạch, khớp CHUẨN BÁO CÁO đúng thiết kế (CONSORT/STROBE/PRISMA/SPIRIT/STARD/TRIPOD+AI; COREQ/SRQR cho định tính; SQUIRE cho QI). Dùng khi cần viết bài báo, protocol, hoặc bá… |
| `/anthropic-skills:scikit-survival` | kỹ năng | Mac | Phân tích SỐNG CÒN / thời gian-đến-biến-cố (time-to-event) bằng scikit-survival: mô hình Cox, Random Survival Forest, Gradient Boosting, Survival SVM; xử lý dữ liệu KIỂM DUYỆT (censoring) và NGUY CƠ CẠNH TRANH (competing risks); đánh giá… |
| `/anthropic-skills:scvi-tools` | kỹ năng | Mac | [Tế bào đơn] Phân tích RNA-seq tế bào đơn theo mô hình xác suất với scvi-tools. Dùng khi cần hiệu chỉnh lô hoặc chuyển nhãn bán giám sát. Từ khoá: scvi-tools, scVI. |
| `/anthropic-skills:self-awareness` | kỹ năng | Mac | Truy vấn cơ sở dữ liệu phiên làm việc của Claude Science. Dùng khi cần tự kiểm phiên đang chạy gì. Từ khoá: session introspection. |
| `/anthropic-skills:setup-claude` | kỹ năng | Mac | Guided setup — install role-matched plugins, connect your tools, try a skill. |
| `/anthropic-skills:setup-cowork` | kỹ năng | Mac | [Hỗ trợ] Cài đặt Cowork có dẫn dắt từng bước: cài plugin hợp với vai trò, nối các công cụ đang dùng, chạy thử một skill cho quen. Dùng khi mới dựng máy hoặc mới bật Cowork lần đầu. Từ khoá: setup Cowork, cowork onboarding. |
| `/anthropic-skills:skill-creator` | kỹ năng | Mac | Tạo skill mới, sửa và cải thiện skill sẵn có, đo hiệu quả của skill. Dùng khi bác sĩ muốn tự đóng gói một quy trình thành skill gọi được. Từ khoá: skill creator. |
| `/anthropic-skills:slack-gif-creator` | kỹ năng | Mac | Tạo ảnh động GIF tối ưu cho Slack, kèm ràng buộc kích thước và công cụ kiểm tra. Dùng khi cần ảnh động cho tin nhắn nhóm. Từ khoá: Slack GIF. |
| `/anthropic-skills:solublempnn` | kỹ năng | Mac | [Thiết kế protein] Suy ngược chuỗi thiên về protein TAN được. Dùng cho nghiên cứu tiền lâm sàng. Từ khoá: SolubleMPNN. |
| `/anthropic-skills:statistical-analysis` | kỹ năng | Mac | Quy trình phân tích thống kê lâm sàng/nghiên cứu y khoa — mô tả dữ liệu, chọn kiểm định theo loại biến + thiết kế + giả định, hồi quy/sống còn/ROC/hiệu chỉnh, báo cáo ước lượng + 95% CI. Dùng khi cần chạy/đọc phân tích thống kê cho một đ… |
| `/anthropic-skills:statistical-power` | kỹ năng | Mac | Tính CỠ MẪU / LỰC THỐNG KÊ (power analysis) TRƯỚC khi thu thập dữ liệu — bằng công thức đóng (t-test, ANOVA, tỷ lệ, tương quan, chi-square, hồi quy) VÀ mô phỏng Monte Carlo cho thiết kế không có công thức chuẩn (hồi quy logistic/Poisson,… |
| `/anthropic-skills:statsmodels` | kỹ năng | Mac | Chạy mô hình thống kê THẬT bằng thư viện statsmodels: OLS, GLM, mô hình hỗn hợp (mixed-effects), ARIMA/chuỗi thời gian — kèm bảng hệ số, chẩn đoán giả định, phân tích residual. Dùng khi ĐÃ có dữ liệu và cần fit một mô hình cụ thể (khác s… |
| `/anthropic-skills:tao-video-tiktok` | kỹ năng | Mac | >- Tạo video TikTok dọc (9:16, 1080x1920) từ nội dung do người dùng cung cấp, có GIỌNG ĐỌC tiếng Việt mềm mại, ngắt nghỉ tự nhiên (edge-tts HoaiMy nữ / NamMinh nam, tự lùi về giọng macOS "Linh" khi mất mạng) và PHỤ ĐỀ ĐỘNG karaoke đồng b… |
| `/anthropic-skills:tham-dinh-chung-cu-grade-nnt` | kỹ năng | Mac | Sử dụng skill này khi cần THẨM ĐỊNH NHANH một bài báo/guideline/nghiên cứu để quyết định có đáng đổi thực hành không. Kích hoạt với "bài này có đáng tin không", "đọc giúp tôi nghiên cứu này", "NNT/NNH bao nhiêu", "nguy cơ sai lệch (risk … |
| `/anthropic-skills:theme-factory` | kỹ năng | Mac | Bộ chủ đề trình bày cho slide, tài liệu, báo cáo, trang HTML — có 10 chủ đề dựng sẵn. Dùng khi muốn thống nhất phong cách một bộ sản phẩm. Từ khoá: theme, styling. |
| `/anthropic-skills:tiep-can-chan-doan-co-do-chuyen-tuyen` | kỹ năng | Mac | Sử dụng skill này khi bác sĩ tiếp cận MỘT triệu chứng/hội chứng ngoại trú và cần đi từ triệu chứng → chẩn đoán phân biệt → CỜ ĐỎ bắt buộc loại trừ → ngưỡng chuyển tuyến/cấp cứu một cách AN TOÀN. Kích hoạt với \"bệnh nhân đau ngực/đau đầu… |
| `/anthropic-skills:tong-thuat-chung-cu` | kỹ năng | Mac | Bác sĩ hỏi MỘT chủ đề lâm sàng → trả MỘT bài tổng thuật học thuật liền mạch (kiểu Deep-Research) neo vào hạ tầng liêm chính — 4 làn nguồn song song, trích dẫn Vancouver đánh số qua cổng kiểm, trình bày chuẩn v11. Bác sĩ duyệt gói ① ngày … |
| `/anthropic-skills:treatment-plans` | kỹ năng | Mac | Soạn kế hoạch điều trị y khoa ngắn gọn (3-4 trang) xuất LaTeX/PDF cho nhiều chuyên khoa: nội khoa chung, phục hồi chức năng, sức khỏe tâm thần, quản lý bệnh mạn, chu phẫu, giảm đau. Dùng khung mục tiêu SMART, can thiệp dựa bằng chứng. Kè… |
| `/anthropic-skills:tuan-thu-dieu-tri` | kỹ năng | Mac | Sử dụng skill này khi cần đánh giá và cải thiện TUÂN THỦ ĐIỀU TRỊ (medication & treatment adherence) cho bệnh nhân ngoại trú. Kích hoạt khi bác sĩ nói \"bệnh nhân không tuân thủ\", \"hay quên uống thuốc\", \"bỏ thuốc/tự ngưng thuốc\", \"… |
| `/anthropic-skills:using-model-endpoint` | kỹ năng | Mac | Gọi một mô hình đã đăng ký qua HTTP API của nó. Dùng sau khi đã đăng ký endpoint. Từ khoá: call model endpoint. |
| `/anthropic-skills:venue-templates` | kỹ năng | Mac | Template LaTeX + yêu cầu định dạng cho các tạp chí/hội nghị khoa học lớn (Nature, Science, PLOS, Elsevier...), poster nghiên cứu, và đề cương xin tài trợ — kèm chuẩn báo cáo CONSORT/STROBE/PRISMA cho bài y khoa. Dùng khi chuẩn bị bản thả… |
| `/anthropic-skills:web-artifacts-builder` | kỹ năng | Mac | Bộ công cụ dựng trang HTML nhiều thành phần bằng React/Tailwind/shadcn cho artifact trên claude.ai. Dùng khi trang cần quản lý trạng thái, điều hướng hoặc thành phần shadcn — KHÔNG dùng cho artifact HTML/JSX đơn giản một file. Từ khoá: w… |
| `/anthropic-skills:xlsx` | kỹ năng | Mac | [Bảng tính] Làm việc với bảng tính (.xlsx, .xlsm, .xltx, .csv, .tsv): mở, đọc, sửa, thêm cột, tính công thức, định dạng, vẽ biểu đồ, dọn dữ liệu lộn xộn, dựng bảng mới hoặc đổi qua lại giữa các định dạng. Dùng khi bảng tính là đầu vào ha… |

### openmed-skills  (74)

| Gọi bằng | Loại | Máy | Làm gì |
|---|---|---|---|
| `/openmed-skills:annotating-variants` | kỹ năng | Mac | Chú giải biến thể di truyền trong file VCF và chuẩn hoá danh pháp HGVS bằng công cụ mở (Ensembl VEP, SnpEff, ANNOVAR). Dùng cho nghiên cứu di truyền. Từ khoá: VCF, HGVS, variant annotation. |
| `/openmed-skills:ask-openmed` | kỹ năng | Mac | Choose the first OpenMed workflow skill for an intake, privacy, extraction, exchange, or verification request using deterministic local routing. Use when a goal is broad, spans several clinical-data stages, or leaves the data-sensitivity… |
| `/openmed-skills:assembling-fhir-bundles` | kỹ năng | Mac | Gói nhiều tài nguyên FHIR R4 thành một transaction Bundle hợp lệ, sẵn sàng gửi vào bệnh án điện tử. Dùng ở bước cuối trước khi ghi vào hệ thống. Từ khoá: FHIR Bundle. |
| `/openmed-skills:auditing-deid-leakage` | kỹ năng | Mac | Rà ĐỐI KHÁNG văn bản ĐÃ khử định danh để tìm định danh còn sót, và CHẶN phát hành nếu còn dù một dấu vết. Dùng làm chốt kiểm CUỐI trước khi chia sẻ hay công bố dữ liệu. Từ khoá: leakage audit, residual PHI. |
| `/openmed-skills:auditing-deidentification-runs` | kỹ năng | Mac | Sinh vết kiểm toán có chữ ký, tái lập được và KHÔNG chứa PHI cho một lần chạy khử định danh. Dùng khi cần hồ sơ tuân thủ nộp cho hội đồng hoặc thanh tra. Từ khoá: audit trail, deidentify(audit=True). |
| `/openmed-skills:auditing-part11-trails` | kỹ năng | Mac | Sinh và kiểm vết kiểm toán kiểu 21 CFR Part 11 — ai, làm gì, lúc nào, chữ ký điện tử, chống sửa lén — cho môi trường GxP. Dùng khi đề tài chịu quản lý của cơ quan dược phẩm. Từ khoá: 21 CFR Part 11, GxP. |
| `/openmed-skills:auditing-safe-harbor-checklist` | kỹ năng | Mac | Đối chiếu kết quả khử định danh với đủ 18 nhóm định danh của HIPAA Safe Harbor và báo nguy cơ tái định danh còn lại. Dùng khi cần khẳng định dữ liệu đạt chuẩn Safe Harbor. Từ khoá: HIPAA Safe Harbor, 18 identifiers. |
| `/openmed-skills:auditing-subgroup-fairness` | kỹ năng | Mac | Soi mô hình NER/khử định danh xem có chênh lệch hiệu năng giữa các phân nhóm nhân khẩu (giới, nhóm tuổi, dân tộc). Dùng khi cần chứng minh công cụ không thiệt thòi cho nhóm bệnh nhân nào. Từ khoá: subgroup fairness audit. |
| `/openmed-skills:authoring-model-cards` | kỹ năng | Mac | Soạn 'thẻ mô hình' (model card) ghi mục đích sử dụng, số đo hiệu năng, kết quả theo phân nhóm và giới hạn đã biết. Dùng khi công bố hoặc bàn giao một mô hình. Từ khoá: model card. |
| `/openmed-skills:batch-processing-clinical-text` | kỹ năng | Mac | Chạy NER, bóc PII hoặc khử định danh HÀNG LOẠT trên nhiều bệnh án ngay tại máy, có chia mẻ, lưu điểm dừng và chạy tiếp được khi gián đoạn. Dùng khi xử lý số lượng lớn. Từ khoá: batch processing, sharding, resumable. |
| `/openmed-skills:benchmark-pii-recall` | kỹ năng | Mac | Đo độ NHẠY của mô hình PII bằng dữ liệu chuẩn tổng hợp, báo cáo tỷ lệ bắt đúng mà không in ra chính các định danh. Dùng khi cần bằng chứng model đủ an toàn trước khi xử lý hồ sơ thật. Từ khoá: PII recall benchmark. |
| `/openmed-skills:benchmarking-clinical-ner` | kỹ năng | Mac | Chấm mô hình NER trên bộ ngữ liệu chuẩn của chính bác sĩ: độ chính xác, độ nhạy, F1 ở mức thực thể, rồi phân rã lỗi theo loại. Dùng khi cần biết model sai ở đâu chứ không chỉ điểm tổng. Từ khoá: NER benchmark, precision recall F1. |
| `/openmed-skills:bridging-presidio-and-spacy` | kỹ năng | Mac | Ghép OpenMed với Microsoft Presidio, spaCy hoặc LangChain qua bộ chuyển đổi có sẵn (openmed.interop). Dùng khi đã có sẵn đường ống xử lý khác và muốn dùng chung. Từ khoá: Presidio, spaCy, LangChain interop. |
| `/openmed-skills:building-gold-corpus` | kỹ năng | Mac | Dựng dự án gán nhãn CHUẨN VÀNG tổng hợp để đánh giá model: khung nhãn, hướng dẫn gán nhãn, định dạng BIO. Dùng khi chưa có bộ dữ liệu tham chiếu để chấm điểm. Từ khoá: gold corpus, annotation guidelines. |
| `/openmed-skills:building-patient-timelines` | kỹ năng | Mac | Dựng dòng thời gian bệnh của một người từ các sự kiện đã trích, chuẩn hoá ngày và giải nghĩa mốc tương đối ('ba tuần trước'). Dùng khi cần nhìn diễn tiến bệnh theo trình tự. Từ khoá: patient timeline. |
| `/openmed-skills:building-with-openmed` | kỹ năng | Mac | Khởi động một dự án dùng OpenMed — thư viện xử lý ngôn ngữ y khoa CHẠY NGAY TRÊN MÁY (không gửi dữ liệu ra ngoài): nhận diện thực thể lâm sàng (NER), khử định danh PHI, mã hoá thuật ngữ. Dùng khi bắt đầu bất kỳ việc gì với OpenMed. Từ kh… |
| `/openmed-skills:checking-hipaa-compliance` | kỹ năng | Mac | Chạy checklist Quy tắc Riêng tư và Bảo mật của HIPAA trên toàn đường ống dữ liệu, xuất báo cáo khoảng trống TRƯỚC khi đụng vào PHI thật. Dùng khi chuẩn bị triển khai trên dữ liệu bệnh nhân. Từ khoá: HIPAA compliance checklist. |
| `/openmed-skills:choosing-openmed-models` | kỹ năng | Mac | Chọn đúng mô hình OpenMed cho một nhiệm vụ, chuyên khoa hoặc ngôn ngữ. Dùng khi phân vân 'nên dùng model nào', cần model tiếng Việt/đa ngữ, hoặc cân nhắc độ chính xác so với dung lượng máy. Từ khoá: model selection, OpenMed registry. |
| `/openmed-skills:coding-hcc-risk-adjustment` | kỹ năng | Mac | Ánh xạ bệnh mạn tính đã trích sang nhóm điều chỉnh nguy cơ CMS-HCC V28 và ước tính điểm RAF. Dùng cho bài toán chi trả theo mức nguy cơ; kết quả chỉ để hỗ trợ quyết định. Từ khoá: HCC, RAF, risk adjustment. |
| `/openmed-skills:coding-icd10` | kỹ năng | Mac | Gợi ý mã CHẨN ĐOÁN ICD-10-CM (và mã thủ thuật ICD-10-PCS) kèm lý do, luôn nhắc phải có người mã hoá xác nhận. Dùng khi cần mã hoá danh sách chẩn đoán hoặc chuẩn bị hồ sơ thanh toán. Từ khoá: ICD-10-CM, diagnosis coding, billable code. |
| `/openmed-skills:computing-ecqms` | kỹ năng | Mac | Tính chỉ số chất lượng lâm sàng điện tử (eCQM) bằng logic CQL/QDM, lấy thêm dữ kiện tử số và tiêu chí loại trừ từ bệnh án chữ tự do. Dùng cho báo cáo chất lượng và cải tiến chất lượng (QI). Từ khoá: eCQM, CQL, QDM. |
| `/openmed-skills:configuring-privacy-policies` | kỹ năng | Mac | Chọn và tuỳ chỉnh 7 hồ sơ chính sách bảo mật có sẵn của OpenMed cho việc khử định danh, hoặc tự dựng bộ sinh giá trị thay thế. Dùng khi mức che mặc định quá chặt hoặc quá lỏng so với nhu cầu. Từ khoá: privacy policy profiles. |
| `/openmed-skills:defining-cohort-phenotypes` | kỹ năng | Mac | Viết định nghĩa KIỂU HÌNH và nhóm bệnh nhân theo kiểu OHDSI ATLAS/CIRCE trên OMOP CDM, kết hợp bộ mã chuẩn với dữ kiện rút từ bệnh án. Dùng khi chọn quần thể nghiên cứu từ dữ liệu sẵn có. Từ khoá: computable phenotype, cohort definition. |
| `/openmed-skills:deidentify-a-dataset` | kỹ năng | Mac | Khử định danh các cột chữ tự do trong cả một bộ dữ liệu CSV/JSONL/Parquet, xuất ra bộ dữ liệu đã che kèm báo cáo không chứa PHI. Dùng khi cần làm sạch toàn bộ dữ liệu nghiên cứu chứ không phải một bệnh án lẻ. Từ khoá: dataset de-identifi… |
| `/openmed-skills:deidentifying-clinical-text` | kỹ năng | Mac | KHỬ ĐỊNH DANH bệnh án chữ tự do ngay trên máy — xoá, che hoặc thay thế PHI/PII bằng OpenMed deidentify(). Dùng trước khi đưa bệnh án vào nghiên cứu, chia sẻ hay phân tích. Từ khoá: de-identification, PHI removal, HIPAA. |
| `/openmed-skills:deidentifying-multilingual-text` | kỹ năng | Mac | Khử định danh bệnh án KHÔNG PHẢI TIẾNG ANH bằng tham số lang=/locale=. Dùng khi hồ sơ viết bằng tiếng Việt hoặc ngôn ngữ khác. Từ khoá: multilingual de-identification. |
| `/openmed-skills:deploying-openmed-mcp` | kỹ năng | Mac | Chạy máy chủ MCP của OpenMed để Claude Code, Codex và các ứng dụng chat gọi được trực tiếp NER, bóc PII, khử định danh. Dùng khi muốn dùng OpenMed ngay trong phiên trò chuyện. Từ khoá: MCP server. |
| `/openmed-skills:detecting-pv-signals` | kỹ năng | Mac | Tính tín hiệu bất cân xứng (PRR, ROR, EBGM, IC) trên dữ liệu FAERS/OpenFDA để phát hiện nghi ngờ về an toàn thuốc. Dùng khi nghiên cứu cảnh giác dược. Từ khoá: pharmacovigilance signal, PRR, ROR. |
| `/openmed-skills:enforcing-nophi-logging` | kỹ năng | Mac | Cài lớp chặn PHI lọt vào log, telemetry và báo cáo lỗi. Dùng khi triển khai hệ thống thật — đây là đường rò dữ liệu hay bị bỏ quên nhất. Từ khoá: no-PHI logging guard. |
| `/openmed-skills:etl-to-omop-cdm` | kỹ năng | Mac | Ánh xạ bệnh, thuốc, chỉ số đã mã hoá vào bảng OMOP CDM v5.4 (condition_occurrence, drug_exposure…). Dùng khi cần đưa dữ liệu về chuẩn chung để nghiên cứu đa trung tâm. Từ khoá: OMOP CDM, ETL. |
| `/openmed-skills:evaluating-with-leakage-gates` | kỹ năng | Mac | Chấm mô hình khử định danh hoặc NER theo bộ cổng G1a–G8 lấy tiêu chí rò rỉ PHI làm ưu tiên số một. Dùng khi cần đánh giá chính thức trước khi đưa model vào dùng. Từ khoá: leakage-first gates. |
| `/openmed-skills:exporting-bulk-fhir` | kỹ năng | Mac | Khởi động và thu nhận FHIR Bulk Data $export (toàn hệ thống, theo nhóm hoặc theo bệnh nhân), rồi đẩy thẳng luồng NDJSON vào khử định danh hàng loạt. Dùng khi rút dữ liệu quy mô lớn cho nghiên cứu. Từ khoá: Bulk FHIR export, NDJSON. |
| `/openmed-skills:exporting-to-fhir` | kỹ năng | Mac | Chuyển kết quả NER thành tài nguyên FHIR R4 — Condition, MedicationStatement, Observation. Dùng khi cần đưa dữ liệu bóc từ bệnh án vào hệ thống bệnh án điện tử. Từ khoá: FHIR R4 export. |
| `/openmed-skills:extract-clinical-entities-to-fhir` | kỹ năng | Mac | Chạy trọn một mạch: trích thực thể từ văn bản tổng hợp hoặc đã khử định danh rồi dựng luôn tài nguyên và Bundle FHIR R4. Dùng khi muốn đi thẳng từ bệnh án tới FHIR trong một bước. Từ khoá: text to FHIR. |
| `/openmed-skills:extracting-clinical-entities` | kỹ năng | Mac | Nhận diện thực thể lâm sàng trong văn bản y khoa (bệnh, thuốc, xét nghiệm, thủ thuật, giải phẫu) bằng OpenMed analyze_text. Dùng khi cần bóc thông tin có cấu trúc ra khỏi bệnh án chữ tự do. Từ khoá: clinical NER, extract entities. |
| `/openmed-skills:extracting-dicom-metadata` | kỹ năng | Mac | Đọc header file DICOM và nội dung DICOM-SR để lấy thông tin ca chụp và phần báo cáo, đồng thời gắn cờ PHI nằm lẫn trong header. Dùng khi làm việc với dữ liệu chẩn đoán hình ảnh. Từ khoá: DICOM metadata, DICOM-SR. |
| `/openmed-skills:extracting-lab-tables` | kỹ năng | Mac | Phát hiện và bóc BẢNG xét nghiệm từ PDF, bản scan và ảnh thành dòng dữ liệu có cấu trúc. Dùng khi kết quả cận lâm sàng nằm trong bảng chứ không phải câu văn. Từ khoá: lab table extraction. |
| `/openmed-skills:extracting-pii-entities` | kỹ năng | Mac | PHÁT HIỆN (không xoá) các đoạn chứa thông tin định danh trong bệnh án: họ tên, ngày tháng, số hồ sơ, điện thoại, địa chỉ. Dùng khi cần biết dữ liệu có PHI ở đâu trước khi quyết định xử lý. Từ khoá: extract_pii, PHI detection. |
| `/openmed-skills:extracting-sdoh` | kỹ năng | Mac | Bóc YẾU TỐ XÃ HỘI ẢNH HƯỞNG SỨC KHOẺ (SDOH): nhà ở bấp bênh, thiếu ăn, thất nghiệp, khó khăn đi lại, cô lập xã hội, khó khăn tài chính. Dùng khi nghiên cứu hoặc chăm sóc cần yếu tố xã hội. Từ khoá: SDOH. |
| `/openmed-skills:fetching-fhir-resources` | kỹ năng | Mac | Lấy và phân trang tài nguyên FHIR R4 (Patient, DocumentReference, DiagnosticReport, Observation, Condition) từ máy chủ FHIR, giải mã cả tệp đính kèm. Dùng khi cần kéo dữ liệu về từ bệnh án điện tử. Từ khoá: FHIR REST, paging. |
| `/openmed-skills:gating-deid-leakage` | kỹ năng | Mac | Cài cổng tự động trong CI: dựng thất bại khi độ nhạy phát hiện PHI tụt dưới ngưỡng hoặc lọt loại định danh nghiêm trọng. Dùng khi muốn cơ chế chặn chạy tự động, không phụ thuộc trí nhớ người. Từ khoá: CI leakage gate. |
| `/openmed-skills:generating-synthea-data` | kỹ năng | Mac | Sinh hồ sơ bệnh nhân GIẢ nhưng thực tế bằng MITRE Synthea (FHIR R4, C-CDA, CSV) để phát triển, kiểm thử và trình diễn. Dùng khi cần dữ liệu thử mà không đụng bệnh nhân thật. Từ khoá: Synthea, synthetic patients. |
| `/openmed-skills:generating-synthetic-surrogates` | kỹ năng | Mac | Thay PHI đã phát hiện bằng giá trị GIẢ nhưng hợp lý (tên giả, ngày giả đúng định dạng) để bệnh án vẫn đọc và phân tích được, thay vì đầy dấu [REDACTED]. Dùng khi cần dữ liệu vừa an toàn vừa còn dùng được. Từ khoá: synthetic surrogates. |
| `/openmed-skills:ingesting-clinical-documents` | kỹ năng | Mac | Biến fax scan, ảnh chụp, file CSV/CDA thành văn bản sạch sẵn sàng cho OpenMed, xử lý hoàn toàn trên máy. Dùng khi hồ sơ đầu vào là bản scan hay ảnh. Từ khoá: document ingestion, OCR. |
| `/openmed-skills:linking-umls-concepts` | kỹ năng | Mac | Nối thực thể đã trích với mã khái niệm CUI của UMLS bằng khoá UTS RIÊNG của bác sĩ (không đóng gói sẵn dữ liệu UMLS). Dùng khi cần chuẩn hoá khái niệm ở mức toàn diện nhất. Từ khoá: UMLS, CUI linking. |
| `/openmed-skills:loading-openmed-models` | kỹ năng | Mac | Nạp mô hình OpenMed từ Hugging Face Hub hoặc từ đĩa và dùng lại hiệu quả qua nhiều lần gọi. Dùng khi cần tải model, tăng tốc chạy hàng loạt hoặc quản lý bộ nhớ. Từ khoá: load model, Hugging Face. |
| `/openmed-skills:mapping-loinc` | kỹ năng | Mac | Ánh xạ tên xét nghiệm và chỉ số quan sát sang mã LOINC qua API công khai của Regenstrief. Dùng khi cần chuẩn hoá tên xét nghiệm giữa các labo khác nhau. Từ khoá: LOINC mapping. |
| `/openmed-skills:mapping-to-snomed` | kỹ năng | Mac | Ánh xạ khái niệm lâm sàng sang SNOMED CT qua máy chủ thuật ngữ CỦA CHÍNH BÁC SĨ (Ontoserver, Snowstorm…). Dùng khi cần chuẩn hoá khái niệm để trao đổi hoặc gộp dữ liệu. Từ khoá: SNOMED CT mapping. |
| `/openmed-skills:mining-pubmed-literature` | kỹ năng | Mac | Tìm và tải bài từ PubMed/PMC qua NCBI E-utilities để thu thập bằng chứng và dựng kho văn bản. Dùng khi cần quét y văn số lượng lớn, không phải tra một bài lẻ. Từ khoá: PubMed, E-utilities, PMC. |
| `/openmed-skills:normalizing-rxnorm` | kỹ năng | Mac | Chuẩn hoá tên thuốc đã trích về mã RxCUI của RxNorm qua API RxNav miễn phí. Dùng khi cần gộp biệt dược và hoạt chất về một mối để thống kê. Từ khoá: RxNorm, RxCUI, drug normalization. |
| `/openmed-skills:parsing-ccda-documents` | kỹ năng | Mac | Đọc tài liệu C-CDA/CCD dạng XML để lấy phần tường thuật và các mục đã mã hoá, phân theo mã LOINC của từng mục. Dùng khi nhận hồ sơ trao đổi giữa các cơ sở y tế. Từ khoá: C-CDA, CCD parsing. |
| `/openmed-skills:parsing-hl7v2-messages` | kỹ năng | Mac | Giải mã bản tin HL7 v2.x (ADT, ORU, MDM, ORM) thành segment/field có cấu trúc và lấy ra phần chữ tự do ở OBX-5, NTE-3. Dùng khi ghép nối với hệ thống thông tin bệnh viện. Từ khoá: HL7 v2, ADT, ORU. |
| `/openmed-skills:parsing-lab-values` | kỹ năng | Mac | Đọc trị số xét nghiệm và khoảng tham chiếu từ bệnh án, gắn cờ thấp/bình thường/cao/NGUY KỊCH. Dùng khi cần diễn giải nhanh kết quả trong văn bản. Từ khoá: lab values, reference range, critical. |
| `/openmed-skills:parsing-trial-eligibility` | kỹ năng | Mac | Chuyển tiêu chuẩn chọn/loại của thử nghiệm lâm sàng từ chữ tự do thành logic có cấu trúc, rồi đối chiếu với dữ kiện bệnh nhân. Dùng khi sàng bệnh nhân đủ điều kiện tham gia nghiên cứu. Từ khoá: trial eligibility, patient matching. |
| `/openmed-skills:pick-a-pii-model` | kỹ năng | Mac | Chọn mô hình phát hiện PII chạy trên máy theo ngôn ngữ, định dạng và dung lượng, BẮT BUỘC kiểm định độ nhạy trước khi dùng thật. Dùng khi cần cân nhắc giữa model nhẹ và model bắt sót ít. Từ khoá: PII model selection. |
| `/openmed-skills:pseudonymizing-for-gdpr` | kỹ năng | Mac | Giả danh hoá đạt chuẩn GDPR, giữ khoá liên kết ngược ở nơi tách biệt để có thể khôi phục có kiểm soát. Dùng khi nghiên cứu chịu ràng buộc GDPR châu Âu. Từ khoá: GDPR pseudonymization. |
| `/openmed-skills:querying-openfda-labels` | kỹ năng | Mac | Tra nhãn thuốc FDA, danh mục NDC, chỉ định, CẢNH BÁO ĐÓNG KHUNG và các đợt thu hồi qua API OpenFDA miễn phí. Dùng khi cần kiểm tra thông tin an toàn thuốc từ nguồn gốc. Từ khoá: OpenFDA, drug label, boxed warning. |
| `/openmed-skills:querying-terminology-service` | kỹ năng | Mac | Gọi máy chủ thuật ngữ FHIR ($validate-code, $expand, $lookup, $translate) để kiểm và mở rộng bộ mã. Dùng khi cần xác nhận một mã có hợp lệ hoặc lấy trọn nhánh mã con. Từ khoá: FHIR terminology service. |
| `/openmed-skills:reconciling-problem-lists` | kỹ năng | Mac | Gộp trùng và đối chiếu các chẩn đoán đã trích thành MỘT danh sách vấn đề sạch, có trạng thái đang mắc / đã khỏi / tiền sử. Dùng khi hồ sơ nhiều lần khám bị lặp chẩn đoán. Từ khoá: problem list reconciliation. |
| `/openmed-skills:reidentifying-text` | kỹ năng | Mac | Khử định danh CÓ THỂ ĐẢO NGƯỢC — lưu bảng ánh xạ riêng để sau này khôi phục lại PHI gốc. Dùng khi cần giả danh hoá (pseudonymization) thay vì xoá hẳn, ví dụ còn phải liên hệ lại bệnh nhân. Từ khoá: re-identification, pseudonymization. |
| `/openmed-skills:reporting-adverse-events` | kỹ năng | Mac | Chuyển biến cố bất lợi đã trích thành các trường báo cáo chuẩn FAERS / ICH E2B(R3): thuốc nghi ngờ, phản ứng theo MedDRA, mức nghiêm trọng. Dùng khi làm cảnh giác dược. Từ khoá: adverse event, FAERS, E2B, MedDRA. |
| `/openmed-skills:resolving-clinical-context` | kỹ năng | Mac | Gán PHỦ ĐỊNH, THỜI ĐIỂM và MỨC CHẮC CHẮN cho thực thể đã trích, để 'không đau ngực' không bị đếm thành có đau ngực. Dùng BẮT BUỘC trước khi thống kê tần suất triệu chứng. Từ khoá: negation, temporality, ConText. |
| `/openmed-skills:reviewing-reidentification-risk` | kỹ năng | Mac | Chấm nguy cơ TÁI ĐỊNH DANH theo kiểu chuyên gia thẩm định: k-anonymity, l-diversity, cộng thêm phép tấn công thử nghiệm thật lên dữ liệu đã che. Dùng khi Safe Harbor chưa đủ và cần expert determination. Từ khoá: re-identification risk, k… |
| `/openmed-skills:running-openmed-ondevice` | kỹ năng | Mac | Chạy mô hình OpenMed hoàn toàn trên máy bằng MLX (chip Apple), CoreML hoặc ONNX/WebGPU, kèm cách chuyển đổi định dạng. Dùng khi dữ liệu tuyệt đối không được rời máy. Từ khoá: on-device, MLX, CoreML, ONNX. |
| `/openmed-skills:running-zeroshot-ner` | kỹ năng | Mac | Bóc tách loại thực thể TỰ ĐỊNH NGHĨA mà không cần huấn luyện lại, bằng GLiNER/GLiNER2 trong OpenMed. Dùng khi cần trích một khái niệm lạ chưa có model sẵn (ví dụ 'yếu tố nguy cơ nghề nghiệp'). Từ khoá: zero-shot NER, GLiNER. |
| `/openmed-skills:scaffolding-smart-on-fhir` | kỹ năng | Mac | Dựng khung ứng dụng SMART-on-FHIR (SMART App Launch v2, OAuth2 PKCE, scope, xử lý token) để công cụ chạy được ngay trong bệnh án điện tử. Dùng khi muốn tích hợp vào phần mềm bệnh viện. Từ khoá: SMART on FHIR. |
| `/openmed-skills:searching-clinicaltrials` | kỹ năng | Mac | Tra ClinicalTrials.gov theo bệnh, can thiệp và trạng thái tuyển bệnh, dùng API v2. Dùng khi cần biết 'đã có ai đang làm nghiên cứu này chưa' hoặc tìm thử nghiệm cho bệnh nhân. Từ khoá: ClinicalTrials.gov. |
| `/openmed-skills:segmenting-clinical-sections` | kỹ năng | Mac | Cắt bệnh án thành các mục chuẩn (Lý do khám, Bệnh sử, Tiền sử, Thuốc đang dùng, Dị ứng, Đánh giá & Kế hoạch) trước khi chạy NER. Dùng khi cần trích thông tin đúng mục, tránh lẫn tiền sử với bệnh hiện tại. Từ khoá: section segmentation. |
| `/openmed-skills:serving-openmed-rest-api` | kỹ năng | Mac | Dựng dịch vụ REST FastAPI của OpenMed cho NER, bóc PII và khử định danh, có health check và quản lý vòng đời model. Dùng khi nhiều người/nhiều ứng dụng cùng gọi chung một máy chủ. Từ khoá: REST API, FastAPI. |
| `/openmed-skills:setup-openmed` | kỹ năng | Mac | Collect a bounded set of de-identification policy decisions and write a deterministic, reviewable DEID-POLICY.md from the versioned local template. Use when a project needs explicit jurisdiction, recall floor, surrogate strategy, model p… |
| `/openmed-skills:shifting-clinical-dates` | kỹ năng | Mac | Dời ngày tháng theo từng bệnh nhân sao cho GIỮ NGUYÊN khoảng cách giữa các mốc thời gian mà vẫn đạt quy tắc ngày của HIPAA Safe Harbor. Dùng khi nghiên cứu cần trình tự thời gian nhưng không được lộ ngày thật. Từ khoá: date shifting. |
| `/openmed-skills:structuring-radiology-reports` | kỹ năng | Mac | Chuyển báo cáo chẩn đoán hình ảnh chữ tự do thành cấu trúc: tổn thương, kích thước, bên phải/trái, vị trí giải phẫu, khuyến nghị theo dõi. Dùng khi cần dữ liệu hình ảnh có cấu trúc cho nghiên cứu. Từ khoá: radiology report structuring. |
| `/openmed-skills:summarizing-clinical-notes` | kỹ năng | Mac | Tóm tắt bệnh án có CHỈ RÕ NGUỒN cho từng ý — tóm tắt một dòng, diễn biến nằm viện, tóm tắt theo vấn đề. Dùng khi cần bản tóm tắt kiểm chứng được, không phải bản viết lại tự do. Từ khoá: clinical summarization, citation-anchored. |
| `/openmed-skills:validating-us-core` | kỹ năng | Mac | Kiểm tài nguyên và Bundle FHIR R4 theo hồ sơ US Core/USCDI bằng bộ kiểm chính thức của HL7. Dùng trước khi gửi dữ liệu vào bệnh án điện tử, để bắt lỗi cấu trúc sớm. Từ khoá: US Core validation. |

### ebm-agents  (64)

| Gọi bằng | Loại | Máy | Làm gì |
|---|---|---|---|
| `agent an-toan-nghien-cuu` | agent | Mac | An toàn người tham gia trong nghiên cứu CAN THIỆP — cảnh giác dược (AE/SAE), định nghĩa & phân độ biến cố, quy tắc dừng (stopping rules), điều lệ DSMB/DMC, báo cáo an toàn theo timeline. Dùng cho thử nghiệm lâm sàng/can thiệp. Với nghiên… |
| `agent bien-so-nghien-cuu` | agent | Mac | Đặc tả bộ BIẾN SỐ nghiên cứu đầy đủ-đúng chuẩn, gắn với câu hỏi/PICO/kết cục và loại thiết kế (RCT, cohort, case-control, cắt ngang, chẩn đoán…). Dùng khi cần liệt kê đủ nhóm biến, phân loại vai trò nhân quả (nhiễu/điều chỉnh hiệu quả/tr… |
| `agent binh-duyet` | agent | Mac | Bình duyệt bản thảo/đề cương theo checklist trước khi nộp. Dùng khi cần rà soát phản biện: tính hợp lệ phương pháp, tính đúng thống kê, tuân thủ chuẩn báo cáo (CONSORT/STROBE/PRISMA), liêm chính khoa học (trích dẫn, COI, đạo đức, khai bá… |
| `agent cap-nhat-guideline` | agent | Mac | Theo dõi guideline mới, meta-analysis và thử nghiệm lớn mới công bố; cảnh báo khi khuyến cáo cũ đã lỗi thời ("có guideline 2025 thay đổi thực hành…"). Quét nguồn neo (WHO/NICE/ESC/AHA/ADA/KDIGO/GOLD/GINA…), đối chiếu mốc cập nhật, đề xuấ… |
| `agent cau-hoi-nghien-cuu` | agent | Mac | Xác định câu hỏi nghiên cứu — chuyển một vấn đề lâm sàng thành câu hỏi PICO/PECO rõ ràng, xác định kết cục chính/phụ, đề xuất giả thuyết, và kiểm tính khả thi FINER. Dùng ở cổng G0 trước khi thiết kế. Đầu ra là nền cho tong-quan-y-van và… |
| `agent cham-soc-giam-nhe` | agent | Mac | Chăm sóc GIẢM NHẸ / cuối đời ngoại trú — kiểm soát TRIỆU CHỨNG bệnh nhân bệnh nặng/giai đoạn cuối (đau bậc WHO, khó thở, buồn nôn, táo bón, mê sảng, lo âu; thang ESAS), MỤC TIÊU CHĂM SÓC (goals of care), KẾ HOẠCH CHĂM SÓC TRƯỚC (ACP). Dù… |
| `agent chan-doan-xac-suat` | agent | Mac | Suy luận chẩn đoán theo xác suất (Bayes) tại điểm khám: XÁC SUẤT TIỀN NGHIỆM → áp TỶ SỐ KHẢ DĨ (LR+/LR−) → XÁC SUẤT HẬU NGHIỆM → đối chiếu NGƯỠNG TEST–TREAT để quyết định không làm gì / test thêm / điều trị luôn. Dùng khi câu hỏi loại CH… |
| `agent co-mau-nghien-cuu` | agent | Mac | Tính CỠ MẪU / POWER tối ưu cho nghiên cứu y khoa TRƯỚC khi thu dữ liệu (cổng G3): tự nhận diện thiết kế (RCT song song/bắt chéo, cohort, case-control, cắt ngang, độ chính xác chẩn đoán, sống còn/log-rank, non-inferiority/equivalence), ch… |
| `agent cong-cu-do-luong` | agent | Mac | Phát triển và KIỂM ĐỊNH CÔNG CỤ ĐO LƯỜNG (bộ câu hỏi, thang đo, PROM) theo chuẩn COSMIN. Dùng khi đề tài cần bộ câu hỏi/thang đo (hài lòng người bệnh, chất lượng sống, tuân thủ, mức độ triệu chứng) và phải chứng minh công cụ ĐÁNG TIN: dị… |
| `agent dao-duc-dang-ky` | agent | Mac | Sản xuất hồ sơ đạo đức và đăng ký nghiên cứu TRƯỚC khi thu thập dữ liệu (cổng G2). Dùng khi cần soạn hồ sơ Hội đồng Đạo đức (IRB), phiếu đồng thuận tham gia (ICF), bản đăng ký nghiên cứu (ClinicalTrials.gov/WHO ICTRP/đăng ký trong nước),… |
| `agent dau-man-tinh` | agent | Mac | Quản lý ĐAU MẠN TÍNH ngoại trú (đau > 3 tháng, KHÔNG do ung thư tiến triển cấp): phân loại theo CƠ CHẾ đau, chọn thang đã kiểm định (NRS, BPI, DN4), chiến lược ĐA MÔ THỨC, QUẢN LÝ OPIOID an toàn & cai/giảm liều, tầm soát trầm cảm/lo âu. … |
| `agent dien-giai-can-lam-sang` | agent | Mac | Đọc–diễn giải KẾT QUẢ CẬN LÂM SÀNG ngoại trú (panel xét nghiệm máu/nước tiểu, ECG…): gắn cờ GIÁ TRỊ NGUY KỊCH (critical value) cần xử trí/chuyển tuyến ngay. Dùng khi bác sĩ đưa bộ kết quả và hỏi "kết quả này nghĩa là gì / có nguy hiểm kh… |
| `agent dien-giai-ket-qua` | agent | Mac | Diễn giải kết quả nghiên cứu (Results Interpretation) — chuyển con số thống kê thành Ý NGHĨA LÂM SÀNG, so sánh với y văn, phân tích điểm mạnh/yếu, và đề xuất hướng nghiên cứu tiếp theo. Cầu nối giữa phan-tich-thong-ke (ra số) và viet-ban… |
| `agent dieu-phoi-g0` | agent | Mac | [Nghiên cứu] ĐIỀU PHỐI CỔNG G0 — Câu hỏi nghiên cứu & tính khả thi: CHỊU TRÁCH NHIỆM kết quả mọi nhiệm vụ của cổng — giao từng nhiệm vụ cho agent chuyên trách, tổ chức đánh giá chéo đầu ra (rubric RQ1–RQ8) và tranh biện các điểm quyết đị… |
| `agent dieu-phoi-g1` | agent | Mac | [Nghiên cứu] ĐIỀU PHỐI CỔNG G1 — Thiết kế & đề cương lõi: CHỊU TRÁCH NHIỆM kết quả mọi nhiệm vụ của cổng — giao từng nhiệm vụ cho agent chuyên trách, tổ chức đánh giá chéo đầu ra (rubric RQ1–RQ8) và tranh biện các điểm quyết định trước k… |
| `agent dieu-phoi-g10` | agent | Mac | [Nghiên cứu] ĐIỀU PHỐI CỔNG G10 — Khoá gói phát hành: CHỊU TRÁCH NHIỆM kết quả mọi nhiệm vụ của cổng — giao từng nhiệm vụ cho agent chuyên trách, tổ chức đánh giá chéo đầu ra (rubric RQ1–RQ8) và tranh biện các điểm quyết định trước khi k… |
| `agent dieu-phoi-g2` | agent | Mac | [Nghiên cứu] ĐIỀU PHỐI CỔNG G2 — Đạo đức & đăng ký: CHỊU TRÁCH NHIỆM kết quả mọi nhiệm vụ của cổng — giao từng nhiệm vụ cho agent chuyên trách, tổ chức đánh giá chéo đầu ra (rubric RQ1–RQ8) và tranh biện các điểm quyết định trước khi kết… |
| `agent dieu-phoi-g3` | agent | Mac | [Nghiên cứu] ĐIỀU PHỐI CỔNG G3 — Cỡ mẫu & bộ biến số: CHỊU TRÁCH NHIỆM kết quả mọi nhiệm vụ của cổng — giao từng nhiệm vụ cho agent chuyên trách, tổ chức đánh giá chéo đầu ra (rubric RQ1–RQ8) và tranh biện các điểm quyết định trước khi k… |
| `agent dieu-phoi-g4` | agent | Mac | [Nghiên cứu] ĐIỀU PHỐI CỔNG G4 — Kế hoạch phân tích thống kê (SAP): CHỊU TRÁCH NHIỆM kết quả mọi nhiệm vụ của cổng — giao từng nhiệm vụ cho agent chuyên trách, tổ chức đánh giá chéo đầu ra (rubric RQ1–RQ8) và tranh biện các điểm quyết đị… |
| `agent dieu-phoi-g5` | agent | Mac | [Nghiên cứu] ĐIỀU PHỐI CỔNG G5 — Thu thập, làm sạch & khoá dữ liệu: CHỊU TRÁCH NHIỆM kết quả mọi nhiệm vụ của cổng — giao từng nhiệm vụ cho agent chuyên trách, tổ chức đánh giá chéo đầu ra (rubric RQ1–RQ8) và tranh biện các điểm quyết đị… |
| `agent dieu-phoi-g6` | agent | Mac | [Nghiên cứu] ĐIỀU PHỐI CỔNG G6 — Phân tích & diễn giải: CHỊU TRÁCH NHIỆM kết quả mọi nhiệm vụ của cổng — giao từng nhiệm vụ cho agent chuyên trách, tổ chức đánh giá chéo đầu ra (rubric RQ1–RQ8) và tranh biện các điểm quyết định trước khi… |
| `agent dieu-phoi-g7` | agent | Mac | [Nghiên cứu] ĐIỀU PHỐI CỔNG G7 — Viết bản thảo: CHỊU TRÁCH NHIỆM kết quả mọi nhiệm vụ của cổng — giao từng nhiệm vụ cho agent chuyên trách, tổ chức đánh giá chéo đầu ra (rubric RQ1–RQ8) và tranh biện các điểm quyết định trước khi kết luậ… |
| `agent dieu-phoi-g8` | agent | Mac | [Nghiên cứu] ĐIỀU PHỐI CỔNG G8 — Bình duyệt trước nộp: CHỊU TRÁCH NHIỆM kết quả mọi nhiệm vụ của cổng — giao từng nhiệm vụ cho agent chuyên trách, tổ chức đánh giá chéo đầu ra (rubric RQ1–RQ8) và tranh biện các điểm quyết định trước khi … |
| `agent dieu-phoi-g9` | agent | Mac | [Nghiên cứu] ĐIỀU PHỐI CỔNG G9 — Liêm chính tác giả & công bố: CHỊU TRÁCH NHIỆM kết quả mọi nhiệm vụ của cổng — giao từng nhiệm vụ cho agent chuyên trách, tổ chức đánh giá chéo đầu ra (rubric RQ1–RQ8) và tranh biện các điểm quyết định tr… |
| `agent dieu-phoi-lam-sang` | agent | Mac | Điều phối trọn một CA khám ngoại trú EBM theo 5 bước (Hỏi→Tìm→Thẩm định→Áp dụng→Theo dõi). Dùng khi bác sĩ NÊU MỘT CA/TÌNH HUỐNG lâm sàng ('tôi có bệnh nhân…', 'khám ca này', hỏi chẩn đoán/xử trí cho một người bệnh cụ thể) — tự chạy tuần… |
| `agent dieu-phoi-nghien-cuu` | agent | Mac | Điều phối đề tài nghiên cứu y khoa từ ý tưởng đến gói phát hành qua G0–G10. Dùng khi nhà nghiên cứu nêu MỘT đề tài/câu hỏi nghiên cứu, hoặc chạy một chặng vòng đời. CHỈ CẦN TÊN/MÔ TẢ ĐỀ TÀI là tự march G0→G10, dừng ở 6 cổng cứng: đạo đức… |
| `agent du-phong-tam-soat` | agent | Mac | Dự phòng & tầm soát dựa chứng cứ, bệnh nhân ngoại trú, theo tuổi–giới–nguy cơ: cấp 1 (lối sống, tiêm chủng, hóa dự phòng statin/aspirin), cấp 2 (ung thư cổ tử cung·vú·đại trực tràng·phổi, ĐTĐ, lipid, loãng xương, phình ĐMC bụng…), cấp 3 … |
| `agent giam-khao-cong` | agent | Mac | [Nghiên cứu] GIÁM KHẢO hội đồng cổng G0–G10 — chấm ĐỘC LẬP đầu ra của một agent nhiệm vụ theo rubric RQ1–RQ8 (hợp đồng cổng · phương pháp · truy nguyên · nhất quán xuyên cổng · đầy đủ · thẩm quyền · PII · rõ cho người ký); mọi nhận xét đ… |
| `agent hieu-dinh-song-ngu` | agent | Mac | Hiệu đính & dịch SONG NGỮ Việt↔Anh cho bản thảo khoa học trước khi nộp tạp chí quốc tế — dịch trung thành thuật ngữ y khoa, chống lỗi "Vietlish" (trật tự từ, mạo từ, thì, danh-động hóa, câu dài lê thê), chuẩn hóa văn phong học thuật (act… |
| `agent huong-dan-lam-sang` | agent | Mac | Cầu nối Nghiên cứu ↔ Thực hành — đặt phát hiện vào bối cảnh hướng dẫn lâm sàng hiện hành, dựng khối GRADE Evidence-to-Decision, đề xuất hoặc cập nhật khuyến cáo (chiều + độ mạnh), rồi nạp EBM_MASTER. Dùng khi cần trả lời "phát hiện này đ… |
| `agent ke-don-an-toan` | agent | Mac | Rà soát an toàn kê đơn cho bệnh nhân ngoại trú. Dùng khi cần kiểm tra tương tác thuốc, chống chỉ định, chỉnh liều theo chức năng thận/gan, đa thuốc ở người cao tuổi (Beers/STOPP-START), hiệu chỉnh theo bệnh mạn. Trả về cảnh báo phân tầng… |
| `agent ke-hoach-trien-khai` | agent | Mac | Lập KẾ HOẠCH TRIỂN KHAI đề tài (artifact A13) — nhân lực & phân công vai trò (thu thập/nhập liệu/phân tích/giám sát), TIẾN ĐỘ theo mốc cổng G0–G9 (biểu Gantt/timeline), DỰ TRÙ KINH PHÍ (nhân công, vật tư, xét nghiệm, phần mềm, công bố/AP… |
| `agent ket-qua-hoc-tap` | agent | Mac | Ghi nhận kết quả điều trị (ẩn danh) và phát hiện tín hiệu để cải tiến thực hành. Theo dõi kết cục/biến cố/không dung nạp, tổng hợp \"pattern\" ở nhóm bệnh nhân tương tự. CẢNH BÁO: tín hiệu nội bộ là GIẢ THUYẾT cần kiểm chứng bằng chứng —… |
| `agent khai-thac-benh-su-kham` | agent | Mac | Khai thác BỆNH SỬ và KHÁM LÂM SÀNG CÓ TRỌNG ĐIỂM cho ca ngoại trú — hỏi bệnh có hệ thống (SOCRATES/OPQRST), điểm lại cơ quan (ROS), tiền sử, đề xuất khám thực thể theo hội chứng; trả bộ dữ liệu lâm sàng có cấu trúc cho chẩn đoán phân biệ… |
| `agent khoang-trong-nghien-cuu` | agent | Mac | Đối chiếu câu hỏi nghiên cứu với guideline/khuyến cáo hiện hành và xác định KHOẢNG TRỐNG NGHIÊN CỨU (research gap). Trả lời "câu hỏi này đã được giải đáp chưa, guideline nói gì, còn thiếu gì" để biện minh tính mới và ý nghĩa của đề tài. … |
| `agent kiem-chung-trich-dan` | agent | Mac | Kiểm chứng và quản lý trích dẫn học thuật — cổng cứng chống trích dẫn ma. Dùng khi cần xác minh mọi PMID/DOI có thật và đúng nội dung, đối chiếu tài liệu tham khảo với câu khẳng định trong bài, sinh danh mục Vancouver/AMA/APA hoặc BibTeX… |
| `agent kinh-te-y-te` | agent | Mac | Thiết kế và báo cáo PHÂN TÍCH KINH TẾ Y TẾ cho nghiên cứu/đề tài: chi phí–hiệu quả (CEA), chi phí–thỏa dụng (CUA, QALY/DALY), chi phí–lợi ích (CBA), tác động ngân sách (BIA). ICER + ngưỡng sẵn lòng chi trả (WTP); độ nhạy PSA/CEAC; mô hìn… |
| `agent loi-dan-tuan-thu` | agent | Mac | Sinh lời dặn bệnh nhân khổ A5 và kế hoạch tuân thủ điều trị tại điểm khám. Dùng khi cần in tờ dặn dò dễ hiểu (dùng thuốc, thay đổi lối sống, dấu hiệu nguy hiểm, tái khám) và/hoặc lập kế hoạch theo dõi tuân thủ. Văn phong cho bệnh nhân, k… |
| `agent meta-phan-tich` | agent | Mac | Phân tích gộp (meta-analysis) khi tổng hợp định lượng nhiều nghiên cứu — chọn mô hình hiệu ứng, tính pooled effect (OR/RR/HR/MD/SMD) + 95% CI, vẽ forest/funnel plot, đánh giá tính không đồng nhất (I²/Q/τ²) và publication bias (Egger). Ch… |
| `agent mo-hinh-tien-luong` | agent | Mac | Phát triển và KIỂM ĐỊNH MÔ HÌNH TIÊN LƯỢNG/CHẨN ĐOÁN (clinical prediction model) cho nghiên cứu y khoa theo chuẩn TRIPOD+AI; PROBAST+AI khi thẩm định mô hình đã có. Dùng khi đề tài xây/kiểm định công cụ dự báo nguy cơ. KHÔNG bịa hệ số/AU… |
| `agent nghien-cuu-dinh-tinh` | agent | Mac | Thiết kế & phân tích NGHIÊN CỨU ĐỊNH TÍNH & HỖN HỢP (mixed-methods) — chọn cách tiếp cận (hiện tượng học, grounded theory, phân tích chủ đề, nghiên cứu trường hợp), lấy mẫu có chủ đích + BÃO HÒA DỮ LIỆU, soạn câu hỏi phỏng vấn/nhóm tiêu … |
| `agent nop-bai-phan-hoi` | agent | Mac | Hỗ trợ nộp bài và phản hồi phản biện sau khi bản thảo sẵn sàng. Dùng khi cần chọn tạp chí đích (đúng phạm vi, có chỉ mục uy tín, tránh predatory), soạn cover letter, đóng gói nộp theo yêu cầu tạp chí, và viết thư phản hồi phản biện (resp… |
| `agent phan-bien-tranh-bien` | agent | Mac | [Nghiên cứu] BÊN PHẢN BIỆN trong tranh biện hội đồng cổng G0–G10 — tìm phản đối MẠNH NHẤT, có căn cứ kiểm được, với kết luận dự kiến của điều phối cổng cho một điểm quyết định (DP); không tìm được phản đối có căn cứ thì nhường (nhuong=tr… |
| `agent phan-tich-thong-ke` | agent | Mac | Phân tích thống kê SAU khi dữ liệu đã khóa — chạy đúng SAP đã khóa trên DB đã khóa, kiểm giả định, hồi quy/sống còn/meta-analysis, báo cáo ước lượng + 95% CI chuẩn báo cáo. Dùng ở G6. Mọi việc thiết kế/khóa SAP thuộc về thiet-ke-nghien-c… |
| `agent pico-lam-sang` | agent | Mac | Đặt câu hỏi lâm sàng PICO tại điểm khám — chuyển than phiền/bệnh cảnh thành câu hỏi PICO sắc, xác định KẾT CỤC QUAN TRỌNG VỚI BỆNH NHÂN (tử vong, biến cố tim mạch, chất lượng sống…) và loại câu hỏi (điều trị/chẩn đoán/tiên lượng/tác hại)… |
| `agent quan-ly-du-lieu` | agent | Mac | Quản lý, làm sạch và khóa dữ liệu nghiên cứu + đóng gói tái lặp (cổng G5). Dùng khi cần thiết kế CRF/data dictionary, luật kiểm tra dữ liệu (range/logic/consistency), khử định danh, nhật ký truy vấn, kế hoạch dữ liệu thiếu, quy trình khó… |
| `agent quan-ly-khang-dong` | agent | Mac | Quản lý KHÁNG ĐÔNG ngoại trú trọn vòng (rung nhĩ không do van, VTE, van tim cơ học): cân bằng nguy cơ huyết khối vs chảy máu (CHA₂DS₂-VASc/HAS-BLED qua thang-diem-nguy-co), CHỌN thuốc VKA vs DOAC theo chỉ định (van cơ học/hẹp van 2 lá vừ… |
| `agent quyet-dinh-chung` | agent | Mac | Cá thể hóa khuyến cáo theo bối cảnh bệnh nhân và hỗ trợ quyết định chung (shared decision-making). Điều chỉnh theo bệnh kèm, tuổi, thai kỳ, suy thận/gan, dị ứng, kinh tế, văn hóa, giá trị-ưu tiên; trình bày lợi ích–nguy cơ–bất định + lựa… |
| `agent sang-loc-co-do` | agent | Mac | Sàng lọc CỜ ĐỎ và ngưỡng CHUYỂN TUYẾN/CẤP CỨU ở BƯỚC 0 của mọi ca ngoại trú — quét nhanh dấu hiệu nguy hiểm theo triệu chứng/hội chứng (đau ngực, khó thở, đau đầu, đau bụng, sốt, đau lưng, chóng mặt, sụt cân…), nêu NGAY điều cần loại trừ… |
| `agent so-cai-ghi-nho` | agent | Mac | Thư ký sổ cái & bộ nhớ của đề tài — ghi quyết định, mốc cổng, artifact và bài học vào EBM_MASTER + bộ nhớ bền (MEMORY.md) để không mất qua phiên. Dùng sau mỗi cổng G hoàn tất, khi chốt một quyết định thiết kế/thống kê, hoặc khi cần khôi … |
| `agent tham-dinh-dau-ra` | agent | Mac | THẨM ĐỊNH ĐẦU RA ĐỘC LẬP — chốt kiểm cuối chạy SAU mỗi nhạc trưởng (dieu-phoi-lam-sang, dieu-phoi-nghien-cuu), trước khi trả bác sĩ. Soi gói 2 LỚP: Lớp 1 LIÊM CHÍNH R1–R7 (nguồn · PII · vượt cổng A/B/G · tự gán GRADE · tách 2 trục · nhãn… |
| `agent tham-dinh-do-chinh-xac-chan-doan` | agent | Mac | Thẩm định ĐỘ TIN CẬY nghiên cứu ĐỘ CHÍNH XÁC CHẨN ĐOÁN (diagnostic test accuracy): QUADAS-3 hiện hành (QUADAS-2 chỉ tương thích ngược; 2 test → QUADAS-C khi phù hợp), STARD 2015/STARD-AI, diễn giải Se/Sp/LR/PPV-NPV theo prevalence, GRADE… |
| `agent tham-dinh-grade-nnt` | agent | Mac | Thẩm định chất lượng chứng cứ và lượng hóa lợi ích/tác hại cho một câu hỏi lâm sàng. Dùng khi đã có (các) nghiên cứu và cần chấm GRADE, tính NNT/NNH, đánh giá nguy cơ sai lệch bằng ĐÚNG công cụ theo thiết kế (RoB 2 cho RCT; ROBINS-I V2/R… |
| `agent tham-dinh-phe-binh` | agent | Mac | Thẩm định phê bình MỘT nghiên cứu (đọc toàn văn/PDF) — tóm tắt theo PICO, đánh giá nguy cơ sai lệch theo đúng công cụ của thiết kế (RoB 2, ROBINS-I, QUADAS-3 — bản kế nhiệm QUADAS-2, Ann Intern Med 17/2/2026, doi:10.7326/ANNALS-25-02104,… |
| `agent thang-diem-nguy-co` | agent | Mac | Chọn ĐÚNG và áp dụng THANG ĐIỂM/CÔNG CỤ NGUY CƠ lâm sàng đã kiểm định cho ca ngoại trú → nguy cơ tuyệt đối + ngưỡng hành động (Cổng A): CHA₂DS₂-VASc·HAS-BLED cho rung nhĩ; ASCVD/SCORE2 cho nguy cơ tim mạch; Wells·PERC cho thuyên tắc phổi… |
| `agent theo-doi-benh-man` | agent | Mac | KẾ HOẠCH THEO DÕI DÀI HẠN & ĐIỀU TRỊ THEO MỤC TIÊU (treat-to-target) cho bệnh mạn ngoại trú (ĐTĐ, THA, lipid, COPD/hen, gút…): ĐÍCH điều trị theo guideline, cá thể hóa theo tuổi/bệnh kèm/kỳ vọng sống; TÁI KHÁM, XÉT NGHIỆM theo dõi + tần … |
| `agent thiet-ke-nghien-cuu` | agent | Mac | Thiết kế nghiên cứu y khoa TRƯỚC khi có dữ liệu — chọn thiết kế phù hợp, kiểm soát sai lệch, soạn và KHÓA kế hoạch phân tích thống kê (SAP) + khung bảng kết quả (dummy tables). Dùng ở G1/G4. Cỡ mẫu/power do co-mau-nghien-cuu đảm nhiệm (G… |
| `agent thu-thu-tai-lieu` | agent | Mac | Tìm y văn & dựng/soát tài liệu tham khảo cho nghiên cứu y khoa. TÌM (đề tài/câu hỏi): PICO → CHIẾN LƯỢC TÌM (từ khóa, MeSH, nguồn PubMed/Cochrane/Europe PMC/guideline) → LOẠI TÀI LIỆU ưu tiên (guideline, SR/MA, RCT…) → DANH MỤC → Vancouv… |
| `agent tong-quan-y-van` | agent | Mac | Thực hiện tổng quan y văn có hệ thống cho một câu hỏi nghiên cứu (PICO/PECO). Dùng khi cần rà soát bằng chứng theo PRISMA, dựng chiến lược tìm, sàng lọc, trích xuất dữ liệu, đánh giá nguy cơ sai lệch và tổng hợp (định tính/meta-analysis)… |
| `agent tra-cuu-chung-cu` | agent | Mac | Tra cứu chứng cứ y khoa cho MỘT câu hỏi lâm sàng (PICO). Dùng khi cần tìm bằng chứng tốt nhất + mới nhất để trả lời một thắc mắc tại điểm khám. Trả về câu trả lời CÓ TRÍCH DẪN (PMID/DOI), thứ tự: RAG kho → nguồn CHÍNH THỐNG (guideline hi… |
| `agent tram-cam-lo-au` | agent | Mac | Tiếp cận TRẦM CẢM & LO ÂU người lớn ngoại trú (chăm sóc ban đầu) theo CHĂM SÓC THEO BẬC — sàng lọc PHQ-9/GAD-7, khởi trị/theo dõi đáp ứng & tác dụng phụ, ngưỡng CHUYỂN tâm thần. BẮT BUỘC nối CỨNG sang-loc-co-do sàng Ý TƯỞNG TỰ SÁT/tự hại… |
| `agent trich-xuat-y-van` | agent | Mac | Trích xuất và tóm tắt có cấu trúc MỘT bài báo/nghiên cứu thành bảng dữ liệu chuẩn (PICO, thiết kế, cỡ mẫu, kết cục, hiệu ứng + CI, nguy cơ sai lệch). Dùng khi cần đọc nhanh một bài, dựng bảng trích xuất cho tổng quan hệ thống, hoặc chuẩn… |
| `agent trong-tai-tranh-bien` | agent | Mac | [Nghiên cứu] TRỌNG TÀI tranh biện hội đồng cổng G0–G10 — ngữ cảnh mới, không tham gia soạn; kiểm căn cứ của từng bên, phán từng phản đối (chấp nhận/bác/chưa đủ căn cứ), ra kết quả giữ kết luận · sửa kết luận · chuyển bác sĩ khi tranh chấ… |
| `agent viet-ban-thao` | agent | Mac | Viết bản thảo khoa học theo cấu trúc IMRAD, văn xuôi liền mạch, trích dẫn Vancouver/APA/AMA, tuân thủ chuẩn báo cáo (CONSORT/STROBE/PRISMA/SPIRIT/STARD/TRIPOD). Dùng khi cần viết bài báo nghiên cứu, protocol, hoặc báo cáo nghiệm thu. Quy… |

### medsci-project  (59)

| Gọi bằng | Loại | Máy | Làm gì |
|---|---|---|---|
| `/medsci-project:academic-aio` | kỹ năng | Mac | [MedSci] Tối ưu bài báo AI y tế cho các công cụ tìm kiếm học thuật (Perplexity, Elicit, Consensus) — tiêu đề, tóm tắt, hộp điểm chính. Gắn với TRIPOD+AI, CLAIM 2024, STARD-AI. Dùng khi muốn bài dễ được tìm thấy. Từ khoá: GEO, discoverabi… |
| `/medsci-project:add-journal` | kỹ năng | Mac | [MedSci] Thêm một tạp chí mới vào kho hồ sơ tạp chí của bộ công cụ. Dùng khi tạp chí bác sĩ nhắm tới chưa có sẵn. Từ khoá: journal profile. |
| `/medsci-project:analyze-stats` | kỹ năng | Mac | [MedSci] Phân tích thống kê cho bài báo y khoa, sinh mã R/Python tái lập được kèm bảng và hình đạt chuẩn đăng bài. Bao phủ độ chính xác chẩn đoán, độ đồng thuận, phân tích gộp, sống còn, hồi quy, điểm xu hướng. Dùng sau khi dữ liệu đã kh… |
| `/medsci-project:architecture-zoo` | kỹ năng | Mac | [MedSci — AI hình ảnh] Chọn kiến trúc mô hình cho câu hỏi nghiên cứu hình ảnh y khoa, kèm bài báo gốc và trường hợp nên dùng. Dùng trước khi bắt tay dựng mô hình. Từ khoá: model architecture. |
| `/medsci-project:author-strategy` | kỹ năng | Mac | [MedSci] Phân tích hồ sơ công bố của một tác giả trên PubMed: phân loại loại nghiên cứu, vẽ biểu đồ, gợi ý chiến lược. Dùng khi tìm hiểu một người sắp hợp tác, hoặc tự soi hồ sơ của mình. Từ khoá: author profile. |
| `/medsci-project:batch-cohort` | kỹ năng | Mac | [MedSci] Sinh N script phân tích từ một khuôn phương pháp × nhiều cặp phơi nhiễm–kết cục. Dùng khi chạy cùng một phương pháp cho nhiều biến. Từ khoá: batch analysis. |
| `/medsci-project:calc-sample-size` | kỹ năng | Mac | [MedSci] Tính CỠ MẪU theo cây quyết định, sinh mã R/Python tái lập được và đoạn văn biện minh cho hồ sơ đạo đức. Dùng khi cần con số nhanh; đề tài chính thức phải qua agent `co-mau-nghien-cuu` vì đó là cổng G3 có kiểm nguồn effect size. … |
| `/medsci-project:check-reporting` | kỹ năng | Mac | [MedSci] Kiểm bản thảo theo CHUẨN BÁO CÁO — hỗ trợ 47 chuẩn: STROBE, CONSORT, STARD, TRIPOD+AI, PRISMA, SPIRIT, CARE, CHEERS, COREQ… và các công cụ nguy cơ sai lệch (QUADAS-2, RoB 2, ROBINS-I, PROBAST). Chấm từng mục ĐỦ/THIẾU/MỘT PHẦN. D… |
| `/medsci-project:clean-data` | kỹ năng | Mac | [MedSci] Làm sạch dữ liệu theo 3 bước có bác sĩ duyệt từng bước: khảo sát → gắn cờ → sinh mã. Dùng khi dữ liệu có giá trị thiếu, ngoại lai, trùng lặp. KHÔNG tự sửa dữ liệu — mọi quyết định phải bác sĩ xác nhận. Từ khoá: data cleaning. |
| `/medsci-project:contribute` | kỹ năng | Mac | [MedSci] Gửi phần bác sĩ tự sửa ngược lại cho dự án gốc, có quét dữ liệu bệnh nhân trước khi gửi và cho xem từng dòng. Dùng khi muốn đóng góp cải tiến. Từ khoá: contribute. |
| `/medsci-project:cross-national` | kỹ năng | Mac | [MedSci] Nghiên cứu SO SÁNH ĐA QUỐC GIA dùng các bộ khảo sát song song (KNHANES, NHANES, CHNS): hài hoà biến số, phân tích có trọng số, bảng so sánh. Dùng cho đề tài so sánh quốc tế. Từ khoá: cross-national. |
| `/medsci-project:define-variables` | kỹ năng | Mac | [MedSci] Định nghĩa BIẾN SỐ có dẫn nguồn y văn: ngưỡng cắt, cách mã hoá, ánh xạ sang tên biến trong cơ sở dữ liệu. Dùng khi cần tránh việc tự đặt định nghĩa kiểu hình rồi bị phản biện bác. Từ khoá: variable operationalization. |
| `/medsci-project:deidentify` | kỹ năng | Mac | [MedSci] Khử định danh dữ liệu nghiên cứu bằng công cụ chạy CỤC BỘ, có gói nhận diện cho 10 quốc gia. Dùng TRƯỚC khi đưa dữ liệu cho bất kỳ mô hình AI nào — công cụ này không gọi mạng, không AI nào chạm dữ liệu thô. Từ khoá: de-identific… |
| `/medsci-project:design-ai-benchmarking` | kỹ năng | Mac | [MedSci — AI hình ảnh] Thiết kế nghiên cứu SO SÁNH AI với hội đồng chuyên gia: định nghĩa nhánh so sánh, thang chấm có mỏ neo, độ đồng thuận giữa người chấm. Dùng TRƯỚC khi thu thập dữ liệu. Từ khoá: AI vs expert benchmarking. |
| `/medsci-project:design-study` | kỹ năng | Mac | [MedSci] Thẩm định THIẾT KẾ nghiên cứu trước khi thu thập dữ liệu: xác định đơn vị phân tích, logic chọn cohort, nguy cơ rò rỉ dữ liệu, cách chọn nhóm chứng, chiến lược kiểm định. Dùng ở bước đầu, TRƯỚC khi viết đề cương; đề tài chính th… |
| `/medsci-project:explainability` | kỹ năng | Mac | [MedSci — AI hình ảnh] Làm hoặc thẩm định phần GIẢI THÍCH mô hình (Grad-CAM, saliency) đạt mức phản biện đòi hỏi: bắt buộc có phép thử độ tin cậy và chỉ số định lượng, không chỉ khoe vài ảnh đẹp. Dùng khi bài cần phần diễn giải. Từ khoá:… |
| `/medsci-project:fill-icmje-coi` | kỹ năng | Mac | [MedSci] Sinh hàng loạt phiếu KHAI XUNG ĐỘT LỢI ÍCH theo mẫu ICMJE cho từng tác giả. Dùng khi chuẩn bị nộp bài nhiều tác giả — mỗi người chỉ cần xem và ký. Từ khoá: ICMJE COI. |
| `/medsci-project:fill-protocol` | kỹ năng | Mac | [MedSci] Điền nội dung vào MẪU WORD của cơ quan (đề cương, hồ sơ đạo đức, đề tài) mà giữ nguyên định dạng, bảng biểu, phông chữ. Dùng khi đơn vị bắt nộp đúng biểu mẫu có sẵn. Từ khoá: Word template. |
| `/medsci-project:find-cohort-gap` | kỹ năng | Mac | [MedSci] Tìm KHOẢNG TRỐNG nghiên cứu trong một cơ sở dữ liệu cohort: soi thế mạnh dữ liệu, đối chiếu chuyên môn chủ nhiệm, quét mức bão hoà y văn, xuất danh sách đề tài xếp hạng. Dùng khi có sẵn kho dữ liệu mà chưa biết làm gì. Từ khoá: … |
| `/medsci-project:find-journal` | kỹ năng | Mac | [MedSci] Gợi ý TẠP CHÍ phù hợp cho bản thảo: đối chiếu phạm vi, chính sách khai báo AI, khả năng được nhận, kèm phương án dự phòng nếu bị từ chối. Dùng khi chuẩn bị nộp. Chỉ số ảnh hưởng và phí đăng bài có thể đã cũ — phải kiểm lại trên … |
| `/medsci-project:fulltext-retrieval` | kỹ năng | Mac | [MedSci] Tải hàng loạt PDF toàn văn TRUY CẬP MỞ theo DOI qua Unpaywall, PMC, OpenAlex, Crossref. Dùng khi đã có danh sách DOI và cần đọc toàn văn. Chỉ lấy bài mở, hợp pháp. Từ khoá: open access PDF. |
| `/medsci-project:generate-codebook` | kỹ năng | Mac | [MedSci] Sinh TỪ ĐIỂN DỮ LIỆU từ một file dữ liệu: mọi biến kèm kiểu, phân bố, tỷ lệ thiếu. Dùng ngay khi nhận bộ dữ liệu mới, trước khi phân tích. Biến mã hoá không rõ nghĩa được gắn cờ chứ không đoán bừa. Từ khoá: codebook, data dictio… |
| `/medsci-project:grant-builder` | kỹ năng | Mac | [MedSci] Viết đề xuất ĐỀ TÀI/TÀI TRỢ: ý nghĩa, tính mới, cách tiếp cận, mốc tiến độ, phân vai nhóm nghiên cứu. Dùng khi xin kinh phí. Từ khoá: grant proposal. |
| `/medsci-project:humanize` | kỹ năng | Mac | [MedSci] Phát hiện và xoá 27 dấu hiệu văn phong máy trong bản thảo và thư phản hồi phản biện, giới hạn mức can thiệp để không đổi nội dung khoa học. Dùng sau khi đã viết xong. Từ khoá: AI writing patterns. |
| `/medsci-project:intake-project` | kỹ năng | Mac | [MedSci] Tiếp nhận và chuẩn hoá một đề tài mới: phân loại, tóm tắt hiện trạng, chỉ ra thứ còn thiếu, dựng file ghi nhớ cho đề tài. Dùng khi bắt đầu đề tài mới. Từ khoá: project intake. |
| `/medsci-project:lit-sync` | kỹ năng | Mac | [MedSci] Đồng bộ tài liệu tham khảo từ file .bib sang Zotero và ghi chú Obsidian. Dùng khi bác sĩ quản lý y văn bằng hai công cụ đó. Từ khoá: Zotero, Obsidian. |
| `/medsci-project:ma-scout` | kỹ năng | Mac | [MedSci] Tìm CHỦ ĐỀ cho phân tích gộp và chấm tính khả thi, trước khi viết đề cương. Dùng khi muốn làm tổng quan hệ thống nhưng chưa chọn được đề tài. Từ khoá: meta-analysis topic. |
| `/medsci-project:make-figures` | kỹ năng | Mac | [MedSci] Vẽ hình đạt chuẩn đăng bài: đường cong ROC, biểu đồ rừng, sơ đồ CONSORT/STARD/PRISMA, đường Kaplan-Meier, Bland-Altman, ma trận nhầm lẫn, tóm tắt bằng hình. Dùng khi chuẩn bị hình cho bản thảo. Từ khoá: publication figures. |
| `/medsci-project:manage-project` | kỹ năng | Mac | [MedSci] Quản lý tiến độ đề tài: dựng cấu trúc thư mục, theo dõi từng giai đoạn viết, sinh danh mục kiểm và mốc thời gian lùi từ hạn nộp. Dùng khi chạy nhiều đề tài song song. Từ khoá: project management. |
| `/medsci-project:manage-refs` | kỹ năng | Mac | [MedSci] Xử lý trích dẫn khi nộp bài: kiểm khoá trích dẫn, dựng danh mục theo định dạng tạp chí, chuyển đổi kiểu đánh số, chèn trường Zotero. Dùng ở khâu hoàn thiện bản thảo. Từ khoá: citation rendering. |
| `/medsci-project:meta-analysis` | kỹ năng | Mac | [MedSci] Dây chuyền TỔNG QUAN HỆ THỐNG và PHÂN TÍCH GỘP: đăng ký PROSPERO, chiến lược tìm, sàng lọc, trích xuất, nguy cơ sai lệch (QUADAS-2/ROBINS-I), tổng hợp và báo cáo PRISMA. Dùng cho đề tài tổng quan hệ thống. Từ khoá: meta-analysis… |
| `/medsci-project:mllm-eval` | kỹ năng | Mac | [MedSci — AI hình ảnh] Thiết kế hoặc thẩm định khung đánh giá mô hình ngôn ngữ lớn trên nhiệm vụ lâm sàng (sinh báo cáo, hỏi đáp hình ảnh). Soi cả nguy cơ mô hình đã học thuộc bộ kiểm định công khai. Dùng khi đánh giá LLM y tế. Từ khoá: … |
| `/medsci-project:model-card` | kỹ năng | Mac | [MedSci — AI hình ảnh] Sinh tài liệu bắt buộc đi kèm mô hình: mục đích dùng, chỉ số, giới hạn đã biết. Dùng khi công bố hoặc bàn giao mô hình. Từ khoá: model card. |
| `/medsci-project:model-evaluation` | kỹ năng | Mac | [MedSci — AI hình ảnh] Tính và báo cáo chỉ số trên tập kiểm định độc lập cho đúng loại nhiệm vụ. Dùng sau khi huấn luyện xong. Từ khoá: held-out metrics. |
| `/medsci-project:model-scaffold` | kỹ năng | Mac | [MedSci — AI hình ảnh] Dựng sẵn kho mã huấn luyện PyTorch chạy được và tái lập được. Dùng khi bắt đầu huấn luyện mô hình. Từ khoá: training scaffold. |
| `/medsci-project:model-sourcing` | kỹ năng | Mac | [MedSci — AI hình ảnh] Thẩm định mô hình bên thứ ba mà nghiên cứu định dùng: kho mã nào, bản phát hành nào, giấy phép ra sao. Dùng trước khi dựa vào mô hình có sẵn. Từ khoá: model vetting. |
| `/medsci-project:model-validation` | kỹ năng | Mac | [MedSci — AI hình ảnh] Thiết kế hoặc thẩm định nghiên cứu KIỂM ĐỊNH LÂM SÀNG cho mô hình. Dùng khi muốn chứng minh mô hình dùng được trên bệnh nhân thật. Từ khoá: clinical validation. |
| `/medsci-project:obsidian-paper-vault` | kỹ năng | Mac | [MedSci] Biến thư mục PDF nghiên cứu thành kho tri thức Obsidian: ghi chú y văn cùng khuôn có frontmatter, link nhúng PDF, ghi chú khái niệm liên kết chéo. Dùng khi cần chuyển loạt PDF thành ghi chú Obsidian, tóm nhiều bài theo một mẫu, … |
| `/medsci-project:orchestrate` | kỹ năng | Mac | [MedSci] Điều phối chung của bộ MedSci — nhận yêu cầu mơ hồ rồi chuyển tới đúng skill. Dùng khi chưa biết nên gọi skill nào trong bộ này. Từ khoá: medsci router. |
| `/medsci-project:peer-review` | kỹ năng | Mac | [MedSci] Trợ lý viết BẢN NHẬN XÉT PHẢN BIỆN cho tạp chí, theo khung của từng tạp chí. Dùng khi bác sĩ được mời phản biện cho tạp chí. Khác skill `peer-review` riêng của bác sĩ (rà bản thảo của chính mình trước khi nộp). Từ khoá: peer rev… |
| `/medsci-project:polish-language` | kỹ năng | Mac | [MedSci] Gọt tiếng Anh học thuật cho người không nói tiếng Anh bản ngữ, thống nhất thuật ngữ toàn bài. Dùng ở khâu cuối trước khi nộp tạp chí quốc tế. Từ khoá: ESL polish. |
| `/medsci-project:preprocess-imaging` | kỹ năng | Mac | [MedSci — AI hình ảnh] Thiết kế hoặc thẩm định khâu chuẩn bị dữ liệu ảnh (DICOM/NIfTI). Dùng trước khi huấn luyện — đây là chỗ hay sinh rò rỉ dữ liệu. Từ khoá: imaging preprocessing. |
| `/medsci-project:present-paper` | kỹ năng | Mac | [MedSci] Chuẩn bị BÀI TRÌNH BÀY học thuật từ một bài báo (sinh hoạt khoa học, hội thảo). Dùng khi phải báo cáo journal club hay hội nghị. Từ khoá: academic presentation. |
| `/medsci-project:profile-imaging` | kỹ năng | Mac | [MedSci — AI hình ảnh] Khảo sát bộ dữ liệu ảnh TRƯỚC mọi quyết định mô hình hoá: thông số chụp, phân bố, mất cân bằng nhãn. Dùng ngay khi nhận dữ liệu ảnh. Từ khoá: dataset profiling. |
| `/medsci-project:publish-skill` | kỹ năng | Mac | [MedSci] Chuyển một skill cá nhân thành skill chia sẻ được, có quét thông tin định danh trước. Dùng khi muốn đóng gói quy trình riêng để dùng chung. Từ khoá: publish skill. |
| `/medsci-project:radiomics-ml` | kỹ năng | Mac | [MedSci] Làm hoặc thẩm định nghiên cứu radiomics / học máy trên dữ liệu bảng. Dùng khi rút đặc trưng từ hình ảnh hoặc dữ liệu lâm sàng để dự báo. Từ khoá: radiomics. |
| `/medsci-project:render-pdf-doc` | kỹ năng | Mac | [MedSci] Kết xuất tài liệu Markdown học thuật thành PDF chất lượng in. Dùng ở khâu cuối khi cần bản PDF đẹp; không dùng cho bản thảo có danh mục tài liệu tham khảo — loại đó phải đi qua công cụ quản lý trích dẫn. Từ khoá: PDF rendering. |
| `/medsci-project:replicate-study` | kỹ năng | Mac | [MedSci] Lặp lại phương pháp của một nghiên cứu đã công bố trên cơ sở dữ liệu khác. Dùng khi muốn kiểm chứng kết quả người khác trên dữ liệu của mình. Từ khoá: replication. |
| `/medsci-project:review-paper` | kỹ năng | Mac | [MedSci] Dựng khung và viết TỔNG QUAN y văn: tường thuật, phạm vi (PRISMA-ScR) hoặc hệ thống. Dùng khi viết bài tổng quan. Từ khoá: literature review. |
| `/medsci-project:revise` | kỹ năng | Mac | [MedSci] Đọc góp ý phản biện và sinh THƯ PHẢN HỒI có cấu trúc từng điểm một. Dùng khi nhận quyết định 'sửa và nộp lại'. Từ khoá: response to reviewers. |
| `/medsci-project:search-lit` | kỹ năng | Mac | [MedSci] Tìm y văn trên PubMed, Semantic Scholar và quản lý trích dẫn. Dùng khi cần quét rộng; câu hỏi lâm sàng để ra quyết định vẫn nên qua agent `tra-cuu-chung-cu`. Từ khoá: literature search. |
| `/medsci-project:self-review` | kỹ năng | Mac | [MedSci] Tự rà bản thảo của chính mình bằng con mắt phản biện TRƯỚC khi nộp. Dùng như bước cuối trước khi gửi tạp chí. Từ khoá: pre-submission review. |
| `/medsci-project:setup-medsci` | kỹ năng | Mac | [MedSci] Kiểm môi trường chạy của bộ MedSci: Python, R, Node đã đủ chưa. Dùng khi cài lần đầu hoặc khi một skill báo lỗi thiếu công cụ. Từ khoá: setup, diagnostics. |
| `/medsci-project:sync-submission` | kỹ năng | Mac | [MedSci] Soi độ lệch giữa bản thảo gốc và bộ file đem nộp, rồi lập danh mục hồ sơ nộp. Dùng ngay trước khi bấm nộp. Từ khoá: submission manifest. |
| `/medsci-project:uncertainty-imaging` | kỹ năng | Mac | [MedSci — AI hình ảnh] Thiết kế hoặc thẩm định phần lượng hoá ĐỘ BẤT ĐỊNH và phát hiện dữ liệu ngoài phân bố. Dùng khi mô hình sắp dùng trên lâm sàng — cần biết khi nào nó không chắc. Từ khoá: uncertainty, OOD. |
| `/medsci-project:verify-refs` | kỹ năng | Mac | [MedSci] Kiểm tài liệu tham khảo đối chiếu PubMed và CrossRef, phát hiện trích dẫn BỊA. CHỈ ĐỌC, không sửa. Dùng trước khi nộp; bản của bác sĩ là agent `kiem-chung-trich-dan` (có tra bài bị rút). Từ khoá: reference verification. |
| `/medsci-project:version-dataset` | kỹ năng | Mac | [MedSci] Đánh phiên bản bộ dữ liệu bằng mã băm nội dung để tái lập được kết quả. Dùng khi dữ liệu còn thay đổi mà đã bắt đầu phân tích. Từ khoá: dataset versioning. |
| `/medsci-project:write-paper` | kỹ năng | Mac | [MedSci] Viết bài báo trọn gói theo 8 giai đoạn IMRAD, từ dàn ý tới bản nộp. Dùng cho bài không đi qua dây chuyền G của bác sĩ; đề tài chính thức nên dùng agent `viet-ban-thao`. Từ khoá: paper writing, IMRAD. |
| `/medsci-project:write-protocol` | kỹ năng | Mac | [MedSci] Sinh ĐỀ CƯƠNG nộp Hội đồng Đạo đức gồm 4 phần lõi. Dùng khi cần bản nháp nhanh; hồ sơ nộp thật phải qua agent `dao-duc-dang-ky` (cổng G2) vì nó gắn Helsinki, ICH-GCP và bản đồng thuận. Từ khoá: IRB protocol. |

### academic-research-skills  (58)

| Gọi bằng | Loại | Máy | Làm gì |
|---|---|---|---|
| `agent abstract_bilingual_agent` | agent | Mac | [ARS] Agent viết và dịch tóm tắt sang ngôn ngữ đích theo yêu cầu tạp chí. Từ khoá: bilingual abstract. |
| `agent argument_builder_agent` | agent | Mac | [ARS] Agent dựng lập luận cốt lõi và mạch suy luận của bài. Từ khoá: argument builder. |
| `agent bibliography_agent` | agent | Mac | [ARS] Agent tìm, chú giải và định dạng danh mục tài liệu tham khảo. Từ khoá: bibliography. |
| `agent citation_compliance_agent` | agent | Mac | [ARS] Agent đối chiếu trích dẫn với yêu cầu định dạng của tạp chí và gắn cờ chỗ sai. Từ khoá: citation compliance. |
| `agent claim_ref_alignment_audit_agent` | agent | Mac | [ARS] Agent soi từng khẳng định có trích dẫn xem có ĐÚNG với nội dung tài liệu gốc không — bắt lỗi trích sai ý. Từ khoá: claim-reference alignment. |
| `agent collaboration_depth_agent` | agent | Mac | [ARS] Agent chấm mức độ hợp tác giữa người và AI trong quá trình làm bài. Từ khoá: collaboration depth. |
| `agent compliance_agent` | agent | Mac | [ARS] Agent kiểm tuân thủ chuẩn báo cáo tại các cổng liêm chính giữa chừng. Từ khoá: compliance, PRISMA. |
| `agent devils_advocate_agent` | agent | Mac | [ARS] Agent phản biện ngược: thách thức giả định và thử phá mạch lập luận. Từ khoá: devil's advocate. |
| `agent devils_advocate_reviewer_agent` | agent | Mac | [ARS] Agent phản biện ngược trong vai người bình duyệt: công kích lập luận cốt lõi. Từ khoá: devil's advocate reviewer. |
| `agent domain_reviewer_agent` | agent | Mac | [ARS] Agent phản biện số 2: chấm độ chính xác chuyên ngành. Từ khoá: domain reviewer. |
| `agent draft_writer_agent` | agent | Mac | [ARS] Agent viết bản thảo đầy đủ theo từng mục từ dàn ý đã chốt. Từ khoá: draft writer. |
| `agent editor_in_chief_agent` | agent | Mac | [ARS] Agent rà soát ở mức tạp chí Q1, ra phán quyết Nhận/Từ chối kèm góp ý cụ thể. Từ khoá: editorial verdict. |
| `agent editorial_synthesizer_agent` | agent | Mac | [ARS] Agent gộp mọi báo cáo phản biện thành một thư quyết định thống nhất. Từ khoá: editorial synthesis. |
| `agent eic_agent` | agent | Mac | [ARS] Agent giữ ghế tổng biên tập: chấm mức phù hợp tạp chí, tính mới và chất lượng chung. Từ khoá: editor-in-chief. |
| `agent ethics_review_agent` | agent | Mac | [ARS] Agent tự rà đạo đức nghiên cứu — KHÔNG thay Hội đồng Đạo đức. Hồ sơ nộp hội đồng dùng agent `dao-duc-dang-ky`. Từ khoá: ethics self-check. |
| `agent field_analyst_agent` | agent | Mac | [ARS] Agent nhận diện lĩnh vực của bài rồi cấu hình đội phản biện cho phù hợp. Từ khoá: field analyst. |
| `agent formatter_agent` | agent | Mac | [ARS] Agent định dạng bản thảo cuối theo yêu cầu của tạp chí đích. Từ khoá: formatting. |
| `agent intake_agent` | agent | Mac | [ARS] Agent phỏng vấn đầu vào để dựng hồ sơ cấu hình cho bài báo. Từ khoá: intake. |
| `agent integrity_verification_agent` | agent | Mac | [ARS] Agent kiểm mọi tài liệu, trích dẫn và số liệu trước khi nộp. Bản y khoa xác minh PMID/DOI thật là `kiem-chung-trich-dan`. Từ khoá: integrity verification. |
| `agent literature_strategist_agent` | agent | Mac | [ARS] Agent thiết kế chiến lược tìm y văn và chọn nguồn. Từ khoá: literature strategy. |
| `agent meta_analysis_agent` | agent | Mac | [ARS] Agent tổng hợp định lượng: tính cỡ hiệu ứng, đánh giá tính không đồng nhất. Bản y khoa đầy đủ hơn là agent `meta-phan-tich`. Từ khoá: meta-analysis. |
| `agent methodology_reviewer_agent` | agent | Mac | [ARS] Agent phản biện số 1: chấm tính vững của phương pháp và thiết kế nghiên cứu. Từ khoá: methodology reviewer. |
| `agent monitoring_agent` | agent | Mac | [ARS] Agent theo dõi y văn mới công bố sau khi nghiên cứu đã xong. Từ khoá: literature monitoring. |
| `agent peer_reviewer_agent` | agent | Mac | [ARS] Agent đóng vai phản biện để tìm điểm yếu trước khi nộp. Từ khoá: peer reviewer. |
| `agent perspective_reviewer_agent` | agent | Mac | [ARS] Agent phản biện số 3: chấm mức liên ngành và tác động rộng hơn. Từ khoá: perspective reviewer. |
| `agent pipeline_orchestrator_agent` | agent | Mac | [ARS] Agent điều phối toàn bộ dây chuyền nghiên cứu học thuật nhiều bước. Từ khoá: pipeline orchestrator. |
| `agent report_compiler_agent` | agent | Mac | Agent soạn báo cáo học thuật theo chuẩn APA 7.0 từ kết quả nghiên cứu. Chạy ở Giai đoạn 4 và 6 của dây chuyền ARS. Từ khoá: APA report drafting. |
| `agent research_architect_agent` | agent | Mac | Agent thiết kế KHUNG PHƯƠNG PHÁP: chọn hệ hình nghiên cứu, phương pháp, chiến lược dữ liệu và khung phân tích. Cho đề tài y khoa thì thiet-ke-nghien-cuu của bác sĩ đúng chuẩn hơn. Từ khoá: methodology blueprint. |
| `agent research_question_agent` | agent | Mac | [ARS] Agent biến chủ đề mơ hồ thành câu hỏi nghiên cứu rõ, chấm theo FINER. Với đề tài y khoa nên dùng agent `cau-hoi-nghien-cuu` (có PICO và cổng G0). Từ khoá: research question. |
| `agent revision_coach_agent` | agent | Mac | [ARS] Agent phân tích góp ý phản biện thành kế hoạch sửa bài có cấu trúc. Từ khoá: revision coach. |
| `agent risk_of_bias_agent` | agent | Mac | [ARS] Agent đánh giá nguy cơ sai lệch bằng RoB 2 (thử nghiệm ngẫu nhiên) và ROBINS-I (nghiên cứu quan sát). Trùng vai với `tham-dinh-grade-nnt` của bác sĩ — ưu tiên agent EBM vì có gắn cổng. Từ khoá: risk of bias. |
| `agent socratic_mentor_agent` | agent | Mac | [ARS] Agent dẫn dắt tác giả bằng câu hỏi Socratic để mài sắc lập luận. Từ khoá: Socratic mentor. |
| `agent source_verification_agent` | agent | Mac | [ARS] Agent chấm mức bằng chứng, phát hiện tạp chí săn mồi và kiểm chứng khẳng định. Từ khoá: source verification, predatory journal. |
| `agent state_tracker_agent` | agent | Mac | [ARS] Agent theo dõi trạng thái dây chuyền và lịch sử phiên làm việc. Từ khoá: state tracker. |
| `agent structure_architect_agent` | agent | Mac | [ARS] Agent thiết kế bố cục các mục và dàn ý chi tiết trước khi viết. Từ khoá: structure architect. |
| `agent synthesis_agent` | agent | Mac | Agent TỔNG HỢP xuyên nguồn: gộp phát hiện, xử lý mâu thuẫn giữa các bằng chứng và chỉ ra khoảng trống kiến thức. Từ khoá: synthesis, evidence conflict. |
| `agent timeline_extraction_agent` | agent | Mac | [ARS] Agent rút mốc thời gian và nguồn gốc trích dẫn của từng tài liệu. Từ khoá: timeline extraction. |
| `agent visualization_agent` | agent | Mac | [ARS] Agent mô tả đặc tả hình và biểu đồ đạt chuẩn công bố. Từ khoá: figure specification. |
| `/ars-3w` | lệnh | Mac | Quét bài báo theo ba trục TẠI SAO / LÀM THẾ NÀO / CÁI GÌ. Dùng khi cần so sánh nhanh nhiều bài, nhẹ hơn tổng quan tài liệu. Từ khoá: ARS three-way scan. |
| `/ars-abstract` | lệnh | Mac | Viết TÓM TẮT song ngữ + từ khoá. Dùng khi chuẩn bị nộp bài. LƯU Ý: song ngữ ở đây là Trung phồn thể + Anh (zh-TW/EN), KHÔNG phải Việt–Anh. Từ khoá: ARS abstract. |
| `/ars-cache-invalidate` | lệnh | Mac | Xoá kết quả kiểm trích dẫn đã lưu tạm của một hoặc nhiều tài liệu, buộc kiểm lại từ đầu. Dùng khi nghi kết quả cũ đã lỗi thời. Từ khoá: ARS cache invalidate. |
| `/ars-citation-check` | lệnh | Mac | Xuất BÁO CÁO LỖI TRÍCH DẪN cho bản thảo. Dùng khi rà bài trước khi nộp; với bài y khoa hãy dùng agent `kiem-chung-trich-dan` vì nó xác minh PMID/DOI thật và tra bài bị rút. Từ khoá: ARS citation check. |
| `/ars-disclosure` | lệnh | Mac | Soạn câu KHAI BÁO SỬ DỤNG AI theo yêu cầu riêng của từng tạp chí. Dùng khi nộp bài — ICMJE Mục V bắt buộc khai. Từ khoá: ARS AI disclosure. |
| `/ars-format-convert` | lệnh | Mac | Chuyển bản thảo qua lại giữa LaTeX / DOCX / PDF / Markdown. Dùng khi tạp chí đòi định dạng khác. Từ khoá: ARS format convert. |
| `/ars-full` | lệnh | Mac | Chạy TRỌN dây chuyền bài báo học thuật: tra cứu → viết → bình duyệt → sửa → hoàn thiện. Dùng khi muốn chạy một mạch; tốn token nhất trong bộ ARS. Từ khoá: ARS full pipeline. |
| `/ars-lit-review` | lệnh | Mac | Dựng THƯ MỤC CÓ CHÚ GIẢI trình bày theo dạng bài báo. Dùng khi cần phần tổng quan tài liệu; tổng quan hệ thống theo PRISMA thì dùng agent tong-quan-y-van. Từ khoá: ARS lit-review. |
| `/ars-mark-read` | lệnh | Mac | Đánh dấu 'người đã đọc thật' cho một hoặc nhiều tài liệu trích dẫn. Dùng khi cần phân biệt bài đã đọc toàn văn với bài chỉ đọc tóm tắt. Từ khoá: ARS mark read. |
| `/ars-outline` | lệnh | Mac | Dựng DÀN Ý chi tiết kèm bản đồ bằng chứng cho từng mục, KHÔNG viết thành văn. Dùng khi muốn chốt khung trước khi viết. Từ khoá: ARS outline. |
| `/ars-plan` | lệnh | Mac | Lập kế hoạch bài viết theo lối HỎI ĐÁP SOCRATIC, đi từng chương một. Dùng khi chưa rõ nên viết gì, cần người hỏi ngược để làm rõ ý. Từ khoá: ARS plan mode. |
| `/ars-rebuttal-audit` | lệnh | Mac | Soi lại THƯ PHẢN HỒI đã viết xem đã trả lời hết từng ý phản biện chưa (chỉ góp ý, không viết thay). Dùng trước khi gửi thư đi. Từ khoá: ARS rebuttal audit. |
| `/ars-reviewer` | lệnh | Mac | Chạy hội đồng bình duyệt mô phỏng đầy đủ trên bản thảo. Dùng khi muốn biết bài sẽ bị chê ở đâu trước khi nộp. Từ khoá: ARS reviewer panel. |
| `/ars-revision` | lệnh | Mac | Sinh BẢN SỬA của bản thảo kèm phần trả lời góp ý (R&R). Dùng sau khi đã có nhận xét của phản biện. Từ khoá: ARS revision. |
| `/ars-revision-coach` | lệnh | Mac | Phân tích góp ý của phản biện thành LỘ TRÌNH SỬA BÀI + khung thư phản hồi. Dùng ngay khi vừa nhận quyết định 'sửa và nộp lại'. Từ khoá: ARS revision coach. |
| `/ars-unmark-read` | lệnh | Mac | Gỡ dấu 'đã đọc' đã gắn trước đó cho tài liệu trích dẫn. Dùng khi đánh dấu nhầm. Từ khoá: ARS unmark read. |
| `/academic-research-skills:academic-paper` | kỹ năng | Mac | Dây chuyền VIẾT BÀI BÁO HỌC THUẬT tổng quát (12 agent, 11 chế độ). Dùng khi viết bài NGOÀI y khoa; bài y khoa nên dùng agent `viet-ban-thao` vì bám CONSORT/STROBE. Từ khoá: academic paper, APA. |
| `/academic-research-skills:academic-paper-reviewer` | kỹ năng | Mac | Mô phỏng HỘI ĐỒNG BÌNH DUYỆT nhiều góc nhìn: 1 tổng biên tập + 3 phản biện + người bảo vệ, mỗi vai một tính cách khác nhau. Dùng khi muốn thử phản biện bản thảo trước khi nộp thật. Từ khoá: peer review simulation. |
| `/academic-research-skills:academic-pipeline` | kỹ năng | Mac | Điều phối TRỌN VÒNG bài báo học thuật: tra cứu → viết → kiểm liêm chính → bình duyệt → sửa → bình duyệt lại. Dùng khi muốn chạy một mạch thay vì gọi từng chế độ. Tốn nhiều token (một lần chạy đầy đủ khoảng 4–6 USD). Từ khoá: full pipeline. |
| `/academic-research-skills:deep-research` | kỹ năng | Mac | Đội 13 agent NGHIÊN CỨU SÂU cho bất kỳ chủ đề nào, 8 chế độ (nghiên cứu đầy đủ, tóm lược nhanh, so sánh…). Dùng cho chủ đề ngoài y khoa hoặc cần quét rộng; câu hỏi lâm sàng vẫn nên đi qua tra-cuu-chung-cu để có PMID/DOI. Từ khoá: deep re… |

### user-commands  (53)

| Gọi bằng | Loại | Máy | Làm gì |
|---|---|---|---|
| `/cap-nhat-chung-cu` | lệnh | Mac | Cập nhật chứng cứ cho một vấn đề lâm sàng — dựng dashboard rồi xuất BỘ NĂM (dashboard · bản đọc · Word · Word-dạng-HTML · PDF giữ màu) |
| `/chay-thong-ke` | lệnh | Mac | Chạy phân tích theo đúng SAP đã khoá, trên dữ liệu đã khoá (cổng G6) |
| `/chon-tap-chi` | lệnh | Mac | Gợi ý tạp chí phù hợp kèm chính sách khai báo AI và phương án dự phòng nếu bị từ chối |
| `/cong-cu-gi` | lệnh | Mac | Tra xem việc mình cần làm thì gọi công cụ nào — tìm trong danh mục 532 skill/lệnh/agent đã Việt hoá |
| `/dang-ky-tong-quan` | lệnh | Mac | Soạn nội dung đăng ký PROSPERO cho tổng quan hệ thống / phân tích gộp |
| `/dat-bien-so` | lệnh | Mac | Xác định bộ biến số đầy đủ cho đề tài, xuất được sang CRF/REDCap |
| `/dat-cau-hoi-nghien-cuu` | lệnh | Mac | Chuyển vấn đề lâm sàng thành câu hỏi PICO/PECO rõ, kèm kết cục và kiểm khả thi FINER (cổng G0) |
| `/de-cuong-thu-nghiem-lam-sang` | lệnh | Mac | Soạn đề cương thử nghiệm lâm sàng theo chuẩn quốc tế (SPIRIT/ICH-GCP) |
| `/dien-giai-so-lieu` | lệnh | Mac | Chuyển con số thống kê thành ý nghĩa lâm sàng, so với y văn — cầu nối sang phần Bàn luận |
| `/gop-tron-goi` | lệnh | Mac | Chạy TRỌN dây chuyền phân tích gộp meta-pipe: chủ đề → PICO → tìm → sàng lọc → trích xuất → thống kê → bản thảo |
| `/got-tieng-anh` | lệnh | Mac | Gọt tiếng Anh học thuật cho người không nói tiếng Anh bản ngữ, thống nhất thuật ngữ |
| `/in-to-dan-do` | lệnh | Mac | Sinh tờ dặn dò khổ A5 cho bệnh nhân — văn phong dễ hiểu, không thuật ngữ khó |
| `/kham-ca-benh` | lệnh | Mac | Khám một ca bệnh theo trọn 5 bước EBM — nêu cờ đỏ ngay, dừng ở Cổng A trước khi áp dụng cho bệnh nhân |
| `/khoa-du-lieu` | lệnh | Mac | Làm sạch, khử định danh và KHOÁ cơ sở dữ liệu trước khi phân tích (cổng G5) |
| `/khu-dinh-danh` | lệnh | Mac | Khử định danh bệnh án trước khi đưa vào nghiên cứu — xoá/thay PHI, chạy ngay trên máy |
| `/kiem-chuan-bao-cao` | lệnh | Mac | Đối chiếu bản thảo với 47 chuẩn báo cáo (STROBE, CONSORT, PRISMA, STARD, TRIPOD+AI…) |
| `/kiem-prisma` | lệnh | Mac | Kiểm chất lượng mức tạp chí lớn: PRISMA/MOOSE, Hartung-Knapp, khoảng dự báo, bảng GRADE SoF |
| `/kiem-trich-dan` | lệnh | Mac | Cổng chống trích dẫn ma — xác minh mọi PMID/DOI có thật, đúng nội dung, chưa bị rút |
| `/lam-bang-mot` | lệnh | Mac | Dựng Bảng 1 (đặc điểm nền của quần thể nghiên cứu) từ dữ liệu |
| `/lam-ho-so-dao-duc` | lệnh | Mac | Soạn hồ sơ Hội đồng Đạo đức, phiếu đồng thuận, đăng ký nghiên cứu và kế hoạch dữ liệu (cổng G2) |
| `/lam-nghien-cuu` | lệnh | Mac | Chạy một đề tài qua trọn vòng đời G0–G10 — tự dừng ở 6 cổng cứng cần người ký |
| `/lam-sach-du-lieu` | lệnh | Mac | Khảo sát và làm sạch dữ liệu theo 3 bước có bác sĩ duyệt — không tự ý sửa dữ liệu |
| `/lo-trinh-de-tai` | lệnh | Mac | Lộ trình làm trọn một đề tài: gọi lệnh nào, theo thứ tự nào, dừng ở cổng nào — và đề tài đang ở đâu |
| `/ma-hoa-thu-thuat` | lệnh | Mac | Gợi ý mã thủ thuật và mã chẩn đoán cho một ca, kèm lý do — phục vụ hồ sơ và thống kê |
| `/nho-phan-bien` | lệnh | Mac | Bình duyệt bản thảo/đề cương như một phản biện khó tính trước khi nộp |
| `/nop-bai` | lệnh | Mac | Chọn tạp chí, soạn cover letter, đóng gói nộp và viết thư phản hồi phản biện |
| `/phan-tich-gop` | lệnh | Mac | Phân tích gộp: pooled effect + 95% CI, forest/funnel plot, I2, kiểm sai lệch công bố |
| `/ra-don-thuoc` | lệnh | Mac | Rà an toàn một đơn thuốc: tương tác, chống chỉ định, chỉnh liều theo thận/gan, người cao tuổi |
| `/sang-loc-asreview` | lệnh | Mac | Mở ASReview LAB để sàng lọc tiêu đề/tóm tắt bằng học chủ động — máy xếp lại thứ tự đọc, bác sĩ vẫn là người dán nhãn |
| `/sang-loc-cap-cuu` | lệnh | Mac | Sàng lọc cờ đỏ và ngưỡng chuyển tuyến/cấp cứu — chạy TRƯỚC mọi việc tra cứu |
| `/sang-loc-nghien-cuu` | lệnh | Mac | Sàng lọc tiêu đề/tóm tắt theo tiêu chuẩn chọn-loại và đánh giá nguy cơ sai lệch cho phân tích gộp |
| `/tham-dinh-chung-cu` | lệnh | Mac | Chấm GRADE, tính NNT/NNH, đánh giá nguy cơ sai lệch bằng đúng công cụ theo thiết kế |
| `/theo-doi-benh-man` | lệnh | Mac | Kế hoạch theo dõi dài hạn và điều trị theo đích cho bệnh mạn (ĐTĐ, THA, lipid, COPD…) |
| `/thiet-ke-de-tai` | lệnh | Mac | Chọn thiết kế nghiên cứu, kiểm soát sai lệch, soạn và khoá kế hoạch phân tích (G1/G4) |
| `/tim-chu-de-gop` | lệnh | Mac | Động não tìm và gọt chủ đề cho một phân tích gộp, trước khi chốt câu hỏi nghiên cứu |
| `/tim-khoang-trong` | lệnh | Mac | Đối chiếu câu hỏi với guideline hiện hành để tìm khoảng trống nghiên cứu, biện minh tính mới |
| `/tinh-co-mau` | lệnh | Mac | Tính cỡ mẫu / lực mẫu đúng theo thiết kế, kèm khối văn dán thẳng vào đề cương (cổng G3) |
| `/tinh-thang-diem` | lệnh | Mac | Chọn và áp thang điểm nguy cơ đã kiểm định (CHA2DS2-VASc, HAS-BLED, Wells, CURB-65, FRAX…) |
| `/tong-quan-y-van` | lệnh | Mac | Tổng quan y văn có hệ thống theo PRISMA — tái lập được, dùng cho công bố |
| `/tra-chung-cu` | lệnh | Mac | Tra chứng cứ tốt nhất cho MỘT câu hỏi lâm sàng, trả lời có PMID/DOI |
| `/tra-consensus` | lệnh | Mac | Tra mức ĐỒNG THUẬN của y văn về một câu hỏi — nhiều nghiên cứu nói cùng chiều hay trái chiều |
| `/tra-loi-phan-bien` | lệnh | Mac | Đọc góp ý phản biện và soạn thư phản hồi có cấu trúc, trả lời từng điểm một |
| `/tra-ma-icd10` | lệnh | Mac | Tra mã ICD-10 chẩn đoán/thủ thuật theo tên bệnh hoặc theo mã, kèm kiểm tính hợp lệ |
| `/tra-preprint` | lệnh | Mac | Tra bản thảo tiền in y sinh trên medRxiv/bioRxiv — chứng cứ mới nhất nhưng CHƯA bình duyệt |
| `/tra-thu-nghiem-lam-sang` | lệnh | Mac | Tra thử nghiệm lâm sàng trên ClinicalTrials.gov theo bệnh, can thiệp, tình trạng tuyển bệnh |
| `/tra-thuoc` | lệnh | Mac | Tra dược lý một thuốc: cơ chế tác dụng, đích tác động, hoạt tính sinh học, đặc tính ADMET (ChEMBL) |
| `/tra-y-van` | lệnh | Mac | Tra nhanh PubMed/PMC theo chủ đề, lấy PMID/DOI và tóm tắt — dùng khi cần tra gọn, không cần thẩm định GRADE |
| `/trich-xuat-benh-an` | lệnh | Mac | Bóc thông tin có cấu trúc từ bệnh án chữ tự do: chẩn đoán, thuốc, xét nghiệm, thủ thuật |
| `/tu-dien-du-lieu` | lệnh | Mac | Sinh từ điển dữ liệu từ file dữ liệu — gắn cờ biến mã hoá không rõ nghĩa thay vì đoán |
| `/tu-ra-bai` | lệnh | Mac | Tự rà bản thảo của mình bằng con mắt phản biện trước khi gửi tạp chí |
| `/ve-hinh-bai-bao` | lệnh | Mac | Vẽ hình đạt chuẩn đăng bài: ROC, forest plot, sơ đồ CONSORT/STARD/PRISMA, Kaplan-Meier |
| `/viet-bai-bao` | lệnh | Mac | Viết bản thảo IMRAD bám chuẩn báo cáo (CONSORT/STROBE/PRISMA/STARD/TRIPOD+AI) |
| `/xoa-dau-vet-ai` | lệnh | Mac | Phát hiện và xoá dấu hiệu văn phong máy trong bản thảo, giữ nguyên nội dung khoa học |

### user-skills  (43)

| Gọi bằng | Loại | Máy | Làm gì |
|---|---|---|---|
| `/EBM-MASTER` | kỹ năng | Mac | [EBM tổng hợp] Nền tảng y học chứng cứ hợp nhất cho cả lâm sàng lẫn nghiên cứu: tra và thẩm định chứng cứ, thống kê, giám sát guideline, an toàn thuốc, quản lý kháng sinh, thang điểm lâm sàng và quản trị dashboard. Dùng khi cần vào cửa c… |
| `/antifacts` | kỹ năng | Mac | Sử dụng skill này khi bác sĩ muốn MỞ hoặc CẬP NHẬT \"Antifacts\" — Trung tâm EBM theo chuyên khoa (mặt tiền gom mọi sản phẩm EBM trong thư mục \"Claude AI\" theo chuyên khoa: cập nhật chứng cứ + thang điểm lâm sàng + công cụ nghiên cứu).… |
| `/cap-nhat-chung-cu-y-khoa` | kỹ năng | Mac | Sử dụng skill này khi bác sĩ yêu cầu cập nhật chứng cứ hoặc khuyến cáo hiện hành cho MỘT vấn đề lâm sàng cụ thể. Mỗi cập nhật phải kèm Web Dashboard độc lập theo mô hình MẶC ĐỊNH \"Evidence Workbench\" (bố cục 3 cột: bộ lọc · bảng điểm c… |
| `/citation-management` | kỹ năng | Mac | Quản lý & kiểm chứng trích dẫn học thuật — phân giải PMID/DOI bắt buộc qua API miễn phí (PubMed/Crossref), đối chiếu metadata, bắt trích dẫn ma & citation washing, cảnh báo retracted/trùng, xuất danh mục Vancouver/ICMJE/AMA/BibTeX. Dùng … |
| `/clinical-decision-support` | kỹ năng | Mac | Tạo tài liệu hỗ trợ quyết định lâm sàng (CDS): phân tích nhóm bệnh nhân (cohort) theo dấu ấn sinh học, báo cáo khuyến cáo điều trị dựa trên bằng chứng kèm thuật toán quyết định và phân độ GRADE; phân tích thống kê (HR, đường sống còn); x… |
| `/clinical-evidence-rag` | kỹ năng | Mac | [Tra cứu chứng cứ] Cầu nối kiến thức với thực hành: trả lời câu hỏi lâm sàng bằng cách truy xuất từ kho y văn do chính bác sĩ kiểm soát — guideline, phác đồ khoa hoặc viện, bài tổng quan, bài báo đã tuyển chọn — rồi tổng hợp câu trả lời … |
| `/clinical-reports` | kỹ năng | Mac | Viết báo cáo lâm sàng: case report (chuẩn CARE), báo cáo chẩn đoán (X-quang/giải phẫu bệnh/xét nghiệm), báo cáo thử nghiệm lâm sàng (ICH-E3) và hồ sơ bệnh án (SOAP, H&P, tóm tắt xuất viện). Kèm template và công cụ kiểm tra. Mọi đầu ra kè… |
| `/dao-tao-slide-tai-lieu-y-khoa` | kỹ năng | Mac | Tạo và chuẩn hóa sản phẩm đào tạo y khoa và tài liệu chuyên môn — bài giảng, slide PowerPoint (.pptx), tài liệu Word (.docx), PDF, infographic/poster, bảng tóm tắt, bảng quyết định, thuật toán lâm sàng (Mermaid), checklist cờ đỏ, bảng th… |
| `/dark-analyst` | kỹ năng | Mac | Sử dụng skill này khi bác sĩ yêu cầu cập nhật chứng cứ hoặc khuyến cáo hiện hành cho MỘT vấn đề lâm sàng cụ thể. Mỗi cập nhật phải kèm Web Dashboard độc lập theo mô hình MẶC ĐỊNH \"Evidence Workbench\" (bố cục 3 cột: bộ lọc · bảng điểm c… |
| `/dashboard-master-ebm-ngoai-tru` | kỹ năng | Mac | Tạo, cập nhật hoặc kiểm định Dashboard Master EBM ngoại trú và các sổ Change Log, Evidence Register, Medication Safety, Action Register; xác minh nguồn, loại trùng, lập báo cáo điều hành tháng. |
| `/database-lookup` | kỹ năng | Mac | Truy vấn 78+ CƠ SỞ DỮ LIỆU khoa học/y khoa công khai qua API đã tài liệu hóa rõ endpoint, bộ lọc, phân trang và nguồn gốc dữ liệu (PubChem, ChEMBL, UniProt, ClinicalTrials.gov, FDA, dbSNP, ClinVar, COSMIC, GWAS Catalog, OMIM... phần lớn … |
| `/dieu-phoi-aipoch` | kỹ năng | Mac | Định tuyến yêu cầu nghiên cứu/lâm sàng tới đúng skill trong 605 skill của plugin aipoch-medical-research, theo 35 nhóm chuyên môn. Dùng khi bác sĩ mô tả một việc nhưng KHÔNG biết tên skill cụ thể trong bộ aipoch. |
| `/ehospital-mini` | kỹ năng | Mac | Soạn LỜI DẶN & NHẮC TÁI KHÁM ngoại trú cho bệnh nhân — mẫu in (A5/A4), mốc tái khám, cách dùng thuốc gọn, tiêu chí QUAY LẠI NGAY/đi cấp cứu (safety-netting), kế hoạch tuân thủ. Dùng khi cần phát tay tờ dặn dò sau khám. KHÔNG bịa tích hợp… |
| `/experimental-design` | kỹ năng | Mac | Thiết kế thí nghiệm/nghiên cứu TRƯỚC khi thu thập dữ liệu — chọn thiết kế, ngẫu nhiên hóa (randomization), phân khối (blocking/stratification), bố trí factorial/fractional-factorial, crossover, split-plot, Latin square, kiểm soát hiệu ứn… |
| `/exploratory-data-analysis` | kỹ năng | Mac | Khảo sát nhanh cấu trúc, chất lượng và đặc điểm của MỘT file dữ liệu khoa học (200+ định dạng: bảng tính, gen học, hóa học, ảnh vi mô, phổ, proteomics...) — tự nhận diện định dạng, sinh báo cáo markdown về chất lượng dữ liệu và gợi ý bướ… |
| `/giao-tiep-quyet-dinh-soap` | kỹ năng | Mac | Sử dụng skill này khi cần kỹ năng GIAO TIẾP với bệnh nhân, RA QUYẾT ĐỊNH CÙNG BỆNH NHÂN (shared decision-making), báo tin xấu, hoặc GHI HỒ SƠ SOAP. Kích hoạt với "giải thích cho bệnh nhân thế nào", "bệnh nhân không chịu điều trị/lưỡng lự… |
| `/hypothesis-generation` | kỹ năng | Mac | Hình thức hóa GIẢ THUYẾT khoa học từ quan sát/dữ liệu — sinh 3-5 giả thuyết CẠNH TRANH kèm CƠ CHẾ, chấm chất lượng theo 7 tiêu chí (khả kiểm định, khả bác bỏ theo Popper, tính đơn giản, sức giải thích, phạm vi, nhất quán, tính mới), rồi … |
| `/ke-don-an-toan-benh-man` | kỹ năng | Mac | Sử dụng skill này khi cần KÊ ĐƠN / RÀ ĐƠN AN TOÀN cho bệnh nhân bệnh mạn ngoại trú (mọi lứa tuổi, không chỉ người cao tuổi). Kích hoạt với \"đơn này có an toàn không\", \"thuốc có đánh nhau không/tương tác\", \"hiệu chỉnh liều theo thận/… |
| `/kham-ngoai-tru-ebm` | kỹ năng | Mac | Sử dụng skill này khi bác sĩ cần tiếp cận hoặc ra quyết định cho MỘT ca khám ngoại trú theo Y học chứng cứ (EBM). Dẫn dắt trọn 5 bước tại phòng khám: đặt câu hỏi lâm sàng (PICO) · hỏi–khám có trọng điểm + sàng lọc cờ đỏ · chẩn đoán phân … |
| `/literature-review` | kỹ năng | Mac | Quy trình TỔNG QUAN Y VĂN HỆ THỐNG theo PRISMA 2020 — câu hỏi PICO → đăng ký PROSPERO → chiến lược tìm tái lặp → sàng lọc (sơ đồ dòng chảy) → trích xuất → đánh giá nguy cơ sai lệch → tổng hợp định tính/meta + GRADE. Dùng khi cần làm tổng… |
| `/nghien-cuu-ebm-tong-hop` | kỹ năng | Mac | >- Trợ lý NGHIÊN CỨU Y KHOA & Y HỌC CHỨNG CỨ (EBM) hợp nhất cho bác sĩ lâm sàng. Gồm 5 mô-đun: (1) Tìm & thu thập y văn; (2) Đọc & thẩm định chứng cứ; (3) Thiết kế nghiên cứu lâm sàng; (4) Thống kê & mô hình lâm sàng; (5) Viết & nộp bản … |
| `/nghien-cuu-y-khoa-chuan-quoc-te` | kỹ năng | Mac | Thực hiện, thiết kế và rà soát nghiên cứu y khoa theo chuẩn quốc tế qua cổng chất lượng G0-G9. Dùng skill này khi người dùng cần xác định câu hỏi/đề cương/protocol, hồ sơ đạo đức và đăng ký nghiên cứu, tính cỡ mẫu, thiết kế biến số/CRF/p… |
| `/nguoi-cao-tuoi-da-benh-da-thuoc` | kỹ năng | Mac | Chăm sóc toàn diện người cao tuổi suy yếu, đa bệnh lý và đa thuốc theo hướng an toàn thuốc, giảm hại và tránh điều trị quá mức. Dùng skill này bất cứ khi nào có bệnh nhân lớn tuổi kèm nhiều thuốc hoặc nhiều bệnh đồng mắc — rà soát và đối… |
| `/paper-lookup` | kỹ năng | Mac | Tra cứu bài báo y khoa qua API MIỄN PHÍ (PubMed E-utilities, Crossref, Europe PMC) — tìm theo PICO/từ khóa/MeSH, phân giải và xác minh PMID/DOI, lấy metadata gốc. Dùng khi cần tìm bài cho một câu hỏi, kiểm một PMID/DOI có thật, hoặc lấy … |
| `/peer-review` | kỹ năng | Mac | Bình duyệt bản thảo khoa học có CẤU TRÚC — đánh giá tính hợp lệ (validity), phương pháp, thống kê, đạo đức/đăng ký, trình bày & chuẩn báo cáo, trích dẫn; soạn nhận xét đối kháng đa lăng kính + thư phản biện cho tác giả. Dùng trước khi nộ… |
| `/plugin-router-chatgpt` | kỹ năng | Mac | Điều phối yêu cầu rộng, mơ hồ hoặc nhiều bước tới đúng nhạc trưởng, plugin và skill trong hệ Claude–Codex–ChatGPT. Dùng khi cần tự chọn công cụ, phối hợp nhiều chuyên môn hoặc kiểm tra ai là owner; không thay một skill chuyên biệt đã đượ… |
| `/pyhealth` | kỹ năng | Mac | Xây dựng pipeline học máy lâm sàng bằng thư viện PyHealth: tải dữ liệu EHR (MIMIC-III/IV, eICU, OMOP), định nghĩa tác vụ (tử vong, tái nhập viện, gợi ý thuốc, giai đoạn ngủ, mã hóa ICD), huấn luyện mô hình (Transformer, RETAIN, GAMENet, … |
| `/quan-ly-cap-nhat-ebm` | kỹ năng | Mac | Sử dụng skill này khi bác sĩ muốn QUẢN LÝ kho cập nhật EBM đã lưu (sổ cái EBM_MASTER) — xem tổng quan, tìm/lọc, duyệt và phê chuẩn các cập nhật. Kích hoạt với "quản lý EBM", "xem các cập nhật", "hàng đợi duyệt", "duyệt thẻ…", "thống kê s… |
| `/research-lookup` | kỹ năng | Mac | Tra cứu NGHIÊN CỨU & ĐĂNG KÝ THỬ NGHIỆM qua nguồn mở — ClinicalTrials.gov (API v2), WHO ICTRP, PROSPERO. Dùng khi cần kiểm một thử nghiệm đã đăng ký chưa, tìm nghiên cứu đang tiến hành/đã hoàn tất, đối chiếu kết cục đăng ký vs công bố (c… |
| `/scholar-evaluation` | kỹ năng | Mac | Chấm điểm ĐỊNH LƯỢNG chất lượng học thuật của bản thảo/đề cương/tổng quan theo khung ScholarEval — 8 chiều (đặt vấn đề, tổng quan y văn, phương pháp, thu thập dữ liệu, phân tích, kết quả, văn phong, trích dẫn), mỗi chiều chấm 0-5 có trọn… |
| `/scientific-critical-thinking` | kỹ năng | Mac | Khung THẨM ĐỊNH chất lượng chứng cứ và tính hợp lệ của thiết kế nghiên cứu — áp dụng GRADE, Cochrane Risk of Bias, nhận diện thiên kiến/nhiễu/ngụy biện logic và các lỗi thống kê thường gặp. Dùng để dạy hoặc tự kiểm tra tư duy phản biện k… |
| `/scientific-writing` | kỹ năng | Mac | Viết bản thảo khoa học y khoa theo cấu trúc IMRAD, văn xuôi liền mạch, khớp CHUẨN BÁO CÁO đúng thiết kế (CONSORT/STROBE/PRISMA/SPIRIT/STARD/TRIPOD+AI; COREQ/SRQR cho định tính; SQUIRE cho QI). Dùng khi cần viết bài báo, protocol, hoặc bá… |
| `/scikit-survival` | kỹ năng | Mac | Phân tích SỐNG CÒN / thời gian-đến-biến-cố (time-to-event) bằng scikit-survival: mô hình Cox, Random Survival Forest, Gradient Boosting, Survival SVM; xử lý dữ liệu KIỂM DUYỆT (censoring) và NGUY CƠ CẠNH TRANH (competing risks); đánh giá… |
| `/statistical-analysis` | kỹ năng | Mac | Quy trình phân tích thống kê lâm sàng/nghiên cứu y khoa — mô tả dữ liệu, chọn kiểm định theo loại biến + thiết kế + giả định, hồi quy/sống còn/ROC/hiệu chỉnh, báo cáo ước lượng + 95% CI. Dùng khi cần chạy/đọc phân tích thống kê cho một đ… |
| `/statistical-power` | kỹ năng | Mac | Tính CỠ MẪU / LỰC THỐNG KÊ (power analysis) TRƯỚC khi thu thập dữ liệu — bằng công thức đóng (t-test, ANOVA, tỷ lệ, tương quan, chi-square, hồi quy) VÀ mô phỏng Monte Carlo cho thiết kế không có công thức chuẩn (hồi quy logistic/Poisson,… |
| `/statsmodels` | kỹ năng | Mac | Chạy mô hình thống kê THẬT bằng thư viện statsmodels: OLS, GLM, mô hình hỗn hợp (mixed-effects), ARIMA/chuỗi thời gian — kèm bảng hệ số, chẩn đoán giả định, phân tích residual. Dùng khi ĐÃ có dữ liệu và cần fit một mô hình cụ thể (khác s… |
| `/tao-video-tiktok` | kỹ năng | Mac | >- Tạo video TikTok dọc (9:16, 1080x1920) từ nội dung do người dùng cung cấp, có GIỌNG ĐỌC tiếng Việt mềm mại, ngắt nghỉ tự nhiên (edge-tts HoaiMy nữ / NamMinh nam, tự lùi về giọng macOS "Linh" khi mất mạng) và PHỤ ĐỀ ĐỘNG karaoke đồng b… |
| `/tham-dinh-chung-cu-grade-nnt` | kỹ năng | Mac | Sử dụng skill này khi cần THẨM ĐỊNH NHANH một bài báo/guideline/nghiên cứu để quyết định có đáng đổi thực hành không. Kích hoạt với "bài này có đáng tin không", "đọc giúp tôi nghiên cứu này", "NNT/NNH bao nhiêu", "nguy cơ sai lệch (risk … |
| `/tiep-can-chan-doan-co-do-chuyen-tuyen` | kỹ năng | Mac | Sử dụng skill này khi bác sĩ tiếp cận MỘT triệu chứng/hội chứng ngoại trú và cần đi từ triệu chứng → chẩn đoán phân biệt → CỜ ĐỎ bắt buộc loại trừ → ngưỡng chuyển tuyến/cấp cứu một cách AN TOÀN. Kích hoạt với \"bệnh nhân đau ngực/đau đầu… |
| `/tong-thuat-chung-cu` | kỹ năng | Mac | Bác sĩ hỏi MỘT chủ đề lâm sàng → trả MỘT bài tổng thuật học thuật liền mạch (kiểu Deep-Research) neo vào hạ tầng liêm chính — 4 làn nguồn song song, trích dẫn Vancouver đánh số qua cổng kiểm, trình bày chuẩn v11. Bác sĩ duyệt gói ① ngày … |
| `/treatment-plans` | kỹ năng | Mac | Soạn kế hoạch điều trị y khoa ngắn gọn (3-4 trang) xuất LaTeX/PDF cho nhiều chuyên khoa: nội khoa chung, phục hồi chức năng, sức khỏe tâm thần, quản lý bệnh mạn, chu phẫu, giảm đau. Dùng khung mục tiêu SMART, can thiệp dựa bằng chứng. Kè… |
| `/tuan-thu-dieu-tri` | kỹ năng | Mac | Sử dụng skill này khi cần đánh giá và cải thiện TUÂN THỦ ĐIỀU TRỊ (medication & treatment adherence) cho bệnh nhân ngoại trú. Kích hoạt khi bác sĩ nói \"bệnh nhân không tuân thủ\", \"hay quên uống thuốc\", \"bỏ thuốc/tự ngưng thuốc\", \"… |
| `/venue-templates` | kỹ năng | Mac | Template LaTeX + yêu cầu định dạng cho các tạp chí/hội nghị khoa học lớn (Nature, Science, PLOS, Elsevier...), poster nghiên cứu, và đề cương xin tài trợ — kèm chuẩn báo cáo CONSORT/STROBE/PRISMA cho bài y khoa. Dùng khi chuẩn bị bản thả… |

### healthcare  (14)

| Gọi bằng | Loại | Máy | Làm gì |
|---|---|---|---|
| `agent documents-reader-cli` | agent | Mac | [Pháp lý] Tiến trình con đọc một phần kho hợp đồng, bản chạy qua dòng lệnh. Chạy nội bộ, không gọi trực tiếp. Từ khoá: contracts sweep worker CLI. |
| `agent documents-reader-mcp` | agent | Mac | [Pháp lý] Tiến trình con đọc một phần kho hợp đồng và ghi nhận phát hiện kèm trích dẫn. Chạy nội bộ, không gọi trực tiếp. Từ khoá: contracts sweep worker. |
| `agent note-extract-worker` | agent | Mac | [Y khoa] Tiến trình con bóc dữ liệu cho từng bệnh án khi chạy hàng loạt. Chạy nội bộ, không gọi trực tiếp — dùng `/trich-xuat-benh-an`. Từ khoá: note extraction worker. |
| `/healthcare:clinical-note-extract-skill` | kỹ năng | Mac | [Y khoa] Bóc dữ liệu có cấu trúc từ bệnh án, chỉ rõ vị trí từng thông tin trong văn bản gốc. Dùng khi cần chuyển bệnh án chữ tự do thành bảng dữ liệu; khử định danh trước bằng `/khu-dinh-danh`. Từ khoá: clinical note extraction. |
| `/healthcare:clinical-trial-protocol-skill` | kỹ năng | Mac | [Nghiên cứu] Sinh đề cương thử nghiệm lâm sàng cho thuốc hoặc thiết bị y tế. Dùng khi cần bản nháp nhanh theo khuôn quốc tế; đề tài thật nên đi qua agent `dieu-phoi-nghien-cuu` để có cổng G0–G10. Từ khoá: trial protocol. |
| `/healthcare:contracts` | kỹ năng | Mac | [Pháp lý] Trả lời câu hỏi xuyên suốt một kho hợp đồng, có trích dẫn vị trí. Dùng khi phải tra nhiều hợp đồng cùng lúc. Từ khoá: contract corpus. |
| `/healthcare:doc-extract` | kỹ năng | Mac | [Tài liệu] Rút văn bản thuần từ file PDF, DOCX, XLSX, PPTX. Dùng khi cần lấy nội dung ra khỏi file để xử lý tiếp. Từ khoá: document extraction. |
| `/healthcare:fhir` | kỹ năng | Mac | [Y khoa] Kết nối tới máy chủ FHIR R4 của bệnh viện (Epic, Oracle Health/Cerner). Dùng khi cần lấy dữ liệu trực tiếp từ bệnh án điện tử thay vì nhập tay. Từ khoá: FHIR R4, EHR. |
| `/healthcare:fhir-developer-skill` | kỹ năng | Mac | [Y khoa] Hướng dẫn lập trình API FHIR. Dùng khi tự xây điểm cuối kết nối hệ thống y tế, không phải khi chỉ đọc dữ liệu. Từ khoá: FHIR development. |
| `/healthcare:fraud-detection` | kỹ năng | Mac | [Y khoa — hệ Mỹ] Sàng kho hồ sơ thanh toán Medicare/Medicaid tìm gian lận và lãng phí. Dùng khi kiểm toán chi trả theo hệ Mỹ. Từ khoá: claims fraud. |
| `/healthcare:icd10-cm-skill` | kỹ năng | Mac | [Y khoa] Rút mã chẩn đoán ICD-10-CM dùng để thanh toán từ một bệnh án. Dùng khi cần mã hoá hồ sơ đã có sẵn bệnh án; tra mã lẻ thì dùng `/tra-ma-icd10`. Từ khoá: ICD-10-CM. |
| `/healthcare:prior-auth-review-skill` | kỹ năng | Mac | [Y khoa — hệ Mỹ] Tự động hoá việc xét duyệt yêu cầu chấp thuận trước của hãng bảo hiểm. Dùng khi làm việc với bảo hiểm Mỹ; ít dùng ở Việt Nam. Từ khoá: prior authorization. |
| `/healthcare:procedure-coding` | kỹ năng | Mac | [Y khoa] Gán mã thủ thuật CPT và HCPCS cấp II từ hồ sơ lâm sàng. Dùng khi lập hồ sơ thanh toán theo hệ Mỹ — bộ mã này KHÁC quy định Việt Nam. Từ khoá: CPT, HCPCS. |
| `/healthcare:verify` | kỹ năng | Mac | [Hỗ trợ] Kiểm tra thay đổi đối với script cài đặt quản trị. Dùng khi vừa sửa script cài và muốn chắc không hỏng. Từ khoá: verify install. |

### pubmed  (14)

| Gọi bằng | Loại | Máy | Làm gì |
|---|---|---|---|
| `agent documents-reader-cli` | agent | Mac | [Pháp lý] Tiến trình con đọc một phần kho hợp đồng, bản chạy qua dòng lệnh. Chạy nội bộ, không gọi trực tiếp. Từ khoá: contracts sweep worker CLI. |
| `agent documents-reader-mcp` | agent | Mac | [Pháp lý] Tiến trình con đọc một phần kho hợp đồng và ghi nhận phát hiện kèm trích dẫn. Chạy nội bộ, không gọi trực tiếp. Từ khoá: contracts sweep worker. |
| `agent note-extract-worker` | agent | Mac | [Y khoa] Tiến trình con bóc dữ liệu cho từng bệnh án khi chạy hàng loạt. Chạy nội bộ, không gọi trực tiếp — dùng `/trich-xuat-benh-an`. Từ khoá: note extraction worker. |
| `/pubmed:clinical-note-extract-skill` | kỹ năng | Mac | [Y khoa] Bóc dữ liệu có cấu trúc từ bệnh án, chỉ rõ vị trí từng thông tin trong văn bản gốc. Dùng khi cần chuyển bệnh án chữ tự do thành bảng dữ liệu; khử định danh trước bằng `/khu-dinh-danh`. Từ khoá: clinical note extraction. |
| `/pubmed:clinical-trial-protocol-skill` | kỹ năng | Mac | [Nghiên cứu] Sinh đề cương thử nghiệm lâm sàng cho thuốc hoặc thiết bị y tế. Dùng khi cần bản nháp nhanh theo khuôn quốc tế; đề tài thật nên đi qua agent `dieu-phoi-nghien-cuu` để có cổng G0–G10. Từ khoá: trial protocol. |
| `/pubmed:contracts` | kỹ năng | Mac | [Pháp lý] Trả lời câu hỏi xuyên suốt một kho hợp đồng, có trích dẫn vị trí. Dùng khi phải tra nhiều hợp đồng cùng lúc. Từ khoá: contract corpus. |
| `/pubmed:doc-extract` | kỹ năng | Mac | [Tài liệu] Rút văn bản thuần từ file PDF, DOCX, XLSX, PPTX. Dùng khi cần lấy nội dung ra khỏi file để xử lý tiếp. Từ khoá: document extraction. |
| `/pubmed:fhir` | kỹ năng | Mac | [Y khoa] Kết nối tới máy chủ FHIR R4 của bệnh viện (Epic, Oracle Health/Cerner). Dùng khi cần lấy dữ liệu trực tiếp từ bệnh án điện tử thay vì nhập tay. Từ khoá: FHIR R4, EHR. |
| `/pubmed:fhir-developer-skill` | kỹ năng | Mac | [Y khoa] Hướng dẫn lập trình API FHIR. Dùng khi tự xây điểm cuối kết nối hệ thống y tế, không phải khi chỉ đọc dữ liệu. Từ khoá: FHIR development. |
| `/pubmed:fraud-detection` | kỹ năng | Mac | [Y khoa — hệ Mỹ] Sàng kho hồ sơ thanh toán Medicare/Medicaid tìm gian lận và lãng phí. Dùng khi kiểm toán chi trả theo hệ Mỹ. Từ khoá: claims fraud. |
| `/pubmed:icd10-cm-skill` | kỹ năng | Mac | [Y khoa] Rút mã chẩn đoán ICD-10-CM dùng để thanh toán từ một bệnh án. Dùng khi cần mã hoá hồ sơ đã có sẵn bệnh án; tra mã lẻ thì dùng `/tra-ma-icd10`. Từ khoá: ICD-10-CM. |
| `/pubmed:prior-auth-review-skill` | kỹ năng | Mac | [Y khoa — hệ Mỹ] Tự động hoá việc xét duyệt yêu cầu chấp thuận trước của hãng bảo hiểm. Dùng khi làm việc với bảo hiểm Mỹ; ít dùng ở Việt Nam. Từ khoá: prior authorization. |
| `/pubmed:procedure-coding` | kỹ năng | Mac | [Y khoa] Gán mã thủ thuật CPT và HCPCS cấp II từ hồ sơ lâm sàng. Dùng khi lập hồ sơ thanh toán theo hệ Mỹ — bộ mã này KHÁC quy định Việt Nam. Từ khoá: CPT, HCPCS. |
| `/pubmed:verify` | kỹ năng | Mac | [Hỗ trợ] Kiểm tra thay đổi đối với script cài đặt quản trị. Dùng khi vừa sửa script cài và muốn chắc không hỏng. Từ khoá: verify install. |

### icd10-codes  (14)

| Gọi bằng | Loại | Máy | Làm gì |
|---|---|---|---|
| `agent documents-reader-cli` | agent | Mac | [Pháp lý] Tiến trình con đọc một phần kho hợp đồng, bản chạy qua dòng lệnh. Chạy nội bộ, không gọi trực tiếp. Từ khoá: contracts sweep worker CLI. |
| `agent documents-reader-mcp` | agent | Mac | [Pháp lý] Tiến trình con đọc một phần kho hợp đồng và ghi nhận phát hiện kèm trích dẫn. Chạy nội bộ, không gọi trực tiếp. Từ khoá: contracts sweep worker. |
| `agent note-extract-worker` | agent | Mac | [Y khoa] Tiến trình con bóc dữ liệu cho từng bệnh án khi chạy hàng loạt. Chạy nội bộ, không gọi trực tiếp — dùng `/trich-xuat-benh-an`. Từ khoá: note extraction worker. |
| `/icd10-codes:clinical-note-extract-skill` | kỹ năng | Mac | [Y khoa] Bóc dữ liệu có cấu trúc từ bệnh án, chỉ rõ vị trí từng thông tin trong văn bản gốc. Dùng khi cần chuyển bệnh án chữ tự do thành bảng dữ liệu; khử định danh trước bằng `/khu-dinh-danh`. Từ khoá: clinical note extraction. |
| `/icd10-codes:clinical-trial-protocol-skill` | kỹ năng | Mac | [Nghiên cứu] Sinh đề cương thử nghiệm lâm sàng cho thuốc hoặc thiết bị y tế. Dùng khi cần bản nháp nhanh theo khuôn quốc tế; đề tài thật nên đi qua agent `dieu-phoi-nghien-cuu` để có cổng G0–G10. Từ khoá: trial protocol. |
| `/icd10-codes:contracts` | kỹ năng | Mac | [Pháp lý] Trả lời câu hỏi xuyên suốt một kho hợp đồng, có trích dẫn vị trí. Dùng khi phải tra nhiều hợp đồng cùng lúc. Từ khoá: contract corpus. |
| `/icd10-codes:doc-extract` | kỹ năng | Mac | [Tài liệu] Rút văn bản thuần từ file PDF, DOCX, XLSX, PPTX. Dùng khi cần lấy nội dung ra khỏi file để xử lý tiếp. Từ khoá: document extraction. |
| `/icd10-codes:fhir` | kỹ năng | Mac | [Y khoa] Kết nối tới máy chủ FHIR R4 của bệnh viện (Epic, Oracle Health/Cerner). Dùng khi cần lấy dữ liệu trực tiếp từ bệnh án điện tử thay vì nhập tay. Từ khoá: FHIR R4, EHR. |
| `/icd10-codes:fhir-developer-skill` | kỹ năng | Mac | [Y khoa] Hướng dẫn lập trình API FHIR. Dùng khi tự xây điểm cuối kết nối hệ thống y tế, không phải khi chỉ đọc dữ liệu. Từ khoá: FHIR development. |
| `/icd10-codes:fraud-detection` | kỹ năng | Mac | [Y khoa — hệ Mỹ] Sàng kho hồ sơ thanh toán Medicare/Medicaid tìm gian lận và lãng phí. Dùng khi kiểm toán chi trả theo hệ Mỹ. Từ khoá: claims fraud. |
| `/icd10-codes:icd10-cm-skill` | kỹ năng | Mac | [Y khoa] Rút mã chẩn đoán ICD-10-CM dùng để thanh toán từ một bệnh án. Dùng khi cần mã hoá hồ sơ đã có sẵn bệnh án; tra mã lẻ thì dùng `/tra-ma-icd10`. Từ khoá: ICD-10-CM. |
| `/icd10-codes:prior-auth-review-skill` | kỹ năng | Mac | [Y khoa — hệ Mỹ] Tự động hoá việc xét duyệt yêu cầu chấp thuận trước của hãng bảo hiểm. Dùng khi làm việc với bảo hiểm Mỹ; ít dùng ở Việt Nam. Từ khoá: prior authorization. |
| `/icd10-codes:procedure-coding` | kỹ năng | Mac | [Y khoa] Gán mã thủ thuật CPT và HCPCS cấp II từ hồ sơ lâm sàng. Dùng khi lập hồ sơ thanh toán theo hệ Mỹ — bộ mã này KHÁC quy định Việt Nam. Từ khoá: CPT, HCPCS. |
| `/icd10-codes:verify` | kỹ năng | Mac | [Hỗ trợ] Kiểm tra thay đổi đối với script cài đặt quản trị. Dùng khi vừa sửa script cài và muốn chắc không hỏng. Từ khoá: verify install. |

### bio-research  (6)

| Gọi bằng | Loại | Máy | Làm gì |
|---|---|---|---|
| `/bio-research:instrument-data-to-allotrope` | kỹ năng | Mac | [Tin sinh học] Chuyển dữ liệu máy xét nghiệm (PDF, CSV, Excel) sang chuẩn Allotrope. Dùng khi cần đưa số liệu từ máy labo về một định dạng chung. Từ khoá: Allotrope. |
| `/bio-research:nextflow-development` | kỹ năng | Mac | [Tin sinh học] Chạy các đường ống phân tích nf-core (rnaseq, sarek, atacseq) bằng Nextflow. Dùng khi xử lý dữ liệu giải trình tự quy mô lớn. Từ khoá: Nextflow, nf-core. |
| `/bio-research:scientific-problem-selection` | kỹ năng | Mac | [Nghiên cứu] Giúp chọn vấn đề nghiên cứu đáng làm. Dùng khi còn phân vân giữa nhiều hướng, trước khi đặt câu hỏi PICO. Từ khoá: problem selection. |
| `/bio-research:scvi-tools` | kỹ năng | Mac | [Tế bào đơn] Phân tích RNA tế bào đơn bằng học sâu với scvi-tools. Dùng khi cần hiệu chỉnh lô hoặc chuyển nhãn tế bào. Từ khoá: scvi-tools. |
| `/bio-research:single-cell-rna-qc` | kỹ năng | Mac | [Tin sinh học] Kiểm chất lượng dữ liệu RNA tế bào đơn (file .h5ad). Dùng khi vừa nhận dữ liệu giải trình tự, trước khi phân tích. Từ khoá: single-cell QC. |
| `/bio-research:start` | kỹ năng | Mac | [Nghiên cứu sinh học] Cài môi trường bio-research và xem có sẵn công cụ gì. Dùng khi lần đầu làm quen bộ plugin này, hoặc muốn biết máy chủ tra cứu y văn / dược / hình ảnh nào đang kết nối. Từ khoá: bio-research start, setup. |

### cowork-plugin-management  (2)

| Gọi bằng | Loại | Máy | Làm gì |
|---|---|---|---|
| `/cowork-plugin-management:cowork-plugin-customizer` | kỹ năng | Mac | [Hỗ trợ] Tuỳ chỉnh một plugin Claude Code cho nhu cầu riêng của đơn vị. Dùng khi plugin có sẵn gần đúng nhưng cần sửa vài chỗ. Từ khoá: plugin customizer. |
| `/cowork-plugin-management:create-cowork-plugin` | kỹ năng | Mac | [Hỗ trợ] Hướng dẫn tạo một plugin mới từ đầu. Dùng khi muốn đóng gói quy trình riêng thành plugin dùng lại được. Từ khoá: create plugin. |

### scientific-problem-selection  (2)

| Gọi bằng | Loại | Máy | Làm gì |
|---|---|---|---|
| `/scientific-problem-selection:clinical-trial-protocol-skill` | kỹ năng | Mac | [Nghiên cứu] Sinh đề cương thử nghiệm lâm sàng cho thuốc hoặc thiết bị y tế. Dùng khi cần bản nháp nhanh theo khuôn quốc tế; đề tài thật nên đi qua agent `dieu-phoi-nghien-cuu` để có cổng G0–G10. Từ khoá: trial protocol. |
| `/scientific-problem-selection:scientific-problem-selection` | kỹ năng | Mac | [Nghiên cứu] Giúp chọn vấn đề nghiên cứu đáng làm. Dùng khi còn phân vân giữa nhiều hướng, trước khi đặt câu hỏi PICO. Từ khoá: problem selection. |

### clinical-trial-protocol  (2)

| Gọi bằng | Loại | Máy | Làm gì |
|---|---|---|---|
| `/clinical-trial-protocol:clinical-trial-protocol-skill` | kỹ năng | Mac | [Nghiên cứu] Sinh đề cương thử nghiệm lâm sàng cho thuốc hoặc thiết bị y tế. Dùng khi cần bản nháp nhanh theo khuôn quốc tế; đề tài thật nên đi qua agent `dieu-phoi-nghien-cuu` để có cổng G0–G10. Từ khoá: trial protocol. |
| `/clinical-trial-protocol:scientific-problem-selection` | kỹ năng | Mac | [Nghiên cứu] Giúp chọn vấn đề nghiên cứu đáng làm. Dùng khi còn phân vân giữa nhiều hướng, trước khi đặt câu hỏi PICO. Từ khoá: problem selection. |

---

## TẦNG 2 — Kỹ thuật, dùng khi sửa chính hệ EBM  (95 mục)


### claude-code-harness  (33)

| Gọi bằng | Loại | Máy | Làm gì |
|---|---|---|---|
| `agent advisor` | agent | Mac | [Lập trình] Agent cố vấn KHÔNG thực thi: chỉ trả về hướng xử lý cho yêu cầu mà agent thợ gửi lên. Từ khoá: advisor agent. |
| `agent livemsg-gate` | agent | Mac | [Lập trình] Agent CHỈ ĐỌC kiểm chứng khẳng định trong thông điệp liên phiên trước khi gửi, trả về SEND hoặc HOLD. Từ khoá: livemsg gate, cross-session verification. |
| `agent reviewer` | agent | Mac | [Lập trình] Agent rà soát CHỈ ĐỌC: đưa phán quyết dựa trên hợp đồng công việc và tài liệu rà soát. Từ khoá: reviewer agent. |
| `agent test-wiring-auditor` | agent | Mac | [Lập trình] Agent CHỈ ĐỌC, kiểm xem bộ kiểm thử đã bám theo phần mã vừa thay đổi chưa; chạy trong ngữ cảnh sạch để khỏi bị thiên lệch. Từ khoá: test coverage audit. |
| `agent worker` | agent | Mac | [Lập trình] Agent thợ chính: thực hiện một việc trọn gói — viết mã, tự kiểm trước, xác minh và chuẩn bị commit. Từ khoá: worker agent. |
| `/handoff-to-claude` | lệnh | Mac | [Lập trình] Sinh câu lệnh giao việc cho Claude Code. Từ khoá: handoff to Claude. |
| `/plan-with-cc` | lệnh | Mac | [Lập trình] Lập kế hoạch — phối hợp với Claude Code để chia nhỏ công việc. Từ khoá: plan with CC. |
| `/project-overview` | lệnh | Mac | [Lập trình] Nắm nhanh bức tranh tổng thể của dự án. Từ khoá: project overview. |
| `/review-cc-work` | lệnh | Mac | [Lập trình] Rà soát việc Claude Code đã làm rồi bàn giao lại kèm chỉ dẫn duyệt hoặc sửa. Từ khoá: review CC work. |
| `/start-session` | lệnh | Mac | [Lập trình] Bắt đầu phiên làm việc: nắm tình hình → lập kế hoạch → giao việc cho Claude Code. Từ khoá: start session. |
| `/claude-code-harness:agent-browser` | kỹ năng | Mac | [Lập trình] Điều khiển trình duyệt tự động: mở trang, điền biểu mẫu, chụp màn hình, thu thập dữ liệu. Từ khoá: browser automation. |
| `/claude-code-harness:breezing` | kỹ năng | Mac | [Lập trình] Chế độ chạy theo NHÓM — tên gọi cũ tương đương harness-work có điều phối nhiều agent. Từ khoá: team execution. |
| `/claude-code-harness:cc-update-review` | kỹ năng | Mac | [Lập trình] Chốt chất lượng khi tích hợp bản cập nhật Claude/Codex; bắt trường hợp chỉ thêm tài liệu mà chưa có mã thật. Từ khoá: update review. |
| `/claude-code-harness:ci` | kỹ năng | Mac | [Lập trình] Chữa cháy CI: build đỏ, test hỏng, pipeline lỗi. Từ khoá: CI failure, build error. |
| `/claude-code-harness:cursor-ask` | kỹ năng | Mac | [Lập trình] Hỏi Cursor ở chế độ CHỈ ĐỌC để điều tra, bàn thiết kế, phản biện — không cho sửa file. Từ khoá: cursor ask. |
| `/claude-code-harness:cursor-do` | kỹ năng | Mac | [Lập trình] Giao MỘT việc có sửa file cho Cursor trong nhánh làm việc tách biệt rồi thu kết quả về. Từ khoá: cursor do. |
| `/claude-code-harness:cursor-review` | kỹ năng | Mac | [Lập trình] Nhờ Cursor rà soát như ý kiến thứ hai; kết luận cuối vẫn thuộc về bên chính. Từ khoá: cursor review. |
| `/claude-code-harness:cursor-setup` | kỹ năng | Mac | [Lập trình] Cài và kiểm tra nền Cursor cho harness. Từ khoá: cursor setup. |
| `/claude-code-harness:failure-codifier` | kỹ năng | Mac | [Lập trình] Rút ra các kiểu lỗi LẶP LẠI từ những lần chạy nhiều agent, để lần sau tránh đúng vết cũ. Từ khoá: failure patterns. |
| `/claude-code-harness:harness-accept` | kỹ năng | Mac | [Lập trình] Dựng trang HTML NGHIỆM THU cho người không rành kỹ thuật xem trước khi quyết định phát hành. Từ khoá: acceptance demo. |
| `/claude-code-harness:harness-loop` | kỹ năng | Mac | [Lập trình] Chạy việc DÀI HƠI theo vòng lặp, tự hẹn giờ quay lại với ngữ cảnh mới. Dùng cho việc nhiều giờ. Từ khoá: harness loop. |
| `/claude-code-harness:harness-plan` | kỹ năng | Mac | [Lập trình] Lập KẾ HOẠCH công việc có kiểm chứng, quản lý Plans.md và đồng bộ tiến độ. Dùng khi bắt đầu một hạng mục sửa hệ thống. Từ khoá: harness plan, Plans.md. |
| `/claude-code-harness:harness-plan-brief` | kỹ năng | Mac | [Lập trình] Dựng trang HTML TÓM TẮT KẾ HOẠCH dễ đọc cho người không rành kỹ thuật, trước khi bắt tay làm. Từ khoá: plan brief. |
| `/claude-code-harness:harness-progress` | kỹ năng | Mac | [Lập trình] Dựng trang HTML THEO DÕI TIẾN ĐỘ phiên làm việc để liếc nhanh. Từ khoá: progress tracker. |
| `/claude-code-harness:harness-release` | kỹ năng | Mac | [Lập trình] Tự động hoá phát hành theo Keep a Changelog + GitHub, có một cổng xác nhận trước khi chạy. Từ khoá: harness release. |
| `/claude-code-harness:harness-review` | kỹ năng | Mac | [Lập trình] RÀ SOÁT mã nguồn, kế hoạch và phạm vi từ nhiều góc; kiểm bảo mật và chất lượng. Từ khoá: harness review, code review. |
| `/claude-code-harness:harness-setup` | kỹ năng | Mac | [Lập trình] Khởi tạo dự án, cài công cụ, cấu hình agent, dựng bộ nhớ và đồng bộ bản sao skill. Từ khoá: harness setup, init. |
| `/claude-code-harness:harness-sync` | kỹ năng | Mac | [Lập trình] Đối chiếu Plans.md với mã thật, phát hiện lệch, cập nhật mốc và rút kinh nghiệm. Dùng khi hỏi 'đang làm tới đâu'. Từ khoá: harness sync, drift. |
| `/claude-code-harness:harness-work` | kỹ năng | Mac | [Lập trình] THỰC THI các việc trong Plans.md, từ một việc lẻ tới chạy song song cả nhóm. Từ khoá: harness work, implement. |
| `/claude-code-harness:japanese-writing-drafter` | kỹ năng | Mac | [Lập trình] Bắt lúc người dùng sửa cách diễn đạt TIẾNG NHẬT của agent, rồi ghi đề xuất luật văn phong vào proposals.jsonl chờ người duyệt — nơi DUY NHẤT ghi file đó, không đụng rules.jsonl. Dùng khi người dùng nói 表現を直して, 文体を直して, その言い方はN… |
| `/claude-code-harness:maintenance` | kỹ năng | Mac | [Lập trình] Dọn dẹp và lưu trữ file: Plans.md phình to, nhật ký phiên, log cũ. Từ khoá: cleanup, archiving. |
| `/claude-code-harness:memory` | kỹ năng | Mac | [Lập trình] Quản lý bộ nhớ dự án và tìm kiếm xuyên công cụ; giữ decisions.md và patterns.md. Từ khoá: memory, SSOT. |
| `/claude-code-harness:session-send` | kỹ năng | Mac | [Lập trình] Gửi thông điệp liên phiên tới agent khác — dùng khi bác sĩ yêu cầu báo phiên khác, bàn giao phiên, hoặc "nói với agent kia". Từ khoá: session send, cross-session message. |

### meta-pipe  (14)

| Gọi bằng | Loại | Máy | Làm gì |
|---|---|---|---|
| `/meta-pipe:brainstorm-topic` | kỹ năng | Mac | [Phân tích gộp — bước 0] Động não tương tác để tìm và gọt chủ đề phân tích gộp. Dùng khi chưa có chủ đề rõ, hoặc muốn thử nhiều hướng trước khi chốt câu hỏi. Từ khoá: brainstorm topic. |
| `/meta-pipe:ma-agent-teams` | kỹ năng | Mac | [Phân tích gộp — điều phối] Lập đội agent cho dây chuyền phân tích gộp: tạo đội, sinh thành viên, quản danh sách việc và bàn giao giữa các chặng. Dùng cho đề tài lớn chạy nhiều chặng song song. Từ khoá: agent team orchestration. |
| `/meta-pipe:ma-data-extraction` | kỹ năng | Mac | [Phân tích gộp — bước 5] Định nghĩa khung trích xuất, bóc dữ liệu từ toàn văn và lưu vào cơ sở dữ liệu có cấu trúc. Dùng khi chuyển từ thu thập toàn văn sang phân tích thống kê. Từ khoá: data extraction. |
| `/meta-pipe:ma-end-to-end` | kỹ năng | Mac | [Phân tích gộp — điều phối] Chạy TRỌN dây chuyền phân tích gộp từ file TOPIC.txt tới bản thảo cuối và thư phản hồi phản biện. Dùng khi đã có chủ đề và muốn đi hết một mạch. LƯU Ý: đề tài chính thức của bác sĩ nên đi qua agent `dieu-phoi-… |
| `/meta-pipe:ma-fulltext-management` | kỹ năng | Mac | [Phân tích gộp — bước 4] Thu thập và quản lý PDF toàn văn của các nghiên cứu được chọn, ghi vết nguồn gốc, chuẩn bị tài liệu cho khâu trích xuất. Dùng khi chuyển từ sàng lọc sang trích xuất dữ liệu. Từ khoá: fulltext management. |
| `/meta-pipe:ma-manuscript-quarto` | kỹ năng | Mac | [Phân tích gộp — bước 8] Dựng và kết xuất bản thảo theo cấu trúc IMRaD bằng Quarto, nhúng sẵn hình và bảng. Dùng khi chuyển từ kết quả phân tích sang bản thảo. Từ khoá: Quarto, IMRaD manuscript. |
| `/meta-pipe:ma-meta-analysis` | kỹ năng | Mac | [Phân tích gộp — bước 6] Chạy thống kê gộp bằng R (có renv): ước lượng hiệu ứng, tính không đồng nhất, chẩn đoán sai lệch công bố, xuất hình và bảng. Dùng khi đã trích xuất xong dữ liệu từ các nghiên cứu. Từ khoá: meta-analysis, R, renv. |
| `/meta-pipe:ma-peer-review` | kỹ năng | Mac | [Phân tích gộp — bước 9] Đóng vai Phản biện 1 và Phản biện 2 cho bản thảo phân tích gộp: soi tính chặt chẽ, khả năng tái lập và tuân thủ chuẩn báo cáo. Dùng để tự thử trước khi nộp; KHÔNG thay bình duyệt độc lập thật (cổng G8). Từ khoá: … |
| `/meta-pipe:ma-publication-quality` | kỹ năng | Mac | [Phân tích gộp — bước 7] Kiểm chất lượng mức tạp chí lớn: báo cáo PRISMA/MOOSE, chẩn đoán nâng cao (Hartung-Knapp, khoảng dự báo, phân tích ảnh hưởng), bảng GRADE Summary of Findings, rà khẳng định và đối chiếu chéo. Dùng khi chuẩn bị gó… |
| `/meta-pipe:ma-screening-quality` | kỹ năng | Mac | [Phân tích gộp — bước 3] Sàng lọc tiêu đề và tóm tắt, áp tiêu chuẩn chọn/loại, đánh giá chất lượng và nguy cơ sai lệch. Dùng khi chọn nghiên cứu đủ điều kiện đưa vào gộp. Từ khoá: screening, risk of bias. |
| `/meta-pipe:ma-search-bibliography` | kỹ năng | Mac | [Phân tích gộp — bước 2] Tìm y văn bằng Python (qua uv), truy vấn PubMed và các CSDL khác, khử trùng lặp, lưu thư mục tài liệu theo từng vòng tìm. Dùng khi dựng hoặc cập nhật kho chứng cứ. Từ khoá: literature search, PubMed. |
| `/meta-pipe:ma-topic-intake` | kỹ năng | Mac | [Phân tích gộp — bước 1] Nhận chủ đề từ TOPIC.txt, chuyển thành đề cương PICO/PECO, xác định tiêu chuẩn chọn, kết cục và phạm vi tìm kiếm. Dùng khi khởi động một đề tài phân tích gộp mới. Từ khoá: topic intake, PICO. |
| `/meta-pipe:module-management` | kỹ năng | Mac | [Phân tích gộp — bảo trì] Kiểm và cập nhật sổ đăng ký module của dây chuyền. Dùng sau khi thêm script hoặc tính năng mới, để tài liệu và tích hợp không bị lệch. Từ khoá: module registry. |
| `/meta-pipe:post-to-discussion` | kỹ năng | Mac | [Phân tích gộp — chia sẻ] Đăng đề tài đã hoàn thành lên bảng Discussions của kho meta-pipe trên GitHub. Dùng khi muốn chia sẻ kết quả. LƯU Ý: đây là đăng CÔNG KHAI ra ngoài — kiểm kỹ không còn dữ liệu bệnh nhân hay thông tin định danh tr… |

### codex  (12)

| Gọi bằng | Loại | Máy | Làm gì |
|---|---|---|---|
| `agent codex-rescue` | agent | Mac | [Codex] Agent cứu hộ: dùng khi cần lượt cài đặt hoặc chẩn đoán thứ hai, hoặc giao hẳn một việc lớn cho Codex. Từ khoá: codex rescue agent. |
| `/adversarial-review` | lệnh | Mac | [Codex] Nhờ Codex rà soát theo lối PHẢN BIỆN — chất vấn chính cách tiếp cận và lựa chọn thiết kế. Từ khoá: adversarial review. |
| `/cancel` | lệnh | Mac | [Codex] Huỷ một việc Codex đang chạy nền trong kho mã này. Từ khoá: codex cancel. |
| `/rescue` | lệnh | Mac | [Codex] Giao việc điều tra, sửa lỗi hoặc cứu hộ tiếp nối cho Codex. Dùng khi bí hướng và muốn góc nhìn thứ hai. Từ khoá: codex rescue. |
| `/result` | lệnh | Mac | [Codex] Xem kết quả cuối đã lưu của một việc Codex đã hoàn thành. Từ khoá: codex result. |
| `/review` | lệnh | Mac | [Codex] Nhờ Codex rà soát mã dựa trên trạng thái git hiện tại. Từ khoá: codex review. |
| `/setup` | lệnh | Mac | [Codex] Kiểm Codex CLI đã sẵn sàng chưa và bật/tắt cổng rà soát trước khi dừng phiên. Từ khoá: codex setup. |
| `/status` | lệnh | Mac | [Codex] Xem các việc Codex đang chạy và vừa xong trong kho mã này. Từ khoá: codex status. |
| `/transfer` | lệnh | Mac | [Codex] Chuyển phiên Claude Code hiện tại thành một luồng Codex tiếp tục được. Từ khoá: codex transfer. |
| `/codex:codex-cli-runtime` | kỹ năng | Mac | [Codex] Hợp đồng nội bộ để gọi runtime Codex từ Claude Code. Skill nội bộ, không gọi trực tiếp. Từ khoá: codex runtime. |
| `/codex:codex-result-handling` | kỹ năng | Mac | [Codex] Hướng dẫn nội bộ về cách trình bày kết quả Codex trả về cho người dùng. Từ khoá: codex result. |
| `/codex:gpt-5-4-prompting` | kỹ năng | Mac | [Codex] Hướng dẫn nội bộ soạn câu lệnh cho Codex/GPT-5.4 khi viết mã, rà soát, chẩn đoán, tra cứu. Từ khoá: GPT-5.4 prompting. |

### pubmed-search  (10)

| Gọi bằng | Loại | Máy | Làm gì |
|---|---|---|---|
| `/pubmed-search:pubmed-export-citations` | kỹ năng | Mac | [PubMed 7] Xuất danh mục trích dẫn ra RIS/BibTeX/EndNote/Zotero/Mendeley. Dùng khi chuyển kết quả tìm sang phần mềm quản lý tài liệu. Xuất xong nên chạy /kiem-trich-dan để xác minh PMID/DOI có thật và chưa bị rút. Từ khoá: xuất trích dẫn… |
| `/pubmed-search:pubmed-fulltext-access` | kỹ năng | Mac | [PubMed 5] Lấy TOÀN VĂN hợp pháp — ưu tiên bản truy cập mở (PMC, Unpaywall), trích hình, gợi ý đường truy cập qua thư viện cơ sở. Chỉ lấy bản được phép; KHÔNG vượt tường phí. Từ khoá: toàn văn, tải PDF, truy cập mở, PMC, xin bài. |
| `/pubmed-search:pubmed-gene-drug-research` | kỹ năng | Mac | [PubMed 8] Tra GENE, HOẠT CHẤT và BIẾN THỂ — search_gene, search_compound, search_clinvar (PubChem, ClinVar). Dùng cho câu hỏi dược lý/di truyền, ví dụ ý nghĩa lâm sàng của một biến thể. KHÔNG thay tư vấn di truyền. Từ khoá: gene, biến t… |
| `/pubmed-search:pubmed-mcp-tools-reference` | kỹ năng | Mac | [PubMed 10] Tra cứu đầy đủ 45 công cụ của MCP pubmed-search — dùng khi không nhớ có công cụ nào hoặc muốn gọi thẳng một công cụ cụ thể. Từ khoá: danh sách công cụ, có những công cụ gì, tra cứu công cụ, tool reference. |
| `/pubmed-search:pubmed-multi-source-search` | kỹ năng | Mac | [PubMed 4] Tìm ĐỒNG THỜI nhiều cơ sở dữ liệu — PubMed, Europe PMC, OpenAlex, CORE, Semantic Scholar. Dùng khi cần độ phủ rộng hơn PubMed đơn thuần, hoặc tìm bài ngoài y sinh (kinh tế y tế, khoa học xã hội). Từ khoá: đa nguồn, nhiều cơ sở… |
| `/pubmed-search:pubmed-paper-exploration` | kỹ năng | Mac | [PubMed 6] Lần theo MỘT bài chốt để mở rộng — bài liên quan, bài trích dẫn nó, danh mục tham khảo của nó, cây trích dẫn. Dùng khi đã có một bài quan trọng và muốn tìm hết vùng lân cận (snowballing). Từ khoá: bài liên quan, ai trích dẫn b… |
| `/pubmed-search:pubmed-pico-search` | kỹ năng | Mac | [PubMed 2] Tìm theo câu hỏi lâm sàng PICO — parse_pico tách P/I/C/O rồi dựng truy vấn chạy được. Dùng cho câu hỏi so sánh điều trị ("A có tốt hơn B không"). KHÁC agent cau-hoi-nghien-cuu: agent kia dựng câu hỏi cho ĐỀ TÀI (cổng G0), skil… |
| `/pubmed-search:pubmed-quick-search` | kỹ năng | Mac | [PubMed 1] Tra y văn NHANH một câu hỏi qua unified_search — gộp kết quả nhiều nguồn, trả PMID/DOI. Dùng khi chỉ cần tìm nhanh vài bài, chưa cần chiến lược tìm bài bản. Từ khoá: tra y văn, tìm bài báo, tìm nhanh, search papers, PubMed. |
| `/pubmed-search:pubmed-research-chronicle` | kỹ năng | Mac | [PubMed 9] Dựng BIÊN NIÊN một chủ đề — lĩnh vực tiến triển ra sao theo thời gian, mốc quan trọng, và có gì mới kể từ lần tra trước (lưu lại được, so được giữa các lần). Từ khoá: diễn tiến nghiên cứu, biên niên, mốc quan trọng, có gì mới,… |
| `/pubmed-search:pubmed-systematic-search` | kỹ năng | Mac | [PubMed 3] Tìm HỆ THỐNG, đủ độ phủ cho tổng quan — generate_search_queries mở rộng MeSH và từ đồng nghĩa. Dùng ở bước tìm y văn của tổng quan hệ thống/phân tích gộp; chiến lược tìm phải ghi lại được để tái lặp (PRISMA). Từ khoá: tìm hệ t… |

### desktop-commander  (6)

| Gọi bằng | Loại | Máy | Làm gì |
|---|---|---|---|
| `/desktop-commander:ai-tools-setup` | kỹ năng | Mac | [Máy tính] Cài, nối, kiểm và sửa Claude Desktop cùng các máy chủ MCP. Từ khoá: MCP setup. |
| `/desktop-commander:computer-health-check` | kỹ năng | Mac | [Máy tính] Kiểm tra sức khoẻ máy tính, CHỈ ĐỌC, không thay đổi gì. Từ khoá: health check. |
| `/desktop-commander:desktop-commander-overview` | kỹ năng | Mac | [Máy tính] Tổng quan năng lực Desktop Commander: phiên dòng lệnh lâu dài, thao tác file. Từ khoá: Desktop Commander. |
| `/desktop-commander:knowledge-base` | kỹ năng | Mac | [Máy tính] Tạo và duy trì kho tri thức dạng Markdown cho mọi trợ lý AI dùng chung. Từ khoá: knowledge base. |
| `/desktop-commander:obsidian-vault` | kỹ năng | Mac | [Máy tính] Sắp xếp kho Obsidian: bản đồ nội dung, liên kết wiki, chuẩn hoá frontmatter, bảng điều khiển Dataview, tìm ghi chú mồ côi. Dùng khi bác sĩ nói rõ Obsidian hoặc tính năng riêng của nó; không dùng cho ghi chú Markdown thông thườ… |
| `/desktop-commander:terminal` | kỹ năng | Mac | [Máy tính] Dùng Desktop Commander cho công việc dòng lệnh. Từ khoá: terminal. |

### c8d66619-8921-4ca6-9bfe-6aa306ae74cb  (6)

| Gọi bằng | Loại | Máy | Làm gì |
|---|---|---|---|
| `agent fast-finder` | agent | Mac | The way into KNOWLEDGE.md, KNOWHOW.md and REFEREE.md. Call instead of reading any of them when you need what is known about a symptom, a file, or a function. Returns the few entries that bear on the question, verbatim, and says plainly w… |
| `agent old-man` | agent | Mac | Call before concluding that a paper does not contain something, or before writing a pattern whose match decides presence. Names the alternative spellings and layouts a real paper might use that would defeat the pattern, with how often th… |
| `agent question-monster` | agent | Mac | Call after concluding that something is unsupported, cannot be expressed, or has to be dropped. Checks the record for approaches already reverted, then pushes for a concrete equivalent instead of accepting the first concession, and stops… |
| `agent referee` | agent | Mac | Watches the run as a whole rather than any one chunk. Reads the distribution of check failures across chunks, roles and books, decides whether a repeat belongs to an agent, a brief or a tool, and issues at most a short caution. Also watc… |
| `/release` | lệnh | Mac | Release a new version to GitHub |
| `/c8d66619-8921-4ca6-9bfe-6aa306ae74cb:translate-book` | kỹ năng | Mac | Translate an arXiv paper, or any PDF/DOCX/EPUB book, into any language as a printable book. For arXiv papers it reads the LaTeX source, so equations, tables, figures and numbering survive. Parallel sub-agents translate the chunks; output… |

### pdf-viewer  (5)

| Gọi bằng | Loại | Máy | Làm gì |
|---|---|---|---|
| `/annotate` | lệnh | Mac | [Tài liệu] Chú thích PDF cùng nhau — đề xuất đánh dấu, cùng xem lại và chỉnh dần. Từ khoá: annotate PDF. |
| `/fill-form` | lệnh | Mac | [Tài liệu] Điền biểu mẫu PDF với xem trước trực tiếp từng ô. Từ khoá: fill PDF form. |
| `/open` | lệnh | Mac | [Tài liệu] Mở một file PDF trong trình xem tương tác. Từ khoá: open PDF. |
| `/sign` | lệnh | Mac | [Tài liệu] Đặt chữ ký hoặc chữ viết tắt lên file PDF. LƯU Ý: chỉ chèn hình ảnh chữ ký sẵn có, không thay việc bác sĩ tự ký văn bản pháp lý. Từ khoá: sign PDF. |
| `/pdf-viewer:view-pdf` | kỹ năng | Mac | [Tài liệu] Trình xem PDF tương tác — mở, xem và đánh dấu tài liệu ngay trong phiên. Dùng khi cần nhìn tận mắt nội dung file PDF; không dùng để tóm tắt hay trích xuất chữ, việc đó đọc thẳng file nhanh hơn. Từ khoá: PDF viewer. |

### claude-tag-troubleshoot  (3)

| Gọi bằng | Loại | Máy | Làm gì |
|---|---|---|---|
| `/debug-plugins` | lệnh | Mac | [Hỗ trợ] Chẩn đoán vì sao một plugin hoặc skill không hoạt động như mong đợi. Từ khoá: plugin debug. |
| `/claude-tag-troubleshoot:config-guide` | kỹ năng | Mac | [Hỗ trợ] Tài liệu tra cứu cách cấu hình các agent @Claude. Từ khoá: config guide. |
| `/claude-tag-troubleshoot:debug-plugins` | kỹ năng | Mac | [Hỗ trợ] Chẩn đoán vì sao một plugin hoặc skill không hoạt động như mong đợi. Từ khoá: plugin debug. |

### cochrane  (2)

| Gọi bằng | Loại | Máy | Làm gì |
|---|---|---|---|
| `/cochrane` | lệnh | Mac | Search the Cochrane Library and summarise the top systematic reviews for a question. |
| `/cochrane:cochrane` | kỹ năng | Mac | Use when answering clinical/health evidence questions or asked about systematic reviews, randomised trials, or "what does Cochrane say" — searches the Cochrane Library and fetches review/trial details. |

### humanizer  (1)

| Gọi bằng | Loại | Máy | Làm gì |
|---|---|---|---|
| `/humanizer:humanizer` | kỹ năng | Mac | [Viết lách] Xoá dấu vết văn phong máy trong một đoạn văn bản. Dùng khi biên tập bài viết cho tự nhiên hơn. Từ khoá: humanizer, AI-generated writing. |

### 94f9f849-9134-41a1-a321-c4df6c433a1c  (1)

| Gọi bằng | Loại | Máy | Làm gì |
|---|---|---|---|
| `/94f9f849-9134-41a1-a321-c4df6c433a1c:paper-search` | kỹ năng | Mac | Search for academic papers by keyword, or look up a specific paper by DOI or OpenAlex ID. Powered by OpenAlex (250M+ works, free, no API key). |

### 498fad65-201a-4cfe-8bf1-5b9f28aadfac  (1)

| Gọi bằng | Loại | Máy | Làm gì |
|---|---|---|---|
| `/498fad65-201a-4cfe-8bf1-5b9f28aadfac:search` | kỹ năng | Mac | Search Google, Bing, Amazon, Walmart, YouTube, Google Maps, Google Scholar, and 100+ other engines via the SerpApi REST API. Calls the API using curl. Use when the user wants to search the web, find products or prices, look up local busi… |

### google-drive  (1)

| Gọi bằng | Loại | Máy | Làm gì |
|---|---|---|---|
| `/google-drive:google-drive-api` | kỹ năng | Mac | [Kết nối] Tìm, đọc, tạo, cập nhật và chia sẻ file trên Google Drive. Từ khoá: Google Drive. |

---

## TẦNG 3 — Ngoài chuyên môn (biết là có, hiếm khi dùng)  (0 mục)

