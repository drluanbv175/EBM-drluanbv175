#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""endnote_ebm_mcp.py — Máy chủ MCP «endnote-ebm»: một cửa an toàn giữa EndNote và MỌI nơi dùng Claude trên Mac (19/10/2026).

Bác sĩ 19/10/2026: «Có giải pháp nào giúp cho sự kết nối giữa Endnote và Claude được thông suốt…» → «Hãy làm tất cả 6 việc
giúp tôi» (việc 3). Claude Code (qua `.mcp.json`), Claude Desktop/khung chat (qua `--cai-claude-desktop`) gọi CÙNG các công cụ
đã đo của `tools/nap_endnote_chu_de.py` và `tools/endnote_suc_khoe.py`, với cùng rào chắn:

  • ĐỌC qua cơ sở dữ liệu `sdb.eni` ở chế độ chỉ-đọc (nhanh, không chiếm giao diện EndNote của bác sĩ).
  • GHI chỉ qua lớp `EndNoteMac` (đi qua KHOÁ GHI `tools/khoa_ghi_endnote.py`), mọi công cụ ghi CHẠY KHÔ mặc định —
    `ap_dung: true` mới ghi. Máy chủ sống CẢ PHIÊN Claude ⇒ mỗi lời gọi công cụ là MỘT phạm vi khoá (`giu_khoa_ghi`): khoá lấy
    trong lời gọi được nhả ngay khi công cụ trả về (24/10/2026 — khoá giữ theo tiến trình từng chặn bộ năm bước ⑧ tới 15 phút).
  • KHÔNG có công cụ xoá: không `delete record` (đo 19/10/2026: xoá HẲN), không thùng rác tự động, không `close document`
    (làm EndNote sập). Thùng rác: công cụ chỉ CHUẨN BỊ (hiện đúng bản ghi) và KIỂM — bác sĩ bấm.
  • `endnote_loai_tru` chỉ dùng khi BÁC SĨ đã nói loại bài đó; `ly_do` phải là lời bác sĩ.
  • NHÓM đo theo group_id trên bản sao tạm của `sdb.eni` (21/10/2026), không theo TÊN qua AppleScript — `get records in "<tên>"`
    trả HỢP mọi nhóm cùng tên (2 nhóm 5 + 4 bài từng bị báo thành «1 nhóm 9 bài», tưởng đã gộp). `endnote_dua_vao_nhom` TỪ CHỐI
    ghi khi tên đích đang có ≥2 nhóm hoặc không đo được; tên đích đã có MỘT nhóm ⇒ KHÔNG post (đo 24/10/2026: post vào tên đã
    có LUÔN sinh nhóm mới cùng tên) — bản ghi thiếu vào hàng chờ đưa vào nhóm cho bác sĩ kéo tay.

Giao thức: MCP qua stdio — JSON-RPC 2.0, mỗi thông điệp một dòng. Chỉ dùng thư viện chuẩn (chạy được bằng `python3` hệ thống
hay `uv run`). stdout là KÊNH GIAO THỨC: mọi dòng chữ khác đi stderr.

