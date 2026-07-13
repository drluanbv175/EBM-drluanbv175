#!/usr/bin/env python3
"""Kiểm `EBM_MASTER/tools/sync_all.py` idempotent.

Sau khi hub đã đồng bộ, chạy lại `sync_all.py` KHÔNG được làm tăng/giảm số thẻ
trong `EBM_MASTER.json`. Cổng này bắt lỗi đã gặp thật: ingest dashboard cùng
DOI/PMID nhưng nhiều khuyến cáo khác nhau bị so sai với chỉ một thẻ cũ, khiến
mỗi lần chạy sync lại nhân bản sổ cái.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "EBM_MASTER"
MASTER_JSON = MASTER / "EBM_MASTER.json"
SYNC_ALL = MASTER / "tools" / "sync_all.py"


def evidence_count() -> int:
    data = json.loads(MASTER_JSON.read_text(encoding="utf-8"))
    return len(data.get("evidence_cards", []))


def main() -> int:
    if not MASTER_JSON.exists() or not SYNC_ALL.exists():
        print("FAIL: thiếu EBM_MASTER.json hoặc EBM_MASTER/tools/sync_all.py")
        return 1

    before = evidence_count()
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONPYCACHEPREFIX", str(Path(tempfile.gettempdir()) / "ebm_pycache"))
    proc = subprocess.run(
        [sys.executable, str(SYNC_ALL)],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    after = evidence_count()
    if proc.returncode != 0:
        print(f"FAIL: sync_all.py exit={proc.returncode}")
        tail = "\n".join((proc.stdout + proc.stderr).splitlines()[-12:])
        if tail:
            print(tail)
        return proc.returncode
    if after != before:
        print(f"FAIL: sync_all không idempotent ({before} -> {after} thẻ)")
        return 1
    print(f"PASS: sync_all idempotent ({after} thẻ, không đổi)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
