#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CHỐT SAFETY-NETTING — làm cho lá cờ `enforce_safety_net_templates` có nghĩa thật.

VÌ SAO CÓ (22/08/2026, báo cáo `audit/03-diem-nghen-thuc-hanh-ngoai-tru`):

`clinical_runtime/CLINICAL_RUNTIME_FLAGS.json` khai `enforce_safety_net_templates: true`
từ lâu. Nhưng đo ngày 22/08: `grep` toàn repo trả **0 file tham chiếu** tới
`safety_net_templates.json`, và nội dung file đó là ba mẫu tiếng Anh chung chung
không hội chứng, không tiêu chí đo được, không nguồn.

Đây đúng HỌ lỗi mà `CLAUDE.md` đã ghi ba lần (`return` sớm che 73 mục · BH27
fail-open cổng A12 · BH61 khoá lạ trong `DATA.summary`): **một lá cờ hoặc một
công cụ tuyên bố có thi hành, nhưng thứ cần kiểm thì không bao giờ được kiểm.**
Khác biệt lần này: nó rơi vào tầng AN TOÀN CHO BỆNH NHÂN, không phải tầng
governance — lời dặn "khi nào quay lại" là lưới cuối cùng khi chẩn đoán ban đầu sai,
và độ chính xác chẩn đoán KHÔNG tương quan với độ tự tin của bác sĩ
(55,3% → 5,8% giữa ca dễ và ca khó, tự tin chỉ 7,2 → 6,4/10 —
Meyer 2013, JAMA Intern Med, PMID 23979070, doi:10.1001/jamainternmed.2013.10081).

*Cần bác sĩ kiểm chứng.*

CÔNG CỤ NÀY KIỂM CẤU TRÚC, KHÔNG CHẤM NỘI DUNG Y KHOA. Nó không biết một tiêu chí
cờ đỏ có đúng hay không — nó chỉ bảo đảm: có nguồn truy được · có ít nhất một tiêu
chí ĐO ĐƯỢC · hai trục (cờ đỏ cho bác sĩ ≠ lời dặn cho bệnh nhân) không bị gộp ·
và **độ phủ thật được nói ra** thay vì để một lá cờ `true` nói hộ.

VÁ 2026-09-03 (Workflow đối kháng đa-agent, phát hiện #8): R4/R5/R6 trước đây
CHỈ áp cho khối `co_do_cho_bac_si`, không áp cho `dan_benh_nhan_quay_lai` — dù
trục thứ hai này cũng tự khai `trang_thai: "co-nguon"` và được tính vào độ phủ
báo cho bác sĩ. Ca thật bắt được ngay trên dữ liệu sống: `dau-nguc` khai
`co-nguon` mà vẫn còn nguyên `[CẦN BÁC SĨ ĐIỀN]` bên trong. Nay thêm R10 (nguồn
truy được — biến thể của R4 cho đúng schema của `ld`, xem `_nguon_truy_duoc_ld`)
và R11 (cấm placeholder — mirror trực tiếp của R6). R5 (đo được) CỐ Ý không có
bản sao: `ld.noi_dung[].cau` là câu dặn trực tiếp cho bệnh nhân, khác hẳn
`tieu_chi[].do_duoc` của `cd` — ép cùng luật là đo nhầm chỗ.

Dùng:
    python3 tools/kiem_safety_net.py             # in bảng độ phủ
    python3 tools/kiem_safety_net.py --im-khi-on # chỉ nói khi có lỗi (hook)
    python3 tools/kiem_safety_net.py --json      # máy đọc

Mã thoát: 0 = không lỗi · 1 = có cảnh báo (độ phủ chưa đủ) · 2 = LỖI CỨNG.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]
MAU = REPO / "clinical_runtime" / "safety_net_templates.json"
CO = REPO / "clinical_runtime" / "CLINICAL_RUNTIME_FLAGS.json"

