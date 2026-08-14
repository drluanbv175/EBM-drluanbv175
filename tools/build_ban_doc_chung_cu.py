#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sinh BẢN ĐỌC sau cập nhật chứng cứ từ một Web Dashboard lâm sàng.

Bản đọc là trang HTML độc lập để bác sĩ đọc NGAY sau khi chạy xong dây chuyền cập
nhật chứng cứ: việc cần làm và cờ đỏ đứng trước, chứng cứ đặt trên MỘT trục thang
log dùng chung (vạch 1,0 ở giữa — trái là có lợi, phải là bất lợi).

Khác dashboard (công cụ tra cứu, lọc theo mặt) và khác bản Word (tài liệu lưu trữ
đầy đủ): bản đọc CHỈ giữ phần đổi được thực hành.

Cách dùng:
    python3 tools/build_ban_doc_chung_cu.py <dashboard>.html [-o <đầu ra>.html]

Mặc định ghi vào EBM-Dashboards/derivatives/<mã>_ban-doc.html

QUY ƯỚC TRÌNH BÀY (chuẩn cho tài liệu cập nhật chứng cứ khoa học — bác sĩ chốt 2026-08-05):
  - Font mặc định TIMES NEW ROMAN cho toàn trang, đồng bộ với bản Word xuất kèm.
  - ĐỀ MỤC (mục 1…5) IN HOA và IN ĐẬM. Tiêu đề khối con in đậm, không in hoa —
    giữ đúng bậc dưới đề mục. Tiêu đề trang in đậm, không in hoa vì câu quá dài.
  - Trong VĂN XUÔI thì viết hoa theo câu: KHÔNG dùng VIẾT HOA TOÀN BỘ để nhấn mạnh
    (nhấn mạnh bằng độ đậm và màu). Giữ nguyên viết hoa cho tên riêng, tên thử
    nghiệm (PARADIGM-HF), tên tổ chức (ESC) và đơn vị đo.
  - Tên thuốc gốc viết thường (empagliflozin), tên thử nghiệm viết hoa.
  - Số thập phân dùng dấu phẩy theo chuẩn tiếng Việt (0,79).
  - Nhãn trục được lọc theo khoảng cách thật để KHÔNG bao giờ chồng chữ, xem
    LogAxis.MIN_TICK_GAP.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

