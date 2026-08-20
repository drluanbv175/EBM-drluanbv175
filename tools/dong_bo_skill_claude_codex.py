#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Đồng bộ skill tự động giữa nguồn OneDrive, Claude Code, Codex và Cowork.

Nguồn duy nhất là ``sync/skills``. Claude Code và Codex dùng liên kết trực tiếp,
nên sửa file hiện có có hiệu lực ngay. Skill mới được nối ở SessionStart hoặc
watcher nền. Runtime Cowork được cập nhật bằng công cụ fail-closed hiện có.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = REPO / "sync/skills"
ROUTER_NAME = "plugin-router-chatgpt"


@dataclass(frozen=True)
class LinkResult:
    """Kết quả của một liên kết skill."""

    runtime: str
    skill: str
    status: str
    detail: str = ""


def skill_sources(source: Path) -> list[Path]:
    """Liệt kê các skill nguồn hợp lệ theo thứ tự ổn định."""

    if not source.is_dir():
        raise RuntimeError(f"Không tìm thấy nguồn skill: {source}")
    return sorted(
        (item for item in source.iterdir() if item.is_dir() and (item / "SKILL.md").is_file()),
        key=lambda item: item.name.casefold(),
    )


def backup_path(destination: Path, name: str) -> Path:
    """Tạo đường dẫn sao lưu nằm ngoài thư mục skill đang được quét."""

    root = destination.parent / f"{destination.name}-backup"
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{name}.bak-{stamp}"


def ensure_link(source: Path, destination: Path, apply: bool) -> LinkResult:
    """Tạo symlink an toàn; thư mục thật được sao lưu trước khi thay."""

    target = destination / source.name
    label = destination.parent.name
    if target.is_symlink():
        try:
            if target.resolve(strict=True) == source.resolve(strict=True):
                return LinkResult(label, source.name, "KHOP")
        except OSError:
            pass
        return LinkResult(label, source.name, "XUNG_DOT", f"symlink đang trỏ nơi khác: {target}")
    if target.exists():
        if not apply:
            return LinkResult(label, source.name, "CAN_NOI", "đang là thư mục/file thật")
        backup = backup_path(destination, source.name)
        shutil.move(str(target), str(backup))
        os.symlink(source, target, target_is_directory=True)
        return LinkResult(label, source.name, "DA_NOI", f"đã sao lưu tại {backup}")
    if not apply:
        return LinkResult(label, source.name, "CAN_NOI", "chưa tồn tại")
    destination.mkdir(parents=True, exist_ok=True)
    os.symlink(source, target, target_is_directory=True)
    return LinkResult(label, source.name, "DA_NOI")


def rebuild_router(source_root: Path, quiet: bool) -> int:
    """Dựng lại catalog từ trạng thái plugin Codex thật."""

    script = source_root / ROUTER_NAME / "scripts/build_catalog.py"
    if not script.is_file():
        print(f"LỖI: thiếu {script}", file=sys.stderr)
        return 1
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=script.parent.parent,
        check=False,
        capture_output=quiet,
        text=True,
        timeout=120,
    )
    if proc.returncode != 0 and quiet:
        print((proc.stderr or proc.stdout or "dựng catalog thất bại").strip(), file=sys.stderr)
    return proc.returncode


def newest_mtime(root: Path) -> float:
    """Lấy mtime mới nhất của nội dung skill, bỏ file tạm Python."""

    values = [
        path.stat().st_mtime
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    ]
    return max(values, default=0.0)


def package_router(source_root: Path) -> bool:
    """Cập nhật ZIP phân phối chỉ khi nguồn router mới hơn gói."""

    source = source_root / ROUTER_NAME
    output = REPO / "CHATGPT_SKILLS/dist/plugin-router-chatgpt.zip"
    if output.exists() and output.stat().st_mtime >= newest_mtime(source):
        return False
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".zip.tmp")
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            arcname = Path(ROUTER_NAME) / path.relative_to(source)
            archive.write(path, arcname.as_posix())
    os.replace(temporary, output)
    return True


