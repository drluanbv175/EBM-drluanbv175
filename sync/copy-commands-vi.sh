#!/usr/bin/env bash
# =============================================================
# copy-commands-vi.sh  (macOS / Linux)
# Chép bộ LỆNH TIẾNG VIỆT từ hub OneDrive -> ~/.claude/commands/
#
#   sync/commands-vi/*.md   --(copy)-->   ~/.claude/commands/*.md
#
# Đây là các lệnh do bác sĩ sở hữu, nằm NGOÀI thư mục plugin nên KHÔNG bị
# ghi đè khi cập nhật plugin — khác với mô tả skill (phải chạy lại apply_vi.py).
#
# Idempotent: chạy lại bao nhiêu lần cũng an toàn. Chỉ chép file trong
# commands-vi/, không đụng file khác bác sĩ tự thêm vào ~/.claude/commands/.
# =============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$SCRIPT_DIR/commands-vi"
DEST="$HOME/.claude/commands"

[ -d "$SRC" ] || { echo "✗ Không thấy thư mục nguồn: $SRC"; exit 1; }
mkdir -p "$DEST"

moi=0; capnhat=0; giu=0
for f in "$SRC"/*.md; do
  ten="$(basename "$f")"
  dich="$DEST/$ten"
  if [ ! -f "$dich" ]; then
    cp "$f" "$dich"; moi=$((moi+1)); echo "  + $ten (mới)"
  elif cmp -s "$f" "$dich"; then
    giu=$((giu+1))
  else
    TS="$(date +%Y%m%d-%H%M%S)"
    cp "$dich" "${dich}.bak-$TS"
    cp "$f" "$dich"; capnhat=$((capnhat+1)); echo "  ↻ $ten (cập nhật, bản cũ lưu .bak-$TS)"
  fi
done
echo "✓ Xong: $moi mới · $capnhat cập nhật · $giu không đổi → $DEST"
echo "  Mở lại phiên Claude Code rồi gõ / để thấy các lệnh tiếng Việt."
