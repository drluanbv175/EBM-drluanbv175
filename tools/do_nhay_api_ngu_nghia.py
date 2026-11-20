#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ĐO ĐỘ BẮT LỖI của bộ kiểm ngữ nghĩa Claude API trên CÙNG đột biến tổng hợp tất định của luật cứng (20/11/2026).

VÌ SAO CÓ
=========
Bác sĩ (20/11/2026): «Kiểm ngữ nghĩa chưa đo được độ bắt lỗi. Bộ kiểm Claude API hãy hoàn thiện; giải quyết vấn đề này một
cách triệt để». Luật cứng K1–K4 đã có thước đo độ nhạy KHÔNG phụ thuộc nhãn bác sĩ — đột biến tổng hợp có nhãn theo cấu trúc
(`tools/do_nhay_kiem_ngu_nghia.py`, báo cáo 14/11: K1 99% · K3b 1% · K4b 25%). Bộ kiểm API (`tools/kiem_ngu_nghia_api.py`)
chưa từng đi qua thước đo đó — chỉ chạy trên 56 đột biến tự do đang chờ bác sĩ duyệt ⇒ «chưa đo được». Công cụ này đặt bộ
kiểm API lên ĐÚNG cùng đột biến (cùng hạt giống, cùng bộ sinh, cùng nguồn), đo độ bắt lỗi kèm KTC 95%, và so CẶP với luật
cứng trên từng đột biến (McNemar).

CÁCH LÀM
========
1. Sinh đột biến bằng chính `do_nhay_kiem_ngu_nghia` (không đổi bộ sinh): mục `apply` của dashboard ĐÃ PASS + tóm tắt
   PubMed trong bộ đệm ngoài git; luật cứng chấm từng đột biến như báo cáo 14/11.
2. Lớp trong tầm API và trục phải chuyển false (`LOP_API`): K1 đổi quần thể → quần thể · K2 đổi ngưỡng trong quần thể →
   quần thể · K2 đổi ngưỡng trong HÀNH ĐỘNG → điều kiện (luật cứng đọc từ 20/11/2026) · K3b rụng điều kiện trong mục → điều kiện
   · K4 nguồn nói ngược → chiều · K4b mục đảo sang «không làm» → chiều. Ngoài tầm API (không đo): K2 cỡ mẫu n=, K3 rụng ở
   bản xuất (API không đọc bản xuất).
3. Mẫu PHÂN TẦNG tất định: tối đa `--so-mau` đột biến mỗi lớp (thứ tự theo sha256 của hạt giống + mục + lớp). Đối chứng
   GHÉP CẶP = chính mục gốc của từng đột biến (mục thật + nguồn thật). Đột biến chỉ tính «bắt» khi API phán trục đích của
   BẢN GỐC không phải false mà của BẢN ĐỘT BIẾN là false — gốc đã bị nghi thì không quy được cho đột biến (cùng luật với
   điều kiện tiên quyết K4 của do_nhay).
4. Chia DEV/TEST theo PMID (sha256 hạt giống + PMID; mục không PMID ⇒ theo mục): gốc, mọi đột biến của nó VÀ mọi phiên bản
   dashboard trích cùng một bài luôn cùng một tập. Sửa prompt chỉ nhìn DEV; số báo cáo để quyết là số trên TEST — tránh «học
   tủ» trên chính tập đo. (Trước 20/11/2026 chiều chia theo MỤC = dashboard + chỉ số: cùng một PMID ở hai phiên bản dashboard
   có thể rơi vào hai tập ⇒ rò rỉ DEV→TEST — góp ý rà độc lập. `--chia-theo muc` tái lập cách cũ.)
5. Báo cáo không chép văn bản nguồn hay lý do của mô hình (bàn về văn bản có bản quyền) — chỉ định danh, lớp, mã phán quyết.

GIỚI HẠN NÓI TRƯỚC
==================
* Đột biến TỔNG HỢP — không thay bộ vàng do bác sĩ gắn nhãn; lỗi thật có thể khác hình dạng. Báo động trên đối chứng là CẬN
  TRÊN của báo động giả (mục thật chưa được gắn nhãn đúng/sai).
* Công cụ KHÔNG đổi chế độ chặn, KHÔNG sửa dashboard, KHÔNG đổi `decision`/`gradeLevel`, KHÔNG gắn nhãn bộ vàng.
* Gọi API tính phí: chạy khô mặc định (in số lượt cần gọi + ước chi phí); `--goi-api` mới gọi, qua cầu nối dùng chung
  `medical-ebm-automation/tools/api_claude_nc.py` (trần chi phí tháng kiểm TRƯỚC khi gửi, sổ chi phí nguồn «do_nhay_api»).

Dùng:
    python3 tools/do_nhay_api_ngu_nghia.py                                   # chạy khô: số lượt cần gọi, ước chi phí
    python3 tools/do_nhay_api_ngu_nghia.py --goi-api --so-mau 40             # gọi thật (tính phí), dùng lại bộ đệm
    python3 tools/do_nhay_api_ngu_nghia.py --phien-ban 2026-11-20b --chi-tap test --goi-api   # đo prompt mới trên TEST
    python3 tools/do_nhay_api_ngu_nghia.py --ghi                             # ghi báo cáo từ bộ đệm (không gọi)
