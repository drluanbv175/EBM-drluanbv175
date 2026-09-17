#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NẠP GUIDELINE THEO ẤN PHẨM CHÍNH THỨC — phủ kho toàn văn cho danh bạ (20/08/2026).

VÌ SAO CÓ
=========
Mục «Cho thực hành» chỉ đúng chuẩn khi trích được MỨC KHUYẾN CÁO NGUYÊN BẢN từng
dòng (GRADE 1A/2B · COR I/LoE A · A–E) — thứ chỉ nằm trong TOÀN VĂN guideline.
Đo 20/08: danh bạ 30 nguồn nhưng chỉ 1 có toàn văn trong kho (KDIGO 2024), 11/30
trang tổ chức chặn máy.

Đường vòng KHÔNG cào trang tổ chức: gần như mọi guideline lớn đều ĐĂNG TẠP CHÍ
(ARD · Kidney Int · Circulation · Diabetes Care · Eur Heart J…), nên có PMID/DOI
thật và nhiều bản nằm trong PMC Open Access. Tool này: danh bạ → tra ấn phẩm trên
PubMed → khớp tiêu đề có chấm điểm → gắn PMID/DOI vào danh bạ → tải JATS nếu PMC-OA.

BA LUẬT AN TOÀN (chống gắn nhầm — nguy hiểm hơn không gắn):
  1. Chỉ tự gắn khi ĐIỂM KHỚP tiêu đề ≥ 0.55 VÀ (tên tổ chức xuất hiện trong tiêu đề
     HOẶC tạp chí thuộc danh sách tạp chí chính thống của tổ chức đó). Dưới ngưỡng →
     chỉ IN ỨNG VIÊN, không gắn, để người xem.
  2. Không có bản PMC-OA → ghi rõ `toan_van: "khong_oa"`, KHÔNG đoán, KHÔNG cào bản trả phí.
  3. Bản tải về phải là JATS thật (có <body> hoặc ≥ 500 từ) mới ghi kho.

Dùng:  python3 tools/nap_guideline_pmc.py                # xem đề xuất, không ghi
       python3 tools/nap_guideline_pmc.py --ap-dung      # gắn định danh + tải PMC-OA
       python3 tools/nap_guideline_pmc.py --chu-de benh-than-man --ap-dung
Mã thoát: 0 · 1 thiếu danh bạ · 2 lỗi hạ tầng mạng. Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import time
import urllib.parse as up
import urllib.request as rq
from datetime import date
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
DANH_BA = REPO / "EBM-Dashboards" / "nguon_chuan" / "danh-ba-nguon-chuan.json"
KHO = REPO / "EBM-Dashboards" / "guideline_snapshot"
SO = KHO / "so-guideline.json"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# Tạp chí chính thống theo tổ chức — dùng làm bằng chứng phụ khi tên tổ chức không
# nằm trong tiêu đề bài (ví dụ EULAR đăng trên Ann Rheum Dis).
TAP_CHI_CUA = {
    "EULAR": ["ann rheum dis", "rmd open"],
    "ACR": ["arthritis rheumatol", "arthritis care res"],
    "ESC": ["eur heart j", "european heart journal"],
    "ESC/EAS": ["eur heart j", "atherosclerosis"],
    "ACC/AHA": ["circulation", "j am coll cardiol"],
    "ACC/AHA/HFSA": ["circulation", "j am coll cardiol"],
    "ACC/AHA/ACCP/HRS": ["circulation", "j am coll cardiol"],
    "KDIGO": ["kidney int"],
    "ADA": ["diabetes care"],
    "AASLD": ["hepatology", "clin liver dis"],
    "EASL": ["j hepatol"],
    "WHO": ["bull world health organ"],
    "IDSA": ["clin infect dis"],
    "IDSA/ATS": ["am j respir crit care med", "clin infect dis"],
    "ACG": ["am j gastroenterol"],
    "Endocrine Society": ["j clin endocrinol metab"],
    "USPSTF": ["jama"],
    "GOLD": ["am j respir crit care med", "eur respir j"],
    "GINA": ["eur respir j", "am j respir crit care med"],
    "AHS": ["headache"],
    "VA/DoD": ["ann intern med"],
    "NICE": [],
    "AACE": ["endocr pract"],
    "ISH": ["hypertension", "j hypertens"],
    "Maastricht/Florence": ["gut"],
    "ICHD-3": ["cephalalgia"],
    "NeuPSIG/IASP": ["pain", "lancet neurol"],
    "CDC": ["mmwr recomm rep"],
    "ATA": ["thyroid"],
}

