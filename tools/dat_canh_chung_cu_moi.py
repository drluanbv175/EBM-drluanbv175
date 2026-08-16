#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ĐẶT CẠNH — kết luận ĐANG DÙNG vs kết luận NGUỒN TỔNG HỢP MỚI HƠN (16/08/2026).

VÌ SAO CÓ
=========
`kiem_chung_cu_vuot_qua.py` (14/08) đo được: 125/172 mục `apply` có tổng quan/
guideline MỚI HƠN — nhưng sản phẩm dừng ở DANH SÁCH PMID. Không bác sĩ nào đọc
nổi 125 dòng tiêu đề để biết mục nào đáng mở trước. Tool này đi thêm đúng MỘT
bậc mà không vượt thẩm quyền: chọn các mục nặng ký nhất, lấy NGUYÊN VĂN phần
kết luận trong abstract của nguồn mới, rồi ĐẶT CẠNH kết luận đang dùng.

BA LUẬT — kế thừa trực tiếp BH28/BH10 và luật rút bài:
  1. KHÔNG PHÁN CHIỀU: không nói «củng cố» hay «lật lại» — chỉ đặt hai kết luận
     cạnh nhau, nguyên văn, kèm định danh. Phán đoán ngữ nghĩa là của bác sĩ.
  2. KHÔNG GHI vào dashboard (`decision`/`gradeLevel` nguyên vẹn — BH10).
  3. PMID mới TRA rút bài bằng công cụ (chuỗi 3 tầng qua
     check_citation_retraction.py); không tra được ⇒ ghi «chưa kiểm rút bài»,
     TUYỆT ĐỐI không ghi «chưa bị rút».

Dùng:
    python3 tools/dat_canh_chung_cu_moi.py                # top 12 mục nặng nhất
    python3 tools/dat_canh_chung_cu_moi.py --top 20
    python3 tools/dat_canh_chung_cu_moi.py --gioi-han 40  # chỉ quét N mục đầu (thử nhanh)

Ra: EBM-Dashboards/derivatives/DAT-CANH-CHUNG-CU-MOI_<ngày>.md
Mã thoát: 0 = xong (kể cả 0 mục) · 2 = không gọi được mạng. Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", line_buffering=True)
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
DASH = REPO / "EBM-Dashboards"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


def _nap(ten: str, duong: Path):
    spec = importlib.util.spec_from_file_location(ten, duong)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[ten] = mod
    spec.loader.exec_module(mod)
    return mod


def _diem_bai_moi(b: dict) -> int:
    """Xếp ưu tiên đọc: guideline > SR/MA; càng mới càng cao. KHÔNG phải chất lượng."""
    pts = " ".join(b.get("pubtype") or []).lower()
    d = 0
    if "guideline" in pts:
        d += 3
    if "meta-analysis" in pts or "systematic review" in pts:
        d += 1
    d += max(0, b.get("nam", 0) - 2024)
    return d


def _ket_luan_tu_abstract(xml: str, pmid: str) -> str:
    """Nguyên văn phần kết luận trong abstract của MỘT bài (efetch XML đã tải).

    Abstract có cấu trúc: lấy AbstractText nhãn CONCLUSION(S)/INTERPRETATION.
    Không cấu trúc: lấy 2 câu cuối. Không có abstract ⇒ nói thẳng.
    """
    m = re.search(rf"<PubmedArticle>(?:(?!</PubmedArticle>).)*?<PMID[^>]*>{pmid}</PMID>"
                  r"((?:(?!</PubmedArticle>).)*)</PubmedArticle>", xml, re.S)
    khoi = m.group(1) if m else ""
    if not khoi:
        return "«tóm tắt không tải được»"
    phan = re.findall(r'<AbstractText\b([^>]*)>((?:(?!</AbstractText>).)*)</AbstractText>',
                      khoi, re.S)
    if not phan:
        return "«bài không có abstract trên PubMed»"

    def sach(t: str) -> str:
        t = re.sub(r"<[^>]+>", "", t)
        return re.sub(r"\s+", " ", t).strip()

    for thuoc_tinh, noi_dung in phan:
        nhan = (re.search(r'Label="([^"]*)"', thuoc_tinh) or [None, ""])[1].upper()
        if any(k in nhan for k in ("CONCLUSION", "INTERPRETATION")):
            return sach(noi_dung)
    # không nhãn kết luận → 2 câu cuối của toàn abstract, NÓI RÕ đó không phải mục kết luận
    toan = " ".join(sach(nd) for _, nd in phan)
    cau = re.split(r"(?<=[.!?])\s+", toan)
    duoi = " ".join(cau[-2:]) if len(cau) >= 2 else toan
    return f"(abstract không có mục kết luận — trích 2 câu cuối) {duoi}"