Báo cáo: quality/eval/kiem-cheo-ngu-nghia/do-nhay-api-<YYYYMMDD>.json + .md
Mã thoát: 0 = mọi lớp trong tầm API đều có số đo · 1 = chỉ đo được một phần · 2 = không đo được gì. Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import re
import importlib.util
import json
import math
import os
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
THU_MUC_BAO_CAO = REPO / "quality" / "eval" / "kiem-cheo-ngu-nghia"
NGUON = "do_nhay_api"
SO_MAU_MAC_DINH = 40
TRUC = ("dung_quan_the", "dung_chieu", "du_dieu_kien")
TEN_TRUC = {"dung_quan_the": "quần thể", "dung_chieu": "chiều", "du_dieu_kien": "điều kiện"}
LOP_API = {
    "K1_quan_the": ("dung_quan_the", "K1 · đổi nhãn quần thể"),
    "K2_nguong": ("dung_quan_the", "K2 · đổi ngưỡng số trong quần thể"),
    "K2_nguong_hanh_dong": ("du_dieu_kien", "K2 · đổi ngưỡng số trong HÀNH ĐỘNG"),
    "K3_rung_trong_muc": ("du_dieu_kien", "K3b · rụng điều kiện NGAY TRONG MỤC"),
    "K4_nguon_nguoc": ("dung_chieu", "K4 · nguồn nói NGƯỢC chiều mục"),
    "K4_muc_dao": ("dung_chieu", "K4b · mục đảo sang «không làm»"),
}
NGOAI_TAM_API = {"K2_co_mau": "API không chấm con số cỡ mẫu", "K3_rung_ban_xuat": "API không đọc bản xuất"}
KQ = ("bat", "bat_lech", "lot_xanh", "lot_trang", "goc_da_nghi", "chua_cham")
Z95 = 1.959963984540054


def _nap(ten: str, duong: Path):
    sp = importlib.util.spec_from_file_location(ten, duong)
    if sp is None or sp.loader is None:
        raise ImportError(str(duong))
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


def _dn():
    return _nap("_dna_dn", Path(__file__).resolve().parent / "do_nhay_kiem_ngu_nghia.py")


def _api():
    return _nap("_dna_api", Path(__file__).resolve().parent / "kiem_ngu_nghia_api.py")


def _duoi_pytest() -> bool:
    return "PYTEST_CURRENT_TEST" in os.environ and os.environ.get("EBM_KIEM_API_THAT") != "1"


def wilson(k: int, n: int) -> tuple[float, float] | None:
    if not n:
        return None
    p = k / n
    mau = 1 + Z95 ** 2 / n
    tam = (p + Z95 ** 2 / (2 * n)) / mau
    nua = Z95 * math.sqrt(p * (1 - p) / n + Z95 ** 2 / (4 * n * n)) / mau
    return max(0.0, tam - nua), min(1.0, tam + nua)


def mcnemar_chinh_xac(b: int, c: int) -> float | None:
    """p hai phía của McNemar CHÍNH XÁC (nhị thức trên cặp bất đồng b, c). Không có cặp bất đồng ⇒ None."""
    n = b + c
    if not n:
        return None
    k = min(b, c)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def _bam(*phan) -> str:
    return hashlib.sha256("|".join(str(x) for x in phan).encode("utf-8")).hexdigest()


def tap_cua(hat: int, dashboard: str, chi_so, pmid: str | None = None) -> str:
    """DEV/TEST theo PMID khi có (mọi phiên bản dashboard trích cùng bài ⇒ cùng tập), không có PMID ⇒ theo MỤC."""
    pm = str(pmid or "").strip()
    if re.fullmatch(r"\d{6,9}", pm):
        return "dev" if int(_bam(hat, "tach-pmid", pm)[:8], 16) % 2 == 0 else "test"
    return "dev" if int(_bam(hat, "tach", dashboard, chi_so)[:8], 16) % 2 == 0 else "test"


CHIA_THEO = "pmid"                      # "muc" ⇒ tái lập cách chia trước 20/11/2026 chiều


def tap_dot_bien(hat: int, d: dict, goc_theo_khoa: dict, chia_theo: str | None = None) -> str:
    """Tập của một đột biến theo cách chia đang dùng (PMID lấy từ MỤC GỐC — đột biến không đổi PMID)."""
    if (chia_theo or CHIA_THEO) == "muc":
        return tap_cua(hat, d["dashboard"], d["_khoa"][1])
    g = goc_theo_khoa.get(tuple(d["_khoa"])) or {}
    return tap_cua(hat, d["dashboard"], d["_khoa"][1], str((g.get("muc") or {}).get("pmid") or ""))


def _hien_api(it: dict) -> tuple:
    return tuple(str(it.get(k) or "") for k in ("title", "population", "action"))


# ───────────────────────── chọn mẫu ─────────────────────────

