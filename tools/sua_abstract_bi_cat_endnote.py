#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SỬA ABSTRACT BỊ CẮT TRONG ENDNOTE — bản ghi nạp qua Europe PMC trước bản vá `_bo_the_html` (13/10/2026).

Lỗi gốc (đã vá trong tools/nap_endnote_chu_de.py): `_bo_the_html` cũ dùng `<[^>]+>`, coi MỌI dấu «<» là đầu thẻ HTML.
`abstractText` của Europe PMC chứa «<140 mm Hg», «P < .001» dạng CHỮ thô ⇒ regex xoá từ «<» tới thẻ `<h4>` kế tiếp
(INTERACT2 PMID 23713578 còn «target systolic level of Results»; AβYSS PMID 40401436 «mmHg, P Conclusions»). Chỉ bản ghi
nạp qua làn DỰ PHÒNG Europe PMC (khi NCBI chặn IP) dính lỗi; bản vá chặn lỗi cho lượt nạp SAU, không sửa bản ghi đã nạp.

Công cụ này (CHẠY KHÔ mặc định): bản ghi EndNote khớp PMID của dashboard («Accession Number») → tách abstract GỐC (phần
dưới `PHAN_CACH` của tom_tat_endnote_vi; chưa có khối tiếng Việt thì cả trường) → tải lại PubMed efetch XML (bản ĐỐI
CHIẾU) → so dãy ký tự chữ-số (bỏ khoảng trắng, dấu câu — «HbA 1c» của Europe PMC khớp «HbA1c» của PubMed; thiếu riêng
NHÃN mục «BACKGROUND:» không tính):
  • bi_cat   — abstract gốc là DÃY CON của bản đối chiếu, thiếu ≥ 1 đoạn liền mạch và MỌI đoạn thiếu bắt đầu ngay sau một
               dấu «<» (xét mọi cách gióng tương đương — dấu vân của đúng lỗi này) ⇒ --ap-dung thay bằng bản đối chiếu.
  • thuc_the — đủ chữ nhưng còn mã «&lt;» «&gt;» «&amp;» chưa giải mã (cùng hàm cũ) ⇒ --ap-dung thay bằng bản đối chiếu.
  • khac     — khác kiểu khác (bản nhà xuất bản, bác sĩ sửa tay, PubMed đã cập nhật…) ⇒ CHỈ BÁO, không bao giờ sửa.
  • rong     — không có abstract gốc trong khi bản đối chiếu có ⇒ chỉ báo.
  • khop     — trùng bản đối chiếu.
  • khong_do — không đọc được trường / nguồn không trả bản ghi / khối tiếng Việt mất dấu phân cách ⇒ KHÔNG BIẾT, không
               bao giờ coi là «khớp».
Đo 13/10/2026 trên 828 PMID thật của 72 dashboard (bản Europe PMC): 194/194 abstract bị regex cũ cắt ⇒ bi_cat; 828/828 bản
lọc đúng ⇒ khop; 2.323/2.323 đoạn xoá ngẫu nhiên không bắt đầu ở «<» ⇒ khac (không bao giờ bị «sửa»).
NCBI chặn IP ⇒ mặc định KHÔNG ĐO ĐƯỢC (mã 2). Cờ `--europepmc-khi-ncbi-chan` (bác sĩ chọn) đối chiếu bản Europe PMC qua
bộ lọc thẻ ĐÃ VÁ — báo cáo ghi rõ nguồn đối chiếu.

--ap-dung: sao lưu sdb.eni TRƯỚC (`tom_tat_endnote_vi.sao_luu_thu_vien`; hỏng ⇒ không ghi gì) · đọc lại trường ngay trước
khi ghi (trường đổi từ lúc đo ⇒ bỏ qua bản đó) · thay ĐÚNG phần abstract gốc — khối «EBM · ĐỌC NHANH» phía trên giữ nguyên
từng ký tự · ghi rồi đọc lại. Công cụ KHÔNG tự mở và KHÔNG BAO GIỜ đóng EndNote (AppleScript `close document` làm EndNote
sập, đo 11/10/2026).

