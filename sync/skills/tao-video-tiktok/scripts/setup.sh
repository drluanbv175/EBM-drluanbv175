#!/usr/bin/env bash
# setup.sh — Cài phụ thuộc cho skill tạo video TikTok (khi KHÔNG dùng ~/.ebm-venv).
# Trên máy của bác sĩ đã có sẵn ~/.ebm-venv (đủ edge-tts + imageio-ffmpeg + Pillow),
# nên thường KHÔNG cần chạy file này. Dùng khi chạy ở môi trường mới.
set -e

PYBIN="${PYBIN:-python3}"
VENV="${VENV:-$HOME/.tiktok-venv}"

echo "== Thiết lập môi trường tao-video-tiktok =="
echo "Python: $($PYBIN --version)"

if [ ! -d "$VENV" ]; then
  echo "Tạo venv tại $VENV ..."
  "$PYBIN" -m venv "$VENV"
fi

# shellcheck disable=SC1091
source "$VENV/bin/activate"
python -m pip install --upgrade pip
python -m pip install "edge-tts>=7.0" "imageio-ffmpeg>=0.4.9" "Pillow>=10.0"

echo ""
echo "Xong. Chạy kiểm tra:"
echo "  $VENV/bin/python $(dirname "$0")/kiem_tra.py"
echo "Dựng video:"
echo "  $VENV/bin/python $(dirname "$0")/tao_video.py KICH_BAN.md --out THU_MUC_RA"
echo ""
echo "Ghi chú: giọng macOS 'Linh' (fallback offline) chỉ có trên macOS."
