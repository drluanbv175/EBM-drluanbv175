# PHA 1 — MA TRẬN HIỆN TRẠNG (kiểm kê 15/08/2026, xác minh bằng lệnh thật)

> Quy ước: ✓ = tồn tại, đã xác minh · ✗ = `[KHÔNG TÌM THẤY]` · ◐ = tồn tại một phần.
> Không suy đoán: mọi con số dưới đây lấy từ lệnh chạy trong phiên kiểm kê.

## 1. Skill (11 skill được nêu trong prompt)

| Skill | Trạng thái | Version | Ghi chú trùng lặp/mâu thuẫn |
|---|---|---|---|
| `cap-nhat-chung-cu-y-khoa` | ✓ | **1.41.0** | SKILL TRUNG TÂM. Vừa nâng 14–15/08: 4 lượt tìm (guideline gọi tên → SR/MA → RCT lớn → ⚡mới-vào-PubMed `edat` không lọc), kiểm rút bài 3 tầng, `gradeBy`/`normativeBasis`, `provenanceUnknown` |
| `quan-ly-cap-nhat-ebm` | ✓ | 1.0.0 | Quản sổ cái + hàng duyệt (queue/approve/apply) |
| `ebm-master` | ✓ | 1.0 | Nền tảng hợp nhất |
| `antifacts` | ✓ | 1.0.0 | Mặt tiền chuyên khoa |
| `dashboard-master-ebm-ngoai-tru` | ✓ | (không khai version) | Sổ quản trị riêng, ngoài dây chuyền chứng cứ |
| `tham-dinh-chung-cu-grade-nnt` | ✓ | 1.0.0 | Trùng vai với agent `tham-dinh-grade-nnt` (.claude/agents) — agent là bản đầy đủ hơn |
| `clinical-evidence-rag` | ✓ | (không khai) | ⚠ đã biết: `evidence/` phần lớn TRỐNG, chỉ đáng tin cho 32 thang điểm (ghi trong doctrine `tra-cuu-chung-cu` từ 24/07) |
| `nguoi-cao-tuoi-da-benh-da-thuoc` | ✓ | (không khai) | Lớp an toàn thuốc |
| `citation-management` | ✓ | 1.0 | |
| `paper-lookup` | ✓ | 1.0 | |
| `research-lookup` | ✓ | 2.0-vn | |

**Sổ đăng ký thứ hai — 50 agent `.claude/agents/`** (prompt không nêu nhưng là lực lượng chính):
2 nhạc trưởng (`dieu-phoi-lam-sang` gọi 23 agent · `dieu-phoi-nghien-cuu` gọi 31) + guardrail
`tham-dinh-dau-ra` (R1–R14, có R1c/R4b/R4c mới) · đồng bộ Claude↔Codex 50/50, `sync_errors 0`
· chốt điều phối `kiem_dieu_phoi.py` xanh (BH44).

## 2. Tool (7 tool được nêu)

| Tool | ✓ | `--online` | `--dry-run` | `--since/--days` | Exit code |
|---|---|---|---|---|---|
| `verify_dashboard.py` | ✓ | ✓ (+`--strict-sources`, `--check-topic`) | ✗ | ✗ | 0/1 chuẩn |
| `build_library.py` | ✓ | — | ✗ | ✗ | có |
| `make_derivatives.py` | ✓ | — | ✗ | ✗ | có |
| `drug_safety_scan.py` | ✓ | — | ✗ | ✗ | có |
| `surveillance_scan.py` | ✓ | (nguồn sống mặc định) | ✗ | ✓ `--days` | PASS/PARTIAL/FAIL, mã ≠0 khi hỏng |
| `manage_ledger.py` | ✓ `EBM_MASTER/tools/` | | | | |
| `bridge_to_ebm_master.py` | ✓ `medical-ebm-automation/scripts/` | | | | fail-closed theo `source_health` |

**Tool KHÔNG có trong prompt nhưng đang gánh dây chuyền** (dựng 12–15/08): `so_xac_minh_nguon.py`
(sổ xác minh 1.155 định danh) · `check_citation_retraction.py` + `retraction_chain.py` +
`crossref_retraction.py` (rút bài 3 tầng, phủ PMID+DOI) · `kiem_chung_cu_vuot_qua.py` (chứng cứ
bị vượt qua) · `kiem_phan_hang.py` (`gradeBy`) · `kiem_so_lieu.py` (đối chiếu hiệu số) ·
`dang_ky_chu_de.py` (mâu thuẫn giữa bản) · `kiem_phu_giam_sat.py` · `uu_tien_cap_nhat.py` ·
`chu_trinh_chung_cu.py` (6 chốt một lệnh) · `thu_dau_cuoi_chung_cu.py` (canary 8 lỗi gài) ·
`chot_hoi_quy_bai_hoc.py` (45 chốt BH01–BH45) · `kiem_dieu_phoi.py`.

