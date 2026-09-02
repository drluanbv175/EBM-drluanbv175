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

## 2-ter. VÒNG 2b — hai báo động giả nữa, cùng một họ

**(a) Bảng điểm có thẩm quyền cho thứ không có cổng nào.** Chạy công cụ trên hai thư
mục còn lại của `exports/` — `chatgpt_project` (scaffold dự án) và `phase_2b` (báo cáo
smoke test) — nó **không chết**, nhưng in bảng điểm đầy đủ 11 cổng, 38 🟡, kèm một 🔴
«G0 chưa chạy — máy làm được» và khuyên chạy `run_g0_auto` **trên chúng**. Đó đúng là
thứ bác sĩ gặp ở lần gõ nhầm mã đề tài đầu tiên. Nay `la_de_tai_nghien_cuu()` gọi thẳng
`list_studies.scan_study()` — **không viết luật nhận diện thứ hai** — và từ chối với mã
3 kèm hai đường ra rõ ràng, không in bảng điểm. Fixture cũ dùng thư mục rỗng được sửa
cho **hợp lệ** (đề tài đã ghim chủ đề, chưa chạy cổng), assertion gốc giữ nguyên từng chữ.

**(b) Chốt bài học BH52 vừa nói sai nguyên nhân, vừa có dấu ✓ cho mục chưa hề kiểm.**
Sau khi hợp nhất master của bác sĩ, bộ chốt đỏ ở BH52 (G0 kiểm rút bài tại cửa nhận).
Truy nguyên thì chính chốt đó mắc đúng họ lỗi nó sinh ra để chống:

| Vấn đề | Trước | Sau |
|---|---|---|
| Nền Retraction Watch ngoại tuyến chưa tải (63 MB, gitignore) | ghi «R1C chạy nhưng KHÔNG bắt bài đã rút» — **đổ lỗi cho guardrail, đẩy người đọc đi sửa nhầm file**; vế «nền RW ngoại tuyến có» là khẳng định chưa từng được đo | «CHƯA KẾT LUẬN ĐƯỢC R1C hỏng hay không» + đúng lệnh `tai_retraction_watch.py` |
| Thiếu venv | `return True` ⇒ in dấu **✓ trần** (ghi chú không hiện ở dòng ✓) — mục chưa hề kiểm trông y hệt mục đã đạt | fail-closed kèm lệnh khắc phục |
| Bản sao git trần | ✗ (bức tường đỏ giả) | ⚪ có khai báo — đo bằng `git ls-files`: **0 file** thuộc `medical-ebm-automation/` được repo gốc track |

Kiểm ba chiều bằng phép đo thật: bản trần ⇒ ⚪, tổng đỏ 0 · nối tạm repo y khoa, thiếu
nền ⇒ ✗ với thông điệp mới · ép `Path.home()` sang đường dẫn không tồn tại ⇒ ✗ thay vì ✓.

⚠️ **Hệ quả cần bác sĩ làm trên máy thật:** chạy
`python3 medical-ebm-automation/tools/tai_retraction_watch.py`. Cho tới lúc đó **chưa
máy nào trong phiên này kết luận được R1C của G0 còn sống hay không** — và đó là chốt
canh việc G0 tự bắt bài đã rút ngay tại cửa nhận y văn.

## 2-quater. VÒNG 3 — soi 39 mục 🟡 xem có việc nào máy làm được mà bị xếp nhầm sang bác sĩ

Bảng điểm gộp mọi nhãn `[CẦN` vào một dòng «thẩm quyền chủ nhiệm». Phân loại 250 nhãn
đó theo cụm thì lộ một khoảng hở **tự động hoá dở dang**:

Sổ chứng cứ `G1_A2b_EVIDENCE_LEDGER` để **12 dòng `[CẦN TRÍCH XUẤT METADATA]`** — việc
TAY của chủ nhiệm — trong khi **đủ tiêu đề, tạp chí, năm của đúng 12 PMID đó đã nằm
sẵn trong `G0_pubmed_raw.json` cùng thư mục**, do chính G0 tra về trong cùng dây
chuyền (đo: 12/12 phủ). Nặng hơn: trong **cùng một lượt sinh**, PMID nào có effect
size thì tiêu đề được điền, số còn lại thì không — năng lực đã có, chỉ thiếu một đoạn
dây. Đây là kiểu dở dang đắt nhất vì nó đẩy sang người thật đúng việc máy vừa làm ở
dòng trên, và người đọc không có cách nào biết.

Đã nối, với ranh giới không nới: **không gọi mạng** (đọc file đã có nên ngoại tuyến,
tất định, CI an toàn) · **không bịa** (không có bản ghi ⇒ giữ nguyên nhãn) · **chỉ cột
metadata** — trích xuất dữ liệu, thẩm định RoB và xác nhận nội dung vẫn là việc người
thật · dòng khai nguồn ghi **đúng số dòng** đã điền, không điền được thì không khai.

