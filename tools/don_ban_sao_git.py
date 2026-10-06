#!/usr/bin/env python3
"""Dọn bản sao xung đột OneDrive NẰM TRONG `.git` của hai repo EBM — có sao lưu, cứu ref trước, KHÔNG xoá gì.

Vì sao (06/10/2026): hai máy (Mac «Dr Luân BV175», Windows «C010000PK16BSL») cùng ghi `.git` qua OneDrive đẻ ra bản sao
mang hậu tố máy — `FETCH_HEAD-<máy>`, `index-<máy>`, reflog, `packed-refs-<máy>`, ref ma dưới `refs/`. Chốt
`tools/sync_safety_check.py` (mục 5) báo 🔴 và luật §0.7 chặn kéo cây chính, nhưng chưa có lối xử lý an toàn — dọn tay thì
dễ mất ref thật hoặc làm OneDrive xoá lây bản gốc (sự cố 24/09). Công cụ này làm đúng trình tự chốt khuyên:

  1. Quét như mục 5 (quét chưa hết ⇒ DỪNG, mã 2 — không hành động trên dữ kiện dở).
  2. Mỗi ref mà bản sao giữ (ref ma rời, từng dòng của bản sao packed-refs) mà KHÔNG ref thật nào giữ ⇒ CỨU trước:
     commit ⇒ nhánh `refs/heads/rescue/<ngày>/<tên gốc>`; đối tượng khác (Codex trỏ ref vào tree) ⇒
     `refs/rescue/<ngày>/<tên gốc>`. Đối tượng không còn trong kho ⇒ ghi nhận (không có gì để cứu).
  3. Bản sao `config`/`HEAD` KHÁC bản đang dùng ⇒ BỎ QUA, để người xem (mã 1). Giống hệt ⇒ dời.
  4. DỜI mọi bản sao còn lại ra NGOÀI OneDrive (`--sao-luu`, mặc định `~/ebm-backup-truoc-dong-bo-<ngày>/ban-sao-git-<giờ>`),
     so SHA-256 trước/sau, ghi `manifest.json` (đường dẫn gốc + băm) để trả về bằng tay nếu cần.
  5. KIỂM SAU: tập ref thật không đổi (cộng ref vừa cứu), HEAD không đổi, bản gốc tương ứng (bỏ hậu tố) có trước thì vẫn
     còn, quét lại chỉ còn mục bỏ qua.

Mặc định CHẠY THỬ (in kế hoạch, không đổi gì); `--ap-dung` mới cứu + dời. Không bao giờ xoá; không đụng tệp đang dùng.
Sau khi dời: đợi OneDrive xanh rồi chạy lại `python3 tools/sync_safety_check.py` — máy kia cũng chạy công cụ này.

Mã thoát: 0 sạch/đã dọn · 1 còn mục cần người xem (đã bỏ qua) · 2 không đo được hoặc kiểm sau thất bại.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sync_safety_check as S  # noqa: E402

_SHA_RE = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?")


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for khoi in iter(lambda: f.read(1 << 20), b""):
            h.update(khoi)
    return h.hexdigest()


def _ref_that(repo: Path) -> Optional[Dict[str, str]]:
    """{ref: sha} của mọi ref THẬT (bỏ ref ma do bản sao đẻ ra); None nếu git lỗi."""
    ok, out, _ = S._run_git(["for-each-ref", "--format=%(refname) %(objectname)"], repo, timeout=60)
    if not ok:
        return None
    tb = S._cac_thiet_bi_git()
    ra = {}
    for dong in out.splitlines():
        ref, _, sha = dong.partition(" ")
        if ref and not S._la_ref_ma(ref, tb):
            ra[ref] = sha
    return ra


def _head(repo: Path) -> Optional[str]:
    ok, out, _ = S._run_git(["rev-parse", "--verify", "--quiet", "HEAD"], repo, timeout=20)
    return out if ok else None


def _ref_trong_ban_sao(git_dir: Path, rel: str, tb: str) -> List[Tuple[str, str]]:
    """(tên ref gốc, sha) mà bản sao giữ: ref ma rời ⇒ một cặp (tên đã gỡ hậu tố); bản sao packed-refs ⇒ từng dòng.

    Bỏ nhánh MÁY CHỦ (`refs/remotes/…`) — cùng chính sách mục 5 của chốt an toàn: máy chủ là nguồn sự thật, nhánh PR đã
    xoá thì commit hoặc đã gộp vào nhánh chính hoặc bị bỏ có chủ ý; cứu chúng chỉ đẻ hàng loạt nhánh rescue/ rác. Ref
    tượng trưng («ref: …») không giữ đối tượng nào."""
    try:
        noi_dung = (git_dir / rel).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    if rel.startswith("refs/remotes/"):
        return []
    if rel.startswith("refs/"):
        dau = noi_dung.strip()
        sha = dau.split()[0] if dau else ""
        if dau.startswith("ref:") or not _SHA_RE.fullmatch(sha):
            return []
        return [(S._bo_hau_to(rel, tb) if tb else rel, sha)]
    if rel.startswith("packed-refs"):
        ra = []
        for dong in noi_dung.splitlines():
            p = dong.split()
            if (len(p) == 2 and not dong.startswith(("#", "^")) and p[1].startswith("refs/")
                    and not p[1].startswith("refs/remotes/") and _SHA_RE.fullmatch(p[0])):
                ra.append((p[1], p[0]))
        return ra
    return []


def _khac_ban_dang_dung(repo: Path, git_dir: Path, rel: str) -> Optional[str]:
    """Lý do bỏ qua nếu bản sao `config`/`HEAD` KHÁC bản đang dùng (có thể giữ thiết lập/nhánh máy kia có); None nếu giống
    hệt hoặc không phải hai loại đó."""
    ten = rel.rsplit("/", 1)[-1]
    o_goc = "/" not in rel
    if not o_goc:
        return None
    if ten.lower().startswith("config"):
        ok1, ban_sao, _ = S._run_git(["config", "-f", str(git_dir / rel), "--list"], repo, timeout=20)
        ok2, dang_dung, _ = S._run_git(["config", "-f", str(git_dir / "config"), "--list"], repo, timeout=20)
        if not (ok1 and ok2):
            return "không đọc được để so — người xem"
        thua = sorted(set(ban_sao.splitlines()) - set(dang_dung.splitlines()))
        return f"bản sao config có {len(thua)} dòng bản đang dùng KHÔNG có (vd «{thua[0]}») — người xem" if thua else None
    if ten.startswith("HEAD"):
        try:
            a = (git_dir / rel).read_text(encoding="utf-8", errors="replace").strip()
            b = (git_dir / "HEAD").read_text(encoding="utf-8", errors="replace").strip()
        except OSError:
            return "không đọc được để so — người xem"
        return None if a == b else f"bản sao HEAD trỏ «{a}» ≠ đang dùng «{b}» — người xem"
    return None


def _ten_cuu(repo: Path, ten_ref: str, kieu: str, ngay: str, sha: str) -> str:
    """Tên ref cứu hợp lệ, không đè ref khác: commit ⇒ nhánh rescue/<ngày>/…; đối tượng khác ⇒ refs/rescue/<ngày>/…"""
    duoi = ten_ref[len("refs/"):] if ten_ref.startswith("refs/") else ten_ref
    goc = f"refs/heads/rescue/{ngay}/{duoi}" if kieu == "commit" else f"refs/rescue/{ngay}/{duoi}"
    ten, i = goc, 1
    while True:
        ok, cu, _ = S._run_git(["rev-parse", "--verify", "--quiet", ten], repo, timeout=20)
        if not ok or cu == sha:
            return ten
        i += 1
        ten = f"{goc}-{i}"


def don_repo(nhan: str, repo: Path, sao_luu: Path, *, ap_dung: bool, ngay: str) -> Dict[str, Any]:
    """Kế hoạch (và nếu `ap_dung` thì làm) cho MỘT repo. Trả báo cáo; khoá «loi» có mặt ⇒ không đo được/kiểm sau hỏng."""
    git_dir = repo / ".git"
    bc: Dict[str, Any] = {"repo": nhan, "duong_dan": str(repo), "muc": [], "da_cuu": [], "da_doi": [], "bo_qua": []}
    if not git_dir.is_dir():
        bc["ghi_chu"] = "không có thư mục .git (không phải repo, hoặc worktree phụ) — bỏ qua"
        return bc
    tb_list = S._cac_thiet_bi_git()
    ban_sao, du = S._quet_ban_sao_git(git_dir, tb_list, 60.0)
    if not du:
        bc["loi"] = "quét .git chưa hết trong 60 giây (OneDrive đang tải?) — không làm gì"
        return bc
    truoc, head_truoc = _ref_that(repo), _head(repo)
    if truoc is None:
        bc["loi"] = "git for-each-ref lỗi — không làm gì"
        return bc

    for rel, tb in sorted(ban_sao):
        muc, ly_do = S._xet_mot_ban_sao_git(repo, git_dir, rel, tb)
        can_cuu, mat_doi_tuong = [], []
        for ten_ref, sha in _ref_trong_ban_sao(git_dir, rel, tb):
            ok, kieu, _ = S._run_git(["cat-file", "-t", sha], repo, timeout=20)
            if not ok:
                mat_doi_tuong.append(ten_ref)
            elif S._ref_that_giu(repo, sha) is None:
                can_cuu.append({"ref": ten_ref, "sha": sha, "kieu": kieu})
        bc["muc"].append({"rel": rel, "thiet_bi": tb, "muc": muc, "ly_do": ly_do, "can_cuu": can_cuu,
                          "doi_tuong_khong_con": mat_doi_tuong, "bo_qua": _khac_ban_dang_dung(repo, git_dir, rel)})
    if not ap_dung:
        return bc

    # (2) cứu trước — tạo ref là thao tác CỘNG THÊM, không đổi ref nào đang có.
    for m in bc["muc"]:
        for c in m["can_cuu"]:
            ten = _ten_cuu(repo, c["ref"], c["kieu"], ngay, c["sha"])
            ok, _, loi = S._run_git(["update-ref", ten, c["sha"]], repo, timeout=20)
            if not ok:
                bc["loi"] = f"không tạo được ref cứu {ten}: {loi} — DỪNG trước khi dời"
                return bc
            bc["da_cuu"].append({"ref_cuu": ten, "tu": c["ref"], "sha": c["sha"], "kieu": c["kieu"]})

    # (4) dời ra ngoài OneDrive — chỉ khi mọi ref bản sao giữ đã có ref thật giữ (sau bước cứu).
    dich_goc = sao_luu / ("goc" if nhan == "." else nhan) / ".git"
    for m in bc["muc"]:
        rel, tb = m["rel"], m["thiet_bi"]
        if m["bo_qua"]:
            bc["bo_qua"].append({"rel": rel, "ly_do": m["bo_qua"]})
            continue
        con_mat = [r for r, sha in _ref_trong_ban_sao(git_dir, rel, tb)
                   if S._run_git(["cat-file", "-t", sha], repo, timeout=20)[0] and S._ref_that_giu(repo, sha) is None]
        if con_mat:
            bc["bo_qua"].append({"rel": rel, "ly_do": f"vẫn còn ref chỉ bản sao giữ sau khi cứu: {con_mat[:3]}"})
            continue
        nguon, dich = git_dir / rel, dich_goc / rel
        ban_goc = git_dir / S._bo_hau_to(rel, tb) if tb else None
        co_ban_goc = bool(ban_goc and ban_goc.exists())
        bam = _sha256(nguon)
        dich.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(nguon), str(dich))
        if not dich.is_file() or _sha256(dich) != bam:
            bc["loi"] = f"bản dời của {rel} không khớp SHA-256 — DỪNG (bản sao lưu: {dich})"
            return bc
        bc["da_doi"].append({"rel": rel, "sha256": bam, "toi": str(dich),
                             "ban_goc": str(ban_goc.relative_to(git_dir)) if ban_goc else None, "co_ban_goc": co_ban_goc})

    # (5) kiểm sau.
    sau, head_sau = _ref_that(repo), _head(repo)
    ky_vong = dict(truoc, **{c["ref_cuu"]: c["sha"] for c in bc["da_cuu"]})
    hong = []
    if sau != ky_vong:
        hong.append("tập ref thật đổi ngoài dự kiến")
    if head_sau != head_truoc:
        hong.append(f"HEAD đổi {head_truoc} → {head_sau}")
    for d in bc["da_doi"]:
        if d["co_ban_goc"] and not (git_dir / d["ban_goc"]).exists():
            hong.append(f"bản gốc {d['ban_goc']} biến mất sau khi dời bản sao")
    con_lai, du2 = S._quet_ban_sao_git(git_dir, tb_list, 60.0)
    if du2 and len(con_lai) != len(bc["bo_qua"]):
        hong.append(f"quét lại còn {len(con_lai)} bản sao, dự kiến {len(bc['bo_qua'])} (mục bỏ qua)")
    if hong:
        bc["loi"] = "KIỂM SAU THẤT BẠI: " + "; ".join(hong) + f" — trả bản sao từ {dich_goc} theo manifest.json"
    return bc


def don(repos: Optional[List[Tuple[str, Path]]] = None, *, sao_luu: Optional[Path] = None, ap_dung: bool = False,
        ngay: Optional[str] = None) -> Tuple[int, Dict[str, Any]]:
    """(mã thoát, báo cáo) cho mọi repo — mặc định hai repo của chốt an toàn."""
    bay_gio = datetime.now()
    ngay = ngay or bay_gio.strftime("%Y%m%d")
    sao_luu = sao_luu or (Path.home() / f"ebm-backup-truoc-dong-bo-{ngay}" / f"ban-sao-git-{bay_gio:%H%M%S}")
    ket = {"ap_dung": ap_dung, "sao_luu": str(sao_luu), "repo": []}
    for nhan, repo in (repos if repos is not None else S.GIT_REPOS):
        ket["repo"].append(don_repo(nhan, Path(repo), Path(sao_luu), ap_dung=ap_dung, ngay=ngay))
    if ap_dung and any(r["da_doi"] or r["da_cuu"] for r in ket["repo"]):
        Path(sao_luu).mkdir(parents=True, exist_ok=True)
        (Path(sao_luu) / "manifest.json").write_text(json.dumps(ket, ensure_ascii=False, indent=2), encoding="utf-8",
                                                     newline="\n")
    if any("loi" in r for r in ket["repo"]):
        return 2, ket
    can_nguoi = any(r["bo_qua"] for r in ket["repo"]) or (not ap_dung and any(
        m["bo_qua"] for r in ket["repo"] for m in r["muc"]))
    return (1 if can_nguoi else 0), ket


def _in(ket: Dict[str, Any]) -> None:
    print("=" * 64)
    print(f" DỌN BẢN SAO XUNG ĐỘT TRONG .git — {'ÁP DỤNG' if ket['ap_dung'] else 'CHẠY THỬ (không đổi gì)'}")
    print("=" * 64)
    for r in ket["repo"]:
        print(f"\n[{r['repo']}] {r.get('ghi_chu') or ''}")
        if "loi" in r:
            print(f"  ⛔ {r['loi']}")
        dem = {}
        for m in r["muc"]:
            dem[m["muc"]] = dem.get(m["muc"], 0) + 1
            if m["can_cuu"] or m["bo_qua"] or m["doi_tuong_khong_con"] or m["muc"] != "GREEN":
                print(f"  • {m['rel']} — {m['muc']}" + (f": {m['ly_do']}" if m["ly_do"] else ""))
                for c in m["can_cuu"]:
                    print(f"      ↳ CẦN CỨU {c['ref']} ({c['kieu']} {c['sha'][:7]}) — không ref thật nào giữ")
                if m["doi_tuong_khong_con"]:
                    print(f"      ↳ {len(m['doi_tuong_khong_con'])} ref trỏ đối tượng đã không còn trong kho (không cứu được)")
                if m["bo_qua"]:
                    print(f"      ↳ BỎ QUA: {m['bo_qua']}")
        print(f"  Tổng: {len(r['muc'])} bản sao ({', '.join(f'{k} {v}' for k, v in sorted(dem.items())) or '—'})")
        for c in r["da_cuu"]:
            print(f"  ✅ đã cứu {c['tu']} → {c['ref_cuu']} ({c['sha'][:7]})")
        if r["da_doi"]:
            print(f"  ✅ đã dời {len(r['da_doi'])} bản sao ra ngoài OneDrive")
    print(f"\n Sao lưu: {ket['sao_luu']}" + (" (manifest.json)" if ket["ap_dung"] else " (chưa tạo — chạy thử)"))
    if not ket["ap_dung"]:
        print(" → Áp dụng: python3 tools/don_ban_sao_git.py --ap-dung   (không xoá gì; bản sao dời ra ngoài OneDrive)")
    else:
        print(" → Đợi OneDrive XANH rồi chạy lại: python3 tools/sync_safety_check.py ; máy kia cũng chạy công cụ này.")
    print(" Cần bác sĩ kiểm chứng.")


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Dọn bản sao xung đột OneDrive trong .git (chạy thử mặc định).")
    ap.add_argument("--ap-dung", action="store_true", help="cứu ref thật sự mất rồi dời bản sao ra ngoài OneDrive")
    ap.add_argument("--sao-luu", type=Path, default=None,
                    help="thư mục nhận bản sao (mặc định ~/ebm-backup-truoc-dong-bo-<ngày>/ban-sao-git-<giờ>)")
    ap.add_argument("--json", action="store_true", help="in báo cáo JSON")
    args = ap.parse_args(argv)
    ma, ket = don(sao_luu=args.sao_luu, ap_dung=args.ap_dung)
    if args.json:
        print(json.dumps(ket, ensure_ascii=False, indent=2))
    else:
        _in(ket)
    return ma


if __name__ == "__main__":
    sys.exit(main())