def chon_mau(dot_bien: list[dict], goc_theo_khoa: dict, so_mau: int, hat: int) -> tuple[list[dict], dict]:
    """Mẫu phân tầng tất định. Bỏ đột biến API KHÔNG nhìn thấy (ba trường mục + nguồn đều như gốc). Trả (mẫu, thống kê)."""
    tk: dict[str, dict] = {}
    mau: list[dict] = []
    for lop in LOP_API:
        ds = [d for d in dot_bien if d.get("lop") == lop]
        thay = []
        khong_thay = 0
        for d in ds:
            g = goc_theo_khoa.get(tuple(d["_khoa"]))
            if g is None:
                continue
            if _hien_api(d["muc_dot_bien"]) == _hien_api(g["muc"]) and d.get("nguon_dot_bien") == g["nguon"]:
                khong_thay += 1
                continue
            thay.append(d)
        thay.sort(key=lambda d: _bam(hat, "mau", d["dashboard"], d["_khoa"][1], lop, d.get("bien_the")))
        chon = thay[:max(0, so_mau)]
        tk[lop] = {"co_san": len(ds), "api_khong_thay": khong_thay, "chon": len(chon)}
        mau += chon
    return mau, tk


def khoa_phan_b(bv: dict | None, bvk) -> tuple[set, set]:
    """Mục THẬT của bộ vàng còn chờ nhãn (phần B — tập kiểm độc lập): ({(dashboard, id)}, {(pmid, hành động chuẩn hoá)}).
    Rà độc lập 20/11/2026: 31 đột biến trong mẫu sinh từ đúng các mục này ⇒ phải loại khỏi số đo."""
    if not bv:
        return set(), set()
    cho = [m for m in bv.get("muc") or [] if (m.get("nguon_muc") or "that") == "that" and not bvk._co_nhan(m)]
    return ({(str(m.get("dashboard") or ""), str(m.get("id") or "")) for m in cho},
            {(str(m.get("pmid") or "").strip(), bvk.chuan(str(m.get("action") or ""))) for m in cho})


def loai_phan_b(mau: list[dict], goc_theo_khoa: dict, khoa: tuple[set, set], bvk) -> tuple[list[dict], dict]:
    """(mẫu đã loại đột biến sinh từ mục phần B, {lớp: số bị loại})."""
    theo_id, theo_nd = khoa
    giu, bo = [], {}
    for d in mau:
        g = goc_theo_khoa[tuple(d["_khoa"])]["muc"]
        if (d["dashboard"], str(g.get("id") or "")) in theo_id or \
                (str(g.get("pmid") or "").strip(), bvk.chuan(str(g.get("action") or ""))) in theo_nd:
            bo[d["lop"]] = bo.get(d["lop"], 0) + 1
            continue
        giu.append(d)
    return giu, bo


# ───────────────────────── gọi API (có bộ đệm) ─────────────────────────

def tep_bo_dem() -> Path:
    return _api()._bvk().goc_du_lieu("EBM-Dashboards") / "derivatives" / "do-nhay-api-ngu-nghia.json"


