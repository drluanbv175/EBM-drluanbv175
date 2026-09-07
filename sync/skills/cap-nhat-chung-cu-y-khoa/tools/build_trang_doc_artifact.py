#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dựng TRANG ĐỌC kiểu Artifact (thiết kế, dùng token màu) từ một file HTML
dạng docx→html thô — dùng cho luồng "tái dựng tài liệu đã có sẵn"
(references/14-tai-dung-tai-lieu-co-san.md, §5G của SKILL.md).

Ra đời 07/09/2026 sau khi bác sĩ phản hồi bản Artifact đầu tiên (tài liệu Suy
Tim) "thiết kế chưa cân đối, bảng trình bày, các chứng cứ chưa có điểm nhấn
rõ rệt". Script gốc là một bản dùng-một-lần gắn cứng đường dẫn/tiêu đề cho
đúng một tài liệu; bản này tách phần THẬT SỰ tổng quát (bảng màu, quy tắc
bọc chứng cứ HR/RR/OR, huy hiệu Class/Level, khung CSS 3-theme) khỏi phần
GIẢ ĐỊNH BỐ CỤC (4 đoạn mở đầu + 1 bảng cảnh báo) — phần sau CẦN đối chiếu
lại khi tài liệu mới có bố cục khác, xem "GIỚI HẠN" bên dưới.

DÙNG:
    python3 build_trang_doc_artifact.py <src.html> <out.html> \
        [--title "Tên trang"] [--eyebrow-date YYYY-MM-DD] \
        [--footer-date YYYY-MM-DD]

<src.html> là bản HTML thô xuất từ .docx (vd bằng
`tools/docx_sang_html_khong_pandoc.py` hoặc pandoc) — KHÔNG phải khối `DATA`
của Web Dashboard. Với Web Dashboard (items[] có sẵn), dùng
`build_ban_doc_chung_cu.py` — công cụ đó đã có cơ chế điểm nhấn chứng cứ
RIÊNG phù hợp dữ liệu có cấu trúc (forest-plot theo từng mục), không cần và
không nên dùng script này thay thế.

GIỚI HẠN — ĐỌC TRƯỚC KHI DÙNG CHO TÀI LIỆU MỚI:
- Phần TỔNG QUÁT, dùng lại an toàn cho mọi tài liệu: bảng màu chữ/nền
  (TEXT_COLOR_MAP/BG_COLOR_MAP, đúng bảng màu Evidence Workbench đã dùng khi
  dựng .docx qua skill `docx`), quy tắc bọc chip chứng cứ HR/RR/OR/Rate
  Ratio/Risk Ratio kèm KTC 95%/p (STAT_RE), huy hiệu Class/Level
  (GRADE_RE), khung CSS 3-theme + token --data (điểm nhấn chứng cứ, tách
  biệt màu với --cite của số trích dẫn [n]), bảng có header dính khi cuộn.
- Phần GIẢ ĐỊNH BỐ CỤC, cần bác sĩ/Claude đối chiếu lại mỗi tài liệu mới:
  hàm `main()` giả định 4 đoạn <p> đầu tiên (trước bảng đầu tiên) lần lượt
  là tiêu đề/phụ đề/dòng meta/disclaimer, và bảng ĐẦU TIÊN của tài liệu là
  một khối cảnh báo (<th> chứa các <p> gạch đầu dòng). Tài liệu có bố cục
  khác (không mở đầu bằng khối cảnh báo, ví dụ) sẽ cần sửa lại đoạn trích
  xuất masthead trong `main()` trước khi chạy — KHÔNG chạy "cho chắc" rồi
  tin kết quả nếu bố cục khác biệt rõ rệt.
