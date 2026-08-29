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
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]
DASH = REPO / "EBM-Dashboards"


def _sh_which(ten: str):
    """shutil.which tách riêng để các chốt gọi mà không import lặp."""
    import shutil
    return shutil.which(ten)


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
        for m in ghi.finditer(t):
            # miễn trừ TƯỜNG MINH kèm lý do trên dòng ngay TRƯỚC match — sinh ra
            # 17/08 khi BH10 bắt nhầm fixture BH58 (ghi item giả vào
            # TemporaryDirectory để tự-đột-biến chốt, không phải dashboard thật).
            # Miễn theo TỪNG match, không miễn cả file — code ghi thật vẫn bị bắt.
            dau_dong = t.rfind("\n", 0, t.rfind("\n", 0, m.start()))
            if "bh10-mien:" in t[max(0, dau_dong):m.start()]:
                continue
            pham.append(f.name)
            break
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


def bh70_canary_cong_nghien_cuu_phai_chay_va_phai_bat_duoc():
    """22/08 — chuỗi cổng CHỨNG CỨ có canary đầu-cuối từ 14/08 (BH43), chuỗi 11 cổng
    NGHIÊN CỨU G0–G10 thì KHÔNG có gì tương đương suốt từ đó.

    Bất đối xứng này nguy hiểm vì chuỗi nghiên cứu đã mắc đúng họ lỗi mà canary sinh ra để
    bắt: guardrail G3/G8 phần lớn là TAUTOLOGY (đếm chuỗi do chính hàm sinh artifact in
    cứng, nên không nhánh nào khiến luật BLOCK được); SAP đã ký có thể không còn khớp
    `G3_checkpoint.json` sau khi G3 chạy lại (phát hiện F5, audit 30/07); cổng A12 fail-open
    kiểu BH27. Tất cả đều thuộc lớp «công cụ vẫn chạy, vẫn in kết quả hợp lệ, nhưng thứ cần
    kiểm thì không bao giờ được kiểm».

    `medical-ebm-automation/tools/thu_dau_cuoi_cong_nghien_cuu.py` gài 9 lỗi BIẾT TRƯỚC vào
    một đề tài GIẢ (thư mục tạm, không đụng `exports/` thật, không ký, không gọi mạng) rồi
    đòi các quality gate thật phải BLOCK đúng chỗ.

    Kiểm HÀNH VI, không đếm chữ: canary phải tồn tại VÀ chạy xanh. Đã kiểm bằng đột biến
    TRÊN ĐĨA — vô hiệu luật G4-AUTO-03 ⇒ canary đỏ đúng hai lỗi drift (7/9) và **mã thoát
    đổi sang 1**; khôi phục thì xanh lại. Mã thoát đúng là điều kiện sống còn: một canary in
    ĐỎ mà vẫn thoát 0 thì chính nó fail-open.
    """
    import subprocess

    tp = REPO / "medical-ebm-automation" / "tools" / "thu_dau_cuoi_cong_nghien_cuu.py"
    if not tp.exists():
        return False, "mất canary cổng nghiên cứu — không còn gì chứng minh chuỗi G0–G10 CHẶN thật"
    r = subprocess.run([sys.executable, str(tp)], capture_output=True, text=True,
                       timeout=300, cwd=str(tp.parent.parent))
    if r.returncode != 0:
        dong = [d.strip() for d in (r.stdout or "").splitlines() if "LỌT" in d]
        return False, ("canary cổng nghiên cứu ĐỎ — lỗi gài KHÔNG bị cổng nào bắt: "
                       + (dong[0][:150] if dong else "xem thu_dau_cuoi_cong_nghien_cuu.py"))
    so = (r.stdout or "").count("[✅ BẮT ĐƯỢC]")
    return True, f"canary cổng nghiên cứu xanh {so}/{so} lỗi gài"


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


def bh50_ping_khong_duoc_doi_lot_chay_that():
    """15/08 — vòng «tự động + trung thực»: PING endpoint ≠ LẦN THU HOẠCH THẬT.

    Bản đầu của sources_health ghi `last_success_at` ngay khi ping thành công —
    một nguồn sống mà 3 tuần không ai chạy vẫn hiện «thành công hôm nay», và
    tuyên bố độ phủ đọc trường đó sẽ nói dối bác sĩ. Hợp đồng từ 15/08: ping chỉ
    ghi `last_probe_at`; `last_success_at` SUY TỪ ARTIFACT (log weekly_safety,
    sổ xác minh, mtime kho RW…) và một giá trị BỊA trong sổ phải bị TỰ SỬA về
    ngày artifact ở lượt chạy kế.
    """
    import json
    import sys as _sys
    import tempfile
    sh = _nap(REPO / "tools" / "sources_health.py", "sh_bh50")
    if not hasattr(sh, "lay_thanh_cong_that"):
        return False, "mất lay_thanh_cong_that — tách ping/chạy-thật bị tháo"
    that_006 = sh.lay_thanh_cong_that("SRC-006")
    if not (that_006 and that_006 < "2027"):
        return False, f"SRC-006 không suy được từ log weekly_safety (được: {that_006!r})"
    # Gài ngày BỊA tương lai vào bản SAO sổ → chạy tool trên bản sao → phải bị sửa.
    goc = json.loads((REPO / "data" / "sources.json").read_text(encoding="utf-8"))
    for s in goc["sources"]:
        if s["id"] == "SRC-006":
            s["last_success_at"] = "2099-01-01"
    tmp = Path(tempfile.mkdtemp(prefix="bh50-")) / "sources.json"
    tmp.write_text(json.dumps(goc, ensure_ascii=False), encoding="utf-8")
    cu, sh.SO = sh.SO, tmp
    cu_argv = _sys.argv
    try:
        _sys.argv = ["sources_health", "--khong-mang", "--im-khi-on"]
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            sh.main()
    finally:
        sh.SO = cu
        _sys.argv = cu_argv
    sau = json.loads(tmp.read_text(encoding="utf-8"))
    v = next(s for s in sau["sources"] if s["id"] == "SRC-006")["last_success_at"]
    if v == "2099-01-01":
        return False, "ngày chạy-thật BỊA (2099) sống sót qua lượt kiểm — sổ nói dối được"
    return True, f"ngày bịa bị tự sửa về artifact ({v}); ping tách khỏi chạy thật"


def bh51_ledger_synthetic_dung_pham_vi():
    """15/08 — PHA R: lõi ký công nhận bản ghi synthetic ĐÚNG PHẠM VI (#8 bác sĩ duyệt).

    ĐÍNH CHÍNH trung thực (đo bằng đột biến ngay khi viết chốt): thứ MỞ KHOÁ
    demo là SỬA THỨ TỰ THAM SỐ — tôi gọi (study, gate) suốt buổi sáng, TypeError
    bị nuốt thành False im lặng. CẬP NHẬT 15/08 chiều: #10 ĐÃ ÁP (bác sĩ duyệt
    tường minh qua AskUserQuestion) — admin tool nay ghi is_synthetic=True nên
    nhánh #8 SỐNG THẬT: entry chép sang đề tài KHÔNG marker bị từ chối (đã đo
    bằng đột biến sao-chép-ledger). Chốt này khoá
    hai thứ THẬT SỰ kiểm được: gọi đúng chữ ký (gate_id, study, artifact) trên
    đề tài demo → True; artifact sửa 1 byte → False (hash vẫn ràng, fail-closed).
    """
    import importlib.util
    import shutil
    import sys as _sys
    import tempfile
    mea = REPO / "medical-ebm-automation"
    sap = mea / "exports/ZZPHA-R-AUTO-DEMO/G4_A5_SAP_FINAL_ZZPHA-R-AUTO-DEMO.md"
    if not sap.exists():
        return True, "đề tài demo không còn — chốt bỏ qua có khai báo"
    spec = importlib.util.spec_from_file_location("gc_bh51", mea / "tools/gate_contract.py")
    gc = importlib.util.module_from_spec(spec)
    _sys.modules["gc_bh51"] = gc
    try:
        spec.loader.exec_module(gc)
    except Exception as exc:  # noqa: BLE001
        return False, f"gate_contract không nạp được dưới interpreter này: {exc}"
    if not gc.ledger_approved("G4", "ZZPHA-R-AUTO-DEMO", str(sap)):
        return False, ("chữ ký synthetic hash-khớp KHÔNG được công nhận — #8 bị revert "
                       "hoặc thứ tự tham số lại sai")
    tmp = Path(tempfile.mkdtemp(prefix="bh51-")) / sap.name
    shutil.copy(sap, tmp)
    tmp.write_bytes(tmp.read_bytes() + b" ")
    if gc.ledger_approved("G4", "ZZPHA-R-AUTO-DEMO", str(tmp)):
        return False, "artifact sửa 1 byte mà VẪN được công nhận — hash không còn ràng"
    # PHỦ ĐIỂM GỌI: cổng chấm G6 phải lấy được bằng chứng TỪ LEDGER (không rơi
    # fallback) — đảo tham số ở điểm gọi trong g6_quality_gate sẽ làm dòng
    # «chữ ký thật» biến mất dù lõi ledger_approved vẫn đúng.
    import subprocess
    r = subprocess.run([_sys.executable, str(mea / "tools/g6_quality_gate.py"),
                        "--study", "ZZPHA-R-AUTO-DEMO"],
                       capture_output=True, text=True, cwd=mea, timeout=120)
    if "chữ ký thật" not in r.stdout:
        return False, ("G6-AUTO-01 không còn lấy bằng chứng từ ledger — điểm gọi "
                       "ledger_approved trong g6_quality_gate hỏng (đảo tham số?)")
    return True, "synthetic đúng phạm vi + điểm gọi G6 lấy đúng bằng chứng ledger"


def bh56_cong_cu_moi_phai_co_day():
    """16/08 — BH41 áp cho lứa công cụ Tầng-1/2: «tool không ai gọi = không tồn tại».

    Hai vế, cả hai từng là lỗi thật:
    (1) rag_toan_van/do_tac_dong phải được NHẮC ở ≥1 nơi tiêu thụ (doctrine agent
        hoặc nhịp tuần/tác vụ lịch) — chính BH41 từng bắt so_xac_minh mồ côi.
    (2) chỉ mục RAG kho chung phải TƯƠI theo kho: có XML mới hơn vec.npy quá 8
        ngày mà không dựng lại → lớp hỏi-đáp mù phần mới một cách im lặng
        (weekly 5b là dây nối; chốt này canh dây không bị tháo).
    """
    goc = REPO
    noi_tieu_thu = [goc / ".claude" / "agents" / "tra-cuu-chung-cu.md",
                    goc / ".claude" / "agents" / "tong-quan-y-van.md",
                    goc / "medical-ebm-automation" / "scripts" / "weekly_safety.sh",
                    Path.home() / ".claude" / "scheduled-tasks" / "goi-duyet-tuan-ebm"
                    / "SKILL.md"]
    van_ban = " ".join(p.read_text(encoding="utf-8", errors="replace")
                       for p in noi_tieu_thu if p.exists())
    for tool in ("rag_toan_van", "do_tac_dong", "dat_canh_chung_cu_moi", "dung_hom_thu"):
        if tool not in van_ban:
            return False, f"{tool} MỒ CÔI — không doctrine/nhịp nào gọi (họ BH41)"
    kho = goc / "EBM-Dashboards" / "toan_van_oa"
    vec = kho / ".rag" / "vec.npy"
    xmls = list(kho.glob("PMID-*.xml"))
    if xmls and vec.exists():
        moi_nhat = max(f.stat().st_mtime for f in xmls)
        if moi_nhat - vec.stat().st_mtime > 8 * 86400:
            return False, ("chỉ mục RAG cũ hơn kho >8 ngày — dây weekly 5b đứt "
                           "hoặc chưa chạy; hỏi-đáp đang mù phần bài mới")
    elif xmls and not vec.exists():
        return False, "kho có bài mà CHƯA từng dựng chỉ mục RAG"
    return True, "2 tool có dây gọi · chỉ mục tươi theo kho"


def bh57_ky_lich_lo_phai_nhin_thay():
    """16/08 — KỲ ĐẦU TIÊN của kiến trúc lịch mới (tác vụ Claude thay launchd)
    đã LỠ ngay sáng ra đời: 06:30 T7 máy/app không chạy, nextRunAt nhảy thẳng
    tuần sau, không lastRunAt — KHÔNG bộ đếm nào nhìn thấy. Cùng họ với launchd
    đạt-giả 13/08 (đăng ký ≠ nổ): đăng ký lịch đúng mà kỳ trôi qua im lặng thì
    hệ quay về «chạy khi mở phiên» không ai hay.

    Chốt kiểm HÀNH VI giac_quan_lich_nen (tu_de_xuat_viec) bằng log giả:
    PASS 12 ngày → mức 0; PASS 3 ngày nhưng kỳ T7 vừa qua không nổ → mức 2;
    PASS đúng sáng T7 → im. Giác quan đọc ĐẦU RA THẬT trong log, không đọc
    đăng ký lịch — đó chính là bài học."""
    import datetime as _dt
    import importlib.util as _ilu
    duong = REPO / "tools" / "tu_de_xuat_viec.py"
    spec = _ilu.spec_from_file_location("_tdx_bh57", duong)
    mod = _ilu.module_from_spec(spec)
    sys.modules["_tdx_bh57"] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception as e:  # noqa: BLE001 — chốt nhắc không được làm chết bộ chạy
        return False, f"không nạp được tu_de_xuat_viec: {e}"
    if not hasattr(mod, "giac_quan_lich_nen"):
        return False, "giac_quan_lich_nen BIẾN MẤT khỏi tu_de_xuat_viec (giác quan bị tháo)"
    import tempfile
    t7 = _dt.date(2026, 8, 16)  # một thứ Bảy cố định — không dùng date.today()
    with tempfile.TemporaryDirectory() as td:
        log = Path(td) / "log_gia.log"
        log.write_text("===== 2026-08-04 06:35:00 : KẾT THÚC — tổng thể=PASS =====\n",
                       encoding="utf-8", newline="\n")
        qua_han = mod.giac_quan_lich_nen(log, t7)
        if not qua_han or qua_han[0][0] != 0:
            return False, "log PASS 12 ngày mà giác quan KHÔNG báo mức 0 — mù quá hạn"
        log.write_text("===== 2026-08-13 17:36:22 : KẾT THÚC — tổng thể=PASS =====\n",
                       encoding="utf-8", newline="\n")
        lo_ky = mod.giac_quan_lich_nen(log, t7)
        if not lo_ky or lo_ky[0][0] != 2:
            return False, "kỳ T7 lỡ (PASS 3 ngày) mà giác quan im — mù lỡ-kỳ"
        log.write_text("===== 2026-08-16 06:35:00 : KẾT THÚC — tổng thể=PASS =====\n",
                       encoding="utf-8", newline="\n")
        if mod.giac_quan_lich_nen(log, t7):
            return False, "kỳ NỔ đúng hẹn mà vẫn báo — báo động giả dạy người ta bỏ qua"
    return True, "giác quan lịch-nền bắt đúng 3 ca: quá hạn · lỡ-kỳ · nổ-đúng-hẹn"


def bh59_khoi_data_phai_parse_duoc_nhu_js():
    """16/08 — đợt sửa-hàng-loạt 14/08 («đưa 56 mục về na») chèn ghi chú chứa
    NHÁY ĐƠN LỒNG vào chuỗi nháy đơn của 16 dashboard: JS vỡ ⇒ trang trắng
    im lặng, mà verify_dashboard vẫn PASS (field() dung sai đọc được từng
    trường). Chỉ lộ ra khi bước ③ bộ-năm (parser CHẶT) chết hàng loạt.

    Chốt: chạy extract_dashboard_data (parser chặt nhất hệ có) trên TOÀN KHO —
    bản nào không parse là DATA hỏng thật với trình duyệt. Đây là JS-parse
    canary; hai biến thể đã gặp («đưa về 'na'» · «giữ 'na'») nhắc rằng quét
    theo MẪU CHUỖI sẽ luôn sót — phải parse thật."""
    import importlib.util as _ilu
    duong = REPO / "EBM-Dashboards" / "tools" / "build_dashboard_docx.py"
    spec = _ilu.spec_from_file_location("_bdd_bh59", duong)
    mod = _ilu.module_from_spec(spec)
    sys.modules["_bdd_bh59"] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception as e:  # noqa: BLE001 — chốt nhắc không được làm chết bộ chạy
        return False, f"không nạp được build_dashboard_docx: {e}"
    hong = []
    for f in sorted((REPO / "EBM-Dashboards").glob("WebDashboard_*.html")):
        if ".bak" in f.name:
            continue
        try:
            mod.extract_dashboard_data(str(f))
        except Exception as e:  # noqa: BLE001
            hong.append(f"{f.name[:48]}: {str(e)[:60]}")
    if hong:
        return False, f"{len(hong)} dashboard có khối DATA KHÔNG parse được (JS vỡ → trang trắng) — {hong[0]}"
    return True, "toàn kho parse sạch như JS"


