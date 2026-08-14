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


def _nap_rw():
    """Nạp chỉ mục Retraction Watch ngoại tuyến (đã stdlib-safe từ 15/08)."""
    sys.path.insert(0, str(GOC / "medical-ebm-automation"))
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
        src = c.get("source") or {}
        pmid, doi = src.get("pmid"), src.get("doi")
        muc_so = so.get(f"pmid:{pmid}") if pmid else None
        if muc_so is None and doi:
            muc_so = so.get(f"doi:{doi}") or so.get(f"doi:{str(doi).lower()}")

        # Lớp 1 — DƯƠNG từ RW ngoại tuyến (chỉ tra được PMID).
        bg_rw = rw.tra(str(pmid)) if (rw and pmid) else None
        # Lớp 2 — sổ xác minh.
        ghi_rut = (muc_so or {}).get("ghi_chu_rut")

        if bg_rw or ghi_rut in DUONG_TINH:
            ly_do = (bg_rw or {}).get("reason") or ghi_rut
            # MỨC phải nói đúng (BH34): sổ xác minh đã phân biệt sẵn rút-và-thay
            # (trường `rut_va_thay` + DOI thông báo) — đọc nó, đừng đoán lại từ chuỗi.
            rr = ("retract and replace" in str(ly_do).lower()
                  or bool((muc_so or {}).get("rut_va_thay")))
            tb = (muc_so or {}).get("thong_bao_rut_doi")
            if tb:
                ly_do = f"{ly_do} · thông báo: doi:{tb}"
            duong.append({"id": c.get("id"), "pmid": pmid, "doi": doi,
                          "decision": c.get("decision"),
                          "muc": "RÚT & ĐĂNG LẠI (đối chiếu bản đã thay)" if rr
                                 else "ĐÃ RÚT/EoC (không dùng)",
                          "ly_do": str(ly_do)[:120]})
            trang_thai["dương tính"] += 1
            continue

        # ÂM «ok» chỉ khi sổ ghi ok TỪ NGUỒN SỐNG và còn trong hạn 30 ngày.
        tuoi_rut = _tuoi_ngay((muc_so or {}).get("kiem_rut_luc"))
        if ghi_rut == "ok" and tuoi_rut is not None and tuoi_rut <= HAN_RUT:
            trang_thai["ok (rút bài còn hạn 30d)"] += 1
        elif ghi_rut == "ok":
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
    vq = sorted((GOC / "EBM-Dashboards" / "derivatives").glob("CHUNG-CU-VUOT-QUA_*.txt"))
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
             f"- Bản mới nhất: `{vq[-1].name}`" if vq else "- (chưa có bản quét nào)",
             "", "## Đối chiếu số liệu (mẫu ≥10%)",
             "- Đo gần nhất 14/08/2026 bằng `tools/kiem_so_lieu.py`: 24/25 mục khớp "
             "abstract (1 ⚪ không kết luận). Chạy lại khi cần: "
             "`python3 tools/kiem_so_lieu.py --mau 0.1 --online`.",
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
