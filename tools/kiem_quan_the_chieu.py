#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KIỂM CHÉO NGỮ NGHĨA — K1 QUẦN THỂ + K4 CHIỀU KHUYẾN CÁO (25/09/2026)

VÌ SAO CÓ
=========
Thiết kế ở `audit/16-thiet-ke-kiem-cheo-ngu-nghia-apply_2026-09-25.md`, bác sĩ duyệt 25/09/2026:
K3 trước (đã có, `tools/kiem_cheo_ngu_nghia.py`), rồi tới K1; mọi phép kiểm ở MỨC CẢNH BÁO.

Các cổng hiện có chỉ kiểm nguồn có thật và hiệu số HR. Chúng không bắt hai lỗi nguy hiểm:

* **K1 — sai quần thể.** Mục ghi «HFpEF», nguồn chỉ nói HFrEF; mục ghi «eGFR ≥ 20», nguồn
  nói ≥ 25. `pico.P:'match'` chỉ là lời người soạn tự khai.
* **K4 — sai chiều.** Mục `decision:'apply'` nhưng tiêu đề/tóm tắt nguồn nói «not
  recommended», «no significant benefit», «Class III»…

CÁCH LÀM
========
Chỉ đọc mục `decision:'apply'` có PMID/DOI. Văn bản nguồn (tiêu đề + tóm tắt) lấy từ:
  * `--nguon-json TỆP` — {"<pmid|doi>": {"title": "...", "abstract": "..."}} (ngoại tuyến,
    dùng khi đã tải tóm tắt qua connector MCP hoặc từ một lượt trước), và/hoặc
  * `--online` — tải tóm tắt PubMed bằng CHÍNH hàm `lay_tom_tat()` của `kiem_so_lieu.py`.
Không có văn bản nguồn ⇒ ⚪, không bao giờ ✓.

K1: (a) ngưỡng số của EF, eGFR, tuổi, HbA1c, BMI, LDL trong `population` + `pico.P`: nguồn có
nhắc chỉ số đó mà không thấy CON SỐ ấy gần đó ⇒ 🟠 kèm đoạn nguồn; (b) cặp quần thể loại trừ
nhau (HFrEF↔HFpEF, típ 1↔típ 2, trẻ em↔người lớn, thai kỳ↔ngoài thai kỳ, lọc máu↔không lọc
máu): mục mang một vế mà nguồn chỉ nêu vế kia ⇒ 🟠.
K4: tìm tín hiệu ngược chiều rõ ràng trong nguồn ⇒ 🟠 kèm câu nguyên văn.

BA MỨC — cố ý KHÔNG có mức «SAI» (BH08: vắng mặt trong tóm tắt không chứng minh trích sai)
  ✓ khớp · 🟠 cần đọc lại (kèm đoạn nguồn) · ⚪ chưa kiểm được (nguồn không nêu / không tải được)
Tóm tắt thường nêu kết cục phụ «không khác biệt» ngay trong thử nghiệm dương tính ⇒ K4 SẼ có
báo động giả; đó là lý do công cụ chỉ cảnh báo và phải đo trên bộ vàng trước khi tính chặn.
Công cụ KHÔNG sửa dashboard, KHÔNG đổi `decision`, KHÔNG chặn xuất.

Dùng:
    python tools/kiem_quan_the_chieu.py DASH.html --nguon-json tom_tat.json
    python tools/kiem_quan_the_chieu.py DASH.html --online [--json]

Mã thoát: 0 = không có 🟠 · 1 = có mục cần đọc lại · 2 = không đo được (không đọc được DATA,
hoặc không mục apply nào có văn bản nguồn). «Không đo được» không bao giờ là 0.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / "tools" / tep)
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod


_K3 = _nap("_k3_kqtc", "kiem_cheo_ngu_nghia.py")
chuan_hoa = _K3.chuan_hoa
doc_data = _K3.doc_data

