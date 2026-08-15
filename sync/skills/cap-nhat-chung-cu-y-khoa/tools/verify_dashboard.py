#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_dashboard.py — Cổng kiểm liêm chính cho Web Dashboard EBM (Dark Analyst / Evidence Workbench).

Kiểm TRƯỚC KHI GIAO cho bác sĩ:
  - Mỗi item có ≥1 định danh truy nguyên (pmid hoặc doi).
  - Mỗi item có gradeLevel + decision + references.
  - (--strict-sources) Bắt buộc khai báo `DATA.standards`, ngày tìm kiếm còn mới,
    nguồn tìm kiếm, thứ bậc nguồn, chuẩn báo cáo/công cụ thẩm định; chặn `apply`
    nếu chứng cứ yếu/không phân hạng hoặc chỉ dựa đồng thuận.
  - Có disclaimer "Cần bác sĩ kiểm chứng".
  - Quét dấu hiệu PII (cảnh báo để người rà — không tự ý kết luận).
  - DOI kiểm ĐỊNH DẠNG luôn (offline, mọi lượt chạy); khi --online, còn PHÂN GIẢI THẬT
    qua Crossref API (vá 2026-07-12 — trước đây chỉ kiểm định dạng, DOI bịa/404 vẫn lọt
    qua cổng: tái hiện thật ở EBM_MASTER card EVID-2026-0270, DOI 10.1136/ard-2024-225452
    không tồn tại nhưng đúng định dạng regex nên PASS sạch).
  - (Tùy chọn --online) Tự XÁC MINH mỗi PMID phân giải đúng qua NCBI E-utilities
    (miễn phí, không cần key) → chống trích dẫn ảo PMID; đồng thời so khớp thô tiêu đề
    PubMed thật với nội dung item để dò TRÁO TRÍCH DẪN (PMID có thật nhưng lạc đề).
  - (--online) So NĂM item khai (dateVersion) với năm xuất bản THẬT của PMID (vá 2026-07-12
    — cùng ca EVID-2026-0270: PMID 41826212 có thật nhưng là bản "2025 update" (2026), item
    lại khai dateVersion "2024" — cùng họ guideline nên tiêu đề trùng đủ từ khóa để KHÔNG bị
    heuristic tráo-trích-dẫn ở trên bắt được; đây là dạng lỗi RIÊNG — "đúng họ, sai phiên
    bản/năm" — cần so năm trực tiếp mới bắt được).
  - (--online, SỬA 2026-07-22, vòng lặp kiểm tra-hoàn thiện vòng 10, phát hiện MEDIUM): item
    CHỈ khai `url` (không pmid/doi) nay CŨNG được xác minh mở được thật (GET nhẹ) — trước bản
    vá này, url được chấp nhận ngang pmid/doi để qua cổng truy nguyên nhưng KHÔNG BAO GIỜ được
    xác minh online dù chạy --online, dù docstring cũ chỉ liệt kê PMID/DOI mà không nói rõ url
    bị loại hoàn toàn khỏi mọi lượt xác minh trực tuyến.

Cách dùng:
    python3 verify_dashboard.py <dashboard.html>            # chỉ kiểm cấu trúc (offline)
    python3 verify_dashboard.py <dashboard.html> --online --strict-sources
        # + xác minh PMID/DOI trên mạng + cổng nguồn nghiêm ngặt trước phát hành

Mã thoát: 0 = PASS (không lỗi cứng), 1 = FAIL.
Lỗi cứng: item thiếu cả pmid lẫn doi; PMID/DOI sai định dạng; thiếu disclaimer; item thiếu
  gradeLevel/decision; items[] rỗng (TRỪ artifact tự khai báo kind:'cong-cu' = công cụ hỗ
  trợ quyết định, không phải danh sách thẻ chứng cứ — vẫn bắt buộc disclaimer + kiểm PII/nội dung);
  khi --online: PMID KHÔNG xác minh được (kể cả do lỗi mạng) — fail-closed, không coi lỗi
  mạng là PASS (vá 2026-07-11, trước đây fail-open: PMID bịa lọt qua nếu quét đúng lúc mất mạng);
  khi --online: DOI có định dạng nhưng KHÔNG phân giải được qua Crossref — cùng nguyên tắc
  fail-closed (lỗi mạng khi tra Crossref → CẢNH BÁO, không chặn cứng — phân biệt "404 thật" và
  "Crossref tạm lỗi" bằng mã trạng thái HTTP, không đánh đồng như PMID).
Cảnh báo (không chặn): nghi PII; khi --online, PMID xác minh tồn tại nhưng tiêu đề PubMed
  không khớp nội dung item (nghi tráo trích dẫn — heuristic từ khóa, cần rà tay); khi --online,
  năm PubMed thật lệch >1 năm so với dateVersion item khai (nghi trích dẫn NHẦM PHIÊN BẢN/năm
  của cùng một họ guideline — rà tay, không tự sửa). Khi bật --strict-sources, các cảnh báo
  nguồn này được nâng thành lỗi cứng để không cần bác sĩ tự dò từng nguồn trước khi đọc dashboard.
"""
import argparse
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
from json import JSONDecodeError
from datetime import date, datetime
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


DISCLAIMER = "Cần bác sĩ kiểm chứng"
VALID_GRADE = {"high", "mod", "low", "vlow", "na"}
VALID_DECISION = {"apply", "consider", "notyet"}
# Audit 2026-07-11: docstring hứa "DOI kiểm định dạng" nhưng trước đây chỉ kiểm
# doi không rỗng — DOI bịa/gõ sai vẫn qua cổng nếu không kèm pmid. Regex chuẩn
# DOI (registrant 4+ số + '/' + suffix bất kỳ, theo chuẩn doi.org).
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
# Vá 2026-07-11 (vòng 9): PMID trước đây KHÔNG được kiểm định dạng gì cả — chuỗi bất kỳ
# (kể cả không phải số) qua cổng nếu không rỗng. PMID là số nguyên dương thuần (PubMed
# hiện dùng tới 8 chữ số, cho phép dư tới 9 để an toàn).
PMID_RE = re.compile(r"^\d{1,9}$")
KNOWN_DESIGNS = {"Guideline", "Meta", "RCT", "Cohort", "Consensus"}

# Họ thiết kế/nguồn nhận biết được, khớp theo TIỀN TỐ (không phân biệt hoa/thường).
# Thêm 12/08/2026 sau khi đo trên toàn bộ 60 dashboard: 35 item thuộc 23 loại nằm
# NGOÀI bộ 5 giá trị trên — trong đó có những nguồn quan trọng bậc nhất cho an toàn
# kê đơn như "Nhãn thuốc" (FDA — liều theo CrCl) và "Cảnh báo dược cảnh giác"
# (MHRA/EMA PRAC). Bộ cũ quá hẹp so với thực tế nguồn EBM, nên luật này tạo dương
# tính giả hàng loạt kể từ khi dây chuyền bật --strict-sources (11/08).
#
# Cách xử lý: KHÔNG nới thành chấp nhận chuỗi tự do (làm vậy thì luật vô nghĩa),
# mà phân tầng theo hậu quả — xem `design_khong_nhan_dien()`:
#   • item chỉ mô tả  → CẢNH BÁO (việc phân tầng thật nằm ở gradeLevel/gradeSource,
#     vốn đã có luật riêng chặt hơn);
#   • item decision='apply' → CHẶN (đang định áp dụng dựa trên nguồn không phân
#     tầng được thì phải nói rõ nguồn là loại gì).
DESIGN_FAMILIES = (
    "guideline", "hướng dẫn", "khuyến cáo",
    "meta", "phân tích gộp", "tổng quan hệ thống", "systematic",
    "rct", "thử nghiệm", "trial",
    "cohort", "đoàn hệ",
    "case-control", "bệnh-chứng", "case series", "ca lâm sàng", "chuỗi ca",
    "cross-sectional", "cắt ngang",
    "consensus", "đồng thuận",
    "nhãn thuốc", "drug label", "tờ hướng dẫn sử dụng",
    "cảnh báo", "dược cảnh giác", "drug safety", "đặc tả nguy cơ",
    "rà soát an toàn", "kết luận tín hiệu an toàn", "tín hiệu an toàn",
    "phê duyệt", "regulatory",
    "pk", "dược động", "cơ chế",
    "so sánh đa-guideline", "so sánh guideline",
)


def design_khong_nhan_dien(design):
    """True nếu `design` không thuộc họ nào nhận biết được (khớp theo tiền tố)."""
    d = (design or "").strip().lower()
    if not d:
        return True
    if design in KNOWN_DESIGNS:
        return False
    return not any(d.startswith(p) for p in DESIGN_FAMILIES)
STRICT_SOURCE_MAX_AGE_DAYS = 180
SOURCE_GATE_USER_AGENT = "EBM-Copilot-source-verifier/1.0"
_HTTPS_CONTEXT = None


def _certifi_bundle_path():
    """Ưu tiên kho CA `certifi`; nếu chạy ngoài venv, thử bundle trong venv chuẩn."""
    try:
        import certifi  # type: ignore
        return certifi.where()
    except Exception:
        lib_dir = Path.home() / ".ebm-venv" / "lib"
        matches = sorted(lib_dir.glob("python*/site-packages/certifi/cacert.pem"))
        return str(matches[-1]) if matches else None


def _https_context():
    global _HTTPS_CONTEXT
    if _HTTPS_CONTEXT is not None:
        return _HTTPS_CONTEXT
    cafile = _certifi_bundle_path()
    _HTTPS_CONTEXT = ssl.create_default_context(cafile=cafile) if cafile else ssl.create_default_context()
    return _HTTPS_CONTEXT


def source_urlopen(url, timeout=15):
    """Mở URL nguồn y khoa với CA rõ ràng để tránh lỗi SSL giả khi kiểm online."""
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": SOURCE_GATE_USER_AGENT})
    return urllib.request.urlopen(req, timeout=timeout, context=_https_context())


def configure_utf8_stdio():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def extract_data_block(html):
    """Lấy đoạn từ 'const DATA' tới hết khối (marker hoặc cân bằng ngoặc)."""
    i = html.find("const DATA")
    if i == -1:
        return None
    end = html.find("HẾT KHỐI DATA", i)
    return html[i:end] if end != -1 else html[i:i + 60000]


def split_items(data_block):
    """Tách từng object item theo mốc bắt đầu {id:'...' hoặc {id:"..."."""
    items_pos = data_block.find("items:")
    seg = data_block[items_pos:] if items_pos != -1 else data_block
    starts = [m.start() for m in re.finditer(r"\{\s*id\s*:\s*['\"]", seg)]
    chunks = []
    for k, s in enumerate(starts):
        e = starts[k + 1] if k + 1 < len(starts) else len(seg)
        chunks.append(seg[s:e])
    return chunks


def field(chunk, name):
    """Lấy giá trị chuỗi của khoá `name` trong một đoạn JS.

    VÁ 12/08/2026 — dương tính giả nghiêm trọng: bản cũ dùng lớp ký tự
    `[^'\"]*`, tức DỪNG ở dấu nháy loại kia nằm bên trong chuỗi. Giá trị rất
    thường gặp như

        gradeSource:'"Usually Not Appropriate" — phân loại chính thức của ACR'

    bị cắt thành chuỗi RỖNG (khớp `'` mở, 0 ký tự, rồi `\"`), khiến cổng báo
    "[ITEM-05] thiếu gradeSource" trong khi dữ liệu CÓ đầy đủ. Trích dẫn nguyên
    văn phân hạng của nguồn — đúng thứ `gradeSource` sinh ra để chứa — gần như
    luôn có dấu nháy kép, nên lỗi này nhắm thẳng vào trường quan trọng nhất.

    Bản mới bám đúng dấu nháy MỞ và cho phép dấu nháy loại kia nằm trong, có xử
    lý ký tự thoát. Hệ quả: nhiều trường trước đây bị cắt cụt nay trả về đủ —
    các luật đọc chúng vì thế mới chấm trên nội dung thật.
    """
    m = re.search(
        name + r"""\s*:\s*(?:'((?:[^'\\]|\\.)*)'|"((?:[^"\\]|\\.)*)")""",
        chunk,
    )
    if not m:
        return None
    return m.group(1) if m.group(1) is not None else m.group(2)


