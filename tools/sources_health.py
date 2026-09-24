#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SỨC KHOẺ SỔ NGUỒN — LÔ A PHA 4 (15/08/2026).

«Nguồn hỏng im lặng» là một trong bốn nguyên nhân gốc của bỏ sót (LÔ F), nên sổ
nguồn phải có máy đo riêng: nguồn nào sống, lần thành công gần nhất bao giờ,
nguồn nào hỏng quá 2 chu kỳ. Thuần stdlib, chạy được cả hai trình thông dịch.

Ba lớp kiểm, tách bạch (BH08 — không gộp «không biết» với «có vấn đề»):
  • active + access=api  → thăm sống THẬT (HEAD/GET nhỏ, host đã nằm trong danh
    sách egress được phê duyệt — chính là lý do chúng active được).
  • active + access=file → tuổi file so với scan_frequency.
  • not-covered          → KHÔNG thăm (P2/P5): chỉ đếm và in known_gap — khoảng
    trống phải HIỆN RA mỗi lần chạy, không được chìm.

Mã thoát: 0 = mọi nguồn active khoẻ · 1 = có degraded/broken · 2 = sổ hỏng.
`--im-khi-on` cho hook. Kết quả ghi ngược `last_success_at` (chỉ khi THÀNH CÔNG).

VÁ 24/09/2026 — PHIÊN CLOUD (audit/15 §8). Môi trường Cloud «Trusted» cho proxy thoát mạng
TỪ CHỐI (CONNECT 403, chính sách) mọi host API y văn. Bản cũ đọc 403 của PROXY như nguồn hỏng
⇒ ghi DEGRADED/BROKEN cho 7–10 nguồn đang khoẻ VÀO SỔ TRACKED `data/sources.json` — một lần
commit từ Cloud là làm bẩn sổ dùng chung của mọi máy. Nay:
  • proxy từ chối theo chính sách = KHÔNG ĐO ĐƯỢC (⚪), không đổi `status` (BH08);
  • trên phiên Cloud KHÔNG ghi sổ (chỉ báo cáo) — trạng thái nguồn do mạng CỦA MÔI TRƯỜNG
    quyết định, không phải của nguồn; `--khong-ghi` ép cùng hành vi ở máy khác;
  • nguồn file `medical-ebm-automation/…` phân giải qua `duong_goc()` (Cloud: anh em, không lồng)
    — bản cũ báo SRC-003 BROKEN trên Cloud dù nền Retraction Watch có mặt.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import date, datetime
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

GOC = Path(__file__).resolve().parents[1]
# VÁ 07/09/2026: `GOC / "medical-ebm-automation"` giả định LỒNG — sai trên phiên
# cloud (anh em của GOC). Dùng duong_goc() — xem tools/ban_sao_tran.py.
import importlib.util as _ilu_sh  # noqa: E402
_sp_sh = _ilu_sh.spec_from_file_location(
    "_bst_sh", Path(__file__).resolve().parent / "ban_sao_tran.py")
