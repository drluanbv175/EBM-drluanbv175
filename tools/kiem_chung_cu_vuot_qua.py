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
            data = json.loads(raw)
            # Vá 22/09/2026 (phản biện vòng 2, review:cong-rut-bai #1): NCBI đôi khi trả HTTP 200
            # kèm JSON HỢP LỆ nhưng là bản LỖI (vd {"error":"API rate limit exceeded", ...}) —
            # trước đây đọc thành THÀNH CÔNG (không có exception ⇒ không retry) nên một lần
            # rate-limit thoáng qua (~326 lời gọi/lượt dò, 0,34s/2 lời gọi mỗi PMID) làm hong+=1
            # ngay lập tức, không có cơ hội thử lại như mọi lỗi mạng khác.
            if isinstance(data, dict) and data.get("error"):
                raise ValueError(f"NCBI trả bản lỗi: {str(data.get('error'))[:80]}")
            return data
        except (urllib.error.URLError, ValueError, json.JSONDecodeError,
                http.client.HTTPException, OSError):
            if lan < 2:
                time.sleep(1.5 * (lan + 1))
    return None


def _nam(s: str) -> int | None:
    m = re.search(r"(19|20)\d{2}", s or "")
    return int(m.group(0)) if m else None


def tong_quan_moi_hon(pmid: str, nam_goc: int | None, tu_nam: int | None) -> list[dict] | None:
    """Bài tổng quan/gộp/guideline MỚI HƠN bài đang trích.

    Trả `[]` khi ĐÃ HỎI ĐƯỢC PubMed mà không có bài nào; trả `None` khi KHÔNG HỎI ĐƯỢC
    (mạng lỗi, NCBI trả trang chặn). VÁ 14/09/2026: bản cũ trả `[]` cho CẢ HAI, nên `main()`
    có sẵn nhánh `if moi is None: hong += 1` mà nhánh đó không bao giờ chạy tới — và khi
    NCBI chặn IP, mọi PMID đều "không có bài mới" ⇒ in 🟢. Đúng họ BH27: không kiểm được
    bị trình bày thành đã kiểm và sạch. `dat_canh_chung_cu_moi.py` dùng `if moi:` nên
    `None` không làm gãy nơi tiêu thụ đó.
    """
    j = _goi(f"{EUTILS}elink.fcgi?dbfrom=pubmed&db=pubmed&retmode=json"
             f"&linkname=pubmed_pubmed_reviews&id={pmid}")
    # VÁ 21/09/2026: một phản hồi JSON HỢP LỆ nhưng là bản LỖI (có khoá 'error', hoặc thiếu 'linksets') từng bị
    # đọc thành «không có bài nào» — báo cáo 16/09 in 🟢 «đã dò 163 PMID, không thấy bài mới hơn» (476 byte, 0 dòng PMID)
    # trong khi thực chất không hỏi được gì, rồi `tra_diem_kham` lấy đúng tệp đó làm căn cứ và TẮT mọi cờ 🟠.
    if j is None or j.get("error") or "linksets" not in j:
        return None
    ids: list[str] = []
    for ls in (j.get("linksets") or []):
        for db in (ls.get("linksetdbs") or []):
            ids += [str(x) for x in (db.get("links") or [])]
    ids = [i for i in dict.fromkeys(ids) if i != str(pmid)][:40]
    if not ids:
        return []
    s = _goi(f"{EUTILS}esummary.fcgi?db=pubmed&retmode=json&id=" + ",".join(ids))
    if s is None or s.get("error") or "result" not in s:
        return None
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