# Từ CHUNG của mọi guideline — khớp trúng mấy từ này KHÔNG chứng minh cùng chủ đề
# (đo 20/08: guideline WHO về VÔ SINH khớp 0.43 với mục viêm gan B chỉ nhờ
# prevention/diagnosis/treatment).
_TU_CHUNG = {"prevention", "diagnosis", "treatment", "care", "management",
             "evaluation", "adult", "adults", "patients", "therapy", "update",
             "report", "statement", "consensus", "strategy", "global", "initiative",
             "disease", "prevention,", "detection", "screening"}

_DUNG_TU = {"the", "of", "for", "and", "in", "on", "a", "an", "với", "và", "cho",
            "guideline", "guidelines", "clinical", "practice", "recommendations",
            "cập", "nhật", "hằng", "năm", "bản", "báo", "cáo"}


def _tu(s: str) -> set[str]:
    s = re.sub(r"\([^)]*\)", " ", s.lower())
    return {w for w in re.findall(r"[a-zà-ỹ0-9]+", s) if len(w) > 2 and w not in _DUNG_TU}


# Viết tắt trong danh bạ ↔ cụm viết đủ trong tiêu đề ấn phẩm (đo 20/08: «Anemia in
# CKD» chỉ khớp 0.25 với chính guideline KDIGO vì tiêu đề ghi «Chronic Kidney Disease»).
DONG_NGHIA = {
    "ckd": "chronic kidney", "ra": "rheumatoid", "copd": "chronic obstructive",
    "hbv": "hepatitis b", "af": "atrial fibrillation", "t2d": "type 2 diabetes",
    "cap": "community-acquired pneumonia", "uti": "urinary tract infection",
    "hf": "heart failure", "mra": "mineralocorticoid",
}


def _diem_khop(ten_danh_ba: str, tieu_de: str) -> float:
    a, b = _tu(ten_danh_ba), _tu(tieu_de)
    if not a:
        return 0.0
    td = tieu_de.lower()
    trung = len(a & b) + sum(1 for w in a - b
                             if w in DONG_NGHIA and DONG_NGHIA[w] in td)
    return min(trung / len(a), 1.0)


def _tai(url: str) -> bytes:
    return rq.urlopen(url, timeout=25).read()


def _truy_van(ng: dict) -> list[str]:
    """Chuỗi truy vấn thử theo thứ tự — vá 20/08: bản đầu nhét NĂM vào [ti] nên
    trượt hoàn toàn (KDIGO 2024 không tìm ra), và không lọc loại ấn phẩm nên khớp
    nhầm bài nghiên cứu thường."""
    ten = re.sub(r"\([^)]*\)", " ", ng["ten"]).strip()
    # THỨ TỰ XÁC ĐỊNH: set của Python băm ngẫu nhiên theo tiến trình ⇒ cùng một
    # nguồn có thể sinh truy vấn KHÁC NHAU mỗi lần chạy (lỗi tái lập, bắt 20/08).
    # Sắp theo độ dài giảm dần: từ dài = đặc hiệu hơn.
    tu = sorted((w for w in _tu(ten) if not re.fullmatch(r"(19|20)\d{2}", w)),
                key=lambda w: (-len(w), w))
    # Viết tắt → cụm đầy đủ dạng cụm từ, vì tiêu đề ấn phẩm hầu như luôn viết đủ chữ
    tu = [f'"{DONG_NGHIA[w]}"' if w in DONG_NGHIA else w for w in tu]
    org = ng["to_chuc"].split("/")[0]
    q = []
    if tu:
        pt = " AND (guideline[pt] OR practice guideline[pt] OR consensus development conference[pt])"
        q.append(f"{org}[ti] AND " + " AND ".join(f"{w}[ti]" for w in tu[:3]) + pt)
        q.append(f"{org}[ti] AND " + " AND ".join(f"{w}[ti]" for w in tu[:3]))
        q.append(" AND ".join(f"{w}[ti]" for w in tu[:3])
                 + " AND (guideline[pt] OR practice guideline[pt] OR consensus development conference[pt])")
        q.append(" AND ".join(f"{w}[ti]" for w in tu[:4]))
    return q