## 3. Dữ liệu

| File | Trạng thái | Số đo |
|---|---|---|
| `EBM_MASTER/EBM_MASTER.json` | ✓ | 1.193 thẻ (400 apply · 636 consider · 148 notyet ở lần audit gần nhất; 7 cách ly) |
| `EBM-Dashboards/watchlist.json` | ✓ | **43 chủ đề**, 38 có 4 tầng truy vấn; 4 kênh gọi tên Cochrane/NICE/USPSTF/WHO |
| `EBM-Dashboards/library.json` | ✓ | 62 bản ghi = 62 dashboard |
| `EBM-Dashboards/data/drug_flags.json` | ✓ | 4 nhóm cờ (Beers/STOPP… — tự khai KHÔNG đầy đủ, chỉ để nhắc) |
| `vn-guidelines/registry.json` | **✗ [KHÔNG TÌM THẤY]** | Lớp VN hiện = field `vn` từng item + `[CẦN XÁC NHẬN TẠI ĐƠN VỊ]` + kcb.vn trong doctrine |
| `EBM-Dashboards/giam-sat-chu-de.json` | ✓ | 34 canh + 12 cố ý không — 46/46 khai đủ |
| `EBM-Dashboards/.so-xac-minh-nguon.json` | ✓ | 1.155 định danh, 99% còn hiệu lực, 2 hạn dùng (180ng/30ng) |
| `EBM-Dashboards/mau-thuan-da-duyet.json` | ✓ | 1 cặp bác sĩ đã duyệt "khác kết cục" |
| Schema item | ◐ | Sống trong `DESIGN-SPEC.md` §5 + template (meta/summary/standards/items[]) — **chưa có file `contracts/*.schema.json` hình thức** |

## 4. Lịch chạy — SỰ THẬT ĐO ĐƯỢC (khác kỳ vọng của prompt)

| Cơ chế | Trạng thái |
|---|---|
| launchd `com.medicalebm.weeklysafety` | ✓ nạp, **`runs = 0 · never exited`** — chưa từng nổ (máy không thức đúng giờ) |
| launchd `com.medicalebm.monthlyupdate` | ✓ nạp, **`runs = 0`** — như trên |
| 6 tác vụ nền (Updateebm · Guideline · Updatethuoc · Thangdiemls · Tonghopcapnhat · Ebmdakhoa) | **✗ [KHÔNG TÌM THẤY] trên máy này** — `list_scheduled_tasks` trả rỗng; không có trong `Scheduled/_DANG-KY-LICH-TREN-MAC.md`. Khả năng là tác vụ phía claude.ai web — `[CẦN XÁC NHẬN TẠI ĐƠN VỊ]` |
| `Scheduled/` (7 routine SKILL.md) | ✓ uptodate · drug-safety-daily · giam-sat-chung-cu · nckh · tong-hop-chung-cu-hang-tuan · tu-kiem-dong-bo · antifacts-weekly-ebm — là ĐẶC TẢ cho phiên, không phải daemon |
| **Cơ chế THẬT đang chạy** | Hook `SessionStart`: 7 chốt (`chot_hoi_quy_bai_hoc` 45 bài học + canary · `dong_bo_skill` · `kiem_do_tuoi_chung_cu` · `kiem_nguon_that` · `kiem_plugin_day_du` · `tu_khoi_dong` · `tu_sua_chua`) + `tu_khoi_dong --phong` phóng weekly/monthly khi quá hạn |

## 5. Đồng bộ Mac↔Windows

OneDrive đồng bộ cây `Claude AI/`; secrets ngoài OneDrive (`~/.ebm-secrets`, đọc thẳng từ
`app/config.py` — đã vá vụ symlink làm Windows chạy dữ liệu giả 12/08). Rủi ro đã biết và có
chốt: conflict-copy (`sync_safety_check.py`), 2 phiên ghi song song (đã gặp trong CHÍNH phiên
14/08 — phiên khác sửa `ViemGanB` giữa chừng), git-trong-OneDrive (hướng dẫn bundle).
**Chưa có**: khoá ghi cho `surveillance_scan`/sổ xác minh khi 2 máy cùng chạy (chỉ
`tu_khoi_dong` có khoá PID).

