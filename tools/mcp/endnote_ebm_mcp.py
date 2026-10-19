#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""endnote_ebm_mcp.py — Máy chủ MCP «endnote-ebm»: một cửa an toàn giữa EndNote và MỌI nơi dùng Claude trên Mac (19/10/2026).

Bác sĩ 19/10/2026: «Có giải pháp nào giúp cho sự kết nối giữa Endnote và Claude được thông suốt…» → «Hãy làm tất cả 6 việc
giúp tôi» (việc 3). Claude Code (qua `.mcp.json`), Claude Desktop/khung chat (qua `--cai-claude-desktop`) gọi CÙNG các công cụ
đã đo của `tools/nap_endnote_chu_de.py` và `tools/endnote_suc_khoe.py`, với cùng rào chắn:

  • ĐỌC qua cơ sở dữ liệu `sdb.eni` ở chế độ chỉ-đọc (nhanh, không chiếm giao diện EndNote của bác sĩ).
  • GHI chỉ qua lớp `EndNoteMac` (đi qua KHOÁ GHI `tools/khoa_ghi_endnote.py`), mọi công cụ ghi CHẠY KHÔ mặc định —
    `ap_dung: true` mới ghi.
  • KHÔNG có công cụ xoá: không `delete record` (đo 19/10/2026: xoá HẲN), không thùng rác tự động, không `close document`
    (làm EndNote sập). Thùng rác: công cụ chỉ CHUẨN BỊ (hiện đúng bản ghi) và KIỂM — bác sĩ bấm.
  • `endnote_loai_tru` chỉ dùng khi BÁC SĨ đã nói loại bài đó; `ly_do` phải là lời bác sĩ.

Giao thức: MCP qua stdio — JSON-RPC 2.0, mỗi thông điệp một dòng. Chỉ dùng thư viện chuẩn (chạy được bằng `python3` hệ thống
hay `uv run`). stdout là KÊNH GIAO THỨC: mọi dòng chữ khác đi stderr.

Cài cho Claude Desktop (khung chat): `python3 tools/mcp/endnote_ebm_mcp.py --cai-claude-desktop` (chạy khô) → `--ap-dung`
(sao lưu tệp cấu hình trước khi ghi, chỉ thêm/cập nhật đúng khoá `endnote-ebm`).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
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
PHIEN_BAN = "1.0.0"
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
    kq["khoa_ghi"] = _nap("_mcp_kg", "khoa_ghi_endnote.py").doc_khoa()
    return kq


def cc_tim(a: dict) -> dict:
    dd = [str(x) for x in (a.get("dinh_danh") or [])][:200]
    if not dd:
        raise ValueError("cần `dinh_danh`: danh sách PMID hoặc DOI")
    return mod("sk").tra_dinh_danh(_thu_vien(), dd)


def cc_nhom(a: dict) -> dict:
    en, tv = _endnote()
    ten = (a.get("ten_nhom") or "").strip()
    if not ten:
        ds = list(dict.fromkeys(en.ten_cac_nhom()))
        loc = (a.get("loc") or "").strip()
        return {"nhom": [n for n in ds if loc.lower() in n.lower()] if loc else ds}
    ids = en.thanh_vien_nhom(ten)
    rec = [r for r in (mod("sk").so_rec(x) for x in ids) if r is not None]
    kn = mod("sk")._ket_noi(tv)
    try:
        ban_ghi = [{"rec": r, "tieu_de": ((kn.execute("SELECT title FROM refs WHERE id = ?", (r,)).fetchone() or [""])[0] or "")[:160],
                    "so_tep": kn.execute("SELECT count(*) FROM file_res WHERE refs_id = ?", (r,)).fetchone()[0]} for r in rec]
    finally:
        kn.close()
    return {"ten_nhom": ten, "so_ban_ghi": len(rec), "chua_co_tep": sum(1 for b in ban_ghi if not b["so_tep"]),
            "ban_ghi": ban_ghi}


def cc_gan_pdf_kho(a: dict) -> dict:
    nec = mod("nec")
    en, tv = _endnote()
    kho = nec.xac_dinh_kho(None, nec._tim_dash_goc(), [])
    pm = [str(x) for x in a.get("pmids") or []] or None
    return nec.gan_kho(en, kho, pm, bool(a.get("ap_dung")))


def cc_dua_vao_nhom(a: dict) -> dict:
    en, _tv = _endnote()
    ten = (a.get("ten_nhom") or "").strip()
    rec = [int(x) for x in a.get("rec_nums") or []]
    if not ten or not rec:
        raise ValueError("cần `ten_nhom` và `rec_nums`")
    csdl = en.so_csdl()
    ids = [f'<RecordID database="{csdl}" recNum="{r}" />' for r in rec]
    if not a.get("ap_dung"):
        return {"chay_kho": True, "se_dang": len(ids), "ten_nhom": ten}
    en.dang_vao_nhom(ids, ten)
    co = set(en.thanh_vien_nhom(ten))
    return {"da_dang": sum(1 for i in ids if i in co), "yeu_cau": len(ids), "ten_nhom": ten}


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
     "có tệp/thùng rác, EndNote có đang mở, nhóm chờ thùng rác, khoá ghi. Chỉ đọc.", _sc({}), cc_trang_thai),
    ("endnote_tim", "Tra bản ghi theo PMID hoặc DOI trên cơ sở dữ liệu EndNote (chỉ đọc): recNum, tiêu đề, năm, số tệp đính kèm, "
     "có trong thùng rác không.", _sc({"dinh_danh": {"type": "array", "items": {"type": "string"}}}, ["dinh_danh"]), cc_tim),
    ("endnote_nhom", "Không có ten_nhom: liệt kê tên nhóm (lọc bằng `loc`). Có ten_nhom: các bản ghi của nhóm và bản nào chưa có "
     "tệp. Cần EndNote đang mở thư viện. Chỉ đọc.",
     _sc({"ten_nhom": {"type": "string"}, "loc": {"type": "string"}}), cc_nhom),
    ("endnote_gan_pdf_kho", "Gắn PDF toàn văn có sẵn trong kho EBM (`toan_van_oa/PMID-<n>_*.pdf`) vào bản ghi CHƯA có tệp (khớp "
     "theo PMID). Chạy khô mặc định.",
     _sc({"pmids": {"type": "array", "items": {"type": "string"}}, "ap_dung": _AP}), cc_gan_pdf_kho),
    ("endnote_dua_vao_nhom", "Đăng bản ghi (recNum) vào một nhóm CUSTOM. Chạy khô mặc định. Không xoá, không bỏ khỏi nhóm.",
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
