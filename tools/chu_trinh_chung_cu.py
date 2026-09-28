#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CHU TRÌNH CHỨNG CỨ — một lệnh trả lời: chứng cứ của tôi có MỚI và ĐÁNG TIN không?

VÌ SAO CÓ (12/08/2026)
======================
Hệ đã có đủ mảnh rời — chốt độ tươi, cổng liêm chính, sổ xác minh, tra rút bài,
giám sát tuần/tháng — nhưng KHÔNG có chỗ nào ghép chúng lại. Hệ quả đo được:

  • hai job launchd (tuần/tháng) `runs = 0` — **chưa từng tự chạy lần nào**;
  • máy Windows không có lịch nền nào tương đương;
  • bác sĩ phải tự nhớ gọi từng lệnh, đúng thứ tự, với đúng trình thông dịch;
  • và tệ nhất: máy có thể đang chạy **dữ liệu giả** mà không bước nào nói ra.

Lệnh này chạy các chốt theo đúng thứ tự phụ thuộc và **dừng ngay khi nền tảng
không đáng tin** — thay vì chạy tiếp rồi sinh ra một báo cáo trông sạch sẽ.

THỨ TỰ CÓ CHỦ Ý (không đảo)
    1. NGUỒN THẬT?   — máy có lấy được dữ liệu thật không (chặn cứng nếu không)
    2. ĐỘ TƯƠI       — chứng cứ có cũ quá không
    3. XÁC MINH      — từng PMID/DOI/URL có thật không, tích luỹ qua nhiều vòng
    4. RÚT BÀI       — có trích dẫn nào đã bị rút không
    5. CỔNG LIÊM CHÍNH — gói có còn đạt chuẩn phát hành không

Bước 1 chặn cứng vì mọi bước sau đều VÔ NGHĨA nếu nguồn là giả: xác minh dữ liệu
giả sẽ "thành công" và cho ra một con số độ phủ đẹp nhưng rỗng.

GIỚI HẠN CÓ CHỦ Ý
  • KHÔNG tự quét chứng cứ mới và KHÔNG tự nạp sổ cái: sinh nội dung y khoa phải
    do bác sĩ chủ động và duyệt (Cổng B). Lệnh này chỉ ĐO và BÁO.
  • KHÔNG tự áp dụng gì cho người bệnh (Cổng A).
  • Không thay `verify_dashboard.py --online` ở lượt phát hành thật.

Dùng:
    python tools/chu_trinh_chung_cu.py             # đo toàn bộ kho
    python tools/chu_trinh_chung_cu.py --nhanh     # bỏ bước xác minh mạng (chỉ đọc sổ)
    python tools/chu_trinh_chung_cu.py --vong 3    # mạng chập chờn thì tăng vòng

Mã thoát: 0 = mọi chốt đạt · 1 = có việc cần bác sĩ làm · 2 = nền tảng không đáng tin.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

