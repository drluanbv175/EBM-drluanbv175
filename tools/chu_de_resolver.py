#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PHÂN GIẢI TÊN CHỦ ĐỀ — một cửa duy nhất cho «tên lát cắt» · «chủ đề gốc» · «tên watchlist» (20/09/2026).

Vì sao có (T1-01, đo 20/09/2026): dây chuyền chứng cứ dùng HAI không gian tên rời nhau —
  • quét ứng viên (`surveillance_scan.py --topic`) nhận TÊN WATCHLIST tiếng Việt
    («Bệnh thận mạn (CKD)», «An toàn thuốc — cảnh báo mới (MHRA/FDA/EMA)»);
  • bảng tuổi chứng cứ (`kiem_do_tuoi_chung_cu`) và gợi ý tự động đưa TÊN LÁT CẮT CamelCase
    (`BenhThanMan_CKD`, `AnToanThuoc_MHRA`).
Gõ tên lát cắt vào `ops/orchestrator.py --topic` ⇒ A2 fail 0,1 giây (rc=2), orchestrator in «FAIL HẠ TẦNG
— chạy lại khi mạng ổn» (sai: đó là lỗi tham số). Ánh xạ người-khai `EBM-Dashboards/giam-sat-chu-de.json`
đã có sẵn nhưng KHÔNG công cụ nào dùng để nối hai nửa: đo bằng hàm sống, với tên watchlist orchestrator tìm
được 8 lát cắt trong khi ánh xạ khai 52, và 20/28 chủ đề CÓ dashboard bị in sai «CHƯA có dashboard».

Nguyên tắc (BH28/BH10): KHÔNG ghép theo độ giống tên rồi coi là thật. Chỉ tin ánh xạ NGƯỜI khai; khớp
chuỗi con chỉ dùng khi DUY NHẤT; không phân giải được thì nói «khong_ro» kèm ≤5 gợi ý gần nhất — không đoán
hộ, và tuyệt đối không tự bịa truy vấn tìm kiếm lâm sàng.

Thứ tự ưu tiên: (1) đúng tên watchlist · (2) đúng tên lát cắt / chủ đề gốc (đã gấp dấu, đ→d, bỏ ký tự
phân cách) · (3) chuỗi con DUY NHẤT của tên watchlist · (4) chuỗi con nhiều tên watchlist (mơ hồ — vẫn
trả lát cắt, A2 nhận nguyên chuỗi gõ vào) · (5) không khớp.

