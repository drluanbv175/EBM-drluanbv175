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
  ghi --loi "<nguyên văn>" [--ap-dung] [--ghi-de] [--de-xuat-boi Claude]
                     — ghi nhãn theo mẫu «1: Đ Đ Đ · 2: S Đ Đ quần thể sai · …» (ba chữ = quần thể · chiều · điều kiện; Đ/✓ =
                       đúng, S/✗ = sai, ? = chưa đủ căn cứ). Chạy khô mặc định; KHÔNG ghi đè nhãn đã có trừ khi --ghi-de; lưu nguyên văn lời bác sĩ.
  do [--online]      — đo K1 so với nhãn «đúng quần thể», K4 so với nhãn «đúng chiều»: báo động giả (🟠 trên mục bác sĩ nói
                       đúng) · bỏ lọt (mục bác sĩ nói sai mà máy im). Nhãn còn trống ⇒ CHƯA ĐO (không bao giờ in 0%).
                       Từ 14/11/2026: K3b so với nhãn «đủ điều kiện», K4b so với «đúng chiều» (chỉ mục nói KHÔNG làm).
MỞ RỘNG 19/11/2026 (bác sĩ: «Bộ vàng này hiện chưa có. Hãy giải quyết», chọn «Kết hợp hai cách»): 20 nhãn hiện có đều
  do máy soạn sẵn, bác sĩ xác nhận, và KHÔNG mục nào sai ⇒ không đo được bỏ lọt. Thêm hai nguồn mục, tách bạch khi đo:
  duyet-dot-bien --loi "<nguyên văn>" [--ap-dung] [--ghi-de]
                     — (a) ĐỘT BIẾN CÓ KIỂM SOÁT: `dot-bien.de-xuat.json` (Claude soạn từ 16 mục gốc, mỗi biến thể sai đúng
                       MỘT trục, nhãn dự kiến theo cấu trúc phép sửa). Chỉ thành nhãn khi bác sĩ duyệt danh sách — mẫu
                       «duyệt đột biến: tất cả» / «duyệt đột biến: tất cả trừ D05, D12» / «duyệt D01-D10». Ghi vào
                       `bo-vang.dot-bien.json` kèm nguyên văn lời bác sĩ. KHÁC `do_nhay_kiem_ngu_nghia.py` (14/11): bên đó
                       là đột biến TỔNG HỢP theo khuôn, đo độ nhạy của luật cứng; bên này là lỗi do người soạn như lỗi thật,
                       bác sĩ duyệt, dùng chung cho luật cứng LẪN bộ kiểm API.
  them-muc-that [--so-muc 40] [--ap-dung]
                     — (b) MỤC THẬT PHÂN TẦNG: rút thêm mục apply có PMID từ bản ĐÃ PASS mới nhất mỗi chủ đề, theo tầng
                       phủ định · có điều kiện · nhóm đặc biệt · khác (dồn chỗ cho ca khó, nơi lỗi hay nằm), loại mục đã có.
                       Nhãn để trống — bác sĩ gắn ĐỘC LẬP qua phiếu (phần B) rồi `ghi --loi`.
  phieu              — phần A: danh sách đột biến chờ duyệt (bản gốc cạnh bản sửa, nhãn dự kiến); phần B: CHỈ mục chưa có
                       nhãn, vẫn MÙ với nhận định của máy.
  do [--api]         — tách số đo theo nguồn mục (thật · đột biến); --api đặt bộ kiểm API (`kiem_ngu_nghia_api.py`, kết
                       quả trong bộ đệm) cạnh luật cứng trên cùng các mục, theo ba trục quần thể · chiều · điều kiện.
GIỚI HẠN NÓI TRƯỚC: K3 kiểm bản xuất (bản đọc/Word) có GIỮ cụm điều kiện của chính mục không — nhãn «đủ điều kiện» của bác sĩ
hỏi khác (mục có giữ đủ điều kiện của BÀI GỐC không) ⇒ K3 không đo bằng nhãn này; nhãn đó đo K3b (14/11/2026 — so mục với
câu khuyến cáo có điều kiện của tóm tắt nguồn, chỉ phần ánh xạ được qua hai thứ tiếng).
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
TEP_DOT_BIEN_DE_XUAT = TEP_BO_VANG.parent / "dot-bien.de-xuat.json"
TEP_DOT_BIEN = TEP_BO_VANG.parent / "bo-vang.dot-bien.json"
NHAN = ("dung_quan_the", "dung_chieu", "du_dieu_kien")
# kiểu đột biến → trục bị cố ý làm sai · trường được phép sửa (trục còn lại chỉ kế thừa nhãn gốc khi trường của nó giữ nguyên)
KIEU_DOT_BIEN = {"quan_the": "dung_quan_the", "chieu": "dung_chieu", "dieu_kien": "du_dieu_kien"}
TRUONG_DUOC_SUA = {"quan_the": {"population"}, "chieu": {"title", "action"}, "dieu_kien": {"action"}}
DE_XUAT_BOI_DOT_BIEN = "đột biến có kiểm soát (Claude soạn) — bác sĩ duyệt danh sách"
TANG = ("phu_dinh", "dieu_kien", "dac_biet", "khac")
TEN_TANG = {"phu_dinh": "khuyến cáo KHÔNG làm", "dieu_kien": "hành động có điều kiện",
            "dac_biet": "nhóm đặc biệt / ngưỡng", "khac": "khác"}
HAN_NGACH_TANG = {"phu_dinh": 10, "dieu_kien": 12, "dac_biet": 12, "khac": 6}   # trên 40 mục; tầng thiếu thì dồn sang tầng sau
TEN_NHAN = {"dung_quan_the": "Quần thể của mục ĐÚNG với quần thể nghiên cứu/khuyến cáo trong nguồn",
            "dung_chieu": "Chiều khuyến cáo của mục (làm / không làm) ĐÚNG với nguồn",
            "du_dieu_kien": "Mục giữ ĐỦ mệnh đề điều kiện của nguồn (không nới rộng ra ngoài quần thể được chứng minh)"}
_DUNG = {"đ", "d", "✓", "dung", "đúng", "y", "co", "có"}
_SAI = {"s", "✗", "x", "sai", "n", "khong", "không"}
_CHUA_RO = {"?"}  # bác sĩ chưa đủ căn cứ cho trục đó (vd cần toàn văn) ⇒ để trống trục, không ép Đ/S


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

