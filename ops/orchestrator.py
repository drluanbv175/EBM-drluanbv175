#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ORCHESTRATOR MỘT CỬA cho dây chuyền chứng cứ — LÔ 4 PHA 2 (15/08/2026); viết lại 20/09/2026 (T1-01…T1-14).

Driver MỎNG: gọi các hiện thân A2→B5 ĐÚNG THỨ TỰ, dừng đúng chỗ khi một bước FAIL, ghi log máy đọc được
— và KHÔNG chứa một dòng logic y khoa nào. Mọi phán đoán nằm trong từng công cụ (chúng đã có cổng riêng);
mọi quyết định lâm sàng nằm ở bác sĩ (Cổng A/B, I4).

Vì sao B1 (dựng dashboard) là "PHIÊN LÀM VIỆC" chứ không phải lệnh: dựng nội dung lâm sàng cần skill
`cap-nhat-chung-cu-y-khoa` + bác sĩ chốt phạm vi — tự động hoá bước đó là vi phạm BH10. Orchestrator dừng
lại và in "việc cần phiên" kèm lệnh cụ thể thay vì làm bừa.

Các bước máy chạy được (mỗi bước = một hiện thân đã có, T4 — không viết lại):
  A2  quét ứng viên        surveillance_scan.py --topic <TÊN WATCHLIST> --report/--json-report (lưu ứng viên)
  A3  ưu tiên toàn kho     uu_tien_cap_nhat.py   (CHỈ khi --uu-tien: bảng TOÀN KHO, ~70 phút, không theo chủ đề)
  A4  sổ xác minh nguồn    so_xac_minh_nguon.py --quet <dashboard mới nhất của TỪNG lát cắt>
  B2  cổng liêm chính      verify_dashboard.py <dashboard> --strict-sources [--online]
  B4  BỘ NĂM               xuat_goi_cap_nhat.py (CHỈ khi --xuat — nặng, sinh 5 sản phẩm)
  B5  hàng chờ bác sĩ      trinh_muc_can_duyet.py

TÊN CHỦ ĐỀ (T1-01): nhận tên watchlist, tên lát cắt (`BenhThanMan_CKD`), chủ đề gốc (`SuyTim`) hoặc chuỗi
con duy nhất — phân giải qua `tools/chu_de_resolver.py` (ánh xạ người-khai `giam-sat-chu-de.json`). A2 LUÔN
nhận TÊN WATCHLIST đầy đủ. Bản tin gộp (`khong_can`) không có A2 — máy không tự bịa truy vấn (BH10).

CHẾ ĐỘ LÔ: `--cu-nhat N` tự chọn N chủ đề có lát cắt cũ nhất (mặc định 3, trần 8; bỏ `khong_can`), một
run_id + một khoá cho cả lô.

Log: `logs/<run_id>.jsonl` — mỗi dòng {run_id, buoc, lenh, rc, giay, luc}; dòng đầu ghi THAM SỐ lượt chạy để
`--resume` chạy tiếp ĐÚNG cờ (T1-09). Ứng viên A2 lưu ở `logs/<run_id>.A2-<slug>.{md,json}`; phiếu cuối lượt
ở `logs/<run_id>.phieu.md`.
Khoá: `ops/lock.py` trên `EBM-Dashboards/.orchestrator.lock` (không đụng `.quet.lock` của A2).

Mã thoát: 0 = mọi bước sạch · 1 = có bước FAIL NỘI DUNG / cần bác sĩ · 2 = hạ tầng (khoá bận / mạng /
timeout) · 64 = THAM SỐ sai (tên chủ đề không phân giải được) — KHÁC HẲN lỗi mạng.

Dùng:
  python3 ops/orchestrator.py --topic "Suy tim" --dry-run
  python3 ops/orchestrator.py --topic "BenhThanMan_CKD" --online
  python3 ops/orchestrator.py --cu-nhat 3 --online          # 3 chủ đề cũ nhất
  python3 ops/orchestrator.py --resume 20260815T070102-suy-tim
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import re
import subprocess
import sys
import time
import unicodedata
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

GOC = Path(__file__).resolve().parents[1]
DASH = GOC / "EBM-Dashboards"
LOGS = GOC / "logs"
PY = sys.executable  # BH05: không gọi "python3" cứng — Windows không có

HAN_CAP_NHAT_NGAY = 35   # ngưỡng «đáng mở phiên làm mới» — cùng ngưỡng kiem_do_tuoi_chung_cu dùng để nhắc
TRAN_LO = 8              # trần số chủ đề mỗi lô: mỗi chủ đề ≈ vài phút gọi mạng
HAN_KHOA_GIAY = 4 * 3600  # khoá mặc định 30' ngắn hơn một lượt có A3 (~71') — coi mồ côi giữa chừng (T1-08)
TIMEOUT_BUOC = {"A2": 1800, "A3": 7200, "A4": 1800, "B2": 1800, "B4": 3600, "B5": 600}
KHONG_PHAN_GIAI = 64
THIEU_TEP = -7           # mã nội bộ: tệp script/dashboard của bước không tồn tại (chưa chạy gì)


