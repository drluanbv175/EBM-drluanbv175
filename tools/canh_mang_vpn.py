#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CANH MẠNG + VPN — báo SỚM khi máy mất đường ra Internet vì VPN rớt, tự thử nối lại VPN, đếm số lần rớt (27/10/2026).

VÌ SAO CÓ. Đo 27/10/2026 trên Mac mini của bác sĩ: 15:28 Kaspersky VPN rớt («Plugin initiated») ⇒ macOS ghi «No network route»
~930–1.000 dòng/phút (0 dòng trước 15:28) ⇒ MẤT MẠNG ~1 giờ 50 phút, chỉ hết khi bác sĩ khởi động lại máy lúc 17:18; 18:37–18:39 VPN
chập chờn 3 vòng. Wi-Fi không rớt lần nào. Không có gì báo ⇒ bác sĩ chỉ biết khi việc đã hỏng, và cách chữa duy nhất biết được là khởi
động lại. Nhật ký sự cố: audit/nhat-ky/2026-10-27-vpn-rot-mat-duong-mang.md (BH171).

    python3 tools/canh_mang_vpn.py                      # đo MỘT mẫu và in (không hành động, không ghi gì)
    python3 tools/canh_mang_vpn.py --chay-nen           # (launchd mỗi phút) đo · ghi state · thông báo · tự thử nối lại VPN khi MẤT MẠNG
    python3 tools/canh_mang_vpn.py --doc --im-khi-on    # (hook SessionStart) im khi ổn; báo mất mạng 24 giờ qua / đang hỏng
                                   [--do-nguon-nen]     #   + máy chủ VPN đổi ⇒ đo lại nguồn chứng cứ ở nền (do_mang_nguon.py)
    python3 tools/canh_mang_vpn.py --bao-cao [--ngay 7] # thống kê số lần/thời gian mất mạng, VPN tắt, đổi máy chủ
    python3 tools/canh_mang_vpn.py --tam-dung 120       # ngừng nhắc + tự nối lại 120 phút (khi CỐ Ý tắt VPN); --tiep-tuc để bỏ
    python3 tools/canh_mang_vpn.py --cai-launchd        # CHẠY KHÔ; thêm --ap-dung để cài (macOS); --go-launchd [--ap-dung] để gỡ

Phân loại một mẫu: 🟢 ON (có mạng, VPN nối) · 🟡 VPN_TAT (có mạng nhưng đi thẳng — PubMed/NCBI có thể chặn) · 🟡 VPN_DANG_NOI
(có mạng, VPN đang nối/nối lại) · 🔴 MAT_MANG (không ra được Internet) · ⚪ KHONG_DO (không phải macOS / không chạy được scutil —
KHÔNG BAO GIỜ đọc thành ổn). «Có mạng» = mở được kết nối TCP tới ít nhất một trong 1.1.1.1 · 8.8.8.8 · 9.9.9.9 cổng 443 (không
gửi dữ liệu). Sự cố chỉ tính khi ≥ 2 mẫu xấu liên tiếp (chống chớp tắt).
Tự nối lại CHỈ khi MẤT MẠNG mà vẫn có Wi-Fi/mạng dây: VPN tắt ⇒ bật; VPN «đang nối» mà vẫn mất mạng ≥ 3 mẫu ⇒ ngắt rồi bật; tối đa
2 lần mỗi sự cố, cách nhau ≥ 10 phút (đo 27/10: `scutil --nc start` lúc được lúc không — thông báo vẫn là chính). VPN tắt mà vẫn có
mạng thì CHỈ nhắc, không tự bật (có thể bác sĩ cố ý tắt). Không xoá gì, không giết tiến trình, không đổi cấu hình mạng."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import plistlib
import re
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Callable