def bh60_goi_tuan_phai_doc_toan_van():
    """19/08 — đo được: kho toàn văn phủ 170/579 PMID của dashboard CŨ nhưng
    0/12 PMID của gói tuần W34 — dây chuyền TUẦN (chứng cứ MỚI nhất, thứ cần
    chi tiết nhất) thẩm định 100%% từ TÓM TẮT, kể cả khi bài OA nằm sẵn trên PMC.
    Cùng họ BH39: năng lực có ở TẦNG CÔNG CỤ mà doctrine vận hành không gọi tên
    thì với dây chuyền hằng ngày nó không tồn tại.

    Chốt 3 vế: (a) hai tool tồn tại; (b) SKILL gói tuần (bản NGUỒN trong OneDrive
    — sync/scheduled-tasks/) phải gọi tên CẢ gom --queue LẪN doc_sau_toan_van;
    (c) bộ lọc câu-hiệu-số của doc_sau còn sống: bắt câu có MD+CI, chặn rác bảng
    ép phẳng >420 ký tự (đã gặp thật 19/08)."""
    tool_gom = REPO / "tools" / "gom_toan_van_dashboard.py"
    tool_doc = REPO / "tools" / "doc_sau_toan_van.py"
    if not (tool_gom.exists() and tool_doc.exists()):
        return False, "thiếu tool gom/doc_sau toàn văn"
    skill = REPO / "sync" / "scheduled-tasks" / "goi-duyet-tuan-ebm" / "SKILL.md"
    if not skill.exists():
        return False, "thiếu nguồn cứu hộ SKILL gói tuần trong sync/scheduled-tasks/"
    vb = skill.read_text(encoding="utf-8")
    if "gom_toan_van_dashboard" not in vb or "doc_sau_toan_van" not in vb:
        return False, "SKILL gói tuần KHÔNG còn nhắc bước đọc toàn văn (trôi doctrine kiểu BH39)"
    # 19/08 chiều — bác sĩ chỉnh hướng «nguồn chuẩn, không phải toàn văn»: skill
    # tổng thuật phải giữ làn authority-first (tra_nguon_chuan) đi TRƯỚC PubMed
    tt = REPO / "sync" / "skills" / "tong-thuat-chung-cu" / "SKILL.md"
    if not tt.exists() or "tra_nguon_chuan" not in tt.read_text(encoding="utf-8"):
        return False, "skill tổng thuật mất làn NGUỒN CHUẨN (tra_nguon_chuan) — trôi doctrine"
    if not (REPO / "EBM-Dashboards" / "nguon_chuan" / "danh-ba-nguon-chuan.json").exists():
        return False, "thiếu danh bạ nguồn chuẩn (EBM-Dashboards/nguon_chuan/)"
    import importlib.util as _ilu
    spec = _ilu.spec_from_file_location("_dstv_bh60", tool_doc)
    mod = _ilu.module_from_spec(spec)
    sys.modules["_dstv_bh60"] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception as e:  # noqa: BLE001
        return False, f"không nạp được doc_sau_toan_van: {e}"
    cau = mod._cau_hieu_so(["Pooled mean difference was 2.29% (95% CI 1.48-3.09, p = 0.005)."])
    if len(cau) != 1:
        return False, "bộ lọc câu-hiệu-số không bắt được câu MD+CI chuẩn"
    rac = mod._cau_hieu_so(["13.76 g/dL NR NR " + "x" * 500 + " OR 1.2"])
    if rac:
        return False, "bộ lọc câu-hiệu-số nhận cả RÁC BẢNG ép phẳng (>420 ký tự)"
    return True, "gói tuần có dây đọc toàn văn: tool + SKILL + bộ lọc sống"


def bh63_benchmark_mu_khong_de_may_tu_cham():
    """20/08 — bác sĩ duyệt benchmark mù vì mọi so sánh «hệ hơn/thua Gemini» tới nay
    đều do CHÍNH hệ chấm (xung đột grader=generator, sổ bài học 08/07). Chốt giữ ba
    bất biến của công cụ benchmark: (a) có ẩn danh + khoá mở nhãn; (b) KHÔNG có
    đường nào để máy tự cho điểm chất lượng; (c) bản không có định danh nào phải
    được ghi «KHÔNG kiểm được», tuyệt đối không đọc thành «sạch»."""
    f = REPO / "tools" / "bench_mu.py"
    if not f.exists():
        return False, "thiếu tools/bench_mu.py"
    vb = f.read_text(encoding="utf-8")
    if "khoa-mo-nhan.json" not in vb or "random.Random" not in vb:
        return False, "benchmark mất cơ chế ẩn danh/khoá mở nhãn"
    if "KHÔNG kiểm được" not in vb:
        return False, "bản 0 định danh không còn được ghi «KHÔNG kiểm được» (nguy cơ đọc thành sạch)"
    # máy KHÔNG được tự chấm: cấm mọi hàm/nhánh tính điểm chất lượng
    if re.search(r"def\s+cham_diem|diem_chat_luong|tu_cham", vb):
        return False, "xuất hiện đường máy TỰ CHẤM chất lượng — vi phạm nguyên tắc benchmark mù"
    return True, "benchmark mù: có ẩn danh + khoá nhãn, máy không tự chấm"


def bh64_bai_tong_thuat_phai_o_trong_vong_song():
    """20/08 — bài tổng thuật từng là ẢNH TĨNH: không nằm trong hòm thư, không sổ
    đăng ký, không ai canh độ tươi ⇒ cũ đi IM LẶNG (đúng họ lỗi đã vá ở dashboard).
    Chốt: sổ đăng ký còn sống + hòm thư còn khối bài + giác quan độ tươi còn dây."""
    dk = REPO / "tools" / "dang_ky_tong_thuat.py"
    if not dk.exists():
        return False, "thiếu tools/dang_ky_tong_thuat.py"
    hom = (REPO / "tools" / "dung_hom_thu.py").read_text(encoding="utf-8")
    if "so-tong-thuat.json" not in hom:
        return False, "hòm thư KHÔNG còn đọc sổ bài tổng thuật — sản phẩm biến mất khỏi một-cửa"
    tdx = (REPO / "tools" / "tu_de_xuat_viec.py").read_text(encoding="utf-8")
    if "dang_ky_tong_thuat" not in tdx:
        return False, "bảng tự-đề-xuất mất giác quan độ tươi bài tổng thuật"
    # khớp chủ đề phải theo RANH GIỚI TỪ, không phải chuỗi con
    vb = dk.read_text(encoding="utf-8")
    if "la_viet_tat" not in vb:
        return False, ("khớp chủ đề quay lại kiểu chuỗi con — «CAP» sẽ trúng «cấp», "
                       "«THA» trúng «tha», mọi bài dính mọi chủ đề")
    return True, "bài tổng thuật có sổ đăng ký + mặt trong hòm thư + giác quan độ tươi"


def bh65_dinh_danh_guideline_phai_khai_ai_xac_nhan():
    """20/08 — khớp guideline tự động chỉ chứng minh «đúng tổ chức + đúng loại ấn
    phẩm», KHÔNG chứng minh «đúng bản CHỦ LỰC» (đo thật: nhánh IDSA/ATS ra guideline
    hẹp về xét nghiệm acid nucleic; Maastricht ra bản IV/V thay vì VI). Nếu danh bạ
    không phân biệt máy-khớp với người-chốt thì bài tổng thuật sẽ trích guideline
    lệch mà không ai biết. Chốt: mọi nguồn có PMID phải khai `xac_nhan`."""
    f = REPO / "EBM-Dashboards" / "nguon_chuan" / "danh-ba-nguon-chuan.json"
    if not f.exists():
        return True, "chưa có danh bạ nguồn chuẩn (bỏ qua)"
    db = json.loads(f.read_text(encoding="utf-8"))
    thieu = [f"{ma}/{n['to_chuc']}" for ma, cd in db["chu_de"].items()
             for n in cd["nguon"] if n.get("pmid") and not n.get("xac_nhan")]
    if thieu:
        return False, f"{len(thieu)} nguồn có PMID mà KHÔNG khai xac_nhan — {thieu[0]}"
    tool = (REPO / "tools" / "nap_guideline_pmc.py").read_text(encoding="utf-8")
    if '"may"' not in tool or "--chot" not in tool:
        return False, "công cụ nạp guideline mất nhãn «may»/đường «--chot» của người"
    return True, "mọi định danh guideline đều khai ai xác nhận"


def bh66_cong_trich_dan_khong_bao_dam_dung_lam_sang():
    """20/08 — phát hiện đắt nhất của đợt benchmark: 5 bài tổng thuật do máy viết
    có trích dẫn HOÀN HẢO (7/7 dòng Vancouver khớp từng trường, mọi con số truy
    được về tóm tắt, cổng hình thức PASS) mà thẩm định đối kháng vẫn bắt 13 LỖI
    NẶNG, trong đó có lỗi hại người bệnh: ngưỡng kali của MRA bị gán cho ACE-I;
    thiếu luật NGỪNG MRA khi K không giữ được <5,5 (COR 3: Harm); khẳng định mồ
    côi trái điều kiện khởi trị; nói «không nguồn nào nêu mốc chỉnh liều» trong
    khi guideline có mục riêng; dán N gộp của cả tổng quan cho từng ước lượng.

    Bài học: CỔNG TRÍCH DẪN LÀ ĐIỀU KIỆN CẦN, KHÔNG ĐỦ. Chốt giữ bảng 5 lớp lỗi
    nội dung trong skill + yêu cầu một lượt thẩm định ĐỘC LẬP cho bài dùng vào
    quyết định thực hành."""
    f = REPO / "sync" / "skills" / "tong-thuat-chung-cu" / "SKILL.md"
    if not f.exists():
        return False, "thiếu nguồn skill tong-thuat-chung-cu"
    vb = f.read_text(encoding="utf-8")
    if "điều kiện CẦN, không đủ" not in vb and "điều kiện CẦN" not in vb:
        return False, "skill mất cảnh báo «cổng trích dẫn là điều kiện cần, không đủ»"
    thieu = [x for x in ("gán SAI nhóm thuốc", "NGỪNG thuốc", "MỒ CÔI",
                         "CHƯA đọc toàn văn", "N GỘP") if x not in vb]
    if thieu:
        return False, f"skill mất {len(thieu)} lớp lỗi nội dung trong bảng tự soi — {thieu[0]}"
    # Ba lớp thêm 21/08 sau ba vòng thẩm định liên tiếp trên MỘT bài. Cả ba đều là lỗi
    # mà cổng trích dẫn không thể thấy: chữ trích đúng nguyên văn, chỉ có ĐÍCH hoặc CÁN
    # CÂN là sai. ⑩ đáng nhớ nhất — bản «sửa cho đúng mức» theo một guideline lại làm
    # thuốc trông yếu hơn nền chứng cứ, vì guideline kia đặt mức cao hơn cho cùng quần thể.
    thieu2 = [x for x in ("gắn NHẦM khuyến cáo", "LỐI RA",
                          "CẢ BỘ NGUỒN của bài") if x not in vb]
    if thieu2:
        return False, f"skill mất lớp lỗi bổ sung 21/08 — {thieu2[0]}"
    if "thẩm định ĐỘC LẬP" not in vb:
        return False, "skill không còn đòi lượt thẩm định độc lập cho bài dùng thực hành"
    # «0 lỗi nặng» KHÔNG phải điều kiện dừng: đo thật trên bài suy tim, số lỗi nặng về 0
    # từ vòng hai nhưng vòng ba và vòng bốn vẫn ra thêm lỗi CÂN BẰNG do chính vòng sửa
    # trước gây ra. Dừng khi một vòng không còn phát hiện nào do vòng sửa trước sinh ra.
    if "đừng dừng ở «0 lỗi" not in vb:
        return False, "skill mất luật «0 lỗi nặng chưa phải điều kiện dừng»"
    # Đo 21/08: bốn vòng liền lỗi tái sinh ĐÚNG khối vừa vá; viết lại trọn khối thì
    # vòng sau sạch khối đó. Luật này là thứ duy nhất phá được vòng lặp vá-rồi-hỏng.
    if "VIẾT LẠI TRỌN KHỐI" not in vb:
        return False, "skill mất luật «lỗi tái sinh đúng chỗ vừa vá thì viết lại trọn khối»"
    return True, "skill giữ đủ 8 lớp lỗi nội dung + đòi thẩm định độc lập + luật điều kiện dừng"


