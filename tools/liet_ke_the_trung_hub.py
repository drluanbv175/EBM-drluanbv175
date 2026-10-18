#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LIỆT KÊ THẺ TRÙNG TRONG SỔ CÁI HUB — cụm thẻ CÙNG khoá chống trùng + TRÙNG tiêu đề (18/10/2026).

VÌ SAO CÓ
=========
Sổ cái `EBM_MASTER/EBM_MASTER.json` có nhiều thẻ giống hệt tiêu đề, cùng DOI/PMID (vd «Dự phòng
TIÊN PHÁT đột quỵ» EVID-2026-0274/0366/0375/0422/0432/0486/0495), mỗi thẻ ghi history «cùng DOI/PMID
với thẻ khác … nội dung khác biệt (topic similarity < 0.5)». Đo 18/10/2026: 77 cụm, 270 thẻ, 193 thẻ
thừa — TẤT CẢ thẻ thừa tạo ngày 13/07/2026, đúng lúc AUDIT_LOG ghi bốn lượt sync_all.py liên tiếp mỗi
lượt +59…+72 thẻ rồi +0 từ lượt thứ năm. Bản cầu nạp hồi đó chỉ so thẻ mới với MỘT thẻ cho mỗi khoá
DOI/PMID; guideline trích nhiều khuyến cáo cùng DOI nên thẻ đem so thường là khuyến cáo KHÁC ⇒ mỗi
lượt nạp lặp lại sinh thêm một bản sao. Cầu nạp hiện hành so với MỌI thẻ cùng khoá (đã vá từ 13/07;
có test chốt), nhưng phần thẻ thừa chưa ai dọn.

CÔNG CỤ NÀY CHỈ ĐỌC. Nó lập danh sách mọi cụm và ĐỀ XUẤT thẻ giữ cho từng cụm; việc loại thẻ
(`EBM_MASTER/tools/manage_ledger.py drop`) chỉ làm SAU KHI bác sĩ duyệt.

Cụm = thẻ evidence_cards có key_of (luật chống trùng của chính cầu nạp — DOI > PMID > topic) trùng
nhau VÀ tiêu đề trùng sau chuẩn hoá (NFC, không phân biệt hoa/thường, gộp khoảng trắng).

ĐỀ XUẤT GIỮ (lọc lần lượt, dừng khi còn một thẻ):
  1. thẻ đang được THAM CHIẾU ở nơi sống (implementation/EVID-*.md, quality/eval/**.json,
     EBM-Dashboards/*.json, observability/*.jsonl, EBM_MASTER/*.csv, sổ rút bài) — loại nó làm gãy
     tham chiếu; báo cáo sinh lại (clinical_runtime/*_report.json) KHÔNG tính vì nó chụp cả sổ cái;
  2. thẻ mang cập nhật có bác sĩ (history «cập nhật tại chỗ» / «bác sĩ duyệt» / «THAY NGUỒN» /
     «(quản lý)») mới nhất — loại nó là mất nội dung đã duyệt;
  3. thẻ ID nhỏ nhất (thẻ GỐC — giữ định danh và lịch sử lâu nhất). Đo 18/10/2026: thẻ gốc tháng 6
     thường thiếu vài trường practice mà bản sao 13/07 có (cầu nạp cũ chưa ghi), nhưng bản sao lại
     mang chuyên khoa auto_specialty gán NHẦM (bệnh thận/đột quỵ → «Nội tiết – Chuyển hóa») ⇒ «đầy đủ
     nhất» KHÔNG phải tiêu chí chọn; thay vào đó báo cờ `thieu_so_voi_the_loai` để bác sĩ bù trước khi
     loại (hoặc để lượt nạp nối tiếp kế tiếp tự bù trường trống).
KHÔNG đề xuất (bác sĩ chọn) khi: các thẻ trong cụm khác `decision`, hoặc HƠN MỘT thẻ đang được tham
chiếu. Cụm có nội dung lệch nhau vẫn được đề xuất nhưng gắn cờ — xem trường lệch trước khi loại.

Dùng:  python3 tools/liet_ke_the_trung_hub.py [--hub <thư mục EBM_MASTER>] [--ra <thư mục báo cáo>]
Ghi:   <ra>/THE-TRUNG-HUB_<YYYY-MM-DD>.md + .json (mặc định <hub>/AUDITS/).
Mã thoát: 0 = không có cụm · 1 = có cụm chờ bác sĩ duyệt · 2 = không đo được.
Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import importlib.util
import json
import re
import sys
import unicodedata
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
CAU_NAP = REPO / "sync" / "ebm-master-tools" / "ingest_dashboard.py"

# Nơi tham chiếu SỐNG tới mã thẻ (gốc = thư mục cha của hub). Khai TƯỜNG MINH — không quét cả cây.
NGUON_THAM_CHIEU = (
    ("implementation", "EVID-*.md"),
    ("quality/eval", "**/*.json"),
    ("EBM-Dashboards", "*.json"),
    ("observability", "*.jsonl"),
    ("EBM_MASTER", "*.csv"),
    ("EBM_MASTER", "RETRACTION_AND_CORRECTION_WATCH.jsonl"),
)
_RE_MA_THE = re.compile(r"EVID-\d{4}-\d{4,}")
_RE_CAP_NHAT_BAC_SI = re.compile(r"cập nhật tại chỗ|bác sĩ duyệt|THAY NGUỒN|bác sĩ yêu cầu|\(quản lý\)")
# Trường lệch chỉ là NHÃN (không phải nội dung khuyến cáo): chuyên khoa tự gán, tên dashboard nguồn.
TRUONG_NHE = frozenset(("specialty", "source.title", "source.agency"))


