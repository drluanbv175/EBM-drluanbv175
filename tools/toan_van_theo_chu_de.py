#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TOÀN VĂN THEO CHỦ ĐỀ — bước «TV» của `ops/orchestrator.py` (04/10/2026).

VÌ SAO CÓ. Đo 04/10/2026 khi bác sĩ hỏi «hệ thống đã bảo đảm phủ chứng cứ và đọc toàn văn chưa»:
  • chuỗi máy theo chủ đề (A2 quét → A4 sổ xác minh → B2 cổng → B5 hàng chờ) KHÔNG có bước toàn văn nào — ứng viên mới
    được trình bác sĩ khi máy mới đọc tóm tắt;
  • 27 mục `apply` (20 PMID) không có toàn văn trong kho vẫn qua cổng, vì cổng chỉ chặn khi mục TỰ KHAI 'partial'.
Bước này NỐI BA CÔNG CỤ ĐÃ CÓ, không thêm một dòng logic y khoa:
  1. `gom_toan_van_dashboard.py --pmid … --unpaywall` — PMC Open Access + bản mang GIẤY PHÉP MỞ (cổng điều khoản BH160);
  2. `doc_sau_toan_van.py --pmid …`                    — hồ sơ đọc sâu cho bài vừa có toàn văn;
  3. `doc_toan_van_co_nguoi.py --pmid …`               — phiếu LÀN TRÌNH DUYỆT CÓ BÁC SĨ cho bài còn thiếu (theo miền + điều
     khoản NXB: phiên uỷ quyền / bác sĩ đọc trực tiếp / đọc điều khoản trước).
PMID lấy từ: ứng viên của JSON bước A2 (bỏ mục `rut_bai` = retracted) + mục `apply` CHƯA có toàn văn trong các dashboard
của chủ đề (`--dashboard`).

GIỚI HẠN CÓ CHỦ Ý. Máy chỉ lấy được bản HỢP LỆ tự động (OA/giấy phép mở); bài tường phí hoặc bị trang NXB chặn máy vẫn cần
bác sĩ (làn trình duyệt) hay quyền truy cập — bước này nói rõ bài nào, KHÔNG lách. Phụ trợ: lỗi một công cụ không chặn
chuỗi (mã 0, ghi vào báo cáo + một dòng «⚠ …» ra stdout cho người gọi); mã 2 khi đầu vào hỏng (JSON A2 không đọc được) hoặc
⚪ KHÔNG ĐO ĐƯỢC (15/10/2026: `--a2-json`/`--dashboard` đã khai mà vắng, hoặc kho toàn văn vắng — trước đó bị bỏ lặng lẽ ⇒ «Không có
PMID nào» mã 0). Không có PMID nào ⇒ mã 0, báo cáo nói rõ. Kho: `--kho`, mặc định EBM-Dashboards/toan_van_oa theo bố cục lồng rồi
anh em (`ban_sao_tran.duong_goc`).

MỌI TRÍCH DẪN + PHIẾU XÁC THỰC (11/10/2026, bác sĩ: «đảm bảo tất cả phải được kiểm tra, đọc và tải toàn văn giúp tôi, nếu
tài liệu không tải và đọc toàn văn được thì sẽ đưa ra giải pháp để tôi xác thực»). `--moi-trich-dan` xét MỌI trích dẫn của
dashboard (mục + tham khảo — đúng tập định danh nhóm EndNote của chủ đề chứa), không chỉ ứng viên và mục apply; không trần
PMID (trừ `--tran`). Báo cáo thêm bảng «PHIẾU XÁC THỰC»: TỪNG trích dẫn một dòng — đã có toàn văn (nguồn nào, đã đọc sâu
chưa) hay cần bác sĩ, kèm GIẢI PHÁP cụ thể theo đúng đường đọc của bài (làn Chrome uỷ quyền · bác sĩ đọc rồi ghi kết luận ·
Find Full Text · xin tác giả/thư viện · giữ trần «Cân nhắc» khi chỉ có tóm tắt). Trích dẫn chỉ có DOI cũng có dòng riêng
(chuỗi toàn văn chạy theo PMID nên KHÔNG tự lấy được — nói thẳng). Bộ năm (`xuat_goi_cap_nhat.py`) chạy chế độ này mỗi lần
cập nhật chủ đề.

