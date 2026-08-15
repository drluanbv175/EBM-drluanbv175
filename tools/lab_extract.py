# -*- coding: utf-8 -*-
"""
lab_extract.py — CAFÉ-S P2.3 (phần AN TOÀN): đọc kết quả xét nghiệm dạng text/PDF
→ trích xuất chỉ số → GẮN CỜ bất thường THEO KHOẢNG THAM CHIẾU IN TRÊN PHIẾU.

Nguyên tắc liêm chính (đồng bộ `dien-giai-can-lam-sang`):
  • KHÔNG bịa ngưỡng — chỉ dùng khoảng tham chiếu CÓ TRONG phiếu. Chỉ số không
    kèm khoảng → đánh dấu "?" (không tự áp ngưỡng nhớ).
  • KHÔNG chẩn đoán — chỉ trích + gắn cờ H/L/bình thường; diễn giải lâm sàng +
    giá trị nguy kịch giao `dien-giai-can-lam-sang` (agent).
  • KHÔNG phân loại ảnh/âm thanh (cần ML kiểm định — ngoài phạm vi an toàn).
  • KHÔNG PII: chỉ xử lý chỉ số; KHÔNG trích tên/ngày sinh/mã BN.

Dùng:
    python3 lab_extract.py            # self-test trên phiếu synthetic (offline)
    python3 lab_extract.py <file.txt> # trích từ file text
    python3 lab_extract.py <file.pdf> # cần pdfplumber/pypdf (nếu có)
Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations
import re, sys, json, os

# Windows: stdout mặc định cp1252 giết print() tiếng Việt — ép UTF-8 (chốt BH55/R4)
import sys as _sys_r4
for _s_r4 in (_sys_r4.stdout, _sys_r4.stderr):
    try:
        _s_r4.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

# Dòng dạng:  <Tên>  <giá trị>  [đơn vị]  (low - high) | [low-high] | low - high
# Hỗ trợ số thập phân dùng '.' hoặc ',' ; dấu gạch '-', '–', '—' ; ngoặc () [] hoặc không.
_NUM = r"[-+]?\d+(?:[.,]\d+)?"
_LINE = re.compile(
    rf"^\s*(?P<ten>[^:|\t]+?)\s*[:|\t]?\s*"
    rf"(?P<gt>{_NUM})\s*"
    rf"(?P<dv>[A-Za-zµ%/\^\d\.]+(?:/[A-Za-zµ%\^\d\.]+)?)?\s*"
    rf"[\(\[]?\s*(?P<low>{_NUM})\s*[-–—]\s*(?P<high>{_NUM})\s*[\)\]]?\s*$"
)
# Dòng chỉ có giá trị, KHÔNG kèm khoảng tham chiếu → trích nhưng cờ '?'
_LINE_NORANGE = re.compile(
    rf"^\s*(?P<ten>[^:|\t]+?)\s*[:|\t]\s*(?P<gt>{_NUM})\s*(?P<dv>[A-Za-zµ%/\^\d\.]+)?\s*$"
)


def _f(x: str) -> float:
    return float(x.replace(",", "."))


def parse_lab_text(text: str) -> list:
    """Trích từng dòng KQ → dict. Cờ: 'H' cao, 'L' thấp, 'normal', '?' (không có khoảng)."""
    out = []
    for ln in text.splitlines():
        ln = ln.strip()
        if not ln or len(ln) < 3:
            continue
        m = _LINE.match(ln)
        if m:
            gt, low, high = _f(m["gt"]), _f(m["low"]), _f(m["high"])
            flag = "L" if gt < low else ("H" if gt > high else "normal")
            out.append({"ten": m["ten"].strip(), "gia_tri": gt, "don_vi": (m["dv"] or "").strip(),
                        "tc_thap": low, "tc_cao": high, "co": flag})
            continue
        m = _LINE_NORANGE.match(ln)
        if m and re.search(r"[A-Za-zÀ-ỹ]", m["ten"]):  # tên phải có chữ (tránh dòng nhiễu thuần số)
            out.append({"ten": m["ten"].strip(), "gia_tri": _f(m["gt"]),
                        "don_vi": (m["dv"] or "").strip(), "tc_thap": None,
                        "tc_cao": None, "co": "?"})
    return out


def abnormal(parsed: list) -> list:
    """Lọc các chỉ số ngoài khoảng (H/L). Chỉ số '?' (không có khoảng) KHÔNG tự gắn bất thường."""
    return [r for r in parsed if r["co"] in ("H", "L")]


def report(parsed: list) -> dict:
    ab = abnormal(parsed)
    noref = [r for r in parsed if r["co"] == "?"]
    return {
        "tong_chi_so": len(parsed),
        "bat_thuong": [f'{r["ten"]}={r["gia_tri"]}{r["don_vi"]} ({r["co"]}; TC {r["tc_thap"]}-{r["tc_cao"]})' for r in ab],
        "so_bat_thuong": len(ab),
        "khong_co_khoang_tham_chieu": [r["ten"] for r in noref],
        "ghi_chu": "Cờ theo khoảng tham chiếu IN TRÊN PHIẾU. Diễn giải lâm sàng + giá trị nguy kịch → agent dien-giai-can-lam-sang. Cần bác sĩ kiểm chứng.",
    }


def pdf_to_text(path: str) -> str:
    try:
        import pdfplumber  # type: ignore
        with pdfplumber.open(path) as pdf:
            return "\n".join((p.extract_text() or "") for p in pdf.pages)
    except ImportError:
        try:
            from pypdf import PdfReader  # type: ignore
            return "\n".join((pg.extract_text() or "") for pg in PdfReader(path).pages)
        except ImportError:
            raise SystemExit("Cần cài pdfplumber hoặc pypdf để đọc PDF (pip install pdfplumber).")


# ── Self-test (offline, KHÔNG PII) ───────────────────────────────────────
_SAMPLE = """KET QUA XET NGHIEM (synthetic, khong PII)
Glucose doi: 7.2 mmol/L (3.9 - 5.5)
Hemoglobin 9.8 g/dL [12 - 15.5]
Creatinin 180 umol/L 53 - 97
Kali 6.9 mmol/L (3.5 - 5.1)
Natri: 140 mmol/L (136 - 145)
HbA1c: 8.5 %
"""
# Kỳ vọng: Glucose H, Hemoglobin L, Creatinin H, Kali H, Natri normal, HbA1c '?' (không khoảng)
_EXPECT = {"Glucose doi": "H", "Hemoglobin": "L", "Creatinin": "H", "Kali": "H",
           "Natri": "normal", "HbA1c": "?"}


def _selftest():
    parsed = parse_lab_text(_SAMPLE)
    got = {r["ten"]: r["co"] for r in parsed}
    print("=== SELF-TEST lab_extract (synthetic) ===")
    ok = True
    for ten, exp in _EXPECT.items():
        g = got.get(ten)
        mark = "✅" if g == exp else "🔴"
        if g != exp:
            ok = False
        print(f"  {mark} {ten}: cờ={g} (kỳ vọng {exp})")
    print(json.dumps(report(parsed), ensure_ascii=False, indent=2))
    assert ok, "lab_extract sai: cờ không khớp kỳ vọng"
    # specificity: chỉ số bình thường KHÔNG bị gắn bất thường; '?' KHÔNG bị gắn bất thường
    ab_names = {x.split("=")[0] for x in report(parsed)["bat_thuong"]}
    assert "Natri" not in ab_names and "HbA1c" not in ab_names, "Gắn cờ sai ở ca bình thường/không-khoảng"
    print("✅ SELF-TEST ĐẠT: gắn cờ đúng H/L/normal, không bịa ngưỡng cho chỉ số thiếu khoảng.")
    print("Cần bác sĩ kiểm chứng.")


def main():
    if len(sys.argv) < 2:
        _selftest()
        return
    path = sys.argv[1]
    text = pdf_to_text(path) if path.lower().endswith(".pdf") else open(path, encoding="utf-8").read()
    print(json.dumps(report(parse_lab_text(text)), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
