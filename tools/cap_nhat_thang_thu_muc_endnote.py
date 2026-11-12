#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CẬP NHẬT CHỨNG CỨ HẰNG THÁNG THEO THƯ MỤC ENDNOTE — phiếu tháng + phần MÁY (12/11/2026).

Bác sĩ nói trong chat 12/11/2026, nguyên văn: «Xây dựng tự động cập nhật chứng cứ hàng tháng với các thư mục trong Endnote»;
bổ sung cùng ngày: «Với việc cập nhật những chứng cứ áp dụng cho thực hành lâm sàng đảm bảo toàn văn và tóm tắt như đã xây
dựng cho hệ thống cập nhật chứng cứ».

VÌ SAO CÓ. Thư viện EndNote là nơi bác sĩ ĐỌC chứng cứ (mỗi chủ đề một thư mục «EBM · …» hoặc thư mục bác sĩ tự đặt), còn dây
chuyền cập nhật đi theo DASHBOARD và WATCHLIST. Không công cụ nào nhìn từ phía thư mục: thư mục nào đã cũ, thư mục nào không
được bộ quét canh, thư mục nào chưa từng có dashboard, mục «Áp dụng» nào trong thư mục còn thiếu toàn văn/PDF/tóm tắt. Kiểm kê
tay 12/11/2026: 165 thư mục có bài, 96 gắn dashboard, 69 chưa gắn.

LÀM GÌ (mỗi thư mục EndNote có bài — đọc bản sao tạm `sdb.eni`, CHỈ ĐỌC):
  • gắn dashboard nào (khoá `nhom_theo_chu_de` của ~/.ebm-endnote.json) · bản mới nhất ngày nào · độ tươi;
  • chủ đề có trong watchlist chưa (`tools/chu_de_resolver.py` — chỉ tin ánh xạ NGƯỜI khai, BH28);
  • ứng viên mạnh trong ~35 ngày: ĐỌC báo cáo quét đã có (`EBM-Dashboards/surveillance/tuan-*-quet.json` của gói tuần,
    `logs/*.A2-*.json` của orchestrator) — chế độ báo cáo KHÔNG gọi mạng;
  • M1/M2 của `tools/kiem_moi_nhat_toan_van.py` trên bản mới nhất;
  • số bản ghi thiếu PDF toàn văn và thiếu khối tiếng Việt trong thư mục;
  • RIÊNG các mục `apply` (và ★ «Áp dụng – tin cậy cao», luật `gan_tag_endnote.dat_ap_dung_tin_cay`): toàn văn trong kho (nguồn
    sự thật `doc_toan_van_co_nguoi.bao_phu_cuc_bo` — cổng BH161 dùng cùng định nghĩa) · PDF đã gắn vào bản ghi EndNote
    (`file_res`, không tính PDF tóm tắt `_TomTatChungCu.pdf`) · khối «【EBM · ĐỌC NHANH】» trong Abstract
    (`tom_tat_endnote_vi.MO_DAU_DA_DUNG`) · tóm tắt Word ⑨ (`tom_tat_chung_cu_word.hang_cho` + tệp Word đã có).

XẾP NHÓM HÀNH ĐỘNG (mỗi thư mục đúng một nhóm):
  (a) CẦN BẢN NỐI TIẾP — lát cắt có guideline/đồng thuận mới, hoặc ≥ NGUONG_SR_RCT tổng quan/RCT mới chưa có trong dashboard,
      hoặc M1 (guideline ≥ 5 năm chưa kiểm phiên bản), hoặc dashboard quá HAN_TUOI_NGAY ngày;
  (b) CẦN THÊM VÀO WATCHLIST — có dashboard mà chủ đề gốc không được watchlist canh: máy CHỈ ĐỀ XUẤT ở
      `EBM-Dashboards/watchlist.de-xuat.json` khoá `_de_xuat_thu_muc_endnote` (§6.4) — KHÔNG sửa watchlist.json;
  (c) CHƯA GẮN DASHBOARD — tách «nội dung thật của bác sĩ» khỏi nhóm EBM cũ/bản tin, thư mục khung (≤ NGUONG_KHUNG bài), NC/TT;
  (d) ỔN — 🟢 khi mọi trục đã đo; ⚪ khi còn trục KHÔNG ĐO ĐƯỢC (§0.2: không đo được không bao giờ là xanh).

CHẾ ĐỘ (chạy khô mặc định — không ghi, không gọi lệnh nào):
  python3 tools/cap_nhat_thang_thu_muc_endnote.py                       # in tóm tắt, không ghi gì
  python3 tools/cap_nhat_thang_thu_muc_endnote.py --ghi                 # ghi phiếu tháng (.md + .json) + đề xuất watchlist
  python3 tools/cap_nhat_thang_thu_muc_endnote.py --quet --toi-da 3     # (khô) in lệnh orchestrator sẽ chạy
  python3 tools/cap_nhat_thang_thu_muc_endnote.py --quet --toi-da 3 --hoan-thien --ghi       # LƯỢT LỊCH tháng (không ghi EndNote)
  python3 tools/cap_nhat_thang_thu_muc_endnote.py --hoan-thien --ghi-endnote --ghi           # PHIÊN CLAUDE có người: thêm ③④
  python3 tools/cap_nhat_thang_thu_muc_endnote.py --json                # in JSON phân tích (khô)
  Vì sao `--ghi` mà không `--ap-dung`, và vì sao ③④ cần cờ riêng: ranh giới quyền lượt lịch (`sync/quyen-lich-nen.json`
  `_ranh_gioi`, chốt BH173 `test_khai_khong_chua_lenh_ghi_quyet_dinh_thay_bac_si`, bác sĩ duyệt 28/10/2026) chỉ cho lượt lịch
  ĐO/BÁO/DỰNG GÓI — phiếu, đề xuất, quét candidate, gom toàn văn vào kho đều thuộc loại đó (gói tuần đã chạy đúng các việc này);
  GHI EndNote (`nap_endnote_chu_de … --ap-dung`) thì KHÔNG khai cho lượt lịch. Nên lượt lịch chạy ①② và liệt kê ③④ thành việc 🛎
  cho phiên Claude; đổi ranh giới là quyết định của bác sĩ (sửa `_ranh_gioi` + chốt kèm nguyên văn lời bác sĩ), không phải đổi cờ.
  • `--quet`: gọi `ops/orchestrator.py --topic "<lát cắt>" --online` TUẦN TỰ cho thư mục nhóm (a) có chủ đề trong watchlist (A2
    quét `--khong-cursor` → toàn văn → sổ xác minh → cổng → hàng chờ). KHÔNG dựng dashboard, KHÔNG gọi agent. Trần `--toi-da`
    (≤ TRAN_QUET), nghỉ giữa hai chủ đề, hạ tầng hỏng (mã 2: mạng/NCBI chặn/khoá bận) ⇒ dừng cả lượt. Vẫn là candidate-only.
  • `--hoan-thien`: dây chuyền §6.2 phần MÁY cho mục apply/consider của các dashboard trong phiếu — ① gom toàn văn OA
    (`gom_toan_van_dashboard.py --pmid … --unpaywall`) → ② in HTML trong kho sang PDF (`in_pdf_toan_van_kho.py --pmid … --ap-dung`)
    → ③ gắn PDF kho vào bản ghi EndNote (`nap_endnote_chu_de.py --gan-kho --pmid … --ap-dung --chi-khi-dang-mo`) → ④ khối tiếng
    Việt (`--tom-tat-vi --file …`, và `--tom-tat-thu-vien` khi thư mục ngoài dashboard còn bài thiếu khối). ③④ GHI EndNote: chỉ
    chạy khi có THÊM `--ghi-endnote` (phiên có người — xem dưới), trên Mac, khi `endnote_suc_khoe` 🟢, không có giao dịch
    treo, không có khoá `~/.ebm-endnote-dang-ghi.json` của tiến trình khác, không có cờ
    `~/.ebm-worktrees/_giao-viec-c2/TAM-DUNG-ENDNOTE` — kiểm lại TRƯỚC TỪNG bước ghi; một điều kiện hỏng ⇒ dừng phần ghi.
    Làn Chrome (bài không OA) và tóm tắt Word ⑨ (agent, tốn token) KHÔNG BAO GIỜ tự chạy — chỉ liệt kê trong phiếu cho bác sĩ
    duyệt kèm ước tính chi phí.
  Có `--quet`/`--hoan-thien` mà không `--ghi` ⇒ chỉ in kế hoạch. Đã chạy bước máy ⇒ đo lại rồi mới ghi phiếu.

KHÔNG làm: không ghi EndNote ngoài ③④ có rào; không đổi decision/gradeLevel; không tự áp dụng; không sửa watchlist.json; không
dựng dashboard; không mở agent hay làn Chrome. Bản nối tiếp dashboard (agent ≈ 0,5–0,8 triệu token/chủ đề) CHỈ làm khi bác sĩ
duyệt danh sách trong phiếu.

Mã thoát: 0 = không thư mục nào cần việc · 1 = có việc (a/b/c-nội dung thật/mục apply thiếu) · 2 = KHÔNG ĐO ĐƯỢC (không đọc được
cả thư viện EndNote lẫn cấu hình, hoặc vắng EBM-Dashboards/) · 3 = tham số sai.
Chạy cả Mac lẫn Windows (`Path(__file__)`, `sys.executable`, UTF-8); bước ghi EndNote chỉ Mac. Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import datetime as dt
import difflib
import html
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

GOC = Path(__file__).resolve().parents[1]
PY = sys.executable  # BH05: không gọi "python3" cứng — Windows không có

CUA_SO_UNG_VIEN_NGAY = 35      # báo cáo quét trong ~35 ngày (một tháng + đệm cho kỳ lịch lệch)
HAN_TUOI_NGAY = 90             # dashboard quá chừng này ⇒ cần bản nối tiếp
NGUONG_SR_RCT = 5              # ≥ 5 tổng quan/gộp/RCT MỚI (lần đầu trình sau ngày dashboard) ⇒ cần bản nối tiếp — đo 12/11/2026:
                               # bộ quét tuần trình ≤ 6/tầng nên ngưỡng 3 kéo gần mọi chủ đề vào (a)
NGUONG_KHUNG = 2               # thư mục ≤ 2 bài, không dashboard ⇒ thư mục KHUNG (cấu trúc phân loại, chưa có nội dung)
TOI_DA_QUET_MAC_DINH = 3
TRAN_QUET = 8                  # cùng trần lô của ops/orchestrator.py (TRAN_LO)
NGHI_GIUA_QUET_GIAY = 30       # nghỉ giữa hai chủ đề — tôn trọng NCBI (bộ quét tự giới hạn nhịp bên trong)
TIMEOUT_QUET_GIAY = 4 * 3600   # một chủ đề: A2 1800 + TV 3300 + A4/B2 mỗi lát cắt 3600 + B5 600 (TIMEOUT_BUOC của orchestrator)
TOI_DA_PMID_HOAN_THIEN = 80    # trần PMID mỗi lượt gom toàn văn (apply trước)
TIMEOUT_HOAN_THIEN = {"gom": 3600, "in_pdf": 1800, "gan_kho": 1800, "tom_tat_vi": 1800, "tom_tat_thu_vien": 1800}
UOC_TINH_NOI_TIEP = (0.5, 0.8)  # triệu token / chủ đề (agent dựng bản nối tiếp)
UOC_TINH_WORD9 = (0.3, 0.6)     # triệu token / bài ⑨ (đo 12/11/2026: CPIC 41618934 ≈ 0,56 triệu)

