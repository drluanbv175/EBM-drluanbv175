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
4. Phải THỰC SỰ GỌI vào đường mã mình canh. Thêm 14/08/2026 sau một lần vi phạm
   luật 2 ngay trong file này: chốt BH24 bản đầu chỉ thử regex ở BÊN NGOÀI rồi
   tìm một chuỗi trong mã nguồn — nên nó XANH trong khi mã thật ném
   `NameError: name 're' is not defined` ở đúng dòng đầu của nhánh vừa vá, và
   lượt quét nền chết ngay. Một chốt không chạy qua đúng đường nó canh thì
   KHÔNG canh gì cả; tệ hơn, nó phát ra sự yên tâm sai.

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
    # VÁ 14/08/2026 — TỰ DÒ danh sách tool thay vì viết cứng 4 tên.
    # Bản cũ chỉ phủ 4/8 tool của skill, nên `verify_dashboard.py` — chính là cổng
    # liêm chính, tool QUAN TRỌNG NHẤT trong bộ — lệch bản mà chốt vẫn xanh. Cùng
    # bài học BH20: một danh sách viết cứng sẽ mục ngay khi có tool mới.
    NGUON = REPO / "sync/skills/cap-nhat-chung-cu-y-khoa/tools"
    TEN = sorted(p.stem for p in NGUON.glob("*.py")) if NGUON.is_dir() else []
    if not TEN:
        return False, "không thấy thư mục tool của skill cap-nhat-chung-cu-y-khoa"
    NOI = ["EBM-Dashboards/tools/{}.py",
           "sync/skills/cap-nhat-chung-cu-y-khoa/tools/{}.py",
           "EBM_MASTER/skill_assets/{}.py"]
    # VÁ 14/08 (lần hai trong cùng vòng, SAU khi lần một quá tay) —
    # `dark-analyst` là skill KHÁC: tool của nó khác là ĐÚNG, thêm nó vào danh sách
    # chung sẽ báo lệch oan 6 tool. Nhưng cổng triển khai giám sát (ESD02) đòi RIÊNG
    # `surveillance_scan.py` khớp ở CẢ BA nơi kể cả dark-analyst — bỏ sót đúng chỗ đó
    # khiến chốt xanh trong khi ESD02 FAIL. Nên chỉ mở rộng cho ĐÚNG tool có hợp đồng
    # dùng chung, không mở rộng đại trà.
    DUNG_CHUNG = {"surveillance_scan": ["sync/skills/dark-analyst/tools/{}.py"]}
    lech, mat_va = [], []
    for t in TEN:
        ps = [REPO / n.format(t) for n in NOI]
        for them in DUNG_CHUNG.get(t, []):
            ps.append(REPO / them.format(t))
        co = [p for p in ps if p.exists()]
        if len(co) < 2:
            continue
        if len({hashlib.md5(p.read_bytes()).hexdigest() for p in co}) != 1:
            lech.append(t)
        for p in co:
            noi = p.read_text(encoding="utf-8", errors="replace")
            # CHỈ đòi bản vá ở file THẬT SỰ in ký tự ngoài ASCII. Đòi ở nơi không cần
            # là tự tạo báo động giả — đúng thứ chốt này sinh ra để diệt. Đo thật:
            # `test_verify_dashboard_source_gate.py` không in một ký tự tiếng Việt nào,
            # nên cp1252 của Windows không thể làm nó chết.
            in_ngoai_ascii = any(
                not d.isascii() for d in noi.splitlines() if "print(" in d)
            if not in_ngoai_ascii:
                continue
            # Hai lối viết đều hợp lệ: reconfigure inline, hoặc gọi hàm
            # configure_utf8_stdio() (verify_dashboard.py dùng lối này).
            if ("reconfigure(encoding=" not in noi
                    and "configure_utf8_stdio" not in noi):
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


