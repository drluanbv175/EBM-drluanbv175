#!/bin/bash
# Chạy MỘT LƯỢT các việc chỉ làm được trên máy Mac (audit/17 §6bis mục 1, 4, 5) — 26/09/2026.
# Bác sĩ bấm đúp. Nút KHÔNG commit, KHÔNG push, KHÔNG ký cổng, KHÔNG chạm khoá/mật khẩu.
# Việc chỉ bác sĩ làm (nhập kênh cảnh báo, phát khoá Ed25519) được NHẮC ở cuối, không chạy hộ.
# Toàn bộ đầu ra ghi vào ~/.ebm-logs/viec-mac-<ngày-giờ>.log để gửi lại cho Claude đọc.

GOC="$(cd "$(dirname "$0")" && pwd)"
ENGINE="$GOC/medical-ebm-automation"
if [ -x "$HOME/.ebm-venv/bin/python" ]; then
  PY="$HOME/.ebm-venv/bin/python"
else
  PY="$(command -v python3 || command -v python)"
fi
mkdir -p "$HOME/.ebm-logs"
LOG="$HOME/.ebm-logs/viec-mac-$(date '+%Y%m%d-%H%M').log"
KET_QUA=()

buoc() {  # buoc "<tên>" <thư mục> <lệnh...>
  local ten="$1" noi="$2"; shift 2
  echo "" | tee -a "$LOG"
  echo "===== $ten =====" | tee -a "$LOG"
  ( cd "$noi" && "$@" ) 2>&1 | tee -a "$LOG"
  local rc=${PIPESTATUS[0]}
  KET_QUA+=("$ten → mã thoát $rc")
  return "$rc"
}

echo "Nhật ký: $LOG"
echo "Python: $PY" | tee -a "$LOG"
if [ ! -d "$ENGINE" ]; then
  echo "✗ Không thấy medical-ebm-automation/ cạnh nút này — nút phải nằm ở gốc thư mục OneDrive «Claude AI»." | tee -a "$LOG"
  read -r -p "Bấm Enter để đóng..." _; exit 1
fi

# ⓪ Cổng an toàn đồng bộ OneDrive — 🔴 (mã 2) thì DỪNG hẳn (CLAUDE.md §0.7).
buoc "⓪ An toàn đồng bộ OneDrive" "$GOC" "$PY" tools/sync_safety_check.py
if [ "$?" -eq 2 ]; then
  echo "🔴 DỪNG: đồng bộ OneDrive chưa an toàn — đợi OneDrive xanh rồi bấm lại." | tee -a "$LOG"
  read -r -p "Bấm Enter để đóng..." _; exit 2
fi

# ① Vòng giám sát tuần đầy đủ (chủ thu thập duy nhất; ghi sổ cái/hub, có thể gửi email nếu đã có kênh).
buoc "① Giám sát an toàn thuốc hằng tuần" "$ENGINE" bash scripts/weekly_safety.sh
# ② Cổng triển khai giám sát, bản online (ESD06–ESD10).
buoc "② Cổng triển khai giám sát (online)" "$ENGINE" "$PY" tools/verify_evidence_surveillance_deployment.py --online
# ③ Bộ chốt + kiểm toàn hệ + độ tươi — trên Mac đủ dữ liệu OneDrive nên canh được cả mục ⚪ của Cloud.
buoc "③a Chốt hồi quy bài học" "$GOC" "$PY" tools/chot_hoi_quy_bai_hoc.py
buoc "③b Kiểm toàn hệ" "$GOC" "$PY" tools/audit_ebm_system.py
buoc "③c Độ tươi chứng cứ" "$GOC" "$PY" tools/kiem_do_tuoi_chung_cu.py
# ④ Soạn ứng viên bộ vàng K1–K4 (không ghi đè tệp đã có nhãn bác sĩ).
buoc "④ Ứng viên bộ vàng kiểm chéo ngữ nghĩa" "$GOC" "$PY" tools/kiem_cheo_ngu_nghia.py --ung-vien-bo-vang
# ⑤ Hệ còn gì để làm.
buoc "⑤ Hệ còn gì để làm" "$GOC" "$PY" tools/tu_de_xuat_viec.py

echo "" | tee -a "$LOG"
echo "===== TÓM TẮT =====" | tee -a "$LOG"
for d in "${KET_QUA[@]}"; do echo "  $d" | tee -a "$LOG"; done
cat <<'EOF' | tee -a "$LOG"

Mã thoát khác 0 KHÔNG tự động là lỗi (vd kiểm toàn hệ trả 1 khi còn việc của người thật) — đọc
nhật ký hoặc gửi tệp nhật ký cho Claude đọc giúp.

CÒN LẠI — CHỈ BÁC SĨ LÀM (nút này không chạy hộ):
  • Bấm «Nhap Kenh Canh Bao.command» → rồi: cd medical-ebm-automation && python run.py notify-test
  • Bấm «Phat Khoa Ed25519.command» (khoá cho IRB / phản biện độc lập)
  • Mở quality/eval/kiem-cheo-ngu-nghia/bo-vang.cho-duyet.json, điền «nhan_bac_si» cho từng mục
  • reports/EVIDENCE_SURVEILLANCE_DEPLOYMENT_REPORT.* trong medical-ebm-automation vừa được ghi
    bản online THẬT — giữ lại làm bằng chứng, đừng commit lẫn với thay đổi khác.
Cần bác sĩ kiểm chứng.
EOF
echo ""
read -r -p "Bấm Enter để đóng cửa sổ..." _
