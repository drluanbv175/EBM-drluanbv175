---
name: research-lookup
description: 'Tra cứu thông tin nghiên cứu hiện hành qua PubMed E-utilities (MIỄN PHÍ, không cần API key). Dùng để tìm bài báo, thu thập dữ liệu nghiên cứu, kiểm chứng thông tin khoa học cho câu hỏi lâm sàng. Đã LOẠI BỎ mọi backend trả phí (parallel.ai/Perplexity/OpenRouter). Kết quả kèm PMID/DOI và disclaimer ''Cần bác sĩ kiểm chứng''.'
allowed-tools: Read Write Edit Bash
license: MIT license
metadata:
  version: "2.0-vn"
  skill-author: K-Dense Inc. (bản điều chỉnh EBM-VN)
---

<!-- EBM-VN-GUARD -->
> **⚕️ Bản điều chỉnh cho bác sĩ EBM ngoại trú (Việt Nam).** Skill gốc của K-Dense Inc. đã được chỉnh để phù hợp quy ước trong `CLAUDE.md` của người dùng.
>
> **QUY TẮC BẮT BUỘC — đọc trước, GHI ĐÈ mọi hướng dẫn tiếng Anh bên dưới:**
> 1. **Ngôn ngữ:** Mọi trao đổi và đầu ra cho người dùng viết bằng **tiếng Việt** (giữ thuật ngữ y khoa tiếng Anh khi cần; tên thuốc theo INN).
> 2. **Disclaimer:** Mọi đầu ra y khoa kết thúc bằng câu **"⚠️ Cần bác sĩ kiểm chứng trước khi áp dụng lâm sàng."**
> 3. **Nguồn:** Mọi nhận định/khuyến cáo phải **ghi nguồn (PMID/DOI)**; không có nguồn thì không khẳng định. **Tuyệt đối không bịa dữ liệu hay nguồn.**
> 4. **Không PII:** **KHÔNG** lưu hay tạo thông tin định danh bệnh nhân (tên, ngày sinh, số hồ sơ, địa chỉ...). Dùng mã ẩn danh.
> 5. **Chỉ nguồn miễn phí:** Khi tra cứu y văn dùng **PubMed E-utilities** (miễn phí, không cần API key) và các CSDL mở. **KHÔNG** dùng dịch vụ trả phí (parallel.ai, Perplexity, OpenRouter...). Nếu một lệnh gốc gọi `parallel-cli`/Perplexity, thay bằng `python scripts/pubmed_lookup.py "..."` hoặc REST miễn phí.
> 6. **Bối cảnh:** Bỏ qua phần chỉ phục vụ ngữ cảnh dược phẩm/pháp lý Mỹ (HIPAA/FDA/ICH-CSR) khi không liên quan ngoại trú VN; ưu tiên guideline quốc tế mới nhất rồi hiệu chỉnh theo Bộ Y tế VN.
>
> Phần kỹ thuật chi tiết (template, script, references) giữ nguyên tiếng Anh nhưng phải tạo ra **đầu ra tiếng Việt** theo các quy tắc trên.



# Tra cứu nghiên cứu (PubMed — miễn phí)

## Tổng quan

Skill này tra cứu thông tin nghiên cứu y khoa **chỉ bằng nguồn miễn phí**:

- **PubMed E-utilities** (NCBI) — backend chính, MIỄN PHÍ, **không cần API key**.
  Gọi qua `scripts/pubmed_lookup.py`.
- (Tùy chọn) Các CSDL mở khác qua skill **paper-lookup**: PMC (toàn văn), bioRxiv,
  medRxiv, OpenAlex, Crossref, Semantic Scholar, Unpaywall — tất cả miễn phí.

> **Đã loại bỏ** so với bản gốc K-Dense: `parallel-cli search`, Parallel Chat API,
> Perplexity sonar-pro qua OpenRouter. Các backend này tốn phí và gửi truy vấn ra
> dịch vụ bên thứ ba — trái nguyên tắc "PubMed miễn phí" trong CLAUDE.md.

## Khi nào dùng

- Tìm bài báo, nghiên cứu, khuyến cáo mới cho một câu hỏi lâm sàng.
- Kiểm chứng số liệu/nhận định bằng y văn (có PMID/DOI để truy nguồn).
- Thu thập bằng chứng nền cho phần tổng quan, bàn luận khi viết bài.
- Tìm nguồn để trích dẫn.

