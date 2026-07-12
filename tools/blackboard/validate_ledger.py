# -*- coding: utf-8 -*-
"""
validate_ledger.py — Trình KIỂM ĐỊNH SCHEMA cho sổ cái blackboard EBM.

Mục đích: thực thi (enforce) SCHEMA bản ghi của `_SO-EBM-MASTER.md` và hub
`EBM_MASTER/EBM_MASTER.json` — kiểm mỗi bản ghi đủ 8 trường, khóa chống trùng
(dedup), và `verification_status` hợp lệ. GIÚP siết độ chặt của quy ước
blackboard; KHÔNG tự sửa dữ liệu, KHÔNG bịa.

[GIỚI HẠN — đọc kỹ] Đây là TRÌNH KIỂM ĐỊNH offline (lint), KHÔNG phải message
bus cưỡng chế. Schema blackboard hiện vẫn là QUY ƯỚC ở tầng file: các agent
ĐỒNG Ý ghi theo schema, validator chỉ phát hiện vi phạm SAU khi ghi. Vì vậy
hạng mục "1b Blackboard" vẫn ở mức MỘT PHẦN (chắc hơn, nhưng chưa thành bus thật).

Dùng:
    python3 validate_ledger.py <ledger.json>            # kiểm 1 file
    python3 validate_ledger.py <ledger.json> --json     # in JSON
    python3 validate_ledger.py --demo                   # chạy demo trên dữ liệu synthetic

Đầu vào chấp nhận:
  (1) JSON là LIST các bản ghi blackboard 8-trường;
  (2) JSON là OBJECT có khóa "records" (list bản ghi 8-trường); hoặc
  (3) Hub EBM_MASTER.json (object có "evidence_cards") — sẽ tự ánh xạ thẻ -> 8 trường.

Quy ước thoát: 0 = không lỗi ĐỎ; 1 = có ít nhất một lỗi ĐỎ (ERROR).

[PROTOTYPE — chạy demo trên synthetic; KHÔNG tự sửa sổ cái, mọi thay đổi do bác sĩ duyệt.]
"""
from __future__ import annotations
import argparse, json, re, sys, unicodedata

# 8 trường bắt buộc theo SCHEMA của _SO-EBM-MASTER.md
REQUIRED_FIELDS = ["id", "ngay", "chu_de", "nguon", "loai",
                   "verification_status", "phan_loai", "agent_ghi"]

# Tập giá trị hợp lệ (hợp nhất sổ run-log + hub)
VALID_STATUS = {"chưa xác minh", "đang xác minh", "đã xác minh"}
VALID_LOAI = {"chứng cứ", "khuyến cáo"}
VALID_PHANLOAI = {"đáng đổi", "theo dõi", "không đổi"}

# Nhãn placeholder hợp lệ (schema cho phép đánh dấu thay vì bỏ trống)
PLACEHOLDERS = ["[CẦN BỔ SUNG]", "[CẦN KIỂM CHỨNG]",
                "[CẦN XÁC NHẬN TẠI ĐƠN VỊ]", "[DỰ THẢO]"]

RE_PMID = re.compile(r"PMID[:\s]*\d{4,9}", re.I)
RE_DOI = re.compile(r"\b10\.\d{4,9}/\S+", re.I)
RE_URL = re.compile(r"https?://\S+", re.I)
RE_NGAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RE_YEAR = re.compile(r"\b(19|20)\d{2}\b")


def chuan_hoa(s: str) -> str:
    """Chuẩn hóa chuỗi để so khóa chống trùng (bỏ dấu phụ, hạ chữ, gộp khoảng trắng)."""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s


def co_placeholder(v: str) -> bool:
    return any(p in str(v) for p in PLACEHOLDERS)


