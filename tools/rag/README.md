# tools/rag — BỘ NHỚ VECTOR + RAG cho METADATA CHỨNG CỨ (Hạng mục B)

**[PROTOTYPE — cần cài deps + BS duyệt governance trước khi chạy trên dữ liệu thật]**

Prototype truy xuất ngữ nghĩa (semantic retrieval) trên **metadata chứng cứ** của sổ cái EBM
(`EBM_MASTER.json`): chủ đề · PICO · khuyến cáo · độ chắc · **PMID/DOI**. Mục tiêu: vượt "trần"
tra cứu khóa-từ hiện tại bằng tìm kiếm theo NGỮ NGHĨA, nhưng giữ nguyên rào liêm chính.

## BA BACKEND embedder (ưu tiên giảm dần — tự dò, tự lùi để LUÔN chạy được)
| # | Backend | Bản chất | Cần gì | Chất lượng |
|---|---------|----------|--------|-----------|
| 1 | `sentence-transformers` | Embedding NGỮ NGHĨA thật (neural) | cài deps + tải model ~80MB | cao nhất (bắt đồng nghĩa/ngữ cảnh) |
| 2 | **`sklearn-tfidf` (MỚI 2026-06-13)** | TF-IDF + cosine — biểu diễn **từ vựng có trọng số IDF** | `pip install scikit-learn` (nhẹ, **KHÔNG cần torch/CUDA**) | trung bình — tách hạng tốt hơn hashing |
| 3 | `fallback-hashing-ngram` | Băm char/word n-gram vào vector numpy | chỉ cần numpy | thấp nhất — chỉ để CHỨNG MINH LUỒNG |

`get_embedder()` chọn (1)→(2)→(3). Sandbox hiện tại: (1) vắng, (2) đã cài ⇒ **mặc định TF-IDF**.

> **Liêm chính — gọi đúng tên năng lực:** TF-IDF **KHÔNG** phải embedding neural; nó là biểu diễn
> *lexical có trọng số*. Nó "ngữ nghĩa hơn" hashing vì (a) loại nhiễu va-chạm băm, (b) IDF hạ trọng số
> từ phổ biến ("theo nguồn", "ở người") và nâng từ phân biệt ⇒ tách thẻ liên quan rõ hơn. Nhưng nó
> **không** bắt được đồng nghĩa/ngữ cảnh như mô hình neural — muốn vậy phải cài backend (1).

## ⛔ CẢNH BÁO PII & GOVERNANCE (đọc trước khi dùng)
- RAG này **CHỈ** nhận **metadata chứng cứ**. **TUYỆT ĐỐI KHÔNG** ingest dữ liệu định danh
  bệnh nhân (tên, ngày sinh, CCCD/CMND, BHYT, SĐT, địa chỉ, MRN, ảnh nhận dạng…).
- Mọi bản ghi **bắt buộc** qua `deidentify.py`: (1) whitelist trường schema; (2) `assert_no_pii()`
  quét free-text — **nghi PII là DỪNG, từ chối ingest** (đã chứng minh trong demo).
- Kết quả truy vấn là **GỢI Ý truy xuất**, KHÔNG phải kết luận. **Bắt buộc đối chiếu PMID/DOI**
  qua agent `kiem-chung-trich-dan` để chống **trích dẫn ảo** trước khi dùng.
- Không thay phán đoán lâm sàng. Kết mọi đầu ra: **"Cần bác sĩ kiểm chứng."**

## File
| File | Vai trò |
|---|---|
| `deidentify.py` | Khử PII + **cổng chặn** `assert_no_pii` (whitelist trường + regex SĐT/CCCD/BHYT/email/DOB/MRN/tên). |
| `_backend.py` | Lớp embedder + store. Tự dò 3 backend: ST → **sklearn TF-IDF** → hashing; store JSON/npy (Chroma để mở rộng). |
| `ingest.py` | Đọc nguồn → sanitize → assert_no_pii → (fit nếu TF-IDF) → embed → lưu `store/`. Mặc định: dữ liệu **synthetic**. |
| `query.py` | Truy vấn ngữ nghĩa → top-k bản ghi + PMID/DOI để kiểm chứng. |
| `compare_backends.py` | **(MỚI)** So sánh xếp hạng TF-IDF vs hashing trên synthetic (top-1 · MRR · margin) để chứng minh tách hạng tốt hơn. |
| `sample_data/synthetic_evidence.json` | 3 bản ghi MẪU TỔNG HỢP + 1 bản ghi **dính PII cố ý** (để kiểm cổng chặn). |
| `requirements.txt` | Phụ thuộc theo backend (fallback chỉ cần numpy; TF-IDF cần scikit-learn; ST cần sentence-transformers). |
| `store/` | Nơi lưu vectors + records + `tfidf_vectorizer.pkl` (từ vựng/IDF đã fit; tạo khi chạy ingest). |

