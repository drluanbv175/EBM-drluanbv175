#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TRẠM QUAN SÁT THEO TỔ CHỨC — LÔ B PHA 4 (15/08/2026).

Vì sao: guideline thường lên WEB CỦA HỘI trước khi vào PubMed hàng tuần–tháng
(GOLD/GINA/ADA SoC là ca kinh điển) — chỉ quét PubMed là chấp nhận trễ đúng
khoảng đó. Trạm này theo dõi trang danh mục guideline/feed chính thức.

TRẠNG THÁI THẬT (P6 — không bịa): egress tới host ngoài danh sách phê duyệt bị
chặn ở tầng runtime của máy này, và tôi không xác minh sống được URL các hội ⇒
mọi nguồn html-watch/rss trong `data/sources.json` đang `not-covered` với
`endpoint_or_url=null`. Trạm vì thế DỰNG XONG NHƯNG NẰM CHỜ: bác sĩ xác minh
URL + phê duyệt egress → điền endpoint, đổi status → trạm chạy ngay, không cần
sửa code. Năng lực dò được CHỨNG MINH bằng `--self-test` fixture ngoại tuyến.

Cách dò (chống báo động giả — đúng yêu cầu LÔ B):
  • So TIÊU ĐỀ đã chuẩn hoá (bỏ thẻ HTML, gộp khoảng trắng), KHÔNG so vị trí
    phần tử: đổi giao diện thuần tuý ⇒ 0 cảnh báo.
  • Chỉ báo khi xuất hiện TIÊU ĐỀ MỚI mang năm/số hiệu, hoặc feed có item mới.
  • Nguồn fetch hỏng → status degraded + in RÕ «chuyên khoa X đang mù» — tuyệt
    đối không im lặng bỏ qua (I7).

Đầu ra: `EBM-Dashboards/surveillance/to-chuc-<ngày>.md` (ứng viên
source.type=guideline, kèm ngày phát hiện) · state ở `state/giam-sat-to-chuc.json`.
Mã thoát: 0 sạch · 1 có phát hiện/degraded · 2 sổ nguồn hỏng.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

GOC = Path(__file__).resolve().parents[1]
SO_NGUON = GOC / "data" / "sources.json"
STATE = GOC / "state" / "giam-sat-to-chuc.json"
RA = GOC / "EBM-Dashboards" / "surveillance"

# Tiêu đề «đáng giá»: có năm 20xx HOẶC từ khoá guideline/report/update/statement.
RE_TIEU_DE = re.compile(
    r"(?:20\d{2}|guideline|report|update|standards|statement|recommendation)", re.I)


def _loc_tieu_de_hop_le(ung_vien: "list[str] | set[str]") -> set[str]:
    """Bộ lọc DÙNG CHUNG cho cả hai đường trích (HTML thô và văn bản thuần) — một
    luật lọc, không phân nhánh, để hai đường không lệch tiêu chí «tiêu đề đáng
    giá» theo thời gian (bài học lặp lại của repo: hai module viết cho nhau mà
    không dùng chung một hàm sẽ trôi lệch)."""
    ket: set[str] = set()
    for x in ung_vien:
        sach = re.sub(r"<[^>]+>", " ", x)
        sach = re.sub(r"\s+", " ", sach).strip()
        if 12 <= len(sach) <= 220 and RE_TIEU_DE.search(sach):
            ket.add(sach)
    return ket


def rut_tieu_de(html: str) -> set[str]:
    """Rút tập tiêu đề chuẩn hoá từ HTML/feed — so NỘI DUNG, không so vị trí."""
    # feed: <title>…</title>; html: nội dung <a>/<h1..h4>
    tho = re.findall(r"<title[^>]*>(.*?)</title>|<a[^>]*>(.*?)</a>|<h[1-4][^>]*>(.*?)</h[1-4]>",
                     html, re.S | re.I)
    phang = [x for bo in tho for x in bo if x]
    return _loc_tieu_de_hop_le(phang)


_DONG_KHUNG_GET_PAGE_TEXT = re.compile(
    r"^(Title:|URL:|Source element:|Tab Context:|-{3,}$|-\s+Executed on|"
    r"•\s*tabId|Available tabs:)", re.I)
