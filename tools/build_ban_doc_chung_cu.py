#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sinh BẢN ĐỌC sau cập nhật chứng cứ từ một Web Dashboard lâm sàng.

Bản đọc là trang HTML độc lập để bác sĩ đọc NGAY sau khi chạy xong dây chuyền cập
nhật chứng cứ: việc cần làm và cờ đỏ đứng trước, chứng cứ đặt trên MỘT trục thang
log dùng chung (vạch 1,0 ở giữa — mặc định trái là có lợi, phải là bất lợi; khi
nguồn khai rõ chiều ngược lại qua `effect.favors`, mục được xếp dải và gắn nhãn
theo đúng khai báo đó, KHÔNG theo vị trí — sửa 16/09/2026, xem `_ratio_favors_decided`).

Hiệu số dạng CHÊNH LỆCH (SMD, MD, RD — giá trị "không khác biệt" là 0) KHÔNG được
đặt lên trục log đó (sửa 16/09/2026, xem `effect_scale`): chúng có mục riêng trên
thang TUYẾN TÍNH, vạch 0. Trang không có hiệu số chênh lệch giữ nguyên bố cục cũ.

Khác dashboard (công cụ tra cứu, lọc theo mặt) và khác bản Word (tài liệu lưu trữ
đầy đủ): bản đọc CHỈ giữ phần đổi được thực hành.

Cách dùng:
    python3 tools/build_ban_doc_chung_cu.py <dashboard>.html [-o <đầu ra>.html]

Mặc định ghi vào EBM-Dashboards/derivatives/<mã>_ban-doc.html

QUY ƯỚC TRÌNH BÀY (chuẩn cho tài liệu cập nhật chứng cứ khoa học — bác sĩ chốt 2026-08-05):
  - Font mặc định TIMES NEW ROMAN cho toàn trang, đồng bộ với bản Word xuất kèm.
  - ĐỀ MỤC (mục 1…5; 1…6 khi có mục hiệu số chênh lệch) IN HOA và IN ĐẬM. Tiêu đề khối con in đậm, không in hoa —
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
import unicodedata
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


def _tim_goc_repo(bat_dau: Path) -> Path:
    """Tìm gốc repo bằng cách đi lên tìm thư mục có `.git` — ĐỘC LẬP với độ sâu.

    File này (build_ban_doc_chung_cu.py) có HAI bản byte-identical
    (`tools/` ở gốc và `sync/skills/cap-nhat-chung-cu-y-khoa/tools/`), nằm ở
    hai độ sâu KHÁC NHAU so với gốc repo (1 vs 4 cấp). Một `parents[N]` cố
    định chỉ đúng cho MỘT bản — bản kia sẽ trỏ vào đường dẫn không tồn tại
    mà không hề báo lỗi rõ ràng cho tới khi dùng (chính là lỗi đã xảy ra:
    bản mirror gọi `tools/tuyen_bo_do_phu.py` NGAY TRONG thư mục của chính
    nó, trong khi tệp thật chỉ có ở `tools/` gốc repo).
    """
    for p in (bat_dau, *bat_dau.parents):
        if (p / ".git").exists():
            return p
    return bat_dau.parents[1]  # dự phòng nếu không tìm thấy .git


def khoi_do_phu() -> str:
    """Tuyên bố ĐỘ PHỦ NGUỒN — LÔ I PHA 4 phải hiện ở NƠI BÁC SĨ ĐỌC, không chỉ
    nằm trong reports/. Sinh sống từ data/sources.json qua tools/tuyen_bo_do_phu;
    sinh không được thì in rõ «chưa sinh được» — im lặng ≠ an toàn (I7)."""
    import importlib.util as _ilu
    import sys as _sys
    try:
        duong = _tim_goc_repo(Path(__file__).resolve()) / "tools" / "tuyen_bo_do_phu.py"
        spec = _ilu.spec_from_file_location("tbdp_bd", duong)
        m = _ilu.module_from_spec(spec)
        _sys.modules["tbdp_bd"] = m
        spec.loader.exec_module(m)
        return esc(m.tra_khoi())
    except Exception as exc:  # noqa: BLE001
        return esc(f"[CHƯA SINH ĐƯỢC TUYÊN BỐ ĐỘ PHỦ: {exc} — chạy "
                   f"python3 tools/tuyen_bo_do_phu.py]")

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


