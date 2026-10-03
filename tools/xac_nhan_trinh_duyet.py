#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TRANG CHẶN BOT ⇒ MÁY MỞ TRANG, BÁC SĨ TỰ XÁC NHẬN — hàng chờ + ghi bằng chứng trình duyệt (02/10/2026, bác sĩ yêu cầu).

VÌ SAO CÓ. Một số cơ quan (hiện www.fda.gov) chặn trình khách tự động: lượt kiểm của cổng liêm chính nhận 401/403/404/410, còn
trình duyệt trong app gặp trang «Sorry! This resembles an automated request» + nút «I am not a bot». Cổng KHÔNG giả dạng trình
duyệt và Claude KHÔNG BAO GIỜ bấm vượt kiểm tra chống bot. Đường đúng: máy MỞ trang trong khung trình duyệt, BÁC SĨ tự bấm xác
nhận, trang thật hiện ra ⇒ máy đọc tiêu đề trang thật và ghi bằng chứng vào `EBM-Dashboards/url-xac-minh-trinh-duyet.json`
(sổ mà cổng `verify_dashboard.py` tra — hạn 180 ngày). Trước công cụ này: không ai biết URL nào sắp hết hạn bằng chứng, và một URL
thiếu bằng chứng làm DỪNG cả lô `ops/orchestrator.py` (02/10: lô 3 chủ đề dừng ở gói Orlistat).

    python3 tools/xac_nhan_trinh_duyet.py                    # hàng chờ: URL miền chặn bot thiếu/sắp hết hạn bằng chứng (ngoại tuyến)
    python3 tools/xac_nhan_trinh_duyet.py --huong-dan        # quy trình từng bước cho phiên Claude + bác sĩ
    python3 tools/xac_nhan_trinh_duyet.py --ghi URL --tieu-de "<tiêu đề trang thật>" --cach "<đã đọc gì>"
                                                             # ghi bằng chứng SAU KHI trang thật đã hiện (có sao lưu, tự kiểm lại)

Mã thoát: 0 không còn URL chờ · 1 còn URL chờ bác sĩ xác nhận · 2 KHÔNG ĐO ĐƯỢC (thiếu EBM-Dashboards / cổng / sổ hỏng) ·
3 từ chối ghi (tiêu đề là trang chặn/lỗi, miền chưa khai, thiếu cách kiểm…). Luật «miền nào được nhận, hạn bao lâu, tiêu đề tối
thiểu» lấy từ CHÍNH cổng (một nguồn sự thật) — công cụ này không viết lại luật đó. Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import sys
from datetime import date, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DASH = REPO / "EBM-Dashboards"
GATE_CHAY = DASH / "tools" / "verify_dashboard.py"                                       # bản cổng dây chuyền thật chạy
GATE_NGUON = REPO / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "verify_dashboard.py"
SAO_LUU = REPO / "state" / "sao-luu-url-trinh-duyet"
CANH_BAO_TRUOC_NGAY = 30   # bằng chứng còn ≤ 30 ngày ⇒ vào hàng chờ để mở lại sớm, không đợi tới lúc cổng chặn

# Tiêu đề KHÔNG phải tài liệu: trang chặn bot, trang lỗi, tên cơ quan chung chung (đúng thứ trình duyệt thấy khi chưa qua chặn).
_TIEU_DE_CAM = re.compile(
    r"automated request|not a bot|are you a robot|robot check|captcha|verify (that )?you are (a )?human|"
    r"just a moment|attention required|access denied|forbidden|unauthori[sz]ed|page not found|not found|"
    r"\b40[134]\b|\b410\b|\berror\b|security check|request blocked|"
    # Trình duyệt trong app chạy giao diện TIẾNG VIỆT (đo 02/10/2026: Cloudflare hiện «Chờ một chút...», «Thực hiện xác minh bảo mật»).
    r"chờ một chút|xác minh bạn là con người|xác minh bảo mật|không phải là bot|truy cập bị từ chối|không tìm thấy trang|"
    r"\blỗi\b|vui lòng chờ|please wait|one moment", re.I)
_TIEU_DE_CHUNG = {"u.s. food and drug administration", "food and drug administration", "fda", "home", "trang chủ"}

