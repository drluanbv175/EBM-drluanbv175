#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
surveillance_scan.py — GIÁM SÁT định kỳ (Track B) chứng cứ mới theo chủ đề lõi.

Với mỗi chủ đề trong watchlist.json, truy vấn PubMed (E-utilities, MIỄN PHÍ) tìm tài liệu
CHẤT LƯỢNG CAO (guideline / systematic review / meta-analysis / RCT) MỚI trong N ngày gần đây,
in báo cáo ứng viên (PMID · ngày · tiêu đề) để BÁC SĨ rà soát — KHÔNG tự kết luận đổi thực hành.

Cách dùng (chạy trong EBM-Dashboards/):
    python3 tools/surveillance_scan.py                      # 90 ngày, watchlist.json
    python3 tools/surveillance_scan.py --days 30 --max 8
    python3 tools/surveillance_scan.py --report surveillance_2026-06-07.md

CẦN MẠNG. Kết quả là ỨNG VIÊN để thẩm định, không phải khuyến cáo.
"""
import sys, os, re, json, argparse, urllib.request, urllib.parse

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
DESIGN = '(Guideline[ptyp] OR "systematic review"[ptyp] OR meta-analysis[ptyp] OR "practice guideline"[ptyp] OR randomized controlled trial[ptyp])'


def get_json(url):
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def search(query, days, retmax):
    term = "(%s) AND %s" % (query, DESIGN)
    url = EUTILS + "esearch.fcgi?db=pubmed&retmode=json&sort=date&reldate=%d&datetype=pdat&retmax=%d&term=%s" % (
        days, retmax, urllib.parse.quote(term))
    j = get_json(url)
    return j.get("esearchresult", {}).get("idlist", [])


def summarize(ids):
    if not ids:
        return []
    url = EUTILS + "esummary.fcgi?db=pubmed&retmode=json&id=" + ",".join(ids)
    res = get_json(url).get("result", {})
    out = []
    for pid in res.get("uids", []):
        a = res.get(pid, {})
        out.append((pid, a.get("pubdate", ""), a.get("title", "").strip()))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--watchlist", default="watchlist.json")
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--max", type=int, default=6)
    ap.add_argument("--report", default=None)
    a = ap.parse_args()

    wl = json.load(open(a.watchlist, encoding="utf-8"))
    topics = [t for t in wl.get("topics", []) if t.get("active", True)]

    lines = ["# Giám sát định kỳ — chứng cứ mới (%d ngày gần đây)" % a.days,
             "_Nguồn: PubMed E-utilities. ỨNG VIÊN để thẩm định — KHÔNG phải khuyến cáo. Cần bác sĩ kiểm chứng._", ""]
    total = 0
    for t in topics:
        lines.append("## %s" % t["topic"])
        try:
            ids = search(t["query"], a.days, a.max)
            rows = summarize(ids)
        except Exception as e:
            lines.append("- (lỗi truy vấn: %s)" % e); lines.append(""); continue
        if not rows:
            lines.append("- Không có tài liệu chất lượng cao mới.")
        for pid, date, title in rows:
            total += 1
            lines.append("- **%s** · PMID %s · https://pubmed.ncbi.nlm.nih.gov/%s/" % (date, pid, pid))
            lines.append("  - %s" % title)
        lines.append("")
    lines.append("---")
    lines.append("Tổng %d ứng viên trên %d chủ đề. Bước tiếp: chọn mục liên quan → chạy skill cập nhật chứng cứ để thẩm định đầy đủ." % (total, len(topics)))

    report = "\n".join(lines)
    print(report)
    if a.report:
        open(a.report, "w", encoding="utf-8").write(report)
        print("\n[Đã lưu báo cáo: %s]" % a.report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