def _find_matching_brace(text, open_idx):
    depth = 0
    instr = None
    esc = False
    for i in range(open_idx, len(text)):
        c = text[i]
        if instr:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == instr:
                instr = None
            continue
        if c in "\"'`":
            instr = c
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i
    return -1


def object_after_key(text, key):
    m = re.search(r"(?<![\w$])" + re.escape(key) + r"\s*:\s*\{", text)
    if not m:
        return None
    start = text.find("{", m.end() - 1)
    end = _find_matching_brace(text, start)
    return text[start:end + 1] if end != -1 else None


def array_field(block, name):
    if not block:
        return []
    m = re.search(name + r"\s*:\s*\[([^\]]*)\]", block, re.S)
    if not m:
        return []
    # VÁ 14/08/2026 — GỘP chuỗi nối kiểu JS trước khi tách phần tử.
    # Mảng viết tay hay ngắt chuỗi dài bằng dấu cộng:
    #     references:["…EMA; 12 June 2026. "+"https://www.ema.europa.eu/…", "…"]
    # Bản cũ tách thành HAI phần tử ⇒ một tài liệu tham khảo biến thành hai, và một
    # trong hai chỉ là URL trần. Đo thật trên `AnToanThuoc_EMA_PRAC_20260614`: 4 phần
    # tử thay vì 3.
    # Quan trọng hơn con số: `build_dashboard_docx.py` ĐÃ được vá gộp chuỗi nối
    # (13/08), nên từ đó tới nay bộ dựng Word đọc 3 còn cổng đọc 4 — HAI PARSER CỦA
    # CÙNG MỘT DỮ LIỆU BẤT ĐỒNG. Đúng bài học BH20: vá một parser thì phải vá mọi
    # parser đọc cùng thứ đó.
    noi_dung = re.sub(r'"\s*\+\s*"', "", m.group(1))
    noi_dung = re.sub(r"'\s*\+\s*'", "", noi_dung)
    return [x.strip() for x in re.findall(r"['\"]([^'\"]+)['\"]", noi_dung) if x.strip()]


def _parse_exact_date(text):
    m = re.search(r"\b(20\d{2})[-/](\d{1,2})[-/](\d{1,2})\b", text or "")
    if not m:
        return None
    try:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3))).date()
    except ValueError:
        return None


# ── NGUỒN QUY PHẠM ───────────────────────────────────────────────────────────
# Thêm 12/08/2026. Vì sao cần: luật "apply phải có gradeLevel đủ mạnh" đúng với
# chứng cứ NGHIÊN CỨU, nhưng chặn oan một loại nguồn khác hẳn về bản chất —
# nguồn QUY PHẠM: guideline chính thức, nhãn thuốc của cơ quan quản lý, tiêu
# chuẩn phân loại. Chúng để gradeLevel='na' vì KHÔNG dùng thang GRADE, chứ
# không phải vì chứng cứ yếu.
#
# Rà 4 dashboard ngày 12/08 cho thấy hậu quả thật của việc không phân biệt: hạ
# `decision` của một CHỐNG CHỈ ĐỊNH (AASLD+APASL xác nhận độc lập) hay của NHÃN
# THUỐC FDA xuống "cân nhắc" là làm GIẢM an toàn, không phải tăng — đúng thứ mà
# cổng này sinh ra để ngăn.
#
# Chống lách: miễn trừ KHÔNG tự suy đoán hộ. Item phải hội đủ BA điều kiện, và
# hai trong số đó người soạn phải khai tường minh, kiểm toán được:
#   1) design thật sự là Guideline / Nhãn thuốc (Consensus KHÔNG BAO GIỜ đủ —
#      đồng thuận chuyên gia không phải văn bản quy phạm);
#   2) normativeBasis khai đúng MỘT loại quy phạm trong danh sách dưới;
#   3) gradeSource có nội dung — phân hạng hoặc nhận định NGUYÊN BẢN của nguồn.
# Miễn trừ chỉ áp cho gradeLevel='na' (nguồn không phân hạng). Nếu nguồn CÓ
# phân hạng và nói mức thấp ('low'/'vlow') thì vẫn chặn — đó là nguồn đã tự
# đánh giá là yếu, không thể viện cớ quy phạm.
NORMATIVE_BASES = {
    "contraindication",           # chống chỉ định
    "drug-label",                 # nhãn thuốc cơ quan quản lý (FDA/EMA/DAV…)
    "official-classification",    # tiêu chuẩn phân loại chính thức (vd ICHD của IHS)
    "guideline-strong-rec",       # khuyến cáo MẠNH của guideline chính thức
    "guideline-explicit-criteria",  # bộ tiêu chí tường minh (Beers, STOPP/START)
}

# design được coi là văn bản quy phạm. So khớp không phân biệt hoa/thường và cho
# phép hậu tố mô tả (vd "Guideline/tổng quan") — nhưng KHÔNG nhận "Consensus".
NORMATIVE_DESIGN_PREFIXES = ("guideline", "nhãn thuốc", "nhan thuoc")


# Dấu hiệu VĂN BẢN cho thấy nguồn tuyên bố khuyến cáo MẠNH. Cố ý đòi bằng chứng
# nguyên văn thay vì tin nhãn `normativeBasis`: nhãn thì ai gõ cũng được, còn câu
# trích từ nguồn thì phải có thật. Danh sách khớp quy ước của các hệ lớn —
# Endocrine Society/ACP ("we recommend" = mạnh, "we suggest" = yếu), GRADE 1A/1B/1C,
# và cách diễn đạt tiếng Việt đã dùng trong kho.
_MANH_RE = re.compile(
    r"we recommend|strong(ly)? recommend|strong recommendation|khuyến cáo mạnh|"
    r"mức độ mạnh|grade\s*1[abc]?\b|class\s*i\b|loại\s*i\b|(?<![a-z])1[abc](?![a-z])",
    re.I)
# Dấu hiệu NGƯỢC LẠI — nguồn tự nói CÓ ĐIỀU KIỆN/YẾU. Xuất hiện là KHÔNG miễn, kể
# cả khi câu khác trong cùng trường có chữ "recommend".
_CO_DIEU_KIEN_RE = re.compile(
    r"có điều kiện|conditional|we suggest|weak recommendation|khuyến cáo yếu|"
    r"grade\s*2[abc]?\b", re.I)


def _co_bang_chung_khuyen_cao_manh(grade_source):
    """`gradeSource` có TRÍCH ĐƯỢC bằng chứng nguồn tuyên bố khuyến cáo MẠNH không?

    Fail-closed: không có bằng chứng → False. Có dấu hiệu CÓ ĐIỀU KIỆN → False luôn,
    vì khi hai dấu hiệu cùng xuất hiện thì mức thấp hơn mới là mức an toàn để tin.
    """
    t = grade_source or ""
    if not t.strip():
        return False
    if _CO_DIEU_KIEN_RE.search(t):
        return False
    return bool(_MANH_RE.search(t))