"""
import argparse
import datetime
import re
import unicodedata
from bs4 import BeautifulSoup, NavigableString

TEXT_COLOR_MAP = {
    "#1E3A5F": "c-accent",
    "#B91C1C": "c-danger",
    "#15803D": "c-good",
    "#B45309": "c-warn",
    "#6B7280": "c-muted",
    "#334155": "c-muted2",
    "#475569": "c-muted3",
    "#2563EB": "c-cite",
    "#FFFFFF": "c-onaccent",
}
BG_COLOR_MAP = {
    "#1E3A5F": "bg-accent",
    "#EFF6FF": "bg-cite-soft",
    "#F0FDF4": "bg-good-soft",
    "#FEF2F2": "bg-danger-soft",
    "#FFFBEB": "bg-warn-soft",
}

# Effect-measure clause: keyword, value, optional CI (either ", KTC 95%: a-b"
# with no parens, or a fully-bracketed "(KTC 95%: a-b)" — never a lone
# unmatched paren), optional trailing p-value.
#
# NUM must NOT be \d[\d,]* — a trailing comma with no digit after it (the
# delimiter comma before "KTC", as in "Risk Ratio: 0,66, KTC 95%: ...")
# would then get greedily swallowed into the number itself, leaving no
# comma for the CI group to match on and truncating the chip right after
# the ratio value. \d+(?:,\d+)? only consumes a comma when digits follow.
NUM = r"\d+(?:,\d+)?"
STAT_RE = re.compile(
    rf"(?:HR|RR|OR|Rate Ratio|Risk Ratio|Relative Risk Ratio)\s*:?\s*{NUM}"
    rf"(?:"
    rf"\s*[;,]\s*KTC\s*95%\s*:?\s*{NUM}\s*[–-]\s*{NUM}"
    rf"|"
    rf"\s*\(\s*KTC\s*95%\s*:?\s*{NUM}\s*[–-]\s*{NUM}\s*\)"
    rf")?"
    rf"(?:\s*;\s*p\s*[<>=]\s*{NUM})?"
)

GRADE_RE = re.compile(r"^(I{1,3}[ab]?|IV)\s*,\s*([A-C])\b(.*)$")


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[\s_]+", "-", text)


def recolor(soup: BeautifulSoup) -> None:
    for span in soup.find_all("span", style=True):
        m = re.search(r"color:\s*(#[0-9A-Fa-f]{6})", span["style"])
        if m and m.group(1).upper() in TEXT_COLOR_MAP:
            span["class"] = span.get("class", []) + [TEXT_COLOR_MAP[m.group(1).upper()]]
            del span["style"]
    for cell in soup.find_all(["th", "td"], style=True):
        m = re.search(r"background:\s*(#[0-9A-Fa-f]{6})", cell["style"])
        if m and m.group(1).upper() in BG_COLOR_MAP:
            cell["class"] = cell.get("class", []) + [BG_COLOR_MAP[m.group(1).upper()]]
            del cell["style"]


def wrap_stats(soup: BeautifulSoup) -> int:
    """Bọc mọi cụm HR/RR/OR/... trong một text node bằng <span class=stat>."""
    n = 0
    for text_node in list(soup.find_all(string=True)):
        if text_node.parent.name in ("script", "style") or "stat" in (text_node.parent.get("class") or []):
            continue
        s = str(text_node)
        matches = list(STAT_RE.finditer(s))
        if not matches:
            continue
        pieces = []
        last = 0
        for m in matches:
            if m.start() > last:
                pieces.append(NavigableString(s[last:m.start()]))
            chip = soup.new_tag("span", **{"class": "stat"})
            chip.string = m.group(0)
            pieces.append(chip)
            last = m.end()
            n += 1
        if last < len(s):
            pieces.append(NavigableString(s[last:]))
        for node in reversed(pieces):
            text_node.insert_after(node)
        text_node.extract()
    return n


def wrap_pct_compare(soup: BeautifulSoup) -> None:
    """Cho các so sánh 'X% so với Y%' đã in đậm sẵn kiểu chữ số thẳng hàng."""
    pct_re = re.compile(r"\d[\d,]*%\s*so\s*với\s*\d[\d,]*%")
    for strong in soup.find_all("strong"):
        if pct_re.search(strong.get_text()):
            strong["class"] = strong.get("class", []) + ["stat-compare"]


def wrap_grade_badges(soup: BeautifulSoup) -> None:
    """Biến cột 'Mức chứng cứ' của bảng tóm tắt hành động thành huy hiệu màu."""
    for table in soup.find_all("table"):
        header_row = table.find("tr")
        if not header_row:
            continue
        header_cells = header_row.find_all(["th"])
        headers = [c.get_text(strip=True) for c in header_cells]
        if "Mức chứng cứ" not in headers:
            continue
        for tr in table.find_all("tr")[1:]:
            tds = tr.find_all("td")
            if len(tds) != 3:
                continue
            grade_td = tds[-1]
            p = grade_td.find("p") or grade_td
            text = p.get_text(strip=True)
            if not text:
                continue
            m = GRADE_RE.match(text)
            if m:
                cls, level, rest = m.group(1), m.group(2), m.group(3).strip()
                badge_cls = "grade-strong" if cls == "I" else "grade-moderate"
                p.clear()
                badge = soup.new_tag("span", **{"class": f"grade-badge {badge_cls}"})
                badge.string = f"{cls}, {level}"
                p.append(badge)
                if rest:
                    p.append(NavigableString(" " + rest))
            else:
                p.clear()
                badge = soup.new_tag("span", **{"class": "grade-badge grade-info"})
                badge.string = text
                p.append(badge)


def build(src_path: str, out_path: str, title: str | None,
          eyebrow_date: str, footer_date: str) -> int:
    raw = open(src_path, encoding="utf-8").read()
    soup = BeautifulSoup(raw, "html.parser")
    body_children = list(soup.body.children)

    # --- 1. masthead: 4 <p> đầu tiên trước bảng đầu tiên — xem "GIỚI HẠN"
    # ở docstring nếu tài liệu không có bố cục này. ---
    masthead_ps = []
    idx = 0
    for i, el in enumerate(body_children):
        if getattr(el, "name", None) == "table":
            idx = i
            break
        if getattr(el, "name", None) == "p":
            masthead_ps.append(el)

    title_text = masthead_ps[0].get_text(strip=True)
    subtitle_text = masthead_ps[1].get_text(strip=True) if len(masthead_ps) > 1 else ""
    meta_text = masthead_ps[2].get_text(strip=True) if len(masthead_ps) > 2 else ""
    disclaimer_text = masthead_ps[3].get_text(strip=True) if len(masthead_ps) > 3 else ""
    page_title = title or title_text

    # --- 2. bảng cảnh báo: bảng đầu tiên — xem "GIỚI HẠN" ở docstring. ---
    warn_table = body_children[idx]
    warn_th = warn_table.find("th")
    warn_title_p = warn_th.find("p") if warn_th else None
    warn_title = warn_title_p.get_text(strip=True) if warn_title_p else ""
    warn_title = re.sub(r"^[⚠️⚠\s]+", "", warn_title).strip()
    warn_items = []
    if warn_th:
        for p in warn_th.find_all("p")[1:]:
            txt = p.decode_contents()
            txt = re.sub(r'<span[^>]*><strong>•\s*</strong></span>', '', txt)
            warn_items.append(txt.strip())

    rest = body_children[idx + 1:]
    rest_soup = BeautifulSoup("", "html.parser")
    for el in rest:
        rest_soup.append(el)

    # thứ tự có ý nghĩa: huy hiệu trước recolor (đọc chữ thường), stat sau
    # recolor (recolor chỉ chạm <span style>, không ảnh hưởng chữ thống kê),
    # pct-compare trên <strong> trước stats để tránh bọc chồng.
    wrap_grade_badges(rest_soup)
    recolor(rest_soup)
    wrap_pct_compare(rest_soup)
    n_stats = wrap_stats(rest_soup)

    toc = []
    for h1 in rest_soup.find_all("h1"):
        label = h1.get_text(strip=True)
        anchor = slugify(label)[:60] or f"sec-{len(toc)+1}"
        h1["id"] = anchor
        toc.append((anchor, label))

    for table in rest_soup.find_all("table"):
        header_row = table.find("tr")
        ncols = len(header_row.find_all(["th", "td"])) if header_row else 0
        for tr in table.find_all("tr"):
            cells = tr.find_all(["th", "td"])
            if ncols > 1 and len(cells) == 1 and cells[0].name == "td":
                cells[0]["colspan"] = str(ncols)
                cells[0]["class"] = cells[0].get("class", []) + ["row-label"]
        wrapper = rest_soup.new_tag("div", **{"class": "table-wrap"})
        table.wrap(wrapper)

    content_html = rest_soup.decode()

    toc_html = "\n".join(
        f'<a href="#{a}"><span class="toc-num">{i+1:02d}</span>{t}</a>'
        for i, (a, t) in enumerate(toc)
    )
    warn_items_html = "\n".join(f'<li>{it}</li>' for it in warn_items)

    page = TEMPLATE.format(
        page_title=page_title,
        eyebrow_date=eyebrow_date,
        title_text=title_text,
        subtitle_text=subtitle_text,
        meta_text=meta_text,
        disclaimer_text=disclaimer_text,
        warn_title=warn_title,
        warn_items_html=warn_items_html,
        toc_html=toc_html,
        content_html=content_html,
        footer_date=footer_date,
    )
    open(out_path, "w", encoding="utf-8").write(page)
    print(f"wrote {out_path} — {len(page)} chars — {n_stats} chip chứng cứ — {len(toc)} mục lục")
    return n_stats


TEMPLATE = r"""<title>{page_title}</title>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,500;0,8..60,600;0,8..60,700;1,8..60,400;1,8..60,600&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root {{
  --bg: #F3F6FB;
  --surface: #FFFFFF;
  --surface-2: #FBFCFE;
  --ink: #101B2D;
  --ink-2: #3C4A63;
  --ink-3: #6B7686;
  --line: #DCE3EE;
  --line-strong: #B9C4D6;
  --accent: #1E3A5F;
  --accent-ink: #FFFFFF;
  --accent-soft: #E6ECF6;
  --danger: #B91C1C;
  --danger-soft: #FDEDEC;
  --danger-ink: #7F1414;
  --good: #15803D;
  --good-soft: #E9F7EF;
  --good-ink: #0F5C2C;
  --warn: #B45309;
  --warn-soft: #FDF3E2;
  --warn-ink: #8A3E06;
  --cite: #2563EB;
  --cite-soft: #EAF1FE;
  --data: #0F766E;
  --data-soft: #E4F5F3;
  --data-ink: #0B5C56;
  --shadow: 0 1px 2px rgba(16,27,45,.04), 0 8px 24px -12px rgba(16,27,45,.18);
  --serif: "Source Serif 4", Georgia, "Times New Roman", serif;
  --sans: "IBM Plex Sans", "Segoe UI", Helvetica, Arial, sans-serif;
  --mono: "IBM Plex Mono", "SF Mono", Consolas, monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --bg: #0A1220;
    --surface: #101B2E;
    --surface-2: #0D1729;
    --ink: #E7ECF5;
    --ink-2: #AEBBD1;
    --ink-3: #7E8CA3;
    --line: #223050;
    --line-strong: #324566;
    --accent: #8FB2E0;
    --accent-ink: #0A1220;
    --accent-soft: #182741;
    --danger: #F2867E;
    --danger-soft: #2A1417;
    --danger-ink: #FBC7C2;
    --good: #6BDB9B;
    --good-soft: #0F2419;
    --good-ink: #B7F0CD;
    --warn: #F3B860;
    --warn-soft: #2A2010;
    --warn-ink: #F9D8A0;
    --cite: #8EB2FB;
    --cite-soft: #131F38;
    --data: #5EEAD4;
    --data-soft: #0D2B28;
    --data-ink: #9BF3E4;
    --shadow: 0 1px 2px rgba(0,0,0,.3), 0 12px 28px -14px rgba(0,0,0,.6);
  }}
}}
:root[data-theme="dark"] {{
  --bg: #0A1220;
  --surface: #101B2E;
  --surface-2: #0D1729;
  --ink: #E7ECF5;
  --ink-2: #AEBBD1;
  --ink-3: #7E8CA3;
  --line: #223050;
  --line-strong: #324566;
  --accent: #8FB2E0;
  --accent-ink: #0A1220;
  --accent-soft: #182741;
  --danger: #F2867E;
  --danger-soft: #2A1417;
  --danger-ink: #FBC7C2;
  --good: #6BDB9B;
  --good-soft: #0F2419;
  --good-ink: #B7F0CD;
  --warn: #F3B860;
  --warn-soft: #2A2010;
  --warn-ink: #F9D8A0;
  --cite: #8EB2FB;
  --cite-soft: #131F38;
  --data: #5EEAD4;
  --data-soft: #0D2B28;
  --data-ink: #9BF3E4;
  --shadow: 0 1px 2px rgba(0,0,0,.3), 0 12px 28px -14px rgba(0,0,0,.6);
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: var(--serif);
  font-size: 17px;
  line-height: 1.65;
  -webkit-font-smoothing: antialiased;
}}
a {{ color: var(--cite); }}
a:focus-visible, button:focus-visible {{ outline: 2px solid var(--cite); outline-offset: 2px; }}
::selection {{ background: var(--accent-soft); }}

