#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TÓM TẮT THỰC HÀNH TIẾNG VIỆT trong trường Abstract của từng trích dẫn EndNote (13/10/2026).

Bác sĩ yêu cầu: «Với mỗi trích dẫn đưa vào EndNote hãy đảm bảo tải toàn văn, trong phần edit của trích dẫn với mục
Abstract hãy ghi nội dung tiếng Việt tóm tắt trích dẫn đó cho thực hành lâm sàng … giúp tôi mở mỗi trích dẫn có thể
đọc nhanh chứng cứ đó».

NGUYÊN TẮC (không nới bằng cờ):
  • KHÔNG sinh nội dung y khoa mới. Khối tiếng Việt CHÉP các trường của mục dashboard đã qua cổng liêm chính
    (tiêu đề, nguồn, thiết kế, quần thể, PICO, kết quả, mức chứng cứ, khuyến nghị, theo dõi, an toàn, áp dụng tại
    Việt Nam, lưu ý) — rút gọn khoảng trắng được, thêm khẳng định thì không (CHAT-BRIEF-SPEC).
  • Bài chỉ là TÀI LIỆU THAM KHẢO của một mục ⇒ ghi đúng vai đó; KHÔNG gán kết quả/khuyến nghị của nguồn chính
    cho bài tham khảo (gán nhầm = một khẳng định sai về bài).
  • Nhãn giữ đúng nhãn của dashboard: «Nguồn không phân hạng» (gradeLevel 'na') KHÔNG có nghĩa là chứng cứ yếu;
    giá trị lạ ⇒ «chưa rõ», không đoán.
  • Abstract gốc (PubMed/nhà xuất bản) GIỮ NGUYÊN dưới dấu phân cách; chạy lại chỉ thay khối tiếng Việt.
    Khối không mang ngày chạy — chỉ ngày phiên bản dashboard — nên chạy lại khi dashboard không đổi là không ghi gì.
  • Mỗi khối có PMID/DOI + dòng trạng thái toàn văn + «Cần bác sĩ kiểm chứng».
  • Trước lần ghi đầu tiên của một lượt: sao lưu cơ sở dữ liệu thư viện; sao lưu hỏng ⇒ KHÔNG ghi gì.

