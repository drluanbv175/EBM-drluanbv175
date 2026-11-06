#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chốt «TIN CẬY CAO NHẤT · MỚI NHẤT · CÓ TOÀN VĂN» cho MỘT dashboard (bác sĩ giao 06/11/2026) — CHỈ CẢNH BÁO.

Lời bác sĩ (06/11/2026): «Luôn đảm bảo những chứng cứ có độ tin cậy cao nhất và mới nhất», «Hãy cập nhật luôn vào hệ thống»,
«Những chứng cứ độ tin cậy cao nhất và mới nhất hay là chứng cứ có tính áp dụng cho thực hành lâm sàng hãy lấy toàn văn luôn».

VÌ SAO CÓ. Cổng `verify_dashboard.py` đã chặn mục `apply` chưa đọc toàn văn (BH161) và so năm khai với năm PubMed thật, nhưng
KHÔNG hỏi hai điều bác sĩ vừa giao:
  M1 — guideline/nhãn thuốc/đồng thuận đã ≥ 5 năm tuổi: người soạn đã kiểm có bản THAY THẾ chưa? Bản cũ bị thay mà vẫn nằm trên
       dashboard là rủi ro thật tại điểm khám (lô 2 tầng C2, 05/11/2026: một guideline MCI 2018 mang nhãn [RETIRED]).
  M2 — nguồn mạnh/mới/định dùng cho thực hành (mọi mục `apply`; mục `consider` dựa trên guideline · SR/MA · RCT ≤ 3 năm) mà kho
       toàn văn cạnh dashboard CHƯA có toàn văn ⇒ danh sách cần lấy toàn văn (OA → Unpaywall → làn Chrome uỷ quyền).

QUY ƯỚC GHI «ĐÃ KIỂM PHIÊN BẢN» (doctrine skill `cap-nhat-chung-cu-y-khoa` Bước 2, mục «Luật tin cậy cao nhất + mới nhất»): trong
`gradeSource` (hiện ra cho bác sĩ đọc) ghi «đã kiểm phiên bản DD/MM/YYYY: chưa có bản thay thế» hoặc «đã kiểm phiên bản
DD/MM/YYYY: bản thay thế <tên>». Không thêm khoá mới vào DATA (khoá lạ bị vứt âm thầm trên sản phẩm phái sinh — CLAUDE.md §6.1).

KHÔNG phán «nguồn đã lỗi thời», KHÔNG đổi decision/gradeLevel, KHÔNG chặn xuất — chỉ ĐO và BÁO; bộ năm `xuat_goi_cap_nhat.py`
gọi ở bước ④-quater, không đổi mã thoát. Toàn văn đo bằng CHÍNH hàm của cổng (`co_toan_van_trong_kho`, BH161) để hai nơi không
nói hai điều. Mục không có PMID ⇒ không đo được toàn văn bằng kho (kho đánh khoá theo PMID) ⇒ ⚪, không bao giờ «đã có».

Mã thoát: 0 không có cảnh báo · 1 có cảnh báo M1/M2 · 2 KHÔNG ĐO ĐƯỢC (không đọc được DATA / thiếu công cụ cổng).
Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from datetime import date
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]

TUOI_GUIDELINE_PHAI_KIEM = 5      # năm — M1
TUOI_NGUON_MOI = 3                # năm — M2 cho mục consider
HAN_DAU_KIEM_NGAY = 365           # dấu «đã kiểm phiên bản» cũ hơn chừng này ⇒ nhắc kiểm lại

# Thiết kế coi là văn bản khuyến cáo có thể bị THAY THẾ (khớp tiền tố, không phân biệt hoa/thường, đã bỏ dấu cách đầu).
_TIEN_TO_KHUYEN_CAO = ("guideline", "nhãn thuốc", "nhan thuoc", "consensus", "đồng thuận", "dong thuan",
                       "khuyến cáo", "khuyen cao", "position statement", "scientific statement")
# Thiết kế tầng cao cho M2 (ngoài khuyến cáo).
_TIEN_TO_TANG_CAO = ("systematic", "meta", "tổng quan hệ thống", "tong quan he thong", "phân tích gộp", "phan tich gop",
                     "network meta", "rct", "randomi", "thử nghiệm ngẫu nhiên", "thu nghiem ngau nhien",
                     "thử nghiệm lâm sàng ngẫu nhiên", "cochrane")