REPO = Path(__file__).resolve().parent.parent
# State NGOÀI OneDrive (lệ ~/.ebm-venv, ~/.ebm-secrets): agent nền ghi MỖI PHÚT — trong cây OneDrive sẽ bắt OneDrive đồng bộ liên tục
# (máy này từng bị OneDrive kẹt vòng lặp log, BH149), và số đo mạng là của RIÊNG máy này, không đi sang Windows.
THU_MUC = Path.home() / ".ebm-canh-mang"
TEP_STATE = THU_MUC / "state.json"                  # agent nền ghi mỗi phút
TEP_SU_CO = THU_MUC / "su-co.jsonl"                 # mỗi sự cố / lần đổi máy chủ một dòng
TEP_TAM_DUNG = THU_MUC / "tam-dung.json"            # bác sĩ ghi; agent nền chỉ đọc
TEP_PHIEN = THU_MUC / "phien.json"                  # hook phiên ghi — TÁCH tệp để không giành ghi với agent nền
TEP_DO_NGUON = THU_MUC / "do-nguon.json"
TEP_LOG_DO_NGUON = THU_MUC / "do-nguon.log"
BAN_CAI = THU_MUC / "canh_mang_vpn.py"              # agent nền chạy BẢN CHÉP này (không đọc tệp trong OneDrive từ launchd)
CONG_CU_DO_NGUON = REPO / "medical-ebm-automation" / "tools" / "do_mang_nguon.py"
NHAN_LAUNCHD = "vn.drluan.ebm-canh-mang"
TEN_VPN = "Kaspersky VPN"
SCUTIL = "/usr/sbin/scutil"
DICH_KIEM = (("1.1.1.1", 443), ("8.8.8.8", 443), ("9.9.9.9", 443))
HAN_KET_NOI_GIAY = 3.0
CHU_KY_GIAY = 60
MAU_XAC_NHAN = 2                    # ≥ 2 mẫu xấu liên tiếp mới là sự cố
MAU_TRUOC_KHI_NGAT_BAT = 3          # VPN «đang nối» mà mất mạng: chờ 3 mẫu cho nó tự hồi
TOI_DA_NOI_LAI = 2
KHOANG_NOI_LAI_GIAY = 600
KHOANG_NHAC_MAT_MANG_GIAY = 900
MAU_NHAC_VPN_TAT = 5                # tắt VPN tay vài phút (đo nguồn, Scopus) thì chưa nhắc
KHOANG_NHAC_VPN_TAT_GIAY = 3600
TUOI_STATE_NEN_GIAY = 300
KHOANG_DO_NGUON_GIAY = 1800
DUONG_HAM = ("utun", "ipsec", "ppp", "tun", "tap", "wg")
TRANG_THAI_VPN = ("Connected", "Disconnected", "Connecting", "Disconnecting", "Reasserting", "Invalid")
XAU = ("MAT_MANG", "VPN_TAT")
MA_THOAT = {"ON": 0, "VPN_DANG_NOI": 1, "VPN_TAT": 1, "MAT_MANG": 2, "KHONG_DO": 3}
BIEU = {"ON": "🟢", "VPN_DANG_NOI": "🟡", "VPN_TAT": "🟡", "MAT_MANG": "🔴", "KHONG_DO": "⚪"}

ChayLenh = Callable[[list], str]


# ── đo ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _chay(lenh: list, han: float = 8.0) -> str:
    try:
        r = subprocess.run(lenh, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=han)
        return r.stdout or ""
    except (OSError, subprocess.SubprocessError):
        return ""


def _ket_noi(dich=DICH_KIEM, han: float = HAN_KET_NOI_GIAY) -> bool:
    """Có mở được MỘT kết nối TCP ra Internet không (đóng ngay, không gửi dữ liệu)."""
    for may, cong in dich:
        try:
            with socket.create_connection((may, cong), timeout=han):
                return True
        except OSError:
            continue
    return False


def bam(gia_tri: str) -> str:
    """Băm 8 ký tự địa chỉ máy chủ VPN — không lưu IP thô (cùng lệ với dấu vân mạng của engine)."""
    return hashlib.sha256(gia_tri.encode("utf-8")).hexdigest()[:8]


def doc_trang_thai_vpn(ra: str) -> str | None:
    """Dòng đầu của `scutil --nc status <tên>`; không phải trạng thái hợp lệ (vd «No service») ⇒ None."""
    dong = (ra.strip().splitlines() or [""])[0].strip()
    return dong if dong in TRANG_THAI_VPN else None


def doc_nwi(ra: str) -> tuple:
    """(băm máy chủ VPN | None, giao diện VẬT LÝ đang nối | None) từ `scutil --nwi`. None = không đọc được, [] = không có."""
    m = re.search(r"^\s*VPN server\s*:\s*(\S+)\s*$", ra, re.M)
    may_chu = bam(m.group(1)) if m else None
    g = re.search(r"^\s*Network interfaces:[ \t]*(.*)$", ra, re.M)
    if not g:
        return may_chu, None
    return may_chu, [x for x in g.group(1).split() if not x.startswith(DUONG_HAM)]


