#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CHỐT HỒI QUY BÀI HỌC — canh những lỗi ĐÃ TỪNG xảy ra thật, không cho quay lại.

VÌ SAO CÓ (13/08/2026)
======================
Hệ này phát hiện được trôi dạt MÁY MÓC (skill lệch bản, kho plugin thiếu, cấu
hình sai interpreter). Nhưng mọi khiếm khuyết NGHIÊM TRỌNG của tháng vừa rồi đều
do người tìm ra bằng tay, không chốt nào bắt được:

  • lệnh `return` sớm che 73 mục 'Áp dụng ngay' trên chứng cứ yếu (12/08)
  • parser `field()` cắt nhầm giá trị có dấu nháy kép bên trong (12/08)
  • `os.getuid()` làm chết công cụ trên Windows, hook nuốt lỗi im lặng (12/08)
  • `.env` là symlink → Windows chạy DỮ LIỆU GIẢ suốt nhiều tháng (12/08)
  • `unresolved` gộp chung "PubMed không có bài" với "đọc XML lỗi" → 18 báo động giả (12/08)
  • skill sửa ở nguồn KHÔNG tới nơi chạy, 20/22 bản lệch (13/08)

Đó là một vòng học HỞ: sửa xong thì bài học nằm trong tài liệu, không nằm trong
máy. Lần sau ai đó refactor là lỗi quay lại y nguyên, và vẫn im lặng như cũ.

File này đóng vòng đó. Mỗi mục dưới đây là MỘT lỗi có thật, có ngày, được kiểm
bằng cách gọi vào MÃ ĐANG SỐNG — không phải mock, không phải đọc chuỗi tài liệu.

NGUYÊN TẮC KHI THÊM MỤC
========================
1. Chỉ thêm lỗi ĐÃ XẢY RA THẬT. Đây không phải nơi phòng xa cho lỗi tưởng tượng —
   một chốt chưa từng bảo vệ điều gì chỉ làm loãng tín hiệu.
2. Phải kiểm HÀNH VI, không kiểm sự có mặt của câu chữ. Đếm chuỗi trong file là
   đúng cái bẫy TAUTOLOGY đã gặp ở guardrail G3/G8: luật tự đúng, không bao giờ đỏ.
3. Phải chạy NHANH và NGOẠI TUYẾN — nó chạy mỗi phiên.

Dùng:
    python3 tools/chot_hoi_quy_bai_hoc.py             # chạy hết, in bảng
    python3 tools/chot_hoi_quy_bai_hoc.py --im-khi-on  # chỉ nói khi có mục ĐỎ

