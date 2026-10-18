#!/usr/bin/env python3
"""Thu số đo cho trang «Đài hoàn thiện EBM» (15/10/2026) — MỘT lệnh, 0 agent.

Vì sao có: bác sĩ cần MỘT trang theo dõi việc hoàn thiện hệ nghiên cứu G0–G10 SONG SONG với mảng cập nhật chứng cứ
lâm sàng, và muốn tốn ít token nhất. Mỗi lần làm mới trang mà Claude tự chạy chục lệnh rồi đọc từng đầu ra thì tốn
token; công cụ này gom các lệnh đo SẴN CÓ (không lệnh nào gọi agent) thành vài tệp JSON gọn để tải thẳng lên trang.

Chỉ ĐO và GHI tệp vào `state/dai-hoan-thien/` (ngoài git). Không đổi dashboard, sổ cái, cờ hay chữ ký; không đọc khoá.
Đo không được ⇒ trạng thái `khong_do` (không bao giờ coi là «đạt»).

Nguồn từng tệp:
  thuoc_do.json      — bảng thước đo «hoàn thiện» hai mảng + nền hệ thống
  cong_c1a.json      — `hoi_dong_cong.py trach-nhiem --gate ALL --json` (đề tài thật)
  viec.json          — `tu_de_xuat_viec.py --json` (việc treo, gắn mảng)
  chu_de_cu.json     — `kiem_do_tuoi_chung_cu.lau_chua_xem_lai()` (tuổi từng chủ đề)
  lo_trinh.json      — lộ trình: `lo_trinh_vao.json` trong thư mục ghi (đổi trạng thái KHÔNG cần PR); vắng/hỏng ⇒ hằng
                       LO_TRINH dưới đây (bản khởi tạo)
  chi_phi_token.json — chi phí token đã ĐO (hằng số CHI_PHI_TOKEN, mỗi dòng ghi nguồn)
  tien_do.json       — nhật ký việc đã hoàn thiện (`--ghi-tien-do`), mới nhất trước, kèm hạn mức 5 giờ lúc ghi
  han_muc.json       — hạn mức gói Claude (5 giờ · tuần) từ `han_muc_vao.json` do Claude chép từ thẻ usage của app;
                       vắng/hỏng ⇒ một dòng `khong_do` (máy không tự đọc được hạn mức tài khoản)

Theo dõi tiến độ (15/10/2026, bác sĩ: «khi hoàn thiện tự cập nhật để theo dõi tiến độ, đảm bảo tiến độ với mức token
và hạn mức»): mỗi việc xong ghi MỘT dòng bằng `--ghi-tien-do "<mảng>|<việc>|<kết quả>"`; lệnh in danh sách tệp ĐỔI so
với lần trước để chỉ tải lại đúng các tệp đó.

Lệnh:  python3 tools/do_dai_hoan_thien.py [--goc <thư mục Claude AI>] [--ra <thư mục>] [--study <mã>]
              [--ghi-tien-do "<mảng>|<việc>|<kết quả>"]
Mã thoát: 0 đã ghi (kể cả khi có thước đo không đo được) · 2 không ghi được.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Tuple, Any, Dict, List, Optional

for _luong in (sys.stdout, sys.stderr):
    try:
        _luong.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

GOC_MAC_DINH = Path(__file__).resolve().parents[1]
STUDY_MAC_DINH = "hai-long-benh-nhan-C1a-BVQY175"
NGUONG_TUOI = 120  # ngưỡng báo động của kiem_do_tuoi_chung_cu (ngày)
NHANH_Y_KHOA = "feat/r1-1-2-design-gap-remediation"
REPO_GOC = "drluanbv175/EBM-drluanbv175"
REPO_Y_KHOA = "drluanbv175/medical-ebm-automation"
CONG_CUNG = ("G2", "G4", "G5", "G8", "G9", "G10")  # đối chiếu gate_contract._GATE_REQUIRED_STAKEHOLDERS
TEN_CONG = {"G0": "Câu hỏi & khả thi", "G1": "Thiết kế & đề cương", "G2": "Đạo đức & đăng ký",
            "G3": "Cỡ mẫu & biến số", "G4": "Kế hoạch phân tích", "G5": "Thu thập & khoá dữ liệu",
            "G6": "Phân tích & diễn giải", "G7": "Bản thảo", "G8": "Bình duyệt", "G9": "Liêm chính tác giả",
            "G10": "Gói phát hành"}
NHAN_KET_LUAN = {"DAT_TIEU_CHI": "Đạt tiêu chí", "AGENT_XONG_CHO_NGUOI": "Agent xong, chờ người",
                 "AGENT_CON_VIEC": "Agent còn việc", "CHO_CONG_TRUOC": "Chờ cổng trước"}
# «cho» (17/10/2026, bác sĩ chọn): việc CHƯA TỚI LƯỢT vì cổng trước chưa xong — không phải «đạt», cũng không phải lỗi.
NHAN_TRANG_THAI = {"dat": "Đạt", "chua": "Chưa đạt", "khong_do": "Không đo được", "cho": "Chờ cổng trước"}
# Ngưỡng hạn mức (phần trăm đã dùng) — quá ngưỡng thì hoãn việc nặng tới khi cửa sổ đặt lại.
NGUONG_HAN_MUC = {"5 giờ": (85, 95), "tuần": (80, 92)}  # (hoãn việc nặng, dừng hẳn)
_CI_DANG_CHAY = ("in_progress", "queued", "pending", "waiting", "requested")  # chưa có kết luận


def chon_luot_ci(luot: List[Dict[str, Any]]) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """(lượt CI của repo mới nhất, lượt ĐÃ XONG mới nhất) — 17/10/2026: bỏ job tự động của GitHub/Dependabot
    (`event` = «dynamic»: «Dependabot Updates», «Graph Update»…) và lượt «cancelled» (bị lượt mới hơn thay chỗ). Trước
    đây đo `--limit 1` mọi workflow ⇒ một job cập nhật Dependabot hỏng biến thước đo CI nhánh chính thành «failure» giả."""
    that = [r for r in luot if r.get("event") != "dynamic" and r.get("conclusion") != "cancelled"]
    xong = next((r for r in that if r.get("status") == "completed"), None)
    return (that[0] if that else None), xong
_KY_CUNG = re.compile(r"^(PASS|LOCKED|APPROVED|RELEASED)|_LOCKED$")

# Lộ trình đã trình bác sĩ 15/10/2026; `trang_thai` sửa tay khi một giai đoạn đổi trạng thái.
LO_TRINH: List[Dict[str, str]] = [
    {"ma": "R1", "mang": "Nghiên cứu", "giai_doan": "Khép việc đang mở: lắp lại G10, A12 phủ cả bản nộp, PI ký G10",
     "thoi_gian": "Tuần 15–22/10/2026", "chu": "🤖 + 👤", "dich": "G10 có chữ ký; hồ sơ nộp Hội đồng sẵn sàng",
     "trang_thai": "Đang làm"},
    {"ma": "R2", "mang": "Nghiên cứu", "giai_doan": "Diễn tập G5–G10 bằng đề tài mô phỏng (synthetic_test)",
     "thoi_gian": "Song song khi chờ Hội đồng", "chu": "🤖",
     "dich": "Đề tài mô phỏng tới G10 READY; 0 nhiệm vụ chất lượng chưa bảo đảm", "trang_thai": "Chờ bác sĩ duyệt"},
    {"ma": "R3", "mang": "Nghiên cứu", "giai_doan": "C1a qua G2–G4 thật: nộp Hội đồng, pha phát triển công cụ, khoá SAP",
     "thoi_gian": "12/2026–04/2027", "chu": "👤 + 🤖", "dich": "G2 và G4 có chữ ký", "trang_thai": "Chưa bắt đầu"},
    {"ma": "R4", "mang": "Nghiên cứu", "giai_doan": "C1a qua G5–G10 thật: thu thập → phân tích → bản thảo → phát hành",
     "thoi_gian": "05/2027–12/2028", "chu": "👤 + 🤖", "dich": "Gói G10 phát hành có chữ ký",
     "trang_thai": "Chưa bắt đầu"},
    {"ma": "E1", "mang": "Chứng cứ lâm sàng", "giai_doan": "Trả nợ toàn văn các mục «Áp dụng ngay»",
     "thoi_gian": "Trước 03/11/2026", "chu": "👤 + 🤖", "dich": "Sổ nợ toàn văn bằng 0", "trang_thai": "Đang làm"},
    {"ma": "E2", "mang": "Chứng cứ lâm sàng", "giai_doan": "Quyết thẻ gói tuần trong 7 ngày (một câu «duyệt W…»)",
     "thoi_gian": "Hằng tuần", "chu": "👤", "dich": "Không thẻ nào chờ quá 7 ngày", "trang_thai": "Đang làm"},
    {"ma": "E3", "mang": "Chứng cứ lâm sàng", "giai_doan": "Làm mới 3 chủ đề cũ nhất mỗi tuần (máy quét → phiên bác sĩ)",
     "thoi_gian": "Hằng tuần", "chu": "🤖 → 👤", "dich": "Không chủ đề nào quá ngưỡng báo động",
     "trang_thai": "Đang làm"},
    {"ma": "E4", "mang": "Chứng cứ lâm sàng", "giai_doan": "Đặt cạnh mục «Áp dụng» với tổng hợp mới hơn — ưu tiên guideline mới",
     "thoi_gian": "Theo nhịp E3", "chu": "👤", "dich": "Mục chưa so giảm dần đều", "trang_thai": "Đang làm"},
    {"ma": "E5", "mang": "Chứng cứ lâm sàng", "giai_doan": "Gỡ chặn nguồn: NCBI, Semantic Scholar; đo lại sản lượng giám sát",
     "thoi_gian": "Khi đường mạng cho phép", "chu": "👤 + 🤖", "dich": "Sản lượng giám sát đo được cho mọi chủ đề",
     "trang_thai": "Đang chặn"},
    {"ma": "F1", "mang": "Nền hệ thống", "giai_doan": "Khoá Ed25519 cho các vai; chọn thống kê viên và người phản biện độc lập",
     "thoi_gian": "Trước G4 thật", "chu": "👤", "dich": "Chữ ký cổng chứng minh được người ký độc lập",
     "trang_thai": "Chưa bắt đầu"},
    {"ma": "F2", "mang": "Nền hệ thống", "giai_doan": "Tải skill mới lên claude.ai; đồng bộ máy Windows",
     "thoi_gian": "Khi tiện", "chu": "👤", "dich": "Cowork, claude.ai và Windows chạy bản mới nhất",
     "trang_thai": "Chưa bắt đầu"},
]

# Chi phí token ĐÃ ĐO — mỗi dòng ghi nguồn đo; không ước đoán thêm.
CHI_PHI_TOKEN: List[Dict[str, Any]] = [
    {"cach_lam": "Lệnh đo 0 agent (trang này, trach-nhiem, tieu_chuan, study_readiness)", "token": 0,
     "nguon": "Không gọi agent; phiên chính chỉ đọc tệp JSON gọn", "khi_dung": "Mặc định, mọi lần kiểm"},
    {"cach_lam": "Một agent đơn (trung bình)", "token": 380000,
     "nguon": "Đo 07/10/2026 (bộ nhớ: không tự mở workflow)", "khi_dung": "Việc lẻ cần chuyên trách"},
    {"cach_lam": "Một agent thẩm định độc lập (tham-dinh-dau-ra)", "token": 490000,
     "nguon": "Đo 15/10/2026, thẩm định đề cương nộp Hội đồng", "khi_dung": "Đầu ra trình người hoặc nộp ngoài"},
    {"cach_lam": "Workflow 6 agent", "token": 3000000,
     "nguon": "CLAUDE.md §0.6", "khi_dung": "Chỉ khi bác sĩ yêu cầu"},
    {"cach_lam": "Chạy lại (resume) workflow song song", "token": 3650000,
     "nguon": "Đo 07/10/2026 — resume gần như chạy lại hết", "khi_dung": "Tránh; đọc journal làm tay"},
    {"cach_lam": "Hội đồng một cổng (4 nhiệm vụ)", "token": 6000000,
     "nguon": "Đo 07/10/2026, họp thí điểm G0 C1a", "khi_dung": "Chỉ khi uoc-tinh báo đáng họp và bác sĩ đồng ý"},
]


def _python_venv() -> str:
    """Python của venv ~/.ebm-venv (đủ thư viện cho repo y khoa); thiếu thì dùng chính trình đang chạy."""
    for p in (Path.home() / ".ebm-venv" / "bin" / "python", Path.home() / ".ebm-venv" / "Scripts" / "python.exe"):
        if p.exists():
            return str(p)
    return sys.executable


def _chay(cmd: List[str], cwd: Path, giay: int = 300) -> Optional[str]:
    """Chạy một lệnh đo, trả stdout; lỗi khởi chạy/quá giờ ⇒ None (KHÔNG ĐO ĐƯỢC). Mã thoát khác 0 vẫn trả stdout."""
    try:
        r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=giay)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return r.stdout


def _json(text: Optional[str]) -> Any:
    try:
        return json.loads(text) if text else None
    except ValueError:
        return None


def _dong(mang: str, ma: str, thuoc_do: str, hien_tai: str, so: Optional[float], dich: str,
          trang_thai: str, lenh: str) -> Dict[str, Any]:
    return {"mang": mang, "ma": ma, "thuoc_do": thuoc_do, "hien_tai": hien_tai, "so": so, "dich": dich,
            "trang_thai": trang_thai, "nhan": NHAN_TRANG_THAI[trang_thai], "lenh": lenh}


def do_cong(y_khoa: Path, study: str) -> List[Dict[str, Any]]:
    """Một dòng mỗi cổng G0–G10 của đề tài thật, từ bảng trách nhiệm chấm sống."""
    d = _json(_chay([_python_venv(), "tools/hoi_dong_cong.py", "trach-nhiem", "--study", study,
                     "--gate", "ALL", "--json"], y_khoa))
    hang: List[Dict[str, Any]] = []
    for c in (d or {}).get("cong") or []:
        ap = [n for n in c.get("nhiem_vu") or [] if n.get("ap_dung")]
        hieu_luc = sum(1 for n in ap if (n.get("danh_gia_cheo") or {}).get("trang_thai") == "qua")
        hang.append({
            "cong": c.get("gate"), "ten": TEN_CONG.get(c.get("gate"), ""), "cong_cung": c.get("gate") in CONG_CUNG,
            "dieu_phoi": c.get("dieu_phoi"), "trang_thai_song": c.get("trang_thai_song"),
            "ket_luan": c.get("ket_luan"), "ket_luan_nhan": NHAN_KET_LUAN.get(c.get("ket_luan"), c.get("ket_luan")), "tieu_chi_dat": c.get("so_dat"), "tieu_chi": c.get("so_tieu_chi"),
            "agent_con_viec": len(c.get("agent_con_viec") or []), "cho_nguoi": len(c.get("cho_nguoi") or []),
            "cho_cong_truoc": len(c.get("cho_cong_truoc") or []), "nhiem_vu_ap_dung": len(ap),
            "danh_gia_cheo_hieu_luc": hieu_luc,
            "chat_luong_chua_bao_dam": len(c.get("chat_luong_chua_bao_dam") or []),
            # Bản công cụ y khoa trước 17/10/2026 chưa có khoá này ⇒ None (không đo được), KHÔNG coi là 0.
            "chat_luong_chua_toi_luot": ([m.get("ma") for m in c["chat_luong_chua_toi_luot"]]
                                         if isinstance(c.get("chat_luong_chua_toi_luot"), list) else None),
        })
    return hang


def do_viec(goc: Path) -> List[Dict[str, Any]]:
    """Việc treo của toàn hệ (tu_de_xuat_viec), gắn mảng theo nội dung."""
    with tempfile.TemporaryDirectory() as tam:
        ra = Path(tam) / "viec.json"
        _chay([sys.executable, "tools/tu_de_xuat_viec.py", "--gon", "--json", str(ra)], goc, giay=600)
        d = _json(ra.read_text(encoding="utf-8")) if ra.exists() else None
    hang = []
    for v in (d or {}).get("viec") or []:
        chu = v.get("viec") or ""
        if re.search(r"C1a|cổng|đề tài|IRB|\bG\d", chu):
            mang = "Nghiên cứu"
        elif re.search(r"chứng cứ|toàn văn|apply|Áp dụng|thẻ gói|nguồn|điểm-khám|RAG|xác minh|watchlist", chu,
                       re.IGNORECASE):
            mang = "Chứng cứ lâm sàng"
        else:
            mang = "Nền hệ thống"
        hang.append({"ma": f"V{len(hang) + 1:02d}", "uu_tien": v.get("uu"), "ai_lam": "Bác sĩ" if v.get("ai") == "👤" else "Máy",
                     "mang": mang, "viec": chu, "lenh": v.get("lenh") or ""})
    return hang


def do_tuoi(goc: Path) -> List[Dict[str, Any]]:
    """Tuổi (ngày) của từng chủ đề chứng cứ kể từ bản mới nhất; bản tin gộp đánh dấu riêng."""
    sys.path.insert(0, str(goc / "tools"))
    try:
        import kiem_do_tuoi_chung_cu as K  # noqa: E402
        lau = K.lau_chua_xem_lai()
        khong_can = K.doc_khong_can()
        return [{"chu_de": lc, "ngay": n, "ban_tin_gop": bool(K.la_khong_can(lc, khong_can))} for lc, n in lau]
    except Exception:  # công cụ hỏng/vắng dữ liệu ⇒ không đo được, không bịa
        return []
    finally:
        sys.path.remove(str(goc / "tools"))


def _so_trong(viec: List[Dict[str, Any]], mau: str) -> Optional[int]:
    """Lấy một con số từ dòng việc khớp mẫu (bảng việc là nguồn duy nhất của số đó); không khớp ⇒ None."""
    for v in viec:
        m = re.search(mau, v["viec"])
        if m:
            return int(m.group(1))
    return None


def _gh(args: List[str], goc: Path) -> Any:
    return _json(_chay(["gh", *args], goc, giay=60))


def thuoc_do(goc: Path, y_khoa: Path, cong: List[Dict[str, Any]], viec: List[Dict[str, Any]],
             tuoi: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Bảng thước đo «hoàn thiện»: mỗi dòng có hiện tại, đích, trạng thái dat/chua/khong_do và lệnh đo lại."""
    NC, CC, NEN = "Nghiên cứu", "Chứng cứ lâm sàng", "Nền hệ thống"
    hang: List[Dict[str, Any]] = []
    # --- Nghiên cứu ---
    cung = [c for c in cong if c["cong"] in CONG_CUNG]
    if cung:
        ky = sum(1 for c in cung if _KY_CUNG.search(c["trang_thai_song"] or ""))
        hang.append(_dong(NC, "R-KY", "Cổng cứng của đề tài thật có chữ ký", f"{ky}/{len(cung)}", ky,
                          f"{len(cung)}/{len(cung)}", "dat" if ky == len(cung) else "chua",
                          "python3 tools/study_readiness.py --study <mã>"))
        con = [c["cong"] for c in cong if c["ket_luan"] == "AGENT_CON_VIEC"]
        hang.append(_dong(NC, "R-AGENT", "Cổng còn việc của agent", ", ".join(con) or "0", len(con), "0",
                          "chua" if con else "dat", "hoi_dong_cong.py trach-nhiem --gate ALL"))
        clcb = sum(c["chat_luong_chua_bao_dam"] for c in cong)
        hang.append(_dong(NC, "R-CL", "Nhiệm vụ có chất lượng chưa bảo đảm", str(clcb), clcb, "0",
                          "chua" if clcb else "dat", "hoi_dong_cong.py trach-nhiem --gate ALL"))
        # 17/10/2026 (bác sĩ chọn «tách dòng chưa tới lượt»): nhiệm vụ chưa có đầu ra (vd diễn giải cần dữ liệu thật)
        # không chấm chéo được — dòng riêng, trạng thái «cho», không gộp vào R-CL và không bao giờ là «đạt» khi còn.
        tl = [c.get("chat_luong_chua_toi_luot") for c in cong]
        if any(x is None for x in tl):
            hang.append(_dong(NC, "R-CL-CHO", "Nhiệm vụ chưa tới lượt đánh giá chéo (chưa có đầu ra)",
                              "không đo được", None, "—", "khong_do", "hoi_dong_cong.py trach-nhiem --gate ALL"))
        else:
            ma_tl = [m for x in tl for m in x]
            hang.append(_dong(NC, "R-CL-CHO", "Nhiệm vụ chưa tới lượt đánh giá chéo (chưa có đầu ra)",
                              ", ".join(ma_tl) or "0", len(ma_tl), "0 khi cổng trước xong",
                              "cho" if ma_tl else "dat", "hoi_dong_cong.py trach-nhiem --gate ALL"))
    else:
        hang.append(_dong(NC, "R-KY", "Cổng của đề tài thật", "không đo được", None, "—", "khong_do",
                          "hoi_dong_cong.py trach-nhiem --gate ALL"))
    tc = _json(_chay([_python_venv(), "tools/tieu_chuan_hoan_thien.py", "--json"], y_khoa))
    tong = (tc or {}).get("tong") or {}
    if tong:
        a, ad, p, pd = tong.get("agent"), tong.get("agent_dat"), tong.get("dieu_phoi"), tong.get("dieu_phoi_dat")
        ok = a == ad and p == pd
        hang.append(_dong(NC, "R-CHUAN", "Agent và điều phối đạt chuẩn hoàn thiện", f"{ad}/{a} · {pd}/{p}",
                          (ad or 0) + (pd or 0), f"{a}/{a} · {p}/{p}", "dat" if ok else "chua",
                          "tieu_chuan_hoan_thien.py"))
    else:
        hang.append(_dong(NC, "R-CHUAN", "Agent và điều phối đạt chuẩn hoàn thiện", "không đo được", None, "—",
                          "khong_do", "tieu_chuan_hoan_thien.py"))
    # --- Chứng cứ lâm sàng ---
    chu_de = [t for t in tuoi if not t["ban_tin_gop"]]
    if tuoi:
        tv = statistics.median(t["ngay"] for t in tuoi)
        hang.append(_dong(CC, "E-TUOI", "Trung vị tuổi chủ đề (ngày)", f"{tv:g}", tv, f"≤ {NGUONG_TUOI}",
                          "dat" if tv <= NGUONG_TUOI else "chua", "kiem_do_tuoi_chung_cu.py"))
        qua = sum(1 for t in chu_de if t["ngay"] > NGUONG_TUOI)
        hang.append(_dong(CC, "E-QUA", f"Chủ đề quá {NGUONG_TUOI} ngày chưa xem lại", str(qua), qua, "0",
                          "chua" if qua else "dat", "ops/orchestrator.py --cu-nhat 3 --online"))
    else:
        hang.append(_dong(CC, "E-TUOI", "Tuổi chủ đề", "không đo được", None, "—", "khong_do",
                          "kiem_do_tuoi_chung_cu.py"))
    tv_json = _json(_chay([sys.executable, "tools/so_toan_van.py", "--json"], goc))
    if tv_json:
        no = len(tv_json.get("chua_doc_apply") or [])
        hang.append(_dong(CC, "E-TV", "Mục «Áp dụng ngay» còn nợ toàn văn", f"{no} (hạn {tv_json.get('han')})", no,
                          "0", "chua" if no else "dat", "so_toan_van.py"))
    else:
        hang.append(_dong(CC, "E-TV", "Mục «Áp dụng ngay» còn nợ toàn văn", "không đo được", None, "0", "khong_do",
                          "so_toan_van.py"))
    for ma, ten, mau, lenh in (
        ("E-MOI", "Mục «Áp dụng» có tổng hợp mới hơn, chờ so", r"(\d+) mục 'apply' có nguồn tổng hợp MỚI HƠN",
         "kiem_chung_cu_vuot_qua.py"),
        ("E-THE", "Thẻ gói tuần chưa quyết", r"(\d+)/\d+ thẻ gói \S+ chưa ghi quyết định", "ghi_duyet_the_tuan.py"),
        ("E-NGOAI", "Câu hỏi điểm khám ngoài giám sát", r"(\d+) lượt điểm-khám NGOÀI giám sát",
         "state/cau-hoi-chua-giam-sat.jsonl"),
    ):
        if not viec:  # bảng việc không đo được ⇒ không suy ra «0»
            hang.append(_dong(CC, ma, ten, "không đo được", None, "0", "khong_do", lenh))
            continue
        # Bảng việc chỉ liệt kê điều đang treo: không có dòng khớp ⇒ cảm biến không báo ⇒ 0.
        n = _so_trong(viec, mau) or 0
        if ma == "E-NGOAI":  # lượt ĐÃ rà mà còn chờ việc bác sĩ vẫn là câu chưa trả lời được — không đọc thành «đạt»
            n += _so_trong(viec, r"(\d+) câu điểm-khám ngoài giám sát ĐÃ RÀ") or 0
        hang.append(_dong(CC, ma, ten, str(n), n, "0", "chua" if n else "dat", lenh))
    sl = _json((goc / "state" / "san-luong-giam-sat-gan-nhat.json").read_text(encoding="utf-8")
               if (goc / "state" / "san-luong-giam-sat-gan-nhat.json").exists() else None)
    if sl and sl.get("chu_de") is not None:
        tong_cd, kd, mu = len(sl.get("chu_de") or []), len(sl.get("khong_do") or []), len(sl.get("mu") or [])
        tt = "khong_do" if kd == tong_cd and tong_cd else ("chua" if mu or kd else "dat")
        hang.append(_dong(CC, "E-SL", "Chủ đề đo được sản lượng giám sát",
                          f"{tong_cd - kd}/{tong_cd} (đo {str(sl.get('do_luc'))[:10]})", tong_cd - kd,
                          f"{tong_cd}/{tong_cd}", tt, "kiem_san_luong_giam_sat.py"))
    # --- Nền hệ thống ---
    chot = _json((goc / "state" / "chot-hoi-quy-gan-nhat.json").read_text(encoding="utf-8")
                 if (goc / "state" / "chot-hoi-quy-gan-nhat.json").exists() else None)
    if chot:
        tt = {"XANH": "dat", "DO": "chua"}.get(str(chot.get("trang_thai")), "khong_do")
        hang.append(_dong(NEN, "N-CHOT", "Chốt hồi quy bài học",
                          f"{chot.get('trang_thai')} (đo {str(chot.get('ket_thuc'))[:10]})", None, "XANH", tt,
                          "chot_hoi_quy_bai_hoc.py"))
    for ma, repo, nhanh in (("N-CI-GOC", REPO_GOC, "master"), ("N-CI-YK", REPO_Y_KHOA, NHANH_Y_KHOA)):
        r = _gh(["run", "list", "--repo", repo, "--branch", nhanh, "--limit", "20", "--json",
                 "conclusion,status,createdAt,event"], goc)
        moi, xong = chon_luot_ci(r) if isinstance(r, list) else (None, None)
        if moi:
            kl = moi.get("conclusion") or moi.get("status")
            them = (f" · lượt xong gần nhất: {xong.get('conclusion')} ({str(xong.get('createdAt'))[:10]})"
                    if kl in _CI_DANG_CHAY and xong else "")
            hang.append(_dong(NEN, ma, f"CI nhánh chính {'repo gốc' if repo == REPO_GOC else 'repo y khoa'}",
                              f"{kl} ({str(moi.get('createdAt'))[:10]}){them}", None, "success",
                              "dat" if kl == "success" else ("khong_do" if kl in _CI_DANG_CHAY else "chua"),
                              "gh run list"))
        else:
            hang.append(_dong(NEN, ma, "CI nhánh chính", "không đo được", None, "success", "khong_do",
                              "gh run list"))
    pr = tu_gop = 0
    pr_do = True
    for repo in (REPO_GOC, REPO_Y_KHOA):
        r = _gh(["pr", "list", "--repo", repo, "--state", "open", "--json", "number,autoMergeRequest"], goc)
        if r is None:
            pr_do = False
        else:
            # 17/10/2026: PR đã bật tự gộp sẽ tự gộp khi CI xanh — không còn «chờ bác sĩ».
            tu_gop += sum(1 for x in r if x.get("autoMergeRequest"))
            pr += sum(1 for x in r if not x.get("autoMergeRequest"))
    hang.append(_dong(NEN, "N-PR", "PR đang mở chờ bác sĩ",
                      (f"{pr}" + (f" (+{tu_gop} tự gộp khi CI xanh)" if tu_gop else "")) if pr_do else "không đo được",
                      pr if pr_do else None, "0", ("chua" if pr else "dat") if pr_do else "khong_do",
                      "gh pr list"))
    return hang


