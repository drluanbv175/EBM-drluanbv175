#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CÁCH LY tệp Unpaywall CŨ không mang giấy phép mở ra khỏi kho toàn văn (20/11/2026).

VÌ SAO CÓ
=========
Trước bản vá BH160 (04/10/2026 13:47, commit 82ed40c9), tầng 2 Unpaywall lưu MỌI `best_oa_location` có `is_oa` — cả bản
đọc-miễn-phí không giấy phép mở của NXB «cấm» (uỷ quyền 03/10 của bác sĩ là uỷ quyền ĐỌC, «KHÔNG lưu toàn văn») và của NXB chưa
kiểm điều khoản. Nhật ký 04/10 đếm 32/42 tệp `_UPW` như vậy và để việc dữ liệu chờ bác sĩ. Ngày 20/11/2026 bác sĩ («Hoàn thiện
tất cả vấn đề trên») chọn «Dời ra kho cách ly (Khuyến nghị)»: CHUYỂN (không xoá) các tệp đó ra thư mục cách ly ngoài kho; bài
nào còn cần thì lấy lại qua làn Chrome có uỷ quyền. Tệp lưu SAU bản vá đã qua cổng giấy phép lúc lưu ⇒ không thuộc phạm vi.

LUẬT
====
  • Phạm vi: `PMID-<n>_UPW.pdf|html` (tên hợp lệ theo cổng) tạo TRƯỚC mốc `--truoc` (mặc định mốc BH160). `--tat-ca` bỏ mốc.
  • Giữ lại khi CHÍNH TỆP mang dấu giấy phép Creative Commons (cùng luật bộ kiểm API `quyen_gui_toan_van`: tên tệp không
    chứng minh giấy phép). PDF đọc chữ 4 trang đầu + 2 trang cuối (pypdf); đọc lỗi ⇒ coi như KHÔNG thấy giấy phép.
    `--giu PMID…` giữ tệp đã đối chiếu giấy phép bằng nguồn khác (vd Unpaywall chỉ ghi MỘT giấy phép mở cho bài — 20/11/2026:
    PMID 42343056 Springer CC BY, bộ dò chữ PDF bỏ sót); lý do ghi vào báo cáo.
  • Chốt bảo phủ: tệp mà việc dời làm một mục «Áp dụng ngay» mất bằng chứng đọc toàn văn DUY NHẤT (theo đúng định nghĩa cổng
    `verify_dashboard.co_toan_van_trong_kho`) ⇒ KHÔNG dời, trừ khi `--ca-muc-apply` (bác sĩ chấp nhận cổng chặn tới khi lấy lại).
  • BẢN IN đi theo tệp nguồn (thêm 20/11/2026, tối): `PMID-<n>_BANIN.pdf` mà dải đầu trang ghi «nguồn: PMID-<n>_UPW.*» (do
    `in_pdf_toan_van_kho.py` in ngày 18/10 từ chính tệp UPW) mang CÙNG bản quyền với tệp nguồn ⇒ tệp nguồn đã/đang cách ly thì bản
    in cũng chuyển theo (không xoá). Bản in KHÔNG được cổng toàn văn đếm (BANIN không khớp `TEN_TEP_TOAN_VAN`) nên dời nó không
    đổi bảo phủ; PMID còn bản hợp lệ (CHR/PMC) thì in lại bằng `in_pdf_toan_van_kho.py --pmid … --ap-dung`. Bản EndNote đã gắn
    nằm trong thư viện EndNote, công cụ này không đụng. `--khong-ban-in` bỏ bước này.
  • `--ap-dung` chuyển tệp vào `EBM-Dashboards/_cach_ly_toan_van/upw-khong-giay-phep-mo-<YYYYMMDD>/` kèm `MANIFEST.json`
    (tên, PMID, sha256, kích thước, ngày tạo, lý do, mức quyết định, có làm mất bảo phủ không). Không ghi đè tệp đã có ở đích,
    KHÔNG BAO GIỜ xoá. Mặc định chạy khô.
