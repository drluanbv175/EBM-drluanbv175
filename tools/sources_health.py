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

Mã thoát: 0 = không nguồn nào degraded/broken · 1 = có degraded/broken · 2 = sổ hỏng. Nguồn
⚪ KHÔNG ĐO ĐƯỢC không làm đổi mã thoát — nó được nêu tên ở dòng ⚪ và bị TRỪ khỏi số «active
khoẻ» (không đo được ≠ ổn). `--im-khi-on` cho hook. Kết quả ghi ngược `last_success_at` (chỉ khi
THÀNH CÔNG).

VÁ 24/09/2026 — PHIÊN CLOUD (audit/15 §8). Môi trường Cloud «Trusted» cho proxy thoát mạng
TỪ CHỐI (CONNECT 403, chính sách) mọi host API y văn. Bản cũ đọc 403 của PROXY như nguồn hỏng
⇒ ghi DEGRADED/BROKEN cho 7–10 nguồn đang khoẻ VÀO SỔ TRACKED `data/sources.json` — một lần
commit từ Cloud là làm bẩn sổ dùng chung của mọi máy. Nay:
  • proxy từ chối theo chính sách = KHÔNG ĐO ĐƯỢC (⚪), không đổi `status` (BH08);
  • trên phiên Cloud KHÔNG ghi sổ (chỉ báo cáo) — trạng thái nguồn do mạng CỦA MÔI TRƯỜNG
    quyết định, không phải của nguồn; `--khong-ghi` ép cùng hành vi ở máy khác;
  • nguồn file `medical-ebm-automation/…` phân giải qua `duong_goc()` (Cloud: anh em, không lồng)
    — bản cũ báo SRC-003 BROKEN trên Cloud dù nền Retraction Watch có mặt.

VÁ 30/09/2026 — BẢN SAO GIT TRẦN TRÊN MÁY THẬT (BH140). Một worktree git của repo gốc không mang
`medical-ebm-automation/` (không lồng, không anh em). Bản cũ đọc thư mục Retraction Watch vắng mặt
thành «SRC-003 → BROKEN», và — không kèm `--khong-ghi` — GHI nhãn đó vào sổ tracked của worktree.
Bản vá 24/09 chỉ che phiên Cloud. Nay:
  • bản sao trần VÀ không thấy gốc engine ở đâu ⇒ nguồn file của engine là ⚪ «KHÔNG ĐO ĐƯỢC —
    engine vắng»: `status` giữ nguyên, không tính vào mã thoát 1. Cả hai phép dò uỷ quyền cho
    `tools/ban_sao_tran.py` (`ban_sao_git_tran` · `duong_goc`) — không dò riêng ở đây;
  • máy còn ≥ 1 gốc dữ liệu ngoài-git (máy thật, kể cả hỏng dở), hoặc thấy engine mà thiếu đúng
    thư mục nguồn ⇒ vẫn BROKEN: thiếu THẬT không được ⚪ hoá;
  • bản sao trần KHÔNG ghi sổ (như phiên Cloud): ở đó chỉ đo được MỘT PHẦN — không artifact nào để
    suy `last_success_at`, không nguồn file nào — và sổ của worktree là bản chụp sẽ trôi vào PR.
    Sổ sống đo ở cây chính của máy thật.
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
_TEN_ENGINE = "medical-ebm-automation"
_TIEN_TO_ENGINE = _TEN_ENGINE + "/"


def _goc_engine() -> Path | None:
    """Gốc engine THẬT — vị trí lồng (máy thật) rồi anh em (Cloud); `None` khi không có ở đâu.

    Uỷ quyền cho định nghĩa DUY NHẤT `ban_sao_tran.duong_goc()`. Đọc `GOC` lúc GỌI, không chốt
    lúc import: phép thử dựng cây giả bằng cách đổi `GOC`, và mọi nơi trong tệp thấy CÙNG một gốc."""
    return _bst_sh.duong_goc(_TEN_ENGINE, GOC)


def _mea_goc() -> Path:
    """Gốc engine để GHÉP đường dẫn: gốc thật nếu có, không thì vị trí lồng (để `.exists()` ra False)."""
    return _goc_engine() or (GOC / _TEN_ENGINE)


