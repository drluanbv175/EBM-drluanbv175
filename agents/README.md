# BIÊN CHẾ AGENT A/B/C ↔ HIỆN THÂN THẬT (LÔ 5, 15/08/2026)

> File này + 20 file con là **CON TRỎ**, không nhân bản doctrine (chống trôi BH39/BH40).
> Lực lượng thật: 50 agent `.claude/agents/` (đồng bộ Codex 50/50) + ~15 tool chứng cứ.
> Root `AGENTS.md` là hợp đồng repo (alignment-checked) — KHÔNG gộp vào đây.

Đường đi dữ liệu: `watchlist → quét(E1) → sổ xác minh(E2) → thẩm định(E3) → dashboard(E4)
→ ledger/BỘ NĂM(E5) → bác sĩ(E6)`. Cổng: `quality/gates.md`.

| ID | Agent | Hiện thân chính | Nhiệm vụ | Nhịp/Cổng |
|---|---|---|---|---|
| A1 | [watchlist-curator](./A1-watchlist-curator.md) | `watchlist.json` | Giữ watchlist khớp thực hành; 46/46 chủ đề khai canh/không-canh | THÁNG |
| A2 | [source-harvester](./A2-source-harvester.md) | `surveillance_scan.py` | Thu hoạch 5 tầng nguồn; ứng viên mang sẵn rút-bài/loại/trùng-kho/preprint | TUẦN |
| A3 | [dedup-triage](./A3-dedup-triage.md) | `surveillance_scan` | Khử trùng DOI/PMID; tín hiệu vs nhiễu | TUẦN |
| A4 | [provenance-verifier](./A4-provenance-verifier.md) | `so_xac_minh_nguon.py` | E2 cứng: phân giải + retraction + rút-và-thay | MỖI LẦN |
| A5 | [critical-appraiser](./A5-critical-appraiser.md) | `.claude/agents/tham-dinh-grade-nnt.md` | AGREE II·AMSTAR-2·RoB 2·ROBINS-I·QUADAS-3·ROBIS·CERQual·GRADE | MỖI LẦN |
| A6 | [effect-extractor](./A6-effect-extractor.md) | `tham-dinh-grade-nnt` | Hiệu số as-reported; NNT/NNH ghi công thức | MỖI LẦN |
| A7 | [discordance-resolver](./A7-discordance-resolver.md) | `dang_ky_chu_de.py` | Nêu khác biệt, không ép một kết luận | KHI CÓ |
| A8 | [vn-localizer](./A8-vn-localizer.md) | `vn-guidelines/registry.json` | [CẦN XÁC NHẬN TẠI ĐƠN VỊ] khi không tra được; CẤM bịa số QĐ | KHI CÓ |
| A9 | [safety-overlay](./A9-safety-overlay.md) | `drug_safety_scan.py` | Cờ nhắc, không đầy đủ | KHI CÓ THUỐC |
| A10 | [impact-classifier](./A10-impact-classifier.md) | `decision` | Áp dụng ngay/Cân nhắc/Chưa đủ + lý do | MỖI LẦN |
| B1 | [dashboard-builder](./B1-dashboard-builder.md) | `skill` | 3 cột + Quick View + etd | E4 |
| B2 | [integrity-gate](./B2-integrity-gate.md) | `verify_dashboard.py` | E4 cứng; FAIL chặn giao | E4 |
| B3 | [librarian](./B3-librarian.md) | `build_library.py` | Một sổ cái duy nhất | E5 |
| B4 | [derivative-factory](./B4-derivative-factory.md) | `xuat_goi_cap_nhat.py` | Tờ dặn KHÔNG liều; chờ duyệt | E5 |
| B5 | [approval-broker](./B5-approval-broker.md) | `hàng` | TUYỆT ĐỐI không tự duyệt (I4, validator thi hành) | E6 |
| C1 | [red-team](./C1-red-team.md) | `thu_dau_cuoi_chung_cu.py` | Mỗi lỗi thật → test vĩnh viễn | MỖI PHIÊN |
| C2 | [evaluator](./C2-evaluator.md) | `tham-dinh-dau-ra` | FAIL cứng chặn lô | MỖI GÓI |
| C3 | [observability](./C3-observability.md) | `do_tre` | Chỉ số mục 7; thiếu → [CẦN BỔ SUNG] | MỖI LƯỢT |
| C4 | [learner](./C4-learner.md) | `chot_hoi_quy_bai_hoc.py` | Lỗi lặp → chốt + sửa skill; CẤM nới cổng | MỖI PHIÊN |
| C5 | [orchestrator](./C5-orchestrator.md) | `dieu-phoi-lam-sang` | Khoá chống trùng + lịch + báo cáo | — |

*Cần bác sĩ kiểm chứng.*
