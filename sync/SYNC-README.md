# Đồng bộ Claude giữa Windows ↔ MacBook

Có **2 môi trường tách biệt**, cơ chế đồng bộ khác nhau:

| Môi trường | Là gì | Đồng bộ thế nào |
|---|---|---|
| **Cowork** (Claude Desktop) | Skills y khoa + harness bạn upload qua giao diện | **Tự động** qua tài khoản |
| **Code + Codex** | Skill riêng trong `~/.claude/skills` và `~/.codex/skills` | **Tự động** từ `sync/skills/` bằng liên kết + watcher |

## ⚡ MỘT LỆNH DUY NHẤT (21/08/2026)

```bash
python3 tools/dong_bo_tat_ca.py             # KIỂM — không ghi gì
python3 tools/dong_bo_tat_ca.py --ap-dung   # đồng bộ thật
```
Hoặc **bấm đúp** `sync/dong-bo-tat-ca.command` (Mac) · `sync/dong-bo-tat-ca.cmd` (Windows).

Lệnh này phủ **8 làn theo đúng thứ tự phụ thuộc** — xem bằng `--liet-ke-lan`:

| # | Làn | Việc |
|---|---|---|
| ① | An toàn đồng bộ | conflict-copy OneDrive · git hỏng · file lõi chưa tải. **🔴 là DỪNG TẤT CẢ** |
| ② | Git | commit chưa đẩy/chưa kéo — máy kia sẽ không thấy |
| ③ | Skill → Claude + Codex | `sync/skills/` → 2 runtime |
| ④ | Agent → Codex | enforce → sync → check |
| ⑤ | Plugin | đối chiếu 2 máy qua sổ khai chung + chiếu sang Codex |
| ⑥ | Hook SessionStart | cơ chế tự động đi giữa 2 máy |
| ⑦ | Bộ nhớ Claude | mirror 2 chiều, file mới hơn thắng |
| ⑧ | Kho công cụ | kho plugin so mốc chuẩn máy này |

Vì sao gộp: trước đó muốn máy này khớp máy kia phải nhớ đúng thứ tự **chín** thứ rời rạc, mà lệnh gộp duy nhất đang có (`upgrade_verify.py`) kiểm hệ agent chứ không chạm một làn đồng bộ nào. Quy trình phải nhớ chín bước là quy trình sẽ bị bỏ sót bước — và bỏ sót ở đây **không kêu**, nó chỉ làm máy kia thiếu lặng lẽ.

Ba luật giữ cho báo cáo không nói quá: thiếu **nguyên liệu** ghi «bỏ qua» chứ không tô đỏ · **mạng** là 🟡 còn **cấu hình** mới là 🔴 · dòng tổng kết chỉ kể làn **thật sự chạy**.

> Muốn nó tự chạy mỗi phiên: thêm `python3 tools/dong_bo_tat_ca.py --im-khi-on` vào hook `SessionStart` (im lặng khi mọi làn khớp), rồi `python3 tools/dong_bo_hook_sessionstart.py --xuat` để máy kia nhận cùng cấu hình.

---

Nguồn chuẩn duy nhất là `sync/skills/`. Cài liên kết một lần bằng:

```bash
bash sync/link-skills.sh          # macOS/Linux — symlink
```
```powershell
sync\link-skills.ps1              # Windows — junction (bấm đúp link-skills.cmd cũng được)
```

Cả hai script nối **cả `~/.claude/skills` lẫn `~/.codex/skills`** (sửa 21/08/2026 — trước đó chỉ nối Claude, nên Codex trắng skill trên cả hai máy).

Sửa file của skill đã liên kết có hiệu lực ngay. Hook `SessionStart` tự bắt skill mới, thay đổi registry plugin, cập nhật Cowork và dựng lại catalog/ZIP. Không dùng LaunchAgent đọc OneDrive vì macOS chặn tiến trình nền chưa có Full Disk Access. Kiểm tay (chạy được trên **cả hai** máy từ 21/08/2026):

```bash
python3 tools/dong_bo_skill_claude_codex.py --dong-bo-plugin
```

### Ba việc mỗi máy làm MỘT LẦN (21/08/2026)

| Việc | Lệnh | Vì sao |
|---|---|---|
| Nối skill vào Claude + Codex | `bash sync/link-skills.sh` · `sync\link-skills.ps1` | nguồn duy nhất `sync/skills/` |
| Nhận hook `SessionStart` | `python3 tools/dong_bo_hook_sessionstart.py --ap-dung` | `.claude/settings.json` bị gitignore nên hook không tự đi |
| Đối chiếu kho plugin | `python3 tools/dong_bo_plugin_claude_codex.py` | biết máy này thiếu plugin nào so với **sổ khai chung** |