# Tên tháng — CẢ viết tắt 3 chữ (Sep/Jul/Jun…) LẪN đầy đủ (September/July/June…).
# Vá 13/09/2026: ba mẫu ngày-tháng dưới đây trước đó chỉ nhận dạng viết tắt;
# WHO ("10 September 2026") và GINA ("July 21, 2026") dùng tên tháng ĐẦY ĐỦ nên
# lọt qua cả ba, rồi bị chính luật OR-kết-thúc-bằng-năm (vá IDSA cùng ngày, xem
# _DONG_KET_THUC_BANG_NAM) nhận NHẦM thành tiêu đề — hồi quy tự gây ra khi vá
# IDSA, bắt được ngay khi khảo sát tiếp WHO/GINA.
_TEN_THANG = (r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
              r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|"
              r"Dec(?:ember)?)")

# Dòng CHỈ LÀ ngày-tháng kèm/không kèm tên tạp chí (vd «Sep 08, 2026 | Circulation»,
# «Aug 31, 2026», «July 21, 2026» — GINA) — mẫu nhật ký bài viết, không phải tiêu
# đề. Đo trên trang ACC/AHA thật: đây là 2/9 mẫu rác KHÔNG bị chặn bởi sàn số-từ
# vì đủ dài (5 từ) — nay còn phải chặn cả khi ≥5 từ đổi thành OR-kết-thúc-bằng-năm.
_DONG_CHI_NGAY_THANG = re.compile(
    rf"^{_TEN_THANG}\s+\d{{1,2}},?\s+20\d{{2}}(\s*\|.*)?$")
# Dòng CHỈ LÀ "Mon/Month YYYY" — KHÔNG có số ngày, KHÔNG có tên tạp chí — khác
# hẳn _DONG_CHI_NGAY_THANG ở trên. Đo trên trang USPSTF thật 13/09/2026: mỗi
# tiêu đề khuyến cáo nằm MỘT MÌNH trên một dòng (đủ ≥5 từ nhưng không có năm/từ
# khoá nên rớt RE_TIEU_DE), NGAY SAU đó là một dòng ngày-tháng kiểu này (vd «Jun
# 2025» — chỉ 2 từ nên rớt sàn số-từ). Không dòng nào một mình lọt qua bộ lọc;
# phải GHÉP hai dòng liền kề mới ra một tiêu đề hợp lệ (xem vòng lặp merge bên dưới).
_DONG_CHI_THANG_NAM = re.compile(rf"^{_TEN_THANG}\s+20\d{{2}}$")
# Dòng CHỈ LÀ "DD Month YYYY" — ngày ĐỨNG TRƯỚC tên tháng, không dấu phẩy — thứ
# tự khác hẳn hai mẫu trên. Đo trên trang WHO thật 13/09/2026 (khối "Latest WHO
# guidelines approved…"): mỗi tiêu đề khuyến cáo có một dòng ngày kiểu này đứng
# NGAY TRƯỚC nó (vd «10 September 2026», «18 December 2025» — 3 từ, kết thúc
# bằng năm nên bị luật OR-kết-thúc-bằng-năm của IDSA nhận nhầm nếu không chặn ở đây).
_DONG_NGAY_THANG_KIEU_WHO = re.compile(rf"^\d{{1,2}}\s+{_TEN_THANG}\s+20\d{{2}}$")

# Số dòng LIÊN TIẾP tối thiểu để một chuỗi dòng ALL-CAPS ≥2 từ được coi là "khối
# danh mục chủ đề" (xem _la_toan_hoa_nhieu_tu) thay vì trùng ngẫu nhiên với một
# nút/khối điều hướng. Đo trên trang KDIGO thật 13/09/2026: khối chủ đề dài 18
# dòng liên tiếp; chuỗi ALL-CAPS ≥2-từ DÀI NHẤT ngoài khối đó (nút kêu gọi hành
# động "JOIN THE KDIGO MAILING LIST"/"SIGN UP"/"IMPROVING GLOBAL OUTCOMES") chỉ
# dài 3 — chọn 4 để tách rõ hai nhóm với đúng 1 đơn vị biên an toàn đo được.
_NGUONG_CHUOI_TOAN_HOA = 4

# Dòng KẾT THÚC bằng năm 19xx/20xx (không phải chỉ CHỨA năm ở đâu đó — «ESC 2026
# Science News» không khớp vì năm không đứng cuối). Dùng để NỚI sàn ≥5 từ (vốn
# thiết kế cho rác ACC/AHA) cho các nguồn đặt tên tài liệu NGẮN + năm ở cuối
# (vd IDSA: «MRSA 2011», «Vancomycin 2020», «AMR Guidance 2026» — 2-4 từ).
_DONG_KET_THUC_BANG_NAM = re.compile(r"(?:19|20)\d{2}$")