Dùng:  python3 tools/toan_van_theo_chu_de.py --a2-json logs/<run>.A2-<slug>.json [--dashboard <db.html> …] \\
           --bao-cao logs/<run>.TV-<slug>.md
       python3 tools/toan_van_theo_chu_de.py --dashboard <db.html> --moi-trich-dan --bao-cao derivatives/<mã>_toan-van.md
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
_sp_bst = importlib.util.spec_from_file_location("_bst_tv_cd", REPO / "tools" / "ban_sao_tran.py")
_bst = importlib.util.module_from_spec(_sp_bst)
_sp_bst.loader.exec_module(_bst)
# Gốc dữ liệu tìm theo bố cục LỒNG rồi ANH EM (vá 15/10/2026, TT-07) — cùng cách `nap_endnote_chu_de`/`xuat_goi_cap_nhat` dùng; ghép
# cứng `REPO / "EBM-Dashboards"` từng làm bước này chạy từ worktree/bố cục anh em trỏ vào một kho MA (không tồn tại, sẽ bị tạo).
DASH = _bst.duong_goc("EBM-Dashboards", REPO) or (REPO / "EBM-Dashboards")
KHO = DASH / "toan_van_oa"
TRAN_PMID = 60          # một lượt theo chủ đề: tối đa 60 PMID (ứng viên ≤ 6/tầng + mục apply thiếu) — tránh tải dồn
TIMEOUT_CONG_CU = 900   # giây cho mỗi công cụ
MA_PHIEU_CON_BAI_CHO = 1  # mã thoát của `doc_toan_van_co_nguoi.py` (phiếu): còn bài chờ bác sĩ — KHÔNG phải lỗi
TRAN_GIAY_DUONG_DOC = 900   # trần giây dò đường đọc online (--moi-trich-dan) — bài sau trần ghi «chưa đo được», không treo cả bộ năm