LƯU Ý kho tóm tắt máy `EBM-Dashboards/tom-tat-abstract-vi.json`: tóm tắt dựng từ abstract BỊ CẮT vẫn qua chốt `so_khong_khop`
(chốt chỉ đòi mọi số của tóm tắt có trong abstract gốc — abstract đầy đủ chỉ THÊM số) ⇒ công cụ liệt kê PMID cần sửa có mục
trong kho để dựng lại. Khối tiếng Việt cũ trong EndNote làm mới bằng
`python3 tools/nap_endnote_chu_de.py --tat-ca --tom-tat-vi --ap-dung` sau khi dựng lại kho.

Dùng:
  python3 tools/sua_abstract_bi_cat_endnote.py                                   # chạy khô, mọi dashboard
  python3 tools/sua_abstract_bi_cat_endnote.py --file EBM-Dashboards/WebDashboard_X.html
  python3 tools/sua_abstract_bi_cat_endnote.py --pmid 23713578 40401436
  python3 tools/sua_abstract_bi_cat_endnote.py --ap-dung [--json]
  python3 tools/sua_abstract_bi_cat_endnote.py --europepmc-khi-ncbi-chan          # NCBI đang chặn IP
Mã thoát: 0 không còn bản cần sửa · 1 còn bản cần sửa (chạy khô) hoặc ghi lỗi · 2 không đo được (EndNote chưa mở đúng
thư viện, NCBI chặn, hoặc có bản ghi KHÔNG ĐO ĐƯỢC) · 3 tham số sai.
Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import difflib
import html
import importlib.util
import json
import re
import sqlite3
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
MA_OK, MA_CON_VIEC, MA_KHONG_DO, MA_THAM_SO = 0, 1, 2, 3
SUA_DUOC = ("bi_cat", "thuc_the")
# Dấu vân của lỗi: đoạn thiếu BẮT ĐẦU ngay sau một dấu «<» (regex cũ xoá từ «<»). Phép gióng chọn tuỳ ý một trong các
# cách gióng tương đương khi chữ ở hai mép đoạn lặp lại, nên xét MỌI vị trí trượt. Đo 13/10/2026 trên 194 abstract thật bị
# regex cũ cắt: «short-term (< three months) and long-term» ⇒ đoạn thiếu được gióng trượt TRÁI qua «term»; «P <0.001).
# Bleeding … predominant» ⇒ chữ «P» còn giữ bị gióng vào «p» của «predominant», một đoạn thiếu tách làm hai. Cửa sổ cố định
# (12 ký tự trước + 24 sau) bắt đủ 194 nhưng nhận nhầm 18/783 ca «xoá một câu không có «<»» — bị thay bằng cách xét trượt.
TRAN_TRUOT = 40   # trượt tối đa bấy nhiêu ký tự chữ-số mỗi phía
GOP_KHE = 3       # đoạn thiếu cách đoạn trước ≤ bấy nhiêu ký tự chữ-số còn giữ ⇒ phần nối tiếp của cùng một đoạn
_THUC_THE = re.compile(r"&(?:lt|gt|amp|quot|apos|#\d+|#x[0-9a-f]+);", re.I)


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, ROOT / "tools" / tep)
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod


N = _nap("_nap_endnote_sua_abs", "nap_endnote_chu_de.py")
T = _nap("_tom_tat_vi_sua_abs", "tom_tat_endnote_vi.py")
# Câu giữ chỗ mà tom_tat_endnote_vi ghi khi bài không có abstract — lấy từ chính hàm ghép, không chép tay chuỗi.
KHONG_CO_ABS = T.ghep_abstract("", "x").partition(T.PHAN_CACH)[2].strip()


# ── so abstract gốc trong EndNote với bản đối chiếu ────────────────────────────────────────────────────────────────

