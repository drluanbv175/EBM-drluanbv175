#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HÒM THƯ BÁC SĨ — một cửa cố định cho mọi sản phẩm hệ sinh ra (17/08/2026).

v2 (17/08 tối): bác sĩ chê bản đầu «không chấp nhận được» về học thuật/thẩm mỹ
— renderer thô bẹt cấu trúc 6-trường/thẻ thành văn xuôi. Nay: PARSE thẻ thành
cấu trúc rồi render CARD học thuật theo ngôn ngữ thiết kế Evidence Workbench
(semantic màu Áp dụng/Cân nhắc/Chưa đủ; hiệu số tách khối tabular; PMID/DOI
thành link chuẩn; rủi ro tách hai vế; footnote thẩm định riêng).

Khối: ① gói tuần (card từng thẻ) ② cảnh báo 14d ③ bản đọc 7d ④ việc chờ 👤
⑤ ứng viên ngoài-quét. Chỉ ĐỌC và RENDER. Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import re
import subprocess
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
RA = REPO / "HOM-THU-BAC-SI.html"

MAU_DE_XUAT = {"Áp dụng ngay": ("apply", "#15803d", "#dcfce7"),
               "Cân nhắc": ("consider", "#a16207", "#fef9c3"),
               "Chưa đủ": ("notyet", "#c2410c", "#ffedd5")}


def _inline(t: str) -> str:
    """Inline markdown → HTML: bold, italic, code, PMID/DOI thành link."""
    t = html.escape(t, quote=False)
    t = _ha_caps_nhan_manh(t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<i>\1</i>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"PMID (\d{6,9})",
               r'<a class="id" href="https://pubmed.ncbi.nlm.nih.gov/\1/">PMID \1</a>', t)
    t = re.sub(r"doi:(10\.\S+?)(?=[\s|,)]|$)",
               r'<a class="id" href="https://doi.org/\1">doi:\1</a>', t)
    # ký hiệu vận hành → dạng học thuật: chấm màu + chữ nghiêng, không gãy dòng
    t = t.replace("🔴", '<span class="cham do">●</span>')
    t = t.replace("🟠", '<span class="cham cam">●</span>')
    t = t.replace("🟡", '<span class="cham vang">●</span>')
    t = t.replace("🟢", '<span class="cham xanh">●</span>')
    t = t.replace("👤 bác sĩ", '<span class="vai">Bác&nbsp;sĩ</span>')
    t = t.replace("🤖 máy", '<span class="vai">Máy</span>')
    t = t.replace("👤", '<span class="vai">Bác&nbsp;sĩ</span>')
    t = t.replace("🤖", '<span class="vai">Máy</span>')
    return t


# Viết tắt tiếng Việt CÓ DẤU được phép toàn-hoa (không hạ):
VIET_TAT_VIET = {"ĐTĐ", "ĐM", "ĐMC", "ĐĐ"}
_DAU_VIET = "ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ"
# Từ Việt thuần ASCII (không mang dấu ở dạng nào) — chỉ hạ khi đứng CÙNG CỤM
# với một từ có dấu (vd «THEO DÕI»); đứng lẻ thì giữ để không đụng viết tắt:
_TU_VIET_KHONG_DAU = {"theo", "trong", "khi", "cho", "hay", "ngay",
                       "sung", "gian", "hai", "cao", "an"}
_CUM_HOA = re.compile(rf"\b[A-Z{_DAU_VIET}]{{2,}}(?:[ ]+[A-Z{_DAU_VIET}]{{2,}})*\b")


def _ha_caps_nhan_manh(s: str) -> str:
    """CHỮ HOA TOÀN PHẦN kiểu nhấn mạnh (quy ước terminal cũ) → thường + <b>.

    Yêu cầu bác sĩ 17/08: «đừng viết hoa tuỳ tiện, cần nhấn mạnh thì in đậm».
    Xử theo CỤM (v11 — lỗi thật «THEO DÕI» bị xé đôi: DÕI hạ, THEO sót lại):
    trong một cụm toàn-hoa liên tiếp, từ CÓ DẤU luôn hạ; từ ASCII chỉ hạ khi
    (a) cụm có ít nhất một từ có dấu VÀ (b) nó nằm trong danh sách từ Việt
    thuần ASCII đã duyệt — viết tắt thật (RCT, PMID, COPD…) không bao giờ hạ."""
    def thay_cum(m):
        toks = m.group(0).split()
        co_dau = any(any(c in _DAU_VIET for c in tk) for tk in toks)
        ra = []
        for tk in toks:
            if tk in VIET_TAT_VIET:
                ra.append(tk)
            elif any(c in _DAU_VIET for c in tk):
                ra.append(f"<b>{tk.lower()}</b>")
            elif co_dau and tk.lower() in _TU_VIET_KHONG_DAU:
                ra.append(f"<b>{tk.lower()}</b>")
            else:
                ra.append(tk)
        return " ".join(ra)
    s = _CUM_HOA.sub(thay_cum, s)
    return s.replace("</b> <b>", " ")


