#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SỔ BẢO ĐẢM ĐỌC TOÀN VĂN — mọi mục «Áp dụng ngay» phải được ĐỌC TOÀN VĂN (04/10/2026, bác sĩ: «Hãy xây dựng đảm bảo việc
đọc toàn văn cho tôi»).

BỐN LỚP (công cụ này là lớp 3; nguồn sự thật dùng chung là `doc_toan_van_co_nguoi.bao_phu_cuc_bo`):
  1. NGUỒN SỰ THẬT — trạng thái từng PMID từ kho `EBM-Dashboards/toan_van_oa/`: toàn văn máy đọc (XML JATS · PDF/HTML có giấy phép
     mở · TDM · phiên Chrome), hồ sơ làn trình duyệt có bác sĩ, hoặc «bác sĩ đã đọc trực tiếp» (`trinh_duyet/bac-si-da-doc.jsonl`).
  2. CỔNG (`verify_dashboard.kiem_toan_van_apply`, BÁNH CÓC): mục apply CHƯA đọc toàn văn ⇒ CHẶN; riêng các mục ĐÃ TỒN lúc dựng
     bảo đảm nằm trong SỔ NỢ (`EBM-Dashboards/no-toan-van-apply.json`) ⇒ chỉ cảnh báo tới HẠN, quá hạn ⇒ chặn. Sổ nợ chỉ GIẢM:
     mục mới không bao giờ được thêm vào (lập một lần; gia hạn phải có NGUYÊN VĂN lời bác sĩ).
  3. SỔ — báo cáo độ phủ theo mức quyết định, danh sách nợ kèm cách trả từng mục (công cụ này).
  4. GIÁC QUAN — `tu_de_xuat_viec.py` nhắc nợ toàn văn ở hòm việc mỗi phiên (không để chìm).

TRẢ NỢ một mục (bất kỳ cách nào): (a) máy lấy được toàn văn hợp lệ (`gom_toan_van_dashboard.py --pmid … --unpaywall`);
(b) làn trình duyệt có bác sĩ (`doc_toan_van_co_nguoi.py --pmid …` → phiếu; trích xuất → `--nap`); (c) bác sĩ tự đọc rồi
`doc_toan_van_co_nguoi.py --bac-si-da-doc <PMID> --ghi-chu "<kết luận>" --ghi`; (d) bác sĩ hạ mục xuống «Cân nhắc».

Dùng:
  python3 tools/so_toan_van.py                         # báo cáo (mặc định)
  python3 tools/so_toan_van.py --json
  python3 tools/so_toan_van.py --tao-no --han 2026-11-03 --can-cu "<nguyên văn lời bác sĩ>" [--ghi]
  python3 tools/so_toan_van.py --gia-han 2026-12-03 --can-cu "<nguyên văn lời bác sĩ>" [--ghi]
Mã thoát: 0 · 1 = còn mục apply chưa đọc toàn văn NGOÀI sổ nợ hoặc nợ QUÁ HẠN (cổng đang chặn) · 2 = không đo được (vắng kho)
· 3 = từ chối ghi.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
DASH = REPO / "EBM-Dashboards"
TEN_SO_NO = "no-toan-van-apply.json"
CAN_CU_MIN = 20
HAN_TOI_DA_NGAY = 90


def _nap(ten: str, duong: Path):
    sp = importlib.util.spec_from_file_location(ten, duong)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


def doc_so_no(dash: Path) -> dict | None:
    """Sổ nợ toàn văn; vắng ⇒ None; hỏng ⇒ {"hong": lý do} (cổng coi như vắng — fail-closed)."""
    tep = Path(dash) / TEN_SO_NO
    if not tep.exists():
        return None
    try:
        d = json.loads(tep.read_text(encoding="utf-8"))
        date.fromisoformat(d["han"])
        if not isinstance(d.get("muc"), list):
            raise ValueError("muc không phải danh sách")
        return d
    except (OSError, ValueError, KeyError, TypeError) as e:
        return {"hong": f"{type(e).__name__}: {e}"}


