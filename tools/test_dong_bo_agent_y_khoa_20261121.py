# -*- coding: utf-8 -*-
"""PR cặp cho agent gốc → bản sao repo y khoa (21/11/2026). Ngoại tuyến, repo git tạm.

Chốt: (1) phân loại đúng bốn nhóm — cần PR cặp · cần kéo cây · chỉ có ở gốc · khớp; (2) thay SHA đúng MỘT hằng, chèn chú thích,
từ chối mẫu lạ/SHA sai; (3) chốt pre-commit `--staged` chỉ nhắc khi agent đang stage khác origin y khoa, im lặng khi trùng; (4)
`--ap-dung` dựng commit trong worktree mới: chép NGUYÊN VĂN bản HEAD gốc, manifest + SHA mới, không đẩy khi thiếu `--mo-pr`; (5) giác
quan hòm việc tách «cần PR cặp» khỏi «origin đã trùng, cây chưa kéo». Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NHANH = "feat/r1-1-2-design-gap-remediation"


def _nap(duong: Path, ten: str):
    sp = importlib.util.spec_from_file_location(ten, duong)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


D = _nap(REPO / "tools" / "dong_bo_agent_y_khoa.py", "_dbay_t")
SHA_CU = "a" * 64
SHA_MOI = "b" * 64
REGISTRY = f'''"""reg"""
MINIMUM = 64
# 20/11/2026: dòng cũ.
MANIFEST_SELF_CHECK_SHA256 = (
    "{SHA_CU}"
)
'''
REGEN = f'''import sys
from pathlib import Path
if "--write" in sys.argv:
    Path("runtime/manifests").mkdir(parents=True, exist_ok=True)
    Path("runtime/manifests/agent_source_manifest.csv").write_text("path,sha\\n", encoding="utf-8")
    print("Self-check SHA-256 của manifest MỚI: {SHA_MOI}")
elif "--check" in sys.argv:
    print("CHECK PASS")
'''


def _g(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout


def _repo(p: Path, tep: dict[str, str]) -> Path:
    p.mkdir(parents=True)
    _g(p, "init", "-q", "-b", "main")
    _g(p, "config", "user.email", "t@t.invalid")
    _g(p, "config", "user.name", "t")
    _g(p, "config", "core.hooksPath", "/dev/null")
    for ten, nd in tep.items():
        (p / ten).parent.mkdir(parents=True, exist_ok=True)
        (p / ten).write_text(nd, encoding="utf-8", newline="\n")
    _g(p, "add", "-A")
    _g(p, "commit", "-q", "-m", "khoi tao")
    return p


def _hai_repo(tmp_path: Path, *, goc: dict[str, str], mea_origin: dict[str, str]):
    goc_r = _repo(tmp_path / "goc", {f".claude/agents/{k}": v for k, v in goc.items()})
    mea = _repo(tmp_path / "mea", {**{f".claude/agents/{k}": v for k, v in mea_origin.items()},
                                   "runtime/agent_registry.py": REGISTRY,
                                   "scripts/regenerate_agent_manifest.py": REGEN})
    _g(mea, "update-ref", f"refs/remotes/origin/{NHANH}", "HEAD")   # «origin đã fetch» giả
    return goc_r, mea


def test_phan_loai_bon_nhom():
    goc = {"a.md": b"1", "b.md": b"2", "c.md": b"3", "moi.md": b"4"}
    org = {"a.md": b"1", "b.md": b"X", "c.md": b"3"}
    cay = {"a.md": b"1", "b.md": b"X", "c.md": b"CU"}
    ds = {x["ten"]: x["loai"] for x in D.phan_loai(list(goc) + ["vang.md"], goc.get, org.get, cay.get)}
    assert ds == {"a.md": "khop", "b.md": "can_pr_cap", "c.md": "can_keo_cay", "moi.md": "chi_goc"}


def test_cap_nhat_sha_mot_hang_va_chu_thich():
    moi = D.cap_nhat_sha(REGISTRY, SHA_MOI, "21/11/2026: đồng bộ x.md")
    assert SHA_MOI in moi and SHA_CU not in moi
    assert "# 21/11/2026: đồng bộ x.md\nMANIFEST_SELF_CHECK_SHA256 = (" in moi
    assert "# 20/11/2026: dòng cũ." in moi, "chú thích cũ giữ nguyên"
    for sai in (lambda: D.cap_nhat_sha(REGISTRY, "xyz", "c"), lambda: D.cap_nhat_sha("không có hằng", SHA_MOI, "c"),
                lambda: D.cap_nhat_sha(REGISTRY + REGISTRY, SHA_MOI, "c")):
        try:
            sai()
        except ValueError:
            continue
        raise AssertionError("phải từ chối SHA sai / mẫu không khớp đúng một lần")


def test_cap_nhat_sha_ngat_chu_thich_dai_duoi_120_ky_tu():
    ten = ["cong-cu-do-luong.md", "kinh-te-y-te.md", "meta-phan-tich.md", "mo-hinh-tien-luong.md",
           "phan-tich-thong-ke.md", "tham-dinh-do-chinh-xac-chan-doan.md", "viet-ban-thao.md"]
    ghi = f"21/11/2026: đồng bộ bản sao {', '.join(ten)} với nguồn gốc (tools/dong_bo_agent_y_khoa.py)."
    moi = D.cap_nhat_sha(REGISTRY, SHA_MOI, ghi)
    dau = moi.index("# 21/11/2026: đồng bộ bản sao")
    khoi = moi[dau:moi.index("MANIFEST_SELF_CHECK_SHA256 = (")].rstrip("\n").split("\n")
    assert len(khoi) >= 2 and all(len(d) <= 120 and d.startswith("# ") for d in khoi)
    assert " ".join(d[2:] for d in khoi) == ghi, "ngắt dòng không được mất/đổi chữ (tên agent có gạch nối giữ nguyên)"


def test_staged_chi_nhac_khi_khac_origin(tmp_path):
    # HEAD gốc «Z» ≠ origin «A»: stage «A» là thay đổi THẬT so với HEAD mà trùng origin ⇒ phải im lặng (không trả về sớm vì rỗng)
    goc, mea = _hai_repo(tmp_path, goc={"ke-don.md": "Z\n", "khac.md": "K\n"}, mea_origin={"ke-don.md": "A\n", "khac.md": "K\n"})
    assert D.canh_bao_staged(goc, mea, NHANH) == [], "không stage gì ⇒ im lặng"
    (goc / ".claude/agents/khac.md").write_text("K\n", encoding="utf-8", newline="\n")
    (goc / ".claude/agents/ke-don.md").write_text("B\n", encoding="utf-8", newline="\n")
    _g(goc, "add", "-A")
    dong = D.canh_bao_staged(goc, mea, NHANH)
    assert dong and "ke-don.md" in dong[0] and "--ap-dung --mo-pr" in dong[1]
    (goc / ".claude/agents/ke-don.md").write_text("A\n", encoding="utf-8", newline="\n")
    _g(goc, "add", "-A")
    assert _g(goc, "diff", "--cached", "--name-only").strip() == ".claude/agents/ke-don.md", "fixture: phải CÓ tệp stage"
    assert D.canh_bao_staged(goc, mea, NHANH) == [], "stage trùng bản origin ⇒ im lặng"
    assert D.canh_bao_staged(goc, None, NHANH) == [], "vắng repo y khoa ⇒ im lặng, không đỏ giả ở pre-commit"


def test_bao_cao_tach_pr_cap_khoi_keo_cay(tmp_path):
    goc, mea = _hai_repo(tmp_path, goc={"a.md": "1\n", "b.md": "MOI\n", "c.md": "3\n", "chi-goc.md": "x\n"},
                         mea_origin={"a.md": "1\n", "b.md": "CU\n", "c.md": "3\n"})
    (mea / ".claude/agents/c.md").write_text("CAY-CU\n", encoding="utf-8", newline="\n")   # cây trên máy lệch origin
    ma, ds, dong = D.bao_cao(goc, mea, NHANH)
    loai = {x["ten"]: x["loai"] for x in ds}
    assert ma == 1 and loai == {"a.md": "khop", "b.md": "can_pr_cap", "c.md": "can_keo_cay", "chi-goc.md": "chi_goc"}
    assert any("cần PR CẶP: b.md" in x for x in dong) and any("chưa kéo: c.md" in x for x in dong)
    ma, _, dong = D.bao_cao(goc, None, NHANH)
    assert ma == 2 and "không đo được" in dong[0]


def test_ap_dung_dung_commit_trong_worktree_moi(tmp_path):
    goc, mea = _hai_repo(tmp_path, goc={"a.md": "1\n", "b.md": "MOI\n"}, mea_origin={"a.md": "1\n", "b.md": "CU\n"})
    (goc / ".claude/agents/b.md").write_text("CHUA-COMMIT\n", encoding="utf-8", newline="\n")   # không được sang y khoa
    wt_goc = tmp_path / "wt"
    ma, dong = D.ap_dung(goc, mea, NHANH, ["b.md"], mo_pr=False, luc=dt.datetime(2026, 11, 21, 9, 30), goc_wt=wt_goc)
    assert ma == 0, dong
    wt = wt_goc / "ykhoa-dong-bo-agent-20261121-0930"
    assert (wt / ".claude/agents/b.md").read_text(encoding="utf-8") == "MOI\n", "chép bản HEAD, không bản chưa commit"
    reg = (wt / "runtime/agent_registry.py").read_text(encoding="utf-8")
    assert SHA_MOI in reg and "đồng bộ bản sao b.md" in reg
    log = _g(wt, "log", "-1", "--name-only", "--format=%s")
    assert "đồng bộ bản sao b.md" in log and ".claude/agents/b.md" in log and "agent_source_manifest.csv" in log
    assert _g(wt, "status", "--porcelain").strip() == ""
    assert any("--mo-pr" in x for x in dong), "không --mo-pr ⇒ không đẩy, chỉ in hướng dẫn"
    ma2, dong2 = D.ap_dung(goc, mea, NHANH, ["b.md"], mo_pr=False, luc=dt.datetime(2026, 11, 21, 9, 30), goc_wt=wt_goc)
    assert ma2 == 3 and "đã tồn tại" in dong2[0], "không ghi chồng worktree cũ"


def test_giac_quan_hom_viec_tach_keo_cay(tmp_path):
    TD = _nap(REPO / "tools" / "tu_de_xuat_viec.py", "_dbay_td")
    g, m = tmp_path / "g", tmp_path / "m"
    g.mkdir()
    m.mkdir()
    for ten, ng, nm in (("pr.md", "MOI", "CU"), ("keo.md", "MOI", "CU"), ("khop.md", "X", "X")):
        (g / ten).write_text(ng, encoding="utf-8")
        (m / ten).write_text(nm, encoding="utf-8")
    origin = {"pr.md": b"CU", "keo.md": b"MOI"}
    ra = TD.giac_quan_agent_lech(g, m, doc_origin=origin.get)
    assert len(ra) == 2
    assert "1 lệch nội dung (pr.md)" in ra[0][1] and "dong_bo_agent_y_khoa.py" in ra[0][2]
    assert "chưa kéo (1: keo.md)" in ra[1][1] and "pull --ff-only" in ra[1][2]
    ra = TD.giac_quan_agent_lech(g, m)
    assert len(ra) == 1 and "2 lệch nội dung" in ra[0][1], "không có origin ⇒ hành vi cũ, không giấu lệch"
    def hong(_ten):
        raise OSError("git hỏng")
    assert "2 lệch nội dung" in TD.giac_quan_agent_lech(g, m, doc_origin=hong)[0][1], "đọc origin lỗi ⇒ vẫn báo cần PR cặp"
