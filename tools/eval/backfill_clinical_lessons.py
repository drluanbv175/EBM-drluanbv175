#!/usr/bin/env python3
"""backfill_clinical_lessons.py — Nạp LỖI LÂM SÀNG THẬT vào LEDGER_LESSONS.jsonl.

Vá khoảng hở D2 (rubric lâm sàng): trước đây ledger chỉ có lỗi *mã cổng kiểm*
(run_eval.py), ~0 mục về lỗi LÂM SÀNG thật. Script này append (idempotent, append-only,
PII-FREE) các mục lỗi lâm sàng ĐÃ ĐƯỢC GHI NHẬN ở nơi khác trong hệ:

  • 2026-06-15: 4 lỗi lâm sàng thật từ kiểm-toán per-case 50 vignette (_STATUS_50_CASES.md) —
    safety-net thiếu, AWaRe thiếu, disclaimer thiếu, trích dẫn sai — đã ghi-ngược vào agent
    và RE-TEST 2026-07-08 (probe CL-A4/CL-A5/CL-A6) xác nhận KHÔNG tái phạm (recurrence↓).
  • 2026-07-08: 2 DƯƠNG TÍNH GIẢ của cổng QA rule-based phát hiện khi chạy cổng thật trên
    output probe CL-A5/CL-A8 (cổng buộc citation cho tờ dặn BN; áp red-flag cho output định
    vị chứng cứ) — đề xuất fix, KHÔNG tự sửa run_eval.py (đang có thay đổi chưa commit của
    phiên khác → tránh clobber; ghi vào PROMOTION_QUEUE để phiên sở hữu áp).

KHÔNG bịa: mọi mục truy về nguồn đã ghi (_STATUS_50_CASES.md / APPRAISALS.jsonl phiên này).
Chạy lại nhiều lần AN TOÀN: bỏ qua mục có `id` đã tồn tại.
"""
from __future__ import annotations
import json
from pathlib import Path

LEDGER = Path(__file__).resolve().parents[2] / "LEDGER_LESSONS.jsonl"

