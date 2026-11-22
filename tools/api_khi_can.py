#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TỰ CHẠY API CLAUDE KHI CẦN — một lối vào cho các việc dùng API mà trước đây chỉ chạy khi có người gọi.

VÌ SAO (18/11/2026, bác sĩ duyệt)
=================================
Bác sĩ: «Những vấn đề chưa tự động hãy xây dựng … cơ chế tự động giúp tôi», rồi chọn TỰ CHẠY «Khi hệ thống nghiên cứu
y khoa và cập nhật chứng cứ cần, Quét lạc chủ đề phần đổi, Kiểm đề cương khi đổi, CAFÉ-S khi agent an toàn đổi»; trần
chi tiêu «Tôi đã cài đặt trên Claude Console». Chính sách nằm ở `sync/api-khi-can.json` (đi qua git); tệp vắng/hỏng ⇒
cơ chế TẮT HẲN, không chi tiền.

BA VIỆC
=======
  chu_de    QUÉT LẠC CHỦ ĐỀ PHẦN ĐỔI. Bản mới nhất của mỗi chủ đề (đúng luật chọn của quet_lac_chu_de_kho) mà nội dung
            được chấm — chủ đề + id · tiêu đề · hành động từng mục, tức ĐÚNG prompt của cổng — có vân tay khác lần chấm
            «ok» gần nhất trong sổ `~/.ebm-kiem-chu-de.json` (do CHÍNH cổng ghi, nên lượt chấm trong dây chuyền xuất gói
            cũng tính). Dashboard chưa có trong sổ mà lượt quét toàn kho gần nhất đã chấm «ok» và tệp không sửa sau đó
            cũng tính là đã kiểm. Chấm bằng chính cổng `check_topic_relevance` (thiếu SDK ⇒ cổng tự sang ~/.ebm-venv);
            có mục nghi lạc / không chắc / lỗi ⇒ báo cáo `EBM-Dashboards/derivatives/KIEM-CHU-DE-KHI-CAN_<lúc>.md`
            để bác sĩ rà. Máy KHÔNG gỡ mục nào.
  de_cuong  KIỂM ĐỀ CƯƠNG KHI ĐỔI. Báo cáo A12 / phản biện máy mà `duyet_kiem_may_api.tinh_trang_tat_ca` (repo y khoa,
            PR #306 của phiên khác) KHẲNG ĐỊNH là cũ (đề cương đổi sau lượt kiểm) ⇒ chạy lại công cụ đó `--goi-api`.
            «Không khẳng định được» KHÔNG tự chạy. Cầu nối y khoa dùng THEO TÍN DỤNG tài khoản (bác sĩ 21/11/2026 — không trần
            tháng tự đặt); tài khoản hết tín dụng / chạm giới hạn Console ⇒ cầu nối tự dừng và lượt này dừng theo.
  cafes     CAFÉ-S KHI AGENT AN TOÀN ĐỔI. Vân tay agent khác lượt đo gần nhất VÀ lượt đó cách ≥ N ngày (mặc định 30).

KHÔNG có ở đây (cố ý): hội đồng cổng (triệu tập phải hỏi bác sĩ — CLAUDE.md §1); ambient scribe / đọc ảnh (dữ liệu
từng ca, bác sĩ bấm).

LỐI VÀO
=======
    python3 tools/api_khi_can.py                      # CHẠY KHÔ: việc nào cần, ước chi phí — KHÔNG gọi API
    python3 tools/api_khi_can.py --chay               # chạy các việc cần mà chính sách cho phép
    python3 tools/api_khi_can.py --chay --chi cafes   # giới hạn việc (chu_de,de_cuong,cafes)
    python3 tools/api_khi_can.py --nen --im-khi-on    # hook đầu phiên: ≥ N giờ từ lần xét trước ⇒ phóng --chay ở NỀN

RÀO
===
- Một lượt tại một thời điểm (khoá tệp, coi là treo sau HAN_KHOA_GIO giờ).
- Hook chỉ phóng khi đã ≥ `nen_cach_gio_toi_thieu` giờ từ lần xét trước; phiên Cloud (CLAUDE_CODE_REMOTE=true) không phóng.
- Dưới pytest KHÔNG BAO GIỜ gọi thật, không phóng nền, không đụng sổ thật (rào BH181; đo thật thì EBM_KIEM_API_THAT=1).
- Sổ lượt chạy `~/.ebm-api-khi-can.json` (ngoài repo, ngoài OneDrive): thời điểm xét, kết quả từng việc — hòm việc đọc.
Mã thoát: 0 = không có việc / chạy xong sạch · 1 = có việc lỗi · 2 = chính sách hỏng hoặc vắng.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass

GOC = Path(__file__).resolve().parents[1]
GOC_MEA = GOC / "medical-ebm-automation"
CHINH_SACH = GOC / "sync" / "api-khi-can.json"
VIEC = ("chu_de", "de_cuong", "cafes")
TEN_VIEC = {"chu_de": "quét lạc chủ đề phần đổi", "de_cuong": "kiểm đề cương khi đổi",
            "cafes": "CAFÉ-S khi agent an toàn đổi"}
_SO_THAT = Path.home() / ".ebm-api-khi-can.json"
SO = Path(os.environ.get("EBM_SO_API_KHI_CAN") or _SO_THAT)   # kiểm thử trỏ tệp tạm
HAN_KHOA_GIO = 3
GIAY_DE_CUONG = 1800
GIAY_CAFES = 3600
CONG_CU_DE_CUONG = {"A12": "kiem_noi_dung_trich_dan.py", "PHAN_BIEN": "phan_bien_may_de_cuong.py"}
# 21/11/2026 (bác sĩ: tối ưu Claude API): A12 chạy NỀN ⇒ qua Batch BẤT ĐỒNG BỘ của y khoa #389 (−50% mọi token).
# `--batch`: chưa có batch chờ ⇒ nộp (mã 4); có ⇒ lấy kết quả (xong ⇒ ghi báo cáo, mã 0/1; chưa xong ⇒ mã 4). Mã 4 là
# «đang chờ batch», KHÔNG phải lỗi — lượt nền sau báo cáo vẫn cũ nên tự gọi lại và lấy kết quả. Đề cương đổi sau khi
# nộp ⇒ công cụ từ chối ghép (mã 3) và GIỮ sổ batch (batch đã trả phí) ⇒ lượt này chạy lại THƯỜNG để vẫn có báo cáo
# đúng bản hiện hành; không bao giờ tự xoá sổ batch. Chỉ bật khi công cụ y khoa đã có `--chi-lay` (đọc mã nguồn).
MA_DANG_CHO_BATCH = 4
CO_BATCH_BAT_DONG_BO = {"A12"}
# Dấu hiệu cầu nối y khoa từ chối gọi — so CHỮ THƯỜNG. 21/11/2026: cầu nối dùng theo tín dụng tài khoản; hết tín dụng ⇒
# `api_claude_nc.HetTinDung` («HẾT TÍN DỤNG»). Trần tháng chỉ còn khi biến môi trường OS đặt (kiểm thử/khoá khẩn cấp).
DAU_HIEU_HET_TIN_DUNG = ("hết tín dụng", "hettindung")
DAU_HIEU_HET_TRAN = ("trần chi phí", "kiểm được trần", "ngân sách", "hetngansach") + DAU_HIEU_HET_TIN_DUNG
MAC_DINH = {"chu_de_toi_da_moi_luot": 60, "cafes_cach_ngay_toi_thieu": 30, "nen_cach_gio_toi_thieu": 6}
GIA_SONNET = (2.0, 10.0)   # USD / triệu token vào · ra (Sonnet 5.5) — chỉ để IN ước tính, không dùng chặn


# ─────────────────────────── rào pytest ───────────────────────────
def _duoi_pytest() -> bool:
    return bool(os.environ.get("PYTEST_CURRENT_TEST")) and os.environ.get("EBM_KIEM_API_THAT") != "1"


def _la_tep_that(duong: Path) -> bool:
    """True khi `duong` là sổ THẬT hoặc khoá/nhật ký đi kèm nó ở thư mục nhà."""
    try:
        that = {_SO_THAT.resolve(), Path(str(_SO_THAT) + ".lock").resolve(), Path(str(_SO_THAT) + ".log").resolve()}
        return Path(duong).resolve() in that
    except (OSError, ValueError):
        return True   # không phân định được ⇒ thận trọng


# ─────────────────────────── chính sách · sổ · khoá ───────────────────────────
def doc_chinh_sach(tep: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Chính sách đã duyệt; None khi vắng / hỏng / sai kiểu ⇒ người gọi coi như TẮT (không chi tiền)."""
    try:
        d = json.loads(Path(tep or CHINH_SACH).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(d, dict) or not isinstance(d.get("tu_chay"), dict):
        return None
    tc = d["tu_chay"]
    if any(not isinstance(tc.get(v, False), bool) for v in VIEC):
        return None
    ra: Dict[str, Any] = {"tu_chay": {v: tc.get(v) is True for v in VIEC}}
    for k, md in MAC_DINH.items():
        gt = d.get(k, md)
        if isinstance(gt, bool) or not isinstance(gt, int) or gt < 1:
            return None
        ra[k] = gt
    return ra


def doc_so(tep: Optional[Path] = None) -> Dict[str, Any]:
    try:
        d = json.loads(Path(tep or SO).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        d = {}
    if not isinstance(d, dict):
        d = {}
    if not isinstance(d.get("luot"), list):
        d["luot"] = []
    return d


def ghi_so(so: Dict[str, Any], tep: Optional[Path] = None) -> None:
    duong = Path(tep or SO)
    if _duoi_pytest() and _la_tep_that(duong):
        return
    so["luot"] = list(so.get("luot") or [])[-100:]
    tam = duong.with_name(f"{duong.name}.{os.getpid()}.tmp")
    try:
        tam.write_text(json.dumps(so, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
        os.replace(tam, duong)
    except OSError:
        pass
    finally:
        if tam.exists():
            try:
                tam.unlink()
            except OSError:
                pass


def _khoa_tep() -> Path:
    return Path(str(SO) + ".lock")


def khoa_dang_giu(bay_gio: Optional[dt.datetime] = None) -> bool:
    k = _khoa_tep()
    try:
        tuoi = (bay_gio or dt.datetime.now()) - dt.datetime.fromtimestamp(k.stat().st_mtime)
    except OSError:
        return False
    return tuoi < dt.timedelta(hours=HAN_KHOA_GIO)


def lay_khoa() -> bool:
    k = _khoa_tep()
    if (_duoi_pytest() and _la_tep_that(k)) or khoa_dang_giu():
        return False
    try:
        if k.exists():
            k.unlink()          # khoá treo quá hạn
        fd = os.open(str(k), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(f"{os.getpid()} {dt.datetime.now().isoformat(timespec='seconds')}\n")
        return True
    except OSError:
        return False


def tra_khoa() -> None:
    try:
        _khoa_tep().unlink()
    except OSError:
        pass


def python_venv() -> Optional[str]:
    """Python của ~/.ebm-venv (Mac/Linux `bin/python`, Windows `Scripts/python.exe`) — nơi có SDK anthropic."""
    goc = Path.home() / ".ebm-venv"
    for p in (goc / "bin" / "python", goc / "Scripts" / "python.exe"):
        if p.is_file():
            return str(p)
    return None


def _nap(ten: str, duong: Path):
    sp = importlib.util.spec_from_file_location(ten, duong)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


def _chay_lenh(lenh: List[str], cwd: Path, timeout: int) -> Tuple[int, str]:
    """Chạy một công cụ con; trả (mã thoát, đuôi đầu ra). Quá giờ / không chạy được ⇒ mã 99 kèm lý do."""
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        r = subprocess.run(lenh, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return 99, f"quá {timeout} giây"
    except OSError as exc:
        return 99, f"không chạy được: {exc}"
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()[-600:]


# ─────────────────────────── việc 1 — quét lạc chủ đề phần đổi ───────────────────────────
def _nap_quet(goc: Path = GOC):
    return _nap("_quet_api_khi_can", goc / "tools" / "quet_lac_chu_de_kho.py")


def phu_quet_toan_kho(goc: Path = GOC) -> Dict[str, float]:
    """{tên dashboard: mốc} — các dashboard lượt quét toàn kho GẦN NHẤT đã chấm «ok»; mốc = lúc ghi báo cáo đó."""
    ds = sorted((goc / "EBM-Dashboards" / "derivatives").glob("QUET-LAC-CHU-DE_????????.json"))
    if not ds:
        return {}
    try:
        d = json.loads(ds[-1].read_text(encoding="utf-8"))
        moc = ds[-1].stat().st_mtime
    except (OSError, ValueError):
        return {}
    return {str(c.get("tep")): moc for c in (d.get("ket_qua") or []) if isinstance(c, dict) and c.get("status") == "ok"}


def _uoc_chu_de(prompt: str, so_muc: int) -> float:
    vao, ra = len(prompt) / 3.5, 75 * so_muc + 300
    return (vao * GIA_SONNET[0] + ra * GIA_SONNET[1]) / 1e6


def can_chu_de(goc: Path = GOC, so_chu_de: Optional[Dict[str, Dict]] = None, Q=None, C=None) -> List[Dict[str, Any]]:
    """Dashboard (bản mới nhất mỗi chủ đề) có nội dung được chấm khác lần chấm «ok» gần nhất. Chỉ đọc, miễn phí.

    `Q`/`C` (mô-đun quét toàn kho / cổng) để kiểm thử tiêm vào; mặc định nạp từ repo."""
    Q = Q or _nap_quet(GOC)
    C = C or Q.nap_cong(GOC)
    so = so_chu_de if so_chu_de is not None else C.doc_so_chu_de()
    phu = phu_quet_toan_kho(goc)
    ra = []
    for f in Q.chon_ban_moi_nhat(goc / "EBM-Dashboards"):
        yc = Q.dung_yeu_cau(C, f)
        if not yc:
            continue
        vt = hashlib.sha256(yc["prompt"].encode("utf-8")).hexdigest()
        if f.name in so:                       # sổ của cổng là căn cứ chính: khớp ⇒ đã kiểm; lệch ⇒ nội dung đã đổi
            if so[f.name].get("van_tay") == vt:
                continue
        elif f.name in phu and f.stat().st_mtime <= phu[f.name]:
            continue                           # quét toàn kho đã chấm «ok», tệp không sửa sau đó
        ra.append({"tep": f, "so_muc": len(yc["muc"]), "uoc_usd": _uoc_chu_de(yc["prompt"], len(yc["muc"]))})
    return ra


def chay_chu_de(can: List[Dict[str, Any]], cs: Dict[str, Any], goc: Path = GOC,
                goi: Optional[Callable[[str], Dict]] = None) -> Dict[str, Any]:
    """Chấm từng dashboard bằng ĐÚNG cổng; có phát hiện/lỗi ⇒ ghi báo cáo để bác sĩ rà. Ba lỗi liền / thiếu khoá ⇒ dừng."""
    if goi is None:
        if _duoi_pytest():
            return {"ket_qua": "bo_qua", "ly_do": "dưới pytest không gọi API thật"}
        goi = _nap_quet(GOC).nap_cong(GOC).check_dashboard_topic_relevance
    ket, loi_lien, dung = [], 0, ""
    for x in can[: cs["chu_de_toi_da_moi_luot"]]:
        kq = goi(str(x["tep"]))
        st, tin = kq.get("status"), str(kq.get("message") or "")
        ket.append({"tep": Path(x["tep"]).name, "chu_de": kq.get("topic") or "", "so_muc": x["so_muc"], "status": st,
                    "off_topic": kq.get("off_topic") or [], "uncertain": kq.get("uncertain") or [], "ly_do": tin[:200]})
        if st == "skipped" and ("ANTHROPIC_API_KEY" in tin or "cài SDK" in tin):
            dung = f"dừng: {tin[:120]}"
            break
        loi_lien = loi_lien + 1 if st == "error" else 0
        if loi_lien >= 3:
            dung = "dừng sau 3 lỗi liền (khoá/tín dụng/mạng?)"
            break
    so_lac = sum(len(k["off_topic"]) for k in ket)
    so_kc = sum(len(k["uncertain"]) for k in ket)
    so_loi = sum(1 for k in ket if k["status"] not in ("ok", "skipped"))
    bao_cao = ghi_bao_cao_chu_de(ket, goc) if (so_lac or so_kc or so_loi) else None
    return {"ket_qua": "loi" if (so_loi or dung) else "ok", "da_cham": len(ket), "con_lai": max(0, len(can) - len(ket)),
            "so_lac": so_lac, "so_khong_chac": so_kc, "so_loi": so_loi, "dung": dung,
            "bao_cao": bao_cao.as_posix() if bao_cao else ""}


def ghi_bao_cao_chu_de(ket: List[Dict[str, Any]], goc: Path = GOC, luc: Optional[dt.datetime] = None) -> Path:
    luc = luc or dt.datetime.now()
    thu_muc = goc / "EBM-Dashboards" / "derivatives"
    thu_muc.mkdir(parents=True, exist_ok=True)
    ten = f"KIEM-CHU-DE-KHI-CAN_{luc:%Y%m%d-%H%M}"
    co_viec = [k for k in ket if k["off_topic"] or k["uncertain"]]
    loi = [k for k in ket if k["status"] not in ("ok", "skipped")]
    d = [f"# Kiểm lạc chủ đề tự động (API khi cần) — {luc:%d/%m/%Y %H:%M}", "",
         f"Đã chấm **{len(ket)} dashboard** có nội dung đổi so với lần kiểm trước · "
         f"**{sum(len(k['off_topic']) for k in ket)} mục NGHI LẠC** · {sum(len(k['uncertain']) for k in ket)} mục "
         f"không chắc · {len(loi)} dashboard không chấm được.", "",
         "> LLM chấm từ tiêu đề + hành động của mục — có sai số. Danh sách ĐỂ BÁC SĨ RÀ: không mục nào bị gỡ, không "
         "dashboard nào bị sửa. Cần bác sĩ kiểm chứng.", ""]
    for k in co_viec:
        d += [f"## {k['tep']}", f"Chủ đề khai báo: *{k['chu_de']}* · {k['so_muc']} mục", ""]
        for x in k["off_topic"]:
            d.append(f"- 🔴 lạc · {x.get('id')} · {str(x.get('title', ''))[:140]} — {str(x.get('reason', ''))[:160]}")
        if k["uncertain"]:
            d.append("- 🟡 không chắc: " + ", ".join(str(i) for i in k["uncertain"]))
        d.append("")
    if loi:
        d += ["## Không chấm được", ""] + [f"- {k['tep']}: {k['ly_do']}" for k in loi] + [""]
    md = thu_muc / f"{ten}.md"
    md.write_text("\n".join(d), encoding="utf-8", newline="\n")
    (thu_muc / f"{ten}.json").write_text(json.dumps({"luc": luc.isoformat(timespec="seconds"), "ket_qua": ket},
                                                    ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    return md


# ─────────────────────────── việc 2 — kiểm đề cương khi đổi ───────────────────────────
def can_de_cuong(goc_mea: Path = GOC_MEA) -> Tuple[List[Dict[str, Any]], str]:
    """(việc cần, lý do KHÔNG đo được). Chỉ báo cáo mà công cụ của repo y khoa KHẲNG ĐỊNH là cũ."""
    duong = goc_mea / "tools" / "duyet_kiem_may_api.py"
    if not duong.is_file():
        return [], "repo y khoa chưa có duyet_kiem_may_api.py (PR y khoa #306 chưa gộp)"
    try:
        tt = _nap("_dkm_api_khi_can", duong).tinh_trang_tat_ca(goc_mea)
    except Exception as exc:  # noqa: BLE001 — bộ đo hỏng phải hiện ra, không được đọc thành «không có việc»
        return [], f"duyet_kiem_may_api lỗi {type(exc).__name__}: {exc}"[:200]
    ra = []
    for t in tt:
        for b in t.get("bao_cao") or []:
            if b.get("cu") is True and b.get("loai") in CONG_CU_DE_CUONG:
                ra.append({"study": t["study"], "loai": b["loai"], "ten": b.get("ten") or b["loai"],
                           "ly_do": str(b.get("ly_do") or "")})
    return ra, ""


def _co_batch_bat_dong_bo(tep: Path) -> bool:
    """Công cụ y khoa đã có Batch bất đồng bộ (`--batch` + `--chi-lay`, y khoa #389) chưa — đọc mã nguồn."""
    try:
        van = tep.read_text(encoding="utf-8")
    except OSError:
        return False
    return '"--batch"' in van and '"--chi-lay"' in van


def chay_de_cuong(can: List[Dict[str, Any]], goc_mea: Path = GOC_MEA,
                  chay: Optional[Callable[[List[str], Path, int], Tuple[int, str]]] = None) -> Dict[str, Any]:
    """Chạy lại công cụ kiểm có báo cáo cũ. Mã 0/1 = chạy xong (1 = có phát hiện cần duyệt); khác = lỗi. Chạm trần ⇒ dừng."""
    if chay is None:
        if _duoi_pytest():
            return {"ket_qua": "bo_qua", "ly_do": "dưới pytest không gọi API thật"}
        chay = _chay_lenh
    py = python_venv() or sys.executable
    ket, dung = [], ""
    for x in can:
        tep = goc_mea / "tools" / CONG_CU_DE_CUONG[x["loai"]]
        lenh = [py, str(tep), "--study", x["study"], "--goi-api"]
        batch = x["loai"] in CO_BATCH_BAT_DONG_BO and _co_batch_bat_dong_bo(tep)
        ma, duoi = chay(lenh + (["--batch"] if batch else []), goc_mea, GIAY_DE_CUONG)
        ghi_chu = ""
        if batch and ma == 3:  # đề cương/lời dặn đổi sau khi nộp ⇒ sổ batch cũ lệch bản: chạy thường lượt này
            ghi_chu = "batch cũ lệch bản hiện hành (sổ batch giữ nguyên — xem Claude Console) ⇒ đã chạy thường"
            ma, duoi = chay(lenh, goc_mea, GIAY_DE_CUONG)
        cho = batch and ma == MA_DANG_CHO_BATCH
        # 21/11/2026: Python SẬP cũng thoát mã 1 (vd help «50%» làm kiem_noi_dung_trich_dan sập trên Python 3.14) —
        # trước đây bị đọc thành «chạy xong, có phát hiện». Mã 1 kèm traceback ⇒ LỖI.
        sap = ma == 1 and ("Traceback (most recent call last)" in duoi  # đuôi chỉ giữ 600 ký tự ⇒ nhận cả dòng File
                           or re.search(r'File ".+", line \d+', duoi) is not None)
        ket.append({"study": x["study"], "loai": x["loai"], "ma_thoat": ma, "ok": (ma in (0, 1) and not sap) or cho,
                    "co_phat_hien": ma == 1 and not sap, "sap": sap, "dang_cho_batch": cho, "ghi_chu": ghi_chu,
                    "duoi": duoi[-200:]})
        # Không phân biệt hoa thường: thông điệp vượt trần chính của cầu nối mở đầu «Trần chi phí Claude API tháng…»
        # (viết hoa) — so khớp phân biệt hoa thường từng bỏ sót nó (đo 18/11/2026 sau khi y khoa #306 gộp).
        if ma not in (0, 1) and any(s in duoi.lower() for s in DAU_HIEU_HET_TRAN):
            dung = ("dừng: tài khoản Claude API hết tín dụng (cầu nối y khoa tự dừng) — nạp thêm ở Claude Console"
                    if any(s in duoi.lower() for s in DAU_HIEU_HET_TIN_DUNG)
                    else "dừng: chạm trần chi phí tháng của cầu nối y khoa")
            break
    so_loi = sum(1 for k in ket if not k["ok"])
    return {"ket_qua": "loi" if so_loi else "ok", "da_chay": len(ket), "so_loi": so_loi, "dung": dung,
            "dang_cho_batch": sum(1 for k in ket if k.get("dang_cho_batch")), "chi_tiet": ket}


# ─────────────────────────── việc 3 — CAFÉ-S khi agent an toàn đổi ───────────────────────────
def _luot_cafes_moi_nhat(goc: Path = GOC) -> Optional[Tuple[str, Path, Dict[str, Any]]]:
    hop_le = []
    for p in (goc / "tools" / "eval" / "agent_outputs").glob("cafes_api_*/_ket_qua.json"):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(d, dict) and d.get("luc"):
            hop_le.append((str(d["luc"]), p, d))
    return max(hop_le, key=lambda x: x[0]) if hop_le else None


def agent_doi(goc: Path = GOC) -> Tuple[List[str], Optional[str]]:
    """(agent đã đổi so với lượt đo CAFÉ-S gần nhất, mốc lượt đó). Không có lượt / vân tay ⇒ ([], None)."""
    m = _luot_cafes_moi_nhat(goc)
    if not m:
        return [], None
    luc, _p, d = m
    vt = d.get("van_tay_agent")
    if not isinstance(vt, dict) or not vt:
        return [], luc
    doi = []
    for ten, h in sorted(vt.items()):
        try:
            hien = hashlib.sha256((goc / ".claude" / "agents" / f"{ten}.md").read_bytes()).hexdigest()
        except OSError:
            hien = ""
        if hien != h:
            doi.append(ten)
    return doi, luc


def can_cafes(cs: Dict[str, Any], goc: Path = GOC, bay_gio: Optional[dt.datetime] = None) -> Tuple[Optional[Dict], str]:
    """(việc cần hoặc None, ghi chú). Chưa có lượt đo nào ⇒ lượt đầu do bác sĩ quyết, không tự chạy."""
    doi, luc = agent_doi(goc)
    if luc is None:
        return None, "chưa có lượt đo CAFÉ-S nào — lượt đầu do bác sĩ quyết"
    if not doi:
        return None, ""
    try:
        moc = dt.datetime.fromisoformat(luc[:19])
    except ValueError:
        return None, f"lượt đo gần nhất có mốc không đọc được ({luc})"
    som_nhat = moc + dt.timedelta(days=cs["cafes_cach_ngay_toi_thieu"])
    if (bay_gio or dt.datetime.now()) < som_nhat:
        return None, (f"agent đổi ({', '.join(doi)}) — chờ đủ {cs['cafes_cach_ngay_toi_thieu']} ngày từ lượt đo "
                      f"{moc:%d/%m}, sớm nhất {som_nhat:%d/%m/%Y}")
    return {"agent_doi": doi, "luc_do_truoc": luc}, ""


def chay_cafes(viec: Dict[str, Any], goc: Path = GOC,
               chay: Optional[Callable[[List[str], Path, int], Tuple[int, str]]] = None) -> Dict[str, Any]:
    if chay is None:
        if _duoi_pytest():
            return {"ket_qua": "bo_qua", "ly_do": "dưới pytest không gọi API thật"}
        chay = _chay_lenh
    ma, duoi = chay([python_venv() or sys.executable, str(goc / "tools" / "eval" / "cafes_suite.py"), "--api"],
                    goc, GIAY_CAFES)
    m = _luot_cafes_moi_nhat(goc)
    cong = ((m[2].get("bao_cao") or {}).get("CRITICAL_GATE") if m and m[0] > viec["luc_do_truoc"] else None)
    return {"ket_qua": "ok" if (ma == 0 and cong) else "loi", "ma_thoat": ma, "critical_gate": cong or "",
            "agent_doi": viec["agent_doi"], "duoi": duoi[-200:]}


# ─────────────────────────── điều phối ───────────────────────────
def xet(cs: Dict[str, Any], chi: Tuple[str, ...] = VIEC, goc: Path = GOC, goc_mea: Path = GOC_MEA,
        bay_gio: Optional[dt.datetime] = None) -> Dict[str, Dict[str, Any]]:
    """Phát hiện việc cần cho từng loại (miễn phí, không gọi API)."""
    ra: Dict[str, Dict[str, Any]] = {}
    if "chu_de" in chi:
        try:
            c = can_chu_de(goc)
            ra["chu_de"] = {"can": c, "uoc_usd": sum(x["uoc_usd"] for x in c[: cs["chu_de_toi_da_moi_luot"]]),
                            "ghi_chu": "", "do_duoc": True}
        except Exception as exc:  # noqa: BLE001 — bộ đo hỏng phải hiện ra, không được đọc thành «không có việc»
            ra["chu_de"] = {"can": [], "uoc_usd": 0.0, "do_duoc": False,
                            "ghi_chu": f"không đo được: {type(exc).__name__}: {exc}"[:200]}
    if "de_cuong" in chi:
        c, ly = can_de_cuong(goc_mea)
        ra["de_cuong"] = {"can": c, "uoc_usd": 0.15 * len(c), "ghi_chu": ly, "do_duoc": not ly}
    if "cafes" in chi:
        v, ly = can_cafes(cs, goc, bay_gio)
        ra["cafes"] = {"can": [v] if v else [], "uoc_usd": 3.0 if v else 0.0, "ghi_chu": ly, "do_duoc": True}
    return ra


def chay(chi: Tuple[str, ...] = VIEC, goc: Path = GOC, goc_mea: Path = GOC_MEA, goi_cong=None, chay_lenh=None,
         bay_gio: Optional[dt.datetime] = None, duyet: Optional[str] = None) -> int:
    """Chạy các việc cần. 22/11/2026 (bác sĩ: «gọi Claude API khi tôi duyệt»): việc có `tu_chay` = false chỉ chạy khi
    có `duyet` — NGUYÊN VĂN lời duyệt của bác sĩ trong chat — và lời đó được ghi vào sổ cùng ước chi phí."""
    if duyet is not None and len(duyet.strip()) < 2:
        print("❌ --duyet phải là nguyên văn lời duyệt của bác sĩ (không rỗng) — không chạy, không chi tiền.")
        return 2
    cs = doc_chinh_sach()
    if cs is None:
        print("⚪ Chính sách sync/api-khi-can.json vắng/hỏng — cơ chế TẮT, không chạy việc nào (không chi tiền).")
        return 2
    if not lay_khoa():
        print("⏭ Một lượt API khi cần khác đang chạy — bỏ qua lượt này.")
        return 0
    try:
        bay_gio = bay_gio or dt.datetime.now()
        so = doc_so()
        so["lan_xet_cuoi"] = bay_gio.isoformat(timespec="seconds")
        ghi_so(so)
        phat_hien = xet(cs, chi, goc, goc_mea, bay_gio)
        luot: Dict[str, Any] = {"luc": bay_gio.isoformat(timespec="seconds"), "viec": {}}
        if duyet is not None:
            luot["duyet"] = {"loi": duyet.strip(), "chi": list(chi),
                             "uoc_usd": round(sum(float((phat_hien.get(v) or {}).get("uoc_usd") or 0) for v in chi), 2)}
        for v in chi:
            p = phat_hien.get(v) or {"can": [], "ghi_chu": "", "do_duoc": True}
            if not cs["tu_chay"][v] and duyet is None:
                luot["viec"][v] = {"ket_qua": "tat", "so_can": len(p["can"])}
                continue
            if not p["can"]:
                luot["viec"][v] = {"ket_qua": "khong_can" if p["do_duoc"] else "khong_do_duoc", "ghi_chu": p["ghi_chu"]}
                continue
            if v == "chu_de":
                luot["viec"][v] = chay_chu_de(p["can"], cs, goc, goi_cong)
            elif v == "de_cuong":
                luot["viec"][v] = chay_de_cuong(p["can"], goc_mea, chay_lenh)
            else:
                luot["viec"][v] = chay_cafes(p["can"][0], goc, chay_lenh)
        so = doc_so()
        so["luot"].append(luot)
        ghi_so(so)
    finally:
        tra_khoa()
    loi = False
    for v, r in luot["viec"].items():
        loi = loi or r.get("ket_qua") == "loi"
        print(f"  {TEN_VIEC[v]}: {_tom_tat(r)}")
    print("Cần bác sĩ kiểm chứng (kết quả kiểm máy là gợi ý, không tự sửa nội dung nào).")
    return 1 if loi else 0


def _tom_tat(r: Dict[str, Any]) -> str:
    kq = r.get("ket_qua")
    if kq == "tat":
        return f"TẮT theo chính sách ({r.get('so_can', 0)} việc cần)"
    if kq in ("khong_can", "khong_do_duoc"):
        return ("⚪ " if kq == "khong_do_duoc" else "không có việc") + (f" — {r['ghi_chu']}" if r.get("ghi_chu") else "")
    if kq == "bo_qua":
        return f"bỏ qua — {r.get('ly_do')}"
    if "da_cham" in r:
        s = (f"đã chấm {r['da_cham']} dashboard · {r['so_lac']} mục nghi lạc · {r['so_khong_chac']} không chắc · "
             f"{r['so_loi']} lỗi")
        s += f" · còn {r['con_lai']} để lượt sau" if r.get("con_lai") else ""
        return s + (f" · {r['dung']}" if r.get("dung") else "") + (f" · báo cáo {r['bao_cao']}" if r.get("bao_cao") else "")
    if "da_chay" in r:
        return f"đã chạy {r['da_chay']} công cụ · {r['so_loi']} lỗi" + (f" · {r['dung']}" if r.get("dung") else "")
    return f"mã {r.get('ma_thoat')} · cổng critical {r.get('critical_gate') or '?'}"


def chay_kho(chi: Tuple[str, ...] = VIEC) -> int:
    cs = doc_chinh_sach()
    if cs is None:
        print("⚪ Chính sách sync/api-khi-can.json vắng/hỏng — cơ chế TẮT.")
        return 2
    print("API KHI CẦN — CHẠY KHÔ (không gọi API). Thêm --chay để chạy các việc chính sách cho phép.")
    for v, p in xet(cs, chi).items():
        tu = "TỰ CHẠY" if cs["tu_chay"][v] else "chỉ báo"
        print(f"  {TEN_VIEC[v]} [{tu}]: {len(p['can'])} việc cần · ước ~{p['uoc_usd']:.2f} USD"
              + (f" — {p['ghi_chu']}" if p["ghi_chu"] else ""))
        for x in p["can"][:8]:
            print(f"     · {_mo_ta_viec(x)}")
    return 0


def _mo_ta_viec(x: Dict[str, Any]) -> str:
    if "tep" in x:
        return f"{Path(x['tep']).name} ({x['so_muc']} mục)"
    if "study" in x:
        return f"{x['study']} · {x['ten']} — {x['ly_do']}"
    return "agent đổi: " + ", ".join(x.get("agent_doi", []))


def phong_nen(im_khi_on: bool = False, bay_gio: Optional[dt.datetime] = None) -> int:
    """Cho hook đầu phiên: đủ giờ từ lần xét trước ⇒ phóng `--chay` ở NỀN rồi trả lại ngay. Không bao giờ chặn phiên."""
    if os.environ.get("CLAUDE_CODE_REMOTE") == "true" or _duoi_pytest():
        return 0
    cs = doc_chinh_sach()
    if cs is None:
        print("⚪ API khi cần: chính sách sync/api-khi-can.json vắng/hỏng — cơ chế TẮT.")
        return 0
    if not any(cs["tu_chay"].values()) or khoa_dang_giu(bay_gio):
        return 0
    try:
        cuoi = dt.datetime.fromisoformat(str(doc_so().get("lan_xet_cuoi"))[:19])
        if (bay_gio or dt.datetime.now()) - cuoi < dt.timedelta(hours=cs["nen_cach_gio_toi_thieu"]):
            return 0
    except ValueError:
        pass
    kw: Dict[str, Any] = {"cwd": str(GOC), "stdin": subprocess.DEVNULL}
    if os.name == "nt":
        kw["creationflags"] = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    else:
        kw["start_new_session"] = True
    try:
        with open(str(SO) + ".log", "a", encoding="utf-8") as log:
            log.write(f"\n=== {dt.datetime.now().isoformat(timespec='seconds')} phóng --chay từ hook ===\n")
            log.flush()
            subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--chay"], stdout=log,
                             stderr=subprocess.STDOUT, **kw)
    except OSError as exc:
        print(f"🟠 API khi cần: không phóng được lượt nền ({exc})")
        return 0
    if not im_khi_on:
        print("🤖 API khi cần: đã phóng lượt xét ở nền (nhật ký ~/.ebm-api-khi-can.json.log).")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Tự chạy API Claude khi cần (chính sách sync/api-khi-can.json).")
    nhom = ap.add_mutually_exclusive_group()
    nhom.add_argument("--chay", action="store_true", help="chạy các việc cần mà chính sách cho phép (TỐN TIỀN API)")
    nhom.add_argument("--nen", action="store_true", help="cho hook: đủ giờ ⇒ phóng --chay ở nền rồi trả lại ngay")
    ap.add_argument("--duyet", default=None,
                    help="NGUYÊN VĂN lời duyệt của bác sĩ trong chat (22/11/2026: «gọi Claude API khi tôi duyệt») — chỉ "
                         "dùng với --chay; thiếu thì việc có tu_chay=false không chạy")
    ap.add_argument("--chi", default=",".join(VIEC), help="giới hạn việc: chu_de,de_cuong,cafes")
    ap.add_argument("--im-khi-on", action="store_true", help="im lặng khi không có gì đáng báo (dùng với --nen)")
    a = ap.parse_args(argv)
    chi = tuple(v for v in (s.strip() for s in a.chi.split(",")) if v)
    sai = [v for v in chi if v not in VIEC]
    if sai:
        print(f"❌ --chi không nhận: {', '.join(sai)} (chỉ {', '.join(VIEC)})")
        return 2
    if a.nen:
        return phong_nen(a.im_khi_on)
    if a.duyet is not None and not a.chay:
        print("❌ --duyet chỉ dùng cùng --chay.")
        return 2
    if a.chay:
        return chay(chi, duyet=a.duyet)
    return chay_kho(chi)


if __name__ == "__main__":
    raise SystemExit(main())
