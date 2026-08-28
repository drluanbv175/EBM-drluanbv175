# Rà toàn diện hệ nghiên cứu & cập nhật chứng cứ — phiên cloud 28/08/2026

**Người chạy:** Claude Code (phiên cloud, bản sao git trần — KHÔNG có cây OneDrive).
**Phạm vi kiểm được:** repo gốc `EBM-drluanbv175` (tools/ · .claude/agents/ · sync/ ·
clinical_runtime/ · ops/ · contracts/ · quality/). **Phạm vi KHÔNG kiểm được ở máy này:**
`medical-ebm-automation/` (repo riêng — toàn bộ cổng G0–G10 runtime, gate_contract, ledger),
`EBM-Dashboards/` (verify_dashboard + 60+ dashboard), `EBM_MASTER/` (sổ cái), cấu hình máy
(`~/.claude/settings.json`, venv, plugin). Báo cáo này nói rõ từng kết luận thuộc phạm vi nào —
**không suy «xanh ở đây» thành «toàn kho sạch»** (đúng quy ước CI đã ghi trong
`.github/workflows/kiem-tinh-da-nen.yml`).

Cần bác sĩ kiểm chứng.

---

## 1. Vì sao «gọi plugin không được» trong phiên này

`/claude-code-harness:harness-loop` báo *Unknown command* vì **phiên cloud không có plugin
nào của hai máy**. Đo trực tiếp trên container: không có `~/.claude/settings.json`, không có
`~/.claude/plugins/cache`, không có marketplace nào — chỉ có (a) nội dung repo git và
(b) skill đồng bộ theo TÀI KHOẢN (40+ skill riêng của bác sĩ, trong đó có
`cap-nhat-chung-cu-y-khoa`, `nghien-cuu-y-khoa-chuan-quoc-te`…).

Plugin (`claude-code-harness`, aipoch, medsci…) là **cài đặt cấp MÁY** — nằm ở
`~/.claude/plugins/` trên Mac/Windows, không đi theo git, không đi theo tài khoản. Đây là
tầng thứ ba của cùng một bài học đã ghi (BH72/BH81 — ngân sách skill; cache plugin):
**ba môi trường = ba kho công cụ khác nhau**:

| Môi trường | Có gì |
|---|---|
| Mac / Windows | plugin (harness, aipoch…) + skill riêng + agent + tools |
| Phiên cloud (claude.ai/code) | skill riêng theo tài khoản + agent + tools trong repo — **KHÔNG plugin** |

Trong phiên cloud, thay `/claude-code-harness:harness-loop` bằng: nói thẳng việc cần làm
(agent + tools của repo đều dùng được), hoặc skill dựng sẵn `/loop` cho việc lặp.

## 2. Đã kiểm những gì, kết quả ra sao

