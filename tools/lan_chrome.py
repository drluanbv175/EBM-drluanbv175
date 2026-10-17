#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LÀN CHROME — đóng gói hai làn chạy qua Chrome thật của bác sĩ thành công cụ dùng lại được (17/10/2026).

VÌ SAO CÓ. Tới 17/10 làn toàn văn (`phien_uy_quyen_chrome.py`) chỉ mô tả quy trình bằng lời: hàm JavaScript dựng tệp, cách
lấy thân bài/PDF theo từng nhà xuất bản (ScienceDirect /pii/<PII>/pdfft, OUP silverchair, trang xem PDF của Cochrane…), dấu
«không có quyền» (OUP redirectedFrom=fulltext, Nature «Access options», LWW chuyển sang trang abstract Ovid), hàng chờ theo
ưu tiên và lệnh nhận tệp tải về đều nằm trong script TẠM của một phiên ⇒ phiên/máy khác phải dò lại từ đầu. Làn nguồn web hội
(ACC/AHA, WHO — urllib bị chặn bot) phải chạy tay, không có gì nhắc khi trạm cũ, và lượt quét urllib hằng tuần hạ trạm về
`degraded` ngay cả khi làn trình duyệt vừa nạp thành công.

LỆNH
  toan-van --pmid P --url URL [--doi D]   kiểm phiên (`--kiem`) rồi IN mã JS (bo_luu.js + lời gọi đã điền cấu hình miền) để dán
                                          vào javascript_tool; in luôn các bước kế (bấm nút đỏ · bước PDF · nhận tệp).
  pdf --pmid P [--kiem CHUỖI]             IN mã JS bước 2 cho NXB tách PDF sang trang riêng (đang đứng trên trang PDF).
  nhan --pmid P --url URL [--doi D]       nhận mọi tệp ~/Downloads/PMID-<P>_phien.* qua `phien_uy_quyen_chrome.py --nhan`.
  hang-cho [--mien HOST] [--json TỆP]     bài chưa có toàn văn từ phiếu xác thực, theo miền + ưu tiên (áp dụng → tham khảo),
                                          bỏ bài đã có trong kho / đã ghi «không có quyền» (90 ngày); cột: có cấu hình · trong
                                          phạm vi phiên.
  nguon [--cat SRC-xxx TỆP]               trạm nguồn cần trình duyệt: lần nạp cuối, quá hạn chưa, điều kiện (tắt VPN…).
                                          --cat: cắt ĐÚNG vùng danh sách guideline đã phát hành từ văn bản trang (get_page_text)
                                          rồi nạp qua `giam_sat_to_chuc.py --nap-van-ban` (17/10: nạp cả trang WHO sinh 71 ứng
                                          viên giả từ bảng guideline DỰ KIẾN).

GIỚI HẠN — giữ nguyên của làn: chỉ chạy trong phiên uỷ quyền đang mở; trần 20 bài/miền và nhịp 60 giây do `--kiem` quyết; KHÔNG
bấm xác minh chống bot, KHÔNG gõ mật khẩu; DynaMed/Scopus/WoS không bao giờ thuộc làn. Công cụ này chỉ IN mã và gọi các công cụ
gốc — mọi luật kiểm tệp (dấu phiên, cổng nội dung toàn văn, không ghi đè) vẫn nằm ở `--nhan`.
Mã thoát: 0 được/xong · 1 nguon: có trạm quá hạn · 2 không đo được/không có dữ liệu · 3 bị từ chối/thiếu cấu hình.
Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import tempfile
import time
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
THU_MUC = TOOLS / "lan_chrome"
CAU_HINH = THU_MUC / "cau_hinh.json"
BO_LUU = THU_MUC / "bo_luu.js"
TAI_VE = Path.home() / "Downloads"
CHO_MOI_LAN = 10          # giây — khoảng thử lại khi `--kiem` báo chưa đủ nhịp
UU_TIEN = {"apply": 0, "consider": 1, "notyet": 2, "tham_khao": 3}
TEN_UU_TIEN = ("áp dụng", "cân nhắc", "chưa đủ", "tham khảo")
MAU_TEMPLATE = re.compile(r"\{(\w+)\}")
MA_OK, MA_QUA_HAN, MA_KHONG_DO, MA_TU_CHOI = 0, 1, 2, 3


