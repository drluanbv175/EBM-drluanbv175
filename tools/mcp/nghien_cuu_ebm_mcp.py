#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nghien_cuu_ebm_mcp.py — Máy chủ MCP «nghien-cuu-ebm»: một cửa CHỈ ĐỌC vào hệ nghiên cứu G0–G10, tra điểm khám và
trạng thái chứng cứ cho MỌI nơi dùng Claude (15/11/2026).

Bác sĩ 14/11/2026 giao lộ trình R8 («muốn có» một máy chủ MCP nghiên cứu CHỈ ĐỌC). Cùng khuôn `endnote_ebm_mcp.py` và
`spss_r_ebm_mcp.py`: Claude Code (qua `.mcp.json`) và Claude Desktop/khung chat (qua `--cai-claude-desktop`) gọi CHÍNH
các công cụ đã đo của hai repo — máy chủ không tự chấm, không tự suy:

  • repo y khoa (`medical-ebm-automation/tools/`): list_studies.py · cong_song.trang_thai_song (chấm SỐNG từng cổng,
    write=False) · study_readiness.py · kiem_chi_tiet_he_nghien_cuu.py --no-write · hoi_dong_cong.py uoc-tinh / ho-so ·
    nhat_quan_xuyen_cong.py;
  • repo gốc (`tools/`): tra_diem_kham.py (chỉ thẻ ĐÃ DUYỆT; ngoài phạm vi ⇒ «chưa giám sát») · kiem_do_tuoi_chung_cu.py ·
    doc_ket_qua_rut_bai_kho.py · dang_ky_chu_de.py --mau-thuan · kiem_quyet_dinh_da_duyet.py (đều ngoại tuyến).

CHỈ ĐỌC — ba lớp, không ngoại lệ:
  1. KHÔNG có công cụ ký/duyệt cổng, ghi sổ cái, sửa exports/, khoá dữ liệu; không có tham số kiểu `ap_dung`.
     `kiem_bat_bien()` chạy LÚC NẠP: tên công cụ/tham số mang dấu hiệu ghi, danh sách lệnh cho phép một công cụ ghi
     (approve_gate, run_gN_auto, mark_study_synthetic…), cờ ghi, hay mã nội tuyến có thao tác ghi ⇒ máy chủ KHÔNG khởi động.
  2. Mọi tiến trình con đi qua `_LENH_CHI_DOC`: đúng tệp, đúng lệnh con, đúng cờ cho phép; cờ bắt buộc (`--no-write` của
     kiem_chi_tiet) thiếu ⇒ từ chối. Giá trị (mã đề tài, cổng) kiểm khuôn — không bao giờ bắt đầu bằng «-».
  3. Tiến trình con chạy với PYTHONDONTWRITEBYTECODE=1; tra điểm khám ép `ghi=False` và trỏ thư mục nhật ký vào nơi KHÔNG
     tồn tại — lượt tra qua MCP không ghi nhật ký tác động lẫn sổ ứng viên watchlist; câu hỏi đi qua stdin, không qua argv.
Việc «chạy dự thảo cổng» (run_gN_auto) CỐ Ý không có ở đây — nếu cần sẽ là quyết định riêng của bác sĩ.

Giao thức: MCP qua stdio — JSON-RPC 2.0, mỗi thông điệp một dòng. Chỉ dùng thư viện chuẩn. stdout là KÊNH GIAO THỨC: tiến
trình con bị bắt đầu ra; mọi dòng chữ khác đi stderr.

Cài cho Claude Desktop: `python3 tools/mcp/nghien_cuu_ebm_mcp.py --cai-claude-desktop` (chạy khô) → `--ap-dung` (sao lưu
tệp cấu hình trước khi ghi, chỉ thêm/cập nhật đúng khoá `nghien-cuu-ebm`). Cần bác sĩ kiểm chứng.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path

