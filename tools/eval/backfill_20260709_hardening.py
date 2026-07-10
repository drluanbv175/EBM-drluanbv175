#!/usr/bin/env python3
"""backfill_20260709_hardening.py — Ghi vao LEDGER_LESSONS.jsonl vong 2 cua phien 2026-07-09:
kiem dinh doi khang TU PHAT HIEN (truoc khi ban giao, khong phai bac si/cong khac bat) tren
chinh 2 ham mien tru moi them trong vong 1, + dong 2 diem mem da ghi nhan o LSN-20260709-04.

  - LSN-20260709-05: BUG NGHIEM TRONG tu phat hien - _is_evidence_positioning() (vong 1) co
    the bi bypass bang cach ket hop ngon ngu "dinh vi chung cu/EtD" voi mo ta khong khop mau
    "benh nhan nam/nu NN"/"ca nay/cu the" liet ke huu han - trong khi VAN mo ta mot QUYET
    DINH LAM SANG THAT (dung trigger S1/R13 - ma ESCALATE_HARD nghiem trong nhat he). Da vá
    bang thiet ke 2 lop: (1) hard veto S1-trigger/red-flag/patient-marker, (2) yeu cau DUONG
    - doi chinh van ban TU NHAN "khong ap dung cho benh nhan" tuong minh (kho gia mao hon
    nhieu so voi chi tranh vai tu khoa).
  - LSN-20260709-06: dong LSN-20260709-04 (2 diem mem effect_size_ci_required + who_aware_
    if_antibiotic) - ca hai da sua that + re-test tren chinh RS-SMOKE da phat hien.

Idempotent (bo qua id da co).
"""
from __future__ import annotations
import json
from pathlib import Path

LEDGER = Path(__file__).resolve().parents[2] / "LEDGER_LESSONS.jsonl"

ENTRIES = [
    {
        "id": "LSN-20260709-05", "ngay_phat_hien": "2026-07-09T06:00:00+07:00",
        "ma_loi": "CLIN-SAFETYQ",
        "mo_ta": "BUG NGHIEM TRONG TU PHAT HIEN (truoc khi ban giao): ham _is_evidence_positioning() moi them (vong 1, cung phien) co the BI BYPASS - van ban ket hop ngon ngu dinh vi chung cu/EtD voi mo ta ca lam sang KHONG khop mau benh-nhan-that liet ke huu han (vd 'ca lam sang mat ngu man tinh... xin thuoc ngu manh' - dung trigger S1/R13) van bi mien red_flags/mandatory_safety_question SAI. Tu kiem dinh doi khang 3 bien the (S1/redflag/S2) truoc khi bao cao xong, KHONG doi bac si/cong khac bat.",
        "noi_phat_sinh": "tools/eval/run_eval.py::_is_evidence_positioning (code moi them 2026-07-09 vong 1, cung phien)",
        "cach_bat": "Tu chay 3 van ban doi khang tu tao (khong phai gold case co san) truoc khi bao cao hoan tat - phat hien is_evidence_positioning tra True SAI cho ca co trigger S1 that",
        "sua_gi": "Redesign 2 lop: (1) hard veto - KHONG BAO GIO mien neu co RE_S1_TRIGGER/RE_REDFLAG/_RE_REAL_PATIENT_PRESENT (bo RE_S2_TRIGGER khoi veto vi tu gay FP tren chinh CL-A8 that - ACEi duoc nhac nhu 1 nhom thuoc trong ban luan guideline, khong phai quyet dinh ke don); (2) yeu cau DUONG - bat buoc van ban TU NHAN tuong minh 'khong ap dung cho benh nhan' (ham _has_explicit_no_patient_disclaimer, dung cua so ky tu thay vi regex lien mach de chiu duoc dau ngoac kep chen giua tu nhu CL-A8 that viet).",
        "quy_tac_rut_ra": "MOI heuristic mien tru cong an toan MOI (dac biet lien quan R13/cac ma ESCALATE_HARD) PHAI qua tu-kiem-dinh-doi-khang (thu bypass bang >=2-3 cach dien dat khac nhau) TRUOC KHI coi la xong - khong duoc dung 'vang mat tin hieu nguy hiem' (whack-a-mole, liet ke mai van thieu) lam dieu kien mien DUY NHAT; phai doi tin hieu DUONG tuong minh tu chinh van ban.",
        "ghi_nguoc_vao": "tools/eval/run_eval.py (da sua) + tools/eval/test_classify.py (5 test moi khoa hoi quy: test_evidence_positioning_bypass_blocked_by_s1_trigger, test_evidence_positioning_bypass_blocked_without_explicit_disclaimer, + 3 test kiem chung dang DAT)",
        "trang_thai": "da-dong", "so_lan_tai_pham": 0,
        "re_test": "test_classify.py 46/46 PASS (9 test moi, gom 2 test khoa bypass) + re-run that tren CL-A8 that: is_evidence_positioning=True dung, verdict DAT; 3 bien the bypass tu tao deu bi chan dung (verdict TRA-VE-SUA, dung check duoc kich hoat lai)",
    },
    {
        "id": "LSN-20260709-06", "ngay_phat_hien": "2026-07-09T06:10:00+07:00",
        "ma_loi": "STAT-MISMATCH",
        "mo_ta": "Dong LSN-20260709-04 (2 diem mem phat hien qua smoke-test RS-SMOKE, truoc do CHUA sua): (a) effect_size_ci_required dung cua so +-240 ky tu qua hep, khong bat CI khi van ban tach doan 'ket qua kiem dinh y nghia' va doan 'uoc luong hieu ung' xa hon (do that: 437-537 ky tu, 3-4 doan van); (b) who_aware_if_antibiotic bat nham khi mo ta NHANH CAN THIEP nghien cuu (khang sinh du phong la bien so duoc nghien cuu, khong phai quyet dinh ke don that).",
        "noi_phat_sinh": "tools/eval/run_eval.py::evaluate (effect_size_ci_required, who_aware_if_antibiotic)",
        "cach_bat": "Da ghi nhan LSN-20260709-04 (moi, chua sua) - phien nay quay lai hoan tat theo dung tinh than 'sua cho toi' cua bac si",
        "sua_gi": "(a) doi cua so ky tu co dinh sang quet theo DOAN VAN (tach boi dong trong, dong bo GRD-SELF) - doan chua p-value CONG 4 doan lien sau; (b) them dieu kien 'typ == clinical' vao who_aware_if_antibiotic (dung tien le da co o red_flags/mandatory_safety_question).",
        "quy_tac_rut_ra": "Check MEM cung can phan biet BOI CANH (quyet dinh that vs mo ta/nghien cuu) - khong chi check CUNG (red_keys) moi can; cua so ky tu co dinh de bo sot khi van ban khoa hoc tach 'ket qua kiem dinh' va 'uoc luong hieu ung' thanh cac khoi rieng - nen quet theo DOAN VAN, khong phai so ky tu tuy y.",
        "ghi_nguoc_vao": "tools/eval/run_eval.py (da sua ca 2) + tools/eval/test_classify.py (4 test moi: paragraph-window catches distant CI + khong noi long qua tay + who_aware khong ap nghien cuu + who_aware van ap lam sang that)",
        "trang_thai": "da-dong", "so_lan_tai_pham": 0,
        "re_test": "RS-SMOKE re-run: effect_size_ci_required PASS (truoc FAIL sai), who_aware_if_antibiotic khong con trong checks list (truoc FAIL sai); test_classify.py 46/46 PASS; toan bo 6 probe lam sang (CL-A1..A5,A8) van DAT dung, khong hoi quy",
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