# ── K1a: ngưỡng số ─────────────────────────────────────────────────────────────
# (khoá, mẫu nhận chỉ số ở MỤC (Việt/Anh), mẫu nhận chỉ số ở NGUỒN (Anh))
_CHI_SO = (
    ("ef", r"(?:lv)?ef|phân suất tống máu", r"(?:lv)?ef|ejection fraction"),
    ("egfr", r"egfr|mlct|mức lọc cầu thận", r"egfr|glomerular filtration"),
    ("tuoi", r"tuổi|age[ds]?", r"aged?|years of age|years old|years or older|older"),
    ("hba1c", r"hba1c|a1c", r"hba1c|a1c|glycated h[a]?emoglobin"),
    ("bmi", r"bmi", r"bmi|body mass index"),
    ("ldl", r"ldl(?:-c)?", r"ldl(?:-c| cholesterol)?"),
)
_SO = r"(\d+(?:[.,]\d+)?)"
_TOAN_TU = r"(<=|>=|<|>|=|dưới|trên|từ)?"
_CUA_SO = 60   # ký tự quanh chỉ số trong nguồn để tìm con số


def trich_nguong(van_ban: str) -> list[tuple[str, str]]:
    """[(khoá chỉ số, con số)] từ văn bản MỤC. «≥65 tuổi» và «tuổi ≥ 65» đều được."""
    t = chuan_hoa(van_ban)
    ra: list[tuple[str, str]] = []
    for khoa, mau_muc, _ in _CHI_SO:
        truoc = re.compile(rf"(?<!\w)(?:{mau_muc})(?!\w)\s*{_TOAN_TU}\s*{_SO}")
        sau = re.compile(rf"{_TOAN_TU}\s*{_SO}\s*%?\s*(?:{mau_muc})(?!\w)")
        for m in list(truoc.finditer(t)) + (list(sau.finditer(t)) if khoa == "tuoi" else []):
            so = m.group(2).replace(",", ".")
            if (khoa, so) not in ra:
                ra.append((khoa, so))
    return ra


def _doan(t: str, i: int, j: int, le: int = 70) -> str:
    return t[max(0, i - le):min(len(t), j + le)].strip()


def kiem_nguong(khoa: str, so: str, nguon: str) -> tuple[str, str]:
    """(mức, đoạn nguồn). Nguồn đã chuẩn hoá."""
    mau_nguon = next(m for k, _, m in _CHI_SO if k == khoa)
    lan = list(re.finditer(rf"(?<!\w)(?:{mau_nguon})(?!\w)", nguon))
    if not lan:
        return "chua_kiem", ""
    so_re = re.compile(rf"(?<![\d.]){re.escape(so)}(?:\.0+)?(?![\d])")
    for m in lan:
        vung = nguon[max(0, m.start() - _CUA_SO):m.end() + _CUA_SO]
        if so_re.search(vung):
            return "khop", _doan(nguon, m.start(), m.end())
    m = lan[0]
    return "can_doc", _doan(nguon, m.start(), m.end())


# ── K1b: cặp quần thể loại trừ nhau ────────────────────────────────────────────
# Mỗi vế: (tên, mẫu ở MỤC, mẫu ở NGUỒN). Vế «phủ định» (non-dialysis…) được xoá khỏi văn bản
# trước khi tìm vế dương tương ứng, để «non-dialysis» không bị đọc thành «dialysis».
_CAP = (
    (("HFrEF", r"hfref|phân suất tống máu giảm|ef giảm", r"hfref|reduced ejection fraction"),
     ("HFpEF", r"hfpef|phân suất tống máu bảo tồn|ef bảo tồn", r"hfpef|preserved ejection fraction")),
    (("ĐTĐ típ 1", r"(?:típ|tuýp|type) ?1", r"type 1 diabetes|t1d"),
     ("ĐTĐ típ 2", r"(?:típ|tuýp|type) ?2", r"type 2 diabetes|t2d")),
    (("trẻ em", r"trẻ em|nhi khoa|children|pediatric", r"children|pa?ediatric|adolescents?|infants?"),
     ("người lớn", r"người lớn|adults?", r"adults?")),
    (("ngoài thai kỳ", r"ngoài thai kỳ|không mang thai|non-pregnant", r"non-?pregnant|not pregnant"),
     ("thai kỳ", r"thai kỳ|phụ nữ có thai|mang thai|pregnan\w*", r"pregnan\w*")),
    (("không lọc máu", r"không lọc máu|chưa lọc máu|non-dialysis", r"non-?dialysis|not (?:on|receiving) dialysis"),
     ("lọc máu", r"lọc máu|chạy thận|thẩm phân|dialysis", r"dialysis|ha?emodialysis")),
)