TIEN_TO_TEP = "CAP-NHAT-THANG-THU-MUC_"
KHOA_DE_XUAT = "_de_xuat_thu_muc_endnote"
CO_TAM_DUNG_MAC_DINH = Path.home() / ".ebm-worktrees" / "_giao-viec-c2" / "TAM-DUNG-ENDNOTE"
TIEN_TO_NC_TT = ("NC ·", "TT ·")
TIEN_TO_EBM = "EBM ·"
KHOA_NC_TT = ("DE-TAI_", "TONG-THUAT_")
PT_GUIDELINE = {"practice guideline", "guideline", "consensus statement"}
PT_SR = {"systematic review", "meta-analysis", "network meta-analysis"}
PT_RCT = {"randomized controlled trial"}
_TEN_DASH = re.compile(r"^WebDashboard_(.+)_(\d{8})\.html$")
_PMID = re.compile(r"^\d{1,9}$")

NHAN_NHOM = {"a": "(a) cần bản nối tiếp", "b": "(b) cần thêm vào watchlist", "c": "(c) chưa gắn dashboard", "d": "(d) ổn"}
NHAN_C = {"noi_dung_that": "nội dung thật của bác sĩ", "ebm_cu": "nhóm EBM cũ/bản tin", "khung": "thư mục khung",
          "nc_tt": "đề tài NC / tổng thuật TT"}


# ───────────────────────── nạp công cụ dùng chung (một nguồn, không chép logic) ─────────────────────────

_MOD: dict[str, object] = {}


def _nap(ten: str, duong: Path):
    if ten not in _MOD:
        sp = importlib.util.spec_from_file_location(ten, duong)
        m = importlib.util.module_from_spec(sp)
        sys.modules[ten] = m
        sp.loader.exec_module(m)
        _MOD[ten] = m
    return _MOD[ten]


def _cong_cu(tep: str):
    return _nap("_cntm_" + Path(tep).stem, GOC / "tools" / tep)


def _goc_du_lieu(ten: str) -> Path:
    """Gốc dữ liệu ngoài git (lồng rồi anh em — `ban_sao_tran.duong_goc`); không thấy ⇒ vị trí lồng (người gọi tự rào vắng)."""
    try:
        return _cong_cu("ban_sao_tran.py").duong_goc(ten, GOC) or (GOC / ten)
    except Exception:  # noqa: BLE001 — không nạp được bộ định vị ⇒ vị trí lồng
        return GOC / ten


def _cong_cu_pipeline(tep: str):
    """Công cụ dây chuyền dashboard (bản máy thật trước, bản vendor git sau) — cùng resolver bộ năm dùng."""
    duong = _cong_cu("ban_sao_tran.py").duong_cong_cu_pipeline(tep, GOC)
    if duong is None:
        raise FileNotFoundError(tep)
    return _nap("_cntm_pl_" + Path(tep).stem, duong)


# ───────────────────────── đọc nguồn thật (không thuần — mỗi hàm tự rào «không đo được») ─────────────────────────

