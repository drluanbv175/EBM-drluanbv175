#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ÁP DỤNG ĐỀ XUẤT WATCHLIST — chép tầng truy vấn `queries` đã được bác sĩ DUYỆT vào watchlist.json (EV-02, 02/10/2026).

Máy chỉ ĐỀ XUẤT (`EBM-Dashboards/watchlist.de-xuat.json`, soạn khi `tools/kiem_san_luong_giam_sat.py` báo chủ đề «mù»);
việc chép vào watchlist thật là quyết định của bác sĩ vì truy vấn là phán đoán y khoa. Công cụ này chỉ làm phần máy móc,
an toàn, đảo ngược được:

    python3 tools/ap_dung_de_xuat_watchlist.py                    # CHẠY KHÔ (mặc định): kiểm hợp lệ + hiện thay đổi, không ghi gì
    python3 tools/ap_dung_de_xuat_watchlist.py --ap-dung          # ghi: sao lưu watchlist.json.bak-<giờ> rồi chép
    python3 tools/ap_dung_de_xuat_watchlist.py --chu-de gout      # chỉ chủ đề có tên chứa chuỗi này

BẢO ĐẢM (đều có test):
  • CHỈ thay `queries` của chủ đề đã có trong watchlist (khớp TÊN CHÍNH XÁC); `topic`, `query` cũ, `truy_van_du_phong`,
    `active` và mọi chủ đề không nằm trong đề xuất giữ nguyên từng byte giá trị.
  • Chủ đề lạ/trùng tên ⇒ từ chối. Bộ tầng phải TRÙNG bộ tầng hiện có (không âm thầm bỏ tầng `moi_vao_pubmed`).
  • `moi_vao_pubmed` phải `edat` + `loc_thiet_ke:false` (bất biến của bộ quét — nếu không nó rơi lại vào bẫy bộ lọc loại thiết kế).
  • Mỗi truy vấn phải cân ngoặc và có số dấu nháy chẵn (lỗi gõ làm PubMed trả 0 hoặc báo lỗi).
  • Ghi nguyên tử (tệp tạm + os.replace); sao lưu được so byte với bản gốc trước khi ghi đè; không ghi được thì giữ nguyên.