| Bộ kiểm | Kết quả | Ghi chú |
|---|---|---|
| `compileall tools ops` (sàn Python 3.11 THẬT — container chạy 3.11.15) | ✅ PASS | BH80 đứng vững lần đầu trên môi trường 3.11 thật |
| `chot_hoi_quy_bai_hoc` (BH01–BH82) | ✅ 47 ✓ · ⚪ 36 ngoài phạm vi · **0 tái phát** | xem mục 3 — trước phiên này in 37 ✗ |
| `kiem_dieu_phoi` (đồ thị điều phối 50 agent) | ✅ 🟢 sau khi vá | trước: 🔴 1 tham chiếu không phân giải |
| `enforce_agent_guardrails` | ✅ 50/50 agent, 0 file phải sửa | doctrine nguyên vẹn |
| `sync_agents_to_codex` + `--check` + `check_claude_codex_sync_health` | ✅ PASS 50/50 ×2 mirror | mirror tự sinh lại trên máy này |
| `kiem_tuong_thich_da_nen` (R1–R6) | ✅ 0 chặn · 0 cảnh báo | |
| `verify_clinical_runtime_schema_hardening` | ✅ PASS | |
| `verify_clinical_practice_apply_gate` | ✅ PASS (chặn đúng red-flag) | |
| `tu_de_xuat_viec --gon` | ✅ chạy trọn | các mục 🔴/🟠 đều là việc trên máy thật (mục 5) |
| `pytest tools/` | 258 pass · 23 fail · 4 lỗi thu thập | **giống hệt trước và sau bản vá** — 0 hồi quy; toàn bộ fail do thiếu repo y khoa/EBM-Dashboards hoặc test viết cho APFS (case-insensitive) chạy trên Linux |
| `audit_ebm_system` | ⛔ FAIL **có khai báo** | mọi ⛔ đều là «thiếu medical-ebm-automation / EBM_MASTER trên máy này» — đúng sự thật |
| `sync_safety_check` | 🟡 THẬN TRỌNG | bình thường với clone tươi |
| `kiem_safety_net` | 🟡 1/8 hội chứng có nguồn | trạng thái trung thực đã ghi từ 22/08 — điền nội dung là thẩm quyền bác sĩ |
| `chu_trinh_chung_cu --nhanh` | 🟡 5 việc chờ | phần lớn cần máy thật; bước ⑤ nay khai báo rõ thay vì traceback |

## 3. Lỗi THẬT tìm thấy và đã sửa (2)

### 3a. Skill `nghien-cuu-y-khoa-chuan-quoc-te` chạy runtime mà KHÔNG có nguồn (BH44 tái phát)

- **Đo được:** 4 file doctrine (`dieu-phoi-nghien-cuu.md`, `_CROSSWALK-NGHIEN-CUU.md`,
  `_PLUGIN-ROUTING-CONTRACT.md`, `_THU-VIEN-KY-NANG.md`) tham chiếu skill này, nhưng
  `sync/skills/` (40 skill) không có nó — chỉ tồn tại ở runtime tài khoản. App dọn runtime
  (đã xảy ra: 20/22 skill lệch bản ngày 13/08) là **mất trắng** — đúng họ lỗi đã cứu 3 skill
  ngày 15/08.
- **Đã sửa:** chép nguyên gói 38 file (SKILL.md v9 + modules/ + quality/ + references/ +
  scripts/ + templates/ + workflows/) từ runtime về `sync/skills/nghien-cuu-y-khoa-chuan-quoc-te/`,
  đối chiếu **khớp byte**. `kiem_dieu_phoi` từ 🔴 về 🟢.

### 3b. «Tường đỏ giả» trên bản sao git trần (vi phạm BH08, suýt che lỗi 3a)

- **Đo được:** bộ chốt in **37 mục ✗**, nhưng phân loại từng mã cho thấy **36/37 đỏ chỉ vì
  nguyên liệu nằm ngoài git** (13 mã cần `verify_dashboard.py`, 3 cần `surveillance_scan.py`,
  phần còn lại cần repo y khoa / EBM_MASTER / cấu hình máy). Chỉ MỘT mục (BH44) là lỗi thật —
  và nó đứng lẫn giữa 36 mục đỏ giả. Đây đúng là điều BH08 cảnh báo: «bức tường đỏ giả sẽ dạy
  người ta bỏ qua cả cảnh báo thật».
- **Đã sửa (BH82, mutation-tested 3 phép):** trên bản sao trần (cả 3 gốc dữ liệu vắng mặt),
  mục thiếu nguyên liệu in **⚪ «ngoài phạm vi» — vẫn hiện đầy đủ, không đếm đỏ, kèm dòng
  «⚪ KHÔNG có nghĩa là ĐẠT»**; lỗi trong-repo vẫn ✗ và exit 1. Trên máy thật (còn ≥1 gốc)
  hành vi fail-closed cũ giữ NGUYÊN — một file thiếu vẫn ✗ như trước. Danh sách 36 mã khai
  báo TƯỜNG MINH (`_CAN_NGUYEN_LIEU_NGOAI_REPO`), không suy từ thông điệp lỗi.