# ---------- Ánh xạ thẻ hub EBM_MASTER.json -> 8 trường blackboard ---------- #
def map_evidence_card(c: dict) -> dict:
    src = c.get("source", {}) or {}
    parts = []
    if src.get("pmid"): parts.append("PMID:" + str(src["pmid"]))
    if src.get("doi"): parts.append(str(src["doi"]))
    if src.get("url"): parts.append(str(src["url"]))
    if src.get("agency") or c.get("date_source"):
        parts.append(f"{src.get('agency','')} {c.get('date_source','')}".strip())
    nguon = " | ".join([p for p in parts if p]) or ""
    loai = "khuyến cáo" if str(c.get("recommendation", "")).strip() else "chứng cứ"
    # ánh xạ tác động -> phan_loai (hub không có cột chuẩn -> đánh dấu nếu thiếu)
    # 2026-07-12: 'consider' (decision phổ biến nhất trong hub, 130/259 thẻ) trước đây rơi
    # vào nhánh else -> cảnh báo giả "phan_loai placeholder" cho gần một nửa sổ cái. Khớp
    # đúng ngữ nghĩa DEC_VI/DEC_ICON đã dùng ở manage_ledger.py ("consider" = "Cân nhắc"
    # -> theo dõi thêm trước khi đổi thực hành).
    impact = str(c.get("impact", "") or c.get("decision", "")).lower()
    if "apply" in impact or "đáng đổi" in impact or "change" in impact:
        phan = "đáng đổi"
    elif "consider" in impact or "monitor" in impact or "theo dõi" in impact or "watch" in impact or "cân nhắc" in impact:
        phan = "theo dõi"
    elif "notyet" in impact or "no" in impact or "không đổi" in impact:
        phan = "không đổi"
    else:
        phan = "[CẦN BỔ SUNG]"
    return {
        "id": c.get("id", ""),
        "ngay": c.get("date_added", ""),
        "chu_de": c.get("topic", ""),
        "nguon": nguon,
        "loai": loai,
        "verification_status": c.get("verification_status", ""),
        "phan_loai": phan,
        "agent_ghi": c.get("provenance", "") or c.get("agent_ghi", ""),
        "_src_pmid": src.get("pmid", ""),
        "_src_doi": src.get("doi", ""),
    }


def load_records(path: str):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data, "blackboard-list"
    if isinstance(data, dict):
        if "records" in data and isinstance(data["records"], list):
            return data["records"], "blackboard-records"
        if "evidence_cards" in data and isinstance(data["evidence_cards"], list):
            return [map_evidence_card(c) for c in data["evidence_cards"]], "hub-EBM_MASTER"
    raise ValueError("Định dạng không nhận diện được (cần list, {records:[]}, hoặc {evidence_cards:[]}).")


def nguon_hop_le(rec: dict) -> bool:
    v = str(rec.get("nguon", ""))
    if co_placeholder(v):
        return True  # cho phép [CẦN KIỂM CHỨNG] thay vì bịa nguồn
    if rec.get("_src_pmid") or rec.get("_src_doi"):
        return True
    return bool(RE_PMID.search(v) or RE_DOI.search(v) or RE_URL.search(v))


