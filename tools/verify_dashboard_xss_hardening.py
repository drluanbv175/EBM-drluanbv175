#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_dashboard_xss_hardening.py — Kiểm HỒI QUY lớp chống XSS của các tool sinh HTML.

Bối cảnh: dự án sinh nhiều file HTML từ dữ liệu có NGUỒN NGOÀI (tiêu đề/abstract PubMed,
khuyến cáo do agent trích, tên file dashboard). Đã có 2 đợt lỗi XSS thật:
  - 2026-07-11: 8 lỗi trong template Evidence Workbench (đã vá).
  - 2026-07-26: tái diễn ở `assemble_dashboard.py::to_js()` và `build_library.py`
    (json.dumps KHÔNG escape "<" → dữ liệu chứa "</script>" phá được khối script;
    thêm `innerHTML` không lọc + `href` không kiểm scheme → chạy được `javascript:`).
    Vòng 2 cùng ngày, red-team ĐỘC LẬP tìm thêm: `escUrl` cũ bỏ sót KÝ TỰ ĐIỀU KHIỂN —
    trình duyệt loại bỏ TAB/LF/CR khi phân tích URL, nên "java<TAB>script:" lọt qua.

Script này chạy OFFLINE, không mạng, không PII. Chạy:
    python3 tools/verify_dashboard_xss_hardening.py

