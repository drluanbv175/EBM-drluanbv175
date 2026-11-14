#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CANH LỊCH NỀN QUA EMAIL — bộ canh «người chết» báo lỗi lịch nền KHÔNG cần bác sĩ mở Claude (14/11/2026).

VÌ SAO CÓ
=========
Hai cảm biến lịch nền đã có — `tools/kiem_lich_nen.py` (kỳ lịch không để lại dấu vết) và `tools/quyen_lich_nen.py`
(lệnh của lượt lịch chưa được phép ⇒ lượt bị cắt ngang mà vẫn ghi «succeeded») — nhưng chỉ chạy ở hook SessionStart / hòm
việc: lượt lịch hỏng chỉ LỘ RA khi bác sĩ mở Claude. Đo 28/10/2026: gói tuần chết 4 lượt liền (19–23/10) và kỳ 26/10 lỡ
hẳn trước khi có người thấy. Công cụ này chạy MỘT LẦN MỖI NGÀY (launchd) và gửi MỘT email tóm tắt khi có lỗi đỏ.

LÀM GÌ
======
  1. Gọi THẲNG hàm `kiem()` của hai cảm biến (import, không đọc chuỗi in ra) — lỗi đỏ là:
       · kỳ lịch gần nhất lỡ hẳn/trễ (mục `uu ≤ 1` — đúng định nghĩa «hỏng» của kiem_lich_nen.main);
       · lệnh SKILL.md chưa khai ở `sync/quyen-lich-nen.json` hoặc máy chưa áp quy tắc (quyen_lich_nen).
  2. Có lỗi đỏ ⇒ gửi MỘT email qua kênh CÓ SẴN của repo y khoa: `medical-ebm-automation/app/services/notify.py::send_email`
     (cấu hình ENABLE_EMAIL_ALERTS/SMTP_*/ALERT_EMAIL_TO do `app/config.py` nạp từ kho secrets). Việc gửi chạy trong TIẾN
     TRÌNH CON bằng Python của venv engine (`~/.ebm-venv`, cần sqlalchemy…), log của engine bị TẮT trong tiến trình con
     (notify.py vốn ghi địa chỉ người nhận vào log), và tiến trình con chỉ trả về một dòng JSON gồm khoá trong danh sách
     trắng (trạng thái · lý do · TÊN khoá cấu hình còn thiếu · loại lỗi). Công cụ KHÔNG in, KHÔNG ghi log, KHÔNG ghi sổ bất
     kỳ GIÁ TRỊ cấu hình nào (máy chủ, tài khoản, mật khẩu, địa chỉ).
  3. Kênh email chưa bật / gửi lỗi ⇒ in «⚪ kênh email chưa bật» (hoặc loại lỗi) và mã 2 — KHÔNG BAO GIỜ giả là đã gửi,
     KHÔNG ghi sổ chống lặp (lượt sau thử lại).
  4. Chống gửi lặp: cùng NỘI DUNG cảnh báo (vân tay SHA-256 của danh sách lỗi đỏ đã sắp xếp) không gửi quá 1 lần/24 giờ.
     Sổ trạng thái `state/canh-lich-nen-email.json` (thư mục `state/` bị `.gitignore` loại — không vào git).
  5. `--cai-launchd`: CHẠY KHÔ in plist (mỗi ngày 09:00, kèm `--thong-bao`); `--ap-dung` mới cài; `--go-launchd` gỡ.
     Windows: chỉ in hướng dẫn Task Scheduler, không cài. Cài là việc của BÁC SĨ — agent không tự chạy `--ap-dung`.
  6. BỘ CANH TỰ HỎNG KHÔNG ĐƯỢC IM LẶNG (duyệt PR #338): dưới launchd mọi đầu ra vào /dev/null và launchd bỏ qua mã thoát.
       · `--thong-bao`: lượt nào mã 2 (cảnh báo KHÔNG tới email / không đo được) ⇒ thông báo hệ thống macOS (osascript,
         ≤ 1 lần/20 giờ) — chỉ NHÃN kết quả, không giá trị cấu hình. Đây là đường lùi duy nhất không cần mở Claude.
       · `--suc-khoe`: CHỈ ĐỌC sổ `lan_chay_cuoi` ⇒ 🟡 khi lượt cuối không tới kênh email, hoặc agent nền đã cài mà lượt
         cuối cũ hơn 48 giờ. Dành cho hòm việc/hook SessionStart đọc (nối dây ở PR sau — không sửa ở đây).

    python3 tools/canh_lich_nen_email.py                  # đo hai cảm biến; đỏ ⇒ gửi email (chống lặp 24 giờ)
    python3 tools/canh_lich_nen_email.py --xem-truoc      # in email SẼ gửi, không gửi, không ghi sổ
    python3 tools/canh_lich_nen_email.py --im-khi-on      # (launchd) im lặng khi 🟢
    python3 tools/canh_lich_nen_email.py --thong-bao      # thêm thông báo macOS khi cảnh báo không tới email (mã 2)
    python3 tools/canh_lich_nen_email.py --suc-khoe       # chỉ đọc sổ: bộ canh có đang làm việc không
    python3 tools/canh_lich_nen_email.py --cai-launchd    # chạy khô; thêm --ap-dung để cài (macOS)

Mã thoát: 0 = đo được cả hai cảm biến, không lỗi đỏ, kênh email sẵn sàng · 1 = có lỗi đỏ VÀ cảnh báo ĐÃ tới kênh email
(gửi ở lượt này, hoặc cùng nội dung đã gửi < 24 giờ) · 2 = ⚪ cảnh báo KHÔNG tới được hoặc không đo được (kênh email chưa
bật, gửi lỗi, không thấy repo y khoa, cảm biến không đo được) — không bao giờ là «ổn» · 3 = `--cai-launchd` trên nền tảng
không cài tự động được. Riêng `--xem-truoc` (không gửi gì): 0 không đỏ · 1 có đỏ · 2 không đo được trọn. Riêng
`--suc-khoe`: 0 bộ canh khoẻ · 1 🟡 cần xem · 3 ⚪ chưa cài agent nền (macOS) — `--im-khi-on` im lặng ở 0 và 3.

Ranh giới: CHỈ ĐO và BÁO — không tạo/xoá/chạy tác vụ lịch, không sửa `settings.local.json`, không đụng nội dung y khoa.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
import plistlib
import subprocess
import sys
import time
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parent.parent
THU_MUC_TOOLS = Path(__file__).resolve().parent
TEP_STATE = REPO / "state" / "canh-lich-nen-email.json"
NHAN_LAUNCHD = "vn.drluan.ebm-canh-lich-email"
GIO_CHAY, PHUT_CHAY = 9, 0            # mỗi ngày 09:00 — sau hạn 30 giờ của các kỳ 18:00–18:30 (sync/lich-nen-ky-vong.json)
KHOANG_CHONG_LAP_GIAY = 24 * 3600
GIU_SO_GIAY = 14 * 24 * 3600          # vân tay cũ hơn 14 ngày bị dọn khỏi sổ
TRAN_MUC_MOI_NHOM = 15                # email chỉ liệt kê ≤15 mục mỗi nhóm (vân tay vẫn tính đủ)
HAN_TIEN_TRINH_CON_GIAY = 120
DAU_KET_QUA = "@@KQ_CANH_LICH@@"      # tiền tố dòng JSON tiến trình con trả về (tách khỏi mọi dòng lạc khác)
# Lý do «skipped» của notify.send_email — chỉ chuyển tiếp đúng các giá trị này (danh sách trắng).
LY_DO_CHUA_BAT = {"email_not_configured", "missing_app_password"}
KHOA_CAU_HINH = ("ENABLE_EMAIL_ALERTS", "SMTP_HOST", "SMTP_FROM", "SMTP_PASSWORD", "ALERT_EMAIL_TO")
# Nhãn `lan_chay_cuoi.ket_qua` nghĩa là cảnh báo TỚI ĐƯỢC kênh email (hoặc không có gì để báo, kênh sẵn sàng). Mọi nhãn
# khác — kenh_chua_bat, kenh_khong_do_duoc, khong_thay_repo, khong_do_duoc, khong_gui_* — là bộ canh KHÔNG làm được việc.
KET_QUA_TOI_KENH = {"xanh", "da_gui", "da_gui_trong_24h"}
HAN_CU_GIAY = 48 * 3600               # lịch chạy mỗi ngày — quá 48 giờ không có lượt mới ⇒ agent nền không chạy
KHOANG_THONG_BAO_GIAY = 20 * 3600     # < 24 giờ để lượt hằng ngày nào cũng báo; lượt chạy tay dồn dập thì không


# ---------------------------------------------------------------------------------------------------------------------
# Nạp hai cảm biến bằng import (không parse chuỗi in)
# ---------------------------------------------------------------------------------------------------------------------
def _nap(ten: str):
    """Nạp `tools/<ten>.py` thành module riêng (không đụng sys.path, không đè module cùng tên của nơi gọi)."""
    spec = importlib.util.spec_from_file_location(f"_canh_lich_email_{ten}", THU_MUC_TOOLS / f"{ten}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _rut_goc(chuoi: str) -> str:
    """Thay đường dẫn tuyệt đối của repo bằng «<gốc-repo>»: email không mang tên thư mục người dùng, vân tay ổn định giữa
    các máy."""
    tuyet_doi = "//" + str(REPO).lstrip("/")
    return chuoi.replace(tuyet_doi, "<gốc-repo>").replace(str(REPO), "<gốc-repo>")


def do_lich(kiem_fn=None) -> dict:
    """Chạy cảm biến kỳ lịch. Trả {'do_duoc': bool, 'do': [lỗi đỏ], 'phu': [⚪]}. Cảm biến sập ⇒ không đo được (⚪)."""
    try:
        kq = (kiem_fn or _nap("kiem_lich_nen").kiem)()
    except Exception as e:  # noqa: BLE001 — cảm biến hỏng là ⚪ «không đo được», không phải đỏ giả, không sập cả công cụ
        return {"do_duoc": False, "do": [], "phu": [f"cảm biến kiem_lich_nen lỗi ({type(e).__name__}) — không đo được"]}
    phat_hien = list(kq.get("phat_hien", []))
    do = [("🔴 " if p.get("uu") == 0 else "🟠 ") + str(p.get("thong_diep", ""))
          for p in sorted(phat_hien, key=lambda x: (x.get("uu", 9), str(x.get("ky", ""))))
          if isinstance(p.get("uu"), int) and p["uu"] <= 1]
    phu = [str(x) for x in kq.get("khong_do_duoc", [])]
    # Đúng ngữ nghĩa của chính cảm biến: không tác vụ nào đo được và không phát hiện gì ⇒ ⚪ (BH08), không phải «đúng hẹn».
    do_duoc = bool(kq.get("ok", 0)) or bool(phat_hien)
    return {"do_duoc": do_duoc, "do": do, "phu": phu}


def do_quyen(kiem_fn=None) -> dict:
    """Chạy cảm biến quyền lượt lịch. Cùng dạng trả về với `do_lich`."""
    try:
        kq = (kiem_fn or _nap("quyen_lich_nen").kiem)()
    except Exception as e:  # noqa: BLE001 — như do_lich
        return {"do_duoc": False, "do": [], "phu": [f"cảm biến quyen_lich_nen lỗi ({type(e).__name__}) — không đo được"]}
    do = [f"🔴 {ten}: SKILL.md có lệnh chưa khai ở sync/quyen-lich-nen.json — {c}" for ten, c in kq.get("thieu_khai", [])]
    do += [f"🔴 máy chưa áp quy tắc: {_rut_goc(str(q))}" for q in kq.get("thieu_may", [])]
    phu = [str(x) for x in kq.get("khong_do", [])]
    # quyen_lich_nen.main trả 2 (⚪) khi có khong_do mà không thiếu gì — giữ đúng nghĩa đó.
    return {"do_duoc": bool(do) or not phu, "do": do, "phu": phu}


def van_tay(do: list[str]) -> str:
    """Vân tay NỘI DUNG cảnh báo: không phụ thuộc thứ tự, không mang mốc giờ chạy."""
    return hashlib.sha256("\n".join(sorted(do)).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------------------------------------------------
# Soạn email
# ---------------------------------------------------------------------------------------------------------------------
def _nhom(tieu_de: str, muc: list[str]) -> list[str]:
    if not muc:
        return []
    dong = [tieu_de] + [f"  • {x}" for x in muc[:TRAN_MUC_MOI_NHOM]]
    if len(muc) > TRAN_MUC_MOI_NHOM:
        dong.append(f"  … và {len(muc) - TRAN_MUC_MOI_NHOM} mục nữa (chạy python3 tools/quyen_lich_nen.py để xem đủ)")
    return dong + [""]


def soan_email(lich: dict, quyen: dict, bay_gio: dt.datetime) -> tuple[str, str]:
    """(tiêu đề, thân văn bản thuần). Không chứa giá trị cấu hình, không chứa tên máy/đường dẫn người dùng."""
    n = len(lich["do"]) + len(quyen["do"])
    tieu_de = f"[EBM] Lịch nền hỏng — {n} lỗi đỏ ({bay_gio:%d/%m/%Y})"
    dong = [f"CẢNH BÁO LỊCH NỀN EBM — {bay_gio:%d/%m/%Y %H:%M} (nền tảng {sys.platform})", "",
            f"Có {n} lỗi đỏ ở lịch nền — các lỗi này chỉ lộ khi mở Claude, nên bộ canh gửi email:", ""]
    dong += _nhom("[Lịch nền — kỳ không nổ đúng hẹn]", lich["do"])
    dong += _nhom("[Quyền lượt lịch — lệnh chưa được phép (lượt bị cắt ngang mà vẫn ghi «succeeded»)]", quyen["do"])
    dong += _nhom("[Không đo được — ⚪, không phải lỗi, cũng không phải «ổn»]", lich["phu"] + quyen["phu"])
    dong += ["Việc cần làm:"]
    if lich["do"]:
        dong.append("  • mở phiên Claude: list_scheduled_tasks + list_task_runs (tác vụ bị xoá/tắt?), rồi «Run now» để bù.")
    if quyen["do"]:
        dong.append("  • lệnh SKILL.md chưa khai: khai ở sync/quyen-lich-nen.json (bác sĩ duyệt); sau đó — hoặc khi chỉ là «máy "
                    "chưa áp quy tắc» — BÁC SĨ chạy python3 tools/quyen_lich_nen.py --ap-dung.")
    dong += ["", "Cùng nội dung chỉ gửi tối đa 1 lần/24 giờ. Công cụ: tools/canh_lich_nen_email.py (chỉ đo và báo; "
             "không tạo/xoá/chạy tác vụ lịch).", "Cần bác sĩ kiểm chứng."]
    return tieu_de, "\n".join(dong) + "\n"


# ---------------------------------------------------------------------------------------------------------------------
# Kênh email: tiến trình con gọi notify.send_email của repo y khoa
# ---------------------------------------------------------------------------------------------------------------------
def repo_y_khoa() -> Path | None:
    """Gốc repo y khoa: vị trí LỒNG/ANH EM (ban_sao_tran.duong_goc), rồi EBM_WORKSPACE_ROOT. None nếu không thấy."""
    try:
        p = _nap("ban_sao_tran").duong_goc("medical-ebm-automation", REPO)
    except Exception:  # noqa: BLE001 — thiếu tiện ích thì vẫn thử biến môi trường
        p = None
    if p is None and os.environ.get("EBM_WORKSPACE_ROOT"):
        ung_vien = Path(os.environ["EBM_WORKSPACE_ROOT"]) / "medical-ebm-automation"
        p = ung_vien if ung_vien.exists() else None
    if p is not None and (p / "app" / "services" / "notify.py").is_file():
        return p
    return None


def python_engine() -> str:
    """Python của venv engine (`~/.ebm-venv`, có sqlalchemy… mà notify.py cần); vắng thì dùng chính trình đang chạy."""
    goc = Path.home() / ".ebm-venv"
    for ung_vien in (goc / "bin" / "python", goc / "Scripts" / "python.exe"):
        if ung_vien.exists():
            return str(ung_vien)
    return sys.executable


def _dang_kiem_thu() -> bool:
    """Cùng tín hiệu với app/config._dang_kiem_thu của repo y khoa."""
    return "pytest" in sys.modules or "PYTEST_CURRENT_TEST" in os.environ


def _la_repo_that(mea: Path) -> bool:
    """`mea` có phải repo y khoa THẬT (vị trí lồng/anh em/EBM_WORKSPACE_ROOT) không — so trực tiếp, không qua
    `repo_y_khoa()` (test hay vá hàm đó)."""
    ung_vien = [REPO / "medical-ebm-automation", REPO.parent / "medical-ebm-automation"]
    if os.environ.get("EBM_WORKSPACE_ROOT"):
        ung_vien.append(Path(os.environ["EBM_WORKSPACE_ROOT"]) / "medical-ebm-automation")
    try:
        dich = mea.resolve()
        return any(dich == u.resolve() for u in ung_vien)
    except OSError:
        return True   # không phân giải được ⇒ coi như thật (an toàn)


def _loai_loi(chuoi: str) -> str:
    """Phân loại lỗi SMTP thành NHÃN cố định — chuỗi lỗi gốc có thể mang tên máy chủ/địa chỉ nên không bao giờ chuyển tiếp."""
    s = chuoi.lower()
    if "535" in s or "auth" in s or "username and password" in s:
        return "xac_thuc"
    if "timed out" in s or "timeout" in s:
        return "het_gio"
    if any(k in s for k in ("refused", "getaddrinfo", "name or service", "nodename", "unreachable", "network")):
        return "ket_noi"
    return "khac"


def chay_con(che_do: str, payload: dict, mea: Path, python: str | None = None) -> dict:
    """Chạy `che_do` ∈ {trang-thai, gui} trong tiến trình con. Chỉ trả khoá trong danh sách trắng."""
    if _dang_kiem_thu() and _la_repo_that(mea):
        # Phòng thủ chiều sâu: dưới pytest không bao giờ chạm kênh/cấu hình THẬT (CLAUDE.md y khoa: test không chạm secrets).
        return {"status": "skipped", "reason": "pytest_khong_goi_kenh_that"}
    lenh = [python or python_engine(), str(Path(__file__).resolve()), "--_con", che_do, "--_mea", str(mea)]
    try:
        r = subprocess.run(lenh, input=json.dumps(payload, ensure_ascii=False), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=HAN_TIEN_TRINH_CON_GIAY, cwd=str(mea))
    except subprocess.TimeoutExpired:
        return {"status": "error", "loai_loi": "het_gio_tien_trinh_con"}
    except OSError as e:
        return {"status": "error", "loai_loi": f"khong_chay_duoc_tien_trinh_con ({type(e).__name__})"}
    # stderr của tiến trình con KHÔNG được in (có thể chứa log engine) — chỉ đọc dòng JSON đánh dấu ở stdout.
    for dong in reversed((r.stdout or "").splitlines()):
        if dong.startswith(DAU_KET_QUA):
            try:
                d = json.loads(dong[len(DAU_KET_QUA):])
            except ValueError:
                break
            if not isinstance(d, dict):
                break
            sach = {k: d[k] for k in ("status", "reason", "bat", "thieu", "loai_loi", "module") if k in d}
            if "thieu" in sach:
                sach["thieu"] = [k for k in sach["thieu"] if k in KHOA_CAU_HINH]
            if sach.get("reason") not in LY_DO_CHUA_BAT:
                sach.pop("reason", None)
            return sach
    return {"status": "error", "loai_loi": f"tien_trinh_con_khong_tra_ket_qua (mã {r.returncode})"}


def _che_do_con(che_do: str, mea: str) -> int:
    """CHẠY TRONG TIẾN TRÌNH CON (venv engine). In DUY NHẤT một dòng `DAU_KET_QUA{json}` ra stdout."""
    import logging

    def tra(d: dict) -> int:
        print(DAU_KET_QUA + json.dumps(d, ensure_ascii=False))
        return 0

    # Tắt TOÀN BỘ logging của tiến trình con TRƯỚC khi import engine: notify.send_email ghi địa chỉ người nhận / chuỗi lỗi
    # SMTP vào log (console + data/archive/app.log) — bộ canh không được để lại giá trị cấu hình ở đâu cả.
    logging.disable(logging.CRITICAL)
    sys.path.insert(0, mea)
    try:
        from app.config import settings
    except Exception as e:  # noqa: BLE001
        return tra({"status": "khong_nap_duoc", "loai_loi": type(e).__name__, "module": getattr(e, "name", None)})
    # Chỉ TÊN khoá còn thiếu (chẩn đoán) — giá trị không rời tiến trình con. Cùng điều kiện với notify.send_email.
    thieu = [k for k in KHOA_CAU_HINH if not getattr(settings, k.lower(), None)]
    if che_do == "trang-thai":
        return tra({"bat": not thieu, "thieu": thieu})
    try:
        payload = json.loads(sys.stdin.read() or "{}")
        from app.services import notify
    except Exception as e:  # noqa: BLE001
        return tra({"status": "khong_nap_duoc", "loai_loi": type(e).__name__, "module": getattr(e, "name", None)})
    # Nguồn sự thật «đã cấu hình chưa» là CHÍNH notify.send_email (trả 'skipped' khi thiếu, không chạm mạng).
    kq = notify.send_email(str(payload.get("subject", "")), str(payload.get("body", "")))
    trang_thai = str(kq.get("status", "error"))
    ra: dict = {"status": trang_thai, "thieu": thieu}
    if trang_thai == "skipped":
        ra["reason"] = kq.get("reason")
    elif trang_thai == "error":
        ra["loai_loi"] = _loai_loi(str(kq.get("error", "")))
    return tra(ra)


# ---------------------------------------------------------------------------------------------------------------------
# Sổ chống lặp
# ---------------------------------------------------------------------------------------------------------------------
def doc_state(duong_dan: Path | None = None) -> dict:
    # Đọc TEP_STATE lúc GỌI (không chốt làm mặc định lúc import) — test vá TEP_STATE thì main() phải theo (bài học canh_dia).
    duong_dan = duong_dan or TEP_STATE
    try:
        d = json.loads(duong_dan.read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def ghi_state(d: dict, duong_dan: Path | None = None) -> None:
    duong_dan = duong_dan or TEP_STATE
    duong_dan.parent.mkdir(parents=True, exist_ok=True)
    tam = duong_dan.with_name(duong_dan.name + f".tmp{os.getpid()}")
    tam.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    os.replace(tam, duong_dan)


def lan_gui_gan(st: dict, vt: str, bay_gio: float) -> float | None:
    """Mốc (epoch) lần gửi cùng vân tay còn trong 24 giờ; None nếu được gửi lại."""
    da_gui = st.get("da_gui")
    luc = da_gui.get(vt) if isinstance(da_gui, dict) else None
    try:
        luc = float(luc)
    except (TypeError, ValueError):
        return None
    return luc if 0 <= bay_gio - luc < KHOANG_CHONG_LAP_GIAY else None


def ghi_da_gui(st: dict, vt: str, bay_gio: float) -> dict:
    """Ghi vân tay vừa gửi; dọn vân tay cũ hơn 14 ngày. Chỉ gọi khi notify trả 'sent'."""
    cu = st.get("da_gui") if isinstance(st.get("da_gui"), dict) else {}
    moi = {}
    for k, v in cu.items():
        try:
            if bay_gio - float(v) < GIU_SO_GIAY:
                moi[k] = float(v)
        except (TypeError, ValueError):
            continue
    moi[vt] = bay_gio
    return {**st, "da_gui": moi}


# ---------------------------------------------------------------------------------------------------------------------
# launchd (macOS) / Task Scheduler (Windows — chỉ hướng dẫn)
# ---------------------------------------------------------------------------------------------------------------------
def tao_plist(python: str, tep: Path) -> bytes:
    # Đầu ra vào /dev/null và launchd bỏ qua mã thoát ⇒ `--thong-bao` là đường duy nhất để bộ canh hỏng tự lộ ra.
    return plistlib.dumps({
        "Label": NHAN_LAUNCHD,
        "ProgramArguments": [python, str(tep), "--im-khi-on", "--thong-bao"],
        "StartCalendarInterval": {"Hour": GIO_CHAY, "Minute": PHUT_CHAY},
        "RunAtLoad": False,
        "StandardOutPath": os.devnull,
        "StandardErrorPath": os.devnull,
        "ProcessType": "Background",
    })


def cai_launchd(ap_dung: bool, go: bool) -> int:
    tep = Path(__file__).resolve()
    if sys.platform != "darwin":
        print("⚪ --cai-launchd chỉ cài tự động trên macOS. Windows: tự tạo tác vụ Task Scheduler (công cụ KHÔNG cài):")
        print(f'   schtasks /Create /SC DAILY /ST {GIO_CHAY:02d}:{PHUT_CHAY:02d} /TN "EBM canh lich nen email" '
              f'/TR "\\"{sys.executable}\\" \\"{tep}\\" --im-khi-on"')
        print("   (Windows không có --thong-bao: kiểm bộ canh bằng python tools/canh_lich_nen_email.py --suc-khoe)")
        print("   (hoặc Task Scheduler → Create Basic Task → Daily → Start a program: python + đường dẫn công cụ + --im-khi-on)")
        return 3
    duong = Path.home() / "Library" / "LaunchAgents" / f"{NHAN_LAUNCHD}.plist"
    lay_uid = getattr(os, "getuid", None)   # API chỉ-POSIX (CLAUDE.md §0.9)
    if lay_uid is None:
        print("⚪ Không lấy được uid người dùng (nền tảng không phải POSIX) — không cài launchd.")
        return 3
    dich = f"gui/{lay_uid()}"
    if go:
        print(f"{'GỠ' if ap_dung else 'CHẠY KHÔ gỡ'}: launchctl bootout {dich}/{NHAN_LAUNCHD} + xoá {duong}")
        if ap_dung:
            subprocess.run(["launchctl", "bootout", f"{dich}/{NHAN_LAUNCHD}"], capture_output=True)
            duong.unlink(missing_ok=True)
        else:
            print("(chạy khô — thêm --ap-dung để gỡ thật)")
        return 0
    noi_dung = tao_plist(sys.executable, tep)
    print(f"{'CÀI' if ap_dung else 'CHẠY KHÔ cài'} agent nền {NHAN_LAUNCHD} (mỗi ngày {GIO_CHAY:02d}:{PHUT_CHAY:02d}; "
          "chỉ đo và gửi email khi lịch nền có lỗi đỏ):")
    print(f"  tệp: {duong}\n  python: {sys.executable}\n  tool: {tep}")
    print(noi_dung.decode("utf-8"))
    if not ap_dung:
        print("(chạy khô — thêm --ap-dung để cài; gỡ: --go-launchd --ap-dung)")
        return 0
    duong.parent.mkdir(parents=True, exist_ok=True)
    duong.write_bytes(noi_dung)
    subprocess.run(["launchctl", "bootout", f"{dich}/{NHAN_LAUNCHD}"], capture_output=True)
    r = subprocess.run(["launchctl", "bootstrap", dich, str(duong)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(f"✗ launchctl bootstrap lỗi (mã {r.returncode}): {(r.stderr or '').strip()[:200]}")
        return 2
    print("✓ Đã cài và nạp. Kiểm: launchctl print " + f"{dich}/{NHAN_LAUNCHD}")
    return 0


def da_cai_launchd() -> bool | None:
    """Agent nền đã cài chưa: macOS ⇒ có/không tệp plist; nền tảng khác ⇒ None (không biết — Task Scheduler cài tay)."""
    if sys.platform != "darwin":
        return None
    return (Path.home() / "Library" / "LaunchAgents" / f"{NHAN_LAUNCHD}.plist").is_file()


# ---------------------------------------------------------------------------------------------------------------------
# Bộ canh tự hỏng không được im lặng: thông báo hệ thống + đọc sức khoẻ từ sổ
# ---------------------------------------------------------------------------------------------------------------------
def _mo_ta_ket_qua(ket_qua: str) -> str:
    """Nhãn kết quả ⇒ câu ngắn tiếng Việt. Chỉ từ NHÃN (không bao giờ giá trị cấu hình)."""
    co_dinh = {
        "kenh_chua_bat": "kênh email chưa bật",
        "kenh_khong_do_duoc": "không đo được kênh email",
        "khong_thay_repo": "không thấy repo y khoa (kênh notify)",
        "khong_do_duoc": "cảm biến lịch nền không đo được trọn",
    }
    if ket_qua in co_dinh:
        return co_dinh[ket_qua]
    if ket_qua.startswith("khong_gui_"):
        return f"có lỗi đỏ nhưng email KHÔNG gửi được ({ket_qua[len('khong_gui_'):][:40]})"
    return f"kết quả lạ «{ket_qua[:40]}»"


def thong_bao_he_thong(noi_dung: str) -> bool:
    """Thông báo hệ thống macOS (osascript). Nền tảng khác ⇒ False (không giả là đã báo)."""
    if sys.platform != "darwin":
        return False
    loi = noi_dung.replace("\\", " ").replace('"', "'")[:180]
    try:
        r = subprocess.run(["osascript", "-e", f'display notification "{loi}" with title "LỊCH NỀN EBM — cần xem"'],
                           capture_output=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return False
    return r.returncode == 0


def noi_dung_thong_bao(ket_qua: str, so_loi_do: int) -> str:
    dau = f"Lịch nền có {so_loi_do} lỗi đỏ; " if so_loi_do else ""
    return (dau + f"bộ canh KHÔNG đưa được cảnh báo tới email: {_mo_ta_ket_qua(ket_qua)}. "
            "Chạy python3 tools/canh_lich_nen_email.py để xem.")


def can_thong_bao(st: dict, bay_gio: float) -> bool:
    try:
        truoc = float(st.get("thong_bao_luc") or 0)
    except (TypeError, ValueError):
        truoc = 0.0
    return not (0 <= bay_gio - truoc < KHOANG_THONG_BAO_GIAY)


def suc_khoe(st: dict, bay_gio: float, da_cai: bool | None) -> tuple[int, str]:
    """Đọc `lan_chay_cuoi` của sổ (không đo lại, không gửi gì). (mã, một dòng):
    0 🟢 lượt cuối tới được kênh email · 1 🟡 lượt cuối không tới kênh / agent đã cài mà không chạy > 48 giờ / sổ hỏng ·
    3 ⚪ chưa cài agent nền (macOS) hoặc chưa từng chạy mà không biết đã cài chưa — trạng thái bác sĩ chọn, không phải
    hỏng, nhưng cũng KHÔNG in là 🟢. Trên nền tảng không biết đã cài hay chưa
    (`da_cai` None) thì bỏ phép «cũ > 48 giờ» (lượt chạy tay để lại sổ cũ sẽ báo giả), vẫn xét nhãn kết quả."""
    if da_cai is False:
        return 3, ("⚪ bộ canh lịch nền chưa cài agent nền — cài là việc của bác sĩ: "
                   "python3 tools/canh_lich_nen_email.py --cai-launchd --ap-dung")
    lan = st.get("lan_chay_cuoi")
    if not isinstance(lan, dict):
        if da_cai:
            return 1, ("🟡 bộ canh lịch nền đã cài nhưng sổ chưa có lượt chạy nào — agent nền có chạy không? "
                       f"(launchctl print gui/<uid>/{NHAN_LAUNCHD})")
        # Không biết đã cài hay chưa (Windows) và chưa từng chạy ⇒ ⚪ nói rõ, không 🟢, cũng không nhắc giả mỗi phiên.
        return 3, ("⚪ bộ canh lịch nền chưa có lượt chạy nào (không biết agent nền đã cài chưa) — "
                   "chạy tay python tools/canh_lich_nen_email.py")
    try:
        luc = float(lan.get("luc"))
    except (TypeError, ValueError):
        return 1, "🟡 sổ bộ canh lịch nền hỏng (thiếu mốc lượt cuối) — chạy tay python3 tools/canh_lich_nen_email.py"
    ket_qua = str(lan.get("ket_qua", ""))
    moc = f"{dt.datetime.fromtimestamp(luc):%H:%M %d/%m}"
    ly_do = []
    if ket_qua not in KET_QUA_TOI_KENH:
        ly_do.append(f"lượt cuối ({moc}) KHÔNG đưa được cảnh báo tới email — {_mo_ta_ket_qua(ket_qua)}")
    if da_cai and bay_gio - luc > HAN_CU_GIAY:
        ly_do.append(f"agent nền đã cài mà {int((bay_gio - luc) // 3600)} giờ không có lượt mới (lượt cuối {moc})")
    if ly_do:
        return 1, "🟡 bộ canh lịch nền: " + "; ".join(ly_do) + " — chạy tay python3 tools/canh_lich_nen_email.py"
    return 0, f"🟢 bộ canh lịch nền: lượt cuối {moc} — cảnh báo tới được kênh email ({ket_qua})"


# ---------------------------------------------------------------------------------------------------------------------
# Luồng chính
# ---------------------------------------------------------------------------------------------------------------------
def _in_do(lich: dict, quyen: dict) -> None:
    print(f"🔴 LỊCH NỀN CÓ {len(lich['do']) + len(quyen['do'])} LỖI ĐỎ:")
    for x in lich["do"] + quyen["do"]:
        print(f"   {x}")
    for x in lich["phu"] + quyen["phu"]:
        print(f"   ⚪ {x}")


def _mo_ta_chua_bat(kq: dict) -> str:
    thieu = kq.get("thieu") or []
    return "⚪ kênh email chưa bật" + (f" (thiếu khoá: {', '.join(thieu)})" if thieu else "") + \
        " — cảnh báo KHÔNG được gửi. Bác sĩ tự nhập kênh: python3 tools/nhap_kenh_canh_bao.py"


def _mo_ta_kenh_khong_do_duoc(kq: dict) -> str:
    """Lịch xanh, phép đo kênh (`trang-thai`) không trả `bat` ⇒ chưa thử gửi gì — không được nói «gửi lỗi», cũng không
    được coi là «sẵn sàng»."""
    if kq.get("status") == "khong_nap_duoc":
        return (f"⚪ không nạp được kênh notify của repo y khoa ({kq.get('loai_loi')}"
                + (f": {kq['module']}" if kq.get("module") else "") + ") — KHÔNG biết kênh email có gửi được không.")
    return (f"⚪ không đo được trạng thái kênh email (loại: {kq.get('loai_loi') or kq.get('status') or 'không rõ'}; "
            "chi tiết không in để khỏi lộ cấu hình) — KHÔNG phải «sẵn sàng».")


def _mo_ta_khong_gui(kq: dict) -> str:
    """Một dòng mô tả vì sao không gửi được — chỉ NHÃN, không bao giờ giá trị cấu hình."""
    if kq.get("status") == "skipped" and kq.get("reason") in LY_DO_CHUA_BAT:
        return _mo_ta_chua_bat(kq)
    if kq.get("status") == "khong_nap_duoc":
        return (f"⚪ không nạp được kênh notify của repo y khoa ({kq.get('loai_loi')}"
                + (f": {kq['module']}" if kq.get("module") else "") + ") — cảnh báo KHÔNG được gửi.")
    if kq.get("status") == "error":
        return (f"✗ gửi email KHÔNG thành công (loại: {kq.get('loai_loi', 'khac')}; chi tiết không in để khỏi lộ cấu hình) — "
                "chưa ghi sổ chống lặp, lượt sau thử lại.")
    return f"⚪ kênh email không trả trạng thái «sent» (trạng thái: {kq.get('status')}) — coi như CHƯA gửi."


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Canh lịch nền qua email (bộ canh người chết; chỉ đo và báo)")
    ap.add_argument("--im-khi-on", action="store_true", help="im lặng khi 🟢")
    ap.add_argument("--xem-truoc", action="store_true", help="in email SẼ gửi; không gửi, không ghi sổ")
    ap.add_argument("--cai-launchd", action="store_true", help="in/cài agent launchd chạy mỗi ngày (macOS)")
    ap.add_argument("--go-launchd", action="store_true", help="in/gỡ agent launchd")
    ap.add_argument("--ap-dung", action="store_true", help="với --cai-launchd/--go-launchd: làm thật (mặc định chạy khô)")
    ap.add_argument("--thong-bao", action="store_true",
                    help="thông báo hệ thống macOS khi cảnh báo KHÔNG tới email (mã 2; ≤ 1 lần/20 giờ)")
    ap.add_argument("--suc-khoe", action="store_true", help="chỉ đọc sổ: bộ canh có đang làm việc không (không đo lại)")
    ap.add_argument("--_con", choices=("trang-thai", "gui"), help=argparse.SUPPRESS)
    ap.add_argument("--_mea", help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    if a._con:
        return _che_do_con(a._con, a._mea or "")
    if a.cai_launchd or a.go_launchd:
        return cai_launchd(a.ap_dung, a.go_launchd)
    if a.suc_khoe:
        ma_sk, dong_sk = suc_khoe(doc_state(), time.time(), da_cai_launchd())
        if not (a.im_khi_on and ma_sk in (0, 3)):
            print(dong_sk)
        return ma_sk

    bay_gio = time.time()
    lich, quyen = do_lich(), do_quyen()
    do = lich["do"] + quyen["do"]
    mea = repo_y_khoa()

    if a.xem_truoc:
        if not do:
            print("🟢 Không có lỗi đỏ — sẽ KHÔNG gửi email." if lich["do_duoc"] and quyen["do_duoc"]
                  else "⚪ Không có lỗi đỏ nhưng cảm biến không đo được trọn — sẽ KHÔNG gửi email.")
            for x in lich["phu"] + quyen["phu"]:
                print(f"   ⚪ {x}")
            return 0 if lich["do_duoc"] and quyen["do_duoc"] else 2
        tieu_de, than = soan_email(lich, quyen, dt.datetime.fromtimestamp(bay_gio))
        print(f"(XEM TRƯỚC — không gửi, không ghi sổ)\nTiêu đề: {tieu_de}\n\n{than}")
        return 1

    st = doc_state()
    ket_qua: str
    if not do:
        if not (lich["do_duoc"] and quyen["do_duoc"]):
            ket_qua, ma = "khong_do_duoc", 2
            print("⚪ Lịch nền: không có lỗi đỏ nhưng cảm biến KHÔNG đo được trọn — không phải «ổn»:")
            for x in lich["phu"] + quyen["phu"]:
                print(f"   ⚪ {x}")
        else:
            # Lịch xanh vẫn đo kênh: bộ canh mà kênh tắt thì im lặng vô dụng — phải nói ra, không giả là đang canh.
            kenh = chay_con("trang-thai", {}, mea) if mea else {}
            if kenh.get("bat") is True:
                ket_qua, ma = "xanh", 0
                if not a.im_khi_on:
                    print("🟢 Lịch nền không có lỗi đỏ; kênh email sẵn sàng (cảnh báo sẽ được gửi khi có lỗi).")
                    for x in lich["phu"] + quyen["phu"]:
                        print(f"   ⚪ {x}")
            else:
                # Nhãn tách bạch từng nguyên nhân — `--suc-khoe` và thông báo hệ thống đọc lại đúng nhãn này.
                if not mea:
                    ket_qua, mo_ta = "khong_thay_repo", "⚪ không thấy repo y khoa (kênh notify) — bộ canh không gửi được email"
                elif "bat" in kenh:
                    ket_qua, mo_ta = "kenh_chua_bat", _mo_ta_chua_bat(kenh)
                else:
                    ket_qua, mo_ta = "kenh_khong_do_duoc", _mo_ta_kenh_khong_do_duoc(kenh)
                ma = 2
                print("🟢 Lịch nền không có lỗi đỏ, NHƯNG " + mo_ta)
    else:
        vt = van_tay(do)
        gan = lan_gui_gan(st, vt, bay_gio)
        _in_do(lich, quyen)
        if gan is not None:
            ket_qua, ma = "da_gui_trong_24h", 1
            print(f"   ✉ cùng nội dung ĐÃ gửi email lúc {dt.datetime.fromtimestamp(gan):%H:%M %d/%m} — chống lặp 24 giờ, "
                  "không gửi lại.")
        elif not mea:
            ket_qua, ma = "khong_thay_repo", 2
            print("   ⚪ không thấy repo y khoa (medical-ebm-automation/app/services/notify.py) — cảnh báo KHÔNG được gửi.")
        else:
            tieu_de, than = soan_email(lich, quyen, dt.datetime.fromtimestamp(bay_gio))
            kq = chay_con("gui", {"subject": tieu_de, "body": than}, mea)
            if kq.get("status") == "sent":
                ket_qua, ma = "da_gui", 1
                st = ghi_da_gui(st, vt, bay_gio)
                print("   ✉ đã gửi MỘT email tóm tắt qua kênh notify (chống lặp 24 giờ cho cùng nội dung).")
            else:
                ket_qua, ma = f"khong_gui_{kq.get('status')}", 2
                print("   " + _mo_ta_khong_gui(kq))
    # Cảnh báo không tới email (mã 2) dưới launchd thì mọi dòng in ở trên đều vào /dev/null ⇒ thông báo hệ thống.
    if a.thong_bao and ma == 2 and can_thong_bao(st, bay_gio) \
            and thong_bao_he_thong(noi_dung_thong_bao(ket_qua, len(do))):
        st["thong_bao_luc"] = round(bay_gio)
    # Sổ chỉ chứa vân tay + mốc giờ + nhãn kết quả — không bao giờ giá trị cấu hình.
    st["lan_chay_cuoi"] = {"luc": round(bay_gio), "ket_qua": ket_qua, "so_loi_do": len(do)}
    try:
        ghi_state(st)
    except OSError as e:
        print(f"⚠ không ghi được sổ chống lặp: {type(e).__name__}", file=sys.stderr)
    return ma


if __name__ == "__main__":
    sys.exit(main())