Máy ĐANG CHẠY ĐÚNG (thường là Mac) chạy trước một lần để nạp bản nguồn vào git:

```bash
python3 tools/dong_bo_hook_sessionstart.py --xuat        # hook thật → sync/hooks-sessionstart.json
python3 tools/dong_bo_plugin_claude_codex.py --tao-so-khai   # dựng khung sync/plugin-manifest.json
```

Rồi mở `sync/plugin-manifest.json`, sửa `can_o_may` cho đúng Ý ĐỊNH và bật `da_xac_nhan: true`. Chừng nào còn `false`, công cụ chỉ **cảnh báo** — vì lúc đó `can_o_may` mới chỉ là suy từ hiện trạng, mà báo đỏ dựa trên suy đoán sẽ dạy người ta bỏ qua cả cảnh báo thật.

> Công cụ **không** tự cài/gỡ plugin qua mạng và **không** sửa `enabledPlugins`. Bài học 11/08: gỡ một mục khỏi `enabledPlugins` khiến Claude Code cài lại 278 MB. Vắng mặt trong `enabledPlugins` = **BẬT**, chỉ ghi rõ `false` mới là tắt.

---

## 1) Cowork — tự động (không cần làm gì)

Skills của Cowork lưu trên **tài khoản Claude** (server), không phải file cục bộ.

- Trên MacBook: cài **Claude Desktop**, **đăng nhập đúng tài khoản** đang dùng ở Windows.
- Mọi custom Skill (25 skill y khoa, và harness nếu đã upload) sẽ tự kéo về.
- ⚠️ Sửa file manifest cục bộ là vô ích — app ghi đè từ server mỗi lần mở. Muốn thêm/sửa skill thì làm qua **giao diện Skills**, nó sẽ tự sync sang máy kia.

> Lưu ý: trong Cowork, harness chỉ là phần hướng dẫn — binary + hooks ép quy trình KHÔNG chạy. Muốn đầy đủ thì dùng Code CLI (mục 2).

---

## 2) Code (CLI) và Codex — liên kết tự động

Cấu hình runtime vẫn nằm trên từng máy, nhưng skill riêng dùng liên kết tới nguồn OneDrive. Chạy script cài đặt một lần trên mỗi máy; các lần sửa sau không cần chép lại.

### Trên MacBook
1. Cài Claude Code CLI và `git`.
2. Mở Terminal, chạy:
   ```bash
   bash "$HOME/OneDrive/Claude AI/sync/setup-claude-cli.sh"
   ```
   (Đường dẫn OneDrive trên Mac thường là `~/OneDrive` hoặc `~/Library/CloudStorage/OneDrive-Personal` — chỉnh lại cho đúng.)
3. Script sẽ: clone/cập nhật harness, mirror skills → `~/.claude/skills`, agents → `~/.claude/agents`, và kiểm tra binary.
4. Mở `claude` trong một thư mục git, gõ `/harness-plan`.

### Cập nhật về sau
Trên macOS và Windows, nội dung skill đã có đi qua symlink/junction ngay lập tức. Hook `SessionStart` tự tạo liên kết cho skill mới. Trên Windows có thể chạy lại `link-skills.ps1` sau khi thêm thư mục mới nếu chưa mở phiên Claude/Codex.

> ⚠️ Windows dùng **junction**, không phải symlink: `os.symlink` ném WinError 1314 khi máy chưa bật Developer Mode (đã đo trên chính máy này 17/08/2026). `tools/lien_ket_da_nen.py` chọn đúng cơ chế theo nền, và nhận diện junction bằng `os.path.isjunction` — `Path.is_symlink()` trả **False** cho junction, dùng nhầm thì mỗi lượt chạy lại đẻ thêm một bản `.bak`.

> Nếu CLI trên máy đó hỗ trợ `/plugin`, có thể dùng cách "xịn" hơn:
> ```
> /plugin marketplace add Chachamaru127/claude-code-harness
> /plugin install claude-code-harness@claude-code-harness-marketplace
> /harness-setup
> ```
> Cách này tự bật cả hooks. Script ở trên là phương án thủ công khi /plugin không có.

---

## 3) File dự án / làm việc

Đặt trong **OneDrive** (`~/OneDrive/Claude AI/...`). Cài OneDrive trên Mac và đăng nhập cùng tài khoản → tự sync.
- ⚠️ Đừng để **cả hai máy cùng mở/ghi một file lúc** → tránh xung đột bản sao. Làm xong ở máy này, đợi OneDrive sync xanh rồi mới làm ở máy kia.

---

## 4) Memory của CLI — đồng bộ liền mạch (QUAN TRỌNG)

Memory CLI (gồm `MEMORY.md` và các file ngữ cảnh dự án) nằm ở
`~/.claude/projects/<đường-dẫn-mã-hóa>/memory/`, **bên ngoài OneDrive** nên mặc định
KHÔNG đi theo sang máy kia → đổi máy là Claude "mất trí nhớ".