# ─────────── thang hiệu số: TỶ SỐ (log, vạch 1,0) hay CHÊNH LỆCH (tuyến tính, vạch 0) ───────────
#
# SỬA 16/09/2026. Trục log ở trên chỉ đúng cho TỶ SỐ. Bộ lọc cũ `_ratio()` chỉ loại hiệu số có
# giá trị âm, nên chênh lệch TOÀN DƯƠNG vẫn lên trục log. Đo thật trên bản VKDT tâm thần kinh
# 11/08: "SMD đau" 0,69 (0,54–0,84) rơi vào dải "ủng hộ" vì cận trên < 1,0, còn "Chênh DAS28"
# 1,24 (1,10–1,37) bị gắn nhãn "Gây hại" vì cận dưới > 1,0 — cả hai sai bản chất, vì vạch
# "không khác biệt" của chênh lệch là 0 chứ không phải 1.
#
# Luật dùng CHUNG với template Evidence Workbench (`effectScale` trong
# templates/web-dashboard-evidence-workbench.html); ba danh sách dưới PHẢI trùng khít bản JS —
# test canh: tools/test_ew_template_ho_thiet_ke_thang_hieu_so.py.
#   • effect.scale 'ratio'|'difference' khai tường minh ⇒ dùng đúng giá trị đó;
#   • không khai ⇒ suy từ effect.measure: cụm từ nhận ra ĐẦU TIÊN theo vị trí quyết định (cùng
#     vị trí thì cụm dài hơn thắng). Khớp NGUYÊN TỪ — "RD" nằm trong "DMARD" không tính; "tỷ số
#     chênh"/"tỷ suất chênh" là odds ratio nên cụm tỷ số đứng trước thắng chữ "chênh". Từ ĐẦU
#     TIÊN bắt đầu bằng Δ hoặc β (ΔHbA1c, hệ số β) ⇒ chênh lệch;
#   • không nhận ra gì ⇒ 'ratio' — tương thích ngược với mọi dashboard cũ.
SCALE_RATIO_TERMS = (
    "hr", "rr", "or", "irr", "ahr", "aor", "shr", "cshr", "ror", "rom",
    "tỷ số", "ty so", "tỷ suất chênh", "ty suat chenh", "nguy cơ tương đối",
    "hazard ratio", "odds ratio", "risk ratio", "rate ratio", "relative risk",
)
SCALE_DIFF_TERMS = (
    "smd", "md", "wmd", "rd", "chênh", "chenh",
    "hiệu số trung bình", "hiệu số trung bình chuẩn hoá", "hiệu số trung bình chuẩn hóa",
    "hiệu số rủi ro", "hiệu số nguy cơ", "khác biệt trung bình",
    "mean difference", "standardized mean difference", "standardised mean difference",
    "risk difference", "hedges", "cohen",
)
SCALE_DIFF_FIRST_TOKEN_PREFIXES = ("δ", "β")
# Chỉ bản đọc dùng: chênh lệch CHUẨN HOÁ không mang đơn vị nên so được với nhau ⇒ chung MỘT trục.
# MD/RD/Δ/β mang đơn vị riêng của từng kết cục (điểm, mmHg, %) ⇒ mỗi mục một trục riêng, để
# không ai so độ dài thanh giữa hai thang khác đơn vị.
STANDARDIZED_DIFF_TERMS = frozenset({
    "smd", "hiệu số trung bình chuẩn hoá", "hiệu số trung bình chuẩn hóa",
    "standardized mean difference", "standardised mean difference", "hedges", "cohen",
})

_SCALE_TOKEN_RE = re.compile(r"[^\W_]+")


def _scale_tokens(text) -> list[str]:
    """Tách từ giống `scaleTokens` bên JS: NFC, chữ thường, chuỗi chữ/số liền nhau."""
    s = "" if text is None else str(text)
    s = unicodedata.normalize("NFC", s.replace("∆", "Δ")).lower()
    return _SCALE_TOKEN_RE.findall(s)


_SCALE_TERM_TOKENS = ([(_scale_tokens(t), "ratio", t) for t in SCALE_RATIO_TERMS]
                      + [(_scale_tokens(t), "difference", t) for t in SCALE_DIFF_TERMS])


def measure_scale_match(measure) -> tuple[str, str | None]:
    """Trả (thang, cụm từ đã khớp); cụm từ là None khi rơi về mặc định 'ratio'."""
    tokens = _scale_tokens(measure)
    if tokens and any(tokens[0].startswith(p) for p in SCALE_DIFF_FIRST_TOKEN_PREFIXES):
        return "difference", tokens[0][0]
    for i in range(len(tokens)):
        best = None
        for words, kind, term in _SCALE_TERM_TOKENS:
            n = len(words)
            if n and (best is None or n > best[0]) and tokens[i:i + n] == words:
                best = (n, kind, term)
        if best:
            return best[1], best[2]
    return "ratio", None


def measure_scale(measure) -> str:
    """'ratio' | 'difference' suy từ nhãn thước đo (`effect.measure`)."""
    return measure_scale_match(measure)[0]


def effect_scale(effect) -> str:
    """'ratio' | 'difference' cho khối `effect` của một item — khai tường minh thắng suy luận."""
    e = effect if isinstance(effect, dict) else {}
    khai = e.get("scale")
    s = ("" if khai is None else str(khai)).strip().lower()
    if s in ("ratio", "difference"):
        return s
    return measure_scale(e.get("measure"))