Cài cho Claude Desktop (khung chat): `python3 tools/mcp/endnote_ebm_mcp.py --cai-claude-desktop` (chạy khô) → `--ap-dung`
(sao lưu tệp cấu hình trước khi ghi, chỉ thêm/cập nhật đúng khoá `endnote-ebm`).
"""
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import json
import os
import shutil
import sqlite3
import sys
import traceback
from datetime import datetime
from pathlib import Path

for _s in (sys.stdin, sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

TOOLS = Path(__file__).resolve().parents[1]
TEN_MAY_CHU = "endnote-ebm"
PHIEN_BAN = "1.2.0"
NGUON_NHOM = "sdb.eni (bản sao tạm, chỉ đọc) — mỗi nhóm theo group_id, tên trùng KHÔNG cộng thành viên"
GIAO_THUC = ("2025-06-18", "2025-03-26", "2024-11-05")


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, TOOLS / tep)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


_MOD: dict = {}


def mod(ten: str):
    if ten not in _MOD:
        _MOD[ten] = _nap(f"_mcp_{ten}", {"sk": "endnote_suc_khoe.py", "nec": "nap_endnote_chu_de.py"}[ten])
    return _MOD[ten]


def _khoa_ghi():
    """CHÍNH bản mô-đun khoá ghi mà `EndNoteMac` dùng (`nap_endnote_chu_de.nap_khoa_ghi`) — None khi không nạp được. Bản nạp
    riêng sẽ có trạng thái khoá riêng: phạm vi mở trên đó không thấy (và không nhả) khoá do lệnh ghi lấy."""
    try:
        return mod("nec").nap_khoa_ghi()
    except Exception as e:  # noqa: BLE001 — cây hỏng thì công cụ đọc vẫn chạy; lệnh ghi tự báo lỗi của nó
        print(f"⚠ không nạp được khoá ghi EndNote ({type(e).__name__}: {str(e)[:120]})", file=sys.stderr)
        return None


def pham_vi_cong_cu():
    """Phạm vi khoá cho MỘT lời gọi công cụ: khoá lấy bên trong được nhả khi công cụ trả về, kể cả khi lỗi."""
    kg = _khoa_ghi()
    return kg.giu_khoa_ghi() if kg else contextlib.nullcontext()


def _endnote():
    """(EndNoteMac, thư viện) — thư viện phải đang MỞ (công cụ không tự bật EndNote)."""
    nec = mod("nec")
    ch = nec.doc_cau_hinh()
    if not ch:
        raise RuntimeError("chưa khai thư viện EndNote (~/.ebm-endnote.json)")
    en = nec.EndNoteMac(ch["ung_dung"], Path(ch["thu_vien"]))
    if not en.dang_mo_dung_thu_vien():
        raise RuntimeError(f"EndNote chưa mở thư viện {Path(ch['thu_vien']).name} — bác sĩ mở EndNote rồi gọi lại")
    return en, Path(ch["thu_vien"])


def _thu_vien() -> Path:
    tv = mod("sk").thu_vien_cau_hinh()
    if tv is None:
        raise RuntimeError("chưa khai thư viện EndNote (~/.ebm-endnote.json)")
    return tv


# ─────────────────────────── công cụ ───────────────────────────

def cc_trang_thai(_a: dict) -> dict:
    kq = mod("sk").tinh_trang()
    try:
        en, _tv = _endnote()
        kq["endnote_dang_mo"] = True
        kq["nhom_cho_thung_rac"] = [n for n in dict.fromkeys(en.ten_cac_nhom()) if n.startswith(mod("sk").TIEN_TO_NHOM_THUNG_RAC)]
    except Exception as e:  # noqa: BLE001 — báo lý do, không coi là lỗi máy chủ
        kq["endnote_dang_mo"] = False
        kq["ly_do_chua_mo"] = str(e)[:200]
    kg = _khoa_ghi()
    kq["khoa_ghi"] = kg.doc_khoa() if kg else "không nạp được mô-đun khoá ghi"
    return kq


def cc_tim(a: dict) -> dict:
    dd = [str(x) for x in (a.get("dinh_danh") or [])][:200]
    if not dd:
        raise ValueError("cần `dinh_danh`: danh sách PMID hoặc DOI")
    return mod("sk").tra_dinh_danh(_thu_vien(), dd)


class NhomTrungTen(RuntimeError):
    """Tên nhóm đích đang có ≥2 nhóm — không ghi (fail-closed)."""


class KhongDoDuocNhom(RuntimeError):
    """Không đọc được bảng nhóm trong sdb.eni — không ghi (fail-closed)."""


def _mo_ta_trung(ten: str, nh: list[dict]) -> str:
    ds = ", ".join(f"group_id {n['group_id']}: {n['so_ban_ghi']} bài" for n in nh)
    return (f"«{ten}» đang có {len(nh)} nhóm RIÊNG ({ds}) — CHƯA gộp. Đếm theo TÊN (AppleScript `get records in`) trả HỢP "
            "nên sai. Gộp chắc nhất: bác sĩ xoá HẾT các nhóm cùng tên trong EndNote (bài không mất), máy đăng lại toàn bộ "
            "recNum vào tên đó (tạo đúng MỘT nhóm), rồi đo lại bằng endnote_nhom.")


def _rut_gon_nhom(n: dict, khoa: tuple[str, ...]) -> dict:
    return {**{k: n[k] for k in khoa if k in n}, **({"loi": n["loi"]} if n.get("loi") else {})}


def cc_nhom(a: dict) -> dict:
    """Nhóm đọc từ sdb.eni THEO group_id (bản sao tạm, chỉ đọc; không cần EndNote đang mở). Tên trùng ⇒ từng nhóm riêng + cờ
    `trung_ten` + cảnh báo — không bao giờ cộng thành viên các nhóm cùng tên."""
    sk, tv = mod("sk"), _thu_vien()
    ten = (a.get("ten_nhom") or "").strip()
    if not ten:
        ds = sk.doc_nhom(tv)
        loc = (a.get("loc") or "").strip().casefold()
        if loc:
            ds = [n for n in ds if loc in n["ten"].casefold()]
        trung = sk.nhom_trung_ten(ds)
        khoa_trung = {sk.khoa_ten(t["ten"]) for t in trung}
        kq = {"nguon": NGUON_NHOM, "so_nhom": len(ds),
              "nhom": [{**_rut_gon_nhom(n, ("group_id", "ten", "loai", "so_ban_ghi")),
                        "trung_ten": sk.khoa_ten(n["ten"]) in khoa_trung} for n in ds],
              "nhom_trung_ten": trung}
        if trung:
            kq["canh_bao"] = (f"{len(trung)} tên đang có ≥2 nhóm RIÊNG (cờ trung_ten) — chưa gộp; gọi endnote_nhom với ten_nhom "
                              "để xem từng nhóm")
        return kq
    nh = sk.nhom_theo_ten(tv, ten, chi_tiet=True)
    kq = {"nguon": NGUON_NHOM, "ten_nhom": ten, "so_nhom": len(nh), "trung_ten": len(nh) >= 2,
          "nhom": [_rut_gon_nhom(n, ("group_id", "ten", "loai", "so_ban_ghi", "chua_co_tep", "ban_ghi")) for n in nh]}
    if not nh:
        kq["ghi_chu"] = "không có nhóm nào mang tên này trong sdb.eni"
    elif len(nh) >= 2:
        kq["canh_bao"] = _mo_ta_trung(ten, nh)
    return kq


def cc_gan_pdf_kho(a: dict) -> dict:
    nec = mod("nec")
    en, tv = _endnote()
    kho = nec.xac_dinh_kho(None, nec._tim_dash_goc(), [])
    pm = [str(x) for x in a.get("pmids") or []] or None
    return nec.gan_kho(en, kho, pm, bool(a.get("ap_dung")))


def _nhom_dich(tv: Path, ten: str) -> list[dict]:
    """Các nhóm đang mang tên đích — fail-closed: không đo được hoặc ≥2 nhóm ⇒ ngoại lệ, KHÔNG ghi."""
    try:
        nh = mod("sk").nhom_theo_ten(tv, ten)
    except (OSError, sqlite3.Error) as e:
        raise KhongDoDuocNhom(f"không đọc được nhóm trong sdb.eni ({type(e).__name__}: {str(e)[:120]}) ⇒ KHÔNG ghi: chưa biết "
                              f"«{ten}» đang có mấy nhóm") from e
    if len(nh) >= 2:
        raise NhomTrungTen("TỪ CHỐI ghi — không biết `post` sẽ rơi vào nhóm nào. " + _mo_ta_trung(ten, nh))
    return nh


def _do_sau_khi_dang(tv: Path, ten: str, rec: list[int], id_truoc: set[int]) -> dict:
    """Đo lại sdb.eni sau `post`: nhóm nào nhận bài, có sinh nhóm MỚI cùng tên không (đo 18/10/2026: post vào tên đã có nhóm
    từng tạo nhóm mới thay vì cộng vào). Không đo được ⇒ nói rõ, không coi là thành công."""
    kq: dict = {"da_goi_post": True, "ten_nhom": ten, "yeu_cau": len(rec)}
    try:
        sau = mod("sk").nhom_theo_ten(tv, ten)
    except (OSError, sqlite3.Error) as e:
        kq["canh_bao"] = f"KHÔNG ĐO LẠI được sdb.eni sau khi đăng ({type(e).__name__}) — gọi endnote_nhom để kiểm theo group_id"
        return kq
    can = set(rec)
    kq["nhom_sau"] = [{"group_id": n["group_id"], "so_ban_ghi": n["so_ban_ghi"], "co_ban_ghi_yeu_cau": len(can & set(n["rec"] or []))}
                      for n in sau]
    kq["nhom_moi_tao"] = [n["group_id"] for n in sau if n["group_id"] not in id_truoc]
    if len(sau) >= 2:
        kq["canh_bao"] = "post vừa để lại ≥2 nhóm cùng tên — các lần ghi sau vào tên này sẽ bị từ chối. " + _mo_ta_trung(ten, sau)
    elif not sau:
        kq["canh_bao"] = "chưa thấy nhóm trong sdb.eni sau khi đăng — EndNote có thể chưa ghi xuống đĩa; gọi endnote_nhom đo lại"
    else:
        kq["da_dang"] = kq["nhom_sau"][0]["co_ban_ghi_yeu_cau"]
        if kq["da_dang"] < len(can):
            kq["canh_bao"] = (f"nhóm group_id {sau[0]['group_id']} mới có {kq['da_dang']}/{len(can)} bài yêu cầu — gọi endnote_nhom "
                              "đo lại (EndNote có thể chưa ghi xuống đĩa)")
    return kq


def cc_dua_vao_nhom(a: dict) -> dict:
    ten = (a.get("ten_nhom") or "").strip()
    rec = list(dict.fromkeys(int(x) for x in a.get("rec_nums") or []))
    if not ten or not rec:
        raise ValueError("cần `ten_nhom` và `rec_nums`")
    en, tv = _endnote()
    truoc = _nhom_dich(tv, ten)
    if truoc:  # ĐÃ có một nhóm: post LUÔN sinh nhóm MỚI cùng tên (đo 24/10/2026) ⇒ không post, hàng chờ cho bác sĩ kéo tay
        da_vao = set(truoc[0]["rec"] or [])
        thieu = [r for r in rec if r not in da_vao]
        kq = {"khong_post": True, "ten_nhom": ten,
              "nhom_hien_co": [{"group_id": n["group_id"], "so_ban_ghi": n["so_ban_ghi"]} for n in truoc],
              "da_trong_nhom": len(rec) - len(thieu), "cho_vao_nhom_moi": thieu,
              "ly_do": "post vào tên đã có nhóm LUÔN sinh nhóm MỚI cùng tên, kể cả nhóm vừa tạo cùng phiên (đo 24/10/2026 trên "
                       "bản sao thư viện); EndNote.sdef không có lệnh thêm vào nhóm đã có ⇒ bác sĩ kéo tay"}
        if not a.get("ap_dung"):
            return {**kq, "chay_kho": True, "se_ghi_hang_cho": len(thieu)}
        kq["cho_vao_nhom"] = mod("nec").ghi_cho_vao_nhom(tv, ten, them=thieu, da_vao=da_vao, group_id=[truoc[0]["group_id"]])
        kq["viec_cua_bac_si"] = (f"python3 tools/nap_endnote_chu_de.py --cho-vao-nhom \"{ten}\" (EndNote chỉ hiện các bài chờ) → "
                                 "⌘A → kéo vào nhóm ở cột trái")
        return kq
    csdl = en.so_csdl()
    ids = [f'<RecordID database="{csdl}" recNum="{r}" />' for r in rec]
    if not a.get("ap_dung"):
        return {"chay_kho": True, "se_dang": len(ids), "ten_nhom": ten, "nhom_hien_co": [],
                "luu_y": "chưa có nhóm tên này — post tạo MỘT nhóm mới (đo 21/10 và 24/10/2026)"}
    en.dang_vao_nhom(ids, ten)
    return _do_sau_khi_dang(tv, ten, rec, set())


def cc_loai_tru(a: dict) -> dict:
    dd, ly = (a.get("dinh_danh") or "").strip(), (a.get("ly_do") or "").strip()
    if not dd or not ly:
        raise ValueError("cần `dinh_danh` (PMID/DOI) và `ly_do` (lời bác sĩ)")
    return mod("nec").them_loai_tru(dd, ly, ap_dung=bool(a.get("ap_dung")))


def cc_chuan_bi_thung_rac(a: dict) -> dict:
    ten = (a.get("ten_nhom") or "").strip()
    if not ten.startswith(mod("sk").TIEN_TO_NHOM_THUNG_RAC):
        raise ValueError(f"chỉ nhận nhóm tên bắt đầu «{mod('sk').TIEN_TO_NHOM_THUNG_RAC}» (nhóm Claude gom theo lời bác sĩ)")
    en, _tv = _endnote()
    ids = en.thanh_vien_nhom(ten)
    if not ids:
        return {"ten_nhom": ten, "so_ban_ghi": 0}
    _nap("_mcp_cntr", "chuyen_nhom_vao_thung_rac.py").hien_cho_bac_si(en, ids)
    return {"ten_nhom": ten, "so_ban_ghi": len(ids),
            "viec_cua_bac_si": "Trong EndNote: bấm vào danh sách đang hiện → ⌘A → References → Move References to Trash; "
                               "xong gọi endnote_kiem_thung_rac để kiểm. Công cụ KHÔNG xoá gì."}


def cc_kiem_thung_rac(a: dict) -> dict:
    ten = (a.get("ten_nhom") or "").strip()
    en, tv = _endnote()
    rec = [r for r in (mod("sk").so_rec(x) for x in en.thanh_vien_nhom(ten)) if r is not None]
    tt = mod("sk").kiem_thung_rac(tv, rec)
    return {"ten_nhom": ten, **{k: len(v) for k, v in tt.items()}, "con_o_thu_vien_rec": tt["con_o_thu_vien"][:50]}


def _sc(props: dict, bat_buoc: list[str] | None = None) -> dict:
    return {"type": "object", "properties": props, "required": bat_buoc or [], "additionalProperties": False}


_AP = {"type": "boolean", "description": "true = GHI thật; mặc định chạy khô (chỉ báo sẽ làm gì)"}
CONG_CU = [
    ("endnote_trang_thai", "Tình trạng thư viện EndNote: vị trí (OneDrive), bản sao xung đột, tệp chỉ còn trên mây, số bản ghi/"
     "có tệp/thùng rác, EndNote có đang mở, nhóm chờ thùng rác, NHÓM TRÙNG TÊN (`nhom_trung_ten`: từng group_id + số bài), khoá "
     "ghi. Chỉ đọc.", _sc({}), cc_trang_thai),
    ("endnote_tim", "Tra bản ghi theo PMID hoặc DOI trên cơ sở dữ liệu EndNote (chỉ đọc): recNum, tiêu đề, năm, số tệp đính kèm, "
     "có trong thùng rác không.", _sc({"dinh_danh": {"type": "array", "items": {"type": "string"}}}, ["dinh_danh"]), cc_tim),
    ("endnote_nhom", "Nhóm đọc từ sdb.eni THEO group_id (chỉ đọc, không cần EndNote mở). Không có ten_nhom: liệt kê mọi nhóm "
     "(lọc bằng `loc`) kèm số bài TỪNG nhóm và cờ `trung_ten`. Có ten_nhom: từng nhóm mang tên đó RIÊNG (bản ghi, bản chưa có "
     "tệp); ≥2 nhóm cùng tên ⇒ cảnh báo — KHÔNG cộng thành viên.",
     _sc({"ten_nhom": {"type": "string"}, "loc": {"type": "string"}}), cc_nhom),
    ("endnote_gan_pdf_kho", "Gắn PDF toàn văn có sẵn trong kho EBM (`toan_van_oa/PMID-<n>_*.pdf`) vào bản ghi CHƯA có tệp (khớp "
     "theo PMID). Chạy khô mặc định.",
     _sc({"pmids": {"type": "array", "items": {"type": "string"}}, "ap_dung": _AP}), cc_gan_pdf_kho),
    ("endnote_dua_vao_nhom", "Đăng bản ghi (recNum) vào một nhóm CUSTOM. Chạy khô mặc định. Không xoá, không bỏ khỏi nhóm. CHỈ "
     "post khi tên đích CHƯA có nhóm (tạo đúng một, đo lại theo group_id); nhóm ĐÃ có ⇒ KHÔNG post (post luôn sinh nhóm trùng "
     "tên — đo 24/10/2026), bản ghi thiếu vào hàng chờ cho bác sĩ kéo tay. TỪ CHỐI khi tên đích có ≥2 nhóm hoặc không đọc "
     "được sdb.eni.",
     _sc({"rec_nums": {"type": "array", "items": {"type": "integer"}}, "ten_nhom": {"type": "string"}, "ap_dung": _AP},
         ["rec_nums", "ten_nhom"]), cc_dua_vao_nhom),
    ("endnote_loai_tru", "Thêm PMID/DOI vào danh sách LOẠI TRỪ (không nạp lại vào EndNote). CHỈ khi bác sĩ đã nói loại bài này; "
     "`ly_do` là lời bác sĩ. Chạy khô mặc định; ghi có sao lưu.",
     _sc({"dinh_danh": {"type": "string"}, "ly_do": {"type": "string"}, "ap_dung": _AP}, ["dinh_danh", "ly_do"]), cc_loai_tru),
    ("endnote_chuan_bi_thung_rac", "CHUẨN BỊ chuyển một nhóm «_Cho thung rac…» vào thùng rác: đưa EndNote lên trước và chỉ hiện "
     "đúng các bản ghi đó. KHÔNG xoá gì — bác sĩ tự bấm Move References to Trash.",
     _sc({"ten_nhom": {"type": "string"}}, ["ten_nhom"]), cc_chuan_bi_thung_rac),
    ("endnote_kiem_thung_rac", "Kiểm (chỉ đọc) các bản ghi của một nhóm đã vào thùng rác chưa.",
     _sc({"ten_nhom": {"type": "string"}}, ["ten_nhom"]), cc_kiem_thung_rac),
]
_BANG = {ten: ham for ten, _mt, _sc_, ham in CONG_CU}


# ─────────────────────────── giao thức ───────────────────────────

def xu_ly(tin: dict) -> dict | None:
    """Một thông điệp JSON-RPC → phản hồi (None cho thông báo không cần trả lời)."""
    pt, ma = tin.get("method"), tin.get("id")
    if ma is None:  # thông báo (notifications/initialized, notifications/cancelled…)
        return None
    if pt == "initialize":
        ban = (tin.get("params") or {}).get("protocolVersion")
        kq = {"protocolVersion": ban if ban in GIAO_THUC else GIAO_THUC[0], "capabilities": {"tools": {"listChanged": False}},
              "serverInfo": {"name": TEN_MAY_CHU, "version": PHIEN_BAN},
              "instructions": "EndNote của bác sĩ: đọc an toàn, ghi chạy khô mặc định, KHÔNG có công cụ xoá. Trả lời bác sĩ bằng "
                              "tiếng Việt; thao tác thùng rác do bác sĩ bấm."}
    elif pt == "ping":
        kq = {}
    elif pt == "tools/list":
        kq = {"tools": [{"name": t, "description": mt, "inputSchema": sc} for t, mt, sc, _h in CONG_CU]}
    elif pt == "tools/call":
        p = tin.get("params") or {}
        ham = _BANG.get(p.get("name"))
        if ham is None:
            return {"jsonrpc": "2.0", "id": ma, "result": {"isError": True, "content": [
                {"type": "text", "text": f"không có công cụ «{p.get('name')}» (máy chủ không có công cụ xoá)"}]}}
        try:
            with pham_vi_cong_cu():
                ra = ham(p.get("arguments") or {})
            kq = {"content": [{"type": "text", "text": json.dumps(ra, ensure_ascii=False, indent=1, default=str)}], "isError": False}
        except Exception as e:  # noqa: BLE001 — lỗi công cụ trả về như kết quả lỗi, máy chủ sống tiếp
            print(traceback.format_exc(), file=sys.stderr)
            kq = {"content": [{"type": "text", "text": f"{type(e).__name__}: {e}"[:800]}], "isError": True}
    else:
        return {"jsonrpc": "2.0", "id": ma, "error": {"code": -32601, "message": f"không hỗ trợ phương thức {pt}"}}
    return {"jsonrpc": "2.0", "id": ma, "result": kq}


def chay(vao=sys.stdin, ra=sys.stdout) -> None:
    for dong in vao:
        dong = dong.strip()
        if not dong:
            continue
        try:
            tin = json.loads(dong)
        except ValueError:
            ra.write(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "JSON hỏng"}}) + "\n")
            ra.flush()
            continue
        for t in (tin if isinstance(tin, list) else [tin]):
            tl = xu_ly(t) if isinstance(t, dict) else None
            if tl is not None:
                ra.write(json.dumps(tl, ensure_ascii=False) + "\n")
                ra.flush()


# ─────────────────────────── cài cho Claude Desktop ───────────────────────────

def tep_cau_hinh_desktop() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    return Path(os.environ.get("APPDATA", Path.home())) / "Claude" / "claude_desktop_config.json"


def cai_claude_desktop(ap_dung: bool, tep: Path | None = None) -> dict:
    """Thêm/cập nhật ĐÚNG khoá `mcpServers.endnote-ebm` (giữ nguyên mọi khoá khác), sao lưu trước khi ghi."""
    tep = tep or tep_cau_hinh_desktop()
    cu: dict = {}
    if tep.exists():
        cu = json.loads(tep.read_text(encoding="utf-8"))
        if not isinstance(cu, dict):
            raise ValueError(f"{tep} không phải đối tượng JSON — không ghi")
    muc = {"command": sys.executable, "args": [str(Path(__file__).resolve())]}
    may_chu = dict(cu.get("mcpServers") or {})
    da_co = may_chu.get(TEN_MAY_CHU)
    may_chu[TEN_MAY_CHU] = muc
    moi = {**cu, "mcpServers": may_chu}
    kq = {"tep": str(tep), "da_co": da_co, "se_ghi": muc, "khong_doi": da_co == muc}
    if ap_dung and da_co != muc:
        tep.parent.mkdir(parents=True, exist_ok=True)
        if tep.exists():
            sao = tep.with_name(f"{tep.name}.sao-luu-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
            shutil.copy2(tep, sao)
            kq["sao_luu"] = str(sao)
        tep.write_text(json.dumps(moi, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        kq["da_ghi"] = True
    return kq


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Máy chủ MCP endnote-ebm (stdio)")
    ap.add_argument("--cai-claude-desktop", action="store_true", help="khai máy chủ này cho Claude Desktop (chạy khô)")
    ap.add_argument("--ap-dung", action="store_true")
    ap.add_argument("--liet-ke", action="store_true", help="in danh sách công cụ rồi thoát")
    a = ap.parse_args(argv)
    if a.cai_claude_desktop:
        print(json.dumps(cai_claude_desktop(a.ap_dung), ensure_ascii=False, indent=1), file=sys.stderr)
        return 0
    if a.liet_ke:
        for t, mt, _sc_, _h in CONG_CU:
            print(f"{t}: {mt}", file=sys.stderr)
        return 0
    chay()
    return 0


if __name__ == "__main__":
    sys.exit(main())