Mã thoát: 0 = mọi bài học còn được canh · 1 = có bài học TÁI PHÁT.
"""
from __future__ import annotations

import argparse
import importlib.util
import inspect
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]
DASH = REPO / "EBM-Dashboards"


def _nap(duong_dan: Path, ten: str):
    spec = importlib.util.spec_from_file_location(ten, duong_dan)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------------------
# Mỗi hàm trả (đạt, chi_tiết). Ném ngoại lệ = coi như KHÔNG đạt (chốt phải nói
# ra khi chính nó hỏng, thay vì im lặng trả xanh).
# ---------------------------------------------------------------------------

FIXTURE = """const DATA = {
  meta:{topic:'fixture'},
  items:[
    {id:'ITEM-01', title:'fixture', design:'Cohort', gradeLevel:'na',
     gradeSource:'"Usually Not Appropriate" — phân loại chính thức của ACR',
     decision:'apply', pmid:'12345678'}
  ]
};"""


def bh01_khong_return_som():
    """12/08 — `return` sớm khi thiếu DATA.standards che MỌI luật cấp item.

    Triệu chứng đã đo: 47/52 dashboard báo đúng '1 lỗi cứng', và câu kết luận
    'nội dung lâm sàng không sai' được viết ra dựa trên đó — trong khi cổng chưa
    hề đọc tới một item nào. Bỏ `return` xong đo lại: 73 mục nguy hiểm trên 16
    dashboard, trước đó chỉ thấy 4.
    """
    vd = _nap(DASH / "tools/verify_dashboard.py", "vd_hoiquy")
    items = vd.split_items(FIXTURE)
    errs, warns, _ = vd.strict_source_checks(FIXTURE, items)
    thieu_std = any("standards" in x for x in errs + warns)
    co_loi_item = any("ITEM-01" in e and "apply" in e for e in errs)
    if not thieu_std:
        return False, "không còn nhận ra việc thiếu DATA.standards"
    if not co_loi_item:
        return False, ("THIẾU DATA.standards đang CHE luật cấp item — "
                       "đúng lỗi 12/08 đã che 73 mục")
    return True, "thiếu standards vẫn chạy tiếp tới luật item"


def bh02_parser_giu_nguyen_nhay_kep():
    """12/08 — `field()` dùng lớp ký tự `[^'\"]*` nên DỪNG ở dấu nháy loại kia.

    Giá trị `gradeSource:'"Usually Not Appropriate" — ACR'` bị đọc thành RỖNG,
    cổng báo 'thiếu gradeSource' cho item có đủ dữ liệu. Cổng nói SAI về dữ liệu
    ĐÚNG còn nguy hiểm hơn cổng không chạy, vì nó tạo niềm tin sai.
    """
    vd = _nap(DASH / "tools/verify_dashboard.py", "vd_hoiquy2")
    ch = vd.split_items(FIXTURE)[0]
    gs = vd.field(ch, "gradeSource") or ""
    if "Usually Not Appropriate" not in gs:
        return False, f"parser cắt mất giá trị có nháy kép, đọc ra {gs!r}"
    return True, "đọc đúng giá trị chứa dấu nháy kép"


def bh03_quy_pham_khong_nhan_consensus():
    """12/08 — miễn trừ quy phạm phải TỪ CHỐI `design='Consensus'`.

    Nếu nhận, chỉ cần gõ 'Consensus' là một văn bản đồng thuận đi qua cổng như
    nhãn thuốc FDA. Đây là đường lách đã được đo và cố ý bịt.
    """
    vd = _nap(DASH / "tools/verify_dashboard.py", "vd_hoiquy3")
    duoc, _ = vd.normative_exemption("Consensus", "na", "guideline-strong-rec", "nguồn X")
    if duoc:
        return False, "Consensus được miễn như nguồn quy phạm — đường lách đã mở lại"
    duoc2, _ = vd.normative_exemption("Guideline", "na", "drug-label", "Boxed Warning")
    if not duoc2:
        return False, "Guideline + drug-label hợp lệ lại KHÔNG được miễn (chặn oan)"
    return True, "Consensus bị từ chối; Guideline+drug-label được miễn"


def bh04_quy_pham_khong_cuu_nguon_tu_cham_thap():
    """12/08 — nguồn ĐÃ tự phân hạng 'low'/'vlow' thì không được viện cớ quy phạm."""
    vd = _nap(DASH / "tools/verify_dashboard.py", "vd_hoiquy4")
    for muc in ("low", "vlow"):
        duoc, _ = vd.normative_exemption("Guideline", muc, "drug-label", "x")
        if duoc:
            return False, f"gradeLevel={muc!r} vẫn được miễn — nguồn tự chấm yếu bị bỏ qua"
    return True, "low/vlow không được miễn"


def bh05_cong_cu_chung_song_duoc_tren_windows():
    """12/08 — `os.getuid()` không có trên Windows; hook `; true` nuốt lỗi IM LẶNG.

    Máy Windows vì thế chưa từng được nhắc độ tươi chứng cứ lần nào. Kiểm bằng
    cách GỌI THẬT hàm, xác nhận nó không ném ngoại lệ.
    """
    m = _nap(REPO / "tools/kiem_do_tuoi_chung_cu.py", "dotuoi_hoiquy")
    try:
        m.launchd_runs("com.medicalebm.weeklysafety")
    except Exception as e:  # noqa: BLE001 — đúng điều cần bắt
        return False, f"ném ngoại lệ thay vì trả None: {type(e).__name__}: {e}"
    src = inspect.getsource(m.launchd_runs)
    if "except Exception" not in src:
        return False, "bắt ngoại lệ quá hẹp — lỗi lạ vẫn làm chết công cụ"
    return True, "chạy an toàn trên mọi nền, bắt ngoại lệ rộng"


def bh06_khong_duong_dan_cung_cua_mot_may():
    """12/08 — `ensure_strict_source.py` ghi cứng `C:/Users/Admin/...` → gãy trên Mac.

    Cùng lớp lỗi với `docx_sang_pdf_giu_mau.py` chỉ dò trình duyệt theo đường dẫn
    macOS. Bài học: 'chạy được ở máy này' không suy ra 'chạy được ở máy kia'.
    """
    xau = re.compile(r"""["'](?:[A-Za-z]:[\\/]Users[\\/]|/Users/(?!nguyenluan/\.)[A-Za-z])""")
    pham: list[str] = []
    for f in sorted((REPO / "tools").glob("*.py")):
        t = f.read_text(encoding="utf-8", errors="replace")
        for k, dong in enumerate(t.splitlines(), 1):
            s = dong.strip()
            if s.startswith("#") or s.startswith('"""') or s.startswith("*"):
                continue
            if xau.search(dong):
                pham.append(f"{f.name}:{k}")
    if pham:
        return False, "đường dẫn cứng của một máy: " + ", ".join(pham[:4])
    return True, f"{len(list((REPO / 'tools').glob('*.py')))} công cụ, 0 đường dẫn cứng"