### 3c. Vá kèm — 7 công cụ «chết không lời» trên bản trần (cùng họ 3b)

`audit_ebm_system` (chết giữa chừng, NUỐT toàn bộ kết quả đã gom) · `dang_ky_chu_de` ·
`verify_lessons_rubric_alignment` · `verify_hard_gate_count_consistency` ·
`verify_research_gate_contracts` · `verify_research_practical_readiness` ·
`verify_controlled_research_automation` — nay đều «bỏ qua CÓ KHAI BÁO» một dòng rõ nghĩa
(vẫn FAIL/exit≠0, không giả xanh). `kiem_do_tuoi_chung_cu` hết tự xưng «Máy này (Windows)»
khi đứng trên Linux.

## 4. Về hai yêu cầu «cổng tự động» và «phủ hết nguồn chứng cứ» — nói thẳng phạm vi

**Cổng nghiên cứu G0–G10:** tầng DOCTRINE (50 agent, đồ thị điều phối, hợp đồng plugin-owner,
guardrail, mirror Codex) kiểm được ở đây và **sạch**. Tầng RUNTIME (11 file `g*_quality_gate.py`,
`approve_gate.py` đã nối G2/G4/G8 trước-ký theo audit 24/08, canary BH72, ledger niêm phong)
nằm TRỌN trong `medical-ebm-automation/` — **máy này không có repo đó nên KHÔNG kiểm lại
được**. Trạng thái mới nhất có bằng chứng là audit đa-agent 24/08 (đã ghi trong CLAUDE.md):
3144 test pass, 6 cổng cứng fail-closed. Muốn tái xác nhận hôm nay: chạy trên Mac/Windows
`pytest` trong repo y khoa + `python3 tools/thu_dau_cuoi_cong_nghien_cuu.py`.

**Phủ nguồn chứng cứ:** watchlist 4 nguồn thẩm quyền (Cochrane/NICE/USPSTF/WHO) + tầng 4
`moi_vao_pubmed` (edat, không lọc ptyp) + chuỗi rút bài 3 tầng — đều đã xác nhận «active»
trong audit 24/08; **kho dashboard và sổ xác minh nằm ngoài git nên phiên này không đo lại
được độ phủ**. Con số gần nhất có bằng chứng: 0/63 chủ đề quá ngưỡng đỏ 120 ngày (24/08);
độ phủ xác minh nguồn 99% (14/08). Đo lại: `python3 tools/chu_trinh_chung_cu.py` trên máy thật.

**Điều tôi KHÔNG làm:** không «điền PASS» cho bất kỳ cổng nào, không ký thay, không giả lập
UAT/phê duyệt — đúng quy tắc «không dùng PASS kỹ thuật thay IRB/PI/thống kê viên/phản biện».

## 5. Việc còn chờ (không tự làm được từ cloud / thẩm quyền bác sĩ)

1. **Giám sát an toàn thuốc tuần** — log không có trên máy này; kỳ gần nhất cần kiểm trên
   máy thật (`bash medical-ebm-automation/scripts/weekly_safety.sh`).
2. **Safety-netting 1/8 hội chứng có nguồn, 0/8 lời dặn bệnh nhân** — điền là thẩm quyền
   bác sĩ (Cổng A), máy không được sinh thay.
3. **Pre-commit hook không thể xanh trên bản sao trần** (bước `verify_claude_code_repo_alignment`
   cần repo y khoa nằm cạnh) — hook vẫn là chốt của hai máy thật; phiên cloud đã chạy tay
   các bước chạy được (sync mirror ✓, sync health ✓) và ghi rõ ở đây thay vì lách.
