#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TRÍCH DẪN TỰ TẠO TỔNG HỢP CHỦ ĐỀ — mỗi nhóm EndNote «EBM · <chủ đề>» thêm MỘT bản ghi «★ TÓM TẮT THỰC HÀNH» (29/10/2026).

Bác sĩ yêu cầu 29/10/2026: mỗi vấn đề đã cập nhật chứng cứ và trích dẫn thì bổ sung «một trích dẫn tự tạo giúp tổng hợp lại
những vấn đề áp dụng cho thực hành lâm sàng hay là bản tóm tắt vấn đề chính». Nhóm EndNote của chủ đề đang chỉ có các bài gốc;
bản ghi này đứng cạnh chúng như một «trang bìa» đọc nhanh của cả chủ đề.

NỘI DUNG — chép NGUYÊN từ khối DATA của bản dashboard MỚI NHẤT, không sinh khẳng định mới (cùng luật khối «EBM · ĐỌC NHANH»):
  ⛔ CỜ ĐỎ · ✅ LÀM NGAY · ✖️ KHÔNG NÊN LÀM (đúng 3 khoá `DATA.summary`) — đứng trước như bản đọc ②; ⭐ VẤN ĐỀ CHÍNH
  (`summary.conclusion`); rồi các mục theo quyết định: ✅ ÁP DỤNG NGAY (tiêu đề + hành động + PMID/DOI) · ⚠️ CÂN NHẮC CHỌN LỌC ·
  ⏸️ CHƯA ĐỦ THAY ĐỔI (tiêu đề + PMID/DOI). Rút gọn bằng CHỌN TRƯỜNG, không cắt câu. Nhấn mạnh bằng nhãn IN HOA + biểu tượng
  trong mặt phẳng cơ bản (BMP) — EndNote đổi ký tự ngoài BMP thành «?» (đo 13/10/2026); chữ của dashboard đi qua
  `tom_tat_endnote_vi._gon` (emoji ngoài BMP ⇒ nhãn chữ).
  Chân bản ghi nói ĐÚNG trạng thái cổng: chỉ ghi «đã qua cổng» khi bản Word cùng bộ năm ghi «verify_dashboard.py --online đã
  PASS» VÀ sidecar `<mã>_TaiLieuChiTiet.data-sha256` trùng băm khối DATA HIỆN TẠI (dashboard sửa sau lượt xuất ⇒ không còn tính
  là đã xác minh); còn lại ⇒ «⚠️ CHƯA xác minh nguồn sống». `--chua-xac-minh` (bước ⑧ truyền khi cổng chưa PASS) luôn thắng.

BẢN GHI — loại Report, tác giả tập thể «EBM Copilot», nhãn «EBM · TÓM TẮT CHỦ ĐỀ», từ khoá «EBM: <khoá chủ đề>». Khoá bền
`EBM-TT:<khoá chủ đề>` ở «Accession Number» (mọi công cụ khác đọc trường này đều so KHỚP NGUYÊN với PMID thuần số ⇒ khoá chữ
không bị nhầm). Đính PDF tài liệu chi tiết ③⑤ của bộ năm (`derivatives/<mã>_TaiLieuChiTiet.pdf`) khi sidecar còn khớp DATA.
Mỗi lượt: chưa có bản ghi ⇒ nhập MỘT bản ghi rồi tra lại (không thấy ⇒ «nhập hụt», dọn PDF vừa đặt); đã có ⇒ so «dấu» nội
dung trong Notes — khác thì GHI ĐÈ Title/Year/Abstract rồi Notes (Notes ghi CUỐI: hỏng giữa chừng thì lượt sau làm lại), không
bao giờ nhập bản thứ hai. PDF mới thay PDF cũ chỉ khi mọi tệp đang gắn là tài liệu chi tiết do công cụ này gắn; có tệp khác
(bác sĩ tự gắn) ⇒ THÊM, không ghi đè.