def bh07_doc_secrets_ngoai_onedrive():
    """12/08 — `.env` là symlink Unix; OneDrive biến nó thành file text 57 byte trên
    Windows ⇒ `USE_MOCK_SOURCES` rơi về mặc định True ⇒ MỌI lời gọi nguồn y văn
    trả DỮ LIỆU BỊA, cảnh báo duy nhất là một dòng `logger.info`.

    Đây là phát hiện nghiêm trọng nhất ngày 12/08. Chốt canh: `app/config.py`
    phải đọc kho secrets NGOÀI OneDrive trước `.env` trong repo.
    """
    t = (REPO / "medical-ebm-automation/app/config.py").read_text(encoding="utf-8",
                                                                 errors="replace")
    if ".ebm-secrets" not in t:
        return False, "config.py không còn đọc ~/.ebm-secrets — Windows sẽ chạy dữ liệu giả"
    i_sec, i_env = t.find(".ebm-secrets"), t.find('load_dotenv(".env"')
    if i_env != -1 and i_sec > i_env:
        return False, "đọc .env repo TRƯỚC kho secrets — sai thứ tự ưu tiên"
    return True, "kho secrets ngoài OneDrive được đọc trước"


def bh08_khong_gop_khong_biet_voi_co_van_de():
    """12/08 — `unresolved` từng gộp 'PubMed không có bài' (nghi trích dẫn MA) với
    'đọc XML lỗi' (chỉ là KHÔNG BIẾT) ⇒ 18 PMID vừa được PubMed xác minh có thật
    bị báo là trích dẫn ma. Báo động giả tệ hơn không kiểm: nó giết niềm tin vào
    cảnh báo thật.
    """
    t = (REPO / "medical-ebm-automation/app/sources/pubmed.py").read_text(
        encoding="utf-8", errors="replace")
    if "unknown_fetch_error" not in t:
        return False, "mất trạng thái 'unknown_fetch_error' — lại gộp KHÔNG BIẾT với CÓ VẤN ĐỀ"
    if "Blocked Diagnostic" not in t:
        return False, "không còn nhận diện trang chặn IP của NCBI"
    return True, "tách rõ 'không biết' khỏi 'nghi trích dẫn ma'"


