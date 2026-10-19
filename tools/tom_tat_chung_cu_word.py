#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tóm tắt chứng cứ CHI TIẾT bằng tiếng Việt cho từng trích dẫn có toàn văn PDF trong EndNote → Word Times New Roman.

VÌ SAO CÓ (19/10/2026, bác sĩ yêu cầu): «với mỗi trích dẫn có toàn văn với file pdf hãy bổ sung một file Word tóm tắt chi
tiết bằng tiếng Việt, font Times New Roman, theo cấu trúc chuẩn tóm tắt chứng cứ y khoa cho thực hành lâm sàng… tôi sẽ dựa
vào đó áp dụng cho thực hành». Bác sĩ DỰA VÀO bản này ⇒ máy không được để lọt một con số không có trong bài.

DÂY CHUYỀN (mỗi trích dẫn):
  1. `chuan-bi <mã>` — tách văn bản PDF trong EndNote theo TRANG, đối chiếu định danh (DOI/tiêu đề có trong PDF), tra RÚT BÀI
     bằng chuỗi 3 tầng THẬT (không trả lời bằng trí nhớ), gom ngữ cảnh dashboard (mục nào dùng bài, decision, gradeLevel). Gói
     đọc ở `~/.ebm-cache/tom-tat-chung-cu/<khoá>/` (ngoài OneDrive — chứa toàn văn, không phân phối).
  2. Một phiên/agent Claude ĐỌC TOÀN VĂN theo `HUONG_DAN_DOC` (in kèm gói) và viết `tom_tat.json` đúng khuôn `MAU`.
  3. `dung <mã>` — CỔNG kiểm (fail-closed) rồi dựng Word:
       · mọi con số ở bảng kết quả/tác hại phải có NGUYÊN VĂN trên trang khai (±1 trang); số do máy tự tính (ARR, NNT) phải
         khai `may_tinh` và in dấu † — không lẫn với số của bài;
       · mọi trích dẫn nguyên văn ≤ 15 từ và tìm thấy trên trang khai;
       · công cụ nguy cơ sai lệch ĐÚNG thiết kế (RoB 2 chỉ cho RCT; ROBINS cho quan sát; AMSTAR-2 cho tổng quan; QUADAS cho
         chẩn đoán; AGREE II cho guideline);
       · GRADE luôn in là ĐỀ XUẤT CỦA MÁY — không bao giờ thay phân hạng của dashboard/bác sĩ;
       · bài đã RÚT ⇒ chặn (mã 3); định danh PDF không khớp ⇒ chặn (mã 3).
     Word lưu cạnh thư viện EndNote: `<thư mục thư viện>/TomTatChungCu/<khoá>_TomTatChungCu.docx` (đi theo OneDrive);
     JSON nguồn đã qua cổng lưu ở `TomTatChungCu/_nguon/`.
  4. `dung <mã> --gan-endnote --ap-dung` — THÊM tệp Word vào trường «File Attachments» của bản ghi (giữ nguyên PDF cũ; đọc lại
     phải còn đủ tệp cũ, thiếu ⇒ ghi trả lại ngay và báo lỗi). Đo 19/10 trên BẢN SAO thư viện: EndNote nhận Word làm tệp LIÊN
     KẾT (đường dẫn tuyệt đối, `file_type` 2) — mở được trên máy Mac này; máy khác cần mở tệp trong thư mục OneDrive.
     Mọi lần ghi đi qua khoá ghi `khoa_ghi_endnote.py` (chờ khi bác sĩ đang thao tác EndNote). Gán `internal-pdf://` qua
     AppleScript KHÔNG được (EndNote trả «missing value») — đừng thử lại trên thư viện thật.

KHÔNG làm: không đổi `decision`/`gradeLevel` của dashboard, không sinh lời dặn bệnh nhân, không chép đoạn văn của bài (chỉ dữ
kiện + trích ≤ 15 từ), không mở/đọc nội dung DynaMed/Scopus/WoS. Mục «Gợi ý áp dụng» là GỢI Ý — áp dụng cho bệnh nhân là
Cổng A của bác sĩ.

Lệnh:
  python3 tools/tom_tat_chung_cu_word.py liet-ke [--tang 1|2|3|4] [--chua-lam] [--json]
  python3 tools/tom_tat_chung_cu_word.py mau                       # khuôn JSON + hướng dẫn đọc
  python3 tools/tom_tat_chung_cu_word.py chuan-bi <PMID|REC-n>
  python3 tools/tom_tat_chung_cu_word.py kiem <PMID|REC-n>        # chỉ chạy cổng
  python3 tools/tom_tat_chung_cu_word.py dung <PMID|REC-n> [--gan-endnote] [--ap-dung]
  python3 tools/tom_tat_chung_cu_word.py tien-do
Mã thoát: 0 đạt · 1 cổng có lỗi (sửa JSON) · 2 không đo được (thiếu thư viện/PDF/gói) · 3 CHẶN an toàn (rút bài/định danh).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import re
import sys
import unicodedata
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
CACHE = Path.home() / ".ebm-cache" / "tom-tat-chung-cu"
TEN_THU_MUC_RA = "TomTatChungCu"
PHIEN_BAN_KHUON = 1
TOI_DA_TU_TRICH = 15
LOAI_THIET_KE = ("rct", "sr_ma", "cohort", "case_control", "cross_sectional", "diagnostic", "guideline", "nhan_thuoc", "khac")
TEN_THIET_KE = {"rct": "Thử nghiệm lâm sàng ngẫu nhiên có đối chứng", "sr_ma": "Tổng quan hệ thống / phân tích gộp",
                "cohort": "Nghiên cứu thuần tập", "case_control": "Nghiên cứu bệnh–chứng", "cross_sectional": "Nghiên cứu cắt ngang",
                "diagnostic": "Nghiên cứu độ chính xác chẩn đoán", "guideline": "Hướng dẫn thực hành lâm sàng (guideline)",
                "nhan_thuoc": "Nhãn thuốc / thông tin kê đơn", "khac": "Thiết kế khác"}
# Công cụ nguy cơ sai lệch HỢP LỆ theo thiết kế (CLAUDE.md §6.3: RoB 2 chỉ cho RCT). So khớp không phân biệt hoa/thường,
# bỏ khoảng trắng/gạch — «ROBINS-I V2» khớp «robinsi».
CONG_CU_HOP_LE = {
    "rct": ("rob2",),
    "sr_ma": ("amstar2", "robis"),
    "cohort": ("robinsi", "robinse", "newcastleottawa", "nos"),
    "case_control": ("robinse", "robinsi", "newcastleottawa", "nos"),
    "cross_sectional": ("robinse", "jbi", "axis", "newcastleottawa"),
    "diagnostic": ("quadas2", "quadas3", "quadasc"),
    "guideline": ("agreeii", "agree2"),
    "nhan_thuoc": ("khongapdung",),
    "khac": (),
}
MUC_GRADE = ("cao", "trung bình", "thấp", "rất thấp", "không áp dụng")
TRUONG_SO = ("nhom_can_thiep", "nhom_so_sanh", "hieu_ung", "ktc95", "p", "tuyet_doi", "nnt")
MIEN_TRU = "Bản tóm tắt do MÁY (Claude) soạn từ toàn văn — CẦN BÁC SĨ KIỂM CHỨNG trước khi áp dụng cho người bệnh."