Thuần stdlib + `tools/dang_ky_chu_de.py` (nguồn duy nhất tách tên file → lát cắt/gốc/ngày).
CLI: `python3 tools/chu_de_resolver.py "<tên>"` in kết quả JSON (chỉ đọc). Mã thoát 0 = phân giải được,
64 = không phân giải được.
"""
from __future__ import annotations

import datetime as dt
import difflib
import importlib.util
import json
import re
import sys
import unicodedata
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

GOC = Path(__file__).resolve().parents[1]
DASH = GOC / "EBM-Dashboards"
KHONG_PHAN_GIAI = 64  # EX_USAGE — «tham số sai», khác hẳn hạ tầng/mạng (rc=2)


def chuan(s: str) -> str:
    """Gấp về dạng so khớp: bỏ dấu (KỂ CẢ đ/Đ→d — NFD không tự đổi được), chữ thường, chỉ giữ chữ-số."""
    s = unicodedata.normalize("NFD", (s or "").replace("đ", "d").replace("Đ", "D"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def _nap_dang_ky():
    spec = importlib.util.spec_from_file_location("dkcd_resolver", GOC / "tools" / "dang_ky_chu_de.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["dkcd_resolver"] = m
    spec.loader.exec_module(m)
    return m


def nap_du_lieu(dash: Path = DASH) -> dict:
    """Đọc watchlist (mục đang bật), ánh xạ người-khai và kho dashboard. Tiêm được dict thay thế khi kiểm thử."""
    # Lỗi nạp KHÔNG được nuốt im lặng (phản biện đối kháng 20/09/2026, P1-05): kho/ánh xạ hỏng mà resolver trả «không có
    # lát cắt» thì orchestrator rơi về khớp-token cũ, in đúng thông điệp sai «CHƯA có dashboard», bỏ A4/B2 mà vẫn «xanh».
    # Nay ghi vào `loi`; `resolve()` chuyển thành `loi_nap` và driver dừng hạ tầng (rc=2) thay vì đoán.
    loi: list[str] = []
    wl: list[str] = []
    try:
        wl = [t.get("topic") for t in json.loads((dash / "watchlist.json").read_text(encoding="utf-8"))
              .get("topics", []) if t.get("active", True) and t.get("topic")]
    except (OSError, ValueError) as exc:
        loi.append(f"watchlist.json: {type(exc).__name__}")
    try:
        bd = json.loads((dash / "giam-sat-chu-de.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        bd = {}
        loi.append(f"giam-sat-chu-de.json: {type(exc).__name__}")
    try:
        _vd, _lat, theo_goc = _nap_dang_ky().quet_kho(dash)
    except Exception as exc:  # noqa: BLE001
        theo_goc = {}
        loi.append(f"quet_kho: {type(exc).__name__}")
    return {"watchlist": wl, "muc": bd.get("muc", {}) or {}, "khong_can": bd.get("khong_can", {}) or {},
            "theo_goc": theo_goc, "loi": loi}


def _lat_cat_moi_nhat(theo_goc: dict, cac_goc: list[str], chi_lat: str | None = None) -> list[dict]:
    """Bản MỚI NHẤT của từng lát cắt thuộc các gốc `cac_goc` (BH30: lát cắt bổ sung nhau, không thay nhau)."""
    moi: dict[str, tuple[str, Path]] = {}
    for g in cac_goc:
        for ngay, lat, p in theo_goc.get(g, []):
            if chi_lat is not None and lat != chi_lat:
                continue
            if lat not in moi or ngay > moi[lat][0]:
                moi[lat] = (ngay, p)
    hom_nay = dt.date.today()
    ra = []
    for lat, (ngay, p) in moi.items():
        try:
            tuoi = (hom_nay - dt.datetime.strptime(ngay, "%Y%m%d").date()).days
        except ValueError:
            tuoi = None
        ra.append({"ten": lat, "duong_dan": str(p), "ngay": ngay, "tuoi": tuoi})
    return sorted(ra, key=lambda x: x["ngay"])


def resolve(q: str, du_lieu: dict | None = None) -> dict:
    """Phân giải `q`. Luôn trả dict; không bao giờ raise và không bao giờ đoán.

    loai: 'watchlist' (có mục giám sát → A2 chạy được) · 'khong_can' (bản tin gộp, người khai cố ý không
    canh) · 'khong_ro'. `a2_arg` là chuỗi ĐÚNG để truyền cho `surveillance_scan.py --topic`.
    """
    d = du_lieu if du_lieu is not None else nap_du_lieu()
    wl, muc, khong_can, theo_goc = d["watchlist"], d["muc"], d["khong_can"], d["theo_goc"]
    kq = {"q": q, "loai": "khong_ro", "cach": "", "wl_topics": [], "a2_arg": None, "goc": [],
          "lat_cat": [], "ly_do": "", "gan_dung": [], "loi_nap": "; ".join(d.get("loi") or [])}
    cq = chuan(q)
    if not cq:
        kq["ly_do"] = "tên chủ đề rỗng"
        return kq

    def _theo_wl(cac_wl: list[str], cach: str, a2_arg: str) -> dict:
        goc = sorted(g for g, w in muc.items() if w in cac_wl)
        kq.update(loai="watchlist", cach=cach, wl_topics=list(cac_wl), a2_arg=a2_arg, goc=goc,
                  lat_cat=_lat_cat_moi_nhat(theo_goc, goc))
        return kq

    # (1) đúng tên watchlist
    dung = [w for w in wl if chuan(w) == cq]
    if dung:
        return _theo_wl(dung[:1], "ten-watchlist", dung[0])

    # (2) đúng tên lát cắt hoặc chủ đề gốc — dùng ánh xạ NGƯỜI khai
    tap_lat = {lat: g for g, lst in theo_goc.items() for _n, lat, _p in lst}
    lat_khop = [lat for lat in tap_lat if chuan(lat) == cq]
    goc_khop = [g for g in theo_goc if chuan(g) == cq]
    if lat_khop or goc_khop:
        # ƯU TIÊN CHỦ ĐỀ GỐC khi tên gõ trùng CẢ gốc lẫn một lát cắt (vd `COPD`, `DauDau`: lát cắt `COPD` cùng tên
        # gốc `COPD` có 3 lát cắt anh em). Phản biện 20/09/2026 (P-01) bắt bản đầu rẽ nhánh lát cắt trước ⇒ chỉ lấy
        # MỘT lát cắt, A4/B2 bỏ sót 3 lát cắt còn lại của chủ đề. Chỉ dùng cấp lát cắt khi tên đó KHÔNG phải tên gốc.
        if lat_khop and not goc_khop:
            lat = lat_khop[0]
            g = tap_lat[lat]
            cac_goc, chi_lat, cach = [g], lat, "lat-cat"
        else:
            g = goc_khop[0]
            chi_lat, cach = None, "chu-de-goc"
            w0 = muc.get(g)
            # cấp CHỦ ĐỀ: lấy mọi gốc cùng trỏ một mục watchlist — A2 quét theo mục watchlist nên các gốc
            # này cùng được «làm mới» bởi một lượt quét (vd SuyTim + TienLuongSuyTim).
            cac_goc = sorted(x for x, w in muc.items() if w == w0) if w0 else [g]
        if g in khong_can:
            kq.update(loai="khong_can", cach=cach, goc=[g], ly_do=str(khong_can[g]),
                      lat_cat=_lat_cat_moi_nhat(theo_goc, [g], chi_lat))
            return kq
        w = muc.get(g)
        if w:
            kq.update(loai="watchlist", cach=cach, wl_topics=[w], a2_arg=w, goc=cac_goc,
                      lat_cat=_lat_cat_moi_nhat(theo_goc, cac_goc, chi_lat))
            return kq
        kq.update(loai="khong_ro", cach=cach, goc=[g],
                  lat_cat=_lat_cat_moi_nhat(theo_goc, [g], chi_lat),
                  ly_do=f"chủ đề gốc «{g}» CHƯA khai ánh xạ trong giam-sat-chu-de.json — máy không đoán hộ (BH28)")
        return kq

    # (3)/(4) chuỗi con của tên watchlist — CHỈ khi đủ dài (≥ 4 ký tự sau khi gấp): chuỗi 1–3 ký tự («a», «da», «Đ») khớp gần
    # cả kho và bị coi «duy nhất, chắc» (P1-02/P1-16). Nhiều mục khớp KHÔNG được truyền chuỗi thô cho A2: bộ khớp của A2
    # (`surveillance_scan._bo_dau`: chỉ NFD, KHÔNG gấp đ→d, giữ dấu cách) khác bộ này nên «dau» khớp 4 mục ở đây nhưng 0 ở A2
    # (P1-01) — bắt người gõ chọn TÊN ĐẦY ĐỦ.
    con = [w for w in wl if len(cq) >= 4 and cq in chuan(w)]
    if len(con) == 1:
        return _theo_wl(con, "chuoi-con-duy-nhat", con[0])
    if len(con) > 1:
        kq["cach"] = "chuoi-con-nhieu"
        kq["gan_dung"] = list(con)
        kq["ly_do"] = f"«{q}» khớp {len(con)} mục watchlist — gõ TÊN ĐẦY ĐỦ của một mục"
        return kq

    # (5) không khớp: gợi ý gần nhất, KHÔNG đoán
    ung_vien = {chuan(x): x for x in list(wl) + list(tap_lat) + list(theo_goc)}
    gan = difflib.get_close_matches(cq, list(ung_vien), n=5, cutoff=0.5)
    kq["gan_dung"] = [ung_vien[g] for g in gan]
    kq["ly_do"] = "không khớp tên watchlist, lát cắt hay chủ đề gốc nào"
    return kq


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return KHONG_PHAN_GIAI
    kq = resolve(" ".join(sys.argv[1:]))
    print(json.dumps(kq, ensure_ascii=False, indent=2))
    return 0 if kq["loai"] != "khong_ro" or kq["lat_cat"] else KHONG_PHAN_GIAI


if __name__ == "__main__":
    raise SystemExit(main())