def bh14_khong_khuyen_viec_chac_chan_vo_ich():
    """13/08 — chu trình bảo bác sĩ "chạy lại thêm vòng" cho việc chạy lại KHÔNG sửa được.

    Đo thật: 562/1146 mục hết hiệu lực, và CẢ 562 là PMID chưa kiểm được rút bài vì
    NCBI đang chặn máy. Chạy lại một trăm vòng cũng không đổi được gì. Lời khuyên chắc
    chắn vô ích tiêu thời gian THẬT của bác sĩ, và tệ hơn: nó làm mất niềm tin vào
    những cảnh báo ĐÚNG khác của cùng công cụ — cùng lớp tác hại với báo động giả.

    Kiểm HÀNH VI trên dữ liệu sống: chạy `--bao-cao` (chỉ đọc sổ, không gọi mạng);
    nếu có mục hết hiệu lực vì chưa kiểm rút bài thì báo cáo PHẢI phát mã
    CAN_NCBI_API_KEY và PHẢI nói rõ chạy lại không sửa được.
    """
    import subprocess
    try:
        r = subprocess.run([sys.executable, str(REPO / "tools/so_xac_minh_nguon.py"), "--bao-cao"],
                           cwd=REPO, capture_output=True, text=True, timeout=180)
    except (OSError, subprocess.SubprocessError) as e:
        return False, f"không chạy được báo cáo sổ: {e}"
    out = r.stdout + r.stderr
    if "CHƯA kiểm được RÚT BÀI" not in out:
        return True, "không còn mục nào hết hiệu lực vì chưa kiểm rút bài"
    if "CAN_NCBI_API_KEY" not in out:
        return False, "có mục chưa kiểm rút bài nhưng KHÔNG phát mã CAN_NCBI_API_KEY"
    if "KHÔNG sửa được" not in out:
        return False, ("báo cáo không nói rõ 'chạy lại thêm vòng KHÔNG sửa được' — "
                       "bác sĩ sẽ chạy lại vô ích")
    return True, "tách đúng lý do, chỉ đúng cách sửa (cần NCBI_API_KEY)"


def bh15_dem_muc_khong_dem_dong():
    """13/08 — bản báo việc THỔI PHỒNG khối lượng vì đếm DÒNG LỖI thay vì đếm MỤC.

    `verify_dashboard` sinh HAI dòng cho cùng một item khi nó vi phạm hai luật
    ("gradeLevel='na'" VÀ "chỉ dựa Consensus"). `tu_sua_chua` cũ dùng
    `out.count("decision='apply'")` nên báo **64 mục** trong khi thực tế chỉ **49** —
    phóng đại 31%. Con số thổi phồng trong bản báo việc cũng là nói sai, và nó khiến
    người ta hoãn một việc thật ra nhỏ hơn tưởng.

    Kiểm HÀNH VI trên đầu ra tổng hợp có đúng tình huống đó: 3 dòng, 2 item.
    """
    m = _nap(REPO / "tools/tu_sua_chua.py", "tsc_hoiquy")
    f = getattr(m, "id_muc_apply", None)
    if f is None:
        return False, "mất hàm id_muc_apply — nguy cơ quay lại đếm dòng"
    mau = ("  ✗ [ITEM-01] decision='apply' nhưng gradeLevel='na' — phải hạ.\n"
           "  ✗ [ITEM-01] decision='apply' chỉ dựa Consensus — cần guideline.\n"
           "  ✗ [ITEM-07] decision='apply' nhưng gradeLevel='low' — phải hạ.\n"
           "  ⚠ [ITEM-09] 'apply' chỉ có URL — cảnh báo, không phải lỗi cứng.\n")
    ra = f(mau)
    if ra != {"ITEM-01", "ITEM-07"}:
        return False, f"đếm sai: {sorted(ra)} (cần ITEM-01, ITEM-07 — 3 dòng nhưng 2 mục)"
    return True, "đếm mục riêng biệt, không đếm dòng lỗi"


