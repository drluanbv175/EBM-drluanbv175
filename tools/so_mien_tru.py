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
Vì vậy (b) tách hai lớp: hòm việc chỉ nhắc lớp CHỈ CÓ CỜ ở bản HIỆN HÀNH (sửa được bằng một bản nối tiếp ghi đúng
trường); lớp kế thừa và bản đã bị thay chỉ là THÔNG TIN — báo động không bao giờ gỡ được dạy người đọc bỏ qua màu.

CỔNG CHẶN CÓ SỔ NỢ (bác sĩ 21/11/2026 «chặn có sổ nợ»)
------------------------------------------------------
`verify_dashboard.kiem_provenance_goi_moi` (--strict-sources) CHẶN gói dựng từ 15/08/2026 lớp CHỈ CÓ CỜ; tệp đã tồn lúc
chuyển sang chặn nằm trong SỔ NỢ `EBM-Dashboards/no-provenance-goi-moi.json` ⇒ cảnh báo tới «han», quá hạn ⇒ chặn. Phân lớp
dùng CHÍNH `verify_dashboard.phan_loai_provenance` (một định nghĩa — hai parser cùng dữ liệu phải trùng, BH20). Công cụ này
lập/gia hạn sổ (MỘT lần, nguyên văn lời bác sĩ ≥ 20 ký tự, hạn ≤ 90 ngày, chạy khô mặc định — khuôn
`doc_nguon_chinh_thuc.py so-no` của cổng nguồn chính thức 20/11) và báo nợ; agent KHÔNG tự lập/gia hạn sổ.

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
    python3 tools/so_mien_tru.py --so-no      # sổ nợ cổng provenance gói mới (mọi bản dashboard)
    python3 tools/so_mien_tru.py --so-no --tao --han YYYY-MM-DD --can-cu "<nguyên văn lời bác sĩ>" [--ghi]
    python3 tools/so_mien_tru.py --so-no --gia-han YYYY-MM-DD --can-cu "<nguyên văn lời bác sĩ>" [--ghi]
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

MOC_PRISMA_S = "20260815"          # = verify_dashboard.MOC_PROVENANCE_GOI_MOI (test chốt); xem docstring
NGAY_SO_MARKER = 7                 # ⓘ khi marker tăng so với ảnh chụp cũ ≥ 7 ngày
TRAN_LICH_SU = 400                 # số dòng ảnh chụp giữ lại (mỗi ngày tối đa một dòng)
# Cổng nguồn chuẩn trong GIT (luôn có trên mọi checkout); bản chạy EBM-Dashboards/tools chỉ được chép sau khi gộp nên có
# thể cũ hơn — sổ miễn trừ phải đo đúng luật đang nằm trong mã.
CONG_GIT = REPO / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "verify_dashboard.py"
TEN_SO_NO = "no-provenance-goi-moi.json"   # = verify_dashboard.TEN_SO_NO_PROVENANCE (test chốt)
CAN_CU_MIN = 20
HAN_TOI_DA_NGAY = 90
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

def nap_cong():
    """Cổng verify_dashboard: bản GIT nếu có, nếu không thì bản `dang_ky_chu_de.nap_vd()` chọn (bản chạy/vendor)."""
    if CONG_GIT.exists():
        return _nap("_smt_vd", CONG_GIT)
    return _nap("_smt_dkcd_vd", TOOLS / "dang_ky_chu_de.py").nap_vd()


def phan_loai(vd, html: str) -> str:
    """Lớp hợp đồng nguồn của MỘT dashboard — CHÍNH `verify_dashboard.phan_loai_provenance` (một định nghĩa với cổng)."""
    db = vd.extract_data_block(html)
    if not db:
        return KHONG_DOC
    return vd.phan_loai_provenance(db)


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
            "cong_chan": len(kq["so_no"]["ngoai_so"]) + len(kq["so_no"]["qua_han"]),
            "no_trong_han": len(kq["so_no"]["trong_han"]),
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


# ───────────────────────── (e) sổ nợ cổng provenance gói mới ─────────────────────────

def doc_so_no(dash: Path) -> dict | None:
    """Sổ nợ provenance; vắng ⇒ None; hỏng ⇒ {"hong": lý do} (cổng coi như vắng — fail-closed)."""
    tep = Path(dash) / TEN_SO_NO
    if not tep.exists():
        return None
    try:
        d = json.loads(tep.read_text(encoding="utf-8"))
        dt.date.fromisoformat(d["han"])
        if not isinstance(d.get("muc"), list):
            raise ValueError("muc không phải danh sách")
        return d
    except (OSError, ValueError, KeyError, TypeError) as e:
        return {"hong": f"{type(e).__name__}: {e}"}


