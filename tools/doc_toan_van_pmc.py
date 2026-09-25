#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ĐỌC TOÀN VĂN PMC THEO PMID / DOI / PMCID — cửa gọi cho agent (25/09/2026)

VÌ SAO CÓ
=========
`app/sources/pmc_guideline_fulltext.py` (engine) tải toàn văn PMC Open Access qua bucket S3
công khai của NCBI. Đường này chạy thật cả trên phiên Cloud (đo 24/09: SRC-046, 200.000 ký
tự), nơi phần lớn host API y văn bị proxy chặn. Nhưng connector chỉ nhận PMCID và không có
lệnh nào để agent gọi, nên agent `tra-cuu-chung-cu` / `cap-nhat-guideline` chỉ nhắc tới nó ở
nhánh «bị từ chối». Theo luật của hệ, một công cụ không ai gọi thì coi như không tồn tại.

Lệnh này: PMID/DOI → PMCID (NCBI E-utilities `elink`/`esearch`) → toàn văn (connector engine)
→ in đoạn chứa cụm cần tìm, kèm vị trí ký tự, để agent TRÍCH ĐÚNG câu chữ khuyến cáo.

RANH GIỚI
=========
* Chỉ bài trong PMC Open Access Subset mới có. «Không có trong PMC OA» là sự thật của nguồn;
  «không liệt kê/phân giải được» là CHƯA BIẾT — hai trạng thái không được gộp.
* Bản quyền: toàn văn CHỈ dùng làm tham chiếu nội bộ để trích câu chữ kèm PMID/DOI. Không
  đăng lại nguyên văn, không đưa toàn văn lên dashboard công khai.
* Tải được toàn văn KHÔNG có nghĩa bài chưa bị rút — kiểm rút bài qua chuỗi 3 tầng như thường.
* Cờ `ENABLE_PMC_GUIDELINE_FULLTEXT` của engine chỉ được bật TRONG TIẾN TRÌNH NÀY (gọi tay lệnh
  này = đồng ý dùng cho lượt này); không ghi vào tệp cấu hình.

Dùng:
    python3 tools/doc_toan_van_pmc.py PMC13555224 --tim "eGFR" --tim "recommend"
    python3 tools/doc_toan_van_pmc.py 38000000 --tim "SGLT2"       # PMID
    python3 tools/doc_toan_van_pmc.py 10.2337/dc26-S009 --json     # DOI
Mã thoát: 0 = đọc được toàn văn · 1 = nguồn KHÔNG có toàn văn PMC OA (sự thật của nguồn) ·
2 = chưa biết (không phân giải được định danh, lỗi mạng, thiếu engine). Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Callable

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
_EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
_MAU_PMCID = re.compile(r"^PMC\d+$", re.I)
_MAU_DOI = re.compile(r"^10\.\d{4,9}/\S+$")
_GIAN_DOAN = 220        # ký tự hai bên cụm tìm
_TOI_DA_DOAN = 5        # số đoạn tối đa mỗi cụm


class ChuaBiet(RuntimeError):
    """Không kết luận được (mạng/proxy/định dạng lạ) — khác «nguồn không có»."""


def _get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "EBM-Copilot/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except (urllib.error.URLError, OSError, ValueError) as exc:
        raise ChuaBiet(f"{type(exc).__name__}: {exc}") from exc


def phan_giai_pmcid(dinh_danh: str, get_json: Callable[[str], dict] = _get_json) -> str | None:
    """PMCID ('PMC…') hoặc None nếu nguồn CHẮC CHẮN không có bản PMC. Ném ChuaBiet khi không kết luận được."""
    d = dinh_danh.strip()
    if _MAU_PMCID.match(d):
        return d.upper()
    if d.isdigit():
        pmid = d
    elif _MAU_DOI.match(d):
        q = urllib.parse.quote(f"{d}[doi]")
        js = get_json(f"{_EUTILS}esearch.fcgi?db=pubmed&retmode=json&term={q}")
        ids = (js.get("esearchresult") or {}).get("idlist")
        if ids is None:
            raise ChuaBiet("esearch trả bố cục lạ")
        if not ids:
            return None
        pmid = ids[0]
    else:
        raise ChuaBiet(f"'{d}' không phải PMID, DOI hay PMCID")
    js = get_json(f"{_EUTILS}elink.fcgi?dbfrom=pubmed&db=pmc&retmode=json&id={pmid}")
    try:
        bo = js["linksets"][0]
    except (KeyError, IndexError, TypeError) as exc:
        raise ChuaBiet("elink trả bố cục lạ") from exc
    for db in bo.get("linksetdbs") or []:
        if db.get("linkname") == "pubmed_pmc" and db.get("links"):
            return f"PMC{db['links'][0]}"
    return None


def tim_doan(van_ban: str, cum: str, gian: int = _GIAN_DOAN, toi_da: int = _TOI_DA_DOAN) -> list[dict]:
    """[{vi_tri, doan}] — không phân biệt hoa thường; đoạn chồng lấn được gộp."""
    ra: list[dict] = []
    thap = van_ban.lower()
    c = cum.lower().strip()
    if not c:
        return ra
    i = thap.find(c)
    ket_thuc_truoc = -1
    while i != -1 and len(ra) < toi_da:
        a, b = max(0, i - gian), min(len(van_ban), i + len(c) + gian)
        if a > ket_thuc_truoc:
            ra.append({"vi_tri": i, "doan": re.sub(r"\s+", " ", van_ban[a:b]).strip()})
            ket_thuc_truoc = b
        i = thap.find(c, i + len(c))
    return ra


