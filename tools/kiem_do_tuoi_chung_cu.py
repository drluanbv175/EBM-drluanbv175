#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nhắc khi GIÁM SÁT CHỨNG CỨ quá hạn — thay cho lịch launchd vốn không nổ.

VÌ SAO CÓ (11/08/2026):
Hai job launchd `com.medicalebm.weeklysafety` (thứ Bảy 19:00) và
`com.medicalebm.monthlyupdate` (mùng 1, 18:00) khi kiểm thực tế đều cho
`runs = 0` · `last exit code = (never exited)`, log 0 byte từ 06/06 — tức
**chưa từng chạy một lần nào** kể từ khi cài (11/07). Từ đó tới nay đã lỡ 5 thứ
Bảy và 1 mùng 1.

Nguyên nhân: `StartCalendarInterval` của launchd đòi máy phải ĐANG THỨC đúng
thời điểm. MacBook đóng nắp lúc 19:00 thứ Bảy thì job không chạy, và launchd
không bù lại một cách đáng tin.

Máy móc bên dưới KHÔNG hỏng — chạy `weekly_safety.sh --canary` ngày 11/08 cho
PASS toàn bộ: 4/4 nguồn khoẻ (PubMed · Europe PMC · Crossref · openFDA),
scanner tìm được ứng viên, cổng dashboard strict PASS. Chỉ là không ai bật.

Nên cách vá hợp thói quen bác sĩ nhất: bác sĩ mở phiên Claude gần như mỗi ngày,
vậy NHẮC ngay lúc mở phiên. Không phụ thuộc máy có thức lúc 19:00 hay không.

Công cụ này CHỈ NHẮC, không tự chạy giám sát: quét chứng cứ là việc gọi mạng và
sinh nội dung y khoa, phải do bác sĩ chủ động và duyệt kết quả.

Dùng:
    python3 tools/kiem_do_tuoi_chung_cu.py            # in trạng thái
    python3 tools/kiem_do_tuoi_chung_cu.py --im-khi-on  # chỉ nói khi quá hạn (hook)

Mã thoát: 0 = còn hạn · 1 = quá hạn.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]
DASH = REPO / "EBM-Dashboards"
LOG_TUAN = REPO / "medical-ebm-automation/data/archive/launchd_weekly.log"
LOG_THANG = REPO / "medical-ebm-automation/data/archive/launchd_monthly.log"

# Vá 15/09/2026 (workflow kiểm tra toàn diện): mục (2) bên dưới đọc log giám sát
# hằng tuần dưới medical-ebm-automation/ — trên bản sao git trần (mọi phiên
# cloud, clone tươi, CI) thư mục đó KHÔNG TỒN TẠI, nên trước bản vá này công cụ
# luôn kết luận "CHƯA TỪNG chạy" — đúng lớp lỗi BH08 (gộp KHÔNG BIẾT với CÓ VẤN
# ĐỀ) mà các chốt anh em (kiem_nguon_that, chot_hoi_quy_bai_hoc, verify_*) đã
# tránh bằng cách tra tools/ban_sao_tran.py trước khi kết luận. Nạp động (không
# `import` thẳng) theo đúng khuôn đã dùng ở xuat_goi_cap_nhat.py/chot_hoi_quy_
# bai_hoc.py, vì file này chạy như script độc lập (python3 tools/<tên>.py).
_spec_bst = importlib.util.spec_from_file_location(
    "_bst_kdtcc", Path(__file__).resolve().parent / "ban_sao_tran.py")
_bst = importlib.util.module_from_spec(_spec_bst)
_spec_bst.loader.exec_module(_bst)

# Ngưỡng nới hơn chu kỳ danh nghĩa: job tuần trễ 3 ngày chưa đáng gọi là bỏ bê.
HAN_AN_TOAN_NGAY = 10      # giám sát an toàn thuốc: chu kỳ tuần
HAN_CAP_NHAT_NGAY = 35     # cập nhật guideline: chu kỳ tháng
# Ngưỡng RIÊNG cho "chủ đề lâu chưa xem lại", cố ý cao hơn HAN_CAP_NHAT_NGAY nhiều.
# Lý do là chống nhờn cảnh báo: ở nhịp làm việc thật, phần lớn chủ đề luôn quá 35 ngày
# (đo 14/08: 37/59), nên lấy 35 làm ngưỡng báo động sẽ khiến mỗi phiên đều đỏ và bác sĩ
# học cách bỏ qua — lúc đó cảnh báo thật cũng chìm theo. 120 ngày là mức mà "chưa xem
# lại" khó biện minh với gần như mọi lĩnh vực.
HAN_RAT_LAU_NGAY = 120


