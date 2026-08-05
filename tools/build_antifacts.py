#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_antifacts.py — Sinh trang "Antifacts" (Trung tâm EBM theo chuyên khoa).

Antifacts KHÔNG phải nền tảng bên ngoài: đây là MẶT TIỀN gom mọi "sản phẩm" EBM
đã có sẵn trong thư mục "Claude AI" lại theo CHUYÊN KHOA, gồm 2 loại:
  (1) Cập nhật chứng cứ  -> quét EBM-Dashboards/WebDashboard_*.html (+ enrich từ library.json)
  (2) Thang điểm lâm sàng -> đọc medical-ebm-automation/data/reference/clinical_scores_45.json
  (3) Công cụ nghiên cứu  -> danh mục chuẩn (RoB2/GRADE/CONSORT...) trỏ về agent tương ứng

Nguyên tắc: KHÔNG bịa dữ liệu. Chỉ gom + trình bày lại nguồn đã có. Mỗi lần có
dashboard mới, chạy lại script này (hoặc thêm vào "Đồng bộ EBM.command") là Antifacts
tự cập nhật. Sửa BỐ CỤC = sửa file này rồi chạy lại, KHÔNG sửa tay Antifacts.html.

Chạy:  python3 tools/build_antifacts.py
Ra:    Antifacts.html  (ở thư mục gốc "Claude AI")
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

# ---- Đường dẫn (gốc = thư mục cha của tools/) ----------------------------------
ROOT = Path(__file__).resolve().parent.parent
DASH_DIR = ROOT / "EBM-Dashboards"
LIBRARY_JSON = DASH_DIR / "library.json"
SCALES_JSON = ROOT / "medical-ebm-automation" / "data" / "reference" / "clinical_scores_45.json"
OUT_HTML = ROOT / "Antifacts.html"


