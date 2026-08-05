#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Xuất ĐỒNG THỜI bộ ba sản phẩm của một lần cập nhật chứng cứ.

Một lệnh duy nhất, từ file Dashboard đã dựng xong:

    Dashboard (.html)  →  ① Dashboard (đầu vào, kiểm liêm chính)
                          ② Bản đọc (.html)  — trang đọc ngay tại phòng khám
                          ③ Bản Word (.docx) — tài liệu lưu trữ đầy đủ

Cách dùng:
    python3 tools/xuat_goi_cap_nhat.py <dashboard>.html [--online] [--parts parts.json]

    --online   chạy cổng liêm chính có phân giải PMID/DOI thật TRƯỚC khi xuất.
               Chỉ khi cổng PASS thì bản Word mới được truyền cờ --verified —
               nếu không, tool docx tự hạ câu chữ thành "CẦN xác minh" thay vì
               khẳng định sai là đã xác minh.
    --json     in kết quả dạng JSON (đường dẫn 3 file) để tự động hoá.

Vì sao gộp thành một lệnh: ba sản phẩm này phải sinh từ CÙNG một khối DATA và
cùng một thời điểm. Chạy rời rạc thì dễ xảy ra tình trạng bản Word hoặc bản đọc
tụt lại một phiên bản so với dashboard mà không ai nhận ra.

Chạy được trên cả macOS lẫn Windows: gọi trình thông dịch bằng sys.executable
(Windows không có lệnh `python3`) và tự ép UTF-8 cho stdout (Windows mặc định
cp1252 sẽ chết khi in tiếng Việt).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DASH_TOOLS = ROOT / "EBM-Dashboards" / "tools"
BAN_DOC = ROOT / "tools" / "build_ban_doc_chung_cu.py"
VERIFY = DASH_TOOLS / "verify_dashboard.py"
DOCX = DASH_TOOLS / "build_dashboard_docx.py"


def configure_utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def run(cmd: list, cwd: Path | None = None) -> tuple[int, str]:
    """Chạy một tool con, trả về (mã thoát, đầu ra gộp)."""
    proc = subprocess.run(
        [str(c) for c in cmd], cwd=str(cwd) if cwd else None,
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def main() -> int:
    configure_utf8_stdio()
    ap = argparse.ArgumentParser(
        description="Xuất đồng thời Dashboard + Bản đọc + Bản Word cho một lần cập nhật chứng cứ")
    ap.add_argument("dashboard", help="đường dẫn WebDashboard_*.html")
    ap.add_argument("--online", action="store_true",
                    help="chạy cổng liêm chính có phân giải PMID/DOI thật trước khi xuất")
    ap.add_argument("--parts", help="file JSON nhóm 'phần' lớn cho bản Word (tuỳ chọn)")
    ap.add_argument("--json", action="store_true", help="in kết quả dạng JSON")
    a = ap.parse_args()

    dash = Path(a.dashboard).resolve()
    if not dash.exists():
        print(f"✗ Không thấy dashboard: {dash}", file=sys.stderr)
        return 2

    missing = [p.name for p in (BAN_DOC, DOCX) if not p.exists()]
    if missing:
        print(f"✗ Thiếu tool: {', '.join(missing)}", file=sys.stderr)
        print("  Tool trong EBM-Dashboards/tools/ đồng bộ qua OneDrive, không qua git —"
              " đợi OneDrive xanh rồi chạy lại.", file=sys.stderr)
        return 2

    py = sys.executable
    result = {"dashboard": str(dash), "ban_doc": None, "word": None,
              "cong_liem_chinh": "KHÔNG CHẠY", "verified_flag": False}
    rc_final = 0

    # ── ① Cổng liêm chính (tuỳ chọn nhưng nên chạy cho dashboard thật) ──────────
    verified = False
    if a.online:
        if not VERIFY.exists():
            print("✗ Thiếu verify_dashboard.py — bỏ qua cổng liêm chính", file=sys.stderr)
            result["cong_liem_chinh"] = "THIẾU TOOL"
            rc_final = 1
        else:
            print("① Cổng liêm chính (--online)…")
            rc, out = run([py, VERIFY, dash, "--online"], cwd=DASH_TOOLS.parent)
            tail = [ln for ln in out.splitlines() if ln.strip()][-1:] or [""]
            print("   " + tail[0].strip())
            if rc == 0:
                verified = True
                result["cong_liem_chinh"] = "PASS"
            else:
                result["cong_liem_chinh"] = "FAIL"
                rc_final = 1
                print("   ⚠ Cổng KHÔNG đạt — vẫn xuất file nhưng bản Word sẽ KHÔNG"
                      " khẳng định 'đã xác minh'.")
    else:
        print("① Bỏ qua cổng liêm chính (không có --online) —"
              " bản Word sẽ ghi 'CẦN xác minh'.")

    result["verified_flag"] = verified

    # ── ② Bản đọc ─────────────────────────────────────────────────────────────
    print("② Bản đọc…")
    rc, out = run([py, BAN_DOC, dash])
    if rc != 0:
        print(out.strip(), file=sys.stderr)
        return 2
    for line in out.splitlines():
        if line.startswith("✓ Đã ghi"):
            result["ban_doc"] = line.replace("✓ Đã ghi", "").strip()
    print("   " + (result["ban_doc"] or "(không rõ đường dẫn)"))

    # ── ③ Bản Word ────────────────────────────────────────────────────────────
    print("③ Bản Word…")
    cmd = [py, DOCX, dash]
    if verified:
        cmd.append("--verified")
    if a.parts:
        cmd += ["--parts", str(Path(a.parts).resolve())]
    rc, out = run(cmd, cwd=DASH_TOOLS.parent)
    if rc != 0:
        print(out.strip(), file=sys.stderr)
        rc_final = 1
    else:
        for line in out.splitlines():
            if line.startswith("✓ Đã ghi"):
                result["word"] = line.replace("✓ Đã ghi", "").split("—")[0].strip()
        print("   " + (result["word"] or "(không rõ đường dẫn)"))

    print("\n── Bộ ba đã sẵn sàng ──")
    for nhan, key in (("Dashboard", "dashboard"), ("Bản đọc  ", "ban_doc"), ("Bản Word ", "word")):
        print(f"  {nhan}  {result[key] or '(chưa sinh được)'}")
    print(f"  Cổng liêm chính: {result['cong_liem_chinh']}")
    print("\nCần bác sĩ kiểm chứng trước khi áp dụng cho người bệnh cụ thể.")

    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return rc_final


if __name__ == "__main__":
    raise SystemExit(main())
