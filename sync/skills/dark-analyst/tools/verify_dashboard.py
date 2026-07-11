#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_dashboard.py — Cổng kiểm liêm chính cho Web Dashboard EBM (Dark Analyst / Evidence Workbench).

Kiểm TRƯỚC KHI GIAO cho bác sĩ:
  - Mỗi item có ≥1 định danh truy nguyên (pmid hoặc doi).
  - Mỗi item có gradeLevel + decision + references.
  - Có disclaimer "Cần bác sĩ kiểm chứng".
  - Quét dấu hiệu PII (cảnh báo để người rà — không tự ý kết luận).
  - DOI kiểm ĐỊNH DẠNG luôn (offline, mọi lượt chạy) — KHÔNG phân giải online (chưa gọi
    doi.org/Crossref; DOI đúng định dạng nhưng không tồn tại vẫn có thể lọt).
  - (Tùy chọn --online) Tự XÁC MINH mỗi PMID phân giải đúng qua NCBI E-utilities
    (miễn phí, không cần key) → chống trích dẫn ảo PMID.

Cách dùng:
    python3 verify_dashboard.py <dashboard.html>            # chỉ kiểm cấu trúc (offline)
    python3 verify_dashboard.py <dashboard.html> --online   # + xác minh PMID trên mạng

Mã thoát: 0 = PASS (không lỗi cứng), 1 = FAIL.
Lỗi cứng: item thiếu cả pmid lẫn doi; PMID/DOI sai định dạng; thiếu disclaimer; item thiếu
  gradeLevel/decision; items[] rỗng (TRỪ artifact tự khai báo kind:'cong-cu' = công cụ hỗ
  trợ quyết định, không phải danh sách thẻ chứng cứ — vẫn bắt buộc disclaimer + kiểm PII/nội dung);
  khi --online: PMID KHÔNG xác minh được (kể cả do lỗi mạng) — fail-closed, không coi lỗi
  mạng là PASS (vá 2026-07-11, trước đây fail-open: PMID bịa lọt qua nếu quét đúng lúc mất mạng).
Cảnh báo (không chặn): nghi PII.
"""
import sys, re, json, argparse, time
import urllib.error
import urllib.parse

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
    m = re.search(name + r"\s*:\s*['\"]([^'\"]*)['\"]", chunk)
    return m.group(1) if m else None


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
    liên tiếp dễ tạo cảnh báo giả hàng loạt."""
    import urllib.request
    url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
           "?db=pubmed&retmode=json&id=" + pmid)
    last_err = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(url, timeout=15) as r:
                j = json.loads(r.read().decode("utf-8"))
            res = j.get("result", {})
            if pmid in res and "title" in res[pmid]:
                return True, res[pmid].get("title", "")[:90]
            return False, "không có trong PubMed"
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(1.5 * (attempt + 1))
                continue
            return None, "lỗi mạng: %s" % e
        except Exception as e:
            return None, "lỗi mạng: %s" % e
    return None, "lỗi mạng: hết lượt thử lại (%s)" % last_err


def main():
    configure_utf8_stdio()

    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--online", action="store_true",
                    help="xác minh PMID trên mạng qua NCBI (DOI chỉ kiểm định dạng offline, "
                         "KHÔNG phân giải online — chưa gọi doi.org/Crossref)")
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
    for ch in items:
        iid = field(ch, "id") or "(?)"
        pmid = field(ch, "pmid")
        doi = field(ch, "doi")
        url = field(ch, "url")
        grade = field(ch, "gradeLevel")
        dec = field(ch, "decision")
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
        if pmid:
            pmids.append((iid, pmid))
        if grade not in VALID_GRADE:
            errors.append("[%s] gradeLevel không hợp lệ: %r (cần %s)." % (iid, grade, VALID_GRADE))
        if dec not in VALID_DECISION:
            errors.append("[%s] decision không hợp lệ: %r (cần %s)." % (iid, dec, VALID_DECISION))
        if "references" not in ch:
            warns.append("[%s] không thấy references[]." % iid)

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
        oks.append("Đang xác minh %d PMID trên PubMed…" % len(set(p for _, p in pmids)))
        seen = {}
        net_calls = 0
        for iid, p in pmids:
            if p in seen:
                ok, info = seen[p]
            else:
                # Giãn cách ~3 req/s (NCBI E-utilities không key) để tránh TỰ gây rate-limit
                # khi quét nhiều PMID liên tiếp, thay vì chỉ phản ứng bằng retry sau đó.
                if net_calls:
                    time.sleep(0.34)
                net_calls += 1
                ok, info = verify_pmid_online(p)
                seen[p] = (ok, info)
            if ok is True:
                oks.append("[%s] PMID %s ✓ %s" % (iid, p, info))
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
        oks.append("Có %d PMID (chạy --online để xác minh phân giải)." % len(set(p for _, p in pmids)))

    # 4) CHẤT LƯỢNG NỘI DUNG — chống rác abstract NGOẠI NGỮ / placeholder (xem dashboard_content_audit.py)
    try:
        import os as _os, sys as _sys
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
    elif 3 <= n < 8:
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
            import os as _os, sys as _sys
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

    return report(errors, warns, oks)


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
        return 1
    print("KẾT QUẢ: ✓ PASS — 0 lỗi cứng, %d cảnh báo (rà tay nếu có)." % len(warns))
    return 0


if __name__ == "__main__":
    sys.exit(main())