def bh16_hook_neo_vao_thu_muc_du_an_va_bao_to():
    """13/08 — cả 7 chốt SessionStart im lặng bỏ qua khi mở Claude ở thư mục khác.

    Guard cũ là `[ -f tools/X.py ]` — đường dẫn TƯƠNG ĐỐI. Mở Claude ở thư mục con
    (vd `medical-ebm-automation/`) thì guard sai ⇒ KHÔNG chốt nào chạy, và vì mỗi
    lệnh kết thúc bằng `; true` nên mã thoát vẫn 0: **bác sĩ nhận đúng cùng một màn
    hình im lặng như khi mọi thứ đều tốt.** Đây là kiểu hỏng tệ nhất của một hệ giám
    sát — nó không sai, nó biến mất.

    Vá: neo vào `$CLAUDE_PROJECT_DIR` và **BÁO TO** khi không tìm thấy công cụ.

    Kiểm HÀNH VI, nhanh: chạy từng lệnh hook với `CLAUDE_PROJECT_DIR` trỏ vào một
    thư mục KHÔNG có công cụ — mỗi lệnh PHẢI in cảnh báo, không được im.
    """
    import json
    import os
    import subprocess
    import tempfile
    p = REPO / ".claude/settings.json"
    try:
        cfg = json.loads(p.read_text(encoding="utf-8"))
        lenhs = [m["command"] for nhom in cfg["hooks"]["SessionStart"] for m in nhom["hooks"]]
    except (OSError, ValueError, KeyError) as e:
        return False, f"không đọc được hook SessionStart: {e}"
    if not lenhs:
        return False, "không còn chốt SessionStart nào"
    with tempfile.TemporaryDirectory() as rong:
        env = dict(os.environ, CLAUDE_PROJECT_DIR=rong)
        im = []
        for c in lenhs:
            if "CLAUDE_PROJECT_DIR" not in c:
                im.append("có chốt KHÔNG neo vào $CLAUDE_PROJECT_DIR")
                continue
            try:
                r = subprocess.run(["bash", "-c", c], capture_output=True, text=True,
                                   env=env, cwd=rong, timeout=30)
            except (OSError, subprocess.SubprocessError) as e:
                im.append(f"chạy lỗi: {e}")
                continue
            if "KHÔNG CHẠY" not in (r.stdout + r.stderr):
                im.append("một chốt IM LẶNG khi không thấy công cụ")
    if im:
        return False, f"{len(im)}/{len(lenhs)} chốt hỏng im lặng: {im[0]}"
    return True, f"{len(lenhs)} chốt neo vào $CLAUDE_PROJECT_DIR, thiếu file thì báo TO"


def bh17_tieu_de_bo_nam_noi_dung_su_that():
    """13/08 — dây chuyền in "Bộ năm đã sẵn sàng" VÔ ĐIỀU KIỆN, kể cả khi chỉ có 3/5.

    Ca thật cùng ngày: `AnToanThuoc_EMA_PRAC_20260614` hỏng bước ③ (chuỗi nối kiểu JS
    làm chết bộ dựng Word) nên mất cả ④ lẫn ⑤ — mà dòng tiêu đề vẫn tuyên bố "đã sẵn
    sàng". Người đọc lướt sẽ tin gói đã đủ và đem bản Word CŨ đi dùng cho người bệnh.

    Kiểm HÀNH VI: gọi thẳng hàm tóm tắt với ba trạng thái đủ/thiếu.
    """
    m = _nap(REPO / "tools/xuat_goi_cap_nhat.py", "xuat_hoiquy")
    f = getattr(m, "tom_tat_bo_nam", None)
    if f is None:
        return False, "mất hàm tom_tat_bo_nam — nguy cơ quay lại tiêu đề vô điều kiện"
    du = {"dashboard": "a", "ban_doc": "b", "word": "c", "word_html": "d", "pdf": "e"}
    if "5/5" not in f(du):
        return False, f"gói ĐỦ mà không nói 5/5: {f(du)!r}"
    thieu = f({"dashboard": "a", "ban_doc": "b", "word": "c"})
    if "3/5" not in thieu or "THIẾU" not in thieu:
        return False, f"gói THIẾU mà vẫn không nói rõ: {thieu!r}"
    if "sẵn sàng" in thieu:
        return False, f"gói thiếu vẫn tự nhận 'sẵn sàng': {thieu!r}"
    return True, "tiêu đề nói đúng số sản phẩm thật sự sinh được"