def bh09_skill_toi_duoc_noi_chay():
    """13/08 — `sync/skills/` KHÔNG có cơ chế tự đẩy tới nơi Claude thật sự chạy;
    20/22 skill lệch, `cap-nhat-chung-cu-y-khoa` chạy v1.12.0 trong khi nguồn đã
    v1.15.0. Bác sĩ gọi skill và nhận HÀNH VI CŨ trong khi tài liệu nói bản mới.
    """
    m = _nap(REPO / "tools/dong_bo_skill.py", "dbskill_hoiquy")
    rt = m.tim_runtime()
    if rt is None:
        return True, "chưa có thư mục skill runtime trên máy này — bỏ qua"
    lech = [d.name for d in sorted(m.NGUON.iterdir())
            if d.is_dir() and (d / "SKILL.md").exists() and (rt / d.name).is_dir()
            and m.so_mot_skill(d, rt / d.name)["trang_thai"] != "KHOP"]
    if lech:
        return False, f"{len(lech)} skill đang chạy bản khác nguồn: {', '.join(lech[:3])}"
    return True, "mọi skill đang chạy khớp nguồn"


def bh10_ba_viec_cam_van_bi_cam():
    """Ranh giới an toàn do chính bác sĩ đặt (Cổng A/B): máy KHÔNG được tự đổi
    `decision`, tự đổi `gradeLevel`, hay tự phân xử khi hai bản mâu thuẫn.

    Bằng chứng vì sao ranh giới này phải được CANH chứ không chỉ ghi trong tài
    liệu: ngày 13/08 chính bộ phân loại vừa viết xong đã xếp cảnh báo hộp đen FDA
    về JAK inhibitor và chống chỉ định leflunomide vào nhóm 'chứng cứ yếu nên hạ'.
    Nếu lớp đó có quyền ghi, nó đã hạ hai cảnh báo an toàn.
    """
    ghi = re.compile(r"""(write_text|sub|replace)\s*\([^)]{0,120}?(decision|gradeLevel)\s*:""")
    pham: list[str] = []
    for f in sorted((REPO / "tools").glob("*.py")):
        t = f.read_text(encoding="utf-8", errors="replace")
        if ghi.search(t):
            pham.append(f.name)
    if pham:
        return False, ("có công cụ ghi decision/gradeLevel vào dashboard: "
                       + ", ".join(pham))
    return True, "không công cụ nào tự ghi decision/gradeLevel"


def bh11_tool_skill_ba_ban_khop_va_co_va_utf8():
    """13/08 — 4 tool của skill `cap-nhat-chung-cu-y-khoa` tồn tại ở BA nơi, và bản
    ở `EBM-Dashboards/tools` (runtime) đi trước nguồn 11 dòng.

    11 dòng đó là **bản vá UTF-8 cho Windows**: stdout mặc định cp1252 làm mọi
    `print()` tiếng Việt ném UnicodeEncodeError và GIẾT tiến trình — thường SAU KHI
    công việc đã xong (đo 12/08: bản Word 82 KB đã ghi ra đĩa nhưng tool thoát mã 1
    ở đúng dòng print cuối ⇒ caller tưởng hỏng, bỏ luôn 2 bước sau).

    NGUY HIỂM CỦA VIỆC "ĐỒNG BỘ" MÙ: nguồn có 0 dòng riêng, runtime có 11 — đẩy
    nguồn→runtime theo phản xạ sẽ XOÁ bản vá khỏi cả 4 tool và tái sinh đúng lỗi cũ.
    Chiều đúng phải quyết theo NỘI DUNG (bên nào bao trùm), không theo mtime, cũng
    không theo "nguồn thì luôn thắng runtime".

    Chốt này canh HAI điều: ba bản khớp md5, VÀ cả ba đều còn bản vá UTF-8.
    """
    import hashlib
    TEN = ["build_library", "dashboard_content_audit", "drug_safety_scan", "make_derivatives"]
    NOI = ["EBM-Dashboards/tools/{}.py",
           "sync/skills/cap-nhat-chung-cu-y-khoa/tools/{}.py",
           "EBM_MASTER/skill_assets/{}.py"]
    lech, mat_va = [], []
    for t in TEN:
        ps = [REPO / n.format(t) for n in NOI]
        co = [p for p in ps if p.exists()]
        if len(co) < 2:
            continue
        if len({hashlib.md5(p.read_bytes()).hexdigest() for p in co}) != 1:
            lech.append(t)
        for p in co:
            if "reconfigure(encoding=" not in p.read_text(encoding="utf-8", errors="replace"):
                mat_va.append(f"{p.parent.name}/{t}")
    if lech:
        return False, "3 bản lệch nhau: " + ", ".join(lech)
    if mat_va:
        return False, ("MẤT bản vá UTF-8 (sẽ chết giữa chừng trên Windows): "
                       + ", ".join(mat_va[:4]))
    return True, f"{len(TEN)} tool × 3 nơi khớp md5, đều còn bản vá UTF-8"


