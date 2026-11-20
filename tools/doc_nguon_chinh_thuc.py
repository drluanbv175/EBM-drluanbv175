#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ĐỌC NGUỒN CHÍNH THỨC cho mục «Áp dụng ngay» KHÔNG có PMID (20/11/2026).

VÌ SAO CÓ
=========
Bác sĩ (20/11/2026, «Làm 2,3,6»): mở rộng bảo đảm đọc toàn văn (BH161) sang các mục không PMID. Đo 20/11: 164/843 mục
«Áp dụng ngay» ở bản ĐÃ PASS mới nhất mỗi chủ đề không có PMID — phần lớn là trang chính thức (FDA/MHRA Drug Safety, trang
guideline) chỉ có `url`, vài mục chỉ có `doi`. `verify_dashboard.kiem_toan_van_apply` và `so_toan_van.py` chỉ đo PMID ⇒ nhóm
này chưa từng có bằng chứng đã đọc nguồn gốc. Công cụ này tạo bằng chứng; cổng `kiem_doc_nguon_chinh_thuc_apply` đọc nó.

BẰNG CHỨNG (ghi vào `EBM-Dashboards/toan_van_oa/nguon_chinh_thuc/<băm khoá>.json`):
  tai             máy tải TRỌN trang (urllib, nhận diện là công cụ — KHÔNG giả dạng trình duyệt), bóc chữ thân trang, đủ
                  ≥ 1500 ký tự và tiêu đề không phải trang chặn/lỗi ⇒ hồ sơ `cach: may_tai` (độ dài + sha256 của chữ thân).
                  Chỉ LƯU BẢN SAO chữ khi trang thuộc miền giấy phép mở (cơ quan nhà nước — `MIEN_GIAY_PHEP_MO`); miền khác
                  chỉ lưu độ dài + băm. Miền chặn truy cập tự động (FDA, EMA — `verify_dashboard.MIEN_CHAN_TRUY_CAP_TU_DONG`)
                  không tải ⇒ chuyển sang làn trình duyệt.
                  CỔNG ĐIỀU KHOẢN NXB TRƯỚC KHI TẢI (doctrine `_CONNECTOR-CHUNG-CU.md` §2septies — `lan_doc`): máy CHỈ tải
                  miền cơ quan nhà nước (`MIEN_GIAY_PHEP_MO`) hoặc NXB khai giấy phép mở cấp NXB (`GIAY_PHEP_MO_CAP_NXB`);
                  NXB trong bảng «cấm» (`DIEU_KHOAN_NXB` — Elsevier, ESC, OUP, ADA…) ⇒ còn uỷ quyền đọc của bác sĩ thì làn
                  trình duyệt, không thì BÁC SĨ ĐỌC TRỰC TIẾP; NXB/miền chưa kiểm ⇒ làn trình duyệt, Claude đọc trang
                  điều khoản trước và nạp kèm `--dieu-khoan`.
  nap-trinh-duyet trang đã mở bằng TRÌNH DUYỆT THẬT (khung trình duyệt của Claude; trang chặn bot thì BÁC SĨ tự bấm — Claude
                  không giải CAPTCHA); độ dài + sha256 tính TRONG trang (`huong-dan` in đoạn mã) ⇒ `cach: trinh_duyet`.
  bac-si-da-doc   bác sĩ tự đọc nguồn ⇒ dòng `nguon` trong `trinh_duyet/bac-si-da-doc.jsonl` kèm kết luận của bác sĩ
                  (không hết hạn). Agent chỉ chép NGUYÊN VĂN lời bác sĩ — không tự điền.

CỔNG CHẶN + SỔ NỢ (20/11/2026 — bác sĩ «Hoàn thiện tất cả vấn đề trên», chọn «Chặn, có sổ nợ»): cổng
`kiem_doc_nguon_chinh_thuc_apply` CHẶN mục apply không PMID khi nguồn chưa có bằng chứng; riêng các mục ĐÃ TỒN lúc chuyển
sang chặn nằm trong SỔ NỢ `EBM-Dashboards/no-nguon-chinh-thuc-apply.json` (khoá dashboard + item + khoá nguồn) ⇒ cảnh báo tới
hạn. `so-no` báo cáo; `so-no --tao` lập sổ MỘT lần (chỉ gồm mục đang chưa đọc lúc lập — mục mới không bao giờ vào nợ);
`so-no --gia-han` dời hạn, giữ nguyên danh sách. Cả hai đòi NGUYÊN VĂN lời bác sĩ (≥ 20 ký tự), hạn ≤ 90 ngày.

Dùng:
    python3 tools/doc_nguon_chinh_thuc.py liet-ke [--tat-ca] [--json]
    python3 tools/doc_nguon_chinh_thuc.py tai [--ghi] [--toi-da N]
    python3 tools/doc_nguon_chinh_thuc.py huong-dan
    python3 tools/doc_nguon_chinh_thuc.py nap-trinh-duyet --url URL [--doi DOI] --tieu-de "…" --so-ky-tu N --sha256 HEX \
            [--dieu-khoan "<căn cứ điều khoản>"] [--ghi]
    python3 tools/doc_nguon_chinh_thuc.py bac-si-da-doc --nguon "<DOI|URL>" --ghi-chu "<kết luận của bác sĩ>" [--ghi]
    python3 tools/doc_nguon_chinh_thuc.py so-no [--json]
    python3 tools/doc_nguon_chinh_thuc.py so-no --tao --han YYYY-MM-DD --can-cu "<nguyên văn lời bác sĩ>" [--ghi]
    python3 tools/doc_nguon_chinh_thuc.py so-no --gia-han YYYY-MM-DD --can-cu "<nguyên văn lời bác sĩ>" [--ghi]