def _nap_client():
    """Connector của engine (repo y khoa lồng hoặc anh em). None nếu không tìm thấy engine."""
    sp = importlib.util.spec_from_file_location("_bst_dtvp", REPO / "tools" / "ban_sao_tran.py")
    bst = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(bst)
    goc = bst.duong_goc("medical-ebm-automation", REPO)
    if goc is None:
        return None
    if str(goc) not in sys.path:
        sys.path.insert(0, str(goc))
    from app.config import settings  # noqa: PLC0415
    from app.sources.pmc_guideline_fulltext import PmcGuidelineFullTextClient  # noqa: PLC0415
    settings.enable_pmc_guideline_fulltext = True   # chỉ trong tiến trình này, không ghi cấu hình
    return PmcGuidelineFullTextClient()


def main(argv: list[str] | None = None, client_factory=_nap_client,
         get_json: Callable[[str], dict] = _get_json) -> int:
    ap = argparse.ArgumentParser(description="Đọc toàn văn PMC OA theo PMID/DOI/PMCID (tham chiếu nội bộ)")
    ap.add_argument("dinh_danh", help="PMID, DOI hoặc PMCID")
    ap.add_argument("--tim", action="append", default=[], help="cụm cần tìm (lặp được)")
    ap.add_argument("--toan-bo", action="store_true", help="in toàn bộ văn bản (chỉ dùng nội bộ)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    kq: dict = {"dinh_danh": a.dinh_danh, "pmcid": None, "trang_thai": None, "ghi_chu": None}
    try:
        pmcid = phan_giai_pmcid(a.dinh_danh, get_json)
    except ChuaBiet as exc:
        kq.update(trang_thai="chua_biet", ghi_chu=f"Không phân giải được sang PMCID: {exc}")
        return _xuat(kq, a.json, 2)
    if pmcid is None:
        kq.update(trang_thai="khong_co", ghi_chu="Bài không có bản PMC (PubMed không liên kết PMC).")
        return _xuat(kq, a.json, 1)
    kq["pmcid"] = pmcid

    try:
        client = client_factory()
    except Exception as exc:   # noqa: BLE001 — thiếu thư viện engine ⇒ chưa biết
        client, loi = None, f"{type(exc).__name__}: {exc}"
    else:
        loi = "không tìm thấy repo engine medical-ebm-automation"
    if client is None:
        kq.update(trang_thai="chua_biet", ghi_chu=f"Không nạp được connector PMC: {loi}")
        return _xuat(kq, a.json, 2)

    r = client.tai_toan_van(pmcid)
    kq.update(url_nguon=r.url_nguon, ghi_chu=r.ghi_chu, ghi_chu_ban_quyen=r.ghi_chu_ban_quyen)
    if not r.thanh_cong:
        khong_co = "không có trong pmc open access subset" in (r.ghi_chu or "").lower()
        kq["trang_thai"] = "khong_co" if khong_co else "chua_biet"
        return _xuat(kq, a.json, 1 if khong_co else 2)
    vb = r.van_ban_trich or ""
    kq.update(trang_thai="doc_duoc", so_ky_tu=len(vb), dau_van_ban=vb[:1200],
              ket_qua_tim={c: tim_doan(vb, c) for c in a.tim})
    if a.toan_bo:
        kq["van_ban"] = vb
    return _xuat(kq, a.json, 0)


def _xuat(kq: dict, dang_json: bool, ma: int) -> int:
    if dang_json:
        print(json.dumps(kq, ensure_ascii=False, indent=2))
        return ma
    nhan = {"doc_duoc": "✓ ĐỌC ĐƯỢC", "khong_co": "✗ KHÔNG CÓ toàn văn PMC OA", "chua_biet": "⚪ CHƯA BIẾT"}
    print(f"{nhan.get(kq['trang_thai'], '?')} · {kq['dinh_danh']}" + (f" → {kq['pmcid']}" if kq["pmcid"] else ""))
    if kq.get("ghi_chu"):
        print(f"  {kq['ghi_chu']}")
    if kq["trang_thai"] == "doc_duoc":
        print(f"  nguồn: {kq['url_nguon']} · {kq['so_ky_tu']} ký tự")
        for cum, ds in kq["ket_qua_tim"].items():
            print(f"  — «{cum}»: {len(ds)} đoạn" + ("" if ds else " (không thấy nguyên văn — thử từ khác)"))
            for d in ds:
                print(f"    [@{d['vi_tri']}] …{d['doan']}…")
        if not kq["ket_qua_tim"]:
            print("  (đầu văn bản)\n" + kq["dau_van_ban"])
        if kq.get("van_ban"):
            print(kq["van_ban"])
        print(f"  ⚖ {kq['ghi_chu_ban_quyen']}")
    print("Tải được toàn văn KHÔNG xác nhận bài chưa bị rút — kiểm rút bài riêng. Cần bác sĩ kiểm chứng.")
    return ma


if __name__ == "__main__":
    raise SystemExit(main())
