#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TÓM TẮT THỰC HÀNH TIẾNG VIỆT trong trường Abstract của từng trích dẫn EndNote (13/10/2026).

Bác sĩ yêu cầu: «Với mỗi trích dẫn đưa vào EndNote hãy đảm bảo tải toàn văn, trong phần edit của trích dẫn với mục
Abstract hãy ghi nội dung tiếng Việt tóm tắt trích dẫn đó cho thực hành lâm sàng … giúp tôi mở mỗi trích dẫn có thể
đọc nhanh chứng cứ đó».

NGUYÊN TẮC (không nới bằng cờ):
  • KHÔNG sinh nội dung y khoa mới. Khối tiếng Việt CHÉP các trường của mục dashboard đã qua cổng liêm chính
    — rút gọn được, thêm khẳng định thì không (CHAT-BRIEF-SPEC).
  • Bản ĐỌC NHANH (bác sĩ yêu cầu 13/10: «ngắn gọn và thể hiện điểm nhấn»): dòng đầu = khuyến nghị · mức chứng cứ ·
    thiết kế; ★ = tiêu đề mục (câu điểm nhấn của dashboard) kèm PICO (đối tượng · can thiệp · so sánh · kết cục, nhãn
    lệch câu hỏi); rồi Kết quả · Thực hành · An toàn · Lưu ý · Tại Việt Nam; «Đặt cạnh» ≤ 3 mục cùng câu hỏi trong chủ đề.
    Rút gọn bằng CHỌN TRƯỜNG, không cắt giữa câu (cắt câu có thể mất mệnh đề điều kiện); trường dài quá trần thì bỏ
    cả trường. Một ngữ cảnh chính (bản dashboard mới nhất); chủ đề khác chỉ nêu tên — khuyến nghị lệch nhau thì ❗.
  • Nhấn mạnh bằng NHÃN IN HOA + biểu tượng màu trong BMP (✅ ⚠️ ⛔ ⏸️ ▶️ ⭐ ❗ ℹ️) — EndNote không ghi được chữ đậm qua
    AppleScript và trường không có màu chữ (đo 13/10, xem chú thích `NHAN_DONG`).
  • Bài chỉ là TÀI LIỆU THAM KHẢO của một mục ⇒ ghi đúng vai đó; KHÔNG gán kết quả/khuyến nghị của nguồn chính
    cho bài tham khảo (gán nhầm = một khẳng định sai về bài). Dashboard không có nội dung riêng cho bài tham khảo ⇒
    «Tóm tắt MÁY» (thiết kế · PICO · kết quả) rút từ ABSTRACT GỐC, lưu ở kho riêng `EBM-Dashboards/tom-tat-abstract-vi.json`
    (ngoài git), nhãn rõ «chưa qua cổng dashboard — không phải khuyến nghị», không mức chứng cứ. Chốt cứng: mọi con số
    trong tóm tắt phải có NGUYÊN VĂN trong abstract gốc của chính bản ghi — lệch một số ⇒ không in tóm tắt đó.
  • Nhãn giữ đúng nhãn của dashboard: «Nguồn không phân hạng» (gradeLevel 'na') KHÔNG có nghĩa là chứng cứ yếu;
    giá trị lạ ⇒ «chưa rõ», không đoán.
  • Abstract gốc (PubMed/nhà xuất bản) GIỮ NGUYÊN dưới dấu phân cách; chạy lại chỉ thay khối tiếng Việt.
    Khối không mang ngày chạy — chỉ ngày phiên bản dashboard — nên chạy lại khi dashboard không đổi là không ghi gì.
  • Mỗi khối có PMID/DOI + dòng trạng thái toàn văn + «Cần bác sĩ kiểm chứng».
  • Trước lần ghi đầu tiên của một lượt: sao lưu cơ sở dữ liệu thư viện; sao lưu hỏng ⇒ KHÔNG ghi gì.