def _hoa_dau(s: str) -> str:
    """Viết hoa ký tự chữ đầu tiên (bỏ qua tag/ngoặc/nháy mở đầu) — yêu cầu bác sĩ 17/08."""
    return re.sub(r'^((?:<[^>]+>|[«"(\s])*)([a-zà-ỹ])',
                  lambda m: m.group(1) + m.group(2).upper(), s, count=1)


def _tach_ngoai_ngoac(nd: str, dau: str) -> list[str]:
    """Tách theo `dau` CHỈ khi đứng ngoài mọi cặp ngoặc ()/[] và ngoài tag HTML —
    sửa bug 17/08: «RR 0,40 (95% CI 0,26–0,60; P<0,001)» từng bị cắt đôi giữa ngoặc."""
    manh, dem, sau, i = [], 0, 0, 0
    while i < len(nd):
        c = nd[i]
        if c in "([<":
            sau += 1
        elif c in ")]>":
            sau = max(0, sau - 1)
        elif sau == 0 and nd.startswith(dau, i):
            manh.append(nd[dem:i])
            dem = i + len(dau)
            i = dem
            continue
        i += 1
    manh.append(nd[dem:])
    return [m.strip() for m in manh if m.strip()]


def _gach_dau_dong(nd: str, tach: bool = True) -> str:
    """Chuỗi liệt kê « · » / «; » → danh sách gạch đầu dòng, MỖI Ý VIẾT HOA ĐẦU.

    Không áp cho trường Nguồn (dòng trích dẫn chuẩn phải liền mạch)."""
    if tach:
        for dau in (" · ", "; "):
            manh = _tach_ngoai_ngoac(nd, dau)
            if len(manh) >= 3:
                return ("<ul class='gach'>"
                        + "".join(f"<li>{_hoa_dau(m)}</li>" for m in manh) + "</ul>")
    return _hoa_dau(nd)


