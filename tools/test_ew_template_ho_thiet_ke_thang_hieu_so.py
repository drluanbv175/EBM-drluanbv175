#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chốt hồi quy (16/09/2026): template Evidence Workbench + bản đọc chứng cứ.

VÌ SAO CÓ. Dựng dashboard VKDT tâm thần kinh 15/09 (59 mục) lộ ra hai giới hạn:
  1) `DESIGN_META` của template tra KHỚP CHÍNH XÁC 5 khoá, nên 61/1285 mục trong kho (Cắt
     ngang, Nhãn thuốc, Tổng quan hệ thống, Cơ chế, Ca lâm sàng, design lạ) có huy hiệu TRỐNG
     và biến mất khỏi bộ lọc "Loại thiết kế" — trong khi cổng verify_dashboard.py đã nhận các
     HỌ đó theo tiền tố từ 12/08;
  2) forest mini LUÔN vẽ thang log, vạch 1,0 ⇒ SMD/MD/RD vẽ sai phía. Bản đọc còn nặng hơn:
     "SMD đau" 0,69 (0,54–0,84) rơi vào dải "ủng hộ" và "Chênh DAS28" 1,24 (1,10–1,37) bị gắn
     nhãn "Gây hại" chỉ vì vị trí so với vạch 1,0.

Canh ba lớp:
  • CẤU TRÚC (không cần node): bản sao template khớp byte; tập tiền tố họ thiết kế TRÙNG KHÍT
    `DESIGN_FAMILIES` của cổng; danh sách từ của thang hiệu số TRÙNG KHÍT giữa JS và Python;
  • HÀNH VI JS: chạy TOÀN BỘ engine thật của template trên DOM giả — huy hiệu, facet, bộ lọc
    theo họ, forest mini theo thang. Máy không có node ⇒ SKIP CÓ LÝ DO (chưa kiểm được ≠ ĐẠT);
  • HÀNH VI bản đọc: `build_page` đưa chênh lệch vào mục riêng trên thang tuyến tính, và trang
    không có chênh lệch giữ nguyên bố cục cũ.

Fixture offline, dữ liệu giả, không PII.

Kiểm đột biến không cần sửa file thật: đặt EW_TEMPLATE_UNDER_TEST / BAN_DOC_UNDER_TEST trỏ tới
một bản đã gây đột biến (trong thư mục tạm) rồi chạy các test HÀNH VI.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import math
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TEMPLATE = REPO / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "templates" / "web-dashboard-evidence-workbench.html"
TEMPLATE_BAN_SAO_GIT = (
    REPO / "sync" / "skills" / "dark-analyst" / "templates" / "web-dashboard-evidence-workbench.html",
)
# Hai bản ngoài git (đồng bộ qua OneDrive) — chỉ có trên máy thật.
TEMPLATE_BAN_SAO_NGOAI_GIT = (
    REPO / "dashboard_mockups" / "templates" / "evidence-workbench-template.html",
    REPO / "EBM_MASTER" / "skill_assets" / "web-dashboard-evidence-workbench.html",
)
CONG_GIT = (
    REPO / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "verify_dashboard.py",
    REPO / "sync" / "skills" / "dark-analyst" / "tools" / "verify_dashboard.py",
)
CONG_NGOAI_GIT = (
    REPO / "EBM-Dashboards" / "tools" / "verify_dashboard.py",
    REPO / "EBM_MASTER" / "skill_assets" / "verify_dashboard.py",
)
BAN_DOC = REPO / "tools" / "build_ban_doc_chung_cu.py"
BAN_DOC_VENDOR = REPO / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "build_ban_doc_chung_cu.py"

NODE = shutil.which("node")


# ───────────────────────────── tiện ích ─────────────────────────────