class LinearAxis:
    """Trục TUYẾN TÍNH đối xứng quanh 0 cho hiệu số CHÊNH LỆCH.

    Đối xứng là có chủ ý: vạch 0 luôn nằm giữa nên chiều của ước lượng đọc được ngay,
    tương tự vị trí vạch 1,0 trên trục log.
    """

    MIN_TICK_GAP = LogAxis.MIN_TICK_GAP

    def __init__(self, nice: float):
        self.nice = nice            # số tròn bao trọn |giá trị| lớn nhất
        self.ext = nice * 1.1       # biên trục: chừa lề 10% để nhãn mép không bị cắt

    def pos(self, v: float) -> float:
        return (v + self.ext) / (2 * self.ext) * 100

    @staticmethod
    def _nice(x: float) -> float:
        """Số tròn nhỏ nhất ≥ x trong dãy 1 · 2 · 2,5 · 5 × 10^k."""
        k = math.floor(math.log10(x))
        for m in (1, 2, 2.5, 5, 10):
            if m * 10 ** k >= x - 1e-12:
                return m * 10 ** k
        return 10 ** (k + 1)

    @classmethod
    def fit(cls, values) -> "LinearAxis":
        vals = [abs(v) for v in values
                if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)]
        top = max(vals) if vals and max(vals) > 0 else 1.0
        return cls(cls._nice(top))

    def ticks(self) -> list[float]:
        """Nhãn tại 0, ±nửa số tròn, ±số tròn — lọc theo khoảng cách thật như LogAxis."""
        kept = [0.0]
        for t in (-self.nice, -self.nice / 2, self.nice / 2, self.nice):
            if all(abs(self.pos(t) - self.pos(k)) >= self.MIN_TICK_GAP for k in kept):
                kept.append(t)
        return sorted(kept)


def vn_num(x: float) -> str:
    """Số thập phân theo chuẩn tiếng Việt: dấu phẩy."""
    return f"{x:.2f}".replace(".", ",")


def vn_signed(x: float) -> str:
    """Số có dấu cho hiệu số chênh lệch: dấu trừ thật (−) và dấu phẩy thập phân."""
    return ("−" if x < 0 else "") + vn_num(abs(x))


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


# SỬA 16/09/2026 (tiếp nối bản vá `plot_row_diff` ngày trước): nhánh TỶ SỐ (log, vạch 1,0)
# từng suy "Gây hại" THUẦN theo vị trí — `lo > 1.0` — không hề đọc `effect.favors`. Với kết
# cục mà tỷ số CAO là TỐT (tỷ lệ đáp ứng, OR ngưng một thuốc không phù hợp…), nguồn khai
# `favors:true` mà vẫn bị gắn "Gây hại" chỉ vì CI nằm bên phải vạch 1,0 — sai bản chất, cùng
# họ lỗi mà `plot_row_diff` đã vá cho thang chênh lệch. Đo thật trên kho 16/09/2026: 12 mục
# `favors:true` với `lo > 1,0` bị gắn oan (duloxetine OR giảm đau ≥50% 1,91 (1,69–2,17)…).
#
# Hàm dùng CHUNG cho cả nhãn "Gây hại" (plot_row) lẫn dải xếp mục 2/3 (build_page) — một mục
# không được label một đằng, xếp dải một nẻo.
def _ratio_favors_decided(effect: dict) -> bool | None:
    """True/False khi `favors` khai tường minh VÀ khoảng tin cậy KHÔNG chạm vạch 1,0 (đủ để
    đọc chiều mà không cần suy từ vị trí). None khi chưa đủ để quyết bằng favors — `favors`
    vắng mặt, hoặc CI còn chạm vạch 1,0 (lo ≤ 1,0 ≤ hi) — khi đó GIỮ NGUYÊN luật vị trí cũ ở
    nơi gọi, để không đổi hành vi của mọi dashboard đã xuất bản chưa khai `favors`."""
    favors = effect.get("favors")
    if favors not in (True, False):
        return None
    lo, hi = effect.get("lo"), effect.get("hi")
    if not (lo and hi) or not (lo > 1.0 or hi < 1.0):
        return None
    return favors


