#!/usr/bin/env python3
"""Nạp TÀI LIỆU THAM KHẢO của MỘT đề tài nghiên cứu vào EndNote — bản ghi đúng chuẩn trích dẫn + toàn văn, KHÔNG tóm tắt.

Bác sĩ giao 25/10/2026: «Xây dựng cho hệ thống nghiên cứu với các trích dẫn của đề tài nghiên cứu được lưu trữ vào EndNote
đúng chuẩn trích dẫn nghiên cứu, không cần phải tóm tắt trích dẫn chi tiết như các chứng cứ của hệ thống cập nhật chứng cứ,
nhưng phải đảm bảo toàn văn».

Nguồn: mục «TÀI LIỆU THAM KHẢO» của đề cương nộp Hội đồng `exports/<đề tài>/DE_CUONG_NOP_HOI_DONG_<đề tài>.md` (`--tai-lieu`
thay bằng tài liệu khác, nhiều tệp thì gộp — trùng định danh giữ số của tệp đầu). Mỗi tài liệu tham khảo (TLTK):

- có PMID/DOI ⇒ đi ĐÚNG đường nạp chủ đề (`nap_endnote_chu_de.nap_chu_de`): metadata PubMed → Europe PMC → Crossref, kiểm
  trùng thư viện, thùng rác, danh sách loại trừ, nhóm đo theo group_id (không sinh nhóm trùng tên — BH170). Khác dashboard:
  từ khoá «NC: <đề tài>», nhãn «TLTK n», ghi chú nguồn; KHÔNG khối ĐỌC NHANH, KHÔNG tóm tắt Word (bác sĩ không cần);
- chỉ có DOI ⇒ tìm PMID qua PubMed `"<doi>"[aid]`: nhận khi ra ĐÚNG MỘT PMID và DOI của bản ghi PubMed TRÙNG DOI của TLTK;
- không định danh (văn bản nhà nước, sách) ⇒ tách trường từ CHÍNH câu Vancouver của đề cương («Tác giả. Tên. Nơi: Nhà xuất
  bản; Năm.»), chỉ nhận khi khuôn phủ trọn câu; không tách được ⇒ danh sách cho bác sĩ nhập tay. KHÔNG bịa trường.

Đối chiếu chuẩn trích dẫn (chỉ BÁO, không sửa đề cương): đánh số đứt/trùng, hai TLTK cùng định danh, tiêu đề của nguồn không
thấy trong câu TLTK (định danh có thể trỏ bài khác), năm lệch, bài đã rút (PubMed).

Toàn văn: kho chung `EBM-Dashboards/toan_van_oa` (`PMID-<n>_<NGUỒN>.pdf`) rồi thư mục đề tài `exports/<đề tài>/toan_van_tltk/`
(`PMID-<n>.pdf` · `DOI-<doi, ký tự lạ → _>.pdf` · `TLTK-<n>.pdf` cho TLTK không định danh; chỉ nhận tệp bắt đầu `%PDF-`).
`--gom-toan-van` chạy làn truy cập mở: PMC + Unpaywall cho PMID (`gom_toan_van_dashboard.py`, rồi in PDF từ toàn văn XML
bằng `in_pdf_toan_van_kho.py`), Unpaywall theo DOI cho TLTK không PMID — CÙNG cổng điều khoản (`vi_tri_oa_duoc_luu`: chỉ bản
mang giấy phép mở). Bài thuê bao: làn trình duyệt có uỷ quyền / bác sĩ tự đặt tệp đúng tên. Bản ghi đã có tệp đính kèm mà
chưa có PDF toàn văn (vd chỉ có PDF tóm tắt chứng cứ) ⇒ THÊM toàn văn, giữ mọi tệp cũ (`EndNoteMac.them_tep`).
Độ phủ = số TLTK có bản ghi mang PDF toàn văn trong EndNote / tổng TLTK — đo trên thư viện thật, không theo số dự định.

Nhóm: `--ten-nhom` → nhóm ĐÃ GHI NHỚ của đề tài (khoá `DE-TAI_<mã>` trong ~/.ebm-endnote.json, chung với
`nap_endnote_chu_de.py --de-tai`) → «NC · <mã>»; `--ap-dung` thật ghi nhớ tên đã dùng (25/10/2026 — tránh nhóm NC thứ hai).

Chạy khô mặc định. `--ap-dung` mới ghi EndNote và biên nhận `exports/<đề tài>/ENDNOTE_TLTK_<đề tài>.json`.
`--ghi-bien-nhan-toan-van` (18/11/2026 — bác sĩ: «tất cả trích dẫn cho nghiên cứu … phải luôn là toàn văn, nếu không phải
toàn văn và không thể lấy được toàn văn thì loại bỏ»): đo TỪNG TLTK của đề cương nộp + bản thảo G7 trên thư viện EndNote
THẬT (rồi kho toàn văn / `toan_van_tltk/`) và ghi biên nhận `exports/<đề tài>/TOAN_VAN_TLTK_<đề tài>.json` mà cổng
G10-AUTO-12 của repo y khoa đọc (`tools/toan_van_trich_dan.py` — khoá TLTK và khuôn biên nhận lấy từ CHÍNH mô-đun đó).
Ghi được cả khi chạy khô (chỉ ghi tệp đo, không đụng EndNote); EndNote chưa mở thư viện ⇒ KHÔNG ghi (giữ biên nhận cũ —
không đo được ≠ thiếu toàn văn). Làn đã thử: `--gom-toan-van` cùng lượt ⇒ «truy_cap_mo» CHỈ cho định danh làn đã kết
luận (21/11/2026: kho vắng — chạy từ worktree —, bộ gom/bộ in mã ≠ 0, lỗi mạng ⇒ ⚪ KHÔNG ĐO ĐƯỢC, không ghi); sổ «không
truy cập» của làn trình duyệt (`trinh_duyet/khong-truy-cap.jsonl`) ⇒ «trinh_duyet»; làn cũ ở biên nhận trước được giữ.
Mã thoát: 0 đủ (mọi TLTK trong EndNote, đủ toàn văn, không lệch) · 1 còn việc (thiếu toàn văn/lệch/chưa nhập được) ·
2 không chạy được · 3 tham số sai. Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
import urllib.parse
import urllib.request
from datetime import date, datetime
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
try:  # stdout UTF-8 cả trên Windows (CLAUDE.md §0.9)
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass


def _nap(ten_tep: str, ten_mod: str):
    sp = importlib.util.spec_from_file_location(ten_mod, ROOT / "tools" / ten_tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten_mod] = m
    sp.loader.exec_module(m)
    return m


NE = _nap("nap_endnote_chu_de.py", "_nec_de_tai")
MA_OK, MA_MOT_PHAN, MA_KHONG_CHAY, MA_THAM_SO = NE.MA_OK, NE.MA_MOT_PHAN, NE.MA_KHONG_CHAY, NE.MA_THAM_SO
TIEN_TO_NHOM = "NC · "
THU_MUC_TOAN_VAN = "toan_van_tltk"
NGUONG_TIEU_DE = 0.9

# ── đọc mục tài liệu tham khảo ─────────────────────────────────────────────────────────────────────

_DAU_MUC = re.compile(r"(?im)^#{1,3}\s+(?:\d+\.\s*)?(?:tài liệu tham khảo|references)\b.*$")
_DAU_MUC_KE = re.compile(r"(?m)^#{1,3}\s")
_DONG_SO = re.compile(r"^\s*(\d{1,3})\.\s+(\S.*?)\s*$")
_PMID = re.compile(r"PMID:?\s*(\d{6,9})", re.I)
_DOI = re.compile(r"\bdoi:?\s*(10\.\d{4,9}/\S+)", re.I)


def tep_mac_dinh(thu_muc: Path, study: str) -> Path:
    return thu_muc / f"DE_CUONG_NOP_HOI_DONG_{study}.md"


def doc_tltk(tep: Path) -> list[dict]:
    """Mục TLTK của một tài liệu Markdown → [{so, van_ban, pmid, doi}] theo thứ tự xuất hiện.

    Mục bắt đầu ở đề mục «TÀI LIỆU THAM KHẢO»/«References» (cấp 1–3, có thể đánh số) và dừng ở đề mục kế tiếp. Dòng không
    mang số mà nối ngay sau một TLTK là phần XUỐNG DÒNG của TLTK đó. Không thấy mục ⇒ ValueError (không coi là «0 TLTK»)."""
    t = tep.read_text(encoding="utf-8")
    m = _DAU_MUC.search(t)
    if not m:
        raise ValueError(f"{tep.name}: không thấy đề mục «TÀI LIỆU THAM KHẢO»")
    phan = t[m.end():]
    k = _DAU_MUC_KE.search(phan)
    if k:
        phan = phan[:k.start()]
    ra: list[dict] = []
    for dong in phan.splitlines():
        mm = _DONG_SO.match(dong)
        if mm:
            ra.append({"so": int(mm.group(1)), "van_ban": mm.group(2)})
        elif dong.strip() and ra:
            ra[-1]["van_ban"] += " " + dong.strip()
        elif not dong.strip() and ra:
            ra[-1]["_het"] = True  # dòng trống kết thúc TLTK — dòng chữ sau đó không nối vào nữa
    sach: list[dict] = []
    for r in ra:
        r.pop("_het", None)
        van = re.sub(r"\s+", " ", r["van_ban"]).strip()
        pm = _PMID.search(van)
        doi = _DOI.search(van)
        sach.append({"so": r["so"], "van_ban": van, "pmid": pm.group(1) if pm else None,
                     "doi": NE.chuan_doi(doi.group(1)) if doi else None, "tai_lieu": tep.name})
    return sach


def gop_tai_lieu(ds_tep: list[Path]) -> tuple[list[dict], list[str]]:
    """Gộp TLTK của nhiều tài liệu; trả (TLTK, cảnh báo chuẩn trích dẫn của danh mục).

    Trong MỘT tài liệu: số phải liền 1..N, không lặp; hai TLTK cùng PMID/DOI là trùng (Vancouver: mỗi nguồn một số).
    Giữa các tài liệu: trùng định danh (hoặc trùng nguyên văn với TLTK không định danh) giữ bản của tệp ĐẦU."""
    gop: list[dict] = []
    canh_bao: list[str] = []
    thay: dict[str, dict] = {}
    for tep in ds_tep:
        ds = doc_tltk(tep)
        so = [r["so"] for r in ds]
        if so != list(range(1, len(so) + 1)):
            lap = sorted({s for s in so if so.count(s) > 1})
            thieu = sorted(set(range(1, max(so or [0]) + 1)) - set(so))
            canh_bao.append(f"{tep.name}: đánh số TLTK không liền 1..{len(so)}"
                            + (f" — lặp {lap}" if lap else "") + (f" — thiếu {thieu}" if thieu else ""))
        trong_tep: dict[str, int] = {}
        for r in ds:
            khoa = [f"pmid:{r['pmid']}"] if r["pmid"] else []
            khoa += [f"doi:{r['doi']}"] if r["doi"] else []
            khoa = khoa or [f"vb:{_chuan_chu(r['van_ban'])}"]
            lap_tep = next((trong_tep[k] for k in khoa if k in trong_tep), None)
            if lap_tep is not None:
                canh_bao.append(f"{tep.name}: TLTK {r['so']} trùng nguồn với TLTK {lap_tep}")
            for k in khoa:
                trong_tep.setdefault(k, r["so"])
            if any(k in thay for k in khoa):
                continue
            for k in khoa:
                thay[k] = r
            gop.append(r)
    return gop, canh_bao


# ── TLTK không định danh: tách trường từ CHÍNH câu Vancouver ──────────────────────────────────────

_SACH = re.compile(r"^(?P<tac_gia>[^.]+?)\. (?P<tieu_de>.+)\. (?P<noi>[^.:;]+): (?P<nxb>[^.:;]+); "
                   r"(?P<nam>(?:1[5-9]|20)\d{2})\.?$")
_VAN_BAN_NHA_NUOC = re.compile(r"^(?:Quyết định|Thông tư|Nghị định|Nghị quyết|Luật|Chỉ thị|Công văn|Pháp lệnh)\b")
_TAC_GIA_CA_NHAN = re.compile(r"^(?P<ho>\S(?:.*\S)?) (?P<tat>[A-Z]{1,4})$")
_ET_AL = re.compile(r"^(?:et al|và cộng sự|và cs)\.?$", re.I)


def tach_khong_dinh_danh(van_ban: str) -> dict | None:
    """Câu Vancouver sách/văn bản («Tác giả. Tên. Nơi: Nhà xuất bản; Năm.») → metadata EndNote; None nếu không tách AN TOÀN.

    An toàn = khuôn neo hai đầu phủ MỌI ký tự của câu (không phần nào bị bỏ hay đoán), câu không mang doi/URL/PMID. Tác giả
    cá nhân «Họ TẮT» → «Họ, T. Ắ.»
    (dạng EndNote); tác giả không mang chữ tắt là tác giả TẬP THỂ — EndNote cần dấu phẩy cuối («Bộ Y tế,») để không tách họ/tên.
    Văn bản nhà nước (tác giả tập thể, tên mở đầu «Quyết định/Thông tư/…») ⇒ «Government Document», còn lại ⇒ «Book»."""
    van = re.sub(r"\s+", " ", van_ban).strip()
    m = _SACH.match(van)
    if not m or re.search(r"\bdoi\b|https?://|PMID", van, re.I):
        return None
    g = {k: v.strip() for k, v in m.groupdict().items()}
    tac_gia: list[str] = []
    tap_the = True
    for a in (x.strip() for x in g["tac_gia"].split(",")):
        if not a or _ET_AL.match(a):
            continue
        mm = _TAC_GIA_CA_NHAN.match(a)
        if mm:
            tap_the = False
            tac_gia.append(f"{mm.group('ho')}, " + " ".join(f"{c}." for c in mm.group("tat")))
        else:
            tac_gia.append(a + ",")
    if not tac_gia:
        return None
    loai = "Government Document" if tap_the and _VAN_BAN_NHA_NUOC.match(g["tieu_de"]) else "Book"
    return {"pmid": None, "doi": None, "loai_tl": loai, "tac_gia": tac_gia, "tieu_de": g["tieu_de"], "nam": g["nam"],
            "noi_xb": g["noi"], "nha_xb": g["nxb"], "tap_chi": "", "nguon_meta": "câu TLTK của đề cương"}


# ── PMID cho TLTK chỉ có DOI ──────────────────────────────────────────────────────────────────────

def tim_pmid_theo_doi(doi: str, tai=None) -> list[str]:
    """PMID mà PubMed gắn cho DOI này (`"<doi>"[aid]`). NCBI chặn/lỗi ⇒ ném (người gọi ghi «không phân giải được»)."""
    tai = tai or NE._tai
    tu_khoa = urllib.parse.quote('"' + doi + '"[aid]')
    mail = NE._email()
    url = (f"{NE.EUTILS}/esearch.fcgi?db=pubmed&retmode=json&retmax=3&term={tu_khoa}"
           + (f"&email={urllib.parse.quote(mail)}" if mail else ""))
    du_lieu = tai(url)
    if NE.la_trang_chan_ncbi(du_lieu):
        raise NE.NcbiChan("NCBI đang chặn IP này")
    return [str(x) for x in json.loads(du_lieu)["esearchresult"]["idlist"]]


def phan_giai_pmid(ds: list[dict], tim=tim_pmid_theo_doi, lay_pm=None, lay_ep=None) -> dict:
    """Gắn PMID cho TLTK chỉ có DOI khi PubMed xác nhận hai chiều. Trả báo cáo {them: [...], khong_do_duoc: [...]}."""
    lay_pm = lay_pm or NE.lay_pubmed
    lay_ep = lay_ep or NE.lay_europepmc
    bc: dict = {"them": [], "khong_do_duoc": []}
    ung_vien: dict[str, str] = {}
    for r in ds:
        if r["doi"] and not r["pmid"]:
            try:
                ids = tim(r["doi"])
            except Exception as e:  # noqa: BLE001 — NCBI chặn/mạng lỗi: «không đo được», không phải «không có PMID»
                bc["khong_do_duoc"].append(f"TLTK {r['so']} ({type(e).__name__})")
                continue
            if len(ids) == 1:
                ung_vien[r["doi"]] = ids[0]
    if not ung_vien:
        return bc
    try:
        meta = dict(lay_pm(list(ung_vien.values())))
    except Exception:  # noqa: BLE001 — NCBI chặn ⇒ Europe PMC, như lượt nạp chủ đề
        try:
            meta = dict(lay_ep(list(ung_vien.values())))
        except Exception:  # noqa: BLE001
            meta = {}
    for r in ds:
        p = ung_vien.get(r["doi"] or "")
        if p and NE.chuan_doi((meta.get(p) or {}).get("doi")) == r["doi"]:
            r["pmid"] = p
            r["pmid_tu_doi"] = True
            bc["them"].append(f"TLTK {r['so']}: DOI {r['doi']} → PMID {p}")
    return bc


# ── đối chiếu câu TLTK với nguồn ──────────────────────────────────────────────────────────────────

def _chuan_chu(s: str) -> str:
    s = unicodedata.normalize("NFC", s or "").casefold()
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", s)).strip()


def do_giong_tieu_de(tieu_de: str, van_ban: str) -> float:
    """Độ giống tốt nhất giữa tiêu đề của nguồn và một đoạn cùng độ dài trong câu TLTK (1.0 = có nguyên văn)."""
    td, vb = _chuan_chu(tieu_de), _chuan_chu(van_ban)
    if not td:
        return 1.0
    if td in vb:
        return 1.0
    buoc = max(1, len(td) // 10)
    return max((SequenceMatcher(None, td, vb[i:i + len(td)]).ratio()
                for i in range(0, max(1, len(vb) - len(td) + 1), buoc)), default=0.0)


def doi_chieu(r: dict, m: dict) -> list[str]:
    """Lệch giữa câu TLTK của đề cương và bản ghi nguồn — chỉ BÁO (máy không sửa đề cương)."""
    lech: list[str] = []
    td = (m.get("tieu_de") or "").strip()
    gi = do_giong_tieu_de(td, r["van_ban"])
    if gi < NGUONG_TIEU_DE and re.fullmatch(r"\[.+\]\.?", td):
        # PubMed ghi bài không phải tiếng Anh bằng tiêu đề DỊCH trong ngoặc vuông (kiểu NLM) — đo 25/10/2026 ở TLTK 21 của C1a.
        lech.append(f"PubMed ghi tiêu đề DỊCH tiếng Anh trong ngoặc vuông «{td[:90]}» — câu TLTK trích tiêu đề gốc; bản ghi "
                    "EndNote mang tiêu đề dịch (kiểu NLM) — bác sĩ chọn giữ cách nào cho thống nhất")
    elif gi < NGUONG_TIEU_DE:
        lech.append(f"tiêu đề của nguồn «{td[:90]}» không khớp câu TLTK (giống {gi:.0%}) — định danh có thể trỏ bài khác, "
                    "hoặc nguồn ghi tiêu đề bằng ngôn ngữ khác")
    nam = str(m.get("nam") or "")
    if re.fullmatch(r"\d{4}", nam) and not re.search(rf"\b{nam}\b", r["van_ban"]):
        lech.append(f"năm của nguồn {nam} không có trong câu TLTK")
    if m.get("da_rut"):
        lech.append("PubMed gắn «Retracted Publication» — bài ĐÃ RÚT")
    return lech


# ── toàn văn ──────────────────────────────────────────────────────────────────────────────────────

def ten_doi(doi: str) -> str:
    return "DOI-" + re.sub(r"[^A-Za-z0-9._-]", "_", doi)


def ten_tep_can(r: dict) -> str:
    """Tên tệp bác sĩ đặt vào `toan_van_tltk/` khi tự tải toàn văn của TLTK này."""
    if r.get("pmid"):
        return f"PMID-{r['pmid']}.pdf"
    if r.get("doi"):
        return ten_doi(r["doi"]) + ".pdf"
    return f"TLTK-{r['so']}.pdf"


def la_pdf(p: Path) -> bool:
    try:
        with p.open("rb") as f:
            return f.read(5) == b"%PDF-"
    except OSError:
        return False


def chon_toan_van(r: dict, kho: Path | None, thu_muc_tv: Path | None) -> tuple[Path, str] | None:
    """PDF toàn văn của TLTK: kho chung theo PMID trước, rồi thư mục đề tài theo PMID → DOI → số TLTK (chỉ TLTK không định
    danh — đổi số thứ tự TLTK thì phải đổi tên tệp theo). Tệp không bắt đầu bằng `%PDF-` bị bỏ (trang lỗi lưu nhầm đuôi)."""
    pdf = NE.chon_pdf(kho, r.get("pmid"))
    if pdf and la_pdf(pdf[0]):
        return pdf
    if not thu_muc_tv or not thu_muc_tv.is_dir():
        return None
    goc = [f"PMID-{r['pmid']}"] if r.get("pmid") else []
    goc += [ten_doi(r["doi"])] if r.get("doi") else []
    goc += [] if (r.get("pmid") or r.get("doi")) else [f"TLTK-{r['so']}"]
    for g in goc:
        for p in sorted(thu_muc_tv.glob(f"{g}*.pdf")):
            if re.fullmatch(re.escape(g) + r"(?:_[A-Za-z]+)?\.pdf", p.name, flags=re.I) and la_pdf(p):
                return p, f"thư mục toàn văn của đề tài ({p.name})"
    return None


def co_toan_van(truong: str) -> bool:
    """Trường «File Attachments» có PDF TOÀN VĂN (không tính PDF/Word tóm tắt chứng cứ `*_TomTatChungCu.*`)."""
    for x in re.split(r"[\r\n]+", truong or ""):
        ten = urllib.parse.unquote(x.strip().rstrip("/").rsplit("/", 1)[-1])
        if ten.lower().endswith(".pdf") and not ten.endswith("_TomTatChungCu.pdf"):
            return True
    return False


def gom_doi_unpaywall(ds: list[dict], thu_muc_tv: Path, gom_mod=None, tai=None) -> dict:
    """Unpaywall theo DOI cho TLTK không PMID — CÙNG cổng điều khoản với tầng 2 của bộ gom (`vi_tri_oa_duoc_luu`): chỉ bản mang
    giấy phép mở được lưu tự động; chỉ nhận PDF thật (`%PDF-`). Ghi `DOI-<…>_UPW.pdf` vào thư mục toàn văn của đề tài.

    `da_do_doi` (21/11/2026): DOI (chữ thường) mà làn ra KẾT LUẬN được — đã lưu PDF · Unpaywall nói không có bản mở/cổng điều
    khoản chặn · vị trí mở chỉ trả trang HTML. Lỗi mạng/bố cục lạ (ngoại lệ ở lượt tra, hoặc MỌI vị trí đều ngoại lệ) ⇒
    `khong_do_duoc`, KHÔNG vào `da_do_doi`: biên nhận chỉ ghi lượt «truy_cap_mo» cho DOI trong `da_do_doi`."""
    gom_mod = gom_mod or _nap("gom_toan_van_dashboard.py", "_gtvd_de_tai")
    bc: dict = {"luu": [], "khong_luu": [], "da_do_doi": [], "khong_do_duoc": []}
    email = gom_mod._email_lich_su()
    if not email:
        bc["loi"] = "Unpaywall cần email định danh (NCBI_EMAIL trong ~/.ebm-secrets)"
        return bc
    if tai is None:
        def tai(url: str) -> bytes:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (EBM-OA-fetch)"})
            with urllib.request.urlopen(req, timeout=40) as ph:
                return ph.read()
    for r in ds:
        if not r.get("doi") or r.get("pmid"):
            continue
        nhan = f"TLTK {r['so']}"
        try:
            uj = json.loads(tai(f"https://api.unpaywall.org/v2/{urllib.parse.quote(r['doi'], safe='/')}?email={email}"))
            ds_url, ly_do = gom_mod.vi_tri_oa_duoc_luu(uj, r["doi"])
        except Exception as e:  # noqa: BLE001 — lỗi một bài không giết cả lượt
            bc["khong_luu"].append(f"{nhan}: {type(e).__name__}")
            bc["khong_do_duoc"].append(f"{nhan}: {type(e).__name__} khi tra Unpaywall — chưa kết luận")
            continue
        if not ds_url:
            bc["khong_luu"].append(f"{nhan}: {ly_do or 'Unpaywall không có bản truy cập mở'}")
            bc["da_do_doi"].append(r["doi"].lower())
            continue
        tra_loi = False  # ít nhất một vị trí trả nội dung — mọi vị trí ngoại lệ là lỗi mạng, không phải «trang HTML»
        for url in ds_url:
            try:
                du_lieu = tai(url)
            except Exception:  # noqa: BLE001 — vị trí này hỏng thì thử vị trí kế
                continue
            tra_loi = True
            if du_lieu[:5] == b"%PDF-":
                thu_muc_tv.mkdir(parents=True, exist_ok=True)
                gom_mod._ghi_nguyen_tu(thu_muc_tv / f"{ten_doi(r['doi'])}_UPW.pdf", du_lieu)
                bc["luu"].append(nhan)
                bc["da_do_doi"].append(r["doi"].lower())
                break
        else:
            if tra_loi:
                bc["khong_luu"].append(f"{nhan}: vị trí truy cập mở không trả PDF (trang HTML) — làn trình duyệt/bác sĩ")
                bc["da_do_doi"].append(r["doi"].lower())
            else:
                bc["khong_luu"].append(f"{nhan}: mọi vị trí truy cập mở đều lỗi khi tải")
                bc["khong_do_duoc"].append(f"{nhan}: mọi vị trí truy cập mở đều lỗi khi tải — chưa kết luận")
    return bc


# Dòng bộ gom IN RA khi lượt trả mã 0 mà vẫn có bài CHƯA kết luận (lỗi mạng từng bài, tầng Unpaywall bị bỏ vì thiếu email,
# XML lệch md5): thấy một dòng ⇒ cả làn theo PMID của lượt là «không đo được». Test khoá từng chuỗi vào dòng `print` THI HÀNH
# của `gom_toan_van_dashboard.py` — bộ gom đổi câu chữ thì test đỏ, không lặng lẽ thành «đã thử» (21/11/2026).
DAU_HIEU_GOM_CHUA_TRON = ("bài lỗi mạng lượt này", "Unpaywall cần email định danh", "chưa lấy được, lần sau thử lại",
                          "thử vị trí kế", "lượt sau thử lại")


def _kho_lan_oa() -> Path | None:
    """Kho mà làn truy cập mở theo PMID GHI vào: `toan_van_oa` của EBM-Dashboards gốc — bộ gom và bộ in PDF định vị bằng CÙNG
    `ban_sao_tran.duong_goc` từ cây này. None ở worktree/bản sao trần (không tự tạo kho — TT-05/W9)."""
    dash = NE._tim_dash_goc()
    kho = dash / "toan_van_oa" if dash else None
    return kho if kho is not None and kho.is_dir() else None


def _goi_y_cay_chinh() -> str:
    """Cây này là worktree của git mà cây chính có kho ⇒ chỉ đường chạy lại từ cây chính (chỉ GỢI Ý, không tự đọc/ghi kho
    của cây khác: bộ gom, bộ in PDF và engine y khoa đều định vị từ cây của chính chúng)."""
    try:
        kq = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--path-format=absolute", "--git-common-dir"],
                            capture_output=True, text=True, encoding="utf-8", timeout=15)
        chung = Path(kq.stdout.strip())
        chinh = chung.parent
        if (kq.returncode == 0 and chung.name == ".git" and chinh.resolve() != ROOT.resolve()
                and (chinh / "EBM-Dashboards" / "toan_van_oa").is_dir()):
            return f" Cây này là worktree — chạy lại lệnh từ cây chính {chinh}."
    except (OSError, ValueError, subprocess.SubprocessError):
        pass
    return ""


def gom_toan_van(ds: list[dict], thu_muc_tv: Path, kho: Path | None, chay=subprocess.run, gom_doi=gom_doi_unpaywall,
                 tim_kho_oa=_kho_lan_oa) -> dict:
    """Làn truy cập mở cho TLTK còn thiếu PDF: PMID ⇒ bộ gom kho chung (PMC + Unpaywall) rồi in PDF từ toàn văn XML; DOI không
    PMID ⇒ Unpaywall theo DOI vào thư mục đề tài. Không bao giờ tải bài thuê bao.

    21/11/2026: `do_duoc` = định danh mà làn ra KẾT LUẬN được ở lượt này (`pmid`, `doi`) — biên nhận chỉ ghi lượt
    «truy_cap_mo» cho các định danh đó. Làn theo PMID chỉ tính là đo được khi kho làn ghi vào CÓ THẬT và TRÙNG kho lượt này
    đọc, cả bộ gom lẫn bộ in PDF trả mã 0 và bộ gom không in dấu hiệu chưa trọn (`DAU_HIEU_GOM_CHUA_TRON`). Kho vắng/lệch ⇒
    không chạy làn PMID (bộ gom sẽ chỉ trả «KHÔNG ĐO ĐƯỢC»), ghi lý do vào `khong_do_duoc`. Trước bản vá: chạy từ worktree,
    bộ gom trả mã 2 «không thấy kho» mà biên nhận vẫn ghi «không có bản truy cập mở hợp lệ» cho 17 TLTK của C1a."""
    bc: dict = {"do_duoc": {"pmid": [], "doi": []}, "khong_do_duoc": []}
    pmids = [r["pmid"] for r in ds if r.get("pmid") and not chon_toan_van(r, kho, thu_muc_tv)]
    if pmids:
        bc["pmid_gui"] = pmids
        kho_oa = tim_kho_oa()
        if kho_oa is None:
            bc["khong_do_duoc"].append(f"làn theo PMID ({len(pmids)} TLTK): không thấy kho EBM-Dashboards/toan_van_oa ở "
                                       f"cây {ROOT} — KHÔNG chạy.{_goi_y_cay_chinh()}")
        elif kho is None or not Path(kho).is_dir() or Path(kho).resolve() != kho_oa.resolve():
            bc["khong_do_duoc"].append(f"làn theo PMID ({len(pmids)} TLTK) ghi vào {kho_oa} nhưng lượt này đọc kho {kho} "
                                       "— kết quả không đo được trên kho đang đọc — KHÔNG chạy")
        else:
            loi = []
            for ten, doi_so in (("gom", ["tools/gom_toan_van_dashboard.py", "--pmid", *pmids, "--unpaywall"]),
                                ("in_pdf", ["tools/in_pdf_toan_van_kho.py", "--kho", str(kho_oa), "--pmid", *pmids,
                                            "--ap-dung"])):
                kq = chay([sys.executable, *doi_so], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
                ra = (kq.stdout or "").strip()
                bc[ten] = {"ma": kq.returncode, "duoi": ra.splitlines()[-3:]}
                if kq.returncode != 0:
                    loi.append(f"{ten} mã {kq.returncode}")
                if ten == "gom":
                    loi += [f"gom in «{d}»" for d in DAU_HIEU_GOM_CHUA_TRON if d in ra]
            if loi:
                bc["khong_do_duoc"].append(f"làn theo PMID ({len(pmids)} TLTK) chưa trọn: {'; '.join(loi)}")
            else:
                bc["do_duoc"]["pmid"] = list(pmids)
    thieu_doi = [r for r in ds if r.get("doi") and not r.get("pmid") and not chon_toan_van(r, kho, thu_muc_tv)]
    if thieu_doi:
        u = gom_doi(thieu_doi, thu_muc_tv)
        bc["unpaywall_doi"] = u
        bc["do_duoc"]["doi"] = list(u.get("da_do_doi") or [])
        if u.get("loi"):
            bc["khong_do_duoc"].append(f"Unpaywall theo DOI ({len(thieu_doi)} TLTK): {u['loi']}")
        bc["khong_do_duoc"] += [f"Unpaywall theo DOI — {x}" for x in u.get("khong_do_duoc") or []]
    return bc


# ── EndNote ───────────────────────────────────────────────────────────────────────────────────────

def _ghi_chu(r: dict, study: str, m: dict) -> str:
    gc = (f"Tài liệu tham khảo số {r['so']} của {r['tai_lieu']} (đề tài {study}); nạp bởi EBM Copilot ngày "
          f"{date.today().isoformat()}. Metadata: {m.get('nguon_meta', '?')}.")
    if r.get("pmid_tu_doi"):
        gc += " PMID tra từ DOI qua PubMed (DOI của bản ghi PubMed trùng)."
    if m.get("da_rut"):
        gc += " CẢNH BÁO: PubMed gắn «Retracted Publication»."
    return gc


def _nhan(r: dict, m: dict) -> str:
    return f"TLTK {r['so']}" + (" · ĐÃ RÚT (PubMed)" if m.get("da_rut") else "")


def nap_khong_dinh_danh(endnote, ds: list[tuple[dict, dict]], study: str, ap_dung: bool) -> dict:
    """Nhập TLTK không định danh (đã tách khứ hồi). Trùng = bản ghi CÙNG tiêu đề trong thư viện ⇒ không nhập lại.
    Trả {ids: {số TLTK: mã bản ghi}, nhap_moi, da_co, loai_sai: [...]}. Đếm theo thư viện THẬT sau khi nhập."""
    bc: dict = {"ids": {}, "nhap_moi": 0, "da_co": 0, "loai_sai": [], "nhap_hut": []}
    if not ds or endnote is None:
        bc["ke_hoach"] = [f"TLTK {r['so']} ({m['loai_tl']})" for r, m in ds]
        return bc
    tieu_de = [m["tieu_de"] for _r, m in ds]
    co = endnote.tim_khop(tieu_de, "Title")
    moi = [(r, m) for r, m in ds if not co.get(m["tieu_de"])]
    bc["da_co"] = len(ds) - len(moi)
    for r, m in ds:
        if co.get(m["tieu_de"]):
            bc["ids"][r["so"]] = co[m["tieu_de"]][0]
    if not ap_dung:
        bc["ke_hoach"] = [f"TLTK {r['so']} ({m['loai_tl']})" for r, m in moi]
        return bc
    if moi:
        ban_ghi = [dict(m, tu_khoa=[f"NC: {study}"], ghi_chu=_ghi_chu(r, study, m), nhan=_nhan(r, m)) for r, m in moi]
        with tempfile.TemporaryDirectory(prefix="ebm-endnote-nc-") as tam:
            tep = Path(tam) / "nhap.xml"
            tep.write_text(NE.dung_xml(ban_ghi), encoding="utf-8", newline="\n")
            endnote.nhap(tep)
        sau = {}
        for _ in range(NE.CHO_NHAP_GIAY):
            sau = endnote.tim_khop([m["tieu_de"] for _r, m in moi], "Title")
            if all(sau.get(m["tieu_de"]) for _r, m in moi):
                break
            NE._ngu(1)
        for r, m in moi:
            if sau.get(m["tieu_de"]):
                bc["ids"][r["so"]] = sau[m["tieu_de"]][0]
                bc["nhap_moi"] += 1
            else:
                bc["nhap_hut"].append(f"TLTK {r['so']}")
        loai = endnote.doc_truong([bc["ids"][r["so"]] for r, _m in moi if r["so"] in bc["ids"]], "Reference Type") \
            if hasattr(endnote, "doc_truong") else {}
        for r, m in moi:
            ma = bc["ids"].get(r["so"])
            if ma and ma in loai and loai[ma].strip() != m["loai_tl"]:
                bc["loai_sai"].append(f"TLTK {r['so']}: EndNote ghi loại «{loai[ma].strip()}», dự định «{m['loai_tl']}»")
    return bc


def do_phu_toan_van(endnote, ma_theo_so: dict[int, str]) -> dict[int, bool | None]:
    """{số TLTK: True có PDF toàn văn · False chưa · None không đọc được} — đo trên thư viện THẬT."""
    if endnote is None or not ma_theo_so:
        return {}
    truong = endnote.doc_truong(list(dict.fromkeys(ma_theo_so.values())), "File Attachments")
    return {so: (co_toan_van(truong[ma]) if ma in truong else None) for so, ma in ma_theo_so.items()}


def ma_ban_ghi(endnote, ds: list[dict]) -> dict[int, str]:
    """{số TLTK có định danh: mã bản ghi ĐẦU TIÊN khớp PMID (Accession Number) rồi DOI}."""
    pm = endnote.tim_khop([r["pmid"] for r in ds if r.get("pmid")], "Accession Number")
    doi = endnote.tim_khop([r["doi"] for r in ds if r.get("doi")], "DOI")
    ra: dict[int, str] = {}
    for r in ds:
        ma = (pm.get(r["pmid"]) if r.get("pmid") else None) or (doi.get(r["doi"]) if r.get("doi") else None)
        if ma:
            ra[r["so"]] = ma[0]
    return ra


def khoa_nhom_de_tai(study: str) -> str:
    """Khoá của đề tài trong bảng `nhom_theo_chu_de` (~/.ebm-endnote.json) — CÙNG khoá với `nap_endnote_chu_de.py --de-tai`
    («DE-TAI_<mã>», 25/10/2026) ⇒ hai công cụ nạp trích dẫn đề tài về MỘT nhóm."""
    return NE.khoa_chu_de(Path(f"DE-TAI_{study}.json"))


def _ghi_nho_nhom(khoa: str, nhom: str, cau_hinh: Path | None) -> None:
    """Ghi nhớ nhóm của đề tài. Dưới pytest KHÔNG BAO GIỜ ghi tệp cấu hình thật trong thư mục nhà — test phải trỏ
    `NE.CAU_HINH`/`cau_hinh` sang thư mục tạm (cùng lối `ghi_cho_vao_nhom`)."""
    tep = Path(cau_hinh or NE.CAU_HINH)
    if os.environ.get("PYTEST_CURRENT_TEST") and tep == Path.home() / ".ebm-endnote.json":
        raise NE.KhongChayDuoc(f"đang chạy dưới pytest — không ghi cấu hình EndNote thật {tep}")
    NE.ghi_nhom(khoa, nhom, tep)


def chay(ds_tep: list[Path], study: str, thu_muc: Path, *, endnote, ap_dung: bool, kho: Path | None,
         ten_nhom: str | None = None, gom: bool = False, loai_tru: dict | None = None,
         lay_pm=None, lay_cr=None, lay_ep=None, tim_pmid=tim_pmid_theo_doi, gom_tv=gom_toan_van,
         cau_hinh: Path | None = None) -> dict:
    """Toàn bộ lượt nạp một đề tài. `endnote` None = chỉ lập kế hoạch (không kiểm trùng, không đo độ phủ trong EndNote).

    Tên nhóm (25/10/2026): `ten_nhom` (--ten-nhom) → nhóm ĐÃ GHI NHỚ của đề tài (khoá `DE-TAI_<mã>` trong `cau_hinh`, mặc định
    ~/.ebm-endnote.json — nhóm `--de-tai` hay lượt trước đã dựng) → «NC · <mã>». Thiếu bước giữa thì một đề tài đã có nhóm
    tên khác sinh thêm nhóm «NC · <mã>» thứ hai. Lượt `--ap-dung` thật (EndNote mở, nạp không lỗi) ghi nhớ tên nhóm đã dùng —
    `--ten-nhom` của bác sĩ thắng và được ghi nhớ, như `nap_endnote_chu_de.nap_nhieu`."""
    lay_pm = lay_pm or NE.lay_pubmed
    lay_cr = lay_cr or NE.lay_crossref
    lay_ep = lay_ep or NE.lay_europepmc
    ds, canh_bao = gop_tai_lieu(ds_tep)
    khoa = khoa_nhom_de_tai(study)
    da_ghi = NE.nhom_da_ghi(cau_hinh).get(khoa)
    nhom = ten_nhom or da_ghi or TIEN_TO_NHOM + study
    thu_muc_tv = thu_muc / THU_MUC_TOAN_VAN
    bc: dict = {"study": study, "tai_lieu": [t.name for t in ds_tep], "nhom": nhom, "so_tltk": len(ds),
                "nhom_nguon": "tham_so" if ten_nhom else ("ghi_nho" if da_ghi else "mac_dinh"),
                "ap_dung": ap_dung, "kiem_trung": endnote is not None, "danh_muc": canh_bao,
                "kho_toan_van": bool(kho and kho.is_dir()), "thu_muc_toan_van": str(thu_muc_tv)}
    bc["pmid_tu_doi"] = phan_giai_pmid(ds, tim=tim_pmid, lay_pm=lay_pm, lay_ep=lay_ep)

    # Metadata MỘT lần cho mọi TLTK có định danh — dùng cho đối chiếu và cho chính lượt nạp (không gọi nguồn hai lần).
    co_dd = [r for r in ds if r.get("pmid") or r.get("doi")]
    dd = [{"pmid": r.get("pmid"), "doi": r.get("doi"), "vai": "muc", "muc": f"TLTK {r['so']}"} for r in co_dd]
    co_meta, khong_lay = NE.lay_metadata(dd, lay_pm, lay_cr, lay_ep) if dd else ([], [])
    meta_so: dict[int, dict] = {}
    cache_pm: dict[str, dict] = {}
    cache_doi: dict[str, dict] = {}
    so_theo_muc = {f"TLTK {r['so']}": r for r in co_dd}
    for d, m in co_meta:
        r = so_theo_muc[d["muc"]]
        meta_so[r["so"]] = m
        if d.get("pmid"):
            cache_pm[d["pmid"]] = m
        else:
            cache_doi[d["doi"]] = m
    bc["khong_lay_duoc_metadata"] = khong_lay
    bc["lech"] = {f"TLTK {s}": doi_chieu(next(r for r in co_dd if r["so"] == s), m)
                  for s, m in meta_so.items()}
    bc["lech"] = {k: v for k, v in bc["lech"].items() if v}

    khong_dd = [r for r in ds if not (r.get("pmid") or r.get("doi"))]
    tach = [(r, tach_khong_dinh_danh(r["van_ban"])) for r in khong_dd]
    bc["khong_tach_duoc"] = [f"TLTK {r['so']}: {r['van_ban'][:120]}" for r, m in tach if m is None]
    tach = [(r, m) for r, m in tach if m is not None]

    if gom:
        bc["gom_toan_van"] = gom_tv(ds, thu_muc_tv, kho)

    def chon(d: dict):
        r = so_theo_muc.get(d.get("muc"))
        return chon_toan_van({**(r or {}), "pmid": d.get("pmid"), "doi": d.get("doi"), "so": (r or {}).get("so")},
                             kho, thu_muc_tv)

    bc["khong_dinh_danh"] = nap_khong_dinh_danh(endnote, tach, study, ap_dung)

    def bo_sung(d: dict, m: dict) -> None:
        r = so_theo_muc[d["muc"]]
        m["tu_khoa"] = [f"NC: {study}"]
        m["ghi_chu"] = _ghi_chu(r, study, m)
        m["nhan"] = _nhan(r, m)

    data = {"meta": {"question": nhom}, "items": [{"id": f"TLTK {r['so']}", "pmid": r.get("pmid") or "",
                                                   "doi": r.get("doi") or ""} for r in co_dd]}
    bc["nap"] = NE.nap_chu_de(
        ds_tep[0], endnote=endnote, ap_dung=ap_dung, kho=kho, doc_data=lambda _p: data,
        lay_pm=lambda pmids: {p: cache_pm[p] for p in pmids if p in cache_pm},
        lay_cr=lambda doi: cache_doi.get(doi), lay_ep=lambda _pmids: {}, ten_nhom=nhom, loai_tru=loai_tru,
        bo_sung=bo_sung, chon_pdf_cua=chon, ids_them=list(bc["khong_dinh_danh"]["ids"].values()) if ap_dung else None)
    # Chỉ ghi nhớ khi nhóm THẬT đã được xử lý trong EndNote (như nap_nhieu) — chạy khô/không mở EndNote/nạp lỗi thì không.
    if ap_dung and endnote is not None and not bc["nap"].get("loi") and da_ghi != nhom:
        _ghi_nho_nhom(khoa, nhom, cau_hinh)
        bc["ghi_nho_nhom"] = True

    # TLTK không định danh: gắn toàn văn bác sĩ đặt sẵn (`TLTK-<n>.pdf`) vào bản ghi chưa có tệp nào.
    if ap_dung and endnote is not None and bc["khong_dinh_danh"]["ids"]:
        ids = bc["khong_dinh_danh"]["ids"]
        tep = endnote.tep_dinh_kem(list(ids.values()))
        can = [(ma, None, pdf) for so, ma in ids.items() if tep.get(ma) == 0
               and (pdf := chon_toan_van({"so": so}, None, thu_muc_tv))]
        NE._gan_pdf(endnote, can)

    # Độ phủ đo trên thư viện THẬT; bản ghi có tệp đính kèm mà chưa có PDF toàn văn ⇒ THÊM (giữ tệp cũ).
    bc["thieu_toan_van"] = []
    bc["them_toan_van"] = []
    if endnote is not None:
        ma = ma_ban_ghi(endnote, co_dd)
        ma.update(bc["khong_dinh_danh"]["ids"])
        phu = do_phu_toan_van(endnote, ma)
        if ap_dung:
            for r in ds:
                if phu.get(r["so"]) is False:
                    pdf = chon_toan_van(r, kho, thu_muc_tv)
                    if pdf:
                        url, tm = NE.dat_pdf_vao_thu_vien(endnote.thu_vien, pdf[0], r.get("pmid"))
                        try:
                            endnote.them_tep(ma[r["so"]], url)
                        except Exception as e:  # noqa: BLE001 — một bản ghi hỏng không giết lượt; dọn PDF mồ côi
                            import shutil
                            shutil.rmtree(tm, ignore_errors=True)
                            bc["them_toan_van"].append(f"TLTK {r['so']}: LỖI {type(e).__name__}")
                            continue
                        bc["them_toan_van"].append(f"TLTK {r['so']}")
            phu = do_phu_toan_van(endnote, ma)
        bc["trong_endnote"] = len(ma)
        bc["co_toan_van"] = sum(1 for v in phu.values() if v)
        bc["khong_do_duoc_toan_van"] = [f"TLTK {s}" for s, v in phu.items() if v is None]
        bc["chua_trong_endnote"] = [f"TLTK {r['so']}" for r in ds if r["so"] not in ma]
        for r in ds:
            if phu.get(r["so"]) is False or r["so"] not in ma:
                bc["thieu_toan_van"].append(_viec_toan_van(r, kho, thu_muc_tv))
        bc["cho_gan"] = sum(1 for x in bc["thieu_toan_van"] if "có PDF sẵn" in x)
    else:
        bc["co_toan_van_san"] = sum(1 for r in ds if chon_toan_van(r, kho, thu_muc_tv))
        bc["thieu_toan_van"] = [_viec_toan_van(r, kho, thu_muc_tv) for r in ds if not chon_toan_van(r, kho, thu_muc_tv)]
        bc["cho_gan"] = 0
    return bc


def _viec_toan_van(r: dict, kho: Path | None, thu_muc_tv: Path) -> str:
    if chon_toan_van(r, kho, thu_muc_tv):
        return f"TLTK {r['so']}: có PDF sẵn — chạy lại với --ap-dung để gắn"
    dd = f"PMID {r['pmid']}" if r.get("pmid") else (f"DOI {r['doi']}" if r.get("doi") else "không định danh")
    return f"TLTK {r['so']} ({dd}): chưa có toàn văn — đặt `{THU_MUC_TOAN_VAN}/{ten_tep_can(r)}`"


# ── biên nhận toàn văn từng TLTK (18/11/2026) ──────────────────────────────────────────────────────────────────────

def nap_tvt(thu_muc: Path):
    """Mô-đun `toan_van_trich_dan` của repo y khoa chứa đề tài (exports/<mã> → <repo>/tools/) — None nếu chưa có."""
    tep = Path(thu_muc).resolve().parent.parent / "tools" / "toan_van_trich_dan.py"
    if not tep.is_file():
        return None
    sp = importlib.util.spec_from_file_location("_tvt_de_tai", tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules["_tvt_de_tai"] = m
    sp.loader.exec_module(m)
    return m


def _gop_lan(lan: list[dict], them: dict) -> None:
    if not any(x.get("lan") == them["lan"] and x.get("ngay") == them["ngay"] for x in lan):
        lan.append(them)


def bien_nhan_toan_van(study: str, thu_muc: Path, *, endnote, kho: Path | None, bc: dict, tvt,
                       hom_nay: date | None = None, khong_truy_cap: dict | None = None) -> dict:
    """Biên nhận `de_tai/toan_van_tltk/v1` cho MỌI TLTK của đề cương nộp + bản thảo G7 (khoá TLTK theo `tvt`).

    toan_van: True khi bản ghi EndNote mang PDF toàn văn, hoặc PDF toàn văn có sẵn ở kho chung/`toan_van_tltk/` (chờ
    gắn) · False khi EndNote đo được mà không có (kể cả TLTK chưa có bản ghi) · None khi không đọc được trường tệp."""
    hom_nay = hom_nay or date.today()
    tltk, van_ban = tvt.tltk_de_tai(thu_muc, study)
    cu, _loi = tvt.doc_bien_nhan(thu_muc, study)
    thu_muc_tv = Path(thu_muc) / THU_MUC_TOAN_VAN
    ds = []
    for i, t in enumerate(tltk):
        pm = next((k.split(":", 1)[1] for k in t["khoa"] if k.startswith("pmid:")), None)
        doi = next((k.split(":", 1)[1] for k in t["khoa"] if k.startswith("doi:")), None)
        ds.append({"so": i, "so_tltk": t["so"], "pmid": pm, "doi": doi, "tai_lieu": t["tai_lieu"], "khoa": t["khoa"]})
    ma = ma_ban_ghi(endnote, [r for r in ds if r["pmid"] or r["doi"]]) if endnote is not None else {}
    ids_kdd = {str(k): v for k, v in ((bc.get("khong_dinh_danh") or {}).get("ids") or {}).items()}
    for r in ds:  # TLTK không định danh của đề cương nộp: mã bản ghi do lượt nạp này tạo/tìm (theo số TLTK)
        if not (r["pmid"] or r["doi"]) and r["tai_lieu"].startswith("DE_CUONG_NOP") and ids_kdd.get(str(r["so_tltk"])):
            ma[r["so"]] = ids_kdd[str(r["so_tltk"])]
    phu = do_phu_toan_van(endnote, ma) if endnote is not None else {}
    # 21/11/2026: làn truy cập mở chỉ ghi cho định danh làn ĐÃ KẾT LUẬN ở lượt này (`do_duoc` của `gom_toan_van`). Trước bản
    # vá: có báo cáo gom (kể cả bộ gom trả mã 2 «không thấy kho» khi chạy từ worktree) là MỌI TLTK thiếu PDF — cả TLTK chỉ có
    # trong bản thảo G7 chưa từng được gửi đi gom — nhận «không có bản truy cập mở hợp lệ».
    do_duoc = (bc.get("gom_toan_van") or {}).get("do_duoc") or {}
    da_do_pmid = {str(p) for p in do_duoc.get("pmid") or []}
    da_do_doi = {str(d).lower() for d in do_duoc.get("doi") or []}
    khong_tc = khong_truy_cap or {}
    # 18/11/2026: TLTK chỉ ghi DOI mà lượt nạp đã tra ra PMID («TLTK n: DOI d → PMID p») ⇒ tra sổ «không truy cập» theo
    # cả PMID đó (C1a TLTK 35: sổ ghi theo PMID 16943232, đề cương chỉ có DOI ⇒ trước đây không bao giờ khớp).
    doi_ra_pmid = {d.lower(): p for x in (bc.get("pmid_tu_doi") or {}).get("them") or []
                   for d, p in re.findall(r"DOI (\S+) → PMID (\d+)", str(x))}
    muc = []
    for r in ds:
        tv = phu.get(r["so"]) if r["so"] in ma else (False if endnote is not None else None)
        nguon, tep = ("endnote", None) if tv else (None, None)
        if not tv:
            ra_tep = {"so": r["so_tltk"] if r["tai_lieu"].startswith("DE_CUONG_NOP") else -1,
                      "pmid": r["pmid"], "doi": r["doi"]}
            pdf = chon_toan_van(ra_tep, kho, thu_muc_tv)
            if pdf:
                tv, tep = True, pdf[0].name
                nguon = "toan_van_tltk" if pdf[0].parent.resolve() == thu_muc_tv.resolve() else "kho_toan_van"
        lan = list((tvt._tim_muc(r["khoa"], cu) or {}).get("lan_da_thu") or []) if cu else []
        if tv is False:
            pm_do = next((p for p in (r["pmid"], doi_ra_pmid.get(str(r["doi"] or "").lower())) if p in da_do_pmid), None)
            if pm_do:
                _gop_lan(lan, {"lan": "truy_cap_mo", "ngay": hom_nay.isoformat(),
                               "ket_qua": "--gom-toan-van (PMC + Unpaywall theo PMID): không có bản truy cập mở hợp lệ"})
            elif r["doi"] and r["doi"].lower() in da_do_doi:
                _gop_lan(lan, {"lan": "truy_cap_mo", "ngay": hom_nay.isoformat(),
                               "ket_qua": "--gom-toan-van (Unpaywall theo DOI): không có bản truy cập mở hợp lệ"})
            khoa_ktc = [k for k in (r["pmid"], doi_ra_pmid.get(str(r["doi"] or "").lower()),
                                    f"doi:{str(r['doi']).lower()}" if r["doi"] else None) if k and k in khong_tc]
            if khoa_ktc:
                d = khong_tc[khoa_ktc[0]]
                _gop_lan(lan, {"lan": "trinh_duyet", "ngay": str(d.get("ngay")),
                               "ket_qua": str(d.get("ly_do") or "sổ «không truy cập»: không có quyền đọc")[:200]})
        muc.append({"so": r["so_tltk"], "tai_lieu": r["tai_lieu"], "khoa": r["khoa"], "toan_van": tv, "nguon": nguon,
                    "tep": tep, "lan_da_thu": lan})
    return {"schema": tvt.SCHEMA, "study": study, "luc": datetime.now().isoformat(timespec="seconds"),
            "nguoi_do": "tools/nap_endnote_de_tai.py --ghi-bien-nhan-toan-van (đo trên thư viện EndNote thật)",
            "tai_lieu": van_ban, "muc": muc}


def _chay_bien_nhan(study: str, thu_muc: Path, *, endnote, kho: Path | None, bc: dict) -> None:
    tvt = nap_tvt(thu_muc)
    if tvt is None:
        print("   ⚪ Biên nhận toàn văn: repo y khoa chưa có tools/toan_van_trich_dan.py — không ghi.")
        return
    if endnote is None:
        print("   ⚪ Biên nhận toàn văn: EndNote chưa mở đúng thư viện — KHÔNG ghi (không đo được ≠ thiếu toàn văn; "
              "giữ biên nhận cũ). Mở thư viện rồi chạy lại.")
        return
    ktc = {}
    if kho:
        try:
            dtv = _nap("doc_toan_van_co_nguoi.py", "_dtv_de_tai")
            ktc = dtv._khong_truy_cap(Path(kho), date.today())
        except Exception as e:  # noqa: BLE001 — sổ hỏng: không suy ra làn trình duyệt, vẫn ghi phần đo được
            print(f"   ⚪ không đọc được sổ «không truy cập»: {type(e).__name__}")
    bn = bien_nhan_toan_van(study, thu_muc, endnote=endnote, kho=kho, bc=bc, tvt=tvt, khong_truy_cap=ktc)
    tep = tvt.ghi_bien_nhan(thu_muc, study, bn)
    kq = tvt.danh_gia(thu_muc, study)
    dem = kq.get("dem") or {}
    print(f"   📄 Biên nhận toàn văn: {len(bn['muc'])} TLTK — có {dem.get('co', 0)} · còn làn chưa thử "
          f"{dem.get('chua_thu_het', 0)} · KHÔNG lấy được {dem.get('khong_lay_duoc', 0)} · chưa đo {dem.get('khong_do', 0)}"
          f" → {tep.name} ({kq['trang_thai']})")
    if dem.get("khong_lay_duoc"):
        print(f"   🔴 Có TLTK không lấy được toàn văn ⇒ loại: (repo y khoa) python3 tools/toan_van_trich_dan.py loai-bo "
              f"--study {study} --ap-dung, rồi sinh lại đề cương nộp và gỡ khỏi nhóm EndNote của đề tài.")


def ma_thoat(bc: dict) -> int:
    nap = bc.get("nap") or {}
    if nap.get("loi") or nap.get("nhap_hut") or bc["khong_dinh_danh"].get("nhap_hut"):
        return MA_KHONG_CHAY
    con_viec = (bc["thieu_toan_van"] or bc["lech"] or bc["danh_muc"] or bc["khong_tach_duoc"]
                or bc["khong_lay_duoc_metadata"] or bc.get("chua_trong_endnote") or not bc["kiem_trung"]
                or bc.get("khong_do_duoc_toan_van") or bc["khong_dinh_danh"].get("loai_sai")
                or (bc.get("gom_toan_van") or {}).get("khong_do_duoc"))
    return MA_MOT_PHAN if con_viec else MA_OK


def in_bao_cao(bc: dict) -> None:
    nap = bc.get("nap") or {}
    print(f"📚 TLTK đề tài {bc['study']} → EndNote nhóm «{bc['nhom']}» ({'NẠP THẬT' if bc['ap_dung'] else 'chạy khô'})")
    nguon = {"tham_so": "theo --ten-nhom", "ghi_nho": "nhóm đã ghi nhớ của đề tài",
             "mac_dinh": "tên mặc định — đề tài chưa có nhóm ghi nhớ"}.get(bc.get("nhom_nguon", ""))
    if nguon:
        print(f"   Nhóm: {nguon}" + (" · đã ghi nhớ cho lượt sau" if bc.get("ghi_nho_nhom") else ""))
    print(f"   {bc['so_tltk']} TLTK từ {', '.join(bc['tai_lieu'])}")
    for c in bc["danh_muc"]:
        print(f"   🟠 danh mục: {c}")
    for c in bc["pmid_tu_doi"]["them"]:
        print(f"   ✓ {c}")
    for c in bc["pmid_tu_doi"]["khong_do_duoc"]:
        print(f"   ⚪ chưa tra được PMID từ DOI: {c}")
    kd = bc["khong_dinh_danh"]
    if bc["ap_dung"]:
        print(f"   EndNote: đã có {nap.get('da_co', 0)} · nhập mới {nap.get('nhap_thuc', nap.get('nhap_moi', 0))} · "
              f"không định danh: nhập mới {kd.get('nhap_moi', 0)}, đã có {kd.get('da_co', 0)}")
    else:
        print(f"   EndNote: đã có {nap.get('da_co', 0)} · sẽ nhập {len(nap.get('ke_hoach_nhap') or [])} · không định danh: "
              f"sẽ nhập {len(kd.get('ke_hoach') or [])} ({', '.join(kd.get('ke_hoach') or []) or '—'}), "
              f"đã có {kd.get('da_co', 0)}")
    if not bc["kiem_trung"]:
        print("   ⚪ EndNote chưa mở đúng thư viện — kế hoạch chưa trừ bản ghi đã có, chưa đo độ phủ trong EndNote")
    for k in ("nhap_hut", "loai_tru", "trong_thung_rac"):
        if nap.get(k):
            print(f"   ⚠ {k}: {nap[k]}")
    if nap.get("cho_vao_nhom_moi"):
        print(f"   ⚠ nhóm «{bc['nhom']}» đã có — {len(nap['cho_vao_nhom_moi'])} bản ghi vào hàng chờ, bác sĩ kéo vào nhóm: "
              f"python3 tools/nap_endnote_chu_de.py --cho-vao-nhom \"{bc['nhom']}\"")
    for c in bc["khong_lay_duoc_metadata"]:
        print(f"   ✗ không lấy được metadata: {c}")
    for c in bc["khong_tach_duoc"]:
        print(f"   🟠 không định danh, không tách trường an toàn — bác sĩ nhập tay: {c}")
    for c in bc["khong_dinh_danh"].get("loai_sai", []):
        print(f"   🟠 {c}")
    for k, v in bc["lech"].items():
        for x in v:
            print(f"   🟠 {k}: {x}")
    g = bc.get("gom_toan_van")
    if g:
        for ten in ("gom", "in_pdf"):
            if ten in g:
                print(f"   làn OA {ten}: mã {g[ten]['ma']} · {' | '.join(g[ten]['duoi'])[:200]}")
        u = g.get("unpaywall_doi")
        if u:
            print(f"   Unpaywall theo DOI: lưu {len(u['luu'])} · không lưu {len(u['khong_luu'])}"
                  + (f" · {u['loi']}" if u.get("loi") else ""))
        for c in g.get("khong_do_duoc") or []:
            print(f"   ⚪ làn OA KHÔNG ĐO ĐƯỢC — {c} ⇒ biên nhận KHÔNG ghi lượt «truy_cap_mo» cho phần này")
    if bc["kiem_trung"]:
        print(f"   📄 TOÀN VĂN trong EndNote: {bc.get('co_toan_van', 0)}/{bc['so_tltk']} TLTK"
              + (f" · thêm lượt này {len(bc['them_toan_van'])}" if bc["them_toan_van"] else "")
              + (f" · có PDF sẵn chờ gắn {bc['cho_gan']} (--ap-dung)" if bc.get("cho_gan") else ""))
        for c in bc.get("khong_do_duoc_toan_van", []):
            print(f"   ⚪ không đọc được tệp đính kèm: {c}")
    else:
        print(f"   📄 toàn văn có sẵn ngoài EndNote: {bc.get('co_toan_van_san', 0)}/{bc['so_tltk']} TLTK")
    if bc["thieu_toan_van"]:
        print(f"   Chưa có toàn văn trong EndNote ({len(bc['thieu_toan_van'])}):")
        for c in bc["thieu_toan_van"]:
            print(f"     · {c}")
        print("   Làn lấy toàn văn: (1) --gom-toan-van (bản truy cập mở hợp pháp) · (2) bài thuê bao: "
              "python3 tools/doc_toan_van_co_nguoi.py --pmid <PMID…> (bác sĩ tự đăng nhập/vượt chặn) · (3) bác sĩ tải "
              f"rồi đặt đúng tên vào {bc['thu_muc_toan_van']} · chạy lại lệnh này để gắn.")
    print("   Cần bác sĩ kiểm chứng.")


def _thu_muc_de_tai(study: str) -> Path:
    bst = _nap("ban_sao_tran.py", "_bst_de_tai")
    yk = bst.duong_goc("medical-ebm-automation", ROOT) or (ROOT / "medical-ebm-automation")
    return yk / "exports" / study


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    ap.add_argument("--study", required=True, help="mã đề tài (thư mục exports/<mã>/ của repo y khoa)")
    ap.add_argument("--thu-muc-de-tai", help="thư mục đề tài (mặc định medical-ebm-automation/exports/<mã>)")
    ap.add_argument("--tai-lieu", nargs="*", help="tệp .md có mục TLTK (mặc định DE_CUONG_NOP_HOI_DONG_<mã>.md)")
    ap.add_argument("--ten-nhom", help="tên nhóm EndNote (mặc định: nhóm đã ghi nhớ của đề tài — khoá DE-TAI_<mã> trong "
                                       f"~/.ebm-endnote.json — không có thì «{TIEN_TO_NHOM}<mã>»; --ap-dung ghi nhớ tên đã dùng)")
    ap.add_argument("--kho-toan-van", help="kho toàn văn chung (mặc định EBM-Dashboards/toan_van_oa)")
    ap.add_argument("--gom-toan-van", action="store_true",
                    help="chạy làn truy cập mở (PMC + Unpaywall, cổng điều khoản) cho TLTK còn thiếu PDF trước khi nạp")
    ap.add_argument("--ap-dung", action="store_true", help="ghi thật vào EndNote (mặc định chạy khô)")
    ap.add_argument("--ghi-bien-nhan-toan-van", action="store_true",
                    help="ghi biên nhận TOAN_VAN_TLTK_<mã>.json (đo từng TLTK trên EndNote thật) — cổng G10-AUTO-12 đọc")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,120}", a.study):
        print("✗ --study chỉ gồm chữ, số, «.», «_», «-»")
        return MA_THAM_SO
    thu_muc = Path(a.thu_muc_de_tai) if a.thu_muc_de_tai else _thu_muc_de_tai(a.study)
    if not thu_muc.is_dir():
        print(f"✗ không thấy thư mục đề tài {thu_muc}")
        return MA_KHONG_CHAY
    ds_tep = [Path(t) for t in a.tai_lieu] if a.tai_lieu else [tep_mac_dinh(thu_muc, a.study)]
    for t in ds_tep:
        if not t.is_file():
            print(f"✗ không thấy tài liệu {t}")
            return MA_KHONG_CHAY
    kho = NE.xac_dinh_kho(a.kho_toan_van, NE._tim_dash_goc(), [])

    endnote = None
    try:
        if not NE._la_mac():
            raise NE.KhongChayDuoc(NE.THONG_DIEP_KHONG_PHAI_MAC)
        ch = NE.doc_cau_hinh()
        if ch is None:
            raise NE.KhongChayDuoc(f"chưa cấu hình thư viện EndNote ({NE.CAU_HINH}) — chạy "
                                   "python3 tools/nap_endnote_chu_de.py --ghi-cau-hinh \"<đường dẫn .enl>\"")
        thu_vien = Path(ch["thu_vien"])
        if not thu_vien.is_file():
            raise NE.KhongChayDuoc(f"thư viện đã cấu hình không còn tồn tại: {thu_vien}")
        endnote = NE.EndNoteMac(ch["ung_dung"], thu_vien)
        if not endnote.dang_mo_dung_thu_vien():
            if a.ap_dung:
                endnote.mo_thu_vien()
            else:
                print(f"⚪ EndNote chưa mở thư viện {thu_vien.name} — chạy khô không kiểm được bài đã có.")
                endnote = None
    except NE.KhongChayDuoc as e:
        if a.ap_dung:
            print(f"✗ {e}")
            return MA_KHONG_CHAY
        print(f"⚪ {e} — chỉ lập kế hoạch.")
        endnote = None
    try:
        loai_tru = NE.doc_loai_tru()
    except NE.CauHinhHong as e:
        if a.ap_dung:
            print(f"✗ {e} — không nhập gì.")
            return MA_KHONG_CHAY
        print(f"⚪ {e} — kế hoạch CHƯA trừ danh sách loại trừ của bác sĩ.")
        loai_tru = {"doi": {}, "pmid": {}}
    try:
        bc = chay(ds_tep, a.study, thu_muc, endnote=endnote, ap_dung=a.ap_dung, kho=kho, ten_nhom=a.ten_nhom,
                  gom=a.gom_toan_van, loai_tru=loai_tru)
    except ValueError as e:
        print(f"✗ {e}")
        return MA_KHONG_CHAY
    except (RuntimeError, OSError) as e:
        print(f"✗ nạp TLTK: {type(e).__name__}: {e}"[:300])
        return MA_KHONG_CHAY
    in_bao_cao(bc)
    if a.ghi_bien_nhan_toan_van:
        _chay_bien_nhan(a.study, thu_muc, endnote=endnote, kho=kho, bc=bc)
    if a.ap_dung:
        tep = thu_muc / f"ENDNOTE_TLTK_{a.study}.json"
        tep.write_text(json.dumps({**bc, "luc": datetime.now().isoformat(timespec="seconds")}, ensure_ascii=False,
                                  indent=2, default=str) + "\n", encoding="utf-8", newline="\n")
        print(f"   Biên nhận: {tep}")
    else:
        print("Chạy khô — chưa ghi gì. Thêm --ap-dung để nạp thật.")
    if a.json:
        print(json.dumps(bc, ensure_ascii=False, indent=2, default=str))
    return ma_thoat(bc)


if __name__ == "__main__":
    sys.exit(main())
