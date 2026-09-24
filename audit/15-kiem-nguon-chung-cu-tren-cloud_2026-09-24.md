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

## 8. Chưa làm, có chủ ý

- ~~`tools/sources_health.py` ghi trạng thái ngược vào sổ tracked từ mọi máy~~ — ĐÃ VÁ (§7bis #10).
- Không gọi Consensus MCP (hạn mức). Không đo lại sau khi đổi mạng (không đổi được môi trường từ
  bên trong phiên).
- Engine Python trên Cloud VẪN mù cho tới khi bác sĩ đổi Network access (§7 việc 2) — đây là cấu
  hình môi trường, mã không vượt được proxy (và không được thử vượt).
- `_tham()` của `sources_health` vẫn chưa gắn khoá theo nguồn (CORE/Scopus không thăm sống) — giữ
  nguyên quyết định 22/09.

Cần bác sĩ kiểm chứng.
