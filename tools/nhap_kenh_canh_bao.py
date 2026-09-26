"""Nhập KÊNH CẢNH BÁO (email SMTP hoặc webhook) vào kho bí mật của hệ EBM — đóng ESD10.

★ CHỈ BÁC SĨ TỰ CHẠY — không nhờ agent chạy hộ, và KHÔNG dán mật khẩu/URL webhook vào
khung chat với Claude Code (agent không được nhìn thấy giá trị bí mật thật).

Vì sao cần: cổng triển khai giám sát chứng cứ (`verify_evidence_surveillance_deployment.py`,
kiểm ESD10) chặn khi không có kênh cảnh báo — thiếu kênh thì phát hiện an toàn thuốc chỉ nằm
trong tệp, không ai được báo. ESD10 đạt khi CÓ MỘT trong hai:
  • email: ENABLE_EMAIL_ALERTS=true + SMTP_HOST + SMTP_PASSWORD + SMTP_FROM + ALERT_EMAIL_TO
  • webhook: ALERT_WEBHOOK_URL (https)

Gmail: KHÔNG dùng mật khẩu đăng nhập — dùng «Mật khẩu ứng dụng» 16 chữ cái (Tài khoản Google →
Bảo mật → Xác minh 2 bước → Mật khẩu ứng dụng). Google hiển thị nó thành 4 nhóm cách nhau;
nút này tự bỏ dấu cách.

Script chỉ: hỏi thông tin (mật khẩu/URL bằng ô nhập ẨN); kiểm định dạng; ghi các khoá vào
~/.ebm-secrets/medical-ebm-automation.env (NGOÀI OneDrive, ghi nguyên tử, giữ nguyên mọi dòng
khác, quyền 600); đọc lại để xác nhận; KHÔNG in giá trị bí mật. Gửi thử bằng lệnh in ở cuối.

Thử trên file giả (không đụng file thật): thêm  --file <đường-dẫn>
"""
from __future__ import annotations

import getpass
import os
import re
import stat
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

MAC_DINH = Path.home() / ".ebm-secrets" / "medical-ebm-automation.env"
# Khoá coi là bí mật — không bao giờ in giá trị.
KHOA_BI_MAT = {"SMTP_PASSWORD", "ALERT_WEBHOOK_URL"}
_EMAIL = re.compile(r"^[^@\s,;]+@[^@\s,;]+\.[^@\s,;]+$")


def doc_dong(loi_nhac: str, bi_mat: bool = False) -> str:
    """Đọc một dòng; stdin là ống dẫn (chỉ lúc kiểm thử) thì đọc thẳng stdin."""
    if sys.stdin.isatty():
        return (getpass.getpass(loi_nhac) if bi_mat else input(loi_nhac)).strip()
    return sys.stdin.readline().strip()


def la_email(s: str) -> bool:
    return bool(_EMAIL.match(s.strip()))


def danh_sach_email_hop_le(s: str) -> str | None:
    """«a@x.vn, b@y.vn» → chuỗi chuẩn hoá; một địa chỉ sai ⇒ None (không ghi nửa vời)."""
    ds = [x.strip() for x in s.split(",") if x.strip()]
    if not ds or not all(la_email(x) for x in ds):
        return None
    return ", ".join(ds)


def chuan_hoa_mat_khau_ung_dung_gmail(s: str) -> str | None:
    """Mật khẩu ứng dụng Gmail = đúng 16 chữ cái Latinh; Google in thành 4 nhóm cách nhau.

    Bỏ mọi khoảng trắng rồi kiểm. Không khớp ⇒ None — thường là dán nhầm mật khẩu đăng nhập
    (Gmail sẽ từ chối với lỗi 535, khó hiểu hơn nhiều so với báo sớm ở đây).
    """
    gon = re.sub(r"\s+", "", s)
    return gon if re.fullmatch(r"[A-Za-z]{16}", gon) else None


def webhook_hop_le(url: str) -> bool:
    """Chỉ nhận https có tên máy — webhook http làm lộ nội dung cảnh báo trên đường truyền."""
    try:
        p = urlparse(url.strip())
    except ValueError:
        return False
    return p.scheme == "https" and bool(p.netloc) and " " not in url.strip()


def cap_nhat_env(noi_dung: str, khoa_gia_tri: dict[str, str]) -> str:
    """Thay dòng `KHOA=...` nếu đã có, không thì nối cuối. Giữ nguyên mọi dòng khác."""
    for khoa, gia_tri in khoa_gia_tri.items():
        dong = f"{khoa}={gia_tri}"
        mau = re.compile(r"^" + re.escape(khoa) + r"=.*$", re.MULTILINE)
        if mau.search(noi_dung):
            noi_dung = mau.sub(lambda _m, d=dong: d, noi_dung, count=1)
        else:
            if noi_dung and not noi_dung.endswith("\n"):
                noi_dung += "\n"
            noi_dung += dong + "\n"
    return noi_dung


def doc_gia_tri(noi_dung: str, khoa: str) -> str | None:
    m = re.search(r"^" + re.escape(khoa) + r"=(.*)$", noi_dung, re.MULTILINE)
    return m.group(1).strip() if m else None


def _dat_quyen_rieng_tu(duong_dan: Path) -> None:
    try:
        os.chmod(duong_dan, 0o600 if duong_dan.is_file() else 0o700)
    except OSError:
        pass


