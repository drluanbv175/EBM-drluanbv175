#!/bin/bash
# Nhập KÊNH CẢNH BÁO (Gmail/SMTP/webhook) cho giám sát chứng cứ — đóng kiểm ESD10.
# ★ CHỈ BÁC SĨ TỰ BẤM — không dán mật khẩu/URL webhook vào khung chat với Claude Code.
cd "$(dirname "$0")" || exit 1
if [ -x "$HOME/.ebm-venv/bin/python" ]; then
  PY="$HOME/.ebm-venv/bin/python"
else
  PY="$(command -v python3 || command -v python)"
fi
"$PY" tools/nhap_kenh_canh_bao.py
echo ""
read -r -p "Bấm Enter để đóng cửa sổ..." _
