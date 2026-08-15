#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CHU TRÌNH CHỨNG CỨ — một lệnh trả lời: chứng cứ của tôi có MỚI và ĐÁNG TIN không?

VÌ SAO CÓ (12/08/2026)
======================
Hệ đã có đủ mảnh rời — chốt độ tươi, cổng liêm chính, sổ xác minh, tra rút bài,
giám sát tuần/tháng — nhưng KHÔNG có chỗ nào ghép chúng lại. Hệ quả đo được:

  • hai job launchd (tuần/tháng) `runs = 0` — **chưa từng tự chạy lần nào**;
  • máy Windows không có lịch nền nào tương đương;
  • bác sĩ phải tự nhớ gọi từng lệnh, đúng thứ tự, với đúng trình thông dịch;
  • và tệ nhất: máy có thể đang chạy **dữ liệu giả** mà không bước nào nói ra.

Lệnh này chạy các chốt theo đúng thứ tự phụ thuộc và **dừng ngay khi nền tảng
không đáng tin** — thay vì chạy tiếp rồi sinh ra một báo cáo trông sạch sẽ.

THỨ TỰ CÓ CHỦ Ý (không đảo)
    1. NGUỒN THẬT?   — máy có lấy được dữ liệu thật không (chặn cứng nếu không)
    2. ĐỘ TƯƠI       — chứng cứ có cũ quá không
    3. XÁC MINH      — từng PMID/DOI/URL có thật không, tích luỹ qua nhiều vòng
    4. RÚT BÀI       — có trích dẫn nào đã bị rút không
    5. CỔNG LIÊM CHÍNH — gói có còn đạt chuẩn phát hành không

Bước 1 chặn cứng vì mọi bước sau đều VÔ NGHĨA nếu nguồn là giả: xác minh dữ liệu
giả sẽ "thành công" và cho ra một con số độ phủ đẹp nhưng rỗng.

GIỚI HẠN CÓ CHỦ Ý
  • KHÔNG tự quét chứng cứ mới và KHÔNG tự nạp sổ cái: sinh nội dung y khoa phải
    do bác sĩ chủ động và duyệt (Cổng B). Lệnh này chỉ ĐO và BÁO.
  • KHÔNG tự áp dụng gì cho người bệnh (Cổng A).
  • Không thay `verify_dashboard.py --online` ở lượt phát hành thật.

Dùng:
    python tools/chu_trinh_chung_cu.py             # đo toàn bộ kho
    python tools/chu_trinh_chung_cu.py --nhanh     # bỏ bước xác minh mạng (chỉ đọc sổ)
    python tools/chu_trinh_chung_cu.py --vong 3    # mạng chập chờn thì tăng vòng

Mã thoát: 0 = mọi chốt đạt · 1 = có việc cần bác sĩ làm · 2 = nền tảng không đáng tin.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