for _s in (sys.stdin, sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

GOC = Path(__file__).resolve().parents[2]  # repo gốc — thư mục chứa .mcp.json
TEN_MAY_CHU = "nghien-cuu-ebm"
PHIEN_BAN = "1.0.0"
GIAO_THUC = ("2025-06-18", "2025-03-26", "2024-11-05")
CAN_KIEM = "Cần bác sĩ kiểm chứng."
TRAN_DONG = 100  # đầu ra chữ dài hơn ⇒ rút gọn (giữ dòng tiêu đề), `day_du: true` mới trả đủ
TRAN_CAU_HOI = 500
_GIA_TRI = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")  # giá trị đối số: chữ/số đầu — chặn «-cờ», «..», «.ẩn», «a/b»
_CONG = re.compile(r"G(?:[0-9]|10)")


def thu_muc_goc() -> Path:
    """Repo gốc (EBM_GOC_ROOT đè — chỉ dùng cho test)."""
    env = os.environ.get("EBM_GOC_ROOT")
    return Path(env) if env else GOC


def thu_muc_y_khoa() -> Path:
    """Repo y khoa (EBM_MEDICAL_ROOT đè — cùng biến với spss-r-ebm)."""
    env = os.environ.get("EBM_MEDICAL_ROOT")
    return Path(env) if env else thu_muc_goc() / "medical-ebm-automation"


def python_du_an() -> str:
    """Python của môi trường dự án ~/.ebm-venv (công cụ y khoa cần thư viện của nó). EBM_VENV_PYTHON đè."""
    env = os.environ.get("EBM_VENV_PYTHON")
    if env:
        return env
    for p in (Path.home() / ".ebm-venv" / "bin" / "python", Path.home() / ".ebm-venv" / "Scripts" / "python.exe"):
        if p.exists():
            return str(p)
    return sys.executable


# ─────────────────────────── lớp 2: danh sách lệnh CHỈ ĐỌC ───────────────────────────

# (gốc, tệp) → luật. «co»: cờ được phép → có nhận giá trị không. «lenh_con»: đối số đầu phải thuộc tập này.
# «bat_buoc»: cờ PHẢI có. Không có trong bảng ⇒ không chạy.
_LENH_CHI_DOC: dict[tuple[str, str], dict] = {
    ("y_khoa", "list_studies.py"): {"co": {"--json": False}},
    ("y_khoa", "study_readiness.py"): {"co": {"--study": True}},
    ("y_khoa", "kiem_chi_tiet_he_nghien_cuu.py"): {"co": {"--study": True, "--no-write": False, "--khong-canary": False},
                                                    "bat_buoc": ("--no-write",)},
    ("y_khoa", "hoi_dong_cong.py"): {"lenh_con": ("uoc-tinh", "ho-so"),
                                     "co": {"--study": True, "--gate": True, "--json": False}},
    ("y_khoa", "nhat_quan_xuyen_cong.py"): {"co": {"--study": True, "--json": False}},
    ("goc", "kiem_do_tuoi_chung_cu.py"): {"co": {}},
    ("goc", "doc_ket_qua_rut_bai_kho.py"): {"co": {"--json": False}},
    ("goc", "dang_ky_chu_de.py"): {"co": {"--mau-thuan": False}},
    ("goc", "kiem_quyet_dinh_da_duyet.py"): {"co": {}},
}

# Mã nội tuyến (chạy `python -c` trong thư mục repo tương ứng) — cũng là danh sách đóng.
_MA_TRANG_THAI_CONG = """import json, sys
from pathlib import Path
sys.path[:0] = ['.', 'tools']
import cong_song as CS
try:
    import gate_contract as GC
    cung = set(GC._GATE_REQUIRED_STAKEHOLDERS)
except Exception:
    cung = None
study = sys.argv[1]
d = Path.cwd() / 'exports' / study
kq = []
for i in range(11):
    g = 'G%d' % i
    co = (d / (g + '_checkpoint.json')).exists() or any(d.glob(g + '_*')) or any(d.glob(g.lower() + '_*'))
    dong = {'gate': g, 'cong_cung': (g in cung) if cung is not None else None}
    if not co:
        dong.update(muc='CHUA_CHAY', ly_do='chưa có checkpoint/artifact của cổng')
    else:
        r = CS.trang_thai_song(g, study, d)
        dong.update({k: r.get(k) for k in ('status', 'muc', 'dat', 'bi_chan', 'nguon', 'ly_do', 'trang_thai_luu')})
    kq.append(dong)
print(json.dumps(kq, ensure_ascii=False))
"""

_MA_TRA_DIEM_KHAM = """import contextlib, io, json, sys, tempfile, uuid
from pathlib import Path
sys.path[:0] = ['tools']
import tra_diem_kham as T
cau = sys.stdin.read().strip()
T.STATE = Path(tempfile.gettempdir()) / ('nghien-cuu-ebm-chi-doc-' + uuid.uuid4().hex) / 'state'
bat = {}
_tra, _in = T.tra_chi_tiet, T.in_quick_view
def tra(q, cards):
    r = _tra(q, cards)
    bat['ket'], bat['loai'] = r[0], r[1]
    return r
def in_khong_ghi(*a, **k):
    k['ghi'] = False
    return _in(*a, **k)
T.tra_chi_tiet, T.in_quick_view = tra, in_khong_ghi
sys.argv = ['tra_diem_kham.py', cau]
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    ma = T.main()
the = []
for c in bat.get('ket') or []:
    s = c.get('source') if isinstance(c.get('source'), dict) else {}
    the.append({'id': c.get('id'), 'decision': c.get('decision'), 'topic': str(c.get('topic') or '')[:110],
                'pmid': s.get('pmid') or None, 'doi': s.get('doi') or None, 'gradeLevel': c.get('gradeLevel'),
                'xung_dot': bool(c.get('_xung_dot'))})
print(json.dumps({'ma': ma, 'loai': bat.get('loai'), 'the': the, 'van_ban': buf.getvalue()}, ensure_ascii=False))
"""

_MA_CHI_DOC: dict[str, tuple[str, str]] = {
    "trang_thai_cong": ("y_khoa", _MA_TRANG_THAI_CONG),
    "tra_diem_kham": ("goc", _MA_TRA_DIEM_KHAM),
}


def _kiem_doi_so(goc: str, tep: str, doi_so: list[str]) -> None:
    """Lớp chặn cuối: tệp + lệnh con + cờ + giá trị phải khớp `_LENH_CHI_DOC` — không khớp ⇒ RuntimeError «cấm»."""
    luat = _LENH_CHI_DOC.get((goc, tep))
    if luat is None:
        raise RuntimeError(f"cấm: {tep} không nằm trong danh sách lệnh CHỈ ĐỌC")
    ds, i, gap = [str(x) for x in doi_so], 0, set()
    if luat.get("lenh_con"):
        if not ds or ds[0] not in luat["lenh_con"]:
            raise RuntimeError(f"cấm: lệnh con của {tep} chỉ được là {', '.join(luat['lenh_con'])}")
        i = 1
    co = luat.get("co") or {}
    while i < len(ds):
        x = ds[i]
        if x not in co:
            raise RuntimeError(f"cấm: cờ {x!r} không nằm trong danh sách cho phép của {tep}")
        gap.add(x)
        if co[x]:
            if i + 1 >= len(ds) or not _GIA_TRI.fullmatch(ds[i + 1]):
                raise RuntimeError(f"cấm: {x} thiếu giá trị hợp lệ")
            i += 2
        else:
            i += 1
    thieu = [c for c in luat.get("bat_buoc", ()) if c not in gap]
    if thieu:
        raise RuntimeError(f"cấm: {tep} thiếu cờ bắt buộc {', '.join(thieu)}")


def _moi_truong() -> dict:
    return {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}


def _chay(argv: list[str], cwd: Path, thoi_han: int, vao: str | None = None) -> dict:
    """Tiến trình con bắt trọn đầu ra; `vao` (câu hỏi điểm khám) đi qua stdin — không qua argv, không lộ trong `ps`."""
    kw: dict = {"input": vao} if vao is not None else {"stdin": subprocess.DEVNULL}
    try:
        k = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=thoi_han, check=False, env=_moi_truong(), **kw)  # fmt: skip
    except subprocess.TimeoutExpired:
        return {"ma_thoat": None, "stdout": "", "loi": f"quá thời hạn {thoi_han} giây"}
    return {"ma_thoat": k.returncode, "stdout": k.stdout or "", "loi": "\n".join((k.stderr or "").strip().splitlines()[-15:])}


