#!/usr/bin/env bash
# =============================================================
# copy-claude-md.sh  (macOS / Linux)
# Chép chỉ thị ngôn ngữ toàn cục từ hub OneDrive -> ~/.claude/CLAUDE.md
#
#   sync/CLAUDE-user-global.md   --(copy)-->   ~/.claude/CLAUDE.md
#
# CỐ Ý dùng COPY chứ không symlink: ~/.claude/CLAUDE.md là cấu hình nền, nếu
# OneDrive chưa tải file về (Files On-Demand) thì symlink sẽ làm MẤT chỉ thị
# một cách im lặng. Bản chép thật luôn đọc được kể cả khi offline.
#
# Idempotent: chạy lại nhiều lần đều an toàn (giống nhau thì không làm gì).
# Trên Windows hãy bấm đúp copy-claude-md.cmd.
# =============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$SCRIPT_DIR/CLAUDE-user-global.md"
DEST="$HOME/.claude/CLAUDE.md"

[ -f "$SRC" ] || { echo "✗ Không thấy bản nguồn: $SRC"; exit 1; }
mkdir -p "$(dirname "$DEST")"

if [ -f "$DEST" ] && cmp -s "$SRC" "$DEST"; then
  echo "✓ Đã khớp, không cần chép: $DEST"
  exit 0
fi

if [ -f "$DEST" ]; then
  # Bản trên máy MỚI HƠN hub -> có thể là sửa tay chưa đưa lên hub. Không đè mù.
  if [ "$DEST" -nt "$SRC" ]; then
    echo "⚠ Bản trên máy MỚI HƠN hub:"
    echo "    máy: $DEST"
    echo "    hub: $SRC"
    echo "  Nếu bản trên máy là bản đúng, hãy chép NGƯỢC lên hub rồi commit:"
    echo "    cp \"$DEST\" \"$SRC\""
    echo "  Nếu muốn lấy bản hub đè lên, chạy lại với: FORCE=1 bash \"$0\""
    [ "${FORCE:-0}" = "1" ] || exit 2
  fi
  TS="$(date +%Y%m%d-%H%M%S)"
  cp "$DEST" "${DEST}.bak-$TS"
  echo "  ↳ đã sao lưu bản cũ: ${DEST}.bak-$TS"
fi

cp "$SRC" "$DEST"
echo "✓ Đã cập nhật: $DEST"
