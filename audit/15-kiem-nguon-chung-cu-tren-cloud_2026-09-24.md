# Kiểm nguồn chứng cứ TRÊN CLOUD — đồng bộ, độ phủ, hoạt động thật (24/09/2026)

> Câu hỏi của bác sĩ: «các nguồn chứng cứ trên Cloud đã đồng bộ với hệ thống tôi xây dựng chưa,
> đã được phủ và hoạt động tốt nhất chưa». Mọi số dưới đây là **đo trực tiếp trong phiên Cloud
> này** (container `anthropic_cloud`, môi trường «Default — trusted network access»), bằng chính
> công cụ của hệ (`run.py test-live`, `RSSFeedClient`, `RetractionChain`, `sources_health.py`
> chạy trên BẢN SAO sổ, canary, máy chấm Gold Set) và bằng connector MCP của phiên. Nối tiếp
> `audit/13` + `audit/14` (23/09, đo từ Mac — đang nằm trong PR #21 chưa hợp nhất). Cần bác sĩ
> kiểm chứng.

## 1. Kết luận ngắn

1. **Mã engine (repo y khoa): ĐỒNG BỘ.** Cloud đứng đúng HEAD nhánh mặc định
   `feat/r1-1-2-design-gap-remediation` (`ee03e75`, 23/09) — có đủ connector mới 23/09.
2. **Repo gốc: CHƯA đồng bộ.** Toàn bộ việc nguồn chứng cứ 22–23/09 (24 commit: sổ nguồn 21→36
   mục, vá đường dẫn engine của bộ quét tuần, nối CORE + bậc thang dự phòng, doctrine agent,
   audit/13–14) nằm ở **PR #21 — mở, CI 4/4 xanh, `mergeable: clean`, chưa hợp nhất**. Cloud
   clone `master` nên KHÔNG có những thứ đó.
3. **Engine Python trên Cloud hiện «mù»:** mạng môi trường chặn MỌI host API y văn (proxy trả
   403 theo chính sách) và container không có `~/.ebm-secrets` ⇒ chế độ MOCK. Chỉ PMC toàn văn
   (S3) và — sau bản vá hôm nay — nền Retraction Watch là chạy thật được.
4. **Connector MCP trên Cloud: CHẠY TỐT** (không đi qua allowlist mạng): PubMed, ClinicalTrials,
   Scite, Wiley, Amass ✅; bioRxiv ❌ (lỗi phía máy chủ); Cochrane không có trên Cloud (thiết kế).
5. **Chính hệ kiểm của bác sĩ có 6 chỗ hỏng RIÊNG trên Cloud** (ghi đè log bằng chứng mỗi phiên,
   canary chết, 3 chốt đỏ giả, dòng đỏ bị hook giấu) — **đã vá + kiểm đột biến** (mục 6).

## 2. Đồng bộ mã nguồn Cloud ↔ hệ thống

| Repo | Cloud đứng ở | Nhánh mặc định / PR | Lệch |
|---|---|---|---|
| `medical-ebm-automation` | `ee03e75` (23/09 19:41) | `feat/r1-1-2-design-gap-remediation` = `ee03e75` | **0** |
| `EBM-drluanbv175` | `371dd1e` = `master` (22/09 15:25) | **PR #21** `claude/multi-platform-plugin-sync-cslwb0` — +24 commit, CI 4/4 xanh, mergeable clean | **24 commit chưa vào master** |

Hệ quả đo được của việc PR #21 chưa hợp nhất:

| Thứ | Trên `master` (Cloud) | Trong PR #21 |
|---|---|---|
| `data/sources.json` | 21 nguồn (18 active · 3 not-covered) | 36 nguồn (29 active · 3 degraded · 4 not-covered) |
| SRC-032…046 (Scopus, CORE, Consensus, SerpApi, Epistemonikos, NICE, Cochrane MCP, Semantic Scholar, Scite, Wiley MCP, Wiley TDM, GOLD, GINA, BTS, PMC) | **vắng** — dù `medical-ebm-automation/CLAUDE.md` (đã có trên Cloud) ghi là «đã đăng ký» | có |
| Bộ quét tuần bản vendor `sync/skills/*/tools/surveillance_scan.py` | `parents[2]` trỏ SAI gốc engine ⇒ **kiểm rút bài lúc nhận + làn Scopus im lặng bỏ qua** khi chạy từ bản vendor (Cloud/CI) | đã vá |
| Bằng chứng thực nghiệm | canary trên Cloud với scanner của `master`: ✗ «PMID 30267080 → `chua_kiem`» | cùng canary, thay đúng file scanner của PR #21: **🟢 13/13 kiểm được đều bắt** |
| Doctrine gọi `guideline_citation_summary.py` (công cụ đã có trên Cloud) | chưa agent nào được dạy (BH41: công cụ mồ côi) | đã dạy `tra-cuu-chung-cu` + `huong-dan-lam-sang` |

Các nhánh cũ khác của hai repo đều cũ hơn nhánh mặc định — không có việc nào khác bị kẹt.

## 3. Môi trường Cloud: mạng, bí mật, Python

- Môi trường duy nhất: **Default — Trusted network access**. Danh sách Trusted chỉ gồm kho gói,
  GitHub/GitLab, SDK đám mây (`*.amazonaws.com`, `*.googleapis.com`…) — **không có host y văn nào**.
- Proxy ghi nhận `connect_rejected` (403 chính sách) cho: `api.crossref.org`, `www.ebi.ac.uk`,
  `clinicaltrials.gov`, `api.openalex.org`, `api.semanticscholar.org`, `api.fda.gov`,
  `api.core.ac.uk` — cùng mọi host feed/lane (mục 4).
- Không có `~/.ebm-secrets` ⇒ `USE_MOCK_SOURCES=true`, `NCBI_EMAIL` rỗng
  (`tools/kiem_nguon_that.py`: 🔴 «CHỨNG CỨ KHÔNG ĐÁNG TIN Ở MÁY NÀY»).
- Python mặc định 3.11, nhưng `requirements.lock.txt` ghim `scipy==1.18.0` (cần ≥3.12) ⇒ `pip
  install` thất bại; phải `python3.12 -m venv`. Hook mở phiên chỉ cài python-docx/bs4/lxml (có chủ
  ý), nên engine không nạp được nếu không tự dựng venv.
- Phiên 2 repo: hook mở phiên KHÔNG tự bắn (BH103) — đã chạy tay đầu phiên.

## 4. Đo sống từng nguồn của engine Python (từ Cloud)

| Nguồn | Kết quả | Nguyên nhân |
|---|---|---|
| PubMed | 2 bản ghi **MOCK** (đầu ra cũ vẫn ghi `live: true`) | thiếu `NCBI_EMAIL` ⇒ tự lùi mock; host cũng bị chặn |
| Europe PMC · Crossref · ClinicalTrials.gov · OpenAlex · Semantic Scholar · openFDA · CORE | 0 bản ghi, **mỗi nguồn ≈ 48 giây** | proxy 403 bị coi là lỗi tạm thời ⇒ retry 4 lần vô ích |
| Scopus · Epistemonikos · SerpApi · Consensus | dừng ngay, không gửi request | thiếu khoá — fail-fast đúng thiết kế, không tốn hạn mức |
| 111 feed/lane guideline (31 Crossref-ISSN · 42 Crossref-tiêu đề · 10 Europe PMC · 24 RSS · WHO IRIS · BYT) | **0/111** trả bài | proxy 403 |
| PMC toàn văn qua S3 (SRC-046) | ✅ PMC13555224 → 200.000 ký tự | `*.amazonaws.com` thuộc Trusted |
| Nền Retraction Watch ngoại tuyến | trước vá: **không tải được** (host Crossref bị chặn + không email) → sau vá: ✅ **72.606 dòng · 31.511 PMID** qua gương GitLab chính thức của Crossref | `gitlab.com` thuộc Trusted |
| Chuỗi rút bài 3 tầng | trước: 0 tầng chạy → sau: Wakefield 9500320 `retracted`; Choi 30267080 `retracted` + `retract_and_replace` | tầng ① ngoại tuyến sống lại |

`sources_health.py` chạy trên BẢN SAO sổ (không đụng file tracked): sổ `master` → 7 nguồn API
BROKEN; sổ PR #21 → 10 degraded/broken — **do môi trường, không phải nguồn hỏng**. Công cụ này
GHI trạng thái ngược vào `data/sources.json`; chạy trên Cloud rồi commit sẽ làm bẩn sổ dùng chung
(xem mục 8).

## 5. Connector MCP của phiên Cloud (đi qua máy chủ Anthropic, không qua allowlist)

| Connector | Kết quả | Ghi chú |
|---|---|---|
| PubMed | ✅ | 9500320 mang «Retracted Publication»; **30267080 KHÔNG được PubMed gắn cờ** — đúng lý do tầng Retraction Watch là bắt buộc |
| ClinicalTrials.gov | ✅ | 128 thử nghiệm «heart failure + dapagliflozin» |
| Scite | ✅ | `editorialNotices`: retracted 2010-02-06 (Wakefield) |
| Wiley (Scholar Gateway) | ✅ | 3 đoạn toàn văn; kho cập nhật 09/2026 |
| Amass | ✅ | |
| bioRxiv/medRxiv | ❌ 2/2 lần | máy chủ MCP trả không phải JSON — `/tra-preprint` đang hỏng |
| Consensus | có mặt, **không gọi thử** | giữ hạn mức Free 30 lượt/tháng dùng chung REST (doctrine ≤2 lượt/câu hỏi) |
| Cochrane (SRC-038) | không có trên Cloud | plugin điều khiển trình duyệt — sổ khai ghi «chưa cài trên Cloud»; Cloud vẫn tra được Cochrane qua PubMed MCP |

## 6. Lỗi của CHÍNH hệ kiểm trên Cloud — đã vá trong phiên này

| # | Lỗi (đo thật) | Vá | Kiểm |
|---|---|---|---|
| 1 | **Mỗi phiên Cloud ghi đè 3 log bằng chứng tracked**: hook ⑤ → chốt BH102 → `quality/eval/run_eval.py` làm RỖNG `canary-10-loi-gai.log`, đổi Wakefield/Choi từ `retracted` sang `unknown_mock_or_no_email` trong `rut-bai-3-muc.log` (đúng ca BH94 ngày 02/09). Pre-commit chặn được — nhưng clone Cloud **không có `core.hooksPath`** nên chốt đó không chạy | trên bản sao trần, log âm tính ghi vào `reports/eval-negative-ban-sao-tran/` (gitignore); máy thật giữ nguyên | đột biến «ghi thẳng» ⇒ BH102 đỏ «GHI ĐÈ log bằng chứng tracked»; khôi phục ⇒ băm 5 log khớp |
| 2 | Canary chết vì `cryptography` hệ thống cài hỏng (`pyo3 PanicException` — BaseException, lọt `except ImportError`) ⇒ stdout rỗng ⇒ máy chấm ghi «CÓ LỖ HỔNG» | dò riêng bước nhập, bắt BaseException (ném lại KeyboardInterrupt/SystemExit) ⇒ ⚪ có khai báo; lỗi trong vòng ký-xác minh vẫn lộ | đột biến ⇒ lại traceback, không dòng tổng; venv lành vẫn chạy ed1 thật (`ed1:role:…`) |
| 3 | Canary/Gold Set đọc «chưa có nền RW» thành «lỗ hổng THẬT»/TRƯỢT | ⚪/◌ CHỈ khi nền RW vắng **và** trạng thái `chua_kiem`/`unknown_*`; tầng sống trả «ok» cho 30267080 vẫn ✗ | ẩn nền RW: 🟢 12/12 + ⚪ 2, Gold Set 9/9 + ◌; đột biến ⇒ ✗ trở lại |
| 4 | BH88, BH108 **đỏ giả** trên Cloud (ghép cứng `REPO/"medical-ebm-automation"`, engine là anh em) | dùng `_goc_mea()` | cả hai ✓ |
| 5 | BH102 đòi «mã 2» — lệch quyết định Gap-2 ngày 17/09, đỏ ở mọi phiên Cloud từ đó | hợp đồng mới: mã ∈ {0,2}, không traceback, **không ghi đè log tracked** | nay chỉ đỏ vì lý do THẬT (scanner `master`, mục 2) — hết đỏ khi PR #21 vào |
| 6 | Hook Cloud cắt `\| head -20` mà `--im-khi-on` in đủ 114 dòng rồi mới tới tổng kết ⇒ 3 chốt đỏ **chưa từng hiện** | `--im-khi-on` in tổng + mục đỏ LÊN ĐẦU | kiểm mắt: dòng đỏ nằm trong 7 dòng đầu |

Repo y khoa (engine):

| # | Lỗi | Vá | Kiểm |
|---|---|---|---|
| 7 | Proxy 403/407 bị retry ≈48 s/lần gọi (7 nguồn × 48 s mỗi lượt `test-live`; vòng quét tuần hàng giờ) | `HttpClient` bỏ NGAY khi `ProxyError` + «Tunnel connection failed: 403/407», thông điệp nêu host + chỗ sửa; ProxyError khác vẫn retry | 6 test; đột biến ⇒ 2 đỏ đúng chỗ |
| 8 | `test-live` ghi `live: true` cho bản ghi MOCK; lỗi mạng bị nuốt thành `count: 0` câm | `live` chỉ True khi 0 bản ghi mock, thêm `so_ban_ghi_mock`/`canh_bao`/`loi_goi_mang` | 2 test mới + 2 test SerpApi cũ vẫn đạt |
| 9 | Nền Retraction Watch không tải được trên Cloud (host bị chặn, không email) | `tools/tai_retraction_watch.py` thêm gương GitLab chính thức của Crossref (không cần email), thử tuần tự, cùng cổng schema + ≥1000 dòng, meta không chứa email | 7 test; 2 đột biến đều đỏ; chạy thật ✅ |

## 7. Việc CỦA BÁC SĨ — theo thứ tự lợi ích

1. **Hợp nhất PR #21** (repo gốc) — Cloud nhận sổ 36 nguồn, bộ quét tuần có kiểm rút bài lúc nhận,
   doctrine mới; BH102 xanh. (Agent không được tự merge.)
2. **Sửa môi trường Cloud** (menu môi trường ở thanh tiêu đề phiên → Edit; áp cho phiên MỚI):
   - *Network access* → **Custom**, tick «Also include default list», thêm:
     ```
     *.nlm.nih.gov
     *.ebi.ac.uk
     api.crossref.org
     api.labs.crossref.org
     api.openalex.org
     clinicaltrials.gov
     api.fda.gov
     api.semanticscholar.org
     api.unpaywall.org
     api.core.ac.uk
     api.scite.ai
     www.ema.europa.eu
     iris.who.int
     kcb.vn
     goldcopd.org
     ginasthma.org
     kdigo.org
     easl.eu
     www.aasld.org
     tools.cdc.gov
     www.ecdc.europa.eu
     www.nejm.org
     jamanetwork.com
     journals.plos.org
     www.jacc.org
     bjgp.org
     *.bmj.com
     doi.org
     ```
     (chỉ khi có khoá: `api.elsevier.com` · `serpapi.com` · `api.consensus.app` · `api.epistemonikos.org`)
   - *Environment variables*: `USE_MOCK_SOURCES=false`, `NCBI_EMAIL=<email>` (+ `ENABLE_CORE=true`
     nếu muốn). Biến môi trường ai dùng môi trường đó cũng đọc được.
   - *Khoá API*: từ 24/09 (chiều) DÙNG ĐƯỢC «API credentials» — xem §7ter. Quyết định đưa khoá
     lên Cloud là của bác sĩ; **không dán khoá vào khung chat**.
   - *Setup script* (tuỳ chọn, được cache ~7 ngày): dựng `python3.12 -m venv` + cài
     `requirements.lock.txt` + `python tools/tai_retraction_watch.py --nguon gitlab`.
3. **Bật chốt pre-commit trên Cloud**: thêm `git config core.hooksPath .githooks` vào hook mở phiên
   Cloud (tệp hook được bảo vệ — agent không sửa được).
4. **bioRxiv MCP**: kiểm lại trạng thái connector trong cài đặt connector claude.ai.

## 7bis. Cập nhật sau khi hợp nhất PR #21 · #22 · medical-ebm-automation#4 (24/09/2026, chiều)

Ba PR đã hợp nhất theo yêu cầu bác sĩ; việc 1 ở §7 xong. Vá thêm (repo gốc):

| # | Chỗ chưa hoàn thiện | Vá | Kiểm |
|---|---|---|---|
| 10 | `tools/sources_health.py` đọc 403 của PROXY thành nguồn hỏng và GHI DEGRADED vào sổ tracked từ mọi máy (§8 cũ); còn báo SRC-003 BROKEN trên Cloud dù nền RW có mặt (ghép cứng đường lồng) | proxy từ chối theo chính sách = ⚪ «không đo được», giữ nguyên `status`; phiên Cloud KHÔNG ghi sổ (`--khong-ghi` ép ở máy khác); nguồn `medical-ebm-automation/…` phân giải qua `duong_goc()` | 6 test; 3 đột biến đều đỏ; chạy thật trên Cloud: băm sổ không đổi, 7 nguồn ⚪ |
| 11 | Nền Retraction Watch là tệp gitignore ⇒ container Cloud mới không bao giờ có, dù công cụ tải đã chạy được (vá #9) — không ai gọi nó (BH41) | `tools/nap_nen_rut_bai_cloud.py` nối vào `tu_sua_chua.py::VIEC_MAY` (`chay_tren_cloud=True`) ⇒ hook Cloud ⑤b tự nạp; máy thật no-op | 6 test; 2 đột biến đều đỏ; chạy thật: dời nền đi → `tu_sua_chua --pham-vi-cloud --ap-dung` nạp lại trong 7,8 giây |
| 12 | `/tra-preprint` ghi cứng tên công cụ plugin Mac `mcp__plugin_bio-research_biorxiv__*` — trên Cloud connector là `mcp__bioRxiv__*` ⇒ bước 1 không nạp được | lệnh thử cả hai tên; lời gọi dữ liệu lỗi ⇒ báo «kênh preprint hỏng», cấm đọc thành «không có preprint» | đo lại bioRxiv MCP: `get_categories` ✅, `search_preprints` ❌ (lần 3) — lỗi phía máy chủ connector |
| 13 | Doctrine `_CONNECTOR-CHUNG-CU.md` chỉ liệt tiền tố plugin Mac; agent trên Cloud dễ kết luận «connector không có» | thêm khối «Tên công cụ đổi theo nơi chạy» (PubMed · Clinical_Trials · bioRxiv · Consensus · Scite · ChEMBL · ICD-10) + luật PARTIAL khi máy chủ connector lỗi; chép sang bản in-repo của engine (tệp `_` ngoài manifest) | `sync_agents_to_codex --check` sạch |

**Setup script đề xuất cho môi trường Cloud** (bác sĩ dán ở Edit → Setup script; `[CẦN KIỂM CHỨNG]`
— chưa chạy được trong ngữ cảnh setup thật, vì agent không sửa được môi trường; chỉ kiểm cú pháp):

```bash
#!/bin/bash
# Dựng venv Python 3.12 cho engine (requirements.lock.txt ghim scipy 1.18.0, cần >= 3.12).
# Không có repo/python3.12 lúc chạy ⇒ bỏ qua, không làm hỏng phiên.
for R in /home/user/medical-ebm-automation "$HOME/medical-ebm-automation"; do
  [ -f "$R/requirements.lock.txt" ] || continue
  command -v python3.12 >/dev/null 2>&1 || break
  if ! "$HOME/.ebm-venv/bin/python" -c 'import sys; sys.exit(sys.version_info < (3, 12))' 2>/dev/null; then
    python3.12 -m venv --clear "$HOME/.ebm-venv" && \
      "$HOME/.ebm-venv/bin/pip" install -q -r "$R/requirements.lock.txt"
  fi
  break
done
exit 0
```

Nền Retraction Watch KHÔNG cần đưa vào setup script nữa — hook Cloud tự nạp (vá #11).

## 7ter. Khai khoá API bằng «API credentials» (24/09/2026, chiều)

**Vì sao cần sửa mã:** proxy của môi trường gắn khoá vào HEADER sau khi request rời sandbox — engine
không bao giờ thấy khoá. Trước bản vá, connector thấy biến khoá rỗng liền tự dừng («thiếu …_API_KEY»).
Nay biến KHÔNG bí mật `KHOA_QUA_PROXY` báo cho engine biết nguồn nào có khoá do proxy gắn
(`app/config.py::khoa_do_proxy_gan`); nguồn đó không bị chặn và không gửi header khoá rỗng.

**Chỉ dùng được với nguồn gửi khoá qua HEADER:**

| Nguồn | Allowed websites | Custom header — Name | Prefix | Ghi vào `KHOA_QUA_PROXY` |
|---|---|---|---|---|
| Scopus | `api.elsevier.com` | `X-ELS-APIKey` | *(xoá trống)* | `scopus` |
| CORE | `api.core.ac.uk` | `Authorization` | `Bearer` | `core` |
| Consensus | `api.consensus.app` | `x-api-key` | *(xoá trống)* | `consensus` |
| Epistemonikos | `api.epistemonikos.org` | `Authorization` | `Token` — Value nhập dạng `token="<token>"` `[CẦN KIỂM CHỨNG]` | `epistemonikos` |
| Semantic Scholar | `api.semanticscholar.org` | `x-api-key` | *(xoá trống)* | `semantic_scholar` |

**KHÔNG dùng được** (gửi khoá qua tham số URL, proxy không gắn): SerpApi · NCBI/PubMed · openFDA —
muốn dùng trên Cloud thì đặt ở *Environment variables* thường (ai dùng môi trường cũng đọc được).
NCBI và openFDA vẫn chạy không khoá, chỉ nhịp thấp hơn.

**Các bước (bác sĩ tự làm; máy tính, claude.ai/code):**
1. Nút đám mây trên ô nhập → rê chuột lên **Default** → bánh răng → hộp **Update cloud environment**.
2. Mục **API credentials** (dưới Environment variables) → **Add credential**, giữ Credential type **Bearer**.
3. Điền **Name** (vd `Scopus`), **Allowed websites** và **Custom headers** theo bảng trên; dán khoá vào
   **Value** — trên màn hình đó, KHÔNG dán vào khung chat.
4. Bấm **Connect** (credential lưu ngay, không cần Save changes). Lặp lại cho từng nguồn.
5. Ở **Environment variables** thêm một dòng, ví dụ `KHOA_QUA_PROXY=scopus,core,consensus` (chỉ ghi
   nguồn đã khai), cùng cờ bật nguồn: `ENABLE_SCOPUS=true`, `ENABLE_CORE=true`, `ENABLE_CONSENSUS=true`…
   rồi **Save changes**.
6. Mở phiên MỚI, nhắn «đo lại nguồn chứng cứ». Khoá sai ⇒ nhà cung cấp trả 401/403, connector báo lỗi rõ.

**Điều kiện của nền tảng:** API credentials chỉ có ở gói Pro/Max (tài liệu chính thức: Team/Enterprise
chưa có), cần vai quản trị tổ chức — gói cá nhân thì bác sĩ tự có. Host đã khai credential gọi được
cả khi Network access chưa mở host đó. Proxy không gắn khoá cho request của **setup script**.

Kiểm: `tests/test_khoa_qua_proxy_20260924.py` (6) + 2 test Consensus; 4 phép đột biến đều đỏ đúng chỗ.

## 7quater. Đo lại sau khi bác sĩ mở mạng + khai khoá (24/09/2026, tối) — và 2 lỗ hổng đồng bộ

**Đã chạy thật trên Cloud** (sau `medical-ebm-automation#6` + `EBM-drluanbv175#24`): PubMed · Europe PMC ·
Crossref · ClinicalTrials.gov · openFDA · CORE · **Scopus qua khoá do proxy gắn** (5 bài, DOI thật) ·
Consensus (máy chủ nhận khoá) · Unpaywall (khi có email) · RxNorm · EMA · WHO IRIS · kcb.vn · GOLD/GINA
toàn văn · PMC S3 · nền Retraction Watch · chuỗi rút bài 3 tầng (PubMed bắt PMID 9500320, nền RW bắt
30267080) · **73/77 feed/làn guideline** (Crossref-ISSN 31/31 · Crossref-tiêu đề 21/21 · Europe PMC 5/5 ·
WHO IRIS · BYT · RSS 14/18 — 4 RSS BMJ vẫn 0 mục như trên máy thật).

**Lỗ hổng A — phiên Cloud MỚI không chạy được engine** (đã vá). Python mặc định 3.11, thiếu
`sqlalchemy`/`python-dotenv`/`pypdf`/`wiley-tdm`; `requirements.lock.txt` cần ≥3.12. Venv dùng để đo là
do agent dựng tay và mất theo container, hook Cloud không dựng lại. Nay
`tools/dung_venv_engine_cloud.py` (nối `tu_sua_chua.py` · `chay_tren_cloud=True`) dựng `~/.ebm-venv`
bằng python3.12 **ở nền** (~5 phút lần đầu) khi mở phiên; có `--clear` vì đo được container còn một
`~/.ebm-venv` Python 3.11 cũ (không clear ⇒ pip chết ở scipy 1.18.0 — lỗi thật gặp khi chạy thử). Máy
thật: no-op. Test `tools/test_dung_venv_engine_cloud_20260924.py` (9).

**Lỗ hổng B — connector GOLD trả báo cáo CŨ** (đã vá, `medical-ebm-automation`). Chỉ đọc
`archived-reports/` — trang này theo định nghĩa không có bản năm hiện hành ⇒ trả GOLD-2025 v1.0 trong khi
GOLD 2026 v1.3 (8/12/2025) đã phát hành. Nay đọc năm từ link trên trang chủ, lấy PDF đầy đủ (loại Pocket
Guide + «Summary of Changes»), lùi về archived khi lỗi. Test 4 ca, 2 đột biến đều đỏ.

**Host còn bị proxy chặn** (đo từ sổ nguồn + mọi URL mã gọi; bác sĩ thêm ở Network access → Custom nếu
cần nguồn đó): cảnh báo an toàn thuốc `www.fda.gov` · `www.gov.uk` (MHRA) — **3/3 feed an toàn thuốc đang
0 mục vì thiếu 2 host này** · web hội `professional.heart.org` · `www.escardio.org` · `professional.diabetes.org`
· `www.idsociety.org` · `www.uspreventiveservicestaskforce.org` · `www.who.int` · `www.brit-thoracic.org.uk` ·
`www.nice.org.uk` · `www.cdc.gov` · `www.cochranelibrary.com` · khác: `api.epistemonikos.org` (cần token) ·
`serpapi.com` (khoá qua URL) · `api.wiley.com` (Wiley TDM, còn giới hạn IP tổ chức) · `dav.gov.vn` (chưa
kiểm được từ bất kỳ môi trường nào). **Hai host «chặn» khác là lỗi phía máy chủ, không phải mạng:**
OpenAlex 503 («tạm dừng tìm kiếm ẩn danh» — nay khuyên dùng khoá API miễn phí; mã chưa hỗ trợ khoá này) ·
Semantic Scholar 429 (không khoá).

**Connector MCP:** Cochrane MCP (`cochrane_search`…) KHÔNG có trên phiên Cloud (plugin cài trên máy
Mac, không phải connector claude.ai) — trên Cloud engine phủ Cochrane bằng làn Crossref ISSN 1465-1858.

## 7quinquies. Đo lại trong phiên Cloud MỚI (24/09/2026, 18:50–19:40 giờ VN) — sau khi bác sĩ mở thêm host

**Điều kiện đo.** Phiên CHỈ-MỘT-REPO (`EBM-drluanbv175`). Biến môi trường có sẵn: `USE_MOCK_SOURCES=false` · `NCBI_EMAIL` ·
`UNPAYWALL_EMAIL` · `OPENALEX_EMAIL` · `NCBI_API_KEY` · `OPENFDA_API_KEY` · `SERPAPI_API_KEY` ·
`ENABLE_SCOPUS/CORE/CONSENSUS/SERPAPI_SCHOLAR=true` · `KHOA_QUA_PROXY=scopus,core,consensus`; API credentials do proxy gắn:
Scopus · CORE · Consensus. Engine KHÔNG có trong phiên ⇒ agent clone `medical-ebm-automation` (công khai, chỉ đọc) cạnh repo
gốc → `tools/dung_venv_engine_cloud.py --ap-dung` (venv Python 3.12.3, ~2 phút) → `tools/nap_nen_rut_bai_cloud.py --ap-dung`
(nền Retraction Watch 72.606 dòng từ `api.labs.crossref.org`, 9 giây). Engine đo ở `719b360` (#6); PR #7 (GOLD) hợp nhất
GIỮA phiên ⇒ cập nhật lên `8ffc4ee` và đo lại GOLD (diff #6→#7 chỉ chạm `gold_copd.py` + test). Repo gốc cập nhật lên
`0936391` (#27) trước khi sửa mã.

**Kết luận ngắn.**
1. Engine trên Cloud nay LẤY ĐƯỢC chứng cứ thật: 8/11 nguồn tìm kiếm chạy (Consensus không gọi — giữ hạn mức), 76/80
   feed/làn, chuỗi rút bài 3 tầng, toàn văn PMC S3 · GOLD 2026 v1.3 · GINA 2026 (khi bật cờ).
2. Mới so với §7quater: **3/3 feed an toàn thuốc chạy** (FDA MedWatch · FDA Recalls · MHRA DSU — trước 0/3); 11 host
   web hội/cơ quan đã mở.
3. Còn hỏng/thiếu — đều có việc cụ thể (g): SerpApi (host `serpapi.com` chưa mở dù khoá đã đặt) · OpenAlex (hết ngân sách
   ẩn danh theo IP dùng chung — cần khoá miễn phí) · Semantic Scholar (429 chập chờn, không khoá) · Epistemonikos (chưa
   token) · 4 RSS BMJ (Cloudflare 429) · bioRxiv MCP `search_preprints` (lỗi máy chủ lần 5; làn preprint qua Europe PMC VẪN
   chạy) · Wiley TDM (`api.wiley.com` bị chặn).
4. **Hai cảnh báo lúc mở phiên là BÁO ĐỘNG GIẢ do vắng engine:** «⚠ DỮ LIỆU GIẢ (không có secrets)» và 3 chốt đỏ
   BH88/108/109. Có engine ⇒ `kiem_nguon_that.py` 🟢, bộ chốt 87/114 ✓ · 0 ✗. Đã vá phía công cụ (e, #15–#16); dòng
   «DỮ LIỆU GIẢ» của hook còn chờ bác sĩ (F1).
5. **Phát hiện chi phí:** chốt BH113 (chạy mỗi lần mở phiên) gọi THẬT CORE, và Consensus + SerpApi khi Python có
   sqlalchemy — đã vá (e, #14).

### a. Mạng — 54 host, thăm qua proxy

| Nhóm | Host |
|---|---|
| Proxy CHẶN theo chính sách (CONNECT 403) | `serpapi.com` · `api.wiley.com` · `api.biorxiv.org`/`api.medrxiv.org` · `dav.gov.vn` · `link.springer.com` · `europepmc.org` (engine chỉ dùng làm link; API đi `www.ebi.ac.uk` — mở) · `scite.ai` (engine gọi `api.scite.ai` — mở) |
| Mở MỚI so với §7quater | `www.fda.gov` · `www.gov.uk` · `www.who.int` · `www.nice.org.uk` · `www.cdc.gov` · `www.escardio.org` · `professional.diabetes.org` · `www.idsociety.org` · `www.uspreventiveservicestaskforce.org` · `www.brit-thoracic.org.uk` · `api.epistemonikos.org` |
| Tới được nhưng MÁY CHỦ từ chối bot ở trang gốc (403/429 — không phải proxy) | `*.bmj.com` · `jamanetwork.com` · `www.nejm.org` · `www.jacc.org` · `professional.heart.org` · `www.cochranelibrary.com` |

### b. 11 nguồn tìm kiếm của engine (`run.py test-live`, venv 3.12)

| Nguồn | Kết quả | Ghi chú |
|---|---|---|
| PubMed | ✅ 5/5 thật · 1,6 s | có `NCBI_API_KEY` |
| Europe PMC · Crossref · ClinicalTrials.gov | ✅ 5 · 5 · 5 | |
| Scopus | ✅ 5 (DOI 5, PMID 3) | khoá do proxy gắn |
| CORE | ✅ 5 | khoá do proxy gắn |
| openFDA | ✅ 5 với «metformin» · khoá «FDA CHẤP NHẬN» | truy vấn mặc định của test-live không phải tên thuốc ⇒ 404 «no match» bị báo thành lỗi mạng (F5) |
| OpenAlex | ❌ 429 | «This request has no API key, so it counts against the free daily budget shared by everyone on your network's IP address» — IP thoát của Cloud dùng chung; cần khoá miễn phí |
| Semantic Scholar | ❌ 429 (curl một phút sau: 200) | không khoá ⇒ chập chờn |
| Epistemonikos | ⚪ chưa có token | xin qua email |
| SerpApi Scholar | ❌ proxy chặn `serpapi.com` | khoá ĐÃ đặt ở biến môi trường — chỉ thiếu host |
| Consensus | KHÔNG gọi | giữ hạn mức 30 lượt/tháng dùng chung MCP; máy chủ đã nhận khoá ở §7quater |

### c. Feed/làn, rút bài, toàn văn, khâu thu nhận

- **80 feed/làn: 76 có mục.** An toàn thuốc 3/3 (MỚI) · Crossref-ISSN 31/31 · Crossref-tiêu đề 21/21 (`acp_annals` 429 chỉ
  khi gọi song song 8 luồng; gọi riêng: 5 mục) · Europe PMC 5/5 · WHO IRIS 1/1 · kcb.vn 1/1 · RSS 14/18 — 4 RSS BMJ
  (Frontline Gastroenterology · Gut · Heart · Thorax) trả 429 của Cloudflare kể cả gọi tuần tự với UA trình duyệt (§7quater:
  máy thật cũng 0 mục).
- **Chuỗi rút bài 3 tầng ✅:** 9500320 `retracted` (PubMed) · 30267080 `retracted` + retract-and-replace (nền RW — PubMed và
  PubMed MCP KHÔNG gắn cờ) · 33264437 `ok` (PubMed).
- **Toàn văn guideline:** PMC S3 ✅ · GOLD ✅ **GOLD 2026 v1.3 (8/12/2025)** trên `8ffc4ee` (trên `719b360` vẫn trả GOLD-2025
  v1.0 — PR #7 sửa đúng) · GINA ✅ link GINA-2026 Strategy Report. **Cả ba chỉ chạy khi bật cờ** — Cloud CHƯA đặt
  `ENABLE_PMC_GUIDELINE_FULLTEXT` · `ENABLE_GOLD_COPD_FULLTEXT` · `ENABLE_GINA_ASTHMA_FULLTEXT` ·
  `ENABLE_BTS_GUIDELINES_FULLTEXT` (đo bằng cờ bật TẠM trong tiến trình đo).
- Unpaywall ✅ · Scite API công khai ✅ (tally Wakefield 1.521) · RxNorm ✅ `khop_chinh_xac` · EMA ✅ 3 kết quả · Wiley TDM ❌
  host bị chặn.
- **Khâu thu nhận** (bản vendor `surveillance_scan.py`, 2 chủ đề canary, tắt tạm Consensus/SerpApi, chạy trong thư mục gốc
  giả để không ghi vào repo): `--max 20` ⇒ PASS, 38 ứng viên (PubMed 11 · Scopus 27), rút bài 21 `ok` / 17 chưa kiểm (Scopus
  không PMID); làn preprint (Europe PMC `SRC:PPR`) · ClinicalTrials.gov · CORE đều trả ứng viên.

### d. Connector MCP, sổ nguồn, chốt tổng

- PubMed ✅ · ClinicalTrials.gov ✅ (128) · Scite ✅ · Wiley ✅ (kho 09/2026) · Amass ✅ · bioRxiv: `get_categories` ✅,
  `search_preprints` ❌ (lần 5) · Consensus MCP: không gọi.
- `sources_health.py --khong-ghi`: 28 active · 4 degraded (SRC-007 OpenAlex · SRC-015 ACC/AHA web · SRC-039 Semantic Scholar
  · SRC-042 Wiley TDM) · 4 not-covered; băm `data/sources.json` trước = sau.
- `chu_trinh_chung_cu.py --nhanh`: ① 🟢 · ⑤ 🟢 · ② ③④ ⑥ không đo được trên Cloud (giám sát tuần chưa chạy trên Linux; sổ xác
  minh trống; `dashboard_mockups/`/`EBM_MASTER/` ngoài git).
- Canary giám sát của engine (`weekly_safety.sh --canary`): ESD06 nguồn online ✅ (PubMed · Europe PMC · Crossref · openFDA);
  ESD02/04/07/08 FAIL GIẢ trên Cloud — F3.

### e. Đã vá trong phiên (repo gốc)

| # | Lỗi (đo thật) | Vá | Kiểm |
|---|---|---|---|
| 14 | **BH113 không ngoại tuyến.** Chốt gọi `run_scan()` thật nhưng chỉ chặn 3 làn cũ; 2 làn thêm 22/09 (`search_core_lane`, `bo_sung_du_phong_lane`) chạy thật. Đo dưới proxy từ chối mọi kết nối: Python hệ thống ⇒ 3 CONNECT `api.core.ac.uk`; Python có sqlalchemy ⇒ thêm 3 `api.consensus.app` + 3 `serpapi.com` — **mỗi lượt chốt ăn hạn mức tháng Consensus (dùng chung MCP) và SerpApi (trả phí)**. Test pytest đã chặn đủ 5 làn từ 22/09; chốt bị sót | chặn đủ 5 làn; rào TĨNH (mọi hàm `*_lane` mới phải được chặn — đỏ ở MỌI máy); rào ĐỘNG (thân chốt chạy dưới khoá socket — mở kết nối ⇒ đỏ) | 3 đột biến đỏ đúng chỗ (M1 rào tĩnh; M2 gắn lại làn CORE thật ⇒ «chốt mở 15 kết nối»; M3 gắn lại bậc thang thật ⇒ «6 kết nối»); phục hồi xanh, 0 kết nối; trọn bộ 87/114 ✓ · 0 ✗; `pytest tools/` 1091 passed · 30 skipped có khai báo |
| 15 | `kiem_nguon_that.py` báo «THIẾU THƯ VIỆN (No module named 'app') — cài venv» khi phiên VẮNG engine; hook đọc mã 1 thành «DỮ LIỆU GIẢ» | vắng engine ⇒ 🟡 «KHÔNG ĐO ĐƯỢC», nêu biến môi trường OS khai gì (không in giá trị `NCBI_EMAIL`) và cách gắn engine | `tools/test_kiem_nguon_that_vang_engine_20260924.py` (3 ca, chạy được trên bản sao trần); đột biến ⇒ 2 đỏ, nhánh «thiếu thư viện THẬT» vẫn xanh |
| 16 | BH88/108/109 đỏ «tái phát» ở mọi phiên một-repo chỉ vì vắng engine (3 dòng đỏ giả lúc mở phiên) | luật phân loại HẸP `_CAN_ENGINE_NEU_TEN`: ⚪ CHỈ KHI thông điệp nêu đích danh `medical-ebm-automation` VÀ engine thật sự vắng; lỗi doctrine trong repo, crash thật, engine có mặt ⇒ vẫn ✗ (cố ý KHÔNG dùng `_CAN_NGUYEN_LIEU_NGOAI_REPO` — nhánh lùi `tran` ở đó sẽ ⚪ hoá cả lỗi trong repo trên Cloud); BH108 nêu đủ đường dẫn engine | 4 ca mới trong tự kiểm BH82; 4 đột biến (bỏ luật · bỏ điều kiện vắng · bỏ điều kiện nêu tên · bỏ rào crash) đều đỏ đúng câu; mô phỏng phiên một-repo: 78/114 ✓ · ⚪ 36 · 0 ✗ (trước: 3 ✗) |

**Lượt gọi thật do chính phiên này gây ra (minh bạch):** lượt chạy bộ chốt ĐẦU TIÊN (18:56 giờ VN, trước khi phát hiện #14)
gọi CORE thật 3 lần (bộ đệm HTTP giữ 3 phản hồi CORE). Consensus/SerpApi KHÔNG bị gọi ở lượt đó (Python hệ thống thiếu
sqlalchemy ⇒ bậc thang dừng ở import). Mọi phép tái hiện sau đó chạy dưới proxy/khoá socket từ chối; bộ đếm tháng
Consensus của engine = 0. `serpapi.com` bị proxy chặn ⇒ không lượt SerpApi nào tới máy chủ (bộ đếm cục bộ vẫn tăng — đếm
dư có chủ ý). Đo có chủ ý: Scopus ~5 lượt, CORE ~9 lượt.

### f. Phát hiện chưa vá — đề xuất

| # | Chỗ | Vấn đề đo được | Đề xuất | Ai |
|---|---|---|---|---|
| F1 | Hook Cloud ⑥b (`.claude/hooks/` — được bảo vệ) | mọi mã ≠ 0 ⇒ «DỮ LIỆU GIẢ (không có secrets)»; tiền đề «Cloud không có secrets — BÌNH THƯỜNG VĨNH VIỄN» đã lỗi thời từ khi đặt biến môi trường | tách mã 2 (🔴 dữ liệu giả) với mã 1 (🟡 không đo được), mỗi mức một dòng đúng nghĩa | bác sĩ |
| F2 | Hook Cloud ⑤ đứng TRƯỚC ⑤b | phiên có engine: bộ chốt chạy trước khi nạp nền RW ⇒ BH52 đỏ «CHƯA KẾT LUẬN» lúc mở phiên | chuyển ⑤ xuống sau ⑤b (hoặc BH52 ⚪ khi nền RW vắng) | bác sĩ |
| F3 | engine `tools/verify_evidence_surveillance_deployment.py` | ghép cứng bố cục LỒNG (`ROOT/sync/…`, `ROOT/EBM-Dashboards/…`) ⇒ ESD02/04/07/08 FAIL giả trên Cloud (engine là anh em); ESD07 chạy `--max 1` trong khi luật «cắt ở retmax ⇒ PASS_DEGRADED» ⇒ không bao giờ PASS khi chủ đề canary có >1 bài/30 ngày (đo trên bộ quét TRƯỚC PR #28: `--max 1` ⇒ PARTIAL; `--max 20` ⇒ PASS) — **phần ESD07 này hết áp dụng từ `405dc44`**: PR #28 (phương án B) đã bỏ luật «bị cắt ⇒ suy giảm» | phân giải gốc repo như `_goc_mea()` | PR engine (phiên `session_01W8uKHisKhxF3tJnR2JDW5y`) |
| F4 | bộ quét `surveillance_scan.py` (3 bản) | (i) ~~báo cáo + alert quy MỌI `PASS_DEGRADED` về «NCBI lỗi/bị chặn»~~ — **đã sửa ở master bởi PR #28** (câu suy giảm không còn mặc định đổ cho NCBI); (ii) `ghi_alert()` ghi vào `DEFAULT_WATCHLIST.parent.parent/alerts` — bản vendor ghi sai chỗ `sync/skills/alerts/` (đã dọn tệp do lượt đo sinh ra); (iii) lượt canary `--khong-cursor` vẫn ghi alert vào thư mục dùng chung | (ii)–(iii) còn nguyên sau PR #28: dò gốc repo như `_tim_medical_ebm_automation()`; canary không ghi alert | PR riêng (nguồn chuẩn + đồng bộ 3 bản) |
| F5 | engine `run.py test-live openfda` | truy vấn mặc định không phải tên thuốc ⇒ 404 «no match» bị báo `loi_goi_mang`, khoá «chưa gọi được lần nào» | mặc định một tên thuốc; 404 NOT_FOUND = 0 kết quả | PR engine |
| F6 | engine `app/sources/feeds.py` | 4 RSS BMJ bị Cloudflare 429 ở cả Cloud lẫn máy thật | chuyển sang chế độ Crossref-ISSN như `_CROSSREF_THAY_RSS` | PR engine |
| F7 | test không kín mạng (nguồn miễn phí) | BH43 · BH52 · BH102 và 4 tệp test bộ quét vẫn gọi NCBI/Europe PMC/Crossref thật; `test_surveillance_scan_ghi_alert_20260922.py` ĐỎ 2 ca khi mạng bị từ chối | tiêm bộ lấy dữ liệu giả cho `gan_do_tin_cay` trong các test đó | PR sau |

### g. Việc CỦA BÁC SĨ (theo lợi ích)

1. **Network access → thêm `serpapi.com`** — khoá SerpApi đã đặt nhưng làn SerpApi chết trên Cloud tới khi mở host.
2. **OpenAlex:** tạo khoá miễn phí (https://help.openalex.org/api/authentication/) → API credentials: Allowed websites
   `api.openalex.org`, header `Authorization`, prefix `Bearer`. Connector không tự gửi `Authorization` nên không cần sửa mã
   `[CẦN KIỂM CHỨNG — chưa chạy với khoá thật]`.
3. **Semantic Scholar:** khai khoá (header `x-api-key`, §7ter) để hết 429 chập chờn.
4. Muốn toàn văn guideline trên Cloud: thêm 3 cờ ở mục h (GOLD · GINA · PMC; BTS không cần lúc này).
5. Duyệt F1–F2 (hook được bảo vệ) và F3/F5/F6 (engine — cần phiên có quyền ghi repo engine).
6. **Trên Mac `[CẦN KIỂM CHỨNG]`:** nếu `python3` mà hook `SessionStart` dùng để chạy bộ chốt có đủ sqlalchemy + dotenv thì
   trước bản vá #14 mỗi lần mở phiên có thể đã tiêu Consensus/SerpApi — đối chiếu
   `medical-ebm-automation/data/raw/_state/consensus_usage.json` · `serpapi_usage.json` với trang hạn mức của nhà cung cấp.

### h. Toàn văn guideline trên Cloud (bác sĩ yêu cầu, 24/09/2026 tối)

**Đo end-to-end với cờ bật TẠM trong tiến trình đo** (engine `8ffc4ee`):

| Connector | Kết quả | Ghi chú |
|---|---|---|
| GOLD (`gold_copd.py`) | ✅ GOLD 2026 v1.3 (8/12/2025) · 200.000 ký tự · 7 giây | trích thử «GOLD 2026 REPORT HIGHLIGHTS» |
| GINA (`gina_asthma.py`) | ✅ GINA 2026 Strategy Report · 200.000 ký tự · 23 giây | trích thử «Track 1 (preferred): … ICS-formoterol reliever» |
| PMC (`pmc_guideline_fulltext.py`) | ✅ PMC13555224 · 200.000 ký tự · 0,6 giây | bucket S3 chính thức |
| BTS (`bts_guidelines.py`) | ❌ URL pleural-disease (URL trong test 23/09) nay 404 — site đổi cấu trúc, gần như không còn PDF; URL nice.org.uk bị từ chối ĐÚNG (giấy phép AI của NICE) | đường lùi `guideline_citation_summary` ✅ (PMID 37433578) |

**Hai giới hạn thật:** (1) bốn connector là CÔNG CỤ MỒ CÔI — chỉ export ở `app/sources/__init__.py`, không lệnh/tool/agent nào
gọi ⇒ bật cờ xong vẫn chưa ai dùng; (2) `trich_van_ban_tu_pdf` cắt ở 200.000 ký tự ⇒ mất phần sau của báo cáo GINA/GOLD (vài trăm
trang). **Đã giao cho phiên engine riêng** (`session_01W8uKHisKhxF3tJnR2JDW5y`, theo yêu cầu «mở phiên» của bác sĩ): lệnh
`tools/toan_van_guideline.py` (khuôn `tra_thuoc_quoc_te.py`, có `--tim`), tìm được trong toàn bộ PDF, thông điệp cờ tắt nói đúng cách
bật trên Cloud, cùng F3 · F5 · F6. Doctrine agent (`tra-cuu-chung-cu`, `huong-dan-lam-sang`) nối lệnh đó SAU khi PR engine được merge.

**Việc của bác sĩ — bật trên Cloud** (menu môi trường ở thanh tiêu đề phiên → Edit → Environment variables; áp cho phiên MỚI):
```
ENABLE_GOLD_COPD_FULLTEXT=true
ENABLE_GINA_ASTHMA_FULLTEXT=true
ENABLE_PMC_GUIDELINE_FULLTEXT=true
```
`ENABLE_BTS_GUIDELINES_FULLTEXT` không cần lúc này (không còn nội dung tải được). Bật là quyết định của bác sĩ vì bản quyền:
báo cáo GOLD/GINA chỉ dùng làm nguồn tham chiếu NỘI BỘ để trích câu chữ kèm nguồn — KHÔNG đăng lại toàn văn, KHÔNG phân phối
lại file (`GHI_CHU_BAN_QUYEN_CHUAN`).

## 7sexies. Chất lượng kết quả, không chỉ kết nối (25/09/2026) — «mới nhất» ≠ «mạnh nhất»

Kết nối đạt (engine tự chạy 9 nguồn thật), nhưng phép thử có đáp án biết trước lộ lỗi chất lượng: đường
thu thập mặc định (`ingest_all` → `PubMedClient.search`) sắp PubMed theo NGÀY rồi cắt 10 bài ⇒ trả 10 bài
**mới nhất**. Trên 6 bệnh ngoại trú (THA · suy tim · rung nhĩ · ĐTĐ2 · COPD · CKD): **0/15 guideline chuẩn
2023–2026** lọt vào; 4/6 chủ đề có 7–8/10 bài tier C. Đã vá (`medical-ebm-automation`):

| Việc | Kết quả đo |
|---|---|
| #1 PubMed «lấy đủ rồi chọn mạnh nhất»: vùng 100 bài mới nhất + làn guideline 20 bài theo relevance (5 năm / cửa sổ `since_date`), xếp: độ mạnh → tiêu đề sát chủ đề (có đồng nghĩa «blood pressure», «chronic obstructive»…) → relevance → năm; bài bị rút xếp cuối (không vứt); tắt bằng `PUBMED_CHON_MANH_NHAT=false` | Chuẩn vàng **0/9 → 8/9**; suy tim → AHA/ACC/HFSA 2022 hạng 1; THA → AHA/ACC 2025 hạng 1, ESC 2024 hạng 2; rung nhĩ → ACC/AHA 2023 + ESC 2024; CKD → KDIGO 2024 hạng 1 |
| #2 `tools/kiem_chuan_vang_guideline.py` + `config/chuan_vang_guideline.json` (9 nhóm guideline, PMID tra thật; mã 0/1/2, «không đo được» ≠ «đạt») | Còn trượt: ADA Standards of Care 2026 (PubMed gắn «Review», tiêu đề không ghi «type 2»). **Bác sĩ cần duyệt danh sách** (`bac_si_duyet`) |
| #3 Heart/Gut/Frontline Gastro/Thorax (BMJ) sang Crossref ISSN điện tử | Feed/làn guideline **73/77 → 77/77** |
| #6 Feed thu hồi thuốc FDA bị chặn ⇒ lùi openFDA `drug/enforcement` (API chính thức; không giả dạng trình duyệt); MedWatch không có API tương đương nên vẫn báo lỗi thật | Dự phòng trả bản thu hồi thật (16/09/2026) |
| #7 Kiểm chéo ngữ nghĩa mục `apply` | Thiết kế ở `audit/16`, **chờ bác sĩ duyệt hướng** |

Loại khỏi đề xuất theo quyết định bác sĩ 25/09: khoá Semantic Scholar, token Epistemonikos.
Kiểm: 5.811 test đạt; 3 phép đột biến trên bộ xếp hạng đều đỏ đúng chỗ.

**Cập nhật 25/09/2026 (chiều): ADA Standards of Care đã lọt top.** Đo sống có hai nguyên nhân.
(1) Chương 9 «Pharmacologic Approaches to Glycemic Treatment: Standards of Care in Diabetes—2026»
(PMID 41358900) không có trong 20 bài đầu của làn guideline, vì tiêu đề không ghi «type 2».
(2) Kể cả có mặt, nó vẫn bị hạ do luật «tiêu đề sát chủ đề» đòi chữ «type».
Đã vá bằng một **làn chuỗi guideline sống** (`_CHUOI_GUIDELINE_SONG`), chỉ chạy khi truy vấn có «diabetes»
hoặc «diabetic». Làn lấy các chương ADA trên *Diabetes Care*, chỉ giữ **ấn bản mới nhất** (năm đọc từ tiêu
đề) và bỏ đính chính, tóm tắt sửa đổi, lời giới thiệu. Làn chọn 2 chương sát nhất theo relevance và coi hai
chương này là sát chủ đề. Các chương cũ chỉ đến từ làn này thì bị bỏ, để không chiếm chỗ trong top.

Kết quả chuẩn vàng: **8/9 → 9/9**. Với «type 2 diabetes», ADA SoC 2026 ch.9 xếp hạng 8 và ch.2 hạng 7. Với
«diabetic kidney disease», ch.11 hạng 8. Có 3 test mới; 4 phép đột biến đều làm test đỏ đúng chỗ.

## 8. Chưa làm, có chủ ý

- ~~`tools/sources_health.py` ghi trạng thái ngược vào sổ tracked từ mọi máy~~ — ĐÃ VÁ (§7bis #10).
- Không gọi Consensus MCP (hạn mức). Không đo lại sau khi đổi mạng (không đổi được môi trường từ
  bên trong phiên).
- Engine Python trên Cloud VẪN mù cho tới khi bác sĩ đổi Network access (§7 việc 2) — đây là cấu
  hình môi trường, mã không vượt được proxy (và không được thử vượt).
- `_tham()` của `sources_health` vẫn chưa gắn khoá theo nguồn (CORE/Scopus không thăm sống) — giữ
  nguyên quyết định 22/09.

Cần bác sĩ kiểm chứng.
