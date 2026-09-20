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
            if len(vb.split()) < 500 or "Cookies must be enabled" in vb:
                print(f"  ⚠ Unpaywall {pm}: trang trả về KHÔNG phải toàn văn "
                      f"({len(vb.split())} từ) — từ chối, không lưu")
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
    da_co_sau = {re.search(r"PMID-(\d+)_", p.name).group(1) for p in KHO.glob("PMID-*.xml")}
    tong_co = len(da_co_sau)
    phu_quet = len(pmids & da_co_sau)
    (KHO / "DO-PHU-OA.md").write_text(
        f"# ĐỘ PHỦ TOÀN VĂN OA — kho dùng chung dashboard — {date.today().isoformat()}\n\n"
        f"- Kho hiện có **{tong_co}** toàn văn OA; tập vừa quét phủ **{phu_quet}/{len(pmids)}**\n"
        f"- Lượt này: +{moi} tải mới · {len(khong_oa)} có PMC nhưng không-OA · "
        f"{len(khong_pmc)} không có bản PMC\n\n"
        "> Phần không-OA cần quyền truy cập của bác sĩ — độ phủ thấp là SỰ THẬT về OA,\n"
        "> không phải lỗi. Cần bác sĩ kiểm chứng.\n", encoding="utf-8")
    print(f"  +{moi} toàn văn mới · không-OA {len(khong_oa)} · không-PMC {len(khong_pmc)} "
          f"→ kho {tong_co}/{len(pmids)} PMID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