**Cách giải quyết:** đặt 1 thư mục memory **chung** trong OneDrive (`sync/memory/`) rồi
trỏ thư mục memory cục bộ của mỗi máy vào đó. Từ đó OneDrive tự đồng bộ **liên tục**.

| Máy | Cơ chế | Cách làm (chạy 1 lần/máy) |
|---|---|---|
| **Mac/Linux** | symlink | `bash "$HOME/OneDrive/Claude AI/sync/link-memory.sh"` (hoặc tự chạy khi cài bằng `setup-claude-cli.sh`) |
| **Windows** | junction (không cần admin) | Bấm đúp **`sync/link-memory.cmd`** |

Script tự: tạo `sync/memory/`, gộp memory đang có (không mất dữ liệu máy nào),
sao lưu thư mục cũ thành `memory.bak-…`, rồi tạo liên kết. Chạy lại nhiều lần đều an toàn.

> ⚠️ **OneDrive Files On-Demand:** để chắc chắn memory luôn đọc được kể cả khi offline,
> chuột phải thư mục `sync/memory` → **"Always keep on this device"** / "Luôn giữ trên thiết bị này".
> (File memory rất nhỏ ~30KB nên hiếm khi bị đẩy lên mây, nhưng bật cho chắc.)

> ⚠️ **Không mở Claude trên CẢ HAI máy cùng lúc** rồi sửa memory song song — dễ tạo bản
> sao xung đột của OneDrive. Làm xong ở máy này, đợi OneDrive xanh rồi mới qua máy kia.

### Bàn giao công việc giữa 2 máy
Dùng **`Plans.md`** trong thư mục dự án (đã tự sync qua OneDrive) làm điểm bàn giao:
mục **In Progress** = đang làm dở, **Last Update** = chốt phiên gần nhất. Đầu mỗi phiên
Claude đọc `Plans.md` (theo `CLAUDE.md` §3) nên biết ngay tiếp nối từ đâu.

---

## 5) Chỉ thị ngôn ngữ toàn cục (`~/.claude/CLAUDE.md`)

Skill và plugin cài từ marketplace **viết bằng tiếng Anh**, nhưng đầu ra vẫn ra tiếng Việt
nếu có chỉ thị ngôn ngữ ở tầng user. Chỉ thị đó nằm ở `~/.claude/CLAUDE.md` — **ngoài
OneDrive**, nên phải cài lại trên từng máy (giống venv và secrets).

| Máy | Cách làm (chạy 1 lần/máy, và mỗi khi sửa bản nguồn) |
|---|---|
| **Mac/Linux** | `bash "$HOME/OneDrive/Claude AI/sync/copy-claude-md.sh"` |
| **Windows** | Bấm đúp **`sync/copy-claude-md.cmd`** |

- Bản nguồn duy nhất: **`sync/CLAUDE-user-global.md`** — sửa ở đây rồi chạy lại script.
- Script **chép** chứ không symlink (cố ý): `~/.claude/CLAUDE.md` là cấu hình nền, nếu
  OneDrive chưa tải file về (Files On-Demand) thì symlink sẽ làm **mất chỉ thị một cách im
  lặng**; bản chép thật luôn đọc được kể cả khi offline.
- Nếu bản trên máy mới hơn hub, script **dừng lại (mã thoát 2) và không đè** — nó in sẵn
  lệnh chép ngược lên hub. Muốn lấy bản hub đè lên: `FORCE=1 bash sync/copy-claude-md.sh`.
- Ghi chú phạm vi: file này chỉ quy định **ngôn ngữ**. Doctrine chuyên môn vẫn nằm ở
  `CLAUDE.md` của từng dự án; cả hai cùng có hiệu lực.

---

## 6) Việt hoá phần hiển thị khi gõ `/`

Có **hai lớp**, cơ chế đồng bộ khác nhau — đừng nhầm:

| Lớp | Là gì | Bị cập nhật plugin ghi đè? | Cài lại bằng |
|---|---|---|---|
| **Mô tả skill/lệnh/agent** (1665 mục trên Mac 03/08/2026) | Trường `description` trong frontmatter của chính plugin | **CÓ** — nằm trong thư mục cài có số phiên bản | `tools/vietnamize/apply_vi.py` |
| **Lệnh tiếng Việt của bác sĩ** (52 lệnh) | File riêng trong `~/.claude/commands/` | Không | `sync/copy-commands-vi.sh` (Windows: bấm đúp `.cmd`) |

Số mục khác nhau giữa hai máy là **bình thường** — mỗi máy cài bộ plugin riêng.
`DANH-MUC-CONG-CU.md` gộp bản chụp của cả hai (1920 mục) nên luôn lớn hơn số của một máy.