Mã thoát: 0 xong/không còn gì · 1 còn tệp bị chốt bảo phủ giữ lại · 2 không đo được (vắng kho) · 3 từ chối (đích đã có tệp).
Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
VD_NGUON = REPO / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "verify_dashboard.py"
MOC_BH160 = dt.datetime(2026, 10, 4, 13, 47, 32, tzinfo=dt.timezone(dt.timedelta(hours=7)))
THU_MUC_CACH_LY = "_cach_ly_toan_van"
DAU_CC = re.compile(r"creativecommons\.org/(?:licenses|publicdomain)/|\bCC[ -]BY(?:[ -](?:NC|ND|SA))*\b|\bCC0\b"
                    r"|Creative Commons (?:Attribution|Zero|licen[cs]e)", re.I)


def _nap(ten: str, duong: Path):
    sp = importlib.util.spec_from_file_location(ten, duong)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


def goc_dashboards() -> Path:
    try:
        p = _nap("_clu_bst", REPO / "tools" / "ban_sao_tran.py").duong_goc("EBM-Dashboards", REPO)
    except Exception:  # noqa: BLE001
        p = None
    if p is None and os.environ.get("EBM_WORKSPACE_ROOT"):
        p = Path(os.environ["EBM_WORKSPACE_ROOT"]) / "EBM-Dashboards"
    return p or (REPO / "EBM-Dashboards")


def thoi_diem_tao(p: Path) -> dt.datetime:
    """Ngày TẠO tệp (macOS/Windows 3.12+: st_birthtime; Windows cũ: st_ctime; Linux: st_mtime — không có ngày tạo)."""
    st = p.stat()
    ts = getattr(st, "st_birthtime", None)
    if ts is None:
        ts = st.st_ctime if os.name == "nt" else st.st_mtime
    return dt.datetime.fromtimestamp(ts, tz=dt.timezone.utc)


def chu_cua_tep(p: Path) -> str:
    """Chữ để tìm dấu giấy phép. HTML: nguyên văn (400 nghìn ký tự đầu). PDF: 4 trang đầu + 2 trang cuối. Lỗi ⇒ chuỗi rỗng."""
    if p.suffix == ".html":
        try:
            return p.read_text(encoding="utf-8", errors="replace")[:400_000]
        except OSError:
            return ""
    try:
        from pypdf import PdfReader
        rd = PdfReader(str(p))
        n = len(rd.pages)
        chi_so = sorted(set(list(range(min(4, n))) + list(range(max(0, n - 2), n))))
        return "\n".join((rd.pages[i].extract_text() or "") for i in chi_so)
    except Exception:  # noqa: BLE001 — PDF hỏng/mã hoá ⇒ không thấy giấy phép (fail-closed: không giữ vì đoán)
        return ""


def co_giay_phep_mo(p: Path) -> bool:
    return bool(DAU_CC.search(chu_cua_tep(p)))


def muc_theo_pmid(dash: Path, V) -> dict[str, set[str]]:
    ra: dict[str, set[str]] = {}
    for f in sorted(dash.glob("WebDashboard_*.html")):
        blk = V.extract_data_block(f.read_text(encoding="utf-8", errors="replace"))
        if not blk:
            continue
        for ch in V.split_items(blk):
            pm = (V.field(ch, "pmid") or "").strip()
            if V.PMID_RE.match(pm):
                ra.setdefault(pm, set()).add(V.field(ch, "decision") or "khac")
    return ra


def con_bao_phu_khi_bo(pmid: str, bo: Path, kho: Path, V, bsd: set[str]) -> bool:
    """PMID còn «đã đọc toàn văn» theo cổng nếu BỎ tệp `bo` (cùng định nghĩa `co_toan_van_trong_kho`)."""
    for q in sorted(kho.glob("PMID-%s_*" % pmid)):
        if q == bo:
            continue
        m = V._TEN_TEP_TOAN_VAN.fullmatch(q.name)
        if m and m.group(1) == pmid and q.is_file() and (q.suffix != ".html" or V._html_la_toan_van(q)):
            return True
    return (kho / "trinh_duyet" / ("PMID-%s.json" % pmid)).exists() or pmid in bsd