def _doc_json_tep(p: Path) -> Any:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def do_han_muc(ra: Path) -> List[Dict[str, Any]]:
    """Hạn mức gói Claude từ `han_muc_vao.json` (Claude chép từ thẻ usage của app: {do_luc, windows:[{label,
    percentUsed, resetsAt}]}). Mỗi cửa sổ một dòng kèm khuyến nghị theo NGUONG_HAN_MUC; vắng ⇒ dòng khong_do."""
    d = _doc_json_tep(ra / "han_muc_vao.json")
    hang: List[Dict[str, Any]] = []
    for w in (d or {}).get("windows") or []:
        nhan = str(w.get("label") or "")
        loai = "5 giờ" if "5-hour" in nhan or "5 giờ" in nhan else ("tuần" if "eekly" in nhan or "tuần" in nhan else None)
        pct = w.get("percentUsed")
        if loai is None or not isinstance(pct, (int, float)):
            continue
        hoan, dung = NGUONG_HAN_MUC[loai]
        tt = "dung" if pct >= dung else ("hoan_viec_nang" if pct >= hoan else "binh_thuong")
        hang.append({"cua_so": nhan, "loai": loai, "da_dung": pct, "dat_lai_luc": w.get("resetsAt"),
                     "nguong_hoan": hoan, "nguong_dung": dung, "trang_thai": tt,
                     "khuyen_nghi": {"dung": "Dừng, chờ cửa sổ đặt lại", "hoan_viec_nang": "Chỉ làm việc nhẹ, 0 agent",
                                     "binh_thuong": "Làm theo lộ trình"}[tt],
                     "do_luc": (d or {}).get("do_luc")})
    if not hang:
        hang.append({"cua_so": "Hạn mức gói Claude", "loai": "", "da_dung": None, "dat_lai_luc": None,
                     "nguong_hoan": None, "nguong_dung": None, "trang_thai": "khong_do",
                     "khuyen_nghi": "Chưa có số đo hạn mức — hỏi Claude «đo hạn mức»", "do_luc": None})
    return hang


