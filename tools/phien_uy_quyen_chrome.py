#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PHIÊN UỶ QUYỀN CHROME — bác sĩ nói MỘT câu mỗi phiên, Claude đọc và LƯU bản sao toàn văn trong phiên đó (04/10/2026).

VÌ SAO CÓ. Làn trình duyệt có bác sĩ (`tools/doc_toan_van_co_nguoi.py`) hỏi bác sĩ cho TỪNG tệp trước khi lưu, nên một buổi
vượt chặn Cloudflare chỉ lưu được vài bài. Bác sĩ yêu cầu 04/10: «khi tôi đăng nhập làn Chrome thì uỷ quyền truy cập toàn văn và
tải trong phiên làm việc đó luôn», chọn LƯU «HTML thân bài + PDF nếu có», phiên kéo dài «đến khi bác sĩ nói "dừng"».

GIỚI HẠN — không mở rộng được bằng cờ:
  • Phiên chỉ mở bằng LỜI BÁC SĨ trong chat, cho TỪNG phiên (`--mo "<nguyên văn>"`). Agent KHÔNG suy uỷ quyền từ việc bác sĩ đã
    đăng nhập và KHÔNG tự mở phiên. Quyền tải là của phiên đó; hết ngày phiên tự đóng, phiên sau phải có lời mới.
  • Uỷ quyền đọc ngày 03/10 (`dieu-khoan-bac-si-uy-quyen.json`) ghi phạm vi «tóm tắt… KHÔNG lưu toàn văn». Lưu bản sao là phạm vi
    RỘNG HƠN ⇒ cần lời phiên này; và CHỈ áp cho NXB đã có uỷ quyền đọc còn hiệu lực. NXB chưa kiểm điều khoản ⇒ không lưu.
    Cơ sở dữ liệu (DynaMed/EBSCO, Scopus, Web of Science) KHÔNG BAO GIỜ thuộc phiên — điều khoản cấm dùng nội dung với AI.
  • Điều khoản nhà xuất bản KHÔNG đổi: tài khoản cá nhân cho phép đọc cá nhân; tải nhiều tự động có thể bị NXB khoá tài khoản.
    Trách nhiệm điều khoản thuộc bác sĩ. Vì vậy có TRẦN mỗi miền (TRAN_MOI_MIEN bài/phiên) và NHỊP (≥ NGHI_TOI_THIEU_GIAY giây
    giữa hai bài cùng miền) như một người đọc — không dùng cờ để tắt.
  • Claude KHÔNG bấm xác minh chống bot, KHÔNG giải CAPTCHA, KHÔNG gõ tài khoản/mật khẩu — bác sĩ tự làm trên trang.
  • Lưu CHỈ thân bài (`<article>`/`<main>`, bỏ đầu trang có thông tin tài khoản) và PDF của NXB; tệp ngoài git
    (`EBM-Dashboards/toan_van_oa/PMID-<n>_CHR.html|pdf`), dùng cá nhân, không phân phối lại. Hậu tố `_CHR` ≠ `_UPW` (OA): kho và
    bộ đọc sâu gắn nhãn «có bản quyền, KHÔNG phải OA».

QUY TRÌNH (Claude làm; bác sĩ chỉ vượt chặn/đăng nhập và nói câu uỷ quyền):
  1. Bác sĩ nói trong chat, ví dụ «uỷ quyền phiên: đọc và lưu toàn văn các bài trong phiếu» ⇒
     `python3 tools/phien_uy_quyen_chrome.py --mo "<nguyên văn lời bác sĩ>"`.
  2. Trước MỖI bài: `--kiem <PMID> --url <URL> [--doi <DOI>]` (mã 0 = được; 3 = dừng/đợi — đọc lý do).
  3. Trên tab, trong MỘT lần nạp trang: tạo Blob của thân bài (dòng đầu `<!-- ebm-phien:<mã phiên> pmid:<n> url:<URL> -->`);
     PDF của NXB (fetch cùng nguồn) NHÚNG vào chính tệp HTML đó dạng `<script type="application/pdf;base64" id="ebm-pdf">…`
     ⇒ mỗi bài chỉ MỘT lần tải. Đo 04/10: Chrome chặn lặng lẽ lần tải tự động thứ hai trên cùng trang và GHI NHỚ lệnh chặn cho
     miền; nạp lại trang để tải tiếp làm Cloudflare chặn lại (ahajournals). Rồi `--nhan <PMID> --tep <tệp> --url <URL>
     [--doi <DOI>]` (kiểm loại, cỡ, dấu phiên, không ghi đè; tách PDF nhúng ra `_CHR.pdf`; chuyển vào kho; nhật ký kèm SHA-256).
  4. `python3 tools/doc_sau_toan_van.py --pmid <PMID…>` sinh bản đọc sâu từ PDF `_CHR`.
  5. Bác sĩ nói «dừng» ⇒ `--dung`. `--trang-thai` xem phiên đang mở.