def validate(records):
    """Trả về (danh sách kết quả từng bản ghi, thống kê)."""
    results = []
    seen_id = {}
    seen_dedup = {}
    n_err = n_warn = 0

    for i, rec in enumerate(records):
        errs, warns = [], []
        if not isinstance(rec, dict):
            errs.append("Bản ghi không phải object.")
            results.append({"index": i, "id": None, "errors": errs, "warnings": warns})
            n_err += len(errs)
            continue

        # 1) Đủ 8 trường
        for fld in REQUIRED_FIELDS:
            if fld not in rec:
                errs.append(f"THIẾU trường bắt buộc: '{fld}'")
            elif str(rec[fld]).strip() == "":
                errs.append(f"Trường '{fld}' rỗng (nếu thiếu dữ liệu phải ghi nhãn [CẦN BỔ SUNG]).")
            elif co_placeholder(rec[fld]) and fld != "nguon":
                warns.append(f"Trường '{fld}' đang là placeholder ({rec[fld]}) — cần bổ sung sau.")

        rid = str(rec.get("id", "")).strip()

        # 2) id duy nhất
        if rid:
            if rid in seen_id:
                errs.append(f"TRÙNG id '{rid}' (đã xuất hiện ở bản ghi #{seen_id[rid]}).")
            else:
                seen_id[rid] = i

        # 3) verification_status hợp lệ
        # 2026-07-12: so khớp CHÍNH XÁC trước đây báo lỗi ĐỎ giả cho 85/259 thẻ hub —
        # hub thật dùng biến thể mở rộng có chú thích thêm (vd "đã xác minh nguồn chính
        # thức", "chưa xác minh — thấp ưu tiên...") mà vẫn hợp lệ vì BẮT ĐẦU bằng 1 trong
        # 3 giá trị chuẩn. Đổi sang so khớp TIỀN TỐ — không nới lỏng: giá trị không bắt
        # đầu bằng chuẩn nào (vd "đã duyệt" ở ca demo #2) vẫn bị bắt lỗi như cũ.
        vs = str(rec.get("verification_status", "")).strip()
        if vs and not any(vs.startswith(s) for s in VALID_STATUS):
            errs.append(f"verification_status không hợp lệ: '{vs}' (phải KHỚP hoặc BẮT ĐẦU bằng: {sorted(VALID_STATUS)}).")

        # 4) loai / phan_loai
        lo = str(rec.get("loai", "")).strip()
        if lo and lo not in VALID_LOAI:
            warns.append(f"loai='{lo}' ngoài tập chuẩn {sorted(VALID_LOAI)}.")
        pl = str(rec.get("phan_loai", "")).strip()
        if pl and not co_placeholder(pl) and pl not in VALID_PHANLOAI:
            warns.append(f"phan_loai='{pl}' ngoài tập chuẩn {sorted(VALID_PHANLOAI)}.")

        # 5) ngay đúng dạng YYYY-MM-DD
        ng = str(rec.get("ngay", "")).strip()
        if ng and not co_placeholder(ng) and not RE_NGAY.match(ng):
            warns.append(f"ngay='{ng}' không đúng dạng YYYY-MM-DD.")

        # 6) nguon: có PMID/DOI/URL hoặc nhãn [CẦN KIỂM CHỨNG] (chống bịa/không nguồn)
        if "nguon" in rec and str(rec["nguon"]).strip():
            if not nguon_hop_le(rec):
                errs.append("nguon không có PMID/DOI/URL và cũng không gắn [CẦN KIỂM CHỨNG] (KHÔNG để nguồn trống).")
            elif not co_placeholder(rec["nguon"]) and not RE_YEAR.search(str(rec["nguon"])):
                warns.append("nguon thiếu NĂM — mặc định nên có nguồn + năm.")

        # 7) khóa chống trùng: pmid | doi | (chu_de chuẩn hóa)
        pmid = ""
        m = RE_PMID.search(str(rec.get("nguon", "")))
        if m: pmid = re.sub(r"\D", "", m.group(0))
        if rec.get("_src_pmid"): pmid = re.sub(r"\D", "", str(rec["_src_pmid"]))
        doi = ""
        md = RE_DOI.search(str(rec.get("nguon", "")))
        if md: doi = md.group(0).lower()
        if rec.get("_src_doi"): doi = str(rec["_src_doi"]).lower()
        dedup = pmid or doi or chuan_hoa(rec.get("chu_de", ""))
        if dedup:
            if dedup in seen_dedup:
                warns.append(f"KHÓA TRÙNG '{dedup}' với bản ghi #{seen_dedup[dedup]} "
                             f"(theo schema: KHÔNG thêm bản ghi mới — chỉ nối bản ghi cập nhật trạng thái trỏ id cũ).")
            else:
                seen_dedup[dedup] = i

        results.append({"index": i, "id": rid or None, "errors": errs, "warnings": warns})
        n_err += len(errs)
        n_warn += len(warns)

    stats = {"records": len(records), "errors": n_err, "warnings": n_warn,
             "records_with_error": sum(1 for r in results if r["errors"])}
    return results, stats


