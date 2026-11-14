#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KIỂM CHÉO NGỮ NGHĨA — K1 QUẦN THỂ + K4 CHIỀU KHUYẾN CÁO (25/09/2026)

VÌ SAO CÓ
=========
Thiết kế ở `audit/16-thiet-ke-kiem-cheo-ngu-nghia-apply_2026-09-25.md`, bác sĩ duyệt 25/09/2026:
K3 trước (đã có, `tools/kiem_cheo_ngu_nghia.py`), rồi tới K1; mọi phép kiểm ở MỨC CẢNH BÁO.

Các cổng hiện có chỉ kiểm nguồn có thật và hiệu số HR. Chúng không bắt hai lỗi nguy hiểm:

* **K1 — sai quần thể.** Mục ghi «HFpEF», nguồn chỉ nói HFrEF; mục ghi «eGFR ≥ 20», nguồn
  nói ≥ 25. `pico.P:'match'` chỉ là lời người soạn tự khai.
* **K4 — sai chiều.** Mục `decision:'apply'` nhưng tiêu đề/tóm tắt nguồn nói «not
  recommended», «no significant benefit», «Class III»…

CÁCH LÀM
========
Chỉ đọc mục `decision:'apply'` có PMID/DOI. Văn bản nguồn (tiêu đề + tóm tắt) lấy từ:
  * `--nguon-json TỆP` — {"<pmid|doi>": {"title": "...", "abstract": "..."}} (ngoại tuyến,
    dùng khi đã tải tóm tắt qua connector MCP hoặc từ một lượt trước), và/hoặc
  * `--online` — tải tóm tắt PubMed bằng CHÍNH hàm `lay_tom_tat()` của `kiem_so_lieu.py`.
Không có văn bản nguồn ⇒ ⚪, không bao giờ ✓.

K1: (a) ngưỡng số của EF, eGFR, tuổi, HbA1c, BMI, LDL trong `population` + `pico.P`: nguồn có
nhắc chỉ số đó mà không thấy CON SỐ ấy gần đó ⇒ 🟠 kèm đoạn nguồn; (b) cặp quần thể loại trừ
nhau (HFrEF↔HFpEF, típ 1↔típ 2, trẻ em↔người lớn, thai kỳ↔ngoài thai kỳ, lọc máu↔không lọc
máu): mục mang một vế mà nguồn chỉ nêu vế kia ⇒ 🟠.
K4: tìm tín hiệu ngược chiều rõ ràng trong nguồn ⇒ 🟠 kèm câu nguyên văn.

BA MỨC — cố ý KHÔNG có mức «SAI» (BH08: vắng mặt trong tóm tắt không chứng minh trích sai)
  ✓ khớp · 🟠 cần đọc lại (kèm đoạn nguồn) · ⚪ chưa kiểm được (nguồn không nêu / không tải được)
Tóm tắt thường nêu kết cục phụ «không khác biệt» ngay trong thử nghiệm dương tính ⇒ K4 SẼ có
báo động giả; đó là lý do công cụ chỉ cảnh báo và phải đo trên bộ vàng trước khi tính chặn.
Công cụ KHÔNG sửa dashboard, KHÔNG đổi `decision`, KHÔNG chặn xuất.

Dùng:
    python tools/kiem_quan_the_chieu.py DASH.html --nguon-json tom_tat.json
    python tools/kiem_quan_the_chieu.py DASH.html --online [--json]

Mã thoát: 0 = không có 🟠 · 1 = có mục cần đọc lại · 2 = không đo được (không đọc được DATA,
hoặc không mục apply nào có văn bản nguồn). «Không đo được» không bao giờ là 0.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / "tools" / tep)
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod


_K3 = _nap("_k3_kqtc", "kiem_cheo_ngu_nghia.py")
chuan_hoa = _K3.chuan_hoa
doc_data = _K3.doc_data


def chuan_hoa_nguon(t: str) -> str:
    """Chuẩn hoá văn bản NGUỒN (tóm tắt PubMed — văn bản thuần): «<»/«>» là dấu so sánh, không phải thẻ HTML (vá 14/11/2026)."""
    return chuan_hoa(t, html=False)


# ── Thân tóm tắt: bỏ dòng trích dẫn, tác giả, cơ quan, định danh (vá 14/11/2026) ─────────────────
# Bản efetch dạng text: «1. Tạp chí. Năm…» · tiêu đề · tác giả (cá nhân hoặc tổ chức) · Collaborators · Author information
# (cơ quan) · Comment in/Erratum in… · THÂN tóm tắt · © · Conflict of interest · DOI/PMCID/PMID. Trước đây K1/K4 đọc CẢ bản ⇒
# «Children's Hospital», «Department of Paediatrics», «American Academy of Pediatrics» làm K1 tưởng nguồn có nêu «trẻ em»
# (4 lần K1 báo ✓ trên mục đã bị đổi quần thể), số trang/năm trong dòng trích dẫn khớp nhầm cỡ mẫu.
_LA_EFETCH = re.compile(r"(?m)^PMID:\s*\d+")
_DOAN_SIEU_DU_LIEU = re.compile(
    r"^(?:author information|collaborators|comment (?:in|on)|erratum (?:in|for)|update (?:of|in)|updated (?:and )?"
    r"(?:republished )?(?:in|from)|republished (?:in|from)|corrected and republished|retraction (?:in|of)|retracted|"
    r"expression of concern|copyright|©|\(c\) \d{4}|conflict of interest|competing interests?|declaration of "
    r"(?:competing )?interests?|doi:|pmid:|pmcid:|summary for patients in)", re.I)
_PHAN_TAC_GIA = re.compile(r"^(?:[\w'’.\-]+\s+){1,4}[A-Z]{1,4}(?:\(\d+\))*$")


def _la_ds_tac_gia(d: str) -> bool:
    """Đoạn là danh sách tác giả «Họ AB(1), Họ C, …» (≥ 3 phần, ≥ 60% phần đúng khuôn tên PubMed)."""
    phan = [x.strip() for x in re.split(r"[,;]", d.strip().rstrip(".")) if x.strip()]
    return len(phan) >= 3 and sum(bool(_PHAN_TAC_GIA.match(x)) for x in phan) >= 0.6 * len(phan)


