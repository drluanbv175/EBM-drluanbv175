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
"""
import argparse
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
    _acquire_standalone_ledger_lock()
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--today", default="")
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    hub = os.path.dirname(here)
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

    # Backup trước khi ghi
    backups = os.path.join(hub, "BACKUPS")
    os.makedirs(backups, exist_ok=True)
    stamp = (args.today or "manual").replace("-", "")
    shutil.copy(master_path, os.path.join(backups, "EBM_MASTER_%s_pre-ingest.json" % stamp))

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

    for f in args.files:
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
            # Vá 2026-07-10: GIỮ url (trước đây hardcode "" → thẻ guideline/quy định chỉ có
            # URL, không PMID/DOI, bị mất dấu truy nguyên → cách ly nhầm).
            source = {"agency": it["org"], "title": question, "url": it.get("url", ""),
                      "pmid": it["pmid"], "doi": it["doi"], "type": "guideline/RCT"}
            seq += 1
            card = {
                "id": "EVID-%s-%04d" % ((args.today or "0000")[:4], seq),
                "cycle": "from_dashboard",
                "date_added": args.today or "",
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
                "history": [{"date": args.today or "", "change": "nạp từ dashboard %s" % os.path.basename(f)}],
            }
            if it["replacesPmid"]:
                card["replacement"] = {
                    "supersedes_pmid": it["replacesPmid"],
                    "notice_pmid": it["replacementNoticePmid"],
                    "notice_doi": it["replacementNoticeDoi"],
                    "status": "REPLACEMENT_REQUIRES_DOCTOR_REVIEW",
                }
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
                              "(topic similarity < %.1f) — nạp như thẻ mới, không gộp." % SIMILARITY_THRESHOLD,
                })
            existing.add(k)
            data.setdefault("evidence_cards", []).append(card)
            cards_by_key.setdefault(k, []).append(card)
            added += 1

    assert_unique(data["evidence_cards"])   # cổng bất biến: không bao giờ ghi sổ cái có id trùng
    data["meta"]["last_updated"] = args.today or data["meta"].get("last_updated", "")
    data["meta"]["last_backup"] = "BACKUPS/EBM_MASTER_%s_pre-ingest.json" % stamp
    data["meta"]["counts"]["evidence_cards"] = len(data["evidence_cards"])
    data["meta"]["counts"]["quarantined_cards"] = len(data.get("quarantined_cards", []))
    json.dump(data, open(master_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Nạp xong: +%d thẻ mới; %d thẻ cách ly đã khôi phục về notyet "
          "(%d thẻ phải cấp ID mới do xung đột lịch sử); "
          "%d thẻ Retraction and Replacement đã cập nhật tại chỗ "
          "(%d bản trùng cũ đã hợp nhất); %d cùng DOI/PMID nguồn khác nội dung — không gộp; "
          "%d trùng (bỏ qua, %d đã bù trường pmid/doi thiếu). Tổng sổ cái: %d thẻ." %
          (added, rehydrated, rehydrated_reassigned, replaced, replacement_duplicates_removed,
           same_source_new, dup, enriched,
           len(data["evidence_cards"])))
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
                "Nạp %d dashboard: +%d thẻ mới, %d thẻ cách ly khôi phục về notyet, "
                "%d trùng bỏ qua. Tổng sổ cái sau nạp: %d thẻ."
                % (len(args.files), added, rehydrated, dup, len(data["evidence_cards"]))
            ),
            affected_files=["EBM_MASTER.json"],
            source_files_modified=[os.path.basename(f) for f in args.files],
            pii_present=False,
            notes="Backup trước ghi: BACKUPS/EBM_MASTER_%s_pre-ingest.json" % stamp,
            session_id=args.today or "",
        )
    except Exception as exc:  # noqa: BLE001 — log lỗi không được chặn kết quả ingest
        print("  ⚠ Không ghi được AUDIT_LOG.jsonl (%s)." % exc)

    return 0


if __name__ == "__main__":
    sys.exit(main())
