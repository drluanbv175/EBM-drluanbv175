#!/bin/bash
# Vá Route Scopus Qua VPN.command — 13/09/2026
#
# VÌ SAO CÓ: NCBI cần Kaspersky VPN đang mở (mạng nội bộ chặn khi không VPN);
# Scopus (Elsevier, đặt sau Cloudflare) chặn chính địa chỉ thoát của VPN đó.
# Kaspersky Split Tunneling tách theo ỨNG DỤNG, không theo domain — không giúp
# được vì NCBI và Scopus gọi ra từ CÙNG một tiến trình Python.
#
# CÁCH SỬA: thêm 2 route CỤ THỂ (chỉ đúng IP của Scopus/Elsevier) đi thẳng qua
# cổng mạng vật lý (bỏ qua tunnel VPN) — route cụ thể hơn sẽ THẮNG route mặc
# định "0/1 + 128.0/1" mà Kaspersky VPN dùng để hút hết traffic. Mọi thứ khác
# (gồm NCBI) vẫn đi qua VPN như cũ, không đổi gì.
#
# CẦN CHẠY LẠI sau mỗi lần: khởi động lại máy, kết nối lại Kaspersky VPN, hoặc
# đổi Wi-Fi/mạng (cổng mạng vật lý có thể đổi số). Bấm đúp file này để chạy lại
# — sẽ hỏi mật khẩu máy (cần quyền quản trị để sửa bảng định tuyến).
#
# GIỚI HẠN: IP của Scopus đi qua Cloudflare, CÓ THỂ đổi theo thời gian (dùng
# chung hạ tầng Cloudflare, không phải IP cố định riêng của Elsevier). Nếu
# sau này Scopus lại bị chặn dù đã chạy file này, có thể IP đã đổi — chạy lại
# `host api.elsevier.com` để lấy IP mới rồi báo Claude Code sửa file này.

set -e
echo "════════════════════════════════════════════════════════"
echo " VÁ ROUTE: cho Scopus đi thẳng, giữ VPN cho NCBI"
echo "════════════════════════════════════════════════════════"

CONG_VAT_LY=$(netstat -rn | awk '$1=="default" && $4!~/^utun/ {print $2; exit}')
if [ -z "$CONG_VAT_LY" ]; then
  echo "⚠ Không tìm thấy cổng mạng vật lý (default route không qua utun)."
  echo "  Có thể VPN đang TẮT — nếu vậy không cần chạy file này (Scopus đã chạy thẳng)."
  exit 1
fi
echo "Cổng mạng vật lý phát hiện được: $CONG_VAT_LY"

echo ""
echo "IP hiện tại của Scopus/Elsevier (qua Cloudflare):"
IPS=$(python3 -c "import socket; print(' '.join(socket.gethostbyname_ex('api.elsevier.com')[2]))" 2>/dev/null || echo "104.17.39.96 104.17.38.96")
echo "  $IPS"

echo ""
echo "Cần quyền quản trị để sửa bảng định tuyến — sẽ hỏi mật khẩu máy Mac."
for ip in $IPS; do
  echo "  → thêm route cho $ip qua $CONG_VAT_LY (bỏ qua VPN)"
  sudo route -n add -host "$ip" "$CONG_VAT_LY" 2>&1 || sudo route -n change -host "$ip" "$CONG_VAT_LY" 2>&1
done

echo ""
echo "════════════════════════════════════════════════════════"
echo " ĐÃ XONG — kiểm tra lại (không cần sudo):"
echo "════════════════════════════════════════════════════════"
for ip in $IPS; do
  echo "  route tới $ip:"
  route -n get "$ip" 2>&1 | grep -E "gateway|interface"
done
echo ""
echo "Bây giờ NCBI vẫn qua VPN, Scopus đi thẳng — mở Claude Code và thử lại cả hai."