MAU = {
    "phien_ban_khuon": PHIEN_BAN_KHUON,
    "khoa": "PMID-10471456",
    "pmid": "10471456",
    "doi": "10.1056/NEJM199909023411001",
    "loai_thiet_ke": "rct",
    "thiet_ke_mo_ta": "Thử nghiệm ngẫu nhiên, mù đôi, đa trung tâm, đối chứng giả dược",
    "linh_vuc": "Tim mạch — suy tim",
    "cau_hoi_lam_sang": {"loai": "điều trị", "P": "…", "I": "…", "C": "…", "O": "…"},
    "ket_luan_thuc_hanh": ["Mỗi gạch một kết luận thực hành, giữ mệnh đề điều kiện của bài (quần thể, ngưỡng, chống chỉ định)."],
    "boi_canh": {"dia_diem": "…", "thoi_gian": "…", "dang_ky": "NCT… hoặc «không khai»", "tai_tro": "…",
                 "xung_dot_loi_ich": "…"},
    "doi_tuong": {"tieu_chuan_chon": ["…"], "tieu_chuan_loai": ["…"], "co_mau": "…", "dac_diem_nen": "…"},
    "can_thiep_so_sanh": {"can_thiep": "thuốc · liều · đường dùng · thời gian", "so_sanh": "…", "dong_tri_lieu": "…"},
    "ket_cuc": {"chinh": "…", "phu": ["…"], "theo_doi": "…"},
    "phan_tich": "ITT/PP, mô hình, xử lý dữ liệu thiếu, dừng sớm…",
    "ket_qua": [{"ket_cuc": "Tử vong mọi nguyên nhân", "chinh": True, "nhom_can_thiep": "284/822 (35%)",
                 "nhom_so_sanh": "386/841 (46%)", "hieu_ung": "RR 0.70", "ktc95": "0.60–0.82", "p": "<0.001",
                 "tuyet_doi": "ARR 11%", "nnt": "9", "may_tinh": ["tuyet_doi", "nnt"], "trang": 3}],
    "tac_hai": [{"ket_cuc": "Vú to/đau vú ở nam", "chinh": False, "nhom_can_thiep": "10%", "nhom_so_sanh": "1%",
                 "hieu_ung": "", "ktc95": "", "p": "<0.001", "tuyet_doi": "", "nnt": "", "may_tinh": [], "trang": 4}],
    "tac_hai_ghi_chu": "Ghi khi bài không báo cáo tác hại có cấu trúc.",
    "phan_nhom": ["Phân nhóm (kèm kiểm định tương tác nếu bài báo cáo)."],
    "khuyen_cao": [],
    "nguy_co_sai_lech": {"cong_cu": "RoB 2", "mien": [{"ten": "Quy trình ngẫu nhiên hoá", "danh_gia": "thấp",
                                                         "ly_do": "…", "trang": 2}], "tong_the": "nguy cơ thấp"},
    "grade_de_xuat": [{"ket_cuc": "Tử vong mọi nguyên nhân", "muc": "cao", "ly_do": "lý do hạ/nâng từng miền GRADE"}],
    "kha_nang_ap_dung": {"tuong_dong": "…", "khac_biet": "…", "trien_khai_viet_nam": "thuốc sẵn có, BHYT, xét nghiệm theo dõi…"},
    "goi_y_ap_dung": {"nen_lam": ["…"], "khong_nen": ["…"], "dieu_kien": ["…"], "theo_doi": ["…"]},
    "diem_manh": ["…"],
    "han_che": ["…"],
    "doi_chieu_dashboard": "Bài là nguồn chính của mục … (decision …); bản tóm tắt khớp/lệch ở điểm …",
    "trich_nguyen_van": [{"cau": "tối đa 15 từ, chép đúng chữ trong PDF", "trang": 3}],
    "cau_hoi_mo": ["…"],
    "nguoi_soan": "Claude (máy) — đề xuất, chưa qua bác sĩ",
}
# Khoá bắt buộc theo thiết kế (guideline/nhãn thuốc không có nhóm can thiệp–so sánh theo nghĩa thử nghiệm).
_BAT_BUOC_CHUNG = ("khoa", "loai_thiet_ke", "thiet_ke_mo_ta", "cau_hoi_lam_sang", "ket_luan_thuc_hanh", "boi_canh",
                   "nguy_co_sai_lech", "grade_de_xuat", "kha_nang_ap_dung", "goi_y_ap_dung", "diem_manh", "han_che",
                   "doi_chieu_dashboard", "trich_nguyen_van")
_BAT_BUOC_NGHIEN_CUU = ("doi_tuong", "ket_cuc", "phan_tich", "ket_qua")
_BAT_BUOC_THEO_THIET_KE = {
    "rct": _BAT_BUOC_NGHIEN_CUU + ("can_thiep_so_sanh",),
    "sr_ma": _BAT_BUOC_NGHIEN_CUU + ("can_thiep_so_sanh",),
    "cohort": _BAT_BUOC_NGHIEN_CUU,
    "case_control": _BAT_BUOC_NGHIEN_CUU,
    "cross_sectional": _BAT_BUOC_NGHIEN_CUU,
    "diagnostic": _BAT_BUOC_NGHIEN_CUU,
    "guideline": ("khuyen_cao",),
    "nhan_thuoc": ("khuyen_cao",),
    "khac": ("ket_qua",),
}

HUONG_DAN_DOC = """# Hướng dẫn ĐỌC TOÀN VĂN và viết `tom_tat.json` — khuôn phiên bản {pb}

Bác sĩ sẽ DỰA VÀO bản này để thực hành. Đọc HẾT văn bản trong `van_ban.txt` (mỗi trang mở đầu bằng `=== TRANG n ===`);
guideline dài: đọc phần phương pháp + MỌI khuyến cáo liên quan câu hỏi của dashboard trong `ngu_canh.json`.

Luật (cổng `dung` kiểm máy — sai là KHÔNG ra Word):
1. MỌI con số trong `ket_qua` và `tac_hai` (các trường `nhom_can_thiep`, `nhom_so_sanh`, `hieu_ung`, `ktc95`, `p`, `tuyet_doi`,
   `nnt`) phải chép ĐÚNG như trong bài, và có trên trang `trang` (±1). Dấu thập phân giữ như bài (0.70 / 0·70 đều được).
   Số do bạn TỰ TÍNH (ARR, NNT, NNH…) ⇒ ghi tên trường vào `may_tinh` (Word in dấu †) và ghi cách tính ở `phan_tich`.
   Bài không báo cáo ⇒ để chuỗi rỗng, KHÔNG suy đoán.
2. `trich_nguyen_van`: tối đa {tu} từ mỗi câu, chép đúng chữ trên trang khai. Không chép đoạn văn dài (bản quyền).
3. `nguy_co_sai_lech.cong_cu` đúng thiết kế: RCT → «RoB 2»; tổng quan/gộp → «AMSTAR-2» (hoặc ROBIS); thuần tập/bệnh–chứng →
   «ROBINS-I» / «ROBINS-E» (hoặc Newcastle-Ottawa); chẩn đoán → «QUADAS-2»/«QUADAS-3»; guideline → «AGREE II» (ghi rõ Miền 3
   Rigour nếu guideline không mô tả); nhãn thuốc → «Không áp dụng». Mỗi miền: `danh_gia` + `ly_do` + `trang`.
4. `grade_de_xuat`: mức ∈ {{cao, trung bình, thấp, rất thấp, không áp dụng}} cho TỪNG kết cục chính, lý do theo 5 miền hạ
   (nguy cơ sai lệch · không nhất quán · gián tiếp · không chính xác · sai lệch xuất bản) và miền nâng. Đây là ĐỀ XUẤT — Word in
   rõ như vậy; guideline thì ghi phân hạng NGUYÊN BẢN của guideline trong `khuyen_cao`, không tự gán.
5. `ket_luan_thuc_hanh` (2–8 gạch) và `goi_y_ap_dung`: giữ mệnh đề điều kiện của bài (quần thể, ngưỡng, chống chỉ định,
   «ngoài thai kỳ»…); số liệu gắn đúng kết cục nó đo; không khẳng định vượt bài. Không viết lời dặn bệnh nhân, không bịa liều —
   liều chỉ chép từ bài kèm trang.
6. `kha_nang_ap_dung.trien_khai_viet_nam`: sẵn có thuốc/xét nghiệm, BHYT, khác biệt quần thể — điều chưa chắc ghi «[CẦN XÁC
   NHẬN]», không đoán.
7. `doi_chieu_dashboard`: đọc `ngu_canh.json` — bài là nguồn chính hay tham khảo của mục nào, decision/gradeLevel hiện tại;
   nói rõ bản tóm tắt KHỚP hay LỆCH ở điểm nào (chỉ đặt cạnh, không đổi decision).
8. guideline/nhãn thuốc: điền `khuyen_cao` (mỗi khuyến cáo liên quan: nội dung tiếng Việt, `luc_khuyen_cao`, `muc_chung_cu`
   NGUYÊN BẢN, `trang`, `lien_quan_dashboard`); `ket_qua` để [].
9. Không PII. Không thông tin ngoài bài trừ khi ghi nguồn (PMID/DOI) ngay trong câu.
10. Viết tiếng Việt chuẩn y khoa, thuật ngữ chưa có tương đương thì tiếng Việt kèm tiếng Anh trong ngoặc lần đầu.

Khuôn JSON (thay «…» bằng nội dung thật; giữ đủ khoá):
"""


