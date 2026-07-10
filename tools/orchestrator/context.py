"""context.py — QUẢN LÝ NGỮ CẢNH: Session + checkpoint + resume.

Giữ trạng thái một request qua các bước (điều gì đã chạy, kết quả agent, cổng đã tới),
lưu bền ra `~/.ebm-orchestrator/sessions/<id>.json` (NGOÀI OneDrive, tránh churn). Cho phép
RESUME đúng chỗ giữa phiên — đối xứng schema `_SO-TRANG-THAI-CHECKPOINT.md`.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path

SESSIONS_DIR = Path.home() / ".ebm-orchestrator" / "sessions"


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


@dataclass
class Checkpoint:
    stage: str
    gate: str | None
    summary: str
    at: str = field(default_factory=_now)
    data: dict = field(default_factory=dict)


@dataclass
class Session:
    request: str
    session_id: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6])
    intent: dict = field(default_factory=dict)
    kind: str = ""
    entry_agent: str = ""
    status: str = "received"
    trace: list[dict] = field(default_factory=list)       # mỗi bước/agent đã (dry-)chạy
    checkpoints: list[dict] = field(default_factory=list)
    gates_pending: list[str] = field(default_factory=list)  # cổng đang chờ bác sĩ
    guardrail: dict = field(default_factory=dict)
    exit_code: int = 0
    retries: int = 0
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    def record(self, entry: dict) -> None:
        self.trace.append(entry)
        self.updated_at = _now()

    def checkpoint(self, stage: str, gate: str | None, summary: str, data: dict | None = None) -> None:
        self.checkpoints.append(asdict(Checkpoint(stage=stage, gate=gate, summary=summary, data=data or {})))
        self.updated_at = _now()

    def as_dict(self) -> dict:
        return asdict(self)


class ContextStore:
    """Lưu/khôi phục Session. Idempotent, append-only cho checkpoint (không xóa lịch sử)."""

    def __init__(self, root: Path = SESSIONS_DIR) -> None:
        self.root = root

    def _path(self, session_id: str) -> Path:
        return self.root / f"{session_id}.json"

    def save(self, session: Session) -> Path:
        self.root.mkdir(parents=True, exist_ok=True)
        p = self._path(session.session_id)
        p.write_text(json.dumps(session.as_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return p

    def load(self, session_id: str) -> Session | None:
        p = self._path(session_id)
        if not p.exists():
            return None
        data = json.loads(p.read_text(encoding="utf-8"))
        return Session(**data)

    def latest(self) -> Session | None:
        if not self.root.exists():
            return None
        files = sorted(self.root.glob("*.json"))
        return self.load(files[-1].stem) if files else None

    def list_ids(self) -> list[str]:
        if not self.root.exists():
            return []
        return sorted(p.stem for p in self.root.glob("*.json"))