# Windows: stdout mặc định là cp1252 → mọi print() tiếng Việt hoặc ký hiệu (✓ ⚠ →)
# ném UnicodeEncodeError và GIẾT tiến trình, thường SAU KHI công việc đã xong. Đo thật
# ngày 12/08/2026 trên dây chuyền cập nhật chứng cứ: bản Word 82 KB đã ghi ra đĩa nhưng
# tool thoát mã 1 ở đúng dòng print cuối ⇒ caller đọc mã thoát, tưởng hỏng, bỏ luôn 2
# bước sau. Cùng lớp lỗi đã vá cho tools/vietnamize/.
import sys as _sys_utf8
for _s in (_sys_utf8.stdout, _sys_utf8.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass


ROOT = Path(__file__).resolve().parent.parent
DERIV = ROOT / "EBM-Dashboards" / "derivatives"


def configure_utf8_stdio() -> None:
    """Ép UTF-8 cho stdout — Windows mặc định cp1252 làm chết script khi in tiếng Việt."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


# ───────────────────────── đọc khối DATA của dashboard ─────────────────────────

def _balanced(src: str, start: int, opener: str, closer: str) -> str:
    """Cắt đoạn cân bằng ngoặc, có nhận biết chuỗi (tránh vỡ vì '[CẦN…]' trong text)."""
    depth = 0
    instr = False
    esc = False
    for i in range(start, len(src)):
        c = src[i]
        if instr:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == instr:
                instr = False
            continue
        if c in "\"'":
            instr = c
        elif c == opener:
            depth += 1
        elif c == closer:
            depth -= 1
            if depth == 0:
                return src[start:i + 1]
    raise ValueError("Không tìm được ngoặc đóng cân bằng")


def extract_data(html: str) -> dict:
    """Lấy khối `const DATA = {...}` và nạp thành dict.

    Dashboard sinh bằng generator dùng khoá KHÔNG nháy (cú pháp JS), nên phải bọc
    lại nháy cho tên khoá trước khi json.loads.
    """
    i = html.find("const DATA")
    if i == -1:
        raise SystemExit("✗ Không tìm thấy khối `const DATA` — đây có phải dashboard không?")
    brace = html.index("{", i)
    raw = _balanced(html, brace, "{", "}")
    try:
        return json.loads(_quote_keys(raw))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"✗ Không đọc được khối DATA: {exc}")


def _quote_keys(src: str) -> str:
    """Bọc nháy cho TÊN KHOÁ chưa có nháy, chỉ ở NGOÀI chuỗi.

    Không dùng regex trên cả khối được: dấu hai chấm xuất hiện đầy trong nội dung
    tiếng Việt ("Chẩn đoán theo trình tự: lâm sàng…") nên regex sẽ bọc nhầm giữa
    câu và phá vỡ JSON. Vì vậy quét từng ký tự, bỏ qua phần nằm trong chuỗi.
    """
    out: list[str] = []
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if c in "\"'":
            value, i = _read_js_string(src, i)
            # Nối chuỗi kiểu JS: "phần đầu " + "phần sau" — JSON không có phép cộng,
            # nên phải gộp ngay tại đây thành một chuỗi duy nhất.
            while True:
                j = i
                while j < n and src[j] in " \t\r\n":
                    j += 1
                if j < n and src[j] == "+":
                    k = j + 1
                    while k < n and src[k] in " \t\r\n":
                        k += 1
                    if k < n and src[k] in "\"'":
                        more, i = _read_js_string(src, k)
                        value += more
                        continue
                break
            # json.dumps lo hết: thoát nháy kép, xuống dòng thật, tab, ký tự điều khiển
            out.append(json.dumps(value, ensure_ascii=False))
            continue
        # Bỏ chú thích JS — JSON không chấp nhận
        if c == "/" and i + 1 < n and src[i + 1] == "/":
            i = src.find("\n", i)
            if i == -1:
                break
            continue
        if c == "/" and i + 1 < n and src[i + 1] == "*":
            end = src.find("*/", i + 2)
            i = (end + 2) if end != -1 else n
            continue
        # Dấu phẩy thừa trước } hoặc ] — JS cho phép, JSON thì không
        if c in "}]":
            while out and out[-1].strip() == "":
                out.pop()
            if out and out[-1].endswith(","):
                out[-1] = out[-1][:-1]
            out.append(c)
            i += 1
            continue
        m = re.match(r"([A-Za-z_$][A-Za-z0-9_$]*)(\s*):", src[i:])
        if m and (not out or out[-1].strip("\n\r\t ") in ("{", ",", "")):
            out.append(f'"{m.group(1)}"{m.group(2)}:')
            i += m.end()
            continue
        out.append(c)
        i += 1
    return "".join(out)


_JS_ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f",
               "\\": "\\", "'": "'", '"': '"', "/": "/", "\n": ""}


def _read_js_string(src: str, start: int) -> tuple[str, int]:
    """Đọc TRỌN một chuỗi JS (nháy đơn hoặc kép) và trả về GIÁ TRỊ thật của nó.

    Phải giải mã tận nơi thay vì đổi nháy đơn thành nháy kép: chuỗi nháy đơn của JS
    có thể chứa nháy kép chưa thoát, và khối DATA đôi khi có ký tự xuống dòng thật
    bên trong chuỗi — cả hai đều làm vỡ JSON nếu chỉ thay ký tự bao ngoài.
    """
    quote = src[start]
    buf: list[str] = []
    i = start + 1
    while i < len(src):
        c = src[i]
        if c == "\\" and i + 1 < len(src):
            nxt = src[i + 1]
            if nxt == "u" and re.match(r"[0-9a-fA-F]{4}", src[i + 2:i + 6] or ""):
                buf.append(chr(int(src[i + 2:i + 6], 16)))
                i += 6
                continue
            buf.append(_JS_ESCAPES.get(nxt, nxt))
            i += 2
            continue
        if c == quote:
            return "".join(buf), i + 1
        buf.append(c)
        i += 1
    raise ValueError("Chuỗi JS không có nháy đóng")


# ───────────────────────────── trục thang log ─────────────────────────────

class LogAxis:
    """Trục thang log dùng CHUNG cho mọi chứng cứ trên trang.

    Dùng một trục duy nhất là có chủ ý: hai thang khác nhau trên cùng một trang
    khiến người đọc so sánh nhầm độ lớn hiệu quả.
    """

    def __init__(self, lo: float, hi: float):
        self.lo, self.hi = lo, hi
        self._span = math.log(hi) - math.log(lo)

    def pos(self, v: float) -> float:
        return (math.log(v) - math.log(self.lo)) / self._span * 100

    @classmethod
    def fit(cls, values: list[float]) -> "LogAxis":
        """Chọn biên bao trọn dữ liệu và luôn chứa vạch 1,0, chừa lề hai bên."""
        vals = [v for v in values if v and v > 0] or [0.7, 1.4]
        lo = min(min(vals), 0.95) * 0.92
        hi = max(max(vals), 1.05) * 1.08
        return cls(round(lo, 3), round(hi, 3))

    # Khoảng cách tối thiểu giữa hai nhãn trục, tính theo % bề ngang cột biểu đồ.
    # Nhãn kiểu "1,25" rộng ~30px, cột biểu đồ hẹp nhất ~300px → cần ~11%.
    MIN_TICK_GAP = 11.0

    def ticks(self) -> list[float]:
        """Chọn nhãn trục sao cho KHÔNG chồng nhau.

        Trục tự co giãn theo dữ liệu, nên khi có một khoảng tin cậy rất rộng (vd
        CASTLE-HTx 0,11–0,52) thì vùng quanh 1,0 bị nén lại và các nhãn 0,7 0,8 0,9
        đè lên nhau. Vì vậy phải lọc theo khoảng cách thực tế trên trục, và luôn
        giữ vạch 1,0 vì đó là mốc đọc chính.
        """
        cand = [0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,
                1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0]
        inside = [t for t in cand if self.lo * 1.02 <= t <= self.hi * 0.98]
        kept: list[float] = []
        if self.lo * 1.02 <= 1.0 <= self.hi * 0.98:
            kept.append(1.0)          # mốc 1,0 luôn được ưu tiên giữ
        for t in inside:
            if t == 1.0:
                continue
            if all(abs(self.pos(t) - self.pos(k)) >= self.MIN_TICK_GAP for k in kept):
                kept.append(t)
        return sorted(kept)


def vn_num(x: float) -> str:
    """Số thập phân theo chuẩn tiếng Việt: dấu phẩy."""
    return f"{x:.2f}".replace(".", ",")


# ───────────────────────────── dựng HTML ─────────────────────────────

def esc(t) -> str:
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# Từ viết tắt và tên thử nghiệm phải GIỮ NGUYÊN viết hoa. Danh sách này chỉ cần
# phủ các token TOÀN CHỮ HOA thuần ASCII; token có chữ thường lẫn vào (HFrEF) hay
# có gạch nối kèm số (REVIVED-BCIS2) đã được bảo vệ bằng luật riêng bên dưới.
PROTECTED = {
    "PCI", "ASV", "MRA", "TEER", "GDMT", "ARNI", "ARB", "CRT", "ICD", "LVEF",
    "NYHA", "BNP", "EF", "VN", "TSAT", "DOI", "PMID", "CI", "HR", "RR", "OR",
    "KCCQ", "SGLT2", "ATTR", "CM", "IV", "MCID", "AHA", "ACC", "ESC", "WHF",
    "HFSA", "EMA", "FDA", "WHO", "COPD", "CKD", "SPPB", "SpO", "GRADE",
    "TOPCAT", "IRONMAN", "SUMMIT", "VICTOR", "DELIVER", "COAPT", "TRILUMINATE",
    "ADVOR", "EMPULSE", "STRONG", "DIGIT", "SERVE", "CASTLE", "REVIVED",
    "PARAGON", "PARADIGM", "FINEARTS", "EMPEROR", "AFFIRM", "HEART", "FID",
}

_VN_DIACRITIC = re.compile(
    r"[ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢ"
    r"ÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ]")

# Từ tiếng Việt KHÔNG mang dấu — không nhận ra được bằng luật dấu ở trên, nên phải
# liệt kê. Chỉ gồm từ thực sự hay bị viết hoa để nhấn mạnh trong khối DATA.
VN_PLAIN = {"NHANH", "SOM", "MUON", "CAO", "THAP", "MOI", "RUNG", "TIM", "GAN",
            "THAN", "MAU", "NANG", "NHE", "DAI", "NGAN", "AN", "TOAN"}


def _is_vn_shout(tok: str) -> bool:
    core = tok.strip("().,;:—–")
    return bool(_VN_DIACRITIC.search(core)) or core in VN_PLAIN


def _is_protected(tok: str) -> bool:
    core = tok.strip("().,;:—–")
    if not core:
        return True
    if core in PROTECTED:
        return True
    if any(ch.islower() for ch in core):      # HFrEF, SGLT2i, HFpEF…
        return True
    if any(ch.isdigit() for ch in core):      # BCIS2, SGLT2…
        return True
    # Tên viết tắt/thử nghiệm có gạch nối, không mang dấu tiếng Việt: ATTR-CM, SERVE-HF
    if "-" in core and not _VN_DIACRITIC.search(core):
        return True
    return False


def normalize_title(text: str) -> str:
    """Đưa tiêu đề về VIẾT HOA THEO CÂU — chuẩn của tài liệu khoa học.

    Trong khối DATA của dashboard, người soạn hay dùng VIẾT HOA TOÀN BỘ để nhấn
    mạnh ("KHÔNG đạt kết cục chính", "phân suất tống máu BẢO TỒN"). Trên trang đọc,
    nhấn mạnh thuộc về độ đậm và màu, không phải viết hoa — nên hạ về chữ thường,
    NHƯNG giữ nguyên từ viết tắt và tên thử nghiệm.
    """
    text = re.sub(r"^[\s⚠️!*·—–-]+", "", str(text))          # bỏ ký hiệu cảnh báo dẫn đầu
    toks = text.split(" ")
    caps_run: list[int] = []

    def flush():
        # Chỉ hạ chữ khi trong cụm viết hoa có ít nhất một từ tiếng Việt
        if len(caps_run) >= 1 and any(_is_vn_shout(toks[i]) for i in caps_run):
            for i in caps_run:
                if not _is_protected(toks[i]):
                    toks[i] = toks[i].lower()
        caps_run.clear()

    for idx, tok in enumerate(toks):
        letters = [c for c in tok if c.isalpha()]
        if letters and all(c.isupper() for c in letters):
            caps_run.append(idx)
        else:
            flush()
    flush()

    out = " ".join(toks).strip()
    # Viết hoa chữ cái đầu câu — chỉ khi từ đầu là từ thường (không phải viết tắt).
    # Không dùng _is_protected ở đây: hàm đó coi mọi từ có chữ thường là "được bảo
    # vệ", nên sẽ bỏ qua đúng những từ tiếng Việt vừa được hạ chữ.
    if out:
        first = out.split(" ")[0]
        if not any(ch.isupper() for ch in first):
            out = out[0].upper() + out[1:]
    return re.sub(r"\s{2,}", " ", out)


DECISION = {
    "apply":   ("benefit", "Áp dụng ngay"),
    "consider": ("caution", "Cân nhắc"),
    "notyet":  ("neutral", "Chưa đủ đổi"),
}


def plot_row(item: dict, ax: LogAxis) -> str:
    eff = item.get("effect") or {}
    tone, label = DECISION.get(item.get("decision"), ("neutral", "Chưa đủ đổi"))
    hr, lo, hi = eff.get("hr"), eff.get("lo"), eff.get("hi")
    # Chứng cứ gây hại: toàn bộ khoảng tin cậy nằm bên phải vạch 1,0
    if lo and lo > 1.0:
        tone = "harm"
        label = "Gây hại"

    name = esc(normalize_title(item.get("title", "")))
    sub_bits = []
    if item.get("design"):
        sub_bits.append(esc(item["design"]))
    if hr and lo and hi:
        m = esc(eff.get("measure", "HR"))
        sub_bits.append(
            f'<span class="num">{m} {vn_num(hr)} ({vn_num(lo)}–{vn_num(hi)})</span>')
    sub = " · ".join(sub_bits)

    if hr and lo and hi:
        gl = "".join(f'<div class="gl" style="left:{ax.pos(t):.2f}%"></div>'
                     for t in ax.ticks() if t != 1.0)
        plot = (
            f'<div class="plot" aria-hidden="true">{gl}'
            f'<div class="nline" style="left:{ax.pos(1.0):.2f}%"></div>'
            f'<div class="ci" style="left:{ax.pos(lo):.2f}%;width:{ax.pos(hi)-ax.pos(lo):.2f}%"></div>'
            f'<div class="wh" style="left:{ax.pos(lo):.2f}%"></div>'
            f'<div class="wh" style="left:{ax.pos(hi):.2f}%"></div>'
            f'<div class="dot" style="left:{ax.pos(hr):.2f}%"></div></div>')
    else:
        txt = esc(item.get("effectText") or "không có tỷ số đơn lẻ")
        plot = f'<div class="plot"><span class="na">{txt}</span></div>'

    return (f'<div class="trial {tone}">'
            f'<div class="name">{name}<small>{sub}</small></div>{plot}'
            f'<div class="tagcell"><span class="tag t-{tone}">{esc(label)}</span></div></div>')


def li_list(items, cls="") -> str:
    """Danh sách việc cần làm / cờ đỏ — cũng chuẩn hoá viết hoa như tiêu đề.

    Khối `summary` trong dashboard hay viết "KHÔNG dùng…", "ĐỒNG THỜI…" để nhấn
    mạnh; trên trang đọc, nhấn mạnh thuộc về màu và độ đậm.
    """
    return "".join(f"<li>{esc(normalize_title(x))}</li>" for x in items)


DEC_VN = {"apply": "áp dụng ngay", "consider": "cân nhắc chọn lọc",
          "notyet": "chưa đủ để đổi thực hành"}


def khoi_mau_thuan(src: Path) -> str:
    """Dải cảnh báo: bản KHÁC cùng chủ đề đang kết luận ngược về cùng một PMID.

    VÌ SAO Ở ĐÂY (14/08/2026). Phép dò đã có từ 12/08 trong
    `tools/dang_ky_chu_de.py`, nhưng nó chỉ nói ra khi bác sĩ chủ động gõ lệnh đó.
    Tại phòng khám, thứ được mở là bản đọc — và bản đọc trước nay hoàn toàn im
    lặng về việc một lát cắt khác của cùng chủ đề đã kết luận ngược lại. Cảnh báo
    nằm đúng nơi người ta nhìn thì mới có tác dụng.

    KHÔNG đổi `decision` của bất kỳ mục nào (BH10) — chỉ đặt hai kết luận cạnh
    nhau để bác sĩ tự quyết. Cũng KHÔNG đoán bên nào đúng: hai bản có thể đang nói
    về hai KẾT CỤC khác nhau của cùng một thử nghiệm, và độ giống từ vựng không
    phân biệt được việc đó (BH28) — nên in cả hai tiêu đề, để người đọc phán.

    Không tính được (thiếu module, kho không quét được) thì NÓI RA là chưa kiểm,
    tuyệt đối không im lặng bỏ qua — im lặng ở đây đọc thành "đã kiểm, không có".
    """
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from dang_ky_chu_de import mau_thuan_cua_ban  # noqa: PLC0415
        xung_dot = mau_thuan_cua_ban(src)
    except Exception as e:  # noqa: BLE001 — chưa kiểm được phải LỘ RA
        return ('<div class="xungdot chuakiem"><h3>Chưa kiểm được mâu thuẫn giữa các bản</h3>'
                f'<p>Không quét được kho dashboard ({esc(type(e).__name__)}). '
                'Đây là “chưa biết”, không phải “không có”. Chạy '
                '<code>python tools/dang_ky_chu_de.py</code> để kiểm tay.</p></div>')
    if not xung_dot:
        return ""
    hang = "".join(
        f'<li><b>PMID {esc(x["pmid"])}</b> — bản đang đọc kết luận '
        f'<em>{esc(DEC_VN.get(x["quyet_dinh_minh"], x["quyet_dinh_minh"]))}</em>, '
        f'còn bản <b>{esc(x["doi_ben"])}</b> ({esc(x["ngay_ben"])}) kết luận '
        f'<em>{esc(DEC_VN.get(x["quyet_dinh_ben"], x["quyet_dinh_ben"]))}</em>.'
        f'<span class="doi">bản này: {esc(x["tieu_de_minh"])}</span>'
        f'<span class="doi">bản kia: {esc(x["tieu_de_ben"])}</span></li>'
        for x in xung_dot)
    return ('<div class="xungdot"><h3>Bản khác cùng chủ đề đang kết luận ngược — '
            f'{len(xung_dot)} mục</h3>'
            '<p class="sub">Đọc cả hai trước khi áp dụng. Hai bản có thể đang nói về hai kết cục '
            'khác nhau của cùng một nghiên cứu, hoặc một bản chưa được cập nhật. Máy không phán '
            'bên nào đúng và không tự đổi kết luận nào.</p>'
            f'<ul>{hang}</ul></div>')


def build_page(data: dict, source_name: str, src: Path | None = None) -> str:
    meta = data.get("meta", {})
    summary = data.get("summary", {})
    items = data.get("items", [])

    # CHỈ nhận hiệu số dạng TỶ SỐ (dương) lên trục log. Hiệu số dạng chênh lệch
    # trung bình có thể âm (vd −2,13 điểm) — đặt lên trục tỷ số là sai về bản chất,
    # nên những mục đó xuống danh sách không-biểu-đồ và hiển thị bằng chữ.
    def _ratio(it: dict) -> bool:
        e = it.get("effect") or {}
        vals = [e.get("hr"), e.get("lo"), e.get("hi")]
        return all(isinstance(v, (int, float)) and v > 0 for v in vals)

    eff_items = [i for i in items if _ratio(i)]
    bounds = []
    for i in eff_items:
        e = i["effect"]
        bounds += [e.get("lo"), e.get("hi")]
    ax = LogAxis.fit([b for b in bounds if b])

    # Chỉ mục CÓ hiệu số định lượng mới lên biểu đồ; chia theo phía của khoảng tin
    # cậy so với vạch 1,0 (không chia theo quyết định — quyết định là kết luận của
    # người tổng hợp, còn vị trí trên trục là dữ kiện của nguồn).
    support, against = [], []
    for i in eff_items:
        e = i["effect"]
        if e.get("hi") and e["hi"] < 1.0 and i.get("decision") != "notyet":
            support.append(i)
        else:
            against.append(i)

    # Mục không có hiệu số (guideline, đồng thuận, chiến lược…) liệt kê riêng, gọn.
    no_eff = [i for i in items if not _ratio(i)]
    by_dec: dict[str, list] = {"apply": [], "consider": [], "notyet": []}
    for i in no_eff:
        by_dec.setdefault(i.get("decision", "consider"), []).append(i)

    n_apply = sum(1 for i in items if i.get("decision") == "apply")
    n_pmid = sum(1 for i in items if i.get("pmid"))

    ticks = "".join(
        f'<i class="{"mark" if t == 1.0 else ""}" style="left:{ax.pos(t):.2f}%">{vn_num(t).rstrip("0").rstrip(",") if t != 1.0 else "1,0"}</i>'
        for t in ax.ticks())

    axis_head = (
        '<div class="axis-head"><div class="colcap" style="text-align:left">Thử nghiệm · can thiệp</div>'
        f'<div class="scale">{ticks}</div>'
        '<div class="colcap">Quyết định</div></div>')

    def field(rows, band_label, band_tone):
        if not rows:
            return ""
        body = "".join(plot_row(r, ax) for r in rows)
        return (f'<div class="field"><div class="field-inner">{axis_head}'
                f'<div class="band b-{band_tone}"><span>{esc(band_label)}</span><s></s></div>'
                f'{body}</div></div>')

    vn_checks = [i for i in items if "[CẦN XÁC NHẬN TẠI ĐƠN VỊ]" in (i.get("vn") or "")]

    def dec_block(key: str, heading: str) -> str:
        rows = by_dec.get(key) or []
        if not rows:
            return ""
        tone = DECISION[key][0]
        lis = "".join(
            f'<li><b>{esc(normalize_title(r.get("title","")))}</b>'
            f'<span>{esc(r.get("source",""))}</span></li>' for r in rows)
        return (f'<div class="noeff {tone}"><h3>{esc(heading)} '
                f'<span class="cnt">{len(rows)}</span></h3><ul>{lis}</ul></div>')

    noeff_html = "".join([
        dec_block("apply", "Áp dụng ngay"),
        dec_block("consider", "Cân nhắc chọn lọc"),
        dec_block("notyet", "Chưa đủ để đổi thực hành"),
    ])

    css = CSS
    parts = [f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(meta.get('question', 'Bản đọc chứng cứ'))[:90]}</title>
<style>{css}</style>
</head>
<body>
<div class="wrap">
<header>
  <p class="eyebrow">Bản đọc sau cập nhật chứng cứ · {esc(meta.get('updated', ''))}</p>
  <h1>{esc(normalize_title(meta.get('question', '')))}</h1>
  <p class="deck">Bản rút gọn để đọc ngay tại phòng khám: việc cần làm đứng trước, chứng cứ đặt
  sau. Mọi hiệu số nằm trên cùng một trục thang log, vạch 1,0 ở giữa — bên trái là có lợi,
  bên phải là bất lợi.</p>
  <div class="readout">
    <div><b>{len(items)}</b><span>mục đã xác minh</span></div>
    <div><b class="ok">{n_apply}</b><span>áp dụng ngay</span></div>
    <div><b class="ok">{n_pmid}/{len(items)}</b><span>mục có định danh truy nguyên</span></div>
    <div><b class="ok">{len(eff_items)}</b><span>mục có hiệu số định lượng</span></div>
  </div>
</header>

{khoi_mau_thuan(src) if src else ''}

<nav class="nav" aria-label="Mục lục">
  <a href="#lam">1. Việc cần làm</a>
  <a href="#ungho">2. Chứng cứ ủng hộ</a>
  <a href="#khong">3. Không ủng hộ hoặc gây hại</a>
  <a href="#khac">4. Khuyến cáo và đồng thuận</a>
  <a href="#vn">5. Áp dụng tại Việt Nam</a>
</nav>

<section class="sec" id="lam">
  <div class="sec-head"><h2>1. Việc cần làm</h2><p>đọc trước, chi tiết chứng cứ ở các mục sau</p></div>
  <div class="redflags">
    <h3>Cờ đỏ — chuyển cấp cứu, không trì hoãn để tra cứu</h3>
    <p class="sub">Xử trí an toàn đi trước mọi bước thẩm định chứng cứ.</p>
    <ul>{li_list(summary.get('redFlags', []))}</ul>
  </div>
  <div class="acts">
    <div class="act go"><h3>Nên làm hiện nay</h3><ul>{li_list(summary.get('doNow', []))}</ul></div>
    <div class="act stop"><h3>Không nên, hoặc chưa nên đổi</h3><ul>{li_list(summary.get('dontDo', []))}</ul></div>
  </div>
</section>

<section class="sec" id="ungho">
  <div class="sec-head"><h2>2. Chứng cứ ủng hộ thay đổi</h2><p>hiệu số và khoảng tin cậy 95%, trích đúng như nguồn báo cáo</p></div>
  {field(support, 'Khoảng tin cậy nằm trọn bên trái vạch 1,0', 'benefit')}
  <div class="legend">
    <div><span class="k-dot"></span>ước lượng điểm</div>
    <div><span class="k-bar"></span>khoảng tin cậy 95%</div>
    <div><span class="k-nl"></span>vạch 1,0 — không khác biệt</div>
    <div>Thanh càng dài, độ chắc chắn càng thấp</div>
  </div>
</section>

<section class="sec" id="khong">
  <div class="sec-head"><h2>3. Chứng cứ không ủng hộ, hoặc gây hại</h2><p>chú ý phần vượt sang phải vạch 1,0</p></div>
  {field(against, 'Khoảng tin cậy chạm hoặc vượt vạch 1,0', 'harm')}
</section>

<section class="sec" id="khac">
  <div class="sec-head"><h2>4. Khuyến cáo và đồng thuận</h2><p>mục không có hiệu số định lượng để đặt lên trục</p></div>
  <div class="noeffs">{noeff_html}</div>
</section>

<section class="sec vn" id="vn">
  <div class="sec-head"><h2>5. Áp dụng tại Việt Nam</h2><p>mục cần đối chiếu nguồn lực và quy trình tại đơn vị</p></div>
  <div class="flags">
    <h3>Cần xác nhận tại đơn vị trước khi áp dụng</h3>
    <ul>{''.join(f"<li><b>{esc(i.get('title',''))}</b> — {esc(i.get('vn',''))}</li>" for i in vn_checks) or '<li>Không có mục nào cần xác nhận tại đơn vị.</li>'}</ul>
  </div>
</section>

<footer>
  <p>Hiệu số trích đúng như nguồn gốc báo cáo. Nguồn nào không tự phân hạng GRADE thì không gán
  thay. Tài liệu không chứa thông tin định danh người bệnh. Cần bác sĩ kiểm chứng toàn văn trước
  khi áp dụng cho người bệnh cụ thể.</p>
  <p class="stamp">Sinh từ {esc(source_name)}</p>
</footer>
</div>
</body>
</html>
"""]
    return "".join(parts)