def _thu_muc(goc: str) -> Path:
    tm = thu_muc_y_khoa() if goc == "y_khoa" else thu_muc_goc()
    if not (tm / "tools").is_dir():
        raise RuntimeError(f"không thấy {tm / 'tools'} — " + ("repo y khoa chưa có cạnh repo gốc" if goc == "y_khoa"
                                                               else "repo gốc không đủ"))
    return tm


def chay_cong_cu(goc: str, tep: str, doi_so: list[str], thoi_han: int = 180) -> dict:
    """Chạy MỘT công cụ chuẩn trong danh sách CHỈ ĐỌC (tiến trình con, không đụng kênh giao thức stdout)."""
    _kiem_doi_so(goc, tep, doi_so)
    tm = _thu_muc(goc)
    cc = tm / "tools" / tep
    if not cc.is_file():
        raise RuntimeError(f"không thấy {cc} — kéo bản mới của repo")
    return _chay([python_du_an(), str(cc), *doi_so], tm, thoi_han)


def chay_ma(ten: str, doi_so: list[str], thoi_han: int = 300, vao: str | None = None) -> dict:
    """Chạy một mã nội tuyến trong `_MA_CHI_DOC` (danh sách đóng) với giá trị đã kiểm khuôn."""
    if ten not in _MA_CHI_DOC:
        raise RuntimeError(f"cấm: mã nội tuyến {ten!r} không nằm trong danh sách CHỈ ĐỌC")
    for x in doi_so:
        if not _GIA_TRI.fullmatch(str(x)):
            raise RuntimeError(f"cấm: giá trị {x!r} không hợp lệ")
    goc, ma = _MA_CHI_DOC[ten]
    return _chay([python_du_an(), "-c", ma, *[str(x) for x in doi_so]], _thu_muc(goc), thoi_han, vao)


