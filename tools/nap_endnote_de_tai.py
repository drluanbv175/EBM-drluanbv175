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

Chạy khô mặc định. `--ap-dung` mới ghi EndNote và biên nhận `exports/<đề tài>/ENDNOTE_TLTK_<đề tài>.json`.
Mã thoát: 0 đủ (mọi TLTK trong EndNote, đủ toàn văn, không lệch) · 1 còn việc (thiếu toàn văn/lệch/chưa nhập được) ·
2 không chạy được · 3 tham số sai. Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
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
    giấy phép mở được lưu tự động; chỉ nhận PDF thật (`%PDF-`). Ghi `DOI-<…>_UPW.pdf` vào thư mục toàn văn của đề tài."""
    gom_mod = gom_mod or _nap("gom_toan_van_dashboard.py", "_gtvd_de_tai")
    bc: dict = {"luu": [], "khong_luu": []}
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
            continue
        if not ds_url:
            bc["khong_luu"].append(f"{nhan}: {ly_do or 'Unpaywall không có bản truy cập mở'}")
            continue
        for url in ds_url:
            try:
                du_lieu = tai(url)
            except Exception:  # noqa: BLE001 — vị trí này hỏng thì thử vị trí kế
                continue
            if du_lieu[:5] == b"%PDF-":
                thu_muc_tv.mkdir(parents=True, exist_ok=True)
                gom_mod._ghi_nguyen_tu(thu_muc_tv / f"{ten_doi(r['doi'])}_UPW.pdf", du_lieu)
                bc["luu"].append(nhan)
                break
        else:
            bc["khong_luu"].append(f"{nhan}: vị trí truy cập mở không trả PDF (trang HTML) — làn trình duyệt/bác sĩ")
    return bc


def gom_toan_van(ds: list[dict], thu_muc_tv: Path, kho: Path | None, chay=subprocess.run, gom_doi=gom_doi_unpaywall) -> dict:
    """Làn truy cập mở cho TLTK còn thiếu PDF: PMID ⇒ bộ gom kho chung (PMC + Unpaywall) rồi in PDF từ toàn văn XML; DOI không
    PMID ⇒ Unpaywall theo DOI vào thư mục đề tài. Không bao giờ tải bài thuê bao."""
    bc: dict = {}
    pmids = [r["pmid"] for r in ds if r.get("pmid") and not chon_toan_van(r, kho, thu_muc_tv)]
    if pmids:
        for ten, doi_so in (("gom", ["tools/gom_toan_van_dashboard.py", "--pmid", *pmids, "--unpaywall"]),
                            ("in_pdf", ["tools/in_pdf_toan_van_kho.py", "--pmid", *pmids, "--ap-dung"])):
            kq = chay([sys.executable, *doi_so], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
            bc[ten] = {"ma": kq.returncode, "duoi": (kq.stdout or "").strip().splitlines()[-3:]}
    thieu_doi = [r for r in ds if r.get("doi") and not r.get("pmid") and not chon_toan_van(r, kho, thu_muc_tv)]
    if thieu_doi:
        bc["unpaywall_doi"] = gom_doi(thieu_doi, thu_muc_tv)
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


def chay(ds_tep: list[Path], study: str, thu_muc: Path, *, endnote, ap_dung: bool, kho: Path | None,
         ten_nhom: str | None = None, gom: bool = False, loai_tru: dict | None = None,
         lay_pm=None, lay_cr=None, lay_ep=None, tim_pmid=tim_pmid_theo_doi, gom_tv=gom_toan_van) -> dict:
    """Toàn bộ lượt nạp một đề tài. `endnote` None = chỉ lập kế hoạch (không kiểm trùng, không đo độ phủ trong EndNote)."""
    lay_pm = lay_pm or NE.lay_pubmed
    lay_cr = lay_cr or NE.lay_crossref
    lay_ep = lay_ep or NE.lay_europepmc
    ds, canh_bao = gop_tai_lieu(ds_tep)
    nhom = ten_nhom or TIEN_TO_NHOM + study
    thu_muc_tv = thu_muc / THU_MUC_TOAN_VAN
    bc: dict = {"study": study, "tai_lieu": [t.name for t in ds_tep], "nhom": nhom, "so_tltk": len(ds),
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


def ma_thoat(bc: dict) -> int:
    nap = bc.get("nap") or {}
    if nap.get("loi") or nap.get("nhap_hut") or bc["khong_dinh_danh"].get("nhap_hut"):
        return MA_KHONG_CHAY
    con_viec = (bc["thieu_toan_van"] or bc["lech"] or bc["danh_muc"] or bc["khong_tach_duoc"]
                or bc["khong_lay_duoc_metadata"] or bc.get("chua_trong_endnote") or not bc["kiem_trung"]
                or bc.get("khong_do_duoc_toan_van") or bc["khong_dinh_danh"].get("loai_sai"))
    return MA_MOT_PHAN if con_viec else MA_OK


def in_bao_cao(bc: dict) -> None:
    nap = bc.get("nap") or {}
    print(f"📚 TLTK đề tài {bc['study']} → EndNote nhóm «{bc['nhom']}» ({'NẠP THẬT' if bc['ap_dung'] else 'chạy khô'})")
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
    ap.add_argument("--ten-nhom", help=f"tên nhóm EndNote (mặc định «{TIEN_TO_NHOM}<mã>»)")
    ap.add_argument("--kho-toan-van", help="kho toàn văn chung (mặc định EBM-Dashboards/toan_van_oa)")
    ap.add_argument("--gom-toan-van", action="store_true",
                    help="chạy làn truy cập mở (PMC + Unpaywall, cổng điều khoản) cho TLTK còn thiếu PDF trước khi nạp")
    ap.add_argument("--ap-dung", action="store_true", help="ghi thật vào EndNote (mặc định chạy khô)")
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