NHÓM — đi đúng `nap_endnote_chu_de.xep_vao_nhom` (BH170): nhóm chưa có ⇒ post tạo đúng MỘT nhóm; ĐÃ có ⇒ không post (post
luôn sinh nhóm trùng tên — đo 24/10/2026), bản ghi vào HÀNG CHỜ cho bác sĩ kéo một lần (`nap_endnote_chu_de.py --cho-vao-nhom
"<tên>"`); lần cập nhật sau sửa tại chỗ nên không phải kéo lại. Bước ⑧ (`nap_endnote_chu_de.py --kem-tong-hop`) gọi
`dam_bao_ban_ghi` cho bản MỚI NHẤT của chủ đề TRƯỚC khi đăng nhóm ⇒ chủ đề MỚI có bản ghi tổng hợp ngay trong lần post tạo nhóm.

Dùng:
  python3 tools/trich_dan_tong_hop_chu_de.py --file EBM-Dashboards/WebDashboard_X.html --in      # xem nội dung, không EndNote
  python3 tools/trich_dan_tong_hop_chu_de.py --file EBM-Dashboards/WebDashboard_X.html [--ap-dung]
  python3 tools/trich_dan_tong_hop_chu_de.py --tat-ca [--ap-dung]   # mọi chủ đề ĐÃ có nhóm EndNote (bảng nhom_theo_chu_de)
Mã thoát: 0 xong · 2 không chạy được (không phải Mac, chưa cấu hình, thư viện chưa mở) hoặc có chủ đề lỗi/nhập hụt · 3 tham số sai.
Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import sys
import tempfile
import time
from datetime import date
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
TIEN_TO_KHOA = "EBM-TT:"
NHAN = "EBM · TÓM TẮT CHỦ ĐỀ"
MO_DAU = "【EBM · TÓM TẮT THỰC HÀNH】"
TIEU_DE = "★ TÓM TẮT THỰC HÀNH · "
TAC_GIA = "EBM Copilot,"  # dấu phẩy cuối = tác giả tập thể (EndNote không tách họ/tên)
NOI_XB = "EBM Copilot — bản tổng hợp nội bộ, chưa bình duyệt"
TU_KHOA_LOAI = "EBM: tóm tắt chủ đề"
CAU_PASS = "đã PASS trước khi xuất"  # câu build_dashboard_docx.py chỉ in khi bộ năm truyền --verified
TIEN_TO_DASH = re.compile(r"^WebDashboard_EBM_VanDeCuThe_")  # quy tắc tên phái sinh của build_dashboard_docx.py
CHO_NHAP_GIAY = 10
MA_OK, MA_KHONG_CHAY, MA_THAM_SO = 0, 2, 3
_ngu = time.sleep


def _nap(ten: str, tep: str | Path):
    """Nạp MỘT lần một mô-đun theo đường dẫn (`tep` tương đối ⇒ trong tools/)."""
    m = sys.modules.get(ten)
    if m is None:
        duong = Path(tep) if Path(tep).is_absolute() else ROOT / "tools" / tep
        sp = importlib.util.spec_from_file_location(ten, duong)
        m = importlib.util.module_from_spec(sp)
        sys.modules[ten] = m
        sp.loader.exec_module(m)
    return m


_NEC = None  # mô-đun nap_endnote_chu_de người gọi đưa vào (bước ⑧ chạy nó như __main__ — không nạp bản thứ hai)


def dat_nec(m) -> None:
    global _NEC
    _NEC = m


def nec():
    """`tools/nap_endnote_chu_de.py` — EndNoteMac, khoá chủ đề, nhóm, dựng XML (một bản cho cả tiến trình)."""
    return _NEC or _nap("_nec_tong_hop", "nap_endnote_chu_de.py")


def _tt():
    return _nap("_tt_tong_hop", "tom_tat_endnote_vi.py")


# ── trạng thái phái sinh của bộ năm ──────────────────────────────────────────────────────────────────────────────────────

def ma_phai_sinh(dash: Path) -> str:
    return TIEN_TO_DASH.sub("", dash.stem)