# ─────────────────────────── lớp 1: bất biến lúc nạp ───────────────────────────

_TU_GHI = frozenset({"ky", "ghi", "sua", "xoa", "khoa", "chot", "nap", "duyet", "ap", "dung", "chay", "run", "set",
                     "update", "apply", "force", "tep", "ra"})
_CHU_GHI = ("approve", "sign", "seal", "lock", "write", "delete", "ledger", "commit", "merge")
# Tên tệp xét theo TỪ (tách «_») — «nghien» chứa «ghi», «dang_ky»/«da_duyet» là đọc sổ, không phải ký/duyệt.
_TU_TEP_CAM = frozenset({"ghi", "nap", "khoa", "xoa", "sua", "xuat", "tao", "chot", "approve", "sign", "seal", "lock",
                         "ledger", "write", "apply"})
_TEP_CAM = re.compile(r"approve|run_g\d|mark_study|ledger|seal|tiep_nhan")
_CO_CAM = ("ghi", "ap-dung", "apply", "write", "i-know", "i-confirm", "force", "xu-ly", "tiep-nhan", "sua", "xoa",
           "launchd")
_CO_CHI_DOC_HOP_LE = frozenset({"--no-write"})
_LENH_CON_CAM = ("ghi", "ap-dung", "xu-ly", "trach-nhiem", "bai-hoc", "khai")
_MA_CAM = ("write_text", "write_bytes", "open(", "ghi=True", "write=True", "approve", "unlink", "rmtree", "os.remove",
           "shutil", "mkdir", "rename(", "replace(")
_PHAI_CO_CO = {"kiem_chi_tiet_he_nghien_cuu.py": "--no-write"}


def kiem_bat_bien(cong_cu: list | None = None, lenh: dict | None = None, ma: dict | None = None) -> None:
    """Bất biến CHỈ ĐỌC — vi phạm ⇒ RuntimeError (máy chủ không khởi động). Chạy lúc nạp mô-đun."""
    cong_cu = CONG_CU if cong_cu is None else cong_cu
    lenh = _LENH_CHI_DOC if lenh is None else lenh
    ma = _MA_CHI_DOC if ma is None else ma
    loi: list[str] = []

    def _xau(ten: str) -> bool:
        t = ten.casefold()
        return bool(set(t.split("_")) & _TU_GHI) or any(c in t for c in _CHU_GHI)

    for ten, _mt, sc, _h in cong_cu:
        if _xau(ten):
            loi.append(f"công cụ «{ten}» mang dấu hiệu GHI")
        for p in (sc.get("properties") or {}):
            if _xau(p):
                loi.append(f"tham số «{p}» của «{ten}» mang dấu hiệu GHI")
    for (goc, tep), luat in lenh.items():
        if goc not in ("goc", "y_khoa"):
            loi.append(f"{tep}: gốc lạ {goc!r}")
        goc_ten = tep.rsplit(".", 1)[0].casefold()
        if set(goc_ten.split("_")) & _TU_TEP_CAM or _TEP_CAM.search(goc_ten):
            loi.append(f"{tep}: công cụ có thể GHI không được vào danh sách CHỈ ĐỌC")
        for c in (luat.get("co") or {}):
            if c not in _CO_CHI_DOC_HOP_LE and any(x in c for x in _CO_CAM):
                loi.append(f"{tep}: cờ GHI {c}")
        for lc in luat.get("lenh_con") or ():
            if any(x in lc for x in _LENH_CON_CAM):
                loi.append(f"{tep}: lệnh con GHI {lc}")
        can = _PHAI_CO_CO.get(tep)
        if can and can not in (luat.get("bat_buoc") or ()):
            loi.append(f"{tep}: phải BẮT BUỘC {can}")
    for ten, (goc, m) in ma.items():
        if goc not in ("goc", "y_khoa"):
            loi.append(f"mã {ten}: gốc lạ {goc!r}")
        for x in _MA_CAM:
            if x in m:
                loi.append(f"mã nội tuyến {ten} chứa thao tác ghi «{x}»")
    if loi:
        raise RuntimeError("máy chủ nghien-cuu-ebm vi phạm bất biến CHỈ ĐỌC: " + "; ".join(loi))