def doc_bo_dem(tep: Path) -> dict:
    try:
        d = json.loads(Path(tep).read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def ghi_bo_dem(tep: Path, dem: dict) -> None:
    if _duoi_pytest() and Path(tep).resolve() == tep_bo_dem().resolve():
        raise RuntimeError("dưới pytest không ghi bộ đệm đo API thật (đặt EBM_KIEM_API_THAT=1 để đo thật)")
    tep = Path(tep)
    tep.parent.mkdir(parents=True, exist_ok=True)
    tam = tep.with_name(tep.name + ".tam")
    tam.write_text(json.dumps(dem, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tam, tep)


KHO_TOAN_VAN: Path | None = None       # đặt ở main() khi phiên bản prompt ghép đoạn toàn văn
QUYEN_FN = None                        # hàm quyền gửi theo sổ uỷ quyền của đúng thư mục dashboard (đặt ở main())
_BO_NHO_DOAN: dict = {}


def van_ban(it: dict, raw: str, A, kqtc, phien_ban: str) -> tuple[str, str]:
    """(tóm tắt gửi đi, đoạn toàn văn) — đoạn chỉ khi phiên bản prompt dùng toàn văn và tệp có quyền gửi."""
    tt = A.than_tom_tat(raw, kqtc)
    if phien_ban not in getattr(A, "PHIEN_BAN_TOAN_VAN", ()) or KHO_TOAN_VAN is None:
        return tt, ""
    return tt, A.doan_toan_van(it, KHO_TOAN_VAN, bo_nho=_BO_NHO_DOAN, quyen_fn=QUYEN_FN,
                               co_bang=phien_ban in getattr(A, "PHIEN_BAN_CO_BANG", ()))[0]


def khoa(it: dict, raw: str, A, kqtc, mdl: str, phien_ban: str) -> str:
    tt, doan = van_ban(it, raw, A, kqtc, phien_ban)
    return A.khoa_muc(it, tt, mdl, phien_ban, doan)


def lap_yeu_cau(mau: list[dict], goc_theo_khoa: dict, A, kqtc, mdl: str, phien_ban: str) -> dict:
    """{khoá bộ đệm: (mục, tóm tắt, đoạn toàn văn)} cho mọi đột biến trong mẫu + mục gốc của chúng (khử trùng)."""
    ra: dict[str, tuple[dict, str, str]] = {}
    for d in mau:
        g = goc_theo_khoa[tuple(d["_khoa"])]
        for it, raw in ((d["muc_dot_bien"], d.get("nguon_dot_bien")), (g["muc"], g["nguon"])):
            if not raw:
                continue
            tt, doan = van_ban(it, raw, A, kqtc, phien_ban)
            ra.setdefault(A.khoa_muc(it, tt, mdl, phien_ban, doan), (it, tt, doan))
    return ra


def goi_thieu(yeu_cau: dict, dem: dict, *, A, cau_noi, client, mdl: str, phien_ban: str, tep: Path,
              toi_da: int | None = None) -> dict:
    """Gọi các khoá CHƯA có trong bộ đệm. Trần tháng/khoá/mạng ⇒ dừng; kết quả hỏng một mục ⇒ ghi lỗi, đi tiếp."""
    viec = [(k, it, tt, doan) for k, (it, tt, doan) in yeu_cau.items() if k not in dem]
    if toi_da is not None:
        viec = viec[:max(0, toi_da)]
    ok, loi, dung = 0, [], ""
    for k, it, tt, doan in viec:
        try:
            kq = cau_noi.goi(A.dung_noi_dung(it, tt, doan), he_thong=A.he_thong(phien_ban), model=mdl, effort="low",
                             client=client, cache_he_thong=True, nguon=NGUON)
            tra = A.doc_tra_loi(kq.van_ban, cau_noi.doc_json)
        except cau_noi.LoiCucBo as exc:
            dung = f"{type(exc).__name__}: {exc}"
            break
        except (cau_noi.KetQuaHong, ValueError) as exc:
            loi.append(str(exc)[:120])
            continue
        except cau_noi.LoiApi as exc:
            dung = f"{type(exc).__name__}: {exc}"
            break
        dem[k] = {"ket_qua": tra, "model": kq.model, "prompt": phien_ban, "toan_van": bool(doan),
                  "luc": dt.datetime.now().isoformat(timespec="seconds"),
                  "token": {"vao": kq.token_vao, "ra": kq.token_ra, "cache_doc": kq.token_cache_doc}}
        ghi_bo_dem(tep, dem)
        ok += 1
    if viec:
        cau_noi.ghi_nhat_ky_api("ok" if not loi and not dung else "loi", dung or (loi[0] if loi else ""), ok, nguon=NGUON)
    return {"can_goi": len(viec), "da_goi": ok, "loi": loi, "dung": dung}


# ───────────────────────── chấm ─────────────────────────

def goc_phan_duoc(d: dict, goc: dict, R: dict, A, kqtc, mdl: str, phien_ban: str) -> bool:
    """Bản GỐC có được phán (true/false, không null) ở trục đích không — tức nguồn gửi đi đủ thông tin cho trục đó."""
    x = R.get(khoa(goc["muc"], goc["nguon"], A, kqtc, mdl, phien_ban))
    return isinstance(x, dict) and (x.get("ket_qua") or {}).get(LOP_API[d["lop"]][0]) is not None


def cham(d: dict, goc: dict, R: dict, A, kqtc, mdl: str, phien_ban: str) -> str:
    truc = LOP_API[d["lop"]][0]

    def kq(it, raw):
        if not raw:
            return None
        x = R.get(khoa(it, raw, A, kqtc, mdl, phien_ban))
        return x.get("ket_qua") if isinstance(x, dict) else None
    o, r = kq(goc["muc"], goc["nguon"]), kq(d["muc_dot_bien"], d.get("nguon_dot_bien"))
    if o is None or r is None:
        return "chua_cham"
    if o.get(truc) is False:
        return "goc_da_nghi"
    if r.get(truc) is False:
        return "bat"
    if any(r.get(t) is False and o.get(t) is not False for t in TRUC if t != truc):
        return "bat_lech"
    return "lot_trang" if r.get(truc) is None else "lot_xanh"


def _o(ds: list[str], luat: list[str] | None = None, phan_duoc: list[bool] | None = None) -> dict:
    dem = {k: ds.count(k) for k in KQ}
    n_tinh = len(ds) - dem["goc_da_nghi"] - dem["chua_cham"]
    ra = {"n": len(ds), "n_tinh": n_tinh, **dem, "do_nhay": (dem["bat"] / n_tinh) if n_tinh else None,
          "ktc95": wilson(dem["bat"], n_tinh)}
    if phan_duoc is not None:                      # chỉ đột biến mà bản gốc được phán ở trục đích (nguồn đủ thông tin)
        x = [a for a, pd in zip(ds, phan_duoc) if pd and a not in ("goc_da_nghi", "chua_cham")]
        k = x.count("bat")
        ra["phan_duoc"] = {"n": len(x), "bat": k, "do_nhay": (k / len(x)) if x else None, "ktc95": wilson(k, len(x))}
    if luat is not None:
        cap = [(a, b) for a, b in zip(ds, luat) if a not in ("goc_da_nghi", "chua_cham")]
        ca_hai = sum(1 for a, b in cap if a == "bat" and b == "bat")
        chi_api = sum(1 for a, b in cap if a == "bat" and b != "bat")
        chi_luat = sum(1 for a, b in cap if a != "bat" and b == "bat")
        k_luat = sum(1 for _, b in cap if b == "bat")
        ra["luat_cung"] = {"n": len(cap), "bat": k_luat, "do_nhay": (k_luat / len(cap)) if cap else None,
                           "ktc95": wilson(k_luat, len(cap))}
        ra["cap"] = {"ca_hai": ca_hai, "chi_api": chi_api, "chi_luat_cung": chi_luat,
                     "ca_hai_lot": len(cap) - ca_hai - chi_api - chi_luat,
                     "p_mcnemar": mcnemar_chinh_xac(chi_api, chi_luat)}
        # Bộ năm chạy CẢ HAI (④-ter luật cứng + ④-quinquies API) ⇒ độ bắt lỗi của hệ = một trong hai bắt.
        k_kh = ca_hai + chi_api + chi_luat
        ra["ket_hop"] = {"n": len(cap), "bat": k_kh, "do_nhay": (k_kh / len(cap)) if cap else None,
                         "ktc95": wilson(k_kh, len(cap))}
    return ra


def doi_chung(mau: list[dict], goc_theo_khoa: dict, R: dict, A, kqtc, mdl: str, phien_ban: str, bo: dict, DN) -> dict:
    """Báo động trên mục GỐC (mỗi mục một lần): API theo trục + bất kỳ trục; luật cứng (K1/K2/K3b/K4/K4b) trên cùng mục."""
    da: set = set()
    n = bat_ky = luat = 0
    theo = {t: 0 for t in TRUC}
    null = {t: 0 for t in TRUC}
    for d in mau:
        k = tuple(d["_khoa"])
        if k in da:
            continue
        da.add(k)
        g = goc_theo_khoa[k]
        x = R.get(khoa(g["muc"], g["nguon"], A, kqtc, mdl, phien_ban))
        if not isinstance(x, dict):
            continue
        o = x["ket_qua"]
        n += 1
        bat_ky += any(o.get(t) is False for t in TRUC)
        for t in TRUC:
            theo[t] += o.get(t) is False
            null[t] += o.get(t) is None
        r0 = g.get("ket_qua_luat")
        luat += bool(r0) and any(DN.chu_ky_bao(r0, p) for p in DN.PHEP_NGUON)
    return {"n": n, "api_bat_ky": bat_ky, "api_ty_le": (bat_ky / n) if n else None, "api_ktc95": wilson(bat_ky, n),
            "api_theo_truc": theo, "api_null_theo_truc": null, "luat_cung_bao": luat,
            "luat_cung_ty_le": (luat / n) if n else None}


def tong_hop(mau: list[dict], goc_theo_khoa: dict, R: dict, A, kqtc, mdl: str, phien_ban: str, hat: int, bo: dict, DN,
             chi_tap: str | None = None) -> dict:
    ra: dict = {"theo_tap": {}, "chi_tap": chi_tap}
    for tap in ("dev", "test", "tat_ca"):
        if chi_tap and tap != chi_tap:                 # đo một tập ⇒ báo cáo CHỈ tập đó (không trộn mục chưa chấm)
            continue
        ds = [d for d in mau if tap == "tat_ca" or tap_dot_bien(hat, d, goc_theo_khoa) == tap]
        lop = {}
        for ten in LOP_API:
            x = [d for d in ds if d["lop"] == ten]
            kq_api = [cham(d, goc_theo_khoa[tuple(d["_khoa"])], R, A, kqtc, mdl, phien_ban) for d in x]
            pd = [goc_phan_duoc(d, goc_theo_khoa[tuple(d["_khoa"])], R, A, kqtc, mdl, phien_ban) for d in x]
            lop[ten] = _o(kq_api, [d.get("ket_qua") for d in x], pd)
        ra["theo_tap"][tap] = {"lop": lop, "doi_chung": doi_chung(ds, goc_theo_khoa, R, A, kqtc, mdl, phien_ban, bo, DN)}
    return ra


# ───────────────────────── dữ liệu ─────────────────────────

def nap_du_lieu(thu_muc: Path, *, hat: int, DN, tep_dem_nguon: Path | None = None) -> dict:
    """Sinh đột biến + chấm luật cứng ĐÚNG như do_nhay (ngoại tuyến, bộ đệm tóm tắt). Trả {dot_bien, goc_theo_khoa, bo}."""
    bo = DN.bo_kiem_that()
    doc = DN._k3().doc_data
    dashboards = DN.chon_dashboard(thu_muc, None)
    du_lieu = {f: d for f in dashboards if (d := doc(f))}
    muc = DN.lay_muc_apply(du_lieu)
    pmids = sorted({p for d in du_lieu.values() for it in d.get("items") or []
                    if isinstance(it, dict) and it.get("decision") == "apply" for p in [DN._pmid(it)] if p})
    tep = tep_dem_nguon or thu_muc / "derivatives" / "do-nhay-ngu-nghia-nguon.json"
    nguon, _ = DN.nap_nguon(pmids, tep_dem=tep, tep_them=(thu_muc / "derivatives" / "bo-vang-ngu-nghia-nguon.json",),
                            online=False)
    _, goc = DN.do_doi_chung(muc, nguon, du_lieu, bo)
    word = {f: (DN.gon_dau(DN.chuan_hoa(w)) if (w := DN._doc(DN._duong_word(f))) else None) for f in du_lieu}
    neo = {f: bo["k3_neo"](d) for f, d in du_lieu.items()} if "k3_neo" in bo else None
    dot_bien = DN.sinh_dot_bien(muc, nguon, goc, hat, bo, word, neo)
    DN.cham_tat_ca(dot_bien, goc, bo, nguon)
    goc_theo_khoa = {}
    for rec in muc:
        pm = DN._pmid(rec["muc"])
        if pm and pm in nguon:
            goc_theo_khoa[DN._khoa(rec)] = {"muc": rec["muc"], "nguon": nguon[pm],
                                            "ket_qua_luat": goc.get(DN._khoa(rec))}
    return {"dot_bien": dot_bien, "goc_theo_khoa": goc_theo_khoa, "bo": bo, "so_dashboard": len(du_lieu),
            "so_muc": len(muc)}


# ───────────────────────── báo cáo ─────────────────────────

def _pt(x) -> str:
    return "—" if x is None else f"{x * 100:.0f}%"


def _ktc(x) -> str:
    return "—" if not x else f"{x[0] * 100:.0f}%–{x[1] * 100:.0f}%"


def ban_md(bj: dict) -> str:
    d = ["# Độ bắt lỗi bộ kiểm ngữ nghĩa Claude API — đột biến tổng hợp tất định "
         f"({bj['ngay']}, prompt {bj['phien_ban']})", "",
         "> **Đột biến TỔNG HỢP có nhãn theo cấu trúc — KHÔNG thay bộ vàng do bác sĩ gắn nhãn.** Cùng bộ sinh, cùng hạt "
         f"giống ({bj['hat_giong']}) với báo cáo độ nhạy luật cứng `do-nhay-dot-bien-*.md`; luật cứng chấm trên CÙNG đột biến "
         "để so cặp. Báo động trên đối chứng là CẬN TRÊN của báo động giả. Công cụ không đổi chế độ chặn.", "",
         f"Model `{bj['model']}` · mẫu tối đa {bj['so_mau']} đột biến/lớp · dashboard PASS {bj['so_dashboard']} · mục apply "
         f"{bj['so_muc']} · mã: " + ", ".join(f"`{k}` {v}" for k, v in bj["bam_ma"].items()), ""]
    for tap, ten in (("test", "TEST (tập giữ lại — số để quyết)"), ("dev", "DEV (tập dùng để sửa prompt)"),
                     ("tat_ca", "Gộp DEV + TEST")):
        x = bj["ket_qua"]["theo_tap"].get(tap)
        if not x:
            continue
        d += [f"## {ten}", "",
              "| Lớp đột biến | Trục API | n tính | API bắt | Độ bắt lỗi API (KTC 95%) | Riêng phần nguồn đủ thông tin "
              "(KTC 95%; bắt/n) | Luật cứng cùng đột biến (KTC 95%) | **Kết hợp: luật cứng HOẶC API** (KTC 95%) | Chỉ API bắt | "
              "Chỉ luật cứng bắt | p McNemar | Lọt ✓ | Lọt ⚪ | Bắt lệch trục | Gốc đã nghi |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for lop, o in x["lop"].items():
            lc, cap = o.get("luat_cung") or {}, o.get("cap") or {}
            p = cap.get("p_mcnemar")
            pdx = o.get("phan_duoc") or {}
            d.append(f"| {LOP_API[lop][1]} | {TEN_TRUC[LOP_API[lop][0]]} | {o['n_tinh']} | {o['bat']} | {_pt(o['do_nhay'])} "
                     f"({_ktc(o['ktc95'])}) | {_pt(pdx.get('do_nhay'))} ({_ktc(pdx.get('ktc95'))}; {pdx.get('bat', '—')}/"
                     f"{pdx.get('n', '—')}) | {_pt(lc.get('do_nhay'))} ({_ktc(lc.get('ktc95'))}) | "
                     f"**{_pt((o.get('ket_hop') or {}).get('do_nhay'))}** ({_ktc((o.get('ket_hop') or {}).get('ktc95'))}) | "
                     f"{cap.get('chi_api', '—')} | "
                     f"{cap.get('chi_luat_cung', '—')} | {'—' if p is None else f'{p:.3g}'} | {o['lot_xanh']} | "
                     f"{o['lot_trang']} | {o['bat_lech']} | {o['goc_da_nghi']} |")
        dc = x["doi_chung"]
        d += ["", f"**Đối chứng (mục gốc, không đột biến):** n = {dc['n']} · API nghi ≥ 1 trục {dc['api_bat_ky']} "
              f"({_pt(dc['api_ty_le'])}; KTC {_ktc(dc['api_ktc95'])}) — theo trục: "
              + " · ".join(f"{TEN_TRUC[t]} {dc['api_theo_truc'][t]}" for t in TRUC)
              + f" · luật cứng báo {dc['luat_cung_bao']} ({_pt(dc['luat_cung_ty_le'])}). Trả «không đủ thông tin» (null): "
              + " · ".join(f"{TEN_TRUC[t]} {dc['api_null_theo_truc'][t]}" for t in TRUC) + ".", ""]
    d += ["## Phủ mẫu", "", "| Lớp | Đột biến có sẵn | API không nhìn thấy phần đổi | Đã chọn | Loại vì sinh từ mục phần B "
          "(giữ mù) |", "|---|---|---|---|---|"]
    for lop, t in bj["phu_mau"].items():
        d.append(f"| {LOP_API[lop][1]} | {t['co_san']} | {t['api_khong_thay']} | {t['chon']} | {t.get('loai_phan_b', 0)} |")
    d += ["", "Ngoài tầm API (không đo): " + " · ".join(f"{k} — {v}" for k, v in NGOAI_TAM_API.items()) + ".", "",
          "Cách đọc: «bắt» = trục đích của bản đột biến là false trong khi bản gốc không false; «gốc đã nghi» = API đã phán "
          "false trục đó ở bản gốc nên không quy được cho đột biến (loại khỏi mẫu số); «lọt ⚪» = mô hình trả null (không "
          "đủ thông tin trong tóm tắt). Chuyển sang CHẶN là quyết định của bác sĩ; bỏ lọt trên lỗi THẬT vẫn cần bộ vàng do "
          "bác sĩ gắn nhãn (`tools/bo_vang_kiem_ngu_nghia.py`).", "", "Cần bác sĩ kiểm chứng.", ""]
    return "\n".join(d)


def _bam_tep(p: Path) -> str:
    try:
        return hashlib.sha256(p.read_bytes()).hexdigest()[:16]
    except OSError:
        return "—"


def main(argv: list[str] | None = None, *, cau_noi=None, client=None) -> int:
    ap = argparse.ArgumentParser(description="Đo độ bắt lỗi bộ kiểm ngữ nghĩa Claude API trên đột biến tổng hợp")
    ap.add_argument("--thu-muc", help="thư mục dashboard (mặc định EBM-Dashboards/)")
    ap.add_argument("--hat-giong", type=int)
    ap.add_argument("--so-mau", type=int, default=SO_MAU_MAC_DINH)
    ap.add_argument("--phien-ban", help="phiên bản prompt (mặc định phiên bản đang dùng của kiem_ngu_nghia_api)")
    ap.add_argument("--model")
    ap.add_argument("--chia-theo", choices=("pmid", "muc"), default="pmid",
                    help="chia DEV/TEST theo PMID (mặc định, chống rò rỉ giữa phiên bản) hoặc theo mục (cách cũ)")
    ap.add_argument("--chi-tap", choices=("dev", "test"), help="chỉ gọi/chấm một tập")
    ap.add_argument("--goi-api", action="store_true", help="gọi thật (tính phí) các lượt còn thiếu trong bộ đệm")
    ap.add_argument("--toi-da", type=int, help="trần số lượt gọi lượt này")
    ap.add_argument("--cau-noi", help="đường dẫn api_claude_nc.py (worktree chưa nối engine)")
    ap.add_argument("--bo-dem", help="bộ đệm kết quả API (mặc định EBM-Dashboards/derivatives/do-nhay-api-ngu-nghia.json)")
    ap.add_argument("--ghi", action="store_true", help="ghi báo cáo .json + .md")
    ap.add_argument("--ngay")
    a = ap.parse_args(argv)
    DN, A = _dn(), _api()
    kqtc = A._kqtc()
    thu_muc = Path(a.thu_muc) if a.thu_muc else DN.goc_du_lieu("EBM-Dashboards")
    if not thu_muc.is_dir():
        print(f"⚪ Không thấy thư mục dashboard {thu_muc.as_posix()} — không đo được.")
        return 2
    hat = a.hat_giong or DN.HAT_GIONG_MAC_DINH
    mdl = a.model or os.environ.get("EBM_NC_API_MODEL") or A.MODEL_MAC_DINH
    pb = a.phien_ban or A.PHIEN_BAN_PROMPT
    if pb not in A.PROMPT_THEO_PHIEN_BAN:
        print(f"✗ phiên bản prompt lạ: {pb} (có: {', '.join(A.PROMPT_THEO_PHIEN_BAN)})")
        return 2
    global KHO_TOAN_VAN, QUYEN_FN
    KHO_TOAN_VAN = thu_muc / "toan_van_oa" if (thu_muc / "toan_van_oa").is_dir() else None
    QUYEN_FN = A.ham_quyen_theo_thu_muc(thu_muc) if KHO_TOAN_VAN else None
    dl = nap_du_lieu(thu_muc, hat=hat, DN=DN)
    mau, phu = chon_mau(dl["dot_bien"], dl["goc_theo_khoa"], a.so_mau, hat)
    bvk = A._bvk()
    bv = bvk.doc_bo_vang() if bvk.TEP_BO_VANG.is_file() else None
    if bv is None:
        print("⚪ Không đọc được bộ vàng — không biết mục phần B để loại (giữ mù fail-closed) — không đo.")
        return 2
    mau, bo_b = loai_phan_b(mau, dl["goc_theo_khoa"], khoa_phan_b(bv, bvk), bvk)
    for lop, n in bo_b.items():
        phu.setdefault(lop, {"co_san": 0, "api_khong_thay": 0, "chon": 0})["loai_phan_b"] = n
    if not mau:
        print("⚪ Không có đột biến nào trong tầm API — không đo được.")
        return 2
    global CHIA_THEO
    CHIA_THEO = a.chia_theo
    mau_goi = [d for d in mau if not a.chi_tap or tap_dot_bien(hat, d, dl["goc_theo_khoa"]) == a.chi_tap]
    yc = lap_yeu_cau(mau_goi, dl["goc_theo_khoa"], A, kqtc, mdl, pb)
    tep = Path(a.bo_dem) if a.bo_dem else tep_bo_dem()
    dem = doc_bo_dem(tep)
    for t in (A.tep_bo_dem(), A.tep_bo_dem_xuat()):         # kết quả đã trả phí ở bộ vàng / bước xuất — chỉ đọc
        for k, v in doc_bo_dem(t).items():
            if isinstance(v, dict) and v.get("ket_qua"):
                dem.setdefault(k, v)
    thieu = [k for k in yc if k not in dem]
    tok_vao = sum((len(A.he_thong(pb)) + len(A.dung_noi_dung(it, tt, doan))) // 3
                  for k, (it, tt, doan) in yc.items() if k in thieu)
    so_tv = sum(1 for _, _, doan in yc.values() if doan)
    cn = cau_noi if cau_noi is not None else A.nap_cau_noi(Path(a.cau_noi) if a.cau_noi else None)
    uoc = cn.in_chi_phi(tok_vao, A.TOKEN_RA_UOC * len(thieu), mdl) if cn else f"~{tok_vao:,} token vào"
    print(f"Đo độ bắt lỗi API (prompt {pb}, {mdl}, hạt giống {hat}): {len(mau)} đột biến trong mẫu · cần {len(yc)} lượt chấm "
          f"(đột biến + gốc){' — tập ' + a.chi_tap if a.chi_tap else ''} · kèm đoạn toàn văn {so_tv} · đã có "
          f"{len(yc) - len(thieu)} · thiếu {len(thieu)} — {uoc}")
    if thieu and a.goi_api:
        if cn is None:
            print(f"⚪ không có cầu nối {A.CAU_NOI} — dùng --cau-noi <đường dẫn api_claude_nc.py>")
            return 2
        rieng = doc_bo_dem(tep)
        kq = goi_thieu({k: yc[k] for k in thieu}, rieng, A=A, cau_noi=cn, client=client, mdl=mdl, phien_ban=pb, tep=tep,
                       toi_da=a.toi_da)
        dem.update(rieng)
        print(f"  đã gọi {kq['da_goi']}/{kq['can_goi']}" + (f" · lỗi {len(kq['loi'])}" if kq["loi"] else "")
              + (f" · ⛔ dừng: {kq['dung']}" if kq["dung"] else ""))
    elif thieu:
        print("  (chạy khô) không gọi API — thêm --goi-api để gọi thật (tính phí; trần tháng của cầu nối vẫn áp)")
    th = tong_hop(mau, dl["goc_theo_khoa"], dem, A, kqtc, mdl, pb, hat, dl["bo"], DN, a.chi_tap)
    for tap in ("test", "dev", "tat_ca"):
        x = th["theo_tap"].get(tap)
        if not x:
            continue
        dong = []
        for lop, o in x["lop"].items():
            lc = o.get("luat_cung") or {}
            dong.append(f"{lop} {_pt(o['do_nhay'])} [{_ktc(o['ktc95'])}; {o['bat']}/{o['n_tinh']}] vs luật {_pt(lc.get('do_nhay'))}")
        dc = x["doi_chung"]
        print(f"  [{tap}] " + " · ".join(dong) + f" · đối chứng API nghi {_pt(dc['api_ty_le'])} (n={dc['n']})")
    ngay = a.ngay or dt.date.today().strftime("%Y%m%d")
    bj = {"cong_cu": "do_nhay_api_ngu_nghia", "ngay": ngay, "phien_ban": pb, "model": mdl, "hat_giong": hat,
          "so_mau": a.so_mau, "chia_theo": CHIA_THEO, "so_dashboard": dl["so_dashboard"], "so_muc": dl["so_muc"], "phu_mau": phu,
          "bam_ma": {n: _bam_tep(Path(__file__).resolve().parent / n) for n in
                     ("do_nhay_api_ngu_nghia.py", "kiem_ngu_nghia_api.py", "do_nhay_kiem_ngu_nghia.py")},
          "ket_qua": th}
    if a.ghi:
        THU_MUC_BAO_CAO.mkdir(parents=True, exist_ok=True)
        hau = ("" if pb == A.PHIEN_BAN_PROMPT else f"-{pb}") + (f"-{a.chi_tap}" if a.chi_tap else "")   # DEV không đè TEST
        tj, tm = THU_MUC_BAO_CAO / f"do-nhay-api-{ngay}{hau}.json", THU_MUC_BAO_CAO / f"do-nhay-api-{ngay}{hau}.md"
        tj.write_text(json.dumps(bj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        tm.write_text(ban_md(bj), encoding="utf-8", newline="\n")
        print(f"✓ Đã ghi {tj.as_posix()} + {tm.name}")
    lop_tat_ca = (th["theo_tap"].get("tat_ca") or th["theo_tap"][a.chi_tap])["lop"]
    co_so = [o["do_nhay"] is not None for o in lop_tat_ca.values()]
    return 0 if all(co_so) else (1 if any(co_so) else 2)


if __name__ == "__main__":
    raise SystemExit(main())
