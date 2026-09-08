#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dashboard_content_audit.py — CỔNG KIỂM CHẤT LƯỢNG NỘI DUNG dashboard EBM (chống "rác" tái diễn).

Phát hiện 3 loại rác làm dashboard mất giá trị/khó đọc:
  (A) Câu NGOẠI NGỮ nhồi nguyên văn abstract vào summary (conclusion/doNow/dontDo/redFlags)
      hoặc vào item.action  → đáng lẽ phải là tổng hợp TIẾNG VIỆT.
  (B) item.vn (Áp dụng tại VN) chỉ là PLACEHOLDER "[CẦN…]" hoặc rỗng/lặp y hệt nhau.
  (C) item.action rỗng/'—'.

Dùng 2 vai:
  • AUDIT:  python3 tools/dashboard_content_audit.py            → liệt kê rác mọi file
            python3 tools/dashboard_content_audit.py FILE.html  → 1 file (in chi tiết từng item)
  • GATE :  python3 tools/dashboard_content_audit.py --gate FILE.html
            → exit 0 nếu SẠCH, exit 1 nếu còn rác (nối vào pipeline xuất dashboard để CHẶN).

KHÔNG sửa gì — chỉ kiểm. Heuristic: câu ≥5 từ mà không có dấu tiếng Việt = ngoại ngữ.
"""
import os
import re
import sys
import glob
import json

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


HERE = os.path.dirname(os.path.abspath(__file__))
DASH_DIR = os.path.dirname(HERE)

_VI = "ăâđêôơưàáạảãằắặẳẵầấậẩẫèéẹẻẽềếệểễìíịỉĩòóọỏõồốộổỗờớợởỡùúụủũừứựửữỳýỵỷỹ"
_HEAD = re.compile(r"^\s*(conclusion|in conclusion|keywords?|background|objective|"
                   r"methods?|results?|findings?|introduction|aim|purpose)\b", re.I)


def has_vi(t):
    t = (t or "").lower()
    return any(c in _VI for c in t)


def foreign(t):
    t = str(t or "").strip()
    if not t:
        return False
    if _HEAD.match(t):
        return True
    return len(t.split()) >= 5 and not has_vi(t)


def placeholder(t):
    return bool(re.match(r"^\s*\[\s*CẦN", str(t or "")))


def read_js_string(text, i):
    """Đọc 1 chuỗi JS bắt đầu ở text[i] (phải là ' " hoặc `). Trả (value, end_index_sau_quote)."""
    q = text[i]
    if q not in "\"'`":
        return None, i
    i += 1
    out = []
    while i < len(text):
        c = text[i]
        if c == "\\":
            out.append(text[i:i + 2]); i += 2; continue
        if c == q:
            return "".join(out), i + 1
        out.append(c); i += 1
    return "".join(out), i


def val_after_key(obj, key):
    """Lấy GIÁ TRỊ CHUỖI của key ngay sau dạng `key:` hoặc `key :` trong đoạn obj (chuỗi đầu tiên)."""
    m = re.search(r"(?<![\w$])" + re.escape(key) + r"\s*:\s*", obj)
    if not m:
        return None
    j = m.end()
    if j < len(obj) and obj[j] in "\"'`":
        v, _ = read_js_string(obj, j)
        return v
    return None


def find_obj_end(text, open_idx):
    depth = 0; i = open_idx; instr = None; esc = False
    while i < len(text):
        c = text[i]
        if instr:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == instr: instr = None
        else:
            if c in "\"'`": instr = c
            elif c == "{": depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0: return i
        i += 1
    return -1


def split_items(items_text):
    """Cắt mảng items[...] thành danh sách đoạn text từng object {...} (cân ngoặc, bỏ qua chuỗi)."""
    objs = []; i = 0
    while i < len(items_text):
        if items_text[i] == "{":
            e = find_obj_end(items_text, i)
            if e == -1: break
            objs.append(items_text[i:e + 1]); i = e + 1
        else:
            i += 1
    return objs


def string_list(arr_text):
    """Trích mọi chuỗi trong đoạn [ ... ]."""
    out = []; i = 0
    while i < len(arr_text):
        if arr_text[i] in "\"'`":
            v, j = read_js_string(arr_text, i); out.append(v); i = j
        else:
            i += 1
    return out


def audit_file(path):
    t = open(path, encoding="utf-8").read()
    m = re.search(r"const\s+DATA\s*=", t)
    if not m:
        return {"file": os.path.basename(path), "error": "no DATA"}
    ob = t.find("{", m.end())
    data = t[ob:find_obj_end(t, ob) + 1]

    issues = {"summary_foreign": [], "items_action_foreign": [], "items_vn_placeholder": [],
              "items_action_empty": []}

    # summary
    sm = re.search(r"summary\s*:\s*\{", data)
    if sm:
        so = data.find("{", sm.end() - 1)
        summ = data[so:find_obj_end(data, so) + 1]
        concl = val_after_key(summ, "conclusion")
        if foreign(concl):
            issues["summary_foreign"].append("conclusion")
        for key in ("doNow", "dontDo", "redFlags"):
            am = re.search(re.escape(key) + r"\s*:\s*\[", summ)
            if am:
                ao = summ.find("[", am.end() - 1)
                ae = summ.find("]", ao)
                for s in string_list(summ[ao:ae + 1]):
                    if foreign(s):
                        issues["summary_foreign"].append("%s: %s…" % (key, (s or "")[:40]))

    # items
    im = re.search(r"items\s*:\s*\[", data)
    n_items = 0
    if im:
        io = data.find("[", im.end() - 1)
        ie = find_obj_end(data, data.find("{", io)) if data.find("{", io) != -1 else -1
        items_text = data[io:]
        for obj in split_items(items_text):
            iid = val_after_key(obj, "id") or "?"
            if not re.match(r"ITEM-?\d", str(iid)):
                continue
            n_items += 1
            action = val_after_key(obj, "action")
            vn = val_after_key(obj, "vn")
            if foreign(action):
                issues["items_action_foreign"].append(iid)
            elif not action or str(action).strip() in ("", "—", "-"):
                issues["items_action_empty"].append(iid)
            if placeholder(vn) or not vn or str(vn).strip() in ("", "—"):
                issues["items_vn_placeholder"].append(iid)

    total = sum(len(v) for v in issues.values())
    return {"file": os.path.basename(path), "n_items": n_items, "total_issues": total, "issues": issues}


def main():
    args = sys.argv[1:]
    gate = "--gate" in args
    args = [a for a in args if a != "--gate"]
    if args:
        files = [a if os.path.isabs(a) else os.path.join(DASH_DIR, a) for a in args]
    else:
        files = sorted(glob.glob(os.path.join(DASH_DIR, "WebDashboard_*.html")))

    rep = [audit_file(f) for f in files]
    polluted = [r for r in rep if r.get("total_issues")]

    # Rác CỨNG (chặn phát hành): câu ngoại ngữ ở summary/action, hoặc action rỗng.
    # Rác MỀM (chỉ cảnh báo): vn chỉ là placeholder [CẦN…] — trung thực, nên bổ sung nhưng không chặn.
    HARD = ("summary_foreign", "items_action_foreign", "items_action_empty")
    if gate:
        hard_fail = [r for r in polluted if any(r["issues"].get(k) for k in HARD)]
        for r in polluted:
            hi = {k: v for k, v in r["issues"].items() if v and k in HARD}
            soft = {k: v for k, v in r["issues"].items() if v and k not in HARD}
            tag = "⛔ RÁC CỨNG" if hi else "⚠ cảnh báo mềm"
            print("%s: %s%s%s" % (tag, r["file"],
                                  " | cứng=%s" % hi if hi else "",
                                  " | mềm=%s" % {k: len(v) for k, v in soft.items()} if soft else ""))
        if hard_fail:
            print("⛔ GATE FAIL: %d/%d dashboard còn rác CỨNG (ngoại ngữ) — KHÔNG phát hành."
                  % (len(hard_fail), len(rep)))
            return 1
        print("✓ GATE PASS: không còn rác cứng (%d file; có thể còn placeholder vn cần bổ sung)." % len(rep))
        return 0

    # audit
    print("%-58s items  rác  chi tiết" % "FILE")
    for r in sorted(rep, key=lambda x: -x.get("total_issues", 0)):
        if "error" in r:
            print("  %-56s  (lỗi: %s)" % (r["file"][:56], r["error"])); continue
        d = {k: len(v) for k, v in r["issues"].items() if v}
        print("  %-56s %3d  %3d  %s" % (r["file"].replace("WebDashboard_EBM_", "")[:56],
                                        r["n_items"], r["total_issues"], d or "✓ sạch"))
    print("\nTổng: %d/%d dashboard có rác nội dung." % (len(polluted), len(rep)))
    if len(files) == 1:
        print(json.dumps(rep[0], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
