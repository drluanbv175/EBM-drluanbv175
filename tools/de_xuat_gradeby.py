#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ĐỀ XUẤT `gradeBy` HÀNG LOẠT — máy đề xuất, bác sĩ duyệt THEO NHÓM (Tầng-1, 16/08/2026).

Vì sao: 474 item có `gradeLevel` khác 'na' chưa khai `gradeBy` (230 đang `apply`) —
tồn kho khai báo lớn nhất còn lại. Gõ tay 474 lần là phi thực tế; máy tự GHI là vi
phạm ranh giới (một `gradeBy` sai là lỗi truy nguyên — họ R4). Đường giữa đúng luật:
máy chỉ đề xuất khi CHÍNH `gradeSource`/`org` của item ĐÃ chứa bằng chứng chữ về hệ
chấm (COR/LOE · GRADE · USPSTF A–D · LoE/SoR EULAR…), gom thành NHÓM kèm trích
nguyên văn; bác sĩ duyệt nhóm nào thì `--ap-dung` nhóm đó (có sao lưu).

Ba luật cứng:
  1. KHÔNG suy từ tên tạp chí/thiết kế — chỉ từ chữ ĐANG CÓ trong item (chống BH08).
  2. Item không đủ bằng chứng chữ → nhóm «KHÔNG TỰ SUY ĐƯỢC», để nguyên cho tay người.
  3. `--ap-dung` CHỈ thêm trường `gradeBy` — không bao giờ chạm decision/gradeLevel (BH10).

Dùng:  python3 tools/de_xuat_gradeby.py                # quét + ghi file đề xuất
       python3 tools/de_xuat_gradeby.py --ap-dung G1 G3 # áp các nhóm bác sĩ đã duyệt
Mã thoát: 0 = chạy trọn · 2 = tham số/kho hỏng. Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
DASH = REPO / "EBM-Dashboards"
DE_XUAT_JSON = DASH / "derivatives" / "de-xuat-gradeby.json"

# Ngân hàng mẫu: (mã nhóm, tổ chức-hệ-chấm, [regex bằng chứng trên gradeSource+org]).
# Mỗi mẫu đòi BẰNG CHỨNG HỆ CHẤM tường minh — tên tổ chức suông KHÔNG đủ.
MAU = [
    ("G1", "ACC/AHA (COR/LOE)",
     [r"\bCOR\s*[I1V]+", r"\bLOE\s*[A-C]\b", r"Class\s*[I1V]+.{0,25}Level",
      r"khuyến cáo (?:COR|Class)"]),
    ("G2", "ESC (Class/Level)",
     [r"\bESC\b.{0,60}(?:Class|Level|I[ab])", r"Class\s*I{1,3}[ab]?\b.{0,40}\bESC\b"]),
    ("G3", "GRADE — tổ chức nêu trong nguồn",
     [r"\bGRADE\b", r"chứng cứ (?:cao|trung bình|thấp|rất thấp) theo GRADE",
      r"khuyến cáo (?:mạnh|có điều kiện|yếu)"]),
    ("G4", "USPSTF (A–D/I)",
     [r"\bUSPSTF\b.{0,40}(?:cấp|grade|mức|\b[A-DI]\b)", r"khuyến cáo cấp [A-DI]\b"]),
    ("G5", "EULAR (LoE/SoR)",
     [r"\bLoE\b", r"\bSoR\b", r"\bEULAR\b.{0,50}(?:mức|level|1[ab]|2[ab])"]),
    ("G6", "Oxford CEBM (level 1–5)",
     [r"\bOxford\b.{0,30}(?:CEBM|level)", r"\bCEBM\b"]),
]
TO_CHUC = re.compile(
    r"\b(ACC|AHA|ESC|EULAR|ACR|KDIGO|NICE|Cochrane|USPSTF|WHO|ADA|EASD|AASLD|EASL|"
    r"APASL|GOLD|GINA|IDSA|ATS|ERS|ASH|AGS|CHEST|SIGN|Endocrine Society|IHS|EAN)\b")


def _nap_vd():
    sp = importlib.util.spec_from_file_location("vd_gb", DASH / "tools" / "verify_dashboard.py")
    m = importlib.util.module_from_spec(sp)
    sys.modules["vd_gb"] = m
    sp.loader.exec_module(m)
    return m