HUONG_DAN = """QUY TRÌNH «TRANG CHẶN BOT — BÁC SĨ XÁC NHẬN» (Claude làm, bác sĩ chỉ bấm xác nhận trên trang):
  1. `python3 tools/xac_nhan_trinh_duyet.py` → danh sách URL chờ (đánh số).
  2. Với từng URL: Claude mở bằng trình duyệt trong app (Claude_Browser → navigate) và chụp màn hình.
     • Trang thật hiện ngay ⇒ sang bước 3.
     • Trang chặn bot («I am not a bot», CAPTCHA, «Just a moment…») ⇒ Claude NHỜ BÁC SĨ tự bấm xác nhận ngay trong khung
       trình duyệt rồi nói «xong». Claude KHÔNG bấm, KHÔNG giải CAPTCHA, KHÔNG giả dạng trình duyệt.
     • «Page Not Found»/404 trong chính trình duyệt ⇒ link chết THẬT: KHÔNG ghi sổ; báo bác sĩ sửa URL trong dashboard.
  3. Claude đọc document.title + h1 + câu đầu nội dung, đối chiếu đúng tài liệu mà dashboard trích (thuốc, cảnh báo, năm).
  4. `python3 tools/xac_nhan_trinh_duyet.py --ghi "<URL>" --tieu-de "<document.title thật>" --cach "Claude_Browser: <đã đọc gì>"`
     — công cụ từ chối tiêu đề trang chặn/lỗi, sao lưu sổ, ghi, rồi tự kiểm lại bằng CHÍNH hàm của cổng.
  5. Hết hàng chờ ⇒ chạy lại cổng/lô (vd `python3 ops/orchestrator.py --resume <run_id>`)."""


def nap_cong():
    """Nạp module cổng: ưu tiên bản dây chuyền thật chạy (EBM-Dashboards/tools), không có thì bản nguồn chuẩn trong git."""
    for p in (GATE_CHAY, GATE_NGUON):
        if p.exists():
            spec = importlib.util.spec_from_file_location("vd_xac_nhan_trinh_duyet", p)
            m = importlib.util.module_from_spec(spec)
            sys.modules["vd_xac_nhan_trinh_duyet"] = m
            try:
                spec.loader.exec_module(m)
            except BaseException:
                sys.modules.pop("vd_xac_nhan_trinh_duyet", None)
                raise
            return m
    raise FileNotFoundError("không thấy verify_dashboard.py (EBM-Dashboards/tools lẫn bản nguồn chuẩn)")


def url_mien_chan_cua_dashboard(duong: Path, vd) -> list[tuple[str, str]]:
    """[(id mục, url)] của mục CHỈ có url (không pmid/doi) thuộc miền chặn — ĐÚNG điều kiện `urls_only` mà cổng xác minh online."""
    try:
        html = duong.read_text(encoding="utf-8")
    except OSError:
        return []
    khoi = vd.extract_data_block(html)
    if not khoi:
        return []
    ra = []
    for ch in vd.split_items(khoi):
        url = (vd.field(ch, "url") or "").strip()
        if url and not vd.field(ch, "pmid") and not vd.field(ch, "doi") and vd.mien_chan_tu_dong(url):
            ra.append((vd.field(ch, "id") or "(?)", url))
    return ra


def _ngay_bang_chung(info: str) -> date | None:
    m = re.search(r"ngày (\d{4}-\d{2}-\d{2})", info or "")
    try:
        return date.fromisoformat(m.group(1)) if m else None
    except ValueError:
        return None


def quet(vd, thu_muc: Path | None = None, hom_nay: date | None = None, canh_bao_truoc: int = CANH_BAO_TRUOC_NGAY) -> list[dict]:
    """Mọi URL miền chặn đang được dashboard trích, kèm trạng thái bằng chứng: THIEU · SAP_HET_HAN · CON_HAN. Ngoại tuyến."""
    thu_muc = thu_muc or DASH   # tra lúc GỌI — tham số mặc định chốt lúc nạp mô-đun thì vá hằng (test, công cụ khác) vô tác dụng
    hom_nay = hom_nay or date.today()
    theo_url: dict[str, dict] = {}
    for db in sorted(thu_muc.glob("WebDashboard_*.html")):
        for iid, url in url_mien_chan_cua_dashboard(db, vd):
            m = theo_url.setdefault(url, {"url": url, "mien": vd.mien_chan_tu_dong(url), "dung_o": [], "dashboard_mau": db})
            m["dung_o"].append(f"{db.name}#{iid}")
    han = int(getattr(vd, "URL_TRINH_DUYET_HAN_NGAY", 180))
    for m in theo_url.values():
        ok, info = vd.xac_minh_url_bang_trinh_duyet(m["url"], m["dashboard_mau"], hom_nay=hom_nay)
        ngay = _ngay_bang_chung(info) if ok is True else None
        if ok is True and ngay is not None:
            con = han - (hom_nay - ngay).days
            m["con_ngay"] = con
            m["trang_thai"] = "SAP_HET_HAN" if con <= canh_bao_truoc else "CON_HAN"
            m["ly_do"] = info
        else:
            m["trang_thai"] = "THIEU"
            m["ly_do"] = info
    return sorted(theo_url.values(), key=lambda x: ({"THIEU": 0, "SAP_HET_HAN": 1, "CON_HAN": 2}[x["trang_thai"]], x["url"]))