def _la_toan_hoa_nhieu_tu(dong: str) -> bool:
    """Dòng ALL-CAPS (mọi chữ cái đều viết hoa) có ≥2 từ — tín hiệu heading/nhãn
    danh mục, khác văn xuôi (có chữ thường) và khác nút điều hướng đơn từ
    (ABOUT/EVENTS/NEWS…) vốn không đủ ≥2 từ để bị coi là ứng viên."""
    return bool(re.search(r"[A-Za-z]", dong)) and dong == dong.upper() and len(dong.split()) >= 2


def rut_tieu_de_tu_van_ban(text: str) -> set[str]:
    """Rút tiêu đề từ VĂN BẢN THUẦN (không có thẻ HTML) — dùng khi nội dung tới
    từ một trình duyệt thật (Browser tool của phiên agent, get_page_text) thay
    vì fetch HTML thô bằng urllib. Ra đời 09/09/2026 khi SRC-015 (ACC/AHA)
    xác nhận: trang bị Cloudflare bot-challenge chặn MỌI request urllib (kể cả
    đổi User-Agent trình duyệt thật — 403 kèm cookie __cf_bm), nhưng một phiên
    Browser THẬT (thực thi JS) tải được nội dung đầy đủ.

    HAI LỚP LỌC RIÊNG cho đường này (khác _loc_tieu_de_hop_le dùng chung với
    HTML — KHÔNG sửa hàm dùng chung, vì self-test HTML có fixture 4-từ hợp
    lệ "2026 GOLD Report — NEW"; siết chung sẽ làm nó đỏ oan):
    (1) bỏ dòng KHUNG do chính get_page_text in ra (Title:/URL:/---/Tab
        Context:…) — không phải nội dung trang, đưa vào sẽ tự sinh «tiêu đề
        giả» từ chính công cụ đọc trang.
    (2) đo LẦN ĐẦU trên trang ACC/AHA thật (09/09/2026): tách dòng thuần
        (không có thẻ HTML để phân biệt heading/link khỏi văn xuôi/breadcrumb)
        cho 20/20 dòng "qua" bộ lọc nội dung — 17/20 là rác (ngày tháng đơn
        độc kiểu «Sep 08, 2026 | Circulation», breadcrumb «Home Guidelines
        and Statements», nút «Search Guidelines and Statements»…). Vá bằng
        HAI luật cộng thêm: sàn ĐỘ DÀI ≥5 từ (loại 7/9 mẫu rác đo được) +
        mẫu riêng cho «chỉ ngày-tháng [kèm tạp chí]» (loại nốt 2/9 mẫu rác
        còn lại — đủ dài để qua sàn từ nhưng KHÔNG phải tiêu đề). Không phải
        bộ lọc hoàn hảo (còn lọt vài CTA như «Read the AHA/ASA Guideline in
        Stroke») nhưng cắt phần lớn rác mà không cần biết cấu trúc DOM của
        riêng trang này (đúng nguyên tắc «so nội dung, không so vị trí» của
        module — cả hai luật đều là tiêu chí NỘI DUNG, không phải toạ độ).
    (3) vá 13/09/2026 (SRC-019 USPSTF): trang này tách tiêu đề khuyến cáo và
        ngày cập nhật ra HAI dòng liền kề («…: Screening» rồi «Jun 2025») —
        khác ACC/AHA gộp ngày+tạp chí trên MỘT dòng. Không dòng nào một mình
        đủ điều kiện (tiêu đề thiếu năm/từ khoá, ngày chỉ 2 từ) nên phải GHÉP
        cặp dòng liền kề khi dòng sau khớp _DONG_CHI_THANG_NAM trước khi lọc,
        để không đổi hành vi ACC/AHA (nơi ngày luôn đứng riêng, không cần ghép).
    (4) vá 13/09/2026 (SRC-012 KDIGO): trang này liệt kê 18 chủ đề guideline
        bằng TÊN BỆNH VIẾT HOA («ANEMIA IN CKD», «TRANSPLANT CANDIDATE»…) —
        KHÔNG năm, KHÔNG từ khoá guideline/report/…, nên rớt RE_TIEU_DE dù là
        tiêu đề thật; đo sống: 0/18 lọt qua bộ lọc cũ, chỉ 3 dòng văn xuôi giới
        thiệu (không đổi bao giờ) bị nhận nhầm thành "tiêu đề". Không thể chỉ
        nhận diện "dòng ALL-CAPS ≥2 từ" một mình — nút CTA cuối trang («JOIN
        THE KDIGO MAILING LIST») cũng ALL-CAPS ≥2 từ. Khác biệt THẬT đo được:
        18 dòng chủ đề đứng LIÊN TIẾP nhau, còn mọi dòng ALL-CAPS ≥2 từ khác
        trên trang (điều hướng, CTA) chỉ đứng đơn lẻ hoặc thành chuỗi ngắn ≤3.
        Nhận khối bằng NGƯỠNG ĐỘ DÀI CHUỖI liên tiếp (_NGUONG_CHUOI_TOAN_HOA),
        bỏ qua RE_TIEU_DE cho các dòng trong khối — vẫn là tiêu chí NỘI DUNG
        (hình thức chữ + vị trí trong DÒNG CHẢY văn bản, không phải toạ độ
        DOM), không sửa _loc_tieu_de_hop_le dùng chung.
    (5) vá 13/09/2026 (SRC-017 IDSA): sàn ≥5 từ ở (2) đúng cho ACC/AHA nhưng
        SAI cho trang này — IDSA đặt tên tài liệu NGẮN + năm cuối dòng («MRSA
        2011», «Vancomycin 2020», «AMR Guidance 2026»: 2-4 từ). Đo sống trên
        đúng văn bản trang thật: sàn ≥5 từ làm rớt 47/114 tiêu đề thật (41%),
        toàn bộ đều 2-4 từ, không cái nào là rác đã biết. NỚI sàn bằng luật
        OR: chấp nhận <5 từ nếu dòng KẾT THÚC bằng năm (_DONG_KET_THUC_BANG_NAM)
        — khác «CHỨA năm ở giữa» của rác ACC/AHA «ESC 2026 Science News» (năm
        không đứng cuối, vẫn rớt đúng như cũ, test khoá hành vi này không đổi).
        Không nới cho MỌI dòng ngắn — chỉ dòng có năm cuối, một tín hiệu hẹp
        và mạnh hơn hẳn "ngắn = rác". Vẫn còn 1/47 lọt lưới do sàn ĐỘ DÀI KÝ TỰ
        ≥12 của _loc_tieu_de_hop_le dùng chung («MRSA 2011» chỉ 9 ký tự) — chấp
        nhận, không sửa hàm dùng chung để đổi một trường hợp biên.
    (6) vá 13/09/2026 (HỒI QUY do (5) tự gây ra, bắt được khi khảo sát tiếp
        SRC-022 WHO/SRC-011 GINA): luật OR ở (5) chỉ loại trừ dòng ngày-tháng
        VIẾT TẮT 3 chữ («Sep»/«Jun»…), nhưng WHO dùng «DD Month YYYY» đầy đủ
        không dấu phẩy («10 September 2026») còn GINA dùng «Month DD, YYYY»
        đầy đủ («July 21, 2026») — cả hai đều 3 từ, kết thúc bằng năm, KHÔNG
        khớp _DONG_CHI_NGAY_THANG/_DONG_CHI_THANG_NAM cũ (chỉ nhận viết tắt)
        nên lọt qua rồi bị chính luật OR-kết-thúc-bằng-năm nhận NHẦM thành tiêu
        đề. Đo sống: 6/8 dòng ngày trên trang WHO thật bị nhận nhầm. Vá bằng
        cách MỞ RỘNG _TEN_THANG cho cả viết tắt lẫn đầy đủ (áp dụng lại cho
        CẢ _DONG_CHI_NGAY_THANG lẫn _DONG_CHI_THANG_NAM, không chỉ chỗ mới)
        và thêm mẫu thứ ba _DONG_NGAY_THANG_KIEU_WHO cho thứ tự «ngày trước
        tháng» mà hai mẫu cũ chưa từng phủ. KHÔNG vá vấn đề riêng «tiêu đề
        NGẮN mà ngày nằm ở dòng KHÁC» (vd «WHO guidelines for malaria» 4 từ,
        ngày đứng dòng TRƯỚC nó) — đó là lỗ hổng ĐỘ PHỦ (recall) có mức nguy
        hại thấp hơn hẳn báo động giả hàng loạt đang vá ở đây, và cần đo thêm
        trước khi thiết kế đúng (chưa đủ bằng chứng để vá an toàn trong lượt
        này)."""
    dong_tho = [d.strip() for d in text.splitlines() if d.strip()
                and not _DONG_KHUNG_GET_PAGE_TEXT.match(d.strip())]

    ung_vien: list[str] = []
    i = 0
    while i < len(dong_tho):
        hien_tai = dong_tho[i]
        ke_tiep = dong_tho[i + 1] if i + 1 < len(dong_tho) else None
        neu_ghep_duoc = (
            ke_tiep is not None
            and not _DONG_CHI_NGAY_THANG.match(hien_tai)
            and not _DONG_CHI_THANG_NAM.match(hien_tai)
            and not _DONG_NGAY_THANG_KIEU_WHO.match(hien_tai)
            and _DONG_CHI_THANG_NAM.match(ke_tiep)
            and len(hien_tai.split()) >= 5
        )
        if neu_ghep_duoc:
            ung_vien.append(f"{hien_tai} {ke_tiep}")
            i += 2
            continue
        ung_vien.append(hien_tai)
        i += 1

    dong = [d for d in ung_vien
            if not _DONG_CHI_NGAY_THANG.match(d)
            and not _DONG_CHI_THANG_NAM.match(d)
            and not _DONG_NGAY_THANG_KIEU_WHO.match(d)
            and (len(d.split()) >= 5 or _DONG_KET_THUC_BANG_NAM.search(d))]
    ket = _loc_tieu_de_hop_le(dong)

    khoi: list[str] = []
    for d in ung_vien + [None]:
        if d is not None and _la_toan_hoa_nhieu_tu(d):
            khoi.append(d)
            continue
        if len(khoi) >= _NGUONG_CHUOI_TOAN_HOA:
            for tieu_de in khoi:
                sach = re.sub(r"\s+", " ", tieu_de).strip()
                if 8 <= len(sach) <= 220:
                    ket.add(sach)
        khoi = []
    return ket