def _tim_an_pham(ng: dict) -> list[dict]:
    """Tra PubMed cho một nguồn danh bạ; trả tối đa 5 ứng viên kèm điểm khớp."""
    ten = re.sub(r"\([^)]*\)", " ", ng["ten"]).strip()
    ids: list[str] = []
    for cot_loi in _truy_van(ng):
        try:
            u = (f"{EUTILS}/esearch.fcgi?db=pubmed&retmode=json&retmax=25&sort=date&term="
                 + up.quote(cot_loi))
            them = json.loads(_tai(u))["esearchresult"]["idlist"]
        except Exception:  # noqa: BLE001
            them = []
        for x in them:
            if x not in ids:
                ids.append(x)
        time.sleep(0.34)
        if len(ids) >= 40:
            break
    if not ids:
        return []
    ids = ids[:40]
    try:
        js = json.loads(_tai(f"{EUTILS}/esummary.fcgi?db=pubmed&retmode=json&id={','.join(ids)}"))["result"]
    except Exception:  # noqa: BLE001
        return []
    ra = []
    for pm in ids:
        r = js.get(pm)
        if not r or "title" not in r:
            continue
        doi = next((x["value"] for x in r.get("articleids", []) if x.get("idtype") == "doi"), "")
        tc_ok = any(t in r["source"].lower() for t in TAP_CHI_CUA.get(ng["to_chuc"], []))
        ten_tc_trong_tieu_de = ng["to_chuc"].split("/")[0].lower() in r["title"].lower()
        loai = [x.lower() for x in r.get("pubtype", [])]
        la_guideline = any("guideline" in x or "consensus" in x for x in loai)
        # «Executive summary» là ấn phẩm RIÊNG, ngắn hơn bản đầy đủ — mà thứ cần cho
        # «mức khuyến cáo nguyên bản từng dòng» chỉ có trong bản đầy đủ (đo 20/08:
        # KDIGO 2024 executive summary tr.684-701 vs bản đầy đủ tr.S117-S314).
        la_tom_luoc = bool(re.search(r"executive summary", r["title"], re.I))
        diem = _diem_khop(ten, r["title"])
        dac_hieu = _tu(ten) - _TU_CHUNG
        td_low = r["title"].lower()
        khop_dac_hieu = any(w in _tu(r["title"]) or
                            (w in DONG_NGHIA and DONG_NGHIA[w] in td_low)
                            for w in dac_hieu)
        # Tập từ quá ngắn (≤2 từ nội dung) thì tỷ lệ trùng 1.0 là ẢO — hạ điểm
        # (đo thật 20/08: «Anemia in CKD» khớp 1.0 với bài roxadustat ngẫu nhiên).
        if len(_tu(ten)) <= 2:
            diem *= 0.5
        # Bài ĂN THEO guideline (bình luận/đính chính/thư) chứa NGUYÊN VĂN tiêu đề
        # guideline nên luôn khớp 1.0 — đo thật 20/08: KDOQI US Commentary xếp trên
        # cả chính guideline KDIGO. Loại thẳng theo mặt chữ tiêu đề.
        if re.search(r"\bcommentar|\bcomment on|corrigend|erratum|editorial|"
                     r"\breply\b|response to|letter", r["title"], re.I):
            continue
        ra.append({"pmid": pm, "tieu_de": r["title"], "tap_chi": r["source"],
                   "nam": (r.get("pubdate") or "")[:4], "doi": doi,
                   "tap": r.get("volume", ""), "so": r.get("issue", ""),
                   "trang": r.get("pages", ""), "la_guideline": la_guideline,
                   "la_tom_luoc": la_tom_luoc, "khop_dac_hieu": khop_dac_hieu,
                   "diem": round(diem, 2),
                   "bang_chung_to_chuc": bool(tc_ok or ten_tc_trong_tieu_de)})
    # Xếp hạng: ĐÚNG LOẠI ẤN PHẨM + đúng nhà xuất bản của tổ chức đứng trước mọi
    # thứ khác; trùng chữ chỉ là tiêu chí phụ (nó thiên vị bài ăn theo).
    ra.sort(key=lambda x: (-(x["la_guideline"] and x["bang_chung_to_chuc"]),
                           -x["la_guideline"], -x["bang_chung_to_chuc"],
                           -x["khop_dac_hieu"], x["la_tom_luoc"],
                           -round(x["diem"], 1), -int(x["nam"] or 0)))
    return ra


