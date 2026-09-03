"""flows.py — Định nghĩa LUỒNG điều phối (grounded vào 2 nhạc trưởng).

CLINICAL_FLOW: 5 bước EBM (BƯỚC 0 cờ đỏ → nhánh chuyên biệt → Hỏi → Tìm → Thẩm định →
Áp dụng[Cổng A] → Theo dõi[Cổng B] → Khép vòng), có nhánh chẩn đoán + nhánh chuyên biệt.
RESEARCH_FLOW: G0→G10 với 6 cổng cứng (G2 đạo đức · G4 khóa SAP · G5 khóa dữ liệu ·
G8 bình duyệt độc lập · G9 liêm chính tác giả · G10 PI khóa gói phát hành).

Mỗi AGENT trong một bước mang `condition` RIÊNG (không phải cả bước) — vd bước "Theo dõi"
có `loi-dan-tuan-thu` LUÔN chạy, nhưng `theo-doi-benh-man` CHỈ khi tín hiệu 'chronic'.
Điều kiện tra ở `signals.py`; agent không điều kiện (condition=None) LUÔN chạy.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StepAgent:
    name: str
    condition: str | None = None  # None = luôn chạy; khác None = tên tín hiệu cần True (signals.py)


def sa(name: str, condition: str | None = None) -> StepAgent:
    return StepAgent(name, condition)


@dataclass(frozen=True)
class FlowStep:
    step_id: str
    title: str
    agents: tuple[StepAgent, ...]
    gate: str | None = None          # None | 'A' | 'B' | 'G2' | 'G4' | 'G5' | 'G8' | 'G9' | 'G10'
    note: str = ""

    @property
    def has_conditional(self) -> bool:
        return any(a.condition for a in self.agents)


# GUARDRAIL cuối — cả hai luồng đều gọi trước khi trả bác sĩ
GUARDRAIL_STEP = FlowStep("guardrail", "Chốt kiểm đầu ra 2 lớp",
                          (sa("tham-dinh-dau-ra"),),
                          note="R1–R14 + Q1–Q7; còn lỗi đỏ → TRẢ-VỀ-SỬA")

CLINICAL_FLOW: tuple[FlowStep, ...] = (
    FlowStep("0", "🚑 Cờ đỏ (bước 0)", (sa("sang-loc-co-do"),),
             note="quét dấu hiệu nguy hiểm + câu hỏi an toàn bắt buộc TRƯỚC TIÊN"),
    FlowStep("0b", "Nhánh chuyên biệt (nếu có)",
             (sa("dau-man-tinh", "pain_chronic_branch"),
              sa("cham-soc-giam-nhe", "palliative_branch"),
              sa("tram-cam-lo-au", "mental_branch")),
             note="chạy SAU bước 0 cờ đỏ, theo loại ca; đổi/giảm thuốc vẫn qua ke-don-an-toan"),
    FlowStep("1", "Hỏi–Khám", (sa("khai-thac-benh-su-kham"), sa("pico-lam-sang"))),
    FlowStep("2", "Tìm", (sa("tra-cuu-chung-cu"),)),
    FlowStep("2b", "Đọc cận lâm sàng", (sa("dien-giai-can-lam-sang", "has_labs"),),
             note="nếu ca có panel XN/ECG — giá trị nguy kịch nêu NGAY"),
    FlowStep("3", "Thẩm định", (sa("tham-dinh-grade-nnt"), sa("huong-dan-lam-sang"))),
    FlowStep("3dx", "Thẩm định — nhánh CHẨN ĐOÁN",
             (sa("chan-doan-xac-suat", "is_diagnostic"),
              sa("tham-dinh-do-chinh-xac-chan-doan", "is_diagnostic"),
              sa("thang-diem-nguy-co", "needs_risk_score")),
             note="nếu câu hỏi chẩn đoán: Bayes + QUADAS-3 hiện hành + GRADE-cho-test; thang nguy cơ nếu cần"),
    FlowStep("4", "Áp dụng", (sa("ke-don-an-toan"),
                              sa("quan-ly-khang-dong", "anticoag"),
                              sa("quyet-dinh-chung")),
             gate="A", note="⛔ Cổng A — chỉ ĐỀ XUẤT; bác sĩ duyệt mới 'áp dụng'"),
    FlowStep("5", "Theo dõi", (sa("loi-dan-tuan-thu"),
                               sa("theo-doi-benh-man", "chronic"),
                               sa("du-phong-tam-soat", "prevention")),
             gate="B", note="⛔ Cổng B — ghi EBM_MASTER hàng chờ duyệt"),
    FlowStep("6", "Khép vòng", (sa("ket-qua-hoc-tap"), sa("cap-nhat-guideline")),
             note="tín hiệu học tập = GIẢ THUYẾT, không tự đổi thực hành"),
)

# Agent xuyên suốt lâm sàng (là nhạc trưởng — validate() cần biết agent này tồn tại thật)
CLINICAL_CROSSCUT: tuple[str, ...] = ("dieu-phoi-lam-sang",)

RESEARCH_FLOW: tuple[FlowStep, ...] = (
    FlowStep("G0", "Câu hỏi & khoảng trống",
             (sa("cau-hoi-nghien-cuu"), sa("khoang-trong-nghien-cuu"), sa("thu-thu-tai-lieu"))),
    FlowStep("G1", "Thiết kế & kế hoạch",
             (sa("thiet-ke-nghien-cuu"), sa("ke-hoach-trien-khai"), sa("bien-so-nghien-cuu"),
              sa("cong-cu-do-luong", "prom_tool"),
              sa("mo-hinh-tien-luong", "prognostic_model"),
              sa("kinh-te-y-te", "economic"),
              sa("nghien-cuu-dinh-tinh", "qualitative")),
             note="4 agent cuối CHỈ khi đề tài có cấu phần tương ứng (PROM/mô hình/kinh tế/định tính)"),
    FlowStep("G2", "Đạo đức & đăng ký", (sa("dao-duc-dang-ky"),),
             gate="G2", note="⛔ CỔNG CỨNG — không phân tích dữ liệu thật khi chưa phê duyệt + đăng ký "
                             "(sau khi bác sĩ duyệt → so-cai-ghi-nho ghi checkpoint)"),
    FlowStep("G3", "Cỡ mẫu / power", (sa("co-mau-nghien-cuu"),)),
    FlowStep("G4", "Khóa SAP", (sa("thiet-ke-nghien-cuu"),),
             gate="G4", note="⛔ CỔNG CỨNG — khóa kế hoạch phân tích TRƯỚC khi xem dữ liệu "
                             "(sau khi bác sĩ ký khóa → so-cai-ghi-nho ghi G4_STATUS=LOCKED)"),
    FlowStep("G5", "Dữ liệu & an toàn", (sa("quan-ly-du-lieu"), sa("an-toan-nghien-cuu")),
             gate="G5", note="⛔ CỔNG CỨNG — chỉ phân tích trên dataset đã khóa; quản lý dữ liệu "
                              "hoặc PI ký data-lock thật"),
    FlowStep("G6", "Phân tích", (sa("phan-tich-thong-ke"), sa("meta-phan-tich"), sa("dien-giai-ket-qua"))),
    FlowStep("G7", "Viết & trích dẫn 🔒",
             (sa("viet-ban-thao"), sa("hieu-dinh-song-ngu", "international_journal"), sa("kiem-chung-trich-dan")),
             note="hieu-dinh-song-ngu CHỈ khi nộp tạp chí quốc tế"),
    FlowStep("G8", "Bình duyệt", (sa("binh-duyet"),),
             gate="G8", note="⛔ CỔNG CỨNG — bình duyệt độc lập (không phải PI/tác giả) trước khi nộp "
                             "(sau khi bác sĩ duyệt → so-cai-ghi-nho ghi checkpoint)"),
    FlowStep("G9", "Nộp bài & liêm chính tác giả", (sa("nop-bai-phan-hoi"),),
             gate="G9", note="⛔ CỔNG CỨNG — COI/đóng góp/khai báo AI do nhà nghiên cứu xác nhận "
                             "(sau khi xác nhận → so-cai-ghi-nho ghi khép đề tài)"),
    FlowStep("G10", "Khóa gói phát hành", (sa("dieu-phoi-nghien-cuu"),),
             gate="G10", note="⛔ CỔNG CỨNG — chạy run_g10_assemble.py + quality gate; "
                               "chỉ PI được khóa manifest phát hành cuối"),
)

# Agent xuyên suốt nghiên cứu (nhạc trưởng + thư ký sổ cái — không phải bước riêng vì
# so-cai-ghi-nho chỉ thực sự ghi SAU KHI bác sĩ duyệt cổng, không phải lúc lập plan)
RESEARCH_CROSSCUT: tuple[str, ...] = ("dieu-phoi-nghien-cuu", "so-cai-ghi-nho")


def flow_for(kind: str) -> tuple[FlowStep, ...]:
    """Trả luồng theo intent kind."""
    if kind == "clinical_case":
        return CLINICAL_FLOW + (GUARDRAIL_STEP,)
    if kind == "research_topic":
        return RESEARCH_FLOW + (GUARDRAIL_STEP,)
    return ()


def all_agents_in_flows() -> set[str]:
    names: set[str] = set()
    for flow in (CLINICAL_FLOW, RESEARCH_FLOW):
        for step in flow:
            names.update(a.name for a in step.agents)
    names.update(CLINICAL_CROSSCUT)
    names.update(RESEARCH_CROSSCUT)
    names.add("tham-dinh-dau-ra")
    return names