def bh70_bo_dong_bo_khong_tro_vao_thu_khong_co():
    """21/08 — bộ hợp nhất `dong_bo_skill_claude_codex.py` được commit và tài liệu
    hoá ở CẢ AGENTS.md lẫn CLAUDE.md, nhưng gọi vào BỐN thứ không tồn tại:
      · `tools/dong_bo_plugin_claude_codex.py` — chưa bao giờ có trong repo
      · `sync/skills/plugin-router-chatgpt/scripts/build_catalog.py` — chỉ có trên Mac
      · cờ `--nguon-la-chuan` của `dong_bo_skill.py` — **chưa từng tồn tại**
        (`git log -S` không ra lần thêm nào), nên argparse trả mã 2
      · và chính nó tự chặn Windows bằng `if os.name == "nt": return 1`
    Đo được: `--ap-dung` thoát mã 2 trên máy sạch, `--dong-bo-plugin` in
    `can't open file`. Tức lệnh đồng bộ được tin là «xương sống tự động» chưa từng
    chạy trọn ở đâu, và trên Windows thì chưa từng chạy dòng nào.

    Đây là họ lỗi TÀI LIỆU-TRỎ-VÀO-KHOẢNG-KHÔNG, đúng thứ commit b7c4bb7 nói là đi
    sửa («bỏ lại là doctrine trỏ vào công cụ không có trong repo») — mà bản thân
    nó lại mang vào bốn cái mới. Chốt vì thế KHÔNG đếm chữ trong tài liệu: nó phân
    giải TỪNG công cụ được gọi và TỪNG cờ được truyền, đối chiếu với argparse thật
    của file đích. Cờ sai tên là lỗi im lặng — argparse chỉ kêu lúc chạy thật.
    """
    import ast

    gm = REPO / "tools/dong_bo_skill_claude_codex.py"
    if not gm.exists():
        return False, "thiếu bộ hợp nhất dong_bo_skill_claude_codex.py"
    vb = gm.read_text(encoding="utf-8")

    # (a) không còn tự chặn Windows
    cay = ast.parse(vb)
    for nut in ast.walk(cay):
        if (isinstance(nut, ast.Compare) and isinstance(nut.left, ast.Attribute)
                and nut.left.attr == "name"
                and any(isinstance(c, ast.Constant) and c.value == "nt"
                        for c in nut.comparators)):
            return False, "bộ hợp nhất lại tự chặn Windows bằng os.name == 'nt'"

    def co_o(ham: ast.FunctionDef) -> tuple[list[str], list[str]]:
        """Trả (công cụ tools/*.py được gọi, cờ --* truyền trong cùng hàm)."""
        cong_cu, co = [], []
        for n in ast.walk(ham):
            if isinstance(n, ast.Constant) and isinstance(n.value, str):
                if n.value.startswith("tools/") and n.value.endswith(".py"):
                    cong_cu.append(n.value)
                elif n.value.startswith("--"):
                    co.append(n.value)
        return cong_cu, co

    thieu, sai_co = [], []
    for ham in [n for n in ast.walk(cay) if isinstance(n, ast.FunctionDef)]:
        cong_cu, co_truyen = co_o(ham)
        for tuong_doi in cong_cu:
            dich = REPO / tuong_doi
            if not dich.exists():
                thieu.append(f"{ham.name}() gọi {tuong_doi} — không có trong repo")
                continue
            nhan = set()
            for n in ast.walk(ast.parse(dich.read_text(encoding="utf-8"))):
                if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                        and n.func.attr == "add_argument"):
                    nhan.update(a.value for a in n.args
                                if isinstance(a, ast.Constant) and isinstance(a.value, str))
            for c in co_truyen:
                if c not in nhan:
                    sai_co.append(f"{ham.name}() truyền {c} cho {tuong_doi} "
                                  f"— argparse của nó KHÔNG nhận cờ này")
    if thieu:
        return False, f"{len(thieu)} công cụ được gọi mà không có: {thieu[0]}"
    if sai_co:
        return False, f"{len(sai_co)} cờ không được chấp nhận: {sai_co[0]}"

    # (b) hai script cài đặt phải nối CẢ HAI runtime — bỏ sót Codex thì máy đó
    #     không thấy skill nào, đúng tình trạng Windows trước 21/08.
    #
    # KIỂM BẰNG HÀNH VI, KHÔNG ĐẾM CHUỖI. Bản đầu của chốt này chỉ hỏi «chuỗi
    # .codex có trong file không» — và đột biến gỡ Codex khỏi vòng lặp vẫn XANH,
    # vì chữ .codex còn nguyên trong chú thích. Đúng bẫy TAUTOLOGY mà kho đã vấp ở
    # guardrail G3/G8: đếm chuỗi thì thứ được canh là câu chữ, không phải hành vi.
    import os as _os
    import shutil as _sh
    import subprocess
    import tempfile

    sh = REPO / "sync/link-skills.sh"
    ps = REPO / "sync/link-skills.ps1"
    for f in (sh, ps):
        if not f.exists():
            return False, f"thiếu {f.name}"

    bash = _sh.which("bash")
    if bash:
        # Chạy THẬT với HOME tạm rồi đếm liên kết sinh ra ở từng runtime.
        with tempfile.TemporaryDirectory() as tam:
            kq = subprocess.run([bash, str(sh)], check=False, capture_output=True,
                                text=True, timeout=120,
                                env={"HOME": tam, "PATH": _os.environ.get("PATH", "")})
            if kq.returncode != 0:
                return False, f"link-skills.sh chạy lỗi: {(kq.stderr or '').strip()[:120]}"
            for runtime in (".claude", ".codex"):
                d = Path(tam) / runtime / "skills"
                n = sum(1 for x in d.iterdir() if x.is_symlink()) if d.is_dir() else 0
                if n == 0:
                    return False, (f"link-skills.sh KHÔNG nối {runtime}/skills "
                                   f"(chạy thật, 0 liên kết) — runtime đó sẽ trắng skill")

    # Bản .ps1: chạy THẬT nếu máy có PowerShell (tức trên chính Windows, nơi nó
    # phải đúng). Máy không có thì kiểm tĩnh — nhưng loại cả CHÚ THÍCH lẫn dòng
    # `Write-Host`: bản đầu của chốt để lọt đột biến vì chuỗi ".codex\skills" vẫn
    # còn ở dòng in hướng dẫn cuối file. Chữ dùng để HIỂN THỊ không phải hành vi.
    pwsh = _sh.which("pwsh") or _sh.which("powershell")
    if pwsh:
        with tempfile.TemporaryDirectory() as tam:
            moi_truong = dict(_os.environ, USERPROFILE=tam, HOME=tam)
            kq = subprocess.run([pwsh, "-ExecutionPolicy", "Bypass", "-File", str(ps)],
                                check=False, capture_output=True, text=True,
                                timeout=180, env=moi_truong)
            if kq.returncode != 0:
                return False, f"link-skills.ps1 chạy lỗi: {(kq.stderr or '').strip()[:120]}"
            for runtime in (".claude", ".codex"):
                d = Path(tam) / runtime / "skills"
                n = sum(1 for _x in d.iterdir()) if d.is_dir() else 0
                if n == 0:
                    return False, (f"link-skills.ps1 KHÔNG nối {runtime}/skills "
                                   f"(chạy thật, 0 mục)")
    else:
        ma_ps = "\n".join(
            d for d in ps.read_text(encoding="utf-8-sig").splitlines()
            if not d.lstrip().startswith("#") and not d.lstrip().startswith("Write-Host"))
        for runtime in (".claude", ".codex"):
            if f"{runtime}\\skills" not in ma_ps:
                return False, (f"link-skills.ps1 không nối {runtime}\\skills trong phần MÃ "
                               f"(chữ trong chú thích hay dòng in không tính)")
    # (c) Sổ khai dùng chung phải THEO ĐƯỢC git. `.gitignore` của repo mở đầu bằng
    # `/*` rồi un-ignore từng mục, nên một file mới ở gốc `sync/` bị loại IM LẶNG:
    # cơ chế «hai máy đọc cùng một bản ý định» sẽ không có bản nào đi sang máy kia.
    # Đúng họ lỗi mà chính BH này đi vá, chỉ khác chỗ hỏng là .gitignore.
    git = _sh.which("git")
    if git:
        for ten in ("sync/plugin-manifest.json", "sync/hooks-sessionstart.json"):
            kq = subprocess.run([git, "check-ignore", "-q", ten], cwd=REPO,
                                check=False, capture_output=True, timeout=60)
            if kq.returncode == 0:
                return False, (f"{ten} đang bị .gitignore loại — sổ khai dùng chung "
                               f"không đi được sang máy kia")
    return True, ("công cụ + cờ phân giải được · Windows không bị chặn · "
                  "link-skills.sh chạy thật nối đủ 2 runtime · sổ khai theo được git")


def bh71_lenh_gop_phu_du_lan_va_dung_khi_nguy_hiem():
    """21/08 — hệ có đủ công cụ cho từng làn đồng bộ nhưng KHÔNG có lối vào duy
    nhất: muốn máy này khớp máy kia phải nhớ đúng thứ tự CHÍN thứ rời rạc. Lệnh gộp
    duy nhất đang có (`upgrade_verify.py`, 27 bước) kiểm HỆ AGENT và không chạm một
    làn đồng bộ nào. Quy trình phải nhớ chín bước là quy trình sẽ bị bỏ sót bước —
    và bỏ sót ở đây không kêu, nó chỉ làm máy kia thiếu lặng lẽ.

    Chốt canh ba thứ mà `dong_bo_tat_ca.py` phải giữ, tất cả bằng HÀNH VI:
      (a) Chốt an toàn 🔴 phải DỪNG mọi làn sau — đồng bộ khi cây thư mục đang hỏng
          là nhân bản cái hỏng sang máy kia. Nhưng công cụ VẮNG MẶT thì KHÔNG được
          dừng: thiếu nguyên liệu không phải bằng chứng nguy hiểm (BH08).
      (b) Danh sách làn khai ra phải KHỚP làn chạy thật — thêm công cụ đồng bộ mới
          mà quên nối thì lệnh gộp âm thầm phủ ít hơn tên gọi của nó.
      (c) Nút bấm đúp phải THEO ĐƯỢC git và giữ CRLF. `.gitattributes` đặt
          `eol=lf` toàn cục; batch có khối nhiều dòng đọc LF-only là hỏng thất
          thường — hỏng kiểu khó truy vì file vẫn mở được và vài dòng đầu vẫn chạy.
    """
    import ast
    import subprocess

    f = REPO / "tools/dong_bo_tat_ca.py"
    if not f.exists():
        return False, "thiếu tools/dong_bo_tat_ca.py — hệ lại không có lối vào duy nhất"
    m = _nap(f, "dbtc_bh68")

    # (a) quy tắc dừng, kiểm bằng cách GỌI hàm chứ không đọc chữ
    do = m.KetQua("thử", ma=2)
    vang = m.KetQua("thử", ma=1)
    vang_mat = m.KetQua("thử", bo_qua="máy chưa có công cụ")
    if not m.phai_dung_som(do):
        return False, "chốt an toàn 🔴 KHÔNG còn dừng — sẽ nhân bản cây hỏng sang máy kia"
    if m.phai_dung_som(vang):
        return False, "🟡 đã làm dừng cả lệnh — cảnh báo thường không được chặn"
    if m.phai_dung_som(vang_mat):
        return False, "công cụ VẮNG MẶT làm dừng cả lệnh — biến CHƯA BIẾT thành CÓ VẤN ĐỀ"

    # (b) khai vs chạy. Dùng --liet-ke-lan (không chạy làn nào) để chốt vẫn nhanh
    # và ngoại tuyến: chạy thật sẽ gọi `git fetch`, tức chạm mạng.
    khai = m.ten_cac_lan()
    if len(khai) < 8:
        return False, f"lệnh gộp chỉ còn khai {len(khai)} làn (cần ≥8)"
    # `cac_lan()` là nguồn duy nhất: mỗi mục phải gọi được và tên phải khớp danh
    # sách khai. Bản đầu của chốt so với chuỗi trong main() và bắt được đúng việc
    # hai chỗ đang lệch — nay lệch đó đã được đóng bằng THIẾT KẾ, chốt canh để nó
    # không mở lại. Chỉ gọi các làn KHÔNG chạm mạng/tiến trình con: ở đây chỉ kiểm
    # tên và tính gọi được, không thực thi (bộ chốt phải nhanh và ngoại tuyến).
    bo = m.cac_lan()
    if [t for t, _ in bo] != khai:
        return False, "ten_cac_lan() lệch cac_lan() — lại có hai bản danh sách làn"
    khong_goi_duoc = [t for t, h in bo if not callable(h)]
    if khong_goi_duoc:
        return False, f"làn không gọi được: {khong_goi_duoc[0]}"
    goc = ast.parse(f.read_text(encoding="utf-8"))
    ham_main = next((n for n in ast.walk(goc)
                     if isinstance(n, ast.FunctionDef) and n.name == "main"), None)
    if ham_main is None:
        return False, "không tìm thấy main() trong dong_bo_tat_ca.py"
    if not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
               and n.func.id == "cac_lan" for n in ast.walk(ham_main)):
        return False, ("main() không còn lặp trên cac_lan() — làn khai và làn chạy "
                       "có thể lệch nhau trở lại")

    # (c) nút bấm đúp
    for ten in ("sync/dong-bo-tat-ca.command", "sync/dong-bo-tat-ca.cmd"):
        if not (REPO / ten).exists():
            return False, f"thiếu nút bấm đúp {ten}"
    git = _sh_which("git")
    if git:
        for ten in ("sync/dong-bo-tat-ca.command", "sync/dong-bo-tat-ca.cmd"):
            if subprocess.run([git, "check-ignore", "-q", ten], cwd=REPO,
                              check=False, capture_output=True, timeout=60).returncode == 0:
                return False, f"{ten} bị .gitignore loại — nút bấm không đi sang máy kia"
        ra = subprocess.run([git, "check-attr", "eol", "--", "sync/dong-bo-tat-ca.cmd"],
                            cwd=REPO, check=False, capture_output=True, text=True, timeout=60)
        if "crlf" not in (ra.stdout or ""):
            return False, ".cmd không được ép CRLF — batch LF-only hỏng thất thường trên Windows"
    return True, (f"dừng đúng khi nguy hiểm · {len(khai)} làn khai khớp main() · "
                  f"nút bấm đúp theo git, .cmd giữ CRLF")


def bh81_khoa_cau_hinh_nguoi_dung_duoc_khoi_phuc():
    """22/08 — bác sĩ than nhiều tháng «skill cài rồi mà gọi không được». Nguyên
    nhân gốc tìm 10/08 là ngân sách danh sách skill (mặc định 0,01 = 8.000 ký tự,
    kho ~869 skill cần ~45.000 ⇒ Claude Code CẮT). Đã vá bằng 0.08 trên cả hai máy.

    Chỗ hở còn lại: **app Claude ghi đè ~/.claude/settings.json** (đo hai lần trên
    Mac: 17/08 kho 839→1311 skill, 21/08 870→1319). Đợt ghi đè xoá cờ enabledPlugins
    — có `kiem_co_tat_plugin_trung.py` khôi phục — VÀ xoá luôn bản vá ngân sách, mà
    KHÔNG công cụ nào khôi phục: `kiem_plugin_day_du.py` chỉ ĐỌC và báo 🔴, còn
    `kiem_co_tat_plugin_trung.py` tự giới hạn «chỉ chạm enabledPlugins». Nên mỗi lần
    app ghi đè là triệu chứng cũ quay lại nguyên vẹn.

    Chốt canh ba vế, bằng HÀNH VI:
      (a) khôi phục đúng khoá đã khai và KHÔNG đụng khoá nào khác — đè cả file là
          xoá mất enabledPlugins/hooks/theme của máy;
      (b) công cụ được nối vào `tu_sua_chua.py` (chạy mỗi phiên) — không nối thì
          nó chỉ tồn tại chứ không canh gì;
      (c) bản khai theo được git — `/sync/*` loại mọi file gốc, và đây là lần thứ
          BA vấp đúng cái bẫy ignore-im-lặng đó.
    """
    import json
    import subprocess
    import tempfile

    f = REPO / "tools/kiem_cau_hinh_nguoi_dung.py"
    khai_f = REPO / "sync/cau-hinh-nguoi-dung.json"
    if not f.exists():
        return False, "thiếu tools/kiem_cau_hinh_nguoi_dung.py — khoá ngân sách lại không ai khôi phục"
    if not khai_f.exists():
        return False, "thiếu sync/cau-hinh-nguoi-dung.json — không biết phải giữ khoá nào"
    khai = (json.loads(khai_f.read_text(encoding="utf-8")).get("khoa") or {})
    if "skillListingBudgetFraction" not in khai:
        return False, "bản khai mất skillListingBudgetFraction — đúng khoá gây «gọi skill không được»"

    # (a) hành vi: mất khoá → khôi phục, và mọi khoá khác còn nguyên
    m = _nap(f, "kchnd_bh72")
    with tempfile.TemporaryDirectory() as tam:
        st = Path(tam) / "settings.json"
        goc = {"enabledPlugins": {"x@y": False}, "hooks": {"SessionStart": [1]}, "theme": "dark"}
        st.write_text(json.dumps(goc), encoding="utf-8")
        m.SETTINGS = st
        # Nuốt đầu ra của công cụ: bộ chốt phải im khi mọi thứ ổn, không kéo theo
        # báo cáo của thứ nó đang kiểm.
        import contextlib
        import io
        cu_argv = sys.argv
        try:
            sys.argv = ["x", "--ap-dung"]
            with contextlib.redirect_stdout(io.StringIO()), \
                 contextlib.redirect_stderr(io.StringIO()):
                m.main()
        finally:
            sys.argv = cu_argv
        sau = json.loads(st.read_text(encoding="utf-8"))
        for ten, muc in khai.items():
            if sau.get(ten) != muc.get("gia_tri"):
                return False, f"không khôi phục được {ten}"
        for ten, gt in goc.items():
            if sau.get(ten) != gt:
                return False, (f"khoá KHÁC bị đụng: {ten} — đè cả settings.json là xoá "
                               f"mất cấu hình riêng của máy")

    # (b) đã nối vào tự-sửa-chữa
    tsc = (REPO / "tools/tu_sua_chua.py").read_text(encoding="utf-8")
    if "kiem_cau_hinh_nguoi_dung.py" not in tsc:
        return False, "chưa nối vào tu_sua_chua.py — công cụ tồn tại nhưng không canh gì"

    # (c) bản khai theo được git
    git = _sh_which("git")
    if git and subprocess.run([git, "check-ignore", "-q", "sync/cau-hinh-nguoi-dung.json"],
                              cwd=REPO, check=False, capture_output=True,
                              timeout=60).returncode == 0:
        return False, "sync/cau-hinh-nguoi-dung.json bị .gitignore loại — máy kia không nhận được"
    return True, "khôi phục đúng khoá · không đụng khoá khác · đã nối tu_sua_chua · theo được git"


def bh58_quyet_dinh_da_duyet_khong_lat_nguoc():
    """16/08 — vòng học NỘI DUNG chưa từng được đóng: 15+ quyết định lâm sàng
    bác sĩ duyệt 13–14/08 chỉ nằm trong văn xuôi CLAUDE.md; dashboard sinh lại
    từ skill cũ có thể LẬT NGƯỢC IM LẶNG (tiền lệ thật: 5 mục Đau Đầu tái lệch
    là hệ quả đợt sửa 12/08; CSS «sửa xong lại như cũ»).

    Hai vế: (1) kho THẬT không có tái phạm và sổ đọc được; (2) chốt còn RĂNG —
    fixture item lật consider→apply phải ra đúng 1 🔴 (đột biến tự chạy, chống
    chốt bị sửa thành luôn-xanh)."""
    import importlib.util as _ilu
    import tempfile
    duong = REPO / "tools" / "kiem_quyet_dinh_da_duyet.py"
    if not duong.exists():
        return False, "kiem_quyet_dinh_da_duyet.py BIẾN MẤT — vòng học nội dung lại hở"
    spec = _ilu.spec_from_file_location("_kqd_bh58", duong)
    mod = _ilu.module_from_spec(spec)
    sys.modules["_kqd_bh58"] = mod
    try:
        spec.loader.exec_module(mod)
        khop, lech, mu = mod.kiem()
    except Exception as e:  # noqa: BLE001 — chốt nhắc không được làm chết bộ chạy
        return False, f"chốt quyết định không chạy được: {e}"
    if lech:
        return False, f"{len(lech)} quyết định ĐÃ DUYỆT bị lật ngược — {lech[0][:90]}"
    with tempfile.TemporaryDirectory() as td:
        goc = Path(td)
        (goc / "so.json").write_text(json.dumps({"quyet_dinh": [
            {"file": "A.html", "item": "ITEM-01", "ky_vong": {"decision": "consider"},
             "duyet": "x", "ly_do": "fixture"}]}), encoding="utf-8", newline="\n")
        # bh10-mien: fixture TemporaryDirectory tự-đột-biến chốt BH58 — không phải dashboard thật
        (goc / "A.html").write_text(
            'const DATA = { items: [\n  {id:"ITEM-01", pmid:"1", decision:"apply"},\n]};'
            "\n// HẾT KHỐI DATA", encoding="utf-8", newline="\n")
        _, lech_gia, _ = mod.kiem(goc / "so.json", goc)
        if len(lech_gia) != 1:
            return False, "chốt MẤT RĂNG — fixture lật consider→apply mà không ra 🔴"
    return True, f"✓ {len(khop)} quyết định còn nguyên · ⚪ {len(mu)} · răng còn (fixture đỏ đúng)"