def than_nguon(raw: str) -> str:
    """Tiêu đề + THÂN tóm tắt của bản efetch dạng text. Văn bản không theo khuôn efetch (vd «tiêu đề. tóm tắt» từ
    --nguon-json) ⇒ giữ nguyên."""
    raw = raw or ""
    doan = [d.strip() for d in re.split(r"\n\s*\n", raw) if d.strip()]
    if not (doan and re.match(r"^\d+\.\s", doan[0]) and _LA_EFETCH.search(raw)):
        return raw
    if not re.search(r"\d{4}", doan[0]):
        # khuôn sách/«RETRACTED ARTICLE»: dòng đầu là tiêu đề hoặc nhãn — giữ mọi đoạn trừ siêu dữ liệu và danh sách tác giả
        giu = [re.sub(r"^\d+\.\s+", "", doan[0])]
        giu += [d for d in doan[1:] if not _DOAN_SIEU_DU_LIEU.match(d) and not _la_ds_tac_gia(d)]
        return "\n\n".join(giu)
    giu, i = [], 1
    if i < len(doan):
        giu.append(doan[i])                           # tiêu đề
        i += 1
    tac_gia_da_bo = False
    while i < len(doan) and doan[i].startswith("["):  # «[Article in German…]», «[No authors listed]»
        tac_gia_da_bo |= doan[i].lower().startswith("[no authors")
        i += 1
    if not tac_gia_da_bo and i < len(doan) and not _DOAN_SIEU_DU_LIEU.match(doan[i]):
        i += 1                                        # dòng tác giả (cá nhân hoặc TỔ CHỨC — tổ chức không nhận được qua khuôn tên)
    giu += [d for d in doan[i:] if not _DOAN_SIEU_DU_LIEU.match(d) and not _la_ds_tac_gia(d)]
    return "\n\n".join(giu)

# ── K1a: ngưỡng số ─────────────────────────────────────────────────────────────
# (khoá, mẫu nhận chỉ số ở MỤC (Việt/Anh), mẫu nhận chỉ số ở NGUỒN (Anh))
_CHI_SO = (
    ("ef", r"(?:lv)?ef|phân suất tống máu", r"(?:lv)?ef|ejection fraction"),
    ("egfr", r"egfr|mlct|mức lọc cầu thận", r"egfr|glomerular filtration"),
    ("tuoi", r"tuổi|age[ds]?", r"aged?|years of age|years old|years or older|older"),
    ("hba1c", r"hba1c|a1c", r"hba1c|a1c|glycated h[a]?emoglobin"),
    ("bmi", r"bmi", r"bmi|body mass index"),
    ("ldl", r"ldl(?:-c)?", r"ldl(?:-c| cholesterol)?"),
)
_SO = r"(\d+(?:[.,]\d+)?)"
_TOAN_TU = r"(<=|>=|<|>|=|dưới|trên|từ)?"
_CUA_SO = 60   # ký tự quanh chỉ số trong nguồn để tìm con số


def trich_nguong(van_ban: str) -> list[tuple[str, str]]:
    """[(khoá chỉ số, con số)] từ văn bản MỤC. «≥65 tuổi» và «tuổi ≥ 65» đều được."""
    t = chuan_hoa(van_ban)
    ra: list[tuple[str, str]] = []
    for khoa, mau_muc, _ in _CHI_SO:
        truoc = re.compile(rf"(?<!\w)(?:{mau_muc})(?!\w)\s*{_TOAN_TU}\s*{_SO}")
        sau = re.compile(rf"{_TOAN_TU}\s*{_SO}\s*%?\s*(?:{mau_muc})(?!\w)")
        for m in list(truoc.finditer(t)) + (list(sau.finditer(t)) if khoa == "tuoi" else []):
            so = m.group(2).replace(",", ".")
            if (khoa, so) not in ra:
                ra.append((khoa, so))
    return ra


def _doan(t: str, i: int, j: int, le: int = 70) -> str:
    return t[max(0, i - le):min(len(t), j + le)].strip()


def kiem_nguong(khoa: str, so: str, nguon: str) -> tuple[str, str]:
    """(mức, đoạn nguồn). Nguồn đã chuẩn hoá."""
    mau_nguon = next(m for k, _, m in _CHI_SO if k == khoa)
    lan = list(re.finditer(rf"(?<!\w)(?:{mau_nguon})(?!\w)", nguon))
    if not lan:
        return "chua_kiem", ""
    so_re = re.compile(rf"(?<![\d.]){re.escape(so)}(?:\.0+)?(?![\d])")
    for m in lan:
        vung = nguon[max(0, m.start() - _CUA_SO):m.end() + _CUA_SO]
        if so_re.search(vung):
            return "khop", _doan(nguon, m.start(), m.end())
    m = lan[0]
    return "can_doc", _doan(nguon, m.start(), m.end())


# ── K1b: cặp quần thể loại trừ nhau ────────────────────────────────────────────
# Mỗi vế: (tên, mẫu ở MỤC, mẫu ở NGUỒN). Vế «phủ định» (non-dialysis…) được xoá khỏi văn bản
# trước khi tìm vế dương tương ứng, để «non-dialysis» không bị đọc thành «dialysis».
# Từ vựng mở rộng 14/11/2026 (đo: 84 lần K1 lọt im vì cách viết tiếng Việt ngoài từ điển — «bệnh nhi», «trẻ vị thành niên»,
# «người trưởng thành», «ĐTĐ1», «PSTM giảm», «phân suất tống máu còn bảo tồn»). Phía NGUỒN cố ý KHÔNG có «child» trần
# (khớp nhầm «Child-Pugh»).
_CAP = (
    (("HFrEF", r"hfref|(?:phân suất tống máu|pstm|ef) giảm", r"hfref|reduced (?:left ventricular )?ejection fraction"),
     ("HFpEF", r"hfpef|(?:phân suất tống máu|pstm|ef) (?:còn )?bảo tồn",
      r"hfpef|preserved (?:left ventricular )?ejection fraction")),
    (("ĐTĐ típ 1", r"(?:típ|tuýp|type) ?1|đtđ ?1", r"type 1 diabetes|t1d"),
     ("ĐTĐ típ 2", r"(?:típ|tuýp|type) ?2|đtđ ?2", r"type 2 diabetes|t2d")),
    (("trẻ em", r"trẻ em|bệnh nhi|nhi khoa|(?:trẻ )?vị thành niên|thanh thiếu niên|trẻ sơ sinh|children|pediatric",
      r"children|pa?ediatric|adolescen\w*|infants?|neonat\w*|newborns?"),
     ("người lớn", r"người lớn|người trưởng thành|adults?", r"adults?")),
    (("ngoài thai kỳ", r"ngoài thai kỳ|không mang thai|non-pregnant", r"non-?pregnant|not pregnant"),
     ("thai kỳ", r"thai kỳ|thai phụ|phụ nữ có thai|mang thai|pregnan\w*", r"pregnan\w*")),
    (("không lọc máu", r"không lọc máu|chưa lọc máu|chưa chạy thận|non-dialysis",
      r"non-?dialysis|not (?:on|receiving|requiring) dialysis"),
     ("lọc máu", r"lọc máu|chạy thận|thẩm phân|dialysis", r"dialysis|ha?emodialysis")),
)


