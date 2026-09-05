#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cap_nhat_plugin_tay.py — Cập nhật các plugin mà nút "Update" của app KHÔNG làm được.

VÌ SAO CẦN: ba kho meta-pipe · pubmed-search · aipoch-medical-research không kèm sẵn
manifest plugin, nên phải khai vào Claude Code dưới dạng marketplace kiểu `directory`
(trỏ vào một thư mục trên máy). Kiểu `directory` KHÔNG có nguồn từ xa, nên app không
biết lấy bản mới ở đâu — bấm cập nhật cũng không có gì xảy ra. 11 marketplace còn lại
là kiểu `git` nên app tự lo được.

Script này làm đúng phần app không làm: kéo bản mới từ GitHub → dựng lại manifest →
chép vào cache app đang dùng → áp lại bản dịch tiếng Việt.

RỦI RO ĐÃ GẶP THẬT, ĐỪNG QUÊN: kiểu `directory` nạp THẲNG từ thư mục clone. Xoá thư
mục đó là giết plugin — ngày 05/08/2026 cả ba thư mục đều biến mất (nhiều khả năng do
một đợt dọn đĩa) và aipoch mất luôn cache. Script tự phát hiện thư mục mất và clone lại.

Chạy:  python3 tools/cap_nhat_plugin_tay.py            # cập nhật tất cả
       python3 tools/cap_nhat_plugin_tay.py --xem-truoc # chỉ xem, không đổi gì
       python3 tools/cap_nhat_plugin_tay.py --chi meta-pipe
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shlex
import shutil
import subprocess
import sys

# Windows: stdout mặc định cp1252 giết print() tiếng Việt — ép UTF-8 (chốt BH55/R4)
import sys as _sys_r4
for _s_r4 in (_sys_r4.stdout, _sys_r4.stderr):
    try:
        _s_r4.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

HOME = pathlib.Path.home()
KHO_GOC = HOME / "Documents" / "GitHub"
CACHE = HOME / ".claude" / "plugins" / "cache"
INSTALLED = HOME / ".claude" / "plugins" / "installed_plugins.json"

# Thư mục KHÔNG chép vào cache: công cụ lập trình nội bộ của chính kho đó, không liên
# quan việc của bác sĩ, chỉ làm rối danh sách khi gõ `/` và phình cache.
BO_QUA_CHUNG = {".git", ".github", ".vscode", ".cline", ".codex", "tests", "node_modules"}

CAU_HINH = {
    "meta-pipe": {
        "kho": "meta-pipe",
        "url": "https://github.com/htlin222/meta-pipe",
        "plugin_key": "meta-pipe@meta-pipe",
        "bo_them": set(),
        # None = giữ nguyên manifest viết tay trong kho (nó là file chưa track nên
        # `git pull` không đụng tới)
        "sinh_manifest": None,
    },
    "pubmed-search": {
        "kho": "pubmed-search-mcp",
        "url": "https://github.com/u9401066/pubmed-search-mcp",
        "plugin_key": "pubmed-search@pubmed-search",
        # giữ docs/ và scripts/ vì 10 skill có tham chiếu thật vào đó
        "bo_them": {"memory-bank", "nginx", "copilot-studio"},
        # kho mang 26 skill; chỉ 10 skill tra y văn là việc của bác sĩ, 16 skill còn lại
        # (code-reviewer, git-precommit, test-generator…) là công cụ lập trình nội bộ
        "giu_skill": {"pubmed-" + x for x in (
            "quick-search", "pico-search", "systematic-search", "multi-source-search",
            "fulltext-access", "paper-exploration", "export-citations",
            "gene-drug-research", "research-chronicle", "mcp-tools-reference")},
        "sinh_manifest": None,
    },
    "watermarks-remover": {
        "kho": "watermarks-remover",
        "url": "https://github.com/guillaumemeyer/watermarks-remover",
        "plugin_key": "watermarks-remover@watermarks-remover",
        "bo_them": {"docs", "integrations", "service/scripts/__pycache__"},
        "sinh_manifest": None,
    },
    "aipoch-medical-research": {
        "kho": "medical-research-skills",
        "url": "https://github.com/aipoch/medical-research-skills",
        "plugin_key": "aipoch-medical-research@aipoch-medical-research",
        "bo_them": set(),
        # kho này 605 skill và hay thêm skill mới → sinh lại manifest từ cây thư mục
        "sinh_manifest": "quet",
    },
}