def ghi_tien_do(ra: Path, dong: str, han_muc: List[Dict[str, Any]], luc: str) -> Dict[str, Any]:
    """Nối MỘT dòng việc đã xong vào nhật ký tien_do.jsonl (chỉ nối, không sửa dòng cũ)."""
    phan = [x.strip() for x in dong.split("|")]
    if len(phan) != 3 or not all(phan):
        raise ValueError("--ghi-tien-do cần đúng dạng «<mảng>|<việc>|<kết quả>»")
    h5 = next((h["da_dung"] for h in han_muc if h.get("loai") == "5 giờ"), None)
    rec = {"luc": luc, "mang": phan[0], "viec": phan[1], "ket_qua": phan[2], "han_muc_5h": h5}
    ra.mkdir(parents=True, exist_ok=True)
    with (ra / "tien_do.jsonl").open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def doc_tien_do(ra: Path) -> List[Dict[str, Any]]:
    """Nhật ký tiến độ, mới nhất trước; dòng hỏng bị bỏ qua (không chặn cả trang)."""
    hang = []
    try:
        dong = (ra / "tien_do.jsonl").read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    for i, x in enumerate(dong, 1):
        try:
            r = json.loads(x)
        except ValueError:
            continue
        if isinstance(r, dict):
            r["ma"] = f"T{i:03d}"
            hang.append(r)
    return list(reversed(hang))