def bh55_khong_duong_dan_cung_mot_may():
    """15/08 — HỌ LỖI TÁI PHÁT NHIỀU NHẤT KHO: tool viết cho MỘT máy, gãy IM LẶNG
    trên máy kia (ensure_strict_source · run_retraction_and_med_safety ·
    docx_sang_pdf · kiem_do_tuoi/os.getuid · 7 script vietnamize/cp1252 —
    mỗi lần vá một tool, chưa từng có chốt quét CẢ KHO).

    Chốt chạy kiem_tuong_thich_da_nen.py: exit 2 (có 🔴 — đường dẫn user ghi
    cứng / getuid không nhận thức nền tảng / subprocess literal python3) là đỏ.
    Ngay lượt quét đầu đã bắt 1 ca thật: generate_cerebrovascular ROOT=C:\\Users
    — chưa từng chạy được trên Mac. Đột biến gieo-file-đường-dẫn-cứng → đỏ ✓.
    Nhóm 🟡 (104 mục, chủ yếu cp1252 chưa reconfigure) là tồn kho soi dần,
    KHÔNG chặn — 🔴 oan hàng loạt sẽ dạy người ta bỏ 🔴.
    """
    import subprocess
    duong = REPO / "tools" / "kiem_tuong_thich_da_nen.py"
    if not duong.exists():
        return False, "kiem_tuong_thich_da_nen.py biến mất"
    r = subprocess.run([sys.executable, str(duong)], capture_output=True,
                       text=True, cwd=REPO, timeout=180)
    if r.returncode == 2:
        dong_do = [x.strip() for x in r.stdout.splitlines() if "🔴" in x][:3]
        return False, "tool viết-cho-một-máy quay lại: " + " | ".join(dong_do)
    if "KẾT:" not in r.stdout:
        return False, f"chốt đa nền không chạy trọn: {r.stderr.strip()[-100:]}"
    return True, "0 🔴 toàn kho tool (5 cây, ~268 file)"


def bh54_ma_thoat_rut_bai_ba_muc():
    """15/08 — bao_cao() sổ xác minh: còi ĐỎ (rc=2) CHỈ dành cho «rút BỎ HẲN đang
    được dashboard trích».

    Lỗi thật: BH34 tách phần IN từ 14/08 nhưng return vẫn `if rut: return 2` ⇒ ca
    rút-và-thay ĐÃ phân xử xong trong gói (verify_dashboard PASS với dải cảnh báo)
    vẫn làm chu_trinh in «🔴 xử lý trước khi dùng» vĩnh viễn — chuông không tắt
    được dạy người ta bỏ chuông. Chốt tiêm sổ giả: rút-bỏ-hẳn → 2; chỉ
    rút-và-thay → 1; đảo lại là đỏ.
    """
    import subprocess
    ma = (
        "import importlib.util,sys;"
        "sp=importlib.util.spec_from_file_location('so','tools/so_xac_minh_nguon.py');"
        "m=importlib.util.module_from_spec(sp);sys.modules['so']=m;sp.loader.exec_module(m);"
        "lam=lambda muc: (setattr(m,'doc_so',lambda: {'muc': muc}) or m.bao_cao(set(muc)));"
        "han={'pmid:1': {'loai':'pmid','gia_tri':'1','da_rut':True,"
        "'ghi_chu_rut':'retracted','cac_dashboard':['x.html'],"
        "'kiem_rut_luc':'2026-08-15T00:00:00','xac_minh_luc':'2026-08-15T00:00:00'}};"
        "thay={'pmid:2': {'loai':'pmid','gia_tri':'2','da_rut':True,'rut_va_thay':True,"
        "'ghi_chu_rut':'retracted','cac_dashboard':['x.html'],"
        "'kiem_rut_luc':'2026-08-15T00:00:00','xac_minh_luc':'2026-08-15T00:00:00'}};"
        "print('HAN=%d THAY=%d' % (lam(han), lam(thay)))"
    )
    r = subprocess.run([sys.executable, "-c", ma], capture_output=True, text=True,
                       cwd=REPO, timeout=120)
    if r.returncode != 0:
        return False, f"bao_cao không chạy được: {r.stderr.strip()[-120:]}"
    dong = [x for x in r.stdout.splitlines() if x.startswith("HAN=")]
    if not dong:
        return False, "không đọc được kết quả HAN/THAY"
    if dong[0] != "HAN=2 THAY=1":
        return False, (f"mã thoát sai ({dong[0]}) — rút-bỏ-hẳn phải 2, "
                       "rút-và-thay đơn thuần phải 1 (không kéo còi đỏ mãi)")
    return True, "rc: rút-bỏ-hẳn=2 · chỉ rút-và-thay=1"


def bh53_elink_chi_nhan_pubmed_pmc():
    """15/08 — PHA R5-D2: elink pubmed→pmc CHỈ được nhận linkname `pubmed_pmc`.

    Lỗi thật, nguy hiểm nhất của mảng toàn văn: bài KHÔNG có trong PMC (Polit &
    Beck 17654487) vẫn trả linkset `pubmed_pmc_refs` = 1.678 bài TRÍCH DẪN nó;
    bản đầu của gom_toan_van_oa vơ mọi dbto=="pmc" nên gắn TOÀN VĂN BÀI KHÁC vào
    PMID gốc — «56/62 OA» hoá 31/62, kho demo 5/5 nhiễm, và mọi phép hỏi/đối
    chiếu hạ nguồn chạy trên văn bản sai không một dòng báo. Chỉ vòng thẩm định
    toàn văn (⚪ hàng loạt ở ngưỡng kinh điển 0,78) mới lộ. Chốt gọi thẳng
    _parse_linksets với fixture mang CẢ HAI linkname — nhận nhầm refs là đỏ.
    """
    import importlib.util
    duong = REPO / "medical-ebm-automation" / "tools" / "gom_toan_van_oa.py"
    if not duong.exists():
        return False, "gom_toan_van_oa.py biến mất"
    sp = importlib.util.spec_from_file_location("gom_tv", duong)
    m = importlib.util.module_from_spec(sp)
    import sys as _sys
    _sys.modules["gom_tv"] = m
    sp.loader.exec_module(m)
    fixture = {"linksets": [
        {"ids": ["17654487"], "linksetdbs": [
            {"dbto": "pmc", "linkname": "pubmed_pmc_refs", "links": ["13469762"]}]},
        {"ids": ["34017606"], "linksetdbs": [
            {"dbto": "pmc", "linkname": "pubmed_pmc", "links": ["8114273"]},
            {"dbto": "pmc", "linkname": "pubmed_pmc_refs", "links": ["12832380"]}]},
    ]}
    ra = m._parse_linksets(fixture)
    if "17654487" in ra:
        return False, ("_parse_linksets lại vơ pubmed_pmc_refs — bài không-OA sẽ "
                       "được gắn toàn văn của bài ĐI TRÍCH DẪN nó")
    if ra.get("34017606") != "8114273":
        return False, f"mất ánh xạ pubmed_pmc hợp lệ: {ra}"
    return True, "chỉ nhận pubmed_pmc; refs bị loại đúng"


def bh52_g0_kiem_rut_bai_tai_cua():
    """15/08 — PHA R4/R5: G0 phải TỰ kiểm rút bài nền y văn (R1C), không tin PMID.

    Lỗi thật: đề tài demo đầu tiên đi qua G0 với một Expression-of-Concern trong
    nền mà không dòng nào nói ra — chỉ lộ khi kiểm tay. Chốt gọi THẲNG
    guardrail_check_g0 với PMID Wakefield 9500320 (retracted, nền Retraction
    Watch NGOẠI TUYẾN có phán quyết ⇒ chốt chạy được không cần mạng): errors
    phải mang R1C + đúng PMID. Tháo R1C là đỏ ngay.
    """
    # run_g0_auto import defusedxml ở mức module — python3 hệ thống không có
    # (đúng lớp BH34/BH05: hook chạy python3). Chốt vì thế chạy qua VENV tường
    # minh, đa nền tảng; venv vắng mặt thì khai rõ thay vì đỏ oan/chết phiên.
    import subprocess
    import sys as _sys
    venv = Path.home() / ".ebm-venv" / ("Scripts/python.exe" if _sys.platform == "win32"
                                        else "bin/python")
    if not venv.exists():
        return True, "venv ~/.ebm-venv vắng mặt trên máy này — chốt bỏ qua CÓ KHAI BÁO"
    ma = ("import importlib.util,sys,json;"
          "sp=importlib.util.spec_from_file_location('g0','tools/run_g0_auto.py');"
          "m=importlib.util.module_from_spec(sp);sys.modules['g0']=m;"
          "sp.loader.exec_module(m);"
          "print(json.dumps(m.guardrail_check_g0('',{'all_pmids':['9500320']}),"
          "ensure_ascii=False))")
    r = subprocess.run([str(venv), "-c", ma], capture_output=True, text=True,
                       cwd=REPO / "medical-ebm-automation", timeout=180)
    if r.returncode != 0:
        return False, f"guardrail_check_g0 không chạy được: {r.stderr.strip()[-120:]}"
    goi = r.stdout
    if "R1C" not in goi:
        return False, "R1C biến mất — G0 lại tin PMID còn hiệu lực mà không kiểm"
    if "9500320" not in goi:
        return False, "R1C chạy nhưng KHÔNG bắt bài đã rút 9500320 (nền RW ngoại tuyến có)"
    return True, "G0 tự bắt bài đã rút tại cửa nhận (R1C sống, chạy được ngoại tuyến)"


def bh60_array_field_khong_gay_o_ngoac_vuong():
    """18/08 — `array_field` cắt mảng ở dấu `]` NẰM TRONG chuỗi truy vấn PubMed.

    Lỗi thật, đo được ngày 18/08 khi dựng gói «đau mạn tính»: bản cũ dùng lớp ký
    tự `[^\\]]*` để lấy phần trong `[...]`, nên nó DỪNG ở dấu `]` ĐẦU TIÊN gặp
    được. Nhưng MỌI truy vấn PubMed đều mang ngoặc vuông — `[MeSH]`, `[Title]`,
    `[pt]`, `[ta]`. Hệ quả: dashboard nào ghi TRUNG THỰC chiến lược tìm (đúng thứ
    `DATA.standards.searchSources` sinh ra để ghi, và đúng thứ PRISMA-S đòi) thì
    mảng bị cắt còn 1 phần tử ⇒ cổng ném LỖI CỨNG «searchSources cần ≥2 nguồn tìm
    kiếm độc lập» TRÊN DỮ LIỆU HOÀN TOÀN ĐÚNG.

    Đây đúng họ lỗi nguy hiểm nhất của hệ và đã gặp ba lần: cổng NÓI SAI về dữ
    liệu ĐÚNG (bug `field()` nháy lồng 12/08 — che 1 lỗi an toàn thật; BH21 — hai
    parser của cùng một dữ liệu bất đồng). Nó phạt đúng người khai báo trung thực
    nhất, và cách «sửa» tự nhiên nhất lại là bỏ bớt truy vấn khỏi provenance.

    Chốt gọi THẲNG `array_field` đang sống, ngoại tuyến: (a) mảng có ngoặc vuông
    lồng phải đọc đủ 3 phần tử; (b) nháy đơn lồng trong chuỗi nháy kép không được
    làm vỡ phần tử; (c) chuỗi nối kiểu JS vẫn phải GỘP (giữ bản vá BH13/BH21).
    """
    import importlib.util
    kq = []
    for ten, duong in (("runtime", REPO / "EBM-Dashboards/tools/verify_dashboard.py"),
                       ("nguồn", REPO / "sync/skills/cap-nhat-chung-cu-y-khoa/tools/verify_dashboard.py")):
        if not duong.exists():
            return False, f"thiếu bản {ten}: {duong}"
        sp = importlib.util.spec_from_file_location(f"vd_{ten}", duong)
        m = importlib.util.module_from_spec(sp)
        import sys as _s
        _s.modules[sp.name] = m
        sp.loader.exec_module(m)

        # (a) ngoặc vuông TRONG chuỗi — ca đã làm gãy bản cũ
        mau = ('searchSources:["PubMed E-utilities. Truy vấn: '
               "'chronic pain[MeSH] AND practice guideline[pt]'" '",'
               '"openFDA drug/label API — nhãn gabapentin mục 5.7",'
               '"Europe PMC — toàn văn CDC 2022"],')
        r = m.array_field(mau, "searchSources")
        if len(r) != 3:
            return False, (f"[{ten}] array_field đọc {len(r)}/3 phần tử khi chuỗi chứa "
                           f"'[MeSH]'/'[pt]' — mảng lại bị cắt ở ngoặc vuông")
        if "[MeSH]" not in r[0]:
            return False, f"[{ten}] phần tử 1 mất nội dung trong ngoặc vuông: {r[0][:70]!r}"

        # (b) nháy đơn lồng không được làm vỡ phần tử
        if not r[0].endswith("'"):
            return False, f"[{ten}] nháy đơn lồng làm vỡ phần tử: {r[0][-40:]!r}"

        # (c) chuỗi nối kiểu JS vẫn phải GỘP (bản vá BH13/BH21 còn nguyên)
        noi = 'references:["Phần đầu. "+"https://vi-du.org/x","Bài hai."]'
        r2 = m.array_field(noi, "references")
        if len(r2) != 2:
            return False, f"[{ten}] chuỗi nối JS không còn được gộp: đọc {len(r2)}/2"
        kq.append(ten)
    return True, f"array_field chịu được ngoặc vuông + nháy lồng, vẫn gộp chuỗi nối ({', '.join(kq)})"


def bh61_khoa_summary_sai_ten_phai_bi_bat():
    """18/08 — hai dashboard mới nhất ghi `notDo:` trong khi template VÀ cả ba bộ
    sinh phái sinh (bản đọc · Word · bộ ba) đều đọc `dontDo` ⇒ panel
    «Không nên / giới hạn» render RỖNG trên MỌI sản phẩm. Thứ bị giấu là nội
    dung an toàn thật: «KHÔNG ngừng opioid ĐỘT NGỘT» và «không bình thường hoá
    Hb bằng ESA — tăng biến cố tim mạch». Không cổng nào bắt được vì khối DATA
    vẫn đúng cú pháp và mọi luật khác vẫn chạy đúng.

    Cùng HỌ với `return` sớm 12/08 (che 73 mục) và BH27 (fail-open A12): công cụ
    vẫn chạy, vẫn in kết quả hợp lệ, nhưng thứ cần kiểm thì không bao giờ được
    kiểm. Chốt gọi THẲNG kiem_khoa_summary() nên nó kiểm HÀNH VI, không đếm chuỗi.
    """
    import importlib.util as _ilu
    duong = REPO / "EBM-Dashboards" / "tools" / "verify_dashboard.py"
    spec = _ilu.spec_from_file_location("_vd_bh61", duong)
    mod = _ilu.module_from_spec(spec)
    sys.modules["_vd_bh61"] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception as e:  # noqa: BLE001 — chốt nhắc không được làm chết bộ chạy
        return False, f"không nạp được verify_dashboard: {e}"
    if not hasattr(mod, "kiem_khoa_summary"):
        return False, "verify_dashboard KHÔNG còn hàm kiem_khoa_summary — luật đã bị gỡ"

    # (a) khoá SAI TÊN phải thành LỖI CỨNG
    hong = 'const DATA = { summary:{ conclusion:"x", doNow:["a"], notDo:["b"], redFlags:["c"] } };'
    e1, w1, o1 = [], [], []
    mod.kiem_khoa_summary(hong, e1, w1, o1)
    if not e1:
        return False, "khoá lạ 'notDo' KHÔNG bị bắt — lỗi 18/08 tái phát được"

    # (b) khoá ĐÚNG phải sạch (chống chốt bắt oan)
    dung = 'const DATA = { summary:{ conclusion:"x", doNow:["a"], dontDo:["b"], redFlags:["c"] } };'
    e2, w2, o2 = [], [], []
    mod.kiem_khoa_summary(dung, e2, w2, o2)
    if e2:
        return False, f"bản ĐÚNG bị báo lỗi oan: {e2[0][:80]}"

    # (c) toàn kho thật phải sạch
    ban_hong = []
    for f in sorted((REPO / "EBM-Dashboards").glob("WebDashboard_*.html")):
        if ".bak" in f.name:
            continue
        t = f.read_text(encoding="utf-8", errors="replace")
        i = t.find("const DATA")
        if i < 0:
            continue
        e3, w3, o3 = [], [], []
        mod.kiem_khoa_summary(t[i:], e3, w3, o3)
        if e3:
            ban_hong.append(f.name[:52])
    if ban_hong:
        return False, f"{len(ban_hong)} dashboard có khoá summary bị vứt âm thầm — {ban_hong[0]}"
    return True, "khoá lạ bị chặn cứng, bản đúng không bắt oan, toàn kho sạch"


