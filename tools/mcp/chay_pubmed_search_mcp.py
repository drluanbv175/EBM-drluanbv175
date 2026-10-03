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
Từ 30/09/2026 `.mcp.json` KHÔNG gọi tệp này bằng đường dẫn tương đối nữa: đoạn mã `-c` ở đó dò
từ thư mục của phiên ngược lên tới thư mục có CẢ `.mcp.json` LẪN `tools/mcp/chay_pubmed_search_mcp.py`
rồi chạy tệp này (phiên mở dưới repo lồng `medical-ebm-automation/` từng spawn hỏng — chốt BH139).
Đổi tên/dời tệp này thì phải sửa chuỗi đường dẫn trong `.mcp.json` và chốt BH139 cùng lúc.

QUAN TRỌNG: stdout là kênh JSON-RPC của MCP, TUYỆT ĐỐI không in gì ra đó.
Mọi thông báo đi stderr.
"""
from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import sys

# Windows: stdout mặc định cp1252 giết print() tiếng Việt — ép UTF-8 (chốt BH55/R4)
import sys as _sys_r4
for _s_r4 in (_sys_r4.stdout, _sys_r4.stderr):
    try:
        _s_r4.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

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
    return chay_may_chu(lenh, env)


def chay_may_chu(lenh: list[str], env: dict[str, str], *, la_windows: bool | None = None) -> int:
    """Chạy máy chủ MCP với stdin/stdout/stderr nối thẳng vào tiến trình gọi — không chèn lớp đệm nào vào kênh JSON-RPC.

    POSIX: `os.execvpe` thay hẳn tiến trình. WINDOWS: `os.exec*` KHÔNG thay tiến trình — nó tạo một tiến trình mới rồi
    cho tiến trình hiện tại thoát NGAY với mã 0 (đo 01/10/2026: cha `poll()` = 0 sau vài giây trong khi con vẫn chạy),
    và còn không bọc dấu nháy cho đối số có dấu cách. Hệ quả đo được trên máy Windows thật: qua lớp bọc, khởi chạy MCP
    thành công 3/6 lượt (python lớp bọc) và 5/6 lượt (`uv run`), trong khi `uvx pubmed-search-mcp` chạy thẳng 6/6 — máy
    chủ lúc mất stdio, lúc bị kéo theo khi `uv` thấy lớp bọc «đã xong». Nên trên Windows chạy máy chủ như tiến trình CON
    (stdio kế thừa nguyên), chờ nó thoát và trả đúng mã thoát; đường dẫn tệp thực thi phân giải theo PATH của `env` vì
    CreateProcess tìm theo PATH của tiến trình cha."""
    if la_windows is None:
        la_windows = os.name == "nt"
    if la_windows:
        exe = shutil.which(lenh[0], path=env.get("PATH")) or lenh[0]
        try:
            return subprocess.call([exe, *lenh[1:]], env=env)   # stdin/stdout/stderr kế thừa — không chuyển hướng gì
        except OSError as loi:
            print(f"[pubmed-search] không chạy được {lenh[0]}: {loi}", file=sys.stderr)
            return 1
    try:
        os.execvpe(lenh[0], lenh, env)
    except OSError as loi:  # execvpe chỉ trả về khi thất bại
        print(f"[pubmed-search] không chạy được {lenh[0]}: {loi}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