Mã thoát: 0 được/xong · 2 không đọc/ghi được tệp · 3 bị từ chối (ngoài phạm vi, hết phiên, quá trần, chưa đủ nhịp, tệp sai).
Cần bác sĩ kiểm chứng."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parent.parent
SO_PHIEN = REPO / "state" / "phien-uy-quyen-chrome.json"
KHO = REPO / "EBM-Dashboards" / "toan_van_oa"
HAU_TO = "_CHR"
TRAN_MOI_MIEN = 20            # bài (PMID khác nhau) mỗi miền trong một phiên
NGHI_TOI_THIEU_GIAY = 60      # giữa hai bài cùng miền
CAN_CU_MIN = 20               # ký tự tối thiểu của lời bác sĩ
CO_HTML = (5_000, 30_000_000)  # byte của HTML SAU KHI tách PDF nhúng (thân bài ngắn nhất … trần an toàn)
CO_TEP_TAI = 120_000_000       # trần tệp tải về (HTML + PDF nhúng base64)
CO_PDF = (20_000, 60_000_000)
# Cơ sở dữ liệu tra cứu — điều khoản cấm dùng nội dung với AI; KHÔNG BAO GIỜ thuộc phiên dù có uỷ quyền khác.
KHONG_BAO_GIO = ("EBSCO (DynaMed)", "Scopus (Elsevier)", "Clarivate (Web of Science)")
# Dấu giao diện tài khoản/đầu trang lọt vào tệp ⇒ từ chối (chỉ lưu thân bài).
_DAU_TAI_KHOAN = re.compile(r"\b(sign out|log ?out|my account|đăng xuất|tài khoản của tôi)\b", re.I)
_DAU_PHIEN = re.compile(r"<!--\s*ebm-phien:(?P<ma>[0-9A-Za-z_-]+)\s+pmid:(?P<pmid>\d{1,9})\b")
_PDF_NHUNG = re.compile(r'<script type="application/pdf;base64" id="ebm-pdf">(?P<b64>[A-Za-z0-9+/=\s]+)</script>')


def tach_pdf_nhung(van_ban: str) -> tuple[str, bytes | None, str]:
    """(HTML đã gỡ khối PDF nhúng, byte PDF | None, lý do lỗi). Khối nhúng hỏng/không phải PDF ⇒ lỗi (không im lặng bỏ)."""
    import base64
    import binascii
    m = _PDF_NHUNG.search(van_ban)
    if not m:
        if '<script type="application/pdf;base64" id="ebm-pdf">' in van_ban:
            return van_ban, None, "khối PDF nhúng hỏng (có thẻ mở nhưng nội dung không phải base64/thiếu thẻ đóng)"
        return van_ban, None, ""
    try:
        pdf = base64.b64decode(re.sub(r"\s+", "", m.group("b64")), validate=True)
    except (binascii.Error, ValueError):
        return van_ban, None, "khối PDF nhúng không phải base64 hợp lệ"
    if not pdf.startswith(b"%PDF-") or not CO_PDF[0] <= len(pdf) <= CO_PDF[1]:
        return van_ban, None, f"khối nhúng không phải PDF hợp lệ ({len(pdf)} byte)"
    return van_ban[:m.start()] + van_ban[m.end():], pdf, ""


def _nap_dtv():
    sp = importlib.util.spec_from_file_location("_dtv_phien", Path(__file__).resolve().parent / "doc_toan_van_co_nguoi.py")
    m = importlib.util.module_from_spec(sp)
    sys.modules[sp.name] = m
    sp.loader.exec_module(m)
    return m


def _bay_gio() -> datetime:
    return datetime.now().astimezone()