def normative_exemption(design, grade, normative_basis, grade_source):
    """Item có được miễn luật 'apply cần gradeLevel mạnh' vì là nguồn QUY PHẠM không?

    Trả về (được_miễn, lý_do_không_miễn). Lý do dùng để báo cho người soạn biết
    còn thiếu gì, thay vì im lặng từ chối.
    """
    # VÁ 14/08/2026 — TÁCH HAI TRỤC MÀ GRADE CỐ Ý TÁCH.
    # Bản cũ: `grade != "na"` ⇒ chặn thẳng. Nhưng GRADE có HAI trục ĐỘC LẬP:
    #   • ĐỘ MẠNH khuyến cáo : strong (1) vs conditional (2)
    #   • CHẤT LƯỢNG chứng cứ: high / moderate / low / very low
    # Một khuyến cáo MẠNH trên chứng cứ chất lượng THẤP là kết quả GRADE hợp lệ và
    # phổ biến — đúng những tình huống đe doạ tính mạng mà bỏ sót thì tai hoạ.
    # Ca thật: `SuyTim_NoiTiet ITEM-05` (nhận biết khủng hoảng thượng thận). Hướng dẫn
    # Endocrine Society (PMID 26760044, doi:10.1210/jc.2015-1710) dùng GRADE và viết
    # "We recommend" = khuyến cáo MẠNH, trong khi chất lượng chứng cứ chỉ ở mức thấp.
    # Cổng cũ ép một lựa chọn SAI CẢ HAI ĐƯỜNG: giữ `low` thì bị chặn dù nguồn nói
    # MẠNH; đổi sang `na` thì NÓI SAI về nguồn (nguồn CÓ phân hạng).
    #
    # Nay: chứng cứ chất lượng thấp VẪN được miễn NẾU nguồn tuyên bố khuyến cáo MẠNH,
    # và điều đó phải có BẰNG CHỨNG VĂN BẢN trong `gradeSource` — không chấp nhận chỉ
    # dán nhãn. Khuyến cáo CÓ ĐIỀU KIỆN (ACR "conditional") vẫn bị chặn như cũ.
    # Kiểm `design` TRƯỚC mọi nhánh khác. Bản đầu của chính bản vá này đặt nhánh
    # low/vlow lên trên và trả True sớm ⇒ MỞ LẠI đúng lỗ hổng BH03 đã bịt: một văn
    # bản `Consensus` gõ thêm nhãn `guideline-strong-rec` là đi qua cổng. Bắt được
    # nhờ ca biên "Consensus → PHẢI chặn" trong bộ kiểm 7 ca.
    d = (design or "").strip().lower()
    if not any(d.startswith(p) for p in NORMATIVE_DESIGN_PREFIXES):
        return False, None  # không phải văn bản quy phạm → giữ luật gốc
    if grade != "na":
        if grade in ("low", "vlow") and normative_basis == "guideline-strong-rec" \
                and _co_bang_chung_khuyen_cao_manh(grade_source):
            return True, None
        return False, None  # nguồn tự phân hạng thấp mà KHÔNG tuyên bố mạnh → không miễn
    if not normative_basis:
        return False, ("thiếu normativeBasis — nguồn quy phạm muốn giữ 'apply' phải khai "
                       "tường minh loại quy phạm (%s)" % "/".join(sorted(NORMATIVE_BASES)))
    if normative_basis not in NORMATIVE_BASES:
        return False, ("normativeBasis=%r không hợp lệ (cần %s)"
                       % (normative_basis, "/".join(sorted(NORMATIVE_BASES))))
    if not grade_source:
        return False, ("có normativeBasis nhưng thiếu gradeSource — phải ghi phân hạng "
                       "hoặc nhận định NGUYÊN BẢN của nguồn")
    return True, None


def strict_source_checks(data_block, items, *, today=None):
    """Cổng nguồn nghiêm ngặt cho dashboard thật.

    Mục tiêu là giảm tối đa việc bác sĩ phải tự dò từng nguồn: dashboard phải khai báo
    chiến lược cập nhật, nguồn tìm kiếm và từng item phải đủ truy nguyên/chất lượng trước
    khi được phát hành. Cổng này không thay quyết định lâm sàng cuối cùng.
    """
    today = today or date.today()
    errors, warns, oks = [], [], []
    standards = object_after_key(data_block, "standards")
    # KHAI BÁO "CHƯA GHI NHẬN PROVENANCE" — thêm 14/08/2026.
    # 44/62 gói không có khối `standards`, rải đều từ 06→08/2026 (không có mốc ngày nào
    # để suy). Trước bản vá này chúng sinh 10 lỗi cứng GIỐNG HỆT một gói lẽ ra phải có
    # mà cố tình bỏ — tức cổng KHÔNG phân biệt được **chưa khai** với **có vấn đề**,
    # đúng lỗi BH08. Một bức tường 10 lỗi × 44 gói cũng dạy người đọc bỏ qua màu đỏ.
    # Nay: gói được phép khai THẲNG là provenance chưa từng ghi nhận. Đó là nói ra một
    # sự thật kiểm chứng được (file không có khối standards), KHÔNG phải bịa chiến lược
    # tìm kiếm — bịa provenance mới là thứ tuyệt đối cấm.
    # Đổi lại, cổng nói to rằng gói ấy KHÔNG tái lập và KHÔNG kiểm toán được.
    if standards and re.search(r"\bprovenanceUnknown\s*:\s*true\b", standards):
        ly_do = field(standards, "provenanceUnknownLyDo") or ""
        if not ly_do.strip():
            errors.append("Khai provenanceUnknown nhưng THIẾU `provenanceUnknownLyDo` — "
                          "phải nói rõ vì sao không ghi nhận được chiến lược tìm kiếm.")
        else:
            warns.append("PROVENANCE CHƯA GHI NHẬN (gói tự khai): không tái lập và không "
                         "kiểm toán được chiến lược tìm kiếm của gói này — %s. Đây là "
                         "'chưa biết', KHÔNG phải 'đã kiểm đủ'; gói mới BẮT BUỘC khai "
                         "DATA.standards đầy đủ." % ly_do[:120])
        # Vẫn chấm TIẾP mọi luật an toàn cấp item ở dưới (bài học 12/08) — chỉ bỏ phần
        # đòi từng trường của hợp đồng nguồn, vì gói đã khai là không có.
        bo_qua_truong = True
        standards = ""
    else:
        bo_qua_truong = False
    if not bo_qua_truong and not standards:
        errors.append("THIẾU DATA.standards — không có hợp đồng nguồn/độ mới/chuẩn thẩm định. "
                      "Gói cũ chưa từng ghi nhận provenance thì khai thẳng "
                      "`provenanceUnknown: true` + `provenanceUnknownLyDo` thay vì bịa.")
        # KHÔNG return sớm (sửa 12/08/2026). Bản cũ thoát ngay tại đây, nên với
        # dashboard thiếu khối siêu dữ liệu thì TOÀN BỘ luật an toàn cấp item —
        # `apply` trên gradeLevel yếu, `apply` chỉ dựa Consensus — KHÔNG BAO GIỜ
        # được chạy. Hậu quả là một ảo ảnh nguy hiểm: cổng báo đúng "1 lỗi cứng",
        # người đọc kết luận "chỉ thiếu siêu dữ liệu, nội dung lâm sàng không sai"
        # — trong khi cổng chưa hề đọc tới một item nào để có căn cứ nói vậy.
        # Kết luận sai đó đã bị ghi vào CLAUDE.md ngày 11/08 và lan sang cả cách
        # xuat_goi_cap_nhat.py phân loại "chỉ cảnh báo" vs "chặn xuất".
        # Nay: ghi nhận lỗi thiếu hợp đồng nguồn rồi CHẤM TIẾP, để luật an toàn
        # phủ mọi dashboard bất kể có khối standards hay không.
        standards = ""

    required_fields = {
        "frame": "khung câu hỏi",
        "sourceHierarchy": "thứ bậc nguồn",
        "reporting": "chuẩn báo cáo",
        "appraisal": "công cụ thẩm định",
        "currency": "ngày cập nhật/tìm kiếm",
        "safety": "an toàn",
        "vietnamFit": "tính phù hợp Việt Nam",
    }
    # Gói đã khai THẲNG là chưa từng ghi nhận provenance ⇒ không đòi từng trường nữa.
    # Đòi tiếp chỉ tạo 10 dòng đỏ lặp lại cùng một sự thật đã được nói ra ở trên.
    for key, label in ({} if bo_qua_truong else required_fields).items():
        if not field(standards, key):
            errors.append("DATA.standards thiếu %s (%s)." % (key, label))

    search_sources = array_field(standards, "searchSources")
    if not bo_qua_truong and len(search_sources) < 2:
        errors.append("DATA.standards.searchSources cần ≥2 nguồn tìm kiếm độc lập (vd PubMed + guideline/Cochrane/nhãn thuốc).")

    currency = field(standards, "currency") or field(data_block, "updated")
    currency_date = _parse_exact_date(currency) or _parse_exact_date(field(data_block, "updated"))
    if not currency_date:
        (warns if bo_qua_truong else errors).append(
            "Không thấy ngày tìm kiếm/cập nhật dạng YYYY-MM-DD trong DATA.standards.currency "
            "hoặc DATA.meta.updated.")
    else:
        age = (today - currency_date).days
        if age < 0:
            errors.append("Ngày tìm kiếm/cập nhật ở tương lai: %s." % currency_date.isoformat())
        elif age > STRICT_SOURCE_MAX_AGE_DAYS:
            errors.append(
                "Nguồn không còn đủ mới: ngày tìm kiếm/cập nhật %s đã %d ngày "
                "(ngưỡng strict %d ngày)." % (currency_date.isoformat(), age, STRICT_SOURCE_MAX_AGE_DAYS)
            )
        else:
            oks.append("Nguồn còn mới: ngày tìm kiếm/cập nhật %s (%d ngày)." % (currency_date.isoformat(), age))

    if not bo_qua_truong and "gates" not in standards:
        errors.append("DATA.standards thiếu gates[] — không có cổng liêm chính nguồn trước phát hành.")

    for ch in items:
        iid = field(ch, "id") or "(?)"
        design = field(ch, "design")
        grade = field(ch, "gradeLevel")
        dec = field(ch, "decision")
        source = field(ch, "source")
        org = field(ch, "org")
        date_version = field(ch, "dateVersion")
        grade_source = field(ch, "gradeSource")
        pmid = field(ch, "pmid")
        doi = field(ch, "doi")
        url = field(ch, "url")

        if not source:
            errors.append("[%s] thiếu source — không xác định được tài liệu gốc." % iid)
        if not org:
            warns.append("[%s] thiếu org — nên ghi tổ chức/tạp chí/hội chuyên môn phát hành." % iid)
        if not date_version:
            errors.append("[%s] thiếu dateVersion — không thể đánh giá phiên bản/độ mới của nguồn." % iid)
        if not design:
            errors.append("[%s] thiếu design — không thể phân tầng độ tin cậy nguồn." % iid)
        elif design_khong_nhan_dien(design):
            # Nghiêm ở chỗ có hậu quả: chỉ CHẶN khi item đang định 'apply'.
            if dec == "apply":
                errors.append("[%s] decision='apply' nhưng design=%r không thuộc họ nguồn nào "
                              "nhận diện được — ghi rõ loại nguồn (vd Guideline, RCT, Cohort, "
                              "Nhãn thuốc, Cảnh báo dược cảnh giác) hoặc hạ quyết định."
                              % (iid, design))
            else:
                warns.append("[%s] design=%r không thuộc họ nguồn nhận diện được — nên ghi rõ "
                             "loại nguồn để phân tầng được độ tin cậy." % (iid, design))
        if not grade_source:
            errors.append("[%s] thiếu gradeSource — không thấy phân hạng/nhận định nguyên bản của nguồn." % iid)
        if "references" not in ch:
            errors.append("[%s] thiếu references[] — strict-sources không cho phát hành." % iid)

        if dec == "apply" and grade in {"low", "vlow", "na"}:
            normative_basis = field(ch, "normativeBasis")
            duoc_mien, ly_do_thieu = normative_exemption(design, grade, normative_basis, grade_source)
            if duoc_mien:
                oks.append("[%s] 'apply' trên nguồn QUY PHẠM (%s, %s) — miễn luật gradeLevel, "
                           "đã khai tường minh và có phân hạng nguyên bản."
                           % (iid, design, normative_basis))
            elif ly_do_thieu:
                errors.append("[%s] decision='apply' nhưng gradeLevel=%r: %s." % (iid, grade, ly_do_thieu))
            else:
                errors.append("[%s] decision='apply' nhưng gradeLevel=%r — phải hạ xuống consider/notyet hoặc bổ sung nguồn mạnh hơn." % (iid, grade))
        # AI ĐÃ CHẤM MỨC NÀY? — thêm 14/08/2026.
        # Đo trên toàn kho: 530 item có `gradeLevel` khác 'na', trong đó **249 (47%)
        # KHÔNG truy được về một tổ chức nào đã chấm**; 128 mục lấy mô tả THIẾT KẾ
        # ("RCT đa trung tâm, mù đôi") làm lý do cho mức, và 18 mục tự khai thẳng
        # "nguồn không nêu GRADE" mà vẫn mang mức `mod`/`low`.
        # `gradeLevel` là thứ bác sĩ HÀNH ĐỘNG THEO, nên một mức không truy được nguồn
        # gây hại ở MỌI lần đọc — khác rút bài vốn hiếm.
        # KIỂM KHAI BÁO, KHÔNG DÒ TỪ KHOÁ: bản đo đầu tiên của chính luật này đã dò tên
        # tổ chức trong `gradeSource` và đếm nhầm 18 mục có tên tổ chức trong câu PHỦ
        # ĐỊNH ("CHƯA được AASLD đưa vào khuyến cáo") thành "đã có tổ chức chấm" — đúng
        # lỗi BH28. Nên đòi một trường RIÊNG `gradeBy`, giống cách `normativeBasis` làm.
        if grade and grade != "na" and not field(ch, "gradeBy"):
            thieu = ("[%s] gradeLevel=%r nhưng KHÔNG khai `gradeBy` — ai đã chấm mức này? "
                     "Khai tên tổ chức/hệ thống chấm (vd 'KDIGO 2024', 'Cochrane (GRADE)', "
                     "'EULAR LoE/SoR'). Mô tả thiết kế nghiên cứu KHÔNG phải phân hạng: "
                     "nguồn không chấm thì để gradeLevel='na'." % (iid, grade))
            # CẢNH BÁO, KHÔNG chặn — và đây là quyết định đã cân nhắc rồi SỬA LẠI.
            # Bản đầu của luật này chặn cứng mọi mục `apply` thiếu `gradeBy`: 256 mục
            # trên ~50 dashboard. Nhưng "chưa khai `gradeBy`" KHÔNG đồng nghĩa "mức sai"
            # — rất nhiều mục đã nêu hệ chấm ngay trong `gradeSource` (vd "khuyến cáo
            # COR I của AHA/ASA"), chỉ là chưa tách ra trường riêng. Chặn cứng ở đây
            # chính là biến CHƯA BIẾT thành CÓ VẤN ĐỀ (BH08), và một bức tường đỏ như
            # vậy sẽ bị vô hiệu hoá bằng cách bỏ qua — mất luôn cả cảnh báo thật.
            # Nhóm THỰC SỰ tự mâu thuẫn (gradeSource tự khai "nguồn không phân hạng" mà
            # vẫn mang mức) đã được đưa về `na` ngày 14/08 — đó mới là phần chặn được.
            # Chuyển thành lỗi cứng khi `tools/kiem_phan_hang.py` về 0.
            warns.append(thieu)
        if dec == "apply" and design == "Consensus":
            errors.append("[%s] decision='apply' chỉ dựa Consensus — cần guideline/SR-MA/RCT hoặc hạ quyết định." % iid)
        # TẦNG TOÀN VĂN (PHA 4 LÔ D, 15/08/2026): thẩm định trên abstract KHÔNG
        # ngang thẩm định đầy đủ. Item tự khai `appraisalCompleteness:'partial'`
        # (chưa đọc toàn văn) thì bị CHẶN khỏi mức 'apply' — tối đa 'consider'.
        # CHỈ chặn khi khai TƯỜNG MINH 'partial'; trường VẮNG MẶT thì không suy
        # đoán (BH08 — «chưa khai» ≠ «một phần»; kho cũ chưa có trường này).
        ac = field(ch, "appraisalCompleteness")
        if dec == "apply" and ac == "partial":
            errors.append("[%s] decision='apply' nhưng appraisalCompleteness='partial' "
                          "(thẩm định CHƯA có toàn văn) — hạ xuống consider, hoặc đọc "
                          "toàn văn hợp pháp (PMC OA/Europe PMC/bản công khai của tổ "
                          "chức) rồi đổi thành 'full'." % iid)
        elif ac == "partial":
            warns.append("[%s] thẩm định MỘT PHẦN (chưa toàn văn) — nhãn này phải hiện "
                         "trên bản đọc, không giấu trong metadata." % iid)
        if dec == "apply" and not (pmid or doi) and url:
            warns.append("[%s] 'apply' chỉ có URL, không có PMID/DOI — chỉ chấp nhận nếu là guideline/label chính thức và đã ghi rõ trong standards.gates." % iid)

    oks.append("Strict source gate đã rà DATA.standards và %d item." % len(items))
    return errors, warns, oks