def plot_row(item: dict, ax: LogAxis) -> str:
    eff = item.get("effect") or {}
    tone, label = DECISION.get(item.get("decision"), ("neutral", "Chưa đủ đổi"))
    hr, lo, hi = eff.get("hr"), eff.get("lo"), eff.get("hi")
    decided = _ratio_favors_decided(eff)
    if decided is False:
        # Nguồn khai rõ: chiều đã quan sát của tỷ số này BẤT LỢI, và CI không chạm vạch 1,0.
        tone, label = "harm", "Gây hại"
    elif decided is None and lo and lo > 1.0:
        # `favors` vắng mặt (hoặc CI chạm vạch 1,0) — luật vị trí cũ, tương thích ngược.
        tone, label = "harm", "Gây hại"
    # decided is True: nguồn khai rõ chiều này CÓ LỢI — giữ nguyên tone/label theo quyết định,
    # KHÔNG BAO GIỜ gắn "Gây hại" chỉ vì tỷ số nằm bên phải vạch 1,0.

    name = esc(normalize_title(item.get("title", "")))
    sub_bits = []
    if item.get("design"):
        sub_bits.append(esc(item["design"]))
    # Thẩm định MỚI CÓ TÓM TẮT phải hiện ra cho người ĐỌC, không nằm im trong metadata:
    # cổng liêm chính cảnh báo đúng điều này, và bản đọc là nơi bác sĩ thật sự đọc.
    if item.get("appraisalCompleteness") == "partial":
        sub_bits.append('<span class="partial">thẩm định trên tóm tắt — '
                        'chưa đọc toàn văn</span>')
    if hr and lo and hi:
        m = esc(eff.get("measure", "HR"))
        sub_bits.append(
            f'<span class="num">{m} {vn_num(hr)} ({vn_num(lo)}–{vn_num(hi)})</span>')
    # Định danh truy nguyên (PMID ưu tiên, rồi DOI, rồi URL) PHẢI hiện ra ở đây —
    # đây là nơi bác sĩ thật sự đọc. Trước bản vá này, plot_row() chỉ ĐẾM
    # item.get("pmid") cho thống kê đầu trang ("N/N mục có định danh truy
    # nguyên") mà không bao giờ IN nó ra: trang tự nhận có định danh truy
    # nguyên nhưng không một dòng nào trong 6 mục thật sự cho thấy định danh
    # đó — phát hiện khi dựng dashboard Suy tim HFnrEF 2026-09-07 (0/6 PMID
    # xuất hiện trong bản đọc dù cả 6 item đều khai đủ). Vi phạm bất biến
    # "mỗi đầu ra kèm PMID/DOI" của CLAUDE.md.
    ident = item.get("pmid") or item.get("doi") or item.get("url")
    if ident:
        label_id = "PMID" if item.get("pmid") else ("DOI" if item.get("doi") else "URL")
        sub_bits.append(esc(f"{label_id} {ident}"))
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


def plot_row_diff(item: dict, ax: LinearAxis) -> str:
    """Một dòng hiệu số CHÊNH LỆCH trên trục tuyến tính, vạch 0.

    Chiều có lợi của chênh lệch tuỳ KẾT CỤC — điểm đau giảm là tốt, điểm chất lượng sống tăng
    là tốt — nên KHÔNG suy từ phía của vạch 0 như nhánh tỷ số suy từ vạch 1,0. Nhãn "Gây hại"
    chỉ gắn khi nguồn khai rõ `favors` = false VÀ khoảng tin cậy không chạm vạch 0.
    """
    eff = item["effect"]
    tone, label = DECISION.get(item.get("decision"), ("neutral", "Chưa đủ đổi"))
    hr, lo, hi = eff["hr"], eff["lo"], eff["hi"]
    if eff.get("favors") is False and (lo > 0 or hi < 0):
        tone, label = "harm", "Gây hại"

    name = esc(normalize_title(item.get("title", "")))
    sub_bits = []
    if item.get("design"):
        sub_bits.append(esc(item["design"]))
    if item.get("appraisalCompleteness") == "partial":
        sub_bits.append('<span class="partial">thẩm định trên tóm tắt — '
                        'chưa đọc toàn văn</span>')
    m = esc(eff.get("measure") or "Hiệu số chênh lệch")
    sub_bits.append(f'<span class="num">{m} {vn_signed(hr)} '
                    f'({vn_signed(lo)} đến {vn_signed(hi)})</span>')
    sub = " · ".join(sub_bits)

    gl = "".join(f'<div class="gl" style="left:{ax.pos(t):.2f}%"></div>'
                 for t in ax.ticks() if t != 0)
    plot = (
        f'<div class="plot" aria-hidden="true">{gl}'
        f'<div class="nline" style="left:{ax.pos(0):.2f}%"></div>'
        f'<div class="ci" style="left:{ax.pos(lo):.2f}%;width:{ax.pos(hi)-ax.pos(lo):.2f}%"></div>'
        f'<div class="wh" style="left:{ax.pos(lo):.2f}%"></div>'
        f'<div class="wh" style="left:{ax.pos(hi):.2f}%"></div>'
        f'<div class="dot" style="left:{ax.pos(hr):.2f}%"></div></div>')

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


