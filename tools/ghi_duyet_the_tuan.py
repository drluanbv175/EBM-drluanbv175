#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GHI QUYẾT ĐỊNH CỦA BÁC SĨ trên THẺ gói tuần — đóng vòng phản hồi (EV-10, kiểm toàn diện 02/10/2026).

VÌ SAO CÓ. Đo 02/10: `queue/` có 7 gói, 49 thẻ có PMID mà 0 dấu ✓/✗/hoãn; quyết định thật diễn ra trong chat («duyệt truy vấn 22,
26, 27…» 27/09) và không quay lại hệ thống ⇒ máy không biết thẻ nào hữu ích, không đo được thông lượng duyệt, và tuần sau không biết
thẻ nào còn treo. Công cụ này CHỈ GHI ĐÚNG LỜI BÁC SĨ — máy không tự quyết, không đổi decision/gradeLevel của dashboard nào.

    python3 tools/ghi_duyet_the_tuan.py "duyệt W40: 1 ✓ 3 ✗ 5 hoãn"        # chạy thử: in các dòng sẽ ghi
    python3 tools/ghi_duyet_the_tuan.py "W40-02 ✗ thiếu đối chứng" --ghi     # ghi vào state/duyet-the-tuan.jsonl
    python3 tools/ghi_duyet_the_tuan.py --tong-hop                          # thẻ nào của gói mới nhất còn chưa có quyết định

Cú pháp lời bác sĩ: tuần (`W40`) + từng cặp «số thẻ + dấu». Dấu: ✓/v/đồng ý/áp dụng/duyệt ⇒ `ap_dung` · ✗/x/không/bỏ ⇒ `khong` · hoãn/
chờ/để sau ⇒ `hoan`. Thẻ trùng trong một câu ⇒ TỪ CHỐI (không đoán). Thẻ không có trong gói ⇒ TỪ CHỐI. Ghi chú sau dấu (vd «✗ thiếu đối
chứng») được giữ nguyên văn. Sổ `state/duyet-the-tuan.jsonl` (ngoài git) chỉ nối thêm; quyết định sau cùng của một thẻ là dòng mới nhất.
Mã thoát: 0 ổn · 1 (--tong-hop) còn thẻ chưa có quyết định · 2 không đo được (thiếu gói) · 3 từ chối câu. Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import date, datetime
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parent.parent
QUEUE = REPO / "queue"
SO = REPO / "state" / "duyet-the-tuan.jsonl"

_DAU = (
    ("ap_dung", r"✓|✔|\bv\b|đồng ý|dong y|áp dụng|ap dung|duyệt|duyet|\bok\b"),
    ("khong", r"✗|✘|\bx\b|không|khong|bỏ|bo qua|loại|loai"),
    ("hoan", r"hoãn|hoan|chờ|để sau|de sau"),   # KHÔNG có «cho» trơn — từ thường gặp trong ghi chú («cho bệnh nhân…»)
)
_RE_DAU = re.compile("|".join(f"(?P<{k}>{v})" for k, v in _DAU), re.I)
_RE_TUAN = re.compile(r"\bW(\d{1,2})\b", re.I)


def _nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s or "")


def the_cua_goi(tep: Path) -> list[str]:
    """Mã thẻ có trong gói (thứ tự xuất hiện): `[W40-01]`…"""
    return list(dict.fromkeys(re.findall(r"\[(W\d{1,2}-\d{2})\]", tep.read_text(encoding="utf-8", errors="replace"))))


def goi_cua_tuan(tuan: int, queue: Path | None = None) -> Path | None:
    queue = queue or QUEUE
    ds = sorted(queue.glob(f"tuan-*-W{tuan:02d}.md")) if queue.is_dir() else []
    return ds[-1] if ds else None


def phan_tich(cau: str, the_hop_le: list[str] | None = None) -> tuple[list[dict], list[str]]:
    """(quyết định, lỗi). Mỗi quyết định: {the, quyet_dinh, ghi_chu}. Lỗi ⇒ người gọi KHÔNG ghi gì."""
    cau = _nfc(cau)
    m = _RE_TUAN.search(cau)
    if not m:
        return [], ["không thấy tuần (vd «W40») — không đoán tuần"]
    tuan = int(m.group(1))
    # Tách từng cụm «số thẻ (+ mã đầy đủ W40-02 hoặc chỉ 2) + dấu + ghi chú tới cụm kế».
    than = cau[m.end():]
    cum = list(re.finditer(r"(?:W\d{1,2}-)?(?P<so>\d{1,2})\s*[:\-–]?\s*", than, re.I))
    ra, loi, da = [], [], set()
    for i, c in enumerate(cum):
        doan = than[c.end(): cum[i + 1].start() if i + 1 < len(cum) else len(than)]
        md = _RE_DAU.match(doan.strip())
        if not md:
            continue  # số không đi kèm dấu (vd số trong ghi chú) — không phải một quyết định
        the = f"W{tuan:02d}-{int(c.group('so')):02d}"
        if the in da:
            loi.append(f"thẻ {the} xuất hiện hai lần trong cùng câu — không đoán lời nào đúng")
            continue
        da.add(the)
        qd = md.lastgroup
        ghi_chu = doan.strip()[md.end():].strip(" ,;.·—-")
        if the_hop_le is not None and the not in the_hop_le:
            loi.append(f"thẻ {the} không có trong gói tuần W{tuan:02d} (gói có: {', '.join(the_hop_le) or 'không thẻ nào'})")
            continue
        ra.append({"the": the, "quyet_dinh": qd, "ghi_chu": ghi_chu})
    if not ra and not loi:
        loi.append("không thấy cặp «số thẻ + dấu» nào (vd «1 ✓ 3 ✗ 5 hoãn»)")
    return ra, loi


