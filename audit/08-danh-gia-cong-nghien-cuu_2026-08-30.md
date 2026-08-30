# Đánh giá chi tiết CÁC CỔNG của hệ thống nghiên cứu (G0→G10) — 30/08/2026

> Theo yêu cầu bác sĩ. **Phạm vi đo trung thực:** phiên này là bản sao git trần —
> phần ĐO ĐƯỢC ở đây là doctrine 50 agent + 4 verifier hợp đồng cổng + bộ chốt bài học
> + hồ sơ audit trong repo; phần THI HÀNH SỐNG (run_gN_auto · gN_quality_gate ·
> approve_gate · gate_contract · ledger) nằm ở `medical-ebm-automation/` trên OneDrive
> — 4 verifier cổng chạy ở đây đều tự khai ⚪ đúng thiết kế. Các phán quyết ghi
> «đã kiểm ngày X» dưới đây lấy từ hồ sơ audit đã tài liệu hoá trong repo (nặng nhất
> là audit đa-agent 24/08/2026), không phải đo lại hôm nay. Cần bác sĩ kiểm chứng.

## 0. Kiến trúc — mỗi cổng có tối đa BA lớp, đừng nhầm lớp này với lớp kia

| Lớp | Làm gì | Phủ |
|---|---|---|
| ① `run_gN_auto.py` | sinh artifact + guardrail nội bộ | G0→G10 |
| ② `gN_quality_gate.py` | hợp đồng CHẤT LƯỢNG (tiêu chí tự động + tiêu chí người thật, neo chuẩn quốc tế) | **11/11 cổng** (xác nhận 24/08 — trước đó tài liệu chỉ ghi 5 cổng có) |
| ③ `approve_gate.py` + `gate_contract.py` | KÝ mật mã + sổ cái niêm phong — cổng chỉ ĐÓNG THẬT ở lớp này | **6 cổng cứng: G2·G4·G5·G8·G9·G10** |

Doctrine đã khoá hai phân biệt sống còn (đo hôm nay trong `dieu-phoi-nghien-cuu.md`,
111 tham chiếu cổng): **(a)** `LOCKED` trong checkpoint JSON KHÔNG đóng cổng — chỉ bản
ghi ký tay trong `approval_ledger.json` mới đóng; **(b)** «chặng cơ học xong» ≠ «cổng
cứng đã đóng» (giấy tờ G3 soạn xong không có nghĩa G2 đã qua). Vai ký fail-closed:
G2→IRB · G4→thống kê viên/PI · G5→quản lý dữ liệu/PI · G8→phản biện độc lập · G9→PI · G10→PI.

## 1. Đánh giá từng cổng

### G0 — Câu hỏi nghiên cứu 🟡 vững, hai giới hạn ghi rõ
- 3 trạng thái rời nghĩa (BLOCKED → DRAFT_READY_NEEDS_HUMAN_REVIEW → PASS_G0_CONFIRMED);
  nơi chốt là `study_meta.json → gate_params.G0`, không phải file .md (file bị ghi đè).
  Tự tra ClinicalTrials.gov («đã có ai ĐANG làm chưa»); kiểm rút bài ngay tại cửa (BH52).
- Giới hạn ①: 3/9 luật guardrail là tautology (template in cứng) — đã ghi chú trung
  thực tại chỗ, phạm vi thật chỉ bắt tampering sau sinh. Giới hạn ② (đánh đổi có chủ ý
  31/07): R5 chặn chỉ-thị-lâm-sàng-đội-lốt-câu-hỏi có thể LÁCH bằng diễn đạt mệnh lệnh
  cụ thể — chấp nhận vì G0 chưa qua Cổng A và không có phân tích ngữ nghĩa tiếng Việt.

### G1 — Đề cương & thiết kế 🟢
Lớp ② đã có (24/08). Được đỡ bởi `khoang-trong-nghien-cuu` (tính mới) +
`ke-hoach-trien-khai` (A13 — nhân lực/tiến độ/kinh phí, số tiền không bịa).

### G2 — Đạo đức & đăng ký 🔒 CỨNG · 🟢 sau vá 24/08
- Fail-closed NỘI DUNG: WHO TRDS v1.3.1 — thiếu mục 13/14/19/20 lấy từ dữ kiện PI đã
  pin, hoặc tham chiếu Hội đồng chỉ là fallback ⇒ DRAFT, không mở cổng.
  `verify_controlled_research_automation.py` kiểm đúng HÀNH VI này (không phải nhãn).
