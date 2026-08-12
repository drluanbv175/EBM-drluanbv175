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
import sys
from pathlib import Path

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
    if ban_ghi.get("loai") == "pmid":
        if tuoi_rut is None:
            return False, "chưa kiểm rút bài lần nào"
        if tuoi_rut > HAN_RUT_BAI_NGAY:
            return False, f"kiểm rút bài đã {tuoi_rut} ngày (hạn {HAN_RUT_BAI_NGAY})"
    return True, ""


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


def kiem_rut_bai(pmids: list[str]) -> dict[str, dict]:
    """Tra CHỦ ĐỘNG trạng thái rút bài qua PubMedClient thật của repo y khoa.

    Không có sẵn (thiếu môi trường) → trả {} và caller phải coi là CHƯA kiểm,
    KHÔNG được coi là "không bị rút".
    """
    if not pmids:
        return {}
    mea = REPO / "medical-ebm-automation"
    if not (mea / "app" / "sources" / "pubmed.py").exists():
        return {}
    sys.path.insert(0, str(mea))
    try:
        from app.sources.pubmed import PubMedClient  # noqa: PLC0415
        return PubMedClient().check_retraction_status(pmids) or {}
    except Exception as e:  # noqa: BLE001
        print(f"  ⚠ Không tra được rút bài lần này ({e}) — coi như CHƯA kiểm.")
        return {}


def lenh_quet(files: list[Path], vong: int) -> int:
    vd = _nap_verify_dashboard()
    so = doc_so()
    muc = so["muc"]
    nguon = gom_nguon(files, vd)
    print(f"Gom được {len(nguon)} nguồn khác nhau từ {len(files)} dashboard.")

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
        ghi_so(so)
        print(f"  Vòng {v}: thêm {len(can_lam) - len(that_bai)} · còn thiếu {len(that_bai)}")
        can_lam = that_bai

    # ── kiểm rút bài cho PMID đã xác minh nhưng quá hạn kiểm ────────────────
    can_kiem_rut = []
    for khoa, bg in muc.items():
        if bg.get("loai") != "pmid" or bg.get("da_rut"):
            continue
        if khoa not in nguon:
            continue
        t = _tuoi_ngay(bg.get("kiem_rut_luc"))
        if t is None or t > HAN_RUT_BAI_NGAY:
            can_kiem_rut.append(bg["gia_tri"])
    if can_kiem_rut:
        print(f"\n── Tra rút bài cho {len(can_kiem_rut)} PMID ──")
        kq = kiem_rut_bai(can_kiem_rut)
        bay_gio = dt.datetime.now().isoformat(timespec="seconds")
        chua_tra_duoc = 0
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
                continue

            muc[khoa]["kiem_rut_luc"] = bay_gio
            muc[khoa]["ghi_chu_rut"] = trang_thai
            if trang_thai == "retracted":
                muc[khoa]["da_rut"] = True
                print(f"  🔴 {pmid}: ĐÃ BỊ RÚT")
            elif trang_thai == "expression_of_concern":
                muc[khoa]["quan_ngai"] = True
                print(f"  🟠 {pmid}: có Expression of Concern — cần bác sĩ đọc lại")
            elif trang_thai == "unresolved":
                # PubMed không trả bản ghi. Mâu thuẫn với việc đã xác minh tồn tại ở
                # trên => phải nói ra, không im lặng bỏ qua.
                muc[khoa]["nghi_ma"] = True
                print(f"  🟠 {pmid}: PubMed không trả bản ghi (nghi trích dẫn ma) — rà tay")

        if chua_tra_duoc:
            print(f"  ⚠ {chua_tra_duoc} PMID KHÔNG tra cứu thật được (thiếu NCBI_EMAIL "
                  f"hoặc đang bật mock) — giữ nguyên trạng thái CHƯA kiểm rút bài, "
                  f"KHÔNG coi là sạch.")
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
    print(f"  ĐÃ BỊ RÚT    : {len(rut)}")
    if rut:
        print("\n  🔴 NGUỒN ĐÃ BỊ RÚT — phải xử lý trước khi dùng gói chứa chúng:")
        for khoa, gc in rut:
            dash = ", ".join(muc[khoa].get("cac_dashboard", [])[:3])
            print(f"     • {khoa} [{gc}]  ← {dash}")
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
    a = ap.parse_args()

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