def _kiem_manifest_hop_le(man: dict) -> str:
    """'' nếu manifest ĐỦ điều kiện để kết luận «không có cờ» cho PMID không nằm trong danh sách dương tính; ngược lại lý do.

    Phản biện độc lập 21/09 tái hiện được các manifest THIẾU/THU HẸP vẫn bị nhận là hợp lệ: CO_BAI_MOI với 100/163 PMID hỏng;
    `--tu-nam` bỏ qua mọi tổng quan cũ mà vẫn «toàn kho»; CO_BAI_MOI với danh sách dương tính rỗng. Quy tắc: tập PMID ĐÃ DÒ
    phải được liệt kê (để biết PMID nào CHƯA dò), mọi PMID dò được hết (0 hỏng), phạm vi toàn kho và không thu hẹp theo năm."""
    if man.get("ket_luan") not in ("SACH", "CO_BAI_MOI"):
        return f"kết luận {man.get('ket_luan')!r} — không phải «đã dò xong»"
    pv = man.get("pham_vi") or {}
    if not pv.get("toan_kho"):
        return "chỉ là lượt dò MẪU/MỘT FILE"
    if pv.get("tu_nam"):
        return f"đã thu hẹp theo --tu-nam {pv.get('tu_nam')} (bỏ qua mọi tổng quan cũ hơn)"
    if man.get("so_pmid_hong"):
        return f"{man.get('so_pmid_hong')} PMID KHÔNG hỏi được — phần đó chưa dò"
    da_do = man.get("pmid_da_do")
    if not isinstance(da_do, list) or not da_do or len(da_do) != man.get("so_pmid_do"):
        return "manifest không liệt kê tập PMID đã dò (bản cũ) — không biết PMID nào CHƯA dò"
    if man.get("so_pmid_tong") != man.get("so_pmid_do"):
        return f"chỉ dò {man.get('so_pmid_do')}/{man.get('so_pmid_tong')} PMID khác nhau của phạm vi"
    co = man.get("pmid_co_bai_moi") or []
    if man.get("ket_luan") == "CO_BAI_MOI" and (not co or not set(map(str, co)) <= set(map(str, da_do))):
        return "danh sách PMID có bài mới hơn rỗng hoặc nằm ngoài tập đã dò"
    if man.get("ket_luan") == "SACH" and co:
        return "kết luận SACH nhưng vẫn có PMID dương tính — manifest tự mâu thuẫn"
    return ""