PLACEHOLDER = "[CẦN BÁC SĨ ĐIỀN]"
TRANG_THAI_HOP_LE = {"co-nguon", "chua-dien"}
HAN_RA_SOAT_NGAY = 365

# SỬA (vá "R4 chấp nhận nguồn không định danh được", 2026-09-04): mốc chuẩn dùng
# ĐÚNG ngưỡng đã canonical trong hệ — khớp
# `medical-ebm-automation/app/evidence/citation_validator.py::_PMID`/`_DOI`
# (`^\d{4,9}$` / `^10\.\d{4,9}/\S+$`) — không phát minh ngưỡng mới. Riêng "toàn
# số 0" (`"00000"`) khớp `\d{4,9}` nhưng KHÔNG phải PMID thật (PubMed đánh số
# từ 1, không có PMID 0) nên loại thêm bằng kiểm tra giá trị > 0 ở nơi dùng.
_PMID_HOP_LE = re.compile(r"^\d{4,9}$")
_DOI_HOP_LE = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)
_NAM_HOP_LE = re.compile(r"^(19|20)\d{2}$")


def _nguon_truy_duoc(nguon: object) -> bool:
    """Nguồn phải phân giải được: PMID, hoặc DOI, hoặc guideline kèm năm.

    SỬA (vá "R4 chấp nhận nguồn không định danh được", 2026-09-04): trước bản vá
    `pmid` chỉ đòi `.isdigit()` — không giới hạn độ dài, nên `"0"`/`"00000"`/một
    chuỗi số bất kỳ đều qua dù không phải PMID thật. `doi` chỉ đòi
    `.startswith("10.")` — một DOI thật LUÔN có mã đăng ký (4-9 chữ số) VÀ hậu
    tố sau dấu gạch chéo; chuỗi trơn `"10."` không trỏ tới bài nào cũng qua được.
    `nam` chỉ đòi khác rỗng — `"y"` cũng qua. Cả ba lỗ đều khiến `trang_thai:
    "co-nguon"` + R4 PASS cho một nguồn không ai tra ngược lại được, đúng nghĩa
    "không định danh được" của phát hiện. Đã kiểm bằng dữ liệu THẬT trong
    `safety_net_templates.json` (8/8 hội chứng `co-nguon`, PMID 8 chữ số/DOI
    `10.xxxx/...`/năm 4 chữ số) — không mục nào bị chặn oan bởi bản vá này."""
    if not isinstance(nguon, dict):
        return False
    pmid = str(nguon.get("pmid", "")).strip()
    if _PMID_HOP_LE.match(pmid) and int(pmid) > 0:
        return True
    if _DOI_HOP_LE.match(str(nguon.get("doi", "")).strip()):
        return True
    return bool(str(nguon.get("guideline", "")).strip()
                and _NAM_HOP_LE.match(str(nguon.get("nam", "")).strip()))


_MAU_PMID_DOI = re.compile(r"PMID\s*[:\s]?\d{5,9}|doi\s*:\s*10\.\d{4,9}/", re.IGNORECASE)


def _nguon_truy_duoc_ld(ld: dict) -> bool:
    """Nguồn của khối `dan_benh_nhan_quay_lai` truy được — biến thể của
    `_nguon_truy_duoc()` cho đúng HAI hình dạng dữ liệu THẬT đang tồn tại song
    song trong `safety_net_templates.json` (đo trực tiếp trên file, không suy
    đoán): (a) một `nguon` cấp KHỐI giống hệt `co_do_cho_bac_si` (dau-dau,
    kho-tho, sot, sut-can); (b) KHÔNG có `nguon` cấp khối, mỗi mục trong
    `noi_dung[]` tự mang nguồn riêng qua `ma_nguon` (mã tham chiếu ngược về
    `tieu_chi` của `co_do_cho_bac_si` — đã được R4 xác minh nguồn CHUNG) hoặc
    `nguon_goc` (chuỗi tự do nhúng PMID/DOI, dau-nguc/dau-bung/dau-lung/
    chong-mat). Chấp nhận (a) HOẶC mọi mục đều đạt (b) — không đòi cả hai."""
    if _nguon_truy_duoc(ld.get("nguon")):
        return True
    noi_dung = ld.get("noi_dung")
    if not isinstance(noi_dung, list) or not noi_dung:
        return False
    for muc in noi_dung:
        if not isinstance(muc, dict):
            return False
        if str(muc.get("ma_nguon", "")).strip():
            continue
        if _MAU_PMID_DOI.search(str(muc.get("nguon_goc", ""))):
            continue
        return False
    return True


