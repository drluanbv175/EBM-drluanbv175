#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CHỦ ĐỀ NÀO CÓ TRUY VẤN GIÁM SÁT «MÙ»? — chốt SẢN LƯỢNG của watchlist (EV-02, 02/10/2026).

VÌ SAO CÓ. `tools/kiem_phu_giam_sat.py` chỉ đo KHAI BÁO («chủ đề này có mục watchlist»), không đo mục đó có tìm ra gì không.
Đo 02/10/2026 (esearch retmax=0 trên 42 chủ đề có 4 tầng, cửa sổ 90 ngày, đúng chuỗi trong `EBM-Dashboards/watchlist.json` ghép
đúng bộ lọc loại thiết kế của bộ quét thật): 10/42 chủ đề cho ≤3 bản ghi TRONG CẢ BỐN TẦNG (Lupus thận, Cấp cứu ban đầu, Hội chứng thận hư,
Suy thượng thận = 0; Viêm đa dây TK, Kê đơn tâm thần kinh = 1; RA, Động mạch cảnh/mạch máu não = 2; Gout, Hen = 3), trong khi cùng cửa sổ
ĐTĐ+béo phì+GLP-1 có 1.315. Chủ đề RA: truy vấn đang dùng ('rheumatoid arthritis treatment EULAR guideline') bị PubMed ngầm AND mọi từ
(đòi có cả «EULAR» lẫn «guideline») ⇒ 2 bản ghi/90 ngày; thử MeSH + loại thiết kế cho 27–34 mỗi tầng. Nghĩa là «0 ứng viên» ở các chủ đề đó là
CẤU TRÚC TRUY VẤN, không phải «không có chứng cứ mới» (CLAUDE.md §6.4) — và chốt phủ vẫn xanh.

CÔNG CỤ NÀY CHỈ ĐO VÀ BÁO. Không sửa watchlist, không quét, không nạp sổ cái. Soạn lại truy vấn là phán đoán y khoa: máy chỉ ĐỀ XUẤT (tệp
`watchlist.de-xuat.json` cạnh watchlist), bác sĩ duyệt rồi mới chép vào `EBM-Dashboards/watchlist.json` (có sao lưu).

    python3 tools/kiem_san_luong_giam_sat.py                       # đo watchlist thật (≈ 190 lời gọi esearch retmax=0)
    python3 tools/kiem_san_luong_giam_sat.py --watchlist <tệp>     # đo một bản đề xuất TRƯỚC khi duyệt
    python3 tools/kiem_san_luong_giam_sat.py --chu-de lupus --json ra.json

TẦNG THỨ BẬC TRỐNG (thêm 04/10/2026). Ngưỡng «mù» tính TỔNG 4 tầng nên tầng «mới vào PubMed» (không lọc thiết kế) che mất chủ
đề mà ba tầng thứ bậc gần như trống. Đo 04/10: 10 chủ đề KHÔNG mù có 0 tổng quan hệ thống/gộp và guideline+SR+RCT ≤ 1 trong 90
ngày — gồm statin, CKD, COPD (lĩnh vực ra hàng chục tổng quan mỗi quý), trong khi tầng mới-vào-PubMed vẫn có 6–49 bản ghi. Chủ đề
đo trọn, không mù, mà tầng `sr_ma` = 0 VÀ guideline+sr_ma+rct ≤ NGUONG_THU_BAC ⇒ 🟠 «tầng thứ bậc trống — nghi truy vấn hẹp ở tầng
tổng quan/RCT» (khoá JSON `thu_bac_trong`). Chỉ là NGHI để soạn lại truy vấn, không kết luận lĩnh vực thiếu chứng cứ; KHÔNG đổi
mã thoát (chu_trinh_chung_cu đọc mã 1 = «có chủ đề mù»). Chủ đề không có tầng `sr_ma` ⇒ không xét.