def _nap(ten: str):
    sp = importlib.util.spec_from_file_location(f"_lan_chrome_{ten}", TOOLS / f"{ten}.py")
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


# ───────────────────────── cấu hình ─────────────────────────

def doc_cau_hinh(tep: Path | None = None) -> dict:
    """Đọc + kiểm khuôn cấu hình. Sai khuôn ⇒ ValueError (không chạy với cấu hình hỏng)."""
    d = json.loads((tep or CAU_HINH).read_text(encoding="utf-8"))
    loi = kiem_cau_hinh(d)
    if loi:
        raise ValueError("cấu hình làn Chrome sai khuôn: " + "; ".join(loi))
    return d


def kiem_cau_hinh(d: dict) -> list[str]:
    """Lỗi khuôn: mỗi NXB có `mien` + `chon` + `kiem_lan_cuoi`; mẫu regex dịch được; khuôn chỉ dùng {doi}/{pii}; mỗi trạm nguồn hoặc
    đủ (url, dong_dau, dong_cuoi, chu_ky_ngay) — làn đang chạy — hoặc khai `dieu_kien` (chưa chạy được, nói rõ vì sao)."""
    loi: list[str] = []
    for host, dich in (d.get("chuyen_huong") or {}).items():
        if dich not in (d.get("nxb") or {}):
            loi.append(f"chuyen_huong.{host}: trỏ tới «{dich}» không có trong nxb")
    for mau in d.get("dau_khong_quyen_url", []):
        try:
            re.compile(mau)
        except re.error as e:
            loi.append(f"dau_khong_quyen_url «{mau}»: {e}")
    for ten, c in (d.get("nxb") or {}).items():
        if not c.get("mien") or not c.get("chon"):
            loi.append(f"nxb.{ten}: thiếu mien/chon")
        if not c.get("kiem_lan_cuoi"):
            loi.append(f"nxb.{ten}: thiếu kiem_lan_cuoi — chỉ ghi cấu hình ĐÃ KIỂM THẬT")
        for k in ("khoa", "khoaTrang", "pdfXem"):
            if c.get(k):
                try:
                    re.compile(c[k])
                except re.error as e:
                    loi.append(f"nxb.{ten}.{k}: {e}")
        for k in ("pdf", "pdf2"):
            for bien in MAU_TEMPLATE.findall(str(c.get(k) or "")):
                if bien not in ("doi", "pii"):
                    loi.append(f"nxb.{ten}.{k}: biến lạ {{{bien}}}")
    for sid, c in (d.get("nguon") or {}).items():
        dang_chay = all(c.get(k) for k in ("url", "dong_dau", "dong_cuoi", "chu_ky_ngay"))
        if not dang_chay and not c.get("dieu_kien"):
            loi.append(f"nguon.{sid}: thiếu url/dong_dau/dong_cuoi/chu_ky_ngay mà cũng không khai dieu_kien")
        for k in ("dong_dau", "dong_cuoi"):
            if c.get(k):
                try:
                    re.compile(c[k])
                except re.error as e:
                    loi.append(f"nguon.{sid}.{k}: {e}")
    return loi


def tim_nxb(host: str, cau_hinh: dict) -> tuple[str, dict] | tuple[None, None]:
    """Cấu hình của miền: khớp đúng tên, hoặc mẫu «*.x» khớp mọi miền con của x."""
    host = (host or "").lower()
    for ten, c in (cau_hinh.get("nxb") or {}).items():
        for m in c["mien"]:
            m = m.lower()
            if host == m or (m.startswith("*.") and host.endswith(m[1:])):
                return ten, c
    return None, None