# ───────────────────────── tiện ích chung ─────────────────────────

def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, Path(__file__).resolve().parent / tep)
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod


_MOD: dict = {}


def mod(ten: str):
    tep = {"sk": "endnote_suc_khoe.py", "nec": "nap_endnote_chu_de.py", "tt": "tom_tat_endnote_vi.py",
           "sx": "so_xac_minh_nguon.py", "md": "md_sang_docx_times.py"}[ten]
    if ten not in _MOD:
        _MOD[ten] = _nap(f"_ttcc_{ten}", tep)
    return _MOD[ten]


def khoa_cua(pmid: str | None, rec: int) -> str:
    return f"PMID-{pmid}" if pmid and re.fullmatch(r"\d{1,9}", str(pmid)) else f"REC-{rec}"


def thu_muc_ra(thu_vien: Path) -> Path:
    return thu_vien.parent / TEN_THU_MUC_RA


def tep_word(thu_vien: Path, khoa: str) -> Path:
    return thu_muc_ra(thu_vien) / f"{khoa}_TomTatChungCu.docx"


def _chuan_chu(s: str) -> str:
    """Chuẩn hoá để so khớp chữ trong PDF: NFKC, bỏ gạch nối cuối dòng, gộp khoảng trắng, chữ thường, thống nhất nháy/gạch."""
    s = unicodedata.normalize("NFKC", s or "")
    s = s.replace("­", "")
    s = re.sub(r"-\s*\n\s*", "", s)
    s = s.translate(str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-",
                                   "−": "-", "·": ".", "⋅": "."}))
    return re.sub(r"\s+", " ", s).strip().lower()


def _chuan_so(s: str) -> str:
    """Chuẩn hoá cách viết số hai phía như nhau: «0·70»→0.70; phân cách nghìn «10 000»/«10,000»→10000; phẩy thập phân → chấm."""
    s = unicodedata.normalize("NFKC", s or "")
    s = re.sub(r"(?<=\d)[·⋅](?=\d)", ".", s)
    s = re.sub(r"(?<=\d)[,    ](?=\d{3}(?!\d))", "", s)
    return re.sub(r"(?<=\d),(?=\d)", ".", s)


_SO = re.compile(r"\d+(?:\.\d+)?")


def cac_so(s: str) -> list[str]:
    return _SO.findall(_chuan_so(s))


def _so_khop(so: str, tap: set[str]) -> bool:
    if so in tap:
        return True
    if "." in so:  # 0.6 ≡ 0.60 — chỉ nới cho số thập phân, số nguyên phải trùng nguyên văn
        try:
            f = float(so)
        except ValueError:
            return False
        return any("." in t and abs(float(t) - f) < 1e-12 for t in tap)
    return False


# ───────────────────────── văn bản PDF ─────────────────────────

def tach_trang(pdf: Path) -> list[str]:
    """Văn bản từng trang (pypdf). Trang không trích được ⇒ chuỗi rỗng (PDF ảnh)."""
    import logging  # noqa: PLC0415

    import pypdf  # noqa: PLC0415
    logging.getLogger("pypdf").setLevel(logging.ERROR)
    doc = pypdf.PdfReader(str(pdf))
    ra = []
    for tr in doc.pages:
        try:
            ra.append(tr.extract_text() or "")
        except Exception:  # noqa: BLE001 — một trang hỏng không làm hỏng cả bài
            ra.append("")
    return ra


def ghep_van_ban(trang: list[str]) -> str:
    return "\n".join(f"=== TRANG {i} ===\n{t}" for i, t in enumerate(trang, 1))


def doc_van_ban(goi: Path) -> list[str]:
    """Đọc lại `van_ban.txt` thành danh sách trang (trang 1 ở chỉ số 0)."""
    tho = (goi / "van_ban.txt").read_text(encoding="utf-8")
    phan = re.split(r"^=== TRANG (\d+) ===\n", tho, flags=re.M)
    trang: dict[int, str] = {}
    for i in range(1, len(phan) - 1, 2):
        trang[int(phan[i])] = phan[i + 1]
    return [trang.get(i, "") for i in range(1, max(trang, default=0) + 1)]


def khop_dinh_danh(trang: list[str], doi: str | None, tieu_de: str | None) -> tuple[bool, str]:
    """PDF có đúng là bài này không — DOI xuất hiện trong văn bản, hoặc ≥ 60% từ (≥ 4 chữ) của tiêu đề có ở 3 trang đầu."""
    dau = _chuan_chu(" ".join(trang[:3]))
    toan = _chuan_chu(" ".join(trang)).replace(" ", "")
    if doi and _chuan_chu(doi).replace(" ", "") in toan:
        return True, "DOI có trong PDF"
    tu = [w for w in re.findall(r"[a-z0-9]+", _chuan_chu(tieu_de or "")) if len(w) >= 4]
    if tu:
        ty_le = sum(w in dau for w in tu) / len(tu)
        if ty_le >= 0.6:
            return True, f"{ty_le:.0%} từ của tiêu đề có ở 3 trang đầu"
        return False, f"chỉ {ty_le:.0%} từ của tiêu đề có ở 3 trang đầu và không thấy DOI"
    return False, "bản ghi không có DOI/tiêu đề để đối chiếu"


# ───────────────────────── EndNote (chỉ đọc) ─────────────────────────

def ban_ghi_co_pdf(thu_vien: Path) -> list[dict]:
    """Mọi bản ghi NGOÀI thùng rác có ít nhất một tệp PDF — đọc `sdb.eni` chế độ chỉ-đọc."""
    sk = mod("sk")
    c = sk._ket_noi(thu_vien)
    try:
        cot = {r[1] for r in c.execute("pragma table_info(refs)")}
        tac_gia = "author" if "author" in cot else "''"
        tap_chi = "secondary_title" if "secondary_title" in cot else "''"
        hang = c.execute(
            f"select r.id, r.accession_number, r.electronic_resource_number, r.title, r.year, {tac_gia}, {tap_chi}, "
            "f.file_path from refs r join file_res f on f.refs_id = r.id where r.trash_state = 0 "
            "and lower(f.file_path) like '%.pdf' order by r.id, f.file_pos").fetchall()
    finally:
        c.close()
    ra: dict[int, dict] = {}
    pdf_goc = thu_vien.with_suffix(".Data") / "PDF"
    for rec, acc, erd, tieu_de, nam, tg, tc, fp in hang:
        pmid = acc if acc and re.fullmatch(r"\d{1,9}", str(acc).strip()) else None
        doi = mod("nec").chuan_doi(erd) if erd else None
        m = ra.setdefault(rec, {"rec": rec, "pmid": pmid, "doi": doi, "tieu_de": (tieu_de or "").strip(),
                                "nam": str(nam or ""), "tac_gia": (tg or "").split("\r")[0].strip(),
                                "tap_chi": (tc or "").strip(), "pdf": []})
        m["pdf"].append(str(pdf_goc / fp))
    for m in ra.values():
        m["khoa"] = khoa_cua(m["pmid"], m["rec"])
    return list(ra.values())