Gọi qua `tools/nap_endnote_chu_de.py --tom-tat-vi` (riêng) hoặc tự chạy sau mỗi lượt nạp `--ap-dung`.
Cần bác sĩ kiểm chứng."""
from __future__ import annotations

import re
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

MO_DAU = "【TÓM TẮT THỰC HÀNH · tiếng Việt】"
PHAN_CACH = "━━━━━━━━ ABSTRACT GỐC (nguyên văn PubMed/nhà xuất bản) ━━━━━━━━"
CHAN = ("Cần bác sĩ kiểm chứng. Khối này CHÉP nội dung dashboard đã qua cổng liêm chính (EBM Copilot) — không thêm "
        "khẳng định mới; áp dụng cho từng bệnh nhân qua Cổng A của bác sĩ.")
NHAN_GRADE = {"high": "Cao", "mod": "Trung bình", "low": "Thấp", "vlow": "Rất thấp",
              "na": "Nguồn không phân hạng (không dùng thang GRADE — KHÔNG có nghĩa là chứng cứ yếu)"}
NHAN_QD = {"apply": "Áp dụng ngay", "consider": "Cân nhắc chọn lọc", "notyet": "Chưa đủ thay đổi"}
# Hậu tố tệp trong kho toàn văn → nhãn nguồn (cùng quy ước với nap_endnote_chu_de.NGUON_PDF và doc_sau_toan_van).
NGUON_TOAN_VAN = (("_CHR", "phiên Chrome có uỷ quyền của bác sĩ — có bản quyền, chỉ dùng cá nhân"),
                  ("_WTDM", "kênh TDM của nhà xuất bản (Wiley)"),
                  ("_UPW", "Unpaywall — bản truy cập mở"),
                  ("_PMC", "PMC — bản truy cập mở"))
TOI_DA_MUC = 3        # ngữ cảnh «nguồn chính của mục» tối đa mỗi trích dẫn
TOI_DA_THAM_KHAO = 3  # ngữ cảnh «tài liệu tham khảo» tối đa mỗi trích dẫn


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


def _pico(p) -> str:
    if not isinstance(p, dict):
        return ""
    phan = []
    for k in ("P", "I", "C", "O"):
        v = p.get(k)
        if isinstance(v, (list, tuple)):
            v = v[0] if v else ""
        v = _gon(v)
        if v:
            phan.append(f"{k}: {v}")
    return " | ".join(phan)


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

    def khoa_cua(pmid, doi) -> tuple[str | None, str | None, str | None]:
        pmid = pmid if pmid and re.fullmatch(r"\d{1,9}", str(pmid)) else None
        doi = chuan_doi(doi)
        if not pmid and not doi:
            return None, None, None
        if pmid:
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

        for it in data.get("items") or []:
            if not isinstance(it, dict):
                continue
            chung = {"dashboard": dash.name, "ngay": _ngay_dashboard(dash), "chu_de": cau_hoi,
                     "muc": str(it.get("id") or "?"), "tieu_de": _gon(it.get("title"))}
            pm_chinh = _gon(it.get("pmid")) or None
            doi_chinh = it.get("doi")
            them(pm_chinh, doi_chinh, dict(chung, vai="muc", item=it))
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


def trang_thai_toan_van(pmid: str | None, kho: Path | None) -> str:
    if kho is None:
        return "chưa xét (không thấy kho toàn văn)"
    if not pmid:
        return "chưa xét được (trích dẫn không có PMID — kho đặt tên theo PMID)"
    tep = sorted(p.name for p in kho.glob(f"PMID-{pmid}_*") if p.is_file())
    if not tep:
        return ("CHƯA có toàn văn trong kho — cách lấy ghi trong phiếu xác thực của chủ đề "
                "(EBM-Dashboards/derivatives/…_toan-van.md); bài thuê bao cần bác sĩ đăng nhập làn Chrome")
    pdf = [t for t in tep if t.lower().endswith(".pdf")]
    chinh = pdf[0] if pdf else tep[0]
    nguon = next((nh for hau_to, nh in NGUON_TOAN_VAN if hau_to in chinh), "kho toàn văn")
    loai = "PDF" if pdf else ("HTML" if chinh.lower().endswith((".html", ".htm")) else "XML")
    doc_sau = (kho / "doc_sau" / f"PMID-{pmid}.md").is_file()
    return (f"có {loai} toàn văn ({chinh} — {nguon})"
            + (f"; bản đọc sâu máy: toan_van_oa/doc_sau/PMID-{pmid}.md" if doc_sau else ""))


def _dong_chu_de(nc: dict) -> str:
    return (f"▸ Chủ đề: {nc['chu_de']}  [{nc['dashboard']}" + (f" · {nc['ngay']}" if nc["ngay"] else "") + "]"
            + ("  (bản dashboard CŨ — bản mới của chủ đề không còn trích bài này)" if nc.get("ban_cu") else ""))


def _khoi_muc(nc: dict) -> list[str]:
    it = nc["item"]
    dong = [_dong_chu_de(nc),
            f"• Mục: {nc['tieu_de']}"]
    nguon = " · ".join(x for x in (_gon(it.get("source")), _gon(it.get("design")), _gon(it.get("org")),
                                   _gon(it.get("dateVersion"))) if x)
    if nguon:
        dong.append(f"• Nguồn: {nguon}")
    for nhan, gia_tri in (("Quần thể", _gon(it.get("population"))), ("PICO", _pico(it.get("pico")))):
        if gia_tri:
            dong.append(f"• {nhan}: {gia_tri}")
    ket_qua = "; ".join(x for x in (_gon(it.get("effectText")), _hieu_so(it.get("effect"))) if x)
    if ket_qua:
        dong.append(f"• Kết quả chính: {ket_qua}")
    gl = str(it.get("gradeLevel") or "")
    muc_cc = NHAN_GRADE.get(gl, f"chưa rõ (giá trị «{gl}»)" if gl else "chưa ghi")
    gb, gs = _gon(it.get("gradeBy")), _gon(it.get("gradeSource"))
    dong.append(f"• Mức chứng cứ: {muc_cc}" + (f" — {gb}" if gb else "") + (f". Nguồn phân hạng: {gs}" if gs else ""))
    qd = str(it.get("decision") or "")
    nhan_qd = NHAN_QD.get(qd, f"chưa rõ (giá trị «{qd}»)" if qd else "chưa ghi")
    hd = _gon(it.get("action"))
    dong.append(f"• Khuyến nghị cho thực hành: {nhan_qd}" + (f" — {hd}" if hd else ""))
    for nhan, khoa in (("Theo dõi", "monitoring"), ("An toàn", "safety"), ("Áp dụng tại Việt Nam", "vn"),
                       ("Lưu ý", "flag")):
        v = _gon(it.get(khoa))
        if v:
            dong.append(f"• {nhan}: {v}")
    if it.get("replacementNoticePmid") or it.get("replacementNoticeDoi") or it.get("replacesPmid"):
        tb = it.get("replacementNoticePmid") or it.get("replacementNoticeDoi") or "—"
        dong.append(f"• Rút và thay: bài gốc đã bị rút và thay thế (thông báo {tb}) — số liệu theo BẢN ĐÃ THAY.")
    return dong


def _khoi_tham_khao(nc: dict) -> list[str]:
    return [_dong_chu_de(nc),
            f"• Vai trò: TÀI LIỆU THAM KHẢO bổ trợ cho mục «{nc['tieu_de']}» (nguồn chính của mục: {nc['nguon_chinh']}). "
            "Kết quả và khuyến nghị của mục thuộc NGUỒN CHÍNH — không gán cho bài này.",
            f"• Dashboard ghi: {nc['tham_khao']}"]


def khoi_tieng_viet(muc: dict, kho: Path | None) -> str:
    """Khối tiếng Việt cho MỘT trích dẫn (đầu ra của `ngu_canh`)."""
    dinh_danh = " · ".join(x for x in (f"PMID {muc['pmid']}" if muc.get("pmid") else "",
                                       f"DOI {muc['doi']}" if muc.get("doi") else "") if x)
    dong = [MO_DAU, dinh_danh, f"Toàn văn: {trang_thai_toan_van(muc.get('pmid'), kho)}"]
    chinh = [x for x in muc["ngu_canh"] if x["vai"] == "muc"]
    tk = [x for x in muc["ngu_canh"] if x["vai"] == "tham_khao"]
    for nc in chinh[:TOI_DA_MUC]:
        dong += ["", *_khoi_muc(nc)]
    for nc in tk[:TOI_DA_THAM_KHAO]:
        dong += ["", *_khoi_tham_khao(nc)]
    con = max(0, len(chinh) - TOI_DA_MUC) + max(0, len(tk) - TOI_DA_THAM_KHAO)
    if con:
        dong += ["", f"… và {con} ngữ cảnh khác trong các dashboard (xem nhóm «EBM · …» của chủ đề)."]
    dong += ["", CHAN]
    return "\n".join(dong)


def chuan_dong(s: str) -> str:
    """EndNote đổi \\n thành \\r khi lưu — so sánh luôn trên dạng \\n, bỏ khoảng trắng cuối."""
    return (s or "").replace("\r\n", "\n").replace("\r", "\n").strip()


def tach_goc(cu: str) -> str:
    """Abstract GỐC trong trường hiện tại: phần dưới dấu phân cách nếu đã có khối tiếng Việt, nguyên trường nếu chưa."""
    cu = chuan_dong(cu)
    if cu.startswith(MO_DAU):
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
                sao_luu=None) -> dict:
    """Ghi khối tiếng Việt vào trường Abstract của mọi bản ghi khớp (PMID → «Accession Number», rồi DOI).

    Chạy khô (ap_dung=False): chỉ đếm. Bản ghi mà nội dung mới trùng nội dung cũ ⇒ không ghi."""
    ds = ngu_canh(files, doc_data)
    bc: dict = {"trich_dan": len(ds), "co_ban_ghi": 0, "khong_co_ban_ghi": [], "khong_doi": 0,
                "se_ghi": 0, "da_ghi": 0, "loi": [], "sao_luu": None}
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
        moi = ghep_abstract(cu[m], khoi_tieng_viet(v, kho))
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
