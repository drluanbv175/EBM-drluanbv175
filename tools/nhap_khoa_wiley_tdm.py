"""Nhập TOKEN Wiley Text and Data Mining (TDM) API vào kho bí mật của hệ EBM.

★ CHỈ BÁC SĨ TỰ CHẠY — không nhờ agent chạy hộ, và KHÔNG dán token vào khung chat
với Claude Code (agent không được phép nhìn thấy/đọc/gõ giá trị token thật).

Lấy token ở đâu: đăng nhập tài khoản Wiley Online Library (WOL) của bác sĩ ->
trang "Text and Data Mining" trong phần cài đặt tài khoản. Token là một chuỗi
UUID (vd "550e8400-e29b-41d4-a716-446655440000").

⚠️ Giới hạn đã biết TRƯỚC khi có token (theo README chính thức của thư viện
wiley-tdm, mục Known Limitations): "Access is IP address based only" — dù
token đúng, quyền truy cập các bài KHÔNG PHẢI Open Access phụ thuộc DẢI IP mà
tài khoản WOL được cấp quyền (thường là mạng bệnh viện/tổ chức). Gọi từ mạng
khác có thể nhận ACCESS_DENIED dù token hợp lệ — đây KHÔNG phải lỗi của công cụ
này, phải kiểm bằng lệnh ở cuối cùng.

Script này chỉ: hỏi token bằng ô nhập ẨN (không hiện ký tự); kiểm định dạng
UUID bằng CHÍNH lớp `uuid.UUID` mà thư viện `wiley_tdm` dùng để xác thực (nên
không bao giờ lệch với thứ code thật sẽ chấp nhận); ghi
WILEY_TDM_API_TOKEN=<token> và ENABLE_WILEY_TDM=true vào
~/.ebm-secrets/medical-ebm-automation.env (NGOÀI OneDrive, ghi nguyên tử, giữ
nguyên mọi dòng khác trong file, không bao giờ in giá trị token ra màn hình).

Thử trên file giả (không đụng file thật): thêm  --file <đường-dẫn>
"""
from __future__ import annotations

import getpass
import os
import re
import stat
import sys
import tempfile
import uuid
from pathlib import Path

# Windows mặc định stdout/stderr là cp1252 -> chết khi in tiếng Việt có dấu (đã
# gặp nhiều lần trong repo này). Tự ép UTF-8 tại chỗ, không phụ thuộc biến môi
# trường PYTHONIOENCODING của nơi gọi (cùng khuôn tools/add_vn_source.py).
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

TEN_KHOA = "WILEY_TDM_API_TOKEN"
TEN_CO_BAT = "ENABLE_WILEY_TDM"
MAC_DINH = Path.home() / ".ebm-secrets" / "medical-ebm-automation.env"


def doc_dong(loi_nhac: str, bi_mat: bool = False) -> str:
    """Đọc một dòng từ bàn phím. Khi stdin là ống dẫn (chỉ dùng lúc kiểm thử) thì đọc từ stdin."""
    if sys.stdin.isatty():
        return (getpass.getpass(loi_nhac) if bi_mat else input(loi_nhac)).strip()
    return sys.stdin.readline().strip()