def doc_so(so: Path | None = None) -> dict[str, dict]:
    """Quyết định SAU CÙNG của từng thẻ (dòng mới nhất thắng)."""
    so = so or SO
    ra: dict[str, dict] = {}
    if not so.exists():
        return ra
    for dong in so.read_text(encoding="utf-8").splitlines():
        try:
            d = json.loads(dong)
            ra[d["the"]] = d
        except (ValueError, KeyError, TypeError):
            continue
    return ra


def ghi(quyet_dinh: list[dict], nguyen_van: str, so: Path | None = None, bay_gio: datetime | None = None) -> None:
    so = so or SO
    bay_gio = bay_gio or datetime.now()
    so.parent.mkdir(parents=True, exist_ok=True)
    with open(so, "a", encoding="utf-8", newline="\n") as f:
        for q in quyet_dinh:
            f.write(json.dumps({**q, "luc": bay_gio.isoformat(timespec="seconds"), "nguyen_van": nguyen_van,
                                "nguoi_quyet": "bac_si"}, ensure_ascii=False) + "\n")


def chua_quyet(goi: Path, so: Path | None = None) -> tuple[list[str], list[str]]:
    """(thẻ của gói, thẻ CHƯA có quyết định)."""
    the = the_cua_goi(goi)
    da = doc_so(so)
    return the, [t for t in the if t not in da]


def goi_moi_nhat(queue: Path | None = None) -> Path | None:
    queue = queue or QUEUE
    ds = sorted(queue.glob("tuan-*-W*.md")) if queue.is_dir() else []
    return ds[-1] if ds else None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Ghi quyết định của bác sĩ trên thẻ gói tuần (máy chỉ ghi, không quyết)")
    ap.add_argument("cau", nargs="?", help="lời bác sĩ, vd «duyệt W40: 1 ✓ 3 ✗ 5 hoãn»")
    ap.add_argument("--ghi", action="store_true", help="ghi vào sổ (mặc định chạy thử)")
    ap.add_argument("--tong-hop", action="store_true", help="thẻ của gói mới nhất còn chưa có quyết định")
    a = ap.parse_args(argv)
    if a.tong_hop:
        goi = goi_moi_nhat()
        if goi is None:
            print("⚪ KHÔNG ĐO ĐƯỢC — không thấy queue/tuan-*.md")
            return 2
        the, chua = chua_quyet(goi)
        print(f"Gói {goi.stem}: {len(the) - len(chua)}/{len(the)} thẻ đã có quyết định của bác sĩ.")
        if chua:
            print("  Chưa có: " + " · ".join(chua))
            print('  Ghi: python3 tools/ghi_duyet_the_tuan.py "duyệt W<tuần>: 1 ✓ 3 ✗ 5 hoãn" --ghi')
        print("Cần bác sĩ kiểm chứng.")
        return 1 if chua else 0
    if not a.cau:
        ap.print_help()
        return 2
    m = _RE_TUAN.search(_nfc(a.cau))
    goi = goi_cua_tuan(int(m.group(1))) if m else None
    if m and goi is None:
        print(f"⚪ KHÔNG ĐO ĐƯỢC — không thấy gói queue/tuan-*-W{int(m.group(1)):02d}.md")
        return 2
    qd, loi = phan_tich(a.cau, the_cua_goi(goi) if goi else None)
    for x in loi:
        print(f"✗ {x}")
    if loi:
        print("TỪ CHỐI — chưa ghi gì (sửa câu rồi chạy lại).")
        return 3
    nhan = {"ap_dung": "✓ áp dụng", "khong": "✗ không", "hoan": "⏸ hoãn"}
    for q in qd:
        print(f"  {q['the']}: {nhan[q['quyet_dinh']]}" + (f" — {q['ghi_chu']}" if q["ghi_chu"] else ""))
    if not a.ghi:
        print("(chạy thử — thêm --ghi để ghi vào state/duyet-the-tuan.jsonl)")
        return 0
    ghi(qd, a.cau)
    try:
        noi = SO.relative_to(REPO)
    except ValueError:
        noi = SO
    print(f"✓ đã ghi {len(qd)} quyết định của bác sĩ vào {noi} ({date.today():%d/%m/%Y}).")
    print("Máy KHÔNG đổi decision/gradeLevel của dashboard nào. Cần bác sĩ kiểm chứng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
