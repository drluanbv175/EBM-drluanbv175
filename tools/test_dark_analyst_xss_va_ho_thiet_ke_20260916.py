#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chốt hồi quy (16/09/2026): template Dark Analyst — khôi phục XSS + họ thiết kế/thang hiệu số.

VÌ SAO CÓ. Rà 3 bản Dark Analyst đang tồn tại (chuẩn bị cổng designFamily/effectScale từ
`test_ew_template_ho_thiet_ke_thang_hieu_so.py` sang mẫu này) phát hiện 2/3 bản GIT-TRACKED
(dùng thật cho hai skill `dark-analyst` và `cap-nhat-chung-cu-y-khoa`) đã MẤT HOÀN TOÀN lớp
chống XSS (`escHtml`/`escUrl`/`escJs`) — tiêu đề/nguồn/hiệu số trích từ PubMed/guideline được
nội suy thẳng vào `innerHTML` không escape, liên kết PMID/DOI mất cả `encodeURIComponent` lẫn
`rel="noopener"`. Đo bằng `git log --follow`: commit GỐC của 2 file này là một lần "rebuild
history root after OneDrive/Mac-worktree object loss" — lỗi có từ TRƯỚC khi file vào git, do
một lần khôi phục sau sự cố OneDrive làm hỏng `.git`, không phải một sửa đổi có chủ ý. Bản
`dashboard_mockups`/`EBM_MASTER` (ngoài git, mtime cũ hơn) vẫn giữ nguyên lớp chống XSS —
dùng làm NỀN để hợp nhất, cộng thêm Lớp 4 `qualityView` (DATA.standards, thêm 10/09/2026 chỉ ở
bản cap-nhat-chung-cu-y-khoa) + GROUP_META (thai-ky, tre-em) + hai cơ chế của
`test_ew_template_ho_thiet_ke_thang_hieu_so.py` (designFamily theo tiền tố, effectScale/
measureScale vẽ đúng thang).

Rà 72 dashboard thật trong EBM-Dashboards/ trước khi vá: 0/72 dùng template Dark Analyst (tất
cả dùng Evidence Workbench, đúng mặc định "EW mặc định, DA chỉ khi bác sĩ yêu cầu riêng") — chỉ
2 file `_view_DarkAnalyst_*.html` là bản xem trước/demo, không phải dữ liệu lâm sàng thật.

Canh bốn lớp, cùng khuôn `test_ew_template_ho_thiet_ke_thang_hieu_so.py`:
  • AN TOÀN (không cần node): escHtml/escUrl/escJs vẫn ĐỊNH NGHĨA đúng nguyên văn và được GỌI
    đủ số lượt tối thiểu — chặn tái diễn đúng lỗi vừa vá;
  • CẤU TRÚC (không cần node): 4 bản khớp byte; tập tiền tố họ thiết kế TRÙNG KHÍT
    `DESIGN_FAMILIES` của cổng liêm chính VÀ của evidence-workbench-template.html; danh sách từ
    của thang hiệu số TRÙNG KHÍT giữa DA/EW/Python (`build_ban_doc_chung_cu.py`);
  • HÀNH VI JS: chạy TOÀN BỘ engine thật của template trên DOM giả — designFamily, forest theo
    thang, qualityView có escape, panel chi tiết giữ design gốc. Máy không có node ⇒ SKIP CÓ LÝ
    DO (chưa kiểm được ≠ ĐẠT);
  • KHÔNG HỒI QUY tính năng cũ: GROUP_META còn đủ nhóm; forestBox/expandRow vẫn dùng escHtml.

Fixture offline, dữ liệu giả, không PII.