def bh18_giu_moi_item_cung_pmid():
    """13/08 — `doc_muc()` khoá dict theo PMID nên BỎ IM LẶNG mọi item trùng nguồn.

    Một guideline mang hàng chục khuyến cáo, mỗi khuyến cáo có `decision` riêng —
    đo được **21 ca** như vậy trong kho. Bản cũ chỉ giữ item CUỐI theo thứ tự file,
    nên phần so mâu thuẫn đem so một item TÙY Ý của bản này với một item TÙY Ý của
    bản kia ⇒ có thể tuyên bố "hai bản nói ngược nhau" trong khi chúng chỉ nói về
    HAI KHUYẾN CÁO KHÁC NHAU của cùng tài liệu.

    Đo trên toàn kho: 3/224 PMID chung bị ảnh hưởng, và **2 trong số đó đã bị báo
    cho bác sĩ như mâu thuẫn thật** (BenhThanMan PMID 38490803 · ViemGanB PMID
    41186418). Sau vá: 14 → 12 mâu thuẫn thật. Báo động giả trong hàng đợi quyết
    định của bác sĩ là thứ đã được ghi là tệ hơn không kiểm.

    Kiểm HÀNH VI: khối DATA tổng hợp có HAI item cùng một PMID, khác decision.
    """
    m = _nap(REPO / "tools/dang_ky_chu_de.py", "dkcd_hoiquy")
    vd = _nap(DASH / "tools/verify_dashboard.py", "vd_bh18")
    import tempfile
    mau = ("const DATA = {items:[\n"
           " {id:'ITEM-01', title:'khuyến cáo A', pmid:'99999999', decision:'apply'},\n"
           " {id:'ITEM-02', title:'khuyến cáo B', pmid:'99999999', decision:'consider'}\n"
           "]};")
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "WebDashboard_EBM_VanDeCuThe_Thu_20260101.html"
        p.write_text(mau, encoding="utf-8")
        ra = m.doc_muc(vd, p)
    ds = ra.get("99999999")
    if not isinstance(ds, list):
        return False, f"doc_muc không trả LIST — item trùng PMID lại bị bỏ ({type(ds).__name__})"
    if len(ds) != 2:
        return False, f"giữ {len(ds)}/2 item cùng PMID — vẫn mất item"
    if {x[0] for x in ds} != {"apply", "consider"}:
        return False, f"mất quyết định của item bị ghi đè: {[x[0] for x in ds]}"
    return True, "giữ đủ mọi item cùng PMID, phân biệt được mâu thuẫn thật"


def bh19_do_tuoi_doc_ket_qua_khong_doc_mtime():
    """13/08 — chốt độ tươi kết luận "còn hạn" chỉ từ `st_mtime` của file log.

    Hai script giám sát ghi dòng "BẮT ĐẦU" vào log **NGAY khi khởi động**, trước khi
    làm bất cứ việc gì ⇒ một lượt chạy KHỞI ĐỘNG RỒI CHẾT vẫn làm mtime tươi mới, và
    bác sĩ nhận "🟢 CHỨNG CỨ còn hạn" trong khi giám sát thật sự đã hỏng.

    Từ khi `tu_khoi_dong.py` tự phóng mỗi phiên, đây thành VÒNG LẶP IM LẶNG:
    phóng → hỏng → mtime tươi → "còn hạn" → không ai biết, tuần này qua tuần khác.
    Bản thân log ĐÃ chứa câu trả lời ("KẾT THÚC … tổng thể=PASS | CÓ BƯỚC LỖI") —
    chỉ là chưa ai đọc. Cùng họ BH14–BH18: hệ nói sai mà không sai phép tính nào.

    Kiểm HÀNH VI trên log tổng hợp, gồm cả ca lượt cũ LỖI nhưng lượt mới PASS.
    """
    import tempfile
    m = _nap(REPO / "tools/kiem_do_tuoi_chung_cu.py", "dotuoi_bh19")
    ca = [("PASS", "= BẮT ĐẦU =\n= KẾT THÚC — tổng thể=PASS =\n"),
          ("LỖI", "= BẮT ĐẦU =\n= KẾT THÚC — bước (1)=1, tổng thể=CÓ BƯỚC LỖI =\n"),
          ("DANG_DO", "= BẮT ĐẦU an toàn thuốc =\nđang chạy…\n"),
          ("PASS", "= KẾT THÚC — tổng thể=CÓ BƯỚC LỖI =\n= BẮT ĐẦU =\n"
                   "= KẾT THÚC — tổng thể=PASS =\n")]
    with tempfile.TemporaryDirectory() as d:
        for mong, noi in ca:
            p = Path(d) / "t.log"
            p.write_text(noi, encoding="utf-8")
            try:
                _, tt = m.lan_chay_cuoi(p)
            except (TypeError, ValueError) as e:
                return False, f"lan_chay_cuoi không còn trả (ngày, trạng thái): {e}"
            if tt != mong:
                return False, (f"lượt chạy {mong} bị đọc thành {tt!r} — "
                               f"một lượt giám sát HỎNG có thể bị coi là còn hạn")
    return True, "đọc KẾT QUẢ lượt chạy, không chỉ nhìn mtime"