def nap_cau_nap(duong: Path = CAU_NAP):
    """Nạp cầu nạp nguồn chuẩn để dùng ĐÚNG key_of/NOI_TIEP_TRUONG của nó (không chép luật sang đây)."""
    thu_muc = str(duong.parent)
    if thu_muc not in sys.path:
        sys.path.insert(0, thu_muc)
    spec = importlib.util.spec_from_file_location("_cau_nap_liet_ke_trung", duong)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def chuan_tieu_de(s) -> str:
    return " ".join(unicodedata.normalize("NFC", str(s or "")).casefold().split())


def _so_thu_tu(card) -> int:
    m = re.search(r"(\d+)\s*$", str(card.get("id") or ""))
    return int(m.group(1)) if m else 10 ** 9


def tim_cum(cards, key_of) -> list[list[dict]]:
    """Mọi nhóm ≥2 thẻ cùng key_of + cùng tiêu đề chuẩn hoá; thẻ trong cụm xếp theo số thứ tự ID."""
    nhom = collections.defaultdict(list)
    for c in cards:
        if isinstance(c, dict):
            nhom[(key_of(c), chuan_tieu_de(c.get("topic")))].append(c)
    cum = [sorted(v, key=_so_thu_tu) for v in nhom.values() if len(v) > 1]
    return sorted(cum, key=lambda v: _so_thu_tu(v[0]))


def truong_lech(cum, cau_nap) -> list[str]:
    """Trường (đường dẫn phẳng) mà các thẻ trong cụm KHÁC nhau."""
    duong = list(cau_nap.NOI_TIEP_TRUONG) + ["references", "specialty"]
    lech = []
    for d in duong:
        gia_tri = {cau_nap._gia_tri_so_sanh(cau_nap._lay_truong(c, d)) for c in cum}
        if len(gia_tri) > 1:
            lech.append(d)
    return lech


def quet_tham_chieu(goc: Path, ids: set[str]) -> dict[str, list[str]]:
    """{mã thẻ: [tệp tham chiếu]} trong các nguồn sống đã khai."""
    ra: dict[str, set[str]] = collections.defaultdict(set)
    for thu_muc, mau in NGUON_THAM_CHIEU:
        base = goc / thu_muc
        if not base.is_dir():
            continue
        for p in base.glob(mau):
            if not p.is_file() or p.name.startswith("EBM_MASTER"):
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for ma in set(_RE_MA_THE.findall(text + " " + p.name)) & ids:
                ra[ma].add(p.relative_to(goc).as_posix())
    return {k: sorted(v) for k, v in ra.items()}