# Tiền tố phủ định ở MỤC: «không chuyên HFrEF», «loại trừ trẻ em», «excluding dialysis»… ⇒ mục KHÔNG
# mang vế đó. Cho phép tối đa 2 từ chen giữa («không áp dụng cho bệnh nhân HFrEF»).
_PHU_DINH = (r"(?:không(?: chuyên| phải| chỉ| dành cho| áp dụng cho| gồm| có)?|ngoại trừ|loại trừ|trừ"
             r"|excluding|without|not)")


def _bo_phu_dinh(mau: str, t: str) -> str:
    """Xoá các lần vế `mau` xuất hiện SAU một tiền tố phủ định (vế phủ định không phải vế mang)."""
    return re.sub(rf"(?<!\w){_PHU_DINH}\s+(?:[^\s.;,()]+\s+){{0,2}}?(?:{mau})(?!\w)", " ", t)


def _co(mau: str, t: str) -> bool:
    return re.search(rf"(?<!\w)(?:{mau})(?!\w)", t) is not None


def _xoa(mau: str, t: str) -> str:
    return re.sub(rf"(?<!\w)(?:{mau})(?!\w)", " ", t)


def kiem_cap(muc: str, nguon: str) -> list[dict]:
    """Mỗi phần tử: {ve_muc, ve_nguon, muc: khop|can_doc|chua_kiem}."""
    ra = []
    for a, b in _CAP:
        # vế đầu của mỗi cặp ở trên được đặt sao cho vế «phủ định/đặc hiệu hơn» xét trước
        muc_con = muc
        nguon_con = nguon
        co_muc = {}
        co_nguon = {}
        for ten, m_muc, m_nguon in (a, b):
            muc_con = _bo_phu_dinh(m_muc, muc_con)
            co_muc[ten] = _co(m_muc, muc_con)
            co_nguon[ten] = _co(m_nguon, nguon_con)
            if co_muc[ten]:
                muc_con = _xoa(m_muc, muc_con)
            if co_nguon[ten]:
                nguon_con = _xoa(m_nguon, nguon_con)
        for ten, doi in ((a[0], b[0]), (b[0], a[0])):
            if not co_muc[ten] or co_muc[doi]:
                continue           # mục không mang vế này, hoặc mang cả hai vế (không kết luận)
            if co_nguon[ten]:
                kq = "khop"
            elif co_nguon[doi]:
                kq = "can_doc"
            else:
                kq = "chua_kiem"
            ra.append({"ve_muc": ten, "ve_nguon": doi if kq == "can_doc" else ten, "muc": kq})
    return ra


# ── K4: tín hiệu ngược chiều ───────────────────────────────────────────────────
_NGUOC = re.compile(
    r"(?<!\w)(?:is |are )?not recommended|should not be (?:routinely )?(?:used|given|offered|prescribed|considered|initiated"
    r"|started|screened)"
    r"|no (?:significant |clinically meaningful |additional )?(?:benefit|reduction|improvement|difference)"
    # 14/11/2026: thì hiện tại «does not reduce», «did not result in/lead to», «was not lower», «not effective», «were/is not
    # superior», «not non-inferior» — đo được 35 lần K4 lọt vì các dạng này (do-nhay-dot-bien-20261114)
    r"|(?:did|does|do) not (?:significantly )?(?:reduce|improve|lower|prevent|decrease|attenuate|slow|result in|lead to)"
    r"|(?:was|were|is|are) not (?:significantly )?(?:superior|non-?inferior|lower|reduced|decreased"
    r"|associated with (?:a |an )?(?:significantly )?(?:lower|reduced|decreased|improved))"
    r"|(?:was|were|is|are) not (?:highly )?(?:effective|efficacious|beneficial)"
    r"|failed to (?:reduce|improve|show|demonstrate)"
    r"|class iii|net harm|(?:increased|caused) (?:the )?(?:risk of )?harm|stopped (?:early )?for futility"
    # 20/10/2026: cách nói CHUẨN của khuyến cáo chống trong guideline — GRADE «(strong|conditional) recommendation
    # against», «we recommend/suggest against»; USPSTF «recommends against … (D recommendation)», «harms … outweigh the
    # benefits». Đo trên 85 câu ngược chiều thật của kho toàn văn: trước bản vá K4 bắt 0/8 câu «against» và 0/3 câu USPSTF D.
    r"|(?:recommends?|suggests?|advises?) against|recommendations? against"
    r"|harms?\b[^.;]{0,120}?\boutweighs? (?:the |its )?benefits?|\(d recommendation\)|grade d recommendation"
)


# Câu «không khác biệt» về kết cục PHỤ/an toàn/phân nhóm là chuyện thường trong thử nghiệm DƯƠNG
# tính — không phải tín hiệu ngược chiều của khuyến cáo. Bỏ qua trừ khi câu cũng nói tới kết cục
# CHÍNH; «not recommended»/«Class III»/«should not» thì KHÔNG BAO GIỜ bỏ qua.
# 14/11/2026: «secondary» CHỈ khi là kết cục phụ — trước đây «secondary analysis»/«secondary prevention» (thiết kế, quần thể)
# cũng làm câu bị bỏ qua (3 lần K4 lọt).
_PHU = re.compile(r"secondary (?:(?:efficacy |safety |key )?(?:end ?points?|outcomes?|measures?|composite)|analyses of (?:the )?"
                  r"secondary)|key secondary|exploratory|subgroup|post[ -]?hoc|adverse events?|serious adverse|safety"
                  r"|tolerab|discontinuation")
_CHINH = re.compile(r"primary (?:end ?point|outcome|composite)")
_LUON_BAO = re.compile(r"not recommended|should not be|class iii|net harm|futility|against|outweighs? (?:the |its )?benefit"
                       r"|d recommendation")