def do_mang(chay: ChayLenh | None = None, ket_noi: Callable[[], bool] | None = None, nen_tang: str | None = None,
            ten_vpn: str = TEN_VPN, bay_gio: float | None = None) -> dict:
    """Một mẫu đường mạng LÚC NÀY. Không ném lỗi. `chay`/`ket_noi`/`nen_tang` chỉ để kiểm thử."""
    t = time.time() if bay_gio is None else bay_gio
    nen_tang = nen_tang or sys.platform
    if nen_tang != "darwin":
        return {"t": t, "do_duoc": False, "ly_do": f"chỉ canh được trên macOS (máy này: {nen_tang})"}
    chay = chay or _chay
    ra_vpn = chay([SCUTIL, "--nc", "status", ten_vpn])
    ra_nwi = chay([SCUTIL, "--nwi"])
    if not ra_vpn and not ra_nwi:
        return {"t": t, "do_duoc": False, "ly_do": "không chạy được scutil"}
    may_chu, vat_ly = doc_nwi(ra_nwi)
    return {"t": t, "do_duoc": True, "vpn": doc_trang_thai_vpn(ra_vpn), "may_chu": may_chu, "vat_ly": vat_ly,
            "co_mang": bool((ket_noi or _ket_noi)())}


def phan_loai(do: dict) -> tuple:
    """(mức, lý do). HÀM THUẦN. Mất mạng thì luôn ĐỎ dù scutil báo VPN «Connected» (đường hầm có thể đã chết)."""
    if not do.get("do_duoc"):
        return "KHONG_DO", do.get("ly_do") or "không đo được"
    vpn = do.get("vpn")
    ten = vpn or "không thấy dịch vụ VPN"
    if not do.get("co_mang"):
        if do.get("vat_ly") == []:
            return "MAT_MANG", "không có Wi-Fi/mạng dây nào đang nối"
        return "MAT_MANG", f"có Wi-Fi/mạng dây nhưng không ra được Internet (VPN: {ten})"
    if vpn == "Connected":
        return "ON", "có mạng, đi qua VPN"
    if vpn in ("Connecting", "Reasserting", "Disconnecting"):
        return "VPN_DANG_NOI", f"có mạng, VPN đang {vpn}"
    return "VPN_TAT", f"có mạng nhưng KHÔNG qua VPN ({ten}) — PubMed/NCBI có thể chặn"


# ── máy trạng thái (thuần) ───────────────────────────────────────────────────────────────────────────────────────────────
def thoi_luong(giay: float) -> str:
    giay = int(max(0, giay))
    if giay < 60:
        return f"{giay} giây"
    gio, phut = divmod(round(giay / 60), 60)
    return f"{gio} giờ {phut} phút" if gio else f"{phut} phút"


def _viec_khi_xau(sc: dict, do: dict, t: float) -> list:
    """Việc cần làm cho sự cố ĐANG diễn ra (sửa `sc` tại chỗ: mốc nhắc, lần nối lại)."""
    viec: list = []
    n = sc["so_mau"]
    keo_dai = thoi_luong(t - sc["bat_dau"])
    if sc["loai"] == "MAT_MANG":
        if n < MAU_XAC_NHAN:
            return viec
        vpn = do.get("vpn")
        co_vat_ly = do.get("vat_ly") != []
        kieu = None
        if co_vat_ly and vpn is not None:
            if vpn in ("Disconnected", "Invalid"):
                kieu = "bat"
            elif n >= MAU_TRUOC_KHI_NGAT_BAT:
                kieu = "ngat_bat"
        lan = sc["noi_lai"]
        if kieu and len(lan) < TOI_DA_NOI_LAI and (not lan or t - lan[-1]["luc"] >= KHOANG_NOI_LAI_GIAY):
            lan.append({"luc": t, "kieu": kieu})
            viec.append(("noi_lai", kieu))
        if sc.get("nhac_luc") is None or t - sc["nhac_luc"] >= KHOANG_NHAC_MAT_MANG_GIAY:
            sc["nhac_luc"] = t
            if not co_vat_ly:
                nd = f"Mất mạng {keo_dai}: Wi-Fi/mạng dây không nối — kiểm tra Wi-Fi, router."
            else:
                nd = (f"Mất mạng {keo_dai} (VPN: {vpn or 'không rõ'}). Mở Kaspersky → VPN → ngắt rồi kết nối lại; "
                      "không cần khởi động lại máy.") + (" Máy đã tự thử nối lại VPN." if lan else "")
            viec.append(("thong_bao", "MẠNG — mất kết nối", nd))
    elif n >= MAU_NHAC_VPN_TAT and (sc.get("nhac_luc") is None or t - sc["nhac_luc"] >= KHOANG_NHAC_VPN_TAT_GIAY):
        sc["nhac_luc"] = t
        viec.append(("thong_bao", "VPN đang tắt",
                     f"Máy đi thẳng không qua VPN đã {keo_dai} — PubMed/NCBI có thể chặn. Bật lại trong app Kaspersky "
                     "(cố ý tắt thì: canh_mang_vpn.py --tam-dung <phút>)."))
    return viec