# Windows: stdout mặc định là cp1252 → mọi print() tiếng Việt hoặc ký hiệu (✓ ⚠ →)
# ném UnicodeEncodeError và GIẾT tiến trình, thường SAU KHI công việc đã xong. Đo thật
# ngày 12/08/2026 trên dây chuyền cập nhật chứng cứ: bản Word 82 KB đã ghi ra đĩa nhưng
# tool thoát mã 1 ở đúng dòng print cuối ⇒ caller đọc mã thoát, tưởng hỏng, bỏ luôn 2
# bước sau. Cùng lớp lỗi đã vá cho tools/vietnamize/.
import sys as _sys_utf8
for _s in (_sys_utf8.stdout, _sys_utf8.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass


REPO = Path(__file__).resolve().parents[1]
PY = sys.executable


def _dem_rut_bai(out: str) -> tuple[int | None, int | None, int | None]:
    """(số «ĐÃ BỊ RÚT» trong báo cáo sổ, số ca đính-chính-bị-rút CÒN chờ ký, tổng ca đính-chính-bị-rút); None = không đọc được."""
    m = re.search(r"ĐÃ BỊ RÚT\s*:\s*(\d+)", out)

    def dem(co: str) -> int | None:
        p = subprocess.run([str(PY), "tools/mau_ky_rut_bai.py", co], cwd=str(REPO), capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        dong = [x.strip() for x in (p.stdout or "").splitlines() if x.strip()]
        return int(dong[-1]) if p.returncode == 0 and dong and dong[-1].isdigit() else None
    return (int(m.group(1)) if m else None), dem("--dem"), dem("--dem-tat-ca")


def _co_dashboard_that() -> bool:
    """Máy có EBM-Dashboards thật (nơi `so_xac_minh_nguon` tìm sổ + bộ xác minh của cổng) hay không."""
    return (REPO / "EBM-Dashboards" / "tools" / "verify_dashboard.py").exists()


def chay(cmd: list[str], tieu_de: str) -> tuple[int, str]:
    print("\n" + "─" * 68)
    print(f"  {tieu_de}")
    print("─" * 68)
    proc = subprocess.run([str(c) for c in cmd], cwd=str(REPO),
                          capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    out = (proc.stdout or "") + (proc.stderr or "")
    print(out.rstrip() or "  (không có đầu ra)")
    return proc.returncode, out


def main(argv: list[str] | None = None) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser(description="Chu trình đo độ mới + độ tin cậy của kho chứng cứ")
    ap.add_argument("--vong", type=int, default=2, help="số vòng xác minh (mạng kém thì tăng)")
    ap.add_argument("--nhanh", action="store_true", help="không gọi mạng, chỉ đọc sổ đã có")
    ap.add_argument("--ghi-log", metavar="TỆP",
                    help="nối một dòng «===== <thời điểm> : KẾT THÚC (mã N)» vào TỆP khi xong — dấu vết máy-đọc-được "
                         "cho tools/kiem_lich_nen.py (tác vụ lịch kiem-rut-bai-kho-thang)")
    a = ap.parse_args(argv)
    rc = _chu_trinh(a)
    if a.ghi_log:
        ghi_dau_vet(Path(a.ghi_log), rc)
    return rc


def ghi_dau_vet(tep: Path, rc: int, luc: dt.datetime | None = None) -> None:
    """Nối dòng KẾT THÚC đúng khuôn mà kiem_lich_nen._ket_thuc() đọc. Lỗi ghi chỉ cảnh báo, không đổi mã thoát."""
    luc = luc or dt.datetime.now()
    try:
        tep.parent.mkdir(parents=True, exist_ok=True)
        with tep.open("a", encoding="utf-8", newline="\n") as f:
            f.write(f"===== {luc:%Y-%m-%d %H:%M:%S} : KẾT THÚC chu_trinh_chung_cu (mã {rc})\n")
    except OSError as e:
        print(f"  ⚠ không ghi được dấu vết vào {tep}: {e}", file=sys.stderr)


def _chu_trinh(a: argparse.Namespace) -> int:
    print("=" * 68)
    print("  CHU TRÌNH CHỨNG CỨ — độ mới và độ tin cậy")
    print("=" * 68)

    viec_can_lam: list[str] = []
    ghi_chu: list[str] = []   # điều ĐÃ BIẾT, không phải việc — in cạnh tổng kết để câu 🟢 không nói quá

    # ── 1. NỀN TẢNG: nguồn có THẬT không ────────────────────────────────────
    rc, _ = chay([PY, "tools/kiem_nguon_that.py"], "① Nguồn có thật không?")
    if rc == 2:
        print("\n" + "=" * 68)
        print("  ⛔ DỪNG — nền tảng không đáng tin.")
        print("=" * 68)
        print("  Mọi bước sau đều vô nghĩa khi nguồn là dữ liệu giả: xác minh dữ liệu")
        print("  giả vẫn 'thành công' và cho ra độ phủ đẹp nhưng rỗng ruột.")
        print("  Sửa theo hướng dẫn ở trên rồi chạy lại lệnh này.")
        print("\n  Cần bác sĩ kiểm chứng.")
        return 2
    if rc == 1:
        viec_can_lam.append("Mạng tới nguồn chập chờn — kết quả xác minh có thể chưa đủ.")

    # ── 2. ĐỘ TƯƠI ──────────────────────────────────────────────────────────
    rc, out = chay([PY, "tools/kiem_do_tuoi_chung_cu.py"], "② Chứng cứ có còn mới không?")
    if rc != 0:
        viec_can_lam.append("Có mục giám sát quá hạn — xem phần ② ở trên.")

    # ── 3 + 4. XÁC MINH TỪNG NGUỒN và RÚT BÀI ───────────────────────────────
    if a.nhanh:
        rc, out = chay([PY, "tools/so_xac_minh_nguon.py", "--bao-cao"],
                       "③④ Độ phủ xác minh (đọc sổ, không gọi mạng)")
    else:
        rc, out = chay([PY, "tools/so_xac_minh_nguon.py", "--vong", str(a.vong)],
                       f"③④ Xác minh nguồn + tra rút bài ({a.vong} vòng)")
        # ③a/③b PHỦ BẢN GHI MỒ CÔI (vá 27/09/2026): `--vong` chỉ tái kiểm định danh gom TỪ DASHBOARD; bản ghi do cầu NC⇄LS/hub
        # tạo trần (không ngày xác minh) không bao giờ được chạm ⇒ «Chưa/hết hạn» của TOÀN sổ đứng yên dù chu trình chạy
        # đều (đo 27/09: `--vong 3` thêm 220 mục mới, 125 mục cũ vẫn nguyên; `--phu-mo-coi` nhắm đúng 125 mục đó). Công cụ
        # có sẵn từ 16/08 nhưng không quy trình nào gọi (BH41). Bản sao trần/Cloud (mã 3) đã có dòng ⚪ ở trên — bỏ qua.
        # Mã thoát của lượt này KHÔNG thay phán quyết ③④ — phán quyết vẫn đọc từ lượt quét dashboard.
        # Thứ tự để sổ HỘI TỤ trong một lượt: quét hub (`--quet-ledger`: phán quyết rút bài cho định danh chỉ-có-trong-hub,
        # có thể TẠO bản ghi chưa có ngày xác minh) rồi mới phủ mồ côi (xác minh tồn tại cho mọi PMID/DOI còn thiếu, kể cả
        # bản ghi hub vừa tạo). `--quet-ledger` cũng chưa quy trình nào gọi ⇒ phán quyết rút bài của thẻ hub hết hạn lặng lẽ.
        if _co_dashboard_that() and rc != 3:
            chay([PY, "tools/so_xac_minh_nguon.py", "--quet-ledger", "--vong", str(a.vong)],
                 f"③a Rút bài cho định danh chỉ-có-trong-hub ({a.vong} vòng)")
            chay([PY, "tools/so_xac_minh_nguon.py", "--phu-mo-coi", "--vong", str(a.vong)],
                 f"③b Phủ bản ghi mồ côi của sổ ({a.vong} vòng)")
    khong_do_duoc = (rc == 3 or "KHONG_DO_DUOC" in out
                     # chuỗi của bản so_xac_minh_nguon CŨ (trả 2/1 cho hai ca này) — vẫn phải ra ⚪, không ra 🔴
                     or "Không thấy dashboard nào khớp" in out or "Sổ trống" in out)
    if rc == 2 and "SO_HONG" in out:
        # SỔ HỎNG (26/09/2026, phát hiện #3): so_xac_minh_nguon từ chối đọc/ghi sổ hỏng và trả 2 kèm dòng
        # «[MA] SO_HONG». Vẫn là việc ĐỎ (dương tính rút bài đã biết có thể đã mất) nhưng KHÔNG được gọi là
        # «có nguồn rút bỏ hẳn» — chưa ai thấy bài nào bị rút ở lượt này.
        viec_can_lam.append("🔴 SỔ XÁC MINH NGUỒN HỎNG — dương tính rút bài đã biết có thể bị mất; mọi phát "
                            "hành bị chặn tới khi khôi phục sổ (xem hướng dẫn ở phần ③④). KHÔNG xoá tệp hỏng.")
    elif khong_do_duoc:
        # VÁ 26/09/2026 (phát hiện #28): bản sao trần/Cloud không có EBM-Dashboards ⇒ so_xac_minh_nguon trả 3.
        # BẮT BUỘC thêm một việc ⚪ (không «bỏ qua»): nếu viec_can_lam rỗng, tổng kết sẽ in 🟢 «không thấy bài bị
        # rút» trong khi chưa đọc nguồn nào — xanh giả nguy hiểm hơn đỏ giả. Đọc MÃ THOÁT/đầu ra, không đoán theo
        # duong_goc(): so_xac_minh_nguon chỉ tìm REPO/EBM-Dashboards, hai bên sẽ lệch ở bố cục anh em.
        viec_can_lam.append("⚪ Chưa đo được xác minh nguồn/rút bài — thiếu EBM-Dashboards/ (hoặc sổ xác minh) "
                            "trên máy này (xem ③④). KHÔNG phải đã thấy bài bị rút, cũng KHÔNG phải đã kiểm là sạch.")
    elif rc == 2:
        # rc=2 từ 15/08 CHỈ còn nghĩa «rút BỎ HẲN đang được dashboard trích» —
        # rút-và-thay đã phân xử trong gói không kéo còi đỏ nữa (nó ở rc=1, phần
        # 🟠 của báo cáo); thẩm quyền chặn từng gói thuộc verify_dashboard.
        # VÁ 27/09/2026: ca «thông báo rút là BẢN ĐÍNH CHÍNH bị rút» (BH109) cũng làm sổ trả 2, kể cả khi bác sĩ ĐÃ KÝ xem
        # xét (`EBM-Dashboards/rut-bai-da-xem-xet.json`, gắn vân tay thông báo) ⇒ chu trình kéo 🔴 «RÚT BỎ HẲN» giả trong khi
        # cổng đã cho qua và `tu_de_xuat_viec` đã trừ đúng ca này (P2-03, họ BH115). Chỉ hạ khi ĐỌC ĐƯỢC cả số «ĐÃ BỊ RÚT»
        # lẫn hai bộ đếm của `mau_ky_rut_bai.py`; đọc không được ⇒ giữ 🔴 (fail-closed).
        n_rut, n_cho_ky, n_dinh_chinh = _dem_rut_bai(out)
        if None not in (n_rut, n_cho_ky, n_dinh_chinh) and n_rut <= n_dinh_chinh:
            if n_cho_ky:
                viec_can_lam.append(f"👤 {n_cho_ky} nguồn bị cờ rút bài mà thông báo là BẢN ĐÍNH CHÍNH bị rút — đọc "
                                    "thông báo rồi ký (máy đã dựng mẫu, KHÔNG ký thay): `python3 tools/mau_ky_rut_bai.py`")
            if n_dinh_chinh - n_cho_ky > 0:
                ghi_chu.append(f"ℹ {n_dinh_chinh - n_cho_ky} nguồn mang cờ rút bài là BẢN ĐÍNH CHÍNH bị rút — bác sĩ đã ký "
                               "xem xét (`EBM-Dashboards/rut-bai-da-xem-xet.json`); cổng cho qua. Không phải bài bị rút bỏ.")
        else:
            viec_can_lam.append("🔴 CÓ NGUỒN RÚT BỎ HẲN đang được trích — xử lý trước khi dùng gói chứa chúng.")
    elif rc == 1:
        # VÁ 13/08/2026 — đọc MÃ lý do thay vì đưa một lời khuyên chung.
        # Bản cũ luôn nói "chạy lại thêm vòng". Đo thật: 562/1146 mục hết hiệu lực và
        # CẢ 562 là PMID chưa kiểm được rút bài vì NCBI chặn máy — chạy lại bao nhiêu
        # vòng cũng không đổi. Lời khuyên chắc chắn vô ích tiêu thời gian thật của bác
        # sĩ và làm mất niềm tin vào những cảnh báo ĐÚNG khác của cùng công cụ.
        # BỔ SUNG 14/08/2026 — kiểm rút bài nay có chuỗi 3 tầng, nên khi chưa tải nền
        # ngoại tuyến thì cách sửa ĐÚNG là tải nó (miễn phí, không khoá), KHÔNG phải
        # ngồi chờ NCBI_API_KEY. Đặt TRƯỚC nhánh CAN_NCBI_API_KEY vì đây mới là việc
        # có tác dụng ngay.
        if "CAN_TAI_RETRACTION_WATCH" in out:
            viec_can_lam.append(
                "PMID CHƯA kiểm được RÚT BÀI vì chưa có nền ngoại tuyến — chạy "
                "`python medical-ebm-automation/tools/tai_retraction_watch.py` (một lần, "
                "không cần khoá API) rồi chạy lại.")
        if "CAN_NCBI_API_KEY" in out:
            viec_can_lam.append(
                "PMID CHƯA kiểm được RÚT BÀI dù đã qua cả 3 tầng (Retraction Watch ngoại "
                "tuyến → NCBI → Europe PMC). Thêm `NCBI_API_KEY` vào "
                "~/.ebm-secrets/medical-ebm-automation.env sẽ mở lại tầng NCBI.")
        if "CAN_CHAY_THEM_VONG" in out:
            viec_can_lam.append("Có nguồn quá hạn xác minh tồn tại — chạy lại thêm vòng SẼ sửa được.")
        if "CAN_XEM_TAY" in out:
            viec_can_lam.append("Có nguồn hết hiệu lực vì lý do khác — xem phần ③④ ở trên.")
        if not any(x in out for x in ("CAN_NCBI_API_KEY", "CAN_TAI_RETRACTION_WATCH",
                                      "CAN_CHAY_THEM_VONG", "CAN_XEM_TAY")):
            viec_can_lam.append("Còn nguồn chưa xác minh hoặc hết hạn — xem phần ③④ ở trên.")
    elif rc != 0:
        # Mã lạ (tiến trình bị giết, lỗi chưa đặt tên…) — KHÔNG được rơi im lặng thành 🟢 (vá #28, 26/09/2026).
        viec_can_lam.append(f"⚪ Bước ③④ thoát mã lạ ({rc}) — chưa đo được xác minh nguồn/rút bài; xem phần ③④.")

    # ── 5. NHẤT QUÁN GIỮA CÁC BẢN CÙNG CHỦ ĐỀ ───────────────────────────────
    # Đặt SAU phần xác minh vì nó đọc nội dung dashboard, không gọi mạng; và đặt
    # TRƯỚC cổng dây chuyền vì mâu thuẫn nội dung nghiêm trọng hơn lỗi cấu trúc.
    rc, out = chay([PY, "tools/dang_ky_chu_de.py", "--mau-thuan"],
                   "⑤ Có hai bản nào nói ngược nhau không?")
    # VÁ 26/09/2026 (phát hiện #17): dang_ky_chu_de nay trả 2 khi «không kiểm được» (0 dashboard / thiếu công cụ)
    # thay vì in 🟢 + 0. Nhánh này PHẢI sửa CÙNG lúc với công cụ: nếu không, rc=2 rơi qua mọi nhánh và tổng kết
    # vẫn im lặng — xanh giả. Chuỗi «Không kiểm được trên máy này» giữ cho bản công cụ cũ (trả 1).
    if rc == 2 or "Không kiểm được trên máy này" in out:
        viec_can_lam.append("⚪ Chưa quét được mâu thuẫn hai bản — không có dashboard nào để so trên máy này "
                            "(xem phần ⑤). KHÔNG phải đã tìm thấy mâu thuẫn, cũng KHÔNG phải «không có mâu thuẫn».")
    elif rc not in (0, 1):
        viec_can_lam.append(f"⚪ Bước ⑤ thoát mã lạ ({rc}) — chưa quét được mâu thuẫn hai bản; xem phần ⑤.")
    elif rc == 1:
        # VÁ 04/09/2026 (Workflow đối kháng đa-agent, phát hiện MEDIUM) — rc=1 của
        # dang_ky_chu_de.py mang HAI NGHĨA HOÀN TOÀN KHÁC NHAU: (a) tìm thấy mâu
        # thuẫn thật (dòng cuối main() của nó), hoặc (b) KHÔNG QUÉT ĐƯỢC vì thiếu
        # EBM-Dashboards/ (FileNotFoundError bắt ở đầu main(), in "⚪ Không kiểm
        # được trên máy này" rồi CŨNG trả về 1). Bản cũ gộp cả hai thành một lời
        # cảnh báo "🔴 CÓ mâu thuẫn" — xác nhận bằng thực nghiệm trên chính bản
        # sao trần này (EBM-Dashboards/ không tồn tại): rc=1 vì KHÔNG QUÉT ĐƯỢC,
        # nhưng chu trình vẫn báo "🔴 Có mục hai bản CÙNG CHỦ ĐỀ nói ngược nhau"
        # — một báo động giả về nội dung lâm sàng trong khi sự thật chỉ là thiếu
        # nguyên liệu. Đọc `out` để phân biệt, đúng khuôn mẫu bước ③④ đã dùng — phép phân
        # biệt đó nay nằm ở nhánh ⚪ phía trên (26/09/2026), nhánh này chỉ còn mâu thuẫn THẬT.
        viec_can_lam.append("🔴 Có mục hai bản CÙNG CHỦ ĐỀ nói ngược nhau — bác sĩ cần "
                            "quyết bản nào đúng (xem phần ⑤).")

    # ── 6. CỔNG LIÊM CHÍNH trên toàn kho (offline, nhanh) ────────────────────
    rc, out = chay([PY, "tools/verify_clinical_evidence_update_pipeline.py"],
                   "⑥ Dây chuyền cập nhật chứng cứ còn nguyên vẹn?")
    if rc == 2:
        # MEASUREMENT_INCOMPLETE (26/09/2026): bản sao git trần thiếu template/hub chỉ có trên OneDrive —
        # KHÔNG phải dây chuyền hỏng, nhưng cũng chưa được coi là đạt.
        viec_can_lam.append("⚪ Dây chuyền cập nhật chứng cứ CHƯA đo đủ trên máy này (thiếu tệp chỉ có "
                            "trên OneDrive) — chạy lại trên máy có cây OneDrive; xem phần ⑥.")
    elif rc != 0:
        viec_can_lam.append("Dây chuyền cập nhật chứng cứ có lỗi — xem phần ⑥.")

    # ── Tổng kết ────────────────────────────────────────────────────────────
    print("\n" + "=" * 68)
    print("  TỔNG KẾT")
    print("=" * 68)
    if not viec_can_lam:
        print("  🟢 Mọi chốt đạt: nguồn thật · còn hạn · đã xác minh · "
              + ("không có bài bị rút bỏ hẳn." if ghi_chu else "không thấy bài bị rút."))
        for dong in ghi_chu:
            print(f"     {dong}")
        print("\n  Lưu ý phạm vi: đây là kết luận về TÍNH TOÀN VẸN KỸ THUẬT của kho —")
        print("  nguồn có thật, chưa bị rút, gói đúng cấu trúc. Nó KHÔNG nói rằng nội")
        print("  dung lâm sàng đã đúng hay đã cập nhật hết mọi guideline mới; việc đó")
        print("  cần bác sĩ đọc và cần một lượt quét chứng cứ chủ động.")
        print("\n  Cần bác sĩ kiểm chứng.")
        return 0

    print(f"  🟡 Còn {len(viec_can_lam)} việc cần bác sĩ:")
    for i, v in enumerate(viec_can_lam, 1):
        print(f"     {i}. {v}")
    print("\n  Chu trình này chỉ ĐO và BÁO — không tự quét chứng cứ mới, không tự nạp")
    print("  sổ cái, không tự áp dụng cho người bệnh (Cổng A/B).")
    print("\n  Cần bác sĩ kiểm chứng.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