Mã thoát: 0 không chủ đề nào mù · 1 có chủ đề mù (≤ ngưỡng, mặc định 3) · 2 KHÔNG ĐO ĐƯỢC (mạng/NCBI chặn/không nạp được bộ quét) — không
đọc thành «ổn». Chủ đề có tầng không đo được ⇒ ghi ⚪ riêng, KHÔNG tính là mù cũng KHÔNG tính là ổn.
Dùng đúng `DESIGN`, `EUTILS` và kênh TLS của bộ quét chuẩn (`sync/skills/cap-nhat-chung-cu-y-khoa/tools/surveillance_scan.py`) để không trôi."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import time
import urllib.error
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parent.parent
WATCHLIST = REPO / "EBM-Dashboards" / "watchlist.json"
SCANNER = REPO / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "surveillance_scan.py"
# Nơi chu_trinh_chung_cu (②b) và tác vụ tuần (2b) ghi kết quả `--json`; `kiem_chuoi_0_ung_vien.py` đọc lại ở đây.
KET_QUA_GAN_NHAT = REPO / "state" / "san-luong-giam-sat-gan-nhat.json"

NGUONG_MU = 3       # tổng bản ghi 4 tầng trong cửa sổ ≤ ngưỡng ⇒ «truy vấn có thể mù»
NGUONG_THU_BAC = 1  # không mù, sr_ma = 0 và guideline+sr_ma+rct ≤ ngưỡng ⇒ «tầng thứ bậc trống» (🟠, không đổi mã thoát)
TANG_THU_BAC = ("guideline", "sr_ma", "rct")
SO_NGAY = 90        # cùng trần cửa sổ `--days` mặc định của bộ quét
GIAN_CACH_S = 0.4   # NCBI không khoá: tối đa 3 lời gọi/giây (có NCBI_API_KEY thì 0.12)
SO_LAN_THU = 3

Fetch = Callable[[str, str, int], int]   # (term, datetype, days) -> số bản ghi


def nap_bo_quet():
    """Nạp bộ quét chuẩn để lấy ĐÚNG hằng DESIGN/EUTILS và kênh TLS. Lỗi nạp ⇒ ném (người gọi trả mã 2)."""
    spec = importlib.util.spec_from_file_location("surveillance_scan_san_luong", SCANNER)
    m = importlib.util.module_from_spec(spec)
    sys.modules["surveillance_scan_san_luong"] = m  # @dataclass cần mô-đun đã đăng ký trước khi exec
    try:
        spec.loader.exec_module(m)
    except BaseException:
        sys.modules.pop("surveillance_scan_san_luong", None)
        raise
    return m


def tao_fetch_ncbi(bo_quet) -> Fetch:
    """Fetch thật: esearch retmax=0, ĐẾM số bản ghi. Trang chặn IP/HTML/JSON hỏng ⇒ ném (không đọc thành 0)."""
    khoa = os.environ.get("NCBI_API_KEY", "").strip()
    email = os.environ.get("NCBI_EMAIL", "").strip()
    gian_cach = 0.12 if khoa else GIAN_CACH_S

    def fetch(term: str, datetype: str, days: int) -> int:
        params = {"db": "pubmed", "retmode": "json", "retmax": "0", "term": term, "datetype": datetype,
                  "reldate": str(days), "tool": "medical_ebm_surveillance_san_luong"}
        if khoa:
            params["api_key"] = khoa
        if email:
            params["email"] = email
        url = bo_quet.EUTILS + "esearch.fcgi?" + urllib.parse.urlencode(params)
        loi: Exception | None = None
        for lan in range(SO_LAN_THU):
            time.sleep(gian_cach * (lan + 1))
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "ebm-san-luong/1"})
                with bo_quet._open_url(req, timeout=30) as r:
                    raw = r.read().decode("utf-8", "replace")
                kq = json.loads(raw)["esearchresult"]
                if "ERROR" in kq:
                    raise ValueError(f"NCBI báo lỗi: {kq['ERROR']}")
                return int(kq["count"])
            except (urllib.error.URLError, TimeoutError, ValueError, KeyError, OSError) as e:
                loi = e
        raise RuntimeError(f"không đo được sau {SO_LAN_THU} lần: {loi}")

    return fetch


