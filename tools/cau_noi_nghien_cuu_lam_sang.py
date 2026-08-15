#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CẦU NỐI NGHIÊN CỨU ⇄ LÂM SÀNG — hai hệ phải nói chuyện với nhau (nâng cấp D, 15/08/2026).

Vì sao: hai hệ sống cạnh nhau nhưng câm với nhau, đo được hai lỗ:
  (1) NỀN Y VĂN của đề tài (62 PMID C1a) không nằm trong sổ xác minh nguồn — mọi
      nhịp canh rút bài định kỳ của hệ lâm sàng KHÔNG canh hộ đề tài đang chạy;
      đề tài chỉ được kiểm đúng lúc ai đó chạy tay.
  (2) Chiều ngược: `kiem_chung_cu_vuot_qua` bắt được guideline/SR mới nhưng không
      báo cho đề tài liên quan; một đề tài viết Bàn luận trên nền đã bị vượt qua
      mà không hay biết.

Việc tool làm — chỉ ĐO, GHI SỔ và BÁO; không sửa artifact đề tài, không đổi
decision, không mở cổng nào:
  ① Chiều NC → LS: gom PMID nền của MỖI đề tài thật trong exports/ vào sổ xác minh
     (gắn nhãn `NC:<mã đề tài>` trong cac_dashboard) — từ đây các nhịp quét định kỳ
     của hệ lâm sàng tự canh rút bài/hết hạn CHO CẢ nền đề tài.
  ② Chiều LS → NC: chạy chuỗi rút bài trên nền từng đề tài; có tín hiệu DƯƠNG
     (rút bài/EoC) → ghi `exports/<study>/CANH-BAO-CHUNG-CU_<ngày>.md` để lần
     mở đề tài nào cũng thấy (study_readiness liệt kê file .md).

Đề tài fixture/demo (ZZ*, PYTEST*, TEST*) bỏ qua — cầu chỉ phục vụ đề tài thật.

Dùng:  python3 tools/cau_noi_nghien_cuu_lam_sang.py            # mọi đề tài thật
       python3 tools/cau_noi_nghien_cuu_lam_sang.py --study hai-long-benh-nhan-C1a-BVQY175
Mã thoát: 0 = chạy trọn (kể cả khi CÓ cảnh báo — cảnh báo là sản phẩm, không phải lỗi)
· 1 = không có đề tài nào · 2 = hạ tầng.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
EXPORTS = REPO / "medical-ebm-automation" / "exports"
BO_QUA = re.compile(r"^(ZZ|PYTEST|TEST|DEMO)", re.I)


def _nap(ten: str, duong: Path):
    sp = importlib.util.spec_from_file_location(ten, duong)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


def pmids_cua_de_tai(sdir: Path) -> set[str]:
    ra: set[str] = set()
    for f in sdir.glob("*.md"):
        ra |= set(re.findall(r"PMID[: ]*(\d{7,9})", f.read_text(encoding="utf-8",
                                                                errors="replace")))
    return ra


def main() -> int:
    ap = argparse.ArgumentParser(description="Cầu nối nền y văn đề tài ⇄ sổ canh lâm sàng")
    ap.add_argument("--study", help="chỉ một đề tài (mặc định: mọi đề tài thật)")
    a = ap.parse_args()
    if not EXPORTS.exists():
        print("🔴 Không thấy exports/ — chạy từ thư mục gốc Claude AI.")
        return 2
    studies = ([EXPORTS / a.study] if a.study
               else [d for d in sorted(EXPORTS.iterdir())
                     if d.is_dir() and not BO_QUA.match(d.name)])
    studies = [d for d in studies if d.exists() and any(d.glob("*.md"))]
    if not studies:
        print("Không có đề tài thật nào có tài liệu — cầu chưa có gì để nối.")
        return 1

    so_mod = _nap("so_xm_cau", REPO / "tools" / "so_xac_minh_nguon.py")
    so = so_mod.doc_so()
    muc = so["muc"]
    chain = None
    try:
        sys.path.insert(0, str(REPO / "medical-ebm-automation"))
        from app.sources.retraction_chain import RetractionChain  # noqa: PLC0415
        chain = RetractionChain()
    except Exception as e:  # noqa: BLE001
        print(f"⚠ Chuỗi rút bài không nạp được ({e}) — chiều ② sẽ ghi «chưa kiểm», "
              "KHÔNG ghi «sạch».")

    hom_nay = dt.date.today().isoformat()
    tong_ghi_so = 0
    for sdir in studies:
        ten = sdir.name
        pmids = pmids_cua_de_tai(sdir)
        if not pmids:
            continue
        nhan = f"NC:{ten}"
        ghi_so = 0
        for pm in sorted(pmids):
            khoa = f"pmid:{pm}"
            bg = muc.setdefault(khoa, {"loai": "pmid", "gia_tri": pm,
                                       "cac_dashboard": []})
            ds = bg.setdefault("cac_dashboard", [])
            if nhan not in ds:
                ds.append(nhan)
                ds.sort()
                ghi_so += 1
        tong_ghi_so += ghi_so

        # ② chuỗi rút bài trên nền đề tài — bất đối xứng: dương từ mọi nguồn = nhận
        duong_tinh, chua_kiem = [], []
        if chain is not None:
            try:
                kq = chain.check(sorted(pmids)) or {}
            except Exception:  # noqa: BLE001
                kq = {}
            for pm in sorted(pmids):
                tt = (kq.get(pm) or {}).get("status", "")
                if tt in ("retracted", "expression_of_concern"):
                    duong_tinh.append((pm, tt,
                                       bool((kq.get(pm) or {}).get("retract_and_replace"))))
                elif tt != "ok":
                    chua_kiem.append(pm)
        else:
            chua_kiem = sorted(pmids)

        print(f"  {ten}: {len(pmids)} PMID nền · +{ghi_so} liên kết mới vào sổ canh"
              f" · dương tính {len(duong_tinh)} · chưa kiểm {len(chua_kiem)}")
        if duong_tinh:
            f_cb = sdir / f"CANH-BAO-CHUNG-CU_{hom_nay}.md"
            dong = [f"# ⚠️ CẢNH BÁO CHỨNG CỨ NỀN — {ten} — {hom_nay}", "",
                    "Chuỗi rút bài 3 tầng phát hiện tín hiệu DƯƠNG trong nền y văn "
                    "của đề tài. Máy KHÔNG sửa artifact — bác sĩ đối chiếu từng mục:", ""]
            for pm, tt, thay in duong_tinh:
                loai = ("RÚT & ĐĂNG LẠI BẢN SỬA — đối chiếu số liệu với BẢN ĐÃ SỬA"
                        if thay else
                        ("ĐÃ BỊ RÚT — không dùng kết luận" if tt == "retracted"
                         else "EXPRESSION OF CONCERN — đọc lại trước khi dựa"))
                dong.append(f"- PMID {pm}: **{loai}**")
            dong += ["", "> Sinh bởi cau_noi_nghien_cuu_lam_sang.py — chạy lại để "
                     "cập nhật. Cần bác sĩ kiểm chứng."]
            f_cb.write_text("\n".join(dong) + "\n", encoding="utf-8")
            print(f"    → đã ghi {f_cb.name}")

    if tong_ghi_so:
        so_mod.ghi_so(so)
        print(f"Đã ghi sổ xác minh: +{tong_ghi_so} liên kết NC:<đề tài> — các nhịp "
              "quét định kỳ của hệ lâm sàng từ nay canh hộ nền đề tài.")
    else:
        print("Sổ canh đã có đủ liên kết — không ghi gì thêm.")
    print("Cần bác sĩ kiểm chứng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