def bh20_tu_khoi_dong_cung_doc_ket_qua():
    """14/08 — VÁ DỞ DANG của BH19: `tu_khoi_dong.qua_han()` bị bỏ sót.

    Hôm trước đã sửa `kiem_do_tuoi_chung_cu` để đọc KẾT QUẢ lượt chạy thay vì chỉ
    nhìn `st_mtime` — nhưng `tu_khoi_dong` dùng CÙNG tín hiệu cho CÙNG mục đích thì
    vẫn nguyên. Hậu quả nếu để nguyên còn nặng hơn BH19: script ghi "BẮT ĐẦU" ngay
    lúc khởi động ⇒ một lượt **khởi động rồi chết** vẫn làm mtime tươi ⇒ `qua_han()`
    kết luận "còn hạn" ⇒ **KHÔNG phóng lại**. Giám sát hỏng vĩnh viễn, không bao giờ
    được thử lại, và cũng không ai được báo.

    Bài học kép: (a) khi vá một tín hiệu bị dùng sai nghĩa, phải tìm MỌI nơi dùng
    tín hiệu đó cho cùng mục đích; (b) hai công cụ hỏi cùng một câu phải dùng CHUNG
    một câu trả lời — nay `tu_khoi_dong` gọi lại chính `lan_chay_cuoi()`.

    Kiểm HÀNH VI: log lượt cuối LỖI và log CHẾT GIỮA CHỪNG đều phải ra "cần chạy lại".
    """
    import tempfile
    m = _nap(REPO / "tools/tu_khoi_dong.py", "tk_bh20")
    ca = [("= BẮT ĐẦU =\n= KẾT THÚC — tổng thể=PASS =\n", False, "lượt PASS mới"),
          ("= BẮT ĐẦU =\n= KẾT THÚC — tổng thể=CÓ BƯỚC LỖI =\n", True, "lượt cuối LỖI"),
          ("= BẮT ĐẦU an toàn thuốc =\n", True, "chết giữa chừng")]
    goc = {k: v["log"] for k, v in m.OWNER.items()}
    try:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "t.log"
            for ten in m.OWNER:
                m.OWNER[ten]["log"] = Path(d) / "khong-co.log"
            m.OWNER["tuan"]["log"] = p
            for noi, mong, nhan in ca:
                p.write_text(noi, encoding="utf-8")
                can = any(x[0] == "tuan" for x in m.qua_han())
                if can != mong:
                    return False, (f"{nhan}: {'không' if mong else ''} phóng lại sai — "
                                   f"giám sát hỏng có thể KHÔNG BAO GIỜ được chạy lại")
    finally:
        for k, v in goc.items():
            m.OWNER[k]["log"] = v
    return True, "lượt hỏng/chết giữa chừng đều được phóng lại"


def bh21_moi_parser_deu_gop_chuoi_noi():
    """14/08 — vá `build_dashboard_docx` (BH13) nhưng bỏ sót `array_field` của cổng.

    Từ 13/08 tới nay HAI PARSER CỦA CÙNG MỘT DỮ LIỆU BẤT ĐỒNG: bộ dựng Word đọc
    `references` của `AnToanThuoc_EMA_PRAC_20260614` ra **3** phần tử, còn cổng liêm
    chính đọc ra **4** — vì cổng tách `"…12 June 2026. "+"https://…"` thành hai, biến
    một tài liệu tham khảo thành hai, một trong đó chỉ là URL trần.

    Đúng bài học BH20 lặp lại: vá một nơi dùng logic đó thì phải vá MỌI nơi.

    Kiểm HÀNH VI: gộp đúng, và dấu `+` nằm TRONG nội dung không được đụng.
    """
    vd = _nap(DASH / "tools/verify_dashboard.py", "vd_bh21")
    ra = vd.array_field('references:["phần đầu. "+"https://vd.org/x","mục hai"]',
                        "references")
    if len(ra) != 2 or "https://vd.org/x" not in ra[0]:
        return False, f"không gộp chuỗi nối: {ra}"
    giu = vd.array_field('x:["nguy cơ tim mạch + chuyển hoá","b"]', "x")
    if giu != ["nguy cơ tim mạch + chuyển hoá", "b"]:
        return False, f"đụng vào dấu + nằm TRONG nội dung: {giu}"
    return True, "gộp chuỗi nối, không đụng dấu + trong nội dung"


