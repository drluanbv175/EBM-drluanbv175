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

# ── Mở rộng 20/10/2026 (bác sĩ: «Giải quyết 3 vấn đề chưa đạt» — 330 mục chưa khai gradeBy). Đo cùng ngày: 255/256 mục
# rơi vào «không tự suy» dù CHÍNH gradeSource đã nói rõ ai chấm, chỉ vì kho mẫu thiếu. Ba nhóm mới, vẫn đúng luật 1 (chỉ
# từ CHỮ đang có trong item), xét theo THỨ TỰ: G9 trước G8 — «đánh giá vận hành» là lời người soạn tự nhận đã chấm.
#   G9  lời người soạn tự nhận («đánh giá vận hành») ⇒ «Người soạn — đánh giá vận hành» (giá trị đã dùng sẵn trong kho);
#   G8  Cochrane + từ chỉ mức chắc chắn ⇒ «Cochrane (GRADE)»;
#   G10 ĐÚNG MỘT tổ chức có tên + thuật ngữ phân hạng tường minh (Class/Level, loại I, mức A, 1A, A/B/C/E, A–D…) ⇒
#       «<tổ chức> (phân hạng nguyên bản)»; hai tổ chức trở lên ⇒ không đoán;
#   G11 KHÔNG nêu tổ chức nào, chỉ mô tả thiết kế/nguy cơ sai lệch ⇒ «Người soạn — đánh giá theo thiết kế (nguồn không
#       tự phân hạng)»: mức trên dashboard do người soạn gán (nghiên cứu gốc không tự mang mức chắc chắn).
TO_CHUC_RONG = re.compile(
    r"\b(ACC/AHA|AHA/ASA|ACC|AHA|ASA|ESC|ESO|EANS|ESVS|ESH|EAS|EULAR|ACR|KDIGO|NICE|USPSTF|WHO|ADA|EASD|AASLD|"
    r"EASL|APASL|GOLD|GINA|IDSA|ATS|ERS|ASH|AGS|CHEST|SIGN|Endocrine Society|IHS|EAN|AAN|AAP|BSH|HFSA|AGA|ACG|"
    r"ASCO|ESMO|NCCN|SMFM|ACOG|SVS|Cochrane|FDA|EMA|PRAC|MHRA)\b")
# Tên đầy đủ hay gặp ở trường `org` — G10 đòi tổ chức nêu trong gradeSource TRÙNG tổ chức của item (soát 20/10: một bài
# tổng quan trên Am J Emerg Med nói lại «chất lượng rất thấp» của ATS — không chắc ai chấm ⇒ không được gán cho ATS).
TEN_DAY_DU = {"AHA": "American Heart Association", "ASA": "American Stroke Association", "ADA": "American Diabetes",
              "AAN": "American Academy of Neurology", "GOLD": "Global Initiative for Chronic", "ACC": "American College of Cardiology",
              "ESC": "European Society of Cardiology", "EULAR": "European Alliance", "ACR": "American College of Rheumatology",
              "KDIGO": "Kidney Disease", "AASLD": "American Association for the Study of Liver", "WHO": "World Health",
              "AAP": "American Academy of Pediatrics", "BSH": "British Society for Haematology", "ATS": "American Thoracic"}
_THUAT_NGU_PHAN_HANG = re.compile(
    r"khuyến cáo loại\s*(?:I{1,3}|[123])|\bClass\s*(?:I{1,3}|[123])[ab]?\b|Class/Level|\bCOR\b|\bLOE\b|"
    r"\bLevel\s*[A-C]\b|\bmức\s*[A-C]\b|\b[12][A-D]\b|A/B/C/E|\(A[–-]D\)|\bLoE\b|\bSoR\b|"
    r"khuyến cáo (?:mạnh|có điều kiện|yếu)|chất lượng (?:RẤT THẤP|rất thấp|thấp|trung bình|cao)", re.I)
_COCHRANE_MUC = re.compile(r"Cochrane.{0,80}(?:chất lượng|chắc chắn|tin cậy|certainty|moderate|high|low)|"
                           r"(?:chất lượng|chắc chắn|tin cậy|certainty).{0,40}Cochrane", re.I)
_THIET_KE = re.compile(r"\bRCT\b|thử nghiệm (?:ngẫu nhiên|pha)|cohort|đoàn hệ|phân tích gộp|meta-?analysis|\bSR-?MA\b|"
                       r"tổng quan hệ thống|nghiên cứu quan sát|bệnh-chứng|cắt ngang|nguy cơ sai lệch|"
                       r"thiết kế|kiểm định|IPD", re.I)
# Chữ nói về MỨC CHẮC CHẮN mà không nói ai chấm (vd «GRADE nguyên văn: very low», «Meta-analysis độ chắc chắn cao») — có thể
# là phân hạng CỦA NGUỒN ⇒ không được gắn G11 «nguồn không tự phân hạng» (soát 20/10/2026: VKDT ITEM-05 trích GRADE của bài
# mà bị xếp G11). «GRADE EtD» là khối Evidence-to-Decision do người soạn dựng ⇒ không tính.
_MUC_CO_THE_CUA_NGUON = re.compile(r"GRADE(?!\s*EtD)|nguyên văn|certainty|\bquality\b|độ chắc chắn|"
                                   r"chất lượng\s+(?:rất\s+)?(?:cao|thấp|trung bình)", re.I)
NHOM_MO_RONG = [("G9", "Người soạn — đánh giá vận hành"), ("G8", "Cochrane (GRADE)"),
                ("G10", "<tổ chức> (phân hạng nguyên bản)"),
                ("G11", "Người soạn — đánh giá theo thiết kế (nguồn không tự phân hạng)")]


