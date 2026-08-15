# -*- coding: utf-8 -*-
"""
ingest.py — Nạp METADATA CHỨNG CỨ vào vector store (qua cổng khử PII).

Luồng: đọc nguồn JSON (evidence_cards[]) -> sanitize_record (whitelist trường)
       -> assert_no_pii (CHẶN nếu nghi PII) -> (fit nếu TF-IDF) -> embed -> lưu store.

Nguồn hỗ trợ: EBM_MASTER.json hoặc file synthetic cùng cấu trúc {"evidence_cards":[...]}.
MẶC ĐỊNH dùng dữ liệu SYNTHETIC để demo — KHÔNG tự đụng dữ liệu thật.

Dùng:
    python3 ingest.py                         # demo trên sample_data/synthetic_evidence.json
    python3 ingest.py --source <path.json>    # nạp nguồn khác (vẫn qua cổng PII)

[PROTOTYPE — embedder mặc định = TF-IDF nếu có sklearn; KHÔNG chạy trên dữ liệu BN thật]
"""
from __future__ import annotations
import argparse, json, os, sys
from deidentify import sanitize_record, assert_no_pii, record_to_text, PiiDetectedError
from _backend import get_embedder, get_store, backend_info

# Windows: stdout mặc định cp1252 giết print() tiếng Việt — ép UTF-8 (chốt BH55/R4)
import sys as _sys_r4
for _s_r4 in (_sys_r4.stdout, _sys_r4.stderr):
    try:
        _s_r4.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

DEFAULT_SOURCE = os.path.join(os.path.dirname(__file__), "sample_data", "synthetic_evidence.json")


def load_cards(path: str):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "evidence_cards" in data:
        return data["evidence_cards"]
    if isinstance(data, list):
        return data
    raise ValueError("Nguồn phải có 'evidence_cards': [...] hoặc là list bản ghi.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=DEFAULT_SOURCE)
    args = ap.parse_args()

    print(f"[ingest] backend: {json.dumps(backend_info(), ensure_ascii=False)}")
    print(f"[ingest] nguồn  : {args.source}")
    cards = load_cards(args.source)

    clean_records, texts, rejected = [], [], []
    for raw in cards:
        rid = raw.get("id", "?")
        try:
            rec = sanitize_record(raw)
            assert_no_pii(rec)
        except PiiDetectedError as e:
            rejected.append((rid, str(e)))
            print(f"  ⛔ TỪ CHỐI {rid}: {e}")
            continue
        clean_records.append(rec)
        texts.append(record_to_text(rec))
        print(f"  ✅ NHẬN  {rid}: {rec.get('topic','')[:50]}")

    if not clean_records:
        print("[ingest] Không có bản ghi hợp lệ để nạp.")
        sys.exit(0)

    emb = get_embedder()
    # Backend có trạng thái (TF-IDF) cần học từ vựng/IDF từ corpus trước khi nhúng.
    # Hashing / sentence-transformers không có .fit -> bỏ qua an toàn.
    if hasattr(emb, "fit"):
        emb.fit(texts)
    vectors = emb.embed(texts)
    store = get_store()
    ids = [r["id"] for r in clean_records]
    store.upsert(ids=ids, vectors=vectors, metadatas=clean_records, documents=texts)

    print(f"\n[ingest] ĐÃ NẠP {len(clean_records)} bản ghi · TỪ CHỐI {len(rejected)} (PII). Embedder={emb.name}")
    print(f"[ingest] Store: {store.count()} bản ghi tại tools/rag/store/")
    print("[ingest] Lưu ý: chỉ metadata chứng cứ (PMID/DOI/chủ đề). KHÔNG có PII. Cần bác sĩ kiểm chứng.")


if __name__ == "__main__":
    main()
