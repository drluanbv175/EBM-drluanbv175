#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GOM TOÀN VĂN OA CHO DASHBOARD LÂM SÀNG — kho DÙNG CHUNG theo PMID (nâng cấp A, 15/08/2026).

Vì sao: bộ máy toàn văn (gom → hỏi → đối chiếu số) đã chạy cho đề tài nghiên cứu
(C1a); phía lâm sàng `kiem_so_lieu` vẫn chỉ đọc TÓM TẮT nên tồn cả lớp ⚪ «không
thấy» dù con số nằm ngay trong thân bài. Tool này phủ kho toàn văn sang lâm sàng.

Khác bản nghiên cứu (`medical-ebm-automation/tools/gom_toan_van_oa.py` — kho THEO
ĐỀ TÀI): kho ở đây DÙNG CHUNG toàn thư mục `EBM-Dashboards/toan_van_oa/`, khoá theo
PMID, tải một lần dùng cho mọi dashboard. TÁI DÙNG nguyên hàm của bản nghiên cứu
(qua importlib — không chép đôi logic, kế thừa luôn bộ lọc `pubmed_pmc` của BH53).

P5 giữ nguyên: chỉ PMC Open Access — không cào nguồn trả phí. Bài không-OA được
ghi rõ, KHÔNG đoán. Chạy lại an toàn: PMID đã có XML thì bỏ qua (idempotent).

Dùng:  python3 tools/gom_toan_van_dashboard.py            # mọi dashboard
       python3 tools/gom_toan_van_dashboard.py --file EBM-Dashboards/WebDashboard_X.html
