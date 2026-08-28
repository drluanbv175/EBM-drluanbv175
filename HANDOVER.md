# HANDOVER — người khác tiếp quản hệ trong 30 phút (PHA 5 LÔ 7, 15/08/2026)

1. **Hệ là gì:** giám sát chứng cứ EBM ngoại trú; máy chỉ ĐỀ XUẤT, bác sĩ giữ Cổng A/B.
   Bản đồ 10 dòng: `README.md`. Vận hành thường kỳ: prompt PHA 3 (tuần/tháng/quý/năm).
2. **Chạy tuần:** `python3 EBM-Dashboards/tools/surveillance_scan.py` → chọn ≤7 thẻ
   → `queue/tuan-<W>.md` (mẫu W33). Một cửa theo chủ đề: `python3 ops/orchestrator.py
   --topic "<tên>" --online`. Tra điểm khám: `python3 tools/tra_diem_kham.py "<câu hỏi>"`.
3. **Sức khoẻ:** mở phiên là 7 hook tự chấm (bộ chốt BH + canary (con số hiện hành in đầu phiên)). Đỏ = việc số 1.
   Tay: `python3 tools/chu_trinh_chung_cu.py --nhanh` · `python3 tools/sources_health.py`.
4. **Duyệt:** bác sĩ ghi ✓/✗ vào queue; decision/gradeLevel KHÔNG tool nào được sửa
   (ma trận `agents/README.md`). Sự cố: `ops/runbook.md`. Đề xuất đổi hệ:
   `reports/de-xuat-thay-doi.md` (chờ phiên PHA 2 mới).
5. **NGỦ ĐÔNG** (nghỉ dài): `python3 tools/tu_khoi_dong.py --tat` (dừng sinh thẻ mới);
   GIỮ quét rút bài + an toàn thuốc bằng cách vẫn mở phiên định kỳ (hook chạy) hoặc
   chạy tay `tools/provenance_ledger.py` mỗi tháng. Quay lại: xoá cờ
   `.tu-khoi-dong-tat`, chạy scan `--since <ngày nghỉ>` → báo cáo «đã bỏ lỡ gì».
6. **Khôi phục:** snapshot `backups/` + `LATEST.txt`; diễn tập PHỤC HỒI THẬT đã chạy
   15/08/2026 (hash khớp từng byte — `ops/runbook.md` §Sao lưu); lặp lại MỖI QUÝ
   (chu trình quý PHA 3). Secrets NGOÀI OneDrive: `~/.ebm-secrets/` — máy mới phải
   chép tay (xem CLAUDE.md).
7. **Chi phí định kỳ:** API miễn phí (PubMed/Crossref/EuropePMC/openFDA) · lưu trữ
   OneDrive hiện có · Claude theo gói bác sĩ đang dùng · toàn văn: quyền cá nhân
   [CẦN XÁC NHẬN TẠI ĐƠN VỊ]. Ngưỡng xem lại: khi phát sinh phí API/khoá trả tiền.
8. **Phiên bản đang tin:** skill cap-nhat v1.45.0 · Python venv `~/.ebm-venv`
   (requirements.lock) · đổi lớn mô hình/thư viện → chạy `quality/eval/run_eval.py`
   + toàn bộ chốt BH TRƯỚC khi tin lại.
9. **NHẬN VỀ TỪ PHIÊN CLOUD 28/08/2026** (nhánh `claude/medical-research-system-phggdf`,
   CI xanh, chờ bác sĩ merge): trên MỖI máy sau khi kéo nhánh — (a) chạy
   `python3 tools/chot_hoi_quy_bai_hoc.py`: trên máy đủ dữ liệu cả 83 chốt phải chạy đủ,
   KHÔNG mục nào ⚪ (⚪ chỉ hợp lệ trên bản clone không có cây OneDrive); (b) DUYỆT 7 khối
   cờ đỏ safety-netting mang nhãn `de_xuat` trong `clinical_runtime/safety_net_templates.json`
   — nguồn đã tra PubMed nhưng CHƯA được bác sĩ chuẩn y, và lời dặn bệnh nhân 0/8 là phần
   bác sĩ tự viết (Cổng A); (c) đọc `audit/05-ra-toan-dien-ban-sao-tran_2026-08-28.md`
   để biết trọn ba vòng thay đổi (BH82/BH83, conftest, CI pytest 4 lane).