def bh22_khong_day_file_sao_luu_vao_noi_chay():
    """14/08 — quy trình đồng bộ tự đẩy CHÍNH file sao lưu của mình vào nơi chạy.

    `BO_QUA` so trên `f.parts` (thành phần đường dẫn) nên không bao giờ bắt được
    một TÊN FILE như `verify_dashboard.py.bak-20260814-005720`. Đo được **8 file
    sao lưu** đã nằm trong thư mục skill ĐANG CHẠY, ngay cạnh bản sống.

    Không gây lỗi chạy (đuôi `.bak-*` không import được), nhưng kho phình mãi, và
    một bản CŨ của công cụ an toàn nằm cạnh bản mới gây hiểu nhầm cho bất kỳ ai mở
    thư mục đó ra xem. Cùng họ với các lỗi hôm nay: bộ lọc **kiểm sai trục** —
    tên file vs thành phần đường dẫn.

    Kiểm HÀNH VI: bộ lọc phải bắt tên file sao lưu, và không đụng file thật.
    """
    m = _nap(REPO / "tools/dong_bo_skill.py", "dbs_bh22")
    f = getattr(m, "_bi_bo_qua", None)
    if f is None:
        return False, "mất bộ lọc _bi_bo_qua — file sao lưu sẽ lại lọt vào nơi chạy"
    goc = Path("a")
    ca = [(Path("a/tools/verify_dashboard.py"), False),
          (Path("a/tools/verify_dashboard.py.bak-20260814-005720"), True),
          (Path("a/SKILL.md"), False),
          (Path("a/__pycache__/x.py"), True),
          (Path("a/x.py.orig"), True)]
    for p, mong in ca:
        if f(p, goc) != mong:
            return False, f"lọc sai {p.name!r}: {f(p, goc)} (cần {mong})"
    rt = m.tim_runtime()
    if rt is not None:
        con = [p for p in rt.rglob("*.bak-*") if p.is_file()]
        if con:
            return False, f"{len(con)} file sao lưu vẫn nằm trong nơi chạy"
    return True, "lọc đúng theo tên file; nơi chạy sạch file sao lưu"


def bh23_khong_dashboard_nao_bi_loai_im_lang():
    """14/08 — regex tên file loại IM LẶNG một dashboard khỏi đăng ký chủ đề.

    `tach_ten()` bắt buộc dạng `<nhóm>_<chủ-đề>_<ngày>`, nên
    `WebDashboard_EBM_Uptodate_20260607.html` (không có phần chủ đề) KHÔNG khớp và
    bị bỏ qua — **vô hình luôn với phần dò mâu thuẫn**. Đo được 61/62 tách được,
    đúng một bản rơi ra mà **không một dòng báo**: nó trông hệt như "đã kiểm hết".

    Cùng họ với BH16 (chốt biến mất) và BH22 (lọc sai trục): thứ bị loại thầm lặng
    nguy hiểm hơn thứ báo lỗi, vì không ai đi tìm cái mình không biết là đang thiếu.

    Kiểm HÀNH VI trên dữ liệu SỐNG: MỌI dashboard trong kho phải tách được tên.
    """
    m = _nap(REPO / "tools/dang_ky_chu_de.py", "dkcd_bh23")
    ds = sorted(DASH.glob("WebDashboard_*.html"))
    if not ds:
        return True, "kho chưa có dashboard nào"
    hong = [p.name for p in ds if m.tach_ten(p.name) is None]
    if hong:
        return False, (f"{len(hong)}/{len(ds)} dashboard bị LOẠI IM LẶNG khỏi đăng ký "
                       f"chủ đề (vô hình với dò mâu thuẫn): {', '.join(hong[:3])}")
    return True, f"{len(ds)}/{len(ds)} dashboard đều nằm trong đăng ký chủ đề"


