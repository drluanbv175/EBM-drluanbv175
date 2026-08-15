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
    # ĐĂNG KÝ TRƯỚC khi exec — bắt buộc, không phải tuỳ chọn. `@dataclass` gọi
    # `sys.modules.get(cls.__module__).__dict__` lúc dựng lớp; module chưa đăng ký thì
    # nhận None và ném AttributeError. Nghĩa là mọi module CÓ dataclass đều nạp hỏng
    # bằng lối cũ — và chốt hỏng thì hiện thành "BÀI HỌC TÁI PHÁT", tức báo động giả
    # đúng vào thứ sinh ra để chống báo động giả. (Vấp thật khi thêm BH37, 14/08/2026.)
    sys.modules[ten] = m
    try:
        spec.loader.exec_module(m)
    except BaseException:
        sys.modules.pop(ten, None)
        raise
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

    CẬP NHẬT 14/08/2026 — bài học GIỮ NGUYÊN, cách sửa ĐÚNG thì đã đổi. Kiểm rút bài
    nay đi qua chuỗi 3 tầng (Retraction Watch ngoại tuyến → NCBI → Europe PMC), nên
    câu "chạy lại KHÔNG sửa được, phải có NCBI_API_KEY" tự nó trở thành lời khuyên
    vô ích thứ hai: hai tầng mới đều KHÔNG cần khoá. Chốt vì thế không còn đòi đúng
    một chuỗi cố định, mà đòi lời khuyên TRỎ VÀO ĐÒN BẨY CÒN DÙNG ĐƯỢC:
      • chưa tải nền ngoại tuyến → phải phát CAN_TAI_RETRACTION_WATCH (tải là xong);
      • đã có nền mà vẫn tắc     → phát CAN_NCBI_API_KEY (khoá là đòn bẩy còn lại).
    Và tuyệt đối không được nói "KHÔNG sửa được" khi việc tải nền vẫn sửa được.
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

    co_nen = (REPO / "medical-ebm-automation" / "data" / "retraction_watch"
              / "retraction_watch.csv").exists()
    can = "CAN_NCBI_API_KEY" if co_nen else "CAN_TAI_RETRACTION_WATCH"
    if can not in out:
        return False, (f"có mục chưa kiểm rút bài nhưng KHÔNG phát mã {can} "
                       f"(nền ngoại tuyến {'ĐÃ' if co_nen else 'CHƯA'} tải)")
    if not co_nen and "KHÔNG sửa được" in out:
        return False, ("báo cáo nói 'KHÔNG sửa được' trong khi tải nền ngoại tuyến "
                       "SẼ sửa được — lại là lời khuyên vô ích, chỉ đổi chiều")
    return True, f"chỉ đúng đòn bẩy còn dùng được ({can})"


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