def quet_muc(dash: Path, kho: Path, hom_nay: date | None = None) -> list[dict]:
    """Mọi mục có PMID chính (`pmid:`) trong các dashboard: {dashboard, item, pmid, decision, trang_thai, da_doc}."""
    vd = _nap("_vd_stv", REPO / "sync/skills/cap-nhat-chung-cu-y-khoa/tools/verify_dashboard.py")
    dtv = _nap("_dtv_stv", REPO / "tools/doc_toan_van_co_nguoi.py")
    tho = []
    for f in sorted(Path(dash).glob("WebDashboard_*.html")):
        blk = vd.extract_data_block(f.read_text(encoding="utf-8", errors="replace"))
        if not blk:
            continue
        for ch in vd.split_items(blk):
            pm = (vd.field(ch, "pmid") or "").strip()
            if re.fullmatch(r"\d{6,9}", pm):
                tho.append({"dashboard": f.stem, "item": vd.field(ch, "id") or "(?)", "pmid": pm,
                            "decision": vd.field(ch, "decision") or "khac"})
    tt = dtv.bao_phu_cuc_bo(sorted({m["pmid"] for m in tho}), kho, hom_nay)
    for m in tho:
        m["trang_thai"] = tt[m["pmid"]]
        m["da_doc"] = tt[m["pmid"]] in dtv.TRANG_THAI_DA_PHU
    return tho


def phan_loai_no(muc: list[dict], so_no: dict | None, hom_nay: date) -> dict:
    """Mục apply chưa đọc ⇒ «trong_han» (có trong sổ nợ, chưa quá hạn) · «qua_han» · «ngoai_so» (mục MỚI — cổng chặn ngay)."""
    chua = [m for m in muc if m["decision"] == "apply" and not m["da_doc"]]
    khoa = set()
    han = None
    if so_no and "hong" not in so_no:
        han = date.fromisoformat(so_no["han"])
        khoa = {(x.get("dashboard"), x.get("item"), x.get("pmid")) for x in so_no["muc"] if isinstance(x, dict)}
    ra = {"trong_han": [], "qua_han": [], "ngoai_so": [], "han": han.isoformat() if han else None}
    for m in chua:
        if (m["dashboard"], m["item"], m["pmid"]) in khoa:
            ra["trong_han" if hom_nay <= han else "qua_han"].append(m)
        else:
            ra["ngoai_so"].append(m)
    return ra


