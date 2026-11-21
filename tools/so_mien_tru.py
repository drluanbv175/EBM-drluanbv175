#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SỔ MIỄN TRỪ — đo tỷ lệ miễn trừ / vượt cổng THEO THỜI GIAN (21/11/2026).

VÌ SAO CÓ
=========
Bác sĩ 21/11/2026 («giải quyết vấn đề ở ý 2 … nếu làm cho hệ thống hoàn thiện thì thực hiện»): mượn ý tưởng của plugin
research-superpowers (KHÔNG cài) — theo dõi tỷ lệ miễn trừ/vượt cổng theo thời gian, để một miễn trừ «tạm thời» không
lặng lẽ thành thói quen.

Miễn trừ QUAN TRỌNG nhất của hệ không nằm trong mã mà nằm trong dữ liệu: `provenanceUnknown: true` trong
`DATA.standards` của dashboard (gói tự khai là chiến lược tìm KHÔNG tái lập được). Cổng `verify_dashboard.py` chỉ CẢNH
BÁO cho cờ này (14/08/2026, để 44/62 gói cũ không thành bức tường đỏ). Đo 21/11/2026: 63/304 dashboard mang cờ; 18/114
bản HIỆN HÀNH; 9 sau khi bỏ bản tin gộp — trong đó có bản dựng tháng 11 — mà không công cụ nào hiện con số này.

NGUYÊN NHÂN GỐC (đo 21/11/2026, đọc lý do trong từng dashboard)
---------------------------------------------------------------
Không công cụ nào ghi cờ. Bản nối tiếp do PHIÊN Claude dựng bằng cách chép khối `DATA` của bản cũ — kể cả `standards`
— rồi thêm mục mới. Doctrine (skill `cap-nhat-chung-cu-y-khoa`) chỉ dạy «dashboard MỚI phải khai DATA.standards», KHÔNG
nói gì về bản nối tiếp của một gói đã mang cờ. Hai cách phiên đã làm, đo được bằng máy:
  • KẾ THỪA CÓ GHI LƯỢT MỚI (`mien_tru_co_ghi_luot_moi`): giữ cờ cho mục kế thừa, ghi lượt tìm của chính bản vào
    `searchSources`/`currency`/`searchStrategy` (vd RA_EULAR2024, NhiKhoa_SocPhanVe, VKDT_TongHop 05–14/11). Đúng tinh
    thần «không hồi tố được, nhưng gói MỚI phải khai đủ» — cờ còn vì mục cũ, không vì lượt mới.
  • CHỈ CÓ CỜ (`mien_tru_chi_co`): chép nguyên câu «bản sinh trước khi khối DATA.standards thành bắt buộc…» (SAI với
    một tệp dựng 25/10 hay 07/11), lượt tìm mới hoặc không ghi đâu cả (CAP_ATS2025, LaoKhoa_Deprescribing 26/10 thêm
    mục mới mà không một dòng chiến lược) hoặc chỉ viết văn xuôi trong `provenanceUnknownLyDo` (DaLieu_HS,
    SuyTim_NoiTiet 07/11) — trường mà cổng không đọc như hợp đồng nguồn.
Vì vậy (b) tách hai lớp: 🟠 chỉ dành cho lớp CHỈ CÓ CỜ ở bản HIỆN HÀNH (sửa được bằng một bản nối tiếp ghi đúng
trường); lớp kế thừa và bản đã bị thay chỉ là THÔNG TIN — báo động không bao giờ gỡ được dạy người đọc bỏ qua màu.

BỐN SỐ ĐO
  (a) bản MỚI NHẤT của mỗi lát cắt còn `provenanceUnknown` — nhóm lát cắt bằng ĐÚNG `dang_ky_chu_de.tach_ten`, loại bản
      tin gộp bằng ĐÚNG `kiem_do_tuoi_chung_cu.la_khong_can` (không tự chế regex). Kèm n/N lát cắt «tái lập được».
  (b) dashboard có ngày (trong tên tệp) ≥ MOC_PRISMA_S mà vẫn khai miễn trừ — mọi tệp, tách lớp và bản hiện hành.
  (c) marker miễn trừ trong mã — `bh10-mien:` / `bimat-mien:` đứng NGAY sau dấu chú thích `#` và có lý do, trong tệp git
      track của repo gốc và repo y khoa (dòng tài liệu nhắc tên marker không tính).
  (d) ảnh chụp xu hướng `state/so-mien-tru.json` — CHỈ ghi khi số đổi (luật BH153), mỗi ngày một dòng, giữ lịch sử.

