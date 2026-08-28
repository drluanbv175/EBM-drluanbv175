#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SỔ VIỆC CHƯA ĐÓNG — canh mọi thứ còn treo sau khi bệnh nhân ra về.

VÌ SAO CÓ (22/08/2026, báo cáo `audit/03-diem-nghen-thuc-hanh-ngoai-tru`):

Kho công cụ của hệ này đo rất kỹ CHUỖI CUNG ỨNG CHỨNG CỨ — 117 tool, trong đó
32 tool chỉ để hệ tự kiểm chính nó. Nhưng đếm lại thì **đúng 1 tool** chạm vào
khoảnh khắc trong phòng khám (`tra_diem_kham.py`), và **0 tool** canh cái vòng
SAU cuộc khám. Trong khi đó số đo y văn nói tổn hại nằm chính ở đó:

  • 6,8%–62% kết quả xét nghiệm và 1,0%–35,7% kết quả chẩn đoán hình ảnh của
    bệnh nhân ngoại trú KHÔNG được theo dõi tiếp; hậu quả ghi nhận gồm cả
    chẩn đoán ung thư bị bỏ sót.
    (Callen 2012, J Gen Intern Med · PMID 22183961 · doi:10.1007/s11606-011-1949-5)
  • 14,7% điểm gãy của sai sót chẩn đoán ngoại trú nằm ở khâu "theo dõi và truy
    vết thông tin chẩn đoán".
    (Singh 2013, JAMA Intern Med · PMID 23440149 · doi:10.1001/jamainternmed.2013.2777)

Và lý do phải là MỘT SỔ NGOÀI ĐẦU BÁC SĨ, không phải trí nhớ hay cảm giác:
độ chính xác chẩn đoán rơi từ 55,3% (ca dễ) xuống 5,8% (ca khó) trong khi độ
tự tin gần như không đổi (7,2 → 6,4/10) — niềm tin KHÔNG đo được độ đúng.
(Meyer 2013, JAMA Intern Med · PMID 23979070 · doi:10.1001/jamainternmed.2013.10081)

*Cần bác sĩ kiểm chứng.* Các số trên là dữ liệu Mỹ; thứ chuyển được sang tuyến
ngoại trú Việt Nam là VỊ TRÍ điểm gãy, không phải con số tuyệt đối.

RANH GIỚI CỨNG — công cụ này CHỈ ĐO VÀ NHẮC:
  • KHÔNG suy diễn lâm sàng, KHÔNG gợi ý chẩn đoán, KHÔNG ghi `decision` hay
    `gradeLevel` (BH10 — không công cụ nào được ghi hai trường đó).
  • KHÔNG tự đóng việc. Đóng một việc là một hành vi lâm sàng, thuộc bác sĩ.
  • KHÔNG PII: mọi mô tả đi qua bộ chặn ở `soi_pii()` trước khi được ghi.
  • Ngoại tuyến 100%, chỉ thư viện chuẩn — mất mạng phòng khám không mất sổ.

SỔ NẰM NGOÀI GIT — CÓ CHỦ Ý. `state/` rơi vào luật `/*` của .gitignore nên
không bao giờ lên GitHub: đây là dữ liệu vận hành phòng khám, chỉ có CÔNG CỤ
mới cần version-control.

Dùng:
    python3 tools/so_viec_chua_dong.py                      # báo cáo việc quá hạn
    python3 tools/so_viec_chua_dong.py --im-khi-on          # chỉ nói khi có việc quá hạn (hook)
    python3 tools/so_viec_chua_dong.py --them --loai xet-nghiem \\
            --mo-ta "HbA1c + creatinin, hẹn xem kết quả" --han-sau 14 --ma BN-K12
    python3 tools/so_viec_chua_dong.py --dong V003 --ket-qua "HbA1c 7,1% — đã báo, giữ phác đồ"
    python3 tools/so_viec_chua_dong.py --huy V004 --ly-do "bệnh nhân chuyển tuyến trên"
    python3 tools/so_viec_chua_dong.py --ds                 # liệt kê việc đang mở
    python3 tools/so_viec_chua_dong.py --tuan               # bảng tổng kết tuần

Mã thoát: 0 = không có việc quá hạn · 1 = CÓ việc quá hạn · 2 = lỗi dữ liệu/PII.
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
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]
SO_MAC_DINH = REPO / "state" / "viec-chua-dong.jsonl"