def meta_kind(data_block):
    """Loại artifact tự khai báo trong meta (vd kind:'cong-cu' = CÔNG CỤ HỖ TRỢ quyết định,
    KHÔNG phải danh sách thẻ chứng cứ → items[] rỗng là hợp lệ). Marker phải nằm trong meta của
    khối const DATA, do người soạn chủ động khai báo — không suy đoán hộ."""
    m = re.search(r"\bkind\s*:\s*['\"]([^'\"]*)['\"]", data_block)
    return m.group(1) if m else None


def verify_pmid_online(pmid, retries=2):
    """Tri-state (True/False/None) — xem docstring caller. Audit 2026-07-11: thêm
    retry-with-backoff cho lỗi rate-limit/server tạm thời (HTTP 429/5xx) của NCBI
    (không key → giới hạn ~3 req/s) — trước đây MỘT lần bị rate-limit là hạ ngay
    thành "lỗi mạng" không phân biệt được với hiccup thật, khiến quét nhiều PMID
    liên tiếp dễ tạo cảnh báo giả hàng loạt.
    Vá tiếp (vòng kế): lỗi mạng THÔNG THƯỜNG (timeout/DNS/URLError — ca thực tế phổ
    biến hơn rate-limit) trước đây trả None NGAY, không retry, dù cùng bản chất "hiccup
    tạm thời" như 429/5xx — giờ mọi lỗi (trừ HTTPError không nằm trong nhóm tạm thời)
    đều được thử lại giống nhau. Trả tiêu đề ĐẦY ĐỦ (không cắt 90 ký tự) — caller tự cắt
    khi hiển thị; giữ nguyên đủ để so khớp tráo trích dẫn (_title_overlap_ratio).

    Vá 2026-07-25: NCBI đôi lúc trả HTTP 200 nhưng body là HTML "Blocked Diagnostic"
    thay vì JSON; nếu vậy dùng Europe PMC MED mirror làm fallback metadata để vẫn xác minh
    PMID tồn tại + tiêu đề/năm, nhưng KHÔNG dùng fallback này cho cổng retraction."""
    url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
           "?db=pubmed&retmode=json&id=" + pmid)
    last_err = None
    for attempt in range(retries + 1):
        try:
            with source_urlopen(url, timeout=15) as r:
                raw = r.read().decode("utf-8", "replace")
                content_type = (r.headers.get("content-type") or "").lower()
            if "json" not in content_type and raw.lstrip().startswith("<"):
                raise ValueError("NCBI trả HTML thay vì JSON (có thể bị block)")
            j = json.loads(raw)
            res = j.get("result", {})
            if pmid in res and "title" in res[pmid]:
                # pubdate thường dạng "2026 Mar 13" hoặc "2026" — chỉ cần năm cho so khớp
                # dateVersion (vá 2026-07-12, xem docstring module).
                return True, res[pmid].get("title", ""), res[pmid].get("pubdate", "")
            return False, "không có trong PubMed", ""
        except (ValueError, JSONDecodeError) as e:
            last_err = e
            fallback = verify_pmid_europe_pmc(pmid)
            if fallback[0] is True:
                return fallback
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
                continue
            return None, "NCBI không trả JSON và Europe PMC fallback không xác minh được: %s" % e, ""
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(1.5 * (attempt + 1))
                continue
            return None, "lỗi mạng: %s" % e, ""
        except Exception as e:
            last_err = e
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
                continue
            return None, "lỗi mạng: %s" % e, ""
    return None, "lỗi mạng: hết lượt thử lại (%s)" % last_err, ""