def bh62_cong_phai_tu_parse_chat_khoi_data():
    """18/08 — CỔNG in PASS trên khối DATA đã VỠ cú pháp. `field()` của cổng là parser
    DUNG SAI (đọc từng trường bằng regex) nên vẫn rút được dữ liệu từ JS hỏng. Đo thật
    cùng ngày: chèn 2 mục mới làm rơi MỘT dấu phẩy giữa ITEM-22 và ITEM-23 ⇒ trình duyệt
    render TRANG TRẮNG, mà `verify_dashboard.py` vẫn nói ✓ PASS. BH59 bắt được ở mức
    PHIÊN và bước ② của bộ năm chết to, nhưng ai chỉ chạy CỔNG rồi tin thì đã tin nhầm —
    và cổng chính là thứ doctrine bảo phải chạy trước khi phát hành.

    Chốt canh BA điều, tất cả bằng HÀNH VI:
      (a) cổng còn hàm kiem_parse_chat và nó CHẶN CỨNG khối DATA vỡ cú pháp;
      (b) cổng KHÔNG bắt oan khối DATA đúng;
      (c) parser chỉ có ĐÚNG MỘT bản cài đặt — build_dashboard_docx phải dùng CHUNG
          hàm của verify_dashboard (BH21: hai parser của cùng dữ liệu sẽ bất đồng, và
          lúc đó không ai biết bên nào đúng).
    """
    import importlib.util as _ilu
    thu_muc = REPO / "EBM-Dashboards" / "tools"
    spec = _ilu.spec_from_file_location("_vd_bh62", thu_muc / "verify_dashboard.py")
    vd = _ilu.module_from_spec(spec)
    sys.modules["_vd_bh62"] = vd
    try:
        spec.loader.exec_module(vd)
    except Exception as e:  # noqa: BLE001
        return False, f"không nạp được verify_dashboard: {e}"
    if not hasattr(vd, "kiem_parse_chat"):
        return False, "verify_dashboard KHÔNG còn kiem_parse_chat — luật parse chặt đã bị gỡ"

    dung = ('const DATA = {items:[{id:"ITEM-01"},{id:"ITEM-02"}]};\n'
            '/* \u25b2\u25b2\u25b2  HẾT KHỐI DATA  \u25b2\u25b2\u25b2 */')
    vo = dung.replace('{id:"ITEM-01"},', '{id:"ITEM-01"}')   # rơi dấu phẩy — đúng lỗi 18/08

    e1, w1, o1 = [], [], []
    vd.kiem_parse_chat(vo, e1, w1, o1)
    if not e1:
        return False, "khối DATA VỠ cú pháp KHÔNG bị chặn — lỗi trang trắng tái phát được"

    e2, w2, o2 = [], [], []
    vd.kiem_parse_chat(dung, e2, w2, o2)
    if e2:
        return False, f"khối DATA ĐÚNG bị bắt oan: {e2[0][:80]}"

    # (c) một bản cài đặt duy nhất
    spec2 = _ilu.spec_from_file_location("_bdd_bh62", thu_muc / "build_dashboard_docx.py")
    bdd = _ilu.module_from_spec(spec2)
    sys.modules["_bdd_bh62"] = bdd
    try:
        sys.path.insert(0, str(thu_muc))
        spec2.loader.exec_module(bdd)
    except Exception as e:  # noqa: BLE001
        return False, f"không nạp được build_dashboard_docx: {e}"
    finally:
        if str(thu_muc) in sys.path:
            sys.path.remove(str(thu_muc))
    ten_mod = getattr(bdd.js_object_literal_to_json, "__module__", "")
    if "verify_dashboard" not in ten_mod:
        return False, ("build_dashboard_docx KHÔNG dùng chung parser của verify_dashboard "
                       f"(đang là {ten_mod!r}) — đã có HAI bản, nguy cơ bất đồng như BH21")

    # toàn kho phải parse sạch
    hong = []
    for f in sorted((REPO / "EBM-Dashboards").glob("WebDashboard_*.html")):
        if ".bak" in f.name:
            continue
        e3, w3, o3 = [], [], []
        vd.kiem_parse_chat(f.read_text(encoding="utf-8", errors="replace"), e3, w3, o3)
        if e3:
            hong.append(f.name[:52])
    if hong:
        return False, f"{len(hong)} dashboard không parse chặt được — {hong[0]}"
    return True, "cổng tự chặn khối DATA vỡ, không bắt oan, và dùng chung MỘT parser"


def bh69_co_tat_plugin_trung_phai_duoc_khoi_phuc() -> tuple[bool, str]:
    """21/08/2026 — app Claude ghi đè `settings.json` và xoá sạch các cờ `false` của 8
    plugin medsci trùng (đã xảy ra 17/08 và 21/08, kho phồng 870 → 1319 skill).

    Hai điều dễ làm sai, chốt canh cả hai:
    (a) Phải GHI `false`, KHÔNG được xoá khoá — vắng mặt trong `enabledPlugins` nghĩa là
        BẬT. Lời khuyên «gỡ hẳn khỏi enabledPlugins» ngày 11/08 từng làm Claude Code cài
        lại cả 8 bộ (278 MB).
    (b) Plugin mà mốc chuẩn đang giữ thì tuyệt đối không được đụng tới.

    Kiểm bằng cách gọi thẳng vào mã đang sống trên một `settings.json` giả.
    """
    import json
    import tempfile

    m = _nap(REPO / "tools" / "kiem_co_tat_plugin_trung.py", "_bh69_co_tat")

    with tempfile.TemporaryDirectory() as d:
        st = Path(d) / "settings.json"
        moc = Path(d) / "moc.json"
        # mốc giữ đúng một thành viên của họ
        moc.write_text(json.dumps({"plugin": {"medsci-project@medsci-skills": {"so_skill": 58}}}),
                       encoding="utf-8")
        # app vừa ghi đè: cờ false biến mất, một bộ ghi true, một bộ vắng mặt hoàn toàn
        st.write_text(json.dumps({"enabledPlugins": {
            "medsci-project@medsci-skills": True,
            "medsci-data@medsci-skills": True,
            "khac@marketplace-khac": True,
        }}), encoding="utf-8")
        m.SETTINGS, m.MOC = st, moc

        thieu, _ = m.do()
        if "medsci-data@medsci-skills" not in thieu:
            return False, "không phát hiện plugin trùng đang bật"
        if "medsci-project@medsci-skills" in thieu:
            return False, "đụng vào plugin mà mốc đang giữ"
        if "khac@marketplace-khac" in thieu:
            return False, "đụng vào họ plugin ngoài phạm vi"

        m.sua(thieu)
        ep = json.loads(st.read_text(encoding="utf-8"))["enabledPlugins"]
        if "medsci-data@medsci-skills" not in ep:
            return False, "đã XOÁ khoá thay vì ghi false — vắng mặt nghĩa là BẬT"
        if ep["medsci-data@medsci-skills"] is not False:
            return False, "không ghi được cờ false"
        if ep["medsci-project@medsci-skills"] is not True:
            return False, "đã tắt nhầm plugin mốc đang giữ"

    return True, "ghi false đúng bộ trùng, giữ nguyên bộ trong mốc"


def bh73_viet_hoa_phai_tu_phuc_hoi_sau_cap_nhat_plugin() -> tuple[bool, str]:
    """23/08/2026 — bác sĩ hỏi «sao Việt hoá plugin lại bị lỗi». Đo ra: 87 mô tả đã
    trở lại tiếng Anh (claude-code-harness 5.9.0→5.11.0 làm mất 85, humanizer
    2.11.1→2.11.2 mất 1, medsci thêm 1 skill mới chưa dịch).

    Cơ chế: bản cập nhật plugin tạo thư mục PHIÊN BẢN MỚI với file gốc tiếng Anh; bản
    đã Việt hoá nằm lại thư mục cũ thành mồ côi. `apply_vi.py` là thứ DUY NHẤT ghi
    tiếng Việt vào file plugin — nhưng KHÔNG chỗ nào chạy lại nó. Mỗi lần cập nhật là
    một lần mất tiếng Việt, IM LẶNG, chỉ lộ ra khi bác sĩ tình cờ gõ `/`.

    Lớp phủ `vi_descriptions.json` (dựng 10/08) KHÔNG cứu được ca này: nó chỉ áp lúc
    dựng DANH-MUC/TRA-CUU, còn menu gõ `/` đọc THẲNG file plugin. Đây đúng họ lỗi
    BH41 — công cụ chạy đúng, có test, nhưng không ai gọi thì với dây chuyền hằng
    ngày nó KHÔNG TỒN TẠI.

    Chốt canh CẢ HAI vế, vì vế thứ hai mới là vế đã hỏng:
      (a) apply_vi phát hiện được mô tả bị trả về tiếng Anh và vá lại đúng;
      (b) tu_sua_chua CÓ GỌI apply_vi — chạy trên bảng VIEC_MAY đang sống.
    """
    import sys as _sys
    import tempfile

    # apply_vi.py import anh em cùng thư mục (`from extract_catalog import VN_CHARS`),
    # nên nạp rời khỏi thư mục đó sẽ ModuleNotFoundError. Thêm đường dẫn trước khi nạp.
    _vn = str(REPO / "tools" / "vietnamize")
    _da_co = _vn in _sys.path
    if not _da_co:
        _sys.path.insert(0, _vn)
    try:
        m = _nap(REPO / "tools" / "vietnamize" / "apply_vi.py", "_bh73_apply_vi")
    finally:
        if not _da_co and _vn in _sys.path:
            _sys.path.remove(_vn)

    # --- (a) hành vi: bắt được drift, vá đúng, không vá lại lần hai ----------
    with tempfile.TemporaryDirectory() as d:
        sk = Path(d) / "SKILL.md"
        sk.write_text('---\nname: thu-nghiem\n'
                      'description: Draft a plan and validate it with the team.\n'
                      '---\n\n# Thân file không được đổi\n', encoding="utf-8")
        item = {"id": "skill:x:thu-nghiem", "name": "thu-nghiem", "path": str(sk)}
        entry = {"vi": "[Lập trình] Lập KẾ HOẠCH rồi kiểm chứng cùng đội. "
                       "Dùng khi mở một hạng mục mới. Từ khoá: plan."}

        if m.process(item, entry, restore=False, dry=True) != "applied":
            return False, "không phát hiện mô tả bị bản cập nhật trả về tiếng Anh"
        if "Draft a plan" not in sk.read_text(encoding="utf-8"):
            return False, "--dry-run đã GHI vào file"

        if m.process(item, entry, restore=False, dry=False) != "applied":
            return False, "không vá được mô tả"
        t = sk.read_text(encoding="utf-8")
        if entry["vi"] not in t:
            return False, "vá xong nhưng mô tả tiếng Việt không có trong file"
        if "# Thân file không được đổi" not in t:
            return False, "đã làm hỏng thân file"
        if m.process(item, entry, restore=False, dry=True) != "already":
            return False, "vá xong vẫn báo còn lệch — sẽ vá lặp mỗi phiên"

    # --- (b) nối dây: tu_sua_chua PHẢI gọi apply_vi -------------------------
    ts = _nap(REPO / "tools" / "tu_sua_chua.py", "_bh73_tu_sua_chua")
    goi = [v for v in ts.VIEC_MAY
           if any("apply_vi" in str(x) for x in (v[1] or []) + (v[2] or []))]
    if not goi:
        return False, ("tu_sua_chua KHÔNG gọi apply_vi — công cụ có mà không ai chạy "
                       "thì mỗi lần cập nhật plugin lại mất tiếng Việt (BH41)")
    nhan, kiem, sua = goi[0]
    if not kiem or "--im-khi-on" not in kiem:
        return False, f"bước «{nhan}» thiếu --im-khi-on → sẽ ồn mỗi phiên"
    if not sua:
        return False, f"bước «{nhan}» chỉ báo mà không tự sửa"
    if "yaml" not in Path(sua[0]).name.lower() and ".ebm-venv" not in sua[0]:
        # Cho qua khi máy chưa dựng venv (lúc đó PY_YAML lùi về sys.executable);
        # apply_vi tự từ chối ghi nếu thiếu PyYAML nên không có đường hỏng im lặng.
        if getattr(ts, "_VENV", Path("/")).exists():
            return False, "lệnh sửa không dùng trình thông dịch có PyYAML"

    return True, f"apply_vi bắt+vá đúng; tu_sua_chua đã nối «{nhan}»"


def bh74_catalog_phai_do_dung_mat_dang_phuc_vu() -> tuple[bool, str]:
    """24/08/2026 — BH73 nối dây xong, nhưng chốt vẫn báo SẠCH trong khi 147 mô tả đã
    trở về tiếng Anh. Ba lỗi khác nhau, cùng một họ «đo đúng, nhưng đo nhầm chỗ»:

    (a) SAI THƯ MỤC. `extract_catalog` quét `~/.claude-science/orgs/*/skills/` rồi gán
        nhãn `/anthropic-skills:<tên>`, nhưng lệnh đó THẬT SỰ chạy bản nằm ở
        `local-agent-mode-sessions/skills-plugin/`. Đo được: `.claude-science/learn`
        tiếng Việt trong khi bản Cowork — bản bác sĩ thấy khi gõ `/` — vẫn tiếng Anh.
        Mọi công cụ báo «đã Việt hoá 100%», còn bác sĩ thì đang đọc tiếng Anh.

    (b) CATALOG LẠC HẬU. `catalog_raw.json` ghi đường dẫn TUYỆT ĐỐI kèm số phiên bản
        (…/claude-code-harness/5.11.0/…). Plugin lên 5.12.0 thì catalog vẫn trỏ 5.11.0
        — nơi tiếng Việt còn nguyên — nên chốt đọc catalog cũ báo «sạch» trong khi thư
        mục đang phục vụ 100% tiếng Anh. Vá bằng `--tu-quet` (quét lại, ~1,3 giây).

    (c) VÁ LÀM HỎNG THỨ NÓ PHẢI GIỮ. Thêm Cowork vào catalog kéo CHÍNH skill của bác sĩ
        vào tầm ghi của apply_vi. Rào «giữ-bản-việt-tự-viết» khi đó chỉ chạy cho khoá
        `name:`, nên đường khoá `id` vẫn đè — mất mô tả tự viết của 3 skill
        (clinical-evidence-rag, ebm-master, literature-review). Nguồn gốc của khoá
        không đổi được sự thật rằng mô tả đang có là do người viết.
    """
    import sys as _sys
    import tempfile

    src = (REPO / "tools" / "vietnamize" / "extract_catalog.py").read_text(encoding="utf-8")
    if "skills-plugin/*/*/skills/*/SKILL.md" not in src:
        return False, ("extract_catalog KHÔNG quét mặt Cowork (skills-plugin) — đó mới là "
                       "nơi lệnh /anthropic-skills:* chạy; chỉ quét .claude-science thì "
                       "công cụ báo Việt hoá xong trong lúc bác sĩ vẫn đọc tiếng Anh")

    ts = _nap(REPO / "tools" / "tu_sua_chua.py", "_bh74_tu_sua_chua")
    viet = [v for v in ts.VIEC_MAY
            if any("apply_vi" in str(x) for x in (v[1] or []) + (v[2] or []))]
    if not viet:
        return False, "tu_sua_chua không còn gọi apply_vi (xem BH73)"
    nhan, kiem, sua = viet[0]
    for ten, lenh in (("lệnh kiểm", kiem), ("lệnh sửa", sua)):
        if not lenh or "--tu-quet" not in lenh:
            return False, (f"{ten} của bước «{nhan}» thiếu --tu-quet ⇒ đọc catalog cũ, "
                           "sẽ báo sạch sau mỗi lần plugin đổi phiên bản")

    ap = (REPO / "tools" / "vietnamize" / "apply_vi.py").read_text(encoding="utf-8")
    dau = ap.find("giữ-bản-việt-tự-viết")
    dieu_kien = ap[max(0, dau - 400):dau]
    if "VN_CHARS.search(cur_desc)" not in dieu_kien:
        return False, "không tìm thấy rào giữ-bản-việt-tự-viết trong apply_vi"
    dong_if = dieu_kien[dieu_kien.rfind("if "):]
    if "qua_ten" in dong_if:
        return False, ("rào giữ-bản-việt-tự-viết vẫn phụ thuộc `qua_ten` ⇒ bản dịch khớp "
                       "qua khoá `id` sẽ đè mô tả bác sĩ tự viết")

    _vn = str(REPO / "tools" / "vietnamize")
    _co = _vn in _sys.path
    if not _co:
        _sys.path.insert(0, _vn)
    try:
        m2 = _nap(REPO / "tools" / "vietnamize" / "apply_vi.py", "_bh74_apply_vi")
    finally:
        if not _co and _vn in _sys.path:
            _sys.path.remove(_vn)

    with tempfile.TemporaryDirectory() as d:
        sk = Path(d) / "SKILL.md"
        tu_viet = "Mô tả do bác sĩ tự viết bằng tiếng Việt, không phải bản dịch máy."
        sk.write_text("---" + chr(10) + "name: cua-bac-si" + chr(10)
                      + 'description: "' + tu_viet + '"' + chr(10) + "---" + chr(10)
                      + chr(10) + "# than file" + chr(10), encoding="utf-8")
        item = {"id": "skill:anthropic-skills:cua-bac-si", "name": "cua-bac-si",
                "path": str(sk)}
        kq = m2.process(item, {"vi": "Ban dich trong tu dien, KHONG duoc phep de."},
                        restore=False, dry=False, qua_ten=False)
        if kq != "giữ-bản-việt-tự-viết":
            return False, f"khoá `id` vẫn đè mô tả tự viết (process trả '{kq}')"
        if tu_viet not in sk.read_text(encoding="utf-8"):
            return False, "mô tả bác sĩ tự viết đã bị ghi đè"

    return True, "catalog quét mặt phục vụ · chốt --tu-quet · rào giữ chữ bác sĩ tự viết"


