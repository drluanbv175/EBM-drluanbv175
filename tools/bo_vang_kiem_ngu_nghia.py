#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BỘ VÀNG cho kiểm chéo ngữ nghĩa mục `apply` — phiếu gắn nhãn, ghi nhãn của bác sĩ, đo báo động giả (20/10/2026).

VÌ SAO CÓ: thiết kế `audit/16` (bác sĩ duyệt 25/09/2026) đặt K1 (quần thể) · K3 (mệnh đề điều kiện) · K4 (chiều khuyến cáo) ở
mức CẢNH BÁO và «chỉ cân nhắc chuyển sang CHẶN sau khi đo tỉ lệ báo động giả trên bộ vàng», «máy soạn ứng viên, bác sĩ gắn
nhãn, máy không tự gắn nhãn». Tới 20/10/2026 bộ vàng CHƯA TỪNG được soạn ⇒ K1–K4 mãi chỉ cảnh báo. Bác sĩ: «Giải quyết 3 vấn
đề chưa đạt». Công cụ này đóng vòng: ứng viên (`kiem_cheo_ngu_nghia.py --ung-vien-bo-vang`) → PHIẾU cho bác sĩ → GHI nhãn từ
nguyên văn lời bác sĩ → ĐO.

Ba lệnh:
  phieu [--online]   — Word Times New Roman cho bác sĩ gắn nhãn: mỗi mục có quần thể, khuyến cáo, nguồn và tóm tắt PubMed.
                       CỐ Ý KHÔNG in kết quả của máy (K1/K4) — nhãn chuẩn phải độc lập, không bị máy dẫn dắt.
  ghi --loi "<nguyên văn>" [--ap-dung] [--ghi-de]
                     — ghi nhãn theo mẫu «1: Đ Đ Đ · 2: S Đ Đ quần thể sai · …» (ba chữ = quần thể · chiều · điều kiện; Đ/✓ =
                       đúng, S/✗ = sai). Chạy khô mặc định; KHÔNG ghi đè nhãn đã có trừ khi --ghi-de; lưu nguyên văn lời bác sĩ.
  do [--online]      — đo K1 so với nhãn «đúng quần thể», K4 so với nhãn «đúng chiều»: báo động giả (🟠 trên mục bác sĩ nói
                       đúng) · bỏ lọt (mục bác sĩ nói sai mà máy im). Nhãn còn trống ⇒ CHƯA ĐO (không bao giờ in 0%).
GIỚI HẠN NÓI TRƯỚC: K3 kiểm bản xuất (bản đọc/Word) có GIỮ cụm điều kiện của chính mục không — nhãn «đủ điều kiện» của bác sĩ
hỏi khác (mục có giữ đủ điều kiện của BÀI GỐC không) ⇒ K3 không đo bằng nhãn này; nhãn đó cho biết lỗi «rụng điều kiện ngay
trong mục» có xảy ra không — hiện chưa phép kiểm nào bắt.
Chuyển một phép kiểm sang CHẶN là quyết định của BÁC SĨ sau khi xem số đo — công cụ không bao giờ tự chuyển.
Mã thoát: 0 chạy xong · 1 lời bác sĩ không đọc được · 2 thiếu tệp/không đo được.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TEP_BO_VANG = REPO / "quality" / "eval" / "kiem-cheo-ngu-nghia" / "bo-vang.cho-duyet.json"
NHAN = ("dung_quan_the", "dung_chieu", "du_dieu_kien")
TEN_NHAN = {"dung_quan_the": "Quần thể của mục ĐÚNG với quần thể nghiên cứu/khuyến cáo trong nguồn",
            "dung_chieu": "Chiều khuyến cáo của mục (làm / không làm) ĐÚNG với nguồn",
            "du_dieu_kien": "Mục giữ ĐỦ mệnh đề điều kiện của nguồn (không nới rộng ra ngoài quần thể được chứng minh)"}