Đo trên C1a: nhãn metadata **12 → 0**; bảng điểm **🟡 39 → 38 · 🔴 0**. Lượt chạy lại
G1 không mất nội dung nào (diff chỉ là dấu thời gian và seed theo ngày). Test 6 mục,
**4 phép đột biến đều đỏ đúng chỗ**. Ghi lại một bài học nhỏ của chính đợt test: bản
đầu dùng khoá checkpoint tự nghĩ (`pmids_verified`) nên **test xanh giả** — phải lấy
đúng hình dạng thật của C1a (`pubmed_results.all_pmids`) mới đo được thứ cần đo.

## 2-quinquies. VÒNG 4 — artifact mồ côi trông như sản phẩm THẬT của cổng chưa chạy

Chạy lại công cụ trên C1a sau vòng 3 (0 🔴), rồi hỏi tiếp: bảng điểm đã chấm ĐỦ mọi
tổ hợp «checkpoint có/không × artifact có/không» chưa? Đo trực tiếp: `G6_checkpoint.json`
và `G9_checkpoint.json` **KHÔNG TỒN TẠI** (đúng thực tế — G5 khoá dữ liệu chưa ký, G6
không thể phân tích trước khi có dữ liệu khoá), nhưng thư mục vẫn có bốn `.docx` mang
tên **G6a_ANALYSIS · G6b_INTERPRETATION · G6d_CLINICAL-GUIDELINE · G9_READINESS** — trông
như sản phẩm THẬT của G6/G9 mà đài kiểm soát trước đây không chạm tới.

Xác minh nội dung trước khi kết luận: ba file G6 là khung mẫu 100%, không một chữ do
người viết (`[CẦN CHỦ NHIỆM XÁC NHẬN] Chủ nhiệm điền nội dung cho phần này.`). File
`G9_READINESS` có cấu trúc hơn — kết luận "NOT READY", bảng ba cổng cứng đều "CHƯA
ĐÓNG" (khớp thực tế).

⛔ **ĐÍNH CHÍNH cùng ngày — bản đầu ở đây viết SAI "bộ sinh ra nó không còn tồn tại
trong repo".** Grep lần đầu tìm nhầm tiêu đề IN HOA trong khi mã nguồn lưu chữ thường
có hoa đầu câu; đọc lại `gen_research_docx.py::_gen_readiness()` xác nhận hàm **VẪN
TỒN TẠI** (khoá `readiness` trong `ARTIFACT_MAP`, sinh đúng tên `G9_READINESS_<mã>.docx`).
**Vấn đề thật:** hàm nhận `content: dict` từ người gọi; không truyền `dod`/`gaps`/
`g2_status`/`g4_status`/`g9_status` thì rơi về mặc định "NOT READY"/"CHƯA ĐÓNG" — đúng
những gì thấy trên đĩa. Không nơi nào trong repo tính các giá trị đó từ checkpoint/
ledger thật rồi truyền vào. Quan trọng hơn: **cổng G9 THẬT không hề đụng tới file này**
— `run_g9_auto.py` → `g9_quality_gate.write_readiness_template()` ghi
`G9_PUBLICATION_READINESS.json` (tên hoàn toàn khác). Kết luận hành động không đổi
(vẫn nên dời — không có checkpoint ràng buộc, không đảm bảo còn đúng khi trạng thái ba
cổng đổi), chỉ lý do bị viết sai lúc đầu. Chi tiết ở commit `9e4aa26` repo y khoa.

Vá ở hai lớp: (1) cổng không có checkpoint mà **có** `.docx` trùng tiền tố ⇒ 🔴 tại
trục ①, chỉ đúng cách sửa — dời sang `exports/<mã>/_tai-lieu-mo-coi/` nếu chỉ là khung
rỗng, dùng tiền tố `_` là quy ước NỘI BỘ đã có sẵn trong `verify_exports_integrity.py`,
không tạo quy ước mới; (2) đã dời 4 file thật của C1a bằng `git mv` (giữ lịch sử), kèm
`_GHI-CHU.md` giải thích và đường phục hồi khi G6/G9 chạy thật.

Đo trước/sau: **🟢 41 → 38 · 🔴 2 → 0** (xanh giảm vì ba mục "0 ký tự trang trí" của
file mồ côi không còn được chấm ở trục ④ — đúng, chúng không còn là artifact chính
thức). Test thêm 4 mục, **2 phép đột biến đều đỏ đúng chỗ**.

## 2-sexies. VÒNG 5 — cảnh báo "bản dự thảo, không phải artifact chính thức" mới phủ 2/6 cổng cứng