def tim_ban_ghi(thu_vien: Path, ma: str) -> dict | None:
    ma = ma.strip()
    so = re.sub(r"^(PMID[-:]?|REC[-:]?)", "", ma, flags=re.I)
    la_rec = bool(re.match(r"^REC", ma, flags=re.I))
    for m in ban_ghi_co_pdf(thu_vien):
        if (la_rec and str(m["rec"]) == so) or (not la_rec and m["pmid"] == so):
            return m
    return None


# ───────────────────────── ngữ cảnh dashboard + ưu tiên ─────────────────────────

def goc_du_lieu(ten: str) -> Path:
    """Gốc dữ liệu ngoài git (lồng rồi anh em) qua `ban_sao_tran.duong_goc` — cùng cách định vị với `so_toan_van.py`."""
    try:
        return _nap("_ttcc_bst", "ban_sao_tran.py").duong_goc(ten, GOC) or (GOC / ten)
    except Exception:  # noqa: BLE001 — thiếu bộ định vị ⇒ vị trí lồng
        return GOC / ten


def ngu_canh_dashboard() -> dict[str, dict]:
    files = sorted(goc_du_lieu("EBM-Dashboards").glob("WebDashboard_*.html"))
    if not files:
        return {}
    return mod("tt").ngu_canh(files, mod("nec")._nap_doc_data())


def _ngu_canh_cua(ds: dict[str, dict], pmid: str | None, doi: str | None) -> list[dict]:
    v = ds.get(f"pmid:{pmid}") if pmid else None
    if v is None and doi:
        v = ds.get(f"doi:{doi}") or next((x for x in ds.values() if x.get("doi") == doi), None)
    ra = []
    for nc in (v or {}).get("ngu_canh", []):
        it = nc.get("item") or {}
        ra.append({"dashboard": nc.get("dashboard"), "ngay": nc.get("ngay"), "chu_de": nc.get("chu_de"),
                   "muc": nc.get("muc"), "tieu_de_muc": nc.get("tieu_de"), "vai": nc.get("vai"),
                   "ban_cu": bool(nc.get("ban_cu")), "decision": it.get("decision"), "gradeLevel": it.get("gradeLevel"),
                   "gradeSource": it.get("gradeSource"), "design": it.get("design"), "population": it.get("population"),
                   "action": it.get("action"), "monitoring": it.get("monitoring"), "vn": it.get("vn"),
                   "tham_khao": nc.get("tham_khao")})
    return ra


def tang_uu_tien(ngu_canh: list[dict]) -> int:
    """1 = nguồn chính của mục apply · 2 = consider · 3 = notyet/khác · 4 = chỉ tham khảo hoặc không có dashboard."""
    moi = [x for x in ngu_canh if not x.get("ban_cu")] or ngu_canh
    dec = {str(x.get("decision") or "") for x in moi if x.get("vai") == "muc"}
    if "apply" in dec:
        return 1
    if "consider" in dec:
        return 2
    if any(x.get("vai") == "muc" for x in moi):
        return 3
    return 4


# ───────────────────────── rút bài ─────────────────────────

def kiem_rut_bai(pmid: str | None, doi: str | None) -> dict:
    """Tra bằng CÔNG CỤ (chuỗi 3 tầng của repo y khoa; DOI-only ⇒ nền Retraction Watch ngoại tuyến). Không tra được ⇒
    trạng thái «chua_kiem» — tuyệt đối không coi là «chưa bị rút»."""
    luc = dt.datetime.now().isoformat(timespec="seconds")
    try:
        sx = mod("sx")
        if pmid:
            kq = (sx.kiem_rut_bai([pmid]) or {}).get(pmid)
            if isinstance(kq, dict) and kq.get("status") in ("ok", "retracted"):
                return {"trang_thai": "da_rut" if kq["status"] == "retracted" else "khong_thay_rut",
                        "nguon": kq.get("source") or ",".join(kq.get("sources_tried") or []), "luc": luc}
        elif doi:
            kq = sx.rut_bai_retraction_watch_ngoai_tuyen_doi([doi])
            if kq is not None:
                return {"trang_thai": "da_rut" if kq else "khong_thay_rut_rw", "nguon": "retraction_watch (ngoại tuyến)",
                        "luc": luc}
    except Exception as e:  # noqa: BLE001 — mọi lỗi tra ⇒ KHÔNG BIẾT
        return {"trang_thai": "chua_kiem", "nguon": f"lỗi tra: {str(e)[:160]}", "luc": luc}
    return {"trang_thai": "chua_kiem", "nguon": "công cụ không trả kết luận", "luc": luc}


NHAN_RUT_BAI = {"khong_thay_rut": "Không thấy thông báo rút bài (chuỗi 3 tầng: Retraction Watch · PubMed · Europe PMC)",
                "khong_thay_rut_rw": "Không thấy trong Retraction Watch (chỉ tra ngoại tuyến theo DOI — bài không có PMID)",
                "da_rut": "ĐÃ BỊ RÚT — KHÔNG ĐƯỢC DÙNG",
                "chua_kiem": "CHƯA KIỂM ĐƯỢC RÚT BÀI — tra lại trước khi dùng"}


# ───────────────────────── chuẩn bị gói đọc ─────────────────────────

def chuan_bi(thu_vien: Path, ma: str, *, ngu_canh_tat_ca: dict | None = None, rut_bai=kiem_rut_bai) -> tuple[int, Path | None]:
    bg = tim_ban_ghi(thu_vien, ma)
    if bg is None:
        print(f"⚪ không thấy bản ghi có PDF cho «{ma}» trong thư viện {thu_vien.name}")
        return 2, None
    goi = CACHE / bg["khoa"]
    goi.mkdir(parents=True, exist_ok=True)
    pdf = Path(bg["pdf"][0])
    if not pdf.is_file():
        print(f"⚪ tệp PDF vắng trên đĩa: {pdf} (OneDrive chưa tải về?)")
        return 2, None
    trang = tach_trang(pdf)
    so_ky_tu = sum(len(t) for t in trang)
    (goi / "van_ban.txt").write_text(ghep_van_ban(trang), encoding="utf-8")
    khop, ly_do = khop_dinh_danh(trang, bg["doi"], bg["tieu_de"])
    ngu_canh = _ngu_canh_cua(ngu_canh_tat_ca if ngu_canh_tat_ca is not None else ngu_canh_dashboard(), bg["pmid"], bg["doi"])
    rb = rut_bai(bg["pmid"], bg["doi"])
    nc = {"ban_ghi": {k: bg[k] for k in ("rec", "pmid", "doi", "tieu_de", "nam", "tac_gia", "tap_chi", "khoa")},
          "pdf": {"tep": pdf.name, "sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(), "so_trang": len(trang),
                  "so_ky_tu": so_ky_tu, "trang_trong": [i for i, t in enumerate(trang, 1) if len(t.strip()) < 40]},
          "dinh_danh": {"khop": khop, "ly_do": ly_do}, "rut_bai": rb, "tang_uu_tien": tang_uu_tien(ngu_canh),
          "ngu_canh_dashboard": ngu_canh, "chuan_bi_luc": dt.datetime.now().isoformat(timespec="seconds")}
    (goi / "ngu_canh.json").write_text(json.dumps(nc, ensure_ascii=False, indent=2), encoding="utf-8")
    (goi / "HUONG-DAN-DOC.md").write_text(
        HUONG_DAN_DOC.format(pb=PHIEN_BAN_KHUON, tu=TOI_DA_TU_TRICH) + "\n```json\n"
        + json.dumps(MAU, ensure_ascii=False, indent=2) + "\n```\n", encoding="utf-8")
    print(f"Gói đọc: {goi}")
    print(f"  {bg['khoa']} · recNum {bg['rec']} · {len(trang)} trang · {so_ky_tu} ký tự · tầng ưu tiên {nc['tang_uu_tien']}")
    print(f"  định danh: {'✓' if khop else '✗'} {ly_do} · rút bài: {NHAN_RUT_BAI.get(rb['trang_thai'], rb['trang_thai'])}")
    if so_ky_tu < 2000:
        print("  ⚠ PDF gần như không có lớp chữ (PDF ảnh) — không tóm tắt máy được; bác sĩ đọc trực tiếp")
        return 2, goi
    if rb["trang_thai"] == "da_rut":
        print("  ⛔ BÀI ĐÃ BỊ RÚT — không soạn tóm tắt để áp dụng")
        return 3, goi
    if not khop:
        print("  ⛔ PDF có thể KHÔNG phải bài này — kiểm tệp đính kèm trước khi tóm tắt")
        return 3, goi
    print(f"  Đọc: {goi / 'HUONG-DAN-DOC.md'} → viết {goi / 'tom_tat.json'} → `dung {bg['khoa']}`")
    return 0, goi


