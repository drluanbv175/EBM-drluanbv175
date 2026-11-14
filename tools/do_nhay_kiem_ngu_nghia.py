#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ĐO ĐỘ NHẠY của kiểm chéo ngữ nghĩa K1–K4 bằng ĐỘT BIẾN TỔNG HỢP có nhãn theo cấu trúc (14/11/2026).

VÌ SAO CÓ
=========
K1 (quần thể) · K2 (con số) · K3 (mệnh đề điều kiện) · K4 (chiều khuyến cáo) đang ở mức CẢNH BÁO
(`audit/16`, bác sĩ duyệt 25/09/2026). Bộ vàng 20 mục (`tools/bo_vang_kiem_ngu_nghia.py do`) mới đo được
BÁO ĐỘNG GIẢ; ĐỘ NHẠY (bỏ lọt) chưa đo vì 20 mục đó không có ca sai nào. Chuyển K1–K4 sang CHẶN là quyết
định của bác sĩ — cần số đo cả hai chiều.

CÁCH LÀM (không đổi hành vi `kiem_cheo_ngu_nghia.py` / `kiem_quan_the_chieu.py` — chỉ GỌI chúng)
==================================================================================================
1. Lấy mục `decision:'apply'` thật từ các dashboard ĐÃ PASS trong `EBM-Dashboards/` (đúng luật «đã qua cổng»
   của `trich_dan_tong_hop_chu_de.trang_thai_phai_sinh`: sidecar Word trùng băm DATA hiện tại + câu PASS
   của cổng), mỗi chủ đề lấy bản PASS mới nhất, khử trùng mục giống hệt giữa các bản. Chỉ ĐỌC dashboard.
2. Văn bản nguồn = đúng thứ dây chuyền dùng ở bước ④-ter: bản tóm tắt PubMed của `kiem_so_lieu.lay_tom_tat`
   (bộ đệm ngoài git; `--online` mới tải phần thiếu).
3. Sinh ĐỘT BIẾN có NHÃN THEO CẤU TRÚC — mỗi đột biến biết trước nó PHẢI bị phép nào bắt, ở trường nào:
     K1  đổi quần thể      — thay/chèn nhãn quần thể loại trừ nhau (HFrEF↔HFpEF, típ 1↔típ 2, …) ⇒ `k1_cap`
     K2  đổi con số        — ngưỡng EF/eGFR/tuổi/HbA1c/BMI/LDL ⇒ `k1_nguong` (audit/16: phần ngưỡng của K2 nằm
                             trong K1) · cỡ mẫu n= ⇒ `k2_co_mau`
     K3  rụng điều kiện    — ở BẢN XUẤT (đúng phạm vi K3) · NGAY TRONG MỤC so với nguồn (ngoài phạm vi K3)
     K4  đảo chiều         — NGUỒN nói ngược chiều với mục apply (đúng phạm vi K4) · MỤC đảo sang «không làm»
                             khi nguồn ủng hộ (ngoài phạm vi K4)
   Nhãn «lỗi» đến từ CẤU TRÚC phép biến đổi (máy biết đã đổi gì), không từ kết quả của chính phép kiểm. Danh
   mục cụm điều kiện, nhãn quần thể, ngưỡng của bộ sinh RỘNG HƠN từ điển của bộ kiểm có chủ ý — để đo được
   cả lỗ hổng từ vựng. Mỗi đột biến có hạt giống riêng (sha256 của hạt giống + khoá mục) ⇒ tất định.
4. Đối chứng KHÔNG đột biến = mục thật + nguồn thật + bản xuất thật ⇒ báo động trên đối chứng. Vì mục thật
   chưa được bác sĩ gắn nhãn đúng/sai, con số này là CẬN TRÊN của báo động giả (một phần 🟠 có thể là lỗi thật).
5. Chạy ĐÚNG hàm kiểm thật (`kiem_muc`, `kiem_dashboard`, `lay_nguon_dieu_kien`, `doi_chieu`). Một đột biến
   «bắt» chỉ khi trường đích chuyển 🟠; 🟠 mới ở chỗ khác ⇒ «bắt lệch»; ✓ ⇒ «lọt xanh» (trấn an sai);
   ⚪ ⇒ «lọt trắng»; phép không sinh dòng nào cho phần bị đổi ⇒ «lọt im». Độ nhạy + KTC 95% Wilson.

GIỚI HẠN NÓI TRƯỚC
==================
* Đây là đột biến TỔNG HỢP — KHÔNG thay bộ vàng do bác sĩ gắn nhãn; lỗi thật có thể khác hình dạng.
* Công cụ KHÔNG đổi chế độ chặn, KHÔNG sửa dashboard, KHÔNG đổi `decision`/`gradeLevel`.
* Báo cáo không chép văn bản nguồn (tóm tắt có bản quyền) — chỉ định danh, mô tả phép biến đổi.

Dùng:
    python3 tools/do_nhay_kiem_ngu_nghia.py                       # chạy khô: in bảng, không ghi tệp
    python3 tools/do_nhay_kiem_ngu_nghia.py --online --ghi        # tải tóm tắt còn thiếu, ghi báo cáo
    python3 tools/do_nhay_kiem_ngu_nghia.py --bo-dem <tệp.json> --hat-giong 20261114 --ghi
Báo cáo: quality/eval/kiem-cheo-ngu-nghia/do-nhay-dot-bien-<YYYYMMDD>.json + .md
Mã thoát: 0 = cả bốn phép đều đo được · 1 = chỉ đo được một phần (phép nào CHƯA ĐO ghi rõ) ·
          2 = không đo được gì (không có dashboard PASS / không có mục apply). «Không đo được» không bao giờ là 0.
Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import html as _html
import importlib.util
import json
import math
import os
import random
import re
import sys
import time
import unicodedata
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
THU_MUC_BAO_CAO = REPO / "quality" / "eval" / "kiem-cheo-ngu-nghia"
HAT_GIONG_MAC_DINH = 20261114
Z95 = 1.959963984540054
PHEP = ("K1", "K2", "K3", "K4")
# Trường phán quyết của kiem_quan_the_chieu.kiem_muc thuộc về phép nào (audit/16: ngưỡng của K2 nằm trong K1).
TRUONG_CUA_PHEP = {"K1": ("k1_cap",), "K2": ("k1_nguong", "k2_co_mau"), "K4": ("k4",)}
KQ = ("bat", "bat_lech", "lot_xanh", "lot_trang", "lot_im")


def _nap(ten: str, tep: str):
    """Nạp MỘT lần một mô-đun trong tools/ theo đường dẫn tệp (không phụ thuộc sys.path)."""
    m = sys.modules.get(ten)
    if m is None:
        sp = importlib.util.spec_from_file_location(ten, Path(__file__).resolve().parent / tep)
        m = importlib.util.module_from_spec(sp)
        sys.modules[ten] = m
        sp.loader.exec_module(m)
    return m


def _k3():
    return _nap("_dnk_k3", "kiem_cheo_ngu_nghia.py")


def _kq():
    return _nap("_dnk_kqtc", "kiem_quan_the_chieu.py")


def _tt():
    return _nap("_dnk_tong_hop", "trich_dan_tong_hop_chu_de.py")


def chuan_hoa(t: str) -> str:
    return _k3().chuan_hoa(t)


def bo_kiem_that() -> dict:
    """Các hàm kiểm THẬT — đo đúng thứ dây chuyền chạy ở ④-bis/④-ter của xuat_goi_cap_nhat.py."""
    return {"kiem_muc": _kq().kiem_muc, "kiem_dashboard": _kq().kiem_dashboard,
            "muc_phu_dinh": _kq().muc_phu_dinh, "k3_nguon": _k3().lay_nguon_dieu_kien,
            "k3_doi_chieu": _k3().doi_chieu}


def goc_du_lieu(ten: str) -> Path:
    """Gốc dữ liệu ngoài git (lồng/anh em của repo); worktree ngoài OneDrive đọc EBM_WORKSPACE_ROOT."""
    try:
        p = _nap("_dnk_bst", "ban_sao_tran.py").duong_goc(ten, REPO)
    except Exception:  # noqa: BLE001 — không dò được ⇒ thử biến môi trường
        p = None
    if p is None and os.environ.get("EBM_WORKSPACE_ROOT"):
        p = Path(os.environ["EBM_WORKSPACE_ROOT"]) / ten
    return p or (REPO / ten)


# ───────────────────────── tiện ích chung ─────────────────────────

def wilson(k: int, n: int, z: float = Z95) -> tuple[float, float] | None:
    """Khoảng tin cậy Wilson cho tỉ lệ k/n (None khi n = 0 — không bao giờ giả vờ là 0%)."""
    if n <= 0:
        return None
    p = k / n
    d = 1 + z * z / n
    tam = (p + z * z / (2 * n)) / d
    nua = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, tam - nua), min(1.0, tam + nua))


def rng_cho(hat: int, *khoa) -> random.Random:
    """Bộ sinh ngẫu nhiên riêng cho MỘT mục/lớp — tất định, không phụ thuộc thứ tự hay số mục khác."""
    h = hashlib.sha256("|".join([str(hat), *map(str, khoa)]).encode("utf-8")).hexdigest()
    return random.Random(int(h[:16], 16))


def _sao(it: dict) -> dict:
    return copy.deepcopy(it)


def _nfc_json(x) -> str:
    return unicodedata.normalize("NFC", json.dumps(x, ensure_ascii=False, sort_keys=True))


def _pmid(it: dict) -> str | None:
    s = str(it.get("pmid") or "").strip()
    return s if re.fullmatch(r"\d{1,9}", s) else None


def _thay(van_ban: str, i: int, j: int, moi: str) -> str:
    return van_ban[:i] + moi + van_ban[j:]


def _don_cau(t: str) -> str:
    """Dọn chỗ hở sau khi cắt một cụm: khoảng trắng đôi, dấu phẩy treo, ngoặc rỗng."""
    t = re.sub(r"\(\s*\)", "", t)
    t = re.sub(r"\s+([,.;:])", r"\1", t)
    t = re.sub(r"([,;:])\s*([,.;:])", r"\2", t)
    t = re.sub(r"\s{2,}", " ", t)
    return t.strip(" ,;:")


def _thay_so(van_ban: str, so_cu_span: tuple[int, int], moi: str) -> str:
    return _thay(van_ban, so_cu_span[0], so_cu_span[1], moi)


_BO_DOAN = re.compile(r"^(author information|copyright|©|conflict of interest|comment in|erratum in|update of|"
                      r"doi:|pmid:|pmcid:|retraction|expression of concern)", re.I)


def doan_than(raw: str) -> list[tuple[int, int]]:
    """Khoảng ký tự [đầu, cuối) của các đoạn THÂN tóm tắt trong bản efetch dạng text (bỏ dòng trích dẫn đầu,
    danh sách tác giả, thông tin tác giả, bản quyền, định danh). Dùng để đặt ĐIỀU KIỆN TIÊN QUYẾT của bộ sinh
    và chọn câu để đảo chiều — bộ kiểm thì vẫn đọc NGUYÊN bản efetch như dây chuyền."""
    ra: list[tuple[int, int]] = []
    vi_tri = [(m.start(), m.end()) for m in re.finditer(r"(?:[^\n]|\n(?!\s*\n))+", raw)]
    co_info = any(raw[a:b].strip().lower().startswith("author information") for a, b in vi_tri)
    qua_tac_gia = not co_info
    for idx, (a, b) in enumerate(vi_tri):
        doan = raw[a:b].strip()
        if not doan:
            continue
        if idx == 0 and re.match(r"^\d+\.\s", doan):
            continue                                  # dòng trích dẫn «1. N Engl J Med. 2021…»
        if doan.lower().startswith("author information"):
            qua_tac_gia = True
            continue
        if not qua_tac_gia:
            if idx == 1:
                ra.append((a, b))                     # tiêu đề
            continue                                  # danh sách tác giả
        if _BO_DOAN.match(doan):
            continue
        ra.append((a, b))
    return ra


def van_ban_than(raw: str) -> str:
    return "\n\n".join(raw[a:b] for a, b in doan_than(raw))