def configure_utf8_stdio() -> None:
    """In tiếng Việt ổn định trên Windows console."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

# ---- Danh mục chuyên khoa (thứ tự hiển thị + biểu tượng) -----------------------
SPECIALTIES = [
    ("Tim mạch", "❤️"),
    ("Hô hấp", "🫁"),
    ("Tiêu hóa – Gan mật", "🩺"),
    ("Nội tiết – Chuyển hóa", "🧬"),
    ("Thận – Tiết niệu", "🫘"),
    ("Huyết học", "🩸"),
    ("Thần kinh – Đột quỵ", "🧠"),
    ("Cơ xương khớp – Thấp khớp", "🦴"),
    ("Nhiễm khuẩn", "🦠"),
    ("Tâm thần kinh", "🧩"),
    ("Lão khoa – Đa bệnh lý", "👴"),
    ("Cấp cứu", "🚑"),
    ("Thuốc & An toàn thuốc", "💊"),
    ("Tổng hợp / Đa khoa", "📚"),
]
SPEC_NAMES = [s[0] for s in SPECIALTIES]
FALLBACK_SPEC = "Tổng hợp / Đa khoa"


def specialty_of_scale(group: str) -> str:
    """Quy nhóm thang điểm (A. Tim mạch, B. Tiêu hóa…) về 1 chuyên khoa chuẩn."""
    g = (group or "").lower()
    if "tâm thần" in g:
        return "Tâm thần kinh"
    if "tim mạch" in g:
        return "Tim mạch"
    if "tiêu hóa" in g:
        return "Tiêu hóa – Gan mật"
    if "nội tiết" in g:
        return "Nội tiết – Chuyển hóa"
    if "cơ xương" in g or "đau mạn" in g or "thấp khớp" in g:
        return "Cơ xương khớp – Thấp khớp"
    if "hô hấp" in g or "giấc ngủ" in g:
        return "Hô hấp"
    if "cấp cứu" in g:
        return "Cấp cứu"
    # còn lại của nhóm F (lão khoa, chức năng, nhận thức, đa bệnh, đa thuốc, dinh dưỡng)
    return "Lão khoa – Đa bệnh lý"


# Bộ luật map DASHBOARD -> chuyên khoa (xét theo THỨ TỰ; khớp đầu tiên thắng).
# Đặt nội tiết/thần kinh TRƯỚC "thận" để tránh 'than' dính nhầm 'thankinh'.
DASH_RULES = [
    # Da liễu/Nhi khoa/PHCN ĐẶT TRƯỚC "Cấp cứu"/"Tổng hợp" để khớp từ khóa cụ thể
    # trước khi rơi vào "ban đầu" (cấp cứu ban đầu) hay bị gộp catch-all chung.
    ("Da liễu", ["dalieu", "da liễu", "hidradenitis", "viêm tuyến mồ hôi mủ", "acne inversa"]),
    ("Nhi khoa", ["nhikhoa", "nhi khoa", "socphanve", "sốc phản vệ", "anaphylaxis", "phản vệ ở trẻ"]),
    ("Phục hồi chức năng – Ngôn ngữ trị liệu", ["phatamphuam", "phát âm phụ âm", "âm ngữ trị liệu", "ngôn ngữ trị liệu", "loạn vận ngôn"]),
    ("Thuốc & An toàn thuốc", ["antoanthuoc", "an toàn thuốc", "orlistat", "mhra", " ema", "prac", "fda", "akI".lower()]),
    ("Hô hấp", ["copd", "hohap", "hô hấp", "asthma", "hen "]),
    ("Cơ xương khớp – Thấp khớp", ["viemkhopdangthap", "viêm khớp", "thấp khớp", "khớp", "arthritis", "gout", "gút"]),
    ("Nội tiết – Chuyển hóa", ["dtd", "đái tháo", "diabet", "noitiet", "nội tiết", "lipid", "statin", "loãng xương", "tuyến giáp"]),
    # Tâm thần kinh ĐẶT TRƯỚC "Thần kinh – Đột quỵ" để 'tamthankinh'/'tâm thần' không bị 'thankinh' bắt nhầm.
    ("Tâm thần kinh", ["tamthan", "tâm thần", "hướng tâm thần", "thuốc tâm thần", "chống trầm cảm", "trầm cảm", "chống loạn thần", "loạn thần", "an thần kinh", "giải lo âu", "ổn định khí sắc", "psych", "ssri", "snri", "antidepressant", "antipsychotic"]),
    ("Thần kinh – Đột quỵ", ["machmaunao", "mạch máu não", "dotquy", "đột quỵ", "dmcanh", "đm cảnh", "dongmachcanh", "động mạch cảnh", "tia ", "stroke", "thankinh", "thần kinh", "neuro", "động kinh", "sa sút trí tuệ", "daudau", "đau đầu", "nhức đầu", "migraine", "cluster headache", "đau nửa đầu"]),
    # Vá 2026-07-16: "Tiêu hóa – Gan mật" có trong SPECIALTIES nhưng chưa từng có luật
    # DASH_RULES nào — mọi dashboard gan mật trước đó rơi vào khoa khác do không khớp
    # luật nào (vd viemganb rơi vào "Thận – Tiết niệu" chỉ vì câu hỏi có chữ "CKD").
    # ĐẶT TRƯỚC "Thận – Tiết niệu" vì nhiều dashboard gan có đối tượng CKD/lọc máu kèm
    # theo (chữ "ckd" xuất hiện trong tiêu đề chung) nhưng chủ đề chính vẫn là gan mật.
    ("Tiêu hóa – Gan mật", ["viemganb", "viêm gan", "gan mật", "xơ gan", "hepatitis", "cirrhosis", "hepatic", "hbv", "hcv", "gan nhiễm mỡ", "viêm tụy", "loét dạ dày", "trào ngược dạ dày"]),
    # Vá 2026-08-05: "Huyết học" chưa từng có trong SPECIALTIES lẫn DASH_RULES — dashboard
    # huyết học đầu tiên (thiếu máu · đa hồng cầu) rơi vào "Thận – Tiết niệu" chỉ vì nội dung
    # có mục thiếu máu do CKD. CÙNG LỚP LỖI với "Tiêu hóa – Gan mật" đã vá 2026-07-16.
    # ĐẶT TRƯỚC "Thận – Tiết niệu" vì dashboard huyết học thường kèm mục CKD/lọc máu.
    # CỐ Ý KHÔNG dùng từ khóa "thiếu máu" trần: "thiếu máu cơ tim"/"thiếu máu não" sẽ bị
    # bắt nhầm khỏi Tim mạch/Thần kinh. Cũng KHÔNG dùng "anemia" trần để dashboard thiếu
    # máu do bệnh thận mạn thuần vẫn thuộc "Thận – Tiết niệu".
    ("Huyết học", ["huyethoc", "huyết học", "thiếu máu thiếu sắt", "thieumau_", "thiếu sắt",
                   "đa hồng cầu", "dahongcau", "polycythemia", "erythrocytosis", "thalassemia",
                   "hemoglobin", "huyết sắc tố", "truyền máu", "transfusion", "hồng cầu lưới",
                   "giảm tiểu cầu", "đông máu", "hemophilia", "lơ xê mi", "leukemia",
                   "u lympho", "lymphoma", "đa u tủy", "myeloma", "myeloproliferative",
                   "tân sinh tủy", "ferritin", "hepcidin"]),
    ("Thận – Tiết niệu", ["ckd", "benhthanman", "bệnh thận", "suy thận", "tiết niệu", "_than_", "than_2026"]),
    ("Tim mạch", ["timmach", "tim mạch", "suytim", "suy tim", "tienluongsuytim", "rung nhĩ", "tăng huyết áp", "tha ", "mạch vành"]),
    ("Lão khoa – Đa bệnh lý", ["laokhoa", "lão khoa", "deprescrib", "beers", "stopp", "start criteria", "cao tuổi", "người cao tuổi", "polypharmacy", "đa thuốc"]),
    ("Cấp cứu", ["capcuu", "cấp cứu", "banau", "ban đầu"]),
    ("Nhiễm khuẩn", ["nhiễm", "vaccine", "vắc", "kháng sinh", "viêm phổi", "sepsis", "cap_ats", "cap ats"]),
    ("Tổng hợp / Đa khoa", ["tuanthu", "tuân thủ", "adherence", "uptodate", "capnhattuan", "cập nhật tuần", "weekly"]),
]


def specialty_of_dashboard(filename: str, question: str) -> str:
    """Suy chuyên khoa của 1 dashboard từ tên file + câu hỏi."""
    hay = (filename + " " + (question or "")).lower()
    for spec, kws in DASH_RULES:
        for kw in kws:
            if kw and kw in hay:
                return spec
    return FALLBACK_SPEC


# ---- Làm sạch tên file thành tiêu đề người đọc --------------------------------
TOKEN_MAP = {
    "TimMach": "Tim mạch", "TienLuongSuyTim": "Tiên lượng suy tim",
    "BenhThanMan": "Bệnh thận mạn", "CKD": "(CKD)", "Than": "Thận",
    "BienChungThanKinh": "Biến chứng thần kinh", "DTD": "ĐTĐ",
    "MachMauNao": "Bệnh mạch máu não", "DongMachCanh": "Động mạch cảnh",
    "BenhDMCanh": "Bệnh ĐM cảnh", "DuPhongDotQuy": "Dự phòng đột quỵ",
    "ViemKhopDangThap": "Viêm khớp dạng thấp", "ViemDaDayThanKinh": "Viêm đa dây thần kinh",
    "COPD": "COPD", "HoHap": "Hô hấp", "CapCuuBanau": "Cấp cứu ban đầu",
    "TuanThuDieuTri": "Tuân thủ điều trị", "HopNhat": "(bản hợp nhất)",
    "AnToanThuoc": "An toàn thuốc", "Orlistat": "Orlistat", "AKI": "(AKI)",
    "CapNhatTuan": "Cập nhật tuần", "NgoaiTru": "ngoại trú",
    "PhatAmPhuAm": "Phát âm phụ âm",
    "HuyetHoc": "Huyết học", "ThieuMau": "Thiếu máu", "DaHongCau": "Đa hồng cầu",
}


def title_from_filename(fname: str) -> str:
    base = re.sub(r"\.html$", "", fname)
    base = base.replace("WebDashboard_EBM_", "").replace("VanDeCuThe_", "")
    base = re.sub(r"_?\d{8}$", "", base)  # bỏ ngày YYYYMMDD ở cuối
    parts = [p for p in base.split("_") if p]
    out = []
    for p in parts:
        out.append(TOKEN_MAP.get(p, p))
    return " ".join(out).strip() or fname


def date_from_filename(fname: str) -> str:
    m = re.search(r"(\d{4})(\d{2})(\d{2})", fname)
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


# ---- Đọc thang điểm lâm sàng ---------------------------------------------------
def load_scales():
    if not SCALES_JSON.exists():
        print(f"⚠️  Không thấy {SCALES_JSON} — bỏ qua phần thang điểm.", file=sys.stderr)
        return []
    # Vá 2026-07-11 (vòng 8): thiếu try/except (bất đối xứng với load_updates() ngay dưới) —
    # JSON hỏng/ghi dở (OneDrive sync) làm crash toàn bộ build_antifacts.py thay vì chỉ bỏ
    # qua phần thang điểm.
    try:
        data = json.loads(SCALES_JSON.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"⚠️  Lỗi đọc {SCALES_JSON}: {exc} — bỏ qua phần thang điểm.", file=sys.stderr)
        return []
    items = data.get("items", [])
    out = []
    for it in items:
        out.append({
            "name": it.get("name", "").strip(),
            "group": it.get("group", ""),
            "specialty": specialty_of_scale(it.get("group", "")),
            "evidence": it.get("evidence", ""),
            "situation": it.get("situation", ""),
            "purpose": it.get("purpose", ""),
            "tool_type": it.get("tool_type", ""),
            "population": it.get("population", ""),
            # LƯU Ý (vòng lặp kiểm tra-hoàn thiện vòng 4, 2026-07-21): trường "html" được
            # render THẲNG vào innerHTML ở Antifacts.html (showScaleTab/openScale), KHÔNG
            # qua escHtml()/sanitize — CHỦ Ý, vì đây là markup thật (bảng/danh sách tính
            # điểm) do người biên tập tự viết, không phải văn bản tự do từ nguồn ngoài.
            # Chấp nhận được MIỄN LÀ nguồn dữ liệu (clinical_scores_45.json) chỉ được sửa
            # bởi người biên tập nội bộ — KHÔNG copy-paste HTML chưa rà soát từ nguồn ngoài
            # vào trường này (không có lớp chặn kỹ thuật nào khác bảo vệ ở đây).
            "detail_html": it.get("html", ""),
        })
    return out


# ---- Đọc dashboard cập nhật ----------------------------------------------------
def load_updates():
    lib = {}
    if LIBRARY_JSON.exists():
        try:
            for e in json.loads(LIBRARY_JSON.read_text(encoding="utf-8")):
                lib[e.get("file")] = e
        except Exception as exc:  # noqa: BLE001
            print(f"⚠️  Lỗi đọc library.json: {exc}", file=sys.stderr)

    out = []
    if not DASH_DIR.exists():
        print(f"⚠️  Không thấy {DASH_DIR}", file=sys.stderr)
        return out

    for f in sorted(DASH_DIR.glob("WebDashboard_*.html")):
        fname = f.name
        meta = lib.get(fname, {})
        question = meta.get("question") or title_from_filename(fname)
        date = meta.get("updated") or date_from_filename(fname)
        out.append({
            "file": f"EBM-Dashboards/{fname}",
            "title": question,
            "eyebrow": meta.get("eyebrow", ""),
            "date": date,
            "specialty": specialty_of_dashboard(fname, question),
            "total": meta.get("total"),
            "apply": meta.get("apply"),
            "consider": meta.get("consider"),
            "notyet": meta.get("notyet"),
            "pmids": len(meta.get("pmids", [])) if meta.get("pmids") else None,
            "indexed": fname in lib,
        })
    # mới nhất lên đầu
    out.sort(key=lambda x: x["date"] or "", reverse=True)
    return out


# ---- Danh mục công cụ NGHIÊN CỨU (chuẩn, trỏ về agent đã có) -------------------
RESEARCH = [
    {"cat": "Thẩm định nguy cơ sai lệch (Risk of Bias)", "agent": "tham-dinh-phe-binh", "tools": [
        {"name": "RoB 2", "for": "RCT", "purpose": "Nguy cơ sai lệch trong thử nghiệm ngẫu nhiên (5 miền)"},
        {"name": "ROBINS-I", "for": "Can thiệp không ngẫu nhiên", "purpose": "Nguy cơ sai lệch ở nghiên cứu quan sát có can thiệp"},
        {"name": "QUADAS-2", "for": "Độ chính xác chẩn đoán", "purpose": "Nguy cơ sai lệch ở nghiên cứu xét nghiệm chẩn đoán"},
        {"name": "AMSTAR-2", "for": "Tổng quan hệ thống", "purpose": "Đánh giá chất lượng phương pháp của SR/MA"},
        {"name": "PROBAST", "for": "Mô hình dự báo", "purpose": "Nguy cơ sai lệch của mô hình tiên lượng/chẩn đoán"},
    ]},
    {"cat": "Phân hạng & lượng hóa chứng cứ", "agent": "tham-dinh-grade-nnt", "tools": [
        {"name": "GRADE", "for": "Mọi câu hỏi PICO", "purpose": "Phân hạng độ tin cậy (cao→rất thấp) + độ mạnh khuyến cáo"},
        {"name": "NNT / NNH", "for": "Điều trị / tác hại", "purpose": "Số cần điều trị để có 1 lợi ích / gây 1 tác hại"},
        {"name": "OR / RR / HR + 95% CI", "for": "Mọi thiết kế", "purpose": "Độ lớn hiệu quả kèm khoảng tin cậy"},
    ]},
    {"cat": "Chuẩn báo cáo (Reporting checklists)", "agent": "viet-ban-thao", "tools": [
        {"name": "CONSORT 2025", "for": "RCT", "purpose": "Chuẩn báo cáo thử nghiệm ngẫu nhiên"},
        {"name": "STROBE", "for": "Quan sát", "purpose": "Cohort / bệnh-chứng / cắt ngang"},
        {"name": "PRISMA 2020", "for": "SR / Meta-analysis", "purpose": "Chuẩn báo cáo tổng quan hệ thống"},
        {"name": "SPIRIT 2025", "for": "Đề cương thử nghiệm", "purpose": "Chuẩn nội dung protocol RCT"},
        {"name": "STARD", "for": "Chẩn đoán", "purpose": "Chuẩn báo cáo nghiên cứu độ chính xác chẩn đoán"},
        {"name": "TRIPOD+AI", "for": "Mô hình dự báo", "purpose": "Chuẩn báo cáo mô hình tiên lượng/AI"},
        {"name": "COREQ / SRQR", "for": "Định tính", "purpose": "Chuẩn báo cáo nghiên cứu định tính"},
        {"name": "SQUIRE", "for": "Cải tiến chất lượng", "purpose": "Chuẩn báo cáo nghiên cứu QI"},
    ]},
    {"cat": "Thiết kế · cỡ mẫu · đo lường · kinh tế", "agent": "co-mau-nghien-cuu", "tools": [
        {"name": "Cỡ mẫu / Power", "for": "Trước thu thập (G3)", "purpose": "Tính cỡ mẫu/lực theo thiết kế → agent co-mau-nghien-cuu"},
        {"name": "COSMIN", "for": "Công cụ đo lường / PROM", "purpose": "Kiểm định bộ câu hỏi/thang đo → agent cong-cu-do-luong"},
        {"name": "CHEERS 2022", "for": "Kinh tế y tế", "purpose": "Chuẩn báo cáo phân tích chi phí–hiệu quả → agent kinh-te-y-te"},
    ]},
]


def build_data():
    scales = load_scales()
    updates = load_updates()
    counts = {s: {"updates": 0, "scales": 0} for s in SPEC_NAMES}
    for u in updates:
        counts.setdefault(u["specialty"], {"updates": 0, "scales": 0})
        counts[u["specialty"]]["updates"] += 1
    for s in scales:
        counts.setdefault(s["specialty"], {"updates": 0, "scales": 0})
        counts[s["specialty"]]["scales"] += 1
    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "specialties": [{"name": n, "icon": i} for n, i in SPECIALTIES],
        "counts": counts,
        "updates": updates,
        "scales": scales,
        "research": RESEARCH,
        "totals": {
            "updates": len(updates),
            "scales": len(scales),
            "research": sum(len(c["tools"]) for c in RESEARCH),
        },
    }


# ============================ HTML (vỏ tĩnh) ===================================
HEAD = """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Antifacts — Trung tâm EBM theo chuyên khoa</title>
<style>
:root{
  --bg:#f5f7fb; --card:#ffffff; --ink:#0f172a; --muted:#64748b; --line:#e2e8f0;
  --brand:#4f46e5; --brand2:#0ea5e9; --ok:#16a34a; --warn:#d97706; --bad:#dc2626;
  --shadow:0 1px 2px rgba(15,23,42,.06),0 4px 14px rgba(15,23,42,.06);
}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans",sans-serif;
  background:var(--bg);color:var(--ink);line-height:1.5;-webkit-font-smoothing:antialiased}