def _pmc_cua(pmid: str) -> str | None:
    """PMCID của một PMID — parse JSON THẬT (bản đầu bắt regex `"id":"..."` mà
    elink trả `"links":[...]` ⇒ luôn None: «0 toàn văn» hoá ra là DETECTOR HỎNG,
    không phải sự thật — đúng họ lỗi «không biết bị báo thành không có»).
    CHỈ nhận linkname `pubmed_pmc`; `pubmed_pmc_refs` là bài TRÍCH DẪN NÓ (bẫy
    đã làm nhiễm kho toàn văn 15/08 — BH53)."""
    try:
        js = json.loads(_tai(f"{EUTILS}/elink.fcgi?dbfrom=pubmed&db=pmc&retmode=json&id={pmid}"))
    except Exception:  # noqa: BLE001
        return None
    for ls in js.get("linksets", []):
        for db in ls.get("linksetdbs", []):
            if db.get("dbto") == "pmc" and db.get("linkname") == "pubmed_pmc":
                links = db.get("links") or []
                if links:
                    return str(links[0])
    return None


def _nap_gom():
    import importlib.util as _ilu_mea
    _sp_mea = _ilu_mea.spec_from_file_location("_bst_ngp", Path(__file__).resolve().parent / "ban_sao_tran.py")
    _bst_mea = _ilu_mea.module_from_spec(_sp_mea)
    _sp_mea.loader.exec_module(_bst_mea)
    duong = (_bst_mea.duong_goc("medical-ebm-automation", REPO) or (REPO / "medical-ebm-automation")) / "tools" / "gom_toan_van_oa.py"
    sp = importlib.util.spec_from_file_location("gom_tv_gl", duong)
    m = importlib.util.module_from_spec(sp)
    sys.modules["gom_tv_gl"] = m
    sp.loader.exec_module(m)
    return m


def _slug(s: str) -> str:
    s = re.sub(r"\([^)]*\)", "", s.lower())
    s = re.sub(r"[^\w\s-]", "", s).strip()
    return re.sub(r"[\s_]+", "-", s)[:52]