Kiểm đột biến không cần sửa file thật: đặt DA_TEMPLATE_UNDER_TEST trỏ tới một bản đã gây đột
biến (trong thư mục tạm) rồi chạy các test HÀNH VI/CẤU TRÚC.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TEMPLATE = REPO / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "templates" / "web-dashboard-dark-analyst.html"
TEMPLATE_BAN_SAO_GIT = (
    REPO / "sync" / "skills" / "dark-analyst" / "templates" / "web-dashboard-dark-analyst.html",
)
# Hai bản ngoài git (đồng bộ qua OneDrive) — chỉ có trên máy thật.
TEMPLATE_BAN_SAO_NGOAI_GIT = (
    REPO / "dashboard_mockups" / "templates" / "dark-analyst-template.html",
    REPO / "EBM_MASTER" / "skill_assets" / "web-dashboard-dark-analyst.html",
)
CONG_GIT = (
    REPO / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "verify_dashboard.py",
    REPO / "sync" / "skills" / "dark-analyst" / "tools" / "verify_dashboard.py",
)
CONG_NGOAI_GIT = (
    REPO / "EBM-Dashboards" / "tools" / "verify_dashboard.py",
    REPO / "EBM_MASTER" / "skill_assets" / "verify_dashboard.py",
)
EW_TEMPLATE = REPO / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "templates" / "web-dashboard-evidence-workbench.html"
BAN_DOC = REPO / "tools" / "build_ban_doc_chung_cu.py"

NODE = shutil.which("node")


# ───────────────────────────── tiện ích ─────────────────────────────