def doc_cau_hinh_endnote(tep: Path | None = None) -> tuple[dict | None, str | None]:
    """(cấu hình, lý do không đọc được). Cùng tệp `nap_endnote_chu_de` đọc (~/.ebm-endnote.json)."""
    tep = tep or (Path.home() / ".ebm-endnote.json")
    try:
        d = json.loads(tep.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return None, f"không đọc được {tep.name} ({type(e).__name__})"
    if not isinstance(d, dict):
        return None, f"{tep.name} không phải đối tượng JSON"
    return d, None


def doc_thu_vien(thu_vien: Path) -> dict:
    """Nhóm + bản ghi của thư viện EndNote — đọc BẢN SAO TẠM (`endnote_suc_khoe.ban_sao_csdl`, mode=ro). Không bao giờ ghi.

    Trả {"nhom": [{group_id, ten, loai, rec, loi?}], "ban_ghi": {rec: {pmid, doi, pdf, khoi_vi}}, "thung_rac": {định danh}}.
    Lỗi ⇒ ném (người gọi ⚪). Định danh của bản ghi TRONG THÙNG RÁC tách riêng: bác sĩ đã bỏ ⇒ không mời «nạp lại»."""
    sk = _cong_cu("endnote_suc_khoe.py")
    ttv = _cong_cu("tom_tat_endnote_vi.py")
    ndt = _cong_cu("nap_endnote_de_tai.py")
    nec = _cong_cu("nap_endnote_chu_de.py")
    with sk.ban_sao_csdl(Path(thu_vien)) as kn:
        nhom = sk._doc_nhom_kn(kn)
        tep: dict[int, list[str]] = {}
        for rid, fp in kn.execute("SELECT refs_id, file_path FROM file_res"):
            tep.setdefault(int(rid), []).append(str(fp or ""))
        ban_ghi: dict[int, dict] = {}
        thung_rac: set[str] = set()
        for rid, acc, erd, ab, rac in kn.execute("SELECT id, accession_number, electronic_resource_number, abstract, trash_state "
                                                 "FROM refs"):
            acc = str(acc or "").strip()
            if rac:
                thung_rac |= {x for x in (acc if _PMID.match(acc) else None, nec.chuan_doi(erd) if erd else None) if x}
                continue
            ban_ghi[int(rid)] = {"pmid": acc if _PMID.match(acc) else None,
                                 "doi": nec.chuan_doi(erd) if erd else None,
                                 "pdf": ndt.co_toan_van("\n".join(tep.get(int(rid), []))),
                                 "khoi_vi": ttv.chuan_dong(str(ab or "")).startswith(ttv.MO_DAU_DA_DUNG)}
    return {"nhom": nhom, "ban_ghi": ban_ghi, "thung_rac": thung_rac}


def bo_qua_cau_hinh(ch: dict | None) -> set[str]:
    """PMID/DOI bác sĩ đã loại (`bo_qua` của ~/.ebm-endnote.json, khuôn `nap_endnote_chu_de.doc_loai_tru`)."""
    ra: set[str] = set()
    nec = None
    for x in (ch or {}).get("bo_qua") or []:
        if not isinstance(x, dict):
            continue
        if x.get("pmid") and _PMID.match(str(x["pmid"]).strip()):
            ra.add(str(x["pmid"]).strip())
        if x.get("doi"):
            nec = nec or _cong_cu("nap_endnote_chu_de.py")
            d = nec.chuan_doi(x["doi"])
            if d:
                ra.add(d)
    return ra


def dashboards_moi_nhat(dash_dir: Path) -> dict[str, dict]:
    """{khoá chủ đề: {"tep", "ngay", "cac_ban": [(ngay, tệp)]}} — khoá = tên tệp bỏ «WebDashboard_» và «_YYYYMMDD»
    (đúng `nap_endnote_chu_de.khoa_chu_de`). Bỏ tệp sao lưu `.bak-*` (không khớp đuôi .html)."""
    ra: dict[str, dict] = {}
    for p in sorted(Path(dash_dir).glob("WebDashboard_*.html")):
        m = _TEN_DASH.match(p.name)
        if not m:
            continue
        khoa, ngay = m.group(1), m.group(2)
        muc = ra.setdefault(khoa, {"tep": p, "ngay": ngay, "cac_ban": []})
        muc["cac_ban"].append((ngay, p))
        if ngay > muc["ngay"]:
            muc.update(tep=p, ngay=ngay)
    return ra


def doc_bao_cao_quet(dash_dir: Path, logs_dir: Path, bay_gio: dt.datetime) -> dict:
    """Báo cáo quét: {"bao_cao": [{tep, luc, topics: {tên: [ứng viên]}}] (chỉ trong CUA_SO_UNG_VIEN_NGAY), "lan_dau": {PMID/URL:
    lúc ĐẦU TIÊN bộ quét trình bài đó (đọc MỌI báo cáo, không giới hạn cửa sổ)}, "loi": [...]}.

    Nguồn: `EBM-Dashboards/surveillance/tuan-*-quet.json` (gói tuần) + `logs/*.A2-*.json` (orchestrator). Mốc thời gian đọc
    TRONG nội dung (`finished_at`), không dùng mtime (OneDrive làm mtime tươi giả). Chủ đề PASS_DEGRADED/FAIL không được tính là
    «đã quét» (0 ứng viên ở đó không phải «không có chứng cứ mới»). «Lần đầu» cho biết ứng viên có MỚI với hệ sau ngày dashboard
    không: bộ quét lấy cửa sổ 90 ngày nên mỗi tuần trình lại bài cũ — bài đã trình trước khi dựng dashboard là bài người soạn đã
    có dịp xét (đo 12/11/2026: tính theo «lần đầu» thay vì «có mặt» cắt số tổng quan/RCT mới của nhóm suy tim từ 25 xuống 13)."""
    ra: dict = {"bao_cao": [], "lan_dau": {}, "loi": []}
    tep = sorted((Path(dash_dir) / "surveillance").glob("tuan-*-quet.json")) + sorted(Path(logs_dir).glob("*.A2-*.json"))
    for f in tep:
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            luc = dt.datetime.fromisoformat(str(d.get("finished_at")))
        except (OSError, ValueError, TypeError) as e:
            ra["loi"].append(f"{f.name}: {type(e).__name__}")
            continue
        if luc.tzinfo is not None:
            luc = luc.astimezone().replace(tzinfo=None)
        topics = {}
        for t in d.get("topics") or []:
            if isinstance(t, dict) and t.get("topic") and str(t.get("status") or "PASS") == "PASS":
                topics[str(t["topic"])] = [c for c in t.get("candidates") or [] if isinstance(c, dict)]
        for cs in topics.values():
            for c in cs:
                k = str(c.get("pmid") or c.get("url") or "").strip()
                if k and (k not in ra["lan_dau"] or luc < ra["lan_dau"][k]):
                    ra["lan_dau"][k] = luc
        if 0 <= (bay_gio - luc).days <= CUA_SO_UNG_VIEN_NGAY:
            ra["bao_cao"].append({"tep": f.name, "luc": luc, "topics": topics})
    return ra


class DoDashboard:
    """Đo MỘT dashboard bằng đúng công cụ của hệ: DATA (build_ban_doc_chung_cu) · M1/M2 (kiem_moi_nhat_toan_van) · định danh
    (nap_endnote_chu_de.trich_dinh_danh) · ★ (gan_tag_endnote.dat_ap_dung_tin_cay). Nạp công cụ một lần."""

    def __init__(self) -> None:
        self.bbd = _cong_cu_pipeline("build_ban_doc_chung_cu.py")
        self.vd = _cong_cu_pipeline("verify_dashboard.py")
        self.kmn = _cong_cu("kiem_moi_nhat_toan_van.py")
        self.nec = _cong_cu("nap_endnote_chu_de.py")
        self.gte = _cong_cu("gan_tag_endnote.py")

    def doc_data(self, tep: Path) -> dict | None:
        try:
            return self.bbd.extract_data(Path(tep).read_text(encoding="utf-8", errors="replace"))
        except (SystemExit, OSError, ValueError):
            return None

    def cau_hoi(self, tep: Path) -> str | None:
        d = self.doc_data(tep)
        return self.nec.ten_chu_de(d, Path(tep)) if d else None

    def __call__(self, tep: Path) -> dict:
        data = self.doc_data(tep)
        if data is None:
            return {"doc_duoc": False}
        co_tv = getattr(self.vd, "co_toan_van_trong_kho", None)
        kq = self.kmn.kiem(data, Path(tep).parent / "toan_van_oa", co_toan_van=co_tv)
        dd = self.nec.trich_dinh_danh(data)
        muc = []
        for it in data.get("items") or []:
            if not isinstance(it, dict):
                continue
            quyet = str(it.get("decision") or "").strip().lower()
            if quyet not in ("apply", "consider"):
                continue
            pm = str(it.get("pmid") or "").strip()
            muc.append({"id": str(it.get("id") or "(?)"), "pmid": pm if _PMID.match(pm) else None,
                        "doi": self.nec.chuan_doi(it.get("doi")), "decision": quyet,
                        "sao": quyet == "apply" and self.gte.dat_ap_dung_tin_cay(
                            [{"vai": "muc", "decision": quyet, "gradeLevel": it.get("gradeLevel"),
                              "design": it.get("design"), "ban_cu": False}])})
        return {"doc_duoc": True, "cau_hoi": self.nec.ten_chu_de(data, Path(tep)),
                "pmids": {d["pmid"] for d in dd if d.get("pmid")}, "dois": {d["doi"] for d in dd if d.get("doi")},
                "m1": len(kq["m1"]) + len(kq["m1_cu"]), "m2": len(kq["m2"]), "m2_khong_do": len(kq["khong_do"]),
                "m1_ds": [d["id"] for d in kq["m1"] + kq["m1_cu"]], "muc": muc}


def toan_van_kho(pmids: list[str], kho: Path) -> dict[str, bool] | None:
    """{PMID: đã đọc toàn văn?} theo NGUỒN SỰ THẬT `doc_toan_van_co_nguoi.bao_phu_cuc_bo` (cổng BH161 cùng định nghĩa).
    Kho vắng ⇒ None (không đo được — không bao giờ «đủ»)."""
    if not Path(kho).is_dir():
        return None
    dtv = _cong_cu("doc_toan_van_co_nguoi.py")
    tt = dtv.bao_phu_cuc_bo(sorted(set(pmids)), Path(kho))
    return {pm: tt[pm] in dtv.TRANG_THAI_DA_PHU for pm in tt}


def doc_so_no(dash_dir: Path) -> set[tuple[str, str, str]]:
    """Khoá (dashboard, item, pmid) của sổ nợ toàn văn apply (`so_toan_van.doc_so_no`); vắng/hỏng ⇒ rỗng (cổng coi như vắng)."""
    try:
        so = _cong_cu("so_toan_van.py").doc_so_no(Path(dash_dir))
    except Exception:  # noqa: BLE001
        return set()
    if not so or "hong" in so:
        return set()
    return {(str(x.get("dashboard")), str(x.get("item")), str(x.get("pmid"))) for x in so.get("muc") or []
            if isinstance(x, dict)}


def doc_word9(thu_vien: Path) -> dict:
    """⑨: {"hang_cho": [bản ghi chờ], "da_co": {khoá «PMID-n»/«REC-n» đã có Word}} hoặc {"loi": lý do} — cùng hàm
    `tom_tat_chung_cu_word.hang_cho` (mốc 19/10, ngoại lệ mốc, chính sách «chỉ ★», loại bài chỉ thuộc đề tài)."""
    try:
        ttw = _cong_cu("tom_tat_chung_cu_word.py")
        hc = ttw.hang_cho(Path(thu_vien))
        thu_muc = ttw.thu_muc_ra(Path(thu_vien))
        da_co = {p.name[: -len("_TomTatChungCu.docx")] for p in thu_muc.glob("*_TomTatChungCu.docx")} if thu_muc.is_dir() else set()
    except Exception as e:  # noqa: BLE001 — hàng chờ không đo được ⇒ ⚪, không phải «không có bài chờ»
        return {"loi": f"{type(e).__name__}: {str(e)[:160]}"}
    if hc is None:
        return {"loi": "chưa có mốc «để nguyên» của hàng chờ ⑨ (tom_tat_chung_cu_word.py moc) — không đoán"}
    return {"hang_cho": hc, "da_co": da_co}


# ───────────────────────── phân tích (THUẦN — test bằng fixture) ─────────────────────────

def _chuan(s: str) -> str:
    try:
        return _cong_cu("chu_de_resolver.py").chuan(s)
    except Exception:  # noqa: BLE001
        return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def phan_loai_ung_vien(c: dict) -> str | None:
    """«guideline» · «sr_ma» · «rct» theo LOẠI XUẤT BẢN THẬT của PubMed; None = không tính là mạnh. Tên tầng không đủ (tầng
    guideline có cả bài chỉ khớp tiêu đề) và `authority_source` không đủ (đó là hội gắn với TẠP CHÍ — đo 12/11/2026: một tổng quan
    trên Diabetologia mang «ADA/EASD»). Bỏ: đã có trong kho, chưa bình duyệt (preprint), rút bài khác ok/chưa kiểm."""
    if c.get("da_co_trong_kho") or c.get("chua_binh_duyet"):
        return None
    if str(c.get("rut_bai") or "ok") not in ("ok", "chua_kiem"):
        return None
    pt = {str(x).strip().lower() for x in c.get("pubtype") or []}
    if pt & PT_GUIDELINE:
        return "guideline"
    if pt & PT_SR:
        return "sr_ma"
    if pt & PT_RCT:
        return "rct"
    return None


def ung_vien_manh(bao_cao: list[dict], topic: str, tu_ngay: dt.date, pmid_da_co: set[str],
                  lan_dau: dict[str, dt.datetime] | None = None) -> dict:
    """Ứng viên mạnh MỚI cho một chủ đề watchlist từ các báo cáo quét KẾT THÚC từ `tu_ngay` (ngày dashboard) trở đi.

    {"so_bao_cao": n, "guideline": [...], "sr_ma": [...], "rct": [...]} — n = 0 ⇒ chưa có lượt quét nào sau dashboard trong cửa
    sổ ⇒ người gọi ⚪ (không phải «0 ứng viên»). Loại: bài có định danh trong dashboard (đã đưa vào) và bài bộ quét đã trình
    LẦN ĐẦU vào/trước ngày dashboard (`lan_dau` — người soạn đã có dịp xét)."""
    ra: dict = {"so_bao_cao": 0, "guideline": [], "sr_ma": [], "rct": []}
    thay: set[str] = set()
    for bc in sorted(bao_cao, key=lambda x: x["luc"], reverse=True):
        if topic not in bc["topics"] or bc["luc"].date() < tu_ngay:
            continue
        ra["so_bao_cao"] += 1
        for c in bc["topics"][topic]:
            loai = phan_loai_ung_vien(c)
            dd = str(c.get("pmid") or c.get("url") or "").strip()
            if loai is None or not dd or dd in thay or dd in pmid_da_co:
                continue
            if lan_dau is not None and dd in lan_dau and lan_dau[dd].date() <= tu_ngay:
                continue
            thay.add(dd)
            ra[loai].append({"pmid": str(c.get("pmid") or ""), "tieu_de": str(c.get("title") or "")[:160],
                             "ngay": str(c.get("publication_date") or ""), "nguon": str(c.get("authority_source") or ""),
                             "bao_cao": bc["tep"]})
    return ra


def goi_y_gan_ten(goc: str, watchlist: list[str]) -> list[str]:
    """Mục watchlist GẦN TÊN chủ đề gốc — CHỈ để bác sĩ xem, máy không ghép (BH28). Chuỗi gốc đã gấp (≥ 4 ký tự) nằm trong tên
    mục, hoặc độ giống ≥ 0,8 (ngưỡng thấp hơn gợi nhầm: đo 12/11/2026 với 0,5 «Tăng áp phổi» → «Tăng huyết áp», «PTSD» → «BPH»)."""
    cg = _chuan(goc)
    bang = {_chuan(w): w for w in watchlist}
    ra = [w for k, w in bang.items() if len(cg) >= 4 and cg in k]
    ra += [bang[k] for k in difflib.get_close_matches(cg, list(bang), n=3, cutoff=0.8) if bang[k] not in ra]
    return ra[:3]


def phan_loai_c(ten: str, so_bai: int | None, khoa: list[str], cau_hoi_cu: dict[str, str]) -> tuple[str, str]:
    """(phụ loại, ghi chú) của thư mục chưa gắn dashboard."""
    t = (ten or "").strip()
    if t.startswith(TIEN_TO_NC_TT) or any(k.startswith(KHOA_NC_TT) for k in khoa):
        return "nc_tt", "đề tài nghiên cứu / tổng thuật — ngoài nhịp chứng cứ tháng (nạp bằng --de-tai/--tong-thuat)"
    if t.startswith(TIEN_TO_EBM):
        cu = cau_hoi_cu.get(_khoa_ten(t))
        if cu:
            return "ebm_cu", f"nhóm của bản dashboard CŨ «{cu}» — khoá chủ đề nay trỏ nhóm khác (bác sĩ quyết gộp/lưu trữ)"
        return "ebm_cu", "nhóm «EBM · …» cũ/bản tin — không còn khoá chủ đề nào trỏ tới"
    if so_bai is not None and so_bai <= NGUONG_KHUNG:
        return "khung", f"≤ {NGUONG_KHUNG} bài — thư mục khung phân loại"
    return "noi_dung_that", "thư mục bác sĩ có nội dung thật, chưa có dashboard"


def _khoa_ten(ten: str) -> str:
    import unicodedata
    return unicodedata.normalize("NFC", html.unescape(ten or "")).strip().casefold()


def phan_tich(*, nhom: list[dict] | None, ban_ghi: dict[int, dict] | None, bang_nhom: dict[str, str],
              dashboards: dict[str, dict], phan_giai, do_dash, bao_cao: list[dict] | None, toan_van: dict[str, bool] | None,
              so_no: set, word9: dict | None, cau_hoi_cu: dict[str, str], watchlist: list[str] | None,
              hom_nay: dt.date, lan_dau: dict | None = None, bo_qua: set[str] | None = None) -> dict:
    """Phân tích mọi thư mục. THUẦN: mọi nguồn được tiêm vào (test bằng fixture, không đọc tệp thật).

    nhom=None ⇒ thư viện EndNote KHÔNG đọc được: thư mục lấy từ `bang_nhom` (cấu hình), số bài ⚪, nhóm (c) không xét được.
    `phan_giai(lát cắt) -> dict` theo khuôn `chu_de_resolver.resolve`; `do_dash(tệp) -> dict` theo khuôn `DoDashboard.__call__`.
    `bo_qua` = định danh bác sĩ đã loại (khoá `bo_qua` của ~/.ebm-endnote.json) hoặc đang ở thùng rác EndNote — không bao giờ
    thành «chưa có bản ghi» (mời nạp lại bài bác sĩ đã bỏ — sự cố 18/10/2026)."""
    khong_do: list[str] = []
    theo_ten: dict[str, list[str]] = {}
    for k, v in bang_nhom.items():
        theo_ten.setdefault(_khoa_ten(str(v)), []).append(str(k))
    thu_muc: list[dict] = []
    if nhom is None:
        khong_do.append("thư viện EndNote không đọc được — thư mục lấy từ bảng nhom_theo_chu_de; số bài/toàn văn/khối tiếng Việt ⚪; "
                        "nhóm (c) chưa xét được")
        for ten in sorted({str(v) for v in bang_nhom.values()}):
            thu_muc.append({"group_id": None, "ten": html.unescape(ten), "rec": None})
    else:
        for n in nhom:
            ten = str(n.get("ten") or "")
            if n.get("loai") == "online":
                continue  # nhóm tìm kiếm trực tuyến (PubMed, WoS…): không phải thư mục bác sĩ đặt bài vào
            if ten.startswith("_"):
                continue  # nhóm LÀM VIỆC (chờ thùng rác, cần toàn văn…) — không phải chủ đề
            if n.get("rec") is None:
                thu_muc.append({"group_id": n.get("group_id"), "ten": ten, "rec": None, "loi_rec": n.get("loi")})
                continue
            rec = [r for r in n["rec"] if ban_ghi is None or r in ban_ghi]
            if rec:
                thu_muc.append({"group_id": n.get("group_id"), "ten": ten, "rec": rec})
    pm_rec: dict[str, list[int]] = {}
    doi_rec: dict[str, list[int]] = {}
    for r, b in (ban_ghi or {}).items():
        if b.get("pmid"):
            pm_rec.setdefault(b["pmid"], []).append(r)
        if b.get("doi"):
            doi_rec.setdefault(b["doi"], []).append(r)
    wl = set(watchlist) if watchlist is not None else None
    if watchlist is None:
        khong_do.append("watchlist/ánh xạ giám sát không nạp được — trục «trong watchlist» ⚪")
    if bao_cao is None:
        khong_do.append("không đọc được báo cáo quét — trục ứng viên ⚪")
    if toan_van is None:
        khong_do.append("không thấy kho toàn văn EBM-Dashboards/toan_van_oa — toàn văn mục apply ⚪")
    if word9 is not None and "loi" in word9:
        khong_do.append(f"hàng chờ ⑨ không đo được ({word9['loi']})")
    hc9 = (word9 or {}).get("hang_cho") or []
    da_co9 = (word9 or {}).get("da_co") or set()
    do_cache: dict[str, dict] = {}

    for tm in thu_muc:
        khoa = theo_ten.get(_khoa_ten(tm["ten"]), [])
        tm["khoa"] = khoa
        tm["so_bai"] = len(tm["rec"]) if tm.get("rec") is not None else None
        if tm.get("rec") is not None and ban_ghi is not None:
            tm["thieu_pdf"] = sum(1 for r in tm["rec"] if not ban_ghi[r]["pdf"])
            tm["thieu_khoi_vi"] = sum(1 for r in tm["rec"] if not ban_ghi[r]["khoi_vi"])
        else:
            tm["thieu_pdf"] = tm["thieu_khoi_vi"] = None
        tm["khong_do"] = [] if tm["so_bai"] is not None else ["số bài/PDF/khối tiếng Việt của thư mục"]
        tm["lat_cat"] = []
        khoa_dash = [k for k in khoa if not k.startswith(KHOA_NC_TT)]
        if not khoa_dash:
            if nhom is None:
                tm.update(nhom="c", phu_loai="khong_ro", ghi_chu="không đọc được thư viện — chưa phân loại", ly_do=[])
                continue
            pl, gc = phan_loai_c(tm["ten"], tm["so_bai"], khoa, cau_hoi_cu)
            tm.update(nhom="c", phu_loai=pl, ghi_chu=gc, ly_do=[], dashboard_cu=cau_hoi_cu.get(_khoa_ten(tm["ten"])))
            continue
        ly_do_a: list[str] = []
        tag_a: set[str] = set()
        can_wl = False
        for k in khoa_dash:
            dsh = dashboards.get(k)
            lc: dict = {"khoa": k, "tep": None, "ngay": None, "tuoi": None, "watchlist": None, "loai_wl": None}
            tm["lat_cat"].append(lc)
            if not dsh:
                lc["loi"] = "khoá có trong bảng nhóm nhưng KHÔNG thấy tệp dashboard"
                tm["khong_do"].append(f"dashboard của khoá {k} vắng")
                continue
            tep = Path(dsh["tep"])
            ngay = dt.datetime.strptime(dsh["ngay"], "%Y%m%d").date()
            lc.update(tep=tep.name, ngay=ngay.isoformat(), tuoi=(hom_nay - ngay).days,
                      lat=re.sub(r"^EBM_(?:VanDeCuThe|Uptodate|CapNhatTuan|AnToanThuoc|CongCuKeDon)_", "", k))
            pg = phan_giai(lc["lat"]) if watchlist is not None else {"loai": "khong_do"}
            lc["loai_wl"] = pg.get("loai")
            if pg.get("loai") == "watchlist" and pg.get("a2_arg") and (wl is None or pg["a2_arg"] in wl):
                lc["watchlist"] = pg["a2_arg"]
            elif pg.get("loai") == "khong_can":
                lc["ghi_chu"] = f"bản tin gộp — cố ý không giám sát ({pg.get('ly_do', '')})"
            elif pg.get("loai") == "khong_do":
                pass
            else:
                can_wl = True
                lc["goc"] = (pg.get("goc") or [None])[0]
                lc["goi_y_wl"] = goi_y_gan_ten(lc.get("goc") or lc["lat"], watchlist or [])
            if str(tep) not in do_cache:
                do_cache[str(tep)] = do_dash(tep)
            dd = do_cache[str(tep)]
            lc["do"] = {x: dd.get(x) for x in ("doc_duoc", "m1", "m2", "m2_khong_do", "m1_ds")}
            if not dd.get("doc_duoc"):
                tm["khong_do"].append(f"DATA của {tep.name} (M1/M2/mục apply)")
            if lc.get("ghi_chu"):  # bản tin: snapshot, không nối tiếp
                continue
            if lc["tuoi"] > HAN_TUOI_NGAY:
                tag_a.add("tuoi")
                ly_do_a.append(f"{lc['lat']}: {lc['tuoi']} ngày (> {HAN_TUOI_NGAY})")
            if dd.get("doc_duoc") and dd.get("m1"):
                tag_a.add("m1")
                ly_do_a.append(f"{lc['lat']}: M1 {dd['m1']} guideline ≥ 5 năm chưa kiểm phiên bản ({', '.join(dd['m1_ds'][:4])})")
            if lc["watchlist"] and bao_cao is not None:
                uv = ung_vien_manh(bao_cao, lc["watchlist"], ngay, set(dd.get("pmids") or ()), lan_dau)
                lc["ung_vien"] = uv
                if uv["so_bao_cao"] == 0:
                    tm["khong_do"].append(f"ứng viên của «{lc['watchlist']}» (chưa có lượt quét nào từ {ngay:%d/%m} trong "
                                          f"{CUA_SO_UNG_VIEN_NGAY} ngày)")
                else:
                    g, sr = len(uv["guideline"]), len(uv["sr_ma"]) + len(uv["rct"])
                    if g:
                        tag_a.add("guideline")
                        ly_do_a.append(f"{lc['lat']}: {g} guideline/đồng thuận mới")
                    if sr >= NGUONG_SR_RCT:
                        tag_a.add("sr_rct")
                        ly_do_a.append(f"{lc['lat']}: {sr} tổng quan/RCT mới (≥ {NGUONG_SR_RCT})")
            # mục apply/consider — toàn văn · PDF EndNote · khối tiếng Việt · ⑨
            lc["muc"] = _do_muc(dd, tep, toan_van, so_no, ban_ghi, pm_rec, doi_rec, hc9, da_co9, word9, bo_qua or set())
        tm["ly_do"] = ly_do_a
        tm["ly_do_loai"] = sorted(tag_a)
        # ƯU TIÊN = guideline/nguồn mới, M1 hoặc quá hạn tuổi; chỉ có tổng quan/RCT mới ⇒ «theo dõi» (bác sĩ chọn khi có hạn mức)
        tm["uu_tien"] = bool(tag_a - {"sr_rct"})
        tm["can_watchlist"] = can_wl
        tm["tuoi_moi_nhat"] = min((lc["tuoi"] for lc in tm["lat_cat"] if lc.get("tuoi") is not None), default=None)
        if ly_do_a:
            tm["nhom"] = "a"
        elif can_wl:
            tm["nhom"] = "b"
        else:
            tm["nhom"] = "d"
    return {"thu_muc": thu_muc, "khong_do": khong_do, "hom_nay": hom_nay.isoformat()}


def _do_muc(dd: dict, tep: Path, toan_van, so_no, ban_ghi, pm_rec, doi_rec, hc9, da_co9, word9, bo_qua: set) -> list[dict]:
    """Từng mục apply/consider của MỘT dashboard: trạng thái toàn văn kho, PDF EndNote, khối tiếng Việt, ⑨ (★).
    Mục không PMID/DOI ⇒ trạng thái EndNote ⚪ (không khớp được bản ghi — không phải «chưa có»)."""
    ra = []
    hc_rec = {int(x.get("rec")) for x in hc9 if x.get("rec") is not None}
    for m in dd.get("muc") or []:
        rec = (pm_rec.get(m["pmid"]) if m.get("pmid") else None) or (doi_rec.get(m["doi"]) if m.get("doi") else None) or []
        x = dict(m)
        x["toan_van"] = (toan_van.get(m["pmid"]) if (toan_van is not None and m.get("pmid")) else None)
        x["no_trong_so"] = (tep.stem, m["id"], str(m.get("pmid"))) in so_no
        if ban_ghi is None or not (m.get("pmid") or m.get("doi")):
            x["ban_ghi"] = x["pdf_endnote"] = x["khoi_vi"] = None
        elif not rec and ({m.get("pmid"), m.get("doi")} - {None}) & bo_qua:
            x["ban_ghi"] = "bo_qua"
            x["pdf_endnote"] = x["khoi_vi"] = None
        else:
            x["ban_ghi"] = bool(rec)
            x["pdf_endnote"] = any(ban_ghi[r]["pdf"] for r in rec) if rec else False
            x["khoi_vi"] = any(ban_ghi[r]["khoi_vi"] for r in rec) if rec else False
        if not m.get("sao"):
            x["word9"] = "khong_ap_dung"
        elif word9 is None or "loi" in word9 or ban_ghi is None or x["ban_ghi"] in (None, "bo_qua"):
            x["word9"] = None
        else:
            khoa9 = {f"PMID-{m['pmid']}"} if m.get("pmid") else set()
            khoa9 |= {f"REC-{r}" for r in rec}
            if khoa9 & da_co9:
                x["word9"] = "co"
            elif set(rec) & hc_rec:
                x["word9"] = "cho"
            elif not x["pdf_endnote"]:
                x["word9"] = "chua_pdf"
            else:
                x["word9"] = "ngoai_hang_cho"
        ra.append(x)
    return ra


# ───────────────────────── việc + lệnh (từ kết quả phân tích) ─────────────────────────

def _lenh_orchestrator(lat: str) -> str:
    return f'python3 ops/orchestrator.py --topic "{lat}" --online'


def viec_muc(pt: dict) -> dict:
    """Gom thiếu hụt của mục apply/consider: {"apply_thieu_tv", "thieu_pdf", "chua_ban_ghi", "thieu_khoi", "word9_cho",
    "pmid_gom" (chưa có toàn văn trong kho — máy gom OA, phần còn lại qua làn Chrome có bác sĩ)} — mỗi phần tử mang thư mục +
    dashboard + mục; một định danh chỉ đếm MỘT lần dù nhiều dashboard cùng trích."""
    ra: dict = {k: [] for k in ("apply_thieu_tv", "thieu_pdf", "chua_ban_ghi", "thieu_khoi", "word9_cho", "pmid_gom")}
    thay: dict[str, set] = {k: set() for k in ra}
    for tm in pt["thu_muc"]:
        for lc in tm.get("lat_cat") or []:
            for m in lc.get("muc") or []:
                ctx = {"thu_muc": tm["ten"], "tep": lc.get("tep"), "id": m["id"], "pmid": m.get("pmid"), "doi": m.get("doi"),
                       "decision": m["decision"], "sao": m.get("sao"), "no_trong_so": m.get("no_trong_so")}
                k_dd = m.get("pmid") or m.get("doi") or f"{lc.get('tep')}:{m['id']}"

                def them(nhom_viec: str, ctx=ctx, k_dd=k_dd) -> None:
                    if k_dd not in thay[nhom_viec]:
                        thay[nhom_viec].add(k_dd)
                        ra[nhom_viec].append(ctx)
                if m.get("toan_van") is False:
                    if m["decision"] == "apply":
                        them("apply_thieu_tv")
                    them("pmid_gom")
                if m.get("ban_ghi") is False:
                    them("chua_ban_ghi")
                elif m.get("pdf_endnote") is False:
                    them("thieu_pdf")
                if m.get("ban_ghi") and m.get("khoi_vi") is False:
                    them("thieu_khoi")
                if m.get("word9") == "cho":
                    them("word9_cho")
    ra["apply_thieu_tv"].sort(key=lambda x: (not x.get("sao"), x["thu_muc"]))
    ra["pmid_gom"].sort(key=lambda x: (x["decision"] != "apply", not x.get("sao")))
    return ra


def ke_hoach_quet(pt: dict, toi_da: int) -> list[dict]:
    """Chủ đề sẽ quét: lát cắt của thư mục (a) có chủ đề watchlist; mỗi mục watchlist quét tối đa MỘT lần/lượt; ưu tiên M1 →
    guideline mới → tổng quan/RCT mới → tuổi. Trần `toi_da` (≤ TRAN_QUET)."""
    ung: list[tuple[tuple, dict]] = []
    for tm in pt["thu_muc"]:
        if tm.get("nhom") != "a":
            continue
        for lc in tm.get("lat_cat") or []:
            if not lc.get("watchlist"):
                continue
            uv = lc.get("ung_vien") or {}
            diem = (-int(bool((lc.get("do") or {}).get("m1"))), -len(uv.get("guideline") or []),
                    -(len(uv.get("sr_ma") or []) + len(uv.get("rct") or [])), -(lc.get("tuoi") or 0))
            ung.append((diem, {"thu_muc": tm["ten"], "lat": lc["lat"], "watchlist": lc["watchlist"],
                               "lenh": [PY, str(GOC / "ops" / "orchestrator.py"), "--topic", lc["lat"], "--online"]}))
    ra, thay = [], set()
    for _d, x in sorted(ung, key=lambda t: t[0]):
        if x["watchlist"] in thay:
            continue
        thay.add(x["watchlist"])
        ra.append(x)
        if len(ra) >= max(0, min(toi_da, TRAN_QUET)):
            break
    return ra


def chay_quet(ke: list[dict], *, chay=None, ngu=None, nghi: float = NGHI_GIUA_QUET_GIAY) -> list[dict]:
    """Chạy orchestrator TUẦN TỰ. Mã 2 (hạ tầng: mạng/NCBI chặn/khoá bận) ⇒ dừng cả lượt (không dội tiếp vào nguồn đang chặn);
    mã 64 (tên chủ đề) ⇒ ghi và đi tiếp. Trả kết quả từng chủ đề (rc, run_id, giây) — kể cả các chủ đề bị bỏ vì dừng."""
    chay, ngu = chay or subprocess.run, ngu or time.sleep  # tra LÚC GỌI (test vá được subprocess.run của mô-đun)
    ra: list[dict] = []
    dung = None
    for i, x in enumerate(ke):
        if dung:
            ra.append(dict(x, rc=None, bo_qua=dung))
            continue
        if i:
            ngu(nghi)
        t0 = time.monotonic()
        try:
            r = chay(x["lenh"], cwd=str(GOC), capture_output=True, text=True, encoding="utf-8", errors="replace",
                     timeout=TIMEOUT_QUET_GIAY)
            rc, out = r.returncode, (r.stdout or "") + (r.stderr or "")
        except subprocess.TimeoutExpired:
            rc, out = -9, ""
        except OSError as e:
            rc, out = -1, str(e)
        m = re.search(r"KẾ HOẠCH run (\S+)", out)
        ra.append(dict(x, rc=rc, run_id=m.group(1) if m else None, giay=round(time.monotonic() - t0)))
        if rc in (2, -9):
            dung = f"lượt dừng sau «{x['lat']}» (mã {rc}: hạ tầng/quá giờ) — không dội tiếp vào nguồn"
    return ra


# ── ③④ ghi EndNote: rào ──
def kiem_ghi_endnote(*, nen_tang: str | None = None, co_tam_dung: Path | None = None, khoa=None, tinh_trang=None) -> tuple[bool, str]:
    """(được ghi?, lý do). Mỗi điều kiện đọc LÚC GỌI — người gọi kiểm lại TRƯỚC TỪNG bước ghi."""
    if (nen_tang or sys.platform) != "darwin":
        return False, "không phải Mac — EndNote chỉ ghi được bằng AppleScript trên Mac"
    co = Path(os.environ.get("EBM_CO_TAM_DUNG_ENDNOTE") or co_tam_dung or CO_TAM_DUNG_MAC_DINH)
    if co.exists():
        return False, f"cờ tạm dừng EndNote đang bật ({co}) — CHỜ TÍN HIỆU ENDNOTE"
    if khoa is None:
        kg = _cong_cu("khoa_ghi_endnote.py")
        khoa = lambda: kg.doc_khoa() if kg.khoa_con_hieu_luc(kg.doc_khoa()) else None  # noqa: E731
    k = khoa()
    if k:
        return False, f"khoá ghi EndNote đang do tiến trình khác giữ (pid {k.get('pid')}: {str(k.get('ly_do') or '')[:80]})"
    if tinh_trang is None:
        tinh_trang = _cong_cu("endnote_suc_khoe.py").tinh_trang
    tt = tinh_trang()
    if not tt.get("do_duoc"):
        return False, f"sức khoẻ EndNote không đo được ({tt.get('ly_do')})"
    if (tt.get("giao_dich_mo") or {}).get("treo"):
        return False, f"EndNote giữ giao dịch ghi TREO — {tt['giao_dich_mo'].get('mo_ta', '')[:120]}"
    if tt.get("canh_bao"):
        return False, f"sức khoẻ EndNote chưa 🟢 ({tt['canh_bao'][0][:120]})"
    return True, "🟢"


def ke_hoach_hoan_thien(pt: dict, vm: dict, toi_da_pmid: int = TOI_DA_PMID_HOAN_THIEN) -> list[dict]:
    """Chuỗi lệnh MÁY theo đúng thứ tự §6.2: gom → in PDF → gắn kho → tóm tắt tiếng Việt. Bước nào không có việc thì bỏ."""
    tools = GOC / "tools"
    buoc: list[dict] = []
    pm_gom = [x["pmid"] for x in vm["pmid_gom"] if x.get("pmid")][:max(0, toi_da_pmid)]
    pm_pdf = sorted({x["pmid"] for x in vm["thieu_pdf"] if x.get("pmid")}, key=int)
    if pm_gom:
        buoc.append({"buoc": "gom", "ghi_endnote": False,
                     "lenh": [PY, str(tools / "gom_toan_van_dashboard.py"), "--pmid", *pm_gom, "--unpaywall"]})
    pm_in = sorted(set(pm_gom) | set(pm_pdf), key=int)
    if pm_in:
        buoc.append({"buoc": "in_pdf", "ghi_endnote": False,
                     "lenh": [PY, str(tools / "in_pdf_toan_van_kho.py"), "--pmid", *pm_in, "--ap-dung"]})
    pm_gan = sorted(set(pm_pdf) | set(pm_gom), key=int)
    if pm_gan:
        buoc.append({"buoc": "gan_kho", "ghi_endnote": True,
                     "lenh": [PY, str(tools / "nap_endnote_chu_de.py"), "--gan-kho", "--pmid", *pm_gan, "--ap-dung",
                              "--chi-khi-dang-mo"]})
    dash_dir = _goc_du_lieu("EBM-Dashboards")
    tep_khoi = sorted({x["tep"] for x in vm["thieu_khoi"] if x.get("tep")})
    if tep_khoi:
        buoc.append({"buoc": "tom_tat_vi", "ghi_endnote": True,
                     "lenh": [PY, str(tools / "nap_endnote_chu_de.py"), "--tom-tat-vi", "--file",
                              *[str(dash_dir / t) for t in tep_khoi], "--ap-dung", "--chi-khi-dang-mo"]})
    ngoai = sum(tm.get("thieu_khoi_vi") or 0 for tm in pt["thu_muc"]
                if tm.get("nhom") == "c" and tm.get("phu_loai") == "noi_dung_that")
    if ngoai:
        buoc.append({"buoc": "tom_tat_thu_vien", "ghi_endnote": True,
                     "lenh": [PY, str(tools / "nap_endnote_chu_de.py"), "--tom-tat-thu-vien", "--ap-dung", "--chi-khi-dang-mo"]})
    return buoc


LY_DO_CHO_PHIEN = ("chờ phiên Claude: lượt lịch không ghi EndNote (ranh giới sync/quyen-lich-nen.json, BH173) — chạy "
                   "python3 tools/cap_nhat_thang_thu_muc_endnote.py --hoan-thien --ghi-endnote --ghi")


def chay_hoan_thien(buoc: list[dict], *, ghi_endnote: bool = False, chay=None, kiem_ghi=None) -> list[dict]:
    """Chạy tuần tự. Bước ghi EndNote: không có `ghi_endnote` ⇒ KHÔNG chạy (việc 🛎 cho phiên Claude); có ⇒ kiểm rào TRƯỚC TỪNG
    bước, rào hỏng ⇒ dừng mọi bước ghi còn lại (bước không ghi vẫn chạy)."""
    chay, kiem_ghi = chay or subprocess.run, kiem_ghi or kiem_ghi_endnote
    ra: list[dict] = []
    dung_ghi = None if ghi_endnote else LY_DO_CHO_PHIEN
    for b in buoc:
        if b["ghi_endnote"]:
            if dung_ghi is None:
                ok, ly_do = kiem_ghi()  # MỖI bước ghi — phiên khác có thể vừa lấy khoá/bật cờ giữa hai bước
                if not ok:
                    dung_ghi = ly_do
            if dung_ghi:
                ra.append(dict(b, rc=None, bo_qua=dung_ghi))
                continue
        t0 = time.monotonic()
        try:
            r = chay(b["lenh"], cwd=str(GOC), capture_output=True, text=True, encoding="utf-8", errors="replace",
                     timeout=TIMEOUT_HOAN_THIEN.get(b["buoc"], 1800))
            rc, duoi = r.returncode, ((r.stdout or "") + (r.stderr or "")).strip().splitlines()[-3:]
        except subprocess.TimeoutExpired:
            rc, duoi = -9, ["quá giờ"]
        except OSError as e:
            rc, duoi = -1, [str(e)]
        ra.append(dict(b, rc=rc, giay=round(time.monotonic() - t0), duoi=duoi))
    return ra


# ───────────────────────── đề xuất watchlist (b) ─────────────────────────

def _hat_giong_tieng_anh(ten: str) -> str | None:
    """Từ khoá hạt giống CHỈ lấy từ tên thư mục bác sĩ đặt bằng tiếng Anh (phần ASCII) — máy KHÔNG dịch, KHÔNG soạn truy vấn
    lâm sàng (BH10); tên thuần tiếng Việt ⇒ None (phiên người soạn)."""
    t = re.sub(r"\([^)]*\)", " ", html.unescape(ten or ""))
    if not t.isascii():
        return None
    t = re.sub(r"[^A-Za-z0-9\- ]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t or None


def de_xuat_watchlist(pt: dict, thang: str, sinh_luc: str) -> dict:
    muc = []
    for tm in pt["thu_muc"]:
        if not tm.get("can_watchlist"):
            continue
        for lc in tm.get("lat_cat") or []:
            if lc.get("watchlist") or lc.get("ghi_chu") or lc.get("loai_wl") in (None, "khong_do"):
                continue
            hg = _hat_giong_tieng_anh(tm["ten"])
            muc.append({"thu_muc": tm["ten"], "group_id": tm.get("group_id"), "dashboard": lc.get("tep"),
                        "chu_de_goc": lc.get("goc") or lc.get("lat"),
                        "topic_de_xuat": tm["ten"][:120], "query": hg, "queries": None,
                        "goi_y_watchlist_gan_ten": lc.get("goi_y_wl") or [],
                        "can_bac_si": ("gợi ý gần tên chỉ để bác sĩ xem — máy KHÔNG ghép (BH28); nếu một mục watchlist đã phủ chủ đề "
                                       "thì chỉ khai ánh xạ ở giam-sat-chu-de.json → muc") if lc.get("goi_y_wl") else
                                      "soạn truy vấn theo tầng (guideline · sr_ma · rct · moi_vao_pubmed edat loc_thiet_ke:false)",
                        "trang_thai": "CHUA_SOAN_TRUY_VAN"})
    return {"_about": (f"ĐỀ XUẤT của phiếu cập nhật tháng thư mục EndNote {thang} (máy soạn {sinh_luc}, CHƯA ÁP DỤNG): chủ đề gốc có "
                       "dashboard mà không mục watchlist nào canh. `query` chỉ là từ khoá hạt giống lấy từ TÊN thư mục tiếng Anh của "
                       "bác sĩ (máy không dịch, không soạn truy vấn lâm sàng — BH10); `queries` để phiên người soạn theo tầng và đo "
                       "sản lượng. Bác sĩ duyệt ⇒ thêm vào watchlist.json (sao lưu trước) + khai ánh xạ giam-sat-chu-de.json; "
                       "đo lại: python3 tools/kiem_phu_giam_sat.py · python3 tools/kiem_san_luong_giam_sat.py. Cần bác sĩ kiểm chứng."),
            "thang": thang, "sinh_luc": sinh_luc, "chu_de": muc}


def ghi_de_xuat(tep: Path, khoi: dict) -> str:
    """Ghi khối đề xuất vào `watchlist.de-xuat.json` dưới KHOA_DE_XUAT — GIỮ NGUYÊN mọi khoá khác (đề xuất của đợt khác),
    sao lưu trước, ghi nguyên tử. Tệp vắng ⇒ tạo mới. Tệp hỏng ⇒ KHÔNG ghi (không đè thứ chưa đọc được)."""
    cu: dict = {}
    if tep.exists():
        try:
            cu = json.loads(tep.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            return f"⚪ không ghi đề xuất: {tep.name} hỏng ({type(e).__name__}) — sửa tay trước"
        if not isinstance(cu, dict):
            return f"⚪ không ghi đề xuất: {tep.name} không phải đối tượng JSON"
        if cu.get(KHOA_DE_XUAT, {}).get("chu_de") == khoi["chu_de"]:
            return f"= {tep.name}: đề xuất không đổi"
        shutil.copyfile(tep, tep.with_name(f"{tep.name}.bak-{dt.datetime.now():%Y%m%d-%H%M%S}-truoc-thu-muc-endnote"))
    cu[KHOA_DE_XUAT] = khoi
    tam = tep.with_name(tep.name + f".tmp{os.getpid()}")
    tam.write_text(json.dumps(cu, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    json.loads(tam.read_text(encoding="utf-8"))
    os.replace(tam, tep)
    return f"✓ {tep.name}: {len(khoi['chu_de'])} chủ đề đề xuất (khoá {KHOA_DE_XUAT})"


# ───────────────────────── phiếu ─────────────────────────

def dem_nhom(pt: dict) -> dict:
    d = {k: [] for k in "abcd"}
    for tm in pt["thu_muc"]:
        d[tm["nhom"]].append(tm)
    return d


def _tv(x) -> str:
    return "⚪" if x is None else ("✓" if x else "✗")


def _uoc(n: int, cap: tuple[float, float]) -> str:
    return f"≈ {n * cap[0]:.1f}–{n * cap[1]:.1f} triệu token".replace(".", ",")


def dung_phieu(pt: dict, vm: dict, *, thang: str, sinh_luc: str, che_do: str, quet: list[dict] | None,
               hoan_thien: list[dict] | None, de_xuat_kq: str | None) -> str:
    g = dem_nhom(pt)
    c_pl: dict[str, list] = {}
    for tm in g["c"]:
        c_pl.setdefault(tm.get("phu_loai", "khong_ro"), []).append(tm)
    d_xanh = [tm for tm in g["d"] if not tm["khong_do"]]
    b_cung = [tm for tm in g["a"] if tm.get("can_watchlist")]
    L: list[str] = [f"# Cập nhật chứng cứ tháng theo thư mục EndNote — {thang[5:]}/{thang[:4]}", "",
                    f"Sinh {sinh_luc} · chế độ: {che_do} · candidate-only, không đổi decision/gradeLevel, không ghi EndNote ngoài "
                    "bước máy có rào. Cần bác sĩ kiểm chứng.", "",
                    "| Nhóm | Số thư mục | Ghi chú |", "|---|---:|---|",
                    f"| {NHAN_NHOM['a']} | {len(g['a'])} | {len(b_cung)} trong số này cũng chưa có watchlist |",
                    f"| {NHAN_NHOM['b']} | {len(g['b'])} | đề xuất ở watchlist.de-xuat.json khoá `{KHOA_DE_XUAT}` |",
                    f"| {NHAN_NHOM['c']} | {len(g['c'])} | "
                    + " · ".join(f"{NHAN_C.get(k, k)} {len(v)}" for k, v in sorted(c_pl.items())) + " |",
                    f"| {NHAN_NHOM['d']} | {len(g['d'])} | 🟢 {len(d_xanh)} · ⚪ {len(g['d']) - len(d_xanh)} còn trục không đo được |",
                    ""]
    for x in pt["khong_do"]:
        L.append(f"- ⚪ {x}")
    if pt["khong_do"]:
        L.append("")
    L += ["## 1. Việc bác sĩ cần quyết", ""]
    # 1.1 apply thiếu toàn văn
    at = vm["apply_thieu_tv"]
    L.append(f"### 1.1 🔴 Mục «Áp dụng» chưa đọc toàn văn — {len(at)} mục (cổng BH161 đáng lẽ đã chặn)")
    if at:
        L.append("Lệnh: gom OA `python3 tools/gom_toan_van_dashboard.py --pmid <PMID> --unpaywall` → làn trình duyệt có bác sĩ "
                 "`python3 tools/doc_toan_van_co_nguoi.py --pmid <PMID>` → hoặc bác sĩ đã đọc `--bac-si-da-doc <PMID> --ghi-chu "
                 "\"…\" --ghi` → hoặc bác sĩ hạ «Cân nhắc».")
        for x in at[:40]:
            L.append(f"- 🔴 {'★ ' if x.get('sao') else ''}[{x['thu_muc'][:60]}] {x['tep']} · {x['id']} · PMID {x['pmid']}"
                     + (" · nợ trong sổ" if x.get("no_trong_so") else " · NGOÀI sổ nợ"))
        if len(at) > 40:
            L.append(f"- … +{len(at) - 40} mục (xem tệp .json)")
    else:
        L.append("- 🟢 không có (trong phạm vi đo được)")
    L.append("")
    # 1.2 bản nối tiếp
    ut = [tm for tm in g["a"] if tm.get("uu_tien")]
    td = [tm for tm in g["a"] if not tm.get("uu_tien")]
    L.append(f"### 1.2 Duyệt danh sách bản nối tiếp — {len(g['a'])} thư mục: ưu tiên {len(ut)} ({_uoc(len(ut), UOC_TINH_NOI_TIEP)}) "
             f"· theo dõi {len(td)} ({_uoc(len(td), UOC_TINH_NOI_TIEP)})")
    L.append("Máy chạy được ngay (candidate): lệnh orchestrator ở từng dòng. Bản nối tiếp = phiên skill `cap-nhat-chung-cu-y-khoa` "
             "(agent ≈ 0,5–0,8 triệu token/chủ đề) CHỈ khi bác sĩ duyệt dòng đó; bộ năm của bản nối tiếp lo toàn văn/EndNote/⑨ "
             "như thường. Ưu tiên = guideline/đồng thuận mới · M1 · quá hạn tuổi; theo dõi = chỉ có ≥ "
             f"{NGUONG_SR_RCT} tổng quan/RCT mới.")

    def _khoa_xep(t: dict) -> tuple:
        return (-len(t.get("ly_do_loai") or []), -max([lc.get("tuoi") or 0 for lc in t["lat_cat"]] or [0]), t["ten"])
    so = 0
    for nhan, ds in (("Ưu tiên", ut), ("Theo dõi — chỉ có tổng quan/RCT mới", td)):
        if not ds:
            continue
        L.append(f"**{nhan}** ({len(ds)})")
        for tm in sorted(ds, key=_khoa_xep):
            so += 1
            lat = [lc for lc in tm["lat_cat"] if lc.get("lat")]
            L.append(f"{so}. **{tm['ten'][:90]}** — " + "; ".join(tm["ly_do"][:3])
                     + ("" if len(tm["ly_do"]) <= 3 else f" (+{len(tm['ly_do']) - 3})")
                     + (" · ⚠ chưa có watchlist" if tm.get("can_watchlist") else ""))
            for lc in lat[:3]:
                L.append(f"   - `{_lenh_orchestrator(lc['lat'])}` ({lc['tep']}, {lc['tuoi']} ngày)")
    L.append("")
    # 1.3 ⑨
    w9 = vm["word9_cho"]
    L.append(f"### 1.3 Tóm tắt Word ⑨ (★) chờ duyệt — {len(w9)} bài" + (f" ({_uoc(len(w9), UOC_TINH_WORD9)})" if w9 else "")
             + " — KHÔNG tự chạy (agent đọc toàn văn + agent kiểm chéo)")
    if w9:
        L.append("Lệnh (phiên Claude, tuần tự): `python3 tools/tom_tat_chung_cu_word.py hang-cho --dashboard <tệp>`")
        for x in w9[:25]:
            L.append(f"- ★ [{x['thu_muc'][:60]}] {x['tep']} · {x['id']} · PMID {x['pmid']}")
    L.append("")
    # 1.4 làn Chrome
    con_thieu = [x for x in vm["pmid_gom"]]
    L.append(f"### 1.4 Toàn văn còn thiếu — {len(con_thieu)} PMID apply/consider chưa có trong kho: máy gom OA trước (`--hoan-thien`), "
             "phần còn lại qua làn Chrome có bác sĩ (KHÔNG tự mở)")
    if con_thieu:
        L.append("Lệnh: `python3 tools/doc_toan_van_co_nguoi.py --pmid <PMID>` (phiếu theo miền → `--huong-dan`); phiên uỷ quyền "
                 "`python3 tools/phien_uy_quyen_chrome.py --mo \"<nguyên văn>\"`.")
        L.append("- " + ", ".join(f"{x['pmid']}{'★' if x.get('sao') else ''}" for x in con_thieu[:60])
                 + (f" … +{len(con_thieu) - 60}" if len(con_thieu) > 60 else ""))
    L.append("")
    # 1.5 watchlist
    L.append(f"### 1.5 Thêm vào watchlist — {len(g['b'])} thư mục nhóm (b) + {len(b_cung)} thư mục nhóm (a)")
    if de_xuat_kq:
        L.append(f"- {de_xuat_kq}")
    for tm in g["b"] + b_cung:
        lc0 = next((lc for lc in tm["lat_cat"] if lc.get("loai_wl") not in ("watchlist",) and not lc.get("ghi_chu")), {})
        gy = lc0.get("goi_y_wl") or []
        L.append(f"- [{tm['ten'][:70]}] gốc `{lc0.get('goc') or lc0.get('lat')}`"
                 + (f" · watchlist gần tên (máy không ghép): {' | '.join(gy)}" if gy else " · chưa có mục gần tên"))
    if g["b"] or b_cung:
        L.append("- Lệnh sau khi bác sĩ duyệt: khai `EBM-Dashboards/giam-sat-chu-de.json` (+ thêm chủ đề vào watchlist.json, sao lưu "
                 "trước) → `python3 tools/kiem_phu_giam_sat.py` → `python3 tools/kiem_san_luong_giam_sat.py`")
    L.append("")
    # 1.6 c nội dung thật
    nd = c_pl.get("noi_dung_that", [])
    L.append(f"### 1.6 Thư mục có nội dung thật nhưng chưa có dashboard — {len(nd)}")
    for tm in sorted(nd, key=lambda t: -(t.get("so_bai") or 0)):
        L.append(f"- [{tm['ten'][:80]}] {tm.get('so_bai')} bài (thiếu PDF {tm.get('thieu_pdf')}) — dựng dashboard? phiên skill "
                 f"`cap-nhat-chung-cu-y-khoa` (bác sĩ chốt phạm vi)")
    L.append("")
    # 2. việc máy
    L += ["## 2. Việc máy (`--hoan-thien` làm được, không phán đoán y khoa)", "",
          f"- Mục apply/consider có toàn văn cần gom OA: {len(vm['pmid_gom'])} PMID",
          f"- Mục chưa có PDF trong EndNote: {len(vm['thieu_pdf'])} → `python3 tools/in_pdf_toan_van_kho.py --pmid … --ap-dung` rồi "
          "`python3 tools/nap_endnote_chu_de.py --gan-kho --pmid … --ap-dung`",
          f"- Mục chưa có bản ghi EndNote: {len(vm['chua_ban_ghi'])} → `python3 tools/nap_endnote_chu_de.py --file <dashboard> --ap-dung`",
          f"- Mục thiếu khối «EBM · ĐỌC NHANH»: {len(vm['thieu_khoi'])} → `python3 tools/nap_endnote_chu_de.py --tom-tat-vi --file "
          "<dashboard> --ap-dung`",
          "- 🛎 Bước GHI EndNote (gắn kho · tóm tắt tiếng Việt) lượt lịch KHÔNG làm (ranh giới quyền lượt lịch, BH173) — phiên Claude "
          "có người: `python3 tools/cap_nhat_thang_thu_muc_endnote.py --hoan-thien --ghi-endnote --ghi` (rào: sức khoẻ EndNote 🟢 · "
          "không giao dịch treo · không khoá ghi của phiên khác · không cờ TAM-DUNG-ENDNOTE).", ""]
    if quet is not None:
        L.append(f"### Lượt quét máy (`--quet`) — {len(quet)} chủ đề")
        for x in quet:
            L.append(f"- {x['watchlist'][:60]} ← `{x['lat']}`: " + (f"bỏ — {x['bo_qua']}" if x.get("bo_qua") else
                     f"mã {x.get('rc')} · run `{x.get('run_id')}` · {x.get('giay')} giây · phiếu logs/{x.get('run_id')}.phieu.md"))
        L.append("")
    if hoan_thien is not None:
        L.append(f"### Lượt hoàn thiện máy (`--hoan-thien`) — {len(hoan_thien)} bước")
        for b in hoan_thien:
            L.append(f"- {b['buoc']}: " + (f"bỏ — {b['bo_qua']}" if b.get("bo_qua") else f"mã {b.get('rc')} · {b.get('giay')} giây"))
        L.append("")
    # 3. bảng thư mục có dashboard
    L += ["## 3. Thư mục có dashboard (a · b · d)", "",
          "| Nhóm | Thư mục | Bài | Thiếu PDF | Thiếu khối VN | Bản mới nhất (tuổi) | Watchlist | Ứng viên G/SR/RCT | M1/M2 | ⚪ |",
          "|---|---|---:|---:|---:|---|---|---|---|---|"]
    for k in "abd":
        for tm in sorted(g[k], key=lambda t: t["ten"]):
            for j, lc in enumerate(tm["lat_cat"] or [{}]):
                uv = lc.get("ung_vien")
                uvs = ("⚪" if lc.get("watchlist") and (uv is None or uv["so_bao_cao"] == 0) else
                       f"{len(uv['guideline'])}/{len(uv['sr_ma'])}/{len(uv['rct'])}" if uv else "—")
                do = lc.get("do") or {}
                m12 = f"{do.get('m1')}/{do.get('m2')}" if do.get("doc_duoc") else "⚪"
                wl = ("✓" if lc.get("watchlist") else "bản tin" if lc.get("ghi_chu") else
                      "⚪" if lc.get("loai_wl") in (None, "khong_do") else "✗")
                L.append(f"| {k if j == 0 else ''} | {tm['ten'][:55] if j == 0 else '↳'} | {tm.get('so_bai') if j == 0 else ''} | "
                         f"{tm.get('thieu_pdf') if j == 0 else ''} | {tm.get('thieu_khoi_vi') if j == 0 else ''} | "
                         f"{(lc.get('lat') or lc.get('khoa') or '')[:40]} {lc.get('ngay') or '⚪'} ({lc.get('tuoi')}) | {wl} | {uvs} | "
                         f"{m12} | {len(tm['khong_do']) if j == 0 else ''} |")
    L.append("")
    # 4. c còn lại
    L += ["## 4. Thư mục chưa gắn dashboard (c)", ""]
    for k in ("ebm_cu", "khung", "nc_tt", "khong_ro"):
        ds = c_pl.get(k, [])
        if not ds:
            continue
        L.append(f"**{NHAN_C.get(k, 'chưa phân loại')}** ({len(ds)}): "
                 + " · ".join(f"{tm['ten'][:50]} ({tm.get('so_bai')}"
                              + (f"; bản cũ của {re.sub(r'^EBM_(?:VanDeCuThe_)?', '', tm['dashboard_cu'])}" if tm.get("dashboard_cu")
                                 else "") + ")"
                              for tm in sorted(ds, key=lambda t: -(t.get('so_bai') or 0))))
        if k == "ebm_cu":
            L.append("Bác sĩ quyết: gộp vào nhóm hiện hành của chủ đề, giữ làm lưu trữ, hay bỏ — máy không gộp/xoá nhóm.")
        L.append("")
    L.append("Cần bác sĩ kiểm chứng.")
    return "\n".join(L) + "\n"


def _json_an_toan(o):
    if isinstance(o, (set, frozenset)):
        return sorted(o)
    if isinstance(o, (Path, dt.date, dt.datetime)):
        return str(o)
    return str(o)


def tep_phieu(dash_dir: Path, thang: str) -> tuple[Path, Path]:
    goc = Path(dash_dir) / "derivatives" / f"{TIEN_TO_TEP}{thang}"
    return goc.with_suffix(".md"), goc.with_suffix(".json")


# ───────────────────────── giác quan hòm việc (tu_de_xuat_viec.py gọi) ─────────────────────────

def giac_quan(dash_dir: Path, hom_nay: dt.date | None = None) -> tuple[list[tuple[int, str, str, str]], str | None]:
    """([(ưu tiên, 👤|🛎, việc, lệnh)], lý do ⚪ | None). Chưa có phiếu THÁNG NÀY ⇒ ⚪ (không phải «không có việc»). Có phiếu ⇒
    đếm thư mục (a) mà CHƯA có bản dashboard mới hơn bản phiếu ghi (bản nối tiếp đã làm thì tự rơi khỏi dòng nhắc) — 👤; mục
    thiếu PDF/khối tiếng Việt trong EndNote — 🛎 (máy làm được nhưng lượt lịch không được ghi EndNote, cần phiên Claude)."""
    hom_nay = hom_nay or dt.date.today()
    thang = f"{hom_nay:%Y-%m}"
    _md, js = tep_phieu(dash_dir, thang)
    if not Path(dash_dir).is_dir():
        return [], "không có EBM-Dashboards/ ở cây này"
    try:
        d = json.loads(js.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [], f"chưa có phiếu tháng {thang} (tác vụ lịch cap-nhat-thang-thu-muc-endnote, ngày 5)"
    except (OSError, ValueError) as e:
        return [], f"phiếu {js.name} không đọc được ({type(e).__name__})"
    moi = dashboards_moi_nhat(dash_dir)
    a = [tm for tm in d.get("thu_muc") or [] if tm.get("nhom") == "a"]
    con = 0
    for tm in a:
        da_lam = any(lc.get("ngay") and moi.get(lc.get("khoa"), {}).get("ngay", "") > lc["ngay"].replace("-", "")
                     for lc in tm.get("lat_cat") or [])
        con += not da_lam
    viec = []
    if con:
        viec.append((2, "👤", f"Phiếu cập nhật tháng thư mục EndNote {thang}: {len(a)} thư mục cần bản nối tiếp (còn {con} chưa làm) — "
                        f"bác sĩ duyệt danh sách (agent ≈ {UOC_TINH_NOI_TIEP[0]:g}–{UOC_TINH_NOI_TIEP[1]:g} triệu token/chủ đề)"
                     .replace(".", ","), f"mở EBM-Dashboards/derivatives/{TIEN_TO_TEP}{thang}.md"))
    nb = sum(1 for tm in d.get("thu_muc") or [] if tm.get("nhom") == "b")
    if nb:
        viec.append((3, "👤", f"Phiếu tháng {thang}: {nb} thư mục có dashboard mà chủ đề chưa có watchlist — bác sĩ duyệt đề xuất",
                     f"EBM-Dashboards/watchlist.de-xuat.json khoá {KHOA_DE_XUAT}"))
    vm = d.get("viec_muc") or {}
    n_pdf, n_khoi = len(vm.get("thieu_pdf") or []), len(vm.get("thieu_khoi") or [])
    if n_pdf or n_khoi:
        viec.append((3, "🛎", f"Phiếu tháng {thang}: {n_pdf} mục apply/consider chưa có PDF trong EndNote · {n_khoi} thiếu khối "
                              "tiếng Việt — máy gắn kho/tóm tắt được, lượt lịch không ghi EndNote ⇒ cần phiên Claude",
                     "python3 tools/cap_nhat_thang_thu_muc_endnote.py --hoan-thien --ghi-endnote --ghi"))
    return viec, None


# ───────────────────────── điều phối ─────────────────────────

def thu_thap_va_phan_tich(hom_nay: dt.date, bay_gio: dt.datetime) -> tuple[dict | None, str | None, dict]:
    """Đọc mọi nguồn THẬT rồi `phan_tich`. Trả (kết quả, lý do không đo được toàn cục, bối cảnh)."""
    dash_dir = _goc_du_lieu("EBM-Dashboards")
    if not dash_dir.is_dir():
        return None, f"không thấy {dash_dir} (bản sao trần) — không đo được", {}
    ch, loi_ch = doc_cau_hinh_endnote()
    bang = (ch or {}).get("nhom_theo_chu_de") or {}
    nhom = ban_ghi = None
    rac: set[str] = set()
    loi_tv = None
    thu_vien = Path(ch["thu_vien"]) if ch and isinstance(ch.get("thu_vien"), str) else None
    if thu_vien is None:
        loi_tv = loi_ch or "chưa khai thư viện EndNote"
    else:
        try:
            tv = doc_thu_vien(thu_vien)
            nhom, ban_ghi, rac = tv["nhom"], tv["ban_ghi"], tv["thung_rac"]
        except Exception as e:  # noqa: BLE001 — thư viện không đọc được ⇒ ⚪, vẫn lập phiếu theo bảng nhóm
            loi_tv = f"{type(e).__name__}: {str(e)[:160]}"
    if nhom is None and not bang:
        return None, f"không đọc được thư viện EndNote ({loi_tv}) và bảng nhom_theo_chu_de trống — không đo được", {}
    dashboards = dashboards_moi_nhat(dash_dir)
    try:
        cdr = _cong_cu("chu_de_resolver.py")
        du_lieu = cdr.nap_du_lieu(dash_dir)
        watchlist = None if du_lieu.get("loi") else list(du_lieu["watchlist"])
        phan_giai = (lambda q: cdr.resolve(q, du_lieu))  # noqa: E731
    except Exception:  # noqa: BLE001
        watchlist, phan_giai = None, (lambda q: {"loai": "khong_do"})  # noqa: E731
    try:
        bc = doc_bao_cao_quet(dash_dir, _goc_du_lieu("logs"), bay_gio)
        bao_cao, lan_dau = bc["bao_cao"], bc["lan_dau"]
    except Exception:  # noqa: BLE001
        bao_cao, lan_dau = None, None
    do = DoDashboard()
    # câu hỏi của MỌI phiên bản ⇒ nhận ra nhóm «EBM · …» của bản dashboard cũ
    cau_hoi_cu: dict[str, str] = {}
    for k, v in dashboards.items():
        for _n, p in v["cac_ban"]:
            q = do.cau_hoi(p)
            if q:
                cau_hoi_cu.setdefault(_khoa_ten("EBM · " + q), k)
    # PMID mục apply/consider của bản mới nhất ⇒ toàn văn kho một lần
    do_cache: dict[str, dict] = {}

    def do_dash(tep: Path) -> dict:
        if str(tep) not in do_cache:
            do_cache[str(tep)] = do(tep)
        return do_cache[str(tep)]
    pm = []
    for k in bang:
        if k in dashboards:
            pm += [m["pmid"] for m in do_dash(dashboards[k]["tep"]).get("muc") or [] if m.get("pmid")]
    tv = toan_van_kho(pm, dash_dir / "toan_van_oa")
    word9 = doc_word9(thu_vien) if thu_vien and nhom is not None else None
    pt = phan_tich(nhom=nhom, ban_ghi=ban_ghi, bang_nhom=bang, dashboards=dashboards, phan_giai=phan_giai, do_dash=do_dash,
                   bao_cao=bao_cao, toan_van=tv, so_no=doc_so_no(dash_dir), word9=word9, cau_hoi_cu=cau_hoi_cu,
                   watchlist=watchlist, hom_nay=hom_nay, lan_dau=lan_dau, bo_qua=rac | bo_qua_cau_hinh(ch))
    if loi_tv:
        pt["khong_do"].insert(0, f"thư viện EndNote: {loi_tv}")
    return pt, None, {"dash_dir": dash_dir}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Phiếu cập nhật chứng cứ tháng theo thư mục EndNote (chạy khô mặc định)")
    ap.add_argument("--ghi", action="store_true", help="ghi phiếu + đề xuất watchlist; chạy thật --quet/--hoan-thien")
    ap.add_argument("--ghi-endnote", action="store_true",
                    help="cùng --hoan-thien --ghi: cho chạy bước GHI EndNote ③④ (phiên Claude có người; KHÔNG dùng cho lượt lịch)")
    ap.add_argument("--quet", action="store_true", help="gọi ops/orchestrator.py --topic … --online cho thư mục nhóm (a)")
    ap.add_argument("--toi-da", type=int, default=TOI_DA_QUET_MAC_DINH, help=f"số chủ đề quét tối đa (≤ {TRAN_QUET})")
    ap.add_argument("--hoan-thien", action="store_true", help="phần MÁY của dây chuyền toàn văn/EndNote/tóm tắt tiếng Việt")
    ap.add_argument("--toi-da-pmid", type=int, default=TOI_DA_PMID_HOAN_THIEN, help="trần PMID gom toàn văn mỗi lượt")
    ap.add_argument("--hom-nay", help="YYYY-MM-DD (kiểm thử/đo lại)")
    ap.add_argument("--json", action="store_true", help="in JSON phân tích")
    a = ap.parse_args(argv)
    if a.toi_da < 0 or a.toi_da > TRAN_QUET or a.toi_da_pmid < 0:
        print(f"✗ tham số sai: 0 ≤ --toi-da ≤ {TRAN_QUET}, --toi-da-pmid ≥ 0")
        return 3
    if a.ghi_endnote and not a.hoan_thien:
        print("✗ tham số sai: --ghi-endnote chỉ đi cùng --hoan-thien")
        return 3
    try:
        hom_nay = dt.date.fromisoformat(a.hom_nay) if a.hom_nay else dt.date.today()
    except ValueError:
        print("✗ tham số sai: --hom-nay phải là YYYY-MM-DD")
        return 3
    bay_gio = dt.datetime.combine(hom_nay, dt.datetime.now().time())
    pt, loi, bc = thu_thap_va_phan_tich(hom_nay, bay_gio)
    if pt is None:
        print(f"⚪ KHÔNG ĐO ĐƯỢC — {loi}")
        return 2
    vm = viec_muc(pt)
    thang = f"{hom_nay:%Y-%m}"
    ke_q = ke_hoach_quet(pt, a.toi_da) if a.quet else None
    ke_h = ke_hoach_hoan_thien(pt, vm, a.toi_da_pmid) if a.hoan_thien else None
    kq_q = kq_h = None
    if a.ghi and ke_q:
        kq_q = chay_quet(ke_q)
    if a.ghi and ke_h:
        kq_h = chay_hoan_thien(ke_h, ghi_endnote=a.ghi_endnote)
    if (kq_q and any(x.get("rc") is not None for x in kq_q)) or (kq_h and any(x.get("rc") is not None for x in kq_h)):
        pt2, loi2, _ = thu_thap_va_phan_tich(hom_nay, dt.datetime.now())  # đo LẠI sau bước máy ⇒ phiếu nói đúng phần còn thiếu
        if pt2 is not None:
            pt, vm = pt2, viec_muc(pt2)
    g = dem_nhom(pt)
    sinh_luc = dt.datetime.now().isoformat(timespec="minutes")
    che_do = ("báo cáo" + (" + quét" if a.quet else "") + (" + hoàn thiện" if a.hoan_thien else "")
              + (" + ghi EndNote" if a.ghi_endnote else "")
              + ("" if a.ghi else " (CHẠY KHÔ — chưa ghi, chưa chạy lệnh nào)"))
    print(f"Cập nhật tháng theo thư mục EndNote {thang} — {len(pt['thu_muc'])} thư mục · "
          + " · ".join(f"{NHAN_NHOM[k]} {len(g[k])}" for k in "abcd"))
    print(f"  🔴 mục apply chưa đọc toàn văn: {len(vm['apply_thieu_tv'])} · thiếu PDF EndNote: {len(vm['thieu_pdf'])} · "
          f"chưa có bản ghi: {len(vm['chua_ban_ghi'])} · thiếu khối tiếng Việt: {len(vm['thieu_khoi'])} · ⑨ chờ: {len(vm['word9_cho'])}")
    for x in pt["khong_do"]:
        print(f"  ⚪ {x}")
    if ke_q is not None and not a.ghi:
        print(f"  (khô) --quet sẽ chạy {len(ke_q)} chủ đề:")
        for x in ke_q:
            print("     " + " ".join(x["lenh"][1:]))
    if ke_h is not None and not a.ghi:
        print(f"  (khô) --hoan-thien sẽ chạy {len(ke_h)} bước:")
        for b in ke_h:
            nhan = ((" [ghi EndNote — có rào]" if a.ghi_endnote else " [ghi EndNote — BỎ, thiếu --ghi-endnote]")
                    if b["ghi_endnote"] else "")
            print(f"     {b['buoc']}{nhan}: "
                  + " ".join(b["lenh"][1:])[:200])
    if a.json:
        print(json.dumps({"thang": thang, **pt, "viec_muc": vm}, ensure_ascii=False, indent=1, default=_json_an_toan))
    if a.ghi:
        dash_dir = bc.get("dash_dir") or _goc_du_lieu("EBM-Dashboards")
        md, js = tep_phieu(dash_dir, thang)
        md.parent.mkdir(parents=True, exist_ok=True)
        kq_dx = ghi_de_xuat(dash_dir / "watchlist.de-xuat.json", de_xuat_watchlist(pt, thang, sinh_luc))
        md.write_text(dung_phieu(pt, vm, thang=thang, sinh_luc=sinh_luc, che_do=che_do, quet=kq_q, hoan_thien=kq_h,
                                 de_xuat_kq=kq_dx), encoding="utf-8", newline="\n")
        js.write_text(json.dumps({"thang": thang, "sinh_luc": sinh_luc, "che_do": che_do, **pt, "viec_muc": vm,
                                  "quet": kq_q, "hoan_thien": kq_h}, ensure_ascii=False, indent=1, default=_json_an_toan) + "\n",
                      encoding="utf-8", newline="\n")
        print(f"  ✓ phiếu: {md}")
        print(f"  {kq_dx}")
    else:
        print("  (chạy khô — thêm --ghi để ghi phiếu tháng)")
    nd = sum(1 for tm in g["c"] if tm.get("phu_loai") == "noi_dung_that")
    return 1 if (g["a"] or g["b"] or nd or vm["apply_thieu_tv"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