def dien_cau_hinh(c: dict, url: str, doi: str, dau_khong_quyen: list[str]) -> dict:
    """Cấu hình truyền cho `__ebmTai`: thay {doi}/{pii}; thiếu giá trị cần thiết ⇒ ValueError (không đoán)."""
    pii = (re.search(r"/pii/([A-Z0-9]+)", url or "", re.I) or [None, ""])[1]
    gia_tri = {"doi": (doi or "").strip(), "pii": pii}
    ra = {k: v for k, v in c.items() if k in ("chon", "khoa", "khoaTrang", "min", "pdf", "pdf2", "pdfXem", "khoaDeMuc")}
    for k in ("pdf", "pdf2"):
        if isinstance(ra.get(k), str):
            for bien in MAU_TEMPLATE.findall(ra[k]):
                if not gia_tri.get(bien):
                    raise ValueError(f"cấu hình cần {{{bien}}} cho «{k}» mà chưa có — " +
                                     ("truyền --doi" if bien == "doi" else "mở bài tới URL /pii/<PII> rồi truyền location.href"))
                ra[k] = ra[k].replace("{" + bien + "}", gia_tri[bien])
    ra["dauKhongQuyenUrl"] = list(dau_khong_quyen)
    return ra


def chuoi_kiem_pdf(c: dict, url: str, doi: str) -> str:
    """Chuỗi URL PDF phải chứa ở bước 2 — PII (ScienceDirect) hoặc hậu tố DOI (OUP: …/ehaf170.pdf)."""
    loai = c.get("kiem_pdf")
    if loai == "pii":
        return (re.search(r"/pii/([A-Z0-9]+)", url or "", re.I) or [None, ""])[1]
    if loai == "doi_cuoi" and doi:
        return doi.rstrip("/").split("/")[-1]
    return ""


def ma_js(lenh: str) -> str:
    """Mã dán vào javascript_tool: bộ lưu + đúng một lời gọi."""
    return BO_LUU.read_text(encoding="utf-8").rstrip() + "\n" + lenh + "\n"


# ───────────────────────── toàn văn ─────────────────────────

def _kiem_co_cho(phien, pmid: str, url: str, doi: str, cho: int) -> tuple[int, str]:
    """`--kiem`; chưa đủ nhịp thì đợi tối đa `cho` giây (thử lại mỗi CHO_MOI_LAN giây)."""
    het = time.monotonic() + max(0, cho)
    while True:
        ma, ly = phien.kiem(pmid, url, doi)
        if ma == 0 or "chưa đủ nhịp" not in ly or time.monotonic() >= het:
            return ma, ly
        time.sleep(CHO_MOI_LAN)


