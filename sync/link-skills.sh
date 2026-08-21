#!/usr/bin/env bash
# =============================================================
# link-skills.sh  (macOS / Linux)
# Trỏ từng skill EBM trong hub -> ~/.claude/skills/<tên> VÀ ~/.codex/skills/<tên>
# bằng symlink, để đồng bộ Mac<->Windows.
#
#   sync/skills/<tên>   --(symlink)-->   ~/.claude/skills/<tên>
#                        \-(symlink)-->  ~/.codex/skills/<tên>
#
# Idempotent: chạy lại nhiều lần đều an toàn.
# Trên Windows hãy dùng link-skills.cmd / link-skills.ps1 (junction).
# Bỏ qua các thư mục bắt đầu bằng "_" (vd _vietnamize.py không phải skill).
#
# HAI THỨ ĐÃ SỬA 21/08/2026:
#   1. NỐI CẢ CODEX. Bản cũ chỉ nối ~/.claude/skills, nên Codex không thấy skill
#      nào của bác sĩ — trong khi SYNC-README và AGENTS.md đều nói cả hai runtime
#      dùng chung nguồn sync/skills.
#   2. SAO LƯU RA NGOÀI vùng quét. Bản cũ để bản cũ thành "<tên>.bak-<giờ>" NGAY
#      TRONG ~/.claude/skills — mà Claude Code nạp mọi thư mục ở đó thành skill,
#      nên menu "/" hiện HAI bản trùng tên và bản cũ mang mô tả cũ. Đã xảy ra thật
#      03/08/2026 với kham-ngoai-tru-ebm và tuan-thu-dieu-tri; bản .ps1 của Windows
#      đã vá từ hồi đó, bản .sh này thì chưa — đúng họ lỗi "chạy được ở đây không
#      có nghĩa chạy được ở kia" mà CLAUDE.md dặn phải kiểm trên CẢ HAI máy.
# =============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HUB="$SCRIPT_DIR/skills"                 # .../Claude AI/sync/skills

echo "==> Hub : $HUB"
echo ""

tong=0
for DEST in "$HOME/.claude/skills" "$HOME/.codex/skills"; do
  BACKUP="${DEST}-backup"                # NGOÀI vùng Claude/Codex quét skill
  mkdir -p "$DEST"
  echo "==> Đích: $DEST"

  count=0
  for d in "$HUB"/*/; do
    name="$(basename "$d")"
    case "$name" in
      _*) continue ;;                    # bỏ thư mục nội bộ
    esac
    [ -f "${d}SKILL.md" ] || continue    # chỉ link thư mục là skill thật

    target="$DEST/$name"
    if [ -L "$target" ]; then
      ln -sfn "${d%/}" "$target"         # đã là symlink -> trỏ lại cho chắc
      echo "    ↻ $name (cập nhật symlink)"
    elif [ -e "$target" ]; then
      TS="$(date +%Y%m%d-%H%M%S)"
      mkdir -p "$BACKUP"
      mv "$target" "$BACKUP/$name.bak-$TS"
      ln -s "${d%/}" "$target"
      echo "    ⚠ $name (đã có sẵn → sao lưu vào $(basename "$BACKUP")/$name.bak-$TS)"
    else
      ln -s "${d%/}" "$target"
      echo "    + $name (symlink mới)"
    fi
    count=$((count+1))
  done
  echo "    → $count skill"
  echo ""
  tong=$((tong+count))
done

echo "HOÀN TẤT: đã liên kết $tong lượt (skill × 2 runtime)."
echo "Kiểm tra: ls -la \"$HOME/.claude/skills\" \"$HOME/.codex/skills\" | grep ' -> '"
echo "Mở 'claude' và gõ tên skill (vd 'tổng quan y văn về ...') để dùng."