_MAU_DA_KIEM = re.compile(
    r"đã\s+kiểm\s+(?:phiên\s+bản|bản\s+thay\s+thế|bản\s+mới)\D{0,12}?(\d{1,2})/(\d{1,2})/(\d{4})", re.IGNORECASE)
_MAU_NAM = re.compile(r"(19|20)\d{2}")
_PMID = re.compile(r"^\d{1,9}$")


def _nap(ten_tep: str, ten_mod: str):
    """Nạp một công cụ của dây chuyền dashboard (bản máy thật trước, bản vendor git sau) — cùng resolver bộ năm dùng."""
    sp = importlib.util.spec_from_file_location("_bst_kmn", REPO / "tools" / "ban_sao_tran.py")
    bst = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(bst)
    duong = bst.duong_cong_cu_pipeline(ten_tep, REPO)
    if duong is None:
        return None
    sp2 = importlib.util.spec_from_file_location(ten_mod, duong)
    mod = importlib.util.module_from_spec(sp2)
    sp2.loader.exec_module(mod)
    return mod


def doc_data(dash: Path) -> dict | None:
    bbd = _nap("build_ban_doc_chung_cu.py", "_bbd_kmn")
    if bbd is None:
        return None
    try:
        return bbd.extract_data(dash.read_text(encoding="utf-8", errors="replace"))
    except (SystemExit, OSError, ValueError):
        return None


def _bo_dau_cach(t) -> str:
    return str(t or "").strip().lower()


def la_khuyen_cao(design) -> bool:
    return _bo_dau_cach(design).startswith(_TIEN_TO_KHUYEN_CAO)


def la_tang_cao(design) -> bool:
    d = _bo_dau_cach(design)
    return la_khuyen_cao(d) or d.startswith(_TIEN_TO_TANG_CAO)


def nam_cua(chuoi) -> int | None:
    m = _MAU_NAM.search(str(chuoi or ""))
    return int(m.group(0)) if m else None


def dau_da_kiem(item: dict) -> date | None:
    """Ngày ghi trong dấu «đã kiểm phiên bản DD/MM/YYYY» (gradeSource trước, rồi note/notes). Không có/ngày sai ⇒ None."""
    for khoa in ("gradeSource", "note", "notes", "versionNote"):
        m = _MAU_DA_KIEM.search(str(item.get(khoa) or ""))
        if m:
            try:
                return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
            except ValueError:
                return None
    return None


def ngay_tham_chieu(data: dict, hom_nay: date | None) -> date:
    if hom_nay:
        return hom_nay
    cap_nhat = str((data.get("meta") or {}).get("updated") or "")
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", cap_nhat)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass
    return date.today()


def kiem(data: dict, kho: Path | None, *, hom_nay: date | None = None, co_toan_van=None) -> dict:
    """Trả {'m1': [...], 'm1_cu': [...], 'm2': [...], 'khong_do': [...], 'tong': {...}}. `co_toan_van(pmid, kho)` là hàm
    của cổng (tiêm vào để test); None ⇒ M2 không đo được (mọi mục ứng viên vào `khong_do`)."""
    ref = ngay_tham_chieu(data, hom_nay)
    kq = {"ngay_tham_chieu": ref.isoformat(), "m1": [], "m1_cu": [], "m2": [], "khong_do": []}
    so_ung_vien_m2 = 0
    for it in data.get("items") or []:
        if not isinstance(it, dict):
            continue
        iid = str(it.get("id") or "(?)")
        design = it.get("design")
        nam = nam_cua(it.get("dateVersion"))
        tuoi = (ref.year - nam) if nam else None
        dong = {"id": iid, "design": str(design or ""), "dateVersion": str(it.get("dateVersion") or ""),
                "pmid": str(it.get("pmid") or ""), "doi": str(it.get("doi") or ""), "decision": str(it.get("decision") or ""),
                "nguon": str(it.get("source") or "")[:120]}
        # M1 — guideline cũ phải có dấu đã kiểm bản thay thế
        if la_khuyen_cao(design) and tuoi is not None and tuoi >= TUOI_GUIDELINE_PHAI_KIEM:
            d = dau_da_kiem(it)
            if d is None:
                kq["m1"].append(dict(dong, tuoi=tuoi))
            elif (ref - d).days > HAN_DAU_KIEM_NGAY:
                kq["m1_cu"].append(dict(dong, tuoi=tuoi, da_kiem=d.isoformat()))
        # M2 — nguồn cần toàn văn
        quyet = dong["decision"]
        can = quyet == "apply" or (quyet == "consider" and la_tang_cao(design) and tuoi is not None
                                    and tuoi <= TUOI_NGUON_MOI)
        if not can:
            continue
        so_ung_vien_m2 += 1
        pmid = dong["pmid"].strip()
        if not _PMID.match(pmid) or co_toan_van is None or kho is None or not kho.is_dir():
            kq["khong_do"].append(dong)
            continue
        if not co_toan_van(pmid, kho):
            kq["m2"].append(dong)
    kq["tong"] = {"m1": len(kq["m1"]), "m1_cu": len(kq["m1_cu"]), "m2": len(kq["m2"]),
                  "khong_do": len(kq["khong_do"]), "ung_vien_m2": so_ung_vien_m2}
    return kq


