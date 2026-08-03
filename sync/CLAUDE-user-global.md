# Ngôn ngữ làm việc — chỉ thị toàn cục

Áp dụng cho MỌI dự án, MỌI thư mục, MỌI skill/plugin/agent trên máy này.

## Quy tắc nền
1. **Mọi nội dung trả cho tôi đều bằng tiếng Việt** — kể cả việc kỹ thuật: git, lỗi build,
   tóm tắt code, giải thích thuật toán, báo cáo test. KHÔNG mặc định tiếng Anh chỉ vì tài
   liệu nguồn, skill hay plugin viết bằng tiếng Anh.
2. **Skill/plugin/agent viết bằng tiếng Anh vẫn được tuân thủ ĐẦY ĐỦ về nội dung** — chỉ đổi
   ngôn ngữ ĐẦU RA. Hướng dẫn tiếng Anh bên trong skill là chỉ dẫn dành cho Claude, KHÔNG
   phải yêu cầu trả lời bằng tiếng Anh.
3. Câu hỏi tôi gõ bằng tiếng Anh cũng trả lời bằng tiếng Việt, trừ khi tôi nói rõ muốn tiếng Anh.

## GIỮ NGUYÊN, không dịch
- Tên lệnh, cờ CLI, tên tool/skill/agent, tên file và đường dẫn.
- Mã nguồn: tên hàm/biến/lớp, chuỗi ký tự trong code, khoá JSON/YAML.
- Thông điệp lỗi khi trích nguyên văn (muốn diễn giải thì thêm câu tiếng Việt bên dưới).
- Tên chuẩn quốc tế: CONSORT, STROBE, PRISMA, SPIRIT, STARD, TRIPOD+AI, GRADE, ICMJE,
  QUADAS, RoB 2, COSMIN…; mã định danh PMID / DOI / NCT.
- Thuật ngữ chuyên ngành chưa có tương đương chuẩn: dùng tiếng Việt kèm tiếng Anh trong
  ngoặc ở lần xuất hiện đầu — ví dụ "nguy cơ sai lệch (risk of bias)".

## Ngoại lệ — ngôn ngữ của SẢN PHẨM đầu ra
Ngôn ngữ của TÀI LIỆU tôi đặt hàng theo đúng yêu cầu của tài liệu đó, không theo quy tắc chat:
- Bản thảo / abstract / cover letter / thư phản hồi phản biện nộp tạp chí quốc tế → tiếng Anh.
- Đề cương, hồ sơ Hội đồng Đạo đức, phiếu đồng thuận, tài liệu cho bệnh nhân, tờ dặn dò → tiếng Việt.
- Không rõ → HỎI tôi trước khi viết, đừng tự đoán.

Phần trao đổi, giải thích và báo cáo quanh tài liệu vẫn bằng tiếng Việt, kể cả khi bản thân
tài liệu viết bằng tiếng Anh.

## Commit và mã nguồn
- Thông điệp commit: tiếng Việt (theo lệ đang dùng trong các repo của tôi).
- Docstring và comment trong code: tiếng Việt.
- Tên biến/hàm/lớp: tiếng Anh theo thông lệ lập trình.

## Lưu ý bảo trì
File này nằm ở `~/.claude/CLAUDE.md`, **NGOÀI cây OneDrive** → không tự đồng bộ sang máy
khác. Khi dùng máy mới phải chép lại bằng tay. Bản sao tham chiếu để chép:
`<OneDrive>/Claude AI/sync/CLAUDE-user-global.md`.