Gọi qua `tools/nap_endnote_chu_de.py --tom-tat-vi` (riêng) hoặc tự chạy sau mỗi lượt nạp `--ap-dung`.
Cần bác sĩ kiểm chứng."""
from __future__ import annotations

import json
import re
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

MO_DAU = "【EBM · ĐỌC NHANH】"
# Dấu mở đầu của MỌI dạng khối đã từng ghi (13/10: bản đầy đủ → bản đọc nhanh). Chạy lại phải nhận ra để THAY khối cũ —
# không nhận ra là coi khối cũ như abstract gốc và lồng khối mới lên trên.
MO_DAU_DA_DUNG = (MO_DAU, "【TÓM TẮT THỰC HÀNH · tiếng Việt】")
PHAN_CACH = "━━━━━━━━ ABSTRACT GỐC (nguyên văn PubMed/nhà xuất bản) ━━━━━━━━"
CHAN = "Cần bác sĩ kiểm chứng · chép từ dashboard đã qua cổng, không thêm khẳng định mới · áp dụng qua Cổng A."
NHAN_GRADE = {"high": "Cao", "mod": "Trung bình", "low": "Thấp", "vlow": "Rất thấp",
              "na": "nguồn không phân hạng (≠ chứng cứ yếu)"}
# TRÌNH BÀY (bác sĩ 13/10: «nội dung cần nhấn mạnh hãy in đậm», «có thể hiện được màu sắc không»). Đo 13/10 trên EndNote
# 2025: `set field` chỉ nhận chữ thường, `set record contents` (XML có <style>) bị bỏ qua, sửa thẳng `text_styles` trong
# sdb.eni kích hoạt trigger dùng hàm/collation riêng của EndNote (nguy cơ hỏng chỉ mục); thanh định dạng của trường không
# có màu chữ. ⇒ Nhấn mạnh bằng NHÃN IN HOA + biểu tượng màu trong mặt phẳng cơ bản (BMP) — EndNote lưu được và hiện có màu
# trên macOS (đã nhìn thật). Ký tự ngoài BMP bị EndNote đổi thành «?» ⇒ mọi nhãn phải nằm trong BMP (có test chốt).
NHAN_QD = {"apply": "✅ ÁP DỤNG NGAY", "consider": "⚠️ CÂN NHẮC CHỌN LỌC", "notyet": "⏸️ CHƯA ĐỦ THAY ĐỔI"}
NHAN_DONG = {"diem_nhan": "⭐", "ket_qua": "▶️ KẾT QUẢ", "action": "✅ THỰC HÀNH", "safety": "⛔ AN TOÀN",
             "flag": "⚠️ LƯU Ý", "vn": "▶️ TẠI VIỆT NAM", "rut": "❌ RÚT VÀ THAY", "dat_canh": "↔️ ĐẶT CẠNH TRONG CHỦ ĐỀ",
             "lech": "❗ KHUYẾN NGHỊ KHÁC NHAU GIỮA CÁC CHỦ ĐỀ", "tham_khao": "ℹ️ TÀI LIỆU THAM KHẢO BỔ TRỢ",
             "may": "ℹ️ TÓM TẮT MÁY TỪ ABSTRACT"}
# Hậu tố tệp trong kho toàn văn → nhãn nguồn ngắn (cùng quy ước với nap_endnote_chu_de.NGUON_PDF).
NGUON_TOAN_VAN = (("_CHR", "bản quyền — dùng cá nhân"), ("_WTDM", "TDM Wiley"), ("_UPW", "truy cập mở"),
                  ("_PMC", "truy cập mở"))
# Bản ĐỌC NHANH (bác sĩ yêu cầu 13/10: «ngắn gọn, thể hiện điểm nhấn»): rút gọn bằng cách CHỌN TRƯỜNG — trường nào in ra thì
# in NGUYÊN VẸN (cắt giữa câu có thể mất mệnh đề điều kiện «ngoài thai kỳ», «nếu không chống chỉ định»). Trường dài quá
# trần thì bỏ cả trường; «Thực hành», «An toàn», «Lưu ý» luôn in nguyên vẹn.
TRAN_KET_QUA = 320
TRAN_VN = 220
TRAN_THAM_KHAO = 220
TOI_DA_CHU_DE_KHAC = 3
# Trích dẫn CHỈ là tài liệu tham khảo (bác sĩ 13/10: «hoàn thiện với các trích dẫn còn lại»): tóm tắt MÁY từ abstract gốc.
TEP_TOM_TAT_ABS = "tom-tat-abstract-vi.json"
NHAN_TOM_TAT = (("thiet_ke", "THIẾT KẾ"), ("P", "P · ĐỐI TƯỢNG"), ("I", "I · CAN THIỆP/PHƠI NHIỄM"), ("C", "C · SO SÁNH"),
                ("O", "O · KẾT CỤC"), ("ket_qua", "KẾT QUẢ"))
CHAN_MAY = ("Cần bác sĩ kiểm chứng · «Tóm tắt MÁY» rút từ abstract gốc bên dưới, chưa qua cổng dashboard, không phải "
            "khuyến nghị · áp dụng qua Cổng A.")
# KHUÔN kho tóm tắt máy (TT-08, 15/10/2026): kho do một phiên Claude soạn tay theo SKILL — khoá sai trước đó bị bỏ IM LẶNG.
# Khoá định danh: «PMID <n>» hoặc «DOI <doi chữ thường>»; trường hợp lệ: đúng các khoá của NHAN_TOM_TAT. `--mau` in khuôn này.
KHOA_TRUONG_TOM_TAT = tuple(k for k, _ in NHAN_TOM_TAT)
# Trường SIÊU DỮ LIỆU của kho (17/10/2026) — hợp lệ nhưng KHÔNG BAO GIỜ in vào EndNote:
#   `soan`   — ai/khi nào/từ nguồn nào soạn mục. 164/165 mục mang trường này từ 13/10 nên trước đó mỗi lượt nạp in hàng loạt
#              «trường lạ soan» — nhiễu che mất lỗi khuôn thật.
#   `bo_qua` — LÝ DO cố ý không tóm tắt máy (13/10: trường Abstract của bản ghi là GHI CHÚ của bác sĩ, không phải abstract
#              PubMed). Mục `bo_qua` không bao giờ in tóm tắt máy và không bị tính «chưa tóm tắt» — trước đó công cụ vẫn mời
#              phiên sau «SOẠN mục» trái với quyết định đã ghi.
TRUONG_SIEU_DU_LIEU = ("soan", "bo_qua")
_KHOA_DINH_DANH = re.compile(r"PMID \d{1,9}|DOI 10\.\d{4,9}/\S+")
MAU_KHO_TOM_TAT = {
    "_about": ("Kho «Tóm tắt MÁY» cho trích dẫn CHỈ là tài liệu tham khảo — phiên Claude soạn từ ABSTRACT GỐC (mọi con số phải có "
               "nguyên văn trong abstract, lệch ⇒ không in). Khoá định danh «PMID <n>» hoặc «DOI <doi chữ thường>»; trường hợp lệ: "
               + ", ".join(KHOA_TRUONG_TOM_TAT) + ". Siêu dữ liệu tuỳ chọn, không bao giờ in: «soan» (ai/khi nào/từ nguồn nào "
               "soạn) và «bo_qua» (LÝ DO cố ý không tóm tắt — vd trường Abstract của bản ghi là ghi chú của bác sĩ; mục bo_qua "
               "không in tóm tắt máy, không tính «chưa tóm tắt», KHÔNG soạn đè). Khoá lạ khác bị báo lỗi, mục không có trường "
               "hợp lệ (và không bo_qua) = «chưa tóm tắt»."),
    "muc": {
        "PMID 12345678": {k: f"<{nhan.lower()} — tiếng Việt, rút từ abstract gốc>" for k, nhan in NHAN_TOM_TAT},
        "DOI 10.1000/vi-du.2026.001": {k: f"<{nhan.lower()}>" for k, nhan in NHAN_TOM_TAT},
    },
}


def _nap():
    """Công cụ nạp EndNote cùng thư mục — nạp theo đường dẫn (tools/ không phải gói Python)."""
    import importlib.util  # noqa: PLC0415
    sp = importlib.util.spec_from_file_location("_nap_endnote_tomtat", Path(__file__).resolve().parent / "nap_endnote_chu_de.py")
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod


_GIU_CHO = {"—", "–", "-", "--", "n/a", "none"}
# EndNote KHÔNG lưu được ký tự ngoài mặt phẳng cơ bản (emoji) — đo 13/10: «🔴» đọc lại thành «?». Đổi sang nhãn chữ
# giữ nghĩa màu cảnh báo của dashboard; ký tự lạ khác ⇒ «◆» (không để EndNote tự đổi thành «?»).
_EMOJI = {"🔴": "●đỏ", "🟥": "●đỏ", "🟠": "●cam", "🟧": "●cam", "🟡": "●vàng", "🟨": "●vàng",
          "🟢": "●xanh", "🟩": "●xanh", "🔵": "●lam", "🛑": "⛔", "👤": "[bác sĩ]", "🤖": "[máy]"}
_NGOAI_BMP = re.compile(r"[\U00010000-\U0010FFFF]")


def _gon(s) -> str:
    """Chuỗi một dòng, gộp khoảng trắng; ô giữ chỗ («—», «N/A») ⇒ rỗng; emoji ngoài mặt phẳng cơ bản ⇒ chữ.
    Không cắt chữ — rút gọn bằng cách bỏ trường, không bằng cách cụt câu."""
    t = re.sub(r"\s+", " ", str(s or "")).strip()
    for e, chu in _EMOJI.items():
        t = t.replace(e, chu)
    t = _NGOAI_BMP.sub("◆", t)
    return "" if t.lower() in _GIU_CHO else t


def _ngay_dashboard(dash: Path) -> str:
    m = re.search(r"_(\d{4})(\d{2})(\d{2})$", dash.stem)
    return f"{m.group(3)}/{m.group(2)}/{m.group(1)}" if m else ""


def _hieu_so(e) -> str:
    """{measure, hr, ci} → «RR 0.84 (KTC 95% 0.74–0.95)». Thiếu số đo/giá trị thì bỏ — không đoán chiều."""
    if not isinstance(e, dict) or not e.get("measure") or e.get("hr") in (None, ""):
        return ""
    ci = _gon(e.get("ci"))
    return f"{_gon(e['measure'])} {e['hr']}" + (f" (KTC 95% {ci})" if ci else "")


def ngu_canh(files: list[Path], doc_data) -> dict[str, dict]:
    """{khoá: {pmid, doi, ngu_canh: [...]}} — khoá «pmid:<n>» hoặc «doi:<doi>».

    Mỗi chủ đề (khoá = tên tệp bỏ đuôi ngày) lấy ngữ cảnh từ phiên bản MỚI NHẤT. Trích dẫn chỉ còn ở phiên bản CŨ hơn
    (bản mới đã bỏ) vẫn nằm trong nhóm EndNote ⇒ vẫn có ngữ cảnh, gắn nhãn «bản dashboard cũ» — không trộn hai bản
    cho cùng một trích dẫn của cùng chủ đề."""
    nap = _nap()
    chuan_doi, khoa_chu_de, sap_xep_phien_ban = nap.chuan_doi, nap.khoa_chu_de, nap.sap_xep_phien_ban
    da_thay: dict[str, set[str]] = {}   # chủ đề → khoá trích dẫn đã có ngữ cảnh từ phiên bản mới hơn
    ra: dict[str, dict] = {}
    tap_khoa: list[set[str]] = []       # mọi tập khoá đang giữ (đổi tên khi gộp khoá «doi:» vào khoá «pmid:»)

    def gop_doi_vao_pmid(doi: str, k_pm: str) -> None:
        """Trích dẫn gặp TRƯỚC chỉ có DOI (khoá «doi:»), gặp SAU kèm PMID ⇒ một khoá «pmid:» (đo 13/10: SELECT là mục chính
        trích theo DOI ở chủ đề CKM, là tham khảo kèm PMID ở chủ đề GLP-1 — hai khoá cùng trỏ một bản ghi EndNote)."""
        cu = ra.pop(f"doi:{doi}", None)
        if cu is None:
            return
        dich = ra.setdefault(k_pm, {"pmid": k_pm.split(":", 1)[1], "doi": doi, "ngu_canh": []})
        dich["doi"] = dich["doi"] or doi
        for ngc in cu["ngu_canh"]:
            if not any(x["dashboard"] == ngc["dashboard"] and x["vai"] == ngc["vai"] and x.get("muc") == ngc.get("muc")
                       for x in dich["ngu_canh"]):
                dich["ngu_canh"].append(ngc)
        for t in tap_khoa:
            if f"doi:{doi}" in t:
                t.discard(f"doi:{doi}")
                t.add(k_pm)

    def khoa_cua(pmid, doi) -> tuple[str | None, str | None, str | None]:
        pmid = pmid if pmid and re.fullmatch(r"\d{1,9}", str(pmid)) else None
        doi = chuan_doi(doi)
        if not pmid and not doi:
            return None, None, None
        if pmid:
            if doi:
                gop_doi_vao_pmid(doi, f"pmid:{pmid}")
            return f"pmid:{pmid}", pmid, doi
        for k, v in ra.items():  # trích dẫn chỉ có DOI có thể đã gặp dưới khoá PMID ở nơi khác
            if v.get("doi") == doi:
                return k, None, doi
        return f"doi:{doi}", None, doi

    for dash in sap_xep_phien_ban([Path(f) for f in files]):
        chu_de = khoa_chu_de(dash)
        ban_cu = chu_de in da_thay
        cua_chu_de = da_thay.setdefault(chu_de, set())
        trong_ban_nay: set[str] = set()
        tap_khoa.extend(x for x in (cua_chu_de, trong_ban_nay) if not any(x is t for t in tap_khoa))
        data = doc_data(dash) or {}
        cau_hoi = _gon((data.get("meta") or {}).get("question")) or dash.stem

        def them(pmid, doi, nc: dict) -> None:
            khoa, pmid, doi = khoa_cua(pmid, doi)
            if not khoa or khoa in cua_chu_de:
                return
            trong_ban_nay.add(khoa)
            muc = ra.setdefault(khoa, {"pmid": pmid, "doi": doi, "ngu_canh": []})
            muc["pmid"] = muc["pmid"] or pmid
            muc["doi"] = muc["doi"] or doi
            if not any(x["dashboard"] == nc["dashboard"] and x["vai"] == nc["vai"] and x.get("muc") == nc.get("muc")
                       for x in muc["ngu_canh"]):
                muc["ngu_canh"].append(dict(nc, ban_cu=ban_cu))

        cac_muc = [x for x in data.get("items") or [] if isinstance(x, dict)]
        for it in cac_muc:
            chung = {"dashboard": dash.name, "ngay": _ngay_dashboard(dash), "chu_de": cau_hoi,
                     "muc": str(it.get("id") or "?"), "tieu_de": _gon(it.get("title"))}
            pm_chinh = _gon(it.get("pmid")) or None
            doi_chinh = it.get("doi")
            them(pm_chinh, doi_chinh, dict(chung, vai="muc", item=it, anh_em=cac_muc))
            for tk in it.get("references") or []:
                tk = str(tk)
                m_pm = re.search(r"PMID[:\s]*(\d{6,9})", tk)
                m_doi = re.search(r"\b(10\.\d{4,9}/[^\s\"<>]+)", tk)
                pm = m_pm.group(1) if m_pm else None
                do = m_doi.group(1) if m_doi else None
                if (pm and pm == pm_chinh) or (not pm and do and chuan_doi(do) == chuan_doi(doi_chinh)):
                    continue  # tham khảo trỏ lại chính nguồn của mục — đã có ngữ cảnh «muc»
                them(pm, do, dict(chung, vai="tham_khao", tham_khao=_gon(tk),
                                  nguon_chinh=f"PMID {pm_chinh}" if pm_chinh else (f"DOI {doi_chinh}" if doi_chinh else "—")))
        cua_chu_de |= trong_ban_nay
    return ra


_DTV = None
_NHAN_DA_PHU = None


def _dtv():
    """`doc_toan_van_co_nguoi` — NGUỒN SỰ THẬT dùng chung về độ phủ toàn văn (`bao_phu_cuc_bo`), nạp một lần."""
    global _DTV
    if _DTV is None:
        import importlib.util  # noqa: PLC0415
        sp = importlib.util.spec_from_file_location("_dtv_tom_tat", Path(__file__).resolve().parent / "doc_toan_van_co_nguoi.py")
        _DTV = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(_DTV)
    return _DTV


def _nhan_da_phu(trang_thai: str) -> str:
    """Nhãn người đọc của một trạng thái ĐÃ PHỦ — dùng chung `toan_van_theo_chu_de.NHAN_DA_PHU` (phiếu ⑦); không nạp được ⇒ mã."""
    global _NHAN_DA_PHU
    if _NHAN_DA_PHU is None:
        try:
            import importlib.util  # noqa: PLC0415
            sp = importlib.util.spec_from_file_location("_tvcd_tom_tat", Path(__file__).resolve().parent / "toan_van_theo_chu_de.py")
            m = importlib.util.module_from_spec(sp)
            sp.loader.exec_module(m)
            _NHAN_DA_PHU = dict(m.NHAN_DA_PHU)
        except Exception:  # noqa: BLE001 — chỉ là nhãn hiển thị
            _NHAN_DA_PHU = {}
    return _NHAN_DA_PHU.get(trang_thai, trang_thai)


def trang_thai_toan_van(pmid: str | None, kho: Path | None) -> str:
    """Dòng «Toàn văn» của khối ĐỌC NHANH — theo NGUỒN SỰ THẬT `doc_toan_van_co_nguoi.bao_phu_cuc_bo` (TT-03, 15/10/2026: trước đó
    glob riêng `PMID-<n>_*` ⇒ trang giới thiệu kho lưu trữ thành «có HTML (truy cập mở)», tệp tạm `.tam-*` thành «có XML», còn bài
    bác sĩ đã đọc trực tiếp lại «CHƯA có»). Chỉ khi ĐÃ PHỦ mới xét tệp — chỉ tệp toàn văn THẬT (tên hợp lệ, HTML qua cổng nội
    dung) — để in loại PDF/HTML/XML."""
    if kho is None:
        return "chưa xét (không thấy kho)"
    if not pmid:
        return "chưa xét (không có PMID)"
    try:
        dtv = _dtv()
        t = dtv.bao_phu_cuc_bo([str(pmid)], kho)[str(pmid)]
    except Exception as e:  # noqa: BLE001 — không nạp/đo được nguồn sự thật ⇒ nói «chưa xét», không sập cả khối ĐỌC NHANH
        return f"chưa xét (không đo được độ phủ toàn văn: {type(e).__name__})"
    if t not in dtv.TRANG_THAI_DA_PHU:
        return "CHƯA có — cách lấy ở phiếu toàn văn của chủ đề (derivatives/…_toan-van.md)"
    tep = sorted(q.name for q in dtv.tep_toan_van_that(kho, str(pmid)))
    if not tep:   # đã đọc qua làn trình duyệt / bác sĩ đã đọc trực tiếp — máy KHÔNG có tệp toàn văn
        doc_sau = (kho / "doc_sau" / f"PMID-{pmid}.md").is_file()
        return _nhan_da_phu(t) + (" · có bản đọc sâu" if doc_sau else "")
    pdf = [x for x in tep if x.lower().endswith(".pdf")]
    chinh = pdf[0] if pdf else tep[0]
    nguon = next((nh for hau_to, nh in NGUON_TOAN_VAN if hau_to in chinh), "kho toàn văn")
    loai = "PDF" if pdf else ("HTML" if chinh.lower().endswith((".html", ".htm")) else "XML")
    doc_sau = (kho / "doc_sau" / f"PMID-{pmid}.md").is_file()
    return f"có {loai} ({nguon})" + (" · có bản đọc sâu" if doc_sau else "")


def _chu_de_ngan(cau_hoi: str) -> str:
    """Nhãn chủ đề ngắn — phần trước « — »/«:» đầu tiên, ≤ 70 ký tự. Đây là NHÃN nhóm, không phải khẳng định y khoa."""
    t = re.split(r"\s[—–]\s|:\s", cau_hoi or "", maxsplit=1)[0].strip() or (cau_hoi or "")
    return t if len(t) <= 70 else t[:69].rstrip() + "…"


def _ngay_so(nc: dict) -> int:
    m = re.search(r"_(\d{8})\.html?$", nc.get("dashboard") or "")
    return int(m.group(1)) if m else 0


def _nhan(bang: dict, gia_tri) -> str:
    g = str(gia_tri or "")
    return bang.get(g, f"chưa rõ («{g}»)" if g else "chưa ghi")


def _dong_nguon_goc(nc: dict) -> str:
    return (f"Chủ đề: {_chu_de_ngan(nc['chu_de'])}" + (f" · {nc['ngay']}" if nc["ngay"] else "")
            + (" (bản dashboard CŨ)" if nc.get("ban_cu") else ""))


NHAN_PICO = (("P", "ĐỐI TƯỢNG"), ("I", "CAN THIỆP/PHƠI NHIỄM"), ("C", "SO SÁNH"), ("O", "KẾT CỤC"))
# Nhãn khớp của từng thành phần PICO so với câu hỏi của chủ đề (trường `pico` của mục dashboard). «match» không in.
NHAN_KHOP = {"mis": " ⚠️ LỆCH câu hỏi của chủ đề", "partial": " (khớp một phần)", "diff": " (khác câu hỏi)",
             "gap": " (khoảng trống)"}
TOI_DA_DAT_CANH = 3
# ĐẶT CẠNH (bác sĩ yêu cầu 13/10: «so sánh với các kết quả khác»): mục KHÁC của cùng dashboard có cùng can thiệp (I) và
# kết cục (O) — máy ghép theo từ khoá PICO, CHỈ đặt cạnh, không phán chiều (luật của dat_canh_chung_cu_moi.py). Bắt buộc
# trùng I: chỉ trùng nhóm so sánh (C, vd «không dùng công cụ») từng ghép nhầm thang điểm suy tim với vắc-xin RSV (đo 13/10).
NGUONG_I, NGUONG_O, NGUONG_I_MANH = 0.25, 0.15, 0.5
_TU_DUNG = {"va", "hoac", "cua", "cho", "voi", "khong", "nhom", "benh", "nhan", "nguoi", "dieu", "tri", "cham", "soc",
            "thuong", "quy", "don", "thuan", "sau", "truoc", "trong", "ngay", "tuan", "thang", "nam", "lieu", "muc",
            "kem", "theo", "duoc", "co", "la", "mot", "cac", "tren", "duoi", "toi", "den", "tu", "khi", "neu", "dung",
            "thuoc", "so", "gia", "chuan", "hon", "it", "nhat", "lon", "nho", "the", "nay", "do", "bi", "can", "giua",
            "ve", "tai", "phat",
            # đơn vị, liều, đường dùng — đo 13/10: «mg» + «tối đa»/«dưới da» (cùng thành «da») ghép nhầm finerenone
            # (FINEARTS-HF) với semaglutide (FLOW); chúng không nói gì về CÂU HỎI nghiên cứu
            "mg", "mcg", "ml", "kg", "ug", "iu", "da", "tiem", "uong", "lan", "moi", "duong", "tinh", "nen", "dai",
            "ngan", "lien", "tuc", "dau", "hang",
            # «ức chế» là từ chung của mọi nhóm thuốc ức chế — từng ghép SGLT2i với DPP-4i (đo 13/10)
            "uc", "che"}


def _pico_tp(it: dict, k: str) -> tuple[str, str]:
    """(nội dung, nhãn khớp) của một thành phần PICO — trường là [nội dung, nhãn] hoặc chuỗi."""
    v = (it.get("pico") or {}).get(k) if isinstance(it.get("pico"), dict) else None
    if isinstance(v, (list, tuple)):
        return _gon(v[0] if v else ""), str(v[1]) if len(v) > 1 else ""
    return _gon(v), ""


def _tu_khoa(s: str) -> set[str]:
    import unicodedata  # noqa: PLC0415
    t = unicodedata.normalize("NFD", (s or "").lower()).replace("đ", "d")
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return {w for w in re.findall(r"[a-z0-9]+", t) if len(w) >= 2 and not w.isdigit() and w not in _TU_DUNG}


_GIU_CHO_PICO = re.compile(r"^\(.*\b(không|chưa)\b.*\)$", re.I)


def _tk_pico(it: dict, k: str) -> set[str]:
    """Từ khoá của một thành phần PICO để GHÉP. Ô giữ chỗ «(không nêu rõ trong abstract)» ⇒ rỗng — đo 13/10: hai mục
    cùng ghi câu giữ chỗ đó bị ghép thành «cùng câu hỏi». Khi HIỂN THỊ vẫn in nguyên câu giữ chỗ (nói thật là thiếu)."""
    nd = _pico_tp(it, k)[0]
    return set() if _GIU_CHO_PICO.match(nd) else _tu_khoa(nd)


def _jac(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0


def _ung_vien_canh(it: dict, anh_em: list[dict]) -> list[tuple[float, dict, bool]]:
    """(điểm, mục, cùng kết cục?) của mục khác cùng dashboard có cùng câu hỏi: trùng I và O, hoặc trùng I rất mạnh
    (khi đó kết cục có thể KHÁC — dòng đặt cạnh phải nói ra, không để người đọc tưởng hai bài đo cùng một thứ)."""
    tk = {k: _tk_pico(it, k) for k in "ICO"}
    ung: list[tuple[float, dict, bool]] = []
    for b in anh_em:
        if b is it or (it.get("pmid") and _gon(b.get("pmid")) == _gon(it.get("pmid"))):
            continue
        si = _jac(tk["I"], _tk_pico(b, "I"))
        so = _jac(tk["O"], _tk_pico(b, "O"))
        if (si >= NGUONG_I and so >= NGUONG_O) or si >= NGUONG_I_MANH:
            ung.append((si + so + 0.3 * _jac(tk["C"], _tk_pico(b, "C")), b, so >= NGUONG_O))
    return ung


def dat_canh(ngu_canh_muc: list[dict]) -> list[tuple[dict, bool]]:
    """Gom ứng viên đặt cạnh từ MỌI chủ đề có trích bài này làm nguồn chính (một bài có thể chỉ có «hàng xóm» cùng
    câu hỏi ở dashboard khác); khử trùng theo PMID/DOI/tiêu đề; tối đa TOI_DA_DAT_CANH, điểm cao trước."""
    tot: dict[str, tuple[float, dict, bool]] = {}
    for ngu in ngu_canh_muc:
        for diem, b, cung_o in _ung_vien_canh(ngu["item"], ngu.get("anh_em") or []):
            khoa = _gon(b.get("pmid")) or _gon(b.get("doi")) or _gon(b.get("title"))
            if khoa not in tot or diem > tot[khoa][0]:
                tot[khoa] = (diem, b, cung_o)
    return [(b, cung_o) for _, b, cung_o in sorted(tot.values(), key=lambda x: -x[0])[:TOI_DA_DAT_CANH]]


def _dong_dat_canh(b: dict, cung_o: bool = True) -> str:
    dd = f"PMID {_gon(b.get('pmid'))}" if _gon(b.get("pmid")) else (f"DOI {_gon(b.get('doi'))}" if b.get("doi") else "")
    phu = " · ".join(x for x in (dd, _nhan(NHAN_QD, b.get("decision")), f"chứng cứ: {_nhan(NHAN_GRADE, b.get('gradeLevel'))}",
                                 _hieu_so(b.get("effect"))) if x)
    o = _pico_tp(b, "O")[0]
    return f"   – {_gon(b.get('title'))} [{phu}]" + ("" if cung_o or not o else f" — kết cục khác: {o}")


def _khoi_muc(nc: dict, khac: list[dict], so_tham_khao: int) -> list[str]:
    it = nc["item"]
    thiet_ke = " ".join(x for x in (_gon(it.get("design")), _gon(it.get("dateVersion"))) if x)
    dong = [f"{MO_DAU} {_nhan(NHAN_QD, it.get('decision'))} · Chứng cứ: {_nhan(NHAN_GRADE, it.get('gradeLevel'))}"
            + (f" · {thiet_ke}" if thiet_ke else ""),
            f"{NHAN_DONG['diem_nhan']} {nc['tieu_de']}"]
    for k, nhan in NHAN_PICO:
        nd, khop = _pico_tp(it, k)
        if k == "P" and not nd:
            nd = _gon(it.get("population"))
        if nd:
            dong.append(f"   {k} · {nhan}: {nd}{NHAN_KHOP.get(khop, '')}")
    et = _gon(it.get("effectText"))
    ket_qua = "; ".join(x for x in (et if len(et) <= TRAN_KET_QUA else "", _hieu_so(it.get("effect"))) if x)
    if ket_qua:
        dong.append(f"{NHAN_DONG['ket_qua']}: {ket_qua}")
    for khoa in ("action", "safety", "flag"):
        v = _gon(it.get(khoa))
        if v:
            dong.append(f"{NHAN_DONG[khoa]}: {v}")
    vn = _gon(it.get("vn"))
    if vn and len(vn) <= TRAN_VN:
        dong.append(f"{NHAN_DONG['vn']}: {vn}")
    if it.get("replacementNoticePmid") or it.get("replacementNoticeDoi") or it.get("replacesPmid"):
        tb = it.get("replacementNoticePmid") or it.get("replacementNoticeDoi") or "—"
        dong.append(f"{NHAN_DONG['rut']}: bài gốc đã bị rút và thay thế (thông báo {tb}) — số liệu theo BẢN ĐÃ THAY.")
    canh = dat_canh([nc, *khac])
    if canh:
        dong.append(f"{NHAN_DONG['dat_canh']} (máy ghép theo PICO — chỉ đặt cạnh, không phán chiều):")
        dong += [_dong_dat_canh(b, cung_o) for b, cung_o in canh]
    if khac:
        if any(x["item"].get("decision") != it.get("decision") for x in khac):
            dong.append(f"{NHAN_DONG['lech']} — " + "; ".join(
                f"{_chu_de_ngan(x['chu_de'])}: {_nhan(NHAN_QD, x['item'].get('decision'))}"
                for x in [nc, *khac[:TOI_DA_CHU_DE_KHAC]]))
        else:
            dong.append("▸ Cũng dùng trong: " + "; ".join(_chu_de_ngan(x["chu_de"]) for x in khac[:TOI_DA_CHU_DE_KHAC])
                        + (f" (+{len(khac) - TOI_DA_CHU_DE_KHAC})" if len(khac) > TOI_DA_CHU_DE_KHAC else ""))
    if so_tham_khao:
        dong.append(f"▸ Còn là tài liệu tham khảo cho {so_tham_khao} mục khác")
    dong.append(_dong_nguon_goc(nc))
    return dong


def nap_tom_tat_abstract(dash: Path | None) -> dict[str, dict]:
    """Kho tóm tắt máy `<EBM-Dashboards>/tom-tat-abstract-vi.json` → {«PMID <n>» | «DOI <doi chữ thường>»: {trường}}.
    Vắng tệp ⇒ {}; tệp hỏng/sai khuôn ⇒ ValueError — người gọi báo rõ, không lặng lẽ coi như rỗng."""
    tep = dash / TEP_TOM_TAT_ABS if dash else None
    if tep is None or not tep.is_file():
        return {}
    du_lieu = json.loads(tep.read_text(encoding="utf-8"))
    muc = du_lieu.get("muc") if isinstance(du_lieu, dict) else None
    if not isinstance(muc, dict) or not all(isinstance(v, dict) for v in muc.values()):
        raise ValueError(f"{tep.name}: thiếu khoá «muc» dạng {{định danh: {{trường: nội dung}}}}")
    return muc


def kiem_kho_tom_tat(kho_tt: dict) -> list[str]:
    """Lỗi KHUÔN của kho tóm tắt máy (TT-08, 15/10/2026 — trước đó khoá sai bị bỏ IM LẶNG: `design/population` ⇒ không in, không báo
    thiếu; «thiết kế» có dấu ⇒ mất trường mà không ai biết). Khoá định danh sai dạng / DOI không chữ thường / trường lạ ⇒ một dòng
    lỗi; khuôn đúng: `python3 tools/tom_tat_endnote_vi.py --mau`."""
    loi = []
    for k, v in (kho_tt or {}).items():
        if not _KHOA_DINH_DANH.fullmatch(str(k)):
            loi.append(f"kho tóm tắt máy: khoá «{k}» sai dạng — cần «PMID <n>» hoặc «DOI <doi chữ thường>» (xem --mau)")
            continue
        if str(k).startswith("DOI ") and str(k)[4:] != str(k)[4:].lower():
            loi.append(f"kho tóm tắt máy: khoá «{k}» — DOI phải viết chữ thường (bộ đọc tra «DOI <doi chữ thường>»)")
        la = [f for f in (v or {}) if f not in KHOA_TRUONG_TOM_TAT and f not in TRUONG_SIEU_DU_LIEU]
        if la:
            loi.append(f"kho tóm tắt máy: «{k}» có trường lạ {', '.join(map(str, la))} — trường hợp lệ: "
                       + ", ".join(KHOA_TRUONG_TOM_TAT) + "; siêu dữ liệu (không in): " + ", ".join(TRUONG_SIEU_DU_LIEU)
                       + " (xem --mau)")
        if "bo_qua" in (v or {}) and not _gon(v.get("bo_qua")):
            loi.append(f"kho tóm tắt máy: «{k}» có «bo_qua» rỗng — ghi LÝ DO cố ý không tóm tắt, hoặc bỏ hẳn trường này")
        elif _bo_qua(v) and any(_gon(v.get(f)) for f in KHOA_TRUONG_TOM_TAT):
            loi.append(f"kho tóm tắt máy: «{k}» vừa «bo_qua» vừa có trường tóm tắt — mâu thuẫn; mục bo_qua KHÔNG in tóm tắt "
                       "máy (xoá bo_qua nếu bác sĩ đã đồng ý cho tóm tắt)")
    return loi


_SO = re.compile(r"\d+(?:\.\d+)?")


def _cac_so(s: str) -> set[str]:
    """Các con số trong chuỗi. Chuẩn hoá hai cách viết của abstract: «0·85» (Lancet) → 0.85; «1,234» / «1 234» (phân
    cách hàng nghìn) → 1234. Dấu phẩy thập phân KHÔNG chuẩn hoá — tóm tắt phải chép số đúng như abstract."""
    s = re.sub(r"(?<=\d)[·⋅](?=\d)", ".", s or "")
    s = re.sub(r"(?<=\d)[,    ](?=\d{3}(?!\d))", "", s)
    return set(_SO.findall(s))


def so_khong_khop(tom_tat: dict, goc: str) -> list[str]:
    """Các số có trong tóm tắt máy mà KHÔNG có nguyên văn trong abstract gốc. Rỗng mới được in tóm tắt."""
    co = _cac_so(goc)
    return sorted({x for k, _ in NHAN_TOM_TAT for x in _cac_so(str(tom_tat.get(k) or "")) if x not in co})


def _bo_qua(tt) -> bool:
    """Mục kho mang «bo_qua» có nội dung ⇒ CỐ Ý không tóm tắt máy (xem TRUONG_SIEU_DU_LIEU)."""
    return isinstance(tt, dict) and bool(_gon(tt.get("bo_qua")))


def _muc_kho(muc: dict, kho_tt: dict):
    """Mục kho tóm tắt máy của MỘT trích dẫn: tra «PMID <n>» trước, rồi «DOI <doi chữ thường>»; không có ⇒ None."""
    tt = kho_tt.get(f"PMID {muc['pmid']}") if muc.get("pmid") else None
    if tt is None and muc.get("doi"):
        tt = kho_tt.get(f"DOI {str(muc['doi']).lower()}")
    return tt


def tom_tat_cho(muc: dict, kho_tt: dict, goc: str) -> tuple[dict | None, list[str]]:
    """(tóm tắt máy, số lệch) cho MỘT trích dẫn. Chỉ áp cho trích dẫn KHÔNG là mục chính ở dashboard nào — mục chính
    đã có nội dung qua cổng. Mục kho mang «bo_qua» ⇒ không bao giờ in, kể cả khi lỡ có trường tóm tắt (mâu thuẫn — báo ở
    `kiem_kho_tom_tat`). Có số lệch abstract gốc ⇒ (None, các số lệch): không in."""
    if not kho_tt or any(x["vai"] == "muc" for x in muc["ngu_canh"]):
        return None, []
    tt = _muc_kho(muc, kho_tt)
    if _bo_qua(tt) or not isinstance(tt, dict) or not any(_gon(tt.get(k)) for k in KHOA_TRUONG_TOM_TAT):
        return None, []
    lech = so_khong_khop(tt, goc)
    return (None, lech) if lech else (tt, [])


def _khoi_tham_khao(nc: dict, so_khac: int, tom_tat: dict | None = None) -> list[str]:
    dong = [f"{MO_DAU} {NHAN_DONG['tham_khao']}",
            f"{NHAN_DONG['diem_nhan']} Cho mục «{nc['tieu_de']}» (nguồn chính {nc['nguon_chinh']}) — kết quả và khuyến nghị thuộc NGUỒN CHÍNH, "
            "không gán cho bài này"]
    if tom_tat:
        dong.append(f"{NHAN_DONG['may']} (chưa qua cổng dashboard — không phải khuyến nghị):")
        dong += [f"   {nhan}: {_gon(tom_tat.get(k))}" for k, nhan in NHAN_TOM_TAT if _gon(tom_tat.get(k))]
    if len(nc["tham_khao"]) <= TRAN_THAM_KHAO:
        dong.append(f"▸ Dashboard ghi: {nc['tham_khao']}")
    if so_khac:
        dong.append(f"▸ Cũng là tham khảo cho {so_khac} mục khác")
    dong.append(_dong_nguon_goc(nc))
    return dong


def khoi_tieng_viet(muc: dict, kho: Path | None, tom_tat: dict | None = None) -> str:
    """Khối ĐỌC NHANH cho MỘT trích dẫn (đầu ra của `ngu_canh`): một ngữ cảnh chính — bản dashboard MỚI NHẤT, không
    phải bản cũ — các chủ đề khác chỉ nêu tên; khuyến nghị lệch nhau giữa chủ đề thì nêu rõ ❗. `tom_tat` (đã qua
    `tom_tat_cho`) chỉ in cho bài CHỈ là tài liệu tham khảo, và đổi dòng chân cho đúng nguồn gốc nội dung."""
    xep = sorted(muc["ngu_canh"], key=lambda x: (bool(x.get("ban_cu")), -_ngay_so(x)))
    chinh = [x for x in xep if x["vai"] == "muc"]
    tk = [x for x in xep if x["vai"] == "tham_khao"]
    may = None if chinh else tom_tat
    dong = _khoi_muc(chinh[0], chinh[1:], len(tk)) if chinh else _khoi_tham_khao(tk[0], len(tk) - 1, may)
    dinh_danh = f"PMID {muc['pmid']}" if muc.get("pmid") else f"DOI {muc.get('doi')}"
    dong += [f"{dinh_danh} · Toàn văn: {trang_thai_toan_van(muc.get('pmid'), kho)}", CHAN_MAY if may else CHAN]
    return "\n".join(dong)


def chuan_dong(s: str) -> str:
    """EndNote đổi \\n thành \\r khi lưu — so sánh luôn trên dạng \\n, bỏ khoảng trắng cuối."""
    return (s or "").replace("\r\n", "\n").replace("\r", "\n").strip()


def tach_goc(cu: str) -> str:
    """Abstract GỐC trong trường hiện tại: phần dưới dấu phân cách nếu đã có khối tiếng Việt, nguyên trường nếu chưa."""
    cu = chuan_dong(cu)
    if cu.startswith(MO_DAU_DA_DUNG):
        _, co, sau = cu.partition(PHAN_CACH)
        return sau.strip() if co else ""
    return cu


def ghep_abstract(cu: str, khoi: str) -> str:
    goc = tach_goc(cu)
    return f"{khoi}\n\n{PHAN_CACH}\n{goc}" if goc else f"{khoi}\n\n{PHAN_CACH}\n(PubMed không có abstract cho bài này)"


def sao_luu_thu_vien(thu_vien: Path, dich: Path | None = None) -> Path:
    """Sao lưu NHẤT QUÁN cơ sở dữ liệu làm việc (`<thư viện>.Data/sdb/sdb.eni`, đọc được khi EndNote đang mở) + chép
    tệp `.enl`. Trả thư mục sao lưu. Lỗi ⇒ ném — người gọi KHÔNG được ghi gì khi chưa sao lưu được."""
    sdb = thu_vien.with_suffix(".Data") / "sdb" / "sdb.eni"
    if not sdb.is_file():
        raise OSError(f"không thấy cơ sở dữ liệu làm việc {sdb}")
    goc = dich or (Path.home() / ".ebm-endnote-sao-luu")
    thu_muc = goc / f"{thu_vien.stem}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    thu_muc.mkdir(parents=True, exist_ok=False)
    nguon = sqlite3.connect(f"file:{sdb}?mode=ro", uri=True)
    dich_db = sqlite3.connect(thu_muc / "sdb.eni")
    try:
        nguon.backup(dich_db)
    finally:
        dich_db.close()
        nguon.close()
    if (thu_muc / "sdb.eni").stat().st_size < 4096:
        raise OSError("bản sao lưu sdb.eni rỗng bất thường")
    shutil.copy2(thu_vien, thu_muc / thu_vien.name)
    return thu_muc


def ghi_tom_tat(endnote, files: list[Path], *, kho: Path | None, ap_dung: bool, doc_data,
                sao_luu=None, tom_tat_abs: dict | None = None, boi_canh: list[Path] | None = None) -> dict:
    """Ghi khối tiếng Việt vào trường Abstract của mọi bản ghi khớp (PMID → «Accession Number», rồi DOI).

    Chạy khô (ap_dung=False): chỉ đếm. Bản ghi mà nội dung mới trùng nội dung cũ ⇒ không ghi. `tom_tat_abs` = kho
    tóm tắt máy (`nap_tom_tat_abstract`); số lệch abstract gốc của bản ghi ⇒ báo ở `tom_tat_lech_so`, không in;
    trích dẫn chỉ là tham khảo mà kho CHƯA có mục ⇒ `tham_khao_chua_tom_tat` (cần một phiên Claude soạn — máy không tự sinh).

    `boi_canh` = MỌI dashboard của thư mục. Bước ⑧ của dây chuyền chỉ nạp MỘT dashboard; dựng ngữ cảnh chỉ từ nó thì một
    bài là MỤC CHÍNH ở chủ đề khác bị ghi đè bằng khối «tham khảo», mất «Cũng dùng trong»/«Đặt cạnh» (đo 13/10: SELECT).
    Có `boi_canh` ⇒ ngữ cảnh từ toàn bộ, nhưng CHỈ GHI trích dẫn có mặt trong `files`."""
    ds = ngu_canh(sorted({*map(Path, files), *map(Path, boi_canh)}) if boi_canh else files, doc_data)
    if boi_canh:
        ten = {Path(f).name for f in files}
        ds = {k: v for k, v in ds.items() if any(x["dashboard"] in ten for x in v["ngu_canh"])}
    bc: dict = {"trich_dan": len(ds), "co_ban_ghi": 0, "khong_co_ban_ghi": [], "khong_doi": 0,
                "se_ghi": 0, "da_ghi": 0, "loi": kiem_kho_tom_tat(tom_tat_abs or {}), "sao_luu": None, "tom_tat_may": 0,
                "tom_tat_lech_so": [], "tham_khao_chua_tom_tat": [], "tham_khao_bo_qua": []}
    theo_pm = endnote.tim_khop([v["pmid"] for v in ds.values() if v.get("pmid")], "Accession Number")
    con_doi = [v["doi"] for v in ds.values() if v.get("doi") and not theo_pm.get(v.get("pmid") or "")]
    theo_doi = endnote.tim_khop(con_doi, "DOI") if con_doi else {}
    cap: list[tuple[str, dict]] = []
    da_ma: set[str] = set()
    for v in ds.values():
        ma = theo_pm.get(v.get("pmid") or "") or theo_doi.get(v.get("doi") or "") or []
        if not ma:
            bc["khong_co_ban_ghi"].append(f"PMID {v['pmid']}" if v.get("pmid") else f"DOI {v['doi']}")
            continue
        bc["co_ban_ghi"] += 1
        for m in ma:
            if m not in da_ma:
                da_ma.add(m)
                cap.append((m, v))
    cu = endnote.doc_truong([m for m, _ in cap], "Abstract") if cap else {}
    can_ghi: list[tuple[str, str]] = []
    for m, v in cap:
        if m not in cu:
            bc["loi"].append(f"{m}: không đọc được Abstract — bỏ qua (không ghi đè thứ chưa đọc được)")
            continue
        tt, lech = tom_tat_cho(v, tom_tat_abs or {}, tach_goc(cu[m]))
        if lech:
            bc["tom_tat_lech_so"].append(f"{m}: số không có trong abstract gốc ({', '.join(lech[:5])}) — không in tóm tắt máy")
        bc["tom_tat_may"] += bool(tt)
        dinh_danh = f"PMID {v['pmid']}" if v.get("pmid") else f"DOI {v['doi']}"
        # «Chưa tóm tắt» = kho KHÔNG cho ra tóm tắt dùng được (vắng mục, hoặc mục không có trường hợp lệ nào — TT-08), trừ khi
        # mục có mà lệch số (đã báo ở tom_tat_lech_so). Trước đó chỉ xét khoá định danh có mặt ⇒ mục khoá sai lọt khỏi cả hai danh sách.
        # Mục kho «bo_qua» (cố ý không tóm tắt — 17/10/2026) sang danh sách riêng: không mời phiên sau soạn đè quyết định đã ghi.
        if (tom_tat_abs is not None and tt is None and not lech
                and not any(x["vai"] == "muc" for x in v["ngu_canh"])):
            ds_ra = "tham_khao_bo_qua" if _bo_qua(_muc_kho(v, tom_tat_abs)) else "tham_khao_chua_tom_tat"
            if dinh_danh not in bc[ds_ra]:
                bc[ds_ra].append(dinh_danh)
        moi = ghep_abstract(cu[m], khoi_tieng_viet(v, kho, tt))
        if chuan_dong(moi) == chuan_dong(cu[m]):
            bc["khong_doi"] += 1
        else:
            can_ghi.append((m, moi))
    bc["se_ghi"] = len(can_ghi)
    if not ap_dung or not can_ghi:
        return bc
    bc["sao_luu"] = str((sao_luu or (lambda: sao_luu_thu_vien(endnote.thu_vien)))())
    for i in range(0, len(can_ghi), 25):
        for m, loi in endnote.ghi_truong(can_ghi[i:i + 25], "Abstract").items():
            if loi:
                bc["loi"].append(f"{m}: {loi}")
            else:
                bc["da_ghi"] += 1
    return bc


def main(argv: list[str] | None = None) -> int:
    """Cửa dòng lệnh nhỏ (TT-08, 15/10/2026): `--mau` in khuôn kho `tom-tat-abstract-vi.json` cho phiên Claude soạn; `--kiem <tệp>`
    kiểm khuôn một kho đã có (mã 0 đạt · 1 có lỗi khuôn · 2 không đọc được). Ghi vào EndNote đi qua `nap_endnote_chu_de.py`."""
    import argparse  # noqa: PLC0415
    import sys  # noqa: PLC0415
    for _s in (sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Tóm tắt thực hành tiếng Việt cho EndNote — khuôn kho tóm tắt máy")
    nhom = ap.add_mutually_exclusive_group(required=True)
    nhom.add_argument("--mau", action="store_true", help=f"in khuôn JSON hợp lệ của kho {TEP_TOM_TAT_ABS}")
    nhom.add_argument("--kiem", type=Path, metavar="THU_MUC_HOAC_TEP",
                      help=f"kiểm khuôn kho {TEP_TOM_TAT_ABS} (thư mục EBM-Dashboards hoặc chính tệp)")
    a = ap.parse_args(argv)
    if a.mau:
        print(json.dumps(MAU_KHO_TOM_TAT, ensure_ascii=False, indent=2))
        return 0
    thu_muc = a.kiem if a.kiem.is_dir() else a.kiem.parent
    if not (thu_muc / TEP_TOM_TAT_ABS).is_file():
        print(f"⚪ KHÔNG ĐO ĐƯỢC — không thấy {thu_muc / TEP_TOM_TAT_ABS}")
        return 2
    try:
        kho_tt = nap_tom_tat_abstract(thu_muc)
    except (OSError, ValueError) as e:
        print(f"✗ {TEP_TOM_TAT_ABS} không đọc được: {e}")
        return 2
    loi = kiem_kho_tom_tat(kho_tt)
    bo = [k for k, v in kho_tt.items() if _bo_qua(v)]
    rong = [k for k, v in kho_tt.items() if not _bo_qua(v) and not any(_gon(v.get(f)) for f in KHOA_TRUONG_TOM_TAT)]
    for x in loi:
        print(f"✗ {x}")
    for k in rong:
        print(f"🟡 «{k}»: không có trường hợp lệ nào có nội dung — tính là «chưa tóm tắt»")
    print(f"{'✓' if not loi else '✗'} {len(kho_tt)} mục · {len(loi)} lỗi khuôn · {len(rong)} mục rỗng · {len(bo)} mục cố ý "
          "bỏ qua (bo_qua). Cần bác sĩ kiểm chứng.")
    return 1 if loi else 0


if __name__ == "__main__":
    raise SystemExit(main())