# Tiền tố phủ định ở MỤC: «không chuyên HFrEF», «loại trừ trẻ em», «excluding dialysis»… ⇒ mục KHÔNG
# mang vế đó. Cho phép tối đa 2 từ chen giữa («không áp dụng cho bệnh nhân HFrEF»).
_PHU_DINH = (r"(?:không(?: chuyên| phải| chỉ| dành cho| áp dụng cho| gồm| có)?|ngoại trừ|loại trừ|trừ"
             r"|excluding|without|not)")


def _bo_phu_dinh(mau: str, t: str) -> str:
    """Xoá các lần vế `mau` xuất hiện SAU một tiền tố phủ định (vế phủ định không phải vế mang)."""
    return re.sub(rf"(?<!\w){_PHU_DINH}\s+(?:[^\s.;,()]+\s+){{0,2}}?(?:{mau})(?!\w)", " ", t)


def _co(mau: str, t: str) -> bool:
    return re.search(rf"(?<!\w)(?:{mau})(?!\w)", t) is not None


def _xoa(mau: str, t: str) -> str:
    return re.sub(rf"(?<!\w)(?:{mau})(?!\w)", " ", t)


def kiem_cap(muc: str, nguon: str) -> list[dict]:
    """Mỗi phần tử: {ve_muc, ve_nguon, muc: khop|can_doc|chua_kiem}."""
    ra = []
    for a, b in _CAP:
        # vế đầu của mỗi cặp ở trên được đặt sao cho vế «phủ định/đặc hiệu hơn» xét trước
        muc_con = muc
        nguon_con = nguon
        co_muc = {}
        co_nguon = {}
        for ten, m_muc, m_nguon in (a, b):
            muc_con = _bo_phu_dinh(m_muc, muc_con)
            co_muc[ten] = _co(m_muc, muc_con)
            co_nguon[ten] = _co(m_nguon, nguon_con)
            if co_muc[ten]:
                muc_con = _xoa(m_muc, muc_con)
            if co_nguon[ten]:
                nguon_con = _xoa(m_nguon, nguon_con)
        for ten, doi in ((a[0], b[0]), (b[0], a[0])):
            if not co_muc[ten] or co_muc[doi]:
                continue           # mục không mang vế này, hoặc mang cả hai vế (không kết luận)
            if co_nguon[ten]:
                kq = "khop"
            elif co_nguon[doi]:
                kq = "can_doc"
            else:
                kq = "chua_kiem"
            ra.append({"ve_muc": ten, "ve_nguon": doi if kq == "can_doc" else ten, "muc": kq})
    return ra


# ── K4: tín hiệu ngược chiều ───────────────────────────────────────────────────
_NGUOC = re.compile(
    r"(?<!\w)(?:is |are )?not recommended|should not be (?:used|given|offered|prescribed)"
    r"|no (?:significant |clinically meaningful |additional )?(?:benefit|reduction|improvement|difference)"
    r"|did not (?:significantly )?(?:reduce|improve|lower|prevent|decrease)"
    r"|was not (?:superior|associated with (?:a )?(?:lower|reduced|improved))"
    r"|failed to (?:reduce|improve|show|demonstrate)"
    r"|class iii|net harm|(?:increased|caused) (?:the )?(?:risk of )?harm|stopped (?:early )?for futility"
)


