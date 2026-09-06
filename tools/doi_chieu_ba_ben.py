#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Đối chiếu skill giữa BA BÊN: cloud (tài khoản) · repo (nguồn git) · cục bộ (máy).

VÌ SAO CÓ
=========
Hệ EBM có ba nơi giữ skill, và trước công cụ này chỉ có hai cặp được kiểm:

    repo  --link-skills.sh-->  ~/.claude/skills, ~/.codex/skills      (đã có)
    repo  --dong_bo_skill.py-> Claude Desktop local-agent-mode        (đã có)
    repo  <--- ??? --->        bundle tài khoản (cloud)               (KHÔNG AI KIỂM)

Bundle cloud là thứ mà **Routine và mọi phiên claude.ai/code nạp**. Nó đi qua
đồng bộ tài khoản, không qua git. Nên repo và cloud trôi khỏi nhau âm thầm.

BA LOẠI LỆCH — phân biệt được mới xử lý đúng
============================================
  GIỐNG      hai bên trùng khít từng byte.
  LỆCH BẢN   cùng một skill, khác phiên bản. Xử lý: chọn bản mới hơn.
  KHÁC HẲN   TRÙNG TÊN nhưng là HAI SKILL KHÁC NHAU.
             Đây là loại nguy hiểm: "đồng bộ" theo nghĩa chép đè sẽ XÓA MẤT
             một trong hai họ skill. Bắt buộc người xem quyết định, không tự chép.

Công cụ này CHỈ ĐỌC — không ghi, không chép, không sửa gì ở bất kỳ bên nào.

MÃ THOÁT
  0  ba bên khớp (hoặc chỉ lệch ở skill được bỏ qua)
  1  có LỆCH BẢN hoặc thiếu/thừa skill
  2  có KHÁC HẲN — nguy hiểm, đừng chạy lệnh chép đè nào
  3  không đo được (thiếu một bên) — KHÔNG kết luận là "khớp"
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

# Bẫy cp1252: stdout/stderr trên Windows không mặc định UTF-8, và mọi thông điệp
# ở đây là tiếng Việt có dấu. Không reconfigure thì `print()` chết UnicodeEncodeError
# ngay khi gặp ký tự ngoài-ASCII đầu tiên — đúng họ lỗi mà tools/kiem_tuong_thich_da_nen.py
# của repo này dò riêng cho việc này (luật R4).
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

# Dưới ngưỡng này coi là HAI SKILL KHÁC NHAU chứ không phải hai phiên bản.
# 0.35 chọn theo đo thực tế trên bộ EBM: các cặp lệch-phiên-bản thật đều > 0.55;
# các cặp trùng tên khác skill (Việt vs K-Dense tiếng Anh) đều < 0.15.
NGUONG_KHAC_HAN = 0.35

# Dấu do tools/vietnamize (_vietnamize.py) chèn khi Việt hóa skill tiếng Anh.
DAU_VIET_HOA = "<!-- EBM-VN-GUARD -->"


class KhongDoDuoc(Exception):
    """Thiếu dữ liệu để kết luận. Ném ra thay vì trả kết quả rỗng."""