def _ghi_nguyen_tu(duong_dan: Path, noi_dung: str) -> None:
    fd, tam = tempfile.mkstemp(dir=str(duong_dan.parent), prefix=".kenh-canh-bao-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(noi_dung)
        _dat_quyen_rieng_tu(Path(tam))
        os.replace(tam, duong_dan)
    except BaseException:
        try:
            os.unlink(tam)
        except OSError:
            pass
        raise


def _hoi_email(gmail: bool) -> dict[str, str] | None:
    if gmail:
        host, port = "smtp.gmail.com", "587"
    else:
        host = doc_dong("Máy chủ SMTP (vd smtp.office365.com): ")
        if not host or " " in host or "." not in host:
            print("✗ Tên máy chủ SMTP không hợp lệ. Chưa ghi gì.")
            return None
        port = doc_dong("Cổng SMTP (Enter = 587, STARTTLS): ") or "587"
        if not port.isdigit() or not 0 < int(port) < 65536:
            print("✗ Cổng phải là số 1–65535. Chưa ghi gì.")
            return None
    nguoi_gui = doc_dong("Địa chỉ email GỬI (tài khoản đăng nhập SMTP): ")
    if not la_email(nguoi_gui):
        print("✗ Địa chỉ email gửi không hợp lệ. Chưa ghi gì.")
        return None
    mk = doc_dong(("Dán MẬT KHẨU ỨNG DỤNG Gmail 16 chữ" if gmail else "Mật khẩu SMTP")
                  + " (ký tự sẽ KHÔNG hiện ra): ", bi_mat=True)
    if gmail:
        mk_chuan = chuan_hoa_mat_khau_ung_dung_gmail(mk)
        if mk_chuan is None:
            print("✗ Không phải mật khẩu ứng dụng Gmail (cần đúng 16 chữ cái). Có thể bạn dán mật "
                  "khẩu đăng nhập — tạo mật khẩu ứng dụng ở Tài khoản Google → Bảo mật. Chưa ghi gì.")
            return None
        mk = mk_chuan
    elif not mk:
        print("✗ Chưa nhập mật khẩu. Chưa ghi gì.")
        return None
    nhan = doc_dong(f"Gửi cảnh báo TỚI (Enter = chính {nguoi_gui}; nhiều địa chỉ cách nhau dấu phẩy): ")
    ds_nhan = danh_sach_email_hop_le(nhan or nguoi_gui)
    if ds_nhan is None:
        print("✗ Có địa chỉ nhận không hợp lệ. Chưa ghi gì.")
        return None
    return {
        "ENABLE_EMAIL_ALERTS": "true", "SMTP_HOST": host, "SMTP_PORT": port,
        "SMTP_USE_TLS": "true", "SMTP_USER": nguoi_gui, "SMTP_FROM": nguoi_gui,
        "SMTP_PASSWORD": mk, "ALERT_EMAIL_TO": ds_nhan,
    }


def _hoi_webhook() -> dict[str, str] | None:
    url = doc_dong("Dán URL webhook (https://…; ký tự sẽ KHÔNG hiện ra): ", bi_mat=True)
    if not webhook_hop_le(url):
        print("✗ URL webhook phải bắt đầu bằng https:// và có tên máy. Chưa ghi gì.")
        return None
    return {"ALERT_WEBHOOK_URL": url.strip()}


def main(argv: list[str]) -> int:
    duong_dan = MAC_DINH
    if len(argv) >= 2 and argv[0] == "--file":
        duong_dan = Path(argv[1]).expanduser()
    la_mac_dinh = duong_dan == MAC_DINH
    duong_dan = duong_dan.resolve()
    duong_dan.parent.mkdir(parents=True, exist_ok=True)
    if la_mac_dinh:
        _dat_quyen_rieng_tu(duong_dan.parent)
    noi_dung = duong_dan.read_text(encoding="utf-8") if duong_dan.exists() else ""

    print("Chọn kênh cảnh báo:")
    print("  1) Gmail (mật khẩu ứng dụng)   2) Máy chủ SMTP khác   3) Webhook (Slack/Telegram/n8n…)")
    chon = doc_dong("Gõ 1, 2 hoặc 3 rồi Enter: ")
    if chon == "1":
        moi = _hoi_email(gmail=True)
    elif chon == "2":
        moi = _hoi_email(gmail=False)
    elif chon == "3":
        moi = _hoi_webhook()
    else:
        print("✗ Không chọn kênh nào. Chưa ghi gì.")
        return 1
    if moi is None:
        return 1

    moi_noi_dung = cap_nhat_env(noi_dung, moi)
    _ghi_nguyen_tu(duong_dan, moi_noi_dung)

    doc_lai = duong_dan.read_text(encoding="utf-8")
    sai = [k for k, v in moi.items() if doc_gia_tri(doc_lai, k) != v]
    if sai:
        print(f"✗ Đọc lại không khớp ở {', '.join(sai)} — KHÔNG tin bản ghi này, chạy lại nút.")
        return 2
    quyen = oct(stat.S_IMODE(duong_dan.stat().st_mode))
    hien = ", ".join(k + ("=<đã ẩn>" if k in KHOA_BI_MAT else "=" + v) for k, v in moi.items())
    print(f"✅ Đã lưu vào {duong_dan} (quyền {quyen}): {hien}")
    print("")
    print("Việc tiếp theo — gửi thử thật, KHÔNG giả định là chạy được:")
    print("  cd medical-ebm-automation && python run.py notify-test")
    print("  rồi: python tools/verify_evidence_surveillance_deployment.py  (ESD10 phải PASS)")
    print("  ⚠️  ESD10 PASS chỉ chứng minh CẤU HÌNH có mặt. Bác sĩ phải thấy thư/tin thử tới nơi —")
    print("     đó là bằng chứng UAT, máy không tự điền thay.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
