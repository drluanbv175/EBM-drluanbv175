"""intent.py — Định tuyến INTENT: request thô → {clinical_case | research_topic | single_task | cong_cu}.

Grounded vào ma trận định tuyến trong README (§'Ma trận định tuyến'). Trả về đích + các luật
khớp để minh bạch. Không phán đoán mù: nếu không khớp → 'unknown' + gợi ý.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import NamedTuple

# Cụm từ báo hiệu một CA lâm sàng trọn vẹn → nhạc trưởng lâm sàng
CLINICAL_CASE_CUES = [
    "bệnh nhân", "tôi có bn", "tôi có một", "ca này", "khám ca", "người bệnh",
    "bn nam", "bn nữ", "nam ~", "nữ ~", "nam,", "nữ,", "cụ ông", "cụ bà",
]
# SỬA 2026-09-03 (Workflow đối kháng đa-agent vòng 2, phát hiện CRITICAL cùng nhóm với
# BƯỚC 0 cờ đỏ ở orchestrator.py): CLINICAL_CASE_CUES liệt kê hữu hạn không tổng quát hoá
# cho cách diễn đạt tự nhiên khác — đo được bằng chạy sống: "Phụ nữ mang thai 32 tuần bị
# đau đầu dữ dội..." và "Bé trai 8 tuổi khó thở về đêm..." đều rơi 'unknown'. Thêm regex
# HẸP, chỉ khớp các mô tả tuổi/giới/thai kỳ đặc trưng của một CA — CỐ Ý không dùng một
# mẫu \d+\s*tuổi trần (quá rộng, sẽ khớp cả câu nhắc tuổi trong mô tả quần thể nghiên cứu
# như "nghiên cứu ở người trên 65 tuổi" — dù thứ tự kiểm RESEARCH_TOPIC_CUES trước vẫn xử
# lý đúng khi có đủ từ khoá thiết kế, quy tắc AN TOÀN vẫn là: rộng hơn CHỈ khi thu hẹp có
# chủ đích, không phải mặc định).
CLINICAL_CASE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(nam|nữ)\s*\d+\s*tuổi"),        # "nữ 60 tuổi" (không dấu phẩy/dấu ~)
    re.compile(r"(bé|cháu)\s*(trai|gái|bé)"),     # "bé trai", "cháu bé", "cháu gái"
    re.compile(r"phụ nữ (mang thai|có thai)"),    # thai kỳ
]
# SỬA 2026-09-05 (Workflow đối kháng đa-agent vòng 4, HIGH): tập CON của
# CLINICAL_CASE_PATTERNS — CHỈ hai mẫu ĐẦU (tuổi+giới cụ thể, giới tính trẻ em) — dùng RIÊNG
# cho nhánh "cờ đỏ luôn thắng cue đề tài" trong route() bên dưới. CỐ Ý LOẠI mẫu thai kỳ (mẫu
# thứ 3): xác nhận bằng thực nghiệm — bản vá đầu tiên dùng CẢ BA mẫu làm hỏng chính CA_CHINH
# của test_orchestrator_workflow_20260904_research_topic_step0.py ("Nghiên cứu cắt ngang tỷ lệ
# đau đầu dữ dội kèm sốt cao ở phụ nữ mang thai tại phòng khám" — một ĐỀ TÀI THẬT mô tả QUẦN
# THỂ nghiên cứu, không phải một ca cụ thể) bị misroute ngược thành clinical_case — tái phát
# đúng lỗi vòng 10 mà RESEARCH_TOPIC_CUES sinh ra để chặn. "phụ nữ mang thai" một mình KHÔNG
# phải tín hiệu an toàn để phân biệt "một bệnh nhân cụ thể" khỏi "mô tả quần thể", khác
# "nữ 60 tuổi,"/"bé trai..." (số tuổi/giới GẮN VÀO một chủ ngữ số ít, đúng khuôn trình bày ca
# lâm sàng — không có tiền lệ dùng để mô tả quần thể trong toàn bộ test suite hiện có). Đây là
# đánh đổi CÓ CHỦ Ý, cùng tinh thần giới hạn đã ghi nhận ở R5 của guardrail_check_g0 — một cấp
# cứu sản khoa (tiền sản giật…) mô tả BẰNG "protocol" mà KHÔNG kèm tuổi/giới cụ thể vẫn có thể
# lọt qua override này; ghi nhận ở đây để không bị coi là "đã đóng hoàn toàn".
_INDIVIDUAL_PATIENT_OVERRIDE_PATTERNS = CLINICAL_CASE_PATTERNS[:2]
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
# SỬA 2026-09-03 (Workflow đối kháng đa-agent vòng 2): "khảo sát cắt ngang"/"khảo sát mô
# tả"... ở trên đòi cụm liền kề — câu diễn đạt tự nhiên có từ chen giữa ("khảo sát tỷ lệ
# trầm cảm sau sinh tại phòng khám, thiết kế cắt ngang mô tả") không khớp, rồi bị
# SINGLE_TASK_RULES nuốt mất vì chỉ cần khớp một từ đơn lẻ ("trầm cảm") ở bất kỳ đâu →
# misroute sang agent lâm sàng đơn lẻ thay vì mở đề tài G0-G10. Thêm luật RIÊNG cho
# "khảo sát" (không mở rộng cho "nghiên cứu" trần — xem comment RESEARCH_TOPIC_CUES phía
# trên: "nghiên cứu" một mình dễ khớp nhầm câu hỏi tra cứu chứng cứ tại điểm khám): "khảo
# sát" + bất kỳ từ THIẾT KẾ nào xuất hiện Ở ĐÂU ĐÓ trong câu (không cần liền kề).
_RESEARCH_DESIGN_WORDS = (
    "hồi cứu", "tiến cứu", "cắt ngang", "so sánh", "thuần tập",
    "bệnh chứng", "can thiệp", "quan sát", "mô tả",
)


def _khao_sat_co_thiet_ke(text: str) -> bool:
    return "khảo sát" in text and any(w in text for w in _RESEARCH_DESIGN_WORDS)

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
    (["đơn này an toàn", "thuốc đánh nhau", "tương tác thuốc", "chỉnh liều theo thận", "chống chỉ định",
      # 20/09/2026 (T3-05): tra tên thuốc quốc tế qua RxNorm/EMA — trước đó 0 cửa vào trong router
      # CỐ Ý là CỤM tra cứu, không phải từ trần «biệt dược»/«hoạt chất»: phản biện đối kháng 20/09 (L1) tái hiện — câu mô tả
      # ca («Bà 70 tuổi uống biệt dược Coversyl, nay khó thở, phù mặt») từ unknown (có BƯỚC 0 cờ đỏ) thành single_task
      # (KHÔNG BƯỚC 0) chỉ vì nhắc tên thuốc.
      "tra biệt dược", "tên quốc tế của", "hoạt chất của", "hoạt chất gì", "rxnorm", "tên hoạt chất",
      "tra tên thuốc", "tên thuốc quốc tế"], "ke-don-an-toan", "an toàn kê đơn"),
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
    (["kiểm trích dẫn", "kiểm chứng trích dẫn", "kiểm chứng pmid", "kiểm chứng doi",
      "trích dẫn ma", "verify pmid", "verify doi", "xác minh pmid",
      "xác minh doi", "bibtex",
      # 20/09/2026 (T3-05): nguồn bị rút / thông báo đính chính bị rút (BH109) — trước đó không có cửa vào
      # KHÔNG thêm «retraction»/«corrigendum» trần: agent này thuộc VIEC_LE_MANH nên thắng cue đề tài — một đề tài
      # nghiên cứu VỀ retraction sẽ bị nuốt khỏi G0–G10 (phản biện 20/09, L5).
      "bị rút bài", "thông báo rút", "đã bị rút"], "kiem-chung-trich-dan", "kiểm trích dẫn"),
    (["chi phí hiệu quả", "chi phí–hiệu quả", "kinh tế y tế", "tác động ngân sách", "icer"], "kinh-te-y-te", "kinh tế y tế"),
    (["mô hình tiên lượng", "tripod", "điểm dự báo", "validate thang điểm"], "mo-hinh-tien-luong", "mô hình tiên lượng"),
    (["cosmin", "kiểm định thang đo", "prom"], "cong-cu-do-luong", "công cụ đo lường"),
    (["định tính", "phỏng vấn", "nhóm tiêu điểm", "coreq"], "nghien-cuu-dinh-tinh", "định tính"),
    (["soi gói", "kiểm liêm chính", "có vượt cổng", "có lẫn pii"], "tham-dinh-dau-ra", "guardrail"),
    # ── ĐO 02/09/2026: 12/30 câu bác sĩ nói TỰ NHIÊN rơi `unknown`, tức nhạc trưởng
    # KHÔNG vào cửa — dù MỌI câu trong đó đều đã có chủ (agent/skill/lệnh). Khoảng
    # trống nằm ở CỬA VÀO, không phải ở năng lực. Chín luật dưới đây trỏ vào agent CÓ
    # THẬT (validate() chặn tham chiếu treo); ba việc còn lại không có agent nên nằm ở
    # VIEC_CONG_CU. Cụm chọn theo lời bác sĩ hay dùng, không phải thuật ngữ nội bộ.
    (["viết bản thảo", "viết bài báo", "làm bài báo", "làm một bài báo", "phần bàn luận",
      "phần kết quả", "viết phần"],
     "viet-ban-thao", "viết bản thảo"),
    (["phân tích số liệu", "phân tích dữ liệu", "chạy thống kê", "xử lý số liệu"],
     "phan-tich-thong-ke", "phân tích số liệu"),
    (["có gì mới", "cập nhật chứng cứ", "chứng cứ mới", "guideline mới", "khuyến cáo mới"],
     "cap-nhat-guideline", "cập nhật chứng cứ chủ đề"),
    (["dashboard", "cổng liêm chính", "bộ năm", "bản đọc chứng cứ"],
     "cap-nhat-guideline", "kiểm gói cập nhật chứng cứ"),
    (["bị rút không", "đã bị rút", "rút bài", "retracted"],
     "kiem-chung-trich-dan", "kiểm rút bài"),
    (["chọn tạp chí", "nộp bài", "cover letter", "tạp chí nào"],
     "nop-bai-phan-hoi", "chọn tạp chí / nộp bài"),
    (["tương tác gì", "thuốc này với", "dùng chung được không", "có dùng được"],
     "ke-don-an-toan", "an toàn kê đơn"),
    (["sàng lọc ung thư", "sàng lọc từ tuổi", "nên sàng lọc", "khám định kỳ"],
     "du-phong-tam-soat", "dự phòng–tầm soát"),
    (["tờ dặn dò", "dặn dò bệnh nhân", "in tờ", "hướng dẫn cho bệnh nhân"],
     "loi-dan-tuan-thu", "tờ dặn dò A5"),
]

# VIỆC LẺ MẠNH — cụm gọi ĐÍCH DANH ĐÚNG MỘT sản phẩm. Khi câu vừa khớp việc lẻ này vừa
# mang cue ĐỀ TÀI, việc lẻ thắng: "tính cỡ mẫu cho nghiên cứu cắt ngang" là xin MỘT con
# số, không phải khởi động vòng đời G0–G10 (đo 02/09: câu đó từng đẩy cả nhạc trưởng
# nghiên cứu chạy 11 cổng).
# ⚠️ BẤT ĐỐI XỨNG CÓ CHỦ Ý: việc lẻ mạnh KHÔNG bao giờ thắng cue CA LÂM SÀNG. Câu vừa có
# "bệnh nhân" vừa xin một sản phẩm lẻ vẫn đi vào nhạc trưởng lâm sàng — over-route sang
# nơi CÓ sàng lọc cờ đỏ là chiều an toàn; under-route bỏ qua cờ đỏ thì không.
VIEC_LE_MANH: set[str] = {
    "co-mau-nghien-cuu", "kiem-chung-trich-dan", "thu-thu-tai-lieu",
    "nop-bai-phan-hoi", "viet-ban-thao", "phan-tich-thong-ke", "tham-dinh-phe-binh",
}

# VIỆC CÓ CHỦ NHƯNG KHÔNG PHẢI AGENT — chủ là lệnh/skill/công cụ. Tách riêng vì
# `_run_step` tra registry AGENT: nhét tên lệnh vào SINGLE_TASK_RULES sẽ thành tham
# chiếu treo. Trả `cong_cu` để nhạc trưởng gọi đúng chủ, thay vì trả "không biết" về
# một việc mà hệ biết rõ chủ của nó.
VIEC_CONG_CU: list[tuple[list[str], str, str]] = [
    (["còn gì để hoàn thiện", "còn gì phải làm", "hệ thống còn gì", "còn việc gì"],
     "tools/tu_de_xuat_viec.py", "bảng 8 giác quan — hệ còn gì để hoàn thiện"),
    # 20/09/2026 (T3-05): năng lực mới CÓ CHỦ nhưng chưa có cửa vào router (đo: unknown).
    (["làm mới chứng cứ", "cập nhật chứng cứ chủ đề", "chủ đề nào cũ", "chủ đề nào lâu", "độ tươi chứng cứ",
      "làm mới chủ đề"],
     "ops/orchestrator.py", "làm mới chứng cứ chủ đề (--cu-nhat N | --topic X; máy làm A2/A4/B2, dừng ở CANDIDATE)"),
    (["độ tươi thang điểm", "thang điểm bị rút", "thang điểm còn hiệu lực", "kiểm rút bài thang điểm"],
     "medical-ebm-automation/tools/kiem_do_tuoi_thang_diem.py", "rút bài + độ tươi 32 thang điểm verified"),
    (["lịch nền", "tác vụ nền", "tác vụ lịch", "giám sát tuần có chạy", "gói duyệt tuần có chạy"],
     "tools/kiem_lich_nen.py", "cảm biến người chết lịch nền — kỳ nào không nổ"),
    (["icd-10", "icd10", "mã bệnh", "mã chẩn đoán", "mã thủ thuật"],
     "/tra-ma-icd10", "tra mã ICD-10"),
    (["làm slide", "bài giảng", "soạn slide", "tài liệu đào tạo", "poster"],
     "dao-tao-slide-tai-lieu-y-khoa", "sản phẩm đào tạo / slide"),
]

CLINICAL_ORCHESTRATOR = "dieu-phoi-lam-sang"
RESEARCH_ORCHESTRATOR = "dieu-phoi-nghien-cuu"


@dataclass
class IntentResult:
    kind: str  # 'clinical_case' | 'research_topic' | 'single_task' | 'cong_cu' | 'unknown'
    target: str  # agent điểm vào
    reason: str
    matches: list[str] = field(default_factory=list)  # các luật việc-lẻ khớp (minh bạch)

    def as_dict(self) -> dict:
        return {"kind": self.kind, "target": self.target, "reason": self.reason, "matches": self.matches}


def _any(text: str, cues: list[str]) -> list[str]:
    return [c for c in cues if c in text]


def _any_ascii(text: str, cues: list[str]) -> list[str]:
    """Khớp cue đã gấp dấu theo RANH GIỚI TỪ. `in` trần va chạm: «co do» ⊂ «co doi chung» (có đối chứng), «dau man» ⊂ «dau
    mang» (đau màng phổi), «lo au» ⊂ «hello author» — phản biện đối kháng 20/09 (L2/L3) đã tái hiện."""
    return [c for c in cues if re.search(r"(?<![a-z0-9])" + re.escape(c) + r"(?![a-z0-9])", text)]


# Cue gấp dấu MƠ HỒ ngay cả khi có ranh giới từ ⇒ KHÔNG dùng cho câu ASCII (kèm thay thế cụ thể bên dưới):
#   «cỡ mẫu»→co mau = «có máu» (phân có máu, ho có máu bị chuyển thành việc cỡ mẫu — mất BƯỚC 0);
#   «cờ đỏ»→co do = «có đo» (có đo huyết áp 24 giờ).
_CUE_ASCII_LOAI = {"co mau", "co do"}
_CUE_ASCII_THEM = {"co-mau-nghien-cuu": ["tinh co mau", "co mau nghien cuu", "co mau cho nghien cuu", "tinh cong thuc co mau"]}


def _fold(s: str) -> str:
    """Bỏ dấu tiếng Việt (KỂ CẢ đ→d, mà NFD không tự tách được) và hạ chữ thường."""
    s = unicodedata.normalize("NFD", s.replace("đ", "d").replace("Đ", "D"))
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower()


class _Bang(NamedTuple):
    khop: object
    single: list
    research_cues: list
    design_words: tuple
    khao_sat: str
    individual: list
    patterns: list
    case_cues: list
    cong_cu: list


def _gap(x):
    return [_fold(c) for c in x]


# CỬA VÀO MÙ DẤU (T3-01, 20/09/2026): 7/7 câu gõ KHÔNG dấu («benh nhan nam 60 tuoi dau nguc 2 gio») rơi `unknown`, kể
# cả ca có cờ đỏ — bác sĩ gõ nhanh trên điện thoại thường bỏ dấu. Câu THUẦN ASCII không thể khớp cue có dấu, nên nó dùng
# bảng đã GẤP DẤU của chính các cue/mẫu đó. Câu CÓ dấu giữ nguyên bảng cũ (để «năm,» không khớp nhầm «nam,»).
_CO_DAU = _Bang(_any, SINGLE_TASK_RULES, RESEARCH_TOPIC_CUES, _RESEARCH_DESIGN_WORDS, "khảo sát",
                _INDIVIDUAL_PATIENT_OVERRIDE_PATTERNS, CLINICAL_CASE_PATTERNS, CLINICAL_CASE_CUES, VIEC_CONG_CU)
_ASCII = _Bang(
    _any_ascii,
    [([k for k in _gap(kws) if k not in _CUE_ASCII_LOAI] + _CUE_ASCII_THEM.get(a, []), a, n)
     for kws, a, n in SINGLE_TASK_RULES], _gap(RESEARCH_TOPIC_CUES),
    tuple(_gap(_RESEARCH_DESIGN_WORDS)), _fold("khảo sát"),
    [re.compile(_fold(p.pattern)) for p in _INDIVIDUAL_PATIENT_OVERRIDE_PATTERNS],
    [re.compile(_fold(p.pattern)) for p in CLINICAL_CASE_PATTERNS], _gap(CLINICAL_CASE_CUES),
    [(_gap(kws), c, n) for kws, c, n in VIEC_CONG_CU])


def route(request: str) -> IntentResult:
    """Phân loại request. Ưu tiên: ĐỀ TÀI > CA lâm sàng > việc lẻ > unknown (đề tài kiểm trước vì
    'bệnh nhân' cũng xuất hiện khi mô tả quần thể nghiên cứu — xem lý do dưới)."""
    # NFC trước: chữ chép từ Finder/một số IME là dấu TỔ HỢP (NFD) và không khớp cue nào (L11).
    t = unicodedata.normalize("NFC", request or "").lower().strip()
    if not t:
        return IntentResult("unknown", "", "request rỗng")
    # Chọn bảng theo việc câu có DẤU TIẾNG VIỆT hay không — KHÔNG theo `isascii()`: một ký tự phi-ASCII vô hại (°, …, –, NBSP,
    # emoji trong «sốt 39°C») từng đẩy cả câu không dấu về bảng có dấu và rơi unknown (L4).
    B = _CO_DAU if _fold(t) != t else _ASCII

    single_hits = [(agent, note) for kws, agent, note in B.single if B.khop(t, kws)]
    match_labels = [f"{a} ({n})" for a, n in single_hits]

    # Cue nghiên cứu ('đề tài/đề cương/protocol') là tín hiệu MẠNH → kiểm TRƯỚC cue lâm sàng
    # ('bệnh nhân' cũng xuất hiện khi mô tả quần thể nghiên cứu, nên không được thắng 'đề tài').
    if B.khop(t, B.research_cues) or (B.khop(t, [B.khao_sat]) and B.khop(t, list(B.design_words))):
        # SỬA 2026-09-04 (Workflow đối kháng đa-agent vòng 3, CRITICAL): CỜ ĐỎ LUÔN THẮNG
        # cue đề tài, kể cả khi cue đề tài đến từ một từ TRUNG TÍNH như "protocol" (rất phổ
        # biến trong ca thật: "đang trong protocol hoá trị", "chạy protocol hồi sức"). Trước
        # đây "manh" bên dưới chỉ giải cứu VIEC_LE_MANH (agent nghiên cứu thuần) —
        # "sang-loc-co-do" KHÔNG nằm trong tập đó (đúng ý, xem comment VIEC_LE_MANH ngay
        # dưới nó), nên một ca cấp cứu THẬT ("bệnh nhân ngừng tim, chạy protocol hồi sức thế
        # nào, cần chuyển cấp cứu ngay?") vẫn lọt xuống research_topic mà KHÔNG một bước
        # sàng lọc cờ đỏ nào chạy — RESEARCH_FLOW không có bước nào tương đương BƯỚC 0 của
        # CLINICAL_FLOW. Cùng nguyên tắc bất đối xứng đã ghi ở VIEC_LE_MANH: over-route sang
        # nơi CÓ sàng lọc cờ đỏ là chiều an toàn, under-route bỏ qua cờ đỏ thì không.
        #
        # SỬA 2026-09-05 (Workflow đối kháng đa-agent vòng 4, HIGH): bản vá vòng 3 CHỈ giải
        # cứu khi câu chứa một TỪ KHOÁ cờ đỏ tường minh ("cấp cứu"/"chuyển viện"/"cờ đỏ"…).
        # Một ca cấp cứu THẬT có thể mang dấu hiệu RÕ RÀNG là mô tả MỘT bệnh nhân cụ thể (theo
        # đúng khuôn trình bày ca lâm sàng "nữ 60 tuổi,"/"bé trai...") mà không dùng đúng từ nào
        # trong số đó — xác nhận bằng thực nghiệm: "nữ 60 tuổi, tiền sử ung thư vú, đang trong
        # protocol hoá trị, nay sốt cao 39 độ, rét run" (giảm bạch cầu hạt sốt — cấp cứu ung thư
        # thật) khớp RESEARCH_TOPIC_CUES qua "protocol" nhưng KHÔNG khớp "sang-loc-co-do" → vẫn
        # lọt xuống research_topic trước bản vá này. Dùng ĐÚNG `_INDIVIDUAL_PATIENT_OVERRIDE_
        # PATTERNS` (xem comment tại định nghĩa — CỐ Ý hẹp hơn CLINICAL_CASE_PATTERNS đầy đủ, đã
        # loại mẫu thai kỳ vì nó gây báo động giả cho mô tả QUẦN THỂ nghiên cứu, xác nhận bằng
        # chính hồi quy có sẵn của task #57).
        if (any(a == "sang-loc-co-do" for a, _ in single_hits)
                or any(p.search(t) for p in B.individual)):
            return IntentResult("clinical_case", CLINICAL_ORCHESTRATOR,
                                "khớp CỜ ĐỎ hoặc mô tả CA lâm sàng cụ thể (tuổi+giới/trẻ em) "
                                "cùng lúc với cue đề tài — an toàn luôn thắng, over-route sang "
                                "nhạc trưởng lâm sàng (có sàng lọc cờ đỏ ở BƯỚC 0) là chiều an "
                                "toàn", match_labels)
        # Việc lẻ MẠNH thắng cue đề tài: xin một sản phẩm cụ thể ≠ khởi động vòng đời.
        manh = [(a, n) for a, n in single_hits if a in VIEC_LE_MANH]
        if manh:
            agent, note = manh[0]
            return IntentResult("single_task", agent,
                                f"khớp việc lẻ MẠNH ({note}) — xin một sản phẩm cụ thể, "
                                f"không khởi động vòng đời G0–G10", match_labels)
        return IntentResult("research_topic", RESEARCH_ORCHESTRATOR,
                            "phát hiện một ĐỀ TÀI nghiên cứu → nhạc trưởng nghiên cứu (G0→G10)",
                            match_labels)
    pattern_hits = [p.pattern for p in B.patterns if p.search(t)]
    if B.khop(t, B.case_cues) or pattern_hits:
        return IntentResult("clinical_case", CLINICAL_ORCHESTRATOR,
                            "phát hiện mô tả một CA lâm sàng → nhạc trưởng lâm sàng (5 bước EBM)",
                            match_labels)
    if single_hits:
        agent, note = single_hits[0]
        return IntentResult("single_task", agent, f"khớp việc lẻ: {note}", match_labels)

    for kws, cong_cu, note in B.cong_cu:
        if B.khop(t, kws):
            return IntentResult("cong_cu", cong_cu, f"việc có chủ là CÔNG CỤ/SKILL: {note}",
                                match_labels)

    return IntentResult("unknown", "",
                        "chưa khớp luật nào — nêu rõ CA (‘tôi có bệnh nhân…’) / ĐỀ TÀI (‘đề tài…’) / hoặc câu hỏi cụ thể",
                        match_labels)