def phan_loai_no(ban: list[dict], so_no: dict | None, hom_nay: dt.date, moc: str = MOC_PRISMA_S) -> dict:
    """Bản CHỈ CÓ CỜ dựng từ mốc mà cổng CHẶN («ngoai_so», «qua_han») hoặc chỉ cảnh báo («trong_han»). Cùng định nghĩa
    với `verify_dashboard.kiem_provenance_goi_moi` (khoá sổ = tên tệp không đuôi)."""
    no, han = set(), None
    if so_no and "hong" not in so_no:
        han = dt.date.fromisoformat(so_no["han"])
        no = {str(x.get("dashboard")) for x in so_no["muc"] if isinstance(x, dict)}
    ra = {"ngoai_so": [], "qua_han": [], "trong_han": [], "han": han.isoformat() if han else None,
          "hong": (so_no or {}).get("hong"), "co_so": bool(so_no) and "hong" not in so_no}
    for b in ban:
        if b["loai"] != CHI_CO or b["ngay"] < moc:
            continue
        if Path(b["ten"]).stem in no:
            ra["trong_han" if hom_nay <= han else "qua_han"].append(b)
        else:
            ra["ngoai_so"].append(b)
    return ra


def ghi_so_no(dash: Path, muc_no: list[dict], han: str, can_cu: str, *, ghi: bool, cu: dict | None,
              hom_nay: dt.date) -> tuple[int, str]:
    """Lập sổ nợ (CHỈ khi chưa có) hoặc gia hạn (giữ nguyên danh sách — bánh cóc). Mặc định chạy khô."""
    if len((can_cu or "").strip()) < CAN_CU_MIN:
        return 3, f"✗ phải ghi NGUYÊN VĂN lời bác sĩ (≥ {CAN_CU_MIN} ký tự) — agent không tự lập/gia hạn sổ nợ"
    try:
        h = dt.date.fromisoformat(han or "")
    except ValueError:
        return 3, f"✗ hạn «{han}» sai dạng YYYY-MM-DD"
    if not (hom_nay < h <= hom_nay + dt.timedelta(days=HAN_TOI_DA_NGAY)):
        return 3, f"✗ hạn phải sau hôm nay và không quá {HAN_TOI_DA_NGAY} ngày"
    luc = dt.datetime.now().isoformat(timespec="seconds")
    if cu is None:
        so = {"_about": "Sổ NỢ provenance gói mới (bánh cóc): dashboard dựng từ 15/08/2026 khai provenanceUnknown mà KHÔNG "
                        "ghi lượt tìm của chính bản (searchSources + currency), đã tồn lúc cổng chuyển sang CHẶN "
                        "(21/11/2026). Cổng chỉ cảnh báo các tệp này tới «han»; quá hạn ⇒ CHẶN. Trả nợ bằng bản nối tiếp ghi "
                        "lượt tìm. Tệp mới KHÔNG bao giờ được thêm vào. Sinh bằng tools/so_mien_tru.py --so-no — không sửa tay.",
              "tao_luc": luc, "han": h.isoformat(), "can_cu": can_cu.strip(),
              "muc": [{"dashboard": Path(b["ten"]).stem, "lat_cat": b["lat_cat"], "hien_hanh": b["hien_hanh"]}
                      for b in muc_no], "lich_su": []}
        viec = (f"lập sổ nợ {len(muc_no)} tệp ({sum(1 for b in muc_no if b['hien_hanh'])} bản hiện hành), "
                f"hạn {h.isoformat()}")
    else:
        if "hong" in cu:
            return 3, "✗ sổ nợ hiện có KHÔNG đọc được — không gia hạn đè lên sổ hỏng; bác sĩ xem tệp trước"
        so = dict(cu)
        so.setdefault("lich_su", []).append({"luc": luc, "han_cu": cu["han"], "han_moi": h.isoformat(),
                                             "can_cu": can_cu.strip()})
        so["han"] = h.isoformat()
        viec = f"gia hạn {cu['han']} → {h.isoformat()} (danh sách giữ nguyên {len(cu['muc'])} tệp)"
    if not ghi:
        return 0, f"(chạy khô) sẽ {viec} — thêm --ghi để ghi {TEN_SO_NO}"
    (Path(dash) / TEN_SO_NO).write_text(json.dumps(so, ensure_ascii=False, indent=1) + "\n", encoding="utf-8",
                                        newline="\n")
    return 0, f"✓ đã {viec} → {Path(dash) / TEN_SO_NO}"