def _ky_tu(s: str) -> list[tuple[str, int]]:
    """[(ký tự chữ-số viết thường, vị trí trong `s`)] — bỏ khoảng trắng, dấu câu, ký hiệu. `s` đã chuẩn hoá NFKC."""
    return [(k, i) for i, c in enumerate(s) for k in c.lower() if k.isalnum()]


def vi_tri_truot(a: list[tuple[str, int]], i1: int, i2: int) -> range:
    """Mọi điểm đầu tương đương của đoạn thiếu a[i1:i2]: trượt trái được khi chữ ngay trước đoạn trùng chữ cuối đoạn,
    trượt phải được khi chữ đầu đoạn trùng chữ ngay sau đoạn (cùng một chuỗi còn lại, phép gióng chọn tuỳ ý)."""
    k = [c for c, _ in a]
    trai = 0
    while trai < TRAN_TRUOT and i1 - trai - 1 >= 0 and k[i1 - trai - 1] == k[i2 - trai - 1]:
        trai += 1
    phai = 0
    while phai < TRAN_TRUOT and i2 + phai < len(k) and k[i1 + phai] == k[i2 + phai]:
        phai += 1
    return range(i1 - trai, i1 + phai + 1)


def bat_dau_sau_dau_nho_hon(pm: str, a: list[tuple[str, int]], i1: int, i2: int) -> bool:
    """Có cách gióng tương đương nào mà đoạn thiếu a[i1:i2] bắt đầu ngay sau dấu «<» — tức khe ký tự KHÔNG chữ-số ngay
    trước ký tự thiếu đầu tiên có chứa «<»."""
    return any("<" in pm[(a[s - 1][1] + 1 if s else 0):a[s][1]] for s in vi_tri_truot(a, i1, i2))


def chi_la_nhan(a: list[tuple[str, int]], i1: int, i2: int, nhan: list[range]) -> bool:
    """Đoạn thiếu a[i1:i2] (ở một cách gióng tương đương nào đó) nằm trọn trong một nhãn mục «BACKGROUND:»."""
    n = i2 - i1
    return any(a[s][1] in r and a[s + n - 1][1] in r for s in vi_tri_truot(a, i1, i2) for r in nhan)


def phan_loai(goc_en: str, goc_pm: str) -> dict:
    """Abstract gốc trong EndNote so với bản đối chiếu (PubMed) → {"loai", "thieu" (số ký tự chữ-số thiếu), "doan", "ly_do"}."""
    en = T.chuan_dong(goc_en)
    pm = unicodedata.normalize("NFKC", goc_pm or "").strip()
    if not en or en == KHONG_CO_ABS:
        return {"loai": "rong", "ly_do": "EndNote không có abstract gốc, bản đối chiếu có"} if pm else {"loai": "khop"}
    if not pm:
        return {"loai": "khac", "ly_do": "bản đối chiếu không có abstract mà EndNote có"}
    a = _ky_tu(pm)
    b = _ky_tu(unicodedata.normalize("NFKC", html.unescape(en)))
    # Nhãn mục của abstract có cấu trúc («BACKGROUND:» đầu dòng — khuôn của phan_tich_pubmed_xml). Bản Europe PMC có thể
    # không in tiêu đề mục ⇒ thiếu NHÃN không phải thiếu nội dung, không tính.
    nhan = [range(m.start(1), m.end(1)) for m in re.finditer(r"(?m)^([A-Z][A-Za-z0-9 ,/&()'-]{0,58}):[ \t]", pm)]
    sm = difflib.SequenceMatcher(None, [k for k, _ in a], [k for k, _ in b], autojunk=False)
    thieu: list[tuple[int, int]] = []
    thua = 0
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        thua += j2 - j1
        if i2 > i1 and not (j2 == j1 and chi_la_nhan(a, i1, i2, nhan)):
            thieu.append((i1, i2))
    if not thieu and not thua:
        return {"loai": "thuc_the" if _THUC_THE.search(en) else "khop"}
    if thua:
        return {"loai": "khac", "ly_do": f"{thua} ký tự chữ-số có trong EndNote mà bản đối chiếu không có",
                "thieu": sum(i2 - i1 for i1, i2 in thieu)}
    so = sum(i2 - i1 for i1, i2 in thieu)
    doan: list[str] = []
    dau_vet = True
    cuoi, dat_truoc, tu_nhom = -GOP_KHE - 1, False, 0
    for i1, i2 in thieu:
        # Đoạn cách đoạn trước ≤ GOP_KHE ký tự = phần nối tiếp của CÙNG một đoạn bị xoá (phép gióng bắt nhầm một chữ
        # lẻ ở giữa) ⇒ đạt nếu đoạn trước đạt. Không gộp TRƯỚC khi xét: gộp làm mất khe «<» của chính đoạn đầu (đo 13/10:
        # «(<25 kg/m<sup>2</sup>) (p < 0.001)» — hai đoạn thật cách nhau một chữ «2» còn giữ).
        noi_tiep = i1 - cuoi <= GOP_KHE
        dat = (noi_tiep and dat_truoc) or bat_dau_sau_dau_nho_hon(pm, a, i1, i2)
        dau_vet = dau_vet and dat
        if not noi_tiep:
            tu_nhom = a[i1 - 1][1] + 1 if i1 else 0   # ngay sau ký tự còn giữ cuối cùng trước đoạn thiếu
            doan.append("")
        doan[-1] = re.sub(r"\s+", " ", pm[tu_nhom:a[i2 - 1][1] + 1]).strip()
        cuoi, dat_truoc = i2, dat
    if not dau_vet:
        return {"loai": "khac", "ly_do": "thiếu đoạn không bắt đầu sau dấu «<» — không phải dấu vân của lỗi này",
                "thieu": so, "doan": doan}
    return {"loai": "bi_cat", "thieu": so, "doan": doan}