# ---------------- Dữ liệu synthetic cho --demo (KHÔNG phải dữ liệu thật) ---------------- #
SYNTHETIC = [
    {  # 0 — hợp lệ
        "id": "EBM-20260613-timmach-01", "ngay": "2026-06-13",
        "chu_de": "Ngưỡng huyết áp khởi trị ở người lớn nguy cơ cao",
        "nguon": "PMID:38000001 (ESC 2024)", "loai": "khuyến cáo",
        "verification_status": "chưa xác minh", "phan_loai": "đáng đổi",
        "agent_ghi": "cap-nhat-guideline",
    },
    {  # 1 — hợp lệ, nguồn DOI
        "id": "EBM-20260613-hohap-01", "ngay": "2026-06-13",
        "chu_de": "Vai trò ICS trong COPD ổn định",
        "nguon": "10.1016/j.jacc.2023.05.001 (GOLD 2024)", "loai": "chứng cứ",
        "verification_status": "đã xác minh", "phan_loai": "theo dõi",
        "agent_ghi": "tra-cuu-chung-cu",
    },
    {  # 2 — LỖI: thiếu trường 'agent_ghi' + verification_status sai
        "id": "EBM-20260613-than-01", "ngay": "2026-06-13",
        "chu_de": "SGLT2i ở bệnh thận mạn không đái tháo đường",
        "nguon": "PMID:38000003 (KDIGO 2024)", "loai": "khuyến cáo",
        "verification_status": "đã duyệt", "phan_loai": "đáng đổi",
    },
    {  # 3 — LỖI: nguồn trống/không nguồn, không [CẦN KIỂM CHỨNG]
        "id": "EBM-20260613-tieuhoa-01", "ngay": "2026-06-13",
        "chu_de": "Thời gian dùng PPI trong loét dạ dày",
        "nguon": "theo kinh nghiệm", "loai": "chứng cứ",
        "verification_status": "chưa xác minh", "phan_loai": "không đổi",
        "agent_ghi": "huong-dan-lam-sang",
    },
    {  # 4 — LỖI: TRÙNG id với #0
        "id": "EBM-20260613-timmach-01", "ngay": "2026-06-13",
        "chu_de": "Mục tiêu LDL-C trong phòng ngừa thứ phát",
        "nguon": "PMID:38000005 (ESC 2024)", "loai": "khuyến cáo",
        "verification_status": "chưa xác minh", "phan_loai": "đáng đổi",
        "agent_ghi": "cap-nhat-guideline",
    },
    {  # 5 — CẢNH BÁO: khóa trùng PMID với #0 (cùng PMID 38000001), placeholder hợp lệ ở 'ngay'
        "id": "EBM-20260613-timmach-02", "ngay": "[CẦN BỔ SUNG]",
        "chu_de": "Ngưỡng huyết áp khởi trị — bản nhắc lại",
        "nguon": "PMID:38000001 (ESC 2024)", "loai": "khuyến cáo",
        "verification_status": "đang xác minh", "phan_loai": "theo dõi",
        "agent_ghi": "so-cai-ghi-nho",
    },
    {  # 6 — hợp lệ, nguồn dạng [CẦN KIỂM CHỨNG] (chấp nhận, không bịa)
        "id": "EBM-20260613-noitiet-01", "ngay": "2026-06-13",
        "chu_de": "Cá thể hóa HbA1c ở người cao tuổi",
        "nguon": "[CẦN KIỂM CHỨNG]", "loai": "khuyến cáo",
        "verification_status": "chưa xác minh", "phan_loai": "theo dõi",
        "agent_ghi": "ke-don-an-toan",
    },
]


def in_bao_cao(results, stats, src_label):
    print(f"== KIỂM ĐỊNH SỔ CÁI BLACKBOARD ==  (nguồn: {src_label})")
    print(f"Tổng bản ghi: {stats['records']} | ĐỎ (error): {stats['errors']} "
          f"| VÀNG (warn): {stats['warnings']} | bản ghi có lỗi: {stats['records_with_error']}\n")
    for r in results:
        if not r["errors"] and not r["warnings"]:
            print(f"  ✅ #{r['index']} [{r['id']}] — ĐẠT")
            continue
        head = "⛔" if r["errors"] else "⚠️"
        print(f"  {head} #{r['index']} [{r['id']}]")
        for e in r["errors"]:
            print(f"       ĐỎ : {e}")
        for w in r["warnings"]:
            print(f"       VÀNG: {w}")
    print()
    verdict = "TRẢ-VỀ-SỬA (có lỗi ĐỎ)" if stats["errors"] else "PASS schema (không lỗi ĐỎ)"
    print(f"KẾT LUẬN: {verdict}")
    print("Cần bác sĩ kiểm chứng.")


def main():
    ap = argparse.ArgumentParser(description="Kiểm định schema sổ cái blackboard EBM.")
    ap.add_argument("ledger", nargs="?", help="đường dẫn JSON sổ cái")
    ap.add_argument("--demo", action="store_true", help="chạy trên dữ liệu synthetic")
    ap.add_argument("--json", action="store_true", help="in kết quả JSON")
    args = ap.parse_args()

    if args.demo:
        records, src = SYNTHETIC, "DEMO-synthetic (KHÔNG phải dữ liệu thật)"
    elif args.ledger:
        records, src = load_records(args.ledger)
    else:
        ap.error("cần <ledger.json> hoặc --demo")

    results, stats = validate(records)
    if args.json:
        print(json.dumps({"source": src, "stats": stats, "results": results},
                         ensure_ascii=False, indent=2))
    else:
        in_bao_cao(results, stats, src)
    sys.exit(1 if stats["errors"] else 0)


if __name__ == "__main__":
    main()
