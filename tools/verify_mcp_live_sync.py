#!/usr/bin/env python3
"""verify_mcp_live_sync.py — kiểm READ-ONLY 2 cơ chế đồng bộ MCP mặc định.

Không tự sửa `git config` hay tự cài LaunchAgent nào (đúng nguyên tắc dự án:
tool không tự đổi cấu hình hệ thống). Chỉ PHÁT HIỆN + báo rõ lệnh khắc phục,
để lỗ hổng "quên kích hoạt trên máy mới" không im lặng trôi qua khi chạy
`upgrade_verify.py` định kỳ.

5 điều kiện coi là "đồng bộ MCP mặc định đã bật" trên máy này:
  1. Repo gốc (Claude AI): git config core.hooksPath == .githooks
  2. Hook repo gốc có hợp đồng fail-closed toàn cục
  3. Repo medical-ebm-automation: git config core.hooksPath == .githooks
  4. Hook repo y khoa gọi lại chốt đồng bộ của repo gốc trước commit
  5. LaunchAgent vn.drluan.ebm-mcp-code-watch đã load (macOS launchctl)
     (tự restart tunnel-client NGAY khi file server MCP đổi trên đĩa,
     không cần chờ commit)

Bỏ qua (PASS, không phải lỗi) nếu:
  - Không phải macOS: chỉ bỏ qua LaunchAgent/launchd; vẫn kiểm 2 Git hook.
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
ROOT_PRE_COMMIT = ROOT / ".githooks" / "pre-commit"
MIRROR_PRE_COMMIT = MIRROR / ".githooks" / "pre-commit"

ROOT_HOOK_MARKERS = (
    "COMPLETION_SYNC_FAIL_CLOSED=1",
    "git diff --name-only -- .claude/agents .Codex/agents .codex/agents",
    "tools/sync_agents_to_codex.py --check",
    "tools/check_claude_codex_sync_health.py",
    "tools/verify_claude_code_repo_alignment.py",
)
MIRROR_HOOK_MARKERS = (
    "COMPLETION_SYNC_FAIL_CLOSED=1",
    'ROOT_HOOK="$WORKSPACE_ROOT/.githooks/pre-commit"',
    '"$ROOT_HOOK"',
    "scripts/regenerate_agent_manifest.py --check",
    "tools/agent_gate_governance.py",
)


def _hook_contract_errors(path: Path, markers: tuple[str, ...]) -> list[str]:
    """Trả các marker còn thiếu trong hook fail-closed."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return [f"missing:{path}"]
    return [marker for marker in markers if marker not in text]


def _git_hooks_path(repo: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "config", "--get", "core.hooksPath"],
            cwd=str(repo), capture_output=True, text=True, check=False,
            encoding="utf-8", errors="replace",
        )
    except OSError:
        return _git_hooks_path_from_local_config(repo)
    value = out.stdout.strip()
    return value or _git_hooks_path_from_local_config(repo)


def _git_config_path(repo: Path) -> Path | None:
    git_path = repo / ".git"
    if git_path.is_dir():
        return git_path / "config"
    if not git_path.is_file():
        return None
    try:
        for raw in git_path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = raw.strip()
            if line.lower().startswith("gitdir:"):
                target = line.split(":", 1)[1].strip()
                git_dir = Path(target)
                if not git_dir.is_absolute():
                    git_dir = (repo / git_dir).resolve()
                return git_dir / "config"
    except OSError:
        return None
    return None


def _git_hooks_path_from_local_config(repo: Path) -> str | None:
    """Read local config directly when Git refuses a repo due dubious ownership."""
    config_path = _git_config_path(repo)
    if config_path is None:
        return None
    try:
        lines = config_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    in_core = False
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith(("#", ";")):
            continue
        if line.startswith("[") and line.endswith("]"):
            in_core = line[1:-1].strip().split(" ", 1)[0].lower() == "core"
            continue
        if in_core and "=" in line:
            key, value = line.split("=", 1)
            if key.strip().lower() == "hookspath":
                return value.strip() or None
    return None


def _launchd_job_loaded(label: str) -> bool:
    import os

    try:
        uid = getattr(os, "getuid", lambda: 0)()   # PEP 701 chỉ có từ 3.12; sàn khai là 3.11
        result = subprocess.run(
            ["launchctl", "print", f"gui/{uid}/{label}"],
            capture_output=True, text=True, check=False,
            encoding="utf-8", errors="replace",
        )
    except OSError:
        return False
    return result.returncode == 0


def _sha256(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def ensure_utf8_console() -> None:
    """Keep Windows PowerShell/cp1252 from crashing on Vietnamese sync messages."""
    for stream in (sys.stdout, sys.stderr):
        try:
            encoding = (getattr(stream, "encoding", "") or "").lower()
            if encoding and "utf" not in encoding and hasattr(stream, "reconfigure"):
                stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            continue


def main() -> int:
    ensure_utf8_console()
    problems: list[str] = []
    notes: list[str] = []

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
        missing = _hook_contract_errors(ROOT_PRE_COMMIT, ROOT_HOOK_MARKERS)
        if missing:
            problems.append(
                "Hook repo gốc chưa có hợp đồng completion-sync fail-closed: "
                + ", ".join(missing)
            )
        else:
            notes.append("Repo gốc: pre-commit chặn drift toàn cục và lệch index/worktree.")

    if MIRROR.is_dir():
        mirror_hooks = _git_hooks_path(MIRROR)
        if mirror_hooks != ".githooks":
            problems.append(
                f"Repo medical-ebm-automation core.hooksPath={mirror_hooks!r} (cần '.githooks'). "
                "Kích hoạt: cd '" + str(MIRROR) + "' && git config core.hooksPath .githooks"
            )
        else:
            notes.append("Repo medical-ebm-automation: hooksPath đã kích hoạt.")
            missing = _hook_contract_errors(MIRROR_PRE_COMMIT, MIRROR_HOOK_MARKERS)
            if missing:
                problems.append(
                    "Hook repo y khoa chưa gọi chốt đồng bộ workspace trước commit: "
                    + ", ".join(missing)
                )
            else:
                notes.append("Repo y khoa: pre-commit bắt buộc Claude Code ↔ Codex cùng đạt.")

    system_name = platform.system()
    if system_name != "Darwin":
        notes.append(f"{system_name}: launchd watcher không áp dụng; đã kiểm Git hook đồng bộ cục bộ.")
        for note in notes:
            print(f"  ok: {note}")
        if problems:
            print("CẢNH BÁO — đồng bộ MCP mặc định CHƯA đầy đủ trên máy này:", file=sys.stderr)
            for problem in problems:
                print(f"  - {problem}", file=sys.stderr)
            return 1
        print("Đồng bộ MCP mặc định: Git hooks đầy đủ; launchd watcher N/A trên máy này.")
        return 0

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
