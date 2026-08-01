"""lifecycle.py — QUẢN LÝ VÒNG ĐỜI REQUEST: máy trạng thái + cổng + guardrail + retry.

Vòng đời: RECEIVED → ROUTED → PLANNED → RUNNING → (GATE_PENDING dừng chờ bác sĩ) →
GUARDRAIL → RELEASED / RETURNED_FOR_FIX (retry ≤3) → LOGGED. Hợp đồng DỪNG 4 mã thoát
(đối xứng block-contract của pipeline nghiên cứu): released=0 · returned=1 · gate_pending=2 ·
blocked=3.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# ── Trạng thái vòng đời ─────────────────────────────────────────────
STAGES = [
    "received", "routed", "planned", "running",
    "gate_pending", "guardrail", "released", "returned_for_fix", "blocked", "logged",
]

# Mã thoát (hợp đồng DỪNG)
EXIT = {"released": 0, "returned_for_fix": 1, "gate_pending": 2, "blocked": 3, "unknown": 4}

# Ý nghĩa cổng
GATES = {
    "A": "Cổng A — Quyết định lâm sàng (chỉ ĐỀ XUẤT; bác sĩ duyệt mới áp dụng)",
    "B": "Cổng B — Ghi EBM_MASTER (thẻ vào hàng chờ duyệt, chưa xác minh)",
    "G2": "Cổng cứng G2 — Đạo đức + đăng ký trước dữ liệu",
    "G4": "Cổng cứng G4 — Khóa SAP trước khi xem dữ liệu",
    "G5": "Cổng cứng G5 — Khóa dữ liệu thật trước phân tích",
    "G8": "Cổng cứng G8 — Bình duyệt độc lập trước nộp",
    "G9": "Cổng cứng G9 — Liêm chính tác giả (COI/AI/đóng góp do PI xác nhận)",
    "G10": "Cổng cứng G10 — PI khóa manifest gói phát hành cuối",
}

MAX_RETRIES = 3


@dataclass
class Lifecycle:
    stage: str = "received"
    history: list[str] = field(default_factory=lambda: ["received"])
    gates_hit: list[str] = field(default_factory=list)
    retries: int = 0
    notes: list[str] = field(default_factory=list)

    def to(self, stage: str, note: str = "") -> None:
        assert stage in STAGES, f"stage lạ: {stage}"
        self.stage = stage
        self.history.append(stage)
        if note:
            self.notes.append(f"[{stage}] {note}")

    def hit_gate(self, gate: str) -> None:
        """Dừng ở cổng — chờ bác sĩ. KHÔNG tự vượt."""
        self.gates_hit.append(gate)
        self.to("gate_pending", f"{GATES.get(gate, gate)} — DỪNG chờ bác sĩ")

    def guardrail_pass(self) -> None:
        self.to("released", "guardrail ĐẠT — sẵn sàng bàn giao (vẫn dừng Cổng A/B)")

    def guardrail_fail(self) -> bool:
        """Trả True nếu còn được retry; False nếu hết lượt → leo thang."""
        self.retries += 1
        if self.retries > MAX_RETRIES:
            self.to("blocked", f"guardrail TRẢ-VỀ-SỬA quá {MAX_RETRIES} vòng — LEO THANG bác sĩ")
            return False
        self.to("returned_for_fix", f"guardrail TRẢ-VỀ-SỬA (vòng {self.retries}/{MAX_RETRIES})")
        return True

    def exit_code(self) -> int:
        return EXIT.get(self.stage, EXIT["unknown"])

    def summary(self) -> dict:
        return {
            "stage": self.stage,
            "history": self.history,
            "gates_hit": self.gates_hit,
            "retries": self.retries,
            "exit_code": self.exit_code(),
            "notes": self.notes,
        }