def bh12_quet_nguon_giu_tien_do_va_hien_tien_do():
    """13/08 — vòng quét xác minh nguồn chạy 12 phút mà log 0 byte và sổ không đổi.

    HAI lỗi im lặng chồng nhau:
      • `ghi_so()` chỉ gọi SAU khi hết một vòng. Mạng chậm (NCBI đang chặn máy này)
        làm một vòng ~180 mục kéo rất dài ⇒ đóng phiên / máy ngủ / Ctrl-C là MẤT
        TRẮNG mọi bằng chứng vừa thu, dù từng mục đã xác minh thành công.
      • stdout bị đệm theo KHỐI khi chuyển hướng ra file ⇒ không một dòng tiến độ.
    Cộng lại: một lượt quét ĐANG CHẠY ĐÚNG trông y hệt như treo, nên dễ bị giết nhầm.

    Kiểm bằng AST — cấu trúc chương trình, không đếm chuỗi: `ghi_so` phải được gọi
    BÊN TRONG vòng lặp từng mục (for lồng trong for), và stdout phải bật line_buffering.
    """
    import ast
    p = REPO / "tools/so_xac_minh_nguon.py"
    cay = ast.parse(p.read_text(encoding="utf-8"))

    def goi_trong(node) -> bool:
        return any(isinstance(x, ast.Call) and getattr(x.func, "id", "") == "ghi_so"
                   for x in ast.walk(node))

    trong_vong_lap_con = False
    for ngoai in ast.walk(cay):
        if not isinstance(ngoai, ast.For):
            continue
        for trong in ast.walk(ngoai):
            if trong is not ngoai and isinstance(trong, ast.For) and goi_trong(trong):
                trong_vong_lap_con = True
    if not trong_vong_lap_con:
        return False, ("ghi_so() không còn nằm trong vòng lặp từng mục — "
                       "mất trắng tiến độ nếu bị ngắt giữa chừng")
    if "line_buffering=True" not in p.read_text(encoding="utf-8"):
        return False, "stdout không bật line_buffering — chạy nền sẽ không thấy tiến độ"
    return True, "ghi sổ từng chặng + tiến độ hiện ngay khi chạy nền"


def bh13_docx_doc_duoc_chuoi_noi_kieu_js():
    """13/08 — `build_dashboard_docx.py` chết trên dashboard dùng nối chuỗi JS.

        source:"...EMA; 12 June 2026. "+"https://www.ema.europa.eu/..."

    Hợp lệ trong JavaScript, KHÔNG hợp lệ trong JSON ⇒ `json.loads()` ném
    "Expecting ',' delimiter". `AnToanThuoc_EMA_PRAC_20260614` là bản DUY NHẤT trong
    10 bản xuất lại không ra được .docx — và vì PDF dựng TỪ .docx nên mất luôn PDF.
    Dây chuyền chỉ in "⚠ Bỏ qua: chưa có file .docx", không nói lý do, nên lỗi trông
    như một bước bị bỏ chứ không như một bản thảo hỏng.

    Kiểm HÀNH VI: gọi thẳng hàm gộp, và bảo đảm dấu cộng nằm TRONG nội dung không bị
    đụng ("nguy cơ tim mạch + chuyển hoá" là câu y khoa bình thường).
    """
    m = _nap(DASH / "tools/build_dashboard_docx.py", "docx_hoiquy")
    f = getattr(m, "join_string_concatenation", None)
    if f is None:
        return False, "mất hàm gộp chuỗi nối — dashboard dùng \"a\"+\"b\" sẽ lại hỏng .docx"
    ca = [('{"a":"x "+"y"}', '{"a":"x y"}'),
          ('{"a":"nguy cơ tim mạch + chuyển hoá"}', '{"a":"nguy cơ tim mạch + chuyển hoá"}'),
          ('{"a":"x"+\n  "y"}', '{"a":"xy"}')]
    for vao, mong in ca:
        if f(vao) != mong:
            return False, f"gộp sai: {vao!r} → {f(vao)!r} (cần {mong!r})"
    return True, "đọc được chuỗi nối JS, không đụng dấu + trong nội dung"


