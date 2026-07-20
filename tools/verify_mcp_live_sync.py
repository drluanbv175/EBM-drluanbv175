#!/usr/bin/env python3
"""verify_mcp_live_sync.py — kiểm READ-ONLY 2 cơ chế đồng bộ MCP mặc định.

Không tự sửa `git config` hay tự cài LaunchAgent nào (đúng nguyên tắc dự án:
tool không tự đổi cấu hình hệ thống). Chỉ PHÁT HIỆN + báo rõ lệnh khắc phục,
để lỗ hổng "quên kích hoạt trên máy mới" không im lặng trôi qua khi chạy
`upgrade_verify.py` định kỳ.

3 điều kiện coi là "đồng bộ MCP mặc định đã bật" trên máy này:
  1. Repo gốc (Claude AI): git config core.hooksPath == .githooks
     (chặn commit nếu .claude/agents/*.md lệch mirror Codex)
  2. Repo medical-ebm-automation: git config core.hooksPath == .githooks
     (tự restart tunnel-client SAU mỗi commit chạm code server MCP)
  3. LaunchAgent vn.drluan.ebm-mcp-code-watch đã load (macOS launchctl)
     (tự restart tunnel-client NGAY khi file server MCP đổi trên đĩa,
     không cần chờ commit)

Bỏ qua (PASS, không phải lỗi) nếu:
  - Không phải macOS (launchd không tồn tại trên nền tảng khác).
  - Máy này rõ ràng chưa từng cài môi trường dev EBM (không có ~/.ebm-venv)
    — không phải máy đang dùng để sửa hệ thống này.
  - Máy này rõ ràng chưa từng cài tunnel-client — mục 3 không áp dụng, vẫn
    kiểm mục 1+2 (2 hook không phụ thuộc tunnel).
Thêm 2026-07-20 (vòng lặp kiểm tra-hoàn thiện, audit đối kháng xác nhận HIGH):
trước đây mục 3 chỉ kiểm LaunchAgent "đã load" (boolean) — không so khớp nội
dung `~/.ebm-tools/bin/watch-restart-ebm-tunnel` (bản cài cục bộ, KHÔNG tự
cập nhật) với `tools/watch_restart_ebm_tunnel.sh` (nguồn trong repo). Nếu ai
đó sửa script nguồn mà quên chạy lại `install_ebm_mcp_code_watcher.py`, mục 3
báo PASS giả dù bản đang chạy đã lỗi thời. Nay kiểm thêm hash nội dung.
"""
from __future__ import annotations

import hashlib
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIRROR = ROOT / "medical-ebm-automation"
TUNNEL_LABEL = "vn.drluan.ebm-copilot-tunnel"
WATCH_LABEL = "vn.drluan.ebm-mcp-code-watch"
WATCHER_SOURCE = MIRROR / "tools/watch_restart_ebm_tunnel.sh"
WATCHER_INSTALLED = Path.home() / ".ebm-tools/bin/watch-restart-ebm-tunnel"


def _git_hooks_path(repo: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "config", "--get", "core.hooksPath"],
            cwd=str(repo), capture_output=True, text=True, check=False,
        )
    except OSError:
        return None
    value = out.stdout.strip()
    return value or None


def _launchd_job_loaded(label: str) -> bool:
    import os

    try:
        result = subprocess.run(
            ["launchctl", "print", f"gui/{os.getuid()}/{label}"],
            capture_output=True, text=True, check=False,
        )
    except OSError:
        return False
    return result.returncode == 0


def _sha256(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def main() -> int:
    problems: list[str] = []
    notes: list[str] = []

    if platform.system() != "Darwin":
        print(f"N/A — không phải macOS ({platform.system()}), bỏ qua kiểm launchd/hook cục bộ.")
        return 0

    dev_env_present = (Path.home() / ".ebm-venv").is_dir()
    if not dev_env_present:
        print("N/A — máy này chưa có ~/.ebm-venv, có vẻ chưa dùng để phát triển EBM.")
        return 0

    root_hooks = _git_hooks_path(ROOT)
    if root_hooks != ".githooks":
        problems.append(
            f"Repo gốc (Claude AI) core.hooksPath={root_hooks!r} (cần '.githooks'). "
            "Kích hoạt: cd '" + str(ROOT) + "' && git config core.hooksPath .githooks"
        )
    else:
        notes.append("Repo gốc: hook doctrine-sync đã kích hoạt.")

    if MIRROR.is_dir():
        mirror_hooks = _git_hooks_path(MIRROR)
        if mirror_hooks != ".githooks":
            problems.append(
                f"Repo medical-ebm-automation core.hooksPath={mirror_hooks!r} (cần '.githooks'). "
                "Kích hoạt: cd '" + str(MIRROR) + "' && git config core.hooksPath .githooks"
            )
        else:
            notes.append("Repo medical-ebm-automation: hook post-commit restart tunnel đã kích hoạt.")

    tunnel_ever_installed = (Path.home() / ".ebm-tools/bin/tunnel-client").is_file()
    if tunnel_ever_installed:
        if not _launchd_job_loaded(WATCH_LABEL):
            problems.append(
                f"LaunchAgent {WATCH_LABEL} (auto-restart khi file đổi, không cần commit) chưa load. "
                f"Kích hoạt: cd '{MIRROR}' && ~/.ebm-venv/bin/python3 tools/install_ebm_mcp_code_watcher.py"
            )
        else:
            notes.append(f"LaunchAgent {WATCH_LABEL}: đã load, theo dõi file MCP sống.")
            source_hash = _sha256(WATCHER_SOURCE)
            installed_hash = _sha256(WATCHER_INSTALLED)
            if source_hash is None:
                pass  # repo không có file nguồn (bất thường) — không phải lỗi của máy này
            elif installed_hash is None:
                problems.append(
                    f"Không đọc được bản cài {WATCHER_INSTALLED} dù LaunchAgent đã load — "
                    f"cài lại: cd '{MIRROR}' && ~/.ebm-venv/bin/python3 tools/install_ebm_mcp_code_watcher.py"
                )
            elif source_hash != installed_hash:
                problems.append(
                    f"Bản cài {WATCHER_INSTALLED} LỖI THỜI so với nguồn {WATCHER_SOURCE} "
                    "(watch_restart_ebm_tunnel.sh đã sửa nhưng chưa chạy lại installer). "
                    f"Cập nhật: cd '{MIRROR}' && ~/.ebm-venv/bin/python3 tools/install_ebm_mcp_code_watcher.py"
                )
            else:
                notes.append(f"LaunchAgent {WATCH_LABEL}: bản cài khớp hash với nguồn repo.")
        if not _launchd_job_loaded(TUNNEL_LABEL):
            notes.append(
                f"Lưu ý: {TUNNEL_LABEL} (Secure MCP Tunnel) chưa load — nếu chủ ý không dùng tunnel "
                "(chỉ dùng Codex desktop stdio cục bộ) thì bỏ qua, đây không phải lỗi."
            )
    else:
        notes.append(f"Máy này chưa cài tunnel-client — bỏ qua kiểm {WATCH_LABEL} (không bắt buộc).")

    for note in notes:
        print(f"  ok: {note}")

    if problems:
        print("CẢNH BÁO — đồng bộ MCP mặc định CHƯA đầy đủ trên máy này:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    print("Đồng bộ MCP mặc định: đầy đủ trên máy này.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