def lenh_toan_van(pmid: str, url: str, doi: str, cau_hinh_tay: str | None, cho: int, *, phien=None,
                  cau_hinh: dict | None = None) -> int:
    phien = phien or _nap("phien_uy_quyen_chrome")
    ma, ly = _kiem_co_cho(phien, pmid, url, doi, cho)
    print(f"{'✓' if ma == 0 else '✗'} {pmid}: {ly}")
    if ma != 0:
        return MA_TU_CHOI
    d = phien.phien_mo()
    if not d:
        print("✗ không đọc được phiên đang mở")
        return MA_TU_CHOI
    ch = cau_hinh or doc_cau_hinh()
    host = (urlparse(url).hostname or "").lower()
    if cau_hinh_tay:
        ten, c = "thủ công", json.loads(cau_hinh_tay)
    else:
        ten, c = tim_nxb(host, ch)
    if c is None and host in (ch.get("chuyen_huong") or {}):
        print(f"✗ {host} là miền CHUYỂN HƯỚNG của «{ch['chuyen_huong'][host]}» — mở URL, đợi trang bài tải xong rồi chạy lại với "
              "--url là location.href (miền thật của bài).")
        return MA_TU_CHOI
    if c is None:
        print(f"✗ chưa có cấu hình ĐÃ KIỂM cho miền {host} — xem trang rồi thử bằng --cau-hinh "
              "'{\"chon\": \"article\", \"min\": 12000, \"pdf\": \"meta\"}'; lưu được bài thật thì bổ sung "
              f"{CAU_HINH.relative_to(REPO)} kèm kiem_lan_cuoi.")
        return MA_TU_CHOI
    try:
        o = dien_cau_hinh(c, url, doi, ch.get("dau_khong_quyen_url", []))
    except ValueError as e:
        print(f"✗ {e}")
        return MA_TU_CHOI
    goi = (f"await window.__ebmTai({json.dumps(d['ma'])}, {json.dumps(str(pmid))}, {json.dumps(url)}, "
           f"{json.dumps(o, ensure_ascii=False)})")
    print(f"Cấu hình: {ten}" + (f" — {c['ghi_chu']}" if c.get("ghi_chu") else ""))
    print("───── MÃ JS — dán NGUYÊN khối vào javascript_tool trên tab bài (đã đợi trang tải xong) ─────")
    print(ma_js(goi), end="")
    print("───── HẾT MÃ ─────")
    kiem = chuoi_kiem_pdf(c, url, doi)
    print("Bước kế:\n"
          "  1. Kết quả ok:false ⇒ đọc «ly»: không quyền thì `python3 tools/doc_toan_van_co_nguoi.py --khong-truy-cap "
          f"{pmid} --ly-do \"…\"`; KHÔNG bấm gì.\n"
          "  2. ok:true ⇒ zoom vùng (0,0,400,150) thấy nút đỏ «EBM tải PMID …» rồi left_click (120,40).\n"
          + (f"  3. pdf2 có giá trị ⇒ điều hướng tới window.__pdf2, đợi trang PDF, rồi `python3 tools/lan_chrome.py pdf --pmid {pmid}"
             + (f" --kiem {kiem}" if kiem else "") + "` → dán mã → bấm nút.\n" if c.get("pdf2") else "")
          + f"  {'4' if c.get('pdf2') else '3'}. `python3 tools/lan_chrome.py nhan --pmid {pmid} --url {json.dumps(url)}"
          + (f" --doi {doi}" if doi else "") + "`")
    return MA_OK


def lenh_pdf(pmid: str, kiem: str) -> int:
    print("───── MÃ JS — dán vào javascript_tool khi tab ĐANG Ở trang PDF ─────")
    print(ma_js(f"await window.__ebmPdfNut({json.dumps(str(pmid))}, '', {json.dumps(kiem or '')})"), end="")
    print("───── HẾT MÃ ─────\nok:true ⇒ zoom (0,0,400,150) rồi left_click (120,40); sau đó `lan_chrome.py nhan`.")
    return MA_OK


def tep_tai_ve(pmid: str, thu_muc: Path) -> list[Path]:
    """Tệp tải về của bài: HTML trước, PDF sau; bỏ tệp Chrome đang tải dở (.crdownload)."""
    ds = [p for p in thu_muc.glob(f"PMID-{pmid}_phien*") if p.is_file() and not p.name.endswith(".crdownload")]
    return sorted(ds, key=lambda p: (p.suffix.lower() != ".html", p.name))


def lenh_nhan(pmid: str, url: str, doi: str, thu_muc: Path, *, phien=None) -> int:
    ds = tep_tai_ve(pmid, thu_muc)
    if not ds:
        print(f"✗ {pmid}: chưa thấy tệp PMID-{pmid}_phien.* trong {thu_muc} — đã bấm nút đỏ chưa?")
        return MA_KHONG_DO
    phien = phien or _nap("phien_uy_quyen_chrome")
    ma_cuoi = MA_OK
    for t in ds:
        argv = ["--nhan", str(pmid), "--tep", str(t), "--url", url] + (["--doi", doi] if doi else [])
        ma_cuoi = max(ma_cuoi, phien.main(argv) or 0)
    return ma_cuoi