# Câu «không khác biệt» về kết cục PHỤ/an toàn/phân nhóm là chuyện thường trong thử nghiệm DƯƠNG
# tính — không phải tín hiệu ngược chiều của khuyến cáo. Bỏ qua trừ khi câu cũng nói tới kết cục
# CHÍNH; «not recommended»/«Class III»/«should not» thì KHÔNG BAO GIỜ bỏ qua.
_PHU = re.compile(r"secondary|exploratory|subgroup|post[ -]?hoc|adverse events?|serious adverse|safety"
                  r"|tolerab|discontinuation")
_CHINH = re.compile(r"primary (?:end ?point|outcome|composite)")
_LUON_BAO = re.compile(r"not recommended|should not be|class iii|net harm|futility")


def kiem_chieu_chi_tiet(nguon: str) -> tuple[list[str], list[str]]:
    """(câu ngược chiều cần đọc lại, câu đã bỏ qua vì chỉ về kết cục phụ/an toàn) — tối đa 3 mỗi loại."""
    cau = re.split(r"(?<=[.;])\s+", nguon)
    bao: list[str] = []
    bo: list[str] = []
    for c in cau:
        c = c.strip()
        if not _NGUOC.search(c):
            continue
        if not _LUON_BAO.search(c) and _PHU.search(c) and not _CHINH.search(c):
            bo.append(c)
        else:
            bao.append(c)
    return bao[:3], bo[:3]


def kiem_chieu(nguon: str) -> list[str]:
    """Các câu nguồn chứa tín hiệu ngược chiều (nguyên văn đã chuẩn hoá, tối đa 3)."""
    return kiem_chieu_chi_tiet(nguon)[0]


# ── Nguồn ──────────────────────────────────────────────────────────────────────
def _khoa_nguon(it: dict) -> list[str]:
    return [str(x).strip() for x in (it.get("pmid"), it.get("doi")) if x and str(x).strip()]


def nap_nguon_json(p: str | None) -> dict[str, str]:
    if not p:
        return {}
    try:
        raw = json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    ra = {}
    for k, v in (raw.items() if isinstance(raw, dict) else []):
        if isinstance(v, dict):
            ra[str(k).strip()] = f"{v.get('title') or ''}. {v.get('abstract') or ''}"
        elif isinstance(v, str):
            ra[str(k).strip()] = v
    return ra


def _tai_online(pmid: str) -> str | None:
    if not pmid.isdigit():
        return None
    try:
        return _nap("_ksl_kqtc", "kiem_so_lieu.py").lay_tom_tat(pmid)
    except Exception:   # noqa: BLE001 — lỗi tải = ⚪ chưa kiểm, không làm chết cả lượt
        return None


def _van_ban_muc(it: dict) -> str:
    p = it.get("population") or ""
    pico = it.get("pico")
    if isinstance(pico, dict) and isinstance(pico.get("P"), str) and pico["P"] not in ("match", "partial", "mismatch"):
        p = f"{p}. {pico['P']}"
    return p


def kiem_muc(it: dict, nguon_tho: str | None) -> dict:
    muc_tx = chuan_hoa(_van_ban_muc(it))
    dong = {"id": it.get("id") or "?", "pmid": it.get("pmid"), "doi": it.get("doi"),
            "co_nguon": nguon_tho is not None, "k1_nguong": [], "k1_cap": [], "k4": None}
    if nguon_tho is None:
        return dong
    ng = chuan_hoa(nguon_tho)
    for khoa, so in trich_nguong(muc_tx):
        muc, doan = kiem_nguong(khoa, so, ng)
        dong["k1_nguong"].append({"chi_so": khoa, "so": so, "muc": muc, "doan_nguon": doan})
    dong["k1_cap"] = kiem_cap(muc_tx, ng)
    tin_hieu, bo_qua = kiem_chieu_chi_tiet(ng)
    dong["k4"] = {"muc": "can_doc" if tin_hieu else "khop", "cau_nguon": tin_hieu, "cau_bo_qua": bo_qua}
    return dong