MỐC (b) — 15/08/2026. Căn cứ: luật «mọi gói MỚI phải khai đủ» chiến lược tìm theo PRISMA-S vào kho ngày 14/08/2026 —
commit 8c469c1f (BH42, 21:53; audit/NHAT-KY-SU-CO.md, đoạn «PRISMA-S gắn vào lỗ hổng provenance») — cùng ngày cổng thêm
miễn trừ `provenanceUnknown` kèm câu «gói mới BẮT BUỘC khai DATA.standards đầy đủ» (commit 18b878d0, 19:22). Tệp mang
ngày 14/08 có thể dựng trước giờ commit nên không tính.

GIỚI HẠN CÓ CHỦ Ý
  • Chỉ ĐO và BÁO. Không sửa dashboard, không đổi `decision`/`gradeLevel`, không bịa hợp đồng nguồn, không đổi cổng
    `verify_dashboard.py` — chặn `provenanceUnknown` cho gói mới là QUYẾT ĐỊNH của bác sĩ (đề xuất in ở cuối báo cáo).
  • «Không đo được» ⇒ ⚪ (mã 2), không bao giờ xanh giả: vắng EBM-Dashboards, không nạp được cổng/đăng ký chủ đề.
  • `du` = có `standards` và không cờ — tức gói KHAI hợp đồng nguồn; công cụ không chấm lại từng trường (việc của cổng).

Dùng:
    python3 tools/so_mien_tru.py              # báo cáo + ghi ảnh chụp khi số đổi
    python3 tools/so_mien_tru.py --json       # máy đọc (Đài hoàn thiện)
    python3 tools/so_mien_tru.py --khong-ghi  # chỉ đo, không đụng state/
Chạy từ worktree ngoài OneDrive: đặt EBM_WORKSPACE_ROOT về gốc «Claude AI».

Mã thoát: 0 = đo được, không bản hiện hành nào mang miễn trừ · 1 = có miễn trừ cần chú ý · 2 = KHÔNG ĐO ĐƯỢC.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

for _luong in (sys.stdout, sys.stderr):
    try:
        _luong.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
TOOLS = Path(__file__).resolve().parent

MOC_PRISMA_S = "20260815"          # xem docstring: luật PRISMA-S gói mới 14/08/2026 (8c469c1f · 18b878d0)
NGAY_SO_MARKER = 7                 # ⓘ khi marker tăng so với ảnh chụp cũ ≥ 7 ngày
TRAN_LICH_SU = 400                 # số dòng ảnh chụp giữ lại (mỗi ngày tối đa một dòng)
# Cùng regex với cổng verify_dashboard.strict_source_checks — đọc cờ đúng như cổng đọc.
CO_PROVENANCE = re.compile(r"\bprovenanceUnknown\s*:\s*true\b")
# Marker THẬT: đứng ngay sau dấu chú thích và có lý do (khuôn bimat-mien của kiem_bi_mat_truoc_commit.MIEN).
MAU_MARKER = {"bh10-mien": re.compile(r"#\s*bh10-mien:\s*\S"),
              "bimat-mien": re.compile(r"#\s*bimat-mien:\s*\S")}
MAU_GIT_GREP = r"#[[:space:]]*(bh10|bimat)-mien:[[:space:]]*[^[:space:]]"