# ───────────────────────── hàng chờ ─────────────────────────

_DONG_PHIEU = re.compile(r"^\| \d+ \| PMID (\d+) \| ✗[^|]*\| (.*)\|\s*$")
_URL_PHIEU = re.compile(r"mở (https?://\S+) trong Chrome")


def dung_hang_cho(phieu: list[str], co_trong_kho: set[str], khong_quyen: set[str], uu_tien: dict[str, int],
                  doi_cua: dict[str, str]) -> list[dict]:
    """Bài ✗ trong các phiếu (mỗi PMID một lần), trừ bài đã có trong kho / đã ghi không quyền; kèm miền + ưu tiên."""
    ra: dict[str, dict] = {}
    for van_ban in phieu:
        for dong in van_ban.splitlines():
            m = _DONG_PHIEU.match(dong)
            if not m or m.group(1) in co_trong_kho or m.group(1) in khong_quyen or m.group(1) in ra:
                continue
            u = _URL_PHIEU.search(m.group(2))
            url = u.group(1) if u else ""
            ra[m.group(1)] = {"pmid": m.group(1), "url": url, "doi": doi_cua.get(m.group(1), ""),
                              "mien": (urlparse(url).hostname or "").lower(), "uu_tien": uu_tien.get(m.group(1), 3),
                              "goi_y": m.group(2).strip()[:160]}
    return sorted(ra.values(), key=lambda x: (x["uu_tien"], x["mien"], x["pmid"]))


def _uu_tien_va_doi(dashboards: list[Path], doc) -> tuple[dict[str, int], dict[str, str]]:
    uu: dict[str, int] = {}
    doi: dict[str, str] = {}
    for f in dashboards:
        d = doc(f) or {}
        for it in d.get("items") or []:
            p = str(it.get("pmid") or "").strip()
            if p.isdigit():
                uu[p] = min(uu.get(p, 9), UU_TIEN.get(it.get("decision"), 3))
                if it.get("doi"):
                    doi.setdefault(p, str(it["doi"]).strip())
            for ref in it.get("references") or []:
                for m in re.finditer(r"PMID[:\s]*(\d{6,9})", str(ref)):
                    uu[m.group(1)] = min(uu.get(m.group(1), 9), 3)
    return uu, doi