def bam_data(dash: Path) -> str | None:
    """SHA-256 khối `const DATA` — đúng cách `xuat_goi_cap_nhat.ghi_sidecar_hash_data` băm (cắt bằng `extract_data_block` của
    verify_dashboard). Không đọc/không cắt được ⇒ None (người gọi coi là KHÔNG khớp)."""
    try:
        bst = _nap("_bst_tong_hop", "ban_sao_tran.py")
        vd_tep = bst.duong_cong_cu_pipeline("verify_dashboard.py", ROOT) or (ROOT / "EBM-Dashboards" / "tools"
                                                                              / "verify_dashboard.py")
        vd = _nap("_vd_tong_hop", Path(vd_tep).resolve())
        khoi = vd.extract_data_block(dash.read_text(encoding="utf-8", errors="replace"))
    except Exception:  # noqa: BLE001 — không đo được ⇒ không khẳng định gì
        return None
    return hashlib.sha256(khoi.encode("utf-8")).hexdigest() if khoi else None


def trang_thai_phai_sinh(dash: Path) -> dict:
    """{tuoi, xac_minh, pdf}: `tuoi` = sidecar của bản Word trùng băm DATA hiện tại; `xac_minh` = tuoi VÀ bản Word ghi câu PASS
    của cổng; `pdf` = PDF tài liệu chi tiết (chỉ khi tuoi — PDF cũ mô tả phiên bản khác của chủ đề)."""
    d = dash.parent / "derivatives"
    ma = ma_phai_sinh(dash)
    side, html, pdf = (d / f"{ma}_TaiLieuChiTiet{duoi}" for duoi in (".data-sha256", ".html", ".pdf"))
    try:
        h_luu = side.read_text(encoding="utf-8").strip() if side.is_file() else None
    except OSError:
        h_luu = None
    tuoi = bool(h_luu) and h_luu == bam_data(dash)
    try:
        pass_ = tuoi and html.is_file() and CAU_PASS in html.read_text(encoding="utf-8", errors="replace")
    except OSError:
        pass_ = False
    return {"tuoi": tuoi, "xac_minh": bool(pass_), "pdf": pdf if tuoi and pdf.is_file() else None}


# ── nội dung ─────────────────────────────────────────────────────────────────────────────────────────────────────────────

def khoa_ban_ghi(khoa_chu_de: str) -> str:
    return TIEN_TO_KHOA + khoa_chu_de


def _ds(v) -> list[str]:
    """Danh sách câu của một khoá summary (list hoặc một chuỗi), đã qua `_gon`, bỏ rỗng."""
    g = _tt()._gon
    return [x for x in (g(s) for s in (v if isinstance(v, list) else [v])) if x]


def _dinh_danh(it: dict) -> str:
    pm = str(it.get("pmid") or "").strip()
    if re.fullmatch(r"\d{1,9}", pm):
        return f"PMID {pm}"
    doi = nec().chuan_doi(it.get("doi"))
    return f"doi:{doi}" if doi else ""


def dung_noi_dung(data: dict, dash: Path, *, xac_minh: bool, so_trich_dan: int) -> dict:
    """{tieu_de, tom_tat, nam} của bản ghi tổng hợp — CHỈ chép trường của dashboard (không sinh khẳng định mới)."""
    g = _tt()._gon
    meta = data.get("meta") or {}
    sm = data.get("summary") or {}
    items = [it for it in data.get("items") or [] if isinstance(it, dict)]
    cau_hoi = g(meta.get("question")) or dash.stem
    cap_nhat = g(meta.get("updated"))
    nhan_qd = _tt().NHAN_QD
    theo_qd = {qd: [it for it in items if it.get("decision") == qd] for qd in nhan_qd}
    dong = [f"{MO_DAU} {cau_hoi}",
            f"Dashboard {dash.name}{' · cập nhật ' + cap_nhat if cap_nhat else ''} · {len(items)} mục: "
            f"{len(theo_qd['apply'])} áp dụng · {len(theo_qd['consider'])} cân nhắc · {len(theo_qd['notyet'])} chưa đủ"]

    def phan(tieu: str, cau: list[str]) -> None:
        if cau:
            dong.extend(["", tieu, *(f"• {c}" for c in cau)])

    phan("⛔ CỜ ĐỎ — CHUYỂN TUYẾN / CẤP CỨU", _ds(sm.get("redFlags")))
    phan("✅ LÀM NGAY", _ds(sm.get("doNow")))
    phan("✖️ KHÔNG NÊN LÀM", _ds(sm.get("dontDo")))
    ket_luan = _ds(sm.get("conclusion"))
    if ket_luan:
        dong.extend(["", "⭐ VẤN ĐỀ CHÍNH", *ket_luan])
    for qd, nhan in nhan_qd.items():
        if not theo_qd[qd]:
            continue
        dong.extend(["", f"{nhan} — {len(theo_qd[qd])} mục"])
        for it in theo_qd[qd]:
            dd = _dinh_danh(it)
            dong.append(f"• {g(it.get('id')) or '?'} · {g(it.get('title'))}{' — ' + dd if dd else ''}")
            hanh_dong = g(it.get("action")) if qd == "apply" else ""
            if hanh_dong:
                dong.append(f"  ▶️ THỰC HÀNH: {hanh_dong}")
    dong.extend(["", f"ℹ️ NGUỒN: dashboard có {so_trich_dan} trích dẫn (PMID/DOI ghi ở từng mục; bản ghi gốc nằm cùng nhóm "
                     "EndNote này). Bản ghi tổng hợp KHÔNG phải nguồn gốc — khi viết bài, trích dẫn bài gốc."])
    if xac_minh:
        dong.append(_tt().CHAN)
    else:
        dong.extend([nec().DONG_CHUA_XAC_MINH, nec().CHAN_CHUA_XAC_MINH])
    nam = (re.search(r"(20\d\d)", cap_nhat or "") or re.search(r"_(20\d\d)\d{4}$", dash.stem))
    return {"tieu_de": TIEU_DE + cau_hoi, "tom_tat": "\n".join(dong), "nam": nam.group(1) if nam else ""}