# Ngưỡng nhắc. Cố ý KHÁC nhau theo loại: một kết quả xét nghiệm nằm im 7 ngày là
# bất thường, còn một hẹn tái khám 3 tháng thì không. Ngưỡng là số ngày QUÁ HẠN
# so với `han` do bác sĩ đặt, không phải tuổi tuyệt đối của việc.
NGAY_AN_TOAN = 7          # quá hạn dưới mức này: nhắc nhẹ
NGAY_BAO_DONG = 21        # quá hạn trên mức này: nhắc đậm

LOAI_HOP_LE = {
    "xet-nghiem":  "Xét nghiệm đã chỉ định, chờ kết quả",
    "hinh-anh":    "Chẩn đoán hình ảnh đã chỉ định, chờ kết quả",
    "chuyen-tuyen": "Đã chuyển tuyến / hội chẩn, chờ phản hồi",
    "tai-kham":    "Hẹn tái khám theo lịch",
    "thu-dieu-tri": "Thử điều trị, cần đánh giá đáp ứng",
    "khac":        "Việc treo khác",
}
TRANG_THAI_HOP_LE = {"mo", "dong", "huy"}

# ---------------------------------------------------------------------------
# BỘ CHẶN PII
# ---------------------------------------------------------------------------
# CỐ Ý CHỈ BẮT MẪU ĐỘ CHÍNH XÁC CAO. Không dò "tên người" bằng heuristic:
# tiếng Việt viết hoa đầu từ ở rất nhiều chỗ ("Đau Đầu", "Hồng Cầu"), nên bộ dò
# tên sẽ chặn oan hàng loạt — và theo BH08, biến CHƯA BIẾT thành CÓ VẤN ĐỀ sẽ
# dạy người dùng bỏ qua cảnh báo, làm hỏng đúng cái nó sinh ra để bảo vệ.
# Bù lại, thông điệp lỗi nói thẳng: bộ chặn KHÔNG bắt được tên riêng, nên trách
# nhiệm không ghi tên vẫn là của người nhập.
_PII = [
    (re.compile(r"(?<!\d)(?:\+?84|0)(?:3|5|7|8|9)\d{8}(?!\d)"), "số điện thoại"),
    (re.compile(r"(?<!\d)\d{9}(?:\d{3})?(?!\d)"), "dãy 9 hoặc 12 chữ số (nghi CMND/CCCD)"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "địa chỉ email"),
    (re.compile(r"\b(?:0?[1-9]|[12]\d|3[01])[/-](?:0?[1-9]|1[0-2])[/-](?:19|20)\d{2}\b"),
     "ngày tháng năm đầy đủ (nghi ngày sinh)"),
    (re.compile(r"(?i)\b(?:ngày sinh|họ và tên|họ tên|hovaten|cccd|cmnd|bhyt|"
                r"số thẻ|sđt|số điện thoại|địa chỉ nhà)\b"), "từ khoá định danh"),
]


def soi_pii(text: str) -> list[str]:
    """Trả danh sách loại PII phát hiện được trong `text` (rỗng = sạch)."""
    return [nhan for rx, nhan in _PII if rx.search(text or "")]


# ---------------------------------------------------------------------------
# ĐỌC / GHI SỔ
# ---------------------------------------------------------------------------
def doc_so(duong_dan: Path) -> list[dict]:
    """Đọc sổ JSONL. Dòng hỏng KHÔNG bị bỏ qua im lặng — ném lỗi có số dòng."""
    if not duong_dan.exists():
        return []
    ds: list[dict] = []
    for i, dong in enumerate(duong_dan.read_text(encoding="utf-8").splitlines(), 1):
        dong = dong.strip()
        if not dong:
            continue
        try:
            ds.append(json.loads(dong))
        except json.JSONDecodeError as e:
            raise ValueError(f"sổ hỏng ở dòng {i}: {e}") from e
    return ds


def ghi_so(duong_dan: Path, ds: list[dict]) -> None:
    duong_dan.parent.mkdir(parents=True, exist_ok=True)
    noi_dung = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in ds)
    duong_dan.write_text(noi_dung, encoding="utf-8")


def ma_tiep_theo(ds: list[dict]) -> str:
    so = 0
    for r in ds:
        m = re.fullmatch(r"V(\d+)", str(r.get("id", "")))
        if m:
            so = max(so, int(m.group(1)))
    return f"V{so + 1:03d}"