# ─────────────────────────── tiện ích ───────────────────────────

def _ma_de_tai(a: dict) -> str:
    s = str(a.get("study") or "")
    if not _GIA_TRI.fullmatch(s):
        raise ValueError(f"mã đề tài không hợp lệ: {s!r}")
    if not (thu_muc_y_khoa() / "exports" / s).is_dir():
        raise ValueError(f"không có thư mục đề tài exports/{s}")
    return s


def _cong(a: dict, cho_all: bool, mac_dinh: str | None = None) -> str:
    g = str(a.get("gate") or mac_dinh or "").strip().upper()
    if g == "ALL" and cho_all:
        return g
    if not _CONG.fullmatch(g):
        raise ValueError(f"cổng không hợp lệ: {g!r} — G0…G10" + (" hoặc ALL" if cho_all else ""))
    return g


def _gon(chu: str, day_du: bool = False) -> dict:
    """Đầu ra chữ của công cụ chuẩn; quá trần ⇒ giữ dòng tiêu đề (thụt ≤2), rồi bỏ dòng 🟢, rồi đầu/cuối."""
    dong = (chu or "").rstrip().splitlines()
    tran = 400 if day_du else TRAN_DONG
    if len(dong) <= tran:
        return {"dau_ra": "\n".join(dong)}
    giu = [d for d in dong if len(d) - len(d.lstrip(" ")) <= 2]
    if len(giu) > tran:
        giu = [d for d in giu if not d.strip().startswith(("🟢", "✔", "✓"))]
    if len(giu) > tran:
        nua = tran // 2
        giu = [*giu[:nua], f"… (bỏ {len(giu) - 2 * nua} dòng giữa)", *giu[-nua:]]
    return {"dau_ra": "\n".join(giu),
            "rut_gon": f"rút gọn từ {len(dong)} dòng (giữ dòng tiêu đề, bỏ chi tiết thụt sâu/dòng 🟢) — gọi lại với "
                       "day_du: true để xem đủ"}


def _json(k: dict, ten: str):
    """JSON ở dòng cuối/toàn bộ stdout của công cụ — không đọc được ⇒ RuntimeError kèm mã thoát + lỗi."""
    out = (k.get("stdout") or "").strip()
    for thu in (out, out.splitlines()[-1] if out else ""):
        try:
            return json.loads(thu)
        except ValueError:
            continue
    raise RuntimeError(f"{ten}: không đọc được kết quả (mã thoát {k.get('ma_thoat')}) — {k.get('loi') or out[-300:]}")


# ─────────────────────────── công cụ ───────────────────────────

def cc_danh_sach(a: dict) -> dict:
    rows = _json(chay_cong_cu("y_khoa", "list_studies.py", ["--json"]), "list_studies")
    rows = rows if isinstance(rows, list) else []
    ds = [r for r in rows if a.get("tat_ca") or (r.get("recognized") and not r.get("system"))]
    return {"so_de_tai": len(ds), "an_di": len(rows) - len(ds),
            "de_tai": [{"study": r.get("study"), "topic": str(r.get("topic") or "")[:160] or None,
                        "cong_xa_nhat_da_chay": r.get("furthest_gate"), "moc": r.get("milestones"),
                        "sua_lan_cuoi": r.get("last_modified")} for r in ds],
            "ghi_chu": "«cong_xa_nhat_da_chay» = cổng xa nhất CÓ checkpoint, KHÔNG phải đã đạt — trạng thái sống: "
                       "trang_thai_cong; «an_di» = thư mục hệ thống/không rõ đề tài (tat_ca: true để xem)."}


def cc_trang_thai_cong(a: dict) -> dict:
    study = _ma_de_tai(a)
    k = chay_ma("trang_thai_cong", [study])
    return {"study": study, "cong": _json(k, "cong_song"),
            "ghi_chu": "Chấm SỐNG bằng chính gN_quality_gate.evaluate_study(write=False) qua cong_song — không ghi gì. "
                       "KHONG_DO_DUOC không bao giờ là «đạt»; READY = chờ người có thẩm quyền ký. Chữ ký sổ cái: san_sang."}