# Mục mà CHÍNH NÓ là khuyến cáo phủ định («KHÔNG tầm soát…», «Tránh…», «Ngừng…») thì tín hiệu ngược chiều của nguồn là
# CÙNG chiều với mục — không phải lỗi (bộ vàng 20/10: USPSTF «recommends against screening» ↔ mục «KHÔNG tầm soát»).
# «Bỏ thuốc lá» là khuyến cáo NÊN làm ⇒ không tính «bỏ»; «không chỉ/không những…» là câu khẳng định.
_MUC_PHU_DINH = re.compile(r"^\W*(?:không(?!\s+(?:chỉ|những)(?!\w))|tránh|ngừng|chống chỉ định)(?!\w)", re.I)


def muc_phu_dinh(it: dict) -> bool:
    """Tiêu đề hoặc hành động của mục MỞ ĐẦU bằng phủ định ⇒ mục là khuyến cáo chống/ngừng."""
    return any(_MUC_PHU_DINH.match(str(it.get(k) or "")) for k in ("title", "action"))


# Mệnh đề GIẢ ĐỊNH/ĐIỀU KIỆN đứng TRƯỚC tín hiệu ngược chiều («if a liberal policy does not improve…», «patients in whom
# education is not effective should…», «PDT was recommended when CBT was not effective») — không phải kết luận ngược chiều.
# Đo 14/11/2026: 5/7 báo động K4 MỚI trên mục thật sau khi mở rộng từ vựng thuộc dạng này. «when compared» không phải điều kiện.
_GIA_DINH_TRUOC = re.compile(r"(?<!\w)(?:if|whether|unless|in whom|in those whom|when(?! compared))(?!\w)")


def _nguoc_sau_gia_dinh(c: str) -> bool:
    """Mọi lần khớp _NGUOC trong câu đều đứng SAU một dấu giả định/điều kiện ⇒ câu chỉ nêu tình huống giả định."""
    ds = list(_NGUOC.finditer(c))
    return bool(ds) and all(_GIA_DINH_TRUOC.search(c, 0, m.start()) for m in ds)


def kiem_chieu_chi_tiet(nguon: str) -> tuple[list[str], list[str]]:
    """(câu ngược chiều cần đọc lại, câu đã bỏ qua vì chỉ về kết cục phụ/an toàn hoặc chỉ là mệnh đề giả định) — tối đa 3
    mỗi loại. «not recommended»/«Class III»/«against»… (_LUON_BAO) thì KHÔNG BAO GIỜ bỏ qua."""
    cau = re.split(r"(?<=[.;])\s+", nguon)
    bao: list[str] = []
    bo: list[str] = []
    for c in cau:
        c = c.strip()
        if not _NGUOC.search(c):
            continue
        luon = _LUON_BAO.search(c)
        if not luon and ((_PHU.search(c) and not _CHINH.search(c)) or _nguoc_sau_gia_dinh(c)):
            bo.append(c)
        else:
            bao.append(c)
    return bao[:3], bo[:3]


def kiem_chieu(nguon: str) -> list[str]:
    """Các câu nguồn chứa tín hiệu ngược chiều (nguyên văn đã chuẩn hoá, tối đa 3)."""
    return kiem_chieu_chi_tiet(nguon)[0]


# ── Câu nguồn: tách câu + phần KẾT LUẬN (dùng chung cho K3b/K4b, 14/11/2026) ──────────────────────
_KET_LUAN = re.compile(r"(?:conclusions?|interpretation|recommendations?|implications for practice)\s*:")


def tach_cau(t: str) -> list[str]:
    return [c.strip() for c in re.split(r"(?<=[.;])\s+", t or "") if c.strip()]


def phan_ket_luan(nguon: str) -> str:
    """Phần sau nhãn Kết luận/Interpretation CUỐI cùng của thân tóm tắt; không có nhãn ⇒ cả thân."""
    m = None
    for m in _KET_LUAN.finditer(nguon):
        pass
    return nguon[m.end():] if m else nguon


# ── K4b: MỤC nói «KHÔNG làm» trong khi NGUỒN ủng hộ (14/11/2026) ─────────────────────────────────
# K4 chỉ tìm tín hiệu ngược chiều ở NGUỒN; mục nói «không làm» còn được coi là cùng chiều nguồn ⇒ đột biến «mục đảo sang
# KHÔNG làm khi nguồn ủng hộ» lọt 582/582 (do-nhay-dot-bien-20261114). K4b: mục là khuyến cáo phủ định THẬT VÀ phần Kết luận
# của nguồn (không có nhãn ⇒ cả thân) có câu ủng hộ rõ VÀ không có câu chống/hại nào ⇒ 🟠. Có câu chống/hại ⇒ ✓ (cùng chiều).
# Không có câu ủng hộ lẫn chống ⇒ ⚪ (không phán được — thường gặp ở tóm tắt guideline chỉ mô tả phạm vi).
# «Không» + từ mô tả/phủ định kép KHÔNG phải khuyến cáo chống: «KHÔNG từ chối SGLT2i…» (= nên dùng), «Không dung nạp NSAID: …»
# (= người không dung nạp), «KHÔNG khuyên kiêng sữa» (= nên giữ).
_PHU_DINH_KEP = re.compile(r"^\W*không\s+(?:nên\s+)?(?:bỏ|từ chối|ngừng|dừng|trì hoãn|hoãn|né|chờ|đợi|ngại|bỏ qua|quên|kiêng"
                           r"|khuyên (?:kiêng|tránh|ngừng|bỏ)|dung nạp|đáp ứng|triệu chứng|đái tháo đường|mang thai|lọc máu"
                           r"|có triệu chứng)(?!\w)", re.I)
_UNG_HO = re.compile(
    r"(?<!not )(?<!no )(?<!\w)(?:significantly |substantially |markedly )?(?:reduced|lowered|decreased|improved|prevented"
    r"|slowed|attenuated)(?!\w)(?! (?:ejection|left|renal|kidney|egfr|glomerular|bone|function|lung|exercise|dose|doses"
    r"|sodium|salt|calorie|fat|intensity|frequency|gfr|cardiac|hepatic|mobility)(?!\w))"
    r"|(?<!not )(?<!\w)(?:reduces|lowers|decreases|improves|prevents|slows)(?!\w)"
    r"|(?<!\w)(?:is|are|be) (?:strongly |conditionally )?recommended"
    r"|(?<!\w)(?:we|panel|guideline|uspstf|task force|who|nice|committee|acp|ada|gina) (?:strongly )?(?:recommends?|suggests?)"
    r"(?! against)"
    r"|(?<!\w)(?:was|were|is|are) (?:superior|non-?inferior) to"
    r"|(?<!\w)(?:was|were|is|are) associated with (?:a |an )?(?:significantly )?(?:lower|reduced|decreased)"
    r"|(?<!\w)(?:resulted in|led to) (?:a |an )?(?:significantly )?(?:lower|reduced|fewer)"
    r"|(?<!\w)(?:is|was|are|were|remains?) (?:highly |an )?(?:effective|efficacious|beneficial)"
    r"|(?<!\w)(?:showed|demonstrated|provided|conferred|offers?|has|have) (?:a |significant |clinical |substantial )?"
    r"(?:net )?benefits?"
    r"|(?<!\w)should (?:be (?:used|offered|given|prescribed|considered|initiated|started|screened)|receive)"
    r"|(?<!\w)(?:is|are) indicated|(?<!\w)first-line|(?<!\w)reduc\w* (?:the )?(?:risk|incidence|rates?|mortality|hospitali\w*)")
