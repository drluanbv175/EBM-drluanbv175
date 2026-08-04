#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
chay_pubmed_search_mcp.py — Bọc MCP server pubmed-search để KHOÁ KHÔNG NẰM TRONG GIT.

Vì sao cần lớp bọc này: server chỉ đọc cấu hình từ BIẾN MÔI TRƯỜNG
(`shared/settings.py` khai `env_file=None`, không tự đọc file .env). Nếu ghi thẳng
`NCBI_API_KEY` vào `.mcp.json` thì khoá sẽ bị commit lên GitHub — trái nguyên tắc
"API key CHỈ trong .env, không hardcode, không commit" của dự án.

Lớp bọc đọc khoá từ `~/.ebm-secrets/medical-ebm-automation.env` (NGOÀI OneDrive, ngoài
git) rồi mới khởi động server. File này an toàn để commit vì KHÔNG chứa giá trị nào.

Chạy được nguyên văn trên cả Mac lẫn Windows nhờ gọi qua `uv run` — xem `.mcp.json`.

QUAN TRỌNG: stdout là kênh JSON-RPC của MCP, TUYỆT ĐỐI không in gì ra đó.
Mọi thông báo đi stderr.
"""
from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import sys

# Các khoá lấy từ kho secrets. Thiếu khoá nào thì bỏ qua khoá đó, không chặn:
# NCBI_EMAIL là bắt buộc theo chính sách NCBI, còn API key chỉ để nâng hạn mức
# (3 → 10 lượt/giây), không có vẫn tra cứu được.
KHOA_CAN = ("NCBI_EMAIL", "NCBI_API_KEY", "UNPAYWALL_EMAIL", "CROSSREF_EMAIL", "CORE_API_KEY")

KHO_SECRETS = pathlib.Path.home() / ".ebm-secrets" / "medical-ebm-automation.env"


def nap_secrets(env: dict[str, str]) -> list[str]:
    """Đọc kho secrets, đặt vào env. Trả về TÊN các khoá đã nạp (không bao giờ trả giá trị)."""
    da_nap: list[str] = []
    if not KHO_SECRETS.exists():
        print(f"[pubmed-search] không thấy kho secrets: {KHO_SECRETS}", file=sys.stderr)
        return da_nap
    for dong in KHO_SECRETS.read_text("utf-8", errors="replace").splitlines():
        dong = dong.strip()
        if not dong or dong.startswith("#") or "=" not in dong:
            continue
        ten, _, gia_tri = dong.partition("=")
        ten = ten.strip()
        gia_tri = gia_tri.strip().strip('"').strip("'")
        # Biến sẵn có trong môi trường được ưu tiên — cho phép ghi đè khi cần thử nghiệm
        if ten in KHOA_CAN and gia_tri and not env.get(ten):
            env[ten] = gia_tri
            da_nap.append(ten)
    return da_nap


def main() -> int:
    env = os.environ.copy()
    da_nap = nap_secrets(env)
    print(f"[pubmed-search] nạp từ secrets: {', '.join(da_nap) or '(không có khoá nào)'}",
          file=sys.stderr)
    if not env.get("NCBI_EMAIL"):
        print("[pubmed-search] CẢNH BÁO: thiếu NCBI_EMAIL — NCBI yêu cầu email trong mọi "
              "lời gọi, nhánh PubMed có thể bị từ chối.", file=sys.stderr)
    if not env.get("NCBI_API_KEY"):
        print("[pubmed-search] chưa có NCBI_API_KEY → hạn mức 3 lượt/giây thay vì 10. "
              "Đặt bằng: python3 tools/mcp/dat_ncbi_api_key.py", file=sys.stderr)

    # Ưu tiên bản đã cài trong venv riêng (khởi động nhanh, không phụ thuộc mạng);
    # không có thì rơi về uvx (máy mới chưa cài vẫn chạy được).
    venv_exe = pathlib.Path.home() / ".pubmed-mcp-venv" / "bin" / "pubmed-search-mcp"
    venv_exe_win = pathlib.Path.home() / ".pubmed-mcp-venv" / "Scripts" / "pubmed-search-mcp.exe"
    if venv_exe.exists():
        lenh = [str(venv_exe)]
    elif venv_exe_win.exists():
        lenh = [str(venv_exe_win)]
    elif shutil.which("uvx"):
        lenh = ["uvx", "pubmed-search-mcp"]
    else:
        print("[pubmed-search] KHÔNG tìm thấy pubmed-search-mcp: chưa cài venv "
              "~/.pubmed-mcp-venv và cũng không có uvx trong PATH.", file=sys.stderr)
        return 1

    print(f"[pubmed-search] khởi động: {lenh[0]}", file=sys.stderr)
    # Thay hẳn tiến trình để stdin/stdout nối thẳng vào server — không chèn lớp đệm nào
    # vào giữa kênh JSON-RPC.
    try:
        os.execvpe(lenh[0], lenh, env)
    except OSError as loi:  # execvpe chỉ trả về khi thất bại
        print(f"[pubmed-search] không chạy được {lenh[0]}: {loi}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