BAI_HOC = [
    ("BH01", "12/08", "Cổng không được `return` sớm che luật item", bh01_khong_return_som),
    ("BH02", "12/08", "Parser giữ nguyên giá trị có nháy kép", bh02_parser_giu_nguyen_nhay_kep),
    ("BH03", "12/08", "Miễn trừ quy phạm từ chối Consensus", bh03_quy_pham_khong_nhan_consensus),
    ("BH04", "12/08", "Quy phạm không cứu nguồn tự chấm thấp", bh04_quy_pham_khong_cuu_nguon_tu_cham_thap),
    ("BH05", "12/08", "Công cụ chung sống được trên Windows", bh05_cong_cu_chung_song_duoc_tren_windows),
    ("BH06", "12/08", "Không đường dẫn cứng của một máy", bh06_khong_duong_dan_cung_cua_mot_may),
    ("BH07", "12/08", "Đọc secrets ngoài OneDrive (chống dữ liệu giả)", bh07_doc_secrets_ngoai_onedrive),
    ("BH08", "12/08", "Không gộp 'không biết' với 'có vấn đề'", bh08_khong_gop_khong_biet_voi_co_van_de),
    ("BH09", "13/08", "Skill sửa ở nguồn tới được nơi chạy", bh09_skill_toi_duoc_noi_chay),
    ("BH10", "13/08", "Ba việc lâm sàng vẫn bị cấm tự động", bh10_ba_viec_cam_van_bi_cam),
    ("BH11", "13/08", "Tool skill 3 bản khớp + còn vá UTF-8", bh11_tool_skill_ba_ban_khop_va_co_va_utf8),
    ("BH12", "13/08", "Quét nguồn giữ tiến độ + hiện tiến độ", bh12_quet_nguon_giu_tien_do_va_hien_tien_do),
    ("BH13", "13/08", "Bộ dựng Word đọc được chuỗi nối JS", bh13_docx_doc_duoc_chuoi_noi_kieu_js),
]


def main() -> int:
    ap = argparse.ArgumentParser(description="Chốt hồi quy trên các lỗi đã từng xảy ra")
    ap.add_argument("--im-khi-on", action="store_true", help="chỉ nói khi có mục tái phát")
    a = ap.parse_args()

    ket: list[tuple[str, str, str, bool, str]] = []
    for ma, ngay, ten, ham in BAI_HOC:
        try:
            ok, ct = ham()
        except Exception as e:  # noqa: BLE001 — chốt hỏng phải LỘ RA, không im lặng xanh
            ok, ct = False, f"chốt lỗi: {type(e).__name__}: {e}"
        ket.append((ma, ngay, ten, ok, ct))

    do = [k for k in ket if not k[3]]
    if a.im_khi_on and not do:
        return 0

    if a.im_khi_on:
        print("")
    print(f"CHỐT HỒI QUY BÀI HỌC — {len(ket) - len(do)}/{len(ket)} còn được canh")
    for ma, ngay, ten, ok, ct in ket:
        print(f"  {'✓' if ok else '✗'} {ma} [{ngay}] {ten}")
        if not ok:
            print(f"      → {ct}")
    if do:
        print(f"\n🔴 {len(do)} BÀI HỌC TÁI PHÁT — lỗi đã sửa nay quay lại.")
        print("   Đọc docstring của hàm tương ứng trong tools/chot_hoi_quy_bai_hoc.py")
        print("   để biết lỗi đó từng gây hại gì.")
        return 1
    print("\n🟢 Không bài học nào tái phát.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
