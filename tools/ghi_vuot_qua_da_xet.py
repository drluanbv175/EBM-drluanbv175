#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ghi sổ «BÁC SĨ ĐÃ XÉT» cho các mục `apply` có tổng quan/guideline mới hơn — `EBM-Dashboards/vuot-qua-da-xet.json`.

VÌ SAO CÓ (18/10/2026)
======================
`dat_canh_chung_cu_moi.py` đếm mọi mục `apply` mà PubMed (`pubmed_pubmed_reviews`) trả về bài tổng hợp mới hơn — kể cả
khi các bài đó LẠC CHỦ ĐỀ — và không có chỗ ghi «đã so». Con số trên hòm việc / Đài hoàn thiện vì thế không bao giờ
giảm (đo 18/10: 112/155 mục, 358 cặp; sàng lọc theo tiêu đề: 29 mục mọi nguồn lạc chủ đề, 4 mục là chính nguồn).

THẨM QUYỀN
==========
Phán đoán «lạc chủ đề / đã so, giữ / cần cập nhật» là của BÁC SĨ (BH28). Máy chỉ SOẠN đề xuất sàng lọc; công cụ này chỉ
GHI LẠI lời bác sĩ: bắt buộc `--loi` (nguyên văn), chạy khô mặc định, `--ghi` mới ghi (sao lưu trước). Không đổi dashboard,
`decision` hay `gradeLevel` (BH10).

Dùng:
    # đóng hàng loạt các mục bác sĩ xác nhận là lạc chủ đề / chính nguồn (CHỈ nhóm L, S của tệp sàng lọc)
    python3 tools/ghi_vuot_qua_da_xet.py --sang-loc <tệp.json> --nhom L,S --loi "<nguyên văn bác sĩ>" [--ghi]
    # một mục sau khi bác sĩ đã đọc so
    python3 tools/ghi_vuot_qua_da_xet.py --pmid 123 --ket-luan da_so_giu --pmid-moi 456,789 --loi "<…>" [--ghi]

Kết luận: lac_chu_de · chinh_nguon · da_so_giu (ba loại ĐÓNG) · can_cap_nhat (vẫn được đếm tới khi gói cập nhật).
Mã thoát: 0 = xong / chạy khô · 2 = tham số sai. Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
SO = REPO / "EBM-Dashboards" / "vuot-qua-da-xet.json"
KET_LUAN = ("lac_chu_de", "chinh_nguon", "da_so_giu", "can_cap_nhat")
NHOM_DONG_LOAT = {"L": "lac_chu_de", "S": "chinh_nguon"}
GIOI_THIEU = ("Sổ BÁC SĨ đã xét các mục `apply` có tổng quan/guideline mới hơn (dat_canh_chung_cu_moi.py). Chỉ "
              "tools/ghi_vuot_qua_da_xet.py ghi, theo nguyên văn lời bác sĩ; nguồn mới chưa có trong pmid_moi_da_xet ⇒ "
              "mục tự mở lại.")


def doc_so(p: Path) -> dict:
    """Sổ hiện có; vắng ⇒ sổ rỗng. Hỏng ⇒ ném lỗi (KHÔNG ghi đè sổ hỏng bằng sổ mới)."""
    if not p.exists():
        return {"_about": GIOI_THIEU, "muc": {}}
    d = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(d, dict) or not isinstance(d.get("muc"), dict):
        raise ValueError(f"{p.name} sai cấu trúc — không ghi đè")
    return d


def muc_tu_sang_loc(sang_loc: dict, nhom: set[str]) -> list[dict]:
    """Các mục của tệp sàng lọc thuộc nhóm được đóng hàng loạt (chỉ L/S)."""
    return [m for m in sang_loc.get("muc") or [] if m.get("nhom") in nhom]


