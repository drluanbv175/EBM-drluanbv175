#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TRA CỨU TẠI ĐIỂM KHÁM — Clinical Quick View (PHA 5 LÔ 2, 15/08/2026).

Khác hẳn dashboard đọc-lúc-rảnh: giữa hai bệnh nhân chỉ có vài giây. Luật cứng:

  • CHỈ thẻ ĐÃ DUYỆT (N4): decision do bác sĩ chốt trong dashboard đã xác minh
    (`from_doctor_master`/`from_dashboard_master`). Ứng viên CANDIDATE (hàng quét
    tuần, `from_engine`) TUYỆT ĐỐI không hiện lúc đang khám.
  • KHÔNG có thẻ ⇒ nói thẳng «CHƯA ĐƯỢC GIÁM SÁT» + chỉ nguồn tra tay. CẤM sinh
    câu trả lời từ trí nhớ mô hình (mục 10) — câu hỏi được GHI LẠI làm tín hiệu
    bổ sung watchlist (LÔ 5, `state/cau-hoi-chua-giam-sat.jsonl`).
  • Thẻ có bản tổng hợp MỚI HƠN chưa rà (danh sách quét quý) → hiện kèm cờ 🟠
    «có bản mới hơn chưa rà» — đọc xong phải biết mình đang đứng trên nền nào.
  • Ngoại tuyến 100%% — mất mạng phòng khám không làm mất tra cứu.

Dùng:  python3 tools/tra_diem_kham.py "copd đợt cấp bộ ba"
       python3 tools/tra_diem_kham.py --demo   # 5 câu mô phỏng + đo tốc độ