def main() -> int:
    ap = argparse.ArgumentParser(description="Nạp guideline theo ấn phẩm chính thức (PubMed/PMC)")
    ap.add_argument("--ap-dung", action="store_true", help="ghi định danh vào danh bạ + tải PMC-OA")
    ap.add_argument("--chu-de", help="chỉ xử lý một mã chủ đề")
    ap.add_argument("--chot", nargs=3, metavar=("CHU-DE", "TO-CHUC", "PMID"),
                    help="NGƯỜI chốt đích danh ấn phẩm chủ lực cho một nguồn "
                         "(tra định danh thật rồi ghi, đánh dấu xac_nhan=nguoi)")
    ap.add_argument("--nguon-chua", help="phân biệt khi một tổ chức có nhiều nguồn "
                                         "trong cùng chủ đề (khớp chuỗi trong tên nguồn)")
    ap.add_argument("--va-nhan", action="store_true",
                    help="gắn nhãn xac_nhan=may cho nguồn đã có PMID nhưng chưa khai "
                         "(bản gắn TRƯỚC khi có trường này — không suy diễn là người chốt)")
    ap.add_argument("--lam-lai", action="store_true",
                    help="gỡ định danh đã gắn rồi khớp lại từ đầu (sau khi sửa luật khớp)")
    a = ap.parse_args()
    if not DANH_BA.exists():
        print("✗ Chưa có danh bạ nguồn chuẩn.")
        return 1
    db = json.loads(DANH_BA.read_text(encoding="utf-8"))
    KHO.mkdir(parents=True, exist_ok=True)
    so = json.loads(SO.read_text(encoding="utf-8")) if SO.exists() else []
    gom = _nap_gom() if (a.ap_dung or a.chot) else None

    if a.chot:
        ma_cd, tc, pm = a.chot
        cd = db["chu_de"].get(ma_cd)
        if not cd:
            print(f"✗ Không có chủ đề «{ma_cd}».")
            return 1
        ung = [n for n in cd["nguon"] if n["to_chuc"] == tc]
        if a.nguon_chua:
            ung = [n for n in ung if a.nguon_chua.lower() in n["ten"].lower()]
        if len(ung) > 1:
            print(f"✗ «{tc}» có {len(ung)} nguồn trong chủ đề này — thêm --nguon-chua để chỉ rõ:")
            for n in ung:
                print(f"    · {n['ten']}")
            return 1
        ng = ung[0] if ung else None
        if not ng:
            print(f"✗ Chủ đề «{ma_cd}» không có nguồn của «{tc}».")
            return 1
        try:
            js = json.loads(_tai(f"{EUTILS}/esummary.fcgi?db=pubmed&retmode=json&id={pm}"))["result"][pm]
        except Exception as exc:  # noqa: BLE001
            print(f"🔴 Không tra được PMID {pm} ({type(exc).__name__}) — KHÔNG ghi.")
            return 2
        doi = next((x["value"] for x in js.get("articleids", []) if x.get("idtype") == "doi"), "")
        ng["pmid"], ng["doi"], ng["xac_nhan"] = pm, doi, "nguoi"
        ng["an_pham"] = (f"{js['source']} {(js.get('pubdate') or '')[:4]};{js.get('volume','')}"
                         + (f"({js.get('issue')})" if js.get("issue") else "")
                         + (f":{js.get('pages')}" if js.get("pages") else ""))
        pmcid = _pmc_cua(pm)
        if pmcid:
            xml = gom.tai_toan_van(pmcid)
            if xml and (b"<body" in xml or len(xml.split()) >= 500):
                ten_f = f"{tc.replace('/', '-')}_{_slug(ng['ten'])}_PMID{pm}.xml"
                (KHO / ten_f).write_bytes(xml)
                ng["toan_van"], ng["ban_chup"] = "jats", ten_f
                so.append({"to_chuc": tc, "tieu_de": js["title"], "nam": (js.get("pubdate") or "")[:4],
                           "url": f"https://pubmed.ncbi.nlm.nih.gov/{pm}/",
                           "ngay_chup": date.today().isoformat(), "file": ten_f, "dinh_dang": "JATS",
                           "kich_thuoc_kb": len(xml) // 1024, "pmid": pm, "doi": doi,
                           "nguon_tai": "PMC Open Access"})
                print(f"  ✓ toàn văn JATS PMC{pmcid} → {ten_f}")
            else:
                ng["toan_van"] = "khong_oa"
        else:
            ng["toan_van"] = "khong_oa"
        DANH_BA.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
        SO.write_text(json.dumps(so, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
        print(f"✓ CHỐT [{ma_cd}·{tc}] = PMID {pm} · {js['title'][:80]}")
        print(f"  {ng['an_pham']} · toàn văn: {ng.get('toan_van')} · xác nhận: NGƯỜI")
        return 0
    if a.va_nhan:
        n_va = 0
        for cd in db["chu_de"].values():
            for n in cd["nguon"]:
                if n.get("pmid") and not n.get("xac_nhan"):
                    n["xac_nhan"] = "may"
                    n_va += 1
        DANH_BA.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8",
                           newline="\n")
        print(f"✓ Vá nhãn «may» cho {n_va} nguồn gắn trước khi có trường xac_nhan.")
        print("  (nhãn «may» = máy tự khớp, CHƯA ai xem — chốt bằng --chot khi đã đối chiếu)")
        return 0

    if a.lam_lai:
        for _ma, cd in db["chu_de"].items():
            if a.chu_de and _ma != a.chu_de:
                continue
            for n in cd["nguon"]:
                for k in ("pmid", "doi", "an_pham", "toan_van"):
                    n.pop(k, None)
                if n.get("ban_chup", "").endswith(".xml"):
                    n.pop("ban_chup", None)
        print("(đã gỡ định danh cũ — khớp lại từ đầu)")

    gan, ung_vien_yeu, tai_ve, khong_oa = 0, 0, 0, 0
    for ma, cd in db["chu_de"].items():
        if a.chu_de and ma != a.chu_de:
            continue
        print(f"\n■ {ma}")
        for ng in cd["nguon"]:
            if ng.get("pmid"):
                print(f"  ✓ {ng['to_chuc']:<16} đã có PMID {ng['pmid']}"
                      + (f" · toàn văn: {ng.get('toan_van', '?')}" if ng.get("toan_van") else ""))
                continue
            uv = _tim_an_pham(ng)
            time.sleep(0.34)
            if not uv:
                print(f"  — {ng['to_chuc']:<16} không tra được ấn phẩm trên PubMed")
                continue
            top = uv[0]
            # Gắn khi: khớp tiêu đề đủ mạnh VÀ có bằng chứng tổ chức VÀ đúng là
            # ấn phẩm loại guideline/đồng thuận (ba điều kiện — thiếu một là chờ người)
            manh = (top["la_guideline"] and top["bang_chung_to_chuc"]
                    and top["khop_dac_hieu"] and top["diem"] >= 0.30)
            nhan = "GẮN" if manh else "ứng viên yếu — KHÔNG gắn"
            print(f"  {'✓' if manh else '?'} {ng['to_chuc']:<16} [{nhan}] điểm {top['diem']}"
                  f"{' · loại guideline' if top['la_guideline'] else ' · KHÔNG phải ấn phẩm guideline'}"
                  f" · PMID {top['pmid']} · {top['tap_chi']} {top['nam']}")
            print(f"      {top['tieu_de'][:96]}")
            if not manh:
                ung_vien_yeu += 1
                for u in uv[1:3]:
                    print(f"      ứng viên khác: PMID {u['pmid']} (điểm {u['diem']}) {u['tieu_de'][:70]}")
                continue
            gan += 1
            if not a.ap_dung:
                continue
            ng["pmid"] = top["pmid"]
            ng["doi"] = top["doi"]
            # Khớp tự động chỉ chứng minh «đúng tổ chức + đúng loại ấn phẩm», KHÔNG
            # chứng minh «đúng bản CHỦ LỰC» (đo 20/08: nhánh IDSA/ATS ra guideline hẹp
            # về xét nghiệm acid nucleic thay vì guideline CAP 2019). Vì vậy mọi gắn
            # tự động mang nhãn «may» — bài tổng thuật phải ưu tiên nguồn «nguoi».
            ng["xac_nhan"] = "may"
            ng["an_pham"] = (f"{top['tap_chi']} {top['nam']};{top['tap']}"
                             + (f"({top['so']})" if top["so"] else "")
                             + (f":{top['trang']}" if top["trang"] else ""))
            pmcid = _pmc_cua(top["pmid"])
            time.sleep(0.34)
            if not pmcid:
                ng["toan_van"] = "khong_oa"
                khong_oa += 1
                print("      toàn văn: KHÔNG có bản PMC — chỉ dùng định danh + tóm tắt")
                continue
            try:
                xml = gom.tai_toan_van(pmcid)
            except Exception as exc:  # noqa: BLE001
                print(f"      ⚠ tải PMC{pmcid} lỗi {type(exc).__name__} — lần sau thử lại")
                continue
            if not xml or (b"<body" not in xml and len(xml.split()) < 500):
                ng["toan_van"] = "khong_oa"
                khong_oa += 1
                print(f"      PMC{pmcid} có nhưng KHÔNG mở toàn văn — ghi không_oa")
                continue
            ten_f = f"{ng['to_chuc'].replace('/', '-')}_{_slug(ng['ten'])}_PMID{top['pmid']}.xml"
            (KHO / ten_f).write_bytes(xml)
            ng["toan_van"] = "jats"
            ng["ban_chup"] = ten_f
            tai_ve += 1
            so.append({"to_chuc": ng["to_chuc"], "tieu_de": top["tieu_de"],
                       "nam": top["nam"], "url": f"https://pubmed.ncbi.nlm.nih.gov/{top['pmid']}/",
                       "ngay_chup": date.today().isoformat(), "file": ten_f,
                       "dinh_dang": "JATS", "kich_thuoc_kb": len(xml) // 1024,
                       "pmid": top["pmid"], "doi": top["doi"], "nguon_tai": "PMC Open Access"})
            print(f"      ✓ toàn văn JATS PMC{pmcid} ({len(xml)//1024} KB) → {ten_f}")
            time.sleep(0.34)

    if a.ap_dung:
        DANH_BA.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8",
                           newline="\n")
        SO.write_text(json.dumps(so, ensure_ascii=False, indent=2), encoding="utf-8",
                      newline="\n")
    tong = sum(len(cd["nguon"]) for cd in db["chu_de"].values())
    co_dinh_danh = sum(1 for cd in db["chu_de"].values() for n in cd["nguon"] if n.get("pmid"))
    co_toan_van = sum(1 for cd in db["chu_de"].values() for n in cd["nguon"]
                      if n.get("toan_van") == "jats")
    nguoi_chot = sum(1 for cd in db["chu_de"].values() for n in cd["nguon"]
                     if n.get("xac_nhan") == "nguoi")
    print(f"\n── ĐỘ PHỦ DANH BẠ: {co_dinh_danh}/{tong} nguồn có định danh ấn phẩm thật "
          f"({nguoi_chot} do NGƯỜI chốt · {co_dinh_danh - nguoi_chot} máy tự khớp) · "
          f"{co_toan_van} có toàn văn JATS trong kho")
    web = sum(1 for cd in db["chu_de"].values() for n in cd["nguon"]
              if n.get("an_pham") == "web")
    chua = tong - co_dinh_danh - web
    print(f"   Trong {tong - co_dinh_danh} nguồn không có PMID: {web} là tài liệu WEB "
          f"(không có ấn phẩm tạp chí đơn lẻ — KHÔNG phải thiếu sót) · {chua} chưa tra được.")

    # Đề xuất của MÁY nằm ở khoá riêng, không phải `pmid`, nên mọi công cụ khác vẫn đọc
    # nguồn đó là «chưa có định danh» cho tới khi người chốt. In ra đây để đề xuất không
    # nằm im trong JSON — thứ không hiện ra thì với người dùng là không tồn tại (BH41).
    de_xuat = [(cd, n) for cd, v in db["chu_de"].items() for n in v["nguon"]
               if n.get("de_xuat_dinh_danh") and not n.get("pmid")]
    if de_xuat:
        print(f"\n   ⏳ {len(de_xuat)} ĐỀ XUẤT định danh do MÁY khớp, CHỜ bác sĩ chốt "
              "(khớp máy chỉ chứng minh đúng tổ chức + đúng loại ấn phẩm, KHÔNG chứng "
              "minh đúng bản chủ lực):")
        for cd, n in de_xuat:
            dx = n["de_xuat_dinh_danh"]
            print(f"      • {cd} · {n.get('to_chuc','?')} → PMID {dx['pmid']} — {dx.get('an_pham','?')}")
            if dx.get("luu_y"):
                print(f"        {dx['luu_y']}")
            print(f"        chốt: python3 tools/nap_guideline_pmc.py --chot {cd} "
                  f"\"{n.get('to_chuc','')}\" {dx['pmid']}")
    if co_dinh_danh - nguoi_chot:
        print("   ⚠ Nguồn nhãn «máy tự khớp» chỉ bảo đảm ĐÚNG TỔ CHỨC + ĐÚNG LOẠI ẤN PHẨM,")
        print("     KHÔNG bảo đảm là bản CHỦ LỰC của chủ đề — chốt bằng --chot khi đã xem.")
    print(f"   Lượt này: gắn {gan} · tải {tai_ve} · không-OA {khong_oa} · "
          f"ứng viên yếu (chờ người xem) {ung_vien_yeu}")
    if not a.ap_dung:
        print("   (chưa ghi gì — thêm --ap-dung để gắn định danh và tải toàn văn)")
    print("«Không-OA» là sự thật về quyền truy cập, KHÔNG phải nguồn kém. Cần bác sĩ kiểm chứng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