def _co_nhan(m: dict) -> bool:
    return any((m.get("nhan_bac_si") or {}).get(k) is not None for k in NHAN)


def _ky_hieu(v) -> str:
    return "—" if v is None else ("Đ" if v else "S")


def _phan_a(bv: dict, cho_duyet: list[dict]) -> list[str]:
    """Phần A: đột biến chờ duyệt — bản gốc cạnh bản sửa + nhãn dự kiến. Không có kết quả phép kiểm nào của máy."""
    L = ["# PHẦN A — DUYỆT DANH SÁCH ĐỘT BIẾN CÓ KIỂM SOÁT", "",
         f"{len(cho_duyet)} biến thể do Claude soạn từ các mục gốc đã có nhãn. Mỗi biến thể cố ý làm SAI đúng một trục "
         "(quần thể · chiều khuyến cáo · điều kiện); nhãn dự kiến suy ra từ phép sửa. Bác sĩ chỉ cần xác nhận biến thể "
         "đó THẬT SỰ sai như mô tả — biến thể nào chưa chắc thì loại.", "",
         "**Cách trả lời trong khung chat:**", "",
         "> duyệt đột biến: tất cả  ·  hoặc  ·  duyệt đột biến: tất cả trừ D05, D12", "",
         "Nhãn dự kiến ghi theo thứ tự quần thể · chiều · điều kiện (Đ đúng, S sai, — máy không khẳng định).", "", "---", ""]
    ten_kieu = {"quan_the": "sai QUẦN THỂ", "chieu": "sai CHIỀU khuyến cáo", "dieu_kien": "rụng ĐIỀU KIỆN"}
    ten_truong = {"title": "Tiêu đề", "population": "Quần thể", "action": "Hành động"}
    for x in cho_duyet:
        goc = bv["muc"][x["tu_muc"] - 1]
        nh = x.get("nhan_du_kien") or {}
        L += [f"## {x['ma']} — từ mục {x['tu_muc']}: {goc.get('title') or '—'}", "",
              f"**Kiểu lỗi:** {ten_kieu.get(x['kieu'], x['kieu'])} — {x.get('mo_ta') or ''}", "",
              f"**Nguồn của mục gốc:** PMID {goc.get('pmid') or '—'}", ""]
        for k in ("title", "population", "action"):
            if k in (x.get("sua") or {}):
                L += [f"- {ten_truong[k]} GỐC: {goc.get(k) or '—'}", f"- {ten_truong[k]} ĐỘT BIẾN: {x['sua'][k]}"]
        L += ["", f"**Nhãn dự kiến:** {' · '.join(_ky_hieu(nh.get(k)) for k in NHAN)}", "", "---", ""]
    return L


def dung_phieu_md(bv: dict, nguon: dict[str, str | None], cho_duyet: list[dict] | None = None) -> str:
    """Phiếu Word cho bác sĩ. Phần A (khi có `cho_duyet`): đột biến chờ duyệt. Phần B: CHỈ mục chưa có nhãn, đánh số
    theo vị trí trong bộ vàng (để `ghi --loi "21: Đ Đ Đ"` trúng mục) — MÙ với nhận định của máy."""
    chua = [(i, m) for i, m in enumerate(bv["muc"], 1) if not _co_nhan(m)]
    L = ["# PHIẾU GẮN NHÃN BỘ VÀNG — KIỂM CHÉO NGỮ NGHĨA MỤC «ÁP DỤNG»", "",
         f"Ngày dựng: {dt.date.today().strftime('%d/%m/%Y')} · {len(chua)} mục chưa có nhãn"
         + (f" · {len(cho_duyet)} đột biến chờ duyệt" if cho_duyet else "") + ".", ""]
    if cho_duyet:
        L += _phan_a(bv, cho_duyet)
        L += ["# PHẦN B — GẮN NHÃN ĐỘC LẬP MỤC THẬT", ""]
    L += ["Mục do máy chọn từ các dashboard. Phiếu CỐ Ý không in nhận định của máy — bác sĩ đọc mục và nguồn rồi trả "
          "lời ba câu cho từng mục.", "", "**Ba câu hỏi cho mỗi mục** (trả lời Đ = đúng, S = sai, ? = chưa đủ căn cứ):", ""]
    for i, k in enumerate(NHAN, 1):
        L.append(f"{i}. {TEN_NHAN[k]}.")
    L += ["", "**Cách trả lời trong khung chat** (một dòng mỗi mục, ghi chú tuỳ ý sau ba chữ):", "",
          "> 1: Đ Đ Đ · 2: S Đ Đ quần thể bài là HFrEF · 3: Đ Đ S thiếu «ngoài thai kỳ»", "", "---", ""]
    if not chua:
        L += ["*Mọi mục trong bộ vàng đã có nhãn — không còn mục nào cần gắn.*", ""]
    for i, m in chua:
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

_TOK = "|".join(sorted((re.escape(t) for t in _DUNG | _SAI | _CHUA_RO), key=len, reverse=True))
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
        gt = [None if m.group(k) in _CHUA_RO else m.group(k).lower() in _DUNG for k in (2, 3, 4)]
        ra[so] = {"dung_quan_the": gt[0], "dung_chieu": gt[1], "du_dieu_kien": gt[2], "ghi_chu": ghi_chu or None}
    return ra, loi_doc


