#!/usr/bin/env python3
"""backfill_20260709_round3_adversarial.py — Ghi vao LEDGER_LESSONS.jsonl VONG 3 kiem dinh
doi khang doc lap (bac si yeu cau vong moi, gia dinh he VAN CON khe ho) - 16 probe: S1 sau
hon, RE_REDFLAG/RE_ANTIBIOTIC qua trieu chung/thuoc khong trong danh sach, EtD mau thuan tu
than (context-classification, khong phai tu khoa), PII (3 loai that + 2 xac nhan gioi han),
R1-R7 rong hon, E2 outcome-transition (sua mot phan + xfail phan con lai). Idempotent.
"""
from __future__ import annotations
import json
from pathlib import Path

LEDGER = Path(__file__).resolve().parents[2] / "LEDGER_LESSONS.jsonl"

ENTRIES = [
    {
        "id": "LSN-20260709-13", "ngay_phat_hien": "2026-07-09T08:00:00+07:00",
        "ma_loi": "SEC-BYPASS",
        "mo_ta": "NGHIEM TRONG (context-classification, khong phai tu khoa) - phat hien phu qua probe F5/F6: R3 gate_respected (RE_GATE_VIOLATION) chi bat tuyen bo THI QUA KHU 'DA ap dung cho benh nhan' - KHONG bat duoc TU MAU THUAN: van ban tu nhan 'khong ap dung cho benh nhan cu the' (disclaimer dung de duoc mien red_flags/mandatory_safety_question) NHUNG NOI DUNG CUNG co chi dan ca the hoa TRUC TIEP (xung ho 2 ngoi 'Anh/Chi nen...' HOAC hen tai kham cu the + lieu cu the). Day la LO HONG THUC SU o chinh co che mien tru da xay dung 2 vong truoc, khong phai thieu 1 tu khoa don le.",
        "noi_phat_sinh": "tools/eval/run_eval.py::RE_GATE_VIOLATION + _is_evidence_positioning (thieu lop phat hien mau thuan)",
        "cach_bat": "Tu thiet ke probe F5 (xung ho truc tiep) + F6 (ke hoach dieu tri cu the) doc lap, uu tien tim loi TRUOC khi ket luan tot hon",
        "sua_gi": "Them ham _has_disclaimer_directive_contradiction() (context-classification MOI, khong phai them keyword): dieu kien la disclaimer 'khong ap dung...' CUNG co xung-ho-2-ngoi-chi-dan HOAC hen-tai-kham-cu-the. Wire vao CA gate_respected (bao loi R3 ro rang) VA _is_evidence_positioning (khong mien red_flags/safety_question cho van ban mau thuan).",
        "quy_tac_rut_ra": "Khi mot co che MIEN TRU dua tren disclaimer tu-nhan, luon phai kiem tra dong thoi 'noi dung co THAT SU khop voi disclaimer khong' - mot disclaimer dung de 'qua cong' ma noi dung mau thuan voi no la mot LOAI LOI RIENG (tu-mau-thuan), khac voi 'thieu tu khoa don le' - can ham phat hien MAU THUAN rieng, khong chi mo rong danh sach tu khoa.",
        "ghi_nguoc_vao": "tools/eval/run_eval.py (_has_disclaimer_directive_contradiction, wire vao gate_respected + _is_evidence_positioning) + tools/eval/test_classify.py (2 test F5/F6)",
        "trang_thai": "da-dong", "so_lan_tai_pham": 0,
        "re_test": "test_classify.py 68/68 PASS (gom 2 test khoa dung F5/F6); CL-A8 that khong hoi quy (van duoc mien dung, khong co mau thuan trong noi dung that)",
    },
    {
        "id": "LSN-20260709-14", "ngay_phat_hien": "2026-07-09T08:05:00+07:00",
        "ma_loi": "SEC-PII",
        "mo_ta": "CAO: scan_pii bo lot 3 dang PII THAT PHO BIEN: (P1) ten benh nhan qua dai tu xung ho ton trong ('Chi Nguyen Thi Lan') KHONG co tien to 'benh nhan'/'BN'; (P2) ngay sinh qua cach dien dat 'ra doi ngay' (it gap hon P1, nhung re de them); (P3) ma dinh danh dang 'Ma BN: ...' khac cum 'so ho so benh an' ma SO_HO_SO dang doi.",
        "noi_phat_sinh": "tools/eval/run_eval.py::_RE_HOTEN, PII list (DOB, SO_HO_SO)",
        "cach_bat": "Tu thiet ke 3 probe PII doc lap (P1/P2/P3) theo dung yeu cau bac si kiem PII rong hon",
        "sua_gi": "(P1) _RE_HOTEN them dai tu 'anh/chi/ong/ba' TRUOC ten, kem RAO CHONG duong tinh gia moi: mo rong _HOTEN_STOP voi tu chuc danh (bac/si/duoc/dieu/duong/giao/su...) de 'Anh Bac Si Nguyen' KHONG bi coi la ten nguoi - da tu kiem dinh doi khang chinh sua chua nay truoc khi ghi nhan xong. (P2) DOB them 'ra doi' + cho phep tu 'ngay' xen giua tu khoa va ngay thang. (P3) PII list them MA_BN rieng (an toan hon SO_HO_SO vi chu 'BN' nam ngay trong viet tat, khong mo ho voi ho so hanh chinh-nghien cuu).",
        "quy_tac_rut_ra": "Moi lan MO RONG mot pattern nhan dang (ten/ma so) PHAI tu kiem tra CHEO nguy co duong tinh gia MOI (vd dai tu xung ho + tu chuc danh) TRUOC khi coi la xong - khong chi kiem huong bo lot.",
        "ghi_nguoc_vao": "tools/eval/run_eval.py (_RE_HOTEN, _HOTEN_STOP, DOB, PII list MA_BN) + tools/eval/test_classify.py (5 test: 3 phat hien That + 1 rao chong FP + 1 regression SO_HO_SO)",
        "trang_thai": "da-dong", "so_lan_tai_pham": 0,
        "re_test": "test_classify.py 68/68 PASS; regression xac nhan 'so ho so de tai' (hanh chinh-nghien cuu) van KHONG bi flag sai",
    },
    {
        "id": "LSN-20260709-15", "ngay_phat_hien": "2026-07-09T08:10:00+07:00",
        "ma_loi": "CLIN-REDFLAG",
        "mo_ta": "TRUNG BINH: RE_REDFLAG bo lot thuat ngu cap cuu dot quy/NMCT CHUAN HOA 'gio vang'/'tieu soi huyet' (khac voi dien giai tu do vo han - day la thuat ngu Y KHOA CO DINH, bounded).",
        "noi_phat_sinh": "tools/eval/run_eval.py::RE_REDFLAG",
        "cach_bat": "Tu thiet ke probe F2 (trieu chung FAST dot quy + 'gio vang', khong dung tu cap cuu/chuyen tuyen/115)",
        "sua_gi": "Them 'gio vang'/'tieu soi huyet' vao RE_REDFLAG - CUNG tien le nhu 'goi 115'/'dua di vien' da them vong 2 (thuat ngu Y KHOA CO DINH, KHONG phai dien giai ca nhan nhu 'dem cuu' cua F1).",
        "quy_tac_rut_ra": "Phan biet RO 2 loai mo rong tu vung: (a) THUAT NGU Y KHOA CHUAN HOA (bounded, dang them duoc, vd 'gio vang'/'115') vs (b) DIEN GIAI TU NHIEN VO HAN (khong bounded, khong nen duoi theo tung cai, vd an du mat ngu cua F1) - chi (a) dang gia tri de them, (b) nen ghi nhan la gioi han co huu.",
        "ghi_nguoc_vao": "tools/eval/run_eval.py (RE_REDFLAG) + tools/eval/test_classify.py (test_red_flags_recognizes_gio_vang_stroke_urgency)",
        "trang_thai": "da-dong", "so_lan_tai_pham": 0,
        "re_test": "test_classify.py 68/68 PASS",
    },
    {
        "id": "LSN-20260709-16", "ngay_phat_hien": "2026-07-09T08:12:00+07:00",
        "ma_loi": "DRG-ABX",
        "mo_ta": "TRUNG BINH: RE_ANTIBIOTIC bo lot (F3) khang sinh THE HE MOI/nang hon (carbapenem: meropenem...) va (F4) chu vi khai niem BOUNDED ('thuoc diet khuan'/'khang khuan'/'chong nhiem khuan' - KHONG ten thuoc cu the, KHONG chu 'khang sinh').",
        "noi_phat_sinh": "tools/eval/run_eval.py::RE_ANTIBIOTIC",
        "cach_bat": "Tu thiet ke probe F3+F4 doc lap, dung ten thuoc THAT (meropenem/linezolid) + chu vi THAT pho bien",
        "sua_gi": "Them 8 ten thuoc nhom carbapenem/oxazolidinon/glycopeptide/fluoroquinolon moi + 3 chu vi khai niem (diet khuan/khang khuan/chong nhiem khuan) - danh sach nho, huu han, cung ban chat voi tien le RE_S2_TRIGGER/RE_ANTIBIOTIC brand-name da lam vong 2.",
        "quy_tac_rut_ra": "Danh sach ten thuoc PHAI ra soat dinh ky theo THE HE/nhom thuoc moi ra doi (khong chi ten cu) - day la loai gap se TAI DIEN theo thoi gian khi thuoc moi duoc dua vao thi truong, khac ban chat voi F1 (dien giai tu do).",
        "ghi_nguoc_vao": "tools/eval/run_eval.py (RE_ANTIBIOTIC) + tools/eval/test_classify.py (2 test: meropenem + chu vi)",
        "trang_thai": "da-dong", "so_lan_tai_pham": 0,
        "re_test": "test_classify.py 68/68 PASS",
    },
    {
        "id": "LSN-20260709-17", "ngay_phat_hien": "2026-07-09T08:15:00+07:00",
        "ma_loi": "SEC-BYPASS",
        "mo_ta": "TRUNG BINH: RE_GATE_VIOLATION (R3) chi chap nhan dong tu 'da ap dung' - 'da trien khai phac do nay cho benh nhan' (dong nghia tu nhien, co tan ngu xen giua) ne duoc.",
        "noi_phat_sinh": "tools/eval/run_eval.py::RE_GATE_VIOLATION",
        "cach_bat": "Tu thiet ke probe R3a doc lap",
        "sua_gi": "Gop nhom dong tu dong nghia (ap dung/trien khai/thuc hien) + cho phep toi da ~20 ky tu xen giua dong tu va 'cho benh nhan' (thuong co tan ngu nhu 'phac do nay').",
        "quy_tac_rut_ra": "Pattern kiem tra 'tuyen bo da lam X cho ai do' nen du tinh TAN NGU xen giua dong tu va doi tuong tu dau, khong doi cum co dinh lien mach.",
        "ghi_nguoc_vao": "tools/eval/run_eval.py (RE_GATE_VIOLATION) + tools/eval/test_classify.py (test_gate_respected_catches_da_trien_khai_paraphrase)",
        "trang_thai": "da-dong", "so_lan_tai_pham": 0,
        "re_test": "test_classify.py 68/68 PASS",
    },
    {
        "id": "LSN-20260709-18", "ngay_phat_hien": "2026-07-09T08:20:00+07:00",
        "ma_loi": "STAT-MISMATCH",
        "mo_ta": "Dong MOT PHAN LSN-20260709-12 (E2, ghi 'gioi han khong sua' vong 2): effect_size_ci_required co the coi CI cua MOT KET CUC KHAC la 'du' cho p-value cua ket cuc DANG XET. Vong 3 SUA DUOC phan co MOC CHUYEN KET CUC tuong minh (ket cuc phu/ket cuc khac/tac dung phu/bien co khac/ngoai ra) - neu mot trong cac moc nay xuat hien GIUA p-value goc va CI ung vien, KHONG cho CI do 'che' p-value goc nua. CON LAI (ghi xfail rieng, khong con la 'ghi chu mo ho'): chuyen kET CUC NGAM (khong dung moc tu tuong minh nao) VAN chua giai duoc - can NLP that de lien ket outcome<->effect-size chac chan, ngoai pham vi harness regex.",
        "noi_phat_sinh": "tools/eval/run_eval.py::evaluate (effect_size_ci_required)",
        "cach_bat": "Tu thiet ke E2b (bien the 'ket cuc phu') + tai xac nhan E2 goc (vong 2, 've tac dung phu') deu duoc sua bang CUNG mot co che; rieng bien the 'chuyen ngam' van con gap, chuyen thanh xfail_ ro rang thay vi ghi chu",
        "sua_gi": "Them _RE_OUTCOME_TRANSITION (kết cục phụ/kết cục khác/về tác dụng phụ/biến cố khác/ngoài ra) + ap dung NHAT QUAN cho CA cua so hep (+-240 ky tu) LAN cua so mo rong theo doan van (truoc day chi ap dung cho cua so mo rong, cua so hep short-circuit truoc khi toi luot outcome-transition - da sua ca 2 nhat quan). the ham xfail_effect_size_ci_required_still_wrong_on_implicit_outcome_switch() trong test_classify.py (quy uoc xfail_ tu-cai vi moi truong khong co pytest) - test PHAI raise AssertionError voi dieu kien fail ro rang, _run_all() bao XFAIL (da biet) rieng biet, KHONG tinh la FAIL cua suite, va bao XPASS canh bao NEU tu nhien het fail (can nguoi ra lai, khong am tham coi la tot hon).",
        "quy_tac_rut_ra": "'Gioi han khong sua' ghi vong truoc KHONG co nghia 'khong the sua gi them' - quay lai voi gia dinh 'he thong van con sai' co the tim ra MOT PHAN giai duoc bang heuristic bounded (moc chuyen doi tuong tuong minh), du KHONG giai duoc TOAN BO (chuyen ngam). Phan CON LAI phai duoc GHI RO bang co che xfail (dieu kien fail cu the, kiem tra duoc) thay vi cau 'can NLP that' mo ho - de phien sau/bac si biet CHINH XAC khi nao coi la da sua xong.",
        "ghi_nguoc_vao": "tools/eval/run_eval.py (_RE_OUTCOME_TRANSITION, ap dung ca 2 cua so) + tools/eval/test_classify.py (3 test thuong + 1 xfail_ + quy uoc xfail moi trong _run_all())",
        "trang_thai": "da-dong", "so_lan_tai_pham": 0,
        "re_test": "test_classify.py 68/68 test PASS + 1/1 xfail dung nhu ky vong; RS-SMOKE + ca goc round-1 (bang so sanh phuong phap CUNG ket cuc) khong hoi quy",
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
