# -*- coding: utf-8 -*-
"""
compare_backends.py — SO SÁNH chất lượng xếp hạng: TF-IDF (semantic nhẹ) vs hashing (fallback).

Mục đích: CHỨNG MINH backend TF-IDF (mới) tách hạng tốt hơn hashing trên dữ liệu SYNTHETIC.
Với mỗi truy vấn (cố ý DIỄN ĐẠT KHÁC chữ trong thẻ), đo:
  - Top-1 có đúng thẻ kỳ vọng (ground-truth synthetic) không?
  - MARGIN = điểm(top1) - điểm(top2): margin lớn = tách hạng rõ, ít nhiễu.
  - MRR (Mean Reciprocal Rank) của thẻ kỳ vọng.

LIÊM CHÍNH: đây KHÔNG phải benchmark chuẩn (chỉ 3 thẻ synthetic). Chỉ minh hoạ luồng + lợi thế
IDF của TF-IDF (hạ trọng số từ phổ biến -> đẩy thẻ không liên quan về ~0). KHÔNG dùng dữ liệu thật.

Dùng:  cd tools/rag && python3 compare_backends.py
[PROTOTYPE — minh hoạ tách hạng; kết quả truy xuất vẫn phải kiểm chứng PMID/DOI. Cần bác sĩ kiểm chứng.]
"""
import json, os
import numpy as np
from deidentify import sanitize_record, assert_no_pii, record_to_text, PiiDetectedError
from _backend import _HashingEmbedder, _SklearnTfidfEmbedder

SRC = os.path.join(os.path.dirname(__file__), "sample_data", "synthetic_evidence.json")

# Truy vấn diễn đạt KHÁC chữ trong thẻ + thẻ kỳ vọng (ground-truth synthetic).
QUERIES = [
    ("thuốc giúp bớt nằm viện vì suy tim cho người tiểu đường", "SYN-2026-0001"),
    ("đặt mục tiêu kiểm soát đường huyết cho cụ già yếu mắc nhiều bệnh", "SYN-2026-0002"),
    ("xét nghiệm đạm niệu để đánh giá phân tầng bệnh thận", "SYN-2026-0003"),
]


def load_clean():
    """Đọc thẻ synthetic -> qua cổng PII -> trả (ids, texts) các thẻ SẠCH."""
    cards = json.load(open(SRC, encoding="utf-8"))["evidence_cards"]
    ids, texts = [], []
    for raw in cards:
        try:
            rec = sanitize_record(raw); assert_no_pii(rec)
        except PiiDetectedError:
            continue  # bỏ thẻ dính PII (SYN-2026-DIRTY)
        ids.append(rec["id"]); texts.append(record_to_text(rec))
    return ids, texts


def rank(emb, ids, texts, query):
    if hasattr(emb, "fit"):
        emb.fit(texts)
    M = emb.embed(texts)
    q = emb.embed([query])[0]
    sims = M @ q
    order = np.argsort(-sims)
    return [(ids[k], float(sims[k])) for k in order]


def eval_backend(label, emb_factory, ids, texts):
    print(f"\n===== BACKEND: {label} =====")
    top1_correct, rr_sum, margins = 0, 0.0, []
    for q, gold in QUERIES:
        emb = emb_factory()
        ranked = rank(emb, ids, texts, q)
        top1 = ranked[0][0]
        ok = (top1 == gold)
        top1_correct += int(ok)
        gold_rank = [i for i, (cid, _) in enumerate(ranked) if cid == gold][0] + 1
        rr_sum += 1.0 / gold_rank
        margin = ranked[0][1] - ranked[1][1]
        margins.append(margin)
        print(f"  Q: {q[:48]}...")
        print(f"     top1={top1} ({'✅' if ok else '🔴 sai, kỳ vọng '+gold}) "
              f"| rank(gold)={gold_rank} | margin={margin:.3f}")
        print(f"     thứ hạng: " + ", ".join(f"{c}:{s:.3f}" for c, s in ranked))
    n = len(QUERIES)
    print(f"  --> Top-1 đúng: {top1_correct}/{n} | MRR={rr_sum/n:.3f} | margin TB={np.mean(margins):.3f}")
    return {"top1": top1_correct, "n": n, "mrr": rr_sum / n, "margin": float(np.mean(margins))}


if __name__ == "__main__":
    ids, texts = load_clean()
    print(f"Corpus synthetic: {len(ids)} thẻ sạch -> {ids}")
    r_tfidf = eval_backend("sklearn-tfidf (MỚI)", _SklearnTfidfEmbedder, ids, texts)
    r_hash = eval_backend("hashing-ngram (fallback cũ)", _HashingEmbedder, ids, texts)
    print("\n===== TÓM TẮT =====")
    print(f"{'backend':<26}{'top1':>8}{'MRR':>8}{'margin TB':>12}")
    print(f"{'sklearn-tfidf':<26}{r_tfidf['top1']}/{r_tfidf['n']:>5}{r_tfidf['mrr']:>8.3f}{r_tfidf['margin']:>12.3f}")
    print(f"{'hashing-ngram':<26}{r_hash['top1']}/{r_hash['n']:>5}{r_hash['mrr']:>8.3f}{r_hash['margin']:>12.3f}")
    print("\nGhi chú: margin lớn hơn = tách hạng rõ hơn (ít nhiễu). TF-IDF dùng IDF hạ trọng số")
    print("từ phổ biến -> thường đẩy thẻ không liên quan về ~0, tách rõ hơn hashing.")
    print("KHÔNG phải benchmark chuẩn. Cần bác sĩ kiểm chứng.")
