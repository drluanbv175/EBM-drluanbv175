# Báo cáo thi hành Prompt KIỂM CHI TIẾT hệ nghiên cứu — 02/09/2026

> Thi hành `audit/09-prompt-kiem-chi-tiet-he-nghien-cuu_2026-09-02.md` ngay trong phiên, trên
> đề tài THẬT `hai-long-benh-nhan-C1a-BVQY175` (repo `medical-ebm-automation`, nhánh
> `claude/medical-research-system-phggdf`). Mọi con số dưới đây là số ĐO của lần chạy, không
> phải mô tả. Cần bác sĩ kiểm chứng.

## 1. Đã dựng gì

| Lô | Sản phẩm | Trạng thái |
|---|---|---|
| K1 | `tools/kiem_chi_tiet_he_nghien_cuu.py` — một lệnh ghép 9 nguồn sự thật sẵn có (audit_research_gates · pipeline_freshness · 11 `gN_quality_gate` chấm SỐNG `write=False` · dây nối `approve_gate` · sổ cái `gate_contract` · `verify_exports_integrity` · `chuan_trinh_bay`/python-docx · `skill_standards` · canary) thành bảng điểm **11 cổng × 5 trục** + nhóm hệ thống; ra `exports/<mã>/KIEM_CHI_TIET_report.{json,md}`; mã thoát 0/1/2/3 | ✅ chạy Python 3.11/3.12, ruff sạch, ngoại tuyến, ~1,6 s kể cả canary |
| K2 | `tests/test_kiem_chi_tiet_he_nghien_cuu_20260902.py` (7 test) | ✅ **4 phép đột biến đều đỏ đúng chỗ**: bỏ đếm ký tự trang trí · cổng đầu chuỗi không đỏ · bỏ nhánh «checkpoint tự mâu thuẫn» · không tách tiêu chí người/máy |
| K3 | Chạy trên C1a, vá mọi 🔴 máy-sửa-được | ✅ **3 🔴 → 0 🔴** (xem §2) |
| K4 | Nối dây: `CLAUDE.md ## Lệnh` (repo gốc) + doctrine `dieu-phoi-nghien-cuu.md` («chạy TRƯỚC khi nói đã hoàn thiện») | ✅ enforce → sync Codex → `--check` sạch |
| K5 | Báo cáo này | ✅ |

## 2. Kết quả trên C1a — lần chạy 1 (trước vá) → lần chạy 2 (sau vá)

| | 🟢 | 🟡 việc người thật | 🔴 máy sửa được / hở | ⚪ | Mã thoát |
|---|---|---|---|---|---|
| Lần 1 | 33 | 38 | **3** | 1 (canary tắt) | 2 |
| Lần 2 | 38 | 39 | **0** | 0 | **1** |

**Bảng điểm lần 2** (màu xấu nhất của ô; `·` = trục không áp dụng cho cổng):

| Cổng | ① Tự động | ② Chuẩn | ③ Tài liệu | ④ Trình bày | ⑤ Điểm dừng người |
|---|---|---|---|---|---|
| G0 | 🟢 | 🟢 | 🟡 | 🟢 | · |
| G1 | 🟡 | 🟡 | 🟡 | 🟢 | · |
| G2 | 🟡 | 🟡 | 🟡 | 🟢 | 🟡 |
| G3 | 🟡 | 🟡 | 🟡 | 🟢 | · |
| G4 | 🟡 | 🟡 | 🟡 | 🟢 | 🟡 |
| G5 | 🟡 | 🟡 | 🟡 | · | 🟡 |
| G6 | 🟡 | 🟡 | 🟡 | · | · |
| G7 | 🟡 | 🟡 | 🟡 | · | · |
| G8 | 🟡 | 🟡 | 🟡 | · | 🟡 |
| G9 | 🟡 | 🟡 | 🟡 | · | 🟡 |
| G10 | 🟡 | 🟡 | 🟡 | 🟢 | 🟡 |

Nhóm HỆ THỐNG: 7/7 🟢 — 13/13 script biên dịch · 11/11 quality gate có CLI · `approve_gate`
nối đủ 6 cổng cứng · 11/11 bộ sinh `.docx` qua `chuan_trinh_bay`, 0 vi phạm `p.style` ·
G5/G6/G10 tự tra sổ cái thượng nguồn · `ARTIFACT_MAP` 38 khoá · canary **9/9 lỗi gài bị bắt +
3/3 dây nối** (`approve_gate.main` thật từ chối G2/G4/G8).

### Hai lỗi THẬT bắt được ngay lần chạy đầu