def ngay_cap_nhat_bac_si(card) -> str:
    ngay = [str(h.get("date") or "") for h in card.get("history") or []
            if isinstance(h, dict) and _RE_CAP_NHAT_BAC_SI.search(unicodedata.normalize("NFC", str(h.get("change") or "")))]
    return max(ngay) if ngay else ""


def thieu_so_voi_the_loai(giu, loai, cau_nap) -> list[str]:
    """Trường mà thẻ GIỮ đang TRỐNG trong khi ít nhất một thẻ bị loại có giá trị — loại ngay là mất
    phần nội dung đó."""
    duong = list(cau_nap.NOI_TIEP_TRUONG) + ["references"]
    return [d for d in duong
            if cau_nap._gia_tri_so_sanh(cau_nap._lay_truong(giu, d)) == ""
            and any(cau_nap._gia_tri_so_sanh(cau_nap._lay_truong(c, d)) != "" for c in loai)]


def de_xuat(cum, tham_chieu, cau_nap) -> dict:
    """Đề xuất thẻ giữ cho MỘT cụm (xem docstring đầu tệp)."""
    ids = [c.get("id") for c in cum]
    quyet_dinh = sorted({str(c.get("decision")) for c in cum})
    co_ref = [c.get("id") for c in cum if tham_chieu.get(c.get("id"))]
    ket = {"ids": ids, "giu": None, "loai": [], "can_bac_si": True, "ly_do": "", "thieu_so_voi_the_loai": []}
    if len(quyet_dinh) > 1:
        ket["ly_do"] = "các thẻ khác decision (%s) — bác sĩ chọn thẻ giữ" % " / ".join(quyet_dinh)
        return ket
    if len(co_ref) > 1:
        ket["ly_do"] = "hơn một thẻ đang được tham chiếu (%s) — bác sĩ chọn" % ", ".join(co_ref)
        return ket
    tieu_chi = (
        ("đang được tham chiếu", lambda c: 1 if tham_chieu.get(c.get("id")) else 0),
        ("mang cập nhật có bác sĩ mới nhất", ngay_cap_nhat_bac_si),
        ("ID nhỏ nhất (thẻ gốc)", lambda c: -_so_thu_tu(c)),
    )
    ung_vien = list(cum)
    da_loc = []
    for ten, ham in tieu_chi:
        tot = max(ham(c) for c in ung_vien)
        loc = [c for c in ung_vien if ham(c) == tot]
        if len(loc) < len(ung_vien):
            da_loc.append(ten)
        ung_vien = loc
        if len(ung_vien) == 1:
            break
    giu = ung_vien[0]
    bi_loai = [c for c in cum if c is not giu]
    ket.update(giu=giu.get("id"), loai=[c.get("id") for c in bi_loai], can_bac_si=False,
               ly_do=" → ".join(da_loc) or "ID nhỏ nhất (thẻ gốc)",
               thieu_so_voi_the_loai=thieu_so_voi_the_loai(giu, bi_loai, cau_nap))
    return ket


def _nguon_dashboard(card, cau_nap) -> list[str]:
    return sorted(cau_nap.card_dashboard_names(card))


def lap_bao_cao(data, cau_nap, goc: Path) -> dict:
    cards = [c for c in data.get("evidence_cards") or [] if isinstance(c, dict)]
    cum = tim_cum(cards, cau_nap.key_of)
    ids = {c.get("id") for v in cum for c in v}
    tham_chieu = quet_tham_chieu(goc, ids)
    ds = []
    for v in cum:
        dx = de_xuat(v, tham_chieu, cau_nap)
        lech = truong_lech(v, cau_nap)
        dx.update(
            tieu_de=v[0].get("topic", ""), khoa=cau_nap.key_of(v[0]), decision=v[0].get("decision"),
            truong_lech=lech,
            muc_lech=("nội dung" if any(f not in TRUONG_NHE for f in lech) else ("nhãn" if lech else "giống hệt")),
            the=[{"id": c.get("id"), "date_added": c.get("date_added"), "specialty": c.get("specialty"),
                  "dashboard": _nguon_dashboard(c, cau_nap), "tham_chieu": tham_chieu.get(c.get("id"), []),
                  "cap_nhat_bac_si": ngay_cap_nhat_bac_si(c)} for c in v],
        )
        ds.append(dx)
    thua = [c for v in cum for c in v[1:]]
    return {
        "so_the": len(cards), "so_cum": len(cum), "so_the_trong_cum": sum(len(v) for v in cum),
        "so_the_thua": len(thua),
        "the_thua_theo_ngay_tao": dict(sorted(collections.Counter(str(c.get("date_added")) for c in thua).items())),
        "cum": ds,
    }