def bh24_doi_ghi_dang_url_van_qua_crossref():
    """14/08 — cùng một nguồn, chỉ khác CÁCH GHI, nhận hai mức bảo đảm khác hẳn.

    Mục `doi:` được xác minh METADATA qua Crossref; mục `url:` chỉ được kiểm "địa
    chỉ có phản hồi". Nhưng **17 định danh** trong kho là DOI viết dạng
    `https://doi.org/10.…` nên rơi vào nhánh yếu — và mức yếu hơn đó **không hề được
    nói ra**. Hệ đưa ra một bảo đảm THẤP HƠN mức nó ngụ ý.

    Nay nhận diện link doi.org, rút DOI và xác minh qua Crossref; Crossref không
    phân giải được thì LÙI về kiểm HTTP — đúng mức bảo đảm cũ, không tự hạ thành
    "chưa xác minh" (HTTP vẫn là bằng chứng thật, chỉ yếu hơn).

    Kiểm HÀNH VI: regex rút DOI phải đúng trên link doi.org và link `/doi/` của nhà
    xuất bản, và KHÔNG bắt nhầm URL không phải DOI.
    """
    m = _nap(REPO / "tools/so_xac_minh_nguon.py", "sx_bh24")

    # GỌI THẬT vào `xac_minh_mot`, KHÔNG đếm chuỗi trong mã nguồn.
    # Bản đầu của chính chốt này chỉ (a) thử regex ở BÊN NGOÀI và (b) tìm chuỗi
    # "doi_rut_tu_url" trong file — nên nó XANH trong khi mã thật ném
    # `NameError: name 're' is not defined` ngay dòng đầu của nhánh vừa vá, và
    # cả lượt quét nền chết. Một chốt không chạy qua đúng đường nó canh thì không
    # canh gì cả. Đây là luật 2 của file này, và tôi vừa vi phạm nó.
    class _VdGia:
        """vd giả, NGOẠI TUYẾN: chỉ cần đủ để đi hết nhánh url→doi."""
        @staticmethod
        def verify_doi_online(doi, *a, **k):
            return True, f"tiêu đề giả cho {doi}"

        @staticmethod
        def verify_url_online(url, *a, **k):
            return True, "trang có phản hồi"

    try:
        r_doi = m.xac_minh_mot("url:https://doi.org/10.1056/NEJMoa2109927", _VdGia)
        r_thuong = m.xac_minh_mot("url:https://www.ema.europa.eu/en/news/abc", _VdGia)
    except Exception as e:  # noqa: BLE001 — đúng thứ chốt cũ đã bỏ lọt
        return False, f"xac_minh_mot ném lỗi: {type(e).__name__}: {e}"

    if not r_doi or r_doi.get("nguon_xac_minh") != "crossref":
        return False, (f"DOI dạng URL KHÔNG được nâng lên Crossref: "
                       f"{(r_doi or {}).get('nguon_xac_minh')!r}")
    if r_doi.get("doi_rut_tu_url") != "10.1056/NEJMoa2109927":
        return False, f"rút DOI sai: {r_doi.get('doi_rut_tu_url')!r}"
    if not r_thuong or r_thuong.get("nguon_xac_minh") != "http":
        return False, "URL thường bị nhận nhầm là DOI"
    return True, "gọi thật: DOI-trong-URL → crossref; URL thường → http"


def bh25_tach_do_manh_khuyen_cao_khoi_chat_luong_chung_cu():
    """14/08 — cổng GỘP hai trục mà GRADE cố ý TÁCH.

    GRADE có hai trục ĐỘC LẬP: ĐỘ MẠNH khuyến cáo (strong/conditional) và CHẤT
    LƯỢNG chứng cứ (high…very low). Một khuyến cáo MẠNH trên chứng cứ chất lượng
    THẤP là kết quả hợp lệ và phổ biến — đúng những tình huống đe doạ tính mạng.

    Cổng cũ chặn thẳng mọi `gradeLevel` khác `na`, nên ép một lựa chọn SAI CẢ HAI
    ĐƯỜNG với `SuyTim_NoiTiet ITEM-05` (nhận biết khủng hoảng thượng thận): giữ
    `low` thì bị chặn dù Endocrine Society viết "We recommend" (= MẠNH); đổi sang
    `na` thì NÓI SAI về nguồn (nguồn CÓ dùng GRADE).

    Miễn trừ mới đòi BẰNG CHỨNG VĂN BẢN, không chấp nhận chỉ dán nhãn; và khuyến
    cáo CÓ ĐIỀU KIỆN vẫn bị chặn. Bản đầu của chính bản vá này đặt nhánh mới lên
    TRƯỚC phép kiểm `design` ⇒ mở lại lỗ hổng BH03 (Consensus đi qua cổng) — bắt
    được nhờ ca biên, đã sửa thứ tự.
    """
    vd = _nap(DASH / "tools/verify_dashboard.py", "vd_bh25")
    ca = [("Guideline", "low", "guideline-strong-rec",
           'Endocrine Society dùng GRADE; "We recommend" = MẠNH', True),
          ("Guideline", "low", "guideline-strong-rec",
           "ACR 2021 — khuyến cáo CÓ ĐIỀU KIỆN", False),
          ("Guideline", "low", "guideline-strong-rec", "", False),
          ("Guideline", "low", "drug-label", '"We recommend"', False),
          ("Consensus", "low", "guideline-strong-rec", '"We recommend"', False),
          ("Consensus", "na", "guideline-strong-rec", "x", False),
          ("Guideline", "na", "drug-label", "Boxed Warning FDA", True),
          ("Guideline", "vlow", "guideline-strong-rec",
           "GRADE 1C — strong recommendation", True)]
    for d, g, b, gs, mong in ca:
        duoc, _ = vd.normative_exemption(d, g, b, gs)
        if duoc != mong:
            return False, (f"design={d} grade={g} basis={b}: {'miễn' if duoc else 'chặn'} "
                           f"(cần {'miễn' if mong else 'chặn'})")
    return True, "tách đúng hai trục; Consensus và conditional vẫn bị chặn"


