# 17/11/2026 — Gọi API Claude: cổng kiểm chủ đề cụt trên dashboard lớn mà im lặng, nuốt «uncertain»; CAFÉ-S đo sai (BH180)

**Mã:** BH180 · liền sau BH179 (vá nguồn không tới bản chạy) · cùng họ §0.2 («không đo được» ≠ «ổn»).

## Đo được gì (17/11/2026)

Rà toàn bộ điểm gọi API Claude của hai repo sau khi bác sĩ hỏi «đề xuất và giải quyết vấn đề API tốt nhất».
Không còn mã model thế hệ cũ nào; ba điểm gọi: cổng kiểm lạc chủ đề (dây chuyền), `tools/eval/cafes_suite.py
--api` (đo đội agent lâm sàng), `medical-ebm-automation/runtime/claude_api_runtime.py` (nhánh mồ côi, không đụng).

1. **Cổng kiểm chủ đề bị CẮT CỤT trên dashboard lớn.** `call_claude` gọi Sonnet 5.5 với `max_tokens=2000`, không
   đặt effort. Trên Sonnet 5.5 thinking luôn bật và ăn CHUNG ngân sách với JSON phán quyết. Lượt thật trên
   `WebDashboard_EBM_VanDeCuThe_SuyTim_TongHop_20261113.html` (83 mục, 25.521 token vào):
   `stop_reason=max_tokens`, ra 2000/2000, JSON hỏng (0,071 USD). Bộ vàng 19 mục đã dùng 1.427/2.000 token
   (~75 token/mục) ⇒ trần cũ tràn quanh ~26 mục. 303 dashboard: trung vị 32 mục, 181 cái ≥ 25, 116 cái ≥ 40,
   lớn nhất 83 (ước vùng hỏng từ số đo, chưa chạy từng cái).
2. **Cụt mà IM LẶNG.** JSON hỏng ném `TopicCheckError` ⇒ `status: "skipped"` — cùng nhóm với «thiếu khoá». Cảm
   biến ⑦r chỉ báo «skipped» khi lý do nhắc `ANTHROPIC_API_KEY` ⇒ cổng trơ mà hòm việc không bao giờ báo.
3. **Nuốt «uncertain».** `check_topic_relevance` trả ba mức, `verify_dashboard` chỉ đọc `off_topic`, nên
   dashboard có mục LLM không đủ thông tin vẫn in «N/N item đều khớp». Lượt thật đầu tiên (17/11) có 1 mục
   uncertain; dashboard hôm nay có 0 — câu «13/13 đều khớp» của nó đúng là nhờ may.
