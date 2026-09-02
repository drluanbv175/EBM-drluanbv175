# PROMPT KIỂM CHI TIẾT HỆ NGHIÊN CỨU — từng bước · từng cổng · toàn tài liệu (02/09/2026)

**Đề xuất theo yêu cầu bác sĩ 02/09/2026** («đề xuất một Prompt và thực hiện theo Prompt đó về
việc kiểm tra chi tiết hệ thống nghiên cứu… đảm bảo tất cả các bước và các cổng đã được tự động
một cách chi tiết, đã đúng chuẩn của một nghiên cứu y khoa, toàn tài liệu của một nghiên cứu»).
**Tự thi công ngay trong phiên; báo cáo thi hành ở `audit/10-…`.** Cần bác sĩ kiểm chứng.

## 0. VÌ SAO CẦN MỘT PROMPT RIÊNG — bài học đã lặp ít nhất bốn lần

Chuỗi «đã hoàn thiện» → «kiểm lại thì chưa» (xử lý số liệu · diễn giải · thiết kế · trình bày)
có một nguyên nhân cấu trúc, không phải do lười: muốn trả lời «hệ đã tự động và đúng chuẩn ở
TỪNG cổng chưa» phải chạy tay **ít nhất 7 công cụ rời rạc** (`audit_research_gates` ·
`study_readiness` · `run_pipeline --check-only` · 11 `gN_quality_gate` · canary ·
`verify_exports_integrity` · `xuat_docx_chuan`) rồi **tự ghép trong đầu** — và mỗi lần ghép là
một lần bỏ sót một trục (họ BH41: công cụ không ai gọi thì với dây chuyền hằng ngày nó không tồn
tại). Prompt này biến việc ghép đó thành **một lệnh, một bảng điểm, một mã thoát**.

## 1. VAI TRÒ & BẤT BIẾN

Bạn là Kiểm toán viên hệ nghiên cứu y khoa. Bạn **CHỈ ĐO và BÁO**. Tuyệt đối không:
ký cổng · chạy `approve_gate.py`/`setup_gate_approval_key.py` · ghi `decision`/`gradeLevel`
(BH10) · sinh lại artifact đã biên tập (rào G2/G4) · bịa nguồn/PMID/phê duyệt · qua mạng ·
dùng PASS kỹ thuật thay IRB/PI/thống kê viên/phản biện. Mọi kết luận kèm «Cần bác sĩ kiểm chứng».

## 2. ĐỐI TƯỢNG ĐO: NĂM TRỤC cho MỖI cổng G0→G10, cộng một nhóm HỆ THỐNG

| Trục | Câu hỏi | Nguồn sự thật (không tự đo lại) |
|---|---|---|
| ① **TỰ ĐỘNG** | Script cổng có, biên dịch được? Quality gate có CLI? Cổng cứng có được nối vào `approve_gate` TRƯỚC khi ghi sổ cái? Checkpoint có? Có cũ/mồ côi so với thượng nguồn? | `run_gN_auto.py` · `gN_quality_gate.py` · mã nguồn `approve_gate.py` · `pipeline_freshness` |
| ② **CHUẨN** | Hợp đồng chất lượng của cổng chấm SỐNG ra trạng thái gì? Tiêu chí tự động nào FAIL? Chuẩn báo cáo theo thiết kế (CONSORT/STROBE/STARD/TRIPOD…) có được đề cương gọi tên? | `gN_quality_gate.evaluate_study(write=False)` · `skill_standards.reporting_standards_for` · SAP↔G6 (`gate_contract.sap_declares_ordinal`) |
| ③ **TÀI LIỆU** | Artifact BẮT BUỘC của cổng có mặt? Mỗi file `.md` qua 5 luật liêm chính (placeholder bảng · PMID/DOI · disclaimer · PII · cân bằng markdown)? Còn bao nhiêu nhãn `[CẦN`? | `audit_research_gates.GATE_ARTIFACT_REQUIREMENTS` · `verify_exports_integrity.check_file` |
| ④ **TRÌNH BÀY** | Mỗi artifact có bản `.docx`? Font Times New Roman toàn văn? Cỡ thân bài 13 / bảng 11? 0 ký tự trang trí (khung ═║, emoji, ô tick)? Bản in có cũ hơn nội dung? | `chuan_trinh_bay` · `xuat_docx_chuan.do_ky_tu_la` · python-docx |
| ⑤ **ĐIỂM DỪNG NGƯỜI** | Cổng cứng (G2·G4·G5·G8·G9·G10): chưa ai ký / đã ký đúng vai / **THU HỒI** / **sổ cái có dấu hiệu bị sửa** / nội dung đổi sau khi ký? | `gate_contract.ledger_approved` + `gate_block_reason` |
| **HỆ THỐNG** | 11/11 script + 11/11 quality gate + dây nối 6 cổng cứng · canary gài lỗi 9/9 + canary dây nối 3/3 · luật trình bày ở TẦNG MÃ (không bộ sinh nào gán font qua `p.style`) · ARTIFACT_MAP ≥ 32 | `thu_dau_cuoi_cong_nghien_cuu` · grep mã nguồn |

## 3. LUẬT MÀU — «không biết» KHÔNG phải «có vấn đề» (BH08)