def bao_cao(muc: list[dict], no: dict, so_no: dict | None, hom_nay: date) -> list[str]:
    dong = [f"SỔ BẢO ĐẢM ĐỌC TOÀN VĂN — {hom_nay.isoformat()}", ""]
    for dec, ten in (("apply", "Áp dụng ngay"), ("consider", "Cân nhắc"), ("notyet", "Chưa đủ")):
        nhom = {m["pmid"] for m in muc if m["decision"] == dec}
        doc = {m["pmid"] for m in muc if m["decision"] == dec and m["da_doc"]}
        if nhom:
            dong.append(f"  {ten:<13} đã đọc toàn văn {len(doc):>4}/{len(nhom):<4} PMID ({100 * len(doc) // len(nhom)}%)")
    dong.append("")
    if so_no and "hong" in so_no:
        dong.append(f"🔴 SỔ NỢ KHÔNG ĐỌC ĐƯỢC ({so_no['hong']}) — cổng coi như KHÔNG có sổ ⇒ mọi mục apply chưa đọc đều bị CHẶN.")
    if no["ngoai_so"]:
        dong.append(f"🔴 {len(no['ngoai_so'])} mục apply CHƯA đọc toàn văn NGOÀI sổ nợ — cổng ĐANG CHẶN:")
        dong += [f"     · {m['dashboard'].replace('WebDashboard_EBM_VanDeCuThe_', '')} {m['item']} PMID {m['pmid']} ({m['trang_thai']})"
                 for m in no["ngoai_so"]]
    if no["qua_han"]:
        dong.append(f"🔴 {len(no['qua_han'])} mục NỢ QUÁ HẠN {no['han']} — cổng ĐANG CHẶN:")
        dong += [f"     · {m['dashboard'].replace('WebDashboard_EBM_VanDeCuThe_', '')} {m['item']} PMID {m['pmid']}" for m in no["qua_han"]]
    if no["trong_han"]:
        con = (date.fromisoformat(no["han"]) - hom_nay).days
        dong.append(f"🟠 {len(no['trong_han'])} mục NỢ toàn văn (hạn {no['han']}, còn {con} ngày — sau hạn cổng CHẶN):")
        dong += [f"     · {m['dashboard'].replace('WebDashboard_EBM_VanDeCuThe_', '')} {m['item']} PMID {m['pmid']} ({m['trang_thai']})"
                 for m in no["trong_han"]]
    if not (no["ngoai_so"] or no["qua_han"] or no["trong_han"]):
        dong.append("🟢 Mọi mục «Áp dụng ngay» có PMID đã được đọc toàn văn (máy, làn trình duyệt, hoặc bác sĩ đã đọc).")
    else:
        pm = sorted({m["pmid"] for k in ("ngoai_so", "qua_han", "trong_han") for m in no[k]})
        dong += ["", "Cách trả nợ (bất kỳ cách nào cho từng PMID):",
                 f"  (a) máy lấy bản hợp lệ:   python3 tools/gom_toan_van_dashboard.py --pmid {' '.join(pm)} --unpaywall",
                 f"  (b) làn trình duyệt:      python3 tools/doc_toan_van_co_nguoi.py --pmid {' '.join(pm)}",
                 "  (c) bác sĩ đã tự đọc:     python3 tools/doc_toan_van_co_nguoi.py --bac-si-da-doc <PMID> --ghi-chu \"<kết luận>\" --ghi",
                 "  (d) bác sĩ hạ mục xuống «Cân nhắc» (quyết định lâm sàng của bác sĩ)."]
    khong_pmid = "Mục không có PMID (guideline chỉ có URL/DOI) chưa được sổ này đo — đọc trực tiếp nguồn chính thức."
    return dong + ["", khong_pmid, "Cần bác sĩ kiểm chứng."]


