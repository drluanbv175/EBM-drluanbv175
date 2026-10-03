#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CHỐT BÍ MẬT / PII TRƯỚC COMMIT — quét dòng THÊM MỚI trong phần đã stage (AN-06, kiểm toàn diện 02/10/2026).

VÌ SAO CÓ. Pre-commit hai repo gọi 9 công cụ mà 0 công cụ quét bí mật/PII; GitHub chỉ chặn mẫu của nhà cung cấp khi push (mẫu tuỳ chỉnh
tắt). Repo CÔNG KHAI, sắp có khoá Ed25519 thật và dữ liệu khảo sát — một tệp khoá lạc vào `config/gate_ed25519_pubkeys/` (thư mục vốn
để commit) sẽ được stage mà không ai báo.

    python3 tools/kiem_bi_mat_truoc_commit.py            # pre-commit: quét phần đã stage (dòng thêm + tên tệp)
    python3 tools/kiem_bi_mat_truoc_commit.py --tat-ca   # quét MỌI tệp đã track (đo hiện trạng, chỉ đọc)

CHẶN (mã 1): khối PRIVATE KEY · token dạng nhà cung cấp (Anthropic/OpenAI `sk-…`, GitHub `ghp_/github_pat_`, Slack `xox…`, AWS `AKIA…`,
Google `AIza…`) · URL kèm user:mật-khẩu · TỆP khoá (`.pem/.key/.p12/.pfx`, `id_rsa*`, `.env` thật, `gate_approval_key_*`, tệp không
phải `.pub` trong `config/gate_ed25519_pubkeys/`). CẢNH BÁO (không chặn — mẫu dễ báo oan, đo 02/10: 88 số 12 chữ là mảnh băm/ID):
gán `api_key/password/secret/token = <giá trị dài>`, số điện thoại VN, số 12 chữ (CCCD?), email cá nhân.
KHÔNG BAO GIỜ in giá trị khớp — chỉ «tệp:dòng · loại». Miễn trừ một dòng: thêm chú thích `bimat-mien: <lý do>` trên CHÍNH dòng đó
(vd khoá giả trong test). Không dùng `--no-verify` để vòng. Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parent.parent
MIEN = re.compile(r"bimat-mien:\s*\S")