- **Phát hiện 24/08 (đã vá):** 24 tiêu chí WHO TRDS trước đó chỉ chạy SAU khi ledger
  đã ghi (thuần advisory) — nay `G2Q.evaluate_study` chặn TRƯỚC bước ghi ledger,
  từ chối khi BLOCKED/DRAFT; kiểm bằng đột biến thật.

### G3 — Cỡ mẫu/power 🟡 vững, MỘT ranh giới phải nhớ
- 18 tiêu chí tự động + 7 người thật, neo DELTA2 · ICH E9(R1) · CONSORT 2025 (16a/16b)
  · SPIRIT 2025 · Riley/pmsampsize · biên NI theo FDA/EMA · cluster. Đã sửa lớp lỗi
  «ngầm giả định so sánh hai nhóm» khi đề tài thật đầu tiên đi qua (31/07): có
  `--prevalence/--precision` cho mô tả cắt ngang.
- **Ranh giới:** G3 KHÔNG phải cổng ký — `PASS_G3_CONFIRMED` là lời tự khai có dấu vết,
  và quality-BLOCKED cố ý KHÔNG đổi mã thoát pipeline (đổi là đổi quy trình — cần bác sĩ
  quyết). Đây là chỗ «trông như cổng cứng mà không phải».

### G4 — Khoá SAP 🔒 CỨNG · 🟢 sau hai đợt vá
- Chốt giá trị nhất: **G4-AUTO-03 đối chiếu số liệu trong SAP-đã-ký với
  `G3_checkpoint.json` HIỆN TẠI** — SAP sửa tay hay sinh trước khi G3 chạy lại đều bị
  bắt (chữ ký chỉ bảo vệ toàn vẹn, không bảo đảm còn đúng). G4-AUTO-09 chặn CỨNG
  NI/equivalence thiếu biên Δ. N ghi vào SAP là N KẾ HOẠCH (`confirmed_n`) cho MỌI
  thiết kế — vá lỗi nghiêm trọng nhất 31/07 (SAP từng ghi N tối thiểu 453 thay vì 1000
  Hội đồng đã chốt).
- **24/08 (đã vá):** như G2, 12 tiêu chí trước đó chỉ chạy sau ký — nay chặn trước ký,
  chỉ nhận `READY_FOR_SIGNATURE`.

### G5 — Khoá dữ liệu 🔒 CỨNG · 🟢
Nối lớp ② vào trước-ký từ TRƯỚC đợt 24/08 (cùng nhóm G5/G9/G10 làm khuôn cho bản vá
G2/G4/G8). ALCOA+ · CRF/data dictionary · khử định danh · gói tái lặp.

### G6 / G6.5 — Phân tích & diễn giải 🟢
Lớp ② có (24/08); chạy đúng SAP đã khoá trên DB đã khoá; `dien-giai-ket-qua` tách
ý nghĩa thống kê khỏi ý nghĩa lâm sàng.

### G7 — Bản thảo (+ cổng A12) 🟢
A12 kiểm chứng trích dẫn là cổng THẬT: `run_g10_assemble` xác minh artifact
`A12_CITATION_VERIFICATION` trước khi lắp gói; rút bài tra CHỦ ĐỘNG qua chuỗi 3 tầng
bất đối xứng (Retraction Watch ngoại tuyến → NCBI → Europe PMC; DOI qua Crossref
`updated-by` — BH33). **BH27 (14/08, đã vá + khoá):** `unknown_fetch_error` từng làm
`all_clean=true` được ký khi NCBI chặn — fail-open kinh điển, nay fail-closed.

### G8 — Bình duyệt độc lập 🔒 CỨNG · 🟡 vững, MỘT giới hạn bản chất
- **Phát hiện nặng nhất của audit 24/08 (đã vá, mutation-tested):** `approve_gate.py`
  trước đó KHÔNG import `g8_quality_gate` — ai giữ khoá vai `PHAN_BIEN` ký được «đã
  bình duyệt độc lập» mà không cần bản nhận xét phản biện tồn tại, không cần A12 từng
  chạy, kể cả tự duyệt đề tài mình đứng tên thống kê viên. Nay lớp ② chặn trước ký.
