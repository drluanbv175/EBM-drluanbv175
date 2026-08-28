# Nguồn chính thức và quy tắc kiểm tra cập nhật

## Nguyên tắc

Mọi nội dung pháp lý, chuẩn báo cáo, đăng ký nghiên cứu, liêm chính xuất bản và yêu cầu kỹ thuật Claude Skills có thể thay đổi. Khi có truy cập internet, kiểm tra nguồn chính thức trước khi hoàn tất tài liệu chính thức; nếu không kiểm tra được, ghi `[CẦN KIỂM CHỨNG NGUỒN CHÍNH THỨC]`.

## Danh mục nguồn nền tảng đã kiểm tra ngày 2026-05-30

| Lĩnh vực | Nguồn ưu tiên | Tình trạng/điểm cần dùng |
|---|---|---|
| Claude Skills | Anthropic Platform Docs: Agent Skills overview; Skill authoring best practices | `SKILL.md` bắt buộc có `name`, `description`; `name` tối đa 64 ký tự; `description` tối đa 1024 ký tự; nên viết gọn và kiểm thử thực tế |
| Đạo đức nghiên cứu người tham gia | World Medical Association, Declaration of Helsinki | Bản sửa đổi 2024; rủi ro-lợi ích, quyền người tham gia, công bằng, bảo vệ dữ liệu |
| Thử nghiệm lâm sàng | ICH E6(R3) Good Clinical Practice | Step 4 Final Guideline, 2025; quality by design và giám sát dựa trên nguy cơ |
| Reporting guidelines | EQUATOR Network; website guideline gốc | Kiểm tra chuẩn/extension đúng thiết kế và phiên bản hiện hành |
| Thử nghiệm ngẫu nhiên | CONSORT-SPIRIT | CONSORT 2025 và SPIRIT 2025 |
| Công bố y khoa | ICMJE Recommendations | Cập nhật tháng 01/2026; AI trong xuất bản và quyền tác giả truy cập dữ liệu |
| PROM/thang đo | COSMIN | Phát triển, thích nghi, measurement properties và reporting |
| Chứng cứ/khuyến cáo | GRADE Working Group/GRADEpro | Phân biệt certainty of evidence và strength of recommendation |
| Việt Nam: dữ liệu cá nhân | Cổng Văn bản Chính phủ | Luật 91/2025/QH15, ban hành 26/06/2025, hiệu lực 01/01/2026 |
| Việt Nam: khám chữa bệnh | Cổng Văn bản Chính phủ | Luật 15/2023/QH15, hiệu lực 01/01/2024 |
| Việt Nam: Hội đồng đạo đức | CSDL quốc gia về VBPL/Bộ Y tế | Thông tư 43/2024/TT-BYT, ban hành 12/12/2024, hiệu lực 01/02/2025 |

## Tái kiểm chứng nguồn sơ cấp (2026-05-30)

Các mục sau đã được đối chiếu trực tiếp với nguồn gốc chính thức trong lần rà soát này; các mục khác trong bảng trên giữ trạng thái cần kiểm tra lại trước mỗi sản phẩm chính thức.

- Declaration of Helsinki: bản sửa đổi 2024, thông qua tại Đại hội đồng WMA lần thứ 75 (Helsinki, 19/10/2024); là bản chính thức duy nhất, các bản trước chỉ dùng cho mục đích lịch sử. `[ĐÃ KIỂM CHỨNG: wma.net]`
- ICH E6(R3) GCP: Step 4 Final Guideline (2025). `[ĐÃ KIỂM CHỨNG: database.ich.org]`
- CONSORT 2025 và SPIRIT 2025: công bố đồng thời 2025 trên BMJ/JAMA/Lancet/Nature Medicine/PLOS Medicine; CONSORT 2025 có checklist 30 mục và mục Open Science mới; SPIRIT 2025 có checklist 34 mục. `[ĐÃ KIỂM CHỨNG: consort-spirit.org]`
- ICMJE Recommendations: bản cập nhật 01/2026, có Section V mới về AI, yêu cầu mới về quyền truy cập dữ liệu trong hợp tác có tài trợ/công nghiệp, và siết kiểm tra đăng ký thử nghiệm lâm sàng. `[ĐÃ KIỂM CHỨNG: icmje.org]`

## Tái kiểm chứng bổ sung (2026-06-06)

Đối chiếu lại văn bản pháp luật Việt Nam với nguồn sơ cấp; không phát hiện thay đổi so với rà soát 2026-05-30:

- Thông tư 43/2024/TT-BYT: ban hành 12/12/2024; **hiệu lực 01/02/2025** theo Điều 22 ("Thông tư này có hiệu lực thi hành kể từ ngày 01 tháng 02 năm 2025"); thay thế Thông tư 04/2020/TT-BYT (05/3/2020). `[ĐÃ KIỂM CHỨNG: thuvienphapluat.vn; moh.gov.vn]`
- Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15: thông qua 26/6/2025; **hiệu lực 01/01/2026** (đã có hiệu lực tại thời điểm rà soát). `[ĐÃ KIỂM CHỨNG: chinhphu.vn; bocongan.gov.vn; vbpl.vn]`

## Liên kết nguồn gốc để kiểm chứng

- Anthropic Agent Skills overview: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- Anthropic Skill authoring best practices: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- WMA Declaration of Helsinki: https://www.wma.net/policies-post/wma-declaration-of-helsinki/
- ICH E6(R3) Final Guideline: https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf
- EQUATOR reporting guidelines library: https://www.equator-network.org/reporting-guidelines/
- CONSORT-SPIRIT: https://www.consort-spirit.org/
- PRISMA: https://www.prisma-statement.org/
- ICMJE Recommendations: https://www.icmje.org/recommendations/
- COSMIN: https://www.cosmin.nl/
- GRADE Working Group: https://www.gradeworkinggroup.org/
- Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15: https://vanban.chinhphu.vn/?classid=1&docid=214590&pageid=27160&typegroupid=3
- Luật Khám bệnh, chữa bệnh 15/2023/QH15: https://vanban.chinhphu.vn/?docid=207396&pageid=27160
- Thông tư 43/2024/TT-BYT: https://vbpl.vn/boyte/Pages/vbpq-thuoctinh.aspx?ItemID=172919

## Quy trình kiểm chứng trước một sản phẩm chính thức

1. Ghi ngày kiểm tra nguồn.
2. Mở nguồn chính thức, xác định số hiệu, phiên bản, ngày hiệu lực hoặc ngày cập nhật.
3. Chọn chuẩn báo cáo đúng thiết kế; tìm extension nếu nghiên cứu đặc thù.
4. Kiểm tra yêu cầu của Hội đồng đạo đức/đơn vị/tạp chí đích.
5. Ghi vào bảng tuân thủ: chuẩn, phiên bản, nguồn, mục đã áp dụng, mục chưa đạt.
6. Khi không xác minh được, không khẳng định đã tuân thủ; ghi trạng thái cần kiểm chứng.
