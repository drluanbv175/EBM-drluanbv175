# BIÊN CHẾ AGENT — hệ cập nhật chứng cứ (PHA 2, cập nhật LÔ 3 15/08/2026)

20 hồ sơ trong thư mục này là **con trỏ biên chế 10-mục**: mỗi file khai định
danh, đầu vào/ra, công cụ, **file được ghi**, cổng, điều kiện dừng khẩn, giới
hạn, một ca chuẩn và số đo. Doctrine thật nằm ở HIỆN THÂN (tool/skill/agent
`.claude/agents/`) — sửa ở nguồn, không sửa ở đây.

> **Vì sao ma trận GHI nằm ở đây mà không ở `AGENTS.md` gốc:** file gốc là hợp
> đồng của REPO (bị `verify_claude_code_repo_alignment.py` khoá và phiên khác
> đang biên tập). Lệch khỏi đề bài có chủ ý, ghi lại tại đây (luật mục 10).

## Sơ đồ luồng chuẩn (một chủ đề)

```
watchlist (BÁC SĨ, A1 đề xuất)
   │
   ▼
A2 thu hoạch ──A10 nhãn tin cậy──A3 dedup/ưu tiên──► ứng viên surveillance/*.md
   │                                  │
   │        A4 truy nguyên (E2 cứng) ─┤   A9 cờ an toàn thuốc
   │        A5 phân hạng khai báo ────┤   A7 mâu thuẫn giữa bản
   │        A6 đối chiếu số liệu ─────┘
   ▼
B1 dựng dashboard ──► B2 CỔNG liêm chính (exit 0/1/2) ──► B3 thư viện ──► B4 BỘ NĂM
                                                              │
                                            B5 trình bác sĩ ──┴──► CỔNG A/B (NGƯỜI)
C1 canary · C2 eval · C3 quan sát · C4 chốt bài học · C5 orchestrator (bọc ngoài)
```

## MA TRẬN QUYỀN GHI — mỗi file state có đúng MỘT chủ

| File | Chủ ghi DUY NHẤT | Ghi chú |
|---|---|---|
| `EBM-Dashboards/watchlist.json` | **BÁC SĨ** | A1 chỉ đề xuất |
| `EBM-Dashboards/giam-sat-chu-de.json` | **BÁC SĨ** | khai báo phạm vi (BH29) |
| `EBM-Dashboards/mau-thuan-da-duyet.json` | **BÁC SĨ** | qua phiên duyệt A7 trình |
| `EBM-Dashboards/.quet-cursor.json` | A2 | dưới khoá `.quet.lock` |
| `EBM-Dashboards/.quet.lock` | A2 | pid+host, hết hạn 30' |
| `EBM-Dashboards/.so-xac-minh-nguon.json` | A4 | chỉ ghi THÀNH CÔNG |
| `EBM-Dashboards/data/drug_flags.json` | A9 | đợt có bác sĩ duyệt |
| `EBM-Dashboards/WebDashboard_*.html` | B1 | `.bak-*` trước mỗi đợt sửa |
| `EBM-Dashboards/library.json` + `evidence-library.html` | B3 | |
| `EBM-Dashboards/derivatives/*` | B4 | + bản quét quý (owner `quarterly_superseded.sh`) |
| `EBM_MASTER/EBM_MASTER.json` | `EBM_MASTER/tools/` (sync_all/ingest) | CHỈ khi bác sĩ yêu cầu (mặc định 05/08) |
| `EBM_MASTER/EBM_MASTER.v2.json` | `tools/migrate_ledger.py --ap-dung` | CHỈ sau khi bác sĩ duyệt diff |
| `vn-guidelines/registry.json` | A8 (khung) / **BÁC SĨ** (nội dung) | cấm bịa số QĐ |
| `reports/*.md` | mỗi công cụ MỘT tên file riêng | ledger-health / provenance-* / eval-* |
| `logs/*.jsonl` | C5 | mỗi run_id một file |
| `backups/<ISO>/` | quy trình LÔ 0 | chỉ tạo, không sửa |
| `alerts/<ngày>.md` | ⚠️ **NGOẠI LỆ CÓ CHỦ Ý**: kênh APPEND chung (A2, A4, quét quý) | từng dòng idempotent theo định danh — kiểm trước khi ghi, không nhân đôi |
| `decision`/`gradeLevel`/`APPROVED`/`APPLIED` trong MỌI file | **BÁC SĨ — không tool nào** | I4/BH10; validator I4 thi hành |

**Luật:** (1) không agent nào ghi file ngoài dòng của mình; (2) ghi state phải
qua khoá khi có thể chạy song song (`ops/lock.py`); (3) mọi lần sửa hàng loạt
có `.bak-<timestamp>`; (4) im lặng ≠ an toàn — FAIL phải nói RÕ (I7).

## Chỉ mục

| Nhánh A — thu nhận | Nhánh B — sản xuất | Nhánh C — bảo đảm |
|---|---|---|
| A1 watchlist-curator | B1 dashboard-builder | C1 red-team |
| A2 source-harvester | B2 integrity-gate | C2 evaluator |
| A3 dedup-triage | B3 librarian | C3 observability |
| A4 provenance-verifier | B4 derivative-factory | C4 learner |
| A5 critical-appraiser | B5 approval-broker | C5 orchestrator |
| A6 effect-extractor · A7 discordance-resolver · A8 vn-localizer · A9 safety-overlay · A10 impact-classifier | | |

> Cần bác sĩ kiểm chứng. Máy chỉ ĐỀ XUẤT — Cổng A/B và mọi `decision` thuộc bác sĩ.
