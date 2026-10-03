#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CHỦ ĐỀ NÀO 0 ỨNG VIÊN NHIỀU LƯỢT TUẦN LIỀN? — tín hiệu «chỗ mù» của vòng quét giám sát (03/10/2026).

VÌ SAO CÓ. Đếm thô 03/10/2026 trên `EBM-Dashboards/surveillance/tuan-2026-W39-quet.json` + `…W40…`: 10/47 chủ
đề watchlist 0 ứng viên ở cả hai tệp; 7 trong số đó trùng danh sách «truy vấn mù» mà
`tools/kiem_san_luong_giam_sat.py` đo 02/10. Bộ quét vẫn PASS và tiến con trỏ, đề xuất viết lại truy vấn
(`EBM-Dashboards/watchlist.de-xuat.json`, 02/10) chưa được áp, chốt sản lượng không nằm trong dây chuyền tuần
⇒ không ai thấy. «0 ứng viên» ≠ «không có chứng cứ mới» (CLAUDE.md §6.4).

ĐO GÌ. Đọc ≤ 8 tệp `tuan-<năm>-W<tuần>-quet.json` mới nhất (xếp theo tuần ISO trong TÊN tệp). Với mỗi chủ đề
đang bật của watchlist có mặt trong lượt đọc được mới nhất, đếm ngược số lượt LIỀN NHAU mà chủ đề ĐO ĐƯỢC và có 0
ứng viên:
  • ĐO ĐƯỢC = tệp đọc được, lượt PASS/PARTIAL và CHÍNH chủ đề có `status == "PASS"` — đúng tiêu chí bộ quét dùng
    để tiến con trỏ. Lượt PARTIAL không làm hỏng chủ đề PASS bên trong: trạng thái lượt là số của TẬP HỢP, không
    phải của từng chủ đề (CLAUDE.md §0.2; đo W39: chủ đề WHO vẫn lấy được 5 bản ghi PubMed trong lượt PARTIAL).
    Chủ đề PASS_DEGRADED/FAIL, tệp hỏng, lượt FAIL ⇒ KHÔNG ĐO ĐƯỢC — không bao giờ đọc thành «0 ứng viên».
  • Lượt không đo được nằm GIỮA ⇒ chuỗi bị cắt, không bắc cầu. Chủ đề 0 ở lượt mới mà lượt liền trước không đo
    được ⇒ ghi riêng ⚪ «chưa tính là liền». Lượt MỚI NHẤT không đo được cho một chủ đề ⇒ bỏ qua ở đầu chuỗi (có ghi
    chú) và đếm từ lượt đo được gần nhất: một tuần NCBI chập chờn không được xoá tín hiệu đã có.
  • Chủ đề vắng ở một lượt (mới thêm vào watchlist) ⇒ chuỗi dừng ở đó.
  • Tuần KHÔNG có tệp quét (lượt không chạy — vd W38/2026: không có cả tệp quét lẫn hàng chờ) không phải một lượt:
    bộ quét dùng CON TRỎ TĂNG DẦN (K8 — `mindate` = con trỏ lùi 3 ngày), lượt sau quét cả cửa sổ của tuần bị bỏ ⇒
    hai tệp kề nhau là hai lượt LIỀN. Giới hạn đã biết: lượt có chạy mà không lưu bản sao thì công cụ không thấy.
Rồi đối chiếu: (1) `watchlist.de-xuat.json` — đề xuất CHƯA ÁP (đúng phép so của
`ap_dung_de_xuat_watchlist.lap_ke_hoach`); (2) kết quả gần nhất của `kiem_san_luong_giam_sat`
(`state/san-luong-giam-sat-gan-nhat.json`) — chỉ tin khi cùng watchlist (băm), đo trọn, ≤ 9 ngày (luật
`dung_lai_duoc` của chính công cụ đó; 9 = một lượt tuần + 2 ngày ân hạn); (3) bảng `KENH_THAT_NGOAI_PUBMED` của
bộ quét chuẩn (đọc bằng AST, không chạy bộ quét) + khối `quan_sat_han_che` của lượt mới nhất (EV-03) — chủ đề thẩm
quyền mà làn PubMed không quan sát được là khoảng trống ĐÃ BIẾT, có kênh khác: dòng ⓘ, không phải việc.