def ngay_tu_ten(p: Path) -> dt.date | None:
    """Lấy ngày từ đuôi tên file `..._YYYYMMDD.html` — đáng tin hơn mtime, vì
    mtime bị OneDrive và các lần dựng lại vỏ (reskin) làm nhiễu."""
    m = re.search(r"_(\d{8})\.html$", p.name)
    if not m:
        return None
    try:
        return dt.datetime.strptime(m.group(1), "%Y%m%d").date()
    except ValueError:
        return None


def lan_chay_cuoi(log: Path) -> tuple[dt.date | None, str]:
    """(ngày lần chạy cuối, trạng thái) — trạng thái ∈ PASS · LỖI · KHONG_CAN_LAP_LAI · DANG_DO · "".

    VÁ 13/08/2026 — bản cũ CHỈ đọc `st_mtime` rồi kết luận "còn hạn". Nhưng hai script
    giám sát ghi dòng "BẮT ĐẦU" vào log **NGAY khi khởi động**, trước khi làm bất cứ
    việc gì ⇒ một lượt chạy KHỞI ĐỘNG RỒI CHẾT vẫn làm mtime tươi mới, và bác sĩ nhận
    "🟢 CHỨNG CỨ còn hạn" trong khi giám sát thật sự đã hỏng.

    Từ khi `tu_khoi_dong.py` tự phóng mỗi phiên, điều này thành vòng lặp im lặng:
    phóng → hỏng → mtime tươi → "còn hạn" → không ai biết. Chính log ĐÃ chứa câu trả
    lời (dòng "KẾT THÚC … tổng thể=PASS | CÓ BƯỚC LỖI") — chỉ là chưa ai đọc.

    VÁ 22/09/2026 (phản biện vòng 2, review:cong-rut-bai #8) — thêm nhãn thứ ba
    `KHONG_CAN_LAP_LAI`, đọc từ "tổng thể=KHÔNG CẦN LẶP LẠI" mà `quarterly_superseded.sh`
    nay ghi cho ba tình trạng TẤT ĐỊNH (0 mục để dò / lượt bị giới hạn cố ý / thiếu công
    cụ) — KHÁC "LỖI" thật (mạng hỏng, thiếu PMID). Người tiêu thụ (`tu_khoi_dong.qua_han()`)
    phải phân biệt được hai nhãn này: "LỖI" đáng phóng lại NGAY bất kể số ngày, còn
    "KHONG_CAN_LAP_LAI" thì retry ngay không giúp gì — chỉ nên chờ tới hạn ngày như PASS.
    """
    if not (log.exists() and log.stat().st_size > 0):
        return None, ""
    ngay = dt.date.fromtimestamp(log.stat().st_mtime)
    try:
        dong = log.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ngay, ""
    for d in reversed(dong):
        if "KẾT THÚC" in d:
            if "tổng thể=PASS" in d:
                return ngay, "PASS"
            if "tổng thể=KHÔNG CẦN LẶP LẠI" in d:
                return ngay, "KHONG_CAN_LAP_LAI"
            return ngay, "LỖI"
        if "BẮT ĐẦU" in d:
            # Gặp BẮT ĐẦU trước KẾT THÚC ⇒ lượt cuối chưa khép lại: đang chạy, hoặc
            # đã chết giữa chừng. Cả hai đều KHÔNG được coi là một lượt giám sát xong.
            return ngay, "DANG_DO"
    return ngay, ""


def launchd_runs(nhan: str) -> int | None:
    """Số lần job launchd đã chạy — CHỈ macOS mới có launchd.

    Trên Windows trả None (không phải lỗi): ở đó không có lịch nền nào để hỏi,
    nhưng chốt này vẫn nhắc được theo dấu vết log và ngày gói chứng cứ.

    VÁ 12/08/2026: bản cũ gọi `getattr(os, "getuid", lambda: 0)()` — hàm KHÔNG tồn tại trên Windows —
    và chỉ bắt (OSError, SubprocessError), nên AttributeError lọt ra ngoài làm
    CHẾT cả công cụ. Vì hook SessionStart kết thúc bằng `; true`, lỗi bị nuốt
    IM LẶNG: suốt thời gian qua máy Windows không hề được nhắc độ tươi chứng cứ
    mà không ai biết. Đây đúng lớp lỗi "công cụ dùng chung gãy im lặng trên
    Windows" đã gặp nhiều lần — nên bắt Exception rộng, không đoán trước tên lỗi.
    """
    if sys.platform != "darwin":
        return None
    import os

    try:
        uid = getattr(os, "getuid", lambda: 0)()   # PEP 701 chỉ có từ 3.12; sàn khai là 3.11
        r = subprocess.run(["launchctl", "print", f"gui/{uid}/{nhan}"],
                           capture_output=True, text=True, timeout=10, encoding="utf-8", errors="replace")
        m = re.search(r"runs = (\d+)", r.stdout)
        return int(m.group(1)) if m else None
    except Exception:  # noqa: BLE001 — chốt nhắc không được phép làm chết phiên
        return None