# ----------------------------------------------------------------- đọc skill
def _doc(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def tach_frontmatter(text: str) -> tuple[dict, str]:
    """Trả (frontmatter dạng dict thô, phần thân). Không có frontmatter -> ({}, text)."""
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not m:
        return {}, text
    fm = {}
    for khoa in ("name", "description", "version"):
        mm = re.search(rf"^{khoa}:\s*(.+?)\s*$", m.group(1), re.M)
        if mm:
            fm[khoa] = mm.group(1).strip()
    return fm, text[m.end():]


def ty_le_tieng_viet(than: str) -> float:
    """Tỷ lệ chữ cái có dấu tiếng Việt. Dùng làm BẰNG CHỨNG PHỤ, không phải căn cứ."""
    if not than:
        return 0.0
    co_dau = sum(
        1 for c in than
        if c.isalpha() and "WITH" in unicodedata.name(c, "")
    )
    return co_dau / len(than)


def _tap_dong(than: str) -> set[str]:
    return {d.strip() for d in than.splitlines() if d.strip()}


def _tap_tu(than: str) -> set[str]:
    return set(re.findall(r"\w+", than.lower()))


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def do_giong_nhau_tu(than_a: str, than_b: str) -> float:
    """Jaccard trên tập TỪ — chỉ số CHÍNH để phân loại.

    Dùng từ chứ không dùng dòng vì đo thực tế bắt được một bẫy: bản cloud của
    `antifacts` đã bị DÀN PHẲNG (bỏ đề mục, gộp gạch đầu dòng thành câu dài).
    Nội dung gần như y nguyên nhưng KHÔNG một dòng nào trùng, nên chỉ số theo
    dòng rơi về 0,0% và công cụ kết luận nhầm là "hai skill khác nhau".
    Đo lại theo từ: 67,1% — cùng một skill.

    Trên bộ EBM thật, hai nhóm tách sạch: khác skill 6,2-18,8% · cùng skill
    53,6-98,6%. Ngưỡng 0,35 nằm giữa khoảng trống đó.
    """
    return _jaccard(_tap_tu(than_a), _tap_tu(than_b))


def do_giong_nhau_dong(than_a: str, than_b: str) -> float:
    """Jaccard trên tập DÒNG — chỉ số PHỤ.

    Không dùng để phân loại. Dùng để phát hiện việc dàn phẳng: từ giống nhiều
    mà dòng giống rất ít nghĩa là cùng nội dung nhưng khác cấu trúc trình bày.
    """
    return _jaccard(_tap_dong(than_a), _tap_dong(than_b))


class Skill:
    def __init__(self, ten: str, duong_dan: Path):
        self.ten = ten
        self.duong_dan = duong_dan
        raw = _doc(duong_dan)
        self.fm, self.than = tach_frontmatter(raw)
        self.sha = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        self.so_byte = len(raw.encode("utf-8"))
        self.vn = ty_le_tieng_viet(self.than)
        self.viet_hoa_may = DAU_VIET_HOA in raw

    @property
    def mo_ta(self) -> str:
        return self.fm.get("description", "")


# ------------------------------------------------------------- quét từng bên
def quet_thu_muc(goc: Path) -> dict[str, Skill]:
    """Mọi thư mục con chứa SKILL.md. Bỏ thư mục bắt đầu bằng '_' (nội bộ)."""
    if not goc.is_dir():
        raise KhongDoDuoc(f"không có thư mục: {goc}")
    ket = {}
    for sk in sorted(goc.glob("*/SKILL.md")):
        ten = sk.parent.name
        if ten.startswith("_") or ten.startswith("."):
            continue
        ket[ten] = Skill(ten, sk)
    return ket


def tim_bundle_cloud(chi_dinh: str | None) -> Path:
    """Bundle tài khoản: ~/.claude/skills/synced/<uuid>_<uuid>/."""
    if chi_dinh:
        p = Path(chi_dinh).expanduser()
        if not p.is_dir():
            raise KhongDoDuoc(f"đường dẫn cloud không tồn tại: {p}")
        return p
    goc = Path.home() / ".claude" / "skills" / "synced"
    if not goc.is_dir():
        raise KhongDoDuoc(
            f"không thấy {goc} — máy này chưa đồng bộ skill tài khoản, "
            "hoặc đang chạy ở nơi không có bundle cloud"
        )
    ung_vien = [d for d in sorted(goc.iterdir()) if d.is_dir()]
    if not ung_vien:
        raise KhongDoDuoc(f"{goc} rỗng — không có bundle nào")
    if len(ung_vien) > 1:
        ten = ", ".join(d.name for d in ung_vien)
        raise KhongDoDuoc(
            f"có {len(ung_vien)} bundle trong {goc} ({ten}); "
            "chỉ rõ bằng --cloud để khỏi đoán nhầm"
        )
    return ung_vien[0]


def doc_manifest(bundle: Path) -> dict[str, dict]:
    """manifest.json của bundle cloud: cho biết skill nào là 'custom' của bác sĩ."""
    f = bundle / "manifest.json"
    if not f.exists():
        return {}
    try:
        data = json.loads(_doc(f))
    except json.JSONDecodeError as e:
        raise KhongDoDuoc(f"manifest.json hỏng: {e}") from e
    return {s["name"]: s for s in data.get("skills", []) if "name" in s}


# ---------------------------------------------------------------- phân loại
def phan_loai(a: Skill, b: Skill) -> tuple[str, float, float, bool]:
    """Trả (loại, giống-theo-từ, giống-theo-dòng, có-bị-dàn-phẳng)."""
    if a.sha == b.sha:
        return "GIỐNG", 1.0, 1.0, False
    tu = do_giong_nhau_tu(a.than, b.than)
    dong = do_giong_nhau_dong(a.than, b.than)
    if tu < NGUONG_KHAC_HAN:
        return "KHÁC HẲN", tu, dong, False
    # Cùng nội dung nhưng gần như không dòng nào trùng = một bên đã bị dàn phẳng.
    # Chỉ kết luận vậy khi có CẤU TRÚC để mất: file một-hai dòng thì hai dòng khác
    # nhau đã đủ kéo chỉ số dòng về 0, gắn nhãn ở đó chỉ là nhiễu.
    co_cau_truc = max(len(_tap_dong(a.than)), len(_tap_dong(b.than))) >= 5
    return "LỆCH BẢN", tu, dong, (dong < NGUONG_KHAC_HAN and co_cau_truc)


def _bang(tieu_de: str, dong: list[str]) -> None:
    print(f"\n{tieu_de}")
    print("─" * max(len(tieu_de), 60))
    if not dong:
        print("  (không có)")
    for d in dong:
        print(d)


def doi_chieu(cloud: dict[str, Skill], repo: dict[str, Skill],
              manifest: dict[str, dict], chi_custom: bool) -> dict:
    """So cloud với repo. Trả về kết quả có cấu trúc để in và để xuất JSON."""
    ten_cloud = set(cloud)
    if chi_custom and manifest:
        # Skill do Anthropic phát hành không thuộc trách nhiệm đồng bộ của bác sĩ.
        ten_cloud = {
            t for t in ten_cloud
            if manifest.get(t, {}).get("source", "custom") == "custom"
        }
    chung = sorted(ten_cloud & set(repo))
    kq = {
        "giong": [], "lech_ban": [], "khac_han": [],
        "chi_cloud": sorted(ten_cloud - set(repo)),
        "chi_repo": sorted(set(repo) - set(cloud)),
    }
    for t in chung:
        loai, tt, dong, dan_phang = phan_loai(cloud[t], repo[t])
        muc = {
            "ten": t, "tuong_tu": round(tt, 3),
            "tuong_tu_dong": round(dong, 3), "dan_phang": dan_phang,
            "byte_cloud": cloud[t].so_byte, "byte_repo": repo[t].so_byte,
            "vn_cloud": round(cloud[t].vn * 100, 1),
            "vn_repo": round(repo[t].vn * 100, 1),
            "repo_viet_hoa_may": repo[t].viet_hoa_may,
            "mo_ta_khop": cloud[t].mo_ta == repo[t].mo_ta,
        }
        {"GIỐNG": kq["giong"], "LỆCH BẢN": kq["lech_ban"],
         "KHÁC HẲN": kq["khac_han"]}[loai].append(muc)
    return kq


def in_ket_qua(kq: dict, ten_cloud: str, ten_repo: str) -> None:
    print("\n" + "=" * 78)
    print("  ĐỐI CHIẾU SKILL: CLOUD (tài khoản)  ↔  REPO (nguồn git)")
    print("=" * 78)
    print(f"  cloud : {ten_cloud}")
    print(f"  repo  : {ten_repo}")
    print(f"\n  giống hệt {len(kq['giong'])} · lệch bản {len(kq['lech_ban'])} · "
          f"KHÁC HẲN {len(kq['khac_han'])} · chỉ cloud {len(kq['chi_cloud'])} · "
          f"chỉ repo {len(kq['chi_repo'])}")

    if kq["khac_han"]:
        dong = []
        for m in kq["khac_han"]:
            dong.append(
                f"  🔴 {m['ten']:<34} trùng {m['tuong_tu']*100:>5.1f}%  "
                f"cloud {m['byte_cloud']:>6}B (VN {m['vn_cloud']:>4.1f}%)  "
                f"repo {m['byte_repo']:>6}B (VN {m['vn_repo']:>4.1f}%)"
                + ("  [repo do máy Việt hóa]" if m["repo_viet_hoa_may"] else "")
            )
        _bang("🔴 KHÁC HẲN — TRÙNG TÊN nhưng là HAI SKILL KHÁC NHAU", dong)
        print("\n  ⚠ TUYỆT ĐỐI KHÔNG chạy lệnh chép đè cho nhóm này. Chép một chiều")
        print("    sẽ xóa mất họ skill bên kia. Phải đổi tên hoặc chọn bản giữ lại.")

    if kq["lech_ban"]:
        dong = [
            f"  🟡 {m['ten']:<34} trùng {m['tuong_tu']*100:>5.1f}%  "
            f"cloud {m['byte_cloud']:>6}B  repo {m['byte_repo']:>6}B"
            f"{'' if m['mo_ta_khop'] else '  [mô tả khác]'}"
            f"{'  [cloud bị dàn phẳng]' if m['dan_phang'] else ''}"
            for m in kq["lech_ban"]
        ]
        _bang("🟡 LỆCH BẢN — cùng skill, khác phiên bản", dong)

    if kq["chi_repo"]:
        _bang(f"⚪ CHỈ CÓ TRONG REPO ({len(kq['chi_repo'])}) — cloud không nạp được",
              [f"  {t}" for t in kq["chi_repo"]])
    if kq["chi_cloud"]:
        _bang(f"⚪ CHỈ CÓ TRÊN CLOUD ({len(kq['chi_cloud'])}) — không có bản git",
              [f"  {t}" for t in kq["chi_cloud"]])
    if kq["giong"]:
        _bang(f"✅ GIỐNG HỆT ({len(kq['giong'])})",
              [f"  {m['ten']}" for m in kq["giong"]])


def in_cuc_bo(cuc_bo: dict[str, Path], repo_goc: Path) -> None:
    """Bên thứ ba: máy của bác sĩ. Chỉ có ý nghĩa khi chạy trên chính máy đó."""
    print("\n" + "=" * 78)
    print("  BÊN THỨ BA: CỤC BỘ (máy đang chạy)")
    print("=" * 78)
    for nhan, p in cuc_bo.items():
        if not p.is_dir():
            print(f"  {nhan:<22} — không có ({p})")
            continue
        muc = [d for d in sorted(p.iterdir())
               if d.is_dir() and not d.name.startswith((".", "_"))]
        lk = [d for d in muc if d.is_symlink()]
        tro_dung = [
            d for d in lk
            if repo_goc in d.resolve().parents or d.resolve() == repo_goc
        ]
        print(f"  {nhan:<22} {len(muc):>3} skill · {len(lk)} symlink · "
              f"{len(tro_dung)} trỏ vào repo")
        if lk and len(tro_dung) < len(lk):
            for d in lk:
                if d not in tro_dung:
                    print(f"      ⚠ {d.name} → {d.resolve()}  (KHÔNG trỏ vào repo)")


# Dấu hiệu tác vụ bị neo vào MỘT máy cụ thể: đường dẫn tuyệt đối tới thư mục nhà
# của một người dùng, hoặc thư mục đồng bộ đám mây của máy đó. Tác vụ mang các dấu
# này KHÔNG THỂ chạy ở phiên cloud — container không có những đường dẫn ấy.
NEO_MAY = re.compile(r"/Users/[A-Za-z0-9._-]+|/home/[A-Za-z0-9._-]+/|CloudStorage|OneDrive")


def kiem_tac_vu(goc_repo: Path, cloud: dict[str, Skill]) -> list[dict]:
    """Soát sync/scheduled-tasks/: tác vụ nào neo vào máy, tác vụ nào có trên cloud.

    Đây KHÔNG phải so ba bên. Tác vụ định kỳ thao tác trên file cục bộ nên neo máy
    là ĐÚNG THIẾT KẾ, không phải lỗi. Việc cần biết là: tác vụ neo máy thì phiên
    cloud không gánh thay được, nên nếu lịch trên máy không chạy thì việc đó KHÔNG
    AI LÀM — và chỗ đó im lặng, không ai báo.
    """
    thu_muc = goc_repo / "sync" / "scheduled-tasks"
    if not thu_muc.is_dir():
        return []
    ket = []
    for f in sorted(thu_muc.glob("*/SKILL.md")):
        raw = _doc(f)
        fm, _ = tach_frontmatter(raw)
        neo = sorted(set(NEO_MAY.findall(raw)))
        ket.append({
            "ten": f.parent.name,
            "mo_ta": fm.get("description", ""),
            "neo_may": bool(neo),
            "dau_neo": neo[:3],
            "co_tren_cloud": f.parent.name in cloud,
        })
    return ket


def in_tac_vu(ds: list[dict]) -> None:
    if not ds:
        return
    print("\n" + "=" * 78)
    print("  TÁC VỤ ĐỊNH KỲ (sync/scheduled-tasks)")
    print("=" * 78)
    neo = [t for t in ds if t["neo_may"]]
    print(f"  {len(ds)} tác vụ · {len(neo)} neo vào một máy cụ thể · "
          f"{sum(t['co_tren_cloud'] for t in ds)} có mặt trên cloud\n")
    for t in ds:
        dau = "🖥" if t["neo_may"] else "☁"
        print(f"  {dau} {t['ten']:<30} {t['mo_ta'][:44]}")
    if neo:
        print(f"\n  🖥 = neo vào máy ({', '.join(sorted({d for t in neo for d in t['dau_neo']}))[:60]}...)")
        print("     Phiên cloud KHÔNG gánh thay được. Nếu lịch trên máy không chạy thì")
        print("     việc này KHÔNG AI LÀM — và nó im lặng, không có gì báo.")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Đối chiếu skill ba bên: cloud · repo · cục bộ. CHỈ ĐỌC.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("repo", nargs="?", default=None,
                    help="thư mục hub skill của repo (vd .../sync/skills), hoặc gốc repo "
                         "— công cụ tự tìm sync/skills. Bỏ trống thì lấy repo chứa chính "
                         "công cụ này (để chạy được như một làn trong dong_bo_tat_ca.py)")
    ap.add_argument("--cloud", help="bundle tài khoản; bỏ trống thì tự dò "
                                    "~/.claude/skills/synced/<uuid>")
    ap.add_argument("--tat-ca", action="store_true",
                    help="so cả skill do Anthropic phát hành (mặc định chỉ so 'custom')")
    ap.add_argument("--json", action="store_true", help="xuất JSON thay vì bảng")
    a = ap.parse_args(argv)

    try:
        # Bỏ trống -> repo chứa chính file này (tools/<file> -> gốc repo là parents[1]).
        goc_repo = (Path(a.repo).expanduser().resolve() if a.repo
                    else Path(__file__).resolve().parents[1])
        hub = goc_repo / "sync" / "skills" if (goc_repo / "sync" / "skills").is_dir() else goc_repo
        repo = quet_thu_muc(hub)
        bundle = tim_bundle_cloud(a.cloud)
        cloud = quet_thu_muc(bundle)
        manifest = doc_manifest(bundle)
    except KhongDoDuoc as e:
        print(f"KHÔNG ĐO ĐƯỢC: {e}", file=sys.stderr)
        print("Đây KHÔNG phải kết luận 'ba bên đã khớp'.", file=sys.stderr)
        return 3

    kq = doi_chieu(cloud, repo, manifest, chi_custom=not a.tat_ca)

    if a.json:
        print(json.dumps({"cloud": str(bundle), "repo": str(hub), **kq,
                          "tac_vu_dinh_ky": kiem_tac_vu(goc_repo, cloud)},
                         ensure_ascii=False, indent=2))
    else:
        in_ket_qua(kq, str(bundle), str(hub))
        in_tac_vu(kiem_tac_vu(goc_repo, cloud))
        in_cuc_bo({"~/.claude/skills": Path.home() / ".claude" / "skills",
                   "~/.codex/skills": Path.home() / ".codex" / "skills"}, hub)

    if kq["khac_han"]:
        return 2
    if kq["lech_ban"] or kq["chi_cloud"] or kq["chi_repo"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
