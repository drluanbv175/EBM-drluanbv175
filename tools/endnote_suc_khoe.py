#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""endnote_suc_khoe.py — SỨC KHOẺ thư viện EndNote và tra cứu CHỈ-ĐỌC trên cơ sở dữ liệu của nó (19/10/2026).

Bác sĩ 19/10/2026: «Hãy làm tất cả 6 việc giúp tôi» (kết nối EndNote ↔ Claude thông suốt). Mô-đun này là nền dùng chung cho
máy chủ MCP `tools/mcp/endnote_ebm_mcp.py`, nút `Chuyen Nhom Vao Thung Rac.command` và giác quan EndNote của hòm việc.

Nguyên tắc:
  • Đọc `<thư viện>.Data/sdb/sdb.eni` ở chế độ `mode=ro` (đọc được khi EndNote đang mở) — KHÔNG BAO GIỜ ghi tệp này.
  • Không gửi sự kiện AppleScript nào ở đây (không khởi động EndNote, không chiếm giao diện bác sĩ).
  • «Không đo được» ⇒ trả lý do, không bao giờ coi là «ổn».

Đo 19/10/2026 (bản sao thư viện): bảng `refs` (id, trash_state, title, year, accession_number,
electronic_resource_number…), `file_res` (refs_id, file_path) — mỗi hàng là một tệp đính kèm. Thư viện bác sĩ nằm ở
OneDrive/EndNote/ theo lựa chọn của bác sĩ (19/10/2026) ⇒ phải canh BẢN SAO XUNG ĐỘT của OneDrive và tệp bị OneDrive đẩy
lên mây (dataless) — hai rủi ro Clarivate cảnh báo cho thư viện đặt trong thư mục đồng bộ.

Chạy tay: `python3 tools/endnote_suc_khoe.py [--json]` — in tình trạng; mã 0 ổn · 1 có cảnh báo · 2 không đo được.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

CAU_HINH = Path.home() / ".ebm-endnote.json"
SF_DATALESS = 0x40000000  # cờ macOS: tệp chỉ còn trên mây (File Provider đã đẩy đi), mở ra mới tải về
TIEN_TO_NHOM_THUNG_RAC = "_Cho thung rac"
# Bản sao xung đột của OneDrive/iCloud: «Tên 2.enl», «Tên (1).enl», «Tên-<tên máy>.enl», «Tên (conflicted copy …).enl».
_XUNG_DOT = r"(?: \d+| \(\d+\)|-[A-Za-z0-9][A-Za-z0-9 ._'’-]*| \(conflicted copy[^)]*\))"


