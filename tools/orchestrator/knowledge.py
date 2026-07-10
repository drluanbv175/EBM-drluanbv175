"""knowledge.py — Tầng TÍCH HỢP TRI THỨC: thứ bậc nguồn chứng cứ Cấp 0/0.5/1.

Thao tác hóa §2bis của `_CONNECTOR-CHUNG-CU.md`: nguồn chính thống TRƯỚC, PubMed là lớp
đối chiếu + lấy PMID/khử trùng. Cung cấp thứ tự tra cứu + phân tầng + quy tắc PARTIAL cho
mọi agent tra cứu/thẩm định/tổng quan.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import ROOT

CONNECTOR_SSOT = ROOT / ".claude" / "agents" / "_CONNECTOR-CHUNG-CU.md"


@dataclass(frozen=True)
class SourceTier:
    code: str          # '0' | '0.5' | '1' | 'drug'
    label: str
    role: str
    sources: tuple[str, ...]


SOURCE_TIERS: tuple[SourceTier, ...] = (
    SourceTier("0", "Cấp 0 — Chính thống", "nơi lấy khuyến cáo / kết luận (nguồn của record)",
               ("Cochrane", "NICE", "USPSTF", "Epistemonikos", "Europe PMC",
                "ESC/ACC-AHA", "ADA", "KDIGO", "GOLD/GINA", "IDSA/WHO",
                "EULAR/ACR", "ASCO/ESMO", "APA/ACOG", "kcb.vn (🇻🇳 QĐ-BYT)")),
    SourceTier("0.5", "Cấp 0.5 — Tạp chí đỉnh", "toàn văn nghiên cứu gốc / đồng thuận",
               ("NEJM", "Lancet", "JAMA", "BMJ", "Annals of IM", "Nature Medicine",
                "Circulation/JACC", "Diabetes Care", "Blood/Gut")),
    SourceTier("1", "Cấp 1 — Đối chiếu", "lấy PMID/DOI + xác nhận trùng khớp",
               ("PubMed/MEDLINE", "Europe PMC", "ClinicalTrials.gov")),
    SourceTier("drug", "An toàn thuốc", "nguồn của record cho cảnh báo kê đơn",
               ("openFDA", "DailyMed", "EMA", "MHRA", "LactMed", "WHO AWaRe", "BNF")),
)

# Thứ tự tra cứu mặc định (§2bis) — trả cho agent để tuân theo.
RETRIEVAL_ORDER: tuple[str, ...] = (
    "RAG nội bộ đã curate (clinical-evidence-rag)",
    "Cấp 0 — nguồn CHÍNH THỐNG (Cochrane/HTA + hiệp hội chuyên khoa + kcb.vn)",
    "Cấp 0.5 — tạp chí đỉnh (toàn văn khi cần)",
    "PubMed/Europe PMC — LỚP ĐỐI CHIẾU: lấy PMID/DOI + xác nhận trùng khớp",
    "CHỈ tìm PubMed sơ cấp độc lập khi nguồn chính thống KHÔNG phủ (ghi rõ)",
)

INVARIANTS: tuple[str, ...] = (
    "Mọi mục cần PMID/DOI (hoặc URL guideline + năm) để verify",
    "Thiếu nguồn → PARTIAL (không kết luận 'không có')",
    "KHÔNG PII outbound (truy vấn chỉ chứa PICO/từ khóa y khoa)",
    "Chỉ nguồn miễn phí (loại Consensus vì có upsell)",
    "Nguồn bậc cao mâu thuẫn → nêu mâu thuẫn, không chọn bài hợp ý",
)


@dataclass
class KnowledgeLayer:
    tiers: tuple[SourceTier, ...] = field(default_factory=lambda: SOURCE_TIERS)

    def retrieval_order(self) -> tuple[str, ...]:
        return RETRIEVAL_ORDER

    def tier_of(self, source: str) -> str | None:
        s = source.lower()
        for t in self.tiers:
            if any(s in x.lower() or x.lower().split("/")[0] in s for x in t.sources):
                return t.code
        return None

    def verify_against_ssot(self) -> list[str]:
        """Cảnh báo nếu SSOT connector không còn nhắc các nguồn cột sống (chống trôi)."""
        warns: list[str] = []
        if not CONNECTOR_SSOT.exists():
            return ["Thiếu file SSOT _CONNECTOR-CHUNG-CU.md"]
        text = CONNECTOR_SSOT.read_text(encoding="utf-8", errors="ignore")
        for key in ("Cochrane", "USPSTF", "kcb.vn", "Europe PMC", "1bis", "2bis"):
            if key not in text:
                warns.append(f"SSOT thiếu tham chiếu: {key}")
        return warns