def quet_mot_nguon(s: dict, noi_dung: str, state: dict, *,
                    la_van_ban_thuan: bool = False) -> tuple[list[str], bool]:
    """So với state cũ. Trả (tiêu đề MỚI, có_thay_đổi_thuần_giao_diện).
    `la_van_ban_thuan=True` khi `noi_dung` là văn bản đã tải qua Browser thật
    (xem `rut_tieu_de_tu_van_ban`), không phải HTML thô."""
    cu = state.get(s["id"], {})
    tieu_de = (rut_tieu_de_tu_van_ban(noi_dung) if la_van_ban_thuan
               else rut_tieu_de(noi_dung))
    moi = sorted(tieu_de - set(cu.get("titles", [])))
    hash_moi = hashlib.sha256(noi_dung.encode("utf-8", "replace")).hexdigest()
    chi_giao_dien = (not moi) and cu.get("hash") and cu["hash"] != hash_moi
    state[s["id"]] = {"hash": hash_moi, "titles": sorted(tieu_de),
                      "luc": date.today().isoformat()}
    return moi, bool(chi_giao_dien)


def _fetch(url: str) -> str | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent":
                                     "Mozilla/5.0 EBM-org-watch/1.0 (+bac si ngoai tru)"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read(400_000).decode("utf-8", "replace")
    except (urllib.error.URLError, OSError, ValueError):
        return None