def cc_san_sang(a: dict) -> dict:
    study = _ma_de_tai(a)
    k = chay_cong_cu("y_khoa", "study_readiness.py", ["--study", study])
    return {"study": study, "ma_thoat": k["ma_thoat"], **_gon(k["stdout"], bool(a.get("day_du"))),
            **({"loi": k["loi"]} if k["ma_thoat"] else {})}


def cc_kiem_chi_tiet(a: dict) -> dict:
    study = _ma_de_tai(a)
    k = chay_cong_cu("y_khoa", "kiem_chi_tiet_he_nghien_cuu.py", ["--study", study, "--no-write", "--khong-canary"],
                     thoi_han=300)
    nghia = {0: "không 🔴, không 🟡", 1: "còn việc của người thật (🟡)", 2: "có 🔴 máy sửa được/fail-closed hở",
             3: "công cụ chết — KHÔNG ĐO ĐƯỢC"}
    return {"study": study, "ma_thoat": k["ma_thoat"], "y_nghia": nghia.get(k["ma_thoat"], "không đo được"),
            **_gon(k["stdout"], bool(a.get("day_du"))), **({"loi": k["loi"]} if k["ma_thoat"] == 3 else {})}


def cc_hoi_dong(a: dict) -> dict:
    study = _ma_de_tai(a)
    che_do = a.get("che_do") or "uoc_tinh"
    if che_do not in ("uoc_tinh", "ho_so"):
        raise ValueError("che_do: uoc_tinh hoặc ho_so")
    gate = _cong(a, cho_all=che_do == "uoc_tinh", mac_dinh="ALL" if che_do == "uoc_tinh" else None)
    lenh = {"uoc_tinh": "uoc-tinh", "ho_so": "ho-so"}[che_do]
    k = chay_cong_cu("y_khoa", "hoi_dong_cong.py", [lenh, "--study", study, "--gate", gate, "--json"])
    return {"study": study, "gate": gate, "che_do": che_do, "ket_qua": _json(k, "hoi_dong_cong"),
            "ghi_chu": "TƯ VẤN, 0 agent — máy lập ước tính/hồ sơ; KHÔNG triệu tập họp. Triệu tập phải hỏi bác sĩ (chi phí "
                       "token); hội đồng không mở/chặn cổng."}


def cc_nhat_quan(a: dict) -> dict:
    study = _ma_de_tai(a)
    k = chay_cong_cu("y_khoa", "nhat_quan_xuyen_cong.py", ["--study", study, "--json"])
    nghia = {0: "PASS — khớp", 1: "REVIEW — cần chủ nhiệm xem", 2: "BLOCK — lệch cứng (G10-AUTO-11 chặn)",
             3: "KHÔNG ĐO ĐƯỢC"}
    kq = {"study": study, "ma_thoat": k["ma_thoat"], "y_nghia": nghia.get(k["ma_thoat"], "không đo được")}
    if k["ma_thoat"] == 3 or not (k["stdout"] or "").strip():
        return {**kq, "loi": k["loi"]}
    return {**kq, "ket_qua": _json(k, "nhat_quan_xuyen_cong")}


_DONG_DEMO = "(chế độ --demo: không ghi sổ ứng viên watchlist)"
_DONG_MCP = "(MCP chỉ đọc: lượt tra này KHÔNG ghi nhật ký tác động lẫn sổ ứng viên watchlist)"


def cc_tra_diem_kham(a: dict) -> dict:
    cau = " ".join(str(a.get("cau_hoi") or "").split())
    if not cau or cau.startswith("-") or len(cau) > TRAN_CAU_HOI:
        raise ValueError(f"cau_hoi: 1–{TRAN_CAU_HOI} ký tự, không bắt đầu bằng «-»")
    k = chay_ma("tra_diem_kham", [], thoi_han=120, vao=cau)
    kq = _json(k, "tra_diem_kham")
    the = kq.get("the") or []
    return {"cau_hoi": cau, "chua_giam_sat": not the, "loai": kq.get("loai"), "the": the,
            "van_ban": str(kq.get("van_ban") or "").replace(_DONG_DEMO, _DONG_MCP).strip(),
            "luat": "CHỈ thẻ ĐÃ DUYỆT. chua_giam_sat=true ⇒ nói «CHƯA ĐƯỢC GIÁM SÁT» + tra tay; KHÔNG trả lời từ trí "
                    "nhớ mô hình. Đọc TIÊU ĐỀ thẻ trước khi dựa vào; cờ rút bài/bản mới hơn nằm trong van_ban."}