def lau_chua_xem_lai() -> list[tuple[str, int]]:
    """[(lát cắt, số ngày kể từ bản mới nhất của nó)] — xếp cũ nhất lên đầu.

    VÌ SAO CÓ (14/08/2026, vòng lặp kiểm tra–hoàn thiện vòng 3): mục (1) của công cụ
    này lấy `max(ngày)` trên toàn kho, nên **một gói mới làm cả kho trông còn hạn**.
    Đo thật hôm nay: gói mới nhất 1 ngày tuổi ⇒ in 🟢, trong khi 37/59 chủ đề đã quá
    35 ngày và trung vị là 45 ngày. Bác sĩ đọc dòng 🟢 đó sẽ tin rằng mọi chủ đề đều
    vừa được rà — đúng loại bảo đảm sai mà kho này đã vấp nhiều lần.

    Đơn vị đếm là LÁT CẮT, không phải file: ba bản SuyTim_TongHop nối tiếp nhau chỉ
    là một chủ đề được xem lại ba lần, không phải ba chủ đề.

    Công cụ CHỈ ĐO, không phán "đã lỗi thời": nhịp cập nhật của mỗi lĩnh vực rất khác
    nhau (cảnh báo thuốc tính bằng tuần, guideline tính bằng năm), và quyết định xem
    lại chủ đề nào trước là của bác sĩ.
    """
    import datetime as _dt
    hom_nay = _dt.date.today()
    moi_nhat: dict[str, _dt.date] = {}
    for p in DASH.glob("WebDashboard_*.html"):
        d = ngay_tu_ten(p)
        if not d:
            continue
        # Lát cắt = tên file bỏ tiền tố nhóm và bỏ ngày.
        m = re.match(r"WebDashboard_EBM_(?:VanDeCuThe|Uptodate|CapNhatTuan|AnToanThuoc|"
                     r"CongCuKeDon)_(?:(.+?)_)?\d{8}\.html$", p.name)
        if not m:
            continue
        lc = m.group(1) or p.name.split("_")[2]
        if lc not in moi_nhat or d > moi_nhat[lc]:
            moi_nhat[lc] = d
    return sorted(((k, (hom_nay - v).days) for k, v in moi_nhat.items()),
                  key=lambda kv: -kv[1])


def doc_khong_can() -> dict:
    """Các chủ đề gốc / lát cắt bác sĩ khai «cố ý không canh» (bản tin tuần GỘP) trong giam-sat-chu-de.json."""
    import json as _json
    try:
        return dict(_json.loads((DASH / "giam-sat-chu-de.json").read_text(encoding="utf-8")).get("khong_can") or {})
    except (OSError, ValueError):
        return {}


def la_khong_can(lat_cat: str, khong_can: dict) -> bool:
    """Bản tin gộp KHÔNG thể «xem lại» thành một chủ đề (T1-12, 20/09/2026): 12/64 lát cắt là loại này. Không loại
    thì từ ~06/10 chúng vượt ngưỡng 120 ngày và hook nhắc MỖI phiên một mục không bao giờ gỡ được — đúng kiểu
    cảnh báo bị bác sĩ học cách bỏ qua, kéo theo cảnh báo thật chìm."""
    return lat_cat in khong_can or lat_cat.split("_")[0] in khong_can


def in_bang_tuoi(lau: list[tuple[str, int]], khong_can: dict | None = None) -> None:
    """In phân bố tuổi để dòng 🟢 ở trên không bị đọc quá rộng."""
    if not lau:
        return
    tuoi = [t for _k, t in lau]
    qua = sum(1 for t in tuoi if t > HAN_CAP_NHAT_NGAY)
    print(f"   {len(lau)} chủ đề · trung vị {sorted(tuoi)[len(tuoi) // 2]} ngày kể từ lần "
          f"xem lại · {qua} chủ đề quá {HAN_CAP_NHAT_NGAY} ngày")
    if qua:
        lam_moi_duoc = [x for x in lau if not la_khong_can(x[0], khong_can or {})]
        ten = " · ".join(f"{k} ({t}ng)" for k, t in lam_moi_duoc[:5])
        print(f"   Lâu nhất: {ten}")
        if khong_can is not None and len(lam_moi_duoc) < len(lau):
            print(f"   ({len(lau) - len(lam_moi_duoc)} bản tin gộp không tính vào «lâu nhất» — không thể làm mới thành một chủ đề)")
        print("   (Đây là số ĐO, không phải phán quyết 'đã lỗi thời' — nhịp cập nhật mỗi")
        print("    lĩnh vực một khác, chọn chủ đề xem lại trước là quyết định của bác sĩ.)")


