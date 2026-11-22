# 22/11/2026 — Nguyên tắc tổng nghiên cứu: sửa đúng khâu rồi khoá · giao sản phẩm · 8 nguyên tắc · không sổ nợ

## Chỉ thị (nguyên văn bác sĩ, 22/11/2026)

- **Nguyên tắc tổng:** «Mỗi quyết định trong nghiên cứu phải dựa trên bằng chứng khoa học, được thực hiện một cách đạo
  đức, được kiểm chứng khách quan, và chỉ được chuyển sang bước tiếp theo khi bước hiện tại đã đạt chuẩn xác định
  trước.»
- «Khi phát hiện một vấn đề không đúng trong quy trình thực hiện nghiên cứu thì hệ thống phải quay lại bước đó để sửa,
  kiểm tra lại, sau khi đạt chuẩn thì "khóa" bước đó và mới cho phép chuyển sang bước tiếp theo. Chứ cứ làm hoài và mãi
  luôn phải chỉnh sửa hoài; Hãy ghi nhớ và cập nhật vào hệ thống»
- «Khi tôi đã giao nhiệm vụ thì hãy bám vào nguyên tắc xây dựng hệ thống và giao cho tôi sản phẩm đúng; Đừng bao giờ để
  nói là phần việc máy, phần của tôi, bạn phải đứng trên vai trò của bạn; Hãy tiếp tục nhắc đi nhắc lại nhiều lần»
- «Đề cương nghiên cứu theo từng tiêu chuẩn và từng tiêu chuẩn trong từng cấu trúc đề cương nghiên cứu phải Tính trung
  thực và minh bạch (Integrity), Tính khoa học (Scientific Validity), Tính đạo đức (Ethical Conduct), Tính khách quan
  (Objectivity), Tính tái lập (Reproducibility), Tính hợp lệ và tin cậy (Validity & Reliability), Tôn trọng đối tượng
  nghiên cứu, Kiểm soát chất lượng liên tục»
- «ghi nhỏ sổ nợ sẽ không ghi sổ nợ nữa, giải quyết theo nguyên tắc»

## Nguyên nhân gốc

Không lệnh nào trả lời gọn «khâu nào đang mở, sửa ở đâu, cổng nào chỉ còn chờ ký». Agent phát hiện lỗi ở khâu trước
nhưng vá văn bản ở khâu sau (đề cương G10, SAP, bản thảo) — lần sinh lại kế tiếp xoá bản vá, lỗi quay lại. Báo cáo cuối
lượt chia «phần máy / phần của bác sĩ» thay vì nói về sản phẩm đã giao và gói ký đã chuẩn bị. Sổ nợ/bánh cóc cho phép
chốt xanh khi chuẩn chưa đạt.

## Cách vá

- **Repo y khoa:** `tools/buoc_dang_mo.py --study <mã> [--json] [--goc <thư mục chứa exports/>]`, CHỈ ĐỌC. Công cụ chấm
  sống G0→G10 theo thứ tự số bằng `cong_song.trang_thai_song`.
  - Khoá = PASS; riêng G2 = `g7_quality_gate.g2_da_duyet`, cùng nghĩa mà G5–G10 dùng. READY và «không đo được» không
    bao giờ là khoá.
  - Công cụ in:
    - khâu đang mở;
    - gói ký đã chuẩn bị: cổng cứng READY; cổng thường READY hoặc «DRAFT_READY_…»; `hoi_dong_cong.trach_nhiem` trả mã
      0; vai cổng cứng lấy từ `gate_contract._GATE_REQUIRED_STAKEHOLDERS`;
    - khâu cần hoàn thiện — chỗ duy nhất được sửa;
    - cổng «chưa được làm tiếp — sinh lại sau khi khâu mở được khoá»;
    - cổng khoá ngoài thứ tự.
  - Mã thoát 0/1/2/3. Lời trình bày nói về sản phẩm; khoá máy-đọc giữ nguyên.
- **Repo gốc:**
  - `_HOI-DONG-CONG.md` §1c: nguyên tắc tổng đứng đầu, rồi 9 mục triển khai (khâu đang mở · sửa tại nguồn · kiểm bằng
    chốt của khâu · khoá rồi đi tiếp · một gói ký · ma trận đề cương phần × chuẩn × 8 nguyên tắc, ô chưa đo là ⚪ ·
    không sổ nợ · giao sản phẩm · nhắc lại).
  - Bước 1 của «Tám bước» chạy `buoc_dang_mo.py` trước.
  - Khối bàn giao §6 dùng «Khâu» và «Gói ký đã chuẩn bị».
  - `dieu-phoi-nghien-cuu.md`: mục 🔒 «Nguyên tắc tổng nghiên cứu»; RESUME tại khâu cần hoàn thiện; mẫu đầu ra theo sản
    phẩm.
  - Cặp `THAY_THE` mới trong `tools/enforce_agent_guardrails.py` cấy mục 5 (nguyên tắc tổng + sửa đúng khâu rồi khoá),
    mục 6 (giao sản phẩm) và mục 7 (không sổ nợ) vào khối guardrail cuối của CẢ 64 agent, để luật được nhắc lại ở mọi
    agent.
  - CLAUDE.md: §0 mục 10 (giao sản phẩm) và 11 (không sổ nợ); §1 «NGUYÊN TẮC TỔNG NGHIÊN CỨU» (câu nguyên văn rồi
    triển khai a–c). Câu mô tả sổ nợ toàn văn cũ đổi thành «chỉ được xoá về 0».