def gop_neu_dan_doi(token: str) -> tuple[str, bool]:
    """Token bị DÁN ĐÔI (hai nửa giống hệt nhau, độ dài chẵn) thì lấy MỘT nửa.

    Nhận diện chắc chắn, không đoán: chỉ gộp khi token[:n/2] == token[n/2:] và n >= 32.
    """
    n = len(token)
    if n >= 32 and n % 2 == 0 and token[: n // 2] == token[n // 2:]:
        return token[: n // 2], True
    return token, False


def chuan_hoa_uuid(token: str) -> str | None:
    """Trả chuỗi UUID đã chuẩn hoá (dạng có dấu gạch ngang, chữ thường) nếu hợp lệ,
    None nếu không phải UUID — dùng ĐÚNG lớp uuid.UUID mà thư viện wiley_tdm dùng
    để xác thực, tránh lệch chuẩn giữa nút bấm này và code thật sẽ chạy."""
    try:
        return str(uuid.UUID(token))
    except (ValueError, AttributeError, TypeError):
        return None


def _dat_quyen_rieng_tu(duong_dan: Path) -> None:
    """chmod 600/700 — trên Windows, os.chmod chỉ chỉnh được cờ ghi-được, không có
    ACL POSIX đầy đủ; không để việc đó làm hỏng luồng chính."""
    try:
        os.chmod(duong_dan, 0o600 if duong_dan.is_file() else 0o700)
    except OSError:
        pass


def main(argv: list[str]) -> int:
    duong_dan = MAC_DINH
    if len(argv) >= 2 and argv[0] == "--file":
        duong_dan = Path(argv[1]).expanduser()
    la_mac_dinh = duong_dan == MAC_DINH
    duong_dan = duong_dan.resolve()
    thu_muc = duong_dan.parent
    thu_muc.mkdir(parents=True, exist_ok=True)
    if la_mac_dinh:
        _dat_quyen_rieng_tu(thu_muc)

    noi_dung = duong_dan.read_text(encoding="utf-8") if duong_dan.exists() else ""
    mau = re.compile(r"^" + TEN_KHOA + r"=(.*)$", re.MULTILINE)
    cu = mau.search(noi_dung)
    token = None
    if cu and cu.group(1).strip().strip("\"'"):
        token_cu = cu.group(1).strip().strip("\"'")
        print(f"ℹ️  File đã có {TEN_KHOA} (độ dài {len(token_cu)} ký tự).")
        gop, co_gop = gop_neu_dan_doi(token_cu)
        chuan = chuan_hoa_uuid(gop)
        if co_gop and chuan:
            print(f"⚠️  Token đang lưu bị DÁN ĐÔI — đã tự sửa tại chỗ về đúng 1 UUID, "
                  f"bạn KHÔNG cần dán lại.")
            token = chuan
        else:
            tra_loi = doc_dong(
                "Gõ  g  rồi Enter để GHI ĐÈ bằng token mới; chỉ Enter = giữ nguyên và thoát: "
            ).lower()
            if tra_loi != "g":
                print("Giữ nguyên, chưa ghi gì.")
                return 0

    if token is None:
        token_tho = doc_dong("Dán token Wiley TDM (UUID) rồi bấm Enter (ký tự sẽ KHÔNG hiện ra): ",
                              bi_mat=True)
        if not token_tho:
            print("✗ Chưa nhập gì — thoát, chưa ghi gì.")
            return 1
        token_tho, co_gop_nhap = gop_neu_dan_doi(token_tho)
        if co_gop_nhap:
            print(f"ℹ️  Token vừa dán bị lặp đôi — đã tự gộp về {len(token_tho)} ký tự.")
        token = chuan_hoa_uuid(token_tho)
        if token is None:
            print("✗ Không phải định dạng UUID hợp lệ (Wiley TDM đòi đúng dạng UUID, vd "
                  "550e8400-e29b-41d4-a716-446655440000). Có thể dán thiếu/thừa ký tự. Chưa ghi gì.")
            return 1

    dong_token = TEN_KHOA + "=" + token
    dong_bat = TEN_CO_BAT + "=true"

    # Thay/ghi TEN_KHOA
    if mau.search(noi_dung):
        noi_dung, _ = mau.subn(lambda _m: dong_token, noi_dung)
    else:
        tien_to = "" if (not noi_dung or noi_dung.endswith("\n")) else "\n"
        noi_dung = (noi_dung + tien_to
                    + "\n# Wiley Text and Data Mining API — bác sĩ tự nhập bằng nút "
                      "'Nhap Khoa Wiley TDM.cmd'\n" + dong_token + "\n")

    # Thay/ghi TEN_CO_BAT (bật luôn — token vừa nhập là để dùng ngay)
    mau_bat = re.compile(r"^" + TEN_CO_BAT + r"=(.*)$", re.MULTILINE)
    if mau_bat.search(noi_dung):
        noi_dung, _ = mau_bat.subn(lambda _m: dong_bat, noi_dung)
    else:
        noi_dung = noi_dung.rstrip("\n") + "\n" + dong_bat + "\n"

    # Ghi nguyên tử: viết file tạm cùng thư mục (quyền 600) rồi đổi tên đè lên — hỏng
    # giữa chừng thì file cũ (chứa các khoá khác) vẫn còn nguyên.
    fd, tam = tempfile.mkstemp(dir=str(thu_muc), prefix=".wiley-tdm-", suffix=".tmp")
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

    kiem = mau.search(duong_dan.read_text(encoding="utf-8"))
    if not kiem or kiem.group(1).strip() != token:
        print("✗ Đọc lại không khớp — KHÔNG tin bản ghi này, chạy lại nút.")
        return 2
    quyen = oct(stat.S_IMODE(duong_dan.stat().st_mode))
    print(f"✅ Đã lưu {TEN_KHOA} (UUID hợp lệ) và {dong_bat} vào {duong_dan} — quyền {quyen}.")
    print("")
    print("Việc tiếp theo — kiểm sống, KHÔNG giả định là chắc chắn chạy được:")
    print("  1) Thử một DOI OPEN ACCESS trước (tách lỗi token khỏi lỗi phạm vi IP):")
    print('     python run.py wiley-tdm-test "<DOI Open Access>"')
    print("  2) Rồi thử một DOI KHÔNG Open Access:")
    print('     python run.py wiley-tdm-test "<DOI khác, không Open Access>"')
    print("  ⚠️  Bước 2 báo ACCESS_DENIED KHÔNG có nghĩa token sai — nghĩa là mạng đang chạy lệnh")
    print("     này KHÔNG nằm trong dải IP mà tài khoản Wiley Online Library được cấp quyền")
    print("     (thường là mạng bệnh viện/tổ chức). Đây là giới hạn CỦA TÀI KHOẢN, không phải")
    print("     lỗi cấu hình — xem app/sources/wiley_tdm.py để đọc đầy đủ.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
