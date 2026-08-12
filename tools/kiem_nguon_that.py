#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CHỐT KIỂM: máy này có đang lấy chứng cứ THẬT không, hay đang chạy dữ liệu giả?

VÌ SAO CÓ (12/08/2026)
======================
Rà máy Windows tìm ra một lỗ hổng im lặng ảnh hưởng thẳng tới độ tin cậy:

  • `medical-ebm-automation/.env` trên Windows KHÔNG phải file cấu hình. Nó là
    **symlink Unix bị OneDrive đồng bộ thành file text 57 byte** chứa đúng một
    dòng: đường dẫn macOS `/Users/nguyenluan/.ebm-secrets/...`. Windows không
    hiểu symlink Unix nên đọc ra rác.
  • Hệ quả dây chuyền: không đọc được biến nào ⇒ `USE_MOCK_SOURCES` rơi về
    **mặc định True** ⇒ mọi lời gọi PubMed/nguồn y văn trả **DỮ LIỆU GIẢ**.
  • Cảnh báo duy nhất là một dòng `logger.info` — không ai thấy khi chạy routine.

Nghĩa là bác sĩ có thể chạy giám sát an toàn thuốc trên máy này, nhận một báo
cáo trông bình thường, mà toàn bộ nội dung là bịa. Đây đúng lớp lỗi "gãy im
lặng vì viết cho một nền tảng" đã gặp nhiều lần, nhưng lần này hậu quả nằm ở
NỘI DUNG Y KHOA chứ không chỉ ở công cụ.

Chốt này trả lời đúng một câu: **số liệu sắp lấy có thật không?**
Nó KHÔNG tự sửa cấu hình và KHÔNG tự điền secrets — chỉ nói rõ trạng thái.

Dùng:
    python tools/kiem_nguon_that.py            # in trạng thái đầy đủ
    python tools/kiem_nguon_that.py --im-khi-on  # chỉ nói khi có vấn đề (hook)