4. **Test `test_sync_agents_to_codex.py::test_real_checkout_active_targets_dedups...`** viết
   riêng cho filesystem case-insensitive (APFS/NTFS) — trên Linux nó fail «oan» vì `.Codex`
   và `.codex` là hai thư mục thật. Nếu muốn CI Linux chạy được test này thì phải thêm skip
   theo nền tảng — để bác sĩ quyết, không tự sửa trong đợt này.
5. **5 mục `gradeLevel:'na'` chờ neo phân hạng thật** (3 CKD + 2 RA) và **ITEM-05 ViemGanB
   (rút-và-thay)** — các quyết định lâm sàng tồn đọng từ 14/08, chỉ bác sĩ quyết.

## 5-bis. VÒNG 2 cùng ngày — «Hoàn thiện cho tôi» (3 việc đã đóng thêm)

### (a) Safety-netting: 1/8 → 8/8 hội chứng có nguồn — ĐỀ XUẤT chờ bác sĩ chuẩn y

7 hội chứng còn trống của `clinical_runtime/safety_net_templates.json` (v2.1.0) nay có khối
cờ đỏ cho bác sĩ, mỗi khối neo vào MỘT nguồn đã tra PubMed ngày 28/08 (metadata khớp,
không mục nào mang nhãn Retracted Publication — theo PubMed):