def can_xac_nhan(ds: list[dict]) -> list[dict]:
    return [m for m in ds if m["trang_thai"] != "CON_HAN"]


def kiem_tieu_de(tieu_de: str) -> str | None:
    """Lý do từ chối tiêu đề (trang chặn/lỗi/chung chung/quá ngắn); None nếu nhận."""
    t = (tieu_de or "").strip()
    if len(t) < 10:
        return "tiêu đề < 10 ký tự — chưa phải tiêu đề trang thật"
    if _TIEU_DE_CAM.search(t):
        return f"tiêu đề giống trang CHẶN BOT/LỖI («{t[:60]}») — trang thật chưa hiện, chưa được ghi"
    if t.casefold().strip(" .") in _TIEU_DE_CHUNG:
        return f"tiêu đề chỉ là tên cơ quan («{t}») — chưa phải tài liệu cụ thể"
    return None


def ghi(vd, url: str, tieu_de: str, cach: str, nguoi_kiem: str, thu_muc: Path | None = None,
        hom_nay: date | None = None, sao_luu: Path | None = None) -> tuple[int, str]:
    """Ghi MỘT bằng chứng trình duyệt. Trả (mã, thông điệp): 0 ghi xong và cổng nhận · 2 không ghi được · 3 từ chối."""
    thu_muc, sao_luu = thu_muc or DASH, sao_luu or SAO_LUU
    hom_nay = hom_nay or date.today()
    url = (url or "").strip()
    if not vd.mien_chan_tu_dong(url):
        return 3, ("miền của URL này CHƯA khai trong MIEN_CHAN_TRUY_CAP_TU_DONG — sổ trình duyệt chỉ dành cho miền chặn bot đã "
                   "khai kèm bằng chứng; thêm miền mới là một thay đổi CỔNG (qua PR), không ghi sổ để lách")
    ly_do = kiem_tieu_de(tieu_de)
    if ly_do:
        return 3, ly_do
    if len((cach or "").strip()) < 10:
        return 3, "thiếu --cach (đã mở bằng gì, đã đọc gì để xác nhận đúng tài liệu)"
    ten_so = getattr(vd, "SO_URL_TRINH_DUYET", "url-xac-minh-trinh-duyet.json")
    tep = thu_muc / ten_so
    if tep.exists():
        try:
            du_lieu = json.loads(tep.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            return 2, f"{ten_so} đọc không được ({type(e).__name__}) — KHÔNG ghi đè sổ hỏng; khôi phục bản sao lưu trước"
        if not isinstance(du_lieu, dict) or not isinstance(du_lieu.get("muc"), list):
            return 2, f"{ten_so} sai cấu trúc (thiếu danh sách 'muc') — KHÔNG ghi đè"
    else:
        du_lieu = {"_about": "Sổ bằng chứng mở URL bằng trình duyệt thật cho miền chặn bot — xem verify_dashboard.py.", "muc": []}
    dung_o = sorted({db.name for db in thu_muc.glob("WebDashboard_*.html")
                     if any(u == url for _i, u in url_mien_chan_cua_dashboard(db, vd))})
    if tep.exists():
        sao_luu.mkdir(parents=True, exist_ok=True)
        ban = sao_luu / f"{ten_so}.{datetime.now().strftime('%Y%m%d-%H%M%S')}.bak"
        shutil.copyfile(tep, ban)
        if ban.read_bytes() != tep.read_bytes():
            return 2, f"bản sao lưu không khớp byte ({ban}) — dừng, không ghi"
    goc = tep.read_bytes() if tep.exists() else None
    du_lieu["muc"].append({"url": url, "tieu_de": tieu_de.strip(), "ngay": hom_nay.isoformat(), "cach": cach.strip(),
                           "nguoi_kiem": nguoi_kiem, "dung_o": dung_o})
    tam = tep.with_name(tep.name + f".tmp{os.getpid()}")
    tam.write_text(json.dumps(du_lieu, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    os.replace(tam, tep)
    cho = thu_muc / (dung_o[0] if dung_o else "WebDashboard_khong_co.html")
    ok, info = vd.xac_minh_url_bang_trinh_duyet(url, cho, hom_nay=hom_nay)
    if ok is not True:   # cổng không nhận ⇒ hoàn nguyên đúng byte cũ, không để lại mục rác
        if goc is None:
            tep.unlink(missing_ok=True)
        else:
            tep.write_bytes(goc)
        return 2, f"ghi xong nhưng CỔNG không nhận ({info}) — đã hoàn nguyên sổ"
    return 0, f"đã ghi; cổng nhận: {info}" + ("" if dung_o else " (chưa dashboard nào trích URL này)")


def in_hang_cho(ds: list[dict]) -> None:
    cho = can_xac_nhan(ds)
    print(f"TRANG CHẶN BOT — {len(ds)} URL miền chặn đang được trích · {len(cho)} chờ bác sĩ xác nhận trên trình duyệt")
    for i, m in enumerate(cho, 1):
        nhan = "THIẾU bằng chứng" if m["trang_thai"] == "THIEU" else f"còn {m['con_ngay']} ngày"
        print(f"  {i}. [{nhan}] {m['url']}")
        print(f"     dùng ở: {', '.join(m['dung_o'][:3])}{' …' if len(m['dung_o']) > 3 else ''}")
        if m["trang_thai"] == "THIEU":
            print(f"     lý do: {m['ly_do'][:160]}")
    if cho:
        print("\n  → Mở từng URL trong khung trình duyệt; trang chặn bot thì BÁC SĨ tự bấm xác nhận. Quy trình: --huong-dan")
    print("Cần bác sĩ kiểm chứng.")


def main(argv: list[str] | None = None) -> int:
    for luong in (sys.stdout, sys.stderr):
        try:
            if "utf" not in (getattr(luong, "encoding", "") or "").lower() and hasattr(luong, "reconfigure"):
                luong.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Trang chặn bot: hàng chờ bác sĩ xác nhận + ghi bằng chứng trình duyệt")
    ap.add_argument("--huong-dan", action="store_true", help="in quy trình từng bước")
    ap.add_argument("--ghi", metavar="URL", help="ghi bằng chứng cho URL này (sau khi trang thật đã hiện)")
    ap.add_argument("--tieu-de", default="", help="document.title của trang THẬT")
    ap.add_argument("--cach", default="", help="đã mở bằng gì và đã đọc gì để xác nhận")
    ap.add_argument("--nguoi-kiem", default="Claude (Claude_Browser) — bác sĩ tự vượt kiểm tra chống bot",
                    help="ai mở/ai xác nhận")
    ap.add_argument("--json", default="", help="ghi hàng chờ máy đọc ra tệp này")
    a = ap.parse_args(argv)
    if a.huong_dan:
        print(HUONG_DAN)
        return 0
    if not DASH.is_dir():
        print("⚪ KHÔNG ĐO ĐƯỢC — máy này không có EBM-Dashboards/ (bản sao trần/Cloud). KHÔNG phải «không có URL chờ».")
        return 2
    try:
        vd = nap_cong()
    except BaseException as e:  # noqa: BLE001 — chốt hỏng phải LỘ RA
        if isinstance(e, KeyboardInterrupt):
            raise
        print(f"⚪ KHÔNG ĐO ĐƯỢC — không nạp được cổng verify_dashboard.py: {type(e).__name__}: {e}")
        return 2
    if a.ghi:
        ma, tb = ghi(vd, a.ghi, a.tieu_de, a.cach, a.nguoi_kiem)
        print(("✓ " if ma == 0 else "✗ ") + tb)
        return ma
    ds = quet(vd)
    if a.json:
        Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        Path(a.json).write_text(json.dumps([{k: v for k, v in m.items() if k != "dashboard_mau"} for m in ds],
                                           ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    in_hang_cho(ds)
    return 1 if can_xac_nhan(ds) else 0


if __name__ == "__main__":
    sys.exit(main())