def ghi_markdown(bc: dict, hub: Path, ngay: str) -> str:
    L = [f"# Thẻ trùng trong sổ cái hub — {ngay}", "",
         f"Sổ cái: `{(hub / 'EBM_MASTER.json').as_posix()}` · {bc['so_the']} thẻ · sinh bởi "
         "`tools/liet_ke_the_trung_hub.py` (CHỈ ĐỌC — chưa loại thẻ nào).", "",
         "## Kết quả đo", "",
         f"- **{bc['so_cum']} cụm** thẻ cùng khoá chống trùng (DOI > PMID > tiêu đề) + trùng tiêu đề; "
         f"{bc['so_the_trong_cum']} thẻ trong cụm; **{bc['so_the_thua']} thẻ thừa** nếu mỗi cụm giữ một.",
         "- Thẻ thừa theo ngày tạo: " + ", ".join(f"{k}: {v}" for k, v in bc["the_thua_theo_ngay_tao"].items()),
         f"- Đề xuất được: {sum(1 for c in bc['cum'] if not c['can_bac_si'])} cụm · "
         f"bác sĩ phải chọn: {sum(1 for c in bc['cum'] if c['can_bac_si'])} cụm · "
         f"cụm lệch NỘI DUNG: {sum(1 for c in bc['cum'] if c['muc_lech'] == 'nội dung')}.", "",
         "## Luật đề xuất thẻ giữ", "",
         "1. đang được tham chiếu ở nơi sống · 2. mang cập nhật có bác sĩ mới nhất · 3. ID nhỏ nhất "
         "(thẻ gốc). Không đề xuất khi khác `decision` hoặc >1 thẻ được tham chiếu. Thẻ giữ thiếu "
         "trường mà thẻ bị loại có ⇒ gắn ⚠ để bù trước khi loại.", "",
         "## Từng cụm", ""]
    for i, c in enumerate(bc["cum"], 1):
        co = "🔴 BÁC SĨ CHỌN" if c["can_bac_si"] else ("⚠ lệch nội dung — xem trước khi loại"
                                                     if c["muc_lech"] == "nội dung" else "✓")
        L.append(f"### {i}. {c['tieu_de'][:110]}")
        L.append("")
        L.append(f"- Khoá `{c['khoa']}` · decision `{c['decision']}` · {len(c['ids'])} thẻ · {co}")
        if c["giu"]:
            L.append(f"- **Đề xuất giữ {c['giu']}** ({c['ly_do']}); loại: {', '.join(c['loai'])}")
            if c["thieu_so_voi_the_loai"]:
                L.append(f"- ⚠ Thẻ giữ đang TRỐNG trường mà thẻ bị loại có: "
                         f"{', '.join(c['thieu_so_voi_the_loai'])} — bù trước khi loại (hoặc để lượt nạp "
                         "nối tiếp kế tiếp tự bù trường trống).")
        else:
            L.append(f"- Không đề xuất: {c['ly_do']}")
        if c["truong_lech"]:
            L.append(f"- Trường lệch giữa các thẻ ({c['muc_lech']}): {', '.join(c['truong_lech'])}")
        for t in c["the"]:
            phu = []
            if t["tham_chieu"]:
                phu.append("tham chiếu: " + ", ".join(t["tham_chieu"]))
            if t["cap_nhat_bac_si"]:
                phu.append("cập nhật có bác sĩ " + t["cap_nhat_bac_si"])
            L.append(f"  - `{t['id']}` · tạo {t['date_added']} · {t['specialty'] or '—'} · "
                     f"{', '.join(t['dashboard']) or '(không rõ dashboard)'}" + (" · " + " · ".join(phu) if phu else ""))
        L.append("")
    lenh = [f'python3 tools/manage_ledger.py drop {i} "thẻ trùng cụm — giữ {c["giu"]} (bác sĩ duyệt {ngay})"'
            for c in bc["cum"] if c["giu"] for i in c["loai"]]
    L += ["## Lệnh loại thẻ — CHỈ chạy sau khi bác sĩ duyệt từng cụm", "",
          f"Chạy trong `EBM_MASTER/`. {len(lenh)} lệnh; mỗi lệnh `drop` sao lưu TRỌN sổ cái (~"
          f"{(hub / 'EBM_MASTER.json').stat().st_size // 1_000_000 if (hub / 'EBM_MASTER.json').is_file() else '?'} MB) "
          "vào BACKUPS/ — chạy hết sẽ phình BACKUPS đáng kể trên OneDrive.", "", "```bash", *lenh, "```", "",
          "Cần bác sĩ kiểm chứng."]
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Liệt kê cụm thẻ trùng trong sổ cái hub (chỉ đọc)")
    ap.add_argument("--hub", default=None, help="thư mục EBM_MASTER (mặc định: dò cạnh repo)")
    ap.add_argument("--ra", default=None, help="thư mục ghi báo cáo (mặc định <hub>/AUDITS/)")
    ap.add_argument("--ngay", default=None, help="ngày ghi trên báo cáo/tên tệp (YYYY-MM-DD)")
    args = ap.parse_args()

    if args.hub:
        hub = Path(args.hub).resolve()
    else:
        spec = importlib.util.spec_from_file_location("_bst_liet_ke", REPO / "tools" / "ban_sao_tran.py")
        bst = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bst)
        hub = bst.duong_goc("EBM_MASTER", REPO)
    if hub is None or not (Path(hub) / "EBM_MASTER.json").is_file():
        print("⚪ Không thấy EBM_MASTER/EBM_MASTER.json — KHÔNG ĐO ĐƯỢC (truyền --hub). Không phải «không có thẻ trùng».")
        return 2
    hub = Path(hub)
    try:
        cau_nap = nap_cau_nap()
        data = json.loads((hub / "EBM_MASTER.json").read_text(encoding="utf-8"))
    except (OSError, ValueError, ImportError) as e:
        print(f"⚪ KHÔNG ĐO ĐƯỢC: {e}")
        return 2
    ngay = args.ngay or dt.date.today().isoformat()
    bc = lap_bao_cao(data, cau_nap, hub.parent)
    ra = Path(args.ra) if args.ra else hub / "AUDITS"
    ra.mkdir(parents=True, exist_ok=True)
    (ra / f"THE-TRUNG-HUB_{ngay}.json").write_text(
        json.dumps(dict(bc, ngay=ngay, hub=hub.as_posix()), ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8", newline="\n")
    (ra / f"THE-TRUNG-HUB_{ngay}.md").write_text(ghi_markdown(bc, hub, ngay), encoding="utf-8", newline="\n")
    print(f"THẺ TRÙNG SỔ CÁI HUB — {bc['so_cum']} cụm · {bc['so_the_trong_cum']} thẻ · {bc['so_the_thua']} thẻ thừa "
          f"(theo ngày tạo: {bc['the_thua_theo_ngay_tao']}).")
    print(f"  Đề xuất được {sum(1 for c in bc['cum'] if not c['can_bac_si'])} cụm · bác sĩ chọn "
          f"{sum(1 for c in bc['cum'] if c['can_bac_si'])} cụm · báo cáo: {(ra / f'THE-TRUNG-HUB_{ngay}.md').as_posix()}")
    print("  CHỈ ĐỌC — chưa loại thẻ nào. Cần bác sĩ kiểm chứng.")
    return 1 if bc["so_cum"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