CHỈ ĐỌC VÀ BÁO. Không sửa watchlist, không áp đề xuất, không đổi PASS của bộ quét, không gọi mạng.

    python3 tools/kiem_chuoi_0_ung_vien.py
    python3 tools/kiem_chuoi_0_ung_vien.py --dash <thư mục EBM-Dashboards> --san-luong <tệp kết quả sản lượng>

Mã thoát: 0 không có việc (kể cả khi chỉ còn khoảng trống đã biết) · 1 có việc (duyệt đề xuất / đo sản lượng /
soạn đề xuất / rà truy vấn) · 2 KHÔNG ĐO ĐƯỢC (không có thư mục quét, < 2 lượt đọc được, không đọc được
watchlist, công cụ lỗi) — không đọc thành «ổn». Cần bác sĩ kiểm chứng."""
from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import re
import sys
from datetime import datetime
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent


def _nap(ten: str, tep: str):
    """Nạp một công cụ cùng thư mục theo đường dẫn tệp (không phụ thuộc sys.path của nơi gọi)."""
    sp = importlib.util.spec_from_file_location(ten, TOOLS / tep)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


_SL = _nap("_k0uv_san_luong", "kiem_san_luong_giam_sat.py")
_AD = _nap("_k0uv_ap_dung", "ap_dung_de_xuat_watchlist.py")
_BST = _nap("_k0uv_ban_sao_tran", "ban_sao_tran.py")

SO_LUOT_DOC = 8            # đọc tối đa 8 lượt tuần gần nhất (≈ 2 tháng)
TOI_THIEU_LIEN = 2         # ≥ 2 lượt LIỀN NHAU đo được mà 0 ứng viên ⇒ nêu
HAN_SAN_LUONG_NGAY = 9.0   # số đo sản lượng ≤ 9 ngày mới tin (lượt tuần + 2 ngày ân hạn: không nhấp nháy)
LUOT_CO_KET_QUA = ("PASS", "PARTIAL")   # lượt FAIL không có chủ đề nào đo được
_MAU_TEP = re.compile(r"^tuan-(\d{4})-W(\d{1,2})-quet\.json$")
NHAC = "0 ứng viên ≠ không có chứng cứ mới"
LENH_DUYET = "python3 tools/ap_dung_de_xuat_watchlist.py"
LENH_DO = ("python3 tools/kiem_san_luong_giam_sat.py --json state/san-luong-giam-sat-gan-nhat.json "
           "--dung-lai-neu-moi-hon-ngay 2")
_NHAN_NHOM = {
    "duyet_de_xuat": "đề xuất truy vấn CHỜ BÁC SĨ DUYỆT",
    "han_che_da_biet": "QUAN SÁT HẠN CHẾ đã biết (EV-03) — theo dõi ở kênh khác",
    "khong_tang": "không có tầng truy vấn, chưa có kênh khác — cần rà truy vấn",
    "can_do": "chưa có số đo sản lượng tin được — cần đo",
    "mu_chua_de_xuat": "sản lượng MÙ, chưa có đề xuất — cần soạn đề xuất",
    "san_luong_du": "sản lượng > ngưỡng — truy vấn không mù",
}


def doc_cac_luot(thu_muc: Path, so_luot: int = SO_LUOT_DOC) -> list[dict]:
    """≤ `so_luot` lượt tuần MỚI NHẤT, xếp cũ → mới theo (năm, tuần) trong TÊN tệp.

    Mỗi lượt: nhan («W40») · tep · doc_duoc · status · chu_de {tên: (status chủ đề, số ứng viên | None)} ·
    han_che {tên: kênh}. Tệp không đọc được (JSON hỏng, OneDrive chưa tải về, sai dạng) ⇒ doc_duoc=False: cả lượt
    KHÔNG ĐO ĐƯỢC."""
    ds = []
    for p in thu_muc.glob("tuan-*-quet.json"):
        m = _MAU_TEP.match(p.name)
        if m:
            ds.append(((int(m.group(1)), int(m.group(2))), p))
    ds.sort()
    ra = []
    for (_nam, tuan), p in ds[-so_luot:]:
        luot = {"nhan": f"W{tuan:02d}", "tep": p.name, "doc_duoc": False, "status": "", "chu_de": {}, "han_che": {}}
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            d = None
        if not isinstance(d, dict) or not isinstance(d.get("topics"), list):
            ra.append(luot)
            continue
        for t in d["topics"]:
            if isinstance(t, dict) and isinstance(t.get("topic"), str):
                c = t.get("candidates")
                luot["chu_de"][t["topic"]] = (str(t.get("status") or ""), len(c) if isinstance(c, list) else None)
        qs = d.get("quan_sat_han_che")
        for x in qs if isinstance(qs, list) else []:
            if isinstance(x, dict) and isinstance(x.get("topic"), str):
                luot["han_che"][x["topic"]] = str(x.get("kenh_khac") or "")
        luot["doc_duoc"], luot["status"] = True, str(d.get("status") or "")
        ra.append(luot)
    return ra


def do_trong_luot(luot: dict, ten: str) -> tuple[str, str]:
    """(loại, lý do) của MỘT chủ đề trong MỘT lượt: «0» đo được và 0 ứng viên · «co» đo được, ≥ 1 ·
    «khong_do» · «vang» (chủ đề không có trong lượt)."""
    if not luot["doc_duoc"]:
        return "khong_do", "tệp quét không đọc được"
    if luot["status"] not in LUOT_CO_KET_QUA:
        return "khong_do", "lượt " + (luot["status"] or "không rõ trạng thái")
    if ten not in luot["chu_de"]:
        return "vang", ""
    st, n = luot["chu_de"][ten]
    if st != "PASS" or n is None:
        return "khong_do", st or "không rõ trạng thái"
    return ("0", "") if n == 0 else ("co", "")


def chuoi_cua(cac_luot: list[dict], ten: str) -> dict:
    """Chuỗi 0 ứng viên LIỀN NHAU của một chủ đề, đếm ngược từ lượt mới nhất (luật ở docstring module).

    lien · cac_luot_0 (cũ → mới) · ngat_boi («W39 (PASS_DEGRADED)» khi chuỗi bị cắt bởi lượt KHÔNG ĐO ĐƯỢC — không
    phải bởi lượt có ứng viên) · dau_khong_do (các lượt mới nhất không đo được, đã bỏ qua ở đầu chuỗi)."""
    i = len(cac_luot) - 1
    dau: list[str] = []
    while i >= 0:
        loai, ly_do = do_trong_luot(cac_luot[i], ten)
        if loai != "khong_do":
            break
        dau.append(f"{cac_luot[i]['nhan']} ({ly_do})")
        i -= 1
    cac_0: list[str] = []
    ngat = ""
    while i >= 0:
        loai, ly_do = do_trong_luot(cac_luot[i], ten)
        if loai != "0":
            if loai == "khong_do":
                ngat = f"{cac_luot[i]['nhan']} ({ly_do})"
            break
        cac_0.append(cac_luot[i]["nhan"])
        i -= 1
    return {"lien": len(cac_0), "cac_luot_0": cac_0[::-1], "ngat_boi": ngat, "dau_khong_do": dau[::-1]}


def bang_kenh_ngoai_pubmed(bo_quet: Path) -> dict[str, str]:
    """Bảng `KENH_THAT_NGOAI_PUBMED` của bộ quét chuẩn, đọc bằng AST (không thực thi bộ quét).

    Hỏng ⇒ {}: chủ đề rơi về nhóm thường và VẪN được nêu (báo dư, không giấu)."""
    try:
        cay = ast.parse(bo_quet.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, ValueError):
        return {}
    for nut in cay.body:
        if isinstance(nut, ast.AnnAssign):
            dich, gia_tri = nut.target, nut.value
        elif isinstance(nut, ast.Assign) and len(nut.targets) == 1:
            dich, gia_tri = nut.targets[0], nut.value
        else:
            continue
        if isinstance(dich, ast.Name) and dich.id == "KENH_THAT_NGOAI_PUBMED" and gia_tri is not None:
            try:
                bang = ast.literal_eval(gia_tri)
            except (ValueError, TypeError, SyntaxError):
                return {}
            return {str(k): str(v) for k, v in bang.items()} if isinstance(bang, dict) else {}
    return {}


def doc_de_xuat(tep: Path, watchlist: dict) -> dict:
    """Trạng thái đề xuất watchlist: trang_thai {tên: «cho_duyet» | «loi» | «da_ap»} · so_loi · ngay · loi_doc.

    Dùng đúng `ap_dung_de_xuat_watchlist.lap_ke_hoach` (một nguồn sự thật cho «chưa áp»): hợp lệ và khác hiện hành
    ⇒ cho_duyet; trùng hiện hành ⇒ da_ap; còn lại (chủ đề lạ, đổi bộ tầng, sai cú pháp…) ⇒ loi — chạy khô sẽ từ
    chối, bác sĩ vẫn phải xem. Không có tệp ⇒ không có đề xuất (hợp lệ). Tệp hỏng ⇒ loi_doc (bên gọi ghi ⚪)."""
    ra: dict = {"trang_thai": {}, "so_loi": 0, "ngay": "", "loi_doc": ""}
    if not tep.exists():
        return ra
    try:
        dx = json.loads(tep.read_text(encoding="utf-8"))
        if not isinstance(dx, dict) or not isinstance(dx.get("topics"), list):
            raise ValueError("không có danh sách topics")
        doi, loi, khong_doi = _AD.lap_ke_hoach(watchlist, dx)
    except Exception as e:  # noqa: BLE001 — đề xuất hỏng phải LỘ RA, không thành «không có đề xuất»
        ra["loi_doc"] = f"không đọc được {tep.name} ({type(e).__name__})"
        return ra
    cho = {ten for ten, _ in doi}
    for muc in dx["topics"]:
        ten = muc.get("topic") if isinstance(muc, dict) else None
        if isinstance(ten, str):
            ra["trang_thai"][ten] = "cho_duyet" if ten in cho else ("da_ap" if ten in khong_doi else "loi")
    ra["so_loi"] = len(loi)
    m = re.search(r"\d{2}/\d{2}/\d{4}", str(dx.get("_about") or ""))
    ra["ngay"] = m.group(0) if m else ""
    return ra


def doc_san_luong(tep: Path, wl_text: str, bay_gio: datetime | None = None) -> dict:
    """Kết quả gần nhất của `kiem_san_luong_giam_sat` còn tin được không — ĐÚNG luật `dung_lai_duoc` của chính
    công cụ đó (cùng băm watchlist, cùng ngưỡng/cửa sổ mặc định, đo trọn, ≤ HAN_SAN_LUONG_NGAY ngày).

    Trả tuoi · do_luc · theo_chu_de {tên: (loại MU/ON/KHONG_DO, tổng)} · mo_ta."""
    d = _SL.dung_lai_duoc(tep, _SL.bam_watchlist(wl_text), _SL.NGUONG_MU, _SL.SO_NGAY, HAN_SAN_LUONG_NGAY,
                          bay_gio)
    if d is None:
        mo_ta = (f"chưa có số đo sản lượng lưu ({tep.name})" if not tep.exists() else
                 f"số đo sản lượng lưu cũ hơn {HAN_SAN_LUONG_NGAY:g} ngày, khác watchlist hiện hành hoặc đo không trọn")
        return {"tuoi": False, "do_luc": "", "theo_chu_de": {}, "mo_ta": mo_ta}
    theo = {}
    for k in d.get("chu_de") or []:
        if isinstance(k, dict) and isinstance(k.get("topic"), str):
            theo[k["topic"]] = (str(k.get("loai") or ""), k.get("tong"))
    do_luc = str(d.get("do_luc") or "")[:10]
    return {"tuoi": True, "do_luc": do_luc, "theo_chu_de": theo,
            "mo_ta": f"sản lượng đo {do_luc} (cùng watchlist, ≤ {HAN_SAN_LUONG_NGAY:g} ngày, mù ≤ {_SL.NGUONG_MU})"}


def _nhom(m: dict) -> str:
    """Đường xử lý của MỘT chủ đề bị nêu — việc của bác sĩ trước, rồi khoảng trống đã biết, rồi việc máy."""
    if m["de_xuat"] in ("cho_duyet", "loi"):
        return "duyet_de_xuat"
    if m["kenh_khac"]:
        return "han_che_da_biet"
    if not m["co_tang"]:
        return "khong_tang"
    if m["san_luong"] is None:
        return "can_do"
    if m["san_luong"][0] == "MU":
        return "mu_chua_de_xuat"
    if m["san_luong"][0] == "ON":
        return "san_luong_du"
    return "can_do"


def phan_tich(dash: Path, san_luong: Path | None = None, bo_quet: Path | None = None,
              bay_gio: datetime | None = None, so_luot: int = SO_LUOT_DOC, toi_thieu: int = TOI_THIEU_LIEN) -> dict:
    """Đọc mọi nguyên liệu, trả bảng phân tích. Không gọi mạng, không ghi gì.

    do_duoc=False kèm ly_do khi KHÔNG ĐO ĐƯỢC (không thư mục quét · < `toi_thieu` lượt đọc được · watchlist hỏng)
    — không phải «ổn». canh_bao: nguyên liệu phụ hỏng (đề xuất không đọc được) — bên gọi ghi giác quan ⚪."""
    san_luong = san_luong or _SL.KET_QUA_GAN_NHAT
    bo_quet = bo_quet or _SL.SCANNER
    thu_muc = dash / "surveillance"
    if not thu_muc.is_dir():
        return {"do_duoc": False, "ly_do": f"không có thư mục quét {thu_muc.name}/ trong {dash}"}
    cac_luot = doc_cac_luot(thu_muc, so_luot)
    doc_duoc = [lt for lt in cac_luot if lt["doc_duoc"]]
    if len(doc_duoc) < toi_thieu:
        return {"do_duoc": False, "ly_do": f"chỉ {len(doc_duoc)} lượt quét tuần đọc được (cần ≥ {toi_thieu})"}
    try:
        wl_text = (dash / "watchlist.json").read_text(encoding="utf-8")
        wl = json.loads(wl_text)
        if not isinstance(wl, dict) or not isinstance(wl.get("topics"), list):
            raise ValueError("không có danh sách topics")
    except (OSError, ValueError) as e:
        return {"do_duoc": False, "ly_do": f"không đọc được watchlist.json ({type(e).__name__})"}
    theo_wl = {t["topic"]: t for t in wl["topics"]
               if isinstance(t, dict) and isinstance(t.get("topic"), str) and t.get("active", True)}
    dx = doc_de_xuat(dash / "watchlist.de-xuat.json", wl)
    sl = doc_san_luong(san_luong, wl_text, bay_gio)
    kenh = bang_kenh_ngoai_pubmed(bo_quet)
    kenh.update(doc_duoc[-1]["han_che"])
    chu_de = []
    for ten in doc_duoc[-1]["chu_de"]:
        if ten not in theo_wl:
            continue  # đã rời watchlist hoặc đã tắt: không còn giám sát — không phải chỗ mù
        ch = chuoi_cua(cac_luot, ten)
        if ch["lien"] >= toi_thieu:
            muc = "lien"
        elif ch["lien"] >= 1 and ch["ngat_boi"]:
            muc = "chua_tinh_lien"
        else:
            continue
        m = {"topic": ten, "muc": muc, **ch, "de_xuat": dx["trang_thai"].get(ten), "kenh_khac": kenh.get(ten, ""),
             "co_tang": bool(theo_wl[ten].get("queries")), "san_luong": sl["theo_chu_de"].get(ten)}
        m["nhom"] = _nhom(m)
        chu_de.append(m)
    return {"do_duoc": True, "ly_do": "", "toi_thieu": toi_thieu, "luot": [lt["nhan"] for lt in cac_luot],
            "luot_khong_doc_duoc": [lt["nhan"] for lt in cac_luot if not lt["doc_duoc"]], "chu_de": chu_de,
            "de_xuat": dx, "san_luong": sl, "canh_bao": [dx["loi_doc"]] if dx["loi_doc"] else []}


def _chuoi_ngan(m: dict) -> str:
    if m["muc"] == "lien":
        return f"{m['lien']} lượt {m['cac_luot_0'][0]}–{m['cac_luot_0'][-1]}"
    return f"0 ở {', '.join(m['cac_luot_0'])}, {m['ngat_boi']} không đo được"


def _ten(ds: list[dict], toi_da: int = 5) -> str:
    phan = [f"{m['topic']} [{_chuoi_ngan(m)}]" for m in ds[:toi_da]]
    return "; ".join(phan) + ("…" if len(ds) > toi_da else "")


def viec_tu_phan_tich(pt: dict) -> tuple[list[tuple[int, str, str, str]], list[str]]:
    """(việc [(ưu tiên, ai, mô tả, lệnh)], dòng ⓘ) — MỘT nguồn cho cả CLI lẫn `tu_de_xuat_viec.py`.

    Hòm việc một cửa đọc bảng của `tu_de_xuat_viec`, cắt mô tả ở 150 ký tự và KHÔNG in lệnh ⇒ điều cốt lõi
    («0 ứng viên ≠ không có chứng cứ mới» + lệnh duyệt) đứng đầu mô tả. 👤 duyệt đề xuất hiện khi CÒN đề xuất chưa
    áp (việc treo của bác sĩ, dù chủ đề có bị nêu hay không): 🟠 nếu có chủ đề chờ duyệt đang 0 ứng viên nhiều lượt
    (liền, hoặc lượt liền trước không đo được), 🟡 nếu không."""
    viec: list[tuple[int, str, str, str]] = []
    tt: list[str] = []
    if not pt.get("do_duoc"):
        return viec, tt
    k, cd, sl, dx = pt["toi_thieu"], pt["chu_de"], pt["san_luong"], pt["de_xuat"]

    def nhom(ten_nhom: str, chi_lien: bool = False) -> list[dict]:
        return [m for m in cd if m["nhom"] == ten_nhom and (m["muc"] == "lien" or not chi_lien)]

    cho = {t for t, s in dx["trang_thai"].items() if s in ("cho_duyet", "loi")}
    if cho:
        lien = [m for m in cd if m["topic"] in cho and m["muc"] == "lien"]
        chua = [m for m in cd if m["topic"] in cho and m["muc"] == "chua_tinh_lien"]
        con = len(cho) - len(lien) - len(chua)
        chi_tiet = []
        if lien:
            chi_tiet.append(f"{len(lien)} chủ đề 0 ứng viên ≥ {k} lượt liền")
        if chua:
            chi_tiet.append(f"{len(chua)} chủ đề 0 ở lượt mới nhất, lượt liền trước KHÔNG đo được")
        if con:
            chi_tiet.append(f"{con} chủ đề còn có ứng viên gần đây")
        if dx["so_loi"]:
            chi_tiet.append(f"đề xuất có {dx['so_loi']} lỗi — chạy khô sẽ từ chối, sửa trước")
        if dx["ngay"]:
            chi_tiet.append(f"soạn {dx['ngay']}")
        viec.append((1 if (lien or chua) else 2, "👤",
                     f"{len(cho)} chủ đề watchlist có đề xuất truy vấn CHỜ BÁC SĨ DUYỆT ({NHAC}) → {LENH_DUYET} · "
                     + " · ".join(chi_tiet),
                     f"{LENH_DUYET}  # chạy khô: đọc `_ly_do` từng chủ đề, xoá chủ đề không muốn đổi, rồi --ap-dung "
                     "(có sao lưu); chi tiết: python3 tools/kiem_chuoi_0_ung_vien.py"))
    can_do = nhom("can_do")
    if can_do:
        viec.append((1 if any(m["muc"] == "lien" for m in can_do) else 2, "🛎",
                     f"{len(can_do)} chủ đề có tầng 0 ứng viên nhiều lượt mà CHƯA có số đo sản lượng tin được "
                     f"({NHAC}) — máy đo để biết truy vấn có mù không ({sl['mo_ta']}): {_ten(can_do)}", LENH_DO))
    mu = nhom("mu_chua_de_xuat")
    if mu:
        viec.append((1, "🛎",
                     f"{len(mu)} chủ đề 0 ứng viên nhiều lượt và sản lượng ≤ {_SL.NGUONG_MU} bản ghi/90 ngày (MÙ) "
                     f"mà CHƯA có đề xuất truy vấn ({NHAC}) — máy soạn đề xuất, bác sĩ duyệt: {_ten(mu)}",
                     "soạn vào EBM-Dashboards/watchlist.de-xuat.json theo khuôn EV-02 (giữ bộ tầng; moi_vao_pubmed "
                     "edat, không lọc thiết kế) rồi đo: python3 tools/kiem_san_luong_giam_sat.py "
                     "--watchlist EBM-Dashboards/watchlist.de-xuat.json"))
    kt = nhom("khong_tang", chi_lien=True)
    if kt:
        viec.append((2, "🛎",
                     f"{len(kt)} chủ đề KHÔNG có tầng truy vấn 0 ứng viên ≥ {k} lượt liền, chưa có kênh khác khai "
                     f"báo ({NHAC}) — chốt sản lượng không đo nhóm này; máy rà truy vấn rồi đề xuất: {_ten(kt)}",
                     "xem `query` của chủ đề trong EBM-Dashboards/watchlist.json; có kênh ngoài PubMed thì khai vào "
                     "KENH_THAT_NGOAI_PUBMED (sync/skills/cap-nhat-chung-cu-y-khoa/tools/surveillance_scan.py)"))
    hc = nhom("han_che_da_biet", chi_lien=True)
    if hc:
        tt.append(f"{len(hc)} chủ đề thẩm quyền 0 ứng viên ≥ {k} lượt liền — QUAN SÁT HẠN CHẾ ĐÃ BIẾT (EV-03): làn "
                  f"PubMed không thấy văn bản chính thức, theo dõi ở kênh khác; 0 ứng viên ≠ không có cập nhật: "
                  f"{_ten(hc)}")
    du = nhom("san_luong_du", chi_lien=True)
    if du:
        tt.append(f"{len(du)} chủ đề 0 ứng viên ≥ {k} lượt liền nhưng sản lượng 90 ngày > {_SL.NGUONG_MU} (truy vấn "
                  f"không mù, {sl['mo_ta']}) — 0 có thể là thật (bài mới đã có trong kho / cửa sổ con trỏ hẹp): "
                  f"{_ten(du)}")
    return viec, tt


def in_bao_cao(pt: dict) -> int:
    """In báo cáo cho người đọc; trả mã thoát (0 · 1 · 2 — xem docstring module)."""
    if not pt.get("do_duoc"):
        print(f"⚪ KHÔNG ĐO ĐƯỢC chuỗi 0 ứng viên — {pt.get('ly_do')}. KHÔNG đọc là «không có chủ đề mù».")
        return 2
    viec, tt = viec_tu_phan_tich(pt)
    k, luot = pt["toi_thieu"], pt["luot"]
    print(f"CHỦ ĐỀ 0 ỨNG VIÊN NHIỀU LƯỢT TUẦN LIỀN — {len(luot)} lượt ({luot[0]} → {luot[-1]}) · "
          f"nêu khi ≥ {k} lượt liền")
    if pt["luot_khong_doc_duoc"]:
        print(f"  ⚪ tệp quét không đọc được (cả lượt KHÔNG ĐO ĐƯỢC): {', '.join(pt['luot_khong_doc_duoc'])}")
    lien = sorted((m for m in pt["chu_de"] if m["muc"] == "lien"), key=lambda m: (-m["lien"], m["topic"]))
    chua = [m for m in pt["chu_de"] if m["muc"] == "chua_tinh_lien"]
    if not lien:
        print(f"  Không chủ đề nào 0 ứng viên ≥ {k} lượt liền trong các lượt đo được.")
    for m in lien:
        bieu = "ⓘ" if m["nhom"] in ("han_che_da_biet", "san_luong_du") else "🟠"
        them = f" · sản lượng {m['san_luong'][0]} {m['san_luong'][1]}/90 ngày" if m["san_luong"] else ""
        if m["dau_khong_do"]:
            them += f" · {', '.join(m['dau_khong_do'])} không đo được (bỏ qua ở đầu chuỗi)"
        print(f"  {bieu} {m['topic']} — 0 ứng viên {m['lien']} lượt liền ({', '.join(m['cac_luot_0'])}) · "
              f"{_NHAN_NHOM[m['nhom']]}{them}")
    if chua:
        print("⚪ CHƯA TÍNH LÀ LIỀN — 0 ở lượt mới nhất nhưng lượt liền trước KHÔNG ĐO ĐƯỢC "
              "(không bắc cầu qua lượt hỏng):")
        for m in chua:
            print(f"  ⚪ {m['topic']} — 0 ở {', '.join(m['cac_luot_0'])} · {m['ngat_boi']} không đo được · "
                  f"{_NHAN_NHOM[m['nhom']]}")
    print(f"Sản lượng: {pt['san_luong']['mo_ta']}")
    for cb in pt["canh_bao"]:
        print(f"⚪ {cb}")
    if viec or tt:
        print("VIỆC:")
    for uu, ai, mo_ta, lenh in sorted(viec, key=lambda x: x[0]):
        print(f"  {'🔴' if uu == 0 else '🟠' if uu == 1 else '🟡'} {ai} {mo_ta}")
        print(f"       → {lenh}")
    for x in tt:
        print(f"  ⓘ {x}")
    print(f"\n«{NHAC}» (CLAUDE.md §6.4). Chỉ ĐỌC — không áp đề xuất, không sửa watchlist, không đổi PASS của "
          "bộ quét. Cần bác sĩ kiểm chứng.")
    return 1 if viec else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Chủ đề watchlist 0 ứng viên ≥ 2 lượt tuần liền (chỉ đọc, ngoại tuyến)")
    ap.add_argument("--dash", type=Path, default=_BST.duong_goc("EBM-Dashboards", REPO) or (REPO / "EBM-Dashboards"),
                    help="thư mục EBM-Dashboards (có surveillance/, watchlist.json, watchlist.de-xuat.json)")
    ap.add_argument("--san-luong", type=Path, default=_SL.KET_QUA_GAN_NHAT,
                    help="kết quả --json gần nhất của kiem_san_luong_giam_sat.py")
    a = ap.parse_args(argv)
    try:
        pt = phan_tich(a.dash, a.san_luong)
    except Exception as e:  # noqa: BLE001 — chốt hỏng phải LỘ RA (⚪, mã 2), không im như «không có chủ đề mù»
        print(f"⚪ KHÔNG ĐO ĐƯỢC chuỗi 0 ứng viên — công cụ lỗi {type(e).__name__}: {e}")
        return 2
    return in_bao_cao(pt)


if __name__ == "__main__":
    sys.exit(main())
