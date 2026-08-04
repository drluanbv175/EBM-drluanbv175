# Việc cần chạy TRÊN MÁY WINDOWS (bàn giao từ phiên Mac 03/08/2026)

> Đợi OneDrive **XANH** rồi mới bắt đầu. Mở Claude Code trong `%USERPROFILE%\OneDrive\Claude AI`.
> Đây là bản đối xứng của `MAC-LAM-TIEP.md` (chiều ngược lại, do phiên Windows viết sáng cùng ngày).

Phiên Mac đã làm tiếp sau bàn giao của Windows: thêm **52 lệnh tên tiếng Việt** (trước là 47),
cài **plugin meta-pipe** 14 skill phân tích gộp, dựng **lộ trình gọi lệnh cho một đề tài trọn
vẹn**, vá **lỗi font** ở danh sách gõ `/`, và dựng đủ môi trường chạy meta-pipe trên Mac.

**Tin tốt cho Windows:** từ hôm nay thư mục `sync/` đã nằm trong Git (trừ `sync/memory/`), nên
52 lệnh và toàn bộ script `.ps1`/`.cmd` về theo `git pull` — không còn phụ thuộc riêng OneDrive.

---

## 1. Kéo mã mới về (bắt buộc, làm trước)

```
cd %USERPROFILE%\OneDrive\Claude AI
git pull
cd medical-ebm-automation
git branch --show-current
git pull
cd ..
```

> ### ⚠ Repo y khoa: kiểm NHÁNH trước khi kết luận "thiếu file"
>
> Repo `medical-ebm-automation` **không làm việc trên `master`**. Toàn bộ đề tài C1a
> (đề cương, hồ sơ đạo đức, SAP, 7 bản Word) nằm trên nhánh
> **`feat/r1-1-2-design-gap-remediation`** — nhánh này đi trước `master` **510 commit**.
>
> Đứng ở `master` mà `git pull` thì thư mục `exports/hai-long-benh-nhan-C1a-BVQY175/`
> **sẽ không có** — đó là do sai nhánh, không phải mất dữ liệu. Chuyển nhánh:
>
> ```
> git checkout feat/r1-1-2-design-gap-remediation
> git pull
> ```
>
> Việc gộp nhánh này vào `master` là **quyết định của bác sĩ**, không máy nào tự làm.

## 2. Cài 52 lệnh tiếng Việt

Bấm đúp **`sync\copy-commands-vi.cmd`** (hoặc chạy `sync\copy-commands-vi.ps1`).
Script idempotent, tự báo *mới / cập nhật / không đổi* và tự lưu `.bak-<thời-gian>` khi ghi đè.

Lệnh mới có hiệu lực **ngay**, không cần mở lại phiên — khác với mô tả skill ở bước 3.

> **4 lệnh sẽ chưa chạy được cho tới khi làm bước 5:** `/tim-chu-de-gop` ·
> `/sang-loc-nghien-cuu` · `/kiem-prisma` · `/gop-tron-goi` — chúng gọi vào skill của
> meta-pipe, mà kho này Windows chưa có.

## 3. Áp bản dịch cho plugin của máy Windows

Bản dịch nằm trong Git nên tự có; nhưng việc *ghi* bản dịch vào file plugin thì **mỗi máy phải
tự làm** (thư mục cài có kèm số phiên bản, khác nhau giữa hai máy).

```
python tools\vietnamize\extract_catalog.py
python tools\vietnamize\apply_vi.py
python tools\vietnamize\verify_vi.py
python tools\vietnamize\check_chat_luong.py
python tools\vietnamize\build_danh_muc.py
```

Kỳ vọng: `verify_vi.py` ra **"✓ Sạch"**, `check_chat_luong.py` ra **0 lỗi chặn**.
Dòng "N bản dịch không dùng tới trên máy này" là **bình thường** — đó là plugin chỉ cài ở máy kia.

Xong bước này `DANH-MUC-CONG-CU.md` sẽ đổi (số liệu Windows tươi hơn) → commit lại:

```
git add tools\vietnamize\DANH-MUC-CONG-CU.md
git commit -m "chore(vietnamize): sinh lai danh muc sau khi quet lai may Windows"
git push
```