Đính chính ở VÒNG 4 (`_gen_readiness()` rơi về mặc định NOT READY khi gọi thiếu
`content` thật) đặt ra câu hỏi rộng hơn: bản vá `task_a5fde306` (2026-07-12) từng thêm
cảnh báo "đây là bản DỰ THẢO scaffold, KHÔNG phải artifact chính thức" vào `_gen_ethics`
(G2) và `_gen_sap` (G4) — hai trong sáu cổng cứng. **5/6 cổng cứng còn lại có cảnh báo
này chưa?** Grep trực tiếp `gen_research_docx.py` cho 6 hàm `_gen_*` tương ứng G2/G4/
G5/G8/G9/G10 (G10 không có generator riêng — cổng lắp gói, không sinh tài liệu độc lập
qua công cụ này):

- G2 (`_gen_ethics`) — **CÓ** cảnh báo.
- G4 (`_gen_sap`) — **CÓ** cảnh báo.
- G5 (`_gen_dmp`) — **KHÔNG.**
- G8 (`review`) — **KHÔNG có hàm riêng**, rơi vào `_gen_generic()` — không cảnh báo, không
  cấu trúc gì đặc thù cho bình duyệt.
- G9 (`_gen_readiness`) — **KHÔNG** — đúng file gây ra đính chính ở VÒNG 4.

Không phải lỗi đối xứng ngẫu nhiên: ledger của G2/G4/G8 hash một artifact `.md` THẬT
(`G2_A3_ETHICS_PACKAGE_<mã>.md` · `G4_A5_SAP_FINAL_<mã>.md` ·
`G8_A9_PRESUBMISSION_<mã>.md`, xác nhận qua `approve_gate.py`), trong khi G5 và G9 hash
CHÍNH checkpoint JSON của cổng đó (`G5_checkpoint.json` · `G9Q.CHECKPOINT_JSON` —
`expected_artifact` trong `approve_gate.py` dòng 496/592, đối lập dòng 554 của G8 trỏ
vào `G8Q.presubmission_artifact_name()`). Nghĩa là nguyên văn cảnh báo G2/G4 dùng
("Artifact chính thức là ... được `approve_gate.py` hash") **sai với G5/G9** — không thể
copy-paste, phải viết lại đúng cơ chế của từng cổng.

**Vá theo 2 khuôn câu chữ ("Variant"), không lẫn lộn:**
- **Variant A** (G8 — hash file `.md` thật, giống hệt G2/G4): thêm cảnh báo nguyên khuôn
  cũ, đổi tên artifact/script cho đúng G8. Đồng thời nói rõ nhận xét phản biện THẬT phải
  là file khác hẳn — `G8_PEER_REVIEW_REPORT_<mã>.md` (do người phản biện viết theo mẫu
  `binh-duyet.md`), vì `.docx` này không chứa nhận xét thật.
- **Variant B** (G5, G9 — hash checkpoint JSON): cảnh báo KHÔNG được nói "sẽ ghi đè
  artifact đã hash" (sai) mà nói "không phản ánh trạng thái khóa/nghiệm thu THẬT — đọc
  checkpoint JSON hoặc chạy `gN_quality_gate.py --study <mã>`". Với G9 còn nêu thêm tên
  file THẬT của pipeline G9 (`G9_PUBLICATION_READINESS.json`) để không ai lặp lại đúng
  hiểu nhầm đã xảy ra ở VÒNG 4.

`_gen_generic()` trước đó là điểm vào DUY NHẤT cho `review` (G8) — không có hàm riêng để
gắn cảnh báo vào. Thay vì chèn logic đặc thù artifact vào `_gen_generic()` (sẽ làm hàm
generic không còn generic), tách phần thân render nội dung (list/dict/str) thành hàm
dùng chung `_render_kv_body()`, rồi thêm `_gen_review()` riêng gọi `_render_kv_body()` +
cảnh báo Variant A. `_gen_generic()` sau khi tách hành vi giữ NGUYÊN (có test khóa).

Kiểm tên file trước khi vá: `G5b_DMP_<mã>.docx` (thật là `G5_A6_DATA_MGMT_<mã>.md`/
`.docx`) · `G8_REVIEW_<mã>.docx` (thật là `G8_A9_PRESUBMISSION_<mã>.md`/`.docx`) ·
`G9_READINESS_<mã>.docx` (thật là `G9_PUBLICATION_READINESS.json`, không có `.docx`) —
**không tên nào trùng artifact ledger thật**, giữ đúng bất biến của `task_a5fde306`
(không đổi tên để "khớp" — nguy cơ ghi đè nhầm bản đã khóa).