# CSS tách riêng cho dễ bảo trì; quy ước viết hoa theo câu (xem docstring đầu file).
CSS = """
:root{--ground:#F5F7F6;--surface:#FFF;--ink:#111A1C;--ink-2:#47575B;--ink-3:#7B8A8D;
--rule:#DDE4E3;--rule-strong:#C0CBCA;--benefit:#0F7A68;--benefit-soft:#E2F0ED;
--caution:#B0731A;--caution-soft:#F7EEDE;--harm:#9E2F2F;--harm-soft:#F6E7E5;
--null:#5F7280;--null-soft:#ECEFF1;--axis:#40607F;
--sans:"Times New Roman",Times,"Liberation Serif","Nimbus Roman",serif;
--mono:"Times New Roman",Times,"Liberation Serif",serif;--measure:70ch}
@media (prefers-color-scheme:dark){:root{--ground:#0F1618;--surface:#161F21;--ink:#E9EFEE;
--ink-2:#A3B4B5;--ink-3:#748688;--rule:#263234;--rule-strong:#3A4B4E;--benefit:#4FC0A7;
--benefit-soft:#12302A;--caution:#DCA64E;--caution-soft:#332614;--harm:#E28079;
--harm-soft:#341B19;--null:#93A5AE;--null-soft:#1E282B;--axis:#82A6CA}}
:root[data-theme=dark]{--ground:#0F1618;--surface:#161F21;--ink:#E9EFEE;--ink-2:#A3B4B5;
--ink-3:#748688;--rule:#263234;--rule-strong:#3A4B4E;--benefit:#4FC0A7;--benefit-soft:#12302A;
--caution:#DCA64E;--caution-soft:#332614;--harm:#E28079;--harm-soft:#341B19;--null:#93A5AE;
--null-soft:#1E282B;--axis:#82A6CA}
:root[data-theme=light]{--ground:#F5F7F6;--surface:#FFF;--ink:#111A1C;--ink-2:#47575B;
--ink-3:#7B8A8D;--rule:#DDE4E3;--rule-strong:#C0CBCA;--benefit:#0F7A68;--benefit-soft:#E2F0ED;
--caution:#B0731A;--caution-soft:#F7EEDE;--harm:#9E2F2F;--harm-soft:#F6E7E5;--null:#5F7280;
--null-soft:#ECEFF1;--axis:#40607F}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);font-family:var(--sans);
font-size:17.5px;line-height:1.6}
.wrap{max-width:1000px;margin:0 auto;padding:clamp(28px,5vw,64px) clamp(20px,4vw,48px) 72px}
a{color:inherit}a:focus-visible{outline:2px solid var(--axis);outline-offset:3px}
.eyebrow{margin:0;font-family:var(--mono);font-size:12px;letter-spacing:.06em;color:var(--axis)}
h1{font-size:clamp(28px,3.9vw,40px);line-height:1.2;font-weight:700;letter-spacing:0;
margin:14px 0 0;max-width:34ch;text-wrap:balance}
.deck{max-width:var(--measure);color:var(--ink-2);font-size:16.5px;margin:18px 0 0;text-wrap:pretty}
.readout{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:20px 28px;
margin:32px 0 0;padding:22px 0 0;border-top:1px solid var(--rule)}
.readout div{display:flex;flex-direction:column;gap:3px}
.readout b{font-family:var(--mono);font-size:27px;font-weight:700;letter-spacing:0;
font-variant-numeric:tabular-nums;color:var(--ink)}
.readout b.ok{color:var(--benefit)}
.readout span{font-size:12.5px;color:var(--ink-3);line-height:1.45}
.nav{position:sticky;top:0;z-index:20;margin-top:32px;padding:12px 0;background:var(--ground);
border-bottom:1px solid var(--rule);display:flex;flex-wrap:wrap;gap:20px}
.nav a{font-size:13px;color:var(--ink-3);text-decoration:none;border-bottom:1px solid transparent}
.nav a:hover{color:var(--ink);border-bottom-color:var(--rule-strong)}
.sec{margin-top:56px;scroll-margin-top:64px}
.sec-head{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;padding-bottom:12px;
border-bottom:1px solid var(--rule-strong)}
.sec-head h2{font-size:19px;font-weight:700;text-transform:uppercase;letter-spacing:.02em;
color:var(--ink);margin:0}
.sec-head p{margin:0;color:var(--ink-3);font-size:13.5px}
.redflags{margin-top:24px;background:var(--harm-soft);border-top:3px solid var(--harm);padding:22px 26px}
.redflags h3{margin:0 0 4px;font-size:16.5px;font-weight:700;color:var(--harm)}
.redflags .sub{margin:0 0 14px;font-size:13.5px;color:var(--ink-2)}
.redflags ul{margin:0;padding:0;list-style:none;display:grid;
grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:10px 30px}
.redflags li{position:relative;padding-left:18px;font-size:14.5px;line-height:1.55;color:var(--ink-2)}
.redflags li::before{content:"";position:absolute;left:0;top:8px;width:7px;height:7px;
border-radius:50%;background:var(--harm)}
/* Dải mâu thuẫn giữa các bản — đặt ngay dưới đầu trang, trước mục lục, vì đây là
   cảnh báo về ĐỘ TIN CẬY của chính tài liệu đang đọc. Dùng tông cảnh báo (cam)
   chứ KHÔNG dùng tông cờ đỏ: cờ đỏ là nguy cấp lâm sàng của người bệnh, hai thứ
   không được trông giống nhau. */
.xungdot{background:var(--caution-soft);border-left:4px solid var(--caution);
padding:20px 24px;margin:26px 0 0}
.xungdot h3{margin:0 0 6px;font-size:16px;font-weight:700;color:var(--caution)}
.xungdot .sub{margin:0 0 14px;font-size:13.5px;line-height:1.55;color:var(--ink-2)}
.xungdot ul{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:13px}
.xungdot li{font-size:14.5px;line-height:1.55;color:var(--ink-2)}
.xungdot li b{color:var(--ink)}.xungdot li em{font-style:normal;font-weight:700;color:var(--caution)}
.xungdot .doi{display:block;font-size:13px;color:var(--ink-3);margin-top:2px}
.xungdot.chuakiem{background:var(--ground);border-left-color:var(--rule-strong)}
.xungdot.chuakiem h3{color:var(--ink-2)}
.xungdot code{font-size:12.5px;background:var(--surface);padding:1px 5px;border-radius:3px}
.acts{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:1px;
margin-top:24px;background:var(--rule)}
.act{background:var(--ground);padding:22px 24px}
.act h3{margin:0 0 14px;font-size:16px;font-weight:700}
.act.go h3{color:var(--benefit)}.act.stop h3{color:var(--caution)}
.act ul{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:11px}
.act li{position:relative;padding-left:20px;font-size:14.5px;line-height:1.55;color:var(--ink-2)}
.act.go li::before,.act.stop li::before{content:"";position:absolute;left:0;top:6px;width:9px;
height:9px;border-radius:2px}
.act.go li::before{background:var(--benefit)}.act.stop li::before{background:var(--caution)}
.field{margin-top:22px;overflow-x:auto}.field-inner{min-width:700px}
.axis-head{display:grid;grid-template-columns:minmax(240px,1.05fr) minmax(300px,1.3fr) 104px;
gap:20px;align-items:end;padding-bottom:10px}
.scale{position:relative;height:18px}
.scale i{position:absolute;top:4px;transform:translateX(-50%);font-style:normal;
font-family:var(--mono);font-size:12.5px;color:var(--ink-3);font-variant-numeric:tabular-nums}
.scale i.mark{color:var(--axis);font-weight:700}
.colcap{font-size:12px;color:var(--ink-3);text-align:right}
.band{display:flex;align-items:center;gap:14px;margin:24px 0 2px}
.band span{font-size:13.5px;font-weight:700}
.band s{flex:1;height:1px;background:var(--rule-strong);text-decoration:none}
.band.b-benefit span{color:var(--benefit)}.band.b-harm span{color:var(--harm)}
.trial{display:grid;grid-template-columns:minmax(240px,1.05fr) minmax(300px,1.3fr) 104px;
gap:20px;align-items:center;padding:16px 0;border-bottom:1px solid var(--rule);
transition:background .18s ease}
.trial:hover{background:var(--surface)}
.trial .name{font-size:15.5px;font-weight:700;line-height:1.35;text-wrap:pretty}
.trial .name small{display:block;font-weight:400;font-size:13px;color:var(--ink-3);margin-top:4px}
.trial .name .num{font-family:var(--mono);font-variant-numeric:tabular-nums;color:var(--ink-2)}
.plot{position:relative;height:26px}
.gl{position:absolute;top:2px;bottom:2px;width:1px;background:var(--rule)}
.nline{position:absolute;top:-4px;bottom:-4px;width:1.5px;background:var(--axis);opacity:.85}
.ci{position:absolute;top:12px;height:2.5px;border-radius:2px}
.wh{position:absolute;top:7px;height:12px;width:1.5px;opacity:.75}
.dot{position:absolute;top:7.5px;width:11px;height:11px;margin-left:-5.5px;border-radius:50%;
border:2.5px solid var(--surface)}
.trial:hover .dot{transform:scale(1.2);transition:transform .18s ease}
.benefit .ci,.benefit .dot,.benefit .wh{background:var(--benefit)}
.caution .ci,.caution .dot,.caution .wh{background:var(--caution)}
.neutral .ci,.neutral .dot,.neutral .wh{background:var(--null)}
.harm .ci,.harm .dot,.harm .wh{background:var(--harm)}
.plot .na{font-size:12.5px;color:var(--ink-3);line-height:26px}
.tag{display:inline-block;font-size:12px;padding:4px 10px;border-radius:3px;white-space:nowrap}
.t-benefit{background:var(--benefit-soft);color:var(--benefit)}
.t-caution{background:var(--caution-soft);color:var(--caution)}
.t-neutral{background:var(--null-soft);color:var(--null)}
.t-harm{background:var(--harm-soft);color:var(--harm)}
.trial .tagcell{text-align:right}
.legend{display:flex;flex-wrap:wrap;gap:24px;margin-top:20px;font-size:12.5px;color:var(--ink-3)}
.legend div{display:flex;align-items:center;gap:8px}
.k-dot{width:10px;height:10px;border-radius:50%;background:var(--ink-3)}
.k-bar{width:22px;height:2.5px;border-radius:2px;background:var(--ink-3)}
.k-nl{width:1.5px;height:14px;background:var(--axis)}
.noeffs{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:1px;
margin-top:22px;background:var(--rule)}
.noeff{background:var(--ground);padding:20px 22px}
.noeff h3{margin:0 0 12px;font-size:16px;font-weight:700;display:flex;align-items:baseline;gap:8px}
.noeff .cnt{font-family:var(--mono);font-size:12px;font-weight:400;color:var(--ink-3)}
.noeff.benefit h3{color:var(--benefit)}
.noeff.caution h3{color:var(--caution)}
.noeff.neutral h3{color:var(--null)}
.noeff ul{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:12px}
.noeff li{font-size:14px;line-height:1.5;color:var(--ink-2)}
.noeff li b{display:block;font-weight:700;color:var(--ink);margin-bottom:2px;text-wrap:pretty}
.noeff li span{display:block;font-size:12.5px;color:var(--ink-3)}
.flags{margin-top:22px;padding:20px 24px;background:var(--caution-soft);border-top:2px solid var(--caution)}
.flags h3{margin:0 0 10px;font-size:16px;font-weight:700;color:var(--caution)}
.flags ul{margin:0;padding-left:18px;color:var(--ink-2);font-size:14.5px;line-height:1.7}
.flags li{margin-bottom:8px}.flags li::marker{color:var(--caution)}
.flags b{font-weight:700;color:var(--ink)}
footer{margin-top:56px;padding-top:22px;border-top:1px solid var(--rule)}
footer p{margin:0;max-width:var(--measure);font-size:12.5px;line-height:1.65;color:var(--ink-3)}
footer .stamp{margin-top:10px;font-family:var(--mono);font-size:11.5px}
@media (max-width:640px){.nav{gap:14px}}
@media (prefers-reduced-motion:reduce){.trial,.trial .dot{transition:none}
.trial:hover .dot{transform:none}}
@media print{:root{--ground:#fff;--surface:#fff;--ink:#000;--ink-2:#333;--ink-3:#666;
--rule:#ccc;--rule-strong:#999}
.nav{display:none}.wrap{max-width:none;padding:0}.field{overflow:visible}
.field-inner{min-width:0}.sec{margin-top:26px;page-break-inside:avoid}
.trial,.flags,.redflags,.act{page-break-inside:avoid}h1{font-size:28px}}
"""


def main() -> int:
    configure_utf8_stdio()
    ap = argparse.ArgumentParser(description="Sinh bản đọc từ Web Dashboard lâm sàng")
    ap.add_argument("dashboard", help="đường dẫn tới WebDashboard_*.html")
    ap.add_argument("-o", "--out", help="file đầu ra (mặc định: derivatives/<mã>_ban-doc.html)")
    a = ap.parse_args()

    src = Path(a.dashboard)
    if not src.exists():
        print(f"✗ Không thấy file: {src}", file=sys.stderr)
        return 2

    data = extract_data(src.read_text(encoding="utf-8"))
    page = build_page(data, src.name, src)

    if a.out:
        out = Path(a.out)
    else:
        stem = src.stem.replace("WebDashboard_EBM_VanDeCuThe_", "")
        DERIV.mkdir(parents=True, exist_ok=True)
        out = DERIV / f"{stem}_ban-doc.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")

    n = len(data.get("items", []))
    print(f"✓ Đã ghi {out}")
    print(f"  {n} mục · {len(page):,} ký tự")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