_KHOA_LO_TRINH = ("ma", "mang", "giai_doan", "thoi_gian", "chu", "dich", "trang_thai")


def do_lo_trinh(ra: Path) -> List[Dict[str, Any]]:
    """Lộ trình từ `lo_trinh_vao.json` (danh sách dòng đủ khoá _KHOA_LO_TRINH, mã không trùng); tệp vắng, hỏng hoặc sai
    khuôn ⇒ hằng LO_TRINH — không bao giờ trả lộ trình rỗng/nửa vời."""
    d = _doc_json_tep(ra / "lo_trinh_vao.json")
    if (isinstance(d, list) and d and all(isinstance(r, dict) and all(isinstance(r.get(k), str) and r.get(k)
                                                                        for k in _KHOA_LO_TRINH) for r in d)
            and len({r["ma"] for r in d}) == len(d)):
        return [{k: r[k] for k in _KHOA_LO_TRINH} for r in d]
    return LO_TRINH


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Thu số đo cho trang Đài hoàn thiện EBM (0 agent).")
    ap.add_argument("--goc", type=Path, default=GOC_MAC_DINH, help="thư mục «Claude AI» (mặc định: repo chứa tệp này)")
    ap.add_argument("--ra", type=Path, default=None, help="thư mục ghi (mặc định <gốc>/state/dai-hoan-thien)")
    ap.add_argument("--study", default=STUDY_MAC_DINH)
    ap.add_argument("--ghi-tien-do", default=None, metavar="MẢNG|VIỆC|KẾT QUẢ",
                    help="nối một dòng việc đã hoàn thiện vào nhật ký tiến độ trước khi đo")
    a = ap.parse_args(argv)
    goc = a.goc.resolve()
    y_khoa = goc / "medical-ebm-automation"
    ra = (a.ra or goc / "state" / "dai-hoan-thien").resolve()
    luc = dt.datetime.now().astimezone().isoformat(timespec="seconds")

    han_muc = do_han_muc(ra)
    if a.ghi_tien_do:
        try:
            rec = ghi_tien_do(ra, a.ghi_tien_do, han_muc, luc)
        except (ValueError, OSError) as e:
            print(f"Không ghi được tiến độ: {e}", file=sys.stderr)
            return 2
        print(f"Đã ghi tiến độ: {rec['mang']} — {rec['viec']}")
    cong = do_cong(y_khoa, a.study) if y_khoa.is_dir() else []
    viec = do_viec(goc)
    tuoi = do_tuoi(goc)
    bo = {
        "thuoc_do": thuoc_do(goc, y_khoa, cong, viec, tuoi),
        "cong_c1a": cong,
        "viec": viec,
        "chu_de_cu": [t for t in tuoi if not t["ban_tin_gop"]],
        "lo_trinh": do_lo_trinh(ra),
        "chi_phi_token": CHI_PHI_TOKEN,
        "tien_do": doc_tien_do(ra),
        "han_muc": han_muc,
    }
    doi = []
    try:
        ra.mkdir(parents=True, exist_ok=True)
        for ten, hang in bo.items():
            cu = _doc_json_tep(ra / f"{ten}.json")
            if not isinstance(cu, dict) or cu.get("rows") != hang:
                doi.append(f"{ten}.json")
            (ra / f"{ten}.json").write_text(json.dumps({"do_luc": luc, "rows": hang}, ensure_ascii=False, indent=1),
                                            encoding="utf-8", newline="\n")
    except OSError as e:
        print(f"Không ghi được {ra}: {e}", file=sys.stderr)
        return 2
    td = bo["thuoc_do"]
    dem = {k: sum(1 for h in td if h["trang_thai"] == k) for k in ("dat", "chua", "khong_do", "cho")}
    print(f"Đài hoàn thiện — đo lúc {luc}: {dem['dat']} đạt · {dem['chua']} chưa · {dem['khong_do']} không đo được"
          + (f" · {dem['cho']} chờ cổng trước" if dem["cho"] else ""))
    print(f"  {len(cong)} cổng · {len(viec)} việc · {len(bo['chu_de_cu'])} chủ đề → {ra.as_posix()}")
    print("  Tệp đổi (cần tải lại lên trang): " + (", ".join(doi) if doi else "không có"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