/* ---------- masthead ---------- */
.masthead {{
  background: var(--accent);
  color: var(--accent-ink);
  padding: 3.2rem 1.5rem 2.4rem;
}}
.masthead-inner {{ max-width: 900px; margin: 0 auto; }}
.eyebrow {{
  font-family: var(--sans);
  font-size: .72rem;
  font-weight: 600;
  letter-spacing: .12em;
  text-transform: uppercase;
  opacity: .78;
  margin: 0 0 .9rem;
}}
.masthead h1 {{
  font-family: var(--serif);
  font-weight: 700;
  font-size: clamp(1.9rem, 3.6vw, 2.6rem);
  line-height: 1.16;
  margin: 0 0 .7rem;
  text-wrap: balance;
  max-width: 22ch;
}}
.masthead .subtitle {{
  font-family: var(--serif);
  font-style: italic;
  font-size: 1.1rem;
  opacity: .92;
  margin: 0 0 1.3rem;
  max-width: 52ch;
}}
.meta-row {{
  display: flex;
  flex-wrap: wrap;
  gap: .5rem 1.2rem;
  font-family: var(--sans);
  font-size: .86rem;
  opacity: .88;
  border-top: 1px solid rgba(255,255,255,.22);
  padding-top: 1rem;
}}
.meta-row .disclaimer {{
  font-family: var(--sans);
  font-weight: 600;
  color: #FFE3B0;
}}

