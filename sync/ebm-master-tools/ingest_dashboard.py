#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ingest_dashboard.py — Nạp các item từ một Web Dashboard (đã PASS cổng liêm chính) vào sổ cái
EBM_MASTER.json dưới dạng Evidence Card. Dùng để DI TRÚ dashboard cũ vào sổ cái trung tâm.

Liêm chính: chỉ nạp nội dung ĐÃ có sẵn trong dashboard (không bịa thêm). Backup trước khi ghi.
Chống trùng theo (pmid|doi|title). provenance="from_doctor_master".

Cách dùng (trong thư mục EBM_MASTER/):
    python3 tools/ingest_dashboard.py <đường-dẫn-dashboard.html> [--today YYYY-MM-DD]
    python3 tools/ingest_dashboard.py a.html b.html --today 2026-06-09

PHIÊN BẢN NỐI TIẾP (cùng lát cắt, khác ngày — vd ..._HopNhat_20260614 → ..._HopNhat_20261018):
    python3 tools/ingest_dashboard.py <bản-mới.html> --thay-ban <bản-cũ.html> --today YYYY-MM-DD
    python3 tools/ingest_dashboard.py <bản-mới.html> --noi-tiep --today YYYY-MM-DD   # tự tìm bản trước
  Mặc định CHẠY KHÔ (in kế hoạch, không ghi gì); thêm --ap-dung để ghi sau khi bác sĩ xem kế hoạch.
  Cập nhật TẠI CHỖ trường nội dung của thẻ bản cũ (giữ id/date_added/specialty/provenance, nối
  history); mục mới thì thêm; mục biến mất thì BÁO, không tự xoá.
  Nạp thường (sync_all.py) tự BỎ QUA bản cũ khi đã có bản mới hơn cùng lát cắt, và KHÔNG nạp bản
  mới khi bản trước đã có thẻ trong sổ cái mà chưa chạy nối tiếp (in đúng lệnh cần chạy).