def quet(kho: Path, dash: Path, *, truoc: dt.datetime | None, V=None, giu: set[str] | frozenset = frozenset()) -> list[dict]:
    V = V or _nap("_clu_vd", VD_NGUON)
    muc = muc_theo_pmid(dash, V)
    bsd = V._bac_si_da_doc_kho(kho)
    ra = []
    for q in sorted(kho.glob("PMID-*_UPW.*")):
        m = V._TEN_TEP_TOAN_VAN.fullmatch(q.name)
        if not m or not q.is_file():
            continue
        tao = thoi_diem_tao(q)
        if truoc is not None and tao >= truoc:
            continue
        pm = m.group(1)
        mo = pm in giu or co_giay_phep_mo(q)
        tinh = q.suffix != ".html" or V._html_la_toan_van(q)
        mat = (not mo) and tinh and "apply" in muc.get(pm, set()) and not con_bao_phu_khi_bo(pm, q, kho, V, bsd)
        ra.append({"tep": q.name, "pmid": pm, "tao_luc": tao.isoformat(timespec="seconds"), "giay_phep_mo": mo,
                   "tinh_la_toan_van": tinh, "quyet_dinh": sorted(muc.get(pm, set())), "mat_bao_phu_apply": mat})
    return ra


NGUON_BAN_IN = re.compile(r"nguồn:\s*(PMID-\d{1,9}_[A-Z]+\.[a-z]+)")


def chu_trang_dau(p: Path) -> str:
    """Chữ trang 1 của PDF (dải đầu trang của bản in). Lỗi đọc ⇒ chuỗi rỗng."""
    try:
        from pypdf import PdfReader
        return PdfReader(str(p)).pages[0].extract_text() or ""
    except Exception:  # noqa: BLE001 — PDF hỏng ⇒ không biết nguồn ⇒ không dời vì đoán
        return ""


def ten_da_cach_ly(dash: Path) -> set[str]:
    """Tên mọi tệp nguồn đã nằm trong một MANIFEST cách ly (mọi đợt). Manifest hỏng ⇒ bỏ qua đợt đó."""
    ra: set[str] = set()
    for mf in sorted((dash / THU_MUC_CACH_LY).glob("*/MANIFEST.json")):
        try:
            ra |= {str(t.get("tep")) for t in json.loads(mf.read_text(encoding="utf-8")).get("tep", [])}
        except (OSError, ValueError, AttributeError):
            continue
    return ra


def quet_ban_in(kho: Path, dash: Path, sap_cach_ly: set[str] | frozenset = frozenset()) -> list[dict]:
    """Bản in `PMID-<n>_BANIN.pdf` sinh từ tệp UPW đã cách ly (theo manifest) hoặc SẮP cách ly lượt này.

    Chỉ nhận khi dải đầu trang ghi ĐÚNG tên tệp nguồn đó VÀ tệp nguồn không còn ở kho (hoặc đang được dời) — bản in từ CHR/PMC
    của cùng PMID không bị đụng."""
    ra = []
    for ten in sorted(ten_da_cach_ly(dash) | set(sap_cach_ly)):
        m = re.fullmatch(r"PMID-(\d{1,9})_UPW\.(?:html|pdf)", ten)
        if not m:
            continue
        pm = m.group(1)
        b = kho / f"PMID-{pm}_BANIN.pdf"
        if not b.is_file() or ((kho / ten).exists() and ten not in sap_cach_ly):
            continue
        n = NGUON_BAN_IN.search(chu_trang_dau(b))
        if not n or n.group(1) != ten:
            continue
        khac = sorted(q.name for q in kho.glob(f"PMID-{pm}_*")
                      if q.name not in (b.name, ten) and q.suffix.lower() in (".html", ".xml", ".pdf"))
        ra.append({"tep": b.name, "pmid": pm, "nguon_ban_in": ten, "con_nguon_khac": khac})
    return ra