def thay_goc(cu: str, goc_moi: str) -> str | None:
    """Trường Abstract mới: khối tiếng Việt (nếu có) GIỮ NGUYÊN, chỉ phần dưới `PHAN_CACH` thay bằng `goc_moi`.
    Khối tiếng Việt mà mất dấu phân cách ⇒ None (không biết abstract gốc bắt đầu ở đâu — không ghi)."""
    c = T.chuan_dong(cu)
    if c.startswith(T.MO_DAU_DA_DUNG):
        dau, co, _ = c.partition(T.PHAN_CACH)
        return f"{dau}{T.PHAN_CACH}\n{goc_moi}" if co else None
    return goc_moi


def _nguon_meta(ghi_chu: str | None) -> str:
    """Nguồn metadata ghi trong Notes lúc nạp («Metadata: Europe PMC.») — chỉ để báo, không dùng để quyết định sửa."""
    m = re.search(r"Metadata: (PubMed|Europe PMC|Crossref)", ghi_chu or "")
    return m.group(1) if m else "?"


# ── đo và sửa ──────────────────────────────────────────────────────────────────────────────────────────────────

def lay_doi_chieu(pmids: list[str], lay_pm, lay_ep) -> tuple[dict, str]:
    """(metadata theo PMID, nhãn nguồn đối chiếu). PubMed efetch trước; NCBI chặn IP mà `lay_ep` được cho phép (cờ
    --europepmc-khi-ncbi-chan) ⇒ Europe PMC qua bộ lọc thẻ ĐÃ VÁ. Không cho phép ⇒ NcbiChan ném ra: không đo được."""
    try:
        return lay_pm(pmids), "PubMed efetch"
    except N.NcbiChan:
        if lay_ep is None:
            raise
        return lay_ep(pmids), "Europe PMC (NCBI chặn IP — cờ --europepmc-khi-ncbi-chan; bộ lọc thẻ đã vá)"