def _tra_rut_bai(pmids: list[str]) -> dict[str, str]:
    """Phán quyết rút bài qua CLI chuỗi 3 tầng (--json). Không chạy được ⇒ «chưa kiểm»."""
    nhan = {p: "⚠️ chưa kiểm rút bài" for p in pmids}
    if not pmids:
        return nhan
    cli = REPO / "medical-ebm-automation" / "tools" / "check_citation_retraction.py"
    venv_py = Path.home() / ".ebm-venv" / "bin" / "python"
    py = str(venv_py) if venv_py.exists() else sys.executable
    if not cli.exists():
        return nhan
    try:
        r = subprocess.run([py, str(cli), "--pmids", ",".join(pmids), "--json"],
                           capture_output=True, text=True, timeout=240,
                           cwd=cli.parent.parent)
        du_lieu = json.loads(r.stdout or "{}")
        for p, kq in du_lieu.items():
            st = (kq or {}).get("status", "")
            if st in ("retracted", "retract_and_replace", "expression_of_concern"):
                nhan[p] = (f"🔴 {kq.get('nature') or st} — notice PMID "
                           f"{kq.get('notice_pmid', '?')}; ĐỌC PHÁN QUYẾT trước khi dùng")
            elif st == "ok":
                nhan[p] = f"✓ không phát hiện rút bài (tra {dt.date.today().isoformat()})"
            # mọi status khác giữ «chưa kiểm» — KHÔNG BIẾT không được thành ok
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
        pass
    return nhan


def _title_goc(pmids: list[str]) -> dict[str, str]:
    """Title tiếng Anh của các bài GỐC — đặt cạnh title bài mới để bác sĩ loại
    nhanh mục lạc chủ đề (đã ĐO: cosine title không phân tách được lạc/đúng —
    cặp lạc «Screening…USPSTF» đạt 0.550 > cặp đúng 0.468 vì trùng khung câu,
    nên KHÔNG lọc máy; làm cho sự lạc NHÌN THẤY ĐƯỢC thay vì lọc sai)."""
    ra: dict[str, str] = {}
    if not pmids:
        return ra
    try:
        with urllib.request.urlopen(
                f"{EUTILS}esummary.fcgi?db=pubmed&retmode=json&id=" + ",".join(pmids),
                timeout=40) as r:
            s = json.load(r).get("result", {})
        for p in pmids:
            ra[p] = (s.get(p) or {}).get("title", "")
    except (OSError, json.JSONDecodeError):
        pass
    return ra


