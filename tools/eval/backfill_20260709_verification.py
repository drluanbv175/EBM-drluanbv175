#!/usr/bin/env python3
"""backfill_20260709_verification.py — Ghi vao LEDGER_LESSONS.jsonl viec HOAN TAT + XAC MINH
cac khoang ho con lai tu SCORECARD-LAMSANG_2026-07-08.md / SCORECARD_2026-07-08_NGHIEN-CUU.md
(phien 2026-07-09):

  - LSN-20260709-01/02: dong LSN-20260708-51/52 (2 duong tinh gia cong QA) - da sua + re-test
    that qua run_eval.py --source gate tren chinh 2 probe CL-A5/CL-A8 da phat hien FP.
  - LSN-20260709-03: hoan tat "1 buoc hoa mang con lai" - wire research_checks.py vao
    run_eval.py::evaluate(), sinh APPRAISAL nhanh NGHIEN CUU dau tien tren mot ban thao that.
  - LSN-20260709-04: PHAT HIEN MOI (khong chan) 2 diem non cua 2 check mem co san, tim thay
    qua chinh smoke-test tren - CHUA sua (ngoai pham vi phien nay), ghi nhan trung thuc.

Idempotent (bo qua id da co). KHONG bia: moi id tham chieu APPRAISAL-<id> that da sinh
o observability/APPRAISALS.jsonl phien nay.
"""
from __future__ import annotations
import json
from pathlib import Path

LEDGER = Path(__file__).resolve().parents[2] / "LEDGER_LESSONS.jsonl"