def do_va_sua(endnote, pmids: list[str], *, ap_dung: bool, lay_pm=None, lay_ep=None, sao_luu=None,
              kho_tt: dict | None = None) -> dict:
    """Đo mọi bản ghi khớp `pmids`; `ap_dung` ⇒ sửa bản `bi_cat`/`thuc_the`. NcbiChan/RuntimeError của nguồn đối chiếu
    ném ra cho người gọi — không đo được thì KHÔNG báo «khớp». `lay_ep` None = không lùi sang Europe PMC."""
    lay_pm = lay_pm or N.lay_pubmed
    bc: dict = {"pmid": len(pmids), "ban_ghi": 0, "khong_co_ban_ghi": [], "doi_chieu": None, "dem": dict.fromkeys(
        ("khop", "bi_cat", "thuc_the", "khac", "rong", "khong_do"), 0), "chi_tiet": [], "se_sua": 0, "da_sua": 0,
        "loi": [], "sao_luu": None, "kho_tom_tat_dung_lai": []}
    theo_pm = endnote.tim_khop(pmids, "Accession Number") if pmids else {}
    cap: list[tuple[str, str]] = []
    thay: set[str] = set()
    for p in pmids:
        ma = theo_pm.get(p) or []
        if not ma:
            bc["khong_co_ban_ghi"].append(p)
        for m in ma:   # bản trùng PMID (bác sĩ tự nhập thêm) cũng đo — chỉ sửa khi đúng dấu vân lỗi
            if m not in thay:
                thay.add(m)
                cap.append((p, m))
    bc["ban_ghi"] = len(cap)
    if not cap:
        return bc
    ids = [m for _, m in cap]
    truong = endnote.doc_truong(ids, "Abstract")
    ghi_chu = endnote.doc_truong(ids, "Notes")
    meta, bc["doi_chieu"] = lay_doi_chieu(sorted({p for p, _ in cap}), lay_pm, lay_ep)
    can_sua: list[dict] = []
    for p, m in cap:
        dong = {"pmid": p, "ma": m, "nguon": _nguon_meta(ghi_chu.get(m))}
        if m not in truong:
            kq = {"loai": "khong_do", "ly_do": "không đọc được trường Abstract"}
        elif p not in meta:
            kq = {"loai": "khong_do", "ly_do": "nguồn đối chiếu không trả bản ghi cho PMID này"}
        elif (T.chuan_dong(truong[m]).startswith(T.MO_DAU_DA_DUNG)
              and T.PHAN_CACH not in T.chuan_dong(truong[m])):
            kq = {"loai": "khong_do", "ly_do": "khối tiếng Việt mất dấu phân cách — không tách được abstract gốc"}
        else:
            kq = phan_loai(T.tach_goc(truong[m]), meta[p].get("tom_tat") or "")
        dong.update(kq)
        bc["dem"][kq["loai"]] += 1
        if kq["loai"] != "khop":
            bc["chi_tiet"].append(dong)
        if kq["loai"] in SUA_DUOC:
            can_sua.append(dict(dong, cu=truong[m], moi=thay_goc(truong[m], meta[p]["tom_tat"])))
    bc["se_sua"] = len(can_sua)
    if kho_tt:
        bc["kho_tom_tat_dung_lai"] = sorted({x["pmid"] for x in can_sua if f"PMID {x['pmid']}" in kho_tt}, key=int)
    if not ap_dung or not can_sua:
        return bc

    bc["sao_luu"] = str((sao_luu or (lambda: T.sao_luu_thu_vien(endnote.thu_vien)))())   # hỏng ⇒ ném, chưa ghi gì
    lai = endnote.doc_truong([x["ma"] for x in can_sua], "Abstract")
    ghi: list[tuple[str, str]] = []
    for x in can_sua:
        if x["ma"] not in lai or T.chuan_dong(lai[x["ma"]]) != T.chuan_dong(x["cu"]):
            bc["loi"].append(f"{x['ma']} (PMID {x['pmid']}): trường Abstract đổi từ lúc đo — bỏ qua, chạy lại để đo lại")
            continue
        ghi.append((x["ma"], x["moi"]))
    for i in range(0, len(ghi), 25):
        for ma, loi in endnote.ghi_truong(ghi[i:i + 25], "Abstract").items():
            if loi:
                bc["loi"].append(f"{ma}: {loi}")
            else:
                bc["da_sua"] += 1
    return bc