## Chạy demo
```bash
cd tools/rag
python3 deidentify.py     # tự kiểm cổng PII (PASS bản sạch / CHẶN bản bẩn)
python3 ingest.py         # nạp 3 synthetic, TỪ CHỐI 1 bản PII (mặc định embedder = TF-IDF nếu có sklearn)
python3 query.py "thuốc nào giảm nhập viện suy tim ở đái tháo đường" --k 3
python3 compare_backends.py   # SO SÁNH TF-IDF vs hashing (top-1 · MRR · margin)
```
**Kết quả demo đã chạy thật trong sandbox (synthetic):**
- `ingest`: nhận 3 / từ chối 1 (PII: tên BN/SĐT+CCCD+DOB). Embedder mặc định `sklearn-tfidf`.
- `compare_backends` (3 truy vấn diễn đạt KHÁC chữ trong thẻ): **cả hai** backend top-1 đúng 3/3, MRR=1.000,
  nhưng **margin tách hạng TB: TF-IDF 0.299 vs hashing 0.135** — TF-IDF đẩy thẻ không liên quan về ~0
  (nhờ IDF), trong khi hashing vẫn gán điểm ~0.29 cho thẻ không liên quan (nhiễu va-chạm băm).
  ⇒ TF-IDF **tách hạng rõ hơn ~2,2×**. (Số nhỏ vì corpus chỉ 3 thẻ synthetic; KHÔNG phải benchmark chuẩn.)

## Chọn backend / nâng cấp chất lượng
- **TF-IDF (mặc định khi có sklearn):** `pip install --break-system-packages scikit-learn` — nhẹ, không cần torch.
- **Ngữ nghĩa đầy đủ (neural):** cài thêm `sentence-transformers` (xem `requirements.txt`) → `_backend.py`
  tự ưu tiên model `all-MiniLM-L6-v2` (local, miễn phí).
- **Ép chọn backend để kiểm thử:** `get_embedder(prefer="tfidf"|"hashing"|"st")`.
- **Nâng cấp Chroma:** sau khi `pip install chromadb`, thay `get_store()` trả adapter Chroma
  (`PersistentClient(path=store/chroma)`) — khung đã chừa sẵn ở `_backend._try_chroma()`.

## Nạp từ sổ cái thật (CHỈ sau khi BS duyệt governance)
```bash
python3 ingest.py --source "../../EBM_MASTER/EBM_MASTER.json"
```
`ingest.py` chỉ lấy các trường trong `ALLOWED_FIELDS`/`ALLOWED_SOURCE_KEYS`; mọi trường khác bị loại,
mọi bản ghi nghi PII bị từ chối. Dù vậy, **chỉ chạy trên dữ liệu thật khi**: (1) xác nhận sổ cái
không chứa PII; (2) bác sĩ duyệt; (3) đã rà điều kiện ở `_LO-TRINH-HA-TANG.md` §1.

## Trạng thái
Prototype **CHẠY ĐƯỢC & FUNCTIONAL HƠN** — đã có backend semantic NHẸ (TF-IDF) chạy thật trên synthetic,
tách hạng tốt hơn hashing (demo ở trên). **CHƯA vận hành trên dữ liệu thật.**
Điều kiện vận hành: (1) BS duyệt governance; (2) xác nhận nguồn không-PII; (3) (tùy chọn) cài
`sentence-transformers` cho ngữ nghĩa đầy đủ. Rào liêm chính/PII **không đổi**.