/* ---------- callout ---------- */
.callout {{
  max-width: 900px;
  margin: 1.8rem auto 0;
  padding: 0 1.5rem;
}}
.callout-box {{
  background: var(--danger-soft);
  border: 1px solid color-mix(in srgb, var(--danger) 35%, transparent);
  border-left: 4px solid var(--danger);
  border-radius: 10px;
  padding: 1.1rem 1.3rem 1.2rem;
}}
.callout-box .callout-title {{
  font-family: var(--sans);
  font-weight: 700;
  font-size: .92rem;
  color: var(--danger-ink);
  margin: 0 0 .6rem;
  display: flex;
  align-items: center;
  gap: .45rem;
}}
.callout-box ul {{
  margin: 0;
  padding: 0 0 0 1.15rem;
  font-family: var(--sans);
  font-size: .87rem;
  line-height: 1.55;
  color: var(--ink-2);
}}
.callout-box li + li {{ margin-top: .5rem; }}
.callout-box li::marker {{ color: var(--danger); }}
.callout-box strong {{ color: var(--ink); }}

/* ---------- layout ---------- */
.layout {{
  max-width: 1220px;
  margin: 2.6rem auto 4rem;
  padding: 0 1.5rem;
  display: grid;
  grid-template-columns: 240px minmax(0, 1fr);
  gap: 2.6rem;
  align-items: start;
}}
.toc {{
  position: sticky;
  top: 1.4rem;
  align-self: start;
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-family: var(--sans);
  max-height: calc(100vh - 2.8rem);
  overflow-y: auto;
  padding-right: .4rem;
}}
.toc-label {{
  font-size: .68rem;
  font-weight: 700;
  letter-spacing: .1em;
  text-transform: uppercase;
  color: var(--ink-3);
  margin: 0 0 .5rem .6rem;
}}
.toc a {{
  color: var(--ink-2);
  text-decoration: none;
  font-size: .85rem;
  line-height: 1.3;
  padding: .42rem .6rem;
  border-radius: 7px;
  display: flex;
  gap: .55rem;
  align-items: baseline;
}}
.toc a:hover {{ background: var(--accent-soft); color: var(--ink); }}
.toc-num {{
  font-family: var(--mono);
  font-size: .72rem;
  color: var(--ink-3);
  flex-shrink: 0;
}}