def sync_cowork(quiet: bool) -> int:
    """Đẩy bản nguồn sang runtime Cowork bằng luật chống mất nội dung hiện có."""

    command = [
        sys.executable,
        str(REPO / "tools/dong_bo_skill.py"),
        "--ap-dung",
        "--nguon-la-chuan",
    ]
    if quiet:
        command.append("--im-khi-on")
    proc = subprocess.run(command, cwd=REPO, check=False, timeout=300)
    return proc.returncode


def sync_plugins(apply: bool, quiet: bool) -> int:
    """Giữ plugin Codex không cũ hơn registry Claude."""

    command = [sys.executable, str(REPO / "tools/dong_bo_plugin_claude_codex.py")]
    if apply:
        command.append("--ap-dung")
    if quiet:
        command.append("--im-khi-on")
    proc = subprocess.run(command, cwd=REPO, check=False, timeout=1200)
    return proc.returncode


def parse_args() -> argparse.Namespace:
    """Nhận chế độ kiểm hoặc áp dụng và cho phép test bằng thư mục tạm."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ap-dung", action="store_true", help="tạo liên kết và cập nhật runtime")
    parser.add_argument("--dong-bo-plugin", action="store_true", help="kiểm/nâng plugin Claude → Codex")
    parser.add_argument("--im-khi-on", action="store_true", help="im lặng khi hệ thống đã khớp")
    parser.add_argument("--bo-qua-runtime", action="store_true", help="không đẩy sang Cowork runtime")
    parser.add_argument("--bo-qua-dong-goi", action="store_true", help="không dựng catalog/ZIP router")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--claude-skills", type=Path, default=Path.home() / ".claude/skills")
    parser.add_argument("--codex-skills", type=Path, default=Path.home() / ".codex/skills")
    return parser.parse_args()


def main() -> int:
    """Điều phối đồng bộ và trả mã lỗi fail-closed."""

    args = parse_args()
    if os.name == "nt":
        print("Trên Windows hãy chạy sync/link-skills.ps1 để dùng junction.", file=sys.stderr)
        return 1
    try:
        sources = skill_sources(args.source)
        results = [
            ensure_link(source, destination, args.ap_dung)
            for destination in (args.claude_skills, args.codex_skills)
            for source in sources
        ]
    except (OSError, RuntimeError) as exc:
        print(f"LỖI đồng bộ skill: {exc}", file=sys.stderr)
        return 1

    conflicts = [item for item in results if item.status == "XUNG_DOT"]
    pending = [item for item in results if item.status == "CAN_NOI"]
    changed = [item for item in results if item.status == "DA_NOI"]
    if changed and not args.im_khi_on:
        print(f"✓ Đã liên kết {len(changed)} skill vào Claude/Codex")
    for item in conflicts:
        print(f"✗ {item.runtime}/{item.skill}: {item.detail}", file=sys.stderr)

    codes: list[int] = [2 if conflicts else (1 if pending else 0)]
    if args.dong_bo_plugin:
        codes.append(sync_plugins(args.ap_dung, args.im_khi_on))
    if args.ap_dung and not args.bo_qua_dong_goi:
        codes.append(rebuild_router(args.source, args.im_khi_on))
        try:
            packaged = package_router(args.source)
            if packaged and not args.im_khi_on:
                print("✓ Đã cập nhật gói plugin-router-chatgpt.zip")
        except OSError as exc:
            print(f"LỖI đóng gói router: {exc}", file=sys.stderr)
            codes.append(1)
    if args.ap_dung and not args.bo_qua_runtime:
        codes.append(sync_cowork(args.im_khi_on))

    final = 2 if 2 in codes else (1 if any(code != 0 for code in codes) else 0)
    if final == 0 and not args.im_khi_on:
        print(f"✓ Đồng bộ đạt: {len(sources)} skill × 2 runtime; Cowork và plugin đã kiểm")
    elif not args.ap_dung and pending:
        print(f"⚠ Còn {len(pending)} liên kết cần tạo; chạy lại với --ap-dung.")
    return final


if __name__ == "__main__":
    raise SystemExit(main())
