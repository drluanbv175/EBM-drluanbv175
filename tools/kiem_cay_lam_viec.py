#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KIỂM CÂY LÀM VIỆC — cây mã đang đứng có ĐỦ TƯ CÁCH để kết luận không?

VÌ SAO CÓ (02/09/2026, BH93). Một cuộc kiểm toán 11 agent trên chính repo này đã
báo động NGHIÊM TRỌNG rằng cổng G8 «không có bất kỳ chốt chất lượng nào», kèm bằng
chứng `git log --all -S` cho thấy bản vá 24/08 «chưa từng tồn tại trong bất kỳ ref
nào». Kết luận đó SAI HOÀN TOÀN. Sự thật đo được ngay sau đó:

    medical-ebm-automation:  HEAD 17/08/2026 · shallow=true · KHÔNG có ref master

`git log --all` trên một clone NÔNG chỉ thấy các ref đã fetch. Ở đây `master` chưa
từng được fetch, nên «--all» không hề bao gồm nhánh mang bản vá. Sau `git fetch
origin master`, toàn bộ 5 khẳng định đáng sợ nhất đều bị bác bỏ: G8Q có nối dây
(`approve_gate.py:76,567`), test hồi quy có thật, canary có thật, G2/G4 chấm TRƯỚC
`add_approval` chứ không phải sau.

Đây đúng là họ lỗi BH74 «đo đúng, nhưng đo nhầm chỗ» — lần này nạn nhân là chính bộ
kiểm toán. Hại của nó bất đối xứng và rất xấu: cây lạc hậu sinh ra **âm tính giả** —
tuyên bố một cơ chế an toàn KHÔNG tồn tại trong khi nó đang chạy. Một khoảng hở đã
được vá bị báo là còn hở thì người ta sẽ đi vá lại thứ đã lành; tệ hơn, một cơ chế
đang lành bị nghi ngờ thì niềm tin vào cả hệ giảm theo.

CÔNG CỤ NÀY CHỈ ĐO VÀ BÁO. Nó KHÔNG tự `git fetch`, KHÔNG tự đổi nhánh, KHÔNG tự
`unshallow` — chạm vào cây mã của bác sĩ là quyết định của bác sĩ, và một lần fetch
tự động trong hook có thể kéo về hàng trăm MB trên mạng bệnh viện.

LUẬT BH08 ÁP TRIỆT ĐỂ Ở ĐÂY: thiếu ref để so KHÔNG phải là «có vấn đề», nó là
«CHƯA KIỂM ĐƯỢC». Chỉ báo đỏ khi CHỨNG MINH được cây đang lạc hậu (có ref, đếm ra
số commit thiếu) hoặc chứng minh được cây nông (git tự khai). Biến chưa-biết thành
có-vấn-đề chính là lỗi mà công cụ này sinh ra để chống.

Mã thoát: 0 = cây đủ tư cách (hoặc chưa kiểm được) · 1 = cây KHÔNG đủ tư cách kết luận.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]

# Kết luận nào KHÔNG được phép rút ra trên cây nông — in kèm cảnh báo để người đọc
# biết chính xác loại suy luận nào vừa mất hiệu lực, thay vì chỉ biết "cây nông".
SUY_LUAN_CAM_TREN_CAY_NONG = (
    "«chưa từng tồn tại», «không có trong lịch sử», «git log --all không thấy» — "
    "MỌI kết luận dạng phủ-định-toàn-lịch-sử đều VÔ HIỆU trên cây nông"
)


def _git(cay: Path, *args: str) -> tuple[int, str]:
    """Chạy git trong `cay`, trả (mã thoát, stdout đã strip). Không bao giờ ném."""
    try:
        r = subprocess.run(["git", *args], cwd=cay, capture_output=True,
                           text=True, timeout=30)
        return r.returncode, (r.stdout or "").strip()
    except (OSError, subprocess.SubprocessError):
        return 99, ""


