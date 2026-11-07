#!/usr/bin/env python3
"""Canh RÚT BÀI cho TOÀN thư viện EndNote — đối chiếu mọi PMID/DOI với Retraction Watch ngoại tuyến (07/11/2026, bác sĩ giao).

Bác sĩ 07/11/2026 chọn «Làm 1 và 2» trong đề xuất hệ chứng cứ ↔ EndNote; mục 1 = canh rút bài cho toàn thư viện. Vì sao cần:
cổng `verify_dashboard` và tác vụ lịch `kiem-rut-bai-kho-thang` chỉ tái kiểm trích dẫn CỦA DASHBOARD; bản ghi đã nằm trong
EndNote (bác sĩ tự nhập, trích dẫn đề tài, câu hỏi AskTrip…) thì không ai đối chiếu lại. Đo 07/11/2026: 3.586 bản ghi, 3.375 có
PMID/DOI, 211 không có định danh; nền Retraction Watch trên máy 48 ngày tuổi (hạn 30) — không tác vụ nào làm mới khi quá hạn.

Luật (dùng ĐÚNG chỉ mục của engine `app/sources/retraction_watch.RetractionWatchIndex`, không tự phân loại lại):
  • «Retraction» ⇒ ĐÃ RÚT ⇒ bản ghi cần tag `TAG_RUT_BAI` và KHÔNG còn đạt «★ Áp dụng – tin cậy cao» (`gan_tag_endnote` tính).
  • «Expression of concern» ⇒ báo riêng (🟠), không gắn tag.
  • Correction/Erratum không tính; bài được PHỤC HỒI (Reinstatement) ⇒ chỉ mục trả «không biết» — không bao giờ «đã rút».
  • Không thấy trong Retraction Watch = «chưa thấy trong danh mục ngày <tải về>», KHÔNG BAO GIỜ là «chưa bị rút» (bài rất mới
    có thể chưa vào danh mục; nguồn sống PubMed/Europe PMC là tầng sau của chuỗi 3 tầng, công cụ này không gọi mạng).
  • Nền vắng/hỏng ⇒ «không đo được» (mã 2); nền quá hạn 30 ngày ⇒ vẫn đối chiếu nhưng báo 🟡 và mã 2 — làm mới bằng
    `python3 medical-ebm-automation/tools/tai_retraction_watch.py` (tác vụ `kiem-rut-bai-kho-thang` chạy việc này hằng tháng).

Chỉ ĐỌC `sdb.eni` (chế độ chỉ-đọc) và CSV trên đĩa; không ghi gì, không gọi mạng. Gắn tag là việc của `gan_tag_endnote.py`
(kéo-thả qua giao diện). Agent KHÔNG ký sổ rút bài, KHÔNG xoá bản ghi — bác sĩ xem.

Lệnh:
  python3 tools/kiem_rut_bai_endnote.py          # báo cáo
  python3 tools/kiem_rut_bai_endnote.py --json
Mã thoát: 0 không thấy bài rút/EoC và nền còn hạn · 1 có bài ĐÃ RÚT hoặc EoC · 2 không đo được hoặc nền quá hạn · 3 tham số sai.
Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sqlite3
import sys
from collections.abc import Callable
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
TAG_RUT_BAI = "⛔ Đã rút bài"
HAN_NGAY = 30  # khớp `tai_retraction_watch.HAN_NGAY` — danh mục rút bài phải làm mới hằng tháng
LENH_LAM_MOI = "python3 medical-ebm-automation/tools/tai_retraction_watch.py"
MA_OK, MA_CO_RUT, MA_KHONG_DO, MA_THAM_SO = 0, 1, 2, 3
_PMID = re.compile(r"\d{1,9}")


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, Path(__file__).resolve().parent / tep)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


# ───────────────────────── luật (thuần, test được) ─────────────────────────

def dinh_danh(acc: str | None, erd: str | None) -> tuple[str | None, str | None]:
    """(PMID, DOI) từ Accession Number / Electronic Resource Number. Accession chữ (vd `EBM-TT:…`) KHÔNG phải PMID."""
    pmid = acc.strip() if acc and _PMID.fullmatch(acc.strip()) else None
    doi = (erd or "").strip() or None
    return pmid, doi if doi and "10." in doi else None


def phan_loai(ban_ghi: dict[int, dict], tra_pmid: Callable[[str], dict | None],
              tra_doi: Callable[[str], dict | None]) -> dict:
    """`ban_ghi` = {rec: {pmid, doi, tieu_de}} ⇒ {rut: [...], eoc: [...], khong_dinh_danh: [rec], da_kiem: n}.

    Tra PMID trước; PMID «không biết» (None) thì tra DOI — chỉ mục DOI phủ 33.294 dòng không có PMID (đo 26/09/2026)."""
    rut, eoc, khong = [], [], []
    for rec in sorted(ban_ghi):
        bg = ban_ghi[rec]
        pmid, doi = bg.get("pmid"), bg.get("doi")
        if not pmid and not doi:
            khong.append(rec)
            continue
        kq = (tra_pmid(pmid) if pmid else None) or (tra_doi(doi) if doi else None)
        if not kq:
            continue
        muc = {"rec": rec, "pmid": pmid, "doi": doi, "tieu_de": (bg.get("tieu_de") or "")[:120],
               "nature": kq.get("nature"), "ngay_rut": kq.get("retraction_date"), "ly_do": (kq.get("reason") or "")[:160]}
        if kq.get("status") == "retracted":
            rut.append(muc)
        elif kq.get("status") == "expression_of_concern":
            eoc.append(muc)
    return {"rut": rut, "eoc": eoc, "khong_dinh_danh": khong, "da_kiem": len(ban_ghi) - len(khong)}


# ───────────────────────── nền + thư viện thật (chỉ đọc) ─────────────────────────

def nap_chi_muc(goc: Path = GOC) -> tuple[object | None, str | None, float | None]:
    """(chỉ mục RetractionWatchIndex đã nạp | None, lý do khi None, tuổi ngày). Engine ở bố cục lồng hoặc anh em."""
    bst = _nap("_bst_rbe", "ban_sao_tran.py")
    mea = bst.duong_goc("medical-ebm-automation", goc) or (goc / "medical-ebm-automation")
    if not (mea / "app" / "sources" / "retraction_watch.py").is_file():
        return None, "không thấy repo y khoa (nền Retraction Watch)", None
    if str(mea) not in sys.path:
        sys.path.insert(0, str(mea))
    try:
        from app.sources.retraction_watch import RetractionWatchIndex  # noqa: PLC0415 — nạp trễ
    except Exception as e:  # noqa: BLE001 — engine hỏng ⇒ không đo được, không phải «sạch»
        return None, f"không nạp được engine: {type(e).__name__}", None
    idx = RetractionWatchIndex()
    if not idx.san_sang():
        return None, f"nền Retraction Watch vắng/rỗng — chạy `{LENH_LAM_MOI}`", idx.tuoi_ngay()
    return idx, None, idx.tuoi_ngay()


def doc_ban_ghi(kn: sqlite3.Connection) -> dict[int, dict]:
    ra = {}
    for rec, acc, erd, ti in kn.execute(
            "select id, accession_number, electronic_resource_number, title from refs where trash_state = 0"):
        pmid, doi = dinh_danh(acc, erd)
        ra[int(rec)] = {"pmid": pmid, "doi": doi, "tieu_de": ti or ""}
    return ra


def kiem_ban_ghi(ban_ghi: dict[int, dict], chi_muc=None) -> dict:
    """Đối chiếu một tập bản ghi đã đọc (dùng chung cho `gan_tag_endnote`). Không đo được ⇒ {"do_duoc": False, …}."""
    if chi_muc is None:
        chi_muc, ly_do, tuoi = nap_chi_muc()
        if chi_muc is None:
            return {"do_duoc": False, "ly_do": ly_do, "tuoi_ngay": tuoi}
    tuoi = chi_muc.tuoi_ngay()
    kq = phan_loai(ban_ghi, chi_muc.tra, chi_muc.tra_doi)
    kq.update(do_duoc=True, tuoi_ngay=tuoi, qua_han=tuoi is None or tuoi > HAN_NGAY, tong=len(ban_ghi))
    return kq


def kiem_thu_vien(thu_vien: Path | None = None) -> dict:
    try:
        sk = _nap("_sk_rbe", "endnote_suc_khoe.py")
        tv = Path(thu_vien) if thu_vien else sk.thu_vien_cau_hinh()
        if not tv or not Path(tv).is_file():
            return {"do_duoc": False, "ly_do": "chưa khai thư viện EndNote (~/.ebm-endnote.json) hoặc tệp .enl vắng"}
        kn = sk._ket_noi(Path(tv))
        try:
            ban_ghi = doc_ban_ghi(kn)
        finally:
            kn.close()
    except (OSError, sqlite3.Error, ValueError) as e:
        return {"do_duoc": False, "ly_do": f"{type(e).__name__}: {str(e)[:200]}"}
    kq = kiem_ban_ghi(ban_ghi)
    kq["thu_vien"] = str(tv)
    return kq


# ───────────────────────── in / lệnh ─────────────────────────

def dong_nen(kq: dict) -> str:
    """Một mệnh đề về nền: tuổi + hạn. Không đo được ⇒ ⚪ (không bao giờ «sạch»)."""
    if not kq.get("do_duoc"):
        return f"⚪ chưa kiểm rút bài: {kq.get('ly_do')}"
    tuoi = kq.get("tuoi_ngay")
    if kq.get("qua_han"):
        return (f"🟡 nền Retraction Watch {'không rõ tuổi' if tuoi is None else f'{tuoi:.0f} ngày tuổi'} (hạn {HAN_NGAY}) — "
                f"làm mới: `{LENH_LAM_MOI}`")
    return f"nền Retraction Watch {tuoi:.0f} ngày tuổi"


def tom_tat_mot_dong(kq: dict) -> str:
    if not kq.get("do_duoc"):
        return dong_nen(kq)
    phan = []
    if kq["rut"]:
        phan.append(f"🔴 {len(kq['rut'])} bản ghi ĐÃ RÚT (recNum {', '.join(str(m['rec']) for m in kq['rut'][:20])})")
    if kq["eoc"]:
        phan.append(f"🟠 {len(kq['eoc'])} bản ghi có Expression of concern")
    if not phan:
        phan.append(f"không thấy bài rút trong {kq['da_kiem']} bản ghi có PMID/DOI (chưa thấy trong danh mục ≠ chưa bị rút)")
    return " · ".join(phan + [dong_nen(kq), f"{len(kq['khong_dinh_danh'])} bản ghi không có PMID/DOI — không kiểm được"])


def in_bao_cao(kq: dict) -> None:
    if not kq.get("do_duoc"):
        print(dong_nen(kq))
        return
    print(f"Thư viện: {kq.get('thu_vien', '?')} — {kq['tong']} bản ghi ngoài thùng rác; {kq['da_kiem']} có PMID/DOI đã đối "
          f"chiếu; {len(kq['khong_dinh_danh'])} không có định danh (không kiểm được).")
    print(dong_nen(kq))
    for m in kq["rut"]:
        print(f"🔴 ĐÃ RÚT · recNum {m['rec']} · {m['pmid'] or m['doi']} · ngày rút {m['ngay_rut'] or '?'} · {m['tieu_de'][:90]}")
    for m in kq["eoc"]:
        print(f"🟠 Expression of concern · recNum {m['rec']} · {m['pmid'] or m['doi']} · {m['tieu_de'][:90]}")
    if kq["rut"]:
        print(f"   ⇒ Cần bác sĩ xem. Bản ghi rút cần tag «{TAG_RUT_BAI}» và mất «★ Áp dụng – tin cậy cao»: "
              "`python3 tools/gan_tag_endnote.py` rồi `--huong-dan`. Dashboard còn trích bài này ⇒ cổng verify_dashboard chặn;"
              " thông báo rút là bản đính chính ⇒ `python3 tools/mau_ky_rut_bai.py` (CHỈ bác sĩ ký).")
    if not kq["rut"] and not kq["eoc"]:
        print(f"✓ Không thấy bài rút/EoC trong {kq['da_kiem']} bản ghi có PMID/DOI — «chưa thấy trong danh mục» KHÔNG phải "
              "«chưa bị rút».")
    print("Cần bác sĩ kiểm chứng.")


def ma_thoat(kq: dict) -> int:
    if not kq.get("do_duoc"):
        return MA_KHONG_DO
    if kq["rut"] or kq["eoc"]:
        return MA_CO_RUT
    return MA_KHONG_DO if kq.get("qua_han") else MA_OK


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    kq = kiem_thu_vien()
    if a.json:
        print(json.dumps(kq, ensure_ascii=False, indent=1))
    else:
        in_bao_cao(kq)
    return ma_thoat(kq)


if __name__ == "__main__":
    sys.exit(main())