def khoi_rut_bai(src: Path) -> str:
    """Dải cảnh báo: gói này trích một nguồn ĐÃ BỊ RÚT / có quan ngại.

    Nặng hơn mâu thuẫn giữa các bản nên đặt TRÊN, và dùng tông đỏ. Nguồn dữ kiện là
    sổ xác minh (`tools/so_xac_minh_nguon.py::nguon_da_rut`) — chỉ đọc kết luận
    DƯƠNG TÍNH đã được chuỗi 3 tầng xác nhận, không tự suy diễn.

    Sổ im lặng KHÔNG được hiển thị thành "đã kiểm, sạch": khi không đọc được sổ thì
    nói rõ là CHƯA KIỂM. Không tự gỡ mục nào — một bài "rút và thay" cần đối chiếu
    với bản đã thay chứ không phải xoá đi, và đó là việc của bác sĩ.
    """
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from so_xac_minh_nguon import nguon_da_rut  # noqa: PLC0415
        da_rut = nguon_da_rut(Path(src).name)
    except Exception as e:  # noqa: BLE001 — chưa kiểm được phải LỘ RA
        return ('<div class="xungdot chuakiem"><h3>Chưa kiểm được tình trạng rút bài</h3>'
                f'<p>Không đọc được sổ xác minh nguồn ({esc(type(e).__name__)}). Đây là '
                '“chưa biết”, không phải “không có”. Chạy '
                '<code>python tools/so_xac_minh_nguon.py --quet &lt;file&gt;</code>.</p></div>')
    if not da_rut:
        return ""
    def _nhan(r):
        if r.get("rut_va_thay"):
            return ("đã rút &amp; đăng lại bản sửa",
                    "Trích dẫn vẫn dùng được, nhưng số liệu phải lấy từ BẢN ĐÃ SỬA "
                    "(thường cùng DOI/PMID).")
        if r["tinh_trang"] == "retracted":
            return "đã bị rút", "Không dùng kết luận của bài này."
        return "có quan ngại (EoC)", "Chưa kết luận — đọc lại trước khi dùng."

    hang = ""
    for r in da_rut:
        nhan, viec = _nhan(r)
        tb = (f'<span class="doi">thông báo: {esc(r["thong_bao"])}</span>'
              if r.get("thong_bao") else "")
        hang += (f'<li><b>{esc(r["loai"])}:{esc(r["gia_tri"])}</b> — <em>{nhan}</em>'
                 f'<span class="doi">{esc(r["tieu_de"])}</span>'
                 f'<span class="doi">{viec}</span>{tb}'
                 f'<span class="doi">sổ ghi {esc(r["kiem_luc"])} · nguồn '
                 f'{esc(r["nguon"])}</span></li>')
    # Tiêu đề phải nói ĐÚNG mức nặng. Một gói chỉ chứa bài "rút &amp; đăng lại" mà bị
    # gắn nhãn "không dùng" là cảnh báo sai về trích dẫn hợp lệ — và cảnh báo sai làm
    # hỏng giá trị của cảnh báo đúng.
    chi_rut_va_thay = all(r.get("rut_va_thay") for r in da_rut)
    tieu_de = ("Nguồn đã rút &amp; đăng lại bản sửa — đối chiếu số liệu trước khi dùng"
               if chi_rut_va_thay
               else "Nguồn đã bị rút — không dùng kết luận này trước khi đối chiếu")
    return (f'<div class="rutbai"><h3>{tieu_de} ({len(da_rut)} nguồn)</h3>'
            '<p class="sub">“Rút và thay” nghĩa là bài đã được sửa rồi đăng lại: việc cần làm là '
            'đối chiếu số liệu với bản đã sửa, KHÔNG phải bỏ mục đi. Máy không tự gỡ mục nào.</p>'
            f'<ul>{hang}</ul></div>')


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


# Khoá cấp 1 HỢP LỆ của DATA.summary — PHẢI khớp verify_dashboard.py::KHOA_SUMMARY_HOP_LE.
# Sửa danh sách này mà không sửa CẢ HAI nơi là tái lập đúng lỗi mà nó sinh ra để chặn.
KHOA_SUMMARY_HOP_LE = {"conclusion", "doNow", "dontDo", "redFlags"}


def khoi_khoa_summary_la(summary: dict) -> str:
    """Dải cảnh báo: DATA.summary có khoá LẠ — nội dung dưới khoá đó bị VỨT ÂM THẦM.

    VÌ SAO Ở ĐÂY (2026-09-04, Workflow đối kháng đa-agent vòng 3). verify_dashboard.py
    đã CHẶN CỨNG lỗi này từ 18/08/2026 (kiem_khoa_summary, BH61) — nhưng bản chặn đó
    chỉ chạy trong dây chuyền CÓ QUA CỔNG (`xuat_goi_cap_nhat.py --online`). File này
    tự nó KHÔNG kiểm gì cả: `summary.get('redFlags', [])`/`get('doNow', [])`/
    `get('dontDo', [])` coi khoá SAI TÊN (vd `notDo` thay vì `dontDo`) y hệt khoá VẮNG
    MẶT — trả về [] êm ru, không lỗi/cảnh báo nào — nên khi công cụ này được gọi
    ĐỘC LẬP (không qua cổng, vd chạy tay để soát lại một bản đã xuất), nó vẫn có thể
    sinh trang "bản đọc" với panel an toàn RỖNG mà không một dấu hiệu nào lộ ra.
    Ca thật đã xảy ra HAI LẦN (BH61): mất "KHÔNG ngừng opioid ĐỘT NGỘT ở người dùng
    dài hạn" và một cảnh báo ESA-hemoglobin.

    Đây là lớp phòng thủ THỨ HAI, không thay cổng — cổng vẫn là nơi CHẶN XUẤT.
    """
    la = sorted(set(summary) - KHOA_SUMMARY_HOP_LE)
    if not la:
        return ""
    ds = "".join(f"<li><b>{esc(k)}</b></li>" for k in la)
    return (
        '<div class="rutbai"><h3>DATA.summary có khoá LẠ — nội dung có thể đã bị vứt âm thầm '
        f'({len(la)} khoá)</h3>'
        '<p class="sub">Khoá hợp lệ CHỈ gồm conclusion/doNow/dontDo/redFlags — nội dung nằm '
        'dưới một khoá SAI TÊN (vd gõ nhầm <code>notDo</code> thay vì <code>dontDo</code>) '
        'không hiện ra ở đâu trên trang này, kể cả panel "Không nên, hoặc chưa nên đổi" bên '
        'dưới có thể đang RỖNG dù dữ liệu gốc có nội dung. Sửa lại đúng tên khoá trong '
        'dashboard rồi xuất lại — máy không tự đoán khoá đúng.</p>'
        f'<ul>{ds}</ul></div>'
    )