def _ngay(chuoi: str | None) -> dt.date | None:
    try:
        return dt.date.fromisoformat(chuoi) if chuoi else None
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# HÀNH ĐỘNG
# ---------------------------------------------------------------------------
def them(duong_dan: Path, loai: str, mo_ta: str, han: str | None,
         han_sau: int | None, ma: str | None, nguoi_dong: str | None,
         hom_nay: dt.date) -> int:
    if loai not in LOAI_HOP_LE:
        print(f"❌ --loai không hợp lệ: {loai!r}", file=sys.stderr)
        print(f"   Chọn một trong: {' · '.join(LOAI_HOP_LE)}", file=sys.stderr)
        return 2

    for truong, gia_tri in (("--mo-ta", mo_ta), ("--ma", ma or ""),
                            ("--nguoi-dong", nguoi_dong or "")):
        loi = soi_pii(gia_tri)
        if loi:
            print(f"❌ CHẶN VÌ NGHI CÓ THÔNG TIN ĐỊNH DANH trong {truong}: "
                  f"{', '.join(loi)}", file=sys.stderr)
            print("   Sổ này KHÔNG lưu PII. Dùng mã nội bộ do bác sĩ tự đặt "
                  "(vd 'BN-K12'), mô tả theo việc chứ không theo người.", file=sys.stderr)
            print("   ⚠️  Bộ chặn chỉ bắt mẫu độ chính xác cao (điện thoại · dãy số "
                  "định danh · email · ngày sinh · từ khoá). Nó KHÔNG bắt được TÊN "
                  "RIÊNG — trách nhiệm không ghi tên vẫn là của người nhập.",
                  file=sys.stderr)
            return 2

    if han and han_sau is not None:
        print("❌ Chọn một: --han (ngày cụ thể) HOẶC --han-sau (số ngày).", file=sys.stderr)
        return 2
    if han:
        if _ngay(han) is None:
            print(f"❌ --han phải là ngày ISO YYYY-MM-DD, nhận {han!r}", file=sys.stderr)
            return 2
        han_cuoi = han
    elif han_sau is not None:
        if han_sau < 0:
            print("❌ --han-sau phải ≥ 0.", file=sys.stderr)
            return 2
        han_cuoi = (hom_nay + dt.timedelta(days=han_sau)).isoformat()
    else:
        print("❌ Thiếu hạn. Truyền --han YYYY-MM-DD hoặc --han-sau N.", file=sys.stderr)
        print("   Một việc treo KHÔNG có hạn thì không ai biết lúc nào nó quá hạn — "
              "đúng thứ sổ này sinh ra để chặn.", file=sys.stderr)
        return 2

    ds = doc_so(duong_dan)
    ban_ghi = {
        "id": ma_tiep_theo(ds),
        "ma_noi_bo": ma or "",
        "ngay_mo": hom_nay.isoformat(),
        "loai": loai,
        "mo_ta": mo_ta.strip(),
        "han": han_cuoi,
        "nguoi_dong": nguoi_dong or "bác sĩ",
        "trang_thai": "mo",
        "ngay_dong": None,
        "ket_qua": None,
    }
    ds.append(ban_ghi)
    ghi_so(duong_dan, ds)
    print(f"✅ Đã mở {ban_ghi['id']} · {LOAI_HOP_LE[loai]} · hạn {han_cuoi}")
    return 0


def _doi_trang_thai(duong_dan: Path, ma_id: str, trang_thai: str,
                    ghi_chu: str | None, hom_nay: dt.date) -> int:
    if ghi_chu and (loi := soi_pii(ghi_chu)):
        print(f"❌ CHẶN VÌ NGHI CÓ THÔNG TIN ĐỊNH DANH: {', '.join(loi)}", file=sys.stderr)
        return 2
    ds = doc_so(duong_dan)
    for r in ds:
        if r.get("id") == ma_id:
            if r.get("trang_thai") != "mo":
                print(f"❌ {ma_id} đã ở trạng thái {r.get('trang_thai')!r}, không mở.",
                      file=sys.stderr)
                return 2
            r["trang_thai"] = trang_thai
            r["ngay_dong"] = hom_nay.isoformat()
            r["ket_qua"] = (ghi_chu or "").strip() or None
            ghi_so(duong_dan, ds)
            nhan = "đóng" if trang_thai == "dong" else "huỷ"
            print(f"✅ Đã {nhan} {ma_id}.")
            return 0
    print(f"❌ Không tìm thấy việc có id {ma_id!r}.", file=sys.stderr)
    return 2