Mã thoát: 0 xong/không có gì để đổi · 1 đề xuất không hợp lệ (không ghi gì) · 2 không đọc/ghi được tệp.
Sau khi áp dụng: đo lại bằng `python3 tools/kiem_san_luong_giam_sat.py`. Cần bác sĩ kiểm chứng."""
from __future__ import annotations

import argparse
import copy
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parent.parent
WATCHLIST = REPO / "EBM-Dashboards" / "watchlist.json"
DE_XUAT = REPO / "EBM-Dashboards" / "watchlist.de-xuat.json"
DATETYPE_HOP_LE = {"pdat", "edat"}
TANG_MOI = "moi_vao_pubmed"


def _truy_van_hop_le(q: object) -> str | None:
    """Trả lý do nếu truy vấn rõ ràng sai cú pháp; None nếu qua. Chỉ bắt lỗi gõ — không thay PubMed kiểm cú pháp."""
    if not isinstance(q, str) or not q.strip():
        return "truy vấn rỗng/không phải chuỗi"
    sau = 0
    for ch in q:
        sau += (ch == "(") - (ch == ")")
        if sau < 0:
            return "ngoặc đóng thừa"
    if sau != 0:
        return "ngoặc không cân"
    if q.count('"') % 2:
        return "số dấu nháy kép lẻ"
    if q.count("[") != q.count("]"):
        return "ngoặc vuông [..] không cân"
    return None


def kiem_tung_chu_de(muc_cu: dict, muc_moi: dict) -> list[str]:
    """Danh sách lỗi của MỘT chủ đề đề xuất so với mục hiện có (rỗng = hợp lệ)."""
    loi: list[str] = []
    ds = muc_moi.get("queries")
    if not isinstance(ds, list) or not ds:
        return ["đề xuất thiếu `queries`"]
    tang_cu = [t.get("tang") for t in muc_cu.get("queries") or []]
    tang_moi = [t.get("tang") if isinstance(t, dict) else None for t in ds]
    if len(set(tang_moi)) != len(tang_moi):
        loi.append(f"trùng tên tầng: {tang_moi}")
    if set(tang_moi) != set(tang_cu):
        loi.append(f"bộ tầng {sorted(map(str, tang_moi))} khác bộ tầng hiện có {sorted(map(str, tang_cu))} "
                   "(không âm thầm thêm/bỏ tầng)")
    for t in ds:
        if not isinstance(t, dict):
            loi.append("một tầng không phải đối tượng")
            continue
        nhan = str(t.get("tang"))
        if t.get("datetype") not in DATETYPE_HOP_LE:
            loi.append(f"tầng {nhan}: datetype {t.get('datetype')!r} ngoài {sorted(DATETYPE_HOP_LE)}")
        if not isinstance(t.get("loc_thiet_ke"), bool):
            loi.append(f"tầng {nhan}: loc_thiet_ke phải là true/false")
        ly_do = _truy_van_hop_le(t.get("query"))
        if ly_do:
            loi.append(f"tầng {nhan}: {ly_do}")
        if nhan == TANG_MOI and (t.get("datetype") != "edat" or t.get("loc_thiet_ke") is not False):
            loi.append(f"tầng {TANG_MOI} phải datetype=edat và loc_thiet_ke=false (bất biến của bộ quét)")
    return loi


def lap_ke_hoach(watchlist: dict, de_xuat: dict, loc_ten: str = "") -> tuple[list[tuple[str, dict]], list[str], list[str]]:
    """Trả (các thay đổi [(tên, queries mới)], lỗi, không đổi). Lỗi ở BẤT KỲ chủ đề nào ⇒ người gọi không ghi gì."""
    theo_ten: dict[str, list[dict]] = {}
    for t in watchlist.get("topics", []):
        theo_ten.setdefault(t.get("topic"), []).append(t)
    doi, loi, khong_doi = [], [], []
    thay_ten: set[str] = set()
    for muc in de_xuat.get("topics", []):
        ten = muc.get("topic")
        if loc_ten and loc_ten.lower() not in str(ten).lower():
            continue
        if ten in thay_ten:
            loi.append(f"{ten}: xuất hiện hai lần trong đề xuất")
            continue
        thay_ten.add(ten)
        cu = theo_ten.get(ten) or []
        if len(cu) != 1:
            loi.append(f"{ten}: " + ("không có trong watchlist" if not cu else f"trùng tên {len(cu)} lần trong watchlist"))
            continue
        e = kiem_tung_chu_de(cu[0], muc)
        if e:
            loi.extend(f"{ten}: {x}" for x in e)
            continue
        if muc["queries"] == cu[0].get("queries"):
            khong_doi.append(ten)
        else:
            doi.append((ten, muc["queries"]))
    return doi, loi, khong_doi


def ap_dung_vao(watchlist: dict, doi: list[tuple[str, list]], hom_nay: str) -> dict:
    """Bản watchlist mới (sao chép sâu): chỉ `queries` của chủ đề đổi + `_updated`."""
    moi = copy.deepcopy(watchlist)
    theo_ten = {t["topic"]: t for t in moi["topics"]}
    for ten, qs in doi:
        theo_ten[ten]["queries"] = copy.deepcopy(qs)
    moi["_updated"] = hom_nay
    return moi


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Chép đề xuất watchlist đã duyệt vào watchlist.json (mặc định chạy khô)")
    ap.add_argument("--watchlist", default=str(WATCHLIST))
    ap.add_argument("--de-xuat", default=str(DE_XUAT))
    ap.add_argument("--chu-de", default="", help="chỉ chủ đề có tên chứa chuỗi này")
    ap.add_argument("--ap-dung", action="store_true", help="GHI thật (có sao lưu). Không có cờ này = chạy khô")
    a = ap.parse_args(argv)
    wl_p, dx_p = Path(a.watchlist), Path(a.de_xuat)
    try:
        wl_text = wl_p.read_text(encoding="utf-8")
        wl = json.loads(wl_text)
        dx = json.loads(dx_p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"✗ Không đọc được tệp: {e}")
        return 2
    doi, loi, khong_doi = lap_ke_hoach(wl, dx, a.chu_de)
    if loi:
        print(f"✗ ĐỀ XUẤT KHÔNG HỢP LỆ — {len(loi)} lỗi, KHÔNG ghi gì:")
        for x in loi:
            print("   ·", x)
        return 1
    print(f"{'ÁP DỤNG' if a.ap_dung else 'CHẠY KHÔ'} — {len(doi)} chủ đề đổi · {len(khong_doi)} đã giống hệt (bỏ qua)")
    for ten, qs in doi:
        print(f"  → {ten}: {len(qs)} tầng ({', '.join(t['tang'] for t in qs)})")
    for ten in khong_doi:
        print(f"  = {ten}: không đổi")
    if not doi:
        print("Không có gì để đổi.")
        return 0
    if not a.ap_dung:
        print("\n(Chạy khô — chưa ghi gì. Thêm --ap-dung để ghi; watchlist.json sẽ được sao lưu trước.)")
        return 0
    sao_luu = wl_p.with_name(wl_p.name + ".bak-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    try:
        shutil.copyfile(wl_p, sao_luu)
        if sao_luu.read_bytes() != wl_p.read_bytes():
            print(f"✗ Bản sao lưu KHÔNG khớp byte với bản gốc — dừng, không ghi: {sao_luu}")
            return 2
        moi = ap_dung_vao(wl, doi, datetime.now().strftime("%Y-%m-%d"))
        tam = wl_p.with_name(wl_p.name + f".tmp{os.getpid()}")
        tam.write_text(json.dumps(moi, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        json.loads(tam.read_text(encoding="utf-8"))  # đọc lại được trước khi thay
        os.replace(tam, wl_p)
    except OSError as e:
        print(f"✗ Không ghi được: {e} — watchlist.json giữ nguyên")
        return 2
    print(f"\n✓ Đã ghi {wl_p.name}; sao lưu: {sao_luu.name}")
    print("  Đo lại: python3 tools/kiem_san_luong_giam_sat.py   (khôi phục: chép lại bản .bak-… đè lên watchlist.json)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
