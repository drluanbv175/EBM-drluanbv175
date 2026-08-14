# EBM Copilot — hub cập nhật chứng cứ ngoại trú (bản đồ 10 dòng)

1. **Một cửa:** `python3 ops/orchestrator.py --topic "<chủ đề>" --online` (A2 quét → A4 truy nguyên → B2 cổng → B5 hàng chờ; `--dry-run` xem trước, `--resume <run_id>` chạy tiếp).
2. **Sức khoẻ toàn hệ:** `python3 tools/chu_trinh_chung_cu.py --nhanh` · chốt hồi quy `python3 tools/chot_hoi_quy_bai_hoc.py` (BH01–BH48, tự chạy mỗi phiên).
3. **Sổ cái:** `EBM_MASTER/EBM_MASTER.json` (1193 thẻ) — sức khoẻ: `tools/validate_ledger.py`; truy nguyên: `tools/provenance_ledger.py`; di trú: `tools/migrate_ledger.py` (dry-run, chờ bác sĩ).
4. **Kho dashboard:** `EBM-Dashboards/` (62 bản, cổng `verify_dashboard.py` exit 0/1/2) · BỘ NĂM: `tools/xuat_goi_cap_nhat.py <file> --online`.
5. **Biên chế agent + ma trận quyền GHI:** `agents/README.md` (20 hồ sơ 10-mục; decision/APPROVED = BÁC SĨ, không tool nào).
6. **Hợp đồng dữ liệu:** `contracts/` (schema + máy trạng thái; validator `tools/kiem_hop_dong_item.py --self-test`).
7. **Chất lượng:** cổng E0–E6 `quality/gates.md` · gold set `python3 quality/eval/run_eval.py` (12 nhóm) · báo cáo vào `reports/`.
8. **Vận hành:** lịch thật `ops/schedule.md` · sự cố `ops/runbook.md` · số đo `ops/metrics.md` · khẩn cấp `alerts/<ngày>.md` · sao lưu `backups/` (`LATEST.txt`).
9. **Tra công cụ:** mở `TRA-CUU-CONG-CU.html` (không tốn ngữ cảnh) hoặc `/cong-cu-gi <việc>`.
10. **Luật nền:** máy chỉ ĐỀ XUẤT — Cổng A/B và mọi `decision` thuộc bác sĩ; mọi đầu ra kèm PMID/DOI + "Cần bác sĩ kiểm chứng"; KHÔNG PII; im lặng ≠ an toàn.