# Giải nghĩa CHO THỰC HÀNH LÂM SÀNG — nội dung giáo khoa chuẩn, ngắn; mỗi chỉ số
# trong văn bản thành link nhảy tới Phụ lục B (yêu cầu bác sĩ 17/08).
TU_DIEN_TK = {
    "RR": ("Risk Ratio — tỷ số nguy cơ",
           "Nguy cơ biến cố ở nhóm can thiệp chia cho nhóm chứng. RR 0,40 nghĩa là nguy cơ "
           "bằng 40% so với nhóm chứng (giảm tương đối 60%); RR > 1 là tăng nguy cơ; RR = 1 "
           "là không khác biệt. Cho thực hành: RR là con số TƯƠNG ĐỐI — cùng RR 0,40 nhưng "
           "nguy cơ nền 20% thì lợi ích tuyệt đối lớn (giảm 12 điểm phần trăm), nguy cơ nền "
           "0,2% thì lợi ích rất nhỏ; luôn hỏi thêm nguy cơ nền và NNT."),
    "HR": ("Hazard Ratio — tỷ số rủi ro tức thời",
           "Giống RR nhưng tính trên TOÀN THỜI GIAN theo dõi (phân tích sống còn): tốc độ "
           "xảy ra biến cố ở nhóm can thiệp so với nhóm chứng tại mỗi thời điểm. HR 0,82 ≈ "
           "giảm 18% tốc độ xảy ra biến cố. Cho thực hành: HR không cho biết TRÌ HOÃN được "
           "bao lâu hay bao nhiêu người thoát hẳn biến cố — nên xem kèm đường Kaplan–Meier "
           "và mốc thời gian cụ thể."),
    "OR": ("Odds Ratio — tỷ số chênh",
           "Tỷ số giữa odds (số ca có biến cố : số ca không) của hai nhóm. Khi biến cố HIẾM "
           "(<10%), OR xấp xỉ RR; khi biến cố phổ biến, OR luôn XA 1 hơn RR — dễ đọc thành "
           "phóng đại hiệu quả/tác hại. Cho thực hành: gặp OR với biến cố phổ biến, đừng "
           "đọc như «tăng/giảm X%» của nguy cơ."),
    "95% CI": ("Confidence Interval — khoảng tin cậy 95%",
           "Khoảng giá trị tương thích với dữ liệu: nếu lặp nghiên cứu nhiều lần, ~95% các "
           "khoảng như vậy chứa giá trị thật. Cho thực hành: đọc HAI ĐẦU khoảng — với "
           "RR/HR/OR, khoảng chứa 1 nghĩa là chưa loại trừ được «không khác biệt»; khoảng "
           "hẹp là ước lượng chính xác, khoảng rộng là dữ liệu còn mỏng dù p có «đẹp»."),
    "P": ("Trị số p",
           "Xác suất quan sát được kết quả cực đoan như vậy (hoặc hơn) NẾU thật sự không có "
           "khác biệt. p < 0,05 là quy ước, không phải ranh giới chân lý. Cho thực hành: p "
           "nhỏ không có nghĩa hiệu quả LỚN hay quan trọng lâm sàng — độ lớn hiệu quả nằm ở "
           "RR/HR/MD và khoảng tin cậy; nghiên cứu nhỏ không làm mù thì p nhỏ vẫn có thể do "
           "sai lệch."),
    "I²": ("I-squared — chỉ số không đồng nhất",
           "Phần trăm biến thiên giữa các nghiên cứu trong một phân tích gộp KHÔNG do ngẫu "
           "nhiên: ≤25% thấp, ~50% vừa, ≥75% cao. Cho thực hành: I² 90–99% nghĩa là các "
           "nghiên cứu nói những điều rất khác nhau — con số gộp gần như không dùng được "
           "như một ước lượng duy nhất; hãy đọc phân tích dưới nhóm và hỏi vì sao lệch."),
    "NNT": ("Number Needed to Treat — số cần điều trị",
           "Số bệnh nhân cần điều trị trong một khoảng thời gian để THÊM một người hưởng "
           "lợi (= 1/độ giảm nguy cơ tuyệt đối). Cho thực hành: NNT gắn với nguy cơ nền và "
           "thời gian — NNT 20/5 năm rất khác NNT 20/6 tuần; so sánh NNT với NNH để cân "
           "lợi–hại cho từng bệnh nhân."),
    "NNH": ("Number Needed to Harm — số gây thêm một ca hại",
           "Số bệnh nhân điều trị để THÊM một người gặp tác hại. NNH càng nhỏ càng đáng "
           "ngại. Cho thực hành: đặt NNT cạnh NNH cùng khung thời gian; bệnh nhân nguy cơ "
           "nền thấp thì NNT phình to trong khi NNH thường giữ nguyên — cán cân đổi chiều."),
    "MD": ("Mean Difference — hiệu số trung bình",
           "Chênh lệch trung bình giữa hai nhóm trên cùng một thang đo gốc (mmHg, điểm "
           "VAS…). Cho thực hành: so hiệu số với NGƯỠNG CÓ Ý NGHĨA LÂM SÀNG (MCID) của "
           "thang — giảm 3/100 điểm có thể «có ý nghĩa thống kê» mà bệnh nhân không cảm "
           "nhận được."),
    "SMD": ("Standardized Mean Difference — hiệu số chuẩn hoá",
           "Hiệu số trung bình chia cho độ lệch chuẩn — dùng khi các nghiên cứu đo bằng "
           "thang khác nhau. Quy ước thô: 0,2 nhỏ · 0,5 vừa · 0,8 lớn. Cho thực hành: SMD "
           "khó dịch ngược ra đơn vị lâm sàng; muốn tư vấn cụ thể phải quy về thang gốc."),
    "RD": ("Risk Difference — hiệu số nguy cơ tuyệt đối",
           "Nguy cơ nhóm can thiệp trừ nhóm chứng, tính bằng điểm phần trăm — chính là con "
           "số làm nền cho NNT (NNT = 1/RD). Cho thực hành: đây là con số dễ tư vấn nhất "
           "cho bệnh nhân («trong 100 người như ông/bà, thêm X người tránh được biến cố»)."),
    "AUC": ("Area Under the Curve — diện tích dưới đường cong ROC",
           "Khả năng phân biệt của một test/mô hình: 0,5 = tung đồng xu, 1,0 = hoàn hảo; "
           "≥0,8 thường coi là tốt. Cho thực hành: AUC không nói tại NGƯỠNG CẮT nào nên "
           "dùng — quyết định lâm sàng cần độ nhạy/độ đặc hiệu tại ngưỡng cụ thể."),
}


_TK_DEM = [0]  # id duy nhất cho từng cặp label/checkbox trong MỘT lần dựng


def _lk_thong_ke(doan: str) -> str:
    """Chỉ số thống kê → bấm BUNG giải nghĩa tại chỗ bằng label+checkbox ẩn
    (thuần HTML/CSS, không JS). KHÔNG dùng <details>: nhiều engine ép nó xuống
    dòng dù display:inline — chính là lỗi «câu vỡ giữa ngoặc» bác sĩ chụp 17/08."""
    def _bung(ten_hien, khoa):
        ten, giai = TU_DIEN_TK[khoa]
        giai = _ha_caps_nhan_manh(giai)
        cau_dau = giai.split(". ")[0] + "."
        thuc_hanh = ""
        mth = re.search(r"Cho thực hành:([^—]*?)(?:\.\s*$|\.$|$)", giai)
        if mth:
            thuc_hanh = f" <b>Cho thực hành:</b>{mth.group(1)}."
        _TK_DEM[0] += 1
        i = _TK_DEM[0]
        return (f'<label class="tkx" for="tk-{i}">{ten_hien}</label>'
                f'<input type="checkbox" id="tk-{i}" class="tkx-c">'
                f'<span class="giai"><b>{khoa}</b> · <i>{ten}</i> — {cau_dau}'
                f'{thuc_hanh} <span class="mo">(đầy đủ: Phụ lục B)</span></span>')

    manh = re.split(r"(<[^>]+>)", doan)
    for i, m in enumerate(manh):
        if m.startswith("<"):
            continue
        m = re.sub(r"(?<![\w-])(95%\s?CI)(?![\w])", lambda x: _bung(x.group(1), "95% CI"), m)
        m = re.sub(r"(?<![\w-])(RR|HR|OR|NNT|NNH|SMD|MD|RD|AUC)(?=\s*(?:[=:]|gộp|\d|<b>))",
                   lambda x: _bung(x.group(1), x.group(1)), m)
        m = re.sub(r"(?<![\wà-ỹ])([pP])(?=\s*[<=>≤≥])", lambda x: _bung(x.group(1), "P"), m)
        m = re.sub(r"(I²|I2)(?=\s*[=≈<>≥\d])", lambda x: _bung("I²", "I²"), m)
        manh[i] = m
    return "".join(manh)