def ap_dung(so: dict, cac_muc: list[dict], ngay: str, loi: str, nguon: str) -> list[str]:
    """Ghi từng mục vào sổ (gộp pmid_moi_da_xet với lần xét trước). Trả danh sách dòng mô tả thay đổi."""
    doi = []
    for m in cac_muc:
        pm = str(m["pmid"])
        cu = so["muc"].get(pm) or {}
        moi = sorted({str(x) for x in (cu.get("pmid_moi_da_xet") or [])} | {str(x) for x in m["pmid_moi"]})
        so["muc"][pm] = {"pmid_moi_da_xet": moi, "ket_luan": m["ket_luan"], "ngay": ngay, "loi_bac_si": loi,
                         "de_xuat_tu": nguon}
        doi.append(f"PMID {pm}: {m['ket_luan']} · {len(moi)} nguồn mới đã xét")
    return doi


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Ghi sổ bác sĩ đã xét nguồn tổng hợp mới hơn")
    ap.add_argument("--sang-loc", type=Path, help="tệp sàng lọc JSON (máy soạn) — dùng kèm --nhom")
    ap.add_argument("--nhom", help="nhóm đóng hàng loạt, chỉ L và/hoặc S (vd L,S)")
    ap.add_argument("--pmid", help="một mục: PMID đang dùng")
    ap.add_argument("--ket-luan", choices=KET_LUAN)
    ap.add_argument("--pmid-moi", help="một mục: các PMID nguồn mới đã xét, cách nhau dấu phẩy")
    ap.add_argument("--loi", help="NGUYÊN VĂN lời bác sĩ (bắt buộc)")
    ap.add_argument("--so", type=Path, default=SO, help=argparse.SUPPRESS)
    ap.add_argument("--ghi", action="store_true")
    a = ap.parse_args(argv)
    if not (a.loi or "").strip():
        print("Thiếu --loi: chỉ ghi khi có nguyên văn lời bác sĩ.")
        return 2
    if a.sang_loc:
        nhom = {x.strip().upper() for x in (a.nhom or "").split(",") if x.strip()}
        if not nhom or not nhom <= set(NHOM_DONG_LOAT):
            print("--nhom chỉ nhận L và/hoặc S — nhóm A/B phải đọc so từng mục rồi ghi bằng --pmid.")
            return 2
        sl = json.loads(a.sang_loc.read_text(encoding="utf-8"))
        cac_muc = [{"pmid": m["pmid"], "pmid_moi": m.get("pmid_moi") or [], "ket_luan": NHOM_DONG_LOAT[m["nhom"]]}
                   for m in muc_tu_sang_loc(sl, nhom)]
        nguon = f"sàng lọc máy theo tiêu đề ({a.sang_loc.name}), bác sĩ xác nhận nhóm {','.join(sorted(nhom))}"
    elif a.pmid and a.ket_luan and a.pmid_moi:
        cac_muc = [{"pmid": a.pmid, "pmid_moi": [x.strip() for x in a.pmid_moi.split(",") if x.strip()],
                    "ket_luan": a.ket_luan}]
        nguon = "bác sĩ đọc so từng mục"
    else:
        print("Cần --sang-loc + --nhom, hoặc --pmid + --ket-luan + --pmid-moi.")
        return 2
    so = doc_so(a.so)
    doi = ap_dung(so, cac_muc, dt.date.today().isoformat(), a.loi.strip(), nguon)
    print("\n".join(doi) or "Không có mục nào thuộc nhóm đã chọn.")
    if not a.ghi:
        print(f"CHẠY KHÔ — {len(doi)} mục, chưa ghi. Thêm --ghi để ghi (có sao lưu).")
        return 0
    if a.so.exists():
        shutil.copy2(a.so, a.so.with_name(a.so.name + f".bak-{dt.datetime.now():%Y%m%d-%H%M%S}"))
    so["_about"] = GIOI_THIEU
    a.so.parent.mkdir(parents=True, exist_ok=True)
    with open(a.so, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(so, ensure_ascii=False, indent=1) + "\n")
    print(f"ĐÃ GHI {len(doi)} mục → {a.so.name}. Lượt dat_canh_chung_cu_moi.py sau sẽ không đếm các mục đã đóng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
