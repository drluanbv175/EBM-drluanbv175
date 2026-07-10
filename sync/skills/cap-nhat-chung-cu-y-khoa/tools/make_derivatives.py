#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_derivatives.py — TỰ ĐỘNG sinh 3 sản phẩm phái sinh từ một dashboard đã PASS cổng liêm chính.

Đầu ra (vào derivatives/):
  <slug>_to-dan-nguoi-benh.md   — BẢN NHÁP tờ dặn người bệnh (model/bác sĩ rà ngôn ngữ phổ thông, BỎ liều)
  <slug>_slide-outline.md       — dàn ý slide (FAITHFUL: giữ hiệu số + GRADE + PMID) → nạp skill slide ra .pptx
  <slug>_kich-ban-tiktok.md     — BẢN NHÁP kịch bản TikTok (rà ngôn ngữ; video thật: skill tao-video-tiktok)

Cách dùng (trong EBM-Dashboards/):
    python3 tools/make_derivatives.py WebDashboard_EBM_<...>.html

LƯU Ý LIÊM CHÍNH: tờ dặn & TikTok là BẢN NHÁP — rà lại để bỏ liều/thuật ngữ trước khi phát/đăng.
"""
import sys, os, re, argparse

GRADE = {"high": "Cao", "mod": "Trung bình", "low": "Thấp", "vlow": "Rất thấp", "na": "Không phân hạng"}
DEC = {"apply": "Áp dụng ngay", "consider": "Cân nhắc", "notyet": "Chưa đủ"}


def block(html):
    i = html.find("const DATA")
    return html[i:html.find("HẾT KHỐI DATA", i)] if i != -1 else html


def meta(b, name):
    m = re.search(name + r"\s*:\s*['\"]([^'\"]*)['\"]", b)
    return m.group(1) if m else ""


def arr(b, name):
    m = re.search(name + r"\s*:\s*\[(.*?)\]", b, re.S)
    if not m:
        return []
    return [x.group(1) for x in re.finditer(r"['\"]((?:[^'\"\\]|\\.)*)['\"]", m.group(1))]


def items(b):
    ipos = b.find("items:")
    seg = b[ipos:] if ipos != -1 else b
    starts = [m.start() for m in re.finditer(r"\{\s*id\s*:\s*['\"]", seg)]
    out = []
    for k, s in enumerate(starts):
        e = starts[k + 1] if k + 1 < len(starts) else len(seg)
        ch = seg[s:e]
        f = lambda n: (re.search(n + r"\s*:\s*['\"]([^'\"]*)['\"]", ch) or [None, ""])[1] if re.search(n + r"\s*:\s*['\"]([^'\"]*)['\"]", ch) else ""
        out.append({
            "title": f("title"), "source": f("source"), "pmid": f("pmid"),
            "effectText": f("effectText"), "grade": f("gradeLevel"), "decision": f("decision"),
        })
    return out


def slug_of(path):
    s = os.path.basename(path)
    s = re.sub(r"^WebDashboard_EBM_(VanDeCuThe_)?", "", s)
    s = re.sub(r"\.html$", "", s)
    return s or "capnhat"


def li(xs):
    return "\n".join("- " + x for x in xs) if xs else "- —"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--outdir", default="derivatives")
    a = ap.parse_args()

    html = open(a.file, encoding="utf-8").read()
    b = block(html)
    q = meta(b, "question") or "Vấn đề lâm sàng"
    upd = meta(b, "updated") or ""
    conclusion = meta(b, "conclusion")
    doNow, dontDo, redFlags = arr(b, "doNow"), arr(b, "dontDo"), arr(b, "redFlags")
    its = items(b)
    os.makedirs(a.outdir, exist_ok=True)
    slug = slug_of(a.file)

    # 1) Tờ dặn người bệnh (BẢN NHÁP)
    patient = """# TỜ DẶN NGƯỜI BỆNH — {q}
*Ngày: {upd}*

> **BẢN NHÁP TỰ ĐỘNG** — rà lại NGÔN NGỮ PHỔ THÔNG, **BỎ liều & thuật ngữ kỹ thuật**, trước khi in/phát.

**Tóm tắt**
{conclusion}

**Bạn nên làm**
{do}

**Đi khám ngay nếu**
{rf}

**Lưu ý**
{dont}

---
*Thông tin tham khảo — **không thay thế tư vấn của bác sĩ của bạn**.*
""".format(q=q, upd=upd, conclusion=conclusion or "—", do=li(doNow), rf=li(redFlags), dont=li(dontDo))

    # 2) Dàn ý slide (FAITHFUL — giữ kỹ thuật + PMID)
    rows = []
    for i, it in enumerate(its, 1):
        eff = (" — " + it["effectText"]) if it["effectText"] else ""
        gr = GRADE.get(it["grade"], it["grade"] or "")
        dc = DEC.get(it["decision"], it["decision"] or "")
        pm = (" · PMID " + it["pmid"]) if it["pmid"] else ""
        rows.append("{i}. **{t}**{eff} — *GRADE {gr} · {dc}*{pm} ({src})".format(
            i=i + 2, t=it["title"], eff=eff, gr=gr, dc=dc, pm=pm, src=it["source"]))
    slide = """# DÀN Ý SLIDE — {q}
*Nạp vào skill dao-tao-slide-tai-lieu-y-khoa để xuất .pptx. Giữ số liệu + PMID.*

1. **Tiêu đề:** Cập nhật chứng cứ — {q} ({upd})
2. **Tóm tắt thực hành:** {conclusion}
{rows}
{nslide}. **Cờ đỏ / chuyển tuyến:** {rf}
{nslide2}. **Tài liệu tham khảo (Vancouver) + disclaimer "Cần bác sĩ kiểm chứng"**

*Mọi số liệu trích đúng nguồn từ bản cập nhật đã PASS cổng liêm chính.*
""".format(q=q, upd=upd, conclusion=conclusion or "—", rows="\n".join(rows),
           nslide=len(its) + 3, nslide2=len(its) + 4, rf="; ".join(redFlags) or "—")

    # 3) Kịch bản TikTok (BẢN NHÁP)
    pts = doNow[:3]
    tiktok = """# KỊCH BẢN TIKTOK — {q} (~45s)
*Giọng: HoaiMy · Phụ đề động: bật · Overlay: "Thông tin tham khảo — không thay tư vấn bác sĩ"*

> **BẢN NHÁP TỰ ĐỘNG** — rà ngôn ngữ đời thường, **bỏ liều**. Video thật: skill `tao-video-tiktok`.

**[Hook]** {hook}

**[Nội dung]**
{pts}

**[Cảnh báo + chốt]** Đi khám ngay nếu: {rf} 👉 Hỏi bác sĩ của bạn.

---
*Bác sĩ duyệt trước khi đăng. Không dùng PII/ảnh bệnh nhân thật.*
""".format(q=q, hook=(conclusion[:90] + "…") if conclusion else q,
           pts="\n".join("• " + x for x in pts) or "• —", rf="; ".join(redFlags[:2]) or "—")

    written = []
    for suffix, content in [("to-dan-nguoi-benh", patient), ("slide-outline", slide), ("kich-ban-tiktok", tiktok)]:
        path = os.path.join(a.outdir, "%s_%s.md" % (slug, suffix))
        open(path, "w", encoding="utf-8").write(content)
        written.append(path)
        print("  + " + path)
    print("Đã sinh %d sản phẩm phái sinh. Slide=faithful; tờ dặn & TikTok = BẢN NHÁP cần rà ngôn ngữ phổ thông." % len(written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
