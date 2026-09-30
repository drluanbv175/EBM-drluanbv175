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
import os
import random
import socket
import struct
import sys
import time
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


def _chuyen_sang_venv() -> None:
    """Tự chạy lại bằng venv EBM khi interpreter hiện tại thiếu thư viện.

    VÌ SAO CÓ (12/08/2026) — đây là một BÁO ĐỘNG GIẢ đã xảy ra thật:
    `app.config` cần `python-dotenv`, thư viện này CHỈ có trong `~/.ebm-venv`.
    Nhưng lệnh ghi trong CLAUDE.md là `python3 tools/chu_trinh_chung_cu.py`, mà
    `python3` trên máy này trỏ tới Python hệ thống 3.14 — KHÔNG có dotenv. Khi đó
    `kiem_env()` bắt mọi Exception rồi kết luận "🔴 CHỨNG CỨ KHÔNG ĐÁNG TIN Ở MÁY
    NÀY", và `chu_trinh_chung_cu.py` DỪNG toàn bộ 5 bước còn lại.

    Tức là: chạy đúng lệnh đã ghi trong tài liệu thì hệ báo chứng cứ không đáng
    tin — trong khi chạy bằng venv lại cho 🟢 4/4 nguồn phân giải được. Đúng thứ
    mà docstring của `kiem_env()` cảnh báo phải tránh: "cảnh báo sai sẽ làm người
    ta quen bỏ qua cảnh báo thật".

    Cách vá: thay vì bắt bác sĩ nhớ gõ đường dẫn venv, công cụ TỰ chuyển sang
    venv một lần. Biến môi trường chặn đệ quy vô hạn nếu chính venv cũng thiếu.
    """
    import os

    if os.environ.get("_EBM_DA_CHUYEN_VENV"):
        return                      # đã thử một lần rồi — không lặp
    try:
        import dotenv  # noqa: F401, PLC0415
        return                      # interpreter hiện tại đã đủ
    except ImportError:
        pass

    goc_venv = Path.home() / ".ebm-venv"
    venv = goc_venv / "bin/python"
    if not venv.exists():
        return
    # So sánh bằng `sys.prefix`, TUYỆT ĐỐI không dùng `Path(...).resolve()` trên
    # đường dẫn interpreter: `~/.ebm-venv/bin/python` là symlink → `python3.14` →
    # `/Library/Frameworks/.../bin/python3.14`, tức resolve() của venv và của
    # python hệ thống ra CÙNG một đường dẫn. Bản vá đầu tiên của chính rào này đã
    # mắc đúng bẫy đó và thoát sớm, không bao giờ chuyển venv. `sys.prefix` thì
    # khác nhau thật: venv cho `~/.ebm-venv`, hệ thống cho `/Library/Frameworks/...`.
    if Path(_sys_utf8.prefix) == goc_venv:
        return                      # đang chạy chính venv rồi
    os.environ["_EBM_DA_CHUYEN_VENV"] = "1"
    os.execv(str(venv), [str(venv), *_sys_utf8.argv])


# CHỈ chuyển venv khi chạy TRỰC TIẾP. Nếu để ở mức module, một tool khác chỉ cần
# `import` file này là os.execv() THAY THẾ luôn tiến trình của nó — mất sạch việc
# đang làm. (Đã vấp đúng lỗi này khi tự kiểm bản vá, 12/08/2026.)
if __name__ == "__main__":
    _chuyen_sang_venv()