- **Còn phải xây tiếp (theo luật vừa ghi):**
  - Trục 8 nguyên tắc của ma trận đề cương chưa có phép đo ⇒ ⚪.
  - Mã các cổng còn đọc sổ nợ (`so_mien_tru.py --so-no`, `no-toan-van-apply.json`, `no-nguon-chinh-thuc-apply.json`)
    và mức ⚠ không làm đỏ của K17 phải chuyển sang «sửa tại nguồn tới 0, chốt đỏ khi thiếu».
- **CLAUDE.md rút gọn để giữ ngân sách 60.000 ký tự (không bỏ luật nào):**
  - Gộp hai câu trùng về chép bản chạy thật của bộ quét (§6.4 Khâu THU NHẬN); nén câu «lượt quét SẬP» và ngoặc giải
    thích ở «Bậc thang dự phòng TÍNH PHÍ».
  - Bỏ các dòng trùng: §10 «Trạng thái tổng» (ba lệnh đã có ở §0.7, §6.4, §9); câu «Lịch sử từng mục» ở §9 (trùng đầu
    tệp); «trả lời bằng TIẾNG VIỆT (§0.1)» ở §5; «không giả dạng trình duyệt» ở «Trang chặn bot»; «Agent KHÔNG ký» ở mục
    rút bài; «không áp cho DynaMed/Scopus/WoS» lặp trong cùng câu.
  - «bật/tắt Actions…», «cài là việc của bác sĩ», «Cài: bác sĩ» gộp vào §0.5 (thêm «launchd»).
  - Nén ⑧ EndNote: thư viện và nhóm cùng ghi nhớ ở `~/.ebm-endnote.json`.
  - Bỏ số đo ảnh chụp: 1887 bản ghi, 80/80 câu, «(gồm Elsevier, ADA; giữ 07/11)», «bác sĩ đã đặt 25/09», 203 tiêu chí,
    ba giá trị đầu ra của `uoc-tinh`.
  - Bỏ các dấu ngày, «bác sĩ giao» chỉ mang tính lịch sử ở tiêu đề gạch đầu dòng (lịch sử ở `audit/`).
  - Mọi chuỗi chốt BH kiểm trong CLAUDE.md giữ nguyên, vd hook cloud ≥2 repo (đã `grep` từng chuỗi trước khi bỏ).

## Đo thật (22/11/2026, bản chép chỉ đọc `~/.ebm-worktrees/kiem-13-khau-20261122`, `--goc`)

- `hai-long-benh-nhan-C1a-BVQY175`:
  - G0, G1 đã khoá.
  - **Khâu đang mở G2** (READY_FOR_IRB_SUBMISSION, bảng trách nhiệm AGENT_XONG_CHO_NGUOI) ⇒ **gói ký: 1. G2 — IRB**.
  - G3, G4 khoá ngoài thứ tự.
  - **Khâu cần hoàn thiện G5** (DRAFT_READY_NEEDS_REAL_DATA — phụ thuộc G2 chưa khoá).
  - G6, G10 chưa được làm tiếp. Mã 1.
- `btm-dtd2-ngoai-tru-BVQY175`:
  - G0, G1 đã khoá.
  - **Khâu đang mở = khâu cần hoàn thiện G2** (DRAFT_NEEDS_HUMAN_COMPLETION — mục G2-AUTO-05 còn thiếu dữ kiện thật).
  - Gói ký trống.
  - G3 khoá ngoài thứ tự; G4 (READY_FOR_SIGNATURE) và G6 chưa được làm tiếp. Mã 1.
- Không tệp nào của bản chép bị ghi (băm `git status --porcelain` trước = sau).

## Kiểm hồi quy

- `tests/test_buoc_dang_mo_20261122.py` (21 ca). Một ca dùng chuỗi G0→G1 chốt THẬT qua CLI, kèm ảnh chụp thư mục chứng
  minh không ghi tệp.
- Đột biến chạy `python -B` và xoá `__pycache__` trước mỗi phép. Phép nào cũng ĐỎ rồi phục hồi XANH:
  - (1a) sắp cổng theo chữ — 4 ca đỏ;
  - (1b) không dừng ở khâu chưa đạt — 5 ca đỏ;
  - (2) coi READY của cổng cứng là khoá — 10 ca đỏ;
  - (3) coi «không đo được» là khoá — 2 ca đỏ.