Test mới: `tests/test_gen_research_docx_scaffold_warning_vong5_20260902.py` (7 mục —
3 cảnh báo đúng khuôn · 1 nội dung mặc định vẫn bảo thủ (NOT READY) · 1 không trùng tên
· 2 khóa hành vi refactor `_render_kv_body`). **5 phép đột biến, cả 5 đều đỏ đúng chỗ**
(gỡ từng cảnh báo G5/G8/G9 riêng lẻ · vô hiệu hóa nhánh render nội dung · đổi tên file
G8 trùng artifact thật). `pytest` toàn bộ nhóm test đụng `gen_research_docx.py` (9 file,
88 test) xanh; `ruff check` sạch. Toàn bộ pytest repo y khoa: **3225 passed, 42 skipped,
0 fail** (315s). Chi tiết ở commit `5ea8d13` repo y khoa (3 nhánh `claude/medical-research-
system-phggdf` · `master` · `feat/r1-1-2-design-gap-remediation` đã đồng bộ).

## 2-septies. VÒNG RÀ 6 — hai hàng scaffold khác nội dung dùng chung một khóa artifact

`SCAFFOLD_FILES` (21 hàng, `tools/scaffold_research_project.py`) có 3 cặp hàng dùng
CHUNG một `artifact_key`: `literature` (hàng 03/04), `sap` (hàng 11/15), `checklist`
(hàng 17/19) — điều tra để lại dở dang ở VÒNG RÀ 5 quay lại đây. Kiểm từng cặp bằng
`ARTIFACT_MAP[key]` (tiêu đề + nội dung generator thật, không suy đoán):

- `literature` — tiêu đề ARTIFACT_MAP đã gộp CẢ HAI khái niệm ("Tổng quan y văn &
  Evidence Ledger") → có chủ ý, gọi `generate()` hai lần cho hai hàng 03/04 ra cùng
  một nội dung đúng như thiết kế.
- `sap` — `_gen_sap()` tự có mục "10. Khung bảng kết quả dự kiến (Dummy Tables)" phủ
  đúng khái niệm của hàng 15 (Table_Shells) → cùng lý do, có chủ ý.
- `checklist` — tiêu đề ARTIFACT_MAP chỉ nói **"Checklist chuẩn báo cáo
  (CONSORT/STROBE/PRISMA)"**, không hề nhắc "kiểm toán completeness" — trong khi hàng
  19 (Research_Integrity_Audit) là một khái niệm HOÀN TOÀN KHÁC: bảng kiểm toán A1–A18
  (đủ hồ sơ IRB/đăng ký/cỡ mẫu…) trước khi nghiệm thu G9. **Đây là lỗi thật, không phải
  thiết kế.**

Tái hiện bằng `scaffold()` thật (không giả lập): chạy scaffold một đề tài test, log
cho thấy `G7b_CHECKLIST_<mã>.docx` được in **HAI LẦN** — lần từ hàng 17, lần từ hàng 19
— lần sau GHI ĐÈ lần trước trên đĩa. Vì cả hai lần gọi `generate("checklist")` đều
không truyền `content` (rơi vào `_gen_generic` với cờ nhắc điền rỗng), nội dung hai lần
ghi giống hệt nhau nên **không mất thông tin duy nhất nào trên đĩa** — nhưng
`STUDY_INDEX.md` (bảng bác sĩ đọc để biết trạng thái 20 tài liệu) ghi **CÙNG MỘT** tên
`.docx` kỳ vọng cho hai hàng 17 và 19 khác nội dung — bác sĩ đọc chỉ mục sẽ hiểu nhầm
hai mục dùng chung một tài liệu output.

Vá: thêm khóa `integrity-audit` (mã `G9b`, gate `G7-G9`) riêng cho hàng 19 trong
`ARTIFACT_MAP` — `len(ARTIFACT_MAP)` 38 → 39 (cập nhật cả assertion khóa hồi quy trong
`tests/test_gen_research_docx_round11_artifact_keys.py` lẫn con số cũ trong docstring
`generate()`). Không đổi `num`/`fname` của hai hàng 17/19 (nội dung `.md` — thứ cổng
thật đọc — chưa bao giờ bị ảnh hưởng, chỉ tên `.docx` phụ trợ mới trùng).

Test mới `tests/test_scaffold_checklist_vs_integrity_audit_distinct_20260902.py` (7
mục: 2 khóa khác nhau + mã riêng biệt · scaffold thật sinh 2 tên `.docx` khác nhau ·
2 file `.md` giữ nội dung thật distinct · `STUDY_INDEX.md` không còn ghi trùng tên cho
2 hàng). **2 phép đột biến, cả 2 đều đỏ đúng chỗ** (trả hàng 19 về khóa `checklist` cũ
→ 3 test đỏ; xóa khóa `integrity-audit` khỏi `ARTIFACT_MAP` → 4 test đỏ, gồm cả test
đếm-mã-không-trùng đã có từ vòng 11). Nhóm test đụng `gen_research_docx.py`/
`scaffold_research_project.py` (11 file, 109 test) xanh; `ruff check` sạch.

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