def doc_phien(tep: Path | None = None) -> dict | None:
    """Phiên trong sổ (mở hay đã đóng), hoặc None khi sổ vắng/hỏng — hỏng ⇒ None (fail-closed: không có phiên)."""
    try:
        d = json.loads((tep or SO_PHIEN).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return d if isinstance(d, dict) and d.get("ma") else None


def phien_mo(bay_gio: datetime | None = None, tep: Path | None = None) -> dict | None:
    """Phiên CÒN HIỆU LỰC: chưa đóng và mở trong CÙNG ngày (hết ngày tự đóng)."""
    d = doc_phien(tep)
    if not d or d.get("dong_luc"):
        return None
    bay_gio = bay_gio or _bay_gio()
    try:
        mo = datetime.fromisoformat(d["mo_luc"])
    except (KeyError, ValueError, TypeError):
        return None
    return d if mo.date() == bay_gio.date() and mo <= bay_gio else None


def _ghi(d: dict, tep: Path | None = None) -> None:
    tep = tep or SO_PHIEN
    tep.parent.mkdir(parents=True, exist_ok=True)
    tam = tep.with_name(tep.name + f".tam-{os.getpid()}")
    tam.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    os.replace(tam, tep)


def nxb_duoc_luu(dtv, hom_nay=None) -> list[str]:
    """NXB thuộc phạm vi lưu: có uỷ quyền đọc CÒN HIỆU LỰC (khoá «cam» của DIEU_KHOAN_NXB) và không thuộc KHONG_BAO_GIO."""
    return [ten for ten in dtv.DIEU_KHOAN_NXB if ten not in KHONG_BAO_GIO and dtv.uy_quyen_bac_si(ten, hom_nay)]


def mo(can_cu: str, *, bay_gio: datetime | None = None, tep: Path | None = None, dtv=None) -> tuple[int, str]:
    """Mở phiên bằng NGUYÊN VĂN lời bác sĩ. Đã có phiên mở cùng ngày ⇒ từ chối (đóng trước rồi mở lại)."""
    can_cu = (can_cu or "").strip()
    if len(can_cu) < CAN_CU_MIN:
        return 3, f"lời bác sĩ phải ghi NGUYÊN VĂN, ≥ {CAN_CU_MIN} ký tự — agent không tự mở phiên"
    bay_gio = bay_gio or _bay_gio()
    if phien_mo(bay_gio, tep):
        return 3, "đã có phiên đang mở hôm nay — `--dung` trước nếu muốn mở phiên mới"
    dtv = dtv or _nap_dtv()
    nxb = nxb_duoc_luu(dtv, bay_gio.date())
    if not nxb:
        return 3, "không NXB nào có uỷ quyền đọc còn hiệu lực — phiên không có gì để lưu (ghi uỷ quyền trước, đúng lời bác sĩ)"
    d = {"ma": bay_gio.strftime("%Y%m%d-%H%M%S"), "mo_luc": bay_gio.isoformat(timespec="seconds"), "can_cu": can_cu,
         "pham_vi": "đọc và LƯU bản sao (HTML thân bài + PDF của NXB) vào kho ngoài git, dùng cá nhân, không phân phối lại",
         "nxb": nxb, "tran_moi_mien": TRAN_MOI_MIEN, "nghi_toi_thieu_giay": NGHI_TOI_THIEU_GIAY,
         "ghi_chu": "Điều khoản NXB KHÔNG đổi — trách nhiệm thuộc bác sĩ. Hết ngày tự đóng; bác sĩ nói «dừng» ⇒ --dung.",
         "lich_su": []}
    _ghi(d, tep)
    return 0, f"đã mở phiên {d['ma']} — {len(nxb)} NXB: " + "; ".join(nxb)


def _mien(url: str) -> str:
    from urllib.parse import urlparse
    return (urlparse(url or "").hostname or "").lower()


def kiem(pmid: str, url: str, doi: str = "", *, bay_gio: datetime | None = None, tep: Path | None = None,
         dtv=None) -> tuple[int, str]:
    """Được đọc/lưu bài này NGAY BÂY GIỜ không: phiên mở · NXB trong phạm vi · chưa quá trần miền · đủ nhịp."""
    bay_gio = bay_gio or _bay_gio()
    d = phien_mo(bay_gio, tep)
    if not d:
        return 3, "không có phiên uỷ quyền đang mở hôm nay — bác sĩ nói câu uỷ quyền phiên rồi `--mo`"
    if not re.fullmatch(r"\d{1,9}", str(pmid or "")):
        return 3, "PMID sai dạng"
    dtv = dtv or _nap_dtv()
    ten, _dk = dtv.nxb_cua(doi=doi, url=url)
    if not ten or ten not in d["nxb"]:
        return 3, f"NXB của bài ({ten or 'chưa kiểm điều khoản'}) KHÔNG thuộc phạm vi phiên — đọc theo làn thường, không lưu"
    mien = _mien(url)
    if not mien:
        return 3, "thiếu URL trang bài"
    cua_mien = [x for x in d["lich_su"] if x.get("mien") == mien]
    if str(pmid) not in {x.get("pmid") for x in cua_mien} and len({x.get("pmid") for x in cua_mien}) >= d["tran_moi_mien"]:
        return 3, f"đã đủ {d['tran_moi_mien']} bài ở {mien} trong phiên này — dừng miền này (tránh bị NXB khoá tài khoản)"
    if cua_mien:
        cuoi = max(datetime.fromisoformat(x["luc"]) for x in cua_mien)
        con = d["nghi_toi_thieu_giay"] - (bay_gio - cuoi).total_seconds()
        if con > 0:
            return 3, f"chưa đủ nhịp ở {mien} — đợi thêm {int(con) + 1} giây"
    return 0, f"được — phiên {d['ma']}, {ten}, {mien}"


def kiem_tep(tep: Path, pmid: str, ma_phien: str) -> tuple[str | None, str]:
    """(loại 'html'|'pdf' | None, lý do). HTML phải mang dấu phiên ĐÚNG mã + PMID ở đầu tệp và không có giao diện tài khoản."""
    try:
        co = tep.stat().st_size
        dau = tep.read_bytes()[:4096]
    except OSError as e:
        return None, f"không đọc được tệp: {e}"
    if dau.startswith(b"%PDF-"):
        if not CO_PDF[0] <= co <= CO_PDF[1]:
            return None, f"PDF {co} byte ngoài khoảng {CO_PDF} — trang lỗi/bìa?"
        return "pdf", ""
    if co > CO_TEP_TAI:
        return None, f"tệp {co} byte vượt trần {CO_TEP_TAI}"
    try:
        van_ban = tep.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None, "không phải PDF cũng không phải HTML UTF-8"
    m = _DAU_PHIEN.search(van_ban[:2000])
    if not m or m.group("ma") != ma_phien or m.group("pmid") != str(pmid):
        return None, "HTML thiếu dấu phiên đúng (<!-- ebm-phien:<mã> pmid:<n> … -->) — tệp không do phiên này tạo"
    van_ban, _pdf, loi = tach_pdf_nhung(van_ban)
    if loi:
        return None, loi
    co = len(van_ban.encode("utf-8"))
    if not CO_HTML[0] <= co <= CO_HTML[1]:
        return None, f"HTML {co} byte ngoài khoảng {CO_HTML} — thân bài quá ngắn (chỉ tóm tắt/trang chặn?)"
    if _DAU_TAI_KHOAN.search(van_ban):
        return None, "HTML có giao diện tài khoản (Sign out/My account…) — chỉ lưu thân bài, bỏ đầu trang"
    return "html", ""


def nhan(pmid: str, tep: Path, url: str, doi: str = "", *, bay_gio: datetime | None = None, so: Path | None = None,
         kho: Path | None = None, dtv=None) -> tuple[int, str]:
    """Kiểm lại phạm vi + tệp ⇒ chuyển vào kho `PMID-<n>_CHR.<ext>` (không ghi đè) ⇒ ghi nhật ký phiên kèm SHA-256."""
    bay_gio = bay_gio or _bay_gio()
    d = phien_mo(bay_gio, so)
    if not d:
        return 3, "không có phiên uỷ quyền đang mở hôm nay"
    dtv = dtv or _nap_dtv()
    ma, ly_do = kiem(pmid, url, doi, bay_gio=bay_gio, tep=so, dtv=dtv)
    da_co = any(x.get("pmid") == str(pmid) and x.get("mien") == _mien(url) for x in d["lich_su"])
    if ma != 0 and not (da_co and "chưa đủ nhịp" in ly_do):
        return ma, ly_do                      # cùng bài (HTML rồi PDF) không phải đợi nhịp lần hai
    loai, ly = kiem_tep(tep, pmid, d["ma"])
    if not loai:
        return 3, ly
    kho = kho or KHO
    if loai == "pdf":
        cac_tep = {"pdf": tep.read_bytes()}
    else:
        html, pdf, _loi = tach_pdf_nhung(tep.read_text(encoding="utf-8"))
        cac_tep = {"html": html.encode("utf-8"), **({"pdf": pdf} if pdf else {})}
    dich = {k: kho / f"PMID-{pmid}{HAU_TO}.{k}" for k in cac_tep}
    co_san = [x.name for x in dich.values() if x.exists()]
    if co_san:
        return 3, f"kho đã có {', '.join(co_san)} — không ghi đè (xoá tay nếu thật sự muốn thay)"
    kho.mkdir(parents=True, exist_ok=True)
    tb = []
    for k, noi_dung in cac_tep.items():
        tam = dich[k].with_name(dich[k].name + f".tam-{os.getpid()}")
        try:
            tam.write_bytes(noi_dung)
            os.replace(tam, dich[k])
        except OSError as e:
            return 2, f"không ghi được {dich[k].name} vào kho: {e}"
        sha = hashlib.sha256(noi_dung).hexdigest()
        d["lich_su"].append({"luc": bay_gio.isoformat(timespec="seconds"), "pmid": str(pmid), "url": url, "doi": doi,
                             "mien": _mien(url), "tep": dich[k].name, "byte": len(noi_dung), "sha256": sha, "loai": k})
        tb.append(f"{dich[k].name} ({len(noi_dung)} byte, sha256 {sha[:16]}…)")
    _ghi(d, so)
    try:
        tep.unlink()                     # tệp tải về đã vào kho — không để bản sao thứ hai trong Downloads
    except OSError:
        pass
    return 0, f"đã lưu {' + '.join(tb)} — phiên {d['ma']}"


def dung(*, bay_gio: datetime | None = None, tep: Path | None = None) -> tuple[int, str]:
    d = doc_phien(tep)
    if not d or d.get("dong_luc"):
        return 0, "không có phiên đang mở"
    d["dong_luc"] = (bay_gio or _bay_gio()).isoformat(timespec="seconds")
    _ghi(d, tep)
    n = len({x["pmid"] for x in d["lich_su"]})
    return 0, f"đã đóng phiên {d['ma']} — {n} bài, {len(d['lich_su'])} tệp"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Phiên uỷ quyền Chrome: đọc và lưu toàn văn trong phiên bác sĩ đã nói")
    nhom = ap.add_mutually_exclusive_group(required=True)
    nhom.add_argument("--mo", metavar="LOI_BAC_SI", help="mở phiên bằng NGUYÊN VĂN lời bác sĩ trong chat")
    nhom.add_argument("--kiem", metavar="PMID")
    nhom.add_argument("--nhan", metavar="PMID")
    nhom.add_argument("--dung", action="store_true")
    nhom.add_argument("--trang-thai", action="store_true")
    ap.add_argument("--url", default="")
    ap.add_argument("--doi", default="")
    ap.add_argument("--tep", type=Path)
    a = ap.parse_args(argv)
    if a.mo is not None:
        ma, tb = mo(a.mo)
    elif a.kiem:
        ma, tb = kiem(a.kiem, a.url, a.doi)
    elif a.nhan:
        if not a.tep:
            print("✗ --nhan cần --tep")
            return 3
        ma, tb = nhan(a.nhan, a.tep, a.url, a.doi)
    elif a.dung:
        ma, tb = dung()
    else:
        d = phien_mo()
        if not d:
            print("Không có phiên uỷ quyền đang mở hôm nay.")
            return 0
        so_bai = len({x["pmid"] for x in d["lich_su"]})
        print(f"Phiên {d['ma']} mở {d['mo_luc']} — {len(d['nxb'])} NXB, {so_bai} bài, {len(d['lich_su'])} tệp. Lời bác sĩ: "
              f"«{d['can_cu'][:160]}»")
        return 0
    print(("✓ " if ma == 0 else "✗ ") + tb)
    return ma


if __name__ == "__main__":
    sys.exit(main())