4. **CAFÉ-S `--api` chưa từng chạy được, và chạy sẽ đo sai.** `Anthropic()` chỉ đọc biến môi trường (khoá
   chỉ nằm trong kho ⇒ chết ngay, cùng họ #402); `max_tokens=1500` trên Opus 5.5 ⇒ dễ cụt ⇒ chấm TRƯỢT oan;
   không kiểm stop_reason; một lỗi API giết cả lượt; thiếu tệp agent ⇒ lặng lẽ chạy model TRẦN; không cache
   system prompt (14.722 + 12.420 token × 32 ca); không in chi phí.
5. Chốt chuẩn vàng của cổng (`EBM-Dashboards/tools/test_check_topic_relevance.py`) nằm NGOÀI git — CI không chạy;
   chốt «thiếu khoá» từ khi có kho bí mật sẽ đọc khoá THẬT và gọi API thật; chốt tích hợp xoá vô điều kiện
   biến môi trường `ANTHROPIC_API_KEY`.

## Cách vá

- `check_topic_relevance.py` (2 bản khớp byte): `max_tokens` 16000, `output_config.effort="low"` (phân loại),
  dự phòng khi từ chối `fallbacks: "default"` (beta `server-side-fallback-2026-07-01`) cho model hiện hành —
  model khác (đặt qua `TOPIC_CHECK_MODEL`) gọi như cũ để khỏi 400; kiểm `stop_reason` TRƯỚC khi đọc nội dung;
  lớp `KetQuaApiHong` (con của `TopicCheckError`) ⇒ cụt / từ chối / JSON hỏng là `status: "error"`. Prompt sinh
  ra giữ nguyên y như master.
- `verify_dashboard.py` (2 bản khớp byte): mỗi mức một dòng — lạc chủ đề, KHÔNG CHẮC, «đều khớp» chỉ khi cả hai rỗng.
- `cafes_suite.py`: khoá qua chính `_khoa_tu_kho` của cổng (một nguồn sự thật); `max_tokens` 16000; effort tường
  minh (mặc định high, `--effort`); cache system prompt; dự phòng khi từ chối; kiểm stop_reason; ba trạng thái
  pass True/False/None — ca không đo được không tính đạt hay trượt, cổng critical còn ca chưa đo ⇒ «KHÔNG ĐỦ ĐO»
  (khi mọi ca đo được, kết quả TRÙNG KHÍT bản cũ: mock 32 PASS · 31 FAIL · 0 FAIL); thiếu tệp agent / lỗi khoá /
  400 ⇒ dừng cả lượt; `--uoc-tinh` ước chi phí bằng count_tokens (miễn phí); in chi phí THẬT sau lượt chạy.
- Chốt chuẩn vàng đưa vào nguồn chuẩn (vá ba chỗ: chuyển hướng kho khoá, khôi phục biến môi trường, lượt thật chỉ
  khi `EBM_KIEM_API_THAT=1`); `tools/test_check_topic_relevance_20261117.py` cho CI thu nó.

## Số đo sau vá

| | Bộ vàng 19 mục | Token ra | Dashboard 83 mục |
|---|---|---|---|
| Cũ (max 2000, effort mặc định) | 18/19 (95%) | 1.427 | cụt, JSON hỏng |
| Mới (max 16000, effort low) | 18/19 (95%) | 1.335 | ok, 83/83 |

Mục lệch duy nhất là ITEM-11 — chính tệp chuẩn vàng ghi «ground-truth gây tranh cãi». Hạ effort không làm kém.

CAFÉ-S `--uoc-tinh` (count_tokens, miễn phí): 446.857 token vào ⇒ 1,787 USD không cache · 0,224 USD có cache;
ra giả định 1.000–4.000 token/ca ⇒ tổng ước 0,86–2,78 USD một lượt. Lượt đo thật chưa chạy — chờ bác sĩ.

## Kiểm hồi quy

- `tools/test_check_topic_relevance_20261117.py` (19 đạt, 1 bỏ qua có khai báo — lượt thật cần opt-in),
  `tools/test_cafes_api_20261117.py` (15), `tools/test_xuat_goi_cap_nhat_check_topic_20261117.py` (SDK giả có kênh beta).
- BH180 — khoá hành vi ngoại tuyến bằng SDK giả.
- Đột biến 10/10 bị bắt (max_tokens về 2000 · bỏ effort · hỏng quy về skipped · bỏ kiểm cụt · verify nuốt uncertain ·
  CAFÉ-S max 1500 · thiếu agent lặng lẽ · cổng critical PASS khi còn ca chưa đo · bỏ cache · ca cụt tính là kết quả);
  phục hồi khớp byte.
- `pytest tools/` (đúng lệnh CI) trên worktree: 5031 đạt, 39 bỏ qua.

Chi phí mọi lượt đo thật hôm nay ≈ 0,15 USD (xấp xỉ, giá Sonnet 5.5).

## Bài học

Đọc `stop_reason` TRƯỚC khi đọc nội dung, và trên model có thinking luôn bật thì `max_tokens` là ngân sách CHUNG —
đặt rộng (token trần không tính tiền) và đặt effort theo việc. «API trả lời mà kết quả hỏng» là LỖI, không bao
giờ được gộp với «chưa cấu hình».