def main() -> int:
    ap = argparse.ArgumentParser(description="Đặt cạnh kết luận đang dùng vs nguồn mới hơn")
    ap.add_argument("--top", type=int, default=12, help="số mục nặng ký đưa vào báo cáo")
    ap.add_argument("--gioi-han", type=int, default=0, help="chỉ quét N mục apply đầu (thử nhanh)")
    a = ap.parse_args()

    vd = _nap("_vd_dc", DASH / "tools" / "verify_dashboard.py")
    kcv = _nap("_kcv_dc", REPO / "tools" / "kiem_chung_cu_vuot_qua.py")

    # ① gom mục apply có PMID (mỗi PMID một lần, nhớ mọi nơi nó xuất hiện)
    muc: dict[str, dict] = {}
    for f in sorted(DASH.glob("WebDashboard_*.html")):
        try:
            blk = vd.extract_data_block(f.read_text(encoding="utf-8", errors="replace"))
        except Exception:  # noqa: BLE001 — dashboard hỏng khối DATA thì bỏ qua, không chết cả lượt
            continue
        for c in vd.split_items(blk):
            if vd.field(c, "decision") != "apply":
                continue
            pm = (vd.field(c, "pmid") or "").strip()
            if not pm.isdigit():
                continue
            m = muc.setdefault(pm, {"title": vd.field(c, "title") or "(không tiêu đề)",
                                    "noi": [], "nam": None})
            m["noi"].append(f"{f.name} · {vd.field(c, 'id')}")
            n = re.search(r"(20\d\d)", vd.field(c, "dateVersion") or "")
            if n and m["nam"] is None:
                m["nam"] = int(n.group(1))

    ds = list(muc.items())
    if a.gioi_han:
        ds = ds[: a.gioi_han]
    print(f"Quét {len(ds)} PMID đang 'apply'…")

    # ② hỏi PubMed từng mục (tái dùng tool 14/08 — không tự dựng truy vấn)
    ung_vien = []
    for i, (pm, m) in enumerate(ds, 1):
        moi = kcv.tong_quan_moi_hon(pm, m["nam"], None)
        if moi:
            tot = max(moi, key=_diem_bai_moi)
            ung_vien.append((_diem_bai_moi(tot), pm, m, tot))
        if i % 25 == 0:
            print(f"  …{i}/{len(ds)}")
        time.sleep(0.35)  # nhịp E-utilities không key
    if not ung_vien and len(ds):
        print("Không hỏi được PubMed cho mục nào — kiểm mạng rồi chạy lại.")
        return 2

    ung_vien.sort(key=lambda x: -x[0])
    chon = ung_vien[: a.top]
    print(f"{len(ung_vien)} mục có nguồn tổng hợp mới hơn → đặt cạnh top {len(chon)}.")

    # ③ abstract nguồn mới (một lượt efetch) + tra rút bài + title EN bài gốc
    pmids_moi = [t["pmid"] for _, _, _, t in chon]
    title_goc = _title_goc([pm for _, pm, _, _ in chon])
    xml = ""
    if pmids_moi:
        url = (f"{EUTILS}efetch.fcgi?db=pubmed&retmode=xml&id="
               + urllib.parse.quote(",".join(pmids_moi)))
        try:
            with urllib.request.urlopen(url, timeout=40) as r:
                xml = r.read().decode("utf-8", "replace")
        except OSError:
            print("⚠️ không tải được abstract — báo cáo sẽ ghi «tóm tắt không tải được».")
    rut = _tra_rut_bai(pmids_moi)

    # ④ báo cáo đặt-cạnh
    hom_nay = dt.date.today().isoformat()
    ra = DASH / "derivatives" / f"DAT-CANH-CHUNG-CU-MOI_{hom_nay}.md"
    dong = [
        f"# ĐẶT CẠNH — chứng cứ đang `apply` vs nguồn tổng hợp mới hơn ({hom_nay})",
        "",
        f"> Quét {len(ds)} PMID đang `apply` · {len(ung_vien)} mục có tổng quan/guideline",
        f"> mới hơn · trình {len(chon)} mục nặng ký nhất (guideline > SR/MA, ưu tiên năm mới).",
        "> **Tool KHÔNG phán chiều** — nguồn mới có thể CỦNG CỐ hoặc LẬT kết luận đang",
        "> dùng; hai cột chỉ được đặt cạnh nhau, nguyên văn, để bác sĩ tự so. Không đổi",
        "> `decision`/`gradeLevel`.",
        "> ⚠️ Danh sách «liên quan» do chính PubMed trả (`pubmed_pubmed_reviews`) và",
        "> **có thể lạc chủ đề** (đã đo: không lọc máy được — cặp lạc còn giống khung",
        "> câu hơn cặp đúng). Title bài gốc in kèm để bác sĩ loại mục lạc trong vài",
        "> giây. Cần bác sĩ kiểm chứng.",
        "",
    ]
    for stt, (_, pm, m, tot) in enumerate(chon, 1):
        pts = ", ".join(tot.get("pubtype") or [])
        tg = title_goc.get(pm, "")
        dong += [
            f"## {stt}. {m['title']}",
            f"- **Đang dùng:** PMID {pm}" + (f" (năm ghi trên gói: {m['nam']})" if m["nam"] else "")
            + (f" — *{tg[:110]}*" if tg else ""),
            f"  - nơi dùng: {'; '.join(m['noi'][:3])}" + (" …" if len(m["noi"]) > 3 else ""),
            f"- **Nguồn tổng hợp mới hơn:** {tot['title']} — *{tot['journal']}*, "
            f"{tot['nam']} · PMID {tot['pmid']} · [{pts}] · {rut.get(tot['pmid'], '⚠️ chưa kiểm rút bài')}",
            f"  - **Kết luận nguyên văn (abstract):** {_ket_luan_tu_abstract(xml, tot['pmid'])}",
            "",
        ]
    if len(ung_vien) > len(chon):
        dong += [f"_Còn {len(ung_vien) - len(chon)} mục khác có nguồn mới hơn — chạy lại với "
                 f"`--top {len(ung_vien)}` để xem đủ, hoặc đọc báo cáo kiem_chung_cu_vuot_qua._", ""]
    dong += ["---", "Sinh bởi `tools/dat_canh_chung_cu_moi.py` — đặt cạnh, không phán chiều "
             "(BH28), không ghi vào dashboard (BH10). Cần bác sĩ kiểm chứng."]
    ra.parent.mkdir(parents=True, exist_ok=True)
    ra.write_text("\n".join(dong), encoding="utf-8", newline="\n")
    print(f"→ {ra}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
