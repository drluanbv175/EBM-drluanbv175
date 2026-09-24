#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NẠP NỀN RETRACTION WATCH CHO PHIÊN CLOUD (24/09/2026, audit/15 §6 #9 · §8).

Vì sao có: tầng ① của chuỗi rút bài 3 tầng (`app/sources/retraction_chain.py`) là nền
Retraction Watch NGOẠI TUYẾN — tầng DUY NHẤT bắt được PMID 30267080 (rút-và-thay, cả PubMed lẫn
Europe PMC đều trả «ok»). Tệp nền là dữ liệu sinh lại được nên gitignore ⇒ container Cloud mới
KHÔNG BAO GIỜ có nó, trong khi proxy Cloud chặn cả NCBI lẫn Europe PMC ⇒ trên Cloud cả 3 tầng
cùng câm, mọi trích dẫn thành «chưa kiểm rút bài». Từ 24/09 `tools/tai_retraction_watch.py`
tải được qua gương GitLab chính thức của Crossref (thuộc Trusted, ~7 giây, 72.606 dòng) — mảnh
còn thiếu là KHÔNG AI CHẠY nó khi mở phiên Cloud (BH41: công cụ không ai gọi thì không tồn tại).

Nối vào `tu_sua_chua.py::VIEC_MAY` với `chay_tren_cloud=True` (hook Cloud ⑤b chạy
`--pham-vi-cloud --ap-dung`). Trên máy thật: KHÔNG làm gì (mã 0) — máy thật có tệp bền và
làm mới 30 ngày theo quy trình riêng; công cụ này không được tự tải hộ ở đó.

Mã thoát: 0 = không phải Cloud, hoặc nền đã có · 1 = Cloud mà thiếu nền (--im-khi-on) ·
2 = đã thử tải nhưng thất bại (--ap-dung).
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

GOC = Path(__file__).resolve().parents[1]
_sp = importlib.util.spec_from_file_location("_bst_nrb", Path(__file__).resolve().parent / "ban_sao_tran.py")
_bst = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(_bst)

NGUONG_DONG_TOI_THIEU = 1000  # khớp cổng schema của tai_retraction_watch.py


def la_phien_cloud() -> bool:
    return os.environ.get("CLAUDE_CODE_REMOTE", "").strip().lower() == "true"


def goc_engine() -> Path | None:
    return _bst.duong_goc("medical-ebm-automation", GOC)


def nen_san_sang(mea: Path) -> bool:
    csv = mea / "data" / "retraction_watch" / "retraction_watch.csv"
    try:
        with csv.open("rb") as f:
            return sum(1 for _ in f) > NGUONG_DONG_TOI_THIEU
    except OSError:
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--im-khi-on", action="store_true")
    ap.add_argument("--ap-dung", action="store_true", help="tải nền nếu thiếu (chỉ trên Cloud)")
    a = ap.parse_args()

    if not la_phien_cloud():
        if not a.im_khi_on:
            print("ℹ Không phải phiên Cloud — máy thật tự quản nền Retraction Watch, không làm gì.")
        return 0
    mea = goc_engine()
    if mea is None:
        if not a.im_khi_on:
            print("⚪ Phiên Cloud không có medical-ebm-automation — không có engine để nạp nền.")
        return 0
    if nen_san_sang(mea):
        if not a.im_khi_on:
            print("🟢 Nền Retraction Watch ngoại tuyến đã có trên phiên Cloud.")
        return 0
    if not a.ap_dung:
        print("🟠 Phiên Cloud THIẾU nền Retraction Watch — tầng ① chuỗi rút bài câm. "
              "Chạy: python3 tools/nap_nen_rut_bai_cloud.py --ap-dung")
        return 1
    try:
        r = subprocess.run([sys.executable, str(mea / "tools" / "tai_retraction_watch.py"),
                            "--nguon", "tu-dong"], cwd=str(mea), capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=180)
    except (OSError, subprocess.SubprocessError) as exc:
        print(f"🔴 Không chạy được tai_retraction_watch.py: {exc}")
        return 2
    if r.returncode != 0 or not nen_san_sang(mea):
        duoi = [d for d in (r.stdout or "").splitlines() + (r.stderr or "").splitlines() if d.strip()][-3:]
        print(f"🔴 Tải nền Retraction Watch thất bại (mã {r.returncode}): {duoi}")
        return 2
    print("✓ Đã nạp nền Retraction Watch ngoại tuyến cho phiên Cloud.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