- Đòi artifact THẬT `G8_PEER_REVIEW_REPORT` (máy không sinh); ICMJE 1/2026 V.A + V.B
  (người phản biện khai AI); đối chiếu `reviewer_ref` với G2/G4/G5/G9 chống một-người-
  nhiều-vai.
- **Giới hạn bản chất (cố ý ghi vào tên nhãn):** `PASS_G8_REVIEW_RECORDED` KHÔNG mang
  chữ «ĐỘC LẬP» — HMAC đối xứng không chứng minh được người ký độc lập với PI. Đường
  đóng đã sẵn trong lõi: Ed25519 «ed1» (khoá công trong repo, verify không cần bí mật)
  — CHỜ bác sĩ tự tay phát khoá riêng từng vai (nút «Phat Khoa Ed25519»).

### G9 — Liêm chính tác giả 🔒 CỨNG · 🟢, một hở nhỏ còn mở
ICMJE 4 tiêu chí + CRediT + COI + khai AI đủ tools/purposes + Data Availability đủ
chi tiết + quyền truy cập dữ liệu/độc lập nhà tài trợ theo ICMJE 1/2026 + xác nhận
thể chế; G9-HUMAN-10 soi ngược `reviewer_ref`. **Hở còn mở (đã ghi 30/07):** checklist
giấy «Phần 8 — Hard Gate» bác sĩ ký tay vẫn tách rời cổng máy-chấm (đã có dòng trỏ
đúng lệnh, chưa có cơ chế đọc ngược ô tick).

### G10 — PI khoá gói phát hành 🔒 CỨNG · 🟢
Fail-closed theo A12 (`all_clean is not True` ⇒ chặn); bị ép qua bằng `--i-know-*`
trả mã thoát **3** (vá 26/07 — trước trả 0 khiến caller tưởng gói đủ điều kiện nộp).

## 2. Lớp ký & sổ cái (nền của 6 cổng cứng) 🟢 sau ba đợt gia cố

- **26/07 — vá 3 lỗ mật mã:** payload ký v2 buộc `reviewer_role` (chữ ký hết dùng lại
  chéo vai); `EBM_GATE_KEY_PATH` chỉ còn tác dụng dưới pytest; `ledger_approved()` hết
  fail-open khi máy chưa cấu hình khoá (ngoại lệ duy nhất: `study_kind=synthetic_test`
  tự tay đánh dấu — BH51 canh phạm vi).
- **27/07 — niêm phong:** `prev_hash` chuỗi băm + con dấu `approval_ledger.seal.json`
  — xoá/đảo/chèn/cắt-đuôi bản ghi (kể cả gỡ quyết định THU HỒI) đều bị bắt; sửa tay
  ledger ⇒ mọi cổng của đề tài đó BỊ CHẶN; đường phục hồi chuẩn: ký lại trên máy hiện tại.
- **`approve_gate` nói rõ mức bảo đảm** («shared» vs «role») thay vì im lặng.

## 3. Lưới canh cổng (đo được hôm nay)

- Bộ chốt bài học có **≥13 mục canh trực tiếp họ lỗi cổng** (BH01 return-sớm · BH27
  fail-open A12 · BH31 nguồn rút chặn ở cổng · BH39 doctrine không trôi sau cổng ·
  BH51 ledger synthetic đúng phạm vi · BH52 G0 kiểm rút tại cửa · BH62 cổng tự parse
  chặt · BH66 cổng trích dẫn ≠ bảo đảm lâm sàng · BH72 canary chuỗi cổng nghiên cứu…),
  chạy mỗi phiên, mutation-tested.
- 4 verifier hợp đồng cổng trong repo này (`verify_controlled_research_automation` ·
  `verify_research_gate_contracts` · `verify_hard_gate_count_consistency` ·
  `verify_research_practical_readiness`) — trên bản trần đều ⚪ CÓ KHAI BÁO (thoát ≠0,
  không ai đọc nhầm thành «đã kiểm»); trên máy thật chúng là phán quyết sống.
- Doctrine: 50 agent; `dieu-phoi-nghien-cuu` nhắc trục cổng 111 lần, có bảng quy đổi
  `_CROSSWALK-NGHIEN-CUU.md` chống lẫn trục số của skill (skill đánh Đạo đức=G3 —
  agent giữ trục riêng, bàn giao gọi cổng bằng TÊN).

