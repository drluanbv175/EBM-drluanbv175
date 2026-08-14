# CỔNG CHẤT LƯỢNG E0–E6 — hệ CẬP NHẬT CHỨNG CỨ (bác sĩ chốt Q1, 15/08/2026)

> **Tên cổng dùng tiền tố E (Evidence)** — tách hẳn chuỗi **G0–G10 của NGHIÊN CỨU**
> (`gate_contract.py`, chữ ký HMAC, KHÔNG đổi). Mỗi cổng E ánh xạ vào CÔNG CỤ THẬT đang
> chạy — bảng này là bản đồ, không phải tầng thi hành mới (chống hai-hệ-tên, BH39).

| Cổng | Kiểm gì | Thi hành bởi (công cụ thật) | FAIL thì |
|---|---|---|---|
| **E0** Phạm vi | chủ đề thuộc watchlist đã khai | `watchlist.json` + `kiem_phu_giam_sat.py` (46/46 chủ đề khai) | bỏ qua, ghi log |
| **E1** Thu hoạch | 4 tầng nguồn + tầng ⚡mới-vào-PubMed; khoá chống chạy chồng; cursor chống hở khe | `surveillance_scan.py` (4 tầng · `edat` · `gan_do_tin_cay` · lock · cursor) | chủ đề FAIL ghi rõ, không nuốt |
| **E2 (cứng)** Truy nguyên | PMID/DOI phân giải; RÚT BÀI 3 tầng (phủ cả DOI); rút-và-thay nói đúng mức | `so_xac_minh_nguon.py` + `check_citation_retraction.py` + `verify_dashboard --online` | `UNRESOLVED`, không vào dashboard |
| **E3** Thẩm định | đúng công cụ theo thiết kế (RoB 2·ROBINS-I·AMSTAR-2·**QUADAS-3**·AGREE II·ROBIS·CERQual); 3 lớp tách; `gradeBy`; hiệu số as-reported | agent `tham-dinh-grade-nnt` + `kiem_phan_hang.py` + `kiem_so_lieu.py` + validator `kiem_hop_dong_item.py` | trả về sửa |
| **E4 (cứng)** Liêm chính sản phẩm | `--strict-sources`: chặn `apply` yếu · Consensus · nguồn ĐÃ RÚT · PII · disclaimer | `verify_dashboard.py --online --strict-sources` + guardrail `tham-dinh-dau-ra` | chặn giao, mã ≠0 |
| **E5** Sổ cái & phái sinh | ledger chờ-duyệt, BỘ NĂM, tờ dặn không liều | `build_library` + `sync_all` (khi yêu cầu) + `xuat_goi_cap_nhat` | rollback lô (.bak-*) |
| **E6 (NGƯỜI)** Bác sĩ duyệt | Cổng A/B; `human_review.reviewed_by` bắt buộc cho APPROVED/APPLIED | hàng chờ EBM_MASTER + `kiem_hop_dong_item.py` (I4) + `trinh_muc_can_duyet.py` | giữ CANDIDATE vô thời hạn |

Chứng minh cổng CHẶN được: canary `thu_dau_cuoi_chung_cu.py` — 10 lỗi gài/10 bị bắt,
tự chạy mỗi phiên (BH43). Rubric chi tiết: `_RUBRIC-EVALUATE-CUNG-QA-GATE.md` (.claude/agents).

*Cần bác sĩ kiểm chứng.*