Chạy khô mặc định (`--ghi` mới ghi). Mã thoát: 0 xong · 1 có nguồn chưa đọc được / đầu vào bị từ chối · 2 không đo được.
Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html as _html
import importlib.util
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
VD_NGUON = REPO / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "verify_dashboard.py"
TAC_NHAN = "EBM-Copilot/1.0 (doc nguon chinh thuc de kiem chung y khoa; cong cu, khong phai trinh duyet)"
# Miền cơ quan nhà nước — nội dung công bố theo giấy phép mở/miền công cộng (FDA/CDC/NIH: public domain; gov.uk: Open Government
# Licence; WHO: CC BY-NC-SA 3.0 IGO; EMA: cho phép tái sử dụng kèm ghi nguồn) ⇒ được lưu bản sao chữ để đối chiếu về sau.
MIEN_GIAY_PHEP_MO = ("gov.uk", "fda.gov", "cdc.gov", "nih.gov", "who.int", "ema.europa.eu", "hhs.gov")
# Trừ khỏi MIEN_GIAY_PHEP_MO (rà độc lập 20/11/2026): PMC và Bookshelf của NCBI nằm dưới nih.gov nhưng chứa nội dung CÓ BẢN QUYỀN
# của NXB/tác giả bên thứ ba — không phải tài liệu do cơ quan nhà nước soạn ⇒ không tự tải, không lưu bản sao.
MIEN_LOAI_TRU_GIAY_PHEP = ("ncbi.nlm.nih.gov",)


def mien_mo(host: str) -> bool:
    """Miền cơ quan nhà nước có giấy phép mở, TRỪ các kho nội dung bên thứ ba (PMC/Bookshelf)."""
    return thuoc_mien(host, MIEN_GIAY_PHEP_MO) and not thuoc_mien(host, MIEN_LOAI_TRU_GIAY_PHEP)


def doi_tron(doi: str) -> str:
    """DOI trần, chữ thường («https://doi.org/10.1016/…», «doi: 10.1016/…» ⇒ «10.1016/…») — để tra bảng NXB theo tiền tố."""
    return re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", (doi or "").strip(), flags=re.I).strip().lower()
_TIEU_DE_CHAN = re.compile(r"just a moment|attention required|access denied|request blocked|forbidden|page not found|"
                           r"not found|error 40\d|error 50\d|captcha|are you a robot|verify you are human|sign in|log in",
                           re.I)
_THE_BO = re.compile(r"<(script|style|noscript|nav|header|footer|aside|form|svg)\b.*?</\1\s*>", re.I | re.S)


def _nap(ten: str, duong: Path):
    sp = importlib.util.spec_from_file_location(ten, duong)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


def vd():
    return _nap("_dnct_vd", VD_NGUON)


def dtcn():
    """Mô-đun bảng điều khoản NXB (`tools/doc_toan_van_co_nguoi.py`) — nguồn DUY NHẤT của DIEU_KHOAN_NXB / uỷ quyền."""
    return _nap("_dnct_dtcn", REPO / "tools" / "doc_toan_van_co_nguoi.py")


def lan_doc(url: str, doi: str = "", *, V=None, DT=None, uy_quyen_fn=None) -> dict:
    """Làn được phép đọc một nguồn: {lan: may|trinh_duyet|bac_si, ly_do, can_dieu_khoan}.

    Thứ tự (fail-closed): bảng «cấm» (tiền tố DOI hoặc miền) TRƯỚC — có uỷ quyền đọc còn hiệu lực ⇒ chỉ làn trình duyệt, không
    ⇒ bác sĩ đọc trực tiếp; miền chặn truy cập tự động ⇒ làn trình duyệt; miền cơ quan nhà nước / NXB giấy phép mở cấp NXB ⇒ máy
    tải; còn lại = CHƯA KIỂM điều khoản ⇒ làn trình duyệt và phải khai căn cứ điều khoản khi nạp."""
    V = V or vd()
    DT = DT or dtcn()
    uy_quyen_fn = uy_quyen_fn or DT.uy_quyen_bac_si
    ten, d = DT.nxb_cua(doi_tron(doi), url or "")
    if ten:
        if (d or {}).get("ket_luan") == "cam" and uy_quyen_fn(ten):
            return {"lan": "trinh_duyet", "can_dieu_khoan": False,
                    "ly_do": f"NXB «{ten}» cấm dùng nội dung với AI nhưng còn uỷ quyền đọc của bác sĩ — chỉ làn trình duyệt, "
                             "máy không tải"}
        return {"lan": "bac_si", "can_dieu_khoan": False,
                "ly_do": f"NXB «{ten}» cấm (hoặc không rõ ⇒ xử như cấm) dùng nội dung với AI, chưa có uỷ quyền đọc ⇒ BÁC SĨ đọc "
                         "trực tiếp rồi ghi bac-si-da-doc; Claude không mở trang"}
    host = mien_cua(url or "")
    if host in V.MIEN_CHAN_TRUY_CAP_TU_DONG:          # ĐÚNG tên máy như cổng (api.fda.gov — openFDA — không bị chặn)
        return {"lan": "trinh_duyet", "can_dieu_khoan": False, "ly_do": "miền chặn truy cập tự động (FDA/EMA)"}
    if mien_mo(host):
        return {"lan": "may", "can_dieu_khoan": False, "ly_do": "miền cơ quan nhà nước (giấy phép mở/miền công cộng)"}
    t2, _ = DT.giay_phep_mo_cap_nxb(url or "")
    if t2:
        return {"lan": "may", "can_dieu_khoan": False, "ly_do": f"NXB «{t2}» khai giấy phép mở cho mọi nội dung trên miền"}
    return {"lan": "trinh_duyet", "can_dieu_khoan": True,
            "ly_do": "NXB/miền CHƯA kiểm điều khoản ⇒ Claude đọc trang điều khoản trước (doctrine §2septies), nạp kèm "
                     "--dieu-khoan; máy không tự tải"}