def phan_loai(ds: list[dict], hom_nay: dt.date) -> tuple[list, list]:
    """Trả (đang mở còn hạn, quá hạn) — mỗi mục là (bản ghi, số ngày quá hạn)."""
    con_han, qua_han = [], []
    for r in ds:
        if r.get("trang_thai") != "mo":
            continue
        h = _ngay(r.get("han"))
        if h is None:
            # Không suy đoán hạn. Một bản ghi thiếu hạn là dữ liệu hỏng, và theo
            # nguyên tắc fail-closed thì xếp vào nhóm PHẢI XEM, không phải nhóm ổn.
            qua_han.append((r, None))
            continue
        tre = (hom_nay - h).days
        (qua_han if tre > 0 else con_han).append((r, tre))
    qua_han.sort(key=lambda x: (x[1] is not None, -(x[1] or 0)))
    return con_han, qua_han


def _dong_viec(r: dict, tre: int | None) -> str:
    ma = f" [{r['ma_noi_bo']}]" if r.get("ma_noi_bo") else ""
    if tre is None:
        return f"{r['id']}{ma} · {r['mo_ta']} — ⚠️ BẢN GHI THIẾU HẠN, phải sửa tay"
    dau = "🔴" if tre > NGAY_BAO_DONG else ("🟠" if tre > NGAY_AN_TOAN else "🟡")
    return (f"{dau} {r['id']}{ma} · {LOAI_HOP_LE.get(r['loai'], r['loai'])} · "
            f"{r['mo_ta']} — quá hạn {tre} ngày (hạn {r['han']})")


def bao_cao(duong_dan: Path, im_khi_on: bool, hom_nay: dt.date) -> int:
    ds = doc_so(duong_dan)
    con_han, qua_han = phan_loai(ds, hom_nay)

    if not qua_han:
        if not im_khi_on:
            # NÓI ĐÚNG THỨ ĐÃ ĐO. "Không có việc quá hạn" KHÔNG có nghĩa là
            # "không bỏ sót gì" — nó chỉ nói về những việc ĐÃ ĐƯỢC GHI VÀO SỔ.
            # Cùng lớp lỗi BH32: một chỉ số gộp không được trình bày như kết
            # luận về toàn bộ.
            if not ds:
                print("⚪ SỔ VIỆC CHƯA ĐÓNG còn trống — chưa có việc nào được ghi.")
                print("   Sổ trống KHÔNG có nghĩa là không có việc treo; nó chỉ có "
                      "nghĩa là chưa ai ghi. Mở việc đầu tiên bằng --them.")
            else:
                print(f"🟢 KHÔNG có việc quá hạn — {len(con_han)} việc đang mở còn trong hạn.")
                print("   (Chỉ nói về những việc ĐÃ ghi vào sổ, không nói về việc chưa ghi.)")
        return 0

    if im_khi_on:
        print("")
    print(f"🟠 VIỆC CHƯA ĐÓNG ĐÃ QUÁ HẠN — {len(qua_han)} việc")
    for r, tre in qua_han:
        print(f"   • {_dong_viec(r, tre)}")
    print(f"   ({len(con_han)} việc khác đang mở còn trong hạn.)")
    print("   Sổ chỉ ĐO và NHẮC — đóng một việc là hành vi lâm sàng, thuộc bác sĩ.")
    return 1


def liet_ke(duong_dan: Path, tat_ca: bool, hom_nay: dt.date) -> int:
    ds = doc_so(duong_dan)
    muc = ds if tat_ca else [r for r in ds if r.get("trang_thai") == "mo"]
    if not muc:
        print("⚪ Không có mục nào để hiện.")
        return 0
    for r in muc:
        h = _ngay(r.get("han"))
        tre = (hom_nay - h).days if h else None
        if r.get("trang_thai") != "mo":
            print(f"   ✓ {r['id']} · {r['mo_ta']} — {r['trang_thai']} "
                  f"({r.get('ngay_dong') or 'không rõ ngày'})")
        elif tre is not None and tre > 0:
            print(f"   • {_dong_viec(r, tre)}")
        else:
            con = -tre if tre is not None else None
            print(f"   ○ {r['id']} · {r['mo_ta']} — còn "
                  f"{con if con is not None else '?'} ngày (hạn {r.get('han')})")
    return 0