_DUNG = {"đ", "d", "✓", "dung", "đúng", "y", "co", "có"}
_SAI = {"s", "✗", "x", "sai", "n", "khong", "không"}


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, Path(__file__).resolve().parent / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


def goc_du_lieu(ten: str) -> Path:
    """Gốc dữ liệu ngoài git (lồng/anh em của repo); chạy từ worktree ngoài OneDrive thì đọc EBM_WORKSPACE_ROOT."""
    try:
        p = _nap("_bvk_bst", "ban_sao_tran.py").duong_goc(ten, REPO)
    except Exception:  # noqa: BLE001
        p = None
    if p is None and os.environ.get("EBM_WORKSPACE_ROOT"):
        p = Path(os.environ["EBM_WORKSPACE_ROOT"]) / ten
    return p or (REPO / ten)


def doc_bo_vang(tep: Path = TEP_BO_VANG) -> dict:
    return json.loads(tep.read_text(encoding="utf-8"))


def tep_nguon(tep: Path = TEP_BO_VANG) -> Path:
    """Tóm tắt PubMed của nguồn — để NGOÀI git (văn bản có bản quyền của nhà xuất bản, chỉ dùng nội bộ để gắn nhãn/đo)."""
    return goc_du_lieu("EBM-Dashboards") / "derivatives" / "bo-vang-ngu-nghia-nguon.json"


