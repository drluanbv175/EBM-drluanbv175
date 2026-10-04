#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TOÀN VĂN THEO CHỦ ĐỀ — bước «TV» của `ops/orchestrator.py` (04/10/2026).

VÌ SAO CÓ. Đo 04/10/2026 khi bác sĩ hỏi «hệ thống đã bảo đảm phủ chứng cứ và đọc toàn văn chưa»:
  • chuỗi máy theo chủ đề (A2 quét → A4 sổ xác minh → B2 cổng → B5 hàng chờ) KHÔNG có bước toàn văn nào — ứng viên mới
    được trình bác sĩ khi máy mới đọc tóm tắt;
  • 27 mục `apply` (20 PMID) không có toàn văn trong kho vẫn qua cổng, vì cổng chỉ chặn khi mục TỰ KHAI 'partial'.
Bước này NỐI BA CÔNG CỤ ĐÃ CÓ, không thêm một dòng logic y khoa:
  1. `gom_toan_van_dashboard.py --pmid … --unpaywall` — PMC Open Access + bản mang GIẤY PHÉP MỞ (cổng điều khoản BH160);
  2. `doc_sau_toan_van.py --pmid …`                    — hồ sơ đọc sâu cho bài vừa có toàn văn;
  3. `doc_toan_van_co_nguoi.py --pmid …`               — phiếu LÀN TRÌNH DUYỆT CÓ BÁC SĨ cho bài còn thiếu (theo miền + điều
     khoản NXB: phiên uỷ quyền / bác sĩ đọc trực tiếp / đọc điều khoản trước).
PMID lấy từ: ứng viên của JSON bước A2 (bỏ mục `rut_bai` = retracted) + mục `apply` CHƯA có toàn văn trong các dashboard
của chủ đề (`--dashboard`).

GIỚI HẠN CÓ CHỦ Ý. Máy chỉ lấy được bản HỢP LỆ tự động (OA/giấy phép mở); bài tường phí hoặc bị trang NXB chặn máy vẫn cần
bác sĩ (làn trình duyệt) hay quyền truy cập — bước này nói rõ bài nào, KHÔNG lách. Phụ trợ: lỗi một công cụ không chặn
chuỗi (mã 0, ghi vào báo cáo); mã 2 khi đầu vào hỏng (JSON A2 không đọc được). Không có PMID nào ⇒ mã 0, báo cáo nói rõ.

Dùng:  python3 tools/toan_van_theo_chu_de.py --a2-json logs/<run>.A2-<slug>.json [--dashboard <db.html> …] \\
           --bao-cao logs/<run>.TV-<slug>.md
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
DASH = REPO / "EBM-Dashboards"
KHO = DASH / "toan_van_oa"
TRAN_PMID = 60          # một lượt theo chủ đề: tối đa 60 PMID (ứng viên ≤ 6/tầng + mục apply thiếu) — tránh tải dồn
TIMEOUT_CONG_CU = 900   # giây cho mỗi công cụ