def _phu_luc_thong_ke() -> str:
    khoa = {"95% CI": "95-ci", "I²": "i2", "P": "p"}
    muc = []
    for k, (ten, giai) in TU_DIEN_TK.items():
        mid = khoa.get(k, k.lower())
        muc.append(f'<div class="dn" id="tk-{mid}"><b>{k}</b> · <i>{ten}</i>'
                   f'<p>{_ha_caps_nhan_manh(giai)}</p></div>')
    return ('<section id="phu-luc-b"><div class="dau-muc"><h2 class="muc">'
            '<span class="so">VI.</span>Phụ lục B — Giải nghĩa chỉ số thống kê '
            'cho thực hành</h2></div>'
            '<p class="mo">Bấm vào chỉ số gạch chấm trong văn bản để bung giải nghĩa ngắn tại chỗ; '
            'bảng dưới đây là bản đầy đủ.</p>' + "".join(muc) + "</section>")


def _hang(nhan: str, noi_dung: str, lop: str = "") -> str:
    return (f'<tr class="{lop}"><th scope="row">{nhan}</th>'
            f'<td>{noi_dung}</td></tr>')


def render_the(khoi: str) -> str:
    """Một thẻ 6-trường → card học thuật."""
    dong = [d for d in khoi.strip().splitlines() if d.strip()]
    m = re.match(r"\*\*\[([\w-]+)\]\s*(.+?)\s*—\s*(Áp dụng ngay|Cân nhắc|Chưa đủ)\s*(\([^)]*\))?\s*\*?\*?$",
                 dong[0].strip())
    if not m:
        return f"<p>{_inline(dong[0])}</p>" + "".join(f"<p>{_inline(d)}</p>" for d in dong[1:])
    ma, tieu_de, de_xuat, ly_do = m.group(1), m.group(2), m.group(3), (m.group(4) or "")
    lop, mau_chu, mau_nen = MAU_DE_XUAT[de_xuat]
    truong: dict[str, str] = {}
    phu: list[str] = []
    for d in dong[1:]:
        mm = re.match(r"(Điều gì thay đổi|Nguồn|Hiệu số như nguồn báo cáo|Ai bị ảnh hưởng|Rủi ro nếu áp dụng sai|Thẩm định toàn văn)\s*:\s*(.*)", d.strip())
        if mm:
            truong[mm.group(1)] = mm.group(2)
        else:
            phu.append(d.strip())
    than = []
    if "Điều gì thay đổi" in truong:
        than.append(_hang("Điều gì thay đổi", _lk_thong_ke(_gach_dau_dong(_inline(truong["Điều gì thay đổi"])))))
    if "Nguồn" in truong:
        than.append(_hang("Nguồn", f'<span class="nguon">{_hoa_dau(_inline(truong["Nguồn"]))}</span>'))
    if "Hiệu số như nguồn báo cáo" in truong:
        than.append(_hang("Hiệu số<div class='chu-thich'>như nguồn báo cáo</div>",
                          f'<div class="hieu-so">{_lk_thong_ke(_gach_dau_dong(_inline(truong["Hiệu số như nguồn báo cáo"])))}</div>'))
    if "Thẩm định toàn văn" in truong:
        than.append(_hang("Thẩm định toàn văn",
                          _lk_thong_ke(_gach_dau_dong(_inline(truong["Thẩm định toàn văn"])))))
    if "Ai bị ảnh hưởng" in truong:
        than.append(_hang("Ai bị ảnh hưởng", _gach_dau_dong(_inline(truong["Ai bị ảnh hưởng"]))))
    if "Rủi ro nếu áp dụng sai" in truong:
        ve = re.split(r"\s*\|\s*[Nn]ếu bỏ qua\s*:\s*", truong["Rủi ro nếu áp dụng sai"], maxsplit=1)
        rr = f'<div class="rui-ro"><b>Nếu áp dụng sai:</b> {_inline(ve[0])}</div>'
        if len(ve) > 1:
            rr += f'<div class="rui-ro bo-qua"><b>Nếu bỏ qua:</b> {_inline(ve[1])}</div>'
        than.append(_hang("Rủi ro", rr, "hang-rui-ro"))
    chan = "".join(f'<div class="ghi-chu-tham-dinh">{_hoa_dau(_inline(p))}</div>' for p in phu)
    return f"""<article class="the {lop}">
  <header><span class="ma">{ma}</span>
    <h3>{_hoa_dau(_inline(tieu_de))}</h3>
    <span class="badge">{de_xuat}{_ha_caps_nhan_manh(html.escape(" " + ly_do)) if ly_do else ""}</span>
  </header>
  <table class="truong">{"".join(than)}</table>{chan}
</article>"""