def nap_nguon(bv: dict, *, online: bool, tep: Path | None = None, lay=None) -> dict[str, str | None]:
    """{pmid: tóm tắt | None}. Dùng bộ đệm; --online mới tải phần thiếu (qua `kiem_so_lieu.lay_tom_tat`)."""
    tep = tep or tep_nguon()
    try:
        dem = json.loads(tep.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        dem = {}
    thieu = [str(m["pmid"]) for m in bv["muc"] if m.get("pmid") and str(m["pmid"]) not in dem]
    if online and thieu:
        lay = lay or _nap("_bvk_ksl", "kiem_so_lieu.py").lay_tom_tat
        for pm in thieu:
            dem[pm] = lay(pm)
        tep.parent.mkdir(parents=True, exist_ok=True)
        tep.write_text(json.dumps(dem, ensure_ascii=False, indent=1), encoding="utf-8")
    return {str(m["pmid"]): dem.get(str(m["pmid"])) for m in bv["muc"] if m.get("pmid")}


# ───────────────────────── phiếu gắn nhãn ─────────────────────────

_BO_DOAN = re.compile(r"^(author information|copyright|©|conflict of interest|comment in|erratum in|update of|"
                      r"doi:|pmid:|pmcid:)", re.I)


def gon_tom_tat(tt: str, tran: int = 2500) -> str:
    """Tóm tắt efetch → một đoạn gọn: bỏ khối thông tin tác giả/bản quyền/định danh, che email tác giả."""
    doan = [re.sub(r"\s+", " ", d).strip() for d in re.split(r"\n\s*\n", tt)]
    giu = [d for d in doan if d and not _BO_DOAN.match(d)]
    gon = re.sub(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", "[email]", " ¶ ".join(giu))
    return gon if len(gon) <= tran else gon[:tran] + "…"

def dung_phieu_md(bv: dict, nguon: dict[str, str | None]) -> str:
    L = ["# PHIẾU GẮN NHÃN BỘ VÀNG — KIỂM CHÉO NGỮ NGHĨA MỤC «ÁP DỤNG»", "",
         f"Ngày dựng: {dt.date.today().strftime('%d/%m/%Y')} · {len(bv['muc'])} mục do máy chọn ngẫu nhiên đều giữa các "
         "dashboard. Phiếu CỐ Ý không in nhận định của máy — bác sĩ đọc mục và nguồn rồi trả lời ba câu cho từng mục.", "",
         "**Ba câu hỏi cho mỗi mục** (trả lời Đ = đúng, S = sai):", ""]
    for i, k in enumerate(NHAN, 1):
        L.append(f"{i}. {TEN_NHAN[k]}.")
    L += ["", "**Cách trả lời trong khung chat** (một dòng mỗi mục, ghi chú tuỳ ý sau ba chữ):", "",
          "> 1: Đ Đ Đ · 2: S Đ Đ quần thể bài là HFrEF · 3: Đ Đ S thiếu «ngoài thai kỳ»", "", "---", ""]
    for i, m in enumerate(bv["muc"], 1):
        ten_dash = re.sub(r"^WebDashboard_EBM_|\.html$", "", m.get("dashboard") or "")
        L += [f"## Mục {i} — {m.get('title') or '—'}", "",
              f"**Chủ đề:** {ten_dash} · {m.get('id') or '?'}", "",
              f"**Quần thể ghi trong mục:** {m.get('population') or '—'}", "",
              f"**Khuyến cáo / hành động của mục:** {m.get('action') or '—'}", "",
              f"**Nguồn:** PMID {m.get('pmid') or '—'} · DOI {m.get('doi') or '—'}", ""]
        tt = nguon.get(str(m.get("pmid"))) if m.get("pmid") else None
        if tt:
            L += [f"**Tóm tắt nguồn (PubMed):** {gon_tom_tat(tt)}", ""]
        else:
            L += ["**Tóm tắt nguồn:** chưa tải được — bác sĩ mở PMID/DOI để đọc.", ""]
        L += ["**Trả lời:** quần thể ……  ·  chiều ……  ·  điều kiện ……  ·  ghi chú ……………………………", "", "---", ""]
    L += ["*Nhãn của bác sĩ là chuẩn vàng — máy chỉ dùng để đo, không tự gắn nhãn. Không chứa thông tin người bệnh.*"]
    return "\n".join(L)


# ───────────────────────── ghi nhãn ─────────────────────────

_TOK = "|".join(sorted((re.escape(t) for t in _DUNG | _SAI), key=len, reverse=True))
_MUC = re.compile(rf"(?<!\w)(?:mục\s*)?(\d+)\s*[:.)-]\s*({_TOK})[,.]?\s+({_TOK})[,.]?\s+({_TOK})[,.]?(?=\s|$|[·;])",
                  re.I)
# «N: …» còn sót trong ghi chú/phần đầu = một mục viết sai mẫu (vd thiếu một chữ) — phải báo, không nuốt vào ghi chú
_MUC_SOT = re.compile(r"(?:^|[·;\n\s])(?:mục\s*)?\d+\s*:\s+\S", re.I)


def doc_loi(loi: str, so_muc: int) -> tuple[dict[int, dict], list[str]]:
    """{số mục: {dung_quan_the, dung_chieu, du_dieu_kien, ghi_chu}} + danh sách phần không đọc được.

    Tìm MỌI chỗ bắt đầu một nhãn mục (kể cả khi bác sĩ không dùng dấu ngăn cách) rồi cắt lời giữa các chỗ đó —
    ghi chú chứa «2.5 mg» hay «;» không bị cắt nhầm, «1: Đ Đ Đ 2: S Đ Đ» không bị nuốt mục 2 vào ghi chú."""
    ra: dict[int, dict] = {}
    loi_doc: list[str] = []
    dau = list(_MUC.finditer(loi))
    truoc = loi[:dau[0].start()] if dau else loi
    if truoc.strip(" ·;\n\t"):
        loi_doc.append(truoc.strip())
    for i, m in enumerate(dau):
        het = dau[i + 1].start() if i + 1 < len(dau) else len(loi)
        ghi_chu = loi[m.end():het].strip(" ·;\n\t")
        so = int(m.group(1))
        if not 1 <= so <= so_muc or so in ra or _MUC_SOT.search(ghi_chu):
            loi_doc.append(loi[m.start():het].strip(" ·;\n\t"))
            continue
        gt = [m.group(k).lower() in _DUNG for k in (2, 3, 4)]
        ra[so] = {"dung_quan_the": gt[0], "dung_chieu": gt[1], "du_dieu_kien": gt[2], "ghi_chu": ghi_chu or None}
    return ra, loi_doc


def ghi_nhan(loi: str, *, ap_dung: bool, ghi_de: bool, tep: Path = TEP_BO_VANG) -> int:
    bv = doc_bo_vang(tep)
    nhan, loi_doc = doc_loi(loi, len(bv["muc"]))
    for x in loi_doc:
        print(f"✗ không đọc được: «{x}» — mẫu «N: Đ Đ Đ ghi chú»")
    if loi_doc or not nhan:
        return 1
    se_ghi, bo = [], []
    for so, nh in sorted(nhan.items()):
        cu = bv["muc"][so - 1].get("nhan_bac_si") or {}
        if any(cu.get(k) is not None for k in NHAN) and not ghi_de:
            bo.append(so)
            continue
        se_ghi.append(so)
        if ap_dung:
            bv["muc"][so - 1]["nhan_bac_si"] = {**nh, "loi_bac_si": loi.strip(), "ngay": dt.date.today().isoformat()}
    if bo:
        print(f"= bỏ qua mục {bo}: đã có nhãn (dùng --ghi-de nếu bác sĩ muốn sửa)")
    if not ap_dung:
        print(f"(chạy khô) sẽ ghi nhãn cho mục {se_ghi} — thêm --ap-dung để ghi")
        return 0
    tep.write_text(json.dumps(bv, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✓ đã ghi nhãn của bác sĩ cho {len(se_ghi)} mục → {tep}")
    return 0


# ───────────────────────── đo ─────────────────────────

def bang_nham_lan(cap: list[tuple[bool, bool]]) -> dict:
    """cap: [(máy báo 🟠, bác sĩ nói SAI)] ⇒ bảng nhầm lẫn và tỉ lệ (None khi mẫu số 0)."""
    tp = sum(1 for bao, sai in cap if bao and sai)
    fp = sum(1 for bao, sai in cap if bao and not sai)
    fn = sum(1 for bao, sai in cap if not bao and sai)
    tn = sum(1 for bao, sai in cap if not bao and not sai)
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "n": len(cap),
            "bao_dong_gia": (fp / (fp + tn)) if (fp + tn) else None,
            "bo_lot": (fn / (fn + tp)) if (fn + tp) else None}


def do(bv: dict, nguon: dict[str, str | None], kiem_muc=None) -> dict:
    """K1 so với «đúng quần thể», K4 so với «đúng chiều» — chỉ trên mục ĐÃ có nhãn và ĐÃ có tóm tắt nguồn."""
    kiem_muc = kiem_muc or _nap("_bvk_kqtc", "kiem_quan_the_chieu.py").kiem_muc
    k1, k4, chua = [], [], {"chua_nhan": 0, "chua_nguon": 0}
    for m in bv["muc"]:
        nh = m.get("nhan_bac_si") or {}
        if nh.get("dung_quan_the") is None and nh.get("dung_chieu") is None:
            chua["chua_nhan"] += 1
            continue
        tx = nguon.get(str(m.get("pmid"))) if m.get("pmid") else None
        if not tx:
            chua["chua_nguon"] += 1
            continue
        kq = kiem_muc({"id": m.get("id"), "title": m.get("title"), "population": m.get("population"),
                       "pmid": m.get("pmid"), "doi": m.get("doi")}, tx)
        if nh.get("dung_quan_the") is not None:
            bao = any(x["muc"] == "can_doc" for x in kq["k1_nguong"] + kq["k1_cap"])
            k1.append((bao, not nh["dung_quan_the"]))
        if nh.get("dung_chieu") is not None and kq.get("k4"):
            k4.append((kq["k4"]["muc"] == "can_doc", not nh["dung_chieu"]))
    dk = [(m.get("nhan_bac_si") or {}).get("du_dieu_kien") for m in bv["muc"]]
    co_nhan_dk = [x for x in dk if x is not None]
    return {"K1": bang_nham_lan(k1), "K4": bang_nham_lan(k4), "chua": chua,
            "muc_rung_dieu_kien": sum(1 for x in co_nhan_dk if x is False) if co_nhan_dk else None,
            "so_nhan_dieu_kien": len(co_nhan_dk)}


def _pt(x) -> str:
    return "CHƯA ĐO" if x is None else f"{x:.0%}"


def in_do(kq: dict) -> None:
    print("ĐO BỘ VÀNG — kiểm chéo ngữ nghĩa mục «apply» (nhãn của bác sĩ là chuẩn)")
    for k, ten in (("K1", "quần thể"), ("K4", "chiều khuyến cáo")):
        b = kq[k]
        print(f"  {k} ({ten}): {b['n']} mục có nhãn · máy bắt đúng {b['tp']} · báo động giả {b['fp']} "
              f"({_pt(b['bao_dong_gia'])}) · bỏ lọt {b['fn']} ({_pt(b['bo_lot'])})")
    c = kq["chua"]
    print(f"  Chưa đo: {c['chua_nhan']} mục chưa có nhãn bác sĩ · {c['chua_nguon']} mục chưa có tóm tắt nguồn")
    rung = kq["muc_rung_dieu_kien"]
    so_rung = "CHƯA ĐO" if rung is None else f"{rung}/{kq['so_nhan_dieu_kien']}"
    print(f"  Mục bác sĩ nói RỤNG ĐIỀU KIỆN so với bài gốc: {so_rung} — hiện CHƯA phép kiểm nào bắt lỗi này "
          "(K3 kiểm bản xuất giữ cụm điều kiện của MỤC, không so với bài gốc).")
    print("  Chuyển K1/K4 từ CẢNH BÁO sang CHẶN là quyết định của bác sĩ sau khi xem số này (audit/16 §4). "
          "Cần bác sĩ kiểm chứng.")


def main(argv: list[str] | None = None) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Bộ vàng kiểm chéo ngữ nghĩa: phiếu · ghi nhãn · đo")
    sub = ap.add_subparsers(dest="lenh", required=True)
    p = sub.add_parser("phieu")
    p.add_argument("--online", action="store_true")
    p = sub.add_parser("ghi")
    p.add_argument("--loi", required=True)
    p.add_argument("--ap-dung", action="store_true")
    p.add_argument("--ghi-de", action="store_true")
    p = sub.add_parser("do")
    p.add_argument("--online", action="store_true")
    a = ap.parse_args(argv)
    if not TEP_BO_VANG.is_file():
        print(f"⚪ chưa có {TEP_BO_VANG} — chạy `python3 tools/kiem_cheo_ngu_nghia.py --ung-vien-bo-vang` trước")
        return 2
    if a.lenh == "ghi":
        return ghi_nhan(a.loi, ap_dung=a.ap_dung, ghi_de=a.ghi_de)
    bv = doc_bo_vang()
    nguon = nap_nguon(bv, online=a.online)
    if a.lenh == "phieu":
        ra = goc_du_lieu("EBM-Dashboards") / "derivatives" / f"PHIEU-GAN-NHAN-BO-VANG_{dt.date.today():%Y%m%d}.docx"
        ra.parent.mkdir(parents=True, exist_ok=True)
        _nap("_bvk_md", "md_sang_docx_times.py").dung_docx(dung_phieu_md(bv, nguon), 12.0).save(str(ra))
        co = sum(1 for v in nguon.values() if v)
        print(f"✓ Phiếu gắn nhãn: {ra} ({len(bv['muc'])} mục · {co}/{len(nguon)} có tóm tắt nguồn)")
        return 0
    in_do(do(bv, nguon))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
