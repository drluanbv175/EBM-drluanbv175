#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TRUY NGUYÊN TOÀN SỔ (E2 trên ledger) — LÔ 2 PHA 2, 15/08/2026.

Trả lời cho TOÀN BỘ 1193 thẻ EBM_MASTER: «nguồn còn nguyên vẹn không, đã kiểm
lúc nào, có thẻ APPLY nào đang đứng trên bài ĐÃ RÚT không?» — bằng ba lớp bằng
chứng ĐANG CÓ, không gọi mạng (mạng bệnh viện chập chờn là lý do sổ xác minh
tồn tại; công cụ này ĐỌC bằng chứng tích luỹ, không đo lại):

  1. Retraction Watch NGOẠI TUYẾN (30.851 PMID có phán quyết) — tín hiệu DƯƠNG.
  2. Sổ xác minh nguồn `.so-xac-minh-nguon.json` — tồn tại (hạn 180 ngày) +
     trạng thái rút (hạn 30 ngày), chỉ ghi THÀNH CÔNG.
  3. Ledger — decision hiện hành để bắt tổ hợp nguy hiểm APPLY × ĐÃ RÚT.

Luật gộp giữ nguyên bất đối xứng của chuỗi rút bài: DƯƠNG từ bất kỳ lớp nào là
nhận; «ok» chỉ từ sổ khi nguồn SỐNG đã thật sự trả bản ghi; còn lại = KHÔNG BIẾT
(fail-closed, BH27: «không kiểm được» bị TÍNH là vấn đề coverage, không lặng im).

Ra `reports/provenance-<ngày>.md`. Tổ hợp APPLY × ĐÃ RÚT còn ghi một dòng 🔴 vào
`alerts/<ngày>.md` (idempotent — không nhân đôi khi chạy lại). KHÔNG đổi
decision nào (BH10). Mã thoát: 0 = không phát hiện dương tính · 1 = CÓ phát hiện
nội dung (đã rút/EoC) · 2 = HẠ TẦNG hỏng (thiếu cả RW lẫn sổ — «không kiểm được»
tuyệt đối không được đọc thành «sạch», BH08/BH27).
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

GOC = Path(__file__).resolve().parents[1]
# VÁ 07/09/2026: `GOC / "medical-ebm-automation"` (dòng _nap_rw() dưới) giả định
# LỒNG — sai trên phiên cloud (anh em của GOC). Dùng duong_goc() — xem
# tools/ban_sao_tran.py.
import importlib.util as _ilu_pl  # noqa: E402
_sp_pl = _ilu_pl.spec_from_file_location(
    "_bst_pl", Path(__file__).resolve().parent / "ban_sao_tran.py")
_bst_pl = _ilu_pl.module_from_spec(_sp_pl)
_sp_pl.loader.exec_module(_bst_pl)
_MEA_GOC = _bst_pl.duong_goc("medical-ebm-automation", GOC) or (GOC / "medical-ebm-automation")
LEDGER = GOC / "EBM_MASTER" / "EBM_MASTER.json"
SO = GOC / "EBM-Dashboards" / ".so-xac-minh-nguon.json"
HAN_TON_TAI = 180  # ngày — metadata gần bất biến
HAN_RUT = 30       # ngày — bài tốt hôm nay có thể bị rút ngày mai
DUONG_TINH = {"retracted", "expression_of_concern"}


def _tuoi_ngay(iso: str | None) -> float | None:
    if not iso:
        return None
    try:
        return (datetime.now() - datetime.fromisoformat(str(iso)[:19])).days
    except ValueError:
        return None


# Mức rút bài của MỘT thẻ — hợp đồng dùng chung (vá 26/09/2026, #5) giữa sổ truy nguyên
# này và `tools/tra_diem_kham.py` (điểm khám), để hai nơi KHÔNG BAO GIỜ phân loại lệch nhau.
MUC_DUONG_TINH = frozenset({"duong", "rut_va_thay", "eoc"})
MUC_RUT = ("duong", "rut_va_thay", "eoc", "ok_con_han", "ok_qua_han", "khong_biet")


def tra_muc_so(src: dict, so: dict) -> dict | None:
    """Bản ghi sổ xác minh của nguồn: khoá `pmid:` trước, rồi `doi:` (nguyên dạng → chữ thường)."""
    pmid, doi = src.get("pmid"), src.get("doi")
    muc_so = so.get(f"pmid:{pmid}") if pmid else None
    if muc_so is None and doi:
        muc_so = so.get(f"doi:{doi}") or so.get(f"doi:{str(doi).lower()}")
    return muc_so if isinstance(muc_so, dict) else None