ENTRIES = [
    {
        "id": "LSN-20260709-01", "ngay_phat_hien": "2026-07-09T05:15:00+07:00",
        "ma_loi": "CIT-GHOST",
        "mo_ta": "FIX + VERIFY LSN-20260708-51: them _is_patient_leaflet() (heuristic to dan/loi dan/kho A5 + KHONG co khuyen cao/GRADE moi) mien pmid_or_doi cho van ban to dan benh nhan.",
        "noi_phat_sinh": "tools/eval/run_eval.py::evaluate (pmid_or_doi)",
        "cach_bat": "Ke thua tu LSN-20260708-51 (grader doc lap phat hien FP ngay hom truoc); fix ap dung + re-test that phien nay",
        "sua_gi": "Them _RE_PATIENT_LEAFLET/_RE_NEW_EVIDENCE_CLAIM + _is_patient_leaflet(); pmid_or_doi tra pass=True kem ghi chu n/a khi la to dan",
        "quy_tac_rut_ra": "Cong QA PHAI phan loai document-type truoc khi ap red-check pmid_or_doi; to dan/loi dan A5 dien dat lai phac do da duyet KHONG can trich dan moi.",
        "ghi_nguoc_vao": "tools/eval/run_eval.py (da ap dung that, khong con [DE XUAT])",
        "trang_thai": "da-dong", "so_lan_tai_pham": 0,
        "re_test": "2026-07-09: run_eval.py --source gate tren CL-A5 -> APPRAISAL-20260709T051508-fa5ca9, verdict PASS, tier0_red_fails=[] (truoc: RETURN-FOR-FIX, tier0_red_fails=['pmid_or_doi'])",
    },
    {
        "id": "LSN-20260709-02", "ngay_phat_hien": "2026-07-09T05:15:00+07:00",
        "ma_loi": "CLIN-REDFLAG",
        "mo_ta": "FIX + VERIFY LSN-20260708-52: them _is_evidence_positioning() (heuristic EtD/dinh vi chung cu + KHONG co benh nhan cu the) mien red_flags + mandatory_safety_question cho van ban dinh vi chung cu cap he thong.",
        "noi_phat_sinh": "tools/eval/run_eval.py::evaluate (red_flags, mandatory_safety_question)",
        "cach_bat": "Ke thua tu LSN-20260708-52 (grader doc lap phat hien FP ngay hom truoc); fix ap dung + re-test that phien nay",
        "sua_gi": "Them _RE_EVIDENCE_POSITIONING/_RE_REAL_PATIENT_PRESENT + _is_evidence_positioning(); 2 check bo qua (khong them vao checks list) khi la dinh vi chung cu khong co benh nhan",
        "quy_tac_rut_ra": "Cong QA PHAI phan biet TASK-TYPE: chi ap red_flags/mandatory_safety_question cho output CO benh nhan thuc; dinh vi chung cu/EtD/tong quan khong co BN cu the thi mien.",
        "ghi_nguoc_vao": "tools/eval/run_eval.py (da ap dung that, khong con [DE XUAT])",
        "trang_thai": "da-dong", "so_lan_tai_pham": 0,
        "re_test": "2026-07-09: run_eval.py --source gate tren CL-A8 -> APPRAISAL-20260709T051510-977488, verdict PASS, tier0_red_fails=[] (truoc: RETURN-FOR-FIX, tier0_red_fails=['red_flags','mandatory_safety_question'])",
    },
    {
        "id": "LSN-20260709-03", "ngay_phat_hien": "2026-07-09T05:29:00+07:00",
        "ma_loi": "STD-REPORT",
        "mo_ta": "Hoan tat '1 buoc hoa mang con lai' cua SCORECARD_2026-07-08_NGHIEN-CUU.md muc 7: wire research_checks.py (STD-REPORT/STAT-MISMATCH/AI-DISCLOSE) vao run_eval.py::evaluate(). Sinh ban ghi APPRAISAL nhanh NGHIEN CUU DAU TIEN tren mot doan Ket qua doan he hu cau that (agent viet-ban-thao that, tu tinh lai thong ke bang Python doc lap).",
        "noi_phat_sinh": "tools/eval/run_eval.py::evaluate + tools/eval/research_checks.py",
        "cach_bat": "Khong phai loi bi bat - la hoan tat viec con do dang da duoc chinh scorecard 2026-07-08 xac dinh ro",
        "sua_gi": "3 diem noi (import + checks+=research_checks(...) + CHECK_ID_TO_RCODE.update(...)); test_classify.py 37/37 khong hoi quy, research_checks.py selftest 9/9",
        "quy_tac_rut_ra": "Module check moi phai duoc HOA MANG THAT vao run_eval.py::evaluate(), khong chi ton tai nhu module doc lap co selftest rieng - neu khong D1 khong the tien tu muc 2 len 3 cho nhanh do (co logic nhung chua bao gio cham that tren dung nhanh).",
        "ghi_nguoc_vao": "tools/eval/run_eval.py (da hoa mang that) + observability/APPRAISALS.jsonl (APPRAISAL-20260709T052941-61fc71 - ban ghi nhanh nghien cuu dau tien tu truoc den nay)",
        "trang_thai": "da-dong", "so_lan_tai_pham": 0,
        "re_test": "APPRAISAL-20260709T052941-61fc71: verdict PASS, ca 3 check moi (reporting_standard/stat_mismatch/ai_disclosure) deu DAT tren van ban nghien cuu that",
    },
    {
        "id": "LSN-20260709-04", "ngay_phat_hien": "2026-07-09T05:29:41+07:00",
        "ma_loi": "STAT-MISMATCH",
        "mo_ta": "PHAT HIEN MOI (khong chan/khong auto-fail, qua smoke-test RS-SMOKE) 2 diem non cua 2 check MEM co san tu truoc (ITER_1 2026-07-08, KHONG phai do phien nay them): (a) effect_size_ci_required (R8) dung cua so +-240 ky tu quanh p-value de tim CI gan do - mot van ban tach rieng khoi 'ket qua kiem dinh y nghia' (chi p, vd so sanh 3 phuong phap kiem dinh) va khoi 'uoc luong hieu ung' (RR/OR/ARR kem CI) o xa hon lam check bao FAIL SAI du van ban CO du CI; (b) who_aware_if_antibiotic bat tu khoa 'khang sinh' ke ca khi dang MO TA mot NHANH CAN THIEP nghien cuu (khang sinh du phong la BIEN SO duoc nghien cuu, khong phai quyet dinh ke don that).",
        "noi_phat_sinh": "tools/eval/run_eval.py::evaluate (effect_size_ci_required, who_aware_if_antibiotic) - code co tu ITER_1 2026-07-08",
        "cach_bat": "Chay that run_eval.py tren RS-SMOKE_cohort-results (agent viet-ban-thao that) de sinh APPRAISAL nhanh nghien cuu dau tien - phat hien phu ngoai muc tieu chinh",
        "sua_gi": "CHUA sua (ca hai la check MEM, KHONG trong red_keys, khong doi verdict/khong chan DAT cho ca nay) - de xuat, chua ap dung, ngoai pham vi phien nay",
        "quy_tac_rut_ra": "[CAN BAC SI QUYET] (a) effect_size_ci_required nen xet CI ca truoc+sau trong pham vi doan van (khong chi cua so ky tu co dinh quanh p-value), HOAC chap nhan 'bao cao kiem dinh rieng, uoc luong hieu ung rieng' la van phong hop le khong nen phat; (b) who_aware_if_antibiotic nen gioi han boi canh QUYET DINH KE DON (ke-don-an-toan), khong ap cho van ban MO TA bien so can thiep trong ban thao nghien cuu.",
        "ghi_nguoc_vao": "[DE XUAT] observability/PROMOTION_QUEUE.md - chua sua run_eval.py, chi ghi nhan qua smoke-test de bac si/phien sau quyet",
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