# Câu chống/hại — RỘNG có chủ ý (thà ✓ còn hơn báo động giả): ngoài _NGUOC còn «avoid», «discontinue», «deprescribe»,
# «contraindicated», «increased risk of», «harm», «inappropriate», «overuse», «low-value», «unnecessary».
# «benefits and harms» (khuôn USPSTF «balance of benefits and harms») là câu mô tả phương pháp, không phải câu chống.
_CHONG = re.compile(r"(?<!\w)(?:avoid\w*|discontinu\w*|deprescrib\w*|withdraw\w*|contraindicat\w*|inappropriate\w*|overuse"
                    r"|overdiagnos\w*|overtreat\w*|low[- ]value|unnecessary|(?<!benefits and )(?<!benefit and )harms?|harmful"
                    r"|(?:increased|higher|excess) (?:the )?risks? of|no longer recommended|should not|must not|do not|don't)(?!\w)")


def muc_phu_dinh_that(it: dict) -> bool:
    """Mục là khuyến cáo «KHÔNG làm» thật: tiêu đề/hành động mở đầu bằng phủ định, không phải phủ định kép hay từ mô tả."""
    return any(_MUC_PHU_DINH.match(v) and not _PHU_DINH_KEP.match(v)
               for v in (str(it.get(k) or "") for k in ("title", "action")))


def kiem_k4b(it: dict, nguon: str) -> dict | None:
    """None khi mục không phải khuyến cáo «KHÔNG làm». Nguồn đã chuẩn hoá (thân tóm tắt)."""
    if not muc_phu_dinh_that(it):
        return None
    tat_ca = tach_cau(nguon)
    cau = tat_ca[:1] + tach_cau(phan_ket_luan(nguon))
    chong = [c for c in cau if _NGUOC.search(c) or _CHONG.search(c)]
    if chong:
        return {"muc": "khop", "cau_nguon": chong[:3]}
    # câu ủng hộ: ưu tiên tiêu đề + Kết luận; Kết luận im lặng thì xét cả thân (kết quả chính thường nằm ở RESULTS)
    ung_ho = [c for c in cau if _UNG_HO.search(c)] or [c for c in tat_ca if _UNG_HO.search(c)
                                                       and not (_NGUOC.search(c) or _CHONG.search(c))]
    if ung_ho:
        return {"muc": "can_doc", "cau_nguon": ung_ho[:3]}
    return {"muc": "chua_kiem", "cau_nguon": []}


# ── K3b: NGUỒN khuyến cáo CÓ ĐIỀU KIỆN mà MỤC không giữ (14/11/2026) ─────────────────────────────
# K3 chỉ so BẢN XUẤT với MỤC ⇒ cụm đã rụng NGAY TRONG MỤC thì không còn gì để so (0/602 ở do-nhay-dot-bien-20261114).
# Nguồn tiếng ANH, mục tiếng VIỆT ⇒ chỉ so được thứ ánh xạ tất định qua hai thứ tiếng. K3b xét CÂU KHUYẾN CÁO CÓ ĐIỀU KIỆN của
# nguồn (động từ khuyến cáo «recommend/suggest/should/is indicated» + dấu điều kiện «if/unless/only/when/in the absence of/
# contraindicated/in patients with…», không phải câu mô tả phạm vi tài liệu) VÀ có chung ít nhất một THUẬT NGỮ La-tinh với
# hành động của mục (tên thuốc/can thiệp/bệnh: «sglt2i», «bisphosphonate», «saba») — để chắc câu đó nói về CÙNG khuyến cáo:
#   · câu có NGƯỠNG kèm toán tử (EF/eGFR/tuổi/HbA1c/BMI/LDL) mà mục (tiêu đề + quần thể + pico.P + hành động) không nhắc chỉ
#     số đó ⇒ 🟠; nhắc đúng con số ⇒ ✓; nhắc con số khác ⇒ để K1 phán (không báo trùng);
#   · câu không có ngưỡng: hành động của mục không còn dấu điều kiện nào («nếu/khi/trừ/chỉ/ở người…/cho bệnh nhân…»,
#     ngưỡng số) ⇒ 🟠; còn ⇒ ✓ (máy không hiểu nghĩa, chỉ biết mục CÓ giữ một điều kiện).
# Không câu nào đủ ba điều kiện ⇒ K3b không phán (im). Đo 14/11 trên 663 mục thật: bản KHÔNG neo thuật ngữ báo 25 mục, bản
# đối chiếu ngưỡng/quần thể cho mọi câu báo 62 mục (gần hết là giả: «pregnancy» trong mục lục guideline, tuổi trong thang
# điểm, thời gian theo dõi) ⇒ chọn bản neo thuật ngữ (thà im còn hơn báo động giả). Mệnh đề định tính («khi đã tối ưu nền
# tảng») chỉ được nhận là «còn/không còn điều kiện», không so được nội dung — giới hạn nói trước.
_K3B_DONG_TU = re.compile(r"(?<!\w)(?:recommends?|recommended(?! (?:by|in the|for the))|suggests?|suggested|should"
                          r"|(?:is|are) indicated|advises?)(?!\w)")
_K3B_DAU = re.compile(r"(?<!\w)(?:if|unless|only|provided that|in the absence of|except|contraindicat\w*"
                      r"|when(?! compared| used| exercising)|(?:in|for|among) (?:patients|adults|people|persons|individuals"
                      r"|those|women|men|children) (?:with|who|aged|without|at|receiving|on|taking))(?!\w)")
_K3B_MO_TA = re.compile(r"this guideline|these guidelines|this update|this document|this statement|clinical judgment"
                        r"|health ?care providers? should|this report|recommendations? (?:address|cover|were)")
