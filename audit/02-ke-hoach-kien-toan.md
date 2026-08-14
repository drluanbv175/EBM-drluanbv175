# PHA 1 — KẾ HOẠCH KIỆN TOÀN THEO LÔ (chờ bác sĩ duyệt trước khi thi công)

> Nguyên tắc thi công (mục 10 của prompt): tái dùng tối đa, chỉ viết mới cho khoảng trống đã
> chứng minh ở `01-khoang-trong.md`; mỗi lô nhỏ, có nghiệm thu riêng, có rollback; không sửa
> `EBM_MASTER.json` khi chưa backup. **KHÔNG xây biên chế A1–C5 song song với 50 agent đang
> chạy** — chỉ tài liệu hoá ánh xạ + lấp khoảng trống (chống lỗi hai-sổ BH39/BH40).

## LÔ 0 — QUYẾT ĐỊNH CỦA BÁC SĨ (chặn các lô sau)

| # | Câu hỏi | Phương án đề xuất |
|---|---|---|
| Q1 | **Tên cổng** (K1): du nhập "G0–G6" mới hay giữ tên hiện có? | **Giữ tên hiện có.** `quality/gates.md` sẽ ánh xạ: G2-prompt (truy nguyên) → `verify_dashboard --online` + sổ xác minh + chuỗi rút bài; G4-prompt (liêm chính) → `--strict-sources` + PII + disclaimer; G6-prompt (người) → Cổng A/B + hàng chờ EBM_MASTER. Chuỗi G0–G10 nghiên cứu KHÔNG đổi |
| Q2 | 6 tác vụ nền (Updateebm…) có tồn tại phía claude.ai web không? | `[CẦN XÁC NHẬN TẠI ĐƠN VỊ]` — máy này không thấy. Nếu có: liệt kê để hợp nhất; nếu không: lịch tối giản ở Lô 1 là toàn bộ |
| Q3 | Nhịp chạy chấp nhận được? | Đề xuất: quét ứng viên TUẦN (tự phóng khi quá hạn 10ng) · rút bài toàn sổ THÁNG (hạn 30ng có sẵn) · guideline-bị-thay-thế QUÝ · độ trễ đo mỗi lượt quét |

## LÔ 1 — AN TOÀN VẬN HÀNH (K3 · K7 · K8 · K11) — nhỏ, làm trước