def _nap_gom():
    sp = importlib.util.spec_from_file_location("_gom_tv_cd", REPO / "tools" / "gom_toan_van_dashboard.py")
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def pmid_tu_a2(duong: Path) -> list[str]:
    """PMID ứng viên của JSON bước A2, giữ thứ tự, bỏ trùng; bỏ mục đã bị rút (`rut_bai` = retracted). Lỗi đọc ⇒ ValueError."""
    try:
        d = json.loads(Path(duong).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise ValueError(f"không đọc được JSON A2 {duong}: {e}") from e
    ds: list[str] = []
    for t in d.get("topics") or []:
        for c in t.get("candidates") or []:
            pm = str(c.get("pmid") or "").strip()
            if re.fullmatch(r"\d{6,9}", pm) and c.get("rut_bai") != "retracted" and pm not in ds:
                ds.append(pm)
    return ds


_DTV = None


def co_toan_van(pmid: str, kho: Path, gom=None) -> bool:
    """PMID ĐÃ ĐỌC toàn văn theo NGUỒN SỰ THẬT dùng chung `doc_toan_van_co_nguoi.bao_phu_cuc_bo` (toàn văn máy đọc — loại trang
    giới thiệu kho lưu trữ —, hồ sơ làn trình duyệt, hoặc bác sĩ đã đọc trực tiếp). `gom` giữ cho tương thích chữ ký."""
    dtv = _dtv()
    return dtv.bao_phu_cuc_bo([pmid], kho)[pmid] in dtv.TRANG_THAI_DA_PHU


def _dtv():
    """Mô-đun `doc_toan_van_co_nguoi` — NGUỒN SỰ THẬT dùng chung về độ phủ toàn văn (nạp một lần)."""
    global _DTV
    if _DTV is None:
        sp = importlib.util.spec_from_file_location("_dtv_tv_cd", REPO / "tools" / "doc_toan_van_co_nguoi.py")
        _DTV = importlib.util.module_from_spec(sp)
        sys.modules["_dtv_tv_cd"] = _DTV
        sp.loader.exec_module(_DTV)
    return _DTV


def pmid_apply_thieu(dashboards: list[Path], kho: Path, gom=None) -> list[str]:
    """PMID chính (`pmid:`) của mục decision='apply' CHƯA ĐỌC toàn văn (theo nguồn sự thật `bao_phu_cuc_bo`)."""
    sp = importlib.util.spec_from_file_location("_vd_tv_cd", REPO / "sync/skills/cap-nhat-chung-cu-y-khoa/tools/verify_dashboard.py")
    vd = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(vd)
    ds: list[str] = []
    for db in dashboards:
        blk = vd.extract_data_block(Path(db).read_text(encoding="utf-8", errors="replace"))
        if not blk:
            continue
        for ch in vd.split_items(blk):
            if vd.field(ch, "decision") != "apply":  # tự khai «full» không thay bằng chứng đọc (bảo đảm 04/10/2026)
                continue
            pm = (vd.field(ch, "pmid") or "").strip()
            if re.fullmatch(r"\d{6,9}", pm) and not co_toan_van(pm, kho, gom) and pm not in ds:
                ds.append(pm)
    return ds


def trich_dan_moi_dashboard(dashboards: list[Path]) -> tuple[list[str], list[str]]:
    """MỌI trích dẫn (mục + tham khảo) — đúng tập định danh mà nhóm EndNote của chủ đề chứa
    (`nap_endnote_chu_de.trich_dinh_danh`). Trả (PMID, DOI của các trích dẫn KHÔNG có PMID), giữ thứ tự, bỏ trùng."""
    sp = importlib.util.spec_from_file_location("_nap_en_tv_cd", REPO / "tools" / "nap_endnote_chu_de.py")
    nap = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(nap)
    doc = nap._nap_doc_data()
    pm: list[str] = []
    doi: list[str] = []
    for db in dashboards:
        for d in nap.trich_dinh_danh(doc(db) or {}):
            if d.get("pmid"):
                if d["pmid"] not in pm:
                    pm.append(d["pmid"])
            elif d.get("doi") and d["doi"] not in doi:
                doi.append(d["doi"])
    return pm, doi


# Trạng thái ĐÃ PHỦ của nguồn sự thật `bao_phu_cuc_bo` → nhãn cho bác sĩ.
NHAN_DA_PHU = {
    "oa_xml": "máy có toàn văn — PMC truy cập mở (XML)",
    "oa_khac": "máy có toàn văn — bản giấy phép mở (Unpaywall)",
    "tdm_nxb": "máy có toàn văn — kênh TDM của NXB (Wiley)",
    "phien_chrome": "máy có toàn văn — phiên Chrome uỷ quyền của bác sĩ",
    "da_doc_trinh_duyet": "đã đọc qua làn trình duyệt (hồ sơ trích xuất)",
    "bac_si_da_doc_truc_tiep": "bác sĩ đã đọc trực tiếp (kết luận ghi sổ)",
}


def chua_do_duoc(p: dict) -> bool:
    """Đường đọc «chua_ro» vì LỖI MẠNG (Europe PMC/doi.org) hoặc hết trần giờ dò — «chưa đo được», KHÔNG phải «cần bác sĩ».

    `chua_ro` vì «không có DOI/URL toàn văn» thì vẫn là việc của bác sĩ (máy đã tra được, chỉ là không có đường)."""
    return p.get("cach") == "chua_ro" and (bool(p.get("het_gio")) or "lỗi" in (p.get("ly_do") or ""))


def giai_phap(p: dict) -> str:
    """Giải pháp xác thực cho MỘT bài máy chưa đọc toàn văn — theo đúng đường đọc `doc_toan_van_co_nguoi.duong_doc` trả về."""
    pm, cach, url = p.get("pmid", ""), p.get("cach", ""), p.get("url") or ""
    pubmed = f"https://pubmed.ncbi.nlm.nih.gov/{pm}/"
    if cach == "trinh_duyet":
        mo = (f"mở {url} trong Chrome hồ sơ «Dr Luân» (miền {p.get('mien', '?')}), bác sĩ tự đăng nhập/vượt chặn rồi nói «xong»")
        # «Claude lưu bản sao» CHỈ khi NXB có uỷ quyền của bác sĩ còn hiệu lực (vá 15/10/2026, W2): phiên lưu bản sao
        # (`phien_uy_quyen_chrome.py --kiem`) từ chối mọi NXB khác — hứa «lưu» cho NXB chưa kiểm điều khoản là dạy agent làm sai.
        if p.get("dieu_khoan") == _dtv().KET_LUAN_UY_QUYEN:
            return (f"Làn Chrome có uỷ quyền: {mo} — Claude lưu bản sao (cần phiên uỷ quyền đang mở: bác sĩ nói câu uỷ quyền ⇒ "
                    "`python3 tools/phien_uy_quyen_chrome.py --mo \"<nguyên văn>\"`, `--kiem` trước mỗi bài), đọc sâu, gắn vào EndNote.")
        if p.get("dieu_khoan") == "chua_kiem":
            return (f"Làn trình duyệt có bác sĩ: ⚠ điều khoản NXB về AI chưa kiểm — Claude đọc trang điều khoản trước; chưa thuộc "
                    f"phạm vi lưu — {mo}, Claude lập hồ sơ trích xuất có cấu trúc rồi "
                    "`python3 tools/doc_toan_van_co_nguoi.py --nap <hồ sơ> --ghi` (hồ sơ khai `dieu_khoan`; KHÔNG lưu bản sao).")
        return (f"Làn trình duyệt có bác sĩ: {mo}; NXB ngoài phạm vi phiên lưu bản sao — Claude trích xuất có cấu trúc rồi "
                "`python3 tools/doc_toan_van_co_nguoi.py --nap <hồ sơ> --ghi` (KHÔNG lưu bản sao).")
    if chua_do_duoc(p):
        return (f"Chưa đo được ({p.get('ly_do', 'lỗi mạng')}) — KHÔNG phải «không có toàn văn»; chạy lại lệnh này khi mạng ổn. "
                f"Cần gấp: mở {pubmed} → «Full text links».")
    if cach == "bac_si_doc_truc_tiep":
        return (f"NXB {p.get('nxb', '?')} cấm xử lý bằng AI và CHƯA có uỷ quyền: bác sĩ tự đọc {url} rồi ghi kết luận "
                f"`python3 tools/doc_toan_van_co_nguoi.py --bac-si-da-doc {pm} --ghi-chu \"<kết luận>\" --ghi`; hoặc nói "
                f"«uỷ quyền máy đọc {p.get('nxb', '?')}».")
    if cach == "oa_chua_gom":
        return f"Có bản truy cập mở ({p.get('pmcid', '?')}) nhưng lượt này chưa gom được — chạy lại lệnh này."
    if cach == "khong_truy_cap":
        return ("Đã ghi «không có quyền đọc». Xác thực bằng: (1) EndNote → chọn bài → Find Full Text qua tài khoản cơ sở; "
                "(2) xin bản từ tác giả liên hệ (email trong bài, ResearchGate); (3) nhờ thư viện cơ sở (document delivery); "
                "(4) không lấy được ⇒ giữ thẩm định từ TÓM TẮT, mục ở trần «Cân nhắc» (`appraisalCompleteness:'partial'`).")
    if cach == "chua_co":
        return "Chạy lại có mạng để biết đường đọc của bài."
    ly = f" ({p['ly_do']})" if p.get("ly_do") else ""
    return (f"Chưa xác định được đường đọc{ly}: mở {pubmed} → «Full text links», hoặc EndNote → Find Full Text; lấy được thì "
            "theo làn Chrome như trên.")


def phieu_xac_thuc(pmids: list[str], dois: list[str], kho: Path, lap_phieu, co_doc_sau) -> tuple[list[str], dict]:
    """Bảng TỪNG trích dẫn: trạng thái toàn văn + đọc sâu, hoặc giải pháp để bác sĩ xác thực. Trả (dòng Markdown, đếm)."""
    dtv = _dtv()
    trang = dtv.bao_phu_cuc_bo(pmids, kho) if pmids else {}
    thieu = [pm for pm in pmids if trang.get(pm) not in dtv.TRANG_THAI_DA_PHU]
    duong = {p["pmid"]: p for p in (lap_phieu(thieu) if thieu else [])}
    dem = {"da_phu": 0, "doc_sau": 0, "can_bac_si": 0, "khong_do_duoc": 0, "chi_doi": len(dois)}
    hang = ["| # | Trích dẫn | Trạng thái | Việc cần làm / giải pháp xác thực |", "|---|---|---|---|"]
    for i, pm in enumerate(pmids, 1):
        t = trang.get(pm, "chua_co")
        if t in dtv.TRANG_THAI_DA_PHU:
            dem["da_phu"] += 1
            ds = co_doc_sau(pm)
            dem["doc_sau"] += 1 if ds else 0
            viec = "—" if ds or t == "bac_si_da_doc_truc_tiep" else "Có toàn văn, chưa có bản đọc sâu tự động: đọc trực tiếp khi thẩm định."
            hang.append(f"| {i} | PMID {pm} | ✓ {NHAN_DA_PHU.get(t, t)}{' · đã đọc sâu' if ds else ''} | {viec} |")
        else:
            p = duong.get(pm) or {"pmid": pm, "cach": t}
            if chua_do_duoc(p):  # lỗi mạng ⇒ «chưa đo được», đếm RIÊNG — không đẩy thành việc tay của bác sĩ (W6)
                dem["khong_do_duoc"] += 1
                hang.append(f"| {i} | PMID {pm} | ⚪ chưa đo được ({p.get('ly_do', 'lỗi mạng')}) | {giai_phap(p)} |")
                continue
            dem["can_bac_si"] += 1
            hang.append(f"| {i} | PMID {pm} | ✗ chưa đọc toàn văn ({p.get('cach', t)}) | {giai_phap(p)} |")
    for j, d in enumerate(dois, len(pmids) + 1):
        hang.append(f"| {j} | DOI {d} | ✗ không có PMID — chuỗi toàn văn tự động không xét | Mở https://doi.org/{d}; đọc "
                    "được thì bác sĩ ghi kết luận vào mục của dashboard; không lấy được ⇒ giữ trần «Cân nhắc». |")
    tong = len(pmids) + len(dois)
    dau = [f"## PHIẾU XÁC THỰC — {tong} trích dẫn: {dem['da_phu']} đã đọc toàn văn ({dem['doc_sau']} có bản đọc sâu) · "
           f"{dem['can_bac_si']} cần bác sĩ · {dem['chi_doi']} chỉ có DOI"
           + (f" · {dem['khong_do_duoc']} chưa đo được (lỗi mạng — chạy lại khi mạng ổn)" if dem["khong_do_duoc"] else ""), ""]
    return dau + hang + [""], dem


def _chay(lenh: list[str]) -> tuple[int, str]:
    try:
        # encoding cố định (14/10/2026): công cụ con in UTF-8; để trống thì Python giải mã bằng bảng mã máy ⇒ Windows
        # chưa bật UTF-8 mode mất đầu ra, máy locale ASCII ném UnicodeDecodeError ra khỏi hàm này.
        r = subprocess.run(lenh, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=TIMEOUT_CONG_CU, cwd=str(REPO))
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return -9, f"QUÁ {TIMEOUT_CONG_CU} giây — bỏ bước này, lượt sau chạy lại"
    except OSError as e:
        return -1, f"không chạy được: {e}"


def lap_phieu_co_han(kho: Path, *, tran_giay: float | None = None, dong_ho=time.monotonic, dtv=None):
    """Bộ dò đường đọc online có TRẦN GIỜ (vá 15/10/2026, W1): `lap_phieu` online chạy NGAY trong tiến trình, mỗi PMID tới Europe PMC
    (timeout 30 s × 3 lần thử) rồi doi.org — không trần thì ⑦ của bộ năm có thể chạy quá ngân sách B4 của orchestrator. Dò từng PMID;
    hết trần ⇒ các bài còn lại ghi `chua_ro` + `het_gio` («chưa đo được — chạy lại»), KHÔNG đọc thành «cần bác sĩ»."""
    tran = TRAN_GIAY_DUONG_DOC if tran_giay is None else tran_giay

    def lap(ds: list[str]) -> list[dict]:
        m = dtv or _dtv()
        han = dong_ho() + tran
        ra: list[dict] = []
        for i, pm in enumerate(ds):
            if dong_ho() >= han:
                ra += [{"pmid": x, "cach": "chua_ro", "het_gio": True,
                        "ly_do": f"hết trần {int(tran)} giây dò đường đọc lượt này"} for x in ds[i:]]
                break
            ra += m.lap_phieu([pm], ngoai_tuyen=False, kho=kho)
        return ra
    return lap


def _canh_bao_cong_cu(ten: str, rc: int, out: str) -> str:
    """Dòng «⚠ …» cho công cụ con trả mã ≠ 0 — in ra stdout để `xuat_goi_cap_nhat` (⑦) và phiếu orchestrator bắt được (W6).

    Trước 15/10/2026 mã 2 (HẠ TẦNG — «KHÔNG kết luận độ phủ» của gom) chỉ nằm ở tiêu đề mục trong báo cáo; công cụ vẫn trả 0 và
    người gọi coi bước toàn văn là xong."""
    cuoi = (out.strip().splitlines() or [""])[-1].strip()[:160]
    if rc == 2:
        loai = "HẠ TẦNG (mạng/kho/đầu vào) — KHÔNG kết luận độ phủ toàn văn; chạy lại khi mạng ổn"
    elif rc == -9:
        loai = f"QUÁ {TIMEOUT_CONG_CU} giây — bỏ bước này, lượt sau chạy lại"
    else:
        loai = "xem báo cáo"
    return f"⚠ {ten}: mã {rc} — {loai}" + (f" · {cuoi}" if cuoi else "")


def _khong_do(bao_cao: Path, ly_do: str) -> int:
    """⚪ KHÔNG ĐO ĐƯỢC (TT-06): đầu vào đã khai mà vắng, hoặc kho toàn văn vắng ⇒ mã 2, báo cáo nói rõ — KHÔNG in «Không có PMID
    nào» (xanh giả) hay «N cần bác sĩ» (đỏ giả)."""
    dong = [f"# TOÀN VĂN THEO CHỦ ĐỀ — {datetime.now().isoformat(timespec='seconds')}", "",
            f"⚪ KHÔNG ĐO ĐƯỢC — {ly_do}", "",
            "KHÔNG kết luận «không có PMID nào» hay «cần bác sĩ»: sửa đầu vào rồi chạy lại. Cần bác sĩ kiểm chứng."]
    bao_cao.parent.mkdir(parents=True, exist_ok=True)
    bao_cao.write_text("\n".join(dong) + "\n", encoding="utf-8")
    print(f"⚪ KHÔNG ĐO ĐƯỢC — {ly_do}")
    print(f"→ {bao_cao}")
    return 2


def main(argv: list[str] | None = None, *, chay=_chay, kho: Path | None = None, lap_phieu=None) -> int:
    ap = argparse.ArgumentParser(description="Toàn văn cho ứng viên và mục apply của MỘT chủ đề (bước TV của orchestrator)")
    ap.add_argument("--a2-json", type=Path, help="JSON của bước A2 (logs/<run>.A2-<slug>.json)")
    ap.add_argument("--dashboard", nargs="*", default=[], type=Path, help="dashboard của chủ đề — lấy mục apply thiếu toàn văn")
    ap.add_argument("--moi-trich-dan", action="store_true",
                    help="MỌI trích dẫn của dashboard (mục + tham khảo) + phiếu xác thực cho bác sĩ")
    ap.add_argument("--tran", type=int, help=f"trần PMID mỗi lượt (mặc định {TRAN_PMID}; với --moi-trich-dan: không trần); 0 = không trần")
    ap.add_argument("--bao-cao", type=Path, required=True, help="tệp Markdown báo cáo")
    ap.add_argument("--kho", type=Path, default=None,
                    help="thư mục toan_van_oa (mặc định: EBM-Dashboards/toan_van_oa — bố cục lồng rồi anh em); bộ năm truyền kho "
                         "cạnh dashboard, đúng kho cổng liêm chính đọc")
    a = ap.parse_args(argv)
    kho = kho or a.kho or KHO
    # TT-06 (15/10/2026): đầu vào ĐÃ KHAI mà vắng trước đây bị bỏ lặng lẽ ⇒ «Không có PMID nào…» mã 0 (xanh giả).
    vang = ([str(a.a2_json)] if a.a2_json and not a.a2_json.exists() else []) + [str(d) for d in a.dashboard if not d.exists()]
    if vang:
        return _khong_do(a.bao_cao, "đầu vào đã khai mà KHÔNG có: " + ", ".join(vang))
    if not kho.is_dir():
        return _khong_do(a.bao_cao, f"không thấy kho toàn văn {kho} (chạy từ worktree/bản sao trần? thêm --kho "
                                    "<EBM-Dashboards>/toan_van_oa)")
    try:
        gom = _nap_gom()
    except Exception:  # noqa: BLE001 — thiếu bộ gom thì vẫn liệt kê được, chỉ không lọc trang giới thiệu
        gom = None
    ung_vien: list[str] = []
    if a.a2_json:
        try:
            ung_vien = pmid_tu_a2(a.a2_json)
        except ValueError as e:
            print(f"✗ {e}")
            return 2
    dashboards = list(a.dashboard)
    apply_thieu = pmid_apply_thieu(dashboards, kho, gom)
    moi_pm, moi_doi = trich_dan_moi_dashboard(dashboards) if a.moi_trich_dan else ([], [])
    tat_ca = list(dict.fromkeys(ung_vien + apply_thieu + moi_pm))
    tran = a.tran if a.tran is not None else (0 if a.moi_trich_dan else TRAN_PMID)
    bo_tran = tat_ca[tran:] if tran > 0 else []
    tat_ca = tat_ca[:tran] if tran > 0 else tat_ca
    truoc = {pm for pm in tat_ca if co_toan_van(pm, kho, gom)}
    dong = [f"# TOÀN VĂN THEO CHỦ ĐỀ — {datetime.now().isoformat(timespec='seconds')}", "",
            f"- Ứng viên A2: {len(ung_vien)} PMID · mục apply chưa có toàn văn: {len(apply_thieu)} PMID"
            + (f" · MỌI trích dẫn: {len(moi_pm)} PMID + {len(moi_doi)} chỉ có DOI" if a.moi_trich_dan else ""),
            f"- Xử lý lượt này: {len(tat_ca)} PMID (trần {tran or 'không'}"
            + (f"; DỜI sang lượt sau: {', '.join(bo_tran)}" if bo_tran else "")
            + f") · đã có toàn văn từ trước: {len(truoc)}", ""]
    canh_bao: list[str] = []
    if not tat_ca:
        dong.append("Không có PMID nào cần lấy toàn văn lượt này.")
    else:
        py = sys.executable
        # doc_sau_toan_van nhận `--dash` (kho = <dash>/toan_van_oa) ⇒ truyền để nó đọc ĐÚNG kho này (TT-07). gom_toan_van_dashboard và
        # doc_toan_van_co_nguoi chưa có cờ chọn kho ⇒ không truyền (cờ lạ làm argparse chết).
        dash_con = ["--dash", str(kho.parent)] if kho.name == "toan_van_oa" else []
        buoc = [
            ("① Gom bản hợp lệ (PMC OA + giấy phép mở)",
             [py, str(REPO / "tools/gom_toan_van_dashboard.py"), "--pmid", *tat_ca, "--unpaywall"]),
            ("② Đọc sâu bài có toàn văn", [py, str(REPO / "tools/doc_sau_toan_van.py"), *dash_con, "--pmid", *tat_ca]),
        ]
        for ten, lenh in buoc:
            rc, out = chay(lenh)
            dong += [f"## {ten} — mã {rc}", "```", "\n".join(out.strip().splitlines()[-25:]) or "(không in gì)", "```", ""]
            if rc != 0:
                canh_bao.append(_canh_bao_cong_cu(ten, rc, out))
                dong += [canh_bao[-1], ""]
        con_thieu = [pm for pm in tat_ca if not co_toan_van(pm, kho, gom)]
        moi = sorted(set(tat_ca) - truoc - set(con_thieu))
        dong += [f"## Kết quả: +{len(moi)} bài có toàn văn mới · còn thiếu {len(con_thieu)}",
                 "", f"- Mới có toàn văn: {', '.join(moi) or '—'}", f"- Còn thiếu: {', '.join(con_thieu) or '—'}", ""]
        if con_thieu and not a.moi_trich_dan:
            rc, out = chay([py, str(REPO / "tools/doc_toan_van_co_nguoi.py"), "--pmid", *con_thieu])
            # Phiếu trả 1 = «còn bài chờ bác sĩ» — đúng việc của bước này, đã đếm ở «còn thiếu N». Trước 20/10/2026 mã 1 cũng thành
            # dòng ⚠ ⇒ orchestrator in «công cụ con lỗi hạ tầng/quá giờ» cho MỌI chủ đề có bài thiếu toàn văn (đỏ giả, 7/7 chủ đề
            # lượt 20/10). Chỉ 2 (KHÔNG ĐO ĐƯỢC), quá giờ hay mã lạ mới là cảnh báo.
            loi_3 = rc not in (0, MA_PHIEU_CON_BAI_CHO)
            if loi_3:
                canh_bao.append(_canh_bao_cong_cu("③ Phiếu làn trình duyệt", rc, out))
            dong += [f"## ③ Phiếu làn trình duyệt có bác sĩ cho bài còn thiếu — mã {rc}", "```",
                     "\n".join(out.strip().splitlines()[-60:]) or "(không in gì)", "```", "",
                     *([canh_bao[-1], ""] if loi_3 else []),
                     "> Bài tường phí/bị trang NXB chặn máy: bác sĩ mở theo phiếu (tự qua Cloudflare/đăng nhập), Claude trích",
                     "> xuất có cấu trúc rồi `doc_toan_van_co_nguoi.py --nap`. Bài không có quyền truy cập ⇒ thẩm định từ tóm",
                     "> tắt và khai `appraisalCompleteness:'partial'` (cổng giữ ở mức «Cân nhắc»)."]
    tom_phieu = ""
    if a.moi_trich_dan and (moi_pm or moi_doi):
        lap = lap_phieu or lap_phieu_co_han(kho)
        phieu, dem = phieu_xac_thuc(moi_pm, moi_doi, kho, lap, lambda pm: (kho / "doc_sau" / f"PMID-{pm}.md").is_file())
        dong += [""] + phieu
        tom_phieu = phieu[0].replace("## ", "")
        if dem["khong_do_duoc"]:
            canh_bao.append(f"⚠ {dem['khong_do_duoc']} trích dẫn CHƯA ĐO ĐƯỢC đường đọc (lỗi mạng/hết trần giờ) — KHÔNG phải «không có "
                            "toàn văn»; chạy lại khi mạng ổn")
            dong += [canh_bao[-1], ""]
        if dem["can_bac_si"] or dem["chi_doi"]:
            dong += ["> Bài «cần bác sĩ»: làm theo cột giải pháp rồi chạy lại lệnh này — bảng tự cập nhật. Bài không lấy được",
                     "> toàn văn bằng mọi đường ⇒ thẩm định từ tóm tắt, mục giữ trần «Cân nhắc»; KHÔNG được coi là đã đọc."]
    dong += ["", "Máy chỉ ĐO và LẤY bản hợp lệ — không đổi dashboard, không đổi decision. Cần bác sĩ kiểm chứng."]
    a.bao_cao.parent.mkdir(parents=True, exist_ok=True)
    a.bao_cao.write_text("\n".join(dong) + "\n", encoding="utf-8")
    print("\n".join(dong[:4]))
    if tom_phieu:
        print(tom_phieu)
    for cb in canh_bao:  # dòng «⚠» đứng riêng một dòng ⇒ bộ năm (⑦) in lại được, không bị nuốt
        print(cb)
    print(f"→ {a.bao_cao}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