def ghi_so_no(dash: Path, muc_no: list[dict], han: str, can_cu: str, *, ghi: bool, cu: dict | None,
              hom_nay: date) -> tuple[int, str]:
    """Lập sổ nợ (CHỈ khi chưa có) hoặc gia hạn (giữ nguyên danh sách — bánh cóc). Mặc định chạy thử."""
    if len((can_cu or "").strip()) < CAN_CU_MIN:
        return 3, f"✗ phải ghi NGUYÊN VĂN lời bác sĩ (≥ {CAN_CU_MIN} ký tự) — agent không tự lập/gia hạn sổ nợ"
    try:
        h = date.fromisoformat(han)
    except ValueError:
        return 3, f"✗ hạn «{han}» sai dạng YYYY-MM-DD"
    if not (hom_nay < h <= hom_nay.fromordinal(hom_nay.toordinal() + HAN_TOI_DA_NGAY)):
        return 3, f"✗ hạn phải sau hôm nay và không quá {HAN_TOI_DA_NGAY} ngày"
    if cu is None:
        so = {"_about": "Sổ NỢ toàn văn (bánh cóc): mục apply CHƯA đọc toàn văn đã tồn lúc dựng bảo đảm 04/10/2026. Cổng chỉ "
                        "cảnh báo các mục này tới «han»; quá hạn ⇒ CHẶN. Mục mới KHÔNG bao giờ được thêm vào. Sinh bằng "
                        "tools/so_toan_van.py — không sửa tay.",
              "tao_luc": datetime.now().isoformat(timespec="seconds"), "han": h.isoformat(), "can_cu": can_cu.strip(),
              "muc": [{"dashboard": m["dashboard"], "item": m["item"], "pmid": m["pmid"], "trang_thai": m["trang_thai"]}
                      for m in muc_no], "lich_su": []}
        viec = f"lập sổ nợ {len(muc_no)} mục, hạn {h.isoformat()}"
    else:
        if "hong" in cu:
            return 3, "✗ sổ nợ hiện có KHÔNG đọc được — không gia hạn đè lên sổ hỏng; bác sĩ xem tệp trước"
        so = dict(cu)
        so.setdefault("lich_su", []).append({"luc": datetime.now().isoformat(timespec="seconds"), "han_cu": cu["han"],
                                             "han_moi": h.isoformat(), "can_cu": can_cu.strip()})
        so["han"] = h.isoformat()
        viec = f"gia hạn {cu['han']} → {h.isoformat()} (danh sách giữ nguyên {len(cu['muc'])} mục)"
    if not ghi:
        return 0, f"(chạy thử) sẽ {viec} — thêm --ghi để ghi {TEN_SO_NO}"
    (Path(dash) / TEN_SO_NO).write_text(json.dumps(so, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0, f"✓ đã {viec} → {Path(dash) / TEN_SO_NO}"


def main(argv: list[str] | None = None, *, dash: Path | None = None, hom_nay: date | None = None) -> int:
    ap = argparse.ArgumentParser(description="Sổ bảo đảm đọc toàn văn cho mục «Áp dụng ngay»")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--tao-no", action="store_true", help="lập sổ nợ cho các mục apply chưa đọc (chỉ khi CHƯA có sổ)")
    ap.add_argument("--gia-han", metavar="YYYY-MM-DD", help="gia hạn sổ nợ (danh sách giữ nguyên)")
    ap.add_argument("--han", metavar="YYYY-MM-DD")
    ap.add_argument("--can-cu", default=None, help="NGUYÊN VĂN lời bác sĩ")
    ap.add_argument("--ghi", action="store_true")
    ap.add_argument("--dash", type=Path, default=None, help="thư mục EBM-Dashboards khác (mặc định: cạnh repo)")
    a = ap.parse_args(argv)
    dash = Path(dash or a.dash or DASH)
    hom_nay = hom_nay or date.today()
    kho = dash / "toan_van_oa"
    if not kho.is_dir():
        print(f"⚪ KHÔNG ĐO ĐƯỢC — không thấy kho {kho} (EBM-Dashboards/ vắng ở cây này). KHÔNG phải «đủ toàn văn».")
        return 2
    muc = quet_muc(dash, kho, hom_nay)
    so_no = doc_so_no(dash)
    if a.tao_no or a.gia_han:
        if a.tao_no and so_no is not None:
            print("✗ ĐÃ có sổ nợ — sổ chỉ được lập MỘT lần (bánh cóc: mục mới không vào nợ). Gia hạn: --gia-han.")
            return 3
        if a.gia_han and so_no is None:
            print("✗ chưa có sổ nợ để gia hạn — lập bằng --tao-no trước")
            return 3
        muc_no = [m for m in muc if m["decision"] == "apply" and not m["da_doc"]]
        rc, thong_diep = ghi_so_no(dash, muc_no, a.han if a.tao_no else a.gia_han, a.can_cu or "", ghi=a.ghi,
                                   cu=so_no if a.gia_han else None, hom_nay=hom_nay)
        print(thong_diep)
        return rc
    no = phan_loai_no(muc, so_no, hom_nay)
    if a.json:
        print(json.dumps({"ngay": hom_nay.isoformat(), "han": no["han"],
                          "dem": {k: len(no[k]) for k in ("ngoai_so", "qua_han", "trong_han")},
                          "chua_doc_apply": no["ngoai_so"] + no["qua_han"] + no["trong_han"]}, ensure_ascii=False, indent=1))
    else:
        print("\n".join(bao_cao(muc, no, so_no, hom_nay)))
    return 1 if (no["ngoai_so"] or no["qua_han"] or (so_no and "hong" in so_no)) else 0


if __name__ == "__main__":
    raise SystemExit(main())