def verify_pmid_europe_pmc(pmid):
    """Fallback metadata cho PMID khi NCBI E-utilities bị block.

    Europe PMC với `SRC:MED` phản chiếu bản ghi MEDLINE/PubMed đủ để kiểm PMID tồn tại,
    tiêu đề và năm. Không dùng kết quả này để kết luận trạng thái rút bài."""
    query = urllib.parse.quote(f"EXT_ID:{pmid} AND SRC:MED")
    url = (
        "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
        f"?query={query}&format=json&pageSize=1"
    )
    try:
        with source_urlopen(url, timeout=20) as r:
            j = json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return None, "lỗi Europe PMC fallback: %s" % e, ""
    results = j.get("resultList", {}).get("result", [])
    if not results:
        return None, "Europe PMC không trả bản ghi MED cho PMID", ""
    rec = results[0]
    if str(rec.get("pmid") or rec.get("id") or "") != str(pmid):
        return None, "Europe PMC trả bản ghi không khớp PMID", ""
    title = rec.get("title") or ""
    year = rec.get("pubYear") or rec.get("firstPublicationDate") or ""
    return True, title, year


def verify_doi_online(doi, retries=2):
    """Tri-state (True/False/None), phân giải DOI qua Crossref API (miễn phí, không cần key).
    Vá 2026-07-12: trước đây DOI chỉ kiểm ĐỊNH DẠNG (regex), không bao giờ phân giải thật —
    DOI bịa đúng định dạng (vd '10.1136/ard-2024-225452') PASS sạch qua cổng. Tái hiện thật:
    EBM_MASTER card EVID-2026-0270 mang DOI này, 404 khi tự tay tra doi.org/Crossref.
    Cùng nguyên tắc fail-closed như verify_pmid_online — lỗi mạng KHÔNG được coi là đã xác minh."""
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    last_err = None
    for attempt in range(retries + 1):
        try:
            with source_urlopen(url, timeout=15) as r:
                j = json.loads(r.read().decode("utf-8"))
            title = "; ".join(j.get("message", {}).get("title", []) or [])
            return True, title
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return False, "DOI không tồn tại trên Crossref (404)"
            last_err = e
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(1.5 * (attempt + 1))
                continue
            return None, "lỗi mạng: %s" % e
        except Exception as e:
            last_err = e
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
                continue
            return None, "lỗi mạng: %s" % e
    return None, "lỗi mạng: hết lượt thử lại (%s)" % last_err


def verify_url_online(url, retries=2):
    """Tri-state (True/False/None) — kiểm URL THẬT SỰ mở được (không chỉ đúng định dạng).

    SỬA 2026-07-22 (vòng lặp kiểm tra-hoàn thiện vòng 10, phát hiện MEDIUM): trước đây một
    item chỉ khai `url` (không pmid/doi) KHÔNG BAO GIỜ được xác minh online dù chạy --online —
    toàn bộ khối --online chỉ lặp qua `pmids`/`dois`, biến `url` không xuất hiện ở đó. Nay thêm
    nhánh thứ 3 cùng nguyên tắc fail-closed như PMID/DOI: lỗi mạng/timeout KHÔNG được coi là
    "đã xác minh". Chỉ GET nhẹ (không tải toàn bộ nội dung) — đủ để xác nhận URL còn tồn tại,
    không phải 404/hỏng."""
    last_err = None
    for attempt in range(retries + 1):
        try:
            with source_urlopen(url, timeout=15) as r:
                r.read(256)  # chỉ đọc vài trăm byte đầu — đủ xác nhận kết nối/status, không tải hết
                status = getattr(r, "status", None) or r.getcode()
            return True, "HTTP %s" % status
        except urllib.error.HTTPError as e:
            if e.code in (404, 410):
                return False, "URL không tồn tại (HTTP %d)" % e.code
            last_err = e
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(1.5 * (attempt + 1))
                continue
            return None, "lỗi mạng: %s" % e
        except Exception as e:
            last_err = e
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
                continue
            return None, "lỗi mạng: %s" % e
    return None, "lỗi mạng: hết lượt thử lại (%s)" % last_err


def _year_of(text):
    """Trích năm 4 chữ số đầu tiên trong chuỗi (dateVersion item hoặc pubdate PubMed)."""
    m = re.search(r"\b(19|20)\d{2}\b", text or "")
    return int(m.group(0)) if m else None


_TITLE_STOPWORDS = {
    "with", "from", "that", "this", "were", "have", "been", "into", "their",
    "after", "among", "during", "study", "using", "versus", "associated",
    "effect", "effects", "outcomes", "outcome", "results", "patients", "adults",
    "randomized", "controlled", "clinical", "trial", "review", "systematic",
    "analysis", "cohort", "based", "compared", "comparison", "national",
}


def _significant_words(text):
    return {w for w in re.findall(r"[A-Za-z]{4,}", (text or "").lower())} - _TITLE_STOPWORDS


def _title_overlap_ratio(real_title, item_text):
    """Tỷ lệ từ có nghĩa trong TIÊU ĐỀ THẬT (PubMed) xuất hiện đâu đó trong nội dung item
    (title/action/summary/references — references[] thường chứa nguyên văn câu trích dẫn kèm
    tiêu đề gốc). Dò TRÁO TRÍCH DẪN (PMID có thật nhưng LẠC ĐỀ) — verify_pmid_online() chỉ xác
    nhận PMID TỒN TẠI trên PubMed, KHÔNG xác nhận PMID đó nói đúng chủ đề item (audit 2026-07-11:
    tái hiện thật — PMID có thật của một bài không liên quan vẫn PASS sạch qua --online). Heuristic
    thô theo từ khóa (không NLP/không đối chiếu ngữ nghĩa) — CHỈ CẢNH BÁO (warns), không tự chặn:
    có thể bỏ sót khi title[item] diễn giải hoàn toàn khác chữ so với tiêu đề gốc, nhưng bắt được
    trường hợp rõ nhất — PMID hoàn toàn không liên quan (không chung từ khóa nào có nghĩa)."""
    sig = _significant_words(real_title)
    if len(sig) < 2:
        return 1.0  # tiêu đề quá ngắn/toàn hư từ — không đủ tín hiệu, coi như qua (tránh cảnh báo giả)
    text_low = (item_text or "").lower()
    hits = sum(1 for w in sig if w in text_low)
    return hits / len(sig)


