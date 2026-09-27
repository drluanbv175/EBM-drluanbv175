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

SO VỚI MỘT TẬP REF, KHÔNG PHẢI MỘT REF (26/09/2026). Bản đầu so với ĐÚNG MỘT ref mặc
định (origin/HEAD, lùi về origin/master|main). Trên bản clone Cloud `origin/HEAD` không phải
symbolic ref ở CẢ HAI repo, nên repo y khoa lùi về `origin/main` — nhánh BỎ từ 28/06 — và nếu
được soi sẽ báo «LẠC HẬU 30 commit» mỗi phiên (đỏ giả, dạy người ta bỏ qua cảnh báo thật).
Nay mỗi cây được so với một TẬP ref và ĐỎ nếu thua BẤT KỲ ref nào:
  (a) nhánh CHÍNH khai báo (`NHANH_CHINH`, khoá theo tên repo suy từ remote origin);
  (b) upstream `@{u}` khi nó khác (a);
  (c) origin/HEAD → origin/master|main CHỈ khi repo KHÔNG có khai báo.
KHÔNG làm kiểu «xét @{u} trước rồi dừng»: nhánh làm việc push `-u` tự theo dõi CHÍNH NÓ nên
luôn 0 commit lạc hậu dù nhánh chính đã tiến xa — đúng kịch bản BH93 gốc, thành xanh giả.
Ref khai báo vắng cục bộ, hoặc không có lịch sử chung (clone nông) ⇒ «CHƯA KIỂM ĐƯỢC» — không
đỏ, không xanh, và TUYỆT ĐỐI không lùi về origin/main.
Repo y khoa được tìm ở vị trí LỒNG hoặc ANH EM (`ban_sao_tran.duong_goc`) — bản đầu chỉ nhận
vị trí lồng nên trên Cloud (hai repo cạnh nhau) chốt §0.3 im lặng hoàn toàn với repo y khoa.

Mã thoát: 0 = cây đủ tư cách (hoặc chưa kiểm được) · 1 = cây KHÔNG đủ tư cách kết luận.
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]

# Nhánh CHÍNH khai báo của từng repo — khoá = TÊN REPO trên GitHub (suy từ remote origin,
# lùi về tên thư mục; trên Mac/Windows thư mục gốc là «Claude AI» nên không khoá theo thư mục).
# Nguồn: CLAUDE.md gốc §4 «Nhánh mặc định: `feat/r1-1-2-design-gap-remediation`» cho repo y
# khoa (test canh khớp nguyên văn); repo gốc dùng `master`. Dùng chung với cảm biến CI của
# tools/tu_de_xuat_viec.py (nấc lùi cuối) — MỘT nơi định nghĩa, không nhân bản.
NHANH_CHINH = {
    "EBM-drluanbv175": "master",
    "medical-ebm-automation": "feat/r1-1-2-design-gap-remediation",
}

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
                           text=True, timeout=30, encoding="utf-8", errors="replace")
        return r.returncode, (r.stdout or "").strip()
    except (OSError, subprocess.SubprocessError):
        return 99, ""