def ghi_nhan(loi: str, *, ap_dung: bool, ghi_de: bool, tep: Path = TEP_BO_VANG, de_xuat_boi: str | None = None) -> int:
    """Ghi nhãn từ NGUYÊN VĂN lời bác sĩ. `de_xuat_boi` (vd «Claude») khi bác sĩ xác nhận nhãn do máy soạn sẵn — ghi kèm
    từng nhãn để số đo về sau nói rõ «chuẩn có máy tham gia», không trông như bộ vàng bác sĩ gắn độc lập."""
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
            bv["muc"][so - 1]["nhan_bac_si"] = {**nh, "loi_bac_si": loi.strip(), "ngay": dt.date.today().isoformat(),
                                                 **({"de_xuat_boi": de_xuat_boi} if de_xuat_boi else {})}
    if bo:
        print(f"= bỏ qua mục {bo}: đã có nhãn (dùng --ghi-de nếu bác sĩ muốn sửa)")
    if not ap_dung:
        print(f"(chạy khô) sẽ ghi nhãn cho mục {se_ghi} — thêm --ap-dung để ghi")
        return 0
    tep.write_text(json.dumps(bv, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✓ đã ghi nhãn của bác sĩ cho {len(se_ghi)} mục → {tep}")
    return 0


# ───────────────────────── (a) đột biến có kiểm soát ─────────────────────────

def doc_json(tep: Path) -> dict | None:
    try:
        return json.loads(tep.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def kiem_de_xuat(bv: dict, dx: dict) -> list[str]:
    """Lỗi cấu trúc của tệp đề xuất (rỗng = hợp lệ). Bất biến: trục của kiểu đột biến PHẢI là false; trục khác chỉ được
    kế thừa ĐÚNG nhãn của mục gốc hoặc để null; chỉ sửa trường thuộc kiểu (quần thể ⇒ population; chiều ⇒ title/action;
    điều kiện ⇒ action) và phải thật sự đổi nội dung; mục gốc phải là mục thật đã có nhãn."""
    loi: list[str] = []
    thay: set = set()
    ds = dx.get("dot_bien") if isinstance(dx, dict) else None
    if not isinstance(ds, list) or not ds:
        return ["tệp đề xuất không có danh sách `dot_bien`"]
    for x in ds:
        ma = str(x.get("ma") or "?")
        if not re.fullmatch(r"D\d{2,3}", ma) or ma in thay:
            loi.append(f"{ma}: mã trùng hoặc sai khuôn Dnn")
        thay.add(ma)
        tu = x.get("tu_muc")
        if not isinstance(tu, int) or not 1 <= tu <= len(bv["muc"]):
            loi.append(f"{ma}: tu_muc {tu!r} ngoài bộ vàng")
            continue
        goc = bv["muc"][tu - 1]
        if (goc.get("nguon_muc") or "that") != "that" or not _co_nhan(goc):
            loi.append(f"{ma}: mục gốc {tu} phải là mục thật đã có nhãn")
        if x.get("tu_pmid") is not None and str(x["tu_pmid"]) != str(goc.get("pmid")):
            loi.append(f"{ma}: tu_pmid lệch PMID của mục gốc {tu}")
        kieu = x.get("kieu")
        if kieu not in KIEU_DOT_BIEN:
            loi.append(f"{ma}: kiểu «{kieu}» không thuộc {sorted(KIEU_DOT_BIEN)}")
            continue
        sua = x.get("sua") if isinstance(x.get("sua"), dict) else {}
        if not sua or set(sua) - TRUONG_DUOC_SUA[kieu]:
            loi.append(f"{ma}: kiểu {kieu} chỉ được sửa {sorted(TRUONG_DUOC_SUA[kieu])}, đang sửa {sorted(sua)}")
        if sua and all(chuan(str(goc.get(k) or "")) == chuan(str(v)) for k, v in sua.items()):
            loi.append(f"{ma}: phép sửa không đổi nội dung")
        nh = x.get("nhan_du_kien") if isinstance(x.get("nhan_du_kien"), dict) else {}
        truc = KIEU_DOT_BIEN[kieu]
        if nh.get(truc) is not False:
            loi.append(f"{ma}: trục bị đột biến ({truc}) phải mang nhãn dự kiến false")
        goc_nh = goc.get("nhan_bac_si") or {}
        for k in NHAN:
            if k != truc and nh.get(k) is not None and nh.get(k) != goc_nh.get(k):
                loi.append(f"{ma}: trục {k} khẳng định {nh.get(k)} — khác nhãn mục gốc ({goc_nh.get(k)})")
        if not (x.get("mo_ta") or "").strip():
            loi.append(f"{ma}: thiếu mô tả phép sửa")
    return loi


def chuan(t: str) -> str:
    return re.sub(r"\s+", " ", t).strip().casefold()


def dung_dot_bien(bv: dict, dx: dict, chi_ma: set | None = None) -> list[dict]:
    """Mục đột biến (chưa có nhãn): bản sao mục gốc + phép sửa; `id` mang mã đột biến để bộ đệm API không nhầm với gốc."""
    ra = []
    for x in dx["dot_bien"]:
        if chi_ma is not None and x["ma"] not in chi_ma:
            continue
        goc = bv["muc"][x["tu_muc"] - 1]
        m = {k: goc.get(k) for k in ("dashboard", "id", "title", "population", "action", "pmid", "doi", "gradeLevel")}
        m.update(x["sua"])
        m["id"] = f"{goc.get('id')}·{x['ma']}"
        m["nguon_muc"] = "dot_bien"
        m["dot_bien"] = {"ma": x["ma"], "tu_muc": x["tu_muc"], "kieu": x["kieu"], "mo_ta": x.get("mo_ta")}
        m["nhan_du_kien"] = {k: (x.get("nhan_du_kien") or {}).get(k) for k in NHAN}
        m["nhan_bac_si"] = None
        ra.append(m)
    return ra


_MA_DB = re.compile(r"(?<![\w])D(\d{2,3})(?:\s*(?:-|–|…|đến|tới)\s*D?(\d{2,3}))?(?!\w)", re.I)
_LOAI_TRU = re.compile(r"(?<!\w)(?:ngoại trừ|trừ|bỏ|loại|không duyệt|không đồng ý|không đạt)(?!\w)", re.I)
_DONG_Y = re.compile(r"(?<!\w)(?:duyệt|đồng ý|chấp nhận|đạt|ok)(?!\w)", re.I)
_TAT_CA = re.compile(r"(?<!\w)(?:tất cả|toàn bộ|hết|cả danh sách|all)(?!\w)", re.I)


def _cac_ma(doan: str) -> tuple[list[str], list[str]]:
    """(mã Dnn, đoạn khoảng sai) — «D01-D05» bung thành D01…D05; khoảng ngược ⇒ báo lỗi."""
    ra, sai = [], []
    for m in _MA_DB.finditer(doan):
        a, b = int(m.group(1)), int(m.group(2) or m.group(1))
        if b < a:
            sai.append(m.group(0))
            continue
        ra += [f"D{i:02d}" for i in range(a, b + 1)]
    return ra, sai


def doc_loi_duyet(loi: str, ma_hop_le: list[str]) -> tuple[set, set, list[str]]:
    """(mã duyệt, mã loại, phần không đọc được). Mẫu: «duyệt đột biến: tất cả» · «… tất cả trừ D05, D12» · «duyệt D01-D10».
    Không đoán: thiếu lời đồng ý, vừa «tất cả» vừa liệt kê mã ở vế duyệt, mã lạ hoặc không duyệt mã nào ⇒ không đọc được."""
    loi_doc: list[str] = []
    m = _LOAI_TRU.search(loi)
    ve_duyet, ve_loai = (loi[:m.start()], loi[m.end():]) if m else (loi, "")
    if not _DONG_Y.search(ve_duyet):
        loi_doc.append("thiếu lời duyệt («duyệt …» / «đồng ý …»)")
    ma_duyet, sai1 = _cac_ma(ve_duyet)
    ma_loai, sai2 = _cac_ma(ve_loai)
    loi_doc += [f"khoảng mã ngược «{x}»" for x in sai1 + sai2]
    tat_ca = bool(_TAT_CA.search(ve_duyet))
    if tat_ca and ma_duyet:
        loi_doc.append("vừa «tất cả» vừa liệt kê mã ở vế duyệt — nói rõ mã nào loại (sau «trừ»)")
    if m and not ma_loai:
        loi_doc.append(f"có «{m.group(0)}» nhưng không nêu mã nào bị loại")
    la = sorted(set(ma_duyet + ma_loai) - set(ma_hop_le))
    if la:
        loi_doc.append(f"mã không có trong đề xuất: {', '.join(la)}")
    duyet = set(ma_hop_le) if tat_ca else set(ma_duyet)
    loai = set(ma_loai)
    duyet -= loai
    if not duyet and not loi_doc:
        loi_doc.append("không duyệt mã nào")
    return duyet, loai, loi_doc


def doc_dot_bien_da_duyet(tep: Path | None = None) -> list[dict]:
    """Mục đột biến ĐÃ được bác sĩ duyệt (có nhãn) — rỗng khi chưa duyệt / tệp vắng."""
    d = doc_json(tep or TEP_DOT_BIEN) or {}
    return [m for m in d.get("muc") or [] if isinstance(m, dict) and _co_nhan(m)]


def duyet_dot_bien(loi: str, *, ap_dung: bool, ghi_de: bool = False, tep_bv: Path | None = None,
                   tep_de_xuat: Path | None = None, tep_ra: Path | None = None) -> int:
    """Biến đề xuất thành nhãn theo NGUYÊN VĂN lời duyệt của bác sĩ. Chạy khô mặc định; mã đã duyệt không ghi lại trừ
    khi --ghi-de. Nhãn = nhãn dự kiến (cấu trúc phép sửa) + `de_xuat_boi` để số đo luôn nói rõ nguồn gốc."""
    tep_bv, tep_de_xuat, tep_ra = tep_bv or TEP_BO_VANG, tep_de_xuat or TEP_DOT_BIEN_DE_XUAT, tep_ra or TEP_DOT_BIEN
    bv, dx = doc_json(tep_bv), doc_json(tep_de_xuat)
    if not bv or not dx:
        print(f"⚪ thiếu {tep_bv if not bv else tep_de_xuat}")
        return 2
    sai = kiem_de_xuat(bv, dx)
    if sai:
        for x in sai:
            print(f"✗ đề xuất hỏng: {x}")
        return 2
    ma_hop_le = [x["ma"] for x in dx["dot_bien"]]
    duyet, loai, loi_doc = doc_loi_duyet(loi, ma_hop_le)
    for x in loi_doc:
        print(f"✗ không đọc được lời duyệt: {x} — mẫu «duyệt đột biến: tất cả trừ D05, D12»")
    if loi_doc:
        return 1
    cu = doc_json(tep_ra) or {}
    da_co = {(m.get("dot_bien") or {}).get("ma"): m for m in cu.get("muc") or [] if isinstance(m, dict)}
    bo = sorted(ma for ma in duyet if ma in da_co and _co_nhan(da_co[ma]) and not ghi_de)
    moi = sorted(duyet - set(bo))
    if bo:
        print(f"= bỏ qua {', '.join(bo)}: đã duyệt trước đó (dùng --ghi-de nếu bác sĩ muốn duyệt lại)")
    print(f"{'(chạy khô) sẽ ' if not ap_dung else ''}duyệt {len(moi)} đột biến"
          + (f" · loại {len(loai)}: {', '.join(sorted(loai))}" if loai else ""))
    if not ap_dung:
        print("  thêm --ap-dung để ghi")
        return 0
    hom_nay = dt.date.today().isoformat()
    for m in dung_dot_bien(bv, dx, set(moi)):
        m["nhan_bac_si"] = {**m["nhan_du_kien"], "ghi_chu": m["dot_bien"]["mo_ta"], "loi_bac_si": loi.strip(),
                            "ngay": hom_nay, "de_xuat_boi": DE_XUAT_BOI_DOT_BIEN}
        da_co[m["dot_bien"]["ma"]] = m
    for ma in loai:
        if ma in da_co and not _co_nhan(da_co[ma]):
            da_co.pop(ma)
    ra = {"_mo_ta": "Đột biến có kiểm soát ĐÃ được bác sĩ duyệt — nhãn theo cấu trúc phép sửa (xem dot-bien.de-xuat.json). "
                    "Tách riêng mục thật khi đo (nguon_muc: dot_bien).",
          "muc": [da_co[k] for k in sorted(da_co)],
          "bi_loai": sorted(set(cu.get("bi_loai") or []) | loai),
          "lich_su_duyet": [*(cu.get("lich_su_duyet") or []), {"ngay": hom_nay, "loi_bac_si": loi.strip(),
                                                               "duyet": moi, "loai": sorted(loai)}]}
    tep_ra.write_text(json.dumps(ra, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✓ đã ghi {len(moi)} đột biến được duyệt → {tep_ra}")
    return 0


def de_xuat_cho_duyet(bv: dict, tep_de_xuat: Path | None = None, tep_ra: Path | None = None) -> list[dict]:
    """Đề xuất chưa được duyệt hay loại — để in phần A. Đề xuất hỏng ⇒ rỗng (không đưa thứ hỏng cho bác sĩ duyệt)."""
    dx = doc_json(tep_de_xuat or TEP_DOT_BIEN_DE_XUAT)
    if not dx or kiem_de_xuat(bv, dx):
        return []
    cu = doc_json(tep_ra or TEP_DOT_BIEN) or {}
    xong = {(m.get("dot_bien") or {}).get("ma") for m in cu.get("muc") or [] if _co_nhan(m)} | set(cu.get("bi_loai") or [])
    return [x for x in dx["dot_bien"] if x["ma"] not in xong]


# ───────────────────────── (b) mục thật phân tầng ─────────────────────────

_DAC_BIET = re.compile(r"cao tuổi|≥\s*6[05]|>\s*6[05]|trẻ|nhi|thai|mang thai|cho con bú|bệnh thận|ckd|egfr|mlct|lọc máu|"
                       r"suy thận|xơ gan|suy gan|bệnh gan|hfref|hfpef|suy tim|típ 1|type 1|tuýp 1|đa thuốc|suy yếu|"
                       r"hba1c|bmi|ef\s*[<≤>≥]", re.I)


def phan_tang(it: dict, kqtc=None, kcn=None) -> str:
    """Tầng của một mục apply — ưu tiên tầng hiếm (phủ định) trước, để hạn ngạch không bị tầng phổ biến nuốt."""
    kqtc = kqtc or _nap("_bvk_kqtc", "kiem_quan_the_chieu.py")
    kcn = kcn or _nap("_bvk_kcn", "kiem_cheo_ngu_nghia.py")
    if kqtc.muc_phu_dinh_that(it):
        return "phu_dinh"
    if kcn.trich_cum_dieu_kien(it.get("action") or "") or kqtc.hanh_dong_co_dieu_kien(it.get("action") or ""):
        return "dieu_kien"
    if _DAC_BIET.search(f"{it.get('population') or ''} {it.get('title') or ''}"):
        return "dac_biet"
    return "khac"


def _khoa_trung(it: dict) -> tuple:
    return (str(it.get("pmid") or it.get("doi") or "").strip(), chuan(str(it.get("action") or "")))


def chon_muc_that(bv: dict, ung_vien: list[dict], so_muc: int, hat: int = 20261119, tang_cua=None) -> list[dict]:
    """Rút `so_muc` mục theo hạn ngạch tầng (thiếu thì dồn sang tầng sau), tất định theo hạt giống, tối đa 2 mục mỗi
    dashboard, loại mục trùng (định danh + hành động) với bộ vàng và với nhau. `ung_vien`: [{dashboard, it}]."""
    import hashlib
    tang_cua = tang_cua or phan_tang
    da_co = {_khoa_trung(m) for m in bv["muc"]}
    theo_tang: dict[str, list[tuple[str, dict]]] = {t: [] for t in TANG}
    thay: set = set()
    for u in ung_vien:
        it = u["it"]
        if not (isinstance(it, dict) and it.get("decision") == "apply" and it.get("pmid")):
            continue
        k = _khoa_trung(it)
        if k in da_co or k in thay:
            continue
        thay.add(k)
        theo_tang[tang_cua(it)].append((u["dashboard"], it))
    for t in TANG:
        theo_tang[t].sort(key=lambda x: hashlib.sha256(f"{hat}|{x[0]}|{x[1].get('id')}|{x[1].get('pmid')}".encode()).hexdigest())
    he_so = so_muc / sum(HAN_NGACH_TANG.values())
    chi_tieu = {t: round(HAN_NGACH_TANG[t] * he_so) for t in TANG}
    chi_tieu["khac"] += so_muc - sum(chi_tieu.values())
    ra: list[dict] = []
    moi_dash: dict[str, int] = {}
    du = 0
    for t in TANG:
        can = chi_tieu[t] + du
        lay = 0
        for dash, it in theo_tang[t]:
            if lay >= can:
                break
            if moi_dash.get(dash, 0) >= 2:
                continue
            moi_dash[dash] = moi_dash.get(dash, 0) + 1
            lay += 1
            ra.append({"dashboard": dash, "id": it.get("id"), "title": it.get("title"),
                       "population": it.get("population"), "action": it.get("action"), "pmid": it.get("pmid"),
                       "doi": it.get("doi"), "gradeLevel": it.get("gradeLevel"), "nguon_muc": "that", "tang": t,
                       "nhan_bac_si": {"dung_quan_the": None, "dung_chieu": None, "du_dieu_kien": None, "ghi_chu": None}})
        du = can - lay
    return ra


def ung_vien_tu_dashboard() -> list[dict]:
    """Mục apply từ bản ĐÃ PASS mới nhất mỗi chủ đề (đúng luật của `do_nhay_kiem_ngu_nghia.chon_dashboard`)."""
    dn = _nap("_bvk_dn", "do_nhay_kiem_ngu_nghia.py")
    kcn = _nap("_bvk_kcn", "kiem_cheo_ngu_nghia.py")
    ra = []
    for f in dn.chon_dashboard(goc_du_lieu("EBM-Dashboards")):
        data = kcn.doc_data(f) or {}
        ra += [{"dashboard": f.name, "it": it} for it in data.get("items") or []]
    return ra


def them_muc_that(so_muc: int, *, ap_dung: bool, tep: Path | None = None, ung_vien: list[dict] | None = None) -> int:
    tep = tep or TEP_BO_VANG
    bv = doc_json(tep)
    if not bv:
        print(f"⚪ thiếu {tep}")
        return 2
    ung_vien = ung_vien if ung_vien is not None else ung_vien_tu_dashboard()
    moi = chon_muc_that(bv, ung_vien, so_muc)
    if not moi:
        print("⚪ không rút được mục nào (không có dashboard ĐÃ PASS / không còn mục apply có PMID chưa dùng)")
        return 2
    dem = {t: sum(1 for m in moi if m["tang"] == t) for t in TANG}
    print(f"{'(chạy khô) sẽ ' if not ap_dung else ''}thêm {len(moi)} mục thật: "
          + " · ".join(f"{TEN_TANG[t]} {dem[t]}" for t in TANG)
          + (f" (thiếu {so_muc - len(moi)} so với yêu cầu)" if len(moi) < so_muc else ""))
    if not ap_dung:
        print("  thêm --ap-dung để ghi (nhãn để trống — bác sĩ gắn qua phiếu phần B)")
        return 0
    hom_nay = dt.date.today().isoformat()
    for m in moi:
        m["them_ngay"] = hom_nay
    bv["muc"] += moi
    bv["so_muc"] = len(bv["muc"])
    tep.write_text(json.dumps(bv, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✓ đã thêm {len(moi)} mục (bộ vàng nay {bv['so_muc']} mục) → {tep}")
    return 0


_TAT_LOP_API = {"K1_quan_the": "K1", "K2_nguong": "K2", "K2_nguong_hanh_dong": "K2-hđ", "K3_rung_trong_muc": "K3b",
                "K4_nguon_nguoc": "K4", "K4_muc_dao": "K4b"}


def phien_ban_prompt_api(tep: Path | None = None) -> str | None:
    """Phiên bản prompt ĐANG DÙNG của bộ kiểm API — đọc thẳng mã nguồn (không import, tránh vòng nạp)."""
    try:
        t = (tep or REPO / "tools" / "kiem_ngu_nghia_api.py").read_text(encoding="utf-8")
    except OSError:
        return None
    m = re.search(r'^PHIEN_BAN_PROMPT = "([^"]+)"', t, re.M)
    return m.group(1) if m else None


def bao_cao_do_nhay_api(thu_muc: Path | None = None, phien_ban: str | None = None) -> dict | None:
    """Báo cáo `do-nhay-api-*.json` MỚI NHẤT của đúng phiên bản prompt đang dùng (đột biến tổng hợp, 20/11/2026); None nếu
    chưa có/không đọc được."""
    thu_muc = thu_muc or TEP_BO_VANG.parent
    phien_ban = phien_ban or phien_ban_prompt_api()
    tot = None
    for f in sorted(thu_muc.glob("do-nhay-api-*.json")):
        d = doc_json(f)
        if isinstance(d, dict) and d.get("phien_ban") == phien_ban and isinstance(d.get("ket_qua"), dict):
            if tot is None or str(d.get("ngay")) >= str(tot.get("ngay")):
                tot = dict(d, _tep=f.name)
    return tot


def tom_tat_do_nhay_api(bc: dict) -> str:
    """«API K1 95% · … (luật cứng K1 99% · …) trên TEST» — số của tập giữ lại; thiếu TEST thì gộp."""
    th = bc["ket_qua"]["theo_tap"]
    tap = "test" if th.get("test") else "tat_ca"
    lop = th[tap]["lop"]

    def pt(x):
        return "—" if x is None else f"{x * 100:.0f}%"
    api = " · ".join(f"{_TAT_LOP_API.get(k, k)} {pt(o.get('do_nhay'))}" for k, o in lop.items())
    luat = " · ".join(f"{_TAT_LOP_API.get(k, k)} {pt((o.get('luat_cung') or {}).get('do_nhay'))}" for k, o in lop.items())
    kh = " · ".join(f"{_TAT_LOP_API.get(k, k)} {pt((o.get('ket_hop') or {}).get('do_nhay'))}" for k, o in lop.items())
    dc = th[tap].get("doi_chung") or {}
    return (f"đột biến tổng hợp ({bc['_tep']}, tập {tap.upper()}): API {api} — luật cứng {luat} — kết hợp {kh}; API nghi "
            f"trên mục gốc {pt(dc.get('api_ty_le'))}")


def giac_quan(tep_bv: Path | None = None, tep_de_xuat: Path | None = None, tep_ra: Path | None = None,
              thu_muc_bao_cao: Path | None = None) -> tuple[list[tuple[int, str, str, str]], list[str]]:
    """([(ưu tiên, 👤, việc, lệnh)], lý do ⚪) cho hòm việc. Việc của bác sĩ: duyệt đột biến (phần A) và gắn nhãn mục thật
    chưa nhãn (phần B) — chưa xong thì không phép kiểm nào (luật cứng hay API) đo được bỏ lọt. Bộ vàng không đọc được hoặc
    đề xuất hỏng ⇒ ⚪ (không phải «không còn việc»)."""
    bv = doc_json(tep_bv or TEP_BO_VANG)
    if not bv or not isinstance(bv.get("muc"), list):
        return [], ["không đọc được bộ vàng kiểm chéo ngữ nghĩa"]
    chet = []
    dx = doc_json(tep_de_xuat or TEP_DOT_BIEN_DE_XUAT)
    if dx is not None and kiem_de_xuat(bv, dx):
        chet.append("tệp đề xuất đột biến hỏng — không đưa cho bác sĩ duyệt")
    cho = de_xuat_cho_duyet(bv, tep_de_xuat, tep_ra)
    chua = sum(1 for m in bv["muc"] if not _co_nhan(m))
    viec: list[tuple[int, str, str, str]] = []
    bc = bao_cao_do_nhay_api(thu_muc_bao_cao)
    if bc is None:
        viec.append((3, "🛎", f"Độ bắt lỗi bộ kiểm Claude API (prompt {phien_ban_prompt_api() or '?'}) CHƯA đo trên đột biến "
                              "tổng hợp tất định (cùng thước đo với luật cứng K1–K4) — máy đo được, ~2 USD",
                     "python3 tools/do_nhay_api_ngu_nghia.py --goi-api --ghi"))
    if not cho and not chua:
        return viec, chet
    phan = ([f"{len(cho)} đột biến chờ duyệt (phần A, một lượt)"] if cho else []) + \
           ([f"{chua} mục thật chưa có nhãn (phần B, gắn độc lập)"] if chua else [])
    da_do = f"; đã đo trên {tom_tat_do_nhay_api(bc)}" if bc else ""
    viec.insert(0, (3, "👤", f"Bộ vàng kiểm chéo ngữ nghĩa: {' · '.join(phan)} — chưa xong thì bỏ lọt trên LỖI THẬT và báo "
                             f"động giả thật (luật cứng K1–K4 lẫn bộ kiểm API) chưa đo được{da_do}",
                    "python3 tools/bo_vang_kiem_ngu_nghia.py phieu"))
    return viec, chet


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


TRUC_SO_SANH = (("quan_the", "dung_quan_the", "K1"), ("chieu", "dung_chieu", "K4∪K4b"), ("dieu_kien", "du_dieu_kien", "K3b"))


def _do_tap(muc_ds: list[dict], nguon: dict[str, str | None], kiem_muc, api=None) -> dict:
    """Bảng nhầm lẫn của luật cứng (và của bộ kiểm API khi có `api`) trên các mục ĐÃ có nhãn VÀ có tóm tắt nguồn."""
    k1, k4, k3b, k4b, chua = [], [], [], [], {"chua_nhan": 0, "chua_nguon": 0}
    truc: dict[str, dict[str, list]] = {t: {"luat": [], "api": [], "api_null": [], "api_thieu": []} for t, _, _ in TRUC_SO_SANH}
    for m in muc_ds:
        nh = m.get("nhan_bac_si") or {}
        if not any(nh.get(k) is not None for k in NHAN):
            chua["chua_nhan"] += 1
            continue
        tx = nguon.get(str(m.get("pmid"))) if m.get("pmid") else None
        if not tx:
            chua["chua_nguon"] += 1
            continue
        kq = kiem_muc({"id": m.get("id"), "title": m.get("title"), "population": m.get("population"),
                       "action": m.get("action"), "pmid": m.get("pmid"), "doi": m.get("doi")}, tx)
        bao_k1 = any(x["muc"] == "can_doc" for x in kq["k1_nguong"] + kq["k1_cap"])
        bao_k4 = bool(kq.get("k4")) and kq["k4"]["muc"] == "can_doc"
        bao_k4b = bool(kq.get("k4b")) and kq["k4b"]["muc"] == "can_doc"
        bao_k3b = any(x["muc"] == "can_doc" for x in kq.get("k3b") or [])
        if nh.get("dung_quan_the") is not None:
            k1.append((bao_k1, not nh["dung_quan_the"]))
        if nh.get("dung_chieu") is not None and kq.get("k4"):
            k4.append((bao_k4, not nh["dung_chieu"]))
        # K3b/K4b (14/11/2026): chỉ khi bộ kiểm có phép đó (bản kiem_muc cũ/giả không có khoá ⇒ CHƯA ĐO, không phải 0)
        if nh.get("du_dieu_kien") is not None and "k3b" in kq:
            k3b.append((bao_k3b, not nh["du_dieu_kien"]))
        if nh.get("dung_chieu") is not None and kq.get("k4b"):
            k4b.append((bao_k4b, not nh["dung_chieu"]))
        if api is None:
            continue
        tra = api(m, tx)
        luat = {"quan_the": bao_k1, "chieu": bao_k4 or bao_k4b, "dieu_kien": bao_k3b}
        for t, khoa, _ in TRUC_SO_SANH:
            if nh.get(khoa) is None:
                continue
            truc[t]["luat"].append((luat[t], not nh[khoa]))
            if tra is None:
                truc[t]["api_thieu"].append(1)          # chưa chạy API cho mục này ⇒ không tính vào bảng API
                continue
            if tra.get(khoa) is None:
                truc[t]["api_null"].append(1)
            truc[t]["api"].append((tra.get(khoa) is False, not nh[khoa]))
    ra = {"K1": bang_nham_lan(k1), "K4": bang_nham_lan(k4), "K3b": bang_nham_lan(k3b), "K4b": bang_nham_lan(k4b),
          "chua": chua}
    if api is not None:
        ra["so_sanh_api"] = {t: {"luat": bang_nham_lan(v["luat"]), "api": bang_nham_lan(v["api"]),
                                 "api_null": len(v["api_null"]), "api_thieu": len(v["api_thieu"])}
                             for t, v in truc.items()}
    return ra


def do(bv: dict, nguon: dict[str, str | None], kiem_muc=None, dot_bien: list[dict] | None = None, api=None) -> dict:
    """K1 so với «đúng quần thể», K4 so với «đúng chiều» — chỉ trên mục ĐÃ có nhãn và ĐÃ có tóm tắt nguồn.

    Khoá cấp đầu (K1/K4/K3b/K4b) đo MỤC THẬT như trước. `dot_bien` (đột biến bác sĩ đã duyệt) đo RIÊNG ở `theo_nguon`
    — không trộn vào số của mục thật, vì nhãn đột biến đến từ cấu trúc phép sửa chứ không từ bác sĩ đọc độc lập."""
    kiem_muc = kiem_muc or _nap("_bvk_kqtc", "kiem_quan_the_chieu.py").kiem_muc
    that = [m for m in bv["muc"] if (m.get("nguon_muc") or "that") == "that"]
    ra = _do_tap(that, nguon, kiem_muc, api)
    if dot_bien:
        ra["theo_nguon"] = {"that": {k: ra[k] for k in ("K1", "K4", "K3b", "K4b")},
                            "dot_bien": _do_tap(dot_bien, nguon, kiem_muc, api)}
        ra["theo_nguon"]["that"]["n_muc"] = len(that)
        ra["theo_nguon"]["dot_bien"]["n_muc"] = len(dot_bien)
    co_nhan = [m.get("nhan_bac_si") or {} for m in that]
    co_nhan = [nh for nh in co_nhan if any(nh.get(k) is not None for k in NHAN)]
    dk = [(m.get("nhan_bac_si") or {}).get("du_dieu_kien") for m in that]
    co_nhan_dk = [x for x in dk if x is not None]
    ra.update({"muc_rung_dieu_kien": sum(1 for x in co_nhan_dk if x is False) if co_nhan_dk else None,
               "so_nhan_dieu_kien": len(co_nhan_dk),
               "so_nhan": len(co_nhan), "so_nhan_may_de_xuat": sum(1 for nh in co_nhan if nh.get("de_xuat_boi"))})
    return ra


def _pt(x) -> str:
    return "CHƯA ĐO" if x is None else f"{x:.0%}"


def in_do(kq: dict) -> None:
    print("ĐO BỘ VÀNG — kiểm chéo ngữ nghĩa mục «apply» (nhãn của bác sĩ là chuẩn)")
    for k, ten in (("K1", "quần thể"), ("K4", "chiều khuyến cáo"), ("K3b", "nguồn có điều kiện mà mục không giữ"),
                   ("K4b", "mục nói KHÔNG làm khi nguồn ủng hộ — chỉ mục phủ định")):
        b = kq.get(k)
        if b is None:
            continue
        print(f"  {k} ({ten}): {b['n']} mục có nhãn · máy bắt đúng {b['tp']} · báo động giả {b['fp']} "
              f"({_pt(b['bao_dong_gia'])}) · bỏ lọt {b['fn']} ({_pt(b['bo_lot'])})")
    c = kq["chua"]
    print(f"  Chưa đo: {c['chua_nhan']} mục chưa có nhãn bác sĩ · {c['chua_nguon']} mục chưa có tóm tắt nguồn")
    rung = kq["muc_rung_dieu_kien"]
    so_rung = "CHƯA ĐO" if rung is None else f"{rung}/{kq['so_nhan_dieu_kien']}"
    print(f"  Mục bác sĩ nói RỤNG ĐIỀU KIỆN so với bài gốc: {so_rung} — K3b (14/11/2026) là phép duy nhất so mục với bài "
          "gốc, xem dòng K3b ở trên (K3 chỉ kiểm bản xuất giữ cụm điều kiện của MỤC).")
    if kq.get("so_nhan_may_de_xuat"):
        print(f"  ⚠ {kq['so_nhan_may_de_xuat']}/{kq['so_nhan']} nhãn do máy soạn sẵn, bác sĩ xác nhận — chuẩn CÓ máy tham gia, "
              "chưa phải bộ vàng bác sĩ gắn độc lập; đọc số đo với giới hạn đó.")
    if kq.get("theo_nguon"):
        db = kq["theo_nguon"]["dot_bien"]
        print(f"  ── Đột biến có kiểm soát bác sĩ đã duyệt ({db['n_muc']} mục; nhãn theo CẤU TRÚC phép sửa, đo RIÊNG):")
        for k in ("K1", "K4", "K3b", "K4b"):
            b = db[k]
            print(f"     {k}: {b['n']} mục · bắt {b['tp']} · bỏ lọt {b['fn']} ({_pt(b['bo_lot'])}) · "
                  f"báo động giả {b['fp']} ({_pt(b['bao_dong_gia'])})")
    for nhom, ten in (("", "mục thật"), ("dot_bien", "đột biến")):
        ss = (kq.get("theo_nguon", {}).get(nhom) or {}).get("so_sanh_api") if nhom else kq.get("so_sanh_api")
        if not ss:
            continue
        print(f"  ── Luật cứng ↔ bộ kiểm API trên cùng mục ({ten}):")
        for t, _khoa, luat in TRUC_SO_SANH:
            x = ss[t]
            print(f"     {t:9} luật ({luat}): bắt {x['luat']['tp']}/{x['luat']['tp'] + x['luat']['fn']} · báo giả "
                  f"{x['luat']['fp']} ({_pt(x['luat']['bao_dong_gia'])}) │ API: bắt {x['api']['tp']}/"
                  f"{x['api']['tp'] + x['api']['fn']} · báo giả {x['api']['fp']} ({_pt(x['api']['bao_dong_gia'])})"
                  f" · API không phán {x['api_null']}" + (f" · chưa chạy API {x['api_thieu']}" if x["api_thieu"] else ""))
    print("  Chuyển K1/K4 từ CẢNH BÁO sang CHẶN — hay bật bộ kiểm API — là quyết định của bác sĩ sau khi xem số này "
          "(audit/16 §4). Cần bác sĩ kiểm chứng.")


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
    p.add_argument("--de-xuat-boi", help="ai soạn sẵn nhãn mà bác sĩ xác nhận (vd «Claude»); bỏ trống = bác sĩ tự gắn")
    p = sub.add_parser("do")
    p.add_argument("--online", action="store_true")
    p.add_argument("--api", action="store_true", help="đặt kết quả bộ kiểm API (bộ đệm của kiem_ngu_nghia_api.py) cạnh luật cứng")
    p.add_argument("--phien-ban", help="phiên bản prompt của bộ kiểm API khi --api (mặc định phiên bản đang dùng)")
    p = sub.add_parser("duyet-dot-bien")
    p.add_argument("--loi", required=True, help="NGUYÊN VĂN lời duyệt của bác sĩ")
    p.add_argument("--ap-dung", action="store_true")
    p.add_argument("--ghi-de", action="store_true")
    p = sub.add_parser("them-muc-that")
    p.add_argument("--so-muc", type=int, default=40)
    p.add_argument("--ap-dung", action="store_true")
    a = ap.parse_args(argv)
    if not TEP_BO_VANG.is_file():
        print(f"⚪ chưa có {TEP_BO_VANG} — chạy `python3 tools/kiem_cheo_ngu_nghia.py --ung-vien-bo-vang` trước")
        return 2
    if a.lenh == "ghi":
        return ghi_nhan(a.loi, ap_dung=a.ap_dung, ghi_de=a.ghi_de, tep=TEP_BO_VANG, de_xuat_boi=a.de_xuat_boi)
    if a.lenh == "duyet-dot-bien":
        return duyet_dot_bien(a.loi, ap_dung=a.ap_dung, ghi_de=a.ghi_de)
    if a.lenh == "them-muc-that":
        return them_muc_that(a.so_muc, ap_dung=a.ap_dung)
    bv = doc_bo_vang()
    nguon = nap_nguon(bv, online=a.online)
    if a.lenh == "phieu":
        cho = de_xuat_cho_duyet(bv)
        ra = goc_du_lieu("EBM-Dashboards") / "derivatives" / f"PHIEU-GAN-NHAN-BO-VANG_{dt.date.today():%Y%m%d}.docx"
        ra.parent.mkdir(parents=True, exist_ok=True)
        _nap("_bvk_md", "md_sang_docx_times.py").dung_docx(dung_phieu_md(bv, nguon, cho), 12.0).save(str(ra))
        chua = [m for m in bv["muc"] if not _co_nhan(m)]
        co = sum(1 for m in chua if m.get("pmid") and nguon.get(str(m["pmid"])))
        print(f"✓ Phiếu gắn nhãn: {ra} (phần A {len(cho)} đột biến chờ duyệt · phần B {len(chua)} mục chưa có nhãn, "
              f"{co}/{len(chua)} có tóm tắt nguồn)")
        return 0
    api = None
    if a.api:
        api = _nap("_bvk_api", "kiem_ngu_nghia_api.py").tra_bo_dem(phien_ban=getattr(a, "phien_ban", None))
    in_do(do(bv, nguon, dot_bien=doc_dot_bien_da_duyet(), api=api))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