def build_page(data: dict, source_name: str, src: Path | None = None) -> str:
    meta = data.get("meta", {})
    summary = data.get("summary", {})
    items = data.get("items", [])

    # CHỈ nhận hiệu số dạng TỶ SỐ lên trục log. SỬA 16/09/2026: "ba giá trị dương" KHÔNG đủ để
    # là tỷ số — chênh lệch toàn dương (SMD 0,69) từng lọt lên trục này. Nay còn phải được xếp
    # thang TỶ SỐ theo `effect_scale` (khai tường minh hoặc suy từ nhãn thước đo). Tỷ số có giá
    # trị ≤ 0 không tồn tại trên thang log nên vẫn xuống danh sách không-biểu-đồ như cũ.
    def _ratio(it: dict) -> bool:
        e = it.get("effect") or {}
        if effect_scale(e) != "ratio":
            return False
        vals = [e.get("hr"), e.get("lo"), e.get("hi")]
        return all(isinstance(v, (int, float)) and v > 0 for v in vals)

    # Hiệu số CHÊNH LỆCH đủ ba giá trị hữu hạn ⇒ mục riêng trên thang tuyến tính, vạch 0.
    def _diff(it: dict) -> bool:
        e = it.get("effect") or {}
        if effect_scale(e) != "difference":
            return False
        vals = [e.get("hr"), e.get("lo"), e.get("hi")]
        return all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)
                   for v in vals)

    eff_items = [i for i in items if _ratio(i)]
    diff_items = [i for i in items if _diff(i)]
    bounds = []
    for i in eff_items:
        e = i["effect"]
        bounds += [e.get("lo"), e.get("hi")]
    ax = LogAxis.fit([b for b in bounds if b])

    # Chỉ mục CÓ hiệu số định lượng mới lên biểu đồ. SỬA 16/09/2026: khi nguồn khai rõ
    # `favors` VÀ khoảng tin cậy không chạm vạch 1,0, xếp mục THEO ĐÚNG `favors` (dùng
    # CHUNG `_ratio_favors_decided` với `plot_row` — nhãn "Gây hại" và dải xếp mục phải khớp
    # nhau, không được label một đằng xếp một nẻo). Khi `favors` vắng mặt (hoặc CI còn chạm
    # vạch 1,0), GIỮ NGUYÊN luật vị trí cũ — chia theo phía của khoảng tin cậy so với vạch
    # 1,0 — để không đổi hành vi của mọi dashboard đã xuất bản chưa khai `favors`.
    support, against = [], []
    for i in eff_items:
        e = i["effect"]
        decided = _ratio_favors_decided(e)
        if decided is True:
            support.append(i)
        elif decided is False:
            against.append(i)
        elif e.get("hi") and e["hi"] < 1.0 and i.get("decision") != "notyet":
            support.append(i)
        else:
            against.append(i)

    # Mục không có hiệu số (guideline, đồng thuận, chiến lược…) liệt kê riêng, gọn.
    no_eff = [i for i in items if not _ratio(i) and not _diff(i)]
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
        def _src(r):
            # Mục không có hiệu số định lượng chỉ hiện tiêu đề + nguồn, nên nhãn
            # «mới thẩm định trên tóm tắt» phải gắn ngay ở đây — nếu không nó
            # biến mất khỏi đúng trang mà bác sĩ đọc. Cùng lý do, định danh
            # truy nguyên (PMID/DOI/URL) cũng phải gắn ở đây — đường render
            # riêng cho mục "không có hiệu số" (guideline/consensus) này KHÔNG
            # đi qua plot_row(), nên bản vá PMID của plot_row() không tự lan
            # sang đây (phát hiện khi dựng dashboard Suy tim HFnrEF 2026-09-07:
            # ITEM-01 là guideline, đi qua đúng nhánh này, vẫn thiếu PMID sau
            # khi plot_row() đã được vá).
            s = esc(r.get("source", ""))
            if r.get("appraisalCompleteness") == "partial":
                s += (' · <span class="partial">thẩm định trên tóm tắt — '
                      'chưa đọc toàn văn</span>')
            ident = r.get("pmid") or r.get("doi") or r.get("url")
            if ident:
                label_id = "PMID" if r.get("pmid") else ("DOI" if r.get("doi") else "URL")
                s += f" · {esc(f'{label_id} {ident}')}"
            return s
        lis = "".join(
            f'<li><b>{esc(normalize_title(r.get("title","")))}</b>'
            f'<span>{_src(r)}</span></li>' for r in rows)
        return (f'<div class="noeff {tone}"><h3>{esc(heading)} '
                f'<span class="cnt">{len(rows)}</span></h3><ul>{lis}</ul></div>')

    noeff_html = "".join([
        dec_block("apply", "Áp dụng ngay"),
        dec_block("consider", "Cân nhắc chọn lọc"),
        dec_block("notyet", "Chưa đủ để đổi thực hành"),
    ])

    # ── Hiệu số CHÊNH LỆCH: mục riêng, thang tuyến tính, vạch 0 ──
    # Trang KHÔNG có chênh lệch thì mọi phần dưới đây rỗng và trang giữ nguyên từng byte như
    # trước bản sửa (mục lục 5 mục, lời dẫn cũ, CSS cũ).
    def diff_tick_label(t: float) -> str:
        if t == 0:
            return "0"
        return ("−" if t < 0 else "") + vn_num(abs(t)).rstrip("0").rstrip(",")

    def diff_field(rows: list, band_label: str) -> str:
        vals = [r["effect"][k] for r in rows for k in ("hr", "lo", "hi")]
        dax = LinearAxis.fit(vals)
        dticks = "".join(
            f'<i class="{"mark" if t == 0 else ""}" style="left:{dax.pos(t):.2f}%">{diff_tick_label(t)}</i>'
            for t in dax.ticks())
        head = ('<div class="axis-head"><div class="colcap" style="text-align:left">Nghiên cứu · so sánh</div>'
                f'<div class="scale">{dticks}</div>'
                '<div class="colcap">Quyết định</div></div>')
        body = "".join(plot_row_diff(r, dax) for r in rows)
        return (f'<div class="field"><div class="field-inner">{head}'
                f'<div class="band b-diff"><span>{esc(band_label)}</span><s></s></div>'
                f'{body}</div></div>')

    diff_html = ""
    if diff_items:
        # Chênh lệch CHUẨN HOÁ (SMD) không mang đơn vị ⇒ chung MỘT thang, so được với nhau.
        # Chênh lệch có đơn vị (điểm, mmHg, %) ⇒ mỗi mục MỘT thang riêng.
        chuan_hoa, rieng = [], []
        for i in diff_items:
            cum = measure_scale_match((i.get("effect") or {}).get("measure"))[1]
            (chuan_hoa if cum in STANDARDIZED_DIFF_TERMS else rieng).append(i)
        khung = []
        if chuan_hoa:
            khung.append(diff_field(chuan_hoa, "Chênh lệch chuẩn hoá (SMD) — các mục dùng chung một thang"))
        for i in rieng:
            nhan = i["effect"].get("measure") or "Hiệu số chênh lệch"
            khung.append(diff_field([i], f"{nhan} — thang riêng của mục này"))
        diff_html = f"""<section class="sec" id="chenhlech">
  <div class="sec-head"><h2>4. Hiệu số dạng chênh lệch</h2><p>SMD, MD, RD — thang tuyến tính, vạch 0 ở giữa</p></div>
  <p class="diffnote">Hiệu số chênh lệch không đặt được lên trục log ở mục 2 và 3: giá trị «không khác
  biệt» của chúng là 0, không phải 1,0. Các chênh lệch chuẩn hoá (SMD) dùng chung một khung nên so
  được với nhau; chênh lệch có đơn vị (điểm, mmHg, %) thì mỗi mục một thang riêng — đừng so độ dài
  thanh giữa hai khung. Chiều có lợi tuỳ kết cục (điểm đau giảm là tốt, điểm chất lượng sống tăng là
  tốt), nên đọc theo chú thích của nguồn, không suy từ phía trái hay phải của vạch.</p>
  {"".join(khung)}
  <div class="legend">
    <div><span class="k-dot"></span>ước lượng điểm</div>
    <div><span class="k-bar"></span>khoảng tin cậy 95%</div>
    <div><span class="k-nl"></span>vạch 0 — không khác biệt</div>
  </div>
</section>

"""

    deck_truc = ("Mọi hiệu số nằm trên cùng một trục thang log, vạch 1,0 ở giữa — mặc định bên trái là\n"
                 "  có lợi, bên phải là bất lợi; khi nguồn khai rõ chiều ngược lại, mục xếp và gắn nhãn\n"
                 "  theo đúng khai báo đó, không theo vị trí.")
    if diff_items:
        deck_truc = ("Hiệu số dạng tỷ số (HR, RR, OR) nằm trên cùng một trục thang log, vạch 1,0 ở giữa —\n"
                     "  mặc định bên trái là có lợi, bên phải là bất lợi (theo đúng khai báo của nguồn khi\n"
                     "  chiều ngược lại). Hiệu số dạng chênh lệch (SMD, MD, RD) có mục riêng trên thang\n"
                     "  tuyến tính, vạch 0.")
    nav_chenh = '  <a href="#chenhlech">4. Hiệu số dạng chênh lệch</a>\n' if diff_items else ""
    so_khac = 5 if diff_items else 4
    so_vn = so_khac + 1

    css = CSS + (CSS_CHENH_LECH if diff_items else "")
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
  sau. {deck_truc}</p>
  <div class="readout">
    <div><b>{len(items)}</b><span>mục đã xác minh</span></div>
    <div><b class="ok">{n_apply}</b><span>áp dụng ngay</span></div>
    <div><b class="ok">{n_pmid}/{len(items)}</b><span>mục có định danh truy nguyên</span></div>
    <div><b class="ok">{len(eff_items) + len(diff_items)}</b><span>mục có hiệu số định lượng</span></div>
  </div>