# ───────────────────────── CỔNG kiểm tom_tat.json ─────────────────────────

def _rong(v) -> bool:
    if v is None:
        return True
    if isinstance(v, str):
        return not v.strip() or v.strip() in ("…", "...")
    if isinstance(v, (list, dict)):
        return not v or all(_rong(x) for x in (v.values() if isinstance(v, dict) else v))
    return False


def _chuan_cong_cu(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower())


def _tap_so_trang(trang: list[str], so_trang: int) -> set[str]:
    ra: set[str] = set()
    for i in range(max(1, so_trang - 1), min(len(trang), so_trang + 1) + 1):
        ra.update(cac_so(trang[i - 1]))
    return ra


def _cau_co_tren_trang(cau: str, trang: list[str], so_trang: int) -> bool:
    """Câu trích có trên trang khai (±1) — khớp chuỗi sau chuẩn hoá, hoặc đủ các từ theo đúng thứ tự trong một khoảng
    ≤ 2× độ dài câu (PDF hay chèn xuống dòng/ký hiệu giữa chữ)."""
    q = _chuan_chu(cau).strip(" .\"'«»…")
    if not q:
        return False
    vung = _chuan_chu(" ".join(trang[max(0, so_trang - 2):min(len(trang), so_trang + 1)]))
    if q in vung:
        return True
    # PDF ngắt dòng có gạch nối kiểu «air -⏎way» hay «random-⏎ization»: so phần CHỈ chữ và số của hai bên.
    gon_q = re.sub(r"[\W_]+", "", q)
    if len(gon_q) >= 20 and gon_q in re.sub(r"[\W_]+", "", vung):
        return True
    tu_q = re.findall(r"\w+", q)
    tu_v = re.findall(r"\w+", vung)
    if not tu_q:
        return False
    for bat_dau in (i for i, w in enumerate(tu_v) if w == tu_q[0]):
        j, k = bat_dau, 0
        while j < len(tu_v) and j - bat_dau <= 2 * len(tu_q) and k < len(tu_q):
            if tu_v[j] == tu_q[k]:
                k += 1
            j += 1
        if k == len(tu_q):
            return True
    return False


def kiem_tom_tat(tt: dict, trang: list[str], ngu_canh: dict) -> list[str]:
    """Danh sách lỗi (rỗng = đạt). Mỗi lỗi là một câu tiếng Việt chỉ đúng chỗ phải sửa."""
    loi: list[str] = []
    if not isinstance(tt, dict):
        return ["tom_tat.json không phải đối tượng JSON"]
    if tt.get("phien_ban_khuon") != PHIEN_BAN_KHUON:
        loi.append(f"phien_ban_khuon phải là {PHIEN_BAN_KHUON}")
    bg = ngu_canh.get("ban_ghi") or {}
    if tt.get("khoa") != bg.get("khoa"):
        loi.append(f"khoa «{tt.get('khoa')}» khác bản ghi «{bg.get('khoa')}»")
    if bg.get("pmid") and str(tt.get("pmid") or "") != bg["pmid"]:
        loi.append(f"pmid «{tt.get('pmid')}» khác PMID của bản ghi EndNote «{bg['pmid']}»")
    tk = tt.get("loai_thiet_ke")
    if tk not in LOAI_THIET_KE:
        loi.append(f"loai_thiet_ke phải thuộc {LOAI_THIET_KE}")
        return loi
    for k in _BAT_BUOC_CHUNG + _BAT_BUOC_THEO_THIET_KE[tk]:
        if _rong(tt.get(k)):
            loi.append(f"thiếu hoặc rỗng: {k}")
    pico = tt.get("cau_hoi_lam_sang") or {}
    for k in ("loai", "P", "O"):
        if _rong(pico.get(k)):
            loi.append(f"cau_hoi_lam_sang.{k} rỗng")
    kl = tt.get("ket_luan_thuc_hanh") or []
    if not isinstance(kl, list) or not 2 <= len([x for x in kl if not _rong(x)]) <= 8:
        loi.append("ket_luan_thuc_hanh cần 2–8 gạch có nội dung")
    goi_y = tt.get("goi_y_ap_dung") or {}
    if _rong(goi_y.get("nen_lam")) and _rong(goi_y.get("khong_nen")):
        loi.append("goi_y_ap_dung cần ít nhất «nen_lam» hoặc «khong_nen»")
    # Công cụ nguy cơ sai lệch đúng thiết kế
    nc_sl = tt.get("nguy_co_sai_lech") or {}
    cc = _chuan_cong_cu(nc_sl.get("cong_cu", ""))
    hop_le = CONG_CU_HOP_LE[tk]
    if hop_le and not any(cc.startswith(h) for h in hop_le):
        loi.append(f"nguy_co_sai_lech.cong_cu «{nc_sl.get('cong_cu')}» không đúng thiết kế {tk} (hợp lệ: {', '.join(hop_le)})")
    if tk != "rct" and cc.startswith("rob2"):
        loi.append("RoB 2 chỉ dùng cho RCT")
    if tk not in ("nhan_thuoc",) and _rong(nc_sl.get("mien")):
        loi.append("nguy_co_sai_lech.mien rỗng — đánh giá từng miền của công cụ")
    for i, mi in enumerate(nc_sl.get("mien") or [], 1):
        if not isinstance(mi, dict) or _rong(mi.get("ten")) or _rong(mi.get("danh_gia")) or _rong(mi.get("ly_do")):
            loi.append(f"nguy_co_sai_lech.mien[{i}] cần ten · danh_gia · ly_do")
    # GRADE đề xuất
    gr = tt.get("grade_de_xuat") or []
    for i, g in enumerate(gr if isinstance(gr, list) else [], 1):
        if not isinstance(g, dict) or g.get("muc") not in MUC_GRADE or _rong(g.get("ly_do")) or _rong(g.get("ket_cuc")):
            loi.append(f"grade_de_xuat[{i}]: cần ket_cuc · muc ∈ {MUC_GRADE} · ly_do")
    # SỐ LIỆU: mọi số có nguyên văn trên trang khai (±1)
    for khoi in ("ket_qua", "tac_hai"):
        hang = tt.get(khoi) or []
        if not isinstance(hang, list):
            loi.append(f"{khoi} phải là danh sách")
            continue
        for i, h in enumerate(hang, 1):
            if not isinstance(h, dict) or _rong(h.get("ket_cuc")):
                loi.append(f"{khoi}[{i}] thiếu ket_cuc")
                continue
            tr = h.get("trang")
            if not isinstance(tr, int) or not 1 <= tr <= len(trang):
                loi.append(f"{khoi}[{i}] «{h.get('ket_cuc')}»: trang {tr!r} không hợp lệ (PDF có {len(trang)} trang)")
                continue
            tap = _tap_so_trang(trang, tr)
            may_tinh = set(h.get("may_tinh") or [])
            for truong in TRUONG_SO:
                if truong in may_tinh:
                    continue
                for so in cac_so(str(h.get(truong) or "")):
                    if not _so_khop(so, tap):
                        loi.append(f"{khoi}[{i}] «{h.get('ket_cuc')}».{truong}: số {so} KHÔNG có trên trang {tr}±1 "
                                   "— chép sai, sai trang, hay do máy tính (khai may_tinh)?")
    if tk in ("guideline", "nhan_thuoc"):
        for i, kc in enumerate(tt.get("khuyen_cao") or [], 1):
            if not isinstance(kc, dict) or _rong(kc.get("noi_dung")):
                loi.append(f"khuyen_cao[{i}] thiếu noi_dung")
                continue
            tr = kc.get("trang")
            if not isinstance(tr, int) or not 1 <= tr <= len(trang):
                loi.append(f"khuyen_cao[{i}]: trang {tr!r} không hợp lệ")
    # Trích nguyên văn
    for i, tc in enumerate(tt.get("trich_nguyen_van") or [], 1):
        cau = (tc or {}).get("cau", "") if isinstance(tc, dict) else ""
        tr = (tc or {}).get("trang") if isinstance(tc, dict) else None
        if len(re.findall(r"\S+", cau)) > TOI_DA_TU_TRICH:
            loi.append(f"trich_nguyen_van[{i}] dài {len(cau.split())} từ (tối đa {TOI_DA_TU_TRICH})")
        if not isinstance(tr, int) or not 1 <= tr <= len(trang) or not _cau_co_tren_trang(cau, trang, tr):
            loi.append(f"trich_nguyen_van[{i}] «{cau[:60]}» không tìm thấy nguyên văn trên trang {tr}±1")
    return loi