def trang_thai_rut_the(card: dict, rw, so: dict | None) -> dict:
    """Phân loại trạng thái rút bài của MỘT thẻ từ bằng chứng ĐANG CÓ (không gọi mạng).

    Trả ``{"muc", "ly_do", "nguon", "thong_bao", "muc_so"}`` với ``muc`` ∈ ``MUC_RUT``:
      • ``duong`` (đã rút) · ``rut_va_thay`` (rút & đăng lại) · ``eoc`` (thông báo quan ngại) —
        DƯƠNG từ BẤT KỲ lớp nào là nhận: Retraction Watch ngoại tuyến (PMID; DOI nếu nền có
        ``tra_doi``) HOẶC sổ xác minh (``ghi_chu_rut`` dương tính, hay cờ dính ``da_rut``/
        ``quan_ngai`` — cờ dính vẫn còn khi một lượt sau ghi đè ``ghi_chu_rut='ok'``).
      • ``ok_con_han`` — CHỈ khi sổ ghi ``ok`` từ nguồn sống, không có cờ ``nghi_ma``, và
        ``kiem_rut_luc`` còn trong ``HAN_RUT`` ngày. Retraction Watch KHÔNG BAO GIỜ nói «ok».
      • ``ok_qua_han`` — sổ ghi ok nhưng quá hạn/không rõ ngày kiểm.
      • ``khong_biet`` — mọi trường hợp còn lại (fail-closed; không bao giờ đọc thành «sạch»).
    Chỉ ĐỌC — không đổi decision, không ghi sổ (BH10).
    """
    so = so if isinstance(so, dict) else {}
    src = card.get("source") if isinstance(card.get("source"), dict) else {}
    pmid, doi = src.get("pmid"), src.get("doi")
    muc_so = tra_muc_so(src, so)
    bg = muc_so or {}

    # Lớp 1 — DƯƠNG từ RW ngoại tuyến (PMID; DOI khi nền có chỉ mục DOI).
    bg_rw = rw.tra(str(pmid)) if (rw and pmid) else None
    if not bg_rw and rw and doi and callable(getattr(rw, "tra_doi", None)):
        bg_rw = rw.tra_doi(str(doi))
    if bg_rw and not isinstance(bg_rw, dict):
        bg_rw = {"status": ""}  # kết quả lạ nhưng KHÁC rỗng ⇒ vẫn là dương tính (thận trọng)
    # Lớp 2 — sổ xác minh.
    ghi_rut = bg.get("ghi_chu_rut")
    so_duong = ghi_rut in DUONG_TINH or bool(bg.get("da_rut")) or bool(bg.get("quan_ngai"))

    if bg_rw or so_duong:
        if bg_rw or ghi_rut in DUONG_TINH:
            ly_do = (bg_rw or {}).get("reason") or ghi_rut   # giữ nguyên công thức cũ
        else:
            # Dương tính CHỈ từ cờ dính (ghi_chu_rut có thể đã bị lượt sau ghi 'ok'):
            # nói rõ nguồn gốc, đừng in «ok» cạnh một nguồn dương tính.
            ly_do = ("retracted (cờ da_rut của sổ xác minh)" if bg.get("da_rut")
                     else "expression_of_concern (cờ quan_ngai của sổ xác minh)")
        # MỨC phải nói đúng (BH34): sổ xác minh đã phân biệt sẵn rút-và-thay
        # (trường `rut_va_thay` + DOI thông báo) — đọc nó, đừng đoán lại từ chuỗi.
        rr = ("retract and replace" in str(ly_do).lower() or bool(bg.get("rut_va_thay")))
        tb = bg.get("thong_bao_rut_doi")
        if tb:
            ly_do = f"{ly_do} · thông báo: doi:{tb}"
        # Mức RÚT khi bất kỳ lớp nào nói rút; RW trả trạng thái lạ (không phải EoC) cũng xếp
        # mức rút — chiều thận trọng, giữ luật cũ «mọi kết quả RW khác None là dương tính».
        la_rut = (bool(bg.get("da_rut")) or ghi_rut == "retracted"
                  or bool(bg_rw and bg_rw.get("status") != "expression_of_concern"))
        muc = "rut_va_thay" if rr else ("duong" if la_rut else "eoc")
        nguon = (["Retraction Watch"] if bg_rw else []) + (["sổ xác minh"] if so_duong else [])
        thong_bao = ""
        if (bg_rw or {}).get("notice_pmid"):
            thong_bao = f"PMID {bg_rw['notice_pmid']}"
        elif (bg_rw or {}).get("notice_doi") or tb:
            thong_bao = f"doi:{(bg_rw or {}).get('notice_doi') or tb}"
        return {"muc": muc, "ly_do": str(ly_do)[:120], "nguon": nguon,
                "thong_bao": thong_bao, "muc_so": muc_so}

    # ÂM «ok» chỉ khi sổ ghi ok TỪ NGUỒN SỐNG, không nghi ma, và còn trong hạn 30 ngày.
    tuoi_rut = _tuoi_ngay(bg.get("kiem_rut_luc"))
    if ghi_rut == "ok" and not bg.get("nghi_ma"):
        muc = "ok_con_han" if (tuoi_rut is not None and tuoi_rut <= HAN_RUT) else "ok_qua_han"
    else:
        muc = "khong_biet"
    return {"muc": muc, "ly_do": str(ghi_rut or "")[:120], "nguon": ["sổ xác minh"] if muc_so else [],
            "thong_bao": "", "muc_so": muc_so}