def _sha_tep(p: Path | None) -> str:
    if not p:
        return ""
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for khoi in iter(lambda: f.read(1 << 20), b""):
            h.update(khoi)
    return h.hexdigest()


def dau_van(nd: dict, sha_pdf: str) -> str:
    """Dấu 12 hex của nội dung + PDF — ghi trong Notes để lượt sau biết có cần ghi lại không."""
    goc = json.dumps([nd["tieu_de"], nd["tom_tat"], nd["nam"], sha_pdf], ensure_ascii=False)
    return hashlib.sha256(goc.encode("utf-8")).hexdigest()[:12]


def ghi_chu(dash: Path, khoa: str, dau: str, sha_pdf: str) -> str:
    return (f"Bản ghi TỰ TẠO bởi EBM Copilot ngày {date.today().isoformat()} — tổng hợp từ {dash.name}. Khoá {khoa}. "
            f"Không phải nguồn gốc: trích dẫn nguồn gốc là các bản ghi PMID/DOI cùng nhóm. "
            f"{'PDF: tài liệu chi tiết của bộ năm (sha ' + sha_pdf[:12] + '). ' if sha_pdf else ''}dấu {dau}")


def ban_ghi_xml(nd: dict, khoa: str, khoa_chu_de: str, notes: str, pdf_url: str = "") -> dict:
    """Metadata cho `nap_endnote_chu_de.dung_xml` (khoá ở Accession Number qua `so_truy_cap`, KHÔNG có PMID/DOI)."""
    return {"loai_tl": "Report", "tac_gia": [TAC_GIA], "tieu_de": nd["tieu_de"], "nam": nd["nam"], "nha_xb": NOI_XB,
            "so_truy_cap": khoa, "tom_tat": nd["tom_tat"], "ghi_chu": notes, "nhan": NHAN,
            "tu_khoa": [f"EBM: {khoa_chu_de}", TU_KHOA_LOAI], "ngon_ngu": "vie", "pdf_url": pdf_url}


# ── EndNote ──────────────────────────────────────────────────────────────────────────────────────────────────────────────

def _tep_cua_cong_cu(truong: str) -> bool:
    """Mọi tệp đang gắn đều là tài liệu chi tiết do công cụ này gắn ⇒ được THAY; có tệp khác ⇒ chỉ THÊM."""
    tep = [x.strip() for x in re.split(r"[\r\n]+", truong or "") if x.strip()]
    return all(re.search(r"_TaiLieuChiTiet\.pdf$", x) for x in tep)


def _tim(endnote, khoa: str) -> list[str]:
    return endnote.tim_khop([khoa], "Accession Number").get(khoa) or []