.content {{ min-width: 0; }}
/* giới hạn đọc áp cho VĂN BẢN, không cho cả cột — để bảng, callout và các
   khối full-bleed dùng trọn track thay vì để trống một khoảng trắng khi
   màn hình rộng (đây chính là điều bác sĩ phản hồi "chưa cân đối"). */
.content > p, .content > ul {{ max-width: 68ch; }}

/* ---------- kiểu chữ trong nội dung ---------- */
.content h1 {{
  font-family: var(--serif);
  font-weight: 700;
  font-size: 1.65rem;
  line-height: 1.25;
  color: var(--accent);
  margin: 3rem 0 1.1rem;
  padding-top: 1.6rem;
  border-top: 1px solid var(--line);
  text-wrap: balance;
  scroll-margin-top: 1.2rem;
  max-width: 40ch;
}}
.content h1:first-child {{ margin-top: 0; padding-top: 0; border-top: none; }}
.content h2 {{
  font-family: var(--sans);
  font-weight: 700;
  font-size: 1.02rem;
  color: var(--ink);
  margin: 2.1rem 0 .8rem;
  padding-bottom: .5rem;
  border-bottom: 2px solid var(--accent-soft);
  max-width: 68ch;
}}
.content h3 {{
  font-family: var(--sans);
  font-weight: 600;
  font-style: normal !important;
  font-size: .92rem;
  color: var(--ink-2);
  letter-spacing: .01em;
  margin: 1.7rem 0 .6rem;
  max-width: 68ch;
}}
.content h3 em {{ font-style: normal; }}
.content h4 {{
  font-family: var(--sans);
  font-weight: 700;
  font-size: .84rem;
  text-transform: uppercase;
  letter-spacing: .08em;
  color: var(--ink-3);
  margin: 1.6rem 0 .6rem;
}}
.content p {{ margin: 0 0 1.05rem; color: var(--ink); }}
.content ul {{ margin: 0 0 1.2rem; padding-left: 1.3rem; }}
.content li {{ margin-bottom: .55rem; max-width: 68ch; }}
.content li::marker {{ color: var(--accent); }}
.content strong {{ font-weight: 600; color: var(--ink); }}
.content em {{ font-style: italic; }}
.content .c-muted, .content .c-muted3 {{ color: var(--ink-3); }}
.content .c-muted2 {{ color: var(--ink-2); }}
.content .c-accent {{ color: var(--accent); }}
.content .c-danger {{ color: var(--danger); }}
.content .c-good {{ color: var(--good); }}
.content .c-warn {{ color: var(--warn); }}
.content .c-cite {{
  font-family: var(--mono);
  font-size: .82em;
  color: var(--cite);
  background: var(--cite-soft);
  padding: .05em .35em;
  border-radius: 4px;
  font-variant-numeric: tabular-nums;
}}
.content .c-onaccent {{ color: var(--accent-ink); }}

