#!/usr/bin/env python3
"""upgrade_verify.py — MỘT LỆNH kiểm tra + đồng bộ toàn hệ Agent EBM.

Chạy trọn dây chuyền liêm chính theo đúng thứ tự (thay cho việc gõ 6 lệnh tay):
  1. enforce_agent_guardrails.py   — chèn/chuẩn hóa khối guardrail bắt buộc + disclaimer
  2. sync_agents_to_codex.py       — sinh lại bản Codex (.toml) từ nguồn .claude/agents
  3. sync_agents_to_codex.py --check — xác nhận nguồn Claude ↔ Codex khớp
  4. verify_agent_routing.py       — không agent mồ côi / không tham chiếu treo
  5. assess_agent_system.py        — tự đánh giá 13 tiêu chí (A1–A7, S1–S6)
  6. audit_ebm_system.py           — audit tổng thể (guardrail/dashboard/repo/EBM_MASTER)

Dùng:
  python tools/upgrade_verify.py           # chạy đủ, IN bảng tóm tắt + PASS/FAIL
  python tools/upgrade_verify.py --no-sync # chỉ KIỂM (không sinh lại Codex) — an toàn để rà nhanh

Mã thoát: 0 nếu MỌI bước PASS; 1 nếu có bước FAIL. Idempotent — chạy lại nhiều lần vô hại.
"Cần bác sĩ kiểm chứng." — công cụ chỉ kiểm cấu trúc/liêm chính, không thay thẩm định lâm sàng.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
VENV_PY = (
    Path.home() / ".ebm-venv" / "Scripts" / "python.exe"
    if os.name == "nt"
    else Path.home() / ".ebm-venv" / "bin" / "python"
)
PY = str(VENV_PY) if VENV_PY.exists() else sys.executable


def run(label: str, args: list[str], pass_when_returncode_zero: bool = True) -> tuple[bool, str]:
    """Chạy một bước; trả (đạt?, dòng tóm tắt cuối). KHÔNG bịa kết quả — dựa returncode thật."""
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    try:
        proc = subprocess.run(
            [PY, *args], cwd=str(ROOT), env=env,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
    except Exception as exc:  # noqa: BLE001 — báo lỗi hạ tầng rõ, không nuốt
        return False, f"KHÔNG CHẠY ĐƯỢC ({exc})"
    ok = (proc.returncode == 0) if pass_when_returncode_zero else True
    # Lấy dòng cuối có nội dung làm tóm tắt
    lines = [ln.rstrip() for ln in (proc.stdout or "").splitlines() if ln.strip()]
    tail = lines[-1] if lines else (proc.stderr.strip().splitlines() or [""])[-1]
    return ok, tail[:120]


def main() -> int:
    do_sync = "--no-sync" not in sys.argv
    print("=" * 70)
    print("  NÂNG CẤP & KIỂM TRA TOÀN HỆ AGENT EBM  (upgrade_verify)")
    print(f"  Python: {PY}")
    print("=" * 70)

    steps: list[tuple[str, list[str], bool]] = []
    if do_sync:
        steps += [
            ("1. Guardrail (enforce)", ["tools/enforce_agent_guardrails.py"], True),
            ("2. Đồng bộ Codex (sync)", ["tools/sync_agents_to_codex.py"], True),
        ]
    steps += [
        ("3. Kiểm đồng bộ (--check)", ["tools/sync_agents_to_codex.py", "--check"], True),
        ("4. Định tuyến (routing)", ["tools/verify_agent_routing.py"], True),
        ("5. Tự đánh giá 13 tiêu chí", ["tools/assess_agent_system.py"], True),
        ("6. Audit tổng thể", ["tools/audit_ebm_system.py"], True),
    ]

    results: list[tuple[str, bool, str]] = []
    for label, args, need_zero in steps:
        ok, tail = run(label, args, need_zero)
        results.append((label, ok, tail))
        mark = "✅" if ok else "❌"
        print(f"  {mark} {label:<28} {tail}")

    all_ok = all(ok for _, ok, _ in results)
    print("-" * 70)
    if all_ok:
        print("  KẾT: ✅ PASS — toàn hệ nhất quán, đã đồng bộ Claude ↔ Codex.")
    else:
        fails = [lbl for lbl, ok, _ in results if not ok]
        print(f"  KẾT: ❌ FAIL — bước lỗi: {', '.join(fails)}")
    print("  → Cần bác sĩ kiểm chứng (đây là kiểm cấu trúc, không thay thẩm định lâm sàng).")
    print("=" * 70)
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
