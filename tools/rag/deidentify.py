# -*- coding: utf-8 -*-
"""
deidentify.py — KHỬ ĐỊNH DANH & CỔNG CHẶN PII cho pipeline RAG chứng cứ.

NGUYÊN TẮC LIÊM CHÍNH (bắt buộc):
  - RAG này CHỈ thao tác trên METADATA CHỨNG CỨ (PMID/DOI/guideline/chủ đề/trạng thái).
  - TUYỆT ĐỐI KHÔNG ingest thông tin định danh bệnh nhân (PII).
  - Mọi bản ghi PHẢI đi qua `assert_no_pii()` trước khi embed/lưu. Nếu nghi còn PII -> NÉM LỖI, DỪNG.

Cách dùng:
    from deidentify import sanitize_record, assert_no_pii, ALLOWED_FIELDS
    clean = sanitize_record(raw)      # chỉ giữ trường metadata được phép, đã khử PII
    assert_no_pii(clean)             # cổng chặn: ném PiiDetectedError nếu còn nghi PII

[PROTOTYPE — cần cài deps + BS duyệt governance trước khi chạy trên dữ liệu thật]
"""
from __future__ import annotations
import re
from typing import Any, Dict, List, Tuple

# ------------------------------------------------------------------ #
# 1. Chỉ các trường METADATA CHỨNG CỨ này được phép đi vào index.
#    Mọi trường khác bị loại bỏ (whitelist, không blacklist).
# ------------------------------------------------------------------ #
ALLOWED_FIELDS = {
    "id", "cycle", "date_added", "date_source", "specialty", "topic",
    "pico_question", "recommendation", "certainty", "operational_assessment",
    "gradeLevel", "decision", "vietnam_context", "verification_status",
    "provenance",
}
# Trường lồng "source" chỉ giữ các khóa an toàn này:
ALLOWED_SOURCE_KEYS = {"agency", "title", "url", "pmid", "doi", "type"}

# Tên trường gợi ý PII -> nếu xuất hiện, chặn ngay (không cố làm sạch).
PII_FIELD_NAMES = {
    "patient", "ten", "tên", "name", "hoten", "ho_ten", "dob", "ngaysinh",
    "ngay_sinh", "birth", "cccd", "cmnd", "bhyt", "mrn", "sohoso", "so_ho_so",
    "phone", "sdt", "dienthoai", "address", "diachi", "địa_chỉ", "email_bn",
}

