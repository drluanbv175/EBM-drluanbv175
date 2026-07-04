# -*- coding: utf-8 -*-
"""
_backend.py — Lớp trừu tượng EMBEDDING + VECTOR STORE cho RAG chứng cứ.

BA backend embedder (tự dò, ưu tiên chất lượng -> tự lùi để LUÔN chạy được offline):
  (1) sentence-transformers  : embedding NGỮ NGHĨA thật (neural). Cần cài + tải model (~80MB).
  (2) scikit-learn TF-IDF    : vector hoá THỐNG KÊ-NGỮ NGHĨA NHẸ (bag-of-words có trọng số IDF
                               + cosine). Nhẹ, cài nhanh, KHÔNG cần torch/CUDA/mạng. <-- MỚI 2026-06-13.
  (3) hashing n-gram (numpy) : fallback CUỐI — chỉ để CHỨNG MINH LUỒNG khi không có gì khác.

Thứ tự ưu tiên get_embedder(): (1) -> (2) -> (3). Hiện sandbox: (1) vắng, (2) sẵn -> mặc định TF-IDF.

LIÊM CHÍNH — đặt tên cho đúng năng lực:
  - TF-IDF KHÔNG phải embedding neural; nó là biểu diễn TỪ VỰNG CÓ TRỌNG SỐ (lexical). Nó "ngữ nghĩa
    hơn" hashing vì: (a) loại nhiễu va-chạm băm; (b) IDF hạ trọng số từ phổ biến ("theo nguồn", "ở người")
    và nâng từ phân biệt -> tách hạng tốt hơn. Nhưng nó KHÔNG bắt được đồng nghĩa/ngữ cảnh như mô hình
    neural. Muốn ngữ nghĩa đầy đủ -> cài sentence-transformers (backend 1).

Mọi text đưa vào ĐÃ phải qua deidentify (gọi ở ingest.py). Lớp này không tự khử PII.

[PROTOTYPE — TF-IDF/hashing chạy được offline để demo; sản xuất cần BS duyệt governance + nguồn không-PII]
"""
from __future__ import annotations
import json, os, re, hashlib, pickle
from typing import List, Dict, Any
import numpy as np

STORE_DIR = os.path.join(os.path.dirname(__file__), "store")
FALLBACK_DIM = 512
TFIDF_STATE_PATH = os.path.join(STORE_DIR, "tfidf_vectorizer.pkl")


# ----------------------------- EMBEDDERS ----------------------------- #
class _HashingEmbedder:
    """Fallback offline: nhúng char 3-gram vào vector cố định + chuẩn hóa L2.
    Không 'hiểu nghĩa' như mô hình thật nhưng đủ để khớp từ/cụm gần giống -> demo luồng."""
    name = "fallback-hashing-ngram"
    dim = FALLBACK_DIM

    def embed(self, texts: List[str]) -> np.ndarray:
        vecs = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, t in enumerate(texts):
            t = (t or "").lower()
            toks = re.findall(r"\w+", t)
            grams = toks + [t[j:j+3] for j in range(max(0, len(t) - 2))]
            for g in grams:
                h = int(hashlib.md5(g.encode("utf-8")).hexdigest(), 16)
                vecs[i, h % self.dim] += 1.0
            n = np.linalg.norm(vecs[i])
            if n > 0:
                vecs[i] /= n
        return vecs


def _try_st_embedder():
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

        class _STEmbedder:
            name = "sentence-transformers/all-MiniLM-L6-v2"
            dim = model.get_sentence_embedding_dimension()
            def embed(self, texts):
                return np.asarray(model.encode(texts, normalize_embeddings=True), dtype=np.float32)
        return _STEmbedder()
    except Exception:
        return None