def main():
    configure_utf8_stdio()

    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--online", action="store_true",
                    help="xác minh PMID qua NCBI + DOI qua Crossref trên mạng, và so năm "
                         "PubMed thật với dateVersion item khai (vá 2026-07-12)")
    ap.add_argument("--strict-sources", action="store_true",
                    help="bật cổng nguồn nghiêm ngặt: bắt DATA.standards, ngày tìm kiếm còn mới, "
                         "nguồn tìm kiếm ≥2, references[], và chặn apply nếu chứng cứ yếu/không phân hạng")
    ap.add_argument("--check-topic", action="store_true",
                    help="gọi Claude API chấm mỗi item có đúng chủ đề dashboard không (cần "
                         "ANTHROPIC_API_KEY; tốn 1 lượt gọi API/dashboard)")
    a = ap.parse_args()

    html = open(a.file, encoding="utf-8").read()
    errors, warns, oks = [], [], []

    # 1) Disclaimer
    if DISCLAIMER in html:
        oks.append("Có disclaimer \"%s\"." % DISCLAIMER)
    else:
        errors.append("THIẾU disclaimer \"%s\"." % DISCLAIMER)

    data = extract_data_block(html)
    if not data:
        errors.append("Không tìm thấy khối const DATA.")
        return report(errors, warns, oks)

    kind = meta_kind(data)
    is_tool = kind in {"cong-cu", "cong-cu-ho-tro", "tool"}

    items = split_items(data)
    if not items:
        if is_tool:
            # Chống lỗ hổng: dashboard CHỨNG CỨ đội lốt kind:'cong-cu' + items[] rỗng để né cổng truy nguyên.
            masq = re.search(r"gradeLevel|\bdecision\s*:|\bpmid\s*:|\bdoi\s*:", data, re.I)
            if masq:
                warns.append(
                    "kind=%r (miễn thẻ chứng cứ) NHƯNG khối DATA chứa dấu hiệu thẻ chứng cứ "
                    "(%r) với items[] rỗng → NGHI chứng cứ đội lốt công cụ, RÀ TAY." % (kind, masq.group(0))
                )
            oks.append("Loại CÔNG CỤ HỖ TRỢ (kind=%r): items[] rỗng là HỢP LỆ — "
                       "không bắt buộc thẻ chứng cứ (vẫn kiểm disclaimer/PII/nội dung)." % kind)
        else:
            errors.append("Không tách được item nào trong items[].")
    oks.append("Số item: %d." % len(items))

    pmids = []
    dois = []
    urls_only = []
    for ch in items:
        iid = field(ch, "id") or "(?)"
        pmid = field(ch, "pmid")
        doi = field(ch, "doi")
        url = field(ch, "url")
        grade = field(ch, "gradeLevel")
        dec = field(ch, "decision")
        date_version = field(ch, "dateVersion")
        if not (pmid or doi or url):
            errors.append("[%s] THIẾU định danh truy nguyên (pmid/doi/url)." % iid)
        if doi and not DOI_RE.match(doi.strip()):
            errors.append("[%s] DOI sai định dạng (nghi bịa/gõ sai): %r" % (iid, doi))
        if pmid and not PMID_RE.match(pmid.strip()):
            errors.append("[%s] PMID sai định dạng (nghi bịa/gõ sai): %r" % (iid, pmid))
        # Audit 2026-07-11: url được chấp nhận ngang pmid/doi để qua cổng truy nguyên
        # nhưng trước đây KHÔNG kiểm định dạng gì — chỉ kiểm scheme http(s) + có host,
        # KHÔNG phân giải thật (không đủ để xác nhận URL tồn tại, chỉ chặn chuỗi rác rõ ràng).
        if url and not pmid and not doi:
            u = urllib.parse.urlparse(url.strip())
            if u.scheme not in ("http", "https") or not u.netloc:
                errors.append("[%s] url không đúng định dạng (thiếu scheme http(s) hoặc host): %r"
                              % (iid, url))
            else:
                urls_only.append((iid, url.strip()))
        if pmid:
            pmids.append((iid, pmid, ch, date_version))
        if doi and DOI_RE.match(doi.strip()):
            dois.append((iid, doi.strip(), date_version))
        if grade not in VALID_GRADE:
            errors.append("[%s] gradeLevel không hợp lệ: %r (cần %s)." % (iid, grade, VALID_GRADE))
        if dec not in VALID_DECISION:
            errors.append("[%s] decision không hợp lệ: %r (cần %s)." % (iid, dec, VALID_DECISION))
        if "references" not in ch:
            warns.append("[%s] không thấy references[]." % iid)

    if a.strict_sources:
        se, sw, so = strict_source_checks(data, items)
        errors.extend(se)
        warns.extend(sw)
        oks.extend(so)
        if not a.online:
            warns.append("--strict-sources đang chạy offline: đã kiểm hợp đồng nguồn, nhưng chưa phân giải thật PMID/DOI. Dashboard thật nên chạy thêm --online.")

    # 2) PII (heuristic — chỉ cảnh báo)
    pii = []
    pii += re.findall(r"\b\d{1,2}/\d{1,2}/\d{4}\b", html)            # ngày sinh dạng dd/mm/yyyy
    pii += re.findall(r"\b0\d{9}\b", html)                            # SĐT VN
    pii += re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", html)              # email
    pii += re.findall(r"\bCCCD|CMND|số\s*BHYT|mã\s*BN|MRN\b", html, re.I)
    if pii:
        warns.append("Nghi PII (RÀ TAY): %s" % ", ".join(sorted(set(pii))[:8]))
    else:
        oks.append("Không thấy mẫu PII rõ ràng.")

    # 3) Xác minh PMID/DOI online
    if a.online and pmids:
        oks.append("Đang xác minh %d PMID trên PubMed…" % len(set(p for _, p, _, _ in pmids)))
        seen = {}
        net_calls = 0
        for iid, p, ch, date_version in pmids:
            if p in seen:
                ok, info, pubdate = seen[p]
            else:
                # Giãn cách ~3 req/s (NCBI E-utilities không key) để tránh TỰ gây rate-limit
                # khi quét nhiều PMID liên tiếp, thay vì chỉ phản ứng bằng retry sau đó.
                if net_calls:
                    time.sleep(0.34)
                net_calls += 1
                ok, info, pubdate = verify_pmid_online(p)
                seen[p] = (ok, info, pubdate)
            if ok is True:
                oks.append("[%s] PMID %s ✓ %s" % (iid, p, info[:90]))
                # Vá (vòng kế tiếp 2026-07-11): dò TRÁO TRÍCH DẪN — PMID có thật nhưng tiêu đề
                # PubMed KHÔNG khớp nội dung item (đã tái hiện thật: PMID không liên quan vẫn
                # PASS sạch). Tính LẠI theo TỪNG item (không dùng cache) vì cùng 1 PMID có thể bị
                # gán nhầm cho nhiều item khác chủ đề nhau. Chỉ cảnh báo — RÀ TAY, không tự chặn.
                overlap = _title_overlap_ratio(info, ch)
                if overlap < 0.25:
                    msg = (
                        "[%s] PMID %s tồn tại thật trên PubMed nhưng tiêu đề KHÔNG khớp nội dung "
                        "item (trùng %.0f%% từ khóa có nghĩa) — NGHI TRÁO PMID (lạc đề). Tiêu đề "
                        "PubMed thật: \"%s\"." % (iid, p, overlap * 100, info[:120])
                    )
                    if a.strict_sources:
                        errors.append(msg + " Strict-sources: lỗi cứng, không phát hành.")
                    else:
                        warns.append(msg + " RÀ TAY, không tự gỡ.")
                # Vá 2026-07-12: "đúng họ guideline, sai phiên bản/năm" — overlap từ khóa cao
                # (cùng tên guideline lặp lại qua các năm) nên heuristic trên KHÔNG bắt được;
                # so trực tiếp năm PubMed thật với dateVersion item khai. Dung sai 1 năm (in
                # ấn/epub lệch nhau là bình thường).
                real_year, decl_year = _year_of(pubdate), _year_of(date_version)
                if real_year and decl_year and abs(real_year - decl_year) > 1:
                    msg = (
                        "[%s] PMID %s xuất bản THẬT năm %d nhưng item khai dateVersion=%s — "
                        "NGHI TRÍCH DẪN NHẦM PHIÊN BẢN/năm của cùng họ guideline."
                        % (iid, p, real_year, date_version)
                    )
                    if a.strict_sources:
                        errors.append(msg + " Strict-sources: lỗi cứng, không phát hành.")
                    else:
                        warns.append(msg + " RÀ TAY, không tự sửa.")
            elif ok is False:
                errors.append("[%s] PMID %s KHÔNG phân giải: %s" % (iid, p, info))
            else:
                # Vá 2026-07-11 (vòng 9): trước đây vào warns — --online có thể PASS dù
                # KHÔNG PMID nào thực sự được xác nhận (fail-open: PMID bịa lọt qua y hệt
                # PMID thật nếu quét đúng lúc PubMed lỗi/mất mạng). Fail-closed: không xác
                # minh được = không cho qua cổng --online (đúng ý nghĩa "đã xác minh").
                errors.append("[%s] PMID %s CHƯA XÁC MINH ĐƯỢC (%s) — --online yêu cầu xác "
                              "nhận được mới PASS, không coi lỗi mạng là đã xác minh." % (iid, p, info))
    elif pmids:
        oks.append("Có %d PMID (chạy --online để xác minh phân giải)." % len(set(p for _, p, _, _ in pmids)))

    # 3b) Xác minh DOI online qua Crossref (vá 2026-07-12 — xem docstring module: DOI bịa
    # đúng định dạng trước đây PASS sạch qua cổng, kể cả với --online).
    if a.online and dois:
        oks.append("Đang xác minh %d DOI qua Crossref…" % len(set(d for _, d, _ in dois)))
        seen_doi = {}
        net_calls_doi = 0
        for iid, d, date_version in dois:
            if d in seen_doi:
                ok, info = seen_doi[d]
            else:
                if net_calls_doi:
                    time.sleep(0.1)  # Crossref không công bố rate-limit cứng như NCBI, giãn nhẹ
                net_calls_doi += 1
                ok, info = verify_doi_online(d)
                seen_doi[d] = (ok, info)
            if ok is True:
                oks.append("[%s] DOI %s ✓ %s" % (iid, d, info[:90]))
            elif ok is False:
                errors.append("[%s] DOI %s KHÔNG phân giải qua Crossref: %s — nghi DOI bịa/sai."
                              % (iid, d, info))
            else:
                # Fail-closed như PMID — lỗi mạng khi tra Crossref không được coi là đã xác minh.
                msg = ("[%s] DOI %s CHƯA XÁC MINH ĐƯỢC qua Crossref (%s) — mạng lỗi hoặc "
                       "Crossref tạm ngưng." % (iid, d, info))
                if a.strict_sources:
                    errors.append(msg + " Strict-sources: lỗi cứng, không phát hành.")
                else:
                    warns.append(msg + " Rà lại thủ công.")
    elif dois:
        oks.append("Có %d DOI đúng định dạng (chạy --online để xác minh phân giải qua Crossref)."
                   % len(set(d for _, d, _ in dois)))

    # 3c) Xác minh URL online (SỬA 2026-07-22, vòng lặp kiểm tra-hoàn thiện vòng 10, phát hiện
    # MEDIUM): item CHỈ có url (không pmid/doi) trước đây KHÔNG BAO GIỜ được xác minh online dù
    # chạy --online — nhánh này trước đây hoàn toàn không tồn tại. Cùng nguyên tắc fail-closed.
    if a.online and urls_only:
        oks.append("Đang xác minh %d url mở được…" % len(set(u for _, u in urls_only)))
        seen_url = {}
        net_calls_url = 0
        for iid, u in urls_only:
            if u in seen_url:
                ok, info = seen_url[u]
            else:
                if net_calls_url:
                    time.sleep(0.1)
                net_calls_url += 1
                ok, info = verify_url_online(u)
                seen_url[u] = (ok, info)
            if ok is True:
                oks.append("[%s] url %s ✓ %s" % (iid, u, info))
            elif ok is False:
                errors.append("[%s] url %s KHÔNG mở được: %s — nghi link chết/sai." % (iid, u, info))
            else:
                # Fail-closed như PMID/DOI — lỗi mạng không được coi là đã xác minh.
                msg = "[%s] url %s CHƯA XÁC MINH ĐƯỢC (%s) — mạng lỗi hoặc trang tạm ngưng." % (iid, u, info)
                if a.strict_sources:
                    errors.append(msg + " Strict-sources: lỗi cứng, không phát hành.")
                else:
                    warns.append(msg + " Rà lại thủ công.")
    elif urls_only:
        oks.append("Có %d url đúng định dạng, chỉ dùng url làm truy nguyên (chạy --online để "
                   "xác minh mở được)." % len(set(u for _, u in urls_only)))

    # 4) CHẤT LƯỢNG NỘI DUNG — chống rác abstract NGOẠI NGỮ / placeholder (xem dashboard_content_audit.py)
    try:
        import os as _os
        import sys as _sys
        _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
        import dashboard_content_audit as DCA
        iss = DCA.audit_file(a.file).get("issues", {})
        if iss.get("summary_foreign"):
            errors.append("Tóm tắt nhồi câu NGOẠI NGỮ (%d) — cần tổng hợp tiếng Việt: %s"
                          % (len(iss["summary_foreign"]), "; ".join(iss["summary_foreign"][:3])))
        if iss.get("items_action_foreign"):
            errors.append("%d item có 'action' là abstract NGOẠI NGỮ (phải là tổng hợp tiếng Việt): %s"
                          % (len(iss["items_action_foreign"]), ", ".join(iss["items_action_foreign"][:10])))
        if iss.get("items_action_empty"):
            warns.append("%d item 'action' rỗng/—: %s"
                         % (len(iss["items_action_empty"]), ", ".join(iss["items_action_empty"][:10])))
        if iss.get("items_vn_placeholder"):
            warns.append("%d item 'vn' (Áp dụng VN) chỉ là placeholder [CẦN…]/rỗng — nên bổ sung: %s"
                         % (len(iss["items_vn_placeholder"]), ", ".join(iss["items_vn_placeholder"][:10])))
        if not any(iss.values()):
            oks.append("Nội dung sạch: không có abstract ngoại ngữ / placeholder ở action·summary.")
    except Exception as e:
        warns.append("Không chạy được kiểm chất lượng nội dung: %s" % e)

    # 5) NGHI GÁN MỨC MÁY MÓC — toàn bộ item cùng gradeLevel='high' (vi phạm liêm chính R4)
    # Audit 2026-07-11: ngưỡng >=8 trước đây bỏ sót "chế độ nhanh" (3-7 item) — vẫn cùng
    # rủi ro nhưng mẫu nhỏ hơn nên hạ xuống WARN (không auto-chặn) thay vì ERROR cứng như n>=8.
    grades = [field(ch, "gradeLevel") for ch in items]
    n = len(items)
    if n >= 8:
        n_high = sum(1 for g in grades if g == "high")
        if n_high >= 0.9 * n:
            errors.append("NGHI GÁN MỨC MÁY MÓC: %d/%d item đều gradeLevel='high' — không nguồn nào "
                          "đồng loạt 'Cao'. Rà & chấm GRADE từng nguồn (RoB/GRADE thật)." % (n_high, n))
    elif 1 <= n < 8:
        # SỬA 2026-07-22 (vòng lặp kiểm tra-hoàn thiện vòng 10, phát hiện LOW): trước đây điều
        # kiện `3 <= n < 8` bỏ sót dashboard chỉ có 1-2 item — cùng bản chất nghi vấn (gán mức
        # không qua thẩm định thật) như trường hợp 3-7 item nhưng lại đi qua cổng này êm ru,
        # không cảnh báo gì. Hạ ngưỡng xuống n>=1 để nhất quán với chính lý do đã thêm nhánh
        # "chế độ nhanh" này (audit 2026-07-11): mẫu càng nhỏ, rủi ro gán mức máy móc càng khó
        # phân biệt với ngẫu nhiên, không phải lý do để BỎ QUA hoàn toàn.
        n_high = sum(1 for g in grades if g == "high")
        if n_high == n:
            warns.append("NGHI GÁN MỨC MÁY MÓC (mẫu nhỏ, %d item): tất cả đều gradeLevel='high' — "
                         "rà lại xem có thật sự đồng loạt 'Cao' không (RoB/GRADE thật)." % n)

    # 6) (--check-topic, opt-in) ĐỘ LIÊN QUAN CHỦ ĐỀ — gate kỹ thuật ở trên KHÔNG bắt được item
    # lạc chủ đề (vd bài sản khoa/nhi khoa lọt vào dashboard Tim mạch — đã gặp thật ở
    # TimMach_20260609, chỉ phát hiện được bằng đọc tay). Luôn CẢNH BÁO, không chặn cứng — phân
    # loại LLM có sai số, quyết định cuối thuộc bác sĩ. Bỏ qua êm nếu thiếu ANTHROPIC_API_KEY.
    if a.check_topic:
        try:
            import os as _os
            import sys as _sys
            _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
            import check_topic_relevance as CTR
            topic_result = CTR.check_dashboard_topic_relevance(a.file)
            if topic_result["status"] == "skipped":
                warns.append("Kiểm chủ đề (--check-topic): BỎ QUA — %s" % topic_result["message"])
            elif topic_result["status"] == "error":
                warns.append("Kiểm chủ đề (--check-topic): lỗi — %s" % topic_result["message"])
            elif topic_result["off_topic"]:
                ids = ", ".join(it["id"] for it in topic_result["off_topic"])
                warns.append(
                    "NGHI %d item LẠC CHỦ ĐỀ '%s' (LLM chấm, cần bác sĩ rà, KHÔNG tự gỡ): %s"
                    % (len(topic_result["off_topic"]), topic_result["topic"], ids)
                )
            else:
                oks.append("Kiểm chủ đề: %d/%d item đều khớp chủ đề dashboard."
                           % (topic_result["total_items"], topic_result["total_items"]))
        except Exception as e:
            warns.append("Không chạy được kiểm chủ đề: %s" % e)

    kiem_nguon_da_rut(a.file, errors, warns, oks)

    return report(errors, warns, oks)