## 4. BẢNG KHOẢNG HỞ CÒN MỞ — trung thực, xếp theo mức đáng bận tâm

| # | Khoảng hở | Mức | Việc đóng |
|---|---|---|---|
| 1 | Canary chuỗi nghiên cứu (BH72) gọi thẳng hàm Python, chưa đi qua đúng CLI `approve_gate.py` | 🟢 **ĐÃ ĐÓNG TỪ TRƯỚC — đính chính 30/08** | Đối chiếu repo y khoa sống: task 9.5 đã `cc:done` trong Plans.md, canary wiring gọi thật `approve_gate.main()` nằm ở `tools/thu_dau_cuoi_cong_nghien_cuu.py` (từ dòng ~691), kiểm đột biến 3 lượt riêng từng cổng G8/G4/G2. Dòng «chưa làm» trong bản đầu của báo cáo này chép từ ghi chú CLAUDE.md repo gốc đã lỗi thời — bài học: khoảng hở về repo nào phải đối chiếu MÃ SỐNG repo đó |
| 2 | G8 chưa chứng minh ĐỘC LẬP thật (HMAC đối xứng) | 🟠 bản chất | Bác sĩ phát khoá Ed25519 riêng cho vai PHAN_BIEN (nút sẵn, tự tay) — máy không tự làm được, đây là chính điểm bảo đảm |
| 3 | G3 không phải cổng ký + BLOCKED không chặn mã thoát pipeline | 🟡 cố ý | Đổi = đổi QUY TRÌNH (hợp đồng 3 mã thoát + 19 file test) — chờ bác sĩ trả lời câu hỏi riêng, không tự đổi |
| 4 | G0-R5 lách được bằng diễn đạt mệnh lệnh cụ thể | 🟢 **ĐÃ ĐÓNG 30/08** | Luật hẹp trong `run_g0_auto.py` (repo y khoa, commit 5e288d8): vỏ câu hỏi KHÔNG miễn trừ khi hội đủ CẢ HAI dấu hiệu «động từ y lệnh + ngay» VÀ «liều cụ thể»; PICO hợp lệ chỉ mang một dấu hiệu vẫn qua (test vế âm, kiểm đột biến 2 phép) |
| 5 | G9 checklist giấy tách rời cổng máy | 🟢 **ĐÃ ĐÓNG 30/08** | Tiêu chí mới `G9-AUTO-08` trong `g9_quality_gate.py` (commit 2c3d2d3+3b42403): đọc ngược tick ☑/☒/[x] của tờ «Phần 8 — Hard Gate», soi hai chiều lệch tờ-giấy ↔ hồ-sơ-điện-tử; ADVISORY-ONLY (không lật đề tài đã khoá, không phạt người tích sớm); kiểm đột biến 3 phép |
| 6 | Phán quyết SỐNG toàn chuỗi không đo được từ cloud | ⚪ kiến trúc | Trên máy thật: `python3 tools/verify_controlled_research_automation.py` + `python3 tools/upgrade_verify.py` + canary `thu_dau_cuoi_cong_nghien_cuu.py` |

## 5. Kết luận

Chuỗi cổng G0→G10 **vững ở cả ba lớp** sau ba đợt gia cố lớn (26–27/07 mật mã ·
31/07 đề tài thật đầu tiên · 24/08 nối lớp chất lượng vào TRƯỚC ký cho G2/G4/G8):
mọi cổng cứng nay đều fail-closed đúng VAI + đúng NỘI DUNG trước khi ledger nhận
chữ ký, sổ cái chống sửa/cắt, và bộ chốt bài học canh không cho các lỗi cũ quay lại.

**Cập nhật 30/08 (đợt «hoàn thiện cho xanh»):** #1 hoá ra đã đóng từ 24/08 (đính
chính), #4 và #5 đóng hôm nay bằng code + test đột biến trong repo y khoa (suite
3123 passed / 0 fail). Ba mục còn lại đều KHÔNG phải việc máy tự đóng được: #2 là
hành động phát khoá của bác sĩ, #3 là quyết định đổi quy trình chờ bác sĩ trả lời,
#6 là giới hạn kiến trúc phiên cloud — chạy lệnh xác minh trên máy thật.

*Soạn 30/08/2026. Cần bác sĩ kiểm chứng.*