_bst_sh = _ilu_sh.module_from_spec(_sp_sh)
_sp_sh.loader.exec_module(_bst_sh)
_MEA_GOC = _bst_sh.duong_goc("medical-ebm-automation", GOC) or (GOC / "medical-ebm-automation")
SO = GOC / "data" / "sources.json"
# Điểm thăm rẻ nhất của từng API (đều đã phê duyệt egress từ trước):
DIEM_THAM = {
    "SRC-001": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?retmode=json",
    "SRC-002": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?retmode=json",
    "SRC-004": "https://api.crossref.org/works?rows=0",
    "SRC-005": "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=PMID:1&format=json&pageSize=1",
    "SRC-006": "https://api.fda.gov/drug/label.json?limit=1",
    "SRC-007": "https://api.openalex.org/works?per-page=1&mailto=bsluanbv175@gmail.com",
    # SRC-020 (kcb.vn) và SRC-037 (NICE qua Europe PMC) — thêm 22/09/2026 cùng đợt đóng 4 khoảng
    # trống nguồn. Cả hai miễn phí, không hạn mức, không cần khoá — đã kiểm reachability RIÊNG
    # từ chính môi trường chạy chốt này trước khi thêm (khác CORE ở dưới, nơi vấn đề là thiếu
    # header xác thực chứ không phải reachability): kcb.vn trả HTTP 200 thật; Europe PMC đã dùng
    # chung ổn định cho SRC-005.
    "SRC-020": "https://kcb.vn/phac-do",
    "SRC-037": "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=PMID:1&format=json&pageSize=1",
    # CỐ Ý KHÔNG có SRC-032/033/034/035 (Scopus/CORE/Consensus/SerpApi) — thử thêm CORE
    # 22/09/2026 (miễn phí, tưởng an toàn để thăm sống định kỳ) rồi PHÁT HIỆN NGAY lỗi: `_tham()`
    # không gắn header Authorization, nên probe đi ẨN DANH và bị core.ac.uk giới hạn nhịp CHẶT
    # HƠN nhiều so với khi có khoá thật — một lượt `run.py test-live core` thật ngay trước đó
    # (dùng khoá) đã đủ để lượt probe ẩn danh kế tiếp nhận HTTP 429, khiến sources_health.py
    # ghi "degraded" SAI cho một nguồn đang khoẻ. Ba nguồn kia (Scopus/Consensus/SerpApi) vốn
    # đã tránh DIEM_THAM vì tốn hạn mức trả phí/tháng; CORE bị loại vì LÝ DO KHÁC — probe không
    # xác thực không phản ánh đúng tình trạng của client CÓ xác thực. Không thêm lại cho tới khi
    # `_tham()` biết gắn Authorization theo từng nguồn (việc chưa làm).
}
CHU_KY_NGAY = {"daily": 1, "weekly": 7, "monthly": 31, "quarterly": 92, "ad-hoc": 3650}


# Proxy thoát mạng của MÔI TRƯỜNG từ chối theo chính sách (vd Cloud «Trusted») — khác hẳn
# nguồn trả lỗi: request chưa từng tới nguồn.
_PROXY_TU_CHOI_RE = re.compile(r"Tunnel connection failed:\s*(403|407)\b")

OK, LOI, CHAN_MOI_TRUONG = "ok", "loi", "chan_moi_truong"


def la_phien_cloud() -> bool:
    return os.environ.get("CLAUDE_CODE_REMOTE", "").strip().lower() == "true"