def nhanh_mac_dinh(cay: Path) -> str | None:
    """Tên ref mặc định của origin, CHỈ đọc ref cục bộ — không gọi mạng.

    Trả None khi không xác định được (⇒ CHƯA KIỂM ĐƯỢC, không phải lỗi).
    """
    ma, ra = _git(cay, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD")
    if ma == 0 and ra:
        return ra.replace("refs/remotes/", "", 1)
    for ten in ("origin/master", "origin/main"):
        if _git(cay, "rev-parse", "--verify", "--quiet", ten)[0] == 0:
            return ten
    return None


def soi_mot_cay(cay: Path) -> dict:
    """Soi MỘT cây git. Trả dict mô tả tư cách kết luận của cây đó."""
    kq: dict = {"cay": str(cay), "la_git": False, "nong": False,
                "thieu_bao_nhieu": None, "nhanh": None, "goc_so": None,
                "canh_bao": [], "do": False}

    if _git(cay, "rev-parse", "--git-dir")[0] != 0:
        return kq
    kq["la_git"] = True
    kq["nhanh"] = _git(cay, "rev-parse", "--abbrev-ref", "HEAD")[1] or "(không rõ)"

    # (1) Cây nông — chứng minh được cục bộ, không cần mạng.
    if _git(cay, "rev-parse", "--is-shallow-repository")[1] == "true":
        kq["nong"] = True
        # CỐ Ý là VÀNG, không phải ĐỎ: mọi phiên cloud đều là clone nông, đó là trạng
        # thái BÌNH THƯỜNG VĨNH VIỄN ở đây. Báo đỏ mỗi phiên là dựng bức tường đỏ mà
        # không ai xử lý được — đúng thứ BH08/BH32 cấm, và nó sẽ dạy người ta bỏ qua
        # cả cảnh báo THẬT ở dòng «lạc hậu» ngay dưới. Cây nông không phải việc phải
        # SỬA; nó là giới hạn phải BIẾT khi rút kết luận phủ định.
        kq["canh_bao"].append(f"CÂY NÔNG (shallow) — {SUY_LUAN_CAM_TREN_CAY_NONG}")

    # (2) Lạc hậu so với ref mặc định — chỉ kết luận khi CÓ ref để so.
    goc = nhanh_mac_dinh(cay)
    kq["goc_so"] = goc
    if goc is None:
        kq["canh_bao"].append(
            "CHƯA KIỂM ĐƯỢC độ lạc hậu: không có ref origin/master|main cục bộ. "
            "KHÔNG phải bằng chứng cây lành — chạy `git fetch origin <nhánh-chính>` rồi kiểm lại"
        )
        return kq

    ma, ra = _git(cay, "rev-list", "--count", f"HEAD..{goc}")
    if ma != 0 or not ra.isdigit():
        kq["canh_bao"].append(f"CHƯA KIỂM ĐƯỢC độ lạc hậu so với {goc} (git không đếm được)")
        return kq

    thieu = int(ra)
    kq["thieu_bao_nhieu"] = thieu
    if thieu > 0:
        kq["do"] = True
        kq["canh_bao"].append(
            f"LẠC HẬU {thieu} commit so với {goc} — kết luận «mã X không tồn tại» rút ra ở "
            f"đây có thể là ÂM TÍNH GIẢ; đối chiếu lại bằng `git show {goc}:<đường-dẫn>`"
        )
    return kq


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Cây mã đang đứng có đủ tư cách để kết luận «X không tồn tại» không?")
    ap.add_argument("--im-khi-on", action="store_true", help="chỉ nói khi cây không đủ tư cách")
    a = ap.parse_args()

    cac_cay = [REPO]
    phu = REPO / "medical-ebm-automation"
    # resolve() để không soi nhầm chính REPO khi symlink trỏ lòng vòng
    if phu.exists() and phu.resolve() != REPO.resolve():
        cac_cay.append(phu.resolve())

    ket = [soi_mot_cay(c) for c in cac_cay]
    co_do = any(k["do"] for k in ket)          # ĐỎ = lạc hậu ⇒ CÓ việc để làm
    co_nong = any(k["nong"] for k in ket)      # VÀNG = nông ⇒ chỉ giới hạn cần biết
    co_loi_nhac = any(k["canh_bao"] for k in ket)

    if a.im_khi_on and not co_do:
        return 0
    if not co_loi_nhac and not co_do:
        print("🟢 CÂY LÀM VIỆC đủ tư cách kết luận (không nông, không lạc hậu).")
        return 0

    print("KIỂM CÂY LÀM VIỆC — tư cách rút kết luận từ cây mã đang đứng")
    for k in ket:
        if not k["la_git"]:
            continue
        ten = Path(k["cay"]).name
        if k["do"]:
            print(f"\n🔴 {ten}  (nhánh: {k['nhanh']})")
        elif k["canh_bao"]:
            print(f"\n🟡 {ten}  (nhánh: {k['nhanh']})")
        else:
            print(f"\n✓ {ten}  (nhánh: {k['nhanh']}) — đủ tư cách")
        for c in k["canh_bao"]:
            print(f"   • {c}")

    if co_do:
        print("\n   Ý NGHĨA: trên cây này, phủ định KHÔNG phải bằng chứng. Không được kết luận")
        print("   một cơ chế/bản vá «chưa từng có» nếu chỉ dựa vào cây đang đứng.")
        print("   Cần bác sĩ kiểm chứng.")
    return 1 if co_do else 0


if __name__ == "__main__":
    raise SystemExit(main())
