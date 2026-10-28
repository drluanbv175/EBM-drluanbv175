"""Luật MỘT CỬA VÀO cho câu hỏi chủ đề chứng cứ (28/10/2026, bác sĩ chọn).

Sự cố đo được chiều 28/10/2026: ba phiên bác sĩ hỏi «tiếp cận chẩn đoán điều trị … toàn diện dựa trên chứng cứ mới nhất» đều
KHÔNG vào dây chuyền `cap-nhat-chung-cu-y-khoa` (CLAUDE.md §6.2): hai phiên rẽ sang skill `tong-thuat-chung-cu` (không dashboard,
không cổng liêm chính, không bộ năm, không hub), một phiên trả lời từ trí nhớ. Bốn lớp vá được kiểm ở đây:
  ① `intent.route` xếp câu chủ đề chứng cứ vào skill một cửa (ca lâm sàng, cờ đỏ, việc lẻ MẠNH, câu hỏi về hệ thống vẫn như cũ);
  ② hook UserPromptSubmit `tools/nhac_dinh_tuyen.py` nhắc đúng đường, im lặng với câu khác, không bao giờ chặn lượt gõ;
  ③ 80 ký tự đầu của mô tả skill (phần model thấy) nói rõ ai là cửa vào;
  ④ `xuat_tong_thuat.py --dashboard` chặn nguồn ngoài dashboard đã qua cổng.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tools"))

from tools.orchestrator.intent import SKILL_CAP_NHAT_CHUNG_CU, route  # noqa: E402
from xuat_tong_thuat import kiem_neo_dashboard  # noqa: E402

import nhac_dinh_tuyen  # noqa: E402

# Ba câu THẬT bác sĩ gõ chiều 28/10/2026 (hai câu đầu) + biến thể không dấu và mẫu trong SKILL.md.
CAU_CHU_DE = [
    "Tiếp cận chẩn đoán điều trị,tiên lương suy tim một cách toàn diện dựa trên chứng cứ mới nhất và độ tin cậy cao nhất",
    "Tiếp cận chẩn đoán và điều trị bệnh tiểu đường,biến chứng tiểu đường một cách toàn diện nhất dựa trên chứng cứ mới nhất "
    "và độ tin cậy cao nhất",
    "Tiep can chan doan dieu tri suy tim toan dien dua tren chung cu moi nhat",
    "Cập nhật chứng cứ suy tim",
    "Hen phế quản 2026: chẩn đoán và điều trị theo mức chứng cứ hiện hành",
    "Lupus ban đỏ hệ thống: cập nhật điều trị mới nhất",  # «hệ thống» trong TÊN BỆNH không phải câu hỏi về hệ thống
]


@pytest.mark.parametrize("cau", CAU_CHU_DE)
def test_cau_chu_de_chung_cu_vao_mot_cua(cau):
    kq = route(cau)
    assert (kq.kind, kq.target) == ("cong_cu", SKILL_CAP_NHAT_CHUNG_CU), kq.as_dict()


@pytest.mark.parametrize("cau, kind, target", [
    # Ca lâm sàng cụ thể và cờ đỏ LUÔN thắng (over-route sang nơi có BƯỚC 0 là chiều an toàn).
    ("nữ 60 tuổi đau ngực, tiếp cận chẩn đoán theo chứng cứ mới nhất", "clinical_case", "dieu-phoi-lam-sang"),
    ("tiếp cận chẩn đoán đau ngực cấp cứu theo chứng cứ mới nhất", "single_task", "sang-loc-co-do"),
    # Việc lẻ MẠNH thắng.
    ("kiểm trích dẫn bài tổng thuật suy tim mới nhất", "single_task", "kiem-chung-trich-dan"),
    # Câu hỏi PICO hẹp không có cue chủ đề vẫn là tra cứu một câu hỏi.
    ("guideline nói gì về SGLT2i trong HFpEF", "single_task", "tra-cuu-chung-cu"),
    # Làm mới chủ đề cũ nhất vẫn là việc của orchestrator.
    ("làm mới chứng cứ chủ đề nào cũ nhất", "cong_cu", "ops/orchestrator.py"),
])
def test_uu_tien_cu_khong_doi(cau, kind, target):
    kq = route(cau)
    assert (kq.kind, kq.target) == (kind, target), kq.as_dict()


@pytest.mark.parametrize("cau", [
    "Hãy kiểm tra lại tại sao tôi cập nhật chứng cứ y khoa không thực hiện theo đúng thiết kế và xây dựng",
    "Hệ thống cập nhật chứng cứ y khoa của tôi đã hoàn thiện các bước",
    "Kiểm tra toàn diện và hoàn thiện toàn diện hệ thống nghiên cứu y khoa",
])
def test_cau_hoi_ve_he_thong_khong_bi_keo_vao_mot_cua(cau):
    assert route(cau).target != SKILL_CAP_NHAT_CHUNG_CU


# ── ② hook ────────────────────────────────────────────────────────────────────────────────────────────────────────────────


def _chay_hook(du_lieu: bytes) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(REPO / "tools" / "nhac_dinh_tuyen.py")], input=du_lieu,
                          capture_output=True, timeout=30)


def test_hook_nhac_mot_cua_cho_cau_chu_de():
    r = _chay_hook(json.dumps({"prompt": CAU_CHU_DE[0]}).encode("utf-8"))
    assert r.returncode == 0
    ra = json.loads(r.stdout.decode("utf-8"))["hookSpecificOutput"]
    assert ra["hookEventName"] == "UserPromptSubmit"
    assert "cap-nhat-chung-cu-y-khoa" in ra["additionalContext"] and "--dashboard" in ra["additionalContext"]


def test_hook_nhac_nhac_truong_cho_ca_lam_sang():
    assert "dieu-phoi-lam-sang" in nhac_dinh_tuyen.loi_nhac("Bệnh nhân đa bệnh lý lớn tuổi, cách tiếp cận để không sai sót")


@pytest.mark.parametrize("cau", ["Gộp", "Đã bấm G10", "/cap-nhat-chung-cu suy tim", "<task-notification>Cập nhật chứng cứ suy tim</task-notification>", ""])
def test_hook_im_lang_voi_cau_khac(cau):
    assert nhac_dinh_tuyen.loi_nhac(cau) == ""


@pytest.mark.parametrize("rac", [b"khong phai json", b"[1,2]", b"", b"\xff\xfe"])
def test_hook_khong_bao_gio_chan_luot_go(rac):
    r = _chay_hook(rac)
    assert r.returncode == 0 and r.stdout == b""


def test_hook_duoc_khai_trong_settings_di_qua_git_va_chay_that():
    """Chạy ĐÚNG lệnh đã khai (không chỉ tìm chuỗi): khai sai đường dẫn thì hook im lặng mãi mà không ai biết."""
    cfg = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
    lenh = [h["command"] for m in cfg["hooks"]["UserPromptSubmit"] for h in m["hooks"]]
    assert len(lenh) == 1
    bash = shutil.which("bash")
    if bash is None:
        pytest.skip("máy không có bash — Claude Code chạy hook bằng bash")
    r = subprocess.run([bash, "-c", lenh[0]], input=json.dumps({"prompt": CAU_CHU_DE[0]}).encode("utf-8"),
                       capture_output=True, timeout=30, env={**os.environ, "CLAUDE_PROJECT_DIR": str(REPO)})
    assert r.returncode == 0
    assert "cap-nhat-chung-cu-y-khoa" in r.stdout.decode("utf-8")


# ── ③ mô tả skill (80 ký tự đầu là phần model thấy khi chọn skill) ───────────────────────────────────────────────────────


def _mo_ta(skill: str) -> str:
    dau = (REPO / "sync" / "skills" / skill / "SKILL.md").read_text(encoding="utf-8").split("---")[1]
    dong = next(d for d in dau.splitlines() if d.startswith("description:"))
    return dong.split(":", 1)[1].strip().strip('"')


def test_80_ky_tu_dau_noi_ro_cua_vao():
    assert "CỬA VÀO DUY NHẤT" in _mo_ta("cap-nhat-chung-cu-y-khoa")[:80]
    assert "KHÔNG phải cửa vào" in _mo_ta("tong-thuat-chung-cu")[:80]
    assert _mo_ta("dark-analyst")[:80] != _mo_ta("cap-nhat-chung-cu-y-khoa")[:80]


def test_skill_tong_thuat_doi_dashboard_khi_xuat():
    s = (REPO / "sync" / "skills" / "tong-thuat-chung-cu" / "SKILL.md").read_text(encoding="utf-8")
    assert "xuat_tong_thuat.py <file>.md --dashboard" in s
    assert "## ĐIỀU KIỆN VÀO — KHÔNG PHẢI CỬA VÀO" in s


# ── ④ cổng neo dashboard ─────────────────────────────────────────────────────────────────────────────────────────────────

BAI = ("Thân bài [1][2][3][4].\nCần bác sĩ kiểm chứng.\n## Nguồn\n"
       "1. A. Tạp chí 2026. PMID 123456 · doi:10.1/AbC.\n"
       "2. B. Tạp chí 2025. PMID 1234567\n"
       "3. C. Trang chính thức https://example.org/guideline [truy cập ngày 28/10/2026]\n"
       "4. D. Tạp chí 2024. doi:10.9/XYZ\n")


def test_nguon_trong_dashboard_thi_dat():
    dash = "items:[{pmid:'123456'},{pmid:'1234567'}] ref https://example.org/guideline doi 10.9/xyz"
    assert kiem_neo_dashboard(BAI, dash) == []


def test_nguon_ngoai_dashboard_bi_chan():
    # 1234567 KHÔNG được coi là có chỉ vì 12345678 có mặt (khớp trọn số); DOI mục 4 vắng.
    dash = "items:[{pmid:'123456'},{pmid:'12345678'}] https://example.org/guideline"
    loi = kiem_neo_dashboard(BAI, dash)
    assert [x.split(" ")[1] for x in loi] == ["2", "4"], loi


def test_doi_so_chu_thuong_va_bo_dau_cau_cuoi():
    assert kiem_neo_dashboard(BAI.replace("PMID 123456 · ", ""), "1234567 example.org/guideline 10.1/ABC 10.9/Xyz.") == [
        "nguồn 3 không có trong dashboard — thêm vào dashboard (bản nối tiếp) qua cổng rồi mới trích"]