## 6. Ánh xạ biên chế ĐÍCH của prompt ↔ hiện có (Phụ lục A đã đối chiếu)

| Agent đích | Hiện có | Độ phủ |
|---|---|---|
| A1 Watchlist Curator | `watchlist.json` + `kiem_phu_giam_sat.py` + `uu_tien_cap_nhat.py` | ◐ 70% — thiếu: nuôi bằng log câu hỏi thực tế |
| A2 Source Harvester | `surveillance_scan.py` 4 tầng + 4 kênh gọi tên + `gan_do_tin_cay()` | ✓ 90% — thiếu: con trỏ tăng dần (mới có cửa sổ `--days`) |
| A3 Dedup & Triage | dedup trong lượt + `da_co_trong_kho` + ingest chống trùng pmid\|doi\|title | ◐ 75% — thiếu: khử trùng CHÉO LƯỢT bằng con trỏ |
| A4 Provenance Verifier | `so_xac_minh_nguon` + chuỗi rút bài 3 tầng (PMID+DOI) + Crossref `updated-by` | ✓ 95% — thiếu: kiểm "guideline bị THAY THẾ" chủ động (mới có qua `kiem_chung_cu_vuot_qua`) |
| A5 Critical Appraiser | agent `tham-dinh-grade-nnt` (RoB 2/ROBINS-I/AMSTAR-2/QUADAS-3 + AGREE II/ROBIS/CERQual mới nối 14/08) | ✓ 90% |
| A6 Effect Extractor | `tham-dinh-grade-nnt` (NNT/NNH) + `kiem_so_lieu.py` (as-reported check) | ✓ 85% |
| A7 Discordance Resolver | `dang_ky_chu_de.py` + `mau-thuan-da-duyet.json` + agent `dien-giai-ket-qua`/doctrine "nêu mâu thuẫn, không ép" | ◐ 70% — mạnh ở mâu thuẫn GIỮA BẢN, mỏng ở guideline-vs-guideline lúc nhận |
| A8 VN Localizer | field `vn` + `[CẦN XÁC NHẬN TẠI ĐƠN VỊ]` + kcb.vn doctrine | ◐ 50% — **thiếu registry** |
| A9 Safety Overlay | `drug_safety_scan.py` + `ke-don-an-toan` + `nguoi-cao-tuoi-da-benh-da-thuoc` | ✓ 85% — thiếu AWaRe tường minh |
| A10 Impact Classifier | `decision` 3 mức + cổng chặn `apply` yếu + `normativeBasis` | ✓ 95% |
| B1 Dashboard Builder | skill v1.41.0 + template EW | ✓ |
| B2 Integrity Gate | `verify_dashboard.py --online --strict-sources` (+chặn nguồn ĐÃ RÚT từ 14/08) | ✓ |
| B3 Librarian | `build_library.py` + `manage_ledger.py` + `sync_all.py` (chờ-duyệt mặc định) | ✓ |
| B4 Derivative Factory | `make_derivatives.py` + BỘ NĂM `xuat_goi_cap_nhat.py` | ✓ |
| B5 Approval Broker | hàng chờ duyệt EBM_MASTER + `trinh_muc_can_duyet.py` + Cổng A/B | ✓ 90% |
| C1 Red Team | canary `thu_dau_cuoi_chung_cu.py` (8 lỗi gài) + lịch sử đột biến từng chốt | ◐ 60% — 8 ca vs yêu cầu 20–30 |
| C2 Evaluator | `_RUBRIC-EVALUATE-CUNG-QA-GATE` + `tham-dinh-dau-ra` 2 lớp | ✓ 85% |
| C3 Observability | `observability/` (APPRAISALS.jsonl) + báo cáo từng tool | ◐ 60% — **chưa đo ĐỘ TRỄ** (≤14ng/≤7ng) |
| C4 Learner | `chot_hoi_quy_bai_hoc.py` — 45 bài học, mỗi lỗi thật → chốt vĩnh viễn, cấm nới cổng | ✓ 95% |
| C5 Orchestrator | 2 nhạc trưởng + hook SessionStart + `tu_khoi_dong` | ◐ 70% — thiếu khoá scan + lịch hợp nhất |

> **Kết luận hiện trạng: ~80% biên chế đích ĐÃ TỒN TẠI dưới tên khác.** PHA 2 đúng nghĩa là
> HỢP THỨC HOÁ + LẤP KHOẢNG TRỐNG, không phải xây song song — xây song song sẽ tái tạo đúng
> lỗi hai-sổ-đăng-ký-trôi-nhau mà BH39/BH40 vừa đóng.

*Cần bác sĩ kiểm chứng.*