def _tham(url: str) -> str:
    """OK | LOI | CHAN_MOI_TRUONG. Chỉ LOI mới được hạ trạng thái nguồn."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ebm-sources-health/1.0"})
        with urllib.request.urlopen(req, timeout=12) as r:
            return OK if 200 <= r.status < 400 else LOI
    except (urllib.error.URLError, OSError, ValueError) as exc:
        ly_do = getattr(exc, "reason", None)
        if _PROXY_TU_CHOI_RE.search(f"{exc} {ly_do}"):
            return CHAN_MOI_TRUONG
        return LOI


def _duong_file(rel: str) -> Path:
    """Nguồn file khai tương đối theo gốc repo gốc; phần `medical-ebm-automation/…` đi qua
    `duong_goc()` vì trên Cloud engine là thư mục ANH EM, không lồng."""
    tien_to = "medical-ebm-automation/"
    if rel.startswith(tien_to):
        return _MEA_GOC / rel[len(tien_to):]
    return GOC / rel


def lay_thanh_cong_that(sid: str) -> str | None:
    """Ngày CHẠY THẬT gần nhất của nguồn, đọc từ ARTIFACT — không phải ping.

    Vá trung thực 15/08/2026: bản đầu của tool này ghi `last_success_at` ngay khi
    PING endpoint thành công — «endpoint sống» bị đội lốt «đã thu hoạch thành
    công». Một nguồn có thể sống mà 3 tuần không ai chạy; tuyên bố độ phủ đọc
    trường này sẽ nói dối. Nay ping chỉ ghi `last_probe_at`; trường này suy từ
    dấu vết chạy thật:
      SRC-001/002  → lượt quét A2 mới nhất (surveillance/*.json hoặc cursor)
      SRC-003      → mtime kho Retraction Watch
      SRC-004/005  → mốc `kiem_rut_luc` mới nhất trong sổ xác minh theo đúng
                     nguồn (crossref / europepmc·pubmed)
      SRC-006      → dòng «KẾT THÚC … PASS» cuối trong log weekly_safety
    Không có dấu vết → None (KHÔNG BIẾT ≠ hôm nay — BH08).
    """
    try:
        if sid in ("SRC-001", "SRC-002"):
            ung = list((GOC / "EBM-Dashboards" / "surveillance").glob("*.json")) + \
                  [GOC / "EBM-Dashboards" / ".quet-cursor.json"]
            ung = [p for p in ung if p.exists()]
            if ung:
                return datetime.fromtimestamp(
                    max(p.stat().st_mtime for p in ung)).date().isoformat()
        if sid == "SRC-007":
            ung = list((GOC / "EBM-Dashboards" / "surveillance").glob("openalex-*.md"))
            if ung:
                return datetime.fromtimestamp(
                    max(p.stat().st_mtime for p in ung)).date().isoformat()
        if sid == "SRC-003":
            d = _MEA_GOC / "data" / "retraction_watch"
            if d.exists():
                return datetime.fromtimestamp(d.stat().st_mtime).date().isoformat()
        if sid in ("SRC-004", "SRC-005"):
            so = json.loads((GOC / "EBM-Dashboards" / ".so-xac-minh-nguon.json")
                            .read_text(encoding="utf-8")).get("muc", {})
            nhan = {"SRC-004": ("crossref",), "SRC-005": ("europepmc", "pubmed")}[sid]
            moc = [m.get("kiem_rut_luc") or m.get("xac_minh_luc") for m in so.values()
                   if (m.get("nguon_xac_minh") or "") in nhan]
            moc = [x for x in moc if x]
            if moc:
                return max(moc)[:10]
        if sid == "SRC-006":
            log = (_MEA_GOC / "data" / "archive"
                   / "launchd_weekly.log")
            if log.exists():
                for dong in reversed(log.read_text(encoding="utf-8",
                                                   errors="replace").splitlines()):
                    # dạng: «===== 2026-08-13 19:04:11 : KẾT THÚC — ... tổng thể=PASS»
                    if "KẾT THÚC" in dong and "PASS" in dong:
                        return dong[6:16]
    except (OSError, ValueError, KeyError):
        return None
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Sức khoẻ sổ đăng ký nguồn")
    ap.add_argument("--im-khi-on", action="store_true")
    ap.add_argument("--khong-mang", action="store_true", help="bỏ thăm sống, chỉ đọc sổ")
    ap.add_argument("--khong-ghi", action="store_true",
                    help="chỉ báo cáo, không ghi ngược sổ (tự bật trên phiên Cloud)")
    a = ap.parse_args()
    cloud = la_phien_cloud()
    ghi_so = not (a.khong_ghi or cloud)

    try:
        du = json.loads(SO.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"🔴 Sổ nguồn hỏng: {exc}")
        return 2

    hom_nay = date.today()
    loi: list[str] = []
    dong: list[str] = []
    khong_do: list[str] = []
    for s in du["sources"]:
        if s["status"] == "not-covered":
            continue
        chu_ky = CHU_KY_NGAY.get(s["scan_frequency"], 31)
        # (1) thăm sống nguồn API — ping CHỈ ghi last_probe_at («endpoint sống»);
        # last_success_at là chuyện khác hẳn: LẦN CHẠY THẬT, suy từ artifact.
        # Gộp hai thứ này chính là lỗi trung thực đã vá 15/08 (ping ≠ thu hoạch).
        if s["access"] == "api" and s["id"] in DIEM_THAM and not a.khong_mang:
            kq = _tham(DIEM_THAM[s["id"]])
            if kq == OK:
                s["last_probe_at"] = hom_nay.isoformat()
                if s["status"] != "active":
                    dong.append(f"  ↺ {s['id']} hồi phục → active")
                s["status"] = "active"
            elif kq == CHAN_MOI_TRUONG:
                # request chưa tới nguồn — KHÔNG BIẾT, không phải hỏng (BH08)
                khong_do.append(s["id"])
            else:
                # hỏng 1 lần = degraded; quá 2 chu kỳ không thành công = broken
                s["status"] = "degraded"
        that = lay_thanh_cong_that(s["id"])
        if that:
            s["last_success_at"] = that
        # (2) nguồn file: tuổi so với chu kỳ
        if s["access"] == "file" and s.get("endpoint_or_url"):
            f = _duong_file(s["endpoint_or_url"])
            if f.exists():
                tuoi = (datetime.now() - datetime.fromtimestamp(
                    max(p.stat().st_mtime for p in ([f] if f.is_file() else list(f.iterdir()) or [f])))).days
                if tuoi > chu_ky:
                    s["status"] = "degraded"
                    dong.append(f"  ⚠ {s['id']} file {tuoi} ngày tuổi > chu kỳ {chu_ky}ng — chạy làm mới")
            else:
                s["status"] = "broken"
        # (3) quá 2 chu kỳ kể từ last_success → broken (nguồn hỏng không được im)
        ls = s.get("last_success_at")
        if ls:
            try:
                tre = (hom_nay - date.fromisoformat(ls[:10])).days
                if tre > 2 * chu_ky and s["status"] != "active":
                    s["status"] = "broken"
            except ValueError:
                pass
        if s["status"] in ("degraded", "broken"):
            loi.append(f"{s['id']} {s['name'][:50]} → {s['status'].upper()}"
                       f" (thành công gần nhất: {s.get('last_success_at') or 'chưa từng'})")

    if ghi_so:
        du["updated"] = hom_nay.isoformat()
        SO.write_text(json.dumps(du, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if khong_do:
        print(f"⚪ {len(khong_do)} nguồn KHÔNG ĐO ĐƯỢC — proxy môi trường từ chối theo chính sách "
              f"(request chưa tới nguồn, trạng thái giữ nguyên): {', '.join(khong_do)}")
        if cloud:
            print("   Cloud: mở Network access → Custom + thêm host (audit/15 §7) để đo được.")
    if not ghi_so:
        print("ℹ  KHÔNG ghi sổ data/sources.json "
              + ("(phiên Cloud — mạng môi trường, không phải nguồn, quyết định kết quả)."
                 if cloud else "(--khong-ghi)."))

    n_active = sum(1 for s in du["sources"] if s["status"] == "active")
    n_nc = sum(1 for s in du["sources"] if s["status"] == "not-covered")
    if loi:
        print(f"🟠 SỔ NGUỒN: {n_active} active · {len(loi)} degraded/broken · {n_nc} not-covered")
        for x in loi:
            print("  ✗ " + x)
        for x in dong:
            print(x)
        print("  → nguồn hỏng = chuyên khoa đó đang MÙ; không được để im (LÔ F nguyên nhân gốc #4)")
        return 1
    if not a.im_khi_on:
        print(f"🟢 SỔ NGUỒN: {n_active} active khoẻ · {n_nc} not-covered (khoảng trống CÓ khai báo):")
        for s in du["sources"]:
            if s["status"] == "not-covered":
                print(f"  ◌ {s['id']} {s['name'][:58]} — {(s.get('known_gap') or '')[:70]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