def _doc(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _ban_sao_git_tran() -> bool:
    spec = importlib.util.spec_from_file_location("_bst_da", REPO / "tools" / "ban_sao_tran.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.ban_sao_git_tran(REPO)


def _template_under_test() -> str:
    return _doc(Path(os.environ.get("DA_TEMPLATE_UNDER_TEST") or TEMPLATE))


def _js_mang(html: str, ten: str):
    """Đọc `const <ten>=[…];` của template — mảng chỉ chứa chuỗi nháy đơn, mảng lồng, chú thích."""
    m = re.search(r"const %s=(\[.*?\]);" % re.escape(ten), html, re.S)
    assert m, f"template không còn hằng {ten}"
    than = re.sub(r"/\*.*?\*/", "", m.group(1), flags=re.S)
    than = re.sub(r"'((?:[^'\\]|\\.)*)'", lambda x: json.dumps(x.group(1)), than)
    return json.loads(than)


def _hang_so_py(duong: Path, ten: str):
    """Đọc hằng literal ở mức module bằng ast — không thực thi mã của cổng."""
    for nut in ast.parse(_doc(duong)).body:
        if isinstance(nut, ast.Assign) and any(isinstance(t, ast.Name) and t.id == ten for t in nut.targets):
            return ast.literal_eval(nut.value)
    raise AssertionError(f"{duong} không còn hằng {ten}")


def _cong_hien_co() -> list[Path]:
    cong = list(CONG_GIT)
    if not _ban_sao_git_tran():
        cong += [p for p in CONG_NGOAI_GIT if p.exists()]
    return cong


def _mo_script_that(html: str) -> str:
    """Trích khối `<script>…</script>` THẬT (sau `<body>`).

    Bẫy đã gặp lúc viết chốt này: khối chú thích đầu file (`<!-- … -->`) tự nhắc tới chữ
    "<script>" như VÍ DỤ VĂN BẢN ("… ở cuối <script> bằng …"), khiến `re.findall` không mốc
    `<body>` bắt nhầm từ đó tới `</script>` THẬT — nuốt luôn toàn bộ CSS/HTML ở giữa. Trình
    duyệt KHÔNG bị lỗi này (bên trong `<!-- -->` không được phân tích lại thành thẻ), nhưng
    một bộ trích script bằng regex thì có — mốc vào `<body>` trước khi tìm.
    """
    than = html[html.index("<body>"):]
    scripts = re.findall(r"<script>(.*?)</script>", than, re.S)
    assert len(scripts) == 1, "template phải có đúng một khối <script> engine (sau <body>)"
    return scripts[0]


# ───────────────────────────── 1. AN TOÀN — chặn tái diễn mất escaping ─────────────────────────────

_ESCHTML_DEF = (
    "function escHtml(s){return String(s??'').replace(/&/g,'&amp;').replace(/</g,'&lt;')"
    ".replace(/>/g,'&gt;').replace(/\"/g,'&quot;').replace(/'/g,'&#39;');}"
)
_ESCURL_DEF = (
    "function escUrl(u){u=String(u||'').trim();return /^https?:\\/\\//i.test(u)"
    "?encodeURI(u).replace(/\"/g,'%22'):'';}"
)
_ESCJS_DEF = "function escJs(s){return String(s??'').replace(/\\\\/g,'\\\\\\\\').replace(/'/g,\"\\\\'\");}"


def test_ham_chong_xss_dinh_nghia_dung_nguyen_van():
    """escHtml/escUrl/escJs phải TỒN TẠI và ĐÚNG NGUYÊN VĂN — không phải chỉ khai báo suông."""
    html = _template_under_test()
    assert _ESCHTML_DEF in html, "escHtml() thiếu hoặc bị đổi — mất lá chắn XSS cho innerHTML"
    assert _ESCURL_DEF in html, "escUrl() thiếu hoặc bị đổi — href có thể nhận scheme javascript:"
    assert _ESCJS_DEF in html, "escJs() thiếu hoặc bị đổi — onclick=\"toggle('${e.id}')\" có thể bị thoát chuỗi"


def test_ham_chong_xss_duoc_goi_du_so_luot_toi_thieu():
    """Không chỉ ĐỊNH NGHĨA mà còn phải ĐƯỢC GỌI — bản lỗi 16/09 giữ nguyên định nghĩa (hoặc
    thậm chí xoá hẳn) nhưng phần render lõi (title/source/PICO/effect/link) không còn gọi tới."""
    html = _template_under_test()
    assert html.count("escHtml(") >= 40, f"escHtml( chỉ còn {html.count('escHtml(')} lượt gọi — quá ít so với mốc 46"
    assert html.count("escJs(") >= 3, f"escJs( chỉ còn {html.count('escJs(')} lượt gọi"
    assert html.count("escUrl(") >= 7, f"escUrl( chỉ còn {html.count('escUrl(')} lượt gọi"
    assert html.count('rel="noopener"') >= 3, "liên kết mở tab mới thiếu rel=\"noopener\" (reverse tabnabbing)"
    assert html.count("encodeURIComponent") >= 2, "href PMID/DOI thiếu encodeURIComponent"


# ───────────────────────────── 2. CẤU TRÚC ─────────────────────────────

def test_ban_sao_template_trong_git_khop_byte():
    goc = TEMPLATE.read_bytes()
    lech = [str(p.relative_to(REPO)) for p in TEMPLATE_BAN_SAO_GIT if p.read_bytes() != goc]
    assert not lech, f"bản sao template lệch byte so với {TEMPLATE.relative_to(REPO)}: {lech}"


def test_ban_sao_template_ngoai_git_khop_byte():
    if _ban_sao_git_tran():
        pytest.skip("bản sao git trần — dashboard_mockups/ và EBM_MASTER/ nằm ngoài git; "
                    "chạy trên máy có cây OneDrive")
    goc = TEMPLATE.read_bytes()
    thieu = [str(p.relative_to(REPO)) for p in TEMPLATE_BAN_SAO_NGOAI_GIT if not p.exists()]
    lech = [str(p.relative_to(REPO)) for p in TEMPLATE_BAN_SAO_NGOAI_GIT
            if p.exists() and p.read_bytes() != goc]
    assert not thieu, f"thiếu bản sao template ngoài git: {thieu}"
    assert not lech, ("bản sao template ngoài git lệch byte — sửa template rồi ĐỒNG BỘ Y HỆT "
                      f"(CLAUDE.md «BỐ CỤC/CSS = SỬA TEMPLATE»): {lech}")


def test_tien_to_ho_thiet_ke_trung_khit_cong_lien_chinh():
    ho = _js_mang(_template_under_test(), "DESIGN_FAMILIES")
    tien_to = [p for f in ho for p in f[4]]
    assert len(tien_to) == len(set(tien_to)), "một tiền tố xuất hiện ở hai họ — ánh xạ mơ hồ"
    for duong in _cong_hien_co():
        cong = set(_hang_so_py(duong, "DESIGN_FAMILIES"))
        assert set(tien_to) == cong, (
            f"template DA và {duong.relative_to(REPO)} lệch danh sách họ: "
            f"thiếu ở template {sorted(cong - set(tien_to))}, thừa ở template {sorted(set(tien_to) - cong)}")


def test_tien_to_ho_thiet_ke_trung_khit_evidence_workbench():
    """DA và EW phải nhận diện CÙNG một tập tiền tố — hai mẫu dùng chung schema DATA, một
    dashboard chuyển từ EW sang DA (hoặc ngược lại) không được đổi cách phân loại design.

    EW_TEMPLATE có thể CHƯA có `DESIGN_FAMILIES` nếu checkout này chưa hợp nhất bản vá EW
    tương ứng (PR riêng, ngày ký kết có thể khác PR đưa cơ chế này vào DA) — đó là CHƯA KIỂM
    ĐƯỢC, không phải lệch: skip có lý do, không fail."""
    if not EW_TEMPLATE.exists():
        pytest.skip("thiếu evidence-workbench-template.html để đối chiếu (checkout thiếu file)")
    ew_html = _doc(EW_TEMPLATE)
    if not re.search(r"\bconst DESIGN_FAMILIES=", ew_html):
        pytest.skip("evidence-workbench-template.html trong checkout này CHƯA có DESIGN_FAMILIES "
                    "— bản vá tương ứng ở EW chưa hợp nhất vào nhánh này")
    ho_da = _js_mang(_template_under_test(), "DESIGN_FAMILIES")
    ho_ew = _js_mang(ew_html, "DESIGN_FAMILIES")
    tien_to_da = {p for f in ho_da for p in f[4]}
    tien_to_ew = {p for f in ho_ew for p in f[4]}
    assert tien_to_da == tien_to_ew, (
        f"DA và EW lệch tập tiền tố: thiếu ở DA {sorted(tien_to_ew - tien_to_da)}, "
        f"thừa ở DA {sorted(tien_to_da - tien_to_ew)}")


def test_tien_to_hai_ho_khong_long_nhau():
    """Tiền tố của hai họ khác nhau không được là tiền tố của nhau — nếu không, kết quả phụ
    thuộc cách phá hoà thay vì dữ liệu."""
    ho = _js_mang(_template_under_test(), "DESIGN_FAMILIES")
    cap = [(f[0], p) for f in ho for p in f[4]]
    xung_dot = [(a, p, b, q) for a, p in cap for b, q in cap if a != b and (p.startswith(q) or q.startswith(p))]
    assert not xung_dot, xung_dot


def test_khoa_cu_van_thuoc_dung_ho_cua_minh():
    ho = {f[0]: f[4] for f in _js_mang(_template_under_test(), "DESIGN_FAMILIES")}
    for duong in CONG_GIT:
        for khoa in _hang_so_py(duong, "KNOWN_DESIGNS"):
            assert khoa in ho and khoa.lower() in ho[khoa], (
                f"khoá cũ {khoa!r} phải là một họ và là tiền tố của chính họ đó")


def test_danh_sach_thang_hieu_so_trung_khit_ew_va_python():
    """`build_ban_doc_chung_cu.py` là nguồn CHUẨN mà cả DA lẫn EW đều phải trùng khít — nhưng
    nếu checkout này chưa hợp nhất bản vá tương ứng ở Python/EW thì đó là CHƯA KIỂM ĐƯỢC, skip
    có lý do (không fail vì một PR khác chưa tới, không giả vờ đã kiểm)."""
    html = _template_under_test()
    ban_doc = _doc(BAN_DOC)
    ban_doc_co = "SCALE_RATIO_TERMS" in ban_doc
    ew_html = _doc(EW_TEMPLATE) if EW_TEMPLATE.exists() else None
    ew_co = ew_html is not None and re.search(r"\bconst SCALE_RATIO_TERMS=", ew_html)
    if not ban_doc_co and not ew_co:
        pytest.skip("build_ban_doc_chung_cu.py và evidence-workbench-template.html trong checkout "
                    "này đều CHƯA có SCALE_RATIO_TERMS — bản vá tương ứng chưa hợp nhất vào nhánh")
    for ten in ("SCALE_RATIO_TERMS", "SCALE_DIFF_TERMS", "SCALE_DIFF_FIRST_TOKEN_PREFIXES"):
        js_da = _js_mang(html, ten)
        if ban_doc_co:
            py_val = list(_hang_so_py(BAN_DOC, ten))
            assert js_da == py_val, f"{ten}: DA lệch Python (build_ban_doc_chung_cu.py)"
        if ew_co:
            js_ew = _js_mang(ew_html, ten)
            assert js_da == js_ew, f"{ten}: DA lệch EW (evidence-workbench-template.html)"


def test_group_meta_du_nhom_moi():
    html = _template_under_test()
    gm = re.search(r"const GROUP_META=(\{.*?\});", html)
    assert gm, "template không còn GROUP_META"
    for khoa in ("cao-tuoi", "thai-ky", "tre-em", "ckd", "gan", "dtd", "tim-mach", "da-thuoc"):
        assert f"'{khoa}'" in gm.group(1), f"GROUP_META thiếu nhóm {khoa!r} (thêm 2026-09-16)"


def test_rob_entries_dinh_nghia_dung_va_khong_gia_dinh_object():
    """robEntries() — thêm 16/09/2026 (cùng ngày với PR #10 trên evidence-workbench-template.html)
    để khớp lỗi thật: `rob` từng được ghi là CHUỖI VĂN XUÔI thay vì object {miền:'l'|'s'|'h'}
    (schema đòi), khiến `Object.values(chuỗi)`/`Object.keys(chuỗi)` lặp theo TỪNG KÝ TỰ và
    `RM[ký tự]` undefined ⇒ TypeError SẬP TOÀN BỘ render()/expandRow(). robEntries() phải từ
    chối chuỗi/mảng/null và chỉ trả entries khi có ít nhất một mã hợp lệ trong RM."""
    html = _template_under_test()
    m = re.search(r"function robEntries\(rob\)\{.*?\n\}", html, re.S)
    assert m, "template không còn hàm robEntries() — nghi tái diễn lỗi rob-là-chuỗi làm sập trang"
    than = m.group(0)
    assert "typeof rob!=='object'" in than or 'typeof rob!=="object"' in than
    assert "Array.isArray(rob)" in than
    assert "RM[r]" in than or "RM[" in than


def test_lop4_qualityview_dung_escaping():
    """qualityView() — khối MỚI nhất — phải escape mọi giá trị lấy từ DATA.standards/DATA.items,
    không được là chỗ DUY NHẤT còn escape trong khi phần lõi (title/source/effect) đã mất."""
    html = _template_under_test()
    m = re.search(r"function qualityView\(s\)\{.*?\n\}", html, re.S)
    assert m, "template không còn hàm qualityView()"
    than = m.group(0)
    assert than.count("escHtml(") >= 8, "qualityView() escape quá ít lượt so với mốc — nghi mất escaping"
    assert "escUrl(" in than


# ───────────────────────────── 3. HÀNH VI JS ─────────────────────────────

HO_KY_VONG = {
    "Guideline": "Guideline", "Cross-sectional — kiểm định độ chính xác chẩn đoán": "CrossSectional",
    "CẮT NGANG (mô tả)": "CrossSectional", "Nhãn thuốc — cảnh báo thần kinh (FDA)": "Regulatory",
    "Cơ chế — tổng quan tường thuật": "Mechanism", "Ca lâm sàng — tổng quan các báo cáo ca": "CaseSeries",
    "Cohort (A 2025) + Cross-sectional (B 2020)": "Cohort", "Bình luận — xã luận": "Other", "": "Other",
    "Meta": "Meta", "RCT": "RCT",
}

_DOM_GIA = r"""
const __els=new Map();
function __el(id){if(!__els.has(id))__els.set(id,{id,innerHTML:'',textContent:'',value:'',style:{},dataset:{},
  classList:{add(){},remove(){},toggle(){},contains(){return false}},addEventListener(){},click(){},focus(){}});
  return __els.get(id);}
globalThis.document={getElementById:__el,querySelector:s=>__el('qs:'+s),querySelectorAll:()=>[],
  createElement:t=>__el('ce:'+t),addEventListener(){},title:''};
globalThis.window=globalThis;
"""

_KHAI_THAC = r"""
;(()=>{
  const fx=__FX__, out={};
  out.ho=fx.designs.map(d=>designFamily(d));
  out.escHtmlXss=escHtml('<img src=x onerror=alert(1)>');
  out.escJsXss=escJs("a'); alert(1); //");
  out.escUrlXss=escUrl('javascript:alert(1)');
  out.escUrlOk=escUrl('https://pubmed.ncbi.nlm.nih.gov/123/');
  out.forestHR=forest({measure:'HR',hr:0.74,lo:0.65,hi:0.85,favors:true},200,26);
  out.forestSMD=forest({measure:'SMD',hr:0.40,lo:0.22,hi:0.59,favors:true},200,26);
  out.forestSMDneg=forest({measure:'SMD',hr:-0.36,lo:-0.62,hi:-0.10,favors:true},200,26);
  out.forestNegRatio=forest({measure:'',hr:-1.7,lo:-2.7,hi:-0.6},200,26);
  DATA.standards={frame:'X',sourceHierarchy:'PubMed',currency:'2026-09',searchSources:['PubMed'],
    gates:[{label:'<img src=x onerror=alert(1)>',status:'ok',note:'ok'}]};
  DATA.items.push({id:'J-XS',title:'X <script>alert(1)</script>',source:'Nguồn giả',
    design:'Cross-sectional — mô tả',gradeLevel:'na',decision:'consider',groups:[]});
  renderStatic();
  out.qualHtml=document.getElementById('qual').innerHTML;
  state.open='J-XS'; render();
  out.rowsHtml=document.getElementById('rows').innerHTML;
  state.open='J-ROB-STR'; render(); out.rowsRobStr=document.getElementById('rows').innerHTML;
  state.open='J-ROB-OBJ'; render(); out.rowsRobObj=document.getElementById('rows').innerHTML;
  console.log(JSON.stringify(out));
})();
"""


DU_LIEU_JS = {
    "meta": {"eyebrow": "Fixture", "question": "Fixture kiểm thử template DA", "updated": "2026-09-16",
             "pico": {"P": "p", "I": "i", "C": "c", "O": "o"}},
    "etd": None,
    "summary": {"conclusion": "Fixture offline, không phải khuyến cáo.", "doNow": ["Chỉ để kiểm thử"],
                "dontDo": ["Không áp dụng cho người bệnh"], "redFlags": ["Không có"]},
    "items": [
        {"id": "J-GL", "title": "Mục J-GL", "source": "Nguồn giả", "design": "Guideline",
         "gradeLevel": "na", "decision": "consider", "groups": [], "pico": {}},
        # Ca lỗi thật PR #10: `rob` là CHUỖI VĂN XUÔI thay vì object — nếu robEntries() bị gỡ,
        # render() sập ngay TỪ BOOTSTRAP (renderStatic();render(); cuối script) trước khi kịp
        # chạy tới _KHAI_THAC, khiến kq.returncode != 0 — tự nó đã là một phép thử.
        {"id": "J-ROB-STR", "title": "Mục rob chuỗi", "source": "Nguồn giả", "design": "RCT",
         "gradeLevel": "na", "decision": "apply", "groups": [], "pico": {},
         "rob": "Mù đôi, phân bổ ngẫu nhiên che giấu, phân tích ITT — nguy cơ sai lệch thấp."},
        {"id": "J-ROB-OBJ", "title": "Mục rob object", "source": "Nguồn giả", "design": "RCT",
         "gradeLevel": "na", "decision": "apply", "groups": [], "pico": {},
         "rob": {"Ngẫu nhiên hóa": "l", "Miền <script>alert(1)</script>": "s", "Mã lạ": "x"}},
    ],
}


@pytest.fixture(scope="module")
def js():
    if not NODE:
        pytest.skip("không có node trong PATH — CHƯA KIỂM ĐƯỢC hành vi JS của template (không phải ĐẠT)")
    html = _template_under_test()
    s = _mo_script_that(html)
    dau, moc = s.index("const DATA = {"), s.index("HẾT KHỐI DATA")
    fx = {"designs": list(HO_KY_VONG)}
    s = s[:dau] + "const DATA = " + json.dumps(DU_LIEU_JS, ensure_ascii=False) + ";\n" + s[s.rfind("/*", 0, moc):]
    chuong_trinh = _DOM_GIA + s + _KHAI_THAC.replace("__FX__", json.dumps(fx, ensure_ascii=False))
    kq = subprocess.run([NODE, "-"], input=chuong_trinh, capture_output=True, text=True,
                        encoding="utf-8", timeout=120)
    assert kq.returncode == 0, f"engine template lỗi khi chạy:\n{kq.stderr[-3000:]}"
    return json.loads(kq.stdout.strip().splitlines()[-1])


def test_js_designFamily_theo_tien_to(js):
    assert dict(zip(HO_KY_VONG, js["ho"])) == HO_KY_VONG


def test_js_ham_chong_xss_hoat_dong_that(js):
    assert "<img" not in js["escHtmlXss"] and "&lt;img" in js["escHtmlXss"]
    # escJs() KHÔNG xoá chuỗi "'); alert" — nó chỉ chèn "\" ngay TRƯỚC dấu nháy đơn để dấu
    # nháy đó không còn kết thúc chuỗi JS single-quote khi bị nội suy vào onclick='...'.
    # Vì vậy kiểm đúng bằng cách xác nhận dấu nháy trong input GIỜ có "\" đứng ngay trước,
    # không phải bằng cách đòi cả cụm chữ biến mất.
    assert "\\');" in js["escJsXss"], "escJs phải chèn \\ ngay trước mọi dấu nháy đơn"
    assert "a\\');" in js["escJsXss"], "escJs không chặn được thoát chuỗi single-quote"
    assert js["escUrlXss"] == "", "escUrl phải từ chối scheme javascript:"
    assert js["escUrlOk"].startswith("https://pubmed.ncbi.nlm.nih.gov")


def test_js_forest_smd_thang_tuyen_tinh_vach_0(js):
    assert 'data-scale="difference"' in js["forestSMD"]
    assert 'data-scale="difference"' in js["forestSMDneg"]
    m_pos = re.search(r'transform="rotate\(45 ([\d.]+) ', js["forestSMD"])
    m_neg = re.search(r'transform="rotate\(45 ([\d.]+) ', js["forestSMDneg"])
    assert float(m_pos.group(1)) > 100.0, "SMD dương (0,40) phải nằm bên PHẢI vạch 0 (x=100, w=200)"
    assert float(m_neg.group(1)) < 100.0, "SMD âm (-0,36) phải nằm bên TRÁI vạch 0"


def test_js_forest_ty_so_giu_thang_log(js):
    assert 'data-scale="ratio"' in js["forestHR"]


def test_js_forest_ty_so_khong_duong_khong_ve(js):
    assert "<svg" not in js["forestNegRatio"], "tỷ số có giá trị ≤ 0 không được ép vào mép trục log"


def test_js_qualityview_escape_that(js):
    assert "onerror=alert(1)" not in js["qualHtml"] or "&lt;img" in js["qualHtml"]
    assert "<img src=x onerror=alert(1)>" not in js["qualHtml"]


def test_js_khong_sap_khi_rob_la_chuoi_van_xuoi(js):
    """`js` fixture tự nó ĐÃ là phép thử chính: nếu robEntries() bị gỡ, subprocess node sập
    ngay từ bootstrap (renderStatic();render(); cuối script, TRƯỚC _KHAI_THAC) vì J-ROB-STR
    có `rob` là chuỗi — fixture không bao giờ tới được dòng console.log. Ở đây kiểm thêm
    NỘI DUNG hiển thị đúng: chuỗi hiện nguyên văn (đã escape), không phải mã miền giả."""
    assert "Mù đôi" in js["rowsRobStr"] or "M&#249; đ\xf4i" in js["rowsRobStr"]
    assert "robnote" in js["rowsRobStr"], "rob dạng chuỗi phải hiện qua .robnote, không phải chấm màu giả"


def test_js_rob_object_ten_mien_duoc_escape(js):
    assert "<script>alert(1)</script>" not in js["rowsRobObj"], "tên miền RoB chưa escape — lỗ XSS"
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in js["rowsRobObj"]


def test_js_bang_khong_thuc_thi_script_nhung_giu_design_goc(js):
    assert "<script>alert(1)</script>" not in js["rowsHtml"]
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in js["rowsHtml"]
    assert "Cross-sectional — mô tả" in js["rowsHtml"], "tooltip huy hiệu phải giữ design gốc"
    assert "Thiết kế" in js["rowsHtml"], "panel chi tiết phải có dòng Thiết kế cho truy nguyên"