def _doc(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _ban_sao_git_tran() -> bool:
    spec = importlib.util.spec_from_file_location("_bst_ew", REPO / "tools" / "ban_sao_tran.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.ban_sao_git_tran(REPO)


def _template_under_test() -> str:
    return _doc(Path(os.environ.get("EW_TEMPLATE_UNDER_TEST") or TEMPLATE))


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


@pytest.fixture(scope="module")
def bd():
    duong = Path(os.environ.get("BAN_DOC_UNDER_TEST") or BAN_DOC)
    spec = importlib.util.spec_from_file_location("ban_doc_under_test", duong)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


# Bảng chân lý lấy từ nhãn `measure` THẬT trong kho (72 dashboard, 16/09/2026) cộng các bẫy đã
# biết. Mỗi dòng: (nhãn thước đo, thang đúng).
BANG_THANG = [
    ("HR", "ratio"),
    ("HR tử vong khi có trầm cảm", "ratio"),
    ("OR lo âu mới mắc", "ratio"),
    ("IRR đợt cấp", "ratio"),
    ("aOR", "ratio"),
    ("RoM", "ratio"),
    ("RR sa sút trí tuệ — thuốc sinh học so với DMARD cổ điển", "ratio"),   # "RD" nằm trong DMARD
    ("Tỷ lệ đáp ứng ở nhóm dùng bDMARD", "ratio"),     # không có cụm tỷ số nào đứng trước che chắn
    ("Tỷ lệ mắc AMD sau 5 năm", "ratio"),               # "MD" nằm trong AMD
    ("Tỷ số chênh hiệu chỉnh — thuốc được NGƯNG", "ratio"),                # "chênh" sau cụm tỷ số
    ("Tỷ suất chênh (OR) — hút thuốc", "ratio"),
    ("ty so chenh hieu chinh", "ratio"),
    ("Nguy cơ tương đối — tỷ lệ người còn thuốc không phù hợp", "ratio"),
    ("Chẹn β — tử vong", "ratio"),                                          # β KHÔNG đứng đầu
    ("Hiệu số", "ratio"),        # "hiệu số" trơn là cách gọi chung "hiệu quả" của dự án
    ("Se", "ratio"),
    ("", "ratio"),
    (None, "ratio"),
    ("SMD", "difference"),
    ("SMD triệu chứng trầm cảm", "difference"),
    ("smd đau (có trầm cảm so với không)", "difference"),
    ("MD", "difference"),
    ("MD-VAS 0–10", "difference"),
    ("WMD huyết áp tâm thu", "difference"),
    ("RD", "difference"),
    ("Chênh DAS28 khi có đau xơ cơ", "difference"),
    ("Chênh lệch trung bình điểm lo âu Beck", "difference"),
    ("Chênh lệch nguy cơ tuyệt đối — ngưng benzodiazepine", "difference"),
    ("Hiệu số trung bình — chất lượng sống", "difference"),
    ("Hiệu số trung bình chuẩn hoá — số thuốc không phù hợp", "difference"),
    ("Standardized mean difference (Hedges g)", "difference"),
    ("Risk difference", "difference"),
    ("ΔHbA1c(12mg)", "difference"),
    ("\u2206HbA1c", "difference"),                                         # ký hiệu INCREMENT
    ("β eGFR (MTX ≥12 vs 8-12mg/tuần)", "difference"),
]

BANG_KHAI_THANG = [
    ({"measure": "SMD", "scale": "ratio"}, "ratio"),            # khai tường minh thắng suy luận
    ({"measure": "HR", "scale": "difference"}, "difference"),
    ({"measure": "SMD", "scale": " Difference "}, "difference"),
    ({"measure": "HR", "scale": "log"}, "ratio"),               # giá trị lạ ⇒ bỏ qua, suy từ measure
    ({"measure": "SMD", "scale": "log"}, "difference"),
    ({"measure": "HR"}, "ratio"),
    ({}, "ratio"),
]


# ───────────────────────────── 1. CẤU TRÚC ─────────────────────────────

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


def test_ban_doc_vendor_khop_byte():
    assert BAN_DOC_VENDOR.read_bytes() == BAN_DOC.read_bytes(), (
        "sync/skills/cap-nhat-chung-cu-y-khoa/tools/build_ban_doc_chung_cu.py lệch tools/")


def test_verifier_pipeline_bat_ban_sao_template_lech_byte(tmp_path, monkeypatch):
    """`verify_clinical_evidence_update_pipeline._check_templates` phải FAIL khi một bản sao
    template tụt lại dù vẫn đủ marker, và PASS khi bốn bản khớp byte."""
    spec = importlib.util.spec_from_file_location("_vcep_ew", REPO / "tools" / "verify_clinical_evidence_update_pipeline.py")
    V = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = V
    spec.loader.exec_module(V)
    ban = [tmp_path / f"ban{i}.html" for i in range(4)]
    goc = TEMPLATE.read_bytes()
    for p in ban:
        p.write_bytes(goc)
    for ten, p in zip(("EW_TEMPLATE", "EW_HUB_ASSET", "EW_SKILL_TEMPLATE", "EW_DARK_SKILL_TEMPLATE"), ban):
        monkeypatch.setattr(V, ten, p)
    kq = V._check_templates()
    assert kq.status == "PASS", kq.evidence
    ban[1].write_bytes(goc.replace(b"</body>", b"<!-- ban cu -->\n</body>"))
    kq = V._check_templates()
    assert kq.status == "FAIL" and "LỆCH BYTE" in kq.evidence, kq.evidence


def _cong_hien_co() -> list[Path]:
    cong = list(CONG_GIT)
    if not _ban_sao_git_tran():
        cong += [p for p in CONG_NGOAI_GIT if p.exists()]
    return cong


def test_tien_to_ho_thiet_ke_trung_khit_cong_lien_chinh():
    ho = _js_mang(_template_under_test(), "DESIGN_FAMILIES")
    tien_to = [p for f in ho for p in f[4]]
    assert len(tien_to) == len(set(tien_to)), "một tiền tố xuất hiện ở hai họ — ánh xạ mơ hồ"
    for duong in _cong_hien_co():
        cong = set(_hang_so_py(duong, "DESIGN_FAMILIES"))
        assert set(tien_to) == cong, (
            f"template và {duong.relative_to(REPO)} lệch danh sách họ: "
            f"thiếu ở template {sorted(cong - set(tien_to))}, thừa ở template {sorted(set(tien_to) - cong)}")


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


def test_danh_sach_thang_hieu_so_trung_khit_js_va_python(bd):
    html = _template_under_test()
    for ten in ("SCALE_RATIO_TERMS", "SCALE_DIFF_TERMS", "SCALE_DIFF_FIRST_TOKEN_PREFIXES"):
        assert _js_mang(html, ten) == list(getattr(bd, ten)), f"{ten} lệch giữa template và bản đọc"
    assert bd.STANDARDIZED_DIFF_TERMS <= set(bd.SCALE_DIFF_TERMS)


# ───────────────────────────── 2. LUẬT THANG (Python) ─────────────────────────────

@pytest.mark.parametrize("nhan,thang", BANG_THANG)
def test_luat_thang_ban_doc(bd, nhan, thang):
    assert bd.measure_scale(nhan) == thang


@pytest.mark.parametrize("effect,thang", BANG_KHAI_THANG)
def test_khai_thang_tuong_minh_ban_doc(bd, effect, thang):
    assert bd.effect_scale(effect) == thang


def test_effect_khong_phai_dict_la_ty_so(bd):
    assert bd.effect_scale(None) == "ratio"


def test_truc_tuyen_tinh_doi_xung_quanh_0(bd):
    ax = bd.LinearAxis.fit([-0.62, 0.59, 0.40])
    assert ax.pos(0) == pytest.approx(50.0)
    ticks = ax.ticks()
    assert 0.0 in ticks and ticks == sorted(ticks)
    assert min(ticks) == pytest.approx(-1.0) and max(ticks) == pytest.approx(1.0)
    assert all(0 < ax.pos(t) < 100 for t in ticks), "nhãn mép bị cắt"
    vi_tri = [ax.pos(t) for t in ticks]
    assert all(b - a >= ax.MIN_TICK_GAP for a, b in zip(vi_tri, vi_tri[1:])), "nhãn trục chồng nhau"


# ───────────────────────────── 3. HÀNH VI bản đọc ─────────────────────────────

def _item(id_, measure, hr, lo, hi, *, favors=None, decision="consider", design="Meta"):
    eff = {"measure": measure, "hr": hr, "lo": lo, "hi": hi}
    if favors is not None:
        eff["favors"] = favors
    return {"id": id_, "title": f"Mục kiểm thử {id_}", "design": design, "decision": decision,
            "source": "Nguồn giả", "effect": eff}


DU_LIEU_BAN_DOC = {
    "meta": {"question": "Fixture bản đọc: thang hiệu số", "updated": "2026-09-16"},
    "summary": {"conclusion": "Fixture offline, không phải khuyến cáo.",
                "doNow": ["Chỉ dùng để kiểm thử."], "dontDo": ["Không áp dụng cho người bệnh."],
                "redFlags": ["Không có."]},
    "items": [
        _item("R-HR", "HR tử vong", 0.74, 0.65, 0.85, favors=True, decision="apply", design="RCT"),
        _item("R-OR", "OR lo âu mới mắc", 1.2, 1.03, 1.39, favors=False, design="Cohort"),
        _item("D-SMD", "SMD triệu chứng trầm cảm", 0.40, 0.22, 0.59, favors=True),
        _item("D-SMDN", "SMD mệt mỏi — hoạt động thể lực", -0.36, -0.62, -0.10, favors=True),
        _item("D-CHENH", "Chênh DAS28 khi có đau xơ cơ", 1.24, 1.10, 1.37),        # không khai favors
        _item("D-HARM", "SMD nhận thức tổng thể", -0.57, -0.70, -0.43, favors=False),
        _item("N-NEG", "", -1.7, -2.7, -0.6, decision="notyet", design="RCT"),      # tỷ số ≤ 0
        {"id": "N-GL", "title": "Mục kiểm thử N-GL", "design": "Guideline", "decision": "apply",
         "source": "Nguồn giả"},
    ],
}


def _muc(html: str, id_: str) -> str:
    m = re.search(r'<section class="sec[^"]*" id="%s">(.*?)</section>' % re.escape(id_), html, re.S)
    return m.group(1) if m else ""


def _dong(html: str, measure: str) -> str:
    """Khối <div class="trial …"> chứa nhãn thước đo đã cho."""
    for khoi in re.split(r'(?=<div class="trial )', html):
        if f'<span class="num">{measure} ' in khoi:
            return khoi
    raise AssertionError(f"không thấy dòng biểu đồ của {measure!r}")


def _left(khoi: str, lop: str) -> float:
    return float(re.search(r'<div class="%s" style="left:(-?[\d.]+)%%' % lop, khoi).group(1))


def _nhan(khoi: str) -> str:
    return re.search(r'<span class="tag t-\w+">([^<]*)</span>', khoi).group(1)


@pytest.fixture(scope="module")
def trang(bd):
    return bd.build_page(DU_LIEU_BAN_DOC, "fixture.html")


def test_chenh_lech_khong_len_truc_log(trang):
    ung_ho, khong = _muc(trang, "ungho"), _muc(trang, "khong")
    assert "HR tử vong" in ung_ho and "OR lo âu mới mắc" in khong, "nhánh tỷ số phải giữ nguyên"
    for m in ("SMD triệu chứng trầm cảm", "SMD mệt mỏi", "Chênh DAS28", "SMD nhận thức"):
        assert m not in ung_ho and m not in khong, f"{m!r} là chênh lệch nhưng nằm trên trục log"


def test_chenh_lech_co_muc_rieng_thang_tuyen_tinh(trang):
    muc = _muc(trang, "chenhlech")
    assert muc, "thiếu mục «Hiệu số dạng chênh lệch»"
    for m in ("SMD triệu chứng trầm cảm", "SMD mệt mỏi", "Chênh DAS28", "SMD nhận thức"):
        assert m in muc
    duong = _dong(muc, "SMD triệu chứng trầm cảm")
    am = _dong(muc, "SMD mệt mỏi — hoạt động thể lực")
    assert _left(duong, "nline") == pytest.approx(50.0), "vạch 0 phải ở giữa trục tuyến tính"
    assert _left(duong, "dot") > _left(duong, "nline"), "SMD dương phải nằm bên PHẢI vạch 0"
    assert _left(am, "dot") < _left(am, "nline"), "SMD âm phải nằm bên TRÁI vạch 0"
    assert "−0,36 (−0,62 đến −0,10)" in am, "số âm hiển thị bằng dấu trừ thật, khoảng dùng «đến»"


def test_smd_chung_mot_thang_chenh_lech_co_don_vi_thang_rieng(trang):
    khung = re.findall(r'<div class="field">.*?(?=<div class="field">|<div class="legend">)',
                       _muc(trang, "chenhlech"), re.S)
    assert len(khung) == 2, f"cần 1 khung SMD dùng chung + 1 khung riêng cho Chênh DAS28, có {len(khung)}"
    smd = [k for k in khung if "SMD triệu chứng trầm cảm" in k]
    assert smd and "SMD mệt mỏi" in smd[0] and "SMD nhận thức" in smd[0]
    assert "Chênh DAS28" not in smd[0]


def test_nhan_gay_hai_khong_suy_tu_phia_cua_vach(trang):
    muc = _muc(trang, "chenhlech")
    assert _nhan(_dong(muc, "Chênh DAS28 khi có đau xơ cơ")) != "Gây hại", (
        "Chênh DAS28 1,24 (1,10–1,37) không khai favors — không được gắn «Gây hại» theo vị trí")
    assert _nhan(_dong(muc, "SMD nhận thức tổng thể")) == "Gây hại", (
        "favors=false và khoảng tin cậy không chạm 0 ⇒ «Gây hại»")


def test_ty_so_khong_duong_van_xuong_danh_sach_khong_bieu_do(trang):
    assert "N-NEG" in _muc(trang, "khac") and "N-GL" in _muc(trang, "khac")


def test_muc_luc_va_so_dem_khi_co_chenh_lech(trang):
    assert '<a href="#chenhlech">4. Hiệu số dạng chênh lệch</a>' in trang
    assert '<a href="#khac">5. Khuyến cáo và đồng thuận</a>' in trang
    assert '<a href="#vn">6. Áp dụng tại Việt Nam</a>' in trang
    assert '<b class="ok">6</b><span>mục có hiệu số định lượng</span>' in trang   # 2 tỷ số + 4 chênh lệch


def test_trang_khong_co_chenh_lech_giu_bo_cuc_cu(bd):
    du_lieu = dict(DU_LIEU_BAN_DOC, items=[i for i in DU_LIEU_BAN_DOC["items"] if not i["id"].startswith("D-")])
    trang = bd.build_page(du_lieu, "fixture.html")
    assert 'id="chenhlech"' not in trang and "b-diff" not in trang
    assert '<a href="#khac">4. Khuyến cáo và đồng thuận</a>' in trang
    assert "Mọi hiệu số nằm trên cùng một trục thang log" in trang


# ───────────────────────────── 4. HÀNH VI JS của template ─────────────────────────────

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
  out.facet=document.getElementById('f-design').innerHTML;
  out.bang=tableView(DATA.items);
  state.filters.design.add('CrossSectional'); out.locCatNgang=filtered().map(x=>x.id); state.filters.design.clear();
  state.filters.design.add('Other'); out.locKhac=filtered().map(x=>x.id); state.filters.design.clear();
  out.thang=fx.measures.map(m=>measureScale(m));
  out.khaiThang=fx.effects.map(e=>effectScale(e));
  out.forest=Object.fromEntries(DATA.items.filter(x=>x.effect).map(x=>[x.id,miniForest(x.effect)]));
  state.selected='J-SMD'; renderDetail(); out.chiTietSmd=document.getElementById('detail').innerHTML;
  state.selected='J-HR'; renderDetail(); out.chiTietHr=document.getElementById('detail').innerHTML;
  console.log(JSON.stringify(out));
})();
"""


def _j(id_, design, effect=None):
    it = {"id": id_, "title": f"Mục {id_}", "source": "Nguồn giả", "design": design,
          "gradeLevel": "na", "decision": "consider", "groups": []}
    if effect is not None:
        it["effect"] = effect
    return it


DU_LIEU_JS = {
    "meta": {"eyebrow": "Fixture", "question": "Fixture kiểm thử template", "updated": "2026-09-16",
             "pico": {"P": "p", "I": "i", "C": "c", "O": "o"}},
    "summary": {"conclusion": "Fixture offline, không phải khuyến cáo.", "doNow": ["Chỉ để kiểm thử"],
                "dontDo": ["Không áp dụng cho người bệnh"], "redFlags": ["Không có"]},
    "items": [
        _j("J-GL", "Guideline"),
        _j("J-XS1", "Cross-sectional — kiểm định độ chính xác chẩn đoán"),
        _j("J-XS2", "CẮT NGANG (mô tả)"),
        _j("J-LBL", "Nhãn thuốc — cảnh báo thần kinh (FDA)"),
        _j("J-MEC", "Cơ chế — tổng quan tường thuật"),
        _j("J-CAS", "Ca lâm sàng — tổng quan các báo cáo ca"),
        _j("J-MIX", "Cohort (A 2025) + Cross-sectional (B 2020)"),
        _j("J-OTH", "Bình luận — xã luận"),
        _j("J-EMP", ""),
        _j("J-SMD", "Meta", {"measure": "SMD triệu chứng trầm cảm", "hr": 0.40, "lo": 0.22, "hi": 0.59, "favors": True}),
        _j("J-SMDN", "Meta", {"measure": "SMD mệt mỏi — hoạt động thể lực", "hr": -0.36, "lo": -0.62, "hi": -0.10, "favors": True}),
        _j("J-HR", "RCT", {"measure": "HR", "hr": 0.74, "lo": 0.65, "hi": 0.85, "favors": True}),
        _j("J-NEG", "RCT", {"measure": "", "hr": -1.7, "lo": -2.7, "hi": -0.6}),
        _j("J-EXP", "RCT", {"measure": "Điểm VAS", "scale": "difference", "hr": 1.5, "lo": -0.2, "hi": 3.2}),
    ],
}
HO_KY_VONG = {
    "Guideline": "Guideline", "Cross-sectional — kiểm định độ chính xác chẩn đoán": "CrossSectional",
    "CẮT NGANG (mô tả)": "CrossSectional", "Nhãn thuốc — cảnh báo thần kinh (FDA)": "Regulatory",
    "Cơ chế — tổng quan tường thuật": "Mechanism", "Ca lâm sàng — tổng quan các báo cáo ca": "CaseSeries",
    "Cohort (A 2025) + Cross-sectional (B 2020)": "Cohort", "Bình luận — xã luận": "Other", "": "Other",
    "Meta": "Meta", "RCT": "RCT",
}


@pytest.fixture(scope="module")
def js():
    if not NODE:
        pytest.skip("không có node trong PATH — CHƯA KIỂM ĐƯỢC hành vi JS của template (không phải ĐẠT)")
    html = _template_under_test()
    scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
    assert len(scripts) == 1, "template phải có đúng một khối <script> engine"
    s = scripts[0]
    dau, moc = s.index("const DATA = {"), s.index("HẾT KHỐI DATA")
    s = s[:dau] + "const DATA = " + json.dumps(DU_LIEU_JS, ensure_ascii=False) + ";\n" + s[s.rfind("/*", 0, moc):]
    fx = {"designs": list(HO_KY_VONG), "measures": [m for m, _ in BANG_THANG],
          "effects": [e for e, _ in BANG_KHAI_THANG]}
    chuong_trinh = _DOM_GIA + s + _KHAI_THAC.replace("__FX__", json.dumps(fx, ensure_ascii=False))
    kq = subprocess.run([NODE, "-"], input=chuong_trinh, capture_output=True, text=True,
                        encoding="utf-8", timeout=120)
    assert kq.returncode == 0, f"engine template lỗi khi chạy:\n{kq.stderr[-3000:]}"
    return json.loads(kq.stdout.strip().splitlines()[-1])


def test_js_designFamily_theo_tien_to(js):
    assert dict(zip(HO_KY_VONG, js["ho"])) == HO_KY_VONG


def test_js_facet_liet_ke_moi_ho_voi_so_dem(js):
    facet = {k: (nhan, int(n)) for k, nhan, n in re.findall(
        r"toggleFacet\('design','([^']+)'\)\"><span class=\"box\">[^<]*</span><span class=\"dot\" "
        r"style=\"[^\"]*\"></span><span class=\"nm\">([^<]*)</span><span class=\"ct\">(\d+)</span>", js["facet"])}
    assert facet.get("CrossSectional") == ("Cắt ngang", 2)
    assert facet.get("Regulatory") == ("Nhãn thuốc / cơ quan quản lý", 1)
    assert facet.get("Mechanism") == ("Cơ chế / dược động học", 1)
    assert facet.get("CaseSeries") == ("Ca lâm sàng / chuỗi ca", 1)
    assert facet.get("Other") == ("Khác", 2)
    assert facet.get("Cohort") == ("Cohort", 1) and facet.get("RCT") == ("RCT", 3)
    assert sum(n for _, n in facet.values()) == len(DU_LIEU_JS["items"]), "có mục không vào facet nào"


def test_js_moi_huy_hieu_co_nhan_va_giu_design_goc(js):
    huy_hieu = re.findall(r'<span class="badge ([^"]*)"([^>]*)><span class="d"></span>([^<]*)</span>', js["bang"])
    assert len(huy_hieu) == len(DU_LIEU_JS["items"])
    assert all(lop.strip() and nhan.strip() for lop, _, nhan in huy_hieu), "còn huy hiệu trống"
    assert 'title="Nhãn thuốc — cảnh báo thần kinh (FDA)"' in js["bang"], "tooltip phải giữ design gốc"


def test_js_loc_theo_ho(js):
    assert js["locCatNgang"] == ["J-XS1", "J-XS2"]
    assert js["locKhac"] == ["J-OTH", "J-EMP"]


def test_js_luat_thang_trung_python(js, bd):
    ky_vong = [t for _, t in BANG_THANG]
    assert js["thang"] == ky_vong
    assert [bd.measure_scale(m) for m, _ in BANG_THANG] == js["thang"], "JS và Python suy thang khác nhau"
    assert js["khaiThang"] == [t for _, t in BANG_KHAI_THANG]


def _forest(svg: str) -> dict:
    so = r"(-?[\d.]+)"
    lines = re.findall(r'<line x1="%s" y1="([\d.]+)" x2="%s"' % (so, so), svg)
    return {"thang": re.search(r'data-scale="(\w+)"', svg).group(1),
            "vach": float(lines[0][0]),
            "ci": (float(lines[1][0]), float(lines[1][2])) if len(lines) > 1 else None,
            "diem": float(re.search(r"rotate\(45 %s " % so, svg).group(1))}


def test_js_forest_smd_thang_tuyen_tinh_vach_0(js):
    duong, am = _forest(js["forest"]["J-SMD"]), _forest(js["forest"]["J-SMDN"])
    assert duong["thang"] == am["thang"] == "difference"
    assert duong["vach"] == pytest.approx(54.0), "vạch 0 ở giữa khung 108px"
    assert duong["diem"] > duong["vach"] and min(duong["ci"]) > duong["vach"], "SMD 0,40 (0,22–0,59) phải bên PHẢI vạch 0"
    assert am["diem"] < am["vach"] and max(am["ci"]) < am["vach"], "SMD −0,36 (−0,62; −0,10) phải bên TRÁI vạch 0"


def test_js_forest_ty_so_giu_thang_log(js):
    hr = _forest(js["forest"]["J-HR"])
    vach_1 = 108 * (math.log(1) - math.log(0.4)) / (math.log(2.0) - math.log(0.4))
    assert hr["thang"] == "ratio" and hr["vach"] == pytest.approx(vach_1, abs=0.01)
    assert hr["diem"] < hr["vach"]


def test_js_forest_ty_so_khong_duong_khong_ve(js):
    assert "<svg" not in js["forest"]["J-NEG"], "tỷ số có giá trị ≤ 0 không được ép vào mép trục log"


def test_js_forest_khai_thang_tuong_minh(js):
    assert _forest(js["forest"]["J-EXP"])["thang"] == "difference"


def test_js_panel_chi_tiet_noi_ro_thang(js):
    assert "vạch 0 · thang tuyến tính" in js["chiTietSmd"]
    assert "ngưỡng 1.0 · thang log" in js["chiTietHr"]
    assert "SMD triệu chứng trầm cảm" in js["chiTietSmd"]