/* ---------- điểm nhấn chứng cứ ---------- */
.content .stat {{
  display: inline-block;
  font-family: var(--mono);
  font-size: .82em;
  font-weight: 500;
  font-variant-numeric: tabular-nums;
  color: var(--data-ink);
  background: var(--data-soft);
  border: 1px solid color-mix(in srgb, var(--data) 32%, transparent);
  padding: .08em .5em;
  border-radius: 5px;
  line-height: 1.5;
  white-space: nowrap;
}}
.content .stat-compare {{
  font-variant-numeric: tabular-nums;
  text-decoration: underline;
  text-decoration-color: color-mix(in srgb, var(--data) 45%, transparent);
  text-decoration-thickness: 2px;
  text-underline-offset: 3px;
}}
.grade-badge {{
  display: inline-block;
  font-family: var(--sans);
  font-weight: 700;
  font-size: .78rem;
  padding: .28em .65em;
  border-radius: 999px;
  white-space: nowrap;
  line-height: 1.4;
}}
.grade-badge.grade-strong {{
  background: var(--good-soft); color: var(--good-ink);
  border: 1px solid color-mix(in srgb, var(--good) 40%, transparent);
}}
.grade-badge.grade-moderate {{
  background: var(--warn-soft); color: var(--warn-ink);
  border: 1px solid color-mix(in srgb, var(--warn) 40%, transparent);
}}
.grade-badge.grade-info {{
  background: var(--data-soft); color: var(--data-ink);
  border: 1px solid color-mix(in srgb, var(--data) 40%, transparent);
}}