# ───────────────────────── dựng Markdown → Word ─────────────────────────

def _o(s) -> str:
    return re.sub(r"\s+", " ", str(s if s is not None else "")).replace("|", "/").strip() or "—"


def _ds(xs) -> list[str]:
    return [f"- {_o(x)}" for x in (xs or []) if not _rong(x)] or ["- —"]


def _bang(tieu_de: list[str], hang: list[list[str]]) -> list[str]:
    ra = ["| " + " | ".join(tieu_de) + " |", "|" + "---|" * len(tieu_de)]
    ra += ["| " + " | ".join(_o(c) for c in h) + " |" for h in hang]
    return ra + [""]


def _gia_tri(h: dict, truong: str) -> str:
    v = _o(h.get(truong))
    return f"{v} †" if v != "—" and truong in set(h.get("may_tinh") or []) else v


def dung_markdown(tt: dict, ngu_canh: dict) -> str:
    bg = ngu_canh.get("ban_ghi") or {}
    pdf = ngu_canh.get("pdf") or {}
    rb = ngu_canh.get("rut_bai") or {}
    tk = tt["loai_thiet_ke"]
    pico = tt.get("cau_hoi_lam_sang") or {}
    L: list[str] = ["# TÓM TẮT CHỨNG CỨ CHO THỰC HÀNH LÂM SÀNG", "",
                    f"**{_o(bg.get('tieu_de'))}**", "",
                    f"{_o(bg.get('tac_gia'))} · *{_o(bg.get('tap_chi'))}* · {_o(bg.get('nam'))} · "
                    + (f"PMID {bg['pmid']} · " if bg.get("pmid") else "") + (f"DOI {bg['doi']}" if bg.get("doi") else "DOI —"),
                    "", f"> **{MIEN_TRU}** Mức chứng cứ trong bản này là ĐỀ XUẤT CỦA MÁY; áp dụng cho người bệnh là quyết "
                    "định của bác sĩ (Cổng A).", ""]
    if rb.get("trang_thai") != "khong_thay_rut":
        L += [f"> **Trạng thái rút bài: {NHAN_RUT_BAI.get(rb.get('trang_thai'), rb.get('trang_thai'))}** "
              f"(tra lúc {_o(rb.get('luc'))}).", ""]
    L += ["## 1. Kết luận cho thực hành", ""] + _ds(tt.get("ket_luan_thuc_hanh")) + [""]
    L += ["## 2. Thông tin trích dẫn", ""] + _bang(["Mục", "Nội dung"], [
        ["Thiết kế", f"{TEN_THIET_KE[tk]} — {_o(tt.get('thiet_ke_mo_ta'))}"],
        ["Lĩnh vực", tt.get("linh_vuc")],
        ["Địa điểm", (tt.get("boi_canh") or {}).get("dia_diem")],
        ["Thời gian", (tt.get("boi_canh") or {}).get("thoi_gian")],
        ["Đăng ký", (tt.get("boi_canh") or {}).get("dang_ky")],
        ["Tài trợ", (tt.get("boi_canh") or {}).get("tai_tro")],
        ["Xung đột lợi ích", (tt.get("boi_canh") or {}).get("xung_dot_loi_ich")],
        ["Rút bài", f"{NHAN_RUT_BAI.get(rb.get('trang_thai'), '—')} — tra {_o(rb.get('luc'))} ({_o(rb.get('nguon'))})"],
    ])
    L += ["## 3. Câu hỏi lâm sàng (PICO)", ""] + _bang(["Thành phần", "Nội dung"], [
        ["Loại câu hỏi", pico.get("loai")], ["P — Người bệnh", pico.get("P")], ["I — Can thiệp / phơi nhiễm", pico.get("I")],
        ["C — So sánh", pico.get("C")], ["O — Kết cục", pico.get("O")]])
    if tk in ("guideline", "nhan_thuoc"):
        L += ["## 4. Phạm vi và phương pháp xây dựng", "", _o(tt.get("phan_tich")), ""]
        dt_ = tt.get("doi_tuong") or {}
        if not _rong(dt_):
            L += [f"**Đối tượng áp dụng:** {_o(dt_.get('dac_diem_nen') or dt_.get('co_mau'))}", ""]
        L += ["## 5. Các khuyến cáo (phân hạng NGUYÊN BẢN của nguồn)", ""] + _bang(
            ["#", "Khuyến cáo", "Lực khuyến cáo", "Mức chứng cứ", "Trang", "Liên quan dashboard"],
            [[str(i), kc.get("noi_dung"), kc.get("luc_khuyen_cao"), kc.get("muc_chung_cu"), kc.get("trang"),
              "có" if kc.get("lien_quan_dashboard") else "—"] for i, kc in enumerate(tt.get("khuyen_cao") or [], 1)])
        so = 6
    else:
        dt_ = tt.get("doi_tuong") or {}
        ct = tt.get("can_thiep_so_sanh") or {}
        kc_ = tt.get("ket_cuc") or {}
        L += ["## 4. Phương pháp", "", "### 4.1 Đối tượng", "", "**Tiêu chuẩn chọn:**", ""] + _ds(dt_.get("tieu_chuan_chon"))
        L += ["", "**Tiêu chuẩn loại:**", ""] + _ds(dt_.get("tieu_chuan_loai"))
        L += ["", f"**Cỡ mẫu:** {_o(dt_.get('co_mau'))}", "", f"**Đặc điểm nền:** {_o(dt_.get('dac_diem_nen'))}", ""]
        if not _rong(ct):
            L += ["### 4.2 Can thiệp và so sánh", "", f"**Can thiệp:** {_o(ct.get('can_thiep'))}", "",
                  f"**So sánh:** {_o(ct.get('so_sanh'))}", "", f"**Điều trị đi kèm:** {_o(ct.get('dong_tri_lieu'))}", ""]
        L += ["### 4.3 Kết cục và theo dõi", "", f"**Kết cục chính:** {_o(kc_.get('chinh'))}", "", "**Kết cục phụ:**", ""]
        L += _ds(kc_.get("phu")) + ["", f"**Thời gian theo dõi:** {_o(kc_.get('theo_doi'))}", ""]
        L += ["### 4.4 Phân tích thống kê", "", _o(tt.get("phan_tich")), ""]
        cot = ["Kết cục", "Nhóm can thiệp", "Nhóm so sánh", "Hiệu ứng", "KTC 95%", "p", "Tuyệt đối", "NNT/NNH", "Trang"]

        def _dong(h: dict) -> list[str]:
            ten = f"{_o(h.get('ket_cuc'))}" + (" (chính)" if h.get("chinh") else "")
            return [ten] + [_gia_tri(h, t) for t in TRUONG_SO] + [_o(h.get("trang"))]
        L += ["## 5. Kết quả", ""] + _bang(cot, [_dong(h) for h in tt.get("ket_qua") or []])
        if any(h.get("may_tinh") for h in (tt.get("ket_qua") or []) + (tt.get("tac_hai") or [])):
            L += ["† Số do MÁY tính từ số liệu của bài (cách tính ở mục 4.4) — không phải số bài báo công bố.", ""]
        if not _rong(tt.get("phan_nhom")):
            L += ["**Phân nhóm:**", ""] + _ds(tt.get("phan_nhom")) + [""]
        L += ["## 6. Tác hại và an toàn", ""]
        L += _bang(cot, [_dong(h) for h in tt.get("tac_hai") or []]) if tt.get("tac_hai") else []
        if not _rong(tt.get("tac_hai_ghi_chu")):
            L += [_o(tt.get("tac_hai_ghi_chu")), ""]
        so = 7
    nsl = tt.get("nguy_co_sai_lech") or {}
    L += [f"## {so}. Thẩm định nguy cơ sai lệch — {_o(nsl.get('cong_cu'))}", ""] + _bang(
        ["Miền", "Đánh giá", "Lý do", "Trang"],
        [[m.get("ten"), m.get("danh_gia"), m.get("ly_do"), m.get("trang")] for m in nsl.get("mien") or []])
    L += [f"**Tổng thể:** {_o(nsl.get('tong_the'))}", ""]
    L += [f"## {so + 1}. Mức chắc chắn của chứng cứ — GRADE (ĐỀ XUẤT CỦA MÁY, chưa qua bác sĩ)", ""] + _bang(
        ["Kết cục", "Mức đề xuất", "Lý do hạ/nâng"],
        [[g.get("ket_cuc"), g.get("muc"), g.get("ly_do")] for g in tt.get("grade_de_xuat") or []])
    ka = tt.get("kha_nang_ap_dung") or {}
    L += [f"## {so + 2}. Khả năng áp dụng cho người bệnh ngoại trú Việt Nam", "",
          f"**Tương đồng:** {_o(ka.get('tuong_dong'))}", "", f"**Khác biệt:** {_o(ka.get('khac_biet'))}", "",
          f"**Triển khai tại Việt Nam:** {_o(ka.get('trien_khai_viet_nam'))}", ""]
    gy = tt.get("goi_y_ap_dung") or {}
    L += [f"## {so + 3}. Gợi ý áp dụng vào thực hành (GỢI Ý — quyết định thuộc bác sĩ)", "", "**Nên làm:**", ""]
    L += _ds(gy.get("nen_lam")) + ["", "**Không nên:**", ""] + _ds(gy.get("khong_nen"))
    L += ["", "**Điều kiện / thận trọng:**", ""] + _ds(gy.get("dieu_kien")) + ["", "**Theo dõi:**", ""] + _ds(gy.get("theo_doi"))
    L += ["", f"## {so + 4}. Điểm mạnh và hạn chế", "", "**Điểm mạnh:**", ""] + _ds(tt.get("diem_manh"))
    L += ["", "**Hạn chế:**", ""] + _ds(tt.get("han_che")) + [""]
    L += [f"## {so + 5}. Đối chiếu với dashboard EBM", "", _o(tt.get("doi_chieu_dashboard")), ""]
    ds_nc = [x for x in ngu_canh.get("ngu_canh_dashboard") or [] if not x.get("ban_cu")]
    if ds_nc:
        L += _bang(["Dashboard", "Mục", "Vai", "Decision", "gradeLevel"],
                   [[x.get("chu_de"), f"{_o(x.get('muc'))} — {_o(x.get('tieu_de_muc'))}", x.get("vai"), x.get("decision"),
                     x.get("gradeLevel")] for x in ds_nc])
    L += [f"## {so + 6}. Trích nguyên văn chọn lọc (≤ {TOI_DA_TU_TRICH} từ)", ""]
    L += [f"- «{_o(t.get('cau'))}» (tr. {_o(t.get('trang'))})" for t in tt.get("trich_nguyen_van") or []] + [""]
    L += [f"## {so + 7}. Câu hỏi còn mở", ""] + _ds(tt.get("cau_hoi_mo")) + [""]
    L += ["---", "", "**Nguồn của bản tóm tắt**", ""] + _bang(["Mục", "Giá trị"], [
        ["Tệp toàn văn", f"{_o(pdf.get('tep'))} · {_o(pdf.get('so_trang'))} trang · SHA-256 {str(pdf.get('sha256', ''))[:16]}…"],
        ["Bản ghi EndNote", f"recNum {_o(bg.get('rec'))}"],
        ["Người soạn", tt.get("nguoi_soan") or "Claude (máy)"],
        ["Ngày dựng", dt.date.today().strftime("%d/%m/%Y")],
        ["Khuôn", f"phiên bản {PHIEN_BAN_KHUON} — tools/tom_tat_chung_cu_word.py"]])
    L += [f"*{MIEN_TRU} Không chứa thông tin định danh người bệnh.*", ""]
    return "\n".join(L)


