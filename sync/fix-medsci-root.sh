#!/usr/bin/env bash
# =============================================================
# fix-medsci-root.sh  (macOS / Linux)
# Trỏ ~/workspace/medsci-skills về bản medsci-skills đang cài.
#
# VÌ SAO CẦN: các script bên trong skill medsci gọi nhau bằng đường dẫn
#     "${MEDSCI_SKILLS_ROOT:-$HOME/workspace/medsci-skills}/skills/..."
# Khi cài qua Claude Code, skill nằm ở
#     ~/.claude/plugins/cache/medsci-skills/<plugin>/<hash>/skills/...
# nên mặc định trỏ vào thư mục KHÔNG TỒN TẠI → mọi lệnh trong skill báo
# "No such file or directory". Skill vẫn nạp được, chỉ gãy ở bước chạy script.
#
# Hash phiên bản đổi sau mỗi lần cập nhật plugin → chạy lại script này khi đó.
# Idempotent: chạy lại bao nhiêu lần cũng an toàn.
# =============================================================
set -euo pipefail

CACHE="$HOME/.claude/plugins/cache/medsci-skills"
DICH="$HOME/workspace/medsci-skills"

[ -d "$CACHE" ] || { echo "✗ Chưa cài bộ medsci-skills (không thấy $CACHE)"; exit 1; }

# Chọn bản cài có ĐỦ skill nhất; mọi plugin medsci đều chứa trọn bộ, nhưng
# nếu một bản đang tải dở thì bản khác vẫn cứu được.
NGUON=""; NHIEU=0
for d in "$CACHE"/*/*/; do
  [ -d "$d/skills" ] || continue
  n=$(find "$d/skills" -maxdepth 1 -mindepth 1 -type d | wc -l | tr -d ' ')
  if [ "$n" -gt "$NHIEU" ]; then NHIEU=$n; NGUON="${d%/}"; fi
done
[ -n "$NGUON" ] || { echo "✗ Không thấy thư mục skills nào trong $CACHE"; exit 1; }

mkdir -p "$(dirname "$DICH")"

if [ -L "$DICH" ]; then
  HIEN_TAI="$(readlink "$DICH")"
  if [ "$HIEN_TAI" = "$NGUON" ]; then
    echo "✓ Đã trỏ đúng rồi: $DICH → $NGUON ($NHIEU skill)"
    exit 0
  fi
  ln -sfn "$NGUON" "$DICH"
  echo "↻ Cập nhật liên kết (bản cũ: $HIEN_TAI)"
elif [ -e "$DICH" ]; then
  # Có thư mục thật ở đó — KHÔNG đè, để bác sĩ tự quyết
  echo "⚠ $DICH đang là thư mục thật, không phải liên kết."
  echo "  Không đụng vào. Nếu muốn dùng bản cài của Claude Code, hãy đổi tên nó rồi chạy lại."
  exit 2
else
  ln -s "$NGUON" "$DICH"
  echo "+ Tạo liên kết mới"
fi

echo "✓ $DICH → $NGUON"
echo "  ($NHIEU skill dùng được)"
echo
echo "Kiểm nhanh:"
python3 "$DICH/skills/self-review/scripts/check_classical_style.py" --help >/dev/null 2>&1 \
  && echo "  ✓ script trong skill chạy được" \
  || echo "  ✗ script vẫn lỗi — xem lại quyền hoặc bản cài"