def main() -> int:
    ap = argparse.ArgumentParser(description="Nhắc khi giám sát chứng cứ quá hạn")
    ap.add_argument("--im-khi-on", action="store_true",
                    help="không in gì khi còn hạn (dùng cho hook)")
    a = ap.parse_args()

    hom_nay = dt.date.today()
    canh_bao: list[str] = []
    ngoai_pham_vi: list[str] = []

    # 1) Gói chứng cứ mới nhất — thước đo trực tiếp nhất của "hệ có đang sống không"
    ngays = [d for d in (ngay_tu_ten(p) for p in DASH.glob("WebDashboard_*.html")) if d]
    mới_nhất = max(ngays) if ngays else None
    if mới_nhất:
        cach = (hom_nay - mới_nhất).days
        if cach > HAN_CAP_NHAT_NGAY:
            canh_bao.append(
                f"Gói chứng cứ mới nhất là {mới_nhất:%d/%m/%Y} — cách đây {cach} ngày "
                f"(ngưỡng {HAN_CAP_NHAT_NGAY}). Chạy `/cap-nhat-chung-cu <vấn đề>` "
                f"cho chủ đề đang cần.")

    # 2) Giám sát an toàn thuốc hằng tuần — CỐ Ý bỏ qua khi medical-ebm-automation/
    # hoàn toàn vắng mặt (bản sao git trần: mọi phiên cloud, clone tươi, CI). Thiếu
    # NGUYÊN LIỆU để đo (thư mục cha không tồn tại) KHÔNG được kết luận thành "chưa
    # từng chạy" — đó là câu trả lời cho máy CÓ dữ liệu nhưng job không nổ, khác hẳn
    # câu trả lời đúng ở đây là "không đo được" (BH08).
    if _bst.duong_goc("medical-ebm-automation", REPO) is None:
        ngoai_pham_vi.append(
            "Giám sát an toàn thuốc hằng tuần: KHÔNG đo được — thư mục "
            "medical-ebm-automation/ không có trên máy này (bản sao git trần). "
            "Chạy trên máy có đủ cây dữ liệu OneDrive để canh mục này.")
    else:
        _kiem_giam_sat_tuan(canh_bao, hom_nay, sys.platform)

    # 3) TUỔI TỪNG CHỦ ĐỀ — thứ mà `max()` ở mục (1) không nói được.
    lau = lau_chua_xem_lai()
    khong_can = doc_khong_can()
    rat_lau = [x for x in lau if x[1] > HAN_RAT_LAU_NGAY and not la_khong_can(x[0], khong_can)]
    if rat_lau:
        ten = ", ".join(f"{k} ({t}ng)" for k, t in rat_lau[:3])
        canh_bao.append(
            f"{len(rat_lau)} chủ đề chưa xem lại quá {HAN_RAT_LAU_NGAY} ngày: {ten}"
            + (f" và {len(rat_lau) - 3} chủ đề nữa" if len(rat_lau) > 3 else "")
            + ". Chạy `python3 ops/orchestrator.py --cu-nhat 3 --online` (máy làm phần quét/kiểm) rồi "
              "`/cap-nhat-chung-cu <chủ đề>` cho mục cần trước.")

    if not canh_bao:
        if not a.im_khi_on:
            # NÓI ĐÚNG THỨ ĐÃ ĐO. Câu cũ "CHỨNG CỨ còn hạn" suy từ `max(ngày)` — tức
            # chỉ cần MỘT gói mới là cả kho trông còn hạn. Đo 14/08/2026: gói mới nhất
            # 1 ngày tuổi trong khi 37/59 chủ đề đã quá 35 ngày, trung vị 45 ngày. Một
            # dòng 🟢 đọc thành "mọi chủ đề đều mới" là lời bảo đảm không có cơ sở —
            # cùng lớp lỗi BH15/BH30: con số không đo thứ nó tự nhận là đang đo.
            print(f"🟢 HỆ GIÁM SÁT còn hoạt động — gói mới nhất {mới_nhất:%d/%m/%Y}"
                  if mới_nhất else "🟢 HỆ GIÁM SÁT còn hoạt động")
            in_bang_tuoi(lau, khong_can)
            for x in ngoai_pham_vi:
                print(f"   ⚪ {x}")
        return 0

    if a.im_khi_on:
        print("")
    print("🟡 GIÁM SÁT CHỨNG CỨ QUÁ HẠN")
    for c in canh_bao:
        print(f"   • {c}")
    # Vá 14/09/2026 (workflow kiểm tra toàn diện): in_bang_tuoi() trước đây chỉ
    # được gọi bên trong nhánh `if not canh_bao:` — tức bảng median/phân bố tuổi
    # bị NUỐT MẤT mỗi khi có BẤT KỲ cảnh báo nào khác (vd "giám sát an toàn thuốc
    # chưa từng chạy"), dù chính bảng đó mới trả lời "chủ đề nào lâu chưa xem lại
    # NHẤT". Ở nhịp làm việc thật gần như luôn có ít nhất một cảnh báo khác, nên
    # bảng này gần như không bao giờ hiện ra. Nay in cả ở nhánh 🟡.
    in_bang_tuoi(lau, khong_can)
    for x in ngoai_pham_vi:
        print(f"   ⚪ {x}")
    print("   (Chốt này chỉ NHẮC — quét chứng cứ phải do bác sĩ chủ động và duyệt kết quả.)")
    return 1