def lenh_hang_cho(mien: str | None, ra_json: Path | None) -> int:
    phien = _nap("phien_uy_quyen_chrome")
    kho = phien.KHO
    dash = kho.parent
    if not kho.is_dir():
        print(f"⚪ KHÔNG ĐO ĐƯỢC — không thấy kho {kho}")
        return MA_KHONG_DO
    dtv = _nap("doc_toan_van_co_nguoi")
    co = {m.group(1) for p in kho.glob("PMID-*") if (m := re.match(r"PMID-(\d+)_", p.name))}
    khong = set(dtv._khong_truy_cap(kho, date.today()))
    phieu = [f.read_text(encoding="utf-8") for f in sorted((dash / "derivatives").glob("*_toan-van.md"))]
    nap = _nap("nap_endnote_chu_de")
    uu, doi = _uu_tien_va_doi(sorted(dash.glob("WebDashboard_*.html")), nap._nap_doc_data())
    ds = dung_hang_cho(phieu, co, khong, uu, doi)
    if mien:
        ds = [x for x in ds if x["mien"] == mien.lower()]
    ch = doc_cau_hinh()
    duoc = set(phien.nxb_duoc_luu(dtv, date.today()))
    theo: dict[str, list[dict]] = {}
    for x in ds:
        theo.setdefault(x["mien"] or "(không URL)", []).append(x)
    print(f"Hàng chờ làn Chrome — {len(ds)} bài chưa có toàn văn (đã trừ {len(co)} có trong kho, {len(khong)} ghi không quyền).")
    print(f"{'miền':34s} {'bài':>4s}  áp/cân/chưa/tk   cấu hình   phạm vi phiên")
    for host, nhom in sorted(theo.items(), key=lambda kv: (min(x["uu_tien"] for x in kv[1]), -len(kv[1]))):
        dem = [sum(1 for x in nhom if x["uu_tien"] == i) for i in range(4)]
        ten_nxb = dtv.nxb_cua(doi=nhom[0]["doi"], url=nhom[0]["url"])[0]
        cfg = tim_nxb(host, ch)[0] or ((ch.get("chuyen_huong") or {}).get(host, "") + " ↪" if host in (ch.get("chuyen_huong") or {})
                                       else "—")
        pv = "✓" if ten_nxb in duoc else ("✗ chưa kiểm điều khoản" if not ten_nxb else "✗ ngoài phạm vi")
        print(f"{host[:34]:34s} {len(nhom):4d}  {'/'.join(map(str, dem)):14s}   {cfg[:9]:9s}  {pv}")
    if ra_json:
        ra_json.write_text(json.dumps(ds, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"Đã ghi {ra_json}")
    return MA_OK


# ───────────────────────── nguồn web hội ─────────────────────────

def cat_vung(van_ban: str, c: dict) -> str | None:
    """Các dòng nằm GIỮA dòng khớp `dong_dau` và dòng khớp `dong_cuoi` (không gồm hai dòng mốc), bỏ dòng khớp `bo_dong`.
    Thiếu một trong hai mốc hoặc vùng rỗng ⇒ None: không đoán vùng (đoán sai là nạp cả bảng guideline DỰ KIẾN của WHO)."""
    dong = [x.strip() for x in van_ban.replace("\r", "\n").splitlines()]
    dau = next((i for i, x in enumerate(dong) if re.search(c["dong_dau"], x)), None)
    if dau is None:
        return None
    cuoi = next((i for i, x in enumerate(dong) if i > dau and re.search(c["dong_cuoi"], x)), None)
    if cuoi is None:
        return None
    bo = [re.compile(m) for m in c.get("bo_dong", [])]
    giu = [x for x in dong[dau + 1:cuoi] if x and not any(b.search(x) for b in bo)]
    return "\n".join(giu) + "\n" if giu else None


def trang_thai_nguon(c: dict, s: dict | None, hom_nay: date) -> tuple[str, str]:
    """(ký hiệu, mô tả) cho một trạm của làn nguồn: ⚪ điều kiện chưa đạt · 🛎 quá hạn/chưa nạp lần nào · 🟢 còn hạn."""
    if c.get("dieu_kien"):
        return "⚪", f"cần điều kiện «{c['dieu_kien']}» — {c.get('ghi_chu', '')}"
    lan = (s or {}).get("last_success_at")
    if not lan:
        return "🛎", "chưa nạp thành công lần nào"
    tuoi = (hom_nay - date.fromisoformat(lan)).days
    if tuoi > int(c["chu_ky_ngay"]):
        return "🛎", f"quá hạn: nạp cuối {lan} ({tuoi} ngày > chu kỳ {c['chu_ky_ngay']})"
    return "🟢", f"nạp cuối {lan} ({tuoi} ngày, chu kỳ {c['chu_ky_ngay']})"


def lenh_nguon(cat: list[str] | None, *, giam_sat=None, cau_hinh: dict | None = None, hom_nay: date | None = None) -> int:
    ch = cau_hinh or doc_cau_hinh()
    giam_sat = giam_sat or _nap("giam_sat_to_chuc")
    if cat:
        sid, tep = cat
        c = (ch.get("nguon") or {}).get(sid)
        if not c or c.get("dieu_kien") or not c.get("dong_dau"):
            print(f"✗ {sid}: chưa có vùng cắt đã kiểm trong {CAU_HINH.relative_to(REPO)}")
            return MA_TU_CHOI
        vung = cat_vung(Path(tep).read_text(encoding="utf-8"), c)
        if vung is None:
            print(f"✗ {sid}: không thấy đủ hai mốc vùng («{c['dong_dau']}» … «{c['dong_cuoi']}») — trang đổi bố cục? KHÔNG nạp.")
            return MA_KHONG_DO
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=f"_{sid}.txt", delete=False) as f:
            f.write(vung)
        print(f"Vùng cắt {sid}: {len(vung.splitlines())} dòng ⇒ nạp qua giam_sat_to_chuc --nap-van-ban")
        try:
            return giam_sat._nap_van_ban(sid, f.name)
        finally:
            Path(f.name).unlink(missing_ok=True)
    try:
        so = json.loads(giam_sat.SO_NGUON.read_text(encoding="utf-8"))["sources"]
    except (OSError, ValueError, KeyError) as e:
        print(f"⚪ KHÔNG ĐO ĐƯỢC — sổ nguồn: {e}")
        return MA_KHONG_DO
    theo_id = {s["id"]: s for s in so}
    hom_nay = hom_nay or date.today()
    qua_han = False
    print("Trạm nguồn cần trình duyệt (làn Chrome):")
    for sid, c in (ch.get("nguon") or {}).items():
        ky, mo_ta = trang_thai_nguon(c, theo_id.get(sid), hom_nay)
        qua_han |= ky == "🛎"
        print(f"  {ky} {sid} {c['ten']} — {mo_ta}")
        if ky == "🛎":
            print(f"     → mở {c['url']} trong Chrome · get_page_text · lưu văn bản ra tệp · "
                  f"`python3 tools/lan_chrome.py nguon --cat {sid} <tệp>`")
    return MA_QUA_HAN if qua_han else MA_OK