def _co_so(so: str, van_ban_chuan: str) -> bool:
    """Con số (đã đổi «,» thập phân → «.») xuất hiện độc lập trong văn bản đã chuẩn hoá."""
    return re.search(rf"(?<![\d.,]){re.escape(so)}(?:\.0+)?(?![\d]|[.,]\d)", van_ban_chuan.replace(",", ".")) is not None


def _chu_so(s: str) -> str:
    return re.sub(r"[.,\s]", "", s)


def _co_co_mau(so: str, van_ban_chuan: str) -> bool:
    """«8474» có trong văn bản dưới dạng 8474 / 8,474 / 8 474 / 8.474 (không khớp một phần)."""
    dau = len(so) % 3 or 3
    nhom = [so[:dau]] + [so[i:i + 3] for i in range(dau, len(so), 3)]
    return re.search(r"(?<![\d.,])" + r"[.,\s]?".join(nhom) + r"(?![\d]|[.,]\d)", van_ban_chuan) is not None


# ───────────────────────── chọn dashboard + mục ─────────────────────────

_NGAY_DUOI = re.compile(r"_(\d{8})$")


def khoa_chu_de(dash: Path) -> tuple[str, str]:
    """(khoá chủ đề, ngày) — khoá = tên tệp bỏ hậu tố _YYYYMMDD."""
    m = _NGAY_DUOI.search(dash.stem)
    return (dash.stem[:m.start()], m.group(1)) if m else (dash.stem, "")


def da_pass_that(dash: Path) -> bool:
    """Luật «đã qua cổng» của dây chuyền: sidecar Word trùng băm DATA hiện tại + bản Word ghi câu PASS."""
    return bool(_tt().trang_thai_phai_sinh(dash).get("xac_minh"))


def chon_dashboard(thu_muc: Path, da_pass=None) -> list[Path]:
    """Mỗi chủ đề lấy bản ĐÃ PASS mới nhất (bản mới chưa PASS thì lùi về bản PASS trước đó)."""
    da_pass = da_pass or da_pass_that
    moi_nhat: dict[str, Path] = {}
    for f in sorted(thu_muc.glob("WebDashboard_*.html")):
        if not f.is_file() or not da_pass(f):
            continue
        k, ngay = khoa_chu_de(f)
        cu = moi_nhat.get(k)
        if cu is None or ngay >= khoa_chu_de(cu)[1]:
            moi_nhat[k] = f
    return sorted(moi_nhat.values())


def lay_muc_apply(du_lieu: dict[Path, dict]) -> list[dict]:
    """[{dashboard, duong_dan, chi_so, muc}] — mục apply, khử trùng (định danh + hành động + quần thể)."""
    ra: list[dict] = []
    da_thay: set = set()
    for f, data in du_lieu.items():
        for i, it in enumerate(data.get("items") or []):
            if not (isinstance(it, dict) and it.get("decision") == "apply"):
                continue
            khoa = (str(it.get("pmid") or it.get("doi") or "").strip(), chuan_hoa(str(it.get("action") or "")),
                    chuan_hoa(str(it.get("population") or "")))
            if khoa in da_thay:
                continue
            da_thay.add(khoa)
            ra.append({"dashboard": f.name, "duong_dan": f, "chi_so": i, "muc": it})
    return ra


# ───────────────────────── nguồn (tóm tắt PubMed) ─────────────────────────