</header>

{khoi_khoa_summary_la(summary)}
{khoi_rut_bai(src) if src else ''}
{khoi_mau_thuan(src) if src else ''}

<nav class="nav" aria-label="Mục lục">
  <a href="#lam">1. Việc cần làm</a>
  <a href="#ungho">2. Chứng cứ ủng hộ</a>
  <a href="#khong">3. Không ủng hộ hoặc gây hại</a>
{nav_chenh}  <a href="#khac">{so_khac}. Khuyến cáo và đồng thuận</a>
  <a href="#vn">{so_vn}. Áp dụng tại Việt Nam</a>
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
  {field(support, 'Chiều có lợi theo nguồn báo cáo — mặc định bên trái vạch 1,0 khi chưa khai favors', 'benefit')}
  <div class="legend">
    <div><span class="k-dot"></span>ước lượng điểm</div>
    <div><span class="k-bar"></span>khoảng tin cậy 95%</div>
    <div><span class="k-nl"></span>vạch 1,0 — không khác biệt</div>
    <div>Thanh càng dài, độ chắc chắn càng thấp</div>
  </div>
</section>

<section class="sec" id="khong">
  <div class="sec-head"><h2>3. Chứng cứ không ủng hộ, hoặc gây hại</h2><p>chiều bất lợi theo nguồn báo cáo — mặc định bên phải vạch 1,0 khi chưa khai favors</p></div>
  {field(against, 'Chiều bất lợi theo nguồn báo cáo, hoặc chạm/vượt vạch 1,0 khi chưa khai favors', 'harm')}