def buoc(st: dict, do: dict, tam_dung_den: float = 0.0) -> tuple:
    """HÀM THUẦN: (state cũ, mẫu mới) → (state mới, việc). Việc: ("thong_bao", tiêu đề, nội dung) · ("noi_lai", "bat"|"ngat_bat")
    · ("ghi", bản ghi). Đang tạm dừng ⇒ vẫn theo dõi và ghi sự cố, nhưng không nhắc, không tự nối lại."""
    t = float(do["t"])
    muc, ly_do = phan_loai(do)
    moi = {k: v for k, v in st.items() if k != "su_co"}
    viec: list = []
    moi["mau_cuoi"] = {"t": t, "muc": muc, "ly_do": ly_do, "vpn": do.get("vpn"), "co_mang": do.get("co_mang"),
                       "may_chu": do.get("may_chu"), "vat_ly": do.get("vat_ly")}
    sc = json.loads(json.dumps(st.get("su_co"))) if st.get("su_co") else None
    if muc == "KHONG_DO":                       # không đo được: không mở/không đóng sự cố nào — giữ nguyên
        moi["su_co"] = sc
        return moi, viec
    mc = do.get("may_chu")
    if mc:
        if st.get("may_chu") and st["may_chu"] != mc:
            viec.append(("ghi", {"loai": "DOI_MAY_CHU", "luc": t, "truoc": st["may_chu"], "sau": mc}))
        moi["may_chu"] = mc
    dang_dung = float(tam_dung_den or 0) > t
    xau = muc if muc in XAU else None
    if sc and sc.get("loai") != xau:
        if sc.get("so_mau", 0) >= MAU_XAC_NHAN:
            viec.append(("ghi", {"loai": sc["loai"], "bat_dau": sc["bat_dau"], "ket_thuc": t, "giay": int(t - sc["bat_dau"]),
                                 "vpn_luc_dau": sc.get("vpn_luc_dau"), "noi_lai": sc.get("noi_lai", [])}))
            if sc.get("nhac_luc") is not None and not dang_dung:
                if sc["loai"] == "MAT_MANG":
                    viec.append(("thong_bao", "MẠNG — đã hồi phục", f"Có mạng trở lại sau {thoi_luong(t - sc['bat_dau'])}."))
                elif muc == "ON":
                    viec.append(("thong_bao", "VPN đã bật lại", f"Máy lại đi qua VPN (đã tắt {thoi_luong(t - sc['bat_dau'])})."))
        sc = None
    if xau:
        if not sc:
            sc = {"loai": xau, "bat_dau": t, "so_mau": 0, "vpn_luc_dau": do.get("vpn"), "noi_lai": [], "nhac_luc": None}
        sc["so_mau"] += 1
        if not dang_dung:
            viec += _viec_khi_xau(sc, do, t)
    moi["su_co"] = sc
    return moi, viec