def render_goi_tuan(md: str) -> str:
    """Gói tuần → phần mở + dãy card + phần kết."""
    # cắt theo ranh thẻ **[Wxx-yy]
    manh = re.split(r"(?=^\*\*\[[\w-]+\])", md, flags=re.M)
    mo_dau, the_html, ket = [], [], []
    for i, kh in enumerate(manh):
        if re.match(r"^\*\*\[[\w-]+\]", kh.strip()):
            # phần sau thẻ cuối có thể chứa cả đoạn kết — tách tại dòng '---' hoặc '**Đã quét'
            cat = re.split(r"^(?=---$|\*\*Đã quét)", kh, flags=re.M, maxsplit=1)
            the_html.append(render_the(cat[0]))
            if len(cat) > 1:
                ket.append(cat[1])
        elif not the_html:
            mo_dau.append(kh)
        else:
            ket.append(kh)

    def md_don_gian(t: str) -> str:
        ra = []
        dau_bang = True
        for d in t.splitlines():
            if not d.startswith("|"):
                dau_bang = True
            d = re.sub(r"^(#{1,4} )[⓿①②③④⑤⑥⑦⑧⑨⑩🔴🟠🟡🟢📋📊🧭⚠️\s]+", r"\1", d)
            s = _inline(d)
            if d.startswith("### "):
                ra.append(f"<h4>{s[4:]}</h4>")
            elif d.startswith("## "):
                ra.append(f"<h3>{s[3:]}</h3>")
            elif d.startswith("# "):
                ra.append(f"<h2>{s[2:]}</h2>")
            elif d.strip() == "---":
                ra.append("<hr>")
            elif d.startswith("|"):
                o = [x.strip() for x in d.strip("|").split("|")]
                if set("".join(o)) <= set("-: "):
                    dau_bang = False  # hàng kẻ ngăn header — hàng kế là thân
                    continue
                the_o = "th" if dau_bang else "td"
                ra.append("<tr>" + "".join(f"<{the_o}>{_hoa_dau(_inline(x))}</{the_o}>" for x in o) + "</tr>")
            elif d.startswith("- ") or d.startswith("• "):
                ra.append(f"<div class='li'>– {_hoa_dau(s[2:])}</div>")
            elif d.strip():
                ra.append(f"<p>{_hoa_dau(s)}</p>")
        t2 = "\n".join(ra)
        t2 = re.sub(r"((?:<tr>.*?</tr>\n?)+)", r"<table>\1</table>", t2, flags=re.S)
        return t2

    # Văn phong học thuật: CHỨNG CỨ đứng trước; khối vận hành (bảng tự-đề-xuất,
    # thống kê quét, chi tiết máy móc) dồn về «Phụ lục A» cuối mục.
    phu_luc = md_don_gian("".join(mo_dau)) + md_don_gian("".join(ket))
    return ("".join(the_html)
            + (f'<div class="phu-luc"><h4 class="tieu-de-phu-luc">Phụ lục A — Vận hành, '
               f'độ phủ và việc tồn đọng</h4>{phu_luc}</div>' if phu_luc.strip() else ""))