- 🟢 **Đạt** — đo được và đúng.
- 🟡 **Chờ người thật / chưa tới lượt** — cổng chưa chạy vì thượng nguồn chưa ký; tiêu chí
  REVIEW cần thống kê viên/PI; nhãn `[CẦN` còn lại; bản in nghi cũ hơn nội dung.
  **KHÔNG phải lỗi.** Mỗi 🟡 phải ghi rõ **AI** (vai) và **LỆNH** nào để đóng.
- 🔴 **Lỗi máy-sửa-được hoặc fail-closed bị hở** — script không biên dịch; cổng cứng không nối
  quality gate; guardrail FAIL; tiêu chí tự động FAIL/BLOCK; PII; placeholder bảng vỡ; `.docx`
  sai font/cỡ/còn ký tự lạ; **cổng máy chạy được mà chưa chạy**; sổ cái thu hồi/bị sửa.
- ⚪ **Không đo được ở máy này** — thiếu nguyên liệu (module, python-docx…). Không đổi thành 🔴.

Mã thoát: **0** = không 🔴 và không 🟡 · **1** = có 🟡 · **2** = có 🔴 · **3** = công cụ chết.
Một chỉ số gộp không bao giờ được trình bày như kết luận về toàn bộ (BH32): bảng điểm phải
liệt kê **từng cổng × từng trục**, không chỉ tổng.

## 4. LÔ THI CÔNG (lô sau chỉ chạy khi lô trước không FAIL)

- **LÔ K1 — Công cụ.** `medical-ebm-automation/tools/kiem_chi_tiet_he_nghien_cuu.py --study <mã>
  [--no-write] [--khong-canary]`. Ghép các nguồn sự thật ở §2 — **không viết lại phép đo nào đã
  có** (hai bản đo là nguồn trôi dạt). Ra: bảng điểm terminal + `exports/<mã>/KIEM_CHI_TIET_report.{json,md}`.
  Chạy được Python 3.11 (không PEP 701), Windows (UTF-8 stdout, không `os.getuid`), ngoại tuyến.
- **LÔ K2 — Test.** `tests/test_kiem_chi_tiet_he_nghien_cuu_20260902.py`: đề tài giả trong
  `tmp_path` với lỗi GÀI biết trước (docx sai font · md chứa PII · quality gate BLOCKED · cổng
  cứng chưa ký) ⇒ đúng trục đỏ/vàng, đúng mã thoát; đề tài không tồn tại ⇒ mã 3 không im lặng.
  Kiểm bằng **≥3 phép đột biến** (tắt từng trục ⇒ test đỏ đúng chỗ).
- **LÔ K3 — Chạy trên đề tài thật C1a.** Vá **mọi 🔴 máy-sửa-được** (không đụng nội dung khoa
  học, không ký, không nâng decision). Chạy lại tới khi 0 🔴. Liệt kê 🟡 kèm vai + lệnh.
- **LÔ K4 — Nối dây.** Thêm lệnh vào `CLAUDE.md ## Lệnh` (repo gốc) và docstring
  `dieu-phoi-nghien-cuu` biết gọi trước khi báo «hoàn thiện» (BH39/BH41: cổng mới phải dạy agent).
- **LÔ K5 — Báo cáo.** `audit/10-bao-cao-kiem-chi-tiet-he-nghien-cuu_2026-09-02.md`: bảng
  điểm 11 cổng × 5 trục, số 🔴 trước/sau, danh sách 🟡 theo vai, giới hạn cố ý của phép đo.

## 5. TIÊU CHÍ XONG

1. Một lệnh trả lời được «cổng nào, trục nào, màu gì, vì sao, ai/lệnh nào đóng» cho một đề tài.
2. Trên C1a: **0 🔴**; mọi 🟡 đều là việc của người thật (IRB · thống kê viên · PI · chủ nhiệm).
3. Toàn bộ pytest repo y khoa xanh, ruff sạch, CI 2 lane xanh; commit/push cả hai repo.
4. Không dòng nào trong báo cáo dùng chữ «sẵn sàng» cho việc thuộc thẩm quyền Hội đồng/PI.

## 6. GIỚI HẠN CỐ Ý CỦA PHÉP ĐO (ghi trước để không nói quá)

- Công cụ chứng minh **«cổng bắt được lỗi nếu gói đi qua cổng»** và **«tài liệu hiện có đúng
  chuẩn hình thức»**; KHÔNG chứng minh nội dung khoa học đúng (đó là bình duyệt G8) và KHÔNG
  chứng minh agent đã GỌI cổng trong phiên thật.
- Thăm dò fail-closed bằng cách CHẠY `run_g5/run_g10` trên đề tài thật bị loại vì chúng ghi
  checkpoint/`.bak` vào hồ sơ đang track; thay bằng canary dây nối (gọi thật `approve_gate.main`
  trong thư mục tạm) + kiểm tĩnh tham chiếu `ledger_approved`/`gate_block_reason` trong mã.
- Chuẩn báo cáo chỉ kiểm **được gọi tên** trong đề cương, không kiểm từng mục checklist
  (việc đó thuộc `check_de_cuong.py` và G7/G8 quality gate).

Cần bác sĩ kiểm chứng.