"""
from __future__ import annotations

import json
import re
import sys
import time
import unicodedata
from datetime import date
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

GOC = Path(__file__).resolve().parents[1]
LEDGER = GOC / "EBM_MASTER" / "EBM_MASTER.json"
NGUON_DUYET = {"from_doctor_master", "from_dashboard_master"}


def _bo_dau(s: str) -> str:
    s = unicodedata.normalize("NFD", s or "")
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower()


def _vuot_qua_pmids() -> set[str]:
    fs = sorted((GOC / "EBM-Dashboards" / "derivatives").glob("CHUNG-CU-VUOT-QUA_*.txt"))
    if not fs:
        return set()
    return set(re.findall(r"PMID (\d+)", fs[-1].read_text(encoding="utf-8",
                                                          errors="replace")))


def tra(cau_hoi: str, cards: list[dict], vq: set[str]) -> list[dict]:
    # Token ĐẶC HIỆU = bỏ từ lâm sàng chung (đơn âm tiếng Việt mồi nhiễu rất mạnh
    # — đo thật 15/08: «sốt xuất huyết dengue…» match nhầm thẻ WHO thuốc giả chỉ vì
    # «cảnh»+«báo», rồi thẻ truyền máu vì «xuất»+«huyết» trong mô tả). Tại điểm
    # khám, thẻ SAI CHỦ ĐỀ nguy hiểm hơn câu trả lời «chưa giám sát».
    TU_CHUNG = {"ngoai", "tru", "dau", "hieu", "canh", "bao", "benh", "nhan",
                "dieu", "tri", "nguoi", "cao", "tuoi", "thuoc", "trong", "truoc",
                "sau", "khong", "nen", "moi", "dung", "nhieu", "lan"}
    tat_ca = [t for t in _bo_dau(cau_hoi).split() if len(t) >= 3]
    dac_hieu = [t for t in tat_ca if t not in TU_CHUNG]
    if not dac_hieu:
        return []
    # LUẬT NGOÀI PHẠM VI: câu hỏi mang từ đặc hiệu ≥4 ký tự KHÔNG xuất hiện ở
    # BẤT KỲ thẻ nào toàn kho (vd «dengue») ⇒ chủ đề chưa được giám sát — trả
    # rỗng để in «chưa giám sát», thay vì gán ghép thẻ trùng vài từ ghép
    # («xuất huyết» của dengue ≠ «xuất huyết tiêu hoá»).
    kho = getattr(tra, "_kho", None)
    if kho is None:
        kho = _bo_dau(json.dumps([{k: c.get(k) for k in
                                   ("topic", "specialty", "pico_question",
                                    "recommendation")} for c in cards],
                                  ensure_ascii=False))
        tra._kho = kho
    la_ten_rieng = [t for t in dac_hieu if len(t) >= 4 and t not in kho]
    if la_ten_rieng:
        return []
    diem: list[tuple[int, dict]] = []
    for c in cards:
        chu_de = _bo_dau(f"{c.get('topic', '')} {c.get('specialty', '')} "
                         f"{c.get('pico_question', '')}")
        khop_dh = sum(1 for t in dac_hieu if t in chu_de)
        # Chủ đề phải cõng ít nhất NỬA số token đặc hiệu (tối thiểu 1).
        if khop_dh < max(1, len(dac_hieu) // 2):
            continue
        vb = _bo_dau(json.dumps({k: c.get(k) for k in
                                 ("recommendation", "source")}, ensure_ascii=False))
        d = khop_dh * 3 + sum(1 for t in tat_ca if t in vb)
        diem.append((d, c))
    return [c for _d, c in sorted(diem, key=lambda x: -x[0])[:3]]


def in_quick_view(cau_hoi: str, ket: list[dict], vq: set[str], giay: float) -> None:
    print(f"\n❓ {cau_hoi}   ({giay*1000:.0f} ms)")
    if not ket:
        print("  ⛔ CHỦ ĐỀ NÀY CHƯA ĐƯỢC GIÁM SÁT — hệ KHÔNG sinh câu trả lời thay thế.")
        print("     Tra tay: PubMed/guideline hội chuyên khoa · phác đồ BYT (kcb.vn).")
        st = GOC / "state" / "cau-hoi-chua-giam-sat.jsonl"
        st.parent.mkdir(exist_ok=True)
        with st.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"cau_hoi": cau_hoi, "luc": date.today().isoformat()},
                               ensure_ascii=False) + "\n")
        print("     → đã ghi câu hỏi làm ứng viên BỔ SUNG WATCHLIST (vòng phản hồi LÔ 5).")
        return
    for c in ket:
        src = c.get("source") or {}
        pm = src.get("pmid") or ""
        co = " 🟠 CÓ BẢN TỔNG HỢP MỚI HƠN CHƯA RÀ (quét quý)" if pm in vq else ""
        rec = re.sub(r"\s+", " ", str(c.get("recommendation") or ""))[:220]
        print(f"  ▶ [{c.get('decision','?').upper()}] {rec}{co}")
        print(f"    Nguồn: {src.get('agency') or src.get('title','')[:40]} · "
              f"PMID {pm or '—'} / DOI {src.get('doi') or '—'} · "
              f"thẻ cập nhật {c.get('date_added','?')[:10]} · mức {c.get('gradeLevel')}")
        goi = GOC / "implementation" / f"{c.get('id')}.md"
        if goi.exists():
            print(f"    📋 Gói triển khai: implementation/{c.get('id')}.md (cờ đỏ · nhóm đặc biệt · tái khám)")
    print("    ⚠️ Cờ đỏ/nhóm đặc biệt: xem gói triển khai hoặc dashboard chủ đề. "
          "Cần bác sĩ kiểm chứng — quyết định cuối thuộc bác sĩ điều trị.")


def main() -> int:
    t0 = time.perf_counter()
    d = json.loads(LEDGER.read_text(encoding="utf-8"))
    cards = [c for c in d["evidence_cards"]
             if c.get("provenance") in NGUON_DUYET
             and str(c.get("verification_status", "")).startswith("đã xác minh")]
    vq = _vuot_qua_pmids()
    t_nap = time.perf_counter() - t0

    if "--demo" in sys.argv:
        cau = ["COPD đợt cấp nhiều lần có nên bộ ba ICS LABA LAMA",
               "viêm khớp dạng thấp JAK inhibitor người cao tuổi nguy cơ tim mạch",
               "sàng lọc lao tiềm ẩn trước thuốc sinh học",
               "người cao tuổi đa thuốc benzodiazepine Beers",
               "sốt xuất huyết dengue ngoại trú dấu hiệu cảnh báo"]
        print(f"NẠP {len(cards)} thẻ đã duyệt trong {t_nap*1000:.0f} ms (ngoại tuyến)")
        for q in cau:
            t1 = time.perf_counter()
            ket = tra(q, cards, vq)
            in_quick_view(q, ket, vq, time.perf_counter() - t1)
        return 0
    q = " ".join(a for a in sys.argv[1:] if not a.startswith("-"))
    if not q:
        print("Cách dùng: tra_diem_kham.py \"<câu hỏi>\" | --demo")
        return 2
    t1 = time.perf_counter()
    in_quick_view(q, tra(q, cards, vq), vq, time.perf_counter() - t1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
