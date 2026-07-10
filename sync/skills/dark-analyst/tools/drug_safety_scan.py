#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
drug_safety_scan.py — Lớp phủ AN TOÀN THUỐC cho người cao tuổi / đa thuốc.

Quét tên thuốc trong một dashboard EBM, đối chiếu bảng CỜ cô đọng (Beers 2023 / STOPP-START v3
trong data/drug_flags.json) → in cảnh báo + sinh PROMPT để rà soát ĐẦY ĐỦ bằng skill
`nguoi-cao-tuoi-da-benh-da-thuoc`.

LƯU Ý: bảng cờ KHÔNG đầy đủ, chỉ để NHẮC. Quyết định cuối cùng theo tiêu chí gốc + lâm sàng.

Cách dùng:
    python3 tools/drug_safety_scan.py <dashboard>.html
    python3 tools/drug_safety_scan.py <dashboard>.html --flags data/drug_flags.json
"""
import sys, os, re, json, argparse, unicodedata


def _strip_diacritics(s):
    """Bỏ dấu tiếng Việt để so khớp không phân biệt có/không dấu (audit 2026-07-11:
    alias không dấu trong drug_flags.json — vd 'khang viem khong steroid' — trước đây
    KHÔNG BAO GIỜ khớp được vì dashboard luôn viết CÓ dấu; so khớp nay chuẩn hoá cả 2 vế)."""
    s = s.replace("đ", "d").replace("Đ", "D")
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--flags", default=None)
    a = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    flagpath = a.flags or os.path.join(here, "..", "data", "drug_flags.json")
    db = json.load(open(flagpath, encoding="utf-8"))
    text = open(a.file, encoding="utf-8").read().lower()
    text_norm = _strip_diacritics(text)

    hits = []
    for f in db.get("flags", []):
        names = [f["drug"]] + f.get("aliases", [])
        found = next((n for n in names if _strip_diacritics(n.lower()) in text_norm), None)
        if found:
            hits.append((f["drug"], found, f["cat"], f["flag"], f["source"]))

    print("=" * 66)
    print("LỚP PHỦ AN TOÀN THUỐC (người cao tuổi / đa thuốc)")
    print("Nguồn cờ: " + db.get("_source", ""))
    print("=" * 66)
    if not hits:
        print("  ✓ Không phát hiện thuốc nào trong bảng cờ cô đọng.")
        print("  (Bảng KHÔNG đầy đủ — nếu BN cao tuổi/đa thuốc, vẫn nên rà soát toàn diện.)")
        return 0
    seen = set()
    for drug, found, cat, flag, src in hits:
        if drug in seen:
            continue
        seen.add(drug)
        label = drug if found.lower() == drug.lower() else "%s (khớp: %s)" % (drug, found)
        print("  ⚑ %-28s [%s · %s]" % (label, cat, src))
        print("      %s" % flag)
    print("-" * 66)
    drugs = ", ".join(sorted(seen))
    print("→ PROMPT rà soát ĐẦY ĐỦ (dán cho skill nguoi-cao-tuoi-da-benh-da-thuoc):")
    print('   "Đối chiếu các thuốc sau với Beers 2023 và STOPP/START v3 cho người cao tuổi,')
    print('    nêu khuyến cáo giảm liều/ngưng (deprescribing) + tương tác: %s"' % drugs)
    print("-" * 66)
    print("Phát hiện %d nhóm thuốc cần lưu ý. Chỉ để NHẮC — quyết định theo tiêu chí gốc + lâm sàng." % len(seen))
    return 0


if __name__ == "__main__":
    sys.exit(main())