class _SklearnTfidfEmbedder:
    """Backend semantic NHẸ (mới): TF-IDF (sklearn) + cosine.

    Khác hashing: có TRẠNG THÁI (từ vựng + IDF học từ corpus). Vì vậy:
      - ingest gọi .fit(corpus) -> học từ vựng/IDF, LƯU vectorizer ra store/ (pickle).
      - query gọi .embed([q]) -> tự NẠP vectorizer đã fit từ store/ rồi transform.
    Vector trả ra đã chuẩn hoá L2 (TfidfVectorizer norm='l2') -> dot = cosine, khớp _JsonStore.

    Cấu hình: phân tích theo TỪ (tiếng Việt tách âm tiết theo dấu cách), n-gram (1,2),
    sublinear_tf=True (làm mượt tần suất). KHÔNG cắt stopword cứng (corpus nhỏ, IDF tự lo).
    """
    name = "sklearn-tfidf"

    def __init__(self):
        self._vec = None  # TfidfVectorizer đã fit (hoặc None)
        # Lazy-load nếu đã có state trên đĩa (cho tiến trình query tách rời tiến trình ingest).
        if os.path.exists(TFIDF_STATE_PATH):
            try:
                with open(TFIDF_STATE_PATH, "rb") as f:
                    self._vec = pickle.load(f)
            except Exception:
                self._vec = None

    @property
    def dim(self):
        if self._vec is not None and hasattr(self._vec, "vocabulary_"):
            return len(self._vec.vocabulary_)
        return 0  # chưa fit

    def fit(self, texts: List[str]):
        from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
        self._vec = TfidfVectorizer(
            analyzer="word", ngram_range=(1, 2), min_df=1,
            sublinear_tf=True, norm="l2", lowercase=True,
        )
        self._vec.fit(texts)
        os.makedirs(STORE_DIR, exist_ok=True)
        with open(TFIDF_STATE_PATH, "wb") as f:
            pickle.dump(self._vec, f)
        return self

    def embed(self, texts: List[str]) -> np.ndarray:
        if self._vec is None:
            # Tiến trình query nhưng chưa có state -> hướng dẫn chạy ingest.
            if os.path.exists(TFIDF_STATE_PATH):
                with open(TFIDF_STATE_PATH, "rb") as f:
                    self._vec = pickle.load(f)
            else:
                raise RuntimeError(
                    "TF-IDF chưa được fit. Chạy ingest.py trước (ingest sẽ fit + lưu từ vựng)."
                )
        return np.asarray(self._vec.transform(texts).todense(), dtype=np.float32)


def _try_sklearn_tfidf():
    try:
        import sklearn  # noqa: F401  (chỉ kiểm tra có cài không)
        return _SklearnTfidfEmbedder()
    except Exception:
        return None


def get_embedder(prefer: str | None = None):
    """Trả embedder theo ưu tiên: sentence-transformers -> sklearn TF-IDF -> hashing.

    prefer: ép chọn 1 backend để SO SÁNH/kiểm thử ('st' | 'tfidf' | 'hashing').
    """
    if prefer == "hashing":
        return _HashingEmbedder()
    if prefer == "tfidf":
        return _try_sklearn_tfidf() or _HashingEmbedder()
    if prefer == "st":
        return _try_st_embedder() or _HashingEmbedder()
    return _try_st_embedder() or _try_sklearn_tfidf() or _HashingEmbedder()


# ----------------------------- STORES ----------------------------- #
def _try_chroma():
    try:
        import chromadb  # type: ignore
        client = chromadb.PersistentClient(path=os.path.join(STORE_DIR, "chroma"))
        return client
    except Exception:
        return None


class _JsonStore:
    """Fallback store: lưu vectors (.npy) + metadata (.json) trong store/."""
    backend = "fallback-json"
    def __init__(self):
        os.makedirs(STORE_DIR, exist_ok=True)
        self.vec_path = os.path.join(STORE_DIR, "vectors.npy")
        self.meta_path = os.path.join(STORE_DIR, "records.json")

    def upsert(self, ids, vectors, metadatas, documents):
        np.save(self.vec_path, np.asarray(vectors, dtype=np.float32))
        payload = [{"id": i, "metadata": m, "document": d}
                   for i, m, d in zip(ids, metadatas, documents)]
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=1)

    def query(self, query_vec, n_results=5):
        if not (os.path.exists(self.vec_path) and os.path.exists(self.meta_path)):
            raise FileNotFoundError("Store rỗng — chạy ingest.py trước.")
        vectors = np.load(self.vec_path)
        with open(self.meta_path, encoding="utf-8") as f:
            payload = json.load(f)
        sims = vectors @ np.asarray(query_vec, dtype=np.float32).ravel()
        order = np.argsort(-sims)[:n_results]
        return [(payload[k], float(sims[k])) for k in order]

    def count(self):
        if not os.path.exists(self.meta_path):
            return 0
        with open(self.meta_path, encoding="utf-8") as f:
            return len(json.load(f))


def get_store():
    """Hiện tại trả JsonStore (offline-safe). Nếu cài chromadb, có thể mở rộng dùng Chroma.
    Giữ JsonStore làm mặc định để demo chạy không cần deps."""
    # Ghi chú: bản prototype dùng JsonStore cho mọi backend embedder để demo offline ổn định.
    # Khi vận hành thật + đã cài chromadb, thay bằng adapter Chroma (xem README §Nâng cấp).
    return _JsonStore()


def backend_info() -> Dict[str, Any]:
    emb = get_embedder()
    chroma = "có (chromadb import được)" if _try_chroma() else "KHÔNG (dùng fallback JSON)"
    dim = emb.dim
    dim_note = dim if dim else "—(TF-IDF: dim = kích thước từ vựng, có sau khi ingest fit)"
    return {"embedder": emb.name, "embed_dim": dim_note, "chroma": chroma,
            "store": get_store().backend}


if __name__ == "__main__":
    print("Backend hiện tại:", json.dumps(backend_info(), ensure_ascii=False))