def thuat_ngu_that(truy_van: str, loc_thiet_ke: bool, design: str) -> str:
    """ĐÚNG phép ghép của `surveillance_scan.search()` (dòng `term = ...`)."""
    return f"({truy_van}) AND {design}" if loc_thiet_ke else f"({truy_van})"


def do_chu_de(muc: dict, fetch: Fetch, design: str, days: int = SO_NGAY) -> dict:
    """Đo mọi tầng của MỘT chủ đề. Tầng lỗi ⇒ dem=None (không đoán), kèm lý do."""
    tang_ds = []
    for t in muc.get("queries") or []:
        tang = {"tang": t.get("tang", "?"), "datetype": t.get("datetype", "pdat"),
                "loc_thiet_ke": bool(t.get("loc_thiet_ke", True)), "dem": None}
        try:
            tang["dem"] = fetch(thuat_ngu_that(t["query"], tang["loc_thiet_ke"], design), tang["datetype"], days)
        except Exception as e:  # noqa: BLE001 — mạng/NCBI: ghi lý do, KHÔNG biến thành 0
            tang["loi"] = str(e)[:200]
        tang_ds.append(tang)
    do_het = bool(tang_ds) and all(t["dem"] is not None for t in tang_ds)
    return {"topic": muc.get("topic", "?"), "tang": tang_ds, "do_duoc": do_het,
            "tong": sum(t["dem"] for t in tang_ds if t["dem"] is not None)}


def phan_loai(kq: dict, nguong: int) -> str:
    """MU = đo đủ mọi tầng mà tổng ≤ ngưỡng · KHONG_DO = có tầng không đo được · ON = còn lại."""
    if not kq["do_duoc"]:
        return "KHONG_DO"
    return "MU" if kq["tong"] <= nguong else "ON"


def thu_bac_trong(kq: dict) -> bool:
    """Chủ đề ĐO TRỌN, không mù, có tầng `sr_ma` = 0 và guideline+sr_ma+rct ≤ NGUONG_THU_BAC. Tính từ `tang` của chính
    kết quả (nên tệp --json cũ không có khoá `thu_bac_trong` vẫn in đúng khi dùng lại). Tầng thiếu/không đo ⇒ False."""
    if kq.get("loai") != "ON" or not kq.get("do_duoc"):
        return False
    dem = {t.get("tang"): t.get("dem") for t in kq.get("tang") or []}
    if dem.get("sr_ma") != 0:
        return False
    return sum(dem.get(t) or 0 for t in TANG_THU_BAC) <= NGUONG_THU_BAC


def kiem(watchlist: dict, fetch: Fetch, design: str, *, nguong: int = NGUONG_MU, days: int = SO_NGAY,
         loc_ten: str = "") -> dict:
    """Đo mọi chủ đề đang bật CÓ `queries` (nhóm cơ quan thẩm quyền cố ý không áp tầng ⇒ bỏ qua, có đếm)."""
    ket, bo_qua = [], []
    for muc in watchlist.get("topics", []):
        if not muc.get("active", True):
            continue
        if loc_ten and loc_ten.lower() not in str(muc.get("topic", "")).lower():
            continue
        if not muc.get("queries"):
            bo_qua.append(muc.get("topic", "?"))
            continue
        kq = do_chu_de(muc, fetch, design, days)
        kq["loai"] = phan_loai(kq, nguong)
        ket.append(kq)
    return {"nguong": nguong, "so_ngay": days, "chu_de": ket, "bo_qua_khong_tang": bo_qua,
            "mu": [k["topic"] for k in ket if k["loai"] == "MU"],
            "khong_do": [k["topic"] for k in ket if k["loai"] == "KHONG_DO"],
            "thu_bac_trong": [k["topic"] for k in ket if thu_bac_trong(k)]}


def bam_watchlist(wl_text: str) -> str:
    """Băm SHA-256 NỘI DUNG watchlist (văn bản đã đọc) — MỘT định nghĩa cho cả lúc ghi kết quả lẫn lúc xét dùng lại
    (`kiem_chuoi_0_ung_vien.py` cũng gọi hàm này; hai nơi tự băm là hai chỗ cho phép đo trôi)."""
    return hashlib.sha256(wl_text.encode("utf-8")).hexdigest()


