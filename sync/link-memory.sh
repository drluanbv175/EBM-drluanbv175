#!/usr/bin/env bash
# =============================================================
# link-memory.sh  (macOS / Linux)
# Trỏ thư mục memory của Claude CLI -> hub chung trong OneDrive,
# để "trí nhớ" đồng bộ liền mạch giữa Mac và Windows.
#
#   ~/.claude/projects/<encoded>/memory   --(symlink)-->   sync/memory
#
# Idempotent: chạy lại nhiều lần đều an toàn.
# Trên Windows hãy dùng link-memory.cmd / link-memory.ps1 (junction).
# =============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"      # .../Claude AI
HUB="$SCRIPT_DIR/memory"                         # .../Claude AI/sync/memory
mkdir -p "$HUB"

# 1) Tìm thư mục project cục bộ: ưu tiên cái có sẵn (*Claude-AI), nếu không thì tự tính tên mã hóa
LOCALPARENT="$(ls -d "$HOME"/.claude/projects/*Claude-AI 2>/dev/null | head -1 || true)"
if [ -z "$LOCALPARENT" ]; then
  ENC="$(printf '%s' "$PROJ_ROOT" | sed 's/[^a-zA-Z0-9]/-/g')"
  LOCALPARENT="$HOME/.claude/projects/$ENC"
  mkdir -p "$LOCALPARENT"
  echo "==> Tạo project dir mới: $LOCALPARENT"
fi
LOCAL="$LOCALPARENT/memory"
echo "==> Hub  : $HUB"
echo "==> Local: $LOCAL"

# 2) Đồng bộ nội dung 1 lần trước khi link (không mất dữ liệu của máy nào)
if ! ls "$HUB"/*.md >/dev/null 2>&1; then
  if [ -d "$LOCAL" ] && [ ! -L "$LOCAL" ] && ls "$LOCAL"/*.md >/dev/null 2>&1; then
    echo "==> Hub trống → seed từ local"
    cp -p "$LOCAL"/*.md "$HUB"/ 2>/dev/null || true
  fi
else
  if [ -d "$LOCAL" ] && [ ! -L "$LOCAL" ]; then
    for f in "$LOCAL"/*.md; do
      [ -e "$f" ] || continue
      b="$(basename "$f")"
      [ -e "$HUB/$b" ] || { echo "==> Bổ sung file local còn thiếu vào hub: $b"; cp -p "$f" "$HUB/"; }
    done
  fi
fi

# 3) Tạo symlink
if [ -L "$LOCAL" ]; then
  echo "==> Đã là symlink: $LOCAL -> $(readlink "$LOCAL")"
elif [ -d "$LOCAL" ]; then
  TS="$(date +%Y%m%d-%H%M%S)"
  echo "==> Sao lưu $LOCAL -> memory.bak-$TS"
  mv "$LOCAL" "${LOCAL}.bak-$TS"
  ln -s "$HUB" "$LOCAL"
  echo "==> Đã tạo symlink"
else
  ln -s "$HUB" "$LOCAL"
  echo "==> Đã tạo symlink (mới)"
fi

echo ""
echo "HOÀN TẤT. memory -> $(readlink "$LOCAL")"
ls -la "$HUB"/*.md 2>/dev/null || echo "(hub chưa có file .md — sẽ tạo khi dùng)"