def nap_nguon(pmids: list[str], *, tep_dem: Path, tep_them: tuple[Path, ...] = (), online: bool = False,
              lay=None, toi_da: int | None = None, nghi: float = 0.34) -> tuple[dict[str, str], dict]:
    """({pmid: bản efetch text}, thống kê). Đọc bộ đệm (kể cả bộ đệm bộ vàng, CHỈ ĐỌC); --online tải phần thiếu
    bằng CHÍNH `kiem_so_lieu.lay_tom_tat` rồi ghi vào `tep_dem` (ngoài git — văn bản có bản quyền)."""
    dem: dict[str, str] = {}
    for p in (*tep_them, tep_dem):
        try:
            raw = json.loads(Path(p).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for k, v in (raw.items() if isinstance(raw, dict) else []):
            if isinstance(v, str) and v.strip():
                dem[str(k)] = v
    thieu = [p for p in pmids if p not in dem]
    tk = {"can": len(pmids), "co_san": len(pmids) - len(thieu), "tai_moi": 0, "tai_hong": 0}
    if online and thieu:
        lay = lay or _nap("_dnk_ksl", "kiem_so_lieu.py").lay_tom_tat
        cu_tep = {}
        try:
            cu_tep = json.loads(Path(tep_dem).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            cu_tep = {}
        for p in thieu[: toi_da if toi_da is not None else len(thieu)]:
            t = lay(p)
            if t:
                dem[p] = t
                cu_tep[p] = t
                tk["tai_moi"] += 1
            else:
                tk["tai_hong"] += 1
            if nghi:
                time.sleep(nghi)
        Path(tep_dem).parent.mkdir(parents=True, exist_ok=True)
        Path(tep_dem).write_text(json.dumps(cu_tep, ensure_ascii=False, indent=1) + "\n", encoding="utf-8",
                                 newline="\n")
    return {p: dem[p] for p in pmids if dem.get(p)}, tk


# ───────────────────────── K1: nhãn quần thể ─────────────────────────
# Mỗi cặp: vế ĐẶC HIỆU (phủ định/hẹp) đứng trước để tách được «không lọc máu» khỏi «lọc máu».
# ten = tên vế đúng như bộ kiểm in ra (kiem_quan_the_chieu._CAP); vi = mẫu nhận ở MỤC; en = mẫu nhận ở NGUỒN;
# bien_the = các cách viết tiếng Việt CHÈN vào mục (cố ý gồm cách viết bộ kiểm chưa có trong từ điển).
_CAP_K1 = (
    ({"ten": "HFrEF", "vi": r"hfref|phân suất tống máu giảm|ef giảm|pstm giảm",
      "en": r"hfref|reduced (?:left ventricular )?ejection fraction",
      "bien_the": ("HFrEF", "suy tim phân suất tống máu giảm", "suy tim EF giảm", "suy tim PSTM giảm")},
     {"ten": "HFpEF", "vi": r"hfpef|phân suất tống máu (?:còn )?bảo tồn|ef bảo tồn|pstm bảo tồn",
      "en": r"hfpef|preserved (?:left ventricular )?ejection fraction",
      "bien_the": ("HFpEF", "suy tim phân suất tống máu bảo tồn", "suy tim EF bảo tồn",
                   "suy tim phân suất tống máu còn bảo tồn")}),
    ({"ten": "ĐTĐ típ 1", "vi": r"(?:típ|tuýp|type) ?1|đtđ ?1(?!\d)", "en": r"type 1 diabetes|type i diabetes|t1dm?",
      "bien_the": ("ĐTĐ típ 1", "đái tháo đường type 1", "ĐTĐ tuýp 1", "ĐTĐ1")},
     {"ten": "ĐTĐ típ 2", "vi": r"(?:típ|tuýp|type) ?2|đtđ ?2(?!\d)", "en": r"type 2 diabetes|type ii diabetes|t2dm?",
      "bien_the": ("ĐTĐ típ 2", "đái tháo đường type 2", "ĐTĐ tuýp 2", "ĐTĐ2")}),
    ({"ten": "trẻ em", "vi": r"trẻ em|bệnh nhi|nhi khoa|trẻ vị thành niên|children|pediatric",
      "en": r"child(?:ren)?|pa?ediatric|adolescen\w*|infants?|neonat\w*|newborns?",
      "bien_the": ("trẻ em", "bệnh nhi", "trẻ vị thành niên", "nhi khoa")},
     {"ten": "người lớn", "vi": r"người lớn|người trưởng thành|adults?", "en": r"adults?",
      "bien_the": ("người lớn", "người trưởng thành")}),
    ({"ten": "ngoài thai kỳ", "vi": r"ngoài thai kỳ|không mang thai|non-pregnant", "en": r"non-?pregnant|not pregnant",
      "bien_the": ("ngoài thai kỳ", "phụ nữ không mang thai")},
     {"ten": "thai kỳ", "vi": r"thai kỳ|thai phụ|phụ nữ có thai|mang thai|pregnan\w*",
      "en": r"pregnan\w*|gestation\w*|antenatal|prenatal",
      "bien_the": ("phụ nữ mang thai", "thai phụ", "trong thai kỳ", "phụ nữ có thai")}),
    ({"ten": "không lọc máu", "vi": r"không lọc máu|chưa lọc máu|chưa chạy thận|non-dialysis",
      "en": r"non-?dialysis|not (?:on|receiving|requiring) dialysis",
      "bien_the": ("không lọc máu", "chưa lọc máu", "CKD chưa chạy thận")},
     {"ten": "lọc máu", "vi": r"lọc máu|chạy thận|thẩm phân|dialysis", "en": r"dialysis|ha?emodialysis",
      "bien_the": ("lọc máu", "chạy thận nhân tạo", "thẩm phân", "đang lọc máu chu kỳ")}),
)
_PHU_DINH_MUC = r"(?:không|loại trừ|ngoại trừ|trừ|excluding|without|not)"


def _ve_co(cap: tuple[dict, dict], t: str, khoa: str) -> dict[str, bool]:
    """{tên vế: có mặt} trong văn bản `t` (đã chuẩn hoá) — vế đặc hiệu xét và xoá trước."""
    ra = {}
    for ve in cap:
        mau = ve[khoa]
        ra[ve["ten"]] = re.search(rf"(?<!\w)(?:{mau})(?!\w)", t) is not None
        if ra[ve["ten"]]:
            t = re.sub(rf"(?<!\w)(?:{mau})(?!\w)", " ", t)
    return ra


def _co_phu_dinh_truoc(cap: tuple[dict, dict], t: str) -> bool:
    mau = "|".join(ve["vi"] for ve in cap)
    return re.search(rf"(?<!\w){_PHU_DINH_MUC}\s+(?:\S+\s+){{0,2}}?(?:{mau})(?!\w)", t) is not None


def _truong_qt(it: dict) -> list[str]:
    """Trường văn bản quần thể mà K1 đọc: population (+ pico.P nếu là chữ tự do)."""
    ra = ["population"]
    pico = it.get("pico")
    if isinstance(pico, dict) and isinstance(pico.get("P"), str) and pico["P"] not in ("match", "partial", "mismatch"):
        ra.append("pico.P")
    return ra


def _doc_truong(it: dict, truong: str) -> str:
    """Văn bản một trường của mục, NFC (bộ kiểm cũng NFC hoá ⇒ không đổi kết quả, nhưng regex của bộ sinh khớp được)."""
    v = (it.get("pico") or {}).get("P") if truong == "pico.P" else it.get(truong)
    return unicodedata.normalize("NFC", str(v or ""))


def _ghi_truong(it: dict, truong: str, gia_tri: str) -> None:
    if truong == "pico.P":
        it["pico"]["P"] = gia_tri
    else:
        it[truong] = gia_tri


def k1_trong_tu_dien(ve_ten: str, viet: str) -> bool:
    """Cách viết `viet` có được TỪ ĐIỂN của bộ kiểm K1 nhận là vế `ve_ten` không — hỏi thẳng `kiem_cap` thật (cùng
    luật xét vế đặc hiệu trước, bỏ vế sau phủ định). Nhãn CẤU TRÚC tính trước khi chấm, không nhìn nguồn hay kết quả:
    dùng để tách «lỗ hổng từ vựng» (cách viết ngoài từ điển) khỏi «lỗ hổng cơ chế» trong độ nhạy K1."""
    return any(x["ve_muc"] == ve_ten for x in _kq().kiem_cap(chuan_hoa(viet), ""))


def sinh_k1(rec: dict, nguon: str, hat: int) -> dict | None:
    """Thay nhãn quần thể A→B (mục mang A, nguồn nêu A không nêu B) hoặc chèn B khi mục chưa mang nhãn nào."""
    it = rec["muc"]
    than = chuan_hoa(van_ban_than(nguon))
    r = rng_cho(hat, rec["dashboard"], it.get("id"), rec["chi_so"], "K1")
    thay, chen = [], []
    for cap in _CAP_K1:
        ten_truong = _truong_qt(it)
        vb = chuan_hoa(" . ".join(_doc_truong(it, t) for t in ten_truong))
        if _co_phu_dinh_truoc(cap, vb):
            continue
        co_muc, co_nguon = _ve_co(cap, vb, "vi"), _ve_co(cap, than, "en")
        for a, b in ((cap[0], cap[1]), (cap[1], cap[0])):
            if co_nguon[a["ten"]] and not co_nguon[b["ten"]]:
                if co_muc[a["ten"]] and not co_muc[b["ten"]]:
                    thay.append((a, b))
                elif not co_muc[a["ten"]] and not co_muc[b["ten"]]:
                    chen.append((a, b))
    if not thay and not chen:
        return None
    kieu, (a, b) = ("thay_nhan", r.choice(thay)) if thay else ("chen_nhan", r.choice(chen))
    viet = r.choice(b["bien_the"])
    moi = _sao(it)
    if kieu == "thay_nhan":
        for t in _truong_qt(moi):
            goc = _doc_truong(moi, t)
            _ghi_truong(moi, t, re.sub(rf"(?<!\w)(?:{a['vi']})(?!\w)", viet, goc, flags=re.I))
    else:
        moi["population"] = f"{viet}, {it.get('population') or ''}".strip(", ")
    return {"lop": "K1_quan_the", "phep": "K1", "truong": "k1_cap", "trong_pham_vi": True,
            "bien_the": f"{kieu}:{viet}", "dich": {"ve_muc": b["ten"]}, "tu_dien_bo_kiem": k1_trong_tu_dien(b["ten"], viet),
            "mo_ta": f"{kieu}: nguồn nêu «{a['ten']}», mục ghi «{viet}»", "muc_dot_bien": moi, "nguon_dot_bien": nguon}


# ───────────────────────── K2: con số (ngưỡng + cỡ mẫu) ─────────────────────────

_CHI_SO_VI = {
    "ef": r"lvef|ef|phân suất tống máu|pstm",
    "egfr": r"egfr|gfr|mlct|mức lọc cầu thận|độ lọc cầu thận",
    "tuoi": r"tuổi",
    "hba1c": r"hba1c|a1c",
    "bmi": r"bmi|chỉ số khối cơ thể",
    "ldl": r"ldl-c|ldl",
}
_CHI_SO_EN = {
    "ef": r"lvef|ejection fraction|ef",
    "egfr": r"egfr|glomerular filtration rate|gfr",
    "tuoi": r"aged?|years of age|years old|years or older|older|age",
    "hba1c": r"hba1c|a1c|glycated ha?emoglobin|glycosylated ha?emoglobin",
    "bmi": r"bmi|body mass index",
    "ldl": r"ldl-c|ldl cholesterol|ldl|low-density lipoprotein",
}
_NGUONG_THAY = {"ef": (30, 35, 40, 45, 50), "egfr": (15, 20, 25, 30, 45, 60), "tuoi": (18, 40, 50, 60, 65, 70, 75, 80),
                "hba1c": (6.5, 7, 7.5, 8, 9), "bmi": (25, 27, 30, 35, 40), "ldl": (55, 70, 100, 130, 190)}
_TOAN_TU = r"(?:≥|≤|>=|<=|<|>|=|dưới|trên|từ)"
_SO = r"\d+(?:[.,]\d+)?"


def tim_nguong(van_ban: str) -> list[dict]:
    """[{chi_so, so, span, dang}] — ngưỡng số trong văn bản MỤC (bộ sinh tự nhận, rộng hơn bộ kiểm)."""
    ra, da = [], set()
    for chi, mau in _CHI_SO_VI.items():
        mau_dang = [("chi_truoc", rf"(?<!\w)(?:{mau})(?!\w)\s*{_TOAN_TU}?\s*(?P<so>{_SO})(?![\d])")]
        if chi == "tuoi":
            mau_dang += [("so_truoc", rf"{_TOAN_TU}\s*(?P<so>\d+)\s*(?:{mau})(?!\w)"),
                         ("tro_len", rf"(?<![\d.,])(?P<so>\d+)\s*(?:{mau})\s*(?:trở lên|trở xuống)")]
        for dang, mau_re in mau_dang:
            for m in re.finditer(mau_re, van_ban, flags=re.I):
                span = m.span("so")
                if span in da:
                    continue
                da.add(span)
                ra.append({"chi_so": chi, "so": m.group("so"), "span": span, "span_cum": m.span(), "dang": dang})
    return sorted(ra, key=lambda x: x["span"])


def _nguon_ung_ho_nguong(chi: str, so: str, than_chuan: str) -> bool:
    so = so.replace(",", ".")
    for m in re.finditer(rf"(?<!\w)(?:{_CHI_SO_EN[chi]})(?!\w)", than_chuan):
        vung = than_chuan[max(0, m.start() - 60):m.end() + 60]
        if _co_so(so, vung):
            return True
    return False


def _dinh_dang_so(goc: str, gia_tri: float) -> str:
    s = (f"{gia_tri:g}")
    return s.replace(".", ",") if "," in goc else s


def sinh_k2_nguong(rec: dict, nguon: str, hat: int, *, truong_hanh_dong: bool = False) -> dict | None:
    """Đổi MỘT ngưỡng số mà nguồn ủng hộ thành giá trị nguồn KHÔNG nêu. truong_hanh_dong=True ⇒ đổi ngưỡng
    nằm trong `action` (K1/K2 không đọc action ⇒ ngoài phạm vi thiết kế)."""
    it = rec["muc"]
    than = chuan_hoa(van_ban_than(nguon))
    toan_bo = chuan_hoa(nguon)
    ds_truong = ["action"] if truong_hanh_dong else _truong_qt(it)
    ung_vien = []
    for t in ds_truong:
        for x in tim_nguong(_doc_truong(it, t)):
            if _nguon_ung_ho_nguong(x["chi_so"], x["so"], than):
                ung_vien.append((t, x))
    if not ung_vien:
        return None
    r = rng_cho(hat, rec["dashboard"], it.get("id"), rec["chi_so"], "K2a" if truong_hanh_dong else "K2")
    t, x = r.choice(ung_vien)
    cu = float(x["so"].replace(",", "."))
    lua = [v for v in _NGUONG_THAY[x["chi_so"]] if abs(v - cu) > 1e-9 and not _co_so(f"{v:g}", toan_bo)]
    if not lua:
        return None
    v = r.choice(lua)
    moi = _sao(it)
    _ghi_truong(moi, t, _thay_so(_doc_truong(it, t), x["span"], _dinh_dang_so(x["so"], v)))
    lop = "K2_nguong_hanh_dong" if truong_hanh_dong else "K2_nguong"
    return {"lop": lop, "phep": "K2", "truong": "k1_nguong", "trong_pham_vi": not truong_hanh_dong,
            "bien_the": f"{x['chi_so']}:{x['dang']}", "dich": {"chi_so": x["chi_so"], "so": f"{v:g}"},
            "mo_ta": f"{t}: {x['chi_so']} {x['so']} → {_dinh_dang_so(x['so'], v)}", "muc_dot_bien": moi,
            "nguon_dot_bien": nguon}


_N_MUC = re.compile(r"(?<!\w)n\s*=\s*(\d{1,3}(?:[.,\s]\d{3})+|\d+)(?!\d)", re.I)
_N_NGUON = re.compile(r"(?<![\d.,])(\d{1,3}(?:,\d{3})+|\d{2,})\s+(?:patients|participants|adults|subjects|women|men|"
                      r"children|individuals|people|persons)", re.I)
_KIEU_N = ("n={:d}", "n = {:,}", "n={:,}", "N={:,}")


def _viet_n(mau: str, so: int) -> str:
    return mau.format(so)


def sinh_k2_co_mau(rec: dict, nguon: str, hat: int) -> dict | None:
    """Đổi cỡ mẫu n= mà nguồn ủng hộ; mục chưa ghi n= thì CHÈN n= sai khi nguồn có nêu «N patients…»."""
    it = rec["muc"]
    than = chuan_hoa(van_ban_than(nguon))
    toan_bo = chuan_hoa(nguon)
    r = rng_cho(hat, rec["dashboard"], it.get("id"), rec["chi_so"], "K2n")
    ds = ["population"] + [t for t in _truong_qt(it) if t != "population"] + ["title"]
    ung_vien = []
    for t in ds:
        for m in _N_MUC.finditer(_doc_truong(it, t)):
            so = _chu_so(m.group(1))
            if int(so) >= 10 and _co_co_mau(so, than):
                ung_vien.append((t, m))
    he_so = (0.8, 1.25, 1.5, 2.0)
    if ung_vien:
        t, m = r.choice(ung_vien)
        cu = int(_chu_so(m.group(1)))
        lua = [int(round(cu * h)) for h in he_so]
        lua = [v for v in lua if v != cu and not _co_co_mau(str(v), toan_bo)]
        if not lua:
            return None
        v = r.choice(lua)
        moi = _sao(it)
        _ghi_truong(moi, t, _thay(_doc_truong(it, t), m.start(1), m.end(1), f"{v:,}"))
        return {"lop": "K2_co_mau", "phep": "K2", "truong": "k2_co_mau", "trong_pham_vi": True,
                "bien_the": "thay_n", "dich": {"so": str(v)}, "mo_ta": f"{t}: n={cu} → n={v}",
                "muc_dot_bien": moi, "nguon_dot_bien": nguon}
    if any(_N_MUC.search(_doc_truong(it, t)) for t in ds):
        return None
    so_nguon = [int(_chu_so(m.group(1))) for m in _N_NGUON.finditer(than)]
    if not so_nguon:
        return None
    cu = r.choice(so_nguon)
    lua = [v for v in (int(round(cu * h)) for h in he_so) if v != cu and v >= 10 and not _co_co_mau(str(v), toan_bo)]
    if not lua:
        return None
    v = r.choice(lua)
    kieu = r.choice(_KIEU_N)
    moi = _sao(it)
    moi["population"] = f"{it.get('population') or ''} ({_viet_n(kieu, v)})".strip()
    return {"lop": "K2_co_mau", "phep": "K2", "truong": "k2_co_mau", "trong_pham_vi": True,
            "bien_the": f"chen_n:{kieu}", "dich": {"so": str(v)}, "mo_ta": f"chèn {_viet_n(kieu, v)} (nguồn nêu {cu})",
            "muc_dot_bien": moi, "nguon_dot_bien": nguon}


# ───────────────────────── K3: mệnh đề điều kiện ─────────────────────────
# Danh mục dấu điều kiện CỦA BỘ SINH. Nhóm «dau_k3» là cùng chữ với từ điển của bộ kiểm — CHỈ để gắn nhãn phân nhóm
# trong báo cáo, KHÔNG dùng để quyết định bắt/lọt; nhóm «dau_khac» là điều kiện/giới hạn quần thể bộ kiểm chưa có.
_DAU_K3 = ("không dùng khi", "không dùng cho", "với điều kiện", "chống chỉ định", "ngoài thai kỳ", "trong thai kỳ",
           "trừ khi", "chỉ khi", "sau khi", "trước khi", "nếu", "khi")
# Cố ý KHÔNG gồm «cho người bệnh», «với bệnh nhân»… (thường chỉ là đối tượng tư vấn, không giới hạn khuyến cáo).
_DAU_KHAC = ("trong trường hợp", "chỉ dùng cho", "chỉ áp dụng cho", "miễn là", "ngoại trừ", "ở bệnh nhân", "ở người",
             "ở bn", "ở phụ nữ", "ở trẻ", "đối với", "trừ")
_DAU_TU_DU = {"ngoài thai kỳ", "trong thai kỳ"}
_TAT_CA_DAU = sorted(set(_DAU_K3) | set(_DAU_KHAC), key=len, reverse=True)
_MAU_DAU = re.compile(r"(?<!\w)(" + "|".join(re.escape(d) for d in _TAT_CA_DAU) + r")(?!\w)", re.I)
_NGAT = re.compile(r"[.;,()\[\]\n—–:]| - ")


def tim_dieu_kien(van_ban: str) -> list[dict]:
    """[{span, cum, nhom}] — cụm điều kiện trong `action` theo danh mục của BỘ SINH (độc lập với bộ kiểm)."""
    ra: list[dict] = []
    for m in _MAU_DAU.finditer(van_ban):
        dau = m.group(1).lower()
        if any(m.start() < x["span"][1] and x["span"][0] < m.end() for x in ra):
            continue
        if dau == "trừ" and van_ban[max(0, m.start() - 5):m.start()].lower() == "loại ":
            continue                                   # «loại trừ» (chẩn đoán phân biệt) không phải điều kiện
        duoi = van_ban[m.end():m.end() + 90]
        cat = _NGAT.search(duoi)
        het = m.end() + (cat.start() if cat else len(duoi))
        if dau not in _DAU_TU_DU and not van_ban[m.end():het].split():
            continue
        nhom = "dau_k3" if dau in _DAU_K3 else "dau_khac"
        ra.append({"span": (m.start(), het), "cum": van_ban[m.start():het].strip(), "nhom": f"{nhom}:{dau}"})
    for x in tim_nguong(van_ban):
        bat_dau, het = x["span_cum"]
        het += 1 if van_ban[het:het + 1] == "%" else 0
        if any(bat_dau < y["span"][1] and y["span"][0] < het for y in ra):
            continue
        ra.append({"span": (bat_dau, het), "cum": van_ban[bat_dau:het].strip(), "nhom": f"nguong_so:{x['chi_so']}"})
    return sorted(ra, key=lambda x: x["span"])


def _cat_cum(van_ban: str, span: tuple[int, int]) -> str:
    return _don_cau(van_ban[:span[0]] + " " + van_ban[span[1]:])


def _duong_word(dash: Path) -> Path:
    return dash.parent / "derivatives" / f"{_tt().ma_phai_sinh(dash)}_TaiLieuChiTiet.html"


def _duong_ban_doc(dash: Path) -> Path:
    return dash.parent / "derivatives" / f"{_tt().ma_phai_sinh(dash)}_ban-doc.html"


def _doc(p: Path) -> str | None:
    try:
        return p.read_text(encoding="utf-8", errors="replace") if p.is_file() else None
    except OSError:
        return None


def gon_dau(t: str) -> str:
    """Bỏ khoảng trắng trước dấu câu/sau ngoặc mở — thẻ HTML bị thay bằng khoảng trắng («kỳ</b>,» → «kỳ ,») làm hành
    động không còn khớp nguyên văn. Cụm điều kiện của K3 dừng TRƯỚC mọi dấu này nên phép gọn không đổi kết quả K3."""
    return re.sub(r"\s+([,.;:!?)\]])", r"\1", re.sub(r"([(\[])\s+", r"\1", t))


def _boc(van_ban_chuan: str) -> str:
    """Đưa văn bản ĐÃ chuẩn hoá vào doi_chieu mà không bị chuẩn hoá lần hai làm lệch (chuan_hoa không luỹ đẳng:
    «<30 … >» trong văn bản đã giải mã bị đọc như thẻ HTML). html.escape ⇒ chuan_hoa trả lại đúng chuỗi cũ."""
    return _html.escape(van_ban_chuan, quote=False)


def sinh_k3(rec: dict, hat: int, word_chuan: str | None) -> list[dict]:
    """Hai đột biến cho CÙNG một cụm điều kiện: rụng ở BẢN XUẤT (mục giữ nguyên) và rụng NGAY TRONG MỤC."""
    it = rec["muc"]
    act = _doc_truong(it, "action")
    cum = tim_dieu_kien(act)
    if not cum:
        return []
    r = rng_cho(hat, rec["dashboard"], it.get("id"), rec["chi_so"], "K3")
    x = r.choice(cum)
    act_moi = _cat_cum(act, x["span"])
    if not act_moi or chuan_hoa(act_moi) == chuan_hoa(act):
        return []
    a0, a1 = gon_dau(chuan_hoa(act)), gon_dau(chuan_hoa(act_moi))
    n_lan, d1_mot = 0, None
    if word_chuan and a0 and a0 in word_chuan:
        # mọi chỗ hiển thị hành động của mục trong bản Word đều mất cụm; Word in hành động ≥ 2 lần thì đo thêm trường
        # hợp chỉ MỘT chỗ mất (K3 khớp cấp TÀI LIỆU — chỗ còn lại vẫn che)
        n_lan = word_chuan.count(a0)
        d0, d1, kieu = word_chuan, word_chuan.replace(a0, a1), "ban_xuat_that"
        d1_mot = word_chuan.replace(a0, a1, 1) if n_lan >= 2 else None
    else:
        d0, d1, kieu = a0, a1, "ban_xuat_tong_hop"
    moi = _sao(it)
    moi["action"] = act_moi
    chung = {"phep": "K3", "truong": "k3", "dich": {"cum": chuan_hoa(x["cum"])}}
    return [
        {**chung, "lop": "K3_rung_ban_xuat", "trong_pham_vi": True, "bien_the": f"{kieu}|{x['nhom']}",
         "mo_ta": f"bản xuất mất «{x['cum']}»", "muc_dot_bien": _sao(it), "ban_xuat_goc": d0, "ban_xuat_dot_bien": d1,
         "ban_xuat_mot_cho": d1_mot, "so_lan_hien_thi": n_lan,
         # hành động đã cắt, đúng dạng nằm trong bản xuất đột biến — để chan_doan_k3 biết cụm nào CỦA K3 bị mất khỏi
         # mục (không dùng cụm của bộ sinh: bộ sinh rộng hơn từ điển K3, quy kết theo nó che lỗ hổng trích cụm)
         "hanh_dong_cat": a1},
        {**chung, "lop": "K3_rung_trong_muc", "trong_pham_vi": False, "bien_the": x["nhom"],
         "mo_ta": f"mục mất «{x['cum']}» (bản xuất trung thành với mục đã đổi)", "muc_dot_bien": moi,
         "ban_xuat_goc": chuan_hoa(act_moi), "ban_xuat_dot_bien": chuan_hoa(act_moi)},
    ]


# ───────────────────────── K4: chiều khuyến cáo ─────────────────────────

_GOC = {"reduced": "reduce", "lowered": "lower", "decreased": "decrease", "improved": "improve",
        "prevented": "prevent", "attenuated": "attenuate", "slowed": "slow", "reduces": "reduce", "lowers": "lower",
        "decreases": "decrease", "improves": "improve", "prevents": "prevent", "slows": "slow"}
_KHONG_PHAI_DONG_TU = (r"(?!\s+(?:ejection|left|renal|kidney|egfr|glomerular|bone|function|lung|exercise|"
                       r"dose|doses|sodium|salt|calorie|fat|intensity|frequency|gfr|cardiac|hepatic|mobility))")
# (tên phép đảo, mẫu, hàm thay). Cố ý gồm cả dạng bộ kiểm CÓ và CHƯA CÓ trong từ điển _NGUOC.
_DAO = (
    ("qua_khu:did_not", re.compile(r"\b(significantly |markedly |substantially )?(reduced|lowered|decreased|improved|"
                                   r"prevented|attenuated|slowed)\b" + _KHONG_PHAI_DONG_TU, re.I),
     lambda m: "did not " + ("significantly " if m.group(1) else "") + _GOC[m.group(2).lower()]),
    ("hien_tai:does_not", re.compile(r"\b(reduces|lowers|decreases|improves|prevents|slows)\b", re.I),
     lambda m: "does not " + _GOC[m.group(1).lower()]),
    ("superior:not", re.compile(r"\b(was|were|is|are) (superior|noninferior|non-inferior) to\b", re.I),
     lambda m: f"{m.group(1)} not {m.group(2)} to"),
    ("recommended:not", re.compile(r"\b(is|are) (strongly |conditionally )?recommended\b", re.I),
     lambda m: f"{m.group(1)} not recommended"),
    ("recommend:against", re.compile(r"\b(we|panel|guideline|uspstf|task force|who|nice) (recommends?|suggests?)\b"
                                     r"(?! against)", re.I),
     lambda m: f"{m.group(1)} {m.group(2)} against"),
    ("should_be:not", re.compile(r"\bshould be (used|offered|given|prescribed|considered|initiated|started|screened)\b",
                                 re.I),
     lambda m: f"should not be {m.group(1)}"),
    ("associated_lower:not", re.compile(r"\b(was|were|is|are) associated with (?:a |an )?(?:significantly )?(lower|"
                                        r"reduced|decreased)\b", re.I),
     lambda m: f"{m.group(1)} not associated with a {m.group(2)}"),
    ("resulted_in:did_not", re.compile(r"\b(resulted in|led to) (?:a |an )?(?:significantly )?(lower|reduced|fewer|"
                                       r"greater)\b", re.I),
     lambda m: f"did not {'result in' if m.group(1).lower() == 'resulted in' else 'lead to'} a {m.group(2)}"),
    ("was_lower:not", re.compile(r"\b(was|were) (?:significantly )?(lower|reduced|decreased)(?= (?:with|in|among|for) )",
                                 re.I),
     lambda m: f"{m.group(1)} not {m.group(2)}"),
    ("effective:not", re.compile(r"\b(is|was|are|were) (?:highly )?(effective|efficacious|beneficial)\b", re.I),
     lambda m: f"{m.group(1)} not {m.group(2)}"),
    ("benefit:no", re.compile(r"\b(showed|demonstrated|provided|conferred|offers?) (?:a |significant |clinical |"
                              r"substantial )?benefits?\b", re.I),
     lambda m: f"{m.group(1)} no benefit"),
)
_KET_LUAN = re.compile(r"conclusions?\s*:|in conclusion|interpretation\s*:|recommendations?\s*:", re.I)


def sinh_k4_nguon(rec: dict, nguon: str, hat: int) -> dict | None:
    """Đảo MỘT mệnh đề tích cực trong thân tóm tắt (ưu tiên phần Kết luận) sang phủ định — mục apply giữ nguyên."""
    than = doan_than(nguon)
    if not than:
        return None
    vung_kl = None
    for a, b in than:
        for m in _KET_LUAN.finditer(nguon, a, b):
            vung_kl = (m.start(), b)
    vung = [vung_kl] if vung_kl else than
    ung_vien = []
    for a, b in vung:
        for ten, mau, ham in _DAO:
            for m in mau.finditer(nguon, a, b):
                ung_vien.append((m.start(), ten, m, ham))
    if not ung_vien:
        return None
    if not vung_kl:                                   # không có phần Kết luận ⇒ chỉ chọn trong đoạn THÂN cuối có mẫu
        cuoi = max(next(i for i, (a, b) in enumerate(than) if a <= x[0] < b) for x in ung_vien)
        a, b = than[cuoi]
        ung_vien = [x for x in ung_vien if a <= x[0] < b]
    r = rng_cho(hat, rec["dashboard"], rec["muc"].get("id"), rec["chi_so"], "K4")
    _, ten, m, ham = r.choice(sorted(ung_vien, key=lambda x: (x[0], x[1])))
    moi = _thay(nguon, m.start(), m.end(), ham(m))
    return {"lop": "K4_nguon_nguoc", "phep": "K4", "truong": "k4", "trong_pham_vi": True, "bien_the": ten,
            "dich": {}, "mo_ta": f"nguồn: «{m.group(0)}» → «{ham(m)}»", "muc_dot_bien": _sao(rec["muc"]),
            "nguon_dot_bien": moi, "vi_tri_nguon": m.start(), "cum_moi": ham(m)}


_TIEN_TO_DAO = ("KHÔNG", "Tránh", "Không nên")


def sinh_k4_muc(rec: dict, nguon: str, hat: int) -> dict:
    """Mục apply đảo sang «không làm» trong khi nguồn ủng hộ (K4 chỉ soi tín hiệu ngược chiều ở NGUỒN)."""
    it = rec["muc"]
    r = rng_cho(hat, rec["dashboard"], it.get("id"), rec["chi_so"], "K4b")
    tien = r.choice(_TIEN_TO_DAO)
    act = _doc_truong(it, "action")
    moi = _sao(it)
    moi["action"] = f"{tien} {act[:1].lower()}{act[1:]}" if act else tien
    return {"lop": "K4_muc_dao", "phep": "K4", "truong": "k4", "trong_pham_vi": False, "bien_the": f"tien_to:{tien}",
            "dich": {}, "mo_ta": f"mục: thêm «{tien}» đầu hành động", "muc_dot_bien": moi, "nguon_dot_bien": nguon}


# ───────────────────────── chẩn đoán lý do lọt ─────────────────────────
# chuan_hoa() của K3 (bộ K1/K2/K4 dùng lại) xoá mọi đoạn «<…>» như thẻ HTML. Bản efetch là VĂN BẢN THUẦN — «<» là dấu so
# sánh («LNM risk < 3 %», «p<0.05») ⇒ cả đoạn tới dấu «>» kế tiếp bị xoá. Mẫu dưới CHÉP đúng mẫu đó để đo phần bị mất.
_THE_GIA = re.compile(r"<[^>]+>")


def vung_bi_cat(raw: str) -> list[tuple[int, int]]:
    """Các đoạn của văn bản THUẦN mà chuan_hoa sẽ xoá (efetch không có thẻ HTML ⇒ mọi đoạn khớp đều là chữ bị mất)."""
    return [m.span() for m in _THE_GIA.finditer(raw or "")]


def chan_doan_nguon(nguon: dict[str, str]) -> dict:
    vung = {p: vung_bi_cat(t) for p, t in nguon.items()}
    return {"so_nguon": len(nguon), "nguon_bi_cat": sum(1 for v in vung.values() if v),
            "nguon_bi_cat_tren_200_ky_tu": sum(1 for v in vung.values() if any(e - s > 200 for s, e in v)),
            "ky_tu_bi_cat": sum(e - s for v in vung.values() for s, e in v),
            "ky_tu_tong": sum(len(t) for t in nguon.values())}


def chan_doan_k3(db: dict, bo: dict) -> dict | None:
    """Đột biến K3 ở bản xuất: K3 THỰC trích bao nhiêu cụm từ hành động của mục (đúng hàm k3_nguon của bộ kiểm), bao
    nhiêu cụm trong đó bị phép cắt làm mất khỏi hành động, và bao nhiêu cụm bị mất vẫn còn ở chỗ khác trong bản xuất
    đột biến (K3 khớp cấp TÀI LIỆU nên vẫn thấy). None khi đột biến không mang hành động đã cắt (không chẩn đoán được)."""
    cat = db.get("hanh_dong_cat")
    if cat is None:
        return None
    cum = [c for n in bo["k3_nguon"]({"summary": {}, "items": [db["muc_dot_bien"]]}) for c in n["cum"]]
    bi_cat = [c for c in cum if c not in cat]
    return {"so_cum_k3": len(cum), "cum_k3_bi_cat": len(bi_cat),
            "cum_k3_bi_cat_con_cho_khac": sum(1 for c in bi_cat if c in db["ban_xuat_dot_bien"])}


def ly_do_lot(db: dict, r: dict | None, nguon_goc: str | None) -> str | None:
    """Giải thích MỘT lần lọt (chỉ để đọc báo cáo — không đổi kết quả chấm)."""
    if db["ket_qua"] in ("bat", "bat_lech") or not db["trong_pham_vi"]:
        return None
    if db["lop"] == "K1_quan_the":
        if db["ket_qua"] == "lot_im":
            return "cach_viet_ngoai_tu_dien"
        ve = next((v for cap in _CAP_K1 for v in cap if v["ten"] == db["dich"]["ve_muc"]), None)
        if ve and nguon_goc:
            mau = rf"(?<!\w)(?:{ve['en']})(?!\w)"
            if not re.search(mau, chuan_hoa(van_ban_than(nguon_goc))) and re.search(mau, chuan_hoa(nguon_goc)):
                return "tu_khoa_chi_o_dong_tac_gia"
        return "khac"
    if db["lop"] == "K4_nguon_nguoc":
        if nguon_goc and any(a <= db.get("vi_tri_nguon", -1) < b for a, b in vung_bi_cat(nguon_goc)):
            return "chuan_hoa_xoa_mat_cau"
        if r and any(chuan_hoa(db.get("cum_moi", "")) in c for c in (r.get("k4") or {}).get("cau_bo_qua") or []):
            return "bo_loc_ket_cuc_phu"
        return "dang_phu_dinh_ngoai_tu_dien"
    if db["lop"] == "K3_rung_ban_xuat":
        # Quy kết theo cụm mà K3 THỰC trích (chan_doan_k3), theo thứ tự: không trích được cụm nào ⇒ dù bản xuất ra sao
        # cũng lọt; mọi cụm K3 trích vẫn nguyên trong hành động đã cắt ⇒ phần bị cắt nằm ngoài cụm K3; chỉ khi cụm K3
        # bị cắt mà còn ở chỗ khác trong bản xuất mới là lỗi so khớp cấp TÀI LIỆU.
        if db["ket_qua"] == "lot_im":
            return "k3_khong_trich_cum"
        cd = db.get("k3_chan_doan")
        if not cd:
            return "khac"
        if not cd["cum_k3_bi_cat"]:
            return "k3_trich_cum_khac"
        if cd["cum_k3_bi_cat_con_cho_khac"]:
            return "cum_con_o_cho_khac_trong_ban_xuat"
        return "khac"
    if db["lop"] in ("K2_nguong", "K2_co_mau"):
        return "nguon_khong_neu" if db["ket_qua"] == "lot_trang" else ("ngoai_tu_dien" if db["ket_qua"] == "lot_im" else "khac")
    return "khac"


# ───────────────────────── chấm ─────────────────────────

def chu_ky_bao(r: dict, phep: str) -> set[str]:
    """Chữ ký các 🟠 của MỘT phép trong kết quả kiem_muc (để biết 🟠 nào là MỚI do đột biến)."""
    ra = set()
    if phep == "K1":
        ra |= {f"cap:{x['ve_muc']}>{x['ve_nguon']}" for x in r.get("k1_cap") or [] if x["muc"] == "can_doc"}
    elif phep == "K2":
        ra |= {f"nguong:{x['chi_so']}:{x['so']}" for x in r.get("k1_nguong") or [] if x["muc"] == "can_doc"}
        ra |= {f"n:{x['so']}" for x in r.get("k2_co_mau") or [] if x["muc"] == "can_doc"}
    elif phep == "K4":
        if (r.get("k4") or {}).get("muc") == "can_doc":
            ra.add("k4")
    return ra


def _muc_dich(db: dict, r: dict) -> str | None:
    """Mức (khop/can_doc/chua_kiem) ở ĐÚNG phần tử bị đột biến; None khi bộ kiểm không sinh dòng nào cho nó."""
    tr, dich = db["truong"], db["dich"]
    if tr == "k1_cap":
        ds = [x["muc"] for x in r.get("k1_cap") or [] if x["ve_muc"] == dich["ve_muc"]]
    elif tr == "k1_nguong":
        ds = [x["muc"] for x in r.get("k1_nguong") or [] if x["chi_so"] == dich["chi_so"]
              and x["so"].replace(",", ".") == dich["so"]]
    elif tr == "k2_co_mau":
        ds = [x["muc"] for x in r.get("k2_co_mau") or [] if x["so"] == dich["so"]]
    else:
        ds = [(r.get("k4") or {}).get("muc")] if r.get("k4") else []
    for muc in ("can_doc", "khop", "chua_kiem"):
        if muc in ds:
            return muc
    return None


def cham_k124(db: dict, r_goc: dict, bo: dict) -> str:
    r = bo["kiem_muc"](db["muc_dot_bien"], db["nguon_dot_bien"])
    db["_r"] = r
    muc = _muc_dich(db, r)
    if muc == "can_doc":
        return "bat"
    if chu_ky_bao(r, db["phep"]) - chu_ky_bao(r_goc, db["phep"]):
        return "bat_lech"
    return {"khop": "lot_xanh", "chua_kiem": "lot_trang"}.get(muc or "", "lot_im")


def cham_k3(db: dict, bo: dict, khoa_dich: str = "ban_xuat_dot_bien") -> str:
    """bat = có cụm K3 CHUYỂN từ ✓ (đối chứng) sang 🟠 (đột biến); K3 không trích được cụm nào ⇒ lot_im."""
    nguon = bo["k3_nguon"]({"summary": {}, "items": [db["muc_dot_bien"]]})
    if not nguon:
        return "lot_im"
    goc = bo["k3_doi_chieu"](nguon, {"ban_xuat": _boc(db["ban_xuat_goc"])})
    moi = bo["k3_doi_chieu"](nguon, {"ban_xuat": _boc(db[khoa_dich])})
    lat = any(g["ket_qua"]["ban_xuat"] == "con" and m["ket_qua"]["ban_xuat"] == "can_doc"
              for g, m in zip(goc["dong"], moi["dong"]))
    return "bat" if lat else "lot_xanh"


# ───────────────────────── đối chứng + sinh + đo ─────────────────────────

def _co_phan_quyet(r: dict, phep: str) -> bool:
    """Phép có phán ✓ hoặc 🟠 cho mục (⚪ / không có dòng = không phán được)."""
    if phep == "K4":
        return bool(r.get("k4"))
    return any(x["muc"] in ("khop", "can_doc") for tr in TRUONG_CUA_PHEP[phep] for x in r.get(tr) or [])


def do_doi_chung(muc: list[dict], nguon: dict[str, str], du_lieu: dict[Path, dict], bo: dict) -> tuple[dict, dict]:
    """(thống kê đối chứng, {khoá mục: kết quả kiem_muc gốc}). Không đột biến gì."""
    ket_qua, dem = {}, {p: {"n": 0, "bao": 0, "phan_quyet": 0} for p in ("K1", "K2", "K4")}
    for rec in muc:
        pm = _pmid(rec["muc"])
        if not pm or pm not in nguon:
            continue
        r = bo["kiem_muc"](rec["muc"], nguon[pm])
        ket_qua[_khoa(rec)] = r
        for p in ("K1", "K2", "K4"):
            dem[p]["n"] += 1
            dem[p]["bao"] += bool(chu_ky_bao(r, p))
            dem[p]["phan_quyet"] += _co_phan_quyet(r, p)
    # mức DASHBOARD — đúng như mã thoát của ④-bis/④-ter: nếu chuyển sang CHẶN thì bao nhiêu bản PASS hôm nay bị chặn
    dash = {"K124": {"n": 0, "bao": 0}, "K3": {"n": 0, "bao": 0, "dong_can_doc": 0, "dong": 0}}
    for f, data in du_lieu.items():
        kd = bo["kiem_dashboard"](data, nguon, False)
        if kd["so_muc_co_nguon"]:
            dash["K124"]["n"] += 1
            dash["K124"]["bao"] += kd["dem"]["can_doc"] > 0
        dich = {"ban_doc": _doc(_duong_ban_doc(f)), "word_html": _doc(_duong_word(f))}
        if any(v is not None for v in dich.values()):
            k3 = bo["k3_doi_chieu"](bo["k3_nguon"](data), dich)
            dash["K3"]["n"] += 1
            dash["K3"]["bao"] += k3["dem"]["can_doc"] > 0
            dash["K3"]["dong_can_doc"] += k3["dem"]["can_doc"]
            dash["K3"]["dong"] += k3["dem"]["can_doc"] + k3["dem"]["con"]
    return {"muc": dem, "dashboard": dash}, ket_qua


def _khoa(rec: dict) -> tuple:
    return (rec["dashboard"], rec["chi_so"])


PHU_BO_SINH: dict[str, dict] = {}   # {lớp: {muc_thu, sinh_duoc}} của lượt sinh gần nhất (bộ sinh phủ được bao nhiêu mục)


def sinh_dot_bien(muc: list[dict], nguon: dict[str, str], goc: dict, hat: int, bo: dict,
                  word: dict[Path, str | None]) -> list[dict]:
    """Mọi đột biến, kèm thông tin mục (dashboard, id, pmid). Điều kiện tiên quyết K4: đối chứng K4 = ✓ (đối
    chứng đã 🟠 thì 🟠 sau đột biến không quy được cho đột biến) và mục không phải khuyến cáo phủ định."""
    ra: list[dict] = []
    phu = PHU_BO_SINH
    phu.clear()

    def thu(ten: str, db):
        o = phu.setdefault(ten, {"muc_thu": 0, "sinh_duoc": 0})
        o["muc_thu"] += 1
        o["sinh_duoc"] += bool(db)
        return db

    for rec in muc:
        it = rec["muc"]
        pm = _pmid(it)
        src = nguon.get(pm) if pm else None
        ds: list[dict | None] = []
        if src is not None:
            ds += [thu("K1_quan_the", sinh_k1(rec, src, hat)), thu("K2_nguong", sinh_k2_nguong(rec, src, hat)),
                   thu("K2_nguong_hanh_dong", sinh_k2_nguong(rec, src, hat, truong_hanh_dong=True)),
                   thu("K2_co_mau", sinh_k2_co_mau(rec, src, hat))]
            r0 = goc.get(_khoa(rec)) or {}
            if (r0.get("k4") or {}).get("muc") == "khop" and not bo["muc_phu_dinh"](it):
                ds += [thu("K4_nguon_nguoc", sinh_k4_nguon(rec, src, hat)), thu("K4_muc_dao", sinh_k4_muc(rec, src, hat))]
        k3 = sinh_k3(rec, hat, word.get(rec["duong_dan"]))
        thu("K3", k3)
        ds += k3
        for db in ds:
            if db and db["phep"] != "K3" and _nfc_json(db["muc_dot_bien"]) == _nfc_json(it) \
                    and db["nguon_dot_bien"] == src:
                continue                               # phép biến đổi không đổi được gì ⇒ không phải đột biến
            if db:
                db.update({"dashboard": rec["dashboard"], "id": it.get("id"), "pmid": pm, "_khoa": _khoa(rec)})
                ra.append(db)
    return ra


def cham_tat_ca(dot_bien: list[dict], goc: dict, bo: dict, nguon: dict[str, str] | None = None) -> None:
    for db in dot_bien:
        db["ket_qua"] = cham_k3(db, bo) if db["phep"] == "K3" else cham_k124(db, goc.get(db["_khoa"]) or {}, bo)
        if db.get("ban_xuat_mot_cho"):
            db["ket_qua_mot_cho"] = cham_k3(db, bo, "ban_xuat_mot_cho")
        if db["lop"] == "K3_rung_ban_xuat":
            db["k3_chan_doan"] = chan_doan_k3(db, bo)
        db["ly_do_lot"] = ly_do_lot(db, db.pop("_r", None), (nguon or {}).get(db.get("pmid") or ""))


def _o(ds: list[dict]) -> dict:
    n = len(ds)
    dem = {k: sum(1 for d in ds if d["ket_qua"] == k) for k in KQ}
    ktc = wilson(dem["bat"], n)
    ktc_rong = wilson(dem["bat"] + dem["bat_lech"], n)
    return {"n": n, **dem, "do_nhay": (dem["bat"] / n) if n else None, "ktc95": ktc,
            "do_nhay_rong": ((dem["bat"] + dem["bat_lech"]) / n) if n else None, "ktc95_rong": ktc_rong}


def tong_hop(dot_bien: list[dict]) -> dict:
    theo_lop, theo_bien_the, theo_phep = {}, {}, {}
    for db in dot_bien:
        theo_lop.setdefault(db["lop"], []).append(db)
        theo_bien_the.setdefault((db["lop"], db["bien_the"]), []).append(db)
        if db["trong_pham_vi"]:
            theo_phep.setdefault(db["phep"], []).append(db)
    k3 = theo_lop.get("K3_rung_ban_xuat", [])
    lot_k3 = [d for d in k3 if d["ket_qua"] != "bat"]
    hai_cho = [d for d in k3 if d.get("ket_qua_mot_cho")]
    # Lý do lọt K3 quy theo cụm K3 THỰC trích (ly_do_lot/chan_doan_k3), không theo cụm của bộ sinh.
    ld_k3 = {k: sum(1 for d in lot_k3 if d.get("ly_do_lot") == k)
             for k in ("k3_khong_trich_cum", "k3_trich_cum_khac", "cum_con_o_cho_khac_trong_ban_xuat")}
    bat_k3 = sum(1 for d in k3 if d["ket_qua"] == "bat")
    cap_tl = ld_k3["cum_con_o_cho_khac_trong_ban_xuat"]
    k3_phu = {"n": len(k3), "bat": bat_k3, "lot": len(lot_k3),
              "lot_k3_khong_trich_cum": ld_k3["k3_khong_trich_cum"],
              "lot_k3_trich_cum_khac": ld_k3["k3_trich_cum_khac"],
              "lot_do_khop_cap_tai_lieu": cap_tl,
              "lot_khac": len(lot_k3) - sum(ld_k3.values()),
              # CẬN TRÊN nếu K3 so theo TỪNG MỤC: chỉ thu hồi được các ca khớp cấp tài liệu; lọt do trích cụm vẫn lọt
              "do_nhay_neu_so_theo_tung_muc": (bat_k3 + cap_tl) / len(k3) if k3 else None,
              "ktc95_neu_so_theo_tung_muc": wilson(bat_k3 + cap_tl, len(k3)),
              "hien_thi_tu_2_lan": len(hai_cho),
              "mot_cho_mat_van_bat": sum(1 for d in hai_cho if d["ket_qua_mot_cho"] == "bat"),
              "theo_nhom_dau": {}}
    for d in k3:
        nhom = d["bien_the"].split("|")[-1].split(":")[0]
        o = k3_phu["theo_nhom_dau"].setdefault(nhom, {"n": 0, "bat": 0})
        o["n"] += 1
        o["bat"] += d["ket_qua"] == "bat"
    for o in k3_phu["theo_nhom_dau"].values():
        o["do_nhay"], o["ktc95"] = o["bat"] / o["n"], wilson(o["bat"], o["n"])
    # K1: tách cách viết CÓ / KHÔNG có trong từ điển bộ kiểm (nhãn cấu trúc của bộ sinh) — lỗ hổng từ vựng ≠ cơ chế
    k1 = theo_phep.get("K1", [])
    k1_phu = {"trong_tu_dien": _o([d for d in k1 if d.get("tu_dien_bo_kiem") is True]),
              "ngoai_tu_dien": _o([d for d in k1 if d.get("tu_dien_bo_kiem") is False])}
    ly_do: dict[str, dict[str, int]] = {}
    for db in dot_bien:
        if db.get("ly_do_lot"):
            o = ly_do.setdefault(db["lop"], {})
            o[db["ly_do_lot"]] = o.get(db["ly_do_lot"], 0) + 1
    return {
        "ly_do_lot": ly_do,
        "k1_phu": k1_phu,
        "k3_phu": k3_phu,
        "theo_phep_trong_pham_vi": {p: _o(theo_phep.get(p, [])) for p in PHEP},
        "theo_lop": {k: {**_o(v), "phep": v[0]["phep"], "trong_pham_vi": v[0]["trong_pham_vi"]}
                     for k, v in sorted(theo_lop.items())},
        "theo_bien_the": [{"lop": k[0], "bien_the": k[1], **_o(v)} for k, v in sorted(theo_bien_the.items())],
    }


def do_tat_ca(thu_muc: Path, *, hat: int, nguon_fn, bo: dict | None = None, da_pass=None, doc=None) -> dict:
    bo = bo or bo_kiem_that()
    doc = doc or _k3().doc_data
    dashboards = chon_dashboard(thu_muc, da_pass)
    du_lieu = {}
    for f in dashboards:
        d = doc(f)
        if d:
            du_lieu[f] = d
    muc = lay_muc_apply(du_lieu)
    pmids = sorted({p for d in du_lieu.values() for it in d.get("items") or []
                    if isinstance(it, dict) and it.get("decision") == "apply" for p in [_pmid(it)] if p})
    nguon, tk_nguon = nguon_fn(pmids)
    doi_chung, goc = do_doi_chung(muc, nguon, du_lieu, bo)
    word = {f: (gon_dau(chuan_hoa(w)) if (w := _doc(_duong_word(f))) else None) for f in du_lieu}
    dot_bien = sinh_dot_bien(muc, nguon, goc, hat, bo, word)
    cham_tat_ca(dot_bien, goc, bo, nguon)
    return {"so_dashboard_pass": len(dashboards), "so_dashboard_doc_duoc": len(du_lieu), "so_muc_apply": len(muc),
            "so_muc_co_nguon": sum(1 for rec in muc if _pmid(rec["muc"]) in nguon), "nguon": tk_nguon,
            "chan_doan_nguon": chan_doan_nguon(nguon),
            "doi_chung": doi_chung, "tong_hop": tong_hop(dot_bien), "dot_bien": dot_bien,
            "phu_bo_sinh": copy.deepcopy(PHU_BO_SINH),
            "dashboards": [f.name for f in du_lieu]}


# ───────────────────────── báo cáo ─────────────────────────

def _bam_tep(ten: str) -> str:
    try:
        return hashlib.sha256((Path(__file__).resolve().parent / ten).read_bytes()).hexdigest()[:16]
    except OSError:
        return "?"


def ban_json(kq: dict, *, hat: int, ngay: str) -> dict:
    """Bản ghi báo cáo — KHÔNG chứa văn bản nguồn (tóm tắt có bản quyền), chỉ định danh + mô tả phép biến đổi."""
    return {
        "_mo_ta": "Độ nhạy K1–K4 đo bằng ĐỘT BIẾN TỔNG HỢP có nhãn theo cấu trúc (tools/do_nhay_kiem_ngu_nghia.py). "
                  "KHÔNG thay bộ vàng do bác sĩ gắn nhãn; KHÔNG tự đổi chế độ chặn (quyết định của bác sĩ). "
                  "Báo động trên đối chứng là CẬN TRÊN của báo động giả (mục thật chưa gắn nhãn).",
        "ngay": ngay, "hat_giong": hat,
        "ma_bo_kiem_sha256_16": {t: _bam_tep(t) for t in ("kiem_cheo_ngu_nghia.py", "kiem_quan_the_chieu.py",
                                                          "do_nhay_kiem_ngu_nghia.py")},
        "du_lieu": {k: kq[k] for k in ("so_dashboard_pass", "so_dashboard_doc_duoc", "so_muc_apply",
                                       "so_muc_co_nguon", "nguon")},
        "chan_doan_nguon": kq.get("chan_doan_nguon", {}),
        "doi_chung": kq["doi_chung"], "tong_hop": kq["tong_hop"], "phu_bo_sinh": kq.get("phu_bo_sinh", {}),
        "_ghi_chu_dot_bien_lot": "Chỉ liệt kê đột biến TRONG phạm vi thiết kế mà phép kiểm BỎ LỌT (phần cần hành động); số bắt/"
                                 "lọt đầy đủ ở tong_hop. Danh sách đầy đủ: chạy lại công cụ với --json (cùng dữ liệu, cùng hạt giống).",
        "dot_bien_lot": [{"lop": d["lop"], "bien_the": d["bien_the"], "dashboard": d["dashboard"], "id": d["id"],
                      "pmid": d["pmid"], "mo_ta": d["mo_ta"][:160], "ket_qua": d["ket_qua"],
                      **({"k3_chan_doan": d["k3_chan_doan"]} if d.get("k3_chan_doan") else {}),
                      **({"ket_qua_mot_cho": d["ket_qua_mot_cho"]} if d.get("ket_qua_mot_cho") else {}),
                      **({"ly_do_lot": d["ly_do_lot"]} if d.get("ly_do_lot") else {})}
                         for d in kq["dot_bien"] if d["trong_pham_vi"] and d["ket_qua"] not in ("bat", "bat_lech")],
        "dashboards": kq["dashboards"],
    }


def json_gon(bj: dict) -> str:
    """JSON đọc được + diff được: phần đầu thụt dòng, mỗi đột biến lọt nằm trên MỘT dòng."""
    dau = {k: v for k, v in bj.items() if k != "dot_bien_lot"}
    hang = ",\n".join("  " + json.dumps(r, ensure_ascii=False) for r in bj.get("dot_bien_lot") or [])
    s = json.dumps(dau, ensure_ascii=False, indent=1)
    return s[:-2] + ',\n "dot_bien_lot": [\n' + hang + ("\n" if hang else "") + " ]\n}\n"


def _pt(x) -> str:
    return "CHƯA ĐO" if x is None else f"{x:.0%}"


def _ktc(x) -> str:
    return "—" if not x else f"{x[0]:.0%}–{x[1]:.0%}"


_TEN_LOP = {
    "K1_quan_the": "K1 · đổi nhãn quần thể (thay/chèn vế loại trừ)",
    "K2_nguong": "K2 · đổi ngưỡng số trong quần thể (EF/eGFR/tuổi/HbA1c/BMI/LDL)",
    "K2_co_mau": "K2 · đổi/chèn cỡ mẫu n=",
    "K2_nguong_hanh_dong": "K2 · đổi ngưỡng số nằm trong HÀNH ĐỘNG",
    "K3_rung_ban_xuat": "K3 · rụng điều kiện ở BẢN XUẤT (mục giữ nguyên)",
    "K3_rung_trong_muc": "K3 · rụng điều kiện NGAY TRONG MỤC so với nguồn",
    "K4_nguon_nguoc": "K4 · nguồn nói NGƯỢC chiều mục apply",
    "K4_muc_dao": "K4 · MỤC đảo sang «không làm» khi nguồn ủng hộ",
}
_LY_DO_NGOAI = {
    "K2_nguong_hanh_dong": "K1/K2 chỉ đọc population/pico.P/title — không đọc action.",
    "K3_rung_trong_muc": "K3 so BẢN XUẤT với MỤC, không so MỤC với nguồn ⇒ cụm đã rụng khỏi mục thì không còn gì để so.",
    "K4_muc_dao": "K4 chỉ tìm tín hiệu ngược chiều trong NGUỒN; mục nói «không làm» còn được coi là cùng chiều nguồn.",
}


_TEN_LY_DO = {
    "cach_viet_ngoai_tu_dien": "cách viết tiếng Việt của nhãn không có trong từ điển bộ kiểm",
    "tu_khoa_chi_o_dong_tac_gia": "từ khoá vế đổi sang chỉ có ở DÒNG TÁC GIẢ/cơ quan (vd «Children's Hospital») ⇒ bộ kiểm "
                                  "tưởng nguồn có nêu",
    "chuan_hoa_xoa_mat_cau": "câu đã đảo nằm trong đoạn chuan_hoa xoá như thẻ HTML («<» so sánh … «>»)",
    "bo_loc_ket_cuc_phu": "câu đã đảo bị bộ lọc «kết cục phụ» bỏ qua (vd «secondary analysis», «secondary prevention»)",
    "dang_phu_dinh_ngoai_tu_dien": "dạng phủ định không có trong từ điển K4 (thì hiện tại, «not effective», «did not result in»…)",
    "cum_con_o_cho_khac_trong_ban_xuat": "cụm K3 trích được bị cắt khỏi hành động nhưng còn ở chỗ khác trong bản xuất ⇒ "
                                         "K3 khớp cấp tài liệu vẫn thấy",
    "k3_khong_trich_cum": "K3 không trích được cụm điều kiện nào từ hành động",
    "k3_trich_cum_khac": "mọi cụm K3 trích được vẫn nguyên trong hành động đã cắt (phần bị cắt nằm ngoài cụm của K3)",
    "nguon_khong_neu": "nguồn không nêu ⇒ ⚪",
    "ngoai_tu_dien": "bộ kiểm không trích được con số",
}


def _rieng_tu_dien(th: dict, p: str) -> dict | None:
    """Độ nhạy riêng phần NẰM TRONG từ điển bộ kiểm (nhãn cấu trúc của bộ sinh): K1 = cách viết bộ kiểm nhận được,
    K3 = nhóm dấu điều kiện có trong từ điển K3 (`dau_k3`). K2/K4 không tách ⇒ None."""
    if p == "K1":
        o = (th.get("k1_phu") or {}).get("trong_tu_dien")
    elif p == "K3":
        o = ((th.get("k3_phu") or {}).get("theo_nhom_dau") or {}).get("dau_k3")
    else:
        o = None
    return o if o and o.get("n") else None


def _o_rieng(o: dict | None) -> str:
    return "—" if not o else f"{_pt(o['do_nhay'])} ({_ktc(o['ktc95'])}; {o['bat']}/{o['n']})"


def ban_md(bj: dict) -> str:
    d, dc, th = bj["du_lieu"], bj["doi_chung"], bj["tong_hop"]
    ngay = bj["ngay"]
    ngay_vn = f"{ngay[6:8]}/{ngay[4:6]}/{ngay[:4]}" if len(ngay) == 8 else ngay
    L = [f"# Độ nhạy kiểm chéo ngữ nghĩa K1–K4 — đột biến tổng hợp ({ngay_vn})", "",
         "> **Đột biến TỔNG HỢP có nhãn theo cấu trúc — KHÔNG thay bộ vàng do bác sĩ gắn nhãn.** Công cụ không đổi "
         "chế độ chặn; chuyển K1–K4 từ CẢNH BÁO sang CHẶN là quyết định của bác sĩ (audit/16 §4). "
         "Báo động trên đối chứng là CẬN TRÊN của báo động giả: mục thật chưa được gắn nhãn đúng/sai.", "",
         f"Sinh bởi `tools/do_nhay_kiem_ngu_nghia.py` · hạt giống {bj['hat_giong']} · băm mã (16 ký tự đầu): "
         + ", ".join(f"`{k}` {v}" for k, v in bj["ma_bo_kiem_sha256_16"].items()) + ".", "",
         "## Tóm tắt", "",
         "- Độ nhạy trong phạm vi thiết kế: " + " · ".join(
             f"{p} {_pt(th['theo_phep_trong_pham_vi'][p]['do_nhay'])} (n={th['theo_phep_trong_pham_vi'][p]['n']}"
             + (f"; riêng phần trong từ điển bộ kiểm {_pt(r['do_nhay'])} [KTC {_ktc(r['ktc95'])}; {r['bat']}/{r['n']}]"
                if (r := _rieng_tu_dien(th, p)) else "") + ")"
             for p in PHEP) + ".",
         "- Số gộp tính cả cách viết/dấu điều kiện mà bộ sinh CỐ Ý chọn ngoài từ điển bộ kiểm (đo lỗ hổng từ vựng); "
         "«riêng phần trong từ điển» = K1 với cách viết bộ kiểm nhận được, K3 với nhóm dấu có trong từ điển K3 "
         "(`dau_k3`) — phần còn lọt ở đó là lỗ hổng CƠ CHẾ, không phải từ vựng.",
         "- Lớp lỗi NGOÀI phạm vi thiết kế (không phép nào được thiết kế để bắt): " + " · ".join(
             f"{_TEN_LOP.get(k, k)} {o['bat']}/{o['n']}" for k, o in th["theo_lop"].items() if not o["trong_pham_vi"]) + ".",
         f"- Đối chứng mức dashboard — nếu chuyển sang CHẶN: K1/K2/K4 chặn {dc['dashboard']['K124']['bao']}/"
         f"{dc['dashboard']['K124']['n']} dashboard đã PASS, K3 chặn {dc['dashboard']['K3']['bao']}/{dc['dashboard']['K3']['n']}.",
         "",
         "## Dữ liệu", "",
         f"- Dashboard ĐÃ PASS (bản mới nhất mỗi chủ đề): {d['so_dashboard_pass']} (đọc được DATA: "
         f"{d['so_dashboard_doc_duoc']}).",
         f"- Mục `apply` sau khử trùng: {d['so_muc_apply']} · có tóm tắt PubMed để K1/K2/K4 đọc: {d['so_muc_co_nguon']}.",
         f"- Tóm tắt: cần {d['nguon']['can']} PMID · có sẵn trong bộ đệm {d['nguon']['co_san']} · tải mới "
         f"{d['nguon']['tai_moi']} · tải hỏng {d['nguon']['tai_hong']}.",
         "- Bộ sinh phủ được (mục đủ điều kiện tiên quyết / mục đã thử): " + " · ".join(
             f"{k} {v['sinh_duoc']}/{v['muc_thu']}" for k, v in sorted((bj.get("phu_bo_sinh") or {}).items())) + ".", "",
         "## 1. Độ nhạy theo phép (chỉ đột biến TRONG phạm vi thiết kế của phép)", "",
         "| Phép | n đột biến | Bắt đúng chỗ | Độ nhạy (KTC 95% Wilson) | Riêng phần trong từ điển bộ kiểm (KTC 95%; bắt/n) "
         "| Kể cả 🟠 lệch chỗ | Lọt ✓ (trấn an sai) | Lọt ⚪ | Lọt im |",
         "|---|---|---|---|---|---|---|---|---|"]
    for p in PHEP:
        o = th["theo_phep_trong_pham_vi"][p]
        L.append(f"| {p} | {o['n']} | {o['bat']} | {_pt(o['do_nhay'])} ({_ktc(o['ktc95'])}) | "
                 f"{_o_rieng(_rieng_tu_dien(th, p))} | "
                 f"{_pt(o['do_nhay_rong'])} ({_ktc(o['ktc95_rong'])}) | {o['lot_xanh']} | {o['lot_trang']} | {o['lot_im']} |")
    L += ["", "## 2. Theo lớp đột biến", "",
          "| Lớp | Phạm vi thiết kế | n | Bắt | Độ nhạy (KTC 95%) | Lọt ✓ | Lọt ⚪ | Lọt im |", "|---|---|---|---|---|---|---|---|"]
    for k, o in th["theo_lop"].items():
        L.append(f"| {_TEN_LOP.get(k, k)} | {'trong' if o['trong_pham_vi'] else '**ngoài**'} | {o['n']} | {o['bat']} | "
                 f"{_pt(o['do_nhay'])} ({_ktc(o['ktc95'])}) | {o['lot_xanh']} | {o['lot_trang']} | {o['lot_im']} |")
    ngoai = [k for k, o in th["theo_lop"].items() if not o["trong_pham_vi"]]
    if ngoai:
        L += ["", "Lớp **ngoài phạm vi thiết kế** đo lỗ hổng — không tính vào độ nhạy của phép ở bảng 1:"]
        L += [f"- {_TEN_LOP.get(k, k)}: {_LY_DO_NGOAI.get(k, '')}" for k in ngoai]
    kp = th.get("k3_phu") or {}
    if kp:
        nhom = ", ".join(f"{k} {v['bat']}/{v['n']} ({_pt(v['do_nhay'])}; KTC {_ktc(v['ktc95'])})"
                         for k, v in sorted(kp["theo_nhom_dau"].items()))
        trich = kp["lot_k3_khong_trich_cum"] + kp["lot_k3_trich_cum_khac"]
        so_sanh = ("lớn hơn" if trich > kp["lot_do_khop_cap_tai_lieu"]
                   else "nhỏ hơn" if trich < kp["lot_do_khop_cap_tai_lieu"] else "bằng")
        L += ["", "**K3 — phân tích thêm (rụng ở bản xuất):**",
              f"- Bắt theo nhóm dấu điều kiện của bộ sinh: {nhom} (`dau_k3` = dấu có trong từ điển K3; `dau_khac` = "
              "giới hạn quần thể/điều kiện ngoài từ điển; `nguong_so` = ngưỡng số đứng trần, không có «nếu/khi»).",
              f"- {kp['lot']} lần lọt, quy theo cụm mà K3 THỰC trích từ hành động (không theo cụm của bộ sinh): "
              f"{kp['lot_k3_khong_trich_cum']} lần K3 không trích được cụm nào · {kp['lot_k3_trich_cum_khac']} lần mọi cụm "
              f"K3 trích vẫn nguyên trong hành động đã cắt (phần bị cắt nằm ngoài cụm của K3) · "
              f"{kp['lot_do_khop_cap_tai_lieu']} lần cụm K3 bị cắt khỏi hành động nhưng còn ở chỗ khác trong bản xuất "
              f"(K3 khớp cấp TÀI LIỆU, không biết cụm thuộc mục nào)"
              + (f" · {kp['lot_khac']} lần khác" if kp.get("lot_khac") else "") + ".",
              f"- Độ nhạy TỐI ĐA nếu K3 so theo TỪNG MỤC (bắt + ca khớp cấp tài liệu, trên cùng n = {kp['n']}): "
              f"{_pt(kp.get('do_nhay_neu_so_theo_tung_muc'))} ({_ktc(kp.get('ktc95_neu_so_theo_tung_muc'))}). Lỗ hổng "
              f"trích cụm/từ vựng ({trich}/{kp['lot']} lần lọt) {so_sanh} lỗ hổng so khớp cấp tài liệu "
              f"({kp['lot_do_khop_cap_tai_lieu']}/{kp['lot']}).",
              f"- {kp['hien_thi_tu_2_lan']} đột biến có hành động hiển thị ≥ 2 lần nguyên văn trong Word; nếu chỉ MỘT chỗ mất "
              f"cụm thì K3 bắt {kp['mot_cho_mat_van_bat']}/{kp['hien_thi_tu_2_lan']}."]
    k1p = th.get("k1_phu") or {}
    if k1p.get("trong_tu_dien", {}).get("n") or k1p.get("ngoai_tu_dien", {}).get("n"):
        t, n = k1p["trong_tu_dien"], k1p["ngoai_tu_dien"]
        L += ["", "**K1 — tách từ vựng khỏi cơ chế:**",
              f"- Cách viết bộ kiểm NHẬN được (hỏi thẳng `kiem_cap` thật): {_o_rieng(t)} · cách viết NGOÀI từ điển: "
              f"{_o_rieng(n)}."]
    ld = th.get("ly_do_lot") or {}
    if ld:
        L += ["", "**Lý do lọt (trong phạm vi thiết kế):**", "", "| Lớp | Lý do | Số lần |", "|---|---|---|"]
        for lop, o in sorted(ld.items()):
            for k, v in sorted(o.items(), key=lambda x: -x[1]):
                L.append(f"| {lop} | {_TEN_LY_DO.get(k, k)} | {v} |")
    L += ["", "## 3. Theo biến thể (dạng bề mặt) — lỗ hổng từ vựng", "",
          "| Lớp | Biến thể | n | Bắt | Độ nhạy (KTC 95%) | Lọt |", "|---|---|---|---|---|---|"]
    for o in th["theo_bien_the"]:
        lot = o["lot_xanh"] + o["lot_trang"] + o["lot_im"]
        L.append(f"| {o['lop']} | `{o['bien_the']}` | {o['n']} | {o['bat']} | {_pt(o['do_nhay'])} ({_ktc(o['ktc95'])}) | {lot} |")
    L += ["", "## 4. Đối chứng KHÔNG đột biến (cận trên báo động giả)", "",
          "| Phép | Mục có nguồn | Mục có 🟠 | Tỉ lệ (KTC 95%) | Mục phép phán được ✓/🟠 |", "|---|---|---|---|---|"]
    for p in ("K1", "K2", "K4"):
        o = dc["muc"][p]
        L.append(f"| {p} | {o['n']} | {o['bao']} | {_pt(o['bao'] / o['n'] if o['n'] else None)} "
                 f"({_ktc(wilson(o['bao'], o['n']))}) | {o['phan_quyet']} ({_pt(o['phan_quyet'] / o['n'] if o['n'] else None)}) |")
    k124, k3 = dc["dashboard"]["K124"], dc["dashboard"]["K3"]
    L += ["", "Mức DASHBOARD (đúng như mã thoát bước ④-bis/④-ter — nếu chuyển sang CHẶN, bao nhiêu bản đã PASS hôm nay "
          "sẽ bị chặn):", "",
          f"- K1/K2/K4 (bộ đệm tóm tắt, ngoại tuyến): {k124['bao']}/{k124['n']} dashboard có ≥1 🟠 "
          f"({_pt(k124['bao'] / k124['n'] if k124['n'] else None)}).",
          f"- K3 (bản đọc + Word HTML thật): {k3['bao']}/{k3['n']} dashboard có ≥1 🟠 · {k3['dong_can_doc']}/{k3['dong']} "
          "dòng cụm-điều-kiện × sản phẩm là 🟠.", "",
          ""]
    cd = bj.get("chan_doan_nguon") or {}
    if cd.get("so_nguon"):
        L += ["## Phát hiện phụ — chuẩn hoá nguồn làm mất chữ", "",
              f"`chuan_hoa()` (K3, được K1/K2/K4 dùng lại) xoá mọi đoạn «<…>» như thẻ HTML. Bản tóm tắt efetch là văn bản THUẦN, "
              f"«<» là dấu so sánh ⇒ chữ tới dấu «>» kế tiếp bị xoá trước khi K1/K2/K4 đọc: {cd['nguon_bi_cat']}/{cd['so_nguon']} "
              f"nguồn bị cắt, {cd['nguon_bi_cat_tren_200_ky_tu']} nguồn mất đoạn > 200 ký tự, tổng {cd['ky_tu_bi_cat']:,} / "
              f"{cd['ky_tu_tong']:,} ký tự. Đoạn bị xoá có thể chứa đúng câu «not recommended» mà K4 cần thấy.", ""]
    L += ["## Cách đọc và giới hạn", "",
          "- «Bắt đúng chỗ» = trường đích của phép chuyển 🟠; «🟠 lệch chỗ» = phép có 🟠 MỚI nhưng ở phần tử khác; "
          "«Lọt ✓» = phép báo khớp trên mục đã bị làm sai (nguy hiểm nhất); «Lọt ⚪» = phép nói chưa kiểm được; "
          "«Lọt im» = phép không sinh dòng nào cho phần bị đổi (từ điển/phạm vi không với tới).",
          "- Nhãn lỗi theo CẤU TRÚC: máy biết đã đổi gì; điều kiện tiên quyết bảo đảm bản gốc khớp nguồn (ngưỡng/cỡ mẫu/"
          "nhãn có trong thân tóm tắt) và giá trị mới không có trong nguồn. K4: chỉ đột biến mục mà đối chứng K4 = ✓.",
          "- Danh mục của bộ sinh cố ý rộng hơn từ điển bộ kiểm (cách viết tiếng Việt khác, dạng động từ hiện tại, "
          "dấu điều kiện ngoài danh sách K3) — vì vậy độ nhạy phản ánh cả lỗ hổng từ vựng, không chỉ cơ chế.",
          "- Đột biến tổng hợp ≠ lỗi thật: lỗi do người/agent soạn có thể tinh vi hơn (diễn đạt lại, sai một phần). "
          "Tóm tắt PubMed không phải toàn văn. Khử trùng theo bản PASS mới nhất mỗi chủ đề.",
          "- Báo cáo không chép văn bản nguồn; tóm tắt nằm ở bộ đệm ngoài git.", "",
          "_Cần bác sĩ kiểm chứng._", ""]
    return "\n".join(L)


def in_tom_tat(bj: dict) -> None:
    d, th = bj["du_lieu"], bj["tong_hop"]
    print(f"ĐỘ NHẠY K1–K4 (đột biến tổng hợp, hạt giống {bj['hat_giong']}) — {d['so_dashboard_pass']} dashboard PASS · "
          f"{d['so_muc_apply']} mục apply · {d['so_muc_co_nguon']} có tóm tắt")
    for p in PHEP:
        o = th["theo_phep_trong_pham_vi"][p]
        print(f"  {p}: n={o['n']} · bắt {o['bat']} · độ nhạy {_pt(o['do_nhay'])} (KTC95 {_ktc(o['ktc95'])}) · "
              f"lọt ✓ {o['lot_xanh']} · ⚪ {o['lot_trang']} · im {o['lot_im']}")
    for k, o in th["theo_lop"].items():
        if not o["trong_pham_vi"]:
            print(f"  [ngoài phạm vi] {k}: n={o['n']} · bắt {o['bat']} ({_pt(o['do_nhay'])})")
    dc = bj["doi_chung"]["muc"]
    print("  Đối chứng (cận trên báo động giả): " + " · ".join(
        f"{p} {dc[p]['bao']}/{dc[p]['n']}" for p in ("K1", "K2", "K4")))
    print("  Đột biến TỔNG HỢP — không thay bộ vàng; không tự đổi chế độ chặn. Cần bác sĩ kiểm chứng.")


def ma_thoat(th: dict) -> int:
    so = [th["theo_phep_trong_pham_vi"][p]["n"] for p in PHEP]
    if not any(so):
        return 2
    return 0 if all(so) else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Đo độ nhạy K1–K4 bằng đột biến tổng hợp (chỉ đo, không chặn)")
    ap.add_argument("--thu-muc", help="thư mục dashboard (mặc định EBM-Dashboards/)")
    ap.add_argument("--bo-dem", help="bộ đệm tóm tắt PubMed (mặc định EBM-Dashboards/derivatives/"
                                     "do-nhay-ngu-nghia-nguon.json, ngoài git)")
    ap.add_argument("--online", action="store_true", help="tải tóm tắt còn thiếu bằng kiem_so_lieu.lay_tom_tat")
    ap.add_argument("--toi-da-tai", type=int, help="trần số PMID tải mới mỗi lượt")
    ap.add_argument("--hat-giong", type=int, default=HAT_GIONG_MAC_DINH)
    ap.add_argument("--ngay", help="YYYYMMDD cho tên báo cáo (mặc định hôm nay)")
    ap.add_argument("--bao-cao", help="thư mục ghi báo cáo (mặc định quality/eval/kiem-cheo-ngu-nghia/)")
    ap.add_argument("--ghi", action="store_true", help="ghi báo cáo .json + .md (mặc định chạy khô)")
    ap.add_argument("--json", action="store_true", help="in bản JSON ra stdout")
    a = ap.parse_args(argv)

    goc = goc_du_lieu("EBM-Dashboards")
    thu_muc = Path(a.thu_muc) if a.thu_muc else goc
    if not thu_muc.is_dir():
        print(f"⚪ Không thấy thư mục dashboard {thu_muc.as_posix()} (EBM-Dashboards/ nằm ngoài git) — không đo được.")
        return 2
    tep_dem = Path(a.bo_dem) if a.bo_dem else thu_muc / "derivatives" / "do-nhay-ngu-nghia-nguon.json"
    tep_bo_vang = thu_muc / "derivatives" / "bo-vang-ngu-nghia-nguon.json"

    def nguon_fn(pmids):
        return nap_nguon(pmids, tep_dem=tep_dem, tep_them=(tep_bo_vang,), online=a.online, toi_da=a.toi_da_tai)

    kq = do_tat_ca(thu_muc, hat=a.hat_giong, nguon_fn=nguon_fn)
    if not kq["so_muc_apply"]:
        print(f"⚪ Không có mục apply nào từ dashboard đã PASS trong {thu_muc.as_posix()} — không đo được.")
        return 2
    ngay = a.ngay or dt.date.today().strftime("%Y%m%d")
    bj = ban_json(kq, hat=a.hat_giong, ngay=ngay)
    if a.json:
        print(json.dumps(bj, ensure_ascii=False, indent=1))
    else:
        in_tom_tat(bj)
    if a.ghi:
        ra = Path(a.bao_cao) if a.bao_cao else THU_MUC_BAO_CAO
        ra.mkdir(parents=True, exist_ok=True)
        tj, tm = ra / f"do-nhay-dot-bien-{ngay}.json", ra / f"do-nhay-dot-bien-{ngay}.md"
        tj.write_text(json_gon(bj), encoding="utf-8", newline="\n")
        tm.write_text(ban_md(bj), encoding="utf-8", newline="\n")
        print(f"✓ Đã ghi {tj.as_posix()} + {tm.name}", file=sys.stderr if a.json else sys.stdout)
    else:
        print("(chạy khô — thêm --ghi để ghi báo cáo)", file=sys.stderr if a.json else sys.stdout)
    return ma_thoat(kq["tong_hop"])


if __name__ == "__main__":
    raise SystemExit(main())