**Phải mở lại phiên Claude Code** thì mô tả mới hiện — frontmatter chỉ đọc lúc nạp.

## 4. Chỉ thị ngôn ngữ toàn cục

`~/.claude/CLAUDE.md` nằm **ngoài** OneDrive nên không tự sang máy khác. Nếu Windows chưa có,
bấm đúp **`sync\copy-claude-md.cmd`**.

## 5. Cài plugin meta-pipe (14 skill phân tích gộp)

Kho gốc: <https://github.com/htlin222/meta-pipe> — giấy phép học thuật, phi thương mại.
Nó là một *dự án* Claude Code, không phải plugin, nên phải tự đóng gói. File đóng gói
(`.claude-plugin/marketplace.json` + `plugin.json`) Mac đã viết và nằm trong kho đã clone;
Windows clone về là có luôn.

**Cách chính thức, nên thử trước** — trong một phiên Claude Code tương tác:

```
git clone https://github.com/htlin222/meta-pipe %USERPROFILE%\Documents\GitHub\meta-pipe
```

rồi gõ `/plugin marketplace add %USERPROFILE%\Documents\GitHub\meta-pipe` và bật plugin.

**Nếu app nhận marketplace nhưng gọi skill vẫn báo không tìm thấy** — đúng lỗi Mac vừa gặp:
app ghi cấu hình nhưng **chưa tạo thư mục cache**, mà nó chỉ nạp skill từ cache. Kiểm và sửa:

```powershell
# 1) app đang chờ cache ở đâu:
python -c "import json,pathlib;d=json.loads((pathlib.Path.home()/'.claude/plugins/installed_plugins.json').read_text());print([e['installPath'] for k,v in d.get('plugins',d).items() if 'meta' in k.lower() for e in (v if isinstance(v,list) else [v])])"

# 2) nếu đường dẫn đó KHÔNG tồn tại, chép nội dung kho vào (trừ .git):
robocopy "%USERPROFILE%\Documents\GitHub\meta-pipe" "<đường-dẫn-vừa-in-ra>" /E /XD .git
```

Kiểm chứng: `<đường-dẫn>\.claude-plugin\plugin.json` phải có, và đếm được **14 file SKILL.md**.

> **Hai bẫy đã trả giá, đừng lặp lại:**
> - `installPath` **phải nằm trong** `~/.claude/plugins/`. Trỏ ra ngoài thì app im lặng bỏ qua,
>   chỉ ghi ở `~/AppData/Roaming/Claude/logs/main.log`.
> - Có mục trong `known_marketplaces.json` **không** đồng nghĩa đã cài. Dấu hiệu cài thật là
>   file `~/.claude/plugins/.install-manifests/<plugin>@<marketplace>.json` **hoặc** thư mục
>   cache có nội dung thật.

Cài xong quay lại chạy bước 3 để 14 mô tả này thành tiếng Việt.

## 6. Công cụ ngoài mà meta-pipe cần

Chỉ cần nếu thật sự chạy dây chuyền phân tích gộp:

| Công cụ | Dùng cho | Kiểm |
|---|---|---|
| `uv` | chạy script Python của meta-pipe | `uv --version` |
| `node` | vài bước xử lý văn bản | `node --version` |
| Quarto | dựng bản thảo (đã kèm sẵn `pandoc`) | `quarto --version` |
| R + `renv`, `meta`, `metafor` | thống kê gộp, forest/funnel plot | `R -e "packageVersion('metafor')"` |

`dot` (graphviz), `latexmk`/`pdflatex`, `ffmpeg`, `soffice` là **tuỳ chọn** — thiếu chỉ mất vài
định dạng xuất, `check_plugin_health.py` xếp chúng vào nhóm cảnh báo N3, không chặn.

## 6b. ASReview — sàng lọc tổng quan bằng học chủ động (tuỳ chọn)

Cài trên Mac ngày 04/08/2026. Đây là **ứng dụng Python riêng, không phải plugin** — nó
không hiện khi gõ `/`, và venv nằm ngoài OneDrive nên **Windows phải tự cài**:

```
python -m venv %USERPROFILE%\.asreview-venv
%USERPROFILE%\.asreview-venv\Scripts\python -m pip install asreview
%USERPROFILE%\.asreview-venv\Scripts\asreview lab
```

Lệnh tiếng Việt `/sang-loc-asreview` (giải thích cách dùng, cảnh báo PRISMA và PII) về
theo `git pull` ở bước 2 — có sẵn ngay cả khi chưa cài ASReview.

Ba điều đã biết trước, khỏi mất công dò lại:
- ASReview khai hỗ trợ Python **≤ 3.13**; trên Mac nó vẫn chạy tốt với 3.14.6. Windows
  đang dùng 3.12.10 nên nằm trong vùng hỗ trợ chính thức.
- Giao diện web **chỉ có tiếng Anh** và repo không có hệ đa ngôn ngữ. Bác sĩ đã chọn giữ
  nguyên (04/08/2026) — chữ trên giao diện rất ít, chủ yếu hai nút Relevant / Not relevant.
- Dữ liệu dự án nằm ở `~/.asreview`, **ngoài OneDrive** → mỗi máy một kho riêng, không
  đồng bộ. Muốn mang dự án sang máy kia thì xuất/nhập file trong chính ASReview.

## 7. Đồng bộ bộ nhớ (không tự chạy được, phải gõ tay)

```
python tools\sync_memory.py
```

Bộ nhớ nằm ngoài OneDrive nên đây là bước **bắt buộc mỗi khi đổi máy**, cả hai chiều.

## 8. Kiểm sức khoẻ plugin

```
python tools\check_plugin_health.py
```

Nếu báo **N2** với `$HOME/workspace/medsci-skills` → chạy `sync\fix-medsci-root.ps1`
(phải chạy lại sau **mỗi** lần cập nhật medsci — đường dẫn cài có kèm mã phiên bản).

---

## Cái mới đáng dùng ngay: lộ trình làm trọn một đề tài

`LO-TRINH-DE-TAI.md` ở thư mục gốc liệt kê thứ tự gọi lệnh cho **nghiên cứu gốc (30 bước)** và
**tổng quan hệ thống (10 bước)**, kèm 6 cổng cần **người** ký (G2 · G4 · G5 · G8 · G9 · G10).

Gõ `/lo-trinh-de-tai <mã đề tài>` để biết đề tài đang ở bước nào, lệnh kế tiếp là gì, và cổng ký
gần nhất ai phải ký. Nó **không tự chạy bước nào** — chỉ chỉ đường.

## Lỗi font ở danh sách gõ `/` — đã tìm ra thủ phạm

Không phải mã hoá hỏng. Dữ liệu sạch (UTF-8, NFC, không BOM). Thủ phạm là **ký tự chỉ số**
`₂` (U+2082) và `²` (U+00B2) trong `CHA₂DS₂-VASc` và `I²` — font đơn cách của terminal thiếu
glyph nên vẽ thành ô vuông. Đã đổi sang `CHA2DS2-VASc` / `I2`. Các ký tự `— · → …` vẫn tốt.

Nếu Windows còn hỏng nặng hơn, có sẵn `tools/vietnamize/bo_dau.py` (chuyển mô tả sang không
dấu, phạm vi hẹp — chỉ trường hiển thị, có `--dry-run`). **Chỉ dùng khi thật sự cần**: nó là
bước lùi về ASCII, đọc kém hơn hẳn.

---

## Những thứ VẪN không đi qua Git (chỉ OneDrive hoặc phải làm lại từng máy)

| Thứ | Vì sao |
|---|---|
| `sync/memory/` | bộ nhớ cá nhân — cố ý loại khỏi GitHub, đi qua OneDrive + `sync_memory.py` |
| `tools/vietnamize/catalog_may/*.json` | bản chụp danh mục theo máy, chứa đường dẫn tuyệt đối |
| `~/.claude/CLAUDE.md` | nằm ngoài OneDrive → bước 4 |
| venv `~/.ebm-venv`, secrets `~/.ebm-secrets` | mỗi máy tự dựng, cố ý không sync |
| Quyền truy cập các MCP connector | phải cấp lại trên từng máy |

_Cần bác sĩ kiểm chứng — đây là ghi chú bàn giao, không thay phán đoán._