def main() -> int:
    hom_nay = dt.datetime.now()
    khoi: list[str] = []

    goi = sorted((REPO / "queue").glob("tuan-*.md"))
    if goi:
        g = goi[-1]
        tuoi = (hom_nay.date() - dt.date.fromtimestamp(g.stat().st_mtime)).days
        khoi.append(f"<section class='goi'><div class='dau-muc'><h2 class='muc'><span class='so'>I.</span>Gói duyệt tuần — {g.stem.replace('tuan-', '').upper()}</h2>"
                    f"<p class='mo'>{'Sinh hôm nay' if tuoi == 0 else f'Sinh {tuoi} ngày trước'} bởi chu trình giám sát tự động · mọi thẻ là <b>đề xuất</b> chờ bác sĩ phản bác</p></div>"
                    + render_goi_tuan(g.read_text(encoding="utf-8", errors="replace"))
                    + "</section>")

    # ── II. Cảnh báo: lâm sàng hiện gọn (ngày · một câu · liên kết);
    #    ghi chú KỸ THUẬT/vận hành xếp vào <details> — không đổ nhật ký nguyên
    #    văn vào trang bác sĩ (bị chê đích đáng 17/08).
    KY_THUAT = re.compile(r"python3|venv|logger|BH\d\d|retraction_chain|tools/|\.py\b|/Users/|exit|mã thoát", re.I)

    def _rut_duong_dan(s: str) -> str:
        s = re.sub(r"/Users/[^ ]*?/Claude AI/([^ ]+)", lambda m: f"<a href='{m.group(1)}'>{m.group(1).split('/')[-1]}</a>", s)
        return s

    lam_sang, ky_thuat = [], []
    for f in sorted((REPO / "alerts").glob("*.md"), reverse=True):
        if (hom_nay.date() - dt.date.fromtimestamp(f.stat().st_mtime)).days > 14:
            continue
        for dong_cb in f.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"#\s*CẢNH BÁO KHẨN\s*—\s*([\d-]+)\s*-\s*[🔴🟠🟡⚠️\s]*(.+)", dong_cb.strip())
            if not m:
                continue
            ngay_cb, than = m.group(1), m.group(2).strip()
            ve = re.split(r"\s+—\s+", than, maxsplit=1)
            tieu_de_cb = _hoa_dau(_inline(ve[0].strip().rstrip(".")))
            chi_tiet = _hoa_dau(_rut_duong_dan(_inline(ve[1].strip()))) if len(ve) > 1 else ""
            if KY_THUAT.search(than):
                ky_thuat.append(f"<li><span class='mo'>{ngay_cb}</span> — {tieu_de_cb}."
                                f"<details><summary>Chi tiết kỹ thuật</summary><p>{chi_tiet}</p></details></li>")
            else:
                lam_sang.append(f"<li><span class='mo'>{ngay_cb}</span> — {tieu_de_cb}."
                                + (f" {chi_tiet}" if len(chi_tiet) < 300 else
                                   f"<details><summary>Chi tiết</summary><p>{chi_tiet}</p></details>") + "</li>")
    if lam_sang or ky_thuat:
        phan = ""
        if lam_sang:
            phan += "<ul class='gach'>" + "".join(lam_sang) + "</ul>"
        else:
            phan += "<p class='mo'>Không có cảnh báo lâm sàng nào trong 14 ngày.</p>"
        if ky_thuat:
            phan += ("<details class='van-hanh'><summary>Ghi chú vận hành — dành cho phiên kỹ thuật"
                     f" ({len(ky_thuat)})</summary><ul class='gach'>" + "".join(ky_thuat) + "</ul></details>")
        khoi.append("<section><div class='dau-muc'><h2 class='muc'><span class='so'>II.</span>Cảnh báo trong 14 ngày</h2></div>"
                    + phan + "</section>")

    ban_doc = []
    der = REPO / "EBM-Dashboards" / "derivatives"
    for f in sorted(der.glob("*_ban-doc.html"), key=lambda x: -x.stat().st_mtime):
        if (hom_nay.date() - dt.date.fromtimestamp(f.stat().st_mtime)).days <= 7:
            ten = f.name.replace("_ban-doc.html", "").replace("_", " ")
            ban_doc.append(f"<a class='o-doc' href='EBM-Dashboards/derivatives/{f.name}'>"
                           f"<span>📖</span><span>{html.escape(ten)}</span>"
                           f"<span class='mo'>{dt.date.fromtimestamp(f.stat().st_mtime):%d/%m}</span></a>")
    if ban_doc:
        khoi.append(f"<section><div class='dau-muc'><h2 class='muc'><span class='so'>III.</span>Bản đọc cập nhật trong 7 ngày ({len(ban_doc)})</h2></div>"
                    "<p class='mo'>Bấm mở thẳng — cờ đỏ và việc-cần-làm đứng trước, chứng cứ xếp sau trên một trục.</p>"
                    f"<div class='luoi-doc'>{''.join(ban_doc)}</div></section>")

    try:
        r = subprocess.run([sys.executable, "tools/tu_de_xuat_viec.py", "--gon"],
                           capture_output=True, text=True, timeout=300, cwd=REPO)
        loc, giu = [], False
        for ln in (r.stdout or "").splitlines():
            if "👤" in ln:
                loc.append(f"<div class='li'>{_inline(ln.strip())}</div>")
                giu = True
            elif giu and "→" in ln:
                loc.append(f"<div class='li lenh'>{_inline(ln.strip())}</div>")
                giu = False
            else:
                giu = False
        if loc:
            khoi.append("<section><div class='dau-muc'><h2 class='muc'><span class='so'>IV.</span>Việc chờ bác sĩ</h2></div>"
                        + "\n".join(loc) + "</section>")
    except (OSError, subprocess.SubprocessError):
        pass

    uv = REPO / "EBM-Dashboards" / "surveillance" / "ung-vien-ngoai-quet.jsonl"
    if uv.exists():
        con = [json.loads(x) for x in uv.read_text(encoding="utf-8").splitlines()
               if x.strip() and "CANDIDATE" in x]
        if con:
            dong = [f"<div class='li'>{_inline('PMID ' + c['pmid'])} — {_hoa_dau(html.escape(c['title'][:110]))} "
                    f"<span class='mo'>({html.escape(c.get('nguon_phat_hien', ''))})</span></div>"
                    for c in con]
            khoi.append("<section><div class='dau-muc'><h2 class='muc'><span class='so'>V.</span>Ứng viên ngoài vòng quét còn chờ</h2></div>"
                        + "\n".join(dong) + "</section>")

    RA.write_text(f"""<!DOCTYPE html>
<html lang="vi"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hòm thư Bác sĩ — EBM</title>
<style>
  :root{{--ink:#1a1a1a;--ink2:#333;--muted:#6b6257;--line:#d9d2c7;--line2:#efe9df;
        --nen:#fdfcf9;--giay:#fffefb;--link:#1a4d8f;
        --apply:#1d6b3a;--consider:#8a6d1a;--notyet:#a34a1f;--danger:#8f1d1d}}
  *{{box-sizing:border-box}}
  body{{font-family:'Times New Roman',Times,'Liberation Serif',serif;
       max-width:820px;margin:0 auto;padding:36px 28px 80px;background:var(--nen);
       color:var(--ink);line-height:1.65;font-size:16px}}
  /* ── NHỊP DỌC THỐNG NHẤT (v10 — «hàng cách hàng lúc rộng lúc hẹp») ── */
  p{{margin:7px 0}}
  section p:first-child{{margin-top:0}} section p:last-child{{margin-bottom:0}}
  .li{{margin:0;padding:3.5px 0}}
  ul.gach{{margin:3px 0!important}}
  ul.gach li{{padding:3.5px 0 3.5px 1.15em!important;margin:0!important}}
  table.truong th,table.truong td{{padding-top:8px!important;padding-bottom:8px!important}}
  .hieu-so{{margin:2px 0;padding:9px 14px!important}}
  .hieu-so ul.gach li{{padding:3px 0 3px 1.15em!important}}
  h3{{margin:10px 0 5px}} h4{{margin:12px 0 5px}}
  .ghi-chu-tham-dinh{{margin-top:8px!important;padding-top:6px!important}}
  .dn{{padding:9px 12px!important}} .dn p{{margin:4px 0 0!important}}
  table:not(.truong) th,table:not(.truong) td{{padding-top:7px!important;padding-bottom:7px!important}}

  h1{{font-size:1.7rem;font-weight:700;margin:0;text-align:center;letter-spacing:.01em}}
  .phu-de{{text-align:center;color:var(--muted);font-style:italic;font-size:.95rem;
          margin:6px 0 0}}
  .mang-set{{border-top:3px double var(--line);border-bottom:1px solid var(--line);
            margin:18px 0 30px;padding:0}}
  h2.muc{{font-size:.98rem;font-weight:700;letter-spacing:.16em;margin:0 0 4px;
         text-transform:uppercase}}
  h2.muc .so{{color:var(--muted);margin-right:10px}}
  h3{{font-size:1.05rem;margin:.2em 0}} h4{{font-size:1rem;margin:14px 0 4px}}
  section{{background:var(--giay);border:1px solid var(--line2);
          padding:26px 30px;margin:22px 0}}
  .tag{{display:none}}
  .dau-muc{{border-bottom:1px solid var(--line);padding-bottom:8px;margin-bottom:16px}}
  .dau-muc .mo{{font-style:italic}}
  /* ── thẻ chứng cứ: mục học thuật đánh số ── */
  .the{{margin:28px 0 32px;border:none;padding:0}}
  .the header{{display:block;margin-bottom:10px}}
  .the .ma{{font-size:.8rem;letter-spacing:.08em;color:var(--muted)}}
  .the h3{{font-size:1.12rem;font-weight:700;line-height:1.5;margin:3px 0 2px}}
  .badge{{font-size:.85rem;font-weight:700;letter-spacing:.02em;
         background:none!important;padding:0}}
  .the.apply .badge{{color:var(--apply)}} .the.consider .badge{{color:var(--consider)}}
  .the.notyet .badge{{color:var(--notyet)}}
  .badge::before{{content:"— "}}
  /* bảng trường CÂN ĐỐI: cột nhãn cố định, nhãn MỘT dòng, không small-caps */
  table.truong{{width:100%;border-collapse:collapse;margin:6px 0 0;table-layout:fixed}}
  table.truong th{{width:172px;text-align:left;vertical-align:top;
        font-size:.86rem;font-weight:700;color:var(--muted);
        padding:9px 14px 9px 0;border-top:1px solid var(--line2);white-space:nowrap}}
  table.truong th .chu-thich{{font-weight:400;font-style:italic;font-size:.8rem;
        white-space:normal;line-height:1.3}}
  table.truong td{{vertical-align:top;padding:9px 0;border-top:1px solid var(--line2);
        font-size:1rem;color:var(--ink2);border-bottom:none}}
  table.truong tr:first-child th,table.truong tr:first-child td{{border-top:1px solid var(--line)}}
  a{{color:var(--link)}} a.id{{color:var(--link);text-decoration:none;border-bottom:1px dotted}}
  code{{font-family:'Times New Roman',Times,serif;font-style:italic;background:none;padding:0}}
  hr{{border:none;border-top:1px solid var(--line2);margin:18px 0}}
  table{{border-collapse:collapse;margin:12px 0;font-size:.92rem;width:100%}}
  table:not(.truong){{table-layout:auto}}
  table:not(.truong) th{{text-align:left;font-size:.85rem;padding:6px 12px;
     border-bottom:2px solid var(--line);white-space:nowrap;font-weight:700}}
  table:not(.truong) td{{border-top:1px solid var(--line2);
     padding:7px 12px;vertical-align:top;font-size:.92rem}}
  table:not(.truong) td:first-child,table:not(.truong) th:first-child{{
     width:3.2em;text-align:center;padding-left:4px;padding-right:4px}}
  table:not(.truong) td:nth-child(2),table:not(.truong) th:nth-child(2){{white-space:nowrap}}
  table:not(.truong) td:last-child{{min-width:150px}}
  .cham{{font-size:.8em;vertical-align:middle}}
  .cham.do{{color:var(--danger)}} .cham.cam{{color:var(--notyet)}}
  .cham.vang{{color:var(--consider)}} .cham.xanh{{color:var(--apply)}}
  .vai{{font-style:italic;color:var(--ink2)}}
  ul.gach{{list-style:none;margin:2px 0;padding:0}}
  ul.gach li{{padding:2px 0 2px 1.15em;text-indent:-1.15em;margin:0}}
  ul.gach li::before{{content:"–  ";color:var(--muted)}}
  ul.gach li.bo-qua{{color:var(--muted)}}
  details{{margin:4px 0}} details summary{{cursor:pointer;color:var(--link);
     font-size:.9rem;font-style:italic}}
  details p{{font-size:.9rem;color:var(--ink2);margin:6px 0 2px 1em}}
  details.van-hanh{{margin-top:14px;border-top:1px dotted var(--line);padding-top:8px}}
  details.van-hanh summary{{color:var(--muted)}}
  label.tkx{{cursor:pointer;border-bottom:1px dotted var(--muted)}}
  input.tkx-c{{position:absolute;opacity:0;width:0;height:0;margin:0}}
  span.giai{{display:none}}
  input.tkx-c:checked + span.giai{{display:block;margin:6px 0;padding:9px 13px;
     background:#f6f3ea;border-left:3px solid var(--consider);font-size:.9rem;
     line-height:1.55;font-variant-numeric:normal;text-indent:0;font-weight:400;
     font-style:normal}}
  .dn{{padding:10px 12px;border-top:1px solid var(--line2)}}
  .dn b{{font-size:1.02rem}} .dn i{{color:var(--muted)}}
  .dn p{{margin:4px 0 0;font-size:.95rem;color:var(--ink2)}}
  .dn:target{{background:#fdf6dd;border-left:3px solid var(--consider);
     padding-left:14px;scroll-margin-top:20px}}
  .phu-luc{{margin-top:34px;padding-top:14px;border-top:3px double var(--line)}}
  .tieu-de-phu-luc{{font-size:.95rem;letter-spacing:.05em;text-transform:uppercase;
     color:var(--muted);margin:0 0 8px}}
  .phu-luc p,.phu-luc .li{{font-size:.92rem;color:var(--ink2)}}
  .li{{margin:5px 0}} .li.lenh{{color:var(--muted);font-size:.9rem;margin-left:22px;font-style:italic}}
  .mo{{color:var(--muted);font-size:.9rem}}
  .mo-dau p,.ket-goi p{{font-size:.95rem;color:var(--ink2)}}
  .luoi-doc{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:4px 26px}}
  .o-doc{{display:flex;gap:9px;align-items:baseline;padding:5px 0;text-decoration:none;
         color:var(--ink2);font-size:.95rem;border-bottom:1px dotted var(--line2)}}
  .o-doc:hover{{color:var(--link)}}
  .o-doc .mo{{margin-left:auto;white-space:nowrap;font-variant-numeric:tabular-nums}}
  .chan{{color:var(--muted);font-size:.85rem;margin-top:30px;border-top:3px double var(--line);
        padding-top:12px;text-align:center;font-style:italic}}
  @media (max-width:600px){{table.truong,table.truong tr,table.truong th,table.truong td{{display:block;width:100%}}
    table.truong th{{border-top:1px solid var(--line2);padding:8px 0 0;white-space:normal}}
    table.truong td{{border-top:none;padding:2px 0 9px}}}}
  @media print{{body{{background:#fff;font-size:12.5pt;padding:0}}
    section{{border:none;padding:0 0 18px;margin:0 0 14px}}
    .o-doc{{border:none}} a{{color:var(--ink)}}}}
</style></head><body>
<h1>Hòm thư Bác sĩ</h1>
<p class="phu-de">Bản tin chứng cứ định kỳ · hệ EBM ngoại trú · dựng {hom_nay:%d/%m/%Y %H:%M}</p>
<div class="mang-set"></div>
{"".join(khoi)}
{_phu_luc_thong_ke()}
<p class="chan">Mọi thẻ dừng ở CANDIDATE — đề xuất để bác sĩ phản bác, quyết định áp dụng
thuộc Cổng A/B của bác sĩ. Cần bác sĩ kiểm chứng trước khi áp dụng cho người bệnh cụ thể.</p>
</body></html>""", encoding="utf-8", newline="\n")
    print(f"✓ {RA.name} — {len(khoi)} khối")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
