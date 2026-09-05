#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CÀI PLUGIN CHO PHIÊN CLOUD theo sổ khai ý định `sync/plugin-manifest.json`.

VÌ SAO CÓ (02/09/2026 — quyết định của bác sĩ sau khi nghe lý do không cài)
==========================================================================
Phiên Claude Code trên WEB dựng container MỚI mỗi lần: không `~/.claude/plugins`, không
marketplace, không plugin. Skill riêng đã đi qua git (hook cloud, BH84); plugin thì không —
chúng nằm ở marketplace của từng máy. Bác sĩ quyết định: **cloud phải đủ plugin như local.**

Công cụ này đọc CÙNG sổ khai hai máy đang dùng (`sync/plugin-manifest.json`), lấy các mục có
`"Cloud"` trong `can_o_may`, rồi cài bằng chính CLI `claude plugin` — không tự viết bộ cài
riêng, không đụng `installed_plugins.json` bằng tay. Nguồn cài (`nguon`) có bốn loại:

  git            marketplace add <url>  (harness · humanizer · openai-codex)
  thu-muc-phien  repo anh em ĐÃ CLONE trong container làm marketplace kiểu đường dẫn
                 (aipoch · openmed — fork của bác sĩ); vắng thì clone `url_du_phong`
  git-thu-cong   kho KHÔNG có marketplace.json (meta-pipe · pubmed-search): clone nông, sinh
                 manifest, LỌC skill theo `tools/cap_nhat_plugin_tay.py::CAU_HINH` — đúng bản
                 10 skill tra y văn bác sĩ đã chọn, không đổ 16 skill lập trình nội bộ vào
  chua-ro        chỉ Mac biết nguồn → ⚪ có khai báo, KHÔNG đỏ (BH08); chờ `--xuat-nguon`

RANH GIỚI CỨNG — đọc trước khi mở rộng
=====================================
1. `--ap-dung` CHỈ chạy khi đúng là phiên cloud (`CLAUDE_CODE_REMOTE=true`). Trên Mac/Windows
   nó thoát 0 và KHÔNG chạm gì: bài học 11/08 (gỡ mục enabledPlugins làm Claude Code tải lại
   278 MB) và doctrine «tool không tự cài/gỡ plugin qua mạng trên máy thật» vẫn nguyên.
   Cờ `--toi-biet-day-la-cloud` chỉ để chốt hồi quy chạy trong HOME tạm.
2. Idempotent: plugin đã có trong `installed_plugins.json` và cache còn SKILL.md thì bỏ qua.
   Hook SessionStart gọi ở NỀN mỗi phiên (~1 phút lần đầu, <1 giây khi đã đủ).
3. 8 plugin medsci trùng có `can_o_may: []` nên không bao giờ được cài — kể cả trên cloud.
4. Plugin vẫn chỉ là WORKER (bảng định tuyến CLAUDE.md / `_PLUGIN-ROUTING-CONTRACT.md`);
   có mặt trên cloud không đổi chủ của bất kỳ việc có cổng nào.
5. `--xuat-nguon` chạy được ở MỌI máy: đọc `~/.claude/plugins/known_marketplaces.json` của máy
   đang chạy và điền vào sổ khai những mục còn `chua-ro`. Không cài gì.

Mã thoát: 0 = đủ/không việc · 1 = có plugin cài lỗi hoặc còn thiếu (chỉ đọc) · 2 = lỗi đầu vào.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

for _s in (sys.stdout, sys.stderr):  # Windows cp1252 giết print() tiếng Việt (BH55/R4)
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
SO_KHAI = REPO / "sync" / "plugin-manifest.json"
MAY_CLOUD = "Cloud"
LOAI_HOP_LE = ("git", "thu-muc-phien", "git-thu-cong", "chua-ro")
THOI_HAN_GIAY = 900  # aipoch chép 808 MB vào cache mất ~35 giây; trần rộng cho mạng chậm


def _home() -> Path:
    return Path.home()


def duong_plugins() -> Path:
    return _home() / ".claude" / "plugins"


def la_phien_cloud() -> bool:
    return os.environ.get("CLAUDE_CODE_REMOTE", "").strip().lower() == "true"


def doc_json(p: Path) -> dict:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def claude_bin() -> str | None:
    return shutil.which("claude")