Mã thoát: 0 = chạy trọn · 2 = hạ tầng (elink chết toàn phần).
"""
from __future__ import annotations

import argparse
import glob
import importlib.util
import re
import sys
import time
from datetime import date
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
DASH = REPO / "EBM-Dashboards"
KHO = DASH / "toan_van_oa"


def _email_lich_su() -> str:
    """Email định danh lịch sự cho API (Unpaywall/NCBI đòi) — đọc theo đúng chuỗi
    ưu tiên của app/config.py: biến môi trường → kho secrets ngoài OneDrive."""
    import os
    e = os.environ.get("NCBI_EMAIL") or os.environ.get("UNPAYWALL_EMAIL")
    if e:
        return e
    sec = Path.home() / ".ebm-secrets" / "medical-ebm-automation.env"
    if sec.exists():
        for d in sec.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"\s*NCBI_EMAIL\s*=\s*(\S+)", d)
            if m:
                return m.group(1).strip("'\"")
    return ""


def _van_ban_tho(du_lieu: bytes) -> str:
    import html as _h
    vb = du_lieu.decode("utf-8", errors="replace")
    vb = re.sub(r"<script.*?</script>|<style.*?</style>", " ", vb, flags=re.S | re.I)
    return re.sub(r"\s+", " ", _h.unescape(re.sub(r"<[^>]+>", " ", vb)))


_DTV = None
# Giá trị `license` của Unpaywall được coi là GIẤY PHÉP MỞ (mọi biến thể CC BY*, CC0, phạm vi công cộng).
GIAY_PHEP_MO_DUNG = ("cc0", "pd", "public-domain")
GIAY_PHEP_MO_TIEN_TO = ("cc-by",)
# PMID bị cổng điều khoản chặn ở lượt gần nhất: (pmid, doi, lý do) — để báo cáo, không phải để thử lại mù.
BO_QUA_UNPAYWALL: list[tuple[str, str, str]] = []


def _nap_dtv():
    """Nạp `tools/doc_toan_van_co_nguoi.py` (bảng điều khoản NXB + uỷ quyền bác sĩ). Lỗi ⇒ None: cổng ĐÓNG với mọi bản
    không mang giấy phép mở (fail-closed), không lặng lẽ cho qua."""
    global _DTV
    if _DTV is None:
        try:
            sp = importlib.util.spec_from_file_location("_dtv_gom_tv", REPO / "tools" / "doc_toan_van_co_nguoi.py")
            mod = importlib.util.module_from_spec(sp)
            sp.loader.exec_module(mod)
            _DTV = mod
        except Exception:  # noqa: BLE001
            _DTV = False
    return _DTV or None


def la_giay_phep_mo(license: str | None) -> bool:
    lic = (license or "").strip().lower()
    return lic in GIAY_PHEP_MO_DUNG or lic.startswith(GIAY_PHEP_MO_TIEN_TO)


def quyet_dinh_unpaywall(doi: str, url: str, license: str | None, *, dtv=None, hom_nay=None) -> tuple[bool, str]:
    """CỔNG ĐIỀU KHOẢN của tầng 2 (04/10/2026) — trả (được LƯU tự động?, lý do). Trước bản vá, tầng này lưu MỌI bản «is_oa»
    (kể cả bản đọc-miễn-phí không giấy phép của NXB đã kết luận «cấm» dùng với AI), trái doctrine §2septies.

    CHỈ bản mang GIẤY PHÉP MỞ (CC BY*, CC0, phạm vi công cộng) được lưu tự động — chính giấy phép cho phép dùng.
    Bản không có giấy phép mở thì KHÔNG lưu, kể cả NXB «cấm» mà bác sĩ đã uỷ quyền: uỷ quyền 03/10 là uỷ quyền ĐỌC («KHÔNG lưu
    toàn văn»); lưu bản sao chỉ trong phiên uỷ quyền có lời bác sĩ, trần mỗi miền và nhịp nghỉ (`phien_uy_quyen_chrome.py`) —
    tải tự động hàng loạt là đúng thứ điều khoản NXB cấm. Lý do trả về phân loại để định tuyến:
    «cam_co_uq» → làn trình duyệt có phiên; «cam_khong_uq» → bác sĩ đọc trực tiếp; «chua_kiem» → đọc trang điều khoản trước."""
    lic = (license or "").strip().lower()
    if la_giay_phep_mo(lic):
        return True, f"giấy phép mở ({lic})"
    dtv = dtv if dtv is not None else _nap_dtv()
    if dtv is None:
        return False, "khong_nap_bang: không nạp được bảng điều khoản NXB — chỉ lưu bản có giấy phép mở"
    ten, dk = dtv.nxb_cua(doi=doi or "", url=url or "")
    if ten and (dk or {}).get("ket_luan") == "cam":
        if dtv.uy_quyen_bac_si(ten, hom_nay):
            return False, (f"cam_co_uq: NXB «cấm» {ten}, bản đọc-miễn-phí không giấy phép mở — uỷ quyền ĐỌC không gồm lưu tự "
                           "động; đọc qua làn trình duyệt (phiên uỷ quyền lưu bản sao)")
        return False, f"cam_khong_uq: NXB «cấm» {ten}, chưa có uỷ quyền của bác sĩ — bác sĩ đọc trực tiếp"
    if ten:
        return False, f"khac: NXB {ten} — kết luận điều khoản «{(dk or {}).get('ket_luan')}» tầng này chưa nhận"
    return False, "chua_kiem: NXB chưa có trong DIEU_KHOAN_NXB và bản OA không mang giấy phép mở — đọc trang điều khoản trước"


# Dấu hiệu TRANG GIỚI THIỆU của cổng kho lưu trữ (Pure/Research Explorer, kho đại học): chỉ tóm tắt + metadata + nút tải.
# Đo 04/10/2026: 15/27 tệp `_UPW.html` trong kho là loại này (gồm 4 mục apply: CHA₂DS₂-VASc 19762550, HAS-BLED 20299623,
# EMPOWER 24733354, SUMMIT 27203508) — vượt ngưỡng 500 từ nên lọt vào kho với nhãn «toàn văn».
DAU_TRANG_GIOI_THIEU = ("Fingerprint", "Access to Document", "Link to publication", "Research output", "Accéder au contenu principal")
DE_MUC_TOAN_VAN = ("Methods", "Results", "Discussion", "Introduction", "METHODS", "RESULTS", "DISCUSSION", "INTRODUCTION")
SO_TU_TOAN_VAN_KHONG_DE_MUC = 6000  # guideline/khuyến cáo dài thường không có đề mục IMRaD (vd Tiêu chuẩn ADA: 18–26 nghìn từ)


def la_toan_van_html(vb: str) -> tuple[bool, str]:
    """(có phải TOÀN VĂN?, lý do) cho văn bản thô của một trang HTML. Toàn văn khi: ≥ 3 đề mục IMRaD và ≥ 2500 từ, HOẶC
    ≥ 6000 từ (guideline dài). Mang dấu trang giới thiệu kho mà dưới 6000 từ ⇒ KHÔNG phải toàn văn."""
    so_tu = len(vb.split())
    de_muc = sum(1 for k in DE_MUC_TOAN_VAN if k in vb)
    dau = [k for k in DAU_TRANG_GIOI_THIEU if k in vb]
    if so_tu >= SO_TU_TOAN_VAN_KHONG_DE_MUC:
        return True, f"{so_tu} từ"
    if dau:
        return False, f"trang giới thiệu kho lưu trữ ({', '.join(dau[:2])}; {so_tu} từ)"
    if so_tu >= 2500 and de_muc >= 3:
        return True, f"{so_tu} từ, {de_muc} đề mục"
    return False, f"không đủ dấu hiệu toàn văn ({so_tu} từ, {de_muc} đề mục IMRaD)"


def dem_toan_van(kho: Path) -> dict[str, set[str]]:
    """PMID có toàn văn trong kho theo LOẠI tệp ở gốc kho (XML JATS · PDF/HTML Unpaywall · _CHR phiên Chrome · TDM…) cộng
    `trinh_duyet/` (đọc qua làn trình duyệt có bác sĩ — hồ sơ trích xuất, KHÔNG lưu bản). Trước 04/10 sổ phủ chỉ đếm `*.xml`
    nên báo thấp hơn thật (203/676 trong khi 337/676 PMID đã có toàn văn hoặc đã được đọc toàn văn)."""
    loai: dict[str, set[str]] = {}
    for q in kho.glob("PMID-*"):
        m = re.match(r"PMID-(\d+)(?:_([A-Za-z]+))?", q.name)
        if not m or not q.is_file():
            continue
        nhan = "XML" if q.suffix.lower() == ".xml" else (m.group(2) or "khác").upper()
        loai.setdefault(nhan, set()).add(m.group(1))
    td = kho / "trinh_duyet"
    if td.is_dir():
        for q in td.glob("PMID-*"):
            m = re.match(r"PMID-(\d+)", q.name)
            if m:
                loai.setdefault("TRINH_DUYET", set()).add(m.group(1))
    return loai


def tang_unpaywall(pmids: list[str], gom=None) -> tuple[int, list[str]]:
    """TẦNG 2 OA — Unpaywall (bác sĩ duyệt gói ② 19/08): bài không có bản PMC vẫn
    thường có bản OA HỢP PHÁP ở repository (bản tác giả tự lưu, Gold OA ngoài PMC).
    Chỉ tải link best_oa_location do Unpaywall xác nhận — KHÔNG cào nguồn trả phí.
    Lưu PMID-<n>_UPW.pdf|.html (doc_sau không parse được PDF — phiên Claude đọc
    trực tiếp bằng skill pdf khi thẩm định). Trả (số tải được, danh sách còn thiếu)."""
    import json as _json
    import urllib.request as _rq
    email = _email_lich_su()
    if not email:
        print("  ⚠ Unpaywall cần email định danh (NCBI_EMAIL trong ~/.ebm-secrets) — bỏ tầng 2.")
        return 0, pmids
    moi_tai, con_thieu = 0, []
    BO_QUA_UNPAYWALL.clear()
    for pm in pmids:
        try:  # DOI qua esummary (id → articleids)
            u = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                 f"?db=pubmed&id={pm}&retmode=json&email={email}")
            js = _json.loads(_rq.urlopen(u, timeout=20).read())
            ids = js["result"][pm].get("articleids", [])
            doi = next((x["value"] for x in ids if x.get("idtype") == "doi"), "")
            if not doi:
                con_thieu.append(pm)
                continue
            uj = _json.loads(_rq.urlopen(
                f"https://api.unpaywall.org/v2/{doi}?email={email}", timeout=25).read())
            loc = uj.get("best_oa_location") or {}
            url = loc.get("url_for_pdf") or loc.get("url")
            if not (uj.get("is_oa") and url):
                con_thieu.append(pm)
                continue
            # CỔNG ĐIỀU KHOẢN — xét TRƯỚC khi mở nội dung (04/10/2026)
            duoc, ly_do = quyet_dinh_unpaywall(doi, url, loc.get("license"))
            if not duoc:
                BO_QUA_UNPAYWALL.append((pm, doi, ly_do))
                print(f"  ⛔ Unpaywall {pm}: KHÔNG lưu — {ly_do}")
                con_thieu.append(pm)
                continue
            req = _rq.Request(url, headers={"User-Agent": "Mozilla/5.0 (EBM-OA-fetch)"})
            phan_hoi = _rq.urlopen(req, timeout=40)
            du_lieu = phan_hoi.read()
            url_cuoi = phan_hoi.geturl() or url
            # Link trỏ về PMC → lấy JATS CHUẨN qua đúng đường PMC (doc_sau/RAG
            # parse được), không giữ bản HTML trang web
            m_pmc = (re.search(r"pmc\.ncbi\.nlm\.nih\.gov/articles/PMC(\d+)", url_cuoi)
                     or re.search(r"/articles/PMC(\d+)/", du_lieu[:4000].decode(
                         "utf-8", errors="replace")))
            if m_pmc and gom is not None:
                xml = gom.tai_toan_van(m_pmc.group(1))
                if xml:
                    (KHO / f"PMID-{pm}_PMC{m_pmc.group(1)}.xml").write_bytes(xml)
                    moi_tai += 1
                    print(f"  ✓ Unpaywall→PMC JATS: {pm} (PMC{m_pmc.group(1)})")
                    time.sleep(0.4)
                    continue
            if du_lieu[:5] == b"%PDF-":
                (KHO / f"PMID-{pm}_UPW.pdf").write_bytes(du_lieu)
                moi_tai += 1
                print(f"  ✓ Unpaywall: {pm} → PDF ({len(du_lieu)//1024} KB)")
                time.sleep(0.4)
                continue
            # CỔNG NỘI DUNG THẬT (bẫy đo được 19/08: trang chặn-cookie 15 từ suýt
            # vào kho làm «toàn văn» — tuần sau máy đọc rác mà tưởng đã thẩm định)
            vb = _van_ban_tho(du_lieu)
            la_tv, vi_sao = la_toan_van_html(vb)
            if not la_tv or "Cookies must be enabled" in vb:
                print(f"  ⚠ Unpaywall {pm}: trang trả về KHÔNG phải toàn văn ({vi_sao}) — từ chối, không lưu")
                con_thieu.append(pm)
                continue
            (KHO / f"PMID-{pm}_UPW.html").write_bytes(du_lieu)
            moi_tai += 1
            print(f"  ✓ Unpaywall: {pm} → HTML ({len(vb.split())} từ chữ thật)")
            time.sleep(0.4)
        except Exception as exc:  # noqa: BLE001 — lỗi MỘT bài không giết cả lượt
            print(f"  ⚠ Unpaywall {pm}: {type(exc).__name__} — chưa lấy được, lần sau thử lại")
            con_thieu.append(pm)
    return moi_tai, con_thieu


def _nap_gom():
    import importlib.util as _ilu_mea
    _sp_mea = _ilu_mea.spec_from_file_location("_bst_gtvd", Path(__file__).resolve().parent / "ban_sao_tran.py")
    _bst_mea = _ilu_mea.module_from_spec(_sp_mea)
    _sp_mea.loader.exec_module(_bst_mea)
    duong = (_bst_mea.duong_goc("medical-ebm-automation", REPO) or (REPO / "medical-ebm-automation")) / "tools" / "gom_toan_van_oa.py"
    sp = importlib.util.spec_from_file_location("gom_tv_nc", duong)
    m = importlib.util.module_from_spec(sp)
    sys.modules["gom_tv_nc"] = m
    sp.loader.exec_module(m)
    return m


def pmids_tu_dashboard(f: Path) -> set[str]:
    t = f.read_text(encoding="utf-8", errors="replace")
    return set(re.findall(r"pmid['\"]?\s*[:=]\s*['\"](\d{6,9})['\"]", t, re.I))


def main() -> int:
    ap = argparse.ArgumentParser(description="Gom toàn văn PMC-OA dùng chung cho dashboard")
    ap.add_argument("--file", nargs="*", help="dashboard cụ thể (mặc định: tất cả)")
    ap.add_argument("--queue", nargs="*",
                    help="file queue/tuan-*.md — gom PMID trong thẻ gói tuần "
                         "(mở rộng 18/08: dây chuyền tuần từng thẩm định 100%% từ tóm tắt)")
    ap.add_argument("--pmid", nargs="*", help="PMID chỉ định thêm")
    ap.add_argument("--unpaywall", action="store_true",
                    help="tầng 2 OA: bài không-PMC thử Unpaywall (bản OA hợp pháp ngoài PMC)")
    ap.add_argument("--gioi-han", type=int, default=0,
                    help="chỉ xử lý N PMID chưa có mỗi lần chạy (0 = không giới hạn)")
    a = ap.parse_args()
    chi_dinh = bool(a.queue or a.pmid)
    files = ([Path(p) for m in a.file for p in glob.glob(m)] if a.file
             else [] if chi_dinh else sorted(DASH.glob("WebDashboard_*.html")))
    files = [f for f in files if f.exists()]
    if not files and not chi_dinh:
        print("✗ Không thấy dashboard nào.")
        return 2
    pmids: set[str] = set()
    for f in files:
        pmids |= pmids_tu_dashboard(f)
    for m in (a.queue or []):
        for q in glob.glob(m):
            qt = Path(q).read_text(encoding="utf-8", errors="replace")
            pmids |= set(re.findall(r"PMID[ :]?(\d{6,9})", qt))
    pmids |= {pm for pm in (a.pmid or []) if re.fullmatch(r"\d{6,9}", pm)}
    KHO.mkdir(parents=True, exist_ok=True)
    da_co = {re.search(r"PMID-(\d+)_", p.name).group(1) for p in KHO.glob("PMID-*.xml")}
    # Sổ «không lấy được» CÓ HẠN DÙNG 30 ngày (vá 15/08 chiều — bản đầu là danh
    # sách trần, tức SỔ ĐEN VĨNH VIỄN: một bài vào PMC-OA muộn (embargo hết,
    # tác giả nộp bản OA…) sẽ không bao giờ được thử lại. Tập OA là tập LỚN DẦN
    # theo thời gian — sổ nhớ phải già đi cùng nó. Dòng: «PMID yyyy-mm-dd»;
    # dòng cũ chỉ có PMID (không ngày) = hết hạn ngay, thử lại lượt này.
    ghi_chu = KHO / "khong-oa.txt"
    khong_pmc_cu: dict[str, str] = {}
    if ghi_chu.exists():
        for dong in ghi_chu.read_text(encoding="utf-8").split("\n"):
            phan = dong.split()
            if phan:
                khong_pmc_cu[phan[0]] = phan[1] if len(phan) > 1 else ""
    han = (date.today() - __import__("datetime").timedelta(days=30)).isoformat()
    con_han = {pm for pm, ngay in khong_pmc_cu.items() if ngay and ngay > han}
    can = sorted(pmids - da_co - con_han)
    if a.gioi_han:
        can = can[: a.gioi_han]
    print(f"Kho chung: {len(da_co)} toàn văn sẵn có · {len(pmids)} PMID trong "
          f"{len(files)} dashboard · cần tra lần này: {len(can)}")
    if not can and not a.unpaywall:
        print("✓ Không có gì mới để gom.")
        return 0
    # (họ lỗi return-sớm 12/08: khi --unpaywall bật, KHÔNG thoát ở đây — tầng 2
    # nằm sau và xét tập thiếu độc lập với sổ back-off của tầng PMC)
    gom = _nap_gom()
    try:
        anh_xa = gom.lien_ket_pmc(can) if can else {}
    except Exception as exc:  # noqa: BLE001
        print(f"🔴 HẠ TẦNG: elink không trả lời ({type(exc).__name__}) — chưa gom, "
              "KHÔNG kết luận độ phủ.")
        return 2
    moi, khong_oa, khong_pmc = 0, [], []
    loi_mang = 0
    for pm in can:
        pmcid = anh_xa.get(pm)
        if not pmcid:
            khong_pmc.append(pm)
            continue
        # Lỗi MỘT bài không được giết CẢ lượt (đo thật 15/08: IncompleteRead ở file
        # 17/600 làm mất trọn lượt chạy dài). Bài lỗi mạng KHÔNG vào danh sách
        # «không-OA» — đó là CHƯA TẢI ĐƯỢC, lần chạy sau thử lại (idempotent).
        try:
            xml = gom.tai_toan_van(pmcid)
        except Exception:  # noqa: BLE001
            loi_mang += 1
            continue
        time.sleep(0.34)
        if xml:
            (KHO / f"PMID-{pm}_PMC{pmcid}.xml").write_bytes(xml)
            moi += 1
        else:
            khong_oa.append(pm)
    if loi_mang:
        print(f"  ⚠ {loi_mang} bài lỗi mạng lượt này — CHƯA tải được (không phải "
              "không-OA); chạy lại tool sẽ thử tiếp.")
    # ghi sổ «không lấy được» KÈM NGÀY — mục vừa tra nhận ngày hôm nay; mục còn
    # hạn giữ nguyên ngày cũ; mục hết hạn mà lượt này không tra tới thì rơi khỏi sổ
    if a.unpaywall:
        # Tầng 2 xét TRỰC TIẾP tập còn thiếu trong kho — KHÔNG để sổ 30-ngày của
        # tầng PMC chặn (sổ đó ghi «không có bản PMC»; Unpaywall là nguồn KHÁC
        # chưa từng thử — back-off của nguồn này không được gác cửa nguồn kia).
        da_bat_ky = {re.search(r"PMID-(\d+)_", q.name).group(1)
                     for q in KHO.glob("PMID-*_*.*")}
        thu = sorted(pmids - da_bat_ky)
        if thu:
            print(f"  Tầng 2 Unpaywall: thử {len(thu)} bài không có bản PMC…")
            upw_moi, _ = tang_unpaywall(thu, gom=gom)
            moi += upw_moi
    hom_nay = date.today().isoformat()
    so_moi = {pm: ngay for pm, ngay in khong_pmc_cu.items() if pm in con_han}
    for pm in list(khong_pmc) + list(khong_oa):
        so_moi[pm] = hom_nay
    ghi_chu.write_text("\n".join(f"{pm} {ngay}" for pm, ngay in sorted(so_moi.items()))
                       + "\n", encoding="utf-8")
    loai = dem_toan_van(KHO)
    da_co_sau = set().union(*loai.values()) if loai else set()
    tong_co = len(da_co_sau)
    phu_quet = len(pmids & da_co_sau)
    chi_tiet = " · ".join(f"{k} {len(v)}" for k, v in sorted(loai.items()))
    bo_qua = "".join(f"  - {pm} (doi:{d}) — {ly}\n" for pm, d, ly in BO_QUA_UNPAYWALL)
    (KHO / "DO-PHU-OA.md").write_text(
        f"# ĐỘ PHỦ TOÀN VĂN — kho dùng chung dashboard — {date.today().isoformat()}\n\n"
        f"- Kho có toàn văn (hoặc đã đọc toàn văn qua làn trình duyệt) cho **{tong_co}** PMID; tập vừa quét phủ "
        f"**{phu_quet}/{len(pmids)}**\n"
        f"- Theo loại (một PMID có thể nhiều loại): {chi_tiet or '—'}\n"
        f"- Lượt này: +{moi} tải mới · {len(khong_oa)} có PMC nhưng không-OA · "
        f"{len(khong_pmc)} không có bản PMC\n"
        + (f"- Tầng 2 Unpaywall — KHÔNG lưu vì điều khoản NXB ({len(BO_QUA_UNPAYWALL)}):\n{bo_qua}" if BO_QUA_UNPAYWALL else "")
        + "\n> Phần không-OA cần quyền truy cập của bác sĩ — độ phủ thấp là SỰ THẬT về OA,\n"
        "> không phải lỗi. Cần bác sĩ kiểm chứng.\n", encoding="utf-8")
    print(f"  +{moi} toàn văn mới · không-OA {len(khong_oa)} · không-PMC {len(khong_pmc)} "
          f"→ kho {tong_co}/{len(pmids)} PMID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
