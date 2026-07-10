"""signals.py — TÍN HIỆU NGỮ CẢNH cho các bước/agent NHÁNH (điều kiện áp dụng).

Vá lỗ hổng: trước đây plan CHẠY MÙ mọi nhánh (2b đọc CLS, 3dx chẩn đoán, nhánh chuyên biệt)
bất kể request có đúng bối cảnh không. Module này khớp từ khóa MINH BẠCH (không phải NLU
nặng) để quyết định nhánh nào áp dụng — mọi khớp đều liệt kê được, không phải hộp đen.
Agent thật khi chạy vẫn TỰ xác nhận lại bối cảnh; đây chỉ là control-plane ước lượng để
plan phản ánh đúng ca hơn là liệt kê toàn bộ nhánh có thể.
"""

from __future__ import annotations

from dataclasses import dataclass, field

SIGNAL_CUES: dict[str, list[str]] = {
    "has_labs": ["xét nghiệm", "kết quả xn", "công thức máu", "sinh hóa", "ecg",
                 "điện tâm đồ", "panel", "creatinin", "hba1c", "troponin", "x-quang"],
    "is_diagnostic": ["có nên làm xét nghiệm", "khả năng bệnh", "đủ chắc để điều trị",
                       "chẩn đoán phân biệt", "test này", "độ nhạy", "độ đặc hiệu",
                       "se-sp", "quadas", "xét nghiệm này thay đổi"],
    "needs_risk_score": ["cha2ds2", "has-bled", "ascvd", "score2", "wells", "perc",
                          "curb-65", "frax", "qsofa", "news2", "child-pugh", "meld",
                          "nguy cơ bao nhiêu", "tính thang điểm"],
    "anticoag": ["kháng đông", "doac", "warfarin", "rivaroxaban", "apixaban",
                 "dabigatran", "edoxaban", "bắc cầu", " inr", "inr đích"],
    "chronic": ["đái tháo đường", "đtđ", "tăng huyết áp", " tha ", "copd", "hen",
                "bệnh mạn", "suy tim", "bệnh thận mạn", "ckd", "theo dõi dài hạn"],
    "prevention": ["tầm soát", "dự phòng", "tiêm vắc", "vắc-xin", "khám sức khỏe định kỳ"],
    "pain_chronic_branch": ["đau mạn", "đau lưng mạn", "đau khớp mạn", "opioid",
                            "đau thần kinh mạn", "đau kéo dài"],
    "palliative_branch": ["giảm nhẹ", "cuối đời", "ung thư giai đoạn cuối", "mục tiêu chăm sóc"],
    "mental_branch": ["trầm cảm", "lo âu", "phq-9", "gad-7", "sàng lọc tâm thần"],
    "qualitative": ["phỏng vấn", "định tính", "trải nghiệm bệnh nhân", "nhóm tiêu điểm", "coreq"],
    "prom_tool": ["thang đo", "bộ câu hỏi", "cosmin", "prom", "hài lòng người bệnh"],
    "prognostic_model": ["mô hình tiên lượng", "điểm dự báo", "tripod", "nomogram"],
    "economic": ["chi phí–hiệu quả", "chi phí hiệu quả", "kinh tế y tế", "icer",
                 "tác động ngân sách", "cheers"],
    "international_journal": ["tạp chí quốc tế", "nộp quốc tế", "international journal", "impact factor"],
}


@dataclass
class Signals:
    flags: dict[str, bool] = field(default_factory=dict)
    matches: dict[str, list[str]] = field(default_factory=dict)

    def is_set(self, key: str) -> bool:
        return self.flags.get(key, False)

    def as_dict(self) -> dict:
        return {"flags": self.flags, "matches": self.matches}


def detect(text: str) -> Signals:
    """Khớp từ khóa MINH BẠCH; trả về flags + bằng chứng khớp (không phải hộp đen)."""
    t = f" {(text or '').lower()} "
    flags: dict[str, bool] = {}
    matches: dict[str, list[str]] = {}
    for key, cues in SIGNAL_CUES.items():
        hit = [c for c in cues if c in t]
        flags[key] = bool(hit)
        if hit:
            matches[key] = hit
    return Signals(flags=flags, matches=matches)