# Dấu hiệu lỗi thuộc về MÁY/MẠNG, không phải về nguồn chứng cứ.
_DAU_HIEU_LOI_MANG = (
    "getaddrinfo failed",      # DNS không phân giải được tên miền
    "timed out",
    "lỗi mạng:",
    "Name or service not known",
    "Temporary failure in name resolution",
    "có thể bị block",
)


def _canh_bao_loi_mang(errors):
    """In cảnh báo riêng khi phần lớn lỗi cứng là do MẠNG chứ không phải do nguồn.

    VÌ SAO CÓ (12/08/2026): chạy `--online` ba lần liên tiếp trên CÙNG một dashboard
    ở máy Windows cho 13 → 3 → 6 lỗi cứng. Nguyên nhân là DNS của máy chỉ trỏ một
    server đang chập chờn, không phải nguồn chứng cứ có vấn đề. Nhưng báo cáo cũ
    gộp cả hai vào "✗ ... CHƯA XÁC MINH ĐƯỢC" và chốt "FAIL — n lỗi cứng", nên
    người đọc rất dễ kết luận sai theo CẢ HAI chiều: tưởng nguồn hỏng (trong khi
    nguồn có thể vẫn tốt), hoặc — nguy hiểm hơn — chạy lại vài lần tới khi may mắn
    ra ít lỗi rồi coi đó là đã xác minh.

    Cổng vẫn fail-closed như cũ (không hạ lỗi thành cảnh báo, không đổi mã thoát):
    "chưa xác minh được" vẫn là chưa xác minh. Chỗ này chỉ nói RÕ ràng buộc đó đến
    từ đâu, để kết quả không bị đọc thành nhận định về chất lượng chứng cứ.
    """
    mang = [e for e in errors if any(d in e for d in _DAU_HIEU_LOI_MANG)]
    if not mang:
        return
    print("")
    print("  ⓘ %d/%d lỗi cứng ở trên là do MÁY/MẠNG (DNS không phân giải được, quá thời"
          " gian chờ), KHÔNG phải kết luận về nguồn chứng cứ." % (len(mang), len(errors)))
    print("    → KHÔNG dùng lần chạy này để nói nguồn sai, cũng KHÔNG chạy lại nhiều lần")
    print("      rồi lấy lần ít lỗi nhất làm bằng chứng đã xác minh — kết quả sẽ khác nhau")
    print("      mỗi lần chạy và không tái lập được.")
    print("    → Sửa mạng/DNS rồi chạy lại tới khi số lỗi ổn định thì mới kết luận được.")


def _replacement_acknowledgement(duong_dan, record):
    """Xác nhận dashboard đã khai ĐỦ một bản ``Retraction and Replacement``.

    Chỉ trả mã item khi cùng item: trỏ đúng định danh bị ảnh hưởng, khai nguồn bị
    thay + thông báo thay thế, ghi rõ đang dùng bản sửa, và bị hạ về ``notyet``.
    Thiếu bất kỳ điều kiện nào đều trả ``None`` để cổng tiếp tục chặn fail-closed.
    """
    if not record.get("rut_va_thay"):
        return None
    try:
        html = Path(duong_dan).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    data = extract_data_block(html)
    if not data:
        return None

    def norm_identifier(value):
        value = str(value or "").strip().casefold()
        for prefix in ("https://doi.org/", "http://doi.org/", "doi.org/", "doi:"):
            if value.startswith(prefix):
                value = value[len(prefix):]
                break
        return value

    affected_type = str(record.get("loai") or "").strip()
    affected_value = norm_identifier(record.get("gia_tri"))
    notice = norm_identifier(record.get("thong_bao"))
    for chunk in split_items(data):
        if affected_type not in {"pmid", "doi"}:
            continue
        replaces_pmid = field(chunk, "replacesPmid")
        # Khớp theo HAI đường (vá 15/08/2026, ca ITEM-05 ViemGanB): (a) định danh
        # CHÍNH của item; hoặc (b) bản ghi loại pmid trùng `replacesPmid` — item
        # rút-và-thay chuẩn cố ý để pmid:"" và trỏ nguồn chính bằng DOI bản thay,
        # nên PMID bài gốc CHỈ xuất hiện ở replacesPmid; đòi nó nằm ở trường pmid
        # là đòi một điều khai báo đúng không bao giờ thoả. Mọi điều kiện
        # fail-closed còn lại (notice khai đủ, notyet, chữ «bản thay thế») giữ nguyên.
        own_match = norm_identifier(field(chunk, affected_type)) == affected_value
        replaces_match = (affected_type == "pmid"
                          and norm_identifier(replaces_pmid) == affected_value)
        if not (own_match or replaces_match):
            continue
        notice_pmid = field(chunk, "replacementNoticePmid")
        notice_doi = field(chunk, "replacementNoticeDoi")
        declared_notices = {norm_identifier(notice_pmid), norm_identifier(notice_doi)} - {""}
        if not replaces_pmid or not declared_notices:
            continue
        if notice and notice not in declared_notices and notice not in norm_identifier(chunk):
            continue
        if field(chunk, "decision") != "notyet":
            continue
        # (field() or "") — vá 15/08: field() trả None khi khoá vắng mặt; item thiếu
        # một trong bốn trường làm join nổ TypeError ⇒ cổng CRASH thay vì chặn có
        # thông điệp. Fail-closed nghĩa là trả lời «không đạt», không phải chết.
        revision_text = " ".join(
            [
                field(chunk, "dateVersion") or "",
                field(chunk, "effectText") or "",
                field(chunk, "gradeSource") or "",
                field(chunk, "flag") or "",
            ]
        ).casefold()
        if not any(marker in revision_text for marker in ("bản thay thế", "bản đã sửa", "replacement")):
            continue
        if not any(value in norm_identifier(chunk) for value in declared_notices):
            continue
        return field(chunk, "id") or "(?)"
    return None