_K3B_DAU_VI = re.compile(r"(?<!\w)(?:nếu|khi|trừ|chỉ|ngoại trừ|miễn là|trong trường hợp|đối với|ở người|ở bệnh nhân|ở bn"
                         r"|ở phụ nữ|ở trẻ|ở nam|ở nữ|cho người|cho bệnh nhân|cho bn|cho phụ nữ|cho trẻ|với người|với bệnh nhân"
                         r"|có chỉ định|chống chỉ định|ngoài thai kỳ|trong thai kỳ|sau khi|trước khi)(?!\w)")
_K3B_THUAT_NGU_BO = {"grade", "class", "level", "item", "items", "guideline", "dashboard", "with", "from", "that", "this"}
_K3B_CHI_SO = (
    ("ef", r"lvef|ef|(?:left ventricular )?ejection fraction(?: \(lvef\)| \(ef\))?"),
    ("egfr", r"egfr|(?:estimated )?glomerular filtration rate(?: \(egfr\))?"),
    ("hba1c", r"hba1c|a1c|glycated ha?emoglobin(?: \(hba1c\))?"),
    ("bmi", r"bmi|body mass index(?: \(bmi\))?"),
    ("ldl", r"ldl-c|ldl cholesterol|ldl|low-density lipoprotein cholesterol(?: \(ldl-c\))?"),
)
_K3B_SO = r"(\d+(?:\.\d+)?)"
_K3B_DEM = r"(?:of |is |are |was |were |level of |levels? |value of )?"
_K3B_TOAN_TU = (_K3B_DEM + r"(?:>=|<=|<|>|=<|=>|at least|of at least|less than|greater than|"
                r"more than|above|below|under|over|lower than|higher than)\s*")
# Tuổi chỉ khi có NGỮ CẢNH tuổi («aged», «years of age», «or older») — «> 3 years» trần thường là thời gian theo dõi.
_K3B_TUOI = (
    re.compile(rf"(?<!\w)(?:aged?|age of) (?:>=|<=|<|>|at least|over|under|older than|younger than|less than|greater than)\s*"
               rf"{_K3B_SO}(?!\d)"),
    re.compile(rf"(?<![\d.]){_K3B_SO} (?:years?|yrs?)(?: of age| old)? (?:or|and) (?:older|over|above|younger)"),
    re.compile(rf"(?<!\w)(?:older|younger) than {_K3B_SO}(?!\d)"),
)


def trich_nguong_nguon(cau: str) -> list[tuple[str, str]]:
    """[(khoá, con số)] — ngưỡng CÓ TOÁN TỬ trong một câu nguồn đã chuẩn hoá (khoảng «25 to 75», giá trị nền «mean eGFR 43»
    không tính: không phải điều kiện)."""
    ra: list[tuple[str, str]] = []

    def them(khoa: str, so: str) -> None:
        so = so[:-2] if so.endswith(".0") else so
        if (khoa, so) not in ra:
            ra.append((khoa, so))

    for khoa, mau in _K3B_CHI_SO:
        for m in re.finditer(rf"(?<!\w)(?:{mau})(?!\w)\s*{_K3B_TOAN_TU}{_K3B_SO}(?![\d])", cau):
            them(khoa, m.group(1))
        for m in re.finditer(rf"(?<!\w)(?:{mau})(?!\w)\s*{_K3B_DEM}{_K3B_SO}\s*%?\s*(?:ml/min\S*\s*)?or (?:more|higher|"
                             rf"greater|less|lower|above|below)", cau):
            them(khoa, m.group(1))
    for mau in _K3B_TUOI:
        for m in mau.finditer(cau):
            them("tuoi", m.group(1))
    return ra


def thuat_ngu_la_tinh(van_ban: str) -> set[str]:
    """Từ La-tinh ≥ 4 ký tự trong văn bản tiếng Việt (tên thuốc, can thiệp, viết tắt bệnh) — dùng để NEO câu nguồn."""
    t = chuan_hoa(van_ban)
    return {w for w in re.findall(r"(?<![\w-])[a-z][a-z0-9-]{3,}(?![\w-])", t) if w.isascii() and w not in _K3B_THUAT_NGU_BO}


def cau_khuyen_cao_co_dieu_kien(nguon: str, thuat_ngu: set[str]) -> list[str]:
    """Câu nguồn có động từ khuyến cáo + dấu điều kiện, không mô tả phạm vi tài liệu, có chung thuật ngữ với mục."""
    ra = []
    for c in tach_cau(nguon):
        if not (_K3B_DONG_TU.search(c) and _K3B_DAU.search(c)) or _K3B_MO_TA.search(c):
            continue
        if any(re.search(rf"(?<![\w-]){re.escape(w)}(?![\w-])", c) for w in thuat_ngu):
            ra.append(c)
    return ra


def _co_chi_so_muc(khoa: str, muc: str) -> bool:
    mau = r"tuổi|age[ds]?|người già" if khoa == "tuoi" else next(m for k, m, _ in _CHI_SO if k == khoa)
    return re.search(rf"(?<!\w)(?:{mau})(?!\w)", muc) is not None


def hanh_dong_co_dieu_kien(action: str) -> bool:
    """Hành động còn ít nhất một dấu điều kiện: cụm K3, dấu tiếng Việt mở rộng, hoặc ngưỡng số."""
    a = chuan_hoa(action)
    return bool(_K3.trich_cum_dieu_kien(action) or _K3B_DAU_VI.search(a) or trich_nguong(a))


def kiem_k3b(it: dict, nguon: str) -> list[dict]:
    """Mỗi phần tử: {loai: nguong|menh_de, dieu_kien, muc: khop|can_doc, doan_nguon}. Nguồn đã chuẩn hoá (thân tóm tắt).
    Rỗng = K3b không phán (không có câu khuyến cáo có điều kiện nói về cùng thuật ngữ)."""
    action = str(it.get("action") or "")
    cau = cau_khuyen_cao_co_dieu_kien(nguon, thuat_ngu_la_tinh(action))[:3]
    if not cau:
        return []
    pham_vi = chuan_hoa(f"{it.get('title') or ''}. {_van_ban_muc(it)}. {action}")
    nguong_muc = set(trich_nguong(pham_vi))
    co_dk = hanh_dong_co_dieu_kien(action)
    ra: list[dict] = []
    for c in cau:
        doan = c[:240]
        ng = trich_nguong_nguon(c)
        for khoa, so in ng:
            if (khoa, so) in nguong_muc:
                ra.append({"loai": "nguong", "dieu_kien": f"{khoa} {so}", "muc": "khop", "doan_nguon": doan})
            elif not _co_chi_so_muc(khoa, pham_vi):
                ra.append({"loai": "nguong", "dieu_kien": f"{khoa} {so}", "muc": "can_doc", "doan_nguon": doan})
        if not ng and not any(x["loai"] == "menh_de" for x in ra):
            ra.append({"loai": "menh_de", "dieu_kien": "mệnh đề điều kiện", "muc": "khop" if co_dk else "can_doc",
                       "doan_nguon": doan})
    return ra



