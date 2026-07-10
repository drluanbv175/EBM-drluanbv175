#!/usr/bin/env python3
"""backfill_20260709_round4_adversarial.py — Ghi vao LEDGER_LESSONS.jsonl VONG 4 kiem dinh
doi khang doc lap - trong tam R1/R1b/R4/R5/R6/R11 (truoc do chua phu dung muc) + 6 probe
F1-boundary (bounded vs vo han) + R2 regression + E2 recheck + kiem dinh lai lop LLM judgment
bang 1 loi goi agent that. Idempotent.
"""
from __future__ import annotations
import json
from pathlib import Path

LEDGER = Path(__file__).resolve().parents[2] / "LEDGER_LESSONS.jsonl"

ENTRIES = [
    {
        "id": "LSN-20260709-19", "ngay_phat_hien": "2026-07-09T09:00:00+07:00",
        "ma_loi": "GRD-CONF",
        "mo_ta": "TRUNG BINH (LOGIC - ap lai ky thuat da chung minh, khong phai phat minh moi): label_gaming_r1b (R1b) dung has_src TOAN VAN BAN - 1 PMID that nhung LAC DE o doan van khac (khong lien quan cac nhan [CAN...]) van lam has_src=True, che mat viec CAC NHAN NAY khong co nguon nao gan - CUNG LOP LOI 'presence != per-claim attribution' da vá cho no_fabrication/GRD-SELF 2026-07-08.",
        "noi_phat_sinh": "tools/eval/run_eval.py::evaluate (label_gaming_r1b)",
        "cach_bat": "Tu thiet ke probe R1b-c doc lap, xay dung CAN THAN (khac loi tu construct cua R4a/R1ba vong 3) - PMID ro rang o doan RIENG biet ve chu de KHAC han",
        "sua_gi": "Ap dung ky thuat paragraph-scoping (da chung minh o no_fabrication 2026-07-08) cho label_gaming_r1b: neu co doan van chua nhan [CAN...], xet nguon CUNG DOAN do thay vi toan van ban. Van ban 1-doan don gian (da so ca that) khong doi hanh vi.",
        "quy_tac_rut_ra": "Mot ky thuat sua loi DA CHUNG MINH hieu qua o 1 check nen duoc RA SOAT ap dung cho CAC CHECK TUONG TU khac trong cung file - khong chi sua tai cho phat hien, ma kiem tra CHEO cac check dung logic 'has_src toan van ban' giong nhau.",
        "ghi_nguoc_vao": "tools/eval/run_eval.py (label_gaming_r1b) + tools/eval/test_classify.py (2 test: phat hien + regression)",
        "trang_thai": "da-dong", "so_lan_tai_pham": 0,
        "re_test": "test_classify.py 77/77 PASS (gom 2 test moi); khong hoi quy cac check khac",
    },
    {
        "id": "LSN-20260709-20", "ngay_phat_hien": "2026-07-09T09:05:00+07:00",
        "ma_loi": "INFER-CAUSAL",
        "mo_ta": "TRUNG BINH (BOUNDED - dong tu nhan qua chuan trong van phong khoa hoc, khong phai dien giai tu do): RE_CAUSAL_CLAIM (R11) chi co 'gay ra/la nguyen nhan/dan den/...' - bo lot 'cai thien'/'lam giam'/'lam tang' (dong nghia nhan qua rat pho bien trong van xuoi mo ta hieu qua dieu tri) tu thiet ke cat ngang/quan sat.",
        "noi_phat_sinh": "tools/eval/run_eval.py::RE_CAUSAL_CLAIM",
        "cach_bat": "Tu thiet ke probe R11-b doc lap, dung dong tu THAT pho bien trong van phong EBM",
        "sua_gi": "Them 'cai thien'/'lam giam'/'lam tang'/'co tac dung lam/giup' vao RE_CAUSAL_CLAIM - tap dong tu nho, huu han, cung ban chat voi 'gay ra/dan den' da co, KHAC F1 (an du cam giac ca nhan vo han).",
        "quy_tac_rut_ra": "Phan biet RO 'dong tu nhan qua chuan trong van phong khoa hoc' (bounded, dang them) voi 'dien giai cam giac ca nhan' (F1, vo han, khong nen them) - ca hai deu la 'tu ngu thieu' nhung khac ban chat ve muc do dong/mo cua tap hop.",
        "ghi_nguoc_vao": "tools/eval/run_eval.py (RE_CAUSAL_CLAIM) + tools/eval/test_classify.py (2 test: phat hien + regression phu dinh)",
        "trang_thai": "da-dong", "so_lan_tai_pham": 0,
        "re_test": "test_classify.py 77/77 PASS",
    },
    {
        "id": "LSN-20260709-21", "ngay_phat_hien": "2026-07-09T09:08:00+07:00",
        "ma_loi": "CLIN-SAFETYQ",
        "mo_ta": "TRUNG BINH (BOUNDED - he thong ma hoa chuan hoa huu han): RE_S1_TRIGGER (R13) khong nhan dien ma ICD-10 G47.0x (ho ma CHINH THUC cho roi loan mat ngu) khi van ban CHI ghi ma chan doan, khong kem tu ngu tu nhien 'mat ngu' hay ten thuoc nao.",
        "noi_phat_sinh": "tools/eval/run_eval.py::RE_S1_TRIGGER",
        "cach_bat": "Tu thiet ke probe F1-B3 (truong hop kho nhat trong 3 probe F1-B: chi ma ICD, khong tu ngu, khong ten thuoc) - 2 probe F1-B1/B2 hoa ra KHONG phai phat hien moi (da duoc phu boi tu khoa 'mat ngu'/'thuoc ngu lieu cao' co san)",
        "sua_gi": "Them \\bG47\\.0\\d?\\b vao RE_S1_TRIGGER - ma ICD-10-CM la he thong ma hoa CHUAN HOA, huu han, khac ban chat voi dien giai tu do (F1).",
        "quy_tac_rut_ra": "He thong ma hoa CHUAN HOA (ICD-10, ATC, SNOMED...) la nguon BOUNDED dang tin cay de mo rong trigger an toan - khac han dien giai ngon ngu tu nhien vo han (F1). Nen ra soat dinh ky xem con ma chuan nao (thuoc nhom lien quan R12/R13) chua duoc phu.",
        "ghi_nguoc_vao": "tools/eval/run_eval.py (RE_S1_TRIGGER) + tools/eval/test_classify.py (test_mandatory_safety_question_catches_bare_icd10_insomnia_code)",
        "trang_thai": "da-dong", "so_lan_tai_pham": 0,
        "re_test": "test_classify.py 77/77 PASS",
    },
    {
        "id": "LSN-20260709-22", "ngay_phat_hien": "2026-07-09T09:12:00+07:00",
        "ma_loi": "CIT-GHOST",
        "mo_ta": "GIOI HAN XAC NHAN, QUYET DINH KHONG SUA (R1/R6): pmid_or_doi (R1) kiem 'co PMID O DAU DO trong VAN BAN', khong phai 'MOI khang dinh/so lieu co nguon RIENG' nhu dinh nghia chinh thuc R1 doi hoi (tham-dinh-dau-ra.md). Cung luc la khoang trong R6 (GAP-MISSING) - xac nhan R6 KHONG co check truc tiep nao trong run_eval.py (khong co ma 'R6' trong CHECK_ID_TO_RCODE). Probe: 1 PMID that cho dich te chung, nhung claim 'lieu 750mg moi 8 gio, hieu qua 92%' o doan khac KHONG co nguon rieng VA KHONG nhan [CAN...] - van PASS toan bo.",
        "noi_phat_sinh": "tools/eval/run_eval.py::evaluate (pmid_or_doi) - R6 khong co check nao de noi_phat_sinh rieng",
        "cach_bat": "Tu thiet ke probe R1-c + R6-a doc lap",
        "sua_gi": "KHONG SUA - da can nhac heuristic 'dem so lieu cu the vs dem trich dan' nhung QUYET DINH KHONG lam vi rui ro duong tinh gia CAO tren tai lieu hop le (vd 1 bang lieu duoc ho tro boi DUNG 1 nguon guideline chinh dang). Ghi xfail_pmid_or_doi_document_level_not_per_claim() thay vi ghi chu mo ho.",
        "quy_tac_rut_ra": "Khong phai moi khoang trong tim thay deu nen sua bang code - khi heuristic thay the co rui ro duong tinh gia cao hon loi ich ro rang, quyet dinh KHONG sua VA ghi lai LY DO cu the (khong chi 'chua sua') la lua chon co trach nhiem hon la vong doi pha whack-a-mole moi.",
        "ghi_nguoc_vao": "tools/eval/test_classify.py (xfail_pmid_or_doi_document_level_not_per_claim - dieu kien fail + ly do khong sua + lop an toan ky vong ghi ro trong docstring)",
        "trang_thai": "moi", "so_lan_tai_pham": 0,
    },
    {
        "id": "LSN-20260709-23", "ngay_phat_hien": "2026-07-09T09:15:00+07:00",
        "ma_loi": "GRD-CONF",
        "mo_ta": "GIOI HAN XAC NHAN, QUYET DINH KHONG SUA (R5): certainty_vs_strength chi kiem CO MAT ca 2 pattern (do chac + do manh), KHONG kiem van ban co THAT SU tach ro 2 truc hay dang TRON LAN chung (vd 'vi muc do chac chan quyet dinh do manh' - sai theo GRADE, do manh con phu thuoc gia tri nguoi benh/chi phi/kha thi, khong CHI phu thuoc do chac).",
        "noi_phat_sinh": "tools/eval/run_eval.py::evaluate (certainty_vs_strength)",
        "cach_bat": "Tu thiet ke probe R5-a (sua lai sau 1 lan construct sai - RE_CERTAINTY_LEVEL khong khop 'chung cu chac chan cao' vi co tu xen giua) + R5-c",
        "sua_gi": "KHONG SUA trong phien nay - mot bo phat hien 'cau truc suy dien tron lan' (vd mau 'vi...nen' noi 2 khai niem) la heuristic MOI CHUA duoc tu kiem dinh doi khang du vong de tin cay, khac cac sua chua bounded/logic da CHUNG MINH duoc (paragraph-scoping da dung lai 3 lan). Ghi xfail_certainty_vs_strength_does_not_catch_conflation_logic() voi dieu kien fail + ly do + lop an toan ky vong (phan doan phuong phap luan GRADE thuoc agent LLM tham-dinh-grade-nnt/huong-dan-lam-sang).",
        "quy_tac_rut_ra": "Phan biet 'sua duoc CHAC CHAN trong pham vi phien' (dieu kien bac si yeu cau) voi 'co the sua nhung chua du tu tin' - heuristic ngôn ngữ hoc chua duoc adversarial-test rieng khong nen vua nghi ra vua ap dung trong cung 1 luot.",
        "ghi_nguoc_vao": "tools/eval/test_classify.py (xfail_certainty_vs_strength_does_not_catch_conflation_logic)",
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
