# 09/10/2026 — G0: chấm lại không được kéo theo dựng lại nền bằng chứng · trạng thái checkpoint lấy từ bộ chấm · chiến lược tìm tái lập được

Bác sĩ giao: «Tiếp tục hoàn thiện hệ thống nghiên cứu của tôi». Thi công phần CÔNG CỤ mà hai biên bản tranh biện hội đồng
cổng G0 của đề tài C1a (07/10, `hoi_dong/G0/G0-TB-20261007T192719-*`, TƯ VẤN) khuyến nghị —
drluanbv175/medical-ebm-automation#99 (nhánh `claude/g0-bo-sinh-bo-ghi-20261009`). Hội đồng không mở/chặn cổng; mọi cờ xác nhận của PI giữ nguyên.

## Vấn đề (đo trên C1a)

1. **Ghi trạng thái G0 ⇒ dựng lại nền bằng chứng (BD-G0-T1, P1).** Bộ chấm `g0_quality_gate.py` chế độ ghi, khi G0 còn
   DRAFT, đặt `needs_input.blocked = true` (MISSING_PICO). `run_pipeline.py` coi checkpoint bị chặn là phải CHẠY LẠI cổng ⇒
   gọi `run_g0_auto.py` ⇒ tra lại PubMed (tập PMID và dấu vân tay có thể đổi, A1 sinh lại) — trong khi việc còn lại là của
   PI và lệnh khắc phục ghi trong chính `needs_input` là «chấm lại bằng g0_quality_gate». Hội đồng phải khuyên «tạm đừng chạy
   bộ chấm ở chế độ ghi».
2. **`gate_status` / `pending_doctor_actions` in cứng (BD-G0-T1, P2).** `run_g0_auto.write_checkpoint` ghi hằng
   «DRAFT — CHỜ BÁC SĨ CHỐT PICO…» + 6 việc cố định; `refresh_checkpoint` không đụng hai khoá này. Đo chỉ-đọc 09/10 trên C1a:
   checkpoint lưu «CHỜ BÁC SĨ CHỐT PICO», «Điền PICO 4 thành phần…» trong khi chấm sống: HUMAN-01..04 ĐẠT, chỉ còn
   HUMAN-05..08 (FINER, đọc bằng chứng/tính mới, PI chốt, tra ICTRP). `run_g8_auto.py` in nguyên danh sách cũ vào bảng tồn đọng.
3. **Thông điệp `needs_input` luôn nói «PICO/kết cục chính/FINER còn trống»** kể cả khi câu hỏi đã đạt.
4. **`G0_pubmed_raw.json` chỉ có danh sách bài (BD-G0-T2).** Không ghi CSDL, ngày tra, chuỗi gửi PubMed, bộ lọc thiết kế,
   trần số bài từng nhánh ⇒ không tái lập/thẩm định được lượt tìm (PRISMA-S), không dựng được gói tìm bổ sung cho PI.

## Vá (repo y khoa)

- `run_pipeline._g0_chi_cho_nguoi`: G0 chặn vì MISSING_PICO + checkpoint `n_pmids > 0` + có `G0_pubmed_raw.json` (và không
  `--from G0`, không cũ) ⇒ chỉ chạy `g0_quality_gate.py --study … --exports-dir …`. `--from G0`/G0 cũ/0 PMID/lý do khác ⇒
  chạy trọn như trước.
- `g0_quality_gate.dong_bo_trang_thai_checkpoint`: `gate_status` từ kết quả chấm (0 PMID và guardrail bẩn giữ ưu tiên;
  CONFIRMED ⇒ không còn việc; DRAFT ⇒ liệt kê đúng mã HUMAN còn chờ) + `pending_doctor_actions` = việc thật + lệnh chấm lại.
  Gọi ở CẢ `refresh_checkpoint` lẫn đường chạy trọn `run_g0_auto.main`.
- Thông điệp `needs_input` nói đúng: câu hỏi đã đạt ⇒ «ĐÃ đạt — còn chờ PI: …; không cần tra lại PubMed». Mã lý do giữ
  MISSING_PICO (nơi khác gỡ cờ theo mã này).
- `G0_pubmed_raw.json → search_provenance`: CSDL, giao diện, ngày tra, truy vấn gốc, `query_en` do người cấp hay không, từng
  nhánh (truy vấn, bộ lọc, chuỗi hiệu lực `(<truy vấn>) AND <bộ lọc>`, trần, có loại trùng PMID không, số hit thật, PMID
  lấy về), lỗi nhánh. Các nơi đọc tệp (G1 `raw.values()` chỉ lấy danh sách; `check_de_cuong` gom khoá chứa «pmid» — tập
  con PMID đã có) không đổi hành vi.
- `run_g8_auto._gate_pending_actions`: với G0, khoá có mặt mà rỗng ⇒ «không còn việc» thay vì câu mặc định «Xac nhan PICO».

Phần hội đồng khuyến nghị mà PR này CHƯA làm (để PR sau, cần PI chọn chuỗi): nhánh tìm không lọc thiết kế cho đề tài quan
sát, chế độ dựng lại A1 từ `G0_pubmed_raw.json`, gợi ý thiết kế theo loại câu hỏi, nhãn `[CẦN…]` thay «[suy ra từ topic]».

## Dạy agent (repo gốc, PR này)

`.claude/agents/dieu-phoi-g0.md` §4 thêm «Chấm lại ≠ dựng lại»; mirror Codex sinh lại; bản y hệt ở repo y khoa đi cùng PR y khoa.

## Kiểm

- `tests/test_g0_bo_sinh_bo_ghi_hoi_dong_20261009.py` (repo y khoa): 13 ca. Đột biến 15/15 bị bắt (không bao giờ chấm lại ·
  bỏ kiểm mã lý do · bỏ kiểm n_pmids · bỏ kiểm tệp raw · phớt lờ `--from` · phớt lờ stale · refresh không đồng bộ ·
  `run_g0_auto` không đồng bộ · bỏ ưu tiên 0 PMID · bỏ dòng lệnh chấm lại · thông điệp luôn kiểu cũ · vá G8 áp cho mọi cổng ·
  G8 bỏ nhánh rỗng · chuỗi hiệu lực sai · CONFIRMED vẫn còn việc); khôi phục byte-y-hệt.
- Nhóm test G0/pipeline/G8/đầu–cuối G10: 746 qua. Bộ đầy đủ repo y khoa: 8298 qua, 44 bỏ qua; `exports/` 70 → 70 tệp (không xả rác).
- Đo chỉ-đọc trên C1a (không ghi tệp nào — so SHA-256 trước/sau): nếu chấm lại ở chế độ ghi, checkpoint sẽ mang
  «DRAFT — CHỜ BÁC SĨ: G0-HUMAN-05, G0-HUMAN-06, G0-HUMAN-07, G0-HUMAN-08» và 5 việc thật.