NGUỒN CHUẨN (18/10/2026): tệp này sống trong git ở sync/ebm-master-tools/ của repo gốc; bản chạy
thật ở EBM_MASTER/tools/ được chép sang bằng tools/dong_bo_cong_cu_hub.py — sửa ở nguồn chuẩn,
KHÔNG sửa thẳng bản chạy thật (công cụ đồng bộ sẽ giữ lại bản bị sửa tay và báo bác sĩ).
"""
import argparse
import copy
import difflib
import json
import os
import re
import shutil
import sys
import unicodedata

from ledger_ids import assert_unique, max_ledger_seq

# Windows: stdout mặc định cp1252 giết print() tiếng Việt — ép UTF-8 (chốt BH55/R4)
import sys as _sys_r4
for _s_r4 in (_sys_r4.stdout, _sys_r4.stderr):
    try:
        _s_r4.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

# Vá 2026-07-16 (round audit đối kháng 3): trước bản vá này, ingest_dashboard.py KHÔNG quét
# PII của bất kỳ trường nào trước khi ghi thẳng vào sổ cái trung tâm EBM_MASTER.json — dù
# CLAUDE.md quy định "python3 tools/verify_dashboard.py <file>.html --online" phải PASS
# TRƯỚC khi gọi tool này, đó là bước THỦ CÔNG riêng (có thể bị bỏ qua khi ai đó — người hay
# agent — chạy thẳng sync_all.py/ingest_dashboard.py). Thêm lớp quét PHÒNG THỦ THEO CHIỀU SÂU
# ở ĐÂY, ngay trước khi ghi — cùng công thức heuristic với verify_dashboard.py (giữ nhất
# quán), CHỈ CẢNH BÁO (không tự ý chặn/xóa nội dung) đúng triết lý đã ghi trong docstring của
# verify_dashboard.py ("cảnh báo để người rà — không tự ý kết luận"): nội dung dashboard là
# tóm tắt guideline/chứng cứ CẤP QUẦN THỂ, không phải hồ sơ bệnh nhân cá nhân, nên heuristic
# regex có thể dương tính giả (vd ví dụ minh họa "bệnh nhân nam 65 tuổi, HbA1c 8%") — tự động
# chặn cứng ở đây rủi ro làm mất chứng cứ hợp lệ hơn là lợi ích chống PII mang lại.
_PII_HEURISTIC_PATTERNS = [
    re.compile(r"\b\d{1,2}/\d{1,2}/\d{4}\b"),          # ngày dạng dd/mm/yyyy
    re.compile(r"\b0\d{9}\b"),                          # SĐT VN
    re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),            # email
    re.compile(r"\bCCCD|CMND|số\s*BHYT|mã\s*BN|MRN\b", re.I),
]


def _pii_scan_text(text):
    """Trả danh sách chuỗi khớp mẫu PII nghi ngờ trong `text` (chuẩn hóa NFC trước khi so
    khớp — cùng lớp lỗi NFD-bypass đã vá ở nơi khác trong hệ, xem tools/gate_contract.py)."""
    if not text:
        return []
    normalized = unicodedata.normalize("NFC", str(text))
    hits = []
    for pat in _PII_HEURISTIC_PATTERNS:
        hits += pat.findall(normalized)
    return hits


def _card_pii_warnings(card):
    """Quét các trường VĂN BẢN TỰ DO của một evidence card sắp ghi vào sổ cái (topic,
    khuyến cáo, bối cảnh VN, PICO, thực hành) — bỏ qua trường có cấu trúc (id/pmid/doi/url)
    vốn không phải nơi PII rơi vào theo cách này."""
    fields = [
        card.get("topic", ""),
        card.get("recommendation", ""),
        card.get("vietnam_context", ""),
        card.get("pico_question", ""),
    ]
    pico = card.get("pico") or {}
    fields += [pico.get("population", ""), pico.get("intervention", ""),
               pico.get("comparison", ""), pico.get("outcome", "")]
    practice = card.get("practice") or {}
    fields += [practice.get("action", ""), practice.get("monitoring", ""), practice.get("safety", "")]
    hits = []
    for f in fields:
        hits += _pii_scan_text(f)
    return hits

# Audit 2026-07-11 (vòng 8): key_of() trùng (cùng DOI/PMID) KHÔNG đồng nghĩa trùng NỘI DUNG
# — một guideline dài hợp lệ trích NHIỀU khuyến cáo khác nhau từ CÙNG một DOI/PMID (vd GOLD
# COPD, EULAR RA — xem integrity_guard.py::duplicate_content_keys()). Trước bản vá này,
# ingest_dashboard.py coi MỌI key trùng là trùng thật và BỎ QUA thẻ mới vô điều kiện.
#
# SỬA 2026-07-21 (vòng lặp kiểm tra-hoàn thiện vòng 5, phát hiện HIGH): ngưỡng 0.5 (copy từ
# integrity_guard.py "để nhất quán") thực ra KHÔNG an toàn ở ĐÂY — 2 hàm có rủi ro khác hẳn
# nhau khi vượt ngưỡng. integrity_guard.py::duplicate_content_keys() CHỈ BÁO CÁO cho bác sĩ rà
# (không xoá gì) nên sai dương chỉ tốn 1 dòng review. Ở ĐÂY, vượt ngưỡng nghĩa là ÂM THẦM BỎ
# thẻ mới (chỉ bù pmid/doi rỗng của thẻ cũ, mất toàn bộ nội dung khuyến cáo mới) — sai dương là
# MẤT DỮ LIỆU KHÔNG PHỤC HỒI ĐƯỢC. Thực nghiệm đối kháng cho thấy các cặp khuyến cáo TRÁI NGƯỢC
# nhau về mặt lâm sàng (vd "khởi đầu liều X" vs "ngừng dùng X", "ưu tiên" vs "KHÔNG được khuyến
# cáo") nhưng dùng chung phần lớn từ vựng (cùng thuốc/quần thể/bệnh) đạt độ giống SequenceMatcher
# 0.73–0.88 — TRÙNG dải với các cặp trùng-thật đã hiệu chỉnh ở integrity_guard.py (0.72–0.85):
# độ giống ký tự thô không đủ phân biệt ngữ nghĩa "giống nhau" khỏi "trái ngược nhau" trong dải
# này. Vì hậu quả sai dương ở đây nặng hơn hẳn (mất dữ liệu vs. review thừa), nâng ngưỡng lên
# cao hơn HẲN dải đã biết có lẫn cặp trái ngược — chấp nhận hệ quả phụ là một số trùng-thật nhẹ
# (diễn đạt lại chút ít, dải 0.72–0.94) sẽ KHÔNG còn được tự gộp mà nạp thành thẻ riêng; đây
# không phải mất dữ liệu (thẻ vẫn vào evidence_cards) — integrity_guard.py::duplicate_content_
# keys() (ngưỡng 0.5, giữ NGUYÊN, cố ý KHÔNG nâng theo vì hàm đó không xoá gì) vẫn bắt được và
# báo cho bác sĩ gộp tay nếu đúng là trùng. CỐ Ý không dùng chung ngưỡng với integrity_guard.py
# nữa — 2 hàm có rủi ro khác nhau nên xứng đáng có ngưỡng khác nhau.
SIMILARITY_THRESHOLD = 0.95


def _topic_similarity(a, b):
    """0..1 — độ giống văn bản thô (SequenceMatcher), khớp integrity_guard.py::_topic_similarity."""
    return difflib.SequenceMatcher(None, (a or "").lower(), (b or "").lower()).ratio()


_JS_ESCAPES = {
    "'": "'", '"': '"', "\\": "\\", "/": "/",
    "n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f",
}


def _unescape_js_string(raw):
    """SỬA 2026-07-21 (vòng lặp kiểm tra-hoàn thiện vòng 5, phát hiện MEDIUM): bản
    cũ (2 lệnh .replace() nối tiếp cho \\' \\" \\\\) BỎ SÓT mọi escape JS hợp lệ khác
    — \\/ (hay gặp khi chuỗi nguồn được json_encode()/PHP tạo, escape luôn dấu /),
    \\n \\t \\r \\b \\f, và \\uXXXX — để nguyên dấu backslash trong kết quả, sai
    ngay với lời khẳng định trong docstring cũ ("không còn dấu \\"). Nguy hiểm nhất
    ở trường doi/url: 'doi: "10.1001\\/jama.2024.99999"' (JS hợp lệ) từng bị grab()
    trả về NGUYÊN backslash — giá trị đó đi thẳng vào key_of()/_norm_doi() (khoá
    chống trùng) và các cổng xác minh Crossref/PubMed downstream, làm hỏng cả dedup
    lẫn xác minh mà không hề báo lỗi (đọc sai trong im lặng, nguy hiểm hơn crash).
    Quét từng ký tự một lượt duy nhất (không dùng .replace() nối tiếp — thứ tự xử lý
    sai có thể làm hỏng lẫn nhau, vd \\\\' bị hiểu nhầm) để giải mã ĐÚNG mọi escape
    JS hợp lệ theo chuẩn; escape không nhận diện được thì giữ nguyên (an toàn, không
    đoán mò)."""
    out = []
    i, n = 0, len(raw)
    while i < n:
        c = raw[i]
        if c == "\\" and i + 1 < n:
            nxt = raw[i + 1]
            if nxt == "u" and i + 5 < n:
                hex4 = raw[i + 2:i + 6]
                try:
                    out.append(chr(int(hex4, 16)))
                    i += 6
                    continue
                except ValueError:
                    pass
            if nxt in _JS_ESCAPES:
                out.append(_JS_ESCAPES[nxt])
                i += 2
                continue
            # Escape không nhận diện được — giữ nguyên cả backslash lẫn ký tự sau,
            # không đoán mò.
            out.append(c)
            i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


def grab(chunk, key):
    # SỬA 2026-07-21 (vòng lặp kiểm tra-hoàn thiện vòng 4, phát hiện MEDIUM):
    # regex cũ [^'\"]* loại trừ CẢ hai loại dấu nháy khỏi nhóm bắt, bất kể
    # JS gốc dùng nháy đơn hay nháy kép để bao chuỗi — một chuỗi
    # title:"Cushing's syndrome update" bị cắt cụt tại dấu nháy đơn ĐẦU TIÊN
    # dù nó nằm TRONG cặp nháy kép hợp lệ (đã xác nhận thực nghiệm). Nay xác
    # định ĐÚNG ký tự mở chuỗi rồi chỉ dừng khi gặp ĐÚNG ký tự đó chưa escape.
    m = re.search(key + r"\s*:\s*(['\"])", chunk)
    if not m:
        return ""
    quote = m.group(1)
    j = m.end()
    while j < len(chunk):
        if chunk[j] == "\\" and j + 1 < len(chunk):
            j += 2
            continue
        if chunk[j] == quote:
            raw = chunk[m.end():j]
            return _unescape_js_string(raw).strip()
        j += 1
    return ""


def grab_block(chunk, key):
    """Lấy substring của object/array lồng (pico:{...} hoặc references:[...])."""
    m = re.search(key + r"\s*:\s*([\{\[])", chunk)
    if not m:
        return ""
    op = m.start(1)
    openc, closec = chunk[op], {"{": "}", "[": "]"}[chunk[op]]
    depth, j = 0, op
    while j < len(chunk):
        if chunk[j] == openc:
            depth += 1
        elif chunk[j] == closec:
            depth -= 1
            if depth == 0:
                return chunk[op:j + 1]
        j += 1
    return ""


def parse_dashboard(path):
    h = open(path, encoding="utf-8").read()
    i = h.find("const DATA")
    end = h.find("HẾT KHỐI DATA", i)
    block = h[i:end] if (i != -1 and end != -1) else h
    qm = re.search(r"question\s*:\s*['\"]([^'\"]*)['\"]", block)
    question = qm.group(1) if qm else os.path.basename(path)
    updated = grab(block, "updated")
    starts = [m.start() for m in re.finditer(r"\{\s*id\s*:\s*['\"]", block)]
    items = []
    for k, s in enumerate(starts):
        e = starts[k + 1] if k + 1 < len(starts) else len(block)
        ch = block[s:e]
        pico_b = grab_block(ch, "pico")
        fl_b = grab_block(ch, "frameLabels")
        frame_labels = {kk: grab(fl_b, kk) for kk in ["P", "I", "C", "O"] if grab(fl_b, kk)}
        items.append({
            "local_id": grab(ch, "id"),
            "title": grab(ch, "title"),
            "decision": grab(ch, "decision") or "notyet",
            "gradeLevel": grab(ch, "gradeLevel") or "na",
            "gradeSource": grab(ch, "gradeSource"),
            "pmid": grab(ch, "pmid"),
            "doi": grab(ch, "doi"),
            "url": grab(ch, "url"),
            "replacesPmid": grab(ch, "replacesPmid"),
            "replacementNoticePmid": grab(ch, "replacementNoticePmid"),
            "replacementNoticeDoi": grab(ch, "replacementNoticeDoi"),
            "org": grab(ch, "org"),
            "design": grab(ch, "design"),
            "effectText": grab(ch, "effectText"),
            "vn": grab(ch, "vn"),
            "dateVersion": grab(ch, "dateVersion"),
            "P": grab(pico_b, "P") or grab(ch, "population") or grab(ch, "P"),
            "I": grab(pico_b, "I") or grab(ch, "I"),
            "C": grab(pico_b, "C") or grab(ch, "C"),
            "O": grab(pico_b, "O") or grab(ch, "O"),
            "action": grab(ch, "action"),
            "monitoring": grab(ch, "monitoring"),
            "safety": grab(ch, "safety"),
            "frame": grab(ch, "frame"),
            "frameLabels": frame_labels,
        })
    return question, updated, items


def _norm_doi(doi):
    """Chuẩn hoá DOI để so trùng: bỏ tiền tố URL, hạ chữ thường (DOI không phân
    biệt hoa/thường) — audit 2026-07-11: so thô trước đây có thể bỏ lọt trùng
    chỉ khác định dạng (vd 'https://doi.org/10.X' vs '10.X')."""
    d = str(doi or "").strip()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi.org/", "doi:"):
        if d.lower().startswith(prefix):
            d = d[len(prefix):]
            break
    return d.strip().lower()


def key_of(card):
    s = card.get("source", {})
    return _norm_doi(s.get("doi")) or str(s.get("pmid") or "").strip() or card.get("topic", "")


def build_card(it, *, question, updated, dashboard_name, today, card_id):
    """Dựng Evidence Card từ MỘT item dashboard.

    Tách khỏi main() ngày 18/10/2026 để nạp thường và nạp PHIÊN BẢN NỐI TIẾP dùng CHUNG một
    định nghĩa trường nội dung — hai bản chép tay của khối này sẽ lệch nhau theo thời gian,
    đúng lớp lỗi kho này đã vấp nhiều lần."""
    # Vá 2026-07-10: GIỮ url (trước đây hardcode "" → thẻ guideline/quy định chỉ có
    # URL, không PMID/DOI, bị mất dấu truy nguyên → cách ly nhầm).
    source = {"agency": it["org"], "title": question, "url": it.get("url", ""),
              "pmid": it["pmid"], "doi": it["doi"], "type": "guideline/RCT"}
    card = {
        "id": card_id,
        "cycle": "from_dashboard",
        "date_added": today or "",
        "date_source": it["dateVersion"] or updated,
        "specialty": "",
        "topic": it["title"] or it["local_id"],
        "source": source,
        "provenance": "from_doctor_master",
        # 2026-07-12: "đã xác minh" ở ĐÂY nghĩa là NGUỒN/TRÍCH DẪN đã qua cổng liêm
        # chính TỰ ĐỘNG (verify_dashboard.py --online PASS chạy TRƯỚC khi gọi hàm
        # này) — KHÔNG phải "bác sĩ đã duyệt lâm sàng". Tín hiệu Cổng B thật (chờ/đã
        # duyệt) là trường "decision" bên dưới, luôn "notyet"/"consider" khi mới nạp
        # (không bao giờ tự "apply"). Quyết định thiết kế: xem _SO-EBM-MASTER.md.
        "verification_status": "đã xác minh",
        "pico": {"population": it["P"], "intervention": it["I"],
                 "comparison": it["C"], "outcome": it["O"]},
        "pico_question": ("%s — %s" % (it["I"], it["O"])).strip(" —") or it["title"],
        "recommendation": it.get("action") or it["title"],
        "certainty": it["gradeSource"],
        "operational_assessment": "Nhãn GRADE theo nguồn dashboard (đã PASS cổng liêm chính).",
        "gradeLevel": it["gradeLevel"],
        "decision": it["decision"],
        "vietnam_context": it["vn"],
        "frame": it.get("frame", ""),
        "frameLabels": it.get("frameLabels") or {},
        "practice": {
            "action": it.get("action", ""),
            "monitoring": it.get("monitoring", ""),
            "safety": it.get("safety", ""),
        },
        "critical_appraisal": {"design": it["design"], "effect_estimate": it["effectText"]},
        "references": [
            r for r in [
                it["pmid"] and ("PMID:" + it["pmid"]),
                it["doi"] and ("DOI:" + it["doi"]),
                it["replacementNoticePmid"] and ("PMID:" + it["replacementNoticePmid"]),
                it["replacementNoticeDoi"] and ("DOI:" + it["replacementNoticeDoi"]),
            ] if r
        ],
        "history": [{"date": today or "", "change": "nạp từ dashboard %s" % dashboard_name}],
    }
    if it["replacesPmid"]:
        card["replacement"] = {
            "supersedes_pmid": it["replacesPmid"],
            "notice_pmid": it["replacementNoticePmid"],
            "notice_doi": it["replacementNoticeDoi"],
            "status": "REPLACEMENT_REQUIRES_DOCTOR_REVIEW",
        }
    return card


def apply_explicit_replacement(data, card, replaces_pmid, *, today, dashboard_name):
    """Thay thẻ nguồn bị rút tại chỗ, giữ ID/lịch sử và quay về hàng bác sĩ duyệt.

    Chỉ chạy khi dashboard khai tường minh ``replacesPmid``. Nếu có nhiều thẻ cùng
    PMID cũ thì dừng fail-closed; máy không được đoán thẻ nào cần thay. Các bản trùng
    được hợp nhất chỉ khi chính ingest trước đó đã ghi lịch sử "nạp như thẻ mới".
    """
    replaces_pmid = str(replaces_pmid or "").strip()
    if not replaces_pmid:
        return False, 0
    cards = data.setdefault("evidence_cards", [])
    targets = [
        candidate
        for candidate in cards
        if str((candidate.get("source") or {}).get("pmid") or "").strip() == replaces_pmid
    ]
    if len(targets) > 1:
        raise RuntimeError(
            "Có %d thẻ cùng PMID bị thay %s; cần bác sĩ chọn thẻ đích."
            % (len(targets), replaces_pmid)
        )
    if not targets:
        return False, 0

    target = targets[0]
    old_id = target.get("id")
    old_date_added = target.get("date_added")
    old_specialty = target.get("specialty")
    old_history = list(target.get("history") or [])
    new_doi = _norm_doi((card.get("source") or {}).get("doi"))
    generated_duplicates = []
    for candidate in cards:
        if candidate is target:
            continue
        source = candidate.get("source") or {}
        if not new_doi or _norm_doi(source.get("doi")) != new_doi:
            continue
        if str(source.get("pmid") or "").strip():
            continue
        if _topic_similarity(card.get("topic", ""), candidate.get("topic", "")) < SIMILARITY_THRESHOLD:
            continue
        if any(
            "nạp như thẻ mới" in str(event.get("change") or "")
            for event in (candidate.get("history") or [])
            if isinstance(event, dict)
        ):
            generated_duplicates.append(candidate)

    replacement = dict(card)
    replacement["id"] = old_id
    replacement["date_added"] = old_date_added
    replacement["specialty"] = old_specialty or card.get("specialty", "")
    # Bản thay thế phải được bác sĩ duyệt lại; tuyệt đối không kế thừa/nâng apply.
    replacement["decision"] = "notyet"
    replacement["history"] = old_history + list(card.get("history") or []) + [
        {
            "date": today or "",
            "change": (
                "thay nguồn bị Retraction and Replacement PMID %s bằng bản đã sửa từ %s; "
                "giữ ID và đưa về notyet chờ bác sĩ duyệt lại."
                % (replaces_pmid, dashboard_name)
            ),
        }
    ]
    if generated_duplicates:
        replacement["history"].append(
            {
                "date": today or "",
                "change": "hợp nhất %d thẻ trùng do ingest cũ tạo khi chưa hiểu replacesPmid."
                % len(generated_duplicates),
            }
        )
    target.clear()
    target.update(replacement)
    duplicate_ids = {id(candidate) for candidate in generated_duplicates}
    if duplicate_ids:
        data["evidence_cards"] = [candidate for candidate in cards if id(candidate) not in duplicate_ids]
    return True, len(generated_duplicates)


def _has_traceability(card):
    """Chỉ coi là có truy nguyên khi có PMID/DOI/URL hoặc reference thật."""
    source = card.get("source") or {}
    if any(str(source.get(key) or "").strip() for key in ("pmid", "doi", "url")):
        return True
    references = card.get("references") or []
    return any(str(reference or "").strip() for reference in references)


def _normalized_topic(value):
    """Chuẩn hóa tối thiểu để khớp chính xác topic qua các lần ingest."""
    return " ".join(str(value or "").casefold().split())


def rehydrate_quarantined_card(data, card, *, today, dashboard_name):
    """Khôi phục thẻ cách ly khi dashboard gốc đã bổ sung nguồn truy nguyên.

    Ghép cặp phải đồng thời thỏa: topic khớp chính xác sau chuẩn hóa và history
    của thẻ cách ly ghi đúng dashboard đang nạp. Nếu có nhiều ứng viên thì dừng
    fail-closed. Thẻ khôi phục luôn về ``notyet`` và trạng thái chờ bác sĩ xác
    minh; việc bổ sung URL/DOI/PMID không được tự biến thành phê duyệt lâm sàng.
    """
    if not _has_traceability(card):
        return False
    quarantine = data.get("quarantined_cards") or []
    if not isinstance(quarantine, list):
        return False
    topic = _normalized_topic(card.get("topic"))
    if not topic:
        return False

    def came_from_dashboard(candidate):
        for event in candidate.get("history") or []:
            if dashboard_name in str((event or {}).get("change") or ""):
                return True
        return False

    candidates = [
        candidate
        for candidate in quarantine
        if isinstance(candidate, dict)
        and _normalized_topic(candidate.get("topic")) == topic
        and came_from_dashboard(candidate)
    ]
    if len(candidates) > 1:
        raise RuntimeError(
            "Có %d thẻ cách ly cùng topic từ %s; cần bác sĩ chọn thẻ khôi phục."
            % (len(candidates), dashboard_name)
        )
    if not candidates:
        return False

    old = candidates[0]
    old_id = old.get("id")
    generated_id = card.get("id")
    evidence_cards = data.get("evidence_cards") or []
    id_conflict = any(existing.get("id") == old_id for existing in evidence_cards)
    assigned_id = generated_id if id_conflict else old_id
    if not assigned_id:
        raise RuntimeError("Thẻ khôi phục không có ID hợp lệ.")
    other_cards = evidence_cards + [candidate for candidate in quarantine if candidate is not old]
    if any(existing.get("id") == assigned_id for existing in other_cards):
        raise RuntimeError(
            "ID thay thế %s cũng đã tồn tại; dừng để tránh ghi đè thẻ khác." % assigned_id
        )

    recovered = dict(card)
    recovered["id"] = assigned_id
    recovered["date_added"] = old.get("date_added", card.get("date_added", ""))
    recovered["specialty"] = old.get("specialty") or card.get("specialty", "")
    recovered["cycle"] = old.get("cycle", card.get("cycle"))
    recovered["provenance"] = old.get("provenance") or card.get("provenance")
    recovered["decision"] = "notyet"
    recovered["verification_status"] = "cần bác sĩ xác minh nguồn sau khôi phục tự động"
    recovered["quarantine_recovery"] = {
        "status": "RESTORED_TO_REVIEW_QUEUE",
        "dashboard": dashboard_name,
        "restored_at": today,
        "original_id": old_id,
        "assigned_id": assigned_id,
        "id_conflict": id_conflict,
    }
    id_note = (
        "ID cũ %s đã thuộc thẻ khác nên cấp ID mới %s và giữ original_id trong provenance"
        % (old_id, assigned_id)
        if id_conflict
        else "giữ ID %s" % old_id
    )
    recovered["history"] = list(old.get("history") or []) + [
        {
            "date": today,
            "change": (
                "khôi phục từ quarantined_cards vì dashboard gốc đã có "
                "PMID/DOI/URL/references; %s, buộc notyet và chờ bác sĩ xác minh nguồn."
                % id_note
            ),
        }
    ]
    recovered.pop("quarantine_reason", None)
    recovered.pop("quarantine_date", None)

    data["quarantined_cards"] = [candidate for candidate in quarantine if candidate is not old]
    data.setdefault("evidence_cards", []).append(recovered)
    return "reassigned" if id_conflict else "preserved"


# ---------------------------------------------------------------------------------------------
# PHIÊN BẢN NỐI TIẾP (thêm 18/10/2026)
# ---------------------------------------------------------------------------------------------
# VÌ SAO: chống trùng ở main() (key_of + độ giống chủ đề ≥ SIMILARITY_THRESHOLD) đúng cho một
# dashboard MỚI, nhưng SAI cho phiên bản nối tiếp của CÙNG lát cắt (vd ..._HopNhat_20260614 →
# ..._HopNhat_20261018; quy ước tên ở tools/dang_ky_chu_de.py::tach_ten):
#   • mục GIỮ tiêu đề bị coi là trùng ⇒ BỎ QUA thẻ mới, sổ cái giữ nội dung/decision CŨ;
#   • mục ĐỔI tiêu đề hoặc đổi nguồn thành thẻ thứ hai SONG SONG với thẻ cũ.
# Đo 18/10/2026 trên BẢN SAO sổ cái (sau khi mạch máu não đã được cập nhật tay): một lượt
# sync_all.py kế tiếp nạp CẢ hai bản còn hồi sinh 2 thẻ nội dung CŨ từ bản 20260614 (ITEM-02 đổi
# nguồn, ITEM-03 đổi tiêu đề). Cách vá:
#   (1) --thay-ban/--noi-tiep: cập nhật TẠI CHỖ thẻ của bản cũ (giữ id, date_added, specialty,
#       provenance; nối history), mục mới thì nạp như thường, mục biến mất thì BÁO;
#   (2) nạp thường TỰ BỎ QUA bản cũ khi đã có bản mới hơn cùng lát cắt (trong sổ cái hoặc trong
#       cùng lô), và KHÔNG nạp bản mới khi bản trước đã có thẻ mà chưa chạy nối tiếp.
# Máy KHÔNG tự đổi decision/gradeLevel ngoài nội dung của chính dashboard đã qua cổng; mọi thay
# đổi decision/gradeLevel được in nổi trong bản chạy khô để bác sĩ thấy trước khi --ap-dung.
#
# TRỘN BA CHIỀU (gốc = item bản cũ, sổ = thẻ hub, mới = item bản mới), từng trường một:
#   • mới == sổ                ⇒ không đụng;
#   • sổ == gốc                ⇒ sổ còn y nguyên bản cũ ⇒ lấy theo bản mới;
#   • sổ ≠ gốc (thẻ đã bị sửa NGOÀI dashboard — integrity_guard hạ decision, khôi phục cách ly ép
#     notyet, manage_ledger, «THAY NGUỒN (bác sĩ duyệt)», recommendation điền bằng bản tổng hợp…
#     — hoặc dashboard cũ bị sửa tại chỗ sau khi nạp):
#       – trường NGHIÊM (decision, gradeLevel, PMID/DOI/URL): GIỮ sổ, báo xung đột cho bác sĩ;
#       – trường mô tả: sổ TRỐNG ⇒ bù theo bản mới; sổ là tiền tố của bản mới (chuỗi bị bộ tách
#         trước 21/07/2026 cắt cụt tại dấu nháy, vd «Quy trình») ⇒ bù phần cắt cụt;
#       – còn lại: dashboard KHÔNG đổi trường đó giữa hai bản ⇒ giữ sổ, im lặng; dashboard CÓ đổi ⇒
#         giữ sổ và báo xung đột cho bác sĩ.
# Đo 18/10/2026: so thẳng sổ ↔ bản mới (không có gốc) sẽ đưa lại 'apply' cho thẻ integrity_guard
# đã hạ và ghi đè recommendation đã được điền — chính là «tự đổi decision ngoài dashboard».

# Trường NỘI DUNG được cập nhật tại chỗ (đường dẫn phẳng "cha.con" cho trường lồng). Cố ý KHÔNG
# có: id, date_added, specialty, provenance, cycle, verification_status, quarantine*, replacement
# (luồng Retraction-and-Replacement riêng) và mọi khoá do công cụ khác gắn thêm vào thẻ — kể cả
# khoá con lạ trong source/practice (vd source.type) được giữ nguyên.
NOI_TIEP_TRUONG = (
    "topic", "pico_question", "recommendation", "certainty", "gradeLevel", "decision",
    "date_source", "vietnam_context", "frame", "frameLabels",
    "source.agency", "source.title", "source.url", "source.pmid", "source.doi",
    "pico.population", "pico.intervention", "pico.comparison", "pico.outcome",
    "practice.action", "practice.monitoring", "practice.safety",
    "critical_appraisal.design", "critical_appraisal.effect_estimate",
)
# Trường mà xung đột KHÔNG BAO GIỜ tự giải (quyết định lâm sàng + định danh nguồn).
NOI_TIEP_TRUONG_NGHIEM = frozenset(
    ("decision", "gradeLevel", "source.pmid", "source.doi", "source.url"))

_DANG_KY_CHU_DE = {"ham": None, "loi": None}


def _tach_ten_ban(ten):
    """(lát_cắt, ngày YYYYMMDD) theo quy ước tên dashboard, hoặc None.

    NGUỒN DUY NHẤT của quy ước là tools/dang_ky_chu_de.py::tach_ten ở repo gốc (cùng độ sâu
    từ EBM_MASTER/tools/ lẫn sync/ebm-master-tools/) — KHÔNG chép regex sang đây: hai bản sẽ
    lệch nhau và «lát cắt» bị hiểu khác nhau giữa đăng ký chủ đề và sổ cái. Không nạp được
    công cụ đó ⇒ trả None (không nhận diện được phiên bản) và ghi lý do vào _DANG_KY_CHU_DE."""
    if _DANG_KY_CHU_DE["ham"] is None and _DANG_KY_CHU_DE["loi"] is None:
        duong = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "tools", "dang_ky_chu_de.py")
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("_dang_ky_chu_de_cho_ingest", duong)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            _DANG_KY_CHU_DE["ham"] = mod.tach_ten
        except Exception as exc:  # noqa: BLE001 — thiếu công cụ ⇒ «không nhận diện được», không crash
            _DANG_KY_CHU_DE["loi"] = "%s (%s: %s)" % (duong, type(exc).__name__, exc)
    if _DANG_KY_CHU_DE["ham"] is None:
        return None
    r = _DANG_KY_CHU_DE["ham"](os.path.basename(str(ten)))
    return (r[0], r[2]) if r else None


_RE_NGUON_BAN = re.compile(r"(?:nạp từ dashboard|phiên bản nối tiếp)\s+(\S+?\.html)")


def card_dashboard_names(card):
    """Tên các dashboard mà thẻ MANG NỘI DUNG của nó — đọc từ history: «nạp từ dashboard X»
    (tạo thẻ) và «… phiên bản nối tiếp X …» (cập nhật tại chỗ). «đối chiếu trùng với X» (bù
    trường) KHÔNG tính: thẻ đó chỉ được bù PMID/DOI, nội dung vẫn của dashboard khác."""
    names = set()
    for event in card.get("history") or []:
        if isinstance(event, dict):
            text = unicodedata.normalize("NFC", str(event.get("change") or ""))
            names.update(m.group(1) for m in _RE_NGUON_BAN.finditer(text))
    return names


def hub_dashboard_names(data):
    """Mọi dashboard đã có thẻ trong sổ cái (kể cả thẻ cách ly)."""
    names = set()
    for card in (data.get("evidence_cards") or []) + (data.get("quarantined_cards") or []):
        if isinstance(card, dict):
            names |= card_dashboard_names(card)
    return names


def phan_loai_phien_ban(ten, ten_trong_so, ten_trong_lo=()):
    """Nạp thường có nên nạp dashboard `ten` không, xét phiên bản nối tiếp cùng lát cắt.

    Trả một trong:
      ("nap", None)                      — nạp như trước;
      ("bo_qua_ban_cu", <tên bản mới>)   — đã có bản MỚI HƠN cùng lát cắt trong sổ cái hoặc
                                           trong cùng lô: nạp lại bản cũ sẽ hồi sinh nội dung
                                           đã bị thay (hoặc tạo thẻ song song);
      ("can_noi_tiep", <tên bản trước>)  — bản trước cùng lát cắt đã có thẻ mà bản này chưa:
                                           nạp thường sẽ giữ nội dung cũ/sinh thẻ song song —
                                           phải chạy --thay-ban.
    Tên không theo quy ước hoặc thiếu tools/dang_ky_chu_de.py ⇒ ("nap", None) như trước."""
    ten = os.path.basename(str(ten))
    r = _tach_ten_ban(ten)
    if r is None:
        return ("nap", None)
    lat_cat, ngay = r
    cung_lat = []
    for other in set(ten_trong_so) | {os.path.basename(str(x)) for x in ten_trong_lo}:
        if other == ten:
            continue
        rr = _tach_ten_ban(other)
        if rr and rr[0] == lat_cat:
            cung_lat.append((rr[1], other, other in ten_trong_so))
    moi_hon = sorted(x for x in cung_lat if x[0] > ngay)
    if moi_hon:
        return ("bo_qua_ban_cu", moi_hon[-1][1])
    if ten in ten_trong_so:
        return ("nap", None)
    truoc = sorted(x for x in cung_lat if x[0] < ngay and x[2])
    if truoc:
        return ("can_noi_tiep", truoc[-1][1])
    return ("nap", None)


def kiem_cap_noi_tiep(duong_cu, duong_moi):
    """Chuỗi lỗi (rỗng = hợp lệ) cho cặp bản cũ → bản mới của chế độ nối tiếp. Fail-closed:
    không xác nhận được CÙNG lát cắt + ngày MỚI HƠN thì không cập nhật tại chỗ gì cả — các lát
    cắt khác nhau BỔ SUNG cho nhau, ghi đè chéo là làm mất nội dung của lát cắt kia."""
    ten_cu, ten_moi = os.path.basename(str(duong_cu)), os.path.basename(str(duong_moi))
    if os.path.abspath(str(duong_cu)) == os.path.abspath(str(duong_moi)) or ten_cu == ten_moi:
        return "bản cũ và bản mới là CÙNG một tệp (%s)." % ten_moi
    a, b = _tach_ten_ban(ten_cu), _tach_ten_ban(ten_moi)
    if a is None or b is None:
        if _DANG_KY_CHU_DE["loi"]:
            return ("không nhận diện được lát cắt/ngày vì không nạp được %s — không thể xác "
                    "nhận đây là phiên bản nối tiếp." % _DANG_KY_CHU_DE["loi"])
        return ("tên tệp không theo quy ước WebDashboard_EBM_<nhóm>_<lát cắt>_<YYYYMMDD>.html "
                "(%s)." % (ten_cu if a is None else ten_moi))
    if a[0] != b[0]:
        return ("hai bản KHÁC lát cắt (%s ≠ %s) — các lát cắt khác nhau bổ sung cho nhau, "
                "không thay nhau (tools/dang_ky_chu_de.py::tach_ten)." % (a[0], b[0]))
    if b[1] <= a[1]:
        return "bản mới (%s) không có ngày MỚI HƠN bản cũ (%s)." % (b[1], a[1])
    return ""


def dong_ban_den(ten_cu, ten_trong_so):
    """Mọi bản cùng lát cắt có ngày ≤ bản cũ (kể cả chính nó) đang có thẻ trong sổ cái.

    Thẻ mang nguồn từ BẤT KỲ bản nào trong dòng này đều đang đại diện cho mục của bản cũ: chế
    độ nối tiếp chỉ ghi history cho thẻ ĐỔI nội dung, nên thẻ không đổi ở lượt v1→v2 vẫn chỉ
    mang «nạp từ dashboard v1» khi tới lượt v2→v3."""
    ten_cu = os.path.basename(str(ten_cu))
    r = _tach_ten_ban(ten_cu)
    if r is None:
        return {ten_cu}
    lat_cat, ngay = r
    dong = {ten_cu}
    for other in ten_trong_so:
        rr = _tach_ten_ban(other)
        if rr and rr[0] == lat_cat and rr[1] <= ngay:
            dong.add(other)
    return dong


def tim_file_ban_truoc(duong_moi, ten_trong_so, hub):
    """(đường dẫn bản trước, lý do lỗi) cho --noi-tiep: bản cùng lát cắt mới nhất có ngày nhỏ
    hơn bản mới VÀ đã có thẻ trong sổ cái; tìm tệp cạnh bản mới, rồi EBM-Dashboards/, rồi
    WEB_DASHBOARDS/ của hub."""
    ten_moi = os.path.basename(str(duong_moi))
    r = _tach_ten_ban(ten_moi)
    if r is None:
        if _DANG_KY_CHU_DE["loi"]:
            return None, "không nạp được %s nên không tìm được bản trước." % _DANG_KY_CHU_DE["loi"]
        return None, ("tên tệp không theo quy ước WebDashboard_EBM_<nhóm>_<lát cắt>_<YYYYMMDD>.html "
                      "(%s) — truyền bản cũ bằng --thay-ban." % ten_moi)
    lat_cat, ngay = r
    truoc = sorted(
        (rr[1], other) for other in ten_trong_so
        for rr in [_tach_ten_ban(other)] if rr and rr[0] == lat_cat and rr[1] < ngay
    )
    if not truoc:
        return None, ("sổ cái chưa có thẻ nào từ bản trước của lát cắt %s — không có gì để nối "
                      "tiếp; nạp thường là đủ." % lat_cat)
    ten_truoc = truoc[-1][1]
    noi_tim = [
        os.path.dirname(os.path.abspath(str(duong_moi))),
        os.path.join(os.path.dirname(os.path.abspath(hub)), "EBM-Dashboards"),
        os.path.join(os.path.abspath(hub), "WEB_DASHBOARDS"),
    ]
    for thu_muc in noi_tim:
        ung_vien = os.path.join(thu_muc, ten_truoc)
        if os.path.isfile(ung_vien):
            return ung_vien, ""
    return None, ("thẻ trong sổ cái đến từ %s nhưng không tìm thấy tệp này ở: %s — truyền "
                  "đường dẫn bằng --thay-ban." % (ten_truoc, "; ".join(noi_tim)))


def _khoa_muc(it):
    """Khoá ghép một item giữa hai phiên bản: mã item (ITEM-xx), không có mã thì tiêu đề."""
    local_id = str(it.get("local_id") or "").strip()
    if local_id:
        return ("id", local_id)
    return ("tieu_de", _normalized_topic(it.get("title")))


def _nhan_muc(it):
    return "%s «%s»" % (str(it.get("local_id") or "").strip() or "—", str(it.get("title") or "")[:70])


def ghep_muc_hai_ban(items_cu, items_moi):
    """(cặp [(cũ, mới)], chỉ-mới [..], chỉ-cũ [..]) — ghép theo mã item, thiếu mã thì theo tiêu
    đề. Hai item cùng khoá trong MỘT bản ⇒ dừng fail-closed: máy không đoán item nào là item nào."""
    def chi_muc(items, nhan):
        out = {}
        for it in items:
            khoa = _khoa_muc(it)
            if khoa in out:
                raise RuntimeError(
                    "Bản %s có hai mục cùng khoá %s — không ghép được hai phiên bản, cần bác sĩ "
                    "xem dashboard." % (nhan, khoa[1]))
            out[khoa] = it
        return out

    cu, moi = chi_muc(items_cu, "cũ"), chi_muc(items_moi, "mới")
    cap = [(cu[k], moi[k]) for k in moi if k in cu]
    chi_moi = [moi[k] for k in moi if k not in cu]
    chi_cu = [cu[k] for k in cu if k not in moi]
    return cap, chi_moi, chi_cu


def _gia_tri_so_sanh(value):
    """Chuẩn hoá để so nội dung: None/""/{}/[] coi như nhau (thẻ cũ thường THIẾU khoá mà bản mới
    có khoá rỗng — không phải thay đổi nội dung)."""
    if value is None or value == "" or value == {} or value == []:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def _lay_truong(card, duong):
    """Giá trị theo đường dẫn phẳng ("practice.safety"); cha không phải dict ⇒ None."""
    if "." in duong:
        cha, con = duong.split(".", 1)
        khoi = card.get(cha)
        return khoi.get(con) if isinstance(khoi, dict) else None
    return card.get(duong)


def _dat_truong(card, duong, value):
    """Ghi theo đường dẫn phẳng, GIỮ các khoá con khác của cha (vd source.type)."""
    value = copy.deepcopy(value)
    if "." in duong:
        cha, con = duong.split(".", 1)
        if not isinstance(card.get(cha), dict):
            card[cha] = {}
        card[cha][con] = value
    else:
        card[duong] = value


def tron_ba_chieu(the, goc, moi):
    """So thẻ sổ cái (`the`) với thẻ dựng từ item bản cũ (`goc`) và bản mới (`moi`).

    Trả (thay, xung_dot):
      thay      — [(đường dẫn, giá trị mới, lý do)] với lý do ∈ {"theo bản mới", "bù trường
                  trống", "bù phần bị cắt cụt"};
      xung_dot  — [(đường dẫn, giá trị sổ, giá trị gốc, giá trị mới)]: sổ đã bị sửa ngoài
                  dashboard ⇒ GIỮ sổ, bác sĩ quyết.
    Luật đầy đủ ở khối chú thích «TRỘN BA CHIỀU» phía trên. references xử lý riêng ở
    _tron_tham_chieu() vì nó đi theo nguồn."""
    thay, xung_dot = [], []
    for duong in NOI_TIEP_TRUONG:
        v_so, v_goc, v_moi = _lay_truong(the, duong), _lay_truong(goc, duong), _lay_truong(moi, duong)
        s_so, s_goc, s_moi = _gia_tri_so_sanh(v_so), _gia_tri_so_sanh(v_goc), _gia_tri_so_sanh(v_moi)
        if s_moi == s_so:
            continue
        if s_so == s_goc:
            thay.append((duong, v_moi, "theo bản mới"))
            continue
        if duong not in NOI_TIEP_TRUONG_NGHIEM:
            if s_so == "":
                thay.append((duong, v_moi, "bù trường trống"))
                continue
            if (isinstance(v_so, str) and isinstance(v_moi, str)
                    and len(v_moi) > len(v_so) and v_moi.startswith(v_so)):
                thay.append((duong, v_moi, "bù phần bị cắt cụt"))
                continue
        if s_goc == s_moi:
            # Dashboard KHÔNG đổi trường này giữa hai bản ⇒ không có gì để lan truyền; giữ nguyên sửa
            # đổi của sổ (vd integrity_guard hạ decision) mà không báo xung đột thừa.
            continue
        xung_dot.append((duong, v_so, v_goc, v_moi))
    return thay, xung_dot


def _tron_tham_chieu(the, goc, moi, nguon_bi_thay):
    """references mới cho thẻ, hoặc None nếu không đổi.

    Sổ còn y nguyên bản cũ ⇒ lấy đúng danh sách bản mới. Sổ đã có tham chiếu ngoài bản cũ (vd bù
    trường từ dashboard khác) ⇒ chỉ THÊM tham chiếu mới, và bỏ đúng «PMID:/DOI:» của nguồn vừa bị
    thay ở lượt này (`nguon_bi_thay`) — không xoá tham chiếu nào khác."""
    r_so = list(the.get("references") or [])
    r_goc = list(goc.get("references") or [])
    r_moi = list(moi.get("references") or [])
    if r_so == r_goc:
        ket_qua = r_moi
    else:
        ket_qua = [r for r in r_so if r not in nguon_bi_thay] + [r for r in r_moi if r not in r_so]
    return None if ket_qua == r_so else ket_qua


def ap_dung_phien_ban_noi_tiep(data, items_cu, items_moi, *, ten_cu, ten_moi, question_cu,
                               updated_cu, question_moi, updated_moi, today):
    """Cập nhật TẠI CHỖ thẻ sổ cái của bản cũ theo bản mới. Sửa `data` trong bộ nhớ; ghi đĩa hay
    không là việc của main() (--ap-dung).

    Thẻ «của» một item bản cũ = thẻ evidence_cards có key_of trùng, chủ đề giống ≥
    SIMILARITY_THRESHOLD (đúng luật chống trùng của nạp thường) VÀ mang nội dung từ một bản
    trong dòng phiên bản (dong_ban_den) — không đụng thẻ của LÁT CẮT KHÁC dù trùng khoá + tiêu
    đề. Một cụm thẻ trùng (sinh bởi lỗi nạp lặp 12–13/07/2026) được cập nhật CẢ CỤM để các bản
    sao không lệch nhau, và được báo trong `cum_trung` để bác sĩ dọn. Một thẻ bị hai item khác
    nhau cùng nhận ⇒ dừng fail-closed (RuntimeError) TRƯỚC khi sửa bất cứ thẻ nào.

    Trả báo cáo dict; `xu_ly` là tập khoá item bản mới ĐÃ xử lý (main() bỏ qua chúng ở vòng nạp
    thường). Item bản mới có replacesPmid đi luồng Retraction-and-Replacement (nạp thường)."""
    ten_cu, ten_moi = os.path.basename(str(ten_cu)), os.path.basename(str(ten_moi))
    dong = dong_ban_den(ten_cu, hub_dashboard_names(data))
    the_so = data.setdefault("evidence_cards", [])

    def dung(it, question, updated, ten):
        return build_card(it, question=question, updated=updated, dashboard_name=ten,
                          today=today, card_id="")

    def tim_the(card_cu):
        khoa = key_of(card_cu)
        return [
            c for c in the_so
            if key_of(c) == khoa
            and _topic_similarity(card_cu.get("topic", ""), c.get("topic", "")) >= SIMILARITY_THRESHOLD
            and card_dashboard_names(c) & dong
        ]

    cap, chi_moi, chi_cu = ghep_muc_hai_ban(items_cu, items_moi)
    bao = {
        "ten_cu": ten_cu, "ten_moi": ten_moi, "dong_phien_ban": sorted(dong),
        "cap_nhat": [], "xung_dot": [], "khong_doi": [], "khong_khop_so": [], "muc_moi": [],
        "bien_mat": [], "cum_trung": [], "chuyen_rr": [], "trung_sau_cap_nhat": [],
        "xu_ly": set(),
    }

    # Lượt 1 — ghép và KIỂM, chưa sửa gì (fail-closed phải dừng trước khi đụng thẻ nào).
    ke_hoach = []
    chu_the = {}
    for cu, moi in cap:
        if str(moi.get("replacesPmid") or "").strip():
            bao["chuyen_rr"].append(_nhan_muc(moi))
            continue
        card_goc = dung(cu, question_cu, updated_cu, ten_cu)
        the = tim_the(card_goc)
        if not the:
            bao["khong_khop_so"].append(_nhan_muc(moi))
            continue
        for c in the:
            truoc = chu_the.get(id(c))
            if truoc is not None and truoc != _khoa_muc(moi):
                raise RuntimeError(
                    "Thẻ %s khớp cả hai mục %s và %s của bản cũ — không biết cập nhật theo mục "
                    "nào; cần bác sĩ xem." % (c.get("id"), truoc[1], _khoa_muc(moi)[1]))
            chu_the[id(c)] = _khoa_muc(moi)
        ke_hoach.append((card_goc, moi, the))
    for cu in chi_cu:
        the = tim_the(dung(cu, question_cu, updated_cu, ten_cu))
        bao["bien_mat"].append({"muc": _nhan_muc(cu), "ids": [c.get("id") for c in the]})
    bao["muc_moi"] = [_nhan_muc(m) for m in chi_moi]

    # Lượt 2 — áp (trộn ba chiều). Chỉ đụng thẻ có trường cần đổi; thẻ không đổi giữ nguyên,
    # không thêm history.
    da_doi_khoa = []
    for card_goc, moi, the in ke_hoach:
        card_moi = dung(moi, question_moi, updated_moi, ten_moi)
        nhan = _nhan_muc(moi)
        bao["xu_ly"].add(_khoa_muc(moi))
        if len(the) > 1:
            bao["cum_trung"].append({"muc": nhan, "ids": [c.get("id") for c in the]})
        co_doi = False
        for c in the:
            thay, xung_dot = tron_ba_chieu(c, card_goc, card_moi)
            for duong, v_so, v_goc, v_moi in xung_dot:
                bao["xung_dot"].append({"muc": nhan, "id": c.get("id"), "truong": duong,
                                        "so_cai": v_so, "ban_cu": v_goc, "ban_moi": v_moi})
            nguon_cu = dict(c.get("source") or {})
            khoa_truoc, tieu_de_truoc = key_of(c), _normalized_topic(c.get("topic"))
            dec_cu, grade_cu = c.get("decision"), c.get("gradeLevel")
            for duong, value, _ly_do in thay:
                _dat_truong(c, duong, value)
            nguon_bi_thay = set()
            if any(d == "source.pmid" for d, _v, _l in thay) and nguon_cu.get("pmid"):
                nguon_bi_thay.add("PMID:" + str(nguon_cu["pmid"]))
            if any(d == "source.doi" for d, _v, _l in thay) and nguon_cu.get("doi"):
                nguon_bi_thay.add("DOI:" + str(nguon_cu["doi"]))
            # PMID/DOI đang bị GIỮ do xung đột ⇒ không động tới references: lấy danh sách bản mới lúc
            # này sẽ đưa lại qua cửa sau đúng nguồn mà sổ (bác sĩ) đã bỏ.
            nguon_xung_dot = any(x[0] in ("source.pmid", "source.doi") for x in xung_dot)
            refs = None if nguon_xung_dot else _tron_tham_chieu(c, card_goc, card_moi, nguon_bi_thay)
            if refs is not None:
                c["references"] = refs
                thay.append(("references", refs, "theo nguồn bản mới"))
            if not thay:
                continue
            co_doi = True
            truong = [d if ly_do in ("theo bản mới", "theo nguồn bản mới") else "%s [%s]" % (d, ly_do)
                      for d, _v, ly_do in thay]
            ten_truong = [d for d, _v, _l in thay]
            phan = ["cập nhật tại chỗ theo phiên bản nối tiếp %s (%s; thay bản %s): %s"
                    % (ten_moi, str(moi.get("local_id") or "").strip() or "theo tiêu đề",
                       ten_cu, ", ".join(truong))]
            nguon_moi = c.get("source") or {}
            if ("source.pmid" in ten_truong) or ("source.doi" in ten_truong):
                phan.append("nguồn PMID %s/DOI %s → PMID %s/DOI %s" % (
                    nguon_cu.get("pmid") or "—", nguon_cu.get("doi") or "—",
                    nguon_moi.get("pmid") or "—", nguon_moi.get("doi") or "—"))
            if "decision" in ten_truong:
                phan.append("decision %s → %s theo dashboard đã qua cổng" % (dec_cu, c.get("decision")))
            if "gradeLevel" in ten_truong:
                phan.append("gradeLevel %s → %s theo dashboard đã qua cổng" % (grade_cu, c.get("gradeLevel")))
            c.setdefault("history", []).append({"date": today or "", "change": "; ".join(phan)})
            bao["cap_nhat"].append({
                "muc": nhan, "id": c.get("id"), "truong": truong,
                "decision": [dec_cu, c.get("decision")] if "decision" in ten_truong else None,
                "gradeLevel": [grade_cu, c.get("gradeLevel")] if "gradeLevel" in ten_truong else None,
            })
            if (key_of(c), _normalized_topic(c.get("topic"))) != (khoa_truoc, tieu_de_truoc):
                da_doi_khoa.append((c, the))
        if not co_doi:
            bao["khong_doi"].append({"muc": nhan, "ids": [c.get("id") for c in the]})

    # Sau cập nhật: thẻ vừa ĐỔI khoá/tiêu đề có trùng khoá + tiêu đề với thẻ NGOÀI cụm của nó không
    # (vd bản mới đổi tiêu đề trùng đúng một thẻ của lát cắt khác)? Chỉ BÁO, không gộp.
    for c, cum in da_doi_khoa:
        trong_cum = {id(x) for x in cum}
        khoa, tieu_de = key_of(c), _normalized_topic(c.get("topic"))
        trung = [x.get("id") for x in the_so
                 if id(x) not in trong_cum and key_of(x) == khoa
                 and _normalized_topic(x.get("topic")) == tieu_de]
        if trung:
            bao["trung_sau_cap_nhat"].append({"id": c.get("id"), "trung_voi": trung})
    return bao


def in_bao_noi_tiep(bao, *, ghi_that):
    """In kế hoạch/kết quả nối tiếp cho bác sĩ đọc (cùng nội dung ở chạy khô lẫn --ap-dung)."""
    print("PHIÊN BẢN NỐI TIẾP: %s → %s" % (bao["ten_cu"], bao["ten_moi"]))
    if len(bao["dong_phien_ban"]) > 1:
        print("  Dòng phiên bản đã có thẻ: %s" % ", ".join(bao["dong_phien_ban"]))
    for u in bao["cap_nhat"]:
        print("  ✎ %s %s: %s" % (u["id"], u["muc"], ", ".join(u["truong"])))
        if u["decision"]:
            print("      ⚠ decision %s → %s (theo dashboard đã qua cổng — bác sĩ xem)" % tuple(u["decision"]))
        if u["gradeLevel"]:
            print("      ⚠ gradeLevel %s → %s (theo dashboard đã qua cổng — bác sĩ xem)" % tuple(u["gradeLevel"]))
    for x in bao["xung_dot"]:
        def _ngan(v):
            return (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v or "∅"))[:60]
        print("  ⛔ GIỮ NGUYÊN %s %s.%s — sổ cái đã bị sửa ngoài dashboard (sổ «%s» · bản cũ «%s» · "
              "bản mới «%s»): bác sĩ quyết." % (x["id"], x["muc"].split(" ")[0], x["truong"],
                                               _ngan(x["so_cai"]), _ngan(x["ban_cu"]), _ngan(x["ban_moi"])))
    if bao["khong_doi"]:
        print("  = %d mục không đổi nội dung (không đụng thẻ)." % len(bao["khong_doi"]))
    for m in bao["muc_moi"]:
        print("  + mục mới %s — nạp như thẻ mới (vẫn qua chống trùng thường)." % m)
    for m in bao["khong_khop_so"]:
        print("  + %s — có ở cả hai bản nhưng sổ cái không có thẻ của bản cũ ⇒ nạp thường." % m)
    for m in bao["chuyen_rr"]:
        print("  ↺ %s — khai replacesPmid ⇒ đi luồng Retraction-and-Replacement." % m)
    for b in bao["bien_mat"]:
        print("  ? %s có ở bản cũ, KHÔNG còn ở bản mới — GIỮ NGUYÊN thẻ %s (không tự xoá; "
              "bác sĩ quyết, vd manage_ledger.py drop)." % (b["muc"], ", ".join(b["ids"]) or "(không có thẻ)"))
    for c in bao["cum_trung"]:
        print("  ⚠ %s ứng với CỤM %d thẻ trùng %s — cập nhật cả cụm cho khỏi lệch; dọn cụm theo "
              "báo cáo tools/liet_ke_the_trung_hub.py." % (c["muc"], len(c["ids"]), ", ".join(c["ids"])))
    for t in bao["trung_sau_cap_nhat"]:
        print("  ⚠ %s sau cập nhật trùng khoá + tiêu đề với %s (ngoài dòng phiên bản) — bác sĩ xem."
              % (t["id"], ", ".join(t["trung_voi"])))
    if not ghi_that:
        print("  (CHẠY KHÔ — chưa ghi gì vào sổ cái. Bác sĩ xem kế hoạch trên rồi chạy lại kèm --ap-dung.)")


_STANDALONE_LEDGER_LOCK_CM = None  # tham chiếu MODULE-LEVEL — xem chú thích bên dưới


def _acquire_standalone_ledger_lock():
    """THÊM 2026-07-21 (vòng lặp kiểm tra-hoàn thiện vòng 4, phát hiện LOW):
    nếu script này chạy TRỰC TIẾP (không qua sync_all.py), tự khóa ghi sổ cái
    để tránh đua-ghi với một tiến trình sync_all.py khác (vd launchd cron)
    đang chạy cùng lúc. sync_all.py TỰ đặt biến môi trường
    EBM_MASTER_LEDGER_LOCK_HELD khi ĐÃ giữ khóa ở tiến trình cha trước khi
    subprocess.run() script con này — bỏ qua ở đây để tránh deadlock (con đợi
    khóa cha đang giữ, trong khi cha đang đợi con chạy xong qua
    subprocess.run(), không ai nhường ai). Best-effort: lỗi (Windows thiếu
    fcntl, sync_all.py không import được...) → bỏ qua im lặng, không chặn.

    SỬA 2026-07-21 (vòng lặp kiểm tra-hoàn thiện vòng 5, phát hiện CRITICAL):
    bản trước gọi ledger_lock().__enter__() mà KHÔNG giữ tham chiếu nào tới
    context manager tạm thời đó — refcount về 0 ngay sau câu lệnh, CPython
    hủy đối tượng NGAY LẬP TỨC, generator bên trong bị đóng bằng
    GeneratorExit, khối finally (mở khóa) chạy NGAY — TRƯỚC BẤT KỲ dòng nào
    khác của main() — nên khóa hoàn toàn vô tác dụng (đã tái hiện thực
    nghiệm: mở lại file .ledger.lock ngay sau lệnh trên vẫn lấy được khóa).
    Nay giữ context manager trong biến module-level (khỏi bị garbage-collect
    sớm) và dùng atexit để mở khóa đúng lúc tiến trình kết thúc."""
    if os.environ.get("EBM_MASTER_LEDGER_LOCK_HELD") == "1":
        return
    global _STANDALONE_LEDGER_LOCK_CM
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from sync_all import ledger_lock
        cm = ledger_lock()
        cm.__enter__()
        _STANDALONE_LEDGER_LOCK_CM = cm  # giữ sống tới khi atexit chạy __exit__
        import atexit
        atexit.register(cm.__exit__, None, None, None)
    except Exception:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--today", default="")
    ap.add_argument("--thay-ban", default="", metavar="DASHBOARD_CU",
                    help="nạp PHIÊN BẢN NỐI TIẾP: cập nhật tại chỗ thẻ của bản cũ này theo bản mới "
                         "(đúng MỘT tệp mới; cùng lát cắt, ngày mới hơn)")
    ap.add_argument("--noi-tiep", action="store_true",
                    help="như --thay-ban nhưng tự tìm bản trước cùng lát cắt đã có thẻ trong sổ cái")
    ap.add_argument("--ap-dung", action="store_true",
                    help="chế độ nối tiếp: GHI THẬT (mặc định chạy khô) — chỉ sau khi bác sĩ xem kế hoạch")
    ap.add_argument("--hub", default="",
                    help="thư mục hub chứa EBM_MASTER.json (mặc định: thư mục cha của tools/; dùng cho kiểm thử)")
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    hub = os.path.abspath(args.hub) if args.hub else os.path.dirname(here)
    if not args.hub:
        # Khoá chỉ bảo vệ sổ cái THẬT; hub khác (kiểm thử) không được giành khoá của sổ thật.
        _acquire_standalone_ledger_lock()
    master_path = os.path.join(hub, "EBM_MASTER.json")
    # Vá 2026-07-11 (vòng 8): JSON hỏng/ghi dở (OneDrive sync giữa chừng) trước đây làm crash
    # với traceback thô. Sổ cái là dữ liệu quan trọng nhất trong hub — báo lỗi tiếng Việt rõ
    # ràng + gợi ý phục hồi từ BACKUPS/ thay vì để traceback khó đọc.
    try:
        data = json.load(open(master_path, encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print("✗ EBM_MASTER.json hỏng/ghi dở (%s): %s" % (master_path, exc))
        print("  Phục hồi từ bản backup gần nhất trong EBM_MASTER/BACKUPS/ rồi chạy lại.")
        sys.exit(1)

    che_do_noi_tiep = bool(args.thay_ban or args.noi_tiep)
    # Nạp thường ghi như trước; chế độ nối tiếp mặc định CHẠY KHÔ (sửa tại chỗ thẻ đã có —
    # kể cả decision/gradeLevel theo dashboard — nên bác sĩ phải thấy kế hoạch trước).
    ghi_that = (not che_do_noi_tiep) or args.ap_dung
    ten_trong_so = hub_dashboard_names(data)
    noi_tiep_bao = None
    noi_tiep_xu_ly = set()
    if che_do_noi_tiep:
        if len(args.files) != 1:
            print("⛔ Chế độ nối tiếp nhận đúng MỘT dashboard mới (nhận %d)." % len(args.files))
            return 2
        duong_moi = args.files[0]
        if args.thay_ban:
            duong_cu = args.thay_ban
        else:
            duong_cu, ly_do = tim_file_ban_truoc(duong_moi, ten_trong_so, hub)
            if not duong_cu:
                print("⛔ --noi-tiep: %s" % ly_do)
                return 2
        loi_cap = kiem_cap_noi_tiep(duong_cu, duong_moi)
        if loi_cap:
            print("⛔ Không nạp phiên bản nối tiếp: %s" % loi_cap)
            return 2
        try:
            question_cu, updated_cu, items_cu = parse_dashboard(duong_cu)
            question_moi, updated_moi, items_moi = parse_dashboard(duong_moi)
        except (OSError, UnicodeError) as exc:
            print("⛔ Không đọc được dashboard của cặp nối tiếp: %s" % exc)
            return 2
        try:
            noi_tiep_bao = ap_dung_phien_ban_noi_tiep(
                data, items_cu, items_moi,
                ten_cu=duong_cu, ten_moi=duong_moi,
                question_cu=question_cu, updated_cu=updated_cu,
                question_moi=question_moi, updated_moi=updated_moi,
                today=args.today or "",
            )
        except RuntimeError as exc:
            print("⛔ Không thể nạp phiên bản nối tiếp: %s" % exc)
            return 1
        noi_tiep_xu_ly = noi_tiep_bao["xu_ly"]
        in_bao_noi_tiep(noi_tiep_bao, ghi_that=ghi_that)

    # Backup trước khi ghi (chạy khô không ghi gì nên không sao lưu).
    stamp = (args.today or "manual").replace("-", "")
    nhan_sao_luu = "pre-noi-tiep" if che_do_noi_tiep else "pre-ingest"
    if ghi_that:
        backups = os.path.join(hub, "BACKUPS")
        os.makedirs(backups, exist_ok=True)
        shutil.copy(master_path, os.path.join(backups, "EBM_MASTER_%s_%s.json" % (stamp, nhan_sao_luu)))

    # Chỉ mục chống trùng dựng SAU bước nối tiếp: thẻ cập nhật tại chỗ có thể đã đổi DOI/PMID/topic.
    existing = {
        key_of(c)
        for c in (data.get("evidence_cards", []) + data.get("quarantined_cards", []))
        if key_of(c)
    }
    # THÊM 2026-07-08: cần tra ngược key→card (chỉ evidence_cards, KHÔNG đụng
    # quarantined_cards — thẻ cách ly cần review truy nguyên riêng, không tự
    # "làm giàu") để khi gặp trùng, BÙ được trường pmid/doi rỗng của thẻ cũ
    # thay vì chỉ đếm dup rồi bỏ dữ liệu đầy đủ hơn (phát hiện qua kiểm định
    # đối kháng: 2 PMID "tưởng thiếu" thực ra đã có DOI trùng thẻ cũ pmid rỗng).
    cards_by_key = {}
    for c in data.get("evidence_cards", []):
        ck = key_of(c)
        if ck:
            cards_by_key.setdefault(ck, []).append(c)
    # Phải quét CẢ thẻ cách ly: ID của thẻ cách ly vẫn là định danh đã cấp và không được
    # tái sử dụng. Bỏ sót danh sách này từng làm EVID-2026-0274..0276 bị cấp lại cho ba
    # thẻ khác, chỉ lộ ra khi khôi phục cách ly.
    seq = max_ledger_seq(data)
    added = dup = enriched = same_source_new = pii_warned = 0
    replaced = replacement_duplicates_removed = rehydrated = rehydrated_reassigned = 0
    bo_qua_ban_cu = chua_noi_tiep = 0
    da_bao_thieu_dang_ky = False

    for f in args.files:
        if not che_do_noi_tiep:
            loai, ten_lien_quan = phan_loai_phien_ban(os.path.basename(f), ten_trong_so, args.files)
            if _DANG_KY_CHU_DE["loi"] and not da_bao_thieu_dang_ky:
                da_bao_thieu_dang_ky = True
                print("  ⚪ Không nhận diện được phiên bản nối tiếp (không nạp được %s) — nạp như "
                      "trước, KHÔNG chặn bản cũ/bản mới." % _DANG_KY_CHU_DE["loi"])
            if loai == "bo_qua_ban_cu":
                bo_qua_ban_cu += 1
                print("  ⏭ Bỏ qua %s — đã có phiên bản nối tiếp MỚI HƠN cùng lát cắt (%s); nạp lại "
                      "bản cũ sẽ hồi sinh nội dung đã bị thay." % (os.path.basename(f), ten_lien_quan))
                continue
            if loai == "can_noi_tiep":
                chua_noi_tiep += 1
                print("  ⛔ CHƯA nạp %s — đây là phiên bản nối tiếp của %s (đã có thẻ trong sổ cái); "
                      "nạp thường sẽ giữ nội dung cũ hoặc sinh thẻ song song. Chạy: python3 "
                      "tools/ingest_dashboard.py %s --noi-tiep --today <ngày> (chạy khô, bác sĩ xem) "
                      "rồi thêm --ap-dung." % (os.path.basename(f), ten_lien_quan, f))
                continue
        # SỬA 2026-07-22 (vòng lặp kiểm tra-hoàn thiện vòng 9, phát hiện MEDIUM): vòng lặp
        # này trước đây không có try/except — 1 file lỗi/biến mất giữa chừng (vd bị
        # reskin_dashboards.py di chuyển vào _reskin_backup/ đúng lúc, hoặc OneDrive sync
        # dở) làm crash TOÀN BỘ lô bằng traceback thô, kể cả các dashboard hợp lệ khác
        # trong cùng lệnh (sync_all.py truyền cả list). Nay bỏ qua file lỗi, tiếp tục các
        # file còn lại — nhất quán với cách xử lý JSON hỏng đã có sẵn cho EBM_MASTER.json
        # ở đầu main().
        try:
            question, updated, items = parse_dashboard(f)
        except (OSError, UnicodeError) as exc:
            print("  ⚠ Bỏ qua dashboard lỗi/không đọc được: %s (%s)" % (f, exc))
            continue
        for it in items:
            if noi_tiep_xu_ly and _khoa_muc(it) in noi_tiep_xu_ly:
                continue  # đã cập nhật tại chỗ (hoặc xác nhận không đổi) ở bước nối tiếp
            seq += 1
            card = build_card(
                it, question=question, updated=updated, dashboard_name=os.path.basename(f),
                today=args.today or "", card_id="EVID-%s-%04d" % ((args.today or "0000")[:4], seq),
            )
            source = card["source"]
            pii_hits = _card_pii_warnings(card)
            if pii_hits:
                pii_warned += 1
                print("⚠️  Nghi PII trong thẻ '%s' (từ %s): %s — RÀ TAY trước khi tin tưởng." %
                      (card.get("topic", "")[:60], os.path.basename(f),
                       ", ".join(sorted(set(pii_hits))[:5])))

            try:
                rehydration_mode = rehydrate_quarantined_card(
                    data,
                    card,
                    today=args.today or "",
                    dashboard_name=os.path.basename(f),
                )
            except RuntimeError as exc:
                print("⛔ Không thể tự khôi phục thẻ cách ly: %s" % exc)
                return 1
            if rehydration_mode:
                rehydrated += 1
                if rehydration_mode == "preserved":
                    # ID sinh tạm không được dùng; cho phép item kế tiếp dùng đúng số đó.
                    seq -= 1
                else:
                    # ID cũ đã xung đột nên thẻ khôi phục dùng chính ID sinh mới.
                    rehydrated_reassigned += 1
                existing = {
                    key_of(c)
                    for c in (data.get("evidence_cards", []) + data.get("quarantined_cards", []))
                    if key_of(c)
                }
                cards_by_key = {}
                for existing_card in data.get("evidence_cards", []):
                    existing_key = key_of(existing_card)
                    if existing_key:
                        cards_by_key.setdefault(existing_key, []).append(existing_card)
                continue

            try:
                did_replace, removed = apply_explicit_replacement(
                    data,
                    card,
                    it["replacesPmid"],
                    today=args.today or "",
                    dashboard_name=os.path.basename(f),
                )
            except RuntimeError as exc:
                print("⛔ Không thể tự thay nguồn: %s" % exc)
                return 1
            if did_replace:
                replaced += 1
                replacement_duplicates_removed += removed
                seq -= 1
                # Tái lập chỉ mục vì thẻ đích có thể đã đổi DOI/PMID và danh sách
                # evidence_cards có thể vừa bỏ bản trùng do ingest cũ tạo.
                existing = {key_of(c) for c in data.get("evidence_cards", []) if key_of(c)}
                cards_by_key = {}
                for existing_card in data.get("evidence_cards", []):
                    existing_key = key_of(existing_card)
                    if existing_key:
                        cards_by_key.setdefault(existing_key, []).append(existing_card)
                continue

            k = key_of(card)
            old_candidates = cards_by_key.get(k, []) if k in existing else []
            old = next(
                (
                    candidate for candidate in old_candidates
                    if _topic_similarity(card.get("topic", ""), candidate.get("topic", "")) >= SIMILARITY_THRESHOLD
                ),
                None,
            )
            # Vá 2026-07-11 (vòng 8): key trùng (DOI/PMID) KHÔNG đồng nghĩa trùng NỘI DUNG —
            # chỉ coi là trùng thật khi topic đủ giống (ngưỡng khớp integrity_guard.py).
            # Không so được (old=None, vd key chỉ khớp thẻ đã cách ly) → giữ hành vi cũ, thận
            # trọng coi là trùng nếu key chỉ có trong quarantined_cards để không tự động mở khoá
            # thẻ cách ly. Nếu key có evidence_cards nhưng không khớp topic nào, đó là khuyến cáo
            # khác trong cùng nguồn và được nạp như thẻ riêng.
            is_true_dup = old is not None or (k in existing and not old_candidates)
            if k in existing and is_true_dup:
                dup += 1
                seq -= 1
                # BÙ TRƯỜNG THIẾU: nếu thẻ cũ (khớp key) đang rỗng pmid/doi mà
                # thẻ mới có — bù lại, KHÔNG ghi đè trường nào khác đã có giá
                # trị (chỉ điền chỗ trống, giữ nguyên lịch sử/quyết định cũ).
                if old is not None:
                    old_src = old.setdefault("source", {})
                    filled = []
                    for field in ("pmid", "doi"):
                        new_val = source.get(field) or ""
                        if new_val and not old_src.get(field):
                            old_src[field] = new_val
                            filled.append(field)
                    if filled:
                        old.setdefault("references", [])
                        for field in filled:
                            ref = ("PMID:" if field == "pmid" else "DOI:") + old_src[field]
                            if ref not in old["references"]:
                                old["references"].append(ref)
                        old.setdefault("history", []).append({
                            "date": args.today or "",
                            "change": "bù trường %s còn thiếu (đối chiếu trùng với %s)" %
                                      (", ".join(filled), os.path.basename(f)),
                        })
                        enriched += 1
                continue
            if k in existing:
                # Cùng DOI/PMID nhưng nội dung khác biệt rõ (vd guideline dài trích nhiều
                # khuyến cáo) — nạp bình thường, KHÔNG bỏ qua; ghi rõ vào history để bác sĩ
                # biết nguồn được trích nhiều lần (integrity_guard.py sẽ xếp cụm này vào
                # "same_source_distinct", không cảnh báo trùng).
                same_source_new += 1
                card.setdefault("history", []).append({
                    "date": args.today or "",
                    "change": "cùng DOI/PMID với thẻ khác trong sổ cái nhưng nội dung khác biệt "
                              # %.2f: «%.1f» từng in 0,95 thành «0.9» — sai ngưỡng thật trong history.
                              "(topic similarity < %.2f) — nạp như thẻ mới, không gộp." % SIMILARITY_THRESHOLD,
                })
            existing.add(k)
            data.setdefault("evidence_cards", []).append(card)
            cards_by_key.setdefault(k, []).append(card)
            added += 1

    assert_unique(data["evidence_cards"])   # cổng bất biến: không bao giờ ghi sổ cái có id trùng
    tom_tat = ("+%d thẻ mới; %d thẻ cách ly đã khôi phục về notyet "
               "(%d thẻ phải cấp ID mới do xung đột lịch sử); "
               "%d thẻ Retraction and Replacement đã cập nhật tại chỗ "
               "(%d bản trùng cũ đã hợp nhất); %d cùng DOI/PMID nguồn khác nội dung — không gộp; "
               "%d trùng (bỏ qua, %d đã bù trường pmid/doi thiếu)" %
               (added, rehydrated, rehydrated_reassigned, replaced, replacement_duplicates_removed,
                same_source_new, dup, enriched))
    if noi_tiep_bao is not None:
        tom_tat += ("; nối tiếp: %d thẻ cập nhật tại chỗ, %d mục không đổi, %d mục biến mất (giữ thẻ)"
                    % (len(noi_tiep_bao["cap_nhat"]), len(noi_tiep_bao["khong_doi"]),
                       len(noi_tiep_bao["bien_mat"])))
    if bo_qua_ban_cu or chua_noi_tiep:
        tom_tat += ("; %d bản cũ bỏ qua (đã có phiên bản mới hơn); %d bản mới CHƯA nạp (cần --noi-tiep)"
                    % (bo_qua_ban_cu, chua_noi_tiep))
    if not ghi_that:
        print("CHẠY KHÔ — sẽ: %s. Tổng sổ cái sau nạp: %d thẻ. Chưa ghi gì." %
              (tom_tat, len(data["evidence_cards"])))
        return 0
    meta = data.setdefault("meta", {})
    meta["last_updated"] = args.today or meta.get("last_updated", "")
    meta["last_backup"] = "BACKUPS/EBM_MASTER_%s_%s.json" % (stamp, nhan_sao_luu)
    meta.setdefault("counts", {})["evidence_cards"] = len(data["evidence_cards"])
    meta["counts"]["quarantined_cards"] = len(data.get("quarantined_cards", []))
    json.dump(data, open(master_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Nạp xong: %s. Tổng sổ cái: %d thẻ." % (tom_tat, len(data["evidence_cards"])))
    if pii_warned:
        print("⚠️  %d thẻ có nghi PII (xem cảnh báo ⚠️ ở trên) — bác sĩ RÀ TAY trước khi tin tưởng." %
              pii_warned)

    try:
        from audit_log import append as _log_append
        _log_append(
            hub,
            event_type="DASHBOARD_INGEST",
            actor="ingest_dashboard.py (automated)",
            description=(
                "Nạp %d dashboard%s: %s. Tổng sổ cái sau nạp: %d thẻ."
                % (len(args.files),
                   (" (phiên bản nối tiếp %s → %s)" % (noi_tiep_bao["ten_cu"], noi_tiep_bao["ten_moi"]))
                   if noi_tiep_bao is not None else "",
                   tom_tat, len(data["evidence_cards"]))
            ),
            affected_files=["EBM_MASTER.json"],
            source_files_modified=[os.path.basename(f) for f in args.files],
            pii_present=False,
            notes="Backup trước ghi: BACKUPS/EBM_MASTER_%s_%s.json" % (stamp, nhan_sao_luu),
            session_id=args.today or "",
        )
    except Exception as exc:  # noqa: BLE001 — log lỗi không được chặn kết quả ingest
        print("  ⚠ Không ghi được AUDIT_LOG.jsonl (%s)." % exc)

    return 0


if __name__ == "__main__":
    sys.exit(main())