def ap_dung_ban_in(kho: Path, dich: Path, ds: list[dict], *, ghi: bool) -> tuple[int, list[str]]:
    """Chuyển bản in theo tệp nguồn đã cách ly. Không ghi đè; không xoá. Trả (mã, dòng báo cáo)."""
    if not ds:
        return 0, []
    trung = [x["tep"] for x in ds if (dich / x["tep"]).exists()]
    if trung:
        return 3, [f"✗ đích {dich} đã có bản in cùng tên (vd {trung[0]}) — không ghi đè; bác sĩ xem trước"]
    in_lai = [x["pmid"] for x in ds if any(t.endswith((".html", ".xml")) for t in x["con_nguon_khac"])
              and not any(t.endswith(".pdf") for t in x["con_nguon_khac"])]
    khong_con = [x["pmid"] for x in ds if not x["con_nguon_khac"]]
    if not ghi:
        dong = [f"(chạy khô) sẽ CHUYỂN {len(ds)} bản in BANIN sinh từ tệp UPW cách ly sang {dich}"]
    else:
        dich.mkdir(parents=True, exist_ok=True)
        tep_mf = dich / "MANIFEST.json"
        try:
            mf = json.loads(tep_mf.read_text(encoding="utf-8")) if tep_mf.exists() else {"tep": []}
        except (OSError, ValueError):
            return 3, [f"✗ {tep_mf} hỏng — không ghi chồng; bác sĩ xem trước"]
        for x in ds:
            nguon = kho / x["tep"]
            du_lieu = nguon.read_bytes()
            shutil.move(str(nguon), str(dich / x["tep"]))
            if not (dich / x["tep"]).exists() or nguon.exists():
                return 3, [f"✗ chuyển {x['tep']} không trọn — dừng; kiểm cả hai nơi"]
            mf.setdefault("tep", []).append(dict(
                x, loai="ban_in", sha256=hashlib.sha256(du_lieu).hexdigest(), kich_thuoc=len(du_lieu),
                chuyen_luc=dt.datetime.now().isoformat(timespec="seconds"),
                ly_do=f"bản in sinh từ {x['nguon_ban_in']} (đã cách ly) — cùng bản quyền với tệp nguồn"))
            tep_mf.write_text(json.dumps(mf, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        dong = [f"✓ đã CHUYỂN {len(ds)} bản in BANIN theo tệp nguồn sang {dich}"]
    if in_lai:
        dong.append(f"  ↻ {len(in_lai)} PMID còn toàn văn hợp lệ dạng HTML/XML — in lại: python3 tools/in_pdf_toan_van_kho.py "
                    f"--pmid {' '.join(in_lai)} --ap-dung")
    if khong_con:
        dong.append(f"  ⚠ {len(khong_con)} PMID không còn toàn văn nào trong kho sau khi dời ({', '.join(khong_con)}) — lấy lại qua"
                    " làn Chrome có uỷ quyền nếu còn cần")
    dong.append("  ⓘ bản đã gắn trong EndNote nằm trong thư viện EndNote — công cụ này không đụng")
    return 0, dong


def ap_dung(kho: Path, dich: Path, ds: list[dict], *, ca_muc_apply: bool, ghi: bool,
            hom_nay: dt.date | None = None) -> tuple[int, list[str]]:
    """Chuyển tệp KHÔNG giấy phép mở sang `dich`. Không ghi đè; không xoá. Trả (mã, dòng báo cáo)."""
    chon = [x for x in ds if not x["giay_phep_mo"] and (ca_muc_apply or not x["mat_bao_phu_apply"])]
    giu = [x for x in ds if not x["giay_phep_mo"] and x["mat_bao_phu_apply"] and not ca_muc_apply]
    dong = []
    trung = [x["tep"] for x in chon if (dich / x["tep"]).exists()]
    if trung:
        return 3, [f"✗ đích {dich} đã có {len(trung)} tệp cùng tên (vd {trung[0]}) — không ghi đè; bác sĩ xem trước"]
    if not ghi:
        dong.append(f"(chạy khô) sẽ CHUYỂN {len(chon)} tệp sang {dich} — thêm --ap-dung để chuyển")
    else:
        dich.mkdir(parents=True, exist_ok=True)
        tep_mf = dich / "MANIFEST.json"
        try:
            mf = json.loads(tep_mf.read_text(encoding="utf-8")) if tep_mf.exists() else None
        except (OSError, ValueError):
            return 3, [f"✗ {tep_mf} hỏng — không ghi chồng; bác sĩ xem trước"]
        mf = mf or {"_about": "Tệp Unpaywall lưu TRƯỚC bản vá BH160 (04/10/2026) KHÔNG mang giấy phép mở — CHUYỂN khỏi kho toàn văn "
                              "theo quyết định của bác sĩ 20/11/2026 («Dời ra kho cách ly (Khuyến nghị)»). Không xoá. Bài còn cần "
                              "thì lấy lại qua làn Chrome có uỷ quyền. Sinh bằng tools/cach_ly_upw_khong_giay_phep.py.",
                    "tep": []}
        for x in chon:
            nguon = kho / x["tep"]
            du_lieu = nguon.read_bytes()
            ban_ghi = dict(x, sha256=hashlib.sha256(du_lieu).hexdigest(), kich_thuoc=len(du_lieu),
                           chuyen_luc=dt.datetime.now().isoformat(timespec="seconds"),
                           ly_do="không thấy dấu giấy phép Creative Commons trong tệp; lưu trước bản vá BH160")
            shutil.move(str(nguon), str(dich / x["tep"]))
            if not (dich / x["tep"]).exists() or nguon.exists():
                return 3, [f"✗ chuyển {x['tep']} không trọn — dừng; kiểm cả hai nơi"]
            mf["tep"].append(ban_ghi)
            tep_mf.write_text(json.dumps(mf, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        dong.append(f"✓ đã CHUYỂN {len(chon)} tệp sang {dich} (manifest {tep_mf.name})")
    for x in giu:
        dong.append(f"  ⏸ GIỮ {x['tep']} — dời đi làm mục «Áp dụng ngay» PMID {x['pmid']} mất bằng chứng toàn văn duy nhất: lấy "
                    "lại bản hợp lệ (PMC/làn Chrome có uỷ quyền) trước, hoặc bác sĩ chấp nhận chặn rồi chạy lại với --ca-muc-apply")
    return (1 if giu else 0), dong


def main(argv: list[str] | None = None, *, dash: Path | None = None) -> int:
    ap = argparse.ArgumentParser(description="Cách ly tệp Unpaywall cũ không giấy phép mở (chạy khô mặc định)")
    ap.add_argument("--truoc", default=MOC_BH160.isoformat(), help="chỉ xét tệp tạo trước mốc này (ISO, mặc định mốc BH160)")
    ap.add_argument("--tat-ca", action="store_true", help="bỏ mốc thời gian — xét mọi tệp _UPW")
    ap.add_argument("--giu", nargs="*", default=[], metavar="PMID", help="giữ tệp đã đối chiếu giấy phép mở bằng nguồn khác")
    ap.add_argument("--ca-muc-apply", action="store_true", help="dời cả tệp làm mục apply mất bảo phủ (bác sĩ chấp nhận chặn)")
    ap.add_argument("--khong-ban-in", action="store_true", help="không dời bản in BANIN sinh từ tệp UPW cách ly")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--ap-dung", action="store_true")
    a = ap.parse_args(argv)
    dash = Path(dash or goc_dashboards())
    kho = dash / "toan_van_oa"
    if not kho.is_dir():
        print(f"⚪ không thấy kho {kho} — không đo được")
        return 2
    truoc = None if a.tat_ca else dt.datetime.fromisoformat(a.truoc)
    ds = quet(kho, dash, truoc=truoc, giu={x for x in a.giu if re.fullmatch(r"\d{6,9}", x)})
    if a.json:
        print(json.dumps(ds, ensure_ascii=False, indent=1))
    khong = [x for x in ds if not x["giay_phep_mo"]]
    print(f"Tệp _UPW trong phạm vi: {len(ds)} · có giấy phép mở (giữ) {len(ds) - len(khong)} · KHÔNG giấy phép mở {len(khong)}"
          f" (trong đó làm mục apply mất bảo phủ: {sum(x['mat_bao_phu_apply'] for x in khong)})")
    dich = dash / THU_MUC_CACH_LY / ("upw-khong-giay-phep-mo-" + dt.date.today().strftime("%Y%m%d"))
    ma, dong = ap_dung(kho, dich, ds, ca_muc_apply=a.ca_muc_apply, ghi=a.ap_dung)
    print("\n".join(dong))
    if not a.khong_ban_in and ma != 3:
        sap = {x["tep"] for x in ds if not x["giay_phep_mo"] and (a.ca_muc_apply or not x["mat_bao_phu_apply"])}
        bi = quet_ban_in(kho, dash, sap if not a.ap_dung else frozenset())
        print(f"Bản in BANIN sinh từ tệp UPW đã/sắp cách ly: {len(bi)}")
        ma_bi, dong_bi = ap_dung_ban_in(kho, dich, bi, ghi=a.ap_dung)
        if dong_bi:
            print("\n".join(dong_bi))
        ma = 3 if ma_bi == 3 else ma
    print("Cần bác sĩ kiểm chứng.")
    return ma


if __name__ == "__main__":
    raise SystemExit(main())