def bh26_neo_sua_hang_loat_phai_la_chunk_da_parse():
    """14/08 — khối SCHEMA trong dashboard BẮT CHƯỚC cấu trúc mục, nên neo theo `id`
    trúng phải TÀI LIỆU thay vì DỮ LIỆU.

    Sửa hàng loạt hôm nay hỏng hai lần theo hai kiểu khác nhau:
      • neo bằng ~42 ký tự NGỮ CẢNH → trùng giữa các mục (11/14 mục hỏng);
      • chuyển sang neo theo `{id:'ITEM-xx'}` → vẫn trúng nhầm, vì mỗi dashboard có
        một khối chú thích schema mở đầu bằng đúng dạng đó
        (`design:'Guideline'|'Meta'|'RCT'|…`). ITEM-01 khớp 2 chỗ.
    May là lần đó không hỏng dữ liệu: regex đòi đúng `'Consensus'` nên khối schema
    không khớp. Nhưng đó là MAY, không phải thiết kế.

    Neo AN TOÀN duy nhất: chính đoạn do `split_items()` trả về — đúng thứ mọi công
    cụ khác coi là một mục. Chốt này canh tiền đề của cách đó: mỗi đoạn phải XUẤT
    HIỆN ĐÚNG MỘT LẦN trong file, nếu không thì neo bằng đoạn cũng không an toàn.
    """
    vd = _nap(DASH / "tools/verify_dashboard.py", "vd_bh26")
    xau = []
    for f in sorted(DASH.glob("WebDashboard_*.html")):
        t = f.read_text(encoding="utf-8", errors="replace")
        db = vd.extract_data_block(t)
        if not db:
            continue
        for ch in vd.split_items(db):
            if t.count(ch) != 1:
                xau.append(f"{f.name[:30]}/{vd.field(ch, 'id')}")
                break
    if xau:
        return False, ("đoạn mục KHÔNG duy nhất trong file — sửa hàng loạt bằng neo "
                       "đoạn có thể ghi nhầm: " + ", ".join(xau[:3]))
    return True, "mọi đoạn mục đều duy nhất — neo bằng chunk đã parse là an toàn"


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
    ("BH14", "13/08", "Không khuyên việc chắc chắn vô ích", bh14_khong_khuyen_viec_chac_chan_vo_ich),
    ("BH15", "13/08", "Đếm MỤC, không đếm dòng lỗi", bh15_dem_muc_khong_dem_dong),
    ("BH16", "13/08", "Hook neo thư mục dự án + báo TO khi thiếu", bh16_hook_neo_vao_thu_muc_du_an_va_bao_to),
    ("BH17", "13/08", "Tiêu đề bộ năm nói đúng sự thật", bh17_tieu_de_bo_nam_noi_dung_su_that),
    ("BH18", "13/08", "Giữ mọi item cùng PMID (chống báo động giả)", bh18_giu_moi_item_cung_pmid),
    ("BH19", "13/08", "Độ tươi đọc KẾT QUẢ, không chỉ nhìn mtime", bh19_do_tuoi_doc_ket_qua_khong_doc_mtime),
    ("BH20", "14/08", "Tự khởi động cũng đọc KẾT QUẢ (vá dở dang)", bh20_tu_khoi_dong_cung_doc_ket_qua),
    ("BH21", "14/08", "Mọi parser đều gộp chuỗi nối JS", bh21_moi_parser_deu_gop_chuoi_noi),
    ("BH22", "14/08", "Không đẩy file sao lưu vào nơi chạy", bh22_khong_day_file_sao_luu_vao_noi_chay),
    ("BH23", "14/08", "Không dashboard nào bị loại im lặng", bh23_khong_dashboard_nao_bi_loai_im_lang),
    ("BH24", "14/08", "DOI ghi dạng URL vẫn qua Crossref", bh24_doi_ghi_dang_url_van_qua_crossref),
    ("BH25", "14/08", "Tách độ mạnh khuyến cáo khỏi chất lượng chứng cứ", bh25_tach_do_manh_khuyen_cao_khoi_chat_luong_chung_cu),
    ("BH26", "14/08", "Neo sửa hàng loạt phải là chunk đã parse", bh26_neo_sua_hang_loat_phai_la_chunk_da_parse),
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
