"""Ghi sức khoẻ lượt gọi Claude API cho giác quan hòm việc — dùng chung cho công cụ CHẠY TAY ở repo gốc.

VÌ SAO (17/11/2026, bác sĩ duyệt «mục 3»). `tu_de_xuat_viec.giac_quan_api_claude` đọc `~/.ebm-api-claude.json` để
báo bác sĩ khi khoá hết tín dụng / bị thu hồi, và báo ⚪ khi lượt gọi gần nhất cũ hơn 14 ngày. Cổng kiểm lạc chủ đề
(skill) và cầu nối hệ nghiên cứu (repo y khoa) đã ghi tệp này; hai công cụ chạy tay — quét lạc chủ đề toàn kho
(Batch API) và bộ đo CAFÉ-S — thì chưa. Mỗi lượt chạy thành công của chúng là một lần đo «khoá còn sống» miễn phí mà
hòm việc đang bỏ phí; lượt lỗi 401/429 của chúng hòm việc cũng không thấy.

Cùng KHUÔN với hai bản kia (luc · trang_thai · ly_do · so_muc · nguon). Skill giữ bản riêng vì skill phải tự đứng
được khi tải lên tài khoản claude.ai — không nhập được mô-đun ở `tools/`.

THEO TỪNG CÔNG CỤ (17/11/2026, bác sĩ duyệt «mục 2»): tệp trước chỉ giữ MỘT lượt — 8 công cụ ghi chung một ô nên
lượt sau xoá lượt trước; công cụ A lỗi 401 rồi công cụ B chạy ổn ngay sau thì lỗi của A biến mất trước khi hòm việc
kịp đọc. Nay khoá «theo_nguon» giữ lượt gần nhất của TỪNG công cụ; khoá cấp cao vẫn là lượt gần nhất (bản đọc cũ đọc
như trước). Khuôn trộn có ở BA nơi ghi (đây · cổng check_topic_relevance của skill · cầu nối y khoa api_claude_nc.py)
— sửa một nơi phải sửa cả ba.

Luật: dưới pytest KHÔNG ghi tệp THẬT (`PYTEST_CURRENT_TEST` được tiến trình con kế thừa; chủ động đo thật thì đặt
EBM_KIEM_API_THAT=1). Lỗi ghi đều nuốt — nhật ký hỏng không được làm vỡ lượt chạy. Không bao giờ ghi giá trị khoá.
"""
from __future__ import annotations

import datetime as _dt
import json
import os

# Đường THẬT luôn ở thư mục nhà; rào pytest so với ĐƯỜNG NÀY. `EBM_NHAT_KY_API` chỉ để kiểm thử trỏ sang tệp tạm
# (công cụ nạp lại mô-đun mỗi lượt nên không vá được hằng từ ngoài).
_NK_THAT = os.path.join(os.path.expanduser("~"), ".ebm-api-claude.json")
NHAT_KY_API = os.environ.get("EBM_NHAT_KY_API") or _NK_THAT


def _duoi_pytest_cham_that(duong: str) -> bool:
    if not os.environ.get("PYTEST_CURRENT_TEST") or os.environ.get("EBM_KIEM_API_THAT") == "1":
        return False
    try:
        return os.path.realpath(duong) == os.path.realpath(_NK_THAT)
    except (OSError, ValueError):
        return True  # không phân định được ⇒ thận trọng: coi là tệp thật


_TRUONG_LUOT = ("luc", "trang_thai", "ly_do", "so_muc")


def gop_theo_nguon(duong: str, ban_ghi: dict) -> dict:
    """Trộn lượt mới vào nhật ký đã có: «theo_nguon» giữ lượt gần nhất của TỪNG công cụ; khoá cấp cao = lượt mới.

    Nhật ký kiểu cũ (một lượt, chưa có «theo_nguon») được giữ làm mục của nguồn đã ghi nó — không mất lượt lỗi cũ."""
    try:
        with open(duong, "r", encoding="utf-8") as fh:
            cu = json.load(fh)
    except (OSError, ValueError):
        cu = None
    theo: dict = {}
    if isinstance(cu, dict):
        tn = cu.get("theo_nguon")
        if isinstance(tn, dict):
            theo = {str(k): v for k, v in tn.items() if isinstance(v, dict)}
        elif cu.get("trang_thai"):
            theo[str(cu.get("nguon") or "")] = {k: cu.get(k) for k in _TRUONG_LUOT}
    theo[str(ban_ghi.get("nguon") or "")] = {k: ban_ghi.get(k) for k in _TRUONG_LUOT}
    return dict(ban_ghi, theo_nguon=theo)


def _ghi_nguyen_tu(duong: str, du_lieu: dict) -> None:
    """Ghi qua tệp tạm rồi đổi tên: hai công cụ ghi cùng lúc không bao giờ để lại tệp cụt nửa chừng."""
    tam = f"{duong}.{os.getpid()}.tmp"
    try:
        with open(tam, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(du_lieu, fh, ensure_ascii=False, indent=1)
        os.replace(tam, duong)
    finally:
        if os.path.exists(tam):
            try:
                os.remove(tam)
            except OSError:
                pass


def ghi(trang_thai: str, ly_do: str = "", so_muc: int = 0, nguon: str = "", tep: str | None = None) -> None:
    """Ghi kết quả lượt gọi gần nhất. `trang_thai` ∈ ok · skipped · error (giác quan đọc đúng ba giá trị này)."""
    duong = tep or os.environ.get("EBM_NHAT_KY_API") or NHAT_KY_API
    if _duoi_pytest_cham_that(duong):
        return
    try:
        ban_ghi = {"luc": _dt.datetime.now().isoformat(timespec="seconds"), "trang_thai": str(trang_thai),
                   "ly_do": str(ly_do)[:200], "so_muc": int(so_muc), "nguon": str(nguon)[:80]}
        _ghi_nguyen_tu(duong, gop_theo_nguon(duong, ban_ghi))
    except (OSError, TypeError, ValueError):
        pass