# ------------------------------------------------------------------ #
# 2. Mẫu PII trong nội dung text (regex, thiên về cảnh báo thừa).
# ------------------------------------------------------------------ #
PII_PATTERNS: List[Tuple[str, "re.Pattern[str]"]] = [
    ("SĐT_VN",   re.compile(r"(?<!\d)(?:\+?84|0)(?:\d[\s.\-]?){8,10}\d(?!\d)")),
    ("CCCD/CMND", re.compile(r"(?<!\d)\d{9}(?:\d{3})?(?!\d)")),  # 9 hoặc 12 số liền
    ("BHYT",     re.compile(r"\b[A-Z]{2}\d{1,2}\d{12}\b")),
    ("EMAIL",    re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")),
    ("NGAY_SINH", re.compile(r"\b(?:sinh(?:\s*ng[aà]y)?|dob|ng[aà]y\s*sinh)\b[:\s]*\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}", re.I)),
    ("MRN",      re.compile(r"\b(?:MRN|mã\s*hồ\s*sơ|số\s*hồ\s*sơ|HSBA)\b[:\s]*[A-Za-z0-9\-]+", re.I)),
    ("HO_TEN_CO_NHAN", re.compile(r"\b(?:bệnh\s*nhân|BN|ông|bà|cháu|anh|chị)\s+[A-ZÀ-Ỹ][a-zà-ỹ]+(?:\s+[A-ZÀ-Ỹ][a-zà-ỹ]+){1,3}\b")),
]


class PiiDetectedError(Exception):
    """Ném khi phát hiện (nghi) PII -> DỪNG, không ingest."""


def scan_text_for_pii(text: str) -> List[str]:
    """Trả danh sách nhãn PII bắt được trong một chuỗi (rỗng = sạch)."""
    hits = []
    if not text:
        return hits
    for label, pat in PII_PATTERNS:
        if pat.search(text):
            hits.append(label)
    return hits


def sanitize_record(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Lọc một evidence_card RAW -> chỉ giữ trường metadata được phép.
    KHÔNG cố 'làm sạch' free-text bệnh án; chỉ giữ trường an toàn theo schema.
    """
    if not isinstance(raw, dict):
        raise TypeError("Bản ghi phải là dict (evidence_card).")

    # Chặn sớm nếu có tên trường mang hơi hướng PII (khớp cả tên ghép, vd 'patient_name').
    for k in raw.keys():
        kl = str(k).strip().lower()
        if kl in PII_FIELD_NAMES or any(p in kl for p in PII_FIELD_NAMES):
            raise PiiDetectedError(
                f"Bản ghi {raw.get('id','?')} có trường nghi PII: '{k}' -> TỪ CHỐI ingest."
            )

    clean: Dict[str, Any] = {}
    for k, v in raw.items():
        if k == "source" and isinstance(v, dict):
            clean["source"] = {sk: v.get(sk, "") for sk in ALLOWED_SOURCE_KEYS}
        elif k in ALLOWED_FIELDS:
            clean[k] = v
        # mọi trường khác -> bỏ (kể cả critical_appraisal/history để gọn & an toàn)
    return clean


def record_to_text(rec: Dict[str, Any]) -> str:
    """Ghép các trường metadata thành một đoạn text để embed (không có PII)."""
    src = rec.get("source", {}) or {}
    parts = [
        rec.get("specialty", ""), rec.get("topic", ""),
        rec.get("pico_question", ""), rec.get("recommendation", ""),
        rec.get("certainty", ""), src.get("agency", ""), src.get("title", ""),
        rec.get("vietnam_context", ""),
    ]
    return " | ".join(p for p in parts if p)


# Trường NARRATIVE (tự do) cần quét PII. KHÔNG quét các trường ĐỊNH DANH CẤU TRÚC
# (id, pmid, doi, url, gradeLevel, decision, date_*) vì chúng vốn chứa chuỗi số/ký tự
# hợp lệ (PMID, DOI...) -> tránh báo PII giả khi chuỗi số cấu trúc đứng cạnh nhau.
NARRATIVE_FIELDS = {
    "topic", "pico_question", "recommendation", "certainty",
    "operational_assessment", "vietnam_context",
}
NARRATIVE_SOURCE_KEYS = {"agency", "title"}  # KHÔNG quét pmid/doi/url


def assert_no_pii(rec: Dict[str, Any]) -> None:
    """
    CỔNG CHẶN cuối: quét các trường NARRATIVE của bản ghi đã sanitize.
    Bỏ qua trường định danh cấu trúc (pmid/doi/url/id) để tránh báo PII giả.
    Còn nghi PII -> ném PiiDetectedError (DỪNG pipeline).
    """
    blob_parts = []
    for k, v in rec.items():
        if k in NARRATIVE_FIELDS and isinstance(v, str):
            blob_parts.append(v)
        elif k == "source" and isinstance(v, dict):
            blob_parts.extend(str(v.get(sk, "")) for sk in NARRATIVE_SOURCE_KEYS)
    blob = " | ".join(p for p in blob_parts if p)  # '|' chặn chuỗi số nối ngang qua khoảng trắng
    hits = scan_text_for_pii(blob)
    if hits:
        raise PiiDetectedError(
            f"Bản ghi {rec.get('id','?')} còn nghi PII {hits} -> TỪ CHỐI ingest. "
            f"Chỉ ingest metadata chứng cứ; rà lại nguồn."
        )


if __name__ == "__main__":
    # Tự kiểm nhanh: 1 bản ghi sạch + 1 bản ghi dính PII.
    ok = {"id": "EVID-X", "topic": "CKD", "source": {"pmid": "38490803", "doi": "10.1016/j.kint"}}
    bad = {"id": "EVID-Y", "patient_name": "Nguyễn Văn A", "topic": "ĐTĐ2"}
    print("[clean] sanitize+assert:", end=" ")
    c = sanitize_record(ok); assert_no_pii(c); print("PASS ->", c)
    print("[dirty] expect chặn:", end=" ")
    try:
        sanitize_record(bad)
    except PiiDetectedError as e:
        print("CHẶN OK ->", e)
