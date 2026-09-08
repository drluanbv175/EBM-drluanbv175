#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CHỨNG CỨ ĐANG DÙNG CÓ BỊ VƯỢT QUA CHƯA? — dò tổng quan/phân tích gộp/guideline MỚI HƠN.

VÌ SAO CÓ (14/08/2026)
======================
Hệ đang trả lời được "trích dẫn có thật không" (99% định danh đã xác minh) và "hai bản
dashboard có nói ngược nhau không". Nhưng **không có gì trả lời câu quan trọng nhất của
chữ 'mới nhất'**: *một RCT năm 2020 đang được dùng làm căn cứ `apply` — từ đó tới nay đã
có tổng quan hệ thống hay guideline nào bác nó chưa?*

`kiem_do_tuoi_chung_cu.py` chỉ đo TUỔI CỦA GÓI (ngày dựng dashboard), không đo tuổi của
CHỨNG CỨ bên trong. Một gói dựng hôm qua vẫn có thể đang trích một thử nghiệm đã bị một
phân tích gộp 2026 lật lại.

CÁCH DÒ
=======
Với mỗi PMID đang ở `decision='apply'`:
  1. `elink pubmed_pubmed_reviews` — chính PubMed trả về các bài TỔNG QUAN liên quan.
     Dùng công cụ của PubMed thay vì tự dựng truy vấn MeSH: tự dựng thì sai sót nằm ở
     phía mình và không ai kiểm được.
  2. Lọc: chỉ giữ bài **mới hơn** bài đang trích, và có publication type thuộc
     SR / meta-analysis / practice guideline.
  3. Xếp theo năm giảm dần, trả tối đa vài bài cho mỗi mục.

GIỚI HẠN CÓ CHỦ Ý — ĐỌC KỸ
===========================
Đây là tín hiệu **"có thứ đáng đọc"**, KHÔNG phải kết luận "chứng cứ của anh đã sai".
Một tổng quan mới hơn có thể CỦNG CỐ chính kết luận đang dùng. Công cụ **không đọc nội
dung** bài mới và **không phán** chiều của nó — làm vậy là thay phán đoán ngữ nghĩa bằng
suy đoán, đúng lỗi BH28. Nó chỉ nói: *"có N bài tổng quan mới hơn về cùng chủ đề, đây là
tiêu đề và PMID, bác sĩ đọc lấy"*.

Cũng KHÔNG tự đổi `decision`/`gradeLevel` (BH10).

Dùng:
    python tools/kiem_chung_cu_vuot_qua.py                  # mọi mục 'apply'
    python tools/kiem_chung_cu_vuot_qua.py --file F         # một dashboard
    python tools/kiem_chung_cu_vuot_qua.py --gioi-han 40    # chỉ N mục đầu (thử nhanh)
    python tools/kiem_chung_cu_vuot_qua.py --tu-nam 2024    # chỉ tính bài từ năm này

Mã thoát: 0 = không thấy bài mới hơn · 1 = có mục cần bác sĩ đọc lại · 2 = không gọi được mạng.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import time
import urllib.error
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

import importlib.util as _ilu_kcvq  # noqa: E402
_sp_kcvq = _ilu_kcvq.spec_from_file_location("_bst_kcvq", Path(__file__).resolve().parent / "ban_sao_tran.py")
_bst_kcvq = _ilu_kcvq.module_from_spec(_sp_kcvq)
_sp_kcvq.loader.exec_module(_bst_kcvq)
# Publication type được coi là "có thể vượt qua" một nghiên cứu đơn lẻ.
PT_CAO = ("systematic review", "meta-analysis", "practice guideline", "guideline")


def _goi(url: str, cho: int = 25) -> dict | None:
    # Lưới bắt phải gồm CẢ http.client.HTTPException/OSError — SỬA 2026-09-04
    # (Workflow đối kháng đa-agent, phát hiện MEDIUM), cùng lỗi 15/08 đã vá ở
    # sibling `kiem_so_lieu.py::lay_tom_tat()`: một IncompleteRead đơn lẻ nổ
    # TRONG r.read() thoát lưới URLError (IncompleteRead kế thừa từ
    # http.client.HTTPException, không phải URLError) và không try/except nào
    # ở main() bọc quanh vòng lặp `tong_quan_moi_hon()` — nên lỗi mạng ở MỘT
    # PMID sẽ giết TRỌN lượt dò còn lại. Bài lỗi trả None = «chưa hỏi được»,
    # caller (`tong_quan_moi_hon`) đã coi None là "không có gì mới" một cách
    # AN TOÀN (⚪ KHÔNG THẤY, không phải "đã xác nhận không có bài mới hơn").
    import http.client
    req = urllib.request.Request(url, headers={"User-Agent": "EBM-Copilot/1.0"})
    for lan in range(3):
        try:
            with urllib.request.urlopen(req, timeout=cho) as r:
                raw = r.read().decode("utf-8", "replace")
            if raw.lstrip().startswith("<"):
                raise ValueError("NCBI trả HTML (có thể đang chặn)")
            return json.loads(raw)
        except (urllib.error.URLError, ValueError, json.JSONDecodeError,
                http.client.HTTPException, OSError):
            if lan < 2:
                time.sleep(1.5 * (lan + 1))
    return None