def _nap_gom():
    sp = importlib.util.spec_from_file_location("_gom_tv_cd", REPO / "tools" / "gom_toan_van_dashboard.py")
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def pmid_tu_a2(duong: Path) -> list[str]:
    """PMID ứng viên của JSON bước A2, giữ thứ tự, bỏ trùng; bỏ mục đã bị rút (`rut_bai` = retracted). Lỗi đọc ⇒ ValueError."""
    try:
        d = json.loads(Path(duong).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise ValueError(f"không đọc được JSON A2 {duong}: {e}") from e
    ds: list[str] = []
    for t in d.get("topics") or []:
        for c in t.get("candidates") or []:
            pm = str(c.get("pmid") or "").strip()
            if re.fullmatch(r"\d{6,9}", pm) and c.get("rut_bai") != "retracted" and pm not in ds:
                ds.append(pm)
    return ds


def co_toan_van(pmid: str, kho: Path, gom=None) -> bool:
    """PMID có toàn văn THẬT trong kho (mọi loại tệp ở gốc kho, trừ `_UPW.html` là trang giới thiệu kho lưu trữ) hoặc đã đọc
    qua làn trình duyệt (`trinh_duyet/`)."""
    for q in kho.glob(f"PMID-{pmid}_*"):
        if not q.is_file():
            continue
        if q.name.endswith("_UPW.html") and gom is not None:
            if not gom.la_toan_van_html(gom._van_ban_tho(q.read_bytes()))[0]:
                continue
        return True
    return any((kho / "trinh_duyet").glob(f"PMID-{pmid}*"))


def pmid_apply_thieu(dashboards: list[Path], kho: Path, gom=None) -> list[str]:
    """PMID chính (`pmid:`) của mục decision='apply' CHƯA có toàn văn trong kho (bỏ mục tự khai appraisalCompleteness)."""
    sp = importlib.util.spec_from_file_location("_vd_tv_cd", REPO / "sync/skills/cap-nhat-chung-cu-y-khoa/tools/verify_dashboard.py")
    vd = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(vd)
    ds: list[str] = []
    for db in dashboards:
        blk = vd.extract_data_block(Path(db).read_text(encoding="utf-8", errors="replace"))
        if not blk:
            continue
        for ch in vd.split_items(blk):
            if vd.field(ch, "decision") != "apply" or vd.field(ch, "appraisalCompleteness") in ("full", "partial"):
                continue
            pm = (vd.field(ch, "pmid") or "").strip()
            if re.fullmatch(r"\d{6,9}", pm) and not co_toan_van(pm, kho, gom) and pm not in ds:
                ds.append(pm)
    return ds


def _chay(lenh: list[str]) -> tuple[int, str]:
    try:
        r = subprocess.run(lenh, capture_output=True, text=True, timeout=TIMEOUT_CONG_CU, cwd=str(REPO))
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return -9, f"QUÁ {TIMEOUT_CONG_CU} giây — bỏ bước này, lượt sau chạy lại"
    except OSError as e:
        return -1, f"không chạy được: {e}"


def main(argv: list[str] | None = None, *, chay=_chay, kho: Path | None = None) -> int:
    ap = argparse.ArgumentParser(description="Toàn văn cho ứng viên và mục apply của MỘT chủ đề (bước TV của orchestrator)")
    ap.add_argument("--a2-json", type=Path, help="JSON của bước A2 (logs/<run>.A2-<slug>.json)")
    ap.add_argument("--dashboard", nargs="*", default=[], type=Path, help="dashboard của chủ đề — lấy mục apply thiếu toàn văn")
    ap.add_argument("--bao-cao", type=Path, required=True, help="tệp Markdown báo cáo")
    a = ap.parse_args(argv)
    kho = kho or KHO
    try:
        gom = _nap_gom()
    except Exception:  # noqa: BLE001 — thiếu bộ gom thì vẫn liệt kê được, chỉ không lọc trang giới thiệu
        gom = None
    ung_vien: list[str] = []
    if a.a2_json:
        if not a.a2_json.exists():
            ung_vien = []
        else:
            try:
                ung_vien = pmid_tu_a2(a.a2_json)
            except ValueError as e:
                print(f"✗ {e}")
                return 2
    apply_thieu = pmid_apply_thieu([d for d in a.dashboard if d.exists()], kho, gom)
    tat_ca = list(dict.fromkeys(ung_vien + apply_thieu))
    bo_tran = tat_ca[TRAN_PMID:]
    tat_ca = tat_ca[:TRAN_PMID]
    truoc = {pm for pm in tat_ca if co_toan_van(pm, kho, gom)}
    dong = [f"# TOÀN VĂN THEO CHỦ ĐỀ — {datetime.now().isoformat(timespec='seconds')}", "",
            f"- Ứng viên A2: {len(ung_vien)} PMID · mục apply chưa có toàn văn: {len(apply_thieu)} PMID",
            f"- Xử lý lượt này: {len(tat_ca)} PMID (trần {TRAN_PMID}" + (f"; DỜI sang lượt sau: {', '.join(bo_tran)}" if bo_tran else "")
            + f") · đã có toàn văn từ trước: {len(truoc)}", ""]
    if not tat_ca:
        dong.append("Không có PMID nào cần lấy toàn văn lượt này.")
    else:
        py = sys.executable
        buoc = [
            ("① Gom bản hợp lệ (PMC OA + giấy phép mở)",
             [py, str(REPO / "tools/gom_toan_van_dashboard.py"), "--pmid", *tat_ca, "--unpaywall"]),
            ("② Đọc sâu bài có toàn văn", [py, str(REPO / "tools/doc_sau_toan_van.py"), "--pmid", *tat_ca]),
        ]
        for ten, lenh in buoc:
            rc, out = chay(lenh)
            dong += [f"## {ten} — mã {rc}", "```", "\n".join(out.strip().splitlines()[-25:]) or "(không in gì)", "```", ""]
        con_thieu = [pm for pm in tat_ca if not co_toan_van(pm, kho, gom)]
        moi = sorted(set(tat_ca) - truoc - set(con_thieu))
        dong += [f"## Kết quả: +{len(moi)} bài có toàn văn mới · còn thiếu {len(con_thieu)}",
                 "", f"- Mới có toàn văn: {', '.join(moi) or '—'}", f"- Còn thiếu: {', '.join(con_thieu) or '—'}", ""]
        if con_thieu:
            rc, out = chay([py, str(REPO / "tools/doc_toan_van_co_nguoi.py"), "--pmid", *con_thieu])
            dong += [f"## ③ Phiếu làn trình duyệt có bác sĩ cho bài còn thiếu — mã {rc}", "```",
                     "\n".join(out.strip().splitlines()[-60:]) or "(không in gì)", "```", "",
                     "> Bài tường phí/bị trang NXB chặn máy: bác sĩ mở theo phiếu (tự qua Cloudflare/đăng nhập), Claude trích",
                     "> xuất có cấu trúc rồi `doc_toan_van_co_nguoi.py --nap`. Bài không có quyền truy cập ⇒ thẩm định từ tóm",
                     "> tắt và khai `appraisalCompleteness:'partial'` (cổng giữ ở mức «Cân nhắc»)."]
    dong += ["", "Máy chỉ ĐO và LẤY bản hợp lệ — không đổi dashboard, không đổi decision. Cần bác sĩ kiểm chứng."]
    a.bao_cao.parent.mkdir(parents=True, exist_ok=True)
    a.bao_cao.write_text("\n".join(dong) + "\n", encoding="utf-8")
    print("\n".join(dong[:4]))
    print(f"→ {a.bao_cao}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