def thu_vien_cau_hinh(tep: Path | None = None) -> Path | None:
    """Đường dẫn `.enl` khai ở ~/.ebm-endnote.json (chưa khai / hỏng ⇒ None)."""
    try:
        d = json.loads((tep or CAU_HINH).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    tv = d.get("thu_vien") if isinstance(d, dict) else None
    return Path(tv) if isinstance(tv, str) and tv.endswith(".enl") else None


def sdb(thu_vien: Path) -> Path:
    return thu_vien.with_suffix(".Data") / "sdb" / "sdb.eni"


def _ket_noi(thu_vien: Path) -> sqlite3.Connection:
    p = sdb(thu_vien)
    if not p.is_file():
        raise OSError(f"không thấy cơ sở dữ liệu {p}")
    return sqlite3.connect(p.resolve().as_uri() + "?mode=ro", uri=True)


def vi_tri_dong_bo(thu_vien: Path, nha: Path | None = None) -> str | None:
    """Tên dịch vụ đồng bộ đám mây chứa thư viện («OneDrive», «iCloud», «Dropbox», «Google Drive») hoặc None.

    iCloud «Desktop & Documents» giữ đường dẫn ~/Documents nhưng tệp nằm trong iCloud Drive — đo 19/10/2026 bằng inode trùng
    với `~/Library/Mobile Documents/com~apple~CloudDocs/Documents/<tên>` ⇒ phải so tệp, không chỉ so đường dẫn."""
    nha = nha or Path.home()
    s = str(thu_vien)
    if "/Library/CloudStorage/OneDrive" in s or "\\OneDrive" in s:
        return "OneDrive"
    if "/Library/Mobile Documents/" in s:
        return "iCloud"
    if "/Library/CloudStorage/Dropbox" in s or "/Dropbox/" in s:
        return "Dropbox"
    if "/Library/CloudStorage/GoogleDrive" in s:
        return "Google Drive"
    try:
        rel = thu_vien.resolve().relative_to((nha / "Documents").resolve())
        ban_icloud = nha / "Library" / "Mobile Documents" / "com~apple~CloudDocs" / "Documents" / rel
        if ban_icloud.exists() and os.path.samefile(ban_icloud, thu_vien):
            return "iCloud"
    except (ValueError, OSError):
        pass
    return None


def ban_sao_xung_dot(thu_vien: Path) -> list[Path]:
    """Bản sao xung đột đồng bộ của thư viện (cạnh `.enl`) và của cơ sở dữ liệu (trong `.Data/sdb`)."""
    ra: list[Path] = []
    goc = thu_vien.parent
    mau_enl = re.compile("^" + re.escape(thu_vien.stem) + _XUNG_DOT + r"\.(enl|Data)$")
    mau_sdb = re.compile(r"^(sdb|pdb)" + _XUNG_DOT + r"\.eni$")
    try:
        ra += sorted(p for p in goc.iterdir() if mau_enl.match(p.name))
    except OSError:
        pass
    try:
        ra += sorted(p for p in sdb(thu_vien).parent.iterdir() if mau_sdb.match(p.name))
    except OSError:
        pass
    return ra


def tep_chua_tai(thu_vien: Path, gioi_han: int = 20000) -> int | None:
    """Số tệp của thư viện mà dịch vụ đồng bộ đã đẩy lên mây (cờ dataless) — None nếu không đo được (không phải macOS)."""
    if not hasattr(os.stat_result, "st_flags"):
        return None
    dem = 0
    tep = [thu_vien] + [p for p in thu_vien.with_suffix(".Data").rglob("*") if p.is_file()][:gioi_han]
    for p in tep:
        try:
            if os.lstat(p).st_flags & SF_DATALESS:
                dem += 1
        except OSError:
            continue
    return dem


def dem_ban_ghi(thu_vien: Path) -> dict:
    """{"trong_thu_vien", "thung_rac", "co_tep"} đếm trên cơ sở dữ liệu (mode=ro)."""
    kn = _ket_noi(thu_vien)
    try:
        song = kn.execute("SELECT count(*) FROM refs WHERE trash_state = 0").fetchone()[0]
        rac = kn.execute("SELECT count(*) FROM refs WHERE trash_state <> 0").fetchone()[0]
        co_tep = kn.execute("SELECT count(DISTINCT f.refs_id) FROM file_res f JOIN refs r ON r.id = f.refs_id "
                            "WHERE r.trash_state = 0").fetchone()[0]
    finally:
        kn.close()
    return {"trong_thu_vien": song, "thung_rac": rac, "co_tep": co_tep}


def _chuan_doi(doi: str) -> str:
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", (doi or "").strip(), flags=re.I).lower()


def tra_dinh_danh(thu_vien: Path, dinh_danh: list[str]) -> dict[str, list[dict]]:
    """{PMID|DOI: [{rec, tieu_de, nam, thung_rac, so_tep}]} — tra trên cơ sở dữ liệu, không qua giao diện EndNote."""
    kn = _ket_noi(thu_vien)
    ra: dict[str, list[dict]] = {}
    try:
        for dd in dinh_danh:
            dd = (dd or "").strip()
            if not dd:
                continue
            if re.fullmatch(r"\d{1,9}", dd):
                dong = kn.execute("SELECT id, title, year, trash_state FROM refs WHERE trim(accession_number) = ?", (dd,))
            else:
                dong = kn.execute("SELECT id, title, year, trash_state FROM refs WHERE lower(trim(electronic_resource_number)) "
                                  "IN (?, ?)", (_chuan_doi(dd), "https://doi.org/" + _chuan_doi(dd)))
            ra[dd] = [{"rec": i, "tieu_de": (t or "")[:200], "nam": y or "", "thung_rac": bool(tr),
                       "so_tep": kn.execute("SELECT count(*) FROM file_res WHERE refs_id = ?", (i,)).fetchone()[0]}
                      for i, t, y, tr in dong.fetchall()]
    finally:
        kn.close()
    return ra


def so_rec(ma: str) -> int | None:
    """`<RecordID database="1" recNum="7327" />` hoặc «7327» → 7327."""
    m = re.search(r'recNum="(\d+)"', ma or "") or re.fullmatch(r"\s*(\d+)\s*", ma or "")
    return int(m.group(1)) if m else None


def kiem_thung_rac(thu_vien: Path, rec: list[int]) -> dict[str, list[int]]:
    """Bản ghi nào đã vào THÙNG RÁC (trash_state <> 0), còn ở thư viện, hay không còn hàng (đã bị xoá hẳn)."""
    kn = _ket_noi(thu_vien)
    ra: dict[str, list[int]] = {"da_vao_thung_rac": [], "con_o_thu_vien": [], "khong_con_hang": []}
    try:
        for r in rec:
            h = kn.execute("SELECT trash_state FROM refs WHERE id = ?", (r,)).fetchone()
            ra["khong_con_hang" if h is None else ("da_vao_thung_rac" if h[0] else "con_o_thu_vien")].append(r)
    finally:
        kn.close()
    return ra


def giai_thanh_vien(blob: bytes) -> list[int]:
    """Giải cột `groups.members`: 4 byte phiên bản (00 00 00 02) + số lượng (uint32 little-endian) + từng recNum (uint32 LE).

    Đo 19/10/2026 trên thư viện thật: nhóm 4 bản ghi = `00000002 04000000 89190000 8a190000 …` (recNum 6537, 6538…). Khuôn lạ
    (thiếu byte, số lượng không khớp độ dài) ⇒ ValueError — người gọi báo KHÔNG ĐO ĐƯỢC, không coi là nhóm rỗng."""
    b = bytes(blob or b"")
    if len(b) < 8:
        raise ValueError("members quá ngắn")
    n = int.from_bytes(b[4:8], "little")
    if len(b) != 8 + 4 * n:
        raise ValueError(f"members: số lượng {n} không khớp độ dài {len(b)}")
    return [int.from_bytes(b[8 + 4 * i:12 + 4 * i], "little") for i in range(n)]


def nhom_trong_csdl(thu_vien: Path) -> list[tuple[str, list[int]]]:
    """[(tên nhóm, [recNum])] của mọi nhóm thường (đọc `groups`, mode=ro). Tên trùng thì trả từng nhóm riêng."""
    kn = _ket_noi(thu_vien)
    try:
        dong = kn.execute("SELECT spec, members FROM groups").fetchall()
    finally:
        kn.close()
    ra = []
    for spec, mem in dong:
        s = spec.decode("utf-8", "replace") if isinstance(spec, (bytes, bytearray)) else str(spec or "")
        m = re.search(r"<name>(.*?)</name>", s, re.S)
        if not m or mem is None:
            continue
        ten = m.group(1).replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
        ra.append((ten, giai_thanh_vien(mem)))
    return ra


def nhom_cho_thung_rac(thu_vien: Path) -> list[dict]:
    """Nhóm «_Cho thung rac…» gộp theo tên: số bản ghi CÒN ở thư viện (chưa vào thùng rác) — chỉ đọc cơ sở dữ liệu."""
    gop: dict[str, set[int]] = {}
    so_nhom: dict[str, int] = {}
    for ten, rec in nhom_trong_csdl(thu_vien):
        if ten.startswith(TIEN_TO_NHOM_THUNG_RAC):
            gop.setdefault(ten, set()).update(rec)
            so_nhom[ten] = so_nhom.get(ten, 0) + 1
    ra = []
    for ten, rec in gop.items():
        tt = kiem_thung_rac(thu_vien, sorted(rec))
        ra.append({"ten": ten, "so_nhom_cung_ten": so_nhom[ten], "tong": len(rec), "con_o_thu_vien": len(tt["con_o_thu_vien"])})
    return ra


def tinh_trang(thu_vien: Path | None = None) -> dict:
    """Tình trạng tổng hợp (không gửi AppleScript). Khoá `canh_bao` liệt kê việc cần bác sĩ để ý."""
    thu_vien = thu_vien or thu_vien_cau_hinh()
    if thu_vien is None:
        return {"do_duoc": False, "ly_do": f"chưa khai thư viện ở {CAU_HINH}"}
    kq: dict = {"do_duoc": True, "thu_vien": str(thu_vien), "dong_bo": vi_tri_dong_bo(thu_vien), "canh_bao": []}
    if not thu_vien.is_file():
        return {"do_duoc": False, "ly_do": f"không thấy tệp thư viện {thu_vien}", "thu_vien": str(thu_vien)}
    xd = ban_sao_xung_dot(thu_vien)
    kq["ban_sao_xung_dot"] = [str(p) for p in xd]
    if xd:
        kq["canh_bao"].append(f"{len(xd)} bản sao xung đột đồng bộ của thư viện — đóng EndNote trên MỌI máy, giữ bản mới nhất, "
                              "dời bản thừa ra ngoài (không xoá vội)")
    kq["tep_chua_tai"] = tep_chua_tai(thu_vien)
    if kq["tep_chua_tai"]:
        kq["canh_bao"].append(f"{kq['tep_chua_tai']} tệp của thư viện chỉ còn trên mây — Finder: chuột phải thư mục EndNote → "
                              "«Always Keep on This Device»")
    if kq["dong_bo"] == "iCloud":
        kq["canh_bao"].append("thư viện nằm trong iCloud Drive — bác sĩ đã chọn OneDrive (19/10/2026); kiểm lại "
                              "`~/.ebm-endnote.json`")
    try:
        kq["dem"] = dem_ban_ghi(thu_vien)
    except (OSError, sqlite3.Error) as e:
        kq["dem"] = None
        kq["canh_bao"].append(f"không đọc được cơ sở dữ liệu: {type(e).__name__}")
    try:
        kq["nhom_cho_thung_rac"] = [n for n in nhom_cho_thung_rac(thu_vien) if n["con_o_thu_vien"]]
    except (OSError, sqlite3.Error, ValueError) as e:
        kq["nhom_cho_thung_rac"] = None
        kq["canh_bao"].append(f"không đọc được nhóm chờ thùng rác: {type(e).__name__}")
    return kq


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Sức khoẻ thư viện EndNote (chỉ đọc)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    kq = tinh_trang()
    if a.json:
        print(json.dumps(kq, ensure_ascii=False, indent=1))
    elif not kq.get("do_duoc"):
        print(f"⚪ KHÔNG ĐO ĐƯỢC — {kq.get('ly_do')}")
    else:
        dem = kq.get("dem") or {}
        print(f"Thư viện: {kq['thu_vien']}" + (f" (đồng bộ: {kq['dong_bo']})" if kq["dong_bo"] else ""))
        if dem:
            print(f"  {dem['trong_thu_vien']} bản ghi · {dem['co_tep']} có tệp đính kèm · {dem['thung_rac']} trong thùng rác")
        for c in kq["canh_bao"]:
            print(f"  🟠 {c}")
        for n in kq.get("nhom_cho_thung_rac") or []:
            print(f"  👤 nhóm «{n['ten']}» còn {n['con_o_thu_vien']}/{n['tong']} bản ghi chờ bác sĩ chuyển vào thùng rác — "
                  "bấm đúp «Chuyen Nhom Vao Thung Rac.command»")
        if not kq["canh_bao"]:
            print("  🟢 không có bản sao xung đột, không có tệp chỉ còn trên mây")
    if not kq.get("do_duoc"):
        return 2
    return 1 if kq["canh_bao"] else 0


if __name__ == "__main__":
    sys.exit(main())