ENTRIES = [
    # ── LỖI LÂM SÀNG THẬT (2026-06-15, kiểm-toán per-case 50 vignette) ──────────────
    {
        "id": "LSN-20260615-01", "ngay_phat_hien": "2026-06-15T00:00:00+07:00",
        "ma_loi": "CLIN-SAFETYNET",
        "mo_ta": "Kiem-toan per-case 50 vignette: goi ngoai tru cua dieu-phoi-lam-sang thieu safety-netting (dau hieu quay lai ngay/tieu chi that bai/moc tai kham) o 4 ca (C01, C02, C17, C49). PII-FREE (chi ma ca).",
        "noi_phat_sinh": "dieu-phoi-lam-sang (buoc 5 Theo doi) + loi-dan-tuan-thu",
        "cach_bat": "Kiem-toan per-case (run_eval red_flags/safety-net + doi chieu rubric) — 4/50 ca thieu",
        "sua_gi": "Them khoi 'Dau hieu nguy hiem -> di kham ngay' + moc tai kham chuan cho 4 ca",
        "quy_tac_rut_ra": "MOI goi ngoai tru PHAI co safety-netting du 3 phan (dau hieu quay lai ngay - tieu chi that bai dieu tri - moc tai kham) truoc khi roi tay; khong phu thuoc bac si hoi.",
        "ghi_nguoc_vao": "loi-dan-tuan-thu.md (khoi 5 'Dau hieu nguy hiem -> Tai kham' bat buoc) + tham-dinh-dau-ra.md (CLIN-SAFETYNET TIER-1)",
        "trang_thai": "da-dong", "so_lan_tai_pham": 0, "so_ca_trong_dot": 4,
        "re_test": "2026-07-08 probe CL-A5: agent tu them safety-netting day du -> ghi-nguoc HIEU QUA, khong tai pham",
    },
    {
        "id": "LSN-20260615-02", "ngay_phat_hien": "2026-06-15T00:00:00+07:00",
        "ma_loi": "DRG-ABX",
        "mo_ta": "Kiem-toan per-case: 3 ca THUC SU ke khang sinh (C17, C29, C30) thieu phan loai WHO AWaRe (Access/Watch/Reserve). 5 ca co co AWaRe khac la duong tinh gia (KS trong danh sach tranh/tuong tac).",
        "noi_phat_sinh": "ke-don-an-toan / dieu-phoi-lam-sang",
        "cach_bat": "Kiem-toan per-case (who_aware_if_antibiotic) — 3/50 ca ke KS that thieu AWaRe",
        "sua_gi": "Sinh lai 3 ca bang ke-don-an-toan co AWaRe + nguon xac minh",
        "quy_tac_rut_ra": "Moi khuyen cao CO ke khang sinh phai gan phan loai AWaRe + danh gia 'co thuc su can'; phan biet 'ke KS' voi 'nhac KS trong danh sach tranh'.",
        "ghi_nguoc_vao": "ke-don-an-toan.md (M7/buoc 7 AWaRe bat buoc khi co KS)",
        "trang_thai": "da-dong", "so_lan_tai_pham": 0, "so_ca_trong_dot": 3,
        "re_test": "2026-07-08 probe CL-A4: agent ap AWaRe (azithromycin=Watch) + tu choi KS khong chi dinh -> ghi-nguoc HIEU QUA",
    },
    {
        "id": "LSN-20260615-03", "ngay_phat_hien": "2026-06-15T00:00:00+07:00",
        "ma_loi": "GAP-MISSING",
        "mo_ta": "Kiem-toan per-case: 21/50 ca thieu disclaimer 'Can bac si kiem chung' (ban cham ca-file che loi per-case).",
        "noi_phat_sinh": "dieu-phoi-lam-sang (buoc tong hop goi)",
        "cach_bat": "Doi cham ca-file -> cham PER-CASE (lo 21 ca thieu)",
        "sua_gi": "Them disclaimer tung ca -> 50/50 co",
        "quy_tac_rut_ra": "Kiem liem chinh phai PER-CASE khong ca-file; disclaimer 'Can bac si kiem chung' bat buoc moi goi.",
        "ghi_nguoc_vao": "run_eval.py (cham per-case) + tham-dinh-dau-ra.md (R7 disclaimer moi goi)",
        "trang_thai": "da-dong", "so_lan_tai_pham": 0, "so_ca_trong_dot": 21,
        "re_test": "2026-07-08: ca 6 probe deu co 'Can bac si kiem chung'",
    },
    {
        "id": "LSN-20260615-04", "ngay_phat_hien": "2026-06-15T00:00:00+07:00",
        "ma_loi": "CIT-WASH",
        "mo_ta": "kiem-chung-trich-dan bat 2/50 ca sai trich dan: C12 (PMID 34163157 -> dung 33122447, treatable-trait), C48 (PMID 2178409 = Guyatt 1990 + sua 'tien/chua man kinh').",
        "noi_phat_sinh": "dieu-phoi-lam-sang (trich dan trong goi)",
        "cach_bat": "kiem-chung-trich-dan (tra PubMed doc lap) — 2/50",
        "sua_gi": "Thay PMID dung noi dung",
        "quy_tac_rut_ra": "Moi PMID phai doi chieu NOI DUNG do dung luan diem (khong chi phan giai duoc); kiem-chung-trich-dan chay truoc khi chot goi co trich dan.",
        "ghi_nguoc_vao": "kiem-chung-trich-dan.md (buoc 3 doi chieu noi dung) — da co",
        "trang_thai": "da-dong", "so_lan_tai_pham": 0, "so_ca_trong_dot": 2,
        "re_test": "2026-07-08 probe CL-A6 (cung ngay): PMID ma 99999999 bi bat, tu choi thay bai khac",
    },
    # ── DƯƠNG TÍNH GIẢ CỔNG QA (2026-07-08, phát hiện khi chạy cổng thật phiên này) ──
    {
        "id": "LSN-20260708-51", "ngay_phat_hien": "2026-07-08T20:46:00+07:00",
        "ma_loi": "CIT-GHOST",
        "mo_ta": "DUONG TINH GIA cong QA: run_eval red-check pmid_or_doi buoc trich dan cho to dan benh nhan kho A5 (CL-A5, loi-dan-tuan-thu) von KHONG can citation inline (chung cu nam o goi khuyen cao da duyet). Output DUNG bi RETURN-FOR-FIX sai [R1].",
        "noi_phat_sinh": "tools/eval/run_eval.py::evaluate (pmid_or_doi trong red_keys, khong phan loai document-type)",
        "cach_bat": "Chay cong that tren CL-A5 phien nay -> RETURN-FOR-FIX [R1]; grader doc lap: output DUNG -> FP",
        "sua_gi": "Chua sua ma (run_eval.py dang co thay doi chua commit cua phien khac -> ghi de xuat, tranh clobber)",
        "quy_tac_rut_ra": "Cong QA phai phan loai DOCUMENT-TYPE truoc khi ap red-check; tai lieu benh nhan (to dan A5/loi dan) MIEN pmid_or_doi (khong co khang dinh chung cu moi, chi dien dat goi da duyet). Over-return la huong an toan nhung nen tinh chinh.",
        "ghi_nguoc_vao": "[DE XUAT] run_eval.py::evaluate — nhan dien typ='patient-leaflet' (heuristic: 'to dan'/'loi dan'/kho A5 + khong co 'khuyen cao'/GRADE) -> bo pmid_or_doi khoi red_keys cho typ do; PROMOTION_QUEUE.md",
        "trang_thai": "moi", "so_lan_tai_pham": 0,
    },
    {
        "id": "LSN-20260708-52", "ngay_phat_hien": "2026-07-08T20:46:00+07:00",
        "ma_loi": "CLIN-REDFLAG",
        "mo_ta": "DUONG TINH GIA cong QA: run_eval ap red_flags + mandatory_safety_question cho output DINH VI CHUNG CU/chinh sach (CL-A8, huong-dan-lam-sang — khong co benh nhan cu the). Output DUNG bi RETURN-FOR-FIX sai [R12, R13].",
        "noi_phat_sinh": "tools/eval/run_eval.py::evaluate (typ='clinical' theo tu khoa thuoc/benh, khong phan biet task 'ca benh nhan' vs 'dinh vi chung cu')",
        "cach_bat": "Chay cong that tren CL-A8 phien nay -> RETURN-FOR-FIX [R12, R13]; grader doc lap: output DUNG -> FP",
        "sua_gi": "Chua sua ma (tranh clobber phien khac)",
        "quy_tac_rut_ra": "Cong QA phai phan biet TASK-TYPE: chi ap red_flags/mandatory_safety_question cho output CO benh nhan thuc (ca lam sang/ke don), KHONG ap cho dinh vi chung cu/EtD/tong quan (khong co BN de sang loc).",
        "ghi_nguoc_vao": "[DE XUAT] run_eval.py::evaluate — them phan loai task 'evidence-positioning' (heuristic: EtD/dinh vi/khuyen cao don vi + khong co 'benh nhan'/trieu chung cu the) -> mien red_flags/safety-question; PROMOTION_QUEUE.md",
        "trang_thai": "moi", "so_lan_tai_pham": 0,
    },
]


def main() -> None:
    existing_ids = set()
    if LEDGER.exists():
        for line in LEDGER.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                existing_ids.add(json.loads(line)["id"])
            except (json.JSONDecodeError, KeyError):
                pass
    added = 0
    with open(LEDGER, "a", encoding="utf-8") as f:
        for e in ENTRIES:
            if e["id"] in existing_ids:
                print(f"  = bo qua (da co): {e['id']}")
                continue
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
            print(f"  + them: {e['id']}  [{e['ma_loi']}]  {e['ngay_phat_hien'][:10]}")
            added += 1
    print(f"\nDA THEM {added} muc / tong {len(ENTRIES)} de xuat. Ledger: {LEDGER}")
    print("Can bac si kiem chung.")


if __name__ == "__main__":
    main()