REPO = Path(__file__).resolve().parents[1]
import importlib.util as _ilu_mea  # noqa: E402
_sp_mea = _ilu_mea.spec_from_file_location("_bst_knt", Path(__file__).resolve().parent / "ban_sao_tran.py")
_bst_mea = _ilu_mea.module_from_spec(_sp_mea)
_sp_mea.loader.exec_module(_bst_mea)
MEA = _bst_mea.duong_goc("medical-ebm-automation", REPO) or (REPO / "medical-ebm-automation")

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

    # VÁ 24/09/2026 (đo lại nguồn trên Cloud): phiên Cloud CHỈ-MỘT-REPO không có engine, nên
    # `from app.config` ném «No module named 'app'» và nhánh ImportError dưới đây báo «THIẾU THƯ
    # VIỆN — cài venv» (khuyên sai: không có engine thì cài gì cũng vô ích), còn hook Cloud đọc mã 1
    # thành «DỮ LIỆU GIẢ» — trong khi môi trường đã đặt USE_MOCK_SOURCES=false + NCBI_EMAIL. Vắng
    # engine = KHÔNG ĐO ĐƯỢC (🟡), không phải «thiếu thư viện», càng không phải «dữ liệu giả».
    # Chỉ nêu biến môi trường OS khai gì; KHÔNG in giá trị NCBI_EMAIL (thông tin cá nhân).
    if not (MEA / "app" / "config.py").exists():
        import os  # noqa: PLC0415
        mock = os.environ.get("USE_MOCK_SOURCES")
        return "vang", [
            f"máy này KHÔNG có repo engine medical-ebm-automation (đã tìm {REPO / 'medical-ebm-automation'} và "
            f"{REPO.parent / 'medical-ebm-automation'}) — KHÔNG ĐO ĐƯỢC cấu hình nguồn; đây KHÔNG phải kết luận "
            f"«dữ liệu giả», cũng không phải thiếu thư viện.\n"
            f"     Biến môi trường OS khai: USE_MOCK_SOURCES={mock if mock is not None else '(không đặt)'} · "
            f"NCBI_EMAIL={'có' if os.environ.get('NCBI_EMAIL') else '(không đặt)'}.\n"
            f"     Phiên Cloud một-repo: thêm repo medical-ebm-automation vào phiên (hoặc clone cạnh repo gốc) "
            f"rồi chạy lại."]

    sys.path.insert(0, str(MEA))
    try:
        from app.config import settings  # noqa: PLC0415
    except ImportError as e:  # noqa: BLE001
        # THIẾU THƯ VIỆN ≠ CHỨNG CỨ KHÔNG ĐÁNG TIN. Đây là lỗi MÔI TRƯỜNG CHẠY
        # (gọi nhầm interpreter), không phải phát biểu gì về nguồn y văn. Xếp đỏ
        # ở đây từng làm `chu_trinh_chung_cu.py` DỪNG cả 5 bước sau và tuyên bố
        # "CHỨNG CỨ KHÔNG ĐÁNG TIN Ở MÁY NÀY" — trong khi chạy bằng venv thì 4/4
        # nguồn phân giải được. Rào `_chuyen_sang_venv()` ở đầu file đã tự xử lý
        # trường hợp thường gặp; tới đây nghĩa là venv cũng thiếu.
        return "vang", [
            f"chưa chạy được app.config vì THIẾU THƯ VIỆN ({e}) — đây là lỗi môi "
            f"trường, KHÔNG phải kết luận về nguồn chứng cứ.\n"
            f"     Cài vào venv EBM:  ~/.ebm-venv/bin/pip install -r "
            f"medical-ebm-automation/requirements.txt"]
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


# ── đo mạng HAI TẦNG (30/09/2026, BH135) ─────────────────────────────────────
# Bản cũ chỉ gọi `gethostbyname`: «phân giải được» bị coi là «tới được». Đo thật trên máy Windows 30/09: api.crossref.org
# có lúc phân giải được mà cổng 443 KHÔNG thông 10/10 lần trong 2,5 phút (cùng cụm máy chủ với api.wiley.com) ⇒ chốt ①
# của `chu_trinh_chung_cu` báo 🟢 «4/4 nguồn phân giải được» trong khi Crossref không tới được. Ngược lại, DNS nội bộ
# (192.1.1.214) trả lời sau 7–12 s hoặc hết hạn trong khi DNS công cộng trả lời trong ~45 ms — «không phân giải được» lúc
# đó là lỗi của MÁY CHỦ DNS đang dùng, không phải nguồn sập. Hai loại lỗi có cách chữa khác hẳn nhau nên phải nói riêng.
HAN_NOI_GIAY = 5.0                       # nối TCP tới cổng 443
NGUONG_DNS_CHAM_GIAY = 3.0               # phân giải lâu hơn ngưỡng này là «chậm» (bình thường < 0,3 s)
# Chỉ để ĐỐI CHIẾU khi DNS của máy không trả lời — công cụ KHÔNG đổi cài đặt mạng nào. Không hỏi được (mạng chặn UDP 53
# ra ngoài) ⇒ None ⇒ không kết luận thêm.
DNS_CONG_CONG = ("8.8.8.8", "1.1.1.1")


def _phan_giai(host: str) -> tuple[str | None, float]:
    """(IP hoặc None, số giây) qua bộ phân giải của HỆ ĐIỀU HÀNH — đúng đường mà pipeline dùng."""
    t0 = time.monotonic()
    try:
        ip = socket.gethostbyname(host)
    except OSError:
        ip = None
    return ip, time.monotonic() - t0


def _noi_duoc(ip: str, cong: int = 443, han: float = HAN_NOI_GIAY) -> bool:
    """Bắt tay TCP tới `ip:cong` được không. Không gửi byte nào — chỉ đo đường truyền."""
    try:
        with socket.create_connection((ip, cong), timeout=han):
            return True
    except OSError:
        return False


def _goi_hoi_dns(host: str, ma: int) -> bytes:
    """Gói truy vấn DNS bản ghi A (RFC 1035), bật cờ đệ quy."""
    goi = struct.pack(">HHHHHH", ma, 0x0100, 1, 0, 0, 0)
    for nhan in host.strip(".").split("."):
        goi += bytes([len(nhan)]) + nhan.encode("ascii")
    return goi + b"\x00" + struct.pack(">HH", 1, 1)