# ── tệp ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def doc_json(duong: Path) -> dict:
    try:
        d = json.loads(Path(duong).read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def ghi_json(d: dict, duong: Path) -> None:
    duong = Path(duong)
    duong.parent.mkdir(parents=True, exist_ok=True)
    tam = duong.with_name(duong.name + f".tmp{os.getpid()}")
    tam.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    os.replace(tam, duong)


def ghi_su_co(ban_ghi: dict, duong: Path | None = None) -> None:
    duong = Path(duong or TEP_SU_CO)
    duong.parent.mkdir(parents=True, exist_ok=True)
    with open(duong, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(ban_ghi, ensure_ascii=False) + "\n")


def doc_su_co(tu_luc: float, duong: Path | None = None) -> list:
    """Bản ghi kết thúc (hoặc xảy ra) từ `tu_luc`; dòng hỏng bỏ qua, không sập."""
    ra: list = []
    try:
        dong_tep = Path(duong or TEP_SU_CO).read_text(encoding="utf-8").splitlines()
    except OSError:
        return ra
    for dong in dong_tep:
        try:
            b = json.loads(dong)
        except ValueError:
            continue
        if isinstance(b, dict) and float(b.get("ket_thuc") or b.get("luc") or 0) >= tu_luc:
            ra.append(b)
    return ra


# ── hành động (chỉ ở --chay-nen) ─────────────────────────────────────────────────────────────────────────────────────────
def thong_bao_he_thong(tieu_de: str, noi_dung: str) -> bool:
    if sys.platform != "darwin":
        return False

    def sach(s: str, n: int) -> str:
        return s.replace("\\", " ").replace('"', "'")[:n]
    try:
        subprocess.run(["osascript", "-e", f'display notification "{sach(noi_dung, 220)}" with title "{sach(tieu_de, 60)}"'],
                       capture_output=True, timeout=10)
        return True
    except (OSError, subprocess.SubprocessError):
        return False


def noi_lai_vpn(kieu: str, chay: ChayLenh | None = None, ngu: Callable[[float], None] = time.sleep,
                ten_vpn: str = TEN_VPN, cho_giay: int = 20) -> str:
    """Ngắt (nếu `ngat_bat`) rồi bật VPN qua scutil; trả trạng thái sau ≤ `cho_giay` giây. Chỉ đụng ĐÚNG dịch vụ VPN."""
    chay = chay or _chay
    if kieu == "ngat_bat":
        chay([SCUTIL, "--nc", "stop", ten_vpn])
        ngu(3)
    chay([SCUTIL, "--nc", "start", ten_vpn])
    tt = None
    for _ in range(max(1, cho_giay // 2)):
        ngu(2)
        tt = doc_trang_thai_vpn(chay([SCUTIL, "--nc", "status", ten_vpn]))
        if tt == "Connected":
            break
    return tt or "không rõ"


def chay_nen(do: dict | None = None) -> int:
    """Một nhịp của agent nền: đo → bước máy trạng thái → làm việc → ghi state."""
    st = doc_json(TEP_STATE)
    do = do if do is not None else do_mang()
    moi, viec = buoc(st, do, float(doc_json(TEP_TAM_DUNG).get("den") or 0))
    for v in viec:
        if v[0] == "ghi":
            ghi_su_co(v[1])
        elif v[0] == "noi_lai":
            moi["su_co"]["noi_lai"][-1]["ket_qua"] = noi_lai_vpn(v[1])
        elif v[0] == "thong_bao":
            thong_bao_he_thong(v[1], v[2])
    try:
        ghi_json(moi, TEP_STATE)
    except OSError as e:
        print(f"⚠ không ghi được state: {e}", file=sys.stderr)
    return MA_THOAT[moi["mau_cuoi"]["muc"]]


# ── báo cáo ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _gio(t: float) -> str:
    return datetime.fromtimestamp(float(t)).strftime("%d/%m %H:%M")


def tom_tat_mat_mang(ban_ghi: list) -> dict:
    mat = [b for b in ban_ghi if b.get("loai") == "MAT_MANG"]
    thu = [x for b in mat for x in (b.get("noi_lai") or [])]
    return {"so_lan": len(mat), "tong": sum(int(b.get("giay") or 0) for b in mat),
            "dai_nhat": max((int(b.get("giay") or 0) for b in mat), default=0),
            "thu": len(thu), "thanh_cong": sum(1 for x in thu if x.get("ket_qua") == "Connected")}


def bao_cao(ngay: int = 7, bay_gio: float | None = None) -> str:
    t = time.time() if bay_gio is None else bay_gio
    ban_ghi = doc_su_co(t - ngay * 86400)
    st = doc_json(TEP_STATE)
    mc = st.get("mau_cuoi") or {}
    dong = [f"📶 CANH MẠNG/VPN — {ngay} ngày qua (từ {_gio(t - ngay * 86400)})"]
    if not mc or t - float(mc.get("t") or 0) > TUOI_STATE_NEN_GIAY:
        dong.append("⚪ Cảm biến nền không cập nhật trong 5 phút qua — số liệu dưới đây có thể THIẾU (cài: --cai-launchd --ap-dung).")
    else:
        dong.append(f"{BIEU.get(mc.get('muc'), '⚪')} Lúc này: {mc.get('ly_do')}")
    m = tom_tat_mat_mang(ban_ghi)
    if m["so_lan"]:
        dong.append(f"🔴 Mất mạng: {m['so_lan']} lần, tổng {thoi_luong(m['tong'])}, dài nhất {thoi_luong(m['dai_nhat'])}; "
                    f"tự nối lại VPN: thử {m['thu']} lần, thành công {m['thanh_cong']}.")
    else:
        dong.append("🟢 Không ghi nhận lần mất mạng nào.")
    tat = [b for b in ban_ghi if b.get("loai") == "VPN_TAT"]
    if tat:
        dong.append(f"🟡 VPN tắt (vẫn có mạng): {len(tat)} lần, tổng {thoi_luong(sum(int(b.get('giay') or 0) for b in tat))}.")
    doi = [b for b in ban_ghi if b.get("loai") == "DOI_MAY_CHU"]
    if doi:
        dong.append(f"🔁 Đổi máy chủ VPN: {len(doi)} lần (đổi máy chủ ⇒ nguồn chặn/thông có thể khác — xem dòng 📡 ở hook phiên).")
    su_kien = [b for b in ban_ghi if b.get("loai") in XAU][-8:]
    if su_kien:
        dong.append("Gần nhất:")
        for b in su_kien:
            noi = "; ".join(f"{x.get('kieu')}→{x.get('ket_qua', '?')}" for x in b.get("noi_lai") or [])
            dong.append(f"  {_gio(b['bat_dau'])}  {'MẤT MẠNG' if b['loai'] == 'MAT_MANG' else 'VPN TẮT'} {thoi_luong(b.get('giay') or 0)}"
                        f" (VPN lúc đầu: {b.get('vpn_luc_dau') or 'không rõ'}" + (f"; tự nối lại: {noi}" if noi else "") + ")")
    sc = st.get("su_co")
    if sc and sc.get("so_mau", 0) >= MAU_XAC_NHAN:
        dong.append(f"⏳ Đang diễn ra: {sc['loai']} từ {_gio(sc['bat_dau'])} ({thoi_luong(float(mc.get('t') or t) - sc['bat_dau'])}).")
    return "\n".join(dong)


def tom_tat_do_nguon(d: dict) -> str | None:
    nguon = d.get("nguon") if isinstance(d, dict) else None
    if not isinstance(nguon, dict) or not nguon:
        return None
    hong = [(ten, (v or {}).get("ket_qua")) for ten, v in nguon.items() if (v or {}).get("ket_qua") != "OK"]
    luc = ((d.get("mang") or {}).get("luc") or "")
    try:
        luc = datetime.fromisoformat(luc).astimezone().strftime("%H:%M %d/%m")
    except ValueError:
        pass
    s = f"📡 Nguồn chứng cứ đo lại lúc {luc}: {len(nguon) - len(hong)}/{len(nguon)} tới được"
    if hong:
        s += " · hỏng: " + ", ".join(f"{ten} ({kq})" for ten, kq in hong[:6]) + ("…" if len(hong) > 6 else "")
    if any("NCBI" in ten for ten, _ in hong):
        s += " — ⚠ PubMed/NCBI bị chặn: tra chứng cứ sẽ lỗi, thử đổi vị trí máy chủ VPN trong app Kaspersky"
    return s


def khoi_dong_do_nguon() -> tuple:
    """Chạy do_mang_nguon.py ở NỀN (tách phiên), ghi kết quả vào TEP_DO_NGUON. Không chờ."""
    if not CONG_CU_DO_NGUON.is_file():
        return False, "thiếu " + CONG_CU_DO_NGUON.relative_to(REPO).as_posix()
    venv = Path.home() / ".ebm-venv" / "bin" / "python"
    py = str(venv) if venv.is_file() else sys.executable
    try:
        TEP_LOG_DO_NGUON.parent.mkdir(parents=True, exist_ok=True)
        with open(TEP_LOG_DO_NGUON, "w", encoding="utf-8") as log:
            subprocess.Popen([py, str(CONG_CU_DO_NGUON), "--ghi", str(TEP_DO_NGUON)], cwd=str(CONG_CU_DO_NGUON.parent.parent),
                             stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
    except OSError as e:
        return False, f"không phóng được ({e})"
    return True, ""


def kiem_do_nguon(muc: str, may_chu: str | None, t: float) -> list:
    """Báo kết quả đo nguồn MỚI (một lần); máy chủ VPN khác lần đo trước ⇒ phóng đo lại ở nền (≥ 30 phút một lần)."""
    sp = doc_json(TEP_PHIEN)
    dong: list = []
    try:
        mt = TEP_DO_NGUON.stat().st_mtime
    except OSError:
        mt = None
    if mt and mt > float(sp.get("bao_luc") or 0):
        s = tom_tat_do_nguon(doc_json(TEP_DO_NGUON))
        if s:
            dong.append(s)
        sp["bao_luc"] = mt
    if muc == "ON" and may_chu and may_chu != sp.get("may_chu_da_do") and t - float(sp.get("do_luc") or 0) >= KHOANG_DO_NGUON_GIAY:
        ok, ly = khoi_dong_do_nguon()
        sp["do_luc"] = t
        if ok:
            cu = sp.get("may_chu_da_do")
            sp["may_chu_da_do"] = may_chu
            dong.append(f"📡 Máy chủ VPN {'đổi #' + cu + ' → #' + may_chu if cu else 'hiện tại #' + may_chu + ' chưa có số đo nguồn'}"
                        " — đang đo lại các nguồn chứng cứ ở nền (~1 phút); kết quả hiện ở lần mở phiên sau.")
        else:
            dong.append(f"⚪ Không đo lại nguồn chứng cứ được: {ly}")
    try:
        ghi_json(sp, TEP_PHIEN)
    except OSError:
        pass
    return dong


def da_cai_launchd() -> bool:
    return (Path.home() / "Library" / "LaunchAgents" / f"{NHAN_LAUNCHD}.plist").is_file()


def ban_cai_cu() -> bool:
    """Bản chạy nền đã chép khác bản trong repo (repo vừa cập nhật mà chưa cài lại)."""
    try:
        return BAN_CAI.read_bytes() != Path(__file__).resolve().read_bytes()
    except OSError:
        return False


def doc_cho_phien(im_khi_on: bool, do_nguon_nen: bool, bay_gio: float | None = None, do: dict | None = None) -> int:
    """Hook SessionStart: đọc kết quả agent nền (< 5 phút) — nền không chạy thì đo nhanh một mẫu và nói rõ."""
    t = time.time() if bay_gio is None else bay_gio
    st = doc_json(TEP_STATE)
    mc = st.get("mau_cuoi") or {}
    nen_song = bool(mc) and t - float(mc.get("t") or 0) <= TUOI_STATE_NEN_GIAY
    if nen_song:
        muc, ly_do, may_chu = mc.get("muc", "KHONG_DO"), mc.get("ly_do", ""), mc.get("may_chu")
    else:
        do = do if do is not None else do_mang()
        muc, ly_do = phan_loai(do)
        may_chu = do.get("may_chu")
    if muc == "KHONG_DO":
        print(f"⚪ CANH MẠNG/VPN: không đo được — {ly_do}")
        return 3
    dong: list = []
    if da_cai_launchd() and ban_cai_cu():
        dong.append("🟡 Cảm biến mạng nền đang chạy bản CŨ — cài lại: python3 tools/canh_mang_vpn.py --cai-launchd --ap-dung")
    if not nen_song:
        dong.append("🟡 Cảm biến mạng nền có cài nhưng không cập nhật > 5 phút — kiểm: launchctl list | grep ebm-canh-mang"
                    if da_cai_launchd() else
                    "⚪ Cảm biến mạng chưa chạy nền — cài: python3 tools/canh_mang_vpn.py --cai-launchd --ap-dung")
    m = tom_tat_mat_mang(doc_su_co(t - 86400))
    if m["so_lan"]:
        dong.append(f"🔴 MẠNG 24 giờ qua: mất mạng {m['so_lan']} lần, tổng {thoi_luong(m['tong'])} (dài nhất "
                    f"{thoi_luong(m['dai_nhat'])}); tự nối lại VPN thành công {m['thanh_cong']}/{m['thu']} lần — "
                    "chi tiết: python3 tools/canh_mang_vpn.py --bao-cao")
    if muc != "ON":
        dong.append(f"{BIEU[muc]} MẠNG lúc này: {ly_do}")
    if do_nguon_nen:
        dong += kiem_do_nguon(muc, may_chu, t)
    ma = 2 if (muc == "MAT_MANG" or m["so_lan"]) else (1 if dong else 0)
    if not dong:
        if not im_khi_on:
            print("🟢 MẠNG: có mạng, đi qua VPN; 24 giờ qua không mất mạng.")
        return 0
    print("\n".join(dong))
    return ma


# ── launchd ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
def tao_plist(python: str, tep: Path) -> bytes:
    return plistlib.dumps({
        "Label": NHAN_LAUNCHD,
        "ProgramArguments": [python, str(tep), "--chay-nen"],
        "StartInterval": CHU_KY_GIAY,
        "RunAtLoad": True,
        "StandardOutPath": os.devnull,
        "StandardErrorPath": os.devnull,
        "ProcessType": "Background",
    })


def cai_launchd(ap_dung: bool, go: bool) -> int:
    if sys.platform != "darwin":
        print("⚪ --cai-launchd chỉ cho macOS (công cụ chỉ canh được Kaspersky VPN trên Mac).")
        return 3
    duong = Path.home() / "Library" / "LaunchAgents" / f"{NHAN_LAUNCHD}.plist"
    lay_uid = getattr(os, "getuid", None)   # API chỉ-POSIX (CLAUDE.md §0.9)
    if lay_uid is None:
        print("⚪ Không lấy được uid người dùng — không cài launchd.")
        return 3
    dich = f"gui/{lay_uid()}"
    if go:
        print(f"{'GỠ' if ap_dung else 'CHẠY KHÔ gỡ'}: launchctl bootout {dich}/{NHAN_LAUNCHD} + bỏ {duong}")
        if ap_dung:
            subprocess.run(["launchctl", "bootout", f"{dich}/{NHAN_LAUNCHD}"], capture_output=True)
            duong.unlink(missing_ok=True)
        else:
            print("(chạy khô — thêm --ap-dung để gỡ thật)")
        return 0
    noi_dung = tao_plist(sys.executable, BAN_CAI)
    print(f"{'CÀI' if ap_dung else 'CHẠY KHÔ cài'} agent nền {NHAN_LAUNCHD} (mỗi {CHU_KY_GIAY} giây): đo mạng/VPN, thông báo khi mất "
          "mạng, tự thử nối lại VPN (≤ 2 lần/sự cố); không xoá gì, không đổi cấu hình mạng.")
    print(f"  tệp: {duong}\n  python: {sys.executable}\n  bản chạy (chép từ repo, ngoài OneDrive): {BAN_CAI}\n  state: {THU_MUC}")
    if not ap_dung:
        print("(chạy khô — thêm --ap-dung để cài; gỡ: --go-launchd --ap-dung)")
        return 0
    THU_MUC.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__).resolve(), BAN_CAI)
    duong.parent.mkdir(parents=True, exist_ok=True)
    duong.write_bytes(noi_dung)
    subprocess.run(["launchctl", "bootout", f"{dich}/{NHAN_LAUNCHD}"], capture_output=True)
    r = subprocess.run(["launchctl", "bootstrap", dich, str(duong)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(f"✗ launchctl bootstrap lỗi (mã {r.returncode}): {(r.stderr or '').strip()[:200]}")
        return 2
    print(f"✓ Đã cài và nạp. Kiểm: launchctl print {dich}/{NHAN_LAUNCHD} · thống kê: python3 tools/canh_mang_vpn.py --bao-cao")
    return 0


def main(argv: list | None = None) -> int:
    for luong in (sys.stdout, sys.stderr):
        try:
            if "utf" not in (getattr(luong, "encoding", "") or "").lower() and hasattr(luong, "reconfigure"):
                luong.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Canh mạng + VPN (đo, báo, tự thử nối lại VPN khi mất mạng)")
    ap.add_argument("--chay-nen", action="store_true", help="một nhịp của agent nền (launchd)")
    ap.add_argument("--doc", action="store_true", help="hook SessionStart: đọc kết quả nền, báo khi có chuyện")
    ap.add_argument("--im-khi-on", action="store_true", help="với --doc: im lặng khi ổn")
    ap.add_argument("--do-nguon-nen", action="store_true", help="với --doc: máy chủ VPN đổi ⇒ đo lại nguồn chứng cứ ở nền")
    ap.add_argument("--bao-cao", action="store_true", help="thống kê mất mạng / VPN tắt / đổi máy chủ")
    ap.add_argument("--ngay", type=int, default=7, help="với --bao-cao: số ngày (mặc định 7)")
    ap.add_argument("--tam-dung", type=int, metavar="PHUT", help="ngừng nhắc + tự nối lại trong PHUT phút")
    ap.add_argument("--tiep-tuc", action="store_true", help="bỏ tạm dừng")
    ap.add_argument("--cai-launchd", action="store_true", help="in/cài agent launchd chạy mỗi phút (macOS)")
    ap.add_argument("--go-launchd", action="store_true", help="in/gỡ agent launchd")
    ap.add_argument("--ap-dung", action="store_true", help="với --cai-launchd/--go-launchd: làm thật (mặc định chạy khô)")
    a = ap.parse_args(argv)
    if a.cai_launchd or a.go_launchd:
        return cai_launchd(a.ap_dung, a.go_launchd)
    if a.chay_nen:
        return chay_nen()
    if a.tam_dung is not None or a.tiep_tuc:
        den = 0.0 if a.tiep_tuc else time.time() + max(0, a.tam_dung) * 60
        ghi_json({"den": den}, TEP_TAM_DUNG)
        print("▶ Đã bỏ tạm dừng — cảm biến nhắc và tự nối lại như thường." if a.tiep_tuc else
              f"⏸ Tạm dừng nhắc + tự nối lại tới {_gio(den)} (vẫn ghi sự cố). Bỏ sớm: --tiep-tuc")
        return 0
    if a.bao_cao:
        print(bao_cao(a.ngay))
        return 0
    if a.doc:
        return doc_cho_phien(a.im_khi_on, a.do_nguon_nen)
    do = do_mang()
    muc, ly_do = phan_loai(do)
    if muc != "KHONG_DO":
        print(f"{BIEU[muc]} MẠNG {_gio(do['t'])}: {ly_do} · VPN: {do.get('vpn') or 'không rõ'} · máy chủ "
              f"#{do.get('may_chu') or '—'} · Wi-Fi/mạng dây: {', '.join(do.get('vat_ly') or []) or 'không có'}")
    else:
        print(f"⚪ MẠNG: không đo được — {ly_do}")
    return MA_THOAT[muc]


if __name__ == "__main__":
    sys.exit(main())