</section>

{diff_html}<section class="sec" id="khac">
  <div class="sec-head"><h2>{so_khac}. Khuyến cáo và đồng thuận</h2><p>mục không có hiệu số định lượng để đặt lên trục</p></div>
  <div class="noeffs">{noeff_html}</div>
</section>

<section class="sec vn" id="vn">
  <div class="sec-head"><h2>{so_vn}. Áp dụng tại Việt Nam</h2><p>mục cần đối chiếu nguồn lực và quy trình tại đơn vị</p></div>
  <div class="flags">
    <h3>Cần xác nhận tại đơn vị trước khi áp dụng</h3>
    <ul>{''.join(f"<li><b>{esc(i.get('title',''))}</b> — {esc(i.get('vn',''))}</li>" for i in vn_checks) or '<li>Không có mục nào cần xác nhận tại đơn vị.</li>'}</ul>
  </div>
</section>

<footer>
  <pre class="stamp" style="white-space:pre-wrap;border:1px solid #d1d5db;padding:8px;border-radius:6px;background:#f8fafc">{khoi_do_phu()}</pre>
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
/* Dải RÚT BÀI — nặng nhất trong các cảnh báo về độ tin cậy của tài liệu, nên dùng
   tông đỏ và đứng trên dải mâu thuẫn. Vẫn khác cờ đỏ lâm sàng ở chỗ nằm ngoài
   phần nội dung, ngay dưới đầu trang. */
.rutbai{background:var(--harm-soft);border-left:4px solid var(--harm);
padding:20px 24px;margin:26px 0 0}
.rutbai h3{margin:0 0 6px;font-size:16px;font-weight:700;color:var(--harm)}
.rutbai .sub{margin:0 0 14px;font-size:13.5px;line-height:1.55;color:var(--ink-2)}
.rutbai ul{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:13px}
.rutbai li{font-size:14.5px;line-height:1.55;color:var(--ink-2)}
.rutbai li b{color:var(--ink)}
.rutbai li em{font-style:normal;font-weight:700;color:var(--harm);text-transform:uppercase;
font-size:12.5px;letter-spacing:.04em}
.rutbai .doi{display:block;font-size:13px;color:var(--ink-3);margin-top:2px}
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
.trial .name small .partial{color:var(--caution);font-weight:700}
.noeff li span .partial{color:var(--caution);font-weight:700}
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

# Chỉ nối vào trang CÓ hiệu số chênh lệch — trang không có giữ nguyên CSS cũ từng byte.
CSS_CHENH_LECH = """
.band.b-diff span{color:var(--axis)}
.diffnote{margin:12px 0 0;max-width:78ch;font-size:14px;line-height:1.6;color:var(--ink-2)}
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
