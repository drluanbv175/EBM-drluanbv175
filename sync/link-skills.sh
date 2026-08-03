#!/usr/bin/env bash
# =============================================================
# link-skills.sh  (macOS / Linux)
# Trỏ từng skill EBM (đã Việt hóa) trong hub OneDrive
# -> ~/.claude/skills/<tên>  bằng symlink, để đồng bộ Mac↔Windows.
#
#   sync/skills/<tên>   --(symlink)-->   ~/.claude/skills/<tên>
#
# Idempotent: chạy lại nhiều lần đều an toàn.
# Trên Windows hãy dùng link-skills.cmd / link-skills.ps1 (junction).
# Bỏ qua các thư mục bắt đầu bằng "_" (vd _vietnamize.py không phải skill).
# =============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HUB="$SCRIPT_DIR/skills"                 # .../Claude AI/sync/skills
DEST="$HOME/.claude/skills"              # đích Claude CLI đọc skill
mkdir -p "$DEST"

echo "==> Hub : $HUB"
echo "==> Đích: $DEST"
echo ""

count=0
for d in "$HUB"/*/; do
  name="$(basename "$d")"
  case "$name" in
    _*) continue ;;                      # bỏ thư mục nội bộ
  esac
  [ -f "${d}SKILL.md" ] || continue      # chỉ link thư mục là skill thật

  target="$DEST/$name"
  if [ -L "$target" ]; then
    # đã là symlink -> trỏ lại cho chắc
    ln -sfn "$d" "$target"
    echo "    ↻ $name (cập nhật symlink)"
  elif [ -e "$target" ]; then
    # tồn tại dạng thư mục/ file thật -> sao lưu rồi link
    TS="$(date +%Y%m%d-%H%M%S)"
    mv "$target" "${target}.bak-$TS"
    ln -s "$d" "$target"
    echo "    ⚠ $name (đã có sẵn → sao lưu .bak-$TS, tạo symlink mới)"
  else
    ln -s "$d" "$target"
    echo "    + $name (symlink mới)"
  fi
  count=$((count+1))
done

echo ""
echo "HOÀN TẤT: đã liên kết $count skill."
echo "Kiểm tra: ls -la \"$DEST\" | grep ' -> '"
echo "Mở 'claude' và gõ tên skill (vd 'tổng quan y văn về ...') để dùng."
