#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NẠP TRÍCH DẪN CỦA MỘT CHỦ ĐỀ VÀO ENDNOTE — mỗi chủ đề một nhóm «EBM · <chủ đề>» (11/10/2026).

Bác sĩ yêu cầu 11/10/2026: mỗi vấn đề cập nhật chứng cứ thì trích dẫn được lưu vào EndNote, mỗi
chủ đề một «thư mục» (nhóm tự tạo — custom group), kèm toàn văn khi có. Bác sĩ chọn thư viện
chính và ghi vào cấu hình RIÊNG MÁY `~/.ebm-endnote.json` (ngoài OneDrive, ngoài git — repo này
công khai, không ghi đường dẫn máy vào mã).

ĐO TRỰC TIẾP trên EndNote 2025 (bản 22.4) ngày 11/10/2026, trên một THƯ VIỆN THỬ NGHIỆM (bản chép
từ bản sao lưu cũ), không đụng thư viện thật:
  • AppleScript `import` nhận chuỗi XML của EndNote (RSXML) — đọc tệp bằng «class utf8» thì dấu
    tiếng Việt và ký tự như «Ș» giữ nguyên.
  • `find` tìm CHUỖI CON trong mọi thư viện đang mở và trả mã bản ghi dạng
    `<RecordID database="N" recNum="M" />` ⇒ phải lọc đúng `database` của thư viện đích và so
    KHỚP NGUYÊN trường (PMID 8 chữ số có thể là chuỗi con của số khác).
  • `post records in … as "<tên>" of type "CUSTOM"` tạo nhóm nếu chưa có. ĐÍNH CHÍNH 24/10/2026 (đo lại trên BẢN SAO thư
    viện, EndNote 22.4.1): post vào tên ĐÃ CÓ nhóm KHÔNG cộng thêm — LUÔN sinh nhóm MỚI cùng tên, kể cả nhóm vừa do post tạo
    trong cùng phiên (171 → +146 → +158; tên mới 159 → +160). Từ điển AppleScript (EndNote.sdef) chỉ gọi nhóm theo TÊN, không
    có lệnh thêm bản ghi vào nhóm đã có ⇒ nhóm đã có thì KHÔNG post: bản ghi thiếu vào HÀNG CHỜ cho bác sĩ kéo tay
    (`--cho-vao-nhom`). Chốt nằm ở `EndNoteMac.dang_vao_nhom` (đo sdb.eni theo group_id trước khi post).
  • `retrieve "all" records in document …` chạy với `document`; lệnh nhóm chạy với `window`.
  • Nhập lại cùng XML tạo bản ghi TRÙNG ⇒ tra PMID («Accession Number») và DOI trước khi nhập.
  • PDF đính NỘI BỘ: `internal-pdf://<số>/<tệp>` trỏ tới `<thư viện>.Data/PDF/<số>/<tệp>` (đúng
    dạng thư viện thật đang dùng); đường dẫn `file://` chỉ là liên kết ngoài, không đồng bộ theo
    tài khoản EndNote.
  • Nhập qua AppleScript KHÔNG kích «Find Full Text» tự động (chờ 45 giây, bài truy cập mở vẫn
    không có PDF); AppleScript của EndNote không có lệnh Find Full Text ⇒ phần toàn văn còn thiếu
    do BÁC SĨ bấm: chọn nhóm → References → Find Full Text (dùng quyền truy cập của chính bác sĩ).
  • `set field "File Attachments" of record … to "internal-pdf://…"` gắn PDF vào bản ghi ĐÃ có
    (bảng `file_res` của thư viện nhận đúng dòng đính kèm nội bộ). Lệnh `close document` làm EndNote
    SẬP (SIGSEGV, đo 11/10) ⇒ công cụ KHÔNG BAO GIỜ đóng thư viện.

Toàn văn đính kèm: CHỈ PDF đã có hợp lệ trong kho chung `EBM-Dashboards/toan_van_oa/` cho đúng PMID
(Unpaywall giấy phép mở · Wiley TDM · bản lưu trong phiên trình duyệt có uỷ quyền của bác sĩ). Công
cụ KHÔNG tải bài thuê bao, KHÔNG đọc nội dung PDF. Metadata lấy lại từ PubMed (efetch) hoặc Crossref
— không chép từ chuỗi tham khảo trong dashboard. Không lấy được metadata ⇒ KHÔNG nhập bản ghi đó.
Toàn văn thường về SAU trích dẫn (gom OA/Unpaywall, Wiley TDM, phiên Chrome uỷ quyền của bác sĩ) ⇒
mỗi lượt `--ap-dung` còn GẮN PDF mới có vào bản ghi của chủ đề CHƯA có tệp đính kèm nào — tệp bác sĩ
đã gắn không bao giờ bị ghi đè — rồi liệt kê bản ghi còn thiếu toàn văn cho làn kế tiếp:
  1. `python3 tools/gom_toan_van_dashboard.py --file <dashboard> --unpaywall`   (bản truy cập mở)
  2. `python3 tools/doc_toan_van_co_nguoi.py --pmid <PMID…>`                     (bài thuê bao: phiếu
     làn Chrome có uỷ quyền — Wiley · ScienceDirect · NEJM · JAMA…; bác sĩ tự đăng nhập/vượt chặn)
  3. `python3 tools/doc_sau_toan_van.py --dashboard <dashboard>`                  (bản đọc sâu)
  4. chạy lại công cụ này với `--ap-dung` ⇒ PDF mới vào đúng nhóm EndNote.

Dùng:
  python3 tools/nap_endnote_chu_de.py --ghi-cau-hinh "<đường dẫn .enl>" [--ung-dung "EndNote 2025"]
  python3 tools/nap_endnote_chu_de.py --file EBM-Dashboards/WebDashboard_X.html            # chạy khô
  python3 tools/nap_endnote_chu_de.py --file EBM-Dashboards/WebDashboard_X.html --ap-dung  # nạp thật
  python3 tools/nap_endnote_chu_de.py --tat-ca [--ap-dung]
  python3 tools/nap_endnote_chu_de.py --file … --xuat-xml ra.xml   # tệp nhập tay (Windows)
  python3 tools/nap_endnote_chu_de.py --file … --tom-tat-vi --ap-dung [--chua-xac-minh]
  python3 tools/nap_endnote_chu_de.py --loai-tru <DOI|PMID> --ly-do "<lý do của bác sĩ>" [--ap-dung]
  python3 tools/nap_endnote_chu_de.py --cho-vao-nhom ["<tên nhóm>"]   # hàng chờ đưa vào nhóm đã có; có tên ⇒ hiện bài trong EndNote
  python3 tools/nap_endnote_chu_de.py --de-tai <mã đề tài> [--ap-dung] [--ten-nhom "NC · …"]
ĐỀ TÀI NGHIÊN CỨU (25/10/2026): `--de-tai <mã>` đọc `medical-ebm-automation/exports/<mã>/DANH_MUC_TRICH_DAN_<mã>.json` (khoá
`trich_dan[]`: id, pmid, doi) thay cho khối DATA của dashboard rồi đi ĐÚNG đường `nap_nhieu` (kiểm trùng, loại trừ, thùng rác,
khoá ghi, nhóm theo group_id, gắn PDF từ kho chung). Nhóm mặc định «NC · <tên đề tài> (<mã>)», khoá chủ đề «DE-TAI_<mã>». KHÔNG
ghi tóm tắt tiếng Việt — bác sĩ dặn 25/10/2026: trích dẫn đề tài không cần tóm tắt chi tiết nhưng phải có toàn văn.
DANH SÁCH LOẠI TRỪ CỦA BÁC SĨ (18/10/2026 — bản ghi bác sĩ đã bỏ vào thùng rác bị bước ⑧ nhập lại mỗi lượt bộ năm): khoá
`bo_qua` của `~/.ebm-endnote.json`, mỗi mục {doi|pmid, ly_do, ngay}. Định danh trong đó KHÔNG nhập, KHÔNG đăng vào nhóm, KHÔNG
gắn PDF/ghi khối tóm tắt — bản ghi khác không bị ảnh hưởng; bản ghi còn nằm trong thư viện chỉ được BÁO (công cụ không xoá).
`bo_qua` sai khuôn = cấu hình HỎNG (không nhập gì, có báo). `--loai-tru` chạy khô mặc định, `--ap-dung` ghi sau khi sao lưu —
agent chỉ ghi khi bác sĩ yêu cầu. Ngoài ra trích dẫn chưa có trong thư viện mà đang nằm trong THÙNG RÁC EndNote cũng không nhập
lại (đọc `sdb.eni` CHỈ-ĐỌC, cột `refs.trash_state`; không đọc được ⇒ ⚪ «chưa đo được thùng rác», không coi là rỗng).
Ngoài macOS: phép kiểm nền tảng đứng TRƯỚC phép kiểm cấu hình — máy không phải Mac được chỉ thẳng sang `--xuat-xml`,
không bị bảo «chạy --ghi-cau-hinh» cho một thư viện công cụ không bao giờ điều khiển được (15/10/2026).
`~/.ebm-endnote.json` HỎNG ≠ VẮNG: hỏng ⇒ ⚪ «tệp cấu hình hỏng — xem <đường dẫn>»; `--ghi-cau-hinh` từ chối ghi đè tệp hỏng
(có thể còn bảng nhom_theo_chu_de cứu tay được) trừ khi có `--xac-nhan-cau-hinh-hong` — khi đó giữ bản `.hong-<ngày giờ>`.
`--chua-xac-minh` (bước ⑧ truyền khi cổng liêm chính CHƯA PASS): khối «EBM · ĐỌC NHANH» ghi dòng «CHƯA xác minh nguồn
sống» và chân khối không nói «đã qua cổng».
Mã thoát: 0 xong · 1 có trích dẫn không lấy được metadata (phần còn lại vẫn nạp) ·
          2 không chạy được (không phải Mac, chưa cấu hình/cấu hình hỏng, thư viện chưa mở/lệch) hoặc NHẬP HỤT (sau lệnh
          nhập, tra lại thư viện vẫn thiếu bài — đo 19/10/2026: cửa sổ Preferences mở làm `import` im lặng) · 3 tham số sai.
Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import html
import http.client
import importlib.util
import json
import os
import re
import secrets
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime
from pathlib import Path
from xml.sax.saxutils import escape

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
# Cấu hình RIÊNG MÁY (ngoài OneDrive, ngoài git). Biến môi trường chỉ để trỏ sang thư viện THỬ NGHIỆM.
CAU_HINH = Path(os.environ.get("EBM_ENDNOTE_CAU_HINH") or (Path.home() / ".ebm-endnote.json"))
UNG_DUNG_MAC_DINH = "EndNote 2025"
TIEN_TO_NHOM = "EBM · "
TIEN_TO_NHOM_DE_TAI = "NC · "  # trích dẫn của một ĐỀ TÀI nghiên cứu (--de-tai, 25/10/2026) — tách khỏi nhóm chứng cứ «EBM · »
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
CROSSREF = "https://api.crossref.org/works/"
LO_EFETCH = 150
# Nguồn của PDF trong kho chung, theo hậu tố tên tệp — thứ tự là thứ tự ƯU TIÊN khi một PMID có nhiều bản.
NGUON_PDF = (
    ("UPW", "Unpaywall — bản mang giấy phép mở"),
    ("WTDM", "Wiley TDM"),
    ("CHR", "bản lưu trong phiên trình duyệt có uỷ quyền của bác sĩ"),
    # 18/10/2026: bản in từ toàn văn XML/HTML ĐÃ QUA CỔNG trong kho (tools/in_pdf_toan_van_kho.py) — ưu tiên THẤP NHẤT: mọi PDF
    # gốc ở trên luôn thắng. Không khớp TEN_TEP_TOAN_VAN nên không được đếm thành một nguồn toàn văn mới.
    ("BANIN", "bản in từ toàn văn XML/HTML đã đọc trong kho"),
)
MA_OK, MA_MOT_PHAN, MA_KHONG_CHAY, MA_THAM_SO = 0, 1, 2, 3
_TEN_UNG_DUNG = re.compile(r"^[\w .\-]{1,60}$")


class KhongChayDuoc(RuntimeError):
    """Không làm được ở máy/trạng thái này (không phải Mac, chưa cấu hình, thư viện chưa mở…)."""


class CauHinhHong(KhongChayDuoc):
    """Tệp cấu hình CÓ MẶT nhưng không dùng được — KHÁC «chưa cấu hình» (TT-09, 15/10/2026)."""


def _la_mac() -> bool:
    """Máy này điều khiển được EndNote bằng AppleScript không. Tách hàm để test giả lập «đang ở Mac» mà không sửa
    `sys.platform` toàn cục (EndNoteMac vẫn tự rào `sys.platform` — lớp phòng thứ hai)."""
    return sys.platform == "darwin"


LENH_XUAT_XML = "python tools/nap_endnote_chu_de.py --file <dashboard> --xuat-xml <tệp>.xml"
THONG_DIEP_KHONG_PHAI_MAC = (
    "tự nhập vào EndNote chỉ chạy trên macOS (AppleScript); máy này dùng --xuat-xml rồi nhập tay: "
    f"`{LENH_XUAT_XML}` → EndNote: File → Import, bộ lọc «EndNote generated XML»")


# ── cấu hình riêng máy ──────────────────────────────────────────────────────────────────────────────

