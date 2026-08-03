# Việc cần chạy TRÊN MÁY MAC (bàn giao từ phiên Windows 03/08/2026)

> Đợi OneDrive **XANH** rồi mới bắt đầu. Mở terminal ở `~/OneDrive/Claude AI`.

Phiên Windows đã: cài kho `aipoch/medical-research-skills` làm plugin, Việt hoá
**100%** mọi mục gọi được (1650/1650), vá 8 lỗi công cụ, commit và push cả hai repo.
Máy Mac cần kéo về và chạy lại vài bước **của riêng máy Mac** — bản dịch nằm trong
Git nên tự có, nhưng việc *áp* bản dịch vào file plugin thì mỗi máy phải tự làm.

## 1. Kéo mã mới về (bắt buộc, làm trước)

```bash
cd ~/OneDrive/Claude\ AI && git pull
cd medical-ebm-automation && git pull && cd ..
```

## 2. Áp bản dịch cho plugin trên máy Mac

```bash
source ~/.ebm-venv/bin/activate
python3 tools/vietnamize/extract_catalog.py    # quét lại + ghi catalog_may/Mac.json
python3 tools/vietnamize/apply_vi.py           # áp 568 bản dịch mới
python3 tools/vietnamize/verify_vi.py          # phải ra "✓ Sạch"
python3 tools/vietnamize/check_chat_luong.py   # phải ra 0 lỗi chặn (L1/L2/L3/L7)
python3 tools/vietnamize/build_danh_muc.py     # sinh lại danh mục gộp 2 máy
```

**Vì sao phải chạy `extract_catalog.py` trên Mac:** bản chụp `catalog_may/Mac.json`
hiện tại là bản dựng lại từ danh mục Mac ngày 02/08, **trước** khi công cụ biết quét
`~/.claude/commands`. Chạy lại sẽ cập nhật đúng, và 11 lệnh tiếng Việt hết bị dán
nhãn nhầm là "chỉ Windows".

Sau bước này `DANH-MUC-CONG-CU.md` sẽ đổi (số liệu Mac tươi hơn) → commit lại:

```bash
git add tools/vietnamize/DANH-MUC-CONG-CU.md && git commit -m "chore(vietnamize): sinh lại danh mục sau khi quét lại máy Mac" && git push
```

## 3. Kiểm sức khoẻ plugin

```bash
python3 tools/check_plugin_health.py
```

Nếu báo **N2** với `$HOME/workspace/medsci-skills` → chạy `bash sync/fix-medsci-root.sh`.
(Máy Windows nay đã có bản tương ứng `sync/fix-medsci-root.ps1`, mới viết trong phiên này.)

## 4. Đồng bộ bộ nhớ (không tự chạy được, phải gõ tay)

```bash
python3 tools/sync_memory.py
```

## 5. Kiểm tổng thể

```bash
python3 tools/upgrade_verify.py
```

Kỳ vọng: 22/27 PASS. 5 bước lỗi (**10 · 12 · 20 · 23 · 24**) là cổng người-duyệt có
từ trước — G4 đề tài C1a chưa ký và cổng triển khai giám sát chờ UAT thật. **Không
phải** hồi quy của phiên này.

---

## Những thứ KHÔNG đi qua Git (chỉ đi qua OneDrive) — kiểm bằng mắt

| File | Ghi chú |
|---|---|
| `sync/*.ps1` | 4 script đã thêm BOM UTF-8 (PowerShell 5.1 không đọc được nếu thiếu) |
| `sync/fix-medsci-root.ps1` + `.cmd` | mới, bản Windows của `fix-medsci-root.sh` |
| `sync/MAC-LAM-TIEP.md` | chính file này |
| `tools/vietnamize/catalog_may/*.json` | bản chụp danh mục theo máy (cố ý gitignore) |

Repo gốc chỉ track `.claude/agents/ · sync/skills/ · tools/ · clinical_runtime/` — các
file trên nằm ngoài phạm vi đó theo đúng thiết kế.

## Bài học khi cài plugin bằng tay (áp dụng cho CẢ HAI máy)

`installPath` trong `~/.claude/plugins/installed_plugins.json` **phải nằm trong**
`~/.claude/plugins/`. Trỏ ra ngoài thì app im lặng bỏ qua, chỉ ghi ở
`~/Library/Logs/Claude/main.log` (Mac) hoặc `~/AppData/Roaming/Claude/logs/main.log`
(Windows):

```
[LocalPluginsReader] Skipping plugin with invalid path: <id> at <đường-dẫn>
[CCDMarketplacePluginManagerCLI] Skipping manifest write for ... out-of-bounds installPath
```

Kiểm nhanh xem một plugin đã cài THẬT chưa: phải có file
`~/.claude/plugins/.install-manifests/<plugin>@<marketplace>.json`. Không có = chưa cài.

Trên Windows kho aipoch nay nằm ở
`~/.claude/plugins/cache/aipoch-medical-research/aipoch-medical-research/1.0.0/`.

## Lưu ý về kho aipoch trên Mac

Kho ở `~/Documents/GitHub/medical-research-skills` có thể cũ hơn bản Windows vừa
clone (thư mục nhóm đã đổi từ `academic-writing` sang `Academic Writing`). Bản dịch
khoá theo **tên skill** nên vẫn áp đúng, không bắt buộc phải `git pull`; muốn hai máy
giống hệt thì pull thêm ở kho đó.