def goc_du_lieu(ten: str) -> Path:
    try:
        p = _nap("_dnct_bst", REPO / "tools" / "ban_sao_tran.py").duong_goc(ten, REPO)
    except Exception:  # noqa: BLE001
        p = None
    if p is None and os.environ.get("EBM_WORKSPACE_ROOT"):
        p = Path(os.environ["EBM_WORKSPACE_ROOT"]) / ten       # worktree ngoài OneDrive đọc dữ liệu cây chính
    return p or (REPO / ten)


def kho_mac_dinh() -> Path:
    return goc_du_lieu("EBM-Dashboards") / "toan_van_oa"


def ten_ho_so(khoa: str) -> str:
    return hashlib.sha256(khoa.encode("utf-8")).hexdigest()[:20] + ".json"


# ───────────────────────── quét mục ─────────────────────────

def quet_muc(dashboards: list[Path], V=None) -> list[dict]:
    """Mục decision='apply' KHÔNG có PMID: {dashboard, item, khoa, url, doi}. Khoá None ⇒ không truy nguyên được."""
    V = V or vd()
    ra = []
    for f in dashboards:
        blk = V.extract_data_block(Path(f).read_text(encoding="utf-8", errors="replace"))
        if not blk:
            continue
        for ch in V.split_items(blk):
            if V.field(ch, "decision") != "apply" or V.PMID_RE.match((V.field(ch, "pmid") or "").strip()):
                continue
            doi, url = V.field(ch, "doi"), V.field(ch, "url")
            ra.append({"dashboard": Path(f).stem, "item": V.field(ch, "id") or "(?)",
                       "khoa": V.khoa_nguon_chinh_thuc(doi, url), "url": (url or "").strip(), "doi": (doi or "").strip()})
    return ra


def chon_dashboard(tat_ca: bool) -> list[Path]:
    dash = goc_du_lieu("EBM-Dashboards")
    if tat_ca:
        return sorted(dash.glob("WebDashboard_*.html"))
    return _nap("_dnct_dn", REPO / "tools" / "do_nhay_kiem_ngu_nghia.py").chon_dashboard(dash)


def nhom_theo_khoa(muc: list[dict], co: set) -> dict[str, dict]:
    ra: dict[str, dict] = {}
    for m in muc:
        if not m["khoa"]:
            continue
        x = ra.setdefault(m["khoa"], {"khoa": m["khoa"], "url": m["url"], "doi": m["doi"], "muc": [],
                                      "da_doc": m["khoa"] in co})
        x["muc"].append(f"{m['dashboard'].replace('WebDashboard_EBM_VanDeCuThe_', '')} {m['item']}")
    return ra


# ───────────────────────── tải trang ─────────────────────────

def boc_chu(html: str) -> tuple[str, str]:
    """(tiêu đề, chữ thân trang đã gộp khoảng trắng) — bỏ script/style/nav/header/footer/aside/form."""
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    tieu_de = _html.unescape(re.sub(r"\s+", " ", m.group(1))).strip() if m else ""
    than = _THE_BO.sub(" ", html)
    than = re.sub(r"<[^>]+>", " ", than)
    return tieu_de, re.sub(r"\s+", " ", _html.unescape(than)).strip()


def mien_cua(url: str) -> str:
    """Tên máy (hostname) — KHÔNG tách netloc theo «:»: «https://cdc.gov:x@evil.example/» là evil.example (rà độc lập 20/11)."""
    try:
        return (urllib.parse.urlsplit(url).hostname or "").lower()
    except ValueError:
        return ""


def thuoc_mien(host: str, danh_sach) -> bool:
    return any(host == d or host.endswith("." + d) for d in danh_sach)