def doc_bao_cao_vuot_qua(thu_muc: Path | None = None) -> dict:
    """Báo cáo «bị vượt qua» mới nhất và tập PMID đang có bài tổng hợp mới hơn.

    Trả `{"hop_le": bool, "pmids": set, "da_do": set, "nguon", "ngay", "ly_do", "cu": bool}`.
    NGUỒN SỰ THẬT DUY NHẤT cho mọi bên tiêu thụ (`tra_diem_kham`, `provenance_ledger`, …).

    CHỈ tin MANIFEST (`CHUNG-CU-VUOT-QUA_<ngày>.json`) — tệp `.txt` không manifest không cho biết phạm vi nên KHÔNG dùng để kết
    luận (phản biện 21/09: một lượt dò mẫu cũng có dòng «▸ PMID»). Xét bản MỚI NHẤT (theo ngày trong tên): hợp lệ ⇒ `hop_le=True`
    và `da_do` là tập PMID thật sự đã dò; KHÔNG hợp lệ ⇒ `hop_le=False` kèm lý do, và KHÔNG âm thầm lùi về bản cũ hơn để nói «hợp
    lệ» — bản cũ hợp lệ gần nhất chỉ cung cấp danh sách DƯƠNG TÍNH (`pmids`, `cu=True`) chứ không cho phép kết luận «không có cờ»
    (dương tính cũ vẫn đúng; âm tính cũ đã hết hạn). Không có manifest nào ⇒ `hop_le=False`."""
    thu_muc = thu_muc or (DASH / "derivatives")
    ket = {"hop_le": False, "pmids": set(), "da_do": set(), "nguon": None, "ngay": None, "cu": False,
           "ly_do": "không có manifest báo cáo quét quý nào (báo cáo chỉ có tệp .txt không kiểm chứng được phạm vi)"}
    try:
        man_files = sorted(thu_muc.glob("CHUNG-CU-VUOT-QUA_*.json"), reverse=True)
        stem_txt = {f.stem for f in thu_muc.glob("CHUNG-CU-VUOT-QUA_*.txt")}
    except OSError:
        return ket
    # Báo cáo .txt MỚI HƠN mọi manifest = lượt mới nhất chết giữa chừng (không ghi được manifest): không được lùi âm thầm về
    # manifest cũ rồi nói «hợp lệ» (phản biện 22/09 tái hiện).
    stem_man = {f.stem for f in man_files}
    if stem_txt and (not stem_man or max(stem_txt) > max(stem_man)):
        ket["ly_do"] = f"báo cáo mới nhất {max(stem_txt)}.txt KHÔNG có manifest (lượt dò dở dang/hỏng)"
        ket["_lui_ve_cu"] = True
    moi_nhat = not ket.get("_lui_ve_cu")
    # Vá 22/09/2026 (phản biện vòng 2, review:cong-rut-bai #1) — NGUYÊN TẮC BẤT ĐỐI XỨNG áp cho cả
    # hàm này, không chỉ cho chuỗi rút bài 3 tầng: `hop_le` (điều kiện NGHIÊM để kết luận «không có
    # cờ» cho PMID ngoài danh sách) chỉ cần cho ÂM TÍNH. DƯƠNG TÍNH (ket_luan=CO_BAI_MOI, danh sách
    # PMID nằm trong tập chính manifest đó tự khai đã dò) không cần hop_le để được NHẬN — một manifest
    # bị đánh «không hợp lệ» chỉ vì MỘT PMID KHÁC hỏng thoáng qua (rate limit) vẫn phải giữ được các
    # PMID nó đã dò thành công và tìm ra dương tính thật. Trước đây cổng tất-cả-hoặc-không vứt sạch cả
    # 117+ cờ 🟠 chỉ vì 1 PMID hỏng trong ~326 lời gọi.
    duong_tinh_tu_manifest_khong_hop_le: set[str] = set()
    for f in man_files:
        man = None
        try:
            man = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            ly = "manifest không đọc được/không phải JSON"
        else:
            ly = _kiem_manifest_hop_le(man) if isinstance(man, dict) else "manifest không phải đối tượng JSON"
        ngay = f.stem.rsplit("_", 1)[-1]
        if not ly:
            pmids_ban_nay = {str(x) for x in man.get("pmid_co_bai_moi") or []} | duong_tinh_tu_manifest_khong_hop_le
            if moi_nhat:
                return {"hop_le": True, "pmids": pmids_ban_nay,
                        "da_do": {str(x) for x in man["pmid_da_do"]}, "nguon": f.name, "ngay": ngay, "cu": False, "ly_do": ""}
            ket.update({"pmids": pmids_ban_nay, "nguon": f.name, "ngay": ngay, "cu": True})
            ket.pop("_lui_ve_cu", None)
            return ket
        if moi_nhat:
            ket["ly_do"] = f"báo cáo mới nhất {f.name} KHÔNG hợp lệ: {ly}"
            moi_nhat = False
        if isinstance(man, dict) and man.get("ket_luan") == "CO_BAI_MOI":
            da_do_lo = {str(x) for x in (man.get("pmid_da_do") or [])}
            co = {str(x) for x in (man.get("pmid_co_bai_moi") or [])}
            if da_do_lo:  # chỉ nhận dương tính nằm trong tập CHÍNH manifest này tự khai đã dò
                co &= da_do_lo
            duong_tinh_tu_manifest_khong_hop_le |= co
    ket["pmids"] |= duong_tinh_tu_manifest_khong_hop_le
    ket.pop("_lui_ve_cu", None)
    return ket