def kiem_tra_tram(nguon: list[dict]) -> dict[str, dict]:
    """Dò SỐNG mọi trạm rss/html-watch CÓ endpoint (kể cả not-covered) — CHỈ ĐO,
    không đổi state/sổ. Dùng CHÍNH _fetch + rut_tieu_de của trạm để câu trả lời
    là «trạm chạy được như code hiện tại không», không phải một phép đo khác rồi suy.

    VÌ SAO CÓ (29/08/2026): đã đo từ phiên cloud — mọi host hội bị chính sách
    mạng chặn (CONNECT 403), kể cả WebFetch ⇒ xác minh sống URL hội KHÔNG khả thi
    từ sandbox. Đường hoàn tất duy nhất là chạy phép dò này trên máy thật (ngoài
    sandbox); trước đây «bác sĩ xác minh URL» là việc tay không có công cụ."""
    kq: dict[str, dict] = {}
    for s in nguon:
        if s.get("access") not in ("rss", "html-watch") or not s.get("endpoint_or_url"):
            continue
        nd = _fetch(s["endpoint_or_url"])
        if nd is None:
            kq[s["id"]] = {"ok": False, "so_tieu_de": 0,
                           "ly_do": "fetch hỏng (mạng/chặn egress/URL sai)"}
            continue
        so = len(rut_tieu_de(nd))
        kq[s["id"]] = {"ok": so >= 1, "so_tieu_de": so,
                       "ly_do": None if so >= 1 else
                       "fetch OK nhưng 0 tiêu đề — parser không đọc được trang này"}
    return kq


