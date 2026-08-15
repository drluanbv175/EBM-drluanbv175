# -*- coding: utf-8 -*-
"""
query.py — Truy vấn ngữ nghĩa trên store metadata chứng cứ.

Trả về top-k bản ghi + PMID/DOI để ĐỐI CHIẾU lại qua agent `kiem-chung-trich-dan`
(chống trích dẫn ảo: RAG chỉ GỢI Ý nguồn, phải phân giải PMID/DOI mới được tin).

Dùng:
    python3 query.py "câu hỏi lâm sàng ..."        # mặc định top 3
    python3 query.py "..." --k 5

[PROTOTYPE — kết quả chỉ là gợi ý truy xuất; BẮT BUỘC kiểm chứng PMID/DOI trước khi dùng]
"""
from __future__ import annotations
import argparse, json, sys
from _backend import get_embedder, get_store

# Windows: stdout mặc định cp1252 giết print() tiếng Việt — ép UTF-8 (chốt BH55/R4)
import sys as _sys_r4
for _s_r4 in (_sys_r4.stdout, _sys_r4.stderr):
    try:
        _s_r4.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


def search(question: str, k: int = 3):
    emb = get_embedder()
    qv = emb.embed([question])[0]
    store = get_store()
    return store.query(qv, n_results=k)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("question", nargs="+", help="câu hỏi truy vấn")
    ap.add_argument("--k", type=int, default=3)
    args = ap.parse_args()
    q = " ".join(args.question)

    try:
        hits = search(q, args.k)
    except FileNotFoundError as e:
        print(f"[query] {e}"); sys.exit(1)

    print(f"[query] Hỏi: {q}\n[query] Top {len(hits)} bản ghi (điểm tương đồng giảm dần):\n")
    for rank, (item, score) in enumerate(hits, 1):
        m = item["metadata"]; src = m.get("source", {}) or {}
        pmid = src.get("pmid", "") or "—"; doi = src.get("doi", "") or "—"
        print(f"#{rank}  [{score:.3f}]  {m.get('id')} · {m.get('specialty','')}")
        print(f"      Chủ đề     : {m.get('topic','')}")
        print(f"      Khuyến cáo : {m.get('recommendation','')}")
        print(f"      Độ chắc    : {m.get('certainty','—')}  | GRADE: {m.get('gradeLevel','na')} | QĐ: {m.get('decision','—')}")
        print(f"      NGUỒN→kiểm : PMID:{pmid}  DOI:{doi}  ({src.get('agency','')})")
        print()
    print("[query] ⚠️ Đây là GỢI Ý truy xuất. Phải đối chiếu PMID/DOI qua `kiem-chung-trich-dan` "
          "trước khi trích dẫn. KHÔNG dùng làm kết luận lâm sàng. Cần bác sĩ kiểm chứng.")


if __name__ == "__main__":
    main()