def bh68_ma_bai_hoc_phai_duy_nhat() -> tuple[bool, str]:
    """21/08/2026 — hai phiên làm việc song song cùng thêm một mục và cùng lấy số kế
    tiếp, sinh ra HAI mục cùng mang mã «BH60». Bảng vẫn chạy đủ và báo cáo vẫn xanh,
    nên lỗi sổ sách này không có đường nào lộ ra: tra theo mã sẽ trúng nhầm mục, đếm
    theo mã sẽ hụt một mục. Chốt đọc chính bảng đăng ký đang sống.
    """
    from collections import Counter

    dem = Counter(ma for ma, _, _, _ in BAI_HOC)
    trung = sorted(ma for ma, n in dem.items() if n > 1)
    if trung:
        return False, "mã trùng: " + ", ".join(trung)
    return True, f"{len(BAI_HOC)} mục, mã duy nhất"


def bh75_don_bak_phai_xu_ly_ca_thu_muc() -> tuple[bool, str]:
    """25/08/2026 — `dong_bo_skill.py --don-bak` chỉ biết `.unlink()` (file), nhưng từ
    khi `dong_bo_skill_claude_codex.py` sao lưu NGUYÊN THƯ MỤC skill phân kỳ bằng
    `shutil.copytree(dst, dst.parent / f"{k}.bak-{stamp}", ...)` thay vì từng file rời,
    `rglob("*.bak-*")` trả về CẢ thư mục khớp mẫu tên. Gọi `.unlink()` lên một thư mục
    trên macOS ném `PermissionError` (không phải `IsADirectoryError` — dễ đọc nhầm
    thành lỗi quyền hệ thống) và giết cả lượt dọn giữa chừng, để lại rác `.bak-*` nằm
    cạnh bản sống trong runtime — đúng điều BH22 sinh ra để ngăn, nhưng BH22 chỉ đo
    KẾT QUẢ (còn rác hay không), không đo được đường đi (`--don-bak` có tự chạy nổi
    không). Đo thật: 17 mục rác tồn đọng từ 13/08–25/08 vì mọi lần gọi `--don-bak`
    trước đó đều chết ngay khi gặp thư mục `.bak-*` đầu tiên.

    Kiểm HÀNH VI trên đĩa tạm bằng cách gọi THẲNG `don_bak()` thật (không viết lại
    logic riêng — tránh lệch với bản đang chạy): dựng cả THƯ MỤC lẫn FILE tên
    `.bak-*`, xác nhận không crash và cả hai loại đều bị xoá sạch."""
    import tempfile

    m = _nap(REPO / "tools/dong_bo_skill.py", "dbs_bh75")
    with tempfile.TemporaryDirectory() as d:
        rt = Path(d) / "skills"
        (rt / "mot-skill" / "tools").mkdir(parents=True)
        (rt / "mot-skill" / "tools" / "x.py").write_text("pass", encoding="utf-8")
        thu_muc_bak = rt / "mot-skill.bak-20260101-000000"
        (thu_muc_bak / "tools").mkdir(parents=True)
        (thu_muc_bak / "tools" / "x.py").write_text("pass cu", encoding="utf-8")
        file_bak = rt / "mot-skill" / "tools" / "x.py.bak-20260101-000000"
        file_bak.write_text("pass cu 2", encoding="utf-8")

        try:
            n = m.don_bak(rt)
        except OSError as exc:
            return False, f"don_bak() crash trên thư mục .bak: {exc}"
        if n != 2:
            return False, f"don_bak() báo xoá {n} mục, mong đợi 2 (1 thư mục + 1 file)"
        if thu_muc_bak.exists():
            return False, "thư mục .bak vẫn còn sau khi dọn"
        if file_bak.exists():
            return False, "file .bak vẫn còn sau khi dọn"
    return True, "don_bak() xử lý đúng cả thư mục lẫn file, không crash"


def bh76_do_tuoi_phai_sinh_theo_noi_dung_khong_theo_mtime() -> tuple[bool, str]:
    """25/08/2026 — `tu_de_xuat_viec.py` từng đo độ tươi bản Word/bản-đọc BẰNG MTIME
    (docx cũ hơn html ⇒ "lỗi thời"). Một lần reskin THUẦN VỎ CSS/HTML (Sprint 9, task
    9.2 — đã xác nhận `DATA` byte-for-byte không đổi trên 66/67 dashboard) bump mtime
    của MỌI dashboard đã reskin cùng lúc ⇒ cảm biến báo "66 dashboard lỗi thời" trong
    khi THẬT SỰ chỉ 5 bản có nội dung đổi (đối chiếu DATA-hash với bản backup trước
    reskin xác nhận đúng 5/66). Nếu tin cảm biến mù chữ, bác sĩ sẽ tốn ~60 lượt gọi
    PubMed thật để xuất lại thứ không hề đổi khoa học — đúng họ lỗi BH32 (chỉ số gộp
    kết luận sai cho cả tập) nhưng ở một cảm biến khác.

    Vá bằng sidecar `<tên>.data-sha256` (ghi bởi `xuat_goi_cap_nhat.py` mỗi lần xuất,
    chứa SHA256 của khối `const DATA`) — `dem_dashboard_phai_sinh_loi_thoi()` so HASH
    thay vì MTIME khi sidecar tồn tại, chỉ lùi về mtime khi dashboard chưa từng có
    sidecar (không đổi hành vi cho dashboard cũ).

    Kiểm HÀNH VI trên đĩa tạm, GỌI THẲNG hàm thật (không viết lại logic riêng), MỖI
    CA MỘT THƯ MỤC RIÊNG (không gộp chung rồi chỉ so TỔNG — tự bắt được lúc soạn:
    gộp chung khiến một đột biến làm ① sai + ② sai vẫn cho tổng ĐÚNG NGẪU NHIÊN,
    đúng họ lỗi BH32 mà chính bài học này đang nói tới): sidecar khớp (không lỗi
    thời dù mtime docx cũ hơn) · sidecar lệch (lỗi thời) · thiếu docx (lỗi thời) ·
    mtime fallback cũ hơn (lỗi thời) · mtime fallback mới hơn (không lỗi thời)."""
    import hashlib
    import os
    import shutil as _shutil
    import tempfile

    m = _nap(REPO / "tools/tu_de_xuat_viec.py", "tdxv_bh76")
    vd_src = REPO / "EBM-Dashboards" / "tools" / "verify_dashboard.py"
    vd_mod = _nap(vd_src, "vd_bh76")

    def _html(data_noi_dung: str) -> str:
        return (f"<html><body><script>\nconst DATA = {{{data_noi_dung}}};\n"
                "// HẾT KHỐI DATA\n</script></body></html>")

    def _hash(data_noi_dung: str) -> str:
        # Băm ĐÚNG những gì extract_data_block() thật sự trả về (gồm cả phần
        # ";\n// " trước marker) — không tự dựng chuỗi tay, tránh lệch khỏi
        # logic thật của xuat_goi_cap_nhat.py::ghi_sidecar_hash_data().
        data_block = vd_mod.extract_data_block(_html(data_noi_dung))
        return hashlib.sha256(data_block.encode("utf-8")).hexdigest()

    def _mot_ca(*, sidecar_noi_dung: str | None, mtime_docx: float | None) -> int:
        """Dựng MỘT dashboard trong thư mục tạm RIÊNG, trả kết quả đếm (0 hoặc 1).
        `sidecar_noi_dung=None` ⇒ không ghi sidecar (test nhánh fallback mtime).
        `mtime_docx=None` ⇒ không tạo docx (test nhánh 'thiếu docx')."""
        with tempfile.TemporaryDirectory() as d:
            dash_dir = Path(d)
            (dash_dir / "derivatives").mkdir()
            tools_dir = dash_dir / "tools"
            tools_dir.mkdir()
            _shutil.copy2(vd_src, tools_dir / "verify_dashboard.py")
            f_db = dash_dir / "WebDashboard_EBM_ca.html"
            f_db.write_text(_html("items:[{id:'a'}]"), encoding="utf-8")
            if mtime_docx is not None:
                docx = dash_dir / "derivatives" / "ca_TaiLieuChiTiet.docx"
                docx.write_text("x", encoding="utf-8")
                if sidecar_noi_dung is not None:
                    docx.with_suffix(".data-sha256").write_text(
                        _hash(sidecar_noi_dung) + "\n", encoding="utf-8")
                os.utime(docx, (mtime_docx, mtime_docx))
            return m.dem_dashboard_phai_sinh_loi_thoi(dash_dir)

    ca = [
        ("① sidecar khớp, docx CŨ (mtime không được dùng)",
         _mot_ca(sidecar_noi_dung="items:[{id:'a'}]", mtime_docx=1.0), 0),
        ("② sidecar LỆCH", _mot_ca(sidecar_noi_dung="items:[{id:'KHAC'}]", mtime_docx=1.0), 1),
        ("③ thiếu docx", _mot_ca(sidecar_noi_dung=None, mtime_docx=None), 1),
        ("④ không sidecar, docx CŨ (fallback mtime)",
         _mot_ca(sidecar_noi_dung=None, mtime_docx=1.0), 1),
        ("⑤ không sidecar, docx MỚI (fallback mtime)",
         _mot_ca(sidecar_noi_dung=None, mtime_docx=9_999_999_999.0), 0),
    ]
    sai = [f"{ten}: được {thuc}, mong {mong}" for ten, thuc, mong in ca if thuc != mong]
    if sai:
        return False, "; ".join(sai)
    return True, "dem_dashboard_phai_sinh_loi_thoi() ưu tiên hash DATA, chỉ lùi mtime khi thiếu sidecar"


def bh77_skill_da_viet_hoa_khong_bi_thay_boi_noi_dung_la() -> tuple[bool, str]:
    """26/08/2026 — `sync/skills/peer-review/` và `sync/skills/literature-review/`
    (2 skill dựa trên bản gốc K-Dense Inc., đã được bác sĩ chỉnh khối
    `EBM-VN-GUARD` — bắt buộc tiếng Việt, disclaimer, PMID/DOI, không PII, chỉ
    nguồn miễn phí) bị GHI ĐÈ HOÀN TOÀN bằng một bộ skill khác — tiếng Anh, có
    từ khoá tiếng Hàn (리뷰, 논문 리뷰), mẫu tạp chí X-quang (RYAI/INSI/EURE/AJR/
    KJR), và `kernel.py` tự khai chạy trong hệ sinh thái "Claude Science" —
    KHÔNG liên quan gì tới phòng khám EBM tiếng Việt của bác sĩ. Khối
    EBM-VN-GUARD (tiếng Việt bắt buộc + disclaimer + PMID/DOI + không PII)
    biến mất hoàn toàn khỏi bản NGUỒN git-tracked.

    May mắn: bản Cowork RUNTIME vẫn còn nguyên khối EBM-VN-GUARD (chưa ai chạy
    `--nguon-la-chuan` để đẩy bản nguồn đã hỏng đè lên runtime), và nội dung lạ
    CHƯA TỪNG được git commit — khôi phục bằng cách chép lại từ runtime khiến
    working tree khớp TUYỆT ĐỐI với commit đã có (0 dòng lệch). Không rõ cơ chế
    gốc đã ghi đè — nghi vấn liên quan một tiến trình trên máy khác (tệp
    `catalog_raw-Dr Luân BV175.json` xuất hiện cùng thời điểm) nhưng chưa xác
    định được chắc chắn.

    Đây là biến thể MỚI của họ lỗi BH73/BH74 (plugin cập nhật ghi đè bản Việt
    hoá) — nhưng nặng hơn nhiều: BH73/74 chỉ mất MÔ TẢ, còn ca này mất TOÀN BỘ
    THÂN SKILL kể cả rào an toàn bắt buộc (ngôn ngữ, disclaimer, nguồn, PII).
    Chốt cũ (apply_vi.py --tu-quet) không bắt được vì nó chỉ so mô tả qua từ
    điển, không so sự TỒN TẠI của khối guard trong thân bài.

    Kiểm HÀNH VI: quét toàn bộ 23 skill đã biết mang khối EBM-VN-GUARD (chốt
    tại thời điểm phát hiện sự cố), xác nhận CẢ 22 vẫn còn khối này trong bản
    nguồn hiện tại. Không cái nào tái phát ⇒ ĐẠT."""
    # Danh sách 23 skill mang EBM-VN-GUARD, chốt tại thời điểm phát hiện sự cố
    # 26/08/2026 (grep -rl "EBM-VN-GUARD" sync/skills/*/SKILL.md). Danh sách mới
    # thêm sau này không tự động vào đây — đây là chốt HỒI QUY (không tái phát
    # trên skill ĐàN biết mang guard), không phải kiểm kê skill nào NÊN mang guard.
    SKILL_CO_GUARD = [
        "antifacts", "citation-management", "clinical-decision-support",
        "clinical-reports", "database-lookup", "exploratory-data-analysis",
        "experimental-design", "ebm-master", "hypothesis-generation",
        "literature-review", "paper-lookup", "peer-review", "research-lookup",
        "scholar-evaluation", "scientific-writing", "scikit-survival", "pyhealth",
        "statistical-analysis", "statsmodels", "scientific-critical-thinking",
        "treatment-plans", "statistical-power", "venue-templates",
    ]
    mat = []
    thieu_file = []
    for ten in SKILL_CO_GUARD:
        f = REPO / "sync" / "skills" / ten / "SKILL.md"
        if not f.exists():
            thieu_file.append(ten)
            continue
        noi_dung = f.read_text(encoding="utf-8", errors="replace")
        if "EBM-VN-GUARD" not in noi_dung:
            mat.append(ten)
    if thieu_file:
        return False, "SKILL.md biến mất hoàn toàn (không chỉ mất guard): " + ", ".join(thieu_file)
    if mat:
        return False, ("mất khối EBM-VN-GUARD (khả năng đã bị ghi đè bằng nội dung lạ, "
                       "xem BH77): " + ", ".join(mat))
    return True, f"{len(SKILL_CO_GUARD)}/{len(SKILL_CO_GUARD)} skill còn nguyên khối EBM-VN-GUARD"