def dam_bao_ban_ghi(endnote, dash: Path, data: dict, nhom: str, ap_dung: bool, *, chua_xac_minh: bool = False
                    ) -> tuple[str | None, dict]:
    """Tạo hoặc cập nhật bản ghi tổng hợp của chủ đề. Trả (mã bản ghi AppleScript | None, báo cáo). KHÔNG đăng nhóm — người
    gọi đưa mã vào `xep_vao_nhom` (bước ⑧: cùng lượt post với các bài của chủ đề)."""
    n = nec()
    khoa_cd = n.khoa_chu_de(dash)
    khoa = khoa_ban_ghi(khoa_cd)
    tt = trang_thai_phai_sinh(dash)
    xac_minh = tt["xac_minh"] and not chua_xac_minh
    nd = dung_noi_dung(data, dash, xac_minh=xac_minh, so_trich_dan=len(n.trich_dinh_danh(data)))
    sha_pdf = _sha_tep(tt["pdf"])
    dau = dau_van(nd, sha_pdf)
    bc: dict = {"khoa": khoa, "nhom": nhom, "xac_minh": xac_minh, "pdf": tt["pdf"].name if tt["pdf"] else None,
                "dau": dau, "ap_dung": ap_dung}
    if endnote is None:
        bc["trang_thai"] = "ke_hoach"
        return None, bc
    co = _tim(endnote, khoa)
    if len(co) > 1:
        bc["trung"] = [n._so_ban_ghi(r) for r in co]  # chỉ báo — công cụ không xoá; sửa bản đầu
    notes = ghi_chu(dash, khoa, dau, sha_pdf)
    if not co:
        if not ap_dung:
            bc["trang_thai"] = "se_tao"
            return None, bc
        url, tm = (n.dat_pdf_vao_thu_vien(endnote.thu_vien, tt["pdf"], None) if tt["pdf"] else ("", None))
        try:
            with tempfile.TemporaryDirectory(prefix="ebm-tong-hop-") as tam:
                tep = Path(tam) / "nhap.xml"
                tep.write_text(n.dung_xml([ban_ghi_xml(nd, khoa, khoa_cd, notes, url)]), encoding="utf-8", newline="\n")
                endnote.nhap(tep)
            for _ in range(CHO_NHAP_GIAY):
                co = _tim(endnote, khoa)
                if co:
                    break
                _ngu(1)
        except Exception:
            if tm:
                shutil.rmtree(tm, ignore_errors=True)
            raise
        if not co:  # `import` im lặng không nhập (vd cửa sổ Preferences đang mở — đo 19/10/2026)
            if tm:
                shutil.rmtree(tm, ignore_errors=True)
            bc.update(trang_thai="nhap_hut", loi="nhập xong mà tra lại không thấy bản ghi tổng hợp")
            return None, bc
        bc["trang_thai"] = "da_tao"
        return co[0], bc
    rid = co[0]
    bc["rec"] = n._so_ban_ghi(rid)
    cu = endnote.doc_truong([rid], "Notes").get(rid)
    if cu is None:
        bc.update(trang_thai="khong_doc_duoc", loi="không đọc được Notes của bản ghi tổng hợp — không ghi")
        return rid, bc
    if f"dấu {dau}" in cu:
        bc["trang_thai"] = "khong_doi"
        return rid, bc
    if not ap_dung:
        bc["trang_thai"] = "se_cap_nhat"
        return rid, bc
    loi: dict[str, str] = {}
    for truong, gia_tri in (("Title", nd["tieu_de"]), ("Year", nd["nam"]), ("Abstract", nd["tom_tat"])):
        loi.update({f"{truong}": v for v in endnote.ghi_truong([(rid, gia_tri)], truong).values() if v})
    if tt["pdf"] and not loi and f"sha {sha_pdf[:12]}" not in cu:
        dang_gan = endnote.doc_truong([rid], "File Attachments").get(rid)
        url, tm = n.dat_pdf_vao_thu_vien(endnote.thu_vien, tt["pdf"], None)
        try:
            (endnote.gan_tep if dang_gan is not None and _tep_cua_cong_cu(dang_gan) else endnote.them_tep)(rid, url)
        except Exception:
            shutil.rmtree(tm, ignore_errors=True)
            raise
        bc["pdf_moi"] = True
    if loi:  # Notes giữ dấu cũ ⇒ lượt sau ghi lại
        bc.update(trang_thai="loi_ghi", loi="; ".join(f"{k}: {v}" for k, v in loi.items())[:300])
        return rid, bc
    loi_notes = [v for v in endnote.ghi_truong([(rid, notes)], "Notes").values() if v]
    bc["trang_thai"] = "loi_ghi" if loi_notes else "da_cap_nhat"
    if loi_notes:
        bc["loi"] = f"Notes: {loi_notes[0]}"[:300]
    return rid, bc