def quet() -> tuple[dict, list]:
    vd = _nap_vd()
    nhom: dict[str, list[dict]] = defaultdict(list)
    khong_suy: list[dict] = []
    for f in sorted(DASH.glob("WebDashboard_*.html")):
        try:
            blk = vd.extract_data_block(f.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        if not blk:
            continue
        for c in vd.split_items(blk):
            grade = vd.field(c, "gradeLevel") or ""
            if grade in ("", "na") or vd.field(c, "gradeBy"):
                continue
            gs = vd.field(c, "gradeSource") or ""
            org = vd.field(c, "org") or ""
            von = f"{gs} | {org}"
            muc = {"file": f.name, "item": vd.field(c, "id") or "?",
                   "decision": vd.field(c, "decision") or "",
                   "trich": gs[:100]}
            for ma, ten, mau_re in MAU:
                if any(re.search(m, von, re.I) for m in mau_re):
                    # G3 (GRADE chung) đòi thêm TÊN tổ chức trong chữ — GRADE vô danh
                    # không truy nguyên được, giữ ở nhóm không-suy.
                    tc = TO_CHUC.search(von)
                    if ma == "G3" and not tc:
                        break
                    muc["de_xuat"] = (f"{tc.group(1)} (GRADE)" if ma == "G3"
                                      else ten if not tc or ma != "G3" else ten)
                    if ma != "G3":
                        muc["de_xuat"] = ten
                    nhom[ma].append(muc)
                    break
            else:
                khong_suy.append(muc)
    return dict(nhom), khong_suy


def ap_dung(cac_ma: list[str]) -> int:
    if not DE_XUAT_JSON.exists():
        print("🔴 Chưa có file đề xuất — chạy không tham số trước.")
        return 2
    dx = json.loads(DE_XUAT_JSON.read_text(encoding="utf-8"))
    vd = _nap_vd()
    hom_nay = dt.date.today().isoformat()
    ghi = 0
    theo_file: dict[str, list[dict]] = defaultdict(list)
    for ma in cac_ma:
        for muc in dx.get("nhom", {}).get(ma, []):
            theo_file[muc["file"]].append(muc)
    for ten_f, ds in theo_file.items():
        p = DASH / ten_f
        t = p.read_text(encoding="utf-8")
        goc = t
        for muc in ds:
            blk = vd.extract_data_block(t)
            for c in vd.split_items(blk or ""):
                if vd.field(c, "id") != muc["item"] or vd.field(c, "gradeBy"):
                    continue
                # chèn `gradeBy` NGAY SAU gradeLevel của đúng chunk — thay MỘT lần,
                # neo bằng đoạn duy nhất (id + gradeLevel) để không lây item khác
                m_gl = re.search(r"gradeLevel\s*:\s*['\"][^'\"]*['\"]", c)
                if not m_gl:
                    continue
                cu = c[:m_gl.end()]
                if cu in t:
                    t = t.replace(cu, cu + f", gradeBy: \"{muc['de_xuat']}\"", 1)
                    ghi += 1
                break
        if t != goc:
            p.with_suffix(p.suffix + f".bak-gradeby-{hom_nay}").write_text(
                goc, encoding="utf-8")
            p.write_text(t, encoding="utf-8")
            print(f"  ✓ {ten_f}: +{len(ds)} gradeBy (sao lưu .bak-gradeby-{hom_nay})")
    print(f"Đã ghi {ghi} trường gradeBy theo {len(cac_ma)} nhóm bác sĩ duyệt. "
          "KHÔNG đụng decision/gradeLevel. Chạy lại verify_dashboard các file trên.")
    return 0


def tra_song_g7() -> None:
    """ĐỢT 2 (16/08 — bác sĩ duyệt vòng meta): với nhóm KHÔNG-TỰ-SUY, hỏi PubMed
    loại xuất bản THẬT. CHỈ đề xuất khi chính bài LÀ «Practice Guideline» VÀ tên
    tổ chức đọc được từ tiêu đề/tạp chí của CHÍNH bài — tức tổ chức chấm là tác
    giả guideline, không phải suy từ uy tín tạp chí (chống đúng lỗi authority-
    từ-tên-tạp-chí đã vá 14/08). Ghi thành nhóm G7 chờ bác sĩ duyệt như mọi nhóm."""
    import time
    import urllib.request
    if not DE_XUAT_JSON.exists():
        print("🔴 Chạy quét thường trước để có danh sách không-tự-suy.")
        return
    dx = json.loads(DE_XUAT_JSON.read_text(encoding="utf-8"))
    ks = dx.get("khong_suy_duoc", [])
    # cần PMID: đọc lại từ dashboard theo (file, item)
    vd = _nap_vd()
    pmid_theo_muc: dict[tuple[str, str], str] = {}
    for f in sorted({m["file"] for m in ks}):
        try:
            blk = vd.extract_data_block((DASH / f).read_text(encoding="utf-8",
                                                             errors="replace"))
        except OSError:
            continue
        for c in vd.split_items(blk or ""):
            pm = vd.field(c, "pmid")
            if pm:
                pmid_theo_muc[(f, vd.field(c, "id") or "?")] = pm
    pmids = sorted({pmid_theo_muc.get((m["file"], m["item"]), "") for m in ks} - {""})
    print(f"Tra sống loại xuất bản cho {len(pmids)} PMID (lô 100)…")
    ptypes: dict[str, list[str]] = {}
    tieude: dict[str, str] = {}
    for i in range(0, len(pmids), 100):
        lo = pmids[i:i + 100]
        u = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed"
             f"&retmode=json&id={','.join(lo)}&tool=ebm&email=bsluanbv175@gmail.com")
        try:
            d = json.loads(urllib.request.urlopen(
                urllib.request.Request(u, headers={"User-Agent": "ebm-gradeby"}),
                timeout=30).read())
        except Exception as e:  # noqa: BLE001 — lô hỏng bỏ qua, không chết cả lượt
            print(f"  ⚠ lô {i//100+1} lỗi ({type(e).__name__}) — bỏ qua")
            continue
        for pm, rec in (d.get("result") or {}).items():
            if pm == "uids" or not isinstance(rec, dict):
                continue
            ptypes[pm] = [str(x) for x in (rec.get("pubtype") or [])]
            tieude[pm] = f"{rec.get('title', '')} | {rec.get('fulljournalname', '')}"
        time.sleep(0.34)
    g7 = []
    for m in ks:
        pm = pmid_theo_muc.get((m["file"], m["item"]), "")
        if not pm or "Practice Guideline" not in ptypes.get(pm, []):
            continue
        tc = TO_CHUC.search(tieude.get(pm, ""))
        if not tc:
            continue        # guideline nhưng không đọc được tổ chức → vẫn để tay
        g7.append({**m, "de_xuat": f"{tc.group(1)} (guideline gốc — pubtype PubMed)",
                   "pmid": pm})
    dx.setdefault("nhom", {})["G7"] = g7
    DE_XUAT_JSON.write_text(json.dumps(dx, ensure_ascii=False, indent=1),
                            encoding="utf-8")
    n_a = sum(1 for x in g7 if x["decision"] == "apply")
    print(f"G7 (tra sống pubtype): {len(g7)} item đề xuất được ({n_a} apply) — "
          f"chờ bác sĩ duyệt; {len(ks) - len(g7)} vẫn để tay người.")
    for x in g7[:5]:
        print(f"  · {x['file'][:40]} {x['item']} → {x['de_xuat']}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Đề xuất gradeBy hàng loạt — bác sĩ duyệt theo nhóm")
    ap.add_argument("--ap-dung", nargs="*", metavar="NHÓM",
                    help="áp các nhóm ĐÃ được bác sĩ duyệt (vd: G1 G3)")
    ap.add_argument("--tra-song", action="store_true",
                    help="đợt 2: hỏi PubMed pubtype cho nhóm không-tự-suy → nhóm G7")
    a = ap.parse_args()
    if a.tra_song:
        tra_song_g7()
        return 0
    if a.ap_dung:
        return ap_dung([x.upper() for x in a.ap_dung])

    nhom, khong_suy = quet()
    tong = sum(len(v) for v in nhom.values())
    hom_nay = dt.date.today().isoformat()
    DE_XUAT_JSON.parent.mkdir(exist_ok=True)
    DE_XUAT_JSON.write_text(json.dumps(
        {"ngay": hom_nay, "nhom": nhom,
         "khong_suy_duoc": khong_suy}, ensure_ascii=False, indent=1), encoding="utf-8")

    dong = [f"# ĐỀ XUẤT gradeBy THEO NHÓM — {hom_nay}", "",
            f"Máy nhận diện được **{tong}** item có bằng chứng chữ về hệ chấm ngay trong "
            f"`gradeSource`/`org`; **{len(khong_suy)}** item KHÔNG tự suy được (để tay người).",
            "", "> Máy chỉ ĐỀ XUẤT — bác sĩ duyệt nhóm nào thì chạy:",
            "> `python3 tools/de_xuat_gradeby.py --ap-dung <MÃ NHÓM…>`", ""]
    for ma, ten, _ in MAU:
        ds = nhom.get(ma, [])
        if not ds:
            continue
        n_apply = sum(1 for x in ds if x["decision"] == "apply")
        dong.append(f"## {ma} — {ten}: **{len(ds)} item** ({n_apply} đang apply)")
        for x in ds[:3]:
            dong.append(f"- `{x['file'][:44]}` {x['item']}: «{x['trich'][:90]}»"
                        f" → đề xuất `{x.get('de_xuat', ten)}`")
        if len(ds) > 3:
            dong.append(f"- … và {len(ds) - 3} item nữa (đủ trong de-xuat-gradeby.json)")
        dong.append("")
    dong += [f"## KHÔNG TỰ SUY ĐƯỢC — {len(khong_suy)} item",
             "Nguồn không chứa bằng chứng chữ về hệ chấm — cần bác sĩ tra nguồn gốc "
             "(đúng bài học SuyTim_NoiTiet ITEM-05: gradeSource là lời NGƯỜI SOẠN khai).",
             "", "> Cần bác sĩ kiểm chứng."]
    out = DASH / "derivatives" / f"DE-XUAT-GRADEBY_{hom_nay}.md"
    out.write_text("\n".join(dong) + "\n", encoding="utf-8")
    print(f"ĐỀ XUẤT gradeBy: {tong} item chia {sum(1 for v in nhom.values() if v)} nhóm · "
          f"{len(khong_suy)} không-tự-suy → {out.name}")
    for ma, ten, _ in MAU:
        if nhom.get(ma):
            n_a = sum(1 for x in nhom[ma] if x['decision'] == 'apply')
            print(f"  {ma} {ten}: {len(nhom[ma])} item ({n_a} apply)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