def bat_neu_ok(du: dict, kq: dict[str, dict]) -> list[str]:
    """Đổi status not-covered → active CHỈ cho trạm vừa dò ĐẠT (fetch OK + ≥1 tiêu
    đề), ghi kèm bằng chứng kích hoạt. Trả về danh sách id đã bật. KHÔNG ghi đĩa —
    caller quyết (và phải sao lưu trước khi ghi)."""
    bat: list[str] = []
    for s in du["sources"]:
        r = kq.get(s["id"])
        if r and r["ok"] and s.get("status") == "not-covered":
            s["status"] = "active"
            s["kich_hoat"] = {"ngay": date.today().isoformat(),
                             "bang": "giam_sat_to_chuc --bat-neu-ok",
                             "so_tieu_de_luc_do": r["so_tieu_de"]}
            bat.append(s["id"])
    return bat


def _duong_dan_hien_thi(f: Path) -> str:
    """In đường dẫn NGẮN (tương đối GOC) khi có thể, tuyệt đối khi không — việc
    HIỂN THỊ một đường dẫn cho người đọc không bao giờ được phép làm crash cả
    hàm (bắt được qua test dùng tmp_path: RA trỏ ngoài GOC khiến relative_to
    ném ValueError)."""
    try:
        return str(f.relative_to(GOC))
    except ValueError:
        return str(f)


def _ghi_ung_vien(phat_hien: list[str]) -> Path | None:
    """Ghi file ứng viên, DÙNG CHUNG định dạng với luồng quét chính (main()) —
    tách hàm để _nap_van_ban() không chép lại logic ghi file.

    GỘP với file CÙNG NGÀY đã có, không ghi đè (vá 13/09/2026): trước đây
    f.write_text() ghi đè thẳng, nên gọi --nap-van-ban nhiều trạm khác nhau
    trong CÙNG một ngày làm mất sạch ứng viên của các trạm chạy trước — chỉ
    trạm chạy CUỐI CÙNG còn xuất hiện trong file, dù state/giam-sat-to-chuc.json
    (theo dõi trùng lặp cho lần quét sau) vẫn lưu đúng cho từng trạm. Lỗi im
    lặng: không báo động gì, chỉ đơn giản là bác sĩ không bao giờ thấy được
    ứng viên của các trạm chạy trước trong ngày đó."""
    if not phat_hien:
        return None
    RA.mkdir(parents=True, exist_ok=True)
    f = RA / f"to-chuc-{date.today().isoformat()}.md"
    da_co: list[str] = []
    if f.exists():
        for dong in f.read_text(encoding="utf-8").splitlines():
            if dong.startswith("- **") and dong not in da_co:
                da_co.append(dong)
    gop = da_co + [dong for dong in phat_hien if dong not in da_co]
    f.write_text("# ỨNG VIÊN TỪ TRẠM TỔ CHỨC — " + date.today().isoformat()
                 + "\n\n" + "\n".join(gop)
                 + "\n\n> Cần bác sĩ kiểm chứng.\n", encoding="utf-8")
    return f