DU = "du"                                  # có standards, không cờ — khai hợp đồng nguồn
CO_GHI = "mien_tru_co_ghi_luot_moi"        # cờ (mục kế thừa) + lượt tìm của chính bản ghi vào trường hợp đồng
CHI_CO = "mien_tru_chi_co"                 # chỉ cờ + lý do — lượt tìm của chính bản không nằm trong trường hợp đồng
THIEU = "thieu_standards"                  # không có khối standards (cổng chặn)
KHONG_DOC = "khong_doc_duoc"               # không đọc được tệp / không có khối DATA
MIEN = (CO_GHI, CHI_CO)
NHAN_LOAI = {DU: "khai hợp đồng nguồn", CO_GHI: "kế thừa, có ghi lượt mới", CHI_CO: "CHỈ CÓ CỜ",
             THIEU: "thiếu standards", KHONG_DOC: "không đọc được"}


def _nap(ten: str, duong: Path):
    sp = importlib.util.spec_from_file_location(ten, duong)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


def goc_du_lieu(ten: str) -> Path | None:
    """Gốc dữ liệu ngoài git (lồng/anh em của repo — `ban_sao_tran.duong_goc`); từ worktree ngoài OneDrive thì đọc
    EBM_WORKSPACE_ROOT. None nếu không thấy ở đâu (⇒ ⚪, không đoán)."""
    try:
        p = _nap("_smt_bst", TOOLS / "ban_sao_tran.py").duong_goc(ten, REPO)
    except Exception:  # noqa: BLE001 — thiếu resolver thì thử biến môi trường
        p = None
    if p is None and os.environ.get("EBM_WORKSPACE_ROOT"):
        q = Path(os.environ["EBM_WORKSPACE_ROOT"]) / ten
        p = q if q.exists() else None
    return p


def tep_state_mac_dinh() -> Path:
    goc = os.environ.get("EBM_WORKSPACE_ROOT")
    return (Path(goc) if goc else REPO) / "state" / "so-mien-tru.json"


# ───────────────────────── (a)(b) dashboard ─────────────────────────

def phan_loai(vd, html: str) -> str:
    """Lớp hợp đồng nguồn của MỘT dashboard, đọc bằng parser của chính cổng (`vd` = verify_dashboard)."""
    db = vd.extract_data_block(html)
    if not db:
        return KHONG_DOC
    st = vd.object_after_key(db, "standards")
    if not st:
        return THIEU
    if not CO_PROVENANCE.search(st):
        return DU
    if vd.array_field(st, "searchSources") or (vd.field(st, "currency") or "").strip() \
            or (vd.field(st, "searchStrategy") or "").strip():
        return CO_GHI
    return CHI_CO


