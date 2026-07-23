"""intent.py — Định tuyến INTENT: request thô → {clinical_case | research_topic | single_task}.

Grounded vào ma trận định tuyến trong README (§'Ma trận định tuyến'). Trả về đích + các luật
khớp để minh bạch. Không phán đoán mù: nếu không khớp → 'unknown' + gợi ý.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Cụm từ báo hiệu một CA lâm sàng trọn vẹn → nhạc trưởng lâm sàng
CLINICAL_CASE_CUES = [
    "bệnh nhân", "tôi có bn", "tôi có một", "ca này", "khám ca", "người bệnh",
    "bn nam", "bn nữ", "nam ~", "nữ ~", "nam,", "nữ,", "cụ ông", "cụ bà",
]
# Cụm từ báo hiệu một ĐỀ TÀI nghiên cứu → nhạc trưởng nghiên cứu
# SỬA 2026-07-22 (vòng lặp kiểm tra-hoàn thiện vòng 10, phát hiện HIGH): whitelist cũ chỉ có
# 8 cụm hẹp — một đề tài diễn đạt TỰ NHIÊN ("Nghiên cứu hồi cứu hiệu quả metformin trên bệnh
# nhân PCOS...", "Khảo sát cắt ngang mức độ tuân thủ...") không khớp cụm nào, rơi xuống nhánh
# CLINICAL_CASE_CUES (do có nhắc quần thể bệnh nhân) → định tuyến SAI thành ca lâm sàng đơn
# lẻ, bỏ qua toàn bộ cổng cứng G2/G4/G8/G9. Thêm cụm ghép "nghiên cứu/khảo sát" + từ khóa
# THIẾT KẾ nghiên cứu cụ thể (hồi cứu/tiến cứu/cắt ngang/so sánh/thuần tập/bệnh chứng/can
# thiệp/quan sát/mô tả) + "tôi muốn nghiên cứu" — CỐ Ý không thêm từ TRẦN "nghiên cứu" một
# mình vì sẽ khớp nhầm câu hỏi tra cứu chứng cứ đơn thuần tại điểm khám (vd "nghiên cứu nào
# ủng hộ dùng SGLT2i cho bệnh nhân này?" — việc lẻ, KHÔNG phải khởi động đề tài mới).
RESEARCH_TOPIC_CUES = [
    "đề tài", "chạy nghiên cứu", "làm nghiên cứu", "đề cương", "protocol",
    "nghiên cứu của tôi", "nghiệm thu", "bản thảo của tôi",
    "tôi muốn nghiên cứu", "muốn làm nghiên cứu", "muốn thực hiện nghiên cứu",
    "nghiên cứu hồi cứu", "nghiên cứu tiến cứu", "nghiên cứu cắt ngang",
    "nghiên cứu so sánh", "nghiên cứu thuần tập", "nghiên cứu bệnh chứng",
    "nghiên cứu can thiệp", "nghiên cứu quan sát", "nghiên cứu mô tả",
    "khảo sát cắt ngang", "khảo sát hồi cứu", "khảo sát mô tả",
    "thử nghiệm lâm sàng", "thử nghiệm ngẫu nhiên",
]

# Luật việc lẻ: (keywords, agent, ghi chú). Thứ tự = độ ưu tiên (đặc thù trước).
SINGLE_TASK_RULES: list[tuple[list[str], str, str]] = [
    (["có nguy hiểm", "chuyển viện", "cấp cứu", "cờ đỏ", "đừng bỏ sót"], "sang-loc-co-do", "sàng lọc cờ đỏ"),
    (["quadas", "test này đáng tin", "se-sp", "độ nhạy độ đặc hiệu", "lr+", "độ chính xác chẩn đoán"], "tham-dinh-do-chinh-xac-chan-doan", "thẩm định độ chính xác test"),
    (["có nên làm xét nghiệm", "khả năng bệnh", "đủ chắc để điều trị", "xét nghiệm gì"], "chan-doan-xac-suat", "Bayes chẩn đoán"),
    (["đọc giúp", "kết quả này", "panel xét nghiệm", "nguy kịch", "đọc ecg"], "dien-giai-can-lam-sang", "đọc cận lâm sàng"),
    (["cần hỏi gì", "khám gì", "khai thác bệnh sử"], "khai-thac-benh-su-kham", "bệnh sử–khám"),
    (["kháng đông nào", "doac", "warfarin", "bắc cầu", "inr", "chuyển vka"], "quan-ly-khang-dong", "quản lý kháng đông"),
    (["tính thang điểm", "cha2ds2", "has-bled", "ascvd", "nguy cơ bao nhiêu", "wells", "curb-65"], "thang-diem-nguy-co", "thang nguy cơ"),
    (["tầm soát", "tiêm vắc", "vắc-xin", "dự phòng theo tuổi", "khám sức khỏe định kỳ"], "du-phong-tam-soat", "dự phòng–tầm soát"),
    (["theo dõi bệnh", "đích điều trị", "bao lâu xét nghiệm", "khi nào tăng liều"], "theo-doi-benh-man", "theo dõi bệnh mạn"),
    (["đau mạn", "đau lưng mạn", "opioid", "giảm đau kéo dài"], "dau-man-tinh", "đau mạn"),
    (["giảm nhẹ", "cuối đời", "mục tiêu chăm sóc"], "cham-soc-giam-nhe", "giảm nhẹ"),
    (["trầm cảm", "lo âu", "phq-9", "gad-7", "sàng lọc tâm thần"], "tram-cam-lo-au", "trầm cảm/lo âu"),
    (["đơn này an toàn", "thuốc đánh nhau", "tương tác thuốc", "chỉnh liều theo thận", "chống chỉ định"], "ke-don-an-toan", "an toàn kê đơn"),
    (["giải thích cho bệnh nhân", "trình bày lựa chọn", "cùng quyết"], "quyet-dinh-chung", "quyết định chung"),
    (["lời dặn", "tuân thủ", "tái khám"], "loi-dan-tuan-thu", "lời dặn A5"),
    (["grade", "nnt", "nnh", "evidence-to-decision"], "tham-dinh-grade-nnt", "GRADE/NNT"),
    (["guideline nói gì", "chứng cứ mới nhất", "hiệu quả không", "có bằng chứng"], "tra-cuu-chung-cu", "tra cứu chứng cứ"),
    # Nghiên cứu — việc lẻ
    (["cỡ mẫu", "bao nhiêu bệnh nhân", "đủ lực", "power"], "co-mau-nghien-cuu", "cỡ mẫu/power"),
    (["câu hỏi nghiên cứu", "pico đề tài", "finer"], "cau-hoi-nghien-cuu", "câu hỏi NC"),
    (["tổng quan hệ thống", "prisma", "systematic review"], "tong-quan-y-van", "tổng quan hệ thống"),
    (["thẩm định bài", "risk of bias", "rob 2", "robins"], "tham-dinh-phe-binh", "thẩm định phê bình"),
    (["tìm tài liệu", "danh mục tham khảo", "soát danh mục", "tltk"], "thu-thu-tai-lieu", "thủ thư y văn"),
    (["kiểm trích dẫn", "trích dẫn ma", "verify pmid", "bibtex"], "kiem-chung-trich-dan", "kiểm trích dẫn"),
    (["chi phí hiệu quả", "chi phí–hiệu quả", "kinh tế y tế", "tác động ngân sách", "icer"], "kinh-te-y-te", "kinh tế y tế"),
    (["mô hình tiên lượng", "tripod", "điểm dự báo", "validate thang điểm"], "mo-hinh-tien-luong", "mô hình tiên lượng"),
    (["cosmin", "kiểm định thang đo", "prom"], "cong-cu-do-luong", "công cụ đo lường"),
    (["định tính", "phỏng vấn", "nhóm tiêu điểm", "coreq"], "nghien-cuu-dinh-tinh", "định tính"),
    (["soi gói", "kiểm liêm chính", "có vượt cổng", "có lẫn pii"], "tham-dinh-dau-ra", "guardrail"),
]

CLINICAL_ORCHESTRATOR = "dieu-phoi-lam-sang"
RESEARCH_ORCHESTRATOR = "dieu-phoi-nghien-cuu"


@dataclass
class IntentResult:
    kind: str  # 'clinical_case' | 'research_topic' | 'single_task' | 'unknown'
    target: str  # agent điểm vào
    reason: str
    matches: list[str] = field(default_factory=list)  # các luật việc-lẻ khớp (minh bạch)

    def as_dict(self) -> dict:
        return {"kind": self.kind, "target": self.target, "reason": self.reason, "matches": self.matches}


def _any(text: str, cues: list[str]) -> list[str]:
    return [c for c in cues if c in text]


def route(request: str) -> IntentResult:
    """Phân loại request. Ưu tiên: ĐỀ TÀI > CA lâm sàng > việc lẻ > unknown (đề tài kiểm trước vì
    'bệnh nhân' cũng xuất hiện khi mô tả quần thể nghiên cứu — xem lý do dưới)."""
    t = (request or "").lower().strip()
    if not t:
        return IntentResult("unknown", "", "request rỗng")

    single_hits = [(agent, note) for kws, agent, note in SINGLE_TASK_RULES if _any(t, kws)]
    match_labels = [f"{a} ({n})" for a, n in single_hits]

    # Cue nghiên cứu ('đề tài/đề cương/protocol') là tín hiệu MẠNH → kiểm TRƯỚC cue lâm sàng
    # ('bệnh nhân' cũng xuất hiện khi mô tả quần thể nghiên cứu, nên không được thắng 'đề tài').
    if _any(t, RESEARCH_TOPIC_CUES):
        return IntentResult("research_topic", RESEARCH_ORCHESTRATOR,
                            "phát hiện một ĐỀ TÀI nghiên cứu → nhạc trưởng nghiên cứu (G0→G9)",
                            match_labels)
    if _any(t, CLINICAL_CASE_CUES):
        return IntentResult("clinical_case", CLINICAL_ORCHESTRATOR,
                            "phát hiện mô tả một CA lâm sàng → nhạc trưởng lâm sàng (5 bước EBM)",
                            match_labels)
    if single_hits:
        agent, note = single_hits[0]
        return IntentResult("single_task", agent, f"khớp việc lẻ: {note}", match_labels)

    return IntentResult("unknown", "",
                        "chưa khớp luật nào — nêu rõ CA (‘tôi có bệnh nhân…’) / ĐỀ TÀI (‘đề tài…’) / hoặc câu hỏi cụ thể",
                        match_labels)