a{color:var(--brand);text-decoration:none}
header.top{position:relative;background:linear-gradient(120deg,#312e81,#4f46e5 55%,#0ea5e9);color:#fff;padding:22px 20px 18px}
.hublink{position:absolute;top:18px;right:20px;display:inline-flex;align-items:center;gap:6px;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.32);color:#fff;font-weight:600;font-size:13px;padding:7px 13px;border-radius:9px;text-decoration:none;white-space:nowrap}
.hublink:hover{background:rgba(255,255,255,.27)}
@media(max-width:560px){.hublink{position:static;display:inline-flex;margin-top:10px}}
.wrap{max-width:1180px;margin:0 auto}
.brand{display:flex;align-items:center;gap:12px}
.brand .logo{font-size:30px}
.brand h1{margin:0;font-size:24px;letter-spacing:.3px}
.brand .sub{margin:2px 0 0;font-size:13px;opacity:.9}
.stats{display:flex;gap:10px;flex-wrap:wrap;margin-top:14px}
.stat{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.22);border-radius:10px;padding:7px 12px;font-size:13px}
.stat b{font-size:17px;margin-right:4px}
.toolbar{position:sticky;top:0;z-index:20;background:rgba(245,247,251,.92);backdrop-filter:blur(8px);
  border-bottom:1px solid var(--line);padding:10px 20px}
.toolbar .row{max-width:1180px;margin:0 auto;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.tabs{display:flex;gap:6px;flex-wrap:wrap}
.tab{border:1px solid var(--line);background:var(--card);color:var(--muted);border-radius:999px;
  padding:7px 14px;font-size:13.5px;cursor:pointer;font-weight:600}
.tab.active{background:var(--brand);color:#fff;border-color:var(--brand)}
.search{flex:1;min-width:200px;display:flex;align-items:center;gap:8px;background:var(--card);
  border:1px solid var(--line);border-radius:10px;padding:8px 12px}
.search input{border:0;outline:0;flex:1;font-size:14px;background:transparent;color:var(--ink)}
main{max-width:1180px;margin:18px auto 60px;padding:0 20px}
.spec{background:var(--card);border:1px solid var(--line);border-radius:14px;margin-bottom:14px;box-shadow:var(--shadow);overflow:hidden}
.spec>summary{list-style:none;cursor:pointer;padding:14px 18px;display:flex;align-items:center;gap:12px;user-select:none}
.spec>summary::-webkit-details-marker{display:none}
.spec .ic{font-size:22px}
.spec .nm{font-size:17px;font-weight:700;flex:1}
.spec .pill{font-size:12px;color:var(--muted);background:#f1f5f9;border:1px solid var(--line);border-radius:999px;padding:3px 9px}
.spec .chev{color:var(--muted);transition:transform .2s}
.spec[open] .chev{transform:rotate(90deg)}
.spec .body{padding:4px 18px 18px;border-top:1px solid var(--line)}
.sub-h{font-size:12.5px;font-weight:800;letter-spacing:.6px;text-transform:uppercase;color:var(--muted);margin:16px 0 8px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px}
.item{border:1px solid var(--line);border-radius:11px;padding:12px;background:#fff;transition:.15s;cursor:pointer}
.item:hover{border-color:var(--brand);box-shadow:var(--shadow);transform:translateY(-1px)}
.item .t{font-weight:650;font-size:14px;margin:0 0 4px}
.item .m{font-size:12px;color:var(--muted);display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.badge{font-size:11px;font-weight:700;border-radius:6px;padding:2px 7px;white-space:nowrap}
.b-ok{background:#dcfce7;color:#166534}.b-warn{background:#fef3c7;color:#92400e}.b-bad{background:#fee2e2;color:#991b1b}
.b-info{background:#e0e7ff;color:#3730a3}.b-gray{background:#f1f5f9;color:#475569}
.counts{display:flex;gap:6px;flex-wrap:wrap;margin-top:6px}
.empty{color:var(--muted);font-size:13px;font-style:italic;padding:6px 0}
.research-cat{margin:10px 0 4px;font-weight:700}
.research-cat .ag{font-size:12px;color:var(--brand);font-weight:600}
footer{max-width:1180px;margin:0 auto 40px;padding:18px 20px;color:var(--muted);font-size:12.5px;border-top:1px dashed var(--line)}
.disc{background:#fffbeb;border:1px solid #fde68a;color:#92400e;border-radius:10px;padding:10px 12px;margin:8px 0}
/* modal */
#modal{position:fixed;inset:0;background:rgba(15,23,42,.55);display:none;align-items:center;justify-content:center;z-index:50;padding:20px}
#modal.on{display:flex}
.sheet{background:#fff;max-width:1100px;width:100%;max-height:88vh;overflow:auto;border-radius:16px;padding:22px;box-shadow:0 20px 60px rgba(0,0,0,.3)}
.sheet h3{margin:0 0 2px;font-size:19px}
.sheet .gp{color:var(--muted);font-size:13px;margin-bottom:12px}
.sheet dl{margin:0}
.sheet dt{font-size:11.5px;font-weight:800;letter-spacing:.5px;text-transform:uppercase;color:var(--muted);margin-top:12px}
.sheet dd{margin:3px 0 0;font-size:14px}
.sheet .x{float:right;cursor:pointer;color:var(--muted);font-size:22px;line-height:1;border:0;background:0}
.sheet-tools{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0 10px}
.toolbtn{border:1px solid var(--line);background:#fff;color:var(--ink);border-radius:8px;padding:7px 11px;font-weight:700;font-size:13px;cursor:pointer}
.toolbtn.active{background:var(--brand);border-color:var(--brand);color:#fff}
.calcbox{border:1px solid #bfdbfe;background:#eff6ff;border-radius:12px;padding:12px;margin:12px 0}
.calcbox h4{margin:0 0 8px;font-size:15px}
.calcrow{display:grid;grid-template-columns:22px 1fr 72px;gap:8px;align-items:start;padding:7px 0;border-top:1px solid rgba(37,99,235,.14)}
.calcrow:first-of-type{border-top:0}
.calcrow label{font-size:13.5px}
.calcrow .pt{text-align:right;font-weight:800;color:#1d4ed8}
.calc-total{display:flex;gap:10px;align-items:center;flex-wrap:wrap;border-top:1px solid #bfdbfe;margin-top:10px;padding-top:10px}
.calc-total b{font-size:20px;color:#1d4ed8}
.calc-note{font-size:12.5px;color:var(--muted);margin-top:8px}
.scale-detail{border-top:1px solid var(--line);margin-top:14px;padding-top:12px}
.scale-detail .card-head{display:flex;justify-content:space-between;gap:12px;background:#f8fafc;border:1px solid var(--line);border-radius:12px;padding:12px;margin-bottom:10px}
.scale-detail .card-head h4{margin:0;font-size:18px}
.scale-detail .tags{display:flex;gap:6px;flex-wrap:wrap;margin:8px 0}
.scale-detail .tag,.scale-detail .evidence{font-size:11px;border-radius:999px;padding:3px 8px;background:#f1f5f9;color:#334155}
.scale-detail .card-body{padding:0}
.scale-detail .field{display:grid;grid-template-columns:180px 1fr;gap:12px;padding:8px 0;border-bottom:1px dashed var(--line)}
.scale-detail .label{font-size:11px;text-transform:uppercase;font-weight:800;color:var(--muted)}
.scale-detail .value{font-size:14px}
.scale-detail .tablewrap{overflow:auto;border:1px solid var(--line);border-radius:10px;margin:10px 0}
.scale-detail table{width:100%;border-collapse:collapse;font-size:13.5px}
.scale-detail th{background:#f1f5f9;color:#0f172a;text-align:left;padding:8px;border-bottom:1px solid var(--line)}
.scale-detail td{padding:8px;border-bottom:1px solid var(--line);vertical-align:top}
.scale-detail ul{margin:4px 0 4px 18px;padding:0}
.scale-detail h4{font-size:15px;margin:16px 0 8px}
.practice-actions{background:#eef6ff;border:1px solid #bfdbfe;border-radius:10px;padding:10px;margin:10px 0}
.warning-box{background:#fef2f2;border:1px solid #fecaca;border-left:5px solid #dc2626;border-radius:10px;padding:10px;margin:10px 0}
@media(max-width:560px){.brand h1{font-size:20px}.grid{grid-template-columns:1fr}}
</style>
</head>
<body>
"""

BODY_TAIL = """
<div id="modal" onclick="if(event.target.id==='modal')closeModal()">
  <div class="sheet" id="sheet"></div>
</div>
<footer>
  <div class="disc">⚠️ Mọi nội dung là HỖ TRỢ tra cứu — <b>Cần bác sĩ kiểm chứng</b>. Thang điểm/ngưỡng theo nguồn đã công nhận; chứng cứ kèm PMID/DOI trong từng dashboard. KHÔNG dùng cho thông tin định danh bệnh nhân (PII).</div>
  <div id="gen"></div>
  <div>Antifacts gom dữ liệu từ <code>EBM-Dashboards/</code> + <code>clinical_scores_45.json</code>. Cập nhật: chạy <code>python3 tools/build_antifacts.py</code> (KHÔNG sửa tay file HTML này).</div>
</footer>
<script>
function esc(s){return (s==null?'':String(s)).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function evBadge(e){e=(e||'').toLowerCase();if(e.startsWith('high'))return '<span class="badge b-ok">'+esc(e)+'</span>';
  if(e.startsWith('mod'))return '<span class="badge b-warn">'+esc(e)+'</span>';
  if(e.startsWith('low')||e.startsWith('very'))return '<span class="badge b-bad">'+esc(e)+'</span>';
  return e?'<span class="badge b-gray">'+esc(e)+'</span>':'';}
// Chuẩn hóa để tìm "thông minh": bỏ dấu tiếng Việt, đổi chỉ số dưới ₂→2, đ→d
function norm(s){return (s==null?'':String(s)).toLowerCase().normalize('NFD')
  .replace(/[̀-ͯ]/g,'')
  .replace(/[₀-₉]/g,c=>String(c.charCodeAt(0)-0x2080))
  .replace(/[⁰¹²³⁴-⁹]/g,c=>'⁰¹²³⁴⁵⁶⁷⁸⁹'.indexOf(c))
  .replace(/đ/g,'d');}
let view='specialty', q='';
function match(t){return !q || norm(t).includes(q);}

function updateCard(u){
  let c=[];
  if(u.apply!=null)c.push('<span class="badge b-ok">Áp dụng '+u.apply+'</span>');
  if(u.consider!=null)c.push('<span class="badge b-warn">Cân nhắc '+u.consider+'</span>');
  if(u.notyet!=null)c.push('<span class="badge b-gray">Chưa '+u.notyet+'</span>');
  if(u.pmids)c.push('<span class="badge b-info">'+u.pmids+' PMID</span>');
  return '<a class="item" href="'+esc(u.file)+'" target="_blank" rel="noopener">'
    +'<p class="t">'+esc(u.title)+'</p>'
    +'<div class="m">'+(u.date?('📅 '+esc(u.date)):'')+(u.total!=null?(' · '+u.total+' mục'):'')+'</div>'
    +(c.length?'<div class="counts">'+c.join('')+'</div>':'')+'</a>';
}
function scaleCard(s,i){
  return '<div class="item" onclick="openScale('+i+')">'
    +'<p class="t">'+esc(s.name)+'</p>'
    +'<div class="m">'+evBadge(s.evidence)+' <span>'+esc(s.tool_type||'')+'</span><span class="badge b-info">Xem/tính</span></div></div>';
}
function parsePoint(v){
  const raw=String(v||'').trim().replace(',', '.').replace('−','-');
  if(!raw)return null;
  if(/[–—]/.test(raw) && !/^-[0-9]/.test(raw))return null;
  const m=raw.match(/[-+]?[0-9]+(?:[.][0-9]+)?/);
  return m?Number(m[0]):null;
}
function findScoreTable(doc){
  const heads=[...doc.querySelectorAll('h4,h5')];
  for(const h of heads){
    const ht=norm(h.textContent);
    if(ht.includes('bang cham diem') || ht.includes('cach tinh')){
      let n=h.nextElementSibling;
      while(n && n.tagName!=='TABLE' && !n.querySelector?.('table'))n=n.nextElementSibling;
      const t=n?.tagName==='TABLE'?n:n?.querySelector?.('table');
      if(t)return t;
    }
  }
  return [...doc.querySelectorAll('table')].find(t=>t.querySelector('.score-col')) || null;
}
function extractCalcRows(html){
  if(!html)return [];
  const doc=new DOMParser().parseFromString('<div>'+html+'</div>','text/html');
  const table=findScoreTable(doc);
  if(!table)return [];
  const rows=[];
  table.querySelectorAll('tbody tr').forEach((tr,idx)=>{
    const cells=[...tr.children].map(td=>td.textContent.trim()).filter(Boolean);
    if(cells.length<2)return;
    const scoreCell=tr.querySelector('.score-col');
    const scoreText=scoreCell?scoreCell.textContent.trim():cells[cells.length-1];
    const pts=parsePoint(scoreText);
    if(pts===null)return;
    let label=cells.filter(c=>c!==scoreText).join(' — ');
    if(!label)label=cells[0];
    rows.push({id:'c'+idx,label,pts,scoreText});
  });
  return rows;
}
function findDecisionRows(html){
  if(!html)return [];
  const doc=new DOMParser().parseFromString('<div>'+html+'</div>','text/html');
  const heads=[...doc.querySelectorAll('h4,h5')];
  for(const h of heads){
    const tx=norm(h.textContent);
    if(tx.includes('dien giai') || tx.includes('quyet dinh')){
      let n=h.nextElementSibling;
      while(n && n.tagName!=='TABLE' && !n.querySelector?.('table'))n=n.nextElementSibling;
      const t=n?.tagName==='TABLE'?n:n?.querySelector?.('table');
      if(t)return [...t.querySelectorAll('tbody tr')].map(tr=>[...tr.children].map(td=>td.textContent.trim()));
    }
  }
  return [];
}
function conditionMatches(txt,total){
  const s=String(txt||'').replace(',', '.').replace('−','-').replace(/\\s+/g,' ');
  let m=s.match(/(?:≤|<=|=<)\\s*(-?[0-9]+(?:[.][0-9]+)?)/); if(m)return total<=Number(m[1]);
  m=s.match(/(?:≥|>=|=>)\\s*(-?[0-9]+(?:[.][0-9]+)?)/); if(m)return total>=Number(m[1]);
  m=s.match(/>\\s*(-?[0-9]+(?:[.][0-9]+)?)/); if(m)return total>Number(m[1]);
  m=s.match(/<\\s*(-?[0-9]+(?:[.][0-9]+)?)/); if(m)return total<Number(m[1]);
  m=s.match(/(-?[0-9]+(?:[.][0-9]+)?)\\s*[–-]\\s*(-?[0-9]+(?:[.][0-9]+)?)/);
  if(m)return total>=Number(m[1]) && total<=Number(m[2]);
  m=s.match(/^(-?[0-9]+(?:[.][0-9]+)?)$/); if(m)return total===Number(m[1]);
  return false;
}
function interpretTotal(s,total){
  const rows=findDecisionRows(s.detail_html||'');
  for(const r of rows){
    if(r.some(c=>conditionMatches(c,total)))return r.join(' — ');
  }
  return 'Đối chiếu tổng điểm với bảng diễn giải/decision bên dưới trước khi quyết định.';
}
function renderCalc(s){
  const rows=extractCalcRows(s.detail_html||'');
  if(!rows.length){
    return '<div class="calcbox"><h4>Máy tính</h4><div class="calc-note">Thang này dùng công thức/phân loại phức tạp hoặc bảng không ở dạng cộng điểm đơn giản. Xem phần chi tiết bên dưới và dùng calculator chính thống khi cần.</div></div>';
  }
  return '<div class="calcbox"><h4>Tính điểm nhanh</h4>'
    +rows.map(r=>'<div class="calcrow"><input type="checkbox" data-pt="'+r.pts+'" onchange="recalcScale()">'
      +'<label>'+esc(r.label)+'</label><div class="pt">'+esc(r.scoreText)+'</div></div>').join('')
    +'<div class="calc-total"><span>Tổng điểm</span><b id="calcTotal">0</b><span id="calcInterp">Chọn tiêu chí để tính.</span></div>'
    +'<div class="calc-note">Công cụ tính nhanh chỉ hỗ trợ bảng cộng điểm. Cần bác sĩ kiểm chứng và đối chiếu đúng đối tượng áp dụng.</div></div>';
}
function recalcScale(){
  const s=DATA.scales[window.currentScaleIndex];
  let total=0;
  document.querySelectorAll('#sheet input[data-pt]:checked').forEach(x=>{total+=Number(x.dataset.pt||0);});
  const t=document.getElementById('calcTotal'), it=document.getElementById('calcInterp');
  if(t)t.textContent=Number.isInteger(total)?String(total):String(total.toFixed(1));
  if(it)it.textContent=interpretTotal(s,total);
}
function renderScaleSummary(s){
  return '<dl>'
    +(s.purpose?'<dt>Mục đích</dt><dd>'+esc(s.purpose)+'</dd>':'')
    +(s.situation?'<dt>Tình huống dùng</dt><dd>'+esc(s.situation)+'</dd>':'')
    +(s.population?'<dt>Dân số áp dụng</dt><dd>'+esc(s.population)+'</dd>':'')
    +(s.tool_type?'<dt>Loại công cụ</dt><dd>'+esc(s.tool_type)+'</dd>':'')
    +'</dl>';
}
function showScaleTab(which){
  const s=DATA.scales[window.currentScaleIndex];
  document.querySelectorAll('.sheet-tools .toolbtn').forEach(b=>b.classList.remove('active'));
  document.querySelector('[data-scale-tab="'+which+'"]')?.classList.add('active');
  const box=document.getElementById('scaleContent');
  if(which==='summary'){
    box.innerHTML=renderScaleSummary(s)
      +'<div class="disc" style="margin-top:14px">Cần bác sĩ kiểm chứng — dùng đúng dân số đã kiểm định, không suy diễn ngoài chỉ định.</div>';
  }else{
    box.innerHTML=renderCalc(s)+'<div class="scale-detail">'+(s.detail_html||'<div class="empty">Chưa có bản chi tiết.</div>')+'</div>';
  }
}
function openScale(i){
  const s=DATA.scales[i];
  window.currentScaleIndex=i;
  document.getElementById('sheet').innerHTML=
    '<button class="x" onclick="closeModal()">×</button>'
    +'<h3>'+esc(s.name)+'</h3><div class="gp">'+esc(s.group)+' · '+evBadge(s.evidence)+'</div>'
    +'<div class="sheet-tools"><button class="toolbtn" data-scale-tab="summary" onclick="showScaleTab(\\'summary\\')">Tóm tắt</button>'
    +'<button class="toolbtn active" data-scale-tab="detail" onclick="showScaleTab(\\'detail\\')">Chi tiết + tính điểm</button></div>'
    +'<div id="scaleContent">'+renderCalc(s)+'<div class="scale-detail">'
    +(s.detail_html||'<div class="empty">Chưa có bản chi tiết.</div>')+'</div></div>';
  document.getElementById('modal').classList.add('on');
}
function closeModal(){document.getElementById('modal').classList.remove('on');}
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeModal();});

function bySpec(arr,sp){return arr.map((x,i)=>({x,i})).filter(o=>o.x.specialty===sp);}

function renderSpecialty(){
  let html='';
  DATA.specialties.forEach((sp,si)=>{
    const ups=bySpec(DATA.updates,sp.name).filter(o=>match(o.x.title));
    const scs=bySpec(DATA.scales,sp.name).filter(o=>match(o.x.name+' '+o.x.purpose+' '+o.x.tool_type));
    if(q && !ups.length && !scs.length) return;
    const open=(si===0 && !q)|| (q && (ups.length||scs.length));
    html+='<details class="spec"'+(open?' open':'')+'>'
      +'<summary><span class="ic">'+sp.icon+'</span><span class="nm">'+esc(sp.name)+'</span>'
      +'<span class="pill">'+ups.length+' cập nhật · '+scs.length+' thang điểm</span><span class="chev">▶</span></summary>'
      +'<div class="body">';
    html+='<div class="sub-h">📋 Cập nhật chứng cứ</div>';
    html+= ups.length?('<div class="grid">'+ups.map(o=>updateCard(o.x)).join('')+'</div>')
                     :'<div class="empty">Chưa có cập nhật cho chuyên khoa này.</div>';
    html+='<div class="sub-h">🧮 Thang điểm lâm sàng</div>';
    html+= scs.length?('<div class="grid">'+scs.map(o=>scaleCard(o.x,o.i)).join('')+'</div>')
                     :'<div class="empty">Chưa có thang điểm cho chuyên khoa này.</div>';
    html+='</div></details>';
  });
  return html||'<div class="empty">Không có kết quả khớp "'+esc(q)+'".</div>';
}
function renderUpdates(){
  const u=DATA.updates.filter(x=>match(x.title));
  if(!u.length)return '<div class="empty">Không có cập nhật khớp.</div>';
  return '<div class="grid">'+u.map(updateCard).join('')+'</div>';
}
function renderScales(){
  let html='';
  DATA.specialties.forEach(sp=>{
    const scs=bySpec(DATA.scales,sp.name).filter(o=>match(o.x.name+' '+o.x.purpose+' '+o.x.tool_type));
    if(!scs.length)return;
    html+='<div class="sub-h">'+sp.icon+' '+esc(sp.name)+'</div><div class="grid">'
      +scs.map(o=>scaleCard(o.x,o.i)).join('')+'</div>';
  });
  return html||'<div class="empty">Không có thang điểm khớp.</div>';
}
function renderResearch(){
  let html='<p style="color:var(--muted);font-size:13px;margin:4px 0 14px">Công cụ chuẩn cho nghiên cứu y khoa — mỗi mục trỏ về agent/skill xử lý tương ứng. Đây là chỉ mục tra nhanh, KHÔNG thay thao tác thẩm định đầy đủ.</p>';
  DATA.research.forEach(c=>{
    const tools=c.tools.filter(t=>match(t.name+' '+t.for+' '+t.purpose));
    if(!tools.length)return;
    html+='<div class="research-cat">'+esc(c.cat)+' <span class="ag">→ agent '+esc(c.agent)+'</span></div>';
    html+='<div class="grid">'+tools.map(t=>
      '<div class="item" style="cursor:default">'
      +'<p class="t">'+esc(t.name)+' <span class="badge b-info">'+esc(t.for)+'</span></p>'
      +'<div class="m">'+esc(t.purpose)+'</div></div>').join('')+'</div>';
  });
  return html;
}
function render(){
  const m=document.getElementById('app');
  if(view==='specialty')m.innerHTML=renderSpecialty();
  else if(view==='updates')m.innerHTML=renderUpdates();
  else if(view==='scales')m.innerHTML=renderScales();
  else m.innerHTML=renderResearch();
}
function setView(v,el){view=v;document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));el.classList.add('active');render();}
function onSearch(v){q=norm(v).trim();render();}
document.getElementById('gen').textContent='Sinh tự động lúc '+DATA.generated_at+' · '+DATA.totals.updates+' cập nhật · '+DATA.totals.scales+' thang điểm lâm sàng · '+DATA.totals.research+' công cụ nghiên cứu.';
render();
</script>
</body>
</html>
"""


def render_header(data):
    t = data["totals"]
    nspec = sum(1 for s in SPEC_NAMES if data["counts"].get(s, {}).get("updates") or data["counts"].get(s, {}).get("scales"))
    return (
        '<header class="top">'
        '<a class="hublink" href="EBM_MASTER/EBM_WEBAPP.html" title="Về hub EBM trung tâm — Clinical Quick View (sổ cái)">↩ Hub EBM</a>'
        '<div class="wrap">'
        '<div class="brand"><span class="logo">🛡️</span><div>'
        '<h1>Antifacts</h1>'
        '<p class="sub">Trung tâm EBM theo chuyên khoa — cập nhật chứng cứ &amp; thang điểm tra nhanh</p>'
        '</div></div>'
        '<div class="stats">'
        f'<span class="stat"><b>{t["updates"]}</b>cập nhật chứng cứ</span>'
        f'<span class="stat"><b>{t["scales"]}</b>thang điểm lâm sàng</span>'
        f'<span class="stat"><b>{t["research"]}</b>công cụ nghiên cứu</span>'
        f'<span class="stat"><b>{nspec}</b>chuyên khoa</span>'
        '</div></div></header>'
        '<div class="toolbar"><div class="row">'
        '<div class="tabs">'
        '<button class="tab active" onclick="setView(\'specialty\',this)">🗂️ Theo chuyên khoa</button>'
        '<button class="tab" onclick="setView(\'updates\',this)">📋 Cập nhật</button>'
        '<button class="tab" onclick="setView(\'scales\',this)">🧮 Thang điểm</button>'
        '<button class="tab" onclick="setView(\'research\',this)">🔬 Nghiên cứu</button>'
        '</div>'
        '<div class="search">🔎<input type="text" placeholder="Tìm nhanh: tên thang điểm, chủ đề, chuyên khoa…" oninput="onSearch(this.value)"></div>'
        '</div></div>'
        '<main id="app"></main>'
    )


def main():
    configure_utf8_stdio()
    data = build_data()
    data_js = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = HEAD + render_header(data) + "<script>const DATA=" + data_js + ";</script>" + BODY_TAIL
    OUT_HTML.write_text(html, encoding="utf-8")

    # ---- Báo cáo ----
    print(f"✅ Đã sinh: {OUT_HTML}")
    print(f"   {data['totals']['updates']} cập nhật · {data['totals']['scales']} thang điểm · {data['totals']['research']} công cụ NC")
    print("   Phân bổ theo chuyên khoa (cập nhật / thang điểm):")
    for s in SPEC_NAMES:
        c = data["counts"].get(s, {})
        u, k = c.get("updates", 0), c.get("scales", 0)
        if u or k:
            print(f"     {s:30s}  {u:2d} / {k:2d}")
    # cảnh báo dashboard rơi vào 'Tổng hợp' (có thể cần map lại)
    misc = [u["title"] for u in data["updates"] if u["specialty"] == FALLBACK_SPEC]
    if misc:
        print("   ⚠️  Vào 'Tổng hợp / Đa khoa' (rà lại DASH_RULES nếu cần):")
        for m in misc:
            print(f"        - {m}")


if __name__ == "__main__":
    main()