/* ---------- bảng ---------- */
.table-wrap {{
  overflow-x: auto;
  margin: 0 0 1.8rem;
  border: 1px solid var(--line);
  border-radius: 10px;
  box-shadow: var(--shadow);
  background: var(--surface);
  max-height: 560px;
  overflow-y: auto;
}}
table {{
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-family: var(--sans);
  font-size: .85rem;
}}
th, td {{
  padding: .72rem .9rem;
  text-align: left;
  vertical-align: top;
  border-bottom: 1px solid var(--line);
  line-height: 1.5;
}}
th {{
  position: sticky;
  top: 0;
  z-index: 1;
  font-weight: 700;
  font-size: .72rem;
  letter-spacing: .05em;
  text-transform: uppercase;
  background: var(--surface-2);
  color: var(--ink-2);
  white-space: nowrap;
  box-shadow: inset 0 -1px 0 var(--line-strong);
}}
th.bg-accent {{ background: var(--accent); color: var(--accent-ink); box-shadow: none; }}
tr:last-child td {{ border-bottom: none; }}
tbody tr:nth-child(even) td {{ background: var(--surface-2); }}
tr:hover td {{ background: var(--accent-soft) !important; }}
td.bg-good-soft {{ background: var(--good-soft) !important; }}
td.bg-cite-soft {{ background: var(--cite-soft) !important; }}
td p {{ margin: 0 0 .4em; }}
td p:last-child {{ margin-bottom: 0; }}
table strong {{ font-weight: 700; }}
td.row-label {{
  background: var(--accent-soft) !important;
  font-family: var(--sans);
  font-weight: 700;
  font-size: .76rem;
  letter-spacing: .02em;
  color: var(--accent);
  border-bottom: none;
  padding: .55rem .9rem .3rem;
}}
tr:has(> td.row-label) + tr:hover td {{ background: var(--accent-soft) !important; }}
tr:has(> td.row-label) + tr td {{ padding-top: .35rem; }}
tr:has(> td.row-label) + tr td:first-child {{ padding-left: 1.6rem; }}

/* ---------- chân trang ---------- */
.pagefoot {{
  max-width: 900px;
  margin: 3rem auto 0;
  padding: 1.4rem 1.5rem 0;
  border-top: 1px solid var(--line);
  font-family: var(--sans);
  font-size: .78rem;
  color: var(--ink-3);
  text-align: center;
}}

/* ---------- responsive ---------- */
@media (max-width: 880px) {{
  .layout {{ grid-template-columns: 1fr; }}
  .toc {{
    position: static;
    max-height: none;
    flex-direction: row;
    flex-wrap: wrap;
    gap: .3rem .5rem;
    border-bottom: 1px solid var(--line);
    padding-bottom: 1rem;
    margin-bottom: .5rem;
  }}
  .toc-label {{ width: 100%; }}
  .toc a {{ padding: .3rem .55rem; font-size: .78rem; background: var(--surface-2); }}
  .content > p, .content > ul, .content li {{ max-width: none; }}
}}
</style>

<header class="masthead">
  <div class="masthead-inner">
    <p class="eyebrow">Tổng thuật lâm sàng · Xác minh PubMed {eyebrow_date}</p>
    <h1>{title_text}</h1>
    <p class="subtitle">{subtitle_text}</p>
    <div class="meta-row">
      <span>{meta_text}</span>
      <span class="disclaimer">{disclaimer_text}</span>
    </div>
  </div>
</header>

<div class="callout">
  <div class="callout-box">
    <p class="callout-title">⚠ {warn_title}</p>
    <ul>
      {warn_items_html}
    </ul>
  </div>
</div>

<div class="layout">
  <nav class="toc" aria-label="Mục lục">
    <p class="toc-label">Mục lục</p>
    {toc_html}
  </nav>
  <main class="content">
    {content_html}
  </main>
</div>

<p class="pagefoot">Dựng lại {footer_date} từ bản .docx đã xác minh qua PubMed · Cần bác sĩ kiểm chứng trước khi áp dụng lâm sàng</p>
"""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("src", help="File HTML thô (docx→html) đầu vào")
    ap.add_argument("out", help="File HTML trang đọc kiểu Artifact xuất ra")
    ap.add_argument("--title", default=None, help="Tiêu đề trang (mặc định: lấy từ đoạn <p> đầu tiên)")
    ap.add_argument("--eyebrow-date", default=None, help="Ngày xác minh hiện ở dòng eyebrow, mặc định hôm nay")
    ap.add_argument("--footer-date", default=None, help="Ngày dựng lại hiện ở chân trang, mặc định hôm nay")
    args = ap.parse_args()

    today = datetime.date.today().strftime("%d/%m/%Y")
    build(
        args.src, args.out, args.title,
        eyebrow_date=args.eyebrow_date or today,
        footer_date=args.footer_date or today,
    )


if __name__ == "__main__":
    main()