def _ma_ngan(ma: str) -> str:
    """`<RecordID database="1" recNum="6528" />` → «rec 6528» (số bản ghi bác sĩ thấy trong EndNote)."""
    m = re.search(r'recNum="(\d+)"', ma)
    return f"rec {m.group(1)}" if m else ma


def _trich(doan: list[str], toi_da: int = 70) -> str:
    d = doan[0] if doan else ""
    return f"«{d[:toi_da]}…»" if len(d) > toi_da else (f"«{d}»" if d else "")


def in_bao_cao(bc: dict, ap_dung: bool) -> None:
    d = bc["dem"]
    print(f"✓ Abstract EndNote so với bản đối chiếu: {bc['pmid']} PMID · {bc['ban_ghi']} bản ghi · khớp {d['khop']} · "
          f"BỊ CẮT {d['bi_cat']} · còn mã HTML {d['thuc_the']} · khác bản đối chiếu {d['khac']} (chỉ báo) · "
          f"trống {d['rong']} (chỉ báo) · KHÔNG ĐO ĐƯỢC {d['khong_do']}")
    if bc.get("doi_chieu"):
        print(f"   Đối chiếu: {bc['doi_chieu']}")
    if bc["khong_co_ban_ghi"]:
        print(f"   Chưa có bản ghi trong thư viện: {len(bc['khong_co_ban_ghi'])} PMID (nạp chủ đề trước)")
    lam = "đã thay" if ap_dung else "sẽ thay"
    nhom = (("bi_cat", f"BỊ CẮT — {lam} phần abstract gốc bằng bản đối chiếu; khối «EBM · ĐỌC NHANH» giữ nguyên"),
            ("thuc_the", f"Còn mã HTML (&lt; &gt; …) — {lam} bằng bản đối chiếu"),
            ("khac", "KHÁC bản đối chiếu — KHÔNG sửa, xem tay"),
            ("rong", "Trống trong khi bản đối chiếu có abstract — KHÔNG sửa"),
            ("khong_do", "KHÔNG ĐO ĐƯỢC — không phải «khớp»"))
    for loai, tieu_de in nhom:
        ds = [x for x in bc["chi_tiet"] if x["loai"] == loai]
        if not ds:
            continue
        print(f"   {tieu_de}: {len(ds)}")
        for x in ds[:40]:
            phu = " · ".join(s for s in (f"thiếu {x['thieu']} ký tự chữ-số" if x.get("thieu") else "",
                                         f"metadata {x['nguon']}", x.get("ly_do", ""),
                                         _trich(x.get("doan") or [])) if s)
            print(f"     – PMID {x['pmid']} [{_ma_ngan(x['ma'])}] {phu}")
        if len(ds) > 40:
            print(f"     … +{len(ds) - 40}")
    if bc["kho_tom_tat_dung_lai"]:
        print(f"   ⚠ Kho tóm tắt máy ({T.TEP_TOM_TAT_ABS}): {len(bc['kho_tom_tat_dung_lai'])} PMID có tóm tắt dựng từ abstract "
              "bị cắt — chốt `so_khong_khop` KHÔNG bắt được (abstract đầy đủ chỉ thêm số); cần dựng lại: "
              + ", ".join(bc["kho_tom_tat_dung_lai"]))
    if bc.get("sao_luu"):
        print(f"   Sao lưu trước khi ghi: {bc['sao_luu']}")
    if ap_dung:
        print(f"   Đã sửa {bc['da_sua']}/{bc['se_sua']}")
    for loi in bc["loi"][:12]:
        print(f"   ✗ {loi}")
    if not ap_dung:
        print("Chạy khô — chưa ghi gì." + (" Thêm --ap-dung để sửa (sao lưu sdb.eni trước)." if bc["se_sua"] else ""))