def in_bao_cao(dash: Path, kq: dict) -> None:
    print(f"Chốt tin cậy · mới nhất · toàn văn — {dash.name} (mốc {kq['ngay_tham_chieu']}; chỉ cảnh báo)")
    for d in kq["m1"]:
        print(f"  🟠 M1 [{d['id']}] {d['design'][:40]} · {d['dateVersion']} ({d['tuoi']} năm) — CHƯA ghi «đã kiểm phiên bản "
              f"DD/MM/YYYY» trong gradeSource: tìm bản thay thế cùng tổ chức (vế tiêu đề, 3 năm gần nhất) rồi ghi kết quả.")
    for d in kq["m1_cu"]:
        print(f"  🟡 M1 [{d['id']}] dấu đã kiểm phiên bản {d['da_kiem']} đã quá {HAN_DAU_KIEM_NGAY} ngày — kiểm lại.")
    for d in kq["m2"]:
        dinh_danh = f"PMID {d['pmid']}" + (f" · DOI {d['doi']}" if d["doi"] else "")
        print(f"  🟠 M2 [{d['id']}] {d['decision']} · {d['design'][:40]} · {dinh_danh} — CHƯA có toàn văn trong kho: "
              f"gom OA/Unpaywall (`tools/gom_toan_van_dashboard.py --pmid {d['pmid']} --unpaywall`) → làn Chrome uỷ quyền.")
    for d in kq["khong_do"]:
        print(f"  ⚪ M2 [{d['id']}] {d['decision']} · {d['design'][:40]} — không đo được toàn văn bằng kho (không PMID/không kho).")
    t = kq["tong"]
    print(f"Tổng: M1 {t['m1']} · M1-cũ {t['m1_cu']} · M2 {t['m2']}/{t['ung_vien_m2']} ứng viên · ⚪ {t['khong_do']}. "
          "Cần bác sĩ kiểm chứng.")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Chốt tin cậy cao nhất · mới nhất · có toàn văn cho một dashboard (chỉ cảnh báo)")
    ap.add_argument("dashboard", help="WebDashboard_*.html")
    ap.add_argument("--kho", help="kho toàn văn (mặc định: toan_van_oa cạnh dashboard — đúng kho cổng đọc)")
    ap.add_argument("--hom-nay", help="YYYY-MM-DD (mặc định meta.updated của dashboard)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    dash = Path(a.dashboard)
    data = doc_data(dash)
    if data is None:
        print(f"⚪ Không đọc được khối DATA của {dash} — KHÔNG ĐO ĐƯỢC (không phải đạt).")
        return 2
    vd = _nap("verify_dashboard.py", "_vd_kmn")
    co_tv = getattr(vd, "co_toan_van_trong_kho", None) if vd is not None else None
    kho = Path(a.kho) if a.kho else dash.parent / "toan_van_oa"
    hom_nay = date.fromisoformat(a.hom_nay) if a.hom_nay else None
    kq = kiem(data, kho, hom_nay=hom_nay, co_toan_van=co_tv)
    kq["dashboard"] = str(dash)
    if a.json:
        print(json.dumps(kq, ensure_ascii=False, indent=2))
    else:
        in_bao_cao(dash, kq)
        if co_tv is None:
            print("⚪ Thiếu hàm cổng co_toan_van_trong_kho — M2 KHÔNG ĐO ĐƯỢC.")
    if co_tv is None and kq["tong"]["ung_vien_m2"]:
        return 2
    t = kq["tong"]
    return 1 if (t["m1"] or t["m1_cu"] or t["m2"]) else 0


if __name__ == "__main__":
    sys.exit(main())