| Hội chứng | Nguồn (đã tra PubMed) | PMID / DOI |
|---|---|---|
| Đau ngực | Marburg Heart Score — Bösner, CMAJ 2010 | 20603345 · [10.1503/cmaj.100212](https://doi.org/10.1503/cmaj.100212) |
| Khó thở | NEWS2 — RCP 2017 (guideline); caveat Pimentel, Resuscitation 2018 | 30287355 · [10.1016/j.resuscitation.2018.09.026](https://doi.org/10.1016/j.resuscitation.2018.09.026) |
| Đau bụng (hẹp: khó tiêu) | ACG/CAG Dyspepsia — Moayyedi 2017 | 28631728 · [10.1038/ajg.2017.154](https://doi.org/10.1038/ajg.2017.154) |
| Sốt | qSOFA (Sepsis-3) — Seymour, JAMA 2016 | 26903335 · [10.1001/jama.2016.0288](https://doi.org/10.1001/jama.2016.0288) |
| Đau thắt lưng | Downie, BMJ 2013 (tổng quan hệ thống) | 24335669 · [10.1136/bmj.f7095](https://doi.org/10.1136/bmj.f7095) |
| Chóng mặt (chỉ HC tiền đình cấp) | HINTS — Kattah, Stroke 2009 | 19762709 · [10.1161/STROKEAHA.109.551234](https://doi.org/10.1161/STROKEAHA.109.551234) |
| Sụt cân | Gaddey & Holder, Am Fam Physician 2021 | 34264616 (PubMed không ghi DOI) |

**Kỷ luật đã giữ:** chỉ ghi điều tóm tắt nguồn THẬT SỰ nói — ngưỡng nào tóm tắt không nêu
(ngưỡng tuổi của «older age» ở Downie; ngưỡng ≥5%/6–12 tháng của sụt cân; bảng alarm
features đầy đủ của ACG/CAG) thì ghi rõ ở `gioi_han_nguyen_van_cua_nguon` là *cần đối
chiếu toàn văn*, KHÔNG ghi thành tiêu chí. Mỗi khối mang nhãn `de_xuat` nói rõ **chưa được
bác sĩ chuẩn y**. `dan_benh_nhan_quay_lai` cả 8 hội chứng giữ `[CẦN BÁC SĨ ĐIỀN]` — lời dặn
bệnh nhân là thẩm quyền bác sĩ (Cổng A), máy không sinh thay. `kiem_safety_net`: 0 lỗi cứng ·
8/8 có nguồn · 21/21 test pass.

### (b) Bộ test tools/ chạy sạch trên bản sao trần

`tools/conftest.py` mới: 4 module import repo y khoa lúc thu thập + 23 test đích danh cần
cây OneDrive → **skip CÓ KHAI BÁO** (đọc lý do bằng `pytest -rs`); 1 test viết riêng cho
filesystem APFS/NTFS → skip theo phép đo thuộc tính filesystem THẬT (không đoán theo os).
Kết quả: 23 fail + 4 lỗi thu thập → **258 pass · 23 skip · 0 fail**; đối chứng fail-closed
đã đo (tạo lại một gốc dữ liệu ⇒ fail quay về đúng chỗ). Ghi nhận trung thực: bản đầu của
conftest skip oan 81/92 test của `test_classify` vì quy tắc «cả file» — phát hiện nhờ so
số pass trước/sau (258 → 177), đã khai lại đích danh 11 test.

### (c) CI có thêm bước test thật — và lần chạy ĐẦU TIÊN đã bắt được 2 lỗi thật

`.github/workflows/kiem-tinh-da-nen.yml` thêm bước `pytest tools/` trên lane **ubuntu**
(đúng điều kiện vừa đo). Lane **windows chưa bật có chủ ý** — chưa có phép đo nào trên
Windows bare-clone, và một bức tường đỏ chưa đo sẽ dạy người ta bỏ qua cả đỏ thật (BH08);
điều kiện mở ghi ngay trong workflow.

**Lần CI đầu tiên chạy pytest (run #89) ĐỎ — và cả hai lỗi đều là phát hiện THẬT, đúng
lý do để nối test vào CI:**

1. 🔴 **`test_scan_deduplicates_pmid_across_topics` — unit test phụ thuộc MẠNG THẬT.**
   `run_scan` có hai làn phụ gọi thẳng medRxiv + ClinicalTrials.gov mà test không stub.
   Trên CI (mạng đi thẳng), truy vấn giả «A»/«B» kéo về ứng viên THẬT: candidate_count
   1 → 10, test đỏ. Trên máy dev đi proxy, hai làn lỗi êm (fail-soft) nên test
   **«tình cờ xanh» suốt từ khi ra đời** — cùng họ «công cụ vẫn chạy, vẫn in kết quả
   hợp lệ, nhưng thứ cần kiểm thì không được kiểm». Vá: fixture autouse chặn cả hai làn
   trong file test — unit test phải NGOẠI TUYẾN và tất định, đúng luật của chính bộ chốt.
2. 🔴 **`test_agent_sync_health_is_green` đỏ trên checkout tươi** — mirror Codex là bản
   tự sinh cố ý không track, nên checkout tươi không có. Vá ở workflow: chạy
   `sync_agents_to_codex.py` TRƯỚC pytest — nhờ đó chính đường sync mirror cũng thành
   thứ CI kiểm thật mỗi lần push.

Đối chứng trên clone sạch theo đúng luồng CI mới: **258 pass · 23 skip · 0 fail**.

## 6. Số đo trước/sau của phiên này

| Chỉ số | Trước | Sau |
|---|---|---|
| Bộ chốt bài học trên bản trần | 37 ✗ (36 giả + 1 thật lẫn nhau) · exit 1 | 47 ✓ · 36 ⚪ khai báo · 0 ✗ · exit 0 |
| Tham chiếu điều phối không phân giải | 1 (skill mất nguồn) | 0 — 41 skill nguồn |
| Skill nguồn trong `sync/skills/` | 40 | 41 (+gói 38 file, khớp byte runtime) |
| Công cụ chết-traceback trên bản trần | 7 | 0 (đều khai báo rõ, vẫn fail-closed) |
| `pytest tools/` trên bản trần | 258 pass · 23 fail · 4 lỗi thu thập | **258 pass · 23 skip khai báo · 0 fail** |
| Mirror Codex trên máy này | 0 TOML | 50/50 ×2, check PASS |
| Safety-netting: hội chứng có nguồn cờ đỏ | 1/8 | **8/8** (đề xuất, chờ bác sĩ chuẩn y) |
| CI chạy test thật | không | có (lane ubuntu, skip khai báo) |