def hook_nap(chua_xac_minh: bool):
    """Hàm `tong_hop` cho `nap_endnote_chu_de.nap_chu_de` (bước ⑧ --kem-tong-hop)."""
    def tong_hop(endnote, dash, data, nhom, ap_dung):
        return dam_bao_ban_ghi(endnote, dash, data, nhom, ap_dung, chua_xac_minh=chua_xac_minh)
    return tong_hop


def chu_de_moi_nhat(dash_goc: Path, bang: dict[str, str]) -> list[Path]:
    """Bản dashboard MỚI NHẤT của mỗi chủ đề ĐÃ có nhóm EndNote (bảng nhom_theo_chu_de). Chủ đề chưa từng nạp EndNote thì
    không tạo bản ghi tổng hợp (không có nhóm để nó đứng cạnh) — bước ⑧ sẽ tạo khi chủ đề được nạp."""
    n = nec()
    ra: dict[str, Path] = {}
    for f in n.sap_xep_phien_ban(sorted(dash_goc.glob("WebDashboard_*.html"))):
        k = n.khoa_chu_de(f)
        if k in bang and k not in ra:
            ra[k] = f
    return list(ra.values())


def _in(bc: dict, dash: Path) -> None:
    nhan = {"ke_hoach": "kế hoạch (chưa kiểm EndNote)", "se_tao": "SẼ TẠO", "se_cap_nhat": "SẼ CẬP NHẬT",
            "khong_doi": "không đổi", "da_tao": "✓ đã tạo", "da_cap_nhat": "✓ đã cập nhật", "nhap_hut": "✗ NHẬP HỤT",
            "loi_ghi": "✗ lỗi ghi", "khong_doc_duoc": "⚪ không đọc được"}.get(bc.get("trang_thai"), bc.get("trang_thai"))
    print(f"• {dash.name}: {nhan} · {'đã qua cổng' if bc.get('xac_minh') else 'CHƯA xác minh'} · "
          f"PDF {bc.get('pdf') or '—'}" + (f" · {bc['loi']}" if bc.get("loi") else ""))
    if bc.get("trung"):
        print(f"   ⚠ {len(bc['trung'])} bản ghi tổng hợp trùng khoá (rec {', '.join(bc['trung'])}) — sửa bản đầu; bác sĩ "
              "chuyển bản thừa vào thùng rác")
    nh = bc.get("nhom_kq") or {}
    if nh.get("cho_vao_nhom_moi"):
        print(f"   ↪ nhóm «{bc['nhom']}» đã có ⇒ bản ghi vào HÀNG CHỜ (kéo một lần): python3 tools/nap_endnote_chu_de.py "
              f"--cho-vao-nhom \"{bc['nhom']}\"")
    elif nh.get("dang_vao_nhom"):
        print(f"   ✓ đã tạo nhóm «{bc['nhom']}» kèm bản ghi tổng hợp")