def chay(lenh: list[str], cwd: Path | None = None, thoi_han: int = THOI_HAN_GIAY) -> tuple[int, str, float]:
    t0 = time.monotonic()
    try:
        r = subprocess.run(lenh, cwd=cwd, capture_output=True, text=True, timeout=thoi_han,
                           encoding="utf-8", errors="replace")
        return r.returncode, (r.stdout + r.stderr).strip(), time.monotonic() - t0
    except subprocess.TimeoutExpired:
        return 124, f"quá {thoi_han}s", time.monotonic() - t0
    except OSError as exc:
        return 127, str(exc), time.monotonic() - t0


# ── trạng thái kho trên máy này ────────────────────────────────────────────────

def marketplace_da_khai() -> set[str]:
    d = doc_json(duong_plugins() / "known_marketplaces.json")
    return set(d.keys()) if isinstance(d, dict) else set()


def plugin_da_cai() -> dict[str, dict]:
    """{plugin@marketplace: {'installPath', 'version', 'skill': n}} — chỉ mục còn cache thật."""
    d = doc_json(duong_plugins() / "installed_plugins.json")
    ra: dict[str, dict] = {}
    for khoa, v in (d.get("plugins") or {}).items():
        e = v[0] if isinstance(v, list) and v else v
        if not isinstance(e, dict):
            continue
        p = Path(str(e.get("installPath") or ""))
        n = len(list(p.rglob("SKILL.md"))) if p.is_dir() else 0
        ra[khoa] = {"installPath": str(p), "version": e.get("version"), "skill": n}
    return ra


# ── nguồn cài ─────────────────────────────────────────────────────────────────

def _cau_hinh_thu_cong(ten: str) -> dict:
    """Bảng curation của bác sĩ trong tools/cap_nhat_plugin_tay.py — MỘT nguồn, không chép."""
    import importlib.util
    duong = REPO / "tools" / "cap_nhat_plugin_tay.py"
    spec = importlib.util.spec_from_file_location("_cnpt_cloud", duong)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    cfg = mod.CAU_HINH.get(ten)
    if not cfg:
        raise KeyError(f"CAU_HINH không có '{ten}'")
    return {"url": cfg["url"], "kho": cfg["kho"], "giu_skill": cfg.get("giu_skill"),
            "bo_qua": set(mod.BO_QUA_CHUNG) | set(cfg.get("bo_them") or ())}