def phan_loai(so_pmid: int, so_co: int, so_hong: int) -> str:
    """Kết luận được phép in, xét theo SỐ PMID thật sự hỏi được.

    CHUA_DO · KHONG_HOI_DUOC (mọi PMID đều hỏng) · CO_BAI_MOI · MOT_PHAN (có PMID hỏng,
    phần hỏi được thì sạch) · SACH. Chỉ SACH mới được in 🟢.
    """
    if so_pmid == 0:
        return "CHUA_DO"
    if so_hong >= so_pmid:
        return "KHONG_HOI_DUOC"
    if so_co > 0:
        return "CO_BAI_MOI"
    if so_hong > 0:
        return "MOT_PHAN"
    return "SACH"


def main() -> int:
    ap = argparse.ArgumentParser(description="Dò chứng cứ mới hơn có thể đã vượt qua mục đang dùng")
    ap.add_argument("--file", help="chỉ một dashboard")
    ap.add_argument("--gioi-han", type=int, help="chỉ xử lý N mục đầu")
    ap.add_argument("--tu-nam", type=int, help="chỉ tính bài công bố từ năm này trở đi")
    ap.add_argument("--json-ra", metavar="TỆP",
                    help="ghi manifest JSON (kết luận + phạm vi + danh sách PMID có bài mới hơn) để công cụ khác đọc THAY "
                         "vì phân tích chuỗi văn bản của báo cáo")
    ap.add_argument("--gom-consider", action="store_true",
                    help="dò CẢ mục decision='consider' (mặc định chỉ 'apply'). Cần khi gói mới thẩm định trên tóm tắt nên chưa mục nào ở 'apply'.")
    a = ap.parse_args()

    def _xong(rc: int, ket_luan: str, *, so_do: int = 0, so_hong: int = 0, pmid_co: list | None = None,
              pmid_da_do: list | None = None, so_tong: int = 0) -> int:
        """Ghi manifest (nếu được yêu cầu) rồi trả mã thoát. Manifest là nguồn SỰ THẬT cho bên tiêu thụ.

        Mọi đường thoát của main() đều đi qua đây (kể cả «thiếu công cụ») để không bao giờ còn manifest CŨ ghép với báo cáo
        .txt MỚI: lần chạy lại cùng ngày từng ghi đè .txt bằng lượt hỏng trong khi manifest hợp lệ cũ vẫn nằm đó."""
        if a.json_ra:
            import datetime as _dt
            man = {"phien_ban": 2, "tao_luc": _dt.datetime.now().isoformat(timespec="seconds"), "ket_luan": ket_luan,
                   "ma_thoat": rc,
                   "pham_vi": {"decision": sorted(_pham_vi), "file": a.file, "gioi_han": a.gioi_han, "tu_nam": a.tu_nam,
                               "toan_kho": not (a.file or a.gioi_han or a.tu_nam)},
                   "so_pmid_tong": so_tong, "so_pmid_do": so_do, "so_pmid_hong": so_hong,
                   "pmid_da_do": sorted(pmid_da_do or []),
                   "pmid_co_bai_moi": sorted(pmid_co or [])}
            try:
                Path(a.json_ra).write_text(json.dumps(man, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            except OSError as e:
                print(f"  ⚠ Không ghi được manifest {a.json_ra}: {e}")
        return rc

    if a.json_ra:
        # Xoá manifest cũ NGAY từ đầu lượt: nếu lượt này chết giữa chừng thì không còn manifest nào để bên tiêu thụ tin nhầm.
        try:
            Path(a.json_ra).unlink(missing_ok=True)
        except OSError:
            pass

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
              "git-vendor — không dò được trên máy này (KHÔNG phải «không có bài mới hơn»).")
        return _xong(2, "KHONG_CO_CONG_CU")
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
    # IN THAM SỐ ĐẦU BÁO CÁO: một báo cáo không nói mình quét phạm vi nào thì «🟢 không thấy gì» không đọc được.
    print(f"  tham số: phạm vi={'MỘT FILE ' + Path(a.file).name if a.file else 'TOÀN KHO'} · "
          f"--gioi-han={a.gioi_han or 'không'} · --tu-nam={a.tu_nam or 'không'} · tổng PMID khác nhau={len(theo_pmid)}")
    co = 0
    hong = 0
    da_do: list[str] = []
    ket: list[tuple] = []
    for k, pm in enumerate(ds, 1):
        moi = tong_quan_moi_hon(pm, nam_goc.get(pm), a.tu_nam)
        if moi is None:
            hong += 1
            continue
        da_do.append(pm)
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
        return _xong(0, "CHUA_DO", so_tong=len(theo_pmid))
    loai = phan_loai(len(ds), len(ket), hong)
    if loai == "KHONG_HOI_DUOC":
        print("  🟡 KHÔNG HỎI ĐƯỢC PubMed cho %d/%d PMID (mạng lỗi hoặc NCBI đang chặn)." % (hong, len(ds)))
        print("     Đây KHÔNG phải kết luận 'không có chứng cứ mới hơn' — CHƯA kiểm được gì.")
        print("     Chạy lại khi NCBI trả lời được. Cần bác sĩ kiểm chứng.")
        return _xong(2, loai, so_do=len(ds), so_hong=hong, pmid_da_do=da_do, so_tong=len(theo_pmid))
    if loai == "MOT_PHAN":
        print("  🟡 Dò được %d/%d PMID, không thấy bài mới hơn trong số dò được;" % (len(ds) - hong, len(ds)))
        print("     %d PMID KHÔNG hỏi được — phần đó CHƯA kiểm. Cần bác sĩ kiểm chứng." % hong)
        return _xong(2, loai, so_do=len(ds), so_hong=hong, pmid_da_do=da_do, so_tong=len(theo_pmid))
    if not ket:
        # KHÔNG in xanh cho lượt dò MẪU (--gioi-han nhỏ hơn tổng): «không thấy trong N mục đầu» không phải kết luận
        # về toàn kho (họ BH32: chỉ số của MỘT phần tử trình bày như của tập hợp).
        la_mau = bool(a.gioi_han and a.gioi_han < len(theo_pmid))
        if la_mau:
            print("  🟡 MẪU: đã dò %d/%d PMID (--gioi-han) — không thấy bài mới hơn TRONG MẪU; KHÔNG kết luận cho toàn kho."
                  % (len(ds), len(theo_pmid)))
            print("     Chạy lại không có --gioi-han để dò đủ. Cần bác sĩ kiểm chứng.")
            return _xong(0, "MAU", so_do=len(ds), so_hong=hong, pmid_da_do=da_do, so_tong=len(theo_pmid))
        print("  🟢 Đã dò %d PMID%s, không thấy tổng quan/gộp/guideline nào MỚI HƠN%s."
              % (len(ds), " (một file)" if a.file else " (toàn kho)",
                 f" từ năm {a.tu_nam}" if a.tu_nam else ""))
        print("     (Không chứng minh chứng cứ còn đúng — chỉ nghĩa là PubMed không trả bài")
        print("      tổng quan mới hơn nào liên quan. Cần bác sĩ kiểm chứng.)")
        return _xong(0, "SACH", so_do=len(ds), so_hong=hong, pmid_da_do=da_do, so_tong=len(theo_pmid))
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
    if hong:
        print(f"  ⚠️ Còn {hong} PMID KHÔNG hỏi được PubMed — các mục đó CHƯA kiểm.")
    print("  Công cụ KHÔNG tự đổi decision/gradeLevel. Cần bác sĩ kiểm chứng.")
    return _xong(1, "CO_BAI_MOI", so_do=len(ds), so_hong=hong, pmid_co=[k[0] for k in ket], pmid_da_do=da_do,
                 so_tong=len(theo_pmid))


if __name__ == "__main__":
    raise SystemExit(main())