| Việc | Cách làm | Nghiệm thu | Rollback |
|---|---|---|---|
| Khoá ghi 2 máy | Lock file cạnh `.so-xac-minh-nguon.json` + `raw hits` (PID+host+tuổi, tự hết hạn 30'; theo mẫu `tu_khoi_dong`) | 2 tiến trình song song: 1 chạy, 1 FAIL rõ | xoá file lock |
| `alerts/YYYY-MM-DD.md` | Gom từ: sổ (retraction mới) · `kiem_chung_cu_vuot_qua` (guideline mới hơn cho mục apply) · cổng FAIL. CHỈ sự kiện khẩn — học BH32: không trộn mức | canary gài 1 retraction → file alerts sinh đúng | xoá thư mục alerts |
| `last_run_cursor` theo chủ đề | File `.cursor.json` cạnh watchlist; quét từ `max(cursor−3ng, now−days)` chống hở khe; `--days` vẫn là trần | chạy 2 lần liên tiếp: lần 2 chỉ quét phần mới; KHÔNG hở khe khi bỏ 1 tuần | xoá `.cursor.json` (quay về cửa sổ) |
| `--dry-run` | Thêm cho `build_library`/`make_derivatives`/ledger ops | chạy khô không đổi file (diff rỗng) | cờ mới, không ảnh hưởng mặc định |

## LÔ 2 — HỢP ĐỒNG DỮ LIỆU (K6) — hình thức hoá, KHÔNG migrate

| Việc | Cách làm | Nghiệm thu | Rollback |
|---|---|---|---|
| `contracts/evidence-item.schema.json` | Sinh TỪ schema đang chạy (DESIGN-SPEC §5 + trường mới `gradeBy`/`normativeBasis`/`provenanceUnknown`) + bổ sung khối prompt đòi (`source.resolved/retracted/superseded_by`, `provenance`, `human_review`). Gói CŨ giữ nguyên — schema áp cho gói MỚI | canary validate 1 gói mới PASS, 1 gói gài lỗi FAIL | file tài liệu, không đụng dữ liệu |
| `contracts/state-machine.md` | Ánh xạ máy trạng thái prompt ↔ hiện trạng: `VERIFIED`=sổ xác minh còn hạn · `CANDIDATE`=hàng chờ EBM_MASTER · `APPROVED`=bác sĩ duyệt (Cổng B) · `UNRESOLVED`=verify FAIL · cấm agent chuyển APPROVED/APPLIED (đã đúng hiện trạng — ghi thành luật + chốt BH mới kiểm bằng đột biến) | đột biến: cho tool thử ghi APPROVED → chốt đỏ | tài liệu |

## LÔ 3 — LỚP VIỆT NAM + AN TOÀN THUỐC (K5 · K10)

| Việc | Cách làm | Nghiệm thu | Rollback |
|---|---|---|---|
| `vn-guidelines/registry.json` skeleton | Trường: tên QĐ/hướng dẫn BYT · số-ngày `[CẦN XÁC NHẬN TẠI ĐƠN VỊ]` · URL kcb.vn nếu tra được · phạm vi. **Cấm bịa số quyết định** (I1) — ô trống là ô trống | mọi bản ghi hoặc có URL phân giải được hoặc mang nhãn `[CẦN…]` | xoá file |
| AWaRe overlay | Thêm nhóm `AWaRe` (Access/Watch/Reserve) vào `drug_flags.json` từ danh mục WHO (có nguồn), nối vào `drug_safety_scan` | dashboard có kháng sinh → cờ AWaRe hiện | bỏ nhóm khỏi JSON |

## LÔ 4 — ĐO LƯỜNG + GOLD SET (K4 · K9 · K14)

| Việc | Cách làm | Nghiệm thu | Rollback |
|---|---|---|---|
| `ops/metrics.py` — ĐỘ TRỄ | Với ứng viên: `ngày_vào_sổ − pubdate` (và `edat`); báo cáo phân vị + đếm vượt ngưỡng 14ng/7ng. Thiếu dữ liệu → `[CẦN BỔ SUNG]`, không ước lượng (I-mục-7) | chạy trên lượt quét thật ra bảng trễ | tool đọc-only |
| Quét "bị thay thế" theo QUÝ | Đưa `kiem_chung_cu_vuot_qua.py` vào nhịp quý qua `tu_khoi_dong` (watermark riêng) | watermark ghi + báo cáo sinh | gỡ khỏi tu_khoi_dong |
| Gold set 8→20+ | Thêm ca: guideline bị thay thế (KDIGO 2024→2026 thật) · SR AMSTAR thấp · outcome-switching · guideline mâu thuẫn (IMPACT 2 kết cục thật) · cao tuổi đa thuốc · DOI-của-bài-đã-rút (ca 30267080 thật) | canary 20+ ca xanh; đột biến từng nhóm đỏ đúng chỗ | test thêm, không đụng dây chuyền |

## LÔ 5 — TÀI LIỆU HOÁ BIÊN CHẾ (K12 · K13 + mục 9 của prompt)

| Việc | Cách làm |
|---|---|
| `AGENTS.md` (gốc hub) | Sơ đồ A/B/C ↔ tên thật (bảng ánh xạ ở `00-hien-trang.md` §6) + đường đi dữ liệu |
| `agents/<ID>-<ten>.md` | MỖI FILE LÀ CON TRỎ tới agent/tool thật (mục tiêu·I/O·FAIL·leo thang) — không nhân bản doctrine |
| `quality/gates.md` + `rubric.md` | Ánh xạ cổng (Q1) + trỏ `_RUBRIC-EVALUATE-CUNG-QA-GATE` |
| `ops/schedule.md` + `runbook.md` + `metrics.md` | Lịch tối giản thật (hook+tu_khoi_dong) · sự cố đã gặp (12 vụ có thật trong CLAUDE.md) · mẫu báo cáo tháng |
| Nguồn chân lý kép K13 | Skill `tham-dinh-chung-cu-grade-nnt` thêm 1 dòng đầu: "bản đầy đủ = agent `tham-dinh-grade-nnt`" |

## Thứ tự phụ thuộc & ước lượng

```
LÔ 0 (bác sĩ) ─┬─→ LÔ 1 (1 phiên) ─→ LÔ 4 (1 phiên)
               ├─→ LÔ 2 (1 phiên) ─→ LÔ 5 (1 phiên)
               └─→ LÔ 3 (nửa phiên; registry cần bác sĩ điền số QĐ thật)
```

Mỗi lô kết thúc bằng: chạy 45 chốt BH + canary + `kiem_dieu_phoi` + commit/push. Lỗi mới tìm
thấy trong lúc thi công → thành chốt BH mới (vòng học C4 — đang là `chot_hoi_quy_bai_hoc.py`).

## Tiêu chí nghiệm thu toàn cục (mục 11 prompt — đối chiếu hiện trạng)

- [x] G-truy-nguyên và G-liêm-chính đã CHẶN được ca lỗi cố tình — canary 8/8 (đã có)
- [x] Không item vào dashboard thiếu PMID/DOI phân giải — cổng đang chặn (đã có)
- [x] Agent không chuyển APPROVED/APPLIED — đúng hiện trạng; Lô 2 thêm chốt máy
- [ ] Chạy trọn A1→B5 trên 1 chủ đề thật với log đầy đủ — làm ở nghiệm thu PHA 2
- [ ] Idempotency 2 lần liên tiếp — Lô 1 (cursor) rồi nghiệm thu
- [x] PII/disclaimer/tờ-dặn-không-liều — cổng + make_derivatives đang giữ

---
**DỪNG THEO YÊU CẦU CỦA PROMPT — chờ bác sĩ duyệt kế hoạch này (đặc biệt LÔ 0/Q1–Q3) trước khi sang PHA 2.**

*Cần bác sĩ kiểm chứng.*