CHAN: dict[str, re.Pattern] = {
    "khối PRIVATE KEY": re.compile(r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----"),
    "token Anthropic/OpenAI (sk-…)": re.compile(r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{24,}"),
    "token GitHub": re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}|\bgithub_pat_[A-Za-z0-9_]{30,}"),
    "token Slack (xox…)": re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"),
    "khoá AWS (AKIA…)": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "khoá Google (AIza…)": re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
    "URL kèm user:mật-khẩu": re.compile(r"[a-z][a-z0-9+.-]*://[^/\s:@'\"]+:[^/\s:@'\"]{4,}@[^\s'\"]+", re.I),
}
# URL kèm mật khẩu tới máy chủ CỤC BỘ / dịch vụ docker một nhãn / miền thử ⇒ chuỗi mẫu cho môi trường dev (đo 03/10: 7/7 chỗ ở repo y
# khoa đều thế — `postgres:5432`, `proxy.local`) ⇒ chỉ CẢNH BÁO, không chặn.
_URL_CHU_MAY = re.compile(r"://[^/\s:@'\"]+:[^/\s:@'\"]+@(?P<host>\[[^\]]*\]|[^/\s:'\"?#]+)", re.I)
_MAY_CUC_BO = re.compile(r"^(?:localhost|127\.\d+\.\d+\.\d+|0\.0\.0\.0|\[::1\]|[a-z0-9_-]+|.*\.(?:local|localhost|test|invalid|example|internal))$",
                         re.I)


def _url_mat_khau_cuc_bo(dong: str) -> bool:
    ds = [m.group("host") for m in _URL_CHU_MAY.finditer(dong)]
    return bool(ds) and all(_MAY_CUC_BO.match(h) for h in ds)
CANH_BAO: dict[str, re.Pattern] = {
    "gán khoá/mật khẩu dài": re.compile(r"(?i)\b(?:api[_-]?key|apikey|password|passwd|secret|access[_-]?token|auth[_-]?token)\b"
                                        r"\s*[:=]\s*['\"][A-Za-z0-9_\-./+=]{16,}['\"]"),
    "số điện thoại VN": re.compile(r"(?<![\d.])(?:\+84|0)(?:3[2-9]|5[2689]|7[06-9]|8[1-9]|9\d)\d{7}(?![\d.])"),
    "số 12 chữ (CCCD?)": re.compile(r"(?<![\w.:/-])\d{12}(?![\w.-])"),
    "email cá nhân": re.compile(r"[A-Za-z0-9._%+-]+@(?:gmail|yahoo|hotmail|outlook)\.com", re.I),
}
_TEP_KHOA = re.compile(r"(?:^|/)(?:id_rsa[^/]*|id_ed25519[^/]*|[^/]+\.(?:pem|key|p12|pfx|jks|keystore)|\.env(?:\.[^/]*)?|"
                       r"gate_approval_key_[^/]*)$", re.I)
_TEP_KHOA_MIEN = re.compile(r"(?:^|/)\.env\.(?:example|sample|template|mau)$|\.pub$", re.I)
_NHI_PHAN = re.compile(r"\.(png|jpe?g|gif|webp|pdf|zip|xlsx?|docx?|pptx?|woff2?|ttf|otf|ico|gz|db|sqlite3?|bin|pyc|mp4|mov|mp3)$", re.I)


def tep_khoa(duong: str) -> str | None:
    """Lý do nếu TÊN tệp là tệp khoá/bí mật; None nếu không."""
    if duong.startswith("config/gate_ed25519_pubkeys/") and not duong.endswith((".pub", "README.md", ".gitkeep")):
        return "tệp lạ trong thư mục khoá CÔNG KHAI (chỉ nhận .pub)"
    if _TEP_KHOA.search(duong) and not _TEP_KHOA_MIEN.search(duong):
        return "tên tệp là tệp khoá/bí mật"
    return None


def quet_dong(duong: str, so_dong: int, dong: str) -> tuple[list[tuple[str, int, str]], list[tuple[str, int, str]]]:
    """(chặn, cảnh báo) cho MỘT dòng — mỗi mục (tệp, dòng, loại). Không trả giá trị khớp."""
    if MIEN.search(dong):
        return [], []
    dong = dong[:5000]
    chan = [(duong, so_dong, ten) for ten, m in CHAN.items() if m.search(dong)]
    cb = [(duong, so_dong, ten) for ten, m in CANH_BAO.items() if m.search(dong)]
    if any(t == "URL kèm user:mật-khẩu" for _, _, t in chan) and _url_mat_khau_cuc_bo(dong):
        chan = [x for x in chan if x[2] != "URL kèm user:mật-khẩu"]
        cb.append((duong, so_dong, "URL kèm mật khẩu tới máy CỤC BỘ/dịch vụ docker (chuỗi mẫu dev?)"))
    return chan, cb


def dong_them_da_stage(cwd: Path) -> tuple[list[str], list[tuple[str, int, str]]]:
    """(tệp được thêm/sửa trong phần stage, các dòng THÊM (tệp, số dòng mới, nội dung))."""
    ten = subprocess.run(["git", "-C", str(cwd), "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"],
                         capture_output=True, timeout=60).stdout.decode("utf-8", "replace").split("\0")
    diff = subprocess.run(["git", "-C", str(cwd), "diff", "--cached", "-U0", "--no-color", "--diff-filter=ACMR", "--text"],
                          capture_output=True, timeout=120).stdout.decode("utf-8", "replace")
    dong, tep, so = [], None, 0
    for d in diff.splitlines():
        if d.startswith("+++ "):
            tep = d[6:] if d.startswith("+++ b/") else None
        elif d.startswith("@@"):
            m = re.search(r"\+(\d+)", d)
            so = int(m.group(1)) if m else 0
        elif d.startswith("+") and tep and not _NHI_PHAN.search(tep):
            dong.append((tep, so, d[1:]))
            so += 1
    return [x for x in ten if x], dong


def tat_ca_dong_da_track(cwd: Path) -> tuple[list[str], list[tuple[str, int, str]]]:
    ten = [x for x in subprocess.run(["git", "-C", str(cwd), "ls-files", "-z"], capture_output=True, timeout=60)
           .stdout.decode("utf-8", "replace").split("\0") if x]
    dong = []
    for t in ten:
        if _NHI_PHAN.search(t):
            continue
        try:
            du = (cwd / t).read_bytes()
        except OSError:
            continue
        if b"\0" in du[:4096]:
            continue
        dong += [(t, i, x) for i, x in enumerate(du.decode("utf-8", "replace").split("\n"), 1)]
    return ten, dong


def kiem(ten_tep: list[str], dong: list[tuple[str, int, str]]) -> tuple[list[str], list[str]]:
    chan, cb = [], []
    for t in ten_tep:
        ly = tep_khoa(t)
        if ly:
            chan.append(f"{t} · {ly}")
    for t, so, x in dong:
        c, w = quet_dong(t, so, x)
        chan += [f"{a}:{b} · {c_}" for a, b, c_ in c]
        cb += [f"{a}:{b} · {c_}" for a, b, c_ in w]
    return chan, cb


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Chốt bí mật/PII trước commit (chỉ đọc, không in giá trị khớp)")
    ap.add_argument("--tat-ca", action="store_true", help="quét mọi tệp đã track thay vì phần đã stage")
    ap.add_argument("--repo", type=Path, default=None, help="repo cần quét (mặc định: repo chứa công cụ)")
    a = ap.parse_args(argv)
    cwd = a.repo or REPO
    try:
        ten, dong = tat_ca_dong_da_track(cwd) if a.tat_ca else dong_them_da_stage(cwd)
    except (OSError, subprocess.SubprocessError) as e:
        print(f"⚪ KHÔNG ĐO ĐƯỢC — git lỗi: {type(e).__name__}")
        return 2
    chan, cb = kiem(ten, dong)
    if cb:
        print(f"🟡 {len(cb)} dòng giống PII/khoá (CẢNH BÁO, không chặn) — xem lại trước khi đẩy lên repo công khai:")
        for x in cb[:15]:
            print(f"    {x}")
        if len(cb) > 15:
            print(f"    … và {len(cb) - 15} dòng nữa")
    if chan:
        print(f"🔴 CHẶN: {len(chan)} chỗ giống bí mật THẬT (giá trị không in ra):")
        for x in chan[:20]:
            print(f"    {x}")
        print("   Gỡ khỏi phần stage (git restore --staged <tệp>) và cất khoá vào ~/.ebm-secrets. Khoá GIẢ trong test: thêm chú thích "
              "«bimat-mien: <lý do>» trên đúng dòng đó. KHÔNG dùng --no-verify.")
        return 1
    if not cb:
        print(f"🟢 Không thấy bí mật/PII ({len(dong)} dòng, {len(ten)} tệp).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