# Windows: stdout mặc định là cp1252 → mọi print() tiếng Việt hoặc ký hiệu (✓ ⚠ →)
# ném UnicodeEncodeError và GIẾT tiến trình, thường SAU KHI công việc đã xong. Đo thật
# ngày 12/08/2026 trên dây chuyền cập nhật chứng cứ: bản Word 82 KB đã ghi ra đĩa nhưng
# tool thoát mã 1 ở đúng dòng print cuối ⇒ caller đọc mã thoát, tưởng hỏng, bỏ luôn 2
# bước sau. Cùng lớp lỗi đã vá cho tools/vietnamize/.
import sys as _sys_utf8
for _s in (_sys_utf8.stdout, _sys_utf8.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass


REPO = Path(__file__).resolve().parents[1]
PY = sys.executable


def chay(cmd: list[str], tieu_de: str) -> tuple[int, str]:
    print("\n" + "─" * 68)
    print(f"  {tieu_de}")
    print("─" * 68)
    proc = subprocess.run([str(c) for c in cmd], cwd=str(REPO),
                          capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    out = (proc.stdout or "") + (proc.stderr or "")
    print(out.rstrip() or "  (không có đầu ra)")
    return proc.returncode, out


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser(description="Chu trình đo độ mới + độ tin cậy của kho chứng cứ")
    ap.add_argument("--vong", type=int, default=2, help="số vòng xác minh (mạng kém thì tăng)")
    ap.add_argument("--nhanh", action="store_true", help="không gọi mạng, chỉ đọc sổ đã có")
    a = ap.parse_args()

    print("=" * 68)
    print("  CHU TRÌNH CHỨNG CỨ — độ mới và độ tin cậy")
    print("=" * 68)

    viec_can_lam: list[str] = []

    # ── 1. NỀN TẢNG: nguồn có THẬT không ────────────────────────────────────
    rc, _ = chay([PY, "tools/kiem_nguon_that.py"], "① Nguồn có thật không?")
    if rc == 2:
        print("\n" + "=" * 68)
        print("  ⛔ DỪNG — nền tảng không đáng tin.")
        print("=" * 68)
        print("  Mọi bước sau đều vô nghĩa khi nguồn là dữ liệu giả: xác minh dữ liệu")
        print("  giả vẫn 'thành công' và cho ra độ phủ đẹp nhưng rỗng ruột.")
        print("  Sửa theo hướng dẫn ở trên rồi chạy lại lệnh này.")
        print("\n  Cần bác sĩ kiểm chứng.")
        return 2
    if rc == 1:
        viec_can_lam.append("Mạng tới nguồn chập chờn — kết quả xác minh có thể chưa đủ.")

    # ── 2. ĐỘ TƯƠI ──────────────────────────────────────────────────────────
    rc, out = chay([PY, "tools/kiem_do_tuoi_chung_cu.py"], "② Chứng cứ có còn mới không?")
    if rc != 0:
        viec_can_lam.append("Có mục giám sát quá hạn — xem phần ② ở trên.")

    # ── 3 + 4. XÁC MINH TỪNG NGUỒN và RÚT BÀI ───────────────────────────────
    if a.nhanh:
        rc, out = chay([PY, "tools/so_xac_minh_nguon.py", "--bao-cao"],
                       "③④ Độ phủ xác minh (đọc sổ, không gọi mạng)")
    else:
        rc, out = chay([PY, "tools/so_xac_minh_nguon.py", "--vong", str(a.vong)],
                       f"③④ Xác minh nguồn + tra rút bài ({a.vong} vòng)")
    if rc == 2:
        # rc=2 từ 15/08 CHỈ còn nghĩa «rút BỎ HẲN đang được dashboard trích» —
        # rút-và-thay đã phân xử trong gói không kéo còi đỏ nữa (nó ở rc=1, phần
        # 🟠 của báo cáo); thẩm quyền chặn từng gói thuộc verify_dashboard.
        viec_can_lam.append("🔴 CÓ NGUỒN RÚT BỎ HẲN đang được trích — xử lý trước khi dùng gói chứa chúng.")
    elif rc == 1:
        # VÁ 13/08/2026 — đọc MÃ lý do thay vì đưa một lời khuyên chung.
        # Bản cũ luôn nói "chạy lại thêm vòng". Đo thật: 562/1146 mục hết hiệu lực và
        # CẢ 562 là PMID chưa kiểm được rút bài vì NCBI chặn máy — chạy lại bao nhiêu
        # vòng cũng không đổi. Lời khuyên chắc chắn vô ích tiêu thời gian thật của bác
        # sĩ và làm mất niềm tin vào những cảnh báo ĐÚNG khác của cùng công cụ.
        # BỔ SUNG 14/08/2026 — kiểm rút bài nay có chuỗi 3 tầng, nên khi chưa tải nền
        # ngoại tuyến thì cách sửa ĐÚNG là tải nó (miễn phí, không khoá), KHÔNG phải
        # ngồi chờ NCBI_API_KEY. Đặt TRƯỚC nhánh CAN_NCBI_API_KEY vì đây mới là việc
        # có tác dụng ngay.
        if "CAN_TAI_RETRACTION_WATCH" in out:
            viec_can_lam.append(
                "PMID CHƯA kiểm được RÚT BÀI vì chưa có nền ngoại tuyến — chạy "
                "`python medical-ebm-automation/tools/tai_retraction_watch.py` (một lần, "
                "không cần khoá API) rồi chạy lại.")
        if "CAN_NCBI_API_KEY" in out:
            viec_can_lam.append(
                "PMID CHƯA kiểm được RÚT BÀI dù đã qua cả 3 tầng (Retraction Watch ngoại "
                "tuyến → NCBI → Europe PMC). Thêm `NCBI_API_KEY` vào "
                "~/.ebm-secrets/medical-ebm-automation.env sẽ mở lại tầng NCBI.")
        if "CAN_CHAY_THEM_VONG" in out:
            viec_can_lam.append("Có nguồn quá hạn xác minh tồn tại — chạy lại thêm vòng SẼ sửa được.")
        if "CAN_XEM_TAY" in out:
            viec_can_lam.append("Có nguồn hết hiệu lực vì lý do khác — xem phần ③④ ở trên.")
        if not any(x in out for x in ("CAN_NCBI_API_KEY", "CAN_TAI_RETRACTION_WATCH",
                                      "CAN_CHAY_THEM_VONG", "CAN_XEM_TAY")):
            viec_can_lam.append("Còn nguồn chưa xác minh hoặc hết hạn — xem phần ③④ ở trên.")

    # ── 5. NHẤT QUÁN GIỮA CÁC BẢN CÙNG CHỦ ĐỀ ───────────────────────────────
    # Đặt SAU phần xác minh vì nó đọc nội dung dashboard, không gọi mạng; và đặt
    # TRƯỚC cổng dây chuyền vì mâu thuẫn nội dung nghiêm trọng hơn lỗi cấu trúc.
    rc, out = chay([PY, "tools/dang_ky_chu_de.py", "--mau-thuan"],
                   "⑤ Có hai bản nào nói ngược nhau không?")
    if rc == 1:
        viec_can_lam.append("🔴 Có mục hai bản CÙNG CHỦ ĐỀ nói ngược nhau — bác sĩ cần "
                            "quyết bản nào đúng (xem phần ⑤).")

    # ── 6. CỔNG LIÊM CHÍNH trên toàn kho (offline, nhanh) ────────────────────
    rc, out = chay([PY, "tools/verify_clinical_evidence_update_pipeline.py"],
                   "⑥ Dây chuyền cập nhật chứng cứ còn nguyên vẹn?")
    if rc != 0:
        viec_can_lam.append("Dây chuyền cập nhật chứng cứ có lỗi — xem phần ⑥.")

    # ── Tổng kết ────────────────────────────────────────────────────────────
    print("\n" + "=" * 68)
    print("  TỔNG KẾT")
    print("=" * 68)
    if not viec_can_lam:
        print("  🟢 Mọi chốt đạt: nguồn thật · còn hạn · đã xác minh · không thấy bài bị rút.")
        print("\n  Lưu ý phạm vi: đây là kết luận về TÍNH TOÀN VẸN KỸ THUẬT của kho —")
        print("  nguồn có thật, chưa bị rút, gói đúng cấu trúc. Nó KHÔNG nói rằng nội")
        print("  dung lâm sàng đã đúng hay đã cập nhật hết mọi guideline mới; việc đó")
        print("  cần bác sĩ đọc và cần một lượt quét chứng cứ chủ động.")
        print("\n  Cần bác sĩ kiểm chứng.")
        return 0

    print(f"  🟡 Còn {len(viec_can_lam)} việc cần bác sĩ:")
    for i, v in enumerate(viec_can_lam, 1):
        print(f"     {i}. {v}")
    print("\n  Chu trình này chỉ ĐO và BÁO — không tự quét chứng cứ mới, không tự nạp")
    print("  sổ cái, không tự áp dụng cho người bệnh (Cổng A/B).")
    print("\n  Cần bác sĩ kiểm chứng.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