def dung(thu_vien: Path, ma: str, *, gan_endnote: bool = False, ap_dung: bool = False, endnote=None,
         rut_bai=kiem_rut_bai) -> int:
    bg = tim_ban_ghi(thu_vien, ma)
    if bg is None:
        print(f"⚪ không thấy bản ghi có PDF cho «{ma}»")
        return 2
    goi = CACHE / bg["khoa"]
    if not (goi / "ngu_canh.json").is_file() or not (goi / "van_ban.txt").is_file():
        print(f"⚪ chưa có gói đọc — chạy `chuan-bi {bg['khoa']}` trước")
        return 2
    if not (goi / "tom_tat.json").is_file():
        print(f"⚪ chưa có {goi / 'tom_tat.json'} — phiên Claude đọc toàn văn và viết theo HUONG-DAN-DOC.md")
        return 2
    nc = json.loads((goi / "ngu_canh.json").read_text(encoding="utf-8"))
    if not (nc.get("dinh_danh") or {}).get("khop"):
        print(f"⛔ định danh PDF không khớp bản ghi ({(nc.get('dinh_danh') or {}).get('ly_do')}) — chặn")
        return 3
    nc["rut_bai"] = rut_bai(bg["pmid"], bg["doi"])  # tra LẠI lúc dựng — không dựa kết quả cũ của gói
    if nc["rut_bai"]["trang_thai"] == "da_rut":
        print("⛔ BÀI ĐÃ BỊ RÚT — không dựng tóm tắt để áp dụng")
        return 3
    try:
        tt = json.loads((goi / "tom_tat.json").read_text(encoding="utf-8"))
    except ValueError as e:
        print(f"✗ tom_tat.json không phải JSON hợp lệ: {e}")
        return 1
    loi = kiem_tom_tat(tt, doc_van_ban(goi), nc)
    if loi:
        print(f"✗ CỔNG: {len(loi)} lỗi — sửa tom_tat.json rồi chạy lại:")
        for x in loi:
            print(f"  · {x}")
        return 1
    md = dung_markdown(tt, nc)
    ra = tep_word(thu_vien, bg["khoa"])
    ra.parent.mkdir(parents=True, exist_ok=True)
    (ra.parent / "_nguon").mkdir(exist_ok=True)
    doc = mod("md").dung_docx(md, 12.0)
    doc.save(str(ra))
    (ra.parent / "_nguon" / f"{bg['khoa']}.json").write_text(json.dumps(tt, ensure_ascii=False, indent=2), encoding="utf-8")
    (ra.parent / "_nguon" / f"{bg['khoa']}.md").write_text(md, encoding="utf-8")
    print(f"✓ Word: {ra}")
    if gan_endnote:
        return gan_vao_endnote(thu_vien, bg, ra, ap_dung=ap_dung, endnote=endnote)
    return 0


