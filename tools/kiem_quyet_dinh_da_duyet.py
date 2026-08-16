#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CHỐT HỒI QUY QUYẾT ĐỊNH ĐÃ DUYỆT — bắt tái phạm im lặng (16/08/2026).

VÌ SAO CÓ
=========
Bộ chốt BH01–BH57 đóng vòng học cho CÔNG CỤ. Nhưng vòng học NỘI DUNG thì chưa:
15 quyết định lâm sàng bác sĩ duyệt 13–14/08 (hạ `decision`, khai
`normativeBasis`, giữ `apply` cho cảnh báo an toàn…) chỉ nằm trong văn xuôi
CLAUDE.md — một dashboard sinh lại từ skill cũ, hoặc một đợt sửa hàng loạt sau
này, có thể LẬT NGƯỢC IM LẶNG các quyết định đó mà không chốt nào kêu. Đã xảy
ra thật: 5 mục Đau Đầu tái lệch chính là hệ quả đợt sửa 12/08; và họ lỗi «sửa
xong lại như cũ» từng có tiền sử ở CSS dashboard.

CÁCH LÀM
========
Sổ máy-đọc: `EBM-Dashboards/quyet-dinh-da-duyet.json` (CHỈ bác sĩ thêm/sửa).
Với mỗi quyết định: tìm item theo `item` id (ưu tiên) hoặc `pmid` trong file
nêu đích danh, so từng trường kỳ vọng. Kỳ vọng dạng danh sách = «một trong».

Ba mức, tách «không biết» khỏi «có vấn đề» (BH08):
  ✓  khớp — quyết định còn nguyên
  🔴 LỆCH — tái phạm quyết định đã duyệt (mã thoát 2)
  ⚪ không kiểm được — file/item biến mất, đổi tên (mã thoát 1; không đỏ oan)

Chốt chỉ ĐO và BÁO — không ghi vào dashboard (BH10). Muốn áp lại quyết định,
bác sĩ ra lệnh riêng. Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
DASH = REPO / "EBM-Dashboards"
SO = DASH / "quyet-dinh-da-duyet.json"


def _nap_vd():
    spec = importlib.util.spec_from_file_location("_vd_qd", DASH / "tools" / "verify_dashboard.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_vd_qd"] = mod
    spec.loader.exec_module(mod)
    return mod


def kiem(so_path: Path = SO, dash_dir: Path = DASH) -> tuple[list[str], list[str], list[str]]:
    """Trả (khop, lech, khong_kiem_duoc) — hàm thuần để chốt BH đột biến bằng fixture."""
    vd = _nap_vd()
    du_lieu = json.loads(so_path.read_text(encoding="utf-8"))
    khop: list[str] = []
    lech: list[str] = []
    mu: list[str] = []
    cache: dict[str, list[str]] = {}
    for qd in du_lieu.get("quyet_dinh", []):
        ten = qd["file"]
        nhan = f"{ten} · {qd.get('item') or 'PMID ' + qd.get('pmid', '?')}"
        f = dash_dir / ten
        if not f.exists():
            mu.append(f"{nhan} — FILE không còn (đổi tên? xoá?)")
            continue
        if ten not in cache:
            try:
                blk = vd.extract_data_block(f.read_text(encoding="utf-8", errors="replace"))
                cache[ten] = vd.split_items(blk)
            except Exception as e:  # noqa: BLE001 — khối DATA hỏng là «không kiểm được», không phải «lệch»
                cache[ten] = []
                mu.append(f"{nhan} — khối DATA không đọc được: {e}")
                continue
        items = cache[ten]
        muc = None
        if qd.get("item"):
            muc = next((c for c in items if vd.field(c, "id") == qd["item"]), None)
        elif qd.get("pmid"):
            muc = next((c for c in items if (vd.field(c, "pmid") or "").strip() == qd["pmid"]), None)
        if muc is None:
            mu.append(f"{nhan} — ITEM biến mất khỏi gói")
            continue
        loi_muc = []
        for truong, ky_vong in qd["ky_vong"].items():
            thuc = (vd.field(muc, truong) or "").strip()
            dat = thuc in ky_vong if isinstance(ky_vong, list) else thuc == ky_vong
            if not dat:
                mong = " | ".join(ky_vong) if isinstance(ky_vong, list) else ky_vong
                loi_muc.append(f"{truong}='{thuc or '(rỗng)'}' ≠ đã duyệt '{mong}'")
        if loi_muc:
            lech.append(f"{nhan} — {'; '.join(loi_muc)} (duyệt {qd['duyet']}: {qd['ly_do'][:60]})")
        else:
            khop.append(nhan)
    return khop, lech, mu


def main() -> int:
    if not SO.exists():
        print("⚪ Chưa có sổ quyet-dinh-da-duyet.json — không có gì để canh.")
        return 1
    khop, lech, mu = kiem()
    print(f"CHỐT QUYẾT ĐỊNH ĐÃ DUYỆT — {len(khop) + len(lech) + len(mu)} mục trong sổ")
    for x in lech:
        print(f"  🔴 TÁI PHẠM: {x}")
    for x in mu:
        print(f"  ⚪ {x}")
    print(f"KẾT: ✓ {len(khop)} còn nguyên · 🔴 {len(lech)} tái phạm · ⚪ {len(mu)} không kiểm được.")
    print("Chốt chỉ ĐO — muốn áp lại quyết định, bác sĩ ra lệnh riêng. Cần bác sĩ kiểm chứng.")
    return 2 if lech else (1 if mu else 0)


if __name__ == "__main__":
    raise SystemExit(main())