def dung_lai_duoc(duong_dan: Path, sha_watchlist: str, nguong: int, days: int, so_ngay_moi: float,
                  bay_gio: datetime | None = None) -> dict | None:
    """Kết quả đo CŨ nếu còn dùng được: cùng watchlist (băm SHA-256), cùng ngưỡng/cửa sổ, ≤ N ngày, và LẦN ĐÓ đo trọn
    (không có tầng lỗi). Đổi watchlist (vd sau `ap_dung_de_xuat_watchlist.py`) ⇒ băm đổi ⇒ tự đo lại."""
    try:
        d = json.loads(duong_dan.read_text(encoding="utf-8"))
        t = datetime.fromisoformat(d["do_luc"])
    except (OSError, ValueError, KeyError, TypeError):
        return None
    if t.tzinfo is None:
        t = t.replace(tzinfo=timezone.utc)
    if not isinstance(d, dict) or not {"nguong", "so_ngay", "chu_de", "mu", "khong_do", "bo_qua_khong_tang"} <= set(d):
        return None  # tệp thiếu khoá (bản cũ/sửa tay) ⇒ không in được — đo lại thay vì sập
    if (d.get("watchlist_sha256") != sha_watchlist or d.get("nguong") != nguong or d.get("so_ngay") != days
            or d.get("khong_do") or not d.get("chu_de")):
        return None
    tuoi = (bay_gio or datetime.now(timezone.utc)) - t
    return d if timedelta(0) <= tuoi < timedelta(days=so_ngay_moi) else None


def ma_thoat(bao_cao: dict) -> int:
    """2 nếu KHÔNG đo được (không chủ đề nào đo đủ, hoặc không có chủ đề); 1 nếu có chủ đề mù; 0 nếu không."""
    ds = bao_cao["chu_de"]
    if not ds or all(k["loai"] == "KHONG_DO" for k in ds):
        return 2
    return 1 if bao_cao["mu"] else 0


