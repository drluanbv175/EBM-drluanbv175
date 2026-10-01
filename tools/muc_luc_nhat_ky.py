#!/usr/bin/env python3
"""Mục lục + luật đặt tên cho nhật ký sự cố dạng MỖI SỰ CỐ MỘT TỆP (01/10/2026).

Vì sao có tệp này: từ 24/09 mọi PR nối mục sự cố vào CUỐI cùng một tệp
`audit/NHAT-KY-SU-CO.md`, nên hai PR mở song song gần như chắc xung đột ở đó (đo
01/10: 3/3 lần gộp origin/master có xung đột từ 24/09 đều chỉ ở tệp này). Bác sĩ chọn
phương án «mỗi sự cố một tệp» trong `audit/nhat-ky/`: hai PR khác tên tệp thì không
bao giờ xung đột, kể cả trên GitHub. Tệp cũ giữ nguyên văn và ĐÓNG BĂNG.

Mục lục KHÔNG được commit — một tệp mục lục chung mà PR nào cũng sửa sẽ thành điểm
nóng xung đột mới. Công cụ này in mục lục khi cần, đọc thẳng từ thư mục.

Luật đặt tên (`loi_thu_muc_nhat_ky`) là nguồn DUY NHẤT; chốt
`verify_claude_code_repo_alignment.check_nhat_ky_su_co()` gọi lại hàm này.

Dùng:
    python3 tools/muc_luc_nhat_ky.py              # mục lục các tệp mới
    python3 tools/muc_luc_nhat_ky.py "từ khoá"    # lọc tệp mới + tiêu đề mục ở tệp cũ
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THU_MUC_NHAT_KY = ROOT / "audit" / "nhat-ky"
NHAT_KY_CU = ROOT / "audit" / "NHAT-KY-SU-CO.md"

# Tệp được phép trong thư mục mà không phải một mục sự cố.
TEP_QUY_UOC = "README.md"
# YYYY-MM-DD-<slug>.md; slug chữ thường không dấu, số, nối bằng một gạch.
TEN_TEP_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")


def _ngay_tu_ten(ten: str) -> date | None:
    """Trả ngày trong tên tệp nếu tên đúng mẫu VÀ ngày có thật (loại 2026-02-30)."""
    khop = TEN_TEP_RE.match(ten)
    if not khop:
        return None
    try:
        return date(int(khop.group(1)), int(khop.group(2)), int(khop.group(3)))
    except ValueError:
        return None


def _dong_dau(duong: Path) -> str:
    """Dòng đầu tiên KHÔNG trống của tệp (đã bỏ BOM và khoảng trắng cuối)."""
    for dong in duong.read_text(encoding="utf-8-sig").splitlines():
        if dong.strip():
            return dong.rstrip()
    return ""


def loi_thu_muc_nhat_ky(thu_muc: Path = THU_MUC_NHAT_KY) -> list[str]:
    """Liệt kê lỗi quy ước của thư mục nhật ký; danh sách rỗng = đạt.

    Mỗi tệp (trừ README.md và tệp ẩn như .DS_Store) phải:
    - tên `YYYY-MM-DD-<slug>.md` với ngày có thật — bản sao xung đột OneDrive
      kiểu «… 2.md» cũng rơi vào đây, đúng ý;
    - dòng đầu `# DD/MM/YYYY — <tiêu đề>` với ngày TRÙNG ngày trong tên tệp, để
      `grep -rn "01/10/2026"` tìm ra mục mới giống hệt cách tra mục cũ.
    Thư mục chưa có thì không có lỗi (chưa ai ghi mục nào).
    """
    if not thu_muc.is_dir():
        return []
    loi: list[str] = []
    for duong in sorted(thu_muc.iterdir()):
        ten = duong.name
        if ten.startswith(".") or ten == TEP_QUY_UOC:
            continue
        if duong.is_dir():
            loi.append(f"{ten}/: thư mục con không được phép — mỗi sự cố là MỘT TỆP .md")
            continue
        ngay = _ngay_tu_ten(ten)
        if ngay is None:
            loi.append(f"{ten}: tên phải là YYYY-MM-DD-<slug>.md (ngày có thật; slug chữ "
                       "thường không dấu, số, gạch nối)")
            continue
        tieu_de = f"# {ngay:%d/%m/%Y} — "
        dau = _dong_dau(duong)
        if not dau.startswith(tieu_de) or len(dau) <= len(tieu_de):
            loi.append(f"{ten}: dòng đầu phải là «{tieu_de}<tiêu đề>» (ngày trùng tên tệp), "
                       f"đang là «{dau[:80]}»")
    return loi


def muc_luc(thu_muc: Path = THU_MUC_NHAT_KY) -> list[tuple[str, str]]:
    """(tên tệp, tiêu đề) của mọi mục đúng tên, mới nhất trước."""
    if not thu_muc.is_dir():
        return []
    ra = []
    for duong in thu_muc.iterdir():
        if duong.is_file() and _ngay_tu_ten(duong.name):
            ra.append((duong.name, _dong_dau(duong).lstrip("# ").strip()))
    return sorted(ra, reverse=True)


def _co_tu_khoa(van_ban: str, tu_khoa: str) -> bool:
    return tu_khoa.casefold() in van_ban.casefold()


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    args = sys.argv[1:] if argv is None else argv
    tu_khoa = " ".join(args).strip()

    muc = muc_luc()
    if tu_khoa:
        muc = [(ten, td) for ten, td in muc
               if _co_tu_khoa((THU_MUC_NHAT_KY / ten).read_text(encoding="utf-8-sig"), tu_khoa)]
    print(f"Nhật ký sự cố từ 01/10/2026 — audit/nhat-ky/ ({len(muc)} mục"
          + (f" chứa «{tu_khoa}»" if tu_khoa else "") + "):")
    for ten, td in muc:
        print(f"  audit/nhat-ky/{ten}  —  {td}")

    if tu_khoa and NHAT_KY_CU.exists():
        cu = [(i, d) for i, d in enumerate(NHAT_KY_CU.read_text(encoding="utf-8").splitlines(), 1)
              if d.startswith("#") and _co_tu_khoa(d, tu_khoa)]
        print(f"\nTiêu đề mục ở tệp cũ (đóng băng) audit/NHAT-KY-SU-CO.md chứa «{tu_khoa}»: {len(cu)}")
        for i, d in cu:
            print(f"  :{i}  {d[:150]}")
        print('  (chữ trong THÂN mục cũ: grep -n "<từ khoá>" audit/NHAT-KY-SU-CO.md)')

    loi = loi_thu_muc_nhat_ky()
    if loi:
        print("\n⚠ Tệp sai quy ước (audit/nhat-ky/README.md):")
        for dong in loi:
            print(f"  - {dong}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