def quet(dash: Path, vd, tach_ten, la_khong_can, khong_can: dict) -> dict:
    """{ban: [...], khong_tach: [...]} — mỗi bản: tên, lát cắt, ngày, lớp, bản tin gộp, hiện hành."""
    ban: list[dict] = []
    khong_tach: list[str] = []
    for p in sorted(dash.glob("WebDashboard_*.html")):
        r = tach_ten(p.name)
        if not r:
            khong_tach.append(p.name)
            continue
        lat, _goc, ngay = r
        try:
            loai = phan_loai(vd, p.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            loai = KHONG_DOC
        ban.append({"ten": p.name, "lat_cat": lat, "ngay": ngay, "loai": loai,
                    "ban_tin_gop": bool(la_khong_can(lat, khong_can))})
    moi: dict[str, dict] = {}
    for b in ban:
        k = b["lat_cat"]
        if k not in moi or (b["ngay"], b["ten"]) > (moi[k]["ngay"], moi[k]["ten"]):
            moi[k] = b
    for b in ban:
        b["hien_hanh"] = moi[b["lat_cat"]] is b
    return {"ban": ban, "khong_tach": khong_tach}


def tong_hop(ban: list[dict], moc: str = MOC_PRISMA_S) -> dict:
    """Số đếm (a)(b) + xu hướng theo tháng (ngày trong tên tệp) từ danh sách bản đã phân loại."""
    _k = lambda b: (b["ngay"], b["lat_cat"])  # noqa: E731
    hien = [b for b in ban if b["hien_hanh"]]
    lam_moi = [b for b in hien if not b["ban_tin_gop"]]
    sau_moc = [b for b in ban if b["ngay"] >= moc and b["loai"] in MIEN]
    theo_thang: dict[str, dict] = {}
    for b in ban:
        t = theo_thang.setdefault(f"{b['ngay'][:4]}-{b['ngay'][4:6]}", {"tong": 0, "mien": 0})
        t["tong"] += 1
        t["mien"] += b["loai"] in MIEN
    return {
        "tong_dashboard": len(ban),
        "tong_mien": sum(1 for b in ban if b["loai"] in MIEN),
        "lat_cat_tong": len(hien),
        "lat_cat_lam_moi_duoc": len(lam_moi),
        "tai_lap_duoc": sum(1 for b in lam_moi if b["loai"] == DU),
        "a": sorted((b for b in lam_moi if b["loai"] in MIEN), key=_k),
        "khong_doc_hien_hanh": sorted((b for b in lam_moi if b["loai"] == KHONG_DOC), key=_k),
        "thieu_hien_hanh": sorted((b for b in lam_moi if b["loai"] == THIEU), key=_k),
        "b_tong": len(sau_moc),
        "b_chi_co_tong": sum(1 for b in sau_moc if b["loai"] == CHI_CO),
        "b_co_ghi_tong": sum(1 for b in sau_moc if b["loai"] == CO_GHI),
        "b_chi_co_hien_hanh": sorted((b for b in sau_moc if b["loai"] == CHI_CO and b["hien_hanh"]), key=_k),
        "b_co_ghi_hien_hanh": sorted((b for b in sau_moc if b["loai"] == CO_GHI and b["hien_hanh"]), key=_k),
        "theo_thang": dict(sorted(theo_thang.items())),
    }


# ───────────────────────── (c) marker trong mã ─────────────────────────

def dem_marker(repo: Path) -> dict | None:
    """{dem: {marker: n}, vi_tri: {marker: [tệp:dòng]}} trên tệp git track; None khi git không chạy được (⚪)."""
    try:
        r = subprocess.run(["git", "-C", str(repo), "grep", "-nIE", MAU_GIT_GREP], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode not in (0, 1):     # 1 = không khớp dòng nào (hợp lệ); khác ⇒ không phải repo / git lỗi
        return None
    dem = {k: 0 for k in MAU_MARKER}
    vi_tri: dict[str, list[str]] = {k: [] for k in MAU_MARKER}
    for dong in r.stdout.splitlines():
        phan = dong.split(":", 2)
        for k, mau in MAU_MARKER.items():
            if len(phan) == 3 and mau.search(phan[2]):
                dem[k] += 1
                vi_tri[k].append(f"{phan[0]}:{phan[1]}")
    return {"dem": dem, "vi_tri": vi_tri}


# ───────────────────────── (d) ảnh chụp xu hướng ─────────────────────────

def doc_lich_su(tep: Path) -> list[dict] | None:
    """Lịch sử ảnh chụp; [] khi tệp VẮNG (sổ rỗng hợp lệ); None khi CÓ mà không đọc được (không được ghi đè)."""
    if not tep.exists():
        return []
    try:
        d = json.loads(tep.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    ls = d.get("lich_su") if isinstance(d, dict) else None
    return ls if isinstance(ls, list) and all(isinstance(x, dict) and "ngay" in x for x in ls) else None


def dong_anh_chup(kq: dict, ngay: dt.date) -> dict:
    return {"ngay": ngay.isoformat(),
            "tong_dashboard": kq["tong_dashboard"], "tong_mien": kq["tong_mien"],
            "lat_cat_lam_moi_duoc": kq["lat_cat_lam_moi_duoc"], "tai_lap_duoc": kq["tai_lap_duoc"],
            "a": len(kq["a"]), "a_lat_cat": [b["lat_cat"] for b in kq["a"]],
            "b_tong": kq["b_tong"], "b_chi_co_hien_hanh": [b["lat_cat"] for b in kq["b_chi_co_hien_hanh"]],
            "marker": {ten: (m["dem"] if m else None) for ten, m in kq["marker"].items()}}


def ghi_anh_chup(tep: Path, dong: dict, lich_su: list[dict] | None) -> str:
    """BH153 — chỉ ghi khi số đổi so với dòng cuối; cùng ngày thì thay dòng đó. Trả 'ghi' · 'khong_doi' · 'hong' ·
    'loi_ghi'. Sổ hỏng (lich_su None) KHÔNG bị ghi đè."""
    if lich_su is None:
        return "hong"
    if lich_su and {k: v for k, v in lich_su[-1].items() if k != "ngay"} == {k: v for k, v in dong.items()
                                                                               if k != "ngay"}:
        return "khong_doi"
    moi = [x for x in lich_su if x.get("ngay") != dong["ngay"]] + [dong]
    noi_dung = json.dumps({"mo_ta": "Ảnh chụp sổ miễn trừ (tools/so_mien_tru.py) — chỉ ghi khi số đổi",
                           "moc_prisma_s": MOC_PRISMA_S, "lich_su": moi[-TRAN_LICH_SU:]},
                          ensure_ascii=False, indent=1)
    try:
        tep.parent.mkdir(parents=True, exist_ok=True)
        fd, tam = tempfile.mkstemp(dir=tep.parent, prefix=".so-mien-tru.", suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(noi_dung + "\n")
        os.replace(tam, tep)
    except OSError:
        return "loi_ghi"
    return "ghi"


def marker_tang(lich_su: list[dict] | None, hien_tai: dict, hom_nay: dt.date,
                so_ngay: int = NGAY_SO_MARKER) -> tuple[str, dict] | None:
    """(ngày ảnh chụp mốc, {repo:marker: (cũ, mới)}) khi marker TĂNG so với ảnh chụp mới nhất cũ ≥ `so_ngay` ngày;
    None khi chưa có ảnh chụp đủ cũ hoặc không tăng."""
    if not lich_su:
        return None
    moc = hom_nay - dt.timedelta(days=so_ngay)
    cu = []
    for x in lich_su:
        try:
            if dt.date.fromisoformat(str(x["ngay"])) <= moc:
                cu.append(x)
        except ValueError:
            continue
    if not cu:
        return None
    goc = cu[-1]
    tang: dict[str, tuple[int, int]] = {}
    for repo, m in hien_tai.items():
        cu_repo = (goc.get("marker") or {}).get(repo)
        if not m or not isinstance(cu_repo, dict):
            continue
        for k, v in m["dem"].items():
            if isinstance(cu_repo.get(k), int) and v > cu_repo[k]:
                tang[f"{repo}:{k}"] = (cu_repo[k], v)
    return (str(goc["ngay"]), tang) if tang else None


# ───────────────────────── gom ─────────────────────────

def _lenh_orchestrator(dash: Path, ung_vien: list[dict]) -> tuple[str, str]:
    """(lát cắt, ghi chú) — lát cắt CŨ NHẤT có ánh xạ watchlist (orchestrator mới chạy A2 được); không lát cắt nào có
    ánh xạ thì lấy cũ nhất kèm ghi chú. Phân giải bằng chính `chu_de_resolver` mà orchestrator dùng."""
    try:
        res = _nap("_smt_res", TOOLS / "chu_de_resolver.py")
        du_lieu = res.nap_du_lieu(dash)
        for b in ung_vien:
            if res.resolve(b["lat_cat"], du_lieu).get("loai") == "watchlist":
                return b["lat_cat"], ""
    except Exception:  # noqa: BLE001 — chỉ là gợi ý lệnh; không làm sập phép đo
        return ung_vien[0]["lat_cat"], " (chưa kiểm được ánh xạ watchlist)"
    return ung_vien[0]["lat_cat"], " (chưa ánh xạ watchlist trong giam-sat-chu-de.json — orchestrator sẽ bỏ A2)"


def do(dash: Path | None = None, cac_repo: dict[str, Path | None] | None = None, tep_state: Path | None = None,
       hom_nay: dt.date | None = None, ghi: bool = True) -> dict:
    """Đo cả bốn số. Không raise vì dữ liệu thiếu: trả `do_duoc=False` + `ly_do` (⚪)."""
    hom_nay = hom_nay or dt.date.today()
    tep_state = tep_state or tep_state_mac_dinh()
    if cac_repo is None:
        cac_repo = {"goc": REPO, "y_khoa": goc_du_lieu("medical-ebm-automation")}
    kq: dict = {"ngay": hom_nay.isoformat(), "moc_prisma_s": MOC_PRISMA_S, "do_duoc": False, "ly_do": "",
                "chua_do": [], "tep_state": str(tep_state), "anh_chup": "khong_ghi"}
    kq["marker"] = {ten: (dem_marker(p) if p else None) for ten, p in cac_repo.items()}
    for ten, m in kq["marker"].items():
        if m is None and cac_repo.get(ten):   # repo CÓ mà git lỗi ⇒ ⚪; repo vắng trên máy này (vd y khoa ở cloud) ⇒ bỏ
            kq["chua_do"].append(f"không đếm được marker trong repo {ten} (git lỗi)")
    lich_su = doc_lich_su(tep_state)
    if lich_su is None:
        kq["chua_do"].append(f"ảnh chụp {tep_state.name} hỏng — không ghi đè, chưa so được xu hướng marker")
    kq["marker_tang"] = marker_tang(lich_su, kq["marker"], hom_nay)

    dash = dash or goc_du_lieu("EBM-Dashboards")
    if dash is None or not dash.is_dir():
        kq["ly_do"] = "không thấy EBM-Dashboards ở cây này (bản sao git trần?) — đặt EBM_WORKSPACE_ROOT"
        return kq
    kq["dash"] = str(dash)
    try:
        dk = _nap("_smt_dkcd", TOOLS / "dang_ky_chu_de.py")
        vd = dk.nap_vd()
        kdt = _nap("_smt_kdtcc", TOOLS / "kiem_do_tuoi_chung_cu.py")
    except Exception as exc:  # noqa: BLE001 — cảm biến hỏng phải hiện ra, không im như xanh
        kq["ly_do"] = f"không nạp được cổng/đăng ký chủ đề ({type(exc).__name__}: {str(exc)[:120]})"
        return kq
    try:
        khong_can = dict(json.loads((dash / "giam-sat-chu-de.json").read_text(encoding="utf-8")).get("khong_can")
                         or {})
    except (OSError, ValueError, AttributeError):
        khong_can = {}
        kq["chua_do"].append("không đọc được giam-sat-chu-de.json — bản tin gộp CHƯA được loại khỏi (a)")
    q = quet(dash, vd, dk.tach_ten, kdt.la_khong_can, khong_can)
    if not q["ban"]:
        kq["ly_do"] = f"0 dashboard tách được tên trong {dash} — không phải «0 miễn trừ»"
        return kq
    kq.update(tong_hop(q["ban"]))
    kq["khong_tach"] = q["khong_tach"]
    if kq["khong_doc_hien_hanh"]:
        kq["chua_do"].append(f"{len(kq['khong_doc_hien_hanh'])} bản hiện hành không đọc được khối DATA")
    kq["do_duoc"] = True
    if kq["a"]:
        kq["goi_y_lat_cat"], kq["goi_y_ghi_chu"] = _lenh_orchestrator(dash, kq["a"])
    if ghi:
        kq["anh_chup"] = ghi_anh_chup(tep_state, dong_anh_chup(kq, hom_nay), lich_su)
    return kq


def _ngay(s: str) -> str:
    return f"{s[6:8]}/{s[4:6]}/{s[:4]}" if len(s) == 8 else s


def _ds(ban: list[dict], toi_da: int = 4) -> str:
    phan = [b["lat_cat"] for b in ban[:toi_da]]
    return ", ".join(phan) + (f" +{len(ban) - toi_da}" if len(ban) > toi_da else "")


def giac_quan(**kw) -> tuple[list[tuple[int, str, str, str]], list[str], list[str], list[str]]:
    """(việc [(ưu tiên, 👤, việc, lệnh)], dòng ⓘ, lý do giác quan chết ⚪, mục chưa đo ⚪) cho `tu_de_xuat_viec.py`.

    🟠 (b): bản HIỆN HÀNH dựng sau mốc PRISMA-S mà CHỈ CÓ CỜ (lượt tìm của chính bản không ghi vào hợp đồng nguồn).
    🟡 (a): lát cắt đang dùng bản mang cờ — kèm lệnh orchestrator cho lát cắt cũ nhất.
    ⓘ (c): marker miễn trừ trong mã tăng so với ảnh chụp ≥ 7 ngày."""
    try:
        kq = do(**kw)
    except Exception as exc:  # noqa: BLE001 — cảm biến hỏng phải hiện ra
        return [], [], [f"lỗi {type(exc).__name__}"], []
    viec: list[tuple[int, str, str, str]] = []
    tt: list[str] = []
    chet: list[str] = [] if kq["do_duoc"] else [kq["ly_do"]]
    if kq["do_duoc"]:
        bh = kq["b_chi_co_hien_hanh"]
        if bh:
            viec.append((1, "👤", f"{len(bh)} bản hiện hành dựng sau mốc PRISMA-S ({_ngay(MOC_PRISMA_S)}) CHỈ CÓ CỜ "
                                  f"provenanceUnknown — lượt tìm của chính bản không ghi vào DATA.standards ({_ds(bh)}); "
                                  "bác sĩ quyết: giữ cảnh báo hay «chặn có sổ nợ» cho gói mới",
                         "python3 tools/so_mien_tru.py"))
        a = kq["a"]
        if a:
            cu = next((b for b in a if b["lat_cat"] == kq.get("goi_y_lat_cat")), a[0])
            viec.append((3, "👤", f"{len(a)}/{kq['lat_cat_lam_moi_duoc']} chủ đề đang dùng bản mang provenanceUnknown "
                                  f"(chiến lược tìm không tái lập được) — gợi ý {cu['lat_cat']} ({_ngay(cu['ngay'])}); "
                                  "bản nối tiếp ghi lượt tìm vào searchSources/currency, mục kế thừa vẫn mang cờ tới "
                                  f"khi được tìm lại{kq.get('goi_y_ghi_chu', '')}",
                         f'python3 ops/orchestrator.py --topic "{cu["lat_cat"]}" --online'))
    mt = kq.get("marker_tang")
    if mt:
        ngay, tang = mt
        tt.append("Marker miễn trừ trong mã TĂNG so với ảnh chụp " + ngay + ": "
                  + " · ".join(f"{k} {c}→{m}" for k, (c, m) in sorted(tang.items()))
                  + " — rà lý do từng dòng (python3 tools/so_mien_tru.py)")
    return viec, tt, chet, list(kq["chua_do"])


# ───────────────────────── CLI ─────────────────────────

def in_bao_cao(kq: dict) -> None:
    print(f"SỔ MIỄN TRỪ — {kq['ngay']} (chỉ ĐO và BÁO; không sửa dashboard, không đổi cổng)")
    if not kq["do_duoc"]:
        print(f"⚪ KHÔNG ĐO ĐƯỢC (a)(b): {kq['ly_do']}")
    else:
        n, tong = kq["tai_lap_duoc"], kq["lat_cat_lam_moi_duoc"]
        print(f"\n(a) Chủ đề đang dùng bản mang provenanceUnknown: {len(kq['a'])}/{tong} lát cắt làm mới được "
              f"(khai hợp đồng nguồn {n}/{tong}; {kq['lat_cat_tong'] - tong} bản tin gộp không tính)")
        for b in kq["a"]:
            print(f"    · {b['ngay']} {b['lat_cat']} — {NHAN_LOAI[b['loai']]}")
        if kq["thieu_hien_hanh"]:
            print(f"    ({len(kq['thieu_hien_hanh'])} bản hiện hành THIẾU standards: {_ds(kq['thieu_hien_hanh'], 8)})")
        print(f"\n(b) Gói dựng từ {_ngay(MOC_PRISMA_S)} (mốc luật PRISMA-S gói mới) vẫn khai miễn trừ: {kq['b_tong']} tệp "
              f"({kq['b_chi_co_tong']} chỉ có cờ · {kq['b_co_ghi_tong']} kế thừa có ghi lượt mới)")
        print(f"    🟠 bản HIỆN HÀNH chỉ có cờ: {len(kq['b_chi_co_hien_hanh'])}"
              + (f" — {_ds(kq['b_chi_co_hien_hanh'], 8)}" if kq["b_chi_co_hien_hanh"] else ""))
        print(f"    ⓘ bản hiện hành kế thừa (đã ghi lượt mới, cờ còn vì mục cũ): {len(kq['b_co_ghi_hien_hanh'])}"
              + (f" — {_ds(kq['b_co_ghi_hien_hanh'], 8)}" if kq["b_co_ghi_hien_hanh"] else ""))
        print(f"\n    Tổng: {kq['tong_mien']}/{kq['tong_dashboard']} tệp dashboard mang miễn trừ. Theo tháng dựng "
              "(tên tệp) — miễn trừ/tổng:")
        print("    " + " · ".join(f"{t} {v['mien']}/{v['tong']}" for t, v in kq["theo_thang"].items()))
        if kq.get("khong_tach"):
            print(f"    ({len(kq['khong_tach'])} tệp không tách được tên — dang_ky_chu_de cũng bỏ qua)")
    print("\n(c) Marker miễn trừ trong mã (ngay sau «#», có lý do):")
    for ten, m in kq["marker"].items():
        if m is None:
            print(f"    ⚪ {ten}: không đếm được")
        else:
            print(f"    {ten}: " + " · ".join(f"{k} {v}" for k, v in m["dem"].items()))
    if kq.get("marker_tang"):
        ngay, tang = kq["marker_tang"]
        print(f"    ⓘ TĂNG so với ảnh chụp {ngay}: " + " · ".join(f"{k} {c}→{v}" for k, (c, v) in tang.items()))
    print(f"\n(d) Ảnh chụp {kq['tep_state']}: {kq['anh_chup']}")
    for c in kq["chua_do"]:
        print(f"⚪ {c}")
    if kq["do_duoc"] and (kq["a"] or kq["b_chi_co_hien_hanh"]):
        print("\nĐỀ XUẤT (bác sĩ quyết — máy KHÔNG đổi cổng verify_dashboard.py):")
        print("  1. Doctrine: bản nối tiếp của gói mang cờ giữ cờ cho mục kế thừa nhưng ghi lượt tìm của CHÍNH bản vào")
        print("     searchSources/currency/searchStrategy — không chép câu «bản sinh trước khi…», không viết chiến lược")
        print("     vào provenanceUnknownLyDo.")
        print("  2. «Chặn có sổ nợ» (khuôn cổng nguồn chính thức 20/11): sổ nợ ghi các lát cắt đang mang cờ (chỉ giảm,")
        print("     gia hạn cần lời bác sĩ); cổng chặn gói dựng sau ngày áp dụng khai provenanceUnknown mà KHÔNG có")
        print("     searchSources/currency — mục kế thừa vẫn được miễn (đúng «không hồi tố»).")
        if kq["a"]:
            print(f'  3. Làm mới chủ đề cũ nhất: python3 ops/orchestrator.py --topic "{kq["goi_y_lat_cat"]}" --online'
                  f"{kq.get('goi_y_ghi_chu', '')}")
    print("\nCần bác sĩ kiểm chứng — số đo hỗ trợ, không thay phán đoán.")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Sổ miễn trừ — tỷ lệ provenanceUnknown / marker miễn trừ theo thời gian")
    ap.add_argument("--json", action="store_true", help="in JSON máy đọc")
    ap.add_argument("--khong-ghi", action="store_true", help="không ghi ảnh chụp state/so-mien-tru.json")
    ap.add_argument("--dash", type=Path, help="thư mục EBM-Dashboards (mặc định: tự dò / EBM_WORKSPACE_ROOT)")
    ap.add_argument("--tep-state", type=Path, help="tệp ảnh chụp (mặc định state/so-mien-tru.json)")
    a = ap.parse_args(argv)
    kq = do(dash=a.dash, tep_state=a.tep_state, ghi=not a.khong_ghi)
    if a.json:
        print(json.dumps(kq, ensure_ascii=False, indent=1))
    else:
        in_bao_cao(kq)
    if not kq["do_duoc"]:
        return 2
    return 1 if (kq["a"] or kq["b_chi_co_hien_hanh"]) else 0


if __name__ == "__main__":
    sys.exit(main())