def _nap(duong_dan: Path, ten: str):
    spec = importlib.util.spec_from_file_location(ten, duong_dan)
    m = importlib.util.module_from_spec(spec)
    sys.modules[ten] = m
    spec.loader.exec_module(m)
    return m


def _nap_khoa():
    return _nap(GOC / "ops" / "lock.py", "ops_lock")


def _nap_resolver():
    return _nap(GOC / "tools" / "chu_de_resolver.py", "chu_de_resolver_ops")


def _slug(s: str) -> str:
    # gấp đ→d TRƯỚC NFD — NFD không tách được «đ» nên run_id từng mất chữ (T1-14: 'ai-thao-uong').
    s = unicodedata.normalize("NFD", (s or "").replace("đ", "d").replace("Đ", "D"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "toan-kho"


def _phan_giai(topic: str | None) -> dict:
    """Phân giải tên chủ đề; không raise. Thiếu kho/ánh xạ ⇒ 'khong_ro' (ke_hoach vẫn dựng được bước B2)."""
    if not topic:
        return {"q": topic, "loai": "toan_kho", "wl_topics": [], "a2_arg": None, "goc": [], "lat_cat": [],
                "ly_do": "", "gan_dung": [], "cach": ""}
    try:
        return _nap_resolver().resolve(topic)
    except Exception as exc:  # noqa: BLE001 — resolver hỏng không được làm chết dry-run
        return {"q": topic, "loai": "khong_ro", "wl_topics": [], "a2_arg": None, "goc": [], "lat_cat": [],
                "ly_do": f"không phân giải được ({type(exc).__name__})", "gan_dung": [], "cach": "",
                "loi_nap": f"resolver: {type(exc).__name__}"}


def _dashboards_cua_chu_de(topic: str) -> list[Path]:
    """Bản MỚI NHẤT của TỪNG lát cắt thuộc chủ đề, xếp theo ngày (mới nhất cuối).

    Trả danh sách chứ không «bản mới nhất»: một chủ đề có nhiều LÁT CẮT (SuyTim_TongHop · TienLuongSuyTim…)
    — chúng BỔ SUNG nhau, không thay nhau (BH30). Từ 20/09/2026 lát cắt lấy từ ánh xạ người-khai qua
    `chu_de_resolver` (trước đó khớp token tên tiếng Việt vào tên file CamelCase: với tên watchlist chỉ tìm
    được 8/52 lát cắt, và 20/28 chủ đề có dashboard bị in sai «CHƯA có dashboard»).
    """
    tt = _phan_giai(topic)
    if tt.get("lat_cat"):
        return [Path(x["duong_dan"]) for x in tt["lat_cat"]]
    # Không phân giải được: lùi về khớp token cũ (tên tự do người gõ) — giữ tương thích với chuỗi lẻ.
    tu = [t for t in _slug(topic).split("-") if len(t) > 2]
    khop = [p for p in DASH.glob("WebDashboard_*.html") if all(t in _slug(p.name) for t in tu)]

    def _ngay(p: Path) -> str:
        m = re.search(r"(\d{8})", p.name)
        return m.group(1) if m else "00000000"

    lat_cat: dict[str, Path] = {}
    for p in sorted(khop, key=_ngay):
        lat_cat[re.sub(r"_?\d{8}", "", p.name)] = p
    return sorted(lat_cat.values(), key=_ngay)


def _tuoi_ngay(p: Path) -> int | None:
    m = re.search(r"(\d{8})", p.name)
    if not m:
        return None
    try:
        return (dt.date.today() - dt.datetime.strptime(m.group(1), "%Y%m%d").date()).days
    except ValueError:
        return None


def _ten_lat(db: Path) -> str:
    return re.sub(r"^WebDashboard_EBM_(?:VanDeCuThe|Uptodate|CapNhatTuan|AnToanThuoc|CongCuKeDon)_?|_?\d{8}|\.html$",
                  "", db.name) or re.sub(r"^WebDashboard_EBM_|_?\d{8}|\.html$", "", db.name) or db.stem


def ke_hoach(topic: str | None, online: bool, xuat: bool, *, uu_tien: bool = False,
             run_id: str = "<run_id>", hau_to: str = "") -> list[dict]:
    """Dựng danh sách bước. Mỗi bước: {buoc, lenh (list) | phien (str) | ghi_chu (str), lat?}.

    `hau_to` (chế độ lô) gắn `@<slug>` vào tên bước để `--resume` phân biệt các chủ đề trong cùng run_id.
    """
    vd = str(DASH / "tools" / "verify_dashboard.py")
    tt = _phan_giai(topic)
    buoc: list[dict] = []
    if topic:
        if tt["loai"] == "khong_can":
            buoc.append({"buoc": "A2-bo-qua" + hau_to,
                         "ghi_chu": f"«{topic}» là bản tin gộp ({tt['ly_do']}) — không có mục giám sát; "
                                    "máy KHÔNG tự bịa truy vấn (BH10)"})
        elif tt.get("a2_arg"):
            slug = _slug(tt["a2_arg"])[:40]
            buoc.append({"buoc": "A2-quet" + hau_to,
                         # `--khong-cursor`: làm mới MỘT chủ đề theo yêu cầu KHÔNG được đọc/ghi con trỏ dùng chung của
                         # gói tuần — nếu không nó nuốt cửa sổ mà gói tuần đáng lẽ quét (đã xảy ra 20/09: A3 nuốt cursor 36
                         # chủ đề). Kết quả A2 nằm ở logs/<run>.A2-*.{md,json}; con trỏ tuần chỉ do gói tuần điều khiển.
                         "lenh": [PY, str(DASH / "tools" / "surveillance_scan.py"), "--topic", tt["a2_arg"],
                                  "--khong-cursor",
                                  "--report", str(LOGS / f"{run_id}.A2-{slug}.md"),
                                  "--json-report", str(LOGS / f"{run_id}.A2-{slug}.json")]})
        elif tt["loai"] == "khong_ro":
            # KỂ CẢ khi đã có lát cắt (gốc chưa khai ánh xạ): A2 bị bỏ phải được NÓI RA — trước đây im lặng, chỉ
            # còn A4/B2/B5 chạy và người đọc tưởng đã quét chứng cứ mới (P1-15).
            buoc.append({"buoc": "A2-bo-qua" + hau_to,
                         "ghi_chu": f"«{topic}» chưa ánh xạ tới mục watchlist ({tt['ly_do']}) — bỏ A2 "
                                    "(cần bác sĩ khai vào EBM-Dashboards/giam-sat-chu-de.json)"})
    if uu_tien:
        buoc.append({"buoc": "A3-uu-tien" + hau_to, "lenh": [PY, str(GOC / "tools" / "uu_tien_cap_nhat.py")]})
    cac_db = _dashboards_cua_chu_de(topic) if topic else []
    for db in cac_db:  # TỪNG lát cắt — chúng bổ sung nhau, không thay nhau (BH30)
        lat = _ten_lat(db)
        buoc.append({"buoc": f"A4-so-xac-minh[{lat}]" + hau_to, "lat": lat,
                     "lenh": [PY, str(GOC / "tools" / "so_xac_minh_nguon.py"), "--quet", str(db), "--vong", "1"]})
        # `--strict-sources` LUÔN bật (vá 20/09/2026, T1-07): verify_dashboard hỗ trợ nó cả chế độ offline (in
        # cảnh báo «chưa phân giải thật»); giới hạn «offline chưa có strict-sources» từng ghi ở đây đã hết lý do
        # — đo offline trên 64 lát cắt: 63 PASS, 1 FAIL đúng thiết kế (BH109). Nhóm luật MẠNH NHẤT (chặn
        # `decision='apply'` trên gradeLevel na/low, hoặc chỉ dựa `Consensus`) không được nằm im (BH96).
        buoc.append({"buoc": f"B2-cong-liem-chinh[{lat}]" + hau_to, "lat": lat,
                     "lenh": [PY, vd, str(db), "--strict-sources"] + (["--online"] if online else [])})
        if xuat:
            buoc.append({"buoc": f"B4-bo-nam[{lat}]" + hau_to, "lat": lat,
                         "lenh": [PY, str(GOC / "tools" / "xuat_goi_cap_nhat.py"), str(db)]
                                 + (["--online"] if online else [])})
    if topic and not cac_db and tt["loai"] != "khong_can":
        buoc.append({"buoc": "B1-dung-dashboard" + hau_to,
                     "phien": f"chủ đề «{topic}» CHƯA có dashboard — cần PHIÊN skill "
                              f"cap-nhat-chung-cu-y-khoa (bác sĩ chốt phạm vi; BH10)"})
    buoc.append({"buoc": "B5-hang-cho-bac-si" + hau_to,
                 "lenh": [PY, str(GOC / "tools" / "trinh_muc_can_duyet.py")]})
    return buoc


# ── phân loại mã thoát THEO BƯỚC (T1-04) ─────────────────────────────────────────────────────────────
def phan_loai(buoc: str, rc: int, *, a2_json_khong_pass: bool = False) -> tuple[str, str]:
    """(mức, thông điệp). mức ∈ ok · noi_dung · ha_tang · tham_so · khoa_ban · rut · chan · timeout.

    Số mã thoát KHÔNG có nghĩa chung giữa các bước: A2 rc=2 vừa là argparse vừa là «quét không PASS»; A4 rc=2
    là «có NGUỒN ĐÃ BỊ RÚT» chứ không phải mạng; B4 rc=3 là «CHẶN XUẤT» của cổng. Trước đây mọi rc=2 đều in
    «FAIL HẠ TẦNG — chạy lại khi mạng ổn» và rc=3 lọt thành «đi tiếp».
    """
    if rc == -9:
        return "timeout", f"{buoc} QUÁ THỜI GIAN — dừng bước (hạ tầng/nguồn chậm); chạy lại bằng --resume"
    if rc == THIEU_TEP:  # script/dashboard không tồn tại: KHÔNG được đọc thành «nguồn bị rút» (rc=2 của Python) — P1-06
        return "tham_so", f"{buoc}: THIẾU TỆP (script hoặc dashboard không tồn tại) — lệnh sai, không phải nguồn bị rút"
    if rc == 0:
        return "ok", ""
    if buoc.startswith("A2"):
        if rc == 3:
            return "khoa_ban", "KHOÁ QUÉT BẬN — có lượt quét khác đang chạy; dừng, không đi tiếp"
        if rc == 2 and a2_json_khong_pass:
            return "ha_tang", "HẠ TẦNG NGUỒN — lần quét không PASS (nguồn/mạng); chạy lại sau bằng --resume"
        if rc == 2:
            return "tham_so", "THAM SỐ/LỆNH SAI — không phải lỗi mạng (tên chủ đề không khớp watchlist?)"
        return "noi_dung", f"quét trả rc={rc}"
    if buoc.startswith("A4"):
        if rc == 2:
            return "rut", "🔴 NGUỒN ĐÃ BỊ RÚT — xử lý trước khi dùng (KHÔNG chạy lại vì mạng)"
        return "noi_dung", "sổ xác minh chưa đủ (đi tiếp, ghi vào phiếu)"
    if buoc.startswith("B2"):
        if rc == 2:
            return "ha_tang", "B2 lỗi hạ tầng (không xác minh được nguồn) — dừng; chạy lại khi mạng ổn"
        return "chan", "cổng liêm chính CHẶN gói (rc={}) — bỏ B4 của lát cắt này, đi tiếp lát cắt khác".format(rc)
    if buoc.startswith("B4"):
        if rc == 3:
            return "chan", "CHẶN XUẤT bởi cổng liêm chính — không sinh bộ năm cho lát cắt này"
        if rc == 2:
            return "noi_dung", "B4 thiếu công cụ/đường dẫn — kiểm tools/xuat_goi_cap_nhat.py"
        return "noi_dung", f"B4 rc={rc}"
    if buoc.startswith("A3"):
        return "noi_dung", "A3 không kết luận"
    return "noi_dung", f"rc={rc}"  # B5: rc≠0 chỉ nghĩa CÓ mục cần đọc — không phải hỏng


DUNG_HET = {"ha_tang", "tham_so", "khoa_ban", "timeout"}


def _thieu_tep(lenh: list[str]) -> str | None:
    """Tên tệp thiếu (script ở lenh[1] hoặc tham số `.html`); None = đủ. Chạy TRƯỚC subprocess của bước thật."""
    for x in [lenh[1]] + [a for a in lenh[2:] if str(a).endswith(".html")] if len(lenh) > 1 else []:
        if not Path(x).exists():
            return str(x)
    return None


def _chay_that(lenh: list[str], timeout: int) -> int:
    if _thieu_tep(lenh):
        print(f"🔴 thiếu tệp: {_thieu_tep(lenh)}")
        return THIEU_TEP
    try:
        return subprocess.run(lenh, cwd=GOC, timeout=timeout).returncode
    except subprocess.TimeoutExpired:
        return -9


def _timeout_buoc(ten: str) -> int:
    return TIMEOUT_BUOC.get(ten[:2], 1800)


def _dau_tep(lenh: list[str]) -> dict:
    """{đường dẫn: mtime_ns} của các tham số `.html` đang tồn tại — để resume biết dashboard đã đổi sau khi bước xong."""
    ra: dict = {}
    for a in lenh[2:]:
        if str(a).endswith(".html"):
            try:
                ra[str(a)] = Path(a).stat().st_mtime_ns
            except OSError:
                pass
    return ra


def _la_da_xong(b: dict, da_xong) -> bool:
    """Bước đã xong CHỈ KHI cùng tên, cùng lệnh (kể cả cờ --online) và dashboard chưa đổi (P1-07).

    `da_xong` là set tên (kiểu cũ, dùng trong test) hoặc dict {tên: {"lenh", "dau_tep"}} do main dựng từ log."""
    ten = b["buoc"]
    if ten not in da_xong:
        return False
    if not isinstance(da_xong, dict):
        return True
    cu = da_xong[ten]
    return cu.get("lenh") == b.get("lenh", [None])[1:] and (cu.get("dau_tep") or {}) == _dau_tep(b.get("lenh", [None, None]))


def _ung_vien_a2(duong_json: Path) -> tuple[int | None, bool]:
    """(số ứng viên, quét có KHÔNG-PASS không) đọc từ JSON A2; không đọc được ⇒ (None, False)."""
    try:
        du = json.loads(duong_json.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None, False
    n = sum(len(t.get("candidates") or []) for t in (du.get("topics") or []))
    return n, du.get("status") not in (None, "PASS")


def thuc_thi(cac_buoc: list[dict], *, chay=None, ghi=lambda d: None, da_xong: frozenset | set | dict = frozenset(),
             in_=print, topic: str | None = None) -> dict:
    """Chạy các bước; trả {tong_rc, dung, ket_qua{buoc: (mức, rc)}, lat_hong, rut, ung_vien}.

    Lát cắt độc lập (T1-06/BH30): B2 fail của lát cắt X chỉ bỏ B4 của CHÍNH X rồi đi tiếp lát cắt khác — trước
    đây `return 1` ở B2 đầu tiên lỗi khiến «Suy tim» không bao giờ tới SuyTim_TongHop và B5. Gói bị cổng
    chặn vẫn KHÔNG bao giờ đi tiếp sang B4 xuất bộ năm (BH96).
    """
    chay = chay or _chay_that  # tra lúc GỌI (không phải lúc định nghĩa) để test main() thay được bộ chạy
    res = {"tong_rc": 0, "dung": None, "ket_qua": {}, "lat_hong": set(), "rut": [], "ung_vien": None,
           "phien": [], "a2_bao_cao": [], "b2_offline": False}
    for b in cac_buoc:
        ten = b["buoc"]
        if _la_da_xong(b, da_xong):
            if ten.startswith("A2") and "--json-report" in b.get("lenh", []):
                # Resume: A2 đã xong thì ĐỌC LẠI kết quả từ tệp JSON còn nằm trong logs/ — không được để số ứng viên
                # rơi mất rồi kết luận «sạch» (P1-03).
                n, _kp = _ung_vien_a2(Path(b["lenh"][b["lenh"].index("--json-report") + 1]))
                if n is not None:
                    res["ung_vien"] = (res["ung_vien"] or 0) + n
                if "--report" in b["lenh"]:
                    res["a2_bao_cao"].append(b["lenh"][b["lenh"].index("--report") + 1])
            continue
        if "phien" in b:
            res["phien"].append(b["phien"])  # B1 «chưa có dashboard» phải vào phiếu + kết luận cuối (P1-04)
            in_(f"⏸ {ten}: {b['phien']}")
            ghi({"buoc": ten, "rc": None, "phien": b["phien"]})
            continue
        if "ghi_chu" in b:
            in_(f"ⓘ {ten}: {b['ghi_chu']}")
            ghi({"buoc": ten, "rc": None, "ghi_chu": b["ghi_chu"]})
            continue
        if ten.startswith("B4") and b.get("lat") in res["lat_hong"]:
            in_(f"⏭ {ten}: bỏ — lát cắt «{b['lat']}» đã bị cổng chặn ở B2")
            ghi({"buoc": ten, "rc": None, "bo_qua": "lat_cat_bi_chan"})
            continue
        t0 = time.time()
        in_(f"\n══ {ten} ══")
        rc = chay(b["lenh"], _timeout_buoc(ten))
        if ten.startswith("B2") and "--online" not in b["lenh"]:
            res["b2_offline"] = True
        a2_khong_pass = False
        if ten.startswith("A2"):
            duong_json = Path(b["lenh"][b["lenh"].index("--json-report") + 1]) if "--json-report" in b["lenh"] else None
            if duong_json is not None:
                n, khong_pass = _ung_vien_a2(duong_json)
                res["ung_vien"] = (res["ung_vien"] or 0) + (n or 0) if n is not None else res["ung_vien"]
                a2_khong_pass = khong_pass
            if "--report" in b["lenh"]:
                res["a2_bao_cao"].append(b["lenh"][b["lenh"].index("--report") + 1])
        muc, msg = phan_loai(ten, rc, a2_json_khong_pass=a2_khong_pass)
        res["ket_qua"][ten] = (muc, rc)
        ghi({"buoc": ten, "lenh": b["lenh"][1:], "rc": rc, "muc": muc, "giay": round(time.time() - t0, 1),
             "dau_tep": _dau_tep(b["lenh"])})
        if muc == "ok":
            continue
        if msg:
            in_(f"🔴 {ten}: {msg}")
        if muc in DUNG_HET:
            res["tong_rc"] = 64 if muc == "tham_so" else 2
            res["dung"] = muc
            return res
        res["tong_rc"] = max(res["tong_rc"], 1)
        if muc == "rut":
            res["rut"].append(b.get("lat") or ten)
        if muc == "chan" and ten.startswith("B2"):
            res["lat_hong"].add(b.get("lat"))
    return res


def _cho_ky_rut_bai() -> frozenset:
    """Tên dashboard đang CHỜ BÁC SĨ KÝ miễn trừ «đính chính bị rút» (BH109); không đọc được ⇒ rỗng (không đoán)."""
    try:
        m = _nap(GOC / "tools" / "mau_ky_rut_bai.py", "mau_ky_ops")
        return frozenset(n for e in m.muc_cho_ky() for n in (e.get("_ngu_canh", {}).get("dashboard") or []))
    except Exception:  # noqa: BLE001 — phiếu không được chết vì công cụ phụ
        return frozenset()


def phieu_can_phien(topic: str | None, tt: dict, cac_db: list[Path], res: dict,
                    cho_ky: frozenset | set = frozenset()) -> list[str]:
    """Việc CẦN PHIÊN NGƯỜI, mỗi dòng có lý do đo được + lệnh cụ thể (T1-05). Không tự dựng dashboard (BH10).

    `cho_ky`: dashboard bị cổng chặn CHỈ vì chờ chữ ký miễn trừ (P-07, phản biện 20/09/2026). Gói đó cần bác sĩ
    ĐỌC + KÝ, không cần dựng lại — gợi ý `/cap-nhat-chung-cu` cho nó là chỉ sai việc.
    """
    viec: list[str] = []
    goi_y = tt.get("a2_arg") or topic or ""
    ly_do: list[str] = []
    if tt.get("loai") == "khong_can":
        return viec  # bản tin gộp: không làm mới bằng máy
    if tt.get("loai") == "khong_ro" and tt.get("lat_cat"):
        viec.append(f"👤 khai ánh xạ «{topic}» vào EBM-Dashboards/giam-sat-chu-de.json (hoặc `khong_can` kèm lý do) "
                    "— chưa khai nên A2 KHÔNG quét chứng cứ mới cho chủ đề này")
    ten_ky = {_ten_lat(p) for p in cac_db if p.name in cho_ky}
    if ten_ky & set(res.get("lat_hong") or ()):
        viec.append("👤 KÝ hoặc HẠ mục (không cần dựng lại): " + ", ".join(sorted(ten_ky & set(res["lat_hong"])))
                    + " — bị cổng chặn vì nguồn có thông báo rút là bản đính chính; chạy "
                      "`python3 tools/mau_ky_rut_bai.py` rồi đọc + ký `rut-bai-da-xem-xet.json`")
        res = {**res, "lat_hong": set(res["lat_hong"]) - ten_ky}
    cu_nhat = max((t for t in (_tuoi_ngay(p) for p in cac_db) if t is not None), default=None)
    if cu_nhat is not None and cu_nhat >= HAN_CAP_NHAT_NGAY:  # lát cắt CŨ NHẤT (P1-10: trước ghi nhầm «mới nhất»)
        ly_do.append(f"lát cắt cũ nhất {cu_nhat} ngày (≥ {HAN_CAP_NHAT_NGAY})")
    if res.get("ung_vien"):
        ly_do.append(f"{res['ung_vien']} ứng viên mới ở A2")
    if res.get("rut"):
        ly_do.append("có nguồn bị rút: " + ", ".join(res["rut"]))
    if res.get("lat_hong"):
        ly_do.append("cổng liêm chính chặn: " + ", ".join(sorted(x for x in res["lat_hong"] if x)))
    if ly_do and goi_y:
        viec.append(f"/cap-nhat-chung-cu {goi_y} — " + "; ".join(ly_do))
    return viec


def chon_cu_nhat(n: int, du_lieu: dict | None = None, tuoi: list[tuple[str, int]] | None = None) -> tuple[list[dict], list[str]]:
    """Chọn ≤ n chủ đề (theo TÊN WATCHLIST) có lát cắt cũ nhất, bỏ `khong_can`. Trả (danh sách, ghi chú bỏ qua)."""
    rs = _nap_resolver()
    if tuoi is None:
        tuoi = _nap(GOC / "tools" / "kiem_do_tuoi_chung_cu.py", "kt_ops").lau_chua_xem_lai()
    d = du_lieu if du_lieu is not None else rs.nap_du_lieu()
    nhom: dict[str, dict] = {}
    bo: list[str] = []
    for lat, t in tuoi:
        r = rs.resolve(lat, d)
        if r["loai"] != "watchlist" or not r.get("a2_arg"):
            bo.append(f"{lat} ({r['loai']})")
            continue
        g = nhom.setdefault(r["a2_arg"], {"q": r["a2_arg"], "tuoi_max": t, "lat": []})
        g["tuoi_max"] = max(g["tuoi_max"], t)
        g["lat"].append(lat)
    chon = sorted(nhom.values(), key=lambda x: -x["tuoi_max"])[:max(1, min(n, TRAN_LO))]
    return chon, bo


def _in_ke_hoach(run_id: str, cac_buoc: list[dict], da_xong: set) -> None:
    for b in cac_buoc:
        dau = "⏭" if _la_da_xong(b, da_xong) else "▸"
        if "lenh" in b:
            mo_ta = " ".join(b["lenh"][1:]).replace(run_id, "<run_id>")
        elif "phien" in b:
            mo_ta = f"[PHIÊN NGƯỜI] {b['phien']}"
        else:
            mo_ta = f"[BỎ QUA] {b['ghi_chu']}"
        print(f"  {dau} {b['buoc']}: {mo_ta}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Orchestrator một cửa A2→B5")
    ap.add_argument("--topic", help="tên watchlist · lát cắt · chủ đề gốc; bỏ trống = việc toàn kho")
    ap.add_argument("--cu-nhat", type=int, metavar="N", help=f"chế độ LÔ: N chủ đề cũ nhất (trần {TRAN_LO})")
    ap.add_argument("--uu-tien", action="store_true", help="chạy thêm A3 (bảng ưu tiên TOÀN KHO, ~70 phút)")
    ap.add_argument("--dry-run", action="store_true", help="chỉ in kế hoạch, không chạy")
    ap.add_argument("--online", action="store_true", help="B2/B4 chạy chế độ --online")
    ap.add_argument("--xuat", action="store_true", help="chạy cả B4 BỘ NĂM (nặng)")
    ap.add_argument("--resume", metavar="RUN_ID", help="chạy tiếp run cũ, bỏ qua bước đã rc=0, GIỮ nguyên cờ cũ")
    a = ap.parse_args()

    # Cờ xung đột bị TỪ CHỐI (P1-12): trước đây --cu-nhat kèm --topic bỏ qua topic im lặng mà run_id vẫn mang tên
    # topic; --cu-nhat 0 rơi về chế độ toàn kho; --cu-nhat -2 thành lô 1 chủ đề.
    if a.cu_nhat is not None and a.cu_nhat < 1:
        print("🔴 THAM SỐ SAI — --cu-nhat phải ≥ 1.")
        return KHONG_PHAN_GIAI
    if a.cu_nhat and a.topic:
        print("🔴 THAM SỐ SAI — --topic và --cu-nhat loại trừ nhau (chọn MỘT chế độ).")
        return KHONG_PHAN_GIAI
    if a.resume and (a.topic or a.cu_nhat):
        print("🔴 THAM SỐ SAI — --resume giữ nguyên chủ đề/lô của run cũ; không kèm --topic/--cu-nhat.")
        return KHONG_PHAN_GIAI

    run_id = a.resume or f"{time.strftime('%Y%m%dT%H%M%S')}-{_slug(a.topic or ('lo' if a.cu_nhat else ''))}"
    log_f = LOGS / f"{run_id}.jsonl"
    da_xong: dict = {}
    tham_so = {"topic": a.topic, "cu_nhat": a.cu_nhat, "uu_tien": a.uu_tien, "online": a.online,
               "xuat": a.xuat, "cac_chu_de": None}
    if a.resume:
        if not log_f.exists():
            print(f"🔴 không thấy log run {a.resume}")
            return 2
        for dong in log_f.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(dong)
            except ValueError:
                continue
            if r.get("rc") == 0:  # nhớ CẢ lệnh + dấu tệp: resume nâng cờ/dashboard đổi ⇒ bước phải chạy lại (P1-07)
                da_xong[r["buoc"]] = {"lenh": r.get("lenh"), "dau_tep": r.get("dau_tep")}
            if "tham_so" in r:  # T1-09: resume KHÔNG được hạ cờ (thiếu --online ⇒ B2 offline ghi rc=0 như «đã xong»)
                cu = r["tham_so"]
                for k in ("topic", "cu_nhat", "uu_tien", "online", "xuat", "cac_chu_de"):
                    if k in cu and (tham_so.get(k) in (None, False)):
                        tham_so[k] = cu[k]
            elif r.get("topic") and not tham_so["topic"] and not tham_so["cu_nhat"]:
                tham_so["topic"] = r["topic"]  # log cũ trước 20/09/2026
        a.topic, a.cu_nhat = tham_so["topic"], tham_so["cu_nhat"]
        a.uu_tien, a.online, a.xuat = tham_so["uu_tien"], tham_so["online"], tham_so["xuat"]

    # ── xác định danh sách chủ đề (lô) và dựng kế hoạch ────────────────────────────────────────────
    ke: list[tuple[str | None, dict, list[dict]]] = []  # (topic, tt, các bước)
    if a.cu_nhat:
        chon = tham_so.get("cac_chu_de")
        if not chon:
            chon, bo = chon_cu_nhat(a.cu_nhat)
            tham_so["cac_chu_de"] = chon
            if bo:
                # Tách «cố ý không cần» khỏi «chưa khai — cần bác sĩ»: 12 mục khong_can cố định từng chiếm hết
                # 6 chỗ đầu nên gốc MỚI chưa khai bị che (P1-15).
                chua_khai = [x for x in bo if "(khong_can)" not in x]
                co_y = len(bo) - len(chua_khai)
                if chua_khai:
                    print(f"🟠 {len(chua_khai)} lát cắt CHƯA khai ánh xạ (cần bác sĩ khai vào giam-sat-chu-de.json): "
                          f"{', '.join(chua_khai[:10])}{'…' if len(chua_khai) > 10 else ''}")
                if co_y:
                    print(f"ⓘ bỏ qua {co_y} lát cắt bản tin gộp (khong_can — cố ý, không phải thiếu sót)")
        if not chon:
            print("🟢 Không có chủ đề nào để làm mới.")
            return 0
        for i, c in enumerate(chon):
            ke.append((c["q"], _phan_giai(c["q"]),
                       ke_hoach(c["q"], a.online, a.xuat, uu_tien=a.uu_tien and i == 0, run_id=run_id,
                                hau_to=f"@{_slug(c['q'])[:24]}")))
    else:
        tt = _phan_giai(a.topic)
        if a.topic and tt["loai"] == "khong_ro" and tt.get("loi_nap"):
            # Nạp kho/ánh xạ hỏng ≠ tên sai: dừng HẠ TẦNG (rc=2), không đoán rồi in «CHƯA có dashboard» sai (P1-05).
            print(f"🔴 HẠ TẦNG — không nạp được dữ liệu phân giải chủ đề ({tt['loi_nap']}). "
                  "Đây KHÔNG phải tên chủ đề sai; máy dừng thay vì đoán.")
            return 2
        if a.topic and tt["loai"] == "khong_ro" and not tt.get("lat_cat"):
            print(f"🔴 THAM SỐ SAI — «{a.topic}» không phân giải được ({tt['ly_do']}). Đây KHÔNG phải lỗi mạng.")
            if tt.get("gan_dung"):
                print("   Có phải: " + " · ".join(tt["gan_dung"]))
            return KHONG_PHAN_GIAI
        ke.append((a.topic, tt, ke_hoach(a.topic, a.online, a.xuat, uu_tien=a.uu_tien, run_id=run_id)))

    tong_buoc = sum(len(k[2]) for k in ke)
    so_bo = sum(1 for k in ke for b in k[2] if _la_da_xong(b, da_xong))
    print(f"KẾ HOẠCH run {run_id} — {tong_buoc} bước"
          + (f" (bỏ qua {so_bo} đã xong)" if so_bo else "")
          + (f" · lô {len(ke)} chủ đề" if a.cu_nhat else ""))
    for topic, tt, cac_buoc in ke:
        if a.cu_nhat:
            print(f"— {topic} ({tt.get('cach') or tt.get('loai')})")
        _in_ke_hoach(run_id, cac_buoc, da_xong)
    if a.dry_run:
        print("(dry-run — chưa chạy gì, chưa giành khoá)")
        return 0

    khoa_mod = _nap_khoa()
    LOGS.mkdir(exist_ok=True)
    tong_rc = 0
    tat_ca_phien: list[str] = []
    b2_offline = False
    try:
        with khoa_mod.Khoa(DASH / ".orchestrator.lock", han_giay=HAN_KHOA_GIAY):
            with log_f.open("a", encoding="utf-8") as lf:
                def ghi(d: dict) -> None:
                    d.update({"run_id": run_id, "luc": time.strftime("%FT%T")})
                    lf.write(json.dumps(d, ensure_ascii=False) + "\n")
                    lf.flush()
                if not a.resume:
                    ghi({"tham_so": tham_so, "topic": a.topic})
                for topic, tt, cac_buoc in ke:
                    res = thuc_thi(cac_buoc, ghi=ghi, da_xong=da_xong, topic=topic)
                    cac_db = _dashboards_cua_chu_de(topic) if topic else []
                    viec = phieu_can_phien(topic, tt, cac_db, res, _cho_ky_rut_bai())
                    # B1: «chủ đề CHƯA có dashboard» phải hiện trong phiếu + kết luận cuối (P1-04)
                    viec += [f"👤 {x}" for x in res.get("phien", [])]
                    if res.get("a2_bao_cao") and res.get("ung_vien"):
                        viec.append("👤 đọc ứng viên A2: " + ", ".join(
                            str(Path(x).relative_to(GOC)) if str(x).startswith(str(GOC)) else str(x)
                            for x in res["a2_bao_cao"]))
                    b2_offline = b2_offline or bool(res.get("b2_offline"))
                    tat_ca_phien += viec
                    tong_rc = max(tong_rc, res["tong_rc"])
                    if res["dung"]:
                        break
                phieu = LOGS / f"{run_id}.phieu.md"
                than = ("\n".join(f"- 🟠 {v}" for v in tat_ca_phien) if tat_ca_phien
                        else "- Không có việc nào cần phiên người.")
                if b2_offline:
                    than += "\n- ⚪ B2 chạy OFFLINE — chưa phân giải thật PMID/DOI (thêm --online để xác minh thật)."
                if a.resume and phieu.exists():  # KHÔNG ghi đè phiếu của lượt trước (P1-03): nối thêm một mục
                    with phieu.open("a", encoding="utf-8") as pf:
                        pf.write(f"\n## Lượt resume {time.strftime('%FT%T')}\n\n{than}\n")
                else:
                    phieu.write_text("# Phiếu lượt chạy " + run_id + "\n\n" + than
                                     + "\n\nCần bác sĩ kiểm chứng.\n", encoding="utf-8")
    except khoa_mod.KhoaBanRon as e:
        print(f"🔴 {e}")
        return 2
    if tong_rc == 64:
        print(f"\n🔴 THAM SỐ/LỆNH SAI — dừng. log: logs/{run_id}.jsonl")
        return 64
    if tong_rc == 2:
        print(f"\n🔴 dừng do hạ tầng/khoá — chạy tiếp: --resume {run_id}")
        return 2
    if tat_ca_phien:
        print("\n🟠 CẦN PHIÊN NGƯỜI (máy không tự dựng dashboard — BH10):")
        for v in tat_ca_phien:
            print(f"   • {v}")
    print(f"\n{'🟠 xong, CÓ mục cần bác sĩ đọc' if (tong_rc or tat_ca_phien) else '🟢 xong, sạch'} "
          f"— log: logs/{run_id}.jsonl · phiếu: logs/{run_id}.phieu.md")
    if b2_offline:
        print("   ⚪ B2 chạy OFFLINE — chưa phân giải thật PMID/DOI; «sạch» chỉ đúng về hợp đồng nguồn "
              "(thêm --online để xác minh thật).")
    return tong_rc


if __name__ == "__main__":
    raise SystemExit(main())