def mo_endnote(ap_dung: bool):
    """EndNoteMac của thư viện đã cấu hình (đi đúng các phép kiểm của nap_endnote_chu_de). Không chạy được ⇒ KhongChayDuoc."""
    n = nec()
    if not n._la_mac():
        raise n.KhongChayDuoc(n.THONG_DIEP_KHONG_PHAI_MAC)
    ch = n.doc_cau_hinh()
    if ch is None:
        raise n.KhongChayDuoc(f"chưa cấu hình (hoặc cấu hình hỏng) thư viện EndNote — xem {n.CAU_HINH}")
    tv = Path(ch["thu_vien"])
    if not tv.is_file():
        raise n.KhongChayDuoc(f"thư viện đã cấu hình không còn tồn tại: {tv}")
    en = n.EndNoteMac(ch["ung_dung"], tv)
    if not en.dang_mo_dung_thu_vien():
        if not ap_dung:
            return None
        en.mo_thu_vien()
    return en


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    ap.add_argument("--file", nargs="*", default=[], help="dashboard WebDashboard_*.html (bản MỚI NHẤT của chủ đề)")
    ap.add_argument("--tat-ca", action="store_true", help="mọi chủ đề ĐÃ có nhóm EndNote — bản dashboard mới nhất")
    ap.add_argument("--ap-dung", action="store_true", help="ghi thật vào EndNote (mặc định chạy khô)")
    ap.add_argument("--in", dest="in_noi_dung", action="store_true", help="chỉ in nội dung bản ghi (không đụng EndNote)")
    ap.add_argument("--chua-xac-minh", action="store_true", help="cổng liêm chính CHƯA PASS — chân ghi «CHƯA xác minh»")
    ap.add_argument("--im-khi-chua-cau-hinh", action="store_true", help="máy chưa cấu hình/không phải Mac ⇒ ⚪ và mã 0")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    n = nec()
    files = [Path(f) for f in a.file]
    if a.tat_ca:
        dash_goc = n._tim_dash_goc()
        if dash_goc is None:
            print("✗ không thấy EBM-Dashboards/ (bản sao trần?) — dùng --file")
            return MA_KHONG_CHAY
        files += chu_de_moi_nhat(dash_goc, n.nhom_da_ghi())
    if not files:
        ap.print_usage()
        return MA_THAM_SO
    doc = n._nap_doc_data()
    if a.in_noi_dung:
        for f in files:
            data = doc(f)
            if not data:
                print(f"✗ {f.name}: không đọc được khối DATA")
                continue
            tt = trang_thai_phai_sinh(f)
            nd = dung_noi_dung(data, f, xac_minh=tt["xac_minh"] and not a.chua_xac_minh,
                               so_trich_dan=len(n.trich_dinh_danh(data)))
            print(f"── {nd['tieu_de']} ({nd['nam']}) · PDF {tt['pdf'].name if tt['pdf'] else '—'}\n{nd['tom_tat']}\n")
        return MA_OK
    try:
        endnote = mo_endnote(a.ap_dung)
    except n.KhongChayDuoc as e:
        if a.im_khi_chua_cau_hinh:
            print(f"⚪ EndNote: bỏ qua — {e}")
            return MA_OK
        if a.ap_dung:
            print(f"✗ {e}")
            return MA_KHONG_CHAY
        print(f"⚪ {e} — chỉ lập kế hoạch.")
        endnote = None
    if endnote is None and a.ap_dung:
        print("✗ EndNote chưa mở được thư viện — không ghi gì")
        return MA_KHONG_CHAY
    bang = n.nhom_da_ghi()
    ket_qua: list[dict] = []
    for f in files:
        data = doc(f)
        if not data:
            ket_qua.append({"dashboard": f.name, "loi": "không đọc được khối DATA"})
            print(f"✗ {f.name}: không đọc được khối DATA")
            continue
        nhom = bang.get(n.khoa_chu_de(f)) or n.TIEN_TO_NHOM + n.ten_chu_de(data, f)
        try:
            rid, bc = dam_bao_ban_ghi(endnote, f, data, nhom, a.ap_dung, chua_xac_minh=a.chua_xac_minh)
            if rid and a.ap_dung:
                bc["nhom_kq"] = n.xep_vao_nhom(endnote, nhom, [rid], dashboard=f.name)
        except (RuntimeError, OSError) as e:
            bc = {"loi": f"{type(e).__name__}: {e}"[:300], "trang_thai": "loi_ghi"}
        bc["dashboard"] = f.name
        ket_qua.append(bc)
        _in(bc, f)
    if not a.ap_dung:
        print("Chạy khô — chưa ghi gì. Thêm --ap-dung để ghi.")
    if a.json:
        print(json.dumps(ket_qua, ensure_ascii=False, indent=2, default=str))
    return MA_KHONG_CHAY if any(b.get("loi") for b in ket_qua) else MA_OK


if __name__ == "__main__":
    sys.exit(main())