_BO_DEM_CHUNG_CU = (
    ("do_tuoi", "kiem_do_tuoi_chung_cu.py", [], {0: "còn hạn — hoặc ⚪ không đo được (đọc dòng đầu)", 1: "quá hạn"}),
    ("rut_bai_kho", "doc_ket_qua_rut_bai_kho.py", ["--json"],
     {0: "🟢 lượt tái kiểm cuối sạch (toàn vẹn kỹ thuật)", 1: "🔴 có phát hiện cần bác sĩ xem", 3: "⚪ chưa đo được"}),
    ("mau_thuan_giua_ban", "dang_ky_chu_de.py", ["--mau-thuan"],
     {0: "không mâu thuẫn", 1: "có mâu thuẫn cần bác sĩ quyết", 2: "⚪ KHÔNG KIỂM ĐƯỢC"}),
    ("quyet_dinh_da_duyet", "kiem_quyet_dinh_da_duyet.py", [],
     {0: "còn nguyên", 1: "⚪ có mục không kiểm được", 2: "🔴 tái phạm quyết định đã duyệt"}),
)


def cc_trang_thai_chung_cu(a: dict) -> dict:
    goc = thu_muc_goc()
    kq: dict = {"co_du_lieu_dashboard_that": (goc / "EBM-Dashboards").is_dir()}
    for khoa, tep, doi, nghia in _BO_DEM_CHUNG_CU:
        try:
            k = chay_cong_cu("goc", tep, doi, thoi_han=120)
        except RuntimeError as e:  # một bộ đếm vắng không làm mất các bộ còn lại — báo ⚪, không coi là sạch
            kq[khoa] = {"ma_thoat": None, "y_nghia": "⚪ không đo được", "loi": str(e)[:300]}
            continue
        muc = {"ma_thoat": k["ma_thoat"], "y_nghia": nghia.get(k["ma_thoat"], "⚪ không đo được")}
        if "--json" in doi:
            try:
                muc["ket_qua"] = _json(k, tep)
            except RuntimeError as e:
                muc["loi"] = str(e)[:300]
        else:
            muc.update(_gon(k["stdout"], bool(a.get("day_du"))))
            if k["ma_thoat"] not in nghia and k["loi"]:
                muc["loi"] = k["loi"]
        kq[khoa] = muc
    if not kq["co_du_lieu_dashboard_that"]:
        p = goc / "cloud-mirror" / "trang-thai-chung-cu.json"
        try:
            g = json.loads(p.read_text(encoding="utf-8"))
            bd = g.get("bo_dem") or {}
            kq["anh_chup_cloud_mirror"] = {
                "sinh_luc": g.get("sinh_luc"), "may": g.get("may"),
                "do_tuoi": (bd.get("do_tuoi_chung_cu") or {}).get("stdout"),
                "quyet_dinh_da_duyet": (bd.get("quyet_dinh_da_duyet") or {}).get("stdout"),
                "canh_bao": "ẢNH CHỤP từ máy có dữ liệu — KHÔNG phải số đo sống trên máy này"}
        except (OSError, ValueError, AttributeError):
            kq["anh_chup_cloud_mirror"] = None
    kq["ghi_chu"] = ("Ngoại tuyến, chỉ đọc — không gọi mạng, không tự áp dụng. «Không đo được» ≠ «sạch». Chi tiết rút bài "
                     "từng nguồn: python3 tools/chu_trinh_chung_cu.py --vong 3 (gọi mạng, chạy tay).")
    return kq


def _sc(props: dict, bat_buoc: list[str] | None = None) -> dict:
    return {"type": "object", "properties": props, "required": bat_buoc or [], "additionalProperties": False}