1. **Checkpoint G0 tự mâu thuẫn (🔴 ①).** `G0_checkpoint.json` giữ `needs_input.blocked=true`
   (MISSING_PICO) từ lượt chạy đầu, trong khi hợp đồng chất lượng đã `PASS_G0_CONFIRMED` (bác
   sĩ đã chốt PICO trong `study_meta.json`). Hệ quả đo được: `audit_research_gates` — đài kiểm
   soát — vẫn in `current_actionable_gate=G0 … chốt PICO`, còn `study_readiness` in «✅ ĐÃ
   CHỐT». **Hai lớp kể hai chuyện về cùng một cổng**, cùng họ với «2 lớp xử lý tách rời nhau»
   đã vá ở G6/G7. Nguyên nhân: `g0_quality_gate.refresh_checkpoint()` chỉ ghi khối
   `quality_gate`, không gỡ cờ chặn cũ. **Đã vá**: khi trạng thái CONFIRMED và cờ cũ là
   MISSING_PICO → đặt `blocked=false`, giữ nguyên bản ghi + `resolved_by/resolved_at` (truy
   vết); cờ MISSING_PUBMED **không** bị gỡ (0 PMID không thể được «xác nhận» qua). Test
   `tests/test_g0_needs_input_cleared_20260902.py` (3 test, đột biến gỡ nhánh ⇒ đỏ). Sau vá:
   `audit_research_gates` chuyển đúng sang `current_actionable_gate=G1`.
2. **Hai bản `.docx` đề cương chưa qua chuẩn trình bày (🔴 ④).** `DE_CUONG_THONG_NHAT` còn 1
   ký tự `🚧`; `De-cuong_…` còn `☐` và thân bài **12pt** — cả hai render trước đợt chuẩn hoá
   01/09. Render lại từ chính `.md` bằng `xuat_docx_chuan.py --file` → Times New Roman 13/bảng
   11, 0 ký tự trang trí. Nội dung `.md` không chạm.

### 39 🟡 — toàn bộ là việc của NGƯỜI THẬT, xếp theo vai

| Vai | Việc | Lệnh/nơi |
|---|---|---|
| Chủ nhiệm | điền nốt nhãn `[CẦN…]`: G0 24 · G1 178 · G2 49 · G3 5 · G4 3 · hồ sơ tổng hợp 74 | file `.md` tương ứng → chạy lại `gN_quality_gate.py --study` |
| Chủ nhiệm | G1: `design_confirmed`, ngày bắt đầu, 3 cờ rà soát, evidence review (G1-HUMAN-01/03/06/07/08) | `study_meta.json → gate_params.G1` rồi `run_g1_auto.py` |
| Thống kê viên | G3: 6 xác nhận tham số cỡ mẫu (G3-HUMAN-01…06) | `gate_params.G3` |
| Thống kê viên / PI | G4: G4-AUTO-10 (`chuyenkhoa` khả thi vận hành) + 7 xác nhận | `gate_params.G4` |
| IRB | ký G2 | `tools/trinh_ky_cong.py` (nút Trình Ký) hoặc `approve_gate.py --gate G2` |
| Thống kê viên / PI | ký G4 | `approve_gate.py --gate G4` |
| — | G5→G9 chưa tới lượt (chờ ký G4 → G5); G10 đang BLOCKED = **từ chối fail-closed đúng** | tự chạy khi thượng nguồn ký |
| (tự động, chỉ nhắc) | độ tươi theo **mtime**: G1/G2/G3 «cũ hơn G0», G4 «cũ hơn G3» — do chấm lại G0 và G1 ngày 01–02/09 làm mtime đổi; trục ② chấm SỐNG vẫn PASS mọi tiêu chí tự động (G4-AUTO-03 SAP↔G3 khớp) | không cần chạy lại; `run_pipeline.py --from` khi muốn đồng bộ mtime |

## 2-bis. VÒNG RÀ THỨ HAI — công cụ tự bắt được điểm mù của CHÍNH NÓ

Ngay sau khi đóng 3 mục đỏ, rà lại công cụ trên cùng đề tài lộ ra một khoảng hở
thuộc **đúng họ lỗi mà nó sinh ra để bắt**: trục ④ chỉ soi bản `.docx` **có `.md`
đi kèm**. Nhưng `gen_research_docx.py` dựng thẳng từ checkpoint, không qua `.md` —
nên **4 bản trong thư mục đề tài C1a chưa từng bị kiểm một lần nào**:

| Bản .docx (không có .md nguồn) | Đo được trước khi vá |
|---|---|
| `G6a_ANALYSIS` | thân bài **11pt** (chuẩn 13) · 1 ký tự trang trí `⚠` |
| `G6b_INTERPRETATION` | thân bài **11pt** · 1 ký tự trang trí |
| `G6d_CLINICAL-GUIDELINE` | thân bài **11pt** · 1 ký tự trang trí |
| `G9_READINESS` | đạt chuẩn (13/11, 0 ký tự lạ) |

**Cách vá (bền, không phải vá một ca):** `docx_theo_cong()` gom **MỌI** `.docx` trong
thư mục đề tài theo tiền tố tên file (`G6a…` → G6; tài liệu gói nộp không mang tiền
tố cổng → G10); `danh_gia_docx()` nhận `md=None` cho bản mồ côi — vẫn kiểm đủ chuẩn
trình bày, chỉ khác ở **cách sửa được chỉ ra**: bản mồ côi phải chạy lại bộ sinh của
cổng, không dùng được `xuat_docx_chuan --file` (công cụ đó cần `.md`). Bổ sung luôn
chiều ngược: có `.md` mà chưa render `.docx` ⇒ 🔴.

**Trung thực về nguồn gốc 3 file:** chúng là **dư của chính các lần chạy thử generator
của tôi** ngày 01/09 (nội dung chỉ có ô `[CẦN CHỦ NHIỆM XÁC NHẬN]`, cổng G6 chưa hề
chạy trên C1a), và vì `exports/` nằm ngoài git nên chúng **chỉ tồn tại trong container
phiên này**, không có trên máy bác sĩ. Đã sinh lại cả ba bằng bộ sinh hiện hành →
13pt, 0 ký tự trang trí. **Giá trị bền của vòng này là BẢN VÁ CÔNG CỤ**, thứ sẽ bắt
đúng lớp lỗi đó trên máy thật khi G6/G9 chạy thật.

Đo sau vòng 2: **🟢 38 → 42 · 🟡 39 · 🔴 0**. Test thêm 4 mục
(gom theo tiền tố · mồ côi sai chuẩn bị bắt · mồ côi đạt chuẩn thì xanh · báo cáo chỉ
đúng cách sửa), **3 phép đột biến đều đỏ đúng chỗ**: quay về chỉ soi bản có `.md` ⇒ đỏ;
gom mọi `.docx` về G10 ⇒ đỏ 2; miễn kiểm cỡ chữ cho bản mồ côi ⇒ đỏ.

> **Bài học ghi lại:** một bộ kiểm lấy đầu vào từ *danh sách A* rồi kết luận về *tập B*
> luôn có điểm mù bằng đúng phần B ngoài A. Ở đây A = artifact `.md` khai trong hợp
> đồng cổng, B = mọi thứ bác sĩ có thể mở và in.

## 3. Giới hạn cố ý — để không nói quá

- Vòng 2 cho thấy chính công cụ này cũng phải bị rà lại bằng dữ liệu thật, không chỉ bằng test.
- Công cụ chứng minh **«cổng bắt được lỗi nếu gói đi qua cổng»** và **«tài liệu hiện có đúng
  chuẩn hình thức»**. Nó KHÔNG chứng minh nội dung khoa học đúng (đó là G8) và KHÔNG chứng minh
  agent đã gọi cổng trong phiên thật — vì thế mới nối vào doctrine `dieu-phoi-nghien-cuu`.
- Không thăm dò fail-closed bằng cách CHẠY `run_g5/run_g10` trên đề tài thật (chúng ghi
  checkpoint/`.bak` vào hồ sơ đang track); thay bằng canary dây nối + kiểm tĩnh tham chiếu
  `ledger_approved`.
- Độ tươi vẫn đo theo **mtime** đúng như `pipeline_freshness` thiết kế (một nửa cổng ghi
  `run_date` không có giờ); công cụ dán nhãn «theo mtime» và trỏ sang trục ② để đọc nội dung.
- G1 không có hàm chấm độc lập → trục ② của G1 đọc báo cáo ĐÃ LƯU và nói rõ điều đó.
- «0 🔴» ≠ «sẵn sàng». Kết luận sẵn sàng thuộc Hội đồng Đạo đức và chủ nhiệm.

## 4. Kiểm định kèm theo

- Repo y khoa: `pytest` toàn bộ (kết quả ghi ở commit) · `ruff` sạch · bất biến newline vùng ký
  🟢 0 vi phạm / 392 file · CI 2 lane (ubuntu + windows).
- Repo gốc: `enforce_agent_guardrails` 50 agent · `sync_agents_to_codex --check` sạch.

Cần bác sĩ kiểm chứng.
