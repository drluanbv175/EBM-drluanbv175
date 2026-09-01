#!/bin/bash
# Phát khoá Ed25519 theo VAI TRÒ cho cổng ký duyệt (G2/G4/G8/G9/G10 — scheme "ed1").
# ★ CHỈ BÁC SĨ TỰ BẤM — không nhờ agent (Claude Code/Codex) chạy hộ: khoá riêng phải
#   sinh ngoài tầm với của agent thì chữ ký mới là bằng chứng độc lập thật.
#
# Bản này nằm TRONG git (thay bản OneDrive-only cũ đã hỏng ngày 01/09/2026 vì gọi
# nhầm trình Python — venv ~/.ebm-venv có sẵn `cryptography` mà nút vẫn báo thiếu).
# Quy tắc chọn trình thông dịch chép đúng khuôn đã chạy được của
# medical-ebm-automation/"Thiết lập khóa ký duyệt cổng.command": ƯU TIÊN venv chuẩn.
cd "$(dirname "$0")/medical-ebm-automation" || {
  echo "✗ Không thấy thư mục medical-ebm-automation cạnh file này."; read -r _; exit 1;
}
if [ -x "$HOME/.ebm-venv/bin/python" ]; then
  PY="$HOME/.ebm-venv/bin/python"
else
  PY="$(command -v python3 || command -v python)"
fi
echo "Trình Python sẽ dùng: $PY"
echo ""
echo "Chọn vai trò cần phát khoá (khoá RIÊNG vào ~/.ebm-secrets — trao cho người giữ vai;"
echo "khoá CÔNG vào config/gate_ed25519_pubkeys — commit vào repo):"
select VAI in IRB STATISTICIAN INDEPENDENT_PEER_REVIEWER PI Thoat; do
  case "$VAI" in
    IRB|STATISTICIAN|INDEPENDENT_PEER_REVIEWER|PI)
      "$PY" tools/setup_gate_approval_key.py --role "$VAI" --ed25519
      echo "" ;;
    Thoat)
      break ;;
    *)
      echo "Gõ số 1-5." ;;
  esac
done
echo "──────────────────────────────────────────────"
echo "Nhớ: commit config/gate_ed25519_pubkeys/ sau khi phát; khoá .key KHÔNG commit."
echo "Nhấn Enter để đóng cửa sổ này..."
read -r _