Exit 0 = tất cả bản đều chặn được payload; exit 1 = có bản còn lọt (in rõ bản nào/payload nào).
"""
from __future__ import annotations

import importlib.util
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 4 bản sao ĐANG SỐNG của build_library.py (mẫu "sửa 1 chỗ quên 3 chỗ" dự án từng dính)
BUILD_LIBRARY_COPIES = [
    "EBM-Dashboards/tools/build_library.py",
    "EBM_MASTER/skill_assets/build_library.py",
    "sync/skills/cap-nhat-chung-cu-y-khoa/tools/build_library.py",
    "sync/skills/dark-analyst/tools/build_library.py",
]
ASSEMBLE_DASHBOARD = "EBM-Dashboards/tools/assemble_dashboard.py"

# Payload thoát khối <script>. Trình duyệt kết thúc khối script khi gặp "</script"
# BẤT KỂ nó nằm trong chuỗi JS hợp lệ hay không — đây là quy tắc phân tích HTML.
SCRIPT_BREAKOUT_PAYLOADS = [
    "</script><img src=x onerror=alert(1)>",
    "</ScRiPt ><svg onload=alert(1)>",
    "\\u003c/script\\u003e",              # đã escape sẵn — không được double-decode thành thoát
    "&lt;/script&gt;",                     # mã hóa HTML — không được biến thành thẻ thật
    "abc\u2028def\u2029ghi",              # U+2028/9: JS coi là XUỐNG DÒNG → vỡ chuỗi
    'x"; alert(1); var y="',               # thoát chuỗi bằng nháy kép
]

# URL độc. Ký tự điều khiển XEN GIỮA scheme bị trình duyệt loại bỏ khi phân tích URL
# → phải bỏ chúng TRƯỚC khi dò scheme, nếu không "java<TAB>script:" chạy như javascript:.
BAD_URLS = [
    "javascript:alert(1)",
    "jAvAsCrIpT:alert(1)",
    "  javascript:alert(1)",
    "java\tscript:alert(1)",
    "java\nscript:alert(1)",
    "java\rscript:alert(1)",
    "javascript\n:alert(1)",
    "JaVaScRiPt\t\n\r:alert(1)",
    "\x00javascript:alert(1)",
    "data:text/html,<script>alert(1)</script>",
    "vbscript:msgbox(1)",
]
GOOD_URLS = [
    "WebDashboard_EBM_VanDeCuThe_TimMach_20260609.html",
    "./derivatives/x.html",
    "https://pubmed.ncbi.nlm.nih.gov/12345678/",
    "http://example.org/x?y=1",
]

_CTRL_RE = re.compile(r"[\u0000-\u001F\u007F]")
_SCHEME_RE = re.compile(r"^[a-z][a-z0-9+.-]*:", re.I)
_HTTP_RE = re.compile(r"^https?:", re.I)


def _load(rel: str):
    path = ROOT / rel
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location("m_" + rel.replace("/", "_").replace(".", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.path.pop(0)
    return mod


def _esc_url_reference(u: str) -> str:
    """Mô phỏng ĐÚNG ngữ nghĩa escUrl() trong JS đã vá — máy này không có Node nên
    kiểm bằng bản tham chiếu, ĐỒNG THỜI khẳng định nguồn JS thật có đủ 3 bước
    (bỏ ký tự điều khiển → dò scheme → chỉ cho http/https)."""
    s = _CTRL_RE.sub("", str(u or "")).strip()
    if _SCHEME_RE.search(s):
        return s if _HTTP_RE.search(s) else "#"
    return s


def check_build_library(rel: str) -> list[str]:
    problems: list[str] = []
    mod = _load(rel)
    if mod is None:
        return [f"{rel}: KHÔNG TỒN TẠI"]

    src = (ROOT / rel).read_text(encoding="utf-8")
    # 1) Nguồn JS phải có đủ hàng rào (bắt trường hợp ai đó gỡ mất khi sửa vỏ)
    if "function esc(" not in src or "function escUrl(" not in src:
        problems.append(f"{rel}: thiếu hàm esc()/escUrl() trong JS")
    if "\\u0000-\\u001F" not in src:
        problems.append(f"{rel}: escUrl KHÔNG bỏ ký tự điều khiển trước khi dò scheme "
                        "(java<TAB>script: sẽ lọt)")
    if "${e.question}" in src or 'href="${e.file}"' in src:
        problems.append(f"{rel}: innerHTML còn nội suy THẲNG (chưa bọc esc()/escUrl())")

    # 2) Chạy thật: payload không được phá khối <script>
    for payload in SCRIPT_BREAKOUT_PAYLOADS:
        lib = [{"question": payload, "file": "x.html", "eyebrow": payload,
                "apply": 0, "consider": 0, "notyet": 0, "total": 0,
                "updated": payload, "pmids": [], "dois": [], "skin": payload}]
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "o.html"
            mod.build_html(lib, str(out))
            html = out.read_text(encoding="utf-8")
        if html.count("</script>") != 1:
            problems.append(f"{rel}: payload {payload!r} làm số thẻ </script> = "
                            f"{html.count('</script>')} (phải = 1)")
        region = html.split("const LIB=", 1)[1].split("function esc(", 1)[0]
        if "</script" in region.lower():
            problems.append(f"{rel}: payload {payload!r} thoát ra khỏi khối dữ liệu LIB")
    return problems


def check_assemble_dashboard() -> list[str]:
    problems: list[str] = []
    mod = _load(ASSEMBLE_DASHBOARD)
    if mod is None:
        return [f"{ASSEMBLE_DASHBOARD}: KHÔNG TỒN TẠI"]
    for payload in SCRIPT_BREAKOUT_PAYLOADS:
        out = mod.to_js({"title": payload, "n": 1})
        if "</script" in out.lower():
            problems.append(f"{ASSEMBLE_DASHBOARD}: to_js giữ nguyên '</script' với {payload!r}")
        if "\u2028" in out or "\u2029" in out:
            problems.append(f"{ASSEMBLE_DASHBOARD}: to_js để lọt U+2028/9 thô với {payload!r}")
    return problems


def check_url_filter() -> list[str]:
    problems: list[str] = []
    for u in BAD_URLS:
        if _esc_url_reference(u) != "#":
            problems.append(f"escUrl: URL độc KHÔNG bị chặn: {u!r} → {_esc_url_reference(u)!r}")
    for u in GOOD_URLS:
        if _esc_url_reference(u) == "#":
            problems.append(f"escUrl: chặn NHẦM link hợp lệ: {u!r}")
    return problems


def main() -> int:
    all_problems: list[str] = []
    print("=" * 72)
    print(" KIỂM HỒI QUY CHỐNG XSS — tool sinh HTML dashboard")
    print("=" * 72)

    for rel in BUILD_LIBRARY_COPIES:
        p = check_build_library(rel)
        print(f"  {'✓ PASS' if not p else '✗ FAIL'}  {rel}")
        all_problems += p

    p = check_assemble_dashboard()
    print(f"  {'✓ PASS' if not p else '✗ FAIL'}  {ASSEMBLE_DASHBOARD} (to_js)")
    all_problems += p

    p = check_url_filter()
    print(f"  {'✓ PASS' if not p else '✗ FAIL'}  escUrl — {len(BAD_URLS)} URL độc / "
          f"{len(GOOD_URLS)} link hợp lệ")
    all_problems += p

    print("-" * 72)
    if all_problems:
        print(f"KẾT QUẢ: FAIL — {len(all_problems)} vấn đề")
        for x in all_problems:
            print(f"  ⛔ {x}")
        return 1
    print("KẾT QUẢ: PASS — mọi bản sinh HTML đều chặn được payload thoát <script> và URL độc.")
    print("Lưu ý: đây là kiểm KỸ THUẬT offline; nội dung y khoa vẫn cần bác sĩ kiểm chứng.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
