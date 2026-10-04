#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Đóng gói skill của bác sĩ thành ZIP để BÁC SĨ TỰ TẢI LÊN tài khoản claude.ai (Cowork · claude.ai web · Routine) — 04/10/2026.

VÌ SAO: bộ skill của tài khoản chỉ đổi khi bác sĩ tải skill lên claude.ai. Đẩy vào ~/.claude/skills hay thư mục chạy cục bộ của
Claude Desktop KHÔNG lan lên tài khoản. Đo 04/10: 21/25 skill của bác sĩ trên tài khoản đã cũ (cap-nhat-chung-cu-y-khoa v1.15.0
so với repo v1.53.0 — Cowork chạy cổng tháng 9, chưa có BẢO ĐẢM ĐỌC TOÀN VĂN), 25 skill chưa từng lên (BH162/BH163).

LÀM GÌ (chỉ ĐỌC sync/skills/ và bộ skill tài khoản; chỉ GHI vào thư mục --ra):
  1. So TỪNG skill với bản tài khoản theo TOÀN BỘ tệp sẽ đóng gói (`doi_chieu_ba_ben.tep_skill`), không chỉ SKILL.md: trùng hết ⇒
     «đã mới»; khác ⇒ «cập nhật»; tài khoản chưa có ⇒ «mới»; SKILL.md cùng tên mà nội dung khác hẳn ⇒ «khác hẳn» (không đóng mặc
     định — tải lên sẽ THAY một skill khác trên tài khoản).
  2. Kiểm luật tải lên — nguồn: skill-creator của Anthropic (scripts/quick_validate.py + package_skill.py, có sẵn trong bộ skill
     tài khoản, đọc 04/10/2026): đúng MỘT SKILL.md · có frontmatter · `name` kebab-case ≤ 64 ký tự, không chứa «anthropic»/
     «claude» (tài liệu Skills API) · `description` không rỗng, ≤ 1024 ký tự, không có dấu < > · `compatibility` ≤ 500 ký tự.
     Vi phạm ⇒ KHÔNG đóng gói skill đó (mã thoát 1). Khoá frontmatter ngoài chuẩn chỉ CẢNH BÁO: claude.ai đã từng nhận khoá
     `author` (nghien-cuu-ebm-tong-hop, 08/09/2026) và frontmatter YAML không chặt — parser ở đây cố ý khoan dung như vậy.
  3. Đóng ZIP như package_skill.py: gốc ZIP là thư mục <tên>/; CHỈ tệp git track (tệp chưa commit/rác cục bộ không lên tài khoản);
     bỏ __pycache__/node_modules/*.pyc/.DS_Store và evals/ ở gốc; thứ tự tệp, dấu thời gian, quyền tệp cố định ⇒ cùng nội dung
     thì cùng từng byte trên cùng máy.
  4. `name` khác tên thư mục ⇒ bản ĐÓNG GÓI ghi `name` = tên thư mục, nguồn giữ nguyên. Spec Agent Skills buộc khớp, và tài khoản
     định danh skill theo tên: `citation-management-kdense` mang name «citation-management» sẽ ĐÈ skill tiếng Việt cùng tên.
  5. Ghi DANH-SACH-TAI-LEN.md (thứ tự tải: cập nhật trước, mới sau) và .dong-goi.json (sổ của lượt — lượt sau chỉ xoá ĐÚNG các ZIP
     ghi trong sổ, không đụng tệp khác trong thư mục).

KHÔNG tự tải lên — thao tác trên tài khoản là của bác sĩ. Skill trong `CHI_CLAUDE_CODE` không đóng gói mặc định (nêu lý do; muốn
vẫn đóng thì `--skill <tên>`).

Mã thoát: 0 xong (kể cả không có gì cần tải) · 1 có skill bị chặn vì vi phạm luật tải lên · 3 không đo được (thiếu bộ skill tài
khoản — chạy `--khong-so` để đóng gói mà không so).
Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
HUB = REPO / "sync" / "skills"
RA_MAC_DINH = REPO / "CLAUDE_AI_SKILLS"   # thư mục mới ở gốc repo bị luật `/*` của .gitignore bỏ qua ⇒ ZIP không vào git
SO_LUOT = ".dong-goi.json"
DANH_SACH = "DANH-SACH-TAI-LEN.md"

_sp = importlib.util.spec_from_file_location("_dcbb_dong_goi", Path(__file__).resolve().parent / "doi_chieu_ba_ben.py")
dcbb = importlib.util.module_from_spec(_sp)
sys.modules["_dcbb_dong_goi"] = dcbb
_sp.loader.exec_module(dcbb)
KhongDoDuoc = dcbb.KhongDoDuoc

# Luật tải lên — chép từ skill-creator/scripts/quick_validate.py (Anthropic) + tài liệu Skills API (từ dành riêng trong tên).
KHOA_CHUAN = frozenset({"name", "description", "license", "allowed-tools", "metadata", "compatibility"})
TEN_HOP_LE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
TU_CAM_TRONG_TEN = ("anthropic", "claude")
TRAN_TEN, TRAN_MO_TA, TRAN_TUONG_THICH = 64, 1024, 500
TRAN_ZIP_BYTE = 8 * 1024 * 1024   # giới hạn tải lên của Skills API; claude.ai có thể khác ⇒ chỉ CẢNH BÁO
NGAY_CO_DINH = (1980, 1, 1, 0, 0, 0)

# Skill chỉ có nghĩa trong Claude Code trên máy — tài khoản claude.ai không có các plugin mà chúng định tuyến.
CHI_CLAUDE_CODE = {
    "plugin-router-chatgpt": "định tuyến theo catalog plugin của Claude Code/Codex trên máy — tài khoản claude.ai không có các "
                             "plugin đó (bản cho ChatGPT nằm ở CHATGPT_SKILLS/dist/)",
    "dieu-phoi-aipoch": "định tuyến 605 skill của plugin aipoch-medical-research — plugin này chỉ cài trong Claude Code",
}

_FM = re.compile(r"^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|$)", re.S)
_KHOA = re.compile(r"^([A-Za-z0-9_-]+)[ \t]*:(.*)$")
_PHIEN_BAN = re.compile(r"^\s*version\s*:\s*[\"']?([^\"'\s]+)", re.M)
_TAC_GIA = re.compile(r"^\s*(?:skill-author|author)\s*:\s*[\"']?([^\"'\n]+)", re.M)


# ------------------------------------------------------------------ frontmatter khoan dung
def _gia_tri(dau: str, tiep: list[str]) -> str:
    """Giá trị chuỗi của một khoá cấp 1 (đủ để đo độ dài/ký tự, không phải parser YAML đầy đủ)."""
    dong_tiep = [d.strip() for d in tiep if d.strip()]
    if re.fullmatch(r"[|>][+-]?[0-9]?", dau):
        return ("\n" if dau.startswith("|") else " ").join(dong_tiep).strip()
    gt = " ".join([dau] + dong_tiep).strip()
    if len(gt) >= 2 and gt[0] == gt[-1] and gt[0] in "'\"":
        gt = gt[1:-1]
        gt = gt.replace("''", "'") if dau.startswith("'") else gt.replace('\\"', '"').replace("\\\\", "\\")
    return gt


def doc_frontmatter(van_ban: str) -> dict[str, str] | None:
    """Frontmatter → {khoá cấp 1: giá trị chuỗi}; None khi không có frontmatter. KHOAN DUNG có chủ ý: claude.ai đã nhận mô tả có
    «: » không bọc nháy (PyYAML chặt báo lỗi), nên chỉ cần đọc đúng khoá cấp 1 và giá trị của chúng."""
    m = _FM.match(van_ban)
    if not m:
        return None
    dong = m.group(1).splitlines()
    ket: dict[str, str] = {}
    i = 0
    while i < len(dong):
        mm = _KHOA.match(dong[i])
        if not mm:
            i += 1
            continue
        j = i + 1
        while j < len(dong) and (dong[j][:1] in (" ", "\t") or not dong[j].strip()):
            j += 1
        ket[mm.group(1)] = _gia_tri(mm.group(2).strip(), dong[i + 1:j])
        i = j
    return ket


def ghi_ten(van_ban: str, ten: str) -> str:
    """Thay ĐÚNG dòng `name:` trong frontmatter bằng `name: <ten>` (thiếu thì thêm vào đầu frontmatter); mọi byte khác giữ nguyên,
    kể cả kiểu xuống dòng."""
    m = _FM.match(van_ban)
    if not m:
        return van_ban
    fm = m.group(1)
    moi, n = re.subn(r"^name[ \t]*:[^\r\n]*", "name: " + ten, fm, count=1, flags=re.M)
    if n == 0:
        moi = "name: " + ten + ("\r\n" if "\r\n" in fm else "\n") + fm
    return van_ban[:m.start(1)] + moi + van_ban[m.end(1):]


def kiem_luat(ten: str, tep: dict[str, bytes]) -> tuple[list[str], list[str]]:
    """(lỗi chặn, cảnh báo) cho NỘI DUNG SẼ ĐÓNG GÓI (sau khi ghi lại name)."""
    loi: list[str] = []
    canh: list[str] = []
    thua = sorted(r for r in tep if r.rsplit("/", 1)[-1] == "SKILL.md" and r != "SKILL.md")
    if "SKILL.md" not in tep:
        loi.append("thiếu SKILL.md ở gốc skill")
    if thua:
        loi.append("claude.ai chỉ nhận ĐÚNG MỘT SKILL.md ở gốc — thừa: " + ", ".join(thua))
    if not TEN_HOP_LE.match(ten) or len(ten) > TRAN_TEN:
        loi.append(f"tên «{ten}» phải kebab-case (chữ thường, số, gạch nối) và ≤ {TRAN_TEN} ký tự")
    for tu in TU_CAM_TRONG_TEN:
        if tu in ten:
            loi.append(f"tên «{ten}» chứa từ dành riêng «{tu}»")
    if "SKILL.md" not in tep:
        return loi, canh
    try:
        vb = tep["SKILL.md"].decode("utf-8")
    except UnicodeDecodeError:
        return loi + ["SKILL.md không phải UTF-8"], canh
    fm = doc_frontmatter(vb)
    if fm is None:
        return loi + ["SKILL.md thiếu frontmatter YAML (--- … ---) ở đầu tệp"], canh
    if fm.get("name", "") != ten:
        loi.append(f"name «{fm.get('name', '')}» khác tên thư mục «{ten}»")
    mo_ta = fm.get("description", "")
    if not mo_ta:
        loi.append("frontmatter thiếu description")
    elif len(mo_ta) > TRAN_MO_TA:
        loi.append(f"description dài {len(mo_ta)} ký tự (tối đa {TRAN_MO_TA})")
    if "<" in mo_ta or ">" in mo_ta:
        loi.append("description có dấu < hoặc > (luật tải lên cấm)")
    if len(fm.get("compatibility", "")) > TRAN_TUONG_THICH:
        loi.append(f"compatibility dài quá {TRAN_TUONG_THICH} ký tự")
    la = sorted(set(fm) - KHOA_CHUAN)
    if la:
        canh.append(f"khoá frontmatter ngoài chuẩn {la} — skill-creator coi là lỗi; claude.ai từng nhận khoá «author». "
                    "Bị từ chối thì chuyển vào metadata")
    return loi, canh


# ------------------------------------------------------------------ đánh giá
def _thong_tin_fm(vb: str) -> tuple[str, str, str]:
    """(phiên bản, tác giả, mô tả rút gọn) để bác sĩ chọn skill nào tải."""
    m = _FM.match(vb)
    khoi = m.group(1) if m else ""
    pb = _PHIEN_BAN.search(khoi)
    tg = _TAC_GIA.search(khoi)
    mo_ta = (doc_frontmatter(vb) or {}).get("description", "")
    return (pb.group(1) if pb else ""), (tg.group(1).strip()[:40] if tg else ""), mo_ta[:110]


def _git_ban(thu_muc: Path) -> tuple[int, int]:
    """(số tệp ĐÃ track có thay đổi chưa commit, số tệp chưa track không phải rác) trong thư mục skill; git hỏng ⇒ (0, 0)."""
    try:
        r = subprocess.run(["git", "-C", str(thu_muc), "status", "--porcelain", "-z", "--", "."], capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return 0, 0
    if r.returncode != 0:
        return 0, 0
    sua = chua = 0
    for muc in r.stdout.decode("utf-8", "surrogateescape").split("\0"):
        if len(muc) < 4:
            continue
        if muc.startswith("??"):
            chua += not dcbb.la_tep_rac(muc[3:])
        else:
            sua += 1
    return sua, chua


def danh_gia(hub: Path, bundle: Path | None, chon: set[str] | None = None, tat_ca: bool = False) -> list[dict]:
    """Một mục cho MỖI skill trong `hub`. `bundle` None ⇒ không so (mọi skill «khong_so»). `chon` ⇒ chỉ các skill đó, đóng gói kể
    cả khi đã mới hay thuộc CHI_CLAUDE_CODE. Khoá `_tep` (nội dung sẽ đóng gói) không xuất JSON."""
    repo = dcbb.quet_thu_muc(hub)
    if bundle is not None and not bundle.is_dir():
        raise KhongDoDuoc(f"không có bộ skill tài khoản: {bundle}")
    if chon:
        thieu = sorted(chon - set(repo))
        if thieu:
            raise KhongDoDuoc(f"không có skill {', '.join(thieu)} trong {hub}")
    ket = []
    for ten in sorted(repo):
        if chon and ten not in chon:
            continue
        chon_tay = bool(chon)
        thu_muc = hub / ten
        nguon = {r: (thu_muc / r).read_bytes() for r in dcbb.liet_ke_tep_skill(thu_muc, chi_tep_git=True)}
        muc: dict = {"ten": ten, "so_tep": len(nguon), "byte": sum(len(b) for b in nguon.values()), "loi": [], "canh": [],
                     "doi_ten": "", "chi_tiet": {}}
        vb_nguon = nguon.get("SKILL.md", b"").decode("utf-8", "replace")
        muc["phien_ban"], muc["tac_gia"], muc["mo_ta"] = _thong_tin_fm(vb_nguon)
        muc["phien_ban_tk"] = ""
        if ten in CHI_CLAUDE_CODE and not chon_tay:
            muc.update(trang_thai="chi_claude_code", dong_goi=False, ly_do=CHI_CLAUDE_CODE[ten])
            ket.append(muc)
            continue
        if bundle is None:
            trang_thai = "khong_so"
        elif not (bundle / ten / "SKILL.md").is_file():
            trang_thai = "moi"
        else:
            tk = dcbb.tep_skill(bundle / ten)
            rp = {r: hashlib.sha256(b).hexdigest() for r, b in nguon.items()}
            muc["phien_ban_tk"] = _thong_tin_fm((bundle / ten / "SKILL.md").read_text(encoding="utf-8", errors="replace"))[0]
            if tk == rp:
                trang_thai = "da_moi"
            else:
                chung = set(tk) & set(rp)
                muc["chi_tiet"] = {"tep_khac": sum(1 for r in chung if tk[r] != rp[r]), "tep_moi": len(set(rp) - set(tk)),
                                   "tep_bo": len(set(tk) - set(rp)), "skill_md_khac": tk.get("SKILL.md") != rp.get("SKILL.md")}
                loai = dcbb.phan_loai(dcbb.Skill(ten, bundle / ten / "SKILL.md"), dcbb.Skill(ten, thu_muc / "SKILL.md"))[0]
                trang_thai = "khac_han" if loai == "KHÁC HẲN" else "cap_nhat"
        muc["trang_thai"] = trang_thai
        muc["dong_goi"] = chon_tay or trang_thai in ("moi", "cap_nhat", "khong_so") or (tat_ca and trang_thai == "da_moi")
        tep = dict(nguon)
        if "SKILL.md" in tep:
            fm = doc_frontmatter(vb_nguon) or {}
            if fm.get("name", "") != ten:
                muc["doi_ten"] = fm.get("name", "")
                tep["SKILL.md"] = ghi_ten(vb_nguon, ten).encode("utf-8")
        muc["loi"], muc["canh"] = kiem_luat(ten, tep)
        sua, chua = _git_ban(thu_muc)
        if sua:
            muc["canh"].append(f"{sua} tệp có thay đổi CHƯA commit — ZIP lấy bản trên đĩa (chưa qua chốt bí mật của pre-commit)")
        if chua:
            muc["canh"].append(f"{chua} tệp chưa git track KHÔNG được đóng gói — commit trước nếu cần")
        muc["_tep"] = tep
        ket.append(muc)
    return ket


# ------------------------------------------------------------------ ghi
def ghi_zip(dich: Path, ten: str, tep: dict[str, bytes], che_do: dict[str, int] | None = None) -> str:
    """ZIP tất định (thứ tự, dấu thời gian, quyền cố định); gốc là thư mục <ten>/. Trả sha256 của ZIP."""
    che_do = che_do or {}
    tam = dich.with_name(dich.name + ".tam")
    with zipfile.ZipFile(tam, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for rel in sorted(tep):
            zi = zipfile.ZipInfo(f"{ten}/{rel}", date_time=NGAY_CO_DINH)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.create_system = 3
            zi.external_attr = (0o100000 | che_do.get(rel, 0o644)) << 16
            z.writestr(zi, tep[rel])
    tam.replace(dich)
    return hashlib.sha256(dich.read_bytes()).hexdigest()


def _che_do(thu_muc: Path, tep: dict[str, bytes]) -> dict[str, int]:
    """Quyền tệp trong ZIP lấy theo GIT (100755 ⇒ 755, còn lại 644), KHÔNG theo đĩa. Đo 04/10/2026: OneDrive gắn bit thực thi
    (0o700) cho 7 tệp của cap-nhat-chung-cu-y-khoa ở cây chính mà worktree sạch là 644 ⇒ cùng nội dung ra hai ZIP khác byte. Không
    đọc được git ⇒ mọi tệp 644 (vẫn tất định)."""
    ma = {}
    try:
        r = subprocess.run(["git", "-C", str(thu_muc), "ls-files", "-s", "-z"], capture_output=True, timeout=60)
        if r.returncode == 0:
            for dong in r.stdout.decode("utf-8", "surrogateescape").split("\0"):
                dau, _, duong = dong.partition("\t")
                if duong:
                    ma[duong] = 0o755 if dau.split(" ", 1)[0] == "100755" else 0o644
    except (OSError, subprocess.SubprocessError):
        pass
    return {rel: ma.get(rel, 0o644) for rel in tep}


_NHAN = {"cap_nhat": "cập nhật", "moi": "mới", "da_moi": "đã mới", "khac_han": "KHÁC HẲN", "khong_so": "không so",
         "chi_claude_code": "chỉ Claude Code"}


def _dong_bang(i: int, m: dict) -> str:
    ct = m.get("chi_tiet") or {}
    khac = (f"{ct.get('tep_khac', 0)} khác · {ct.get('tep_moi', 0)} mới · {ct.get('tep_bo', 0)} bỏ" if ct else "—")
    pb = (f"{m['phien_ban_tk'] or '?'} → {m['phien_ban'] or '?'}" if m["trang_thai"] == "cap_nhat" else (m["phien_ban"] or "—"))
    ghi = "; ".join(([f"ZIP ghi name = tên thư mục (nguồn: «{m['doi_ten']}»)"] if m.get("doi_ten") else []) + m.get("canh", []))
    mo_ta = m.get("mo_ta", "").replace("|", "/")
    return f"| {i} | `{m['ten']}.zip` | {pb} | {khac} | {m['so_tep']} tệp · {m['byte'] // 1024} KB | {mo_ta} | {ghi or '—'} |"


def viet_danh_sach(ket: list[dict], luc: str, bundle: Path | None) -> str:
    dg = [m for m in ket if m.get("zip")]
    cap = [m for m in dg if m["trang_thai"] == "cap_nhat"]
    khac = [m for m in dg if m["trang_thai"] != "cap_nhat"]
    dong = [f"# Skill cần tải lên tài khoản claude.ai — {luc}", "",
            "Sinh bởi `python3 tools/dong_goi_skill_tai_khoan.py`. Bộ skill tài khoản đem so: "
            + (f"`{bundle}`." if bundle else "KHÔNG so (`--khong-so`)."), "",
            "## Cách tải (bác sĩ tự làm — Claude không thao tác trên tài khoản)",
            "1. Mở claude.ai → trang quản lý **Skills** trong cài đặt → tải lên từng tệp `.zip` dưới đây, nhóm ① trước.",
            "2. Skill nhóm ① đã có trên tài khoản: nếu claude.ai báo trùng tên, xoá hoặc tắt bản cũ cùng tên rồi tải lại.",
            "3. Nhóm ② là skill chưa từng lên — tuỳ bác sĩ chọn; đọc cột «Mô tả» để quyết.",
            "4. Xong thì chạy lại lệnh trên: sau khi app đồng bộ bộ skill tài khoản về máy, skill đã khớp chuyển sang «đã mới».", ""]
    tieu = "| # | Tệp | Phiên bản (tài khoản → repo) | Tệp khác | Cỡ | Mô tả | Ghi chú |"
    vach = "|---|---|---|---|---|---|---|"
    dong += [f"## ① Cập nhật — đã có trên tài khoản nhưng CŨ ({len(cap)})", "", tieu, vach]
    dong += [_dong_bang(i, m) for i, m in enumerate(cap, 1)] or ["| — | (không có) | | | | | |"]
    dong += ["", f"## ② Mới / theo yêu cầu — chưa có trên tài khoản ({len(khac)})", "", tieu, vach]
    dong += [_dong_bang(i, m) for i, m in enumerate(khac, 1)] or ["| — | (không có) | | | | | |"]
    chan = [m for m in ket if m["loi"] and m.get("dong_goi")]
    bo = [m for m in ket if not m.get("dong_goi")]
    dong += ["", "## ③ Không đóng gói", ""]
    dong += [f"- 🔴 `{m['ten']}` — vi phạm luật tải lên: {'; '.join(m['loi'])}" for m in chan]
    dong += [f"- `{m['ten']}` — {_NHAN.get(m['trang_thai'], m['trang_thai'])}"
             + (f": {m['ly_do']}" if m.get("ly_do") else "")
             + (" (tải lên sẽ THAY một skill khác cùng tên — bác sĩ quyết)" if m["trang_thai"] == "khac_han" else "")
             for m in bo]
    if not chan and not bo:
        dong.append("(không có)")
    dong += ["", "Cần bác sĩ kiểm chứng.", ""]
    return "\n".join(dong)


def dong_goi(ket: list[dict], hub: Path, ra: Path, bundle: Path | None, luc: str) -> dict:
    """Ghi ZIP cho các mục `dong_goi` không lỗi + danh sách + sổ lượt. Trước khi ghi: xoá ĐÚNG các ZIP mà sổ lượt trước ghi."""
    ra.mkdir(parents=True, exist_ok=True)
    so = ra / SO_LUOT
    try:
        cu = json.loads(so.read_text(encoding="utf-8")).get("zip", {}) if so.is_file() else {}
    except (OSError, ValueError, AttributeError):
        cu = {}
    for ten_tep in cu:
        p = ra / ten_tep
        if ten_tep.endswith(".zip") and "/" not in ten_tep and "\\" not in ten_tep and p.is_file():
            p.unlink()
    zip_moi = {}
    for m in ket:
        m["zip"] = ""
        if not m.get("dong_goi") or m["loi"]:
            continue
        dich = ra / f"{m['ten']}.zip"
        sha = ghi_zip(dich, m["ten"], m["_tep"], _che_do(hub / m["ten"], m["_tep"]))
        if dich.stat().st_size > TRAN_ZIP_BYTE:
            m["canh"].append(f"ZIP {dich.stat().st_size // 1024} KB > 8 MiB (giới hạn của Skills API) — claude.ai có thể từ chối")
        m["zip"] = dich.name
        zip_moi[dich.name] = sha
    (ra / DANH_SACH).write_text(viet_danh_sach(ket, luc, bundle), encoding="utf-8")
    so.write_text(json.dumps({"luc": luc, "bundle": str(bundle) if bundle else None, "zip": zip_moi},
                             ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return zip_moi


def tom_tat(ket: list[dict]) -> dict[str, list[str]]:
    """Gom tên skill theo trạng thái (cho giác quan hòm việc và dòng in)."""
    nhom: dict[str, list[str]] = {}
    for m in ket:
        nhom.setdefault(m["trang_thai"], []).append(m["ten"])
        if m["loi"] and m.get("dong_goi"):
            nhom.setdefault("chan", []).append(m["ten"])
    return nhom


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Đóng gói skill thành ZIP để bác sĩ tải lên tài khoản claude.ai.",
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("--hub", default=str(HUB), help="thư mục skill nguồn (mặc định sync/skills của repo)")
    ap.add_argument("--cloud", help="bộ skill tài khoản; bỏ trống thì tự dò ~/.claude/skills/synced/<uuid>")
    ap.add_argument("--ra", default=str(RA_MAC_DINH), help="thư mục ghi ZIP (mặc định CLAUDE_AI_SKILLS/ ở gốc repo, ngoài git)")
    ap.add_argument("--skill", action="append", default=[], help="chỉ đóng gói skill này (lặp được); bỏ qua phép chọn tự động")
    ap.add_argument("--tat-ca", action="store_true", help="đóng gói cả skill đã khớp tài khoản")
    ap.add_argument("--khong-so", action="store_true", help="không so với tài khoản — đóng gói mọi skill (trừ CHI_CLAUDE_CODE)")
    ap.add_argument("--chay-kho", action="store_true", help="chỉ báo, không ghi gì")
    ap.add_argument("--json", action="store_true", help="xuất JSON")
    a = ap.parse_args(argv)
    hub = Path(a.hub).expanduser().resolve()
    try:
        bundle = None if a.khong_so else dcbb.tim_bundle_cloud(a.cloud)
        ket = danh_gia(hub, bundle, set(a.skill) or None, a.tat_ca)
    except KhongDoDuoc as e:
        print(f"KHÔNG ĐO ĐƯỢC: {e}", file=sys.stderr)
        print("Không có bộ skill tài khoản để so thì chạy với --khong-so (đóng gói mọi skill).", file=sys.stderr)
        return 3
    luc = dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")
    ra = Path(a.ra).expanduser().resolve()
    if not a.chay_kho:
        dong_goi(ket, hub, ra, bundle, luc)
    nhom = tom_tat(ket)
    if a.json:
        print(json.dumps({"luc": luc, "bundle": str(bundle) if bundle else None, "ra": None if a.chay_kho else str(ra),
                          "skill": [{k: v for k, v in m.items() if not k.startswith("_")} for m in ket]},
                         ensure_ascii=False, indent=1))
    else:
        print(f"Skill tài khoản ↔ repo ({luc}): cập nhật {len(nhom.get('cap_nhat', []))} · mới {len(nhom.get('moi', []))} · "
              f"đã mới {len(nhom.get('da_moi', []))} · khác hẳn {len(nhom.get('khac_han', []))} · "
              f"chỉ Claude Code {len(nhom.get('chi_claude_code', []))}"
              + (f" · không so {len(nhom['khong_so'])}" if nhom.get("khong_so") else ""))
        for m in ket:
            if m["loi"] and m.get("dong_goi"):
                print(f"  🔴 {m['ten']}: {'; '.join(m['loi'])}")
        if a.chay_kho:
            print("  (chạy khô — không ghi gì)")
        else:
            so_zip = sum(1 for m in ket if m.get("zip"))
            print(f"  → {so_zip} tệp ZIP ở {ra}")
            print(f"  → danh sách và cách tải: {ra / DANH_SACH}")
        print("Cần bác sĩ kiểm chứng.")
    return 1 if nhom.get("chan") else 0


if __name__ == "__main__":
    sys.exit(main())
