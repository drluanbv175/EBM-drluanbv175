#!/usr/bin/env python3
"""Đồng bộ BỘ BA bản sao surveillance_scan.py — tự vá lớp lệch ESD02.

Vì sao tồn tại (01/09/2026): chốt ESD02 của
`medical-ebm-automation/tools/verify_evidence_surveillance_deployment.py`
đòi BA bản sau đồng nhất hash, và hook pre-commit fail-closed toàn cục sẽ
CHẶN MỌI commit khi chúng lệch:

  1. sync/skills/cap-nhat-chung-cu-y-khoa/tools/surveillance_scan.py  (NGUỒN CHUẨN)
  2. sync/skills/dark-analyst/tools/surveillance_scan.py              (bản biến thể)
  3. EBM-Dashboards/tools/surveillance_scan.py                        (bản runtime, NGOÀI git)

Trước công cụ này, bộ ba được giữ khớp BẰNG TAY — nghĩa là với dây chuyền
hằng ngày cơ chế đó không tồn tại (bài học BH41), và ca thật 01/09: bác sĩ
bị chặn commit khoá công Ed25519 chỉ vì bản (3) trên OneDrive đã lệch từ
một đợt cập nhật skill trước đó. Chốt PHÁT HIỆN (ESD02) đã có; đây là mảnh
TỰ VÁ còn thiếu, nối vào tu_sua_chua.py để mỗi phiên tự chạy.

Luật chiều đồng bộ — chép NGUYÊN luật nội dung 21/08 (BH71 kề bên), KHÔNG
tin mtime:
  (a) bản đích KHÔNG có dòng riêng so với nguồn → nguồn bao trùm → chép đè;
  (b) bản đích CÓ dòng riêng → GIỮ LẠI + in các dòng đó cho bác sĩ quyết —
      chép đè lúc này có thể xoá mất một bản vá mới hơn chưa hồi nguồn.
Bản đích không tồn tại = thiếu nguyên liệu, KHÔNG phải nguy hiểm (BH08) —
bỏ qua có ghi chú, không đỏ. Nguồn chuẩn không đọc được mới là lỗi (mã 2).

Mã thoát: 0 = khớp hết / đã vá xong · 1 = còn lệch (dry-run) hoặc còn bản
bị giữ lại chờ người quyết · 2 = lỗi vận hành. Cần bác sĩ kiểm chứng.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]

NGUON_CHUAN = Path("sync/skills/cap-nhat-chung-cu-y-khoa/tools/surveillance_scan.py")
BAN_DICH = [
    Path("sync/skills/dark-analyst/tools/surveillance_scan.py"),
    Path("EBM-Dashboards/tools/surveillance_scan.py"),
]


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _dong_thuc(p: Path) -> set:
    """Tập dòng KHÔNG rỗng của file — đơn vị so 'dòng riêng' của luật (a)/(b)."""
    return {l for l in p.read_text(encoding="utf-8").splitlines() if l.strip()}


def main() -> int:
    ap = argparse.ArgumentParser(description="Đồng bộ bộ ba surveillance_scan.py (ESD02)")
    ap.add_argument("--ap-dung", action="store_true",
                    help="Chép đè thật các bản đích mà nguồn bao trùm (mặc định: chỉ báo)")
    ap.add_argument("--im-khi-on", action="store_true",
                    help="Im lặng khi mọi bản đã khớp (dùng cho tu_sua_chua/hook)")
    ap.add_argument("--goc", default=None,
                    help="Ghi đè thư mục gốc (chỉ dùng cho kiểm thử)")
    args = ap.parse_args()

    goc = Path(args.goc).resolve() if args.goc else REPO
    nguon = goc / NGUON_CHUAN
    if not nguon.exists():
        print(f"⛔ Không thấy nguồn chuẩn: {nguon} — không có căn cứ đồng bộ.")
        return 2
    try:
        hash_nguon = _sha(nguon)
        dong_nguon = _dong_thuc(nguon)
    except OSError as e:
        print(f"⛔ Không đọc được nguồn chuẩn: {e}")
        return 2

    lech_con_lai = 0
    da_va = 0
    thong_diep: list = []
    for rel in BAN_DICH:
        dich = goc / rel
        if not dich.exists():
            # Máy không có nhánh này (vd container không có EBM-Dashboards) —
            # thiếu nguyên liệu không phải bằng chứng nguy hiểm (BH08).
            thong_diep.append(f"⚪ {rel}: không tồn tại trên máy này — bỏ qua.")
            continue
        try:
            if _sha(dich) == hash_nguon:
                thong_diep.append(f"✅ {rel}: khớp nguồn chuẩn.")
                continue
            rieng = sorted(_dong_thuc(dich) - dong_nguon)
        except OSError as e:
            print(f"⛔ Không đọc được {rel}: {e}")
            return 2
        if rieng:
            lech_con_lai += 1
            thong_diep.append(
                f"⛔ {rel}: LỆCH và có {len(rieng)} dòng RIÊNG — giữ lại chờ bác sĩ"
                " (chép đè có thể xoá bản vá chưa hồi nguồn):")
            for l in rieng[:8]:
                thong_diep.append("     RIÊNG: " + l[:100])
        elif args.ap_dung:
            shutil.copyfile(nguon, dich)
            da_va += 1
            thong_diep.append(f"🔧 {rel}: nguồn bao trùm — ĐÃ chép đè khớp nguồn chuẩn.")
        else:
            lech_con_lai += 1
            thong_diep.append(
                f"🟡 {rel}: lệch nhưng nguồn bao trùm — chạy --ap-dung để vá.")

    on_het = lech_con_lai == 0
    if args.im_khi_on and on_het and da_va == 0:
        return 0
    print("ĐỒNG BỘ SCANNER GIÁM SÁT (bộ ba ESD02) — nguồn chuẩn:", NGUON_CHUAN)
    for t in thong_diep:
        print("  " + t)
    if da_va:
        print(f"  Đã vá {da_va} bản. Kiểm lại: verify_evidence_surveillance_deployment.py --contract-check")
    print("Cần bác sĩ kiểm chứng.")
    return 0 if on_het else 1


if __name__ == "__main__":
    raise SystemExit(main())