def sinh_manifest(kho: Path, ten_marketplace: str, ten_plugin: str, mo_ta: str,
                  giu_skill: set[str] | None) -> int:
    """Sinh .claude-plugin/marketplace.json liệt kê đúng các thư mục có SKILL.md
    (lọc theo `giu_skill` trên TÊN thư mục ngay chứa SKILL.md). Trả số skill khai.

    CHỈ sinh marketplace.json — KHÔNG sinh thêm plugin.json (vá 05/09/2026). Tài liệu
    Claude Code chính thức: `strict: false` trong mục plugin của marketplace.json nghĩa
    là "mục này là ĐỊNH NGHĨA DUY NHẤT"; nếu CÙNG thư mục còn có `.claude-plugin/
    plugin.json` cũng khai component (như `skills` ở đây) thì đó là xung đột và
    **CẢ PLUGIN KHÔNG NẠP ĐƯỢC** — im lặng, cache vẫn giữ đủ file nên mọi phép đếm
    file (kiem_plugin_day_du.py) vẫn báo đủ, chỉ có model không bao giờ thấy skill nào.
    Bắt được đúng lỗi này ở meta-pipe/pubmed-search: cả hai vắng mặt hoàn toàn khỏi
    danh sách skill thật của Claude Code dù cache có đủ 14/10 SKILL.md. Khuôn theo
    aipoch-medical-research — plugin DUY NHẤT trong kho đang hoạt động đúng, và nó
    KHÔNG có plugin.json, chỉ có marketplace.json với `strict: false` + `skills`."""
    skills: list[str] = []
    for p in sorted(kho.rglob("SKILL.md")):
        if ".git" in p.parts or "node_modules" in p.parts:
            continue
        if giu_skill is not None and p.parent.name not in giu_skill:
            continue
        skills.append("./" + p.parent.relative_to(kho).as_posix())
    (kho / ".claude-plugin").mkdir(exist_ok=True)
    cu = kho / ".claude-plugin" / "plugin.json"
    if cu.is_file():
        cu.unlink()
    (kho / ".claude-plugin" / "marketplace.json").write_text(json.dumps({
        "$schema": "https://json.schemastore.org/claude-code-marketplace.json",
        "name": ten_marketplace, "description": mo_ta, "owner": {"name": "EBM-drluanbv175"},
        "plugins": [{"name": ten_plugin, "description": mo_ta, "source": "./",
                     "strict": False, "skills": skills}],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(skills)


def chuan_bi_nguon(khoa: str, nguon: dict, log: list[str]) -> tuple[str | None, str]:
    """Trả (đối số cho `marketplace add`, ghi chú). None = không có gì để cài."""
    loai = nguon.get("loai")
    if loai == "git":
        return nguon["url"], "git"
    if loai == "thu-muc-phien":
        d = (REPO / nguon["duong_dan"]).resolve()
        if (d / ".claude-plugin" / "marketplace.json").is_file():
            return str(d), "thư mục phiên"
        url = nguon.get("url_du_phong")
        if not url:
            log.append(f"{khoa}: thư mục phiên vắng ({d}) và không có url_du_phong")
            return None, "thiếu nguồn"
        dich = duong_plugins() / "nguon-thu-cong" / d.name
        if not (dich / ".claude-plugin" / "marketplace.json").is_file():
            dich.parent.mkdir(parents=True, exist_ok=True)
            shutil.rmtree(dich, ignore_errors=True)
            rc, out, _ = chay(["git", "clone", "-q", "--depth", "1", url, str(dich)])
            if rc != 0:
                log.append(f"{khoa}: clone dự phòng thất bại: {out[-200:]}")
                return None, "clone lỗi"
        return str(dich), "clone dự phòng"
    if loai == "git-thu-cong":
        try:
            cfg = _cau_hinh_thu_cong(nguon["cau_hinh"])
        except (KeyError, OSError, AttributeError) as exc:
            log.append(f"{khoa}: không đọc được CAU_HINH — {exc}")
            return None, "thiếu cấu hình"
        dich = duong_plugins() / "nguon-thu-cong" / cfg["kho"]
        if not (dich / ".git").is_dir():
            dich.parent.mkdir(parents=True, exist_ok=True)
            shutil.rmtree(dich, ignore_errors=True)
            rc, out, _ = chay(["git", "clone", "-q", "--depth", "1", cfg["url"], str(dich)])
            if rc != 0:
                log.append(f"{khoa}: clone thất bại: {out[-200:]}")
                return None, "clone lỗi"
        ten_plugin, ten_mk = khoa.split("@", 1)
        giu = set(cfg["giu_skill"]) if cfg.get("giu_skill") else None
        n = sinh_manifest(dich, ten_mk, ten_plugin,
                          f"{ten_plugin} — cài cho phiên cloud từ {cfg['url']} theo curation "
                          f"tools/cap_nhat_plugin_tay.py", giu)
        return str(dich), f"clone + manifest {n} skill" + (" (đã lọc)" if giu else "")
    if loai == "chua-ro":
        return None, "chưa rõ nguồn"
    log.append(f"{khoa}: loai nguồn lạ {loai!r} (hợp lệ: {', '.join(LOAI_HOP_LE)})")
    return None, "loại lạ"


# ── cài ───────────────────────────────────────────────────────────────────────

def cai_mot(khoa: str, nguon: dict, cai: dict[str, dict], mk_co: set[str],
            ap_dung: bool, log: list[str]) -> dict:
    ten_plugin, ten_mk = khoa.split("@", 1)
    kq = {"plugin": khoa, "loai": nguon.get("loai"), "trang_thai": "", "skill": 0, "giay": 0.0}
    da = cai.get(khoa)
    if da and da["skill"] > 0:
        kq.update(trang_thai="đã có", skill=da["skill"])
        return kq
    if nguon.get("loai") == "chua-ro":
        kq["trang_thai"] = "⚪ chưa rõ nguồn"
        return kq
    if not ap_dung:
        kq["trang_thai"] = "thiếu (sẽ cài với --ap-dung)"
        return kq
    cb = claude_bin()
    if not cb:
        log.append(f"{khoa}: không có CLI `claude` trong PATH")
        kq["trang_thai"] = "lỗi: không có claude"
        return kq
    t0 = time.monotonic()
    src, ghi = chuan_bi_nguon(khoa, nguon, log)
    if src is None:
        kq["trang_thai"] = f"lỗi: {ghi}"
        kq["giay"] = round(time.monotonic() - t0, 1)
        return kq
    if ten_mk not in mk_co:
        rc, out, _ = chay([cb, "plugin", "marketplace", "add", src, "--scope", "user"])
        if rc != 0:
            log.append(f"{khoa}: marketplace add thất bại: {out[-240:]}")
            kq["trang_thai"] = "lỗi: marketplace add"
            kq["giay"] = round(time.monotonic() - t0, 1)
            return kq
        mk_co.add(ten_mk)
    rc, out, _ = chay([cb, "plugin", "install", khoa, "--scope", "user", "-y"])
    if rc != 0:
        log.append(f"{khoa}: install thất bại: {out[-240:]}")
        kq["trang_thai"] = "lỗi: install"
        kq["giay"] = round(time.monotonic() - t0, 1)
        return kq
    if nguon.get("loai") == "git-thu-cong":
        # CLI chép TRỌN kho vào cache — với pubmed-search là 35 SKILL.md trong khi bản Mac
        # (chep_vao_cache của cap_nhat_plugin_tay) chỉ giữ 10. Cắt tỉa cho khớp: xoá thư
        # mục skill ngoài giu_skill và các thư mục bo_qua, để mốc/kiểm kê hai máy so được.
        try:
            cfg = _cau_hinh_thu_cong(nguon["cau_hinh"])
            cat_tia_cache(khoa, cfg.get("giu_skill"), cfg["bo_qua"], log)
        except (KeyError, OSError, AttributeError) as exc:
            log.append(f"{khoa}: không cắt tỉa được cache — {exc}")
    sau = plugin_da_cai().get(khoa, {})
    kq.update(trang_thai=f"✓ cài mới ({ghi})", skill=sau.get("skill", 0),
              giay=round(time.monotonic() - t0, 1))
    if kq["skill"] == 0:
        log.append(f"{khoa}: cài xong nhưng cache không có SKILL.md nào")
        kq["trang_thai"] = "lỗi: cache rỗng"
    return kq


def cat_tia_cache(khoa: str, giu_skill: set[str] | None, bo_qua: set[str], log: list[str]) -> int:
    """Xoá khỏi cache của `khoa` những thư mục skill ngoài `giu_skill` và thư mục `bo_qua`.
    CHỈ đụng bên trong installPath của chính plugin đó; trả số thư mục đã xoá."""
    da = plugin_da_cai().get(khoa)
    if not da:
        return 0
    goc = Path(da["installPath"])
    if not goc.is_dir() or goc == goc.anchor or ".claude/plugins/cache" not in goc.as_posix():
        log.append(f"{khoa}: installPath lạ, không cắt tỉa: {goc}")
        return 0
    xoa = 0
    if giu_skill is not None:
        for f in list(goc.rglob("SKILL.md")):
            if ".git" in f.parts:
                continue
            if f.parent.name not in giu_skill:
                shutil.rmtree(f.parent, ignore_errors=True)
                xoa += 1
    for ten in sorted(bo_qua):
        d = goc / ten
        if d.is_dir() and not d.is_symlink():
            shutil.rmtree(d, ignore_errors=True)
            xoa += 1
    return xoa


# ── xuất nguồn từ máy thật ─────────────────────────────────────────────────────

def xuat_nguon(so: dict) -> tuple[int, list[str]]:
    """Điền `nguon` cho mục còn chua-ro từ known_marketplaces.json của máy đang chạy."""
    kmp = doc_json(duong_plugins() / "known_marketplaces.json")
    dien: list[str] = []
    for khoa, m in so.get("plugin", {}).items():
        ng = m.get("nguon") or {}
        if ng.get("loai") not in (None, "chua-ro"):
            continue
        ten_mk = khoa.split("@", 1)[1]
        e = kmp.get(ten_mk) or {}
        src = e.get("source") if isinstance(e, dict) else None
        if not isinstance(src, dict):
            continue
        if src.get("source") in ("github", "git") and (src.get("repo") or src.get("url")):
            url = src.get("url") or f"https://github.com/{src['repo']}"
            m["nguon"] = {"loai": "git", "url": url,
                          "ghi_chu": f"xuất từ known_marketplaces.json ngày {time.strftime('%Y-%m-%d')}"}
            dien.append(f"{khoa} ← {url}")
        elif src.get("source") == "directory" and src.get("path"):
            m["nguon"] = {"loai": "chua-ro",
                          "ghi_chu": f"[CẦN BÁC SĨ] máy này cài kiểu thư mục từ {src['path']} — "
                                     f"khai url git của kho đó vào loai 'git' (hoặc git-thu-cong nếu kho thiếu marketplace.json)"}
            dien.append(f"{khoa}: thư mục {src['path']} — cần bác sĩ khai url")
    return len(dien), dien


def main() -> int:
    ap = argparse.ArgumentParser(description="Cài plugin cho phiên cloud theo sổ khai ý định")
    ap.add_argument("--ap-dung", action="store_true", help="cài (chỉ khi là phiên cloud)")
    ap.add_argument("--toi-biet-day-la-cloud", action="store_true",
                    help="bỏ kiểm CLAUDE_CODE_REMOTE — CHỈ cho chốt hồi quy chạy trong HOME tạm")
    ap.add_argument("--xuat-nguon", action="store_true",
                    help="máy thật: điền nguồn marketplace vào sổ khai cho mục còn chưa rõ")
    ap.add_argument("--im-khi-on", action="store_true", help="im khi mọi thứ đã đủ")
    ap.add_argument("--json", action="store_true", help="xuất JSON máy đọc")
    ap.add_argument("--so-khai", default=str(SO_KHAI), metavar="FILE",
                    help="sổ khai khác (CHỈ cho chốt hồi quy chạy trên fixture)")
    a = ap.parse_args()

    so_khai_path = Path(a.so_khai)
    so = doc_json(so_khai_path)
    if not so.get("plugin"):
        print(f"✗ Không đọc được sổ khai {so_khai_path}", file=sys.stderr)
        return 2

    if a.xuat_nguon:
        n, dong = xuat_nguon(so)
        if n:
            luu = so_khai_path.with_name(f"{so_khai_path.name}.bak-{time.strftime('%Y%m%d-%H%M%S')}")
            shutil.copy2(so_khai_path, luu)
            so_khai_path.write_text(json.dumps(so, ensure_ascii=False, indent=2) + "\n",
                                    encoding="utf-8", newline="\n")
            print(f"✓ Đã điền {n} nguồn vào sổ khai (sao lưu {luu.name}) — commit để cloud dùng:")
            for d in dong:
                print("   •", d)
        else:
            print("Không có mục chua-ro nào tra được từ known_marketplaces.json của máy này.")
        return 0

    if a.ap_dung and not (la_phien_cloud() or a.toi_biet_day_la_cloud):
        print("KHÔNG CHẠY: đây không phải phiên cloud (CLAUDE_CODE_REMOTE≠true). "
              "Máy thật không tự cài plugin qua mạng — bài học 11/08.")
        return 0

    muc = {k: m for k, m in so["plugin"].items() if MAY_CLOUD in (m.get("can_o_may") or [])}
    cai = plugin_da_cai()
    mk_co = marketplace_da_khai()
    log: list[str] = []
    ket: list[dict] = []
    for khoa, m in sorted(muc.items()):
        ng = m.get("nguon") or {"loai": "chua-ro"}
        ket.append(cai_mot(khoa, ng, cai, mk_co, a.ap_dung, log))

    du = sum(1 for k in ket if k["trang_thai"].startswith(("đã có", "✓")))
    chua_ro = sum(1 for k in ket if k["trang_thai"].startswith("⚪"))
    thieu = [k for k in ket if k["trang_thai"].startswith("thiếu")]
    loi = [k for k in ket if k["trang_thai"].startswith("lỗi")]

    if a.json:
        print(json.dumps({"may": MAY_CLOUD if la_phien_cloud() else "khong-phai-cloud",
                          "du": du, "chua_ro": chua_ro, "thieu": len(thieu), "loi": len(loi),
                          "plugin": ket, "log": log}, ensure_ascii=False, indent=2))
    elif not (a.im_khi_on and not thieu and not loi):
        print(f"PLUGIN CHO PHIÊN CLOUD — {du}/{len(ket)} đủ · ⚪ {chua_ro} chưa rõ nguồn · "
              f"thiếu {len(thieu)} · lỗi {len(loi)}")
        for k in ket:
            them = f" · {k['skill']} SKILL.md" if k["skill"] else ""
            giay = f" · {k['giay']}s" if k["giay"] else ""
            print(f"  {k['trang_thai']:<34} {k['plugin']}{them}{giay}")
        for d in log:
            print("  ⚠", d)
        if chua_ro:
            print("  ⚪ chưa rõ nguồn = chỉ Mac biết: trên Mac chạy "
                  "`python3 tools/cai_plugin_phien_cloud.py --xuat-nguon` rồi commit sổ khai.")
        print("  Plugin trên cloud vẫn chỉ là worker — chủ của việc có cổng không đổi. Cần bác sĩ kiểm chứng.")
    return 1 if (thieu or loi) else 0


if __name__ == "__main__":
    raise SystemExit(main())
