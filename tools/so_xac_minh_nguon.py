#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SỔ XÁC MINH NGUỒN — tích luỹ bằng chứng đã xác minh, chịu được mạng chập chờn.

VÌ SAO CÓ (12/08/2026)
======================
Đo thật trên máy Windows: chạy `verify_dashboard.py --online` BỐN lần liên tiếp
trên CÙNG một dashboard, không sửa gì ở giữa, cho 13 → 3 → 6 → 1 lỗi cứng. Nguyên
nhân là DNS của máy chỉ trỏ một server đang chập chờn (Europe PMC và DailyMed
phân giải 0/5 lần), KHÔNG phải nguồn chứng cứ có vấn đề.

Hệ quả nghiêm trọng: **không có lần chạy nào kết luận được về độ tin cậy**, vì
cổng không nhớ gì giữa các lần — mỗi lần lại hỏi mạng từ đầu, và mạng kém thì
không bao giờ đủ trong MỘT lượt.

NGUYÊN TẮC AN TOÀN (đọc kỹ trước khi sửa)
==========================================
Sổ này KHÁC HẲN việc "chạy lại nhiều lần rồi lấy lần ít lỗi nhất làm bằng chứng"
— cách đó là tự lừa mình và `verify_dashboard.py` đã cảnh báo chống lại. Khác ở
chỗ:

  1. **Chỉ ghi THÀNH CÔNG.** Một lần xác minh thành công là bằng chứng dương tính
     về CHÍNH nguồn đó: PMID này có thật, tiêu đề này khớp. Thất bại thì KHÔNG
     ghi gì cả — "chưa xác minh được" vĩnh viễn không được biến thành "đã xác
     minh". Không có đường nào trong file này ghi một mục là hợp lệ dựa trên việc
     mạng hỏng.
  2. **Ghi từng mục, không ghi kết quả tổng của một lượt chạy.** Lấy "lần ít lỗi
     nhất" là suy ra chất lượng của TOÀN BỘ gói từ một lượt may mắn. Ở đây mỗi
     PMID/DOI/URL có bằng chứng riêng, kèm thời điểm và nguồn xác minh.
  3. **Có hạn dùng, hai mức khác nhau** — điểm an toàn quan trọng nhất:
       • sự TỒN TẠI + metadata: gần như bất biến → hạn dài (mặc định 180 ngày);
       • trạng thái RÚT BÀI: thay đổi bất cứ lúc nào, một bài đang tốt hôm nay
         có thể bị rút ngày mai → hạn NGẮN (mặc định 30 ngày).
     Trộn hai thứ này vào một hạn dùng là lỗi an toàn: sẽ có ngày sổ nói "đã xác
     minh" về một bài đã bị rút từ lâu.
  4. **Không bao giờ thay thế `--online`.** Sổ chỉ trả lời "mục này đã từng được
     xác minh lúc nào, bằng nguồn nào". Quyết định phát hành vẫn là của cổng và
     của bác sĩ.

Dùng
====
    # gom mọi nguồn trong dashboard, xác minh những mục CHƯA có hoặc đã hết hạn
    python tools/so_xac_minh_nguon.py --quet EBM-Dashboards/WebDashboard_*.html

    # chạy lại nhiều vòng cho mạng chập chờn — mỗi vòng nhặt thêm được một ít
    python tools/so_xac_minh_nguon.py --quet <file> --vong 3

    # xem độ phủ hiện tại, không gọi mạng
    python tools/so_xac_minh_nguon.py --bao-cao

Mã thoát: 0 = mọi nguồn của phạm vi đã quét đều còn hiệu lực · 1 = còn thiếu
· 2 = có nguồn ĐÃ BỊ RÚT (nghiêm trọng, phải xử lý trước khi dùng).
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import importlib.util
import json
import re
import sys
from pathlib import Path


def _chuyen_sang_venv() -> None:
    """Tự chạy lại bằng venv EBM khi interpreter hiện tại thiếu thư viện.

    Cùng cơ chế đã vá cho tools/kiem_nguon_that.py. Ở ĐÂY hậu quả nặng hơn: thiếu
    `python-dotenv` không làm công cụ chết mà làm bước KIỂM RÚT BÀI im lặng trả
    rỗng, nên 36 PMID trong sổ chưa từng được kiểm lần nào.

    So bằng `sys.prefix`, TUYỆT ĐỐI không dùng `Path(...).resolve()`:
    `~/.ebm-venv/bin/python` là symlink → python3.14 → chính python hệ thống, nên
    resolve() hai bên ra CÙNG một đường dẫn và rào sẽ thoát sớm mà không chuyển.
    """
    import os
    if os.environ.get("_EBM_DA_CHUYEN_VENV"):
        return
    try:
        import dotenv  # noqa: F401, PLC0415
        return
    except ImportError:
        pass
    goc = Path.home() / ".ebm-venv"
    venv = goc / "bin/python"
    if not venv.exists() or Path(sys.prefix) == goc:
        return
    os.environ["_EBM_DA_CHUYEN_VENV"] = "1"
    os.execv(str(venv), [str(venv), *sys.argv])


# CHỈ chuyển venv khi chạy TRỰC TIẾP. Nếu để ở mức module, một tool khác chỉ cần
# `import` file này là os.execv() THAY THẾ luôn tiến trình của nó — mất sạch việc
# đang làm. (Đã vấp đúng lỗi này khi tự kiểm bản vá, 12/08/2026.)
if __name__ == "__main__":
    _chuyen_sang_venv()

# Windows: stdout mặc định là cp1252 → mọi print() tiếng Việt hoặc ký hiệu (✓ ⚠ →)
# ném UnicodeEncodeError và GIẾT tiến trình, thường SAU KHI công việc đã xong. Đo thật
# ngày 12/08/2026 trên dây chuyền cập nhật chứng cứ: bản Word 82 KB đã ghi ra đĩa nhưng
# tool thoát mã 1 ở đúng dòng print cuối ⇒ caller đọc mã thoát, tưởng hỏng, bỏ luôn 2
# bước sau. Cùng lớp lỗi đã vá cho tools/vietnamize/.
# VÁ 13/08/2026 — thêm `line_buffering=True`. Khi chuyển hướng ra file/pipe (chạy nền,
# nohup, hook), Python đệm stdout theo KHỐI ⇒ tiến trình chạy 12 phút mà log vẫn 0 byte.
# Đo thật hôm nay: vòng quét sống, chỉ 5,3 giây CPU trên 12 phút (đang chờ mạng vì NCBI
# chặn) nhưng KHÔNG hiện một dòng nào ⇒ trông y hệt như treo. Với một công cụ đi mạng
# chậm, "không thấy gì" và "đã chết" phải phân biệt được, nếu không người dùng sẽ giết
# nhầm một lượt quét đang chạy đúng.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass


REPO = Path(__file__).resolve().parents[1]
DASH = REPO / "EBM-Dashboards"
SO = DASH / ".so-xac-minh-nguon.json"

# Hạn dùng — xem nguyên tắc 3 ở docstring. KHÔNG gộp hai giá trị này làm một.
HAN_TON_TAI_NGAY = 180
HAN_RUT_BAI_NGAY = 30


def _nap_verify_dashboard():
    """Nạp verify_dashboard.py để dùng lại đúng bộ xác minh của cổng.

    Cố ý KHÔNG viết lại logic gọi PubMed/Crossref: hai bản sẽ trôi khỏi nhau và
    sổ sẽ nói khác cổng — đúng lớp lỗi 'ba bản tool lệch nhau' đã gặp.
    """
    p = DASH / "tools" / "verify_dashboard.py"
    spec = importlib.util.spec_from_file_location("vd_for_so", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def doc_so() -> dict:
    if not SO.exists():
        return {"phien_ban": 1, "muc": {}}
    try:
        return json.loads(SO.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"⚠ Sổ hỏng, bắt đầu lại từ đầu ({e})", file=sys.stderr)
        return {"phien_ban": 1, "muc": {}}


def ghi_so(so: dict) -> None:
    SO.write_text(json.dumps(so, ensure_ascii=False, indent=2, sort_keys=True),
                  encoding="utf-8")


def _hom_nay() -> dt.date:
    return dt.date.today()


def _tuoi_ngay(iso: str | None) -> int | None:
    if not iso:
        return None
    try:
        return (_hom_nay() - dt.date.fromisoformat(iso[:10])).days
    except ValueError:
        return None


def con_hieu_luc(ban_ghi: dict) -> tuple[bool, str]:
    """Mục đã xác minh có còn dùng được không? Trả (còn, lý do nếu không)."""
    if ban_ghi.get("da_rut"):
        return False, "ĐÃ BỊ RÚT"
    tuoi = _tuoi_ngay(ban_ghi.get("xac_minh_luc"))
    if tuoi is None:
        return False, "không đọc được ngày xác minh"
    if tuoi > HAN_TON_TAI_NGAY:
        return False, f"xác minh đã {tuoi} ngày (hạn {HAN_TON_TAI_NGAY})"
    tuoi_rut = _tuoi_ngay(ban_ghi.get("kiem_rut_luc"))
    # MỞ RỘNG 14/08/2026 (vòng 4) — DOI cũng phải có dấu vết kiểm rút bài.
    # Trước đó chỉ `pmid` bị đòi, nên 540 DOI trong kho đứng ở trạng thái "còn hiệu
    # lực" mà CHƯA TỪNG được kiểm rút bài lần nào. Đó là một lời bảo đảm rỗng, và nó
    # đã bị chạm vào thật: một mục đổi từ PMID đã rút sang DOI của CHÍNH bài đã rút
    # thì cổng thôi cảnh báo. Một định danh đi kèm bảo đảm nào thì phải chịu đúng
    # phép kiểm của bảo đảm đó — không phụ thuộc nó được ghi bằng kiểu nào (BH24).
    co_doi = ban_ghi.get("loai") == "doi" or ban_ghi.get("doi_rut_tu_url")
    if ban_ghi.get("loai") == "pmid" or co_doi:
        if tuoi_rut is None:
            return False, "chưa kiểm rút bài lần nào"
        if tuoi_rut > HAN_RUT_BAI_NGAY:
            return False, f"kiểm rút bài đã {tuoi_rut} ngày (hạn {HAN_RUT_BAI_NGAY})"
    return True, ""


def nguon_da_rut(ten_file: str) -> list[dict]:
    """Nguồn của MỘT dashboard đã được sổ ghi nhận là ĐÃ RÚT / có quan ngại.

    Thêm 14/08/2026 (vòng lặp kiểm tra–hoàn thiện, vòng 2). Trước đó việc phát hiện
    rút bài chỉ sống trong sổ và chỉ nói ra khi bác sĩ gõ `--bao-cao`; cổng phát hành
    `verify_dashboard.py` CỐ Ý không kết luận trạng thái rút bài, còn trang bản đọc
    thì im lặng hoàn toàn. Kết quả: PMID 30267080 (đã rút 2019, JAMA Oncology) nằm
    trong ViemGanB_DieuTri suốt mà không chỗ nào bác sĩ mở ra thấy được.

    BẤT ĐỐI XỨNG BẮT BUỘC — chỗ dễ sai nhất:
      • Có bản ghi `da_rut` ⇒ DƯƠNG TÍNH, phát ra. Đó là kết luận đã được một nguồn
        SỐNG xác nhận (xem luật gộp ở `app/sources/retraction_chain.py`).
      • VẮNG MẶT trong sổ ⇒ KHÔNG có nghĩa là sạch. Hàm này KHÔNG BAO GIỜ trả tín
        hiệu "đã kiểm, không sao" — nó chỉ trả những gì đã bị bắt. Biến im lặng
        thành lời bảo đảm chính là BH08/BH27, hai bài học đắt nhất của kho này.

    Không phụ thuộc mạng: chỉ đọc sổ, chạy được ở mọi nơi mọi lúc.
    """
    muc = (doc_so() or {}).get("muc", {}) or {}
    ra: list[dict] = []
    for khoa, bg in sorted(muc.items()):
        if not bg.get("da_rut"):
            continue
        if ten_file not in (bg.get("cac_dashboard") or []):
            continue
        ra.append({
            "khoa": khoa,
            "loai": bg.get("loai", ""),
            "gia_tri": bg.get("gia_tri", ""),
            "tinh_trang": bg.get("ghi_chu_rut") or "retracted",
            "tieu_de": bg.get("tieu_de") or "",
            "kiem_luc": (bg.get("kiem_rut_luc") or "")[:10],
            "nguon": bg.get("nguon_xac_minh") or "",
            "rut_va_thay": bool(bg.get("rut_va_thay")),
            "thong_bao": bg.get("thong_bao_rut_doi") or "",
        })
    return ra


def dinh_danh_da_rut(cac_dinh_danh: list[str]) -> list[dict]:
    """Dương tính rút bài trong MỘT DANH SÁCH định danh — không cần ánh xạ dashboard.

    Vì sao có (PHA 4 LÔ E, 15/08/2026 — lỗ hổng tìm ra bằng fixture): `nguon_da_rut`
    lọc theo `cac_dashboard`, nên một dashboard MỚI trích đúng DOI đã rút mà chưa
    từng qua vòng quét A4 sẽ đi qua cổng sạch sẽ. Hàm này tra THẲNG từng định danh
    vào sổ: sổ đã biết bài đó bị rút thì bất kỳ file nào trích nó đều phải nghe.
    Giữ nguyên bất đối xứng: chỉ trả DƯƠNG TÍNH; vắng mặt ≠ sạch (BH08/BH27).
    """
    muc = (doc_so() or {}).get("muc", {}) or {}
    ra: list[dict] = []
    for dd in cac_dinh_danh:
        dd = str(dd).strip()
        for khoa in (f"pmid:{dd}", f"doi:{dd.lower()}"):
            bg = muc.get(khoa)
            if bg and bg.get("da_rut"):
                ra.append({
                    "khoa": khoa,
                    "loai": bg.get("loai", ""),
                    "gia_tri": bg.get("gia_tri", ""),
                    "tinh_trang": bg.get("ghi_chu_rut") or "retracted",
                    "tieu_de": bg.get("tieu_de") or "",
                    "kiem_luc": (bg.get("kiem_rut_luc") or "")[:10],
                    "nguon": bg.get("nguon_xac_minh") or "",
                    "rut_va_thay": bool(bg.get("rut_va_thay")),
                    "thong_bao": bg.get("thong_bao_rut_doi") or "",
                })
                break
    return ra


def gom_nguon(files: list[Path], vd) -> dict[str, set[str]]:
    """Gom mọi pmid/doi/url từ các dashboard. Trả {khoá: {file đã dùng}}."""
    nguon: dict[str, set[str]] = {}
    for f in files:
        try:
            html = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        db = vd.extract_data_block(html)
        if not db:
            continue
        for ch in vd.split_items(db):
            for loai in ("pmid", "doi", "url"):
                gt = vd.field(ch, loai)
                if not gt:
                    continue
                if loai == "pmid" and not vd.PMID_RE.match(gt):
                    continue
                if loai == "doi" and not vd.DOI_RE.match(gt):
                    continue
                if loai == "url" and not gt.startswith("http"):
                    continue
                nguon.setdefault(f"{loai}:{gt}", set()).add(f.name)
    return nguon


def dong_bo_lien_ket_dashboard(
    muc: dict[str, dict],
    nguon: dict[str, set[str]],
    ten_da_quet: set[str],
) -> int:
    """Đối soát liên kết nguồn↔dashboard trong đúng phạm vi vừa quét.

    Khi một citation bị loại hoặc thay bằng bản hợp lệ, bản cũ trong sổ không được
    tiếp tục khai dashboard đó đang sử dụng nguồn. Tuy nhiên ``--quet`` có thể chỉ
    nhận một vài dashboard, nên phải giữ nguyên liên kết tới các file KHÔNG thuộc
    lượt quét hiện tại; nếu gán thẳng từ ``nguon`` sẽ làm mất lịch sử của cả kho.
    """
    thay_doi = 0
    for khoa, ban_ghi in muc.items():
        cu = set(ban_ghi.get("cac_dashboard") or [])
        moi = (cu - ten_da_quet) | set(nguon.get(khoa, set()))
        moi_sap_xep = sorted(moi)
        if moi_sap_xep != sorted(cu):
            ban_ghi["cac_dashboard"] = moi_sap_xep
            thay_doi += 1
    return thay_doi


def xac_minh_mot(khoa: str, vd) -> dict | None:
    """Xác minh MỘT nguồn. Trả bản ghi khi THÀNH CÔNG, None khi không.

    None nghĩa là "chưa biết" — caller KHÔNG được ghi gì vào sổ. Đây là chỗ duy
    nhất quyết định điều gì được coi là đã xác minh, nên giữ nó thật hẹp.
    """
    loai, _, gt = khoa.partition(":")
    bay_gio = dt.datetime.now().isoformat(timespec="seconds")
    if loai == "pmid":
        ok, tieu_de, nam = vd.verify_pmid_online(gt)
        if ok is not True:
            return None
        return {"loai": "pmid", "gia_tri": gt, "xac_minh_luc": bay_gio,
                "tieu_de": tieu_de, "nam": nam, "nguon_xac_minh": "pubmed"}
    if loai == "doi":
        ok, mo_ta, *_ = _goi_linh_hoat(vd.verify_doi_online, gt)
        if ok is not True:
            return None
        return {"loai": "doi", "gia_tri": gt, "xac_minh_luc": bay_gio,
                "tieu_de": mo_ta, "nguon_xac_minh": "crossref"}
    if loai == "url":
        # VÁ 14/08/2026 — MỘT DOI GHI DƯỚI DẠNG URL VẪN LÀ DOI.
        # Trước đó mọi mục `url:` chỉ được kiểm "địa chỉ có phản hồi" (`http`), trong
        # khi mục `doi:` được xác minh METADATA qua Crossref. Nghĩa là cùng một nguồn,
        # chỉ khác CÁCH GHI, lại nhận hai mức bảo đảm khác hẳn nhau — và mức yếu hơn
        # không hề được nói ra. Đo thật: **17 định danh** là DOI viết dạng
        # `https://doi.org/10.…` nên đang bị hạ cấp xác minh.
        # Cùng họ với các lỗi hôm nay: hệ đưa ra một bảo đảm THẤP HƠN mức nó ngụ ý,
        # mà không ai được báo.
        m_doi = re.search(r"(?:doi\.org/|/doi/)(10\.\d{4,9}/\S+)", gt)
        if m_doi:
            ok, mo_ta, *_ = _goi_linh_hoat(vd.verify_doi_online, m_doi.group(1))
            if ok is True:
                return {"loai": "url", "gia_tri": gt, "xac_minh_luc": bay_gio,
                        "tieu_de": mo_ta, "nguon_xac_minh": "crossref",
                        "doi_rut_tu_url": m_doi.group(1)}
            # Crossref không phân giải được → LÙI về kiểm HTTP, đúng mức bảo đảm cũ.
            # Không tự hạ thành "không xác minh": HTTP vẫn là bằng chứng thật, chỉ yếu hơn.
        ok, mo_ta, *_ = _goi_linh_hoat(vd.verify_url_online, gt)
        if ok is not True:
            return None
        return {"loai": "url", "gia_tri": gt, "xac_minh_luc": bay_gio,
                "tieu_de": mo_ta, "nguon_xac_minh": "http"}
    return None


def _goi_linh_hoat(ham, gt):
    """Các hàm verify_* trả tuple độ dài khác nhau tuỳ phiên bản — chuẩn hoá."""
    kq = ham(gt)
    if isinstance(kq, tuple):
        return list(kq) + [None] * (3 - len(kq)) if len(kq) < 3 else list(kq)
    return [kq, "", None]


def kiem_rut_bai_theo_doi(muc: dict, nguon: dict, so: dict) -> None:
    """Tra rút bài cho các DOI (kể cả DOI ghi dạng URL) và ghi thẳng vào sổ.

    VÌ SAO CÓ (14/08/2026, vòng 4): chuỗi 3 tầng chỉ nhận PMID, nên **540 DOI trong
    kho CHƯA TỪNG được kiểm rút bài lần nào** — gần một nửa số định danh, và không
    một dòng nào nói ra điều đó.

    Điểm mù bị chạm vào ngay trong ngày: một mục trích PMID 30267080 (đã rút) được
    sửa thành trích DOI `10.1001/jamaoncol.2018.4070` — mà Crossref ghi rõ DOI đó
    CHÍNH LÀ bài đã rút (`updated-by: retraction`). Cổng vì thế thôi cảnh báo trong
    khi rủi ro còn nguyên: một đèn đỏ tắt đi mà nguy cơ không mất.

    Giữ nguyên luật bất đối xứng: chỉ ghi `da_rut` khi Crossref khẳng định; "không
    hỏi được" giữ trạng thái CHƯA kiểm, không bao giờ thành "sạch".
    """
    can = []
    for khoa, bg in muc.items():
        # Bản ghi ĐÃ đánh dấu rút bài trước đây bị bỏ qua vĩnh viễn, nên khi thêm một
        # trường mới (vd `rut_va_thay`) nó KHÔNG BAO GIỜ được ghi vào các bản ghi cũ —
        # cảnh báo cứ giữ nguyên câu chữ sai. Cho phép hỏi lại ĐÚNG MỘT LẦN khi thiếu
        # trường đó; đã có phán quyết rồi thì không hỏi lại nữa.
        if khoa not in nguon:
            continue
        if bg.get("da_rut") and "rut_va_thay" in bg:
            continue
        # DOI ghi dạng URL cũng là DOI — cùng lý lẽ của BH24.
        doi = bg.get("gia_tri") if bg.get("loai") == "doi" else bg.get("doi_rut_tu_url")
        if not doi:
            continue
        t = _tuoi_ngay(bg.get("kiem_rut_luc"))
        # Thiếu `rut_va_thay` ⇒ bản ghi có TRƯỚC khi phân biệt "rút bỏ hẳn" với "rút
        # rồi đăng lại bản sửa" ⇒ phải hỏi lại BẤT KỂ vừa kiểm hôm nay, nếu không câu
        # chữ sai sẽ đóng băng vĩnh viễn.
        if t is None or t > HAN_RUT_BAI_NGAY or "rut_va_thay" not in bg:
            can.append((khoa, doi))
    if not can:
        return

    mea = REPO / "medical-ebm-automation"
    if not (mea / "app" / "sources" / "crossref_retraction.py").exists():
        print(f"\n⚠ {len(can)} DOI CHƯA kiểm được rút bài: thiếu "
              f"app/sources/crossref_retraction.py — giữ nguyên trạng thái CHƯA kiểm.")
        return
    sys.path.insert(0, str(mea))
    try:
        from app.sources.crossref_retraction import CrossrefRetraction  # noqa: PLC0415
    except ImportError as e:
        print(f"\n⚠ {len(can)} DOI CHƯA kiểm được rút bài (thiếu thư viện: {e}) — "
              f"KHÔNG coi là sạch.")
        return

    print(f"\n── Tra rút bài cho {len(can)} DOI (Crossref) ──")
    import os
    kq = CrossrefRetraction(mailto=os.environ.get("NCBI_EMAIL", "")).check(
        [d for _k, d in can])
    bay_gio = dt.datetime.now().isoformat(timespec="seconds")
    chua = 0
    for khoa, doi in can:
        info = kq.get(doi) or {}
        tt = info.get("status", "")
        if tt in ("unknown_fetch_error", ""):
            chua += 1
            continue
        muc[khoa]["kiem_rut_luc"] = bay_gio
        muc[khoa]["ghi_chu_rut"] = tt
        if tt == "retracted":
            muc[khoa]["da_rut"] = True
            muc[khoa]["thong_bao_rut_doi"] = info.get("notice_doi", "")
            # Phân biệt "rút bỏ hẳn" với "rút rồi ĐĂNG LẠI bản đã sửa" — xem
            # crossref_retraction.la_rut_va_thay(). Gọi chung một tên là nói sai về
            # một trích dẫn hợp lệ, và cảnh báo sai làm hỏng giá trị của cảnh báo đúng.
            muc[khoa]["rut_va_thay"] = bool(info.get("retract_and_replace"))
            nhan = "ĐÃ RÚT & ĐĂNG LẠI BẢN SỬA" if info.get("retract_and_replace") else "ĐÃ BỊ RÚT"
            print(f"  🔴 {doi}: {nhan} (thông báo {info.get('notice_doi','')})")
        elif tt == "expression_of_concern":
            muc[khoa]["quan_ngai"] = True
            print(f"  🟠 {doi}: có Expression of Concern — bác sĩ đọc lại")
        elif tt == "unresolved":
            muc[khoa]["nghi_ma"] = True
            print(f"  🟠 {doi}: Crossref không có bản ghi (nghi định danh ma) — rà tay")
    if chua:
        print(f"  ⚠ {chua} DOI KHÔNG tra được lần này — giữ nguyên CHƯA kiểm, "
              f"KHÔNG coi là sạch.")
    ghi_so(so)


def kiem_rut_bai(pmids: list[str]) -> dict[str, dict]:
    """Tra CHỦ ĐỘNG trạng thái rút bài qua CHUỖI 3 TẦNG thật của repo y khoa.

    ĐỔI 14/08/2026: trước đây gọi thẳng `PubMedClient` nên NCBI chặn là mất hẳn
    năng lực — đúng thứ đã khiến 562/1146 mục đứng ở "chưa kiểm rút bài". Nay đi
    qua `RetractionChain`: nền Retraction Watch NGOẠI TUYẾN + NCBI + Europe PMC.

    Không có sẵn (thiếu môi trường) → trả {} và caller phải coi là CHƯA kiểm,
    KHÔNG được coi là "không bị rút".
    """
    if not pmids:
        return {}
    mea = REPO / "medical-ebm-automation"
    if not (mea / "app" / "sources" / "retraction_chain.py").exists():
        return {}
    sys.path.insert(0, str(mea))
    try:
        from app.sources.retraction_chain import RetractionChain  # noqa: PLC0415
        return RetractionChain().check(pmids) or {}
    except ImportError as e:  # noqa: BLE001
        # THIẾU THƯ VIỆN ≠ MẠNG TRỤC TRẶC. Gộp hai thứ này vào cùng một thông điệp
        # "coi như CHƯA kiểm" là lỗi đã gây hậu quả thật: chạy bằng `python3` hệ
        # thống thì `app.config` cần python-dotenv (chỉ có trong venv) nên NHÁNH
        # NÀY LUÔN nổ, `kiem_rut_bai()` luôn trả {}, và KHÔNG PMID nào từng được
        # kiểm rút bài — sổ có 36 PMID, cả 36 đều ở trạng thái "chưa kiểm lần nào".
        # Tệ hơn: vì cờ `da_rut` không bao giờ được đặt, `bao_cao()` trả mã 1 thay
        # vì 2, và chu_trinh_chung_cu.py dịch mã 1 thành "chạy lại thêm vòng" —
        # một lời khuyên VÔ HIỆU, vì chạy lại không bao giờ cài được module thiếu.
        # Đã kiểm bằng venv cùng ngày: NCBI KHÔNG chặn máy này (PMID 9500320 →
        # retracted, 15042359 → ok), nên đây thuần tuý là lỗi gọi nhầm interpreter.
        print(f"  ⛔ KHÔNG kiểm được rút bài vì SAI TRÌNH THÔNG DỊCH ({e}).")
        print("     Đây KHÔNG phải lỗi mạng và chạy lại thêm vòng sẽ không sửa được.")
        print("     Chạy bằng:  ~/.ebm-venv/bin/python tools/so_xac_minh_nguon.py …")
        return {}
    except Exception as e:  # noqa: BLE001
        print(f"  ⚠ Không tra được rút bài lần này ({e}) — coi như CHƯA kiểm.")
        return {}


def lenh_quet(files: list[Path], vong: int) -> int:
    vd = _nap_verify_dashboard()
    so = doc_so()
    muc = so["muc"]
    nguon = gom_nguon(files, vd)
    print(f"Gom được {len(nguon)} nguồn khác nhau từ {len(files)} dashboard.")

    # Đối soát TRƯỚC khi gọi mạng để việc loại một citation đã rút có hiệu lực ngay,
    # kể cả lượt xác minh online bị gián đoạn sau đó.
    so_lien_ket = dong_bo_lien_ket_dashboard(
        muc,
        nguon,
        {f.name for f in files},
    )
    if so_lien_ket:
        ghi_so(so)
        print(f"Đã đối soát liên kết nguồn↔dashboard: {so_lien_ket} bản ghi thay đổi.")

    can_lam = []
    for khoa in sorted(nguon):
        cu = muc.get(khoa)
        if cu:
            con, ly_do = con_hieu_luc(cu)
            if con:
                continue
            if cu.get("da_rut"):
                continue  # đã biết bị rút — không xác minh lại, để nguyên cảnh báo
            print(f"  · hết hiệu lực: {khoa} ({ly_do})")
        can_lam.append(khoa)

    print(f"Cần xác minh lần này: {len(can_lam)} "
          f"(đã có sẵn còn hiệu lực: {len(nguon) - len(can_lam)})")

    for v in range(1, vong + 1):
        if not can_lam:
            break
        print(f"\n── Vòng {v}/{vong} — còn {len(can_lam)} mục ──")
        that_bai = []
        for khoa in can_lam:
            ban_ghi = xac_minh_mot(khoa, vd)
            if ban_ghi is None:
                that_bai.append(khoa)
                continue
            ban_ghi["cac_dashboard"] = sorted(nguon.get(khoa, []))
            cu = muc.get(khoa) or {}
            # giữ lại dấu vết kiểm rút bài cũ nếu có, để không mất lịch sử
            for k in ("kiem_rut_luc", "da_rut", "ghi_chu_rut"):
                if k in cu and k not in ban_ghi:
                    ban_ghi[k] = cu[k]
            muc[khoa] = ban_ghi
            print(f"  ✓ {khoa}")
            # VÁ 13/08/2026 — GHI SỔ TỪNG CHẶNG, không đợi hết vòng.
            # Bản cũ chỉ `ghi_so()` sau khi vòng chạy xong. Với mạng chậm (NCBI đang
            # chặn máy này) một vòng ~180 mục kéo dài rất lâu ⇒ phiên đóng, máy ngủ
            # hay Ctrl-C là MẤT TRẮNG toàn bộ bằng chứng vừa thu, dù mỗi mục đã xác
            # minh thành công. Đo thật hôm nay: 12 phút chạy, sổ vẫn đúng 118 mục như
            # lúc bắt đầu. Ghi mỗi 10 mục để công sức luôn được giữ lại.
            if len(muc) % 10 == 0:
                ghi_so(so)
        ghi_so(so)
        print(f"  Vòng {v}: thêm {len(can_lam) - len(that_bai)} · còn thiếu {len(that_bai)}")
        can_lam = that_bai

    kiem_rut_bai_theo_doi(muc, nguon, so)

    # ── kiểm rút bài cho PMID đã xác minh nhưng quá hạn kiểm ────────────────
    can_kiem_rut = []
    for khoa, bg in muc.items():
        if bg.get("loai") != "pmid":
            continue
        if khoa not in nguon:
            continue
        if bg.get("da_rut") and "rut_va_thay" in bg:
            continue  # xem ghi chú cùng lý do ở kiem_rut_bai_theo_doi()
        t = _tuoi_ngay(bg.get("kiem_rut_luc"))
        if t is None or t > HAN_RUT_BAI_NGAY or (bg.get("da_rut") and "rut_va_thay" not in bg):
            can_kiem_rut.append(bg["gia_tri"])
    if can_kiem_rut:
        print(f"\n── Tra rút bài cho {len(can_kiem_rut)} PMID ──")
        kq = kiem_rut_bai(can_kiem_rut)
        bay_gio = dt.datetime.now().isoformat(timespec="seconds")
        chua_tra_duoc = 0
        # Gom lý do THẬT theo từng trạng thái. Trước 12/08/2026 chỗ này chỉ đếm rồi in
        # một câu duy nhất đổ cho "thiếu NCBI_EMAIL hoặc đang bật mock" — nhưng nhánh
        # này bắt CẢ 'unknown_fetch_error' (NCBI CHẶN IP, cần NCBI_API_KEY). Đo thật
        # trên máy Windows hôm đó: cấu hình ĐÚNG (mock tắt, có NCBI_EMAIL) mà vẫn ra
        # câu đó ⇒ bác sĩ bị đẩy đi sửa một cấu hình vốn không sai. Cùng lớp lỗi
        # "không biết bị báo thành có vấn đề" mà chính công cụ này sinh ra để chặn.
        ly_do_chua_tra = {}
        for pmid, info in kq.items():
            khoa = f"pmid:{pmid}"
            if khoa not in muc:
                continue
            trang_thai = (info or {}).get("status", "")

            # DANH SÁCH TRẠNG THÁI LÀ ĐÓNG — xem docstring check_retraction_status().
            # KHÔNG dùng kiểu "khác 'ok' thì coi là bị rút": lần viết đầu của hàm này
            # làm đúng vậy và biến 18 PMID lành thành "ĐÃ BỊ RÚT" chỉ vì máy thiếu
            # NCBI_EMAIL nên PubMed trả 'unknown_mock_or_no_email' (= KHÔNG BIẾT).
            # Đó chính là lỗi "cổng nói sai về dữ liệu đúng" — báo động giả về rút
            # bài còn tệ hơn không kiểm, vì nó khiến người ta mất tin vào cảnh báo thật.
            if trang_thai in ("unknown_mock_or_no_email", "unknown_fetch_error"):
                # KHÔNG ghi kiem_rut_luc: mục này vẫn phải tính là CHƯA kiểm.
                # 'unknown_fetch_error' = gọi được nhưng không đọc được phản hồi
                # (mạng cắt giữa chừng / NCBI trả trang chặn). KHÔNG có cơ sở nào
                # để nghi trích dẫn ma — khác hẳn 'unresolved'.
                chua_tra_duoc += 1
                ly_do_chua_tra[trang_thai] = (info or {}).get("reason", "")
                continue

            muc[khoa]["kiem_rut_luc"] = bay_gio
            muc[khoa]["ghi_chu_rut"] = trang_thai
            if trang_thai == "retracted":
                muc[khoa]["da_rut"] = True
                muc[khoa]["rut_va_thay"] = bool((info or {}).get("retract_and_replace"))
                nhan = ("ĐÃ RÚT & ĐĂNG LẠI BẢN SỬA"
                        if (info or {}).get("retract_and_replace") else "ĐÃ BỊ RÚT")
                print(f"  🔴 {pmid}: {nhan}")
            elif trang_thai == "expression_of_concern":
                muc[khoa]["quan_ngai"] = True
                print(f"  🟠 {pmid}: có Expression of Concern — cần bác sĩ đọc lại")
            elif trang_thai == "unresolved":
                # PubMed không trả bản ghi. Mâu thuẫn với việc đã xác minh tồn tại ở
                # trên => phải nói ra, không im lặng bỏ qua.
                muc[khoa]["nghi_ma"] = True
                print(f"  🟠 {pmid}: PubMed không trả bản ghi (nghi trích dẫn ma) — rà tay")

        if chua_tra_duoc:
            print(f"  ⚠ {chua_tra_duoc} PMID KHÔNG tra cứu rút bài được lần này — giữ "
                  f"nguyên trạng thái CHƯA kiểm, KHÔNG coi là sạch.")
            for tt, ly_do in ly_do_chua_tra.items():
                nhan = {
                    "unknown_mock_or_no_email":
                        "đang bật dữ liệu giả hoặc thiếu NCBI_EMAIL — sửa cấu hình ở "
                        "~/.ebm-secrets/medical-ebm-automation.env",
                    "unknown_fetch_error":
                        "gọi được nhưng không đọc được phản hồi (mạng cắt giữa chừng, "
                        "hoặc NCBI trả trang CHẶN)",
                }.get(tt, tt)
                print(f"     · {nhan}")
                if ly_do:
                    print(f"       lý do nguồn trả về: {ly_do}")
        if not kq:
            print("  ⚠ Không tra được lần này — các PMID này vẫn tính là CHƯA kiểm rút bài.")
        ghi_so(so)

    return bao_cao(nguon_pham_vi=set(nguon))


def bao_cao(nguon_pham_vi: set[str] | None = None) -> int:
    so = doc_so()
    muc = so["muc"]
    khoas = sorted(nguon_pham_vi) if nguon_pham_vi is not None else sorted(muc)
    if not khoas:
        print("Sổ trống — chạy --quet trước.")
        return 1

    du, thieu, rut, luu_y = [], [], [], []
    for khoa in khoas:
        bg = muc.get(khoa)
        if not bg:
            thieu.append((khoa, "chưa xác minh lần nào"))
            continue
        if bg.get("da_rut"):
            rut.append((khoa, bg.get("ghi_chu_rut", "")))
            continue
        if bg.get("quan_ngai"):
            luu_y.append((khoa, "Expression of Concern"))
        elif bg.get("nghi_ma"):
            luu_y.append((khoa, "PubMed không trả bản ghi — nghi trích dẫn ma"))
        con, ly_do = con_hieu_luc(bg)
        (du if con else thieu).append((khoa, ly_do))

    tong = len(khoas)
    print("\n" + "=" * 64)
    print("SỔ XÁC MINH NGUỒN — độ phủ")
    print("=" * 64)
    print(f"  Còn hiệu lực : {len(du)}/{tong} ({len(du) * 100 // max(tong, 1)}%)")
    print(f"  Chưa/hết hạn : {len(thieu)}")

    # VÁ 13/08/2026 — TÁCH LÝ DO, vì cách sửa NGƯỢC NHAU.
    # Trước đó mọi mục "chưa/hết hạn" đều dẫn tới một lời khuyên duy nhất: "chạy lại
    # thêm vòng". Đo thật hôm nay: 562/1146 mục hết hiệu lực, và CẢ 562 là PMID chưa
    # kiểm rút bài được vì NCBI đang chặn máy — chạy lại một trăm vòng cũng KHÔNG đổi
    # được gì. Đẩy bác sĩ đi làm một việc chắc chắn vô ích còn tệ hơn im lặng: nó tiêu
    # thời gian thật và làm mất niềm tin vào mọi lời khuyên khác của công cụ.
    if thieu:
        chua_rut = [x for x in thieu if "chưa kiểm rút bài" in x[1] or "kiểm rút bài đã" in x[1]]
        het_han = [x for x in thieu if "xác minh đã" in x[1]]
        khac = [x for x in thieu if x not in chua_rut and x not in het_han]
        print("\n  Vì sao hết hiệu lực — CÁCH SỬA KHÁC NHAU, đừng gộp:")
        if chua_rut:
            # ĐỔI 14/08/2026: lời khuyên cũ ("chạy lại KHÔNG sửa được, phải có NCBI_API_KEY")
            # nay SAI, vì kiểm rút bài đã đi qua chuỗi 3 tầng — nền Retraction Watch ngoại
            # tuyến và Europe PMC đều không cần khoá. Chỉ đường tới cách sửa THẬT SỰ có tác
            # dụng, đúng tinh thần BH14 (đừng khuyên việc chắc chắn vô ích).
            nen_rw = (REPO / "medical-ebm-automation" / "data" / "retraction_watch"
                      / "retraction_watch.csv")
            print(f"     • {len(chua_rut)} mục: CHƯA kiểm được RÚT BÀI.")
            if not nen_rw.exists():
                print("       → CHƯA tải nền ngoại tuyến. Tải MỘT LẦN (không cần khoá API):")
                print("           python medical-ebm-automation/tools/tai_retraction_watch.py")
                print("         rồi chạy lại — SẼ sửa được, không phụ thuộc NCBI.")
                print("       [MA] CAN_TAI_RETRACTION_WATCH")
            else:
                print("       → Chạy lại thêm vòng CÓ THỂ sửa được (chuỗi 3 tầng: Retraction")
                print("         Watch ngoại tuyến → NCBI → Europe PMC). Phần còn sót là mục cả")
                print("         ba nguồn đều không kết luận được; thêm `NCBI_API_KEY` vào")
                print("         ~/.ebm-secrets/medical-ebm-automation.env sẽ mở lại tầng NCBI.")
                print("       [MA] CAN_NCBI_API_KEY")
        if het_han:
            print(f"     • {len(het_han)} mục: xác minh tồn tại đã quá {HAN_TON_TAI_NGAY} ngày.")
            print("       → Chạy lại thêm vòng SẼ sửa được.")
            print("       [MA] CAN_CHAY_THEM_VONG")
        if khac:
            print(f"     • {len(khac)} mục: lý do khác — {khac[0][1]}")
            print("       [MA] CAN_XEM_TAY")
    # Đếm RIÊNG hai mức: "rút bỏ hẳn" và "rút rồi ĐĂNG LẠI bản đã sửa". Gộp lại thì
    # một trích dẫn HỢP LỆ (bản đã sửa, thường cùng DOI/PMID) bị đọc thành "không được
    # dùng" — cảnh báo sai làm hỏng giá trị của cảnh báo đúng. Xem BH34.
    # CHỈ báo nguồn đang thực sự được MỘT dashboard nào đó trích. Bản ghi mồ côi
    # (đã gỡ khỏi mọi dashboard) không còn là việc phải xử lý — hiện nó lên như báo
    # động đỏ chỉ tạo nhiễu, và nhiễu dạy người ta bỏ qua màu đỏ. Vẫn giữ trong sổ để
    # không mất lịch sử.
    dang_dung = [(k, g) for k, g in rut if muc[k].get("cac_dashboard")]
    mo_coi = len(rut) - len(dang_dung)
    thay = [(k, g) for k, g in dang_dung if muc[k].get("rut_va_thay")]
    han = [(k, g) for k, g in dang_dung if not muc[k].get("rut_va_thay")]
    print(f"  ĐÃ BỊ RÚT    : {len(han)}"
          + (f"  ·  RÚT & ĐĂNG LẠI BẢN SỬA: {len(thay)}" if thay else "")
          + (f"  ·  {mo_coi} bản ghi cũ không còn dashboard nào trích" if mo_coi else ""))
    if han:
        print("\n  🔴 NGUỒN ĐÃ BỊ RÚT — không dùng kết luận của các bài này:")
        for khoa, gc in han:
            dash = ", ".join(muc[khoa].get("cac_dashboard", [])[:3])
            print(f"     • {khoa} [{gc}]  ← {dash}")
    if thay:
        print("\n  🟠 RÚT & ĐĂNG LẠI BẢN ĐÃ SỬA — trích dẫn VẪN dùng được, nhưng số liệu")
        print("     phải lấy từ BẢN ĐÃ SỬA (thường cùng DOI/PMID), không phải bỏ mục đi:")
        for khoa, _gc in thay:
            dash = ", ".join(muc[khoa].get("cac_dashboard", [])[:3])
            tb = muc[khoa].get("thong_bao_rut_doi") or ""
            print(f"     • {khoa}" + (f"  (thông báo {tb})" if tb else "") + f"  ← {dash}")
    if luu_y:
        print("\n  🟠 CẦN BÁC SĨ ĐỌC LẠI (không phải rút bài, nhưng không bỏ qua được):")
        for khoa, gc in luu_y:
            dash = ", ".join(muc[khoa].get("cac_dashboard", [])[:2])
            print(f"     • {khoa} — {gc}  ← {dash}")
    if thieu:
        print(f"\n  Còn thiếu ({min(len(thieu), 10)} mục đầu):")
        for khoa, ly_do in thieu[:10]:
            print(f"     · {khoa} — {ly_do}")
        if len(thieu) > 10:
            print(f"     … và {len(thieu) - 10} mục nữa")
    print("\n  Sổ chỉ ghi nhận THÀNH CÔNG; mạng hỏng không bao giờ thành 'đã xác minh'.")
    print("  Đây KHÔNG thay cổng --online và không thay bác sĩ duyệt.")
    print("  Cần bác sĩ kiểm chứng.")

    if rut:
        return 2
    return 0 if not thieu else 1



def quet_ledger_hub(vong: int = 1) -> None:
    """Quét RÚT BÀI cho định danh CHỈ-CÓ-TRONG-HUB — lựa chọn A bác sĩ duyệt 15/08/2026.

    Vì sao: quét theo-dashboard không chạm được ~240 thẻ hub tích luỹ nhiều tháng
    mà dashboard gốc không còn trên đĩa ⇒ chúng vĩnh viễn KHÔNG BIẾT dù mạng tốt.
    Chế độ này đọc thẳng EBM_MASTER, gom pmid/doi chưa có phán quyết còn hạn,
    hỏi chuỗi 3 tầng (PMID, lô 50) + tầng Crossref (DOI) rồi ghi sổ — CHỈ ghi
    THÀNH CÔNG, thất bại giữ nguyên KHÔNG BIẾT (bất biến của sổ).
    """
    from datetime import datetime as _dt, timedelta as _td
    hub = json.loads((DASH.parent / "EBM_MASTER" / "EBM_MASTER.json")
                     .read_text(encoding="utf-8"))
    so = doc_so()
    muc = so.setdefault("muc", {})
    bay_gio = _dt.now().isoformat(timespec="seconds")
    han = (_dt.now() - _td(days=30)).isoformat()

    can_pmid, can_doi = [], []
    for c in hub.get("evidence_cards", []):
        src = c.get("source") or {}
        pm, doi = src.get("pmid"), (src.get("doi") or "").lower()
        if pm:
            bg = muc.get(f"pmid:{pm}")
            if not (bg and bg.get("ghi_chu_rut") and (bg.get("kiem_rut_luc") or "") > han):
                can_pmid.append(str(pm))
        elif doi:
            bg = muc.get(f"doi:{doi}")
            if not (bg and bg.get("ghi_chu_rut") and (bg.get("kiem_rut_luc") or "") > han):
                can_doi.append(doi)
    can_pmid, can_doi = sorted(set(can_pmid)), sorted(set(can_doi))
    print(f"HUB: cần kiểm {len(can_pmid)} PMID + {len(can_doi)} DOI (chưa có phán quyết còn hạn)")

    sys.path.insert(0, str(DASH.parent / "medical-ebm-automation"))
    from app.sources.retraction_chain import RetractionChain  # noqa: PLC0415
    from app.sources.crossref_retraction import CrossrefRetraction  # noqa: PLC0415
    chain, cr = RetractionChain(), CrossrefRetraction()
    ghi = 0
    for _v in range(max(1, vong)):
        for i in range(0, len(can_pmid), 50):
            lo = can_pmid[i:i + 50]
            try:
                kq = chain.check(lo)
            except Exception as exc:  # noqa: BLE001
                print(f"  lô PMID {i//50+1}: lỗi {type(exc).__name__} — giữ KHÔNG BIẾT")
                continue
            for p, v in kq.items():
                tt = v.get("status", "")
                if tt == "ok" or tt in ("retracted", "expression_of_concern"):
                    k = f"pmid:{p}"
                    bg = muc.setdefault(k, {"loai": "pmid", "gia_tri": p,
                                            "cac_dashboard": ["(hub-only)"]})
                    bg["ghi_chu_rut"] = tt
                    bg["kiem_rut_luc"] = bay_gio
                    bg["nguon_xac_minh"] = v.get("source") or "chain"
                    if tt != "ok":
                        bg["da_rut"] = True
                        if v.get("retract_and_replace"):
                            bg["rut_va_thay"] = True
                    ghi += 1
        for i in range(0, len(can_doi), 20):
            lo = can_doi[i:i + 20]
            try:
                kq = cr.check(lo)
            except Exception as exc:  # noqa: BLE001
                print(f"  lô DOI {i//20+1}: lỗi {type(exc).__name__} — giữ KHÔNG BIẾT")
                continue
            for d, v in (kq or {}).items():
                tt = (v or {}).get("status", "")
                if tt == "ok" or tt in ("retracted", "expression_of_concern"):
                    k = f"doi:{d.lower()}"
                    bg = muc.setdefault(k, {"loai": "doi", "gia_tri": d,
                                            "cac_dashboard": ["(hub-only)"]})
                    bg["ghi_chu_rut"] = tt
                    bg["kiem_rut_luc"] = bay_gio
                    bg["nguon_xac_minh"] = "crossref"
                    if tt != "ok":
                        bg["da_rut"] = True
                        if v.get("retract_and_replace"):
                            bg["rut_va_thay"] = True
                    ghi += 1
        # các mục đã ghi thành công sẽ bị lọc ở vòng kế nhờ điều kiện còn-hạn
        can_pmid = [p for p in can_pmid
                    if not ((muc.get(f"pmid:{p}") or {}).get("kiem_rut_luc") or "") > han]
        can_doi = [d for d in can_doi
                   if not ((muc.get(f"doi:{d}") or {}).get("kiem_rut_luc") or "") > han]
    ghi_so(so)
    print(f"✓ ghi {ghi} phán quyết vào sổ · còn KHÔNG BIẾT: {len(can_pmid)} PMID + {len(can_doi)} DOI")

def main() -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Sổ xác minh nguồn — tích luỹ qua nhiều vòng")
    ap.add_argument("--quet", nargs="*", help="dashboard cần xác minh (mặc định: tất cả)")
    ap.add_argument("--vong", type=int, default=2,
                    help="số vòng thử lại cho mạng chập chờn (mặc định 2)")
    ap.add_argument("--bao-cao", action="store_true", help="chỉ in độ phủ, không gọi mạng")
    ap.add_argument("--quet-ledger", action="store_true",
                    help="quét rút bài cho định danh CHỈ-CÓ-TRONG-HUB (lựa chọn A, 15/08)")
    a = ap.parse_args()

    if a.quet_ledger:
        quet_ledger_hub(a.vong)
        return 0
    if a.bao_cao and a.quet is None:
        return bao_cao()

    mau = a.quet if a.quet else [str(DASH / "WebDashboard_*.html")]
    files: list[Path] = []
    for m in mau:
        files.extend(Path(p) for p in glob.glob(m))
    files = sorted({f.resolve() for f in files if f.exists()})
    if not files:
        print("✗ Không thấy dashboard nào khớp.", file=sys.stderr)
        return 2
    return lenh_quet(files, max(1, a.vong))


if __name__ == "__main__":
    raise SystemExit(main())