def _kiem_giam_sat_tuan(canh_bao: list[str], hom_nay: dt.date, platform: str) -> None:
    """Tách khỏi main() khi vá 15/09/2026 để nhánh «medical-ebm-automation vắng
    mặt» ở trên không phải chép lại logic — hành vi giữ NGUYÊN như trước bản vá
    cho máy THẬT có repo y khoa."""
    chay_tuan, tt_tuan = lan_chay_cuoi(LOG_TUAN)
    runs = launchd_runs("com.medicalebm.weeklysafety")
    if chay_tuan is None:
        if platform == "darwin":
            n = "" if runs is None else f" (launchd runs = {runs})"
            ly_do = (f"{n}. Lịch launchd đòi máy thức lúc 19:00 thứ Bảy nên hay lỡ")
        else:
            # Ngoài macOS KHÔNG có launchd — hai job com.medicalebm.* chỉ tồn tại trên Mac.
            # Nói rõ điều này, thay vì để bác sĩ tưởng có lịch nền đang chạy hộ.
            # 28/08/2026: không ghi cứng "(Windows)" — chạy trên Linux (phiên cloud/CI)
            # mà tự xưng là Windows là nói sai về chính máy đang đứng.
            ten_nen = {"win32": "Windows", "linux": "Linux"}.get(platform, platform)
            ly_do = (f". Máy này ({ten_nen}) KHÔNG có lịch nền nào chạy giám sát — "
                     "hai job launchd chỉ tồn tại trên MacBook, nên ở đây luôn phải chạy tay")
        canh_bao.append(
            f"Giám sát AN TOÀN THUỐC hằng tuần CHƯA TỪNG chạy{ly_do}. Chạy tay khi tiện:\n"
            f"     bash medical-ebm-automation/scripts/weekly_safety.sh\n"
            f"     (kiểm nhanh nguồn, không ghi gì: thêm `--canary`)")
    else:
        cach = (hom_nay - chay_tuan).days
        # Lượt chạy HỎNG hoặc chưa khép lại KHÔNG được tính là một lượt giám sát xong,
        # dù log vừa được ghi (script ghi 'BẮT ĐẦU' ngay lúc khởi động).
        if tt_tuan == "LỖI":
            canh_bao.append(
                f"Giám sát an toàn thuốc lượt cuối ({chay_tuan:%d/%m/%Y}) CÓ BƯỚC LỖI — "
                f"log ghi 'tổng thể=CÓ BƯỚC LỖI'. Chạy lại và đọc "
                f"medical-ebm-automation/data/archive/launchd_weekly.log để biết bước nào.")
        elif tt_tuan == "DANG_DO":
            canh_bao.append(
                f"Giám sát an toàn thuốc lượt cuối ({chay_tuan:%d/%m/%Y}) CHƯA KHÉP LẠI — "
                f"log có 'BẮT ĐẦU' mà không có 'KẾT THÚC': đang chạy dở, hoặc đã chết "
                f"giữa chừng. KHÔNG tính là một lượt giám sát xong.")
        elif cach > HAN_AN_TOAN_NGAY:
            canh_bao.append(
                f"Giám sát an toàn thuốc chạy lần cuối {chay_tuan:%d/%m/%Y} — "
                f"cách đây {cach} ngày (ngưỡng {HAN_AN_TOAN_NGAY}).")


if __name__ == "__main__":
    raise SystemExit(main())