class _ChuyenHuongCoRao(urllib.request.HTTPRedirectHandler):
    """Chỉ đi theo chuyển hướng tới miền được phép TẢI TỰ ĐỘNG (miền nhà nước giấy phép mở, hoặc NXB khai giấy phép mở cấp
    NXB) — không tải byte của miền khác rồi mới bỏ (rà độc lập 20/11/2026)."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        host = mien_cua(newurl)
        cap_nxb = False
        try:
            cap_nxb = bool(dtcn().giay_phep_mo_cap_nxb(newurl)[0])
        except Exception:  # noqa: BLE001 — bảng điều khoản lỗi ⇒ coi như không được phép (fail-closed)
            cap_nxb = False
        if not (mien_mo(host) or cap_nxb):
            raise urllib.error.URLError(f"chuyển hướng sang miền không được phép tải tự động: {host}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def tai_trang(url: str, timeout: int = 60) -> tuple[str, str, bytes]:
    """(url cuối sau chuyển hướng, loại nội dung, byte). Lỗi mạng/HTTP/chuyển hướng bị chặn ⇒ ném (người gọi xử lý)."""
    req = urllib.request.Request(url, headers={"User-Agent": TAC_NHAN,
                                               "Accept": "text/html,application/xhtml+xml,application/pdf,application/json"})
    opener = urllib.request.build_opener(_ChuyenHuongCoRao())
    with opener.open(req, timeout=timeout) as r:  # noqa: S310 — URL từ dashboard đã qua cổng, chỉ http(s)
        return r.geturl(), (r.headers.get("Content-Type") or "").lower(), r.read(30_000_000)


def _chu_json(x) -> list[str]:
    if isinstance(x, str):
        return [x]
    if isinstance(x, dict):
        return [t for v in x.values() for t in _chu_json(v)]
    if isinstance(x, list):
        return [t for v in x for t in _chu_json(v)]
    return []


def boc_noi_dung(loai: str, du_lieu: bytes, url: str = "") -> tuple[str, str]:
    """(tiêu đề, chữ) theo loại nội dung: HTML · PDF (pypdf) · JSON (openFDA: gộp mọi chuỗi). Loại khác ⇒ ValueError."""
    if "pdf" in loai or url.lower().split("?")[0].endswith(".pdf"):
        try:
            import io
            from pypdf import PdfReader
        except ImportError as exc:
            raise ValueError("thiếu pypdf để đọc PDF") from exc
        doc = PdfReader(io.BytesIO(du_lieu))
        chu = re.sub(r"\s+", " ", " ".join((trang.extract_text() or "") for trang in doc.pages)).strip()
        tieu_de = str((doc.metadata or {}).get("/Title") or "").strip() or url.rsplit("/", 1)[-1]
        return tieu_de, chu
    if "json" in loai:
        try:
            d = json.loads(du_lieu.decode("utf-8", errors="replace"))
        except ValueError as exc:
            raise ValueError("JSON hỏng") from exc
        if isinstance(d, dict) and d.get("error"):
            return "error", ""
        ket = d.get("results") if isinstance(d, dict) else None
        chu = re.sub(r"\s+", " ", " ".join(_chu_json(ket if ket else d))).strip()
        return (url.split("?")[0].rsplit("/", 1)[-1] if chu else "error"), chu
    if "html" in loai or not loai:
        return boc_chu(du_lieu.decode("utf-8", errors="replace"))
    raise ValueError(f"loại nội dung chưa hỗ trợ ({loai})")


def danh_gia_trang(tieu_de: str, chu: str, V=None) -> str | None:
    """Lý do TỪ CHỐI (None = trang đủ làm bằng chứng)."""
    V = V or vd()
    if _TIEU_DE_CHAN.search(tieu_de or ""):
        return f"tiêu đề là trang chặn/lỗi («{tieu_de[:60]}»)"
    if len(chu) < V.SO_KY_TU_TOI_THIEU_NGUON:
        return f"chữ thân trang quá ngắn ({len(chu)} < {V.SO_KY_TU_TOI_THIEU_NGUON} ký tự) — có thể là trang chặn hay trang dẫn"
    return None


def ho_so(khoa: str, url: str, url_cuoi: str, tieu_de: str, chu: str, cach: str, ban_sao: bool) -> dict:
    return {"khoa": khoa, "url": url, "url_cuoi": url_cuoi, "tieu_de": tieu_de, "cach": cach, "so_ky_tu": len(chu),
            "sha256": hashlib.sha256(chu.encode("utf-8")).hexdigest(), "ban_sao": ban_sao,
            "luc": dt.datetime.now().isoformat(timespec="seconds")}


def ghi_ho_so(kho: Path, hs: dict, chu: str | None = None) -> Path:
    thu_muc = kho / vd().THU_MUC_NGUON_CHINH_THUC
    thu_muc.mkdir(parents=True, exist_ok=True)
    p = thu_muc / ten_ho_so(hs["khoa"])
    p.write_text(json.dumps(hs, ensure_ascii=False, indent=1), encoding="utf-8")
    if chu is not None:
        p.with_suffix(".txt").write_text(chu, encoding="utf-8")
    return p


def tai(nhom: dict[str, dict], kho: Path, *, ghi: bool, toi_da: int | None = None, nghi: float = 2.0,
        tai_fn=tai_trang, ngu=time.sleep, lan_fn=None) -> dict:
    """Tải trang cho các nguồn CHƯA có bằng chứng, CHỈ khi `lan_doc` cho phép máy tải. Trả {doc_duoc, tu_choi:[(khoa, lý do)],
    trinh_duyet:[khoa], bac_si:[(khoa, lý do)]}."""
    V = vd()
    lan_fn = lan_fn or (lambda url, doi: lan_doc(url, doi, V=V))
    viec = [x for x in nhom.values() if not x["da_doc"]]
    if toi_da is not None:
        viec = viec[:max(0, toi_da)]
    kq = {"doc_duoc": [], "tu_choi": [], "trinh_duyet": [], "bac_si": []}
    da_tai = 0
    for x in viec:
        url = x["url"] or (("https://doi.org/" + x["khoa"][4:]) if x["khoa"].startswith("doi:") else "")
        if not url:
            kq["tu_choi"].append((x["khoa"], "không có URL để tải"))
            continue
        lan = lan_fn(url, x.get("doi") or (x["khoa"][4:] if x["khoa"].startswith("doi:") else ""))
        if lan["lan"] == "bac_si":
            kq["bac_si"].append((x["khoa"], lan["ly_do"]))
            continue
        if lan["lan"] != "may":
            kq["trinh_duyet"].append(x["khoa"])
            continue
        if da_tai:
            ngu(nghi)
        da_tai += 1
        try:
            url_cuoi, loai, du_lieu = tai_fn(url)
            tieu_de, chu = boc_noi_dung(loai, du_lieu, url_cuoi)
        except Exception as exc:  # noqa: BLE001 — một nguồn lỗi (mạng, IncompleteRead, PDF hỏng…) không được giết cả lượt
            kq["tu_choi"].append((x["khoa"], f"tải lỗi: {type(exc).__name__}: {str(exc)[:80]} — chuyển làn trình duyệt"))
            kq["trinh_duyet"].append(x["khoa"])
            continue
        sau = lan_fn(url_cuoi, x.get("doi") or "")
        if sau["lan"] != "may":                     # chuyển hướng ra khỏi miền được phép tải ⇒ bỏ nội dung, không ghi
            (kq["bac_si"].append((x["khoa"], sau["ly_do"])) if sau["lan"] == "bac_si" else kq["trinh_duyet"].append(x["khoa"]))
            kq["tu_choi"].append((x["khoa"], f"chuyển hướng sang {mien_cua(url_cuoi)} — {sau['ly_do']}"))
            continue
        ly_do = danh_gia_trang(tieu_de, chu, V)
        if ly_do:
            kq["tu_choi"].append((x["khoa"], ly_do + " — chuyển làn trình duyệt"))
            kq["trinh_duyet"].append(x["khoa"])
            continue
        ban_sao = mien_mo(mien_cua(url_cuoi))
        if ghi:
            ghi_ho_so(kho, ho_so(x["khoa"], url, url_cuoi, tieu_de, chu, "may_tai", ban_sao), chu if ban_sao else None)
        kq["doc_duoc"].append(x["khoa"])
    return kq


# ───────────────────────── làn trình duyệt & bác sĩ ─────────────────────────

MA_TRONG_TRANG = ("(async()=>{const t=document.body.innerText.replace(/\\s+/g,' ').trim();"
                  "const h=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(t));"
                  "return {tieu_de:document.title,so_ky_tu:t.length,"
                  "sha256:[...new Uint8Array(h)].map(b=>b.toString(16).padStart(2,'0')).join('')}})()")


def doi_khop_url(doi: str, url: str, muc: list[dict] | None, V) -> tuple[bool, str]:
    """ĐỐI CHIẾU --doi với --url (20/11/2026 — góp ý rà độc lập): có DOI thì hồ sơ khoá theo DOI, nên một DOI gõ nhầm sẽ ghi
    «đã đọc» cho NGUỒN KHÁC. Luật: DOI phải hợp lệ; URL dạng doi.org phải trỏ đúng DOI đó; còn lại DOI phải thuộc một mục apply
    không PMID trong dashboard, và nếu mục đó có URL thì URL nạp phải CÙNG MIỀN (hostname) với URL của mục. Mục mang DOI mà
    không có URL ⇒ không đối chiếu được miền, nhận."""
    k = V.khoa_nguon_chinh_thuc(doi, None)
    if k is None:
        return False, f"--doi «{doi}» không phải DOI hợp lệ (10.xxxx/…)"
    sp = urllib.parse.urlsplit(url)
    host = (sp.hostname or "").lower()
    if host in ("doi.org", "dx.doi.org"):
        k_url = V.khoa_nguon_chinh_thuc(urllib.parse.unquote(sp.path.lstrip("/")), None)
        return (True, "") if k_url == k else (False, f"URL doi.org trỏ DOI khác ({k_url or 'không hợp lệ'}) với --doi ({k})")
    cung = [m for m in (muc or []) if m.get("khoa") == k]
    if not cung:
        return False, f"{k} không thuộc mục apply không PMID nào trong dashboard — kiểm lại --doi"
    mien = {(urllib.parse.urlsplit(m["url"]).hostname or "").lower() for m in cung if m.get("url")}
    if mien and host not in mien:
        return False, f"URL ở miền {host}, khác miền URL của mục mang {k} ({', '.join(sorted(mien))}) — kiểm lại --doi/--url"
    return True, ""


def nap_trinh_duyet(kho: Path, url: str, tieu_de: str, so_ky_tu: int, sha256: str, *, ghi: bool, doi: str = "",
                    dieu_khoan: str | None = None, lan_fn=None, muc: list[dict] | None = None) -> tuple[int, str]:
    V = vd()
    if V.khoa_nguon_chinh_thuc(None, url) is None:
        return 1, "URL không hợp lệ (cần http/https)"
    if (doi or "").strip():
        host = (urllib.parse.urlsplit(url).hostname or "").lower()
        if muc is None and host not in ("doi.org", "dx.doi.org"):
            muc = quet_muc(chon_dashboard(True), V)
        ok, ly = doi_khop_url(doi, url, muc, V)
        if not ok:
            return 1, f"từ chối — {ly}"
    k = V.khoa_nguon_chinh_thuc(doi, url)            # có DOI ⇒ khoá theo DOI (khớp khoá của mục trong dashboard)
    lan = (lan_fn or (lambda u, d: lan_doc(u, d, V=V)))(url, doi)
    if lan["lan"] == "bac_si":
        return 1, f"từ chối — {lan['ly_do']}"
    if lan["can_dieu_khoan"] and len((dieu_khoan or "").strip()) < 15:
        return 1, ("từ chối — NXB/miền chưa kiểm điều khoản: đọc trang điều khoản trước rồi khai --dieu-khoan \"<cho phép rõ "
                   "/ giấy phép CC của trang / cơ quan nhà nước…>\" (≥ 15 ký tự)")
    if _TIEU_DE_CHAN.search(tieu_de or "") or not (tieu_de or "").strip():
        return 1, f"tiêu đề rỗng hoặc là trang chặn/lỗi («{tieu_de[:60]}») — trang thật chưa hiện, không ghi"
    if so_ky_tu < V.SO_KY_TU_TOI_THIEU_NGUON:
        return 1, f"chữ thân trang quá ngắn ({so_ky_tu} < {V.SO_KY_TU_TOI_THIEU_NGUON})"
    if not re.fullmatch(r"[0-9a-f]{64}", sha256 or ""):
        return 1, "sha256 phải là 64 ký tự hex tính trong trang (xem `huong-dan`)"
    hs = {"khoa": k, "url": url, "url_cuoi": url, "tieu_de": tieu_de.strip(), "cach": "trinh_duyet", "so_ky_tu": so_ky_tu,
          "sha256": sha256, "ban_sao": False, "luc": dt.datetime.now().isoformat(timespec="seconds"), "lan": lan["ly_do"]}
    if dieu_khoan:
        hs["dieu_khoan"] = dieu_khoan.strip()
    if not ghi:
        return 0, f"(chạy khô) sẽ ghi bằng chứng làn trình duyệt cho {k}"
    return 0, f"✓ đã ghi {ghi_ho_so(kho, hs)}"


def bac_si_da_doc(kho: Path, nguon: str, ghi_chu: str | None, *, ghi: bool) -> tuple[int, str]:
    V = vd()
    n = (nguon or "").strip()
    k = n if re.match(r"^(?:doi:10\.|url:https?://)", n) else (V.khoa_nguon_chinh_thuc(n, None) or V.khoa_nguon_chinh_thuc(None, n))
    if k is None:
        return 1, "nguồn phải là DOI (10.xxxx/…) hoặc URL http(s)"
    if not ghi_chu or len(ghi_chu.strip()) < 10:
        return 1, "cần --ghi-chu là KẾT LUẬN của bác sĩ sau khi đọc (≥ 10 ký tự) — agent không tự điền"
    dong = {"nguon": k, "ghi_chu": ghi_chu.strip(), "luc": dt.datetime.now().isoformat(timespec="seconds")}
    if not ghi:
        return 0, f"(chạy khô) sẽ ghi «bác sĩ đã đọc» cho {k}"
    tep = kho / "trinh_duyet" / "bac-si-da-doc.jsonl"
    tep.parent.mkdir(parents=True, exist_ok=True)
    with tep.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(dong, ensure_ascii=False) + "\n")
    return 0, f"✓ đã ghi «bác sĩ đã đọc» cho {k} → {tep}"


def huong_dan() -> str:
    return "\n".join([
        "LÀN TRÌNH DUYỆT — nguồn chính thức máy không tải được (FDA/EMA chặn truy cập tự động, trang chặn bot, trang ngắn):",
        "  1. Claude mở URL trong khung trình duyệt; trang chặn bot («I am not a bot», CAPTCHA) thì BÁC SĨ tự bấm.",
        "  2. Trang thật hiện ra ⇒ chạy đoạn mã sau trong trang (javascript) để lấy tiêu đề, độ dài, sha256 của chữ thân trang:",
        "     " + MA_TRONG_TRANG,
        "  0. TRƯỚC KHI MỞ: điều khoản NXB (doctrine _CONNECTOR-CHUNG-CU.md §2septies). NXB «cấm» chưa uỷ quyền ⇒ KHÔNG mở,",
        "     bác sĩ đọc trực tiếp; NXB/miền chưa kiểm ⇒ đọc trang điều khoản trước, nạp kèm --dieu-khoan.",
        "  3. python3 tools/doc_nguon_chinh_thuc.py nap-trinh-duyet --url URL [--doi DOI] --tieu-de \"…\" --so-ky-tu N \\",
        "        --sha256 HEX [--dieu-khoan \"<căn cứ>\"] --ghi",
        "Bác sĩ đã tự đọc nguồn: bac-si-da-doc --nguon \"<DOI|URL>\" --ghi-chu \"<kết luận của bác sĩ>\" --ghi",
    ])


# ───────────────────────── sổ nợ (bánh cóc) ─────────────────────────

TEN_SO_NO = "no-nguon-chinh-thuc-apply.json"        # trùng verify_dashboard.TEN_SO_NO_NGUON (test chốt)
CAN_CU_MIN = 20
HAN_TOI_DA_NGAY = 90


def doc_so_no(dash: Path) -> dict | None:
    """Sổ nợ nguồn chính thức; vắng ⇒ None; hỏng ⇒ {"hong": lý do} (cổng coi như vắng — fail-closed)."""
    tep = Path(dash) / TEN_SO_NO
    if not tep.exists():
        return None
    try:
        d = json.loads(tep.read_text(encoding="utf-8"))
        dt.date.fromisoformat(d["han"])
        if not isinstance(d.get("muc"), list):
            raise ValueError("muc không phải danh sách")
        return d
    except (OSError, ValueError, KeyError, TypeError) as e:
        return {"hong": f"{type(e).__name__}: {e}"}


def phan_loai_no(muc: list[dict], co: set, so_no: dict | None, hom_nay: dt.date) -> dict:
    """Mục apply không PMID mà CỔNG CHẶN hoặc cảnh báo: «khong_khoa» (không DOI/URL — chặn) · «ngoai_so» (chặn) · «qua_han»
    (chặn) · «trong_han» (cảnh báo). Cùng định nghĩa với `verify_dashboard.kiem_doc_nguon_chinh_thuc_apply`."""
    khoa_no, han = set(), None
    if so_no and "hong" not in so_no:
        han = dt.date.fromisoformat(so_no["han"])
        khoa_no = {(x.get("dashboard"), x.get("item"), x.get("khoa")) for x in so_no["muc"] if isinstance(x, dict)}
    ra = {"khong_khoa": [], "ngoai_so": [], "qua_han": [], "trong_han": [], "han": han.isoformat() if han else None}
    for m in muc:
        if not m["khoa"]:
            ra["khong_khoa"].append(m)
        elif m["khoa"] in co:
            continue
        elif (m["dashboard"], m["item"], m["khoa"]) in khoa_no:
            ra["trong_han" if hom_nay <= han else "qua_han"].append(m)
        else:
            ra["ngoai_so"].append(m)
    return ra


def ghi_so_no(dash: Path, muc_no: list[dict], han: str, can_cu: str, *, ghi: bool, cu: dict | None,
              hom_nay: dt.date) -> tuple[int, str]:
    """Lập sổ nợ (CHỈ khi chưa có) hoặc gia hạn (giữ nguyên danh sách — bánh cóc). Mặc định chạy khô."""
    if len((can_cu or "").strip()) < CAN_CU_MIN:
        return 3, f"✗ phải ghi NGUYÊN VĂN lời bác sĩ (≥ {CAN_CU_MIN} ký tự) — agent không tự lập/gia hạn sổ nợ"
    try:
        h = dt.date.fromisoformat(han or "")
    except ValueError:
        return 3, f"✗ hạn «{han}» sai dạng YYYY-MM-DD"
    if not (hom_nay < h <= hom_nay + dt.timedelta(days=HAN_TOI_DA_NGAY)):
        return 3, f"✗ hạn phải sau hôm nay và không quá {HAN_TOI_DA_NGAY} ngày"
    luc = dt.datetime.now().isoformat(timespec="seconds")
    if cu is None:
        so = {"_about": "Sổ NỢ nguồn chính thức (bánh cóc): mục apply KHÔNG PMID mà nguồn (DOI/URL) CHƯA có bằng chứng đã đọc, đã "
                        "tồn lúc cổng chuyển sang CHẶN (20/11/2026). Cổng chỉ cảnh báo các mục này tới «han»; quá hạn ⇒ CHẶN. "
                        "Đổi URL/DOI của mục là nguồn MỚI — không còn được nợ. Mục mới KHÔNG bao giờ được thêm vào. Sinh bằng "
                        "tools/doc_nguon_chinh_thuc.py so-no — không sửa tay.",
              "tao_luc": luc, "han": h.isoformat(), "can_cu": can_cu.strip(),
              "muc": [{"dashboard": m["dashboard"], "item": m["item"], "khoa": m["khoa"]} for m in muc_no], "lich_su": []}
        viec = f"lập sổ nợ {len(muc_no)} mục ({len({m['khoa'] for m in muc_no})} nguồn), hạn {h.isoformat()}"
    else:
        if "hong" in cu:
            return 3, "✗ sổ nợ hiện có KHÔNG đọc được — không gia hạn đè lên sổ hỏng; bác sĩ xem tệp trước"
        so = dict(cu)
        so.setdefault("lich_su", []).append({"luc": luc, "han_cu": cu["han"], "han_moi": h.isoformat(),
                                             "can_cu": can_cu.strip()})
        so["han"] = h.isoformat()
        viec = f"gia hạn {cu['han']} → {h.isoformat()} (danh sách giữ nguyên {len(cu['muc'])} mục)"
    if not ghi:
        return 0, f"(chạy khô) sẽ {viec} — thêm --ghi để ghi {TEN_SO_NO}"
    (Path(dash) / TEN_SO_NO).write_text(json.dumps(so, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    return 0, f"✓ đã {viec} → {Path(dash) / TEN_SO_NO}"


def bao_cao_so_no(no: dict, so_no: dict | None, hom_nay: dt.date) -> list[str]:
    ten = lambda m: f"{m['dashboard'].replace('WebDashboard_EBM_VanDeCuThe_', '')} {m['item']}"  # noqa: E731
    dong = [f"SỔ NỢ ĐỌC NGUỒN CHÍNH THỨC (mục apply không PMID) — {hom_nay.isoformat()}"]
    if so_no and "hong" in so_no:
        dong.append(f"🔴 SỔ NỢ KHÔNG ĐỌC ĐƯỢC ({so_no['hong']}) — cổng coi như KHÔNG có sổ ⇒ mọi mục chưa đọc đều bị CHẶN.")
    for k, nhan in (("khong_khoa", "không có DOI/URL hợp lệ — cổng ĐANG CHẶN"),
                    ("ngoai_so", "nguồn chưa đọc, NGOÀI sổ nợ — cổng ĐANG CHẶN"),
                    ("qua_han", f"NỢ QUÁ HẠN {no['han']} — cổng ĐANG CHẶN")):
        if no[k]:
            dong.append(f"🔴 {len(no[k])} mục {nhan}:")
            dong += [f"     · {ten(m)}  {m['khoa'] or '(không khoá)'}" for m in no[k]]
    if no["trong_han"]:
        con = (dt.date.fromisoformat(no["han"]) - hom_nay).days
        dong.append(f"🟠 {len(no['trong_han'])} mục NỢ nguồn chính thức (hạn {no['han']}, còn {con} ngày — sau hạn cổng CHẶN):")
        dong += [f"     · {ten(m)}  {m['khoa']}" for m in no["trong_han"]]
    if not any(no[k] for k in ("khong_khoa", "ngoai_so", "qua_han", "trong_han")):
        dong.append("🟢 Mọi mục «Áp dụng ngay» không PMID đã có bằng chứng đọc nguồn chính thức.")
    else:
        dong += ["Trả nợ: máy tải `tai --tat-ca --ghi` · làn trình duyệt `huong-dan` · bác sĩ đã tự đọc `bac-si-da-doc --nguon "
                 "\"<DOI|URL>\" --ghi-chu \"<kết luận>\" --ghi` · hoặc bác sĩ hạ mục xuống «Cân nhắc»."]
    return dong + ["Cần bác sĩ kiểm chứng."]


# ───────────────────────── CLI ─────────────────────────

def _lenh_so_no(a, kho: Path, dashboards: list[Path] | None, V, hom_nay: dt.date | None = None) -> int:
    """Sổ nợ đo trên MỌI bản dashboard (cổng chạy trên bất kỳ bản nào được xuất lại, không chỉ bản mới nhất)."""
    hom_nay = hom_nay or dt.date.today()
    dash = kho.parent
    muc = quet_muc(dashboards if dashboards is not None else chon_dashboard(True), V)
    co = V.bang_chung_nguon_chinh_thuc(kho)
    so_no = doc_so_no(dash)
    if a.tao or a.gia_han:
        if a.tao and so_no is not None:
            print("✗ ĐÃ có sổ nợ — sổ chỉ được lập MỘT lần (bánh cóc: mục mới không vào nợ). Gia hạn: --gia-han.")
            return 3
        if a.gia_han and so_no is None:
            print("✗ chưa có sổ nợ để gia hạn — lập bằng --tao trước")
            return 3
        muc_no = [m for m in muc if m["khoa"] and m["khoa"] not in co]
        ma, tb = ghi_so_no(dash, muc_no, a.han if a.tao else a.gia_han, a.can_cu or "", ghi=a.ghi,
                           cu=so_no if a.gia_han else None, hom_nay=hom_nay)
        print(tb)
        return ma
    no = phan_loai_no(muc, co, so_no, hom_nay)
    if a.json:
        print(json.dumps({"ngay": hom_nay.isoformat(), "han": no["han"],
                          "dem": {k: len(no[k]) for k in ("khong_khoa", "ngoai_so", "qua_han", "trong_han")},
                          "muc": {k: no[k] for k in ("khong_khoa", "ngoai_so", "qua_han", "trong_han")}},
                         ensure_ascii=False, indent=1))
    else:
        print("\n".join(bao_cao_so_no(no, so_no, hom_nay)))
    return 1 if (no["khong_khoa"] or no["ngoai_so"] or no["qua_han"] or (so_no and "hong" in so_no)) else 0


def main(argv: list[str] | None = None, *, kho: Path | None = None, dashboards: list[Path] | None = None,
         tai_fn=tai_trang) -> int:
    ap = argparse.ArgumentParser(description="Đọc nguồn chính thức cho mục apply không PMID (chạy khô mặc định)")
    sub = ap.add_subparsers(dest="lenh", required=True)
    p = sub.add_parser("liet-ke")
    p.add_argument("--tat-ca", action="store_true", help="mọi bản dashboard (mặc định: bản ĐÃ PASS mới nhất mỗi chủ đề)")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("tai")
    p.add_argument("--tat-ca", action="store_true")
    p.add_argument("--ghi", action="store_true")
    p.add_argument("--toi-da", type=int)
    sub.add_parser("huong-dan")
    p = sub.add_parser("nap-trinh-duyet")
    p.add_argument("--url", required=True)
    p.add_argument("--doi", default="", help="DOI của mục (khoá nguồn theo DOI khi mục có DOI)")
    p.add_argument("--dieu-khoan", help="căn cứ điều khoản đã đọc (bắt buộc với NXB/miền chưa kiểm)")
    p.add_argument("--tieu-de", required=True)
    p.add_argument("--so-ky-tu", type=int, required=True)
    p.add_argument("--sha256", required=True)
    p.add_argument("--ghi", action="store_true")
    p = sub.add_parser("bac-si-da-doc")
    p.add_argument("--nguon", required=True)
    p.add_argument("--ghi-chu")
    p.add_argument("--ghi", action="store_true")
    p = sub.add_parser("so-no", help="sổ nợ của cổng chặn (mọi bản dashboard)")
    p.add_argument("--tao", action="store_true", help="lập sổ nợ cho mục đang chưa đọc (chỉ khi CHƯA có sổ)")
    p.add_argument("--gia-han", metavar="YYYY-MM-DD", help="gia hạn sổ nợ (danh sách giữ nguyên)")
    p.add_argument("--han", metavar="YYYY-MM-DD")
    p.add_argument("--can-cu", default=None, help="NGUYÊN VĂN lời bác sĩ")
    p.add_argument("--json", action="store_true")
    p.add_argument("--ghi", action="store_true")
    a = ap.parse_args(argv)
    kho = kho or kho_mac_dinh()
    if a.lenh == "huong-dan":
        print(huong_dan())
        return 0
    if a.lenh == "nap-trinh-duyet":
        ma, tb = nap_trinh_duyet(kho, a.url, a.tieu_de, a.so_ky_tu, a.sha256, ghi=a.ghi, doi=a.doi, dieu_khoan=a.dieu_khoan)
        print(tb)
        return ma
    if a.lenh == "bac-si-da-doc":
        ma, tb = bac_si_da_doc(kho, a.nguon, a.ghi_chu, ghi=a.ghi)
        print(tb)
        return ma
    if not kho.is_dir():
        print(f"⚪ không thấy kho toàn văn {kho} — không đo được")
        return 2
    V = vd()
    if a.lenh == "so-no":
        return _lenh_so_no(a, kho, dashboards, V)
    dashboards = dashboards if dashboards is not None else chon_dashboard(a.tat_ca)
    muc = quet_muc(dashboards, V)
    nhom = nhom_theo_khoa(muc, V.bang_chung_nguon_chinh_thuc(kho))
    khong_khoa = [m for m in muc if not m["khoa"]]
    if a.lenh == "liet-ke":
        da = sum(1 for x in nhom.values() if x["da_doc"])
        if a.json:
            print(json.dumps({"so_muc": len(muc), "so_nguon": len(nhom), "da_doc": da, "khong_khoa": len(khong_khoa),
                              "nguon": list(nhom.values())}, ensure_ascii=False, indent=1))
        else:
            print(f"Nguồn chính thức của mục apply không PMID: {len(muc)} mục · {len(nhom)} nguồn · {da} đã có bằng chứng đọc"
                  + (f" · {len(khong_khoa)} mục không truy nguyên được" if khong_khoa else ""))
            ky = {"may": "máy", "trinh_duyet": "trình duyệt", "bac_si": "bác sĩ"}
            dem: dict[str, int] = {}
            for x in sorted(nhom.values(), key=lambda x: (x["da_doc"], x["khoa"])):
                u = x["url"] or (("https://doi.org/" + x["khoa"][4:]) if x["khoa"].startswith("doi:") else "")
                ln = "" if x["da_doc"] else lan_doc(u, x["doi"], V=V)["lan"]
                dem[ln] = dem.get(ln, 0) + (0 if x["da_doc"] else 1)
                print(f"  {'✓' if x['da_doc'] else '·'} [{ky.get(ln, 'đã đọc')}] {x['khoa'][:100]}  ({len(x['muc'])} mục)")
            print("  Làn của nguồn chưa đọc: " + " · ".join(f"{ky[k]} {v}" for k, v in dem.items() if k))
        return 0 if da == len(nhom) and not khong_khoa else 1
    kq = tai(nhom, kho, ghi=a.ghi, toi_da=a.toi_da, tai_fn=tai_fn)
    print(f"{'' if a.ghi else '(chạy khô) '}tải được {len(kq['doc_duoc'])} · cần làn trình duyệt {len(set(kq['trinh_duyet']))}"
          f" · bác sĩ đọc trực tiếp {len(kq['bac_si'])} · từ chối {len(kq['tu_choi'])}")
    for k, ly_do in kq["tu_choi"]:
        print(f"  ✗ {k[:100]} — {ly_do}")
    for k, ly_do in kq["bac_si"]:
        print(f"  👤 {k[:100]} — {ly_do}")
    if kq["trinh_duyet"]:
        print("  → làn trình duyệt: python3 tools/doc_nguon_chinh_thuc.py huong-dan")
    if not a.ghi and kq["doc_duoc"]:
        print("  thêm --ghi để ghi bằng chứng")
    return 0 if not kq["trinh_duyet"] and not kq["tu_choi"] and not kq["bac_si"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