def in_bao_cao(b: dict) -> None:
    ds = b["chu_de"]
    print(f"SẢN LƯỢNG GIÁM SÁT — {len(ds)} chủ đề có tầng · cửa sổ {b['so_ngay']} ngày · mù = tổng 4 tầng ≤ {b['nguong']}")
    hep = [k["topic"] for k in ds if thu_bac_trong(k)]
    for k in sorted(ds, key=lambda x: (x["loai"] != "MU", not thu_bac_trong(x), x["tong"])):
        bieu = "🟠" if thu_bac_trong(k) else {"MU": "🔴", "KHONG_DO": "⚪", "ON": "🟢"}[k["loai"]]
        chi_tiet = " ".join(f"{t['tang'].split('_')[0][:5]}={'?' if t['dem'] is None else t['dem']}" for t in k["tang"])
        print(f"  {bieu} {k['topic'][:58]:<58} tổng={k['tong']:<6} {chi_tiet}")
    if b["mu"]:
        print(f"\n🔴 {len(b['mu'])} chủ đề CÓ THỂ MÙ: «0 ứng viên» ở đó là cấu trúc truy vấn, KHÔNG phải «không có chứng cứ mới».")
        print("   Soạn lại bằng MeSH/tiab + OR (không dồn nhiều khái niệm vào một cụm dài — PubMed ngầm AND mọi từ); máy chỉ ĐỀ XUẤT,")
        print("   bác sĩ duyệt rồi chép vào EBM-Dashboards/watchlist.json (có sao lưu). Đo bản đề xuất bằng --watchlist <tệp> trước khi duyệt.")
    if hep:
        print(f"\n🟠 {len(hep)} chủ đề TẦNG THỨ BẬC TRỐNG (không mù, nhưng 0 tổng quan và guideline+SR+RCT ≤ {NGUONG_THU_BAC}/"
              f"{b['so_ngay']} ngày): {'; '.join(hep[:6])}{'…' if len(hep) > 6 else ''}")
        print("   Tầng «mới vào PubMed» làm tổng vượt ngưỡng mù nên che chỗ này. NGHI truy vấn hẹp ở tầng tổng quan/RCT — soạn lại như")
        print("   chủ đề mù (máy đề xuất, bác sĩ duyệt); KHÔNG kết luận lĩnh vực thiếu chứng cứ. Không đổi mã thoát.")
    if b["khong_do"]:
        print(f"\n⚪ {len(b['khong_do'])} chủ đề có tầng KHÔNG đo được (mạng/NCBI) — không phải mù, cũng không phải ổn: "
              + "; ".join(b["khong_do"][:5]))
    if b["bo_qua_khong_tang"]:
        print(f"\nℹ {len(b['bo_qua_khong_tang'])} mục không có tầng (nhóm cơ quan thẩm quyền, cố ý không áp thứ bậc) — không đo ở đây.")
    print("\nChốt này chỉ ĐO sản lượng truy vấn — không chứng minh lượt quét đã chạy, không đánh giá chất lượng bài tìm được. Cần bác sĩ kiểm chứng.")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Đo sản lượng truy vấn giám sát: chủ đề nào có thể «mù»")
    ap.add_argument("--watchlist", default=str(WATCHLIST), help="watchlist cần đo (mặc định EBM-Dashboards/watchlist.json)")
    ap.add_argument("--nguong", type=int, default=NGUONG_MU)
    ap.add_argument("--ngay", type=int, default=SO_NGAY)
    ap.add_argument("--chu-de", default="", help="chỉ đo chủ đề có tên chứa chuỗi này")
    ap.add_argument("--json", default="", help="ghi báo cáo máy đọc ra tệp này")
    ap.add_argument("--dung-lai-neu-moi-hon-ngay", type=float, default=0.0, metavar="N",
                    help="cần --json: nếu tệp đó đo CÙNG watchlist/ngưỡng/cửa sổ, trọn vẹn và ≤ N ngày thì in lại, không gọi mạng")
    a = ap.parse_args(argv)
    try:
        wl_text = Path(a.watchlist).read_text(encoding="utf-8")
        wl = json.loads(wl_text)
    except (OSError, ValueError) as e:
        print(f"⚪ KHÔNG ĐO ĐƯỢC — không đọc được watchlist {a.watchlist}: {e}")
        return 2
    try:
        bo_quet = nap_bo_quet()
        design = bo_quet.DESIGN
        fetch = tao_fetch_ncbi(bo_quet)
    except BaseException as e:  # noqa: BLE001 — chốt hỏng phải LỘ RA, không im lặng xanh
        if isinstance(e, KeyboardInterrupt):
            raise
        print(f"⚪ KHÔNG ĐO ĐƯỢC — không nạp được bộ quét chuẩn: {type(e).__name__}: {e}")
        return 2
    sha = bam_watchlist(wl_text)
    if a.dung_lai_neu_moi_hon_ngay and a.json and not a.chu_de:
        cu = dung_lai_duoc(Path(a.json), sha, a.nguong, a.ngay, a.dung_lai_neu_moi_hon_ngay)
        if cu is not None:
            in_bao_cao(cu)
            print(f"\n(Dùng lại lượt đo {cu['do_luc'][:16]} — cùng watchlist, chưa quá {a.dung_lai_neu_moi_hon_ngay:g} ngày; "
                  "xoá tệp --json hoặc bỏ --dung-lai-neu-moi-hon-ngay để đo lại.)")
            return ma_thoat(cu)
    bao_cao = kiem(wl, fetch, design, nguong=a.nguong, days=a.ngay, loc_ten=a.chu_de)
    bao_cao["do_luc"] = datetime.now(timezone.utc).isoformat()
    bao_cao["watchlist_sha256"] = sha
    in_bao_cao(bao_cao)
    if a.json:
        Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        Path(a.json).write_text(json.dumps(bao_cao, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    ma = ma_thoat(bao_cao)
    if ma == 2:
        print("\n⚪ KHÔNG ĐO ĐƯỢC — không chủ đề nào đo đủ các tầng (NCBI chặn IP/mạng?). KHÔNG đọc là «không có chủ đề mù».")
    return ma


if __name__ == "__main__":
    sys.exit(main())