# ───────────────────────── gom ─────────────────────────

def _lenh_orchestrator(dash: Path, ung_vien: list[dict], _bo_nho: dict | None = None) -> tuple[str, str]:
    """(lát cắt, ghi chú) — lát cắt CŨ NHẤT có ánh xạ watchlist (orchestrator mới chạy A2 được); không lát cắt nào có
    ánh xạ thì lấy cũ nhất kèm ghi chú. Phân giải bằng chính `chu_de_resolver` mà orchestrator dùng."""
    bo_nho = _bo_nho if _bo_nho is not None else {}
    try:
        if "res" not in bo_nho:
            bo_nho["res"] = _nap("_smt_res", TOOLS / "chu_de_resolver.py")
            bo_nho["du_lieu"] = bo_nho["res"].nap_du_lieu(dash)
        for b in ung_vien:
            if bo_nho["res"].resolve(b["lat_cat"], bo_nho["du_lieu"]).get("loai") == "watchlist":
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
        vd = nap_cong()
        kdt = _nap("_smt_kdtcc", TOOLS / "kiem_do_tuoi_chung_cu.py")
    except Exception as exc:  # noqa: BLE001 — cảm biến hỏng phải hiện ra, không im như xanh
        kq["ly_do"] = f"không nạp được cổng/đăng ký chủ đề ({type(exc).__name__}: {str(exc)[:120]})"
        return kq
    if not hasattr(vd, "phan_loai_provenance") or not hasattr(vd, "MOC_PROVENANCE_GOI_MOI"):
        kq["ly_do"] = "cổng verify_dashboard nạp được không có phan_loai_provenance (bản cũ) — không đo theo đúng luật cổng"
        return kq
    moc = vd.MOC_PROVENANCE_GOI_MOI.strftime("%Y%m%d")
    kq["moc_prisma_s"] = moc
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
    kq.update(tong_hop(q["ban"], moc))
    kq["ban"] = q["ban"]
    kq["khong_tach"] = q["khong_tach"]
    if kq["khong_doc_hien_hanh"]:
        kq["chua_do"].append(f"{len(kq['khong_doc_hien_hanh'])} bản hiện hành không đọc được khối DATA")
    sn = phan_loai_no(q["ban"], doc_so_no(dash), hom_nay, moc)
    kq["so_no"] = sn
    if sn["hong"]:
        kq["chua_do"].append(f"sổ nợ {TEN_SO_NO} KHÔNG đọc được ({sn['hong']}) — cổng coi như không có sổ: mọi gói mới "
                             "chỉ có cờ đều bị chặn")
    kq["do_duoc"] = True
    # Ba nhóm cho hòm việc: cổng CHẶN (bản hiện hành) · NỢ còn hạn (bản hiện hành) · chủ đề còn mục kế thừa mang cờ.
    da_noi = {b["lat_cat"] for b in sn["ngoai_so"] + sn["qua_han"] + sn["trong_han"] if b["hien_hanh"]}
    nhom = {"chan": sorted((b for b in sn["ngoai_so"] + sn["qua_han"] if b["hien_hanh"]),
                           key=lambda b: (b["ngay"], b["lat_cat"])),
            "no": sorted((b for b in sn["trong_han"] if b["hien_hanh"]), key=lambda b: (b["ngay"], b["lat_cat"])),
            "a_con_lai": [b for b in kq["a"] if b["lat_cat"] not in da_noi]}
    bo_nho: dict = {}
    kq["goi_y"] = {k: _lenh_orchestrator(dash, v, bo_nho) for k, v in nhom.items() if v}
    kq["nhom"] = nhom
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

    🟠 cổng provenance gói mới ĐANG CHẶN bản hiện hành (CHỈ CÓ CỜ, ngoài sổ nợ hoặc nợ quá hạn).
    🟠/🟡 bản hiện hành còn NỢ trong hạn (≤ 7 ngày ⇒ 🟠) — trả nợ bằng bản nối tiếp ghi lượt tìm.
    🟡 chủ đề còn mục kế thừa mang cờ (lượt mới đã ghi) — làm mới khi tới lượt.
    Mỗi dòng kèm lệnh orchestrator cho lát cắt cũ nhất có ánh xạ watchlist.
    ⓘ marker miễn trừ trong mã tăng so với ảnh chụp ≥ 7 ngày."""
    try:
        kq = do(**kw)
    except Exception as exc:  # noqa: BLE001 — cảm biến hỏng phải hiện ra
        return [], [], [f"lỗi {type(exc).__name__}"], []
    viec: list[tuple[int, str, str, str]] = []
    tt: list[str] = []
    chet: list[str] = [] if kq["do_duoc"] else [kq["ly_do"]]

    def _lenh(k: str) -> tuple[str, str]:
        lat, ghi_chu = kq["goi_y"][k]
        return ghi_chu, f'python3 ops/orchestrator.py --topic "{lat}" --online'

    if kq["do_duoc"]:
        nhom, sn = kq["nhom"], kq["so_no"]
        if nhom["chan"]:
            gc, lenh = _lenh("chan")
            viec.append((1, "👤", f"Cổng provenance gói mới ĐANG CHẶN {len(nhom['chan'])} bản hiện hành CHỈ CÓ CỜ "
                                  f"provenanceUnknown (ngoài sổ nợ hoặc nợ quá hạn): {_ds(nhom['chan'])} — bản nối tiếp "
                                  f"phải ghi lượt tìm vào searchSources + currency{gc}", lenh))
        if nhom["no"]:
            gc, lenh = _lenh("no")
            con = (dt.date.fromisoformat(sn["han"]) - dt.date.fromisoformat(kq["ngay"])).days
            viec.append((1 if con <= 7 else 2, "👤",
                         f"{len(nhom['no'])} bản hiện hành NỢ provenance gói mới (hạn {_ngay(sn['han'].replace('-', ''))}, "
                         f"còn {con} ngày; quá hạn cổng CHẶN): {_ds(nhom['no'])} — trả nợ bằng bản nối tiếp ghi lượt tìm "
                         f"vào searchSources + currency (≈ 0,5–0,8 triệu token/chủ đề){gc}", lenh))
        if nhom["a_con_lai"]:
            gc, lenh = _lenh("a_con_lai")
            viec.append((3, "👤", f"{len(nhom['a_con_lai'])}/{kq['lat_cat_lam_moi_duoc']} chủ đề còn mục KẾ THỪA mang "
                                  f"provenanceUnknown (lượt mới đã ghi; cờ gỡ được khi mục cũ được tìm lại): "
                                  f"{_ds(nhom['a_con_lai'])}{gc}", lenh))
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
        print(f"\n(b) Gói dựng từ {_ngay(kq['moc_prisma_s'])} (mốc luật PRISMA-S gói mới) vẫn khai miễn trừ: "
              f"{kq['b_tong']} tệp ({kq['b_chi_co_tong']} chỉ có cờ · {kq['b_co_ghi_tong']} kế thừa có ghi lượt mới)")
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
    if kq["do_duoc"]:
        print()
        print("\n".join(bao_cao_so_no(kq)))
    for c in kq["chua_do"]:
        print(f"⚪ {c}")
    print("\nCần bác sĩ kiểm chứng — số đo hỗ trợ, không thay phán đoán.")


def bao_cao_so_no(kq: dict) -> list[str]:
    """Các dòng (e) — cổng provenance gói mới và sổ nợ, trên MỌI bản dashboard (cổng chạy trên bất kỳ bản nào xuất lại)."""
    sn = kq["so_no"]
    hh = lambda b: " (hiện hành)" if b["hien_hanh"] else ""  # noqa: E731
    trang = (f"hạn {sn['han']}" if sn["co_so"] else ("HỎNG — coi như không có sổ" if sn["hong"] else "CHƯA lập"))
    dong = [f"(e) Cổng provenance gói mới (CHẶN có sổ nợ từ 21/11/2026) — sổ nợ {TEN_SO_NO}: {trang}"]
    chan = sn["ngoai_so"] + sn["qua_han"]
    if chan:
        dong.append(f"    🔴 cổng ĐANG CHẶN {len(chan)} tệp (ngoài sổ {len(sn['ngoai_so'])} · nợ quá hạn "
                    f"{len(sn['qua_han'])}):")
        dong += [f"       · {b['ngay']} {b['lat_cat']}{hh(b)}" for b in sorted(chan, key=lambda b: b["ngay"])]
    if sn["trong_han"]:
        con = (dt.date.fromisoformat(sn["han"]) - dt.date.fromisoformat(kq["ngay"])).days
        dong.append(f"    🟠 nợ trong hạn {len(sn['trong_han'])} tệp (còn {con} ngày — sau hạn cổng CHẶN):")
        dong += [f"       · {b['ngay']} {b['lat_cat']}{hh(b)}" for b in sorted(sn["trong_han"], key=lambda b: b["ngay"])]
    if not chan and not sn["trong_han"]:
        dong.append("    🟢 Không gói nào dựng từ mốc chỉ có cờ provenanceUnknown.")
    else:
        dong += ["    Trả nợ: bản nối tiếp ghi lượt tìm của CHÍNH bản vào searchSources + currency (giữ cờ cho mục kế "
                 "thừa) —", "    lệnh mỗi chủ đề: python3 ops/orchestrator.py --topic \"<lát cắt>\" --online, rồi dựng bản "
                 "nối tiếp theo skill.", "    Bản đã bị thay không cần trả nợ (không xuất lại). Agent KHÔNG tự lập/gia hạn sổ."]
    return dong


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Sổ miễn trừ — tỷ lệ provenanceUnknown / marker miễn trừ theo thời gian")
    ap.add_argument("--json", action="store_true", help="in JSON máy đọc")
    ap.add_argument("--khong-ghi", action="store_true", help="không ghi ảnh chụp state/so-mien-tru.json")
    ap.add_argument("--dash", type=Path, help="thư mục EBM-Dashboards (mặc định: tự dò / EBM_WORKSPACE_ROOT)")
    ap.add_argument("--tep-state", type=Path, help="tệp ảnh chụp (mặc định state/so-mien-tru.json)")
    ap.add_argument("--so-no", action="store_true", help="sổ nợ cổng provenance gói mới")
    ap.add_argument("--tao", action="store_true", help="(--so-no) lập sổ nợ MỘT lần cho tệp đang vi phạm")
    ap.add_argument("--gia-han", metavar="YYYY-MM-DD", help="(--so-no) dời hạn, giữ nguyên danh sách")
    ap.add_argument("--han", metavar="YYYY-MM-DD", help="(--so-no --tao) hạn trả nợ, ≤ 90 ngày")
    ap.add_argument("--can-cu", help="NGUYÊN VĂN lời bác sĩ (≥ 20 ký tự) — bắt buộc khi lập/gia hạn")
    ap.add_argument("--ghi", action="store_true", help="(--so-no) ghi thật; mặc định chạy khô")
    a = ap.parse_args(argv)
    if a.so_no:
        return lenh_so_no(a)
    kq = do(dash=a.dash, tep_state=a.tep_state, ghi=not a.khong_ghi)
    if a.json:
        print(json.dumps({k: v for k, v in kq.items() if k != "ban"}, ensure_ascii=False, indent=1))
    else:
        in_bao_cao(kq)
    if not kq["do_duoc"]:
        return 2
    return 1 if (kq["a"] or kq["b_chi_co_hien_hanh"]) else 0


def lenh_so_no(a, hom_nay: dt.date | None = None) -> int:
    """Báo nợ / lập / gia hạn sổ nợ provenance. Mã: 0 sạch hoặc lập/gia hạn xong · 1 cổng đang chặn · 2 không đo được ·
    3 từ chối (đã có sổ, thiếu nguyên văn, hạn sai)."""
    hom_nay = hom_nay or dt.date.today()
    kq = do(dash=a.dash, cac_repo={}, tep_state=a.tep_state, hom_nay=hom_nay, ghi=False)
    if not kq["do_duoc"]:
        print(f"⚪ KHÔNG ĐO ĐƯỢC: {kq['ly_do']}")
        return 2
    dash = Path(kq["dash"])
    so_no = doc_so_no(dash)
    if a.tao or a.gia_han:
        if a.tao and so_no is not None:
            print("✗ ĐÃ có sổ nợ — sổ chỉ được lập MỘT lần (bánh cóc: tệp mới không vào nợ). Gia hạn: --gia-han.")
            return 3
        if a.gia_han and so_no is None:
            print("✗ chưa có sổ nợ để gia hạn — lập bằng --tao trước")
            return 3
        muc_no = sorted((b for b in kq["ban"] if b["loai"] == CHI_CO and b["ngay"] >= kq["moc_prisma_s"]),
                        key=lambda b: (b["ngay"], b["lat_cat"]))
        ma, tb = ghi_so_no(dash, muc_no, a.han if a.tao else a.gia_han, a.can_cu or "", ghi=a.ghi,
                           cu=so_no if a.gia_han else None, hom_nay=hom_nay)
        print(tb)
        return ma
    print("\n".join(bao_cao_so_no(kq)))
    print("Cần bác sĩ kiểm chứng.")
    sn = kq["so_no"]
    return 1 if (sn["ngoai_so"] or sn["qua_han"] or sn["hong"]) else 0


if __name__ == "__main__":
    sys.exit(main())