# ───────────────────────── main ─────────────────────────

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    sub = ap.add_subparsers(dest="lenh", required=True)
    p = sub.add_parser("toan-van")
    p.add_argument("--pmid", required=True)
    p.add_argument("--url", required=True, help="URL bài ĐANG mở (location.href sau chuyển hướng)")
    p.add_argument("--doi", default="")
    p.add_argument("--cau-hinh", default=None, help="JSON cấu hình thử cho miền CHƯA có trong cau_hinh.json")
    p.add_argument("--cho", type=int, default=100, help="đợi tối đa N giây khi chưa đủ nhịp (mặc định 100)")
    p = sub.add_parser("pdf")
    p.add_argument("--pmid", required=True)
    p.add_argument("--kiem", default="", help="chuỗi URL PDF phải chứa (PII / hậu tố DOI)")
    p = sub.add_parser("nhan")
    p.add_argument("--pmid", required=True)
    p.add_argument("--url", required=True)
    p.add_argument("--doi", default="")
    p.add_argument("--thu-muc", type=Path, default=TAI_VE)
    p = sub.add_parser("hang-cho")
    p.add_argument("--mien", default=None)
    p.add_argument("--json", type=Path, default=None)
    p = sub.add_parser("nguon")
    p.add_argument("--cat", nargs=2, metavar=("SRC", "TEP"), default=None)
    a = ap.parse_args(argv)
    if a.lenh == "toan-van":
        return lenh_toan_van(a.pmid, a.url, a.doi, a.cau_hinh, a.cho)
    if a.lenh == "pdf":
        return lenh_pdf(a.pmid, a.kiem)
    if a.lenh == "nhan":
        return lenh_nhan(a.pmid, a.url, a.doi, a.thu_muc)
    if a.lenh == "hang-cho":
        return lenh_hang_cho(a.mien, a.json)
    return lenh_nguon(a.cat)


if __name__ == "__main__":
    sys.exit(main())
