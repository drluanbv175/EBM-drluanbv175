# 06/10/2026 — exports/ theo thư mục đang đứng tách đôi hồ sơ đề tài; G0-06; kinh phí G1 → đề cương G10; A12 bớt cảnh báo DOI thừa

Đợt «hoàn thiện từng bước» sau khi gộp y khoa #89/#92/#93 + gốc #128/#130/#131 (việc treo ở VIEC-CON của đợt soát
G0–G10). Nhánh y khoa `claude/hoan-thien-tung-buoc-20261006`; nhánh gốc `claude/hoan-thien-tung-buoc-goc-20261006`.

## 1. exports/<study>/ theo THƯ MỤC ĐANG ĐỨNG (lỗi có thật, có rác làm bằng chứng)

**Nguyên nhân (đo 06/10):**
- run_g0/g1/g2_auto và run_stats_analysis dựng `Path("exports")/study` theo thư mục đang đứng.
- CLI g0_quality_gate mặc định `--exports-dir exports`.
- Trong khi đó run_g3…g10 và bộ chấm G1–G10 neo theo gốc repo y khoa.
- Vài agent hướng dẫn chạy `python medical-ebm-automation/tools/run_g0_auto.py` từ repo gốc. Khi đó G0–G2 ghi
  `exports/` ở repo gốc, còn G3–G10 đọc `medical-ebm-automation/exports/`, nên hồ sơ MỘT đề tài tách làm hai nơi.
- run_stats_analysis còn lệch trong chính nó: checkpoint, artifact và đầu ra theo cwd, nhưng sổ cái và dữ liệu khoá
  (gate_contract) lại theo gốc repo.

**Bằng chứng:** repo gốc có `exports/PYTEST-GATEEXIT-G1` (15/07) — rác của một test, sinh ra khi pytest chạy từ repo gốc
(công cụ ghi theo cwd, test dọn theo gốc repo). Cùng thư mục có `exports/viem-gan-b-dieu-tri` (18/07) — sản phẩm THẬT
nằm sai chỗ. Chưa dọn — chờ bác sĩ quyết.

**Vá (y khoa):**
- Thêm `_thu_muc_de_tai()` neo theo `_REPO_ROOT` (G0/G1/G2) hoặc `BASE` (run_stats).
- run_g0/g1/g2_auto có thêm cờ `--repo-root`.
- g0_quality_gate mặc định đọc exports/ của repo.
- run_stats truyền `repo_root=BASE` cho sổ cái, khoá dữ liệu và lý do chặn.

**Bài học đo:**
- Lượt test đầu sau khi đổi mốc: 30 test đỏ, kèm **101 tệp rác trong exports/ THẬT của worktree** (16 thư mục đề tài thử).
- `git status` KHÔNG thấy số rác này, vì `.gitignore` che thư mục mới trong exports/. Chỉ phép chụp
  `find exports -type f` trước/sau mới lộ ra.
- Có test XANH mà vẫn xả rác (PYTEST-G0-EMPTY, ZZ-EMPTY).
- Đã chuyển 13 tệp test sang cô lập: vá `_REPO_ROOT`/`BASE`, hoặc dùng `--repo-root`/`--exports-dir` cho tiến trình con.

## 2. G0-06 — loại giả thuyết của G3 lấy từ test_type G0, có xét thiết kế

- Thứ tự nguồn: CLI > gate_params.G3 > đặc tả thiết kế G1 > `gate_params.G0.test_type` > mặc định máy.
- Bậc «test_type G0» bọc hai khe hở:
  - đề tài chưa có khối G1 (bản dựng lại bỏ qua G0);
  - G0 khai test_type SAU khi G1 đã chạy.
- **Lộ lỗi tiềm ẩn:** khối đặc tả G1 ánh xạ «descriptive» của đề tài ĐỊNH TÍNH thành `descriptive_precision`, tức khung
  cỡ mẫu theo độ chính xác. Hệ quả: G3-AUTO-17 REVIEW «ngôn ngữ power/alpha».
- Nay dùng `S.gia_thuyet_tu_test_type(test_type, thiết kế)` dùng chung cho khối G1, bản dựng lại và G3. Định tính, SR-MA
  và tiên lượng ⇒ None (cùng tập `N_NOT_APPLICABLE_DESIGNS`).

## 3. Kinh phí G1 → đề cương G10

- Mục «Dự trù kinh phí» trước đây chỉ đọc `study_meta.resources.budget`.
- Nay rơi về `gate_params.G1.budget` (cùng nguồn bảng KINH PHÍ của A13), nhưng CHỈ khi mọi dòng đủ 5 ô. Còn ô trống thì
  giữ «[CẦN]», vì không in một dự trù dở dang.
- `meta_for_render` bổ sung khoá còn thiếu vào khối resources dạng dict mà không sửa bản thô.
- «Tiến độ theo mốc cổng» vẫn chưa có nguồn khai. `study_schema_timeline` là lịch theo dõi người tham gia, KHÔNG phải
  tiến độ dự án — cố ý không ghép.
- C1a: A13 còn 11 ô «[CẦN]» và G1 chưa khai kinh phí, nên đề cương in «[CẦN]» là đúng sự thật.

## 4. A12 — DOI in kèm PMID đã kiểm không còn bị cảnh báo «tự tra Retraction Watch»

**Đo trên chuỗi thật 8 thiết kế:**
- Ghi chú cũ (DOI Piaggio 2012 lọt vào đề cương MỌI thiết kế) đã lỗi thời.
- Nhiễu thật nằm ở DOI SPIRIT 2025 (rct) và PRISMA-P 2015 (sr_ma): PMID song song đã có trong biên nhận.
- Với đề tài thật còn tệ hơn: dòng Vancouver dựng từ metadata PubMed luôn kèm `doi:`, nên cảnh báo sẽ bắn cho gần như MỌI
  tài liệu tham khảo.

**Vá:** ghép DOI↔PMID chỉ từ hai nguồn đã xác minh:
- metadata PubMed đã phân giải trong `A12_METADATA_RECEIPT.json`;
- cặp «doi:… (PMID …)» trong nguồn gốc tài liệu chuẩn (`protocol_checklist_items.cap_doi_pmid_tai_lieu_chuan`).

DOI không ghép được, hoặc ghép được nhưng PMID chưa có trong biên nhận ⇒ vẫn cảnh báo như cũ. Khớp doctrine
`kiem-chung-trich-dan` dòng 40.

## Kiểm

- `tests/test_hoan_thien_tung_buoc_20261006.py`: 16 test.
- Đột biến: 21/21 bị bắt.
- Toàn bộ bộ test y khoa: 8199 qua, 0 đỏ, 44 bỏ qua (commit y khoa 60a39c2).
- exports/ của worktree trước/sau: không đổi (so bằng `find`).

PR: drluanbv175/medical-ebm-automation#94 (y khoa) + PR gốc chứa tệp này.