# ── K2: cỡ mẫu n= (25/09/2026) ──────────────────────────────────────────────────
# Mục ghi «n=4744» / «n = 8,474» ⇒ con số đó có trong nguồn không (chấp nhận dấu tách nghìn).
_MAU_N_MUC = re.compile(r"(?<!\w)n\s*=\s*(\d{1,3}(?:[.,\s]\d{3})+|\d+)(?!\d)")
_MAU_N_NGUON = re.compile(
    r"(?:(?<!\w)n\s*=\s*\d[\d.,]*|(?<![\d.,])\d{1,3}(?:[,\s]\d{3})+|(?<![\d.,])\d{3,}(?![\d.,]))"
    r"(?:\s+(?:patients|participants|adults|subjects|persons|people|women|men|children|individuals))?")


def trich_co_mau(van_ban: str) -> list[str]:
    """Các cỡ mẫu `n=` trong văn bản MỤC (đã chuẩn hoá), dạng chữ số trần: «8,474» → «8474»."""
    ra: list[str] = []
    for m in _MAU_N_MUC.finditer(van_ban):
        so = re.sub(r"[.,\s]", "", m.group(1))
        if so not in ra:
            ra.append(so)
    return ra


def _mau_so(so: str) -> re.Pattern:
    """«8474» khớp «8474», «8,474», «8 474», «8.474» — không khớp «18474» hay «84740»."""
    nhom = []
    dau = len(so) % 3 or 3
    nhom.append(so[:dau])
    nhom += [so[i:i + 3] for i in range(dau, len(so), 3)]
    return re.compile(r"(?<![\d.,])" + r"[.,\s]?".join(nhom) + r"(?![\d]|[.,]\d)")


def kiem_co_mau(so: str, nguon: str) -> tuple[str, str]:
    """(mức, đoạn nguồn). ✓ con số có trong nguồn · 🟠 nguồn có nêu cỡ mẫu khác · ⚪ nguồn không nêu số nào."""
    m = _mau_so(so).search(nguon)
    if m:
        return "khop", _doan(nguon, m.start(), m.end())
    for m2 in _MAU_N_NGUON.finditer(nguon):
        if re.search(r"patients|participants|adults|subjects|persons|people|women|men|children|individuals|n\s*=",
                     m2.group(0)):
            return "can_doc", _doan(nguon, m2.start(), m2.end())
    return "chua_kiem", ""


# ── Nguồn ──────────────────────────────────────────────────────────────────────
def _khoa_nguon(it: dict) -> list[str]:
    return [str(x).strip() for x in (it.get("pmid"), it.get("doi")) if x and str(x).strip()]


def nap_nguon_json(p: str | None) -> dict[str, str]:
    if not p:
        return {}
    try:
        raw = json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    ra = {}
    for k, v in (raw.items() if isinstance(raw, dict) else []):
        if isinstance(v, dict):
            ra[str(k).strip()] = f"{v.get('title') or ''}. {v.get('abstract') or ''}"
        elif isinstance(v, str):
            ra[str(k).strip()] = v
    return ra


def _tai_online(pmid: str) -> str | None:
    if not pmid.isdigit():
        return None
    try:
        return _nap("_ksl_kqtc", "kiem_so_lieu.py").lay_tom_tat(pmid)
    except Exception:   # noqa: BLE001 — lỗi tải = ⚪ chưa kiểm, không làm chết cả lượt
        return None


def _van_ban_muc(it: dict) -> str:
    p = it.get("population") or ""
    pico = it.get("pico")
    if isinstance(pico, dict) and isinstance(pico.get("P"), str) and pico["P"] not in ("match", "partial", "mismatch"):
        p = f"{p}. {pico['P']}"
    return p


def kiem_muc(it: dict, nguon_tho: str | None) -> dict:
    muc_tx = chuan_hoa(_van_ban_muc(it))
    dong = {"id": it.get("id") or "?", "pmid": it.get("pmid"), "doi": it.get("doi"),
            "co_nguon": nguon_tho is not None, "k1_nguong": [], "k1_cap": [], "k2_co_mau": [], "k4": None,
            "k3b": [], "k4b": None}
    if nguon_tho is None:
        return dong
    ng = chuan_hoa_nguon(than_nguon(nguon_tho))
    for khoa, so in trich_nguong(muc_tx):
        muc, doan = kiem_nguong(khoa, so, ng)
        dong["k1_nguong"].append({"chi_so": khoa, "so": so, "muc": muc, "doan_nguon": doan})
    dong["k1_cap"] = kiem_cap(muc_tx, ng)
    for so in trich_co_mau(chuan_hoa(f"{_van_ban_muc(it)}. {it.get('title') or ''}")):
        muc, doan = kiem_co_mau(so, ng)
        dong["k2_co_mau"].append({"so": so, "muc": muc, "doan_nguon": doan})
    dong["k3b"] = kiem_k3b(it, ng)
    dong["k4b"] = kiem_k4b(it, ng)
    tin_hieu, bo_qua = kiem_chieu_chi_tiet(ng)
    if tin_hieu and muc_phu_dinh(it):
        # mục và nguồn cùng nói «không làm» ⇒ khớp; câu nguồn giữ ở cau_bo_qua để người đọc vẫn thấy
        dong["k4"] = {"muc": "khop", "cau_nguon": [], "cau_bo_qua": tin_hieu + bo_qua, "muc_phu_dinh": True}
    else:
        dong["k4"] = {"muc": "can_doc" if tin_hieu else "khop", "cau_nguon": tin_hieu, "cau_bo_qua": bo_qua}
    return dong