def nhanh_mac_dinh(cay: Path) -> str | None:
    """Tên ref mặc định của origin, CHỈ đọc ref cục bộ — không gọi mạng.

    Trả None khi không xác định được (⇒ CHƯA KIỂM ĐƯỢC, không phải lỗi). Chỉ dùng cho repo
    KHÔNG có nhánh chính khai báo (xem `cac_ref_so`).
    """
    ma, ra = _git(cay, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD")
    if ma == 0 and ra:
        return ra.replace("refs/remotes/", "", 1)
    for ten in ("origin/master", "origin/main"):
        if _git(cay, "rev-parse", "--verify", "--quiet", ten)[0] == 0:
            return ten
    return None


def ten_repo(cay: Path) -> str:
    """Tên repo trên GitHub suy từ `git remote get-url origin` (https/ssh/proxy cục bộ/đường
    dẫn tệp); không có remote thì lùi về tên thư mục."""
    ma, url = _git(cay, "remote", "get-url", "origin")
    if ma == 0 and url:
        m = re.search(r"([\w.-]+?)(?:\.git)?/?$", url.strip())
        if m:
            return m.group(1)
    return Path(cay).resolve().name


def cac_ref_so(cay: Path, khai_bao: dict[str, str] | None = None) -> list[tuple[str, str]]:
    """TẬP ref để so độ lạc hậu, mỗi phần tử (ref, nguồn gốc ref).

    (a) nhánh chính khai báo → (b) `@{u}` nếu khác (a) → (c) origin/HEAD|master|main CHỈ khi
    repo không có khai báo. Không bao giờ dừng ở @{u} (nhánh tự theo dõi chính nó ⇒ xanh giả).
    """
    khai_bao = NHANH_CHINH if khai_bao is None else khai_bao
    refs: list[tuple[str, str]] = []
    chinh = khai_bao.get(ten_repo(cay))
    if chinh:
        refs.append((f"origin/{chinh}", "nhánh chính khai báo"))
    ma, u = _git(cay, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    if ma == 0 and u and u not in (r for r, _ in refs):
        refs.append((u, "upstream @{u}"))
    if not chinh:
        goc = nhanh_mac_dinh(cay)
        if goc and goc not in (r for r, _ in refs):
            refs.append((goc, "ref mặc định origin"))
    return refs


def _do_mot_ref(cay: Path, ref: str, nguon: str) -> dict:
    """Đo HEAD thua `ref` bao nhiêu commit. `thieu=None` + `ly_do` khi KHÔNG đo được."""
    kq = {"ref": ref, "nguon": nguon, "thieu": None, "ly_do": ""}
    if _git(cay, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")[0] != 0:
        nhanh = ref.split("/", 1)[1] if ref.startswith("origin/") else ref
        kq["ly_do"] = (f"ref vắng cục bộ — chạy `git fetch origin {nhanh}` rồi kiểm lại; "
                       "KHÔNG lùi về ref khác, KHÔNG phải bằng chứng cây lành")
        return kq
    if _git(cay, "merge-base", "HEAD", ref)[0] != 0:
        # Clone nông / lịch sử rời: `rev-list HEAD..ref` sẽ đếm cả phần lịch sử không chung
        # (con số vô nghĩa, đúng ca «30 commit» của origin/main trên Cloud) ⇒ chưa kiểm được.
        kq["ly_do"] = "không có lịch sử chung với HEAD (clone nông?) — con số lạc hậu vô nghĩa"
        return kq
    ma, ra = _git(cay, "rev-list", "--count", f"HEAD..{ref}")
    if ma != 0 or not ra.isdigit():
        kq["ly_do"] = "git không đếm được"
        return kq
    kq["thieu"] = int(ra)
    return kq


def soi_mot_cay(cay: Path, khai_bao: dict[str, str] | None = None) -> dict:
    """Soi MỘT cây git. Trả dict mô tả tư cách kết luận của cây đó."""
    kq: dict = {"cay": str(cay), "la_git": False, "nong": False,
                "thieu_bao_nhieu": None, "nhanh": None, "goc_so": None,
                "cac_ref_so": [], "canh_bao": [], "do": False}

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

    # (2) Lạc hậu so với TẬP ref — chỉ kết luận khi CÓ ref để so; đỏ nếu thua BẤT KỲ ref nào.
    refs = cac_ref_so(cay, khai_bao)
    if not refs:
        kq["canh_bao"].append(
            "CHƯA KIỂM ĐƯỢC độ lạc hậu: không có nhánh chính khai báo, không có upstream, "
            "không có ref origin/master|main cục bộ. KHÔNG phải bằng chứng cây lành — chạy "
            "`git fetch origin <nhánh-chính>` rồi kiểm lại"
        )
        return kq

    do_duoc = []
    for ref, nguon in refs:
        d = _do_mot_ref(cay, ref, nguon)
        kq["cac_ref_so"].append(d)
        if d["thieu"] is None:
            kq["canh_bao"].append(f"CHƯA KIỂM ĐƯỢC độ lạc hậu so với {ref} ({nguon}): {d['ly_do']}")
            continue
        do_duoc.append(d)
        if d["thieu"] > 0:
            kq["do"] = True
            kq["canh_bao"].append(
                f"LẠC HẬU {d['thieu']} commit so với {ref} ({nguon}) — kết luận «mã X không tồn "
                f"tại» rút ra ở đây có thể là ÂM TÍNH GIẢ; đối chiếu lại bằng `git show {ref}:<đường-dẫn>`"
            )
    kq["goc_so"] = (do_duoc[0] if do_duoc else kq["cac_ref_so"][0])["ref"]
    if do_duoc:
        kq["thieu_bao_nhieu"] = max(d["thieu"] for d in do_duoc)
    return kq


def _nap_ban_sao_tran():
    """Nạp tools/ban_sao_tran.py theo đường dẫn tệp (không phụ thuộc sys.path nơi gọi)."""
    duong = Path(__file__).resolve().parent / "ban_sao_tran.py"
    spec = importlib.util.spec_from_file_location("_kcl_ban_sao_tran", duong)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cac_cay_can_soi(repo: Path | None = None) -> list[Path]:
    """Repo gốc + repo y khoa ở vị trí LỒNG hoặc ANH EM (`ban_sao_tran.duong_goc`)."""
    repo = REPO if repo is None else repo
    cac_cay = [repo]
    phu = _nap_ban_sao_tran().duong_goc("medical-ebm-automation", repo)
    # resolve() để không soi nhầm chính repo khi symlink trỏ lòng vòng
    if phu is not None and phu.resolve() != repo.resolve():
        cac_cay.append(phu.resolve())
    return cac_cay


def _nhan_ref(k: dict) -> str:
    """Nhãn «đã so với …» — in ref đã dùng trên MỖI dòng (biết con số đo so với cái gì)."""
    refs = [d["ref"] for d in k.get("cac_ref_so", [])]
    return f"so với {', '.join(refs)}" if refs else "không có ref để so"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Cây mã đang đứng có đủ tư cách để kết luận «X không tồn tại» không?")
    ap.add_argument("--im-khi-on", action="store_true", help="chỉ nói khi cây không đủ tư cách")
    a = ap.parse_args(argv)

    ket = [soi_mot_cay(c) for c in cac_cay_can_soi(REPO)]
    co_do = any(k["do"] for k in ket)          # ĐỎ = lạc hậu ⇒ CÓ việc để làm
    co_loi_nhac = any(k["canh_bao"] for k in ket)  # VÀNG = nông/chưa kiểm được ⇒ giới hạn cần biết

    if a.im_khi_on and not co_do:
        return 0
    if not co_loi_nhac and not co_do:
        cac = " · ".join(f"{Path(k['cay']).name} [{_nhan_ref(k)}]" for k in ket if k["la_git"])
        print(f"🟢 CÂY LÀM VIỆC đủ tư cách kết luận (không nông, không lạc hậu): {cac}")
        return 0

    print("KIỂM CÂY LÀM VIỆC — tư cách rút kết luận từ cây mã đang đứng")
    for k in ket:
        if not k["la_git"]:
            continue
        ten = Path(k["cay"]).name
        if k["do"]:
            print(f"\n🔴 {ten}  (nhánh: {k['nhanh']}; {_nhan_ref(k)})")
        elif k["canh_bao"]:
            print(f"\n🟡 {ten}  (nhánh: {k['nhanh']}; {_nhan_ref(k)})")
        else:
            print(f"\n✓ {ten}  (nhánh: {k['nhanh']}; {_nhan_ref(k)}) — đủ tư cách")
        for c in k["canh_bao"]:
            print(f"   • {c}")

    if co_do:
        print("\n   Ý NGHĨA: trên cây này, phủ định KHÔNG phải bằng chứng. Không được kết luận")
        print("   một cơ chế/bản vá «chưa từng có» nếu chỉ dựa vào cây đang đứng.")
        print("   Cần bác sĩ kiểm chứng.")
    return 1 if co_do else 0


if __name__ == "__main__":
    raise SystemExit(main())