def _nam(s: str) -> int | None:
    m = re.search(r"(19|20)\d{2}", s or "")
    return int(m.group(0)) if m else None


def tong_quan_moi_hon(pmid: str, nam_goc: int | None, tu_nam: int | None) -> list[dict]:
    """Bài tổng quan/gộp/guideline MỚI HƠN bài đang trích. [] nếu không có/không hỏi được."""
    j = _goi(f"{EUTILS}elink.fcgi?dbfrom=pubmed&db=pubmed&retmode=json"
             f"&linkname=pubmed_pubmed_reviews&id={pmid}")
    if not j:
        return []
    ids: list[str] = []
    for ls in (j.get("linksets") or []):
        for db in (ls.get("linksetdbs") or []):
            ids += [str(x) for x in (db.get("links") or [])]
    ids = [i for i in dict.fromkeys(ids) if i != str(pmid)][:40]
    if not ids:
        return []
    s = _goi(f"{EUTILS}esummary.fcgi?db=pubmed&retmode=json&id=" + ",".join(ids))
    if not s:
        return []
    ra = []
    for i in ids:
        m = (s.get("result") or {}).get(i)
        if not m:
            continue
        n = _nam(m.get("pubdate", ""))
        if n is None:
            continue
        if nam_goc is not None and n <= nam_goc:
            continue
        if tu_nam is not None and n < tu_nam:
            continue
        pts = " ".join(m.get("pubtype") or []).lower()
        if not any(p in pts for p in PT_CAO):
            continue
        ra.append({"pmid": i, "nam": n, "title": (m.get("title") or "")[:120],
                   "journal": m.get("source", ""), "pubtype": m.get("pubtype") or []})
    ra.sort(key=lambda x: -x["nam"])
    return ra[:4]