def doc_cau_hinh(tep: Path | None = None) -> dict | None:
    """Cấu hình dùng được, hoặc None (vắng HOẶC hỏng — hợp đồng cũ của mọi nơi gọi). Cần phân biệt hai trường hợp đó
    thì gọi thêm `ly_do_cau_hinh_hong`."""
    try:
        ch = json.loads((tep or CAU_HINH).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    # Cùng điều kiện với `ly_do_cau_hinh_hong`: «thu_vien» phải là CHUỖI khác rỗng (trước đây số 123 lọt qua rồi Path(123) ném
    # TypeError không ai bắt ở main).
    if not isinstance(ch, dict) or not isinstance(ch.get("thu_vien"), str) or not ch.get("thu_vien"):
        return None
    if _loi_loai_tru(ch.get(KHOA_LOAI_TRU)):  # danh sách loại trừ sai khuôn = cấu hình HỎNG (18/10/2026)
        return None
    ch.setdefault("ung_dung", UNG_DUNG_MAC_DINH)
    return ch


# ── danh sách loại trừ do BÁC SĨ khai (18/10/2026) ─────────────────────────────────────────────────
# Sự cố 18/10/2026: bản ghi bác sĩ đã CHỦ Ý bỏ vào thùng rác EndNote bị bước ⑧ nhập lại mỗi lượt bộ năm (công cụ chỉ so với
# bản ghi đang ở thư viện). Khoá `bo_qua` của `~/.ebm-endnote.json` là quyết định của bác sĩ: mỗi mục {doi|pmid, ly_do, ngay}.
KHOA_LOAI_TRU = "bo_qua"
_NGAY_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_PMID_KHUON = re.compile(r"\d{1,9}")


def _loi_loai_tru(bang) -> str | None:
    """Lý do khoá `bo_qua` sai khuôn; None khi vắng hoặc đúng khuôn.

    Định danh nào CÓ MẶT cũng phải đúng khuôn: một DOI gõ sai mà bị lờ đi là âm thầm KHÔNG loại trừ ⇒ coi cả tệp là hỏng
    (cùng hợp đồng TT-09: hỏng phải được nói ra, không nhập gì)."""
    if bang is None:
        return None
    if not isinstance(bang, list):
        return f"khoá «{KHOA_LOAI_TRU}» không phải danh sách"
    for i, muc in enumerate(bang, 1):
        if not isinstance(muc, dict):
            return f"«{KHOA_LOAI_TRU}» mục {i} không phải bảng"
        doi, pmid = muc.get("doi"), muc.get("pmid")
        if doi is None and pmid is None:
            return f"«{KHOA_LOAI_TRU}» mục {i} thiếu «doi»/«pmid»"
        if doi is not None and (not isinstance(doi, str) or chuan_doi(doi) is None):
            return f"«{KHOA_LOAI_TRU}» mục {i}: DOI sai khuôn ({doi!r})"[:160]
        if pmid is not None and (isinstance(pmid, bool) or not isinstance(pmid, (str, int))
                                 or not _PMID_KHUON.fullmatch(str(pmid).strip())):
            return f"«{KHOA_LOAI_TRU}» mục {i}: PMID sai khuôn ({pmid!r})"[:160]
        if not isinstance(muc.get("ly_do"), str) or not muc["ly_do"].strip():
            return f"«{KHOA_LOAI_TRU}» mục {i} thiếu «ly_do»"
        if not isinstance(muc.get("ngay"), str) or not _NGAY_ISO.match(muc["ngay"]):
            return f"«{KHOA_LOAI_TRU}» mục {i} thiếu «ngay» dạng YYYY-MM-DD"
    return None


def doc_loai_tru(tep: Path | None = None) -> dict[str, dict[str, dict]]:
    """{"doi": {doi chuẩn hoá: mục}, "pmid": {pmid: mục}} từ khoá `bo_qua`.

    Tệp vắng ⇒ rỗng (máy chưa khai gì). Tệp HỎNG (kể cả `bo_qua` sai khuôn) ⇒ ném CauHinhHong: người gọi KHÔNG nhập gì —
    không được coi «không đọc được danh sách» là «danh sách rỗng»."""
    hong = ly_do_cau_hinh_hong(tep)
    if hong:
        raise CauHinhHong(f"tệp cấu hình hỏng — xem {tep or CAU_HINH} ({hong}); không đọc được danh sách loại trừ")
    ra: dict[str, dict[str, dict]] = {"doi": {}, "pmid": {}}
    for muc in (doc_cau_hinh(tep) or {}).get(KHOA_LOAI_TRU) or []:
        if muc.get("doi") is not None:
            ra["doi"][chuan_doi(muc["doi"])] = muc
        if muc.get("pmid") is not None:
            ra["pmid"][str(muc["pmid"]).strip()] = muc
    return ra


def muc_loai_tru(loai_tru: dict | None, pmid: str | None, doi: str | None) -> dict | None:
    """Mục loại trừ khớp PMID hoặc DOI (đã chuẩn hoá), hoặc None."""
    if not loai_tru:
        return None
    return ((loai_tru.get("pmid") or {}).get(str(pmid)) if pmid else None) or \
           ((loai_tru.get("doi") or {}).get(chuan_doi(doi)) if doi else None)


def phan_loai_dinh_danh(gia_tri: str) -> tuple[str, str] | None:
    """Chuỗi bác sĩ gõ ở `--loai-tru` → ("doi", doi chuẩn hoá) | ("pmid", số) | None (không đúng khuôn — không đoán)."""
    s = (gia_tri or "").strip()
    s_pm = re.sub(r"^PMID[:\s]*", "", s, flags=re.I)
    if _PMID_KHUON.fullmatch(s_pm):
        return "pmid", s_pm
    doi = chuan_doi(s)
    return ("doi", doi) if doi else None


def them_loai_tru(gia_tri: str, ly_do: str, *, ap_dung: bool, tep: Path | None = None,
                  hom_nay: str | None = None) -> dict:
    """Thêm MỘT định danh vào `bo_qua` (lệnh `--loai-tru`). Chạy khô mặc định; `ap_dung` mới ghi, và chỉ ghi SAU khi chép
    tệp cũ sang `<tên>.sao-luu-<YYYYmmdd-HHMMSS>` (chép hỏng ⇒ không ghi gì).

    Trả {"trang_thai": "se_them" | "da_them" | "da_co", "muc": …, "sao_luu": …}. Ném ValueError (tham số sai) hoặc
    KhongChayDuoc (chưa cấu hình / cấu hình hỏng — không bao giờ ghi vào tệp hỏng)."""
    loai = phan_loai_dinh_danh(gia_tri)
    if loai is None:
        raise ValueError(f"không phải DOI hay PMID đúng khuôn: {gia_tri!r}")
    if not (ly_do or "").strip():
        raise ValueError("thiếu --ly-do (lý do của bác sĩ là bắt buộc)")
    dich = tep or CAU_HINH
    hong = ly_do_cau_hinh_hong(dich)
    if hong:
        raise CauHinhHong(f"tệp cấu hình hỏng — xem {dich} ({hong}); KHÔNG ghi thêm vào tệp hỏng")
    ch = doc_cau_hinh(dich)
    if ch is None:
        raise KhongChayDuoc(f"chưa cấu hình thư viện EndNote ({dich}) — chạy --ghi-cau-hinh \"<đường dẫn .enl>\" trước")
    khoa, gia = loai
    cu = muc_loai_tru(doc_loai_tru(dich), gia if khoa == "pmid" else None, gia if khoa == "doi" else None)
    if cu is not None:
        return {"trang_thai": "da_co", "muc": cu, "sao_luu": None}
    muc = {khoa: gia, "ly_do": ly_do.strip(), "ngay": hom_nay or date.today().isoformat()}
    if not ap_dung:
        return {"trang_thai": "se_them", "muc": muc, "sao_luu": None}
    sao_luu = dich.with_name(f"{dich.name}.sao-luu-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
    if sao_luu.exists():
        sao_luu = sao_luu.with_name(f"{sao_luu.name}-{os.getpid()}")
    try:
        shutil.copy2(dich, sao_luu)
    except OSError as e:
        raise KhongChayDuoc(f"không sao lưu được {dich} sang {sao_luu} ({type(e).__name__}) — không ghi gì") from e
    ch[KHOA_LOAI_TRU] = [*(ch.get(KHOA_LOAI_TRU) or []), muc]
    _ghi_json(dich, ch)
    return {"trang_thai": "da_them", "muc": muc, "sao_luu": str(sao_luu)}


def ly_do_cau_hinh_hong(tep: Path | None = None) -> str | None:
    """Lý do tệp cấu hình CÓ MẶT mà không dùng được; None khi tệp VẮNG hoặc tệp dùng được.

    VÌ SAO (TT-09, 15/10/2026): bản cũ đọc tệp hỏng (cắt cụt, sửa tay lỗi JSON) thành «chưa cấu hình — chạy
    --ghi-cau-hinh», và lệnh đó ghi đè luôn tệp hỏng ⇒ mất khả năng cứu tay bảng `nhom_theo_chu_de` (một chủ đề một
    nhóm EndNote qua mọi phiên bản dashboard). Hỏng ≠ vắng: hỏng phải được NÓI RA, không được xoá âm thầm."""
    p = tep or CAU_HINH
    try:
        tho = p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except (OSError, ValueError) as e:  # UnicodeDecodeError là ValueError
        return f"không đọc được ({type(e).__name__})"
    try:
        ch = json.loads(tho)
    except ValueError as e:
        return f"JSON hỏng ({e})"[:160]
    if not isinstance(ch, dict):
        return "không phải một bảng JSON"
    if not isinstance(ch.get("thu_vien"), str) or not ch.get("thu_vien"):
        return "thiếu khoá «thu_vien»"
    return _loi_loai_tru(ch.get(KHOA_LOAI_TRU))


def ghi_cau_hinh(thu_vien: str, ung_dung: str, tep: Path | None = None, xac_nhan_hong: bool = False) -> dict:
    """Ghi thư viện chính. Tệp cũ HỎNG ⇒ từ chối (CauHinhHong) trừ khi `xac_nhan_hong` — khi đó chép tệp hỏng sang
    `<tên>.hong-<YYYYmmdd-HHMMSS>` TRƯỚC khi ghi (chép hỏng ⇒ không ghi gì). Trả cấu hình đã ghi; có bản giữ lại thì
    kèm khoá `ban_hong` (chỉ trong giá trị trả về, không ghi vào tệp)."""
    p = Path(thu_vien).expanduser()
    if p.suffix.lower() != ".enl" or not p.is_file():
        raise ValueError(f"không thấy thư viện EndNote (.enl): {p}")
    if not _TEN_UNG_DUNG.match(ung_dung):
        raise ValueError(f"tên ứng dụng không hợp lệ: {ung_dung!r}")
    dich = tep or CAU_HINH
    ban_hong = None
    hong = ly_do_cau_hinh_hong(dich)
    if hong:
        if not xac_nhan_hong:
            raise CauHinhHong(
                f"tệp cấu hình {dich} đang HỎNG ({hong}) — KHÔNG ghi đè: tệp có thể còn bảng nhom_theo_chu_de cứu tay "
                "được. Sửa tay tệp đó, hoặc chạy lại kèm --xac-nhan-cau-hinh-hong (giữ bản .hong-<ngày giờ>).")
        ban_hong = dich.with_name(f"{dich.name}.hong-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
        if ban_hong.exists():
            ban_hong = ban_hong.with_name(f"{ban_hong.name}-{os.getpid()}")
        try:
            shutil.copy2(dich, ban_hong)
        except OSError as e:
            raise CauHinhHong(f"không giữ được bản hỏng {ban_hong} ({type(e).__name__}) — không ghi gì") from e
    cu = doc_cau_hinh(dich) or {}
    ch = {"thu_vien": str(p.resolve()), "ung_dung": ung_dung}
    if cu.get("nhom_theo_chu_de") and cu.get("thu_vien") == ch["thu_vien"]:
        ch["nhom_theo_chu_de"] = cu["nhom_theo_chu_de"]  # khai lại cùng thư viện: giữ bảng nhóm đã dựng
    if cu.get(KHOA_LOAI_TRU):
        # Loại trừ là quyết định của bác sĩ về BÀI BÁO, không về thư viện ⇒ giữ cả khi đổi thư viện (18/10/2026).
        ch[KHOA_LOAI_TRU] = cu[KHOA_LOAI_TRU]
    _ghi_json(dich, ch)
    return dict(ch, ban_hong=str(ban_hong)) if ban_hong else ch


def _ghi_json(tep: Path, d: dict) -> None:
    tam = tep.with_name(tep.name + f".tam-{os.getpid()}")
    tam.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    os.replace(tam, tep)


def nhom_da_ghi(tep: Path | None = None) -> dict[str, str]:
    """Bảng {khoá chủ đề: tên nhóm EndNote} của thư viện đã cấu hình — một chủ đề MỘT nhóm qua mọi phiên bản dashboard."""
    bang = (doc_cau_hinh(tep) or {}).get("nhom_theo_chu_de")
    return {str(k): str(v) for k, v in bang.items()} if isinstance(bang, dict) else {}


def ghi_nhom(khoa: str, ten: str, tep: Path | None = None) -> None:
    """Ghi nhớ nhóm của một chủ đề (chỉ khi máy đã cấu hình thư viện)."""
    ch = doc_cau_hinh(tep)
    if ch is None:
        return
    bang = ch.get("nhom_theo_chu_de") if isinstance(ch.get("nhom_theo_chu_de"), dict) else {}
    if bang.get(khoa) == ten:
        return
    bang[khoa] = ten
    ch["nhom_theo_chu_de"] = bang
    _ghi_json(tep or CAU_HINH, ch)


def sap_xep_phien_ban(files: list[Path]) -> list[Path]:
    """Gom các phiên bản cùng chủ đề và đưa bản MỚI NHẤT (đuôi _YYYYMMDD lớn nhất) lên trước — tên nhóm lấy theo bản đó."""
    def ngay(f: Path) -> int:
        m = re.search(r"_(\d{8})$", f.stem)
        return int(m.group(1)) if m else 0   # không có ngày ⇒ coi là cũ nhất
    thu_tu: dict[str, int] = {}
    for f in files:
        thu_tu.setdefault(khoa_chu_de(f), len(thu_tu))
    return sorted(files, key=lambda f: (thu_tu[khoa_chu_de(f)], -ngay(f)))


# ── đọc dashboard ──────────────────────────────────────────────────────────────────────────────────

def _nap_doc_data():
    sp = importlib.util.spec_from_file_location("_kcnn_endnote", ROOT / "tools" / "kiem_cheo_ngu_nghia.py")
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod.doc_data


def ten_chu_de(data: dict, dash: Path) -> str:
    """Tên nhóm: câu hỏi lâm sàng của dashboard, gọn một dòng, ≤ 100 ký tự; không có thì tên tệp."""
    cau_hoi = str(((data or {}).get("meta") or {}).get("question") or "").strip()
    ten = re.sub(r"\s+", " ", cau_hoi) or dash.stem
    return ten if len(ten) <= 100 else ten[:99].rstrip() + "…"


def khoa_chu_de(dash: Path) -> str:
    """Khoá bền qua các phiên bản: tên tệp bỏ tiền tố WebDashboard_ và đuôi ngày _YYYYMMDD."""
    return re.sub(r"_\d{8}$", "", re.sub(r"^WebDashboard_", "", dash.stem))


def chuan_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    d = str(doi).strip()
    d = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", d, flags=re.I)
    d = d.rstrip(".,;)]")
    return d.lower() if re.match(r"^10\.\d{4,9}/\S+$", d) else None


_PMID_THAM_KHAO = re.compile(r"PMID[:\s]*(\d{6,9})")
_DOI_THAM_KHAO = re.compile(r"\b(10\.\d{4,9}/[^\s\"<>]+)")


def trich_dinh_danh(data: dict) -> list[dict]:
    """Mọi trích dẫn của dashboard: định danh chính của từng mục + PMID/DOI ghi rõ trong `references`.

    Khử trùng theo PMID (rồi DOI). Chỉ nhận định danh đúng khuôn — chữ khác bị bỏ, không đoán."""
    ra: list[dict] = []
    da_thay: set[str] = set()

    def them(pmid: str | None, doi: str | None, vai: str, muc: str) -> None:
        pmid = pmid if pmid and re.fullmatch(r"\d{1,9}", pmid) else None
        doi = chuan_doi(doi)
        if not pmid and not doi:
            return
        khoa = f"pmid:{pmid}" if pmid else f"doi:{doi}"
        if khoa in da_thay or (doi and f"doi:{doi}" in da_thay):
            return
        da_thay.add(khoa)
        if doi:
            da_thay.add(f"doi:{doi}")
        ra.append({"pmid": pmid, "doi": doi, "vai": vai, "muc": muc})

    for it in (data or {}).get("items") or []:
        if not isinstance(it, dict):
            continue
        muc = str(it.get("id") or "?")
        them(str(it.get("pmid") or "").strip() or None, it.get("doi"), "muc", muc)
    for it in (data or {}).get("items") or []:
        if not isinstance(it, dict):
            continue
        muc = str(it.get("id") or "?")
        for tk in it.get("references") or []:
            tk = str(tk)
            m_pm = _PMID_THAM_KHAO.search(tk)
            m_doi = _DOI_THAM_KHAO.search(tk)
            them(m_pm.group(1) if m_pm else None, m_doi.group(1) if m_doi else None, "tham_khao", muc)
    return ra


# ── đọc danh mục trích dẫn của một ĐỀ TÀI nghiên cứu (25/10/2026) ──────────────────────────────────

_MA_DE_TAI = re.compile(r"[A-Za-z0-9][A-Za-z0-9._\-]{0,79}")


def _tim_exports() -> Path | None:
    """Thư mục `exports/` của repo y khoa (None ở worktree/bản sao trần) — tách hàm để test thay được."""
    bst_sp = importlib.util.spec_from_file_location("_bst_endnote", ROOT / "tools" / "ban_sao_tran.py")
    bst = importlib.util.module_from_spec(bst_sp)
    bst_sp.loader.exec_module(bst)
    goc = bst.duong_goc("medical-ebm-automation", ROOT)
    return goc / "exports" if goc is not None and (goc / "exports").is_dir() else None


def ten_de_tai(meta: dict | None, ma: str) -> str:
    """Tên nhóm của đề tài (chưa tiền tố): tên đề tài trong study_meta + «(mã)», gọn một dòng ≤ 100 ký tự để mã không bị cắt;
    study_meta không có tên ⇒ chỉ mã."""
    ten = re.sub(r"\s+", " ", str((meta or {}).get("title") or (meta or {}).get("topic") or "")).strip()
    if not ten:
        return ma
    duoi = f" ({ma})"
    toi_da = 100 - len(duoi)
    return (ten if len(ten) <= toi_da else ten[:toi_da - 1].rstrip() + "…") + duoi


def doc_de_tai(ma: str, exports: Path) -> tuple[dict, Path]:
    """`exports/<mã>/DANH_MUC_TRICH_DAN_<mã>.json` (khoá `trich_dan[]`: id, pmid, doi) → (khối giống DATA của dashboard, tên
    tệp GIẢ `DE-TAI_<mã>.json`). Tên giả là KHOÁ CHỦ ĐỀ («DE-TAI_<mã>» trong bảng nhom_theo_chu_de — đúng khoá lượt nạp tay
    25/10/2026 đã ghi nhớ) và nguồn ghi trong ghi chú bản ghi; không ai đọc tệp đó.
    Mã sai khuôn ⇒ ValueError; thiếu tệp / JSON hỏng / sai khuôn / ghi đề tài khác ⇒ KhongChayDuoc (không nạp gì)."""
    if not _MA_DE_TAI.fullmatch(ma or ""):
        raise ValueError(f"mã đề tài sai khuôn: {ma!r} (chữ, số, «.», «_», «-»; ≤ 80 ký tự)")
    thu_muc = exports / ma
    tep = thu_muc / f"DANH_MUC_TRICH_DAN_{ma}.json"
    if not tep.is_file():
        raise KhongChayDuoc(f"không thấy danh mục trích dẫn của đề tài: {tep}")
    try:
        dm = json.loads(tep.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise KhongChayDuoc(f"không đọc được {tep.name}: {type(e).__name__}: {e}"[:300]) from e
    if not isinstance(dm, dict) or not isinstance(dm.get("trich_dan"), list):
        raise KhongChayDuoc(f"{tep.name} sai khuôn — cần khoá «trich_dan» là danh sách")
    if dm.get("study") not in (None, ma):
        raise KhongChayDuoc(f"{tep.name} ghi đề tài {dm.get('study')!r}, không phải {ma!r}")
    try:
        meta = json.loads((thu_muc / "study_meta.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        meta = None  # thiếu tên đề tài chỉ làm tên nhóm mặc định thành mã — không chặn
    items = [{"id": str(d.get("id") or "?"), "pmid": d.get("pmid"), "doi": d.get("doi")}
             for d in dm["trich_dan"] if isinstance(d, dict)]
    data = {"meta": {"question": ten_de_tai(meta if isinstance(meta, dict) else None, ma)}, "items": items}
    return data, Path(f"DE-TAI_{ma}.json")


# ── metadata: PubMed / Crossref ────────────────────────────────────────────────────────────────────

def _email() -> str:
    try:
        sp = importlib.util.spec_from_file_location("_tdd_endnote", ROOT / "tools" / "tra_dinh_danh.py")
        mod = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(mod)
        return mod.email_lien_he()
    except Exception:  # noqa: BLE001 — thiếu email chỉ làm mất «polite pool», không làm hỏng việc
        return ""


def _tai(url: str, lan_thu: int = 3, cho: float = 2.0) -> bytes:
    """GET có thử lại (lỗi mạng, đứt giữa chừng, 429, 5xx). Lỗi 4xx khác thì ném ngay — thử lại vô ích.

    `http.client.HTTPException` (25/10/2026): gói efetch lớn bị ngắt giữa chừng ném `IncompleteRead` — KHÔNG phải lớp con của
    URLError/OSError nên từng lọt ra ngoài làm hỏng cả lượt nạp (đo 25/10: efetch 52 PMID đứt sau 1.160.011 byte)."""
    loi: Exception | None = None
    for i in range(lan_thu):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "EBM-Copilot-EndNote/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504):
                raise
            loi = e
        except (urllib.error.URLError, http.client.HTTPException, TimeoutError, OSError) as e:
            loi = e
        if i < lan_thu - 1:
            time.sleep(cho * (i + 1))
    raise RuntimeError(f"không tải được sau {lan_thu} lần: {loi}")


def _chu(n: ET.Element | None) -> str:
    return re.sub(r"\s+", " ", "".join(n.itertext())).strip() if n is not None else ""


def _nam(s: str) -> str:
    m = re.search(r"(1[89]\d\d|20\d\d)", s or "")
    return m.group(1) if m else ""


def phan_tich_pubmed_xml(du_lieu: bytes) -> dict[str, dict]:
    """XML efetch của PubMed → {pmid: metadata}. Bài báo và tài liệu sách (Bookshelf) đều nhận."""
    goc = ET.fromstring(du_lieu)
    ra: dict[str, dict] = {}
    for bai in goc.findall("PubmedArticle"):
        mc = bai.find("MedlineCitation")
        pmid = _chu(mc.find("PMID")) if mc is not None else ""
        art = mc.find("Article") if mc is not None else None
        if not pmid or art is None:
            continue
        tac_gia = []
        for a in art.findall("AuthorList/Author"):
            if a.find("CollectiveName") is not None:
                tac_gia.append(_chu(a.find("CollectiveName")))
            elif a.find("LastName") is not None:
                ten = _chu(a.find("ForeName")) or _chu(a.find("Initials"))
                tac_gia.append(_chu(a.find("LastName")) + (f", {ten}" if ten else ""))
        ji = art.find("Journal/JournalIssue")
        nam = _chu(ji.find("PubDate/Year")) if ji is not None else ""
        if not nam and ji is not None:
            nam = _nam(_chu(ji.find("PubDate/MedlineDate")))
        tom_tat = []
        for t in art.findall("Abstract/AbstractText"):
            nhan = t.get("Label")
            tom_tat.append((f"{nhan}: " if nhan else "") + _chu(t))
        ids = {i.get("IdType"): _chu(i) for i in bai.findall("PubmedData/ArticleIdList/ArticleId")}
        doi = ids.get("doi") or next((_chu(e) for e in art.findall("ELocationID")
                                       if e.get("EIdType") == "doi"), "")
        loai = [_chu(p) for p in art.findall("PublicationTypeList/PublicationType")]
        ra[pmid] = {
            "pmid": pmid, "doi": chuan_doi(doi), "loai_tl": "Journal Article",
            "tieu_de": _chu(art.find("ArticleTitle")).rstrip(), "tac_gia": [t for t in tac_gia if t],
            "tap_chi": _chu(art.find("Journal/Title")), "tap_chi_viet_tat": _chu(art.find("Journal/ISOAbbreviation")),
            "nam": nam, "tap": _chu(ji.find("Volume")) if ji is not None else "",
            "so": _chu(ji.find("Issue")) if ji is not None else "", "trang": _chu(art.find("Pagination/MedlinePgn")),
            "issn": _chu(art.find("Journal/ISSN")), "tom_tat": "\n".join(x for x in tom_tat if x),
            "ngon_ngu": _chu(art.find("Language")), "pmcid": ids.get("pmc", ""),
            "da_rut": "Retracted Publication" in loai, "nguon_meta": "PubMed",
        }
    for sach in goc.findall("PubmedBookArticle"):
        bd = sach.find("BookDocument")
        pmid = _chu(bd.find("PMID")) if bd is not None else ""
        if not pmid:
            continue
        tac_gia = []
        for a in bd.findall("AuthorList/Author"):
            if a.find("LastName") is not None:
                ten = _chu(a.find("ForeName")) or _chu(a.find("Initials"))
                tac_gia.append(_chu(a.find("LastName")) + (f", {ten}" if ten else ""))
            elif a.find("CollectiveName") is not None:
                tac_gia.append(_chu(a.find("CollectiveName")))
        ids = {i.get("IdType"): _chu(i) for i in sach.findall("PubmedBookData/ArticleIdList/ArticleId")}
        ra[pmid] = {
            "pmid": pmid, "doi": chuan_doi(ids.get("doi")), "loai_tl": "Book Section",
            "tieu_de": _chu(bd.find("ArticleTitle")) or _chu(bd.find("Book/BookTitle")),
            "tac_gia": [t for t in tac_gia if t], "tap_chi": _chu(bd.find("Book/BookTitle")),
            "tap_chi_viet_tat": "", "nam": _nam(_chu(bd.find("Book/PubDate"))), "tap": "", "so": "", "trang": "",
            "issn": "", "nha_xb": _chu(bd.find("Book/Publisher/PublisherName")),
            "tom_tat": "\n".join(_chu(t) for t in bd.findall("Abstract/AbstractText")),
            "ngon_ngu": _chu(bd.find("Language")), "pmcid": "", "da_rut": False, "nguon_meta": "PubMed",
        }
    return ra


class NcbiChan(RuntimeError):
    """NCBI trả trang chặn IP («WWW Error Blocked Diagnostic») — chặn phía máy chủ, thử lại vô ích."""


def la_trang_chan_ncbi(du_lieu: bytes) -> bool:
    dau = du_lieu[:4000].lower()
    return b"blocked diagnostic" in dau or b"blocked for possible abuse" in dau


def lay_pubmed(pmids: list[str], tai=_tai) -> dict[str, dict]:
    ra: dict[str, dict] = {}
    mail = _email()
    for i in range(0, len(pmids), LO_EFETCH):
        lo = pmids[i:i + LO_EFETCH]
        url = (f"{EUTILS}/efetch.fcgi?db=pubmed&retmode=xml&tool=ebm-copilot&id={','.join(lo)}"
               + (f"&email={urllib.parse.quote(mail)}" if mail else ""))
        du_lieu = tai(url)
        if la_trang_chan_ncbi(du_lieu):
            # Đo 11/10/2026: NCBI trả HTTP 200 kèm trang HTML này — không bắt thì ParseError mù mờ.
            raise NcbiChan("NCBI đang chặn IP mạng này (trang «Blocked Diagnostic») — lùi sang Europe PMC")
        ra.update(phan_tich_pubmed_xml(du_lieu))
        if i + LO_EFETCH < len(pmids):
            time.sleep(0.4)  # ≤ 3 lượt/giây khi không có khoá NCBI
    return ra


EUROPEPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
LO_EUROPEPMC = 80
# CHỈ bỏ thẻ THẬT: tên thẻ nằm trong danh sách và theo ngay sau là khoảng trắng, «/» hoặc «>». Đo 13/10/2026 trên 828 PMID
# của 72 dashboard: abstractText/title của Europe PMC chỉ dùng h4 · i · sup · sub · b, và 211 PMID có dấu «<» là CHỮ
# («<140 mm Hg», «P < .001», «<0·05») không mã hoá. Regex cũ `<[^>]+>` coi mọi «<» là đầu thẻ ⇒ xoá từ «<140» tới thẻ
# `<h4>` kế tiếp (INTERACT2 PMID 23713578 còn «target systolic level of Results»). Thẻ lạ ngoài danh sách thì ĐỂ NGUYÊN:
# hiện thừa một thẻ vô hại, xoá nhầm chữ của abstract thì không.
_THE_HTML = re.compile(r"</?(?:h[1-6]|p|br|div|span|i|b|u|em|strong|sup|sub|sc)(?=[\s/>])[^<>]*>", re.I)


def _bo_the_html(s: str) -> str:
    """Bỏ thẻ HTML thật, giải mã thực thể, rồi bỏ thẻ lần nữa: Europe PMC mã hoá KÉP thẻ trong một số tiêu đề
    («&lt;i&gt;Helicobacter pylori&lt;/i&gt;», đo 13/10 — 6/828 PMID). «&lt;140» giải mã thành «<140» là chữ, lượt hai
    không đụng vì không phải tên thẻ trong danh sách."""
    return re.sub(r"\s+", " ", _THE_HTML.sub(" ", html.unescape(_THE_HTML.sub(" ", s or "")))).strip()


def phan_tich_europepmc(js: dict) -> dict[str, dict]:
    """Kết quả `resultType=core` của Europe PMC (nguồn MED) → {pmid: metadata} cùng khuôn với PubMed."""
    ra: dict[str, dict] = {}
    for r in ((js or {}).get("resultList") or {}).get("result") or []:
        pmid = str(r.get("pmid") or "").strip()
        if not pmid or not r.get("title"):
            continue
        tac_gia = []
        for a in ((r.get("authorList") or {}).get("author")) or []:
            if a.get("lastName"):
                ten = a.get("firstName") or a.get("initials") or ""
                tac_gia.append(a["lastName"] + (f", {ten}" if ten else ""))
            elif a.get("collectiveName"):
                tac_gia.append(a["collectiveName"])
        ji = r.get("journalInfo") or {}
        tc = ji.get("journal") or {}
        loai = ((r.get("pubTypeList") or {}).get("pubType")) or []
        ra[pmid] = {
            "pmid": pmid, "doi": chuan_doi(r.get("doi")), "loai_tl": "Journal Article",
            "tieu_de": _bo_the_html(r["title"]), "tac_gia": tac_gia, "tap_chi": tc.get("title") or "",
            "tap_chi_viet_tat": tc.get("isoabbreviation") or tc.get("medlineAbbreviation") or "",
            "nam": str(ji.get("yearOfPublication") or r.get("pubYear") or ""), "tap": ji.get("volume") or "",
            "so": ji.get("issue") or "", "trang": r.get("pageInfo") or "",
            "issn": tc.get("issn") or tc.get("essn") or "",
            "tom_tat": _bo_the_html(r.get("abstractText") or ""), "ngon_ngu": r.get("language") or "",
            "pmcid": r.get("pmcid") or "", "da_rut": "Retracted Publication" in loai,
            "nguon_meta": "Europe PMC",
        }
    return ra


def lay_europepmc(pmids: list[str], tai=_tai) -> dict[str, dict]:
    ra: dict[str, dict] = {}
    for i in range(0, len(pmids), LO_EUROPEPMC):
        lo = pmids[i:i + LO_EUROPEPMC]
        q = f"EXT_ID:({' OR '.join(lo)}) AND SRC:MED"
        url = f"{EUROPEPMC}?query={urllib.parse.quote(q)}&resultType=core&format=json&pageSize={len(lo) + 5}"
        ra.update(phan_tich_europepmc(json.loads(tai(url))))
    return ra


def phan_tich_crossref(js: dict) -> dict | None:
    m = (js or {}).get("message") or {}
    tieu_de = " ".join(m.get("title") or []).strip()
    if not tieu_de:
        return None
    tac_gia = []
    for a in m.get("author") or []:
        if a.get("family"):
            tac_gia.append(a["family"] + (f", {a['given']}" if a.get("given") else ""))
        elif a.get("name"):
            tac_gia.append(a["name"])
    phan = ((m.get("issued") or {}).get("date-parts") or [[None]])[0]
    loai = m.get("type") or ""
    return {
        "pmid": None, "doi": chuan_doi(m.get("DOI")),
        "loai_tl": "Book Section" if loai in ("book-chapter", "book-section") else "Journal Article",
        "tieu_de": tieu_de, "tac_gia": tac_gia, "tap_chi": " ".join(m.get("container-title") or []),
        "tap_chi_viet_tat": " ".join(m.get("short-container-title") or []),
        "nam": str(phan[0]) if phan and phan[0] else "", "tap": m.get("volume") or "", "so": m.get("issue") or "",
        "trang": m.get("page") or "", "issn": (m.get("ISSN") or [""])[0], "tom_tat": "",
        "ngon_ngu": m.get("language") or "", "pmcid": "", "da_rut": False, "nguon_meta": "Crossref",
    }


def lay_crossref(doi: str, tai=_tai) -> dict | None:
    mail = _email()
    url = CROSSREF + urllib.parse.quote(doi, safe="/") + (f"?mailto={urllib.parse.quote(mail)}" if mail else "")
    try:
        return phan_tich_crossref(json.loads(tai(url)))
    except (RuntimeError, urllib.error.HTTPError, ValueError):
        return None


# ── toàn văn có sẵn trong kho chung ────────────────────────────────────────────────────────────────

def chon_pdf(kho: Path | None, pmid: str | None) -> tuple[Path, str] | None:
    """PDF của ĐÚNG PMID này trong kho (PMID-123 không được bắt nhầm PMID-1234…), theo thứ tự ưu tiên."""
    if not kho or not pmid or not kho.is_dir():
        return None
    co: dict[str, Path] = {}
    for p in kho.iterdir():
        m = re.fullmatch(rf"PMID-{re.escape(pmid)}_([A-Za-z]+)\.pdf", p.name, flags=re.I)
        if m and p.is_file():
            co[m.group(1).upper()] = p
    for hau_to, nhan in NGUON_PDF:
        if hau_to in co:
            return co[hau_to], nhan
    return None


def dat_pdf_vao_thu_vien(thu_vien: Path, pdf: Path, pmid: str) -> tuple[str, Path]:
    """Chép PDF vào `<thư viện>.Data/PDF/<số 10 chữ số>/` — đúng chỗ EndNote cất đính kèm nội bộ.
    Trả (url internal-pdf, thư mục vừa tạo) để người gọi dọn nếu bước nhập hỏng."""
    goc = thu_vien.with_suffix(".Data") / "PDF"
    goc.mkdir(parents=True, exist_ok=True)
    for _ in range(50):
        so = str(1_000_000_000 + secrets.randbelow(8_999_999_999))
        thu_muc = goc / so
        if not thu_muc.exists():
            break
    else:  # pragma: no cover — 50 lần trùng liên tiếp gần như không thể
        raise RuntimeError("không chọn được thư mục đính kèm còn trống")
    thu_muc.mkdir()
    ten = f"PMID-{pmid}.pdf"
    shutil.copyfile(pdf, thu_muc / ten)
    return f"internal-pdf://{so}/{ten}", thu_muc


# ── dựng XML nhập của EndNote ──────────────────────────────────────────────────────────────────────

_MA_LOAI = {"Journal Article": 17, "Book Section": 5}


def _the(ten: str, gia_tri: str) -> str:
    return f"<{ten}>{escape(gia_tri)}</{ten}>" if gia_tri else ""


def dung_xml(ban_ghi: list[dict]) -> str:
    """Danh sách metadata (kèm `tu_khoa`, `ghi_chu`, `pdf_url` tuỳ chọn) → chuỗi XML nhập của EndNote."""
    phan = ['<?xml version="1.0" encoding="UTF-8"?><xml><records>']
    for m in ban_ghi:
        loai = m.get("loai_tl") or "Journal Article"
        phan.append(f'<record><ref-type name="{escape(loai)}">{_MA_LOAI.get(loai, 17)}</ref-type>')
        if m.get("tac_gia"):
            phan.append("<contributors><authors>" + "".join(_the("author", a) for a in m["tac_gia"])
                        + "</authors></contributors>")
        phan.append("<titles>" + _the("title", m.get("tieu_de", "")) + _the("secondary-title", m.get("tap_chi", ""))
                    + "</titles>")
        if m.get("tap_chi"):
            phan.append("<periodical>" + _the("full-title", m["tap_chi"])
                        + _the("abbr-1", m.get("tap_chi_viet_tat", "")) + "</periodical>")
        for ten, khoa in (("pages", "trang"), ("volume", "tap"), ("number", "so")):
            phan.append(_the(ten, m.get(khoa, "")))
        if m.get("tu_khoa"):
            phan.append("<keywords>" + "".join(_the("keyword", k) for k in m["tu_khoa"]) + "</keywords>")
        if m.get("nam"):
            phan.append("<dates>" + _the("year", m["nam"]) + "</dates>")
        phan.append(_the("publisher", m.get("nha_xb", "")))
        phan.append(_the("isbn", m.get("issn", "")))
        phan.append(_the("accession-num", m.get("pmid") or ""))
        phan.append(_the("electronic-resource-num", m.get("doi") or ""))
        phan.append(_the("abstract", m.get("tom_tat", "")))
        phan.append(_the("notes", m.get("ghi_chu", "")))
        phan.append(_the("label", m.get("nhan", "")))
        url = (f"https://pubmed.ncbi.nlm.nih.gov/{m['pmid']}/" if m.get("pmid")
               else (f"https://doi.org/{m['doi']}" if m.get("doi") else ""))
        if url or m.get("pdf_url"):
            phan.append("<urls>" + ("<related-urls>" + _the("url", url) + "</related-urls>" if url else "")
                        + ("<pdf-urls>" + _the("url", m["pdf_url"]) + "</pdf-urls>" if m.get("pdf_url") else "")
                        + "</urls>")
        if m.get("nguon_meta") in ("PubMed", "Europe PMC"):
            phan.append(_the("remote-database-name", m["nguon_meta"])
                        + _the("remote-database-provider", "NLM" if m["nguon_meta"] == "PubMed" else "EMBL-EBI"))
        phan.append(_the("language", m.get("ngon_ngu", "")))
        phan.append("</record>")
    phan.append("</records></xml>")
    return "".join(phan)


# ── điều khiển EndNote trên Mac (AppleScript) ──────────────────────────────────────────────────────

# Phép kiểm «đang chạy?/đang mở?» không được treo lượt gọi (công cụ khác gọi giữa chừng, vd phiên Chrome --nhan).
CHO_KIEM_GIAY = 20


def _cung_tep(a: str | os.PathLike, b: str | os.PathLike) -> bool:
    """Hai đường dẫn có trỏ CÙNG một tệp không (DN-03, 15/10/2026).

    Bản cũ so chuỗi `os.path.realpath` — realpath chỉ giải symlink, không gộp hoa/thường hay dạng chuẩn Unicode
    NFC/NFD, trong khi APFS mặc định KHÔNG phân biệt hoa/thường ⇒ cấu hình gõ «documents/…» so với AppleScript trả
    «Documents/…» thành «chưa mở». Nay so ĐỊNH DANH tệp (`os.path.samefile`: thiết bị + inode). Một bên không stat
    được (OSError) ⇒ lùi về so chuỗi đã chuẩn hoá NFC + casefold — chỉ áp khi hệ tệp KHÔNG trả lời được; hai tệp đều
    tồn tại mà khác inode thì không bao giờ «gộp» vì giống chữ."""
    try:
        return os.path.samefile(a, b)
    except (OSError, ValueError):
        def chuan(x) -> str:
            return unicodedata.normalize("NFC", os.path.realpath(x)).casefold()
        return chuan(a) == chuan(b)


def doc_thung_rac(thu_vien: Path) -> dict[str, set[str]]:
    """{"doi": {...}, "pmid": {...}} của bản ghi đang nằm trong THÙNG RÁC của thư viện — CHỈ ĐỌC `<thư viện>.Data/sdb/sdb.eni`.

    ĐO 18/10/2026: từ điển AppleScript của EndNote 2025 (EndNote.sdef) không có lệnh nào cho thùng rác, và `find` không trả bản
    ghi trong thùng rác (vì vậy bản ghi bác sĩ đã bỏ bị nhập lại: recNum 7249 → 7324 → 7327 cùng một DOI). Bảng `refs` có cột
    `trash_state`: 0 = ở thư viện, 1 = trong thùng rác (đo trên BẢN CHÉP nhất quán của thư viện thật: 1956 / 2). Mở
    `mode=ro` giống `tom_tat_endnote_vi.sao_luu_thu_vien` (đọc được khi EndNote đang mở); KHÔNG BAO GIỜ ghi `sdb.eni`.
    Không đọc được (thiếu tệp, lược đồ khác) ⇒ ném OSError/sqlite3.Error — người gọi báo KHÔNG ĐO ĐƯỢC, không coi là «rỗng»."""
    sdb = thu_vien.with_suffix(".Data") / "sdb" / "sdb.eni"
    if not sdb.is_file():
        raise OSError(f"không thấy cơ sở dữ liệu làm việc {sdb}")
    kn = sqlite3.connect(sdb.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        dong = kn.execute("SELECT accession_number, electronic_resource_number FROM refs WHERE trash_state <> 0").fetchall()
    finally:
        kn.close()
    ra: dict[str, set[str]] = {"doi": set(), "pmid": set()}
    for pm, doi in dong:
        pm = str(pm or "").strip()
        if _PMID_KHUON.fullmatch(pm):
            ra["pmid"].add(pm)
        d = chuan_doi(str(doi or ""))
        if d:
            ra["doi"].add(d)
    return ra


_KHOA_GHI = None  # mô-đun khoá ghi, nạp một lần (None = chưa nạp, False = nạp hỏng)
TEN_MO_DUN_KHOA_GHI = "_khoa_ghi_endnote"


def nap_khoa_ghi():
    """Mô-đun khoá ghi `tools/khoa_ghi_endnote.py` — MỘT bản cho cả tiến trình (đăng ký ở `sys.modules`), None khi nạp hỏng.

    VÌ SAO (24/10/2026): trạng thái khoá là biến của mô-đun. Máy chủ MCP mở phạm vi `giu_khoa_ghi` trên bản mô-đun nó nạp;
    lệnh ghi của `EndNoteMac` lấy khoá trên bản `_KHOA_GHI` này. Hai bản `spec_from_file_location` riêng ⇒ phạm vi không thấy
    lần lấy khoá ⇒ không nhả ⇒ khoá kẹt tới HAN_KHOA. Mọi nơi cần khoá gọi hàm này, không tự nạp."""
    global _KHOA_GHI
    if _KHOA_GHI is None:
        try:
            m = sys.modules.get(TEN_MO_DUN_KHOA_GHI)
            if m is None:
                sp = importlib.util.spec_from_file_location(TEN_MO_DUN_KHOA_GHI,
                                                            Path(__file__).resolve().parent / "khoa_ghi_endnote.py")
                m = importlib.util.module_from_spec(sp)
                sp.loader.exec_module(m)
                m = sys.modules.setdefault(TEN_MO_DUN_KHOA_GHI, m)
            _KHOA_GHI = m
        except Exception as e:  # noqa: BLE001
            _KHOA_GHI = False
            print(f"⚠ không nạp được khoá ghi EndNote ({type(e).__name__}) — ghi không qua khoá", file=sys.stderr)
    return _KHOA_GHI or None


def _sk():
    """Mô-đun `tools/endnote_suc_khoe.py` (đọc sdb.eni chỉ-đọc, nhóm theo group_id, hàng chờ đưa vào nhóm) — nạp một lần."""
    m = sys.modules.get("_sk_nap_endnote")
    if m is None:
        sp = importlib.util.spec_from_file_location("_sk_nap_endnote", Path(__file__).resolve().parent / "endnote_suc_khoe.py")
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        m = sys.modules.setdefault("_sk_nap_endnote", m)
    return m


class NhomDaCo(RuntimeError):
    """Tên nhóm đích ĐÃ có nhóm trong thư viện ⇒ không post (post luôn sinh nhóm mới cùng tên — đo 24/10/2026)."""

    def __init__(self, ten_nhom: str, group_id: list[int]):
        super().__init__(f"nhóm «{ten_nhom[:80]}» đã có (group_id {', '.join(map(str, group_id))}) — post sẽ sinh nhóm MỚI cùng "
                         "tên, KHÔNG cộng thêm (đo 24/10/2026) ⇒ không post; bản ghi thiếu vào hàng chờ cho bác sĩ")
        self.ten_nhom, self.group_id = ten_nhom, group_id


class KhongDoDuocNhom(RuntimeError):
    """Không đọc được nhóm trong sdb.eni ⇒ không biết tên đích đã có nhóm chưa ⇒ KHÔNG post (fail-closed)."""


class EndNoteMac:
    """Bọc các lệnh AppleScript đã đo của EndNote. Mọi lệnh đi qua `_chay` (dễ thay khi test).

    KHÔNG BAO GIỜ dùng lệnh `delete record` của EndNote: đo 19/10/2026 trên BẢN SAO thư viện, lệnh này XOÁ HẲN hàng khỏi
    `refs` (không vào thùng rác). Bỏ bản ghi chỉ qua thùng rác do bác sĩ bấm (`tools/chuyen_nhom_vao_thung_rac.py`)."""

    def __init__(self, ung_dung: str, thu_vien: Path) -> None:
        if sys.platform != "darwin":
            raise KhongChayDuoc("tự nhập vào EndNote chỉ chạy trên macOS (AppleScript); "
                                "máy này dùng --xuat-xml rồi nhập tay (File → Import, bộ lọc «EndNote generated XML»)")
        if os.environ.get("PYTEST_CURRENT_TEST") and not os.environ.get("EBM_ENDNOTE_CHO_PHEP_TRONG_TEST"):
            raise KhongChayDuoc("đang chạy dưới pytest — không bao giờ điều khiển EndNote thật")
        if not _TEN_UNG_DUNG.match(ung_dung):
            raise KhongChayDuoc(f"tên ứng dụng không hợp lệ: {ung_dung!r}")
        self.ung_dung = ung_dung
        self.thu_vien = thu_vien
        self.ten = thu_vien.name
        self._csdl: str | None = None

    def _chay(self, than: str, *doi_so: str, cho: int = 600, trong_tell: bool = True) -> str:
        """Chạy một kịch bản AppleScript. `trong_tell=False` ⇒ KHÔNG bọc `tell application` — dùng cho phép kiểm
        «EndNote có đang chạy không» (một sự kiện gửi vào `tell` sẽ KHỞI ĐỘNG ứng dụng đang tắt)."""
        if trong_tell:
            than = f'tell application "{self.ung_dung}"\n{than}\nend tell'
        kich_ban = f"on run argv\n{than}\nend run"
        kq = subprocess.run(["osascript", "-", *doi_so], input=kich_ban, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=cho)
        if kq.returncode != 0:
            raise RuntimeError(f"AppleScript lỗi: {kq.stderr.strip()[:300]}")
        return kq.stdout.rstrip("\n")

    def dang_chay(self) -> bool:
        """EndNote có đang chạy không — KHÔNG gửi sự kiện nào tới EndNote: `application "X" is running` chỉ đọc danh
        sách tiến trình, không khởi động ứng dụng. Lỗi/hết giờ ⇒ False (không biết ⇒ coi như chưa mở, không bật lên)."""
        try:
            return self._chay(f'return application "{self.ung_dung}" is running', cho=CHO_KIEM_GIAY,
                              trong_tell=False).strip().lower() == "true"
        except (RuntimeError, OSError, subprocess.TimeoutExpired):
            return False

    def dang_mo_dung_thu_vien(self) -> bool:
        """Thư viện đích có đang mở trong EndNote không.

        VÁ 15/10/2026 (gap_endnote_running): bản cũ hỏi thẳng `documents` trong `tell application` — với EndNote đang
        TẮT, chính phép kiểm «đã mở chưa» KHỞI ĐỘNG EndNote lên màn hình bác sĩ, phá lời hứa «không tự bật EndNote» của
        --chi-khi-dang-mo (gom --unpaywall, phien_uy_quyen_chrome --nhan). Nay hỏi `is running` trước (không gửi sự
        kiện); và hết giờ (`TimeoutExpired`, trước đây không bị bắt, có thể treo tới 600 giây) ⇒ False sau
        CHO_KIEM_GIAY giây."""
        if not self.dang_chay():
            return False
        try:
            # `POSIX path of (file of d)` báo lỗi -1700 (đo 11/10) — phải ép sang chuỗi HFS trước.
            ds = self._chay('set out to ""\nrepeat with d in documents\n'
                            'set out to out & (POSIX path of ((file of d) as text)) & linefeed\n'
                            'end repeat\nreturn out', cho=CHO_KIEM_GIAY)
        except (RuntimeError, OSError, subprocess.TimeoutExpired):
            return False
        return any(_cung_tep(d.strip(), self.thu_vien) for d in ds.splitlines() if d.strip())

    def ten_cua_so(self) -> list[str]:
        """Tên các cửa sổ EndNote đang mở — CHỈ ĐỌC, để chỉ ra cửa sổ có thể chặn lệnh nhập (vd «EndNote™ Preferences»).
        Lỗi/hết giờ ⇒ [] (không đo được, không kết luận)."""
        try:
            out = self._chay('set AppleScript\'s text item delimiters to linefeed\nreturn (name of every window) as text',
                             cho=CHO_KIEM_GIAY)
        except (RuntimeError, OSError, subprocess.TimeoutExpired):
            return []
        return [x.strip() for x in out.splitlines() if x.strip()]

    def mo_thu_vien(self, cho_giay: int = 40) -> None:
        subprocess.run(["open", "-a", self.ung_dung, str(self.thu_vien)], check=False, capture_output=True)
        het = time.monotonic() + cho_giay
        while time.monotonic() < het:
            if self.dang_mo_dung_thu_vien():
                return
            time.sleep(2)
        raise KhongChayDuoc(f"EndNote chưa mở được thư viện {self.thu_vien} sau {cho_giay} giây")

    def so_csdl(self) -> str:
        if self._csdl is None:
            ids = self._chay('set ids to retrieve "all" records in document (item 1 of argv)\n'
                             'if ids is missing value or (count of ids) is 0 then return ""\n'
                             'return item 1 of ids', self.ten)
            m = re.search(r'database="(\d+)"', ids)
            if not m:
                raise KhongChayDuoc("thư viện đích rỗng — chưa xác định được mã cơ sở dữ liệu của nó")
            self._csdl = m.group(1)
        return self._csdl

    def tim_khop(self, gia_tri: list[str], truong: str) -> dict[str, list[str]]:
        """{giá trị: [mã bản ghi]} — chỉ bản ghi của thư viện đích, trường KHỚP NGUYÊN (không phân biệt hoa/thường)."""
        if not gia_tri:
            return {}
        than = (
            'set db to "database=\\"" & (item 1 of argv) & "\\""\nset truong to item 2 of argv\nset out to ""\n'
            'repeat with i from 3 to count of argv\nset v to item i of argv\nset ids to find v in field truong\n'
            'set khop to ""\nif ids is not missing value then\nrepeat with r in ids\n'
            'if (r as text) contains db then\nif (field truong of record (r as text)) is v then '
            'set khop to khop & tab & (r as text)\nend if\nend repeat\nend if\n'
            'set out to out & v & khop & linefeed\nend repeat\nreturn out')
        ra: dict[str, list[str]] = {}
        for i in range(0, len(gia_tri), 200):
            for dong in self._chay(than, self.so_csdl(), truong, *gia_tri[i:i + 200]).splitlines():
                phan = dong.split("\t")
                if phan and phan[0]:
                    ra[phan[0]] = [x for x in phan[1:] if x]
        return ra

    def _truoc_khi_ghi(self, ly_do: str) -> None:
        """KHOÁ GHI (19/10/2026, `tools/khoa_ghi_endnote.py`): chờ khi bác sĩ đang thao tác trên EndNote, giữ khoá giữa các
        tiến trình Claude, báo một lần «Claude đang ghi EndNote». Bác sĩ vẫn bận quá hạn ⇒ ném lỗi (bỏ lượt ghi, không chen).
        Thiếu mô-đun khoá (cây cũ) ⇒ ghi như trước kèm một dòng cảnh báo — không làm hỏng dây chuyền."""
        kg = nap_khoa_ghi()
        if kg:
            kg.cho_phep_ghi(getattr(self, "ung_dung", "EndNote"), ly_do)

    def nhap(self, tep_xml: Path) -> None:
        self._truoc_khi_ghi("nhập trích dẫn mới")
        self._chay('set x to read (POSIX file (item 1 of argv)) as «class utf8»\n'
                   'import x into document (item 2 of argv)', str(tep_xml), self.ten)

    def thanh_vien_nhom(self, ten_nhom: str) -> list[str]:
        out = self._chay('set ids to get records in (item 1 of argv) of type "CUSTOM" in window (item 2 of argv)\n'
                         'if ids is missing value then return ""\nset AppleScript\'s text item delimiters to tab\n'
                         'return ids as text', ten_nhom, self.ten)
        return [x for x in out.split("\t") if x.strip()]

    def nhom_theo_ten(self, ten_nhom: str) -> list[dict]:
        """Các nhóm mang tên này, TỪNG nhóm theo group_id ({group_id, so_ban_ghi, rec}) — đọc bản sao sdb.eni, không AppleScript
        (`get records in "<tên>"` trả HỢP các nhóm cùng tên). Không đọc được / thành viên không giải được ⇒ KhongDoDuocNhom."""
        try:
            ra = _sk().nhom_theo_ten(self.thu_vien, ten_nhom)
        except (OSError, sqlite3.Error) as e:
            raise KhongDoDuocNhom(f"không đọc được nhóm trong sdb.eni ({type(e).__name__}: {str(e)[:120]})") from e
        hong = [n["group_id"] for n in ra if n.get("loi")]
        if hong:
            raise KhongDoDuocNhom(f"không giải được thành viên nhóm group_id {hong}")
        return ra

    def dang_vao_nhom(self, ids: list[str], ten_nhom: str) -> None:
        """`post` CHỈ khi tên đích CHƯA có nhóm nào (tạo đúng MỘT nhóm — đo 21/10 và 24/10/2026).

        Đo 24/10/2026 trên BẢN SAO thư viện: post vào tên đã có nhóm LUÔN sinh nhóm MỚI cùng tên, kể cả nhóm vừa tạo trong cùng
        phiên EndNote; EndNote.sdef không có lệnh thêm vào nhóm đã có. Nên đo sdb.eni TRƯỚC: đã có ⇒ NhomDaCo, không đo được ⇒
        KhongDoDuocNhom — không post trong cả hai trường hợp (người gọi ghi hàng chờ cho bác sĩ)."""
        if not ids:
            return
        hien = self.nhom_theo_ten(ten_nhom)
        if hien:
            raise NhomDaCo(ten_nhom, [n["group_id"] for n in hien])
        self._truoc_khi_ghi(f"tạo nhóm «{ten_nhom}» với {len(ids)} bản ghi")
        self._chay('set ids to items 3 thru -1 of argv\n'
                   'post records in ids in window (item 2 of argv) as (item 1 of argv) of type "CUSTOM"',
                   ten_nhom, self.ten, *ids)

    def tep_dinh_kem(self, ids: list[str]) -> dict[str, int]:
        """{mã bản ghi: số ký tự trường «File Attachments»} — 0 = chưa gắn tệp nào.
        Chỉ trả ĐỘ DÀI: trường có nhiều tệp ngăn bằng xuống dòng, đọc nguyên văn sẽ vỡ dòng kết quả."""
        ra: dict[str, int] = {}
        than = ('set out to ""\nrepeat with i from 1 to count of argv\nset r to item i of argv\n'
                'set out to out & r & tab & (count of (field "File Attachments" of record r)) & linefeed\n'
                'end repeat\nreturn out')
        for i in range(0, len(ids), 200):
            for dong in self._chay(than, *ids[i:i + 200]).splitlines():
                ma, _, so = dong.rpartition("\t")
                if ma and so.strip().isdigit():
                    ra[ma] = int(so)
        return ra

    def gan_tep(self, ma: str, url: str) -> None:
        """Gắn MỘT tệp vào bản ghi rồi đọc lại — không khớp ⇒ lỗi (không im lặng coi là đã gắn)."""
        self._truoc_khi_ghi("gắn toàn văn vào bản ghi")
        doc_lai = self._chay('set field "File Attachments" of record (item 1 of argv) to (item 2 of argv)\n'
                             'return field "File Attachments" of record (item 1 of argv)', ma, url)
        if doc_lai.strip() != url:
            raise RuntimeError(f"EndNote không nhận tệp đính kèm cho {ma}: đọc lại {doc_lai[:120]!r}")

    def doc_truong(self, ids: list[str], truong: str) -> dict[str, str]:
        """{mã bản ghi: nội dung trường} — ngăn bằng ký tự điều khiển 30/31 vì trường (Abstract) có xuống dòng.
        Bản ghi không có trong kết quả = không đọc được (người gọi KHÔNG được coi là trường rỗng)."""
        ra: dict[str, str] = {}
        than = ('set RS to character id 30\nset US to character id 31\nset out to ""\n'
                'repeat with i from 2 to count of argv\nset r to item i of argv\n'
                'set out to out & r & US & (field (item 1 of argv) of record r) & RS\nend repeat\nreturn out')
        for i in range(0, len(ids), 100):
            for khoi in self._chay(than, truong, *ids[i:i + 100]).split("\x1e"):
                ma, co, gia_tri = khoi.partition("\x1f")
                if co and ma.strip():
                    ra[ma.strip()] = gia_tri
        return ra

    def ghi_truong(self, cap: list[tuple[str, str]], truong: str) -> dict[str, str]:
        """Ghi (mã, nội dung) rồi ĐỌC LẠI từng bản ghi trong cùng lệnh. {mã: ""} = khớp; {mã: lý do} = lỗi.
        EndNote lưu xuống dòng thành \\r — so sánh sau khi chuẩn hoá xuống dòng."""
        def chuan(s: str) -> str:
            return (s or "").replace("\r\n", "\n").replace("\r", "\n").strip()
        than = ('set RS to character id 30\nset f to item 1 of argv\nset out to ""\n'
                'repeat with i from 2 to (count of argv) by 2\nset r to item i of argv\n'
                'set field f of record r to (item (i + 1) of argv)\n'
                'set out to out & (field f of record r) & RS\nend repeat\nreturn out')
        self._truoc_khi_ghi(f"ghi trường «{truong}» cho {len(cap)} bản ghi")
        try:
            doc_lai = self._chay(than, truong, *[x for p in cap for x in p]).split("\x1e")
        except RuntimeError as e:  # lỗi giữa lô: không biết bản nào đã ghi — lượt sau đọc lại và ghi tiếp
            return {ma: f"AppleScript lỗi giữa lô: {e}"[:200] for ma, _ in cap}
        return {ma: ("" if k < len(doc_lai) and chuan(doc_lai[k]) == chuan(gt) else "đọc lại không khớp nội dung vừa ghi")
                for k, (ma, gt) in enumerate(cap)}

    def hien_ban_ghi(self, rec: list[int]) -> None:
        """Đưa EndNote lên trước, CHỈ hiện và tô sáng các bản ghi này (cho bác sĩ ⌘A rồi kéo vào nhóm). Không ghi gì."""
        csdl = self.so_csdl()
        self._chay('activate\nset ids to items 2 thru -1 of argv\nshow records in ids in window (item 1 of argv)\n'
                   'highlight records in ids in window (item 1 of argv)', self.ten,
                   *[f'<RecordID database="{csdl}" recNum="{r}" />' for r in rec])

    def thung_rac(self) -> dict[str, set[str]]:
        """Định danh của bản ghi trong thùng rác (đọc `sdb.eni` chỉ-đọc — AppleScript không có lệnh cho thùng rác)."""
        return doc_thung_rac(self.thu_vien)

    def ten_cac_nhom(self) -> list[str]:
        """Tên mọi nhóm của thư viện, có lặp nếu EndNote giữ hai nhóm cùng tên (ngăn bằng xuống dòng — tên có dấu phẩy)."""
        out = self._chay('set g to get groups in window (item 1 of argv)\nif g is missing value then return ""\n'
                         "set AppleScript's text item delimiters to linefeed\nreturn g as text", self.ten)
        return [x for x in out.splitlines() if x.strip()]


# ── điều phối một chủ đề ───────────────────────────────────────────────────────────────────────────

def lay_metadata(dd: list[dict], lay_pm=lay_pubmed, lay_cr=lay_crossref,
                 lay_ep=lay_europepmc) -> tuple[list[tuple[dict, dict]], list[str]]:
    """[(định danh, metadata)] cho các trích dẫn lấy được; danh sách nhãn của trích dẫn KHÔNG lấy được.

    PubMed trước (theo lô). PubMed lỗi hoặc NCBI chặn IP (gặp thật 11/10/2026 khi VPN bảo trì) ⇒ Europe PMC
    (độc lập NCBI) cho các PMID còn thiếu. Vẫn thiếu mà có DOI ⇒ Crossref, giữ nguyên PMID của dashboard."""
    pmids = [d["pmid"] for d in dd if d.get("pmid")]
    meta_pm: dict[str, dict] = {}
    if pmids:
        try:
            meta_pm = dict(lay_pm(pmids))
        except (RuntimeError, ET.ParseError, OSError):
            meta_pm = {}
        thieu_pm = [p for p in pmids if p not in meta_pm]
        if thieu_pm:
            try:
                meta_pm.update(lay_ep(thieu_pm))
            except (RuntimeError, ValueError, OSError):
                pass
    co: list[tuple[dict, dict]] = []
    thieu: list[str] = []
    for d in dd:
        m = meta_pm.get(d["pmid"]) if d.get("pmid") else None
        if m is None and d.get("doi"):
            m = lay_cr(d["doi"])
            if m is not None and d.get("pmid"):
                m = dict(m, pmid=d["pmid"])
        if m is None:
            thieu.append(f"PMID {d['pmid']}" if d.get("pmid") else f"doi:{d['doi']}")
        else:
            co.append((d, dict(m)))
    return co, thieu


def xet_toan_van(endnote, cap: list[tuple[dict, str]], kho: Path | None) -> tuple[list[tuple], list[str]]:
    """(trích dẫn, mã bản ghi) → ([(mã, PMID, (pdf, nhãn))] cần gắn, [định danh còn thiếu toàn văn]).

    Bản ghi ĐÃ có tệp đính kèm (bác sĩ gắn, Find Full Text, lượt trước) bị bỏ qua — không bao giờ ghi đè.
    Bản ghi không đọc được trường đính kèm cũng bỏ qua: «không đo được» không phải «chưa có»."""
    tep = endnote.tep_dinh_kem([r for _, r in cap]) if cap else {}
    can_gan: list[tuple] = []
    thieu: list[str] = []
    for d, r in cap:
        if tep.get(r) != 0:
            continue
        pdf = chon_pdf(kho, d.get("pmid"))
        if pdf:
            can_gan.append((r, d["pmid"], pdf))
        else:
            thieu.append(f"PMID {d['pmid']}" if d.get("pmid") else f"DOI {d['doi']}")
    return can_gan, thieu


CHO_NHOM_GIAY = 30  # lượt đo lại sdb.eni (mỗi lượt 1 giây) sau khi post tạo nhóm — EndNote ghi xuống đĩa trễ vài giây
_ngu = time.sleep


def cho_nhom_dang_ky(endnote, nhom: str) -> list[dict] | None:
    """Sau khi post TẠO nhóm: đo lại sdb.eni theo group_id tới khi thấy nhóm (≤ CHO_NHOM_GIAY lượt, mỗi lượt 1 giây).

    Trả các nhóm mang tên đó — [] = vẫn chưa thấy (EndNote chưa ghi xuống đĩa), > 1 nhóm ⇒ người gọi báo trùng tên; None = chưa
    lần nào đo được (sdb.eni đổi liên tục/không đọc được) — KHÔNG phải «đã tạo xong».
    Lịch sử: bản 11/10 đợi `get groups` (AppleScript) vì tưởng nhóm «chưa đăng ký» nên lần post sau sinh nhóm thứ hai; đo 24/10
    cho thấy post vào tên đã có LUÔN sinh nhóm mới — đợi không cứu được, nay chỉ post khi chưa có nhóm (`dang_vao_nhom`)."""
    ds: list[dict] | None = None
    for _ in range(CHO_NHOM_GIAY):
        try:
            ds = endnote.nhom_theo_ten(nhom)
        except KhongDoDuocNhom:
            pass  # EndNote đang ghi ngay sau post ⇒ bản sao không ổn định; đo lại lượt sau
        if ds:
            return ds
        _ngu(1)
    return ds


def ghi_cho_vao_nhom(thu_vien: Path, ten_nhom: str, *, them: list[int], da_vao: set[int], group_id: list[int],
                     dashboard: str | None = None, tep: Path | None = None) -> list[int]:
    """Cập nhật HÀNG CHỜ ĐƯA VÀO NHÓM của thư viện (`endnote_suc_khoe.tep_cho_vao_nhom()`): thêm `them`, bỏ bản ghi đã nằm trong
    nhóm (`da_vao` — bác sĩ kéo xong). Trả danh sách recNum còn chờ của nhóm. Không đổi gì ⇒ không ghi tệp.

    Dưới pytest KHÔNG BAO GIỜ ghi tệp mặc định trong thư mục nhà — test phải truyền `tep` hoặc đặt `EBM_ENDNOTE_CHO_VAO_NHOM`
    sang thư mục tạm. Tệp hỏng ⇒ ValueError (không ghi đè: có thể còn bài chờ cứu tay được)."""
    sk = _sk()
    if tep is None and os.environ.get("PYTEST_CURRENT_TEST") and not os.environ.get("EBM_ENDNOTE_CHO_VAO_NHOM"):
        raise KhongChayDuoc(f"đang chạy dưới pytest — không ghi hàng chờ thật {sk.tep_cho_vao_nhom()}")
    tep = Path(tep or sk.tep_cho_vao_nhom())
    d = sk.doc_cho_vao_nhom(tep)
    bang = d["thu_vien"].setdefault(sk.khoa_thu_vien(thu_vien), {})
    ten_nhom = next((t for t in bang if sk.khoa_ten(t) == sk.khoa_ten(ten_nhom)), ten_nhom)  # EndNote gọi nhóm theo tên khoá
    cu = bang.get(ten_nhom) or {}
    rec = sorted({*cu.get("rec", []), *them} - set(da_vao))
    if not cu and not rec:
        return []
    nguon = list(dict.fromkeys([*(cu.get("dashboard") or []), *([dashboard] if dashboard and them else [])]))
    moi = {"rec": rec, "group_id": sorted(group_id), "dashboard": nguon}
    if {k: cu.get(k) for k in moi} == moi:
        return rec
    if rec:
        bang[ten_nhom] = {**moi, "cap_nhat": datetime.now().isoformat(timespec="seconds")}
    else:
        bang.pop(ten_nhom, None)
    if not bang:
        d["thu_vien"].pop(sk.khoa_thu_vien(thu_vien), None)
    _ghi_json(tep, d)
    return rec


def xep_vao_nhom(endnote, nhom: str, ids: list[str], dashboard: str | None = None, tep_cho: Path | None = None,
                 da_tao: set[str] | None = None) -> dict:
    """Đưa bản ghi (`ids`, mã AppleScript) vào nhóm `nhom` mà KHÔNG BAO GIỜ sinh nhóm trùng tên (24/10/2026).

    Đo nhóm trên sdb.eni theo group_id: chưa có nhóm ⇒ post (tạo đúng MỘT nhóm) rồi đo lại; ĐÃ có ⇒ KHÔNG post — bản ghi chưa
    nằm trong nhóm nào cùng tên vào hàng chờ cho bác sĩ kéo tay (`--cho-vao-nhom`), bản ghi bác sĩ đã kéo xong được dọn khỏi
    hàng chờ; không đo được ⇒ KHÔNG post, không ghi hàng chờ (lượt sau đo lại). `da_tao` = khoá tên các nhóm đã post trong
    CÙNG lượt (`nap_nhieu`): nhóm vừa post mà chưa hiện trên sdb.eni thì bản kế tiếp không post lần hai — vào hàng chờ.
    Trả các khoá báo cáo cho `nap_chu_de`."""
    kq: dict = {"dang_vao_nhom": 0}
    if not ids:
        return kq
    khoa = _sk().khoa_ten(nhom)
    cho_dia = False
    try:
        hien = endnote.nhom_theo_ten(nhom)
        cho_dia = not hien and da_tao is not None and khoa in da_tao
        if not hien and not cho_dia:
            endnote.dang_vao_nhom(ids, nhom)
            if da_tao is not None:
                da_tao.add(khoa)
    except KhongDoDuocNhom as e:
        kq["nhom_khong_do_duoc"] = str(e)[:200]
        return kq
    except NhomDaCo:  # nhóm vừa xuất hiện giữa lần đo và lệnh post (phiên khác/bác sĩ) ⇒ đo lại, đi nhánh hàng chờ
        try:
            hien = endnote.nhom_theo_ten(nhom)
        except KhongDoDuocNhom as e:
            kq["nhom_khong_do_duoc"] = str(e)[:200]
            return kq
    if not hien and not cho_dia:
        kq["dang_vao_nhom"] = len(ids)
        sau = cho_nhom_dang_ky(endnote, nhom)
        if sau is None:
            kq["nhom_sau_khong_do_duoc"] = True
        elif not sau:
            kq["nhom_chua_thay"] = True
        else:
            kq["nhom_sau"] = [{"group_id": n["group_id"], "so_ban_ghi": n["so_ban_ghi"]} for n in sau]
            kq["trong_nhom_sau"] = len({r for n in sau for r in n["rec"]})
            if len(sau) > 1:
                kq["nhom_trung_ten"] = len(sau)
            try:  # nhóm được tạo LẠI (bác sĩ đã xoá nhóm cũ) ⇒ dọn bài đã vào nhóm khỏi hàng chờ cũ của tên này
                ghi_cho_vao_nhom(endnote.thu_vien, nhom, them=[], da_vao={r for n in sau for r in n["rec"]},
                                 group_id=[n["group_id"] for n in sau], tep=tep_cho)
            except (ValueError, OSError, KhongChayDuoc):
                pass  # việc dọn phụ — `--cho-vao-nhom` và lượt sau cũng đo lại theo group_id
        return kq
    da_vao = {r for n in hien for r in n["rec"]}
    so = [int(s) for s in (_so_ban_ghi(r) for r in ids) if s.isdigit()]
    thieu = [r for r in dict.fromkeys(so) if r not in da_vao]
    kq["nhom_da_co"] = [{"group_id": n["group_id"], "so_ban_ghi": n["so_ban_ghi"]} for n in hien]
    kq["nhom_tao_trong_luot_chua_hien"] = cho_dia
    kq["trong_nhom_sau"] = len(da_vao)
    kq["cho_vao_nhom_moi"] = thieu
    if len(hien) > 1:
        kq["nhom_trung_ten"] = len(hien)
    try:
        kq["cho_vao_nhom"] = ghi_cho_vao_nhom(endnote.thu_vien, nhom, them=thieu, da_vao=da_vao,
                                              group_id=[n["group_id"] for n in hien], dashboard=dashboard, tep=tep_cho)
    except (ValueError, OSError) as e:
        kq["cho_vao_nhom_loi"] = f"{type(e).__name__}: {e}"[:200]
    return kq


CHO_NHAP_GIAY = 10  # lượt tra lại (mỗi lượt 1 giây) sau lệnh `import` trước khi kết luận «nhập hụt»


def tra_ban_ghi_sau_nhap(endnote, dd: list[dict], vua_nhap: list[dict], ma_cua) -> tuple[dict, dict, list[dict]]:
    """Tra lại thư viện SAU lệnh nhập: trả (theo_pm, theo_doi, các trích dẫn vừa nhập mà thư viện VẪN KHÔNG có).

    VÌ SAO (19/10/2026, gói THA ngoại trú): `import x into document` trả về KHÔNG lỗi nhưng không nhập gì khi EndNote đang mở
    hai cửa sổ «Libraries Preferences» và «EndNote™ Preferences» — công cụ vẫn in «nhập mới 17» theo SỐ DỰ ĐỊNH, tra lại
    theo PMID lẫn DOI ra 0/17, nhóm không tồn tại. Cùng họ BH17: tuyên bố không điều kiện. Nay đếm theo thư viện THẬT; tra
    lặp ≤ CHO_NHAP_GIAY lượt phòng EndNote ghi chậm, rồi mới kết luận."""
    def tra() -> tuple[dict, dict]:
        return (endnote.tim_khop([d["pmid"] for d in dd if d.get("pmid")], "Accession Number"),
                endnote.tim_khop([d["doi"] for d in dd if d.get("doi")], "DOI"))

    theo_pm, theo_doi = tra()
    for _ in range(CHO_NHAP_GIAY if vua_nhap else 0):
        if all(ma_cua(d, theo_pm, theo_doi) for d in vua_nhap):
            break
        _ngu(1)
        theo_pm, theo_doi = tra()
    return theo_pm, theo_doi, [d for d in vua_nhap if not ma_cua(d, theo_pm, theo_doi)]


def _gan_pdf(endnote, can_gan: list[tuple]) -> None:
    """Đặt từng PDF vào `.Data/PDF/` rồi gắn vào bản ghi; gắn hỏng ⇒ dọn đúng thư mục vừa đặt rồi ném lỗi."""
    for r, pmid, (pdf, _nhan) in can_gan:
        url, tm = dat_pdf_vao_thu_vien(endnote.thu_vien, pdf, pmid)
        try:
            endnote.gan_tep(r, url)
        except Exception:
            shutil.rmtree(tm, ignore_errors=True)  # gắn hỏng ⇒ không để PDF mồ côi
            raise


def doi_cua_pmid(pmids: list[str], lay_pm=lay_pubmed, lay_ep=lay_europepmc) -> dict[str, str]:
    """{PMID: DOI} theo bản ghi PubMed (NCBI chặn/lỗi ⇒ Europe PMC) — cho `gan_kho` khớp bản ghi KHÔNG mang PMID ở
    «Accession Number». Lỗi cả hai nguồn ⇒ ném lên (người gọi ghi «không đo được», không coi là «không có DOI»)."""
    try:
        meta = lay_pm(pmids)
    except Exception:  # noqa: BLE001 — NCBI chặn IP/mạng lỗi ⇒ Europe PMC, như lượt nạp chủ đề
        meta = lay_ep(pmids)
    return {p: d for p, m in meta.items() if (d := chuan_doi((m or {}).get("doi")))}


def _la_pmid_khac(acc: str | None, pmid: str) -> bool:
    """Accession Number là MỘT PMID (thuần số hoặc «PMID: n») KHÁC `pmid` ⇒ định danh mâu thuẫn, không gắn theo DOI."""
    m = re.fullmatch(r"(?:PMID:\s*)?(\d{1,9})", (acc or "").strip(), flags=re.I)
    return bool(m) and m.group(1) != pmid


def gan_kho(endnote, kho: Path | None, pmids: list[str] | None, ap_dung: bool, doi_cua=None) -> dict:
    """PDF trong kho → bản ghi CÓ SẴN trong thư viện cùng PMID («Accession Number»), không cần dashboard.

    Toàn văn về SAU trích dẫn (phiên Chrome uỷ quyền, Unpaywall, Wiley TDM) ⇒ công cụ sinh PDF gọi chế độ này để PDF vào
    ngay mọi nhóm đang chứa bản ghi. Cùng luật với lượt nạp chủ đề: chỉ bản ghi CHƯA có tệp nào; bản trùng PMID trong thư
    viện chỉ gắn bản đầu (giống lúc đăng nhóm).

    Bản ghi KHÔNG mang PMID thuần số ở Accession Number (đo 24/10/2026 trên thư viện thật: 90 bản ghi có PMID trên PubMed
    nhưng 84 mang «WOS:…» — nhập từ Web of Science — và 6 mang «PMID: n») trước đây không bao giờ được gắn PDF. Nay khớp
    thêm hai bậc cho PMID còn thiếu: (1) «PMID: n»; (2) DOI của PMID theo PubMed (`doi_cua`) với trường DOI của bản ghi —
    bỏ bản ghi có Accession Number là MỘT PMID KHÁC. `doi_cua` lỗi ⇒ `doi_khong_do_duoc`, bậc (1) vẫn giữ."""
    bc: dict = {"kho_toan_van": bool(kho and kho.is_dir()), "pdf_trong_kho": 0, "co_ban_ghi": 0, "ap_dung": ap_dung,
                "khop_pmid_tien_to": 0, "khop_doi": 0}
    if not bc["kho_toan_van"]:
        return bc
    co_pdf: set[str] = set()
    for p in kho.iterdir():
        m = re.fullmatch(r"PMID-(\d{1,9})_[A-Za-z]+\.pdf", p.name, flags=re.I)
        if m and p.is_file():
            co_pdf.add(m.group(1))
    pm = sorted(co_pdf if pmids is None else co_pdf & set(pmids))
    bc["pdf_trong_kho"] = len(pm)
    theo_pm = endnote.tim_khop(pm, "Accession Number") if pm else {}
    thieu = [p for p in pm if not theo_pm.get(p)]
    if thieu:
        tien_to = endnote.tim_khop([f"PMID: {p}" for p in thieu], "Accession Number")
        for p in thieu:
            if tien_to.get(f"PMID: {p}"):
                theo_pm[p] = tien_to[f"PMID: {p}"]
                bc["khop_pmid_tien_to"] += 1
        thieu = [p for p in thieu if not theo_pm.get(p)]
    if thieu and doi_cua is not None:
        try:
            doi = doi_cua(thieu)
        except Exception as e:  # noqa: BLE001 — không tra được DOI: không gắn theo DOI lượt này, không phải «không có»
            bc["doi_khong_do_duoc"] = f"{type(e).__name__}: {e}"[:200]
            doi = {}
        theo_doi = endnote.tim_khop(sorted(set(doi.values())), "DOI") if doi else {}
        ung = {p: theo_doi[d] for p, d in doi.items() if theo_doi.get(d)}
        acc = endnote.doc_truong(sorted({r for rs in ung.values() for r in rs}), "Accession Number") if ung else {}
        for p, rs in ung.items():
            hop = [r for r in rs if r in acc and not _la_pmid_khac(acc[r], p)]
            if hop:
                theo_pm[p] = hop
                bc["khop_doi"] += 1
    cap: list[tuple[dict, str]] = []
    thay: set[str] = set()
    for p in pm:
        for r in (theo_pm.get(p) or [])[:1]:
            if r not in thay:
                thay.add(r)
                cap.append(({"pmid": p}, r))
    bc["co_ban_ghi"] = len(cap)
    can_gan, _ = xet_toan_van(endnote, cap, kho)
    if ap_dung:
        _gan_pdf(endnote, can_gan)
        bc["gan_them_pdf"] = len(can_gan)
    else:
        bc["se_gan_pdf"] = len(can_gan)
    return bc


def _nhan_dinh_danh(pmid: str | None, doi: str | None) -> str:
    return " · ".join(x for x in (f"PMID {pmid}" if pmid else "", f"DOI {doi}" if doi else "") if x) or "?"


def _so_ban_ghi(ma: str) -> str:
    """`<RecordID database="2" recNum="7327" />` → "7327" (chuỗi lạ thì trả nguyên văn)."""
    m = re.search(r'recNum="(\d+)"', ma or "")
    return m.group(1) if m else ma


def trong_thung_rac(rac: dict | None, pmid: str | None, doi: str | None) -> bool:
    if not rac:
        return False
    return bool((pmid and str(pmid) in rac.get("pmid", ())) or (doi and chuan_doi(doi) in rac.get("doi", ())))


def doc_thung_rac_an_toan(endnote) -> tuple[dict | None, str | None]:
    """(định danh trong thùng rác, None) hoặc (None, lý do KHÔNG ĐO ĐƯỢC). Lớp EndNote không có `thung_rac` cũng là không đo
    được — không bao giờ là «thùng rác rỗng»."""
    doc = getattr(endnote, "thung_rac", None)
    if doc is None:
        return None, "lớp EndNote này không đọc được thùng rác"
    try:
        return doc(), None
    except (OSError, sqlite3.Error) as e:
        return None, f"{type(e).__name__}: {e}"[:200]


def nap_chu_de(dash: Path, *, endnote, ap_dung: bool, kho: Path | None, doc_data=None,
               lay_pm=lay_pubmed, lay_cr=lay_crossref, lay_ep=lay_europepmc, ten_nhom: str | None = None,
               loai_tru: dict | None = None, tep_cho: Path | None = None, da_tao: set[str] | None = None,
               tien_to: str = TIEN_TO_NHOM) -> dict:
    """Một dashboard → một nhóm EndNote. `endnote` None = chỉ lập kế hoạch, không kiểm trùng được. `tien_to` = tiền tố tên nhóm
    MẶC ĐỊNH («EBM · » chủ đề chứng cứ · «NC · » đề tài nghiên cứu); `ten_nhom` đã có thì không dùng.

    `loai_tru` (`doc_loai_tru`) = danh sách loại trừ của BÁC SĨ (18/10/2026): định danh trong đó KHÔNG nhập, KHÔNG đăng vào
    nhóm, KHÔNG gắn PDF — xét theo định danh của dashboard rồi xét LẠI theo định danh của metadata (dashboard chỉ ghi PMID
    mà bác sĩ loại theo DOI). Trích dẫn chưa có trong thư viện mà đang nằm trong THÙNG RÁC EndNote cũng không nhập lại."""
    doc_data = doc_data or _nap_doc_data()
    data = doc_data(dash)
    if not data:
        return {"dashboard": dash.name, "loi": "không đọc được khối DATA"}
    nhom = ten_nhom or tien_to + ten_chu_de(data, dash)
    khoa = khoa_chu_de(dash)
    dd_tat_ca = trich_dinh_danh(data)
    bc: dict = {"dashboard": dash.name, "nhom": nhom, "so_trich_dan": len(dd_tat_ca), "da_co": 0, "nhap_moi": 0,
                "pdf_dinh_kem": 0, "khong_lay_duoc": [], "chua_toan_van": 0, "dang_vao_nhom": 0,
                "kiem_trung": endnote is not None, "ap_dung": ap_dung,
                # Không thấy kho ⇒ CHƯA XÉT được PDF — khác hẳn «không có toàn văn» (lượt 11/10 từ worktree báo
                # «đính PDF 0» trong khi kho có sẵn PDF Wiley TDM của chủ đề).
                "kho_toan_van": bool(kho and kho.is_dir()),
                # None = không cần đo (không có bài mới) · True = đã đo · False = KHÔNG ĐO ĐƯỢC (khác «không có gì»)
                "loai_tru": [], "trong_thung_rac": [], "thung_rac_do_duoc": None}

    def ma_cua(d: dict, theo_pm: dict, theo_doi: dict) -> list[str]:
        return (theo_pm.get(d["pmid"]) if d.get("pmid") else None) or \
               (theo_doi.get(d["doi"]) if d.get("doi") else None) or []

    def cap_ban_ghi(theo_pm: dict, theo_doi: dict) -> list[tuple[dict, str]]:
        """Mỗi trích dẫn ↔ bản ghi ĐẦU TIÊN khớp (bản trùng sẵn có trong thư viện: chỉ dùng một), không lặp mã."""
        cap: list[tuple[dict, str]] = []
        thay: set[str] = set()
        for d in dd:
            for r in ma_cua(d, theo_pm, theo_doi)[:1]:
                if r not in thay:
                    thay.add(r)
                    cap.append((d, r))
        return cap

    def ghi_loai_tru(d: dict, muc: dict, con_trong: list[str] | None, pmid=None, doi=None) -> None:
        bc["loai_tru"].append({"dinh_danh": _nhan_dinh_danh(pmid or d.get("pmid"), doi or d.get("doi")),
                               "ly_do": muc.get("ly_do"), "ngay": muc.get("ngay"), "con_trong_thu_vien": con_trong})

    theo_pm = endnote.tim_khop([d["pmid"] for d in dd_tat_ca if d.get("pmid")], "Accession Number") if endnote else {}
    theo_doi = endnote.tim_khop([d["doi"] for d in dd_tat_ca if d.get("doi")], "DOI") if endnote else {}

    # ① Danh sách loại trừ của bác sĩ thắng mọi thứ — kể cả khi bản ghi còn nằm trong thư viện (chưa chuyển vào thùng rác):
    #    không đăng vào nhóm, không gắn PDF; chỉ BÁO mã bản ghi để bác sĩ tự xử lý — công cụ không bao giờ xoá.
    dd: list[dict] = []
    for d in dd_tat_ca:
        muc = muc_loai_tru(loai_tru, d.get("pmid"), d.get("doi"))
        if muc is None:
            dd.append(d)
        else:
            ghi_loai_tru(d, muc, [_so_ban_ghi(r) for r in ma_cua(d, theo_pm, theo_doi)] if endnote else None)
    moi = [d for d in dd if not ma_cua(d, theo_pm, theo_doi)]
    bc["da_co"] = len(dd) - len(moi)

    # ② Thùng rác: `find` của EndNote không thấy bản ghi trong thùng rác ⇒ bài bác sĩ đã bỏ trông như «chưa có».
    rac = None
    if moi and endnote is not None:
        rac, loi_rac = doc_thung_rac_an_toan(endnote)
        bc["thung_rac_do_duoc"] = rac is not None
        if loi_rac:
            bc["thung_rac_loi"] = loi_rac
    bo: set[int] = set()
    for d in moi:
        if trong_thung_rac(rac, d.get("pmid"), d.get("doi")):
            bc["trong_thung_rac"].append(_nhan_dinh_danh(d.get("pmid"), d.get("doi")))
            bo.add(id(d))
    moi = [d for d in moi if id(d) not in bo]

    co, bc["khong_lay_duoc"] = lay_metadata(moi, lay_pm, lay_cr, lay_ep) if moi else ([], [])
    hom_nay = date.today().isoformat()
    can_nhap: list[dict] = []
    nguon_nhap: list[tuple[dict, dict]] = []  # (trích dẫn của dashboard, metadata sẽ nhập) — để đếm lại SAU khi nhập
    for d, m in co:
        # ③ Xét LẠI theo định danh của metadata: dashboard chỉ ghi PMID mà bác sĩ loại theo DOI (hoặc ngược lại).
        muc = muc_loai_tru(loai_tru, m.get("pmid"), m.get("doi"))
        if muc is not None:
            ghi_loai_tru(d, muc, None, m.get("pmid"), m.get("doi"))
            bo.add(id(d))
            continue
        if trong_thung_rac(rac, m.get("pmid"), m.get("doi")):
            bc["trong_thung_rac"].append(_nhan_dinh_danh(m.get("pmid"), m.get("doi")))
            bo.add(id(d))
            continue
        m["tu_khoa"] = [f"EBM: {khoa}"]
        m["ghi_chu"] = (f"Nạp tự động bởi EBM Copilot ngày {hom_nay} từ {dash.name} "
                        f"({'mục ' + d['muc'] if d['vai'] == 'muc' else 'tham khảo của ' + d['muc']}). "
                        f"Metadata: {m['nguon_meta']}.")
        if m.get("da_rut"):
            m["nhan"] = "ĐÃ RÚT (PubMed)"
            m["ghi_chu"] += " CẢNH BÁO: PubMed gắn «Retracted Publication»."
        m["_pdf"] = chon_pdf(kho, m.get("pmid"))
        can_nhap.append(m)
        nguon_nhap.append((d, m))
    dd = [d for d in dd if id(d) not in bo]  # cap_ban_ghi đọc `dd` qua closure — bài bị loại không đăng nhóm/gắn PDF
    bc["nhap_moi"] = len(can_nhap)
    bc["pdf_dinh_kem"] = sum(1 for m in can_nhap if m["_pdf"])
    bc["chua_toan_van"] = len(can_nhap) - bc["pdf_dinh_kem"]
    if not ap_dung or endnote is None:
        bc["ke_hoach_nhap"] = [m.get("pmid") or m.get("doi") for m in can_nhap]
        if endnote is not None:  # chạy khô vẫn ĐỌC được trường đính kèm của bản ghi đã có (chỉ đọc)
            bc["se_gan_pdf"] = len(xet_toan_van(endnote, cap_ban_ghi(theo_pm, theo_doi), kho)[0])
        return bc

    thu_muc_moi: list[Path] = []
    try:
        for m in can_nhap:
            if m["_pdf"]:
                url, tm = dat_pdf_vao_thu_vien(endnote.thu_vien, m["_pdf"][0], m["pmid"])
                thu_muc_moi.append(tm)
                m["_thu_muc"] = tm
                m["pdf_url"] = url
                m["ghi_chu"] += f" Toàn văn đính kèm: {m['_pdf'][1]}."
        if can_nhap:
            with tempfile.TemporaryDirectory(prefix="ebm-endnote-") as tam:
                tep = Path(tam) / "nhap.xml"
                tep.write_text(dung_xml(can_nhap), encoding="utf-8", newline="\n")
                endnote.nhap(tep)
    except Exception:
        for tm in thu_muc_moi:  # bước nhập hỏng ⇒ không để PDF mồ côi trong thư viện
            shutil.rmtree(tm, ignore_errors=True)
        raise

    theo_pm, theo_doi, chua_vao = tra_ban_ghi_sau_nhap(endnote, dd, [d for d, _m in nguon_nhap], ma_cua)
    bc["nhap_thuc"] = len(nguon_nhap) - len(chua_vao)
    if chua_vao:
        hut = {id(d) for d in chua_vao}
        bc["nhap_hut"] = [_nhan_dinh_danh(m.get("pmid") or d.get("pmid"), m.get("doi") or d.get("doi"))
                          for d, m in nguon_nhap if id(d) in hut]
        bc["cua_so_endnote"] = endnote.ten_cua_so() if hasattr(endnote, "ten_cua_so") else []
        for d, m in nguon_nhap:  # PDF vừa đặt cho bản ghi KHÔNG vào thư viện ⇒ mồ côi, dọn như nhánh nhập hỏng
            if id(d) in hut and m.get("_thu_muc"):
                shutil.rmtree(m["_thu_muc"], ignore_errors=True)
    cap = cap_ban_ghi(theo_pm, theo_doi)
    # Nhóm đo theo group_id trên sdb.eni; nhóm ĐÃ có thì không post (post luôn sinh nhóm trùng tên — đo 24/10/2026).
    bc.update(xep_vao_nhom(endnote, nhom, [r for _, r in cap], dashboard=dash.name, tep_cho=tep_cho, da_tao=da_tao))

    # Toàn văn về SAU khi trích dẫn đã nằm trong EndNote ⇒ gắn vào bản ghi chưa có tệp đính kèm nào.
    can_gan, bc["thieu_toan_van"] = xet_toan_van(endnote, cap, kho)
    _gan_pdf(endnote, can_gan)
    bc["gan_them_pdf"] = len(can_gan)
    return bc


def nap_nhieu(files: list[Path], *, endnote, ap_dung: bool, kho: Path | None, ten_nhom: str | None = None,
              doc_data=None, cau_hinh: Path | None = None, loai_tru: dict | None = None, tien_to: str = TIEN_TO_NHOM,
              **lay) -> list[dict]:
    """Nạp nhiều dashboard: MỘT chủ đề (khoá bỏ đuôi ngày) = MỘT nhóm qua mọi phiên bản.

    Bác sĩ dặn 11/10/2026: «chủ đề nào đã có và trùng thì giữ nguyên và bổ sung phần thiếu». Câu hỏi lâm sàng đổi chữ giữa
    các phiên bản (Suy tim tổng hợp: 5 bản, 4 câu khác nhau) nên đặt tên theo câu hỏi sẽ sinh nhiều nhóm gần trùng. Vì vậy:
    nhóm đã ghi nhớ cho chủ đề (bảng `nhom_theo_chu_de` trong cấu hình máy) thắng; chưa có thì bản MỚI NHẤT đặt tên và các bản
    cũ hơn đổ vào cùng nhóm (bản ghi đã có giữ nguyên, chỉ thêm bài và thêm thành viên nhóm còn thiếu). `--ten-nhom` của
    bác sĩ thắng tất cả và được ghi nhớ.

    `loai_tru` None ⇒ đọc danh sách loại trừ của bác sĩ từ `cau_hinh` (tệp hỏng ⇒ CauHinhHong — không nhập gì)."""
    doc_data = doc_data or _nap_doc_data()
    bang = nhom_da_ghi(cau_hinh)
    if loai_tru is None:
        loai_tru = doc_loai_tru(cau_hinh)
    ket_qua: list[dict] = []
    da_tao: set[str] = set()  # nhóm đã post trong lượt này — bản kế tiếp cùng chủ đề không post lần hai (xep_vao_nhom)
    for f in sap_xep_phien_ban(files):
        khoa = khoa_chu_de(f)
        ten = ten_nhom or bang.get(khoa)
        try:
            bc = nap_chu_de(f, endnote=endnote, ap_dung=ap_dung, kho=kho, doc_data=doc_data, ten_nhom=ten,
                            loai_tru=loai_tru, da_tao=da_tao, tien_to=tien_to, **lay)
        except (RuntimeError, OSError) as e:
            bc = {"dashboard": f.name, "loi": f"{type(e).__name__}: {e}"[:300]}
        if not bc.get("loi") and bc.get("nhom"):
            moi = bang.get(khoa) != bc["nhom"]
            bang[khoa] = bc["nhom"]
            if moi and ap_dung and endnote is not None:  # chỉ ghi nhớ khi nhóm THẬT đã dựng trong EndNote
                ghi_nhom(khoa, bc["nhom"], cau_hinh)
        ket_qua.append(bc)
        _in_bao_cao(bc)
    return ket_qua


def _ds_rec(rec: list[int], toi_da: int = 15) -> str:
    return ", ".join(map(str, rec[:toi_da])) + (" …" if len(rec) > toi_da else "")


def _in_nhom(bc: dict) -> None:
    """Phần NHÓM của báo cáo một dashboard (khoá do `xep_vao_nhom` trả)."""
    if bc.get("nhom_khong_do_duoc"):
        print(f"   ⚪ KHÔNG ĐO ĐƯỢC nhóm trong sdb.eni ({bc['nhom_khong_do_duoc']}) — KHÔNG đăng vào nhóm (chưa biết nhóm đã có "
              "chưa; post vào tên đã có sinh nhóm trùng tên). Chạy lại lệnh này sau.")
    elif bc.get("dang_vao_nhom"):
        print(f"   Tạo nhóm mới với {bc['dang_vao_nhom']} bản ghi"
              + (" · đo lại theo group_id: " + ", ".join(f"{g['group_id']} ({g['so_ban_ghi']} bài)" for g in bc["nhom_sau"])
                 if bc.get("nhom_sau") else ""))
        if bc.get("nhom_chua_thay") or bc.get("nhom_sau_khong_do_duoc"):
            print(f"   ⚪ Chưa {'thấy' if bc.get('nhom_chua_thay') else 'đo được'} nhóm trong sdb.eni sau {CHO_NHOM_GIAY} giây — "
                  "EndNote có thể chưa ghi xuống đĩa; đo lại: python3 tools/endnote_suc_khoe.py")
    elif bc.get("nhom_da_co") is not None:
        ds = ", ".join(f"group_id {g['group_id']}: {g['so_ban_ghi']} bài" for g in bc["nhom_da_co"])
        if bc.get("nhom_tao_trong_luot_chua_hien"):
            ds = "vừa tạo trong lượt này, chưa hiện trên sdb.eni"
        moi, con = bc.get("cho_vao_nhom_moi") or [], bc.get("cho_vao_nhom")
        if moi or con:
            print(f"   🛎 Nhóm đã có ({ds}) — KHÔNG post (post vào tên đã có LUÔN sinh nhóm trùng tên, đo 24/10/2026). "
                  f"{len(moi)} bản ghi mới chờ bác sĩ đưa vào nhóm" + (f" (recNum {_ds_rec(moi)})" if moi else "")
                  + (f"; hàng chờ của nhóm còn {len(con)}" if con is not None else ""))
            print(f"     Bác sĩ: python3 tools/nap_endnote_chu_de.py --cho-vao-nhom \"{bc['nhom']}\" (EndNote chỉ hiện các bài "
                  "chờ) → ⌘A → kéo vào nhóm ở cột trái (hoặc phiên Claude: chọn từng dòng → Groups › Add References To › nhóm); "
                  "lượt nạp sau tự dọn bài đã vào nhóm khỏi hàng chờ.")
        else:
            print(f"   Nhóm đã có ({ds}) — đủ bài, không cần đăng thêm")
        if bc.get("cho_vao_nhom_loi"):
            print(f"   ⚠ KHÔNG ghi được hàng chờ ({bc['cho_vao_nhom_loi']}) — recNum cần đưa vào nhóm: {_ds_rec(moi, 50)}")
    if bc.get("nhom_trung_ten"):
        print(f"   ⚠ EndNote đang có {bc['nhom_trung_ten']} nhóm cùng tên này — gộp tay: mở nhóm ít bài, chọn hết, kéo vào "
              "nhóm kia, rồi xoá nhóm rỗng (xoá nhóm không xoá bài khỏi thư viện)")


def chay_cho_vao_nhom(ten: str, tep: Path | None = None, endnote_cls=None) -> int:
    """`--cho-vao-nhom ["<tên>"]`: liệt kê hàng chờ đưa vào nhóm của thư viện, đo lại theo group_id và dọn bài bác sĩ đã kéo
    vào nhóm. Có tên ⇒ EndNote chỉ hiện các bài chờ của nhóm đó (bác sĩ ⌘A → kéo vào nhóm). Không ghi gì vào EndNote."""
    sk = _sk()
    ch = doc_cau_hinh()
    if not ch:
        print(f"⚪ chưa khai thư viện EndNote ({CAU_HINH})")
        return MA_KHONG_CHAY
    tv = Path(ch["thu_vien"])
    try:
        da_luu = sk.doc_cho_vao_nhom(tep)["thu_vien"].get(sk.khoa_thu_vien(tv)) or {}
        con = {n["ten"]: n for n in sk.cho_vao_nhom_con_lai(tv, tep)}
        for t, m in da_luu.items():  # dọn bài đã vào nhóm khỏi tệp hàng chờ
            xong = set(m["rec"]) - set((con.get(t) or {}).get("rec", []))
            if xong:
                ghi_cho_vao_nhom(tv, t, them=[], da_vao=xong, group_id=(con.get(t) or m).get("group_id") or [], tep=tep)
    except (OSError, sqlite3.Error, ValueError) as e:
        print(f"⚪ KHÔNG ĐO ĐƯỢC hàng chờ đưa vào nhóm: {type(e).__name__}: {str(e)[:200]}")
        return MA_KHONG_CHAY
    if not con:
        print("✓ Không còn bản ghi nào chờ đưa vào nhóm EndNote.")
        return MA_OK
    for t, n in con.items():
        nhom = (f"group_id {', '.join(map(str, n['group_id']))}" if n["group_id"] else
                "chưa thấy nhóm trong sdb.eni — lượt nạp sau đo lại/tạo nhóm")
        print(f"👤 «{t}» ({nhom}) — {len(n['rec'])} bản ghi chờ bác sĩ đưa vào nhóm: recNum {_ds_rec(n['rec'], 40)}")
        if n["so_nhom"] > 1:
            print(f"   ⚠ tên này đang có {n['so_nhom']} nhóm — gộp hai nhóm trước (kéo nhóm ít bài vào nhóm kia, xoá nhóm rỗng)")
    if not ten:
        print("Hiện các bài của MỘT nhóm trong EndNote: python3 tools/nap_endnote_chu_de.py --cho-vao-nhom \"<tên nhóm>\"")
        return MA_OK
    chon = [n for t, n in con.items() if sk.khoa_ten(t) == sk.khoa_ten(ten)]
    if not chon:
        print(f"✗ «{ten}» không có trong hàng chờ")
        return MA_THAM_SO
    try:
        en = (endnote_cls or EndNoteMac)(ch.get("ung_dung") or UNG_DUNG_MAC_DINH, tv)
    except KhongChayDuoc as e:
        print(f"⚪ {e}")
        return MA_KHONG_CHAY
    if not en.dang_mo_dung_thu_vien():
        print(f"⚪ EndNote chưa mở thư viện {tv.name} — bác sĩ mở EndNote rồi chạy lại")
        return MA_KHONG_CHAY
    en.hien_ban_ghi(chon[0]["rec"])
    print(f"✓ EndNote đang CHỈ hiện {len(chon[0]['rec'])} bài chờ. Bác sĩ: bấm vào danh sách → ⌘A → kéo vào nhóm «{chon[0]['ten']}» "
          "ở cột trái (hoặc menu Groups → Add References To → nhóm đó — menu References KHÔNG có mục này, đo 25/10/2026; "
          "phiên Claude làm được: chọn từng dòng rồi dùng menu đó). Xong chạy lại --cho-vao-nhom để kiểm.")
    return MA_OK


def _in_bao_cao(bc: dict) -> None:
    if bc.get("loi"):
        print(f"✗ {bc['dashboard']}: {bc['loi']}")
        return
    dau = "✓" if not bc["khong_lay_duoc"] else "◐"
    print(f"{dau} {bc['dashboard']} → nhóm «{bc['nhom']}»")
    if not bc["kiem_trung"]:
        print("   (chưa mở EndNote nên CHƯA kiểm được bài nào đã có trong thư viện)")
    loai_tru = bc.get("loai_tru") or []
    rac = bc.get("trong_thung_rac") or []
    so_bo = len(loai_tru) + len(rac)
    # Lượt ghi thật in số ĐÃ VÀO thư viện (đếm lại sau nhập), không in số dự định — xem tra_ban_ghi_sau_nhap.
    nhap = (f"nhập mới {bc['nhap_thuc']}/{bc['nhap_moi']} (đếm lại trong thư viện sau nhập)"
            if bc["ap_dung"] and "nhap_thuc" in bc else
            f"{'nhập mới' if bc['ap_dung'] else 'sẽ nhập mới'} {bc['nhap_moi']}")
    print(f"   {bc['so_trich_dan']} trích dẫn · " + (f"bỏ qua {so_bo} · " if so_bo else "")
          + f"đã có trong thư viện {bc['da_co']} · {nhap} "
          f"(đính PDF {bc['pdf_dinh_kem']}, chưa có toàn văn {bc['chua_toan_van']})")
    if bc.get("nhap_hut"):
        hut = bc["nhap_hut"]
        print(f"   🔴 NHẬP HỤT: {len(hut)}/{bc['nhap_moi']} trích dẫn KHÔNG có trong thư viện sau lệnh nhập của EndNote — "
              f"{', '.join(hut[:8])}{' …' if len(hut) > 8 else ''}")
        cs = [c for c in bc.get("cua_so_endnote") or [] if not c.lower().endswith(".enl")]  # bỏ cửa sổ thư viện
        if cs:
            print(f"     Cửa sổ EndNote đang mở: {' · '.join(cs[:6])} — cửa sổ Preferences/hộp thoại có thể chặn lệnh nhập.")
        print("     Đóng cửa sổ phụ/hộp thoại trong EndNote rồi chạy lại lệnh này (công cụ tra trước khi nhập nên không "
              "nhập trùng bài đã vào); PDF vừa đặt cho các bài hụt đã được dọn.")
    for x in loai_tru:
        print(f"   ⊘ bỏ qua theo danh sách loại trừ của bác sĩ: {x['dinh_danh']} — «{x['ly_do']}» ({x['ngay']})")
        if x.get("con_trong_thu_vien"):
            print(f"     ⚠ Bản ghi vẫn còn trong thư viện (recNum {', '.join(x['con_trong_thu_vien'])}) — công cụ KHÔNG xoá, "
                  "không đăng vào nhóm, không gắn PDF; chuyển vào thùng rác là thao tác của bác sĩ.")
    if rac:
        print(f"   ⊘ Đang nằm trong THÙNG RÁC EndNote — không nhập lại: {', '.join(rac)} (dùng lại: Restore trong EndNote; "
              "chặn hẳn kể cả sau khi dọn thùng rác: --loai-tru <định danh> --ly-do \"…\")")
    if bc.get("thung_rac_do_duoc") is False:
        print(f"   ⚪ Chưa đo được thùng rác EndNote ({bc.get('thung_rac_loi', '?')}) — bài mới chỉ được lọc theo danh sách "
              "loại trừ của bác sĩ.")
    if not bc["kho_toan_van"]:
        print("   ⚠ Không thấy kho toàn văn — CHƯA XÉT PDF (không phải «không có»); chỉ đường bằng --kho-toan-van")
    if bc.get("se_gan_pdf"):
        print(f"   Sẽ gắn toàn văn cho bản ghi đã có: {bc['se_gan_pdf']}")
    if bc["ap_dung"] and bc["kiem_trung"]:
        _in_nhom(bc)
        print(f"   Gắn thêm toàn văn cho bản ghi đã có: {bc.get('gan_them_pdf', 0)}")
        thieu = bc.get("thieu_toan_van") or []
        if thieu:
            print(f"   Còn thiếu toàn văn trong EndNote: {len(thieu)} — {', '.join(thieu[:12])}"
                  f"{' …' if len(thieu) > 12 else ''}")
    if bc["khong_lay_duoc"]:
        print(f"   ⚠ Không lấy được metadata (KHÔNG nhập): {', '.join(bc['khong_lay_duoc'][:10])}")


def _nap_tom_tat():
    sp = importlib.util.spec_from_file_location("_tom_tat_endnote_vi", ROOT / "tools" / "tom_tat_endnote_vi.py")
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod


def _tim_dash_goc() -> Path | None:
    """Thư mục EBM-Dashboards/ của cây đang chạy (None ở worktree/bản sao trần) — tách hàm để test thay được."""
    bst_sp = importlib.util.spec_from_file_location("_bst_endnote", ROOT / "tools" / "ban_sao_tran.py")
    bst = importlib.util.module_from_spec(bst_sp)
    bst_sp.loader.exec_module(bst)
    return bst.duong_goc("EBM-Dashboards", ROOT)


def xac_dinh_kho(kho_tham_so: str | None, dash_goc: Path | None, files: list[Path]) -> Path | None:
    """Kho toàn văn của lượt chạy (17/10/2026). Thứ tự:
    1. `--kho-toan-van` — giữ NGUYÊN kể cả khi sai đường (người gọi kiểm `is_dir()` và từ chối ghi, không tự đoán chỗ khác);
    2. `toan_van_oa` CẠNH dashboard của `--file` — đúng kho mà bước ⑧ và cổng BH161 đọc (TT-07 của xuat_goi_cap_nhat). Chỉ nhận
       khi mọi dashboard cho ra CÙNG MỘT kho có thật — dashboard ở nhiều thư mục khác nhau ⇒ mơ hồ, không chọn bừa;
    3. `<EBM-Dashboards gốc>/toan_van_oa`.
    Không thấy thư mục nào ⇒ None. Trước đó chỉ xét (3): chạy từ worktree/bản sao trần với `--file` trỏ tới dashboard thật ⇒
    kho None ⇒ dòng «Toàn văn» của MỌI bản ghi thành «chưa xét (không thấy kho)» (đo 17/10: «sẽ ghi 877 · không đổi 0»)."""
    if kho_tham_so:
        return Path(kho_tham_so)
    canh = {(Path(f).parent / "toan_van_oa").resolve() for f in files}
    if len(canh) == 1 and next(iter(canh)).is_dir():
        return next(iter(canh))
    goc = dash_goc / "toan_van_oa" if dash_goc else None
    return goc if goc is not None and goc.is_dir() else None


def chan_ghi_khi_thieu_kho(a, kho: Path | None) -> int | None:
    """Fail-closed khi GHI (17/10/2026): không có kho thật thì khối ĐỌC NHANH ghi «Toàn văn: chưa xét (không thấy kho)» ĐÈ
    thông tin tốt hơn đang có («có PDF · có bản đọc sâu») của MỌI bản ghi ⇒ trả mã từ chối, không ghi gì. Chạy khô vẫn đi
    tiếp (để thấy kế hoạch) nhưng in ⚠. Không áp: `--gan-kho` (có báo riêng), `--xuat-xml` (không đụng thư viện),
    `--ap-dung --khong-tom-tat` (chỉ nhập bản ghi, không ghi khối — PDF không đính, có ⚠). Có kho thật ⇒ None (đi tiếp)."""
    if a.gan_kho or a.xuat_xml or (kho is not None and kho.is_dir()):
        return None
    ly = (f"không thấy kho toàn văn {kho}" if kho is not None else
          "không thấy kho toàn văn (không có toan_van_oa cạnh dashboard, cũng không có EBM-Dashboards/ gốc)")
    if a.ap_dung and (a.tom_tat_vi or not a.khong_tom_tat):
        print(f"⚪ KHÔNG ĐO ĐƯỢC — {ly}: khối ĐỌC NHANH sẽ ghi «Toàn văn: chưa xét» đè thông tin đang có của mọi bản ghi "
              "⇒ KHÔNG ghi gì vào EndNote. Chỉ đường: --kho-toan-van <EBM-Dashboards>/toan_van_oa")
        return MA_KHONG_CHAY
    print(f"⚠ {ly} — lượt này không đính PDF, dòng «Toàn văn» tính là «chưa xét»"
          + (" (--ap-dung ghi khối ĐỌC NHANH sẽ bị từ chối)." if not a.ap_dung and (a.tom_tat_vi or not a.khong_tom_tat)
             else "."))
    return None


# W10 (15/10/2026, HỢP ĐỒNG với bước ⑧ của xuat_goi_cap_nhat): cổng liêm chính CHƯA PASS (chạy không --online, mạng lỗi
# ⇒ Word bị hạ «CHƯA xác minh nguồn sống») thì khối ĐỌC NHANH không được mang chân «chép từ dashboard đã qua cổng».
# Dòng cảnh báo đặt ở CHÂN khối — dòng ĐẦU phải giữ dấu mở `MO_DAU` để lượt chạy lại nhận ra và THAY khối cũ.
DONG_CHUA_XAC_MINH = "⚠️ CHƯA xác minh nguồn sống (cổng liêm chính chưa PASS)"
CHAN_CHUA_XAC_MINH = "Cần bác sĩ kiểm chứng · chép từ dashboard, không thêm khẳng định mới · áp dụng qua Cổng A."


def ham_bo_qua(loai_tru: dict | None, rac: dict | None):
    """Vị từ (pmid, doi, co_ban_ghi) → lý do bỏ qua | None cho bước tóm tắt. Danh sách loại trừ của bác sĩ: luôn bỏ qua.
    Thùng rác: chỉ khi CHƯA có bản ghi sống (còn một bản sống thì vẫn ghi khối cho bản đó). Không có gì để lọc ⇒ None."""
    if not (loai_tru and (loai_tru.get("doi") or loai_tru.get("pmid"))) and not (rac and (rac.get("doi") or rac.get("pmid"))):
        return None

    def bo_qua(pmid, doi, co_ban_ghi: bool) -> str | None:
        muc = muc_loai_tru(loai_tru, pmid, doi)
        if muc is not None:
            return f"danh sách loại trừ của bác sĩ — «{muc.get('ly_do')}», {muc.get('ngay')}"
        if not co_ban_ghi and trong_thung_rac(rac, pmid, doi):
            return "đang nằm trong thùng rác EndNote"
        return None
    return bo_qua


def chay_tom_tat(endnote, files: list[Path], kho: Path | None, ap_dung: bool, tt=None,
                 chua_xac_minh: bool = False, bo_qua=None) -> dict | None:
    """Ghi khối «TÓM TẮT THỰC HÀNH» tiếng Việt vào Abstract (tom_tat_endnote_vi). In một dòng; lỗi ⇒ dòng ✗, trả None.
    Không làm hỏng lượt nạp vừa xong: nạp và tóm tắt là hai bước, bước sau hỏng thì bước trước vẫn giữ.

    `chua_xac_minh` ⇒ chân khối đổi sang `DONG_CHUA_XAC_MINH` + chân KHÔNG nói «đã qua cổng» (thay hằng CHAN/CHAN_MAY
    của mô-đun tóm tắt TRONG lượt này rồi trả lại nguyên trạng — mô-đun đó dựng chân khối từ hai hằng ấy). Chạy khô ⇒
    dòng tổng kết mở bằng «ℹ», không bằng «✓» (G3-D8: ✓ + mã 0 dễ bị đọc nhầm thành «đã ghi»)."""
    try:
        tt = tt or _nap_tom_tat()
        # Chỉ đụng hằng của mô-đun tóm tắt khi có cờ — không cờ thì mô-đun (hay bản giả của test) giữ nguyên.
        chan_cu = (getattr(tt, "CHAN", None), getattr(tt, "CHAN_MAY", None)) if chua_xac_minh else None
        if chan_cu is not None:
            tt.CHAN = f"{DONG_CHUA_XAC_MINH}\n{CHAN_CHUA_XAC_MINH}"
            tt.CHAN_MAY = f"{DONG_CHUA_XAC_MINH}\n{chan_cu[1] or CHAN_CHUA_XAC_MINH}"
        try:
            try:
                kho_tt = tt.nap_tom_tat_abstract(files[0].parent if files else None)
            except (ValueError, OSError) as e:
                print(f"⚠ Kho tóm tắt máy {tt.TEP_TOM_TAT_ABS} không đọc được ({e}) — lượt này không in tóm tắt máy"[:300])
                kho_tt = {}
            # Ngữ cảnh từ MỌI dashboard cùng thư mục (bước ⑧ chỉ đưa MỘT dashboard) — chỉ ghi trích dẫn của `files`.
            boi_canh = sorted(files[0].parent.glob("WebDashboard_*.html")) if files and files[0].parent.is_dir() else None
            # `bo_qua` chỉ truyền khi có (bản giả của test cũ không nhận khoá này).
            bc = tt.ghi_tom_tat(endnote, files, kho=kho, ap_dung=ap_dung, doc_data=_nap_doc_data(), tom_tat_abs=kho_tt,
                                boi_canh=boi_canh, **({"bo_qua": bo_qua} if bo_qua else {}))
        finally:
            if chan_cu is not None:
                tt.CHAN, tt.CHAN_MAY = chan_cu
    except (RuntimeError, OSError, sqlite3.Error) as e:
        print(f"✗ Tóm tắt tiếng Việt (Abstract): {type(e).__name__}: {e} — chưa ghi gì sau lỗi này"[:300])
        return None
    if chua_xac_minh:
        print(f"⚠ Cổng liêm chính CHƯA PASS — khối ĐỌC NHANH ghi rõ «{DONG_CHUA_XAC_MINH}».")
    print(f"{'✓' if ap_dung else 'ℹ Chạy khô ·'} Tóm tắt tiếng Việt (Abstract): {bc['trich_dan']} trích dẫn · "
          f"{bc['co_ban_ghi']} có bản ghi · "
          f"{'đã ghi ' + str(bc['da_ghi']) if ap_dung else 'sẽ ghi ' + str(bc['se_ghi'])} · "
          f"không đổi {bc['khong_doi']} · tóm tắt máy (tham khảo) {bc['tom_tat_may']}"
          + (f" · sao lưu trước khi ghi: {bc['sao_luu']}" if bc.get("sao_luu") else ""))
    if bc["khong_co_ban_ghi"]:
        print(f"   Chưa có bản ghi trong thư viện (nạp chủ đề trước): {len(bc['khong_co_ban_ghi'])} — "
              + ", ".join(bc["khong_co_ban_ghi"][:8]) + (" …" if len(bc["khong_co_ban_ghi"]) > 8 else ""))
    bo_bs = bc.get("bo_qua_theo_bac_si") or []
    if bo_bs:
        print(f"   ⊘ Không ghi khối (bác sĩ đã loại/đã bỏ vào thùng rác): {len(bo_bs)} — " + "; ".join(bo_bs[:8])
              + (" …" if len(bo_bs) > 8 else ""))
    for loi in bc["loi"][:8] + bc["tom_tat_lech_so"][:8]:
        print(f"   ⚠ {loi}")
    # 17/10/2026: trước đó cắt IM LẶNG ở 8 dòng — 164 cảnh báo «trường lạ» chỉ hiện 8, không ai thấy quy mô thật.
    an = max(0, len(bc["loi"]) - 8) + max(0, len(bc["tom_tat_lech_so"]) - 8)
    if an:
        print(f"   ⚠ … và {an} cảnh báo khác chưa in (kiểm cả kho: python3 tools/tom_tat_endnote_vi.py --kiem EBM-Dashboards)")
    thieu = bc.get("tham_khao_chua_tom_tat") or []
    if thieu:
        print(f"   ℹ Trích dẫn tham khảo CHƯA có tóm tắt máy: {len(thieu)} — cần một phiên Claude soạn vào "
              f"{tt.TEP_TOM_TAT_ABS} (máy không tự sinh): " + ", ".join(thieu[:8]) + (" …" if len(thieu) > 8 else ""))
    bo = bc.get("tham_khao_bo_qua") or []
    if bo:
        print(f"   ℹ Cố ý KHÔNG tóm tắt máy («bo_qua» trong {tt.TEP_TOM_TAT_ABS}): {len(bo)} — giữ nguyên, KHÔNG soạn đè: "
              + ", ".join(bo[:8]) + (" …" if len(bo) > 8 else ""))
    return bc


def chay_tom_tat_thu_vien(endnote, dash_goc: Path, kho: Path | None, ap_dung: bool, tt=None, bo_qua=None) -> dict | None:
    """Tóm tắt máy cho bài trong thư viện KHÔNG thuộc dashboard nào (24/10/2026, `tom_tat_endnote_vi.ghi_thu_vien`). In tổng
    kết; lỗi ⇒ dòng ✗, trả None. Chạy khô ⇒ dòng mở bằng «ℹ», không bằng «✓»."""
    try:
        tt = tt or _nap_tom_tat()
        kho_tt = tt.nap_tom_tat_abstract(dash_goc)
        bc = tt.ghi_thu_vien(endnote, dashboards=sorted(dash_goc.glob("WebDashboard_*.html")), kho=kho, ap_dung=ap_dung,
                             doc_data=_nap_doc_data(), tom_tat_abs=kho_tt, bo_qua=bo_qua)
    except (RuntimeError, OSError, ValueError, sqlite3.Error) as e:
        print(f"✗ Tóm tắt thư viện (Abstract): {type(e).__name__}: {e} — chưa ghi gì sau lỗi này"[:300])
        return None
    print(f"{'✓' if ap_dung else 'ℹ Chạy khô ·'} Tóm tắt thư viện (Abstract): {bc['muc_kho']} mục kho ngoài dashboard · "
          f"{bc['co_ban_ghi']} có bản ghi · {'đã ghi ' + str(bc['da_ghi']) if ap_dung else 'sẽ ghi ' + str(bc['se_ghi'])} · "
          f"không đổi {bc['khong_doi']} · thuộc dashboard (để bước --tom-tat-vi) {bc['thuoc_dashboard']}"
          + (f" · sao lưu trước khi ghi: {bc['sao_luu']}" if bc.get("sao_luu") else ""))
    for ten, nhan in (("khong_co_ban_ghi", "Không thấy bản ghi trong thư viện"),
                      ("bo_qua_theo_bac_si", "⊘ Không ghi (bác sĩ đã loại/đã bỏ vào thùng rác)")):
        ds = bc.get(ten) or []
        if ds:
            print(f"   {nhan}: {len(ds)} — " + "; ".join(ds[:8]) + (" …" if len(ds) > 8 else ""))
    for loi in bc["loi"][:8] + bc["tom_tat_lech_so"][:8]:
        print(f"   ⚠ {loi}")
    an = max(0, len(bc["loi"]) - 8) + max(0, len(bc["tom_tat_lech_so"]) - 8)
    if an:
        print(f"   ⚠ … và {an} cảnh báo khác chưa in (--json để xem đủ)")
    return bc


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    ap.add_argument("--file", nargs="*", default=[], help="dashboard WebDashboard_*.html")
    ap.add_argument("--tat-ca", action="store_true", help="mọi dashboard trong EBM-Dashboards/")
    ap.add_argument("--de-tai", metavar="MA_DE_TAI",
                    help="nạp danh mục trích dẫn của MỘT đề tài nghiên cứu (medical-ebm-automation/exports/<mã>/"
                         "DANH_MUC_TRICH_DAN_<mã>.json) vào nhóm «NC · …»; KHÔNG ghi tóm tắt tiếng Việt (chạy khô mặc định)")
    ap.add_argument("--ap-dung", action="store_true", help="nạp thật vào EndNote (mặc định chạy khô)")
    ap.add_argument("--ten-nhom", help="đặt tên nhóm thay cho câu hỏi lâm sàng (chỉ khi một --file)")
    ap.add_argument("--xuat-xml", help="chỉ ghi tệp XML để nhập tay (máy không phải Mac)")
    ap.add_argument("--kho-toan-van", help="thư mục toan_van_oa (mặc định: toan_van_oa CẠNH dashboard của --file, rồi "
                                           "EBM-Dashboards/toan_van_oa; không thấy kho ⇒ --ap-dung bị từ chối)")
    ap.add_argument("--ghi-cau-hinh", metavar="THU_VIEN_ENL", help="ghi thư viện chính vào ~/.ebm-endnote.json")
    ap.add_argument("--ung-dung", default=UNG_DUNG_MAC_DINH, help="tên ứng dụng EndNote (đi cùng --ghi-cau-hinh)")
    ap.add_argument("--im-khi-chua-cau-hinh", action="store_true",
                    help="máy chưa cấu hình/không phải Mac thì in một dòng ⚪ và trả 0 (dùng trong bộ năm)")
    ap.add_argument("--gan-kho", action="store_true",
                    help="gắn PDF trong kho vào bản ghi ĐÃ có trong thư viện cùng PMID (không cần dashboard)")
    ap.add_argument("--pmid", nargs="*", help="cùng --gan-kho: chỉ xét các PMID này")
    ap.add_argument("--tom-tat-vi", action="store_true",
                    help="chỉ ghi/làm mới TÓM TẮT THỰC HÀNH tiếng Việt vào trường Abstract (cùng --file/--tat-ca; "
                         "abstract gốc giữ dưới dấu phân cách; chạy khô mặc định)")
    ap.add_argument("--tom-tat-thu-vien", action="store_true",
                    help="ghi tóm tắt máy (kho tom-tat-abstract-vi.json) vào Abstract của bài trong thư viện KHÔNG thuộc "
                         "dashboard nào (không đi cùng --file/--tat-ca; chạy khô mặc định)")
    ap.add_argument("--khong-tom-tat", action="store_true",
                    help="nạp --ap-dung mà KHÔNG ghi tóm tắt tiếng Việt (mặc định nạp xong thì ghi)")
    ap.add_argument("--chi-khi-dang-mo", action="store_true",
                    help="EndNote chưa mở đúng thư viện thì in ⚪ và trả 0 — KHÔNG tự mở EndNote (công cụ khác gọi)")
    ap.add_argument("--xac-nhan-cau-hinh-hong", action="store_true",
                    help="cùng --ghi-cau-hinh: cho ghi đè tệp cấu hình HỎNG (giữ bản .hong-<ngày giờ> trước)")
    ap.add_argument("--chua-xac-minh", action="store_true",
                    help="cổng liêm chính CHƯA PASS (bước ⑧ truyền): khối ĐỌC NHANH ghi «CHƯA xác minh nguồn sống»")
    ap.add_argument("--loai-tru", metavar="DOI_HOAC_PMID",
                    help="khai MỘT định danh bác sĩ không muốn nạp lại vào khoá «bo_qua» của ~/.ebm-endnote.json "
                         "(cần --ly-do; chạy khô mặc định, --ap-dung mới ghi, sao lưu trước — agent chỉ ghi khi bác sĩ yêu cầu)")
    ap.add_argument("--ly-do", help="cùng --loai-tru: lý do của bác sĩ (bắt buộc)")
    ap.add_argument("--cho-vao-nhom", nargs="?", const="", metavar="TEN_NHOM",
                    help="hàng chờ đưa vào nhóm ĐÃ có (post không cộng thêm được — đo 24/10/2026): liệt kê + dọn bài đã vào "
                         "nhóm; có tên ⇒ EndNote chỉ hiện các bài chờ của nhóm đó để bác sĩ kéo vào (chạy riêng)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    if a.de_tai is not None and (a.file or a.tat_ca or a.gan_kho or a.tom_tat_vi or a.tom_tat_thu_vien or a.ghi_cau_hinh
                                 or a.loai_tru is not None or a.cho_vao_nhom is not None):
        print("✗ --de-tai không đi cùng --file/--tat-ca/--gan-kho/--tom-tat-vi/--tom-tat-thu-vien/--ghi-cau-hinh/--loai-tru/"
              "--cho-vao-nhom")
        return MA_THAM_SO

    if a.cho_vao_nhom is not None:
        if a.file or a.tat_ca or a.gan_kho or a.xuat_xml or a.tom_tat_vi or a.ghi_cau_hinh or a.loai_tru or a.tom_tat_thu_vien:
            print("✗ --cho-vao-nhom chạy riêng")
            return MA_THAM_SO
        return chay_cho_vao_nhom(a.cho_vao_nhom)

    if a.ly_do is not None and a.loai_tru is None:
        print("✗ --ly-do chỉ đi cùng --loai-tru")
        return MA_THAM_SO
    if a.loai_tru is not None:
        if a.file or a.tat_ca or a.gan_kho or a.xuat_xml or a.tom_tat_vi or a.ghi_cau_hinh:
            print("✗ --loai-tru chạy riêng (không đi cùng --file/--tat-ca/--gan-kho/--xuat-xml/--tom-tat-vi/--ghi-cau-hinh)")
            return MA_THAM_SO
        try:
            kq = them_loai_tru(a.loai_tru, a.ly_do or "", ap_dung=a.ap_dung)
        except ValueError as e:
            print(f"✗ {e}")
            return MA_THAM_SO
        except KhongChayDuoc as e:
            print(f"✗ {e}")
            return MA_KHONG_CHAY
        muc = kq["muc"]
        nhan = _nhan_dinh_danh(muc.get("pmid"), muc.get("doi"))
        if kq["trang_thai"] == "da_co":
            print(f"ℹ {nhan} đã có trong danh sách loại trừ («{muc.get('ly_do')}», {muc.get('ngay')}) — không ghi gì.")
        elif kq["trang_thai"] == "se_them":
            print(f"ℹ Chạy khô · sẽ thêm vào «{KHOA_LOAI_TRU}» của {CAU_HINH}: {json.dumps(muc, ensure_ascii=False)}\n"
                  "  Thêm --ap-dung để ghi (agent chỉ ghi khi bác sĩ yêu cầu).")
        else:
            print(f"✓ Đã thêm {nhan} vào danh sách loại trừ («{muc['ly_do']}», {muc['ngay']}) · sao lưu: {kq['sao_luu']}")
            print("  Bản ghi đang có trong thư viện (nếu có) KHÔNG bị xoá — chuyển vào thùng rác là thao tác của bác sĩ.")
        if a.json:
            print(json.dumps(kq, ensure_ascii=False, indent=2))
        return MA_OK

    if a.ghi_cau_hinh:
        try:
            ch = ghi_cau_hinh(a.ghi_cau_hinh, a.ung_dung, xac_nhan_hong=a.xac_nhan_cau_hinh_hong)
        except KhongChayDuoc as e:
            print(f"✗ {e}")
            return MA_KHONG_CHAY
        except ValueError as e:
            print(f"✗ {e}")
            return MA_THAM_SO
        if ch.get("ban_hong"):
            print(f"⚠ Tệp cấu hình cũ HỎNG — đã giữ nguyên bản tại {ch['ban_hong']} (bảng nhóm cũ cứu tay từ đó).")
        print(f"✓ Đã ghi {CAU_HINH}: thư viện {ch['thu_vien']} · ứng dụng {ch['ung_dung']}")
        if not _la_mac():  # DN-02: cấu hình chỉ có tác dụng ở nơi điều khiển được EndNote
            print(f"⚠ Máy này không phải macOS — cấu hình vừa ghi KHÔNG có tác dụng ở đây (công cụ chỉ điều khiển EndNote "
                  f"bằng AppleScript trên Mac). Ở máy này dùng: `{LENH_XUAT_XML}` rồi nhập tay (File → Import).")
        return MA_OK

    dash_goc = _tim_dash_goc()
    files = [Path(f) for f in a.file]
    doc_data = None  # None = đọc khối DATA của dashboard (kiem_cheo_ngu_nghia.doc_data)
    if a.de_tai is not None:
        exports = _tim_exports()
        if exports is None:
            print("✗ không thấy thư mục medical-ebm-automation/exports/ (worktree/bản sao trần?) — chạy từ cây OneDrive")
            return MA_KHONG_CHAY
        try:
            data_de_tai, gia = doc_de_tai(a.de_tai, exports)
        except ValueError as e:
            print(f"✗ {e}")
            return MA_THAM_SO
        except KhongChayDuoc as e:
            print(f"✗ {e}")
            return MA_KHONG_CHAY

        def doc_data(_p: Path) -> dict:
            return data_de_tai

        files = [gia]
        # Bác sĩ dặn 25/10/2026: trích dẫn của đề tài KHÔNG cần tóm tắt chi tiết tiếng Việt, nhưng phải có toàn văn ⇒ không
        # chạy bước tóm tắt; PDF trong kho chung vẫn được đính/gắn như mọi chủ đề.
        a.khong_tom_tat = True
        print(f"Đề tài {a.de_tai}: {len(data_de_tai['items'])} trích dẫn trong danh mục · không ghi tóm tắt tiếng Việt")
    if a.tat_ca:
        if dash_goc is None:
            print("✗ không thấy thư mục EBM-Dashboards/ (bản sao trần?) — dùng --file")
            return MA_KHONG_CHAY
        files += sorted(dash_goc.glob("WebDashboard_*.html"))
    if a.tom_tat_thu_vien and (files or a.gan_kho or a.xuat_xml or a.tom_tat_vi):
        print("✗ --tom-tat-thu-vien chạy riêng (không đi cùng --file/--tat-ca/--gan-kho/--xuat-xml/--tom-tat-vi)")
        return MA_THAM_SO
    if a.tom_tat_thu_vien and dash_goc is None:
        print("✗ --tom-tat-thu-vien cần thư mục EBM-Dashboards/ (kho tóm tắt máy + ngữ cảnh mọi dashboard)")
        return MA_KHONG_CHAY
    if not files and not a.gan_kho and not a.tom_tat_thu_vien:
        ap.print_usage()
        return MA_THAM_SO
    if a.gan_kho and (files or a.xuat_xml):
        print("✗ --gan-kho không đi cùng --file/--tat-ca/--xuat-xml")
        return MA_THAM_SO
    if a.tom_tat_vi and (a.gan_kho or a.xuat_xml or not files):
        print("✗ --tom-tat-vi cần --file/--tat-ca và không đi cùng --gan-kho/--xuat-xml")
        return MA_THAM_SO
    if a.ten_nhom and len(files) != 1:
        print("✗ --ten-nhom chỉ dùng với đúng một --file")
        return MA_THAM_SO
    # Đề tài: tệp giả không có thư mục thật — không đoán `toan_van_oa` cạnh thư mục đang đứng, dùng kho chung.
    kho = xac_dinh_kho(a.kho_toan_van, dash_goc, [] if a.de_tai is not None else files)

    if a.xuat_xml:
        # Đường cho máy không phải Mac: một tệp XML để nhập tay; không đính PDF (không có đường vào thư viện).
        # Danh sách loại trừ của bác sĩ áp cả ở đây (18/10/2026); cấu hình hỏng ⇒ không ghi tệp nhập.
        try:
            loai_tru = doc_loai_tru()
        except CauHinhHong as e:
            print(f"✗ {e} — không ghi tệp XML.")
            return MA_KHONG_CHAY
        doc = doc_data or _nap_doc_data()
        tat_ca: list[dict] = []
        thieu: list[str] = []
        bo_lt: list[str] = []
        for f in files:
            dd = []
            for d in trich_dinh_danh(doc(f) or {}):
                if muc_loai_tru(loai_tru, d.get("pmid"), d.get("doi")):
                    bo_lt.append(_nhan_dinh_danh(d.get("pmid"), d.get("doi")))
                else:
                    dd.append(d)
            co, th = lay_metadata(dd)
            thieu += th
            for _, m in co:
                if muc_loai_tru(loai_tru, m.get("pmid"), m.get("doi")):
                    bo_lt.append(_nhan_dinh_danh(m.get("pmid"), m.get("doi")))
                    continue
                tat_ca.append(dict(m, tu_khoa=[f"EBM: {khoa_chu_de(f)}"], ghi_chu=f"Từ {f.name}."))
        Path(a.xuat_xml).write_text(dung_xml(tat_ca), encoding="utf-8", newline="\n")
        print(f"✓ Đã ghi {a.xuat_xml}: {len(tat_ca)} bản ghi — EndNote: File → Import → «EndNote generated XML»."
              " Nhóm theo chủ đề: tạo Smart Group theo từ khoá «EBM: …».")
        if bo_lt:
            print(f"⊘ bỏ qua theo danh sách loại trừ của bác sĩ (không ghi vào tệp): {', '.join(bo_lt[:10])}")
        if thieu:
            print(f"⚠ Không lấy được metadata (không ghi vào tệp): {', '.join(thieu[:10])}")
        return MA_MOT_PHAN if thieu else MA_OK

    endnote = None
    try:
        # DN-02 (15/10/2026): xét NỀN TẢNG trước cấu hình — máy không phải Mac được chỉ thẳng sang --xuat-xml, không bị
        # bảo «chạy --ghi-cau-hinh» cho một thư viện công cụ không bao giờ điều khiển được.
        if not _la_mac():
            raise KhongChayDuoc(THONG_DIEP_KHONG_PHAI_MAC)
        ch = doc_cau_hinh()
        if ch is None:
            hong = ly_do_cau_hinh_hong()
            if hong:  # TT-09: hỏng ≠ vắng — nói rõ, không dạy ghi đè
                raise CauHinhHong(f"tệp cấu hình hỏng — xem {CAU_HINH} ({hong}); sửa tay, hoặc khai lại bằng "
                                  "--ghi-cau-hinh \"<đường dẫn .enl>\" --xac-nhan-cau-hinh-hong (giữ bản .hong-<ngày giờ>)")
            raise KhongChayDuoc("chưa cấu hình thư viện EndNote — chạy --ghi-cau-hinh "
                                f"\"<đường dẫn .enl>\" ({CAU_HINH})")
        thu_vien = Path(ch["thu_vien"])
        if not thu_vien.is_file():
            raise KhongChayDuoc(f"thư viện đã cấu hình không còn tồn tại: {thu_vien}")
        endnote = EndNoteMac(ch["ung_dung"], thu_vien)
        # Xét kho SAU nền tảng/cấu hình (máy không ghi được EndNote thì luật cũ — ⚪/mã 0 trong bộ năm — vẫn thắng) và TRƯỚC
        # bước có thể bật EndNote lên màn hình (không mở EndNote rồi mới từ chối).
        chan = chan_ghi_khi_thieu_kho(a, kho)
        if chan is not None:
            return chan
        if not endnote.dang_mo_dung_thu_vien():
            if a.chi_khi_dang_mo:  # công cụ khác gọi giữa chừng: không bao giờ tự bật EndNote lên màn hình bác sĩ
                print(f"⚪ EndNote chưa mở thư viện {thu_vien.name} — bỏ qua, lần nạp sau sẽ gắn.")
                return MA_OK
            if a.ap_dung:
                endnote.mo_thu_vien()
            else:
                print(f"⚪ EndNote chưa mở thư viện {thu_vien.name} — chạy khô không kiểm được bài đã có.")
                endnote = None
    except KhongChayDuoc as e:
        if a.im_khi_chua_cau_hinh:
            print(f"⚪ EndNote: bỏ qua — {e}")
            return MA_OK
        if a.ap_dung:
            print(f"✗ {e}")
            return MA_KHONG_CHAY
        print(f"⚪ {e} — chỉ lập kế hoạch.")
        endnote = None

    if a.gan_kho:
        if endnote is None:
            print("⚪ --gan-kho cần EndNote đang mở đúng thư viện — chưa gắn gì.")
            return MA_OK if a.chi_khi_dang_mo else MA_KHONG_CHAY
        try:
            bc = gan_kho(endnote, kho, a.pmid, a.ap_dung, doi_cua=doi_cua_pmid)
        except (RuntimeError, OSError) as e:
            print(f"✗ gắn toàn văn từ kho: {type(e).__name__}: {e}"[:300])
            return MA_KHONG_CHAY
        if not bc["kho_toan_van"]:
            print("⚠ Không thấy kho toàn văn — CHƯA XÉT PDF; chỉ đường bằng --kho-toan-van")
        else:
            gan = bc.get("gan_them_pdf", bc.get("se_gan_pdf", 0))
            phu = " · ".join(x for x in (f"«PMID: n» {bc['khop_pmid_tien_to']}" if bc.get("khop_pmid_tien_to") else "",
                                          f"khớp DOI {bc['khop_doi']}" if bc.get("khop_doi") else "") if x)
            print(f"✓ EndNote · kho: {bc['pdf_trong_kho']} PMID có PDF · {bc['co_ban_ghi']} có bản ghi trong thư viện"
                  f"{f' ({phu})' if phu else ''} · {'gắn thêm' if a.ap_dung else 'sẽ gắn'} {gan}")
            if bc.get("doi_khong_do_duoc"):
                print(f"   ⚪ chưa khớp được theo DOI (không tra được DOI: {bc['doi_khong_do_duoc']}) — chạy lại sau")
        if a.json:
            print(json.dumps(bc, ensure_ascii=False, indent=2))
        return MA_OK

    # Danh sách loại trừ của bác sĩ (18/10/2026). Cấu hình hỏng tới được đây CHỈ ở lượt chạy khô lập kế hoạch (--ap-dung đã
    # dừng ở khối trên với mã 2, hoặc ⚪/mã 0 trong bộ năm) ⇒ nói rõ kế hoạch chưa trừ danh sách, không coi là rỗng.
    try:
        loai_tru = doc_loai_tru()
    except CauHinhHong as e:
        if a.ap_dung:  # phòng thủ — không bao giờ nhập khi không đọc được danh sách loại trừ
            print(f"✗ {e} — không nhập gì.")
            return MA_KHONG_CHAY
        print(f"⚪ {e} — kế hoạch dưới đây CHƯA trừ danh sách loại trừ của bác sĩ.")
        loai_tru = {"doi": {}, "pmid": {}}

    def bo_qua_tom_tat():
        return ham_bo_qua(loai_tru, doc_thung_rac_an_toan(endnote)[0] if endnote is not None else None)

    if a.tom_tat_thu_vien:
        if endnote is None:
            print("⚪ --tom-tat-thu-vien cần EndNote đang mở đúng thư viện — chưa ghi gì.")
            return MA_OK if a.chi_khi_dang_mo else MA_KHONG_CHAY
        bc = chay_tom_tat_thu_vien(endnote, dash_goc, kho, a.ap_dung, bo_qua=bo_qua_tom_tat())
        if bc is not None and not a.ap_dung:
            print("Chạy khô — chưa ghi tóm tắt nào. Thêm --ap-dung để ghi.")
        if a.json:
            print(json.dumps(bc, ensure_ascii=False, indent=2, default=str))
        return MA_KHONG_CHAY if bc is None or bc.get("loi") else MA_OK

    if a.tom_tat_vi:
        if endnote is None:
            print("⚪ --tom-tat-vi cần EndNote đang mở đúng thư viện — chưa ghi gì.")
            return MA_OK if a.chi_khi_dang_mo else MA_KHONG_CHAY
        bc = chay_tom_tat(endnote, files, kho, a.ap_dung, chua_xac_minh=a.chua_xac_minh, bo_qua=bo_qua_tom_tat())
        if bc is not None and not a.ap_dung:
            print("Chạy khô — chưa ghi tóm tắt nào. Thêm --ap-dung để ghi.")
        if a.json:
            print(json.dumps(bc, ensure_ascii=False, indent=2, default=str))
        return MA_KHONG_CHAY if bc is None or bc.get("loi") else MA_OK

    tien_to = TIEN_TO_NHOM_DE_TAI if a.de_tai is not None else TIEN_TO_NHOM
    ket_qua = nap_nhieu(files, endnote=endnote, ap_dung=a.ap_dung, kho=kho, ten_nhom=a.ten_nhom, loai_tru=loai_tru,
                        doc_data=doc_data, tien_to=tien_to)
    if a.ap_dung and endnote is not None and not a.khong_tom_tat:
        # mỗi trích dẫn vừa nạp có ngay tóm tắt thực hành tiếng Việt
        chay_tom_tat(endnote, files, kho, True, chua_xac_minh=a.chua_xac_minh, bo_qua=bo_qua_tom_tat())
    if a.ap_dung and endnote is not None and any(b.get("thieu_toan_van") for b in ket_qua):
        nguon = "--pmid <PMID…>" if a.de_tai is not None else "--file <dashboard>"
        print("Toàn văn còn thiếu — làn kế tiếp, rồi chạy lại lệnh này để gắn PDF mới vào nhóm:\n"
              f"  1. python3 tools/gom_toan_van_dashboard.py {nguon} --unpaywall   (bản truy cập mở)\n"
              "  2. python3 tools/doc_toan_van_co_nguoi.py --pmid <PMID…>   (bài thuê bao: làn Chrome có uỷ quyền,\n"
              "     bác sĩ tự đăng nhập/vượt chặn; công cụ này không tải bài thuê bao)\n"
              f"  3. hoặc trong EndNote: chọn nhóm «{tien_to}…» → References → Find Full Text (quyền truy cập của bác sĩ).")
    if not a.ap_dung:
        print("Chạy khô — chưa nhập gì. Thêm --ap-dung để nạp thật.")
    if a.json:
        print(json.dumps(ket_qua, ensure_ascii=False, indent=2, default=str))
    return ma_thoat_nap(ket_qua)


def ma_thoat_nap(ket_qua: list[dict]) -> int:
    """Mã thoát của lượt nạp: lỗi hoặc NHẬP HỤT ⇒ 2 (không nạp được — không phải «xong một phần»); thiếu metadata ⇒ 1."""
    if any(b.get("loi") or b.get("nhap_hut") for b in ket_qua):
        return MA_KHONG_CHAY
    return MA_MOT_PHAN if any(b.get("khong_lay_duoc") for b in ket_qua) else MA_OK


if __name__ == "__main__":
    sys.exit(main())