Mã thoát: 0 = 🟢 nguồn thật · 1 = 🟡 thiếu một phần · 2 = 🔴 đang chạy dữ liệu giả.
"""
from __future__ import annotations

import argparse
import socket
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MEA = REPO / "medical-ebm-automation"

# Nguồn y văn mà dây chuyền thật sự gọi tới.
HOST_NGUON = [
    ("eutils.ncbi.nlm.nih.gov", "PubMed E-utilities (tra cứu + kiểm RÚT BÀI)"),
    ("api.crossref.org", "Crossref (phân giải DOI)"),
    ("www.ebi.ac.uk", "Europe PMC (nguồn dự phòng khi NCBI chặn)"),
    ("api.fda.gov", "openFDA (tín hiệu an toàn thuốc)"),
]


def kiem_env() -> tuple[str, list[str]]:
    """Đọc cấu hình THẬT qua app.config, đúng đường mà pipeline dùng.

    Chấm theo KẾT QUẢ (có chạy được nguồn thật không), KHÔNG theo hình thức file.
    Một `.env` hỏng mà kho secrets ngoài OneDrive vẫn nạp được thì hệ chạy đúng —
    báo đỏ lúc đó là dương tính giả, và cảnh báo sai sẽ làm người ta quen bỏ qua
    cảnh báo thật.
    """
    do, canh_bao = [], []

    sys.path.insert(0, str(MEA))
    try:
        from app.config import settings  # noqa: PLC0415
    except Exception as e:  # noqa: BLE001
        return "do", [f"không nạp được app.config ({e}) — không kết luận được gì về nguồn"]

    if getattr(settings, "use_mock_sources", True):
        do.append(
            "USE_MOCK_SOURCES đang BẬT ⇒ mọi lời gọi nguồn y văn trả DỮ LIỆU GIẢ.\n"
            "     Báo cáo sinh ra lúc này KHÔNG dùng cho quyết định lâm sàng được.")
    if not getattr(settings, "ncbi_email", ""):
        do.append(
            "Thiếu NCBI_EMAIL ⇒ KHÔNG tra cứu RÚT BÀI thật được.\n"
            "     Không biết một trích dẫn đã bị rút hay chưa là rủi ro an toàn trực tiếp.")

    # Chẩn đoán phụ: `.env` bị OneDrive làm phẳng. Chỉ nói khi nó THỰC SỰ gây hại
    # (tức cấu hình chưa nạp được từ nơi khác) — còn không thì nêu như ghi chú.
    env = MEA / ".env"
    if env.exists():
        try:
            noi_dung = env.read_text(encoding="utf-8", errors="replace").strip()
        except OSError:
            noi_dung = ""
        if noi_dung and "\n" not in noi_dung and "=" not in noi_dung:
            thong_diep = (
                f".env trong repo là symlink Unix bị OneDrive làm phẳng thành file text\n"
                f"     ({noi_dung}) — Windows không đọc được biến nào từ đó.")
            if do:
                # Chỉ nêu khi nó THỰC SỰ là nguyên nhân của lỗi đang có.
                do.append(thong_diep + "\n     Đây là nguyên nhân của lỗi bên trên.")
            # Nếu cấu hình đã nạp được từ ~/.ebm-secrets/ thì file phẳng này VÔ HẠI
            # và KHÔNG có việc gì để làm. CỐ Ý không báo: trạng thái này tồn tại vĩnh
            # viễn trên Windows, báo mỗi phiên chỉ tạo nhiễu, mà cảnh báo lặp vô ích
            # là cách nhanh nhất khiến người ta bỏ qua cả cảnh báo thật.

    if do:
        return "do", do + canh_bao
    return ("vang" if canh_bao else "xanh"), canh_bao


def kiem_mang() -> tuple[str, list[str]]:
    """Đo DNS tới từng nguồn, 3 lần mỗi nguồn — mạng chập chờn phải lộ ra."""
    ket, hong, chap_chon = [], [], []
    for host, mo_ta in HOST_NGUON:
        ok = 0
        for _ in range(3):
            try:
                socket.setdefaulttimeout(6)
                socket.gethostbyname(host)
                ok += 1
            except OSError:
                pass
        if ok == 0:
            hong.append(f"{mo_ta} — KHÔNG phân giải được ({host})")
        elif ok < 3:
            chap_chon.append(f"{mo_ta} — chỉ {ok}/3 lần ({host})")
        else:
            ket.append(host)

    thong_diep = []
    if hong:
        thong_diep += hong
    if chap_chon:
        thong_diep += chap_chon
    # Mạng hỏng làm KHÔNG LẤY ĐƯỢC dữ liệu; nó không làm dữ liệu SAI. Khác hẳn
    # mock=True (dữ liệu giả) hay thiếu NCBI_EMAIL (không biết bài đã bị rút).
    # Vì vậy mạng tối đa chỉ là 🟡 — gộp vào 🔴 sẽ lẫn hai loại rủi ro rất khác
    # nhau, và làm bác sĩ quen bỏ qua màu đỏ vì mạng bệnh viện hay chập chờn.
    if hong or chap_chon:
        return "vang", thong_diep
    return "xanh", thong_diep


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Kiểm máy có đang lấy chứng cứ THẬT không")
    ap.add_argument("--im-khi-on", action="store_true",
                    help="không in gì khi mọi thứ ổn (dùng cho hook)")
    ap.add_argument("--nhanh", action="store_true",
                    help="bỏ phần đo mạng (12 truy vấn DNS) — dùng cho hook lúc mở phiên")
    a = ap.parse_args()

    m_env, tin_env = kiem_env()
    if a.nhanh:
        # Chỉ chấm CẤU HÌNH: đây là phần bắt được rủi ro nghiêm trọng nhất (chạy dữ
        # liệu giả) và chạy tức thì. Phần đo mạng để dành cho lượt chạy tay, vì với
        # DNS chập chờn nó có thể mất hàng chục giây — quá lâu cho lúc mở phiên.
        m_mang, tin_mang = "xanh", []
    else:
        m_mang, tin_mang = kiem_mang()

    muc = {"do": 2, "vang": 1, "xanh": 0}
    ma = max(muc[m_env], muc[m_mang])

    if ma == 0:
        if not a.im_khi_on:
            if a.nhanh:
                # KHÔNG được nói gì về mạng ở chế độ nhanh — chế độ này không đo mạng.
                print("🟢 CẤU HÌNH NGUỒN ĐÚNG — không bật chế độ dữ liệu giả, có NCBI_EMAIL.")
                print("   (Chưa đo đường mạng tới nguồn — bỏ `--nhanh` nếu muốn kiểm cả phần đó.)")
            else:
                print(f"🟢 NGUỒN THẬT — cấu hình đúng, {len(HOST_NGUON)}/{len(HOST_NGUON)} "
                      f"nguồn phân giải được.")
            print("   (Chỉ nói về khả năng LẤY được dữ liệu thật — không thay việc bác sĩ "
                  "thẩm định nội dung.)")
        return 0

    if a.im_khi_on:
        print("")
    print("🔴 CHỨNG CỨ KHÔNG ĐÁNG TIN Ở MÁY NÀY" if ma == 2
          else "🟡 NGUỒN CHỨNG CỨ CHƯA CHẮC CHẮN")
    if tin_env:
        print("\n   Cấu hình:")
        for t in tin_env:
            print(f"   • {t}")
    if tin_mang:
        print("\n   Mạng tới nguồn:")
        for t in tin_mang:
            print(f"   • {t}")

    if muc[m_env] == 2:
        # Chỉ hiện hướng dẫn sửa cấu hình khi CHÍNH cấu hình đang hỏng.
        print("\n   ⛔ Trong lúc này, KHÔNG dùng kết quả quét/giám sát của máy này để")
        print("      kết luận về chứng cứ — số liệu có thể là dữ liệu GIẢ.")
        print("\n   Cách sửa:")
        print("      1) Tạo thư mục ngoài OneDrive:  ~/.ebm-secrets/")
        print("      2) Tạo file  ~/.ebm-secrets/medical-ebm-automation.env  với tối thiểu:")
        print("            USE_MOCK_SOURCES=false")
        print("            NCBI_EMAIL=<email của bác sĩ>")
        print("      app/config.py đọc thẳng file này, không cần symlink qua OneDrive.")
    elif muc[m_mang] >= 1:
        print("\n   → Cấu hình nguồn ĐÚNG (không chạy dữ liệu giả). Vấn đề nằm ở đường")
        print("     mạng tới nguồn, nên kết quả xác minh lúc này có thể còn THIẾU —")
        print("     nhưng những gì đã xác minh được vẫn có giá trị.")
        print("     Chạy lại `tools/so_xac_minh_nguon.py --vong 3` khi mạng khá hơn;")
        print("     sổ xác minh tích luỹ dần nên không mất công làm lại từ đầu.")
    print("\n   Cần bác sĩ kiểm chứng.")
    return ma


if __name__ == "__main__":
    raise SystemExit(main())