def bh78_so_viec_treo_fail_closed_va_khong_tu_dong() -> tuple[bool, str]:
    """22/08/2026 — `tools/so_viec_chua_dong.py` ra đời để canh việc còn treo sau khi
    bệnh nhân ra về (6,8-62% kết quả xét nghiệm ngoại trú không được theo dõi tiếp —
    Callen 2012, PMID 22183961). Ba hành vi PHẢI giữ, vì mất bất kỳ cái nào thì sổ
    biến thành lời bảo đảm rỗng:

    (a) Bản ghi THIẾU HẠN phải rơi vào nhóm PHẢI XEM, không phải nhóm "ổn". Dữ liệu
        hỏng rơi về phía im lặng là đúng họ lỗi BH01/BH27/BH61 — công cụ vẫn chạy, vẫn
        in kết quả hợp lệ, nhưng thứ cần thấy thì không bao giờ hiện.
    (b) Công cụ KHÔNG được tự đóng việc. Đóng một việc treo là hành vi lâm sàng.
    (c) Sổ KHÔNG được mang trường `decision`/`gradeLevel` (BH10).

    Kiểm bằng cách gọi thẳng vào mã đang sống.
    """
    import datetime as _dt
    import io
    import json
    import tempfile
    from contextlib import redirect_stdout

    m = _nap(REPO / "tools" / "so_viec_chua_dong.py", "_bh70_so_viec")
    hom_nay = _dt.date(2026, 8, 22)

    # (a) thiếu hạn → PHẢI XEM
    _con_han, qua_han = m.phan_loai(
        [{"id": "V001", "trang_thai": "mo", "mo_ta": "x", "loai": "khac",
          "ma_noi_bo": "", "han": None}], hom_nay)
    if not any(t is None for _r, t in qua_han):
        return False, "bản ghi thiếu hạn KHÔNG rơi vào nhóm phải xem (fail-open)"

    with tempfile.TemporaryDirectory() as d:
        so = Path(d) / "v.jsonl"
        args = ["--so", str(so), "--hom-nay", hom_nay.isoformat()]

        # việc treo không hạn phải bị TỪ CHỐI ngay lúc mở
        with redirect_stdout(io.StringIO()):
            ma = m.main(args + ["--them", "--loai", "tai-kham", "--mo-ta", "hẹn 3 tháng"])
        if ma != 2:
            return False, "mở được việc treo KHÔNG có hạn"

        with redirect_stdout(io.StringIO()):
            m.main(args + ["--them", "--loai", "xet-nghiem",
                           "--mo-ta", "creatinin, chờ kết quả", "--han", "2026-07-01"])
            ma_bc = m.main(args)          # báo cáo
            m.main(args + ["--tuan"])     # bảng tuần

        if ma_bc != 1:
            return False, "việc quá hạn không làm mã thoát = 1"

        # (b) không tự đóng
        ds = [json.loads(x) for x in so.read_text(encoding="utf-8").splitlines() if x.strip()]
        if any(r["trang_thai"] != "mo" for r in ds):
            return False, "công cụ TỰ ĐÓNG việc — vượt thẩm quyền lâm sàng"

        # (c) không ghi decision/gradeLevel
        raw = so.read_text(encoding="utf-8")
        for cam in ("decision", "gradeLevel", "gradeBy", "normativeBasis"):
            if cam in raw:
                return False, f"sổ mang trường {cam} (BH10)"

        # PII: mẫu độ chính xác cao phải bị chặn, mô tả lâm sàng thường KHÔNG bị chặn oan
        if not m.soi_pii("gọi lại 0912345678"):
            return False, "bộ chặn PII bỏ lọt số điện thoại"
        if m.soi_pii("eGFR 48 mL/phút/1,73m2, nhắc lại creatinin"):
            return False, "bộ chặn PII chặn oan mô tả lâm sàng bình thường (BH08)"

    return True, "fail-closed khi thiếu hạn · không tự đóng · không ghi decision · PII đúng mức"


def bh79_la_co_safety_net_khong_duoc_noi_ho() -> tuple[bool, str]:
    """22/08/2026 — `CLINICAL_RUNTIME_FLAGS.json` khai
    `enforce_safety_net_templates: true` từ lâu, nhưng grep toàn repo trả 0 file tham
    chiếu tới `safety_net_templates.json`, và nội dung file đó là ba mẫu tiếng Anh chung
    chung không nguồn. Một lá cờ TUYÊN BỐ có thi hành mà không có gì thi hành — cùng họ
    với BH01 (`return` sớm che 73 mục), BH27 (fail-open cổng A12) và BH61 (khoá lạ trong
    `DATA.summary`), nhưng rơi vào TẦNG AN TOÀN CHO BỆNH NHÂN.

    Chốt canh hai hành vi của `tools/kiem_safety_net.py`:
    (a) R9 — cờ bật mà 0 hội chứng có nguồn ⇒ LỖI CỨNG.
    (b) R3 — hội chứng THIẾU HẲN khối `dan_benh_nhan_quay_lai` phải bị bắt. Bản đầu của
        chốt viết `.get(khoa, {})`, mà `{}` LÀ dict nên `isinstance` luôn đúng ⇒ khối
        thiếu hẳn vẫn lọt. Mặc định phải là `None`.
    """
    import datetime as _dt

    m = _nap(REPO / "tools" / "kiem_safety_net.py", "_bh71_safety_net")
    hom_nay = _dt.date(2026, 8, 22)
    co_bat = {"enforce_safety_net_templates": True}

    def hc_co_nguon():
        return {
            "ten": "Đau đầu", "trang_thai": "co-nguon",
            "co_do_cho_bac_si": {
                "nguon": {"pmid": "30587518"},
                "gioi_han_nguyen_van_cua_nguon": "chưa có công cụ đã kiểm định",
                "tieu_chi": [{"mo_ta": "Khởi phát sau 65 tuổi", "do_duoc": True}],
            },
            "dan_benh_nhan_quay_lai": {"trang_thai": "chua-dien",
                                       "noi_dung": m.PLACEHOLDER},
            "ngay_ra_soat": "2026-08-22",
        }

    def hc_chua_dien():
        return {
            "ten": "Đau ngực", "trang_thai": "chua-dien",
            "co_do_cho_bac_si": {"trang_thai": "chua-dien", "noi_dung": m.PLACEHOLDER},
            "dan_benh_nhan_quay_lai": {"trang_thai": "chua-dien",
                                       "noi_dung": m.PLACEHOLDER},
            "ngay_ra_soat": "2026-08-22",
        }

    # (a) cờ bật + 0 hội chứng có nguồn ⇒ R9
    loi, _, _ = m.kiem({"phien_ban": "2", "hoi_chung": {"dau-nguc": hc_chua_dien()}},
                       co_bat, hom_nay)
    if not any(x.startswith("R9") for x in loi):
        return False, "cờ bật mà 0 hội chứng có nguồn KHÔNG bị bắt (lá cờ nói hộ)"

    # cờ tắt ⇒ R9 không áp
    loi, _, _ = m.kiem({"phien_ban": "2", "hoi_chung": {"dau-nguc": hc_chua_dien()}},
                       {"enforce_safety_net_templates": False}, hom_nay)
    if any(x.startswith("R9") for x in loi):
        return False, "R9 nổ cả khi cờ đang tắt"

    # (b) thiếu hẳn khối lời dặn ⇒ R3
    hc = hc_co_nguon()
    del hc["dan_benh_nhan_quay_lai"]
    loi, _, _ = m.kiem({"phien_ban": "2", "hoi_chung": {"dau-dau": hc}}, co_bat, hom_nay)
    if not any(x.startswith("R3") for x in loi):
        return False, "hội chứng thiếu hẳn khối lời dặn vẫn lọt R3 (fail-open .get(k, {}))"

    # nguồn văn xuôi phải bị từ chối; tiêu chí không đo được phải bị từ chối
    hc = hc_co_nguon()
    hc["co_do_cho_bac_si"]["nguon"] = {"ten": "theo kinh nghiệm lâm sàng"}
    loi, _, _ = m.kiem({"phien_ban": "2", "hoi_chung": {"dau-dau": hc}}, co_bat, hom_nay)
    if not any(x.startswith("R4") for x in loi):
        return False, "nguồn dạng văn xuôi vẫn được chấp nhận"

    hc = hc_co_nguon()
    hc["co_do_cho_bac_si"]["tieu_chi"] = [{"mo_ta": "nếu nặng hơn", "do_duoc": False}]
    loi, _, _ = m.kiem({"phien_ban": "2", "hoi_chung": {"dau-dau": hc}}, co_bat, hom_nay)
    if not any(x.startswith("R5") for x in loi):
        return False, "'nếu nặng hơn' được nhận là tiêu chí"

    # file THẬT trong repo phải qua được chốt (không lỗi cứng)
    that = _nap(REPO / "tools" / "kiem_safety_net.py", "_bh71_that")
    import json as _json
    mau_that = _json.loads((REPO / "clinical_runtime" / "safety_net_templates.json")
                           .read_text(encoding="utf-8"))
    co_that = _json.loads((REPO / "clinical_runtime" / "CLINICAL_RUNTIME_FLAGS.json")
                          .read_text(encoding="utf-8"))
    loi, _, dp = that.kiem(mau_that, co_that, hom_nay)
    if loi:
        return False, f"file thật đang có LỖI CỨNG: {loi[0]}"
    if dp["co_nguon"] < 1:
        return False, "file thật không còn hội chứng nào có nguồn — R9 lẽ ra phải nổ"

    return True, (f"R9 canh lá cờ · R3 bắt khối thiếu · R4/R5 chặn nguồn-văn-xuôi và "
                  f"tiêu-chí-không-đo-được · file thật {dp['co_nguon']}/{dp['tong']} có nguồn")



def bh80_moi_cong_cu_bien_dich_duoc_tren_san_khai_bao() -> tuple[bool, str]:
    """22/08/2026 — `python -m compileall tools ops` trên Python 3.11 báo **5 file
    KHÔNG biên dịch được**: `audit_ebm_system.py` · `fix_launchd_scheduled_jobs.py` ·
    `kiem_do_tuoi_chung_cu.py` · `kiem_phan_hang.py` · `verify_mcp_live_sync.py`
    (6 chỗ). Nguyên nhân: cú pháp PEP 701 — lồng nháy KÉP bên trong f-string nháy kép
    (`f"gui/{getattr(os, "getuid", ...)}"`) và dấu gạch chéo ngược trong phần biểu
    thức của f-string — **chỉ hợp lệ từ Python 3.12**, trong khi `CLAUDE.md` khai sàn
    **3.11+**.

    Vì sao nằm im lâu: CI ghim đúng `python-version: "3.12"`, và hai máy của bác sĩ
    chạy 3.12.10 / 3.14.6 — nên không đâu chạm tới sàn đã khai. Hại thật: trên một
    môi trường 3.11 (container phiên web, máy mới, đồng nghiệp cài bản khác),
    `kiem_do_tuoi_chung_cu.py` — **một trong 7 chốt tự chạy mỗi phiên** — chết
    SyntaxError, mà hook `SessionStart` kết thúc bằng `; true` nên **nuốt lỗi không
    một dòng báo**. Đúng lại họ lỗi mà CHÍNH file đó đã dính hồi 12/08 trên Windows
    (`os.getuid` không tồn tại + chỉ bắt OSError ⇒ chết im lặng).

    ⚠️ GIỚI HẠN CÓ CHỦ Ý, đừng đọc quá: chốt này biên dịch bằng **trình thông dịch
    đang chạy**. Trên máy 3.12+ nó KHÔNG thấy được cú pháp 3.12-only. Guard thật cho
    sàn khai báo là **lane `python-version: "3.11"` trong `.github/workflows/
    kiem-tinh-da-nen.yml`**, thêm cùng ngày. Chốt này bắt mọi lỗi cú pháp khác và bắt
    đúng lớp trên khi phiên đang chạy ở sàn.
    """
    import sys

    hong = []
    for thu_muc in ("tools", "ops"):
        goc = REPO / thu_muc
        if not goc.is_dir():
            continue
        for f in sorted(goc.rglob("*.py")):
            if "__pycache__" in f.parts:
                continue
            try:
                compile(f.read_text(encoding="utf-8"), str(f), "exec")
            except SyntaxError as e:
                hong.append(f"{f.relative_to(REPO)}:{e.lineno} {e.msg}")
            except (OSError, UnicodeDecodeError) as e:
                hong.append(f"{f.relative_to(REPO)} đọc lỗi: {e}")

    if hong:
        return False, f"{len(hong)} file không biên dịch được: " + " · ".join(hong[:3])

    v = f"{sys.version_info.major}.{sys.version_info.minor}"
    o_san = v == "3.11"
    return True, (f"mọi tools/ + ops/ biên dịch được trên Python {v}"
                  + (" (ĐÚNG sàn khai báo)" if o_san
                     else " — lưu ý: không phải sàn 3.11, lane CI 3.11 mới là guard thật"))


# ── Bản sao git TRẦN (phiên cloud/CI): tách «không kiểm được» khỏi «tái phát» ──
# 28/08/2026 — chạy trọn bộ chốt trên một bản clone git KHÔNG có cây OneDrive cho
# 37 mục đỏ, trong đó CHỈ MỘT (BH44) là lỗi thật nằm trong repo; 36 mục còn lại đỏ
# vì nguyên liệu (EBM-Dashboards/ · medical-ebm-automation/ · EBM_MASTER/ · cấu hình
# máy trong ~/.claude) nằm NGOÀI git nên bản clone không bao giờ có. Bức tường đỏ
# giả đó vi phạm đúng BH08 («không biết» ≠ «có vấn đề») và suýt che mất lỗi thật
# duy nhất. Quy ước từ 28/08 (cùng họ «bỏ qua CÓ KHAI BÁO» của BH51/BH52): trên bản
# sao TRẦN, mục thiếu nguyên liệu in ⚪ «ngoài phạm vi» — vẫn HIỆN đầy đủ, không đếm
# vào tổng đỏ; mục trong-repo đỏ vẫn đỏ. Trên máy thật (còn ≥1 gốc dữ liệu) hành vi
# cũ giữ NGUYÊN — fail-closed, một file thiếu là ✗ như trước.
# Vòng 4 (28/08): định nghĩa «bản sao trần» dời về tools/ban_sao_tran.py — MỘT nơi
# duy nhất, vì trong chính PR này năm bản sao của phép thử đã phân kỳ thành hai ngữ
# nghĩa (1-gốc vs 3-gốc) và tạo fail-open ở ba verifier của hook.

# Khai báo TƯỜNG MINH (không suy từ thông điệp lỗi): các mã mà ĐỐI TƯỢNG được kiểm
# nằm ngoài phần git track — đo từng mã ngày 28/08 trên bản clone trần.
_CAN_NGUYEN_LIEU_NGOAI_REPO = frozenset({
    "BH01", "BH02", "BH03", "BH04", "BH07", "BH08", "BH13", "BH16", "BH18",
    "BH21", "BH25", "BH26", "BH27", "BH30", "BH31", "BH34", "BH35", "BH36",
    "BH37", "BH38", "BH39", "BH43", "BH47", "BH48", "BH49", "BH50", "BH53",
    "BH56", "BH58", "BH59", "BH60", "BH61", "BH62", "BH67", "BH72", "BH76",
})


def ban_sao_git_tran() -> bool:
    """Uỷ quyền cho định nghĩa DUY NHẤT ở tools/ban_sao_tran.py (đòi cả BA gốc vắng)."""
    return _nap(REPO / "tools" / "ban_sao_tran.py", "bst_chot").ban_sao_git_tran(REPO)


# Vòng 4 (bình duyệt đối kháng): một chốt trong danh sách ⚪ mà CHẾT vì lỗi mã
# trong-repo (TypeError, AttributeError…) từng bị ⚪ hoá luôn trên bản trần — tức
# một hồi quy trong-git có thể ship từ phiên cloud với dòng «🟢 không tái phát».
# Hai kiểu vắng-nguyên-liệu hợp lệ duy nhất là thiếu FILE/MODULE; mọi exception
# khác trong «chốt lỗi:» là crash thật và phải ✗ kể cả trên bản trần.
_LOI_THIEU_NGUYEN_LIEU = ("FileNotFoundError", "ModuleNotFoundError", "NotADirectoryError")


def phan_loai(ma: str, ok: bool, tran: bool, ct: str = "") -> str:
    """'dat' | 'tai_phat' | 'ngoai_pham_vi' — chỉ bản sao trần mới có ⚪."""
    if ok:
        return "dat"
    if tran and ma in _CAN_NGUYEN_LIEU_NGOAI_REPO:
        if ct.startswith("chốt lỗi:") and not any(t in ct for t in _LOI_THIEU_NGUYEN_LIEU):
            return "tai_phat"  # crash thật trong mã — không được ⚪ hoá
        return "ngoai_pham_vi"
    return "tai_phat"