def chay(lenh: list[str], cwd: pathlib.Path | None = None) -> tuple[int, str]:
    r = subprocess.run(lenh, cwd=cwd, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def duong_dan_cache(plugin_key: str) -> pathlib.Path | None:
    """Đọc installPath app ĐANG dùng — không tự đoán, vì app có thể đã đổi mã băm."""
    if not INSTALLED.exists():
        return None
    d = json.loads(INSTALLED.read_text("utf-8"))
    p = d.get("plugins", d).get(plugin_key)
    if not p:
        return None
    e = p[0] if isinstance(p, list) else p
    return pathlib.Path(e.get("installPath", "")) or None


def sinh_manifest_quet(kho: pathlib.Path, ten: str, mo_ta: str, chu: str) -> int:
    """CHỈ sinh marketplace.json — KHÔNG sinh thêm plugin.json (vá 05/09/2026).

    `strict: false` trong mục plugin của marketplace.json nghĩa là "mục này là ĐỊNH
    NGHĨA DUY NHẤT" (tài liệu Claude Code chính thức); nếu cùng thư mục còn có
    `.claude-plugin/plugin.json` cũng khai `skills` thì xung đột — CẢ PLUGIN KHÔNG
    NẠP ĐƯỢC, im lặng (cache vẫn đủ file nên đếm-file vẫn báo đủ). Bắt được đúng lỗi
    này ở meta-pipe/pubmed-search (phiên bản cũ của hàm này để lại trong kho của họ).
    aipoch-medical-research — plugin DUY NHẤT KHÔNG có plugin.json — là bản đang chạy
    đúng; hàm này nay khuôn theo đúng bản đó."""
    skills = sorted("./" + str(p.parent.relative_to(kho))
                    for p in kho.rglob("SKILL.md") if ".git" not in p.parts)
    (kho / ".claude-plugin").mkdir(exist_ok=True)
    cu = kho / ".claude-plugin/plugin.json"
    if cu.is_file():
        cu.unlink()
    (kho / ".claude-plugin/marketplace.json").write_text(json.dumps({
        "$schema": "https://json.schemastore.org/claude-code-marketplace.json",
        "name": ten, "description": mo_ta, "owner": {"name": chu},
        "plugins": [{"name": ten, "description": mo_ta, "source": "./",
                     "strict": False, "skills": skills}],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(skills)


def chep_vao_cache(kho: pathlib.Path, dich: pathlib.Path, bo_qua: set[str],
                   giu_skill: set[str] | None = None) -> int:
    """Chép kho vào cache bằng `tar`, KHÔNG dùng shutil.copytree.

    Vì sao tar: copytree gãy 4231 lần với [Errno 2] trên kho aipoch (605 skill, tên
    thư mục có dấu cách và chữ hoa) dù mọi đường dẫn đều tồn tại và không có symlink
    gãy. Ống tar cục bộ xử lý cùng cây đó sạch sẽ — đã kiểm bằng lần dựng cache đầu.

    giu_skill: nếu có, CHỈ giữ các thư mục con này trong `.claude/skills/` — dùng cho
    pubmed-search, nơi kho mang thêm 16 skill lập trình nội bộ không liên quan bác sĩ.
    """
    dich.mkdir(parents=True, exist_ok=True)
    for cu in dich.iterdir():          # dọn sạch đích trước, tránh lẫn bản cũ
        shutil.rmtree(cu) if cu.is_dir() and not cu.is_symlink() else cu.unlink()

    loai = " ".join("--exclude=" + shlex.quote(f"./{t}") for t in sorted(bo_qua))
    lenh = (f"cd {shlex.quote(str(kho))} && tar {loai} -cf - . "
            f"| (cd {shlex.quote(str(dich))} && tar -xf -)")
    ma, out = chay(["bash", "-c", lenh])
    if ma != 0:
        raise RuntimeError(f"tar thất bại: {out[:200]}")

    if giu_skill is not None:
        thu_muc_skill = dich / ".claude" / "skills"
        if thu_muc_skill.exists():
            for s in thu_muc_skill.iterdir():
                if s.is_dir() and s.name not in giu_skill:
                    shutil.rmtree(s)
    return len(list(dich.rglob("SKILL.md")))


def main() -> int:
    ap = argparse.ArgumentParser(description="Cập nhật plugin kiểu directory")
    ap.add_argument("--xem-truoc", action="store_true", help="chỉ báo, không thay đổi gì")
    ap.add_argument("--chi", metavar="TÊN", help="chỉ cập nhật một plugin")
    ts = ap.parse_args()

    muc_tieu = {ts.chi: CAU_HINH[ts.chi]} if ts.chi and ts.chi in CAU_HINH else CAU_HINH
    if ts.chi and ts.chi not in CAU_HINH:
        print(f"Không biết plugin '{ts.chi}'. Có: {', '.join(CAU_HINH)}")
        return 2

    print("=" * 68)
    print(" CẬP NHẬT PLUGIN KIỂU 'DIRECTORY' (app không tự làm được)")
    if ts.xem_truoc:
        print(" *** CHẾ ĐỘ XEM TRƯỚC — không thay đổi gì ***")
    print("=" * 68)

    loi = 0
    for ten, cfg in muc_tieu.items():
        kho = KHO_GOC / cfg["kho"]
        print(f"\n── {ten} ──")

        if not kho.exists():
            print(f"  thư mục nguồn ĐÃ MẤT: {kho}")
            if ts.xem_truoc:
                print(f"  → sẽ clone lại từ {cfg['url']}")
                continue
            print("  → clone lại…")
            ma, out = chay(["git", "clone", "-q", cfg["url"], str(kho)])
            if ma != 0:
                print(f"  ✗ clone thất bại: {out[:160]}")
                loi += 1
                continue
        elif not (kho / ".git").exists():
            print("  ! thư mục có nhưng KHÔNG phải kho git → không kéo bản mới được.")
            print("    Xoá thư mục rồi chạy lại script để clone sạch.")
            loi += 1
            continue
        else:
            if ts.xem_truoc:
                chay(["git", "fetch", "-q"], kho)
                _, sau = chay(["git", "rev-list", "--count", "HEAD..@{u}"], kho)
                print(f"  bản mới trên GitHub: {sau or '?'} commit chưa có ở máy")
                continue
            ma, out = chay(["git", "pull", "-q", "--ff-only"], kho)
            print(f"  git pull: {'OK' if ma == 0 else 'lỗi — ' + out[:120]}")

        if ts.xem_truoc:
            continue

        if cfg["sinh_manifest"] == "quet":
            n = sinh_manifest_quet(
                kho, ten,
                "605+ skill nghiên cứu y khoa (aipoch/medical-research-skills): thiết kế đề cương, "
                "thống kê, tin sinh, hình ảnh, viết bài và nộp tạp chí.", "aipoch")
            print(f"  sinh lại manifest: {n} skill")
        elif not (kho / ".claude-plugin/marketplace.json").exists():
            print("  ✗ THIẾU .claude-plugin/marketplace.json — kho vừa clone chưa có manifest "
                  "viết tay. Xem lại tài liệu cài đặt.")
            loi += 1
            continue

        dich = duong_dan_cache(cfg["plugin_key"])
        if not dich:
            print(f"  ✗ không tìm thấy {cfg['plugin_key']} trong installed_plugins.json")
            loi += 1
            continue
        n = chep_vao_cache(kho, dich, BO_QUA_CHUNG | cfg["bo_them"], cfg.get("giu_skill"))
        print(f"  chép vào cache: {n} SKILL.md → …/{dich.name}")

    if not ts.xem_truoc:
        print("\n── áp lại bản dịch tiếng Việt ──")
        goc = pathlib.Path(__file__).resolve().parent.parent
        # verify_vi.py cần PyYAML — chỉ có trong venv EBM, không có ở Python hệ thống
        venv_py = HOME / ".ebm-venv" / "bin" / "python"
        py = str(venv_py) if venv_py.exists() else sys.executable
        for buoc in ("extract_catalog.py", "apply_vi.py", "verify_vi.py"):
            ma, out = chay([py, str(goc / "tools/vietnamize" / buoc)], goc)
            cuoi = [d for d in out.splitlines() if d.strip()][-1] if out.strip() else ""
            print(f"  {buoc:<22} {'OK ' if ma == 0 else '✗ '}{cuoi[:88]}")

    print("\n" + "=" * 68)
    print(f" {'CÓ LỖI — xem ở trên' if loi else 'XONG'}. Mở lại Claude Code để nạp bản mới.")
    print(" Cần bác sĩ kiểm chứng.")
    print("=" * 68)
    return 1 if loi else 0


if __name__ == "__main__":
    raise SystemExit(main())