Mô tả nằm rải ở **ba nguồn**, script quét cả ba:
1. `~/.claude/plugins/` — plugin cài qua Claude Code.
2. `~/Library/Application Support/Claude/local-agent-mode-sessions/.../rpm/` — plugin cài từ
   **claude.ai** (healthcare, legal, data, engineering, zoom, figma…). Thư mục này do app
   quản lý nên **khả năng bị ghi đè cao hơn** — nếu thấy nhóm này trở lại tiếng Anh, chạy lại
   chuỗi lệnh bên dưới.
3. Skill Cowork, skill riêng và 50 agent EBM.

**Sau MỖI lần cập nhật hoặc cài thêm plugin**, chạy trong `Claude AI/` (nên bật venv để có PyYAML):

```bash
source ~/.ebm-venv/bin/activate
python3 tools/vietnamize/extract_catalog.py   # quét lại, báo mục MỚI chưa có tiếng Việt
python3 tools/vietnamize/apply_vi.py          # áp bản dịch
python3 tools/vietnamize/verify_vi.py         # kiểm: frontmatter hợp lệ, bản gốc còn nguyên
python3 tools/vietnamize/check_chat_luong.py  # chấm chất lượng: mô tả có nói dùng khi nào không
python3 tools/vietnamize/build_danh_muc.py    # sinh lại DANH-MUC-CONG-CU.md
```

- `verify_vi.py` trả lời "có ghi đúng không", `check_chat_luong.py` trả lời "đọc có hiểu
  không" — hai câu khác nhau, chạy cả hai. Lớp thứ hai từng bắt được một mô tả gán nhầm
  hẳn sang plugin khác (`/bio-research:start` mang mô tả của Zoom).

- Bản gốc tiếng Anh **luôn được giữ** trong `description-en` + vân tay `description-src`;
  `apply_vi.py --restore` trả tất cả về tiếng Anh bất cứ lúc nào.

### Plugin nạp được nhưng chạy vào là gãy

Việt hoá xong không có nghĩa plugin dùng được. Bộ **medsci-skills** là ví dụ: skill hiện đủ
khi gõ `/`, gọi ra cũng bình thường, nhưng mọi lệnh bên trong đều trỏ tới
`${MEDSCI_SKILLS_ROOT:-$HOME/workspace/medsci-skills}` — thư mục **không tồn tại** khi cài qua
Claude Code (skill thật nằm trong `~/.claude/plugins/cache/medsci-skills/...`). Sửa bằng:

```bash
bash "$HOME/OneDrive/Claude AI/sync/fix-medsci-root.sh"
```

Chạy lại sau **mỗi lần cập nhật medsci** — đường dẫn cài có kèm mã phiên bản nên sẽ đổi.

Soi loại lỗi này trên **mọi** plugin bằng:

```bash
python3 tools/check_plugin_health.py
```

Nó kiểm 4 nhóm: đường dẫn cài biến mất · thư mục gốc gọi script không tồn tại · công cụ ngoài
chưa cài (node, R, pandoc, quarto…) · skill thiếu mô tả. Đây là thứ **không phép đếm nào bắt
được** — chỉ lộ khi thật sự chạy.
- Gõ `/cong-cu-gi <việc cần làm>` khi không nhớ nên dùng công cụ nào.
- Phải **mở lại phiên Claude Code** thì mô tả mới hiện — frontmatter chỉ đọc lúc nạp.

### Gõ tiếng Việt để tìm skill

Khi gõ `/`, bộ lọc khớp theo **TÊN lệnh**. Tên skill là tiếng Anh (`calc-sample-size`,
`check-reporting`) nên gõ "cỡ mẫu" không ra — dù mô tả đã Việt hoá. Cách chắc chắn là có
sẵn lệnh MANG TÊN TIẾNG VIỆT trỏ về đúng skill đó.

52 lệnh như vậy đã cài. Gõ `/` rồi vài chữ tiếng Việt không dấu là ra:
`/tinh-co-mau` · `/kham-ca-benh` · `/kiem-chuan-bao-cao` · `/chon-tap-chi` ·
`/tra-loi-phan-bien` · `/kiem-trich-dan` · `/lam-sach-du-lieu` …

Thêm lệnh mới: sửa `tools/vietnamize/lenh_viet.json` rồi chạy

```bash
python3 tools/vietnamize/sinh_lenh_viet.py    # kiểm đích có thật rồi mới sinh
bash sync/copy-commands-vi.sh                 # cài lên máy
```

Script TỪ CHỐI sinh lệnh trỏ vào skill không có trên máy — một lệnh gọi ra rồi báo
"không tìm thấy" còn tệ hơn là không có lệnh.
