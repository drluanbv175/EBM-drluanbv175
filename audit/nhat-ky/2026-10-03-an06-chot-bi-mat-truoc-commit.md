# 03/10/2026 — AN-06: pre-commit không có chốt bí mật/PII nào (repo công khai, sắp có khoá Ed25519 thật)

**Số đo (kiểm toàn diện 02/10).** `.githooks/pre-commit` của repo gốc gọi 7 công cụ, repo y khoa gọi 2; không công cụ nào quét bí
mật/PII. GitHub secret scanning chỉ chặn mẫu của NHÀ CUNG CẤP khi push (mẫu tuỳ chỉnh đang tắt). Thư mục
`config/gate_ed25519_pubkeys/` vốn để commit, nên một tệp khoá riêng lạc vào đó sẽ được stage mà không ai báo.

**Vá.**
- `tools/kiem_bi_mat_truoc_commit.py` (stdlib) quét DÒNG THÊM của phần stage (`git diff --cached -U0`), nên không báo oan nội dung cũ.
  - **CHẶN:** khối PRIVATE KEY · token Anthropic/OpenAI/GitHub/Slack/AWS/Google · URL kèm user:mật-khẩu tới máy THẬT · tệp khoá
    (`.pem/.key/.p12/.pfx`, `id_rsa*`, tệp biến môi trường thật, `gate_approval_key_*`, tệp không phải `.pub` trong thư mục khoá công).
  - **CẢNH BÁO:** gán khoá/mật khẩu dài, số điện thoại VN, số 12 chữ, email cá nhân, URL kèm mật khẩu tới máy CỤC BỘ / dịch vụ docker
    một nhãn / miền thử.
  - Không in giá trị khớp. Miễn trừ theo dòng: `bimat-mien: <lý do>`. `--tat-ca` đo mọi tệp đã track.
- Nối vào `.githooks/pre-commit` (gốc) trước `exit 0`.

**Hiệu chỉnh bằng số đo.**
- `--tat-ca` repo gốc: 0 chặn, 27 cảnh báo (email mẫu trong test…), 2,5 giây.
- Repo y khoa ban đầu: 7 chặn «URL kèm mật khẩu», đều là chuỗi mẫu dev (`postgres:5432` trong docker-compose, `proxy.local` trong
  test). Hạ xuống cảnh báo khi máy chủ là cục bộ / một nhãn / miền thử ⇒ 0 chặn.

**Kiểm.**
- 26 test, kho git tạm, cấu hình git cô lập. Token giả GHÉP lúc chạy để chính tệp test không bị chặn.
- 6 đột biến đều bị bắt: bỏ mẫu PEM · coi mọi URL là cục bộ · bỏ miễn trừ · quét cả dòng cũ · bỏ chặn tên tệp khoá · thư mục khoá
  công nhận mọi tệp.

**Còn lại.** Repo y khoa chưa gắn chốt này vào pre-commit của nó (PR y khoa #68 đang sửa cùng tệp hook — làm sau khi #68 gộp, chép
công cụ sang repo y khoa).