def kiem_dashboard(data: dict, nguon: dict[str, str], online: bool) -> dict:
    ra = []
    for it in data.get("items") or []:
        if not (isinstance(it, dict) and it.get("decision") == "apply" and _khoa_nguon(it)):
            continue
        tx = next((nguon[k] for k in _khoa_nguon(it) if k in nguon), None)
        if tx is None and online and it.get("pmid"):
            tx = _tai_online(str(it["pmid"]).strip())
        ra.append(kiem_muc(it, tx))
    dem = {"khop": 0, "can_doc": 0, "chua_kiem": 0}
    dem_phep = {p: {"khop": 0, "can_doc": 0, "chua_kiem": 0} for p in PHEP_KQTC}
    for d in ra:
        if not d["co_nguon"]:
            dem["chua_kiem"] += 1
            continue
        for p, ds in phan_quyet_theo_phep(d).items():
            for x in ds:
                dem[x["muc"]] += 1
                dem_phep[p][x["muc"]] += 1
    return {"muc": ra, "dem": dem, "dem_theo_phep": dem_phep, "so_muc_co_nguon": sum(d["co_nguon"] for d in ra)}


PHEP_KQTC = ("K1", "K2", "K3b", "K4", "K4b")


def phan_quyet_theo_phep(d: dict) -> dict[str, list[dict]]:
    """Các dòng phán quyết của MỘT mục, theo phép (audit/16: phần ngưỡng của K2 nằm trong K1 — ở đây ngưỡng tính cho K1).
    K3b/K4b (14/11/2026) đếm riêng để người đọc và bộ đo độ nhạy tách được."""
    return {"K1": d["k1_nguong"] + d["k1_cap"], "K2": d["k2_co_mau"], "K3b": d.get("k3b") or [],
            "K4": [d["k4"]] if d.get("k4") else [], "K4b": [d["k4b"]] if d.get("k4b") else []}


_KH = {"khop": "✓", "can_doc": "🟠", "chua_kiem": "⚪"}


def in_bao_cao(ten: str, kq: dict) -> None:
    print(f"K1 quần thể + K2 cỡ mẫu + K4 chiều khuyến cáo · {ten}")
    print(f"  mục apply có PMID/DOI: {len(kq['muc'])} · có văn bản nguồn: {kq['so_muc_co_nguon']}")
    for d in kq["muc"]:
        dinh_danh = d["pmid"] or d["doi"]
        if not d["co_nguon"]:
            print(f"  ⚪ [{d['id']}] {dinh_danh}: không có văn bản nguồn — chưa kiểm")
            continue
        for x in d["k1_nguong"]:
            print(f"  {_KH[x['muc']]} [{d['id']}] K1 {x['chi_so']} {x['so']}"
                  + (f" — nguồn: «{x['doan_nguon']}»" if x["muc"] == "can_doc" else ""))
        for x in d["k1_cap"]:
            thong = (f"mục ghi «{x['ve_muc']}», nguồn chỉ nêu «{x['ve_nguon']}»"
                     if x["muc"] == "can_doc" else f"«{x['ve_muc']}»")
            print(f"  {_KH[x['muc']]} [{d['id']}] K1 quần thể {thong}")
        for x in d["k2_co_mau"]:
            print(f"  {_KH[x['muc']]} [{d['id']}] K2 cỡ mẫu n={x['so']}"
                  + (f" — nguồn: «{x['doan_nguon']}»" if x["muc"] == "can_doc" else ""))
        k4 = d["k4"]
        if k4["muc"] == "can_doc":
            for c in k4["cau_nguon"]:
                print(f"  🟠 [{d['id']}] K4 tín hiệu ngược chiều trong nguồn: «{c[:200]}»")
        else:
            print(f"  ✓ [{d['id']}] K4 không thấy tín hiệu ngược chiều rõ ràng"
                  + (f" (bỏ qua {len(k4['cau_bo_qua'])} câu chỉ về kết cục phụ/an toàn)" if k4["cau_bo_qua"] else ""))
        for x in d.get("k3b") or []:
            if x["muc"] != "can_doc":
                continue
            if x["loai"] == "nguong":
                print(f"  🟠 [{d['id']}] K3b nguồn khuyến cáo kèm ngưỡng «{x['dieu_kien']}» mà mục không nhắc chỉ số đó — "
                      f"nguồn: «{x['doan_nguon'][:200]}»")
            else:
                print(f"  🟠 [{d['id']}] K3b nguồn khuyến cáo CÓ ĐIỀU KIỆN, hành động của mục không còn dấu điều kiện nào — "
                      f"nguồn: «{x['doan_nguon'][:200]}»")
        k4b = d.get("k4b")
        if k4b and k4b["muc"] == "can_doc":
            for c in k4b["cau_nguon"]:
                print(f"  🟠 [{d['id']}] K4b mục nói KHÔNG làm, nguồn có câu ủng hộ (không câu chống/hại nào): «{c[:200]}»")
        elif k4b and k4b["muc"] == "chua_kiem":
            print(f"  ⚪ [{d['id']}] K4b mục nói KHÔNG làm, nguồn không có câu ủng hộ lẫn chống rõ ràng — chưa phán được")
    e = kq["dem"]
    ep = kq.get("dem_theo_phep") or {}
    theo = " · ".join(f"{p} {ep[p]['can_doc']}" for p in PHEP_KQTC if p in ep)
    print(f"Tổng: {e['khop']} ✓ khớp · {e['can_doc']} 🟠 cần đọc lại · {e['chua_kiem']} ⚪ chưa kiểm"
          + (f" (🟠 theo phép: {theo})" if theo else ""))
    if e["can_doc"]:
        print("🟠 = cần ĐỌC LẠI nguồn gốc, KHÔNG phải kết luận «sai». K4 hay báo cả kết cục phụ "
              "«không khác biệt» trong thử nghiệm dương tính. Công cụ chỉ cảnh báo.")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="K1 quần thể + K4 chiều khuyến cáo (chỉ cảnh báo)")
    ap.add_argument("dashboard", help="WebDashboard_*.html")
    ap.add_argument("--nguon-json", help='{"<pmid|doi>": {"title": "...", "abstract": "..."}}')
    ap.add_argument("--online", action="store_true", help="tải tóm tắt PubMed cho PMID còn thiếu")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    dash = Path(a.dashboard)
    data = doc_data(dash)
    if data is None:
        print(f"⚪ Không đọc được khối DATA của {dash} — không đo được.")
        return 2
    kq = kiem_dashboard(data, nap_nguon_json(a.nguon_json), a.online)
    kq["dashboard"] = str(dash)
    if a.json:
        print(json.dumps(kq, ensure_ascii=False, indent=2))
    else:
        in_bao_cao(dash.name, kq)
    if not kq["so_muc_co_nguon"]:
        return 2
    return 1 if kq["dem"]["can_doc"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