_ST = {"type": "string", "description": "mã đề tài (thư mục exports/<mã>)"}
_DD = {"type": "boolean", "description": "true = trả đủ đầu ra (mặc định rút gọn)"}
CONG_CU = [
    ("danh_sach_de_tai", "Các đề tài trong exports/ (list_studies): cổng xa nhất đã chạy, mốc đời thực. Chỉ đọc.",
     _sc({"tat_ca": {"type": "boolean", "description": "kèm thư mục hệ thống/không rõ"}}), cc_danh_sach),
    ("trang_thai_cong", "Trạng thái SỐNG G0–G10 của một đề tài (cong_song, write=False). Chỉ đọc.",
     _sc({"study": _ST}, ["study"]), cc_trang_thai_cong),
    ("san_sang", "Việc CHƯA làm, ô trống, chữ ký sổ cái của một đề tài (study_readiness). Chỉ đọc.",
     _sc({"study": _ST, "day_du": _DD}, ["study"]), cc_san_sang),
    ("kiem_chi_tiet", "Kiểm 11 cổng × 5 trục (kiem_chi_tiet --no-write). Chỉ đọc.",
     _sc({"study": _ST, "day_du": _DD}, ["study"]), cc_kiem_chi_tiet),
    ("hoi_dong", "Hội đồng cổng, 0 agent: uoc_tinh (gate G0–G10/ALL) hoặc ho_so (một cổng). Không triệu tập.",
     _sc({"study": _ST, "gate": {"type": "string"}, "che_do": {"type": "string", "enum": ["uoc_tinh", "ho_so"]}},
         ["study"]), cc_hoi_dong),
    ("nhat_quan", "Đối chiếu N·α·power·thiết kế·kết cục chính xuyên cổng (nhat_quan_xuyen_cong). Chỉ đọc.",
     _sc({"study": _ST}, ["study"]), cc_nhat_quan),
    ("tra_diem_kham", "Tra tại điểm khám — CHỈ thẻ đã duyệt; ngoài phạm vi ⇒ «chưa giám sát». Không ghi nhật ký.",
     _sc({"cau_hoi": {"type": "string"}}, ["cau_hoi"]), cc_tra_diem_kham),
    ("trang_thai_chung_cu", "Độ tươi · rút bài kho · mâu thuẫn giữa bản · quyết định đã duyệt (ngoại tuyến). Chỉ đọc.",
     _sc({"day_du": _DD}), cc_trang_thai_chung_cu),
]
_BANG = {ten: ham for ten, _mt, _sc_, ham in CONG_CU}
kiem_bat_bien()


# ─────────────────────────── giao thức ───────────────────────────

def xu_ly(tin: dict) -> dict | None:
    """Một thông điệp JSON-RPC → phản hồi (None cho thông báo không cần trả lời)."""
    pt, ma = tin.get("method"), tin.get("id")
    if ma is None:
        return None
    if pt == "initialize":
        ban = (tin.get("params") or {}).get("protocolVersion")
        kq = {"protocolVersion": ban if ban in GIAO_THUC else GIAO_THUC[0], "capabilities": {"tools": {"listChanged": False}},
              "serverInfo": {"name": TEN_MAY_CHU, "version": PHIEN_BAN},
              "instructions": "Hệ nghiên cứu G0–G10, tra điểm khám, trạng thái chứng cứ — CHỈ ĐỌC: KHÔNG có công cụ ký/duyệt "
                              "cổng, ghi sổ cái, sửa exports. Trả lời bác sĩ bằng tiếng Việt, kèm «Cần bác sĩ kiểm chứng»; "
                              "ngoài thẻ đã duyệt thì nói «chưa giám sát», không trả lời từ trí nhớ."}  # fmt: skip
    elif pt == "ping":
        kq = {}
    elif pt == "tools/list":
        kq = {"tools": [{"name": t, "description": mt, "inputSchema": sc} for t, mt, sc, _h in CONG_CU]}
    elif pt == "tools/call":
        p = tin.get("params") or {}
        ham = _BANG.get(p.get("name"))
        if ham is None:
            return {"jsonrpc": "2.0", "id": ma, "result": {"isError": True, "content": [
                {"type": "text", "text": f"không có công cụ «{p.get('name')}» (máy chủ CHỈ ĐỌC — không có công cụ "
                                         "ký/duyệt/ghi)"}]}}  # fmt: skip
        try:
            ra = ham(p.get("arguments") or {})
            if isinstance(ra, dict):
                ra = {**ra, "luu_y": CAN_KIEM}
            kq = {"content": [{"type": "text", "text": json.dumps(ra, ensure_ascii=False, indent=1, default=str)}],
                  "isError": False}  # fmt: skip
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
        for t in tin if isinstance(tin, list) else [tin]:
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
    """Thêm/cập nhật ĐÚNG khoá `mcpServers.nghien-cuu-ebm` (giữ nguyên mọi khoá khác), sao lưu trước khi ghi."""
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
        tep.write_text(json.dumps(moi, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        kq["da_ghi"] = True
    return kq


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Máy chủ MCP nghien-cuu-ebm (stdio, CHỈ ĐỌC)")
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