def main() -> int:
    ap = argparse.ArgumentParser(description="Dò chứng cứ mới hơn có thể đã vượt qua mục đang dùng")
    ap.add_argument("--file", help="chỉ một dashboard")
    ap.add_argument("--gioi-han", type=int, help="chỉ xử lý N mục đầu")
    ap.add_argument("--tu-nam", type=int, help="chỉ tính bài công bố từ năm này trở đi")
    ap.add_argument("--gom-consider", action="store_true",
                    help="dò CẢ mục decision='consider' (mặc định chỉ 'apply'). Cần khi gói mới thẩm định trên tóm tắt nên chưa mục nào ở 'apply'.")
    a = ap.parse_args()
    _pham_vi = {"apply", "consider"} if a.gom_consider else {"apply"}
    _nhan_pham_vi = "'apply'+'consider'" if a.gom_consider else "'apply'"

    # VÁ 08/09/2026 — trước đây nạp thẳng DASH/"tools"/verify_dashboard.py, ném
    # FileNotFoundError thô khi EBM-Dashboards vắng (mọi checkout git-only). Lùi về
    # bản git-vendor tương đương ở sync/skills/cap-nhat-chung-cu-y-khoa/tools/ trước
    # khi báo ⚪ (xem tools/ban_sao_tran.py::duong_cong_cu_pipeline); một dashboard
    # thật vẫn cần tồn tại nên vòng lặp bên dưới rỗng là kết quả đúng trên máy này.
    duong_vd = _bst_kcvq.duong_cong_cu_pipeline("verify_dashboard.py", REPO)
    if duong_vd is None:
        print("⚪ Không tìm thấy verify_dashboard.py ở EBM-Dashboards/tools/ lẫn bản "
              "git-vendor — không dò được trên máy này.")
        return 0
    spec = importlib.util.spec_from_file_location("vd_vq", duong_vd)
    vd = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vd)

    files = [Path(a.file)] if a.file else sorted(DASH.glob("WebDashboard_*.html"))
    muc: list[tuple[str, str, str, int | None]] = []
    for f in files:
        try:
            blk = vd.extract_data_block(f.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        if not blk:
            continue
        for c in vd.split_items(blk):
            _dec = vd.field(c, "decision")
            if _dec not in _pham_vi:
                continue
            pm = vd.field(c, "pmid")
            if pm:
                muc.append((f.name, vd.field(c, "id"), pm, _nam(vd.field(c, "dateVersion") or "")))
    # Cùng một PMID có thể nằm ở nhiều dashboard — hỏi mạng MỘT lần thôi.
    theo_pmid: dict[str, list[tuple[str, str]]] = {}
    nam_goc: dict[str, int | None] = {}
    for fn, iid, pm, n in muc:
        theo_pmid.setdefault(pm, []).append((fn, iid))
        if nam_goc.get(pm) is None:
            nam_goc[pm] = n
    ds = list(theo_pmid)
    if a.gioi_han:
        ds = ds[:a.gioi_han]

    print(f"Dò {len(ds)} PMID ở decision {_nhan_pham_vi} (trên {len(muc)} lượt dùng)…")
    co = 0
    hong = 0
    ket: list[tuple] = []
    for k, pm in enumerate(ds, 1):
        moi = tong_quan_moi_hon(pm, nam_goc.get(pm), a.tu_nam)
        if moi is None:
            hong += 1
            continue
        if moi:
            co += 1
            ket.append((pm, nam_goc.get(pm), moi, theo_pmid[pm]))
        if k % 25 == 0:
            print(f"  … {k}/{len(ds)}")
        time.sleep(0.34)   # tôn trọng hạn mức 3 lời gọi/giây của NCBI khi không có API key

    print("\n" + "=" * 70)
    # VÁ 18/08/2026 — KHÔNG ĐO ĐƯỢC GÌ THÌ KHÔNG ĐƯỢC IN XANH.
    # Bản cũ: lọc apply-only rồi `if not ket` ⇒ gói KHÔNG có mục 'apply' nào (vd gói mới
    # thẩm định trên TÓM TẮT nên toàn bộ ở 'consider') vẫn nhận 🟢 "không thấy bài mới hơn"
    # — trong khi thực tế nó chưa tra một PMID nào. Đúng họ lỗi BH32: một chỉ số GỘP được
    # trình bày như kết luận về toàn bộ. Nay tách rời "đã đo, không thấy" khỏi "chưa đo".
    if not ds:
        print("  ⚪ CHƯA ĐO ĐƯỢC GÌ — không có mục nào khớp phạm vi %s." % _nhan_pham_vi)
        print("     Đây KHÔNG phải kết luận 'chứng cứ còn mới'. Gói mà mọi mục còn ở")
        print("     'consider' (vd mới thẩm định trên tóm tắt) sẽ luôn rơi vào đây.")
        print("     Chạy lại với --gom-consider để thật sự dò. Cần bác sĩ kiểm chứng.")
        return 0
    if not ket:
        print("  🟢 Đã dò %d PMID, không thấy tổng quan/gộp/guideline nào MỚI HƠN." % len(ds))
        print("     (Không chứng minh chứng cứ còn đúng — chỉ nghĩa là PubMed không trả bài")
        print("      tổng quan mới hơn nào liên quan. Cần bác sĩ kiểm chứng.)")
        return 0
    print(f"  🟠 {len(ket)}/{len(ds)} mục có chứng cứ TỔNG HỢP MỚI HƠN — nên đọc lại")
    print("=" * 70)
    print("  Bài mới hơn có thể CỦNG CỐ hoặc BÁC kết luận đang dùng. Máy KHÔNG đọc nội dung")
    print("  và KHÔNG phán chiều — đây chỉ là danh sách đáng đọc.\n")
    for pm, ng, moi, dung in ket:
        noi = ", ".join(f"{f.replace('WebDashboard_EBM_VanDeCuThe_', '')[:30]}:{i}"
                        for f, i in dung[:3])
        print(f"  ▸ PMID {pm} ({ng or '?'}) — đang dùng ở {noi}")
        for m in moi:
            print(f"      {m['nam']}  PMID {m['pmid']}  {m['journal'][:26]:28} {m['title'][:70]}")
        print()
    print("  Công cụ KHÔNG tự đổi decision/gradeLevel. Cần bác sĩ kiểm chứng.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