def la_ban_sao_tran() -> bool:
    """Cây này KHÔNG có gốc dữ liệu ngoài-git nào (worktree · clone tươi · CI · Cloud) — uỷ quyền cho
    định nghĩa DUY NHẤT `ban_sao_tran.ban_sao_git_tran()`. Còn ≥ 1 gốc = máy thật, kể cả hỏng dở."""
    return _bst_sh.ban_sao_git_tran(GOC)


sys.path.insert(0, str(Path(__file__).resolve().parent))
from tra_dinh_danh import email_lien_he  # noqa: E402 — email liên hệ lấy từ cấu hình, không viết cứng (27/09/2026)

_MAIL = email_lien_he()
SO = GOC / "data" / "sources.json"
# Điểm thăm rẻ nhất của từng API (đều đã phê duyệt egress từ trước):
DIEM_THAM = {
    "SRC-001": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?retmode=json",
    "SRC-002": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?retmode=json",
    "SRC-004": "https://api.crossref.org/works?rows=0",
    "SRC-005": "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=PMID:1&format=json&pageSize=1",
    "SRC-006": "https://api.fda.gov/drug/label.json?limit=1",
    "SRC-007": "https://api.openalex.org/works?per-page=1" + (f"&mailto={_MAIL}" if _MAIL else ""),
    # SRC-037 (NICE qua Europe PMC) — thêm 22/09/2026 cùng đợt đóng 4 khoảng trống nguồn. Miễn phí,
    # không hạn mức, không cần khoá — đã kiểm reachability RIÊNG từ chính môi trường chạy chốt này
    # trước khi thêm (khác CORE ở dưới, nơi vấn đề là thiếu header xác thực chứ không phải
    # reachability): Europe PMC đã dùng chung ổn định cho SRC-005.
    "SRC-037": "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=PMID:1&format=json&pageSize=1",
    # CỐ Ý KHÔNG có SRC-020 (kcb.vn). Mục này nằm ở đây từ 22/09 tới 30/09/2026 mà CHƯA LẦN NÀO được
    # thăm: nhánh thăm trong main() chỉ chạy cho `access: api`, còn SRC-020 là `html-watch` — bảng
    # ghi 8 điểm thăm, thực thăm 7. Gỡ thay vì mở nhánh thăm cho nó: nhãn của trạm html-watch/rss do
    # vòng quét trạm `giam_sat_to_chuc.py` giữ (trang có còn đọc ra tiêu đề hay không); một HTTP 200
    # ở đây không chứng minh điều đó (ping ≠ thu hoạch — BH50) và hai công cụ sẽ giành nhau một
    # nhãn. `test_moi_diem_tham_la_nguon_api_trong_so` chặn mục chết quay lại.
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
    if rel.startswith(_TIEN_TO_ENGINE):
        return _mea_goc() / rel[len(_TIEN_TO_ENGINE):]
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
            d = _mea_goc() / "data" / "retraction_watch"
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
            log = (_mea_goc() / "data" / "archive"
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


# VÁ 03/10/2026 (N11/PM-14 kiểm toàn diện): mỗi lượt đo trên máy thật GHI LẠI sổ tracked chỉ để đổi `updated` và
# `last_probe_at` (đo 02/10: 16 dòng diff, toàn dấu ngày) ⇒ cây git bẩn sau mỗi phép ĐO, hai máy cùng ghi một dòng. Nay sổ
# tracked chỉ ghi khi NỘI DUNG đổi (status, last_success_at…); dấu thăm sống luôn ghi vào `state/tham-song-nguon.json` (ngoài git).
def duong_dau_tham() -> Path:
    """Sổ dấu thăm NGOÀI git: `<GOC>/state/` khi dùng sổ thật; sổ bị trỏ đi nơi khác (test, BH50) thì nằm cạnh sổ đó.
    Đọc `GOC`/`SO` lúc GỌI — không chốt lúc import."""
    if SO == GOC / "data" / "sources.json":
        return GOC / "state" / "tham-song-nguon.json"
    return SO.with_name("tham-song-nguon.json")


def chu_ky_so(du: dict) -> str:
    """Nội dung sổ BỎ `updated` và mọi `last_probe_at` — hai chữ ký khác nhau mới là lý do ghi sổ tracked."""
    import copy  # noqa: PLC0415
    d = copy.deepcopy(du)
    d.pop("updated", None)
    for s in d.get("sources", []):
        if isinstance(s, dict):
            s.pop("last_probe_at", None)
    return json.dumps(d, ensure_ascii=False, sort_keys=True)


def ghi_dau_tham(du: dict, hom_nay: date, tep: Path | None = None) -> None:
    """Gộp `last_probe_at` của lượt này vào sổ dấu thăm NGOÀI git (giữ dấu của nguồn lượt này không thăm)."""
    tep = tep or duong_dau_tham()
    try:
        cu = json.loads(tep.read_text(encoding="utf-8"))
        dau = dict(cu.get("last_probe_at") or {})
    except (OSError, ValueError, AttributeError):
        dau = {}
    dau.update({s["id"]: s["last_probe_at"] for s in du.get("sources", []) if isinstance(s, dict) and s.get("last_probe_at")})
    tep.parent.mkdir(parents=True, exist_ok=True)
    tam = tep.with_name(tep.name + f".tam-{os.getpid()}")
    tam.write_text(json.dumps({"cap_nhat": hom_nay.isoformat(), "last_probe_at": dau}, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8", newline="\n")
    os.replace(tam, tep)


def main() -> int:
    ap = argparse.ArgumentParser(description="Sức khoẻ sổ đăng ký nguồn")
    ap.add_argument("--im-khi-on", action="store_true")
    ap.add_argument("--khong-mang", action="store_true", help="bỏ thăm sống, chỉ đọc sổ")
    ap.add_argument("--khong-ghi", action="store_true",
                    help="chỉ báo cáo, không ghi ngược sổ (tự bật trên phiên Cloud và trên bản sao git trần)")
    a = ap.parse_args()
    cloud = la_phien_cloud()
    tran = la_ban_sao_tran()
    # Nguồn file của engine chỉ «không đo được» khi ĐỒNG THỜI: bản sao trần VÀ không thấy engine ở
    # đâu. Thiếu một trong hai vế (máy còn gốc dữ liệu khác · engine có mặt) thì thiếu là THẬT.
    engine_vang = tran and _goc_engine() is None
    ghi_so = not (a.khong_ghi or cloud or tran)

    try:
        du = json.loads(SO.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"🔴 Sổ nguồn hỏng: {exc}")
        return 2
    chu_ky_truoc = chu_ky_so(du)

    hom_nay = date.today()
    loi: list[str] = []
    dong: list[str] = []
    khong_do: list[str] = []          # proxy môi trường từ chối — request chưa tới nguồn
    khong_do_engine: list[str] = []   # nguồn file của engine trên bản sao trần không mang engine
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
        file_khong_do = False
        if s["access"] == "file" and s.get("endpoint_or_url"):
            if engine_vang and s["endpoint_or_url"].startswith(_TIEN_TO_ENGINE):
                # Thư mục nằm trong engine mà cây này không mang engine: tuổi file KHÔNG đo được ở
                # đây. KHÔNG BIẾT ≠ hỏng (BH08) — `status` của sổ giữ nguyên.
                file_khong_do = True
                khong_do_engine.append(s["id"])
            else:
                f = _duong_file(s["endpoint_or_url"])
                if f.exists():
                    tuoi = (datetime.now() - datetime.fromtimestamp(
                        max(p.stat().st_mtime for p in ([f] if f.is_file() else list(f.iterdir()) or [f])))).days
                    if tuoi > chu_ky:
                        s["status"] = "degraded"
                        dong.append(f"  ⚠ {s['id']} file {tuoi} ngày tuổi > chu kỳ {chu_ky}ng — chạy làm mới")
                else:
                    s["status"] = "broken"
                    dong.append(f"  ⚠ {s['id']} không thấy {f} — nguồn file mất THẬT (không phải bản sao trần vắng engine)")
        # (3) quá 2 chu kỳ kể từ last_success → broken (nguồn hỏng không được im). Bỏ qua với nguồn
        # file không đo được: mốc `last_success_at` của nó suy từ chính thư mục đang vắng.
        ls = s.get("last_success_at")
        if ls and not file_khong_do:
            try:
                tre = (hom_nay - date.fromisoformat(ls[:10])).days
                if tre > 2 * chu_ky and s["status"] != "active":
                    s["status"] = "broken"
            except ValueError:
                pass
        if s["status"] in ("degraded", "broken"):
            loi.append(f"{s['id']} {s['name'][:50]} → {s['status'].upper()}"
                       f" (thành công gần nhất: {s.get('last_success_at') or 'chưa từng'})"
                       + (" — nhãn của SỔ, lượt này không đo được" if file_khong_do else ""))

    so_khong_doi = False
    if ghi_so:
        ghi_dau_tham(du, hom_nay)
        so_khong_doi = chu_ky_so(du) == chu_ky_truoc
    if ghi_so and not so_khong_doi:
        du["updated"] = hom_nay.isoformat()
        # Thụt lề 2 + LF: đúng định dạng MỌI commit của sổ (vá 27/09/2026 — thụt lề 1 làm mỗi lượt
        # viết lại ~830/833 dòng; cùng lỗi ở giam_sat_to_chuc.py::_ghi_so_nguon).
        SO.write_text(json.dumps(du, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
                      newline="\n")
    if so_khong_doi and not a.im_khi_on:
        print("≡ Sổ data/sources.json không đổi nội dung (chỉ dấu thăm sống) — KHÔNG ghi sổ tracked; dấu thăm ở "
              "state/tham-song-nguon.json.")
    if khong_do:
        print(f"⚪ {len(khong_do)} nguồn KHÔNG ĐO ĐƯỢC — proxy môi trường từ chối theo chính sách "
              f"(request chưa tới nguồn, trạng thái giữ nguyên): {', '.join(khong_do)}")
        if cloud:
            print("   Cloud: mở Network access → Custom + thêm host (audit/15 §7) để đo được.")
    if khong_do_engine:
        print(f"⚪ {len(khong_do_engine)} nguồn file KHÔNG ĐO ĐƯỢC — engine vắng (bản sao git trần: không thấy "
              f"{_TIEN_TO_ENGINE} ở vị trí lồng lẫn anh em; trạng thái trong sổ giữ nguyên): "
              f"{', '.join(khong_do_engine)}")
        print("   Đo được ở cây có engine: cây chính của máy thật, hoặc phiên Cloud đã nối engine.")
    if not ghi_so:
        if cloud:
            ly_do = "(phiên Cloud — mạng môi trường, không phải nguồn, quyết định kết quả)."
        elif a.khong_ghi:
            ly_do = "(--khong-ghi)."
        else:
            ly_do = ("(bản sao git trần — cây này không có gốc dữ liệu ngoài git nên chỉ đo được MỘT PHẦN; "
                     "sổ sống đo ở cây chính của máy thật).")
        print("ℹ  KHÔNG ghi sổ data/sources.json " + ly_do)

    n_active = sum(1 for s in du["sources"] if s["status"] == "active")
    n_nc = sum(1 for s in du["sources"] if s["status"] == "not-covered")
    # Không đo được ≠ ổn: nguồn ⚪ còn mang nhãn active của sổ thì KHÔNG được đếm là «khoẻ».
    chua_do = set(khong_do) | set(khong_do_engine)
    n_chua_do = sum(1 for s in du["sources"] if s["status"] == "active" and s["id"] in chua_do)
    ghi_chu_chua_do = f" · ⚪ {n_chua_do} active KHÔNG đo được lượt này (nhãn theo sổ)" if n_chua_do else ""
    if loi:
        print(f"🟠 SỔ NGUỒN: {n_active - n_chua_do} active{ghi_chu_chua_do} · {len(loi)} degraded/broken"
              f" · {n_nc} not-covered")
        for x in loi:
            print("  ✗ " + x)
        for x in dong:
            print(x)
        print("  → nguồn hỏng = chuyên khoa đó đang MÙ; không được để im (LÔ F nguyên nhân gốc #4)")
        return 1
    if not a.im_khi_on:
        print(f"🟢 SỔ NGUỒN: {n_active - n_chua_do} active khoẻ{ghi_chu_chua_do} · {n_nc} not-covered"
              " (khoảng trống CÓ khai báo):")
        for s in du["sources"]:
            if s["status"] == "not-covered":
                print(f"  ◌ {s['id']} {s['name'][:58]} — {(s.get('known_gap') or '')[:70]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
