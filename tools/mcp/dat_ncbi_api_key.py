#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dat_ncbi_api_key.py — Đặt NCBI API key vào kho secrets và KIỂM CHỨNG NGAY bằng lời gọi thật.

Vì sao cần: NCBI giới hạn 3 lượt/giây khi không có key, 10 lượt/giây khi có. Tìm hệ
thống (mở rộng MeSH, nhiều truy vấn) rất dễ chạm trần 3 lượt/giây và bị chặn giữa chừng.

Khoá được ghi vào `~/.ebm-secrets/medical-ebm-automation.env` — NGOÀI OneDrive, ngoài
git. Script này KHÔNG BAO GIỜ in giá trị khoá ra màn hình hay log.

LẤY KHOÁ Ở ĐÂU (phải tự làm, script không đăng nhập thay được):
  1. Đăng nhập <https://account.ncbi.nlm.nih.gov/>
  2. Vào Account Settings → mục "API Key Management"
  3. Bấm "Create an API Key", chép chuỗi hiện ra

Chạy:
  python3 tools/mcp/dat_ncbi_api_key.py            # nhập ẩn, không hiện lên màn hình
  python3 tools/mcp/dat_ncbi_api_key.py --kiem-tra # chỉ kiểm khoá đang có, không đổi gì
"""
from __future__ import annotations

import argparse
import getpass
import pathlib
import re
import sys

KHO = pathlib.Path.home() / ".ebm-secrets" / "medical-ebm-automation.env"
TEN_KHOA = "NCBI_API_KEY"
# Khoá NCBI hiện là 36 ký tự hex thường. Kiểm lỏng để không chặn oan nếu NCBI đổi
# định dạng — chỉ CẢNH BÁO, không từ chối.
MAU_KHOA = re.compile(r"^[0-9a-f]{36}$")


def doc_kho() -> dict[str, str]:
    if not KHO.exists():
        return {}
    ket_qua: dict[str, str] = {}
    for dong in KHO.read_text("utf-8", errors="replace").splitlines():
        d = dong.strip()
        if d and not d.startswith("#") and "=" in d:
            t, _, g = d.partition("=")
            ket_qua[t.strip()] = g.strip().strip('"').strip("'")
    return ket_qua


def ghi_khoa(gia_tri: str) -> None:
    """Cập nhật đúng một dòng, giữ nguyên mọi dòng khác và thứ tự file."""
    KHO.parent.mkdir(parents=True, exist_ok=True)
    dong_cu = KHO.read_text("utf-8", errors="replace").splitlines() if KHO.exists() else []
    da_thay = False
    dong_moi = []
    for d in dong_cu:
        if d.strip().startswith(f"{TEN_KHOA}="):
            dong_moi.append(f"{TEN_KHOA}={gia_tri}")
            da_thay = True
        else:
            dong_moi.append(d)
    if not da_thay:
        dong_moi.append(f"{TEN_KHOA}={gia_tri}")
    KHO.write_text("\n".join(dong_moi) + "\n", encoding="utf-8")
    try:
        KHO.chmod(0o600)  # chỉ chủ sở hữu đọc được
    except OSError:
        pass


def kiem_chung(khoa: str, email: str) -> bool:
    """Gọi NCBI THẬT để xác nhận khoá dùng được. Dùng httpx (mang certifi riêng) vì
    urllib trên Python 3.14 bản python.org thiếu chứng chỉ CA."""
    try:
        import httpx
    except ImportError:
        print("  ! không có httpx trong môi trường này — bỏ qua bước kiểm chứng.\n"
              "    Chạy lại trong venv có httpx để kiểm thật:  ~/.pubmed-mcp-venv/bin/python "
              "tools/mcp/dat_ncbi_api_key.py --kiem-tra", file=sys.stderr)
        return False
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    tham_so = {"db": "pubmed", "term": "metformin", "retmax": 1, "retmode": "json",
               "tool": "ebm-copilot", "email": email or ""}
    try:
        r_khong = httpx.get(url, params=tham_so, timeout=30)
        r_co = httpx.get(url, params={**tham_so, "api_key": khoa}, timeout=30)
    except Exception as loi:  # noqa: BLE001 — báo nguyên nhân cho người dùng, không nuốt
        print(f"  ✗ không gọi được NCBI: {type(loi).__name__}: {loi}"[:200])
        return False

    if r_co.status_code == 200:
        n = len(r_co.json().get("esearchresult", {}).get("idlist", []))
        print(f"  ✓ NCBI chấp nhận khoá — HTTP 200, trả {n} kết quả (hạn mức 10 lượt/giây)")
        return True
    if r_co.status_code in (401, 403):
        print(f"  ✗ NCBI TỪ CHỐI khoá (HTTP {r_co.status_code}) — khoá sai hoặc đã bị thu hồi.")
        print(f"    (gọi KHÔNG kèm khoá thì HTTP {r_khong.status_code} → mạng vẫn thông)")
        return False
    print(f"  ? NCBI trả HTTP {r_co.status_code} — chưa kết luận được, thử lại sau.")
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description="Đặt và kiểm chứng NCBI API key")
    ap.add_argument("--kiem-tra", action="store_true",
                    help="chỉ kiểm khoá đang có trong kho, không ghi gì")
    tham_so = ap.parse_args()

    kho = doc_kho()
    email = kho.get("NCBI_EMAIL", "")
    print(f"Kho secrets : {KHO}")
    print(f"NCBI_EMAIL  : {'có' if email else 'THIẾU — NCBI yêu cầu email trong mọi lời gọi'}")

    if tham_so.kiem_tra:
        khoa = kho.get(TEN_KHOA, "")
        if not khoa:
            print(f"{TEN_KHOA}: chưa đặt (đang chạy ở hạn mức 3 lượt/giây)")
            return 2
        print(f"{TEN_KHOA}: đã đặt, {len(khoa)} ký tự — đang kiểm chứng…")
        return 0 if kiem_chung(khoa, email) else 1

    print(f"{TEN_KHOA}  : {'đã có, sẽ GHI ĐÈ' if kho.get(TEN_KHOA) else 'chưa đặt'}")
    print("\nLấy khoá tại https://account.ncbi.nlm.nih.gov/ → Account Settings →")
    print("API Key Management → Create an API Key, rồi dán vào đây.")
    print("(Khoá KHÔNG hiện lên màn hình khi gõ. Bỏ trống rồi Enter để huỷ.)\n")
    try:
        khoa = getpass.getpass("NCBI API key: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nĐã huỷ, không thay đổi gì.")
        return 130
    if not khoa:
        print("Bỏ trống — không thay đổi gì.")
        return 130
    if not MAU_KHOA.match(khoa):
        print(f"  ! khoá dài {len(khoa)} ký tự, không khớp dạng 36 ký tự hex thường mà NCBI "
              "hay cấp. Vẫn ghi, nhưng hãy xem kỹ bước kiểm chứng bên dưới.")

    ghi_khoa(khoa)
    print(f"\n  ✓ đã ghi vào {KHO} (quyền 600, ngoài OneDrive và ngoài git)")
    print("  đang kiểm chứng bằng lời gọi thật tới NCBI…")
    ok = kiem_chung(khoa, email)
    print("\nBước cuối: mở lại phiên Claude Code để MCP pubmed-search nhận khoá mới.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