def kiem_dashboard(data: dict, nguon: dict[str, str], online: bool) -> dict:
    ra = []
    for it in data.get("items") or []:
        if not (isinstance(it, dict) and it.get("decision") == "apply" and _khoa_nguon(it)):
            continue
        tx = next((nguon[k] for k in _khoa_nguon(it) if k in nguon), None)
        if tx is None and online and it.get("pmid"):
            tx = _tai_online(str(it["pmid"]).strip())
        ra.append(kiem_muc(it, tx))
    dem = {"khop": 0, "can_doc": 0, "chua_kiem": 0}
    for d in ra:
        if not d["co_nguon"]:
            dem["chua_kiem"] += 1
            continue
        for x in d["k1_nguong"] + d["k1_cap"] + [d["k4"]]:
            dem[x["muc"]] += 1
    return {"muc": ra, "dem": dem, "so_muc_co_nguon": sum(d["co_nguon"] for d in ra)}


_KH = {"khop": "✓", "can_doc": "🟠", "chua_kiem": "⚪"}


def in_bao_cao(ten: str, kq: dict) -> None:
    print(f"K1 quần thể + K4 chiều khuyến cáo · {ten}")
    print(f"  mục apply có PMID/DOI: {len(kq['muc'])} · có văn bản nguồn: {kq['so_muc_co_nguon']}")
    for d in kq["muc"]:
        dinh_danh = d["pmid"] or d["doi"]
        if not d["co_nguon"]:
            print(f"  ⚪ [{d['id']}] {dinh_danh}: không có văn bản nguồn — chưa kiểm")
            continue
        for x in d["k1_nguong"]:
            print(f"  {_KH[x['muc']]} [{d['id']}] K1 {x['chi_so']} {x['so']}"
                  + (f" — nguồn: «{x['doan_nguon']}»" if x["muc"] == "can_doc" else ""))
        for x in d["k1_cap"]:
            thong = (f"mục ghi «{x['ve_muc']}», nguồn chỉ nêu «{x['ve_nguon']}»"
                     if x["muc"] == "can_doc" else f"«{x['ve_muc']}»")
            print(f"  {_KH[x['muc']]} [{d['id']}] K1 quần thể {thong}")
        k4 = d["k4"]
        if k4["muc"] == "can_doc":
            for c in k4["cau_nguon"]:
                print(f"  🟠 [{d['id']}] K4 tín hiệu ngược chiều trong nguồn: «{c[:200]}»")
        else:
            print(f"  ✓ [{d['id']}] K4 không thấy tín hiệu ngược chiều rõ ràng"
                  + (f" (bỏ qua {len(k4['cau_bo_qua'])} câu chỉ về kết cục phụ/an toàn)" if k4["cau_bo_qua"] else ""))
    e = kq["dem"]
    print(f"Tổng: {e['khop']} ✓ khớp · {e['can_doc']} 🟠 cần đọc lại · {e['chua_kiem']} ⚪ chưa kiểm")
    if e["can_doc"]:
        print("🟠 = cần ĐỌC LẠI nguồn gốc, KHÔNG phải kết luận «sai». K4 hay báo cả kết cục phụ "
              "«không khác biệt» trong thử nghiệm dương tính. Công cụ chỉ cảnh báo.")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="K1 quần thể + K4 chiều khuyến cáo (chỉ cảnh báo)")
    ap.add_argument("dashboard", help="WebDashboard_*.html")
    ap.add_argument("--nguon-json", help='{"<pmid|doi>": {"title": "...", "abstract": "..."}}')
    ap.add_argument("--online", action="store_true", help="tải tóm tắt PubMed cho PMID còn thiếu")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    dash = Path(a.dashboard)
    data = doc_data(dash)
    if data is None:
        print(f"⚪ Không đọc được khối DATA của {dash} — không đo được.")
        return 2
    kq = kiem_dashboard(data, nap_nguon_json(a.nguon_json), a.online)
    kq["dashboard"] = str(dash)
    if a.json:
        print(json.dumps(kq, ensure_ascii=False, indent=2))
    else:
        in_bao_cao(dash.name, kq)
    if not kq["so_muc_co_nguon"]:
        return 2
    return 1 if kq["dem"]["can_doc"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
