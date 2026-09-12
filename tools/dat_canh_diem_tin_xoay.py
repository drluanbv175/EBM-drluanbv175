#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ĐẶT-CẠNH — digest xoay vòng cho SessionStart (12/09/2026).

Vì sao có: `tools/dat_canh_chung_cu_moi.py` sinh
`EBM-Dashboards/derivatives/DAT-CANH-CHUNG-CU-MOI_*.md` — 114 mục đối chiếu
chứng cứ đang dùng với nguồn tổng hợp mới hơn — nhưng bác sĩ chỉ thấy nội
dung này nếu TỰ mở file, hoặc đợi gói tuần thứ Hai 18:30
(`goi-duyet-tuan-ebm`). Không có gì in nó ra màn hình mỗi khi mở phiên.

Script này CHỈ đọc & trích NGUYÊN VĂN các đoạn ngắn đã có sẵn trong file
nguồn (tiêu đề mục, PMID, tên tạp chí/năm, nhãn rút bài) — TUYỆT ĐỐI không
đưa phần "Kết luận nguyên văn (abstract)" (quá dài) và không tự diễn giải/
tóm tắt/phán chiều (R28/BH28: nguồn mới có thể CỦNG CỐ hoặc LẬT kết luận
đang dùng, không được đoán hộ). Mã thoát LUÔN 0 — đây là hiển thị, không
phải phán quyết.

Rotation: con trỏ theo INDEX lưu ở `state/dat-canh-xoay.json` (per-máy,
ngoài git theo `.gitignore` dòng `/*` — cùng quy ước với
`state/viec-chua-dong.jsonl`). Mỗi lần chạy lấy N mục kế tiếp rồi advance,
có wrap-around; đổi tên file DAT-CANH (báo cáo mới ra đời) tự reset về 0.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
DASH = REPO / "EBM-Dashboards"
STATE = REPO / "state" / "dat-canh-xoay.json"

_MUC_RE = re.compile(
    r"^## (?P<so>\d+)\.\s*(?P<tieu_de>.+?)\s*\n"
    r"- \*\*Đang dùng:\*\*\s*PMID\s*(?P<pmid_cu>\d+)"
    r"(?:\s*\(năm ghi trên gói:\s*(?P<nam_cu>\d+)\))?[^\n]*\n"
    r"(?:  - nơi dùng:[^\n]*\n)?"
    r"- \*\*Nguồn tổng hợp mới hơn:\*\*\s*(?P<nguon_moi>[^\n]+)\n",
    re.MULTILINE,
)


def file_moi_nhat() -> Path | None:
    """File DAT-CANH-CHUNG-CU-MOI_*.md mới nhất theo tên (ngày trong tên,
    sắp thứ tự chuỗi trùng thứ tự thời gian vì định dạng YYYY-MM-DD)."""
    ds = sorted(DASH.glob("derivatives/DAT-CANH-CHUNG-CU-MOI_*.md"))
    return ds[-1] if ds else None


def doc_muc(duong: Path) -> list[dict]:
    try:
        text = duong.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    ra = []
    for m in _MUC_RE.finditer(text):
        ra.append({
            "so": int(m.group("so")),
            "tieu_de": m.group("tieu_de"),
            "pmid_cu": m.group("pmid_cu"),
            "nam_cu": m.group("nam_cu"),
            "nguon_moi": m.group("nguon_moi"),
        })
    return ra


def doc_con_tro(ten_file: str, tong: int) -> int:
    try:
        d = json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 0
    if d.get("file") != ten_file:
        return 0  # báo cáo mới ra đời (tên khác) → reset về đầu
    ct = d.get("con_tro", 0)
    return ct if isinstance(ct, int) and 0 <= ct < tong else 0


def ghi_con_tro(ten_file: str, con_tro_moi: int) -> None:
    try:
        STATE.parent.mkdir(parents=True, exist_ok=True)
        STATE.write_text(
            json.dumps(
                {"file": ten_file, "con_tro": con_tro_moi,
                 "cap_nhat": dt.date.today().isoformat()},
                ensure_ascii=False,
            ),
            encoding="utf-8",
            newline="\n",
        )
    except OSError:
        pass  # lỗi ghi state không được làm chết hook


def cua_so(muc: list[dict], con_tro: int, so_muc: int) -> list[dict]:
    n = len(muc)
    if n <= so_muc:
        return muc
    return [muc[(con_tro + i) % n] for i in range(so_muc)]


def in_digest(muc_hien: list[dict], tong: int, ten_file: str, ra=print) -> None:
    ra(f"📋 ĐẶT-CẠNH chứng cứ mới hơn — {len(muc_hien)}/{tong} mục (bản {ten_file}); "
       f"không phán chiều, bác sĩ tự so (BH28)")
    for m in muc_hien:
        nguon = m["nguon_moi"]
        if len(nguon) > 160:
            nguon = nguon[:157] + "..."
        tieu_de = m["tieu_de"]
        if len(tieu_de) > 90:
            tieu_de = tieu_de[:87] + "..."
        ra(f"  #{m['so']} {tieu_de}")
        nam = f" ({m['nam_cu']})" if m.get("nam_cu") else ""
        ra(f"     Đang dùng: PMID {m['pmid_cu']}{nam}")
        ra(f"     Nguồn mới: {nguon}")
    ra(f"     → đọc trọn: EBM-Dashboards/derivatives/{ten_file}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--so-muc", type=int, default=4)
    a = ap.parse_args()

    f = file_moi_nhat()
    if f is None:
        return 0
    muc = doc_muc(f)
    if not muc:
        return 0

    con_tro = doc_con_tro(f.name, len(muc))
    hien = cua_so(muc, con_tro, a.so_muc)
    ghi_con_tro(f.name, (con_tro + a.so_muc) % len(muc))
    in_digest(hien, len(muc), f.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