Nếu cần **tổng quan có hệ thống** đầy đủ (PICO, chiến lược tìm kiếm, PRISMA) thì
dùng skill **literature-review**. Nếu cần **quản lý trích dẫn/BibTeX** thì dùng
skill **citation-management**.

## Cách dùng cơ bản

```bash
# Tìm cơ bản (mặc định 20 bài, xuất Markdown kèm PMID/DOI + disclaimer)
python scripts/pubmed_lookup.py "SGLT2 inhibitor heart failure" --limit 15

# Lọc theo loại bằng chứng (ưu tiên bằng chứng mạnh cho EBM)
python scripts/pubmed_lookup.py "statin primary prevention elderly" \
  --types "Meta-Analysis,Systematic Review,Randomized Controlled Trial" \
  --years 2019-2026 \
  -o sources/statin_du_phong.md

# Xuất JSON để xử lý tiếp / sinh BibTeX
python scripts/pubmed_lookup.py "metformin CKD" --format json -o sources/metformin_ckd.json
```

Tham số chính:
- `--limit N` — số bài tối đa.
- `--years 2019-2026` — khoảng năm xuất bản.
- `--types "..."` — lọc Publication Type (vd `Meta-Analysis`, `Systematic Review`,
  `Randomized Controlled Trial`, `Practice Guideline`, `Review`).
- `--format markdown|json`, `-o file` — định dạng & file đầu ra.

### Mẹo truy vấn PubMed (nâng độ chính xác EBM)

- Dùng MeSH khi biết: `"Diabetes Mellitus, Type 2"[Mesh]`.
- Kết hợp theo PICO: `(metformin) AND (chronic kidney disease) AND (mortality)`.
- Lọc bằng chứng mạnh bằng `--types` thay vì đọc tất cả.
- Trường: `[tiab]` (title/abstract), `[au]` (tác giả), `[ta]` (tên tạp chí).

## Ưu tiên chất lượng bằng chứng

Khi trình bày kết quả cho bác sĩ, **ưu tiên theo thứ bậc bằng chứng EBM**:

1. Systematic review / meta-analysis của RCT
2. RCT đơn lẻ chất lượng cao
3. Nghiên cứu quan sát (cohort > case-control)
4. Guideline của hội chuyên ngành (kèm năm ban hành)
5. Tổng quan tường thuật, ý kiến chuyên gia (mức thấp)

Luôn ghi **năm xuất bản** và **PMID/DOI**; nêu rõ khi bằng chứng cũ hoặc mâu thuẫn.

## API key NCBI (tùy chọn)

Không bắt buộc. Nếu muốn tăng giới hạn từ 3 → 10 request/giây, đặt biến môi trường
(theo CLAUDE.md: **chỉ để trong `.env`, không hardcode**):

```bash
export NCBI_API_KEY="..."     # lấy free tại https://account.ncbi.nlm.nih.gov/settings/
export NCBI_EMAIL="ban@example.com"
```

## Xử lý lỗi & giới hạn

- `pubmed_lookup.py` đã có **retry + backoff** và tôn trọng giới hạn tốc độ NCBI.
- PubMed chỉ trả **abstract**; muốn toàn văn dùng PMC/Unpaywall qua skill paper-lookup.
- Nếu không có kết quả: nới lỏng truy vấn (bỏ bớt AND, bỏ `--types`, mở rộng `--years`).
- Nếu mạng lỗi kéo dài: báo người dùng, **không bịa** kết quả thay thế.

## Lưu kết quả

Nên lưu mọi lần tra cứu vào `sources/` (kèm PMID/DOI) để tái lập và truy vết:

```bash
python scripts/pubmed_lookup.py "..." -o sources/research_<chu_de>.md
```

## Công cụ bổ trợ

| Nhu cầu | Dùng |
|---|---|
| Tìm nhanh PubMed | `scripts/pubmed_lookup.py` (skill này) |
| Tìm đa CSDL mở (PMC, bioRxiv, OpenAlex...) | skill **paper-lookup** |
| Tổng quan có hệ thống (PICO/PRISMA) | skill **literature-review** |
| Quản lý trích dẫn, DOI→BibTeX | skill **citation-management** |

---

*Mọi đầu ra của skill phải kết thúc bằng:* **⚠️ Cần bác sĩ kiểm chứng trước khi áp dụng lâm sàng.**