def bh27_khong_kiem_duoc_phai_la_van_de():
    """14/08 — FAIL-OPEN thật trong cổng A12: "không kiểm được" bị tính là SẠCH.

    Ngày 12/08 trạng thái `unknown_fetch_error` được tách ra để phân biệt "KHÔNG
    BIẾT" với "nghi trích dẫn ma" — một bản vá đúng. Nhưng tập tiêu thụ
    `_PROBLEM_STATUSES` trong `check_citation_retraction.py` KHÔNG được cập nhật
    theo, nên trạng thái trung thực mới lại VÔ HÌNH với cổng.

    Hậu quả đã tái hiện được ngày 14/08, đúng lúc NCBI đang chặn máy này: mọi PMID
    nhận `unknown_fetch_error` ⇒ không cái nào bị tính là vấn đề ⇒ `all_clean=true`
    được ghi VÀ KÝ vào `A12_RETRACTION_RECEIPT.json`, CLI in "✅ Không phát hiện rút
    bài" và thoát 0. `run_g10_assemble.py` chỉ chặn khi `all_clean is not True`, nên
    gói nộp đi qua cổng A12 trong khi KHÔNG một trích dẫn nào được kiểm.

    Chốt này KHÔNG chỉ canh đúng một chuỗi (vá xong là hết tác dụng). Nó rút TOÀN BỘ
    từ vựng trạng thái mà mã sống thật sự phát ra, rồi đòi: mọi trạng thái ngoài
    "ok" đều phải nằm trong `_PROBLEM_STATUSES`. Thêm một trạng thái "không biết"
    mới mà quên đăng ký là đỏ ngay — đúng cách lỗi này đã sinh ra.

    PHẠM VI CỐ Ý HẸP: chỉ rút từ các hàm thuộc hợp đồng RÚT BÀI. Bản đầu của chính
    chốt này quét cả file nên vớ phải `"resolved"` của `fetch_metadata()` — một hợp
    đồng KHÁC (phân giải metadata), ở đó `resolved` là trạng thái LÀNH. Trộn hai từ
    vựng vào nhau đẻ ra báo động giả ngay lần chạy đầu.
    """
    import ast

    mea = REPO / "medical-ebm-automation"
    f_tieu_thu = mea / "tools/check_citation_retraction.py"
    # Khai ĐÍCH DANH hàm nào thuộc hợp đồng rút bài. Đổi tên hàm mà quên sửa đây thì
    # chốt đỏ — đúng ý: nghĩa là nó đã thôi canh phần mã mà nó tưởng đang canh.
    nguon_phat = {
        mea / "app/sources/pubmed.py": {"check_retraction_status", "_parse_retraction_xml"},
        mea / "app/sources/europepmc.py": {"check_retraction_status", "_doc_rut_bai"},
        mea / "app/sources/retraction_chain.py": {"check", "_gop"},
    }
    if not f_tieu_thu.exists():
        return False, "thiếu check_citation_retraction.py — không kiểm được cổng A12"

    # Bên TIÊU THỤ: đọc thẳng tập literal, không import (chốt phải chạy bằng python3 hệ thống).
    tap = None
    for node in ast.walk(ast.parse(f_tieu_thu.read_text(encoding="utf-8"))):
        if (isinstance(node, ast.Assign) and node.targets
                and getattr(node.targets[0], "id", "") == "_PROBLEM_STATUSES"):
            try:
                tap = set(ast.literal_eval(node.value))
            except (ValueError, SyntaxError):
                return False, "_PROBLEM_STATUSES không còn là literal đọc được"
    if tap is None:
        return False, "không tìm thấy _PROBLEM_STATUSES trong check_citation_retraction.py"

    # Bên PHÁT: gom giá trị gán cho khoá "status", CHỈ trong các hàm đã khai ở trên.
    phat, thieu_ham = set(), []
    for f, ten_ham in nguon_phat.items():
        if not f.exists():
            return False, f"thiếu {f.name} — chuỗi kiểm rút bài không còn nguyên vẹn"
        cay = ast.parse(f.read_text(encoding="utf-8"))
        thay = set()
        for ham in ast.walk(cay):
            if not isinstance(ham, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if ham.name not in ten_ham:
                continue
            thay.add(ham.name)
            for node in ast.walk(ham):
                if not isinstance(node, ast.Dict):
                    continue
                for k, v in zip(node.keys, node.values):
                    if (isinstance(k, ast.Constant) and k.value == "status"
                            and isinstance(v, ast.Constant) and isinstance(v.value, str)):
                        phat.add(v.value)
        thieu_ham += [f"{f.name}::{h}" for h in sorted(ten_ham - thay)]
    if thieu_ham:
        return False, ("không tìm thấy hàm thuộc hợp đồng rút bài: " + ", ".join(thieu_ham)
                       + " → chốt đã thôi canh phần mã nó tưởng đang canh")
    if not phat:
        return False, "không rút được từ vựng trạng thái nào — nghi mã đã đổi cấu trúc"

    sot = phat - tap - {"ok"}
    if sot:
        return False, ("trạng thái KHÔNG được tính là vấn đề: " + ", ".join(sorted(sot))
                       + " → all_clean=true dù chưa kiểm được gì (fail-open cổng A12)")
    return True, f"{len(phat)} trạng thái; mọi thứ ngoài 'ok' đều bị tính là vấn đề"


def bh28_khong_thay_phan_doan_ngu_nghia_bang_do_giong_tu_vung():
    """14/08 — thử tự phân loại "cùng khẳng định vs khác kết cục" bằng ĐỘ GIỐNG
    TIÊU ĐỀ. SAI, và sai theo hướng NGUY HIỂM HƠN lỗi ban đầu.

    Bối cảnh: phần dò mâu thuẫn so theo PMID, nên hai bản trích CÙNG một thử nghiệm
    cho HAI KẾT CỤC khác nhau bị gọi là "nói ngược nhau" (IMPACT: đợt cấp vs biến cố
    tim-phổi hậu kiểm). Đó là báo động giả thật.

    Nhưng cách vá bằng `difflib` trên tiêu đề thì đo được ngay là hỏng:
        22%  FIDELIO-DKD — finerenone…   ⟷  Finerenone ở CKD do ĐTĐ type 2…
        45%  JAKi ORAL Surveillance…     ⟷  Thận trọng JAK inhibitor…
        52%  DAPA-CKD — dapagliflozin…   ⟷  SGLT2i (dapagliflozin)…
    Cả ba là CÙNG MỘT khẳng định, chỉ khác cách diễn đạt — nhưng đều rơi dưới ngưỡng
    và BIẾN MẤT khỏi danh sách. Đổi báo động giả lấy BỎ SÓT là đánh đổi tệ hơn: bác
    sĩ không đi tìm thứ mình không biết là đang thiếu.

    Cách đúng: máy ĐO và TRÌNH BÀY (in cả hai tiêu đề cạnh nhau), người PHÁN ĐOÁN.
    Cùng bài học với bộ phân loại `design` ngày 13/08.

    Kiểm HÀNH VI: công cụ không được có ngưỡng tự phân loại, và phải in tiêu đề của
    CẢ HAI bản.
    """
    src = (REPO / "tools/dang_ky_chu_de.py").read_text(encoding="utf-8")
    if "NGUONG_CUNG_KHANG_DINH" in src or "SequenceMatcher" in src:
        return False, ("đã quay lại tự phân loại mâu thuẫn bằng độ giống từ vựng — "
                       "cách đó giấu mất mâu thuẫn thật (FIDELIO-DKD chỉ giống 22%)")
    if src.count("{c[3]}") < 1 or src.count("{m[3]}") < 1:
        return False, "không in đủ tiêu đề CẢ HAI bản — bác sĩ không tự phán đoán được"
    return True, "máy đo và trình bày; phán đoán ngữ nghĩa để cho bác sĩ"


def bh29_moi_ham_bh_deu_phai_duoc_dang_ky():
    """14/08 — một chốt được ĐỊNH NGHĨA nhưng KHÔNG ĐĂNG KÝ = mã chết, im lặng.

    Xảy ra thật ngay trong file này: một phiên Claude KHÁC đang làm song song đã
    thêm BH27 của riêng nó; lệnh chèn của tôi neo vào `("BH26"…)\n]` nên KHÔNG còn
    khớp, và **im lặng không chèn gì**. Hàm `bh28_*` vẫn được thêm vào file nhưng
    không nằm trong `BAI_HOC`, nên nó KHÔNG BAO GIỜ CHẠY — trong khi bảng vẫn xanh
    và trông như đã canh đủ.

    Cùng họ với BH16/BH22/BH23: thứ bị loại thầm lặng nguy hiểm hơn thứ báo lỗi.
    Ở đây nạn nhân chính là bộ chốt — nó tưởng mình canh 29 việc mà thực canh 28.

    Kiểm HÀNH VI: mọi hàm `bh*` định nghĩa trong module phải xuất hiện trong BAI_HOC.
    """
    import inspect as _ins
    mod = sys.modules[__name__]
    dinh_nghia = {ten for ten, _ in _ins.getmembers(mod, _ins.isfunction)
                  if ten.startswith("bh") and ten[2:4].isdigit()}
    da_dang_ky = {h.__name__ for _ma, _ng, _t, h in BAI_HOC}
    mo_coi = sorted(dinh_nghia - da_dang_ky)
    if mo_coi:
        return False, (f"{len(mo_coi)} chốt ĐỊNH NGHĨA mà KHÔNG đăng ký — không bao giờ "
                       f"chạy: {', '.join(mo_coi[:3])}")
    thua = sorted(da_dang_ky - dinh_nghia)
    if thua:
        return False, f"đăng ký hàm không tồn tại: {', '.join(thua[:3])}"
    return True, f"{len(dinh_nghia)} chốt đều được đăng ký và đều chạy"


def bh30_khoa_gom_nhom_phai_dinh_danh_duy_nhat():
    """14/08 — khoá gom nhóm bị TRÙNG thì nội dung bản này bị gán cho bản kia.

    Lỗi thật trong `tools/dang_ky_chu_de.py`: `tach_ten()` trả `m.group(2)` (TÊN
    CHỦ ĐỀ) ở đúng vị trí NGÀY — lệch một bậc sau khi thêm nhóm bắt tuỳ chọn cho
    file không có phần chủ đề. Phần dò mâu thuẫn khoá cache theo giá trị đó, nên
    3 bản `SuyTim_TongHop` (04/08 · 05/08 · 11/08) sập vào MỘT khoá: mọi phép so
    dính tới chúng đọc nhầm nội dung bản 11/08, và cặp 04/08⟷05/08 hoá thành so
    bản 11/08 với CHÍNH NÓ ⇒ vĩnh viễn 0 mâu thuẫn.

    Đã chứng minh bằng đột biến: cấy MỘT mâu thuẫn thật vào bản 04/08 thì bản lỗi
    báo 0, bản vá báo 1. Kho lúc đó tình cờ không có mâu thuẫn nào giữa các bản
    SuyTim nên con số tổng KHÔNG đổi — tức lỗi hoàn toàn vô hình nếu chỉ nhìn số.

    Ngày cũng KHÔNG đủ làm khoá: hai lát cắt khác nhau của cùng chủ đề có thể ra
    cùng ngày (RA_Than và RA_TimMach đều 30/06/2026). Khoá duy nhất là ĐƯỜNG DẪN.

    Cùng họ BH15/BH23: công cụ vẫn chạy, vẫn in một con số, nhưng con số đó không
    đo thứ nó tự nhận là đang đo.

    Kiểm HÀNH VI (không đếm chuỗi): dựng 2 bản cùng lát cắt khác ngày, cấy mâu
    thuẫn, đòi bộ dò phải bắt được.
    """
    import shutil as _sh
    import tempfile as _tmp
    dk = _nap(REPO / "tools" / "dang_ky_chu_de.py", "dk_bh30")
    dash = REPO / "EBM-Dashboards"
    goc = sorted(dash.glob("WebDashboard_*.html"))
    if len(goc) < 1:
        return False, "kho dashboard rỗng — không dựng được ca thử"
    vd = dk.nap_vd()
    mau = None
    for p in goc:
        blk = vd.extract_data_block(p.read_text(encoding="utf-8", errors="replace"))
        if not blk:
            continue
        for c in vd.split_items(blk):
            if vd.field(c, "pmid") and vd.field(c, "decision"):
                mau = (p, c)
                break
        if mau:
            break
    if not mau:
        return False, "không tìm được item có pmid+decision để dựng ca thử"

    p_goc, chunk = mau
    tmp = Path(_tmp.mkdtemp())
    try:
        # Hai bản CÙNG lát cắt, KHÁC ngày — đúng hình dạng đã gây lỗi.
        a = tmp / "WebDashboard_EBM_VanDeCuThe_ChotBH30_20260101.html"
        b = tmp / "WebDashboard_EBM_VanDeCuThe_ChotBH30_20260202.html"
        _sh.copy(p_goc, a)
        _sh.copy(p_goc, b)
        s = a.read_text(encoding="utf-8")
        cu = vd.field(chunk, "decision")
        moi_dec = "notyet" if cu != "notyet" else "apply"
        moi, n = re.subn(r'(decision\s*:\s*)["\'][a-z]+["\']',
                         rf'\1"{moi_dec}"', chunk, count=1)
        if n != 1:
            return False, "không cấy được mâu thuẫn vào chunk"
        a.write_text(s.replace(chunk, moi), encoding="utf-8")

        v, _lat, theo_goc = dk.quet_kho(tmp)
        mt, _ = dk.tim_mau_thuan(v, theo_goc)
        tong = sum(len(m["khac"]) for m in mt)
        if tong < 1:
            return False, ("cấy 1 mâu thuẫn giữa 2 bản cùng lát cắt mà bộ dò báo 0 — "
                           "khoá gom nhóm lại bị trùng")
        # và phải quy đúng cho bản đang đọc, không đảo chiều
        rieng = dk.mau_thuan_cua_ban(a)
        if not rieng or rieng[0]["quyet_dinh_minh"] != moi_dec:
            return False, ("mâu thuẫn quy sai chiều: bản đang đọc phải mang quyết định "
                           f"{moi_dec!r}, nhận {rieng[0]['quyet_dinh_minh'] if rieng else None!r}")
        return True, f"bắt được {tong} mâu thuẫn cấy vào và quy đúng chiều"
    finally:
        _sh.rmtree(tmp, ignore_errors=True)


def bh31_nguon_da_rut_phai_chan_duoc_o_cong():
    """14/08 — kết luận rút bài đã ghi trong sổ phải CHẶN được ở cổng phát hành.

    Lỗ hổng thật: `verify_dashboard.py` cố ý không tự kết luận trạng thái rút bài
    (đúng — không được suy ra từ nguồn metadata thiếu thẩm quyền), nhưng nó cũng
    không ĐỌC LẠI kết luận dương tính mà chuỗi 3 tầng đã xác nhận và ghi vào sổ.
    Hệ quả đo được: PMID 30267080 (JAMA Oncology, rút 2019, 'retract and replace')
    nằm trong ViemGanB_DieuTri và đi qua cổng SẠCH SẼ; nó chỉ hiện khi bác sĩ chủ
    động gõ `so_xac_minh_nguon.py --bao-cao`. Trang bản đọc cũng im lặng hoàn toàn.

    Ba hành vi bị khoá ở đây, mất cái nào cũng đủ tái tạo lỗ hổng:
      1. có bản ghi dương tính ⇒ vào `errors` (chặn), KHÔNG phải `warns`;
      2. sổ không có bản ghi ⇒ TUYỆT ĐỐI không ghi gì vào `oks` — im lặng của sổ
         có thể chỉ vì chưa ai quét file đó, biến nó thành dấu ✓ là dựng một lời
         bảo đảm mà dữ liệu không đỡ nổi (BH08/BH27);
      3. tra cứu hỏng ⇒ phải vào `warns` (lộ ra), không được bỏ qua im lặng.
    """
    vd = _nap(REPO / "EBM-Dashboards" / "tools" / "verify_dashboard.py", "vd_bh31")
    ham = getattr(vd, "kiem_nguon_da_rut", None)
    if ham is None:
        return False, "verify_dashboard.py không còn hàm kiem_nguon_da_rut — cổng rút bài đã mất"

    duong = [{"khoa": "pmid:1", "loai": "pmid", "gia_tri": "1", "tinh_trang": "retracted",
              "tieu_de": "ca thử", "kiem_luc": "2026-08-14", "nguon": "pubmed"}]
    e, w, o = [], [], []
    ham("x.html", e, w, o, tra_cuu=lambda _t: duong)
    if not e:
        return False, "nguồn ĐÃ RÚT không tạo lỗi cứng — cổng cho gói đi qua"
    if w or o:
        return False, "nguồn đã rút bị hạ xuống cảnh báo/ghi nhận thay vì chặn"

    e, w, o = [], [], []
    ham("x.html", e, w, o, tra_cuu=lambda _t: [])
    if o or e:
        return False, ("sổ im lặng mà cổng vẫn phát tín hiệu — 'chưa quét' đang bị đọc "
                       "thành 'đã kiểm, sạch'")

    def _hong(_t):
        raise RuntimeError("sổ hỏng")

    e, w, o = [], [], []
    ham("x.html", e, w, o, tra_cuu=_hong)
    if not w:
        return False, "tra cứu hỏng mà cổng im lặng — thất bại phải lộ ra"

    # ``Retraction and Replacement`` là trường hợp riêng: bài đã sửa vẫn là trích dẫn
    # hợp lệ. Chỉ được qua ở hàng rà khi dashboard khai đầy đủ provenance bản thay thế;
    # thiếu notice hoặc để apply vẫn phải bị chặn như nguồn rút thông thường.
    import tempfile as _tmp
    replacement = [{
        "khoa": "doi:10.1/replaced",
        "loai": "doi",
        "gia_tri": "10.1/replaced",
        "tinh_trang": "retracted",
        "tieu_de": "ca rút và đăng lại",
        "kiem_luc": "2026-08-14",
        "nguon": "crossref",
        "rut_va_thay": True,
        "thong_bao": "10.1/notice",
    }]
    with _tmp.TemporaryDirectory() as td:
        p = Path(td) / "replacement.html"
        decision_key = "deci" + "sion"
        p.write_text(
            ('''const DATA={items:[{id:"ITEM-01",doi:"10.1/replaced",pmid:"",
            replacesPmid:"123",replacementNoticePmid:"456",
            replacementNoticeDoi:"10.1/notice",dateVersion:"bản thay thế 2026",
            effectText:"số liệu của bản đã sửa",gradeSource:"Retraction and Replacement",
            flag:"bản thay thế",%s:"notyet",references:["10.1/notice"]}]};
            /* HẾT KHỐI DATA */''' % decision_key),
            encoding="utf-8",
        )
        e, w, o = [], [], []
        ham(str(p), e, w, o, tra_cuu=lambda _t: replacement)
        if e or not any("hàng bác sĩ rà" in msg for msg in w):
            return False, "bản thay thế khai đủ vẫn không qua được hàng rà fail-closed"
        unsafe = p.read_text(encoding="utf-8").replace(
            f'{decision_key}:"notyet"', f'{decision_key}:"apply"'
        )
        p.write_text(unsafe, encoding="utf-8")
        e, w, o = [], [], []
        ham(str(p), e, w, o, tra_cuu=lambda _t: replacement)
        if not e:
            return False, "bản thay thế để apply vẫn lọt qua cổng rút bài"
    return True, (
        "chặn khi dương tính · bản thay thế chỉ qua ở notyet khi đủ provenance · "
        "không tự khen khi im lặng · lộ ra khi hỏng"
    )


def bh32_chi_so_gop_khong_duoc_ket_luan_cho_ca_tap():
    """14/08 — `max(ngày)` bị trình bày thành kết luận về TOÀN BỘ kho.

    `kiem_do_tuoi_chung_cu.py` lấy gói mới nhất trên toàn kho rồi in
    "🟢 CHỨNG CỨ còn hạn". Nghĩa thật của dòng đó chỉ là "có ít nhất MỘT gói mới".
    Đo 14/08/2026: gói mới nhất 1 ngày tuổi ⇒ 🟢, trong khi 37/59 chủ đề đã quá 35
    ngày và trung vị là 45 ngày. Bác sĩ đọc dòng đó sẽ tin mọi chủ đề đều vừa được rà.

    Cùng họ BH15/BH30 — con số không đo thứ nó tự nhận là đang đo — nhưng ở đây hại
    theo hướng ngược lại: không phải báo động giả mà là YÊN TÂM GIẢ.

    Kiểm HÀNH VI: dựng kho giả có 1 gói mới + 1 gói rất cũ, đòi công cụ phải trả tuổi
    THEO TỪNG chủ đề và thấy được gói cũ — chứ không chỉ thấy gói mới nhất.
    """
    import datetime as _dt
    import shutil as _sh
    import tempfile as _tmp
    kt = _nap(REPO / "tools" / "kiem_do_tuoi_chung_cu.py", "kt_bh32")
    if not hasattr(kt, "lau_chua_xem_lai"):
        return False, "mất hàm lau_chua_xem_lai — độ tươi lại chỉ còn nhìn gói mới nhất"
    tmp = Path(_tmp.mkdtemp())
    goc = kt.DASH
    try:
        hn = _dt.date.today()
        (tmp / f"WebDashboard_EBM_VanDeCuThe_ChuDeMoi_{hn:%Y%m%d}.html").write_text("x")
        cu = hn - _dt.timedelta(days=200)
        (tmp / f"WebDashboard_EBM_VanDeCuThe_ChuDeCu_{cu:%Y%m%d}.html").write_text("x")
        kt.DASH = tmp
        ra = kt.lau_chua_xem_lai()
        if len(ra) != 2:
            return False, f"đếm theo chủ đề sai: nhận {len(ra)} chủ đề, cần 2"
        if ra[0][0] != "ChuDeCu" or ra[0][1] < 190:
            return False, f"không xếp chủ đề cũ lên đầu: {ra[0]}"
        if not any(t > kt.HAN_RAT_LAU_NGAY for _k, t in ra):
            return False, "chủ đề 200 ngày không vượt ngưỡng rất-lâu — cảnh báo sẽ câm"
        if all(t > kt.HAN_RAT_LAU_NGAY for _k, t in ra):
            return False, "gói mới cũng bị tính là rất lâu — sẽ báo động giả"
        return True, f"đo được tuổi từng chủ đề: cũ nhất {ra[0][1]} ngày, mới nhất {ra[-1][1]}"
    finally:
        kt.DASH = goc
        _sh.rmtree(tmp, ignore_errors=True)


def bh33_kiem_rut_bai_phai_phu_moi_kieu_dinh_danh():
    """14/08 — kiểm rút bài chỉ phủ PMID, nên đổi sang trích DOI là thoát cổng.

    Chuỗi 3 tầng dựng cùng ngày chỉ nhận PMID ⇒ **540 DOI trong kho CHƯA TỪNG được
    kiểm rút bài lần nào** (gần một nửa số định danh), mà `con_hieu_luc()` vẫn xếp
    chúng vào nhóm "còn hiệu lực" — một lời bảo đảm rỗng.

    Điểm mù bị chạm vào THẬT trong cùng ngày: một mục trích PMID 30267080 (đã rút)
    được sửa thành trích DOI `10.1001/jamaoncol.2018.4070`; tra Crossref thì DOI đó
    CHÍNH LÀ bài đã rút (`updated-by: retraction → 10.1001/jamaoncol.2019.0576`).
    Cổng thôi cảnh báo trong khi rủi ro còn nguyên — đèn đỏ tắt mà nguy cơ không mất,
    nguy hiểm hơn hẳn chưa từng có đèn.

    Cùng lý lẽ BH24 (DOI ghi dạng URL vẫn là DOI): **một định danh mang bảo đảm nào
    thì phải chịu đúng phép kiểm của bảo đảm đó, bất kể nó được ghi bằng kiểu gì.**

    Kiểm HÀNH VI: bản ghi DOI thiếu dấu vết kiểm rút bài KHÔNG được coi là còn hiệu lực.
    """
    sx = _nap(REPO / "tools" / "so_xac_minh_nguon.py", "sx_bh33")
    moi = __import__("datetime").datetime.now().isoformat(timespec="seconds")
    ca = [
        ({"loai": "doi", "gia_tri": "10.x/y", "xac_minh_luc": moi},
         False, "DOI chưa kiểm rút bài mà vẫn được coi là còn hiệu lực"),
        ({"loai": "url", "gia_tri": "https://doi.org/10.x/y", "doi_rut_tu_url": "10.x/y",
          "xac_minh_luc": moi},
         False, "DOI ghi dạng URL chưa kiểm rút bài mà vẫn còn hiệu lực"),
        ({"loai": "doi", "gia_tri": "10.x/y", "xac_minh_luc": moi, "kiem_rut_luc": moi},
         True, "DOI đã kiểm rút bài mà bị coi là hết hiệu lực (báo động giả)"),
        ({"loai": "url", "gia_tri": "https://nice.org.uk/ng28", "xac_minh_luc": moi},
         True, "URL thuần (không phải DOI) bị đòi kiểm rút bài — báo động giả"),
    ]
    for ban_ghi, mong, thong_diep in ca:
        con, _ly_do = sx.con_hieu_luc(ban_ghi)
        if con is not mong:
            return False, thong_diep
    if not hasattr(sx, "kiem_rut_bai_theo_doi"):
        return False, "mất kiem_rut_bai_theo_doi — DOI lại không có đường nào được kiểm"
    return True, "DOI (kể cả ghi dạng URL) phải có dấu vết kiểm rút bài; URL thuần thì không"


def bh34_canh_bao_phai_noi_dung_muc():
    """14/08 — gộp "rút bỏ hẳn" với "rút rồi ĐĂNG LẠI bản đã sửa" là cảnh báo SAI.

    Ca thật: PMID 30267080 / doi:10.1001/jamaoncol.2018.4070 (Choi và cs., JAMA
    Oncology). Retraction Watch ghi `reason = "Error in Data;Retract and Replace;"`,
    Crossref trỏ thông báo có tiêu đề "Notice of Retraction **and Replacement**", và
    PubMed **KHÔNG** gắn publication type 'Retracted Publication', **không** có dòng
    'RIN' — vì bản đã sửa được đăng lại ở CÙNG DOI/PMID.

    Nói "ĐÃ BỊ RÚT — không dùng kết luận" về một trích dẫn như vậy là **nói sai về
    một nguồn hợp lệ**. Việc cần làm khác hẳn: đối chiếu SỐ LIỆU với bản đã sửa, chứ
    không phải bỏ mục đi. Và mỗi cảnh báo sai lại dạy người đọc bỏ qua cảnh báo — thứ
    đã ghi nhiều lần trong kho này là tệ hơn không cảnh báo.

    Vẫn giữ status 'retracted' để cổng còn CHẶN (fail-closed); chỉ CÂU CHỮ đổi.

    Kiểm HÀNH VI: bản ghi mang cờ rút-và-thay phải sinh thông điệp khác hẳn bản ghi
    rút bỏ hẳn, và cả hai đều phải là LỖI CỨNG.
    """
    mea = REPO / "medical-ebm-automation"
    if str(mea) not in sys.path:
        sys.path.insert(0, str(mea))  # module dùng `from app.utils...`
    cr = _nap(mea / "app" / "sources" / "crossref_retraction.py", "cr_bh34")
    if not cr.la_rut_va_thay("Notice of Retraction and Replacement. Choi et al."):
        return False, "không nhận ra tiêu đề thông báo dạng rút-và-thay"
    if not cr.la_rut_va_thay("Error in Data;Retract and Replace;"):
        return False, "không nhận ra lý do Retraction Watch dạng rút-và-thay"
    if cr.la_rut_va_thay("Retraction: Fabricated data"):
        return False, "nhận nhầm một bài RÚT BỎ HẲN thành rút-và-thay — hạ mức cảnh báo sai"

    vd = _nap(REPO / "EBM-Dashboards" / "tools" / "verify_dashboard.py", "vd_bh34")
    nen = {"khoa": "doi:x", "loai": "doi", "gia_tri": "10.x/y", "tinh_trang": "retracted",
           "tieu_de": "t", "kiem_luc": "2026-08-14", "nguon": "crossref", "thong_bao": "10.x/z"}
    e1, w1, o1 = [], [], []
    vd.kiem_nguon_da_rut("a.html", e1, w1, o1, tra_cuu=lambda _t: [dict(nen, rut_va_thay=True)])
    e2, w2, o2 = [], [], []
    vd.kiem_nguon_da_rut("a.html", e2, w2, o2, tra_cuu=lambda _t: [dict(nen, rut_va_thay=False)])
    if not e1 or not e2:
        return False, "một trong hai mức không còn là lỗi cứng — cổng hết fail-closed"
    if e1[0] == e2[0]:
        return False, "hai mức sinh CÙNG một thông điệp — cảnh báo nói sai về trích dẫn hợp lệ"
    if "ĐĂNG LẠI" not in e1[0]:
        return False, "mức rút-và-thay không nói rõ là bản đã được đăng lại"
    if "không dùng kết luận" not in e2[0]:
        return False, "mức rút bỏ hẳn không còn nói rõ là không được dùng"
    return True, "hai mức nói khác nhau, cả hai vẫn chặn"


def bh35_khai_chua_biet_khong_duoc_tat_luat_an_toan():
    """14/08 — cho phép khai "chưa ghi nhận provenance", nhưng KHÔNG được tắt luật an toàn.

    44/62 gói không có khối `DATA.standards`, rải đều 06→08/2026. Trước đây chúng sinh
    10 lỗi cứng GIỐNG HỆT một gói lẽ ra phải có mà cố tình bỏ ⇒ cổng không phân biệt
    **chưa khai** với **có vấn đề** (BH08), và một bức tường 10 lỗi × 44 gói dạy người
    đọc bỏ qua màu đỏ.

    Nay gói được khai `provenanceUnknown: true` + lý do. Nhưng miễn trừ này CHỈ được
    bỏ phần đòi từng trường của hợp đồng nguồn — **mọi luật an toàn cấp item vẫn phải
    chạy**. Nếu nó tắt luôn luật item thì đây thành đường lách rộng hơn cả lỗi `return`
    sớm ngày 12/08, vốn đã che 73 mục nguy hiểm.

    Kiểm HÀNH VI: gói khai provenanceUnknown mà có `apply` trên chứng cứ yếu ⇒ VẪN CHẶN.
    Và khai mà KHÔNG nêu lý do ⇒ lỗi cứng (miễn trừ phải có người chịu trách nhiệm).
    """
    vd = _nap(REPO / "EBM-Dashboards" / "tools" / "verify_dashboard.py", "vd_bh35")
    khoi = ('const DATA = {standards:{provenanceUnknown:true,'
            'provenanceUnknownLyDo:"bản cũ, không dựng lại được"},'
            'items:[{id:"ITEM-01",pmid:"1",design:"RCT",gradeLevel:"low",'
            'decision:"apply",gradeSource:"x"}]}')
    items = vd.split_items(khoi)
    if not items:
        return False, "không tách được item trong ca thử"
    e, w, _o = vd.strict_source_checks(khoi, items)
    if not any("gradeLevel" in x and "apply" in x for x in e):
        return False, ("gói khai provenanceUnknown mà luật an toàn cấp item KHÔNG chạy — "
                       "miễn trừ đã thành đường lách")
    if any("standards thiếu" in x for x in e):
        return False, "vẫn đòi từng trường hợp đồng nguồn — bức tường đỏ chưa được gỡ"
    if not any("PROVENANCE CHƯA GHI NHẬN" in x for x in w):
        return False, "không nói ra rằng gói này không tái lập/kiểm toán được"

    thieu_ly_do = khoi.replace(',provenanceUnknownLyDo:"bản cũ, không dựng lại được"', "")
    e2, _w2, _o2 = vd.strict_source_checks(thieu_ly_do, vd.split_items(thieu_ly_do))
    if not any("provenanceUnknownLyDo" in x for x in e2):
        return False, "khai miễn trừ mà không cần nêu lý do — miễn trừ vô danh"
    return True, "miễn trừ chỉ bỏ phần hợp đồng nguồn; luật an toàn item vẫn chặn"


def bh36_grade_phai_khai_ai_cham():
    """14/08 — `gradeLevel` không truy được về tổ chức nào đã chấm.

    Đo toàn kho: 530 item có gradeLevel khác 'na', **249 (47%) không truy được**; 128
    lấy MÔ TẢ THIẾT KẾ làm lý do ("RCT đa trung tâm, mù đôi" ⇒ high), và **56 mục tự
    khai thẳng "nguồn không cung cấp phân hạng" mà VẪN mang mức** — vi phạm chính
    DESIGN-SPEC §6 của dự án. 56 mục đó đã đưa về 'na' ngày 14/08.

    `gradeLevel` là thứ bác sĩ HÀNH ĐỘNG THEO, nên mức không truy được nguồn gây hại ở
    MỌI lần đọc — khác rút bài vốn hiếm.

    Luật: mọi `gradeLevel` khác 'na' phải khai `gradeBy` (ai đã chấm). Hiện ở mức CẢNH
    BÁO — "chưa khai" không đồng nghĩa "mức sai", và chặn cứng 256 mục sẽ lại là biến
    chưa-biết thành có-vấn-đề (BH08). Chuyển thành lỗi cứng khi `kiem_phan_hang.py` về 0.

    Kiểm HÀNH VI: thiếu `gradeBy` phải LỘ RA; có `gradeBy` thì im.
    """
    vd = _nap(REPO / "EBM-Dashboards" / "tools" / "verify_dashboard.py", "vd_bh36")
    nen = ('const DATA = {standards:{provenanceUnknown:true,provenanceUnknownLyDo:"x"},'
           'items:[{id:"ITEM-01",pmid:"1",design:"RCT",gradeLevel:"high",'
           'decision:"consider",gradeSource:"RCT đa trung tâm"%s}]}')
    thieu = nen % ""
    e1, w1, _ = vd.strict_source_checks(thieu, vd.split_items(thieu))
    if not any("gradeBy" in x for x in (w1 + e1)):
        return False, "thiếu `gradeBy` mà cổng im lặng — mức chứng cứ không ai truy được"
    co = nen % ',gradeBy:"Cochrane (GRADE)"'
    e2, w2, _ = vd.strict_source_checks(co, vd.split_items(co))
    if any("gradeBy" in x for x in (w2 + e2)):
        return False, "đã khai `gradeBy` mà vẫn báo thiếu — báo động giả"
    return True, "thiếu gradeBy thì lộ ra, khai rồi thì im"


def bh37_ung_vien_phai_mang_do_tin_cay_ngay_luc_nhan():
    """14/08 — khâu THU THẬP chưa bao giờ hỏi "bài này có đáng tin không".

    Chuỗi 3 tầng kiểm rút bài tồn tại từ trước, nhưng chỉ được gọi khi rà kho CŨ. Đo
    trong `surveillance_scan.py`: **0 lần** kiểm rút bài · 0 lần đọc publication type ·
    0 lần đối chiếu kho. Ứng viên tới tay bác sĩ chỉ mang tiêu đề · tạp chí · ngày ·
    một nhãn "authority" SUY TỪ TÊN TẠP CHÍ — thứ trông như bảo đảm chất lượng nhưng
    không phải. Nghĩa là "mới nhất" và "tin cậy nhất" chưa bao giờ đi cùng nhau tại
    đúng chỗ chứng cứ đi vào hệ.

    Hệ quả cụ thể: một bài ĐÃ BỊ RÚT vẫn có thể vào thẳng hàng ứng viên trình bác sĩ.

    Kiểm HÀNH VI: `gan_do_tin_cay()` phải gắn đủ 4 trường, và khi không kiểm được rút
    bài thì để `chua_kiem` — TUYỆT ĐỐI không mặc định 'ok' (BH08/BH27/BH31).
    """
    ss = _nap(REPO / "EBM-Dashboards" / "tools" / "surveillance_scan.py", "ss_bh37")
    for ten in ("gan_do_tin_cay", "_pmid_da_co_trong_kho"):
        if not hasattr(ss, ten):
            return False, f"mất {ten} — khâu nhận lại không gắn độ tin cậy"
    c = ss.Candidate(pmid="0", publication_date="2026", title="t", url="u")
    for truong in ("rut_bai", "da_co_trong_kho", "pubtype", "chua_binh_duyet"):
        if not hasattr(c, truong):
            return False, f"Candidate mất trường {truong}"
    if c.rut_bai != "chua_kiem":
        return False, (f"mặc định rut_bai={c.rut_bai!r} — chưa kiểm PHẢI là 'chua_kiem', "
                       "không được mặc định thành 'ok'")
    # PMID không tồn tại: chuỗi không kết luận được ⇒ phải giữ 'chua_kiem', không thành 'ok'
    ra = ss.gan_do_tin_cay([c])
    if not ra or ra[0].rut_bai == "ok":
        return False, "PMID không tra được mà vẫn gắn 'ok' — im lặng thành lời bảo đảm"
    # Nhãn phải HIỆN trong báo cáo, nằm trong JSON mà không in ra thì coi như không có.
    import dataclasses as _dc
    bc = {"days": 1, "status": "PASS", "successful_topics": 1, "failed_topics": 0,
          "candidate_count": 1, "disclaimer": "x",
          "topics": [{"topic": "T", "query": "q", "status": "PASS", "error": "",
                      "candidates": [_dc.asdict(_dc.replace(c, rut_bai="retracted"))]}]}
    md = ss.markdown_report(bc)
    if "ĐÃ BỊ RÚT" not in md:
        return False, "ứng viên đã bị rút mà báo cáo KHÔNG nói ra"
    return True, "ứng viên mang rút bài · loại thiết kế · trùng kho · preprint, và nhãn có in ra"


def bh38_khong_loc_bo_cai_moi_nhat_o_khau_tim():
    """14/08 — bộ lọc `[ptyp]` ở khâu TÌM KIẾM vứt đi chính thứ mới nhất.

    Publication type do MEDLINE gán TRONG LÚC lập chỉ mục — việc xảy ra hàng tuần đến
    hàng tháng SAU khi bài vào PubMed. Lọc theo nó lúc tìm kiếm nghĩa là chỉ thấy thứ
    đã đánh chỉ mục xong, tức là thứ KHÔNG còn mới.

    Đo thật 14/08/2026, 40 bài mới vào PubMed 45 ngày (chủ đề suy tim): **30 bài chưa
    được gán loại nào ngoài "Journal Article"**, trong đó có PMID 42552200 —
    *"Prevalence of orthostatic hypotension in heart failure: a systematic review"* —
    một tổng quan hệ thống bị vứt chỉ vì chưa kịp đánh chỉ mục.
    Đếm theo chủ đề (45 ngày, `edat`): CÓ lọc 1 · 8 · 0 — KHÔNG lọc 46 · 49 · 22.
    Riêng CKD trả **0** trong khi thực có 22 bản ghi mới, và "0 ứng viên" bị đọc thành
    "không có gì mới" — biến KHÔNG BIẾT thành SỰ THẬT (BH08).

    Luật: loại thiết kế dùng để **GẮN NHÃN và XẾP HẠNG**, KHÔNG dùng để loại bỏ ở khâu
    tìm. Phải luôn còn một tầng đi bằng `edat` và không lọc.

    Kiểm HÀNH VI: watchlist phải có tầng không-lọc, và `search()` phải tôn trọng cờ đó.
    """
    import json as _json
    ss = _nap(REPO / "EBM-Dashboards" / "tools" / "surveillance_scan.py", "ss_bh38")
    wl = REPO / "EBM-Dashboards" / "watchlist.json"
    if not wl.exists():
        return False, "không thấy watchlist.json"
    tp = _json.loads(wl.read_text(encoding="utf-8")).get("topics", [])
    co_tang = [t for t in tp if any(q.get("loc_thiet_ke") is False
                                    for q in (t.get("queries") or []))]
    if not co_tang:
        return False, ("KHÔNG chủ đề nào có tầng không-lọc — hệ chỉ còn thấy tài liệu đã "
                       "đánh chỉ mục xong, tức thứ không còn mới")

    # `search()` phải thực sự bỏ bộ lọc khi được yêu cầu, và dùng đúng datetype.
    ghi: dict[str, str] = {}

    def gia_fetch(url):
        ghi["url"] = url
        return {"esearchresult": {"idlist": []}}

    ss.search("abc", 30, 5, fetch_json=gia_fetch, datetype="edat", loc_thiet_ke=False)
    u1 = ghi.get("url", "")
    if "ptyp" in u1:
        return False, "yêu cầu bỏ lọc mà truy vấn vẫn mang [ptyp] — cái mới vẫn bị vứt"
    if "edat" not in u1:
        return False, "không dùng edat — vẫn hỏi theo ngày công bố, bỏ sót bài mới vào PubMed"
    ss.search("abc", 30, 5, fetch_json=gia_fetch)
    if "ptyp" not in ghi.get("url", ""):
        return False, "chế độ mặc định mất bộ lọc — 3 tầng có thứ bậc hoá ra không lọc gì"
    return True, f"{len(co_tang)} chủ đề có tầng không-lọc; search() tôn trọng cả hai chế độ"


def bh39_doctrine_khong_duoc_troi_sau_cong():
    """14/08 — cổng bắt buộc một trường mà KHÔNG agent nào biết trường đó tồn tại.

    Đo ngày 14/08/2026 trên 84 file trong `.claude/agents/`:
      • `normativeBasis` — cổng bắt buộc từ **12/08**, doctrine nhắc: **0 agent**
      • `gradeBy` — cổng bắt buộc từ 14/08, doctrine nhắc: **0 agent**
      • 8 công cụ chứng cứ lâm sàng (sổ xác minh · chuỗi rút bài · dò vượt qua · phân
        hạng · con số · đăng ký chủ đề · chu trình · phủ giám sát): **0 agent** gọi tên
    Trong khi tuyến NGHIÊN CỨU đã nối dây đầy đủ (`gen_research_docx.py` 73 lượt nhắc,
    `approve_gate.py` 8, `gate_contract.py` 6).

    Hệ quả: agent dựng ra một gói đúng theo doctrine, rồi bị cổng chặn vì một luật nó
    chưa từng được cho biết. Người đọc thấy "cổng chặn" và tưởng nội dung sai, trong khi
    lỗi thật là hai tầng nói hai thứ khác nhau. Nặng hơn: `tra-cuu-chung-cu` có dặn tự hỏi
    *"bài có bị rút không?"* mà KHÔNG đưa công cụ nào — tức bảo mô hình trả lời bằng trí
    nhớ về một sự kiện có thể xảy ra sau ngày cắt kiến thức. Ca thật PMID 30267080: cả
    PubMed lẫn Europe PMC đều trả `ok`, chỉ nền Retraction Watch bắt được.

    Kiểm HÀNH VI: mọi trường mà cổng ĐANG bắt buộc phải xuất hiện trong ít nhất một
    doctrine agent. Thêm luật ở cổng thì phải dạy agent — nếu không, chốt này đỏ.
    """
    cong = (REPO / "EBM-Dashboards" / "tools" / "verify_dashboard.py")
    thu_muc = REPO / ".claude" / "agents"
    if not cong.exists() or not thu_muc.is_dir():
        return False, "không thấy cổng hoặc thư mục agent"
    van_cong = cong.read_text(encoding="utf-8", errors="replace")
    # Trường mà cổng thực sự đọc từ item và có thể sinh lỗi/cảnh báo.
    truong = [t for t in ("normativeBasis", "gradeBy", "provenanceUnknown")
              if f'"{t}"' in van_cong or f"'{t}'" in van_cong]
    if not truong:
        return False, "không dò được trường nào cổng đang bắt buộc — chốt mất hiệu lực"
    van_agent = "\n".join(
        p.read_text(encoding="utf-8", errors="replace") for p in thu_muc.glob("*.md"))
    thieu = [t for t in truong if t not in van_agent]
    if thieu:
        return False, (f"cổng bắt buộc {', '.join(thieu)} mà KHÔNG doctrine agent nào nhắc — "
                       "agent sẽ bị chặn vì luật nó chưa từng được cho biết")
    # Và câu "bài có bị rút không" phải đi kèm CÔNG CỤ, không để mô hình tự nhớ.
    tra = thu_muc / "tra-cuu-chung-cu.md"
    if tra.exists():
        vb = tra.read_text(encoding="utf-8", errors="replace")
        if "retract" in vb.lower() and "check_citation_retraction" not in vb:
            return False, ("tra-cuu-chung-cu hỏi 'bài có bị rút không' mà không đưa công cụ "
                           "— buộc mô hình trả lời bằng trí nhớ về sự kiện sau ngày cắt")
    return True, f"{len(truong)} trường cổng bắt buộc đều có trong doctrine agent"


def bh40_luat_toan_doi_phai_lan_duoc_xuong_moi_agent():
    """14/08 — có luật chung cho cả đội nhưng KHÔNG có đường lan xuống 50 agent.

    `enforce_agent_guardrails.py` cấy một khối chung vào mọi agent, nhưng `_refresh()`
    chỉ biết **đúng MỘT cặp thay thế viết cứng**. Muốn thêm một luật cho toàn đội thì
    phải sửa chính cơ chế — nên trên thực tế không ai thêm, và doctrine cứ trôi tụt sau
    cổng (BH39). Đo trước khi vá: luật "phải TRA rút bài, không được tự nhớ" có ở
    **0/50** agent; sau khi vá: **50/50**.

    Nay `THAY_THE` là một DANH SÁCH cặp: thêm luật = thêm một dòng, chạy `--refresh`.

    Kiểm HÀNH VI: (a) cơ chế phải nhận nhiều cặp; (b) luật rút bài phải có mặt ở MỌI
    agent — thiếu một file cũng là một agent trả lời bằng trí nhớ về chuyện sau ngày cắt.
    """
    e = _nap(REPO / "tools" / "enforce_agent_guardrails.py", "eag_bh40")
    if not isinstance(getattr(e, "THAY_THE", None), list) or len(e.THAY_THE) < 2:
        return False, ("cơ chế refresh lại chỉ nhận một cặp cứng — thêm luật cho toàn đội "
                       "sẽ phải sửa chính cơ chế, và vì thế sẽ không ai thêm")
    if "check_citation_retraction" not in e.BLOCK:
        return False, "khối chung mất luật kiểm rút bài — agent mới cấy sẽ không có"
    thu_muc = REPO / ".claude" / "agents"
    ds = [p for p in thu_muc.glob("*.md") if not p.name.startswith("_")
          and p.name not in ("README.md",)]
    thieu = [p.name for p in ds
             if e.MARKER in p.read_text(encoding="utf-8", errors="replace")
             and "check_citation_retraction" not in p.read_text(encoding="utf-8", errors="replace")]
    if thieu:
        return False, (f"{len(thieu)} agent thiếu luật kiểm rút bài (vd {thieu[0]}) — "
                       "sẽ trả lời bằng trí nhớ về một sự kiện có thể sau ngày cắt")
    return True, f"{len(e.THAY_THE)} cặp lan được; {len(ds)} agent đều có luật kiểm rút bài"


def bh41_cong_cu_chung_cu_khong_duoc_mo_coi():
    """14/08 — 8 công cụ chứng cứ lâm sàng tồn tại mà KHÔNG agent nào gọi tên.

    Đo trước khi vá, trên 84 file `.claude/agents/`: sổ xác minh nguồn · chuỗi rút bài ·
    dò chứng cứ vượt qua · phân hạng · kiểm con số · đăng ký chủ đề · chu trình · phủ
    giám sát — **0 agent** nhắc tới cái nào. Trong khi tuyến NGHIÊN CỨU nối dây đầy đủ
    (`gen_research_docx.py` 73 lượt, `approve_gate.py` 8, `gate_contract.py` 6).

    Một công cụ không agent nào gọi thì với dây chuyền hằng ngày nó **không tồn tại** —
    dù nó chạy đúng và có test. Đây là cách công sức âm thầm bốc hơi: viết xong, chạy
    được một lần, rồi không bao giờ được gọi lại.

    Kiểm HÀNH VI: mỗi công cụ chứng cứ lâm sàng phải được ÍT NHẤT một agent gọi tên.
    Thêm công cụ mới mà quên dạy agent ⇒ chốt này đỏ.
    """
    thu_muc = REPO / ".claude" / "agents"
    if not thu_muc.is_dir():
        return False, "không thấy thư mục agent"
    # Công cụ thuộc dây chuyền CHỨNG CỨ LÂM SÀNG (không tính tuyến nghiên cứu G0-G10).
    CONG_CU = ("check_citation_retraction", "so_xac_minh_nguon", "kiem_chung_cu_vuot_qua",
               "kiem_phan_hang", "kiem_so_lieu", "dang_ky_chu_de", "chu_trinh_chung_cu",
               "kiem_phu_giam_sat", "uu_tien_cap_nhat")
    van = "\n".join(p.read_text(encoding="utf-8", errors="replace")
                    for p in thu_muc.glob("*.md"))
    mo_coi = [t for t in CONG_CU
              if (REPO / "tools" / f"{t}.py").exists()
              or (REPO / "medical-ebm-automation" / "tools" / f"{t}.py").exists()]
    mo_coi = [t for t in mo_coi if t not in van]
    if mo_coi:
        return False, (f"{len(mo_coi)} công cụ chứng cứ KHÔNG agent nào gọi tên "
                       f"({', '.join(mo_coi[:3])}) — với dây chuyền hằng ngày chúng không tồn tại")
    return True, f"{len(CONG_CU)} công cụ chứng cứ đều có agent gọi"


def bh42_guideline_khong_duoc_tin_theo_thuong_hieu():
    """14/08 — hệ hút guideline về rồi tin theo TÊN TỔ CHỨC, không có công cụ thẩm định.

    Đo trên 84 file `.claude/agents/`: **AGREE II xuất hiện ở đúng 1 file — và đó là
    rubric QA nội bộ, không phải agent thẩm định**. Trong khi `cap-nhat-guideline` nhắc
    "guideline" 16 lần, `huong-dan-lam-sang` 19 lần, `tra-cuu-chung-cu` 13 lần — không
    agent nào cầm công cụ đo chất lượng guideline.

    Nguy hiểm hơn kể từ 14/08: watchlist vừa mở 4 kênh gọi thẳng tên Cochrane · NICE ·
    USPSTF · WHO, nên hệ hút về NHIỀU guideline hơn, tất cả đều "có thương hiệu".
    Một khuyến cáo của hiệp hội lớn nhưng **Miền 3 (Rigour of Development)** yếu thì bản
    chất là đồng thuận chuyên gia có logo — đúng thứ `design:'Consensus'` mô tả, và
    Consensus KHÔNG BAO GIỜ đủ để miễn trừ quy phạm (BH03).

    Bốn chuẩn quốc tế khác cũng ở mức 0 agent trước ngày này: RIGHT (báo cáo khuyến cáo
    do chính mình đưa ra) · PRISMA-S (báo cáo chiến lược tìm — 44/62 gói chưa từng ghi) ·
    ROBIS (sai lệch của chính tổng quan) · CERQual (chứng cứ định tính).

    Kiểm HÀNH VI: mỗi chuẩn phải có ít nhất một agent cầm, VÀ định danh trích kèm phải
    đúng bài phương pháp gốc — trích nhầm bài ÁP DỤNG thành bài chuẩn là lỗi trích dẫn.
    """
    thu_muc = REPO / ".claude" / "agents"
    if not thu_muc.is_dir():
        return False, "không thấy thư mục agent"
    van = {p.name: p.read_text(encoding="utf-8", errors="replace")
           for p in thu_muc.glob("*.md")}
    gop = "\n".join(van.values())
    # (chuẩn, PMID bài PHƯƠNG PHÁP GỐC — đã tra PubMed 14/08/2026, không lấy từ trí nhớ)
    CHUAN = (("AGREE II", "20656455"), ("RIGHT", "27893062"), ("PRISMA-S", "34285662"),
             ("CERQual", "26506244"), ("ROBIS", "26092286"))
    thieu = [t for t, _ in CHUAN if t not in gop]
    if thieu:
        return False, (f"{len(thieu)} chuẩn quốc tế không agent nào cầm: {', '.join(thieu)}")
    sai_pmid = [t for t, pm in CHUAN if pm not in gop]
    if sai_pmid:
        return False, (f"chuẩn {', '.join(sai_pmid)} được nhắc nhưng THIẾU PMID bài phương "
                       "pháp gốc — trích tên chuẩn mà không truy được nguồn")
    # AGREE II phải nằm ở agent TIÊU THỤ guideline, không chỉ ở rubric nội bộ.
    tieu_thu = [t for t in ("cap-nhat-guideline.md", "huong-dan-lam-sang.md")
                if t in van and "AGREE II" not in van[t]]
    if tieu_thu:
        return False, (f"agent tiêu thụ guideline thiếu AGREE II: {', '.join(tieu_thu)} — "
                       "hệ lại tin guideline theo thương hiệu")
    return True, f"{len(CHUAN)} chuẩn đều có agent cầm, kèm PMID bài gốc"


def bh43_canary_dau_cuoi_phai_chay_va_phai_bat_duoc():
    """14/08 — mọi chốt BH01–BH42 kiểm CHỮ TRONG FILE, không cái nào kiểm dây chuyền CHẠY.

    Khoảng cách này không lý thuyết. Riêng ngày 14/08 tìm được ba ca mà luật CÓ MẶT nhưng
    KHÔNG BAO GIỜ chạy tới: `return` sớm khi thiếu `DATA.standards` (che 73 mục nguy hiểm
    trên 47 dashboard) · bộ lọc `[ptyp]` ở khâu tìm (22 chủ đề báo "0 ứng viên" trong khi
    có chứng cứ mới) · 8 công cụ chứng cứ mà 0 agent gọi.

    `tools/thu_dau_cuoi_chung_cu.py` gài lỗi ĐÃ BIẾT vào một gói GIẢ rồi đòi dây chuyền
    bắt được — 8 phép thử, gồm cả hai nhánh của luật `apply` + `gradeLevel:'na'` (nhánh
    nghiên cứu thường và nhánh văn bản quy phạm). Chính bản đầu của canary đã kỳ vọng
    NHẦM nhánh, và cổng mới là bên đúng — đúng giá trị của một phép thử có đáp án biết trước.

    Kiểm HÀNH VI: canary phải tồn tại VÀ chạy xanh. Canary đỏ ⇒ có lỗ hổng THẬT ở dây
    chuyền, không phải chuyện câu chữ.
    """
    import subprocess
    tp = REPO / "tools" / "thu_dau_cuoi_chung_cu.py"
    if not tp.exists():
        return False, "mất canary đầu-cuối — không còn gì chứng minh dây chuyền CHẠY đúng"
    r = subprocess.run([sys.executable, str(tp)], capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        dong = [d.strip() for d in (r.stdout or "").splitlines() if d.strip().startswith("✗")]
        return False, ("canary ĐỎ — lỗ hổng thật ở dây chuyền: "
                       + (dong[0][:150] if dong else "xem `python tools/thu_dau_cuoi_chung_cu.py`"))
    so = (r.stdout or "").count("  ✓ ")
    return True, f"canary xanh {so}/{so} phép thử gài lỗi"


def bh44_dieu_phoi_agent_phai_sach():
    """15/08 — tầng ĐIỀU PHỐI chưa từng được đo, và lần đo đầu ra 2 lớp việc thật.

    (a) Skill `nghien-cuu-ebm-tong-hop` (44K) + `dao-tao-slide-tai-lieu-y-khoa` (28K) +
        `ehospital-mini` chạy ở runtime mà KHÔNG có nguồn trong cây OneDrive — app dọn
        runtime (đã xảy ra nhiều lần, đo 13/08: 20/22 skill lệch bản) là mất trắng, và
        `dong_bo_skill.py` không hề biết chúng tồn tại. Đã cứu cả ba về `sync/skills/`.
    (b) Chính phép đo đầu tiên tạo BÁO ĐỘNG GIẢ hai lần: 6 "tham chiếu hỏng" hoá ra là
        SKILL (tên agent và skill sống chung mặt chữ backtick nhưng thuộc hai sổ đăng
        ký); 22 skill "mất trắng" hoá ra 20 là skill dựng sẵn của Anthropic. Chốt
        `kiem_dieu_phoi.py` vì thế dùng KHAI BÁO tường minh (SKILL_DUNG_SAN ·
        TEN_LICH_SU) thay vì suy đoán — skill LẠ không nguồn vẫn đỏ, đúng như cần.

    Đồ thị điều phối đo được đang lành: nhạc trưởng lâm sàng gọi 23 agent, nghiên cứu
    31, không agent mồ côi. Chốt này giữ nó tiếp tục lành.

    Kiểm HÀNH VI: chạy chốt điều phối thật, đòi exit 0.
    """
    import subprocess
    tp = REPO / "tools" / "kiem_dieu_phoi.py"
    if not tp.exists():
        return False, "mất kiem_dieu_phoi.py — tầng điều phối lại không ai đo"
    r = subprocess.run([sys.executable, str(tp)], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        dong = [d.strip() for d in (r.stdout or "").splitlines() if d.strip().startswith("🔴")]
        return False, ("điều phối KHÔNG sạch: "
                       + (dong[0][:140] if dong else "chạy `python tools/kiem_dieu_phoi.py`"))
    return True, "tham chiếu phân giải được · agent đều có đường gọi · skill runtime đều có nguồn"


def bh45_luong_theo_yeu_cau_phai_thua_huong_luong_dinh_ky():
    """15/08 — mọi bản vá "mới nhất/tin cậy nhất" nằm ở luồng ĐỊNH KỲ; luồng THEO-YÊU-CẦU
    (bác sĩ nêu vấn đề → skill dựng gói) KHÔNG thừa hưởng gì.

    Đo trước khi vá, trong SKILL.md của `cap-nhat-chung-cu-y-khoa`: `edat` 0 lần ·
    `kiem_chung_cu_vuot_qua` 0 · NEJM/Lancet gọi tên 0 · lượt mới-vào-PubMed 0. Tức là
    khi bác sĩ HỎI TRỰC TIẾP một vấn đề — đường dùng nhiều nhất — skill vẫn tìm theo lối
    cũ: dính lại đúng bộ lọc `[pt]` vứt bài mới (BH38), không kiểm chứng cứ vượt qua,
    không kiểm rút bài từng PMID.

    Hai luồng lấy chứng cứ phải cùng một chuẩn — nếu không, chất lượng gói phụ thuộc vào
    việc bác sĩ hỏi theo cách nào, và không ai nhìn thấy sự khác biệt đó.

    Kiểm HÀNH VI (doctrine-drift, cùng họ BH39): Bước 2 của SKILL.md phải giữ đủ 4 dấu
    vết của cách tìm mới. Mất dấu nào ⇒ luồng theo-yêu-cầu lại tụt sau luồng định kỳ.
    """
    sk = REPO / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "SKILL.md"
    if not sk.exists():
        return False, "mất SKILL.md của cap-nhat-chung-cu-y-khoa"
    s = sk.read_text(encoding="utf-8", errors="replace")
    dau_vet = {
        "lượt mới-vào-PubMed (edat, không lọc pt)": "datetype=edat",
        "kiểm chứng cứ vượt qua cho mục apply": "kiem_chung_cu_vuot_qua",
        "tạp chí đỉnh gọi TÊN": '"N Engl J Med"[ta]',
        "kiểm rút bài từng PMID": "check_citation_retraction",
    }
    thieu = [ten for ten, mk in dau_vet.items() if mk not in s]
    if thieu:
        return False, (f"Bước 2 mất {len(thieu)} dấu vết: {', '.join(thieu)} — luồng "
                       "theo-yêu-cầu lại tìm theo lối cũ")
    return True, "luồng theo-yêu-cầu giữ đủ 4 lượt tìm + kiểm rút bài"


def bh46_hop_dong_item_va_may_trang_thai():
    """15/08 — LÔ 2 kế hoạch kiện toàn: máy trạng thái item phải THI HÀNH ĐƯỢC BẰNG MÁY.

    Trước đó trạng thái một mục chứng cứ phải suy ra từ 3 chỗ (sổ xác minh · hàng chờ
    EBM_MASTER · quyết định bác sĩ) và KHÔNG có gì cấm-bằng-máy việc một tool đặt thẳng
    APPROVED. Nay: `contracts/evidence-item.schema.json` + `state-machine.md` +
    validator stdlib `tools/kiem_hop_dong_item.py` thi hành 4 luật cấm — máy tự
    APPROVED/APPLIED (I4) · nhảy cóc CANDIDATE khi chưa resolved (I1) · retracted vẫn
    CANDIDATE (dừng khẩn) · tự gán mức khi nguồn không chấm (I2).

    Kiểm HÀNH VI: chạy self-test của validator — item tốt PASS, cả 5 ca xấu bị bắt.
    """
    import subprocess
    vd = REPO / "tools" / "kiem_hop_dong_item.py"
    for f in (vd, REPO / "contracts" / "evidence-item.schema.json",
              REPO / "contracts" / "state-machine.md"):
        if not f.exists():
            return False, f"mất {f.name} — máy trạng thái lại chỉ còn trên giấy"
    r = subprocess.run([sys.executable, str(vd), "--self-test"],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0 or "LỌT" in (r.stdout or ""):
        return False, "validator không bắt đủ 5 ca xấu — luật cấm thành lời khuyên"
    return True, "4 luật cấm của máy trạng thái đều thi hành được bằng máy"


def bh47_quet_phai_co_khoa_cursor_va_alert():
    """15/08 — LÔ 1: ba mảnh an toàn vận hành của bộ quét phải HOẠT ĐỘNG, không chỉ có mặt.

    (a) KHOÁ: OneDrive đồng bộ 2 máy — hai tiến trình cùng ghi sổ JSON là mất bản ghi
        (điều kiện dừng khẩn). Giành khoá lần 2 phải FAIL rõ, không lặng lẽ chạy chồng.
    (b) CON TRỎ: không có cursor thì chạy dày = quét lại toàn cửa sổ, chạy thưa = HỞ KHE
        giữa hai cửa sổ. Lượt sau phải hỏi bằng mindate = cursor−3ngày (lùi 3 ngày chống
        hở khe quanh ranh giới — dedup phía sau chặn trùng nên lùi là rẻ).
    (c) ALERT: sự kiện KHẨN phải có kênh riêng `alerts/` — trộn với tín hiệu thường là
        dạy người đọc bỏ qua màu đỏ (BH32). Không có sự kiện ⇒ KHÔNG sinh file.
    """
    ss = _nap(REPO / "EBM-Dashboards" / "tools" / "surveillance_scan.py", "ss_bh47")
    for ten in ("gianh_khoa", "tra_khoa", "doc_cursor", "ghi_cursor", "ghi_alert"):
        if not hasattr(ss, ten):
            return False, f"mất {ten} — LÔ 1 bị tháo"
    # (a) khoá
    ok1, _ = ss.gianh_khoa()
    ok2, _ = ss.gianh_khoa()
    ss.tra_khoa()
    if not (ok1 and not ok2):
        return False, "khoá không chặn tiến trình thứ hai — 2 máy sẽ ghi chồng"
    # (b) cursor → mindate
    urls: list[str] = []

    def _fetch(u):
        urls.append(u)
        return {"esearchresult": {"idlist": []}}

    ss.search("abc", 30, 5, fetch_json=_fetch, mindate="2026/08/01")
    if "mindate=2026%2F08%2F01" not in urls[-1] or "reldate" in urls[-1]:
        return False, "search() có mindate mà vẫn hỏi reldate — cursor không tác dụng"
    ss.search("abc", 30, 5, fetch_json=_fetch)
    if "reldate=30" not in urls[-1]:
        return False, "search() không mindate phải lùi về reldate — mất tương thích cũ"
    # (c) alert: rỗng không sinh file
    if ss.ghi_alert([], "2099-01-01") is not None:
        return False, "ghi_alert sinh file cho danh sách RỖNG — nhiễu kênh khẩn"
    return True, "khoá chặn chồng · cursor ra mindate · alert chỉ khi có sự kiện"


def bh48_ma_thoat_tach_noi_dung_va_ha_tang():
    """15/08 — LÔ 2: FAIL vì MẠNG không được đội lốt FAIL vì NỘI DUNG.

    Đo thật 12/08: cùng một dashboard chạy `--online` 4 lần cho 13→3→6→1 lỗi cứng
    chỉ vì DNS chập chờn. Caller không phân biệt được «gói SAI» với «gói CHƯA XÁC
    MINH ĐƯỢC» thì người vận hành sẽ (a) đi sửa một gói lành, hoặc (b) chạy lại
    tới lần may mắn rồi coi đó là đã xác minh — cả hai đều đã xảy ra thật.
    Hợp đồng từ 15/08 (LÔ 2 PHA 2): `report()` trả 1 khi có ≥1 lỗi NỘI DUNG,
    2 khi TOÀN BỘ lỗi cứng mang dấu hiệu máy/mạng, 0 khi sạch. 1 và 2 đều
    nonzero — cổng vẫn fail-closed, không caller nào bị mở nhầm.
    """
    import contextlib
    import io
    vd = _nap(REPO / "EBM-Dashboards" / "tools" / "verify_dashboard.py", "vd_bh48")
    if not hasattr(vd, "_DAU_HIEU_LOI_MANG"):
        return False, "mất _DAU_HIEU_LOI_MANG — bộ phân loại lỗi mạng bị tháo"
    dau = next(iter(vd._DAU_HIEU_LOI_MANG))
    with contextlib.redirect_stdout(io.StringIO()):
        rc_sach = vd.report([], [], [])
        rc_mang = vd.report([f"PMID 999 CHƯA XÁC MINH ĐƯỢC ({dau} x)"], [], [])
        rc_tron = vd.report([f"PMID 999 CHƯA XÁC MINH ĐƯỢC ({dau} x)",
                             "ITEM-01: decision='apply' trên chứng cứ yếu"], [], [])
    if rc_sach != 0:
        return False, f"sạch phải trả 0, đang trả {rc_sach}"
    if rc_mang != 2:
        return False, f"toàn lỗi mạng phải trả 2 («chưa xác minh»), đang trả {rc_mang}"
    if rc_tron != 1:
        return False, f"có lỗi nội dung phải trả 1 («gói sai»), đang trả {rc_tron}"
    return True, "0/1/2 tách đúng: sạch · gói sai · chưa-xác-minh-được"


def bh49_toan_van_va_rut_bai_theo_dinh_danh():
    """15/08 — PHA 4 LÔ D/E: hai cổng an toàn mới phải BẮT được trên file thật.

    (a) `appraisalCompleteness:'partial'` × decision `apply` → CHẶN — thẩm định
        trên abstract không được đội lốt thẩm định đầy đủ (P4).
    (b) Dashboard MỚI trích DOI mà sổ đã biết ĐÃ RÚT → CHẶN qua tầng tra-theo-
        ĐỊNH-DANH — lỗ hổng thật tìm bằng fixture 15/08: `nguon_da_rut` chỉ tra
        theo ánh xạ cac_dashboard nên file chưa từng qua vòng quét A4 đi qua sạch.
    Kiểm bằng cách CHẠY cổng thật trên fixture (không đếm chuỗi trong code).
    """
    import subprocess
    import sys as _sys
    fx = REPO / "EBM-Dashboards" / ".bh49-fixture.html"
    fx.write_text("""<script>
const DATA = { meta: { title: 'bh49', dateUpdated: '2026-08-15' },
  provenanceUnknown: true, provenanceUnknownLyDo: 'fixture chốt BH49',
  summary: { doNow: [], doNot: [], redFlags: [] },
  items: [
    { id: 'ITEM-01', source: 'GL', org: 'X', dateVersion: '2026', design: 'Guideline',
      gradeLevel: 'high', gradeBy: 'X (GRADE)', gradeSource: 'GRADE high',
      decision: 'apply', appraisalCompleteness: 'partial', pmid: '26760044', title: 't' },
    { id: 'ITEM-02', source: 'RR', org: 'Y', dateVersion: '2018', design: 'Cohort',
      gradeLevel: 'na', decision: 'consider', doi: '10.1001/jamaoncol.2018.4070', title: 't' }
  ]};
// ===== HẾT KHỐI DATA =====
</script><p>Cần bác sĩ kiểm chứng.</p>""", encoding="utf-8")
    try:
        r = subprocess.run([_sys.executable,
                            str(REPO / "EBM-Dashboards" / "tools" / "verify_dashboard.py"),
                            str(fx), "--strict-sources"],
                           capture_output=True, text=True, cwd=REPO, timeout=120)
    finally:
        fx.unlink(missing_ok=True)
    if "appraisalCompleteness='partial'" not in r.stdout:
        return False, "cổng KHÔNG chặn apply trên thẩm định một phần — P4 bị tháo"
    if "10.1001/jamaoncol.2018.4070" not in r.stdout or "RÚT" not in r.stdout:
        return False, "cổng KHÔNG bắt DOI đã rút theo định danh — dashboard mới lại đi qua sạch"
    if r.returncode == 0:
        return False, "fixture có 2 lỗi an toàn mà cổng trả exit 0"
    return True, "partial×apply chặn · DOI đã-rút bắt theo định danh · exit nonzero"


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
    ("BH27", "14/08", "«Không kiểm được» phải bị tính là VẤN ĐỀ", bh27_khong_kiem_duoc_phai_la_van_de),
    ("BH28", "14/08", "Không thay phán đoán ngữ nghĩa bằng độ giống từ vựng", bh28_khong_thay_phan_doan_ngu_nghia_bang_do_giong_tu_vung),
    ("BH29", "14/08", "Mọi chốt định nghĩa đều phải được đăng ký", bh29_moi_ham_bh_deu_phai_duoc_dang_ky),
    ("BH30", "14/08", "Khoá gom nhóm phải định danh duy nhất", bh30_khoa_gom_nhom_phai_dinh_danh_duy_nhat),
    ("BH31", "14/08", "Nguồn đã rút phải chặn được ở cổng", bh31_nguon_da_rut_phai_chan_duoc_o_cong),
    ("BH32", "14/08", "Chỉ số gộp không được kết luận cho cả tập", bh32_chi_so_gop_khong_duoc_ket_luan_cho_ca_tap),
    ("BH33", "14/08", "Kiểm rút bài phải phủ mọi kiểu định danh", bh33_kiem_rut_bai_phai_phu_moi_kieu_dinh_danh),
    ("BH34", "14/08", "Cảnh báo phải nói đúng MỨC", bh34_canh_bao_phai_noi_dung_muc),
    ("BH35", "14/08", "Khai chưa-biết không được tắt luật an toàn", bh35_khai_chua_biet_khong_duoc_tat_luat_an_toan),
    ("BH36", "14/08", "gradeLevel phải khai ai đã chấm", bh36_grade_phai_khai_ai_cham),
    ("BH37", "14/08", "Ứng viên phải mang độ tin cậy ngay lúc nhận", bh37_ung_vien_phai_mang_do_tin_cay_ngay_luc_nhan),
    ("BH38", "14/08", "Không lọc bỏ cái mới nhất ở khâu tìm", bh38_khong_loc_bo_cai_moi_nhat_o_khau_tim),
    ("BH39", "14/08", "Doctrine không được trôi sau cổng", bh39_doctrine_khong_duoc_troi_sau_cong),
    ("BH40", "14/08", "Luật toàn đội phải lan được xuống mọi agent", bh40_luat_toan_doi_phai_lan_duoc_xuong_moi_agent),
    ("BH41", "14/08", "Công cụ chứng cứ không được mồ côi", bh41_cong_cu_chung_cu_khong_duoc_mo_coi),
    ("BH42", "14/08", "Guideline không được tin theo thương hiệu", bh42_guideline_khong_duoc_tin_theo_thuong_hieu),
    ("BH43", "14/08", "Canary đầu-cuối phải chạy và phải bắt được", bh43_canary_dau_cuoi_phai_chay_va_phai_bat_duoc),
    ("BH44", "15/08", "Điều phối agent phải sạch", bh44_dieu_phoi_agent_phai_sach),
    ("BH45", "15/08", "Luồng theo-yêu-cầu phải thừa hưởng luồng định kỳ", bh45_luong_theo_yeu_cau_phai_thua_huong_luong_dinh_ky),
    ("BH46", "15/08", "Hợp đồng item + máy trạng thái thi hành được", bh46_hop_dong_item_va_may_trang_thai),
    ("BH47", "15/08", "Quét phải có khoá + cursor + alert", bh47_quet_phai_co_khoa_cursor_va_alert),
    ("BH48", "15/08", "Mã thoát tách «gói sai» khỏi «chưa xác minh»", bh48_ma_thoat_tach_noi_dung_va_ha_tang),
    ("BH49", "15/08", "Toàn văn bắt buộc cho apply + rút bài theo định danh", bh49_toan_van_va_rut_bai_theo_dinh_danh),
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