def _doc_tra_loi_dns(du_lieu: bytes, ma: int) -> str | None:
    """IPv4 đầu tiên trong phần trả lời; None khi sai mã, có mã lỗi, không có bản ghi A, hoặc gói hỏng."""
    try:
        ma_tl, co, so_hoi, so_tl = struct.unpack(">HHHH", du_lieu[:8])
        if ma_tl != ma or (co & 0x000F) != 0 or so_tl == 0:
            return None

        def qua_ten(vi_tri: int) -> int:
            while True:
                dai = du_lieu[vi_tri]
                if dai & 0xC0 == 0xC0:                       # con trỏ nén: 2 byte rồi hết tên
                    return vi_tri + 2
                if dai == 0:
                    return vi_tri + 1
                vi_tri += dai + 1

        vi_tri = 12
        for _ in range(so_hoi):
            vi_tri = qua_ten(vi_tri) + 4                     # QTYPE + QCLASS
        for _ in range(so_tl):
            vi_tri = qua_ten(vi_tri)
            loai, _lop, _ttl, dai = struct.unpack(">HHIH", du_lieu[vi_tri:vi_tri + 10])
            vi_tri += 10
            if loai == 1 and dai == 4:
                return ".".join(str(b) for b in du_lieu[vi_tri:vi_tri + 4])
            vi_tri += dai
    except (IndexError, struct.error):
        return None
    return None


def _hoi_dns_cong_cong(host: str, may_chu: str, han: float = 3.0) -> str | None:
    """Hỏi THẲNG một DNS công cộng (UDP 53) — phân biệt «DNS của mạng này hỏng» với «nguồn/tên miền có vấn đề»."""
    ma = random.randint(0, 0xFFFF)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(han)
            s.sendto(_goi_hoi_dns(host, ma), (may_chu, 53))
            du_lieu, _ = s.recvfrom(1024)
    except (OSError, UnicodeError):
        return None
    return _doc_tra_loi_dns(du_lieu, ma)


def _di_qua_proxy() -> bool:
    """Phiên Cloud/mạng có proxy: tiến trình không tự nối thẳng được tới nguồn (mọi thứ đi qua proxy) ⇒ thử bắt tay TCP
    trực tiếp ở đó chỉ sinh báo động giả. Khi ấy giữ phép đo DNS như cũ."""
    return any(os.environ.get(k) for k in ("HTTPS_PROXY", "https_proxy", "ALL_PROXY", "all_proxy"))


def kiem_mang() -> tuple[str, list[str]]:
    """Đo HAI tầng tới từng nguồn: DNS (3 lần — mạng chập chờn phải lộ ra) rồi bắt tay TCP cổng 443.

    «Phân giải được» ≠ «tới được». DNS của máy không trả lời thì đối chiếu DNS công cộng để nói đúng lỗi nằm ở đâu.
    """
    ket, hong, chap_chon = [], [], []
    thu_noi = not _di_qua_proxy()
    for host, mo_ta in HOST_NGUON:
        lan = [_phan_giai(host) for _ in range(3)]
        ips = [ip for ip, _ in lan if ip]
        if not ips:
            ip_cc = next((ip for ip in (_hoi_dns_cong_cong(host, m) for m in DNS_CONG_CONG) if ip), None) \
                if thu_noi else None
            if ip_cc:
                con_vuong = "" if _noi_duoc(ip_cc) else (
                    f"; nối thẳng {ip_cc}:443 cũng KHÔNG thông ⇒ còn vướng cả đường truyền/tường lửa")
                hong.append(f"{mo_ta} — DNS của mạng này KHÔNG phân giải được ({host}) trong khi DNS công cộng "
                            f"phân giải được ⇒ lỗi ở máy chủ DNS đang dùng, không phải nguồn sập{con_vuong}")
            else:
                hong.append(f"{mo_ta} — KHÔNG phân giải được ({host})"
                            + ("; DNS công cộng cũng không hỏi được ⇒ mất mạng hoặc mạng chặn DNS ra ngoài"
                               if thu_noi else ""))
            continue
        if thu_noi and not (_noi_duoc(ips[-1]) or _noi_duoc(ips[-1])):      # thử lại một lần: một nhịp rớt ≠ bị chặn
            hong.append(f"{mo_ta} — phân giải được ({host} → {ips[-1]}) nhưng KHÔNG nối được cổng 443 trong "
                        f"{HAN_NOI_GIAY:.0f} s ⇒ đường truyền/tường lửa, KHÔNG phải DNS; nguồn này hiện không tới được")
        elif len(ips) < 3:
            chap_chon.append(f"{mo_ta} — DNS chỉ {len(ips)}/3 lần ({host})")
        elif max(t for _, t in lan) > NGUONG_DNS_CHAM_GIAY:
            chap_chon.append(f"{mo_ta} — DNS chậm {max(t for _, t in lan):.0f} s ({host}); máy chủ DNS đang dùng "
                             "trả lời chậm, lời gọi nguồn dễ hết hạn ở lần đầu")
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
                    help="bỏ phần đo mạng (DNS + nối cổng 443 tới từng nguồn) — dùng cho hook lúc mở phiên")
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
                      + ("nguồn phân giải được (mạng qua proxy — không đo nối trực tiếp)." if _di_qua_proxy()
                         else "nguồn phân giải VÀ nối được cổng 443."))
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