def ma_thoat(bc: dict, ap_dung: bool) -> int:
    if bc["loi"] or (not ap_dung and bc["se_sua"]):
        return MA_CON_VIEC
    return MA_KHONG_DO if bc["dem"]["khong_do"] else MA_OK


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    ap.add_argument("--file", nargs="*", default=[], help="dashboard WebDashboard_*.html (mặc định: mọi dashboard)")
    ap.add_argument("--pmid", nargs="*", default=[], help="chỉ đo các PMID này (thay cho dashboard)")
    ap.add_argument("--ap-dung", action="store_true", help="sửa thật (mặc định chạy khô)")
    ap.add_argument("--europepmc-khi-ncbi-chan", action="store_true",
                    help="NCBI chặn IP thì đối chiếu bản Europe PMC qua bộ lọc thẻ đã vá (mặc định: không đo được, mã 2)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.pmid and a.file:
        print("✗ --pmid không đi cùng --file")
        return MA_THAM_SO
    if any(not re.fullmatch(r"\d{1,9}", p) for p in a.pmid):
        print("✗ PMID phải là số")
        return MA_THAM_SO

    bst = _nap("_bst_sua_abs", "ban_sao_tran.py")
    dash_goc = bst.duong_goc("EBM-Dashboards", ROOT)
    if a.pmid:
        pmids = list(dict.fromkeys(a.pmid))
    else:
        files = [Path(f) for f in a.file] or (sorted(dash_goc.glob("WebDashboard_*.html")) if dash_goc else [])
        if not files:
            print("✗ không thấy dashboard nào (bản sao trần?) — dùng --file hoặc --pmid")
            return MA_KHONG_DO
        doc = N._nap_doc_data()
        pmids = list(dict.fromkeys(d["pmid"] for f in files for d in N.trich_dinh_danh(doc(f) or {}) if d.get("pmid")))
        dash_goc = dash_goc or files[0].resolve().parent   # worktree ngoài cây OneDrive: kho nằm cạnh dashboard

    ch = N.doc_cau_hinh()
    try:
        if ch is None:
            raise N.KhongChayDuoc(f"chưa cấu hình thư viện EndNote ({N.CAU_HINH}) — "
                                  "chạy tools/nap_endnote_chu_de.py --ghi-cau-hinh \"<đường dẫn .enl>\"")
        endnote = N.EndNoteMac(ch["ung_dung"], Path(ch["thu_vien"]))
        if not endnote.dang_mo_dung_thu_vien():
            raise N.KhongChayDuoc(f"EndNote chưa mở thư viện {Path(ch['thu_vien']).name} — mở thư viện rồi chạy lại "
                                  "(công cụ không tự mở EndNote)")
    except N.KhongChayDuoc as e:
        print(f"⚪ Không đo được: {e}")
        return MA_KHONG_DO
    try:
        kho_tt = T.nap_tom_tat_abstract(dash_goc)
    except (OSError, ValueError) as e:
        print(f"⚠ Kho tóm tắt máy hỏng — bỏ phần đối chiếu kho: {e}"[:300])
        kho_tt = {}
    try:
        bc = do_va_sua(endnote, pmids, ap_dung=a.ap_dung, kho_tt=kho_tt,
                       lay_ep=N.lay_europepmc if a.europepmc_khi_ncbi_chan else None)
    except N.NcbiChan:
        print("⚪ Không đo được: NCBI đang chặn IP mạng này (trang «Blocked Diagnostic»). Không so được thì không kết luận "
              "bản nào «khớp». Chờ NCBI gỡ chặn, hoặc chạy lại với --europepmc-khi-ncbi-chan (đối chiếu Europe PMC qua "
              "bộ lọc thẻ đã vá).")
        return MA_KHONG_DO
    except (RuntimeError, OSError, ET.ParseError, sqlite3.Error) as e:
        print(f"✗ {type(e).__name__}: {e} — không ghi gì sau lỗi này"[:300])
        return MA_KHONG_DO
    in_bao_cao(bc, a.ap_dung)
    if a.json:
        print(json.dumps(bc, ensure_ascii=False, indent=2))
    return ma_thoat(bc, a.ap_dung)


if __name__ == "__main__":
    sys.exit(main())