def bang_tuan(duong_dan: Path, hom_nay: dt.date) -> int:
    ds = doc_so(duong_dan)
    dau_tuan = hom_nay - dt.timedelta(days=7)
    mo_moi = [r for r in ds if (d := _ngay(r.get("ngay_mo"))) and d > dau_tuan]
    dong_moi = [r for r in ds if (d := _ngay(r.get("ngay_dong"))) and d > dau_tuan]
    _, qua_han = phan_loai(ds, hom_nay)
    print(f"BẢNG TUẦN — {dau_tuan:%d/%m} → {hom_nay:%d/%m/%Y}")
    print(f"   mở mới: {len(mo_moi)}   ·   đã đóng/huỷ: {len(dong_moi)}   ·   "
          f"đang quá hạn: {len(qua_han)}")
    theo_loai: dict[str, int] = {}
    for r in ds:
        if r.get("trang_thai") == "mo":
            theo_loai[r.get("loai", "khac")] = theo_loai.get(r.get("loai", "khac"), 0) + 1
    if theo_loai:
        print("   đang mở theo loại: " +
              " · ".join(f"{k} {v}" for k, v in sorted(theo_loai.items())))
    print(f"   Thước đo của báo cáo audit/03: việc quá hạn > {NGAY_AN_TOAN} ngày phải = 0. "
          f"Hiện tại: {sum(1 for _, t in qua_han if t is None or t > NGAY_AN_TOAN)}.")
    return 1 if qua_han else 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Sổ việc chưa đóng — canh mọi thứ còn treo sau khi bệnh nhân ra về.")
    p.add_argument("--so", type=Path, default=SO_MAC_DINH,
                   help=f"đường dẫn sổ JSONL (mặc định {SO_MAC_DINH})")
    p.add_argument("--hom-nay", help="ghi đè ngày hôm nay, YYYY-MM-DD (dùng cho test)")
    p.add_argument("--im-khi-on", action="store_true",
                   help="chỉ in khi CÓ việc quá hạn (dùng cho hook SessionStart)")

    p.add_argument("--them", action="store_true", help="mở một việc treo mới")
    p.add_argument("--loai", choices=sorted(LOAI_HOP_LE), help="loại việc (đi với --them)")
    p.add_argument("--mo-ta", default="", help="mô tả việc, KHÔNG chứa thông tin định danh")
    p.add_argument("--ma", help="mã nội bộ do bác sĩ tự đặt, vd BN-K12 (không phải PII)")
    p.add_argument("--han", help="hạn cụ thể YYYY-MM-DD")
    p.add_argument("--han-sau", type=int, help="hạn sau N ngày kể từ hôm nay")
    p.add_argument("--nguoi-dong", help="ai chịu trách nhiệm đóng việc này")

    p.add_argument("--dong", metavar="ID", help="đóng một việc")
    p.add_argument("--ket-qua", default="", help="tóm tắt kết quả khi đóng")
    p.add_argument("--huy", metavar="ID", help="huỷ một việc")
    p.add_argument("--ly-do", default="", help="lý do huỷ")

    p.add_argument("--ds", action="store_true", help="liệt kê việc đang mở")
    p.add_argument("--tat-ca", action="store_true", help="liệt kê cả việc đã đóng")
    p.add_argument("--tuan", action="store_true", help="bảng tổng kết tuần")

    a = p.parse_args(argv)
    hom_nay = _ngay(a.hom_nay) or dt.date.today()
    if a.hom_nay and _ngay(a.hom_nay) is None:
        print(f"❌ --hom-nay phải là YYYY-MM-DD, nhận {a.hom_nay!r}", file=sys.stderr)
        return 2

    try:
        if a.them:
            return them(a.so, a.loai or "", a.mo_ta, a.han, a.han_sau,
                        a.ma, a.nguoi_dong, hom_nay)
        if a.dong:
            return _doi_trang_thai(a.so, a.dong, "dong", a.ket_qua, hom_nay)
        if a.huy:
            if not a.ly_do.strip():
                print("❌ Huỷ một việc treo phải có --ly-do. Huỷ không dấu vết là "
                      "cách một việc biến mất mà không ai biết.", file=sys.stderr)
                return 2
            return _doi_trang_thai(a.so, a.huy, "huy", a.ly_do, hom_nay)
        if a.ds:
            return liet_ke(a.so, a.tat_ca, hom_nay)
        if a.tuan:
            return bang_tuan(a.so, hom_nay)
        return bao_cao(a.so, a.im_khi_on, hom_nay)
    except ValueError as e:
        print(f"❌ {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