def phan_nhom(gs: str, org: str) -> tuple[str, str] | None:
    """(mã nhóm, gradeBy đề xuất) hoặc None (để tay người) — chỉ đọc CHỮ của item (luật 1).

    Vá 20/10/2026: (a) G1 «ACC/AHA» chỉ khi chữ có ACC — một mục trích AHA/ASA từng bị gán ACC/AHA; (b) G5 «EULAR» chỉ khi
    chữ có EULAR — mẫu «LoE» không phân biệt hoa/thường bắt cả «LOE A» của AHA; (c) mục khớp mẫu G3 mà không có tên tổ
    chức trước đây bị `break` loại khỏi CẢ hai danh sách (mất khỏi báo cáo) — nay rơi xuống nhóm mở rộng / tay người."""
    von = f"{gs} | {org}"
    for ma, ten, mau_re in MAU:
        if ma == "G1" and not re.search(r"\bACC\b", von):
            continue
        if ma == "G5" and not re.search(r"\bEULAR\b", von):
            continue
        if any(re.search(m, von, re.I) for m in mau_re):
            if ma == "G3":
                tc = TO_CHUC.search(von)
                if not tc:
                    break  # GRADE vô danh — không truy nguyên được tổ chức ⇒ không dùng G3
                return "G3", f"{tc.group(1)} (GRADE)"
            return ma, ten
    return phan_nhom_mo_rong(gs, org)


def phan_nhom_mo_rong(gs: str, org: str) -> tuple[str, str] | None:
    """(mã nhóm, gradeBy đề xuất) cho mục MAU gốc không nhận ra; None = để tay người. Chỉ đọc chữ của item."""
    if re.search(r"bác sĩ|thẩm định", gs, re.I):
        return None  # mức có bàn tay bác sĩ (vd «bác sĩ chuẩn y 14/08/2026») — để bác sĩ tự xác nhận, máy không gán nhãn
    if re.search(r"đánh giá vận hành", gs, re.I):
        return "G9", "Người soạn — đánh giá vận hành"
    if _COCHRANE_MUC.search(gs):
        return "G8", "Cochrane (GRADE)"
    # Tên tổ chức CHỈ lấy từ chữ của gradeSource (soát 20/10: org «SVS / ESVS» + «SVS grade 1» bị gán ESVS); trường `org`
    # chỉ dùng để ĐỐI CHIẾU tổ chức đó có đúng là nơi ban hành item không.
    to_chuc = {m.group(1) for m in TO_CHUC_RONG.finditer(gs)}
    if to_chuc and _THUAT_NGU_PHAN_HANG.search(gs):
        # «ACC/AHA» và «ACC», «AHA» là một ⇒ gộp tên con vào tên ghép trước khi đếm.
        ghep = {t for t in to_chuc if "/" in t}
        don = {t for t in to_chuc if "/" not in t and not any(t in g.split("/") for g in ghep)}
        con = ghep | don
        if len(con) == 1:
            ten = next(iter(con))
            if all(t in org or TEN_DAY_DU.get(t, "\0") in org for t in ten.split("/")):
                return "G10", f"{ten} (phân hạng nguyên bản)"
        return None
    if not to_chuc and _THUAT_NGU_PHAN_HANG.search(gs):
        # gradeSource có thuật ngữ phân hạng mà không nêu tổ chức ⇒ mức thuộc NGUỒN của chính item (vd guideline AHA/ASA ghi
        # «Khuyến cáo loại I») — chỉ khi trường `org` chỉ ra ĐÚNG MỘT tổ chức đã biết (tạp chí như «Lancet» ⇒ không đoán).
        o = {m.group(1) for m in TO_CHUC_RONG.finditer(org)} | {k for k, v in TEN_DAY_DU.items() if v in org}
        ghep = {t for t in o if "/" in t}
        con = ghep | {t for t in o if "/" not in t and not any(t in g.split("/") for g in ghep)}
        if len(con) == 1:
            return "G10", f"{next(iter(con))} (phân hạng nguyên bản)"
        return None
    if (not to_chuc and _THIET_KE.search(gs) and not re.search(r"khuyến cáo|guideline|hướng dẫn|đồng thuận", gs, re.I)
            and not _MUC_CO_THE_CUA_NGUON.search(gs)):
        return "G11", "Người soạn — đánh giá theo thiết kế (nguồn không tự phân hạng)"
    return None


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
            muc = {"file": f.name, "item": vd.field(c, "id") or "?",
                   "decision": vd.field(c, "decision") or "",
                   "trich": gs[:100]}
            kq = phan_nhom(gs, org)
            if kq:
                muc["de_xuat"] = kq[1]
                nhom[kq[0]].append(muc)
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
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from tra_dinh_danh import email_lien_he  # noqa: PLC0415 — email liên hệ từ cấu hình, không viết cứng (27/09/2026)
    mail = email_lien_he()
    hau_email = f"&email={mail}" if mail else ""
    for i in range(0, len(pmids), 100):
        lo = pmids[i:i + 100]
        u = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed"
             f"&retmode=json&id={','.join(lo)}&tool=ebm{hau_email}")
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
    for ma, ten in [(m, t) for m, t, _ in MAU] + NHOM_MO_RONG:
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
    for ma, ten in [(m, t) for m, t, _ in MAU] + NHOM_MO_RONG:
        if nhom.get(ma):
            n_a = sum(1 for x in nhom[ma] if x['decision'] == 'apply')
            print(f"  {ma} {ten}: {len(nhom[ma])} item ({n_a} apply)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