# ───────────────────────── gắn vào EndNote (THÊM, không thay) ─────────────────────────

def _tach_tep(gia_tri: str) -> list[str]:
    return [x.strip() for x in re.split(r"[\r\n]+", gia_tri or "") if x.strip()]


def gan_vao_endnote(thu_vien: Path, bg: dict, tep: Path, *, ap_dung: bool, endnote=None) -> int:
    """THÊM tệp Word vào «File Attachments» của bản ghi; tệp cũ (PDF) phải còn nguyên khi đọc lại."""
    if endnote is None:
        nec = mod("nec")
        ch = nec.doc_cau_hinh() or {}
        endnote = nec.EndNoteMac(ch.get("ung_dung") or "EndNote 2025", thu_vien)
        if not endnote.dang_mo_dung_thu_vien():
            print(f"⚪ EndNote chưa mở thư viện {thu_vien.name} — Word đã lưu, chưa gắn")
            return 2
    ma = f'<RecordID database="{endnote.so_csdl()}" recNum="{bg["rec"]}" />'
    cu = _tach_tep(endnote.doc_truong([ma], "File Attachments").get(ma, ""))
    if not cu:
        print("⚪ không đọc được tệp đính kèm hiện có của bản ghi — không ghi (tránh xoá PDF)")
        return 2
    if any(tep.name in x for x in cu):
        print(f"= đã gắn sẵn {tep.name} vào recNum {bg['rec']}")
        return 0
    moi = "\r".join(cu + [tep.resolve().as_uri()])
    if not ap_dung:
        print(f"(chạy khô) sẽ thêm {tep.name} vào recNum {bg['rec']} — giữ {len(cu)} tệp cũ; thêm --ap-dung để ghi")
        return 0
    endnote._truoc_khi_ghi("gắn tóm tắt chứng cứ Word vào bản ghi")
    doc_lai = _tach_tep(endnote._chay('set field "File Attachments" of record (item 1 of argv) to (item 2 of argv)\n'
                                      'return field "File Attachments" of record (item 1 of argv)', ma, moi))
    if not all(x in doc_lai for x in cu):
        endnote._chay('set field "File Attachments" of record (item 1 of argv) to (item 2 of argv)', ma, "\r".join(cu))
        print(f"✗ EndNote làm mất tệp cũ khi thêm — đã ghi trả lại {len(cu)} tệp cũ cho recNum {bg['rec']}")
        return 1
    if not any(tep.name in x for x in doc_lai):
        print(f"✗ EndNote không nhận {tep.name} (đọc lại không thấy)")
        return 1
    print(f"✓ đã gắn {tep.name} vào recNum {bg['rec']} (giữ {len(cu)} tệp cũ)")
    return 0


# ───────────────────────── liệt kê / tiến độ ─────────────────────────

def liet_ke(thu_vien: Path, *, tang: int | None = None, chua_lam: bool = False) -> list[dict]:
    ds = ngu_canh_dashboard()
    ra = []
    for bg in ban_ghi_co_pdf(thu_vien):
        nc = _ngu_canh_cua(ds, bg["pmid"], bg["doi"])
        bg["tang"] = tang_uu_tien(nc)
        bg["da_lam"] = tep_word(thu_vien, bg["khoa"]).is_file()
        bg["muc_dashboard"] = sorted({f"{x.get('muc')}:{x.get('decision')}" for x in nc if x.get("vai") == "muc"})
        if (tang is None or bg["tang"] == tang) and not (chua_lam and bg["da_lam"]):
            ra.append(bg)
    return sorted(ra, key=lambda x: (x["tang"], x["da_lam"], x["khoa"]))


def _thu_vien() -> Path | None:
    tv = mod("sk").thu_vien_cau_hinh()
    if tv is None or not Path(tv).is_file():
        print("⚪ chưa khai thư viện EndNote (~/.ebm-endnote.json) hoặc tệp .enl vắng")
        return None
    return Path(tv)


def main(argv: list[str] | None = None) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Tóm tắt chứng cứ chi tiết tiếng Việt → Word Times New Roman, gắn EndNote")
    sub = ap.add_subparsers(dest="lenh", required=True)
    p = sub.add_parser("liet-ke")
    p.add_argument("--tang", type=int, choices=(1, 2, 3, 4))
    p.add_argument("--chua-lam", action="store_true")
    p.add_argument("--json", action="store_true")
    sub.add_parser("mau")
    sub.add_parser("tien-do")
    for ten in ("chuan-bi", "kiem", "dung"):
        p = sub.add_parser(ten)
        p.add_argument("ma")
        if ten == "dung":
            p.add_argument("--gan-endnote", action="store_true")
            p.add_argument("--ap-dung", action="store_true")
    a = ap.parse_args(argv)
    if a.lenh == "mau":
        print(HUONG_DAN_DOC.format(pb=PHIEN_BAN_KHUON, tu=TOI_DA_TU_TRICH))
        print(json.dumps(MAU, ensure_ascii=False, indent=2))
        return 0
    tv = _thu_vien()
    if tv is None:
        return 2
    if a.lenh == "liet-ke":
        ds = liet_ke(tv, tang=a.tang, chua_lam=a.chua_lam)
        if a.json:
            print(json.dumps([{k: v for k, v in x.items() if k != "pdf"} for x in ds], ensure_ascii=False, indent=1))
        else:
            for x in ds:
                print(f"T{x['tang']} {'✓' if x['da_lam'] else '·'} {x['khoa']:<14} rec {x['rec']:<5} {x['tieu_de'][:70]}"
                      f"  {' '.join(x['muc_dashboard'])[:40]}")
            print(f"— {len(ds)} trích dẫn")
        return 0
    if a.lenh == "tien-do":
        ds = liet_ke(tv)
        for t in (1, 2, 3, 4):
            nhom = [x for x in ds if x["tang"] == t]
            print(f"Tầng {t}: {sum(x['da_lam'] for x in nhom)}/{len(nhom)} đã có Word")
        print(f"Tổng: {sum(x['da_lam'] for x in ds)}/{len(ds)} · thư mục {thu_muc_ra(tv)}")
        return 0
    if a.lenh == "chuan-bi":
        return chuan_bi(tv, a.ma)[0]
    if a.lenh == "kiem":
        bg = tim_ban_ghi(tv, a.ma)
        goi = CACHE / bg["khoa"] if bg else None
        if not goi or not (goi / "tom_tat.json").is_file():
            print("⚪ chưa có gói đọc/tom_tat.json")
            return 2
        loi = kiem_tom_tat(json.loads((goi / "tom_tat.json").read_text(encoding="utf-8")), doc_van_ban(goi),
                           json.loads((goi / "ngu_canh.json").read_text(encoding="utf-8")))
        for x in loi:
            print(f"  · {x}")
        print("✓ cổng đạt" if not loi else f"✗ {len(loi)} lỗi")
        return 1 if loi else 0
    return dung(tv, a.ma, gan_endnote=a.gan_endnote, ap_dung=a.ap_dung)


if __name__ == "__main__":
    raise SystemExit(main())