def _nap_van_ban(sid: str, duong_dan: str) -> int:
    """Hoàn tất MỘT chu kỳ quét cho một trạm bằng nội dung đã tải qua Browser
    thật (xem docstring `rut_tieu_de_tu_van_ban`). Chạy CÙNG logic so-sánh/
    ghi-state/ghi-ứng-viên với luồng quét chính trong main() — chỉ khác nguồn
    nội dung (file văn bản thay vì fetch urllib trực tiếp), để hai đường
    không lệch hành vi theo thời gian."""
    try:
        du = json.loads(SO_NGUON.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"🔴 Sổ nguồn hỏng: {exc}")
        return 2
    s = next((x for x in du["sources"] if x["id"] == sid), None)
    if s is None:
        print(f"🔴 Không thấy trạm {sid} trong data/sources.json")
        return 2
    try:
        van_ban = Path(duong_dan).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"🔴 Không đọc được {duong_dan}: {exc}")
        return 2
    if len(van_ban.strip()) < 200:
        print(f"🔴 Nội dung quá ngắn ({len(van_ban)} ký tự) — nghi trang chưa tải "
              f"xong hoặc bị chặn; KHÔNG ghi gì để tránh coi 'chặn' là 'không có tin mới'.")
        return 2

    state = {}
    if STATE.exists():
        try:
            state = json.loads(STATE.read_text(encoding="utf-8"))
        except ValueError:
            state = {}
    moi, giao_dien = quet_mot_nguon(s, van_ban, state, la_van_ban_thuan=True)
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")

    so_tieu_de_tong = len(state.get(sid, {}).get("titles", []))
    s["last_success_at"] = date.today().isoformat()
    da_bat = False
    if s.get("status") == "not-covered" and so_tieu_de_tong >= 1:
        s["status"] = "active"
        s["kich_hoat"] = {"ngay": date.today().isoformat(),
                          "bang": "giam_sat_to_chuc --nap-van-ban (Browser thật, "
                                  "urllib bị chặn bot-challenge)",
                          "so_tieu_de_luc_do": so_tieu_de_tong}
        da_bat = True
    du["updated"] = date.today().isoformat()
    SO_NGUON.write_text(json.dumps(du, ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8")

    phat_hien = [f"- **{s['org']}** · phát hiện {date.today().isoformat()} · "
                 f"source.type=guideline · «{t}» — [CẦN KIỂM CHỨNG] đối chiếu "
                 f"trang gốc trước khi vào hàng ứng viên (nạp qua Browser thật)"
                 for t in moi]
    f = _ghi_ung_vien(phat_hien)
    if da_bat:
        print(f"🟢 {sid} {s['org']}: BẬT not-covered→active ({so_tieu_de_tong} tiêu đề)")
    if giao_dien:
        print("  (trang đổi thuần giao diện, 0 tiêu đề mới)")
    if f:
        print(f"🟠 {len(phat_hien)} tiêu đề mới → {_duong_dan_hien_thi(f)}")
    elif not moi:
        print(f"◌ {sid}: {so_tieu_de_tong} tiêu đề đã biết, 0 tiêu đề MỚI so với lần trước.")
    return 1 if phat_hien else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Trạm quan sát guideline theo tổ chức")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--kiem-tra", action="store_true",
                    help="dò sống mọi trạm có endpoint (kể cả not-covered), chỉ đo không ghi")
    ap.add_argument("--bat-neu-ok", action="store_true",
                    help="dò sống rồi BẬT (not-covered→active) trạm nào dò đạt; sao lưu sổ trước khi ghi")
    ap.add_argument("--nap-van-ban", nargs=2, metavar=("ID", "FILE"),
                    help="nạp nội dung ĐÃ TẢI SẴN qua Browser thật (văn bản thuần, "
                         "vd get_page_text) cho một trạm — dùng khi urllib bị "
                         "chặn (Cloudflare bot-challenge) nhưng trình duyệt thật "
                         "tải được; ĐẠT lần đầu ⇒ tự bật not-covered→active")
    a = ap.parse_args()
    if a.self_test:
        return _self_test()

    if a.nap_van_ban:
        return _nap_van_ban(*a.nap_van_ban)

    if a.kiem_tra or a.bat_neu_ok:
        try:
            du = json.loads(SO_NGUON.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            print(f"🔴 Sổ nguồn hỏng: {exc}")
            return 2
        kq = kiem_tra_tram(du["sources"])
        if not kq:
            print("◌ Không trạm rss/html-watch nào có endpoint để dò.")
            return 0
        for sid, r in sorted(kq.items()):
            dau = "✓" if r["ok"] else "✗"
            print(f"  {dau} {sid}: {r['so_tieu_de']} tiêu đề" +
                  (f" — {r['ly_do']}" if r["ly_do"] else ""))
        if a.bat_neu_ok:
            bat = bat_neu_ok(du, kq)
            if bat:
                sao_luu = SO_NGUON.with_suffix(
                    f".json.bak-{date.today().isoformat()}")
                sao_luu.write_text(SO_NGUON.read_text(encoding="utf-8"),
                                   encoding="utf-8")
                du["updated"] = date.today().isoformat()
                SO_NGUON.write_text(json.dumps(du, ensure_ascii=False, indent=1)
                                    + "\n", encoding="utf-8")
                print(f"🟢 Đã BẬT {len(bat)} trạm: {', '.join(bat)} "
                      f"(sao lưu: {sao_luu.name})")
            else:
                print("◌ Không trạm not-covered nào dò đạt — sổ giữ nguyên.")
        return 0 if all(r["ok"] for r in kq.values()) else 1

    try:
        du = json.loads(SO_NGUON.read_text(encoding="utf-8"))
        nguon = du["sources"]
    except (OSError, ValueError, KeyError) as exc:
        print(f"🔴 Sổ nguồn hỏng: {exc}")
        return 2
    muc_tieu = [s for s in nguon if s["access"] in ("rss", "html-watch")
                and s.get("endpoint_or_url") and s["status"] != "not-covered"]
    if not muc_tieu:
        cho = [s["id"] for s in nguon if s["access"] in ("rss", "html-watch")]
        print(f"◌ 0 trạm đang bật. {len(cho)} trạm NẰM CHỜ endpoint đã xác minh + "
              f"egress: {', '.join(cho)}")
        print("  → bác sĩ xác minh URL chính thức, điền endpoint_or_url và đổi "
              "status trong data/sources.json — trạm chạy ngay, không sửa code.")
        return 0

    state = {}
    if STATE.exists():
        try:
            state = json.loads(STATE.read_text(encoding="utf-8"))
        except ValueError:
            state = {}
    phat_hien: list[str] = []
    hong: list[str] = []
    for s in muc_tieu:
        nd = _fetch(s["endpoint_or_url"])
        if nd is None:
            s["status"] = "degraded"
            hong.append(f"{s['id']} {s['org']} — fetch hỏng ⇒ chuyên khoa "
                        f"{'/'.join(s['domain'])} đang MÙ ở làn web (PubMed-lane vẫn chạy)")
            continue
        s["last_success_at"] = date.today().isoformat()
        moi, giao_dien = quet_mot_nguon(s, nd, state)
        for t in moi:
            phat_hien.append(f"- **{s['org']}** · phát hiện {date.today().isoformat()} · "
                             f"source.type=guideline · «{t}» — [CẦN KIỂM CHỨNG] đối chiếu "
                             f"trang gốc trước khi vào hàng ứng viên")
        if giao_dien:
            print(f"  (bỏ qua {s['id']}: trang đổi thuần giao diện, 0 tiêu đề mới)")

    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
    # Ghi CHÍNH đối tượng đã sửa (degraded/last_success) — đọc lại từ đĩa ở đây
    # sẽ lặng lẽ vứt các đánh dấu vừa đặt, tức «nguồn hỏng im lặng» ngay trong
    # công cụ chống nguồn-hỏng-im-lặng.
    du["updated"] = date.today().isoformat()
    SO_NGUON.write_text(json.dumps(du, ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8")
    f = _ghi_ung_vien(phat_hien)
    if f:
        print(f"🟠 {len(phat_hien)} tiêu đề mới → {_duong_dan_hien_thi(f)}")
    for h in hong:
        print("  ✗ " + h)
    return 1 if (phat_hien or hong) else 0


def _self_test() -> int:
    """Giả lập «hội đăng guideline mới» — phải bắt trong 1 chu kỳ, giao diện đổi phải im."""
    v1 = """<html><div class=old><h2>GOLD Report 2025 — Global Strategy for COPD</h2>
            <a href=/x>Pocket Guide 2025</a><p>giới thiệu hội</p></html>"""
    v1b = """<html><section class=new-layout><table><tr><td>
             <h3>GOLD Report 2025 — Global Strategy for COPD</h3></td></tr></table>
             <a href=/y>Pocket Guide 2025</a><footer>đổi giao diện</footer></html>"""
    v2 = v1b.replace("</html>", "<a href=/z>2026 GOLD Report — NEW</a></html>")
    s = {"id": "TEST", "org": "GOLD", "domain": ["hô hấp"]}
    st: dict = {}
    moi1, gd1 = quet_mot_nguon(s, v1, st)
    moi1b, gd1b = quet_mot_nguon(s, v1b, st)
    moi2, _gd2 = quet_mot_nguon(s, v2, st)
    ok = True
    print(f"  lượt 1 (nền): {len(moi1)} tiêu đề nạp — OK")
    if moi1b or not gd1b:
        print(f"  ✗ đổi THUẦN GIAO DIỆN mà báo {moi1b} — báo động giả")
        ok = False
    else:
        print("  ✓ đổi thuần giao diện → 0 cảnh báo, nhận diện đúng là giao diện")
    if moi2 == ["2026 GOLD Report — NEW"]:
        print("  ✓ guideline MỚI bắt được trong 1 chu kỳ:", moi2[0])
    else:
        print(f"  ✗ không bắt được guideline mới (được: {moi2})")
        ok = False
    print("🟢 self-test ĐẠT" if ok else "🔴 self-test TRƯỢT")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