def kiem_nguon_da_rut(duong_dan, errors, warns, oks, tra_cuu=None):
    """LỖI CỨNG khi sổ xác minh đã ghi nhận một nguồn của gói này ĐÃ BỊ RÚT.

    Thêm 14/08/2026 (vòng lặp kiểm tra–hoàn thiện, vòng 2). Đây KHÔNG mâu thuẫn với
    nguyên tắc "cổng này cố ý không kết luận trạng thái rút bài" ghi ở
    `verify_pmid_europe_pmc()`: chỗ đó cấm SUY RA trạng thái rút bài từ một nguồn
    metadata không đủ thẩm quyền. Ở đây cổng không suy ra gì cả — nó chỉ ĐỌC LẠI kết
    luận DƯƠNG TÍNH mà chuỗi 3 tầng (Retraction Watch → NCBI → Europe PMC) đã xác
    nhận và ghi vào sổ, theo đúng luật gộp bất đối xứng.

    Vì sao phải chặn: PMID 30267080 (JAMA Oncology, rút 2019) nằm trong
    ViemGanB_DieuTri và đi qua cổng này sạch sẽ, vì trước nay không có bước nào hỏi
    "nguồn này còn hiệu lực không". Một trích dẫn đã bị rút là lỗi nghiêm trọng hơn
    hầu hết những gì cổng đang bắt.

    KHÔNG BAO GIỜ phát tín hiệu ngược lại: sổ im lặng nghĩa là CHƯA KIỂM, không phải
    "đã kiểm và sạch" (BH08/BH27). Khi không đọc được sổ, ghi CẢNH BÁO chứ không âm
    thầm bỏ qua — bỏ qua im lặng sẽ đọc thành "đã kiểm, không có gì".
    """
    from pathlib import Path as _Path
    if tra_cuu is None:
        # DÒ NGƯỢC LÊN, không đếm cứng số bậc: file này sống ở BA nơi có độ sâu khác
        # nhau (EBM-Dashboards/tools · EBM_MASTER/skill_assets · sync/skills/…/tools)
        # cộng thêm bản trong thư mục chạy của skill. Một hằng số `parents[2]` chỉ
        # đúng ở một nơi và im lặng sai ở những nơi còn lại — đúng lớp lỗi BH06.
        _p = None
        for _t in _Path(__file__).resolve().parents:
            _u = _t / "tools" / "so_xac_minh_nguon.py"
            if _u.exists():
                _p = _u
                break
        if _p is None:
            warns.append("Chưa kiểm được rút bài: không thấy tools/so_xac_minh_nguon.py "
                         "(đây là 'chưa biết', KHÔNG phải 'không có').")
            return

        import importlib.util as _ilu
        _spec = _ilu.spec_from_file_location("so_xm_vd", _p)
        _mod_so = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(_mod_so)

        def tra_cuu(ten):
            return _mod_so.nguon_da_rut(ten)
        _tra_dinh_danh = getattr(_mod_so, "dinh_danh_da_rut", None)
    else:
        # tra_cuu tiêm từ ngoài (test/BH31): giữ nguyên hợp đồng cũ, không tự ý
        # mở thêm tầng định danh mà bên tiêm không biết.
        _tra_dinh_danh = None
    try:
        da_rut = list(tra_cuu(_Path(duong_dan).name))
    except Exception as e:
        warns.append("Chưa kiểm được rút bài (%s) — 'chưa biết', KHÔNG phải 'không có'. "
                     "Chạy: python tools/so_xac_minh_nguon.py --quet <file>" % e)
        return

    # TẦNG 2 (PHA 4 LÔ E, 15/08/2026): tra THẲNG định danh của CHÍNH file vào sổ.
    # Lỗ hổng tìm ra bằng fixture: `nguon_da_rut` lọc theo ánh xạ cac_dashboard,
    # nên dashboard MỚI trích đúng DOI đã rút nhưng chưa từng qua vòng quét A4 sẽ
    # đi qua cổng sạch sẽ. Sổ đã BIẾT bài bị rút thì mọi file trích nó phải nghe.
    if _tra_dinh_danh is not None:
        try:
            _nd = _Path(duong_dan).read_text(encoding="utf-8", errors="replace")
            _ids = set(re.findall(r"pmid['\"]?\s*[:=]\s*['\"]?(\d{6,9})", _nd, re.I))
            _ids |= {m.rstrip(".,;'\")”") for m in
                     re.findall(r"10\.\d{4,9}/[^\s'\"<>]+", _nd)}
            da_co = {(r["loai"], r["gia_tri"]) for r in da_rut}
            for r in _tra_dinh_danh(sorted(_ids)):
                if (r["loai"], r["gia_tri"]) not in da_co:
                    da_rut.append(r)
        except Exception as e:
            warns.append("Chưa kiểm được rút bài theo ĐỊNH DANH (%s) — 'chưa biết', "
                         "KHÔNG phải 'không có'." % e)

    if not da_rut:
        # Cố ý KHÔNG ghi vào oks: sổ không có bản ghi dương tính có thể chỉ vì chưa
        # ai quét file này. Một dòng ✓ ở đây sẽ là lời bảo đảm mà dữ liệu không đỡ nổi.
        return
    for r in da_rut:
        # BA mức, KHÔNG gộp — mỗi mức đòi một việc khác hẳn:
        #   • rút rồi ĐĂNG LẠI bản đã sửa → trích dẫn vẫn dùng được, phải đối chiếu SỐ LIỆU
        #     với bản đã sửa (thường CÙNG DOI/PMID). Gọi nó là "đã bị rút, không dùng" là
        #     nói sai về một trích dẫn hợp lệ.
        #   • rút bỏ hẳn → không dùng kết luận.
        #   • Expression of Concern → chưa kết luận, đọc lại.
        if r.get("rut_va_thay"):
            nhan, viec = ("ĐÃ RÚT & ĐĂNG LẠI BẢN SỬA",
                          "trích dẫn VẪN dùng được nhưng số liệu phải lấy từ BẢN ĐÃ SỬA")
            acknowledged_item = _replacement_acknowledgement(duong_dan, r)
            if acknowledged_item:
                warns.append(
                    "[%s] NGUỒN ĐÃ RÚT & ĐĂNG LẠI BẢN SỬA đã được khai tường minh: "
                    "%s:%s; có định danh thông báo thay thế, số liệu bản sửa và "
                    "decision='notyet'. Giữ ở hàng bác sĩ rà, không tự áp dụng."
                    % (acknowledged_item, r["loai"], r["gia_tri"])
                )
                continue
        elif r["tinh_trang"] == "retracted":
            nhan, viec = "ĐÃ BỊ RÚT", "không dùng kết luận của bài này"
        else:
            nhan, viec = "CÓ QUAN NGẠI (EoC)", "chưa kết luận — đọc lại trước khi dùng"
        tb = f", thông báo {r['thong_bao']}" if r.get("thong_bao") else ""
        errors.append(
            "NGUỒN %s: %s:%s — %s (sổ ghi %s, nguồn %s%s). %s; KHÔNG tự xoá mục — "
            "quyết định là của bác sĩ."
            % (nhan, r["loai"], r["gia_tri"], (r["tieu_de"] or "")[:80],
               r["kiem_luc"], r["nguon"], tb, viec))


def report(errors, warns, oks):
    print("=" * 64)
    print("CỔNG KIỂM LIÊM CHÍNH — Web Dashboard EBM")
    print("=" * 64)
    for o in oks:
        print("  ✓ " + o)
    for w in warns:
        print("  ⚠ " + w)
    for e in errors:
        print("  ✗ " + e)
    print("-" * 64)
    if errors:
        print("KẾT QUẢ: ✗ FAIL — %d lỗi cứng, %d cảnh báo. Sửa trước khi giao." % (len(errors), len(warns)))
        _canh_bao_loi_mang(errors)
        # MÃ THOÁT TÁCH HAI LOẠI THẤT BẠI (LÔ 2 PHA 2, 15/08/2026):
        #   1 = có ít nhất MỘT lỗi NỘI DUNG (nguồn/số liệu/an toàn) — phải sửa gói;
        #   2 = TOÀN BỘ lỗi cứng là MÁY/MẠNG (DNS, timeout) — gói chưa được xác
        #       minh chứ không phải gói sai; chạy lại khi mạng ổn / dùng sổ xác minh.
        # Cả hai đều nonzero: cổng vẫn fail-closed, không caller nào bị mở nhầm.
        mang = [e for e in errors if any(d in e for d in _DAU_HIEU_LOI_MANG)]
        return 2 if len(mang) == len(errors) else 1
    print("KẾT QUẢ: ✓ PASS — 0 lỗi cứng, %d cảnh báo (rà tay nếu có)." % len(warns))
    return 0


if __name__ == "__main__":
    sys.exit(main())