def bh82_ban_sao_tran_khong_duoc_do_gia():
    """28/08 — bộ chốt chạy trên bản sao git TRẦN (phiên cloud) in 37 mục đỏ, trong đó
    chỉ MỘT (BH44 — skill `nghien-cuu-y-khoa-chuan-quoc-te` chạy runtime mà không có
    nguồn trong sync/skills/) là lỗi thật trong repo. 36 mục còn lại đỏ chỉ vì nguyên
    liệu nằm ngoài git — đúng «bức tường đỏ giả» mà BH08 cảnh báo: nó suýt che mất lỗi
    thật duy nhất, và nếu thành nếp thì người đọc học cách bỏ qua cả cảnh báo thật.

    Chốt kiểm HÀNH VI phân loại (gọi thẳng `phan_loai`, không đếm chữ):
      • bản trần + mục cần nguyên liệu ngoài repo + fail ⇒ «ngoai_pham_vi» (⚪ có khai báo)
      • bản trần + mục trong-repo (BH44) + fail ⇒ vẫn «tai_phat» — lỗi thật không được ⚪ hoá
      • máy đủ dữ liệu (tran=False) ⇒ mọi fail đều «tai_phat» — fail-closed cũ giữ nguyên
    """
    if phan_loai("BH01", False, True) != "ngoai_pham_vi":
        return False, "mục thiếu nguyên liệu trên bản trần không ra ⚪ — tường đỏ giả quay lại"
    if phan_loai("BH44", False, True) != "tai_phat":
        return False, "lỗi trong-repo bị ⚪ hoá trên bản trần — chốt mất răng"
    if phan_loai("BH01", False, False) != "tai_phat":
        return False, "máy đủ dữ liệu mà vẫn ⚪ — fail-closed bị tháo"
    if phan_loai("BH01", True, True) != "dat":
        return False, "mục đạt bị phân loại sai"
    if "BH44" in _CAN_NGUYEN_LIEU_NGOAI_REPO or "BH82" in _CAN_NGUYEN_LIEU_NGOAI_REPO:
        return False, "mã trong-repo bị khai nhầm là ngoài-repo — đường ⚪ hoá lỗi thật đang mở"
    # Vòng 4 (bình duyệt đối kháng): CRASH trong mã trong-repo không được ⚪ hoá
    # trên bản trần — thiếu nguyên liệu chỉ hiện dạng FileNotFound/ModuleNotFound.
    if phan_loai("BH01", False, True, "chốt lỗi: TypeError: tach_ten() thiếu tham số") != "tai_phat":
        return False, "crash trong-repo (TypeError) bị ⚪ hoá trên bản trần — hồi quy ship được từ cloud"
    if phan_loai("BH01", False, True, "chốt lỗi: FileNotFoundError: thiếu file") != "ngoai_pham_vi":
        return False, "thiếu-file trên bản trần không còn ra ⚪ — tường đỏ giả quay lại"
    return True, "bản trần: ⚪ đúng chỗ có khai báo, ✗ giữ nguyên cho lỗi trong-repo và crash"


def bh83_hook_chay_duoc_tren_ban_tran_khong_mat_rang():
    """28/08 — vòng 3 cùng ngày: hook pre-commit KHÔNG THỂ xanh trên bản sao trần vì
    hai verifier trong hook (alignment · plugin orchestration) và chốt đếm-cổng-cứng
    FAIL do thiếu repo y khoa ⇒ phiên cloud buộc commit KHÔNG QUA CỔNG nào — tệ hơn
    một cổng biết nói «phần này ngoài phạm vi». Hai commit đầu của phiên 28/08 đã đi
    qua đúng lỗ hổng đó.

    Đã sửa: ba công cụ nhận diện bản trần (repo y khoa vắng mặt HOÀN TOÀN) và tách
    phần thiếu-nguyên-liệu thành ⚪ NGOAI-PHAM-VI có khai báo; máy có repo (kể cả thư
    mục RỖNG — tức repo có mà file mất) vẫn FAIL như cũ.

    Chốt kiểm HÀNH VI phân loại (gọi thẳng hàm, chạy được trên MỌI máy):
      • đường ⚪ tồn tại: check_medical_docs(tran=True) → NGOAI-PHAM-VI
      • máy thật không bao giờ ⚪: check_medical_docs(tran=False) ≠ NGOAI-PHAM-VI
      • bộ phân loại lỗi plugin: lỗi trỏ vào repo y khoa/binding → ngoài phạm vi;
        lỗi trong-repo (registry hỏng…) TUYỆT ĐỐI không được nuốt
      • trên bản trần, alignment tổng thể phải PASS (thuộc tính mở khoá hook)
    """
    va = _nap(REPO / "tools" / "verify_claude_code_repo_alignment.py", "va_bh83")
    vp = _nap(REPO / "tools" / "verify_plugin_orchestration.py", "vp_bh83")
    if va.check_medical_docs(tran=True).get("status") != "NGOAI-PHAM-VI":
        return False, "đường ⚪ biến mất — bản trần lại đỏ giả, hook lại chết"
    if va.check_medical_docs(tran=False).get("status") == "NGOAI-PHAM-VI":
        return False, "máy thật bị ⚪ hoá — fail-closed của alignment bị tháo"
    if not vp.loi_ngoai_pham_vi_tran("thieu file medical-ebm-automation/CLAUDE.md"):
        return False, "lỗi thiếu-repo-y-khoa không được nhận là ngoài phạm vi"
    if not vp.loi_ngoai_pham_vi_tran("thieu production tool binding: g10-assemble"):
        return False, "binding trỏ sang repo y khoa không được nhận là ngoài phạm vi"
    if vp.loi_ngoai_pham_vi_tran("registry schema hong: thieu owner_unit"):
        return False, "lỗi TRONG-repo bị nuốt thành ngoài phạm vi — chốt mất răng"
    if va.ban_sao_tran():
        tong = va.run_verification()["overall_status"]
        if tong != "PASS":
            return False, f"bản trần mà alignment tổng thể {tong} — hook vẫn bị chặn oan"
    # Vòng 4: khoá NGỮ NGHĨA 3-GỐC của định nghĩa dùng chung bằng thư mục tạm —
    # chính PR này từng có 5 bản sao phân kỳ thành phép thử 1-gốc, tạo fail-open
    # khi máy thật chỉ thiếu riêng repo y khoa (bình duyệt đối kháng bắt được).
    import tempfile
    bst = _nap(REPO / "tools" / "ban_sao_tran.py", "bst_bh83")
    with tempfile.TemporaryDirectory() as td:
        goc = Path(td)
        if not bst.ban_sao_git_tran(goc):
            return False, "thư mục vắng cả 3 gốc mà không được nhận là bản trần"
        (goc / "EBM_MASTER").mkdir()
        if bst.ban_sao_git_tran(goc):
            return False, ("còn MỘT gốc dữ liệu (EBM_MASTER) mà vẫn bị coi là bản trần — "
                           "ngữ nghĩa 1-gốc quay lại, hook fail-open trên máy thật hỏng dở")
    return True, "hook sống được trên bản trần; máy thật giữ nguyên fail-closed; ngữ nghĩa 3-gốc khoá"


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
    ("BH50", "15/08", "Ping không được đội lốt lần chạy thật", bh50_ping_khong_duoc_doi_lot_chay_that),
    ("BH51", "15/08", "Ledger synthetic đúng phạm vi + gọi đúng chữ ký hàm", bh51_ledger_synthetic_dung_pham_vi),
    ("BH52", "15/08", "G0 kiểm rút bài ngay tại cửa nhận (R1C)", bh52_g0_kiem_rut_bai_tai_cua),
    ("BH53", "15/08", "elink chỉ nhận pubmed_pmc — cấm vơ bài đi-trích-dẫn", bh53_elink_chi_nhan_pubmed_pmc),
    ("BH54", "15/08", "Còi đỏ rút bài chỉ cho «rút bỏ hẳn đang trích»", bh54_ma_thoat_rut_bai_ba_muc),
    ("BH55", "15/08", "Không tool nào viết-cho-một-máy (đa nền tảng)", bh55_khong_duong_dan_cung_mot_may),
    ("BH56", "16/08", "Công cụ mới phải có dây gọi + chỉ mục RAG tươi", bh56_cong_cu_moi_phai_co_day),
    ("BH57", "16/08", "Kỳ lịch lỡ phải nhìn thấy được (đăng ký ≠ nổ)", bh57_ky_lich_lo_phai_nhin_thay),
    ("BH58", "16/08", "Quyết định đã duyệt không bị lật ngược im lặng", bh58_quyet_dinh_da_duyet_khong_lat_nguoc),
    ("BH59", "16/08", "Khối DATA phải parse được như JS (chống trang trắng)", bh59_khoi_data_phai_parse_duoc_nhu_js),
    ("BH60", "19/08", "Gói tuần phải ĐỌC TOÀN VĂN OA, không thẩm định mù từ tóm tắt", bh60_goi_tuan_phai_doc_toan_van),
    ("BH61", "18/08", "Khoá summary sai tên phải bị bắt (chống vứt nội dung an toàn)", bh61_khoa_summary_sai_ten_phai_bi_bat),
    ("BH62", "18/08", "Cổng tự parse chặt khối DATA (chống trang trắng lọt cổng)", bh62_cong_phai_tu_parse_chat_khoi_data),
    ("BH63", "20/08", "Benchmark mù — máy ẩn danh, KHÔNG tự chấm chất lượng", bh63_benchmark_mu_khong_de_may_tu_cham),
    ("BH64", "20/08", "Bài tổng thuật phải nằm trong vòng sống (sổ + hòm thư + độ tươi)", bh64_bai_tong_thuat_phai_o_trong_vong_song),
    ("BH65", "20/08", "Định danh guideline phải khai máy-khớp hay người-chốt", bh65_dinh_danh_guideline_phai_khai_ai_xac_nhan),
    ("BH66", "20/08", "Cổng trích dẫn KHÔNG bảo đảm đúng lâm sàng — giữ bảng 8 lớp lỗi nội dung", bh66_cong_trich_dan_khong_bao_dam_dung_lam_sang),
    ("BH67", "18/08", "array_field không gãy ở ngoặc vuông trong truy vấn", bh60_array_field_khong_gay_o_ngoac_vuong),
    ("BH68", "21/08", "Mã bài học phải DUY NHẤT (hai phiên thêm song song đụng số)", bh68_ma_bai_hoc_phai_duy_nhat),
    ("BH69", "21/08", "Cờ TẮT plugin trùng bị app xoá phải được ghi lại (không xoá khoá)", bh69_co_tat_plugin_trung_phai_duoc_khoi_phuc),
    # Hai mục dưới ra đời song song ở phiên đồng bộ đa nền và ban đầu mang số 67/68
    # — trùng đúng ba mục trên. Chính BH68 vừa thêm ở master là chốt bắt việc này;
    # đánh số lại thành 70/71 thay vì giành số, đúng thứ nó dạy.
    ("BH70", "21/08", "Bộ đồng bộ không được trỏ vào công cụ/cờ không tồn tại; Windows không bị chặn", bh70_bo_dong_bo_khong_tro_vao_thu_khong_co),
    ("BH71", "21/08", "Lệnh gộp phủ đủ làn và DỪNG khi chốt an toàn đỏ", bh71_lenh_gop_phu_du_lan_va_dung_khi_nguy_hiem),
    ("BH72", "22/08", "Chuỗi cổng NGHIÊN CỨU cũng phải có canary đầu-cuối, như chuỗi chứng cứ", bh70_canary_cong_nghien_cuu_phai_chay_va_phai_bat_duoc),
    ("BH73", "23/08", "Việt hoá phải tự phục hồi sau khi plugin cập nhật — và phải CÓ NGƯỜI GỌI", bh73_viet_hoa_phai_tu_phuc_hoi_sau_cap_nhat_plugin),
    ("BH74", "24/08", "Catalog phải đo ĐÚNG mặt đang phục vụ, quét lại trước khi kiểm, và không đè chữ bác sĩ tự viết", bh74_catalog_phai_do_dung_mat_dang_phuc_vu),
    ("BH75", "25/08", "Dọn .bak phải xử lý cả thư mục, không chỉ file", bh75_don_bak_phai_xu_ly_ca_thu_muc),
    ("BH76", "25/08", "Độ tươi phái sinh phải đo theo NỘI DUNG, không theo mtime", bh76_do_tuoi_phai_sinh_theo_noi_dung_khong_theo_mtime),
    ("BH77", "26/08", "Skill đã Việt hoá không được mất khối EBM-VN-GUARD", bh77_skill_da_viet_hoa_khong_bi_thay_boi_noi_dung_la),
    # Ba mục dưới ra đời trên nhánh outpatient 22/08 với số 70/71/72 — trùng với ba
    # mục master đặt song song cùng tuần. Đánh số lại thành 78/79/80 theo đúng tiền lệ
    # ghi ngay phía trên (BH68 canh mã duy nhất).
    ("BH78", "22/08", "Sổ việc treo: fail-closed khi thiếu hạn, không tự đóng việc", bh78_so_viec_treo_fail_closed_va_khong_tu_dong),
    ("BH79", "22/08", "Lá cờ safety-netting không được nói hộ (R9) + R3 bắt khối thiếu", bh79_la_co_safety_net_khong_duoc_noi_ho),
    ("BH80", "22/08", "Mọi công cụ biên dịch được trên SÀN KHAI BÁO (3.11), không chỉ 3.12", bh80_moi_cong_cu_bien_dich_duoc_tren_san_khai_bao),
    # Mục dưới ra đời song song ở phiên đồng bộ đa nền và ban đầu mang số 72 — trùng
    # canary cổng nghiên cứu của master. Đánh số lại thành 81 theo đúng tiền lệ BH68.
    ("BH81", "22/08", "Khoá ngân sách skill bị app xoá phải được khôi phục («gọi skill không được»)", bh81_khoa_cau_hinh_nguoi_dung_duoc_khoi_phuc),
    ("BH82", "28/08", "Bản sao git trần: «không kiểm được» là ⚪ có khai báo, không phải ✗ giả", bh82_ban_sao_tran_khong_duoc_do_gia),
    ("BH83", "28/08", "Hook pre-commit sống được trên bản trần mà không mất răng trên máy thật", bh83_hook_chay_duoc_tren_ban_tran_khong_mat_rang),

]


def main() -> int:
    ap = argparse.ArgumentParser(description="Chốt hồi quy trên các lỗi đã từng xảy ra")
    ap.add_argument("--im-khi-on", action="store_true", help="chỉ nói khi có mục tái phát")
    a = ap.parse_args()

    tran = ban_sao_git_tran()
    ket: list[tuple[str, str, str, str, str]] = []
    for ma, ngay, ten, ham in BAI_HOC:
        try:
            ok, ct = ham()
        except KeyboardInterrupt:
            raise
        # Vòng 4: bắt BaseException, không chỉ Exception — một chốt lỡ ném SystemExit
        # (đã suýt xảy ra với nap_vd bản SystemExit) sẽ giết CẢ lượt chạy giữa chừng,
        # mọi chốt sau không được kiểm, và hook `; true` nuốt sạch không một dòng báo.
        except BaseException as e:  # noqa: BLE001 — chốt hỏng phải LỘ RA, không im lặng xanh
            ok, ct = False, f"chốt lỗi: {type(e).__name__}: {e}"
        ket.append((ma, ngay, ten, phan_loai(ma, ok, tran, ct), ct))

    do = [k for k in ket if k[3] == "tai_phat"]
    ngoai = [k for k in ket if k[3] == "ngoai_pham_vi"]
    if a.im_khi_on and not do:
        return 0

    if a.im_khi_on:
        print("")
    dat = len(ket) - len(do) - len(ngoai)
    print(f"CHỐT HỒI QUY BÀI HỌC — {dat}/{len(ket)} còn được canh"
          + (f" · ⚪ {len(ngoai)} ngoài phạm vi bản sao trần" if ngoai else ""))
    ICON = {"dat": "✓", "tai_phat": "✗", "ngoai_pham_vi": "⚪"}
    for ma, ngay, ten, loai, ct in ket:
        print(f"  {ICON[loai]} {ma} [{ngay}] {ten}")
        if loai == "tai_phat":
            print(f"      → {ct}")
    if ngoai:
        print(f"\n⚪ {len(ngoai)} mục KHÔNG kiểm được trên bản sao git trần — nguyên liệu"
              " (EBM-Dashboards/ · medical-ebm-automation/ · EBM_MASTER/ · cấu hình máy)"
              " nằm ngoài git.")
        print("   ⚪ KHÔNG có nghĩa là ĐẠT — chạy trên máy có đủ cây dữ liệu để canh đủ.")
    if do:
        print(f"\n🔴 {len(do)} BÀI HỌC TÁI PHÁT — lỗi đã sửa nay quay lại.")
        print("   Đọc docstring của hàm tương ứng trong tools/chot_hoi_quy_bai_hoc.py")
        print("   để biết lỗi đó từng gây hại gì.")
        return 1
    print("\n🟢 Không bài học nào tái phát"
          + (" trong phạm vi kiểm được trên bản sao trần." if ngoai else "."))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