def _nap_rw():
    """Nạp chỉ mục Retraction Watch ngoại tuyến (đã stdlib-safe từ 15/08)."""
    sys.path.insert(0, str(_MEA_GOC))
    try:
        from app.sources.retraction_watch import RetractionWatchIndex  # noqa: PLC0415
        rw = RetractionWatchIndex()
        return rw if rw.san_sang() else None
    except Exception as exc:  # noqa: BLE001 — hạ tầng hỏng phải HIỆN, không chết cả quét
        print(f"⚠️ Không nạp được Retraction Watch: {exc}")
        return None


def main() -> int:
    try:
        cards = json.loads(LEDGER.read_text(encoding="utf-8"))["evidence_cards"]
    except (OSError, ValueError, KeyError) as exc:
        print(f"🔴 HẠ TẦNG: không đọc được ledger: {exc}")
        return 2

    rw = _nap_rw()
    try:
        so = json.loads(SO.read_text(encoding="utf-8")).get("muc", {})
    except (OSError, ValueError):
        so = {}
    if rw is None and not so:
        print("🔴 HẠ TẦNG: thiếu CẢ Retraction Watch lẫn sổ xác minh — không có "
              "căn cứ nào; «không kiểm được» KHÔNG được đọc thành «sạch».")
        return 2

    duong: list[dict] = []      # phát hiện dương tính (đã rút / EoC)
    trang_thai = Counter()      # phân loại từng thẻ
    tuoi_qua_han = Counter()
    for c in cards:
        src = c.get("source") if isinstance(c.get("source"), dict) else {}
        pmid, doi = src.get("pmid"), src.get("doi")
        # Phân loại qua hàm DÙNG CHUNG với tra_diem_kham (vá 26/09/2026, #5) — một luật gộp.
        kq = trang_thai_rut_the(c, rw, so)
        muc_so = kq["muc_so"]

        if kq["muc"] in MUC_DUONG_TINH:
            duong.append({"id": c.get("id"), "pmid": pmid, "doi": doi,
                          "decision": c.get("decision"),
                          "muc": "RÚT & ĐĂNG LẠI (đối chiếu bản đã thay)" if kq["muc"] == "rut_va_thay"
                                 else "ĐÃ RÚT/EoC (không dùng)",
                          "ly_do": kq["ly_do"]})
            trang_thai["dương tính"] += 1
            continue

        # ÂM «ok» chỉ khi sổ ghi ok TỪ NGUỒN SỐNG và còn trong hạn 30 ngày.
        if kq["muc"] == "ok_con_han":
            trang_thai["ok (rút bài còn hạn 30d)"] += 1
        elif kq["muc"] == "ok_qua_han":
            trang_thai["ok NHƯNG QUÁ HẠN 30d — cần kiểm lại"] += 1
            tuoi_qua_han["rút bài quá 30d"] += 1
        else:
            trang_thai["KHÔNG BIẾT (chưa nguồn sống nào kết luận)"] += 1

        tuoi_tt = _tuoi_ngay((muc_so or {}).get("xac_minh_luc"))
        if muc_so is None:
            tuoi_qua_han["chưa từng xác minh tồn tại"] += 1
        elif tuoi_tt is not None and tuoi_tt > HAN_TON_TAI:
            tuoi_qua_han["tồn tại quá 180d"] += 1

    # ── Tổ hợp nguy hiểm: APPLY × dương tính → alert idempotent ──────────────
    apply_rut = [h for h in duong if h["decision"] == "apply"]
    if apply_rut:
        ad = GOC / "alerts"
        ad.mkdir(exist_ok=True)
        af = ad / f"{date.today().isoformat()}.md"
        cu = af.read_text(encoding="utf-8") if af.exists() else \
            f"# CẢNH BÁO KHẨN — {date.today().isoformat()}\n\n"
        for h in apply_rut:
            khoa = f"PMID {h['pmid']}" if h["pmid"] else f"DOI {h['doi']}"
            if khoa not in cu:
                cu += (f"- 🔴 LEDGER: thẻ {h['id']} đang **apply** trên nguồn "
                       f"{h['muc']} ({khoa}) — {h['ly_do']}\n")
        af.write_text(cu, encoding="utf-8")

    # ── Báo cáo ──────────────────────────────────────────────────────────────
    # Báo cáo «bị vượt qua» chỉ được trích khi HỢP LỆ (manifest JSON đi kèm, dò TOÀN KHO, không PMID hỏng) — chỉ đếm
    # «có tệp .txt» là đúng lỗi 16/09: tệp 476 byte in 🟢 trong khi NCBI đã trả bản lỗi cho cả 163 PMID.
    try:
        import importlib.util as _ilu
        _sp = _ilu.spec_from_file_location("_kcv_pl", GOC / "tools" / "kiem_chung_cu_vuot_qua.py")
        _kcv = _ilu.module_from_spec(_sp)
        _sp.loader.exec_module(_kcv)
        vq_info = _kcv.doc_bao_cao_vuot_qua(GOC / "EBM-Dashboards" / "derivatives")
    except Exception as e:  # noqa: BLE001 — sổ truy nguyên không được chết vì công cụ phụ
        vq_info = {"hop_le": False, "ly_do": f"không nạp được công cụ đọc báo cáo: {type(e).__name__}", "pmids": [],
                   "nguon": None, "ngay": None}
    dong = [f"# TRUY NGUYÊN TOÀN SỔ — {date.today().isoformat()}", "",
            f"- Tổng: **{len(cards)} thẻ** · căn cứ: RW ngoại tuyến "
            f"{'✓' if rw else '✗'} + sổ xác minh {len(so)} mục",
            f"- Phân loại: {dict(trang_thai)}",
            f"- Quá hạn/thiếu phủ: {dict(tuoi_qua_han) or '—'}", ""]
    dong.append("## 🔴 Dương tính (đã rút / EoC / rút-đăng-lại)")
    if not duong:
        dong.append("- (không phát hiện trong phạm vi căn cứ hiện có)")
    for h in duong[:20]:
        dong.append(f"- {h['id']} · decision=**{h['decision']}** · "
                    f"PMID {h['pmid']} / DOI {h['doi']} — {h['muc']}: {h['ly_do']}")
    dong += ["", "## Chứng cứ bị vượt qua (quét quý — công cụ riêng)",
             (f"- Bản hợp lệ mới nhất: `{vq_info['nguon']}` (ngày {vq_info['ngay']}) — "
              f"{len(vq_info['pmids'])} PMID có tổng hợp mới hơn"
              if vq_info.get("hop_le") else
              f"- ⚪ KHÔNG có báo cáo hợp lệ: {vq_info.get('ly_do')} — 'chưa biết', KHÔNG phải 'không có bài mới hơn'"),
             "", "## Đối chiếu số liệu (mẫu ≥10%)",
             "- Đo gần nhất 14/08/2026 bằng `tools/kiem_so_lieu.py`: 24/25 mục khớp "
             "abstract (1 ⚪ không kết luận) — ĐÓ LÀ MỘT MẪU 25 mục, không phải cả kho. Chạy lại khi cần: "
             "`python3 tools/kiem_so_lieu.py --chi-apply --gioi-han 25` (mẫu) hoặc không cờ (toàn kho); "
             "mã thoát 2 = KHÔNG đo được, không phải sạch.",
             "", "> Chỉ ĐỌC và BÁO — không đổi decision nào (BH10). "
             "Cần bác sĩ kiểm chứng."]
    bc = GOC / "reports" / f"provenance-{date.today().isoformat()}.md"
    bc.parent.mkdir(exist_ok=True)
    bc.write_text("\n".join(dong) + "\n", encoding="utf-8")

    print(f"{'🔴' if duong else '🟢'} {len(cards)} thẻ — dương tính {len(duong)} "
          f"(trong đó APPLY: {len(apply_rut)}) → {bc.relative_to(GOC)}")
    for k, v in trang_thai.most_common():
        print(f"   {k}: {v}")
    if apply_rut:
        print(f"   🔴 đã ghi {len(apply_rut)} dòng cảnh báo vào alerts/")
    return 1 if duong else 0


if __name__ == "__main__":
    raise SystemExit(main())