def kiem(mau: dict, co: dict, hom_nay: dt.date) -> tuple[list[str], list[str], dict]:
    """Trả (lỗi cứng, cảnh báo, số đo độ phủ)."""
    loi: list[str] = []
    canh_bao: list[str] = []

    # R1 — khung bắt buộc
    if not str(mau.get("phien_ban", "")).strip():
        loi.append("R1: thiếu `phien_ban`.")
    hoi_chung = mau.get("hoi_chung")
    if not isinstance(hoi_chung, dict) or not hoi_chung:
        loi.append("R1: thiếu hoặc rỗng khối `hoi_chung` — không có gì để kiểm.")
        return loi, canh_bao, {"tong": 0, "co_nguon": 0, "co_loi_dan": 0}

    co_nguon = 0
    co_loi_dan = 0

    for khoa, hc in sorted(hoi_chung.items()):
        nhan = f"[{khoa}]"
        if not isinstance(hc, dict):
            loi.append(f"R1 {nhan}: mục không phải object.")
            continue

        tt = hc.get("trang_thai")
        # R2 — trạng thái phải tường minh, không suy đoán
        if tt not in TRANG_THAI_HOP_LE:
            loi.append(f"R2 {nhan}: `trang_thai` phải là một trong "
                       f"{sorted(TRANG_THAI_HOP_LE)}, đang là {tt!r}.")
            continue

        # MẶC ĐỊNH PHẢI LÀ `None`, KHÔNG PHẢI `{}`. Bản đầu viết `.get(khoa, {})`
        # nên một hội chứng THIẾU HẲN khối `dan_benh_nhan_quay_lai` vẫn lọt R3 —
        # `{}` là dict nên `isinstance` luôn đúng. Chính test
        # `test_thieu_khoi_loi_dan_bi_chan` bắt được, đúng loại fail-open mà
        # CLAUDE.md đã ghi ba lần: luật CÓ MẶT nhưng không bao giờ chạy tới.
        cd = hc.get("co_do_cho_bac_si")
        ld = hc.get("dan_benh_nhan_quay_lai")

        # R3 — HAI TRỤC KHÔNG ĐƯỢC GỘP. Một danh sách cờ đỏ chuyên môn không dùng
        # làm tờ dặn bệnh nhân được; gộp lại là biến thuật ngữ thành lời khuyên.
        if not isinstance(cd, dict) or not isinstance(ld, dict):
            loi.append(f"R3 {nhan}: phải có ĐỦ HAI khối `co_do_cho_bac_si` và "
                       f"`dan_benh_nhan_quay_lai` (kể cả khi chưa điền).")
            continue

        tieu_chi = cd.get("tieu_chi") or []
        if tt == "co-nguon":
            # R4 — mọi tiêu chí phải truy được nguồn. KHÔNG cho nguồn dạng văn xuôi.
            if not _nguon_truy_duoc(cd.get("nguon")):
                loi.append(f"R4 {nhan}: khai `co-nguon` nhưng `nguon` không truy được "
                           f"(cần PMID, hoặc DOI, hoặc guideline + năm).")
            # R5 — phải có ít nhất MỘT tiêu chí ĐO ĐƯỢC.
            if not any(isinstance(t, dict) and t.get("do_duoc") is True for t in tieu_chi):
                loi.append(f"R5 {nhan}: khai `co-nguon` nhưng KHÔNG có tiêu chí nào "
                           f"`do_duoc: true`. 'nếu nặng hơn' không phải tiêu chí.")
            # R6 — không được để placeholder trong khối đã khai là có nguồn.
            if PLACEHOLDER in json.dumps(cd, ensure_ascii=False):
                loi.append(f"R6 {nhan}: khối `co_do_cho_bac_si` khai `co-nguon` mà "
                           f"vẫn còn {PLACEHOLDER}.")
            # R7 — nguồn có giới hạn thì phải NÓI RA, không im lặng.
            if not str(cd.get("gioi_han_nguyen_van_cua_nguon", "")).strip():
                canh_bao.append(f"R7 {nhan}: chưa ghi giới hạn nguyên văn của nguồn. "
                                f"Một danh sách chưa được kiểm định mà trình bày như đã "
                                f"kiểm định là lời bảo đảm không có cơ sở.")
            co_nguon += 1
        else:
            # Trạng thái `chua-dien` là TRUNG THỰC, không phải lỗi — nhưng phải
            # đếm vào độ phủ để không ai đọc lá cờ `true` thành "đã đủ".
            if PLACEHOLDER not in json.dumps(cd, ensure_ascii=False):
                loi.append(f"R2 {nhan}: khai `chua-dien` mà không có nhãn {PLACEHOLDER} "
                           f"— trạng thái và nội dung nói hai thứ khác nhau.")

        # THÊM 2026-09-03 (Workflow đối kháng đa-agent, phát hiện #8): R4/R5/R6
        # trên `cd` KHÔNG có bản sao cho `ld` — trước bản vá này, một khối
        # `dan_benh_nhan_quay_lai` khai `co-nguon` nhưng còn nguyên
        # `[CẦN BÁC SĨ ĐIỀN]` bên trong (ca THẬT: dau-nguc, tra được ngay trên
        # dữ liệu sống) lọt qua hoàn toàn — chỉ bị đếm vào độ phủ, không hề bị
        # kiểm nội dung. R5 (đo được — `tieu_chi[].do_duoc`) CỐ Ý không có bản
        # sao cho `ld`: hai khối khác schema (`ld.noi_dung[].cau` là câu dặn
        # trực tiếp cho bệnh nhân, không phải danh sách tiêu chí cho bác sĩ
        # chấm) nên ép cùng một luật là đo nhầm chỗ.
        if ld.get("trang_thai") == "co-nguon":
            co_loi_dan += 1
            # R10 — mirror của R4: nguồn phải truy được (xem _nguon_truy_duoc_ld).
            if not _nguon_truy_duoc_ld(ld):
                loi.append(f"R10 {nhan}: `dan_benh_nhan_quay_lai` khai `co-nguon` "
                           f"nhưng nguồn không truy được (cần `nguon` cấp khối, hoặc "
                           f"mỗi mục trong `noi_dung` tự mang `ma_nguon`/`nguon_goc` "
                           f"có PMID/DOI).")
            # R11 — mirror của R6: không placeholder trong khối đã khai có nguồn.
            if PLACEHOLDER in json.dumps(ld, ensure_ascii=False):
                loi.append(f"R11 {nhan}: khối `dan_benh_nhan_quay_lai` khai `co-nguon` "
                           f"mà vẫn còn {PLACEHOLDER}.")

        # R8 — hạn rà soát
        ngay = str(hc.get("ngay_ra_soat", "")).strip()
        try:
            d = dt.date.fromisoformat(ngay)
        except ValueError:
            loi.append(f"R8 {nhan}: `ngay_ra_soat` thiếu hoặc sai định dạng "
                       f"(cần YYYY-MM-DD), đang là {ngay!r}.")
        else:
            if (hom_nay - d).days > HAN_RA_SOAT_NGAY:
                canh_bao.append(f"R8 {nhan}: rà soát lần cuối {d:%d/%m/%Y}, quá "
                                f"{HAN_RA_SOAT_NGAY} ngày.")

    tong = len(hoi_chung)

    # R9 — LUẬT MẠNH NHẤT: lá cờ không được nói hộ.
    # `enforce_safety_net_templates: true` mà 0 hội chứng có nguồn nghĩa là lá cờ
    # đang tuyên bố một sự thi hành không tồn tại. Đó chính xác là tình trạng
    # trước 22/08/2026 và là lý do chốt này ra đời.
    if co.get("enforce_safety_net_templates") is True and co_nguon == 0:
        loi.append("R9: `CLINICAL_RUNTIME_FLAGS.enforce_safety_net_templates = true` "
                   "nhưng KHÔNG hội chứng nào có nguồn — lá cờ đang tuyên bố một sự "
                   "thi hành không tồn tại. Hoặc điền nội dung, hoặc hạ cờ xuống false.")

    if co_nguon < tong:
        canh_bao.append(f"Độ phủ CỜ ĐỎ CHO BÁC SĨ: {co_nguon}/{tong} hội chứng có nguồn.")
    if co_loi_dan < tong:
        canh_bao.append(f"Độ phủ LỜI DẶN CHO BỆNH NHÂN: {co_loi_dan}/{tong} — đây là "
                        f"phần bác sĩ phải tự viết, máy KHÔNG được sinh thay (Cổng A).")

    return loi, canh_bao, {"tong": tong, "co_nguon": co_nguon, "co_loi_dan": co_loi_dan}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Chốt cấu trúc ngân hàng safety-netting.")
    p.add_argument("--mau", type=Path, default=MAU)
    p.add_argument("--co", type=Path, default=CO)
    p.add_argument("--hom-nay", help="ghi đè ngày hôm nay YYYY-MM-DD (dùng cho test)")
    p.add_argument("--im-khi-on", action="store_true")
    p.add_argument("--json", action="store_true", dest="as_json")
    a = p.parse_args(argv)

    hom_nay = dt.date.today()
    if a.hom_nay:
        try:
            hom_nay = dt.date.fromisoformat(a.hom_nay)
        except ValueError:
            print(f"❌ --hom-nay sai định dạng: {a.hom_nay!r}", file=sys.stderr)
            return 2

    try:
        mau = json.loads(a.mau.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"❌ Không tìm thấy {a.mau}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"❌ {a.mau.name} hỏng JSON: {e}", file=sys.stderr)
        return 2

    try:
        co = json.loads(a.co.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        # Thiếu file cờ KHÔNG được coi là "cờ đang tắt" — fail-closed: giả định
        # cờ đang bật để luật R9 vẫn chạy, thay vì im lặng bỏ qua.
        co = {"enforce_safety_net_templates": True}

    loi, canh_bao, do_phu = kiem(mau, co, hom_nay)

    if a.as_json:
        print(json.dumps({"loi": loi, "canh_bao": canh_bao, "do_phu": do_phu},
                         ensure_ascii=False, indent=2))
        return 2 if loi else (1 if canh_bao else 0)

    if loi:
        print("🔴 SAFETY-NETTING — LỖI CỨNG")
        for x in loi:
            print(f"   • {x}")
        return 2

    if canh_bao:
        if a.im_khi_on:
            print("")
        print(f"🟡 SAFETY-NETTING — {do_phu['co_nguon']}/{do_phu['tong']} hội chứng có nguồn")
        for x in canh_bao:
            print(f"   • {x}")
        print("   (Chốt kiểm CẤU TRÚC, không chấm nội dung y khoa. "
              "Điền nội dung là thẩm quyền bác sĩ — Cổng A.)")
        return 1

    if not a.im_khi_on:
        print(f"🟢 SAFETY-NETTING đủ cấu trúc — {do_phu['co_nguon']}/{do_phu['tong']} "
              f"hội chứng có nguồn, {do_phu['co_loi_dan']}/{do_phu['tong']} có lời dặn.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
